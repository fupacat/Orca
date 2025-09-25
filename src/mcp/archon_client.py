"""
Archon MCP client for task management and project coordination.

Provides high-level interfaces for Archon operations including task management,
project operations, document handling, and RAG knowledge base integration.
"""

import asyncio
import httpx
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .base_client import BaseMCPClient, MCPConnectionError, MCPError, MCPValidationError


class ArchonMCPClient(BaseMCPClient):
    """
    Archon MCP client for task management operations.

    Handles HTTP-based communication with the Archon MCP server for
    project management, task coordination, and knowledge base operations.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8051/mcp",
        timeout: float = 30.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Archon MCP client.

        Args:
            base_url: Base URL for Archon MCP server
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        super().__init__(
            server_name="archon",
            connection_type="http",
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay
        )
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> bool:
        """
        Establish connection to Archon MCP server.

        Returns:
            bool: True if connection successful
        """
        try:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )

            # Test connection with health check
            health_result = await self.health_check()
            is_healthy = health_result.get("success", False)

            self.update_connection_status(
                is_connected=True,
                health_status="healthy" if is_healthy else "degraded"
            )

            self.logger.info(f"Connected to Archon MCP server at {self.base_url}")
            return True

        except Exception as e:
            self.update_connection_status(
                is_connected=False,
                health_status="error",
                error_message=str(e)
            )
            self.logger.error(f"Failed to connect to Archon: {e}")
            return False

    async def disconnect(self) -> None:
        """Close connection to Archon MCP server."""
        if self._client:
            await self._client.aclose()
            self._client = None

        self.update_connection_status(
            is_connected=False,
            health_status="disconnected"
        )
        self.logger.info("Disconnected from Archon MCP server")

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Archon MCP server.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Dict[str, Any]: Response data

        Raises:
            MCPConnectionError: If not connected or request fails
            MCPError: If server returns error
        """
        if not self._client:
            raise MCPConnectionError("Not connected to Archon MCP server")

        url = f"{self.base_url}{endpoint}"

        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()

            # Handle different content types
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                data = response.json()
            else:
                data = {"content": response.text}

            return self.validate_response(data)

        except httpx.HTTPStatusError as e:
            raise MCPError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise MCPConnectionError(f"Request failed: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Archon MCP server.

        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            return await self._make_request("GET", "/health")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    # Task Management Operations

    async def find_tasks(
        self,
        query: Optional[str] = None,
        task_id: Optional[str] = None,
        filter_by: Optional[str] = None,
        filter_value: Optional[str] = None,
        project_id: Optional[str] = None,
        include_closed: bool = True,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Find and search tasks using consolidated API.

        Args:
            query: Keyword search in title, description, feature
            task_id: Get specific task by ID (returns full details)
            filter_by: Filter type ("status", "project", "assignee")
            filter_value: Filter value
            project_id: Project UUID for additional filtering
            include_closed: Include done tasks in results
            page: Page number for pagination
            per_page: Items per page

        Returns:
            Dict[str, Any]: Task search results or single task details
        """
        params = {
            "page": page,
            "per_page": per_page,
            "include_closed": include_closed
        }

        if query:
            params["query"] = query
        if task_id:
            params["task_id"] = task_id
        if filter_by:
            params["filter_by"] = filter_by
        if filter_value:
            params["filter_value"] = filter_value
        if project_id:
            params["project_id"] = project_id

        return await self.with_retry(
            self._make_request,
            "GET",
            "/tasks",
            params=params
        )

    async def manage_task(
        self,
        action: str,
        task_id: Optional[str] = None,
        project_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
        task_order: Optional[int] = None,
        feature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Manage tasks (create/update/delete) using consolidated API.

        Args:
            action: Action to perform ("create", "update", "delete")
            task_id: Task UUID for update/delete
            project_id: Project UUID for create
            title: Task title text
            description: Detailed task description
            status: Task status ("todo", "doing", "review", "done")
            assignee: Task assignee ("User", "Archon", "AI IDE Agent")
            task_order: Priority 0-100 (higher = more priority)
            feature: Feature label for grouping

        Returns:
            Dict[str, Any]: Task management result
        """
        data = {"action": action}

        if task_id:
            data["task_id"] = task_id
        if project_id:
            data["project_id"] = project_id
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if status:
            data["status"] = status
        if assignee:
            data["assignee"] = assignee
        if task_order is not None:
            data["task_order"] = task_order
        if feature:
            data["feature"] = feature

        return await self.with_retry(
            self._make_request,
            "POST",
            "/tasks/manage",
            json=data
        )

    # Project Management Operations

    async def find_projects(
        self,
        project_id: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        List and search projects using consolidated API.

        Args:
            project_id: Get specific project by ID (returns full details)
            query: Keyword search in title/description
            page: Page number for pagination
            per_page: Items per page

        Returns:
            Dict[str, Any]: Projects list or single project details
        """
        params = {
            "page": page,
            "per_page": per_page
        }

        if project_id:
            params["project_id"] = project_id
        if query:
            params["query"] = query

        return await self.with_retry(
            self._make_request,
            "GET",
            "/projects",
            params=params
        )

    async def manage_project(
        self,
        action: str,
        project_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        github_repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Manage projects (create/update/delete) using consolidated API.

        Args:
            action: Action to perform ("create", "update", "delete")
            project_id: Project UUID for update/delete
            title: Project title (required for create)
            description: Project goals and scope
            github_repo: GitHub URL

        Returns:
            Dict[str, Any]: Project management result
        """
        data = {"action": action}

        if project_id:
            data["project_id"] = project_id
        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if github_repo:
            data["github_repo"] = github_repo

        return await self.with_retry(
            self._make_request,
            "POST",
            "/projects/manage",
            json=data
        )

    # RAG Knowledge Base Operations

    async def rag_search_knowledge_base(
        self,
        query: str,
        source_domain: Optional[str] = None,
        match_count: int = 5
    ) -> Dict[str, Any]:
        """
        Search knowledge base for relevant content using RAG.

        Args:
            query: Search query
            source_domain: Optional domain filter (e.g., 'docs.anthropic.com')
            match_count: Maximum results to return (default: 5)

        Returns:
            Dict[str, Any]: Search results with content and metadata
        """
        data = {
            "query": query,
            "match_count": match_count
        }

        if source_domain:
            data["source_domain"] = source_domain

        return await self.with_retry(
            self._make_request,
            "POST",
            "/rag/search",
            json=data
        )

    async def rag_search_code_examples(
        self,
        query: str,
        source_domain: Optional[str] = None,
        match_count: int = 5
    ) -> Dict[str, Any]:
        """
        Search for relevant code examples in the knowledge base.

        Args:
            query: Search query
            source_domain: Optional domain filter
            match_count: Maximum results to return (default: 5)

        Returns:
            Dict[str, Any]: Code examples with content and summaries
        """
        data = {
            "query": query,
            "match_count": match_count
        }

        if source_domain:
            data["source_domain"] = source_domain

        return await self.with_retry(
            self._make_request,
            "POST",
            "/rag/code-examples",
            json=data
        )

    async def rag_get_available_sources(self) -> Dict[str, Any]:
        """
        Get list of available sources in the knowledge base.

        Returns:
            Dict[str, Any]: Available sources information
        """
        return await self.with_retry(
            self._make_request,
            "GET",
            "/rag/sources"
        )

    # High-level workflow helpers

    async def create_execution_project(
        self,
        title: str,
        description: str,
        github_repo: Optional[str] = None
    ) -> str:
        """
        Create a new project for development execution workflow.

        Args:
            title: Project title
            description: Project description
            github_repo: Optional GitHub repository URL

        Returns:
            str: Created project ID
        """
        result = await self.manage_project(
            action="create",
            title=title,
            description=description,
            github_repo=github_repo
        )

        if not result.get("success"):
            raise MCPError(f"Failed to create project: {result.get('message', 'Unknown error')}")

        project = result.get("project", {})
        project_id = project.get("id")

        if not project_id:
            raise MCPError("Project created but no ID returned")

        self.logger.info(f"Created execution project: {project_id}")
        return project_id

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        assignee: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update task status and optionally assignee.

        Args:
            task_id: Task ID to update
            status: New status ("todo", "doing", "review", "done")
            assignee: Optional new assignee

        Returns:
            Dict[str, Any]: Update result
        """
        return await self.manage_task(
            action="update",
            task_id=task_id,
            status=status,
            assignee=assignee
        )

    async def get_project_tasks(
        self,
        project_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all tasks for a project, optionally filtered by status.

        Args:
            project_id: Project ID
            status: Optional status filter

        Returns:
            List[Dict[str, Any]]: List of tasks
        """
        params = {}
        if status:
            params["filter_by"] = "status"
            params["filter_value"] = status

        result = await self.find_tasks(project_id=project_id, **params)

        if not result.get("success"):
            raise MCPError(f"Failed to get tasks: {result.get('message', 'Unknown error')}")

        return result.get("tasks", [])
"""
MCP Connection Manager for coordinated multi-server operations.

Manages connections to multiple MCP servers and provides unified interfaces
for complex operations that require coordination between servers.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from .archon_client import ArchonMCPClient
from .serena_client import SerenaMCPClient
from .base_client import MCPError, MCPConnectionError, ConnectionStatus


class MCPConnectionManager:
    """
    Manages connections to multiple MCP servers for coordinated operations.

    Provides unified interfaces for operations that span multiple MCP servers
    and handles connection lifecycle, error recovery, and health monitoring.
    """

    def __init__(
        self,
        archon_base_url: str = "http://localhost:8051/mcp",
        serena_working_directory: Optional[str] = None,
        connection_timeout: float = 30.0,
        health_check_interval: float = 300.0  # 5 minutes
    ):
        """
        Initialize MCP connection manager.

        Args:
            archon_base_url: Base URL for Archon MCP server
            serena_working_directory: Working directory for Serena operations
            connection_timeout: Connection timeout in seconds
            health_check_interval: Health check interval in seconds
        """
        self.logger = logging.getLogger("mcp.manager")

        # Initialize clients
        self.archon = ArchonMCPClient(
            base_url=archon_base_url,
            timeout=connection_timeout
        )
        self.serena = SerenaMCPClient(
            timeout=connection_timeout,
            working_directory=serena_working_directory
        )

        self.health_check_interval = health_check_interval
        self._health_check_task: Optional[asyncio.Task] = None
        self._connected = False

    async def connect_all(self) -> Dict[str, bool]:
        """
        Connect to all MCP servers.

        Returns:
            Dict[str, bool]: Connection status for each server
        """
        results = {}

        # Connect to Archon
        try:
            archon_connected = await self.archon.connect()
            results["archon"] = archon_connected
            if archon_connected:
                self.logger.info("Successfully connected to Archon MCP server")
            else:
                self.logger.error("Failed to connect to Archon MCP server")
        except Exception as e:
            self.logger.error(f"Error connecting to Archon: {e}")
            results["archon"] = False

        # Connect to Serena
        try:
            serena_connected = await self.serena.connect()
            results["serena"] = serena_connected
            if serena_connected:
                self.logger.info("Successfully connected to Serena MCP server")
            else:
                self.logger.error("Failed to connect to Serena MCP server")
        except Exception as e:
            self.logger.error(f"Error connecting to Serena: {e}")
            results["serena"] = False

        self._connected = all(results.values())

        if self._connected:
            self.logger.info("All MCP servers connected successfully")
            # Start periodic health checks
            self._health_check_task = asyncio.create_task(self._periodic_health_check())
        else:
            failed_servers = [name for name, connected in results.items() if not connected]
            self.logger.warning(f"Failed to connect to servers: {failed_servers}")

        return results

    async def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        # Stop health checks
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Disconnect from servers
        disconnect_tasks = [
            self.archon.disconnect(),
            self.serena.disconnect()
        ]

        await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        self._connected = False
        self.logger.info("Disconnected from all MCP servers")

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health check on all connected servers.

        Returns:
            Dict[str, Dict[str, Any]]: Health status for each server
        """
        results = {}

        # Check Archon health
        try:
            archon_health = await self.archon.health_check()
            results["archon"] = archon_health
        except Exception as e:
            results["archon"] = {"success": False, "error": str(e)}

        # Check Serena health
        try:
            serena_health = await self.serena.health_check()
            results["serena"] = serena_health
        except Exception as e:
            results["serena"] = {"success": False, "error": str(e)}

        return results

    async def get_connection_status(self) -> Dict[str, ConnectionStatus]:
        """
        Get connection status for all servers.

        Returns:
            Dict[str, ConnectionStatus]: Connection status for each server
        """
        return {
            "archon": self.archon.get_connection_status(),
            "serena": self.serena.get_connection_status()
        }

    def is_connected(self) -> bool:
        """
        Check if all servers are connected.

        Returns:
            bool: True if all servers are connected
        """
        return self._connected

    def ensure_connected(self) -> None:
        """
        Ensure all servers are connected.

        Raises:
            MCPConnectionError: If any server is not connected
        """
        if not self._connected:
            raise MCPConnectionError("Not all MCP servers are connected")

    # Coordinated Operations

    async def create_execution_workflow(
        self,
        project_title: str,
        project_description: str,
        implementation_tasks: List[Dict[str, Any]],
        github_repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a complete execution workflow with project and tasks.

        Args:
            project_title: Title for the project
            project_description: Description of the project
            implementation_tasks: List of task specifications
            github_repo: Optional GitHub repository URL

        Returns:
            Dict[str, Any]: Created workflow information
        """
        self.ensure_connected()

        try:
            # Create project in Archon
            project_id = await self.archon.create_execution_project(
                title=project_title,
                description=project_description,
                github_repo=github_repo
            )

            # Create tasks in Archon
            created_tasks = []
            for task_spec in implementation_tasks:
                task_result = await self.archon.manage_task(
                    action="create",
                    project_id=project_id,
                    title=task_spec.get("title"),
                    description=task_spec.get("description"),
                    assignee=task_spec.get("assignee", "AI IDE Agent"),
                    feature=task_spec.get("feature"),
                    task_order=task_spec.get("priority", 50)
                )

                if task_result.get("success"):
                    created_tasks.append(task_result.get("task"))

            # Analyze project structure with Serena
            project_analysis = await self.serena.analyze_project_structure()

            # Store project context in Serena memory
            await self.serena.write_memory(
                memory_name=f"execution_workflow_{project_id}",
                content=f"""# Execution Workflow: {project_title}

## Project Overview
{project_description}

## Implementation Tasks
Total tasks: {len(created_tasks)}
Successfully created: {len(created_tasks)}

## Project Structure Analysis
{project_analysis}

## GitHub Repository
{github_repo or 'No repository specified'}

## Workflow Created
Date: {datetime.now().isoformat()}
Archon Project ID: {project_id}
"""
            )

            return {
                "success": True,
                "project_id": project_id,
                "tasks_created": len(created_tasks),
                "created_tasks": created_tasks,
                "project_analysis": project_analysis
            }

        except Exception as e:
            self.logger.error(f"Failed to create execution workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def execute_task_with_context(
        self,
        task_id: str,
        implementation_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a task with full context from both MCP servers.

        Args:
            task_id: Task ID to execute
            implementation_context: Implementation context and specifications

        Returns:
            Dict[str, Any]: Execution results
        """
        self.ensure_connected()

        try:
            # Get task details from Archon
            task_details = await self.archon.find_tasks(task_id=task_id)
            if not task_details.get("success"):
                raise MCPError(f"Task not found: {task_id}")

            task = task_details.get("task", {})

            # Update task status to "doing"
            await self.archon.update_task_status(
                task_id=task_id,
                status="doing",
                assignee="AI IDE Agent"
            )

            # Analyze implementation opportunities with Serena
            opportunities = await self.serena.find_implementation_opportunities(
                task.get("title", "")
            )

            # Store execution context in memory
            await self.serena.write_memory(
                memory_name=f"task_execution_{task_id}",
                content=f"""# Task Execution: {task.get('title')}

## Task Details
- ID: {task_id}
- Status: doing
- Assignee: AI IDE Agent
- Description: {task.get('description', 'No description')}

## Implementation Context
{implementation_context}

## Implementation Opportunities
{opportunities}

## Execution Started
Date: {datetime.now().isoformat()}
"""
            )

            return {
                "success": True,
                "task_id": task_id,
                "task_details": task,
                "implementation_opportunities": opportunities,
                "execution_status": "started"
            }

        except Exception as e:
            self.logger.error(f"Failed to execute task {task_id}: {e}")

            # Update task status to failed
            try:
                await self.archon.update_task_status(
                    task_id=task_id,
                    status="todo"  # Reset to todo for retry
                )
            except Exception:
                pass

            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }

    async def complete_task_execution(
        self,
        task_id: str,
        implementation_results: Dict[str, Any],
        quality_validation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete task execution and update status across servers.

        Args:
            task_id: Task ID that was executed
            implementation_results: Results of implementation
            quality_validation: Optional quality validation results

        Returns:
            Dict[str, Any]: Completion results
        """
        self.ensure_connected()

        try:
            # Determine final status based on results
            success = implementation_results.get("success", False)
            has_quality_issues = False

            if quality_validation:
                has_quality_issues = not quality_validation.get("all_gates_passed", True)

            if success and not has_quality_issues:
                final_status = "done"
            elif success and has_quality_issues:
                final_status = "review"  # Needs review due to quality issues
            else:
                final_status = "todo"  # Failed, needs retry

            # Update task status in Archon
            await self.archon.update_task_status(
                task_id=task_id,
                status=final_status
            )

            # Update task execution memory in Serena
            await self.serena.write_memory(
                memory_name=f"task_execution_{task_id}_completed",
                content=f"""# Task Execution Completed: {task_id}

## Final Status: {final_status}

## Implementation Results
{implementation_results}

## Quality Validation
{quality_validation or 'No quality validation performed'}

## Completion Date
{datetime.now().isoformat()}
"""
            )

            return {
                "success": True,
                "task_id": task_id,
                "final_status": final_status,
                "implementation_success": success,
                "quality_issues": has_quality_issues
            }

        except Exception as e:
            self.logger.error(f"Failed to complete task execution {task_id}: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e)
            }

    async def _periodic_health_check(self) -> None:
        """Perform periodic health checks on all servers."""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                health_results = await self.health_check_all()

                unhealthy_servers = [
                    name for name, status in health_results.items()
                    if not status.get("success", False)
                ]

                if unhealthy_servers:
                    self.logger.warning(f"Unhealthy MCP servers detected: {unhealthy_servers}")
                else:
                    self.logger.debug("All MCP servers healthy")

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect_all()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect_all()
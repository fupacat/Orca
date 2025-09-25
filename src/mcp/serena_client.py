"""
Serena MCP client for code analysis and manipulation.

Provides high-level interfaces for Serena operations including code search,
symbol analysis, file operations, and intelligent code editing.
"""

import asyncio
import subprocess
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from .base_client import BaseMCPClient, MCPConnectionError, MCPError, MCPValidationError


class SerenaMCPClient(BaseMCPClient):
    """
    Serena MCP client for code analysis and manipulation.

    Handles stdio-based communication with the Serena MCP server for
    intelligent code operations, symbol search, and file manipulation.
    """

    def __init__(
        self,
        timeout: float = 60.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        working_directory: Optional[str] = None
    ):
        """
        Initialize Serena MCP client.

        Args:
            timeout: Operation timeout in seconds
            retry_attempts: Number of retry attempts
            retry_delay: Delay between retries in seconds
            working_directory: Working directory for operations
        """
        super().__init__(
            server_name="serena",
            connection_type="stdio",
            timeout=timeout,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay
        )
        self.working_directory = working_directory or str(Path.cwd())
        self._process: Optional[subprocess.Popen] = None

    async def connect(self) -> bool:
        """
        Establish connection to Serena MCP server.

        Returns:
            bool: True if connection successful
        """
        try:
            # Start Serena MCP server process
            cmd = [
                "uvx",
                "--from",
                "git+https://github.com/oraios/serena",
                "serena"
            ]

            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.working_directory
            )

            # Test connection with a simple health check
            health_result = await self.health_check()
            is_healthy = health_result.get("success", False)

            self.update_connection_status(
                is_connected=True,
                health_status="healthy" if is_healthy else "degraded"
            )

            self.logger.info(f"Connected to Serena MCP server in {self.working_directory}")
            return True

        except Exception as e:
            self.update_connection_status(
                is_connected=False,
                health_status="error",
                error_message=str(e)
            )
            self.logger.error(f"Failed to connect to Serena: {e}")
            return False

    async def disconnect(self) -> None:
        """Close connection to Serena MCP server."""
        if self._process:
            try:
                self._process.terminate()
                await asyncio.wait_for(
                    asyncio.create_task(self._wait_for_process()),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                self._process.kill()
                await asyncio.create_task(self._wait_for_process())
            finally:
                self._process = None

        self.update_connection_status(
            is_connected=False,
            health_status="disconnected"
        )
        self.logger.info("Disconnected from Serena MCP server")

    async def _wait_for_process(self):
        """Wait for process to terminate"""
        if self._process:
            self._process.wait()

    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send request to Serena MCP server via stdio.

        Args:
            method: MCP method name
            params: Method parameters

        Returns:
            Dict[str, Any]: Response data

        Raises:
            MCPConnectionError: If not connected
            MCPError: If request fails
        """
        if not self._process or self._process.poll() is not None:
            raise MCPConnectionError("Not connected to Serena MCP server")

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }

        try:
            # Send request
            request_json = json.dumps(request)
            self._process.stdin.write(request_json + "\n")
            self._process.stdin.flush()

            # Read response
            response_line = self._process.stdout.readline()
            if not response_line:
                raise MCPError("No response from Serena server")

            response = json.loads(response_line.strip())

            if "error" in response:
                raise MCPError(f"Serena error: {response['error']}")

            return self.validate_response(response.get("result", {}))

        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise MCPError(f"Request failed: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Serena MCP server.

        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            # Use list_dir as a simple health check
            result = await self._send_request("list_dir", {"relative_path": ".", "recursive": False})
            return {
                "success": True,
                "status": "healthy",
                "working_directory": self.working_directory
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "working_directory": self.working_directory
            }

    # File and Directory Operations

    async def list_dir(
        self,
        relative_path: str,
        recursive: bool = False,
        skip_ignored_files: bool = False,
        max_answer_chars: int = -1
    ) -> Dict[str, Any]:
        """
        List files and directories in the given path.

        Args:
            relative_path: Relative path to list
            recursive: Whether to scan subdirectories recursively
            skip_ignored_files: Whether to skip ignored files
            max_answer_chars: Maximum characters in response

        Returns:
            Dict[str, Any]: Directory listing
        """
        params = {
            "relative_path": relative_path,
            "recursive": recursive,
            "skip_ignored_files": skip_ignored_files
        }

        if max_answer_chars > 0:
            params["max_answer_chars"] = max_answer_chars

        return await self.with_retry(
            self._send_request,
            "list_dir",
            params
        )

    async def find_file(
        self,
        file_mask: str,
        relative_path: str = "."
    ) -> Dict[str, Any]:
        """
        Find files matching the given mask.

        Args:
            file_mask: Filename or file mask with wildcards
            relative_path: Directory to search in

        Returns:
            Dict[str, Any]: Matching files
        """
        return await self.with_retry(
            self._send_request,
            "find_file",
            {
                "file_mask": file_mask,
                "relative_path": relative_path
            }
        )

    # Code Search and Analysis

    async def search_for_pattern(
        self,
        substring_pattern: str,
        relative_path: str = "",
        restrict_search_to_code_files: bool = False,
        paths_include_glob: str = "",
        paths_exclude_glob: str = "",
        context_lines_before: int = 0,
        context_lines_after: int = 0,
        max_answer_chars: int = -1
    ) -> Dict[str, Any]:
        """
        Search for arbitrary patterns in the codebase.

        Args:
            substring_pattern: Regular expression pattern to search for
            relative_path: Path to restrict search to
            restrict_search_to_code_files: Only search code files
            paths_include_glob: Glob pattern for files to include
            paths_exclude_glob: Glob pattern for files to exclude
            context_lines_before: Lines of context before matches
            context_lines_after: Lines of context after matches
            max_answer_chars: Maximum characters in response

        Returns:
            Dict[str, Any]: Pattern search results
        """
        params = {
            "substring_pattern": substring_pattern,
            "relative_path": relative_path,
            "restrict_search_to_code_files": restrict_search_to_code_files,
            "context_lines_before": context_lines_before,
            "context_lines_after": context_lines_after
        }

        if paths_include_glob:
            params["paths_include_glob"] = paths_include_glob
        if paths_exclude_glob:
            params["paths_exclude_glob"] = paths_exclude_glob
        if max_answer_chars > 0:
            params["max_answer_chars"] = max_answer_chars

        return await self.with_retry(
            self._send_request,
            "search_for_pattern",
            params
        )

    async def get_symbols_overview(
        self,
        relative_path: str,
        max_answer_chars: int = -1
    ) -> Dict[str, Any]:
        """
        Get high-level overview of code symbols in a file.

        Args:
            relative_path: Relative path to the file
            max_answer_chars: Maximum characters in response

        Returns:
            Dict[str, Any]: Symbols overview
        """
        params = {"relative_path": relative_path}

        if max_answer_chars > 0:
            params["max_answer_chars"] = max_answer_chars

        return await self.with_retry(
            self._send_request,
            "get_symbols_overview",
            params
        )

    async def find_symbol(
        self,
        name_path: str,
        relative_path: str = "",
        depth: int = 0,
        include_body: bool = False,
        substring_matching: bool = False,
        include_kinds: Optional[List[int]] = None,
        exclude_kinds: Optional[List[int]] = None,
        max_answer_chars: int = -1
    ) -> Dict[str, Any]:
        """
        Find symbols by name path pattern.

        Args:
            name_path: Name path pattern to search for
            relative_path: File or directory to restrict search to
            depth: Depth to retrieve descendants
            include_body: Include symbol source code
            substring_matching: Use substring matching for last segment
            include_kinds: List of LSP symbol kinds to include
            exclude_kinds: List of LSP symbol kinds to exclude
            max_answer_chars: Maximum characters in response

        Returns:
            Dict[str, Any]: Symbol search results
        """
        params = {
            "name_path": name_path,
            "relative_path": relative_path,
            "depth": depth,
            "include_body": include_body,
            "substring_matching": substring_matching
        }

        if include_kinds:
            params["include_kinds"] = include_kinds
        if exclude_kinds:
            params["exclude_kinds"] = exclude_kinds
        if max_answer_chars > 0:
            params["max_answer_chars"] = max_answer_chars

        return await self.with_retry(
            self._send_request,
            "find_symbol",
            params
        )

    async def find_referencing_symbols(
        self,
        name_path: str,
        relative_path: str,
        include_kinds: Optional[List[int]] = None,
        exclude_kinds: Optional[List[int]] = None,
        max_answer_chars: int = -1
    ) -> Dict[str, Any]:
        """
        Find references to the specified symbol.

        Args:
            name_path: Name path of symbol to find references for
            relative_path: File containing the symbol
            include_kinds: List of LSP symbol kinds to include
            exclude_kinds: List of LSP symbol kinds to exclude
            max_answer_chars: Maximum characters in response

        Returns:
            Dict[str, Any]: Symbol references
        """
        params = {
            "name_path": name_path,
            "relative_path": relative_path
        }

        if include_kinds:
            params["include_kinds"] = include_kinds
        if exclude_kinds:
            params["exclude_kinds"] = exclude_kinds
        if max_answer_chars > 0:
            params["max_answer_chars"] = max_answer_chars

        return await self.with_retry(
            self._send_request,
            "find_referencing_symbols",
            params
        )

    # Code Editing Operations

    async def replace_symbol_body(
        self,
        name_path: str,
        relative_path: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Replace the body of a symbol with new content.

        Args:
            name_path: Name path of symbol to replace
            relative_path: File containing the symbol
            body: New symbol body content

        Returns:
            Dict[str, Any]: Replacement result
        """
        return await self.with_retry(
            self._send_request,
            "replace_symbol_body",
            {
                "name_path": name_path,
                "relative_path": relative_path,
                "body": body
            }
        )

    async def insert_after_symbol(
        self,
        name_path: str,
        relative_path: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Insert content after the specified symbol.

        Args:
            name_path: Name path of symbol to insert after
            relative_path: File containing the symbol
            body: Content to insert

        Returns:
            Dict[str, Any]: Insertion result
        """
        return await self.with_retry(
            self._send_request,
            "insert_after_symbol",
            {
                "name_path": name_path,
                "relative_path": relative_path,
                "body": body
            }
        )

    async def insert_before_symbol(
        self,
        name_path: str,
        relative_path: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Insert content before the specified symbol.

        Args:
            name_path: Name path of symbol to insert before
            relative_path: File containing the symbol
            body: Content to insert

        Returns:
            Dict[str, Any]: Insertion result
        """
        return await self.with_retry(
            self._send_request,
            "insert_before_symbol",
            {
                "name_path": name_path,
                "relative_path": relative_path,
                "body": body
            }
        )

    # Memory Operations

    async def write_memory(
        self,
        memory_name: str,
        content: str,
        max_answer_chars: int = -1
    ) -> Dict[str, Any]:
        """
        Write information to memory for future tasks.

        Args:
            memory_name: Meaningful name for the memory
            content: Content to store
            max_answer_chars: Maximum characters in response

        Returns:
            Dict[str, Any]: Write result
        """
        params = {
            "memory_name": memory_name,
            "content": content
        }

        if max_answer_chars > 0:
            params["max_answer_chars"] = max_answer_chars

        return await self.with_retry(
            self._send_request,
            "write_memory",
            params
        )

    async def read_memory(
        self,
        memory_file_name: str,
        max_answer_chars: int = -1
    ) -> Dict[str, Any]:
        """
        Read content from a memory file.

        Args:
            memory_file_name: Name of memory file to read
            max_answer_chars: Maximum characters in response

        Returns:
            Dict[str, Any]: Memory content
        """
        params = {"memory_file_name": memory_file_name}

        if max_answer_chars > 0:
            params["max_answer_chars"] = max_answer_chars

        return await self.with_retry(
            self._send_request,
            "read_memory",
            params
        )

    async def list_memories(self) -> Dict[str, Any]:
        """
        List available memory files.

        Returns:
            Dict[str, Any]: Available memories
        """
        return await self.with_retry(
            self._send_request,
            "list_memories"
        )

    # High-level workflow helpers

    async def analyze_project_structure(self) -> Dict[str, Any]:
        """
        Analyze project structure and provide overview.

        Returns:
            Dict[str, Any]: Project structure analysis
        """
        # Get recursive directory listing
        structure = await self.list_dir(".", recursive=True, skip_ignored_files=True)

        # Get symbols overview for main source files
        main_files = []
        if "files" in structure:
            for file_path in structure["files"]:
                if file_path.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c", ".rs")):
                    main_files.append(file_path)

        symbols_info = {}
        for file_path in main_files[:10]:  # Limit to first 10 files
            try:
                symbols = await self.get_symbols_overview(file_path)
                symbols_info[file_path] = symbols
            except Exception as e:
                self.logger.warning(f"Could not get symbols for {file_path}: {e}")

        return {
            "structure": structure,
            "main_files": main_files,
            "symbols_overview": symbols_info
        }

    async def find_implementation_opportunities(self, feature_description: str) -> List[Dict[str, Any]]:
        """
        Find opportunities to implement a feature in the codebase.

        Args:
            feature_description: Description of the feature to implement

        Returns:
            List[Dict[str, Any]]: Implementation opportunities
        """
        # Search for related patterns and symbols
        opportunities = []

        # Search for similar patterns in code
        try:
            pattern_results = await self.search_for_pattern(
                feature_description.lower().replace(" ", ".*"),
                restrict_search_to_code_files=True
            )
            opportunities.append({
                "type": "pattern_match",
                "results": pattern_results
            })
        except Exception as e:
            self.logger.warning(f"Pattern search failed: {e}")

        # Search for related symbols
        try:
            symbol_results = await self.find_symbol(
                feature_description.lower().replace(" ", "_"),
                substring_matching=True
            )
            opportunities.append({
                "type": "symbol_match",
                "results": symbol_results
            })
        except Exception as e:
            self.logger.warning(f"Symbol search failed: {e}")

        return opportunities
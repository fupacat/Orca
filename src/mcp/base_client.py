"""
Base MCP client with shared functionality for all MCP server interactions.

Provides common patterns for error handling, connection management, and
async operations across different MCP server implementations.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pydantic import BaseModel


class MCPError(Exception):
    """Base exception for MCP operations"""
    pass


class MCPConnectionError(MCPError):
    """Exception for MCP connection failures"""
    pass


class MCPTimeoutError(MCPError):
    """Exception for MCP operation timeouts"""
    pass


class MCPValidationError(MCPError):
    """Exception for MCP response validation failures"""
    pass


class ConnectionStatus(BaseModel):
    """Connection status information"""
    is_connected: bool
    server_name: str
    connection_type: str  # 'http', 'stdio', etc.
    last_check: datetime
    health_status: str
    error_message: Optional[str] = None


class BaseMCPClient(ABC):
    """
    Base class for MCP client implementations with common functionality.

    Provides standardized error handling, connection management, logging,
    and async patterns for all MCP server interactions.
    """

    def __init__(
        self,
        server_name: str,
        connection_type: str,
        timeout: float = 30.0,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize base MCP client.

        Args:
            server_name: Name of the MCP server
            connection_type: Type of connection (http, stdio, etc.)
            timeout: Default timeout for operations in seconds
            retry_attempts: Number of retry attempts for failed operations
            retry_delay: Delay between retry attempts in seconds
        """
        self.server_name = server_name
        self.connection_type = connection_type
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(f"mcp.{server_name}")

        # Connection state
        self._connection_status = ConnectionStatus(
            is_connected=False,
            server_name=server_name,
            connection_type=connection_type,
            last_check=datetime.now(),
            health_status="unknown"
        )

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to MCP server.

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to MCP server."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on MCP server.

        Returns:
            Dict[str, Any]: Health status information
        """
        pass

    async def is_healthy(self) -> bool:
        """
        Check if MCP server is healthy and responsive.

        Returns:
            bool: True if server is healthy, False otherwise
        """
        try:
            health_result = await self.health_check()
            return health_result.get("success", False)
        except Exception as e:
            self.logger.warning(f"Health check failed: {e}")
            return False

    async def with_retry(self, operation, *args, **kwargs) -> Any:
        """
        Execute operation with retry logic.

        Args:
            operation: Async function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Any: Result of the operation

        Raises:
            MCPError: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.retry_attempts + 1):
            try:
                if attempt > 0:
                    self.logger.info(f"Retry attempt {attempt}/{self.retry_attempts} for {operation.__name__}")
                    await asyncio.sleep(self.retry_delay * attempt)

                result = await asyncio.wait_for(
                    operation(*args, **kwargs),
                    timeout=self.timeout
                )
                return result

            except asyncio.TimeoutError as e:
                last_exception = MCPTimeoutError(f"Operation {operation.__name__} timed out after {self.timeout}s")
                self.logger.warning(f"Timeout on attempt {attempt + 1}: {e}")

            except MCPConnectionError as e:
                last_exception = e
                self.logger.warning(f"Connection error on attempt {attempt + 1}: {e}")

            except Exception as e:
                last_exception = MCPError(f"Unexpected error in {operation.__name__}: {str(e)}")
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")

        # All attempts failed
        self.logger.error(f"All {self.retry_attempts + 1} attempts failed for {operation.__name__}")
        raise last_exception

    def validate_response(self, response: Dict[str, Any], required_fields: list = None) -> Dict[str, Any]:
        """
        Validate MCP server response format.

        Args:
            response: Response from MCP server
            required_fields: List of required fields in response

        Returns:
            Dict[str, Any]: Validated response

        Raises:
            MCPValidationError: If response format is invalid
        """
        if not isinstance(response, dict):
            raise MCPValidationError(f"Invalid response type: expected dict, got {type(response)}")

        if required_fields:
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                raise MCPValidationError(f"Missing required fields: {missing_fields}")

        # Check for error in response
        if "error" in response:
            error_msg = response.get("error", "Unknown error")
            raise MCPError(f"Server returned error: {error_msg}")

        return response

    def update_connection_status(
        self,
        is_connected: bool,
        health_status: str = "unknown",
        error_message: Optional[str] = None
    ) -> None:
        """
        Update internal connection status.

        Args:
            is_connected: Current connection state
            health_status: Health status description
            error_message: Error message if applicable
        """
        self._connection_status = ConnectionStatus(
            is_connected=is_connected,
            server_name=self.server_name,
            connection_type=self.connection_type,
            last_check=datetime.now(),
            health_status=health_status,
            error_message=error_message
        )

    def get_connection_status(self) -> ConnectionStatus:
        """
        Get current connection status.

        Returns:
            ConnectionStatus: Current connection information
        """
        return self._connection_status.copy()

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    def __repr__(self) -> str:
        """String representation of client"""
        return f"{self.__class__.__name__}(server_name='{self.server_name}', type='{self.connection_type}')"
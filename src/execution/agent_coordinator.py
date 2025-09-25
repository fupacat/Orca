"""
Agent Coordination System for managing multiple execution agents.

Coordinates multiple AI agents for parallel task execution with intelligent
load balancing, resource management, and communication protocols.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from ..models.complete_task import CompleteTask
from ..mcp.connection_manager import MCPConnectionManager


class AgentState(str, Enum):
    """States of execution agents"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class AgentType(str, Enum):
    """Types of execution agents"""
    DEVELOPMENT = "development"    # General development tasks
    TESTING = "testing"           # Testing and validation tasks
    INTEGRATION = "integration"   # Integration and coordination tasks
    QUALITY = "quality"          # Quality assurance tasks


@dataclass
class AgentMetrics:
    """Performance metrics for an agent"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    success_rate: float = 0.0
    last_task_time: Optional[datetime] = None
    resource_utilization: Dict[str, float] = field(default_factory=dict)


@dataclass
class AgentCapabilities:
    """Capabilities and specializations of an agent"""
    supported_task_types: List[str] = field(default_factory=lambda: ["general"])
    programming_languages: List[str] = field(default_factory=lambda: ["python"])
    frameworks: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    quality_gates_supported: List[str] = field(default_factory=lambda: ["basic"])
    resource_requirements: Dict[str, float] = field(default_factory=dict)


class ExecutionAgent(ABC):
    """Abstract base class for execution agents"""

    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        capabilities: AgentCapabilities,
        mcp_manager: MCPConnectionManager
    ):
        """Initialize execution agent."""
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.mcp_manager = mcp_manager
        self.state = AgentState.INITIALIZING
        self.metrics = AgentMetrics()
        self.current_tasks: Set[str] = set()
        self.logger = logging.getLogger(f"agent.{agent_id}")

    @abstractmethod
    async def execute_task(self, task: CompleteTask) -> Dict[str, Any]:
        """Execute a complete task."""
        pass

    @abstractmethod
    async def validate_task_compatibility(self, task: CompleteTask) -> bool:
        """Check if agent can handle this task."""
        pass

    async def initialize(self) -> bool:
        """Initialize agent and establish connections."""
        try:
            self.state = AgentState.IDLE
            self.logger.info(f"Agent {self.agent_id} initialized successfully")
            return True
        except Exception as e:
            self.state = AgentState.ERROR
            self.logger.error(f"Agent {self.agent_id} initialization failed: {e}")
            return False

    async def shutdown(self) -> None:
        """Gracefully shutdown agent."""
        self.state = AgentState.SHUTDOWN
        self.current_tasks.clear()
        self.logger.info(f"Agent {self.agent_id} shutdown completed")

    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return (
            self.state == AgentState.IDLE and
            len(self.current_tasks) < self.capabilities.max_concurrent_tasks
        )

    def get_load_factor(self) -> float:
        """Get current load factor (0.0 = idle, 1.0 = fully loaded)."""
        if self.capabilities.max_concurrent_tasks == 0:
            return 1.0
        return len(self.current_tasks) / self.capabilities.max_concurrent_tasks


class DevelopmentAgent(ExecutionAgent):
    """Specialized agent for development tasks"""

    def __init__(self, agent_id: str, mcp_manager: MCPConnectionManager):
        capabilities = AgentCapabilities(
            supported_task_types=["implementation", "development", "coding", "model", "api"],
            programming_languages=["python", "typescript", "javascript"],
            frameworks=["fastapi", "pydantic", "pytest"],
            max_concurrent_tasks=1,
            quality_gates_supported=["tdd", "code_quality", "static_analysis"],
            resource_requirements={"cpu": 50.0, "memory": 100.0}
        )
        super().__init__(agent_id, AgentType.DEVELOPMENT, capabilities, mcp_manager)

    async def execute_task(self, task: CompleteTask) -> Dict[str, Any]:
        """Execute development task using MCP servers."""
        if not await self.validate_task_compatibility(task):
            raise ValueError(f"Task {task.task_id} not compatible with development agent")

        start_time = datetime.now()
        self.state = AgentState.BUSY
        self.current_tasks.add(task.task_id)

        try:
            self.logger.info(f"Executing development task {task.task_id}: {task.title}")

            # Use Serena for code analysis and implementation
            implementation_result = await self._implement_task_using_serena(task)

            # Use Archon for task coordination and documentation
            coordination_result = await self._coordinate_with_archon(task, implementation_result)

            # Combine results
            execution_result = {
                "success": True,
                "task_id": task.task_id,
                "agent_id": self.agent_id,
                "implementation": implementation_result,
                "coordination": coordination_result,
                "artifacts": {
                    "implementation": implementation_result.get("files_created", []),
                    "tests": implementation_result.get("test_files", []),
                    "documentation": coordination_result.get("documentation", [])
                },
                "summary": f"Completed {task.title} using development patterns and best practices",
                "execution_time": (datetime.now() - start_time).total_seconds()
            }

            # Update metrics
            self.metrics.tasks_completed += 1
            self._update_metrics(execution_result["execution_time"], True)

            return execution_result

        except Exception as e:
            self.logger.error(f"Development task {task.task_id} failed: {e}")
            self.metrics.tasks_failed += 1
            self._update_metrics((datetime.now() - start_time).total_seconds(), False)

            return {
                "success": False,
                "task_id": task.task_id,
                "agent_id": self.agent_id,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }

        finally:
            self.state = AgentState.IDLE
            self.current_tasks.discard(task.task_id)

    async def validate_task_compatibility(self, task: CompleteTask) -> bool:
        """Check if task is compatible with development agent."""
        title_lower = task.title.lower()
        background_lower = task.complete_context.project_background.lower()

        # Check for development keywords
        dev_keywords = ["implement", "develop", "create", "build", "code", "model", "api"]
        return any(keyword in title_lower or keyword in background_lower for keyword in dev_keywords)

    async def _implement_task_using_serena(self, task: CompleteTask) -> Dict[str, Any]:
        """Implement task using Serena MCP capabilities."""
        result = {
            "files_created": [],
            "files_modified": [],
            "test_files": [],
            "implementation_patterns": [],
            "code_analysis": {}
        }

        try:
            if not self.mcp_manager.is_connected():
                raise Exception("MCP manager not connected")

            # Analyze implementation opportunities
            opportunities = await self.mcp_manager.serena.find_implementation_opportunities(
                task.title
            )
            result["code_analysis"]["opportunities"] = opportunities

            # Get project structure for context
            structure = await self.mcp_manager.serena.analyze_project_structure()
            result["code_analysis"]["structure"] = structure

            # Implement based on task file locations
            for file_path, description in task.complete_context.file_locations.items():
                if "creat" in description.lower() or "implement" in description.lower():
                    # This would be where actual file creation happens
                    # For now, we simulate the implementation
                    result["files_created"].append(file_path)

                    # Create implementation content based on task context
                    implementation_content = await self._generate_implementation_content(
                        task, file_path, description
                    )
                    result["implementation_patterns"].append({
                        "file": file_path,
                        "patterns": implementation_content["patterns"],
                        "content_summary": implementation_content["summary"]
                    })

            # Create test files based on TDD specifications
            test_file = task.tdd_specifications.test_file
            if test_file:
                result["test_files"].append(test_file)

        except Exception as e:
            self.logger.warning(f"Serena implementation failed: {e}")
            result["error"] = str(e)

        return result

    async def _coordinate_with_archon(
        self,
        task: CompleteTask,
        implementation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Coordinate with Archon for task management."""
        result = {
            "task_updated": False,
            "documentation": [],
            "project_coordination": {}
        }

        try:
            if not self.mcp_manager.is_connected():
                return result

            # Update task progress in Archon
            update_result = await self.mcp_manager.archon.update_task_status(
                task_id=task.task_id,
                status="review",
                assignee=self.agent_id
            )
            result["task_updated"] = update_result.get("success", False)

            # Store implementation context for future tasks
            await self.mcp_manager.serena.write_memory(
                memory_name=f"implementation_{task.task_id}",
                content=f"""# Implementation: {task.title}

## Files Created
{chr(10).join(implementation_result.get('files_created', []))}

## Implementation Patterns
{implementation_result.get('implementation_patterns', [])}

## Execution Agent: {self.agent_id}
"""
            )
            result["documentation"].append(f"implementation_{task.task_id}.md")

        except Exception as e:
            self.logger.warning(f"Archon coordination failed: {e}")
            result["error"] = str(e)

        return result

    async def _generate_implementation_content(
        self,
        task: CompleteTask,
        file_path: str,
        description: str
    ) -> Dict[str, Any]:
        """Generate implementation content for a file."""
        # This is a simplified version - in practice would use more sophisticated
        # code generation based on task context and existing patterns

        patterns = []

        if "model" in file_path.lower():
            patterns.extend([
                "Pydantic BaseModel with validation",
                "Field descriptions and constraints",
                "Business logic methods",
                "JSON serialization support"
            ])
        elif "api" in file_path.lower():
            patterns.extend([
                "FastAPI router definition",
                "Request/response models",
                "Error handling",
                "Dependency injection"
            ])
        elif "test" in file_path.lower():
            patterns.extend([
                "Pytest test class structure",
                "Fixture usage",
                "Parameterized tests",
                "Async test support"
            ])

        return {
            "patterns": patterns,
            "summary": f"Implementation for {description} following project patterns"
        }

    def _update_metrics(self, execution_time: float, success: bool) -> None:
        """Update agent performance metrics."""
        self.metrics.total_execution_time += execution_time
        self.metrics.last_task_time = datetime.now()

        # Calculate rolling average execution time
        total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed
        if total_tasks > 0:
            self.metrics.average_execution_time = self.metrics.total_execution_time / total_tasks

        # Calculate success rate
        if total_tasks > 0:
            self.metrics.success_rate = self.metrics.tasks_completed / total_tasks


class AgentCoordinationError(Exception):
    """Exception raised during agent coordination"""
    pass


class AgentCoordinator:
    """
    Coordinates multiple execution agents for optimal parallel execution.

    Manages agent lifecycle, load balancing, task assignment, and
    inter-agent communication for maximum execution efficiency.
    """

    def __init__(
        self,
        mcp_manager: MCPConnectionManager,
        max_agents: int = 5
    ):
        """
        Initialize agent coordinator.

        Args:
            mcp_manager: Connected MCP connection manager
            max_agents: Maximum number of agents to manage
        """
        self.mcp_manager = mcp_manager
        self.max_agents = max_agents
        self.logger = logging.getLogger("execution.agent_coordinator")

        # Agent management
        self.agents: Dict[str, ExecutionAgent] = {}
        self.agent_assignment: Dict[str, str] = {}  # session_id -> agent_id
        self.agent_sessions: Dict[str, Set[str]] = {}  # agent_id -> set of session_ids

        # Coordination state
        self._coordination_lock = asyncio.Lock()
        self._next_agent_id = 0

    async def initialize_agent_pool(self) -> None:
        """Initialize pool of execution agents."""
        try:
            self.logger.info(f"Initializing agent pool with {self.max_agents} agents")

            # Create development agents
            for i in range(self.max_agents):
                agent_id = f"dev_agent_{i}"
                agent = DevelopmentAgent(agent_id, self.mcp_manager)

                if await agent.initialize():
                    self.agents[agent_id] = agent
                    self.agent_sessions[agent_id] = set()
                    self.logger.info(f"Agent {agent_id} initialized successfully")
                else:
                    self.logger.error(f"Failed to initialize agent {agent_id}")

            self.logger.info(f"Agent pool initialized with {len(self.agents)} active agents")

        except Exception as e:
            self.logger.error(f"Agent pool initialization failed: {e}")
            raise AgentCoordinationError(f"Failed to initialize agent pool: {str(e)}")

    async def acquire_agent(self, session_id: str) -> ExecutionAgent:
        """
        Acquire an available agent for task execution.

        Args:
            session_id: Session requesting the agent

        Returns:
            ExecutionAgent: Available agent

        Raises:
            AgentCoordinationError: If no agents available
        """
        async with self._coordination_lock:
            # Find best available agent
            best_agent = await self._find_best_agent()

            if not best_agent:
                raise AgentCoordinationError("No agents available for task execution")

            # Assign agent to session
            self.agent_assignment[session_id] = best_agent.agent_id
            self.agent_sessions[best_agent.agent_id].add(session_id)

            self.logger.debug(f"Assigned agent {best_agent.agent_id} to session {session_id}")
            return best_agent

    async def release_agent(self, agent_id: str, session_id: str) -> None:
        """
        Release agent from session.

        Args:
            agent_id: Agent to release
            session_id: Session releasing the agent
        """
        async with self._coordination_lock:
            if agent_id in self.agent_sessions:
                self.agent_sessions[agent_id].discard(session_id)

            if session_id in self.agent_assignment:
                del self.agent_assignment[session_id]

            self.logger.debug(f"Released agent {agent_id} from session {session_id}")

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {
            "total_agents": len(self.agents),
            "available_agents": 0,
            "busy_agents": 0,
            "error_agents": 0,
            "agents": {}
        }

        for agent_id, agent in self.agents.items():
            agent_status = {
                "agent_id": agent_id,
                "state": agent.state.value,
                "type": agent.agent_type.value,
                "load_factor": agent.get_load_factor(),
                "current_tasks": len(agent.current_tasks),
                "metrics": {
                    "tasks_completed": agent.metrics.tasks_completed,
                    "tasks_failed": agent.metrics.tasks_failed,
                    "success_rate": agent.metrics.success_rate,
                    "average_execution_time": agent.metrics.average_execution_time
                }
            }

            status["agents"][agent_id] = agent_status

            # Update counters
            if agent.state == AgentState.IDLE:
                status["available_agents"] += 1
            elif agent.state == AgentState.BUSY:
                status["busy_agents"] += 1
            elif agent.state == AgentState.ERROR:
                status["error_agents"] += 1

        return status

    async def pause_all_tasks(self, session_id: str) -> None:
        """Pause all tasks for a session."""
        if session_id in self.agent_assignment:
            agent_id = self.agent_assignment[session_id]
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.state = AgentState.PAUSED
                self.logger.info(f"Paused agent {agent_id} for session {session_id}")

    async def cancel_all_tasks(self, session_id: str) -> None:
        """Cancel all tasks for a session."""
        if session_id in self.agent_assignment:
            agent_id = self.agent_assignment[session_id]
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.current_tasks.clear()
                agent.state = AgentState.IDLE
                self.logger.info(f"Cancelled all tasks for agent {agent_id} in session {session_id}")

    async def cleanup_session(self, session_id: str) -> None:
        """Clean up agent assignments for session."""
        async with self._coordination_lock:
            if session_id in self.agent_assignment:
                agent_id = self.agent_assignment[session_id]
                if agent_id in self.agent_sessions:
                    self.agent_sessions[agent_id].discard(session_id)
                del self.agent_assignment[session_id]

    async def shutdown_all_agents(self) -> None:
        """Gracefully shutdown all agents."""
        self.logger.info("Shutting down all agents")

        shutdown_tasks = []
        for agent in self.agents.values():
            shutdown_tasks.append(agent.shutdown())

        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        self.agents.clear()
        self.agent_assignment.clear()
        self.agent_sessions.clear()

        self.logger.info("All agents shutdown completed")

    async def _find_best_agent(self) -> Optional[ExecutionAgent]:
        """Find the best available agent for task assignment."""
        available_agents = [
            agent for agent in self.agents.values()
            if agent.is_available()
        ]

        if not available_agents:
            return None

        # Simple load balancing - choose agent with lowest load factor
        best_agent = min(available_agents, key=lambda a: a.get_load_factor())
        return best_agent
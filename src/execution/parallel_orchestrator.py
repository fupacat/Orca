"""
Parallel Execution Orchestrator - Core engine for coordinated parallel task execution.

Orchestrates the execution of complete tasks across multiple agents with intelligent
coordination, dependency management, and quality gate enforcement.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from ..models.complete_task import CompleteTask
from ..models.execution_graph import ExecutionGraph, ExecutionLayer
from ..models.result_models import ExecutionResult, TaskResult, TaskExecutionStatus
from ..models.quality_models import QualityResult
from ..mcp.connection_manager import MCPConnectionManager
from .agent_coordinator import AgentCoordinator
from .quality_gate_engine import QualityGateEngine
from .execution_monitor import ExecutionMonitor


class OrchestrationState(str, Enum):
    """States of the orchestration process"""
    INITIALIZING = "initializing"
    READY = "ready"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionSession:
    """Represents an active execution session"""
    session_id: str
    execution_graph: ExecutionGraph
    start_time: datetime
    current_layer: int = 0
    state: OrchestrationState = OrchestrationState.INITIALIZING
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)
    running_tasks: Set[str] = field(default_factory=set)
    task_results: Dict[str, TaskResult] = field(default_factory=dict)
    session_metadata: Dict[str, Any] = field(default_factory=dict)


class ParallelExecutionError(Exception):
    """Exception raised during parallel execution"""
    pass


class ParallelExecutionOrchestrator:
    """
    Core parallel execution orchestrator.

    Coordinates the execution of complete tasks across multiple agents with
    intelligent dependency management, quality enforcement, and real-time monitoring.
    """

    def __init__(
        self,
        mcp_manager: MCPConnectionManager,
        max_concurrent_agents: int = 5,
        quality_enforcement: bool = True,
        monitoring_enabled: bool = True
    ):
        """
        Initialize parallel execution orchestrator.

        Args:
            mcp_manager: Connected MCP connection manager
            max_concurrent_agents: Maximum concurrent execution agents
            quality_enforcement: Enable quality gate enforcement
            monitoring_enabled: Enable execution monitoring
        """
        self.mcp_manager = mcp_manager
        self.max_concurrent_agents = max_concurrent_agents
        self.quality_enforcement = quality_enforcement
        self.monitoring_enabled = monitoring_enabled
        self.logger = logging.getLogger("execution.orchestrator")

        # Initialize coordination components
        self.agent_coordinator = AgentCoordinator(
            mcp_manager=mcp_manager,
            max_agents=max_concurrent_agents
        )

        if quality_enforcement:
            self.quality_gate_engine = QualityGateEngine(mcp_manager=mcp_manager)

        if monitoring_enabled:
            self.execution_monitor = ExecutionMonitor()

        # Active execution sessions
        self.active_sessions: Dict[str, ExecutionSession] = {}
        self._execution_lock = asyncio.Lock()

        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            "session_started": [],
            "layer_started": [],
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "layer_completed": [],
            "session_completed": [],
            "session_failed": []
        }

    async def execute_implementation_plan(
        self,
        execution_graph: ExecutionGraph,
        execution_options: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute implementation plan with parallel coordination.

        Args:
            execution_graph: Optimized execution graph
            execution_options: Execution configuration options

        Returns:
            ExecutionResult: Complete execution results

        Raises:
            ParallelExecutionError: If execution fails
        """
        try:
            # Create execution session
            session = await self._create_execution_session(execution_graph, execution_options)

            self.logger.info(
                f"Starting parallel execution session {session.session_id} "
                f"with {execution_graph.total_tasks} tasks across {len(execution_graph.execution_layers)} layers"
            )

            # Initialize monitoring
            if self.monitoring_enabled:
                await self.execution_monitor.start_session_monitoring(session)

            # Execute session
            execution_result = await self._execute_session(session)

            self.logger.info(
                f"Execution session {session.session_id} completed: "
                f"{execution_result.successful_tasks}/{execution_result.total_tasks} tasks successful"
            )

            return execution_result

        except Exception as e:
            self.logger.error(f"Parallel execution failed: {e}")
            raise ParallelExecutionError(f"Failed to execute implementation plan: {str(e)}")

    async def pause_execution(self, session_id: str) -> bool:
        """
        Pause active execution session.

        Args:
            session_id: Session to pause

        Returns:
            bool: True if successfully paused
        """
        async with self._execution_lock:
            if session_id not in self.active_sessions:
                return False

            session = self.active_sessions[session_id]
            if session.state == OrchestrationState.EXECUTING:
                session.state = OrchestrationState.PAUSED

                # Pause all running tasks
                await self.agent_coordinator.pause_all_tasks(session_id)

                self.logger.info(f"Execution session {session_id} paused")
                return True

        return False

    async def resume_execution(self, session_id: str) -> bool:
        """
        Resume paused execution session.

        Args:
            session_id: Session to resume

        Returns:
            bool: True if successfully resumed
        """
        async with self._execution_lock:
            if session_id not in self.active_sessions:
                return False

            session = self.active_sessions[session_id]
            if session.state == OrchestrationState.PAUSED:
                session.state = OrchestrationState.EXECUTING

                # Resume execution from current layer
                await self._resume_session_execution(session)

                self.logger.info(f"Execution session {session_id} resumed")
                return True

        return False

    async def cancel_execution(self, session_id: str) -> bool:
        """
        Cancel active execution session.

        Args:
            session_id: Session to cancel

        Returns:
            bool: True if successfully cancelled
        """
        async with self._execution_lock:
            if session_id not in self.active_sessions:
                return False

            session = self.active_sessions[session_id]
            session.state = OrchestrationState.CANCELLED

            # Cancel all running tasks
            await self.agent_coordinator.cancel_all_tasks(session_id)

            # Clean up session
            await self._cleanup_session(session)

            self.logger.info(f"Execution session {session_id} cancelled")
            return True

    async def get_execution_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current execution status.

        Args:
            session_id: Session to query

        Returns:
            Dict[str, Any]: Current execution status or None
        """
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]

        status = {
            "session_id": session_id,
            "state": session.state.value,
            "current_layer": session.current_layer,
            "total_layers": len(session.execution_graph.execution_layers),
            "completed_tasks": len(session.completed_tasks),
            "failed_tasks": len(session.failed_tasks),
            "running_tasks": len(session.running_tasks),
            "total_tasks": session.execution_graph.total_tasks,
            "elapsed_time_minutes": (datetime.now() - session.start_time).total_seconds() / 60,
            "progress_percentage": len(session.completed_tasks) / session.execution_graph.total_tasks * 100
        }

        # Add monitoring data if available
        if self.monitoring_enabled:
            monitoring_data = await self.execution_monitor.get_session_metrics(session_id)
            status["monitoring"] = monitoring_data

        return status

    async def register_event_callback(self, event_type: str, callback: Callable) -> None:
        """Register callback for execution events."""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)

    async def _create_execution_session(
        self,
        execution_graph: ExecutionGraph,
        options: Optional[Dict[str, Any]]
    ) -> ExecutionSession:
        """Create new execution session."""
        session_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(execution_graph) % 10000}"

        session = ExecutionSession(
            session_id=session_id,
            execution_graph=execution_graph,
            start_time=datetime.now(),
            session_metadata={
                "execution_options": options or {},
                "graph_metrics": {
                    "total_tasks": execution_graph.total_tasks,
                    "total_layers": len(execution_graph.execution_layers),
                    "parallelization_factor": execution_graph.parallelization_factor,
                    "estimated_duration": execution_graph.total_estimated_duration_minutes
                }
            }
        )

        self.active_sessions[session_id] = session

        # Fire session started event
        await self._fire_event("session_started", session)

        return session

    async def _execute_session(self, session: ExecutionSession) -> ExecutionResult:
        """Execute complete session with all layers."""
        session.state = OrchestrationState.EXECUTING
        execution_errors = []

        try:
            # Execute each layer in sequence
            for layer_index, layer in enumerate(session.execution_graph.execution_layers):
                session.current_layer = layer_index

                self.logger.info(
                    f"Starting execution layer {layer_index + 1}/{len(session.execution_graph.execution_layers)} "
                    f"with {len(layer.tasks)} tasks"
                )

                # Fire layer started event
                await self._fire_event("layer_started", session, layer)

                # Execute layer with parallel coordination
                layer_results = await self._execute_layer(session, layer)

                # Process layer results
                layer_success = await self._process_layer_results(session, layer, layer_results)

                if not layer_success and not session.execution_graph.execution_layers[layer_index:]:
                    # Critical layer failure - stop execution
                    break

                # Fire layer completed event
                await self._fire_event("layer_completed", session, layer)

        except Exception as e:
            execution_errors.append(str(e))
            session.state = OrchestrationState.FAILED
            self.logger.error(f"Session execution failed: {e}")

        # Create final execution result
        execution_result = await self._create_execution_result(session, execution_errors)

        # Update session state
        if execution_result.is_successful():
            session.state = OrchestrationState.COMPLETED
            await self._fire_event("session_completed", session, execution_result)
        else:
            session.state = OrchestrationState.FAILED
            await self._fire_event("session_failed", session, execution_result)

        # Cleanup session
        await self._cleanup_session(session)

        return execution_result

    async def _execute_layer(
        self,
        session: ExecutionSession,
        layer: ExecutionLayer
    ) -> List[TaskResult]:
        """Execute all tasks in a layer with parallel coordination."""
        # Check dependencies are satisfied
        await self._verify_layer_dependencies(session, layer)

        # Create task execution coroutines
        task_coroutines = []
        for task in layer.tasks:
            if task.task_id not in session.completed_tasks:
                session.running_tasks.add(task.task_id)
                coroutine = self._execute_single_task(session, task)
                task_coroutines.append(coroutine)

        # Execute tasks in parallel
        if task_coroutines:
            layer_results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        else:
            layer_results = []

        # Convert exceptions to failed task results
        processed_results = []
        for i, result in enumerate(layer_results):
            if isinstance(result, Exception):
                # Create failed task result
                task = layer.tasks[i]
                failed_result = TaskResult(
                    task_id=task.task_id,
                    status=TaskExecutionStatus.FAILED,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    agent_id="unknown",
                    error_details={"error": str(result)}
                )
                processed_results.append(failed_result)
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_single_task(
        self,
        session: ExecutionSession,
        task: CompleteTask
    ) -> TaskResult:
        """Execute a single task with full coordination."""
        try:
            self.logger.info(f"Starting execution of task {task.task_id}")

            # Fire task started event
            await self._fire_event("task_started", session, task)

            # Update task status in Archon
            if self.mcp_manager.is_connected():
                try:
                    await self.mcp_manager.archon.update_task_status(
                        task_id=task.task_id,
                        status="doing",
                        assignee="AI Execution Agent"
                    )
                except Exception as e:
                    self.logger.warning(f"Could not update task status in Archon: {e}")

            # Get available agent
            agent = await self.agent_coordinator.acquire_agent(session.session_id)

            start_time = datetime.now()

            try:
                # Execute task through agent
                execution_result = await agent.execute_task(task)

                # Validate execution result
                if not execution_result.get("success", False):
                    raise Exception(f"Task execution failed: {execution_result.get('error', 'Unknown error')}")

                # Create task result
                task_result = TaskResult(
                    task_id=task.task_id,
                    status=TaskExecutionStatus.COMPLETED,
                    start_time=start_time,
                    end_time=datetime.now(),
                    agent_id=agent.agent_id,
                    implementation_artifacts=execution_result.get("artifacts", {}).get("implementation", []),
                    test_artifacts=execution_result.get("artifacts", {}).get("tests", []),
                    documentation_artifacts=execution_result.get("artifacts", {}).get("documentation", []),
                    implementation_summary=execution_result.get("summary", "")
                )

                # Quality gate validation if enabled
                if self.quality_enforcement:
                    quality_result = await self.quality_gate_engine.validate_task_quality(
                        task, task_result, execution_result
                    )
                    task_result.quality_validation = quality_result

                    # Check if quality gates passed
                    if not quality_result.all_quality_gates_passed():
                        task_result.status = TaskExecutionStatus.FAILED
                        task_result.error_details = {
                            "type": "quality_gate_failure",
                            "failed_gates": [
                                gate for gate, passed in {
                                    "tdd": quality_result.tdd_validation.meets_requirements(),
                                    "security": quality_result.security_validation.meets_security_requirements(),
                                    "performance": quality_result.performance_validation.performance_requirements_met,
                                    "code_quality": quality_result.code_quality_validation.meets_quality_standards()
                                }.items() if not passed
                            ]
                        }

                # Update session tracking
                session.running_tasks.discard(task.task_id)

                if task_result.is_successful():
                    session.completed_tasks.add(task.task_id)

                    # Update task status in Archon
                    if self.mcp_manager.is_connected():
                        try:
                            await self.mcp_manager.archon.update_task_status(
                                task_id=task.task_id,
                                status="done"
                            )
                        except Exception as e:
                            self.logger.warning(f"Could not update completed task status: {e}")

                    await self._fire_event("task_completed", session, task, task_result)
                else:
                    session.failed_tasks.add(task.task_id)
                    await self._fire_event("task_failed", session, task, task_result)

                session.task_results[task.task_id] = task_result

                return task_result

            finally:
                # Release agent
                await self.agent_coordinator.release_agent(agent.agent_id, session.session_id)

        except Exception as e:
            self.logger.error(f"Task {task.task_id} execution failed: {e}")

            # Create failed task result
            session.running_tasks.discard(task.task_id)
            session.failed_tasks.add(task.task_id)

            failed_result = TaskResult(
                task_id=task.task_id,
                status=TaskExecutionStatus.FAILED,
                start_time=start_time if 'start_time' in locals() else datetime.now(),
                end_time=datetime.now(),
                agent_id="unknown",
                error_details={"error": str(e)}
            )

            session.task_results[task.task_id] = failed_result
            await self._fire_event("task_failed", session, task, failed_result)

            return failed_result

    async def _verify_layer_dependencies(
        self,
        session: ExecutionSession,
        layer: ExecutionLayer
    ) -> None:
        """Verify all dependencies for layer are satisfied."""
        for task in layer.tasks:
            for dep_id in task.depends_on:
                if dep_id not in session.completed_tasks:
                    raise ParallelExecutionError(
                        f"Dependency not satisfied: task {task.task_id} depends on {dep_id} "
                        f"which has not completed successfully"
                    )

    async def _process_layer_results(
        self,
        session: ExecutionSession,
        layer: ExecutionLayer,
        results: List[TaskResult]
    ) -> bool:
        """Process results from layer execution."""
        successful_tasks = sum(1 for result in results if result.is_successful())
        total_tasks = len(results)

        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0

        self.logger.info(
            f"Layer {layer.layer_number} completed: {successful_tasks}/{total_tasks} tasks successful "
            f"({success_rate:.1%} success rate)"
        )

        # Determine if layer was successful enough to continue
        # For now, continue if at least 80% of tasks succeeded
        return success_rate >= 0.8

    async def _create_execution_result(
        self,
        session: ExecutionSession,
        execution_errors: List[str]
    ) -> ExecutionResult:
        """Create final execution result from session."""
        end_time = datetime.now()
        total_duration = (end_time - session.start_time).total_seconds()

        # Gather all task results
        task_results = list(session.task_results.values())

        # Calculate counts
        successful_count = len(session.completed_tasks)
        failed_count = len(session.failed_tasks)
        cancelled_count = session.execution_graph.total_tasks - successful_count - failed_count

        # Create execution result
        execution_result = ExecutionResult(
            execution_id=session.session_id,
            start_time=session.start_time,
            end_time=end_time,
            total_duration_seconds=total_duration,
            total_tasks=session.execution_graph.total_tasks,
            successful_tasks=successful_count,
            failed_tasks=failed_count,
            cancelled_tasks=cancelled_count,
            task_results=task_results,
            parallel_execution_stats={
                "total_layers": len(session.execution_graph.execution_layers),
                "parallelization_factor": session.execution_graph.parallelization_factor,
                "average_tasks_per_layer": session.execution_graph.total_tasks / len(session.execution_graph.execution_layers)
            },
            error_summary=execution_errors
        )

        # Update task counts and generate quality summary
        execution_result.update_task_counts()
        execution_result.generate_quality_summary()

        return execution_result

    async def _cleanup_session(self, session: ExecutionSession) -> None:
        """Clean up execution session resources."""
        # Stop monitoring if enabled
        if self.monitoring_enabled:
            await self.execution_monitor.stop_session_monitoring(session.session_id)

        # Clean up agent coordinator
        await self.agent_coordinator.cleanup_session(session.session_id)

        # Remove from active sessions
        if session.session_id in self.active_sessions:
            del self.active_sessions[session.session_id]

        self.logger.info(f"Cleaned up execution session {session.session_id}")

    async def _resume_session_execution(self, session: ExecutionSession) -> None:
        """Resume execution from current layer."""
        # This would continue execution from where it was paused
        # Implementation would depend on the specific pause/resume strategy
        pass

    async def _fire_event(self, event_type: str, *args) -> None:
        """Fire event to registered callbacks."""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    await callback(*args)
                except Exception as e:
                    self.logger.warning(f"Event callback error for {event_type}: {e}")
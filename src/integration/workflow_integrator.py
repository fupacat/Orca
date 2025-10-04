"""
Workflow Integration Module for seamless StartWorkflow-to-Execution transitions.

This module provides the critical bridge between Orca's existing planning
workflow (StartWorkflow) and the new parallel execution capabilities,
enabling automatic transition from plan.md to live implementation.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import json

from ..context.task_context_generator import TaskContextGenerator
from ..analysis.dependency_analyzer import DependencyAnalyzer
from ..execution.parallel_orchestrator import ParallelExecutionOrchestrator
from ..mcp.connection_manager import MCPConnectionManager
from ..models.complete_task import CompleteTask
from ..models.execution_graph import ExecutionGraph
from ..models.result_models import ExecutionResult


class WorkflowIntegrationError(Exception):
    """Exception raised during workflow integration operations"""
    pass


class WorkflowIntegrator:
    """
    Core integration layer connecting Orca planning to execution.

    Provides seamless transition from StartWorkflow artifacts (plan.md)
    to live parallel implementation execution with full context preservation.
    """

    def __init__(
        self,
        project_root: str,
        execution_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize workflow integrator.

        Args:
            project_root: Root directory of the Orca project
            execution_config: Optional execution configuration overrides
        """
        self.project_root = Path(project_root)
        self.execution_config = execution_config or self._get_default_execution_config()
        self.logger = logging.getLogger("orca.integration")

        # Initialize core components
        self.task_generator = TaskContextGenerator()
        self.dependency_analyzer = DependencyAnalyzer()
        self.mcp_manager = MCPConnectionManager()
        self.execution_orchestrator = ParallelExecutionOrchestrator()

        # State tracking
        self.current_session_id: Optional[str] = None
        self.integration_metadata: Dict[str, Any] = {}

    async def execute_workflow_plan(
        self,
        plan_path: Optional[str] = None,
        execution_mode: str = "hybrid"
    ) -> ExecutionResult:
        """
        Execute implementation plan created by StartWorkflow.

        Args:
            plan_path: Path to plan.md file (defaults to project_root/plan.md)
            execution_mode: Execution strategy (aggressive, conservative, hybrid)

        Returns:
            ExecutionResult: Complete execution results with metrics
        """
        try:
            self.logger.info("Starting workflow plan execution")

            # Step 1: Locate and validate plan file
            plan_file = await self._locate_plan_file(plan_path)
            if not plan_file.exists():
                raise WorkflowIntegrationError(f"Plan file not found: {plan_file}")

            # Step 2: Initialize MCP connections
            await self.mcp_manager.initialize()

            # Step 3: Read and parse plan file
            import json
            self.logger.info(f"Reading plan file: {plan_file}")
            plan_content = plan_file.read_text(encoding='utf-8')

            # Convert markdown plan to dict format expected by parser
            # For now, pass the file path for the parser to handle
            implementation_plan = {
                "plan_path": str(plan_file),
                "plan_content": plan_content
            }

            # Generate complete tasks from plan
            self.logger.info("Generating complete task contexts from plan")
            complete_tasks = await self.task_generator.generate_complete_tasks_from_plan(
                implementation_plan,
                project_context={"project_root": str(self.project_root)}
            )

            if not complete_tasks:
                raise WorkflowIntegrationError("No executable tasks found in plan")

            self.logger.info(f"Generated {len(complete_tasks)} complete tasks")

            # Step 4: Analyze dependencies and create execution graph
            self.logger.info("Analyzing task dependencies")
            dependency_graph = await self.dependency_analyzer.analyze_task_dependencies(
                complete_tasks,
                analysis_mode="comprehensive"
            )

            execution_graph = ExecutionGraph.from_dependency_graph(
                dependency_graph,
                optimization_strategy=execution_mode
            )

            # Step 5: Store integration metadata
            await self._store_integration_metadata(complete_tasks, execution_graph)

            # Step 6: Execute with orchestrator
            self.logger.info(f"Starting parallel execution with {execution_mode} strategy")
            result = await self.execution_orchestrator.execute_implementation_plan(
                execution_graph,
                project_root=str(self.project_root),
                execution_config=self.execution_config
            )

            # Step 7: Post-execution integration
            await self._post_execution_integration(result)

            self.logger.info("Workflow plan execution completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise WorkflowIntegrationError(f"Failed to execute workflow plan: {str(e)}")

    async def validate_plan_executability(self, plan_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate that a plan file can be successfully executed.

        Args:
            plan_path: Path to plan.md file

        Returns:
            Dict containing validation results and recommendations
        """
        try:
            plan_file = await self._locate_plan_file(plan_path)

            # Generate tasks without full context
            complete_tasks = await self.task_generator.generate_complete_tasks_from_plan(
                str(plan_file),
                project_root=str(self.project_root),
                validate_only=True
            )

            # Analyze readiness
            validation_results = {
                "is_executable": True,
                "total_tasks": len(complete_tasks),
                "stateless_ready_tasks": 0,
                "missing_context_tasks": [],
                "dependency_issues": [],
                "recommendations": []
            }

            for task in complete_tasks:
                if task.is_stateless_ready():
                    validation_results["stateless_ready_tasks"] += 1
                else:
                    validation_results["missing_context_tasks"].append({
                        "task_id": task.task_id,
                        "title": task.title,
                        "missing_elements": task.get_missing_context_elements()
                    })

            # Check dependencies
            if len(complete_tasks) > 1:
                try:
                    dependency_graph = await self.dependency_analyzer.analyze_task_dependencies(
                        complete_tasks,
                        analysis_mode="basic"
                    )
                    if dependency_graph.has_cycles:
                        validation_results["is_executable"] = False
                        validation_results["dependency_issues"].append("Circular dependencies detected")

                except Exception as e:
                    validation_results["dependency_issues"].append(f"Dependency analysis failed: {str(e)}")

            # Generate recommendations
            readiness_rate = validation_results["stateless_ready_tasks"] / validation_results["total_tasks"]
            if readiness_rate < 0.7:
                validation_results["recommendations"].append(
                    "Consider enriching task contexts before execution"
                )

            if validation_results["dependency_issues"]:
                validation_results["recommendations"].append(
                    "Resolve dependency issues before execution"
                )

            return validation_results

        except Exception as e:
            return {
                "is_executable": False,
                "error": str(e),
                "recommendations": ["Fix plan file issues before attempting execution"]
            }

    async def get_execution_preview(self, plan_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate execution preview showing parallel execution layers.

        Args:
            plan_path: Path to plan.md file

        Returns:
            Dict containing execution preview with timing estimates
        """
        try:
            plan_file = await self._locate_plan_file(plan_path)

            # Generate complete tasks
            complete_tasks = await self.task_generator.generate_complete_tasks_from_plan(
                str(plan_file),
                project_root=str(self.project_root)
            )

            # Create execution graph
            dependency_graph = await self.dependency_analyzer.analyze_task_dependencies(
                complete_tasks,
                analysis_mode="basic"
            )

            execution_graph = ExecutionGraph.from_dependency_graph(
                dependency_graph,
                optimization_strategy="hybrid"
            )

            # Generate preview
            preview = {
                "total_tasks": len(complete_tasks),
                "execution_layers": len(execution_graph.layers),
                "max_parallelism": max(len(layer.tasks) for layer in execution_graph.layers),
                "estimated_duration_minutes": execution_graph.estimated_total_duration / 60,
                "parallel_efficiency": execution_graph.parallel_efficiency,
                "layer_breakdown": []
            }

            for i, layer in enumerate(execution_graph.layers):
                layer_info = {
                    "layer_number": i + 1,
                    "task_count": len(layer.tasks),
                    "estimated_duration_minutes": layer.estimated_duration / 60,
                    "tasks": [
                        {
                            "task_id": task.task_id,
                            "title": task.title,
                            "estimated_duration_minutes": task.estimated_duration_minutes
                        }
                        for task in layer.tasks
                    ]
                }
                preview["layer_breakdown"].append(layer_info)

            return preview

        except Exception as e:
            return {
                "error": f"Failed to generate execution preview: {str(e)}"
            }

    async def resume_execution(self, session_id: str) -> ExecutionResult:
        """
        Resume a previously interrupted execution session.

        Args:
            session_id: ID of session to resume

        Returns:
            ExecutionResult: Resumed execution results
        """
        try:
            self.logger.info(f"Resuming execution session {session_id}")

            # Load session metadata
            session_metadata = await self._load_session_metadata(session_id)
            if not session_metadata:
                raise WorkflowIntegrationError(f"Session {session_id} not found")

            # Initialize MCP connections
            await self.mcp_manager.initialize()

            # Resume with orchestrator
            result = await self.execution_orchestrator.resume_execution(
                session_id,
                project_root=str(self.project_root)
            )

            return result

        except Exception as e:
            self.logger.error(f"Failed to resume execution {session_id}: {e}")
            raise WorkflowIntegrationError(f"Failed to resume execution: {str(e)}")

    async def _locate_plan_file(self, plan_path: Optional[str] = None) -> Path:
        """Locate the plan.md file to execute"""
        if plan_path:
            return Path(plan_path).resolve()

        # Standard Orca plan location
        default_plan = self.project_root / "plan.md"
        if default_plan.exists():
            return default_plan

        # Search for plan files in project
        plan_candidates = list(self.project_root.glob("**/plan.md"))
        if plan_candidates:
            return plan_candidates[0]

        raise WorkflowIntegrationError("No plan.md file found in project")

    async def _store_integration_metadata(
        self,
        complete_tasks: List[CompleteTask],
        execution_graph: ExecutionGraph
    ) -> None:
        """Store integration metadata for session tracking"""
        metadata = {
            "integration_version": "1.0.0",
            "total_tasks": len(complete_tasks),
            "execution_layers": len(execution_graph.layers),
            "project_root": str(self.project_root),
            "created_at": asyncio.get_event_loop().time()
        }

        self.integration_metadata = metadata

        # Store to file for persistence
        metadata_file = self.project_root / ".orca" / "integration_metadata.json"
        metadata_file.parent.mkdir(exist_ok=True)

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    async def _post_execution_integration(self, result: ExecutionResult) -> None:
        """Handle post-execution integration tasks"""
        # Update project artifacts
        if result.success:
            self.logger.info("Execution successful - updating project artifacts")

            # Create execution summary
            summary_file = self.project_root / "execution_summary.md"
            await self._create_execution_summary(result, summary_file)

            # Update .orca directory with results
            await self._archive_execution_results(result)
        else:
            self.logger.warning("Execution failed - creating failure report")
            await self._create_failure_report(result)

    async def _create_execution_summary(self, result: ExecutionResult, summary_file: Path) -> None:
        """Create markdown summary of execution results"""
        summary_content = f"""# Execution Summary

**Session ID**: {result.session_id}
**Status**: {'✅ Success' if result.success else '❌ Failed'}
**Duration**: {result.total_duration_seconds / 60:.1f} minutes
**Completed Tasks**: {len(result.completed_tasks)}/{result.total_tasks}

## Performance Metrics
- **Parallel Efficiency**: {result.parallel_efficiency:.1%}
- **Tasks per Minute**: {result.tasks_per_minute:.1f}
- **Quality Score**: {result.quality_metrics.overall_score:.1%}

## Task Results
"""

        for task_result in result.task_results:
            status_emoji = "✅" if task_result.success else "❌"
            summary_content += f"- {status_emoji} **{task_result.task_id}**: {task_result.title}\n"

        with open(summary_file, 'w') as f:
            f.write(summary_content)

    async def _create_failure_report(self, result: ExecutionResult) -> None:
        """Create detailed failure report for debugging"""
        report_file = self.project_root / "execution_failure_report.md"

        report_content = f"""# Execution Failure Report

**Session ID**: {result.session_id}
**Failed at**: {result.end_time}
**Total Duration**: {result.total_duration_seconds / 60:.1f} minutes

## Failure Analysis
"""

        failed_tasks = [tr for tr in result.task_results if not tr.success]
        for task_result in failed_tasks:
            report_content += f"""
### Task: {task_result.task_id}
**Error**: {task_result.error_message}
**Duration**: {task_result.duration_seconds / 60:.1f} minutes

```
{task_result.execution_log}
```
"""

        with open(report_file, 'w') as f:
            f.write(report_content)

    async def _archive_execution_results(self, result: ExecutionResult) -> None:
        """Archive execution results to .orca directory"""
        archive_dir = self.project_root / ".orca" / "executions" / result.session_id
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Store detailed results as JSON
        results_file = archive_dir / "execution_results.json"
        with open(results_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2, default=str)

    async def _load_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session metadata for resumption"""
        metadata_file = self.project_root / ".orca" / "executions" / session_id / "execution_results.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file, 'r') as f:
            return json.load(f)

    def _get_default_execution_config(self) -> Dict[str, Any]:
        """Get default execution configuration"""
        return {
            "max_parallel_agents": 3,
            "task_timeout_minutes": 30,
            "quality_gates_enabled": True,
            "auto_retry_failed_tasks": True,
            "max_retries": 2,
            "monitoring_enabled": True,
            "metrics_collection_interval": 10.0,
            "alert_on_failures": True
        }
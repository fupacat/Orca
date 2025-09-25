"""
Task Context Generator for intelligent stateless task context creation.

Transforms implementation plans into complete task contexts with embedded information
for independent parallel execution by development agents.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

from ..models.complete_task import CompleteTask, TaskContext, TDDSpecification, QualityGateRequirements
from ..mcp.connection_manager import MCPConnectionManager
from .implementation_plan_parser import ImplementationPlanParser
from .context_enrichment_engine import ContextEnrichmentEngine


class TaskContextGenerationError(Exception):
    """Exception raised during task context generation"""
    pass


class TaskContextGenerator:
    """
    Intelligent task context generator for stateless execution.

    Transforms implementation plans into complete task contexts that contain
    all necessary information for independent parallel execution.
    """

    def __init__(
        self,
        mcp_manager: MCPConnectionManager,
        working_directory: Optional[str] = None,
        quality_requirements: Optional[QualityGateRequirements] = None
    ):
        """
        Initialize task context generator.

        Args:
            mcp_manager: Connected MCP connection manager
            working_directory: Working directory for operations
            quality_requirements: Default quality gate requirements
        """
        self.mcp_manager = mcp_manager
        self.working_directory = working_directory or str(Path.cwd())
        self.default_quality_requirements = quality_requirements or QualityGateRequirements()
        self.logger = logging.getLogger("context.generator")

        # Initialize sub-components
        self.plan_parser = ImplementationPlanParser()
        self.enrichment_engine = ContextEnrichmentEngine(mcp_manager)

    async def generate_complete_tasks_from_plan(
        self,
        implementation_plan: Dict[str, Any],
        project_context: Optional[Dict[str, Any]] = None
    ) -> List[CompleteTask]:
        """
        Generate complete tasks from an implementation plan.

        Args:
            implementation_plan: Parsed implementation plan
            project_context: Additional project context information

        Returns:
            List[CompleteTask]: Complete tasks with embedded context

        Raises:
            TaskContextGenerationError: If generation fails
        """
        try:
            self.logger.info("Starting task context generation from implementation plan")

            # Parse implementation plan
            parsed_plan = await self.plan_parser.parse_implementation_plan(implementation_plan)
            self.logger.info(f"Parsed plan with {len(parsed_plan.tasks)} tasks")

            # Extract global project context
            global_context = await self._extract_global_project_context(
                parsed_plan, project_context
            )

            # Generate complete tasks
            complete_tasks = []
            for task_spec in parsed_plan.tasks:
                complete_task = await self._generate_complete_task(
                    task_spec, global_context, parsed_plan
                )
                complete_tasks.append(complete_task)

            self.logger.info(f"Generated {len(complete_tasks)} complete tasks")

            # Validate tasks for stateless readiness
            stateless_ready_count = sum(1 for task in complete_tasks if task.is_stateless_ready())
            self.logger.info(f"{stateless_ready_count}/{len(complete_tasks)} tasks are stateless ready")

            return complete_tasks

        except Exception as e:
            self.logger.error(f"Task context generation failed: {e}")
            raise TaskContextGenerationError(f"Failed to generate task contexts: {str(e)}")

    async def enrich_task_context(
        self,
        task: CompleteTask,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> CompleteTask:
        """
        Enrich a task's context with additional information.

        Args:
            task: Task to enrich
            additional_context: Additional context to incorporate

        Returns:
            CompleteTask: Task with enriched context
        """
        try:
            self.logger.info(f"Enriching context for task: {task.task_id}")

            # Use enrichment engine to enhance context
            enriched_context = await self.enrichment_engine.enrich_task_context(
                task.complete_context, additional_context
            )

            # Create enriched task
            enriched_task = task.copy(update={"complete_context": enriched_context})

            # Validate enriched task
            if not enriched_task.is_stateless_ready():
                self.logger.warning(f"Task {task.task_id} is not stateless ready after enrichment")

            return enriched_task

        except Exception as e:
            self.logger.error(f"Context enrichment failed for task {task.task_id}: {e}")
            raise TaskContextGenerationError(f"Failed to enrich task context: {str(e)}")

    async def _extract_global_project_context(
        self,
        parsed_plan: Any,
        project_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract global project context information.

        Args:
            parsed_plan: Parsed implementation plan
            project_context: Additional project context

        Returns:
            Dict[str, Any]: Global project context
        """
        # Start with plan-based context
        global_context = {
            "project_title": parsed_plan.title,
            "project_description": parsed_plan.description,
            "project_background": parsed_plan.background,
            "architecture_approach": parsed_plan.architecture,
            "technology_stack": parsed_plan.get("technology_stack", []),
            "quality_requirements": parsed_plan.quality_requirements,
            "total_tasks": len(parsed_plan.tasks)
        }

        # Merge with provided context
        if project_context:
            global_context.update(project_context)

        # Enrich with codebase analysis if available
        try:
            if self.mcp_manager.is_connected():
                codebase_analysis = await self.mcp_manager.serena.analyze_project_structure()
                global_context["codebase_analysis"] = codebase_analysis
                self.logger.info("Added codebase analysis to global context")
        except Exception as e:
            self.logger.warning(f"Could not analyze codebase: {e}")

        # Add generation metadata
        global_context["context_generation"] = {
            "generated_at": datetime.now().isoformat(),
            "working_directory": self.working_directory,
            "generator_version": "1.0.0"
        }

        return global_context

    async def _generate_complete_task(
        self,
        task_spec: Dict[str, Any],
        global_context: Dict[str, Any],
        parsed_plan: Any
    ) -> CompleteTask:
        """
        Generate a complete task from task specification.

        Args:
            task_spec: Task specification from plan
            global_context: Global project context
            parsed_plan: Full parsed implementation plan

        Returns:
            CompleteTask: Complete task with embedded context
        """
        # Generate task context
        task_context = await self._generate_task_context(task_spec, global_context, parsed_plan)

        # Generate TDD specifications
        tdd_specs = await self._generate_tdd_specifications(task_spec, task_context)

        # Determine quality requirements
        quality_requirements = self._determine_quality_requirements(task_spec)

        # Create complete task
        complete_task = CompleteTask(
            task_id=task_spec.get("id", f"task_{hash(task_spec.get('title', 'unknown'))}"),
            title=task_spec.get("title", "Untitled Task"),
            complete_context=task_context,
            tdd_specifications=tdd_specs,
            quality_gates=quality_requirements,
            acceptance_criteria=task_spec.get("acceptance_criteria", []),
            estimated_duration_minutes=int(task_spec.get("estimated_hours", 2) * 60),
            priority=task_spec.get("priority", 50),
            depends_on=task_spec.get("dependencies", [])
        )

        return complete_task

    async def _generate_task_context(
        self,
        task_spec: Dict[str, Any],
        global_context: Dict[str, Any],
        parsed_plan: Any
    ) -> TaskContext:
        """
        Generate embedded task context.

        Args:
            task_spec: Task specification
            global_context: Global project context
            parsed_plan: Full parsed plan

        Returns:
            TaskContext: Complete embedded context
        """
        # Build comprehensive project background
        project_background = self._build_project_background(task_spec, global_context)

        # Extract architecture context relevant to this task
        architecture_context = self._extract_architecture_context(task_spec, global_context)

        # Extract requirements context
        requirements_context = self._extract_requirements_context(task_spec, global_context)

        # Generate implementation guidance
        implementation_guidance = await self._generate_implementation_guidance(
            task_spec, global_context, parsed_plan
        )

        # Determine file locations
        file_locations = self._determine_file_locations(task_spec, global_context)

        # Extract dependencies
        dependencies = task_spec.get("dependencies", [])

        # Build environment context
        environment_context = self._build_environment_context(task_spec, global_context)

        return TaskContext(
            project_background=project_background,
            architecture_context=architecture_context,
            requirements_context=requirements_context,
            implementation_guidance=implementation_guidance,
            file_locations=file_locations,
            dependencies=dependencies,
            environment_context=environment_context
        )

    def _build_project_background(
        self,
        task_spec: Dict[str, Any],
        global_context: Dict[str, Any]
    ) -> str:
        """Build comprehensive project background for the task."""
        background_parts = [
            f"Project: {global_context.get('project_title', 'Unknown Project')}",
            f"Description: {global_context.get('project_description', 'No description')}",
            f"Background: {global_context.get('project_background', 'No background')}",
            f"Task Context: {task_spec.get('description', 'No task description')}",
            f"Architecture: {global_context.get('architecture_approach', {}).get('approach', 'Not specified')}",
            f"Total Project Tasks: {global_context.get('total_tasks', 0)}"
        ]

        # Add codebase information if available
        if "codebase_analysis" in global_context:
            analysis = global_context["codebase_analysis"]
            background_parts.append(f"Codebase Structure: {len(analysis.get('main_files', []))} main files analyzed")

        return " | ".join(background_parts)

    def _extract_architecture_context(
        self,
        task_spec: Dict[str, Any],
        global_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract architecture context relevant to the task."""
        architecture_context = {
            "approach": global_context.get("architecture_approach", {}),
            "technology_stack": global_context.get("technology_stack", []),
            "task_specific_patterns": task_spec.get("architectural_patterns", [])
        }

        # Add integration patterns for this task
        if "integration" in task_spec.get("description", "").lower():
            architecture_context["integration_patterns"] = [
                "Hybrid extension architecture",
                "Stateless agent coordination",
                "MCP server integration"
            ]

        return architecture_context

    def _extract_requirements_context(
        self,
        task_spec: Dict[str, Any],
        global_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract requirements context for the task."""
        return {
            "task_requirements": task_spec.get("requirements", []),
            "global_requirements": global_context.get("quality_requirements", {}),
            "acceptance_criteria": task_spec.get("acceptance_criteria", []),
            "constraints": task_spec.get("constraints", [])
        }

    async def _generate_implementation_guidance(
        self,
        task_spec: Dict[str, Any],
        global_context: Dict[str, Any],
        parsed_plan: Any
    ) -> Dict[str, Any]:
        """Generate detailed implementation guidance."""
        guidance = {
            "implementation_approach": task_spec.get("implementation_approach", "Follow project standards"),
            "code_patterns": task_spec.get("code_patterns", []),
            "testing_strategy": task_spec.get("testing_strategy", "Unit tests with pytest"),
            "quality_standards": global_context.get("quality_requirements", {})
        }

        # Add task-specific guidance based on task type
        task_title = task_spec.get("title", "").lower()

        if "model" in task_title or "pydantic" in task_title:
            guidance["specific_patterns"] = [
                "Use Pydantic BaseModel for all data models",
                "Include comprehensive validation with Field descriptions",
                "Implement JSON serialization and schema generation",
                "Add business logic methods for model behavior"
            ]
        elif "api" in task_title or "endpoint" in task_title:
            guidance["specific_patterns"] = [
                "Follow REST API conventions",
                "Use proper HTTP status codes",
                "Implement comprehensive error handling",
                "Add request/response validation"
            ]
        elif "test" in task_title:
            guidance["specific_patterns"] = [
                "Follow pytest conventions and patterns",
                "Use fixtures for test data and setup",
                "Implement comprehensive test coverage",
                "Include integration and unit tests"
            ]

        # Search for related patterns in codebase if connected
        try:
            if self.mcp_manager.is_connected():
                opportunities = await self.mcp_manager.serena.find_implementation_opportunities(
                    task_spec.get("title", "")
                )
                guidance["codebase_opportunities"] = opportunities
        except Exception as e:
            self.logger.warning(f"Could not find implementation opportunities: {e}")

        return guidance

    def _determine_file_locations(
        self,
        task_spec: Dict[str, Any],
        global_context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Determine file creation and modification locations."""
        base_locations = task_spec.get("file_locations", {})

        # Add standard locations based on task type
        task_title = task_spec.get("title", "").lower()
        task_id = task_spec.get("id", "unknown")

        if "model" in task_title:
            base_locations.update({
                f"src/models/{task_id}.py": f"Data models for {task_spec.get('title', 'task')}",
                f"tests/test_{task_id}.py": f"Unit tests for {task_spec.get('title', 'task')}"
            })
        elif "api" in task_title:
            base_locations.update({
                f"src/api/{task_id}.py": f"API endpoints for {task_spec.get('title', 'task')}",
                f"tests/test_api_{task_id}.py": f"API tests for {task_spec.get('title', 'task')}"
            })
        elif "util" in task_title or "helper" in task_title:
            base_locations.update({
                f"src/utils/{task_id}.py": f"Utility functions for {task_spec.get('title', 'task')}",
                f"tests/test_utils_{task_id}.py": f"Utility tests for {task_spec.get('title', 'task')}"
            })

        return base_locations

    def _build_environment_context(
        self,
        task_spec: Dict[str, Any],
        global_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build environment context for the task."""
        return {
            "python_version": "3.11+",
            "required_packages": global_context.get("technology_stack", []),
            "development_environment": "Cross-platform (Windows/Linux/WSL)",
            "working_directory": self.working_directory,
            "mcp_servers": ["archon", "serena"],
            "task_specific_requirements": task_spec.get("environment_requirements", [])
        }

    async def _generate_tdd_specifications(
        self,
        task_spec: Dict[str, Any],
        task_context: TaskContext
    ) -> TDDSpecification:
        """Generate TDD specifications for the task."""
        task_id = task_spec.get("id", "unknown")

        # Generate test file path
        test_file = f"tests/test_{task_id}.py"
        if "model" in task_spec.get("title", "").lower():
            test_file = f"tests/test_models_{task_id}.py"
        elif "api" in task_spec.get("title", "").lower():
            test_file = f"tests/test_api_{task_id}.py"

        # Generate test cases based on task requirements
        test_cases = []

        # Add standard test cases
        test_cases.extend([
            f"@test {task_spec.get('title', 'Task')} core functionality validation",
            f"@test {task_spec.get('title', 'Task')} error handling and edge cases",
            f"@test {task_spec.get('title', 'Task')} integration with existing components"
        ])

        # Add acceptance criteria as test cases
        for criterion in task_spec.get("acceptance_criteria", []):
            test_cases.append(f"@test {criterion}")

        return TDDSpecification(
            test_file=test_file,
            test_cases=test_cases,
            coverage_requirements="95%+ test coverage for all new code",
            test_framework="pytest with asyncio support",
            mock_requirements=task_spec.get("mock_requirements", [])
        )

    def _determine_quality_requirements(
        self,
        task_spec: Dict[str, Any]
    ) -> QualityGateRequirements:
        """Determine quality gate requirements for the task."""
        # Start with default requirements
        requirements = self.default_quality_requirements.copy()

        # Customize based on task criticality or type
        task_priority = task_spec.get("priority", 50)

        if task_priority >= 80:  # High priority tasks
            requirements.tdd_requirements["minimum_coverage"] = 0.98
            requirements.security_requirements["vulnerability_scanning"] = True
            requirements.performance_requirements["benchmark_execution"] = True

        return requirements

    async def validate_generated_tasks(self, tasks: List[CompleteTask]) -> Dict[str, Any]:
        """
        Validate generated tasks for completeness and readiness.

        Args:
            tasks: List of generated complete tasks

        Returns:
            Dict[str, Any]: Validation results
        """
        validation_results = {
            "total_tasks": len(tasks),
            "stateless_ready": 0,
            "validation_errors": [],
            "warnings": []
        }

        for task in tasks:
            try:
                # Check stateless readiness
                if task.is_stateless_ready():
                    validation_results["stateless_ready"] += 1
                else:
                    validation_results["warnings"].append(
                        f"Task {task.task_id} is not stateless ready"
                    )

                # Validate context completeness
                if not task.complete_context.has_complete_context():
                    validation_results["validation_errors"].append(
                        f"Task {task.task_id} has incomplete context"
                    )

                # Validate TDD specifications
                if len(task.tdd_specifications.test_cases) == 0:
                    validation_results["warnings"].append(
                        f"Task {task.task_id} has no test cases defined"
                    )

            except Exception as e:
                validation_results["validation_errors"].append(
                    f"Validation error for task {task.task_id}: {str(e)}"
                )

        return validation_results
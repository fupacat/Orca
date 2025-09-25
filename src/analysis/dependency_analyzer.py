"""
Dependency Analyzer for intelligent task dependency analysis and graph generation.

Analyzes task relationships, identifies dependencies, and creates optimized
execution graphs for parallel task coordination.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict, deque
from datetime import datetime

from ..models.complete_task import CompleteTask
from ..models.execution_graph import (
    DependencyGraph, ExecutionGraph, ExecutionLayer,
    TaskDependency, DependencyType
)


class DependencyAnalysisError(Exception):
    """Exception raised during dependency analysis"""
    pass


class CircularDependencyError(DependencyAnalysisError):
    """Exception raised when circular dependencies are detected"""
    pass


class DependencyAnalyzer:
    """
    Intelligent dependency analyzer for task execution planning.

    Analyzes task dependencies, detects conflicts, and generates optimized
    execution graphs for maximum parallel efficiency.
    """

    def __init__(self):
        """Initialize dependency analyzer."""
        self.logger = logging.getLogger("analysis.dependencies")

    async def analyze_task_dependencies(
        self,
        tasks: List[CompleteTask]
    ) -> DependencyGraph:
        """
        Analyze dependencies between tasks and create dependency graph.

        Args:
            tasks: List of complete tasks to analyze

        Returns:
            DependencyGraph: Analyzed dependency graph

        Raises:
            DependencyAnalysisError: If analysis fails
            CircularDependencyError: If circular dependencies detected
        """
        try:
            self.logger.info(f"Analyzing dependencies for {len(tasks)} tasks")

            # Extract task IDs and explicit dependencies
            task_ids = [task.task_id for task in tasks]
            explicit_dependencies = await self._extract_explicit_dependencies(tasks)

            # Analyze implicit dependencies
            implicit_dependencies = await self._analyze_implicit_dependencies(tasks)

            # Combine all dependencies
            all_dependencies = explicit_dependencies + implicit_dependencies

            # Create dependency graph
            dependency_graph = DependencyGraph(
                tasks=task_ids,
                dependencies=all_dependencies
            )

            # Validate graph (check for cycles, invalid references)
            await self._validate_dependency_graph(dependency_graph, task_ids)

            self.logger.info(f"Created dependency graph with {len(all_dependencies)} dependencies")

            return dependency_graph

        except Exception as e:
            self.logger.error(f"Dependency analysis failed: {e}")
            raise DependencyAnalysisError(f"Failed to analyze dependencies: {str(e)}")

    async def create_execution_graph(
        self,
        tasks: List[CompleteTask],
        dependency_graph: DependencyGraph
    ) -> ExecutionGraph:
        """
        Create execution graph with parallel execution layers.

        Args:
            tasks: List of complete tasks
            dependency_graph: Analyzed dependency graph

        Returns:
            ExecutionGraph: Optimized execution graph

        Raises:
            DependencyAnalysisError: If graph creation fails
        """
        try:
            self.logger.info("Creating execution graph with parallel layers")

            # Create task lookup for easy access
            task_lookup = {task.task_id: task for task in tasks}

            # Generate execution layers using topological sorting
            execution_layers = await self._generate_execution_layers(
                dependency_graph, task_lookup
            )

            # Calculate parallelization metrics
            parallelization_factor = await self._calculate_parallelization_factor(
                execution_layers, len(tasks)
            )

            # Calculate total estimated duration
            total_duration = await self._calculate_total_duration(execution_layers)

            # Create execution graph
            execution_graph = ExecutionGraph(
                dependency_graph=dependency_graph,
                execution_layers=execution_layers,
                parallelization_factor=parallelization_factor,
                total_estimated_duration_minutes=total_duration,
                total_tasks=len(tasks)
            )

            self.logger.info(
                f"Created execution graph with {len(execution_layers)} layers, "
                f"{parallelization_factor:.2f} parallelization factor"
            )

            return execution_graph

        except Exception as e:
            self.logger.error(f"Execution graph creation failed: {e}")
            raise DependencyAnalysisError(f"Failed to create execution graph: {str(e)}")

    async def optimize_for_parallel_execution(
        self,
        execution_graph: ExecutionGraph,
        optimization_goals: Optional[Dict[str, Any]] = None
    ) -> ExecutionGraph:
        """
        Optimize execution graph for maximum parallel efficiency.

        Args:
            execution_graph: Original execution graph
            optimization_goals: Optimization parameters

        Returns:
            ExecutionGraph: Optimized execution graph
        """
        try:
            self.logger.info("Optimizing execution graph for parallel execution")

            goals = optimization_goals or {
                "maximize_parallelism": True,
                "minimize_duration": True,
                "balance_layers": True
            }

            # Apply optimization strategies
            optimized_layers = execution_graph.execution_layers.copy()

            if goals.get("maximize_parallelism", True):
                optimized_layers = await self._maximize_parallelism(optimized_layers)

            if goals.get("minimize_duration", True):
                optimized_layers = await self._minimize_execution_duration(optimized_layers)

            if goals.get("balance_layers", True):
                optimized_layers = await self._balance_execution_layers(optimized_layers)

            # Recalculate metrics
            new_parallelization_factor = await self._calculate_parallelization_factor(
                optimized_layers, execution_graph.total_tasks
            )
            new_total_duration = await self._calculate_total_duration(optimized_layers)

            # Create optimized execution graph
            optimized_graph = ExecutionGraph(
                dependency_graph=execution_graph.dependency_graph,
                execution_layers=optimized_layers,
                parallelization_factor=new_parallelization_factor,
                total_estimated_duration_minutes=new_total_duration,
                total_tasks=execution_graph.total_tasks
            )

            improvement = (
                execution_graph.total_estimated_duration_minutes - new_total_duration
            ) / execution_graph.total_estimated_duration_minutes * 100

            self.logger.info(
                f"Optimization complete: {improvement:.1f}% duration improvement, "
                f"parallelization factor: {new_parallelization_factor:.2f}"
            )

            return optimized_graph

        except Exception as e:
            self.logger.error(f"Execution optimization failed: {e}")
            raise DependencyAnalysisError(f"Failed to optimize execution graph: {str(e)}")

    async def _extract_explicit_dependencies(
        self,
        tasks: List[CompleteTask]
    ) -> List[TaskDependency]:
        """Extract explicitly declared dependencies from tasks."""
        dependencies = []

        for task in tasks:
            for dep_id in task.depends_on:
                # Validate dependency exists
                if not any(t.task_id == dep_id for t in tasks):
                    self.logger.warning(f"Task {task.task_id} depends on unknown task {dep_id}")
                    continue

                dependency = TaskDependency(
                    from_task_id=task.task_id,
                    to_task_id=dep_id,
                    dependency_type=DependencyType.EXPLICIT,
                    description=f"Explicit dependency: {task.task_id} depends on {dep_id}",
                    is_blocking=True
                )
                dependencies.append(dependency)

        return dependencies

    async def _analyze_implicit_dependencies(
        self,
        tasks: List[CompleteTask]
    ) -> List[TaskDependency]:
        """Analyze implicit dependencies based on file locations and context."""
        dependencies = []

        # Analyze file-based dependencies
        file_dependencies = await self._analyze_file_dependencies(tasks)
        dependencies.extend(file_dependencies)

        # Analyze context-based dependencies
        context_dependencies = await self._analyze_context_dependencies(tasks)
        dependencies.extend(context_dependencies)

        # Analyze architectural dependencies
        arch_dependencies = await self._analyze_architectural_dependencies(tasks)
        dependencies.extend(arch_dependencies)

        return dependencies

    async def _analyze_file_dependencies(
        self,
        tasks: List[CompleteTask]
    ) -> List[TaskDependency]:
        """Analyze dependencies based on file creation and modification."""
        dependencies = []
        file_creators = {}  # file -> task_id that creates it
        file_consumers = defaultdict(list)  # file -> list of task_ids that use it

        # Build file creation and consumption maps
        for task in tasks:
            for file_path, description in task.complete_context.file_locations.items():
                if "creat" in description.lower() or "implement" in description.lower():
                    file_creators[file_path] = task.task_id
                else:
                    file_consumers[file_path].append(task.task_id)

        # Create dependencies: consumers depend on creators
        for file_path, creator_id in file_creators.items():
            for consumer_id in file_consumers.get(file_path, []):
                if creator_id != consumer_id:
                    dependency = TaskDependency(
                        from_task_id=consumer_id,
                        to_task_id=creator_id,
                        dependency_type=DependencyType.FILE,
                        description=f"File dependency: {consumer_id} needs {file_path} created by {creator_id}",
                        is_blocking=True
                    )
                    dependencies.append(dependency)

        return dependencies

    async def _analyze_context_dependencies(
        self,
        tasks: List[CompleteTask]
    ) -> List[TaskDependency]:
        """Analyze dependencies based on task context and requirements."""
        dependencies = []

        # Look for keyword-based dependencies
        dependency_keywords = {
            "model": ["api", "service", "test"],  # models should be created before apis
            "database": ["model", "api"],        # database before models and apis
            "test": [],                          # tests depend on implementation
            "config": ["model", "api", "service"]  # config before other components
        }

        tasks_by_type = defaultdict(list)

        # Categorize tasks by type
        for task in tasks:
            title_lower = task.title.lower()
            background_lower = task.complete_context.project_background.lower()

            for keyword in dependency_keywords:
                if keyword in title_lower or keyword in background_lower:
                    tasks_by_type[keyword].append(task.task_id)

        # Create dependencies based on patterns
        for dependent_type, prereq_types in dependency_keywords.items():
            dependent_tasks = tasks_by_type.get(dependent_type, [])

            for prereq_type in prereq_types:
                prereq_tasks = tasks_by_type.get(prereq_type, [])

                for dependent_id in dependent_tasks:
                    for prereq_id in prereq_tasks:
                        if dependent_id != prereq_id:
                            dependency = TaskDependency(
                                from_task_id=dependent_id,
                                to_task_id=prereq_id,
                                dependency_type=DependencyType.LOGICAL,
                                description=f"Logical dependency: {dependent_type} tasks depend on {prereq_type}",
                                is_blocking=False  # Logical dependencies are often non-blocking
                            )
                            dependencies.append(dependency)

        return dependencies

    async def _analyze_architectural_dependencies(
        self,
        tasks: List[CompleteTask]
    ) -> List[TaskDependency]:
        """Analyze dependencies based on architectural patterns."""
        dependencies = []

        # Look for common architectural patterns
        foundation_tasks = []
        implementation_tasks = []
        integration_tasks = []

        for task in tasks:
            title_lower = task.title.lower()

            if any(keyword in title_lower for keyword in ["setup", "config", "foundation", "basic"]):
                foundation_tasks.append(task.task_id)
            elif any(keyword in title_lower for keyword in ["implement", "create", "build"]):
                implementation_tasks.append(task.task_id)
            elif any(keyword in title_lower for keyword in ["integrat", "connect", "coordin"]):
                integration_tasks.append(task.task_id)

        # Implementation depends on foundation
        for impl_id in implementation_tasks:
            for found_id in foundation_tasks:
                dependency = TaskDependency(
                    from_task_id=impl_id,
                    to_task_id=found_id,
                    dependency_type=DependencyType.ARCHITECTURAL,
                    description="Architectural dependency: implementation depends on foundation",
                    is_blocking=True
                )
                dependencies.append(dependency)

        # Integration depends on implementation
        for integ_id in integration_tasks:
            for impl_id in implementation_tasks:
                dependency = TaskDependency(
                    from_task_id=integ_id,
                    to_task_id=impl_id,
                    dependency_type=DependencyType.ARCHITECTURAL,
                    description="Architectural dependency: integration depends on implementation",
                    is_blocking=True
                )
                dependencies.append(dependency)

        return dependencies

    async def _validate_dependency_graph(
        self,
        dependency_graph: DependencyGraph,
        valid_task_ids: List[str]
    ) -> None:
        """Validate dependency graph for correctness."""
        # Check for invalid task references
        for dependency in dependency_graph.dependencies:
            if dependency.from_task_id not in valid_task_ids:
                raise DependencyAnalysisError(
                    f"Invalid dependency: {dependency.from_task_id} not in task list"
                )
            if dependency.to_task_id not in valid_task_ids:
                raise DependencyAnalysisError(
                    f"Invalid dependency: {dependency.to_task_id} not in task list"
                )

        # Check for circular dependencies using DFS
        if not dependency_graph.validate_acyclic():
            raise CircularDependencyError("Circular dependencies detected in task graph")

    async def _generate_execution_layers(
        self,
        dependency_graph: DependencyGraph,
        task_lookup: Dict[str, CompleteTask]
    ) -> List[ExecutionLayer]:
        """Generate execution layers using topological sorting."""
        # Build adjacency list and in-degree count
        adj_list = defaultdict(list)
        in_degree = defaultdict(int)

        # Initialize all tasks with 0 in-degree
        for task_id in dependency_graph.tasks:
            in_degree[task_id] = 0

        # Build graph
        for dependency in dependency_graph.dependencies:
            if dependency.is_blocking:  # Only consider blocking dependencies for layering
                adj_list[dependency.to_task_id].append(dependency.from_task_id)
                in_degree[dependency.from_task_id] += 1

        # Kahn's algorithm for topological sorting with layers
        layers = []
        remaining_tasks = set(dependency_graph.tasks)

        layer_number = 0
        while remaining_tasks:
            # Find tasks with no dependencies (in-degree 0)
            current_layer_tasks = [
                task_id for task_id in remaining_tasks
                if in_degree[task_id] == 0
            ]

            if not current_layer_tasks:
                # This should not happen if graph is acyclic
                raise DependencyAnalysisError("Cannot create execution layers - possible circular dependency")

            # Create execution layer
            layer_tasks = [task_lookup[task_id] for task_id in current_layer_tasks]

            # Calculate estimated duration for parallel execution
            if layer_tasks:
                max_duration = max(task.estimated_duration_minutes for task in layer_tasks)
            else:
                max_duration = 0

            execution_layer = ExecutionLayer(
                layer_number=layer_number,
                tasks=layer_tasks,
                dependencies_satisfied=[],  # Will be populated later if needed
                estimated_duration_minutes=max_duration
            )

            layers.append(execution_layer)

            # Remove current layer tasks and update in-degrees
            for task_id in current_layer_tasks:
                remaining_tasks.remove(task_id)
                for dependent_id in adj_list[task_id]:
                    in_degree[dependent_id] -= 1

            layer_number += 1

        return layers

    async def _calculate_parallelization_factor(
        self,
        execution_layers: List[ExecutionLayer],
        total_tasks: int
    ) -> float:
        """Calculate parallelization factor for execution plan."""
        if not execution_layers or total_tasks == 0:
            return 0.0

        # Calculate average tasks per layer
        total_layer_tasks = sum(len(layer.tasks) for layer in execution_layers)
        avg_tasks_per_layer = total_layer_tasks / len(execution_layers)

        # Parallelization factor is ratio of average tasks per layer to 1 (sequential)
        parallelization_factor = avg_tasks_per_layer / 1.0

        return min(parallelization_factor, total_tasks)  # Cap at total tasks

    async def _calculate_total_duration(self, execution_layers: List[ExecutionLayer]) -> int:
        """Calculate total estimated execution duration."""
        return sum(layer.estimated_duration_minutes for layer in execution_layers)

    async def _maximize_parallelism(
        self,
        execution_layers: List[ExecutionLayer]
    ) -> List[ExecutionLayer]:
        """Optimize layers to maximize parallelism."""
        # For now, return as-is. More sophisticated optimization could:
        # - Split large layers if tasks have no hidden dependencies
        # - Merge small layers if dependencies allow
        # - Reorder tasks within layers for better resource utilization
        return execution_layers

    async def _minimize_execution_duration(
        self,
        execution_layers: List[ExecutionLayer]
    ) -> List[ExecutionLayer]:
        """Optimize layers to minimize total execution duration."""
        # Sort tasks within each layer by duration (longest first)
        # This can help with better resource utilization
        optimized_layers = []

        for layer in execution_layers:
            sorted_tasks = sorted(
                layer.tasks,
                key=lambda t: t.estimated_duration_minutes,
                reverse=True
            )

            optimized_layer = ExecutionLayer(
                layer_number=layer.layer_number,
                tasks=sorted_tasks,
                dependencies_satisfied=layer.dependencies_satisfied,
                estimated_duration_minutes=layer.estimated_duration_minutes
            )
            optimized_layers.append(optimized_layer)

        return optimized_layers

    async def _balance_execution_layers(
        self,
        execution_layers: List[ExecutionLayer]
    ) -> List[ExecutionLayer]:
        """Balance execution layers for optimal resource utilization."""
        # Simple balancing: ensure no layer has too many or too few tasks
        # More sophisticated balancing would consider resource requirements
        return execution_layers

    async def detect_potential_conflicts(
        self,
        tasks: List[CompleteTask]
    ) -> List[Dict[str, Any]]:
        """
        Detect potential conflicts between tasks.

        Args:
            tasks: List of tasks to analyze

        Returns:
            List[Dict[str, Any]]: List of potential conflicts
        """
        conflicts = []

        # Check for file conflicts (multiple tasks writing to same file)
        file_writers = defaultdict(list)

        for task in tasks:
            for file_path, description in task.complete_context.file_locations.items():
                if any(keyword in description.lower() for keyword in ["creat", "writ", "implement"]):
                    file_writers[file_path].append(task.task_id)

        for file_path, writers in file_writers.items():
            if len(writers) > 1:
                conflicts.append({
                    "type": "file_conflict",
                    "description": f"Multiple tasks writing to {file_path}",
                    "tasks": writers,
                    "severity": "high",
                    "resolution": "Add dependency or merge tasks"
                })

        # Check for resource conflicts
        # (Could be extended to check for database, network, or other resource conflicts)

        return conflicts
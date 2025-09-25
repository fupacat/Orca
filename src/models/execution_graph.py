"""
Execution graph models for parallel coordination and dependency management.

These models represent the dependency analysis results and execution scheduling
for optimal parallel task coordination.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Set, Optional, Any
from enum import Enum
from .complete_task import CompleteTask


class DependencyType(str, Enum):
    """Types of dependencies between tasks"""
    CODE = "code"          # Code dependencies (functions, classes, modules)
    FILE = "file"          # File dependencies (files created/modified)
    ENVIRONMENT = "env"    # Environment dependencies (tools, setup)
    DATA = "data"         # Data dependencies (configuration, state)


class TaskDependency(BaseModel):
    """Individual task dependency specification"""

    from_task_id: str = Field(..., description="Task that depends on another")
    to_task_id: str = Field(..., description="Task that is depended upon")
    dependency_type: DependencyType = Field(..., description="Type of dependency")
    description: Optional[str] = Field(None, description="Human-readable dependency description")
    is_blocking: bool = Field(default=True, description="Whether this dependency is blocking")

    @validator('from_task_id', 'to_task_id')
    def validate_task_ids(cls, v):
        """Ensure task IDs are valid"""
        if not v or not v.strip():
            raise ValueError("Task ID cannot be empty")
        return v.strip()

    def __str__(self) -> str:
        return f"{self.from_task_id} depends on {self.to_task_id} ({self.dependency_type.value})"


class DependencyGraph(BaseModel):
    """Directed acyclic graph representing task dependencies"""

    tasks: List[str] = Field(..., description="All task IDs in the graph")
    dependencies: List[TaskDependency] = Field(..., description="All dependencies between tasks")
    is_acyclic: Optional[bool] = Field(None, description="Whether graph is acyclic (computed)")

    def get_dependencies_for_task(self, task_id: str) -> List[TaskDependency]:
        """Get all dependencies for a specific task"""
        return [dep for dep in self.dependencies if dep.from_task_id == task_id]

    def get_dependents_for_task(self, task_id: str) -> List[TaskDependency]:
        """Get all tasks that depend on a specific task"""
        return [dep for dep in self.dependencies if dep.to_task_id == task_id]

    def get_independent_tasks(self) -> List[str]:
        """Get tasks with no dependencies (can execute immediately)"""
        dependent_tasks = {dep.from_task_id for dep in self.dependencies}
        return [task_id for task_id in self.tasks if task_id not in dependent_tasks]

    def get_leaf_tasks(self) -> List[str]:
        """Get tasks that no other tasks depend on"""
        dependency_targets = {dep.to_task_id for dep in self.dependencies}
        return [task_id for task_id in self.tasks if task_id not in dependency_targets]

    def validate_acyclic(self) -> bool:
        """
        Validate that the dependency graph is acyclic using topological sort.

        Returns:
            bool: True if graph is acyclic, False if cycles detected
        """
        # Build adjacency list
        graph = {task_id: [] for task_id in self.tasks}
        in_degree = {task_id: 0 for task_id in self.tasks}

        for dep in self.dependencies:
            if dep.is_blocking:
                graph[dep.to_task_id].append(dep.from_task_id)
                in_degree[dep.from_task_id] += 1

        # Topological sort using Kahn's algorithm
        queue = [task_id for task_id in self.tasks if in_degree[task_id] == 0]
        processed_count = 0

        while queue:
            current = queue.pop(0)
            processed_count += 1

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If we processed all tasks, the graph is acyclic
        self.is_acyclic = (processed_count == len(self.tasks))
        return self.is_acyclic

    def find_cycles(self) -> List[List[str]]:
        """
        Find all cycles in the dependency graph.

        Returns:
            List[List[str]]: List of cycles (each cycle is a list of task IDs)
        """
        if self.validate_acyclic():
            return []

        # Build adjacency list for cycle detection
        graph = {task_id: [] for task_id in self.tasks}
        for dep in self.dependencies:
            if dep.is_blocking:
                graph[dep.to_task_id].append(dep.from_task_id)

        # DFS-based cycle detection
        white = set(self.tasks)  # Unvisited
        gray = set()   # Currently being processed
        black = set()  # Completely processed
        cycles = []

        def dfs(node, path):
            if node in gray:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return

            if node in black:
                return

            white.remove(node)
            gray.add(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, path + [node])

            gray.remove(node)
            black.add(node)

        for task_id in list(white):
            if task_id in white:
                dfs(task_id, [])

        return cycles


class ExecutionLayer(BaseModel):
    """A layer of tasks that can execute in parallel"""

    layer_number: int = Field(..., description="Layer number in execution sequence", ge=0)
    tasks: List[CompleteTask] = Field(..., description="Tasks in this layer")
    dependencies_satisfied: List[str] = Field(
        default_factory=list,
        description="Task IDs whose completion allows this layer to execute"
    )
    estimated_duration_minutes: Optional[int] = Field(
        None,
        description="Estimated duration for this layer (max of all tasks)"
    )
    parallel_factor: float = Field(
        default=1.0,
        description="Parallelization factor (tasks in layer / 1)",
        gt=0
    )

    @validator('tasks')
    def validate_tasks_not_empty(cls, v):
        """Ensure layer has at least one task"""
        if not v:
            raise ValueError("Execution layer must contain at least one task")
        return v

    def calculate_estimated_duration(self) -> int:
        """
        Calculate estimated duration as maximum of all task durations.

        Returns:
            int: Estimated duration in minutes
        """
        if not self.tasks:
            return 0

        durations = [
            task.estimated_duration_minutes or 60  # Default 1 hour if not specified
            for task in self.tasks
        ]

        self.estimated_duration_minutes = max(durations)
        return self.estimated_duration_minutes

    def get_task_ids(self) -> List[str]:
        """Get list of task IDs in this layer"""
        return [task.task_id for task in self.tasks]

    def get_parallel_factor(self) -> float:
        """
        Calculate parallelization factor for this layer.

        Returns:
            float: Number of tasks that can execute in parallel
        """
        self.parallel_factor = float(len(self.tasks))
        return self.parallel_factor


class ExecutionGraph(BaseModel):
    """Complete execution graph with parallel layers and scheduling"""

    dependency_graph: DependencyGraph = Field(..., description="Task dependency graph")
    execution_layers: List[ExecutionLayer] = Field(..., description="Ordered execution layers")
    total_tasks: int = Field(..., description="Total number of tasks")
    parallel_tasks: int = Field(default=0, description="Number of tasks that can execute in parallel")
    sequential_tasks: int = Field(default=0, description="Number of tasks that must execute sequentially")
    parallelization_factor: float = Field(default=0.0, description="Percentage of tasks that can parallel execute")
    estimated_total_duration_minutes: Optional[int] = Field(
        None,
        description="Total estimated execution duration"
    )

    @validator('execution_layers')
    def validate_layers_sequential(cls, v):
        """Ensure layers are numbered sequentially starting from 0"""
        for i, layer in enumerate(v):
            if layer.layer_number != i:
                raise ValueError(f"Layer {i} has incorrect layer_number {layer.layer_number}")
        return v

    def calculate_parallelization_metrics(self):
        """Calculate parallelization statistics"""
        if not self.execution_layers:
            return

        # Count parallel vs sequential tasks
        self.parallel_tasks = sum(len(layer.tasks) for layer in self.execution_layers if len(layer.tasks) > 1)
        self.sequential_tasks = sum(len(layer.tasks) for layer in self.execution_layers if len(layer.tasks) == 1)

        if self.total_tasks > 0:
            self.parallelization_factor = self.parallel_tasks / self.total_tasks

        # Calculate total estimated duration (sum of layer durations)
        self.estimated_total_duration_minutes = sum(
            layer.calculate_estimated_duration() for layer in self.execution_layers
        )

    def get_execution_schedule(self) -> Dict[str, Any]:
        """
        Generate detailed execution schedule.

        Returns:
            Dict[str, Any]: Execution schedule with timing and dependencies
        """
        schedule = {
            "total_layers": len(self.execution_layers),
            "total_tasks": self.total_tasks,
            "parallelization_factor": self.parallelization_factor,
            "estimated_duration_minutes": self.estimated_total_duration_minutes,
            "layers": []
        }

        cumulative_time = 0
        for layer in self.execution_layers:
            layer_duration = layer.calculate_estimated_duration()
            layer_info = {
                "layer_number": layer.layer_number,
                "task_count": len(layer.tasks),
                "task_ids": layer.get_task_ids(),
                "parallel_factor": layer.get_parallel_factor(),
                "estimated_duration_minutes": layer_duration,
                "start_time_minutes": cumulative_time,
                "end_time_minutes": cumulative_time + layer_duration,
                "dependencies_satisfied": layer.dependencies_satisfied
            }
            schedule["layers"].append(layer_info)
            cumulative_time += layer_duration

        return schedule

    def validate_execution_graph(self) -> Dict[str, Any]:
        """
        Validate the complete execution graph for correctness.

        Returns:
            Dict[str, Any]: Validation results with issues and recommendations
        """
        validation = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "recommendations": []
        }

        # Validate dependency graph is acyclic
        if not self.dependency_graph.validate_acyclic():
            validation["is_valid"] = False
            validation["issues"].append("Dependency graph contains cycles")
            cycles = self.dependency_graph.find_cycles()
            for cycle in cycles:
                validation["issues"].append(f"Cycle detected: {' -> '.join(cycle)}")

        # Check parallelization efficiency
        if self.parallelization_factor < 0.5:
            validation["warnings"].append(
                f"Low parallelization factor ({self.parallelization_factor:.2%}), "
                "consider reducing dependencies"
            )
        elif self.parallelization_factor > 0.8:
            validation["recommendations"].append(
                f"Excellent parallelization ({self.parallelization_factor:.2%})"
            )

        # Validate layer structure
        task_ids_in_layers = set()
        for layer in self.execution_layers:
            for task in layer.tasks:
                if task.task_id in task_ids_in_layers:
                    validation["issues"].append(
                        f"Task {task.task_id} appears in multiple layers"
                    )
                task_ids_in_layers.add(task.task_id)

        # Check all tasks are included in layers
        all_task_ids = set(self.dependency_graph.tasks)
        if task_ids_in_layers != all_task_ids:
            missing_tasks = all_task_ids - task_ids_in_layers
            extra_tasks = task_ids_in_layers - all_task_ids
            if missing_tasks:
                validation["issues"].append(f"Tasks missing from execution layers: {missing_tasks}")
            if extra_tasks:
                validation["issues"].append(f"Extra tasks in execution layers: {extra_tasks}")

        return validation

    def optimize_execution_order(self) -> 'ExecutionGraph':
        """
        Optimize execution order for maximum parallelization.

        Returns:
            ExecutionGraph: Optimized execution graph
        """
        # This is a placeholder for optimization logic
        # In a full implementation, this would use algorithms like:
        # - Critical path method (CPM)
        # - Resource-constrained project scheduling
        # - Genetic algorithms for optimization

        # For now, return self (no optimization)
        return self

    class Config:
        """Pydantic configuration"""
        schema_extra = {
            "example": {
                "dependency_graph": {
                    "tasks": ["task1", "task2", "task3", "task4"],
                    "dependencies": [
                        {
                            "from_task_id": "task2",
                            "to_task_id": "task1",
                            "dependency_type": "code",
                            "description": "Task 2 requires code from Task 1"
                        }
                    ]
                },
                "execution_layers": [
                    {
                        "layer_number": 0,
                        "tasks": ["task1", "task3"],
                        "dependencies_satisfied": []
                    },
                    {
                        "layer_number": 1,
                        "tasks": ["task2", "task4"],
                        "dependencies_satisfied": ["task1"]
                    }
                ],
                "total_tasks": 4,
                "parallelization_factor": 0.5
            }
        }
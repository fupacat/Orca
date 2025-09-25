"""
Execution Planner for coordinating parallel task execution strategies.

Plans and coordinates the execution of tasks based on dependency analysis,
resource availability, and optimization goals.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from ..models.complete_task import CompleteTask
from ..models.execution_graph import ExecutionGraph, ExecutionLayer


class ExecutionStrategy(str, Enum):
    """Execution strategies for task coordination"""
    PARALLEL_AGGRESSIVE = "parallel_aggressive"    # Maximum parallelism
    PARALLEL_CONSERVATIVE = "parallel_conservative"  # Safe parallelism
    SEQUENTIAL = "sequential"                      # No parallelism
    HYBRID = "hybrid"                             # Mix of parallel and sequential


class ResourceType(str, Enum):
    """Types of resources for allocation"""
    CPU = "cpu"
    MEMORY = "memory"
    IO = "io"
    NETWORK = "network"
    AGENT = "agent"


class ExecutionPlanningError(Exception):
    """Exception raised during execution planning"""
    pass


class ExecutionPlanner:
    """
    Intelligent execution planner for parallel task coordination.

    Plans task execution based on dependency analysis, resource constraints,
    and optimization goals to maximize parallel efficiency.
    """

    def __init__(
        self,
        max_parallel_agents: int = 5,
        resource_constraints: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize execution planner.

        Args:
            max_parallel_agents: Maximum number of parallel execution agents
            resource_constraints: Resource availability constraints
        """
        self.max_parallel_agents = max_parallel_agents
        self.resource_constraints = resource_constraints or {}
        self.logger = logging.getLogger("analysis.execution_planner")

    async def create_execution_plan(
        self,
        execution_graph: ExecutionGraph,
        strategy: ExecutionStrategy = ExecutionStrategy.PARALLEL_AGGRESSIVE,
        optimization_goals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create detailed execution plan from execution graph.

        Args:
            execution_graph: Analyzed execution graph
            strategy: Execution strategy to use
            optimization_goals: Optimization parameters

        Returns:
            Dict[str, Any]: Detailed execution plan

        Raises:
            ExecutionPlanningError: If planning fails
        """
        try:
            self.logger.info(f"Creating execution plan with {strategy.value} strategy")

            goals = optimization_goals or {
                "minimize_duration": True,
                "maximize_resource_utilization": True,
                "ensure_reliability": True
            }

            # Calculate execution timeline
            timeline = await self._calculate_execution_timeline(execution_graph, strategy)

            # Allocate resources
            resource_allocation = await self._allocate_resources(execution_graph, strategy)

            # Generate execution schedule
            schedule = await self._generate_execution_schedule(
                execution_graph, timeline, resource_allocation, strategy
            )

            # Calculate performance metrics
            metrics = await self._calculate_execution_metrics(
                execution_graph, timeline, resource_allocation
            )

            # Create execution plan
            execution_plan = {
                "plan_id": f"exec_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "created_at": datetime.now().isoformat(),
                "strategy": strategy.value,
                "execution_graph": execution_graph,
                "timeline": timeline,
                "resource_allocation": resource_allocation,
                "schedule": schedule,
                "metrics": metrics,
                "optimization_goals": goals
            }

            self.logger.info(
                f"Created execution plan: {len(schedule['phases'])} phases, "
                f"{metrics['estimated_duration_minutes']} minutes, "
                f"{metrics['parallelization_efficiency']:.2f} efficiency"
            )

            return execution_plan

        except Exception as e:
            self.logger.error(f"Execution planning failed: {e}")
            raise ExecutionPlanningError(f"Failed to create execution plan: {str(e)}")

    async def optimize_execution_plan(
        self,
        execution_plan: Dict[str, Any],
        optimization_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize execution plan based on specified criteria.

        Args:
            execution_plan: Original execution plan
            optimization_criteria: Optimization criteria

        Returns:
            Dict[str, Any]: Optimized execution plan
        """
        try:
            self.logger.info("Optimizing execution plan")

            criteria = optimization_criteria or {
                "reduce_duration": 0.8,      # Weight for duration reduction
                "improve_reliability": 0.6,  # Weight for reliability
                "balance_resources": 0.7     # Weight for resource balancing
            }

            # Apply optimization strategies
            optimized_timeline = await self._optimize_timeline(
                execution_plan["timeline"], criteria
            )

            optimized_allocation = await self._optimize_resource_allocation(
                execution_plan["resource_allocation"], criteria
            )

            # Regenerate schedule with optimizations
            optimized_schedule = await self._generate_execution_schedule(
                execution_plan["execution_graph"],
                optimized_timeline,
                optimized_allocation,
                ExecutionStrategy(execution_plan["strategy"])
            )

            # Recalculate metrics
            optimized_metrics = await self._calculate_execution_metrics(
                execution_plan["execution_graph"],
                optimized_timeline,
                optimized_allocation
            )

            # Create optimized plan
            optimized_plan = execution_plan.copy()
            optimized_plan.update({
                "timeline": optimized_timeline,
                "resource_allocation": optimized_allocation,
                "schedule": optimized_schedule,
                "metrics": optimized_metrics,
                "optimized_at": datetime.now().isoformat(),
                "optimization_criteria": criteria
            })

            improvement = (
                execution_plan["metrics"]["estimated_duration_minutes"] -
                optimized_metrics["estimated_duration_minutes"]
            ) / execution_plan["metrics"]["estimated_duration_minutes"] * 100

            self.logger.info(f"Execution plan optimized: {improvement:.1f}% improvement")

            return optimized_plan

        except Exception as e:
            self.logger.error(f"Execution plan optimization failed: {e}")
            raise ExecutionPlanningError(f"Failed to optimize execution plan: {str(e)}")

    async def _calculate_execution_timeline(
        self,
        execution_graph: ExecutionGraph,
        strategy: ExecutionStrategy
    ) -> Dict[str, Any]:
        """Calculate execution timeline based on strategy."""
        timeline = {
            "start_time": datetime.now(),
            "phases": [],
            "total_duration_minutes": 0,
            "parallel_phases": 0,
            "sequential_phases": 0
        }

        current_time = timeline["start_time"]

        for layer in execution_graph.execution_layers:
            phase_duration = layer.estimated_duration_minutes

            # Adjust duration based on strategy
            if strategy == ExecutionStrategy.PARALLEL_AGGRESSIVE:
                # Use maximum parallelism (layer duration = max task duration)
                actual_duration = phase_duration
            elif strategy == ExecutionStrategy.PARALLEL_CONSERVATIVE:
                # Add buffer for conservative approach
                actual_duration = int(phase_duration * 1.2)
            elif strategy == ExecutionStrategy.SEQUENTIAL:
                # Sequential execution (sum of all task durations)
                actual_duration = sum(task.estimated_duration_minutes for task in layer.tasks)
            else:  # HYBRID
                # Mix based on layer size
                if len(layer.tasks) <= 2:
                    actual_duration = sum(task.estimated_duration_minutes for task in layer.tasks)
                else:
                    actual_duration = phase_duration

            phase = {
                "phase_number": layer.layer_number,
                "start_time": current_time,
                "end_time": current_time + timedelta(minutes=actual_duration),
                "duration_minutes": actual_duration,
                "tasks": [task.task_id for task in layer.tasks],
                "task_count": len(layer.tasks),
                "is_parallel": len(layer.tasks) > 1 and strategy != ExecutionStrategy.SEQUENTIAL
            }

            timeline["phases"].append(phase)
            timeline["total_duration_minutes"] += actual_duration

            if phase["is_parallel"]:
                timeline["parallel_phases"] += 1
            else:
                timeline["sequential_phases"] += 1

            current_time = phase["end_time"]

        timeline["end_time"] = current_time

        return timeline

    async def _allocate_resources(
        self,
        execution_graph: ExecutionGraph,
        strategy: ExecutionStrategy
    ) -> Dict[str, Any]:
        """Allocate resources for task execution."""
        allocation = {
            "agents": {},
            "resource_pools": {
                ResourceType.CPU: {"total": 100, "allocated": 0},
                ResourceType.MEMORY: {"total": 100, "allocated": 0},
                ResourceType.IO: {"total": 100, "allocated": 0},
                ResourceType.AGENT: {"total": self.max_parallel_agents, "allocated": 0}
            },
            "conflicts": [],
            "bottlenecks": []
        }

        for layer in execution_graph.execution_layers:
            layer_agents = min(len(layer.tasks), self.max_parallel_agents)

            # Allocate agents for this layer
            for i, task in enumerate(layer.tasks):
                if strategy == ExecutionStrategy.SEQUENTIAL:
                    agent_id = "agent_0"  # Single agent for sequential
                else:
                    agent_id = f"agent_{i % layer_agents}"

                if agent_id not in allocation["agents"]:
                    allocation["agents"][agent_id] = []

                allocation["agents"][agent_id].append({
                    "task_id": task.task_id,
                    "layer": layer.layer_number,
                    "estimated_duration": task.estimated_duration_minutes,
                    "resources_required": await self._estimate_task_resources(task)
                })

        # Calculate resource utilization
        await self._calculate_resource_utilization(allocation)

        return allocation

    async def _estimate_task_resources(self, task: CompleteTask) -> Dict[str, float]:
        """Estimate resource requirements for a task."""
        # Simple estimation based on task characteristics
        base_cpu = 20.0
        base_memory = 15.0
        base_io = 10.0

        # Adjust based on task type
        title_lower = task.title.lower()

        if "test" in title_lower:
            base_cpu *= 0.8  # Tests typically lighter on CPU
        elif "model" in title_lower or "data" in title_lower:
            base_memory *= 1.5  # Data models need more memory
        elif "api" in title_lower or "service" in title_lower:
            base_cpu *= 1.2  # Services need more CPU
            base_io *= 1.3   # More I/O operations

        # Adjust based on estimated duration (longer tasks may need more resources)
        duration_factor = min(task.estimated_duration_minutes / 120.0, 2.0)  # Cap at 2x

        return {
            ResourceType.CPU: base_cpu * duration_factor,
            ResourceType.MEMORY: base_memory * duration_factor,
            ResourceType.IO: base_io * duration_factor
        }

    async def _calculate_resource_utilization(self, allocation: Dict[str, Any]) -> None:
        """Calculate resource utilization from allocation."""
        # Calculate peak resource usage
        for agent_id, agent_tasks in allocation["agents"].items():
            total_cpu = sum(task["resources_required"][ResourceType.CPU] for task in agent_tasks)
            total_memory = sum(task["resources_required"][ResourceType.MEMORY] for task in agent_tasks)
            total_io = sum(task["resources_required"][ResourceType.IO] for task in agent_tasks)

            # Update resource pool allocations (simplified)
            allocation["resource_pools"][ResourceType.CPU]["allocated"] += total_cpu / len(allocation["agents"])
            allocation["resource_pools"][ResourceType.MEMORY]["allocated"] += total_memory / len(allocation["agents"])
            allocation["resource_pools"][ResourceType.IO]["allocated"] += total_io / len(allocation["agents"])

        # Identify bottlenecks
        for resource_type, pool in allocation["resource_pools"].items():
            utilization = pool["allocated"] / pool["total"]
            if utilization > 0.9:  # 90% utilization threshold
                allocation["bottlenecks"].append({
                    "resource": resource_type.value,
                    "utilization": utilization,
                    "recommendation": f"Consider increasing {resource_type.value} capacity"
                })

    async def _generate_execution_schedule(
        self,
        execution_graph: ExecutionGraph,
        timeline: Dict[str, Any],
        resource_allocation: Dict[str, Any],
        strategy: ExecutionStrategy
    ) -> Dict[str, Any]:
        """Generate detailed execution schedule."""
        schedule = {
            "phases": [],
            "agent_schedules": defaultdict(list),
            "milestones": [],
            "checkpoints": []
        }

        # Create phase schedules
        for phase in timeline["phases"]:
            phase_schedule = {
                "phase_number": phase["phase_number"],
                "start_time": phase["start_time"],
                "end_time": phase["end_time"],
                "duration_minutes": phase["duration_minutes"],
                "task_assignments": [],
                "coordination_points": [],
                "quality_gates": []
            }

            # Assign tasks to agents
            layer = execution_graph.execution_layers[phase["phase_number"]]
            for i, task in enumerate(layer.tasks):
                if strategy == ExecutionStrategy.SEQUENTIAL:
                    agent_id = "agent_0"
                else:
                    agent_id = f"agent_{i % self.max_parallel_agents}"

                assignment = {
                    "task_id": task.task_id,
                    "agent_id": agent_id,
                    "start_time": phase["start_time"],
                    "estimated_end_time": phase["start_time"] + timedelta(
                        minutes=task.estimated_duration_minutes
                    ),
                    "dependencies_checked": True,
                    "resources_allocated": resource_allocation["agents"][agent_id]
                }

                phase_schedule["task_assignments"].append(assignment)
                schedule["agent_schedules"][agent_id].append(assignment)

            # Add coordination points for parallel phases
            if phase["is_parallel"] and len(layer.tasks) > 1:
                phase_schedule["coordination_points"].append({
                    "type": "parallel_start",
                    "time": phase["start_time"],
                    "description": f"Start parallel execution of {len(layer.tasks)} tasks"
                })
                phase_schedule["coordination_points"].append({
                    "type": "parallel_sync",
                    "time": phase["end_time"],
                    "description": "Wait for all parallel tasks to complete"
                })

            # Add quality gates
            phase_schedule["quality_gates"].append({
                "type": "phase_completion",
                "time": phase["end_time"],
                "checks": ["All tasks completed", "Quality validation passed", "Dependencies satisfied"]
            })

            schedule["phases"].append(phase_schedule)

        # Add milestones
        schedule["milestones"] = [
            {
                "name": "Execution Start",
                "time": timeline["start_time"],
                "description": "Begin parallel task execution"
            },
            {
                "name": "Midpoint Check",
                "time": timeline["start_time"] + timedelta(
                    minutes=timeline["total_duration_minutes"] / 2
                ),
                "description": "Midpoint progress evaluation"
            },
            {
                "name": "Execution Complete",
                "time": timeline["end_time"],
                "description": "All tasks completed successfully"
            }
        ]

        return schedule

    async def _calculate_execution_metrics(
        self,
        execution_graph: ExecutionGraph,
        timeline: Dict[str, Any],
        resource_allocation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate execution performance metrics."""
        # Sequential baseline (all tasks executed one after another)
        sequential_duration = sum(
            sum(task.estimated_duration_minutes for task in layer.tasks)
            for layer in execution_graph.execution_layers
        )

        parallel_duration = timeline["total_duration_minutes"]
        speedup = sequential_duration / parallel_duration if parallel_duration > 0 else 1.0

        # Calculate resource efficiency
        total_agents = len(resource_allocation["agents"])
        agent_utilization = {}

        for agent_id, tasks in resource_allocation["agents"].items():
            agent_duration = sum(task["estimated_duration"] for task in tasks)
            agent_utilization[agent_id] = agent_duration / parallel_duration if parallel_duration > 0 else 0

        avg_utilization = sum(agent_utilization.values()) / len(agent_utilization) if agent_utilization else 0

        return {
            "estimated_duration_minutes": parallel_duration,
            "sequential_baseline_minutes": sequential_duration,
            "speedup_factor": speedup,
            "parallelization_efficiency": execution_graph.parallelization_factor,
            "resource_utilization": {
                "agents": agent_utilization,
                "average_utilization": avg_utilization,
                "resource_pools": resource_allocation["resource_pools"]
            },
            "quality_metrics": {
                "parallel_phases": timeline["parallel_phases"],
                "sequential_phases": timeline["sequential_phases"],
                "total_phases": len(timeline["phases"]),
                "bottlenecks_identified": len(resource_allocation["bottlenecks"])
            }
        }

    async def _optimize_timeline(
        self,
        timeline: Dict[str, Any],
        criteria: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize execution timeline based on criteria."""
        # For now, return original timeline
        # More sophisticated optimization could adjust phase scheduling
        return timeline

    async def _optimize_resource_allocation(
        self,
        allocation: Dict[str, Any],
        criteria: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize resource allocation based on criteria."""
        # For now, return original allocation
        # More sophisticated optimization could redistribute resources
        return allocation
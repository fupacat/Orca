"""
Parallel Optimizer for maximizing execution efficiency and resource utilization.

Optimizes parallel execution strategies to achieve maximum performance improvements
while maintaining reliability and quality standards.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..models.execution_graph import ExecutionGraph, ExecutionLayer
from ..models.complete_task import CompleteTask


class OptimizationStrategy(str, Enum):
    """Optimization strategies for parallel execution"""
    DURATION_FIRST = "duration_first"        # Minimize total duration
    THROUGHPUT_FIRST = "throughput_first"    # Maximize task throughput
    RESOURCE_FIRST = "resource_first"        # Optimize resource utilization
    BALANCED = "balanced"                    # Balance all factors


@dataclass
class OptimizationResult:
    """Results of parallel optimization"""
    optimized_graph: ExecutionGraph
    improvements: Dict[str, float]
    recommendations: List[str]
    warnings: List[str]
    optimization_metadata: Dict[str, Any]


class ParallelOptimizerError(Exception):
    """Exception raised during parallel optimization"""
    pass


class ParallelOptimizer:
    """
    Advanced parallel execution optimizer.

    Analyzes execution graphs and applies sophisticated optimization strategies
    to maximize parallel efficiency while maintaining quality and reliability.
    """

    def __init__(
        self,
        optimization_constraints: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize parallel optimizer.

        Args:
            optimization_constraints: Constraints for optimization
        """
        self.constraints = optimization_constraints or {
            "max_parallel_tasks": 10,
            "min_task_duration": 5,  # minutes
            "max_layer_imbalance": 0.3,  # 30%
            "quality_gate_enforcement": True
        }
        self.logger = logging.getLogger("analysis.parallel_optimizer")

    async def optimize_execution_graph(
        self,
        execution_graph: ExecutionGraph,
        strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        target_improvements: Optional[Dict[str, float]] = None
    ) -> OptimizationResult:
        """
        Optimize execution graph for maximum parallel efficiency.

        Args:
            execution_graph: Original execution graph
            strategy: Optimization strategy to apply
            target_improvements: Target improvement percentages

        Returns:
            OptimizationResult: Optimization results and improvements

        Raises:
            ParallelOptimizerError: If optimization fails
        """
        try:
            self.logger.info(f"Optimizing execution graph with {strategy.value} strategy")

            targets = target_improvements or {
                "duration_reduction": 20.0,      # 20% reduction in duration
                "parallelization_increase": 15.0, # 15% increase in parallelization
                "resource_efficiency": 10.0      # 10% improvement in resource usage
            }

            # Analyze current performance
            baseline_metrics = await self._analyze_baseline_performance(execution_graph)

            # Apply optimization strategies
            optimized_graph = execution_graph
            applied_optimizations = []

            if strategy in [OptimizationStrategy.DURATION_FIRST, OptimizationStrategy.BALANCED]:
                optimized_graph, duration_opts = await self._optimize_for_duration(optimized_graph)
                applied_optimizations.extend(duration_opts)

            if strategy in [OptimizationStrategy.THROUGHPUT_FIRST, OptimizationStrategy.BALANCED]:
                optimized_graph, throughput_opts = await self._optimize_for_throughput(optimized_graph)
                applied_optimizations.extend(throughput_opts)

            if strategy in [OptimizationStrategy.RESOURCE_FIRST, OptimizationStrategy.BALANCED]:
                optimized_graph, resource_opts = await self._optimize_for_resources(optimized_graph)
                applied_optimizations.extend(resource_opts)

            # Apply advanced optimizations
            optimized_graph = await self._apply_advanced_optimizations(optimized_graph, strategy)

            # Calculate improvements
            optimized_metrics = await self._analyze_baseline_performance(optimized_graph)
            improvements = await self._calculate_improvements(baseline_metrics, optimized_metrics)

            # Generate recommendations and warnings
            recommendations = await self._generate_recommendations(
                execution_graph, optimized_graph, improvements, targets
            )
            warnings = await self._identify_optimization_warnings(optimized_graph, improvements)

            # Create optimization result
            result = OptimizationResult(
                optimized_graph=optimized_graph,
                improvements=improvements,
                recommendations=recommendations,
                warnings=warnings,
                optimization_metadata={
                    "strategy": strategy.value,
                    "applied_optimizations": applied_optimizations,
                    "baseline_metrics": baseline_metrics,
                    "optimized_metrics": optimized_metrics,
                    "targets_met": await self._check_targets_met(improvements, targets),
                    "optimization_timestamp": asyncio.get_event_loop().time()
                }
            )

            self.logger.info(
                f"Optimization complete: {improvements.get('duration_reduction', 0):.1f}% duration improvement, "
                f"{improvements.get('parallelization_increase', 0):.1f}% parallelization improvement"
            )

            return result

        except Exception as e:
            self.logger.error(f"Parallel optimization failed: {e}")
            raise ParallelOptimizerError(f"Failed to optimize execution graph: {str(e)}")

    async def analyze_parallelization_opportunities(
        self,
        tasks: List[CompleteTask]
    ) -> Dict[str, Any]:
        """
        Analyze tasks for parallelization opportunities.

        Args:
            tasks: List of tasks to analyze

        Returns:
            Dict[str, Any]: Parallelization analysis results
        """
        try:
            self.logger.info(f"Analyzing parallelization opportunities for {len(tasks)} tasks")

            analysis = {
                "total_tasks": len(tasks),
                "parallelizable_tasks": 0,
                "sequential_tasks": 0,
                "bottleneck_tasks": [],
                "optimization_opportunities": [],
                "resource_conflicts": [],
                "dependency_chains": []
            }

            # Analyze individual tasks
            for task in tasks:
                task_analysis = await self._analyze_task_parallelizability(task)

                if task_analysis["parallelizable"]:
                    analysis["parallelizable_tasks"] += 1
                else:
                    analysis["sequential_tasks"] += 1

                if task_analysis["is_bottleneck"]:
                    analysis["bottleneck_tasks"].append({
                        "task_id": task.task_id,
                        "bottleneck_type": task_analysis["bottleneck_type"],
                        "impact": task_analysis["bottleneck_impact"]
                    })

            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(tasks)
            analysis["optimization_opportunities"] = opportunities

            # Analyze resource conflicts
            conflicts = await self._analyze_resource_conflicts(tasks)
            analysis["resource_conflicts"] = conflicts

            # Identify dependency chains
            chains = await self._identify_dependency_chains(tasks)
            analysis["dependency_chains"] = chains

            # Calculate parallelization potential
            max_theoretical_parallelization = len(tasks)  # All tasks in parallel
            current_parallelization = analysis["parallelizable_tasks"]

            analysis["parallelization_potential"] = {
                "current_parallelizable": current_parallelization,
                "maximum_theoretical": max_theoretical_parallelization,
                "improvement_potential": max_theoretical_parallelization - current_parallelization,
                "efficiency_score": current_parallelization / max_theoretical_parallelization if tasks else 0
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Parallelization analysis failed: {e}")
            raise ParallelOptimizerError(f"Failed to analyze parallelization opportunities: {str(e)}")

    async def _analyze_baseline_performance(self, execution_graph: ExecutionGraph) -> Dict[str, Any]:
        """Analyze baseline performance metrics of execution graph."""
        metrics = {
            "total_duration_minutes": execution_graph.total_estimated_duration_minutes,
            "parallelization_factor": execution_graph.parallelization_factor,
            "layer_count": len(execution_graph.execution_layers),
            "total_tasks": execution_graph.total_tasks,
            "average_tasks_per_layer": execution_graph.total_tasks / len(execution_graph.execution_layers) if execution_graph.execution_layers else 0,
            "layer_balance": await self._calculate_layer_balance(execution_graph.execution_layers),
            "critical_path_length": await self._calculate_critical_path(execution_graph),
            "dependency_complexity": len(execution_graph.dependency_graph.dependencies)
        }

        return metrics

    async def _optimize_for_duration(
        self,
        execution_graph: ExecutionGraph
    ) -> Tuple[ExecutionGraph, List[str]]:
        """Optimize execution graph to minimize total duration."""
        optimizations_applied = []
        optimized_layers = []

        for layer in execution_graph.execution_layers:
            # Sort tasks by duration (longest first) for better resource utilization
            sorted_tasks = sorted(
                layer.tasks,
                key=lambda t: t.estimated_duration_minutes,
                reverse=True
            )

            # Try to split large layers if beneficial
            if len(layer.tasks) > self.constraints["max_parallel_tasks"]:
                split_layers = await self._split_large_layer(layer)
                optimized_layers.extend(split_layers)
                optimizations_applied.append(f"Split layer {layer.layer_number} into {len(split_layers)} sub-layers")
            else:
                optimized_layer = ExecutionLayer(
                    layer_number=layer.layer_number,
                    tasks=sorted_tasks,
                    dependencies_satisfied=layer.dependencies_satisfied,
                    estimated_duration_minutes=max(task.estimated_duration_minutes for task in sorted_tasks) if sorted_tasks else 0
                )
                optimized_layers.append(optimized_layer)
                optimizations_applied.append(f"Optimized task ordering in layer {layer.layer_number}")

        # Renumber layers
        for i, layer in enumerate(optimized_layers):
            layer.layer_number = i

        # Create optimized execution graph
        optimized_graph = ExecutionGraph(
            dependency_graph=execution_graph.dependency_graph,
            execution_layers=optimized_layers,
            parallelization_factor=await self._calculate_parallelization_factor(optimized_layers, execution_graph.total_tasks),
            total_estimated_duration_minutes=sum(layer.estimated_duration_minutes for layer in optimized_layers),
            total_tasks=execution_graph.total_tasks
        )

        return optimized_graph, optimizations_applied

    async def _optimize_for_throughput(
        self,
        execution_graph: ExecutionGraph
    ) -> Tuple[ExecutionGraph, List[str]]:
        """Optimize execution graph to maximize task throughput."""
        optimizations_applied = []
        optimized_layers = execution_graph.execution_layers.copy()

        # Try to merge small layers to increase throughput
        merged_layers = []
        i = 0
        while i < len(optimized_layers):
            current_layer = optimized_layers[i]

            # Check if current layer is small and can be merged with next
            if (i + 1 < len(optimized_layers) and
                len(current_layer.tasks) < 3 and
                len(optimized_layers[i + 1].tasks) < 3):

                next_layer = optimized_layers[i + 1]

                # Check if merging is safe (no dependency conflicts)
                if await self._can_merge_layers(current_layer, next_layer, execution_graph.dependency_graph):
                    merged_tasks = current_layer.tasks + next_layer.tasks
                    merged_duration = max(
                        max(task.estimated_duration_minutes for task in current_layer.tasks),
                        max(task.estimated_duration_minutes for task in next_layer.tasks)
                    )

                    merged_layer = ExecutionLayer(
                        layer_number=current_layer.layer_number,
                        tasks=merged_tasks,
                        dependencies_satisfied=current_layer.dependencies_satisfied + next_layer.dependencies_satisfied,
                        estimated_duration_minutes=merged_duration
                    )

                    merged_layers.append(merged_layer)
                    optimizations_applied.append(f"Merged layers {current_layer.layer_number} and {next_layer.layer_number}")
                    i += 2  # Skip next layer since it's merged
                else:
                    merged_layers.append(current_layer)
                    i += 1
            else:
                merged_layers.append(current_layer)
                i += 1

        # Renumber layers
        for i, layer in enumerate(merged_layers):
            layer.layer_number = i

        # Create optimized execution graph
        optimized_graph = ExecutionGraph(
            dependency_graph=execution_graph.dependency_graph,
            execution_layers=merged_layers,
            parallelization_factor=await self._calculate_parallelization_factor(merged_layers, execution_graph.total_tasks),
            total_estimated_duration_minutes=sum(layer.estimated_duration_minutes for layer in merged_layers),
            total_tasks=execution_graph.total_tasks
        )

        return optimized_graph, optimizations_applied

    async def _optimize_for_resources(
        self,
        execution_graph: ExecutionGraph
    ) -> Tuple[ExecutionGraph, List[str]]:
        """Optimize execution graph for better resource utilization."""
        optimizations_applied = []
        optimized_layers = []

        for layer in execution_graph.execution_layers:
            # Balance tasks within layer by resource requirements
            balanced_tasks = await self._balance_tasks_by_resources(layer.tasks)

            optimized_layer = ExecutionLayer(
                layer_number=layer.layer_number,
                tasks=balanced_tasks,
                dependencies_satisfied=layer.dependencies_satisfied,
                estimated_duration_minutes=layer.estimated_duration_minutes
            )
            optimized_layers.append(optimized_layer)
            optimizations_applied.append(f"Balanced resources in layer {layer.layer_number}")

        # Create optimized execution graph
        optimized_graph = ExecutionGraph(
            dependency_graph=execution_graph.dependency_graph,
            execution_layers=optimized_layers,
            parallelization_factor=execution_graph.parallelization_factor,
            total_estimated_duration_minutes=execution_graph.total_estimated_duration_minutes,
            total_tasks=execution_graph.total_tasks
        )

        return optimized_graph, optimizations_applied

    async def _apply_advanced_optimizations(
        self,
        execution_graph: ExecutionGraph,
        strategy: OptimizationStrategy
    ) -> ExecutionGraph:
        """Apply advanced optimization techniques."""
        # Placeholder for advanced optimizations like:
        # - Critical path optimization
        # - Resource-aware scheduling
        # - Predictive load balancing
        # - Dynamic adaptation based on runtime feedback

        return execution_graph

    async def _calculate_improvements(
        self,
        baseline: Dict[str, Any],
        optimized: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate improvements from optimization."""
        improvements = {}

        # Duration improvement
        if baseline["total_duration_minutes"] > 0:
            duration_improvement = (
                baseline["total_duration_minutes"] - optimized["total_duration_minutes"]
            ) / baseline["total_duration_minutes"] * 100
            improvements["duration_reduction"] = max(0, duration_improvement)

        # Parallelization improvement
        if baseline["parallelization_factor"] > 0:
            parallelization_improvement = (
                optimized["parallelization_factor"] - baseline["parallelization_factor"]
            ) / baseline["parallelization_factor"] * 100
            improvements["parallelization_increase"] = max(0, parallelization_improvement)

        # Layer balance improvement
        layer_balance_improvement = optimized["layer_balance"] - baseline["layer_balance"]
        improvements["layer_balance_improvement"] = layer_balance_improvement

        # Efficiency improvement
        baseline_efficiency = baseline["average_tasks_per_layer"]
        optimized_efficiency = optimized["average_tasks_per_layer"]
        if baseline_efficiency > 0:
            efficiency_improvement = (optimized_efficiency - baseline_efficiency) / baseline_efficiency * 100
            improvements["efficiency_improvement"] = efficiency_improvement

        return improvements

    async def _generate_recommendations(
        self,
        original_graph: ExecutionGraph,
        optimized_graph: ExecutionGraph,
        improvements: Dict[str, float],
        targets: Dict[str, float]
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Check if targets were met
        for target_name, target_value in targets.items():
            actual_improvement = improvements.get(target_name, 0)
            if actual_improvement < target_value:
                recommendations.append(
                    f"Consider additional optimization for {target_name}: "
                    f"achieved {actual_improvement:.1f}% vs target {target_value:.1f}%"
                )

        # Suggest further optimizations
        if optimized_graph.parallelization_factor < 2.0:
            recommendations.append("Parallelization factor is low - consider breaking down tasks or reducing dependencies")

        if len(optimized_graph.execution_layers) > 8:
            recommendations.append("Many execution layers detected - consider consolidating tasks where possible")

        # Resource-based recommendations
        avg_tasks_per_layer = optimized_graph.total_tasks / len(optimized_graph.execution_layers)
        if avg_tasks_per_layer < 2:
            recommendations.append("Low average tasks per layer - consider merging compatible tasks")

        return recommendations

    async def _identify_optimization_warnings(
        self,
        optimized_graph: ExecutionGraph,
        improvements: Dict[str, float]
    ) -> List[str]:
        """Identify potential warnings from optimization."""
        warnings = []

        # Check for over-optimization
        if improvements.get("duration_reduction", 0) > 50:
            warnings.append("Significant duration reduction - verify dependency integrity")

        # Check for layer imbalance
        layer_balance = await self._calculate_layer_balance(optimized_graph.execution_layers)
        if layer_balance < 0.5:
            warnings.append("Low layer balance detected - may impact resource utilization")

        # Check for resource conflicts
        max_parallel_tasks = max(len(layer.tasks) for layer in optimized_graph.execution_layers)
        if max_parallel_tasks > self.constraints["max_parallel_tasks"]:
            warnings.append(f"Layer exceeds max parallel tasks ({max_parallel_tasks} > {self.constraints['max_parallel_tasks']})")

        return warnings

    async def _check_targets_met(
        self,
        improvements: Dict[str, float],
        targets: Dict[str, float]
    ) -> Dict[str, bool]:
        """Check if optimization targets were met."""
        targets_met = {}

        for target_name, target_value in targets.items():
            actual_improvement = improvements.get(target_name, 0)
            targets_met[target_name] = actual_improvement >= target_value

        return targets_met

    # Helper methods (simplified implementations)
    async def _calculate_layer_balance(self, layers: List[ExecutionLayer]) -> float:
        """Calculate balance between execution layers."""
        if not layers:
            return 0.0

        task_counts = [len(layer.tasks) for layer in layers]
        avg_tasks = sum(task_counts) / len(task_counts)
        variance = sum((count - avg_tasks) ** 2 for count in task_counts) / len(task_counts)

        # Return balance score (higher is more balanced)
        return 1.0 / (1.0 + variance)

    async def _calculate_critical_path(self, execution_graph: ExecutionGraph) -> int:
        """Calculate critical path length in the execution graph."""
        return len(execution_graph.execution_layers)  # Simplified

    async def _calculate_parallelization_factor(
        self,
        layers: List[ExecutionLayer],
        total_tasks: int
    ) -> float:
        """Calculate parallelization factor for layers."""
        if not layers or total_tasks == 0:
            return 0.0

        total_layer_tasks = sum(len(layer.tasks) for layer in layers)
        avg_tasks_per_layer = total_layer_tasks / len(layers)
        return avg_tasks_per_layer

    async def _split_large_layer(self, layer: ExecutionLayer) -> List[ExecutionLayer]:
        """Split large layer into smaller layers."""
        max_tasks = self.constraints["max_parallel_tasks"]
        split_layers = []

        for i in range(0, len(layer.tasks), max_tasks):
            chunk_tasks = layer.tasks[i:i + max_tasks]
            split_layer = ExecutionLayer(
                layer_number=layer.layer_number,
                tasks=chunk_tasks,
                dependencies_satisfied=[],
                estimated_duration_minutes=max(task.estimated_duration_minutes for task in chunk_tasks)
            )
            split_layers.append(split_layer)

        return split_layers

    async def _can_merge_layers(
        self,
        layer1: ExecutionLayer,
        layer2: ExecutionLayer,
        dependency_graph
    ) -> bool:
        """Check if two layers can be safely merged."""
        # Simplified check - in reality would need to verify dependencies
        return True  # Placeholder

    async def _balance_tasks_by_resources(self, tasks: List[CompleteTask]) -> List[CompleteTask]:
        """Balance tasks by estimated resource requirements."""
        # Sort by duration to balance resource usage
        return sorted(tasks, key=lambda t: t.estimated_duration_minutes)

    async def _analyze_task_parallelizability(self, task: CompleteTask) -> Dict[str, Any]:
        """Analyze if a task can be parallelized."""
        return {
            "parallelizable": len(task.depends_on) <= 2,  # Simplified
            "is_bottleneck": task.estimated_duration_minutes > 120,
            "bottleneck_type": "duration" if task.estimated_duration_minutes > 120 else None,
            "bottleneck_impact": "high" if task.estimated_duration_minutes > 180 else "medium"
        }

    async def _identify_optimization_opportunities(self, tasks: List[CompleteTask]) -> List[str]:
        """Identify optimization opportunities."""
        opportunities = []

        long_tasks = [task for task in tasks if task.estimated_duration_minutes > 120]
        if long_tasks:
            opportunities.append(f"Consider breaking down {len(long_tasks)} long-duration tasks")

        tasks_with_many_deps = [task for task in tasks if len(task.depends_on) > 3]
        if tasks_with_many_deps:
            opportunities.append(f"Simplify dependencies for {len(tasks_with_many_deps)} heavily dependent tasks")

        return opportunities

    async def _analyze_resource_conflicts(self, tasks: List[CompleteTask]) -> List[str]:
        """Analyze potential resource conflicts."""
        # Simplified analysis
        return []

    async def _identify_dependency_chains(self, tasks: List[CompleteTask]) -> List[Dict[str, Any]]:
        """Identify long dependency chains."""
        # Simplified analysis
        return []
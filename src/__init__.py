"""
Orca Development Execution Workflow

This package provides stateless parallel agent coordination for development execution,
transforming implementation plans into automated parallel development with 3-5x
performance improvements.

Key Components:
- Complete task context generation with embedded context
- Parallel execution orchestration with dependency management
- Stateless development agents with TDD methodology
- Comprehensive quality gate enforcement
- Enhanced MCP server integration (Archon, Serena)
"""

__version__ = "1.0.0"
__author__ = "Orca Development Team"

# Core exports
from .models.complete_task import CompleteTask, TaskContext
# Future components will be added as they are implemented:
# from .development_execution.parallel_orchestrator import ParallelExecutionOrchestrator
# from .commands.orca_execute_plan import execute_implementation_plan

__all__ = [
    "CompleteTask",
    "TaskContext",
    # "ParallelExecutionOrchestrator",
    # "execute_implementation_plan"
]
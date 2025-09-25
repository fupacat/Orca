"""
Context generation and management for stateless task execution.

This module provides intelligent context generation capabilities that transform
implementation plans into complete, stateless task contexts with embedded information.
"""

from .task_context_generator import TaskContextGenerator
from .implementation_plan_parser import ImplementationPlanParser
from .context_enrichment_engine import ContextEnrichmentEngine

__all__ = [
    "TaskContextGenerator",
    "ImplementationPlanParser",
    "ContextEnrichmentEngine"
]
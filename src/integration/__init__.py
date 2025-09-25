"""
Integration layer for connecting Orca planning workflows to execution capabilities.

This module provides seamless integration between the existing StartWorkflow
system and the new parallel execution engine, enabling automatic transition
from planning artifacts to live implementation.
"""

from .workflow_integrator import WorkflowIntegrator, WorkflowIntegrationError

__all__ = [
    "WorkflowIntegrator",
    "WorkflowIntegrationError"
]
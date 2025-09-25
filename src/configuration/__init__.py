"""
Configuration management for Orca execution workflows.

This module provides comprehensive configuration management for parallel execution,
quality gates, monitoring, and system integration settings.
"""

from .execution_config import (
    ExecutionConfiguration,
    ExecutionConfigManager,
    ExecutionSettings,
    QualitySettings,
    MonitoringSettings,
    MCPSettings,
    ResourceSettings,
    ExecutionStrategy,
    QualityGateLevel,
    ExecutionConfigurationError
)

__all__ = [
    "ExecutionConfiguration",
    "ExecutionConfigManager",
    "ExecutionSettings",
    "QualitySettings",
    "MonitoringSettings",
    "MCPSettings",
    "ResourceSettings",
    "ExecutionStrategy",
    "QualityGateLevel",
    "ExecutionConfigurationError"
]
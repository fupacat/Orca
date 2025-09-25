"""
Execution Configuration Management for Orca Development Workflows.

Provides comprehensive configuration management for parallel execution,
quality gates, agent coordination, and performance optimization settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class ExecutionStrategy(Enum):
    """Available execution strategies"""
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    HYBRID = "hybrid"
    SEQUENTIAL = "sequential"


class QualityGateLevel(Enum):
    """Quality gate enforcement levels"""
    DISABLED = "disabled"
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"


@dataclass
class ExecutionSettings:
    """Core execution configuration settings"""
    max_parallel_agents: int = 3
    execution_strategy: ExecutionStrategy = ExecutionStrategy.HYBRID
    task_timeout_minutes: int = 30
    session_timeout_hours: int = 8
    auto_retry_failed_tasks: bool = True
    max_retries: int = 2
    parallel_safety_margin: float = 0.15  # 15% buffer for parallel execution


@dataclass
class QualitySettings:
    """Quality gate configuration settings"""
    quality_gates_enabled: bool = True
    quality_level: QualityGateLevel = QualityGateLevel.STANDARD
    tdd_enforcement: bool = True
    security_scanning: bool = True
    performance_validation: bool = True
    code_review_required: bool = True
    coverage_threshold: float = 0.80
    security_severity_threshold: str = "medium"


@dataclass
class MonitoringSettings:
    """Monitoring and metrics configuration"""
    monitoring_enabled: bool = True
    metrics_collection_interval: float = 10.0
    alert_on_failures: bool = True
    alert_on_long_running_tasks: bool = True
    performance_tracking: bool = True
    detailed_logging: bool = True
    log_level: str = "INFO"


@dataclass
class MCPSettings:
    """MCP server configuration settings"""
    archon_url: str = "http://localhost:8051/mcp"
    archon_timeout: int = 30
    serena_enabled: bool = True
    connection_retry_attempts: int = 3
    connection_timeout: int = 15
    health_check_interval: int = 60


@dataclass
class ResourceSettings:
    """Resource management configuration"""
    memory_limit_mb: Optional[int] = None
    cpu_limit_percent: Optional[int] = None
    disk_space_threshold_gb: int = 5
    temp_cleanup_enabled: bool = True
    resource_monitoring: bool = True


@dataclass
class ExecutionConfiguration:
    """Complete execution configuration"""
    execution: ExecutionSettings = field(default_factory=ExecutionSettings)
    quality: QualitySettings = field(default_factory=QualitySettings)
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)
    mcp: MCPSettings = field(default_factory=MCPSettings)
    resources: ResourceSettings = field(default_factory=ResourceSettings)

    # Project-specific settings
    project_root: Optional[str] = None
    config_version: str = "1.0.0"
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ExecutionConfigurationError(Exception):
    """Exception raised for configuration-related errors"""
    pass


class ExecutionConfigManager:
    """
    Configuration manager for Orca execution settings.

    Handles loading, validation, and management of execution configuration
    from various sources including files, environment variables, and defaults.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config_file = self.project_root / ".orca" / "execution_config.json"
        self.global_config_file = Path.home() / ".orca" / "global_config.json"

        self._config: Optional[ExecutionConfiguration] = None

    def load_configuration(
        self,
        config_path: Optional[str] = None,
        override_settings: Optional[Dict[str, Any]] = None
    ) -> ExecutionConfiguration:
        """
        Load execution configuration from multiple sources.

        Args:
            config_path: Custom configuration file path
            override_settings: Settings to override loaded configuration

        Returns:
            ExecutionConfiguration: Loaded and validated configuration
        """
        try:
            # Start with default configuration
            config = ExecutionConfiguration()
            config.project_root = str(self.project_root)

            # Load global configuration if it exists
            if self.global_config_file.exists():
                global_config = self._load_config_from_file(self.global_config_file)
                config = self._merge_configurations(config, global_config)

            # Load project-specific configuration
            project_config_file = Path(config_path) if config_path else self.config_file
            if project_config_file.exists():
                project_config = self._load_config_from_file(project_config_file)
                config = self._merge_configurations(config, project_config)

            # Apply environment variable overrides
            config = self._apply_environment_overrides(config)

            # Apply explicit overrides
            if override_settings:
                config = self._apply_override_settings(config, override_settings)

            # Validate configuration
            self._validate_configuration(config)

            self._config = config
            return config

        except Exception as e:
            raise ExecutionConfigurationError(f"Failed to load configuration: {str(e)}")

    def save_configuration(
        self,
        config: ExecutionConfiguration,
        config_path: Optional[str] = None,
        global_config: bool = False
    ) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration to save
            config_path: Custom file path
            global_config: Whether to save as global configuration
        """
        try:
            if global_config:
                config_file = self.global_config_file
            else:
                config_file = Path(config_path) if config_path else self.config_file

            # Ensure directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict and save
            config_dict = asdict(config)

            # Convert enums to strings for JSON serialization
            config_dict = self._prepare_for_json(config_dict)

            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2, sort_keys=True)

        except Exception as e:
            raise ExecutionConfigurationError(f"Failed to save configuration: {str(e)}")

    def get_execution_strategy_config(self, strategy: ExecutionStrategy) -> Dict[str, Any]:
        """
        Get optimized settings for a specific execution strategy.

        Args:
            strategy: Execution strategy to get settings for

        Returns:
            Dict containing strategy-specific settings
        """
        strategy_configs = {
            ExecutionStrategy.AGGRESSIVE: {
                "max_parallel_agents": 5,
                "parallel_safety_margin": 0.05,
                "task_timeout_minutes": 20,
                "auto_retry_failed_tasks": False,
                "quality_level": QualityGateLevel.BASIC
            },
            ExecutionStrategy.CONSERVATIVE: {
                "max_parallel_agents": 2,
                "parallel_safety_margin": 0.30,
                "task_timeout_minutes": 60,
                "auto_retry_failed_tasks": True,
                "quality_level": QualityGateLevel.STRICT
            },
            ExecutionStrategy.HYBRID: {
                "max_parallel_agents": 3,
                "parallel_safety_margin": 0.15,
                "task_timeout_minutes": 30,
                "auto_retry_failed_tasks": True,
                "quality_level": QualityGateLevel.STANDARD
            },
            ExecutionStrategy.SEQUENTIAL: {
                "max_parallel_agents": 1,
                "parallel_safety_margin": 0.0,
                "task_timeout_minutes": 45,
                "auto_retry_failed_tasks": True,
                "quality_level": QualityGateLevel.STRICT
            }
        }

        return strategy_configs.get(strategy, strategy_configs[ExecutionStrategy.HYBRID])

    def create_project_config(self, project_settings: Dict[str, Any]) -> ExecutionConfiguration:
        """
        Create optimized configuration for a specific project.

        Args:
            project_settings: Project-specific requirements and constraints

        Returns:
            ExecutionConfiguration: Optimized configuration
        """
        # Start with base configuration
        config = ExecutionConfiguration()

        # Apply project-specific optimizations
        if project_settings.get("language") == "python":
            config.quality.tdd_enforcement = True
            config.quality.coverage_threshold = 0.85

        if project_settings.get("size") == "large":
            config.execution.max_parallel_agents = 5
            config.execution.session_timeout_hours = 12

        if project_settings.get("complexity") == "high":
            config.execution.execution_strategy = ExecutionStrategy.CONSERVATIVE
            config.quality.quality_level = QualityGateLevel.STRICT

        if project_settings.get("deadline") == "urgent":
            config.execution.execution_strategy = ExecutionStrategy.AGGRESSIVE
            config.quality.quality_level = QualityGateLevel.BASIC

        return config

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate execution environment and return status.

        Returns:
            Dict containing validation results
        """
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "mcp_servers": {},
            "system_resources": {},
            "dependencies": {}
        }

        try:
            # Check MCP server connectivity
            validation_results["mcp_servers"] = self._validate_mcp_servers()

            # Check system resources
            validation_results["system_resources"] = self._validate_system_resources()

            # Check dependencies
            validation_results["dependencies"] = self._validate_dependencies()

            # Determine overall validity
            if validation_results["errors"]:
                validation_results["valid"] = False

        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Environment validation failed: {str(e)}")

        return validation_results

    def _load_config_from_file(self, config_file: Path) -> ExecutionConfiguration:
        """Load configuration from JSON file"""
        with open(config_file, 'r') as f:
            config_dict = json.load(f)

        return self._dict_to_configuration(config_dict)

    def _dict_to_configuration(self, config_dict: Dict[str, Any]) -> ExecutionConfiguration:
        """Convert dictionary to ExecutionConfiguration"""
        # Handle enum conversions
        if "execution" in config_dict and "execution_strategy" in config_dict["execution"]:
            config_dict["execution"]["execution_strategy"] = ExecutionStrategy(
                config_dict["execution"]["execution_strategy"]
            )

        if "quality" in config_dict and "quality_level" in config_dict["quality"]:
            config_dict["quality"]["quality_level"] = QualityGateLevel(
                config_dict["quality"]["quality_level"]
            )

        # Create configuration objects
        config = ExecutionConfiguration()

        if "execution" in config_dict:
            config.execution = ExecutionSettings(**config_dict["execution"])
        if "quality" in config_dict:
            config.quality = QualitySettings(**config_dict["quality"])
        if "monitoring" in config_dict:
            config.monitoring = MonitoringSettings(**config_dict["monitoring"])
        if "mcp" in config_dict:
            config.mcp = MCPSettings(**config_dict["mcp"])
        if "resources" in config_dict:
            config.resources = ResourceSettings(**config_dict["resources"])

        # Copy top-level attributes
        for attr in ["project_root", "config_version", "custom_settings"]:
            if attr in config_dict:
                setattr(config, attr, config_dict[attr])

        return config

    def _merge_configurations(
        self,
        base_config: ExecutionConfiguration,
        override_config: ExecutionConfiguration
    ) -> ExecutionConfiguration:
        """Merge two configurations, with override taking precedence"""
        # This is a simplified merge - in practice, you'd want more sophisticated merging
        merged_dict = asdict(base_config)
        override_dict = asdict(override_config)

        def merge_dicts(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result

        merged_dict = merge_dicts(merged_dict, override_dict)
        return self._dict_to_configuration(merged_dict)

    def _apply_environment_overrides(self, config: ExecutionConfiguration) -> ExecutionConfiguration:
        """Apply environment variable overrides to configuration"""
        env_mappings = {
            "ORCA_MAX_AGENTS": ("execution", "max_parallel_agents", int),
            "ORCA_STRATEGY": ("execution", "execution_strategy", ExecutionStrategy),
            "ORCA_TIMEOUT": ("execution", "task_timeout_minutes", int),
            "ORCA_QUALITY_LEVEL": ("quality", "quality_level", QualityGateLevel),
            "ORCA_ARCHON_URL": ("mcp", "archon_url", str),
        }

        for env_var, (section, attr, type_converter) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = type_converter(os.environ[env_var])
                    setattr(getattr(config, section), attr, value)
                except (ValueError, TypeError):
                    pass  # Ignore invalid environment values

        return config

    def _apply_override_settings(
        self,
        config: ExecutionConfiguration,
        overrides: Dict[str, Any]
    ) -> ExecutionConfiguration:
        """Apply explicit override settings"""
        config_dict = asdict(config)

        def apply_overrides(base: Dict, overrides: Dict) -> Dict:
            for key, value in overrides.items():
                if "." in key:
                    # Handle nested keys like "execution.max_parallel_agents"
                    parts = key.split(".")
                    current = base
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    base[key] = value
            return base

        config_dict = apply_overrides(config_dict, overrides)
        return self._dict_to_configuration(config_dict)

    def _validate_configuration(self, config: ExecutionConfiguration) -> None:
        """Validate configuration for consistency and feasibility"""
        # Validate execution settings
        if config.execution.max_parallel_agents < 1:
            raise ExecutionConfigurationError("max_parallel_agents must be >= 1")

        if config.execution.task_timeout_minutes < 1:
            raise ExecutionConfigurationError("task_timeout_minutes must be >= 1")

        # Validate quality settings
        if not (0.0 <= config.quality.coverage_threshold <= 1.0):
            raise ExecutionConfigurationError("coverage_threshold must be between 0.0 and 1.0")

        # Validate monitoring settings
        if config.monitoring.metrics_collection_interval < 1.0:
            raise ExecutionConfigurationError("metrics_collection_interval must be >= 1.0")

    def _prepare_for_json(self, obj: Any) -> Any:
        """Prepare object for JSON serialization by converting enums"""
        if isinstance(obj, dict):
            return {key: self._prepare_for_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(item) for item in obj]
        elif isinstance(obj, Enum):
            return obj.value
        else:
            return obj

    def _validate_mcp_servers(self) -> Dict[str, bool]:
        """Validate MCP server connectivity"""
        # Simplified validation - in practice would check actual connectivity
        return {
            "archon": True,  # Would check HTTP connection
            "serena": True   # Would check stdio connection
        }

    def _validate_system_resources(self) -> Dict[str, Any]:
        """Validate system resource availability"""
        return {
            "memory_available_gb": 8.0,  # Would check actual available memory
            "disk_space_gb": 50.0,       # Would check actual disk space
            "cpu_cores": 4               # Would check actual CPU cores
        }

    def _validate_dependencies(self) -> Dict[str, bool]:
        """Validate required dependencies"""
        return {
            "python": True,    # Would check Python installation
            "git": True,       # Would check Git installation
            "pytest": True     # Would check testing framework
        }
"""
Integration tests for Orca workflow integration with execution capabilities.

Tests the complete flow from StartWorkflow planning to parallel execution,
ensuring seamless integration between all components.
"""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

from src.integration.workflow_integrator import WorkflowIntegrator
from src.configuration.execution_config import ExecutionConfigManager, ExecutionStrategy


class TestWorkflowIntegration:
    """Integration tests for complete workflow execution"""

    @pytest.fixture
    async def temp_project(self):
        """Create temporary project directory for testing"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir(parents=True)

        # Create sample plan.md
        plan_content = """# Implementation Plan

## Tasks

### Task 1: Setup Project Structure
- Create basic directory structure
- Initialize configuration files
- Setup development environment

**Dependencies**: None
**Estimated Duration**: 15 minutes
**Quality Gates**: Directory structure validation

### Task 2: Implement Core Models
- Create Pydantic models for data validation
- Add type annotations and documentation
- Implement model validation methods

**Dependencies**: Task 1
**Estimated Duration**: 30 minutes
**Quality Gates**: Unit tests, type checking

### Task 3: Setup Testing Framework
- Configure pytest with coverage
- Create test fixtures and utilities
- Setup CI/CD pipeline configuration

**Dependencies**: Task 1
**Estimated Duration**: 20 minutes
**Quality Gates**: Test execution, coverage validation
"""

        plan_file = project_path / "plan.md"
        with open(plan_file, 'w') as f:
            f.write(plan_content)

        yield str(project_path)

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def workflow_integrator(self, temp_project):
        """Create workflow integrator instance"""
        return WorkflowIntegrator(project_root=temp_project)

    @pytest.mark.asyncio
    async def test_plan_validation_success(self, workflow_integrator):
        """Test successful plan validation"""
        validation_results = await workflow_integrator.validate_plan_executability()

        assert validation_results["is_executable"] is True
        assert validation_results["total_tasks"] == 3
        assert len(validation_results["missing_context_tasks"]) <= 1  # Some context gaps expected
        assert len(validation_results["dependency_issues"]) == 0

    @pytest.mark.asyncio
    async def test_execution_preview_generation(self, workflow_integrator):
        """Test execution preview generation"""
        preview = await workflow_integrator.get_execution_preview()

        assert "error" not in preview
        assert preview["total_tasks"] == 3
        assert preview["execution_layers"] >= 2  # Some parallelization expected
        assert preview["max_parallelism"] >= 1
        assert preview["estimated_duration_minutes"] > 0
        assert len(preview["layer_breakdown"]) >= 2

    @pytest.mark.asyncio
    async def test_configuration_loading(self, temp_project):
        """Test configuration management"""
        config_manager = ExecutionConfigManager(project_root=temp_project)

        # Test default configuration
        config = config_manager.load_configuration()
        assert config.execution.max_parallel_agents == 3
        assert config.execution.execution_strategy == ExecutionStrategy.HYBRID
        assert config.quality.quality_gates_enabled is True

    @pytest.mark.asyncio
    async def test_strategy_specific_configuration(self, temp_project):
        """Test execution strategy-specific configurations"""
        config_manager = ExecutionConfigManager(project_root=temp_project)

        # Test aggressive strategy settings
        aggressive_settings = config_manager.get_execution_strategy_config(
            ExecutionStrategy.AGGRESSIVE
        )
        assert aggressive_settings["max_parallel_agents"] == 5
        assert aggressive_settings["parallel_safety_margin"] == 0.05

        # Test conservative strategy settings
        conservative_settings = config_manager.get_execution_strategy_config(
            ExecutionStrategy.CONSERVATIVE
        )
        assert conservative_settings["max_parallel_agents"] == 2
        assert conservative_settings["parallel_safety_margin"] == 0.30

    @pytest.mark.asyncio
    async def test_environment_validation(self, temp_project):
        """Test environment validation"""
        config_manager = ExecutionConfigManager(project_root=temp_project)

        validation_results = config_manager.validate_environment()

        # Should have validation structure
        assert "valid" in validation_results
        assert "mcp_servers" in validation_results
        assert "system_resources" in validation_results
        assert "dependencies" in validation_results

    @pytest.mark.asyncio
    async def test_plan_file_detection(self, workflow_integrator, temp_project):
        """Test automatic plan file detection"""
        # Should find plan.md in project root
        plan_file = await workflow_integrator._locate_plan_file()
        assert plan_file.name == "plan.md"
        assert plan_file.parent == Path(temp_project)

    @pytest.mark.asyncio
    async def test_integration_metadata_storage(self, workflow_integrator, temp_project):
        """Test integration metadata storage and retrieval"""
        from src.models.complete_task import CompleteTask, TaskContext
        from src.models.execution_graph import ExecutionGraph, DependencyGraph

        # Create sample tasks and execution graph
        sample_tasks = [
            CompleteTask(
                task_id="task-1",
                title="Sample Task",
                context=TaskContext(
                    project_context="Test project",
                    technical_context="Python development",
                    implementation_context="Create basic structure"
                )
            )
        ]

        dependency_graph = DependencyGraph(
            tasks=sample_tasks,
            dependencies={}
        )

        execution_graph = ExecutionGraph.from_dependency_graph(
            dependency_graph,
            optimization_strategy="hybrid"
        )

        # Store metadata
        await workflow_integrator._store_integration_metadata(sample_tasks, execution_graph)

        # Check metadata file was created
        metadata_file = Path(temp_project) / ".orca" / "integration_metadata.json"
        assert metadata_file.exists()

        # Validate metadata content
        import json
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        assert metadata["total_tasks"] == 1
        assert metadata["execution_layers"] == 1
        assert metadata["project_root"] == temp_project


class TestEndToEndWorkflow:
    """End-to-end workflow integration tests"""

    @pytest.fixture
    async def complete_project_setup(self):
        """Create complete project setup for end-to-end testing"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / "complete_test"
        project_path.mkdir(parents=True)

        # Create comprehensive plan.md with realistic tasks
        plan_content = """# Complete Development Plan

## Phase 1: Foundation

### Task: setup-environment
- Initialize Python project with pyproject.toml
- Setup virtual environment and dependencies
- Configure development tools (black, mypy, pytest)

**Dependencies**: None
**Duration**: 20 minutes
**TDD**: Setup test framework first
**Quality Gates**: Environment validation, tool configuration tests

### Task: data-models
- Design Pydantic models for core entities
- Implement validation and serialization
- Add comprehensive type annotations

**Dependencies**: setup-environment
**Duration**: 45 minutes
**TDD**: Model validation tests, serialization tests
**Quality Gates**: 100% test coverage, type checking

## Phase 2: Core Implementation

### Task: business-logic
- Implement core business logic functions
- Add error handling and logging
- Create service layer abstractions

**Dependencies**: data-models
**Duration**: 60 minutes
**TDD**: Comprehensive unit tests for all functions
**Quality Gates**: 95% test coverage, complexity analysis

### Task: api-endpoints
- Create FastAPI endpoints
- Implement request/response validation
- Add OpenAPI documentation

**Dependencies**: business-logic
**Duration**: 40 minutes
**TDD**: API integration tests, endpoint validation
**Quality Gates**: API tests, security validation

## Phase 3: Quality & Deployment

### Task: integration-tests
- Create end-to-end test suite
- Add performance benchmarks
- Setup test data management

**Dependencies**: api-endpoints
**Duration**: 35 minutes
**TDD**: Complete integration test coverage
**Quality Gates**: All tests pass, performance thresholds

### Task: deployment-config
- Create Docker configuration
- Setup CI/CD pipeline
- Add monitoring and logging

**Dependencies**: integration-tests
**Duration**: 30 minutes
**TDD**: Deployment validation tests
**Quality Gates**: Security scan, deployment verification
"""

        plan_file = project_path / "plan.md"
        with open(plan_file, 'w') as f:
            f.write(plan_content)

        # Create basic project structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()

        # Create pyproject.toml
        pyproject_content = """[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
description = "Test project for integration"
dependencies = [
    "pydantic>=2.0.0",
    "fastapi>=0.100.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.20.0",
    "black>=23.0.0",
    "mypy>=1.0.0"
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
"""

        pyproject_file = project_path / "pyproject.toml"
        with open(pyproject_file, 'w') as f:
            f.write(pyproject_content)

        yield str(project_path)

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.mark.asyncio
    async def test_complete_workflow_validation(self, complete_project_setup):
        """Test validation of complete realistic workflow"""
        integrator = WorkflowIntegrator(project_root=complete_project_setup)

        validation_results = await integrator.validate_plan_executability()

        # Should successfully parse and validate complex plan
        assert validation_results["is_executable"] is True
        assert validation_results["total_tasks"] == 6
        assert len(validation_results["dependency_issues"]) == 0

        # Most tasks should be well-formed
        readiness_rate = (
            validation_results["stateless_ready_tasks"] /
            validation_results["total_tasks"]
        )
        assert readiness_rate >= 0.7  # At least 70% of tasks ready

    @pytest.mark.asyncio
    async def test_complex_execution_preview(self, complete_project_setup):
        """Test execution preview for complex multi-phase plan"""
        integrator = WorkflowIntegrator(project_root=complete_project_setup)

        preview = await integrator.get_execution_preview()

        assert "error" not in preview
        assert preview["total_tasks"] == 6
        assert preview["execution_layers"] >= 3  # Should have multiple phases
        assert preview["max_parallelism"] >= 2   # Some tasks should be parallelizable

        # Should have realistic duration estimates
        assert 2.0 <= preview["estimated_duration_minutes"] <= 6.0  # 2-6 hours total

        # Should show good parallel efficiency
        assert preview["parallel_efficiency"] >= 0.5  # At least 50% efficiency

    @pytest.mark.asyncio
    async def test_configuration_integration(self, complete_project_setup):
        """Test configuration integration with complex workflows"""
        config_manager = ExecutionConfigManager(project_root=complete_project_setup)

        # Create project-specific configuration
        project_settings = {
            "language": "python",
            "size": "medium",
            "complexity": "high",
            "deadline": "normal"
        }

        config = config_manager.create_project_config(project_settings)

        # Should optimize for Python and high complexity
        assert config.quality.tdd_enforcement is True
        assert config.quality.coverage_threshold >= 0.85
        assert config.execution.execution_strategy == ExecutionStrategy.CONSERVATIVE

        # Save and reload configuration
        config_manager.save_configuration(config)

        reloaded_config = config_manager.load_configuration()
        assert reloaded_config.quality.tdd_enforcement is True
        assert reloaded_config.execution.execution_strategy == ExecutionStrategy.CONSERVATIVE


@pytest.mark.asyncio
async def test_mcp_integration_health():
    """Test MCP server integration health (mock-based)"""
    # This would normally test actual MCP connectivity
    # For now, validate the integration structure exists

    from src.mcp.connection_manager import MCPConnectionManager

    manager = MCPConnectionManager()

    # Validate manager has required methods
    assert hasattr(manager, 'initialize')
    assert hasattr(manager, 'health_check')
    assert hasattr(manager, 'get_archon_client')
    assert hasattr(manager, 'get_serena_client')


@pytest.mark.asyncio
async def test_execution_monitoring_integration():
    """Test execution monitoring integration"""
    from src.execution.execution_monitor import ExecutionMonitor

    monitor = ExecutionMonitor()

    # Test monitor initialization
    assert monitor.metrics_interval == 5.0
    assert len(monitor.active_sessions) == 0
    assert len(monitor.monitoring_tasks) == 0

    # Test default alert thresholds
    thresholds = monitor._get_default_alert_thresholds()
    assert "max_task_duration_seconds" in thresholds
    assert "max_failure_rate" in thresholds
    assert "min_completion_rate" in thresholds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
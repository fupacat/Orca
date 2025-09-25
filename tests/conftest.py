"""
pytest configuration and shared fixtures for development execution workflow tests
"""

import pytest
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from src.models.complete_task import CompleteTask, TaskContext, TDDSpecification, QualityGateRequirements
from src.models.execution_graph import ExecutionGraph, ExecutionLayer, DependencyGraph, TaskDependency
from src.models.quality_models import QualityResult, TDDValidation, SecurityValidation, PerformanceValidation, CodeQualityValidation
from src.models.result_models import TaskResult, ExecutionResult, ValidationResult


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_task_context() -> TaskContext:
    """Sample task context for testing"""
    return TaskContext(
        project_background=(
            "Implementing stateless parallel agent coordination system for Orca development "
            "execution workflow. This system transforms implementation plans into automated "
            "parallel development execution with 3-5x performance improvements."
        ),
        architecture_context={
            "integration_approach": "Hybrid extension architecture",
            "file_structure": "src/models/ directory with Pydantic models",
            "data_flow": "Implementation Plan → Task Context Generator → Complete Tasks"
        },
        requirements_context={
            "stateless_design": "Each task must contain complete embedded context",
            "type_safety": "Comprehensive type hints and Pydantic validation"
        },
        implementation_guidance={
            "primary_models": ["CompleteTask", "TaskContext", "TDDSpecification"],
            "validation_patterns": "Use Pydantic Field with descriptions",
            "testing_approach": "Unit tests for model validation and serialization"
        },
        file_locations={
            "src/models/complete_task.py": "Main task specification models",
            "src/models/execution_graph.py": "Parallel execution models",
            "tests/test_models.py": "Model testing"
        },
        dependencies=["project_setup"],
        environment_context={
            "python_version": "3.11+",
            "required_packages": ["pydantic", "pytest"],
            "development_environment": "Windows with WSL support"
        }
    )


@pytest.fixture
def sample_tdd_specification() -> TDDSpecification:
    """Sample TDD specification for testing"""
    return TDDSpecification(
        test_file="tests/test_models.py",
        test_cases=[
            "@test CompleteTask model validation with valid data",
            "@test CompleteTask.is_stateless_ready() validation",
            "@test TaskContext model with complete embedded context",
            "@test JSON serialization and deserialization"
        ],
        coverage_requirements="95%+ test coverage",
        test_framework="pytest",
        mock_requirements=["mock_mcp_servers", "sample_implementation_plans"]
    )


@pytest.fixture
def sample_quality_requirements() -> QualityGateRequirements:
    """Sample quality gate requirements for testing"""
    return QualityGateRequirements(
        tdd_requirements={
            "minimum_coverage": 0.95,
            "red_green_refactor": True,
            "all_tests_pass": True
        },
        security_requirements={
            "input_validation": True,
            "vulnerability_scanning": True,
            "secure_coding_practices": True
        },
        performance_requirements={
            "benchmark_execution": True,
            "resource_usage_validation": True,
            "performance_regression_check": True
        },
        code_quality_requirements={
            "static_analysis": True,
            "type_checking": True,
            "linting_compliance": True,
            "documentation_coverage": True
        }
    )


@pytest.fixture
def sample_complete_task(
    sample_task_context: TaskContext,
    sample_tdd_specification: TDDSpecification,
    sample_quality_requirements: QualityGateRequirements
) -> CompleteTask:
    """Sample complete task for testing"""
    return CompleteTask(
        task_id="test_pydantic_models",
        title="Test Pydantic Data Models Implementation",
        complete_context=sample_task_context,
        tdd_specifications=sample_tdd_specification,
        quality_gates=sample_quality_requirements,
        acceptance_criteria=[
            "CompleteTask model validates task completeness for stateless execution",
            "TaskContext model embeds complete project context per task",
            "All models are JSON serializable with schema generation",
            "Comprehensive validation with clear error messages"
        ],
        estimated_duration_minutes=120,
        priority=90
    )


@pytest.fixture
def sample_task_dependency() -> TaskDependency:
    """Sample task dependency for testing"""
    return TaskDependency(
        from_task_id="task2",
        to_task_id="task1",
        dependency_type="code",
        description="Task 2 requires models from Task 1",
        is_blocking=True
    )


@pytest.fixture
def sample_dependency_graph() -> DependencyGraph:
    """Sample dependency graph for testing"""
    return DependencyGraph(
        tasks=["task1", "task2", "task3", "task4"],
        dependencies=[
            TaskDependency(
                from_task_id="task2",
                to_task_id="task1",
                dependency_type="code",
                description="Task 2 requires models from Task 1"
            ),
            TaskDependency(
                from_task_id="task3",
                to_task_id="task1",
                dependency_type="code",
                description="Task 3 requires models from Task 1"
            ),
            TaskDependency(
                from_task_id="task4",
                to_task_id="task2",
                dependency_type="file",
                description="Task 4 requires files from Task 2"
            )
        ]
    )


@pytest.fixture
def sample_execution_layer(sample_complete_task: CompleteTask) -> ExecutionLayer:
    """Sample execution layer for testing"""
    task2 = sample_complete_task.copy(update={"task_id": "task2", "title": "Task 2"})
    task3 = sample_complete_task.copy(update={"task_id": "task3", "title": "Task 3"})

    return ExecutionLayer(
        layer_number=0,
        tasks=[sample_complete_task, task2, task3],
        dependencies_satisfied=[],
        estimated_duration_minutes=120
    )


@pytest.fixture
def sample_quality_validation() -> QualityResult:
    """Sample quality validation results for testing"""
    return QualityResult(
        task_id="test_task",
        overall_status="passed",
        tdd_validation=TDDValidation(
            status="passed",
            test_coverage_percentage=96.5,
            minimum_coverage_required=95.0,
            total_lines=100,
            covered_lines=96,
            test_count=15,
            passing_tests=15,
            failing_tests=0,
            red_green_refactor_cycle_followed=True,
            test_execution_time_seconds=2.5
        ),
        security_validation=SecurityValidation(
            status="passed",
            vulnerability_scan_passed=True,
            input_validation_implemented=True,
            secure_coding_practices_followed=True,
            high_severity_vulnerabilities=0,
            medium_severity_vulnerabilities=0,
            low_severity_vulnerabilities=1
        ),
        performance_validation=PerformanceValidation(
            status="passed",
            benchmark_executed=True,
            execution_time_seconds=1.8,
            memory_usage_mb=45.2,
            cpu_usage_percentage=25.0,
            performance_requirements_met=True
        ),
        code_quality_validation=CodeQualityValidation(
            status="passed",
            static_analysis_passed=True,
            type_checking_passed=True,
            linting_passed=True,
            complexity_score=4.2,
            maintainability_index=85.0,
            documentation_coverage_percentage=88.0,
            code_style_violations=0
        )
    )


@pytest.fixture
def sample_task_result(sample_quality_validation: QualityResult) -> TaskResult:
    """Sample task execution result for testing"""
    return TaskResult(
        task_id="test_task",
        status="completed",
        start_time=datetime(2025, 1, 23, 10, 0, 0),
        end_time=datetime(2025, 1, 23, 12, 0, 0),
        execution_duration_seconds=7200,
        agent_id="agent_001",
        implementation_artifacts=["src/models/complete_task.py", "src/models/execution_graph.py"],
        test_artifacts=["tests/test_models.py"],
        documentation_artifacts=["docs/models.md"],
        implementation_summary="Implemented Pydantic data models with comprehensive validation",
        quality_validation=sample_quality_validation,
        retry_count=0
    )


@pytest.fixture
def sample_execution_result(sample_task_result: TaskResult) -> ExecutionResult:
    """Sample execution result for testing"""
    task2 = sample_task_result.copy(update={"task_id": "task2"})
    task3 = sample_task_result.copy(update={"task_id": "task3"})

    return ExecutionResult(
        execution_id="exec_test_001",
        start_time=datetime(2025, 1, 23, 9, 0, 0),
        end_time=datetime(2025, 1, 23, 15, 0, 0),
        total_duration_seconds=21600,
        total_tasks=3,
        successful_tasks=3,
        failed_tasks=0,
        cancelled_tasks=0,
        task_results=[sample_task_result, task2, task3],
        parallel_execution_stats={
            "total_layers": 2,
            "parallelization_factor": 0.67,
            "average_tasks_per_layer": 1.5
        },
        performance_metrics={
            "parallel_efficiency": 3.2,
            "average_task_duration": 7200
        }
    )


# Mock fixtures for external dependencies
@pytest.fixture
def mock_archon_client():
    """Mock Archon MCP client for testing"""
    mock = AsyncMock()
    mock.manage_project = AsyncMock(return_value={"success": True, "project_id": "test_project"})
    mock.manage_task = AsyncMock(return_value={"success": True, "task_id": "test_task"})
    mock.health_check = AsyncMock(return_value={"success": True, "status": "healthy"})
    return mock


@pytest.fixture
def mock_serena_client():
    """Mock Serena MCP client for testing"""
    mock = AsyncMock()
    mock.list_dir = AsyncMock(return_value={"dirs": ["src", "tests"], "files": ["setup.py"]})
    mock.get_symbols_overview = AsyncMock(return_value={"symbols": []})
    mock.search_for_pattern = AsyncMock(return_value={})
    return mock


@pytest.fixture
def mock_implementation_plan() -> Dict[str, Any]:
    """Mock implementation plan for testing"""
    return {
        "title": "Test Development Project",
        "description": "Sample project for testing development execution workflow",
        "background": (
            "This is a test implementation plan used for validating the development "
            "execution workflow system. It includes multiple tasks with various "
            "dependencies to test parallel execution coordination."
        ),
        "architecture": {
            "approach": "Test-driven development with modular architecture",
            "technology_stack": ["Python", "pytest", "Pydantic"]
        },
        "tasks": [
            {
                "id": "task1",
                "title": "Foundation Setup",
                "description": "Set up project foundation and basic structure",
                "dependencies": [],
                "estimated_hours": 2
            },
            {
                "id": "task2",
                "title": "Core Implementation",
                "description": "Implement core functionality",
                "dependencies": ["task1"],
                "estimated_hours": 4
            },
            {
                "id": "task3",
                "title": "Testing Framework",
                "description": "Set up comprehensive testing",
                "dependencies": ["task1"],
                "estimated_hours": 3
            },
            {
                "id": "task4",
                "title": "Integration",
                "description": "Integrate all components",
                "dependencies": ["task2", "task3"],
                "estimated_hours": 2
            }
        ],
        "quality_requirements": {
            "test_coverage": 95,
            "security_scanning": True,
            "performance_testing": True,
            "code_quality": True
        }
    }


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create temporary project directory for testing"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create basic structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()

    return project_dir


# Helper functions for tests
def create_sample_tasks(count: int = 3) -> List[CompleteTask]:
    """Create a list of sample complete tasks for testing"""
    tasks = []
    for i in range(count):
        task = CompleteTask(
            task_id=f"test_task_{i+1}",
            title=f"Test Task {i+1}",
            complete_context=TaskContext(
                project_background="Test project background",
                architecture_context={"test": "context"},
                requirements_context={"test": "requirements"},
                implementation_guidance={"test": "guidance"},
                file_locations={f"test_file_{i+1}.py": f"Test file {i+1}"}
            ),
            tdd_specifications=TDDSpecification(
                test_file=f"test_task_{i+1}_test.py",
                test_cases=[f"@test Task {i+1} functionality"]
            ),
            quality_gates=QualityGateRequirements(),
            acceptance_criteria=[f"Task {i+1} meets requirements"]
        )
        tasks.append(task)
    return tasks


# Test data fixtures
@pytest.fixture
def test_data_dir() -> Path:
    """Path to test data directory"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_test_data(test_data_dir: Path) -> Dict[str, Any]:
    """Load sample test data"""
    # This would load from JSON files in the fixtures directory
    # For now, return inline data
    return {
        "sample_plan": {
            "title": "Sample Implementation Plan",
            "tasks": create_sample_tasks(4)
        },
        "expected_results": {
            "parallelization_factor": 0.75,
            "estimated_speedup": 3.2
        }
    }


# Performance testing fixtures
@pytest.fixture
def performance_baseline() -> Dict[str, float]:
    """Performance baselines for testing"""
    return {
        "task_context_generation_seconds": 0.1,
        "dependency_analysis_seconds": 0.5,
        "parallel_coordination_seconds": 1.0,
        "quality_validation_seconds": 2.0
    }


# Async test utilities
@pytest.fixture
def async_test_timeout() -> float:
    """Default timeout for async tests"""
    return 30.0  # 30 seconds


# Markers for test categorization
pytest_plugins = ["pytest_asyncio"]

# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "parallel: Parallel execution tests")
    config.addinivalue_line("markers", "quality: Quality gate tests")
    config.addinivalue_line("markers", "mcp: MCP integration tests")
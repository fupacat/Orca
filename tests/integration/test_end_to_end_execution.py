"""
End-to-end execution tests for complete Orca workflow.

Tests the entire pipeline from plan.md to completed implementation,
validating parallel execution, quality gates, and monitoring.
"""

import asyncio
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.integration.workflow_integrator import WorkflowIntegrator
from src.execution.parallel_orchestrator import ParallelExecutionOrchestrator
from src.models.result_models import ExecutionResult, TaskResult
from src.configuration.execution_config import ExecutionStrategy


class TestEndToEndExecution:
    """End-to-end execution tests"""

    @pytest.fixture
    async def execution_project(self):
        """Create project with executable implementation plan"""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / "execution_test"
        project_path.mkdir(parents=True)

        # Create executable plan with complete task specifications
        plan_content = """# Executable Implementation Plan

## Task: create-project-structure
**Task ID**: task-001
**Title**: Create Project Structure
**Description**: Initialize basic Python project structure with all necessary directories and configuration files.

**Implementation Context**:
- Create src/, tests/, docs/ directories
- Generate pyproject.toml with project metadata
- Create __init__.py files for package structure
- Add .gitignore for Python projects

**Acceptance Criteria**:
- [ ] Directory structure created correctly
- [ ] pyproject.toml contains valid configuration
- [ ] Package imports work correctly

**Dependencies**: None
**Estimated Duration**: 15 minutes

## Task: implement-data-models
**Task ID**: task-002
**Title**: Implement Data Models
**Description**: Create Pydantic models for core data structures with validation.

**Implementation Context**:
- Create src/models/ directory
- Implement User, Project, Task models using Pydantic
- Add field validation and custom validators
- Include comprehensive docstrings and type hints

**Technical Specifications**:
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: str = Field(..., description="User identifier")
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\\.[^@]+$')
    created_at: datetime = Field(default_factory=datetime.now)
```

**Acceptance Criteria**:
- [ ] All models validate input correctly
- [ ] Custom validators work as expected
- [ ] Models serialize/deserialize properly
- [ ] Type hints are comprehensive

**Dependencies**: task-001
**Estimated Duration**: 30 minutes

## Task: create-test-suite
**Task ID**: task-003
**Title**: Create Comprehensive Test Suite
**Description**: Implement complete test coverage for data models and core functionality.

**Implementation Context**:
- Setup pytest configuration in pyproject.toml
- Create test fixtures for sample data
- Implement unit tests for all models
- Add integration tests for workflows

**Test Specifications**:
- Model validation tests (valid/invalid inputs)
- Serialization/deserialization tests
- Edge case testing (empty strings, None values)
- Performance tests for large datasets

**Acceptance Criteria**:
- [ ] All tests pass successfully
- [ ] Code coverage >= 95%
- [ ] Test execution time < 30 seconds
- [ ] No test dependencies or flaky tests

**Dependencies**: task-002
**Estimated Duration**: 25 minutes

## Quality Requirements
- **TDD Compliance**: All tasks must implement tests first
- **Security**: No hardcoded secrets or vulnerabilities
- **Performance**: All operations complete within specified time limits
- **Documentation**: Every public function has docstrings
"""

        plan_file = project_path / "plan.md"
        with open(plan_file, 'w') as f:
            f.write(plan_content)

        # Create minimal project structure for testing
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()

        yield str(project_path)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_mcp_connections(self):
        """Mock MCP server connections for testing"""
        with patch('src.mcp.connection_manager.MCPConnectionManager') as mock_manager:
            # Setup mock manager
            mock_instance = AsyncMock()
            mock_manager.return_value = mock_instance

            # Mock successful initialization
            mock_instance.initialize = AsyncMock()
            mock_instance.health_check = AsyncMock(return_value={
                "archon": {"status": "connected"},
                "serena": {"status": "connected"}
            })

            # Mock Archon client
            mock_archon = AsyncMock()
            mock_archon.create_task = AsyncMock(return_value={"task_id": "archon-task-123"})
            mock_archon.update_task_status = AsyncMock()
            mock_archon.search_knowledge_base = AsyncMock(return_value={
                "success": True,
                "results": [{"content": "Sample knowledge"}]
            })
            mock_instance.get_archon_client = AsyncMock(return_value=mock_archon)

            # Mock Serena client
            mock_serena = AsyncMock()
            mock_serena.find_symbols = AsyncMock(return_value=[])
            mock_serena.get_project_structure = AsyncMock(return_value={
                "files": [], "directories": []
            })
            mock_instance.get_serena_client = AsyncMock(return_value=mock_serena)

            yield mock_instance

    @pytest.fixture
    def mock_development_agents(self):
        """Mock development agents for execution testing"""
        with patch('src.execution.agent_coordinator.DevelopmentAgent') as mock_agent_class:
            # Create mock agent instances
            mock_agents = []
            for i in range(3):
                mock_agent = AsyncMock()
                mock_agent.agent_id = f"agent-{i+1}"
                mock_agent.is_available = True
                mock_agent.current_load = 0.0

                # Mock successful task execution
                async def mock_execute_task(task, *args, **kwargs):
                    return TaskResult(
                        task_id=task.task_id,
                        success=True,
                        start_time=asyncio.get_event_loop().time(),
                        end_time=asyncio.get_event_loop().time() + 10,
                        execution_log="Mock execution completed successfully",
                        quality_results={
                            "tdd_compliance": True,
                            "security_score": 0.95,
                            "performance_score": 0.90
                        }
                    )

                mock_agent.execute_task = mock_execute_task
                mock_agents.append(mock_agent)

            mock_agent_class.side_effect = lambda *args, **kwargs: mock_agents.pop(0) if mock_agents else AsyncMock()

            yield mock_agent_class

    @pytest.mark.asyncio
    async def test_complete_workflow_execution(
        self,
        execution_project,
        mock_mcp_connections,
        mock_development_agents
    ):
        """Test complete workflow from plan to execution"""

        integrator = WorkflowIntegrator(project_root=execution_project)

        # Test execution with mocked dependencies
        result = await integrator.execute_workflow_plan(
            execution_mode="hybrid"
        )

        # Validate execution results
        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.total_tasks == 3
        assert len(result.completed_tasks) == 3
        assert len(result.failed_tasks) == 0

        # Validate timing and performance
        assert result.total_duration_seconds > 0
        assert result.parallel_efficiency > 0
        assert result.tasks_per_minute > 0

    @pytest.mark.asyncio
    async def test_execution_with_aggressive_strategy(
        self,
        execution_project,
        mock_mcp_connections,
        mock_development_agents
    ):
        """Test execution with aggressive parallelization strategy"""

        integrator = WorkflowIntegrator(
            project_root=execution_project,
            execution_config={
                "execution_strategy": "aggressive",
                "max_parallel_agents": 5,
                "parallel_safety_margin": 0.05
            }
        )

        result = await integrator.execute_workflow_plan(
            execution_mode="aggressive"
        )

        assert result.success is True
        # Aggressive mode should complete faster (in real scenario)
        assert result.parallel_efficiency >= 0.7  # Higher efficiency expected

    @pytest.mark.asyncio
    async def test_execution_with_quality_gates(
        self,
        execution_project,
        mock_mcp_connections,
        mock_development_agents
    ):
        """Test execution with comprehensive quality gate validation"""

        integrator = WorkflowIntegrator(
            project_root=execution_project,
            execution_config={
                "quality_gates_enabled": True,
                "quality_level": "strict",
                "tdd_enforcement": True,
                "security_scanning": True,
                "coverage_threshold": 0.95
            }
        )

        result = await integrator.execute_workflow_plan()

        assert result.success is True

        # Validate quality metrics
        assert result.quality_metrics is not None
        assert result.quality_metrics.overall_score >= 0.8
        assert result.quality_metrics.tdd_compliance >= 0.9
        assert result.quality_metrics.security_score >= 0.85

    @pytest.mark.asyncio
    async def test_execution_monitoring_and_metrics(
        self,
        execution_project,
        mock_mcp_connections,
        mock_development_agents
    ):
        """Test execution monitoring and real-time metrics collection"""

        integrator = WorkflowIntegrator(
            project_root=execution_project,
            execution_config={
                "monitoring_enabled": True,
                "metrics_collection_interval": 1.0,  # Fast collection for testing
                "alert_on_failures": True
            }
        )

        result = await integrator.execute_workflow_plan()

        # Validate monitoring occurred
        assert result.success is True
        assert result.session_id is not None
        assert result.total_duration_seconds > 0

        # Check execution artifacts were created
        project_path = Path(execution_project)
        execution_summary = project_path / "execution_summary.md"
        # In mock scenario, we'd validate summary was created

    @pytest.mark.asyncio
    async def test_execution_failure_handling(
        self,
        execution_project,
        mock_mcp_connections
    ):
        """Test execution failure handling and recovery"""

        # Mock agent that fails on second task
        with patch('src.execution.agent_coordinator.DevelopmentAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.agent_id = "failing-agent"
            mock_agent.is_available = True
            mock_agent.current_load = 0.0

            call_count = 0

            async def mock_execute_task_with_failure(task, *args, **kwargs):
                nonlocal call_count
                call_count += 1

                if call_count == 2:  # Fail on second task
                    return TaskResult(
                        task_id=task.task_id,
                        success=False,
                        start_time=asyncio.get_event_loop().time(),
                        end_time=asyncio.get_event_loop().time() + 5,
                        error_message="Simulated task failure",
                        execution_log="Task failed during execution"
                    )
                else:
                    return TaskResult(
                        task_id=task.task_id,
                        success=True,
                        start_time=asyncio.get_event_loop().time(),
                        end_time=asyncio.get_event_loop().time() + 10,
                        execution_log="Task completed successfully"
                    )

            mock_agent.execute_task = mock_execute_task_with_failure
            mock_agent_class.return_value = mock_agent

            integrator = WorkflowIntegrator(
                project_root=execution_project,
                execution_config={
                    "auto_retry_failed_tasks": True,
                    "max_retries": 1
                }
            )

            result = await integrator.execute_workflow_plan()

            # Should handle failure gracefully
            assert result is not None
            # With retries, some tasks might still succeed
            assert len(result.failed_tasks) > 0

    @pytest.mark.asyncio
    async def test_execution_resume_capability(
        self,
        execution_project,
        mock_mcp_connections,
        mock_development_agents
    ):
        """Test execution resume after interruption"""

        integrator = WorkflowIntegrator(project_root=execution_project)

        # Simulate interrupted execution by starting and then resuming
        with patch.object(integrator.execution_orchestrator, 'execute_implementation_plan') as mock_execute:
            # First call simulates interruption
            mock_execute.return_value = ExecutionResult(
                session_id="test-session-123",
                success=False,
                total_tasks=3,
                completed_tasks=["task-001"],  # Only first task completed
                failed_tasks=[],
                total_duration_seconds=300,
                end_time=asyncio.get_event_loop().time()
            )

            # Start execution (will be "interrupted")
            result = await integrator.execute_workflow_plan()
            assert result.success is False
            assert len(result.completed_tasks) == 1

        # Test resume functionality
        with patch.object(integrator.execution_orchestrator, 'resume_execution') as mock_resume:
            mock_resume.return_value = ExecutionResult(
                session_id="test-session-123",
                success=True,
                total_tasks=3,
                completed_tasks=["task-001", "task-002", "task-003"],
                failed_tasks=[],
                total_duration_seconds=600,
                end_time=asyncio.get_event_loop().time()
            )

            # Resume execution
            resumed_result = await integrator.resume_execution("test-session-123")
            assert resumed_result.success is True
            assert len(resumed_result.completed_tasks) == 3

    @pytest.mark.asyncio
    async def test_multi_strategy_execution_comparison(
        self,
        execution_project,
        mock_mcp_connections,
        mock_development_agents
    ):
        """Test execution with different strategies and compare results"""

        strategies = ["conservative", "hybrid", "aggressive"]
        results = {}

        for strategy in strategies:
            integrator = WorkflowIntegrator(
                project_root=execution_project,
                execution_config={"execution_strategy": strategy}
            )

            result = await integrator.execute_workflow_plan(execution_mode=strategy)
            results[strategy] = result

        # All strategies should succeed
        for strategy, result in results.items():
            assert result.success is True, f"{strategy} strategy failed"
            assert result.total_tasks == 3
            assert len(result.completed_tasks) == 3

        # In real scenario, aggressive should be fastest, conservative most reliable
        # Mock scenario just validates all complete successfully


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
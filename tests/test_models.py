"""
Unit tests for Pydantic data models.

Tests validation, serialization, and business logic for all model classes
including CompleteTask, ExecutionGraph, QualityModels, and ResultModels.
"""

import pytest
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from src.models.complete_task import CompleteTask, TaskContext, TDDSpecification, QualityGateRequirements
from src.models.execution_graph import ExecutionGraph, ExecutionLayer, DependencyGraph, TaskDependency
from src.models.quality_models import (
    QualityResult, TDDValidation, SecurityValidation,
    PerformanceValidation, CodeQualityValidation, QualityGateStatus
)
from src.models.result_models import (
    TaskResult, ExecutionResult, ValidationResult,
    TaskExecutionStatus, ValidationStatus
)


class TestCompleteTask:
    """Test CompleteTask model validation and behavior"""

    def test_complete_task_creation(self, sample_complete_task):
        """Test CompleteTask model creation with valid data"""
        task = sample_complete_task

        assert task.task_id == "test_pydantic_models"
        assert task.title == "Test Pydantic Data Models Implementation"
        assert task.estimated_duration_minutes == 120
        assert task.priority == 90
        assert len(task.acceptance_criteria) == 4

    def test_complete_task_validation(self, sample_task_context, sample_tdd_specification, sample_quality_requirements):
        """Test CompleteTask validation rules"""
        # Test valid task
        task = CompleteTask(
            task_id="valid_task",
            title="Valid Task Title",
            complete_context=sample_task_context,
            tdd_specifications=sample_tdd_specification,
            quality_gates=sample_quality_requirements,
            acceptance_criteria=["Criterion 1"]
        )
        assert task.is_stateless_ready()

        # Test invalid task ID (contains spaces)
        with pytest.raises(ValueError):
            CompleteTask(
                task_id="invalid task id",
                title="Valid Title",
                complete_context=sample_task_context,
                tdd_specifications=sample_tdd_specification,
                quality_gates=sample_quality_requirements,
                acceptance_criteria=["Criterion 1"]
            )

        # Test title too short
        with pytest.raises(ValueError):
            CompleteTask(
                task_id="valid_task",
                title="Short",  # Less than 10 characters
                complete_context=sample_task_context,
                tdd_specifications=sample_tdd_specification,
                quality_gates=sample_quality_requirements,
                acceptance_criteria=["Criterion 1"]
            )

    def test_is_stateless_ready(self):
        """Test stateless readiness validation"""
        # Complete context
        complete_context = TaskContext(
            project_background="Complete background",
            architecture_context={"key": "value"},
            requirements_context={"req": "value"},
            implementation_guidance={"guide": "value"},
            file_locations={"file.py": "description"}
        )

        # TDD specifications with tests
        tdd_specs = TDDSpecification(
            test_file="test_file.py",
            test_cases=["@test Test case 1"]
        )

        task = CompleteTask(
            task_id="test_task",
            title="Test Task Title",
            complete_context=complete_context,
            tdd_specifications=tdd_specs,
            quality_gates=QualityGateRequirements(),
            acceptance_criteria=["Criterion 1"]
        )

        assert task.is_stateless_ready()

        # Test with missing implementation guidance
        incomplete_context = TaskContext(
            project_background="Background",
            architecture_context={},
            requirements_context={},
            implementation_guidance={},  # Empty
            file_locations={}
        )

        incomplete_task = CompleteTask(
            task_id="test_task",
            title="Test Task Title",
            complete_context=incomplete_context,
            tdd_specifications=tdd_specs,
            quality_gates=QualityGateRequirements(),
            acceptance_criteria=["Criterion 1"]
        )

        assert not incomplete_task.is_stateless_ready()

    def test_json_serialization(self, sample_complete_task):
        """Test JSON serialization and deserialization"""
        # Serialize to JSON
        json_data = sample_complete_task.json()
        assert isinstance(json_data, str)

        # Deserialize from JSON
        restored_task = CompleteTask.parse_raw(json_data)
        assert restored_task.task_id == sample_complete_task.task_id
        assert restored_task.title == sample_complete_task.title
        assert restored_task.estimated_duration_minutes == sample_complete_task.estimated_duration_minutes

    def test_schema_generation(self):
        """Test Pydantic schema generation"""
        schema = CompleteTask.schema()

        assert "title" in schema
        assert "properties" in schema
        assert "task_id" in schema["properties"]
        assert "complete_context" in schema["properties"]
        assert "tdd_specifications" in schema["properties"]


class TestTaskContext:
    """Test TaskContext model validation and behavior"""

    def test_task_context_creation(self, sample_task_context):
        """Test TaskContext model creation"""
        context = sample_task_context

        assert "Implementing stateless parallel agent coordination" in context.project_background
        assert "Hybrid extension architecture" in context.architecture_context["integration_approach"]
        assert "CompleteTask" in context.implementation_guidance["primary_models"]

    def test_context_completeness_check(self):
        """Test context completeness validation"""
        complete_context = TaskContext(
            project_background="Complete background",
            architecture_context={"approach": "microservices"},
            requirements_context={"type": "functional"},
            implementation_guidance={"patterns": ["pattern1"]},
            file_locations={"src/main.py": "Main module"},
            dependencies=["dep1"],
            environment_context={"python": "3.11"}
        )

        assert complete_context.has_complete_context()

        incomplete_context = TaskContext(
            project_background="",  # Empty
            architecture_context={},
            requirements_context={},
            implementation_guidance={},
            file_locations={}
        )

        assert not incomplete_context.has_complete_context()


class TestExecutionGraph:
    """Test ExecutionGraph and related models"""

    def test_dependency_graph_creation(self, sample_dependency_graph):
        """Test DependencyGraph creation and validation"""
        dep_graph = sample_dependency_graph

        assert len(dep_graph.tasks) == 4
        assert len(dep_graph.dependencies) == 3
        assert dep_graph.has_task("task1")
        assert not dep_graph.has_task("nonexistent_task")

    def test_dependency_validation(self):
        """Test dependency validation logic"""
        # Valid dependency graph (no cycles)
        dep_graph = DependencyGraph(
            tasks=["task1", "task2", "task3"],
            dependencies=[
                TaskDependency(
                    from_task_id="task2",
                    to_task_id="task1",
                    dependency_type="code"
                ),
                TaskDependency(
                    from_task_id="task3",
                    to_task_id="task1",
                    dependency_type="code"
                )
            ]
        )

        assert dep_graph.validate_acyclic()

        # Invalid dependency graph (cycle)
        cyclic_graph = DependencyGraph(
            tasks=["task1", "task2"],
            dependencies=[
                TaskDependency(
                    from_task_id="task1",
                    to_task_id="task2",
                    dependency_type="code"
                ),
                TaskDependency(
                    from_task_id="task2",
                    to_task_id="task1",
                    dependency_type="code"
                )
            ]
        )

        assert not cyclic_graph.validate_acyclic()

    def test_execution_layer(self, sample_execution_layer):
        """Test ExecutionLayer functionality"""
        layer = sample_execution_layer

        assert layer.layer_number == 0
        assert len(layer.tasks) == 3
        assert layer.estimated_duration_minutes == 120

        # Test layer validation
        assert layer.can_execute_in_parallel()

        # Test duration calculation
        layer.calculate_layer_duration()
        # Duration should be max of individual task durations when parallel
        expected_duration = max(task.estimated_duration_minutes for task in layer.tasks)
        assert layer.estimated_duration_minutes == expected_duration

    def test_execution_graph(self, sample_dependency_graph, sample_complete_task):
        """Test complete ExecutionGraph functionality"""
        # Create simple execution graph
        tasks = [sample_complete_task]

        layer = ExecutionLayer(
            layer_number=0,
            tasks=tasks,
            dependencies_satisfied=[],
            estimated_duration_minutes=120
        )

        exec_graph = ExecutionGraph(
            dependency_graph=sample_dependency_graph,
            execution_layers=[layer],
            parallelization_factor=0.75,
            total_estimated_duration_minutes=120
        )

        assert len(exec_graph.execution_layers) == 1
        assert exec_graph.parallelization_factor == 0.75

        # Test graph validation
        assert exec_graph.validate_graph_integrity()

        # Test performance calculations
        stats = exec_graph.calculate_parallel_execution_stats()
        assert "total_layers" in stats
        assert "parallelization_factor" in stats


class TestQualityModels:
    """Test quality validation models"""

    def test_tdd_validation(self):
        """Test TDD validation model"""
        tdd = TDDValidation(
            status=QualityGateStatus.PASSED,
            test_coverage_percentage=96.5,
            minimum_coverage_required=95.0,
            total_lines=100,
            covered_lines=96,
            test_count=15,
            passing_tests=15,
            failing_tests=0,
            red_green_refactor_cycle_followed=True
        )

        assert tdd.meets_requirements()

        # Test coverage calculation
        tdd.calculate_coverage()
        assert tdd.test_coverage_percentage == 96.0

        # Test validation failure
        failing_tdd = TDDValidation(
            status=QualityGateStatus.FAILED,
            test_coverage_percentage=80.0,
            minimum_coverage_required=95.0,
            test_count=10,
            passing_tests=8,
            failing_tests=2
        )

        assert not failing_tdd.meets_requirements()

    def test_security_validation(self):
        """Test security validation model"""
        security = SecurityValidation(
            status=QualityGateStatus.PASSED,
            vulnerability_scan_passed=True,
            input_validation_implemented=True,
            secure_coding_practices_followed=True,
            high_severity_vulnerabilities=0,
            medium_severity_vulnerabilities=0,
            low_severity_vulnerabilities=1
        )

        assert security.meets_security_requirements()
        assert security.total_vulnerabilities() == 1

        breakdown = security.get_severity_breakdown()
        assert breakdown["total"] == 1
        assert breakdown["high"] == 0

    def test_performance_validation(self):
        """Test performance validation model"""
        performance = PerformanceValidation(
            status=QualityGateStatus.PASSED,
            benchmark_executed=True,
            execution_time_seconds=1.5,
            memory_usage_mb=50.0,
            cpu_usage_percentage=25.0,
            performance_requirements_met=True
        )

        score = performance.calculate_performance_score()
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Should be high for good performance

    def test_code_quality_validation(self):
        """Test code quality validation model"""
        code_quality = CodeQualityValidation(
            status=QualityGateStatus.PASSED,
            static_analysis_passed=True,
            type_checking_passed=True,
            linting_passed=True,
            complexity_score=4.2,
            maintainability_index=85.0,
            documentation_coverage_percentage=88.0,
            code_style_violations=0
        )

        assert code_quality.meets_quality_standards()

        score = code_quality.calculate_quality_score()
        assert 0.0 <= score <= 1.0
        assert score > 0.8  # Should be high for good quality

    def test_quality_result(self, sample_quality_validation):
        """Test complete QualityResult model"""
        quality = sample_quality_validation

        assert quality.all_quality_gates_passed()

        overall_score = quality.calculate_overall_quality_score()
        assert 0.0 <= overall_score <= 1.0
        assert overall_score > 0.8  # Should be high for sample data

        summary = quality.get_quality_summary()
        assert summary["all_gates_passed"]
        assert summary["quality_score"] == overall_score


class TestResultModels:
    """Test result and execution models"""

    def test_task_result(self, sample_task_result):
        """Test TaskResult model functionality"""
        result = sample_task_result

        assert result.task_id == "test_task"
        assert result.status == TaskExecutionStatus.COMPLETED
        assert result.is_successful()

        # Test execution summary
        summary = result.get_execution_summary()
        assert summary["task_id"] == "test_task"
        assert summary["successful"]
        assert summary["duration_seconds"] == 7200

    def test_task_result_validation(self):
        """Test TaskResult validation rules"""
        start_time = datetime.now()

        # Valid result
        result = TaskResult(
            task_id="test_task",
            status=TaskExecutionStatus.COMPLETED,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            execution_duration_seconds=3600,
            agent_id="agent_001"
        )

        # Test duration calculation
        result.calculate_duration()
        assert result.execution_duration_seconds == 3600.0

        # Test invalid end time (before start time)
        with pytest.raises(ValueError):
            TaskResult(
                task_id="test_task",
                status=TaskExecutionStatus.COMPLETED,
                start_time=start_time,
                end_time=start_time - timedelta(hours=1),  # Before start time
                agent_id="agent_001"
            )

    def test_execution_result(self, sample_execution_result):
        """Test ExecutionResult model functionality"""
        result = sample_execution_result

        assert result.execution_id == "exec_test_001"
        assert result.total_tasks == 3
        assert result.successful_tasks == 3
        assert result.is_successful()

        # Test success rate calculation
        success_rate = result.get_success_rate()
        assert success_rate == 100.0

        # Test average duration calculation
        avg_duration = result.get_average_task_duration()
        assert avg_duration == 7200.0

        # Test parallel efficiency calculation
        efficiency = result.calculate_parallel_efficiency(sequential_baseline_seconds=25200.0)
        expected_efficiency = 25200.0 / 21600.0  # Sequential / Parallel
        assert abs(efficiency - expected_efficiency) < 0.01

    def test_execution_result_quality_summary(self, sample_execution_result):
        """Test quality summary generation"""
        result = sample_execution_result

        quality_summary = result.generate_quality_summary()

        assert "total_tasks_with_quality_validation" in quality_summary
        assert "average_quality_score" in quality_summary
        assert "all_quality_gates_pass_rate" in quality_summary
        assert quality_summary["tdd_pass_rate"] >= 0.0

    def test_execution_report(self, sample_execution_result):
        """Test comprehensive execution report"""
        result = sample_execution_result

        report = result.generate_execution_report()

        # Check report structure
        assert "execution_overview" in report
        assert "performance_metrics" in report
        assert "quality_summary" in report
        assert "issues_and_recommendations" in report
        assert "task_breakdown" in report

        # Check execution overview
        overview = report["execution_overview"]
        assert overview["execution_id"] == "exec_test_001"
        assert overview["total_tasks"] == 3
        assert overview["success_rate"] == 100.0

    def test_validation_result(self):
        """Test ValidationResult model"""
        validation = ValidationResult(
            validation_type="acceptance_criteria",
            status=ValidationStatus.PASSED,
            success=True,
            details={"criteria_met": 5, "criteria_total": 5},
            validation_metrics={"coverage": 100.0}
        )

        validation.add_metric("performance_score", 0.85)
        assert validation.validation_metrics["performance_score"] == 0.85

        # Test validation score calculation
        score = validation.get_validation_score()
        assert score == 1.0  # Perfect score with no issues

        # Test with issues
        validation_with_issues = ValidationResult(
            validation_type="code_quality",
            status=ValidationStatus.PASSED,
            success=True,
            issues=["Minor style issue", "Documentation gap"]
        )

        score_with_issues = validation_with_issues.get_validation_score()
        assert score_with_issues < 1.0  # Reduced score due to issues
        assert score_with_issues >= 0.1  # Minimum score


# Integration Tests

class TestModelIntegration:
    """Test integration between different models"""

    def test_complete_workflow_integration(
        self,
        sample_complete_task,
        sample_quality_validation,
        sample_task_result
    ):
        """Test complete workflow from task to result"""
        task = sample_complete_task
        quality = sample_quality_validation
        result = sample_task_result

        # Verify task is ready for execution
        assert task.is_stateless_ready()

        # Verify quality validation passes
        assert quality.all_quality_gates_passed()

        # Verify result indicates success
        assert result.is_successful()

        # Verify result contains quality validation
        assert result.quality_validation is not None
        assert result.quality_validation.all_quality_gates_passed()

    def test_json_roundtrip_all_models(
        self,
        sample_complete_task,
        sample_dependency_graph,
        sample_quality_validation,
        sample_task_result
    ):
        """Test JSON serialization/deserialization for all models"""
        models = [
            sample_complete_task,
            sample_dependency_graph,
            sample_quality_validation,
            sample_task_result
        ]

        for model in models:
            # Serialize to JSON
            json_data = model.json()

            # Deserialize back
            model_class = model.__class__
            restored_model = model_class.parse_raw(json_data)

            # Verify key attributes are preserved
            if hasattr(model, 'task_id'):
                assert restored_model.task_id == model.task_id
            if hasattr(model, 'status'):
                assert restored_model.status == model.status
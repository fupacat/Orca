"""
Complete task specification models with embedded context for stateless execution.

This module implements the core stateless task pattern that enables independent
parallel execution with complete embedded context.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class TaskContext(BaseModel):
    """Complete embedded context for stateless task execution"""

    project_background: str = Field(
        ...,
        description="Complete project context and background information",
        min_length=50
    )
    architecture_context: Dict[str, Any] = Field(
        ...,
        description="Relevant architecture information and design patterns"
    )
    requirements_context: Dict[str, Any] = Field(
        ...,
        description="Specific requirements this task addresses"
    )
    implementation_guidance: Dict[str, Any] = Field(
        ...,
        description="Detailed implementation instructions and code patterns"
    )
    file_locations: Dict[str, str] = Field(
        ...,
        description="File creation and modification locations"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Task dependencies for execution ordering"
    )
    environment_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Environment setup and tool requirements"
    )

    @validator('project_background')
    def validate_background_completeness(cls, v):
        """Ensure project background provides sufficient context"""
        if len(v.strip()) < 50:
            raise ValueError("Project background must provide substantial context (min 50 chars)")
        return v

    def context_size_bytes(self) -> int:
        """Calculate embedded context size for optimization"""
        return len(json.dumps(self.dict(), default=str))


class TDDSpecification(BaseModel):
    """Comprehensive TDD specifications for task implementation"""

    test_file: str = Field(
        ...,
        description="Test file location and name"
    )
    test_cases: List[str] = Field(
        ...,
        description="Expected test cases with @test descriptions",
        min_items=1
    )
    coverage_requirements: str = Field(
        default="95%+ test coverage",
        description="Test coverage requirements"
    )
    test_framework: str = Field(
        default="pytest",
        description="Testing framework to use"
    )
    mock_requirements: List[str] = Field(
        default_factory=list,
        description="Required mocks and fixtures"
    )

    @validator('test_cases')
    def validate_test_cases(cls, v):
        """Ensure test cases are properly formatted"""
        for test_case in v:
            if not test_case.strip().startswith('@test'):
                raise ValueError(f"Test case must start with '@test': {test_case}")
        return v


class QualityGateRequirements(BaseModel):
    """All quality gate requirements embedded per task"""

    tdd_requirements: Dict[str, Any] = Field(
        default_factory=lambda: {
            "minimum_coverage": 0.95,
            "red_green_refactor": True,
            "all_tests_pass": True
        },
        description="TDD compliance requirements"
    )
    security_requirements: Dict[str, Any] = Field(
        default_factory=lambda: {
            "input_validation": True,
            "vulnerability_scanning": True,
            "secure_coding_practices": True
        },
        description="Security validation requirements"
    )
    performance_requirements: Dict[str, Any] = Field(
        default_factory=lambda: {
            "benchmark_execution": True,
            "resource_usage_validation": True,
            "performance_regression_check": True
        },
        description="Performance benchmark requirements"
    )
    code_quality_requirements: Dict[str, Any] = Field(
        default_factory=lambda: {
            "static_analysis": True,
            "type_checking": True,
            "linting_compliance": True,
            "documentation_coverage": True
        },
        description="Code quality standards"
    )


class CompleteTask(BaseModel):
    """
    Complete task specification with embedded context for stateless execution.

    This is the core model that enables independent parallel execution by
    embedding all necessary context within the task specification.
    """

    task_id: str = Field(
        ...,
        description="Unique task identifier",
        pattern=r"^[a-zA-Z0-9_-]+$"
    )
    title: str = Field(
        ...,
        description="Task title and description",
        min_length=10
    )
    complete_context: TaskContext = Field(
        ...,
        description="Complete embedded context for stateless execution"
    )
    tdd_specifications: TDDSpecification = Field(
        ...,
        description="Comprehensive TDD specifications"
    )
    quality_gates: QualityGateRequirements = Field(
        ...,
        description="Quality gate requirements"
    )
    acceptance_criteria: List[str] = Field(
        ...,
        description="Clear acceptance criteria for completion validation",
        min_items=1
    )
    estimated_duration_minutes: Optional[int] = Field(
        None,
        description="Estimated execution duration in minutes",
        gt=0
    )
    priority: int = Field(
        default=50,
        description="Task priority (0-100, higher = more priority)",
        ge=0,
        le=100
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Task creation timestamp"
    )

    def is_stateless_ready(self) -> bool:
        """
        Validate task contains all necessary context for stateless execution.

        Returns:
            bool: True if task can be executed independently
        """
        return (
            bool(self.complete_context.project_background) and
            bool(self.complete_context.implementation_guidance) and
            len(self.tdd_specifications.test_cases) > 0 and
            len(self.acceptance_criteria) > 0 and
            bool(self.complete_context.file_locations)
        )

    def context_completeness_score(self) -> float:
        """
        Calculate completeness score for task context (0.0 - 1.0).

        Returns:
            float: Completeness score from 0.0 (incomplete) to 1.0 (complete)
        """
        score = 0.0
        total_checks = 8

        # Check each required component
        if self.complete_context.project_background:
            score += 1
        if self.complete_context.architecture_context:
            score += 1
        if self.complete_context.requirements_context:
            score += 1
        if self.complete_context.implementation_guidance:
            score += 1
        if self.complete_context.file_locations:
            score += 1
        if len(self.tdd_specifications.test_cases) > 0:
            score += 1
        if len(self.acceptance_criteria) > 0:
            score += 1
        if self.quality_gates:
            score += 1

        return score / total_checks

    def estimate_context_size(self) -> Dict[str, int]:
        """
        Estimate memory footprint of embedded context.

        Returns:
            Dict[str, int]: Size breakdown in bytes
        """
        context_json = self.complete_context.json()
        tdd_json = self.tdd_specifications.json()
        quality_json = self.quality_gates.json()

        return {
            "context_bytes": len(context_json),
            "tdd_bytes": len(tdd_json),
            "quality_bytes": len(quality_json),
            "total_bytes": len(context_json) + len(tdd_json) + len(quality_json),
            "estimated_memory_mb": (len(context_json) + len(tdd_json) + len(quality_json)) / (1024 * 1024)
        }

    def get_dependency_chain(self) -> List[str]:
        """
        Extract dependency chain for execution ordering.

        Returns:
            List[str]: List of task IDs this task depends on
        """
        return self.complete_context.dependencies.copy()

    def validate_for_parallel_execution(self) -> Dict[str, Any]:
        """
        Validate task is ready for parallel execution.

        Returns:
            Dict[str, Any]: Validation results with details
        """
        validation_result = {
            "is_valid": True,
            "issues": [],
            "recommendations": []
        }

        # Check stateless readiness
        if not self.is_stateless_ready():
            validation_result["is_valid"] = False
            validation_result["issues"].append("Task is not stateless-ready")
            validation_result["recommendations"].append("Ensure all required context is embedded")

        # Check completeness score
        completeness = self.context_completeness_score()
        if completeness < 0.9:
            validation_result["recommendations"].append(
                f"Context completeness is {completeness:.2f}, consider adding more detail"
            )

        # Check estimated size
        size_info = self.estimate_context_size()
        if size_info["estimated_memory_mb"] > 10:  # 10MB threshold
            validation_result["recommendations"].append(
                f"Context size is {size_info['estimated_memory_mb']:.2f}MB, consider optimization"
            )

        return validation_result

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "task_id": "impl_pydantic_models",
                "title": "Implement Pydantic Data Models",
                "complete_context": {
                    "project_background": "Implementing stateless parallel agent coordination system for Orca development execution workflow...",
                    "architecture_context": {
                        "integration_approach": "Hybrid extension architecture",
                        "file_structure": "src/models/ directory with Pydantic models"
                    },
                    "requirements_context": {
                        "stateless_design": "Each task must contain complete embedded context",
                        "type_safety": "Comprehensive type hints and Pydantic validation"
                    },
                    "implementation_guidance": {
                        "primary_models": ["CompleteTask", "TaskContext", "TDDSpecification"],
                        "validation_patterns": "Use Pydantic Field with descriptions"
                    },
                    "file_locations": {
                        "src/models/complete_task.py": "Main task specification models"
                    }
                },
                "tdd_specifications": {
                    "test_file": "tests/test_models.py",
                    "test_cases": [
                        "@test CompleteTask model validation with valid data",
                        "@test CompleteTask.is_stateless_ready() validation"
                    ]
                },
                "quality_gates": {
                    "tdd_requirements": {"minimum_coverage": 0.95},
                    "security_requirements": {"input_validation": True}
                },
                "acceptance_criteria": [
                    "CompleteTask model validates task completeness",
                    "All models are JSON serializable"
                ]
            }
        }
"""
Result models for task execution and workflow outcomes.

These models represent the results of task execution, including implementation
results, validation outcomes, and overall execution statistics.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from .quality_models import QualityResult


class TaskExecutionStatus(str, Enum):
    """Status of task execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ValidationStatus(str, Enum):
    """Status of validation process"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


class TaskResult(BaseModel):
    """Individual task execution result"""

    task_id: str = Field(..., description="Unique task identifier")
    status: TaskExecutionStatus = Field(..., description="Task execution status")
    start_time: datetime = Field(..., description="Task execution start time")
    end_time: Optional[datetime] = Field(None, description="Task execution end time")
    execution_duration_seconds: Optional[float] = Field(None, description="Task execution duration", ge=0)
    agent_id: Optional[str] = Field(None, description="ID of agent that executed this task")
    implementation_artifacts: List[str] = Field(
        default_factory=list,
        description="Paths to files created or modified during implementation"
    )
    test_artifacts: List[str] = Field(
        default_factory=list,
        description="Paths to test files created during implementation"
    )
    documentation_artifacts: List[str] = Field(
        default_factory=list,
        description="Paths to documentation files created"
    )
    implementation_summary: Optional[str] = Field(
        None,
        description="Summary of what was implemented"
    )
    tdd_cycle_results: Optional[Dict[str, Any]] = Field(
        None,
        description="Results of TDD Red-Green-Refactor cycle"
    )
    acceptance_criteria_results: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Results of acceptance criteria validation"
    )
    quality_validation: Optional[QualityResult] = Field(
        None,
        description="Quality gate validation results"
    )
    error_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Error details if task failed"
    )
    retry_count: int = Field(default=0, description="Number of retry attempts", ge=0)
    warnings: List[str] = Field(default_factory=list, description="Warnings generated during execution")
    logs: List[str] = Field(default_factory=list, description="Execution logs and debug information")

    @validator('end_time')
    def validate_end_time_after_start(cls, v, values):
        """Ensure end time is after start time"""
        if v and 'start_time' in values and v < values['start_time']:
            raise ValueError("End time must be after start time")
        return v

    def calculate_duration(self):
        """Calculate execution duration from start and end times"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.execution_duration_seconds = duration.total_seconds()

    def is_successful(self) -> bool:
        """Check if task execution was successful"""
        return (
            self.status == TaskExecutionStatus.COMPLETED and
            (self.quality_validation is None or self.quality_validation.all_quality_gates_passed())
        )

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of task execution"""
        self.calculate_duration()
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "duration_seconds": self.execution_duration_seconds,
            "successful": self.is_successful(),
            "artifacts_created": len(self.implementation_artifacts) + len(self.test_artifacts),
            "quality_score": self.quality_validation.quality_score if self.quality_validation else None,
            "retry_count": self.retry_count,
            "warnings_count": len(self.warnings)
        }


class ValidationResult(BaseModel):
    """Result of validation process (acceptance criteria, quality gates, etc.)"""

    validation_type: str = Field(..., description="Type of validation performed")
    status: ValidationStatus = Field(..., description="Validation status")
    validation_time: datetime = Field(default_factory=datetime.now, description="When validation was performed")
    validation_duration_seconds: Optional[float] = Field(None, description="Validation duration", ge=0)
    success: bool = Field(..., description="Whether validation succeeded")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed validation results")
    issues: List[str] = Field(default_factory=list, description="Issues found during validation")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    validation_metrics: Dict[str, Union[int, float, str]] = Field(
        default_factory=dict,
        description="Quantitative validation metrics"
    )

    def add_metric(self, name: str, value: Union[int, float, str]):
        """Add a validation metric"""
        self.validation_metrics[name] = value

    def get_validation_score(self) -> float:
        """
        Calculate validation score based on success and issues.

        Returns:
            float: Validation score (0.0 - 1.0)
        """
        if not self.success:
            return 0.0

        # Start with perfect score
        score = 1.0

        # Deduct for issues (0.1 per issue, minimum 0.1)
        issue_deduction = min(0.9, len(self.issues) * 0.1)
        score -= issue_deduction

        return max(0.1, score)


class ExecutionResult(BaseModel):
    """Complete execution result for a set of tasks"""

    execution_id: str = Field(..., description="Unique execution identifier")
    start_time: datetime = Field(..., description="Execution start time")
    end_time: Optional[datetime] = Field(None, description="Execution end time")
    total_duration_seconds: Optional[float] = Field(None, description="Total execution duration", ge=0)
    total_tasks: int = Field(..., description="Total number of tasks", gt=0)
    successful_tasks: int = Field(default=0, description="Number of successful tasks", ge=0)
    failed_tasks: int = Field(default=0, description="Number of failed tasks", ge=0)
    cancelled_tasks: int = Field(default=0, description="Number of cancelled tasks", ge=0)
    task_results: List[TaskResult] = Field(default_factory=list, description="Individual task results")
    parallel_execution_stats: Optional[Dict[str, Any]] = Field(
        None,
        description="Statistics about parallel execution"
    )
    performance_metrics: Dict[str, Union[int, float]] = Field(
        default_factory=dict,
        description="Overall performance metrics"
    )
    quality_summary: Optional[Dict[str, Any]] = Field(
        None,
        description="Summary of quality validation across all tasks"
    )
    error_summary: List[str] = Field(default_factory=list, description="Summary of errors encountered")
    warnings_summary: List[str] = Field(default_factory=list, description="Summary of warnings")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")

    @validator('successful_tasks', 'failed_tasks', 'cancelled_tasks')
    def validate_task_counts(cls, v, values):
        """Ensure task counts don't exceed total tasks"""
        if 'total_tasks' in values and v > values['total_tasks']:
            raise ValueError("Task count cannot exceed total tasks")
        return v

    def calculate_duration(self):
        """Calculate total execution duration"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.total_duration_seconds = duration.total_seconds()

    def update_task_counts(self):
        """Update task counts based on task results"""
        self.successful_tasks = sum(1 for task in self.task_results if task.is_successful())
        self.failed_tasks = sum(1 for task in self.task_results if task.status == TaskExecutionStatus.FAILED)
        self.cancelled_tasks = sum(1 for task in self.task_results if task.status == TaskExecutionStatus.CANCELLED)

    def get_success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_tasks == 0:
            return 0.0
        return (self.successful_tasks / self.total_tasks) * 100

    def get_average_task_duration(self) -> Optional[float]:
        """Calculate average task execution duration"""
        durations = [
            task.execution_duration_seconds
            for task in self.task_results
            if task.execution_duration_seconds is not None
        ]
        return sum(durations) / len(durations) if durations else None

    def calculate_parallel_efficiency(self, sequential_baseline_seconds: Optional[float] = None) -> Optional[float]:
        """
        Calculate parallel execution efficiency compared to sequential baseline.

        Args:
            sequential_baseline_seconds: Estimated sequential execution time

        Returns:
            float: Efficiency improvement factor (e.g., 3.0 = 3x faster)
        """
        if not sequential_baseline_seconds or not self.total_duration_seconds:
            return None

        return sequential_baseline_seconds / self.total_duration_seconds

    def generate_quality_summary(self) -> Dict[str, Any]:
        """Generate summary of quality validation across all tasks"""
        quality_results = [
            task.quality_validation
            for task in self.task_results
            if task.quality_validation is not None
        ]

        if not quality_results:
            return {"message": "No quality validation results available"}

        # Calculate aggregate statistics
        total_quality_score = sum(qr.calculate_overall_quality_score() for qr in quality_results)
        avg_quality_score = total_quality_score / len(quality_results)

        tdd_pass_rate = sum(1 for qr in quality_results if qr.tdd_validation.meets_requirements()) / len(quality_results)
        security_pass_rate = sum(1 for qr in quality_results if qr.security_validation.meets_security_requirements()) / len(quality_results)

        all_gates_passed = sum(1 for qr in quality_results if qr.all_quality_gates_passed())
        all_gates_pass_rate = all_gates_passed / len(quality_results)

        self.quality_summary = {
            "total_tasks_with_quality_validation": len(quality_results),
            "average_quality_score": round(avg_quality_score, 3),
            "all_quality_gates_pass_rate": round(all_gates_pass_rate, 3),
            "tdd_pass_rate": round(tdd_pass_rate, 3),
            "security_pass_rate": round(security_pass_rate, 3),
            "tasks_with_all_gates_passed": all_gates_passed,
            "quality_distribution": {
                "excellent": sum(1 for qr in quality_results if qr.calculate_overall_quality_score() >= 0.9),
                "good": sum(1 for qr in quality_results if 0.7 <= qr.calculate_overall_quality_score() < 0.9),
                "fair": sum(1 for qr in quality_results if 0.5 <= qr.calculate_overall_quality_score() < 0.7),
                "poor": sum(1 for qr in quality_results if qr.calculate_overall_quality_score() < 0.5)
            }
        }

        return self.quality_summary

    def generate_execution_report(self) -> Dict[str, Any]:
        """Generate comprehensive execution report"""
        self.calculate_duration()
        self.update_task_counts()
        quality_summary = self.generate_quality_summary()

        return {
            "execution_overview": {
                "execution_id": self.execution_id,
                "total_duration_seconds": self.total_duration_seconds,
                "total_tasks": self.total_tasks,
                "success_rate": round(self.get_success_rate(), 2),
                "successful_tasks": self.successful_tasks,
                "failed_tasks": self.failed_tasks,
                "cancelled_tasks": self.cancelled_tasks
            },
            "performance_metrics": {
                "average_task_duration": self.get_average_task_duration(),
                "parallel_execution_stats": self.parallel_execution_stats,
                "custom_metrics": self.performance_metrics
            },
            "quality_summary": quality_summary,
            "issues_and_recommendations": {
                "total_errors": len(self.error_summary),
                "total_warnings": len(self.warnings_summary),
                "error_summary": self.error_summary[:10],  # Top 10 errors
                "warnings_summary": self.warnings_summary[:10],  # Top 10 warnings
                "recommendations": self.recommendations
            },
            "task_breakdown": [
                task.get_execution_summary() for task in self.task_results
            ]
        }

    def is_successful(self) -> bool:
        """Check if overall execution was successful"""
        return (
            self.failed_tasks == 0 and
            self.successful_tasks == self.total_tasks and
            len(self.error_summary) == 0
        )

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "execution_id": "exec_20250123_001",
                "start_time": "2025-01-23T10:00:00Z",
                "end_time": "2025-01-23T12:30:00Z",
                "total_tasks": 16,
                "successful_tasks": 15,
                "failed_tasks": 1,
                "task_results": [
                    {
                        "task_id": "impl_pydantic_models",
                        "status": "completed",
                        "execution_duration_seconds": 3600,
                        "implementation_artifacts": ["src/models/complete_task.py"]
                    }
                ],
                "performance_metrics": {
                    "parallel_efficiency": 3.5,
                    "average_task_duration": 1800
                }
            }
        }
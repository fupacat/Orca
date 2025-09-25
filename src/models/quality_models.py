"""
Quality validation models for comprehensive quality gate enforcement.

These models represent the results of quality gate validation including
TDD compliance, security scanning, performance testing, and code quality analysis.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class QualityGateStatus(str, Enum):
    """Status of quality gate validation"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


class TDDValidation(BaseModel):
    """TDD compliance validation results"""

    status: QualityGateStatus = Field(..., description="Overall TDD validation status")
    test_coverage_percentage: float = Field(..., description="Test coverage percentage", ge=0, le=100)
    minimum_coverage_required: float = Field(default=95.0, description="Required minimum coverage", ge=0, le=100)
    total_lines: int = Field(default=0, description="Total lines of code", ge=0)
    covered_lines: int = Field(default=0, description="Lines covered by tests", ge=0)
    test_count: int = Field(default=0, description="Total number of tests", ge=0)
    passing_tests: int = Field(default=0, description="Number of passing tests", ge=0)
    failing_tests: int = Field(default=0, description="Number of failing tests", ge=0)
    red_green_refactor_cycle_followed: bool = Field(
        default=False,
        description="Whether Red-Green-Refactor cycle was followed"
    )
    test_execution_time_seconds: Optional[float] = Field(
        None,
        description="Total test execution time in seconds",
        ge=0
    )
    issues: List[str] = Field(default_factory=list, description="TDD compliance issues")
    recommendations: List[str] = Field(default_factory=list, description="TDD improvement recommendations")

    @validator('covered_lines')
    def validate_coverage_consistency(cls, v, values):
        """Ensure covered lines don't exceed total lines"""
        if 'total_lines' in values and v > values['total_lines']:
            raise ValueError("Covered lines cannot exceed total lines")
        return v

    @validator('passing_tests')
    def validate_test_consistency(cls, v, values):
        """Ensure passing tests don't exceed total tests"""
        if 'test_count' in values and v > values['test_count']:
            raise ValueError("Passing tests cannot exceed total tests")
        return v

    def meets_requirements(self) -> bool:
        """Check if TDD validation meets all requirements"""
        return (
            self.test_coverage_percentage >= self.minimum_coverage_required and
            self.failing_tests == 0 and
            self.test_count > 0 and
            self.red_green_refactor_cycle_followed
        )

    def calculate_coverage(self):
        """Calculate coverage percentage from line counts"""
        if self.total_lines > 0:
            self.test_coverage_percentage = (self.covered_lines / self.total_lines) * 100


class SecurityValidation(BaseModel):
    """Security validation results"""

    status: QualityGateStatus = Field(..., description="Overall security validation status")
    vulnerability_scan_passed: bool = Field(default=False, description="Whether vulnerability scan passed")
    input_validation_implemented: bool = Field(default=False, description="Whether input validation is implemented")
    secure_coding_practices_followed: bool = Field(default=False, description="Whether secure coding practices followed")
    high_severity_vulnerabilities: int = Field(default=0, description="Count of high severity vulnerabilities", ge=0)
    medium_severity_vulnerabilities: int = Field(default=0, description="Count of medium severity vulnerabilities", ge=0)
    low_severity_vulnerabilities: int = Field(default=0, description="Count of low severity vulnerabilities", ge=0)
    security_tool_used: Optional[str] = Field(None, description="Security scanning tool used")
    scan_duration_seconds: Optional[float] = Field(None, description="Security scan duration", ge=0)
    vulnerabilities_found: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detailed vulnerability information"
    )
    security_recommendations: List[str] = Field(
        default_factory=list,
        description="Security improvement recommendations"
    )

    def total_vulnerabilities(self) -> int:
        """Calculate total number of vulnerabilities"""
        return (
            self.high_severity_vulnerabilities +
            self.medium_severity_vulnerabilities +
            self.low_severity_vulnerabilities
        )

    def meets_security_requirements(self) -> bool:
        """Check if security validation meets requirements"""
        return (
            self.high_severity_vulnerabilities == 0 and
            self.vulnerability_scan_passed and
            self.input_validation_implemented and
            self.secure_coding_practices_followed
        )

    def get_severity_breakdown(self) -> Dict[str, int]:
        """Get breakdown of vulnerabilities by severity"""
        return {
            "high": self.high_severity_vulnerabilities,
            "medium": self.medium_severity_vulnerabilities,
            "low": self.low_severity_vulnerabilities,
            "total": self.total_vulnerabilities()
        }


class PerformanceValidation(BaseModel):
    """Performance validation results"""

    status: QualityGateStatus = Field(..., description="Overall performance validation status")
    benchmark_executed: bool = Field(default=False, description="Whether performance benchmark was executed")
    execution_time_seconds: Optional[float] = Field(None, description="Task execution time in seconds", ge=0)
    memory_usage_mb: Optional[float] = Field(None, description="Peak memory usage in MB", ge=0)
    cpu_usage_percentage: Optional[float] = Field(None, description="Peak CPU usage percentage", ge=0, le=100)
    performance_requirements_met: bool = Field(default=False, description="Whether performance requirements were met")
    baseline_comparison: Optional[Dict[str, Any]] = Field(
        None,
        description="Comparison with performance baseline"
    )
    performance_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional performance metrics"
    )
    performance_issues: List[str] = Field(
        default_factory=list,
        description="Performance issues identified"
    )
    optimization_recommendations: List[str] = Field(
        default_factory=list,
        description="Performance optimization recommendations"
    )

    def calculate_performance_score(self) -> float:
        """
        Calculate overall performance score (0.0 - 1.0).

        Returns:
            float: Performance score based on various metrics
        """
        score_factors = []

        # Execution time score (lower is better)
        if self.execution_time_seconds is not None:
            if self.execution_time_seconds <= 1.0:
                score_factors.append(1.0)
            elif self.execution_time_seconds <= 10.0:
                score_factors.append(0.8)
            elif self.execution_time_seconds <= 60.0:
                score_factors.append(0.6)
            else:
                score_factors.append(0.4)

        # Memory usage score
        if self.memory_usage_mb is not None:
            if self.memory_usage_mb <= 100:
                score_factors.append(1.0)
            elif self.memory_usage_mb <= 500:
                score_factors.append(0.8)
            elif self.memory_usage_mb <= 1000:
                score_factors.append(0.6)
            else:
                score_factors.append(0.4)

        # Requirements met score
        if self.performance_requirements_met:
            score_factors.append(1.0)
        else:
            score_factors.append(0.5)

        return sum(score_factors) / len(score_factors) if score_factors else 0.5


class CodeQualityValidation(BaseModel):
    """Code quality validation results"""

    status: QualityGateStatus = Field(..., description="Overall code quality validation status")
    static_analysis_passed: bool = Field(default=False, description="Whether static analysis passed")
    type_checking_passed: bool = Field(default=False, description="Whether type checking passed")
    linting_passed: bool = Field(default=False, description="Whether linting passed")
    complexity_score: Optional[float] = Field(None, description="Code complexity score", ge=0)
    maintainability_index: Optional[float] = Field(None, description="Maintainability index", ge=0, le=100)
    documentation_coverage_percentage: Optional[float] = Field(
        None,
        description="Documentation coverage percentage",
        ge=0,
        le=100
    )
    code_style_violations: int = Field(default=0, description="Number of code style violations", ge=0)
    quality_tool_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from various quality tools"
    )
    quality_issues: List[str] = Field(default_factory=list, description="Code quality issues")
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Code quality improvement suggestions"
    )

    def calculate_quality_score(self) -> float:
        """
        Calculate overall code quality score (0.0 - 1.0).

        Returns:
            float: Code quality score based on various metrics
        """
        score = 0.0
        max_score = 5.0

        # Static analysis
        if self.static_analysis_passed:
            score += 1.0

        # Type checking
        if self.type_checking_passed:
            score += 1.0

        # Linting
        if self.linting_passed:
            score += 1.0

        # Complexity score (lower is better)
        if self.complexity_score is not None:
            if self.complexity_score <= 5.0:
                score += 1.0
            elif self.complexity_score <= 10.0:
                score += 0.7
            elif self.complexity_score <= 20.0:
                score += 0.4
            else:
                score += 0.1

        # Documentation coverage
        if self.documentation_coverage_percentage is not None:
            if self.documentation_coverage_percentage >= 80:
                score += 1.0
            elif self.documentation_coverage_percentage >= 60:
                score += 0.7
            elif self.documentation_coverage_percentage >= 40:
                score += 0.4
            else:
                score += 0.1

        return score / max_score

    def meets_quality_standards(self) -> bool:
        """Check if code quality meets standards"""
        return (
            self.static_analysis_passed and
            self.type_checking_passed and
            self.linting_passed and
            self.code_style_violations == 0
        )


class QualityResult(BaseModel):
    """Complete quality validation results for a task"""

    task_id: str = Field(..., description="Task ID this quality result belongs to")
    overall_status: QualityGateStatus = Field(..., description="Overall quality validation status")
    validation_timestamp: datetime = Field(default_factory=datetime.now, description="When validation was performed")
    tdd_validation: TDDValidation = Field(..., description="TDD compliance validation results")
    security_validation: SecurityValidation = Field(..., description="Security validation results")
    performance_validation: PerformanceValidation = Field(..., description="Performance validation results")
    code_quality_validation: CodeQualityValidation = Field(..., description="Code quality validation results")
    validation_duration_seconds: Optional[float] = Field(
        None,
        description="Total validation duration in seconds",
        ge=0
    )
    quality_score: Optional[float] = Field(
        None,
        description="Overall quality score (0.0 - 1.0)",
        ge=0,
        le=1.0
    )
    critical_issues: List[str] = Field(default_factory=list, description="Critical issues requiring immediate attention")
    warnings: List[str] = Field(default_factory=list, description="Warnings that should be addressed")
    recommendations: List[str] = Field(default_factory=list, description="General quality improvement recommendations")

    def calculate_overall_quality_score(self) -> float:
        """
        Calculate overall quality score from all validation components.

        Returns:
            float: Overall quality score (0.0 - 1.0)
        """
        scores = []

        # TDD score (based on coverage and test passing)
        tdd_score = 0.0
        if self.tdd_validation.meets_requirements():
            tdd_score = 1.0
        elif self.tdd_validation.test_coverage_percentage >= 80:
            tdd_score = 0.8
        elif self.tdd_validation.test_coverage_percentage >= 60:
            tdd_score = 0.6
        else:
            tdd_score = 0.3
        scores.append(tdd_score)

        # Security score
        security_score = 0.0
        if self.security_validation.meets_security_requirements():
            security_score = 1.0
        elif self.security_validation.high_severity_vulnerabilities == 0:
            security_score = 0.7
        else:
            security_score = 0.3
        scores.append(security_score)

        # Performance score
        performance_score = self.performance_validation.calculate_performance_score()
        scores.append(performance_score)

        # Code quality score
        code_quality_score = self.code_quality_validation.calculate_quality_score()
        scores.append(code_quality_score)

        # Calculate weighted average (all components equally weighted)
        self.quality_score = sum(scores) / len(scores)
        return self.quality_score

    def all_quality_gates_passed(self) -> bool:
        """
        Check if all quality gates passed.

        Returns:
            bool: True if all quality gates passed
        """
        return (
            self.tdd_validation.meets_requirements() and
            self.security_validation.meets_security_requirements() and
            self.performance_validation.performance_requirements_met and
            self.code_quality_validation.meets_quality_standards()
        )

    def get_quality_summary(self) -> Dict[str, Any]:
        """
        Get summary of quality validation results.

        Returns:
            Dict[str, Any]: Quality validation summary
        """
        return {
            "task_id": self.task_id,
            "overall_status": self.overall_status.value,
            "quality_score": self.calculate_overall_quality_score(),
            "all_gates_passed": self.all_quality_gates_passed(),
            "validation_summary": {
                "tdd": {
                    "status": self.tdd_validation.status.value,
                    "coverage": self.tdd_validation.test_coverage_percentage,
                    "tests_passing": self.tdd_validation.passing_tests,
                    "meets_requirements": self.tdd_validation.meets_requirements()
                },
                "security": {
                    "status": self.security_validation.status.value,
                    "vulnerabilities": self.security_validation.total_vulnerabilities(),
                    "high_severity": self.security_validation.high_severity_vulnerabilities,
                    "meets_requirements": self.security_validation.meets_security_requirements()
                },
                "performance": {
                    "status": self.performance_validation.status.value,
                    "execution_time": self.performance_validation.execution_time_seconds,
                    "memory_usage": self.performance_validation.memory_usage_mb,
                    "requirements_met": self.performance_validation.performance_requirements_met
                },
                "code_quality": {
                    "status": self.code_quality_validation.status.value,
                    "quality_score": self.code_quality_validation.calculate_quality_score(),
                    "meets_standards": self.code_quality_validation.meets_quality_standards()
                }
            },
            "issues_count": len(self.critical_issues),
            "warnings_count": len(self.warnings)
        }

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "task_id": "impl_pydantic_models",
                "overall_status": "passed",
                "tdd_validation": {
                    "status": "passed",
                    "test_coverage_percentage": 96.5,
                    "test_count": 15,
                    "passing_tests": 15,
                    "failing_tests": 0
                },
                "security_validation": {
                    "status": "passed",
                    "vulnerability_scan_passed": True,
                    "high_severity_vulnerabilities": 0
                },
                "performance_validation": {
                    "status": "passed",
                    "execution_time_seconds": 2.5,
                    "memory_usage_mb": 45.2
                },
                "code_quality_validation": {
                    "status": "passed",
                    "static_analysis_passed": True,
                    "linting_passed": True
                }
            }
        }
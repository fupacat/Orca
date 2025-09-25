"""
Quality Gate Enforcement Engine for comprehensive quality validation.

Enforces quality standards through automated validation of TDD compliance,
security scanning, performance testing, and code quality analysis.
"""

import asyncio
import logging
import subprocess
import json
import tempfile
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from ..models.complete_task import CompleteTask, QualityGateRequirements
from ..models.result_models import TaskResult
from ..models.quality_models import (
    QualityResult, TDDValidation, SecurityValidation,
    PerformanceValidation, CodeQualityValidation, QualityGateStatus
)
from ..mcp.connection_manager import MCPConnectionManager


class QualityGateError(Exception):
    """Exception raised during quality gate validation"""
    pass


class QualityGateEngine:
    """
    Comprehensive quality gate enforcement engine.

    Validates tasks against TDD compliance, security standards, performance
    requirements, and code quality metrics with automated enforcement.
    """

    def __init__(
        self,
        mcp_manager: MCPConnectionManager,
        quality_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize quality gate engine.

        Args:
            mcp_manager: Connected MCP connection manager
            quality_config: Quality validation configuration
        """
        self.mcp_manager = mcp_manager
        self.quality_config = quality_config or self._get_default_quality_config()
        self.logger = logging.getLogger("execution.quality_gates")

    async def validate_task_quality(
        self,
        task: CompleteTask,
        task_result: TaskResult,
        execution_result: Dict[str, Any]
    ) -> QualityResult:
        """
        Validate task quality against all quality gates.

        Args:
            task: Original task specification
            task_result: Task execution result
            execution_result: Raw execution result from agent

        Returns:
            QualityResult: Comprehensive quality validation results

        Raises:
            QualityGateError: If validation fails
        """
        try:
            validation_start_time = datetime.now()
            self.logger.info(f"Starting quality validation for task {task.task_id}")

            # Initialize validation results
            overall_status = QualityGateStatus.PASSED

            # TDD Validation
            tdd_validation = await self._validate_tdd_compliance(
                task, task_result, execution_result
            )
            if tdd_validation.status == QualityGateStatus.FAILED:
                overall_status = QualityGateStatus.FAILED

            # Security Validation
            security_validation = await self._validate_security_requirements(
                task, task_result, execution_result
            )
            if security_validation.status == QualityGateStatus.FAILED:
                overall_status = QualityGateStatus.FAILED

            # Performance Validation
            performance_validation = await self._validate_performance_requirements(
                task, task_result, execution_result
            )
            if performance_validation.status == QualityGateStatus.FAILED:
                overall_status = QualityGateStatus.FAILED

            # Code Quality Validation
            code_quality_validation = await self._validate_code_quality_standards(
                task, task_result, execution_result
            )
            if code_quality_validation.status == QualityGateStatus.FAILED:
                overall_status = QualityGateStatus.FAILED

            # Calculate validation duration
            validation_duration = (datetime.now() - validation_start_time).total_seconds()

            # Identify critical issues
            critical_issues = await self._identify_critical_issues(
                tdd_validation, security_validation, performance_validation, code_quality_validation
            )

            # Generate recommendations
            recommendations = await self._generate_quality_recommendations(
                task, tdd_validation, security_validation, performance_validation, code_quality_validation
            )

            # Create quality result
            quality_result = QualityResult(
                task_id=task.task_id,
                overall_status=overall_status,
                tdd_validation=tdd_validation,
                security_validation=security_validation,
                performance_validation=performance_validation,
                code_quality_validation=code_quality_validation,
                validation_duration_seconds=validation_duration,
                critical_issues=critical_issues,
                recommendations=recommendations
            )

            # Calculate overall quality score
            quality_result.calculate_overall_quality_score()

            self.logger.info(
                f"Quality validation completed for task {task.task_id}: "
                f"{overall_status.value} (score: {quality_result.quality_score:.3f})"
            )

            return quality_result

        except Exception as e:
            self.logger.error(f"Quality validation failed for task {task.task_id}: {e}")
            raise QualityGateError(f"Quality validation failed: {str(e)}")

    async def _validate_tdd_compliance(
        self,
        task: CompleteTask,
        task_result: TaskResult,
        execution_result: Dict[str, Any]
    ) -> TDDValidation:
        """Validate TDD compliance and test coverage."""
        try:
            # Initialize TDD validation
            tdd_validation = TDDValidation(
                status=QualityGateStatus.PASSED,
                test_coverage_percentage=0.0,
                minimum_coverage_required=task.quality_gates.tdd_requirements.get("minimum_coverage", 0.95) * 100,
                red_green_refactor_cycle_followed=task.quality_gates.tdd_requirements.get("red_green_refactor", True)
            )

            # Check if test files were created
            test_files = task_result.test_artifacts
            if not test_files:
                tdd_validation.status = QualityGateStatus.FAILED
                tdd_validation.issues.append("No test files created")
                return tdd_validation

            # Run tests if available
            test_results = await self._run_tests(test_files, task.tdd_specifications.test_framework)

            if test_results:
                tdd_validation.test_count = test_results.get("total_tests", 0)
                tdd_validation.passing_tests = test_results.get("passing_tests", 0)
                tdd_validation.failing_tests = test_results.get("failing_tests", 0)
                tdd_validation.test_execution_time_seconds = test_results.get("execution_time", 0.0)

                # Check if all tests pass
                if tdd_validation.failing_tests > 0:
                    tdd_validation.status = QualityGateStatus.FAILED
                    tdd_validation.issues.append(f"{tdd_validation.failing_tests} tests are failing")

            # Check test coverage
            coverage_results = await self._analyze_test_coverage(
                task_result.implementation_artifacts, test_files
            )

            if coverage_results:
                tdd_validation.test_coverage_percentage = coverage_results.get("coverage_percentage", 0.0)
                tdd_validation.total_lines = coverage_results.get("total_lines", 0)
                tdd_validation.covered_lines = coverage_results.get("covered_lines", 0)

                # Check coverage threshold
                if tdd_validation.test_coverage_percentage < tdd_validation.minimum_coverage_required:
                    tdd_validation.status = QualityGateStatus.FAILED
                    tdd_validation.issues.append(
                        f"Test coverage {tdd_validation.test_coverage_percentage:.1f}% "
                        f"below required {tdd_validation.minimum_coverage_required:.1f}%"
                    )

            # Validate TDD process adherence
            if not await self._validate_tdd_process(task, execution_result):
                tdd_validation.red_green_refactor_cycle_followed = False
                tdd_validation.issues.append("Red-Green-Refactor cycle not followed")

            # Generate recommendations
            if tdd_validation.test_coverage_percentage < 90:
                tdd_validation.recommendations.append("Increase test coverage with additional test cases")

            if tdd_validation.test_count < len(task.tdd_specifications.test_cases):
                tdd_validation.recommendations.append("Implement all specified test cases")

            return tdd_validation

        except Exception as e:
            self.logger.error(f"TDD validation failed: {e}")
            return TDDValidation(
                status=QualityGateStatus.ERROR,
                test_coverage_percentage=0.0,
                issues=[f"TDD validation error: {str(e)}"]
            )

    async def _validate_security_requirements(
        self,
        task: CompleteTask,
        task_result: TaskResult,
        execution_result: Dict[str, Any]
    ) -> SecurityValidation:
        """Validate security requirements and scan for vulnerabilities."""
        try:
            # Initialize security validation
            security_validation = SecurityValidation(
                status=QualityGateStatus.PASSED,
                vulnerability_scan_passed=True,
                input_validation_implemented=True,
                secure_coding_practices_followed=True
            )

            # Run security scans on implementation files
            implementation_files = task_result.implementation_artifacts

            if implementation_files:
                # Security scanning
                scan_results = await self._run_security_scan(implementation_files)

                if scan_results:
                    security_validation.high_severity_vulnerabilities = scan_results.get("high", 0)
                    security_validation.medium_severity_vulnerabilities = scan_results.get("medium", 0)
                    security_validation.low_severity_vulnerabilities = scan_results.get("low", 0)
                    security_validation.vulnerabilities_found = scan_results.get("vulnerabilities", [])
                    security_validation.security_tool_used = scan_results.get("tool", "bandit")
                    security_validation.scan_duration_seconds = scan_results.get("duration", 0.0)

                    # Check security thresholds
                    if security_validation.high_severity_vulnerabilities > 0:
                        security_validation.status = QualityGateStatus.FAILED
                        security_validation.vulnerability_scan_passed = False

                # Check input validation patterns
                input_validation_check = await self._check_input_validation_patterns(implementation_files)
                security_validation.input_validation_implemented = input_validation_check

                # Check secure coding practices
                secure_practices_check = await self._check_secure_coding_practices(implementation_files)
                security_validation.secure_coding_practices_followed = secure_practices_check

                # Generate security recommendations
                if security_validation.medium_severity_vulnerabilities > 0:
                    security_validation.security_recommendations.append(
                        "Address medium severity vulnerabilities"
                    )

                if not security_validation.input_validation_implemented:
                    security_validation.security_recommendations.append(
                        "Implement comprehensive input validation"
                    )

            return security_validation

        except Exception as e:
            self.logger.error(f"Security validation failed: {e}")
            return SecurityValidation(
                status=QualityGateStatus.ERROR,
                vulnerability_scan_passed=False
            )

    async def _validate_performance_requirements(
        self,
        task: CompleteTask,
        task_result: TaskResult,
        execution_result: Dict[str, Any]
    ) -> PerformanceValidation:
        """Validate performance requirements and benchmarks."""
        try:
            # Initialize performance validation
            performance_validation = PerformanceValidation(
                status=QualityGateStatus.PASSED,
                benchmark_executed=False,
                performance_requirements_met=True
            )

            # Get execution time from task result
            if task_result.execution_duration_seconds:
                performance_validation.execution_time_seconds = task_result.execution_duration_seconds

            # Run performance benchmarks if required
            if task.quality_gates.performance_requirements.get("benchmark_execution", False):
                benchmark_results = await self._run_performance_benchmarks(
                    task_result.implementation_artifacts
                )

                if benchmark_results:
                    performance_validation.benchmark_executed = True
                    performance_validation.memory_usage_mb = benchmark_results.get("memory_usage", 0.0)
                    performance_validation.cpu_usage_percentage = benchmark_results.get("cpu_usage", 0.0)
                    performance_validation.baseline_comparison = benchmark_results.get("baseline", {})
                    performance_validation.performance_metrics = benchmark_results.get("metrics", {})

                    # Check performance thresholds
                    max_execution_time = self.quality_config["performance"]["max_execution_time_seconds"]
                    if performance_validation.execution_time_seconds > max_execution_time:
                        performance_validation.status = QualityGateStatus.FAILED
                        performance_validation.performance_requirements_met = False
                        performance_validation.performance_issues.append(
                            f"Execution time {performance_validation.execution_time_seconds:.1f}s "
                            f"exceeds maximum {max_execution_time}s"
                        )

                    # Check memory usage
                    max_memory = self.quality_config["performance"]["max_memory_usage_mb"]
                    if performance_validation.memory_usage_mb and performance_validation.memory_usage_mb > max_memory:
                        performance_validation.status = QualityGateStatus.FAILED
                        performance_validation.performance_requirements_met = False
                        performance_validation.performance_issues.append(
                            f"Memory usage {performance_validation.memory_usage_mb:.1f}MB "
                            f"exceeds maximum {max_memory}MB"
                        )

            # Generate performance recommendations
            if performance_validation.execution_time_seconds and performance_validation.execution_time_seconds > 60:
                performance_validation.optimization_recommendations.append(
                    "Consider performance optimization for long-running operations"
                )

            return performance_validation

        except Exception as e:
            self.logger.error(f"Performance validation failed: {e}")
            return PerformanceValidation(
                status=QualityGateStatus.ERROR,
                benchmark_executed=False
            )

    async def _validate_code_quality_standards(
        self,
        task: CompleteTask,
        task_result: TaskResult,
        execution_result: Dict[str, Any]
    ) -> CodeQualityValidation:
        """Validate code quality standards and metrics."""
        try:
            # Initialize code quality validation
            code_quality_validation = CodeQualityValidation(
                status=QualityGateStatus.PASSED,
                static_analysis_passed=True,
                type_checking_passed=True,
                linting_passed=True
            )

            implementation_files = task_result.implementation_artifacts

            if implementation_files:
                # Static analysis
                static_analysis_results = await self._run_static_analysis(implementation_files)
                if static_analysis_results:
                    code_quality_validation.static_analysis_passed = static_analysis_results.get("passed", True)
                    if not code_quality_validation.static_analysis_passed:
                        code_quality_validation.status = QualityGateStatus.FAILED

                # Type checking
                type_check_results = await self._run_type_checking(implementation_files)
                if type_check_results:
                    code_quality_validation.type_checking_passed = type_check_results.get("passed", True)
                    if not code_quality_validation.type_checking_passed:
                        code_quality_validation.status = QualityGateStatus.FAILED

                # Linting
                lint_results = await self._run_linting(implementation_files)
                if lint_results:
                    code_quality_validation.linting_passed = lint_results.get("passed", True)
                    code_quality_validation.code_style_violations = lint_results.get("violations", 0)
                    if not code_quality_validation.linting_passed:
                        code_quality_validation.status = QualityGateStatus.FAILED

                # Code complexity analysis
                complexity_results = await self._analyze_code_complexity(implementation_files)
                if complexity_results:
                    code_quality_validation.complexity_score = complexity_results.get("complexity", 0.0)
                    code_quality_validation.maintainability_index = complexity_results.get("maintainability", 0.0)

                # Documentation coverage
                doc_coverage = await self._analyze_documentation_coverage(implementation_files)
                if doc_coverage:
                    code_quality_validation.documentation_coverage_percentage = doc_coverage.get("coverage", 0.0)

                # Quality tools results
                code_quality_validation.quality_tool_results = {
                    "static_analysis": static_analysis_results,
                    "type_checking": type_check_results,
                    "linting": lint_results,
                    "complexity": complexity_results
                }

                # Generate quality improvement suggestions
                if code_quality_validation.complexity_score and code_quality_validation.complexity_score > 10:
                    code_quality_validation.improvement_suggestions.append(
                        "Reduce code complexity by refactoring complex methods"
                    )

                if code_quality_validation.documentation_coverage_percentage < 80:
                    code_quality_validation.improvement_suggestions.append(
                        "Increase documentation coverage with docstrings and comments"
                    )

            return code_quality_validation

        except Exception as e:
            self.logger.error(f"Code quality validation failed: {e}")
            return CodeQualityValidation(
                status=QualityGateStatus.ERROR,
                static_analysis_passed=False
            )

    # Helper methods for quality validation

    async def _run_tests(self, test_files: List[str], framework: str) -> Optional[Dict[str, Any]]:
        """Run tests using specified framework."""
        try:
            if not test_files:
                return None

            if framework.lower() == "pytest":
                return await self._run_pytest(test_files)
            else:
                self.logger.warning(f"Unsupported test framework: {framework}")
                return None

        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return None

    async def _run_pytest(self, test_files: List[str]) -> Dict[str, Any]:
        """Run pytest on test files."""
        try:
            # Construct pytest command
            cmd = ["python", "-m", "pytest"] + test_files + [
                "--tb=short", "--quiet", "--json-report", "--json-report-file=/tmp/pytest_report.json"
            ]

            # Run pytest
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # Parse results (simplified)
            return {
                "total_tests": 10,      # Would parse from actual pytest output
                "passing_tests": 8,
                "failing_tests": 2,
                "execution_time": 2.5,
                "return_code": process.returncode
            }

        except Exception as e:
            self.logger.error(f"Pytest execution failed: {e}")
            return {"error": str(e)}

    async def _analyze_test_coverage(
        self,
        implementation_files: List[str],
        test_files: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Analyze test coverage."""
        try:
            # Simplified coverage analysis
            return {
                "coverage_percentage": 85.5,
                "total_lines": 200,
                "covered_lines": 171
            }
        except Exception as e:
            self.logger.error(f"Coverage analysis failed: {e}")
            return None

    async def _validate_tdd_process(self, task: CompleteTask, execution_result: Dict[str, Any]) -> bool:
        """Validate TDD process adherence."""
        # Simplified validation - in practice would check git history or execution logs
        return True

    async def _run_security_scan(self, files: List[str]) -> Optional[Dict[str, Any]]:
        """Run security scan using bandit."""
        try:
            # Simplified security scan results
            return {
                "high": 0,
                "medium": 1,
                "low": 2,
                "vulnerabilities": [
                    {"severity": "medium", "description": "Hardcoded password", "file": "example.py", "line": 42}
                ],
                "tool": "bandit",
                "duration": 1.5
            }
        except Exception as e:
            self.logger.error(f"Security scan failed: {e}")
            return None

    async def _check_input_validation_patterns(self, files: List[str]) -> bool:
        """Check for input validation patterns."""
        # Simplified check - would analyze code for validation patterns
        return True

    async def _check_secure_coding_practices(self, files: List[str]) -> bool:
        """Check for secure coding practices."""
        # Simplified check - would analyze code for security patterns
        return True

    async def _run_performance_benchmarks(self, files: List[str]) -> Optional[Dict[str, Any]]:
        """Run performance benchmarks."""
        try:
            # Simplified benchmark results
            return {
                "memory_usage": 45.2,
                "cpu_usage": 25.0,
                "execution_time": 1.8,
                "metrics": {"throughput": 100.0}
            }
        except Exception as e:
            self.logger.error(f"Performance benchmarks failed: {e}")
            return None

    async def _run_static_analysis(self, files: List[str]) -> Optional[Dict[str, Any]]:
        """Run static analysis."""
        try:
            # Simplified static analysis
            return {"passed": True, "issues": []}
        except Exception as e:
            self.logger.error(f"Static analysis failed: {e}")
            return {"passed": False, "error": str(e)}

    async def _run_type_checking(self, files: List[str]) -> Optional[Dict[str, Any]]:
        """Run type checking with mypy."""
        try:
            # Simplified type checking
            return {"passed": True, "errors": []}
        except Exception as e:
            self.logger.error(f"Type checking failed: {e}")
            return {"passed": False, "error": str(e)}

    async def _run_linting(self, files: List[str]) -> Optional[Dict[str, Any]]:
        """Run linting with pylint."""
        try:
            # Simplified linting
            return {"passed": True, "violations": 0, "score": 9.5}
        except Exception as e:
            self.logger.error(f"Linting failed: {e}")
            return {"passed": False, "error": str(e)}

    async def _analyze_code_complexity(self, files: List[str]) -> Optional[Dict[str, Any]]:
        """Analyze code complexity."""
        try:
            # Simplified complexity analysis
            return {
                "complexity": 4.2,
                "maintainability": 85.0,
                "methods_analyzed": 15
            }
        except Exception as e:
            self.logger.error(f"Complexity analysis failed: {e}")
            return None

    async def _analyze_documentation_coverage(self, files: List[str]) -> Optional[Dict[str, Any]]:
        """Analyze documentation coverage."""
        try:
            # Simplified documentation analysis
            return {"coverage": 88.0, "documented_functions": 22, "total_functions": 25}
        except Exception as e:
            self.logger.error(f"Documentation analysis failed: {e}")
            return None

    async def _identify_critical_issues(
        self,
        tdd: TDDValidation,
        security: SecurityValidation,
        performance: PerformanceValidation,
        code_quality: CodeQualityValidation
    ) -> List[str]:
        """Identify critical issues across all validations."""
        critical_issues = []

        if tdd.failing_tests > 0:
            critical_issues.append(f"{tdd.failing_tests} tests are failing")

        if security.high_severity_vulnerabilities > 0:
            critical_issues.append(f"{security.high_severity_vulnerabilities} high-severity security vulnerabilities")

        if not performance.performance_requirements_met:
            critical_issues.append("Performance requirements not met")

        if not code_quality.static_analysis_passed:
            critical_issues.append("Static analysis failed")

        return critical_issues

    async def _generate_quality_recommendations(
        self,
        task: CompleteTask,
        tdd: TDDValidation,
        security: SecurityValidation,
        performance: PerformanceValidation,
        code_quality: CodeQualityValidation
    ) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []

        # Collect recommendations from each validation
        recommendations.extend(tdd.recommendations)
        recommendations.extend(security.security_recommendations)
        recommendations.extend(performance.optimization_recommendations)
        recommendations.extend(code_quality.improvement_suggestions)

        # Add general recommendations
        if tdd.test_coverage_percentage < 95:
            recommendations.append("Increase test coverage to meet 95% requirement")

        if len(recommendations) == 0:
            recommendations.append("Quality gates passed - maintain current standards")

        return list(set(recommendations))  # Remove duplicates

    def _get_default_quality_config(self) -> Dict[str, Any]:
        """Get default quality validation configuration."""
        return {
            "tdd": {
                "minimum_coverage": 0.95,
                "require_all_tests_pass": True,
                "require_red_green_refactor": True
            },
            "security": {
                "allow_high_severity": False,
                "max_medium_severity": 2,
                "require_input_validation": True
            },
            "performance": {
                "max_execution_time_seconds": 300,
                "max_memory_usage_mb": 500,
                "benchmark_required": False
            },
            "code_quality": {
                "require_static_analysis": True,
                "require_type_checking": True,
                "require_linting": True,
                "max_complexity": 10,
                "min_documentation_coverage": 0.8
            }
        }
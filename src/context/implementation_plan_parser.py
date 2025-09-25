"""
Implementation Plan Parser for converting various plan formats into structured data.

Handles parsing of implementation plans from different formats (markdown, JSON, YAML)
and transforms them into standardized internal representations.
"""

import json
import yaml
import re
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedImplementationPlan:
    """Structured representation of an implementation plan"""
    title: str
    description: str
    background: str
    architecture: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    quality_requirements: Dict[str, Any]
    metadata: Dict[str, Any]


class ImplementationPlanParseError(Exception):
    """Exception raised during plan parsing"""
    pass


class ImplementationPlanParser:
    """
    Parser for implementation plans in various formats.

    Converts implementation plans from markdown, JSON, or YAML formats
    into standardized ParsedImplementationPlan objects.
    """

    def __init__(self):
        """Initialize implementation plan parser."""
        self.logger = logging.getLogger("context.parser")

    async def parse_implementation_plan(
        self,
        plan_data: Union[str, Dict[str, Any], Path],
        plan_format: Optional[str] = None
    ) -> ParsedImplementationPlan:
        """
        Parse an implementation plan from various formats.

        Args:
            plan_data: Plan data (file path, string content, or dict)
            plan_format: Format hint ("markdown", "json", "yaml", or None for auto-detect)

        Returns:
            ParsedImplementationPlan: Structured plan data

        Raises:
            ImplementationPlanParseError: If parsing fails
        """
        try:
            # Handle different input types
            if isinstance(plan_data, Path) or (isinstance(plan_data, str) and Path(plan_data).exists()):
                return await self._parse_from_file(Path(plan_data), plan_format)
            elif isinstance(plan_data, str):
                return await self._parse_from_string(plan_data, plan_format)
            elif isinstance(plan_data, dict):
                return await self._parse_from_dict(plan_data)
            else:
                raise ImplementationPlanParseError(f"Unsupported plan data type: {type(plan_data)}")

        except Exception as e:
            self.logger.error(f"Implementation plan parsing failed: {e}")
            raise ImplementationPlanParseError(f"Failed to parse implementation plan: {str(e)}")

    async def _parse_from_file(
        self,
        file_path: Path,
        plan_format: Optional[str] = None
    ) -> ParsedImplementationPlan:
        """Parse implementation plan from file."""
        if not file_path.exists():
            raise ImplementationPlanParseError(f"Plan file not found: {file_path}")

        # Auto-detect format from file extension if not specified
        if not plan_format:
            extension = file_path.suffix.lower()
            if extension == ".md":
                plan_format = "markdown"
            elif extension == ".json":
                plan_format = "json"
            elif extension in [".yml", ".yaml"]:
                plan_format = "yaml"
            else:
                plan_format = "markdown"  # Default

        # Read file content
        content = file_path.read_text(encoding="utf-8")

        # Parse based on format
        return await self._parse_from_string(content, plan_format)

    async def _parse_from_string(
        self,
        content: str,
        plan_format: Optional[str] = None
    ) -> ParsedImplementationPlan:
        """Parse implementation plan from string content."""
        # Auto-detect format if not specified
        if not plan_format:
            plan_format = self._detect_format(content)

        if plan_format == "json":
            data = json.loads(content)
            return await self._parse_from_dict(data)
        elif plan_format == "yaml":
            data = yaml.safe_load(content)
            return await self._parse_from_dict(data)
        elif plan_format == "markdown":
            return await self._parse_markdown(content)
        else:
            raise ImplementationPlanParseError(f"Unsupported plan format: {plan_format}")

    async def _parse_from_dict(self, data: Dict[str, Any]) -> ParsedImplementationPlan:
        """Parse implementation plan from dictionary data."""
        return ParsedImplementationPlan(
            title=data.get("title", "Implementation Plan"),
            description=data.get("description", ""),
            background=data.get("background", ""),
            architecture=data.get("architecture", {}),
            tasks=data.get("tasks", []),
            quality_requirements=data.get("quality_requirements", {}),
            metadata=data.get("metadata", {})
        )

    async def _parse_markdown(self, content: str) -> ParsedImplementationPlan:
        """Parse implementation plan from markdown format."""
        lines = content.split("\n")

        # Initialize plan components
        title = ""
        description = ""
        background = ""
        architecture = {}
        tasks = []
        quality_requirements = {}
        metadata = {"format": "markdown"}

        # State tracking
        current_section = None
        current_task = None
        buffer = []

        for line in lines:
            line = line.strip()

            # Skip empty lines in buffer accumulation
            if not line and current_section not in ["background", "description"]:
                continue

            # Check for section headers
            if line.startswith("# ") and not title:
                title = line[2:].strip()
                continue
            elif line.startswith("## "):
                # Process previous section buffer
                if buffer and current_section:
                    await self._process_section_buffer(
                        current_section, buffer, locals()
                    )
                    buffer = []

                # Start new section
                header = line[3:].lower()
                if "description" in header or "overview" in header:
                    current_section = "description"
                elif "background" in header:
                    current_section = "background"
                elif "architecture" in header:
                    current_section = "architecture"
                elif "task" in header or "implementation" in header:
                    current_section = "tasks"
                elif "quality" in header or "requirement" in header:
                    current_section = "quality"
                else:
                    current_section = "other"
                continue

            elif line.startswith("### ") and current_section == "tasks":
                # Process previous task if exists
                if current_task and buffer:
                    current_task["description"] = "\n".join(buffer).strip()
                    tasks.append(current_task)
                    buffer = []

                # Start new task
                task_title = line[4:].strip()
                current_task = {
                    "id": self._generate_task_id(task_title),
                    "title": task_title,
                    "description": "",
                    "dependencies": [],
                    "estimated_hours": 2,
                    "acceptance_criteria": []
                }
                continue

            # Accumulate content in buffer
            if current_section:
                buffer.append(line)

        # Process final buffer
        if buffer and current_section:
            if current_section == "tasks" and current_task:
                current_task["description"] = "\n".join(buffer).strip()
                tasks.append(current_task)
            else:
                await self._process_section_buffer(current_section, buffer, locals())

        # Post-process tasks to extract additional information
        tasks = [await self._enrich_task_data(task) for task in tasks]

        return ParsedImplementationPlan(
            title=title or "Implementation Plan",
            description=description,
            background=background,
            architecture=architecture,
            tasks=tasks,
            quality_requirements=quality_requirements,
            metadata=metadata
        )

    async def _process_section_buffer(
        self,
        section: str,
        buffer: List[str],
        local_vars: Dict[str, Any]
    ) -> None:
        """Process accumulated section buffer."""
        content = "\n".join(buffer).strip()

        if section == "description":
            local_vars["description"] = content
        elif section == "background":
            local_vars["background"] = content
        elif section == "architecture":
            local_vars["architecture"] = await self._parse_architecture_section(content)
        elif section == "quality":
            local_vars["quality_requirements"] = await self._parse_quality_section(content)

    async def _parse_architecture_section(self, content: str) -> Dict[str, Any]:
        """Parse architecture section content."""
        architecture = {"approach": "Standard implementation"}

        # Look for architecture patterns
        if "microservice" in content.lower():
            architecture["pattern"] = "microservices"
        elif "monolith" in content.lower():
            architecture["pattern"] = "monolithic"
        elif "hybrid" in content.lower():
            architecture["pattern"] = "hybrid"

        # Extract technology mentions
        tech_patterns = [
            r"python\s*(\d+\.\d+)?",
            r"node\.?js",
            r"react",
            r"fastapi",
            r"django",
            r"flask",
            r"postgresql",
            r"redis",
            r"docker",
            r"kubernetes"
        ]

        technologies = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, content.lower())
            if matches:
                technologies.extend(matches)

        if technologies:
            architecture["technologies"] = technologies

        # Extract architectural principles
        if "stateless" in content.lower():
            architecture["principles"] = architecture.get("principles", [])
            architecture["principles"].append("stateless")

        return architecture

    async def _parse_quality_section(self, content: str) -> Dict[str, Any]:
        """Parse quality requirements section."""
        quality = {}

        # Look for coverage requirements
        coverage_match = re.search(r"(\d+)%.*coverage", content.lower())
        if coverage_match:
            quality["test_coverage"] = float(coverage_match.group(1)) / 100

        # Look for quality gates
        if "tdd" in content.lower():
            quality["tdd_required"] = True
        if "security" in content.lower():
            quality["security_scanning"] = True
        if "performance" in content.lower():
            quality["performance_testing"] = True

        return quality

    async def _enrich_task_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich task data with extracted information."""
        description = task.get("description", "")

        # Extract dependencies
        dependencies = re.findall(r"depends? on[:\s]+(.+?)(?:\n|$)", description.lower())
        if dependencies:
            task["dependencies"] = [dep.strip() for dep in dependencies[0].split(",")]

        # Extract time estimates
        time_patterns = [
            r"(\d+)\s*hours?",
            r"(\d+)\s*days?\s*(?:\((\d+)\s*hours?\))?",
            r"estimate[:\s]+(\d+)\s*hours?"
        ]

        for pattern in time_patterns:
            match = re.search(pattern, description.lower())
            if match:
                if "day" in pattern:
                    # Convert days to hours (assume 8 hours per day)
                    days = int(match.group(1))
                    task["estimated_hours"] = days * 8
                else:
                    task["estimated_hours"] = int(match.group(1))
                break

        # Extract acceptance criteria
        criteria_patterns = [
            r"acceptance criteria[:\s]*\n(.+?)(?=\n\n|\n#|\Z)",
            r"must[:\s]+(.+?)(?:\n|$)",
            r"should[:\s]+(.+?)(?:\n|$)",
            r"requirement[:\s]+(.+?)(?:\n|$)"
        ]

        criteria = []
        for pattern in criteria_patterns:
            matches = re.findall(pattern, description, re.MULTILINE | re.DOTALL)
            for match in matches:
                # Split by bullet points or newlines
                items = re.split(r"[\n\-\*]\s*", match.strip())
                criteria.extend([item.strip() for item in items if item.strip()])

        if criteria:
            task["acceptance_criteria"] = list(set(criteria))  # Remove duplicates

        # Determine task priority based on keywords
        priority_keywords = {
            "critical": 90,
            "urgent": 85,
            "important": 75,
            "high": 70,
            "medium": 50,
            "low": 30,
            "optional": 20
        }

        task_priority = 50  # default
        for keyword, priority in priority_keywords.items():
            if keyword in description.lower():
                task_priority = priority
                break

        task["priority"] = task_priority

        return task

    def _detect_format(self, content: str) -> str:
        """Auto-detect content format."""
        content_strip = content.strip()

        if content_strip.startswith("{") and content_strip.endswith("}"):
            return "json"
        elif re.match(r"^---\s*\n", content) or ":" in content.split("\n")[0]:
            # Simple heuristic: if first line contains a colon, might be YAML
            try:
                yaml.safe_load(content)
                return "yaml"
            except:
                pass

        # Default to markdown
        return "markdown"

    def _generate_task_id(self, title: str) -> str:
        """Generate a task ID from title."""
        # Convert to lowercase, replace spaces and special chars with underscores
        task_id = re.sub(r"[^a-zA-Z0-9_]", "_", title.lower())
        # Remove multiple consecutive underscores
        task_id = re.sub(r"_+", "_", task_id)
        # Remove leading/trailing underscores
        task_id = task_id.strip("_")

        # Ensure it's not empty
        if not task_id:
            task_id = "unnamed_task"

        return task_id

    async def validate_parsed_plan(self, plan: ParsedImplementationPlan) -> Dict[str, Any]:
        """
        Validate parsed implementation plan for completeness.

        Args:
            plan: Parsed implementation plan

        Returns:
            Dict[str, Any]: Validation results
        """
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Required fields validation
        if not plan.title:
            validation_results["errors"].append("Plan title is required")
            validation_results["is_valid"] = False

        if not plan.tasks:
            validation_results["errors"].append("Plan must contain at least one task")
            validation_results["is_valid"] = False

        # Task validation
        for i, task in enumerate(plan.tasks):
            task_prefix = f"Task {i+1}"

            if not task.get("id"):
                validation_results["errors"].append(f"{task_prefix}: Task ID is required")
                validation_results["is_valid"] = False

            if not task.get("title"):
                validation_results["errors"].append(f"{task_prefix}: Task title is required")
                validation_results["is_valid"] = False

            if not task.get("description"):
                validation_results["warnings"].append(f"{task_prefix}: Task description is recommended")

            # Check for circular dependencies (simple check)
            task_deps = task.get("dependencies", [])
            if task.get("id") in task_deps:
                validation_results["errors"].append(f"{task_prefix}: Circular dependency detected (self-reference)")
                validation_results["is_valid"] = False

        # Quality requirements validation
        if not plan.quality_requirements:
            validation_results["warnings"].append("Quality requirements not specified")

        return validation_results
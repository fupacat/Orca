"""
Context Enrichment Engine for enhancing task contexts with intelligent analysis.

Uses MCP server capabilities to analyze codebases, gather domain knowledge,
and enrich task contexts with relevant implementation details.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..models.complete_task import TaskContext
from ..mcp.connection_manager import MCPConnectionManager


class ContextEnrichmentError(Exception):
    """Exception raised during context enrichment"""
    pass


class ContextEnrichmentEngine:
    """
    Intelligent context enrichment engine.

    Uses MCP server capabilities to enhance task contexts with codebase analysis,
    domain knowledge, and implementation patterns.
    """

    def __init__(self, mcp_manager: MCPConnectionManager):
        """
        Initialize context enrichment engine.

        Args:
            mcp_manager: Connected MCP connection manager
        """
        self.mcp_manager = mcp_manager
        self.logger = logging.getLogger("context.enrichment")

    async def enrich_task_context(
        self,
        task_context: TaskContext,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> TaskContext:
        """
        Enrich a task context with additional intelligent analysis.

        Args:
            task_context: Base task context to enrich
            additional_context: Additional context information

        Returns:
            TaskContext: Enriched task context

        Raises:
            ContextEnrichmentError: If enrichment fails
        """
        try:
            self.logger.info("Starting task context enrichment")

            # Create working copy of context
            enriched_data = task_context.dict()

            # Enrich with codebase analysis
            if self.mcp_manager.is_connected():
                codebase_enrichment = await self._enrich_with_codebase_analysis(task_context)
                self._merge_enrichment(enriched_data, codebase_enrichment)

                # Enrich with domain knowledge
                knowledge_enrichment = await self._enrich_with_domain_knowledge(task_context)
                self._merge_enrichment(enriched_data, knowledge_enrichment)

                # Enrich with implementation patterns
                pattern_enrichment = await self._enrich_with_implementation_patterns(task_context)
                self._merge_enrichment(enriched_data, pattern_enrichment)

            # Apply additional context if provided
            if additional_context:
                additional_enrichment = await self._process_additional_context(
                    task_context, additional_context
                )
                self._merge_enrichment(enriched_data, additional_enrichment)

            # Add enrichment metadata
            enriched_data["environment_context"]["enrichment_metadata"] = {
                "enriched_at": datetime.now().isoformat(),
                "enrichment_version": "1.0.0",
                "mcp_servers_used": ["archon", "serena"] if self.mcp_manager.is_connected() else []
            }

            return TaskContext(**enriched_data)

        except Exception as e:
            self.logger.error(f"Context enrichment failed: {e}")
            raise ContextEnrichmentError(f"Failed to enrich task context: {str(e)}")

    async def _enrich_with_codebase_analysis(self, task_context: TaskContext) -> Dict[str, Any]:
        """Enrich context with codebase analysis using Serena."""
        enrichment = {
            "architecture_context": {},
            "implementation_guidance": {},
            "file_locations": {}
        }

        try:
            # Get project structure analysis
            structure_analysis = await self.mcp_manager.serena.analyze_project_structure()

            # Analyze main files for patterns
            main_files = structure_analysis.get("main_files", [])
            file_patterns = {}

            for file_path in main_files[:10]:  # Limit analysis to avoid overwhelming
                try:
                    symbols_overview = await self.mcp_manager.serena.get_symbols_overview(file_path)
                    file_patterns[file_path] = symbols_overview
                except Exception as e:
                    self.logger.warning(f"Could not analyze file {file_path}: {e}")

            # Extract architectural patterns from codebase
            architecture_patterns = await self._extract_architecture_patterns(file_patterns)
            enrichment["architecture_context"]["discovered_patterns"] = architecture_patterns

            # Extract implementation patterns
            impl_patterns = await self._extract_implementation_patterns(file_patterns)
            enrichment["implementation_guidance"]["codebase_patterns"] = impl_patterns

            # Suggest file locations based on existing structure
            suggested_locations = await self._suggest_file_locations(
                structure_analysis, task_context.project_background
            )
            enrichment["file_locations"].update(suggested_locations)

            self.logger.info("Completed codebase analysis enrichment")

        except Exception as e:
            self.logger.warning(f"Codebase analysis enrichment failed: {e}")

        return enrichment

    async def _enrich_with_domain_knowledge(self, task_context: TaskContext) -> Dict[str, Any]:
        """Enrich context with domain knowledge using Archon RAG."""
        enrichment = {
            "implementation_guidance": {},
            "requirements_context": {}
        }

        try:
            # Extract key terms from project background for knowledge search
            search_terms = await self._extract_search_terms(task_context.project_background)

            # Search for relevant knowledge
            knowledge_results = []
            for term in search_terms[:3]:  # Limit searches
                try:
                    results = await self.mcp_manager.archon.rag_search_knowledge_base(
                        query=term,
                        match_count=2
                    )
                    if results.get("success") and results.get("results"):
                        knowledge_results.extend(results["results"])
                except Exception as e:
                    self.logger.warning(f"Knowledge search for '{term}' failed: {e}")

            # Process knowledge results
            if knowledge_results:
                domain_insights = await self._process_knowledge_results(knowledge_results)
                enrichment["implementation_guidance"]["domain_knowledge"] = domain_insights

            # Search for code examples
            code_examples = await self._search_relevant_code_examples(task_context)
            if code_examples:
                enrichment["implementation_guidance"]["code_examples"] = code_examples

            self.logger.info("Completed domain knowledge enrichment")

        except Exception as e:
            self.logger.warning(f"Domain knowledge enrichment failed: {e}")

        return enrichment

    async def _enrich_with_implementation_patterns(self, task_context: TaskContext) -> Dict[str, Any]:
        """Enrich context with implementation patterns and best practices."""
        enrichment = {
            "implementation_guidance": {},
            "architecture_context": {}
        }

        try:
            # Analyze task requirements for pattern matching
            task_type = await self._classify_task_type(task_context)

            # Get patterns for task type
            patterns = await self._get_patterns_for_task_type(task_type)
            enrichment["implementation_guidance"]["recommended_patterns"] = patterns

            # Get architectural considerations
            arch_considerations = await self._get_architectural_considerations(task_context, task_type)
            enrichment["architecture_context"]["considerations"] = arch_considerations

            # Get testing strategies
            testing_strategies = await self._get_testing_strategies(task_type)
            enrichment["implementation_guidance"]["testing_strategies"] = testing_strategies

            self.logger.info("Completed implementation patterns enrichment")

        except Exception as e:
            self.logger.warning(f"Implementation patterns enrichment failed: {e}")

        return enrichment

    async def _process_additional_context(
        self,
        task_context: TaskContext,
        additional_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process additional context provided by user."""
        enrichment = {
            "project_background": task_context.project_background,
            "architecture_context": {},
            "requirements_context": {},
            "implementation_guidance": {},
            "environment_context": {}
        }

        # Merge additional context intelligently
        for key, value in additional_context.items():
            if key in enrichment and isinstance(value, dict):
                enrichment[key].update(value)
            elif key in enrichment and isinstance(value, str):
                enrichment[key] = f"{enrichment.get(key, '')} | {value}"
            else:
                # Add to environment context as fallback
                enrichment["environment_context"][key] = value

        return enrichment

    async def _extract_architecture_patterns(self, file_patterns: Dict[str, Any]) -> List[str]:
        """Extract architectural patterns from codebase analysis."""
        patterns = []

        # Analyze file structure for patterns
        for file_path, symbols in file_patterns.items():
            if not isinstance(symbols, dict) or "symbols" not in symbols:
                continue

            symbol_list = symbols["symbols"]

            # Look for common patterns
            if "BaseModel" in str(symbol_list):
                patterns.append("Pydantic data models")
            if "APIRouter" in str(symbol_list) or "FastAPI" in str(symbol_list):
                patterns.append("FastAPI REST architecture")
            if "async def" in str(symbol_list):
                patterns.append("Asynchronous programming")
            if "pytest" in file_path or "test_" in file_path:
                patterns.append("Test-driven development")

        return list(set(patterns))  # Remove duplicates

    async def _extract_implementation_patterns(self, file_patterns: Dict[str, Any]) -> List[str]:
        """Extract implementation patterns from codebase."""
        patterns = []

        # Common implementation patterns
        pattern_indicators = {
            "Factory pattern": ["factory", "create", "build"],
            "Repository pattern": ["repository", "repo", "data_access"],
            "Service layer": ["service", "business_logic"],
            "Dependency injection": ["inject", "dependency", "container"],
            "Error handling": ["exception", "error", "handle"],
            "Validation": ["validate", "validator", "field"]
        }

        for file_path, symbols in file_patterns.items():
            content_str = str(symbols).lower()
            for pattern_name, indicators in pattern_indicators.items():
                if any(indicator in content_str for indicator in indicators):
                    patterns.append(pattern_name)

        return list(set(patterns))

    async def _suggest_file_locations(
        self,
        structure_analysis: Dict[str, Any],
        project_background: str
    ) -> Dict[str, str]:
        """Suggest file locations based on existing project structure."""
        suggestions = {}

        # Analyze existing structure
        if "structure" in structure_analysis and "dirs" in structure_analysis["structure"]:
            existing_dirs = structure_analysis["structure"]["dirs"]

            # Standard suggestions based on common patterns
            if "src" in existing_dirs:
                if "models" in existing_dirs or any("model" in d for d in existing_dirs):
                    suggestions["src/models/"] = "Data model implementations"
                if "api" in existing_dirs or any("api" in d for d in existing_dirs):
                    suggestions["src/api/"] = "API endpoint implementations"
                if "utils" in existing_dirs or "utilities" in existing_dirs:
                    suggestions["src/utils/"] = "Utility functions and helpers"
                if "services" in existing_dirs:
                    suggestions["src/services/"] = "Business logic services"

            if "tests" in existing_dirs:
                suggestions["tests/"] = "Unit and integration tests"

        return suggestions

    async def _extract_search_terms(self, project_background: str) -> List[str]:
        """Extract key search terms from project background."""
        # Simple keyword extraction (in production, could use NLP)
        words = project_background.lower().split()

        # Common technical keywords to look for
        technical_keywords = [
            "api", "database", "authentication", "authorization", "microservice",
            "rest", "graphql", "redis", "postgresql", "mongodb", "docker",
            "kubernetes", "python", "fastapi", "django", "flask", "async",
            "testing", "security", "performance", "caching", "queue"
        ]

        found_terms = []
        for word in words:
            cleaned_word = word.strip(".,!?;:")
            if cleaned_word in technical_keywords:
                found_terms.append(cleaned_word)

        # Remove duplicates and return top terms
        return list(set(found_terms))[:5]

    async def _process_knowledge_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process knowledge search results into actionable insights."""
        insights = {
            "best_practices": [],
            "common_patterns": [],
            "potential_pitfalls": []
        }

        for result in results:
            content = result.get("content", "").lower()

            # Extract best practices
            if "best practice" in content or "recommended" in content:
                insights["best_practices"].append(result.get("content", "")[:200] + "...")

            # Extract patterns
            if "pattern" in content or "approach" in content:
                insights["common_patterns"].append(result.get("content", "")[:200] + "...")

            # Extract warnings or pitfalls
            if "avoid" in content or "pitfall" in content or "warning" in content:
                insights["potential_pitfalls"].append(result.get("content", "")[:200] + "...")

        return insights

    async def _search_relevant_code_examples(self, task_context: TaskContext) -> List[Dict[str, Any]]:
        """Search for relevant code examples."""
        examples = []

        try:
            # Extract key terms for code example search
            search_terms = await self._extract_search_terms(task_context.project_background)

            for term in search_terms[:2]:  # Limit searches
                try:
                    results = await self.mcp_manager.archon.rag_search_code_examples(
                        query=term,
                        match_count=2
                    )
                    if results.get("success") and results.get("results"):
                        examples.extend(results["results"])
                except Exception as e:
                    self.logger.warning(f"Code example search for '{term}' failed: {e}")

        except Exception as e:
            self.logger.warning(f"Code example search failed: {e}")

        return examples

    async def _classify_task_type(self, task_context: TaskContext) -> str:
        """Classify task type based on context."""
        background = task_context.project_background.lower()

        if "model" in background or "pydantic" in background:
            return "data_modeling"
        elif "api" in background or "endpoint" in background:
            return "api_development"
        elif "test" in background or "testing" in background:
            return "testing"
        elif "database" in background or "data" in background:
            return "database"
        elif "ui" in background or "frontend" in background:
            return "frontend"
        elif "auth" in background or "security" in background:
            return "security"
        else:
            return "general"

    async def _get_patterns_for_task_type(self, task_type: str) -> List[str]:
        """Get recommended patterns for task type."""
        patterns_map = {
            "data_modeling": [
                "Use Pydantic BaseModel for data validation",
                "Implement field validators for business rules",
                "Add JSON schema generation for API documentation",
                "Use Field() for detailed field specifications"
            ],
            "api_development": [
                "Follow REST conventions for resource naming",
                "Use proper HTTP status codes",
                "Implement request/response validation",
                "Add comprehensive error handling",
                "Use dependency injection for services"
            ],
            "testing": [
                "Write tests before implementation (TDD)",
                "Use fixtures for test data setup",
                "Mock external dependencies",
                "Test both happy path and edge cases",
                "Aim for high test coverage (95%+)"
            ],
            "database": [
                "Use async database operations",
                "Implement proper connection pooling",
                "Add database migrations",
                "Use prepared statements to prevent SQL injection",
                "Implement proper indexing strategies"
            ],
            "security": [
                "Validate all inputs",
                "Use proper authentication mechanisms",
                "Implement authorization checks",
                "Hash passwords securely",
                "Use HTTPS for all communications"
            ],
            "general": [
                "Follow project coding standards",
                "Write clean, readable code",
                "Add proper error handling",
                "Include comprehensive documentation",
                "Write unit tests for new functionality"
            ]
        }

        return patterns_map.get(task_type, patterns_map["general"])

    async def _get_architectural_considerations(
        self,
        task_context: TaskContext,
        task_type: str
    ) -> List[str]:
        """Get architectural considerations for task type."""
        considerations = {
            "data_modeling": [
                "Consider model inheritance and composition",
                "Plan for data migration and versioning",
                "Think about serialization performance",
                "Consider validation performance impact"
            ],
            "api_development": [
                "Design for scalability and performance",
                "Consider rate limiting and caching",
                "Plan for API versioning",
                "Think about backwards compatibility"
            ],
            "database": [
                "Consider read/write patterns",
                "Plan for data growth and partitioning",
                "Think about backup and recovery",
                "Consider distributed database needs"
            ],
            "security": [
                "Follow principle of least privilege",
                "Consider security in depth",
                "Plan for security monitoring",
                "Think about compliance requirements"
            ]
        }

        base_considerations = [
            "Maintain consistency with existing architecture",
            "Consider maintainability and readability",
            "Think about testing strategies",
            "Plan for monitoring and observability"
        ]

        return considerations.get(task_type, []) + base_considerations

    async def _get_testing_strategies(self, task_type: str) -> List[str]:
        """Get testing strategies for task type."""
        strategies = {
            "data_modeling": [
                "Test model validation with valid and invalid data",
                "Test serialization and deserialization",
                "Test business logic methods",
                "Test edge cases and boundary conditions"
            ],
            "api_development": [
                "Test all HTTP methods and status codes",
                "Test request validation and error responses",
                "Test authentication and authorization",
                "Test integration with downstream services"
            ],
            "database": [
                "Test CRUD operations",
                "Test transaction handling",
                "Test connection pooling and error recovery",
                "Test data migrations"
            ]
        }

        base_strategies = [
            "Write unit tests for all public methods",
            "Include integration tests for system interactions",
            "Add performance tests for critical paths",
            "Mock external dependencies appropriately"
        ]

        return strategies.get(task_type, []) + base_strategies

    def _merge_enrichment(
        self,
        base_data: Dict[str, Any],
        enrichment: Dict[str, Any]
    ) -> None:
        """Merge enrichment data into base data."""
        for key, value in enrichment.items():
            if key not in base_data:
                base_data[key] = value
            elif isinstance(base_data[key], dict) and isinstance(value, dict):
                base_data[key].update(value)
            elif isinstance(base_data[key], list) and isinstance(value, list):
                base_data[key].extend(value)
            elif isinstance(base_data[key], str) and isinstance(value, str):
                # Append to existing string
                base_data[key] = f"{base_data[key]} | {value}"
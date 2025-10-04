# Windsurf AI Rules for Orca Development

## Project Overview
Orca is a sophisticated multi-agent workflow orchestration system with parallel execution capabilities. It transforms development from planning to implementation through intelligent agent coordination.

## Critical Development Rules

### 1. Archon-First Development (MANDATORY)
- **ALWAYS** check Archon MCP server availability before starting any task
- **NEVER** create tasks manually - use Archon for ALL project and task management
- **ALWAYS** research using Archon RAG before implementing features
- Follow task-driven development workflow exclusively

### 2. Code Quality Standards
- **Coverage**: Minimum 95% test coverage (enforced by pytest)
- **Type Safety**: Strict mypy type checking (no untyped definitions)
- **Formatting**: Black with 120 character line length
- **Linting**: Pylint with configured rules (see pyproject.toml)
- **Security**: Bandit scanning before commits

### 3. Architecture Principles
- **Stateless Agents**: Each agent operates independently with complete context
- **Artifact-Driven**: Agents produce specific markdown artifacts for each phase
- **Template-Based**: Use standardized templates for consistency
- **Clarification Loops**: Built-in pause mechanisms for ambiguity resolution

### 4. Testing Requirements
- Write tests BEFORE implementation (TDD)
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- Async tests use `asyncio_mode = "auto"`
- Mock external dependencies (MCP servers, HTTP calls)

### 5. File Organization
```
src/
├── agents/          # Agent implementations
├── execution/       # Parallel execution engine
├── integration/     # MCP server integration
├── monitoring/      # Analytics and monitoring
└── utils/          # Shared utilities

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── fixtures/       # Test fixtures and mocks
```

### 6. MCP Server Integration
- **Archon** (HTTP): `http://localhost:8051/mcp`
  - Project and task management
  - Knowledge base search
  - Task dependency tracking
  
- **Serena** (stdio): Via uvx
  - Semantic code operations
  - Project context management
  - Code analysis

### 7. Execution Strategies
- **Aggressive**: Fast prototyping, lower reliability
- **Hybrid**: Balanced (default for most scenarios)
- **Conservative**: Production systems, high reliability
- **Sequential**: Debugging, learning, simple projects

### 8. Code Style Guidelines
```python
# Good: Type hints, docstrings, clear structure
async def execute_task(
    task: Task,
    context: ExecutionContext,
    strategy: ExecutionStrategy = ExecutionStrategy.HYBRID
) -> TaskResult:
    """Execute a task with the specified strategy.
    
    Args:
        task: The task to execute
        context: Execution context with dependencies
        strategy: Execution strategy to use
        
    Returns:
        TaskResult with execution status and metrics
    """
    pass

# Bad: No types, no docs, unclear
async def run(t, c, s=None):
    pass
```

### 9. Pre-Commit Workflow
1. Format: `black src tests && isort src tests`
2. Lint: `pylint src tests`
3. Type check: `mypy src`
4. Security: `bandit -r src`
5. Test: `pytest`
6. Pre-commit hooks: `pre-commit run --all-files`

### 10. Documentation Standards
- Update README.md for user-facing changes
- Update CLAUDE.md for Claude Code integration changes
- Update archon_rules.md for workflow changes
- Keep templates/ synchronized with code changes
- Add docstrings to all public functions/classes

## Common Commands

### Development
```bash
# Run tests with coverage
pytest

# Run specific test markers
pytest -m unit
pytest -m integration

# Format and lint
black src tests
isort src tests
pylint src tests

# Type checking
mypy src

# Security scan
bandit -r src -f json -o bandit-report.json
```

### Orca Workflows
```bash
# System verification
/orca-startup

# MCP server check
/orca-deps

# Execute plans
/orca-execute "./plan.md" "hybrid" 3

# Preview execution
/orca-preview "./plan.md" "aggressive"
```

## AI Assistant Guidelines

### When Implementing Features
1. Check Archon for existing tasks/context
2. Research using Archon RAG
3. Write tests first (TDD)
4. Implement with full type hints
5. Run quality checks
6. Update documentation

### When Debugging
1. Check test coverage for affected code
2. Add logging/debugging statements
3. Run specific test markers
4. Use mypy for type-related issues
5. Check MCP server connectivity if integration fails

### When Refactoring
1. Ensure tests pass before changes
2. Maintain or improve coverage
3. Keep stateless architecture
4. Update type hints if signatures change
5. Run full quality suite after changes

## Performance Targets
- **Small Projects** (5-10 tasks): 2-3x faster
- **Medium Projects** (10-25 tasks): 3-4x faster
- **Large Projects** (25+ tasks): 4-5x faster
- **Parallel Efficiency**: 85%+ target

## Security Considerations
- Private repositories by default
- No hardcoded secrets or API keys
- Use environment variables for configuration
- Scan dependencies for vulnerabilities
- Follow secure MCP communication protocols

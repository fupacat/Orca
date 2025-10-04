# Windsurf Configuration for Orca

This directory contains Windsurf IDE configuration for the Orca Development Execution System.

## Configuration Files

### `config.json`
Main configuration file containing:
- Project metadata and settings
- Python tooling configuration (black, pylint, mypy, pytest)
- Task definitions for common workflows
- MCP server integration settings
- AI assistant rules and context

### `settings.json`
Editor-specific settings:
- Python interpreter and analysis settings
- Linting and formatting configuration
- Testing framework setup
- File exclusions and watchers
- Language-specific formatting rules

### `tasks.json`
Predefined tasks for common operations:
- Testing (all, unit, integration, coverage)
- Code quality (format, lint, type-check, security)
- Pre-commit workflows
- Dependency installation

### `launch.json`
Debug configurations:
- Debug current file
- Debug tests (all, current, specific markers)
- Debug modules
- Attach to running processes

### `rules.md`
AI assistant guidelines:
- Archon-first development rules
- Code quality standards
- Architecture principles
- Testing requirements
- Common commands and workflows

## Quick Start

### 1. Setup Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

### 2. Verify Configuration
```bash
# Check Python version
python --version  # Should be 3.11+

# Verify tools are installed
black --version
pylint --version
mypy --version
pytest --version
```

### 3. Run Quality Checks
```bash
# Format code
black src tests
isort src tests

# Run linting
pylint src tests

# Type checking
mypy src

# Run tests
pytest
```

## Available Tasks

Access tasks via Windsurf's task runner or command palette:

### Testing
- **Test: All** - Run all tests with coverage (default)
- **Test: Unit** - Run unit tests only
- **Test: Integration** - Run integration tests only
- **Test: Coverage Report** - Generate HTML coverage report

### Code Quality
- **Format: Black + isort** - Format all code
- **Lint: Pylint** - Run pylint checks
- **Type Check: Mypy** - Run type checking
- **Security: Bandit** - Run security scan
- **Quality: Full Check** - Run all quality checks
- **Pre-commit: All Files** - Run pre-commit hooks

### Development
- **Install: Dev Dependencies** - Install development dependencies
- **Install: Test Dependencies** - Install testing dependencies
- **Install: Quality Dependencies** - Install quality tools
- **Coverage: Open HTML Report** - Open coverage report in browser

## Debug Configurations

Available debug configurations:

1. **Python: Current File** - Debug the currently open Python file
2. **Python: Debug Tests** - Debug all tests in current file
3. **Python: Debug Current Test** - Debug selected test function
4. **Python: All Tests** - Debug all tests in project
5. **Python: Unit Tests Only** - Debug unit tests
6. **Python: Integration Tests Only** - Debug integration tests
7. **Python: Module** - Debug as Python module
8. **Python: Attach to Process** - Attach debugger to running process

## MCP Server Integration

### Archon (HTTP)
- **URL**: `http://localhost:8051/mcp`
- **Purpose**: Task and project management, knowledge base
- **Check**: Run `/orca-deps` in Claude Code

### Serena (stdio)
- **Command**: `uvx --from git+https://github.com/oraios/serena serena start-mcp-server`
- **Purpose**: Semantic code operations, project context
- **Check**: Run `/orca-startup` in Claude Code

## Code Quality Standards

### Coverage
- **Minimum**: 95% (enforced by pytest)
- **Report**: `htmlcov/index.html` after running tests
- **Command**: `pytest --cov=src --cov-report=html`

### Type Checking
- **Mode**: Strict (mypy)
- **Config**: `pyproject.toml` [tool.mypy]
- **Command**: `mypy src`

### Formatting
- **Tool**: Black
- **Line Length**: 120 characters
- **Config**: `pyproject.toml` [tool.black]
- **Command**: `black src tests`

### Import Sorting
- **Tool**: isort
- **Profile**: black
- **Config**: `pyproject.toml` [tool.isort]
- **Command**: `isort src tests`

### Linting
- **Tool**: Pylint
- **Config**: `pyproject.toml` [tool.pylint]
- **Command**: `pylint src tests`

### Security
- **Tool**: Bandit
- **Config**: `pyproject.toml` [tool.bandit]
- **Report**: `bandit-report.json`
- **Command**: `bandit -r src -f json -o bandit-report.json`

## Keyboard Shortcuts (Recommended)

Configure these in Windsurf for faster workflow:

- **Ctrl+Shift+T** - Run Test: All
- **Ctrl+Shift+F** - Format: Black + isort
- **Ctrl+Shift+L** - Lint: Pylint
- **Ctrl+Shift+M** - Type Check: Mypy
- **F5** - Start Debugging (current configuration)
- **Ctrl+F5** - Run Without Debugging

## AI Assistant Integration

The AI assistant is configured with:

### Context Includes
- README.md, CLAUDE.md, archon_rules.md
- pyproject.toml
- All Python source files (src/, tests/)
- Template files (templates/)

### Context Excludes
- Coverage reports (htmlcov/)
- Cache directories (__pycache__, .pytest_cache, .mypy_cache)
- Build artifacts (*.pyc, .coverage)
- Security reports (bandit-report.json, safety-report.json)

### Development Rules
1. **Archon-first**: Always check Archon before starting tasks
2. **TDD**: Write tests before implementation
3. **Type Safety**: Full type hints required
4. **Coverage**: Maintain 95%+ coverage
5. **Security**: Run bandit before commits

## Troubleshooting

### Python Interpreter Not Found
```bash
# Create virtual environment
python -m venv .venv

# Update settings.json if path differs
"python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe"
```

### Tests Not Discovered
```bash
# Ensure pytest is installed
pip install -e .[test]

# Reload window in Windsurf
# Or manually discover tests via command palette
```

### Linting Errors
```bash
# Install quality tools
pip install -e .[quality]

# Check pyproject.toml configuration
# Ensure pylint, mypy, bandit are in PATH
```

### MCP Server Connection Issues
```bash
# Check Archon server
curl http://localhost:8051/mcp

# Verify Serena installation
uvx --from git+https://github.com/oraios/serena serena --version

# Run full system check
# Use /orca-startup in Claude Code
```

## Additional Resources

- **Main README**: `../README.md`
- **Claude Integration**: `../CLAUDE.md`
- **Archon Rules**: `../archon_rules.md`
- **Project Config**: `../pyproject.toml`
- **Templates**: `../templates/`

## Support

For issues or questions:
1. Check `archon_rules.md` for development workflow
2. Review `CLAUDE.md` for Claude Code integration
3. Consult `README.md` for system architecture
4. Use Archon RAG search for implementation guidance

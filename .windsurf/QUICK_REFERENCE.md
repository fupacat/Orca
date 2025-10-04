# Windsurf Quick Reference Card

## 🚀 Essential Commands

### Testing
```bash
pytest                          # Run all tests
pytest -m unit                  # Unit tests only
pytest -m integration           # Integration tests only
pytest --cov=src               # With coverage report
pytest tests/test_file.py      # Specific file
pytest -k "test_name"          # Specific test
```

### Code Quality
```bash
black src tests                 # Format code
isort src tests                 # Sort imports
pylint src tests                # Lint code
mypy src                        # Type check
bandit -r src                   # Security scan
```

### One-Line Quality Check
```bash
black src tests && isort src tests && pylint src tests && mypy src && pytest
```

### Pre-commit
```bash
pre-commit run --all-files      # Run all hooks
pre-commit install              # Install hooks
```

## 🎯 Windsurf Tasks

Access via Command Palette → "Run Task" or Task Runner panel:

- **Test: All** - Run all tests (Ctrl+Shift+T)
- **Test: Unit** - Unit tests only
- **Test: Integration** - Integration tests only
- **Format: Black + isort** - Format all code (Ctrl+Shift+F)
- **Lint: Pylint** - Run linting (Ctrl+Shift+L)
- **Type Check: Mypy** - Type checking (Ctrl+Shift+M)
- **Quality: Full Check** - All quality checks
- **Coverage: Open HTML Report** - View coverage

## 🐛 Debug Configurations

Press F5 or use Debug panel:

- **Python: Current File** - Debug open file
- **Python: Debug Tests** - Debug all tests in file
- **Python: Debug Current Test** - Debug selected test
- **Python: All Tests** - Debug all tests
- **Python: Unit Tests Only** - Debug unit tests
- **Python: Integration Tests Only** - Debug integration tests

## 📝 File Locations

```
.windsurf/
├── config.json          # Main configuration
├── settings.json        # Editor settings
├── tasks.json          # Task definitions
├── launch.json         # Debug configs
├── rules.md            # AI guidelines
├── README.md           # Full documentation
├── SETUP_COMPLETE.md   # Setup summary
└── QUICK_REFERENCE.md  # This file
```

## 🔧 Configuration Files

```
pyproject.toml          # Python project config
.gitignore             # Git ignore rules
.pre-commit-config.yaml # Pre-commit hooks
README.md              # Project documentation
CLAUDE.md              # Claude integration
archon_rules.md        # Development rules
```

## 🎨 Code Style

```python
# Good Example
from typing import Optional, List
from pydantic import BaseModel

class Task(BaseModel):
    """Represents a development task.
    
    Attributes:
        id: Unique task identifier
        name: Task name
        dependencies: List of dependency task IDs
    """
    id: str
    name: str
    dependencies: List[str] = []
    
    async def execute(self, context: ExecutionContext) -> TaskResult:
        """Execute the task with given context.
        
        Args:
            context: Execution context with dependencies
            
        Returns:
            TaskResult with execution status
        """
        pass
```

## 📊 Quality Standards

| Tool | Standard | Config |
|------|----------|--------|
| Coverage | ≥95% | pyproject.toml |
| Line Length | 120 chars | pyproject.toml |
| Type Checking | Strict | pyproject.toml |
| Formatter | Black | pyproject.toml |
| Linter | Pylint | pyproject.toml |
| Security | Bandit | pyproject.toml |

## 🔌 MCP Servers

### Archon (HTTP)
```bash
# URL
http://localhost:8051/mcp

# Check status
curl http://localhost:8051/mcp

# In Claude Code
/orca-deps
```

### Serena (stdio)
```bash
# Command
uvx --from git+https://github.com/oraios/serena serena start-mcp-server

# Check version
uvx --from git+https://github.com/oraios/serena serena --version

# In Claude Code
/orca-startup
```

## 🎯 Orca Commands

In Claude Code:

```bash
/orca-deps              # Quick MCP check
/orca-startup           # Full system check
/orca-start             # Start workflow
/orca-execute           # Execute plans
/orca-preview           # Preview execution
/orca-validate          # Validate plans
/orca-new               # New project
/orca-workflow          # Complete workflow
/orca-github            # GitHub integration
```

## 🔍 Common Patterns

### Run Specific Test
```bash
# By name
pytest -k "test_execution"

# By marker
pytest -m unit

# By file
pytest tests/unit/test_execution.py

# By class
pytest tests/unit/test_execution.py::TestExecution

# By method
pytest tests/unit/test_execution.py::TestExecution::test_method
```

### Debug Test
1. Set breakpoint in test
2. Press F5
3. Select "Python: Debug Tests"
4. Or use "Python: Debug Current Test" for specific test

### View Coverage
```bash
# Generate report
pytest --cov=src --cov-report=html

# Open in browser
start htmlcov/index.html

# Or use task: "Coverage: Open HTML Report"
```

### Format on Save
Already enabled! Just save file (Ctrl+S):
- Black formatting
- Import sorting
- Trailing whitespace removal

## 🚨 Troubleshooting

### Import Errors
```bash
# Add to PYTHONPATH
$env:PYTHONPATH = "$PWD\src"

# Or activate venv
.venv\Scripts\activate
```

### Test Discovery Issues
```bash
# Reinstall test dependencies
pip install -e .[test]

# Reload Windsurf window
Ctrl+Shift+P → "Reload Window"
```

### Linting False Positives
```python
# Disable specific check
# pylint: disable=too-many-arguments

# Disable for line
result = function()  # pylint: disable=line-too-long
```

### Type Checking Issues
```python
# Type ignore
result = function()  # type: ignore

# Type ignore with reason
result = function()  # type: ignore[arg-type]
```

## 📚 Documentation

- **Windsurf Config**: `.windsurf/README.md`
- **AI Rules**: `.windsurf/rules.md`
- **Setup Guide**: `.windsurf/SETUP_COMPLETE.md`
- **Project Docs**: `README.md`
- **Claude Integration**: `CLAUDE.md`
- **Development Rules**: `archon_rules.md`

## ⌨️ Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run Task | Ctrl+Shift+P → "Run Task" |
| Debug | F5 |
| Run Without Debug | Ctrl+F5 |
| Format Document | Shift+Alt+F |
| Organize Imports | Shift+Alt+O |
| Go to Definition | F12 |
| Find References | Shift+F12 |
| Rename Symbol | F2 |
| Quick Fix | Ctrl+. |
| Command Palette | Ctrl+Shift+P |
| Terminal | Ctrl+` |

## 🎓 Best Practices

1. **Archon First** - Always check Archon before starting
2. **TDD** - Write tests before implementation
3. **Type Hints** - Full type annotations required
4. **Coverage** - Maintain 95%+ coverage
5. **Format** - Auto-format on save
6. **Lint** - Fix linting issues immediately
7. **Security** - Run bandit before commits
8. **Documentation** - Docstrings for all public APIs

## 🔗 Quick Links

- [Python Docs](https://docs.python.org/3/)
- [Pytest Docs](https://docs.pytest.org/)
- [Black Docs](https://black.readthedocs.io/)
- [Mypy Docs](https://mypy.readthedocs.io/)
- [Pylint Docs](https://pylint.readthedocs.io/)
- [Pydantic Docs](https://docs.pydantic.dev/)

---

**Last Updated**: 2025-10-02
**Version**: 1.0.0

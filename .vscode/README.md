# VSCode IDE Configuration for Orca

This directory contains recommended IDE settings, tasks, and launch configurations for the Orca project.

## Files

### `settings.json`
Project-specific settings optimized for Python development with Orca:
- **Python**: Black formatting, Pytest testing, type checking
- **Editor**: 88-char ruler (Black standard), auto-save, trim whitespace
- **Files**: Exclude build artifacts, cache directories
- **Markdown**: Word wrap, linkify for documentation
- **Git**: Auto-fetch, smart commit

### `extensions.json`
Recommended VSCode extensions:
- **Python**: Python, Pylance, Black formatter
- **Testing**: Coverage gutters, test adapter
- **Git**: GitLens, Git Graph
- **Markdown**: All-in-one, linting, Mermaid diagrams
- **Utilities**: Todo tree, spell checker
- **Claude Code**: Anthropic Claude Code extension

### `tasks.json`
Pre-configured tasks (Ctrl+Shift+P → "Tasks: Run Task"):
- **Run All Tests**: `pytest tests/ -v`
- **Run Tests with Coverage**: Default test task (Ctrl+Shift+T)
- **Run Single Test File**: Test currently open file
- **Format Code (Black)**: Auto-format with Black
- **Lint Code (Ruff)**: Check code quality
- **Type Check (MyPy)**: Validate type hints
- **Security Scan (Bandit)**: Security vulnerability scan
- **Convert Plan to Tasks**: Run plan-to-tasks converter
- **Full Quality Check**: Run all quality checks in sequence

### `launch.json`
Debug configurations (F5):
- **Python: Current File**: Debug the active file
- **Python: Current Test File**: Debug current test file with pytest
- **Python: All Tests**: Debug entire test suite
- **Convert Plan to Tasks**: Debug the plan converter script

## Quick Start

### 1. Install Recommended Extensions
When you open this project, VSCode will prompt you to install recommended extensions. Click "Install All" or:
```
Ctrl+Shift+P → "Extensions: Show Recommended Extensions"
```

### 2. Keyboard Shortcuts

**Testing:**
- `Ctrl+Shift+T` - Run tests with coverage (default)
- `F5` - Debug current file/test

**Code Quality:**
- `Shift+Alt+F` - Format current file with Black
- `Ctrl+Shift+B` - Run build task

**Tasks:**
- `Ctrl+Shift+P` → "Tasks: Run Task" - Show all available tasks

### 3. Python Environment Setup

The settings assume Python is in your PATH. If using a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt  # If you have one
```

Then reload VSCode to pick up the virtual environment.

### 4. Coverage Display

After running "Run Tests with Coverage" task:
1. Install "Coverage Gutters" extension
2. Click "Watch" in the status bar
3. Green/red indicators appear in the gutter showing coverage

## Orca-Specific Features

### Plan Conversion Task
The "Convert Plan to Tasks" task prompts you for:
- **Plan path**: Input plan file (default: `plan.md`)
- **Output path**: Output execution plan (default: `execution_plan.md`)

Run it via:
```
Ctrl+Shift+P → "Tasks: Run Task" → "Convert Plan to Tasks"
```

### Full Quality Check
Runs the complete quality pipeline:
1. Format code with Black
2. Lint with Ruff
3. Type check with MyPy
4. Run tests with coverage
5. Security scan with Bandit

Run it via:
```
Ctrl+Shift+P → "Tasks: Run Task" → "Full Quality Check"
```

## Troubleshooting

### "Python not found"
Ensure Python is installed and in PATH:
```bash
python --version  # Should show Python 3.11+
```

### "Module not found" errors
Set PYTHONPATH or use virtual environment:
```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### Tests not discovering
Check Python test configuration:
1. `Ctrl+Shift+P` → "Python: Configure Tests"
2. Select "pytest"
3. Select "tests" directory

### Black formatting not working
Install Black:
```bash
pip install black
```

## Customization

Feel free to customize these settings for your workflow:

1. **Copy to user settings**: Settings you want globally
2. **Modify tasks**: Add your own custom tasks
3. **Adjust formatting**: Change line length, quote style, etc.

The provided settings are recommendations based on Python best practices and Orca project structure.

## Additional Resources

- [VSCode Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)
- [VSCode Tasks Documentation](https://code.visualstudio.com/docs/editor/tasks)
- [Black Code Style](https://black.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

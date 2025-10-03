# Git Hooks for Orca Project

Custom git hooks that enforce code quality and best practices.

## Installation

### Quick Setup
```bash
# Configure git to use these hooks
git config core.hooksPath .githooks

# Verify installation
git config core.hooksPath
# Should output: .githooks
```

### Manual Setup (Alternative)
If you prefer to keep system hooks, you can copy these to `.git/hooks/`:
```bash
cp .githooks/* .git/hooks/
chmod +x .git/hooks/pre-commit .git/hooks/commit-msg .git/hooks/pre-push
```

## Available Hooks

### pre-commit
Runs **before every commit** to ensure code quality.

**Checks:**
- ✅ Black code formatting
- ✅ Ruff linting
- ✅ MyPy type checking (src/ files only)
- ✅ Affected tests pass
- ⚠️ Print statements detection (warns)
- ⚠️ TODO/FIXME without issue reference (warns)
- ⚠️ Large files >5000 lines (warns)

**Example output:**
```
🔍 Running pre-commit quality checks...
📝 Files to check:
  - src/state/models.py
  - tests/unit/test_state_models.py

🎨 Checking code formatting with Black...
✅ Black formatting passed
🔍 Running Ruff linter...
✅ Ruff linting passed
🔎 Running MyPy type checker...
✅ MyPy type checking passed
🧪 Running affected tests...
✅ Tests passed
```

**Bypass (when necessary):**
```bash
git commit --no-verify -m "Emergency fix"
```

### commit-msg
Validates **commit message format** for consistency.

**Checks:**
- ❌ Subject line length (max 72 chars, warn at 50)
- ❌ No period at end of subject
- ❌ Blank line between subject and body
- ⚠️ Suggests imperative mood (Add, Fix, Update)
- ⚠️ Suggests emoji prefix (✨ feat, 🐛 fix, etc.)
- ⚠️ Warns about WIP commits
- ⚠️ Body line length (max 72 chars)
- 💡 Suggests TASK-XXX marker for implementations
- 💡 Suggests test coverage info
- 💡 Suggests Claude co-authorship

**Good commit message:**
```
✨ feat: Add state tracking data models

Implement Pydantic V2 models for TaskState, FileState, and CommitState
to enable comprehensive state tracking.

Test coverage: 100% (15/15 tests passing)
Closes TASK-001

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Bad commit message:**
```
Fixed stuff.  <-- Too short, ends with period, no emoji
```

### pre-push
Runs **before every push** for comprehensive quality assurance.

**Checks:**
- ✅ Full test suite passes
- ✅ Test coverage meets threshold (80%+)
- ✅ Security scan (Bandit) passes
- ⚠️ No exposed secrets in diff
- ⚠️ No credential files (.env, etc.)
- ❌ Blocks direct push to main/master/production
- ✅ Validates commit message format

**Example output:**
```
🚀 Running pre-push quality checks...

🧪 Running full test suite...
✅ All tests passed

📊 Checking test coverage...
✅ Coverage meets minimum threshold (80%)

🔒 Running security scan...
✅ No high/medium severity security issues

🔍 Checking for exposed secrets...
✅ No obvious secrets detected

📝 Validating commit messages...
✅ All commit messages valid

╔════════════════════════════════════════╗
║  ✅ All pre-push checks PASSED        ║
╚════════════════════════════════════════╝
```

**Bypass (when necessary):**
```bash
git push --no-verify
```

## Hook Configuration

### Customize Quality Thresholds

Edit the hook files to adjust thresholds:

**pre-commit:**
- Line 90: Adjust file size warning (default: 5000 lines)

**pre-push:**
- Line 35: Adjust coverage threshold (default: 80%)

### Disable Specific Checks

Comment out sections in the hooks:

```bash
# To disable MyPy type checking in pre-commit:
# Find the "# 3. MyPy type checking" section
# Comment out the entire if block
```

### Add Custom Checks

Add your own checks to the hooks:

```bash
# Example: Add spell check to pre-commit
if command_exists codespell; then
    echo -e "${YELLOW}📝 Running spell checker...${NC}"
    if echo "$PYTHON_FILES" | xargs codespell; then
        echo -e "${GREEN}✅ Spell check passed${NC}"
    else
        echo -e "${RED}❌ Spelling errors found${NC}"
        CHECKS_FAILED=1
    fi
fi
```

## Dependencies

Hooks will automatically detect and use these tools if installed:

**Required for full functionality:**
```bash
pip install black ruff mypy pytest pytest-cov bandit
```

**Optional but recommended:**
```bash
pip install coverage codespell git-secrets
```

**Check what's installed:**
```bash
# Test the hooks without committing
.githooks/pre-commit
```

## Best Practices

### 1. Fix Issues Early
Run checks manually before committing:
```bash
# Format code
black src/ tests/

# Fix linting issues
ruff check src/ tests/ --fix

# Run tests
pytest tests/ -v

# Check types
mypy src/
```

### 2. Use VSCode Tasks
The project includes pre-configured VSCode tasks:
```
Ctrl+Shift+P → Tasks: Run Task → Full Quality Check
```

### 3. Commit Often
Hooks run fast on small changes. Commit frequently:
```bash
git add src/state/models.py tests/unit/test_state_models.py
git commit -m "✨ feat: Add TaskState model"
```

### 4. Write Good Commit Messages
Use the `.gitmessage` template:
```bash
# Set it as default template
git config commit.template .gitmessage

# Now when you commit, it shows the template
git commit
```

### 5. Review Before Push
The pre-push hook runs the full suite. If it's slow:
```bash
# Run it manually first
.githooks/pre-push

# Then push if it passes
git push
```

## Troubleshooting

### Hooks Not Running
```bash
# Check hooks path is set
git config core.hooksPath
# Should output: .githooks

# If not, set it:
git config core.hooksPath .githooks

# Verify hooks are executable (Unix/Mac)
ls -la .githooks/
# Should show -rwxr-xr-x
```

### "Command not found" Errors
Install the missing tool:
```bash
# For Black
pip install black

# For Ruff
pip install ruff

# For MyPy
pip install mypy

# For Pytest
pip install pytest pytest-cov

# For Bandit
pip install bandit
```

### Hooks Too Slow
Options:
1. Run only on changed files (already implemented)
2. Disable type checking: Comment out MyPy section
3. Skip hook for emergency commits: `git commit --no-verify`
4. Adjust pre-push to run only critical checks

### False Positives
Add suppression comments in code:
```python
print("Debug info")  # noqa: T201  (suppress print warning)
# TODO(#123): Fix this later  (link to issue)
```

### Windows Git Bash Issues
Ensure you're using Git Bash:
```bash
# In VSCode terminal, select Git Bash as default
# Or run hooks directly:
bash .githooks/pre-commit
```

## Disabling Hooks

### Temporarily (Single Commit)
```bash
git commit --no-verify
git push --no-verify
```

### Permanently (Not Recommended)
```bash
git config --unset core.hooksPath
```

### For Specific Branch
```bash
# Create a branch without hooks
git checkout -b experiment
git config --local core.hooksPath ""

# Re-enable later
git config --local core.hooksPath .githooks
```

## CI/CD Integration

These hooks mirror CI/CD checks. If hooks pass locally, CI should pass too.

**GitHub Actions Example:**
```yaml
name: Quality Checks
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install black ruff mypy pytest pytest-cov bandit
      - name: Run quality checks
        run: |
          black --check src/ tests/
          ruff check src/ tests/
          mypy src/
          pytest tests/ --cov=src --cov-fail-under=80
          bandit -r src/ -ll
```

## Additional Resources

- [Git Hooks Documentation](https://git-scm.com/docs/githooks)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Black Code Style](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)

---

**Questions or Issues?**
- Check the troubleshooting section above
- Review individual hook files for implementation details
- Customize hooks to match your workflow

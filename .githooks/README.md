# Git Hooks - Orca-Archon Integration

Git hooks that enforce the Orca-Archon Hybrid workflow and automate quality checks.

## Quick Start

### Activate Hooks (One-time Setup)
```bash
git config core.hooksPath .githooks
```

### Verify Activation
```bash
git config --get core.hooksPath
# Should output: .githooks
```

## Available Hooks

| Hook | Purpose | When It Runs |
|------|---------|--------------|
| `prepare-commit-msg` | Auto-populate TASK-XXX | Before commit editor opens |
| `commit-msg` | Validate commit message | After commit message entered |
| `pre-commit` | Quality checks | Before commit is created |
| `pre-push` | Full quality suite | Before push to remote |
| `post-checkout` | Display task info | After switching branches |
| `post-merge` | Suggest status update | After merge completes |

## Hook Descriptions

### 1. prepare-commit-msg
- Extracts TASK-XXX from branch name
- Pre-fills commit message template
- Adds TASK-XXX automatically

### 2. commit-msg
**Validates:**
- Subject length (max 72 chars)
- TASK-XXX required for feature/fix/refactor branches
- No period at end
- Message format

### 3. pre-commit
**Runs:**
- Black formatter
- Ruff linter
- MyPy type checker
- Affected tests

### 4. pre-push
**Checks:**
- All commits have TASK-XXX (feature branches)
- Full test suite passes
- Coverage ≥ 80%
- Security scan (Bandit)
- Blocks direct push to main/master

### 5. post-checkout
- Displays TASK-XXX from branch
- Shows task information
- Provides next steps

### 6. post-merge
- Extracts TASK-XXX from merged commit
- Suggests status update
- Provides post-merge actions

## Bypassing Hooks

Only in emergencies:
```bash
git commit --no-verify
git push --no-verify
```

## Troubleshooting

### Hook Not Running
```bash
# Activate hooks
git config core.hooksPath .githooks

# Make executable
chmod +x .githooks/*
```

### TASK-XXX Required Error
```bash
# Add TASK-XXX to message
git commit -m "feat(TASK-XXX): Your change"

# Or use docs/chore prefix
git commit -m "docs: Update documentation"
```

## Related Documentation

- [Complete Workflow](../.github/WORKFLOW.md)
- [Quick Reference](../.github/QUICK_REFERENCE.md)
- [Helper Scripts](../scripts/git-helpers/README.md)

---

🤖 _Git hooks for Orca-Archon Hybrid workflow_

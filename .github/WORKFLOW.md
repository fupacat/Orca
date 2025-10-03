# Orca-Archon Hybrid Git Workflow

Complete guide to the integrated Git and Archon task management workflow for the Orca project.

## 📋 Table of Contents
- [Overview](#overview)
- [Branch Structure](#branch-structure)
- [Daily Workflow](#daily-workflow)
- [Branch Naming Convention](#branch-naming-convention)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Task Status Flow](#task-status-flow)
- [Automation & Hooks](#automation--hooks)
- [VSCode Integration](#vscode-integration)
- [Quick Reference](#quick-reference)

---

## Overview

The Orca-Archon Hybrid workflow combines:
- **GitHub Flow** simplicity (main + develop + feature branches)
- **Archon MCP** task tracking integration
- **TASK-XXX** references for complete traceability

### Key Principles
1. **Task-Driven Development** - All features start from Archon tasks
2. **Branch = Task** - One branch per TASK-XXX
3. **Traceability** - TASK-XXX in branch → commits → PR
4. **Quality Gates** - Automated checks before merge
5. **Status Automation** - Git operations update Archon

---

## Branch Structure

```
main (production)
 ↓
develop (integration) ← Default branch
 ↓
feature/TASK-XXX-description
fix/TASK-XXX-description
refactor/TASK-XXX-description
hotfix/TASK-XXX-description
```

### Protected Branches
- **`main`** - Production code only, strict protection
- **`develop`** - Integration branch, medium protection

### Branch Protection Rules
- Require pull request reviews (1 reviewer)
- Require status checks to pass
- No force pushes
- No deletions
- Dismiss stale PR approvals on new commits

---

## Daily Workflow

### 1. Start New Feature

**Option A: Using Helper Script** ⭐ Recommended
```bash
./scripts/git-helpers/create-feature-branch.sh

# Or with VSCode
Ctrl+Shift+A T
```

**Option B: Manual**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/TASK-005-parallel-orchestration
```

**What happens:**
- ✓ Branch created from latest `develop`
- ✓ TASK-XXX embedded in branch name
- ✓ (Future) Archon task updated to "doing"
- ✓ Git hooks activated for this task

### 2. Code and Commit

```bash
# Make changes
vim src/execution/orchestrator.py

# Commit with TASK-XXX
git add .
git commit -m "feat(TASK-005): Add parallel task orchestration"

# Continue working
git commit -m "feat(TASK-005): Implement load balancing"
git commit -m "test(TASK-005): Add orchestration tests"
```

**Auto-magic:**
- ✓ `prepare-commit-msg` hook auto-adds TASK-XXX
- ✓ `commit-msg` hook validates format
- ✓ Quality checks run on commit

### 3. Push and Create PR

**Option A: Using Helper Script** ⭐ Recommended
```bash
./scripts/git-helpers/finish-feature.sh

# Or with VSCode
Ctrl+Shift+A F
```

**Option B: Manual**
```bash
git push -u origin feature/TASK-005-parallel-orchestration
gh pr create --title "TASK-005: Parallel Orchestration" \
             --body-file .github/pull_request_template.md \
             --base develop
```

**What happens:**
- ✓ `pre-push` hook validates TASK-XXX in all commits
- ✓ Branch pushed to GitHub
- ✓ PR created with auto-filled template
- ✓ GitHub Actions validate TASK-XXX
- ✓ (Future) Archon task updated to "review"

### 4. Code Review & Merge

1. **Review:** Team reviews PR
2. **CI/CD:** All checks must pass
3. **Approve:** Reviewer approves
4. **Merge:** Merge via GitHub (squash or merge commit)
5. **Cleanup:** Feature branch auto-deleted

**What happens after merge:**
- ✓ Code merged to `develop`
- ✓ `post-merge` hook suggests status update
- ✓ (Future) Archon task updated to "done"
- ✓ Version snapshot created in Archon

### 5. Release to Production

```bash
# When ready to release
git checkout main
git merge develop
git tag -a v1.2.0 -m "Release 1.2.0"
git push origin main --tags
```

**What happens:**
- ✓ Changes deployed to production
- ✓ Tagged with version number
- ✓ (Future) Archon version snapshot created

---

## Branch Naming Convention

### Format
```
<type>/TASK-XXX-<description>
```

### Types
- **`feature/`** - New features
- **`fix/`** - Bug fixes
- **`refactor/`** - Code refactoring
- **`hotfix/`** - Urgent production fixes
- **`docs/`** - Documentation only (no TASK required)
- **`chore/`** - Maintenance tasks (no TASK required)

### Examples
✅ **Good:**
```
feature/TASK-005-parallel-orchestration
fix/TASK-012-parser-memory-leak
refactor/TASK-023-simplify-config
hotfix/TASK-089-critical-security-patch
docs/update-api-documentation
```

❌ **Bad:**
```
feature/add-stuff (no TASK-XXX)
TASK-005 (no type or description)
feature/TASK-5-thing (wrong TASK format, must be 3 digits)
my-feature-branch (no TASK-XXX)
```

### Validation
- ✅ Enforced by `post-checkout` hook
- ✅ Validated by GitHub Actions
- ✅ Checked by branch protection rules

---

## Commit Message Format

### Convention
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting (no code change)
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance

### Scope
**Must include TASK-XXX** for feature/fix/refactor commits:
```
feat(TASK-005): Add parallel orchestration
fix(TASK-012): Resolve memory leak in parser
```

### Subject
- Use imperative mood ("Add" not "Added")
- No period at end
- Max 50 characters
- Be concise but descriptive

### Body (Optional)
- Explain *why*, not *what*
- Wrap at 72 characters
- Separate from subject with blank line

### Footer (Optional)
```
BREAKING CHANGE: Describe breaking changes
Closes #123
References TASK-005
```

### Examples

✅ **Good:**
```
feat(TASK-005): Add parallel task orchestration

Implement multi-agent coordination with load balancing.
Supports aggressive, conservative, and hybrid strategies.

Closes #42
References TASK-005
```

```
fix(TASK-012): Resolve memory leak in plan parser

Parser was not releasing references to completed tasks,
causing memory growth over long sessions.
```

```
docs: Update API documentation for v1.2.0
```

❌ **Bad:**
```
Added stuff (no type, no TASK-XXX, past tense, vague)
feat: new feature (no TASK-XXX for feature)
TASK-005 (no type or message)
feat(TASK-005): Added parallel orchestration. (period at end)
```

### Validation
- ✅ `commit-msg` hook enforces format
- ✅ `pre-push` hook validates TASK-XXX
- ✅ GitHub Actions check format
- ✅ Length limits enforced

---

## Pull Request Process

### 1. Create PR

**Using Script:**
```bash
./scripts/git-helpers/finish-feature.sh
```

**Manually:**
```bash
gh pr create --title "TASK-005: Parallel Orchestration" \
             --body-file /tmp/pr_body.md \
             --base develop
```

### 2. PR Template

PRs use `.github/pull_request_template.md` which includes:

- ✅ **Archon Task Reference** - TASK-XXX, status, feature
- ✅ **Description** - What changed and why
- ✅ **Testing** - Test coverage, manual testing
- ✅ **Quality Gates** - Code quality checklist
- ✅ **Architecture** - Design decisions, breaking changes
- ✅ **Review Focus** - Guide reviewers

### 3. Required Checks

**Automatic (GitHub Actions):**
- ✅ TASK-XXX validation
- ✅ Commit message format
- ✅ Branch naming convention
- ✅ Tests pass
- ✅ Coverage ≥ 80%
- ✅ Linting clean
- ✅ Type checking passed
- ✅ Security scan clean

**Manual (Reviewer):**
- ✅ Code review
- ✅ Architecture review
- ✅ Documentation review

### 4. Merge Requirements

Before merging, ensure:
1. ✅ All CI checks pass
2. ✅ At least 1 approval
3. ✅ No unresolved comments
4. ✅ Branch up-to-date with `develop`
5. ✅ Archon task ready for completion

### 5. Merge Strategy

**Preferred:** Squash and Merge
- Keeps `develop` history clean
- Single commit per feature
- TASK-XXX preserved in commit message

**Alternative:** Merge Commit (for complex features)
- Preserves detailed commit history
- Useful for large features
- All commits must have TASK-XXX

### 6. Post-Merge

**Automatic:**
- ✅ Feature branch deleted
- ✅ `post-merge` hook triggered
- ✅ (Future) Archon task updated to "done"

**Manual:**
- ✅ Update Archon task if needed
- ✅ Notify team of completion
- ✅ Close related issues

---

## Task Status Flow

### Status Progression
```
todo → doing → review → done
```

### Status Meanings

**`todo`** - Task not started
- Created in Archon
- Waiting to be picked up
- In backlog

**`doing`** - Task in progress
- Branch created
- Actively coding
- Commits being made

**`review`** - Ready for review
- PR created
- All tests passing
- Awaiting team review

**`done`** - Task completed
- PR merged
- Code in `develop`
- Task finished

### Update Triggers

**Manual:**
```bash
./scripts/git-helpers/sync-task-status.sh TASK-005 doing
# Or: Ctrl+Shift+A U
```

**Automatic (Future):**
- Branch checkout → `doing`
- PR creation → `review`
- PR merge to develop → `review`
- PR merge to main → `done`

### Archon Integration

Tasks are managed in Archon MCP:
```bash
# List tasks
mcp__archon__find_tasks(filter_by="status", filter_value="todo")

# Get specific task
mcp__archon__find_tasks(task_id="TASK-005")

# Update status
mcp__archon__manage_task("update", task_id="TASK-005", status="doing")
```

---

## Automation & Hooks

### Git Hooks (`.githooks/`)

**`prepare-commit-msg`** - Auto-add TASK-XXX
- Extracts TASK-XXX from branch name
- Pre-fills commit message template
- Suggests commit format

**`commit-msg`** - Validate commit message
- Enforces TASK-XXX for feature branches
- Checks message format
- Validates length limits
- Ensures imperative mood

**`pre-commit`** - Quality checks before commit
- Run Black formatter
- Run Ruff linter
- Run MyPy type checker
- Run affected tests

**`pre-push`** - Full quality suite before push
- Verify TASK-XXX in all commits
- Run full test suite
- Check coverage ≥ 80%
- Security scan with Bandit
- Block direct push to main/master

**`post-checkout`** - On branch switch
- Display TASK-XXX from branch
- Show task information
- (Future) Update Archon status to "doing"

**`post-merge`** - After merge
- Extract TASK-XXX from merged commit
- Suggest status update
- (Future) Auto-update Archon task

### Activate Hooks
```bash
git config core.hooksPath .githooks
```

### GitHub Actions (`.github/workflows/`)

**`archon-integration.yml`** - Archon workflow validation
- Validate TASK-XXX in PR
- Check commit messages
- Validate branch naming
- Auto-label PRs
- Post test results
- Check branch sync

**`testing.yml`** - Comprehensive testing
- Unit tests
- Integration tests
- Performance tests
- Security tests
- Cross-platform testing

---

## VSCode Integration

### Tasks (`Ctrl+Shift+P` → Tasks: Run Task)

**Git Tasks:**
- Git: View Status
- Git: View Diff
- Git: View Log (Graph)
- Git: Stage All Changes
- Git: Commit with Pre-commit Checks
- Git: Push Current Branch
- Git: Pull with Rebase

**Archon Tasks:**
- Archon: Create Branch from Task
- Archon: View Task Details
- Archon: Update Task Status
- Archon: Finish Feature (Create PR)
- Archon: Extract TASK-XXX from Branch

**Quality Tasks:**
- Run Tests with Coverage
- Full Quality Check
- Format Code (Black)
- Lint Code (Ruff)
- Type Check (MyPy)

### Keyboard Shortcuts

**Git Operations** - `Ctrl+Shift+G`:
| Key | Action |
|-----|--------|
| `G` | Source Control panel |
| `S` | View Status |
| `D` | View Diff |
| `L` | View Log |
| `A` | Stage All |
| `C` | Commit with Checks |
| `P` | Push |
| `U` | Pull (rebase) |

**Archon Operations** - `Ctrl+Shift+A`:
| Key | Action |
|-----|--------|
| `T` | Create Branch from Task |
| `V` | View Task Details |
| `U` | Update Task Status |
| `F` | Finish Feature (Create PR) |
| `X` | Extract TASK-XXX |

**Quality Operations** - `Ctrl+Shift+T`:
| Key | Action |
|-----|--------|
| `T` | Run Tests |
| `Q` | Full Quality Check |
| `F` | Format Code |
| `L` | Lint Code |
| `M` | Type Check |

---

## Quick Reference

### Starting a Feature
```bash
# 1. Create branch from Archon task
./scripts/git-helpers/create-feature-branch.sh
# Or: Ctrl+Shift+A T

# 2. Code and commit
git commit -m "feat(TASK-005): Your change"

# 3. Push and create PR
./scripts/git-helpers/finish-feature.sh
# Or: Ctrl+Shift+A F
```

### Common Commands
```bash
# Status
git status

# View TASK-XXX
git rev-parse --abbrev-ref HEAD | grep -o 'TASK-[0-9]\{3\}'

# Update task status
./scripts/git-helpers/sync-task-status.sh TASK-005 doing
# Or: Ctrl+Shift+A U

# Rebase on develop
git checkout develop && git pull
git checkout feature/TASK-005-name
git rebase develop

# Force push after rebase
git push --force-with-lease
```

### Troubleshooting
```bash
# Fix commit without TASK-XXX
git commit --amend

# Fix multiple commits
git rebase -i HEAD~N

# Rename branch
git branch -m feature/TASK-005-better-name

# Skip hook temporarily (not recommended)
git commit --no-verify
```

---

## 📚 Additional Resources

- [Quick Reference](.github/QUICK_REFERENCE.md) - Cheat sheet
- [Scripts README](../scripts/git-helpers/README.md) - Helper scripts guide
- [Git Integration](.vscode/GIT_INTEGRATION.md) - VSCode Git setup
- [Hooks README](../.githooks/README.md) - Git hooks documentation
- [CLAUDE.md](../CLAUDE.md) - Project overview

---

🤖 _Generated with [Claude Code](https://claude.com/claude-code)_

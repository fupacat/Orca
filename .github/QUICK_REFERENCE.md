# Orca-Archon Workflow - Quick Reference

One-page cheat sheet for daily development.

## 🚀 Daily Workflow

```bash
# 1. Start feature
./scripts/git-helpers/create-feature-branch.sh  # OR: Ctrl+Shift+A T

# 2. Code + commit
git commit -m "feat(TASK-XXX): Your change"

# 3. Create PR
./scripts/git-helpers/finish-feature.sh          # OR: Ctrl+Shift+A F
```

---

## 🌳 Branch Format

```
<type>/TASK-XXX-<description>

Examples:
  feature/TASK-005-parallel-orchestration
  fix/TASK-012-memory-leak
  refactor/TASK-023-simplify-config
  hotfix/TASK-089-security-patch
```

**Types:** `feature`, `fix`, `refactor`, `hotfix`, `docs`, `chore`

---

## 💬 Commit Format

```
<type>(TASK-XXX): <subject>

Examples:
  feat(TASK-005): Add parallel orchestration
  fix(TASK-012): Resolve memory leak
  docs: Update API documentation
  test(TASK-005): Add orchestration tests
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Rules:**
- Imperative mood ("Add" not "Added")
- Subject ≤ 50 chars
- No period at end
- TASK-XXX required for feature/fix/refactor

---

## ⌨️ VSCode Shortcuts

### Git Operations (`Ctrl+Shift+G`)
| Key | Action |
|-----|--------|
| `G` | Source Control |
| `S` | Status |
| `D` | Diff |
| `L` | Log |
| `C` | Commit |
| `P` | Push |

### Archon Operations (`Ctrl+Shift+A`)
| Key | Action |
|-----|--------|
| `T` | Create Branch |
| `U` | Update Status |
| `F` | Finish Feature |
| `V` | View Task |
| `X` | Extract TASK |

### Quality (`Ctrl+Shift+T`)
| Key | Action |
|-----|--------|
| `T` | Run Tests |
| `Q` | Quality Check |
| `F` | Format |
| `L` | Lint |
| `M` | Type Check |

---

## 📋 Task Status Flow

```
todo → doing → review → done
```

**Update status:**
```bash
./scripts/git-helpers/sync-task-status.sh TASK-XXX doing
# OR: Ctrl+Shift+A U
```

---

## 🔧 Common Commands

```bash
# View current TASK
git rev-parse --abbrev-ref HEAD | grep -o 'TASK-[0-9]\{3\}'

# Rebase on develop
git checkout develop && git pull
git checkout - && git rebase develop

# Force push after rebase
git push --force-with-lease

# Fix last commit
git commit --amend

# Fix multiple commits
git rebase -i HEAD~N

# Activate git hooks
git config core.hooksPath .githooks
```

---

## ✅ PR Checklist

Before creating PR:
- [ ] All commits have TASK-XXX
- [ ] Tests pass
- [ ] Coverage ≥ 80%
- [ ] Code formatted (Black)
- [ ] Linting clean (Ruff)
- [ ] Type checking passed (MyPy)
- [ ] Branch rebased on develop
- [ ] No merge conflicts

---

## 🐛 Troubleshooting

**No TASK-XXX in branch:**
```bash
git branch -m feature/TASK-XXX-description
```

**Commit missing TASK-XXX:**
```bash
git commit --amend  # Fix last commit
git rebase -i HEAD~N  # Fix older commits
```

**Hook blocks commit:**
```bash
# Fix the issue, don't skip hooks!
# Only use --no-verify in emergencies
```

**Branch behind develop:**
```bash
git rebase origin/develop
git push --force-with-lease
```

---

## 📚 Full Documentation

- [Complete Workflow](.github/WORKFLOW.md)
- [Helper Scripts](../scripts/git-helpers/README.md)
- [VSCode Integration](.vscode/GIT_INTEGRATION.md)
- [Git Hooks](../.githooks/README.md)

---

🤖 _Quick reference for Orca-Archon Hybrid Git Workflow_

# Git Helper Scripts - Orca-Archon Integration

These scripts streamline the Orca-Archon Hybrid Git workflow by providing interactive CLI tools for common tasks.

## 📋 Available Scripts

### 1. `create-feature-branch.sh`
**Purpose:** Create a new feature branch from an Archon task

**Usage:**
```bash
# Interactive mode
./scripts/git-helpers/create-feature-branch.sh

# With arguments
./scripts/git-helpers/create-feature-branch.sh TASK-005 "parallel-orchestration"
```

**What it does:**
1. Ensures you're on `develop` branch
2. Prompts for TASK-XXX ID
3. Prompts for branch description
4. Lets you choose branch type (feature/fix/refactor/hotfix)
5. Creates branch with format: `<type>/TASK-XXX-<description>`
6. (Future) Updates Archon task status to "doing"

**Example:**
```bash
$ ./create-feature-branch.sh
> Enter TASK ID: TASK-005
> Enter description: parallel orchestration
> Choose type: 1 (feature)
✓ Created: feature/TASK-005-parallel-orchestration
```

**VSCode Integration:**
- Task: "Archon: Create Branch from Task"
- Shortcut: `Ctrl+Shift+A T`

---

### 2. `finish-feature.sh`
**Purpose:** Complete a feature and create a pull request

**Usage:**
```bash
# Run from your feature branch
./scripts/git-helpers/finish-feature.sh
```

**What it does:**
1. Validates you're on a feature branch
2. Checks for uncommitted changes
3. Pushes branch to remote if needed
4. Checks if branch is behind `develop`
5. Offers to rebase if needed
6. Generates PR title from branch name
7. Creates PR body from commits
8. Creates GitHub PR using `gh` CLI
9. (Future) Updates Archon task status to "review"

**Pre-requisites:**
- GitHub CLI (`gh`) installed and authenticated
- All changes committed

**Example:**
```bash
$ ./finish-feature.sh
✓ No uncommitted changes
✓ Branch up-to-date
✓ PR Title: TASK-005: Parallel orchestration
✓ PR created: https://github.com/user/orca/pull/42
```

**VSCode Integration:**
- Task: "Archon: Finish Feature (Create PR)"
- Shortcut: `Ctrl+Shift+A F`

---

### 3. `sync-task-status.sh`
**Purpose:** Manually sync Archon task status

**Usage:**
```bash
# Interactive mode
./scripts/git-helpers/sync-task-status.sh

# With arguments
./scripts/git-helpers/sync-task-status.sh TASK-005 doing
```

**What it does:**
1. Extracts TASK-XXX from current branch (if available)
2. Prompts for task status (todo/doing/review/done)
3. (Future) Updates Archon task via MCP
4. Provides guidance for manual update

**Status Options:**
- `todo` - Task not started
- `doing` - Task in progress
- `review` - Task completed, awaiting review
- `done` - Task fully completed

**Example:**
```bash
$ ./sync-task-status.sh
✓ Found task in branch: TASK-005
> Select status: 2 (doing)
✓ Task TASK-005 updated to 'doing'
```

**VSCode Integration:**
- Task: "Archon: Update Task Status"
- Shortcut: `Ctrl+Shift+A U`

---

## 🚀 Quick Start

### Installation
All scripts are already executable. No additional setup needed.

### Add to PATH (Optional)
For system-wide access:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/Orca/scripts/git-helpers"

# Now you can run from anywhere
create-feature-branch.sh
```

---

## 🔗 Integration with VSCode

All scripts are integrated into VSCode tasks and keyboard shortcuts.

**VSCode Tasks Menu:**
- `Ctrl+Shift+P` → "Tasks: Run Task"
- Filter by "Archon:"

**Keyboard Shortcuts:**
| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+A T` | Create Branch from Task |
| `Ctrl+Shift+A U` | Update Task Status |
| `Ctrl+Shift+A F` | Finish Feature (Create PR) |
| `Ctrl+Shift+A V` | View Task Details |
| `Ctrl+Shift+A X` | Extract TASK-XXX from Branch |

---

## 🔧 Customization

### Modify Branch Types
Edit `create-feature-branch.sh` to add custom branch types:

```bash
# Add new type
5)
    BRANCH_TYPE="experimental"
    ;;
```

### Change PR Template
Edit `finish-feature.sh` to customize the PR body:

```bash
PR_BODY="Your custom template..."
```

### Add Archon CLI Integration
When Archon CLI becomes available, uncomment the MCP integration sections:

```bash
# Uncomment this block
# if command -v claude >/dev/null 2>&1; then
#     claude mcp archon manage_task update --task-id "$TASK_ID" --status doing
# fi
```

---

## 📚 Workflow Example

### Complete Feature Development Cycle

```bash
# 1. Start new feature
./create-feature-branch.sh
# Creates: feature/TASK-005-parallel-orchestration

# 2. Code and commit (repeatedly)
git add .
git commit -m "feat(TASK-005): Add orchestration engine"
git commit -m "feat(TASK-005): Add load balancing"
git commit -m "test(TASK-005): Add orchestration tests"

# 3. Update task status (optional)
./sync-task-status.sh TASK-005 review

# 4. Create pull request
./finish-feature.sh
# Creates PR with TASK-005 reference

# 5. After PR is merged, task auto-updated to 'done'
```

---

## 🐛 Troubleshooting

### "Not in a git repository"
**Solution:** Run scripts from within the Orca repository directory.

### "GitHub CLI (gh) not installed"
**Solution:** Install GitHub CLI:
```bash
# Windows (Scoop)
scoop install gh

# macOS
brew install gh

# Linux
See: https://cli.github.com/
```

### "Branch name doesn't follow convention"
**Cause:** Branch created manually without TASK-XXX
**Solution:** Use `create-feature-branch.sh` or rename branch:
```bash
git branch -m feature/TASK-XXX-description
```

### "TASK-XXX not found in commit messages"
**Cause:** Commits don't reference the task
**Solution:** Amend commits to include TASK-XXX:
```bash
git rebase -i HEAD~N
# Edit commit messages to include TASK-XXX
```

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Direct Archon MCP CLI integration (when available)
- [ ] Auto-fetch task details from Archon on branch creation
- [ ] Auto-update task status on git operations
- [ ] Task dependency validation
- [ ] Automated task time tracking
- [ ] Integration with GitHub Projects

### Archon CLI Integration
These scripts are designed for future Archon CLI integration. When available, they will:

1. **Fetch Task Details:**
   ```bash
   claude mcp archon find_tasks --task-id "TASK-005"
   ```

2. **Update Task Status:**
   ```bash
   claude mcp archon manage_task update --task-id "TASK-005" --status "doing"
   ```

3. **Create Version Snapshots:**
   ```bash
   claude mcp archon manage_version create --project-id "$PROJECT_ID" \
       --field-name "implementation" --change-summary "Completed TASK-005"
   ```

---

## 📖 Related Documentation

- [.github/WORKFLOW.md](.github/WORKFLOW.md) - Complete workflow guide
- [.github/QUICK_REFERENCE.md](.github/QUICK_REFERENCE.md) - Cheat sheet
- [.vscode/GIT_INTEGRATION.md](.vscode/GIT_INTEGRATION.md) - VSCode Git integration
- [.githooks/README.md](.githooks/README.md) - Git hooks documentation
- [CLAUDE.md](../../CLAUDE.md) - Project overview

---

## 💡 Tips

1. **Always start with `create-feature-branch.sh`**
   - Ensures correct naming convention
   - Reduces manual errors

2. **Commit frequently with TASK-XXX**
   - Makes it easier to track work
   - PR creation is smoother

3. **Use `sync-task-status.sh` for visibility**
   - Keep team informed of progress
   - Helps with Archon project tracking

4. **Run `finish-feature.sh` early to test**
   - Can create draft PRs
   - Get early feedback

5. **Rebase before creating PR**
   - `finish-feature.sh` offers this
   - Keeps history clean

---

🤖 _Generated with [Claude Code](https://claude.com/claude-code)_

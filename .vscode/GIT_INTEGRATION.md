# Git IDE Integration Guide

This document describes the Git integration configured for the Orca project in VSCode.

## 📋 Table of Contents
- [Extension Recommendations](#extension-recommendations)
- [IDE Settings](#ide-settings)
- [Tasks](#tasks)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Source Control Panel](#source-control-panel)
- [GitLens Features](#gitlens-features)
- [Workflows](#workflows)

## 🧩 Extension Recommendations

The following Git-related extensions are recommended (install via Extensions panel):

### Core Git Extensions
- **GitLens** (`eamodio.gitlens`) - Supercharge Git capabilities
  - Inline blame annotations
  - File history
  - Commit search and comparison
  - Repository insights

- **Git Graph** (`mhutchie.git-graph`) - Visual commit graph
  - Interactive branch visualization
  - Commit details and comparisons
  - Branch management

- **Git History** (`donjayamanne.githistory`) - View and search git log
  - File history with diff
  - Branch comparison
  - Commit search

- **GitHub Pull Requests** (`github.vscode-pull-request-github`) - GitHub integration
  - Review PRs in VS Code
  - Create and merge PRs
  - Comment on code

## ⚙️ IDE Settings

### Git Configuration (`.vscode/settings.json`)

```json
// Core Git Settings
"git.autofetch": true                    // Auto-fetch every 3 minutes
"git.autofetchPeriod": 180              // Fetch interval
"git.rebaseWhenSync": true              // Use rebase instead of merge
"git.pruneOnFetch": true                // Remove stale remote branches
"git.fetchOnPull": true                 // Always fetch before pull
"git.pullBeforeCheckout": true          // Pull before switching branches
"git.enableSmartCommit": true           // Auto-stage all changes
"git.untrackedChanges": "separate"      // Show untracked files separately
"git.showPushSuccessNotification": true // Notify on successful push

// Branch Protection
"git.branchProtection": ["main", "master"]
"git.branchProtectionPrompt": "alwaysPrompt"

// Commit Message Validation
"git.inputValidationLength": 72         // Max commit message length
"git.inputValidationSubjectLength": 50  // Max subject line length

// GitLens Configuration
"gitlens.currentLine.enabled": true     // Show blame on current line
"gitlens.codeLens.enabled": true        // Show authorship inline
"gitlens.blame.highlight.enabled": true // Highlight blamed line
```

## 📝 Tasks

Access these tasks via **Terminal → Run Task** or keyboard shortcuts.

### Git Tasks

| Task | Description | Shortcut |
|------|-------------|----------|
| **Git: View Status** | Show working tree status | `Ctrl+Shift+G S` |
| **Git: View Diff** | Show changes since last commit | `Ctrl+Shift+G D` |
| **Git: View Log (Graph)** | Show commit history graph | `Ctrl+Shift+G L` |
| **Git: Stage All Changes** | Stage all modified files | `Ctrl+Shift+G A` |
| **Git: Commit with Pre-commit Checks** | Run quality checks, then commit | `Ctrl+Shift+G C` |
| **Git: Create Branch** | Create and checkout new branch | `Ctrl+Shift+G B` |
| **Git: Push Current Branch** | Push branch to remote | `Ctrl+Shift+G P` |
| **Git: Pull with Rebase** | Pull and rebase on top | `Ctrl+Shift+G U` |
| **Git: Fetch All** | Fetch from all remotes | `Ctrl+Shift+G F` |

### Quality Tasks

| Task | Description | Shortcut |
|------|-------------|----------|
| **Run Tests with Coverage** | Run pytest with coverage report | `Ctrl+Shift+T T` |
| **Full Quality Check** | Run all quality checks | `Ctrl+Shift+T Q` |
| **Format Code (Black)** | Auto-format Python code | `Ctrl+Shift+T F` |
| **Lint Code (Ruff)** | Run linter | `Ctrl+Shift+T L` |
| **Type Check (MyPy)** | Run type checker | `Ctrl+Shift+T M` |

## ⌨️ Keyboard Shortcuts

All Git shortcuts follow the pattern `Ctrl+Shift+G <key>`:

```
Ctrl+Shift+G → Git Operations Menu
├─ G → Open Source Control Panel
├─ S → View Status
├─ D → View Diff
├─ L → View Log (Graph)
├─ A → Stage All Changes
├─ C → Commit with Checks
├─ B → Create Branch
├─ P → Push
├─ U → Pull (with rebase)
├─ F → Fetch All
├─ H → Toggle File Blame (GitLens)
├─ R → Show File History (GitLens)
├─ M → Show Commit Details (GitLens)
└─ V → Open Git Graph
```

Quality shortcuts use `Ctrl+Shift+T <key>`:

```
Ctrl+Shift+T → Testing/Quality Menu
├─ T → Run Tests with Coverage
├─ Q → Full Quality Check
├─ F → Format Code
├─ L → Lint Code
└─ M → Type Check
```

## 🎯 Source Control Panel

Open with `Ctrl+Shift+G G` or click the Source Control icon.

### Panel Features
- **Changes**: Modified files (not staged)
- **Staged Changes**: Files ready to commit
- **Merge Changes**: Files with conflicts
- **Untracked Files**: New files (shown separately)

### Panel Actions
- **Stage File**: Click `+` next to file
- **Unstage File**: Click `−` next to file
- **Discard Changes**: Click `↶` next to file
- **View Diff**: Click on file name
- **Commit**: Enter message and click `✓`

### Timeline View
- Shows file history in bottom panel
- Click timestamp to see commit details
- Right-click for options (compare, restore)

## 🔍 GitLens Features

### Inline Blame
Shows author and date for current line:
```
│ John Doe, 2 days ago • Implement feature X
```

Toggle: `Ctrl+Shift+G H`

### Code Lens
Shows authorship and recent changes above functions/classes:
```
◎ John Doe, 2 days ago  ∙  3 authors
def my_function():
```

### File History
View complete file history:
1. Press `Ctrl+Shift+G R`
2. Select commit to compare
3. View side-by-side diff

### Commit Details
View full commit information:
1. Press `Ctrl+Shift+G M`
2. See commit message, files changed, diff

### Hovers
Hover over any line to see:
- Blame information
- Commit message
- Quick actions (compare, copy SHA)

## 🔄 Workflows

### Daily Development Workflow

```bash
# 1. Start of day - sync with remote
Ctrl+Shift+G F    # Fetch all
Ctrl+Shift+G U    # Pull with rebase

# 2. Create feature branch
Ctrl+Shift+G B    # Create branch: feature/my-feature

# 3. Make changes, then check status
Ctrl+Shift+G S    # View status
Ctrl+Shift+G D    # View diff

# 4. Stage and commit
Ctrl+Shift+G A    # Stage all
Ctrl+Shift+G C    # Commit with quality checks

# 5. Push changes
Ctrl+Shift+G P    # Push to remote
```

### Pre-Commit Workflow

When using `Git: Commit with Pre-commit Checks` task:

1. **Format Code** - Black auto-formats Python files
2. **Lint Code** - Ruff checks for code issues
3. **Type Check** - MyPy validates type hints
4. **Run Tests** - Pytest with coverage report
5. **Commit** - Opens commit message editor

If any check fails, commit is aborted.

### Branch Management

```bash
# Create feature branch
Ctrl+Shift+G B → "feature/new-feature"

# View all branches in graph
Ctrl+Shift+G V

# Switch branches (via Source Control panel)
Ctrl+Shift+G G → Click branch name in status bar

# Merge via Git Graph
Ctrl+Shift+G V → Right-click branch → Merge into current branch
```

### Review Changes Before Commit

```bash
# 1. Check what changed
Ctrl+Shift+G S    # Status

# 2. View diffs
Ctrl+Shift+G D    # Full diff
# Or click files in Source Control panel for side-by-side

# 3. Check file history
Ctrl+Shift+G R    # File history (GitLens)

# 4. View line blame
Ctrl+Shift+G H    # Toggle blame annotations
```

### Resolving Conflicts

1. Pull and see conflicts:
   ```bash
   Ctrl+Shift+G U    # Pull (conflicts appear)
   ```

2. Open Source Control panel:
   ```bash
   Ctrl+Shift+G G
   ```

3. Click conflicted file - opens 3-way merge editor

4. Resolve conflicts, then:
   ```bash
   Ctrl+Shift+G A    # Stage resolved files
   Ctrl+Shift+G C    # Commit merge
   ```

### Creating Pull Requests (GitHub Extension)

1. Ensure GitHub extension is installed
2. Push branch: `Ctrl+Shift+G P`
3. Open Command Palette: `Ctrl+Shift+P`
4. Type: "GitHub Pull Requests: Create Pull Request"
5. Fill in title and description
6. Select reviewers and labels
7. Create PR

## 🔗 Integration with Git Hooks

The project has `.githooks/` directory with quality automation:

- **pre-commit** - Runs Black, Ruff, MyPy, tests
- **commit-msg** - Validates commit message format
- **pre-push** - Full quality suite before push

Activate hooks:
```bash
git config core.hooksPath .githooks
```

The `Git: Commit with Pre-commit Checks` task provides similar functionality within the IDE.

## 📚 Additional Resources

- [GitLens Documentation](https://github.com/gitkraken/vscode-gitlens#readme)
- [Git Graph Documentation](https://github.com/mhutchie/vscode-git-graph#readme)
- [VSCode Git Documentation](https://code.visualstudio.com/docs/sourcecontrol/overview)
- [GitHub PR Extension](https://github.com/microsoft/vscode-pull-request-github#readme)

## 💡 Tips

1. **Use Git Graph for visualization** - Much easier than command line for complex branch history
2. **Enable GitLens blame** - See authorship at a glance
3. **Use keyboard shortcuts** - Faster than clicking through menus
4. **Stage files selectively** - Click `+` on individual files in Source Control panel
5. **Review diffs before committing** - Always check what you're committing
6. **Use quality checks task** - Catch issues before committing
7. **Create descriptive branch names** - Use prefixes: `feature/`, `fix/`, `refactor/`
8. **Commit frequently** - Small, focused commits are easier to review and revert

## 🐛 Troubleshooting

### GitLens not showing blame
- Check: Settings → Search "gitlens.currentLine.enabled" → Should be `true`
- Restart VSCode

### Git tasks not appearing
- Check: `.vscode/tasks.json` exists
- Restart VSCode

### Keyboard shortcuts not working
- Check: `.vscode/keybindings.json` exists
- May conflict with other extensions - customize as needed

### Fetch/Pull failing
- Check Git credentials: `git config --list`
- Ensure remote URL is correct: `git remote -v`
- Try manually: Open terminal and run `git fetch`

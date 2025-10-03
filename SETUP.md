# Orca-Archon Hybrid Workflow Setup

Complete setup guide for the Orca-Archon Hybrid Git workflow.

## 📋 Prerequisites

### Required
- ✅ Git installed and configured
- ✅ Python 3.11+ installed
- ✅ GitHub CLI (`gh`) installed and authenticated
- ✅ Archon MCP server running (http://localhost:8051/mcp)
- ✅ Serena MCP server configured

### Recommended
- ✅ VSCode (for IDE integration)
- ✅ Bash/Zsh shell (for helper scripts)

---

## 🚀 Quick Setup (5 minutes)

### 1. Clone Repository
```bash
git clone git@github.com:fupacat/Orca.git
cd Orca
```

### 2. Switch to Develop Branch
```bash
git checkout develop
git pull origin develop
```

### 3. Activate Git Hooks
```bash
git config core.hooksPath .githooks
```

### 4. Verify Setup
```bash
# Check hooks are activated
git config --get core.hooksPath
# Should output: .githooks

# Check hooks are executable
ls -la .githooks/
# All files should have 'x' permission
```

### 5. Install VSCode Extensions (Optional)
Open VSCode and install recommended extensions:
- GitLens
- Git Graph
- Git History
- GitHub Pull Requests

**Or install all at once:**
```bash
# View recommendations
code --list-extensions

# Install from .vscode/extensions.json
# VSCode will prompt you automatically
```

### 6. Test the Workflow
```bash
# Try creating a test branch
./scripts/git-helpers/create-feature-branch.sh

# Follow prompts:
# Task ID: TASK-001
# Description: test-setup
# Type: 1 (feature)

# You should now be on: feature/TASK-001-test-setup
```

**That's it! You're ready to use the Orca-Archon workflow.**

---

## 📖 Detailed Setup

### Git Configuration

#### Set User Information
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

#### Configure Commit Template (Optional)
```bash
git config commit.template .gitmessage
```

#### Enable Rebase by Default
```bash
git config pull.rebase true
```

### GitHub CLI Authentication

```bash
# Authenticate with GitHub
gh auth login

# Verify authentication
gh auth status

# Test access to repository
gh repo view fupacat/Orca
```

### Archon MCP Server

Ensure Archon is running:
```bash
# Check Archon health
curl http://localhost:8051/mcp/health

# Should return: {"status": "healthy"}
```

If not running, start Archon:
```bash
# See Archon documentation for startup instructions
```

### Helper Scripts Permissions

Make sure all helper scripts are executable:
```bash
chmod +x scripts/git-helpers/*.sh
chmod +x .githooks/*
```

### Add Scripts to PATH (Optional)

For system-wide access to helper scripts:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:$HOME/projects/Orca/scripts/git-helpers"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc

# Now you can run from anywhere
create-feature-branch.sh
finish-feature.sh
sync-task-status.sh
```

---

## 🎯 VSCode Setup

### Workspace Settings

VSCode is pre-configured with optimal settings in `.vscode/settings.json`.

**Key Features:**
- Auto-format on save (Black)
- Lint on save (Ruff)
- Type checking enabled (MyPy)
- Git integration configured
- Archon task shortcuts

### Keyboard Shortcuts

All shortcuts are pre-configured in `.vscode/keybindings.json`:

**Git Operations** - `Ctrl+Shift+G`:
- `G` - Source Control
- `S` - Status
- `D` - Diff
- `L` - Log
- `C` - Commit
- `P` - Push

**Archon Operations** - `Ctrl+Shift+A`:
- `T` - Create Branch from Task
- `U` - Update Task Status
- `F` - Finish Feature (Create PR)

**Quality Operations** - `Ctrl+Shift+T`:
- `T` - Run Tests
- `Q` - Full Quality Check
- `F` - Format Code

### Tasks

Access pre-configured tasks:
1. `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select task

Or use keyboard shortcuts (see above).

---

## 🧪 Verification Steps

### 1. Test Git Hooks

```bash
# Create test branch
git checkout -b test/hooks-verification

# Try commit without TASK-XXX (should warn)
echo "test" > test.txt
git add test.txt
git commit -m "test commit"

# Should see warning or error about TASK-XXX

# Cleanup
git checkout develop
git branch -D test/hooks-verification
```

### 2. Test Helper Scripts

```bash
# Test create-feature-branch.sh
./scripts/git-helpers/create-feature-branch.sh
# Should prompt for task ID and description

# Test finish-feature.sh (from a feature branch)
git checkout -b feature/TASK-999-test
./scripts/git-helpers/finish-feature.sh
# Should run pre-flight checks

# Cleanup
git checkout develop
git branch -D feature/TASK-999-test
```

### 3. Test VSCode Integration

1. Open VSCode in Orca directory
2. Press `Ctrl+Shift+A T`
3. Should run "Archon: Create Branch from Task" task
4. Press `Ctrl+Shift+T T`
5. Should run tests with coverage

### 4. Test GitHub Actions

Create a test PR to verify GitHub Actions:
```bash
# Create test branch
git checkout -b feature/TASK-999-test-actions
echo "# Test" >> README.md
git add README.md
git commit -m "feat(TASK-999): Test GitHub Actions"
git push -u origin feature/TASK-999-test-actions

# Create PR
gh pr create --title "TASK-999: Test Actions" \
             --body "Testing Archon integration workflow" \
             --base develop

# Check Actions tab on GitHub
# Should see "Orca-Archon Integration" workflow running

# Cleanup
gh pr close --delete-branch
```

---

## 🔧 Troubleshooting

### Hooks Not Running

**Problem:** Commits succeed without running hooks

**Solution:**
```bash
# Re-activate hooks
git config core.hooksPath .githooks

# Verify
git config --get core.hooksPath

# Make executable
chmod +x .githooks/*
```

### Scripts Not Executable

**Problem:** "Permission denied" when running scripts

**Solution:**
```bash
chmod +x scripts/git-helpers/*.sh
chmod +x .githooks/*
```

### GitHub CLI Not Authenticated

**Problem:** `gh` commands fail with authentication error

**Solution:**
```bash
gh auth login
# Follow prompts to authenticate
```

### Archon MCP Server Not Running

**Problem:** Helper scripts can't connect to Archon

**Solution:**
```bash
# Check if Archon is running
curl http://localhost:8051/mcp/health

# If not running, start Archon server
# (See Archon documentation)
```

### VSCode Extensions Not Working

**Problem:** Recommended extensions not installed

**Solution:**
1. Open VSCode
2. Click Extensions icon (or `Ctrl+Shift+X`)
3. Look for "Recommended" section
4. Click "Install Workspace Recommended Extensions"

### Python Dependencies Missing

**Problem:** Pre-commit hooks fail due to missing tools

**Solution:**
```bash
# Install development dependencies
pip install black ruff mypy pytest pytest-cov bandit

# Or from requirements-dev.txt (if exists)
pip install -r requirements-dev.txt
```

---

## 📚 Next Steps

After setup, read these documents:

1. **[QUICK_REFERENCE.md](.github/QUICK_REFERENCE.md)** - One-page cheat sheet
2. **[WORKFLOW.md](.github/WORKFLOW.md)** - Complete workflow guide
3. **[Helper Scripts README](scripts/git-helpers/README.md)** - Scripts documentation

---

## 🎓 Learning Path

### Day 1: Basic Workflow
1. Read QUICK_REFERENCE.md
2. Create your first feature branch
3. Make a commit with TASK-XXX
4. Push and create a test PR

### Day 2: Advanced Features
1. Read complete WORKFLOW.md
2. Try all helper scripts
3. Practice with VSCode shortcuts
4. Review GitHub Actions results

### Day 3: Customization
1. Customize commit message template
2. Add your own VSCode tasks
3. Configure git aliases
4. Optimize for your workflow

---

## 💡 Tips for New Users

1. **Start with helper scripts**
   - Use `create-feature-branch.sh` instead of manual commands
   - Use `finish-feature.sh` for PRs
   - Let automation do the work

2. **Learn keyboard shortcuts gradually**
   - Start with `Ctrl+Shift+A T` (create branch)
   - Add `Ctrl+Shift+A F` (finish feature)
   - Build muscle memory over time

3. **Don't bypass hooks**
   - They exist to help you
   - Fix issues instead of using `--no-verify`
   - Ask for help if stuck

4. **Commit frequently**
   - Small, focused commits
   - Always include TASK-XXX
   - Push regularly

5. **Read error messages**
   - Hooks provide helpful guidance
   - Error messages explain what's wrong
   - Follow the suggestions

---

## 🆘 Getting Help

### Documentation
- [WORKFLOW.md](.github/WORKFLOW.md) - Complete guide
- [QUICK_REFERENCE.md](.github/QUICK_REFERENCE.md) - Cheat sheet
- [Scripts README](scripts/git-helpers/README.md) - Script docs
- [Hooks README](.githooks/README.md) - Hook docs

### Support Channels
- GitHub Issues: https://github.com/fupacat/Orca/issues
- Team Chat: [Your team chat link]
- Documentation: Check `.github/` directory

### Common Commands
```bash
# View workflow status
git status

# See current TASK-XXX
git rev-parse --abbrev-ref HEAD | grep -o 'TASK-[0-9]\{3\}'

# List all branches
git branch -a

# View commit history
git log --oneline -10

# Check hooks configuration
git config --get core.hooksPath
```

---

## ✅ Setup Checklist

Use this checklist to verify your setup:

### Basic Setup
- [ ] Git installed and configured
- [ ] Repository cloned
- [ ] On `develop` branch
- [ ] Git hooks activated (`git config core.hooksPath .githooks`)
- [ ] Hooks are executable (`ls -la .githooks/`)

### Tools
- [ ] GitHub CLI installed (`gh --version`)
- [ ] GitHub CLI authenticated (`gh auth status`)
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Black installed (`black --version`)
- [ ] Ruff installed (`ruff --version`)
- [ ] MyPy installed (`mypy --version`)
- [ ] Pytest installed (`pytest --version`)

### Optional
- [ ] VSCode installed with recommended extensions
- [ ] Helper scripts in PATH
- [ ] Archon MCP server running
- [ ] Serena MCP server configured

### Verification
- [ ] Git hooks test passed
- [ ] Helper scripts test passed
- [ ] VSCode integration works
- [ ] Can create test branch
- [ ] Can commit with TASK-XXX

---

## 🎉 You're All Set!

Your Orca-Archon Hybrid workflow is now fully configured. Start developing with:

```bash
./scripts/git-helpers/create-feature-branch.sh
```

Or in VSCode: `Ctrl+Shift+A T`

Happy coding! 🚀

---

🤖 _Setup guide for Orca-Archon Hybrid Git Workflow_

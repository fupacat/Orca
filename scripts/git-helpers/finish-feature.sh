#!/bin/bash
#
# Interactive script to finish a feature and create a pull request
#
# Usage: ./finish-feature.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🏁 Orca-Archon: Finish Feature & Create PR${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${YELLOW}📍 Current branch: $CURRENT_BRANCH${NC}"

# Check if we're on a feature branch
if [[ ! "$CURRENT_BRANCH" =~ ^(feature|fix|refactor|hotfix)/ ]]; then
    echo -e "${RED}❌ Error: Not on a feature/fix/refactor/hotfix branch${NC}"
    exit 1
fi

# Extract TASK-XXX from branch name
if [[ "$CURRENT_BRANCH" =~ TASK-([0-9]{3}) ]]; then
    TASK_ID="TASK-${BASH_REMATCH[1]}"
    echo -e "${GREEN}✓ Task ID: $TASK_ID${NC}"
else
    echo -e "${RED}❌ Error: No TASK-XXX found in branch name${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📋 Pre-Flight Checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ You have uncommitted changes${NC}"
    echo -e "${YELLOW}Commit or stash them first${NC}"
    git status --short
    exit 1
fi
echo -e "${GREEN}✅ No uncommitted changes${NC}"

# Check if branch is pushed to remote
if ! git rev-parse --verify origin/$CURRENT_BRANCH >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Branch not pushed to remote${NC}"
    read -p "Push now? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin $CURRENT_BRANCH
        echo -e "${GREEN}✅ Branch pushed${NC}"
    else
        echo -e "${RED}❌ Cancelled - push manually first${NC}"
        exit 1
    fi
else
    # Check if local is ahead of remote
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u})
    if [ $LOCAL != $REMOTE ]; then
        echo -e "${YELLOW}⚠️  Local branch differs from remote${NC}"
        read -p "Push changes? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin $CURRENT_BRANCH
            echo -e "${GREEN}✅ Changes pushed${NC}"
        fi
    else
        echo -e "${GREEN}✅ Branch up-to-date with remote${NC}"
    fi
fi

# Check if branch is up-to-date with develop
echo ""
echo -e "${YELLOW}Checking if branch is synced with develop...${NC}"
git fetch origin develop
BEHIND_COUNT=$(git rev-list --count HEAD..origin/develop)
if [ "$BEHIND_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Branch is $BEHIND_COUNT commit(s) behind develop${NC}"
    read -p "Rebase on develop? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git rebase origin/develop
        git push --force-with-lease origin $CURRENT_BRANCH
        echo -e "${GREEN}✅ Rebased and pushed${NC}"
    else
        echo -e "${YELLOW}⚠️  Continuing without rebase (PR may have conflicts)${NC}"
    fi
else
    echo -e "${GREEN}✅ Branch up-to-date with develop${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📝 Pull Request Details${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Extract PR title from branch name or recent commits
BRANCH_DESCRIPTION=$(echo "$CURRENT_BRANCH" | sed 's/^[^/]*\/TASK-[0-9]\{3\}-//' | tr '-' ' ')
DEFAULT_TITLE="$TASK_ID: $BRANCH_DESCRIPTION"

echo -e "${YELLOW}PR Title:${NC}"
echo -e "${GREEN}$DEFAULT_TITLE${NC}"
read -p "Use this title? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Enter custom title:${NC}"
    read -e -i "$DEFAULT_TITLE" PR_TITLE
else
    PR_TITLE="$DEFAULT_TITLE"
fi

# Get commit messages for PR body
echo ""
echo -e "${YELLOW}Generating PR body from commits...${NC}"
COMMIT_LIST=$(git log origin/develop..HEAD --pretty=format:"- %s" | head -n 10)

# Create PR body
PR_BODY="## 📋 Archon Task Reference
**Task ID:** $TASK_ID
**Task Status:** \`doing\` → \`review\`

## 📝 Description
<!-- Describe what this PR does -->

### What changed?
$COMMIT_LIST

### Why?
<!-- Explain the motivation -->


## 🧪 Testing
- [ ] Unit tests added/updated
- [ ] All tests passing
- [ ] Coverage ≥ 80%

## ✅ Quality Gates
- [ ] Code formatted (Black)
- [ ] Linting passed (Ruff)
- [ ] Type checking passed (MyPy)
- [ ] No security issues (Bandit)

---
🤖 _Generated with Claude Code_"

# Save PR body to temp file
echo "$PR_BODY" > /tmp/pr_body.md

echo ""
echo -e "${YELLOW}PR body saved to /tmp/pr_body.md${NC}"
echo -e "${YELLOW}You can edit it before submitting${NC}"

echo ""
read -p "Create pull request now? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Cancelled${NC}"
    echo -e "${YELLOW}To create PR manually:${NC}"
    echo "  gh pr create --title '$PR_TITLE' --body-file /tmp/pr_body.md --base develop"
    exit 0
fi

# Create PR using GitHub CLI
if ! command -v gh >/dev/null 2>&1; then
    echo -e "${RED}❌ GitHub CLI (gh) not installed${NC}"
    echo -e "${YELLOW}Install: https://cli.github.com/${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Creating pull request...${NC}"

if gh pr create --title "$PR_TITLE" --body-file /tmp/pr_body.md --base develop; then
    echo -e "${GREEN}✅ Pull request created successfully!${NC}"

    # Get PR URL
    PR_URL=$(gh pr view --json url --jq .url)
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 Success!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}Pull Request: $PR_URL${NC}"
    echo ""
    echo -e "${YELLOW}💡 Next Steps:${NC}"
    echo "  1. Update Archon task status to 'review'"
    echo "  2. Request code review"
    echo "  3. Address review feedback"
    echo "  4. Merge when approved"
    echo ""

    # Future: Auto-update Archon task status
    # if command -v claude >/dev/null 2>&1; then
    #     claude mcp archon manage_task update --task-id "$TASK_ID" --status review
    #     echo -e "${GREEN}✅ Archon task updated to 'review'${NC}"
    # fi

    # Open PR in browser (optional)
    read -p "Open PR in browser? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gh pr view --web
    fi
else
    echo -e "${RED}❌ Failed to create pull request${NC}"
    exit 1
fi

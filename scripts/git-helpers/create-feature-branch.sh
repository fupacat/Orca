#!/bin/bash
#
# Interactive script to create a feature branch from an Archon task
#
# Usage: ./create-feature-branch.sh [TASK_ID] [DESCRIPTION]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Orca-Archon: Create Feature Branch${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${YELLOW}📍 Current branch: $CURRENT_BRANCH${NC}"

# Ensure we're on develop
if [ "$CURRENT_BRANCH" != "develop" ]; then
    echo -e "${YELLOW}⚠️  Not on develop branch${NC}"
    read -p "Switch to develop? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Switching to develop...${NC}"
        git checkout develop
        git pull origin develop
    else
        echo -e "${YELLOW}Continuing from $CURRENT_BRANCH${NC}"
    fi
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📋 Task Information${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Get TASK-XXX (from argument or prompt)
if [ -n "$1" ]; then
    TASK_ID="$1"
else
    echo -e "${YELLOW}Enter TASK ID (e.g., TASK-005):${NC}"
    read TASK_ID
fi

# Validate TASK-XXX format
if ! echo "$TASK_ID" | grep -qE "^TASK-[0-9]{3}$"; then
    echo -e "${RED}❌ Invalid TASK ID format. Must be TASK-XXX (e.g., TASK-005)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Task ID: $TASK_ID${NC}"

# Future: Query Archon MCP for task details
# if command -v claude >/dev/null 2>&1; then
#     echo -e "${YELLOW}Fetching task details from Archon...${NC}"
#     TASK_DETAILS=$(claude mcp archon find_tasks --task-id "$TASK_ID")
#     echo "$TASK_DETAILS"
# fi

echo ""

# Get description (from argument or prompt)
if [ -n "$2" ]; then
    DESCRIPTION="$2"
else
    echo -e "${YELLOW}Enter branch description (lowercase-with-hyphens):${NC}"
    read DESCRIPTION
fi

# Clean description (lowercase, replace spaces with hyphens, remove special chars)
DESCRIPTION=$(echo "$DESCRIPTION" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g' | sed 's/[^a-z0-9-]//g')

echo -e "${GREEN}✓ Description: $DESCRIPTION${NC}"

# Select branch type
echo ""
echo -e "${YELLOW}Select branch type:${NC}"
echo "  1) feature (new features)"
echo "  2) fix (bug fixes)"
echo "  3) refactor (code refactoring)"
echo "  4) hotfix (urgent production fixes)"
read -p "Choice (1-4): " -n 1 -r
echo ""

case $REPLY in
    1)
        BRANCH_TYPE="feature"
        ;;
    2)
        BRANCH_TYPE="fix"
        ;;
    3)
        BRANCH_TYPE="refactor"
        ;;
    4)
        BRANCH_TYPE="hotfix"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

# Construct branch name
BRANCH_NAME="$BRANCH_TYPE/$TASK_ID-$DESCRIPTION"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📝 Branch Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Branch name: $BRANCH_NAME${NC}"
echo -e "${GREEN}Task ID: $TASK_ID${NC}"
echo -e "${GREEN}Type: $BRANCH_TYPE${NC}"
echo -e "${GREEN}Description: $DESCRIPTION${NC}"
echo ""

read -p "Create this branch? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Cancelled${NC}"
    exit 0
fi

# Create and checkout branch
echo ""
echo -e "${YELLOW}Creating branch...${NC}"
git checkout -b "$BRANCH_NAME"

echo -e "${GREEN}✅ Branch created: $BRANCH_NAME${NC}"

# Future: Update Archon task status to "doing"
# if command -v claude >/dev/null 2>&1; then
#     echo -e "${YELLOW}Updating Archon task status to 'doing'...${NC}"
#     claude mcp archon manage_task update --task-id "$TASK_ID" --status doing
#     echo -e "${GREEN}✅ Archon task updated${NC}"
# fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Ready to work on $TASK_ID!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo "  1. Research task requirements (use Archon RAG)"
echo "  2. Write code with frequent commits"
echo "  3. Include $TASK_ID in commit messages"
echo "  4. Run: ./finish-feature.sh when ready for PR"
echo ""
echo -e "${YELLOW}📌 Quick Commands:${NC}"
echo "  git commit -m 'feat($TASK_ID): Your change here'"
echo "  git push -u origin $BRANCH_NAME"
echo ""

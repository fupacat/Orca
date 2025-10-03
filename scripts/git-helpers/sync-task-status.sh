#!/bin/bash
#
# Interactive script to manually sync Archon task status
#
# Usage: ./sync-task-status.sh [TASK_ID] [STATUS]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🔄 Orca-Archon: Sync Task Status${NC}"
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

# Try to extract TASK-XXX from branch name
if [[ "$CURRENT_BRANCH" =~ TASK-([0-9]{3}) ]]; then
    DEFAULT_TASK_ID="TASK-${BASH_REMATCH[1]}"
    echo -e "${GREEN}✓ Found task in branch: $DEFAULT_TASK_ID${NC}"
else
    DEFAULT_TASK_ID=""
fi

echo ""

# Get TASK-XXX (from argument, branch, or prompt)
if [ -n "$1" ]; then
    TASK_ID="$1"
elif [ -n "$DEFAULT_TASK_ID" ]; then
    read -p "Use task $DEFAULT_TASK_ID? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        TASK_ID="$DEFAULT_TASK_ID"
    else
        echo -e "${YELLOW}Enter TASK ID (e.g., TASK-005):${NC}"
        read TASK_ID
    fi
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

# Get new status (from argument or prompt)
if [ -n "$2" ]; then
    NEW_STATUS="$2"
else
    echo ""
    echo -e "${YELLOW}Select new status:${NC}"
    echo "  1) todo (not started)"
    echo "  2) doing (in progress)"
    echo "  3) review (ready for review)"
    echo "  4) done (completed)"
    read -p "Choice (1-4): " -n 1 -r
    echo ""

    case $REPLY in
        1)
            NEW_STATUS="todo"
            ;;
        2)
            NEW_STATUS="doing"
            ;;
        3)
            NEW_STATUS="review"
            ;;
        4)
            NEW_STATUS="done"
            ;;
        *)
            echo -e "${RED}❌ Invalid choice${NC}"
            exit 1
            ;;
    esac
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📋 Update Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Task ID: $TASK_ID${NC}"
echo -e "${GREEN}New Status: $NEW_STATUS${NC}"
echo ""

read -p "Update task status in Archon? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Updating Archon task status...${NC}"

# Future: Actual Archon MCP integration
# if command -v claude >/dev/null 2>&1; then
#     if claude mcp archon manage_task update --task-id "$TASK_ID" --status "$NEW_STATUS"; then
#         echo -e "${GREEN}✅ Archon task updated successfully${NC}"
#     else
#         echo -e "${RED}❌ Failed to update Archon task${NC}"
#         exit 1
#     fi
# else
#     echo -e "${YELLOW}⚠️  Claude MCP CLI not available${NC}"
#     echo -e "${YELLOW}Update task manually via Archon MCP tools${NC}"
# fi

# Placeholder message until Archon CLI integration is available
echo -e "${YELLOW}⚠️  Archon CLI integration not yet available${NC}"
echo ""
echo -e "${YELLOW}To update task status manually:${NC}"
echo "  1. Open Claude Code with Archon MCP connection"
echo "  2. Run: mcp__archon__manage_task"
echo "  3. Parameters:"
echo "     - action: \"update\""
echo "     - task_id: \"$TASK_ID\""
echo "     - status: \"$NEW_STATUS\""
echo ""

# Show helpful context based on status
case $NEW_STATUS in
    doing)
        echo -e "${YELLOW}💡 Tips for 'doing' status:${NC}"
        echo "  - Research task requirements first"
        echo "  - Break into subtasks if large"
        echo "  - Commit frequently with $TASK_ID"
        ;;
    review)
        echo -e "${YELLOW}💡 Tips for 'review' status:${NC}"
        echo "  - Ensure all tests pass"
        echo "  - Create pull request"
        echo "  - Request code review"
        ;;
    done)
        echo -e "${YELLOW}💡 Tips for 'done' status:${NC}"
        echo "  - Ensure PR is merged"
        echo "  - Verify in production if applicable"
        echo "  - Document any lessons learned"
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Status sync complete${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

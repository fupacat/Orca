#!/bin/bash
# archive-workflow.sh - Archive completed Orca workflow artifacts

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Orca Workflow Artifact Archiver${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Change to project root
cd "$PROJECT_ROOT"

# Function to get workflow name
get_workflow_name() {
    if [ -n "${1:-}" ]; then
        echo "$1"
    else
        echo -n "Enter workflow name (e.g., 'process-improvement'): "
        read -r workflow_name
        echo "$workflow_name"
    fi
}

# Function to detect workflow artifacts
detect_artifacts() {
    local pattern="$1"
    find . -maxdepth 1 -name "$pattern" -type f 2>/dev/null || true
}

# Main function
main() {
    local workflow_name="${1:-}"

    # Detect artifacts
    echo -e "${YELLOW}🔍 Scanning for workflow artifacts...${NC}"

    local feature_files=$(detect_artifacts "feature_*.md")
    local impl_files=$(detect_artifacts "impl_*.md")
    local plan_files=$(detect_artifacts "*_impl_plan.md")
    local exec_files=$(detect_artifacts "execute_*.py")

    local total_count=0
    total_count=$(($(echo "$feature_files" | grep -c . || echo 0) + $(echo "$impl_files" | grep -c . || echo 0) + $(echo "$plan_files" | grep -c . || echo 0) + $(echo "$exec_files" | grep -c . || echo 0)))

    if [ "$total_count" -eq 0 ]; then
        echo -e "${GREEN}✓ No workflow artifacts found in root directory${NC}"
        echo -e "  Root directory is clean!"
        exit 0
    fi

    echo -e "${YELLOW}Found $total_count artifact(s) to archive:${NC}"
    [ -n "$feature_files" ] && echo "$feature_files" | sed 's/^/  - /'
    [ -n "$impl_files" ] && echo "$impl_files" | sed 's/^/  - /'
    [ -n "$plan_files" ] && echo "$plan_files" | sed 's/^/  - /'
    [ -n "$exec_files" ] && echo "$exec_files" | sed 's/^/  - /'
    echo

    # Get workflow name if not provided
    if [ -z "$workflow_name" ]; then
        workflow_name=$(get_workflow_name)
    fi

    # Sanitize workflow name (replace spaces with hyphens, lowercase)
    workflow_name=$(echo "$workflow_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')

    if [ -z "$workflow_name" ]; then
        echo -e "${RED}❌ Error: Workflow name cannot be empty${NC}"
        exit 1
    fi

    # Create archive directory with timestamp
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local archive_dir=".archive/workflows/${workflow_name}-${timestamp}"

    echo -e "${BLUE}📦 Creating archive directory: $archive_dir${NC}"
    mkdir -p "$archive_dir"

    # Move artifacts
    local moved_count=0

    if [ -n "$feature_files" ]; then
        echo -e "${YELLOW}Moving feature_*.md files...${NC}"
        echo "$feature_files" | while read -r file; do
            [ -n "$file" ] && mv "$file" "$archive_dir/" && echo -e "  ${GREEN}✓${NC} $(basename "$file")"
            ((moved_count++)) || true
        done
    fi

    if [ -n "$impl_files" ]; then
        echo -e "${YELLOW}Moving impl_*.md files...${NC}"
        echo "$impl_files" | while read -r file; do
            [ -n "$file" ] && mv "$file" "$archive_dir/" && echo -e "  ${GREEN}✓${NC} $(basename "$file")"
            ((moved_count++)) || true
        done
    fi

    if [ -n "$plan_files" ]; then
        echo -e "${YELLOW}Moving *_impl_plan.md files...${NC}"
        echo "$plan_files" | while read -r file; do
            [ -n "$file" ] && mv "$file" ".archive/plans/" && echo -e "  ${GREEN}✓${NC} $(basename "$file") → .archive/plans/"
            ((moved_count++)) || true
        done
    fi

    if [ -n "$exec_files" ]; then
        echo -e "${YELLOW}Moving execute_*.py files...${NC}"
        echo "$exec_files" | while read -r file; do
            [ -n "$file" ] && mv "$file" ".archive/executions/" && echo -e "  ${GREEN}✓${NC} $(basename "$file") → .archive/executions/"
            ((moved_count++)) || true
        done
    fi

    # Create manifest
    local manifest="$archive_dir/MANIFEST.md"
    echo "# Workflow Archive Manifest" > "$manifest"
    echo >> "$manifest"
    echo "**Workflow:** $workflow_name" >> "$manifest"
    echo "**Archived:** $(date)" >> "$manifest"
    echo "**Artifacts:** $total_count files" >> "$manifest"
    echo >> "$manifest"
    echo "## Files Archived" >> "$manifest"
    echo >> "$manifest"
    ls -lh "$archive_dir" | tail -n +2 | awk '{print "- " $9 " (" $5 ")"}' >> "$manifest"

    echo
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Archive complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  Location: ${BLUE}$archive_dir${NC}"
    echo -e "  Manifest: ${BLUE}$manifest${NC}"
    echo
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo -e "  - Review archived files: ${BLUE}cd $archive_dir${NC}"
    echo -e "  - Commit changes: ${BLUE}git add .archive/ .gitignore && git commit -m \"chore: Archive $workflow_name workflow artifacts\"${NC}"
    echo
}

# Run main function
main "$@"

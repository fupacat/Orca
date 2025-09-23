# {project_name} Development Commands

## Core Orca Slash Commands

### Workflow Execution
```bash
# Execute the complete Orca workflow
/orca-start "{project_description}" "{constraints}" true

# Create new project with full workflow
/orca-workflow "ProjectName" "/path/to/parent" "{project_description}" "{constraints}"

# Create new project (setup only)
/orca-new "ProjectName" "/path/to/parent" "{project_description}" "{constraints}"
```

### System Validation
```bash
# Quick MCP server validation
/orca-deps

# Comprehensive system verification
/orca-startup

# Check MCP server connection status
claude mcp list

# GitHub integration and setup
/orca-github setup
```

## MCP Server Management

### Archon Integration
```bash
# Check Archon health
mcp__archon__health_check()

# List project tasks
mcp__archon__find_tasks(project_id="[project_id]")

# Search knowledge base
mcp__archon__rag_search_knowledge_base(query="[search_term]", match_count=5)
```

### Serena Integration
```bash
# Check project directory
mcp__serena__list_dir(".", recursive=false)

# Search for code patterns
mcp__serena__search_for_pattern(substring_pattern="[pattern]")

# Get symbols overview
mcp__serena__get_symbols_overview(relative_path="[file_path]")
```

## Platform-Specific Commands ({platform})

### File System Operations
```cmd
# List directory contents
dir

# Change directory
cd [directory_name]

# Create directory
mkdir [directory_name]

# Copy files
copy [source] [destination]

# Search for files
dir /s [pattern]

# Search for text in files
findstr /s [text] [files]
```

## Development Workflow Commands

### Project Phase Commands
[To be populated as project architecture is determined]

### Build Commands
[To be defined during Architecture phase based on technology stack]

### Test Commands
[To be established during Implementation phase]

### Deployment Commands
[To be specified during Implementation planning]

## Archon Task Management Workflow
```bash
# 1. Check current tasks
mcp__archon__find_tasks(filter_by="status", filter_value="todo")

# 2. Mark task as in progress
mcp__archon__manage_task("update", task_id="[id]", status="doing")

# 3. Research for implementation
mcp__archon__rag_search_code_examples(query="[implementation_pattern]")

# 4. Complete task and mark for review
mcp__archon__manage_task("update", task_id="[id]", status="review")
```

## Critical Workflow Rules
- **ALWAYS** verify MCP servers before starting work
- **FOLLOW** archon_rules.md for all development activities
- **USE** Archon for primary task management
- **RESEARCH** using Archon RAG before implementation
- **MAINTAIN** stateless agent patterns throughout development
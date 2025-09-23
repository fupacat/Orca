# Orca Development Commands

## Core System Commands

### MCP Server Management
```bash
# Check MCP server connection status
claude mcp list

# Expected output should show both servers connected:
# archon: http://localhost:8051/mcp (HTTP) - ✓ Connected
# serena: uvx --from git+https://github.com/oraios/serena ... - ✓ Connected
```

### Dependency Validation
```bash
# Run the CheckDependencies function from check_dependencies.md
# This validates both Archon and Serena MCP servers are available
```

### Workflow Execution
```bash
# Execute StartWorkflow function from start.md with parameters:
# - project_description: Short description of software to develop
# - constraints: Development constraints and limitations  
# - clarification_mode: Whether to pause for clarification on ambiguous requirements
```

## File System Commands (Windows)

### Navigation
```cmd
# List directory contents
dir

# Change directory
cd [directory_name]

# Show current directory
cd
```

### File Operations
```cmd
# Create directory
mkdir [directory_name]

# Copy files
copy [source] [destination]

# Move/rename files
move [source] [destination]

# Delete files
del [filename]

# Delete directory
rmdir [directory_name]
```

### Search Commands
```cmd
# Find files by name pattern
dir /s [pattern]

# Search for text in files
findstr /s [text] [files]
```

## Development Workflow

### Project Initialization
1. Run `CheckDependencies` to verify MCP servers
2. Use `StartupCheck` for comprehensive verification
3. Execute appropriate workflow function based on scenario

### No Build Process
This system has no traditional build, test, or lint commands as it's configuration-driven.

### No Version Control
This directory is not a git repository - no git commands available.

## Archon Integration Commands
See archon_rules.md for complete Archon MCP server integration workflow.
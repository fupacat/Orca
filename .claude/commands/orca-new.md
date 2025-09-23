# /orca-new

Create a new project with complete Orca workflow setup and tool integration.

## Usage
```
/orca-new <project_name> <project_path> <project_description> [constraints] [auto_start] [github_setup]
```

## Parameters
- **project_name** (required): Name of the new project (used as directory name)
- **project_path** (required): Parent directory where project should be created
- **project_description** (required): Short description of the software to be developed
- **constraints** (optional): Development constraints, e.g., "solo developer, free tools"
- **auto_start** (optional): true/false - automatically execute workflow after setup (default: false)
- **github_setup** (optional): true/false - automatically set up GitHub repository (default: true)

## Examples
```
/orca-new "TaskMaster" "C:\Users\eolun\projects" "REST API for task management"
/orca-new "DataViz" "C:\dev" "Data visualization dashboard" "Python, free tools" true true
/orca-new "MobileDash" "/Users/dev/projects" "Mobile-friendly web dashboard" "React, responsive design" false false
```

## Description
Complete automation to create a new project directory, set up all tools (Claude Code, Serena, Archon), copy necessary files, and prepare for Orca workflow execution.

## What it does
1. **Create Project Structure**: Sets up directories and copies Orca core files
2. **Configure MCP Servers**: Adds Archon and Serena to the new project
3. **Initialize Both Systems**:
   - Creates Archon project entry with task management
   - Performs Serena onboarding with standardized memory files
4. **Generate Project Files**: Creates customized documentation and configuration
5. **Validate Setup**: Verifies all systems are operational
6. **Optional Git Init**: Creates git repository if desired
7. **Auto-Start Workflow**: Optionally begins StartWorkflow immediately

## Created Files
- Core Orca workflow files (start.md, archon_rules.md, etc.)
- Project-specific documentation (CLAUDE.md, README.md, PROJECT_BRIEF.md)
- MCP server configurations (.claude/claude.json)
- Serena memory files (project context and guidelines)
- Template files for consistent development

## Generated Output
- ✅ **Project Created**: Full path to new project
- ✅ **Tools Configured**: Archon, Serena, Claude Code status
- ✅ **Systems Initialized**: Both MCP systems ready with project context
- ✅ **Ready for Development**: Confirmation that workflows can be executed
- 🚀 **Next Steps**: Instructions for beginning development

## Prerequisites
- Archon MCP server running at http://localhost:8051/mcp
- Serena MCP server available
- Write permissions to the specified project path

The project will be completely self-contained and ready for independent Orca workflow execution.
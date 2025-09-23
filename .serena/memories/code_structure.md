# Orca Codebase Structure

## Root Directory Files
- `start.md` - Contains the main StartWorkflow function definition and orchestration logic
- `archon_rules.md` - **CRITICAL: Archon-first development rules** that override all other instructions
- `CLAUDE.md` - Project documentation and guidance for Claude Code
- `bootstrap_project.md` - Project bootstrapping utilities
- `check_dependencies.md` - MCP server validation utilities
- `create_new_project.md` - Project creation functions
- `initialize_current_project.md` - Project initialization utilities
- `new_project_workflow.md` - Complete new project workflow
- `startup_check.md` - System verification functions

## Directories
- `templates/` - Contains agent definitions, prompts, and MCP server configuration
  - `agent_definitions.md` - Defines roles and specializations of each agent
  - `agent_prompts.md` - Contains detailed prompts for each specialized agent (with Archon integration)
  - `.claude.json` - MCP server configuration for Archon and Serena integration
  - Template files for project creation

## Configuration Files
- `.claude/` - Claude Code configuration directory
- `.serena/` - Serena MCP server data directory

## File Types
- **Markdown (.md)**: All workflow artifacts, documentation, and agent definitions
- **JSON**: Configuration files for MCP servers
- **Templates**: Reusable project scaffolding files

## No Traditional Code
This is a configuration-driven system with no source code files (no .js, .py, .java, etc.)
The "code" consists of structured markdown files with function definitions and workflows.
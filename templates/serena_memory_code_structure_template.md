# {project_name} Codebase Structure

## Root Directory Files
- `start.md` - Orca StartWorkflow function definition and orchestration logic
- `startup_check.md` - MCP server validation and system verification
- `check_dependencies.md` - Quick dependency validation utilities
- `archon_rules.md` - **CRITICAL: Archon-first development rules**
- `CLAUDE.md` - Project documentation and guidance for Claude Code
- `PROJECT_BRIEF.md` - Project overview and initial requirements
- `README.md` - Project introduction and setup instructions

## Configuration Directories
- `.claude/` - Claude Code project configuration
  - `claude.json` - MCP server configuration for Archon and Serena
- `.serena/` - Serena MCP server data and project context
- `templates/` - Orca workflow configuration files
  - `agent_definitions.md` - Specialized agent roles and responsibilities
  - `agent_prompts.md` - Agent-specific prompts with Archon integration

## Generated Directories
- `docs/` - Workflow artifacts and documentation
  - Created during Orca workflow execution
  - Contains discovery.md, requirements.md, architecture.md, etc.
- `src/` - Source code (created during implementation phase)
- `tests/` - Test files (created during implementation phase)

## File Types and Conventions
- **Markdown (.md)**: All workflow artifacts, documentation, and agent definitions
- **JSON**: Configuration files for MCP servers and project settings
- **Source Code**: [Language and structure to be determined during Architecture phase]

## Project Organization Principles
- **Artifact-Driven**: Each workflow phase produces specific deliverable files
- **Template-Based**: Standardized agent definitions and prompts for consistency
- **MCP-Integrated**: Leverages Archon for task management, Serena for code operations
- **Stateless**: Each workflow phase operates independently

## Future Structure
As the project develops through the Orca workflow:
1. **Discovery Phase**: Adds comprehensive domain understanding
2. **Requirements Phase**: Establishes clear feature specifications
3. **Architecture Phase**: Defines technical structure and file organization
4. **Implementation Phase**: Creates actual source code following established patterns
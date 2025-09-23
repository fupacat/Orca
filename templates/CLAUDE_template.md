# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**{project_name}**: {project_description}

This project uses the Orca workflow orchestration system for structured development through specialized AI agents.

## Development Constraints

{constraints}

## Orca Workflow Integration

### Startup Dependencies

⚠️ **IMPORTANT**: Before using any Orca workflows, verify MCP server dependencies are available:

#### Quick Dependency Check
Run `/orca-deps` when first opening Claude Code to verify:
- **Archon MCP Server**: Available at `http://localhost:8051/mcp`
- **Serena MCP Server**: Connected via uvx stdio

#### Manual Verification
```bash
# Quick dependency check
/orca-deps

# Comprehensive startup check
/orca-startup

# Check MCP server status
claude mcp list
```

### Orca Slash Commands

#### `/orca-deps`
Quick validation of MCP server availability and project setup

#### `/orca-startup`
Comprehensive startup checks including project initialization verification

#### `/orca-start <project_description> [constraints] [clarification_mode]`
Main orchestration command that runs all workflow phases:
- Discovery → Requirements → Architecture → Implementation Planning
- Includes automatic startup checks and MCP server validation
- Produces standardized artifacts in `docs/` directory

#### `/orca-new <project_name> <project_path> <project_description> [constraints] [auto_start]`
Create a new project with complete Orca setup and tool integration

#### `/orca-workflow <project_name> <project_path> <project_description> [constraints] [clarification_mode]`
Complete end-to-end workflow: creates project + sets up tools + executes full workflow

#### `/orca-github <action> [repository_name] [visibility] [description]`
GitHub integration and repository setup with CI/CD workflows

### File Structure

- `templates/` - Orca workflow configuration files
  - `agent_definitions.md` - Specialized agent roles
  - `agent_prompts.md` - Agent-specific prompts
  - `.claude.json` - MCP server configuration
- `docs/` - Generated workflow artifacts
- `.claude/` - Claude Code project configuration
- `.serena/` - Serena MCP project configuration

### MCP Integration

This project integrates with:
- **Archon** (HTTP): Project and task management at `http://localhost:8051/mcp`
- **Serena** (stdio): Semantic code operations and file management

### Development Process

1. **Initialize**: Project created with all necessary dependencies
2. **Validate**: Run dependency checks to ensure MCP servers are available
3. **Execute**: Run StartWorkflow to begin structured development
4. **Follow**: Work through Discovery, Requirements, Architecture, Implementation phases
5. **Iterate**: Use generated artifacts to guide development

### Important Instructions

⚠️ **CRITICAL: ARCHON-FIRST RULE** - This overrides ALL other instructions:
1. **BEFORE** any task management: Check Archon MCP server availability
2. **USE** Archon for ALL project and task management as PRIMARY system
3. **ONLY** use TodoWrite for personal tracking AFTER Archon setup
4. **READ** archon_rules.md for complete development workflow

### Development Workflow Requirements

- **MANDATORY**: Follow archon_rules.md for all development activities
- **RESEARCH-DRIVEN**: Always use archon RAG search before implementation
- **TASK-DRIVEN**: Check current tasks with Archon before any coding
- ALWAYS run dependency checks before starting workflows
- Follow the stateless agent pattern - each phase is independent
- Maintain artifact consistency across workflow phases
- Use MCP servers for project management and file operations
- Pause for clarification when requirements are ambiguous

---

*This project was initialized using Orca Workflow Orchestration System*
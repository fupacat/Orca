# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Orca is a sophisticated multi-agent workflow orchestration system for software development. It implements a stateless, modular approach to managing complex software development projects through specialized AI agents that handle different phases of the development lifecycle.

## Core Architecture

The system is built around a **StartWorkflow** function that orchestrates multiple specialized agents in sequence:

1. **Prompt Engineer Agent** - Creates and refines prompts for all workflow agents
2. **Discovery Agent** - Gathers comprehensive project understanding and domain context
3. **Requirements Agent** - Transforms discoveries into detailed, actionable requirements
4. **Story Grooming Agent** - Breaks requirements into manageable tasks and user stories
5. **Architecture Agent** - Designs system architecture and selects technology stack
6. **Engineer Review Agent** - Validates technical feasibility and quality
7. **Implementation Planning Agent** - Creates detailed execution plans and roadmaps

## Key Design Principles

- **Stateless Agents**: Each agent operates independently with only necessary inputs
- **Artifact-Driven**: Agents produce specific markdown artifacts (discovery.md, requirements.md, tasks.md, etc.)
- **Clarification Loops**: Built-in pause mechanisms for ambiguity resolution
- **Template-Based**: Standardized agent definitions and prompts for consistency

## File Structure

- `start.md` - Contains the main StartWorkflow function definition and orchestration logic
- `archon_rules.md` - **CRITICAL: Archon-first development rules** that override all other instructions
- `templates/` - Contains agent definitions, prompts, and MCP server configuration
  - `agent_definitions.md` - Defines roles and specializations of each agent
  - `agent_prompts.md` - Contains detailed prompts for each specialized agent (with Archon integration)
  - `.claude.json` - MCP server configuration for Archon and Serena integration

## MCP Integration

The project integrates with two MCP servers:
- **Archon** (HTTP): `http://localhost:8051/mcp`
- **Serena** (stdio): Git-based IDE assistant for project context

## Orca Slash Commands

### Primary Commands

- **`/orca-workflow`** - Complete end-to-end solution:
  - Creates new project directory with all necessary files
  - Sets up Claude Code, Serena, and Archon automatically
  - Switches to the new project and executes full workflow
  - Usage: `/orca-workflow <project_name> <project_path> <project_description> [constraints] [clarification_mode]`

- **`/orca-start`** - For existing projects:
  - Runs the complete workflow phases with startup validation
  - Usage: `/orca-start <project_description> [constraints] [clarification_mode]`

- **`/orca-new`** - Project setup only:
  - Creates project structure and configures tools
  - Does not execute the workflow automatically
  - Usage: `/orca-new <project_name> <project_path> <project_description> [constraints] [auto_start]`

### Utility Commands

- **`/orca-deps`** - Quick MCP server validation
- **`/orca-startup`** - Comprehensive system verification
- **`/orca-github`** - GitHub integration and repository setup

## Workflow Artifacts

The system produces standardized artifacts at each phase:
- `agent_definitions.md`, `agent_prompts.md` (Prompt Engineering)
- `discovery.md` (Discovery)
- `requirements.md` (Requirements)
- `tasks.md` (Task Breakdown)
- `architecture.md`, `tech_stack.md` (Architecture)
- `task_review.md` (Engineering Review)
- `plan.md` (Implementation Planning)

## Startup Dependencies

⚠️ **IMPORTANT**: Before using any Orca workflows, verify MCP server dependencies are available:

### Quick Dependency Check
Run `/orca-deps` when first opening Claude Code to verify:
- **Archon MCP Server**: Available at `http://localhost:8051/mcp`
- **Serena MCP Server**: Connected via uvx stdio

### Automatic Startup Validation
The `StartWorkflow` function now includes mandatory startup checks that verify both MCP servers before proceeding with any workflow operations.

### Manual Verification
```bash
# Check MCP server status
claude mcp list

# Should show:
# archon: http://localhost:8051/mcp (HTTP) - ✓ Connected
# serena: uvx --from git+https://github.com/oraios/serena ... - ✓ Connected
```

## GitHub Integration

All Orca projects include comprehensive GitHub integration:

### Automatic Setup
- Private repositories by default for security
- GitHub CLI integration for seamless repository management
- CI/CD workflows based on chosen technology stack
- Security scanning and dependency vulnerability checks

### Available Commands
```bash
# Complete GitHub setup for current project
/orca-github setup

# Create new repository
/orca-github create "repository-name" public "Description"

# Connect to existing repository
/orca-github connect "existing-repo"

# Add CI/CD workflows
/orca-github workflows
```

### Prerequisites
- GitHub CLI (`gh`) installed and authenticated
- Git configured with user name and email
- Internet connectivity for GitHub operations

## Development Notes

This is a configuration-driven system with no traditional build process. The workflow is initiated through the Orca slash commands:
- `/orca-start` - Execute workflow on existing projects
- `/orca-new` - Create new project with optional GitHub setup
- `/orca-workflow` - Complete end-to-end: create + setup + workflow

When working with this system, focus on maintaining the stateless agent pattern and ensuring artifact consistency across workflow phases.
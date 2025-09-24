---
argument-hint: [project_description] [constraints] [clarification_mode]
description: Execute Orca workflow on existing project
---

# /orca-start

Bootstrap and orchestrate the full stateless Orca software development workflow using these parameters: $ARGUMENTS

Parse the arguments as:
1. project_description (required): Short description of the software/tool/feature to be developed
2. constraints (optional, default: "Solo developer, free tools"): Development constraints
3. clarification_mode (optional, default: true): Whether to pause for user clarification on ambiguous requirements

## Examples
```
/orca-start "REST API for task management"
/orca-start "Mobile-friendly web dashboard" "React, free hosting, responsive design"
/orca-start "Data visualization tool" "Python, matplotlib, CSV input" false
```

## Description
Executes the complete Orca multi-agent workflow orchestration system. This command runs all workflow phases with automatic startup validation and Archon-first task management.

## Workflow Phases
1. **Mandatory Startup Check**: Verifies Archon and Serena MCP servers
2. **Archon Project Initialization**: Creates project entry for task management
3. **Prompt Engineer Agent**: Defines all agents and their prompts
4. **Discovery Agent**: Gathers project understanding and domain context
5. **Requirements Agent**: Transforms discoveries into actionable requirements
6. **Story Grooming Agent**: Breaks requirements into manageable tasks
7. **Architecture Agent**: Designs system architecture and selects tech stack
8. **Engineer Review Agent**: Validates technical feasibility and quality
9. **Implementation Planning Agent**: Creates detailed execution plans

## Critical Rules
- **ARCHON-FIRST**: Creates and manages tasks in Archon MCP server
- **RESEARCH-DRIVEN**: Uses Archon RAG search before implementation decisions
- **STATELESS AGENTS**: Each phase operates independently with only necessary inputs
- **CLARIFICATION LOOPS**: Pauses for user input when requirements are ambiguous

## Generated Artifacts
- `agent_definitions.md`, `agent_prompts.md` (Prompt Engineering)
- `discovery.md` (Discovery)
- `requirements.md` (Requirements)
- `tasks.md` (Task Breakdown)
- `architecture.md`, `tech_stack.md` (Architecture)
- `task_review.md` (Engineering Review)
- `plan.md` (Implementation Planning)

## Prerequisites
- Archon MCP server running at http://localhost:8051/mcp
- Serena MCP server connected
- Current project initialized in both systems (run `/orca-startup` to verify)

Use this command to begin the complete Orca development workflow for existing projects.
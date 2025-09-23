---
argument-hint: [feature_description] [constraints] [clarification_mode]
description: Add new feature to existing Orca project using workflow
---

# /orca-add-feature

Execute the Orca workflow to add a new feature to an existing project using these parameters: $ARGUMENTS

Parse the arguments as:
1. feature_description (required): Description of the new feature to add
2. constraints (optional, default: "Solo developer, free tools"): Development constraints
3. clarification_mode (optional, default: true): Whether to pause for user clarification on ambiguous requirements

## Examples
```
/orca-add-feature "User authentication with JWT tokens"
/orca-add-feature "Real-time notifications" "WebSocket, free hosting"
/orca-add-feature "Data export to CSV" "Python pandas, CLI interface" false
```

## Description
Executes the complete Orca multi-agent workflow for adding features to existing projects. This command assumes the project already has Orca workflow files and focuses on feature development rather than initial project setup.

## Workflow Phases
1. **Mandatory Startup Check**: Verifies Archon and Serena MCP servers
2. **Feature Context Discovery**: Analyzes existing codebase and feature requirements
3. **Requirements Analysis**: Defines specific requirements for the new feature
4. **Task Planning**: Breaks feature into manageable development tasks
5. **Architecture Planning**: Designs feature integration with existing system
6. **Implementation Review**: Validates technical approach and compatibility
7. **Development Plan**: Creates detailed execution plan for feature implementation

## Key Differences from /orca-start
- **Existing Project Focus**: Works with established codebase and architecture
- **Feature-Scoped**: Concentrates on specific feature addition rather than full project
- **Integration-Aware**: Considers existing code patterns and architecture
- **Incremental Development**: Builds upon existing project structure

## Critical Rules
- **ARCHON-FIRST**: Creates feature tasks in existing Archon project
- **RESEARCH-DRIVEN**: Uses Archon RAG search for existing code patterns
- **STATELESS AGENTS**: Each phase operates independently with necessary inputs
- **CLARIFICATION LOOPS**: Pauses for user input when feature requirements are unclear
- **COMPATIBILITY-FOCUSED**: Ensures new feature integrates cleanly with existing code

## Generated Artifacts
- `feature_discovery.md` (Feature Context Analysis)
- `feature_requirements.md` (Feature Requirements)
- `feature_tasks.md` (Feature Task Breakdown)
- `feature_architecture.md` (Feature Integration Design)
- `feature_review.md` (Implementation Review)
- `feature_plan.md` (Development Execution Plan)

## Prerequisites
- Existing project with Orca workflow files
- Archon MCP server running at http://localhost:8051/mcp
- Serena MCP server connected
- Project already initialized in both MCP systems

## Workflow Execution
This command executes a modified version of the StartWorkflow function, adapted for feature development:

```markdown
## FeatureWorkflow Function

Execute specialized agents for feature development:

1. **Startup Validation**: Verify MCP servers and existing project setup
2. **Feature Discovery Agent**: Analyze existing codebase and understand feature context
3. **Feature Requirements Agent**: Define specific feature requirements and acceptance criteria
4. **Feature Task Agent**: Break feature into development tasks and user stories
5. **Feature Architecture Agent**: Design feature integration and technical approach
6. **Feature Review Agent**: Validate technical feasibility and code compatibility
7. **Feature Planning Agent**: Create detailed implementation roadmap

Each agent produces feature-specific artifacts and integrates with existing Archon project tasks.
```

## Usage Notes
- Run this command from within an existing project directory
- Ensure the project has been initialized with Orca workflow files
- The command will create feature-specific tasks in your existing Archon project
- Generated artifacts will be prefixed with "feature_" to distinguish from project-level artifacts

Use this command to systematically add new features to existing Orca-managed projects.
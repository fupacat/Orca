# /orca-workflow

Complete end-to-end workflow that creates a new project, sets up all tools, and executes the full Orca development workflow.

## Usage
```
/orca-workflow <project_name> <project_path> <project_description> [constraints] [clarification_mode] [github_setup]
```

## Parameters
- **project_name** (required): Name of the new project (used as directory name)
- **project_path** (required): Parent directory where project should be created
- **project_description** (required): Short description of the software to be developed
- **constraints** (optional): Development constraints, e.g., "solo developer, free tools"
- **clarification_mode** (optional): true/false - pause for clarification on ambiguous requirements (default: true)
- **github_setup** (optional): true/false - automatically set up GitHub repository (default: true)

## Examples
```
/orca-workflow "TaskAPI" "C:\dev" "REST API for task management"
/orca-workflow "DataDash" "/Users/dev" "Data visualization dashboard" "Python, free hosting" false
/orca-workflow "MobileApp" "C:\projects" "Mobile-friendly web app" "React, responsive design, PWA"
```

## Description
The ultimate Orca command that combines project creation, tool setup, and complete workflow execution in one seamless process. This creates a fully functional project ready for implementation.

## Complete Process
### Phase 1: Project Creation
- Creates new project directory with all necessary files
- Sets up Claude Code, Serena, and Archon integration
- Initializes both MCP systems with project context

### Phase 2: Environment Switch
- Switches Claude Code to the new project directory
- Verifies all MCP servers are connected in new context
- Validates project-specific configurations are loaded

### Phase 3: Dependency Validation
- Runs comprehensive dependency checks
- Verifies Archon project creation and Serena onboarding
- Ensures all systems are fully operational

### Phase 4: Complete Workflow Execution
Runs all Orca workflow phases:
1. **Mandatory Startup Checks**: Verifies all dependencies
2. **Archon Project Initialization**: Creates task management structure
3. **Prompt Engineering**: Defines all agents with Archon integration
4. **Discovery**: Gathers comprehensive project understanding
5. **Requirements Analysis**: Transforms discoveries into specifications
6. **Task Breakdown**: Creates manageable user stories and tasks
7. **Architecture Design**: Designs system and selects technology stack
8. **Engineering Review**: Validates technical feasibility and quality
9. **Implementation Planning**: Creates detailed execution roadmap

## Generated Deliverables
### Project Infrastructure
- Complete project directory with Orca integration
- All MCP servers properly configured and initialized
- Standardized documentation and configuration files

### Workflow Artifacts
- `discovery.md` - Project understanding and domain context
- `requirements.md` - Detailed, actionable requirements
- `tasks.md` - Broken down user stories and implementation tasks
- `architecture.md` - System architecture and design decisions
- `tech_stack.md` - Technology selection and justification
- `task_review.md` - Engineering review and validation
- `plan.md` - Implementation roadmap and execution plan

## Success Criteria
- ✅ **Project Infrastructure**: New project with all necessary files and configurations
- ✅ **Tool Integration**: Claude Code, Serena, and Archon properly configured
- ✅ **MCP Initialization**: Both systems initialized with project context
- ✅ **Workflow Completion**: All phases executed and artifacts generated
- ✅ **Ready for Implementation**: Project ready with detailed implementation plan

## Prerequisites
- Archon MCP server running at http://localhost:8051/mcp
- Serena MCP server available
- Write permissions to the specified project path

## Output
Provides comprehensive summary with:
- **Project Location**: Full path to created project
- **Generated Artifacts**: List of all workflow artifacts created
- **Tool Status**: Confirmation that all MCP servers are operational
- **Next Steps**: Clear instructions for beginning implementation

This command gives you a completely set up project ready for development with all workflow phases completed and a detailed implementation plan in hand.
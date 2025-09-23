# 🐋 Orca Workflow Orchestration System

**Sophisticated multi-agent workflow orchestration for structured software development**

Orca is a powerful, stateless workflow system that orchestrates specialized AI agents through the complete software development lifecycle. Built for Claude Code with comprehensive MCP server integration, Orca transforms project requirements into production-ready software through systematic, AI-driven phases.

## 🚀 Key Features

- **🤖 Multi-Agent Architecture**: Specialized agents for each development phase
- **📋 Task-Driven Development**: Integrated with Archon MCP for comprehensive task management
- **🔍 Research-Driven**: Built-in knowledge base search and code example discovery
- **⚡ Slash Command Interface**: Easy-to-use commands for all workflow operations
- **🔧 MCP Integration**: Deep integration with Archon and Serena MCP servers
- **📂 Template System**: Standardized project scaffolding and configurations
- **🔄 GitHub Integration**: Automatic repository setup with CI/CD workflows
- **🎯 Stateless Design**: Each workflow phase operates independently

## 🎭 Specialized Agents

1. **Prompt Engineer Agent** - Creates and refines prompts for all workflow agents
2. **Discovery Agent** - Gathers comprehensive project understanding and domain context
3. **Requirements Agent** - Transforms discoveries into detailed, actionable requirements
4. **Story Grooming Agent** - Breaks requirements into manageable tasks and user stories
5. **Architecture Agent** - Designs system architecture and selects technology stack
6. **Engineer Review Agent** - Validates technical feasibility and quality
7. **Implementation Planning Agent** - Creates detailed execution plans and roadmaps

## 🚀 Quick Start

### Prerequisites

1. **Claude Code** - Latest version with MCP support
2. **Archon MCP Server** - Running at `http://localhost:8051/mcp`
3. **Serena MCP Server** - Available via uvx
4. **GitHub CLI** (optional) - For GitHub integration: `gh auth login`

### Installation

1. **Clone Orca System**:
   ```bash
   git clone https://github.com/[username]/Orca.git
   cd Orca
   ```

2. **Verify Dependencies**:
   ```bash
   /orca-deps
   ```

3. **System Health Check**:
   ```bash
   /orca-startup
   ```

### Creating Your First Project

**Option 1: Complete Workflow (Recommended)**
```bash
/orca-workflow "MyProject" "C:\dev" "REST API for task management" "Solo dev, free tools"
```

**Option 2: Step-by-Step**
```bash
# Create project structure
/orca-new "MyProject" "C:\dev" "REST API for task management"

# Navigate to project
cd C:\dev\MyProject

# Execute workflow
/orca-start "REST API for task management" "Solo dev, free tools"
```

## 📋 Available Commands

### Essential Commands
- **`/orca-deps`** - Quick MCP server validation
- **`/orca-startup`** - Comprehensive system verification

### Workflow Commands
- **`/orca-start`** - Execute workflow on existing project
- **`/orca-new`** - Create new project with setup
- **`/orca-workflow`** - Complete end-to-end: create + setup + workflow

### GitHub Integration
- **`/orca-github setup`** - Complete GitHub setup for current project
- **`/orca-github create`** - Create new GitHub repository
- **`/orca-github connect`** - Connect to existing repository

## 🏗️ Architecture

### Core Design Principles
- **Stateless Agents**: Each agent operates independently with only necessary inputs
- **Artifact-Driven**: Agents produce specific markdown artifacts for each phase
- **Template-Based**: Standardized agent definitions and prompts for consistency
- **Clarification Loops**: Built-in pause mechanisms for ambiguity resolution

### MCP Server Integration
- **Archon** (HTTP): Project and task management, knowledge base search
- **Serena** (stdio): Semantic code operations, project context management

### File Structure
```
Orca/
├── .claude/
│   └── commands/          # Slash command definitions
├── templates/             # Project templates and configurations
│   ├── agent_definitions.md
│   ├── agent_prompts.md
│   ├── CLAUDE_template.md
│   ├── README_template.md
│   └── serena_memory_*.md
├── archon_rules.md        # Critical Archon-first development rules
├── start.md              # Main workflow orchestration
├── startup_check.md      # System verification
├── create_new_project.md # Project creation logic
├── new_project_workflow.md # Complete workflow
└── CLAUDE.md             # Claude Code project guidance
```

## 📊 Workflow Phases

### 1. Discovery Phase
- Comprehensive project understanding
- Domain context gathering
- Stakeholder requirement analysis
- **Output**: `discovery.md`

### 2. Requirements Phase
- Transform discoveries into actionable specifications
- Define clear acceptance criteria
- Identify technical constraints
- **Output**: `requirements.md`

### 3. Task Breakdown Phase
- Break requirements into manageable user stories
- Create implementation tasks with priorities
- Establish development milestones
- **Output**: `tasks.md`

### 4. Architecture Phase
- Design system architecture
- Select appropriate technology stack
- Define technical patterns and conventions
- **Output**: `architecture.md`, `tech_stack.md`

### 5. Engineering Review Phase
- Validate technical feasibility
- Review architecture decisions
- Assess quality and maintainability
- **Output**: `task_review.md`

### 6. Implementation Planning Phase
- Create detailed execution roadmap
- Establish development timeline
- Define deployment strategies
- **Output**: `plan.md`

## 🔧 Configuration

### MCP Server Setup
```json
{
  "mcpServers": {
    "archon": {
      "type": "http",
      "command": "http://localhost:8051/mcp"
    },
    "serena": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "ide-assistant", "--project", "$(pwd)"]
    }
  }
}
```

### Archon-First Development
⚠️ **CRITICAL**: All development follows the Archon-first rule:
1. Check Archon MCP server availability before any task
2. Use Archon for ALL project and task management
3. Research using Archon RAG before implementation
4. Follow task-driven development workflow

## 🤝 Contributing

### Development Workflow
1. **Read Critical Rules**: Start with `archon_rules.md`
2. **Verify System**: Run `/orca-startup` before any changes
3. **Follow Archon Workflow**: Use Archon for task management
4. **Research First**: Use Archon RAG search before implementation
5. **Maintain Stateless Pattern**: Keep agents independent

### Project Standards
- **Documentation**: Update relevant memory files for any changes
- **Templates**: Maintain consistency across all template files
- **Testing**: Verify slash commands work correctly
- **Security**: Follow security best practices for MCP integration

## 📚 Documentation

- **[CLAUDE.md](./CLAUDE.md)** - Claude Code project guidance
- **[archon_rules.md](./archon_rules.md)** - Critical development workflow rules
- **[templates/](./templates/)** - Project templates and configurations
- **Slash Commands** - Individual command documentation in `.claude/commands/`

## 🔒 Security Features

- **Private Repositories**: Default to private for all GitHub integration
- **Dependency Scanning**: Automated vulnerability checks in CI/CD
- **Secret Management**: Proper .gitignore and secret handling
- **MCP Security**: Secure server communication protocols

## 🚀 Advanced Usage

### Custom Project Templates
1. Modify templates in `templates/` directory
2. Update template variables for project-specific needs
3. Test with `/orca-new` command

### Extending Workflow Agents
1. Update `agent_definitions.md` with new agent roles
2. Add corresponding prompts in `agent_prompts.md`
3. Ensure Archon integration in all agent prompts

### Custom Slash Commands
1. Create new command file in `.claude/commands/`
2. Follow existing command documentation format
3. Update main documentation with new command

## 🐛 Troubleshooting

### Common Issues

**MCP Server Connection**
```bash
# Check server status
/orca-deps

# Restart servers if needed
claude mcp list
claude mcp remove archon && claude mcp add archon -- http://localhost:8051/mcp
```

**Project Initialization**
```bash
# Comprehensive system check
/orca-startup

# Manual Archon project creation if needed
# Manual Serena onboarding if needed
```

**GitHub Integration**
```bash
# Verify GitHub CLI
gh auth status

# Re-authenticate if needed
gh auth login
```

## 📄 License

[License to be determined]

## 🏆 Acknowledgments

- **Claude Code** - Primary orchestration platform
- **Archon MCP Server** - Task and project management
- **Serena MCP Server** - Semantic code operations
- **GitHub** - Version control and CI/CD platform

---

**🤖 Generated with Orca Workflow Orchestration System**

*Transforming software development through intelligent multi-agent workflows*
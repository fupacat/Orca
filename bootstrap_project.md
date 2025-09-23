# Project Bootstrap System

{
  "name": "BootstrapProject",
  "description": "Create a new project directory with all necessary Orca workflow files, set up Claude Code, Serena, Archon, and initialize the development environment.",
  "parameters": [
    {
      "name": "project_name",
      "type": "string",
      "description": "Name of the new project (will be used as directory name and project identifier)"
    },
    {
      "name": "project_path",
      "type": "string",
      "description": "Parent directory path where the new project should be created (e.g., 'C:\\Users\\username\\projects')"
    },
    {
      "name": "project_description",
      "type": "string",
      "description": "Short description of the software/tool/feature to be developed"
    },
    {
      "name": "constraints",
      "type": "string",
      "description": "Development constraints, e.g., solo developer, free/open tools, target platform"
    }
  ],
  "prompt": "You are bootstrapping a complete Orca workflow project. Follow these steps in exact order:\n\n## Phase 1: Project Directory Setup\n\n1. **Create Project Directory Structure**:\n   ```bash\n   mkdir -p \"{project_path}/{project_name}\"\n   cd \"{project_path}/{project_name}\"\n   mkdir -p .claude .serena templates docs\n   ```\n\n2. **Copy Core Orca Files**:\n   - Copy `start.md`, `startup_check.md`, `check_dependencies.md` from Orca template\n   - Copy `templates/` directory contents (agent_definitions.md, agent_prompts.md, .claude.json)\n   - Create project-specific `CLAUDE.md` with project information\n   - Create initial `README.md` with project overview\n\n## Phase 2: Tool Configuration\n\n3. **Setup Claude Code Configuration**:\n   ```bash\n   # Copy and customize .claude.json with project-specific settings\n   cp templates/.claude.json .claude/\n   # Update project path in Serena configuration\n   ```\n\n4. **Setup Serena MCP Configuration**:\n   ```yaml\n   # Create .serena/project.yml\n   project_name: {project_name}\n   language: python  # or appropriate language based on project type\n   description: {project_description}\n   ```\n\n5. **Configure Archon Integration**:\n   - Verify Archon server availability at http://localhost:8051/mcp\n   - Create initial Archon project entry using manage_project\n\n## Phase 3: MCP Server Setup\n\n6. **Initialize Claude Code MCP Servers**:\n   ```bash\n   # Add Archon MCP server\n   claude mcp add archon -- http://localhost:8051/mcp\n   \n   # Add Serena MCP server with project path\n   claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)\n   ```\n\n7. **Verify MCP Server Connectivity**:\n   ```bash\n   claude mcp list\n   # Should show both archon and serena as connected\n   ```\n\n## Phase 4: Project Initialization\n\n8. **Create Initial Project Documentation**:\n   - `PROJECT_BRIEF.md` - Contains project_description and constraints\n   - `WORKFLOW_STATUS.md` - Tracks current workflow phase\n   - `.gitignore` - Standard gitignore for the project type\n\n9. **Initialize Git Repository** (optional):\n   ```bash\n   git init\n   git add .\n   git commit -m \"Initial Orca workflow project setup\"\n   ```\n\n## Phase 5: Environment Validation\n\n10. **Run Dependency Checks**:\n    - Execute CheckDependencies to verify all systems are operational\n    - Test Archon connectivity with health_check\n    - Test Serena connectivity with basic file operations\n\n11. **Create Project in Archon**:\n    - Use mcp__archon__manage_project to create new project entry\n    - Set up initial project metadata and description\n\n## Phase 6: Ready for Workflow\n\n12. **Final Setup Verification**:\n    - Confirm all MCP servers are connected\n    - Verify project files are in place\n    - Test that StartWorkflow can be executed\n\n13. **Switch to New Project**:\n    - Navigate Claude Code to the new project directory\n    - Confirm all configurations are loaded\n    - Display success message with next steps\n\n## Success Criteria:\n- ✅ New project directory created with all Orca files\n- ✅ Claude Code configured with MCP servers\n- ✅ Serena and Archon connected and functional\n- ✅ Project ready to execute StartWorkflow\n- ✅ All dependency checks pass\n\n## Output:\nReturn the full path to the new project and confirmation that it's ready for workflow execution."
}
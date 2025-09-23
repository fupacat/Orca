# New Project Workflow

{
  "name": "NewProjectWorkflow",
  "description": "Complete end-to-end workflow that creates a new project, sets up all tools, and begins the Orca development workflow.",
  "parameters": [
    {
      "name": "project_name",
      "type": "string",
      "description": "Name of the new project (will be used as directory name and project identifier)"
    },
    {
      "name": "project_path",
      "type": "string",
      "description": "Parent directory path where the new project should be created (e.g., 'C:\\\\Users\\\\username\\\\projects')"
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
    },
    {
      "name": "clarification_mode",
      "type": "boolean",
      "description": "If true, workflow will pause and ask the user for clarification when ambiguous requirements are detected"
    }
  ],
  "prompt": "You are executing the complete Orca new project workflow. This combines project creation, tool setup, and workflow execution in one seamless process.\n\n## Phase 1: Project Creation\n\n**Execute CreateNewProject function** with parameters:\n- project_name: {project_name}\n- project_path: {project_path}\n- project_description: {project_description}\n- constraints: {constraints}\n- auto_start_workflow: false\n\n**Validation**: Ensure project creation completed successfully before proceeding.\n\n## Phase 2: Environment Switch\n\n1. **Switch to New Project Directory**:\n   ```bash\n   cd \"{project_path}/{project_name}\"\n   ```\n\n2. **Verify Claude Code Context**:\n   - Confirm Claude Code is now operating in the new project\n   - Verify all MCP servers are connected in the new context\n   - Test that project-specific configurations are loaded\n\n## Phase 3: Dependency Validation\n\n**Execute CheckDependencies function** to verify:\n- Archon MCP server connectivity\n- Serena MCP server functionality\n- Project configuration validity\n- All required files are present\n\n**Verify MCP System Initialization**:\n```\n# Verify Archon project was created and store project_id\nmcp__archon__find_projects(query=\"{project_name}\")\n\n# Verify Serena onboarding completed\nmcp__serena__check_onboarding_performed()\n\n# Verify Serena project access\nmcp__serena__list_dir(\".\", recursive=false)\n```\n\n**Critical**: Do not proceed if any dependencies fail validation.\n\n## Phase 4: Workflow Execution\n\n**Execute StartWorkflow function** with the provided parameters:\n- project_description: {project_description}\n- constraints: {constraints}\n- clarification_mode: {clarification_mode}\n\nThis will run through all Orca workflow phases:\n1. Mandatory startup checks\n2. Prompt engineering\n3. Discovery\n4. Requirements analysis\n5. Task breakdown\n6. Architecture design\n7. Engineering review\n8. Implementation planning\n\n## Success Criteria\n\n✅ **Project Infrastructure**: New project directory with all necessary files\n✅ **Tool Integration**: Claude Code, Serena, and Archon properly configured\n✅ **Workflow Completion**: All phases executed and artifacts generated\n✅ **Ready for Development**: Project ready for implementation phase\n\n## Error Recovery\n\nIf any phase fails:\n1. **Project Creation Issues**: Check directory permissions and paths\n2. **MCP Server Issues**: Run troubleshooting steps from startup_check.md\n3. **Workflow Issues**: Verify all dependencies and retry from the failed phase\n\n## Final Output\n\nProvide a comprehensive summary:\n- **Project Location**: Full path to created project\n- **Generated Artifacts**: List of all workflow artifacts created\n- **Next Steps**: Clear instructions for beginning implementation\n- **Tool Status**: Confirmation that all MCP servers are operational\n\nThe user should have a completely set up project ready for development with all workflow phases completed and implementation plan in hand."
}
# Orca Style and Conventions

## File Naming Conventions
- **Markdown files**: Use snake_case with .md extension
- **Function definitions**: CamelCase (e.g., StartWorkflow, CheckDependencies)
- **Artifacts**: lowercase with underscores (e.g., discovery.md, requirements.md)
- **Templates**: Use descriptive names with _template suffix

## Documentation Style
- **Headers**: Use # for main sections, ## for subsections
- **Function definitions**: JSON-like structure with name, description, parameters, and prompt
- **Emphasis**: Use **bold** for critical information and warnings
- **Code blocks**: Use ```bash, ```json, or ```cmd for different contexts

## Agent Design Patterns
- **Stateless**: Each agent operates independently with only necessary inputs
- **Artifact-focused**: Each agent produces specific deliverable files
- **Template-driven**: Use standardized prompts and definitions
- **Clarification-aware**: Built-in pause mechanisms for ambiguous requirements

## Critical Rules Hierarchy
1. **Archon-first rule** (from archon_rules.md) - OVERRIDES all other instructions
2. **MCP dependency checks** - Must verify servers before workflow execution
3. **Stateless agent pattern** - Maintain independence between workflow phases
4. **Artifact consistency** - Ensure standardized output formats

## Markdown Structure Standards
- Always include clear section headers
- Use bullet points for lists and steps
- Include parameter descriptions for functions
- Maintain consistent indentation (2 spaces)
- Use code blocks for command examples

## Configuration Management
- Store MCP server config in templates/.claude.json
- Keep agent definitions separate from prompts
- Use template files for project scaffolding
- Maintain clear separation between system config and workflow logic

## Error Handling Conventions
- Always include startup dependency checks
- Provide clear error messages and troubleshooting guidance
- Implement graceful failure modes
- Include fallback options when possible
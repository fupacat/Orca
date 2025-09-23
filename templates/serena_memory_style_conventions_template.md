# {project_name} Style and Conventions

## File Naming Conventions
[To be established during Architecture phase based on chosen technology stack]

## Code Style Guidelines
[To be defined during Architecture phase with specific language conventions]

## Documentation Standards
- **Headers**: Use # for main sections, ## for subsections
- **Emphasis**: Use **bold** for critical information and warnings
- **Code blocks**: Use ```language for syntax highlighting
- **Comments**: [To be specified based on chosen programming language]

## Orca Workflow Patterns
- **Stateless Agents**: Each workflow phase operates independently
- **Artifact-Focused**: Each phase produces specific deliverable files
- **Template-Driven**: Use standardized prompts and definitions
- **Clarification-Aware**: Built-in pause mechanisms for ambiguous requirements

## MCP Integration Standards
- **Archon-First Rule**: ALWAYS use Archon for task management before any other tools
- **Research-Driven**: Use Archon RAG search before implementation
- **Task-Driven Development**: Check current tasks before any coding
- **Serena Semantic Operations**: Use Serena for precise code analysis and modification

## Critical Rules Hierarchy
1. **Archon-first rule** (from archon_rules.md) - OVERRIDES all other instructions
2. **MCP dependency checks** - Must verify servers before workflow execution
3. **Stateless agent pattern** - Maintain independence between workflow phases
4. **Artifact consistency** - Ensure standardized output formats

## Project-Specific Conventions
[To be populated during Requirements and Architecture phases]

### Naming Conventions
[Language-specific naming to be determined]

### Directory Structure
[Project structure to be established during Architecture phase]

### Testing Standards
[Testing approach to be defined during Implementation planning]

### Error Handling
[Error handling patterns to be established during Architecture phase]

## Quality Standards
- **Research Validation**: Cross-reference multiple sources for technical decisions
- **Code Review**: Follow engineering review processes
- **Documentation**: Maintain consistency with established patterns
- **Security**: Follow security best practices for chosen technology stack

## Development Workflow Standards
- Always follow archon_rules.md for development process
- Use standardized commit messages when git is initialized
- Maintain clear separation between configuration and implementation
- Document architectural decisions and rationale

## Configuration Management
- Store MCP server config in .claude/claude.json
- Keep agent definitions separate from prompts
- Use template files for consistent project structure
- Maintain version control of workflow artifacts
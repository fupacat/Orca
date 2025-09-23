# {project_name} Task Completion Guidelines

## Pre-Task Requirements

### CRITICAL: Always Follow Archon-First Rule
1. **BEFORE any task**: Check Archon MCP server availability
2. **READ** archon_rules.md and follow ALL Archon development protocols
3. **USE** Archon for project and task management as PRIMARY system
4. **RESEARCH-DRIVEN**: Always use Archon RAG search before implementation

### Startup Validation
- Execute `StartupCheck` function to verify MCP server availability
- Ensure both Archon and Serena servers are connected
- Verify project exists in Archon system
- Do not proceed if startup check fails

## Task Execution Workflow

### 1. Archon Task Management Cycle
```bash
# Check current task status for this project
mcp__archon__find_tasks(project_id="[project_id]", filter_by="status", filter_value="todo")

# Mark task as in progress
mcp__archon__manage_task("update", task_id="[task_id]", status="doing")

# Research for task using project context
mcp__archon__rag_search_code_examples(query="[task_specific_query]")
mcp__archon__rag_search_knowledge_base(query="[architecture_patterns]")

# Implement based on research

# Mark for review
mcp__archon__manage_task("update", task_id="[task_id]", status="review")
```

### 2. Research Requirements
- Use `mcp__archon__rag_search_knowledge_base()` for architecture and best practices
- Use `mcp__archon__rag_search_code_examples()` for implementation patterns
- Keep match_count low (2-5) for focused results
- Cross-reference multiple sources for validation

### 3. Implementation Standards
- Follow patterns discovered in research
- Maintain consistency with established project conventions
- Use Serena for precise code operations and symbol manipulation
- Follow the technology stack chosen during Architecture phase

## Completion Criteria

### For Orca Workflow Tasks
- All MCP server dependencies verified
- Startup checks passed
- Required artifacts produced in correct format
- Research conducted using Archon knowledge base
- Task status updated in Archon system

### For Development Tasks
- Code follows project style conventions [to be established]
- Implementation based on Archon research findings
- Tests written and passing [testing framework to be determined]
- Documentation updated as needed
- Security considerations addressed

### For Documentation Tasks
- Markdown follows established style conventions
- All required sections included
- Code examples properly formatted
- Critical warnings highlighted with **bold**

## Post-Completion Actions

### Archon Updates
- Update task status to "review" or "done"
- Document any architectural decisions made
- Create follow-up tasks if scope expanded
- Update project features if applicable using `mcp__archon__manage_project`

### Quality Verification
- Validate all produced artifacts
- Check file naming conventions
- Ensure no missing dependencies
- Verify integration with existing codebase

### Technology-Specific QA
[To be populated during Architecture phase based on chosen tech stack]

#### Build Commands
[To be defined during Architecture phase]

#### Test Commands
[To be established during Implementation phase]

#### Lint/Format Commands
[To be specified based on chosen tools]

## Error Recovery

### MCP Server Issues
- If Archon unavailable: Provide troubleshooting guidance and stop
- If Serena disconnected: Reconnect using claude mcp commands
- Verify server health before retrying operations

### Development Issues
- If build fails: Check dependencies and configuration
- If tests fail: Address failing tests before marking complete
- If integration issues: Review architecture decisions and compatibility

### Workflow Issues
- If artifacts malformed: Regenerate following templates
- If scope unclear: Break into smaller, clearer subtasks
- Use clarification_mode in workflows when requirements are ambiguous

## Documentation Requirements

### When Task Involves Project Changes
- Update relevant memory files using `mcp__serena__write_memory`
- Maintain style and convention consistency
- Include command examples where applicable
- Highlight critical rules and dependencies

### Archon Project Updates
- Update project description if scope changes
- Add new features to project feature list
- Document major architectural decisions
- Maintain task dependencies and relationships

## Success Metrics
- Task completed according to acceptance criteria
- All research findings documented and applied
- Code quality meets project standards
- Integration successful with no breaking changes
- Documentation updated and accurate
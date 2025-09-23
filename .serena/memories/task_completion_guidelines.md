# Task Completion Guidelines for Orca

## Pre-Task Requirements
### CRITICAL: Always Follow Archon-First Rule
1. **BEFORE any task**: Check Archon MCP server availability
2. **READ** archon_rules.md and follow ALL Archon development protocols  
3. **USE** Archon for project and task management as PRIMARY system
4. **RESEARCH-DRIVEN**: Always use Archon RAG search before implementation

### Startup Validation
- Execute `StartupCheck` function to verify MCP server availability
- Ensure both Archon and Serena servers are connected
- Do not proceed if startup check fails

## Task Execution Workflow

### 1. Archon Task Management Cycle
```bash
# Check current task status
archon:manage_task(action="list", filter_by="status", filter_value="todo")

# Mark task as in progress  
archon:manage_task(action="update", task_id="...", status="doing")

# Research for task
archon:search_code_examples() + archon:perform_rag_query()

# Implement based on research

# Mark for review
archon:manage_task(action="update", task_id="...", status="review")
```

### 2. Research Requirements
- Use `archon:perform_rag_query()` for architecture and best practices
- Use `archon:search_code_examples()` for implementation patterns
- Keep match_count low (2-5) for focused results
- Cross-reference multiple sources for validation

### 3. Implementation Standards
- Follow patterns discovered in research
- Maintain stateless agent design
- Produce standardized artifact files
- Ensure artifact consistency across workflow phases

## Completion Criteria

### For Workflow Functions
- All MCP server dependencies verified
- Startup checks passed
- All required artifacts produced in correct format
- Clarification loops properly handled
- Archon project and tasks created/updated

### For Agent Development
- Agent definitions follow template structure
- Prompts include Archon-first principles
- Stateless operation maintained
- Clear input/output specifications

### For Documentation
- Markdown follows style conventions
- All required sections included
- Code examples properly formatted
- Critical warnings highlighted with **bold**

## Post-Completion Actions

### Archon Updates
- Update task status to "review" or "done"
- Document any architectural decisions
- Create follow-up tasks if scope expanded
- Update project features if applicable

### Quality Verification
- Validate all produced artifacts
- Check artifact file naming conventions
- Ensure no missing dependencies
- Verify workflow can proceed to next phase

### No Traditional QA
- No build commands to run (configuration-driven system)
- No test suites to execute  
- No linting or formatting tools
- No git commits (not a git repository)

## Error Recovery
- If Archon unavailable: Provide troubleshooting guidance and stop
- If artifacts malformed: Regenerate following templates
- If workflow blocked: Pause and request clarification
- If scope unclear: Break into smaller, clearer subtasks

## Documentation Requirements
When task involves modifying system:
- Update relevant memory files
- Maintain style and convention consistency  
- Include command examples where applicable
- Highlight critical rules and dependencies
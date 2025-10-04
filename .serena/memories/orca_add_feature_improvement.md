# Orca Add-Feature Command Improvement

## Issue Identified
Date: 2025-10-01

### Current Behavior
The `/orca-add-feature` command produces comprehensive feature planning artifacts but does **not** produce an executable `plan.md` file compatible with `/orca-execute`.

**Current Outputs**:
- `feature_discovery.md` - Feature context analysis
- `feature_requirements.md` - Requirements specification
- `feature_tasks.md` - Task breakdown with dependencies
- `feature_architecture.md` - Architecture design
- `feature_review.md` - Technical feasibility review
- `feature_plan.md` - **Project management plan** (not executable)

### Problem
The `feature_plan.md` is a project management document with:
- Team allocation schedules
- Daily execution plans
- Communication strategies
- Deployment phases

It is **NOT** an executable implementation plan in Orca's format that can be consumed by `/orca-execute`.

### Required Improvement
The `/orca-add-feature` command should produce an additional artifact:
- **`plan.md`** or **`impl_plan.md`** - Executable implementation plan

This file should follow Orca's implementation plan format with:
1. Task specifications in CompleteTask format
2. Full embedded context per task
3. Specific implementation steps
4. Code examples and patterns
5. Test specifications
6. Acceptance criteria
7. Dependencies clearly defined
8. Parallel execution layers

### Expected Workflow
```
User: /orca-add-feature "state tracking system"
↓
Orca executes 6 phases:
1. Discovery
2. Requirements
3. Task Planning
4. Architecture
5. Review
6. Development Plan + EXECUTABLE PLAN ← NEW
↓
Output: 7 artifacts including executable plan.md
↓
User: /orca-execute plan.md
↓
Orca executes implementation with parallel agents
```

### Benefits
- Seamless workflow from feature planning to execution
- Eliminates manual conversion step
- Leverages Orca's parallel execution capabilities immediately
- Consistent with Orca's end-to-end automation philosophy

### Implementation Notes
- Phase 6 (Development Plan) should generate TWO outputs:
  - `feature_plan.md` (project management plan)
  - `plan.md` (executable implementation plan)
- The executable plan should use the task breakdown from `feature_tasks.md`
- Each task should be converted to CompleteTask format with full context
- Plan should be structured for `/orca-execute` consumption

### Priority
HIGH - This is a critical gap in the feature workflow that prevents immediate execution of planned features.

### Related Commands
- `/orca-add-feature` - Needs enhancement
- `/orca-execute` - Consumer of the executable plan
- `/orca-preview` - Should work with generated plans
- `/orca-validate` - Should validate generated plans

---
argument-hint: [plan_path] [execution_strategy]
description: Preview implementation plan execution with timing estimates
---

# /orca-preview

Generate detailed execution preview showing parallel coordination and timing estimates using these parameters: $ARGUMENTS

Parse the arguments as:
1. plan_path (optional, default: "./plan.md"): Path to implementation plan file
2. execution_strategy (optional, default: "hybrid"): Strategy for preview analysis

## Examples
```
/orca-preview
/orca-preview "./api_plan.md" "aggressive"
/orca-preview "plan.md" "conservative"
```

## Description
Analyzes implementation plans to show how Orca's parallel orchestration would execute tasks, including dependency graphs, execution layers, timing estimates, and parallelization efficiency.

## Preview Information
- **Task Dependency Graph**: Visual representation of task relationships
- **Execution Layers**: Parallel execution groups with task assignments
- **Timing Estimates**: Duration predictions for each layer and overall execution
- **Parallelization Analysis**: Efficiency metrics and optimization opportunities
- **Resource Requirements**: Agent allocation and utilization projections
- **Quality Gate Timeline**: When quality validations will occur

## Sample Output Format
```
🚀 Execution Preview: API Development Plan
========================================

📊 Overview:
- Total Tasks: 12
- Execution Layers: 4
- Max Parallelism: 4 tasks
- Estimated Duration: 2.3 hours (vs 8.5 hours sequential)
- Parallel Efficiency: 87%

🔗 Dependency Analysis:
- No circular dependencies detected
- 8 tasks can run in parallel
- 4 tasks have sequential dependencies

⚡ Execution Layers:
Layer 1 (25 min) - 4 parallel tasks:
  ├── Setup database schema (20 min)
  ├── Create base API structure (15 min)
  ├── Setup authentication middleware (25 min)
  └── Configure testing framework (10 min)

Layer 2 (35 min) - 3 parallel tasks:
  ├── Implement user endpoints (35 min)
  ├── Create data validation (25 min)
  └── Add API documentation (20 min)

[Additional layers...]

🎯 Quality Gates:
- TDD validation after each layer
- Security scan at layer 3
- Performance testing in final layer
```

Use this command to understand execution complexity and optimize plans before running /orca-execute.
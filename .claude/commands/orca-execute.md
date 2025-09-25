---
argument-hint: [plan_path] [execution_strategy] [max_agents]
description: Execute implementation plan with parallel orchestration
---

# /orca-execute

Execute an existing implementation plan using Orca's parallel orchestration engine with these parameters: $ARGUMENTS

Parse the arguments as:
1. plan_path (optional, default: "./plan.md"): Path to implementation plan file
2. execution_strategy (optional, default: "hybrid"): Parallel execution strategy - "aggressive", "conservative", "hybrid", or "sequential"
3. max_agents (optional, default: 3): Maximum number of parallel development agents

## Examples
```
/orca-execute
/orca-execute "./custom_plan.md" "aggressive" 5
/orca-execute "plan.md" "conservative" 2
/orca-execute "./project_plans/api_implementation.md" "hybrid"
```

## Description
Executes implementation plans created by Orca's planning workflow using intelligent parallel orchestration. Provides 3-5x faster development through stateless task coordination, dependency analysis, and multi-agent execution.

## Execution Strategies
- **aggressive**: Maximum parallelization with minimal safety margins (fastest, higher risk)
- **conservative**: Safer execution with more sequential dependencies (slower, more stable)
- **hybrid** (default): Balanced approach optimizing both speed and reliability
- **sequential**: Traditional one-task-at-a-time execution (slowest, most predictable)

## Key Features
- **Intelligent Parallelization**: Automatic dependency analysis and parallel layer creation
- **Stateless Task Execution**: Each task contains complete context for independent execution
- **Quality Gate Enforcement**: TDD compliance, security validation, performance checks
- **Real-time Monitoring**: Live progress tracking with metrics and alerting
- **Multi-agent Coordination**: Load-balanced agent assignment with resource optimization
- **Resume Capability**: Can resume interrupted executions from checkpoint

## Generated Outputs
- **execution_summary.md**: Complete execution results and metrics
- **Real-time Progress**: Live task completion status and performance metrics
- **Quality Reports**: TDD compliance, security scan results, code quality scores
- **Session Archive**: Detailed execution logs in `.orca/executions/[session_id]/`

## Prerequisites
- Implementation plan file (plan.md) exists in project
- Archon MCP server running at http://localhost:8051/mcp
- Serena MCP server connected
- Python environment with development tools

## Advanced Usage

### Preview Execution
```
# Get execution preview without running
/orca-preview
/orca-preview "./plan.md" "aggressive"
```

### Validate Plan
```
# Validate plan executability
/orca-validate
/orca-validate "./custom_plan.md"
```

### Resume Execution
```
# Resume interrupted execution
/orca-resume [session_id]
```

## Performance Benefits
- **3-5x Development Speed**: Through intelligent parallel task execution
- **85%+ Parallel Efficiency**: Optimized dependency analysis and scheduling
- **Reduced Context Switching**: Stateless tasks eliminate agent context management overhead
- **Quality Assurance**: Built-in TDD enforcement and quality gates prevent rework

Use this command to execute implementation plans created by /orca-start or custom plans following Orca's task specification format.
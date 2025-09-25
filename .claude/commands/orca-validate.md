---
argument-hint: [plan_path]
description: Validate implementation plan executability and provide recommendations
---

# /orca-validate

Validate that an implementation plan can be successfully executed and provide improvement recommendations using these parameters: $ARGUMENTS

Parse the arguments as:
1. plan_path (optional, default: "./plan.md"): Path to implementation plan file to validate

## Examples
```
/orca-validate
/orca-validate "./custom_plan.md"
/orca-validate "architecture_plan.md"
```

## Description
Comprehensive validation of implementation plans to ensure they can be successfully executed by Orca's parallel orchestration engine. Identifies issues, missing context, and provides actionable recommendations.

## Validation Checks
- **Task Completeness**: Validates all tasks have sufficient context for stateless execution
- **Dependency Analysis**: Detects circular dependencies and invalid relationships
- **Resource Requirements**: Checks if required tools and environments are specified
- **Quality Gate Compatibility**: Ensures tasks support TDD and quality validation
- **Execution Feasibility**: Analyzes if tasks can be realistically completed
- **Context Sufficiency**: Validates each task contains complete implementation context

## Sample Validation Output
```
✅ Plan Validation Results: REST API Implementation
================================================

📊 Summary:
- Total Tasks: 8
- Stateless Ready: 6 (75%)
- Missing Context: 2 tasks
- Dependency Issues: 0
- Overall Status: ⚠️ Needs Improvement

✅ Strengths:
- No circular dependencies detected
- Clear task breakdown with good granularity
- Quality gates properly specified
- Resource requirements well-defined

⚠️ Issues Found:

Task "implement-database-models":
- Missing: Database schema specifications
- Missing: Model relationship definitions
- Recommendation: Add detailed schema design to task context

Task "create-api-endpoints":
- Missing: Request/response schema definitions
- Missing: Authentication requirements per endpoint
- Recommendation: Include OpenAPI specification in task context

🚀 Recommendations:
1. Enrich task contexts with missing technical specifications
2. Consider breaking down complex tasks into smaller units
3. Add integration testing requirements to relevant tasks
4. Specify performance requirements for API endpoints

💡 Optimization Opportunities:
- Tasks 3-5 can be parallelized with minor adjustments
- Consider adding caching strategy task for better performance
- Authentication task could be split for better parallel execution

Estimated improvement with fixes: 85% → 95% execution readiness
```

## Validation Categories
- **🟢 Ready**: Task is fully prepared for stateless execution
- **🟡 Needs Enhancement**: Task has minor context gaps
- **🔴 Requires Attention**: Task has significant issues blocking execution
- **⚪ Dependencies**: Task relationships and execution order

## After Validation
Use recommendations to improve your plan before executing with:
- `/orca-execute` for full execution
- `/orca-preview` to see updated execution analysis

Use this command to ensure optimal execution success before committing to implementation.
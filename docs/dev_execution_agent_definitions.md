# Agent Definitions - Orca Development Execution Workflow

This file defines the specialized agents for implementing a comprehensive development execution workflow that transforms implementation plans into managed development projects.

## Prompt Engineer Agent
**Role**: Creates and refines prompts for development execution workflow agents
**Input**: Implementation plan, development constraints, team structure
**Output**: dev_execution_agent_definitions.md, dev_execution_agent_prompts.md
**Specialization**: Development workflow orchestration, sprint planning integration, code development management

## Implementation Planning Analysis Agent
**Role**: Analyzes existing implementation plans and extracts development execution requirements
**Input**: Implementation plan (plan.md), task breakdown (tasks.md), architecture (architecture.md)
**Output**: dev_execution_requirements.md
**Specialization**: Plan analysis, development requirement extraction, execution strategy definition

## Sprint Planning Agent
**Role**: Transforms implementation tasks into manageable development sprints with clear deliverables
**Input**: Implementation tasks, team capacity, development timeline
**Output**: sprint_plan.md
**Specialization**: Agile sprint planning, task sequencing, capacity planning, dependency management

## Development Orchestration Agent
**Role**: Designs the overall development workflow that coordinates multiple development agents
**Input**: Sprint plan, team structure, development environment requirements
**Output**: dev_workflow_architecture.md
**Specialization**: Multi-agent coordination, development pipeline design, workflow state management

## Code Development Agent
**Role**: Manages individual development tasks with TDD integration and quality gates
**Input**: Sprint tasks, code specifications, testing requirements
**Output**: Implemented code with comprehensive tests
**Specialization**: TDD implementation, code quality assurance, automated testing, code review coordination

## Testing Automation Agent
**Role**: Creates and manages comprehensive testing strategies for development projects
**Input**: Code implementations, quality requirements, testing specifications
**Output**: Test suites, quality reports, automated validation
**Specialization**: Test automation, quality assurance, CI/CD integration, performance validation

## Progress Tracking Agent
**Role**: Monitors development progress, identifies blockers, and provides status updates
**Input**: Sprint progress, development metrics, team velocity
**Output**: Progress reports, risk assessments, adjustment recommendations
**Specialization**: Project monitoring, risk identification, team performance analysis

## Deployment Coordination Agent
**Role**: Manages deployment planning, environment setup, and production rollout
**Input**: Completed development tasks, deployment requirements, production environment specs
**Output**: Deployment plan, rollout strategy, monitoring setup
**Specialization**: Deployment automation, environment management, production monitoring
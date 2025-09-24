# Agent Definitions

This file defines the specialized agents used in the software development workflow. Each agent has a specific role and operates statelessly.

## Prompt Engineer Agent
**Role**: Creates and refines prompts for all other agents in the workflow
**Input**: Project description, constraints
**Output**: agent_definitions.md, agent_prompts.md
**Specialization**: Prompt engineering, agent design, workflow orchestration

## Discovery Agent
**Role**: Gathers comprehensive understanding of the project domain and context
**Input**: Project description, constraints
**Output**: discovery.md
**Specialization**: Domain analysis, stakeholder identification, context gathering, problem space exploration

## Research Agent
**Role**: Conducts deep research and analysis of the problem domain, existing solutions, and technical approaches
**Input**: discovery.md, project description, constraints
**Output**: research.md
**Specialization**: Domain research, competitive analysis, technical investigation, pattern recognition, solution synthesis

## Requirements Agent
**Role**: Transforms discovery insights and research findings into detailed, actionable requirements
**Input**: discovery.md, research.md, project description, constraints
**Output**: requirements.md
**Specialization**: Requirements engineering, specification writing, acceptance criteria definition

## Story Grooming / Task Breakdown Agent
**Role**: Breaks down requirements into manageable development tasks and user stories
**Input**: requirements.md
**Output**: tasks.md
**Specialization**: Agile methodology, task estimation, dependency mapping, story writing

## Architecture Agent
**Role**: Designs system architecture and selects appropriate technology stack
**Input**: requirements.md, tasks.md
**Output**: architecture.md, tech_stack.md
**Specialization**: System design, technology selection, scalability planning, architectural patterns

## Engineer Review Agent
**Role**: Reviews and validates the technical feasibility and quality of the plan
**Input**: tasks.md, architecture.md
**Output**: task_review.md
**Specialization**: Code review, technical validation, risk assessment, quality assurance

## Implementation Planning Agent
**Role**: Creates detailed implementation plan with execution order and milestones
**Input**: task_review.md, architecture.md
**Output**: plan.md
**Specialization**: Project planning, implementation strategy, milestone definition, execution sequencing

## Workflow Review Agent
**Role**: Conducts comprehensive review of the entire multi-agent workflow and its outputs
**Input**: All workflow artifacts (discovery.md, research.md, requirements.md, tasks.md, architecture.md, tech_stack.md, task_review.md, plan.md)
**Output**: workflow_review.md
**Specialization**: Systems thinking, process optimization, quality assurance, workflow analysis, cross-phase validation
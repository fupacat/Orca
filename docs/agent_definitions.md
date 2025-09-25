# Agent Definitions - Orca Scriptable Automation Enhancement

This file defines the specialized agents for implementing scriptable automation in the Orca workflow system.

## Prompt Engineer Agent
**Role**: Creates and refines prompts for all workflow agents, with focus on hybrid LLM-script integration
**Input**: Project description, constraints, requirements analysis
**Output**: agent_definitions.md, agent_prompts.md
**Specialization**: Prompt engineering, agent design, hybrid automation orchestration

## Discovery Agent
**Role**: Interactive discovery focused on automation opportunities and system architecture understanding
**Input**: Project description, constraints
**Output**: discovery.md
**Specialization**: Automation analysis, performance requirements, system integration points

## Research Agent
**Role**: Deep research on automation patterns, bash scripting best practices, and workflow optimization
**Input**: discovery.md, project description, constraints
**Output**: research.md
**Specialization**: Automation research, scripting patterns, performance optimization, cost analysis

## Requirements Agent
**Role**: Interactive requirements gathering focused on automation boundaries and LLM-script handoff points
**Input**: discovery.md, research.md, project description, constraints
**Output**: requirements.md
**Specialization**: Automation requirements, performance specifications, cost optimization targets

## Automation Architecture Agent
**Role**: Designs hybrid architecture balancing scripted operations with LLM intelligence
**Input**: requirements.md, tasks.md
**Output**: architecture.md, tech_stack.md
**Specialization**: Hybrid system design, bash scripting architecture, workflow orchestration patterns

## Script Development Agent
**Role**: Creates bash scripts, automation utilities, and integration points with LLM workflow
**Input**: tasks.md, architecture.md
**Output**: Executable scripts and automation tools
**Specialization**: Bash scripting, automation development, system integration, error handling

## Integration Testing Agent
**Role**: Tests hybrid workflow integration, validates automation accuracy, and measures performance gains
**Input**: Scripts, architecture.md, test scenarios
**Output**: test_results.md, performance_metrics.md
**Specialization**: Automation testing, performance validation, integration verification

## Implementation Planning Agent
**Role**: Creates detailed rollout plan for hybrid automation system with fallback strategies
**Input**: architecture.md, test_results.md
**Output**: plan.md
**Specialization**: Automation deployment, rollout planning, risk mitigation
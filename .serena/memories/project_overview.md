# Orca Project Overview

## Purpose
Orca is a sophisticated multi-agent workflow orchestration system for software development. It implements a stateless, modular approach to managing complex software development projects through specialized AI agents that handle different phases of the development lifecycle.

## Core Architecture
The system is built around a **StartWorkflow** function that orchestrates multiple specialized agents in sequence:

1. **Prompt Engineer Agent** - Creates and refines prompts for all workflow agents
2. **Discovery Agent** - Gathers comprehensive project understanding and domain context
3. **Requirements Agent** - Transforms discoveries into detailed, actionable requirements
4. **Story Grooming Agent** - Breaks requirements into manageable tasks and user stories
5. **Architecture Agent** - Designs system architecture and selects technology stack
6. **Engineer Review Agent** - Validates technical feasibility and quality
7. **Implementation Planning Agent** - Creates detailed execution plans and roadmaps

## Key Design Principles
- **Stateless Agents**: Each agent operates independently with only necessary inputs
- **Artifact-Driven**: Agents produce specific markdown artifacts (discovery.md, requirements.md, tasks.md, etc.)
- **Clarification Loops**: Built-in pause mechanisms for ambiguity resolution
- **Template-Based**: Standardized agent definitions and prompts for consistency

## Tech Stack
- **Configuration-driven system** with no traditional build process
- **Markdown-based** artifacts and documentation
- **MCP (Model Context Protocol)** integration with two servers:
  - **Archon** (HTTP): `http://localhost:8051/mcp` - Task and project management
  - **Serena** (stdio): Git-based IDE assistant for project context
- **Claude Code** as the primary orchestration interface
- **Windows** development environment

## Repository Structure
This is NOT a git repository - it's a configuration and template system.
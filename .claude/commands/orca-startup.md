# /orca-startup

Comprehensive startup health check for Orca workflow system including project initialization verification.

## Usage
```
/orca-startup
```

## Description
Verifies that Archon and Serena MCP servers are available and properly configured, plus checks that the current project is initialized in both systems before running any workflows. **Automatically configures missing MCP servers and project files.**

## What it does
1. **Check and Configure MCP Servers**: Verifies connectivity and automatically adds missing servers
2. **Setup Project Configuration**: Copies `.claude.json` from templates if missing
3. **Test Basic Functionality**: Validates session management and file system access
4. **Verify Project Initialization**: Checks if current project exists in both Archon and Serena
5. **Report Comprehensive Status**: Detailed feedback with specific fix instructions

## Status Levels
- ✅ **READY**: All systems operational, project initialized in both Archon and Serena - workflows can proceed
- ⚠️ **PARTIAL**: MCP servers connected but project not fully initialized - provides initialization steps
- ❌ **BLOCKED**: Critical systems unavailable - provides fix instructions

## Troubleshooting
Provides specific guidance for:
- Archon server issues (port 8051 connectivity)
- Serena disconnection and reconnection
- Project initialization in both systems
- Configuration file problems

Use this before starting any Orca workflow to ensure all dependencies are met.
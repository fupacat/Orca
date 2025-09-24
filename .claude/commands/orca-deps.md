---
description: Quick MCP server validation for Orca system
---

# /orca-deps

Perform a quick dependency check for the Orca workflow orchestration system. Check that both Archon and Serena MCP servers are available and operational.

## What it does
1. **Test Archon MCP Server**: Verifies connection to http://localhost:8051/mcp
2. **Test Serena MCP Server**: Confirms file system access and project connectivity
3. **Report Results**: Provides clear status and fix instructions if needed

## Expected Output
- ✅ **All Systems Ready**: Both Archon and Serena are operational
- ⚠️ **Partial Availability**: Reports which system is unavailable
- ❌ **Systems Unavailable**: Provides quick fix commands

## Quick Fix Commands
- **Archon**: Start the Archon server or check http://localhost:8051/mcp
- **Serena**: Run `claude mcp list` and restart if needed

This check completes in under 10 seconds and gives immediate feedback on system readiness.
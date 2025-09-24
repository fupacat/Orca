# Eloqua MCP Project Overview

## Project Purpose
This project implements an MCP (Model Context Protocol) server for Oracle Eloqua Marketing Platform. It enables AI assistants and applications to interact seamlessly with Eloqua's marketing automation capabilities.

## Core Components
- **MCP Server Core**: Main protocol handler and routing
- **Eloqua API Client**: Wrapper for Oracle Eloqua REST API  
- **Authentication Module**: OAuth 2.0 and basic auth handling
- **Tool Definitions**: MCP tool implementations for each feature
- **Configuration Management**: Settings and credential management

## Key Features
1. Contact Management (CRUD operations, search, segmentation)
2. Campaign Operations (email campaigns, deployment, monitoring)
3. Analytics & Reporting (metrics, performance data)
4. Asset Management (templates, images, content)
5. Landing Pages & Forms

## Technical Stack
- Python 3.8+
- MCP Python SDK
- Oracle Eloqua REST API
- OAuth 2.0 authentication
- pytest for testing

## Project Structure
```
src/
├── server.py           # Main MCP server
├── eloqua/
│   ├── auth.py         # Authentication
│   ├── contacts.py     # Contact management
│   ├── campaigns.py    # Campaign operations
│   └── analytics.py    # Reporting tools
└── config/
```

## Development Constraints
- Solo developer capacity
- Free tooling requirements
- Oracle Eloqua API rate limits (1000 requests/hour)
- MCP protocol compliance requirements
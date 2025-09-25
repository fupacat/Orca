# System Architecture - Orca Scriptable Automation Enhancement

## Executive Summary

This document defines the hybrid system architecture for Orca's scriptable automation enhancement, designed to integrate deterministic script operations as Claude custom commands and tools while preserving Claude's role as the primary workflow orchestrator and maintaining existing MCP server integration.

**Architecture Goals**:
- Achieve 40-60% token cost reduction and 3-5x speed improvement
- Maintain Claude as the central workflow orchestrator
- Integrate scripts as Claude custom commands and tools
- Preserve existing MCP client architecture (Archon, Serena)
- Enable graceful fallback and error recovery

---

## High-Level System Architecture

### Core Components Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Claude Code Environment                      │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    Claude LLM Orchestrator                     │  │
│  │  ┌──────────────────┐    ┌──────────────────────────────────┐  │  │
│  │  │ Workflow Manager │    │     Context & State Manager     │  │  │
│  │  │ (Discovery,      │◄──►│   (Artifact Flow, Progress)     │  │  │
│  │  │  Requirements,   │    │                                  │  │  │
│  │  │  Architecture)   │    │                                  │  │  │
│  │  └──────────────────┘    └──────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                 Claude Custom Commands Layer                    │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │  │
│  │  │/orca-startup │ │/orca-template│ │    /orca-file-ops        │ │  │
│  │  │    -check    │ │  -process    │ │   /orca-config-validate  │ │  │
│  │  └──────────────┘ └──────────────┘ └──────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐                    ┌────────────────────────┐  │
│  │ Automation       │                    │    Traditional LLM     │  │
│  │ Script Engine    │                    │    Agent Operations    │  │
│  │  ┌─────────────┐ │                    │                        │  │
│  │  │Platform Mgr │ │                    │ ┌────────────────────┐ │  │
│  │  │Error Handler│ │                    │ │   Discovery Agent  │ │  │
│  │  │Template Eng │ │◄──── Claude ──────►│ │ Requirements Agent │ │  │
│  │  │File Ops Mgr │ │     Invokes        │ │ Architecture Agent │ │  │
│  │  │Config Proc  │ │                    │ │    (Complex Tasks) │ │  │
│  │  └─────────────┘ │                    │ └────────────────────┘ │  │
│  └──────────────────┘                    └────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                    MCP Client Integration                       │  │
│  │  ┌────────────────┐    ┌────────────────┐   ┌──────────────────┐ │  │
│  │  │ Archon MCP     │    │ Serena MCP     │   │ External Tools   │ │  │
│  │  │ (HTTP API)     │    │ (Stdio)        │   │ (jq, curl, git)  │ │  │
│  │  │ RAG/Tasks/Docs │    │ Code Analysis  │   │ System Utilities │ │  │
│  │  └────────────────┘    └────────────────┘   └──────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Claude-Centric Orchestration Design

### Claude as Workflow Orchestrator

Claude maintains full control over workflow execution and makes intelligent decisions about when to use automation:

```markdown
# Claude's Decision Making Process

## Deterministic Operations → Use Custom Commands
When Claude encounters operations that are:
- File system operations (directory creation, file checks)
- Template processing with known variables
- Configuration validation
- MCP server health checks
- Project structure setup

Claude will invoke: `/orca-[operation-type]` commands

## Complex/Creative Operations → Use LLM Processing
When Claude encounters operations requiring:
- Requirements analysis and interpretation
- Architecture decision-making
- User interaction and clarification
- Code review and quality assessment
- Novel problem solving

Claude will execute using standard LLM capabilities with MCP tools
```

### Claude Custom Commands Integration

Scripts are exposed to Claude as slash commands that Claude can invoke during workflow execution:

```bash
# Example Custom Commands Structure
.claude/
└── commands/
    ├── orca-startup-check.md      # System initialization automation
    ├── orca-template-process.md   # Template processing automation
    ├── orca-file-ops.md          # File system operations
    ├── orca-config-validate.md   # Configuration validation
    └── orca-platform-detect.md   # Platform detection utility
```

### Command Definition Pattern

Each custom command follows a standardized pattern for Claude integration:

```markdown
# /orca-startup-check Command Definition

**Description**: Automated MCP server validation and project initialization

**Usage**: `/orca-startup-check [project_path]`

**When to Use**:
- Beginning of any Orca workflow
- Before any MCP-dependent operations
- When troubleshooting connectivity issues

**Expected Output**:
- MCP server status validation
- Project directory structure verification
- Configuration file validation
- Performance metrics (time saved, tokens preserved)

**Fallback Strategy**:
If command fails, Claude should:
1. Analyze the error output
2. Attempt manual MCP validation using standard tools
3. Continue workflow with appropriate error handling
```

---

## Automation Script Engine Architecture

### Platform-Aware Script Execution

Scripts automatically detect and adapt to the execution environment:

```bash
#!/bin/bash
# orca-startup-check.sh - Cross-platform MCP validation

function main() {
    local project_path="${1:-.}"
    local start_time
    start_time="$(date +%s)"

    # Initialize platform detection
    detect_execution_environment

    # Validate MCP servers
    if ! validate_mcp_connectivity; then
        report_failure "MCP server validation failed"
        return 1
    fi

    # Setup project structure
    if ! ensure_project_structure "$project_path"; then
        report_failure "Project structure setup failed"
        return 1
    fi

    # Process configuration templates
    if ! process_initial_templates "$project_path"; then
        report_failure "Template processing failed"
        return 1
    fi

    # Report success with metrics
    local duration=$(($(date +%s) - start_time))
    report_success "$duration" "800-1500" # tokens saved estimate

    return 0
}

function detect_execution_environment() {
    # Auto-detect platform capabilities
    case "$(uname -s)" in
        Linux*)     export ORCA_PLATFORM="linux" ;;
        Darwin*)    export ORCA_PLATFORM="macos" ;;
        CYGWIN*|MINGW*|MSYS*) export ORCA_PLATFORM="windows" ;;
        *)          export ORCA_PLATFORM="unknown" ;;
    esac

    # Detect available shell environments
    if command -v wsl >/dev/null 2>&1 && [[ "$ORCA_PLATFORM" == "windows" ]]; then
        export WSL_AVAILABLE="true"
    fi

    # Report environment to Claude
    echo "ORCA_ENVIRONMENT_DETECTED: platform=$ORCA_PLATFORM wsl=$WSL_AVAILABLE"
}
```

### Error Handling and Claude Integration

Scripts provide structured output that Claude can interpret and act upon:

```bash
# Structured Output for Claude Integration

function report_success() {
    local duration="$1"
    local tokens_saved="$2"
    local operation="$3"

    # JSON output that Claude can parse
    jq -n \
        --arg status "success" \
        --arg duration "$duration" \
        --arg tokens_saved "$tokens_saved" \
        --arg operation "$operation" \
        --arg timestamp "$(date -Iseconds)" \
        '{
            status: $status,
            performance: {
                duration_seconds: ($duration | tonumber),
                tokens_saved_estimate: $tokens_saved,
                operation: $operation
            },
            timestamp: $timestamp,
            next_action: "continue_workflow"
        }'
}

function report_failure() {
    local error_message="$1"
    local error_code="${2:-1}"
    local suggested_fallback="$3"

    jq -n \
        --arg status "failure" \
        --arg error "$error_message" \
        --arg code "$error_code" \
        --arg fallback "$suggested_fallback" \
        '{
            status: $status,
            error: {
                message: $error,
                code: ($code | tonumber),
                suggested_fallback: $fallback
            },
            next_action: "manual_fallback_required"
        }'
}
```

---

## MCP Client Integration Architecture

### Archon MCP Integration Through Scripts

Scripts can perform Archon operations on behalf of Claude to reduce token usage:

```bash
# orca-archon-operations.sh - Automated Archon interactions

function create_project_in_archon() {
    local project_name="$1"
    local project_description="$2"

    local project_data
    project_data=$(jq -n \
        --arg title "$project_name" \
        --arg description "$project_description" \
        '{
            title: $title,
            description: $description,
            github_repo: null
        }')

    # Direct HTTP call to Archon
    local response
    if response=$(curl -sf \
        -H "Content-Type: application/json" \
        -d "$project_data" \
        "http://localhost:8051/projects"); then

        # Extract project ID for Claude
        local project_id
        project_id="$(echo "$response" | jq -r '.project.id')"

        echo "ARCHON_PROJECT_CREATED: id=$project_id name=$project_name"
        return 0
    else
        echo "ARCHON_PROJECT_FAILED: Unable to create project in Archon"
        return 1
    fi
}

function update_project_progress() {
    local project_id="$1"
    local phase="$2"
    local status="$3"

    # Update project status in Archon
    curl -sf -X PUT \
        -H "Content-Type: application/json" \
        -d "{\"phase\": \"$phase\", \"status\": \"$status\"}" \
        "http://localhost:8051/projects/$project_id/progress"
}
```

### Serena MCP Integration Preservation

Complex code operations remain with Serena through Claude's existing MCP integration:

```markdown
# Integration Strategy

## Automated via Scripts (Token Saving):
- Project structure creation
- Template file processing
- Configuration validation
- File existence checks
- Basic file operations

## Preserved with Serena MCP (LLM Control):
- Code analysis and symbol navigation
- Complex file modifications
- Semantic code operations
- Memory management
- Intelligent code refactoring

This division ensures Claude retains control over complex operations while
automating simple, deterministic tasks.
```

---

## Template Processing Architecture

### Advanced Template Engine

Template processing is automated but remains flexible for complex scenarios:

```bash
# orca-template-processor.sh - Intelligent template processing

function process_templates_for_claude() {
    local template_directory="$1"
    local project_context="$2" # JSON context from Claude
    local output_directory="$3"

    # Parse project context from Claude
    local project_name
    project_name="$(echo "$project_context" | jq -r '.project_name')"

    local project_type
    project_type="$(echo "$project_context" | jq -r '.project_type')"

    # Generate template variables
    local template_vars
    template_vars=$(generate_template_variables "$project_name" "$project_type" "$project_context")

    # Process all templates
    local processed_count=0
    local failed_count=0

    find "$template_directory" -name "*.template" -type f | while IFS= read -r template_file; do
        local output_file="${template_file%.template}"
        output_file="${output_file/$template_directory/$output_directory}"

        # Create output directory
        mkdir -p "$(dirname "$output_file")"

        # Process template with context-aware substitution
        if process_single_template "$template_file" "$template_vars" "$output_file"; then
            ((processed_count++))
            echo "TEMPLATE_PROCESSED: $template_file -> $output_file"
        else
            ((failed_count++))
            echo "TEMPLATE_FAILED: $template_file"
        fi
    done

    # Report results to Claude
    echo "TEMPLATE_SUMMARY: processed=$processed_count failed=$failed_count"

    if [[ $failed_count -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}
```

### Context-Aware Variable Substitution

Templates can access rich context information provided by Claude:

```bash
function generate_template_variables() {
    local project_name="$1"
    local project_type="$2"
    local claude_context="$3"

    # Extract relevant information from Claude's context
    local author_name
    author_name="$(git config user.name 2>/dev/null || echo 'Unknown Author')"

    local current_date
    current_date="$(date +%Y-%m-%d)"

    # Generate comprehensive variable set
    jq -n \
        --arg project_name "$project_name" \
        --arg project_type "$project_type" \
        --arg author_name "$author_name" \
        --arg current_date "$current_date" \
        --argjson context "$claude_context" \
        '{
            PROJECT_NAME: $project_name,
            PROJECT_TYPE: $project_type,
            AUTHOR_NAME: $author_name,
            CURRENT_DATE: $current_date,
            ORCA_VERSION: "2.0",
            PLATFORM: env.ORCA_PLATFORM,
            # Include any additional context from Claude
            CLAUDE_CONTEXT: $context
        }' > /tmp/template_vars.json

    export TEMPLATE_VARIABLES="/tmp/template_vars.json"
}
```

---

## Configuration Management Architecture

### Claude-Driven Configuration Processing

Configuration operations are automated but driven by Claude's requirements:

```bash
# orca-config-manager.sh - Configuration processing for Claude workflows

function validate_project_configuration() {
    local config_file="$1"
    local validation_rules="$2" # JSON rules from Claude

    # Validate configuration structure
    if ! jq empty "$config_file" 2>/dev/null; then
        echo "CONFIG_INVALID: Malformed JSON in $config_file"
        return 1
    fi

    # Apply Claude-provided validation rules
    local validation_result
    validation_result=$(validate_against_rules "$config_file" "$validation_rules")

    if [[ "$validation_result" == "valid" ]]; then
        echo "CONFIG_VALID: $config_file passes all validation rules"
        return 0
    else
        echo "CONFIG_VALIDATION_FAILED: $validation_result"
        return 1
    fi
}

function merge_environment_configs() {
    local base_config="$1"
    local environment="$2"
    local output_file="$3"

    # Environment-specific configuration merging
    local env_config="${base_config%.*}.${environment}.json"

    if [[ -f "$env_config" ]]; then
        # Merge configurations with environment taking precedence
        jq -s '.[0] * .[1]' "$base_config" "$env_config" > "$output_file"
        echo "CONFIG_MERGED: $base_config + $env_config -> $output_file"
    else
        # Copy base configuration
        cp "$base_config" "$output_file"
        echo "CONFIG_COPIED: $base_config -> $output_file (no env override)"
    fi
}
```

---

## Test-Driven Development Integration

### TDD-Friendly Architecture

All automation scripts are designed with TDD principles and can be tested independently:

```bash
# Testing Infrastructure for Claude Integration

function setup_automation_testing() {
    local test_directory="tests/automation"

    # Create test structure
    mkdir -p "$test_directory"/{unit,integration,performance}

    # Install Bats testing framework
    if ! command -v bats >/dev/null 2>&1; then
        install_bats_framework
    fi

    # Setup mock services for isolated testing
    setup_mock_mcp_servers
    setup_test_fixtures

    echo "TESTING_SETUP_COMPLETE: framework=bats directory=$test_directory"
}

# Example test for Claude integration
function test_claude_command_integration() {
    # Test script behavior when invoked by Claude
    local mock_claude_context='{"project_name": "test-project", "phase": "startup"}'

    # Execute startup check with mock context
    run_startup_check_with_context "$mock_claude_context"

    # Verify expected outputs for Claude
    assert_output_contains "ORCA_ENVIRONMENT_DETECTED"
    assert_output_contains "MCP_VALIDATION_SUCCESS"
    assert_output_contains "PROJECT_STRUCTURE_READY"
}
```

### Continuous Testing Integration

Testing integrates seamlessly with Claude's workflow execution:

```bash
function run_automation_tests() {
    local test_type="${1:-all}" # unit, integration, performance, all

    echo "TESTING_STARTED: type=$test_type timestamp=$(date -Iseconds)"

    case "$test_type" in
        "unit")
            bats tests/automation/unit/*.bats
            ;;
        "integration")
            # Start mock services
            start_test_services
            bats tests/automation/integration/*.bats
            stop_test_services
            ;;
        "performance")
            run_performance_benchmarks
            ;;
        "all")
            run_automation_tests "unit"
            run_automation_tests "integration"
            run_automation_tests "performance"
            ;;
    esac

    echo "TESTING_COMPLETED: type=$test_type"
}
```

---

## Performance Optimization and Monitoring

### Performance Tracking Integration

All automation scripts provide performance metrics back to Claude:

```bash
# Performance monitoring integrated with Claude workflows

function track_automation_performance() {
    local operation="$1"
    local start_time="$2"
    local tokens_saved="$3"
    local success="$4"

    local end_time
    end_time="$(date +%s)"
    local duration=$((end_time - start_time))

    # Create performance entry
    local performance_data
    performance_data=$(jq -n \
        --arg operation "$operation" \
        --arg duration "$duration" \
        --arg tokens_saved "$tokens_saved" \
        --arg success "$success" \
        --arg timestamp "$(date -Iseconds)" \
        '{
            operation: $operation,
            duration_seconds: ($duration | tonumber),
            tokens_saved: ($tokens_saved | tonumber),
            success: ($success == "true"),
            timestamp: $timestamp
        }')

    # Append to performance log
    echo "$performance_data" >> "$HOME/.orca/performance.jsonl"

    # Report to Claude
    echo "PERFORMANCE_RECORDED: operation=$operation duration=${duration}s tokens_saved=$tokens_saved"
}
```

### Cost Optimization Reporting

Scripts provide cost impact analysis to Claude:

```bash
function generate_cost_report() {
    local timeframe="${1:-24h}" # 24h, 7d, 30d

    # Calculate savings over timeframe
    local total_tokens_saved
    total_tokens_saved=$(jq -r --arg timeframe "$timeframe" '
        select(.timestamp > (now - ($timeframe | if . == "24h" then 86400 elif . == "7d" then 604800 else 2592000 end))) |
        .tokens_saved
    ' "$HOME/.orca/performance.jsonl" | jq -s 'add // 0')

    local operations_count
    operations_count=$(jq -r --arg timeframe "$timeframe" '
        select(.timestamp > (now - ($timeframe | if . == "24h" then 86400 elif . == "7d" then 604800 else 2592000 end)))
    ' "$HOME/.orca/performance.jsonl" | wc -l)

    # Cost calculation (approximate)
    local cost_per_token="0.00001" # Example rate
    local cost_saved
    cost_saved=$(echo "$total_tokens_saved * $cost_per_token" | bc -l)

    # Report to Claude
    jq -n \
        --arg timeframe "$timeframe" \
        --arg operations "$operations_count" \
        --arg tokens_saved "$total_tokens_saved" \
        --arg cost_saved "$cost_saved" \
        '{
            timeframe: $timeframe,
            operations_automated: ($operations | tonumber),
            tokens_saved: ($tokens_saved | tonumber),
            estimated_cost_saved: ($cost_saved | tonumber),
            generated_at: now
        }'
}
```

---

## Security and Error Handling

### Secure Script Execution

All automation scripts include comprehensive security measures:

```bash
# Security framework for Claude-invoked scripts

function validate_claude_context() {
    local context="$1"

    # Validate JSON structure
    if ! echo "$context" | jq empty 2>/dev/null; then
        echo "SECURITY_ERROR: Invalid JSON context from Claude"
        return 1
    fi

    # Sanitize project names and paths
    local project_name
    project_name="$(echo "$context" | jq -r '.project_name')"

    if [[ ! "$project_name" =~ ^[a-zA-Z0-9._-]+$ ]]; then
        echo "SECURITY_ERROR: Invalid project name format: $project_name"
        return 1
    fi

    # Additional security validations...
    echo "SECURITY_VALIDATED: Context passed security checks"
    return 0
}

function sanitize_file_paths() {
    local path="$1"

    # Remove dangerous path components
    local clean_path
    clean_path="$(echo "$path" | sed 's/\.\.//g' | sed 's/;//g')"

    # Validate against allowed characters
    if [[ ! "$clean_path" =~ ^[a-zA-Z0-9._/-]+$ ]]; then
        echo "SECURITY_ERROR: Invalid characters in path: $path"
        return 1
    fi

    echo "$clean_path"
}
```

### Graceful Error Recovery

Scripts provide clear error information that Claude can act upon:

```bash
function handle_automation_error() {
    local operation="$1"
    local error_code="$2"
    local error_message="$3"

    # Log error for debugging
    log_error "$operation failed with code $error_code: $error_message"

    # Provide Claude with structured error information
    jq -n \
        --arg operation "$operation" \
        --arg error_code "$error_code" \
        --arg error_message "$error_message" \
        --arg timestamp "$(date -Iseconds)" \
        '{
            status: "automation_failed",
            operation: $operation,
            error: {
                code: ($error_code | tonumber),
                message: $error_message,
                timestamp: $timestamp
            },
            recommended_action: "fallback_to_manual_processing",
            manual_steps: [
                "Claude should attempt the operation using standard MCP tools",
                "If that fails, prompt user for manual intervention",
                "Continue workflow with degraded automation"
            ]
        }'
}
```

---

## Deployment and Version Management

### Claude-Aware Update System

Version management integrates with Claude's workflow execution:

```bash
# orca-version-manager.sh - Version control for automation scripts

function update_automation_system() {
    local target_version="${1:-latest}"
    local backup_current="${2:-true}"

    echo "UPDATE_STARTED: target=$target_version backup=$backup_current"

    # Backup current version if requested
    if [[ "$backup_current" == "true" ]]; then
        backup_current_automation
    fi

    # Download and install updates
    if install_automation_version "$target_version"; then
        # Validate new installation
        if validate_automation_installation; then
            echo "UPDATE_SUCCESS: version=$target_version"
            restart_claude_environment
            return 0
        else
            echo "UPDATE_FAILED: Installation validation failed"
            rollback_automation_installation
            return 1
        fi
    else
        echo "UPDATE_FAILED: Download/installation failed"
        return 1
    fi
}

function restart_claude_environment() {
    # Reload Claude custom commands
    echo "CLAUDE_RELOAD_REQUIRED: New automation commands available"
    echo "Please restart Claude Code or run: source ~/.bashrc"
}
```

---

## Integration with Existing Orca Workflow

### Workflow Phase Integration

Automation integrates seamlessly with existing Orca phases:

```markdown
# Enhanced Orca Workflow with Automation

## Phase 0: Startup (AUTOMATED)
**Claude Action**: `/orca-startup-check <project_path>`
- Validates MCP servers automatically
- Sets up project structure
- Processes initial templates
- **Time Savings**: 60s → 12-20s
- **Token Savings**: 800-1500 tokens

## Phase 1: Prompt Engineering (LLM)
**Claude Action**: Standard LLM processing with MCP tools
- Complex prompt optimization
- Agent creation and refinement
- Requires Claude's creative intelligence

## Phase 2: Discovery (HYBRID)
**Claude Action**: LLM processing + `/orca-template-process` for artifacts
- Claude conducts interactive discovery
- Scripts handle artifact generation and organization
- **Token Savings**: 200-300 tokens for file operations

## Phase 3: Requirements (HYBRID)
**Claude Action**: LLM analysis + `/orca-config-validate` for specs
- Claude performs requirements analysis
- Scripts validate and format requirement documents
- **Token Savings**: 150-250 tokens for validation

## Phases 4-8: Architecture through Planning (LLM)
**Claude Action**: Standard LLM processing
- Complex reasoning and decision-making
- Requires Claude's analytical capabilities
- Automation limited to file organization and template processing
```

### Custom Command Reference

```markdown
# Available Orca Automation Commands

## System Operations
- `/orca-startup-check [path]` - Validate MCP servers and initialize project
- `/orca-platform-detect` - Detect execution environment capabilities
- `/orca-health-monitor` - Check system health and performance

## File Operations
- `/orca-file-ops create-structure <path>` - Create project directory structure
- `/orca-file-ops validate-exists <files...>` - Validate file existence
- `/orca-file-ops backup-artifacts <source> <dest>` - Backup workflow artifacts

## Template Processing
- `/orca-template-process <template_dir> <context> <output_dir>` - Process templates
- `/orca-template-validate <template_file>` - Validate template syntax

## Configuration Management
- `/orca-config-validate <config_file> [rules]` - Validate configuration files
- `/orca-config-merge <base> <environment> <output>` - Merge configurations

## Performance and Monitoring
- `/orca-performance-report [timeframe]` - Generate performance analysis
- `/orca-cost-analysis [period]` - Calculate token savings and cost impact
```

---

## Data Flow and Context Management

### Claude-Centric Data Flow

```
User Request
     │
     ▼
┌─────────────────┐
│     Claude      │ ◄─── User Input & Context
│   Orchestrator  │
└─────────────────┘
     │
     ▼ (Decision: Deterministic?)
┌─────────────────┐    ┌─────────────────────┐
│      Yes        │    │        No           │
│ Custom Command  │    │   Standard LLM      │
│ /orca-[action]  │    │   Processing        │
└─────────────────┘    └─────────────────────┘
     │                          │
     ▼                          │
┌─────────────────┐              │
│ Script Engine   │              │
│ (Fast, Cached)  │              │
└─────────────────┘              │
     │ (Success)                 │
     ▼                          │
┌─────────────────┐              │
│ Structured      │              │
│ Results to      │ ◄────────────┘
│ Claude          │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Claude Updates  │
│ Context & State │
└─────────────────┘
     │
     ▼
Continue Workflow / Complete
```

### Context Preservation Pattern

```json
{
  "claude_context_structure": {
    "workflow_phase": "string",
    "project_metadata": {
      "name": "string",
      "type": "string",
      "path": "string"
    },
    "automation_history": [
      {
        "command": "/orca-startup-check",
        "timestamp": "iso8601",
        "duration": "number",
        "tokens_saved": "number",
        "success": "boolean"
      }
    ],
    "artifacts_generated": {
      "files": ["array"],
      "configurations": "object"
    },
    "performance_metrics": {
      "total_tokens_saved": "number",
      "automation_success_rate": "number",
      "time_saved_seconds": "number"
    }
  }
}
```

---

**Architecture Document Completed**: 2024-01-23
**Architecture Agent**: Claude-centric hybrid system design
**Key Features**: Custom commands integration, MCP client preservation, LLM orchestration, performance optimization
**Next Phase**: Engineering review and implementation planning
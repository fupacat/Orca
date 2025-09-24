---
argument-hint: [project_name] [project_path] [description] [constraints] [auto_start] [github_setup]
description: Create new Orca project with complete setup
---

# /orca-new

You are creating a complete new project with the Orca workflow system using these parameters: $ARGUMENTS

Parse the arguments as:
1. project_name (required)
2. project_path (required)
3. project_description (required)
4. constraints (optional, default: "Solo developer, free tools")
5. auto_start (optional, default: false)
6. github_setup (optional, default: true)

## Step 1: Create Project Structure
Create the project directory structure and navigate to it:
```bash
# Validate and expand paths properly
PROJECT_PATH="{project_path}"
PROJECT_NAME="{project_name}"

# Convert to absolute path and handle ~ expansion
if [[ "$PROJECT_PATH" == "~"* ]]; then
    PROJECT_PATH="${PROJECT_PATH/#\~/$HOME}"
fi

# Create full project path
FULL_PROJECT_PATH="$PROJECT_PATH/$PROJECT_NAME"

echo "Creating project at: $FULL_PROJECT_PATH"

# Create directory structure
mkdir -p "$FULL_PROJECT_PATH/.claude/commands" "$FULL_PROJECT_PATH/.serena" "$FULL_PROJECT_PATH/templates" "$FULL_PROJECT_PATH/docs"

# Navigate to project directory
cd "$FULL_PROJECT_PATH" || { echo "Failed to navigate to project directory"; exit 1; }
echo "Current directory: $(pwd)"
```

## Step 2: Copy Orca Core Files
Copy these files from the current Orca directory to the new project:
```bash
# Determine Orca source directory dynamically
ORCA_DIR="$ORCA_DIR"
if [ -z "$ORCA_DIR" ]; then
    # Try to find Orca directory based on common patterns
    if [ -d "/c/Users/eolun/projects/Orca" ]; then
        ORCA_DIR="/c/Users/eolun/projects/Orca"
    elif [ -d "$(dirname "$(pwd)")/Orca" ]; then
        ORCA_DIR="$(dirname "$(pwd)")/Orca"
    else
        echo "Error: Cannot locate Orca source directory"
        echo "Please set ORCA_DIR environment variable or run from Orca parent directory"
        exit 1
    fi
fi

echo "Using Orca source directory: $ORCA_DIR"

# Verify source files exist
if [ ! -f "$ORCA_DIR/start.md" ]; then
    echo "Error: Orca source files not found at $ORCA_DIR"
    exit 1
fi

# Copy Orca core workflow files with error checking
echo "Copying core workflow files..."
cp "$ORCA_DIR/start.md" . || echo "Warning: Failed to copy start.md"
cp "$ORCA_DIR/startup_check.md" . || echo "Warning: Failed to copy startup_check.md"
cp "$ORCA_DIR/check_dependencies.md" . || echo "Warning: Failed to copy check_dependencies.md"
cp "$ORCA_DIR/bootstrap_project.md" . || echo "Warning: Failed to copy bootstrap_project.md"
cp "$ORCA_DIR/archon_rules.md" . || echo "Warning: Failed to copy archon_rules.md"

# Copy template files
echo "Copying template files..."
if [ -d "$ORCA_DIR/templates" ]; then
    cp -r "$ORCA_DIR/templates/"* templates/ || echo "Warning: Failed to copy some template files"

    # Copy settings.local.json to .claude/ directory for Claude Code configuration
    if [ -f "templates/settings.local.json" ]; then
        cp templates/settings.local.json .claude/settings.local.json || echo "Warning: Failed to copy settings.local.json to .claude/ directory"
        echo "✅ settings.local.json configured for project"
    else
        echo "⚠️  Warning: settings.local.json not found in templates"
    fi

    # Copy .mcp.json to project root for automatic MCP server configuration
    if [ -f "templates/.mcp.json" ]; then
        cp templates/.mcp.json .mcp.json || echo "Warning: Failed to copy .mcp.json to project root"
        echo "✅ .mcp.json configured for automatic MCP setup"
    else
        echo "⚠️  Warning: .mcp.json not found in templates"
    fi
else
    echo "Warning: Templates directory not found at $ORCA_DIR/templates"
fi

# Copy Claude commands
echo "Copying Claude commands..."
if [ -d "$ORCA_DIR/.claude/commands" ]; then
    cp -r "$ORCA_DIR/.claude/commands/"* .claude/commands/ || echo "Warning: Failed to copy some commands"
else
    echo "Warning: Commands directory not found at $ORCA_DIR/.claude/commands"
fi

echo "File copying completed."
```

## Step 3: Generate Project-Specific CLAUDE.md
Generate CLAUDE.md from template with project-specific values:
```bash
# Generate CLAUDE.md from template
if [ -f "templates/CLAUDE_template.md" ]; then
    echo "Generating project-specific CLAUDE.md..."

    # Process template variables
    sed "s/{project_name}/${PROJECT_NAME}/g; s/{project_description}/${3:-Project created with Orca}/g; s/{constraints}/${4:-Solo developer, free tools}/g" \
        templates/CLAUDE_template.md > CLAUDE.md

    echo "✅ CLAUDE.md generated successfully"
else
    echo "⚠️  Warning: CLAUDE_template.md not found, CLAUDE.md not generated"
fi
```

## Step 4: Copy Template Files (Do NOT Process)
Copy remaining template files as-is for the project's Claude instance to process:
```bash
# Copy templates without processing - let the project's workflow handle generation
# The templates will be processed when /orca-start or /orca-workflow is run in the new project
echo "Template files copied. Run /orca-start in the new project to generate project-specific files."
```

## Step 5: Verify Setup and Display Results
```bash
# Verify critical files were copied
echo "🔍 Verifying project setup..."

MISSING_FILES=()
[ ! -f "start.md" ] && MISSING_FILES+=("start.md")
[ ! -f "archon_rules.md" ] && MISSING_FILES+=("archon_rules.md")
[ ! -f "CLAUDE.md" ] && MISSING_FILES+=("CLAUDE.md")
[ ! -f ".claude/settings.local.json" ] && MISSING_FILES+=(".claude/settings.local.json")
[ ! -f ".mcp.json" ] && MISSING_FILES+=(".mcp.json")
[ ! -d "templates" ] && MISSING_FILES+=("templates/")
[ ! -d ".claude/commands" ] && MISSING_FILES+=(".claude/commands/")

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ Setup incomplete. Missing files/directories:"
    printf '%s\n' "${MISSING_FILES[@]}"
    echo "Please check the copy operations above for errors."
    exit 1
fi

# Count copied files
CORE_FILES=$(ls *.md 2>/dev/null | wc -l)
TEMPLATE_FILES=$(ls templates/*.md 2>/dev/null | wc -l)
COMMAND_FILES=$(ls .claude/commands/*.md 2>/dev/null | wc -l)

echo "✅ Project structure created at: $FULL_PROJECT_PATH"
echo "🔧 Copied $CORE_FILES core workflow files"
echo "📋 Copied $TEMPLATE_FILES template files"
echo "⚡ Copied $COMMAND_FILES Claude commands"
echo ""
echo "🚀 Next Steps:"
echo "1. cd $FULL_PROJECT_PATH"
echo "2. claude code"
echo "3. Run /orca-startup to configure MCP servers"
echo "4. Run /orca-start \"{project_description}\" to begin workflow"
echo ""
echo "📁 Project is ready for Orca workflow execution!"
```

## Notes for Project Initialization
- **MCP Server Setup**: Will be done by the project's Claude instance via /orca-startup
- **Archon Project Creation**: Will be handled during /orca-start workflow execution
- **Serena Onboarding**: Will be performed when the project's Claude instance starts
- **File Generation**: Templates will be processed during workflow execution
- **Git Initialization**: Can be done during workflow or manually as needed

## What it does
1. **Create Project Structure**: Sets up directories (.claude/commands, .serena, templates, docs)
2. **Copy Orca Core Files**: Copies all workflow files (start.md, archon_rules.md, etc.)
3. **Copy Templates**: Copies all template files for later processing
4. **Copy Claude Commands**: Copies all /orca-* commands to the new project
5. **Provide Setup Instructions**: Shows next steps for project initialization

## Created Files
- Core Orca workflow files (start.md, archon_rules.md, etc.)
- Template files (CLAUDE_template.md, README_template.md, etc.) - **NOT processed**
- Claude commands (.claude/commands/orca-*.md)
- Directory structure ready for MCP servers

## What it does NOT do (left for project's Claude instance)
- ❌ **MCP Server Configuration**: Done via /orca-startup in the new project
- ❌ **File Generation from Templates**: Done during /orca-start workflow
- ❌ **Archon Project Creation**: Done during workflow execution
- ❌ **Serena Onboarding**: Done when project's Claude starts
- ❌ **Git Initialization**: Done during workflow or manually

## Prerequisites
- Write permissions to the specified project path
- Orca source files available in current directory

## Usage
```
/orca-new MyProject ~/Projects "A REST API for task management"
```

The project will be created with all Orca files and templates, ready for the project's Claude instance to run the complete workflow via `/orca-start`.
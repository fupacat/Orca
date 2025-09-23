# /orca-github

Set up GitHub integration for the current Orca project including repository creation, authentication, and CI/CD workflows.

## Usage
```
/orca-github <action> [repository_name] [visibility] [description]
```

## Actions
- **setup** - Complete GitHub setup for current project
- **create** - Create new GitHub repository
- **connect** - Connect existing project to existing GitHub repo
- **workflows** - Add GitHub Actions workflows for CI/CD

## Parameters
- **action** (required): setup | create | connect | workflows
- **repository_name** (optional): GitHub repository name (defaults to project directory name)
- **visibility** (optional): public | private (default: private)
- **description** (optional): Repository description (uses project description if available)

## Examples
```
/orca-github setup
/orca-github create "my-awesome-project" public "REST API for task management"
/orca-github connect "existing-repo"
/orca-github workflows
```

## Description
Comprehensive GitHub integration for Orca projects including repository setup, authentication verification, and automated workflow configuration.

## Setup Action (Recommended)
The `setup` action performs complete GitHub integration:
1. **Verify GitHub CLI**: Ensures `gh` is installed and authenticated
2. **Initialize Git**: Creates git repository if not already present
3. **Create GitHub Repository**: Creates remote repository with appropriate settings
4. **Configure Remote**: Sets up origin remote and establishes connection
5. **Initial Commit**: Commits all project files with proper commit message
6. **Push to GitHub**: Uploads project to remote repository
7. **Add GitHub Workflows**: Creates CI/CD workflows based on project tech stack
8. **Update Archon**: Records GitHub repository URL in Archon project

## What it does

### GitHub CLI Verification
- Checks if GitHub CLI (`gh`) is installed
- Verifies authentication status with `gh auth status`
- Provides setup instructions if not authenticated

### Repository Creation
- Creates GitHub repository with specified visibility
- Sets appropriate description and topics
- Configures repository settings (issues, wiki, etc.)
- Handles naming conflicts gracefully

### Git Configuration
- Initializes git repository if needed
- Sets up proper .gitignore based on project type
- Configures git user settings if not already set
- Creates initial commit with all project files

### GitHub Actions Workflows
- Adds appropriate CI/CD workflows based on detected tech stack
- Includes testing, building, and deployment pipelines
- Configures dependency management and security scanning
- Supports multiple platforms and environments

### Project Integration
- Updates Archon project with GitHub repository URL
- Adds GitHub information to project documentation
- Updates CLAUDE.md with repository-specific guidance
- Creates proper README.md with project information

## Prerequisites
- GitHub CLI (`gh`) installed and authenticated
- Git configured with user name and email
- Current directory is an Orca project
- Internet connectivity for GitHub operations

## Generated Files
- `.github/workflows/` - CI/CD workflow files
- `.gitignore` - Appropriate ignore patterns for project type
- `README.md` - Enhanced with GitHub repository information
- Updated project documentation with repository links

## Troubleshooting
- **GitHub CLI not found**: Install from https://cli.github.com/
- **Not authenticated**: Run `gh auth login` and follow prompts
- **Repository exists**: Command will connect to existing repo if owned
- **Network issues**: Verify internet connection and GitHub status

## Security Features
- Private repositories by default
- Dependency vulnerability scanning
- Secret scanning enabled
- Branch protection rules for main branch

Use this command to seamlessly integrate any Orca project with GitHub for version control, collaboration, and automated workflows.
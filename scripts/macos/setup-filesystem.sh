#!/bin/bash

# Filesystem Setup for Claude Desktop
# Creates and initializes the directory structure for Claude access

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$HOME/claude-desktop-setup.log"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
    log "SUCCESS: $1"
}

error() {
    echo -e "${RED}✗ $1${NC}"
    log "ERROR: $1"
}

info() {
    echo -e "${BLUE}ℹ $1${NC}"
    log "INFO: $1"
}

warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
    log "WARNING: $1"
}

# Create directory structure
create_directory_structure() {
    local base_path="$1"
    
    info "Creating directory structure at: $base_path"
    
    # Create main directories
    local directories=("projects" "documents" "scripts" "logs")
    
    for dir in "${directories[@]}"; do
        local full_path="$base_path/$dir"
        if [ ! -d "$full_path" ]; then
            mkdir -p "$full_path"
            success "Created directory: $dir/"
        else
            info "Directory already exists: $dir/"
        fi
    done
}

# Initialize Git repositories
initialize_git_repos() {
    local base_path="$1"
    
    info "Initializing Git repositories..."
    
    # Initialize projects repository
    local projects_path="$base_path/projects"
    if [ ! -d "$projects_path/.git" ]; then
        (cd "$projects_path" && git init)
        
        # Create initial .gitignore
        cat > "$projects_path/.gitignore" << EOF
# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
EOF
        
        # Initial commit
        (cd "$projects_path" && git add .gitignore && git commit -m "Initial commit: Add .gitignore")
        success "Initialized Git repository in projects/"
    else
        info "Git repository already exists in projects/"
    fi
    
    # Initialize scripts repository
    local scripts_path="$base_path/scripts"
    if [ ! -d "$scripts_path/.git" ]; then
        (cd "$scripts_path" && git init)
        
        # Create initial .gitignore
        cat > "$scripts_path/.gitignore" << EOF
# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Temporary files
*.tmp
*.temp
EOF
        
        # Create initial README
        cat > "$scripts_path/README.md" << EOF
# Scripts Directory

This directory contains scripts and automation tools for your Claude Desktop environment.

## Structure

- **automation/**: Automated workflows and scheduled tasks
- **utilities/**: Helper scripts and tools
- **templates/**: Script templates and boilerplate code

## Getting Started

This directory is monitored by Claude's Git MCP server. You can ask Claude to:
- Create new scripts
- Commit changes to version control
- Review script history
- Manage automation workflows

EOF
        
        # Create subdirectories
        mkdir -p "$scripts_path"/{automation,utilities,templates}
        
        # Initial commit
        (cd "$scripts_path" && git add . && git commit -m "Initial commit: Setup scripts directory structure")
        success "Initialized Git repository in scripts/"
    else
        info "Git repository already exists in scripts/"
    fi
}

# Create README files
create_readme_files() {
    local base_path="$1"
    
    info "Creating documentation files..."
    
    # Main README
    cat > "$base_path/README.md" << EOF
# Claude Desktop Workspace

This directory structure was created by the Claude Desktop Setup installer to provide Claude with organized filesystem access for productive collaboration.

## Directory Structure

### 📁 projects/
Git-initialized directory for your development projects and code repositories.
- Includes basic .gitignore for common file types
- Ready for project organization and version control
- Ask Claude to help manage your projects here

### 📁 documents/
General document storage and organization.
- Meeting notes and documentation
- Research and reference materials
- Reports and presentations
- Ask Claude to help organize and search your documents

### 📁 scripts/
Git-initialized directory for automation scripts and utilities.
- **automation/**: Scheduled tasks and workflows
- **utilities/**: Helper scripts and tools
- **templates/**: Script templates and boilerplate code
- Ask Claude to create and manage automation scripts

### 📁 logs/
System and application logs for troubleshooting.
- Installation logs
- Application debug information
- Error tracking and diagnostics

## MCP Server Integration

Claude has filesystem access to this directory tree through the filesystem MCP server. This enables Claude to:

- Read, write, and organize files
- Create project structures
- Manage documentation
- Execute version control operations
- Monitor logs and troubleshoot issues

## Getting Started

Try these commands with Claude:

\`\`\`
"What files do I have in my projects directory?"
"Create a new project folder for [your project name]"
"Help me organize my documents by type"
"Show me my recent git commits in the scripts directory"
"Create a simple automation script for [task]"
\`\`\`

## Security Notes

- This workspace is scoped specifically for Claude access
- All file operations are logged
- Git repositories track changes for accountability
- Regular backups of important work are recommended

---

*Created by Claude Desktop Setup v1.0*
*Installation Date: $(date '+%Y-%m-%d %H:%M:%S')*
EOF

    # Documents README
    cat > "$base_path/documents/README.md" << EOF
# Documents Directory

This directory is for general document storage and organization.

## Suggested Organization

- **meetings/**: Meeting notes and agendas
- **projects/**: Project documentation and specs
- **reference/**: Reference materials and guides
- **archive/**: Older documents and historical records

## Tips

- Use descriptive filenames with dates (YYYY-MM-DD format)
- Keep active documents in the root for easy access
- Archive completed project documents regularly
- Ask Claude to help search and organize documents

EOF

    # Logs README
    cat > "$base_path/logs/README.md" << EOF
# Logs Directory

This directory contains system and application logs for troubleshooting and monitoring.

## Log Types

- **claude-desktop-setup.log**: Installation and setup logs
- **mcp-server.log**: MCP server operation logs
- **automation.log**: Script execution logs
- **error.log**: Error and exception tracking

## Log Rotation

Logs are automatically rotated to prevent disk space issues. Old logs are archived with timestamps.

## Troubleshooting

If you encounter issues, check the relevant log files or ask Claude to analyze them for you.

EOF

    success "Documentation files created"
}

# Set appropriate permissions
set_permissions() {
    local base_path="$1"
    
    info "Setting appropriate permissions..."
    
    # Ensure user has full access to the workspace
    chmod -R 755 "$base_path"
    
    # Make scripts executable if any exist
    find "$base_path/scripts" -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true
    
    success "Permissions set correctly"
}

# Validate filesystem setup
validate_setup() {
    local base_path="$1"
    
    info "Validating filesystem setup..."
    
    local required_dirs=("projects" "documents" "scripts" "logs")
    local validation_passed=true
    
    # Check directories exist
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$base_path/$dir" ]; then
            error "Missing directory: $dir"
            validation_passed=false
        fi
    done
    
    # Check Git repositories
    if [ ! -d "$base_path/projects/.git" ]; then
        error "Git repository not initialized in projects/"
        validation_passed=false
    fi
    
    if [ ! -d "$base_path/scripts/.git" ]; then
        error "Git repository not initialized in scripts/"
        validation_passed=false
    fi
    
    # Check README files
    if [ ! -f "$base_path/README.md" ]; then
        error "Main README.md not found"
        validation_passed=false
    fi
    
    if [ "$validation_passed" = true ]; then
        success "Filesystem setup validation passed"
        return 0
    else
        error "Filesystem setup validation failed"
        return 1
    fi
}

# Show setup summary
show_summary() {
    local base_path="$1"
    
    echo
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Filesystem Setup Complete${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo
    echo -e "${BLUE}Workspace Location:${NC} $base_path"
    echo
    echo -e "${BLUE}Directory Structure:${NC}"
    tree "$base_path" 2>/dev/null || ls -la "$base_path"
    echo
    echo -e "${BLUE}Git Repositories:${NC}"
    echo "  ✓ projects/ - Ready for development projects"
    echo "  ✓ scripts/ - Ready for automation scripts"
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Configure Claude Desktop with filesystem access to this path"
    echo "  2. Test Claude access: 'What's in my ClaudeDesktop directory?'"
    echo "  3. Start organizing your files and projects"
    echo
}

# Main function
main() {
    local base_path="${1:-/Users/$(whoami)/ClaudeDesktop}"
    
    case "${2:-setup}" in
        "setup")
            create_directory_structure "$base_path"
            initialize_git_repos "$base_path"
            create_readme_files "$base_path"
            set_permissions "$base_path"
            validate_setup "$base_path"
            show_summary "$base_path"
            ;;
        "validate")
            validate_setup "$base_path"
            ;;
        "summary")
            show_summary "$base_path"
            ;;
        *)
            echo "Usage: $0 [path] [setup|validate|summary]"
            echo
            echo "Commands:"
            echo "  setup    - Create complete directory structure (default)"
            echo "  validate - Validate existing setup"
            echo "  summary  - Show setup summary"
            echo
            echo "Default path: /Users/$(whoami)/ClaudeDesktop"
            exit 1
            ;;
    esac
}

main "$@"

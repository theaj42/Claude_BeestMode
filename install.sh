#!/bin/bash

# Claude Desktop Setup - Easy Button Installation
# Creates a pre-configured Claude Desktop environment with essential MCP servers

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_CLAUDE_DESKTOP_PATH="/Users/$(whoami)/ClaudeDesktop"
CLAUDE_CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/claude-desktop-setup.log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✓ $1${NC}"
    log "SUCCESS: $1"
}

# Info message
info() {
    echo -e "${BLUE}ℹ $1${NC}"
    log "INFO: $1"
}

# Warning message
warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
    log "WARNING: $1"
}

# Check if Claude Desktop is installed
check_claude_desktop() {
    info "Checking for Claude Desktop installation..."
    
    if [ ! -d "/Applications/Claude.app" ]; then
        error_exit "Claude Desktop not found. Please install Claude Desktop first from https://claude.ai/download"
    fi
    
    success "Claude Desktop found"
}

# Check system requirements
check_requirements() {
    info "Checking system requirements..."
    
    # Check for Python (for uvx)
    if ! command -v python3 &> /dev/null; then
        error_exit "Python 3 is required but not installed. Please install Python 3."
    fi
    
    # Check for Node.js (for npx)
    if ! command -v node &> /dev/null; then
        error_exit "Node.js is required but not installed. Please install Node.js from https://nodejs.org/"
    fi
    
    # Check for uvx
    if ! command -v uvx &> /dev/null; then
        warn "uvx not found. Installing uvx..."
        pip3 install uvx || error_exit "Failed to install uvx"
    fi
    
    success "System requirements satisfied"
}

# Backup existing configuration
backup_config() {
    info "Backing up existing Claude Desktop configuration..."
    
    if [ -f "$CLAUDE_CONFIG_PATH" ]; then
        local backup_path="${CLAUDE_CONFIG_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$CLAUDE_CONFIG_PATH" "$backup_path"
        success "Configuration backed up to: $backup_path"
    else
        info "No existing configuration found - will create new one"
    fi
}

# Get user preferences
get_user_preferences() {
    echo
    echo -e "${BLUE}=== Claude Desktop Setup Configuration ===${NC}"
    echo
    
    # Filesystem access path
    echo "The installer will create a directory structure for Claude to access."
    echo "Default location: $DEFAULT_CLAUDE_DESKTOP_PATH"
    echo
    read -p "Press Enter to use default, or specify a different path: " user_path
    
    if [ -n "$user_path" ]; then
        CLAUDE_DESKTOP_PATH="$user_path"
    else
        CLAUDE_DESKTOP_PATH="$DEFAULT_CLAUDE_DESKTOP_PATH"
    fi
    
    # Expand tilde if present
    CLAUDE_DESKTOP_PATH="${CLAUDE_DESKTOP_PATH/#\~/$HOME}"
    
    # Additional directories
    echo
    echo "Would you like to grant Claude access to additional directories?"
    echo "Current access will be limited to: $CLAUDE_DESKTOP_PATH"
    echo
    read -p "Add additional directories? (y/N): " add_dirs
    
    ADDITIONAL_DIRS=""
    if [[ "$add_dirs" =~ ^[Yy]$ ]]; then
        echo "Enter additional directories (one per line, empty line to finish):"
        while IFS= read -r dir; do
            [ -z "$dir" ] && break
            # Expand tilde if present
            dir="${dir/#\~/$HOME}"
            ADDITIONAL_DIRS="$ADDITIONAL_DIRS,$dir"
        done
    fi
}

# Create directory structure
create_directories() {
    info "Creating directory structure at: $CLAUDE_DESKTOP_PATH"
    
    # Create main directories
    mkdir -p "$CLAUDE_DESKTOP_PATH"/{projects,documents,scripts,logs}
    
    # Initialize Git repositories
    if [ ! -d "$CLAUDE_DESKTOP_PATH/projects/.git" ]; then
        (cd "$CLAUDE_DESKTOP_PATH/projects" && git init)
        success "Initialized Git repository in projects/"
    fi
    
    if [ ! -d "$CLAUDE_DESKTOP_PATH/scripts/.git" ]; then
        (cd "$CLAUDE_DESKTOP_PATH/scripts" && git init)
        success "Initialized Git repository in scripts/"
    fi
    
    # Create README files
    cat > "$CLAUDE_DESKTOP_PATH/README.md" << EOF
# Claude Desktop Workspace

This directory structure was created by the Claude Desktop Setup installer.

## Directory Structure

- **projects/**: Git-initialized directory for your projects
- **documents/**: General document storage
- **scripts/**: Git-initialized directory for scripts and automation
- **logs/**: System and application logs

## MCP Server Access

Claude has been configured with filesystem access to this directory tree.
You can ask Claude to read, write, and manage files within these directories.

## Getting Started

Try asking Claude:
- "What files do I have in my projects directory?"
- "Create a new project folder for [your project name]"
- "Help me organize my documents"

EOF

    success "Directory structure created successfully"
}

# Install MCP servers
install_mcp_servers() {
    info "Installing core MCP servers..."
    
    # Install Python-based servers via uvx
    local python_servers=("cli-mcp-server" "mcp-ical" "mcp-server-git")
    for server in "${python_servers[@]}"; do
        info "Installing $server..."
        if uvx install "$server"; then
            success "Installed $server"
        else
            warn "Failed to install $server - continuing with other servers"
        fi
    done
    
    # Note: Node.js servers are installed on-demand by npx
    success "MCP server installation completed"
}

# Merge MCP configuration
merge_config() {
    info "Configuring Claude Desktop with MCP servers..."
    
    # Read the template config
    local template_config="$SCRIPT_DIR/configs/default-mcp-config.json"
    local temp_config=$(mktemp)
    
    # Replace USERNAME placeholder
    sed "s/\$USERNAME/$(whoami)/g" "$template_config" > "$temp_config"
    
    # Update filesystem path
    sed -i.bak "s|/Users/$(whoami)/ClaudeDesktop|$CLAUDE_DESKTOP_PATH$ADDITIONAL_DIRS|g" "$temp_config"
    
    # If existing config exists, merge it
    if [ -f "$CLAUDE_CONFIG_PATH" ]; then
        # Create a merged configuration (simplified - just overwrite mcpServers section)
        local existing_config=$(mktemp)
        cp "$CLAUDE_CONFIG_PATH" "$existing_config"
        
        # Use jq to merge if available, otherwise replace
        if command -v jq &> /dev/null; then
            jq -s '.[0] * .[1]' "$existing_config" "$temp_config" > "$CLAUDE_CONFIG_PATH"
        else
            warn "jq not available - replacing entire configuration"
            cp "$temp_config" "$CLAUDE_CONFIG_PATH"
        fi
    else
        # Create config directory if it doesn't exist
        mkdir -p "$(dirname "$CLAUDE_CONFIG_PATH")"
        cp "$temp_config" "$CLAUDE_CONFIG_PATH"
    fi
    
    # Clean up
    rm -f "$temp_config" "$temp_config.bak"
    
    success "Claude Desktop configuration updated"
}

# Validate installation
validate_installation() {
    info "Validating installation..."
    
    # Check if config file exists and is valid JSON
    if [ -f "$CLAUDE_CONFIG_PATH" ]; then
        if command -v jq &> /dev/null; then
            if jq empty "$CLAUDE_CONFIG_PATH" 2>/dev/null; then
                success "Configuration file is valid JSON"
            else
                error_exit "Configuration file contains invalid JSON"
            fi
        else
            success "Configuration file created (JSON validation skipped - jq not available)"
        fi
    else
        error_exit "Configuration file was not created"
    fi
    
    # Check directory structure
    if [ -d "$CLAUDE_DESKTOP_PATH" ]; then
        success "Directory structure created successfully"
    else
        error_exit "Directory structure was not created"
    fi
    
    success "Installation validation completed"
}

# Main installation function
main() {
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════╗"
    echo "║           Claude Desktop Setup Installer         ║"
    echo "║                                                   ║"
    echo "║  Creates a pre-configured environment with        ║"
    echo "║  essential MCP servers for productive AI          ║"
    echo "║  collaboration from day one.                      ║"
    echo "╚═══════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    
    log "Starting Claude Desktop Setup installation"
    
    # Run installation steps
    check_claude_desktop
    check_requirements
    get_user_preferences
    backup_config
    create_directories
    install_mcp_servers
    merge_config
    validate_installation
    
    echo
    echo -e "${GREEN}🎉 Installation completed successfully! 🎉${NC}"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Restart Claude Desktop to load the new configuration"
    echo "2. Try asking Claude: 'What MCP servers do I have available?'"
    echo "3. Test the filesystem access: 'What's in my ClaudeDesktop directory?'"
    echo "4. Run the validation conversation (coming in Phase 3)"
    echo
    echo -e "${BLUE}Workspace location:${NC} $CLAUDE_DESKTOP_PATH"
    echo -e "${BLUE}Configuration:${NC} $CLAUDE_CONFIG_PATH"
    echo -e "${BLUE}Installation log:${NC} $LOG_FILE"
    echo
    echo "For troubleshooting, see the documentation or ask Claude for help!"
    
    log "Installation completed successfully"
}

# Run main function
main "$@"

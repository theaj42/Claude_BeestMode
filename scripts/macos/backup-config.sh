#!/bin/bash

# Claude Desktop Configuration Backup and Restore
# Handles backing up and restoring Claude Desktop configurations

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CLAUDE_CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
BACKUP_DIR="$HOME/.claude-desktop-backups"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "${HOME:-/tmp}/claude-desktop-setup.log" 2>/dev/null || true
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

# Create backup of current configuration
backup_config() {
    local backup_name="${1:-$(date +%Y%m%d_%H%M%S)}"
    
    info "Creating backup of Claude Desktop configuration..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    if [ -f "$CLAUDE_CONFIG_PATH" ]; then
        local backup_path="$BACKUP_DIR/claude_desktop_config_$backup_name.json"
        cp "$CLAUDE_CONFIG_PATH" "$backup_path"
        success "Configuration backed up to: $backup_path"
        
        # Validate backup is valid JSON
        if command -v jq &> /dev/null; then
            if jq empty "$backup_path" 2>/dev/null; then
                success "Backup file validated as valid JSON"
            else
                warn "Backup file may contain invalid JSON"
            fi
        fi
        
        echo "$backup_path"
    else
        warn "No existing configuration found to backup"
        return 1
    fi
}

# List available backups
list_backups() {
    info "Available configuration backups:"
    
    if [ -d "$BACKUP_DIR" ] && [ "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        ls -la "$BACKUP_DIR"/*.json 2>/dev/null | while read -r line; do
            echo "  $line"
        done
    else
        warn "No backups found"
    fi
}

# Restore from backup
restore_config() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        return 1
    fi
    
    info "Restoring configuration from: $backup_file"
    
    # Validate backup file is valid JSON
    if command -v jq &> /dev/null; then
        if ! jq empty "$backup_file" 2>/dev/null; then
            error "Backup file contains invalid JSON"
            return 1
        fi
    fi
    
    # Create a backup of current config before restoring
    if [ -f "$CLAUDE_CONFIG_PATH" ]; then
        backup_config "pre_restore_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Ensure config directory exists
    mkdir -p "$(dirname "$CLAUDE_CONFIG_PATH")"
    
    # Restore the backup
    cp "$backup_file" "$CLAUDE_CONFIG_PATH"
    success "Configuration restored from backup"
}

# Validate current configuration
validate_config() {
    info "Validating current Claude Desktop configuration..."
    
    if [ ! -f "$CLAUDE_CONFIG_PATH" ]; then
        warn "No configuration file found"
        return 1
    fi
    
    if command -v jq &> /dev/null; then
        if jq empty "$CLAUDE_CONFIG_PATH" 2>/dev/null; then
            success "Configuration file is valid JSON"
            
            # Show MCP servers if any
            local mcp_count=$(jq '.mcpServers | length // 0' "$CLAUDE_CONFIG_PATH" 2>/dev/null)
            info "MCP servers configured: $mcp_count"
            
            if [ "$mcp_count" -gt 0 ]; then
                echo "Configured servers:"
                jq -r '.mcpServers | keys[]' "$CLAUDE_CONFIG_PATH" 2>/dev/null | while read -r server; do
                    echo "  - $server"
                done
            fi
        else
            error "Configuration file contains invalid JSON"
            return 1
        fi
    else
        warn "jq not available - cannot validate JSON format"
    fi
}

# Show current configuration
show_config() {
    info "Current Claude Desktop configuration:"
    
    if [ -f "$CLAUDE_CONFIG_PATH" ]; then
        if command -v jq &> /dev/null; then
            jq . "$CLAUDE_CONFIG_PATH"
        else
            cat "$CLAUDE_CONFIG_PATH"
        fi
    else
        warn "No configuration file found"
    fi
}

# Clean old backups (keep last 10)
clean_backups() {
    info "Cleaning old backups (keeping last 10)..."
    
    if [ -d "$BACKUP_DIR" ]; then
        cd "$BACKUP_DIR"
        ls -t *.json 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
        success "Old backups cleaned"
    fi
}

# Main function
main() {
    case "${1:-backup}" in
        "backup")
            backup_config "${2:-}"
            ;;
        "list")
            list_backups
            ;;
        "restore")
            if [ $# -lt 2 ]; then
                error "Usage: $0 restore <backup-file>"
                exit 1
            fi
            restore_config "$2"
            ;;
        "validate")
            validate_config
            ;;
        "show")
            show_config
            ;;
        "clean")
            clean_backups
            ;;
        *)
            echo "Usage: $0 [backup|list|restore <file>|validate|show|clean]"
            echo
            echo "Commands:"
            echo "  backup [name]    - Create backup of current config"
            echo "  list            - List available backups"
            echo "  restore <file>  - Restore from backup file"
            echo "  validate        - Validate current config"
            echo "  show            - Show current config"
            echo "  clean           - Clean old backups"
            exit 1
            ;;
    esac
}

main "$@"

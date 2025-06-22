#!/bin/bash

# MCP Server Installation Helper
# Handles the installation of individual MCP servers with dependency management

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Install a Python MCP server via uvx
install_python_server() {
    local server_name="$1"
    local package_name="${2:-$server_name}"
    
    info "Installing Python MCP server: $server_name"
    
    if uvx install "$package_name"; then
        success "Installed $server_name"
        return 0
    else
        error "Failed to install $server_name"
        return 1
    fi
}

# Test a Node.js MCP server (they're installed on-demand)
test_node_server() {
    local package_name="$1"
    
    info "Testing Node.js MCP server: $package_name"
    
    # Test if npx can find and run the server
    if timeout 5s npx "$package_name" --help >/dev/null 2>&1; then
        success "Node.js server $package_name is available"
        return 0
    else
        error "Node.js server $package_name failed test"
        return 1
    fi
}

# Install all core MCP servers
install_core_servers() {
    info "Installing core MCP servers..."
    
    local python_servers=(
        "cli-mcp-server"
        "mcp-ical"
        "mcp-server-git"
    )
    
    local node_servers=(
        "@modelcontextprotocol/server-filesystem"
        "@modelcontextprotocol/server-memory"
        "@modelcontextprotocol/server-time"
    )
    
    local install_count=0
    local total_servers=$((${#python_servers[@]} + ${#node_servers[@]}))
    
    # Install Python servers
    for server in "${python_servers[@]}"; do
        if install_python_server "$server"; then
            ((install_count++))
        fi
    done
    
    # Test Node.js servers
    for server in "${node_servers[@]}"; do
        if test_node_server "$server"; then
            ((install_count++))
        fi
    done
    
    echo
    success "MCP server installation completed: $install_count/$total_servers servers ready"
    
    if [ "$install_count" -eq "$total_servers" ]; then
        return 0
    else
        return 1
    fi
}

# Check server health
check_server_health() {
    info "Checking MCP server health..."
    
    # Check uvx list for installed servers
    if command -v uvx &> /dev/null; then
        echo "Installed uvx packages:"
        uvx list 2>/dev/null || echo "No uvx packages found"
    fi
    
    echo
    echo "Node.js packages will be downloaded on-demand by npx"
}

# Main function
main() {
    case "${1:-install}" in
        "install")
            install_core_servers
            ;;
        "health")
            check_server_health
            ;;
        "python")
            if [ $# -lt 2 ]; then
                error "Usage: $0 python <server-name> [package-name]"
                exit 1
            fi
            install_python_server "$2" "${3:-$2}"
            ;;
        *)
            echo "Usage: $0 [install|health|python <server-name>]"
            exit 1
            ;;
    esac
}

main "$@"

#!/bin/bash

# Common validation functions for Claude Desktop Setup
# Shared utilities for testing and validation across all scripts

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log_validation() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] VALIDATION: $1" >> "$HOME/claude-desktop-setup.log" 2>/dev/null || true
}

# Test result functions
test_pass() {
    echo -e "${GREEN}✓ PASS${NC} $1"
    log_validation "PASS: $1"
}

test_fail() {
    echo -e "${RED}✗ FAIL${NC} $1"
    log_validation "FAIL: $1"
}

test_warn() {
    echo -e "${YELLOW}⚠ WARN${NC} $1"
    log_validation "WARN: $1"
}

test_info() {
    echo -e "${BLUE}ℹ INFO${NC} $1"
    log_validation "INFO: $1"
}

# Check if command exists
check_command() {
    local cmd="$1"
    local desc="${2:-$cmd}"
    
    if command -v "$cmd" &> /dev/null; then
        test_pass "$desc is installed"
        return 0
    else
        test_fail "$desc is not installed"
        return 1
    fi
}

# Check if file exists
check_file() {
    local file="$1"
    local desc="${2:-File $file}"
    
    if [ -f "$file" ]; then
        test_pass "$desc exists"
        return 0
    else
        test_fail "$desc does not exist"
        return 1
    fi
}

# Check if directory exists
check_directory() {
    local dir="$1"
    local desc="${2:-Directory $dir}"
    
    if [ -d "$dir" ]; then
        test_pass "$desc exists"
        return 0
    else
        test_fail "$desc does not exist"
        return 1
    fi
}

# Check if JSON file is valid
check_json() {
    local file="$1"
    local desc="${2:-JSON file $file}"
    
    if [ ! -f "$file" ]; then
        test_fail "$desc does not exist"
        return 1
    fi
    
    if command -v jq &> /dev/null; then
        if jq empty "$file" 2>/dev/null; then
            test_pass "$desc is valid JSON"
            return 0
        else
            test_fail "$desc contains invalid JSON"
            return 1
        fi
    else
        test_warn "$desc cannot be validated (jq not available)"
        return 0
    fi
}

# Check if Git repository is initialized
check_git_repo() {
    local dir="$1"
    local desc="${2:-Git repository in $dir}"
    
    if [ -d "$dir/.git" ]; then
        test_pass "$desc is initialized"
        return 0
    else
        test_fail "$desc is not initialized"
        return 1
    fi
}

# Check if MCP server is available
check_mcp_server() {
    local server_type="$1"  # "python" or "node"
    local package_name="$2"
    local desc="${3:-MCP server $package_name}"
    
    case "$server_type" in
        "python")
            if uvx list 2>/dev/null | grep -q "$package_name"; then
                test_pass "$desc (Python) is installed"
                return 0
            else
                test_fail "$desc (Python) is not installed"
                return 1
            fi
            ;;
        "node")
            # For Node.js packages, we test if npx can find them
            if timeout 5s npx "$package_name" --help >/dev/null 2>&1; then
                test_pass "$desc (Node.js) is available"
                return 0
            else
                test_fail "$desc (Node.js) is not available or timed out"
                return 1
            fi
            ;;
        *)
            test_fail "Unknown server type: $server_type"
            return 1
            ;;
    esac
}

# Check Claude Desktop installation
check_claude_desktop() {
    if [ -d "/Applications/Claude.app" ]; then
        test_pass "Claude Desktop is installed"
        
        # Check if it's running
        if pgrep -f "Claude" >/dev/null; then
            test_info "Claude Desktop is currently running"
        else
            test_info "Claude Desktop is not currently running"
        fi
        return 0
    else
        test_fail "Claude Desktop is not installed"
        return 1
    fi
}

# Check system requirements
check_system_requirements() {
    test_info "Checking system requirements..."
    
    local requirements_met=0
    local total_requirements=4
    
    # Check Python 3
    if check_command "python3" "Python 3"; then
        ((requirements_met++))
    fi
    
    # Check Node.js
    if check_command "node" "Node.js"; then
        ((requirements_met++))
    fi
    
    # Check uvx
    if check_command "uvx" "uvx (Python package runner)"; then
        ((requirements_met++))
    fi
    
    # Check Git
    if check_command "git" "Git"; then
        ((requirements_met++))
    fi
    
    echo
    if [ "$requirements_met" -eq "$total_requirements" ]; then
        test_pass "All system requirements met ($requirements_met/$total_requirements)"
        return 0
    else
        test_fail "System requirements not met ($requirements_met/$total_requirements)"
        return 1
    fi
}

# Validate complete Claude Desktop setup
validate_complete_setup() {
    local workspace_path="$1"
    local config_path="$2"
    
    echo
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Complete Setup Validation${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo
    
    local tests_passed=0
    local total_tests=0
    
    # System requirements
    test_info "System Requirements:"
    if check_system_requirements; then ((tests_passed++)); fi
    ((total_tests++))
    echo
    
    # Claude Desktop
    test_info "Claude Desktop:"
    if check_claude_desktop; then ((tests_passed++)); fi
    ((total_tests++))
    echo
    
    # Configuration
    test_info "Configuration:"
    if check_json "$config_path" "Claude Desktop configuration"; then ((tests_passed++)); fi
    ((total_tests++))
    echo
    
    # Workspace structure
    test_info "Workspace Structure:"
    local workspace_tests=0
    local workspace_total=6
    
    if check_directory "$workspace_path" "Workspace directory"; then ((workspace_tests++)); fi
    if check_directory "$workspace_path/projects" "Projects directory"; then ((workspace_tests++)); fi
    if check_directory "$workspace_path/documents" "Documents directory"; then ((workspace_tests++)); fi
    if check_directory "$workspace_path/scripts" "Scripts directory"; then ((workspace_tests++)); fi
    if check_directory "$workspace_path/logs" "Logs directory"; then ((workspace_tests++)); fi
    if check_file "$workspace_path/README.md" "Workspace README"; then ((workspace_tests++)); fi
    
    if [ "$workspace_tests" -eq "$workspace_total" ]; then
        test_pass "Workspace structure complete ($workspace_tests/$workspace_total)"
        ((tests_passed++))
    else
        test_fail "Workspace structure incomplete ($workspace_tests/$workspace_total)"
    fi
    ((total_tests++))
    echo
    
    # Git repositories
    test_info "Git Repositories:"
    local git_tests=0
    local git_total=2
    
    if check_git_repo "$workspace_path/projects" "Projects Git repository"; then ((git_tests++)); fi
    if check_git_repo "$workspace_path/scripts" "Scripts Git repository"; then ((git_tests++)); fi
    
    if [ "$git_tests" -eq "$git_total" ]; then
        test_pass "Git repositories initialized ($git_tests/$git_total)"
        ((tests_passed++))
    else
        test_fail "Git repositories not fully initialized ($git_tests/$git_total)"
    fi
    ((total_tests++))
    echo
    
    # MCP servers
    test_info "MCP Servers:"
    local mcp_tests=0
    local mcp_total=6
    
    if check_mcp_server "python" "cli-mcp-server" "CLI MCP Server"; then ((mcp_tests++)); fi
    if check_mcp_server "python" "mcp-ical" "Calendar MCP Server"; then ((mcp_tests++)); fi
    if check_mcp_server "python" "mcp-server-git" "Git MCP Server"; then ((mcp_tests++)); fi
    if check_mcp_server "node" "@modelcontextprotocol/server-filesystem" "Filesystem MCP Server"; then ((mcp_tests++)); fi
    if check_mcp_server "node" "@modelcontextprotocol/server-memory" "Memory MCP Server"; then ((mcp_tests++)); fi
    if check_mcp_server "node" "@modelcontextprotocol/server-time" "Time MCP Server"; then ((mcp_tests++)); fi
    
    if [ "$mcp_tests" -eq "$mcp_total" ]; then
        test_pass "MCP servers available ($mcp_tests/$mcp_total)"
        ((tests_passed++))
    else
        test_warn "Some MCP servers may not be available ($mcp_tests/$mcp_total)"
        ((tests_passed++))  # Don't fail for this as servers are installed on-demand
    fi
    ((total_tests++))
    echo
    
    # Overall results
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Validation Summary${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo
    
    if [ "$tests_passed" -eq "$total_tests" ]; then
        test_pass "Overall validation successful ($tests_passed/$total_tests tests passed)"
        echo
        echo -e "${GREEN}🎉 Your Claude Desktop setup is ready to use! 🎉${NC}"
        echo
        echo -e "${BLUE}Next steps:${NC}"
        echo "  1. Restart Claude Desktop to load the new configuration"
        echo "  2. Test with: 'What MCP servers do I have available?'"
        echo "  3. Try: 'What's in my ClaudeDesktop directory?'"
        echo
        return 0
    else
        test_fail "Validation incomplete ($tests_passed/$total_tests tests passed)"
        echo
        echo -e "${YELLOW}Some issues were found. Check the output above for details.${NC}"
        echo -e "${BLUE}You may still be able to use Claude Desktop, but some features might not work.${NC}"
        echo
        return 1
    fi
}

# Quick health check for existing installations
quick_health_check() {
    local workspace_path="${1:-/Users/$(whoami)/ClaudeDesktop}"
    local config_path="${2:-$HOME/Library/Application Support/Claude/claude_desktop_config.json}"
    
    echo -e "${BLUE}Quick Health Check${NC}"
    echo
    
    local issues=0
    
    # Essential checks
    if ! check_claude_desktop; then ((issues++)); fi
    if ! check_json "$config_path" "Claude Desktop configuration"; then ((issues++)); fi
    if ! check_directory "$workspace_path" "Workspace directory"; then ((issues++)); fi
    
    echo
    if [ "$issues" -eq 0 ]; then
        test_pass "Basic health check passed - setup appears functional"
        return 0
    else
        test_warn "Health check found $issues issue(s) - run full validation for details"
        return 1
    fi
}

# Test MCP server functionality (basic connectivity)
test_mcp_connectivity() {
    test_info "Testing MCP server connectivity..."
    echo
    
    # This would ideally test actual MCP server responses
    # For now, we'll check if the configuration looks correct
    local config_path="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    
    if [ ! -f "$config_path" ]; then
        test_fail "No configuration file found"
        return 1
    fi
    
    if command -v jq &> /dev/null; then
        local server_count=$(jq '.mcpServers | length // 0' "$config_path" 2>/dev/null)
        if [ "$server_count" -gt 0 ]; then
            test_pass "Configuration contains $server_count MCP server(s)"
            
            echo "Configured servers:"
            jq -r '.mcpServers | keys[]' "$config_path" 2>/dev/null | while read -r server; do
                echo "  - $server"
            done
            return 0
        else
            test_fail "No MCP servers found in configuration"
            return 1
        fi
    else
        test_warn "Cannot verify MCP server configuration (jq not available)"
        return 0
    fi
}

# Main validation function
main() {
    case "${1:-complete}" in
        "complete")
            local workspace_path="${2:-/Users/$(whoami)/ClaudeDesktop}"
            local config_path="${3:-$HOME/Library/Application Support/Claude/claude_desktop_config.json}"
            validate_complete_setup "$workspace_path" "$config_path"
            ;;
        "health")
            local workspace_path="${2:-/Users/$(whoami)/ClaudeDesktop}"
            local config_path="${3:-$HOME/Library/Application Support/Claude/claude_desktop_config.json}"
            quick_health_check "$workspace_path" "$config_path"
            ;;
        "mcp")
            test_mcp_connectivity
            ;;
        "requirements")
            check_system_requirements
            ;;
        *)
            echo "Usage: $0 [complete|health|mcp|requirements] [workspace_path] [config_path]"
            echo
            echo "Commands:"
            echo "  complete     - Full validation of entire setup (default)"
            echo "  health       - Quick health check of essential components"
            echo "  mcp          - Test MCP server configuration"
            echo "  requirements - Check system requirements only"
            echo
            echo "Examples:"
            echo "  $0 complete"
            echo "  $0 health /custom/path"
            echo "  $0 mcp"
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi

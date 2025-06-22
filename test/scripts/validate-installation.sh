#!/bin/bash

#################################################
# Claude Desktop Setup - Automated Validation
#################################################
# This script performs automated validation of the Claude Desktop Setup installation
# It tests all core MCP servers and workspace configuration

# Colors and formatting
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Variables
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="$HOME/claude-validation-$(date +%Y%m%d_%H%M%S).log"
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
WORKSPACE_ROOT="${CLAUDE_WORKSPACE:-$HOME/ClaudeDesktop}"
VALIDATION_PASSED=true
TESTS_RUN=0
TESTS_PASSED=0

# Functions
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_test() {
    TESTS_RUN=$((TESTS_RUN + 1))
    log "\n${BLUE}[TEST $TESTS_RUN]${NC} $1"
}

log_success() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    log "${GREEN}✓${NC} $1"
}

log_error() {
    VALIDATION_PASSED=false
    log "${RED}✗${NC} $1"
}

log_warning() {
    log "${YELLOW}⚠${NC} $1"
}

header() {
    log "\n${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "${BOLD}$1${NC}"
    log "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check if script is run from correct location
check_script_location() {
    if [[ ! -f "install.sh" ]]; then
        log_error "This script must be run from the claude-desktop-setup directory"
        log "Please navigate to the project directory and run: ./test/scripts/validate-installation.sh"
        exit 1
    fi
}

# Validation Tests
validate_claude_desktop() {
    header "Validating Claude Desktop Installation"
    
    log_test "Checking Claude Desktop installation"
    if [[ -d "/Applications/Claude.app" ]]; then
        log_success "Claude Desktop is installed"
    else
        log_error "Claude Desktop not found at /Applications/Claude.app"
        log "Please install Claude Desktop from https://claude.ai/download"
        return 1
    fi
    
    log_test "Checking Claude Desktop configuration file"
    if [[ -f "$CLAUDE_CONFIG" ]]; then
        log_success "Configuration file exists"
        
        # Check if it's valid JSON
        if jq empty "$CLAUDE_CONFIG" 2>/dev/null; then
            log_success "Configuration file is valid JSON"
        else
            log_error "Configuration file is not valid JSON"
            return 1
        fi
    else
        log_error "Configuration file not found at: $CLAUDE_CONFIG"
        return 1
    fi
}

validate_workspace() {
    header "Validating Workspace Structure"
    
    log_test "Checking workspace root directory"
    if [[ -d "$WORKSPACE_ROOT" ]]; then
        log_success "Workspace exists at: $WORKSPACE_ROOT"
    else
        log_error "Workspace not found at: $WORKSPACE_ROOT"
        return 1
    fi
    
    # Check subdirectories
    local dirs=("projects" "documents" "scripts" "logs")
    for dir in "${dirs[@]}"; do
        log_test "Checking $dir directory"
        if [[ -d "$WORKSPACE_ROOT/$dir" ]]; then
            log_success "$dir directory exists"
            
            # Check if Git directories are initialized
            if [[ "$dir" == "projects" || "$dir" == "scripts" ]]; then
                if [[ -d "$WORKSPACE_ROOT/$dir/.git" ]]; then
                    log_success "$dir is Git-initialized"
                else
                    log_warning "$dir is not Git-initialized"
                fi
            fi
        else
            log_error "$dir directory missing"
        fi
    done
}

validate_mcp_servers() {
    header "Validating MCP Server Configuration"
    
    # Check each required MCP server in config
    local servers=("cli-mcp-server" "filesystem" "memory" "time" "mcp-ical" "git")
    
    for server in "${servers[@]}"; do
        log_test "Checking $server configuration"
        
        # Use jq to check if server exists in config
        if jq -e ".mcpServers[\"$server\"]" "$CLAUDE_CONFIG" >/dev/null 2>&1; then
            log_success "$server is configured"
            
            # Check command exists
            local cmd=$(jq -r ".mcpServers[\"$server\"].command" "$CLAUDE_CONFIG")
            if [[ "$cmd" != "null" ]]; then
                log_success "$server command is set: $cmd"
            else
                log_error "$server command is not configured"
            fi
        else
            log_error "$server is not configured in Claude Desktop"
        fi
    done
}

validate_dependencies() {
    header "Validating System Dependencies"
    
    # Check Python
    log_test "Checking Python installation"
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version 2>&1)
        log_success "Python installed: $python_version"
    else
        log_error "Python 3 is not installed"
    fi
    
    # Check Node.js
    log_test "Checking Node.js installation"
    if command -v node &> /dev/null; then
        local node_version=$(node --version 2>&1)
        log_success "Node.js installed: $node_version"
    else
        log_error "Node.js is not installed"
    fi
    
    # Check Git
    log_test "Checking Git installation"
    if command -v git &> /dev/null; then
        local git_version=$(git --version 2>&1)
        log_success "Git installed: $git_version"
    else
        log_error "Git is not installed"
    fi
    
    # Check uvx
    log_test "Checking uvx installation"
    if command -v uvx &> /dev/null; then
        log_success "uvx is installed"
    else
        log_warning "uvx is not installed (pip3 install uvx)"
    fi
    
    # Check npx
    log_test "Checking npx installation"
    if command -v npx &> /dev/null; then
        log_success "npx is installed"
    else
        log_warning "npx is not installed (comes with npm)"
    fi
}

validate_filesystem_permissions() {
    header "Validating Filesystem Permissions"
    
    log_test "Checking workspace write permissions"
    local test_file="$WORKSPACE_ROOT/validation-test-$$.txt"
    if echo "test" > "$test_file" 2>/dev/null; then
        log_success "Can write to workspace"
        rm -f "$test_file"
    else
        log_error "Cannot write to workspace directory"
    fi
    
    # Check filesystem MCP server scope
    log_test "Checking filesystem server configuration"
    local fs_paths=$(jq -r '.mcpServers.filesystem.args[]' "$CLAUDE_CONFIG" 2>/dev/null | grep -v null)
    if [[ -n "$fs_paths" ]]; then
        log_success "Filesystem paths configured:"
        echo "$fs_paths" | while read -r path; do
            if [[ -d "$path" ]]; then
                log "  ${GREEN}✓${NC} $path exists"
            else
                log "  ${RED}✗${NC} $path does not exist"
            fi
        done
    else
        log_warning "No filesystem paths configured"
    fi
}

validate_knowledge_base() {
    header "Validating Knowledge Base"
    
    log_test "Checking knowledge base configuration"
    local kb_file="configs/knowledge-base/system-entities.json"
    
    if [[ -f "$kb_file" ]]; then
        log_success "Knowledge base file exists"
        
        # Check if it's valid JSON
        if jq empty "$kb_file" 2>/dev/null; then
            log_success "Knowledge base is valid JSON"
            
            # Count entities
            local entity_count=$(jq '.entities | length' "$kb_file" 2>/dev/null)
            log_success "Knowledge base contains $entity_count entities"
        else
            log_error "Knowledge base is not valid JSON"
        fi
    else
        log_error "Knowledge base file not found"
    fi
}

generate_health_report() {
    header "Health Check Summary"
    
    log "\n${BOLD}Validation Results:${NC}"
    log "Tests Run: $TESTS_RUN"
    log "Tests Passed: $TESTS_PASSED"
    log "Tests Failed: $((TESTS_RUN - TESTS_PASSED))"
    
    if [[ "$VALIDATION_PASSED" == true ]]; then
        log "\n${GREEN}${BOLD}✓ VALIDATION PASSED${NC}"
        log "Your Claude Desktop Setup is ready for use!"
        
        log "\n${BOLD}Next Steps:${NC}"
        log "1. Restart Claude Desktop to ensure all MCP servers are loaded"
        log "2. Test the installation using the validation conversation:"
        log "   - Open Claude Desktop"
        log "   - Copy the contents of test/validation-conversation.md"
        log "   - Paste into a new conversation with Claude"
        log "3. Start using your enhanced Claude Desktop environment!"
    else
        log "\n${RED}${BOLD}✗ VALIDATION FAILED${NC}"
        log "Please address the issues above and run validation again."
        
        log "\n${BOLD}Troubleshooting:${NC}"
        log "1. Check the detailed log at: $LOG_FILE"
        log "2. Run the installation script again: ./install.sh"
        log "3. Consult the troubleshooting guide in the README"
        log "4. Ask Claude for help with the specific errors"
    fi
    
    log "\n${BOLD}Full validation log saved to:${NC} $LOG_FILE"
}

# Main execution
main() {
    clear
    log "${BOLD}Claude Desktop Setup - Automated Validation${NC}"
    log "Started at: $TIMESTAMP"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Run all validation tests
    validate_claude_desktop
    validate_dependencies
    validate_workspace
    validate_mcp_servers
    validate_filesystem_permissions
    validate_knowledge_base
    
    # Generate final report
    generate_health_report
    
    # Set exit code based on validation result
    if [[ "$VALIDATION_PASSED" == true ]]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"

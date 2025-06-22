#!/bin/bash

#################################################
# Claude Desktop Setup - Health Check
#################################################
# Quick health check for Claude Desktop MCP ecosystem
# Can be run periodically to ensure system health

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Quick checks
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
WORKSPACE_ROOT="${CLAUDE_WORKSPACE:-$HOME/ClaudeDesktop}"

echo "Claude Desktop Health Check - $(date '+%Y-%m-%d %H:%M:%S')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Claude Desktop running
if pgrep -q "Claude"; then
    echo -e "${GREEN}✓${NC} Claude Desktop is running"
else
    echo -e "${YELLOW}⚠${NC} Claude Desktop is not running"
fi

# Check configuration exists
if [[ -f "$CLAUDE_CONFIG" ]]; then
    echo -e "${GREEN}✓${NC} Configuration file exists"
    
    # Count MCP servers
    server_count=$(jq '.mcpServers | length' "$CLAUDE_CONFIG" 2>/dev/null || echo "0")
    echo -e "${GREEN}✓${NC} $server_count MCP servers configured"
else
    echo -e "${RED}✗${NC} Configuration file missing"
fi

# Check workspace
if [[ -d "$WORKSPACE_ROOT" ]]; then
    echo -e "${GREEN}✓${NC} Workspace exists at $WORKSPACE_ROOT"
    
    # Check subdirectories
    for dir in projects documents scripts logs; do
        if [[ -d "$WORKSPACE_ROOT/$dir" ]]; then
            echo -e "  ${GREEN}✓${NC} $dir/"
        else
            echo -e "  ${RED}✗${NC} $dir/ missing"
        fi
    done
else
    echo -e "${RED}✗${NC} Workspace missing at $WORKSPACE_ROOT"
fi

# Check for recent errors in logs
if [[ -d "$WORKSPACE_ROOT/logs" ]]; then
    recent_errors=$(find "$WORKSPACE_ROOT/logs" -name "*.log" -mtime -1 -exec grep -l "ERROR\|FAIL" {} \; 2>/dev/null | wc -l)
    if [[ $recent_errors -eq 0 ]]; then
        echo -e "${GREEN}✓${NC} No recent errors in logs"
    else
        echo -e "${YELLOW}⚠${NC} Found errors in $recent_errors log file(s)"
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Run './test/scripts/validate-installation.sh' for detailed validation"

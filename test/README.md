# Claude Desktop Setup - Testing & Validation

This directory contains comprehensive testing and validation tools for the Claude Desktop Setup.

## Available Tools

### 1. Validation Conversation (`validation-conversation.md`)
A comprehensive conversation template that tests all MCP server capabilities through natural interaction with Claude.

**Usage:**
1. Complete the installation
2. Restart Claude Desktop
3. Copy the contents of `validation-conversation.md`
4. Paste into a new Claude conversation
5. Follow the interactive tests

**Tests:**
- All 6 MCP servers (CLI, Filesystem, Memory, Time, Calendar, Git)
- Multi-server workflows
- Error handling and diagnostics
- Context persistence

### 2. Automated Validation Script (`scripts/validate-installation.sh`)
Bash script that performs automated validation of the entire installation.

**Usage:**
```bash
# From the project root directory
./test/scripts/validate-installation.sh
```

**Tests:**
- Claude Desktop installation
- Configuration file validity
- Workspace structure
- MCP server configurations
- System dependencies
- Filesystem permissions
- Knowledge base integrity

**Output:**
- Colored terminal output
- Detailed log file with timestamp
- Pass/fail summary with next steps

### 3. Quick Health Check (`scripts/health-check.sh`)
Lightweight script for periodic system health monitoring.

**Usage:**
```bash
# Quick health check
./test/scripts/health-check.sh

# Add to cron for regular checks
*/30 * * * * /path/to/claude-desktop-setup/test/scripts/health-check.sh
```

**Checks:**
- Claude Desktop process status
- Configuration file presence
- Workspace directory structure
- Recent error logs
- MCP server count

### 4. Interactive Validation (`scripts/interactive-validation.py`)
Python script that performs deeper validation with actual file operations.

**Usage:**
```bash
# Run interactive validation
./test/scripts/interactive-validation.py
```

**Features:**
- Real file I/O testing in workspace
- Dependency version checking
- Knowledge base content validation
- Detailed configuration analysis
- Pretty formatted output

### 5. Onboarding Conversation (`onboarding-conversation.md`)
A guided conversation template for new users to learn their enhanced Claude Desktop.

**Usage:**
1. After successful validation
2. Copy contents of `onboarding-conversation.md`
3. Start new Claude conversation
4. Follow the guided tour

**Covers:**
- Understanding MCP capabilities
- Basic workflows and commands
- Personalization and preferences
- Advanced features and automation
- Best practices

## Validation Workflow

### Initial Setup Validation
1. Run `validate-installation.sh` for comprehensive checks
2. Fix any reported issues
3. Use `validation-conversation.md` with Claude
4. Complete `onboarding-conversation.md` for familiarization

### Ongoing Health Monitoring
1. Run `health-check.sh` periodically
2. Check logs in `~/ClaudeDesktop/logs/`
3. Use `interactive-validation.py` after updates
4. Ask Claude to perform self-diagnostics

## Troubleshooting

### Common Issues

**Validation script fails to run**
- Ensure execute permissions: `chmod +x scripts/*.sh scripts/*.py`
- Run from project root directory
- Check bash/python paths in shebang lines

**MCP servers not detected**
- Restart Claude Desktop after installation
- Verify configuration at `~/Library/Application Support/Claude/claude_desktop_config.json`
- Check server installation with uvx/npx

**Workspace permissions errors**
- Check directory ownership: `ls -la ~/ClaudeDesktop`
- Fix permissions: `chmod -R u+rwX ~/ClaudeDesktop`
- Verify filesystem server configuration includes workspace path

**Knowledge base not loading**
- Run `scripts/load_entities.py` manually
- Check JSON validity of system-entities.json
- Verify memory MCP server is configured

### Getting Help

1. **Check validation logs**: Look for detailed error messages
2. **Ask Claude**: With filesystem access, Claude can help debug
3. **Review documentation**: Check README and troubleshooting guides
4. **Run diagnostics**: Use the various validation scripts

## Test Development

### Adding New Tests

To add new validation tests:

1. **Bash tests**: Add functions to `validate-installation.sh`
2. **Python tests**: Add methods to `MCPValidator` class
3. **Conversation tests**: Add sections to validation-conversation.md
4. **Health checks**: Add quick checks to `health-check.sh`

### Test Guidelines

- Keep tests focused and atomic
- Provide clear success/failure messages
- Include remediation steps for failures
- Use consistent formatting and colors
- Log detailed information for debugging

## Success Metrics

A successful validation shows:
- ✅ All MCP servers configured and accessible
- ✅ Workspace properly structured with Git repos
- ✅ File operations working in designated paths
- ✅ Knowledge base loaded and queryable
- ✅ System dependencies installed
- ✅ No critical errors in logs

With these tools, users can confidently validate their Claude Desktop Setup and maintain it over time.

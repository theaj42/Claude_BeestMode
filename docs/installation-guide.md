# Installation Guide

## Quick Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/theaj42/Claude_BeestMode/main/install.sh | bash
```

## What the Installation Does

### 1. Prerequisites Check
- Verifies macOS environment
- Confirms Claude Desktop installation
- Checks for required tools (curl, git, python3)

### 2. Configuration Backup
- Creates timestamped backup of existing Claude Desktop config
- Ensures you can rollback if needed

### 3. Directory Structure Creation
- Creates `~/ClaudeDesktop/` workspace (or custom path)
- Sets up organized project structure
- Initializes Git repositories

### 4. MCP Server Installation
- Installs essential MCP servers via uvx/pip
- Configures secure filesystem access
- Sets up memory, time, and Git integration

### 5. Claude Desktop Configuration
- Updates configuration file with MCP server settings
- Maintains existing settings while adding new capabilities

### 6. Validation
- Tests all installed components
- Provides clear success/failure feedback

## Manual Installation

If you prefer to install manually or need to troubleshoot:

### Step 1: Clone Repository
```bash
git clone https://github.com/theaj42/Claude_BeestMode.git
cd Claude_BeestMode
```

### Step 2: Run Installation Script
```bash
./install.sh
```

### Step 3: Restart Claude Desktop
Close and reopen Claude Desktop to load the new configuration.

## Troubleshooting

### Installation Fails
1. Check the installation log (location shown in output)
2. Verify prerequisites are installed
3. Ensure Claude Desktop is properly installed

### Claude Desktop Doesn't Recognize MCP Servers
1. Verify configuration file was updated correctly
2. Check file permissions on the configuration
3. Try restarting Claude Desktop again

### Permission Issues
The installer creates directories with appropriate permissions. If you encounter issues:
```bash
chmod -R 755 ~/ClaudeDesktop
```

## Custom Installation Options

### Custom Workspace Directory
During installation, you'll be prompted to choose the workspace location. Default is `~/ClaudeDesktop/` but you can specify any path you prefer.

### Additional Directory Access
After basic installation, you can grant Claude access to additional directories by modifying the filesystem MCP configuration.

## Post-Installation

Once installation completes:
1. Restart Claude Desktop
2. Open a new conversation
3. Test with: "List the files in my BeestMode directory"
4. Follow the [Usage Guide](usage-guide.md) for next steps

## Uninstalling

To remove BeestMode:
1. Restore backup configuration file
2. Remove the workspace directory
3. Uninstall MCP servers if desired

Detailed uninstall instructions coming soon.

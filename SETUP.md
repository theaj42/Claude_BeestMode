# Setup Guide - Claude BeestMode

This guide will walk you through installing and configuring Claude BeestMode on your system.

## Prerequisites

Before you begin, ensure you have:

- **macOS** (Windows/Linux support coming in future phases)
- **Claude Desktop** installed ([download here](https://claude.ai/download))
- **Python 3.8+** installed
- **Node.js 18+** installed
- **Git** installed
- **Basic terminal/command-line familiarity**

### Verify Prerequisites

```bash
# Check Python version
python3 --version

# Check Node.js version
node --version

# Check Git
git --version
```

## Important Safety Considerations

⚠️ **READ THIS BEFORE INSTALLING** ⚠️

This installer gives Claude the ability to:
- **Create, modify, and DELETE files** in designated directories
- **Execute system commands** (if you enable CLI access)
- **Make permanent changes** to your filesystem

**Only install if you:**
- Understand the capabilities you're granting
- Trust Claude Desktop with filesystem access
- Maintain regular backups of important data
- Are comfortable with the security implications

## Installation Steps

### 1. Clone the Repository

```bash
# Clone to your preferred location
git clone https://github.com/theaj42/Claude_BeestMode.git
cd Claude_BeestMode
```

### 2. Create Your Data Directory

BeestMode separates **Engine** (code) from **Fuel** (your data). Choose where your data will live:

```bash
# Recommended: Create a dedicated data directory
mkdir -p ~/ai-data

# Or use an existing directory like your Obsidian vault
# ~/obsidian/YourVault
# ~/Documents/AI-Data
```

### 3. Configure Data Location

Copy the example settings and configure your data path:

```bash
# Copy the example configuration
cp config/settings.example.yaml config/settings.yaml

# Edit the configuration
nano config/settings.yaml  # or use your preferred editor
```

Update `settings.yaml` to point to your data directory:

```yaml
data_root: "/Users/yourusername/ai-data"  # Update this path
```

### 4. Run the Installer

Execute the main installation script:

```bash
./install.sh
```

The installer will:
- Back up your existing Claude Desktop configuration
- Install essential MCP servers (memory, filesystem, CLI, git, etc.)
- Create organized workspace directories
- Set up the Python agent environment
- Merge configurations safely

**What to expect:**
- Installation takes 2-5 minutes
- You'll see progress messages for each step
- Any errors will be clearly reported
- Your original config is backed up automatically

### 5. Restart Claude Desktop

After installation completes:

1. **Quit Claude Desktop completely** (⌘+Q)
2. **Restart Claude Desktop**
3. Wait for it to load the new MCP servers (may take 30-60 seconds)

### 6. Bootstrap Your Context

To help Claude understand your workflow:

```bash
# Copy the template to your data directory
cp bootstrap/context_template.md ~/ai-data/bootstrap.md

# Edit with your actual context paths
nano ~/ai-data/bootstrap.md
```

Then in Claude Desktop:
```
Load context from @~/ai-data/bootstrap.md
```

## Verification

### Check MCP Servers Are Loaded

In Claude Desktop, you should see indicators that MCP servers are active. You can verify by asking Claude:

```
What MCP servers do you have access to?
```

Expected response should include: memory, filesystem, time, git, calendar, etc.

### Test the AI Engine

If you want to use the Python agents directly:

```bash
# Activate the virtual environment
source ~/ClaudeDesktop/.venv/bin/activate

# Test the task extractor agent
python3 engine/agents/task_extractor.py --help
```

## Workspace Structure

After installation, you'll have:

```
~/ClaudeDesktop/
├── projects/    # Git-initialized for development work
├── documents/   # General document storage
├── scripts/     # Git-initialized for automation scripts
├── logs/        # System and error logs
└── .venv/       # Python virtual environment for agents
```

And your data directory (e.g., `~/ai-data/`):
```
~/ai-data/
├── bootstrap.md       # Context loading file
├── context/           # Your context files (create as needed)
├── logs/              # Session logs (optional)
└── memory/            # ChromaDB and knowledge base (optional)
```

## Troubleshooting

### Claude Desktop Won't Start

1. Check the Claude Desktop logs: `~/Library/Logs/Claude/`
2. Restore the backup config:
   ```bash
   ./scripts/macos/backup-config.sh restore ~/.claude-desktop-backups/[latest-backup].json
   ```

### MCP Servers Not Loading

1. Verify the config file is valid JSON:
   ```bash
   ./scripts/macos/backup-config.sh validate
   ```
2. Check Node.js version is 18+
3. Look for errors in Claude Desktop logs

### Python Agents Not Working

1. Verify virtual environment exists:
   ```bash
   ls -la ~/ClaudeDesktop/.venv
   ```
2. Reinstall dependencies:
   ```bash
   cd ~/ClaudeDesktop
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r ~/git/Claude_BeestMode/engine/requirements.txt
   ```

### Permission Errors

If you see permission errors:
```bash
# Make install script executable
chmod +x install.sh

# Make all scripts executable
chmod +x scripts/**/*.sh
```

## Customization

### Add Additional MCP Servers

Edit your Claude Desktop config directly:
```bash
./scripts/macos/backup-config.sh show
```

### Change Workspace Location

The default workspace is `~/ClaudeDesktop/`. To change:
1. Edit `install.sh` before running
2. Update the `WORKSPACE_ROOT` variable

### Modify Agent Configuration

Agent settings are in `config/settings.yaml`:
- Data paths
- API keys (if needed)
- Agent-specific settings

## Uninstallation

To remove BeestMode:

1. Restore original Claude config:
   ```bash
   ./scripts/macos/backup-config.sh list
   ./scripts/macos/backup-config.sh restore [pre-install backup]
   ```

2. Remove workspace (optional):
   ```bash
   rm -rf ~/ClaudeDesktop
   ```

3. Remove engine repo:
   ```bash
   cd ..
   rm -rf Claude_BeestMode
   ```

**Note:** Your data directory (`~/ai-data`) is never touched by the installer, so it's safe.

## Next Steps

After successful installation:

1. **Review the [README.md](README.md)** for feature overview
2. **Check the [ROADMAP.md](ROADMAP.md)** for upcoming features
3. **Explore the Python agents** in `engine/agents/`
4. **Join discussions** on GitHub for tips and best practices

## Getting Help

- **Installation Issues**: Open a GitHub Issue with your installation logs
- **Usage Questions**: Check GitHub Discussions
- **Bug Reports**: Use GitHub Issues with detailed reproduction steps

## Philosophy: Engine vs. Fuel

Remember the core principle:
- **Engine** (this repo): Code, agents, installers - safe to update
- **Fuel** (your data): Personal notes, context, memories - never in this repo

Keep them separate, keep your data private, and enjoy seamless updates.

---

**Installation complete?** Start by asking Claude: "Help me understand what capabilities you now have with the MCP servers."

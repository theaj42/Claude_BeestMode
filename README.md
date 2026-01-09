# Claude BeestMode (v2.0)

**A production-grade AI Assistant Engine and MCP Server Installer.**

## 🚀 New in v2.0: The Engine

We've added a portable, privacy-first **AI Agent Engine** based on the architecture used in a production environment. 

### Key Features
*   **Engine vs. Fuel Separation**: The logic (`engine/`) is kept separate from your personal data (`~/ai-data`), making upgrades safe and easy.
*   **Self-Contained Agents**: Includes production-ready Python agents (e.g., `task_extractor`) that can run locally.
*   **Portable Configuration**: No more hardcoded paths. Configure your data location in `config/settings.yaml`.
*   **Bootstrap Templates**: Quickly load your context into Claude using `bootstrap/context_template.md`.

---

# Claude Desktop Setup - Easy Button Installation

**Create a pre-configured Claude Desktop environment with essential MCP servers for productive AI collaboration from day one.**

## Overview

This installer bridges the gap between sophisticated AI automation and mainstream accessibility. Instead of spending hours exploring and configuring MCP servers, users get a working, productive setup with a single command.

## What You Get

### 1. The AI Engine (New)
*   **Python Agent Framework**: Run autonomous agents locally.
*   **Task Extraction**: Automatically parse your notes into Todoist tasks.
*   **Knowledge Synthesis**: (Coming soon) Summarize your daily activities.

### 2. Core MCP Server Pod
- **CLI Access**: Direct system command execution
- **Filesystem**: Scoped file operations and management  
- **Memory**: Persistent knowledge graph across sessions
- **Time**: Temporal awareness and scheduling
- **Calendar**: Apple Calendar integration
- **Git**: Version control operations

### 3. Organized Workspace
```
/Users/username/ClaudeDesktop/
├── projects/    (Git-initialized for development)
├── documents/   (General document storage)
├── scripts/     (Git-initialized for automation)
└── logs/        (System and error logs)
```

## Quick Start

### Prerequisites
- macOS (Windows/Linux support coming in later phases)
- Claude Desktop installed
- Python 3 and Node.js

### Installation

⚠️ **IMPORTANT SAFETY WARNING** ⚠️

This installer gives Claude the ability to:
- **Create, modify, and DELETE files** in designated directories
- **Execute system commands** (if you enable CLI access)
- **Make permanent changes** to your filesystem

Only install if you're comfortable with Claude having these capabilities. Always maintain backups of important data.

---

```bash
# Clone the repository
git clone https://github.com/theaj42/Claude_BeestMode.git
cd Claude_BeestMode

# 1. Setup Configuration
cp config/settings.example.yaml config/settings.yaml
# Edit config/settings.yaml to point to your data

# 2. Run the MCP Installer
./install.sh
```

### After Installation

1. **Restart Claude Desktop** to load the new configuration
2. **Bootstrap Context**:
   * Copy `bootstrap/context_template.md` to your data repo (e.g., `~/ai-data/bootstrap.md`).
   * Tell Claude: "Load context from @~/ai-data/bootstrap.md".

## Architecture: Engine vs. Fuel

This repository follows a strict separation of concerns:

*   **The Engine (This Repo)**: Contains the code, agents, tools, and installers. It is stateless and safe to update/pull.
*   **The Fuel (Your Data)**: Your personal markdown notes, memory database, and logs. This should live in a separate private repository (e.g., `~/ai-data` or `~/obsidian/Vault`).

Configure the location of your "Fuel" in `config/settings.yaml`.

## Advanced Usage & Agents

See `engine/README.md` (coming soon) for details on running the Python agents directly.

## Development Roadmap

### Phase 1: Core Installation System ✅ COMPLETE
- [x] macOS installation script
- [x] MCP server automation
- [x] Configuration backup/merge

### Phase 2: The AI Engine ✅ IN PROGRESS
- [x] Portable Agent Architecture
- [x] Task Extractor Agent
- [x] Configuration Abstraction
- [ ] Knowledge Synthesizer Port
- [ ] Memory System Port

## Contributing

This project welcomes contributions!
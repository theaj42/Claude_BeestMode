# Claude BeestMode Context

This repository contains the **AI Assistant Engine** and **MCP Installer**.

## Architecture
- **Engine**: Located in `engine/`. Contains Python agents and utilities.
- **Config**: Located in `config/`. `settings.yaml` defines where user data lives.
- **Bootstrap**: Templates in `bootstrap/` for loading user context.
- **Installers**: Shell scripts in `scripts/` and root `install.sh`.

## Developer Guidelines
- **Portability**: Never hardcode paths like `/Users/name`. Use `engine.config.settings`.
- **Separation**: User data ("Fuel") must never be stored in this repo. It belongs in `data_root`.
- **Agents**: Agents must inherit from `SelfContainedAgent` and handle their own dependencies.

## Key Commands
- **Install**: `./install.sh`
- **Run Agent**: `python3 engine/agents/task_extractor.py` (requires venv)
- **Check Health**: `python3 engine/monitoring/health_check.py` (coming soon)

## Bootstrapping
To help a user start:
1. Ask them if they have a `~/ai-data` directory.
2. Recommend copying `bootstrap/context_template.md` to their data folder.
3. Instruct them to `@`-reference it.

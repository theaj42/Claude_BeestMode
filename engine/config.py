import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Root of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent

class Config:
    def __init__(self):
        self._settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from config/settings.yaml or fall back to defaults"""
        settings_path = REPO_ROOT / "config" / "settings.yaml"
        
        if not settings_path.exists():
            # Fallback to example if available, or empty dict
            example_path = REPO_ROOT / "config" / "settings.example.yaml"
            if example_path.exists():
                try:
                    with open(example_path, "r") as f:
                        return yaml.safe_load(f) or {}
                except Exception:
                    pass
            return {}
            
        try:
            with open(settings_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Failed to load settings.yaml: {e}")
            return {}

    @property
    def data_root(self) -> Path:
        """Return path to data root (Fuel), expanded and resolved"""
        raw_path = self._settings.get("data_root", "~/ai-data")
        return Path(raw_path).expanduser().resolve()

    @property
    def obsidian_vault(self) -> Optional[Path]:
        """Return path to Obsidian vault if configured"""
        raw_path = self._settings.get("obsidian_vault")
        if raw_path:
            return Path(raw_path).expanduser().resolve()
        return None

    @property
    def project_root(self) -> Path:
        """Return the root of the engine code"""
        return REPO_ROOT

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration specific to an agent"""
        agents_config = self._settings.get("agents", {})
        return agents_config.get(agent_name, {})

# Global config instance
settings = Config()

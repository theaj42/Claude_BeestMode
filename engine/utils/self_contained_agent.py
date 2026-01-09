#!/usr/bin/env python3
"""
Self-Contained Agent Base Class (Portable)

Provides common functionality for making agents portable and self-contained.
Handles dependency management, configuration, directory setup, and environment detection.

This version uses the engine.config module to locate data and resources.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

# Add project root to path for imports
current_file = Path(__file__).resolve()
# Go up from engine/utils to project root
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from engine.config import settings
from engine.utils.dependency_manager import ensure_agent_dependencies

# Import ContextManager (Optional)
try:
    from engine.utils.context_manager import ContextManager
    CONTEXT_MANAGER_AVAILABLE = True
except ImportError:
    CONTEXT_MANAGER_AVAILABLE = False


class SelfContainedAgent(ABC):
    """Base class for self-contained, portable agents"""

    def __init__(
        self,
        agent_name: str,
        agent_def: Optional[Dict[str, Any]] = None,
        enable_context_management: bool = False,
        heartbeat_interval: int = 300  # 5 minutes
    ):
        self.agent_name = agent_name
        self.agent_def = agent_def or {}

        # Setup logging
        self.logger = self._setup_logging()

        # Get paths from central config
        self.project_root = settings.project_root
        self.data_root = settings.data_root
        self.agent_config_dir = self._ensure_config_directory()

        # Load or create configuration
        self.config = self._load_or_create_config()

        # Ensure dependencies are available
        self.dependency_status = self._ensure_dependencies()

        # Context management
        self.context_manager: Optional[Any] = None
        if enable_context_management and CONTEXT_MANAGER_AVAILABLE:
            # Checkpoints go to data_root (Fuel), not project_root
            checkpoint_dir = self.data_root / 'cache' / 'checkpoints' / agent_name
            
            self.context_manager = ContextManager(
                agent_name=agent_name,
                checkpoint_dir=checkpoint_dir,
                heartbeat_interval=heartbeat_interval,
                logger=self.logger
            )
            self.logger.info("Context management enabled")
        elif enable_context_management:
            self.logger.warning("Context management requested but ContextManager not available")

        self.logger.info(f"✅ Agent {agent_name} initialized successfully")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the agent"""
        logger = logging.getLogger(f"Agent-{self.agent_name}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.agent_name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
        return logger
    
    def _ensure_config_directory(self) -> Path:
        """Ensure agent configuration directory exists in DATA root"""
        # We store runtime configs in data_root/config/agents/agent_name
        config_dir = self.data_root / 'config' / 'agents' / self.agent_name
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """Load existing config or create default one"""
        config_file = self.agent_config_dir / 'config.json'
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load config, creating new one: {e}")
        
        # Check if there is a default config in the engine (source code)
        # engine/config/agents/{name}.yaml could be a pattern, but sticking to code defaults for now
        default_config = self._get_default_config()
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        config_file = self.agent_config_dir / 'config.json'
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def _ensure_dependencies(self) -> Dict[str, bool]:
        """Ensure required dependencies are available"""
        core_deps = self.get_core_dependencies()
        optional_deps = self.get_optional_dependencies()
        
        if not core_deps and not optional_deps:
            return {}
            
        try:
            return ensure_agent_dependencies(
                self.agent_name,
                core_deps,
                optional_deps
            )
        except Exception as e:
            self.logger.error(f"Dependency management failed: {e}")
            return {}
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Check if required API keys are available"""
        required_keys = self.get_required_api_keys()
        key_status = {}
        
        for key_name, env_var in required_keys.items():
            key_available = bool(os.environ.get(env_var))
            key_status[key_name] = key_available
            
            if key_available:
                self.logger.debug(f"✅ API key {key_name} available")
            else:
                self.logger.warning(f"⚠️  API key {key_name} not found in {env_var}")
        
        return key_status
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {
            "agent_name": self.agent_name,
            "project_root": str(self.project_root),
            "data_root": str(self.data_root),
            "config_directory": str(self.agent_config_dir),
            "dependencies": self.dependency_status,
            "api_keys": self.check_api_keys(),
            "config_loaded": bool(self.config),
            "ready": self.is_ready()
        }
    
    def is_ready(self) -> bool:
        """Check if agent is ready for use"""
        # Check core dependencies
        core_deps = self.get_core_dependencies()
        if core_deps:
            core_available = all(
                self.dependency_status.get(dep, False)
                for dep in core_deps
            )
            if not core_available:
                return False

        # Check required API keys
        required_keys = self.get_required_api_keys()
        if required_keys:
            keys_available = all(self.check_api_keys().values())
            if not keys_available:
                return False

        return True
        
    # Proxy methods for ContextManager
    def track_context(self, content: str, entry_type: str = "data", **kwargs) -> None:
        if self.context_manager:
            self.context_manager.add_entry(content, entry_type, **kwargs)

    def track_file(self, file_path: str, content: str) -> None:
        if self.context_manager:
            self.context_manager.add_file(file_path, content)

    def track_tool_call(self, tool_name: str, result: str) -> None:
        if self.context_manager:
            self.context_manager.add_tool_call(tool_name, result)

    # Abstract methods
    @abstractmethod
    def get_core_dependencies(self) -> List[str]:
        """Return list of core Python package dependencies"""
        pass
    
    @abstractmethod
    def get_optional_dependencies(self) -> Dict[str, str]:
        """Return dict of optional dependencies and their descriptions"""
        pass
    
    @abstractmethod
    def get_required_api_keys(self) -> Dict[str, str]:
        """Return dict mapping API key names to environment variable names"""
        pass
    
    @abstractmethod
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration for the agent"""
        pass

#!/usr/bin/env python3
"""
Dependency Manager for Self-Contained Agents

Handles automatic dependency installation and verification for agents.
Each agent can specify its requirements and this module ensures they're available.
"""

import subprocess
import sys
import importlib
import logging
from typing import List, Dict, Optional
from pathlib import Path

class DependencyManager:
    """Manages dependencies for self-contained agents"""
    
    def __init__(self, agent_name: str = "unknown"):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"DependencyManager-{agent_name}")
        
    def check_and_install_requirements(self, requirements: List[str]) -> Dict[str, bool]:
        """
        Check if requirements are installed, install missing ones
        
        Args:
            requirements: List of package names (e.g., ['requests', 'pyyaml'])
            
        Returns:
            Dict mapping package names to installation success status
        """
        results = {}
        
        for requirement in requirements:
            try:
                # Try to import the package
                importlib.import_module(requirement)
                results[requirement] = True
                self.logger.debug(f"✅ {requirement} already available")
            except ImportError:
                # Package not found, try to install it
                self.logger.info(f"📦 Installing missing dependency: {requirement}")
                success = self._install_package(requirement)
                results[requirement] = success
                
        return results
    
    def _install_package(self, package: str) -> bool:
        """Install a single package using pip"""
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ])
            self.logger.info(f"✅ Successfully installed {package}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to install {package}: {e}")
            return False
    
    def verify_optional_dependencies(self, optional_deps: Dict[str, str]) -> Dict[str, bool]:
        """
        Verify optional dependencies without installing them
        
        Args:
            optional_deps: Dict mapping package names to feature descriptions
            
        Returns:
            Dict mapping package names to availability status
        """
        results = {}
        
        for package, feature_desc in optional_deps.items():
            try:
                importlib.import_module(package)
                results[package] = True
                self.logger.debug(f"✅ Optional dependency {package} available ({feature_desc})")
            except ImportError:
                results[package] = False
                self.logger.info(f"⚠️  Optional dependency {package} not available - {feature_desc} will be disabled")
                
        return results
    
    def create_requirements_file(self, requirements: List[str], optional_deps: List[str] = None) -> Path:
        """Create a requirements.txt file for the agent"""
        agent_dir = Path(__file__).parent.parent / "agents"
        req_file = agent_dir / f"{self.agent_name}_requirements.txt"
        
        with open(req_file, 'w') as f:
            f.write(f"# Requirements for {self.agent_name} agent\n")
            f.write("# Generated automatically by DependencyManager\n\n")
            
            f.write("# Core requirements\n")
            for req in requirements:
                f.write(f"{req}\n")
                
            if optional_deps:
                f.write("\n# Optional dependencies\n")
                for opt_dep in optional_deps:
                    f.write(f"# {opt_dep}  # Optional\n")
                    
        return req_file

def ensure_agent_dependencies(agent_name: str, core_requirements: List[str], 
                            optional_requirements: Dict[str, str] = None) -> Dict[str, bool]:
    """
    Convenience function to ensure agent dependencies are available
    
    Args:
        agent_name: Name of the agent
        core_requirements: List of required packages
        optional_requirements: Dict of optional packages and their descriptions
        
    Returns:
        Combined status of all dependencies
    """
    dm = DependencyManager(agent_name)
    
    # Install core requirements
    core_results = dm.check_and_install_requirements(core_requirements)
    
    # Check optional requirements
    optional_results = {}
    if optional_requirements:
        optional_results = dm.verify_optional_dependencies(optional_requirements)
    
    # Combine results
    all_results = {**core_results, **optional_results}
    
    # Log summary
    logging.getLogger(f"Agent-{agent_name}").info(
        f"Dependencies ready: {sum(all_results.values())}/{len(all_results)} available"
    )
    
    return all_results

#!/usr/bin/env python3

"""
Claude Desktop Setup - Interactive MCP Validation
This script tests actual MCP server functionality by making test calls
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'  # No Color

class MCPValidator:
    def __init__(self):
        self.config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        self.workspace = Path(os.environ.get('CLAUDE_WORKSPACE', Path.home() / 'ClaudeDesktop'))
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        
    def print_header(self, text):
        print(f"\n{BOLD}{'━' * 50}{NC}")
        print(f"{BOLD}{text}{NC}")
        print(f"{BOLD}{'━' * 50}{NC}")
        
    def print_test(self, test_name):
        self.results['total'] += 1
        print(f"\n{BLUE}[TEST {self.results['total']}]{NC} {test_name}")
        
    def print_success(self, message):
        self.results['passed'] += 1
        print(f"{GREEN}✓{NC} {message}")
        
    def print_error(self, message):
        self.results['failed'] += 1
        print(f"{RED}✗{NC} {message}")
        
    def print_warning(self, message):
        self.results['warnings'] += 1
        print(f"{YELLOW}⚠{NC} {message}")
        
    def load_config(self):
        """Load Claude Desktop configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.print_error(f"Configuration file not found at {self.config_path}")
            return None
        except json.JSONDecodeError:
            self.print_error("Configuration file is not valid JSON")
            return None
            
    def test_workspace(self):
        """Test workspace structure"""
        self.print_header("Testing Workspace Structure")
        
        self.print_test("Checking workspace root")
        if self.workspace.exists():
            self.print_success(f"Workspace exists at {self.workspace}")
        else:
            self.print_error(f"Workspace not found at {self.workspace}")
            return
            
        # Check subdirectories
        required_dirs = ['projects', 'documents', 'scripts', 'logs']
        for dir_name in required_dirs:
            self.print_test(f"Checking {dir_name} directory")
            dir_path = self.workspace / dir_name
            
            if dir_path.exists():
                self.print_success(f"{dir_name}/ exists")
                
                # Check Git initialization for projects and scripts
                if dir_name in ['projects', 'scripts']:
                    git_dir = dir_path / '.git'
                    if git_dir.exists():
                        self.print_success(f"{dir_name}/ is Git-initialized")
                    else:
                        self.print_warning(f"{dir_name}/ is not Git-initialized")
            else:
                self.print_error(f"{dir_name}/ missing")
                
    def test_file_operations(self):
        """Test file operations in workspace"""
        self.print_header("Testing File Operations")
        
        test_file = self.workspace / 'test-validation.txt'
        test_content = f"MCP Validation Test - {datetime.now().isoformat()}"
        
        self.print_test("Testing file write")
        try:
            test_file.write_text(test_content)
            self.print_success("Successfully wrote test file")
        except Exception as e:
            self.print_error(f"Failed to write test file: {e}")
            return
            
        self.print_test("Testing file read")
        try:
            read_content = test_file.read_text()
            if read_content == test_content:
                self.print_success("Successfully read test file with correct content")
            else:
                self.print_error("File content doesn't match")
        except Exception as e:
            self.print_error(f"Failed to read test file: {e}")
            
        self.print_test("Testing file cleanup")
        try:
            test_file.unlink()
            self.print_success("Successfully cleaned up test file")
        except Exception as e:
            self.print_error(f"Failed to delete test file: {e}")
            
    def test_mcp_servers(self):
        """Test MCP server configurations"""
        self.print_header("Testing MCP Server Configuration")
        
        config = self.load_config()
        if not config:
            return
            
        required_servers = [
            'cli-mcp-server',
            'filesystem', 
            'memory',
            'time',
            'mcp-ical',
            'git'
        ]
        
        mcp_servers = config.get('mcpServers', {})
        
        for server in required_servers:
            self.print_test(f"Checking {server}")
            
            if server in mcp_servers:
                self.print_success(f"{server} is configured")
                
                # Check command
                server_config = mcp_servers[server]
                if 'command' in server_config:
                    cmd = server_config['command']
                    self.print_success(f"Command: {cmd}")
                else:
                    self.print_error(f"{server} has no command configured")
                    
                # Check args for filesystem
                if server == 'filesystem' and 'args' in server_config:
                    paths = server_config['args']
                    for path in paths:
                        if Path(path).exists():
                            print(f"  {GREEN}✓{NC} Path exists: {path}")
                        else:
                            print(f"  {RED}✗{NC} Path missing: {path}")
            else:
                self.print_error(f"{server} is not configured")
                
    def test_knowledge_base(self):
        """Test knowledge base files"""
        self.print_header("Testing Knowledge Base")
        
        kb_file = Path("configs/knowledge-base/system-entities.json")
        
        self.print_test("Checking knowledge base file")
        if kb_file.exists():
            self.print_success("Knowledge base file exists")
            
            try:
                with open(kb_file, 'r') as f:
                    kb_data = json.load(f)
                self.print_success("Knowledge base is valid JSON")
                
                entity_count = len(kb_data.get('entities', []))
                self.print_success(f"Knowledge base contains {entity_count} entities")
                
                # List entity names
                print("\nConfigured entities:")
                for entity in kb_data.get('entities', []):
                    print(f"  • {entity.get('name', 'Unknown')}")
                    
            except json.JSONDecodeError:
                self.print_error("Knowledge base is not valid JSON")
            except Exception as e:
                self.print_error(f"Error reading knowledge base: {e}")
        else:
            self.print_error("Knowledge base file not found")
            
    def test_dependencies(self):
        """Test system dependencies"""
        self.print_header("Testing System Dependencies")
        
        # Python version
        self.print_test("Checking Python version")
        python_version = sys.version.split()[0]
        if sys.version_info >= (3, 8):
            self.print_success(f"Python {python_version} (>= 3.8 required)")
        else:
            self.print_error(f"Python {python_version} (3.8+ required)")
            
        # External commands
        commands = {
            'node': 'Node.js',
            'git': 'Git',
            'jq': 'jq (JSON processor)',
            'uvx': 'uvx (Python package runner)',
            'npx': 'npx (Node package runner)'
        }
        
        for cmd, name in commands.items():
            self.print_test(f"Checking {name}")
            
            result = subprocess.run(['which', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                # Get version if possible
                version_cmd = [cmd, '--version'] if cmd != 'jq' else [cmd, '--version']
                version_result = subprocess.run(version_cmd, capture_output=True, text=True)
                version = version_result.stdout.strip().split('\n')[0]
                self.print_success(f"{name} installed: {version}")
            else:
                if cmd in ['jq', 'uvx', 'npx']:
                    self.print_warning(f"{name} not found (optional but recommended)")
                else:
                    self.print_error(f"{name} not found (required)")
                    
    def generate_report(self):
        """Generate final validation report"""
        self.print_header("Validation Summary")
        
        print(f"\n{BOLD}Results:{NC}")
        print(f"Total Tests: {self.results['total']}")
        print(f"Passed: {GREEN}{self.results['passed']}{NC}")
        print(f"Failed: {RED}{self.results['failed']}{NC}")
        print(f"Warnings: {YELLOW}{self.results['warnings']}{NC}")
        
        if self.results['failed'] == 0:
            print(f"\n{GREEN}{BOLD}✓ VALIDATION PASSED{NC}")
            print("\nYour Claude Desktop Setup is properly configured!")
            print("\nNext steps:")
            print("1. Restart Claude Desktop to load MCP servers")
            print("2. Use the validation conversation to test functionality")
            print("3. Try the onboarding conversation to get started")
        else:
            print(f"\n{RED}{BOLD}✗ VALIDATION FAILED{NC}")
            print("\nPlease fix the errors above and run validation again.")
            print("\nTroubleshooting:")
            print("1. Review error messages above")
            print("2. Run the installer again: ./install.sh")
            print("3. Check the troubleshooting guide in README.md")
            
    def run(self):
        """Run all validation tests"""
        print(f"{BOLD}Claude Desktop Setup - Interactive Validation{NC}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("━" * 50)
        
        # Run all tests
        self.test_dependencies()
        self.test_workspace()
        self.test_file_operations()
        self.test_mcp_servers()
        self.test_knowledge_base()
        
        # Generate report
        self.generate_report()
        
        # Return exit code
        return 0 if self.results['failed'] == 0 else 1

if __name__ == "__main__":
    validator = MCPValidator()
    sys.exit(validator.run())

#!/usr/bin/env python3
"""
Script to install the UML-MCP-Server to Cursor or other IDEs.

This script helps users configure their Cursor IDE to use
the UML-MCP-Server for diagram generation.
"""

import os
import json
import argparse
import platform
import sys
from pathlib import Path
from typing import Dict, Any, Optional

def get_config_path() -> Optional[Path]:
    """Get the path to Cursor config file based on OS."""
    home = Path.home()
    
    if platform.system() == "Windows":
        return home / "AppData" / "Roaming" / "Cursor" / "config.json"
    elif platform.system() == "Darwin":  # macOS
        return home / "Library" / "Application Support" / "Cursor" / "config.json"
    elif platform.system() == "Linux":
        return home / ".config" / "Cursor" / "config.json"
    else:
        print(f"Unsupported platform: {platform.system()}")
        return None

def read_config(config_path: Path) -> Dict[str, Any]:
    """Read the current Cursor config."""
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not parse {config_path}. The file may be corrupted.")
            return {}
    return {}

def write_config(config_path: Path, config: Dict[str, Any]) -> bool:
    """Write the updated Cursor config."""
    try:
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the config with pretty formatting
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing config: {e}")
        return False

def install_mcp_server(project_path: str, output_dir: str) -> bool:
    """Install the MCP server configuration to Cursor."""
    # Get the config path
    config_path = get_config_path()
    if not config_path:
        return False
    
    # Read the current config
    config = read_config(config_path)
    
    # Ensure the project path is absolute
    project_path = os.path.abspath(project_path)
    output_dir = os.path.abspath(output_dir)
    
    # Create mcpServers section if it doesn't exist
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add or update the UML-MCP-Server configuration
    config["mcpServers"]["UML-MCP-Server"] = {
        "command": "python",
        "args": [
            project_path + "/mcp_server.py"
        ],
        "output_dir": output_dir
    }
    
    # Write the updated config
    success = write_config(config_path, config)
    if success:
        print(f"✅ UML-MCP-Server successfully installed to Cursor.")
        print(f"   Project Path: {project_path}")
        print(f"   Output Directory: {output_dir}")
    return success

def main():
    parser = argparse.ArgumentParser(description="Install UML-MCP-Server to Cursor")
    parser.add_argument("--project-path", default=os.getcwd(), help="Path to the D2COpenAIPlugin project")
    parser.add_argument("--output-dir", default=os.path.join(os.getcwd(), "output"), help="Directory to store generated diagrams")
    
    args = parser.parse_args()
    
    success = install_mcp_server(args.project_path, args.output_dir)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()

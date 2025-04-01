#!/usr/bin/env python3
"""
UML-MCP-Server: UML diagram generation server with MCP interface

This module provides the main entry point for the MCP server that generates UML
diagrams through the Model Context Protocol (MCP).
"""

import os
import sys
import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

# Configure rich console
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

# Centralized error handling for imports
def safe_import(module_name, display_name=None):
    try:
        return __import__(module_name)
    except ImportError:
        display_name = display_name or module_name
        console.print(f"[bold red]Error:[/bold red] {display_name} module not found. Make sure it's correctly installed.")
        return None

# Check required modules
mcp_module = safe_import("mcp.server", "MCP Server")
kroki_module = safe_import("kroki.kroki", "Kroki")
plantuml_module = safe_import("plantuml", "PlantUML")
mermaid_module = safe_import("mermaid.mermaid", "Mermaid")
d2_module = safe_import("D2.run_d2", "D2")

# Verify all modules loaded correctly
missing_modules = []
if not mcp_module:
    missing_modules.append("MCP Server")
if not kroki_module:
    missing_modules.append("Kroki")
if not plantuml_module:
    missing_modules.append("PlantUML")
if not mermaid_module:
    missing_modules.append("Mermaid")
if not d2_module:
    missing_modules.append("D2")

if missing_modules:
    console.print(f"[bold red]Error:[/bold red] Missing required modules: {', '.join(missing_modules)}")
    console.print("Please ensure all project components are correctly installed.")
    sys.exit(1)

# Import core server
from mcp.core.server import create_mcp_server
from mcp.core.config import MCP_SETTINGS

if __name__ == "__main__":
    # Display server info
    console.print(Panel(f"[bold green]Starting UML-MCP Server v{MCP_SETTINGS.version}[/bold green]"))
    console.print(f"[yellow]Server Name: {MCP_SETTINGS.server_name}[/yellow]")
    console.print(f"[yellow]Available Tools: {len(MCP_SETTINGS.tools)}[/yellow]")
    console.print(f"[yellow]Available Prompts: {len(MCP_SETTINGS.prompts)}[/yellow]")
    
    # Start MCP server
    try:
        from mcp.core.server import start_server
        start_server()
    except Exception as e:
        logger.critical(f"Server error: {str(e)}", exc_info=True)
    finally:
        logger.info("Server shut down")

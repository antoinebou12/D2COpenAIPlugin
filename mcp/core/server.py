"""
Core MCP server implementation
"""

import os
import logging
import json
import datetime
from typing import Dict, Optional, Any

# Import MCP server framework - try to use the wrapper
try:
    from ..server.fastmcp_wrapper import FastMCP, Context
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP, Context
    except ImportError:
        from fastmcp import FastMCP, Context

# Import configuration
from .config import MCP_SETTINGS
from .utils import setup_logging

# Import tools and resources
from ..tools.diagram_tools import register_diagram_tools
from ..resources.diagram_resources import register_diagram_resources
from ..prompts.diagram_prompts import register_diagram_prompts

# Get logger
logger = logging.getLogger(__name__)

def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools and resources.
    
    Returns:
        Configured FastMCP server instance
    """
    # Initialize MCP server
    logger.info(f"Creating MCP server: {MCP_SETTINGS.server_name}")
    server = FastMCP(MCP_SETTINGS.server_name)
    
    # Register all tools, resources, and prompts
    register_diagram_tools(server)
    register_diagram_resources(server)
    register_diagram_prompts(server)
    
    # Update settings with registered tools and prompts
    MCP_SETTINGS.tools = [name for name, _ in server._tools.items()]
    MCP_SETTINGS.prompts = [name for name, _ in server._prompts.items()]
    
    logger.info(f"MCP server created with {len(MCP_SETTINGS.tools)} tools and {len(MCP_SETTINGS.prompts)} prompts")
    return server

# Create a singleton MCP server instance
_mcp_server = None

def get_mcp_server() -> FastMCP:
    """Get the singleton MCP server instance.
    
    Returns:
        FastMCP server instance
    """
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = create_mcp_server()
    return _mcp_server

def start_server():
    """Start the MCP server"""
    # Get the server
    server = get_mcp_server()
    
    # Start the server
    logger.info("Starting MCP server")
    server.run(transport='stdio')

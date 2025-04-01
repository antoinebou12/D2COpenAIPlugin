"""
MCP tools for diagram generation
"""

import logging
import json
import os
from typing import Dict, Any

from mcp.server.fastmcp import FastMCP
from ..core.utils import generate_diagram
from ..core.config import MCP_SETTINGS

logger = logging.getLogger(__name__)

def register_diagram_tools(server: FastMCP):
    """
    Register all diagram generation tools with the MCP server
    
    Args:
        server: The MCP server instance
    """
    logger.info("Registering diagram tools")
    
    @server.tool()
    def generate_uml(diagram_type: str, code: str, output_dir: str) -> str:
        """Generate a UML diagram using the specified diagram type.
        
        Args:
            diagram_type: Type of diagram (class, sequence, activity, etc.)
            code: The diagram code/description
            output_dir: Directory where to save the generated image
        
        Returns:
            JSON string containing code, URL, and local file path
        """
        logger.info(f"Called generate_uml tool: type={diagram_type}, code length={len(code)}")
        
        # Validate diagram type
        if diagram_type.lower() not in MCP_SETTINGS.diagram_types:
            error_msg = f"Unsupported diagram type: {diagram_type}. Supported types: {', '.join(MCP_SETTINGS.diagram_types.keys())}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
        
        # Generate diagram
        result = generate_diagram(diagram_type, code, "png", output_dir)
        
        # Return JSON string
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    # Register individual diagram type tools
    for diagram_type in ["class", "sequence", "activity", "usecase", "state", "component", "deployment", "object"]:
        register_specific_diagram_tool(server, diagram_type)
    
    # Register other diagram tools
    register_mermaid_tool(server)
    register_d2_tool(server)
    register_graphviz_tool(server)

def register_specific_diagram_tool(server: FastMCP, diagram_type: str):
    """
    Register a tool for a specific diagram type
    
    Args:
        server: The MCP server instance
        diagram_type: The diagram type to register
    """
    
    @server.tool()
    def tool_function(code: str, output_dir: str) -> str:
        """Generate a specific diagram type and return code, URL and local path.
        
        Args:
            code: The diagram code
            output_dir: Directory where to save the generated image
        
        Returns:
            JSON string containing code, URL, and local file path
        """
        logger.info(f"Called generate_{diagram_type}_diagram tool: code length={len(code)}")
        return generate_uml(diagram_type, code, output_dir)
    
    # Dynamically set the function name and docstring
    tool_function.__name__ = f"generate_{diagram_type}_diagram"
    tool_function.__doc__ = f"""Generate a {diagram_type} diagram and return code, URL and local path.
        
        Args:
            code: The PlantUML {diagram_type} diagram code
            output_dir: Directory where to save the generated image
        
        Returns:
            JSON string containing code, URL, and local file path
        """
    
    # Register the tool with the server
    setattr(server, f"generate_{diagram_type}_diagram", tool_function)
    logger.debug(f"Registered tool: generate_{diagram_type}_diagram")

def register_mermaid_tool(server: FastMCP):
    """
    Register Mermaid diagram tool
    
    Args:
        server: The MCP server instance
    """
    @server.tool()
    def generate_mermaid_diagram(code: str, output_dir: str) -> str:
        """Generate a Mermaid diagram and return code, URL and local path.
        
        Args:
            code: The Mermaid diagram code
            output_dir: Directory where to save the generated image
        
        Returns:
            JSON string containing code, URL, playground link, and local file path
        """
        logger.info(f"Called generate_mermaid_diagram tool: code length={len(code)}")
        return generate_uml("mermaid", code, output_dir)

def register_d2_tool(server: FastMCP):
    """
    Register D2 diagram tool
    
    Args:
        server: The MCP server instance
    """
    @server.tool()
    def generate_d2_diagram(code: str, output_dir: str) -> str:
        """Generate a D2 diagram and return code, URL and local path.
        
        Args:
            code: The D2 diagram code
            output_dir: Directory where to save the generated image
        
        Returns:
            JSON string containing code, URL, playground link, and local file path
        """
        logger.info(f"Called generate_d2_diagram tool: code length={len(code)}")
        return generate_uml("d2", code, output_dir)

def register_graphviz_tool(server: FastMCP):
    """
    Register Graphviz diagram tool
    
    Args:
        server: The MCP server instance
    """
    @server.tool()
    def generate_graphviz_diagram(code: str, output_dir: str) -> str:
        """Generate a Graphviz diagram and return code, URL and local path.
        
        Args:
            code: The Graphviz (DOT) diagram code
            output_dir: Directory where to save the generated image
        
        Returns:
            JSON string containing code, URL, playground link, and local file path
        """
        logger.info(f"Called generate_graphviz_diagram tool: code length={len(code)}")
        return generate_uml("graphviz", code, output_dir)

def register_erd_tool(server: FastMCP):
    """
    Register ERD diagram tool
    
    Args:
        server: The MCP server instance
    """
    @server.tool()
    def generate_erd_diagram(code: str, output_dir: str) -> str:
        """Generate an Entity-Relationship diagram and return code, URL and local path.
        
        Args:
            code: The ERD diagram code
            output_dir: Directory where to save the generated image
        
        Returns:
            JSON string containing code, URL, and local file path
        """
        logger.info(f"Called generate_erd_diagram tool: code length={len(code)}")
        return generate_uml("erd", code, output_dir)

"""
MCP resources for diagram information
"""

import logging
import json
from typing import Dict, List, Any

from mcp.server.fastmcp import FastMCP
from ..core.config import MCP_SETTINGS
from kroki.kroki_templates import DiagramTemplates, DiagramExamples

logger = logging.getLogger(__name__)

def register_diagram_resources(server: FastMCP):
    """
    Register diagram resources with the MCP server
    
    Args:
        server: The MCP server instance
    """
    logger.info("Registering diagram resources")
    
    @server.resource("uml://types")
    def get_diagram_types() -> str:
        """Get a list of supported diagram types.
        
        Returns:
            JSON string containing supported diagram types and their descriptions
        """
        logger.info("Getting diagram types list")
        
        # Prepare descriptions
        descriptions = {
            diagram_type: config.description
            for diagram_type, config in MCP_SETTINGS.diagram_types.items()
        }
        
        # Return as JSON
        return json.dumps({
            "types": list(MCP_SETTINGS.diagram_types.keys()),
            "descriptions": descriptions
        }, ensure_ascii=False, indent=2)
    
    @server.resource("uml://templates")
    def get_diagram_templates() -> str:
        """Get templates for various diagram types.
        
        Returns:
            JSON string containing templates for different diagram types
        """
        logger.info("Getting diagram templates")
        
        templates = {}
        for diagram_type, config in MCP_SETTINGS.diagram_types.items():
            try:
                # Try to get template from kroki_templates
                templates[diagram_type] = DiagramTemplates.get_template(config.backend)
            except Exception:
                # If no template found, create a basic one
                if config.backend == "plantuml":
                    templates[diagram_type] = f"@startuml\n' {diagram_type.capitalize()} diagram template\n@enduml"
                elif config.backend == "mermaid":
                    templates[diagram_type] = "graph TD\n    A[Start] --> B[End]"
                elif config.backend == "d2":
                    templates[diagram_type] = "x -> y"
                else:
                    templates[diagram_type] = f"# {diagram_type.capitalize()} template"
        
        return json.dumps(templates, ensure_ascii=False, indent=2)
    
    @server.resource("uml://examples")
    def get_diagram_examples() -> str:
        """Get examples for various diagram types.
        
        Returns:
            JSON string containing examples for different diagram types
        """
        logger.info("Getting diagram examples")
        
        examples = {}
        for diagram_type, config in MCP_SETTINGS.diagram_types.items():
            try:
                # Try to get example from kroki_examples
                examples[diagram_type] = DiagramExamples.get_example(config.backend)
            except Exception:
                # If no example found, leave empty
                examples[diagram_type] = ""
        
        return json.dumps(examples, ensure_ascii=False, indent=2)
    
    @server.resource("uml://formats")
    def get_output_formats() -> str:
        """Get supported output formats for each diagram type.
        
        Returns:
            JSON string containing supported output formats
        """
        logger.info("Getting output formats")
        
        formats = {
            diagram_type: config.formats
            for diagram_type, config in MCP_SETTINGS.diagram_types.items()
        }
        
        return json.dumps(formats, ensure_ascii=False, indent=2)
    
    @server.resource("uml://server-info")
    def get_server_info() -> str:
        """Get information about the server.
        
        Returns:
            JSON string containing server information
        """
        logger.info("Getting server info")
        
        info = {
            "name": MCP_SETTINGS.server_name,
            "version": MCP_SETTINGS.version,
            "description": MCP_SETTINGS.description,
            "tools": MCP_SETTINGS.tools,
            "prompts": MCP_SETTINGS.prompts,
            "supported_diagrams": list(MCP_SETTINGS.diagram_types.keys()),
            "output_dir": MCP_SETTINGS.output_dir
        }
        
        return json.dumps(info, ensure_ascii=False, indent=2)

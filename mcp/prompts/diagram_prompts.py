"""
MCP prompts templates for diagram generation
"""

import logging
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_diagram_prompts(server: FastMCP):
    """
    Register diagram prompts with the MCP server
    
    Args:
        server: The MCP server instance
    """
    logger.info("Registering diagram prompts")
    
    @server.prompt()
    def create_class_diagram() -> str:
        """Prompt template for creating a class diagram."""
        logger.info("Using class diagram prompt template")
        return """
Please help me create a class diagram using PlantUML. Include:

1. Classes with attributes and methods
2. Relationships between classes (association, inheritance, composition)
3. Access modifiers for attributes and methods (+public, -private, #protected)

Example:

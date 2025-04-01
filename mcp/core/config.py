"""
Configuration settings for MCP server
"""

import os
from typing import Dict, List
from pydantic import BaseModel

class DiagramType(BaseModel):
    """Configuration for a diagram type"""
    backend: str
    description: str
    formats: List[str] = ["png", "svg"]
    
class MCPSettings(BaseModel):
    """Configuration settings for MCP server"""
    server_name: str = "UML Diagram Generator"
    version: str = "1.2.0"
    description: str = "Generate UML and other diagrams through MCP"
    output_dir: str = os.environ.get("MCP_OUTPUT_DIR", os.path.join(os.getcwd(), "output"))
    tools: List[str] = []
    prompts: List[str] = []
    diagram_types: Dict[str, DiagramType] = {}
    plantuml_server: str = os.environ.get("PLANTUML_SERVER", "http://plantuml-server:8080")
    kroki_server: str = os.environ.get("KROKI_SERVER", "https://kroki.io")

# Define supported diagram types with their backends
DIAGRAM_TYPES = {
    # UML diagram types (PlantUML)
    "class": DiagramType(
        backend="plantuml",
        description="Shows classes, attributes, methods and relationships between classes"
    ),
    "sequence": DiagramType(
        backend="plantuml", 
        description="Shows object interactions arranged in time sequence"
    ),
    "activity": DiagramType(
        backend="plantuml",
        description="Shows workflows or business processes"
    ),
    "usecase": DiagramType(
        backend="plantuml",
        description="Shows system functionality and actors who interact with it" 
    ),
    "state": DiagramType(
        backend="plantuml",
        description="Shows states of an object during its lifecycle"
    ),
    "component": DiagramType(
        backend="plantuml",
        description="Shows components and dependencies"
    ),
    "deployment": DiagramType(
        backend="plantuml",
        description="Shows physical architecture of a system"
    ),
    "object": DiagramType(
        backend="plantuml",
        description="Shows instances of classes and their relationships"
    ),
    
    # Other diagram types
    "mermaid": DiagramType(
        backend="mermaid",
        description="A JavaScript based diagramming and charting tool"
    ),
    "d2": DiagramType(
        backend="d2",
        description="A modern diagram scripting language"
    ),
    "graphviz": DiagramType(
        backend="graphviz",
        description="Graph visualization software"
    ),
    "erd": DiagramType(
        backend="erd",
        description="Entity-relationship diagrams"
    ),
    "blockdiag": DiagramType(
        backend="blockdiag",
        description="Simple block diagram images"
    ),
    "bpmn": DiagramType(
        backend="bpmn",
        description="Business Process Model and Notation"
    ),
    "c4plantuml": DiagramType(
        backend="c4plantuml",
        description="C4 model diagrams using PlantUML"
    )
}

# Create MCP settings
MCP_SETTINGS = MCPSettings(
    diagram_types=DIAGRAM_TYPES
)

# Configure local Kroki server if available
if os.environ.get("USE_LOCAL_KROKI", "false").lower() == "true":
    MCP_SETTINGS.kroki_server = os.environ.get("KROKI_SERVER", "http://kroki:8000")

# Configure local PlantUML server if available
if os.environ.get("USE_LOCAL_PLANTUML", "false").lower() == "true":
    MCP_SETTINGS.plantuml_server = os.environ.get("PLANTUML_SERVER", "http://plantuml-server:8080")

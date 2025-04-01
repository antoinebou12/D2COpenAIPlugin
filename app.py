"""
Diagram2Code OpenAI Plugin API server.

This module provides a FastAPI server that generates diagrams from text
descriptions through a REST API compatible with the OpenAI plugin system.
"""

import logging
import os
import sys
from typing import Dict, Optional, List

# Import error handling for dependencies
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, field_validator
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.panel import Panel
except ImportError as e:
    print(f"Error: Required dependency not found: {e}")
    print("Please install missing dependencies with: pip install fastapi uvicorn pydantic rich")
    sys.exit(1)

# Centralized error handling for internal imports
def safe_import(module_name, display_name=None):
    try:
        return __import__(module_name)
    except ImportError:
        display_name = display_name or module_name
        print(f"Error: {display_name} module not found. Make sure it's correctly installed.")
        return None

# Internal imports with error handling
d2_module = safe_import("D2.run_d2", "D2")
plantuml_module = safe_import("plantuml", "PlantUML")
mermaid_module = safe_import("mermaid.mermaid", "Mermaid")
kroki_module = safe_import("kroki.kroki", "Kroki")

# Verify all modules loaded correctly
missing_modules = []
if not d2_module:
    missing_modules.append("D2")
if not plantuml_module:
    missing_modules.append("PlantUML") 
if not mermaid_module:
    missing_modules.append("Mermaid")
if not kroki_module:
    missing_modules.append("Kroki")

if missing_modules:
    print(f"Error: Missing required internal modules: {', '.join(missing_modules)}")
    print("Please ensure all project components are correctly installed.")
    sys.exit(1)

# Now import the specific components safely
from D2.run_d2 import run_go_script
from plantuml import PlantUML
from mermaid.mermaid import generate_diagram_state, generate_mermaid_live_editor_url
from kroki.kroki import generate_diagram as generate_kroki_diagram, LANGUAGE_OUTPUT_SUPPORT as KROKI_LANGUAGE_SUPPORT

# Configure rich console and logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Diagram2Code Plugin",
    description="Generate diagrams from text descriptions using various diagram languages",
    version="1.2.0",
    docs_url="/",
    redoc_url=None,
    servers=[
        {"url": "https://openai-uml-plugin.vercel.app"}, 
        {"url": "http://localhost:5003"}
    ],
)

# Mount static files for OpenAI plugin manifest
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

# Configure CORS
ALLOWED_ORIGINS = [
    "https://chat.openai.com",
    "https://openai-uml-plugin.vercel.app",
    "http://localhost:5003",
    "http://127.0.0.1:5003",
    "http://0.0.0.0:5003",
    "devtools"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Define valid languages and types
VALID_LANGUAGES = [
    "plantuml", "mermaid", "mermaidjs", "d2lang", "D2", "d2", "terrastruct", "graphviz",
    # Kroki supported diagram types
    "blockdiag", "bpmn", "bytefield", "seqdiag", "actdiag", "nwdiag", 
    "packetdiag", "rackdiag", "c4plantuml", "dbml", "ditaa", "erd", 
    "excalidraw", "nomnoml", "pikchr", "structurizr", "svgbob", 
    "symbolator", "tikz", "umlet", "vega", "vegalite", "wavedrom", "wireviz"
]

VALID_TYPES = [
    "class", "sequence", "activity", "component", "state", "object", 
    "usecase", "mindmap", "git"
]

# Define request model
class DiagramRequest(BaseModel):
    """Request model for diagram generation."""
    lang: str
    type: str
    code: str
    theme: str = ""

    # Update to Pydantic v2 style validators
    @field_validator('lang')
    @classmethod
    def validate_lang(cls, v: str) -> str:
        if v not in VALID_LANGUAGES:
            # Use ValueError instead of ValidationError for compatibility
            raise ValueError(f"Invalid diagram language: {v}")
        return v

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            logger.error(f"Invalid diagram type: {v}")
        return v

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        if len(v) > 100000:
            raise ValueError("Diagram code is too long.")
        return v

# API endpoints
@app.post("/generate_diagram")
async def generate_diagram_endpoint(diagram: DiagramRequest) -> Dict[str, str]:
    """
    Generate a diagram from text description.
    
    Args:
        diagram: The diagram request containing language, type, code and optional theme
        
    Returns:
        Dictionary with URL to the generated diagram, the content, and playground URL
        
    Raises:
        HTTPException: If there was an error generating the diagram
    """
    logger.info(f"Generating {diagram.lang} diagram of type {diagram.type}")
    
    # Validate input
    if not diagram.code:
        raise HTTPException(status_code=422, detail="No diagram code provided")
    if not diagram.lang:
        raise HTTPException(status_code=422, detail="No diagram language provided")
    if not diagram.type:
        raise HTTPException(status_code=422, detail="No diagram type provided")
    
    try:
        # Process based on diagram language
        if diagram.lang in ["plantuml"]:
            theme = diagram.theme or "blueprint"
            logger.info("Generating PlantUML diagram")
            
            plantuml = PlantUML(url="https://www.plantuml.com/plantuml/dpng")
            url, content, playground = plantuml.generate_image_from_string(str(diagram.code))
            
            if url is None:
                raise HTTPException(status_code=400, detail="Invalid PlantUML syntax")
                
            return {"url": url, "content": content, "playground": playground}
            
        elif diagram.lang in ["mermaid", "mermaidjs"]:
            theme = diagram.theme or "dark"
            logger.info("Generating Mermaid diagram")
            
            diagram_state = generate_diagram_state(str(diagram.code), theme)
            url, content, playground = generate_mermaid_live_editor_url(diagram_state)
            
            if url is None:
                raise HTTPException(status_code=400, detail="Invalid Mermaid syntax")
                
            return {"url": url, "content": content, "playground": playground}
            
        elif diagram.lang in ["d2lang", "D2", "d2", "terrastruct"]:
            theme = diagram.theme or "Neutral default"
            logger.info("Generating D2 diagram")
            
            url, content, playground = await run_go_script(str(diagram.code))
            return {"url": url, "content": content, "playground": playground}
            
        elif diagram.lang in KROKI_LANGUAGE_SUPPORT:
            logger.info(f"Generating Kroki diagram ({diagram.lang})")
            
            url, content, playground = await generate_kroki_diagram(diagram.lang, str(diagram.code), "svg")
            return {"url": url, "content": content, "playground": playground}
            
        else:
            raise HTTPException(status_code=422, detail=f"Unknown diagram type: {diagram.lang}")
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating {diagram.lang} diagram: {str(e)}")
        return {"error": f"An error occurred while generating the diagram: {str(e)}"}

# OpenAI Plugin API endpoints
@app.get("/logo.png")
def plugin_logo():
    """Return the plugin logo."""
    logger.info("Returning plugin logo")
    return FileResponse("./.well-known/logo.png", media_type="image/png")

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    """Return the plugin manifest for OpenAI."""
    logger.info("Returning plugin manifest")
    with open("./.well-known/ai-plugin.json") as f:
        return JSONResponse(content=f.read(), media_type="text/json")

@app.get("/openapi.yaml", response_class=PlainTextResponse)
async def openapi_spec():
    """Return the OpenAPI specification in YAML format."""
    logger.info("Returning OpenAPI specification (YAML)")
    with open("./.well-known/openapi.yaml") as f:
        return f.read()

@app.get("/openapi.json", response_class=PlainTextResponse)
async def openapi_spec_json():
    """Return the OpenAPI specification in JSON format."""
    logger.info("Returning OpenAPI specification (JSON)")
    with open("./.well-known/openapi.json") as f:
        return f.read()

@app.get("/.well-known/privacy.txt", response_class=PlainTextResponse)
async def privacy_policy():
    """Return the privacy policy."""
    logger.info("Returning privacy policy")
    return FileResponse("./.well-known/privacy.txt")

def start_server(host: str = "localhost", port: int = 5003):
    """
    Start the FastAPI server with the given host and port.
    
    Args:
        host: The host to bind to
        port: The port to listen on
    """
    import uvicorn
    
    console.print(Panel(f"[bold green]Starting Diagram2Code Server v1.2.0[/bold green]"))
    console.print(f"[yellow]API endpoints available at http://{host}:{port}[/yellow]")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()

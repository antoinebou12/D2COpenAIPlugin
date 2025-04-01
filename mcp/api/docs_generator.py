"""
Documentation generator for MCP server
"""

import json
import os
import logging
from typing import Dict, List, Any

from ..core.config import MCP_SETTINGS

logger = logging.getLogger(__name__)

def generate_api_docs() -> Dict[str, Any]:
    """
    Generate API documentation in OpenAPI format
    
    Returns:
        Dictionary containing OpenAPI specification
    """
    logger.info("Generating API documentation")
    
    # Base OpenAPI structure
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": MCP_SETTINGS.server_name,
            "description": MCP_SETTINGS.description,
            "version": MCP_SETTINGS.version
        },
        "paths": {},
        "components": {
            "schemas": {}
        }
    }
    
    # Add tools as paths
    for tool_name in MCP_SETTINGS.tools:
        # Convert tool_name to path format
        path = f"/{tool_name.replace('_', '-')}"
        
        openapi_spec["paths"][path] = {
            "post": {
                "summary": f"Execute {tool_name}",
                "description": f"Tool to {' '.join(tool_name.split('_'))}",
                "operationId": tool_name,
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{tool_name}Request"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{tool_name}Response"
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Add request schema
        openapi_spec["components"]["schemas"][f"{tool_name}Request"] = {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Diagram code"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory path"
                }
            },
            "required": ["code", "output_dir"]
        }
        
        # Add response schema
        openapi_spec["components"]["schemas"][f"{tool_name}Response"] = {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Original diagram code"
                },
                "url": {
                    "type": "string",
                    "description": "URL to the generated diagram"
                },
                "playground": {
                    "type": "string",
                    "description": "URL to interactive playground"
                },
                "local_path": {
                    "type": "string",
                    "description": "Local file path to the saved diagram"
                }
            }
        }
    
    # Add resources
    for resource_path in ["uml://types", "uml://templates", "uml://examples", "uml://formats", "uml://server-info"]:
        # Convert resource path to OpenAPI path
        path = f"/resources/{resource_path.replace('://', '-')}"
        
        openapi_spec["paths"][path] = {
            "get": {
                "summary": f"Get {resource_path}",
                "description": f"Resource for {resource_path}",
                "operationId": resource_path.replace("://", "_").replace("/", "_"),
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
            }
        }
    
    logger.info("API documentation generated")
    return openapi_spec

def save_api_docs(output_dir: str = "docs") -> str:
    """
    Generate and save API documentation
    
    Args:
        output_dir: Directory to save the documentation
        
    Returns:
        Path to the saved documentation file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate docs
    docs = generate_api_docs()
    
    # Save as JSON
    json_path = os.path.join(output_dir, "openapi.json")
    with open(json_path, "w") as f:
        json.dump(docs, f, indent=2)
    
    logger.info(f"API documentation saved to {json_path}")
    return json_path

"""Translate the HTTP contract to UML-MCP's generate_uml tool."""

import json
import os

import anyio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

DEFAULT_UML_MCP_URL = "https://uml-mcp.antoineboucher.info/mcp"


def backend_url() -> str:
    """An empty environment value selects the original direct renderers."""
    return os.getenv("UML_MCP_URL", DEFAULT_UML_MCP_URL)


async def generate_with_uml_mcp(lang: str, diagram_type: str, code: str, theme: str) -> dict:
    # UML-MCP uses PlantUML type keys and language keys for other renderers.
    kind = diagram_type if lang == "plantuml" else lang
    arguments = {"diagram_type": kind, "code": code, "output_format": "svg"}
    if theme:
        arguments["theme"] = theme
    with anyio.fail_after(30):
        async with streamable_http_client(backend_url()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("generate_uml", arguments)
    if result.is_error:
        raise ValueError("UML-MCP rejected diagram generation")
    payload = result.structured_content
    if not payload:
        for block in result.content:
            if block.type == "text":
                try:
                    payload = json.loads(block.text)
                except (ValueError, TypeError):
                    continue
                if isinstance(payload, dict):
                    break
    if not isinstance(payload, dict) or payload.get("error") or not payload.get("url"):
        raise ValueError("UML-MCP returned no diagram URL")
    return {"url": payload["url"], "content": code, "playground": payload.get("playground") or ""}

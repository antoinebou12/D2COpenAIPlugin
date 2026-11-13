"""Diagram2Code HTTP Actions API and Streamable HTTP MCP server."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

import anyio
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field, field_validator

from kroki.kroki import LANGUAGE_OUTPUT_SUPPORT
from kroki.kroki import generate_diagram as generate_kroki_diagram
from mermaid.mermaid import generate_diagram_state, generate_mermaid_live_editor_url
from plantuml import PlantUML, PlantUMLHTTPError
from uml_backend import backend_url, generate_with_uml_mcp

ROOT = Path(__file__).resolve().parent
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://openai-uml-plugin.vercel.app")
MCP_HOSTS = [
    "localhost",
    "localhost:*",
    "127.0.0.1",
    "127.0.0.1:*",
    urlsplit(PUBLIC_BASE_URL).netloc,
]
MCP_HOSTS.extend(
    filter(None, [os.getenv("VERCEL_URL"), os.getenv("VERCEL_PROJECT_PRODUCTION_URL")])
)
logger = logging.getLogger(__name__)
ALIASES = {"mermaidjs": "mermaid", "d2lang": "d2", "terrastruct": "d2"}
mcp = MCPServer("Diagram2Code", instructions="Generate diagram links from source text.")
mcp_app = mcp.streamable_http_app(
    streamable_http_path="/",
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        allowed_hosts=MCP_HOSTS,
        allowed_origins=[
            PUBLIC_BASE_URL,
            "https://chatgpt.com",
            "http://localhost:*",
            "http://127.0.0.1:*",
        ],
    ),
)


@asynccontextmanager
async def lifespan(app):
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="Diagram2Code",
    description="Diagram rendering API for Custom GPT Actions and MCP apps, with an optional UML-MCP backend.",
    version="2.0.0",
    docs_url="/",
    redoc_url=None,
    lifespan=lifespan,
    servers=[{"url": os.getenv("PUBLIC_BASE_URL", "https://openai-uml-plugin.vercel.app")}],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chatgpt.com",
        "https://chat.openai.com",
        "http://localhost:5003",
        "http://127.0.0.1:5003",
    ],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "MCP-Protocol-Version", "Mcp-Session-Id"],
    expose_headers=["Mcp-Session-Id"],
)


class DiagramRequest(BaseModel):
    lang: str = Field(
        description="Source language: plantuml, mermaid, d2, graphviz, or another supported Kroki language."
    )
    type: str = Field(
        min_length=1,
        max_length=100,
        description="Diagram type, such as class, sequence or flowchart.",
    )
    code: str = Field(min_length=1, max_length=100000, description="Diagram source text.")
    theme: str = Field(default="", max_length=100)

    @field_validator("lang")
    @classmethod
    def validate_lang(cls, value):
        value = value.strip().lower()
        value = ALIASES.get(value, value)
        if value not in LANGUAGE_OUTPUT_SUPPORT:
            raise ValueError(f"Unsupported diagram language: {value}")
        return value

    @field_validator("code", "type")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Value must contain non-whitespace characters.")
        return value


class DiagramResponse(BaseModel):
    url: str
    content: str
    playground: str


def render_plantuml(code):
    renderer = PlantUML(url="https://www.plantuml.com/plantuml/dpng", http_opts={"timeout": 20})
    try:
        return renderer.generate_image_from_string(code)
    finally:
        renderer.client.close()


async def render_diagram(diagram: DiagramRequest) -> DiagramResponse:
    try:
        if backend_url():
            result = await generate_with_uml_mcp(
                diagram.lang, diagram.type, diagram.code, diagram.theme
            )
            return DiagramResponse(**result)
        if diagram.lang == "plantuml":
            url, content, playground = await anyio.to_thread.run_sync(render_plantuml, diagram.code)
        elif diagram.lang == "mermaid":
            state = generate_diagram_state(diagram.code, diagram.theme or "dark")
            url, content, playground = generate_mermaid_live_editor_url(state)
        else:
            url, content, playground = await generate_kroki_diagram(
                diagram.lang, diagram.code, "svg"
            )
        if not url:
            raise HTTPException(502, "Renderer did not return a diagram URL.")
        return DiagramResponse(url=url, content=content, playground=playground or "")
    except HTTPException:
        raise
    except PlantUMLHTTPError as exc:
        raise HTTPException(502, "PlantUML could not render this diagram.") from exc
    except Exception as exc:
        logger.exception("Diagram rendering failed for %s", diagram.lang)
        raise HTTPException(
            502, "Diagram renderer failed. Check the source or retry later."
        ) from exc


@app.post(
    "/generate_diagram",
    response_model=DiagramResponse,
    operation_id="generate_diagram_endpoint",
    responses={502: {"description": "Diagram renderer failed"}},
)
async def generate_diagram_endpoint(diagram: DiagramRequest):
    return await render_diagram(diagram)


@mcp.tool(
    annotations=ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=True)
)
async def generate_diagram(lang: str, type: str, code: str, theme: str = "") -> DiagramResponse:
    """Generate a diagram URL and editor link from PlantUML, Mermaid, D2 or Kroki source."""
    return await render_diagram(DiagramRequest(lang=lang, type=type, code=code, theme=theme))


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok", "backend": "uml-mcp" if backend_url() else "direct"}


@app.get("/logo.png", include_in_schema=False)
def plugin_logo():
    return FileResponse(ROOT / ".well-known/logo.png", media_type="image/png")


@app.get("/openapi.yaml", response_class=PlainTextResponse, include_in_schema=False)
async def openapi_yaml():
    return yaml.safe_dump(app.openapi(), sort_keys=False)


@app.get("/.well-known/openapi.yaml", response_class=PlainTextResponse, include_in_schema=False)
async def legacy_openapi_yaml():
    return await openapi_yaml()


@app.get("/.well-known/openapi.json", include_in_schema=False)
async def legacy_openapi_json():
    return app.openapi()


app.mount("/.well-known", StaticFiles(directory=ROOT / ".well-known"), name="static")
app.mount("/mcp", mcp_app)


def main():
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5003)


if __name__ == "__main__":
    main()

import logging
import os
import subprocess
from pydantic import BaseModel, ValidationError, validator
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from typing import Dict, List

from plantuml import PlantUML
from mermaid.mermaid import generate_diagram_state, generate_mermaid_live_editor_url
from D2.run_d2 import run_go_script

app = FastAPI(
    title="GPT Plugin Diagrams",
    description="This plugin generates diagrams from text using GPT-4.",
    version="1.1.1",
    docs_url="/",
    redoc_url=None,
    servers=[{"url": "https://openai-uml-plugin.vercel.app"}, {"url": "http://localhost:5003"}],
)

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

# Add logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

origins = [
    "https://chat.openai.com",
    "https://openai-uml-plugin.vercel.app",
    "http://localhost:5003",
    "http://127.0.0.1:5003",
    "http://0.0.0.0:5003",
    "devtools"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)

LANGUAGE_OUTPUT_SUPPORT: Dict[str, List[str]] = {
    "blockdiag": ["png", "svg", "pdf"],
    "bpmn": ["svg"],
    "bytefield": ["svg"],
    "seqdiag": ["png", "svg", "pdf"],
    "actdiag": ["png", "svg", "pdf"],
    "nwdiag": ["png", "svg", "pdf"],
    "packetdiag": ["png", "svg", "pdf"],
    "rackdiag": ["png", "svg", "pdf"],
    "c4plantuml": ["png", "svg", "pdf", "txt", "base64"],
    "d2": ["png", "svg"],
    "dbml": ["svg"],
    "ditaa": ["png", "svg"],
    "erd": ["png", "svg", "pdf"],
    "excalidraw": ["svg"],
    "graphviz": ["png", "svg", "pdf", "jpeg"],
    "nomnoml": ["svg"],
    "pikchr": ["svg"],
    "structurizr": ["png", "svg", "pdf", "txt", "base64"],
    "svgbob": ["svg"],
    "symbolator": ["svg"],
    "tikz": ["png", "svg", "jpeg", "pdf"],
    "umlet": ["png", "svg", "jpeg"],
    "vega": ["svg", "png"],
    "vega-lite": ["svg", "png"],
    "wavedrom": ["svg"],
    "wireviz": ["png", "svg"],
}

def get_media_type(output_format: str) -> str:
    """Return the appropriate media type based on the output format."""
    if output_format == "svg":
        return "image/svg+xml"
    elif output_format == "png":
        return "image/png"
    elif output_format == "pdf":
        return "application/pdf"
    elif output_format == "jpeg":
        return "image/jpeg"
    else:
        return "application/octet-stream"  # Default to binary

class DiagramRequest(BaseModel):
    lang: str
    type: str
    code: str
    output: str = "svg"  # Removed extra space
    theme: str = ""
    endpoint: str = ""

    @validator('lang')
    def validate_lang(cls, v):
        valid_langs = ["plantuml", "mermaid", "mermaidjs", "d2lang", "D2", "d2", "terrastruct"]
        if v not in valid_langs:
            raise ValidationError(f"Invalid diagram language: {v}")
        return v

    @validator('type')
    def validate_type(cls, v, values):
        lang = values.get('lang')
        if lang:
            valid_types = {
                "plantuml": ["class", "sequence", "activity", "component", "state", "object", "usecase", "mindmap", "git"],
                "mermaid": ["class", "sequence", "flowchart", "gantt", "pie"],
                "d2lang": ["class", "sequence", "state", "activity"],
                "terrastruct": ["class", "sequence", "state", "activity", "network", "flow"],
                "kroki": ["blockdiagram", "sequence", "activity", "state", "class", "usecase", "component", "object", "gantt", "pie"],
                "blockdiag": ["blockdiag", "actdiag", "nwdiag", "packetdiag", "rackdiag"],
                "bpmn": ["bpmn"],
                "bytefield": ["bytefield"],
                "seqdiag": ["seqdiag"],
                "actdiag": ["actdiag"],
                "nwdiag": ["nwdiag"],
                "packetdiag": ["packetdiag"],
                "rackdiag": ["rackdiag"],
                "c4plantuml": ["c4plantuml"],
                "dbml": ["dbml"],
                "ditaa": ["ditaa"],
                "erd": ["erd"],
                "excalidraw": ["excalidraw"],
                "graphviz": ["dot", "neato", "fdp", "sfdp", "twopi", "circo"],
                "nomnoml": ["nomnoml"],
                "pikchr": ["pikchr"],
                "structurizr": ["structurizr"],
                "svgbob": ["svgbob"],
                "symbolator": ["symbolator"],
                "tikz": ["tikz"],
                "umlet": ["umlet"],
                "vega": ["vega"],
                "vega-lite": ["vega-lite"],
                "wavedrom": ["wavedrom"],
                "wireviz": ["wireviz"]
            }
            if lang in valid_types and v not in valid_types[lang]:
                raise ValidationError(f"Invalid diagram type '{v}' for language '{lang}'")
        return v

    @validator('code')
    def validate_code(cls, v):
        if len(v) > 100000:
            raise ValidationError("Diagram code is too long.")
        return v

    @validator('output')
    def validate_output(cls, v, values):
        lang = values.get('lang')
        if lang and v not in LANGUAGE_OUTPUT_SUPPORT.get(lang, []):
            raise ValidationError(f"Output format '{v}' is not supported for language '{lang}'")
        return v

    @validator('endpoint')
    def validate_endpoint(cls, v, values):
        lang = values.get('lang')
        if lang not in ["kroki", "plantuml", "mermaid", "mermaidjs", "d2lang", "D2", "d2", "terrastruct"] and v:
            raise ValidationError("Endpoint should not be provided unless 'lang' is set to 'kroki', 'plantuml', 'mermaid', 'mermaidjs', 'd2lang', 'D2', 'd2', or 'terrastruct'.")
        return v

@app.post("/generate_diagram")
async def generate_diagram_endpoint(diagram: DiagramRequest):
    logger.info(f"Received request to generate a {diagram.lang} diagram.")
    if not diagram.code:
        raise HTTPException(status_code=422, detail="No diagram code provided.")
    if not diagram.lang:
        raise HTTPException(status_code=422, detail="No diagram language provided.")
    if not diagram.type:
        raise HTTPException(status_code=422, detail="No diagram type provided.")
    logger.info(f"A request was made to generate a {diagram.lang} diagram.")
    try:
        if diagram.lang in ["plantuml"]:
            if not diagram.theme:
                diagram.theme = "blueprint"
            logger.info("Generating PlantUML diagram.")
            plantuml = PlantUML(url="https://www.plantuml.com/plantuml/dpng")
            url, content, playground = plantuml.generate_image_from_string(str(diagram.code))
            print(url)
            print(content)
            if url is None:
                raise HTTPException(status_code=400, detail="Invalid PlantUML syntax.")
            return {"url": url, "content": content, "playground": playground}
        elif diagram.lang in ["mermaid", "mermaidjs"]:
            if not diagram.theme:
                diagram.theme = "dark"
            logger.info("Generating Mermaid diagram.")
            diagram_state = generate_diagram_state(str(diagram.code), str(diagram.theme))
            url, content, playground = generate_mermaid_live_editor_url(diagram_state)
            if url is None:
                raise HTTPException(status_code=400, detail="Invalid Mermaid syntax.")
            return {"url": url, "content": content, "playground": playground}
        elif diagram.lang in ["d2lang", "D2", "d2", "terrastruct"]:
            logger.info("Generating D2 diagram.")
            if not diagram.theme:
                diagram.theme = "Neutral default"
            url, content, playground = await run_go_script(str(diagram.code))
            return {"url": url, "content": content, "playground": playground}
        else:
            try:
                kroki_endpoint = f"https://kroki.io/{diagram.lang}/{diagram.output}"
                async with httpx.AsyncClient() as client:
                    response = await client.post(kroki_endpoint, content=diagram.code.encode('utf-8'))
                    if response.status_code == 200:
                        media_type = get_media_type(diagram.output)
                        return Response(content=response.content, media_type=media_type)
                    else:
                        raise HTTPException(status_code=400, detail=f"Kroki error: {response.text}")
            except Exception as e:
                logger.error(f"Failed to generate diagram with Kroki: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to generate diagram.")
    except Exception as e:
        logger.error(f"Error generating {diagram.lang} diagram: {str(e)}")
        return {"error": "An error occurred while generating the diagram."}

@app.get("/logo.png")
def plugin_logo():
    logger.info("Received request for plugin logo.")
    return FileResponse("./.well-known/logo.png", media_type="image/png")

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    logger.info("Received request for plugin manifest.")
    with open("./.well-known/ai-plugin.json") as f:
        return JSONResponse(content=f.read(), media_type="text/json")

@app.get("/openapi.yaml", response_class=PlainTextResponse)
async def openapi_spec():
    logger.info("Received request for OpenAPI spec.")
    with open("./.well-known/openapi.yaml") as f:
        return f.read()

@app.get("/openapi.json", response_class=PlainTextResponse)
async def openapi_spec_json():
    with open("./.well-known/openapi.json") as f:
        return f.read()

@app.get("/.well-known/privacy.txt", response_class=PlainTextResponse)
async def privacy_policy():
    return FileResponse("./.well-known/privacy.txt")

def main():
    import uvicorn
    logger.info("Starting server.")
    uvicorn.run(app, host="localhost", port=5003)

if __name__ == "__main__":
    main()

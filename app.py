import logging
import os
import subprocess
from pydantic import BaseModel, validator, ValidationError
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from D2.run_d2 import run_go_script

from plantuml import PlantUML
from mermaid.mermaid import generate_diagram_state, generate_mermaid_live_editor_url
from kroki.kroki import generate_diagram as generate_kroki_diagram, LANGUAGE_OUTPUT_SUPPORT as KROKI_LANGUAGE_SUPPORT

app = FastAPI(
    title="GPT Plugin Diagrams",
    description="This plugin generates diagrams from text using GPT-4.",
    version="1.1.2",
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

class DiagramRequest(BaseModel):
    lang: str
    type: str
    code: str
    theme: str = ""

    @validator('lang')
    def validate_lang(cls, v):
        valid_langs = [
            "plantuml", "mermaid", "mermaidjs", "d2lang", "D2", "d2", "terrastruct", "graphviz",
            "blockdiag", "bpmn", "bytefield", "seqdiag", "actdiag", "nwdiag", 
            "packetdiag", "rackdiag", "c4plantuml", "dbml", "ditaa", "erd", 
            "excalidraw", "nomnoml", "pikchr", "structurizr", "svgbob", 
            "symbolator", "tikz", "umlet", "vega", "vegalite", "wavedrom", "wireviz"
        ]
        if v not in valid_langs:
            raise ValidationError(f"Invalid diagram language: {v}")
        return v

    @validator('type')
    def validate_type(cls, v):
        valid_types = ["class", "sequence", "activity", "component", "state", "object", "usecase", "mindmap", "git", "gantt"]
        if v not in valid_types:
            logger.error(f"Invalid diagram type: {v}")
        return v

    @validator('code')
    def validate_code(cls, v):
        if len(v) > 100000:
            raise ValidationError("Diagram code is too long.")
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
        elif diagram.lang in KROKI_LANGUAGE_SUPPORT:
            logger.info(f"Generating Kroki diagram ({diagram.lang}).")
            output_format = "svg"
            url, content, playground = await generate_kroki_diagram(diagram.lang, str(diagram.code), output_format)
            return {"url": url, "content": content, "playground": playground}
        else:
            raise HTTPException(status_code=422, detail=f"Unknown diagram type: {diagram.lang}")
    except HTTPException as e:
        raise e
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

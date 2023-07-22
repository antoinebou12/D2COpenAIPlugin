import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import re
import asyncio

from plantuml.plantumlapi import PlantUML
from mermaid.mermaid import generate_diagram_state, generate_mermaid_live_editor_url
from D2.playwright_d2 import run_playwright

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

class DiagramRequest(BaseModel):
    lang: str
    type: str
    code: str
    theme: str = None

@app.post("/generate_diagram")
async def generate_diagram_endpoint(diagram: DiagramRequest):
    logger.info(f"Received request to generate a {diagram.lang} diagram.")
    if not diagram.code:
        raise HTTPException(status_code=422, detail="No diagram text provided.")
    if not diagram.lang:
        raise HTTPException(status_code=422, detail="No diagram language provided.")
    if not diagram.type:
        raise HTTPException(status_code=422, detail="No diagram type provided.")
    logger.info(f"A request was made to generate a {diagram.lang} diagram.")
    try:
        if diagram.lang == "plantuml":
            if not diagram.theme:
                diagram.theme = "blueprint"
            logger.info("Generating PlantUML diagram.")
            plantuml = PlantUML(url="https://www.plantuml.com/plantuml/dpng")
            content, url = plantuml.generate_image_from_string(diagram.code)
            if url is None:
                raise HTTPException(status_code=400, detail="Invalid PlantUML syntax.")
            return {"url": url, "content": content}
        elif diagram.lang in ["mermaid", "mermaidjs"]:
            if not diagram.theme:
                diagram.theme = "dark"
            logger.info("Generating Mermaid diagram.")
            diagram_state = generate_diagram_state(diagram.code)
            url = generate_mermaid_live_editor_url(diagram_state)
            if url is None:
                raise HTTPException(status_code=400, detail="Invalid Mermaid syntax.")
            return {"url": url, "content": content}
        elif diagram.lang in ["D2", "d2", "terrastruct", "Declarative Diagramming", "Text to Diagram"]:
            logger.info("Generating D2 diagram.")
            if not diagram.theme:
                diagram.theme = "Neutral default"
            url, content = await run_playwright(diagram.code, "elk", diagram.theme)
            return {"url": url, "content": content}
        elif diagram.lang == "graphviz":
            raise HTTPException(status_code=422, detail="Graphviz diagrams are not yet supported.")
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

def main():
    import uvicorn
    logger.info("Starting server.")
    uvicorn.run(app, host="localhost", port=5003)

if __name__ == "__main__":
    main()

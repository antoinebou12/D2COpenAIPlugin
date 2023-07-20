import os
import re
import logging
import uuid
from pydantic import BaseModel
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import re

from .plantuml.plantumlapi import PlantUML

from .mermaid.mermaid import generate_diagram_state, generate_mermaid_live_editor_url

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
    diagram_type: str
    diagram_text: str

@app.post("/generate_diagram")
async def generate_diagram_endpoint(diagram: DiagramRequest):
    if not diagram.diagram_text:
        raise HTTPException(status_code=422, detail="No diagram text provided.")
    if not diagram.lang:
        raise HTTPException(status_code=422, detail="No diagram language provided.")
    if not diagram.diagram_type:
        raise HTTPException(status_code=422, detail="No diagram type provided.")
    logger.info(f"A request was made to generate a {diagram.lang} diagram.")
    try:
        if diagram.lang == "plantuml":
            plantuml = PlantUML(url="https://www.plantuml.com/plantuml/dpng")
            content, url = plantuml.generate_image_from_string(diagram.diagram_text)
            if url is None:
                raise HTTPException(status_code=400, detail="Invalid PlantUML syntax.")
            print(f"Content: {content}")
            return {"url": url}
        elif diagram.lang in ["mermaid", "mermaidjs"]:
            diagram_state = generate_diagram_state(diagram.diagram_text)
            url = generate_mermaid_live_editor_url(diagram_state)
            if url is None:
                raise HTTPException(status_code=400, detail="Invalid Mermaid syntax.")
            return {"url": url}
        else:
            raise HTTPException(status_code=422, detail=f"Unknown diagram type: {diagram.lang}")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating {diagram.lang} diagram: {str(e)}")
        return {"error": "An error occurred while generating the diagram."}


@app.get("/logo.png")
def plugin_logo():
    return FileResponse("./.well-known/logo.png", media_type="image/png")

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("./.well-known/ai-plugin.json") as f:
        return JSONResponse(content=f.read(), media_type="text/json")

@app.get("/openapi.yaml", response_class=PlainTextResponse)
async def openapi_spec():
    with open("./.well-known/openapi.yaml") as f:
        return f.read()

@app.get("/openapi.json", response_class=PlainTextResponse)
async def openapi_spec_json():
    with open("./.well-known/openapi.json") as f:
        return f.read()

def generate_plantuml(text: str):
    text = text.replace("\n", " \n ").replace("\\n", f"{chr(13)}{chr(10)}")
    text = text.replace("@startuml", f"{chr(13)}{chr(10)}@startuml{chr(13)}{chr(10)}")
    text = text.replace("@enduml", f"{chr(13)}{chr(10)}@enduml{chr(13)}{chr(10)}")
    logger.info(f"Text after replacing newlines: {text}")
    try:
        plantuml = PlantUML(url="https://www.plantuml.com/plantuml/dpng")
        content, url = plantuml.generate_image_from_string(text)
        # with open(output_file, "wb") as f:
        #     f.write(content)
        return content, url
    except Exception as e:
        logger.error(f"Error generating PlantUML diagram: {str(e)}")
        return None, None, None

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()

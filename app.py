import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
import logging
import uuid
from pydantic import BaseModel

from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

import yaml
from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import httpx

from plantumlapi.plantumlapi import PlantUML

app = FastAPI(
    title="GPT Plugin Diagrams",
    description="This plugin generates diagrams from text using GPT-4.",
    version="1.1.1",
    docs_url="/",
    redoc_url=None,
    servers=[{"url": "https://openai-uml-plugin.vercel.app"}],
)

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")
app.mount("/public", StaticFiles(directory="public"), name="public")

# Add logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add this line to serve the OpenAPI YAML file
app.mount(
    "/openapi", StaticFiles(directory=os.path.dirname(__file__)), name="openapi")

class CORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = Response("Temporary", status_code=400)
        origin_regex = "https://.*\.antoinebou12\.vercel\.app"
        if 'origin' in request.headers:
            origin = request.headers['origin']
            if re.match(origin_regex, origin) or origin in ["https://chat.openai.com", "https://openai-uml-plugin.vercel.app"]:
                response = await call_next(request)
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "*"
        return response

app.add_middleware(CORSMiddleware)

def generate_plantuml(text: str, output_file: str):
    # escape newlines for PlantUML
    text = text.replace("\n", " \n ")
    text = text.replace("\\n", f"{chr(13)}{chr(10)}")
    # newline after each @startuml
    text = text.replace(
        "@startuml", f"{chr(13)}{chr(10)}@startuml{chr(13)}{chr(10)}")
    # newline after each @enduml
    text = text.replace(
        "@enduml", f"{chr(13)}{chr(10)}@enduml{chr(13)}{chr(10)}")

    logger.info(f"Text after replacing newlines: {text}")
    try:
        plantuml = PlantUML(
            url="https://www.plantuml.com/plantuml/dpng",
        )
        content, url, output_file = plantuml.generate_image_from_string(
            text, output_file
        )
        with open(output_file, "wb") as f:
            f.write(content)
        return content, url, output_file
    except Exception as e:
        logger.error(f"Error generating PlantUML diagram: {str(e)}")
        return None, None, None

class DiagramRequest(BaseModel):
    text: str

@app.post("/generate_diagram/{diagram_type}")
async def generate_diagram_endpoint(
    diagram_type: str,
    text: DiagramRequest,
):
    logger.info(f"A request was made to generate a {diagram_type} diagram.")
    try:
        print(f"Text: {text}")
        if diagram_type != "plantuml":
            raise HTTPException(
                status_code=422, detail=f"Unknown diagram type: {diagram_type}"
            )
        output_file = f"public/{diagram_type}-{uuid.uuid4()}.png"
        content, url, output_file = generate_plantuml(text.text, output_file)
        return {
            "url": url,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating {diagram_type} diagram: {str(e)}")
        return {"error": "An error occurred while generating the diagram."}


@app.get("/logo.png")
def plugin_logo():
    return FileResponse("./.well-known/logo.png", media_type="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest(request: Request):
    host = request.headers["Host"]
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return JSONResponse(content=text, media_type="text/json")

@app.get("/ai-plugin.json")
async def plugin_manifest(request: Request):
    host = request.headers["Host"]
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return JSONResponse(content=text, media_type="text/json")

@app.get("/openapi.yaml", response_class=PlainTextResponse)
async def openapi_spec():
    with open("./.well-known/openapi.yaml") as f:
        return f.read()

@app.get("/openapi.json", response_class=PlainTextResponse)
async def openapi_spec_json():
    with open("./.well-known/openapi.json") as f:
        return f.read()

def main():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()

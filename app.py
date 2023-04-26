import os
import re
import subprocess
from pathlib import Path
from typing import Optional
import logging
import uuid

from diagrams import Cluster, Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

import yaml
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import httpx

from plantumlapi.plantumlapi import PlantUML

app = FastAPI(
    title="GPT Plugin Diagrams",
    description="This plugin generates diagrams from text using GPT-4.",
    version="0.1.0",
    docs_url="/",
    redoc_url=None,
    servers=[{"url": "https://gpt-plugin-diagrams.antoineboucher.info"}]
)


app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")
app.mount("/public", StaticFiles(directory="public"), name="public")

# Add logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add this line to serve the OpenAPI YAML file
app.mount(
    "/openapi", StaticFiles(directory=os.path.dirname(__file__)), name="openapi")


# CORS middleware configuration
origins = [
    "https://chat.openai.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_plantuml(text: str, output_file: str):
    # escape newlines for PlantUML
    text = text.replace('\n', ' \n ')
    text = text.replace('\\n', f'{chr(13)}{chr(10)}')
    # newline after each @startuml
    text = text.replace('@startuml', f'{chr(13)}{chr(10)}@startuml{chr(13)}{chr(10)}')
    # newline after each @enduml
    text = text.replace('@enduml', f'{chr(13)}{chr(10)}@enduml{chr(13)}{chr(10)}')

    logger.info(f"Text after replacing newlines: {text}")
    try:
        plantuml = PlantUML(
            url='https://www.planttext.com/api/plantuml/png',
        )
        content, url, output_file = plantuml.generate_image_from_string(text, output_file)
        with open(output_file, 'wb') as f:
            f.write(content)
        return content, url, output_file
    except Exception as e:
        logger.error(f"Error generating PlantUML diagram: {str(e)}")
        return None, None, None

@app.post('/generate_diagram/{diagram_type}')
async def generate_diagram_endpoint(diagram_type: str, text: str):
    logger.info(f"A request was made to generate a {diagram_type} diagram.")
    output_file = f'public/{diagram_type}-{uuid.uuid4()}.png'
    try:
        content, url, output_file = generate_plantuml(text, output_file)
        return {
            'url': url,
        }
    except Exception as e:
        logger.error(f"Error generating PlantUML diagram: {str(e)}")
        return {'error': "An error occurred while generating the diagram."}

@app.get("/logo.png")
async def plugin_logo():
    filename = "logo.png"
    return await FastAPI.send_file(filename, mimetype="image/png")

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest(request: Request):
    host = request.headers["Host"]
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return JSONResponse(content=text, media_type="text/json")

@app.get("/openapi.yaml")
async def openapi_spec(request: Request):
    host = request.headers["Host"]
    with open("openapi.yaml") as f:
        text = f.read()
        return JSONResponse(content=text, media_type="text/yaml")

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()

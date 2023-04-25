import os
import subprocess
from pathlib import Path
from typing import Optional
import logging

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

app = FastAPI()

# Use environment variables to store sensitive information
API_KEY = os.environ.get('API_KEY')
PLANTUML_JAR = os.environ.get('PLANTUML_JAR')

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
async def serve_openapi_yaml(request: Request):
    yaml_file = os.path.join(os.path.dirname(__file__), 'openapi.yaml')
    with open(yaml_file, 'r') as f:
        yaml_data = f.read()
    yaml_data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    return JSONResponse(content=yaml_data)

async def generate_text(prompt: str):
    url = 'https://api.openai.com/v1/engines/gpt-4/completions'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': prompt,
        # You can adjust the number of tokens (words) in the response
        'max_tokens': 50,
        'n': 1,
        'stop': None,
        'temperature': 1.0
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['text'].strip()
    else:
        print(f"Error: {response.status_code}")
        return None


def generate_plantuml(input_file: str, output_file: str):
    if not PLANTUML_JAR or not os.path.isfile(PLANTUML_JAR):
        logger.error(
            f"Error generating PlantUML diagram: Invalid PlantUML JAR file path: {PLANTUML_JAR}")
        return None

    if not input_file or not os.path.isfile(input_file):
        logger.error(
            f"Error generating PlantUML diagram: Invalid input file path: {input_file}")
        return None

    try:
        command = f"java -jar {PLANTUML_JAR} -tpng -o {output_file} {input_file}"
        subprocess.run(command, shell=True)
    except Exception as e:
        logger.error(f"Error generating PlantUML diagram: {str(e)}")
        return None


def generate_diagram(title: str, nodes: dict, relationships: list, output_file: str):
    with Diagram(title, show=False, filename=output_file, outformat="png"):
        clusters = {}
        for label in nodes.values():
            if cluster := label.get('cluster', None):
                if cluster not in clusters:
                    clusters[cluster] = Cluster(cluster)
                clusters[cluster] += eval(label.get('class', 'EC2'))(label['name'])
            else:
                eval(label.get('class', 'EC2'))(label['name'])

        for rel in relationships:
            from_node = nodes[rel['from_node']]['name']
            to_node = nodes[rel['to_node']]['name']
            with Cluster(clusters.get(rel.get('cluster', None))):
                eval(rel.get('class', 'Edge'))(from_node, to_node)

def generate_diagrams(output_file: str):
    """
    Generate diagrams from Python script files located in the 'diagrams' folder.
    """
    for file in Path('diagrams').glob('*.py'):
        with open(file, 'r') as f:
            code = f.read()
        exec(code, {'output_file': output_file})


def generate_mermaid(input_file: str, output_file: str):
    if not input_file or not os.path.isfile(input_file):
        logger.error(f"Error generating Mermaid diagram: Invalid input file path: {input_file}")
        return None

    try:
        command = f"mmdc -i {input_file} -o {output_file}"
        subprocess.run(command, shell=True)
    except Exception as e:
        logger.error(f"Error generating Mermaid diagram: {str(e)}")
        return None

@app.get('/generate_text/{prompt}')
async def generate_text_endpoint(prompt: str):
    generated_text = await generate_text(prompt)
    if generated_text:
        return {'text': generated_text}
    else:
        return {'error': "An error occurred while generating text."}


@app.post('/generate_diagram/{diagram_type}')
async def generate_diagram_endpoint(diagram_type: str, input_file: Optional[str] = None, output_file: Optional[str] = None):
    if diagram_type == 'plantuml':
        generate_plantuml(input_file, output_file)
    elif diagram_type == 'diagrams':
        generate_diagrams(output_file)
    elif diagram_type == 'mermaid':
        generate_mermaid(input_file, output_file)
    else:
        return {'error': "Invalid diagram type."}

    return {'output_file': output_file}


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
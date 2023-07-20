from fastapi.testclient import TestClient
import pytest

from .app import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200

def test_plugin_manifest():
    response = client.get("/.well-known/ai-plugin.json")
    assert response.status_code == 200
    assert "api" in response.json()

def test_logo_endpoint():
    response = client.get("/logo.png")
    assert response.status_code == 200

def test_generate_diagram_endpoint():
    response = client.post("/generate_diagram", json={
        "lang": "plantuml",
        "diagram_type": "sequence",
        "diagram_text": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"
    })
    assert response.status_code == 200
    assert "url" in response.json()

def test_generate_mermaid_diagram_endpoint():
    response = client.post("/generate_diagram", json={
        "lang": "mermaid",
        "diagram_type": "sequence",
        "diagram_text": "sequenceDiagram\n    Alice->>Bob: Hello Bob, how are you?\n    Bob-->>Alice: Not too bad, thanks!"
    })
    assert response.status_code == 200
    assert "url" in response.json()

def test_generate_diagram_endpoint_with_empty_text():
    response = client.post("/generate_diagram", json={
        "lang": "plantuml",
        "diagram_type": "sequence",
        "diagram_text": ""
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_generate_diagram_endpoint_with_no_lang():
    response = client.post("/generate_diagram", json={
        "diagram_type": "sequence",
        "diagram_text": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_generate_diagram_endpoint_with_unsupported_lang():
    response = client.post("/generate_diagram", json={
        "lang": "unsupported",
        "diagram_type": "sequence",
        "diagram_text": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_openapi_spec():
    response = client.get("/openapi.yaml")
    assert response.status_code == 200
    assert "openapi: 3.0.2" in response.text

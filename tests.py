import httpx
import pytest
from fastapi.testclient import TestClient
from main import app  # replace 'main' with the name of your Python file

client = TestClient(app)

def test_plugin_manifest():
    response = client.get("/.well-known/ai-plugin.json")
    assert response.status_code == 200
    assert "application" in response.json()

def test_generate_diagram_endpoint():
    response = client.post("/generate_diagram/plantuml", json={"text": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"})
    assert response.status_code == 200
    assert "url" in response.json()

def test_generate_diagram_endpoint_with_invalid_diagram_type():
    response = client.post("/generate_diagram/invalid", json={"text": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"})
    assert response.status_code == 422  # 422 Unprocessable Entity

def test_openapi_spec():
    response = client.get("/openapi.yaml")
    assert response.status_code == 200
    assert "openapi: 3.0.2" in response.text

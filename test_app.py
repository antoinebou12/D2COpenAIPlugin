from fastapi.testclient import TestClient
import pytest

from app import app

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

def test_generate_diagram_endpoint_with_no_text():
    response = client.post("/generate_diagram/plantuml", json={})
    assert response.status_code == 422  # 422 Unprocessable Entity

def test_generate_diagram_endpoint_with_no_diagram_type():
    response = client.post("/generate_diagram/", json={"text": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"})
    assert response.status_code == 404  # 404 Not Found

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

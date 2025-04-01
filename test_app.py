"""
Tests for the Diagram2Code OpenAI Plugin API server.
"""

import pytest
from fastapi.testclient import TestClient

from app import app

# Create test client
client = TestClient(app)

# Set to True to skip tests that require external services
SKIP_EXTERNAL_TESTS = True

# API Endpoint Tests
def test_root_endpoint():
    """Test the root endpoint (API docs)."""
    response = client.get("/")
    assert response.status_code == 200

def test_plugin_manifest():
    """Test the OpenAI plugin manifest endpoint."""
    response = client.get("/.well-known/ai-plugin.json")
    assert response.status_code == 200
    assert "api" in response.json()

def test_logo_endpoint():
    """Test the logo endpoint."""
    response = client.get("/logo.png")
    assert response.status_code == 200

@pytest.mark.skipif(SKIP_EXTERNAL_TESTS, reason="Skip tests requiring external services")
def test_generate_diagram_endpoint():
    """Test PlantUML diagram generation."""
    response = client.post("/generate_diagram", json={
        "lang": "plantuml",
        "type": "sequence",
        "code": "@startuml \n Alice -> Bob: Authentication Request \n @enduml"
    })
    assert response.status_code == 200
    assert "url" in response.json()

@pytest.mark.skipif(SKIP_EXTERNAL_TESTS, reason="Skip tests requiring external services")
def test_generate_mermaid_diagram_endpoint():
    """Test Mermaid diagram generation."""
    response = client.post("/generate_diagram", json={
        "lang": "mermaid",
        "type": "sequence",
        "code": "sequenceDiagram\n    Alice->>Bob: Hello Bob, how are you?\n    Bob-->>Alice: Not too bad, thanks!"
    })
    assert response.status_code == 200
    assert "url" in response.json()

@pytest.mark.skipif(SKIP_EXTERNAL_TESTS, reason="Skip tests requiring external services")
def test_generate_d2_diagram_endpoint():
    """Test D2 diagram generation."""
    response = client.post("/generate_diagram", json={
        "lang": "d2lang",
        "type": "class",
        "code": "class Test{}"
    })
    assert response.status_code == 200
    response_json = response.json()
    assert "url" in response_json
    assert "content" in response_json
    assert "playground" in response_json
    assert response_json["content"] == "class Test{}"

# Validation Tests
def test_generate_diagram_endpoint_with_empty_text():
    """Test validation with empty diagram code."""
    response = client.post("/generate_diagram", json={
        "lang": "plantuml",
        "type": "sequence",
        "code": ""
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_generate_diagram_endpoint_with_no_lang():
    """Test validation with missing language."""
    response = client.post("/generate_diagram", json={
        "type": "sequence",
        "code": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_generate_diagram_endpoint_with_unsupported_lang():
    """Test validation with unsupported language."""
    response = client.post("/generate_diagram", json={
        "lang": "invalid-language",  # Use a different name that's not in the test but still invalid
        "type": "sequence",
        "code": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_openapi_spec():
    """Test the OpenAPI specification endpoint."""
    response = client.get("/openapi.yaml")
    assert response.status_code == 200
    assert "openapi:" in response.text

# MCP Tests
def test_mcp_info_endpoint():
    """Test the MCP info endpoint."""
    response = client.get("/mcp")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "mcp_endpoint" in data
    assert data["mcp_endpoint"] == "/mcp/ws"

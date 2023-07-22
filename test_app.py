from fastapi.testclient import TestClient
import pytest
from D2.run_d2 import run_go_script
from mermaid.mermaid import PakoSerde, deserialize_state, generate_diagram_state, generate_mermaid_live_editor_url, serialize_state
from plantuml import PlantUML, PlantUMLHTTPError

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
        "type": "sequence",
        "code": "@startuml \n Alice -> Bob: Authentication Request  \n @enduml"
    })
    assert response.status_code == 200
    assert "url" in response.json()

def test_generate_mermaid_diagram_endpoint():
    response = client.post("/generate_diagram", json={
        "lang": "mermaid",
        "type": "sequence",
        "code": "sequenceDiagram\n    Alice->>Bob: Hello Bob, how are you?\n    Bob-->>Alice: Not too bad, thanks!"
    })
    assert response.status_code == 200
    assert "url" in response.json()

def test_generate_d2_diagram_endpoint():
    response = client.post("/generate_diagram", json={
        "lang": "D2",
        "type": "class",
        "code": "class Test{}"
    })
    assert response.status_code == 200
    assert "url" in response.json()

def test_generate_diagram_endpoint_with_empty_text():
    response = client.post("/generate_diagram", json={
        "lang": "plantuml",
        "type": "sequence",
        "code": ""
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_generate_diagram_endpoint_with_no_lang():
    response = client.post("/generate_diagram", json={
        "type": "sequence",
        "code": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_generate_diagram_endpoint_with_unsupported_lang():
    response = client.post("/generate_diagram", json={
        "lang": "unsupported",
        "type": "sequence",
        "code": "@startuml\nAlice -> Bob: Authentication Request\n@enduml"
    })
    assert response.status_code == 422  # Unprocessable Entity

def test_openapi_spec():
    response = client.get("/openapi.yaml")
    assert response.status_code == 200
    assert "openapi: 3.0.2" in response.text


def test_generate_image_from_string():
    plantuml = PlantUML(url="https://www.plantuml.com/plantuml/dpng")

    # Test with valid PlantUML text
    valid_text = """@startuml \n Alice -> Bob: Authentication Request \n @enduml"""
    try:
        url, content = plantuml.generate_image_from_string(valid_text)
        assert url is not None
        assert content is not None
    except PlantUMLHTTPError:
        pytest.fail("PlantUMLHTTPError was raised with valid PlantUML text")

    # Test with invalid PlantUML text
    invalid_text = "This is not valid PlantUML text"
    with pytest.raises(PlantUMLHTTPError):
        plantuml.generate_image_from_string(invalid_text)



def test_pako_serde():
    serde = PakoSerde()
    original = "Hello, world!"
    serialized = serde.serialize(original)
    assert original == serde.deserialize(serialized)

def test_generate_diagram_state():
    diagram_text = "graph TD; A-->B;"
    state = generate_diagram_state(diagram_text)
    assert state["code"] == diagram_text
    assert state["mermaid"]["theme"] == "dark"
    assert state["updateEditor"] == True
    assert state["autoSync"] == True
    assert state["updateDiagram"] == True

def test_generate_mermaid_live_editor_url():
    diagram_text = "graph TD; A-->B;"
    state = generate_diagram_state(diagram_text)
    url, code = generate_mermaid_live_editor_url(state)
    assert url.startswith("https://mermaid.ink/svg/")
    assert code == diagram_text

def test_serialize_deserialize_state():
    state = {"key": "value"}
    serialized = serialize_state(state)
    deserialized = deserialize_state(serialized)
    assert state == deserialized

@pytest.mark.asyncio
async def test_run_go_script():
    # Define some test input
    test_input = "test input"

    # Call the function with the test input
    await run_go_script(test_input)
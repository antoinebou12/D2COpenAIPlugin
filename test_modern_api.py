"""Regression coverage for Actions schemas, error responses, and MCP transport."""

from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import yaml
from fastapi.testclient import TestClient

from . import app as api
from . import uml_backend


@pytest.fixture(scope="module")
def client():
    with TestClient(api.app, base_url="http://localhost") as value:
        yield value


@pytest.fixture(autouse=True)
def direct_backend(monkeypatch):
    monkeypatch.setenv("UML_MCP_URL", "")


@pytest.mark.parametrize("code", ["", "  \n", "a" * 100001])
def test_invalid_source(code, client):
    assert (
        client.post(
            "/generate_diagram", json={"lang": "mermaid", "type": "flowchart", "code": code}
        ).status_code
        == 422
    )


def test_schemas_match_and_describe_response(client):
    schema = client.get("/openapi.json").json()
    assert yaml.safe_load(client.get("/openapi.yaml").text) == schema
    assert client.get("/.well-known/openapi.json").json() == schema
    assert yaml.safe_load(client.get("/.well-known/openapi.yaml").text) == schema
    response = schema["components"]["schemas"]["DiagramResponse"]
    assert set(response["required"]) == {"url", "content", "playground"}
    assert (
        schema["paths"]["/generate_diagram"]["post"]["operationId"] == "generate_diagram_endpoint"
    )


def test_renderer_failure_is_not_success(monkeypatch, client):
    monkeypatch.setattr(
        api,
        "generate_kroki_diagram",
        AsyncMock(side_effect=RuntimeError("private upstream details")),
    )
    response = client.post(
        "/generate_diagram", json={"lang": "d2", "type": "class", "code": "a -> b"}
    )
    assert response.status_code == 502
    assert "private upstream details" not in response.text


def test_remote_backend_and_alias(monkeypatch, client):
    monkeypatch.setenv("UML_MCP_URL", "https://uml.example/mcp")
    backend = AsyncMock(
        return_value={
            "url": "https://example.test/image.svg",
            "content": "a -> b",
            "playground": "",
        }
    )
    monkeypatch.setattr(api, "generate_with_uml_mcp", backend)
    response = client.post(
        "/generate_diagram", json={"lang": "D2", "type": "class", "code": "a -> b"}
    )
    assert response.status_code == 200
    backend.assert_awaited_once_with("d2", "class", "a -> b", "")
    assert client.get("/health").json()["backend"] == "uml-mcp"


def test_mcp_discovery_and_generation(client):
    headers = {"Accept": "application/json, text/event-stream"}
    initialized = client.post(
        "/mcp/",
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        },
    )
    assert initialized.status_code == 200, initialized.text
    listed = client.post(
        "/mcp/",
        headers=headers,
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    )
    tool = listed.json()["result"]["tools"][0]
    assert tool["name"] == "generate_diagram"
    assert tool["annotations"]["readOnlyHint"] is True
    result = client.post(
        "/mcp/",
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "generate_diagram",
                "arguments": {
                    "lang": "mermaid",
                    "type": "flowchart",
                    "code": "graph TD; A-->B;",
                },
            },
        },
    )
    payload = result.json()["result"]
    assert not payload.get("isError", False), payload
    assert payload["structuredContent"]["url"].startswith("https://mermaid.ink/")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "lang,kind", [("plantuml", "sequence"), ("mermaid", "mermaid"), ("d2", "d2")]
)
async def test_uml_mcp_protocol_adapter(monkeypatch, lang, kind):
    monkeypatch.setenv("UML_MCP_URL", "https://uml.example/mcp")
    session = SimpleNamespace(
        initialize=AsyncMock(),
        call_tool=AsyncMock(
            return_value=SimpleNamespace(
                is_error=False,
                structured_content={
                    "url": "https://example.test/image.svg",
                    "playground": "https://example.test/edit",
                },
                content=[],
            )
        ),
    )

    @asynccontextmanager
    async def transport(url):
        assert url == "https://uml.example/mcp"
        yield (None, None)

    @asynccontextmanager
    async def client_session(read, write):
        yield session

    monkeypatch.setattr(uml_backend, "streamable_http_client", transport)
    monkeypatch.setattr(uml_backend, "ClientSession", client_session)
    result = await uml_backend.generate_with_uml_mcp(lang, "sequence", "source", "dark")
    session.call_tool.assert_awaited_once_with(
        "generate_uml",
        {"diagram_type": kind, "code": "source", "output_format": "svg", "theme": "dark"},
    )
    assert result["content"] == "source"

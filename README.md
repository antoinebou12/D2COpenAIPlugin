# Diagram2Code

Diagram2Code renders diagram source through [UML-MCP](https://github.com/antoinebou12/uml-mcp) and returns an image URL, the source, and an editor link. It supports Custom GPT Actions through its HTTP API and ChatGPT apps through Streamable HTTP MCP.

The existing `POST /generate_diagram` request and response remain available. The legacy plugin manifest and asset URLs also remain available.

## Run locally

Use Python 3.12 or newer. CI tests Python 3.12, 3.14 and 3.15.

```powershell
uv venv --python 3.14
uv pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 5003
```

Open [API docs](http://127.0.0.1:5003/). The health endpoint is `/health`.

## Custom GPT Actions

Import `https://openai-uml-plugin.vercel.app/openapi.json` in the GPT editor's Actions configuration. Choose no authentication for this public API. Keep the existing `generate_diagram_endpoint` operation when updating an existing GPT.

[OpenAI's GPT Actions documentation](https://developers.openai.com/api/docs/actions/introduction) describes configuration. The server generates OpenAPI JSON and YAML from the live request and response models. The legacy `/.well-known/openapi.json` and `/.well-known/openapi.yaml` URLs serve the same schema.

The [existing Custom GPT](https://chatgpt.com/g/g-B1Bfoq5qh-uml-diagram-creation-expert) can continue using the HTTP API after its Action schema is refreshed.

## MCP apps

Connect an MCP client to `https://openai-uml-plugin.vercel.app/mcp/` or, during local development, `http://127.0.0.1:5003/mcp/`. The endpoint exposes `generate_diagram` with the same arguments as the HTTP API and a structured response. It uses stateless Streamable HTTP with JSON responses.

For ChatGPT app setup, follow [OpenAI's MCP server documentation](https://developers.openai.com/plugins/build/mcp-server). Local development requires a reachable HTTPS endpoint or a supported tunnel. This project exposes tools; it does not include an embedded app widget.

## API

`POST /generate_diagram`

| Field | Required | Description |
|---|---|---|
| `lang` | Yes | Source language, such as `plantuml`, `mermaid`, `d2`, or `graphviz` |
| `type` | Yes | Diagram type, such as `class`, `sequence`, or `flowchart` |
| `code` | Yes | Source text, between 1 and 100,000 characters; whitespace alone is rejected |
| `theme` | No | Renderer theme; UML-MCP validates supported themes |

The `mermaidjs`, `d2lang`, and `terrastruct` aliases remain accepted. Language names ignore case. Supported languages follow the allow-list in `kroki/kroki.py`.

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:5003/generate_diagram' -Method Post `
  -ContentType 'application/json' `
  -Body '{"lang":"mermaid","type":"flowchart","code":"graph TD; A-->B;"}'
```

The response contains `url`, `content`, and `playground`. Invalid requests return HTTP 422. Renderer failures return HTTP 502. Returning a URL does not establish that the image service will render every source successfully.

## UML-MCP backend

By default, requests call `generate_uml` on `https://uml-mcp.antoineboucher.info/mcp`. PlantUML requests use `type` as UML-MCP's diagram type; other languages use `lang`. The bridge requests SVG and preserves the original source in `content`.

To use your own UML-MCP deployment:

```powershell
$env:UML_MCP_URL = 'https://your-uml-server.example/mcp'
```

To use the original direct PlantUML, Mermaid and Kroki renderers:

```powershell
$env:UML_MCP_URL = ''
```

The bridge has a 30-second timeout. A configured backend failure returns HTTP 502. It does not silently send the request to another provider.

## Deployment

`vercel.json` routes requests to the FastAPI ASGI app. Runtime dependencies are in `requirements.txt`; development dependencies are in `requirements-dev.txt`. The Node build environment uses version 26.

Set `PUBLIC_BASE_URL` to your public HTTPS origin when deploying under another domain. It controls OpenAPI's server URL and the MCP host allow-list. Vercel deployment and production hostnames are included automatically. Use Python 3.14 on Vercel; CI also checks 3.15 independently of the hosting runtime.

The configured production URL is [openai-uml-plugin.vercel.app](https://openai-uml-plugin.vercel.app). Pushing code does not establish that its deployment is healthy; check `/health` and an MCP tool call after deployment.

## Verification

```powershell
.\.venv\Scripts\ruff.exe check app.py uml_backend.py test_modern_api.py
.\.venv\Scripts\python.exe -m pytest -q
```

Tests cover the HTTP contract, schema consistency, input validation, backend translation, renderer failures, and MCP initialization, discovery and generation. Original PlantUML helper tests contact the public renderer. The Linux-only D2 helper test is skipped on Windows.

MIT license. See [LICENSE](LICENSE) and [SECURITY.md](SECURITY.md).

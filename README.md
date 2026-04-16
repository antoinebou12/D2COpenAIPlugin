# D2COpenAIPlugin (Diagram2Code)

[![CI](https://github.com/antoinebou12/D2COpenAIPlugin/actions/workflows/CI.yml/badge.svg)](https://github.com/antoinebou12/D2COpenAIPlugin/actions/workflows/CI.yml)
[![GitHub stars](https://img.shields.io/github/stars/antoinebou12/D2COpenAIPlugin?style=flat&logo=github)](https://github.com/antoinebou12/D2COpenAIPlugin/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

**Diagram2Code** is a ChatGPT plugin backend that turns diagram source text into shareable URLs. It supports **PlantUML**, **Mermaid**, **D2**, and many other formats via **[Kroki](https://kroki.io/)**.

Production deployment: [https://openai-uml-plugin.vercel.app](https://openai-uml-plugin.vercel.app) (manifest: [`.well-known/ai-plugin.json`](https://openai-uml-plugin.vercel.app/.well-known/ai-plugin.json)).

> OpenAI’s classic **Plugins** surface is limited today; this repo remains useful as a **reference FastAPI + OpenAPI plugin** and for **local development** with compatible ChatGPT clients. See the [OpenAI developer forum](https://community.openai.com/c/chat-plugins/20) if you hit setup issues.

**Custom GPT:** [UML diagram creation expert](https://chat.openai.com/g/g-B1Bfoq5qh-uml-diagram-creation-expert)

---

## Screenshots

[![Diagram generator demo](https://raw.githubusercontent.com/antoinebou12/UMLOpenAIPlugin/main/docs/DiagramGeneratorPlugin.gif)](https://raw.githubusercontent.com/antoinebou12/UMLOpenAIPlugin/main/docs/DiagramGeneratorPlugin.gif)

![Diagram2Code example](https://github.com/antoinebou12/D2COpenAIPlugin/assets/13888068/638e6ef6-b006-4f63-a7b8-b765fc0d8a41)

---

## Features

- **PlantUML** — server-side render via PlantUML public server
- **Mermaid** — state encoding and Mermaid Live Editor links
- **D2** — optional local `D2/main` encoder + D2 render/playground URLs
- **Kroki-backed languages** — Graphviz, BPMN, Excalidraw, Vega, and [others](https://kroki.io/#supported-diagram-types) supported by this codebase’s allow-list in `app.py`
- **Static plugin assets** — OpenAPI spec, logo, and privacy policy under `/.well-known`

---

## Requirements

- **Python** 3.10+ (CI uses 3.12)
- **pip** and a virtual environment (recommended)

Optional:

- **`D2/main`** — small helper binary expected at `./D2/main` for D2 encoding in `D2/run_d2.py` (only needed if you use the D2 code paths locally)

---

## Quick start

```bash
git clone https://github.com/antoinebou12/D2COpenAIPlugin.git
cd D2COpenAIPlugin
python -m venv .venv
```

Activate the venv (Windows PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate the venv (macOS / Linux):

```bash
source .venv/bin/activate
```

Install dependencies and run the API:

```bash
pip install -r requirements-dev.txt
python -m pytest
uvicorn app:app --host 127.0.0.1 --port 5003
```

Equivalent one-liner after activation:

```bash
python app.py
```

Interactive API docs: [http://127.0.0.1:5003/](http://127.0.0.1:5003/) (FastAPI `docs_url`).

---

## API

`POST /generate_diagram`

JSON body:

| Field   | Type   | Required | Description |
|---------|--------|----------|-------------|
| `lang`  | string | yes      | e.g. `plantuml`, `mermaid`, `d2`, or a [Kroki](https://kroki.io/) type allowed by the server |
| `type`  | string | yes      | e.g. `class`, `sequence`, `activity` (used for validation / logging) |
| `code`  | string | yes      | Diagram source (max length enforced in `app.py`) |
| `theme` | string | no       | PlantUML / Mermaid theming where applicable |

Example (PlantUML) with **curl** (bash / Git Bash):

```bash
curl -s -X POST http://127.0.0.1:5003/generate_diagram -H "Content-Type: application/json" -d '{"lang":"plantuml","type":"sequence","code":"@startuml\nAlice -> Bob: hi\n@enduml"}'
```

Example with **PowerShell**:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5003/generate_diagram" -Method Post `
  -ContentType "application/json" `
  -Body '{"lang":"plantuml","type":"sequence","code":"@startuml\nAlice -> Bob: hi\n@enduml"}'
```

---

## Using the plugin in ChatGPT (localhost)

1. Run the server on **port 5003** (see above).
2. In ChatGPT, open **Plugins** → **Plugin store** → **Develop your own plugin**.
3. Enter `localhost:5003` and choose **Find manifest file** so ChatGPT loads `/.well-known/ai-plugin.json`.

Step-by-step screenshots: [docs/GUIDE.md](docs/GUIDE.md).

---

## Deployment (Vercel)

The app is configured for [Vercel](https://vercel.com/) with `@vercel/python` in [`vercel.json`](vercel.json). The production host used in the manifest is `https://openai-uml-plugin.vercel.app`.

---

## Repository layout (high level)

| Path | Role |
|------|------|
| `app.py` | FastAPI app, CORS, `/generate_diagram` |
| `.well-known/` | `ai-plugin.json`, `openapi.yaml`, logo, privacy |
| `plantuml/`, `mermaid/`, `D2/`, `kroki/` | Language-specific generation helpers |
| `docs/` | Extra guides and examples |

---

## Contributing / security

- Tests: `python -m pytest` (see [`.github/workflows/CI.yml`](.github/workflows/CI.yml))
- Security policy: [SECURITY.md](SECURITY.md)

---

## License

MIT — see [LICENSE](LICENSE).

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=antoinebou12/D2COpenAIPlugin&type=Date)](https://star-history.com/#antoinebou12/D2COpenAIPlugin&Date)

# 🔄 Diagram2Code (D2COpenAIPlugin)

[![Python application test with FastAPI and Pytest](https://github.com/antoinebou12/D2COpenAIPlugin/actions/workflows/python-app.yml/badge.svg)](https://github.com/antoinebou12/D2COpenAIPlugin/actions/workflows/python-app.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **Join the [ChatGPT plugins waitlist here](https://openai.com/waitlist/plugins)!**
> 
> [Try my GPT with the plugin](https://chat.openai.com/g/g-B1Bfoq5qh-uml-diagram-creation-expert)
> [Try my GPT with the plugin](https://chatgpt.com/g/g-B1Bfoq5qh-uml-diagram-expert)

Diagram2Code is a powerful diagramming service that enables AI assistants like ChatGPT to generate beautiful diagrams from text descriptions. The service supports multiple diagram languages and formats, making it easy to create everything from UML diagrams to flowcharts and network diagrams.

![Diagram Generator Plugin Demo](https://raw.githubusercontent.com/antoinebou12/UMLOpenAIPlugin/main/docs/DiagramGeneratorPlugin.gif)

## 🌟 Features

- **Multi-format Diagram Generation**
  - PlantUML for UML diagrams (class, sequence, activity, etc.)
  - Mermaid for flowcharts, sequence diagrams, and more
  - D2 for modern, code-based diagrams
  - 25+ additional formats through Kroki integration

- **Integration Options**
  - OpenAI Plugin API for ChatGPT integration
  - MCP Server for Claude and Cursor integration 
  - Standalone usage via API endpoints

- **Developer-Friendly**
  - Clean, documented codebase
  - Comprehensive CLI with rich formatting
  - Easy deployment options

## 📋 Project Structure

```
├── D2/                  # D2 diagram integration
├── kroki/               # Kroki integration and templates
├── mermaid/             # Mermaid diagram support
├── plantuml/            # PlantUML diagram support
├── docs/                # Documentation and examples
├── app.py               # FastAPI server for OpenAI Plugin
├── main.py              # Primary entry point
└── requirements.txt     # Project dependencies
```

## 🔧 Prerequisites

- Python 3.8+ (3.10+ recommended)
- pip or poetry for dependency management

## 📦 Installation

### Option 1: Using pip (Quick Setup)

```bash
# Clone the repository
git clone https://github.com/antoinebou12/D2COpenAIPlugin.git
cd D2COpenAIPlugin

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using poetry (Recommended for Development)

```bash
# Install poetry if you don't have it
pip install poetry

# Clone the repository
git clone https://github.com/antoinebou12/D2COpenAIPlugin.git
cd D2COpenAIPlugin

# Create a virtual environment with Python 3.10
poetry env use python3.10

# Activate the virtual environment
poetry shell

# Install dependencies
poetry install
```

## 🚀 Running the Server

The project offers multiple ways to run the server to fit different use cases:

### 🔄 All-in-One Command

```bash
# Run the API server
python main.py api
```

### 💬 ChatGPT Plugin Server Only

```bash
# Run with the CLI
python main.py api

# Or run with uvicorn directly
uvicorn app:app --host 127.0.0.1 --port 5003

# Or use the app's convenience function
python app.py
```

## 📊 Supported Diagram Types

The service supports a wide range of diagram types through various backends:

### PlantUML

Create UML diagrams including class, sequence, activity, component, state, object, and use case diagrams.

**Example:**
```
@startuml
class User {
  -id: Long
  -username: String
  +login(): boolean
}
class Post {
  -id: Long
  -content: String
  +publish()
}
User "1" -- "n" Post: creates
@enduml
```

### Mermaid

Generate flowcharts, sequence diagrams, class diagrams, state diagrams, and more.

**Example:**
```
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B
```

### D2

Create modern diagrams with code-based descriptions.

**Example:**
```
# System Architecture
client -> load-balancer: Request
load-balancer -> api: Forward
api -> database: Query
database -> api: Response
api -> load-balancer: Response
load-balancer -> client: Response
```

### Additional Formats (via Kroki)

The service also supports many other formats through Kroki integration:
- BlockDiag, SeqDiag, ActDiag
- GraphViz/DOT
- C4 with PlantUML
- Vega/Vega-Lite
- And many more!

## 🔌 Connecting with AI Assistants

### Setting up with ChatGPT

1. Navigate to https://chat.openai.com
2. In the Model dropdown, select "Plugins"
3. Select "Plugin store"
4. Select "Develop your own plugin"
5. Enter `localhost:5003` and select "Find manifest file"

The plugin should now be installed and enabled! You can start with prompts like:
- "Create a sequence diagram for user authentication"
- "Generate a class diagram for a blog system"

## 🧪 Testing

Run the test suite to ensure everything is working properly:

```bash
# Run tests with pytest
python -m pytest

# Or with coverage reporting
python -m pytest --cov=.
```

## 🛠️ Development

Want to contribute? Here's how to set up the development environment:

```bash
# Clone the repository
git clone https://github.com/antoinebou12/D2COpenAIPlugin.git
cd D2COpenAIPlugin

# Install dev dependencies
pip install -r requirements-dev.txt

# Run the linter
flake8

# Format code
black .
```

## 📚 Documentation

Additional documentation can be found in the `docs/` directory:
- [User Guide](docs/GUIDE.md)
- [Chat Examples](docs/ChatEXAMPLE.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Contact

If you have any questions or suggestions, please open an issue on GitHub.

---

<p align="center">
  <small>Made with ❤️ by Antoine Boucher</small>
</p>
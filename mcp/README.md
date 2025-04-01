# UML-MCP-Server

UML diagram generation server using MCP (Model Context Protocol) for integration with AI assistants like Claude.

## Features

- Generate UML diagrams directly from Claude, Cursor, or other MCP clients
- Support for multiple diagram types:
  - Class diagrams
  - Sequence diagrams
  - Activity diagrams
  - Use case diagrams
  - State diagrams
  - Component diagrams
  - Deployment diagrams
  - Object diagrams
- Integration with additional diagram formats through Kroki:
  - Mermaid
  - D2
  - Graphviz
  - ERD
  - And many more
- Returns URLs, playground links, and local file paths

## Installation

### Using Smithery

The easiest way to install UML-MCP-Server is using Smithery:

```bash
npx -y @smithery/cli install @antoinebou12/uml-mcp-server --client claude
```

### Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/antoinebou12/D2COpenAIPlugin.git
   cd D2COpenAIPlugin
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r mcp/mcp-requirements.txt
   ```

3. Install for your IDE:
   ```bash
   python mcp/install_to_cursor.py
   ```

## Usage

Once installed, you can use UML-MCP-Server through Claude Desktop, Cursor, or any other MCP-compliant client.

### Example Prompts

Try asking your AI assistant:
- "Create a class diagram for a library management system"
- "Generate a sequence diagram for user authentication flow"
- "Make a state diagram for an order processing system"

## Docker Usage

You can also run UML-MCP-Server using Docker:

```bash
docker-compose up diagram-mcp
```

## Documentation

For more information, see the main project documentation at:
https://github.com/antoinebou12/D2COpenAIPlugin

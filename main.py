"""
Main entry point for D2COpenAIPlugin.

This script provides commands for running the FastAPI server
with a rich command-line interface.
"""

import sys
import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

app = typer.Typer(
    help="🔄 Diagram2Code CLI - Generate diagrams with OpenAI",
    rich_markup_mode="rich",
)
console = Console()

# Version information
__version__ = "1.2.0"

# Utility class for CLI helpers
class CLIHelpers:
    @staticmethod
    def print_server_header(title, color):
        """Print a header for the server with nice formatting."""
        console.print(Panel(f"[bold {color}]{title}[/bold {color}]", expand=False))
    
    @staticmethod
    def print_server_url(host, port):
        """Print formatted server URL."""
        display_host = "localhost" if host in ("0.0.0.0", "127.0.0.1") else host
        console.print(f"[green]Server running at:[/green] http://{display_host}:{port}")
    
    @staticmethod
    def print_diagram_capabilities():
        """Print information about supported diagram types."""
        table = Table(title="Supported Diagram Types")
        table.add_column("Type", style="cyan")
        table.add_column("Description", style="green")
        
        table.add_row("PlantUML", "UML diagrams, including class, sequence, activity diagrams")
        table.add_row("Mermaid", "Flowcharts, sequence diagrams, Gantt charts")
        table.add_row("D2", "Modern, code-based diagrams")
        table.add_row("Kroki", "25+ additional formats (GraphViz, C4, etc.)")
        
        console.print(table)

CLI_HELPERS = CLIHelpers()

@app.command()
def api(
    host: str = typer.Option("localhost", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(5003, "--port", "-p", help="Port to listen on"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload for development"),
):
    """🌐 Run the FastAPI server with OpenAI Plugin support."""    
    
    CLI_HELPERS.print_server_header(f"Diagram2Code API Server v{__version__}", "green")
    CLI_HELPERS.print_server_url(host, port)
    
    # Import app here to avoid circular imports
    from app import app as fastapi_app
    
    # Configure uvicorn settings
    try:
        uvicorn.run(
            fastapi_app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        console.print("[bold yellow]Server stopped by user[/bold yellow]")

@app.command()
def dev(
    port: int = typer.Option(5003, "--port", "-p", help="Port to listen on"),
    open_browser: bool = typer.Option(True, "--open-browser/--no-browser", help="Open browser automatically"),
):
    """🧪 Run in development mode with auto-reloading and Swagger UI."""    
    
    CLI_HELPERS.print_server_header("Diagram2Code in Development Mode", "cyan")
    CLI_HELPERS.print_server_url("localhost", port)
    console.print("[yellow]Use the browser to interactively test the API endpoints[/yellow]")
    
    # Configure uvicorn settings for development
    uvicorn_config = {
        "app": "app:app",
        "host": "localhost",
        "port": port,
        "reload": True,
        "reload_dirs": [".", "app", "kroki", "plantuml", "mermaid", "D2"],
        "log_level": "debug"
    }
    
    # Open browser if requested
    if open_browser:
        import webbrowser
        console.print("[dim]Opening browser...[/dim]")
        webbrowser.open(f"http://localhost:{port}")
    
    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        console.print("[bold yellow]Development server stopped by user[/bold yellow]")

@app.command()
def info():
    """ℹ️ Display information about the available services."""    
    CLI_HELPERS.print_server_header(f"Diagram2Code v{__version__}", "cyan")
    
    # Create table for services
    table = Table(title="Available Services")
    table.add_column("Service", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Command", style="yellow")
    
    table.add_row(
        "API Server", 
        "FastAPI server with OpenAI plugin support",
        "python main.py api"
    )
    table.add_row(
        "Development", 
        "Run with auto-reload and Swagger UI",
        "python main.py dev"
    )
    
    console.print(table)
    
    # Display diagram capabilities
    CLI_HELPERS.print_diagram_capabilities()
    
    # Display usage instructions
    console.print(Markdown("""
    ## Usage with ChatGPT
    
    To use with ChatGPT, run the API server and configure as a plugin:
    
    ```bash
    python main.py api
    ```
    
    Then navigate to ChatGPT, go to Plugin Store, select "Develop your own plugin",
    and enter `localhost:5003` as the plugin URL.
    """))

@app.command()
def version():
    """📋 Show version information."""    
    console.print(f"Diagram2Code v{__version__}")
    console.print(f"Python {sys.version.split()[0]}")
    
    # Try to get dependency versions
    try:
        import fastapi
        console.print(f"FastAPI {fastapi.__version__}")
    except (ImportError, AttributeError):
        pass

if __name__ == "__main__":
    app()

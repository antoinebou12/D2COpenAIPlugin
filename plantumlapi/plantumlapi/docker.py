"""Start Server PlantUML

Usage:
    pyplantuml start-server [options]

Options:
    -h --help               Show this screen.
    --host=<host>           Host to listen on [default:
    --port=<port>           Port to listen on [default: 8080]
    --tomcat
    --jetty
    --volume=<volume>       Volume to mount
"""

import os
import sys
import typer
import docker
import logging

from . import __version_string__

app = typer.Typer()
logger = logging.getLogger(__name__)

@app.command(
    help='Start PlantUML Server'
)
def start_server(
    host: str = '0.0.0.0',
    port: int = 8080,
    tomcat: bool = False,
    jetty: bool = True,
    volume: str = None
) -> None:
    """
    Start PlantUML Server
    docker run -d -p 8080:8080 plantuml/plantuml-server:jetty
    """

    if not volume:
        # create volume
        volume = os.path.join(os.getcwd(), 'plantuml')

    if not os.path.exists(volume):
        os.makedirs(volume)

    if tomcat:
        server = 'plantuml/plantuml-server:tomcat'
    elif jetty:
        server = 'plantuml/plantuml-server:jetty'
    else:
        server = 'plantuml/plantuml-server'

    client = docker.from_env()
    container = client.containers.run(
        server,
        detach=True,
        ports={8080: port},
        environment={
            'PUML_LIMIT_SIZE': 8192
        }
    )
    typer.echo(f"PlantUML Server started on http://{host}:{port}")

@app.command(
    help='Stop PlantUML Server'
)
def stop_server() -> None:
    """
    Stop PlantUML Server
    """
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if 'plantuml' in container.image.tags:
            container.stop()
            typer.echo("PlantUML Server stopped")

@app.command(
    help='Show PlantUML Server status'
)
def status_server() -> None:
    """
    Show PlantUML Server status
    """
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if 'plantuml' in container.image.tags:
            typer.echo(f"PlantUML Server status: {container.status}")

@app.command(
    help='Show PlantUML Server logs'
)
def logs_server() -> None:
    """
    Show PlantUML Server logs
    """
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if 'plantuml' in container.image.tags:
            typer.echo(f"PlantUML Server logs: {container.logs()}")

@app.command(
    help='restart PlantUML Server'
)
def restart_server() -> None:
    """
    restart PlantUML Server
    """
    client = docker.from_env()
    containers = client.containers.list()
    for container in containers:
        if 'plantuml' in container.image.tags:
            container.restart()
            typer.echo("PlantUML Server restarted")

if __name__ == '__main__':
    app(
        prog_name='pyplantuml',
        help='PlantUML CLI'
    )



# PlantumlApi

Python interface with the PlantUML web. PlantUML is a library for generating UML diagrams from a simple text markup language.

PyPlantUML is a simple remote client interface to a PlantUML server using the same custom encoding used by most other PlantUML clients.

This client defaults to the public PlantUML server but can be used against any server.

## Installation

To install, run the following command:

```bash
pip install plantumlapi
```

```bash
pip install git+https://github.com/antoinebou12/plantumlapi
```

## Command Line Usage

```bash
usage: plantuml.py [-h] [-o OUT] [-s SERVER] filename [filename ...]

Generate images from PlantUML defined files using PlantUML server

positional arguments: 
  filename            file(s) to generate images from

optional arguments: 
  -h, --help          show this help message and exit 
  -o OUT, --out OUT   directory to put the files into 
  -s SERVER, --server SERVER 
                      server to generate from; defaults to plantuml.com 
```

## Usage

```python
from plantumlapi.plantumlapi import PlantUML

# Create a PlantUML object, set the output directory and server
p = PlantUML(url="https://www.plantuml.com/plantuml/duml/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000")

# Generate a diagram from a string
p.process("@startuml\nclass Foo\n@enduml")

```

## Docker

```bash
docker run -d -p 8080:8080 plantuml/plantuml-server:jetty
```

```
from pyplantuml import PlantUML

# Create a PlantUML object, set the output directory and server
p = PlantUML(url="http://localhost:8080/png")

# Generate a diagram from a string
p.process("@startuml\nclass Foo\n@enduml")
```

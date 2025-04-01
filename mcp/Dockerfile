# This is a specialized Dockerfile for the MCP server component only
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    golang \
    graphviz \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY ../requirements.txt .
COPY mcp-requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r mcp-requirements.txt

# Create output and logs directories
RUN mkdir -p output logs

# Copy only MCP server files
COPY mcp /app/mcp
COPY mcp_server.py .
COPY kroki /app/kroki
COPY D2 /app/D2
COPY plantuml /app/plantuml
COPY mermaid /app/mermaid

# Set environment variables
ENV PYTHONPATH=/app
ENV D2_PATH=/usr/local/bin/d2
ENV MCP_OUTPUT_DIR=/app/output
ENV PLANTUML_SERVER=http://plantuml-server:8080

# Install D2
RUN curl -fsSL https://d2lang.com/install.sh | sh -s --

# Run MCP server
ENTRYPOINT ["python", "mcp_server.py"]
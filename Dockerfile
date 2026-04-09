# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
# git is needed for the toolsmith_github_sync tool
# node is requested for MCP ecosystem compatibility
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create and set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies using uv
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the application code
# We structure it so that 'aether' is a package in the PYTHONPATH (/app)
COPY . /app/aether/

# Ensure the tools and sandbox directories exist
RUN mkdir -p /app/aether/tools/sandbox

# Set execution environment variables
ENV AETHER_ROOT=/app/aether
ENV TOOLS_DIR=/app/aether/tools
ENV PORT=8080
ENV MCP_TRANSPORT=sse

# Expose the port for SSE transport
EXPOSE 8080

# Set the entrypoint to run the MCP server
ENTRYPOINT ["python", "/app/aether/toolsmith_mcp_server.py"]

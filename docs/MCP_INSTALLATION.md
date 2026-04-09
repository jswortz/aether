# 🛠️ MCP Installation & Setup Guide

This guide explains how to install and configure MCP servers for the Aether swarm.

## 1. Prerequisites
- Python 3.10+
- `uv` (recommended for dependency management)
- Node.js 20+ (for Claude Code)
- Google Cloud SDK (`gcloud`)

## 2. Installing the Toolsmith MCP
The Toolsmith MCP is the core builder for the Aether swarm.

```bash
# Clone the repo
git clone https://github.com/jswortz/aether.git
cd aether

# Install dependencies
uv pip install -r requirements.txt
```

## 3. Configuration
MCP servers in Aether use environment variables for configuration.

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | Token for repo syncing | (Required) |
| `MCP_TRANSPORT` | Transport mode (`stdio` or `sse`) | `sse` |
| `PORT` | Port for SSE transport | `8080` |
| `AETHER_ROOT` | Root directory for the project | `/app` |

## 4. Running Locally
To run the Toolsmith MCP server locally in `stdio` mode:
```bash
export MCP_TRANSPORT=stdio
python3 toolsmith_mcp_server.py
```

To run in `sse` mode (for Cloud Run emulation):
```bash
export MCP_TRANSPORT=sse
export PORT=8080
python3 toolsmith_mcp_server.py
```

## 5. Integrating Claude on Vertex
The Aether swarm uses Claude 3.5 Sonnet on Vertex AI for high-fidelity reasoning.

```bash
# Ensure Vertex AI API is enabled
gcloud services enable aiplatform.googleapis.com

# Set up ADC (Application Default Credentials)
gcloud auth application-default login
```

The `claude_vertex_mcp.py` server will automatically use your GCP credentials to invoke Claude.

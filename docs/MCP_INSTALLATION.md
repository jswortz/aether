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

## 5. Connecting to MCP Clients (How to use as a Tool)
Project Aether acts as a high-performance MCP server. You can add it to any MCP-compatible client to give your LLM "Aetherial Powers."

### A. Claude Desktop Integration
Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aether-toolsmith": {
      "command": "python3",
      "args": ["/absolute/path/to/aether/toolsmith_mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "your_token_here",
        "AETHER_ROOT": "/absolute/path/to/aether",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### B. Connecting via SSE (Cloud Run)
If you have deployed Aether to Cloud Run, connect using the SSE transport:
```json
{
  "mcpServers": {
    "aether-remote": {
      "url": "https://your-aether-service-url.a.run.app/sse"
    }
  }
}
```

## 6. Available Tools (What the LLM sees)
Once connected, Aether provides the following tools to the LLM:

| Tool Name | Practical Usage |
|-----------|-----------------|
| `toolsmith_synthesize` | Generates new Python code to fill capability gaps. |
| `toolsmith_execute` | Securely runs synthesized code in a sandbox. |
| `router_register` | Registers a new tool with the Agent Router. |
| `router_route` | Finds the best specialist for a specific task. |
| `toolsmith_add_memory` | Injects high-signal facts into Aetherial Memory (via Surprise Gate). |
| `toolsmith_github_sync` | Pushes evolved code directly to your repository. |

## 7. Integrating Claude on Vertex
...

The Aether swarm uses Claude 3.5 Sonnet on Vertex AI for high-fidelity reasoning.

```bash
# Ensure Vertex AI API is enabled
gcloud services enable aiplatform.googleapis.com

# Set up ADC (Application Default Credentials)
gcloud auth application-default login
```

The `claude_vertex_mcp.py` server will automatically use your GCP credentials to invoke Claude.

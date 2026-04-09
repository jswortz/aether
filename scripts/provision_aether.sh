#!/bin/bash
# provision_aether.sh - Environment setup for Project Aether on GCP Compute Engine
# 
# Usage: 
#   export GITHUB_TOKEN=your_token
#   sudo -E ./provision_aether.sh
#

set -euo pipefail

# 1. System Updates & Dependencies
echo "Installing system dependencies..."
apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    python3-pip \
    python3-venv \
    software-properties-common

# 2. Install 'uv' for Python dependency management
echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# 3. Install Node.js (required for Claude Code CLI)
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# 4. Install Claude Code CLI
echo "Installing Claude Code CLI..."
npm install -g @anthropic-ai/claude-code

# 5. Set up Project Aether Environment
AETHER_HOME="/opt/aether"
if [ ! -d "$AETHER_HOME" ]; then
    echo "Creating Aether home at $AETHER_HOME..."
    mkdir -p "$AETHER_HOME"
    # Assuming the script is run from within the repo or we clone it
    # If we are in the repo, copy it
    if [ -f "pyproject.toml" ]; then
        cp -r . "$AETHER_HOME/"
    fi
fi

cd "$AETHER_HOME"

# Initialize uv environment
echo "Initializing Python environment with uv..."
uv venv
source .venv/bin/activate
uv sync

# 6. Configure Environment Variables
# Using /etc/aether.env to store configuration
ENV_FILE="/etc/aether.env"
cat <<EOF > "$ENV_FILE"
GITHUB_TOKEN=${GITHUB_TOKEN:-""}
MCP_TRANSPORT=sse
AETHER_HOME=$AETHER_HOME
PYTHONPATH=$AETHER_HOME
EOF

# Secure the env file
chmod 600 "$ENV_FILE"

# 7. Create systemd service for Toolsmith MCP Server
echo "Configuring systemd service for Toolsmith MCP..."
SERVICE_USER=${SUDO_USER:-$(whoami)}
echo "Using user $SERVICE_USER for service."

cat <<EOF > /etc/systemd/system/aether-toolsmith.service
[Unit]
Description=Aether Toolsmith MCP Server
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$AETHER_HOME
EnvironmentFile=$ENV_FILE
ExecStart=$AETHER_HOME/.venv/bin/python toolsmith_mcp_server.py sse
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable aether-toolsmith.service
# systemctl start aether-toolsmith.service # Let the user start it after verifying config

echo "Provisioning complete."
echo "Please verify /etc/aether.env and run 'sudo systemctl start aether-toolsmith.service'"
echo "To initialize Claude Code, run: claude auth login"

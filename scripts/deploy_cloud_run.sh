#!/bin/bash
# deploy_cloud_run.sh: Automates Project Aether deployment to Cloud Run as a Serverless MCP service.

set -euo pipefail

# Configuration
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-"us-central1"}

SERVICES=("aether-toolsmith-mcp" "claude-vertex-mcp")
ENTRYPOINTS=("toolsmith_mcp_server.py" "claude_vertex_mcp.py")
PORTS=(8080 8081)

echo "--- Aether Cloud Run Multi-Service Deployment ---"

# Navigate to project root
cd "$(dirname "$0")/.."

# 1. Build common base image
echo "Step 1: Building base image with Cloud Build..."
IMAGE_TAG="gcr.io/${PROJECT_ID}/aether-base:latest"
gcloud builds submit --tag "${IMAGE_TAG}" .

# 2. Deploy each service
for i in "${!SERVICES[@]}"; do
    SERVICE_NAME="${SERVICES[$i]}"
    ENTRYPOINT="${ENTRYPOINTS[$i]}"
    PORT="${PORTS[$i]}"
    
    echo "--- Deploying ${SERVICE_NAME} ---"
    
    gcloud run deploy "${SERVICE_NAME}" \
        --image "${IMAGE_TAG}" \
        --platform managed \
        --region "${REGION}" \
        --allow-unauthenticated \
        --port "${PORT}" \
        --command "python3" \
        --args "/app/aether/${ENTRYPOINT}" \
        --set-env-vars "AETHER_ROOT=/app/aether,TOOLS_DIR=/app/aether/tools,PYTHONPATH=/app:/app/aether,MCP_TRANSPORT=sse" \
        --memory 2Gi \
        --cpu 1
    
    URL=$(gcloud run services describe "${SERVICE_NAME}" --platform managed --region "${REGION}" --format='value(status.url)')
    echo "${SERVICE_NAME} URL: ${URL}/sse"
done

echo "--- All Deployments Complete ---"

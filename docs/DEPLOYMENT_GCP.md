# Project Aether: GCP Deployment Strategy (Serverless Cloud Run)

This document outlines the strategy for deploying Project Aether as a serverless MCP service using Google Cloud Run. This approach provides auto-scaling, built-in SSE support, and reduced operational overhead.

## 1. Infrastructure Requirements

### Cloud Run Service
- **Platform**: Fully Managed
- **Region**: `us-central1` (recommended for low latency to Vertex AI)
- **Memory**: 2 GiB (minimum for analytical/agentic loads)
- **CPU**: 1 vCPU
- **Port**: 8080 (Mapped to the `PORT` environment variable)

### IAM Roles
The Cloud Run service account must have the following roles:
- **Vertex AI User** (`roles/aiplatform.user`): For Gemini model invocation.
- **Artifact Registry Writer** (`roles/artifactregistry.writer`): For storing container images.
- **Cloud Build Editor** (`roles/cloudbuild.builds.editor`): For automated image builds.

## 2. Containerization

Project Aether uses a `Dockerfile` that packages the application logic with its dependencies.

### Key Components:
- **Base Image**: `python:3.11-slim`
- **Dependency Manager**: `uv` (for rapid Python package installation)
- **System Deps**: `git`, `curl`, `nodejs` (v20)
- **MCP Transport**: Configured for SSE (Server-Sent Events)

## 3. Automated Deployment

We provide a `scripts/deploy_cloud_run.sh` script that automates the build and deployment process.

### Execution:
1. Ensure your `gcloud` CLI is authenticated and the project is set.
2. Run the deployment script:

```bash
./scripts/deploy_cloud_run.sh
```

The script performs the following:
- Builds the container image using **Cloud Build**.
- Pushes the image to **Google Container Registry**.
- Deploys the service to **Cloud Run** with appropriate environment variables:
    - `AETHER_ROOT`: Path to the project root in the container.
    - `TOOLS_DIR`: Path to the tools directory.
    - `MCP_TRANSPORT`: Defaults to `sse`.
    - `PYTHONPATH`: Set to `/app` to ensure the `aether` package is importable.

## 4. Toolsmith MCP Server Configuration

The Toolsmith MCP server is the primary interface for tool synthesis and registration within the SCION pattern.

### SSE Endpoint:
Once deployed, the service exposes an SSE endpoint at:
`https://<SERVICE_URL>/sse`

### Surprise Gate Integration:
The server maintains the "Surprise Gate" logic to filter out low-signal memory updates. This ensures the serverless instance remains focused on high-bandwidth, high-impact data without context poisoning.

## 5. Security & Constraints

- **Forbidden Names**: Never hardcode retail client names (e.g., Kroger, HEB). Use parameterization through environment variables.
- **Authentication**: By default, the deployment script uses `--allow-unauthenticated` for demo purposes. For production use, configure Cloud IAM for service-to-service authentication.
- **Secrets Management**: Use **Secret Manager** to inject sensitive values like `GITHUB_TOKEN` as environment variables instead of hardcoding them in the source.

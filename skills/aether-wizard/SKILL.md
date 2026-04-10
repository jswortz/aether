---
name: aether-wizard
description: Interactive installation and setup wizard for Project Aether. Use when the user wants to "install Aether", "setup the swarm", or "configure Aether as a wizard". Guides through repo cloning, dependency installation, GCP configuration, and Cloud Run deployment.
---

# Aether Installation Wizard

This skill guides you through the full installation and initialization of Project Aether—the autonomous SCION-Router swarm.

## 🚀 Interactive Setup Steps

When this skill is activated, follow these clinical steps to instantiate the swarm:

### 1. Repository Instantiation
Ensure you are in the target parent directory.
```bash
git clone https://github.com/jswortz/aether.git
cd aether
```

### 2. Dependency Infusion
Install the core execution and orchestration dependencies.
```bash
pip install -r requirements.txt
```

### 3. Environment Synchronization
Aether requires critical credentials for autonomous evolution.
- **GITHUB_TOKEN**: Required for the Toolsmith to sync evolved code.
- **GOOGLE_CLOUD_PROJECT**: Required for Vertex AI and Cloud Run.

```bash
export GITHUB_TOKEN=your_pat_here
export GOOGLE_CLOUD_PROJECT=your_project_id
```

### 4. Execution Plane Deployment
Deploy the specialized MCP workers to Google Cloud Run. This command builds the base image and deploys the Toolsmith and Claude Vertex services.
```bash
bash scripts/deploy_cloud_run.sh
```

### 5. Verification Dialectic
Run the core logic tests to ensure the architectural integrity of the routing and memory layers.
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/test_aether_core.py tests/test_model_skill_routing.py
```

## 🛠️ Verification Checklist
- [ ] `aether-toolsmith-mcp` service is live on Cloud Run.
- [ ] `claude-vertex-mcp` service is live on Cloud Run.
- [ ] Core tests passed (100% success rate).
- [ ] `GRAND_MANIFESTO.md` has been reviewed.

---
**The swarm is now active. Trust the evolution.**

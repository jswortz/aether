# 🪐 Project Aether: Autonomous SCION-Router Swarm

**STOP CHATTING. START ORCHESTRATING.**

Aether is a next-generation agentic framework designed for high-stakes, multi-step autonomous work. It moves beyond the "helpful assistant" paradigm to a clinical, goal-oriented execution engine that identifies its own capability gaps and evolves its own toolset.

## 🚀 Practical Utility: What does Aether actually do?

Aether is an **autonomous builder** and **orchestrator**. It is designed to:
- **Self-Evolve**: Identify missing technical capabilities and synthesize new Python/MCP tools on-the-fly via the **Toolsmith**.
- **Optimize Model-Skill Selection**: Automatically route tasks to the best model (e.g., Gemini for speed, Claude for reasoning) based on intent and complexity.
- **Dispatch at Scale**: Route semantic intent to the optimal specialist in milliseconds using a high-bandwidth **Agent Router**.
- **Serverless Execution**: Run a fleet of specialized workers as serverless **Cloud Run** services.
- **Protect Context**: Use a **Surprise Gate** to filter noise and ensure only high-signal data enters the reasoning loop.

## 🏛️ Architecture: The SCION-Router Pattern

Aether strictly separates the **Control Plane** (Brain) from the **Execution Plane** (Swarm):

- **Control Plane (Supervisor/Router)**: Centralized management of mission goals, intent routing, and Aetherial Memory.
- **Execution Plane (MCP Workers)**: A decentralized swarm of specialists (Toolsmith, Claude Vertex, Reflection Agents) running in isolated containers.

For a deep dive, see **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** and **[AGENTS.md](AGENTS.md)**.

## 🛠️ Installation

### 1. Local Setup
```bash
# Clone and install
git clone https://github.com/jswortz/aether.git
cd aether
pip install -r requirements.txt

# Configure environment
export GITHUB_TOKEN=your_token
export GOOGLE_CLOUD_PROJECT=your_project
```

### 2. Cloud Run Deployment (Serverless Swarm)
Deploy the entire execution plane with one command:
```bash
bash scripts/deploy_cloud_run.sh
```

## 🎯 Core Use Cases

### 1. Autonomous Bug Fixing
The Supervisor identifies a failure, the **Model-Skill Router** upgrades the task to `claude-3-5-sonnet` for its high-fidelity reasoning, and the worker invokes `claude code` to refactor the fix.

### 2. Dynamic Skill Expansion
When Aether needs a specialized tool (e.g., a BigQuery complexity analyzer), the **Toolsmith** synthesizes the script, tests it in a sandbox, and registers it with the Router for immediate use.

### 3. High-Fidelity Architectural Review
By using **Adversarial Debaters** (Proponent/Critic), Aether subjects every architectural proposal to rigorous peer review before finalization.

## 📖 Instructions & Examples

### Registering a Tool with Model-Skill Optimization
```python
from core.router import AgentRouter

router = AgentRouter()
router.register_tool(
    intent="architectural review",
    tool_name="architect",
    path="/app/tools/architect.py",
    score=1.0,
    preferred_model="claude-3-5-sonnet-v2" # Explicit high-fidelity request
)
```

### Routing an Intent (Auto-Upgrade Logic)
```python
# Aether detects "analyze" and automatically recommends a high-reasoning model
results = router.route("analyze the security of this protocol")
# results[0]["recommended_model"] -> "claude-3-5-sonnet-v2"
```

### Starting the Toolsmith MCP
```bash
export MCP_TRANSPORT=sse
python3 toolsmith_mcp_server.py
```

## 🧪 Testing & Verification
Aether includes a rigorous test suite to ensure technical integrity:
```bash
# Run core logic and routing tests
pytest tests/test_aether_core.py
pytest tests/test_model_skill_routing.py

# Verify GCP model connectivity (requires GOOGLE_CLOUD_PROJECT)
pytest tests/test_model_connectivity.py
```

---
**Build for the swarm. Trust the evolution. Welcome to Aether.**

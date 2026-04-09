# Getting Started: The Aether Way

This is the definitive workflow for running Project Aether. Follow this strictly to ensure the swarm operates at peak efficiency.

## 1. The Environment
Aether requires `uv` for lightning-fast dependency management and a provisioned BigQuery dataset ("The Oracle") for telemetry.

```bash
# Initialize the Aether environment
uv sync
export GOOGLE_CLOUD_PROJECT="your-project"
export BQ_DATASET="aether_oracle"
```

## 2. The First Run: Headless Command
Do not launch the CLI. Launch the **Orchestrator**. Provide a high-level goal and walk away.

```bash
# The correct way to invoke Aether
export PYTHONPATH=.
python3 -m aether.orchestrator --goal "Map the dependency graph of this repo and synthesize a visualization tool"
```

## 3. The Reflection Loop: HITL Steering
Aether will generate report samples via GitHub MCP. Review these in the "Aether Discovery" tab. If the swarm is drifting, provide **Voice Feedback** (Text Transcripts).

**Example Steering:**
> "The Toolsmith is being too verbose in its docstrings. Optimize for execution speed."

This will trigger an **Adversarial Debate** to refactor the `toolsmith_worker` instructions.

## 4. Monitoring the Swarm
Check "The Oracle" (BigQuery) to see your **Evolution Velocity**. 
- **Score < 0.8?** Trigger a refinement cycle.
- **Latency > 30s per step?** Trigger a Trajectory Compression.
- **Agent Stuck?** Ensure the `Prodder` is active in the orchestrator config.

## 5. Adding Workers
If you need a new domain expert (e.g., a "Security Auditor"), do not write a new agent from scratch. Use the `aether_worker_template.md` and let the **Supervisor** integrate it into the next run.

---
**Remember: You are the Architect. Aether is the Swarm. Stop chatting and start orchestrating.**

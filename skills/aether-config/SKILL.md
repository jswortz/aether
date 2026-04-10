---
name: aether-config
description: Configuration and management skill for Project Aether. Use as a tool to "register a new capability", "update worker capability scores", "modify routing logic", or "configure model preferences". Provides a programmatic interface for the Agent Router.
---

# Aether Configuration Tool

This skill allows you to programmatically configure the Aether swarm's routing table and worker preferences.

## 🏹 Tool: Register Capability

Use the following Python pattern to register or update a tool in the **Agent Router**.

### Example: Registering a Security Specialist
```python
from core.router import AgentRouter

router = AgentRouter()
router.register_tool(
    intent="perform security audit and scan for vulnerabilities",
    tool_name="sentinel_v1",
    path="/app/tools/sentinel.py",
    score=0.95,
    preferred_model="claude-3-5-sonnet-v2" # High-fidelity reasoning required
)
```

## 🧠 Model-Skill Preferences

Aether supports high-fidelity model auto-upgrades. When configuring a tool, consider these best practices:
- **Fast Execution (Default)**: `gemini-2.0-flash` for deterministic code tasks, basic synthesis, and file operations.
- **High-Fidelity Reasoning**: `claude-3-5-sonnet-v2` for architectural review, security audits, and complex debugging.

## 📊 Managing WC Scores

The **Worker Capability (WC) Score** determines routing priority:
- **1.0**: Verified, production-grade specialist.
- **0.5**: Experimental tool synthesized by the Toolsmith.
- **0.1**: Degraded or untrusted capability.

To update a score, simply re-register the tool with the new value.

## 📡 Environment Configuration

Aether relies on these core variables:
- `AETHER_ROOT`: Absolute path to the repository.
- `TOOLS_DIR`: Directory where the Toolsmith persists new capabilities.
- `MCP_TRANSPORT`: Set to `sse` for Cloud Run or `stdio` for local.

---
**Configure with precision. Build for the swarm.**

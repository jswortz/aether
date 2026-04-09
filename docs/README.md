# Project Aether: Autonomous SCION Orchestration

**STOP CHATTING. START ORCHESTRATING.**

Aether is a next-generation agentic framework built on the **SCION (Supervisor-Worker)** pattern. It is designed for high-stakes, multi-step autonomous work where "human-in-the-loop" is a bottleneck to be optimized, not a feature to be celebrated.

## 🌌 Core Philosophy
Before you touch the code, read **[The Aether Manifesto](../MANIFESTO.md)**. 

Aether treats agents as an evolving swarm. It does not just "run tasks"; it identifies its own capability gaps, synthesizes its own tools, and refines its own instructions via adversarial debate.

## 🚀 The Workflow
See **[Getting Started: The Aether Way](../GETTING_STARTED.md)** for the definitive setup and execution guide.

### Key Autonomous Loops:
- **The Toolsmith:** Synthesizes and registers new Python tools on-the-fly.
- **The Debaters:** Optimizer/Critic pairs that evolutionarily refactor agent instructions.
- **The Compressor:** Prunes redundant reasoning traces to optimize token efficiency.
- **The Judge:** Semantic, rubric-based evaluation using LLM-as-a-Judge and RAGAS.
- **The Prodder:** Watchdog skill that unblocks stalled agents in YOLO mode.

## 🏗️ Architecture
Aether operates as a headless wrapper for the Gemini CLI, using **Aetherial Memory** (Active Attention Filtering) to manage long-term state without context bloat.

![Aether Architecture](./assets/aether_diagram.png)

---
**Project Aether: Built for the swarm. Trust the evolution.**

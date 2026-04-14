# 🪐 Project Aether: Global Air Support for Your Agent

**STOP CHATTING. START ORCHESTRATING.**

Aether is a next-generation agentic framework designed for high-stakes, multi-step autonomous work. It acts as **Global Air Support for your agent**—providing rapid horizontal scaling for intensive technical workloads that evolve and optimize over time.

## 🚀 The Aether Advantage

- **Rapid Horizontal Scaling**: Dynamically spin up a serverless technical swarm to handle massive builds, complex refactors, and exhaustive security audits.
- **Self-Evolving Technical Swarm**: Aether identifies its own capability gaps and synthesizes new tools on-the-fly via the **Toolsmith**.
- **Open & Flexible**: Designed to integrate seamlessly with any agentic stack via **MCP (Model Context Protocol)**.
- **Stochastic Optimization**: Uses High-Temp Mixture of Experts (MoE) and statistical validation to ensure high-fidelity outcomes.

## 🏛️ Architecture: The SCION-Router Pattern
...

Aether strictly separates the **Control Plane** (Strategic Brain) from the **Execution Plane** (Technical Swarm) using the **SCION (Supervisor-Worker)** pattern and **Model Context Protocol (MCP)**.

### 1. The Orchestration Plane (Control)
The centralized Management layer that handles mission-level logic, decomposition, and routing.
- **[ORCHESTRATION_PLANE.md](docs/ORCHESTRATION_PLANE.md)**: Deep dive into the Master-Worker architecture.
- **Agent Router**: A high-bandwidth dispatcher that maps semantic intent to optimal worker capability scores.
- **Aetherial Memory**: Uses a **Surprise Gate** to protect the reasoning loop from context poisoning.

### 2. The Execution Plane (Workers)
A decentralized fleet of specialists running as serverless **Cloud Run** containers.
- **Toolsmith**: Autonomously synthesizes and registers new tools on-the-fly.
- **Specialists**: High-fidelity reasoning workers (e.g., Claude 3.5 Sonnet on Vertex AI) for deep architectural work.
- **Isolation**: Workers are sandboxed and communicate via **MCP over SSE**, ensuring a secure and scalable execution environment.

## 🚀 Advanced Patterns

### ⛽ Gas Town Persistence (Continuous Engine)
Inspired by Steve Yegge's ["Welcome to Gas Town"](https://steve-yegge.medium.com/welcome-to-gas-town-24ca60d29f86), Aether is a high-throughput factory of intent. It achieves "immortality" through a protocol of **Micro-Epoch Gating** and **GCS Checkpointing**. The engine serializes its state after every unit of work, allowing for seamless resurrection if an instance is terminated.

### 🔄 Ubiquitous Self-Optimization (Self-Optimizing Evals)
Every execution trace is a signal. Aether uses **LLM-as-a-Judge** and the **RAGAS** framework to audit its own performance. If a **Worker Capability (WC)** score falls below a threshold, the swarm autonomously triggers a **Reflection Agent** and **Toolsmith** to refactor the failing prompt or code.

### 🏹 All-In-One Orchestration Plane
Aether acts as a centralized master service on Cloud Run that dynamically provisions and manages ephemeral SCION worker instances. It separates the **Control Plane** from the **Execution Plane** via **MCP over SSE**, ensuring a high-scale, decoupled technical swarm.

## 🎮 High-Fidelity Showcases

### 1. Aether Spy Game: Adversarial Swarm
The ultimate test of Aether's SCION-Router architecture. Interrogate a swarm of adversarial LLMs (The Mole, The Gatekeeper, The Decoy) to find "Spy Secrets."
- **Adversarial Orchestration**: Uses the **Agent Router** to select the most deceptive model (Claude) for infiltrators and the most clinical model (Gemini) for fact-checkers.
- **Deception Logic**: Personas utilize **Signal Mimicry** and **Adversarial Shunting** to bypass the **Surprise Gate**.
- **Location**: See the `spy_game/` directory and `spy_game/cli.py` to start the mission.

### 2. Aether Action Shooter
A FastAPI/JS Canvas game featuring **Gas Town Persistence** and NPC AI synthesized by the **Toolsmith**.

## 📖 Developer Resources

### [Aether Developer Guide](docs/DEVELOPER_GUIDE.md)
The definitive guide on building autonomous systems. Learn best practices for:
- **SCION Decomposition**: Breaking goals into atomic tasks.
- **Eval-Gated Execution**: Using **RAGAS** and the **Judge** to mandate competency.
- **Gas Town Persistence**: Achieving "immortality" through GCS checkpointing.

## 🛠️ Installation & Setup Skills

Aether includes specialized **Gemini CLI Skills** to automate your workflow:

### 1. Aether Installation Wizard
Automatically configures your environment, installs dependencies, and deploys the swarm to Cloud Run.
```bash
# Activate in Gemini CLI
/activate_skill aether-wizard
```

### 2. Aether Configuration Tool
A programmatic tool for the LLM to register new capabilities, update WC scores, and optimize model routing on-the-fly.
```bash
# Activate in Gemini CLI
/activate_skill aether-config
```

## 📊 Visualizing the Swarm

- **[Architecture Diagram](assets/aether_swarm_architecture.png)**: Visualizing the Control vs. Execution plane separation.
- **[SCION Handoff Protocol](docs/assets/scion_handoff_protocol.png)**: Detailed logic of the Supervisor-Worker interaction.
## 🛠️ Installation & Setup

### 1. How to use Aether as a Tool
Project Aether is a high-bandwidth MCP server. You can connect it to **Claude Desktop**, **Gemini CLI**, or any MCP-compatible client to give your LLM autonomous powers.

- **[MCP Client Setup Guide](docs/MCP_INSTALLATION.md#5-connecting-to-mcp-clients-how-to-use-as-a-tool)**: Step-by-step instructions for integration.

### 2. Local Setup
...

```bash
# Clone and install
git clone https://github.com/jswortz/aether.git
cd aether
pip install -r requirements.txt

# Configure environment
export GITHUB_TOKEN=your_token
export GOOGLE_CLOUD_PROJECT=your_project
```

### 2. Deploy the Swarm
Deploy the execution plane to Google Cloud Run:
```bash
bash scripts/deploy_cloud_run.sh
```

### 4. Stochastic MoE & High-Temp Creativity
For tasks requiring maximum creative divergence (e.g., "Deep Debugging"), Aether invokes its **Mixture of Experts (MoE)** engine. 
- **Moderated Synthesis**: A Moderator agent orchestrates multiple high-temperature (T=0.9) expert completions.
- **Offline Sovereignty**: Includes the **Gemma-4 Offline Recipe**, allowing for completely local, high-fidelity MoE execution.

### 5. Aether-Stats: Experimental Precision
Aether now includes a specialized **Statistics & Experimental Design** layer (`aether-stats`).
- **Confidence Intervals**: Uses Bootstrapping and Bayesian Posterior methods to calculate CIs with minimal samples.
- **Scientific Evolution**: Statistically validates performance improvements before committing them to the swarm's core.

### 6. First-Class Recipes (GKE-Inspired)
Aether treats complex multi-agent workflows as **Declarative Recipes**.
- **Workload Manifests**: Similar to GKE, recipes define `metadata`, `spec`, and `status`.
- **Closed-Loop Reviews**: Every recipe mandates an **Adversarial Review** step, serving as a self-correcting evaluation loop.

### 7. Scheduled Dream Mode
The swarm improves itself while you sleep.
- **Idle-Time Reflection**: A locally scheduled (cron) process that analyzes historical traces and runs counterfactual simulations.
- **Proactive Refinement**: Automatically updates Worker Capability (WC) scores and triggers the Toolsmith to fill newly identified gaps.

## 🎯 Core Use Cases
...
- **Sovereign Creative Architecting**: Using the Gemma-4 Offline MoE recipe for sensitive design work.
- **Statistically Significant Optimization**: Validating a 5% latency reduction using `aether-stats`.

---
**Build for the swarm. Trust the evolution. Welcome to Aether.**

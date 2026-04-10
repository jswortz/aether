# Aether Agent Orchestration: The SCION-Router Pattern

Project Aether utilizes a high-bandwidth, hierarchical orchestration pattern designed for autonomous evolution and high-fidelity execution.

## 🏛️ Architectural Hierarchy

### 1. The Control Plane (The Brain)
The Control Plane is responsible for mission logic, goal decomposition, and swarm management.

#### **Aether Supervisor**
- **Role**: Central Orchestrator.
- **Responsibility**: Decomposes complex user requests into atomic tasks. It monitors worker progress and performs final synthesis of results.
- **Key Pattern**: SCION (Supervisor-Worker).

#### **Agent Router**
- **Role**: High-Speed Dispatcher.
- **Responsibility**: Maps semantic intent to the optimal worker path in milliseconds. It uses **Worker Capability (WC) Scores** to rank available tools and agents.
- **Tool**: `core/router.py`.

### 2. The Execution Plane (The Swarm)
The Execution Plane consists of specialized workers that perform technical tasks. All workers are exposed via the **Model Context Protocol (MCP)**.

#### **Toolsmith (Worker)**
- **Role**: Dynamic Capability Synthesis.
- **Responsibility**: Identifies capability gaps and autonomously generates new Python tools or MCP servers to fill them.
- **Server**: `toolsmith_mcp_server.py`.

#### **Claude Vertex MCP (Worker)**
- **Role**: High-Fidelity Reasoning.
- **Responsibility**: Performs deep architectural analysis and complex code drafting using Claude 3.5 Sonnet on Vertex AI.
- **Server**: `claude_vertex_mcp.py`.

#### **Reflection Agent (Worker)**
- **Role**: Evolutionary Analysis.
- **Responsibility**: Reviews performance traces and suggests optimizations for agent instructions and tools.

### 3. Adversarial Persona Swarms (Experimental)
Highly specialized personas designed for red-teaming, simulations, and adversarial reasoning.

#### **Aether Spy Swarm**
- **The Mole**: Friendly persona that leaks lethal misinformation and poisons Aetherial Memory.
- **The Gatekeeper**: Guarding sensitive data via logical validation and high-pass filtering.
- **The Decoy**: Diverts reasoning into logical dead-ends and shunts valid insights to the Adversarial Buffer.

## 📡 Communication: Model Context Protocol (MCP)

Aether uses MCP as the primary interface between the Control and Execution planes. This allows for:
- **Decoupled Scaling**: Workers can run as serverless Cloud Run services while the Supervisor remains centralized.
- **Dynamic Discovery**: The Supervisor can discover new tools synthesized by the Toolsmith on-the-fly.
- **Standardized Intent**: Intent queries are semantically routed to the best-fit capability.

## 📊 Worker Capability (WC) Scores

Every tool and agent in the Aether swarm is assigned a **WC Score (0.0 - 1.0)**.
- **1.0**: Gold standard, verified specialist.
- **0.5**: Experimental or synthesized tool.
- **0.0**: Deprecated or failed capability.

The Agent Router combines the WC Score with semantic relevance to calculate the final **Match Score**, ensuring the most reliable specialist is always selected.

## 🧠 Model-Skill Optimization

Aether autonomously selects the optimal reasoning engine for every task:
- **Fast Execution**: Tasks like basic tool synthesis or file operations default to `gemini-2.0-flash`.
- **High-Fidelity Reasoning**: Complex tasks involving architectural review, deep debugging, or security analysis trigger an automatic upgrade to `claude-3-5-sonnet-v2`.

The Router implements a **Keyword-Triggered Upgrade** strategy:
- **Keywords**: `analyze`, `review`, `refactor`, `architect`, `complex`, `debug`.
- **Logic**: If an intent query contains a reasoning keyword, the Router overrides the default worker model with a high-fidelity recommendation.

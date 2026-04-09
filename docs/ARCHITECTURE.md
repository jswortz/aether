# 🏗️ Aether Architecture: Control vs. Execution Plane

Project Aether follows a strict separation of concerns to ensure scalability, security, and autonomous evolution.

## 1. The Control Plane (SCION Supervisor)
The **Control Plane** is the "Brain" of the swarm. It manages the high-level logic, mission goals, and delegation strategies.

- **Components**:
    - **Aether Supervisor**: Decomposes user requests and monitors worker progress.
    - **Agent Router**: A high-bandwidth dispatcher that maps semantic intent to worker capability scores.
    - **Aetherial Memory**: Distills long-term context into high-signal attention filters.
- **Orchestration**: Uses the SCION (Supervisor-Worker) pattern. It does not perform technical tasks directly but orchestrates workers.
- **Environment**: Typically runs in a secure, high-trust environment (e.g., a central management VM or local dev machine).

## 2. The Execution Plane (MCP Workers)
The **Execution Plane** is the "Swarm" of workers that perform the actual technical work.

- **Components**:
    - **Toolsmith MCP**: Synthesizes and executes new tools.
    - **Claude Vertex MCP**: Provides high-fidelity reasoning and code generation via Vertex AI.
    - **Reflection Agent**: Analyzes traces and identifies evolutionary paths.
- **Communication**: All workers are exposed via the **Model Context Protocol (MCP)**.
- **Environment**: Runs in isolated, scalable containers on **Google Cloud Run**.
- **Security**: Workers have restricted IAM roles and run in sandboxed environments to prevent lateral movement.

## 3. Communication: The Fifth Element
The Control Plane communicates with the Execution Plane via **MCP (Model Context Protocol)** over **SSE (Server-Sent Events)**. This allows the Supervisor to dynamically discover and invoke worker capabilities without being tightly coupled to their implementation.

![Aether Architecture](../assets/aether_swarm_architecture.png)

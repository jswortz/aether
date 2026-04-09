# Aether Orchestration Plane: SCION & MCP Architecture

The Aether Orchestration Plane is the high-bandwidth connective tissue that separates strategic reasoning (Control) from technical execution (Work). It is built on the **SCION (Supervisor-Controlled Intelligence & Orchestration Network)** pattern and utilizes the **Model Context Protocol (MCP)** to maintain a decoupled, scalable, and autonomous swarm.

## 🏛️ The Control Plane vs. The Execution Plane

Aether enforces a strict "Air-Gap" between decision-making and implementation to ensure security, isolation, and scalability.

### 1. The Control Plane (The Supervisor)
The Control Plane is the "Master" of the architecture. It resides in a high-trust environment (Local or a secure Management VM) and is responsible for:
- **Strategic Decomposition**: Breaking down high-level user goals into a dependency graph of atomic tasks.
- **Intent Routing**: Using the **Agent Router** to map tasks to the optimal worker based on **Worker Capability (WC)** scores.
- **Aetherial Memory Management**: Filtering global session state through the **Surprise Gate** to keep the worker's reasoning window clean.
- **Synthesis**: Recombining worker outputs into a final, high-fidelity result.

### 2. The Execution Plane (The Workers)
The Execution Plane is the "Worker Swarm." These are specialized, ephemeral containers running on **Google Cloud Run** that perform specific technical tasks. Aether manages this via the **OrchestratorPlane**—a management layer that handles **Dynamic Provisioning**:
- **Resource Profiling**: Workers are provisioned with standardized performance profiles, typically **2Gi RAM and 1 CPU**, ensuring sufficient overhead for complex reasoning while maintaining cost efficiency.
- **Lifecycle Management**: The OrchestratorPlane manages the full lifecycle (`gcloud run deploy`), from provisioning specialized agent instances to automated teardown once the analytical load is complete.
- **Isolation**: Each worker runs in a sandboxed environment with restricted IAM permissions, preventing lateral movement or system compromise.

## 📡 The SCION-MCP Bridge

Communication between the Control Plane and Execution Plane occurs via **MCP over SSE (Server-Sent Events)**.

- **Standardization**: MCP provides a universal interface for the Supervisor to discover and invoke tools, resources, and prompts across the entire worker fleet.
- **Decoupling**: The Supervisor doesn't need to know *how* a worker is implemented (Python, Node, etc.) or *where* it is running, only its MCP capability.
- **Dynamic Expansion**: When the Toolsmith generates a new capability, it is immediately registered as a new MCP tool, allowing the Supervisor to use it without a restart.

## ⛽ Gas Town: Continuous Persistence

Aether implements the **"Gas Town"** pattern—a concept popularized by Steve Yegge in ["Welcome to Gas Town"](https://steve-yegge.medium.com/welcome-to-gas-town-24ca60d29f86). 

In traditional architectures, agents are ephemeral and reactive. Aether's Orchestration Plane is designed for **Continuous Persistence** through the **Gas Town Engine**:
- **Micro-Epoch Gating**: Work is broken down into discrete micro-epochs. Each epoch represents a transactional unit of progress.
- **GCS Checkpointing**: Upon the completion of every micro-epoch, the engine serializes the current state (history, variables, and context) and persists it to **Google Cloud Storage (GCS)** using `gsutil`.
- **Resurrection Protocol**: This checkpointing allows Aether to be effectively immortal. If a worker instance is terminated, the engine can "resurrect" the session by pulling the latest state from GCS and resuming from the exact epoch where it left off.
- **Latency Tolerance**: The SCION pattern handles high-latency technical tasks by offloading them to the Execution Plane, allowing the Control Plane to remain responsive or work on other tasks.
- **Persistent Sovereign Environment**: The Orchestration Plane maintains a stateful, autonomous "factory" that continuously refines its own code and capabilities.

## 🚀 Cloud Run Deployment Best Practices

To achieve a true "Serverless Swarm," Aether utilizes Google Cloud Run for the Execution Plane:

1. **Ephemeral Specialists**: Workers should be stateless and boot quickly (Cold-start optimization).
2. **Standardized Transport**: Use **SSE** for MCP to handle the long-running streaming connections required for complex reasoning.
3. **Concurrency Management**: Set Cloud Run concurrency limits to match the model's token-per-minute (TPM) limits to prevent rate-limiting cascading failures.
4. **IAM Granularity**: Assign each Worker service its own Service Account with the minimum permissions required for its specific domain (e.g., only the Toolsmith needs `storage.objects.create`).

## 📊 Orchestration Diagrams

- **[Swarm Architecture](../assets/aether_swarm_architecture.png)**: High-level view of the Control and Execution Plane separation.
- **[SCION Handoff Protocol](assets/scion_handoff_protocol.png)**: The step-by-step logic of how the Supervisor delegates and retrieves work from the swarm.

---
**Orchestrate the evolution. Build for the swarm.**

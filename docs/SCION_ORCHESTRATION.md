# SCION Orchestration

SCION (Supervisor-Controlled Intelligence & Orchestration Network) is the primary architectural pattern used in Project Aether. It is a strictly hierarchical approach to agent coordination that prioritizes task decomposition, role clarity, and error isolation.

## The Supervisor-Worker Pattern

In the SCION pattern, responsibilities are bifurcated between two primary tiers:

### 1. The Supervisor (The Architect)
The Supervisor is the "brain" of the operation. It does not perform low-level tasks itself; instead, it orchestrates the swarm.

- **Objective**: Strategic alignment and task decomposition.
- **Capabilities**:
    - **Intent Analysis**: Parsing complex user requests into discrete, actionable sub-tasks.
    - **Worker Selection**: Identifying the most appropriate Worker for a given task.
    - **Synthesis**: Merging the outputs of multiple Workers into a coherent final response.
    - **State Management**: Maintaining the global context of the session.

### 2. The Workers (The Specialists)
Workers are specialized agents designed for high performance in narrow domains.

- **Objective**: Tactical execution and specialized output.
- **Capabilities**:
    - **Domain Expertise**: Deep knowledge of specific languages, frameworks, or tools.
    - **Tool Access**: Fine-grained access to necessary utilities (e.g., shell, file system, APIs).
    - **Self-Correction**: Iterative improvement within their specialized task scope.

## Execution Flow

Aether uses a formal hand-off protocol to maintain context and intent through multiple worker transitions.

![SCION Hand-off Protocol](./assets/scion_handoff_protocol.png)

1. **Intake**: The Supervisor receives a high-level goal.
2. **Decomposition**: The goal is broken into a dependency graph of sub-tasks.
3. **Dispatch**: Sub-tasks are assigned to specialized Workers (e.g., Toolsmith, Backend, Frontend).
4. **Handoff**: The Supervisor uses a handoff mechanism (e.g., `transfer_to_agent`) to pass control and context.
5. **Execution**: Workers execute their tasks and return results to the Supervisor.
6. **Validation**: The Supervisor validates the results against the original goal.
7. **Consolidation**: Final results are synthesized and delivered to the user.

## Advantages of SCION

- **Scalability**: New specialized Workers can be added without modifying the Supervisor's core logic.
- **Isolation**: Failures in a single Worker do not crash the entire orchestration loop.
- **Reduced Context Drift**: By isolating specialized logic into Workers, the Supervisor's context window remains focused on high-level strategy.
- **Self-Evolution**: The [Toolsmith](./BOOK_OF_AETHER.md#toolsmith) pattern allows SCION to dynamically create new Workers as needed.

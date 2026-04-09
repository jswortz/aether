# Aether Agent Orchestration

This document outlines the agent hierarchy and orchestration patterns for the Aether ecosystem.

## Orchestration Pattern: SCION (Supervisor-Worker)

Aether uses the SCION pattern to manage complexity. The **Aether Supervisor** acts as the central orchestrator, delegating specialized tasks to **Workers**.

### Aether Supervisor
- **Role**: Central intelligence and task delegator.
- **Key Tools**: `transfer_to_agent`.
- **Primary Responsibility**: Decomposing user requests and monitoring worker execution.

### Specialized Workers

#### Aether Toolsmith
- **Role**: Dynamic skill synthesis and tool development.
- **Key Tools**: `write_file` (Write), `run_shell_command` (Bash).
- **Primary Responsibility**: Building and testing new capabilities for the ecosystem.

#### Aether Reflection Agent (The Mirror)
- **Role**: Performance reflection and steering directive synthesis.
- **Key Tools**: `bigquery_query`.
- **Primary Responsibility**: Analyzing low-performing traces and human feedback to guide Adversarial Debaters.

#### Worker Template
- **Role**: Blueprint for new specialized agents.
- **Primary Responsibility**: Providing a consistent structure for domain-specific workers.

## Delegation Workflow

1. **User Request**: The user interacts with the system.
2. **Supervisor Analysis**: The Aether Supervisor analyzes the request.
3. **Task Decomposition**: The Supervisor breaks the request into sub-tasks.
4. **Worker Delegation**: The Supervisor uses `transfer_to_agent` to hand off tasks to specialized workers.
5. **Synthesis**: The Supervisor collects and integrates results for the final response.

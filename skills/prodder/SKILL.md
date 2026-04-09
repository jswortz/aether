# Prodder Skill

The **Prodder** is a specialized capability within the Aether framework designed to ensure that agents operating in "yolo" mode (autonomous execution without confirmation) do not remain stuck in idle or deadlocked states.

## Purpose

In high-velocity autonomous workflows, agents may occasionally encounter "stuck" states where they are waiting for a response that will never come or are looping without making progress. The Prodder identifies these states and sends a "prod" (signal or interrupt) to force a re-evaluation or termination of the stalled process.

## Capabilities

- **Stall Detection**: Identifies agents that have not produced output or tool calls within a defined timeout period.
- **Context Injection**: Prods the agent by injecting a "system ping" or "status request" into its context to trigger a response.
- **Process Management**: Can forcibly restart or terminate agents that fail to respond to pings while in yolo mode.

## Usage

Agents can invoke the prodder when they detect a sub-agent or worker is taking longer than expected without yielding results.

### Example Logic

```python
if agent.is_yolo() and agent.idle_time > MAX_IDLE:
    prodder.prod(agent.id)
```

## Configuration

- `MAX_IDLE_SECONDS`: The threshold for considering an agent "stuck" (default: 300s).
- `PROD_METHOD`: The mechanism used to prod (e.g., `signal`, `context_injection`, `restart`).

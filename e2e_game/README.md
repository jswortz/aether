# Aether E2E Test: Action Shooter

This project demonstrates the Aether SCION pattern in action.

## Components

- **Frontend**: A high-performance HTML5 Canvas action shooter.
- **Backend**: FastAPI server managing state via the **Gas Town Protocol**.
- **Persistence**: Game state is checkpointed and resurrected using GCS (mocked for local dev).
- **Orchestration**: Built using the SCION pattern where the **Toolsmith** synthesized the core game engine.

## Deployment

To deploy to Google Cloud Run:

```bash
./deploy.sh
```

## Local Development

```bash
uvicorn main:app --reload
```

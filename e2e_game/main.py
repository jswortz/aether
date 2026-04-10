import os
import json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, Any

# Mocking GasTownEngine logic for the E2E demo if core isn't available
# or just implementing the persistence directly.
class GasTownPersistence:
    def __init__(self, bucket: str, session_id: str):
        self.bucket = bucket
        self.session_id = session_id
        self.local_state_path = f"/tmp/gastown_{session_id}.json"

    def save(self, state: Dict[str, Any]):
        with open(self.local_state_path, "w") as f:
            json.dump(state, f)
        # In a real GCS environment, we'd run:
        # os.system(f"gsutil cp {self.local_state_path} gs://{self.bucket}/state.json")
        print(f"Checkpoint saved to Gas Town (local simulation): {self.local_state_path}")

    def load(self) -> Dict[str, Any]:
        # In a real GCS environment, we'd run:
        # os.system(f"gsutil cp gs://{self.bucket}/state.json {self.local_state_path}")
        if os.path.exists(self.local_state_path):
            with open(self.local_state_path, "r") as f:
                return json.load(f)
        return {}

app = FastAPI()
persistence = GasTownPersistence(
    bucket=os.getenv("GCS_BUCKET", "aether-e2e-game"),
    session_id="player-1"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(os.path.join(BASE_DIR, "index.html"), "r") as f:
        return f.read()

@app.post("/save")
async def save_state(state: Dict[str, Any]):
    persistence.save(state)
    return {"status": "success", "message": "State checkpointed to Gas Town"}

@app.get("/load")
async def load_state():
    state = persistence.load()
    return state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

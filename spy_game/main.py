from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from spy_game.mission_controller import MissionController
from spy_game.router_config import configure_game_router
import uuid

app = FastAPI(title="Aether Spy Game Engine")

# Configure the router on startup
@app.on_event("startup")
async def startup_event():
    configure_game_router()

class ActionRequest(BaseModel):
    session_id: str
    player_id: str
    target_agent: str
    message: str

@app.post("/action")
async def perform_action(request: ActionRequest):
    try:
        controller = MissionController(request.session_id)
        response = controller.process_player_action(
            request.player_id, 
            request.target_agent, 
            request.message
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state/{session_id}")
async def get_state(session_id: str):
    controller = MissionController(session_id)
    return controller.get_summary()

@app.post("/session")
async def create_session():
    session_id = str(uuid.uuid4())
    # This will initialize the state via GasTownEngine
    MissionController(session_id)
    return {"session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

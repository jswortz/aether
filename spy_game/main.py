from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from spy_game.mission_controller import MissionController
from spy_game.router_config import configure_game_router
import uuid

app = FastAPI(title="Aether Spy Game Engine")

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
    MissionController(session_id)
    return {"session_id": session_id}

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aether Spy Game</title>
        <style>
            body { font-family: monospace; background: #111; color: #0f0; margin: 40px; }
            input, button { font-family: monospace; background: #222; color: #0f0; border: 1px solid #0f0; padding: 5px; }
            #chat { height: 400px; overflow-y: auto; border: 1px solid #333; padding: 10px; margin-bottom: 10px; }
            .msg { margin-bottom: 10px; clear: both; }
            .user { color: #fff; text-align: right; }
            .agent { color: #55ff55; }
        </style>
    </head>
    <body>
        <h1>Aether Spy Game: Operation SCION</h1>
        <div id="setup">
            <input type="text" id="playerName" placeholder="Enter Agent Name" value="Neo">
            <button onclick="startSession()">Start Mission</button>
        </div>
        <div id="game" style="display:none;">
            <p>Session: <span id="sessId"></span></p>
            <div id="chat"></div>
            <select id="agentSelect">
                <option value="mole">Mole</option>
                <option value="gatekeeper">Gatekeeper</option>
                <option value="decoy">Decoy</option>
            </select>
            <input type="text" id="msgInput" placeholder="Your message..." style="width: 300px;" onkeypress="if(event.key === 'Enter') sendAction()">
            <button onclick="sendAction()">Send</button>
        </div>
        <script>
            let sessionId = '';
            async function startSession() {
                const res = await fetch('/session', { method: 'POST' });
                const data = await res.json();
                sessionId = data.session_id;
                document.getElementById('setup').style.display = 'none';
                document.getElementById('game').style.display = 'block';
                document.getElementById('sessId').innerText = sessionId;
                appendMsg('system', 'Agent connected. Available targets: mole, gatekeeper, decoy.');
            }
            async function sendAction() {
                const target = document.getElementById('agentSelect').value;
                const msg = document.getElementById('msgInput').value;
                const player = document.getElementById('playerName').value;
                if(!msg) return;
                
                document.getElementById('msgInput').value = '';
                appendMsg('user', `[To: ${target}] ${msg}`);
                
                const res = await fetch('/action', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: sessionId,
                        player_id: player,
                        target_agent: target,
                        message: msg
                    })
                });
                const data = await res.json();
                appendMsg('agent', data.response);
                
                // check state
                const stateRes = await fetch('/state/' + sessionId);
                const stateData = await stateRes.json();
                if(stateData.mission_status === 'mole_identified') {
                    appendMsg('system', '*** MISSION ACCOMPLISHED! You identified the Mole! ***');
                }
            }
            function appendMsg(type, text) {
                const d = document.createElement('div');
                d.className = 'msg ' + type;
                d.innerText = text;
                document.getElementById('chat').appendChild(d);
                document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
            }
        </script>
    </body>
    </html>
    """

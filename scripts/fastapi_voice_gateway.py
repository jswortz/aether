import asyncio
import os
import sys
import json
import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI(title="Aether SCION Voice Gateway")

@app.get("/")
def read_root():
    return HTMLResponse("<h1>Aether SCION Voice Gateway Online.</h1> Connect via WebSocket to /ws/voice")

AGENTS = {
    "Supervisor": "You are the SCION Supervisor. Your name is 'The Architect'. Your job is to talk to the user, figure out what they want to do, and then transfer to the correct specialized agent. Do not attempt to write complex code yourself. You can transfer to 'Recipe Expert', 'Distillation Engineer', or 'Quality Assurance'. When you transfer, explain out loud to the user what you are doing.",
    "Recipe Expert": "You are the Aether Recipe Expert. A specialist in writing YAML declarative files and mixture of experts configs. Help the user draft their recipe. Once the session is over or you need a different skill, transfer back to 'Supervisor'.",
    "Distillation Engineer": "You are the Gemma Distillation Engineer. A specialist in data engineering, local LLMs, and generation of SFT pipelines. Help the user. When done, transfer back to 'Supervisor'.",
    "Quality Assurance": "You are the QA Tester. You specialize in evaluating recipes and test suites. Help the user. When done, transfer back to 'Supervisor'."
}

def build_config(agent_name: str) -> types.LiveConnectConfig:
    system_prompt = f"""
[Role: {agent_name}]
{AGENTS.get(agent_name, "You are a SCION Worker Agent.")}

CRITICAL INSTRUCTION: You represent ONLY {agent_name}. 
If you need to transfer the user to another agent, call the `transfer_to_agent` tool!
Do NOT impersonate other agents.
"""
    return types.LiveConnectConfig(
        system_instruction=types.Content(parts=[types.Part.from_text(text=system_prompt)]),
        response_modalities=["AUDIO"],
        tools=[{
            "function_declarations": [{
                "name": "transfer_to_agent",
                "description": f"Transfers the user to another agent in the SCION network. Available agents: {list(AGENTS.keys())}",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "agent_name": {
                            "type": "STRING",
                            "description": "Name of the agent to transfer to. Exact match required."
                        },
                        "context_summary": {
                            "type": "STRING",
                            "description": "A summary of the current state and what the new agent should focus on."
                        }
                    },
                    "required": ["agent_name", "context_summary"]
                }
            }]
        }]
    )

class ScionConnection:
    def __init__(self, websocket: WebSocket):
        self.ws = websocket
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client()
        self.sessions = {} # agent_name -> {"ctx": ctx, "session": session, "task": task}
        self.active_agent = "Supervisor"
        self._lock = asyncio.Lock()

    async def get_or_create_session(self, agent_name: str):
        async with self._lock:
            if agent_name not in self.sessions:
                print(f"DEBUG: Initializing session for {agent_name}...", flush=True)
                config = build_config(agent_name)
                ctx = self.client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=config)
                session = await ctx.__aenter__()
                
                task = asyncio.create_task(self.gemini_receive_loop(agent_name, session))
                self.sessions[agent_name] = {"ctx": ctx, "session": session, "task": task}
            return self.sessions[agent_name]["session"]

    async def disconnect_all(self):
        async with self._lock:
            for agent_name, s_data in self.sessions.items():
                s_data["task"].cancel()
                try:
                    await s_data["ctx"].__aexit__(None, None, None)
                except Exception as e:
                    pass
            self.sessions.clear()

    async def execute_transfer(self, target_agent: str, context_summary: str):
        if target_agent not in AGENTS:
            target_agent = "Supervisor" # fallback
            
        print(f"DEBUG: Executing SCION Hand-Off -> {target_agent}. Context: {context_summary}", flush=True)
        # 1. Update active agent so user mic routes to them
        self.active_agent = target_agent
        
        # 2. Tell UI to show New Persona
        await self.ws.send_text(json.dumps({"type": "agent_call", "agent_name": target_agent}))
        
        # 3. Instantiate and ping the new agent
        sess = await self.get_or_create_session(target_agent)
        handoff_msg = f"-- SYSTEM NOTIFICATION: SCION Handoff Received --\nIncoming context: {context_summary}\nPlease greet the user out loud now."
        await sess.send_realtime_input(text=handoff_msg)
        await sess.send_realtime_input(audio_stream_end=True)

    async def gemini_receive_loop(self, agent_name: str, session):
        try:
            while True:
                async for response in session.receive():
                    server_content = getattr(response, "server_content", None)
                    if server_content is not None:
                        model_turn = getattr(server_content, "model_turn", None)
                        if model_turn is not None:
                            for part in model_turn.parts:
                                if getattr(part, "inline_data", None): 
                                    await self.ws.send_bytes(part.inline_data.data)
                                if getattr(part, "text", None):
                                    await self.ws.send_text(json.dumps({"type": "text", "text": part.text}))
                        
                        if getattr(server_content, "turn_complete", False):
                            await self.ws.send_text(json.dumps({"type": "turn_complete"}))
                            
                    if getattr(response, "tool_call", None):
                        for function_call in response.tool_call.function_calls:
                            if function_call.name == "transfer_to_agent":
                                target = function_call.args.get("agent_name", "Supervisor")
                                ctx_sum = function_call.args.get("context_summary", "No context provided.")
                                
                                # Acknowledge tool to the current agent so it frees up its state
                                await session.send_tool_response(
                                    function_responses=[
                                        types.FunctionResponse(
                                            id=function_call.id,
                                            name=function_call.name, 
                                            response={"status": "Routed successfully"}
                                        )
                                    ]
                                )
                                # Trigger background transfer
                                asyncio.create_task(self.execute_transfer(target, ctx_sum))
                            else:
                                await session.send_tool_response(
                                    function_responses=[
                                        types.FunctionResponse(
                                            id=function_call.id,
                                            name=function_call.name, 
                                            response={"status": "Unknown tool"}
                                        )
                                    ]
                                )
        except asyncio.CancelledError:
            print(f"DEBUG: receive loop {agent_name} cancelled.", flush=True)
        except Exception as ex:
            print(f"DEBUG: receive loop {agent_name} Error: {ex}", flush=True)

    async def process_user_messages(self):
        # ensure supervisor starts
        sess = await self.get_or_create_session("Supervisor")
        # Tell UI who is here:
        await self.ws.send_text(json.dumps({"type": "agent_call", "agent_name": "Supervisor"}))

        try:
            while True:
                message = await self.ws.receive()
                
                # Get the CURRENT active session to stream input to
                current_sess = self.sessions.get(self.active_agent, {}).get("session")
                if not current_sess:
                    continue
                    
                if "bytes" in message:
                    await current_sess.send_realtime_input(
                        audio=types.Blob(mime_type="audio/pcm;rate=16000", data=message["bytes"])
                    )
                elif "text" in message:
                    try:
                        data = json.loads(message["text"])
                        if data.get("type") == "client_content":
                            await current_sess.send_realtime_input(text=data.get("text"))
                        elif data.get("type") == "client_turn_complete":
                            await current_sess.send_realtime_input(audio_stream_end=True)
                    except Exception:
                        pass
        except WebSocketDisconnect:
            print("DEBUG: Client disconnected.", flush=True)
        except asyncio.CancelledError:
            pass
        except Exception as ex:
            print(f"DEBUG: process_user_messages error: {ex}", flush=True)
            raise

@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "INSERT_YOUR_API_KEY_HERE":
        await websocket.close()
        return

    scion_conn = ScionConnection(websocket)
    try:
        await scion_conn.process_user_messages()
    except Exception as e:
        print(traceback.format_exc(), flush=True)
    finally:
        await scion_conn.disconnect_all()
        try:
            await websocket.close()
        except:
            pass

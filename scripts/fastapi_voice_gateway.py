import asyncio
import os
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types

app = FastAPI(title="Aether Swarm Voice Gateway")

SWARM_PROXY_PROMPT = """
CRITICAL INSTRUCTION: AT THE START OF EVERY SINGLE TURN, BEFORE YOU SPEAK, YOU MUST EMIT YOUR PERSONA AS TEXT EXACTLY LIKE THIS:
[Role: Aether Architect]
or [Role: Distillation Engineer] etc.
Do not say the brackets or role out loud. Only include them in the text response!
"""

@app.get("/")
def read_root():
    return HTMLResponse("<h1>Aether Voice Gateway Online.</h1> Connect via WebSocket to /ws/voice")

@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("DEBUG: Client WebSocket Accepted.", flush=True)
    
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key or api_key == "INSERT_YOUR_API_KEY_HERE":
            print("DEBUG: Invalid or Missing GEMINI_API_KEY", flush=True)
            await websocket.close()
            return
            
        print("DEBUG: Initializing GenAI Client...", flush=True)
        client = genai.Client()
        
        config = types.LiveConnectConfig(
            system_instruction=types.Content(parts=[types.Part(text=SWARM_PROXY_PROMPT)]),
            response_modalities=["AUDIO"],
            tools=[{"function_declarations": [{"name": "generate_aether_recipe", "description": "Triggers Aether swarm..."}]}]
        )
        
        print("DEBUG: Connecting to gemini-3.1-flash-live-preview...", flush=True)
        async with client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=config) as session:
            print("DEBUG: Session Connected Successfully!", flush=True)
            
            async def receive_from_gemini():
                try:
                    async for response in session.receive():
                        server_content = getattr(response, "server_content", None)
                        if server_content is not None:
                            model_turn = getattr(server_content, "model_turn", None)
                            if model_turn is not None:
                                for part in model_turn.parts:
                                    if getattr(part, "inline_data", None): 
                                        await websocket.send_bytes(part.inline_data.data)
                                    if getattr(part, "text", None):
                                        import json
                                        await websocket.send_text(json.dumps({"type": "text", "text": part.text}))
                            if getattr(server_content, "turn_complete", False):
                                import json
                                await websocket.send_text(json.dumps({"type": "turn_complete"}))
                                
                        if getattr(response, "tool_call", None):
                            print(f"Executing Aether Swarm Tool: {response.tool_call}", flush=True)
                            for function_call in response.tool_call.function_calls:
                                await session.send_tool_response(
                                    function_responses=[
                                        types.FunctionResponse(
                                            id=function_call.id,
                                            name=function_call.name, 
                                            response={"status": "dispatched"}
                                        )
                                    ]
                                )
                except asyncio.CancelledError:
                    print("DEBUG: receive_from_gemini cancelled.", flush=True)
                except Exception as ex:
                    print(f"DEBUG: receive_from_gemini Error: {ex}", flush=True)
                    raise
            
            async def send_to_gemini():
                try:
                    while True:
                        message = await websocket.receive()
                        if "bytes" in message:
                            # It's raw PCM audio
                            await session.send_realtime_input(
                                audio=types.Blob(mime_type="audio/pcm;rate=16000", data=message["bytes"])
                            )
                        elif "text" in message:
                            # Parse JSON chat messages
                            import json
                            try:
                                data = json.loads(message["text"])
                                if data.get("type") == "client_content":
                                    await session.send_realtime_input(
                                        text=data.get("text")
                                    )
                            except json.JSONDecodeError:
                                pass
                except WebSocketDisconnect:
                    print("DEBUG: User disconnected from browser.", flush=True)
                except asyncio.CancelledError:
                    print("DEBUG: send_to_gemini cancelled.", flush=True)
                except Exception as ex:
                    print(f"DEBUG: send_to_gemini Error: {ex}", flush=True)
                    raise

            print("DEBUG: Gathering concurrent tasks...", flush=True)
            await asyncio.gather(receive_from_gemini(), send_to_gemini())
            
    except Exception as e:
        import traceback
        print("DEBUG: Gateway Fatal Error:", flush=True)
        print(traceback.format_exc(), flush=True)
        try:
            await websocket.close()
        except Exception:
            pass

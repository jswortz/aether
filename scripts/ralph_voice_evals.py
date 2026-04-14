import asyncio
import os
from google import genai
from google.genai import types

# Rely on environment variable GEMINI_API_KEY being set externally
if not os.environ.get("GEMINI_API_KEY"):
    raise Exception("GEMINI_API_KEY environment variable is missing")

async def evaluator():
    print("Ralph Wiggum Eval Loop: Testing Gemini Live API Configuration...")
    try:
        SWARM_PROXY_PROMPT = "You are the Voice Interface for Project Aether. Speak confidently."
        
        config = types.LiveConnectConfig(
            system_instruction=types.Content(parts=[types.Part(text=SWARM_PROXY_PROMPT)]),
            response_modalities=["AUDIO"],
            tools=[{"function_declarations": [{"name": "generate_aether_recipe", "description": "Triggers Aether swarm..."}]}]
        )
        
        client = genai.Client()
        async with client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=config) as session:
            print("Eval [API Connectivity]: PASSED")
            
            # Send audio
            await session.send_realtime_input(
                audio=types.Blob(mime_type="audio/pcm;rate=16000", data=b"\x00" * 3200) # 100ms of silence
            )
            print("Eval [Audio Transmission]: PASSED")
            
            # Wait for response
            print("Waiting for server response...")
            async for response in session.receive():
                print("Received response!")
                break
                
        print("🎉 ALL EVALS PASSED!")
        return True

    except Exception as e:
        import traceback
        print(f"Eval Fatal Loop Crash:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(evaluator())

from dotenv import load_dotenv
load_dotenv()

import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from playwright_manager import PlaywrightManager
from agent import run_agent_loop

pm = PlaywrightManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Playwright Manager...")
    await pm.start()
    yield
    print("Stopping Playwright Manager...")
    await pm.stop()

app = FastAPI(title="NeoFish Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to NeoFish Backend"}


@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({
        "type": "info", 
        "message": "Connected to NeoFish Agent WebSocket",
        "message_key": "common.connected_ws"
    }))
    
    # Callback to send action required to frontend
    async def request_human_action(reason: str, b64_image: str):
        payload = {
            "type": "action_required",
            "reason": reason,
            "image": b64_image
        }
        await websocket.send_text(json.dumps(payload))
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            msg_type = payload.get("type")
            
            if msg_type == "resume":
                pm.resume_from_human()
                await websocket.send_text(json.dumps({
                    "type": "info", 
                    "message": "Agent resumed execution.",
                    "message_key": "common.agent_resumed"
                }))
            
            elif msg_type == "user_input":
                # Start the agent loop in background to not block WS receive loop
                user_msg = payload.get("message", "")
                
                async def ws_send_msg(msg: str):
                    await websocket.send_text(json.dumps({"type": "info", "message": msg}))
                
                # We implement the agent loop
                asyncio.create_task(run_agent_loop(pm, user_msg, ws_send_msg, request_human_action))
                
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

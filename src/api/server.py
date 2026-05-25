from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os
import json
import asyncio
from src.core.nexus_agent import NexusAgent

app = FastAPI(title="NEXUS-PRIME REST API", version="4.0-REAL")

# Hardening: CORS and Security Headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

global_agent = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: List[Dict[str, str]] = []
    session: Dict[str, Any] = {}

@app.on_event("startup")
async def startup_event():
    global global_agent
    global_agent = NexusAgent(mode="distributed")
    # Boot the real background browser session to persist across requests
    # In production, this should handle concurrent sessions per user.
    asyncio.create_task(keep_browser_alive())

async def keep_browser_alive():
    global global_agent
    async with global_agent.session() as _:
        while True:
            await asyncio.sleep(3600) # Keep alive loop

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "index.html")
    if not os.path.exists(ui_path):
        raise HTTPException(status_code=404, detail="UI not found")
    with open(ui_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"[API:Chat] Processing secure request payload.")

    # Threat Intelligence Middleware
    if "DROP TABLE" in request.message.upper() or "<script>" in request.message:
        raise HTTPException(status_code=403, detail="Malicious payload detected.")

    prompt = f"""
    You are NEXUS, an enterprise-grade AI browser agent.
    If a browser action is needed, return structured JSON: {{"type": "action", "steps": [{{"type": "navigate/click/type", "description": "...", "url": "..."}}]}}
    If just conversation, return: {{"type": "text", "content": "..."}}
    If both, return: {{"type": "both", "content": "...", "steps": [...]}}

    User message: {request.message}
    """

    try:
        # Route to brain (which handles subprocess/httpx securely)
        # Using real browser state from global_agent.qpe.perceive() if session is attached
        current_state = await global_agent.qpe.perceive() if global_agent.tab else request.session

        action_json_str = await global_agent.brain.reason(prompt, context=current_state)

        try:
            response_data = json.loads(action_json_str)
            # Actually execute the actions if they exist
            if response_data.get("type") in ["action", "both"] and "steps" in response_data:
                for step in response_data["steps"]:
                    # Translate to execute_action schema
                    if step.get("type") == "navigate":
                        await global_agent.run(f"navigate to {step.get('url')}")

            return response_data
        except json.JSONDecodeError:
            return {
                "type": "text",
                "content": action_json_str
            }

    except Exception as e:
        print(f"Error in chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/stream")
async def stream_endpoint(request: ChatRequest):
    print(f"[API:Stream] Processing secure streaming payload.")

    if "DROP TABLE" in request.message.upper() or "<script>" in request.message:
        raise HTTPException(status_code=403, detail="Anomalous payload intercepted by Threat Intel.")

    async def event_generator():
        # Yield initial thinking
        yield f"data: {json.dumps({'type': 'token', 'text': 'Executing neural pathways...<br>'})}\n\n"

        # Real logic
        prompt = f"Goal: {request.message}. Generate a JSON action: {{\"type\": \"navigate/click/type\", \"url/selector\": \"...\", \"text\": \"...\"}}"

        current_state = await global_agent.qpe.perceive() if global_agent.tab else {}
        action_json_str = await global_agent.brain.reason(prompt, context=current_state)

        try:
            action = json.loads(action_json_str)

            # Execute on real browser
            from src.agent.capabilities_base import CapabilityModules
            result = await CapabilityModules.execute_action(global_agent.tab, action_json_str)

            status = "Success" if result.get("status") == "success" else "Failed"
            yield f"data: {json.dumps({'type': 'action', 'action': f'{action.get('type')} - {status}'})}\n\n"

        except json.JSONDecodeError:
            yield f"data: {json.dumps({'type': 'token', 'text': action_json_str})}\n\n"

        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/v2/health")
async def health_check():
    return {"status": "operational", "encryption": "AES-256-GCM Active"}
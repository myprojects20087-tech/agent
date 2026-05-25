from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
from src.core.nexus_agent import NexusAgent

app = FastAPI(title="NEXUS-PRIME REST API")
global_agent = None

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    session: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    global global_agent
    global_agent = NexusAgent(mode="local")
    print("[API] Global Nexus Agent initialized for chat backend.")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "index.html")
    with open(ui_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"[API:Chat] Received message: {request.message}")

    # Normally, we would pass request.message to global_agent.brain.reason() here
    # to let the LLM decide. For demonstration of the UI contract:

    msg_lower = request.message.lower()

    if "go to" in msg_lower or "navigate" in msg_lower or "open" in msg_lower:
        url = "https://google.com"
        if "youtube" in msg_lower: url = "https://youtube.com"
        elif "github" in msg_lower: url = "https://github.com"

        # In a real scenario, we would trigger global_agent.run() asynchronously
        # and stream back the steps.
        return {
            "type": "both",
            "content": f"Navigating to {url} now.",
            "steps": [
                {"type": "navigate", "url": url, "description": f"Navigating to {url}"},
                {"type": "done", "description": "Page loaded"}
            ]
        }

    elif "fill" in msg_lower or "login" in msg_lower:
        return {
            "type": "action",
            "message": "Form filled successfully.",
            "steps": [
                {"type": "click", "description": "Clicking email input field"},
                {"type": "type", "description": "Typing 'user@example.com'"},
                {"type": "click", "description": "Clicking 'Sign In' button"},
                {"type": "done", "description": "Action completed in 1.2s"}
            ]
        }

    else:
        # Conversational response
        return {
            "type": "text",
            "content": f"I am NEXUS. You said: '{request.message}'. I can navigate, click, type, or extract data based on your commands."
        }

@app.get("/api/v2/health")
async def health_check():
    return {"status": "healthy"}
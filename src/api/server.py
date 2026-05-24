from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="NEXUS-PRIME Swarm Gateway")

class TaskRequest(BaseModel):
    goal: str
    num_workers: int = 1

@app.post("/api/v2/task")
async def execute_task(request: TaskRequest):
    return {"status": "Task accepted", "goal": request.goal, "workers": request.num_workers}

@app.get("/api/v2/health")
async def health_check():
    return {"status": "healthy"}
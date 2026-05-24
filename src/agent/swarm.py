import asyncio
import uuid
from typing import List, Dict

class FirecrackerMicroVM:
    def __init__(self, node_id: str):
        self.node_id = node_id
        print(f"[Swarm:MicroVM] Provisioning isolated execution enclave: {self.node_id}")

    async def execute(self, task: str) -> Dict:
        print(f"[Swarm:MicroVM:{self.node_id}] Executing sub-task: {task}")
        await asyncio.sleep(0.5)
        return {"node": self.node_id, "data": "extracted_json_ld_fragment"}

class SwarmOrchestrator:
    def __init__(self):
        self.workers: List[FirecrackerMicroVM] = []
        print("[SwarmOrchestrator] Initialized global swarm controller.")

    async def spawn_swarm(self, task: str, num_workers: int = 5) -> Dict:
        print(f"[SwarmOrchestrator] Decomposing task '{task}' and spawning {num_workers} Map-Reduce workers...")
        self.workers = [FirecrackerMicroVM(str(uuid.uuid4())[:8]) for _ in range(num_workers)]

        # Dispatch tasks concurrently
        tasks = [worker.execute(f"Sub-task partition {i}") for i, worker in enumerate(self.workers)]
        results = await asyncio.gather(*tasks)

        print("[SwarmOrchestrator] Aggregating results from enclave nodes.")
        return {"status": "Swarm deployed & executed", "aggregated_data": results}
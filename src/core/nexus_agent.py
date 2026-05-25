import asyncio
import json
from typing import Dict, Any, Optional
from src.perception.qpe import QuadLayerPerceptionEngine
from src.agent.planner import NeuroSymbolicPlanner
from src.evasion.stealth import StealthCore
from src.memory.stores import EpisodicMemory, KnowledgeGraph
from src.brain import BrainFactory
from src.agent.capabilities_base import CapabilityModules
from pydantic import BaseModel

class NexusAgent:
    def __init__(self, mode="distributed", profile: Optional[Dict] = None, brain_config: Optional[Dict] = None):
        print(f"[NexusAgent] Initializing Real NEXUS-PRIME in {mode} mode")
        self.mode = mode
        self.profile = profile or {}

        default_brain_config = {"type": "api", "endpoint": "https://api.openai.com/v1/chat/completions"}
        self.brain = BrainFactory.get_brain(brain_config or default_brain_config)

        self.qpe = QuadLayerPerceptionEngine()
        self.planner = NeuroSymbolicPlanner(brain=self.brain)
        self.stealth = StealthCore()
        self.episodic_memory = EpisodicMemory()

        self.tab = None # Will be set by BrowserSession

    async def run(self, task: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        print(f"\n[NexusAgent] Engaging Real Task: {task}")

        if not self.tab:
            print("[NexusAgent] ERROR: No browser session active. Use 'async with agent.session():'")
            return {"status": "error"}

        max_steps = 10

        # Real Execution Loop
        for step in range(max_steps):
            print(f"\n--- Step {step + 1} ---")

            # 1. Real Perception
            current_state = await self.qpe.perceive()

            # Condense the DOM for the LLM to fit in context window
            dom_summary = [{"tag": n["tag"], "text": n["text"]} for n in current_state.get("dom", {}).get("nodes", [])[:20]]

            context = {
                "url": current_state.get("url"),
                "title": current_state.get("title"),
                "visible_elements": dom_summary
            }

            # 2. Real Brain Reasoning
            prompt = f"Goal: {task}\nBased on the context, what is the single next JSON action to take? Format: {{\"type\": \"navigate/click/type\", \"selector/url\": \"...\", \"text\": \"...\"}}. If the goal is complete, return {{\"type\": \"done\"}}"

            print("[NexusAgent] Querying Brain for next action...")
            action_json_str = await self.brain.reason(prompt, context=context)
            print(f"[NexusAgent] Brain Decision: {action_json_str}")

            if "done" in action_json_str.lower():
                print("[NexusAgent] Task reported complete by Brain.")
                break

            # 3. Real Execution
            result = await CapabilityModules.execute_action(self.tab, action_json_str)
            if result.get("status") == "error":
                print(f"[NexusAgent] Action execution failed: {result}")

            await asyncio.sleep(1) # Pace the loop

        return {"status": "success", "task": task}

    def session(self):
        from .browser_session import BrowserSession
        return BrowserSession(self)
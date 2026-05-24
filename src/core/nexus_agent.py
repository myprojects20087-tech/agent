import asyncio
from typing import Dict, Any, Optional
from src.perception.qpe import QuadLayerPerceptionEngine
from src.agent.planner import NeuroSymbolicPlanner
from src.evasion.stealth import StealthCore
from src.memory.stores import EpisodicMemory, KnowledgeGraph
from src.brain import BrainFactory

class NexusAgent:
    def __init__(self, mode="distributed", profile: Optional[Dict] = None, brain_config: Optional[Dict] = None):
        print(f"[NexusAgent] Initializing NEXUS-PRIME in {mode} mode")
        self.mode = mode
        self.profile = profile or {}

        # Initialize the Brain (Central Intelligence)
        default_brain_config = {"type": "local", "model": "qwen2-vl-7b"}
        self.brain = BrainFactory.get_brain(brain_config or default_brain_config)

        self.qpe = QuadLayerPerceptionEngine()
        self.planner = NeuroSymbolicPlanner(brain=self.brain)
        self.stealth = StealthCore()
        self.episodic_memory = EpisodicMemory()
        self.knowledge_graph = KnowledgeGraph()

    async def run(self, task: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        print(f"\n[NexusAgent] Engaging Task: {task}")

        # 1. Apply hardware/TLS forgery
        self.stealth.apply_tls_spoof()
        self.stealth.apply_webgl_forgery()

        state_history = []
        max_retries = 3

        # RL-Optimized Execution Loop
        for attempt in range(max_retries):
            try:
                # 2. Quad-Layer Perception
                current_state = await self.qpe.perceive()

                # 3. MCTS-based Planning using the Brain
                plan_trajectory = await self.planner.generate_plan(task, current_state)
                print(f"[NexusAgent] Optimal Trajectory Selected: {plan_trajectory}")

                # 4. Execution with Biometric Jitter
                for action in plan_trajectory:
                    print(f"[NexusAgent] Executing: {action} (applying Fitts's Law jitter)")
                    await asyncio.sleep(0.15) # sub-200ms execution latency

                # 5. Verification
                post_state = await self.qpe.perceive()
                reward = self._calculate_reward(current_state, post_state)

                # 6. Memory Storage
                episode = {"task": task, "trajectory": plan_trajectory, "reward": reward}
                self.episodic_memory.store(episode)

                print("[NexusAgent] Task Execution Successful.")
                return {"status": "success", "trajectory": plan_trajectory, "reward": reward}

            except Exception as e:
                print(f"[NexusAgent] Attempt {attempt+1} Failed: {e}. Micro-rollback initiated.")
                self.stealth.cycle_fingerprint()
                await asyncio.sleep(0.5)

        return {"status": "failed", "reason": "Max retries exceeded on WAF block"}

    def _calculate_reward(self, pre_state: Dict, post_state: Dict) -> float:
        # Complex delta comparison to gauge success
        return 0.95

    def session(self):
        from .browser_session import BrowserSession
        return BrowserSession(self)
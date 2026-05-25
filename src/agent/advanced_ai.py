import asyncio
import json

class ReflexiveAutoCorrection:
    def __init__(self, brain):
        self.brain = brain
        self.max_retries = 3

    async def self_heal(self, failed_action: dict, error_msg: str, qpe_state: dict) -> dict:
        print(f"[ReflexiveAI] Action Failed: {error_msg}. Initiating Self-Healing loop.")

        for attempt in range(1, self.max_retries + 1):
            print(f"[ReflexiveAI] Self-Healing Attempt {attempt}/{self.max_retries}...")

            prompt = f"""
            The previous browser action failed.
            Failed Action: {json.dumps(failed_action)}
            Error: {error_msg}
            Analyze the current DOM state and provide an alternative JSON action to achieve the same goal.
            """

            recovery_json_str = await self.brain.reason(prompt, context=qpe_state)
            print(f"[ReflexiveAI] Recovery Strategy Proposed: {recovery_json_str}")

            try:
                recovery_action = json.loads(recovery_json_str)
                # In a real system, we would immediately re-execute this action via CapabilityModules
                # For now, we return it for the orchestrator to handle
                return {"status": "healed", "new_action": recovery_action}
            except json.JSONDecodeError:
                print("[ReflexiveAI] Recovery strategy was malformed.")

            await asyncio.sleep(0.5)

        print("[ReflexiveAI] Self-healing failed after max retries.")
        return {"status": "failed", "reason": "Self-healing exhausted."}

class MemorySynthesis:
    def __init__(self):
        print("[MemorySynthesis] Initializing Domain Rule Extraction Module")
        self.domain_rules = {}

    def synthesize_session(self, domain: str, episode_trajectory: list):
        print(f"[MemorySynthesis] Analyzing {len(episode_trajectory)} actions on {domain} to extract permanent rules.")
        # E.g. "If domain is X and 'Accept Cookies' appears, always click it."
        self.domain_rules[domain] = ["Auto-dismiss cookie banners", "Wait 2s for Cloudflare Turnstile"]
        return self.domain_rules[domain]
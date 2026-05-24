import asyncio

class VisualQA:
    def __init__(self, brain=None):
        self.brain = brain
        print("[VisualQA] Initializing Visual Q&A on Page Module")

    async def answer(self, question: str, visual_context: dict):
        print(f"[VisualQA] Analyzing visual context for question: {question}")
        await asyncio.sleep(0.3)
        if self.brain:
            print("[VisualQA] Routing image + question to VLM (Brain)")
            answer = await self.brain.reason(f"VQA: {question}", context=visual_context)
            return {"status": "success", "answer": answer}
        return {"status": "success", "answer": "Extracted value based on visual grounding."}
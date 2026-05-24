import asyncio
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class BrainProvider(ABC):
    @abstractmethod
    async def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        pass

class LocalBrain(BrainProvider):
    def __init__(self, model_name: str = "qwen2-vl-7b"):
        self.model_name = model_name
        print(f"[Brain] Initialized Local Brain (TensorRT/Ollama) with model: {self.model_name}")

    async def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        print(f"[Brain:Local] Running fast local inference for prompt length: {len(prompt)}")
        await asyncio.sleep(0.1)
        return "LOCAL_INFERENCE_RESULT"

class APIBrain(BrainProvider):
    def __init__(self, api_key: str, endpoint: str = "openai/gemini/anthropic"):
        self.endpoint = endpoint
        print(f"[Brain] Initialized API Brain for endpoint: {self.endpoint}")

    async def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        print(f"[Brain:API] Dispatching request to {self.endpoint}...")
        await asyncio.sleep(0.5)
        return "API_INFERENCE_RESULT"

class CLIBrain(BrainProvider):
    def __init__(self, cli_tool: str = "gemini"): # e.g. "gemini", "anigravity"
        self.cli_tool = cli_tool
        print(f"[Brain] Initialized CLI Brain wrapping external tool: {self.cli_tool}")

    async def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        print(f"[Brain:CLI] Executing subprocess call to `{self.cli_tool}`...")
        await asyncio.sleep(0.8)
        return "CLI_TOOL_RESULT"
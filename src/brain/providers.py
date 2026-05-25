import asyncio
import shlex
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
import json

class BrainProvider(ABC):
    @abstractmethod
    async def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        pass

class LocalBrain(BrainProvider):
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name
        self.api_base = "http://localhost:11434/api/generate" # Default Ollama endpoint
        print(f"[Brain] Initialized Local Brain (Ollama) with model: {self.model_name}")

    async def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        payload = {"model": self.model_name, "prompt": prompt, "stream": False}
        if context:
            payload["prompt"] = f"Context: {json.dumps(context)}\n\nGoal: {prompt}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_base, json=payload, timeout=60.0)
                response.raise_for_status()
                return response.json().get("response", "")
            except Exception as e:
                print(f"[Brain:Local] Error communicating with local model: {e}")
                return "ERROR: Could not reach local brain."

class APIBrain(BrainProvider):
    def __init__(self, api_key: str, endpoint: str = "https://api.openai.com/v1/chat/completions"):
        self.api_key = api_key
        self.endpoint = endpoint
        print(f"[Brain] Initialized API Brain for endpoint: {self.endpoint}")

    async def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        full_prompt = prompt if not context else f"Context:\n{json.dumps(context)}\n\n{prompt}"

        payload = {
            "model": "gpt-4o", # Default fallback
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.2
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.endpoint, headers=headers, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[Brain:API] Request failed: {e}")
                return f"ERROR: API request failed. {e}"

class CLIBrain(BrainProvider):
    def __init__(self, cli_tool: str = "gemini"):
        self.cli_tool = cli_tool
        print(f"[Brain] Initialized CLI Brain wrapping external tool: {self.cli_tool}")

    async def reason(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        # Construct the CLI command safely
        full_prompt = prompt
        if context:
            # We truncate context heavily for CLI so it doesn't break bash limits
            ctx_str = json.dumps(context)[:500]
            full_prompt = f"Context: {ctx_str} | Goal: {prompt}"

        # Example: `anigravity "What is the current page about?"`
        safe_prompt = shlex.quote(full_prompt)
        command = f"{self.cli_tool} {safe_prompt}"

        print(f"[Brain:CLI] Executing subprocess: {command[:100]}...")
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return f"ERROR: CLI tool failed with: {stderr.decode().strip()}"

            return stdout.decode().strip()
        except Exception as e:
            return f"ERROR: Subprocess execution failed: {e}"
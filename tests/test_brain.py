import pytest
from src.brain.providers import LocalBrain, APIBrain

@pytest.mark.asyncio
async def test_brain_initialization():
    local_brain = LocalBrain()
    assert local_brain.model_name == "qwen2-vl-7b"

    api_brain = APIBrain(api_key="test")
    assert api_brain.endpoint == "openai/gemini/anthropic"

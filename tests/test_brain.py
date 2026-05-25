import pytest
from src.brain.providers import LocalBrain, APIBrain

@pytest.mark.asyncio
async def test_brain_initialization():
    local_brain = LocalBrain()
    assert local_brain.model_name == "llama3"

    api_brain = APIBrain(api_key="test")
    assert api_brain.endpoint == "https://api.openai.com/v1/chat/completions"

from .providers import BrainProvider, LocalBrain, APIBrain, CLIBrain

class BrainFactory:
    @staticmethod
    def get_brain(config: dict) -> BrainProvider:
        brain_type = config.get("type", "local").lower()
        if brain_type == "local":
            return LocalBrain(model_name=config.get("model", "qwen2-vl-7b"))
        elif brain_type == "api":
            return APIBrain(api_key=config.get("api_key", ""), endpoint=config.get("endpoint", "openai"))
        elif brain_type == "cli":
            return CLIBrain(cli_tool=config.get("cli_tool", "gemini"))
        else:
            raise ValueError(f"Unknown brain type: {brain_type}")

__all__ = ["BrainFactory", "BrainProvider"]
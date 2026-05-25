import asyncio
import os

class VoiceCommandModule:
    def __init__(self):
        print("[Voice] Initializing faster-whisper Speech-to-Text module...")
        self.model = None

    def _lazy_load_model(self):
        if not self.model:
            try:
                from faster_whisper import WhisperModel
                # Tiny model for ultra-low latency local transcription
                self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
                print("[Voice] faster-whisper 'tiny' model loaded.")
            except ImportError:
                print("[Voice] faster-whisper not installed. Voice transcription unavailable.")
                self.model = "mock"

    async def transcribe(self, audio_file_path: str) -> str:
        self._lazy_load_model()
        if self.model == "mock":
            await asyncio.sleep(0.5)
            return "Mock transcription of voice command."

        print(f"[Voice] Transcribing audio file: {audio_file_path}")
        try:
            # Using run_in_executor to avoid blocking the async event loop with heavy ML inference
            loop = asyncio.get_event_loop()
            def _run():
                segments, info = self.model.transcribe(audio_file_path, beam_size=1)
                return " ".join([segment.text for segment in segments]).strip()

            transcription = await loop.run_in_executor(None, _run)
            print(f"[Voice] Transcription success: {transcription}")
            return transcription
        except Exception as e:
            print(f"[Voice] Transcription error: {e}")
            return f"Error transcribing audio: {e}"
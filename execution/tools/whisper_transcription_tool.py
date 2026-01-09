"""Tool for transcribing audio using OpenAI Whisper."""

from typing import Dict, Any, Optional
from langchain_core.tools import BaseTool
from execution.core.config import get_settings
import logging
import os

logger = logging.getLogger(__name__)

class WhisperTranscriptionTool(BaseTool):
    name: str = "whisper_transcription"
    description: str = """
    Transcribe voice messages to text using OpenAI Whisper API.

    Input format:
    {
        "audio_file_path": ".tmp/voice_message.ogg",
        "language": "fr"  # optional
    }
    """

    def _run(self, **kwargs) -> Dict[str, Any]:
        """Synchronous run not implemented."""
        raise NotImplementedError("Use _arun for WhisperTranscriptionTool")

    async def _arun(
        self,
        audio_file_path: str,
        language: Optional[str] = "fr"
    ) -> Dict[str, Any]:
        """Transcibe audio using Whisper API."""
        settings = get_settings()
        if not settings.openai_api_key:
            return {"error": "OPENAI_API_KEY not configured"}

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)

            if not os.path.exists(audio_file_path):
                return {"error": f"Audio file not found: {audio_file_path}"}

            with open(audio_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )

            logger.info(f"✅ Audio transcribed: {audio_file_path}")
            return {
                "text": transcript.text,
                "language": getattr(transcript, 'language', language),
                "duration": getattr(transcript, 'duration', 0)
            }

        except Exception as e:
            logger.error(f"❌ Whisper Error: {e}")
            return {"error": str(e)}

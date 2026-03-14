# Audio agent – Coqui TTS: turns simplified text into speech for dyslexic learners
import os
import tempfile
from typing import Optional


class AudioAgent:
    """Converts text (e.g. simplified course text) to audio using Coqui TTS."""

    def __init__(
        self,
        model_name: str = "tts_models/en/ljspeech/tacotron2-DDC",
        output_dir: Optional[str] = None,
    ):
        self.model_name = model_name
        self.output_dir = output_dir or tempfile.gettempdir()
        self._tts = None

    def _get_tts(self):
        if self._tts is None:
            from TTS.api import TTS
            self._tts = TTS(model_name=self.model_name)
        return self._tts

    def generate_audio(
        self,
        text: str,
        file_path: Optional[str] = None,
        prefix: str = "lesson_audio",
    ) -> str:
        """
        Generate audio from text (intended for simplified text from TextSimplifierAgent).
        Returns path to the generated .wav file.
        """
        if not (text or "").strip():
            raise ValueError("Text cannot be empty for TTS.")

        if file_path is None:
            base = os.path.join(self.output_dir, prefix)
            file_path = f"{base}.wav"
            # Avoid overwriting: use unique name if needed
            if os.path.exists(file_path):
                import uuid
                file_path = os.path.join(
                    self.output_dir, f"{prefix}_{uuid.uuid4().hex[:8]}.wav"
                )

        tts = self._get_tts()
        tts.tts_to_file(text=text, file_path=file_path)
        return file_path

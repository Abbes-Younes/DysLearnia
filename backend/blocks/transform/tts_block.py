"""
blocks/transform/tts_block.py — Text-to-Speech block.

Synthesises speech from text using either:
  1. Kokoro-82M (local, preferred — if kokoro package is installed)
  2. pyttsx3 (fallback — slower, more robotic)
"""
from __future__ import annotations

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block


@register_block
class TTSBlock(IBlock):
    description = BlockDescription(
        name="tts",
        display_name="Text-to-Speech",
        group="transform",
        input_types=["text"],
        output_types=["binary/wav"],
        parameters=[
            {
                "name": "speed",
                "type": "slider",
                "min": 0.5,
                "max": 2.0,
                "default": 1.0,
                "label": "Speech speed",
            },
            {
                "name": "voice",
                "type": "select",
                "options": ["warm_female", "neutral_male", "clear_female"],
                "default": "warm_female",
                "label": "Voice style",
            },
        ],
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        text = self.first_text(inputs)
        if not text:
            return [BlockData(binary=b"", mime_type="audio/wav",
                              metadata={"error": "No text input"})]

        speed = float(params.get("speed", 1.0))
        voice = params.get("voice", "warm_female")

        wav_bytes = await self._synthesise(text, speed, voice)

        return [BlockData(
            binary=wav_bytes,
            mime_type="audio/wav",
            metadata={
                "voice": voice,
                "speed": speed,
                "text_length": len(text),
            },
        )]

    async def _synthesise(self, text: str, speed: float, voice: str) -> bytes:
        """Try Kokoro first, fall back to pyttsx3."""
        # 1. Try Kokoro
        try:
            return await self._kokoro_synthesise(text, speed, voice)
        except Exception:
            pass

        # 2. Fall back to pyttsx3 (sync, run in thread)
        try:
            import asyncio
            return await asyncio.get_event_loop().run_in_executor(
                None, self._pyttsx3_synthesise, text, speed
            )
        except Exception:
            pass

        # 3. Return empty WAV header as last resort
        return self._empty_wav()

    async def _kokoro_synthesise(self, text: str, speed: float, voice: str) -> bytes:
        import io
        import asyncio
        from kokoro import KPipeline  # type: ignore

        voice_map = {
            "warm_female": "af_heart",
            "neutral_male": "am_adam",
            "clear_female": "af_sarah",
        }
        kokoro_voice = voice_map.get(voice, "af_heart")

        pipeline = KPipeline(lang_code="a")  # English
        samples: list[bytes] = []

        def _run():
            for _, _, audio in pipeline(text, voice=kokoro_voice, speed=speed):
                import soundfile as sf
                buf = io.BytesIO()
                sf.write(buf, audio, 24000, format="WAV")
                samples.append(buf.getvalue())

        await asyncio.get_event_loop().run_in_executor(None, _run)

        # Concatenate WAV chunks (simple byte concat — headers only in first)
        if not samples:
            return self._empty_wav()
        return samples[0] if len(samples) == 1 else b"".join(samples)

    def _pyttsx3_synthesise(self, text: str, speed: float) -> bytes:
        import io
        import pyttsx3
        import tempfile
        import os

        engine = pyttsx3.init()
        rate = engine.getProperty("rate")
        engine.setProperty("rate", int(rate * speed))

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        try:
            engine.save_to_file(text, tmp_path)
            engine.runAndWait()
            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def _empty_wav() -> bytes:
        """Minimal valid WAV file (44-byte header, 0 samples)."""
        import struct
        data_size = 0
        return struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF", 36 + data_size, b"WAVE",
            b"fmt ", 16, 1, 1,
            22050, 22050 * 2, 2, 16,
            b"data", data_size,
        )

"""
blocks/output/unifiers/audio_unifier.py — MP3 audio export unifier block.

Accepts text sections or binary WAV clips from upstream blocks,
synthesises missing text via TTS, concatenates everything, and exports as MP3.
Uses pydub for concatenation/normalisation.
"""
from __future__ import annotations

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block


@register_block
class AudioUnifierBlock(IBlock):
    description = BlockDescription(
        name="audio_unifier",
        display_name="Export as Audio",
        group="output",
        input_types=["text", "binary/wav"],
        output_types=["binary/mp3"],
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
            },
            {
                "name": "silence_between_s",
                "type": "slider",
                "min": 0.0,
                "max": 3.0,
                "default": 0.5,
                "label": "Silence between sections (seconds)",
            },
        ],
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        try:
            from pydub import AudioSegment  # type: ignore
        except ImportError:
            return [BlockData(
                text="[Audio export unavailable — pydub not installed]",
                mime_type="text/plain",
            )]

        from io import BytesIO

        silence_ms = int(params.get("silence_between_s", 0.5) * 1000)
        pause = AudioSegment.silent(duration=silence_ms)
        combined = AudioSegment.empty()

        for bd in inputs:
            if bd.binary and bd.mime_type == "audio/wav":
                # Pre-rendered WAV from TTS block — append directly
                seg = AudioSegment.from_wav(BytesIO(bd.binary))
            elif bd.text:
                # Raw text — synthesise on-the-fly via TTSBlock helper
                wav_bytes = await self._synthesise_text(
                    bd.text,
                    speed=params.get("speed", 1.0),
                    voice=params.get("voice", "warm_female"),
                )
                if not wav_bytes:
                    continue
                seg = AudioSegment.from_wav(BytesIO(wav_bytes))
            else:
                continue

            combined = combined + seg + pause

        if len(combined) == 0:
            return [BlockData(
                text="[Audio unifier: no audio content to export]",
                mime_type="text/plain",
            )]

        combined = combined.normalize()
        out = BytesIO()
        combined.export(out, format="mp3", bitrate="128k")

        return [BlockData(
            binary=out.getvalue(),
            mime_type="audio/mpeg",
            metadata={
                "filename": "dyslearnia_export.mp3",
                "duration_s": len(combined) / 1000,
            },
        )]

    @staticmethod
    async def _synthesise_text(text: str, speed: float, voice: str) -> bytes | None:
        """Delegate to TTSBlock for synthesis."""
        try:
            from blocks.transform.tts_block import TTSBlock
            tts = TTSBlock()
            results = await tts.execute(
                [BlockData(text=text)],
                {"speed": speed, "voice": voice},
            )
            if results and results[0].binary:
                return results[0].binary
        except Exception:
            pass
        return None

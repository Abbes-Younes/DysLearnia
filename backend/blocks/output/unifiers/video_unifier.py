"""
blocks/output/unifiers/video_unifier.py — MP4 video export unifier block.

Accepts slide PNGs + optional WAV narration, produces an MP4 using MoviePy v2.
"""
from __future__ import annotations

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block


@register_block
class VideoUnifierBlock(IBlock):
    description = BlockDescription(
        name="video_unifier",
        display_name="Export as Video",
        group="output",
        input_types=["binary/png", "binary/wav"],
        output_types=["binary/mp4"],
        parameters=[
            {
                "name": "seconds_per_slide",
                "type": "slider",
                "min": 3,
                "max": 30,
                "default": 8,
                "label": "Seconds per slide",
            },
            {
                "name": "resolution",
                "type": "select",
                "options": ["1280x720", "1920x1080"],
                "default": "1280x720",
            },
            {
                "name": "fps",
                "type": "select",
                "options": ["24", "30"],
                "default": "24",
            },
            {
                "name": "show_captions",
                "type": "toggle",
                "default": True,
                "label": "Overlay text captions",
            },
        ],
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        try:
            from moviepy import (  # type: ignore
                ImageClip,
                AudioFileClip,
                CompositeVideoClip,
                TextClip,
                concatenate_videoclips,
            )
        except ImportError:
            return [BlockData(
                text="[Video export unavailable — moviepy not installed]",
                mime_type="text/plain",
            )]

        import asyncio
        import os
        import tempfile

        png_inputs = [bd for bd in inputs if bd.mime_type == "image/png" and bd.binary]
        wav_inputs = [bd for bd in inputs if bd.mime_type == "audio/wav" and bd.binary]
        text_inputs = [bd for bd in inputs if bd.text]

        if not png_inputs:
            return [BlockData(
                text="[Video unifier: no PNG slide inputs found]",
                mime_type="text/plain",
            )]

        secs = int(params.get("seconds_per_slide", 8))
        fps = int(params.get("fps", 24))
        w, h = (int(x) for x in params.get("resolution", "1280x720").split("x"))
        show_captions = params.get("show_captions", True)

        def _build_video() -> bytes:
            with tempfile.TemporaryDirectory() as tmp:
                clips = []
                for i, png_bd in enumerate(png_inputs):
                    img_path = os.path.join(tmp, f"slide_{i}.png")
                    with open(img_path, "wb") as f:
                        f.write(png_bd.binary)

                    clip = ImageClip(img_path).with_duration(secs).resized((w, h))

                    if show_captions and i < len(text_inputs):
                        caption = (text_inputs[i].text or "")[:120]
                        if caption:
                            txt = (
                                TextClip(
                                    caption,
                                    font_size=24,
                                    color="white",
                                    bg_color="rgba(0,0,0,0.5)",
                                    size=(w - 40, None),
                                )
                                .with_position(("center", h - 100))
                                .with_duration(secs)
                            )
                            clip = CompositeVideoClip([clip, txt])

                    clips.append(clip)

                video = concatenate_videoclips(clips, method="compose")

                if wav_inputs:
                    wav_path = os.path.join(tmp, "narration.wav")
                    with open(wav_path, "wb") as f:
                        f.write(wav_inputs[0].binary)
                    audio = AudioFileClip(wav_path)
                    video = video.with_audio(audio)

                out_path = os.path.join(tmp, "output.mp4")
                video.write_videofile(
                    out_path,
                    fps=fps,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    ffmpeg_params=["-pix_fmt", "yuv420p"],
                    logger=None,
                )
                with open(out_path, "rb") as f:
                    return f.read()

        mp4_bytes = await asyncio.get_event_loop().run_in_executor(None, _build_video)

        return [BlockData(
            binary=mp4_bytes,
            mime_type="video/mp4",
            metadata={"filename": "dyslearnia_export.mp4"},
        )]

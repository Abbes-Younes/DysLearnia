"""
blocks/transform/dyslexia_font.py — Dyslexia font block.

Reformats plain text as HTML using OpenDyslexic font with adjustable
spacing and line height. No LLM required — pure HTML reformatter.
"""
from __future__ import annotations

import html

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block

_OPENDYSLEXIC_CDN = (
    "https://cdn.jsdelivr.net/npm/open-dyslexic@1.0.3/open-dyslexic-regular.woff2"
)

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <style>
    @font-face {{
      font-family: 'OpenDyslexic';
      src: url('{cdn}') format('woff2');
    }}
    body {{
      font-family: {font}, Arial, sans-serif;
      font-size: {font_size}pt;
      line-height: {line_height};
      letter-spacing: {letter_spacing}em;
      word-spacing: {word_spacing}em;
      max-width: 760px;
      margin: 2em auto;
      padding: 1em;
      background: {bg_color};
      color: {text_color};
    }}
    p {{
      margin-bottom: 1.2em;
    }}
  </style>
</head>
<body>
{content}
</body>
</html>
"""


@register_block
class DyslexiaFontBlock(IBlock):
    description = BlockDescription(
        name="dyslexia_font",
        display_name="Dyslexia Font",
        group="transform",
        input_types=["text"],
        output_types=["text"],
        parameters=[
            {
                "name": "font",
                "type": "select",
                "options": ["OpenDyslexic", "Arial", "Verdana"],
                "default": "OpenDyslexic",
            },
            {
                "name": "font_size",
                "type": "slider",
                "min": 10,
                "max": 24,
                "default": 14,
                "label": "Font size (pt)",
            },
            {
                "name": "line_height",
                "type": "slider",
                "min": 1.2,
                "max": 3.0,
                "default": 1.8,
                "label": "Line height",
            },
            {
                "name": "letter_spacing",
                "type": "slider",
                "min": 0.0,
                "max": 0.3,
                "default": 0.05,
                "label": "Letter spacing (em)",
            },
            {
                "name": "word_spacing",
                "type": "slider",
                "min": 0.0,
                "max": 0.5,
                "default": 0.1,
                "label": "Word spacing (em)",
            },
            {
                "name": "bg_color",
                "type": "color",
                "default": "#FFFDE7",
                "label": "Background colour (cream reduces visual stress)",
            },
        ],
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        text = self.first_text(inputs)
        if not text:
            return [BlockData(text="", mime_type="text/html",
                              metadata={"error": "No text input"})]

        font = params.get("font", "OpenDyslexic")
        font_size = params.get("font_size", 14)
        line_height = params.get("line_height", 1.8)
        letter_spacing = params.get("letter_spacing", 0.05)
        word_spacing = params.get("word_spacing", 0.1)
        bg_color = params.get("bg_color", "#FFFDE7")

        # Convert plain text paragraphs to <p> tags
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        html_content = "\n".join(
            f"<p>{html.escape(p).replace(chr(10), '<br/>')}</p>"
            for p in paragraphs
        )

        rendered = _HTML_TEMPLATE.format(
            cdn=_OPENDYSLEXIC_CDN,
            font=font,
            font_size=font_size,
            line_height=line_height,
            letter_spacing=letter_spacing,
            word_spacing=word_spacing,
            bg_color=bg_color,
            text_color="#111111",
            content=html_content,
        )

        return [BlockData(
            text=rendered,
            mime_type="text/html",
            metadata={
                "font": font,
                "font_size": font_size,
                "line_height": line_height,
            },
        )]

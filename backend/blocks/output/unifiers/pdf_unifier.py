"""
blocks/output/unifiers/pdf_unifier.py — PDF export unifier block.

Accepts markdown text + PNG infographics from upstream blocks
and renders a downloadable PDF using WeasyPrint.
"""
from __future__ import annotations

from blocks.base import BlockData, BlockDescription, IBlock
from blocks.registry import register_block


@register_block
class PDFUnifierBlock(IBlock):
    description = BlockDescription(
        name="pdf_unifier",
        display_name="Export as PDF",
        group="output",
        input_types=["text", "binary/png"],
        output_types=["binary/pdf"],
        parameters=[
            {
                "name": "font_size",
                "type": "slider",
                "min": 10,
                "max": 20,
                "default": 13,
                "label": "Font size (pt)",
            },
            {
                "name": "include_toc",
                "type": "toggle",
                "default": True,
                "label": "Include table of contents",
            },
            {
                "name": "theme",
                "type": "select",
                "options": ["clean", "dyslexia", "dark"],
                "default": "clean",
            },
        ],
    )

    async def execute(self, inputs: list[BlockData], params: dict) -> list[BlockData]:
        try:
            import markdown as md_lib
            from weasyprint import HTML
        except ImportError as exc:
            return [BlockData(
                text=f"[PDF export unavailable — missing dependency: {exc}]",
                mime_type="text/plain",
            )]

        import base64

        md_parts = [bd.text for bd in inputs if bd.text]
        png_parts = [bd.binary for bd in inputs if bd.mime_type == "image/png" and bd.binary]

        font_size = params.get("font_size", 13)
        theme = params.get("theme", "clean")
        include_toc = params.get("include_toc", True)

        # Markdown → HTML
        full_md = "\n\n---\n\n".join(md_parts)
        extensions = ["tables", "fenced_code"]
        if include_toc:
            extensions.append("toc")
        body_html = md_lib.markdown(full_md, extensions=extensions)

        # Embed infographic PNGs
        img_tags = "".join(
            f'<figure><img src="data:image/png;base64,'
            f'{base64.b64encode(png).decode()}" '
            f'style="max-width:100%;page-break-inside:avoid"/></figure>'
            for png in png_parts
        )

        theme_css = self._theme_css(theme, font_size)
        html = f"""<!DOCTYPE html><html><head>
            <meta charset="utf-8"/>
            <style>{theme_css}</style>
        </head><body>{body_html}{img_tags}</body></html>"""

        pdf_bytes = HTML(string=html, base_url="").write_pdf()

        return [BlockData(
            binary=pdf_bytes,
            mime_type="application/pdf",
            metadata={"filename": "dyslearnia_export.pdf"},
        )]

    @staticmethod
    def _theme_css(theme: str, font_size: int) -> str:
        base = f"""
            @page {{ margin: 2cm; }}
            body {{
                font-size: {font_size}pt;
                line-height: 1.7;
                font-family: Georgia, serif;
            }}
            h1, h2, h3 {{ font-family: Arial, sans-serif; color: #2D4A8A; }}
            img {{ max-width: 100%; }}
            table {{ border-collapse: collapse; width: 100%; }}
            td, th {{ border: 1px solid #ccc; padding: 6px; }}
            pre {{ background: #f4f4f4; padding: 1em; border-radius: 4px; }}
            hr {{ border: none; border-top: 1px solid #ddd; margin: 2em 0; }}
            figure {{ margin: 1em 0; }}
        """
        if theme == "dyslexia":
            base += (
                "body { font-family: OpenDyslexic, Arial; "
                "letter-spacing: 0.1em; line-height: 2; "
                "background: #FFFDE7; }"
            )
        elif theme == "dark":
            base += (
                "body { background: #1e1e1e; color: #eee; } "
                "h1, h2, h3 { color: #64B5F6; }"
            )
        return base

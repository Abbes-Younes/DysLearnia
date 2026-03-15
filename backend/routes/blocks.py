"""
routes/blocks.py — Block registry endpoint.

GET /api/blocks returns the full block catalogue for the frontend palette.
The frontend uses this to populate the drag-and-drop sidebar and validate edges.
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Blocks"])


@router.get(
    "/blocks",
    summary="List all registered blocks",
    response_description="Array of BlockDescription objects",
    responses={
        200: {
            "description": "Full block catalogue",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "name": "summarizer",
                            "display_name": "Summarizer",
                            "group": "transform",
                            "input_types": ["text"],
                            "output_types": ["text"],
                            "parameters": [
                                {"name": "ratio", "type": "slider", "min": 0.1, "max": 0.9, "default": 0.4}
                            ],
                        }
                    ]
                }
            },
        }
    },
)
async def list_blocks():
    """
    Returns the full block registry as a JSON array.

    Each object describes one block type with:
    - `name`: machine key used in pipeline node `type` field
    - `display_name`: human-readable UI label
    - `group`: palette group (`input` | `transform` | `output`)
    - `input_types`: accepted upstream output types
    - `output_types`: types this block produces
    - `parameters`: schema for the block config panel (sliders, selects, toggles)
    """
    from blocks.registry import get_registry_schema
    return JSONResponse(content=get_registry_schema())

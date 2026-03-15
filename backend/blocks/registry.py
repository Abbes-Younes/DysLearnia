"""
blocks/registry.py — Auto-discovery registry for IBlock implementations.

Usage:
    @register_block
    class MyBlock(IBlock):
        description = BlockDescription(name="my_block", ...)

GET /api/blocks returns the full registry as JSON for the frontend palette.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blocks.base import IBlock

BLOCK_REGISTRY: dict[str, type["IBlock"]] = {}


def register_block(cls: type["IBlock"]) -> type["IBlock"]:
    """Class decorator that adds the block to the global registry."""
    BLOCK_REGISTRY[cls.description.name] = cls
    return cls


def get_registry_schema() -> list[dict]:
    """
    Serialize the full registry to a list of BlockDescription dicts.
    Used by GET /api/blocks.
    """
    schema = []
    for block_cls in BLOCK_REGISTRY.values():
        desc = block_cls.description
        schema.append({
            "name": desc.name,
            "display_name": desc.display_name,
            "group": desc.group,
            "input_types": desc.input_types,
            "output_types": desc.output_types,
            "parameters": desc.parameters,
        })
    return sorted(schema, key=lambda b: (b["group"], b["name"]))

"""Stage 2 — file_suggestion.

Decides which uploaded files serve the objective and what role each plays.
Mirrors the course's file_suggestion_agent (which recommends input files).
"""
from __future__ import annotations

from typing import Any

from .. import llm

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "selections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "include": {"type": "boolean"},
                    "role": {"type": "string", "description": "How this file feeds the graph."},
                },
                "required": ["name", "include", "role"],
            },
        }
    },
    "required": ["selections"],
}

_SYSTEM = (
    "You are the file-suggestion agent. Given the objective and a preview of each "
    "uploaded file, decide which files to include and what role each plays "
    "(e.g. 'defines Product nodes', 'review text for sentiment extraction'). "
    "Include a file unless it is clearly irrelevant to the objective."
)


def select(objective: str, source_previews: list[str]) -> dict[str, Any]:
    user = f"OBJECTIVE: {objective}\n\nFILES:\n" + "\n".join(source_previews)
    return llm.structured(_SYSTEM, user, _SCHEMA)

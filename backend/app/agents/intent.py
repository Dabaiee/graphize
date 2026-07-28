"""Stage 1 — user_intent.

The course captures intent through a dialogue. We capture it from the one-time
form the user filled, plus a peek at their data, in a single structured call.
"""
from __future__ import annotations

from typing import Any

from .. import llm

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "objective": {"type": "string", "description": "One-sentence goal for the graph."},
        "entity_types": {"type": "array", "items": {"type": "string"}},
        "relationship_types": {"type": "array", "items": {"type": "string"}},
        "key_things": {
            "type": "array", "items": {"type": "string"},
            "description": "Specific things the user cares about tracking.",
        },
        "summary": {"type": "string", "description": "Plain-language recap of what we'll build."},
    },
    "required": ["objective", "entity_types", "relationship_types", "key_things", "summary"],
}

_SYSTEM = (
    "You are the intent agent for an automated knowledge-graph builder. "
    "From the user's plain-language answers and a sample of their data, infer a "
    "concrete objective and a candidate set of entity and relationship types. "
    "Prefer types that are actually supported by the data. Keep names short and "
    "TitleCase for entities, UPPER_SNAKE for relationships."
)


def analyze(answers: dict[str, str], source_previews: list[str]) -> dict[str, Any]:
    about = answers.get("about", "").strip()
    questions = answers.get("questions", "").strip()
    track = answers.get("track", "").strip()

    user = (
        "USER ANSWERS\n"
        f"- What is this data about?: {about or '(blank — infer from data)'}\n"
        f"- What do you want to ask it?: {questions or '(blank — infer from data)'}\n"
        f"- Specific things to track?: {track or '(blank — auto-detect)'}\n\n"
        "DATA SAMPLE\n" + "\n".join(source_previews)
    )
    return llm.structured(_SYSTEM, user, _SCHEMA)

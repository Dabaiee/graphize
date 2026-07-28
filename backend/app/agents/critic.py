"""Stage 6 — critic / evaluation (enhancement over the course reference).

Checks the finished graph against the objective. Non-blocking: its findings are
surfaced to the user but do not stop the build.
"""
from __future__ import annotations

from typing import Any

from .. import llm

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "coverage_ok": {"type": "boolean"},
        "verdict": {"type": "string", "description": "One-line assessment."},
        "issues": {"type": "array", "items": {"type": "string"}},
        "suggestions": {"type": "array", "items": {"type": "string"}},
        "example_questions": {
            "type": "array", "items": {"type": "string"},
            "description": "Questions the graph can now answer, to show the user.",
        },
    },
    "required": ["coverage_ok", "verdict", "issues", "suggestions", "example_questions"],
}

_SYSTEM = (
    "You are the critic agent. Given the user's objective, the schema, and stats "
    "about the built graph (node/relationship counts, labels, orphans), judge "
    "whether the graph plausibly supports the objective. Flag concrete gaps "
    "(missing entity types, no relationships, empty extraction) and give short "
    "suggestions. Also propose a few example questions the graph can answer."
)


def critique(objective: str, schema: dict[str, Any], stats: dict[str, Any]) -> dict[str, Any]:
    labels = schema.get("node_types", [])
    rels = schema.get("relationship_types", [])
    user = (
        f"OBJECTIVE: {objective}\n\n"
        f"SCHEMA node types: {[n['label'] for n in labels]}\n"
        f"SCHEMA relationship types: {[r['type'] for r in rels]}\n\n"
        f"BUILT GRAPH STATS: {stats}"
    )
    return llm.structured(_SYSTEM, user, _SCHEMA, max_tokens=3000)

"""Stage 5 — entity resolution (enhancement over the course reference).

Given the deduped-by-exact-name entity list, find entities that refer to the
same real-world thing under different surface forms ("IBM" / "I.B.M." /
"International Business Machines") and merge them into a canonical node.
"""
from __future__ import annotations

from typing import Any

from .. import llm

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "merges": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "canonical_uid": {"type": "string"},
                    "duplicate_uids": {"type": "array", "items": {"type": "string"}},
                    "reason": {"type": "string"},
                },
                "required": ["canonical_uid", "duplicate_uids", "reason"],
            },
        }
    },
    "required": ["merges"],
}

_SYSTEM = (
    "You are the entity-resolution agent. You are given a list of graph nodes "
    "(uid, type, name). Identify groups that refer to the SAME real-world entity "
    "under different spellings, abbreviations, or casings. Only merge within the "
    "same type, and only when you are confident. Pick the clearest/longest form "
    "as the canonical. Return no merges if unsure."
)


def resolve(entities: list[dict[str, Any]]) -> dict[str, Any]:
    # Bound the payload; resolution on very large sets is skipped by the caller.
    listing = "\n".join(f"{e['uid']} | {e['type']} | {e['name']}" for e in entities)
    user = "NODES (uid | type | name):\n" + listing
    return llm.structured(_SYSTEM, user, _SCHEMA, max_tokens=4000)

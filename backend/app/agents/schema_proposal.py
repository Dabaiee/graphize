"""Stage 3 — schema_proposal.

Produces the graph schema AND the concrete mapping used to build it:
  - structured_mappings: how each CSV/table becomes nodes + relationships
    (deterministic build — no per-row LLM calls).
  - unstructured_targets: which entity/relationship types to extract from text
    (per-chunk LLM extraction downstream).
"""
from __future__ import annotations

from typing import Any

from .. import llm

_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "node_types": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "label": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["label", "description"],
            },
        },
        "relationship_types": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"type": "string"},
                    "source_label": {"type": "string"},
                    "target_label": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["type", "source_label", "target_label", "description"],
            },
        },
        "structured_mappings": {
            "type": "array",
            "description": "One mapping per structured (tabular) source file.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "source": {"type": "string", "description": "Exact filename."},
                    "node_label": {"type": "string"},
                    "key_column": {"type": "string", "description": "Column that identifies each row's node."},
                    "property_columns": {"type": "array", "items": {"type": "string"}},
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "type": {"type": "string"},
                                "target_label": {"type": "string"},
                                "via_column": {"type": "string", "description": "Column whose value is the target node's key."},
                            },
                            "required": ["type", "target_label", "via_column"],
                        },
                    },
                },
                "required": ["source", "node_label", "key_column", "property_columns", "relationships"],
            },
        },
        "unstructured_targets": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "entity_types": {"type": "array", "items": {"type": "string"}},
                "relationship_types": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["entity_types", "relationship_types"],
        },
    },
    "required": [
        "node_types", "relationship_types",
        "structured_mappings", "unstructured_targets",
    ],
}

_SYSTEM = (
    "You are the schema-proposal agent for an automated knowledge-graph builder. "
    "Design a concrete, buildable graph schema from the objective and data.\n\n"
    "Rules:\n"
    "- For each STRUCTURED source, produce a structured_mapping: pick the column "
    "that best identifies each row (key_column), the columns to keep as node "
    "properties, and any columns that reference another node type (relationships "
    "via that column's value).\n"
    "- via_column values must match the KEY of the target node type so rows link "
    "up. Only create a relationship when a column plausibly references another "
    "entity.\n"
    "- For UNSTRUCTURED sources, list the entity_types and relationship_types worth "
    "extracting from the text. Reuse structured node labels where the text refers "
    "to the same things, so the two halves connect into one graph.\n"
    "- Entity labels TitleCase, relationship types UPPER_SNAKE. Keep the schema "
    "tight — only what the objective needs."
)


def propose(intent: dict[str, Any], source_previews: list[str]) -> dict[str, Any]:
    user = (
        f"OBJECTIVE: {intent['objective']}\n"
        f"CANDIDATE ENTITY TYPES: {intent['entity_types']}\n"
        f"CANDIDATE RELATIONSHIP TYPES: {intent['relationship_types']}\n"
        f"KEY THINGS TO TRACK: {intent['key_things']}\n\n"
        "DATA (each file with columns / text sample):\n" + "\n".join(source_previews)
    )
    return llm.structured(_SYSTEM, user, _SCHEMA, max_tokens=8000)

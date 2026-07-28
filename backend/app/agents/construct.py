"""Stage 4 — graph_construction.

Two paths:
  - build_structured(): deterministic. Turns CSV/table rows into nodes + edges
    using the schema's structured_mapping. No LLM per row.
  - extract_chunk(): per-chunk LLM extraction for unstructured text, against the
    schema's unstructured_targets. The orchestrator fans these out in parallel.
"""
from __future__ import annotations

from typing import Any

from . import make_uid
from .. import llm
from ..ingest import Source

# ---------------------------------------------------------------------------
# Structured (deterministic)
# ---------------------------------------------------------------------------

def build_structured(mapping: dict[str, Any], source: Source) -> tuple[list[dict], list[dict]]:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    label = mapping["node_label"]
    key_col = mapping["key_column"]
    prop_cols = mapping.get("property_columns", [])
    rels = mapping.get("relationships", [])

    for row in source.rows:
        key_val = row.get(key_col)
        if key_val in (None, ""):
            continue
        uid = make_uid(label, key_val)
        props = {c: row[c] for c in prop_cols if row.get(c) not in (None, "")}
        nodes[uid] = {"uid": uid, "label": label, "name": str(key_val), "properties": props}

        for rel in rels:
            target_val = row.get(rel.get("via_column"))
            if target_val in (None, ""):
                continue
            target_label = rel["target_label"]
            t_uid = make_uid(target_label, target_val)
            # Ensure the referenced node exists (minimal stub; enriched if its own
            # source is also loaded, since uid is deterministic).
            nodes.setdefault(
                t_uid,
                {"uid": t_uid, "label": target_label, "name": str(target_val), "properties": {}},
            )
            edges.append({"source": uid, "target": t_uid, "type": rel["type"], "properties": {}})

    return list(nodes.values()), edges


# ---------------------------------------------------------------------------
# Unstructured (LLM extraction, one call per chunk)
# ---------------------------------------------------------------------------

_EXTRACT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                },
                "required": ["name", "type"],
            },
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "source_name": {"type": "string"},
                    "source_type": {"type": "string"},
                    "target_name": {"type": "string"},
                    "target_type": {"type": "string"},
                    "type": {"type": "string"},
                },
                "required": ["source_name", "source_type", "target_name", "target_type", "type"],
            },
        },
    },
    "required": ["entities", "relationships"],
}

_EXTRACT_SYSTEM = (
    "You extract a knowledge graph from a single passage of text. Only emit "
    "entities whose type is in the allowed entity types, and relationships whose "
    "type is in the allowed relationship types. Use names exactly as they appear "
    "in the text. Do not invent facts not stated in the passage. If nothing "
    "relevant appears, return empty lists."
)


def extract_chunk(
    text: str,
    entity_types: list[str],
    relationship_types: list[str],
) -> dict[str, Any]:
    user = (
        f"ALLOWED ENTITY TYPES: {entity_types}\n"
        f"ALLOWED RELATIONSHIP TYPES: {relationship_types}\n\n"
        f"TEXT:\n{text}"
    )
    return llm.structured(_EXTRACT_SYSTEM, user, _EXTRACT_SCHEMA, max_tokens=3000)


def chunk_to_graph(extraction: dict[str, Any]) -> tuple[list[dict], list[dict], list[str]]:
    """Convert one chunk's extraction into (nodes, edges, mentioned_uids)."""
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    mentions: set[str] = set()

    for ent in extraction.get("entities", []):
        uid = make_uid(ent["type"], ent["name"])
        nodes[uid] = {"uid": uid, "label": ent["type"], "name": ent["name"], "properties": {}}
        mentions.add(uid)

    for rel in extraction.get("relationships", []):
        s_uid = make_uid(rel["source_type"], rel["source_name"])
        t_uid = make_uid(rel["target_type"], rel["target_name"])
        nodes.setdefault(s_uid, {"uid": s_uid, "label": rel["source_type"], "name": rel["source_name"], "properties": {}})
        nodes.setdefault(t_uid, {"uid": t_uid, "label": rel["target_type"], "name": rel["target_name"], "properties": {}})
        edges.append({"source": s_uid, "target": t_uid, "type": rel["type"], "properties": {}})
        mentions.update({s_uid, t_uid})

    return list(nodes.values()), edges, list(mentions)

"""Stage 7 — graphrag (query time).

Answers a natural-language question over the finished graph by combining:
  1. full-text retrieval of relevant entities and their neighborhoods,
  2. full-text retrieval of relevant source chunks,
  3. an optional model-generated READ-ONLY Cypher query (guarded).
Then grounds an answer with adaptive thinking, citing what it used.
"""
from __future__ import annotations

from typing import Any

from .. import graph, llm

_CYPHER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "should_query": {"type": "boolean", "description": "True if a graph query helps."},
        "cypher": {"type": "string", "description": "A single read-only Cypher query, or empty."},
    },
    "required": ["should_query", "cypher"],
}

_CYPHER_SYSTEM = (
    "You translate a question into ONE read-only Cypher query over a Neo4j graph. "
    "All entities share the label :Entity plus a specific label; each has "
    ".name and .type. Relationships are typed. Use MATCH/WHERE/RETURN only — never "
    "write. Prefer matching on n.name with toLower() CONTAINS. Always add LIMIT 25. "
    "If a query won't help, set should_query=false and cypher to an empty string."
)

_ANSWER_SYSTEM = (
    "You answer the user's question using ONLY the provided graph context "
    "(entities, relationships, query results, and source snippets). If the context "
    "is insufficient, say so plainly. Be concise and cite what you used, e.g. "
    "'(from graph)' or the source filename for snippets."
)


def _graph_query(question: str, labels: list[str]) -> list[dict] | None:
    try:
        plan = llm.structured(
            _CYPHER_SYSTEM,
            f"LABELS: {labels}\nQUESTION: {question}",
            _CYPHER_SCHEMA,
            max_tokens=1500,
        )
    except Exception:
        return None
    if not plan.get("should_query") or not plan.get("cypher", "").strip():
        return None
    try:
        return graph.run_read(plan["cypher"])
    except Exception:
        return None


def answer(question: str) -> dict[str, Any]:
    stats = graph.stats()
    entities = graph.search_entities(question, limit=8)
    chunks = graph.search_chunks(question, limit=4)
    query_rows = _graph_query(question, stats.get("labels", []))

    context_parts: list[str] = []
    if entities:
        ent_lines = [
            f"- {e['name']} ({e['type']}): " + "; ".join(e.get("rels") or []) if e.get("rels")
            else f"- {e['name']} ({e['type']})"
            for e in entities
        ]
        context_parts.append("RELEVANT ENTITIES & CONNECTIONS:\n" + "\n".join(ent_lines))
    if query_rows:
        context_parts.append(f"GRAPH QUERY RESULTS:\n{query_rows}")
    if chunks:
        snip = [f"- [{c['source']}] {c['text'][:400]}" for c in chunks]
        context_parts.append("SOURCE SNIPPETS:\n" + "\n".join(snip))

    context = "\n\n".join(context_parts) if context_parts else "(no matching graph context found)"
    text = llm.text(
        _ANSWER_SYSTEM,
        f"GRAPH CONTEXT:\n{context}\n\nQUESTION: {question}",
        thinking=True,
    )
    return {
        "answer": text,
        "used": {
            "entities": [e["name"] for e in entities],
            "sources": sorted({c["source"] for c in chunks}),
            "ran_cypher": query_rows is not None,
        },
    }

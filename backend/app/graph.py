"""Neo4j access + deterministic graph loader.

Design choice: the agents propose a graph as structured JSON (nodes + edges),
and THIS module writes it with parameterized Cypher (via APOC for dynamic
labels/relationship types). We do not execute LLM-generated write Cypher — only
read Cypher, and only for the GraphRAG query step, guarded to read-only.

Retrieval for unstructured text uses a Neo4j full-text (Lucene) index rather
than vector embeddings, so the whole stack stays self-contained with no
embedding provider — Claude is the only external service.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from neo4j import GraphDatabase

from . import config

_driver = GraphDatabase.driver(
    config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
)

# Cypher clauses we refuse to run in the "read-only" query path.
_WRITE_KEYWORDS = (
    "create", "merge", "delete", "set ", "remove", "drop",
    "detach", "load csv", "call apoc.merge", "call apoc.create",
    "foreach", "call db.create", "call dbms",
)


def close() -> None:
    _driver.close()


@contextmanager
def _session():
    with _driver.session() as s:
        yield s


def is_ready() -> bool:
    try:
        with _session() as s:
            s.run("RETURN 1").consume()
        return True
    except Exception:
        return False


def reset() -> None:
    """Wipe the graph (single-graph app: each build starts clean)."""
    with _session() as s:
        s.run("MATCH (n) DETACH DELETE n").consume()


def ensure_indexes() -> None:
    with _session() as s:
        s.run(
            "CREATE FULLTEXT INDEX entityText IF NOT EXISTS "
            "FOR (n:Entity) ON EACH [n.name]"
        ).consume()
        s.run(
            "CREATE FULLTEXT INDEX chunkText IF NOT EXISTS "
            "FOR (c:Chunk) ON EACH [c.text]"
        ).consume()
        s.run(
            "CREATE CONSTRAINT entityId IF NOT EXISTS "
            "FOR (n:Entity) REQUIRE n.uid IS UNIQUE"
        ).consume()


# ---------------------------------------------------------------------------
# Loading (deterministic writes)
# ---------------------------------------------------------------------------

def load_nodes(nodes: list[dict[str, Any]]) -> None:
    """Upsert entity nodes.

    Each node: {uid, label, name, properties: {...}}. `label` becomes a real
    Neo4j label (via APOC) plus the shared :Entity label for indexing.
    """
    if not nodes:
        return
    with _session() as s:
        s.run(
            """
            UNWIND $nodes AS node
            CALL apoc.merge.node(
                ['Entity', node.label],
                {uid: node.uid},
                apoc.map.merge({name: node.name, type: node.label}, node.properties)
            ) YIELD node AS n
            RETURN count(n)
            """,
            nodes=nodes,
        ).consume()


def load_edges(edges: list[dict[str, Any]]) -> None:
    """Upsert relationships. Each edge: {source, target, type, properties}."""
    if not edges:
        return
    with _session() as s:
        s.run(
            """
            UNWIND $edges AS edge
            MATCH (a:Entity {uid: edge.source})
            MATCH (b:Entity {uid: edge.target})
            CALL apoc.merge.relationship(
                a, edge.type, {}, coalesce(edge.properties, {}), b, {}
            ) YIELD rel
            RETURN count(rel)
            """,
            edges=edges,
        ).consume()


def load_chunks(chunks: list[dict[str, Any]]) -> None:
    """Store source text chunks and link them to the entities they mention.

    Each chunk: {uid, text, source, mentions: [entity_uid, ...]}.
    """
    if not chunks:
        return
    with _session() as s:
        s.run(
            """
            UNWIND $chunks AS ch
            MERGE (c:Chunk {uid: ch.uid})
            SET c.text = ch.text, c.source = ch.source
            WITH c, ch
            UNWIND (CASE WHEN ch.mentions = [] THEN [null] ELSE ch.mentions END) AS m
            WITH c, m WHERE m IS NOT NULL
            MATCH (e:Entity {uid: m})
            MERGE (c)-[:MENTIONS]->(e)
            RETURN count(c)
            """,
            chunks=chunks,
        ).consume()


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def stats() -> dict[str, Any]:
    with _session() as s:
        nodes = s.run("MATCH (n:Entity) RETURN count(n) AS c").single()["c"]
        rels = s.run("MATCH (:Entity)-[r]->(:Entity) RETURN count(r) AS c").single()["c"]
        chunks = s.run("MATCH (c:Chunk) RETURN count(c) AS c").single()["c"]
        labels = [
            r["label"]
            for r in s.run(
                "MATCH (n:Entity) UNWIND labels(n) AS label "
                "WITH label WHERE label <> 'Entity' "
                "RETURN DISTINCT label ORDER BY label"
            )
        ]
    return {"nodes": nodes, "relationships": rels, "chunks": chunks, "labels": labels}


def sample_graph(limit: int = 150) -> dict[str, Any]:
    """Return a node/edge sample for visualization."""
    with _session() as s:
        rows = s.run(
            """
            MATCH (a:Entity)-[r]->(b:Entity)
            RETURN a.uid AS s, a.name AS sn, a.type AS st,
                   type(r) AS rt,
                   b.uid AS t, b.name AS tn, b.type AS tt
            LIMIT $limit
            """,
            limit=limit,
        ).data()
    nodes: dict[str, dict] = {}
    edges = []
    for row in rows:
        nodes.setdefault(row["s"], {"id": row["s"], "label": row["sn"], "type": row["st"]})
        nodes.setdefault(row["t"], {"id": row["t"], "label": row["tn"], "type": row["tt"]})
        edges.append({"source": row["s"], "target": row["t"], "type": row["rt"]})
    return {"nodes": list(nodes.values()), "edges": edges}


def search_chunks(query: str, limit: int = 5) -> list[dict[str, Any]]:
    terms = _lucene_terms(query)
    if not terms:
        return []
    with _session() as s:
        return s.run(
            """
            CALL db.index.fulltext.queryNodes('chunkText', $q) YIELD node, score
            RETURN node.text AS text, node.source AS source, score
            ORDER BY score DESC LIMIT $limit
            """,
            q=terms, limit=limit,
        ).data()


def search_entities(query: str, limit: int = 10) -> list[dict[str, Any]]:
    terms = _lucene_terms(query)
    if not terms:
        return []
    with _session() as s:
        return s.run(
            """
            CALL db.index.fulltext.queryNodes('entityText', $q) YIELD node, score
            OPTIONAL MATCH (node)-[r]-(nb:Entity)
            WITH node, score, collect(DISTINCT type(r) + ' -> ' + nb.name)[..8] AS rels
            RETURN node.name AS name, node.type AS type, rels, score
            ORDER BY score DESC LIMIT $limit
            """,
            q=terms, limit=limit,
        ).data()


def run_read(cypher: str, params: dict[str, Any] | None = None, limit: int = 25) -> list[dict]:
    """Execute a read-only Cypher query (used by the GraphRAG agent)."""
    if any(kw in cypher.lower() for kw in _WRITE_KEYWORDS):
        raise ValueError("Only read-only queries are permitted.")
    with _driver.session(default_access_mode="READ") as s:
        return s.run(cypher, params or {}).data()[:limit]


def _lucene_terms(query: str) -> str:
    """Sanitize a natural-language string into a safe Lucene OR-query."""
    import re

    words = re.findall(r"[A-Za-z0-9]+", query)
    stop = {"the", "a", "an", "of", "and", "or", "to", "in", "is", "are",
            "what", "who", "which", "how", "does", "do", "for", "on", "with"}
    words = [w for w in words if w.lower() not in stop and len(w) > 1]
    return " OR ".join(words)

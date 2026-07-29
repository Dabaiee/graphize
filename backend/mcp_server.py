"""Graphize MCP server.

Exposes the Graphize pipeline as MCP tools so any MCP client — Claude Code,
Cursor, Claude Desktop — can build and query a knowledge graph from chat, using
its own Claude access. You run this locally; it talks to a running Neo4j and the
Anthropic API. No hosting, no cost to anyone but the user's own key.

Setup + client config: see docs/MCP.md.
Requires: a reachable Neo4j (NEO4J_URI) and ANTHROPIC_API_KEY in the environment.
"""
from __future__ import annotations

import os
import sys

# Allow `import app` when launched directly as `python backend/mcp_server.py`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from app import graph, orchestrator  # noqa: E402
from app.agents import graphrag  # noqa: E402
from app.ingest import Source, _chunk_text, parse_file  # noqa: E402

mcp = FastMCP("graphize")

_NOOP = lambda _event: None  # noqa: E731  (MCP has no progress stream; discard)


@mcp.tool()
def build_graph_from_text(
    text: str, about: str = "", questions: str = "", track: str = ""
) -> dict:
    """Build a knowledge graph from a block of text.

    Runs the full agent pipeline (intent -> schema -> extraction -> resolution ->
    load) and stores the graph in Neo4j, REPLACING any previous graph. May take a
    minute for large inputs. Optionally steer it with `about` (what the data is),
    `questions` (what you want to ask), `track` (entities to focus on). Returns the
    objective, graph stats, and example questions to try with `ask_graph`.
    """
    if not text.strip():
        return {"error": "text is empty"}
    src = Source(name="pasted.txt", kind="unstructured", chunks=_chunk_text(text))
    r = orchestrator.run_build(
        [src], {"about": about, "questions": questions, "track": track}, _NOOP
    )
    return {
        "objective": r["objective"],
        "stats": r["stats"],
        "example_questions": r["review"]["example_questions"],
    }


@mcp.tool()
def build_graph_from_files(
    paths: list[str], about: str = "", questions: str = "", track: str = ""
) -> dict:
    """Build a knowledge graph from local files (CSV, JSON, PDF, DOCX, TXT/MD).

    `paths` must be absolute paths on this machine. REPLACES any previous graph.
    """
    sources: list[Source] = []
    for p in paths:
        if not os.path.exists(p):
            return {"error": f"file not found: {p}"}
        sources.append(parse_file(p, os.path.basename(p)))
    if not sources:
        return {"error": "no files provided"}
    r = orchestrator.run_build(
        sources, {"about": about, "questions": questions, "track": track}, _NOOP
    )
    return {
        "objective": r["objective"],
        "stats": r["stats"],
        "example_questions": r["review"]["example_questions"],
    }


@mcp.tool()
def ask_graph(question: str) -> dict:
    """Ask a natural-language question over the current knowledge graph (GraphRAG).

    Uses full-text retrieval + a guarded read-only Cypher query. Returns the answer
    and which entities/sources it used. Build a graph first.
    """
    if not graph.is_ready():
        return {"error": "Neo4j is not reachable. Is it running? Check NEO4J_URI."}
    return graphrag.answer(question)


@mcp.tool()
def graph_stats() -> dict:
    """Return counts (nodes, relationships, chunks) and node types of the current graph."""
    if not graph.is_ready():
        return {"error": "Neo4j is not reachable. Is it running? Check NEO4J_URI."}
    return graph.stats()


def main() -> None:
    mcp.run()  # stdio transport


if __name__ == "__main__":
    main()

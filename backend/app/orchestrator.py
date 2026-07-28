"""Runs the full agentic pipeline and streams progress via an `emit` callback.

Synchronous by design (Anthropic + Neo4j clients are sync). The API layer runs
this in a worker thread and bridges `emit` events onto a WebSocket.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

from . import config, graph
from .agents import construct, critic, file_suggestion, graphrag, intent, resolve, schema_proposal
from .ingest import Source

Emit = Callable[[dict[str, Any]], None]

# Above this many distinct entities we skip the single-call resolution pass.
_RESOLVE_LIMIT = 400


def _ev(stage: str, status: str, message: str, **data: Any) -> dict[str, Any]:
    return {"stage": stage, "status": status, "message": message, "data": data}


def run_build(sources: list[Source], answers: dict[str, str], emit: Emit) -> dict[str, Any]:
    previews = [s.preview() for s in sources]

    # 1 — intent -------------------------------------------------------------
    emit(_ev("intent", "start", "Understanding what you want…"))
    spec = intent.analyze(answers, previews)
    emit(_ev("intent", "done", spec["summary"], objective=spec["objective"],
             entity_types=spec["entity_types"], relationship_types=spec["relationship_types"]))

    # 2 — file suggestion ----------------------------------------------------
    emit(_ev("files", "start", "Choosing which files to use…"))
    sel = file_suggestion.select(spec["objective"], previews)
    included = {s["name"] for s in sel["selections"] if s["include"]}
    active = [s for s in sources if s.name in included] or sources  # never drop everything
    emit(_ev("files", "done", f"Using {len(active)} file(s).",
             selections=sel["selections"]))

    # 3 — schema proposal ----------------------------------------------------
    emit(_ev("schema", "start", "Designing the graph schema…"))
    active_previews = [s.preview() for s in active]
    schema = schema_proposal.propose(spec, active_previews)
    emit(_ev("schema", "done",
             f"{len(schema['node_types'])} node types, {len(schema['relationship_types'])} relationship types.",
             node_types=[n["label"] for n in schema["node_types"]],
             relationship_types=[r["type"] for r in schema["relationship_types"]]))

    # 4 — construction -------------------------------------------------------
    emit(_ev("construct", "start", "Extracting entities and relationships…"))
    all_nodes: dict[str, dict] = {}
    all_edges: list[dict] = []
    chunk_records: list[dict] = []

    # 4a structured (deterministic)
    mappings = {m["source"]: m for m in schema.get("structured_mappings", [])}
    for src in active:
        if src.kind == "structured" and src.name in mappings:
            nodes, edges = construct.build_structured(mappings[src.name], src)
            for n in nodes:
                _merge_node(all_nodes, n)
            all_edges.extend(edges)
            emit(_ev("construct", "info", f"{src.name}: {len(nodes)} nodes from {len(src.rows)} rows."))

    # 4b unstructured (parallel LLM extraction)
    targets = schema.get("unstructured_targets", {})
    ent_types = targets.get("entity_types", [])
    rel_types = targets.get("relationship_types", [])
    unstructured = [s for s in active if s.kind == "unstructured"]
    if unstructured and ent_types:
        jobs: list[tuple[str, int, str]] = []  # (source, chunk_index, text)
        for src in unstructured:
            for i, ch in enumerate(src.chunks):
                jobs.append((src.name, i, ch))
        emit(_ev("construct", "info", f"Extracting from {len(jobs)} text chunk(s)…"))
        done = 0
        with ThreadPoolExecutor(max_workers=config.MAX_EXTRACTION_CONCURRENCY) as ex:
            futs = {
                ex.submit(_extract_one, text, ent_types, rel_types): (name, idx, text)
                for (name, idx, text) in jobs
            }
            for fut in as_completed(futs):
                name, idx, text = futs[fut]
                nodes, edges, mentions = fut.result()
                for n in nodes:
                    _merge_node(all_nodes, n)
                all_edges.extend(edges)
                chunk_records.append({
                    "uid": f"{name}:{idx}", "text": text, "source": name, "mentions": mentions,
                })
                done += 1
                if done % 5 == 0 or done == len(jobs):
                    emit(_ev("construct", "info", f"Extracted {done}/{len(jobs)} chunks."))

    emit(_ev("construct", "done",
             f"{len(all_nodes)} nodes, {len(all_edges)} relationships before resolution."))

    # 5 — entity resolution --------------------------------------------------
    emit(_ev("resolve", "start", "Merging duplicate entities…"))
    if 1 < len(all_nodes) <= _RESOLVE_LIMIT:
        try:
            entities = [{"uid": n["uid"], "type": n["label"], "name": n["name"]}
                        for n in all_nodes.values()]
            merges = resolve.resolve(entities)["merges"]
            n_merged = _apply_merges(all_nodes, all_edges, chunk_records, merges)
            emit(_ev("resolve", "done", f"Merged {n_merged} duplicate entities."))
        except Exception as e:  # non-fatal
            emit(_ev("resolve", "done", f"Skipped ({e.__class__.__name__})."))
    else:
        emit(_ev("resolve", "done", "Skipped (graph too large or too small)."))

    # 6 — load into Neo4j ----------------------------------------------------
    emit(_ev("load", "start", "Writing the graph to Neo4j…"))
    graph.reset()
    graph.ensure_indexes()
    graph.load_nodes(list(all_nodes.values()))
    graph.load_edges(all_edges)
    graph.load_chunks(chunk_records)
    stats = graph.stats()
    emit(_ev("load", "done",
             f"Graph stored: {stats['nodes']} nodes, {stats['relationships']} relationships, "
             f"{stats['chunks']} text chunks."))

    # 7 — critic -------------------------------------------------------------
    emit(_ev("critic", "start", "Checking the graph…"))
    review = critic.critique(spec["objective"], schema, stats)
    emit(_ev("critic", "done", review["verdict"],
             issues=review["issues"], suggestions=review["suggestions"],
             example_questions=review["example_questions"]))

    result = {
        "objective": spec["objective"],
        "schema": schema,
        "stats": stats,
        "review": review,
        "graph": graph.sample_graph(),
    }
    emit(_ev("complete", "done", "Your knowledge graph is ready.", result=result))
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_one(text, ent_types, rel_types):
    try:
        extraction = construct.extract_chunk(text, ent_types, rel_types)
        return construct.chunk_to_graph(extraction)
    except Exception:
        return [], [], []


def _merge_node(store: dict[str, dict], node: dict) -> None:
    existing = store.get(node["uid"])
    if existing is None:
        store[node["uid"]] = node
    else:
        # Enrich: prefer non-empty properties, keep longer name.
        existing["properties"].update(node.get("properties") or {})
        if len(node.get("name", "")) > len(existing.get("name", "")):
            existing["name"] = node["name"]


def _apply_merges(nodes: dict[str, dict], edges: list[dict], chunks: list[dict],
                  merges: list[dict]) -> int:
    remap: dict[str, str] = {}
    for m in merges:
        canon = m["canonical_uid"]
        if canon not in nodes:
            continue
        for dup in m["duplicate_uids"]:
            if dup in nodes and dup != canon:
                remap[dup] = canon
                nodes[canon]["properties"].update(nodes[dup].get("properties") or {})
                del nodes[dup]
    if not remap:
        return 0
    for e in edges:
        e["source"] = remap.get(e["source"], e["source"])
        e["target"] = remap.get(e["target"], e["target"])
    for c in chunks:
        c["mentions"] = [remap.get(u, u) for u in c["mentions"]]
    return len(remap)

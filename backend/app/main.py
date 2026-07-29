"""fastGraph API.

Endpoints:
  POST /api/upload         upload files -> a session with parsed sources
  POST /api/sample         create a session from the bundled sample dataset
  WS   /api/build/{sid}    run the pipeline, streaming live progress
  POST /api/chat           ask a question over the finished graph (GraphRAG)
  GET  /api/graph          current graph sample (for the visualization)
  GET  /api/stats          node/relationship counts
  GET  /api/health         readiness
"""
from __future__ import annotations

import asyncio
import os
import uuid
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import config, graph, ingest, llm, orchestrator
from .agents import graphrag
from .ingest import Source, parse_file

app = FastAPI(title="fastGraph", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# In-memory session store: session_id -> [Source]. Fine for a single-graph app.
_SESSIONS: dict[str, list[Source]] = {}

os.makedirs(config.UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    question: str


class ConfigUpdate(BaseModel):
    provider: str | None = None
    anthropic_api_key: str | None = None
    anthropic_model: str | None = None
    openai_api_key: str | None = None
    openai_model: str | None = None
    openai_base_url: str | None = None
    ollama_base_url: str | None = None
    ollama_model: str | None = None


class PasteRequest(BaseModel):
    text: str
    name: str | None = None
    session_id: str | None = None


def _summaries(sources: list[Source]) -> list[dict[str, Any]]:
    out = []
    for s in sources:
        item = {"name": s.name, "kind": s.kind}
        if s.kind == "structured":
            item.update(columns=s.columns, rows=len(s.rows))
        else:
            item.update(chunks=len(s.chunks))
        out.append(item)
    return out


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "neo4j": graph.is_ready(), **config.public()}


@app.get("/api/config")
def get_config() -> dict[str, Any]:
    return config.public()


@app.post("/api/config")
def set_config(body: ConfigUpdate) -> dict[str, Any]:
    patch = {k: v for k, v in body.model_dump().items() if v is not None}
    config.update(patch)
    llm.reset_clients()  # rebuild clients with the new provider/keys
    return config.public()


@app.post("/api/config/test")
def test_config() -> dict[str, Any]:
    """Ping the currently-configured provider so the UI can validate it."""
    return llm.ping()


@app.post("/api/upload")
async def upload(files: list[UploadFile] = File(...)) -> dict[str, Any]:
    sid = uuid.uuid4().hex[:12]
    sources: list[Source] = []
    for f in files:
        dest = os.path.join(config.UPLOAD_DIR, f"{sid}_{f.filename}")
        with open(dest, "wb") as out:
            out.write(await f.read())
        sources.append(parse_file(dest, f.filename))
    _SESSIONS[sid] = sources
    return {"session_id": sid, "sources": _summaries(sources)}


@app.post("/api/paste")
def paste(req: PasteRequest) -> dict[str, Any]:
    """Create (or add to) a session from raw pasted text — no file needed."""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")
    name = (req.name or "pasted-text.txt").strip() or "pasted-text.txt"
    src = Source(name=name, kind="unstructured", chunks=ingest._chunk_text(req.text))

    if req.session_id and req.session_id in _SESSIONS:
        sid = req.session_id
        # Replace any prior paste with the same name; keep other sources.
        _SESSIONS[sid] = [s for s in _SESSIONS[sid] if s.name != name] + [src]
    else:
        sid = uuid.uuid4().hex[:12]
        _SESSIONS[sid] = [src]
    return {"session_id": sid, "sources": _summaries(_SESSIONS[sid])}


@app.post("/api/sample")
def load_sample() -> dict[str, Any]:
    sid = uuid.uuid4().hex[:12]
    base = os.path.join(os.path.dirname(__file__), "..", "sample_data")
    sources: list[Source] = []
    for fname in sorted(os.listdir(base)):
        sources.append(parse_file(os.path.join(base, fname), fname))
    _SESSIONS[sid] = sources
    return {"session_id": sid, "sources": _summaries(sources)}


@app.websocket("/api/build/{session_id}")
async def build(ws: WebSocket, session_id: str) -> None:
    await ws.accept()
    sources = _SESSIONS.get(session_id)
    if not sources:
        await ws.send_json({"stage": "error", "status": "error", "message": "Unknown session."})
        await ws.close()
        return

    answers = await ws.receive_json()  # {about, questions, track}
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def emit(event: dict[str, Any]) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, event)

    def worker() -> None:
        try:
            orchestrator.run_build(sources, answers, emit)
        except Exception as e:  # surface build failures to the client
            emit({"stage": "error", "status": "error", "message": f"{type(e).__name__}: {e}"})
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

    task = loop.run_in_executor(None, worker)
    try:
        while True:
            event = await queue.get()
            if event is None:
                break
            await ws.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        await task
        await ws.close()


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict[str, Any]:
    return graphrag.answer(req.question)


@app.get("/api/graph")
def get_graph() -> dict[str, Any]:
    return graph.sample_graph()


@app.get("/api/stats")
def get_stats() -> dict[str, Any]:
    return graph.stats()

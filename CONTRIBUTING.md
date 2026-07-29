# Contributing to Graphize

Thanks for your interest! Graphize is an open (Apache-2.0) 1-click knowledge-graph
builder. Contributions of all sizes are welcome — bug reports, docs, and PRs.

## Quick start (dev)

```bash
git clone https://github.com/Dabaiee/graphize && cd graphize
cp .env.example .env            # set a provider key, or use Ollama (free/local)
docker compose up -d neo4j      # start the graph store

# backend
cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt
NEO4J_URI=bolt://localhost:7690 .venv/bin/uvicorn app.main:app --reload --port 8180

# frontend (another terminal)
cd frontend && npm install && npm run dev   # http://localhost:5280
```

Or run the whole stack: `./deploy.sh`.

## Project layout
- `backend/app/agents/` — one module per pipeline stage (intent → … → graphrag)
- `backend/app/orchestrator.py` — runs the pipeline, streams progress
- `backend/app/llm.py` — provider-agnostic LLM layer (Anthropic / OpenAI / Ollama)
- `backend/app/graph.py` — Neo4j loader + retrieval
- `backend/mcp_server.py` — MCP integration (`docs/MCP.md`)
- `frontend/src/` — the one-button UI

## How to contribute
1. Open an issue first for anything non-trivial, so we can align on approach.
2. Fork → branch (`feat/…` or `fix/…`) → PR against `main`.
3. Keep PRs focused. Match the surrounding code style (it's plain, comment-light
   where obvious, comment-rich where non-obvious).
4. Test your change: for the pipeline, `docs/TESTCASE.md` has a copy-paste sample.

## Good first issues
Look for the [`good first issue`](https://github.com/Dabaiee/graphize/labels/good%20first%20issue)
label. A few starter areas:
- Add a new file-type parser (e.g. `.html`, `.eml`) in `backend/app/ingest.py`
- Add a provider to `llm.py` (e.g. Google Gemini)
- Graph export (GraphML / Cypher dump)
- UI polish on the graph visualization

## Code of conduct
Be kind and constructive. We're here to build something useful together.

## License
By contributing, you agree your contributions are licensed under the Apache
License 2.0 (see `LICENSE`).

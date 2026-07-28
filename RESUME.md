# 🔄 Resume Package — Graphize

This doc lets you (or a fresh Claude Code session on another device) pick up
exactly where we left off. Read it top to bottom.

## ⏱️ Status at handoff (2026-07-28)
- **Product is built and runs.** Full-stack 1-click agentic knowledge-graph builder.
- **Rebranded** `fastGraph` → **Graphize**.
- **Launch kit written** (README, LICENSE, `marketing/`).
- **Shareable landing page** published (private): https://claude.ai/code/artifact/8ad717e1-f3ac-4343-85a1-6eae1e500e92
- **Not yet done:** real `ANTHROPIC_API_KEY` in `.env` (only a placeholder), the
  demo GIF, pushing GitHub `OWNER`→`Dabaiee` link swaps, and the two roadmap features.

## ▶️ Resume prompt (paste into Claude Code on the new device)
> I'm resuming work on **Graphize** — a 1-click agentic knowledge-graph builder
> (the automated, open-source version of DeepLearning.AI × Neo4j's agentic
> knowledge-graph course). Read `RESUME.md`, then `README.md` and
> `marketing/LAUNCH_PLAN.md`. It's a self-branding/OSS-launch project. Next I want
> to: [pick one] (a) build the two roadmap features (field-type inference +
> hypothetical-question validation), (b) add CONTRIBUTING.md + good-first-issues,
> (c) record/refine the demo and launch. Confirm you're oriented, then proceed.

## 🖥️ Run it on the new device
```bash
git clone https://github.com/Dabaiee/graphize && cd graphize
cp .env.example .env          # set ANTHROPIC_API_KEY=sk-ant-<your real key>
./deploy.sh                   # needs Docker Desktop running
```
| Service | URL |
|---|---|
| App (Graphize UI) | http://localhost:5280 |
| API docs | http://localhost:8180/docs |
| Neo4j browser | http://localhost:7580 (neo4j / fastgraph) |

> Ports were shifted off defaults (5173/8000/7474/7687) so Graphize coexists with
> the **cadence** project. Change host ports in `docker-compose.yml` if needed.

## 🧩 What it is (elevator)
Paste text or drop files → 7 Claude agents build a Neo4j knowledge graph you can
chat with. Marketing wedge: *"DeepLearning.AI/Neo4j/Google shipped a 3-hour course
to hand-build agentic knowledge graphs; I built the 1-click version and shipped the
features their repo lists as TODO (entity resolution + evaluation + unstructured
import)."*

## 🗂️ File map
```
backend/app/
  llm.py            Claude layer (structured outputs via output_config.format)
  ingest.py         CSV/JSON/PDF/DOCX/TXT/paste → normalized sources
  graph.py          Neo4j driver + deterministic APOC loader + full-text retrieval
  orchestrator.py   runs the 7-stage pipeline, streams progress over WebSocket
  main.py           FastAPI: /upload /paste /sample, WS /build, /chat, /graph
  agents/           intent · file_suggestion · schema_proposal · construct ·
                    resolve · critic · graphrag
  sample_data/      products.csv · suppliers.csv · reviews.txt
frontend/src/       App.jsx (1-button UI) · GraphView.jsx · Chat.jsx · api.js
marketing/          CONTENT.md · DEMO_SCRIPT.md · LAUNCH_PLAN.md · landing.html
README.md · LICENSE (add your name) · docker-compose.yml · deploy.sh
```

## 🧠 Pipeline (mirrors the course + our additions)
`intent → file_suggestion → schema_proposal → graph_construction → resolve🆕 → critic🆕 → graphrag`
Structured data builds deterministically from schema mappings; unstructured text
uses parallel per-chunk LLM extraction. 🆕 = shipped past the course reference repo.

## 🧱 Key decisions (so you don't re-litigate)
- **LLM:** Claude `claude-opus-4-8`, structured outputs (`output_config.format`),
  adaptive thinking for the chat answer. `anthropic` pinned loose so the container
  gets an SDK new enough for these.
- **Graph store:** Neo4j + APOC (dynamic labels/rel types). Deterministic loader —
  we never execute LLM-generated *write* Cypher; only guarded read-only Cypher at
  query time.
- **Retrieval:** Neo4j full-text (Lucene), **no embedding provider** — Claude is the
  only external service.
- **Deploy:** Docker Compose, one command.
- **Name:** Graphize (alternates considered: Constellate, GraphForge, AutoKG).

## ✅ Verified vs ⏳ pending
- ✅ Backend compiles; ingest/construct/merge logic tested offline (8 products + 6
  suppliers → 14 nodes, 8 edges). Frontend prod-build passes. Compose validates.
  Stack ran locally; `/api/paste` + `/api/sample` + `/api/health` verified.
- ⏳ Full LLM pipeline (Build/Chat) **never run live** — needs a real API key.
- ⏳ Demo GIF not recorded (`marketing/DEMO_SCRIPT.md` has the script).
- ⏳ Roadmap features not built: **field-type inference**, **hypothetical-question
  validation**, pluggable GraphRAG retrievers, embeddings option, graph export.

## 🚀 Launch checklist (see marketing/LAUNCH_PLAN.md for full plan)
- [ ] Put your name in `LICENSE` + a bio line in README footer.
- [ ] Swap remaining `OWNER`/`<REPO>` placeholders → `Dabaiee/graphize` (README
      badges/clone URL, `marketing/landing.html` GitHub links, `marketing/CONTENT.md`).
- [ ] Record demo → add `docs/demo.gif` to README.
- [ ] Add repo topics: knowledge-graph, graphrag, ai-agents, llm, neo4j, claude,
      rag, fastapi, react. Set About + website to the landing page.
- [ ] Share the landing artifact from its Share menu; post per LAUNCH_PLAN Day 1→3.

## 🔐 Secrets
`.env` is git-ignored and **not** in the repo. Set `ANTHROPIC_API_KEY` locally on
each device. Never commit a real key.

# Graphize — Market & Positioning

## The one-line position
**The open, 1-click knowledge-graph app — the "Ollama of knowledge graphs."**
Paste data → graph + chat, self-hostable, run it *fully free* with a local model
or bring your own Claude/GPT key. No lock-in.

## Where Graphize sits
The GraphRAG / doc-to-knowledge-graph space splits into **libraries** and
**closed services**. Nobody owns the consumer-grade, 1-click, self-hostable *app*.

| Product | What it is | Model | Gap Graphize fills |
|---|---|---|---|
| **Microsoft GraphRAG** | OSS Python library, community-summary pipeline | Free OSS | CLI/library for engineers; heavy to index; no UI, no deploy |
| **Neo4j LLM KG Builder** | Neo4j's own docs→graph tool | Free, funnels to Aura | Enterprise/dev; tied to Neo4j; not 1-button for non-technical users |
| **Cognee** | OSS "AI memory engine" SDK | Open-core + cloud (VC) | A library you code against, not a click-and-chat product |
| **Graphlit** | RAG-as-a-Service | Pure SaaS/API | Closed, API-first, no self-host, no OSS |
| **LlamaIndex PropertyGraph** | Graph index in a framework | Free OSS framework | A component for builders, not an end product |

**Sources:** neo4j.com/labs/genai-ecosystem/llm-graph-builder · Microsoft GraphRAG
(github.com/microsoft/graphrag) · cognee.ai · graphlit.com · docs.llamaindex.ai

## Honest weaknesses (don't oversell)
- Extraction quality/scale won't beat Microsoft/Neo4j head-on.
- Single-graph app today — no persistence/multi-tenant/auth.
- Local-model quality is lower than Claude/GPT (mitigated by JSON validation + retry).

So: pitch it as the **easiest way to go from data to a graph you can chat with**,
self-hostable and free — not as an enterprise contender.

## Differentiators (use these in posts / README / FAQ)
1. **1 button, non-technical.** Paste text → graph + chat. No schema, no Cypher.
2. **Structured + unstructured in one graph.** CSV builds deterministically; text
   is extracted in parallel; both halves fuse.
3. **Run it free & local** (Ollama) or bring your own key (Claude / GPT) — no lock-in.
4. **Ships what the reference course repo lists as TODO:** unstructured import,
   entity resolution, evaluation.
5. **One-command deploy** + an **MCP server** (use it inside Claude Code / Cursor).

## Business model — matched to goals (portfolio + stars; consulting optional)

**Tier 0 — now (recommended): OSS as career capital.** 100% free / Apache-2.0.
The product you monetize is *you* — the repo converts to job offers, inbound, and
audience. Do **not** add billing before ~500 stars / real inbound.

**Tier 1 — if it gains traction: open-core + "Graphize Cloud."** Free self-host
core stays; the paid layer sells what self-hosting is annoying at:
- Free (cloud): small graphs, ephemeral, bring-your-own key
- Pro ~$19–29/mo: persistent graphs, larger inputs, export, private sharing
- Team ~$99+/mo: members, workspaces, higher limits
Proven pattern here (Cognee, Ollama, Neo4j).

**Tier 2 — adjacent, cheaper:** vertical templates (KG for papers / tickets /
codebases), or a hosted bring-your-own-key endpoint.

## Recommendation
Launch as pure OSS to win the "1-click open KG app" slot and stack stars/credibility.
Build Cloud only if the launch pulls real demand.

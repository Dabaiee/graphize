# Copy-paste test case

A single text sample that produces a rich, connected graph (people, places,
awards, discoveries, institutions, dates), plus three ways to run it. Prereqs:
Neo4j up (`docker compose up -d neo4j`) and a real `ANTHROPIC_API_KEY`.

## The sample text

```
Marie Curie was a physicist and chemist born in Warsaw, Poland, who spent most of
her career in Paris, France. Together with her husband Pierre Curie she discovered
the elements polonium and radium. In 1903 she won the Nobel Prize in Physics,
shared with Pierre Curie and Henri Becquerel, whose discovery of radioactivity her
work built on. In 1911 she won a second Nobel Prize, in Chemistry, becoming the
first person to win Nobel Prizes in two different sciences. She founded the Radium
Institute in Paris. Her daughter Irène Joliot-Curie, working with her husband
Frédéric Joliot-Curie, later won the Nobel Prize in Chemistry in 1935 for the
discovery of artificial radioactivity.
```

---

## A) In an MCP client (Claude Code / Cursor / Claude Desktop)

Paste this whole message into the chat (the `graphize` MCP server must be
registered — see `docs/MCP.md`):

```
Use the graphize MCP tool `build_graph_from_text` to build a knowledge graph from
the text below, with about="The Curie family and their Nobel Prizes" and
questions="Who won which Nobel Prizes and who did they work with?". Then call
`ask_graph` with "Which Nobel Prizes did Marie Curie win, and who did she share
them with?" and show me the answer plus the graph stats.

TEXT:
Marie Curie was a physicist and chemist born in Warsaw, Poland, who spent most of
her career in Paris, France. Together with her husband Pierre Curie she discovered
the elements polonium and radium. In 1903 she won the Nobel Prize in Physics,
shared with Pierre Curie and Henri Becquerel, whose discovery of radioactivity her
work built on. In 1911 she won a second Nobel Prize, in Chemistry, becoming the
first person to win Nobel Prizes in two different sciences. She founded the Radium
Institute in Paris. Her daughter Irène Joliot-Curie, working with her husband
Frédéric Joliot-Curie, later won the Nobel Prize in Chemistry in 1935 for the
discovery of artificial radioactivity.
```

---

## B) In the web UI (http://localhost:5280)

1. Paste the sample text into **"Or paste text directly."**
2. (Optional) about = `The Curie family and their Nobel Prizes`; questions =
   `Who won which Nobel Prizes and who did they work with?`
3. Click **⚡ Build my graph**, then ask in chat:
   `Which Nobel Prizes did Marie Curie win, and who did she share them with?`

---

## C) Terminal smoke test (no client, streams progress)

From the repo root, with the backend venv created (`docs/MCP.md` step 1):

```bash
cd backend
ANTHROPIC_API_KEY=sk-ant-... NEO4J_URI=bolt://localhost:7690 NEO4J_PASSWORD=fastgraph \
.venv/bin/python - <<'PY'
from app.ingest import Source, _chunk_text
from app import orchestrator
from app.agents import graphrag

text = """Marie Curie was a physicist and chemist born in Warsaw, Poland, who spent
most of her career in Paris, France. Together with her husband Pierre Curie she
discovered the elements polonium and radium. In 1903 she won the Nobel Prize in
Physics, shared with Pierre Curie and Henri Becquerel, whose discovery of
radioactivity her work built on. In 1911 she won a second Nobel Prize, in
Chemistry. She founded the Radium Institute in Paris. Her daughter Irène
Joliot-Curie, with her husband Frédéric Joliot-Curie, won the Nobel Prize in
Chemistry in 1935 for the discovery of artificial radioactivity."""

r = orchestrator.run_build(
    [Source(name="curie.txt", kind="unstructured", chunks=_chunk_text(text))],
    {"about": "Curie family Nobel Prizes", "questions": "who won what and with whom",
     "track": "people, prizes, discoveries"},
    lambda e: print("·", e["stage"], "—", e["message"]),
)
print("\nSTATS:", r["stats"])
print("\nANSWER:", graphrag.answer(
    "Which Nobel Prizes did Marie Curie win, and who did she share them with?"
)["answer"])
PY
```

---

## What a good result looks like

- **Stats:** roughly 12–20 nodes, 10+ relationships; node types include something
  like `Person`, `Place`, `Award`/`Prize`, `Element`/`Discovery`, `Institution`.
- **Entities:** Marie Curie, Pierre Curie, Henri Becquerel, Irène Joliot-Curie,
  Frédéric Joliot-Curie, polonium, radium, Nobel Prize (Physics/Chemistry), Paris,
  Warsaw, Radium Institute.
- **Answer** should say: **1903 Nobel Prize in Physics**, shared with **Pierre
  Curie** and **Henri Becquerel**; and **1911 Nobel Prize in Chemistry** (hers
  alone).

If the answer is vague or the graph is tiny, the model/provider is the likely
cause — try a stronger model or check the API key.
```

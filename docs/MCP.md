# Use Graphize from Claude Code / Cursor / Claude Desktop (MCP)

Graphize ships an **MCP server** so you can build and query knowledge graphs
straight from your AI chat — using your own Claude, with **no hosting and no cost
to anyone but your own API key**.

Tools exposed:
- `build_graph_from_text(text, about?, questions?, track?)`
- `build_graph_from_files(paths[], about?, questions?, track?)`
- `ask_graph(question)`
- `graph_stats()`

## 1. One-time setup

```bash
# clone
git clone https://github.com/Dabaiee/graphize && cd graphize

# start Neo4j (the graph store the MCP server writes to)
cp .env.example .env               # set NEO4J_PASSWORD if you want; ANTHROPIC_API_KEY goes in the client config below
docker compose up -d neo4j

# python env for the MCP server
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cd ..
```

Note the two paths you'll need below:
- Python: `<REPO>/backend/.venv/bin/python`
- Server: `<REPO>/backend/mcp_server.py`

> Neo4j's bolt port is mapped to **7690** on the host (shifted off the default so
> Graphize coexists with other projects), so the MCP server connects with
> `NEO4J_URI=bolt://localhost:7690`.

## 2. Register it with your client

### Claude Code (CLI)
```bash
claude mcp add graphize \
  --env ANTHROPIC_API_KEY=sk-ant-... \
  --env NEO4J_URI=bolt://localhost:7690 \
  --env NEO4J_PASSWORD=fastgraph \
  -- /ABS/PATH/graphize/backend/.venv/bin/python /ABS/PATH/graphize/backend/mcp_server.py
```

### Claude Desktop
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) / `%APPDATA%\Claude\claude_desktop_config.json` (Windows):
```json
{
  "mcpServers": {
    "graphize": {
      "command": "/ABS/PATH/graphize/backend/.venv/bin/python",
      "args": ["/ABS/PATH/graphize/backend/mcp_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "NEO4J_URI": "bolt://localhost:7690",
        "NEO4J_PASSWORD": "fastgraph"
      }
    }
  }
}
```

### Cursor
Create `.cursor/mcp.json` in your workspace (same shape as the Claude Desktop
`mcpServers` block above).

Restart the client so it picks up the server.

## 3. Use it (in chat)

> "Use graphize to build a graph from this text: *<paste anything>*, then tell me
> what it can answer."

> "Ask the graph: which products are supplied by Fellow?"

> "Build a graph from `/Users/me/data/papers/` and give me its stats."

The client calls the tools; Graphize runs the pipeline against your Neo4j and
returns results inline. The web UI (`docker compose up`, http://localhost:5280)
and the MCP server share the same graph, so you can build in one and inspect in
the other.

## Troubleshooting
- **"Neo4j is not reachable"** → `docker compose up -d neo4j`; confirm
  `NEO4J_URI=bolt://localhost:7690` in the client config.
- **Auth errors** → check `ANTHROPIC_API_KEY` in the client config env.
- **Tool not appearing** → fully restart the client; verify the absolute paths.

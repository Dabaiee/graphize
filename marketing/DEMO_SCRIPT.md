# Graphize — Demo Script & Storyboard

Two assets from one recording:
- **20-second silent GIF** → README hero + X tweet 1 + PH gallery (autoplay, no audio).
- **60–90-second narrated video** → LinkedIn, Medium embed, YouTube.

Record the full narrated take, then clip the tightest 20s (paste → graph → one
chat answer) for the GIF.

## Setup before recording
- Real `ANTHROPIC_API_KEY` in `.env`; `docker compose up -d` running.
- Browser at `http://localhost:5280`, window ~1280×800, clean (no bookmarks bar).
- Have the paste text ready on your clipboard (below).
- Record at 30fps. For the GIF: ≤ 1000px wide, ≤ 8MB so it autoplays on GitHub/X.
- Tool: macOS `screen.studio` or `Kap` (free) for smooth cursor + zoom.

## Paste-text sample (short, high-yield graph)
```
Marie Curie was a physicist and chemist who worked in Paris. She discovered
polonium and radium, and won the Nobel Prize in Physics in 1903 with her husband
Pierre Curie, and the Nobel Prize in Chemistry in 1911. Her work built on
Henri Becquerel's discovery of radioactivity. Her daughter Irène Joliot-Curie
also won a Nobel Prize in Chemistry.
```
(Yields People, Prizes, Places, Discoveries + rich relationships — reads great as a graph.)

## Storyboard (narrated, ~75s)

| Time | On screen | Voiceover / caption |
|---|---|---|
| 0:00–0:06 | Landing page, cursor on the ⚡ Graphize title | "This is Graphize. It turns any data into a knowledge graph you can talk to." |
| 0:06–0:14 | Paste the Marie Curie text into the textarea | "I'll just paste some plain text — no files, no setup." |
| 0:14–0:18 | Cursor hits **⚡ Build my graph** | "One click." |
| 0:18–0:38 | Progress panel streaming: intent → schema → construct → resolve → critic | "Seven Claude agents run behind the scenes — they figure out the schema, extract the entities, merge duplicates, and check their own work." |
| 0:38–0:50 | Graph visualization animates into place; legend of types | "And here's the graph — people, prizes, places, discoveries, all connected." |
| 0:50–1:05 | Type in chat: *"What did Marie Curie win and who did she work with?"* → answer with citations | "Now I can just ask it questions, and it answers from the graph." |
| 1:05–1:15 | Cut to README / GitHub repo page | "It's open source, runs with one command, and it's the automated version of DeepLearning.AI's agentic knowledge-graph course. Link below." |

## GIF clip (20s, silent, captioned)
Trim to: paste (2s) → click (1s) → progress fast-forward 2× (7s) → graph appears
(5s) → one chat Q&A (5s). Burn in 2 captions: **"Paste any text"** and
**"Chat with the graph."** Loop it.

## Screenshots to grab (for PH gallery / Medium / X)
1. Live build progress (the streaming agent list).
2. The finished graph visualization with the type legend.
3. A chat answer showing citations.
4. The comparison table from the README (course vs Graphize).

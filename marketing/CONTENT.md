# Graphize — Launch Content Pack

Ready-to-post copy for each channel. Replace `<HANDLE>` and `<DEMO_LINK>`
before posting. The one narrative through-line everywhere:

> **"Google/DeepLearning.AI shipped a 3-hour course to hand-build agentic
> knowledge graphs. I open-sourced the 1-click version — and shipped the two
> features their own repo lists as TODO."**

Post order (see `LAUNCH_PLAN.md`): X → LinkedIn → Medium (same day) → Show HN +
Reddit (day 2, morning PT) → Product Hunt (optional, day 3).

---

## 1) X / Twitter thread

**Tweet 1 (the hook — attach the 20s demo GIF):**
> DeepLearning.AI + Neo4j + Google just dropped a 3-hour course on building
> agentic knowledge graphs by hand.
>
> I built the 1-click open-source version.
>
> Paste text → get a knowledge graph you can chat with. 7 Claude agents do the
> rest. 🧵

**Tweet 2:**
> The course teaches a multi-agent pipeline you drive through a conversation:
> intent → file suggestion → schema → construction → GraphRAG.
>
> Graphize runs the same pipeline — but the user just fills a tiny form and
> clicks once. No dialogue, no Cypher, no schema design.

**Tweet 3 (the one-up — screenshot the comparison table):**
> Their reference repo lists 3 things as "not yet implemented":
> • unstructured-text import
> • entity resolution
> • evaluation
>
> Graphize ships all three. Structured CSVs + messy text merge into ONE graph.

**Tweet 4 (the tech flex):**
> Stack:
> • Claude (claude-opus-4-8) w/ structured outputs — every agent returns typed JSON
> • FastAPI + WebSockets for live agent progress
> • Neo4j + APOC, deterministic loader (no LLM-generated write Cypher)
> • React one-button UI
> • `docker compose up` → whole thing runs

**Tweet 5 (design taste):**
> The hard part isn't the graph — it's hiding it.
>
> Structured data builds deterministically. Unstructured text fans out to
> parallel per-chunk extraction. Entity resolution merges "IBM"/"I.B.M." You
> see none of it — just a graph and a chat box.

**Tweet 6 (CTA):**
> 100% open source (Apache-2.0). One command to run locally.
>
> ⭐ Repo: https://github.com/Dabaiee/graphize
> 🎬 Demo: <DEMO_LINK>
>
> Built with Claude. If you're into agents + graphs, I'd love a star and your
> feedback. What should it build a graph of next?

---

## 2) LinkedIn post

> **I turned a 3-hour course into a one-click tool.**
>
> DeepLearning.AI, Neo4j, and Google recently launched a course on building
> *agentic knowledge graphs* — a team of AI agents that reads your data and
> constructs a queryable graph. It's a great course. It's also a lot of manual,
> conversational work, and the reference repo openly lists several features as
> "not yet implemented."
>
> So I built **Graphize** — the automated, open-source version.
>
> → Paste text or drop files
> → Answer 3 plain-English questions (optional)
> → Click once
> → Get a Neo4j knowledge graph you can chat with
>
> Under the button, 7 Claude agents run a pipeline: understand intent, pick
> files, design the schema, extract entities from structured *and* unstructured
> data, resolve duplicates, evaluate the result, and answer questions over it.
>
> The three features the course's repo marks as TODO — unstructured import,
> entity resolution, evaluation — are all shipped.
>
> Tech: Claude (structured outputs) · FastAPI + WebSockets · Neo4j + APOC ·
> React · one-command Docker deploy.
>
> It's Apache-2.0 licensed and runs with a single command. Link in the comments. 👇
>
> I'd genuinely value feedback from anyone working on RAG, graphs, or agent
> orchestration — what would you point it at?
>
> #AI #KnowledgeGraphs #LLM #Agents #GraphRAG #Neo4j #OpenSource

_(First comment: the repo link + demo link. LinkedIn suppresses posts with
outbound links in the body — put links in the first comment.)_

---

## 3) Medium / blog article

**Title options (A/B these):**
1. "I Turned Andrew Ng's New Knowledge-Graph Course Into a One-Click Tool"
2. "Agentic Knowledge Graphs, Automated: Building the 1-Click Version of a 3-Hour Course"
3. "From 3 Hours to 1 Click: Open-Sourcing an Agentic Knowledge-Graph Builder"

**Subtitle:** How I wrapped a multi-agent GraphRAG pipeline behind a single
button — and shipped the features the reference implementation left as TODO.

**Outline (target ~1,400 words, 6–8 min read):**

1. **Hook (150w).** The course exists; it's great; it's manual. The gap: what if
   a non-technical user could get the same result with one click? Show the demo
   GIF immediately.
2. **What a knowledge graph buys you (150w).** Why graph + RAG beats plain RAG
   for connected questions. Keep it concrete with the coffee-gear sample.
3. **The pipeline (350w).** Walk the 7 agents. Emphasize the design decision:
   structured data builds *deterministically* (no LLM per row — cheaper, exact),
   unstructured text uses *parallel per-chunk extraction*. Include the mermaid
   diagram.
4. **The three TODOs I shipped (300w).** Unstructured import, entity resolution,
   evaluation. Show the entity-resolution example ("IBM"/"I.B.M.").
5. **Hiding the graph is the product (200w).** The UX thesis: the value is
   removing the need to understand graphs. Structured outputs make every agent
   return typed JSON, which is what makes the automation reliable.
6. **Run it yourself (150w).** `docker compose up`. Link the repo.
7. **What's next / call for contributors (100w).** Roadmap + "star it, break it,
   PR it."

**SEO tags:** knowledge graph, GraphRAG, AI agents, Neo4j, LLM, Claude, RAG,
multi-agent systems, open source.

**Cross-post:** dev.to and Hashnode with a canonical link back to Medium (or
vice versa). Submit to any "AI/LLM weekly" newsletters that accept links.

---

## 4) Hacker News (Show HN)

**Title:**
> Show HN: Graphize – Paste text, get a knowledge graph you can chat with (Apache-2.0)

**First comment (post immediately after submitting):**
> Author here. I built this after DeepLearning.AI/Neo4j/Google released a course
> on hand-building agentic knowledge graphs. The course drives a multi-agent
> pipeline through a conversation; I wanted the one-click version a non-technical
> user could actually use.
>
> How it works: 7 Claude agents run intent → file-suggestion → schema-proposal →
> construction → entity-resolution → critic → GraphRAG. Structured data (CSV)
> builds deterministically from a mapping the schema agent proposes — no
> LLM-generated write Cypher touches the DB. Unstructured text fans out to
> parallel per-chunk extraction, and the two halves merge into one graph via
> deterministic entity IDs. Retrieval is Neo4j full-text + guarded read-only
> Cypher, so there's no embedding provider — Claude is the only external service.
>
> Notably, the course's reference repo lists unstructured import, entity
> resolution, and evaluation as not-yet-implemented; those are the parts I found
> most interesting to build, so they're in.
>
> Stack: Claude (structured outputs) / FastAPI + WebSockets / Neo4j + APOC /
> React / docker-compose. Apache-2.0. Feedback and adversarial test cases very welcome —
> especially where the schema inference or entity resolution falls over.

_HN tips: submit 8–10am PT on a weekday. No emojis in title. Respond to every
comment fast and technically. Don't ask for upvotes anywhere._

---

## 5) Reddit

**r/LocalLLaMA, r/MachineLearning (Saturday self-promo threads), r/Neo4j, r/dataengineering**

**Title:**
> I open-sourced a 1-click agentic knowledge-graph builder (Claude + Neo4j) —
> paste text, get a graph you can chat with

**Body:**
> Built this to automate the multi-agent pipeline from the recent DeepLearning.AI
> × Neo4j course. Paste text or drop CSVs → 7 Claude agents build a Neo4j graph
> and a GraphRAG chat over it. Structured data builds deterministically;
> unstructured text is extracted per-chunk in parallel; duplicate entities get
> merged.
>
> It's Apache-2.0 licensed, runs with `docker compose up`, and Claude is the only
> external dependency (retrieval is Neo4j full-text, no embedding service).
>
> Repo: https://github.com/Dabaiee/graphize — would love feedback on the schema-inference and
> entity-resolution steps, that's where it's most likely to break.

_Read each sub's self-promotion rules first. Lead with substance, not the link.
r/MachineLearning generally wants the [P] (project) tag and a real writeup._

---

## 6) Product Hunt (optional, day 3)

**Name:** Graphize
**Tagline:** Paste your data, get a knowledge graph you can talk to
**Description:**
> Graphize turns files or raw text into a queryable Neo4j knowledge graph
> automatically, using a team of Claude agents. No schema, no Cypher, no graph
> expertise. Open source, one-command deploy, chat with your data.
**First comment:** the origin story (course → 1-click) + the tech + ask for
feedback.
**Gallery:** demo GIF first, then the architecture diagram, then 2–3 annotated
screenshots (build progress, graph viz, chat).

---

## Reusable one-liners (bio / pinned / elsewhere)

- "Paste your data. Click once. Get a knowledge graph you can talk to."
- "The 1-click version of DeepLearning.AI's agentic knowledge-graph course."
- "7 Claude agents turn your text into a Neo4j graph you can chat with."
- "Knowledge graphs without the Cypher."

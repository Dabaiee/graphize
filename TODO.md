# ✅ Graphize — Launch TODO

**Strategy (Tier 0):** ship as 100% free OSS, win the *"1-click open knowledge-graph
app"* position (the "Ollama of knowledge graphs" — nobody owns that slot), and rack
up stars + credibility. Build a paid Cloud (open-core) **only if** the launch pulls
real demand. Don't add billing before ~500 stars / real inbound.

**Definition of done for the launch:** demo GIF live + posted on X/LinkedIn/Medium +
Show HN, with first 50 stars. (The first 50 is the hard part.)

`[YOU]` = only you · `[CLAUDE]` = ask me and I'll do it

---

## P0 — Before you post anything (this week)

- [ ] `[YOU]` Put a real `ANTHROPIC_API_KEY` in `.env`; run one live build end-to-end
      (sample dataset → graph → ask 2 questions). Confirm it actually works.
- [ ] `[CLAUDE]` Weave the sharper positioning ("the Ollama of knowledge graphs /
      1-click, self-hostable, no lock-in") into the README hero + landing page.
- [ ] `[CLAUDE]` Add `marketing/MARKET.md` — competitive table + business-model plan
      + differentiator one-liners (for your own pitch + FAQ).
- [ ] `[CLAUDE]` Add `CONTRIBUTING.md` + open 3–5 `good first issue`s (invites PRs,
      makes the repo look alive).
- [ ] `[YOU]` Record the demo (script in `marketing/DEMO_SCRIPT.md`) → add
      `docs/demo.gif` and reference it in the README. **Single biggest lever — do not
      launch without it.**
- [ ] `[YOU]` Grab 3 screenshots (build progress, graph, chat) → `docs/`; embed in README.
- [ ] `[YOU]` Real name in `LICENSE` (currently "Dabaiee"); one bio line in README footer.
- [ ] `[YOU]` Set GitHub repo **About** + website to the landing-page URL (after you
      Share it from the artifact's Share menu).
- [ ] `[YOU]` Test `git clone && ./deploy.sh` on a clean machine / fresh Docker so
      first-run works for strangers.

## P1 — Launch week (distribution — see `marketing/LAUNCH_PLAN.md`)

- [ ] `[YOU]` Fill `<HANDLE>` (your X handle) + `<DEMO_LINK>` in `marketing/CONTENT.md`.
- [ ] `[YOU]` **Day 1 (Tue–Thu ~9am):** post X thread (GIF on tweet 1, pin it) →
      LinkedIn (links in first comment) → publish Medium + cross-post dev.to/Hashnode.
- [ ] `[YOU]` **Day 2 (8–10am PT):** Show HN (title + first comment from CONTENT.md);
      then Reddit r/LocalLLaMA, r/Neo4j, r/dataengineering (respect each sub's rules).
- [ ] `[YOU]` **Day 3+ (optional):** Product Hunt; submit to TLDR AI / Ben's Bites;
      PR Graphize into "Awesome Knowledge Graph" / "Awesome LLM" lists.
- [ ] `[YOU]` Reply to **every** comment in the first 48h. Fix reported bugs fast and
      thank people in-thread — responsiveness converts skeptics to stargazers.

## P2 — Harden the differentiator (post-launch, only if it gets traction)

- [ ] `[CLAUDE]` **Field-type inference** — type CSV values (numbers/dates) so numeric
      queries ("products under $50") work. Strengthens the "vs course" story.
- [ ] `[CLAUDE]` **Hypothetical-question validation** — critic runs its proposed
      questions through GraphRAG and flags any the graph can't answer.
- [ ] `[CLAUDE]` A small `pytest` suite (ingest, structured build, entity merge) + a
      GitHub Actions CI badge (looks credible on the repo).
- [ ] `[CLAUDE]` Pluggable GraphRAG retrievers + optional vector embeddings.
- [ ] `[CLAUDE]` Graph export (GraphML / Cypher dump).

## P3 — Only if demand is real (open-core Cloud)

- [ ] Decide go/no-go on **Graphize Cloud** (no Docker/Neo4j, saved graphs, sharing).
- [ ] Persistence + auth + multi-tenant (the app is single-graph today).
- [ ] Pricing: Free (small, BYO-key) · Pro ~$19–29/mo · Team ~$99+/mo.

---

## Metrics to watch (lightweight)
- Stars in first 72h (target: first 50).
- GitHub → Traffic: which platform drove clones. Double down on the winner.
- Inbound DMs / job or consulting leads (your actual Tier-0 payoff).

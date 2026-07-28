# Graphize — Launch Plan

**Goal:** portfolio credibility (AI-eng roles) + GitHub stars. Secondary:
consulting/inbound. **Spotlight:** AI agents · Graph/RAG · product taste.

## Positioning (one line)
The 1-click, open-source version of DeepLearning.AI's agentic knowledge-graph
course — with the features their repo lists as TODO already shipped.

## Pre-launch checklist (do all before posting anything)
- [ ] Put your real name in `LICENSE` and a short bio + links in the README footer.
- [ ] Create the GitHub repo `graphize` (public). Add topics: `knowledge-graph`,
      `graphrag`, `ai-agents`, `llm`, `neo4j`, `claude`, `rag`, `fastapi`, `react`.
- [ ] Set the repo's **About** blurb + website to the demo link.
- [ ] Record the demo → add `docs/demo.gif` to the README (single biggest
      conversion lever — do not launch without it).
- [ ] Add 3 screenshots to `docs/` and reference them in the README.
- [ ] Swap `<OWNER>/<REPO>` placeholders in README badges + clone URL.
- [ ] Test `git clone … && ./deploy.sh` on a clean machine (or fresh Docker) so
      first-run works for strangers. Confirm the sample build succeeds with a key.
- [ ] Pin a tweet / featured LinkedIn once posted.

## Timeline

**Day 0 — Ship the repo**
Push code, README, LICENSE, demo GIF. Quiet — no announcement yet. Let it be
real for a day; fix anything broken.

**Day 1 — Owned channels (Tue–Thu, ~9am your time)**
- X thread (demo GIF on tweet 1). Pin it.
- LinkedIn post (links in first comment). Feature it on your profile.
- Publish the Medium article; cross-post to dev.to/Hashnode with canonical link.
- DM/share to 5–10 people who'd genuinely find it interesting (no mass spam).

**Day 2 — Communities (Tue/Wed, 8–10am PT for HN)**
- Show HN (title + first comment from CONTENT.md). Camp the thread, reply fast.
- Reddit: r/LocalLLaMA, r/Neo4j, r/dataengineering (respect each sub's rules;
  many require weekend self-promo threads — check first).
- If HN gains traction, quote-tweet it.

**Day 3+ — Optional amplifiers**
- Product Hunt (schedule 12:01am PT; line up a few people to check it out).
- Submit to newsletters/aggregators: TLDR AI, Ben's Bites, "Awesome
  Knowledge Graph" / "Awesome LLM" lists (open a PR to add Graphize).
- Neo4j community forum + Anthropic Discord "built-with-Claude" channels.

## Engagement rules (these matter more than the copy)
- Reply to **every** comment in the first 48h, technically and generously.
- When someone hits a bug, fix it fast and thank them in-thread. Public
  responsiveness converts skeptics to stargazers.
- Never buy/ask for upvotes; never mass-DM. One authentic thread > ten spammy ones.
- Convert interest into a next artifact: if a question comes up twice, that's
  your next tweet/section.

## Metrics to watch (lightweight)
- Stars in first 72h (aim: first 50 is the hard part).
- README → repo referral sources (GitHub Insights → Traffic).
- Which platform drove clones. Double down on the winner next time.

## After the launch (compounding)
- Ship a roadmap item, post a "shipped X" follow-up (keeps the repo alive-looking).
- Write a focused deep-dive: "Why we don't let the LLM write Cypher" or
  "Deterministic vs. LLM graph construction." Evergreen, links back.
- Add a `CONTRIBUTING.md` + a few `good first issue`s to invite PRs.

# Ideation Pipeline — design v0

**Date:** 2026-05-17
**Author:** Aletheia, after James's 2026-05-17 architecture conversation.
**Status:** v0 design, not yet load-bearing. Tested with one entry (`pivot/idea_learner_solution_steps_corpus_2026-05-17.md`).

---

## What this is

The meta-pipeline that runs **above** all the agent pipelines. Source of every architecture, every agent, every pivot, every pipeline currently in Prometheus. Until now it lived entirely in James's head + Aporia's dispatch queue + the daily Gemini Deep Research yield + NotebookLM audio listening.

This doc names it, gives it a workflow, and proposes a low-friction capture mechanism.

## The workflow

```
Source → Capture → Evolve → Promote (or Archive)
   ↑                  │
   └──────────────────┘
   (research feedback loops back to source)
```

**Source** — anywhere an idea can come from:
- James-in-conversation with any agent / Titan
- Aporia's Gemini Deep Research dispatch (20/day quota)
- Intelligence pipeline outputs (when tuned for surfacing-things-worth-thinking-about)
- NotebookLM audio listening → morning epiphany
- Frontier model interactions (ChatGPT, Gemini, DeepSeek, Grok)
- Reading existing pivot docs and noticing gaps
- Replaying old artifacts under new criteria

**Capture** — a low-friction doc at `pivot/idea_<short_title>_<date>.md`. Required fields:
- Title
- Status: `raw`
- Captured at: date
- Captured by: (agent or human)
- Source: how the idea arrived
- The idea — verbatim where possible, in the speaker's words
- Reframed in structured form (the capturer's interpretation)

Optional but encouraged at capture time:
- Connection to existing thinking (related work, prior art)
- Open questions worth deep-research
- Possible relationship to other Prometheus pieces

**Evolve** — the idea matures through:
- Aporia dispatches deep research on the open questions → results get appended to the doc, status goes `raw → researched`
- Frontier model passes (ChatGPT / Gemini / Grok / etc.) → critique gets appended, status remains `researched` or moves to `drafted`
- James commentary and re-evaluation → status moves toward `drafted`
- A short experiment falsifies or supports the idea cheaply → status moves toward `promoted` or `archived`

Each evolution gets a row in the doc's "Status timeline" table, plus an appended section with the new content. The doc is append-only after capture.

**Promote** — when an idea is `drafted` and survives Frontier-model pressure-testing:
- Lightweight: dispatch a deep-research batch, run a small experiment
- Substantial: spawn a new agent or pipeline, add a manifest at `pipelines/<name>.yaml`
- Full: re-orient existing agents around the new direction (with a pivot doc explaining the redirect)

**Archive** — when an idea is `drafted` but doesn't survive critique, or when a cheap experiment falsifies it:
- Status moves to `archived`
- Doc stays on disk forever (negative-space data is itself valuable)
- The archive is searchable for related ideas that may revive

## Why low-friction matters

James said "I don't need a formal entry form." The intent: capture should be near-zero ceremony so ideas don't get lost. A half-formed thought dumped from his phone should become a tracked artifact without any other action required.

Concrete capture paths:

1. **In-conversation capture** — when James says "I have an idea for X" mid-conversation, the listening agent (Aletheia or otherwise) writes the doc immediately. Verbatim quote at the top. The agent's structured reframe follows. James doesn't have to do anything else.

2. **Voice memo capture** — record idea on phone, transcribe via whatever, paste into a new doc at `pivot/idea_<short_title>_<date>.md`. The agent then evolves it via the workflow above.

3. **Email-to-self capture** — send a quick email to a known address; an agent watching that inbox creates the doc.

4. **Direct edit** — James opens his editor on M1 and creates the doc himself. The fastest path when the idea is structured enough to write directly.

5. **Frontier-model dialog capture** — when a Titan conversation produces an interesting idea (like ChatGPT's "close one tiny loop" advice from 2026-05-17), the agent extracts the idea and creates the doc.

## Tracking + surfacing

The reporting pipeline picks up ideas-in-flight automatically:

- `scripts/portfolio_monitor.py` scans `pivot/idea_*.md` and adds a summary to `docs/state.json` under a new top-level field `ideas_in_flight`. Each entry: title, status, last_updated, doc_path.
- `scripts/metis_portfolio.py` includes ideas-in-flight in the brief: surfaces which need next-research, which are mature enough to promote, which haven't moved in N days.
- `scripts/send_brief_email.py` adds an "Ideas in flight" section to the email's References (or above it as a higher-priority section, TBD).
- React dashboard adds an "Ideas" panel listing the in-flight ones with their status.

This means once an idea is captured, the orchestration layer carries it through to your attention naturally — you don't have to remember it.

## The Aporia + Intelligence Pipeline relationship

Two of these are *idea generators*, intended to run 24/7:

- **Aporia** — currently runs Gemini Deep Research dispatch (20/day quota). Her output is high-quality research notes that often surface novel angles. Each Aporia-surfaced idea should produce an `pivot/idea_*.md` capture by default. Currently this happens manually; could be automated.

- **Intelligence pipeline** — currently runs Eos→Aletheia→Skopos→Metis-paper→Clymene. The synthesis is paper-research-oriented (what landed in arXiv today). To be an idea generator, it needs tuning toward "what does this paper imply for Prometheus that wasn't true before?" — a different LLM prompt for Metis-paper that focuses on idea-yield rather than entity-extraction.

If both run ambient and feed the capture stream, you have ~25-30 idea candidates surfacing per day across both. Most go straight to `archived` (not load-bearing). A few graduate to `researched`. Fewer to `drafted`. Maybe one per week promotes.

## NotebookLM audio synthesis — the back-end

Separate from the capture pipeline but parallel: the synthesis-for-listening loop.

At end of each day:
1. An agent reads recent activity (commits, briefs, ideas captured, agent outputs)
2. Writes a daily progress summary tuned for ELI5 + narrative arc + celebration of small wins
3. Output is a markdown file James pastes into NotebookLM
4. NotebookLM produces audio
5. James listens before bed
6. Morning: epiphanies feed back into the capture pipeline

The new piece needed here is a different Metis mode — call it `metis_audio_brief.py` or `metis_celebrate.py`. Different system prompt, different output file. Same data sources as the operational brief, different voice.

This explicitly serves James's learning loop, which is itself the project's most important loop.

## v0 implementation plan (proposed, not yet shipped)

Smallest set of moves that make the ideation pipeline a real artifact:

1. **`pivot/ideas/`** — new directory, or `pivot/idea_*.md` glob, becomes the canonical idea location. Either works; glob is simpler. (Used in this doc.)

2. **Idea status convention** — `raw / researched / drafted / promoted / archived`. Required in every idea doc.

3. **`scripts/list_ideas.py`** — small CLI that scans `pivot/idea_*.md`, parses status from the YAML frontmatter or first table row, prints a status report.

4. **`scripts/portfolio_monitor.py`** — adds `ideas_in_flight` to `state.json` based on the scan above. ~20 lines.

5. **`scripts/metis_portfolio.py`** — reads `ideas_in_flight` from state.json; adds them to the prompt context; surfaces them in the brief.

6. **`scripts/send_brief_email.py`** — adds an "Ideas in flight" section above References.

7. **`docs/index.html`** — adds an Ideas panel.

8. **`scripts/metis_audio_brief.py`** — new file. Same LLM cascade as metis_portfolio but with a different system prompt (ELI5, narrative, hype small wins, contextualize against bigger picture). Output: `docs/audio_brief.md`. Run daily or on-demand.

Steps 1-3 are zero-ceremony (just a convention + a list script). 4-7 are mechanical extensions of what exists. Step 8 is a new sister to metis_portfolio.

Estimated effort: ~2 cycles for steps 1-7, ~1 cycle for step 8, sequenced as desired.

## What this doesn't try to do (out of scope for v0)

- Automated "idea quality scoring" — too easy to Goodhart. The status flow + James's judgment is the filter.
- Automated promotion from `drafted` to `promoted` — promotion is a human decision because it commits real attention.
- NotebookLM integration via API — the audio production stays manual (paste markdown into NotebookLM web UI) until there's a clear API path.
- Ideation across multiple humans / multiple intelligences — single-user assumption holds for now.
- A separate "ideas" table in Postgres — file-based docs are sufficient at this scale. Promote to Postgres if the volume justifies it.

## What this implies for the dashboard

The dashboard's role shifts slightly. Today it's *operational observability* — who's alive, what's queued, what just shipped. With ideation pipeline added, it's also *attention routing* — which ideas need James's next look, which deep researches landed today, which agents are stale on the ideas they were supposed to surface.

This matches what James said about orchestration: "where I should focus my time and energy." Operational dashboards show *what's happening*. Attention-routing dashboards show *what needs you next*. Those are different.

---

## Status

This doc itself is `raw` for the ideation-pipeline concept. The first test case (`pivot/idea_learner_solution_steps_corpus_2026-05-17.md`) was captured as part of the proposal. Promote to load-bearing in a future cycle by:

1. Shipping steps 1-7 of v0 implementation
2. Watching whether ideas flow through capture → research → drafted → promote without friction
3. Adding the audio-brief mode (step 8) once the capture flow is proven

# Frontier-Model Review Prompt — Daedalus (Self-Improving Reasoning Ladder Climber)

**Paste-ready for ChatGPT / Claude / Gemini.** Block-quote everything below the `---` and submit. The reviewer's response should be markdown, returned to James for placement at `D:\Prometheus\agents\daedalus\frontier_inbox\<reviewer-name>_<date>_response.md`.

---

You are being asked to review the design of a new agent called **Daedalus**. Daedalus is a self-improving loop-based agent that will run as part of Project Prometheus — an existing falsification-first reasoning substrate for automated mathematical discovery. I need your critique, your additional ideas, and your honest assessment of where the design will fail.

## Background context (skim this; needed to follow the questions)

**Project Prometheus** is a multi-agent system that treats LLM-generated variance as the engine of evolutionary search through mathematical hypothesis space, with ruthless mechanistic selection. Hypotheses are forced through a falsification battery; kills are logged with high-dimensional structured records called KillVectors; the kill-pattern geometry over ~314K logged kills is the gradient field downstream search and training navigate. Major existing agents:

- **Hephaestus** — forges atomic reasoning primitives. ~1,960 tools to date.
- **Apollo** — evolutionarily composes Hephaestus primitives. Current best gen failed a falsification test on 2026-05-24 (apparent compositional reasoning was actually a two-primitive numerical hack; perturbation tests collapsed it).
- **Ergon** — trains on the substrate; "Learner" v1.0 paused awaiting more substrate volume.
- **Aporia** — runs the daily Pythia Deep Research dispatch (~20-30 Gemini Deep Research reports per day).
- **Harmonia** — substrate architecture; runs a 5-child swarm (Phylax, Sophia, Iris, Argos, Telos) on a documented auto-promotion pipeline (`AUTOPROMOTION_TARGETS.md`).
- **Charon** — runs the 4-fold falsification battery.

**The Prometheus Reasoning Ladder** (v0.1, 2026-05-24) defines tier R0 through R12 of reasoning capability, with a specific falsification test per tier:

```
R0  — Pattern response (fails first paraphrase)
R1  — Local operation (applies one known operation correctly)
R2  — Multi-step execution
R3  — Constraint maintenance
R4  — Strategy selection
R5  — Counterfactual control
R6  — Error detection + local repair
R7  — Global plan revision
R8  — Representation shift
R9  — Compositional synthesis
R10 — Epistemic self-modeling
R11 — Substrate formation
R12 — Open-ended research behavior
```

Plus three orthogonal dimensions: **F** (failure transformation depth, F0-F8), **M** (representation mobility, M0-M6), **H** (epistemic humility, H0-H6).

**Core doctrine: a system does not occupy a reasoning tier because its output resembles that tier. It occupies the tier only if the relevant mechanism survives perturbation, beats lower-tier baselines, and fails in the tier-predicted way.**

Apollo's gen-3551 looked R9 (compositional) until the single-primitive-baseline test showed its 2-primitive recipe didn't beat the best of its component primitives. That's the anchor failure mode we're trying to design Daedalus to avoid.

## What Daedalus does

A continuously-running loop. Each iteration does five things:

1. **Self-code evaluation.** Reads its own source; asks a local code-gen LLM (default Qwen2.5-Coder-7B on a 16GB GPU) "what should I change to pass the next-tier falsification test?" Emits a proposed diff.
2. **External ingestion** (three sub-steps in parallel):
   - **2a. Deep Research.** Enqueues 1-3 Pythia DR requests via Gemini Deep Research (Aporia's existing pipeline) per cycle. Capped at 5/day to share quota.
   - **2b. Open-source code.** Searches GitHub/HuggingFace for code addressing analogous problems; pulls into a candidates dir.
   - **2c. Hephaestus Forge.** Scans the Forge ledger for new primitives; imports those matching the current tier challenge.
3. **Enriched logging.** Emits a structured `cycle_<N>.jsonl` with tier attempted, baseline metrics, candidate diffs, sources ingested, test outcomes, complexity delta, adversarial-probe results, score components, decision (keep / park / regress).
4. **TDD.** Three test sources, all must pass: built-in tier falsification tests, Daedalus-generated tests, and frontier-supplied tests. Red → green → refactor. Diffs are sandboxed; only sandboxed passes land in main.
5. **Frontier review emit + inbox scan.** Writes `frontier_outbox/cycle_<N>_review_request.md` (paste-ready prompts for human curation → frontier models). Scans `frontier_inbox/*.md` for responses I have written from prior cycles' frontier responses; ingests asynchronously. **The loop never waits.**

**Pause / resume protocol.** I can intervene at any time by writing a `pause.flag` file. Daedalus halts at end of current cycle. I clean up code by hand, fix bugs, redirect strategy. When I write `resume.flag`, Daedalus picks up.

**Anti-gaming probes.** Every cycle runs single-primitive baseline tests, random-wiring tests, ablation tests, and perturbation tests against Daedalus's own output. Compositions that score high on the headline metric but fail any anti-gaming probe are **parked**, not committed.

**Complexity management.** Each cycle tracks LOC delta, cyclomatic complexity delta, import-graph delta. When any metric exceeds 1.5× its 30-cycle moving average without a tier-lift, the diff rolls back and a `complexity_alarm` fires. Hard cap: 5,000 LOC for v0.1.

**Sequenced rollout:** Phase 0 (week 1, skeleton + R1 baseline) → Phase 1 (weeks 2-3, R1→R2) → Phase 2 (weeks 4-6, R2→R3) → Phase 3 (weeks 7+, indefinite climb).

**Quality expectation:** local LLM code-gen will be poor. I will pause periodically, clean up, resume. The agent is designed to bog down and need intervention.

The full design document is at `D:\Prometheus\pivot\daedalus_design_v01_2026-05-25.md`. I'd appreciate you working from this summary; if you need depth on a specific question, ask me for the relevant section.

## What I want from you

### A. Honest skepticism

Tell me where this will fail. Be specific. I care less about polite suggestions and more about the failure modes the design hasn't accounted for.

### B. Answers to ten open questions

Pick **any 3-5 of these** to engage with substantively. If you want to address all ten, that's welcome. If you have something to say about questions not listed here, also welcome.

1. **Tier transitions.** What is the right signal that Daedalus has "consistently passed" tier N and should target N+1? Cycle count? Perturbation breadth? Cross-validation against a held-out test set? Statistical-significance-adjusted threshold? Something else?

2. **Adversarial discipline.** The Apollo gen-3551 lesson showed that the single-primitive baseline test catches a class of fake-tier output. Are there other falsification tests that should be baked into every cycle, not just at tier transitions? What's the canonical "adversarial battery" for self-improving agents climbing a reasoning ladder?

3. **Local LLM quality.** What's the smallest local model that produces *useful* (not just non-broken) code-gen output for self-improvement tasks at this scope? Are there fine-tuning data sources that would make a 7B model competitive for this niche? Open-weight checkpoints I should know about?

4. **Combinatorial strategy at R5+.** Once Daedalus is composing 5+ Hephaestus primitives, the search space is large. What policy should govern primitive selection — beam search, MCTS, multi-armed bandit, evolutionary, something else? How does this interact with the agent's TDD discipline (every composition must pass falsification tests)?

5. **Complexity vs depth.** The complexity-alarm threshold (1.5× 30-cycle moving average) is a guess. What's the right way to balance "necessary complexity at higher tiers" vs "Icarus growth that needs to be reined in"? Are there published heuristics from self-modifying systems research that should inform this?

6. **Frontier feedback latency.** What's the right cadence for me to curate frontier prompts? Once per cycle? Once per tier transition? When the agent emits a `frontier_review_recommended` event because it has reached a strategic decision point? How does feedback latency affect agent learning when feedback may be days late?

7. **State sharing across pauses.** When I intervene and rewrite a chunk of Daedalus's source, the agent's prior cycles' learning is partially invalidated (its bandit state, its parked-concept rationale, its strategy log all reference code I just changed). How should the agent reconcile pre-pause and post-pause state? Reset some metrics, preserve others?

8. **Neural-network strategy gates.** When does it become correct for Daedalus to write its own neural network (small transformer for routing, or GANN, or RL agent) as part of its self-improvement? What signals justify the complexity cost? Are there examples from the literature of self-modifying systems that successfully introduced neural components?

9. **Park-and-revisit.** Concepts and compositions that score poorly are parked with rationale. Should there be a periodic "revisit parked" sweep, or are parks permanent unless I un-park them? What's the cost of re-evaluating parked concepts against newer substrate?

10. **Coexistence with Apollo.** Apollo is also climbing the ladder via evolutionary composition; Daedalus is climbing via direct code-gen + curation. When (if ever) should these two be coupled? Apollo's elites → Daedalus's primitive imports? Daedalus's solutions → Apollo's seed candidates? Adversarial competition? Cross-validation only?

### C. Ideas the design doesn't include

What's missing? Specifically I'd value ideas on:

- **Reasoning-substrate strategies** beyond combinatorial composition (e.g., program synthesis, neurosymbolic, abstract interpretation, constraint programming)
- **Curriculum design for self-improvement** — what's the right "difficulty progression" given that tiers are not strictly monotonic
- **Failure-mode taxonomy** specific to self-improving agents — what fails differently here than in Apollo's evolutionary loop or Hephaestus's atomic-tool forging
- **Multi-modal substrate sources** — should Daedalus also pull from formal proof libraries (Lean/Coq/Mathlib), interactive theorem provers, or competitive programming corpora?
- **Adversarial agents inside Daedalus** — would a paired "Falsifier" sub-agent that tries to break every commit be useful?
- **Convergence vs divergence** — at what point does Daedalus's continuous tuning hurt rather than help? (Local-optimum trap?)

### D. The Icarus question

The agent is named for Daedalus, the master craftsman whose son Icarus died from over-reaching. The myth is intentional — I expect this agent to bog down and grow complex past usefulness, and the design includes guards (complexity alarm, LOC cap, my intervention protocol). **What additional Icarus failure modes should I expect?** Specifically:

- Reasoning quality regression (the agent gets better at passing its own tests, worse at solving novel problems)
- Substrate corruption (the agent's commits pollute the broader Prometheus substrate)
- Quota addiction (the agent learns to game the DR-budget cap by enqueuing easy questions)
- Adversarial-probe gaming (the agent learns to pass anti-gaming probes by superficial means)

## Response format

A markdown document is ideal. Top-level headings per section above (A. Honest skepticism / B. Open questions / C. Ideas the design doesn't include / D. The Icarus question). Within each section, free-form prose or bullets, your call. Length: I'd rather have 1,500 words of substance than 5,000 of careful hedging.

If you don't have a view on a specific point, say so explicitly. I'd rather know what you don't have a view on than read confident-sounding fill.

If you cite published work, link to it. If you cite specific OSS projects, name them. If you cite specific failure cases from your training, describe them concretely.

Thank you. The agent is being designed honestly and shipped honestly — your critique is part of the falsification discipline this whole project is built on.

— James (Project Prometheus)

---

**End of paste-ready prompt.** Below the line is for your own reference, not for the frontier model:

## Routing instructions (after frontier response arrives)

- Save the frontier response as `D:\Prometheus\agents\daedalus\frontier_inbox\<reviewer-name>_<date>_response.md` where reviewer-name is one of `gpt5` / `claude_opus` / `gemini` / `o3` / etc.
- Daedalus's inbox scanner will pick it up on the next cycle automatically.
- Test-case suggestions in the response move to `tests/frontier_supplied/`.
- Code-snippet suggestions move to `incoming_research/frontier/`.
- Strategy suggestions append to `state/strategy_log.md`.
- Specific design changes recommended by the reviewer get incorporated into `daedalus_design_v0.2_*.md` (the next design revision); the v0.1 draft is preserved unchanged.

## Reviewer-routing checklist

If running this prompt past multiple frontier models in parallel, the diversity is valuable. Suggested rotation:
- ChatGPT (GPT-5 / o3) — strongest on architecture critique
- Claude Opus — strongest on long-form failure-mode reasoning
- Gemini Pro — strongest on related literature + research-citation
- Other (DeepSeek-V4 / Qwen / Llama) — sanity check; surfaces cheap-LLM blind spots

Aim for ≥2 independent reviewers before incorporating major design changes.

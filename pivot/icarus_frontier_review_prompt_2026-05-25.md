# Frontier-Model Review Prompt — Icarus (Experimental Self-Improving Reasoning Ladder Climber)

**Paste-ready for ChatGPT / Claude / Gemini.** Block-quote everything below the `---` and submit. Reviewer's response should be markdown, returned for placement at `D:\Prometheus\agents\icarus\frontier_inbox\<reviewer-name>_<date>_response.md`.

---

You are being asked to review the design of a new experimental agent called **Icarus**. Icarus is a self-improving loop-based agent that will run as part of Project Prometheus — an existing falsification-first reasoning substrate for automated mathematical discovery. The agent is **experimental, not foundational** — I expect it to break frequently. The design includes a strict immutable-lineage mechanism so breakage is recoverable. I need your critique, your additional ideas, and your honest assessment of where the design will fail.

## Background context (skim this; needed to follow the questions)

**Project Prometheus** is a multi-agent system that treats LLM-generated variance as the engine of evolutionary search through mathematical hypothesis space, with ruthless mechanistic selection. Hypotheses are forced through a falsification battery; kills are logged with high-dimensional structured records called KillVectors; the kill-pattern geometry over ~314K logged kills is the gradient field downstream search and training navigate.

Major existing agents:
- **Hephaestus** — forges atomic reasoning primitives. ~1,960 tools to date.
- **Apollo** — evolutionarily composes Hephaestus primitives. Its current best generation failed a falsification test on 2026-05-24 (apparent compositional reasoning was actually a 2-primitive numerical hack; perturbation tests collapsed it).
- **Ergon** — trains on the substrate; "Learner" v1.0 paused awaiting more substrate volume.
- **Aporia** — runs the daily Pythia Deep Research dispatch (~20-30 Gemini Deep Research reports per day).
- **Harmonia** — substrate architect; runs a 5-child swarm (Phylax, Sophia, Iris, Argos, Telos) on a documented auto-promotion pipeline.
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

Plus three orthogonal dimensions: F (failure-transformation depth), M (representation mobility), H (epistemic humility).

**Core doctrine: a system does not occupy a reasoning tier because its output resembles that tier. It occupies the tier only if the relevant mechanism survives perturbation, beats lower-tier baselines, and fails in the tier-predicted way.**

Apollo's gen-3551 looked R9 until the single-primitive-baseline test showed its 2-primitive recipe didn't beat the best of its component primitives. That's the anchor failure mode we're designing Icarus to avoid.

## What Icarus does

A continuously-running loop. **Each iteration begins by cloning the last *stable* cycle's frozen snapshot** into a new cycle directory; that clone is the working tree. Then five steps run:

1. **Self-code evaluation.** Reads the cloned source; asks a local code-gen LLM (default Qwen2.5-Coder-7B via Ollama on a 16GB GPU) "what should I change to pass the next-tier falsification test?" Emits a proposed diff.
2. **External ingestion** (three sub-steps in parallel):
   - **2a. Deep Research.** Enqueues 1-3 Pythia DR requests per cycle (capped 5/day).
   - **2b. Open-source code.** Searches GitHub/HuggingFace for analogous code; pulls into a candidates dir.
   - **2c. Hephaestus Forge.** Scans the Forge ledger for primitives matching the current tier challenge; imports them.
3. **Enriched logging.** Structured `cycles/cycle_<N>/log.jsonl` records phase outcomes, metrics, complexity deltas, adversarial-probe results, decision.
4. **TDD.** Three test sources, all must pass: built-in tier falsification, Icarus-generated, frontier-supplied. Red → green → refactor. Diff applied in-place inside the cycle directory.
5. **Frontier review emit + inbox scan.** Writes `frontier_outbox/cycle_<N>_review_request.md`. Scans `frontier_inbox/*.md` for responses; ingests asynchronously. **The loop never waits.**

Then **(implicit step 6) freeze + stability decision**:
- The cycle directory becomes immutable (forensic snapshot).
- If all gates passed → update `state/last_stable_cycle.json` → pointer to N. Next iteration clones from N.
- If gates failed → pointer unchanged. Next iteration clones from the same prior stable. Cycle N stays frozen as forensic record.

**Critical architectural element: each cycle is a frozen full snapshot of the working tree.** The lineage discipline is from a prior James-built agent where this made breakage recoverable. Three revert paths:
- Automatic (failed cycles don't advance the pointer)
- Manual single-step (James edits `last_stable_cycle.json`)
- Manual fork (James copies an older cycle and edits)

Failed cycles are PARKED (frozen for forensics), not deleted. The lineage is the audit trail of every attempt.

**Anti-gaming probes every cycle:** single-primitive baseline test, random-wiring, ablation, perturbation. Failures park, not commit.

**Complexity guard:** 1.5× 30-cycle moving average per metric (LOC, cyclomatic, import-graph, test-runtime). Hard cap: 5,000 LOC for v0.1.

**Pause / resume protocol:** James writes `pause.flag` → halts at end of current cycle. James edits, repoints, intervenes. Writes `resume.flag` → resumes. Hard kill via `kill.flag`.

**Disk-usage envelope:** ~500KB-2MB per cycle × 1,000 cycles ≈ 1-2 GB. v0.2 adds tarball archival of parked cycles >30 days.

**Sequenced rollout:** Phase 0 (week 1, skeleton + R1 baseline + exercise lineage mechanism with 10 no-op cycles) → Phase 1 (weeks 2-3, R1→R2) → Phase 2 (weeks 4-6, R2→R3) → Phase 3 (weeks 7+, indefinite).

The full design document is at `D:\Prometheus\pivot\icarus_design_v01_2026-05-25.md`. I'd appreciate you working from this summary; if you need depth on a specific question, ask me for the relevant section.

## What I want from you

### A. Honest skepticism

Tell me where this will fail. Be specific. I care less about polite suggestions and more about the failure modes the design hasn't accounted for. The agent's name is "Icarus" because I expect it to fall.

### B. Answers to eleven open questions

Pick **any 3-5 of these** to engage with substantively. If you have something to say about questions not listed here, also welcome.

1. **Tier transitions.** What signal indicates Icarus has "consistently passed" tier N and should target N+1? Cycle count? Perturbation breadth? Cross-validation against a held-out test set? Statistical-significance-adjusted threshold?

2. **Adversarial discipline.** The Apollo gen-3551 lesson showed that the single-primitive baseline test catches a class of fake-tier output. Are there other falsification tests that should be baked into every cycle? What's the canonical "adversarial battery" for self-improving agents climbing a reasoning ladder?

3. **Local LLM quality.** What's the smallest local model that produces *useful* (not just non-broken) code-gen output for self-improvement tasks at this scope? Fine-tuning data sources that would make a 7B model competitive for this niche? Open-weight checkpoints worth knowing?

4. **Combinatorial strategy at R5+.** Once Icarus is composing 5+ Hephaestus primitives, the search space is large. What policy should govern primitive selection — beam search, MCTS, multi-armed bandit, evolutionary, something else? How does this interact with the TDD discipline?

5. **Complexity vs depth.** The complexity-alarm threshold (1.5× 30-cycle moving average) is a guess. What's the right way to balance "necessary complexity at higher tiers" vs "growth that needs to be reined in"? Heuristics from self-modifying systems research?

6. **Frontier feedback latency.** What's the right cadence for me to curate frontier prompts? Per cycle? Per tier transition? When the agent emits a `frontier_review_recommended` event? How does feedback latency affect agent learning when feedback may be days late?

7. **Lineage state reconciliation.** When I edit a frozen cycle or repoint the stable pointer, the agent's prior cycles' learning is partially invalidated (its bandit state, parked-concept rationales, strategy log). How should the agent reconcile pre-revert and post-revert state? Reset some metrics, preserve others?

8. **Neural-network strategy gates.** When does it become correct for Icarus to write its own neural network (small transformer for routing, GANN, RL agent) as part of self-improvement? What signals justify the complexity cost? Examples from the literature?

9. **Park-and-revisit.** Concepts and compositions that score poorly are parked. Should there be a periodic "revisit parked" sweep, or are parks permanent unless I un-park them? What's the cost of re-evaluating parked concepts against newer substrate?

10. **Coexistence with Apollo.** Apollo is also climbing the ladder via evolutionary composition; Icarus via direct code-gen + curation. When (if ever) should these two be coupled? Apollo's elites → Icarus's primitive imports? Icarus solutions → Apollo's seed candidates? Adversarial competition? Cross-validation only?

11. **Lineage explosion + pruning.** At what cycle count or disk-usage threshold should the lineage start being pruned/archived? What's the right retention policy for parked cycles given their forensic value diminishes over time? Are there published practices from version-controlled experimentation systems (e.g., DVC, MLflow, Weights & Biases) that should inform this?

### C. Ideas the design doesn't include

What's missing? Specifically I'd value ideas on:

- **Reasoning-substrate strategies** beyond combinatorial composition (program synthesis, neurosymbolic, abstract interpretation, constraint programming)
- **Curriculum design for self-improvement** — what's the right "difficulty progression" given that tiers are not strictly monotonic
- **Failure-mode taxonomy** specific to self-improving agents — what fails differently here than in Apollo's evolutionary loop or Hephaestus's atomic-tool forging
- **Multi-modal substrate sources** — should Icarus also pull from formal proof libraries (Lean/Coq/Mathlib), interactive theorem provers, or competitive programming corpora?
- **Adversarial agents inside Icarus** — would a paired "Falsifier" sub-agent that tries to break every commit be useful?
- **Convergence vs divergence** — at what point does Icarus's continuous tuning hurt rather than help? (Local-optimum trap?)
- **Cycle-graph analysis** — given that every cycle's parent is recorded, the lineage forms a DAG. Are there published techniques for mining DAGs of failed/successful experiments to extract general principles?

### D. The Icarus question

The agent is named for Icarus, who flew too close to the sun. The myth is intentional — I expect the agent to bog down, grow complex past usefulness, hallucinate progress, or game its own tests. The design includes guards:

- Immutable frozen lineage → revert is a pointer update
- Complexity alarm (1.5× moving avg)
- Hard LOC cap (5,000 for v0.1)
- Adversarial probes every cycle (the gen-3551 lesson)
- Pause/resume protocol for human intervention

**What additional Icarus failure modes should I expect?** Specifically:

- Reasoning quality regression (the agent gets better at passing its own tests, worse at solving novel problems)
- Substrate corruption (the agent's commits pollute the broader Prometheus substrate)
- Quota addiction (the agent learns to game the DR-budget cap by enqueuing easy questions)
- Adversarial-probe gaming (the agent learns to pass anti-gaming probes by superficial means)
- Lineage-thrash (rapid park-stable-park-stable oscillations that look like progress but aren't)
- Revert-paralysis (after several revert episodes, the agent is stuck at a sub-optimal early cycle and can't climb)
- Forensic-corpus exhaustion (the parked cycles accumulate but no learning gets extracted from them)

## Response format

A markdown document is ideal. Top-level headings per section above (A. Honest skepticism / B. Open questions / C. Ideas the design doesn't include / D. The Icarus question). Within each section, free-form prose or bullets, your call. Length: I'd rather have 1,500 words of substance than 5,000 of careful hedging.

If you don't have a view on a specific point, say so explicitly. I'd rather know what you don't have a view on than read confident-sounding fill.

If you cite published work, link to it. If you cite specific OSS projects, name them. If you cite specific failure cases from your training, describe them concretely.

Thank you. The agent is being designed honestly and shipped honestly — your critique is part of the falsification discipline this whole project is built on.

— James (Project Prometheus)

---

**End of paste-ready prompt.** Below the line is reference, not for the frontier model:

## Routing instructions (after frontier response arrives)

- Save as `D:\Prometheus\agents\icarus\frontier_inbox\<reviewer-name>_<date>_response.md` where reviewer-name is `gpt5` / `claude_opus` / `gemini` / `o3` etc.
- Icarus's inbox scanner picks it up on the next cycle.
- Test-case suggestions → `tests/frontier_supplied/`.
- Code-snippet suggestions → `incoming_research/frontier/`.
- Strategy suggestions → `state/strategy_log.md`.
- Major design changes → incorporate into `icarus_design_v0.2_*.md` (next revision); v0.1 preserved unchanged.

## Reviewer-rotation checklist

Suggested rotation across frontier models:
- ChatGPT (GPT-5 / o3) — strongest on architecture critique
- Claude Opus — strongest on long-form failure-mode reasoning
- Gemini Pro — strongest on related literature + research-citation
- Other (DeepSeek-V4 / Qwen / Llama) — cheap-LLM sanity check; surfaces blind spots

Aim for ≥2 independent reviewers before incorporating major design changes into v0.2.

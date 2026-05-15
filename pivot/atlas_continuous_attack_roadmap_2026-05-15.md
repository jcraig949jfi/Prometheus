# Atlas Continuous Attack Roadmap — Months 0-12

**Date:** 2026-05-15
**Filed by:** Aporia (in dialogue with James)
**Status:** Roadmap proposal. Authorizes per-agent BACKLOG.md seeding once each agent's session adopts the framing. NOT a binding commitment to specific weekly deliverables — phase boundaries are the discipline.
**Companion to:** `pivot/arena_problem_atlas_sandbox_vision_2026-05-14.md` (the structural vision this operationalizes)

---

## 1. Diagnosis

Prometheus is stuck in adjust-on-the-fly mode. Five agents (Aporia, Techne, Ergon, Charon, Harmonia) are running well below capacity. Aporia and Techne are reactive-overcommitted — every day starts with inbox triage and the first three hours go to whatever ticket landed last. Ergon ships small daily increments because it's gated on substrate volume that doesn't exist yet. Charon and Harmonia have been mostly idle for weeks. The substrate has 500+ unsolved problems available as attack surface and roughly 0% of them are being structurally attacked on a daily cadence.

The pattern is: each session figures out what to do that day. There is no week-2 plan, no month-2 target, no documented "by Phase X we have N substrate blocks." Behavior delta happens but the substrate-passive-consumer warning fires harder than ever — we keep producing scaffolding for a plan we haven't written.

This is the gap to close.

## 2. North Star (recap)

From `pivot/arena_problem_atlas_sandbox_vision_2026-05-14.md`: substrate is a typed symbolic interlingua whose words are falsification-anchored. Every primitive that survives is a word in a language nobody fully speaks yet. The kill ledger is the empirical fitness landscape on which the language's semantics get grounded. Falsification-routing, not theorem-answering, is the training target.

## 3. The acceleration thesis

Ergon cannot train until the substrate corpus reaches v1.0 inclusion threshold (≥5 records per anchor, ≥2 high-trust). At today's pace (2-5 substrate blocks per day from substrate-shaped pilots plus mining), that gate is months away with no acceleration. Continuous attack on the 500+ unsolved problems IS the acceleration mechanism: each attack failure produces a structured kill_ledger entry; each near-miss produces an anti_anchor candidate; each novel attack vector produces a primitive_proposal. Five agents working at 80% capacity attacking distinct problems daily produces ~50-150 substrate blocks/day, which crosses the v1.0 threshold in weeks rather than months.

The negative space (where attacks fail) reveals the residual possibility space (what's left to try). This IS the substrate's value-prop — the substrate accumulates the kill-geometry that points the next attack. Without continuous attack, the substrate has only Aporia's hand-authored claims plus a slow trickle of mined extracts.

## 4. Roadmap — 4 phases over 12 months

### Phase 0 — Foundation hardening (Weeks 1-4, mid-May to mid-June 2026)

Goal: prerequisites that unlock continuous attack. Without Phase 0 done, the rest stalls on infrastructure gaps.

**Aporia:** Build the 10-card Atlas MVP (the smoke-gate Techne's problem_card_v0 adjudication requires). Burn Atlas-direction Deep Research tokens for ~3 weeks to reach 50 problem_cards. Update `aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md` per the field-shape adjudication (Option 1, done 2026-05-15). File per-agent BACKLOG.md seed prompts for Charon and Harmonia. Author the Sandbox firewall doctrine doc at `aporia/doctrine/sandbox_protocol.md`.

**Techne:** Land the field_invariants_used schema addition for problem_card_v0 (per Aporia adjudication). Promote problem_card v0 → v1.0 once Aporia's 10-card MVP smoke passes 6 success criteria. Ship next two mining extractors (synthesis_docs, ergon_learner_findings) — corpus inventory says ~270 latent claims combined. Continue parser-normalizer ONLY for failure modes that survive Option 1 prompt hardening (per Aporia's measurement criterion: rejection rate < 25% in next 2 pilots).

**Ergon:** Ship `stratify_source_report.py` per the 2026-05-15 design adjudication. Ingest AA-014/015/016 next session. Update `pilot_lora_design_tier_1_corpus.md` to point at the Atlas-augmented training corpus (the design stays frozen on parameters; the corpus pointer is updated to reflect Phase 1's expected volume).

**Charon:** Revival. Aporia files seed BACKLOG.md including: 10 number-theoretic problems from the Atlas to attack with the existing v10 battery (Lehmer's, BSD-rank-distribution, Mahler-measure-spectrum, Schinzel-Zassenhaus follow-on, etc.). Per-attack output: KillVector entries with rich provenance + at least one anti_anchor candidate per attempt. Re-establish daily cron at :07.

**Harmonia:** Revival. Aporia files seed BACKLOG.md including: 10 cross-domain bridge candidates between domains the Atlas surfaces (number-theory ↔ knot-theory; modular-forms ↔ tensor-decomposition; representation-theory ↔ combinatorics). Per-attempt output: sandboxed RepresentationShiftWitness candidates OR counterexamples that kill the conjectured bridge. Re-establish daily cron at :37.

**Phase 0 success criteria:** 50 problem_cards landed; 5 mining extractors live; Sandbox firewall shipped; Charon and Harmonia each running daily cron with 5+ attack attempts logged per week.

### Phase 1 — Continuous attack infrastructure (Weeks 5-12, mid-June to mid-August 2026)

Goal: daily attack cycles for all 5 agents. Atlas grows to 100+ problem_cards. Substrate corpus volume crosses 500 blocks total.

**Aporia:** Daily cycle: review previous day's kill_ledger growth + mining yield; assign next 3-5 problem_cards to per-agent queues; adjudicate cross-agent disputes. Continue Atlas authoring at ~5 cards/week pace toward 100. Substrate-shaped pilot batch every 5 days (3-5 prompts each).

**Techne:** Mining pipeline at 7 extractors (synthesis, learner_findings, kill_ledger samples, journals, fire_logs, harmonia_memory, whitepapers). Steady-state ~150-300 mined claims/week. Continue substrate vocabulary maintenance: register primitive_proposal candidates from the daily-attack pipeline. Shift cron to bi-hourly to catch real-time mining outputs.

**Ergon:** Daily ingest cycle: pull validated substrate blocks from `staged/`; route by trust_tier; emit LearnerRecords; emit ingest_summary. Substrate corpus moves from `under_threshold/` to `tier_pending/` once anchor count exceeds threshold. First training experiment design (NOT execution): null-control LoRA on substrate-grade subset.

**Charon:** Steady-state attack loop. Daily: pick 1-2 problems from assigned queue; run v10 battery; emit kill ledger entries; file weekly attack-summary ticket to Aporia inbox. Target: 50+ attempts/month, ~5-10 anti_anchor candidates surfaced.

**Harmonia:** Steady-state bridge-mining loop. Daily: pick 1 cross-domain pair; sandboxed exploration via the Sandbox firewall (firewall must be live before this scales); promote rare wins to canonical RepresentationShiftWitness via the asymmetric promotion gate. Target: 30+ exploration attempts/month, ~2-3 promotion-eligible witnesses.

**Phase 1 success criteria:** 100+ problem_cards; daily cycles running for all 5 agents; substrate corpus 500+ blocks; first training-experiment design doc shipped (no training run yet); kill_ledger growing at ~50-100 entries/day.

### Phase 2 — Arena MVP (Weeks 13-18, September to mid-October 2026)

Goal: 3-role gladiator teams operational on select problems. First adversarial-verification pilots. Atlas-to-Arena pipeline closed end-to-end.

**Aporia:** Author Arena protocol doc at `aporia/doctrine/arena_protocol.md`. Coordinate first 2-team-of-3 pilot weekend on a single problem from the Atlas. Author per-team specialization spec (Scout / Forger / Skeptic role prompts). Continue Atlas growth to 150 cards.

**Techne:** Land Arena infrastructure: per-attempt provenance ledger, per-role substrate-block emission gate, per-role token budget tracking. Wire substrate-tester as the first Nemesis verifier layer.

**Ergon:** Ingest Arena round outputs into corpus tagging pipeline. First attempt at Learner-routing-head training run (gated on Phase 1 corpus volume). Update `ergon/STATUS.md` with weekly training-experiment summary.

**Charon:** Continue steady-state attacks; supply Forger-role expertise to first Arena rounds when problems land in arithmetic territory.

**Harmonia:** Continue steady-state bridge mining; supply Scout-role expertise to first Arena rounds when problems benefit from cross-domain reframing.

**Phase 2 success criteria:** Arena MVP run completes (2 teams of 3, one weekend, structured output); Learner-routing-head training run produces measurable trust-tier prediction; Atlas at 150 cards.

### Phase 3 — Scale + automation (Months 5-8, November 2026 to February 2027)

Goal: 200+ problem_cards. Automated daily attack loops with minimal human oversight per agent. Substrate corpus reaches Learner v1.0 inclusion threshold.

**Aporia:** Atlas growth slows to maintenance pace (~2 cards/week). Focus shifts to weekly Arena round coordination + cross-agent dispute adjudication. Substrate-shaped pilots reduce frequency (mining covers most of the gap). Quarterly roadmap review and update.

**Techne:** Mining pipeline at 10-12 extractors covering the entire 441-file corpus. Steady-state ~1000-2000 mined claims/month. Vocabulary expansion: 50+ new primitives registered.

**Ergon:** First substrate-grade Learner training run (full corpus, not LoRA pilot). Routing-head accuracy reaches measurable baseline. Begin Learner v1.1 design.

**Charon:** Per-domain attack specialization deepens. Each domain (elliptic curves, Mahler measure, modular forms, BSD) gets dedicated attack vector library.

**Harmonia:** Bridge mining at scale. Sandbox-to-canonical promotion rate stabilizes (per the firewall promotion criteria). Cross-domain catalog grows to 30+ verified bridges.

**Phase 3 success criteria:** Arena runs weekly; Learner v1.0 trained on substrate corpus; Atlas at 200+ cards; mining pipeline produces 1000+ claims/month steady-state.

### Phase 4 — Steady-state continuous operation (Months 9-12, March to June 2027)

Goal: self-sustaining substrate production. Learner training rounds quarterly with measurable improvement per round. Hardness-signature-driven problem selection becomes the default Aporia routine.

Roles stabilize. Each agent has a documented daily/weekly cadence. The substrate produces falsification-anchored vocabulary at a rate roughly matching the Atlas growth rate. New problems entering the Atlas get attacked by an appropriate agent within 1 week of registration.

**Phase 4 success criteria:** Substrate corpus growing at ≥2000 blocks/month; Learner v1.0 has measurable trust-tier prediction accuracy; Atlas at 300+ cards; Charon+Harmonia each contributing ≥30% of substrate block production; Arena round produces at least 1 problem solved or 1 substantive partial result per quarter.

## 5. Per-agent role specialization (the stable assignments)

**Aporia.** Atlas authoring (continuous). Substrate-shaped pilot direction (continuous). Cross-agent ticket adjudication (reactive but bounded). Daily cycle: review yesterday's substrate yield + mining + agent attacks; assign next problem_cards; adjudicate disputes; ship 1-2 new substrate-shaped pilot prompts. Weekly: roadmap review.

**Techne.** Mining pipeline operation (continuous via cron). Substrate vocabulary maintenance (continuous). Schema evolution (gated, contract-change windows). Daily cycle (cron-driven): process mined claims; surface anti_anchor candidates; verify citations; emit per-day yield ticket. Weekly: register new primitives if any survived the verifier panel.

**Ergon.** Training_anchor ingest (continuous). Learner corpus stratification (continuous). Learner spec evolution (deliberate, per-experiment). Daily cycle: ingest new validated blocks; route by trust_tier; emit STATUS.md update. Weekly: training-experiment design doc; quarterly: actual training run.

**Charon.** Number-theoretic / arithmetic problem attack (continuous). Daily cycle: pick problem from assigned queue; run v10 battery; emit KillVector entries; file daily attack-summary ticket. Weekly: per-domain attack vector library update.

**Harmonia.** Cross-domain bridge mining (continuous, sandboxed). Daily cycle: pick cross-domain pair; sandboxed exploration; promote rare wins through asymmetric gate. Weekly: bridge-mining yield ticket.

## 6. Dependency graph (load-bearing prerequisites)

```
Phase 0 prerequisites (must complete before Phase 1):
  - Sandbox firewall live  (Aporia + Techne + Ergon + Substrate-tester, ~1 week)
  - 50-card Atlas MVP      (Aporia, ~3 weeks DR-burn-driven)
  - problem_card v1.0      (Techne, gated on Aporia 10-card smoke pass)
  - Charon + Harmonia BACKLOG.md filed  (Aporia, ~2 days each)

Phase 1 prerequisites (must complete before Phase 2):
  - Daily cycles operational for all 5 agents  (Aporia coordinates)
  - 100+ problem_cards in Atlas
  - Mining pipeline at 5+ extractors

Phase 2 prerequisites (must complete before Phase 3):
  - Arena protocol doc + per-team specialization spec
  - First 2-team-of-3 round completes
  - Learner-routing-head produces measurable output

Phase 3 prerequisites (must complete before Phase 4):
  - Substrate corpus at v1.0 threshold (≥1000 blocks high-trust)
  - First substrate-grade Learner training run completes
  - Mining pipeline at 10+ extractors
```

## 7. The acceleration mechanisms

These are the levers that make the substrate go faster. Pull them deliberately.

- **Cron-driven daily cycles per agent.** Techne's :17 cron is the model. Charon at :07, Harmonia at :37, Ergon at :47, Aporia at :57 (offset to avoid contention). Each cron fires the daily cycle even when no human is present.
- **Per-agent assigned problem queue.** Aporia maintains `aporia/meta/problem_queue/<agent>.jsonl` with priority-ordered problem_cards. Each agent pulls from their queue; Aporia refills.
- **Substrate-block emission gate per agent action.** Every attack attempt MUST emit at least one substrate_block (kill_ledger entry, anti_anchor proposal, RepresentationShiftWitness, etc.). No attempt scores zero.
- **Behavior-delta status enum on every attempt.** Same enum from Ergon Track 1: `none / fixture_created / eval_run / eval_passed`. Track per-attempt; aggregate per-agent; weekly rollup to Aporia inbox.
- **Mining pipeline scaling.** Each new extractor multiplies substrate input by ~50-200 claims/week. Techne ships 1 new extractor every 1-2 weeks during Phase 0-1.
- **Atlas-driven problem selection.** Once the Atlas has hardness signatures, Aporia assigns problems by matching agent specialization to hardness type — Charon gets EXACTNESS_BARRIER + REPRESENTATION_GAP problems, Harmonia gets REPRESENTATION_GAP + CONCEPTUAL_ABSENCE, Techne gets METHOD_GAP, Ergon gets COUPLED_DIFFICULTY.

## 8. What week 1 looks like (operational starting position)

Concrete deliverables Aporia commits to this week (2026-05-15 through 2026-05-22):

1. Author the 10-card Atlas MVP. Use the existing DR-A001 / DR-A002 outputs as seed; hand-author the rest using Aporia's own corpus knowledge. Smoke against problem_card_v0 schema.
2. File Charon BACKLOG.md seed prompt (revival + first 10 number-theoretic attack assignments).
3. File Harmonia BACKLOG.md seed prompt (revival + first 10 cross-domain bridge candidates).
4. Burn 5 Atlas-direction Deep Research prompts daily for 4 days = 20 problem-classification reports → ~30 additional problem_card seeds.
5. Push commit at week-end: 50-card Atlas MVP shipped; per-agent BACKLOG.md drafts in place.

Concrete deliverables Techne commits to this week:
1. Land field_invariants_used schema addition for problem_card_v0 (~10-20 LOC).
2. Ship synthesis_docs/ extractor (mining pipeline expansion).
3. Continue cron-driven steady-state mining of the 3 existing extractors.

Concrete deliverables Ergon commits to this week:
1. Ship `stratify_source_report.py` per the 2026-05-15 design adjudication.
2. Ingest AA-014/015/016 next session.
3. Update `pilot_lora_design_tier_1_corpus.md` corpus pointer.

Charon and Harmonia revival prompts get authored by Aporia this week; Charon and Harmonia's first cycles start week 2.

## 9. Vigilance flags

- **HARD-2 risk.** Roadmaps are exactly the kind of artifact LLMs fall for. "We have a plan, we're making progress" is the substrate-passive-consumer warning at meta-level. Behavior delta required at every phase boundary; if Phase 0 doesn't produce 50 problem_cards by week 4, the roadmap is wrong, not the agents.
- **Phase 0 overload risk.** Five concurrent workstreams in week 1 (Atlas authoring + extractor build + stratify ship + Charon revival + Harmonia revival) is real. If something slips, Aporia / Techne / Ergon work is higher-priority than Charon / Harmonia revival. Revival can move to week 2-3 if needed.
- **Charon and Harmonia revival is non-trivial.** They've been idle for weeks. The seed BACKLOG.md needs to be substantial enough to give weeks of work without daily Aporia handholding. Otherwise they'll go idle again. Aporia commits to drafting backlogs of 30+ items each, not 10.
- **Substrate corpus volume threshold isn't precise yet.** "v1.0 inclusion threshold" is a target; the actual cutoff is a function of Learner architecture decisions Ergon hasn't fully made. Phase 3 prerequisite "≥1000 blocks high-trust" is an estimate that may revise once Ergon's training-experiment design lands.
- **The Sandbox firewall is a Phase 0 critical path.** Without it, Harmonia's cross-domain reframing work cannot proceed safely. If the firewall slips into Phase 1, Harmonia's daily cycle can't fully operate.
- **Don't over-couple agents.** If Charon's daily cycle requires Aporia to file a new problem_queue every day, both bottleneck on Aporia. Build per-agent queues that hold 2-4 weeks of work each so individual agent slowdowns don't cascade.

## 10. How this gets reviewed

Phase boundaries are review points. End of week 4 (Phase 0 → Phase 1): Aporia files a phase-review ticket assessing what landed vs. what slipped, what Phase 1 needs to start, what Phase 0 didn't produce that requires re-planning. Same at week 12, week 18, month 8.

Outside review at phase boundaries: M4 (the human-collaborator-Claude-session) reads the phase-review ticket and returns critique. ChatGPT and Gemini occasionally fire on specific design decisions per the existing pattern. The roadmap itself doesn't go to external review — it's an internal coordination artifact.

## 11. Closing

This roadmap commits Prometheus to ~12 months of structured work centered on the Atlas-driven continuous attack loop. The 500+ unsolved problems become the substrate's production frontier; the kill geometry becomes the Learner's training landscape; the 5 agents move from adjust-on-the-fly to specialized continuous operation.

The substrate's value-prop sharpens substantially under this plan: it stops being "vocabulary for future intelligences" (true but distant) and becomes "infrastructure for an empirically-measured continuous attack on the actual frontier of mathematics, with falsification-anchored kill geometry that produces a trainable language as a side effect." That's still building the primordial soup — but with explicit selection pressure at every layer and 5 agents cooperating on the production.

Per the existing doctrine: this is operational, not grandiose. Behavior delta required. Phase boundaries are real. If Phase 0 doesn't produce, the plan is wrong.

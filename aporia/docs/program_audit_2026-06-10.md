# Prometheus Program Audit — 2026-06-10

**Author:** Aporia (full-program assessment, 8 parallel deep audits)
**Scope:** All roles, agents, closed loops, pivot documents, doctrine, and source code.
**Question:** Where is time best spent to move toward the north star — synthetic reasoning technology that grows stronger with each iteration?

---

## 1. Executive Summary

The program is not failing at falsification — it is failing at **consumption**. Every
major loop produces artifacts no downstream system consumes, and every monoculture
traces to a single concrete code location, not to a mysterious emergent dynamic.

The five-sentence diagnosis:

1. **Theseus** emitted 658M records (367M kills) into a corpus with **zero consumers** —
   the Learner handoff has consumed nothing since May 19, and the loop ran 90
   consecutive zero-promotion batches before stalling.
2. **Ergon's Learner** trained on a corpus that inverted the doctrine — 79% confirmations,
   1.4% failures — because the handoff mapper serializes exactly one claim_kind
   (`invariant_equality`) and the weight threshold excludes the kills.
3. **The measurement layer is the program's crown jewel**: permutation nulls, the Hodge
   decomposer, calibration v3, and Phase 3.K honestly killed every false signal claim,
   including our own strongest ones (v2 corpus coupling, Erebos Layer-2).
4. **Three genuine signals toward the north star exist** and none is being scaled:
   warm-start behavioral routing (+0.075 AUC, survives adversarial tail), worked-derivation
   training (+0.16 in-op transfer), and Hephaestus failure-mined engines (+11pp/+32pp).
5. The 2026-05-11 "substrate volume first" pivot was the wrong lever — volume without a
   consumer produced the /dev/null corpus; the right gate is **consumption and transfer,
   not volume**.

**Recommendation in one line:** stop all production loops that lack a consumer, fix the
three small, fully-diagnosed code breaks that strand >100M failure records, and rebuild
the program around one compounding loop: generate → train → transfer-eval → route
failures behaviorally → mine residue into the next iteration's data and tools.

---

## 2. North Star & Current Ladder Position

Canonical formulations (CONSTITUTION.md, prometheus_thesis_v2.md):
- "Demote the LLM from oracle to mutation operator and put a structural-falsification
  engine downstream."
- "Optimization consumes failure; Prometheus metabolizes failure."

Reasoning Ladder (R0–R9, reasoning_ladder_design_2026-05-15.md):
R0 recognition → R1 rule execution → R2 multi-step deduction → R3 abstraction/rule
discovery → R4 search/backtracking → R5 counterfactual/causal → R6 self-monitoring →
R7 OOD transfer → R8 conjecture formation → R9 research-grade.

**Honest current position of the Learner: R0–R1 surface.** The greedy LoRA's +0.68
decomposes into format-following (~0.61), relation base-rate priors, and per-template
memorization; genuine reasoning is ~0.10 and does not transfer across domains
(summation/inequality flat at chance). The compute-trace experiment shows R2 is
reachable: worked derivations give +0.16 within-op transfer. **R3 (cross-op
abstraction) is the wall** — zero transfer where computation is required, and modexp
ceilings at ~0.52 on 1.5B regardless of traces (capacity bound).

The multi-agent *system* operates with R9-grade discipline (preregistration, nulls,
adversarial audit) — but the system's discipline is not the model's capability, and the
model is the deliverable.

---

## 3. Subsystem Verdicts

### 3.1 Theseus (batch-generation loop) — KILL the continuous loop, KEEP as harness
- 273 batches, 658M records, 2,351 promoted (0.000357%), 0 verified findings.
- Stalled since Fire #234 (2026-05-30); it was always a one-shot CLI, never a managed loop.
- Monoculture root causes (code-level):
  - `theseus/generators/a1_catalog_cross_product.py:49` — ONE hardcoded 4-relation tuple
    shared by 25+ generators.
  - `theseus/config.py:25-26` — single catalog pair (52 knots × ~1000 ECs); no other
    pairing exists anywhere.
  - All 55 generators are the same sample-catalog-test-emit shape; the 20-gen "monoculture
    breaking" cohort (K1–Z1) produced <4% of corpus volume.
- Keep: A1 (null control), D1 (kill-neighborhood), A3 (refactored, skip trivial cells),
  H2 (post-refactor structured kill patterns). Kill or merge: F-family, C-family into
  single controllers; E2–E5 to on-demand; K1–Z1 cohort except M1.
- **Do not restart until a real consumer exists.**

### 3.2 Ergon / Learner — REFACTOR; the failure is fully diagnosed and the fixes are small
- Greedy LoRA v1: gold 0.907 vs base 0.228, but shuffled-label control 0.681; decomposition:
  format ~0.61, priors ~0.52-relative, memorization ~0.12, genuine reasoning ~0.10.
  Zero cross-source and zero cross-domain transfer (per-source ablations; OOD NT 0.550
  with T=0.20/F=0.90 asymmetry).
- Monoculture root causes (code-level):
  - `theseus/handoff/ergon_handoff.py:116-117` — mapper serializes only
    `invariant_equality`; 15+ other claim_kinds fall through to unparseable placeholders.
  - `theseus/handoff/ergon_handoff.py:185-197` — weight threshold 0.5 while
    invariant_equality kills score ~0.2 → nothing both mappable and above threshold.
  - The fix already exists in-repo: `ergon/learner/greedy/serializers.py` renders all
    claim_kinds correctly. Porting it is ~100 lines.
- Corpus on disk: 1,486 LearnerRecords (telemetry claimed 46.5K — 31× overcount),
  71% knots×EC, **79% promoted / 1.4% rejected** — the doctrine inverted at ingestion.
- Stranded failure data one adapter away: Theseus ~108M REJECTED, Techne 360M+ kills,
  Charon pantheon 1,255 structured kill-ledger rows, Hephaestus 4,546 scraps.
- Salvage: Σ-kernel, MAP-Elites archive/descriptor, greedy serializers, compute-trace
  infrastructure, eval_greedy.py (already supports entity-disjoint + transfer testing).

### 3.3 Aporia instruments — KEEP; this is the measurement backbone
- Hodge decomposer (stage0, 47 tests) + relational pipeline (stage0b, 50 tests): proven
  on positive controls (planted Condorcet cycle BEATS_NULL p=0.005; Efron dice curl 0.986),
  honest NULLs on math objects (genus-2 fair test p=0.355). NULLs are true negatives.
- The conservative-by-construction catch (flow = Δ(node scalar) ⇒ gradient identically)
  was caught in design, before expensive runs — the discipline works.
- Routing eval (preregistered, 2026-06-09): cold-start metadata routing NULL
  (ΔAUC −0.009); warm-start collaborative +0.075 (p<0.0001, survives drop-top-8 tail).
  **Residue is navigable behaviorally, not semantically.**
- Reasoning H-R1 is one logging change from a real answer: per-evaluator vectors
  (`reasoning_quality_emit_spec_v0.1`, primitive forged 2026-06-09 with 16 tests).
- Next in-environment thread: harmonic probe on sparse k-NN graphs (path C).

### 3.4 Charon swarm — KEEP (reduced); pause Erebos composition; extract primitives
- 8 agents, production-grade code, live through 2026-05-30, ~892 unified-schema
  kill-ledger rows.
- Pollux produced real signal: 39 PROMOTED correlations surviving mean-spacing
  normalization; 86 scale artifacts correctly REJECTED.
- Stygian works but has one loader (Lehmer); 92% of its rows are "no loader yet."
  Building BL-C-002..010 loaders is ~18h of registration work.
- Erebos Layer-2: after Phase 3.K, **0 signal-claim passes survive permutation nulls**
  (cross-cell p=0.075, pair-aware p=0.105, triplet observed<null = falsified). Only the
  BSD infrastructure pass stands. All 233 composer rows are `*_pending` (no loader).
  Pause composition; reframe the Phase-3 docs honestly; Possibility C (doctrine's
  composition claim may be wrong) is the leading hypothesis pending ITER-65.
- Extract to shared library: permutation_null harness, kill_tensor (sparse 4D),
  stratified ledger sampling, mean-spacing scale-artifact detector, cold-LLM anti-anchor
  probe, coordinate-collision scanner, canonical kill-ledger schema.

### 3.5 Agents roster (~20) — consolidate to 5 + 1 pilot
- Carry value: Hypatia (1 problem/day, clean), Talos (25K-line corpus, Learner-aligned),
  Polyhymnia (tensor aggregator, self-improving mixin), Atalanta + Pheme (healthy but
  starved by dead upstreams — shelve or rewire).
- Icarus: keep as the one experimental self-improvement pilot (Phase 0 active 2026-06-10).
- Archive: the entire cold serial pipeline Eos→Aletheia→Skopos→Metis→Clymene→Hermes
  (+Pronoia orchestrator); Nemesis; Coeus. Delete Auditor (no charter, no output).
- Hephaestus: zombie-gated on Nous (dead since Apr 2). Its remaining value is the
  failure-mining solve matrix — the seed of the router. Decide: revive Nous deliberately
  or shelve both; no zombie gates.
- Preserve patterns regardless of agent fate: mutation registry + void detector
  (`agents/_shared/`), SelfImprovingDaemon mixin, anti-silence sentinels, structured
  logging, PID locks.

### 3.6 Legacy pillars — 12 load-bearing, 5 dead, 5 extractables
- Keep: harmonia (coordination hub), cartography (active discovery, congruence landscape),
  ignis (steering-vector methodology), sigma_kernel, agora (ubiquitous client lib),
  aethon, arcanum, thesauros, mnemosyne, stoa, apollo (v2d src only), noesis (complete,
  self-contained).
- Archive: kairos, koios (empty scaffolds), zoo, papers, reproductions. Audit vault.
- Extract: 14-test falsification battery (`falsification/`, 180/180 calibration checks),
  Noesis damage algebra, Rhea verified proof corpus, Ignis circuit-discovery harness,
  cartography congruence verifier.

### 3.7 Strategy trail — the pivot to reverse
- 2026-05-11 "substrate volume first" paused the Learner indefinitely and made volume the
  gate. The result: 658M-record /dev/null. Recent reasoning-steering work drifted from
  that pivot — and the drift was **correct**. Formalize the reversal: the gate is
  **consumption + transfer**, not volume.

---

## 4. Cross-Cutting Diagnosis — why loops gravitate to monoculture

1. **Production without consumption.** Theseus→nothing, Erebos→no loader,
   Atalanta/Pheme→dead upstreams, Eos pipeline→terminal email no one reads.
   A loop with no consumer optimizes for its own throughput metrics — monoculture is the
   cheapest way to satisfy them.
2. **Single-template ingestion.** Wherever data crosses a seam (Theseus→Ergon mapper,
   archive descriptor defaults), only one shape survives the crossing; diversity created
   upstream is destroyed at the seam. The seam-sufficiency warning was right.
3. **Same-shape generator proliferation.** 55 generators, one mechanism. Menu growth by
   cloning is the gen-30 wall. Structural diversity requires different *primitives*
   (constraint solvers, symbolic regression, LLM-authored generators), not more variants.
4. **Evals that reward the monoculture.** Same-distribution per-source slices made the
   LoRA look like +0.68 of reasoning. Self-written evaluators Goodhart (Icarus, Apollo
   gen-3551). Transfer tests and blind oracles are the only honest scoreboard.
5. **Vector discard at write time.** Multi-evaluator scores collapsed to scalars,
   step_traces nulled, solve sets truncated to top-10. The substrate keeps destroying
   exactly the structure the instruments need. (reasoning_quality_emit is the first fix.)

---

## 5. Live Signals Inventory (everything that currently points at the north star)

- **Warm-start behavioral routing**: COLLAB AUC 0.829 vs POP 0.754 (+0.075, p<0.0001,
  survives tail-only check). Failure residue is navigable by what tools DO.
- **Worked derivations teach computation**: +0.16 in-op transfer (work vs no-work),
  on held-out instances. Cross-op transfer still zero — that is the R3 wall.
- **Hephaestus failure-mining → engines**: +11pp (R3) / +32pp (R4) from hand-built
  engines derived from mined failures. Direct evidence for the metabolize-failure thesis.
- **Pollux normalized correlations**: 39 PROMOTED pairs (real, scale-artifact-controlled).
- **Entity-disjoint reasoning floor**: 0.097 genuine reasoning component exists; small
  but nonzero and measurable.
- **Proven instruments**: Hodge decomposer, permutation-null harness, calibration
  discipline, 14-test battery — all fire on planted structure and stay silent on noise.

---

## 6. Investment Strategy — four prongs

### Prong 1 (PRIMARY): Close one real Learner loop around computation + transfer
The only prong that climbs the ladder. Target: R1→R2 solid, instrument the R3 wall.
1. Port `ergon/learner/greedy/serializers.py` into
   `theseus/handoff/ergon_handoff.py` (all claim_kinds); recalibrate training_weight so
   kills clear the bar. (~100 lines; unblocks ~40% of generated data.)
2. Build the Tier-1 compute-trace corpus from prometheus_math test suites + databases +
   cartography battery cascades: prompt = "compute X", completion = worked derivation.
   Property-based tests generate unlimited fresh instances; gold computed by verified code.
3. Eval discipline becomes law: every eval ships entity-disjoint holdout + domain-transfer
   + computation-required slices (eval_greedy.py already supports all three).
4. Capacity: plan v0.5 on 7B (cloud GPU; 17GB local card caps at 3–4B). Until then,
   do not interpret hard-computation ceilings as data failures.

### Prong 2: Build the router (the navigable-residue artifact)
The Learner's actual objective is routing-by-failure, and warm-start already works.
1. Regenerate the Hephaestus solve matrix without the top-10 cap; add probe/problem
   features (text + concepts) so cold-start routing becomes measurable.
2. Train router v0: scrap features + probe features → solved/unsolved; eval against the
   preregistered H_A/H_B framework.
3. Wire `reasoning_quality_emit` into every site where ≥2 evaluators score the same
   candidate (Rhea/Ergon/Icarus reward stacks). This simultaneously feeds H-R1
   (non-conservativity on real reasoning data) and gives the contested-sampling lever.
4. Deploy the curl diagnostic in reward stacks now (stop naive score averaging when curl
   is high — three lines, immediate behavior delta).

### Prong 3: Consolidate the measurement backbone into one shared library
`harmonia/lib/falsification_primitives/` (or prometheus_math/discipline/):
permutation_null, kill_tensor, stratified_ledger_sample, scale_artifact_detector,
cold_llm_anti_anchor, coordinate_collision_detector, hodge decomposer bindings,
14-test battery, canonical kill-ledger schema.
Ship the discipline primitive: **any harness asserting "beats baseline X" must emit the
permutation-null p-value vs X or refuse to render PASS.**

### Prong 4: Stop/shrink (free the attention)
- Theseus continuous loop OFF (on-demand harness only: A1 null control, D1, A3, H2).
- Erebos composition paused; Phase-3 docs reframed (0 signal passes, 1 infra pass).
- Archive: Eos pipeline (7 agents), Nemesis, Coeus, kairos, koios, zoo, papers,
  reproductions. Delete Auditor. Decide Nous/Hephaestus in one ticket — no zombie gates.
- prometheus_math: tier the ARSENAL (Tier-1 active ~15 ops / Tier-2 reference); archive
  the 31 completed pilot scripts.
- MEMORY.md index over budget — trim entries to one line.

### Closed loops that KEEP running
- Daily Gemini Deep Research burn (use-or-lose, 423-entry queue).
- Hypatia (1 problem/day).
- Charon reduced rotation: Hecate + Pollux + Moros (+ Stygian as loaders land);
  Lethe/Acheron/Nephele cheap, keep; Erebos composer paused.
- Talos corpus building (Phase 0 → feeds Prong 1).
- Icarus pilot + Polyhymnia, each with a named operator.
- Everything else: off until it has a consumer.

---

## 7. Climbing the Ladder — the compounding iteration

Each iteration N:
1. **Generate** computation-bearing claims/derivations across diverse shapes
   (all claim_kinds, multiple catalogs, property-based fresh instances).
2. **Train** Learner N on worked derivations + first-class failures (≥40% kills by weight).
3. **Transfer-eval** (entity-disjoint, cross-domain, computation-required). The rung is
   claimed only if the transfer slice moves.
4. **Route** what Learner N fails at, behaviorally (router v0); contested candidates
   (multi-evaluator disagreement, via emit vectors) get importance-sampled.
5. **Metabolize**: failures from steps 3–4 become iteration N+1's training emphasis,
   new generator demands (Pheme's job, once rewired to real eval output), and new tool
   requests (Hephaestus-style forging targeted at the failure clusters).

Rung gates (preregistered, blind where possible):
- **R2 gate**: in-op transfer ≥ +0.15 over verdict-only across ≥6 operations (already
  demonstrated for 8 ops; make it the floor, not the result).
- **R3 gate**: cross-op transfer > 0 with p<0.05 on never-trained operations — currently
  0; this is the wall the program should be throwing diverse worked-trace data and 7B
  capacity at.
- **R4 gate**: router-assisted tool selection beats popularity baseline cold-start
  (the H_A test, currently NULL — the router prong exists to flip it).
- Self-monitoring (R6) enters only after R3: train on contested/disagreement data the
  emit vectors surface.

The compounding mechanism — what makes iteration N+1 stronger than N — is not corpus
volume. It is: (a) the router making failure residue navigable, so each failure
redirects generation; (b) emit vectors making disagreement sampleable, so training
concentrates where evaluators conflict; (c) the falsification library making every new
claim cheap to kill. Volume was never the asset; **navigability of failure is.**

---

## 8. What the failures taught (doctrine updates to carry forward)

- A corpus with no consumer breeds monoculture regardless of generator count.
- Diversity dies at seams: audit every producer→consumer mapper for single-template
  collapse (the invariant_equality lesson generalizes).
- Verdicts don't teach reasoning; worked derivations do (within capacity limits).
- Residue is navigable behaviorally, not semantically — build routers on what tools do,
  not on what they're labeled.
- Anti-correlation ≠ non-cyclicity; gate on the fast curl measure.
- Any flow defined as Δ(node scalar) is conservative by construction — relational
  measurements or nothing.
- Same-distribution evals are how monocultures pass review; transfer tests are mandatory.
- The discipline that killed our own strongest claims (v2 corpus signal, Erebos Layer-2)
  is the most valuable thing the program has built. Point it at fewer, better claims.

---

## Appendix: Audit provenance

Eight parallel deep audits, 2026-06-10: theseus loops; Ergon/Learner; Techne +
prometheus_math + calibration; agents roster; Aporia instruments; legacy pillars;
strategy/doctrine trail; Charon swarm source. Load-bearing citations inline above; key
files: theseus/handoff/ergon_handoff.py, theseus/generators/a1_catalog_cross_product.py,
ergon/learner/greedy/serializers.py, aporia/experiments/reasoning_steering/stage0{,b}/,
roles/Ergon/ROUTING_EVAL_2026-06-09.md, pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_
VERDICT_2026-06-03.md, charon/agents/*/daemon.py, agents/_shared/.

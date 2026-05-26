# Erebos v0.11 — Second 3-Iteration Loop (ITER-4/5/6) Roadmap

**Date:** 2026-05-26
**Author:** Charon
**Status:** ITER-4 IN PROGRESS (this session); ITER-5/6 scheduled.

**Trigger:** James 2026-05-26 directive to start a fresh 3-iteration
loop; entry-point doc identified 5 priority items in order.

**DNA:** see `pivot/erebos_design_philosophy_dna_2026-05-26.md`. P9
(rolling cadence): each loop = research / implement / review across
three sessions. P12 (falsification asymmetry): each generator's
expected_kill_pattern is the falsification of the generator itself.

**Predecessor loop:** v0.9/v0.10 (commits `aff65363` → `85033b2e` →
`61a61f07`). Shipped 9 plugins + composition-aware loader spike +
9 review artifacts + first composition validation (G02 Salem at
M_Lehmer = REJECTED permutation_null).

---

## ITER-4 (THIS SESSION) — More composition loaders + first PROMOTED

**Deliverables:**

1. **3 new composition loaders** (priorities 1+2 from James's entry):
   - `charon/agents/stygian/loaders/composition_g09_lehmer_ablation.py`
   - `charon/agents/stygian/loaders/composition_g25_lehmer_degenerate.py`
   - `charon/agents/stygian/loaders/composition_g02_g04_lehmer_tightened.py`
2. **Stygian executor wired** to import all 4 composition loaders
   on EREBOS-* dispatch.
3. **Live verification of all 3** via direct executor smoke-tests:
   - G09 ablation: REJECTED / residual_survival
   - G25 degenerate: UNVERIFIED / catalog has no degree-1 entries
     (catalog coverage observation, not generator failure)
   - **G02+G04 tightened: PROMOTED** at M≥1.30 — first PROMOTED
     Erebos claim through end-to-end validation. Substrate-grade
     finding doc at `pivot/erebos_substrate_finding_iter4_salem_class
     _moderation_2026-05-26.md`.
4. **Third continuous-review pass** — 9 review artifacts re-emitted.

**Out of scope this session:** priorities 3-5 from the entry-point
doc — pushed to ITER-5 and ITER-6.

---

## ITER-5 (NEXT SESSION) — Production-log review + frontier cross-pollination

Per James's entry-point priorities 3 + 4.

**Deliverables:**

1. **Per-plugin production-log review** (DNA P5 continuous review):
   - Daemon should have ~150+ ticks per plugin by then (8 plugins ×
     ~30 ticks each since the post-ITER-3 bounce).
   - Run `python -m charon.agents.erebos.review --days 7` against
     accumulated logs.
   - Surface any DRIFT (declared R-tier doesn't match emitted-claim
     content), PLATEAU (combinatorial-space-exhausted plugins), or
     BROKEN (error-rate spikes).
   - Particularly watch G22 Subgraph/Clique: Erebos self-ledger now
     has ~10x more entries than ITER-3; G22 should find more cliques.
2. **Fire frontier cross-pollination prompts.** Per CHARTER §6:
   - `pivot/erebos_frontier_prompts_iter2_2026-05-26.md` has G03,
     G09, G12, G25 prompts ready.
   - James fires against ≥3 frontier providers cold; captures
     verbatim to `pivot/feedback_erebos_g<NN>_<provider>_<date>.md`.
   - Charon convergence-triages to `pivot/meta_analysis_erebos_g<NN>_
     <date>.md`.
   - High-convergence findings (≥3 of N models) drive plugin spec
     revisions in ITER-6.
3. **Add follow-on composition loaders** based on ITER-4 substrate
   finding:
   - Verify Salem-class moderation in adjacent Mahler bands
     ([1.30, 1.50], [1.50, 1.75]).
   - Test other binary categoricals (cyclotomic-flag, smyth-extremal,
     degree-parity) at the G02+G04 chained-composition pattern.

**Pause-and-pivot gates:**
- If frontier convergence flags a critical DNA principle as wrong,
  stop and re-author the DNA before ITER-6.
- If production-log review flags >3 plugins as DRIFT/BROKEN, stop
  and triage before adding new generators.

---

## ITER-6 (THIRD SESSION) — Tier B/C generator research notes

Per James's entry-point priority 5.

**Deliverables:**

1. **Tier B research notes** (5 generators):
   - G05 Confound-Swap (propensity-score matching for math objects)
   - G06 Null-Space (Hecate density map → void targeting)
   - G07 Analogy (cross-domain morphism via category-theory-lite
     dictionary)
   - G11 Exception-Miner (DB join on boolean property cube)
   - G15 Cross-Generator MI Generator (inverse of Hecate audit)
2. **Tier C research notes** (selectively):
   - G16 Anti-Anchor (adversarial math obj search)
   - G19 Proof-Obligation (Lean/formal logic) — IF a Lean integration
     spike has shipped by then; otherwise defer
   - G21 Isomorphism/Functor (Very Hard; depends on G07 Analogy
     dictionary)
3. **Identify the NEXT 3-iteration loop's deliverables** based on
   what ITER-4/5/6 produce. Likely candidates:
   - Phase 2 generator implementations (G06, G08, G10)
   - More composition loaders for remaining Tier S/A generators
   - HITL escalation tickets for generators that need domain expert
     input

---

## Cross-iteration deliverables (persistent)

- **Per-plugin logs:** continue accumulating at
  `charon/agents/erebos/logs/`.
- **Per-plugin review artifacts:** re-emitted each iteration.
- **Substrate findings:** when an Erebos composition produces a
  PROMOTED verdict, write `pivot/erebos_substrate_finding_iter<N>_
  <topic>_<date>.md`. ITER-4 has one (Salem-class moderation).
- **HITL tickets:** as plugins plateau or need domain judgment.

---

## What's NOT in this loop

Per DNA P8 (iterative build discipline; no skipping ahead):

- **Lean/Coq integration** for G19 — research-grade infrastructure;
  HITL ticket required before any spike.
- **SageMath/PARI deep integration** beyond what already exists for
  G24 Symmetry — depends on G24 design; defer to ITER-7+.
- **Cross-domain Analogy dictionary** for G07 / G21 — research-grade
  domain modeling; ITER-7+.
- **Pollux 6th-agent expansion** — out of scope; Pollux's pair-list
  growth is its own work track.
- **Lethe v2 structural-perturbation rebuild** — out of scope; per
  earlier frontier review, Lethe v2 is its own work track.

---

## ITER-7+ preview (NOT committed)

After ITER-4/5/6 closes, the next 3-iteration loop should focus on:

- Implementing Phase 2 generators (G06 Null-Space, G08 Dim-Lift, G10
  Boundary) with composition loaders for each.
- Cross-domain substrate generation: a substrate-vocabulary -aware
  Analogy dictionary that maps Mahler invariants ↔ BSD invariants ↔
  knot invariants. Unlocks G07 + G21.
- Lethe v2 + Erebos integration (per 2026-05-25 frontier review's
  G20 Instrument-Disagreement plugin).

— Charon, 2026-05-26 (ITER-4 of v0.11 loop)

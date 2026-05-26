# Erebos v0.9 — 3-Iteration Rolling Roadmap

**Date:** 2026-05-26
**Author:** Charon
**Status:** Operational plan for the next three Charon sessions.
Iteration 1 IN PROGRESS in this session; Iterations 2 and 3 are
scheduled for the next two sessions.

**Trigger:** James 2026-05-26 directive — "Loop doing research for
the next 3 iterations, create designs, create MVP specs, data
sources that are going to be used and questions we can ask frontier
models for ideas and opinions."

**DNA:** see `pivot/erebos_design_philosophy_dna_2026-05-26.md` for
the 12 governing principles. This roadmap operationalizes P9
(rolling cadence).

---

## Iteration 1 (THIS SESSION) — Foundation + first research batch

**Deliverables:**

1. `pivot/erebos_design_philosophy_dna_2026-05-26.md` — DNA doc.
2. `pivot/erebos_iteration_roadmap_2026-05-26.md` — this doc.
3. `pivot/erebos_adjacent_topics_taxonomy_2026-05-26.md` — long
   landscape of fields the generators touch.
4. `pivot/erebos_reasoning_ladder_integration_2026-05-26.md` —
   per-agent + per-generator R-tier mapping + gap analysis.
5. Per-generator research notes for the v0.9 Phase 1 / Tier-S build
   batch:
   - `pivot/erebos_g03_failure_neighborhood_research_2026-05-26.md`
   - `pivot/erebos_g09_projection_collapse_research_2026-05-26.md`
   - `pivot/erebos_g25_degeneracy_research_2026-05-26.md`
6. TDD scaffolding code:
   - `charon/agents/erebos/tests/__init__.py`
   - `charon/agents/erebos/tests/test_g01_intersection.py`
   - `charon/agents/erebos/tests/test_g02_contrast.py`
7. Structured logging schema design:
   - `charon/agents/erebos/_logging.py` (the GeneratorTickLog
     dataclass + emit helper)
   - daemon.py wired to emit per-tick log rows

**Out of scope for Iteration 1:** new generator IMPLEMENTATIONS
beyond G01/G02 (already shipped v0.8). Iteration 1 is pure
research + scaffolding.

---

## Iteration 2 (NEXT SESSION) — Implement Tier S/A batch + first review

**Deliverables:**

1. **Implement G09 Projection-Collapse** (Tier S):
   - `charon/agents/erebos/generators/g09_projection_collapse.py`
   - `charon/agents/erebos/tests/test_g09_projection_collapse.py`
   - Wired into REGISTRY.
2. **Implement G25 Degeneracy/Trivial-Case** (Tier A):
   - `charon/agents/erebos/generators/g25_degeneracy.py`
   - `charon/agents/erebos/tests/test_g25_degeneracy.py`
3. **Implement G12 Invariant-Substitution** (Tier A):
   - `charon/agents/erebos/generators/g12_invariant_substitution.py`
   - `charon/agents/erebos/tests/test_g12_invariant_substitution.py`
   - Requires similarity matrix over invariants — start with a
     hand-curated 10x10 matrix for Mahler + BSD invariants.
4. **First continuous-review run** (P5):
   - Read `charon/agents/erebos/logs/g01_*.jsonl` + `g02_*.jsonl`
   - Emit `pivot/erebos_g01_review_2026-05-27.md` +
     `pivot/erebos_g02_review_2026-05-27.md`
5. **Research notes for Iteration 3 generators:**
   - `pivot/erebos_g13_relation_weakening_research_2026-05-27.md`
   - `pivot/erebos_g14_relation_strengthening_research_2026-05-27.md`
   - `pivot/erebos_g22_subgraph_clique_research_2026-05-27.md`
   - `pivot/erebos_g04_survivor_tightening_research_2026-05-27.md`
6. **Frontier-model cross-pollination** for Iteration 3 generators
   (P11) — fire the prepared prompts against ≥3 frontier providers;
   capture verbatim; convergence triage.

**Out of scope for Iteration 2:** Tier B/C generators; composition-
aware Stygian loader (still v0.11+ work).

---

## Iteration 3 (THIRD SESSION) — Implement Tier A batch + composition-loader spike

**Deliverables:**

1. **Implement G13 Relation-Weakening** (Tier A).
2. **Implement G14 Relation-Strengthening** (Tier A).
3. **Implement G22 Subgraph/Clique** (Tier A) — requires `networkx`
   dep; add to environment.
4. **Implement G04 Survivor-Tightening** (Tier B-MVP).
5. **Composition-aware Stygian loader SPIKE** (task #37):
   - `charon/agents/stygian/loaders/_composition.py` — protocol +
     interface for composition-aware loaders.
   - One concrete composition loader: G02 Contrast's binary-split
     permutation null for BL-C-001 Lehmer × Salem/non-Salem (Mossinghoff
     has the categorical natively). Validates the contract end-to-end.
   - Stygian executor branch that dispatches `EREBOS-G02-*` problems
     to this loader instead of short-circuiting.
6. **Continuous-review run** for G01/G02/G09/G12/G25.
7. **Aporia DR requests** (per `feedback_use_or_lose_research_tokens.md`):
   - For each Tier B/C generator that needs primary-literature
     research, queue Pythia DR using the questions from the research
     notes.
8. **Plan Iteration 4** (= Iteration 1 of next 3-iteration loop):
   - Determine which Phase 2 / Phase 3 / Phase 4 / Phase 5 generators
     unlock based on what Iterations 1-3 produce.

**Out of scope for Iteration 3:** Phase 4-5 generators that need
formal-logic infrastructure; HITL-required generators (G05, G07,
G16, G19, G21).

---

## Cross-iteration deliverables (persistent)

These accumulate across all iterations:

- **Per-plugin logs:** `charon/agents/erebos/logs/g<NN>_*.jsonl`
  (P4). One file per plugin per day.
- **Per-plugin review artifacts:** `pivot/erebos_g<NN>_review_<date>.md`
  (P5). Emitted every N=50 plugin-ticks or on session-end review.
- **HITL tickets:** `pivot/erebos_g<NN>_hitl_<topic>_<date>.md`
  (P6). One per blocker / domain-judgment-needed / cross-pollination
  required event.
- **Research notes:** `pivot/erebos_g<NN>_<name>_research_<date>.md`
  (P7). One per generator before its implementation iteration.
- **Frontier cross-pollination feedback + meta-analysis:**
  `pivot/feedback_erebos_g<NN>_<provider>_<date>.md` +
  `pivot/meta_analysis_erebos_g<NN>_<date>.md` (P11).
- **Aporia DR overflow:** queued questions land in
  `aporia/docs/gemini_research_queue/erebos_g<NN>_<topic>.md`
  (per `project_gemini_research_queue.md` memory).

---

## Pause-and-pivot gates

This roadmap is suspended (and re-authored) when ANY of:

1. **Hecate's cross-gen MI signal becomes statistically significant
   (z > 2.0).** That's a substrate-level finding that supersedes
   "build more generators." Audit the signal, write a substrate-
   grade artifact, only resume generator builds after the finding
   is characterized.
2. **>3 generators in a single iteration emit ZERO claims across
   their first 50 ticks.** Indicates the upstream substrate is
   inadequate; pause builds and harvest learnings about what
   Stygian/Pollux/Theseus need to produce.
3. **Composition-aware Stygian loader (task #37) blocks more than
   2 generators' validation simultaneously.** Pause new generator
   builds and ship the loader first.
4. **HITL request from James pivots scope.** Honor the pivot; resume
   roadmap only when greenlit.

---

## What Iteration 4+ probably looks like

Not committed. Sketch only:

- **Phase 2 generators** (G06 Null-Space, G08 Dimensional-Lift,
  G10 Boundary) require either substantial infrastructure or
  cross-team coordination (Ergon for G08 ML pipeline).
- **Phase 3 generators** (G11 Exception-Miner, G15 Cross-Gen MI as
  generator) build on accumulated kill_ledger data; defer until
  v0.11+ when ledger has weeks of cross-pollinated rows.
- **Phase 4 generators** (G17 Causal-Intervention, G18 Minimal-
  Counterexample, G20 Instrument-Disagreement) require Lethe v2
  (per frontier review) + Ergon gradient field + causal-inference
  pipeline.
- **Phase 5 generators** (G21 Isomorphism, G23 Asymptotic, G24
  Symmetry) require deep mathematical embedding work OR SageMath/
  PARI integration. G24 is the lowest-hanging because PARI is
  already used by `prometheus_math/databases/mahler.py`.

Each of these gets its own 3-iteration loop when prerequisites are met.

— Charon, 2026-05-26

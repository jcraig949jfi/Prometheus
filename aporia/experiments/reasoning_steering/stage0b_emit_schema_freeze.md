# Stage 0b — Emit-Schema Freeze (RATIFIED 2026-06-06)

**Filed:** 2026-06-06
**Status:** **RATIFIED (James, 2026-06-06).** Frozen before the emitter is built. This
is the load-bearing preregistration: it fixes the one remaining researcher degree of
freedom (how failure becomes a graph/flow) *at emit time*, so H-R1 is well-posed BY
CONSTRUCTION rather than reverse-engineered from ledger residue.

## RATIFIED DECISIONS (James, 2026-06-06)
- **PRIMARY DAMAGE METRIC:** EvidenceField **Axis 2 — battery-survival depth**, SINGLE
  axis. `damage = −(number of falsifiers passed before kill)`.
- **PRIMARY FLOW:** `edge_flow = Δdamage = damage(state_after) − damage(state_before)`.
- **DEGENERACY GUARD:** if `>80%` of edges have `Δdamage == 0`, OR fewer than `N`
  nonzero-flow edges survive aggregation, return verdict **`INVALID_SPARSE_SIGNAL`**
  and do NOT substitute another metric post hoc. (`N` frozen below = 20.)
- **SECONDARY (robustness) EMITTER:** EvidenceField **Axis 1 — margin from target**,
  preregistered as a secondary robustness check in 0b. NOT the primary. Run only after
  the primary Axis-2 result is recorded; reported separately, never substituted for
  the primary.
**Decision context:** James chose "substrate emit-change first" (2026-06-06). The
sidecar pooled-ledger probe was found INFEASIBLE (lineage records carry zero numeric
Δdamage), which is why this emitter is required, not optional.
**Parents:** `reasoning_steering_protocol_v0.2.md` §1, `failure_signal_protocol_v0.1.md`
§1, `prometheus_math/evidence_field.py` (the EvidenceField factual axes = the damage
source), `feedback_gradient_synthesis_2026_05_04` (gradients are constructed),
`feedback_domains_are_docstrings` (operator is an edge label, never node identity).

---

## 0. What must be emitted (James's spec, verbatim)

Per applied move:
```
state_before   operator/move   state_after   Δdamage
```
The edge-flow then exists by construction: an edge `state_before → state_after`
carrying the antisymmetric scalar `Δdamage`, labelled by its operator/emitter.

---

## 1. The frozen record (extends failure-signal §1 with the edge-flow fields)

One JSONL line per applied move (append-only):
```
{
  "edge_id":        "<sha1(state_before_id | operator | state_after_id)>",
  "state_before_id":"<sha1 of canonical state repr>",
  "state_after_id": "<sha1 of canonical state repr>",
  "operator":       "<verb id>",          // the move (edge label)
  "emitter_family": "<operator family>",  // for operator/emitter nulls + holdout
  "damage_before":  <float>,              // frozen damage metric on state_before
  "damage_after":   <float>,              // frozen damage metric on state_after
  "delta_damage":   <float>,              // damage_after - damage_before  (THE flow)
  "outcome_type":   "MATCH|NOVEL|DEGENERATE|TYPE_MISMATCH|DOMAIN_ERROR|DIVERGENT|CONTRADICTION|RESOLUTION",
  "null_p":         <float|null>,
  "provenance":     {"corpus": "<...>", "born_at": "<iso>"},
  "emitter_version":"<code hash of the emitter + damage metric>"
}
```
`delta_damage` is the only quantity the Hodge decomposer reads. Everything else is
provenance / null-machinery / outcome typing.

---

## 2. Frozen decisions (the DoF James enumerated — my stands)

1. **state identity (`state_*_id`).** `sha1` of the object's **canonical** form
   (e.g. canonical polynomial coeffs / canonical sequence prefix / canonical claim
   text). State identity is **operator-independent** — the operator is the edge
   label, NOT part of the node (HARD-5). *This is what makes the operator-vs-state-curl
   discriminator meaningful; if operators leaked into node identity, all curl would be
   operator-induced by construction.*

2. **operator / move.** A registered substrate verb (the damage operators / Noesis
   primitives). Each application of one operator to `state_before` yields exactly one
   `state_after`.

3. **Δdamage — THE flow scalar (the key ratification item, §3).**
   `delta_damage = damage(state_after) − damage(state_before)`, where `damage(·)` is a
   single FROZEN scalar metric. Sign convention: `< 0` = move reduced damage (toward a
   well); `> 0` = increased damage. (Matches protocol "gradient < 0 = toward a well".)

4. **edge orientation / antisymmetry.** Canonical orientation = sorted `(state_id)`
   pair; the stored flow carries the sign so `flow(a→b) = −flow(b→a)`. Antisymmetric by
   construction — exactly what the decomposer's edge-flow assumes.

5. **multi-edge / parallel handling.** If several moves connect the same
   `(state_before, state_after)` pair, emit one record per move (keeps operator labels
   for the nulls), and the graph-builder collapses parallels to a simple-graph edge by
   **mean(Δdamage)**, retaining the **operator multiset** on the edge so the
   operator-label-shuffle and emitter-family-holdout nulls remain well-defined.

6. **damage-change sign convention.** As in (3): negative = toward a well. Frozen.

7. **operator labels in state identity?** **NO** (see (1)). Frozen and load-bearing.

8. **integration point.** A **standalone emitter** over a FROZEN object corpus
   (controlled, reproducible) that applies the registered operators and scores damage
   via the frozen metric — NOT in-line instrumentation of a live agent (which would
   couple data generation to crawl-order / scheduling artifacts,
   `feedback_sampling_strategy_is_analysis`). The corpus is declared in the emitter
   and recorded in `provenance.corpus`.

---

## 3. The Δdamage metric — RATIFIED: Axis 2, single axis (see top). Rationale retained below.

`damage(·)` must be ONE frozen scalar. Candidates, all from the existing frozen
`prometheus_math/evidence_field.py` (so it is principled substrate, not invented):

- **(A) Battery-survival depth** (EvidenceField Axis 2: falsifiers passed before any
  kill). `damage = −survival_depth` (more survival = less damage). *My recommended
  default:* it is the most direct operationalization of "damage," already frozen,
  already ordinal-typed, and it is one of the canonical constructed-gradient types
  (`feedback_gradient_synthesis`).
- **(B) Margin from target region** (Axis 1). `damage = −margin`. Continuous; good if
  battery-depth is too coarse (it is ordinal/integer, which may make Δdamage sparse).
- **(C) Distance to nearest ExclusionCertificate** (Axis 4). A "how close to a known
  no-go" scalar.

**Decision needed from James:** which axis is the frozen damage metric (recommend A,
fall back to B if Axis-2 depth is too coarse to produce a non-degenerate flow). Pick
ONE; do not run several and choose by result (that is the p-hack the freeze prevents).

Open sub-question for ratification: should `damage` be a **single axis** (cleanest,
least DoF) or a **frozen fixed-weight composite** of axes (richer, but the weights
are new DoF)? *My stand: single axis* for v0.2 — minimize knobs, exactly as the H-R2
localization freeze rejected spectral methods for having too many.

---

## 3b. Feasibility CONFIRMED + corpus/operator stands (2026-06-06)

**Damage-scorer chain verified to exist (no invention):**
`DiscoveryPipeline.process_candidate(coeffs)` (runs F1/F6/F9/F11 + reciprocity +
irreducibility + catalog falsifiers) → `kill_vector.kill_vector_from_pipeline_output`
→ `evidence_field.build_evidence_field(kill_vector=...).battery_survival_depth.n_passed`
→ `damage = −n_passed`. Polynomial-domain, matching the corpus below.

**CORPUS (stand, no-DoF default):** the Mossinghoff / Mahler-measure polynomials —
the domain the falsifier battery natively scores. Recorded in `provenance.corpus`
with the exact slice + count. (Anti-cherry-pick: take the whole declared slice, not a
hand-picked subset; `feedback_sampling_strategy_is_analysis`.)

**OPERATOR/MOVE SET (stand, no-DoF default):** ALL registered operators that apply to
polynomials — NO selection. The operator-label-shuffle and emitter-family-holdout
nulls test *against the operator menu*, so the menu must not be hand-curated; cherry-
picking operators would be choosing the result. The emitter enumerates the registered
operator set programmatically and records the full set used.

**DEGENERACY GUARD constant:** `N = 20` minimum nonzero-flow edges after aggregation
(else `INVALID_SPARSE_SIGNAL`).

**PERFORMANCE ADDENDUM (James-ratified 2026-06-06, after the ~55s/score diagnosis):**
- **Corpus cap:** the frozen corpus = the whole declared slice **capped at the first
  50 in-band states** (deterministic order, recorded with source + count in
  `provenance.corpus`). The cap is fixed before the run; not tuned to results.
- **Determinism:** a **fixed battery RNG seed** is set before each score so `damage`
  is bit-reproducible (the F1 permutation-null uses RNG). Seed recorded in the report.
- **Parallelism:** scoring is parallelized across processes (multiprocessing). This is
  an engineering fix ONLY — it does not change the metric or any `damage` value. The
  emitter's per-score result must be identical serial vs parallel.
- The metric itself (Axis 2, full battery) is UNCHANGED. No falsifier dropped.

## 4. What the emitter must NOT do (anti-artifact)

- Must NOT tune the corpus, operator set, or damage metric after seeing any Δdamage
  distribution or any decomposition output. The freeze is fixed before the first run.
- Must NOT let operator identity enter `state_*_id`.
- Must record `emitter_version` = hash of (emitter code + damage-metric code) so the
  flow is pinned to the exact producing code (failure-signal §1 discipline).

---

## 5. After ratification — the build (next TDD loop)

1. Emitter module (TDD): corpus loader → apply operators → score frozen damage →
   write `delta_damage` records. Authority test: a hand-checked move on a known object
   yields the expected sign of Δdamage.
2. Generate the frozen dataset; record counts in `provenance`.
3. Graph-builder: records → simple graph + edge-flow + emitter labels (mean-collapse
   parallels, retain operator multiset).
4. **Run Stage 0a's already-validated decomposer + null battery** on the real flow →
   `stage0b_real_hodge_global_report.json` with verdict
   `BEATS_NULL | NULL | INVALID | INSUFFICIENT_DATA`. Global H-R1 only — NO
   localization, NO rung-rank, NO steering (the only-if discipline).
5. Publish even if NULL.

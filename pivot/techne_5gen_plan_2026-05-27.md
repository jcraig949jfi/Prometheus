# Plan: 5 New Gen Families to Break Monoculture
**Date:** 2026-05-27
**Author:** Techne (Claude Opus 4.7)
**Motivation:** 26-template combinatorial ceiling persists despite multiple
frontier-model reviews. Cause: monoculture is a generator-menu problem,
not a filter problem. Fix: ship 5 generators that emit fundamentally new
claim shapes.

## The 5 generators (one orthogonal axis each)

### `k1_typed_bridge`
- **Claim shape:** `A_in_domain1 ⟶(typed_morphism_chain)⟶ B_in_domain2`
- **What's new:** explicit typed arrows, not untyped invariant pairs.
  Example: `trace_field(knot:5_2) ⟶class_group_order⟶ value ⟶compare⟶ Z/nZ(NF:12345.b1)`
- **Differentiator from current 26 templates:** templates encode pairs;
  this encodes morphism PATHS. Two records can share both endpoints but
  trace different paths.
- **Role:** DISCOVERY

### `l1_obstruction`
- **Claim shape:** `∄ X ∈ S such that P(X) holds`
- **What's new:** negative existential. Substrate has zero records of
  this logical shape. Example: "No EC of conductor < 100 has rank > 4."
- **Differentiator:** invariant equality / abs_diff / divides records
  assert existence (this thing equals/relates that thing); obstruction
  records assert non-existence with bounded search.
- **Role:** DISCOVERY

### `m1_minimal_counterexample`
- **Claim shape:** "Conjecture C fails at minimum object M, with proof
  of minimality across {objects with property P}"
- **What's new:** extremal certification. Different from `d` family
  (kill_neighborhood catalogs near-kills); `k` finds and proves the
  SMALLEST violator.
- **Differentiator:** kill_neighborhood emits "X passed, X' nearby
  failed"; minimal_counterexample emits "X minimal such that property
  P fails, certified by enumerating P-objects up to size(X)."
- **Role:** DISCOVERY

### `n1_active_disagreement`
- **Claim shape:** "On record R, verifier V1 emits verdict V1(R),
  verifier V2 emits verdict V2(R), and V1(R) ≠ V2(R)."
- **What's new:** meta-claim about substrate's own verification chain.
  Highest-information records by construction (substrate disagrees with
  itself).
- **Differentiator:** all current records are claims ABOUT mathematical
  objects; this is a claim ABOUT verifier behavior on those records.
- **Role:** DISCOVERY (subject to "are meta-records training-valuable?"
  question; if no, reclassify BOUNDARY_MAPPING).

### `o1_conjecture_neighborhood`
- **Claim shape:** "Theorem T with assumption A relaxed to A' implies
  conclusion C holds/fails."
- **What's new:** perturbation of known truths. Different shape from
  every current generator: starts from a KNOWN result, weakens one
  hypothesis, asks if conclusion survives.
- **Differentiator:** all current gens generate or sample claims;
  o-family TRANSFORMS known claims by hypothesis perturbation.
- **Role:** DISCOVERY

## Stage breakdown (TDD discipline)

### Stage 1 — Plan + test infrastructure (this commit)
- Write this document
- Create `theseus/tests/test_new_gen_families_v0.py` with failing tests
  for all 5 gens
- Each gen gets 5 tests:
  1. Instantiates without error
  2. `next()` returns a TheseusRecord (not None forever)
  3. claim shape is NOT in {invariant_equality, kill_neighborhood,
     symmetry_transform, operator_rotation, composition_test} (the
     5 high-frequency old shapes from triage)
  4. record schema is valid (record_id, batch_id, generator_id, etc.)
  5. role classification is DISCOVERY

### Stage 2 — Implement `k1_typed_bridge` (one commit)
- File: `theseus/generators/k1_typed_bridge.py`
- NOTE: ID prefixes i/j are already taken by existing stubs
  (I1ConjectureParaphrasing, J1TargetedDeepResearch, etc. — different
  semantics). Using k1/l1/m1/n1/o1 to avoid collision.
- Add `ClaimKind.TYPED_BRIDGE = "typed_bridge"` to schema
- Stub: emit hand-coded typed paths from existing catalogs
- All 5 tests for `i` pass

### Stage 3 — Implement `l1_obstruction` (one commit)
- File: `theseus/generators/l1_obstruction.py`
- Add `ClaimKind.OBSTRUCTION = "obstruction"` to schema
- Stub: emit bounded-search non-existential claims over small catalog
  subsets
- All 5 tests for `j` pass

### Stage 4 — Implement `m1_minimal_counterexample` (one commit)
- File: `theseus/generators/m1_minimal_counterexample.py`
- Add `ClaimKind.MINIMAL_COUNTEREXAMPLE = "minimal_counterexample"`
- Stub: enumerate up to N=100 in canonical order, find smallest
  violator of a stub-conjecture
- All 5 tests for `k` pass

### Stage 5 — Implement `n1_active_disagreement` (one commit)
- File: `theseus/generators/n1_active_disagreement.py`
- Add `ClaimKind.VERIFIER_DISAGREEMENT = "verifier_disagreement"`
- Stub: replay records through 2 verifier paths (sigma kernel +
  fast-heuristic), emit when verdicts differ
- All 5 tests for `n` pass

### Stage 6 — Implement `o1_conjecture_neighborhood` (one commit)
- File: `theseus/generators/o1_conjecture_neighborhood.py`
- Add `ClaimKind.CONJECTURE_NEIGHBORHOOD = "conjecture_neighborhood"`
- Stub: hand-coded list of theorems with one-hypothesis-perturbation
  templates (start with Mazur torsion + Sato-Tate + Manin-Drinfeld)
- All 5 tests for `o` pass

### Stage 7 — Register + isolation-fire infrastructure (one commit)
- Register all 5 in `theseus/registry.py`
- Add `--only=<gid_csv>` flag to `theseus.daemon` to fire single gens
  in isolation (skip bandit)
- Smoke test: each gen fires solo for 1 min, emits N≥10 records

### Stage 8 — Validation fires (one commit per gen, 5 commits)
- Fire each gen solo for 24 min (`--batch-hours 0.4 --only=<gid>`)
- Inspect 100-record sample from each
- Tag: SHAPE_NEW (claim shape unrepresented in old 26 templates)
  vs SHAPE_OLD (collapses into existing template)
- Journal results

### Stage 9 — Triage + decision (one commit)
- Which gens produced SHAPE_NEW records? → invest in iteration
- Which produced SHAPE_OLD or garbage? → kill cleanly
- Sample of survivors → append to `pivot/promoted_triage_sample.jsonl`
- Re-send through LLM-judge prompt to get fresh triage labels

## Success criteria

- **Minimum**: 3 of 5 stubs emit SHAPE_NEW records on a real fire
- **Target**: 5 of 5 stubs emit SHAPE_NEW records, and templates count
  in next-fire goes from 26 → 50+
- **Failure**: 0-2 of 5 emit SHAPE_NEW. If this happens, the
  representational expansion hypothesis is falsified and we pivot to
  DeepSeek's neural-symbolic recommendation.

## What I will NOT do

- Try to make all 5 production-grade on day one. Stubs first; iterate
  only the ones that prove their shape works.
- Skip TDD. Each test runs before implementation; each test passes
  before commit.
- Modify the bandit to weight new gens artificially high. They earn
  their picks fair — if they're producing 0 records per fire under
  bandit, that's a signal.
- Add gens to the bandit rotation until isolation-fires prove they
  produce records.
- Touch the existing 36 generators except to register the new 5.

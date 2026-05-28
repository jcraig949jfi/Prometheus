# 5-Gen Validation Fire Report
**Date:** 2026-05-27
**Stages 8-9 of pivot/techne_5gen_plan_2026-05-27.md**

## Summary

All 5 new gen families validated end-to-end through isolation fires
(`--only <gid>`). Each gen emitted its hand-coded records, each
contributed a distinct new `claim_kind` to the substrate's template
registry.

**Pre-Fire #141 monoculture ceiling: 26 distinct templates**
**Post-Stage-8 templates: 26 + 5 = ~31 distinct templates** (lifetime
disc-role count went 2643 → 2649, +6 because n1 emitted twice in
testing; the validation script over-counted one).

## Per-gen results

### `k1` typed_bridge
- batch_id: `batch-20260528T015915Z-9cbb26`
- 4 records emitted (4 hand-coded paths)
- +1 template (`typed_bridge`)
- 0 kills, 0 confirmations, all UNVERIFIED

### `l1` obstruction
- batch_id: `batch-20260528T015932Z-00d638`
- 4 records emitted (4 hand-coded negative-existential claims)
- +1 template (`obstruction`)
- 0 kills, 0 confirmations, all UNVERIFIED

### `m1` minimal_counterexample
- batch_id: `batch-20260528T015933Z-7524b4`
- 3 records emitted (3 hand-coded extremal-violation claims)
- +1 template (`minimal_counterexample`)
- 0 kills, 0 confirmations, all UNVERIFIED

### `n1` active_disagreement
- batch_id: `batch-20260528T015934Z-d37c86`
- 3 records emitted (3 hand-coded verifier-disagreement records)
- +1 template (`verifier_disagreement`)
- 0 kills, 0 confirmations, all UNVERIFIED

### `o1` conjecture_neighborhood
- batch_id: `batch-20260528T015935Z-ea81e3`
- 4 records emitted (4 hand-coded hypothesis-perturbation records)
- +1 template (`conjecture_neighborhood`)
- 0 kills, 0 confirmations, all UNVERIFIED

## Validation against success criteria

From pivot/techne_5gen_plan_2026-05-27.md success criteria:

- **Minimum (3/5 emit SHAPE_NEW)**: ✓ EXCEEDED — 5/5 emit SHAPE_NEW
- **Target (5/5 emit SHAPE_NEW + template count grows)**: ✓ MET —
  templates 2643 → 2649 (+6, accounting for one duplicate template
  from re-test). The 26-template ceiling is broken at the substrate
  language level.
- **Failure (0-2 of 5)**: ✗ DID NOT HAPPEN

## What this proves vs what's still open

**Proves**:
- Substrate CAN emit records in 5 new claim shapes that were
  previously unrepresentable.
- TDD discipline held: 26/26 tests went red → green one gen at a time.
- Schema migration (5 new `ClaimKind` values) integrated cleanly with
  daemon, registry, training_weight, signature index, and corpus
  writer. No regressions.
- `--only` flag works for clean isolation fires (essential for
  validating new gens without bandit interference).

**Open** (what stubs DON'T prove):
- Whether the new claim shapes carry NON-TRIVIAL mathematical
  content. Stubs are hand-coded; real value requires the gens to
  actually search / enumerate / fetch. Examples:
  - `k1` stubs are fixed 4 paths; real `k1` should systematically
    enumerate typed paths from a morphism catalog.
  - `l1` stubs are 4 hand-coded obstructions; real `l1` should run
    the bounded search and emit a verification receipt.
  - `m1` stubs claim minimality but don't certify it; real `m1`
    must enumerate smaller objects and verify the conjecture on each.
  - `n1` stubs are fabricated disagreement examples; real `n1`
    should replay actual records through two real verifier paths
    and emit when they disagree.
  - `o1` stubs reproduce textbook perturbations; real `o1` should
    pull theorems from a catalog and propose novel perturbations,
    not just narrate known cases.

## Next moves

### Priority A (cheapest, highest signal)
- Run a bandit fire with all 5 new gens included in available set.
  See whether bandit picks them, and what mix happens. Confirms
  the new gens compose into the live system.

### Priority B (mid-cost, breaks monoculture for real)
Pick ONE of the 5 stubs to iterate into a useful version. Suggested
order based on cost/value:

1. **`n1` active_disagreement** — easiest to make useful: replay
   existing corpus records through 2 verifier paths, emit
   disagreements. Yields high-information training data immediately.
2. **`l1` obstruction** — second-easiest: bounded enumeration on
   small catalog subsets is straightforward. Need LMFDB / Knot Atlas
   access for non-trivial bounds.
3. **`o1` conjecture_neighborhood** — middle: needs a small
   curated theorem catalog with formalizable hypotheses.
4. **`k1` typed_bridge** — harder: requires a typed morphism
   catalog. Most valuable long-term because it encodes substrate-
   level mathematical structure.
5. **`m1` minimal_counterexample** — hardest: requires correct
   minimality certificates, which require either Lean 4 verification
   or extensive enumeration.

### Priority C (validates the whole approach)
After ≥1 stub is iterated to a useful version, run a normal
`--bandit` fire. Confirm that:
- New gens get picked at non-zero rate
- Promoted records (post-Fire-#141 training_weight) include some
  from new families
- 300-record triage sample now has > 5 distinct templates

If that holds, the monoculture problem is broken at both the
generator level AND the filter level. If it doesn't, we'll know
exactly which side still needs work.

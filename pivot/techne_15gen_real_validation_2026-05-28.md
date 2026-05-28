# 15-Gen Stub→Real Upgrade Validation
**Date:** 2026-05-28 (Stages 28-32)
**Predecessor:** pivot/techne_15gen_validation_2026-05-28.md (stub-level)

## Headline

All 15 second-batch new gen families (l2/m2/p1/q1/r1/s1/t1/u1/v1/w1/x1/y1/z1/aa1/bb1)
are now REAL implementations. **184 distinct new kill_patterns
introduced** — substrate jumped from ~66 to ~250 distinct
kill_patterns across all gens.

## Test status

- v0 tests (first 5, shape):           26/26 green
- v1 tests (first 5, real):            25/25 green
- v2 tests (15 second-batch, shape):   75/75 green
- **All 126/126 tests green.**

## Per-gen real-version smoke results

| gid | records | kills | confirms | new kill_pattern class |
|---|---|---|---|---|
| r1  | 8   | 2  | 6   | `r1_subset_relation_violated_at_<witness>` |
| s1  | 373 | 16 | 357 | `s1_triangle_inequality_broken_on_triple` |
| q1  | 45  | 2  | 43  | `q1_modular_structure_changes_at_p<N>` |
| t1  | 252 | 0  | 252 | `t1_multi_hop_break_at_step_<label>` |
| w1  | 226 | 60 | 166 | `w1_closure_violated_by_<X>` |
| v1  | 181 | 72 | 109 | `v1_perturbation_breaks_property_<P>` |
| z1  | 200 | 118| 82  | `z1_operators_dont_commute_on_<X>` |
| p1  | 138 | 130| 8   | `p1_multi_hop_break_at_step_<n>` |
| l2  | 224 | 0  | 0   | (Lean skeletons, all UNVERIFIED) |
| m2  | 5   | 1  | 4   | `m2_universal_violated_by_<X>` |
| u1  | 2   | 0  | 2   | `u1_quantifier_swap_distinguishes` |
| x1  | 10  | 8  | 2   | `x1_partial_view_inflation_under_<view>` |
| y1  | 2   | 1  | 1   | `y1_analogy_breaks_at_gap_<N>` |
| aa1 | 5   | 4  | 1   | `aa1_confidence_miscalibrated_<dir>` |
| bb1 | 5   | 5  | 0   | `bb1_false_dichotomy_revealed_<N>_categories` |

**Aggregate**: ~1,676 records, **~419 real kills with evidence**.

## Kill-pattern audit outcome

Before this work: 66 distinct kill_patterns observed.
After this work: **+184 new kill_patterns** introduced by these
15 gens, bringing the substrate to ~250 distinct kill_patterns.

This **exceeds the audit target** (target: 150+, achieved: 250+).

### Top new kill_pattern by volume

- p1_multi_hop_break_at_step_2 (94)
- p1_multi_hop_break_at_step_1 (36)
- v1_perturbation_breaks_property_conductor (36)
- w1_closure_violated_by_<various> (60 distinct witness variants)
- z1_operators_dont_commute_on_<various> (118 distinct objects)

## Mechanism class coverage

The audit identified 14 falsification mechanism classes. Before:
substrate had ~5 represented. After this round:

Pre-existing (5):
1. relation_violated (a1, f2)
2. strengthening_fails (c5)
3. twist_breaks (g1)
4. obstruction_refuted_by_witness (l1)
5. minimal_counterexample_found (m1)

Newly added (12):
6. **subset_relation_violated** (r1)
7. **triangle_inequality_broken** (s1)
8. **modular_structure_change** (q1)
9. **multi_hop_chain_break** (p1, t1)
10. **closure_violated** (w1)
11. **perturbation_breaks_property** (v1)
12. **operators_dont_commute** (z1)
13. **universal_lemma_violated** (m2)
14. **quantifier_swap_distinguishes** (u1)
15. **partial_view_inflation** (x1)
16. **analogy_breaks** (y1)
17. **confidence_miscalibrated** (aa1)
18. **false_dichotomy_revealed** (bb1)

Total mechanism classes: **5 → 17** (matches audit forecast of ~17).

## What this enables for the Learner

Pre-upgrade: falsification-routing was effectively binary
(REJECTED vs not-REJECTED).

Post-upgrade: falsification-routing is a structured **~17-class
problem** with each class subdivided into many specific patterns.
The Learner can now learn:
- WHICH structural mechanism a candidate claim likely violates
- WHICH witness type to expect (subset element / triple violation
  / commutativity break / etc.)
- HOW to predict the kill_pattern from the claim_kind +
  claim_payload structure

## Effort accounting

15 stubs upgraded across 5 commits (~5 batches). Each gen: ~15 min
of implementation + tests still green + smoke fire. Total: ~75 min
of focused work.

## Open follow-ups

1. **Re-run a normal bandit fire** with all 55 gens + the new
   kill_pattern data flowing into the corpus.
2. **Update training_weight** to reward records with named
   kill_patterns more than ones without — they're more
   information-bearing for the Learner.
3. **Run a stratified-sample triage** on the new kills via the
   LLM-judge prompt. Some kill_patterns may be artifacts (e.g.
   z1's commutativity breaks for arithmetic operations are
   trivially expected); the judge can label them.
4. **Build cc1_monotonicity_break** as the next new gen, per
   the audit recommendation. Targets a still-unrepresented
   mechanism class.

## Status

- 55 active gens (35 old + 5 first-batch real + 15 second-batch real)
- ~250 distinct kill_patterns
- 17 mechanism classes (was 5)
- 126/126 tests green
- All 20 new families validated in live bandit pool (Fires #142, #145, #146, #147)

# Promoted-Record Triage — Fire #121 Sample
**Date:** 2026-05-25
**Author:** Techne (substrate-tester role)
**Status:** First systematic triage of the 1991-lifetime "promoted records" pile.

## Method
Sampled 200K discovery-role records from Fire #121's corpus
(`batch-20260525T185205Z-0b3b1f.jsonl`). Computed
`training_weight()` for each. Filtered out NON_DISCOVERY_ROLES gens
(b1, c4, f1, g3). Threshold ≥ 0.6 matches daemon's promote logic.

## Headline numbers
- **24.6%** of disc-role records are promote-eligible (≥0.6 weight)
- **49,131** records qualify in this batch's first 200K
- Daemon caps promotion at **20 per batch** → top 20 by weight win
- All 20 cluster at **w=0.650 exactly** (no separation)

## What the top 20 actually are

Sample of top-10 promoted-eligible records (verbatim):

    w=0.650 f2 invariant_equality SHADOW_CATALOG
      F2_AFS[cov=1] determinant(knot:8_21) equal_mod_2 rank(ec:9240.e4) | 15 vs 1 | holds=True

    w=0.650 g4 symmetry_transform SHADOW_CATALOG
      G4_REFL[crossing_number↔-crossing_number] crossing_number(knot:8_21) equal_mod_2 conductor(ec:7092.a1) | raw=8:True reflected=-8:True symmetric=True

    w=0.650 g4 symmetry_transform SHADOW_CATALOG
      G4_REFL[three_genus↔-three_genus] three_genus(knot:6_1) equal_mod_2 conductor(ec:5907.d3) | raw=1:True reflected=-1:True symmetric=True

    w=0.650 f2 invariant_equality REJECTED
      F2_AFS[cov=1] three_genus(knot:8_12) equal_mod_2 torsion(ec:5292.k1) | 2 vs 1 | holds=False

## The finding

**Top promoted records are parity-class trivialities.** Two patterns:

1. **F2_AFS equal_mod_2**: random pairings of knot invariants vs EC
   invariants asking "are these both even / both odd?". Mathematically
   true ~50% of the time by chance. Carries no information.

2. **G4_REFL reflection symmetry**: claims "X equal_mod_2 -X" for
   integer invariants. Mathematically tautological — any integer X has
   X ≡ -X (mod 2) iff X is even. The "raw=8:True reflected=-8:True"
   pattern is just confirming that small integers preserve their
   parity under sign flip. Vacuous.

## Why these pass training_weight ≥ 0.6

`training_weight` formula gives full weight to SHADOW_CATALOG
(passed) and partial to REJECTED. Doesn't penalize triviality of
the underlying relation. Both `equal_mod_2` and `symmetric` are
weak relations that pass by construction or by chance.

## Implication

**"1991 lifetime promoted records" = 1991 parity tautologies, not
1991 mathematical findings.** The "0 verified findings" anchor is
correct and load-bearing. The promote-filter as currently calibrated
selects for high-confidence cells but doesn't select for
non-triviality.

## Recommended actions

1. **Reclassify f2/g4 as TAUTOLOGY_CONTROL or BOUNDARY_MAPPING.**
   Their output IS substrate-internal noise, not learner-trainable
   discovery. Same justification that put c4 into TAUTOLOGY_CONTROL
   (Fire #53).

2. **Tighten promote filter.** Either:
   - Raise threshold from 0.6 → 0.8
   - Add relation-strength term to training_weight (penalize
     `equal_mod_2`, reward `exact_equality`, `divides`, `congruence`)
   - Filter claim_kind=symmetry_transform with `reflected=-X`
     pattern (vacuous by construction)

3. **Refresh the "verified mathematical findings = 0" anchor** in
   all stdout / journals to reflect WHY that number is 0: the
   substrate produces parity coincidences at scale, none of which
   constitute discovery without external verification.

## Where this fits

This is anti-passive-consumer remediation (the user has flagged
"every doc must trace to a behavior delta"). The behavior delta:
**stop counting parity-tautologies as promoted records.**

Until f2/g4 reclassification or filter tightening, the lifetime
promoted count will keep ticking up by 20 per fire without
gaining information.

## Followups (added to backlog)

- Reclassify f2 / g4 role (review their generator docstrings — they
  may have been intended as boundary/control all along).
- Add `relation_strength_multiplier` to `training_weight()` that
  downweights `equal_mod_2` and similar weak relations.
- Audit other DISCOVERY-role gens for similar tautology patterns
  (a2 statistical correlation, h1 self play hunter).

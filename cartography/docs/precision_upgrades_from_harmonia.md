# Precision Upgrades from Harmonia Falsification
## What each kill taught us about our own battery
### 2026-04-13

---

## The Kills and What They Expose

### Kill 1: Random Arithmos (rho=0.91 real vs 0.92 random)
**What broke:** Sorting two sets of small integers by rank and correlating them gives rho≈0.9 regardless of whether the integers are related.

**What our battery missed:** We had F29 (distributional baseline) for SET OVERLAP but nothing for RANK-SORTED TRANSFER. Harmonia's "cross-domain prediction" isn't overlap — it's nearest-neighbor matching in a projected space. Our F29-F32 test the wrong thing for this claim type.

**New test needed:**
> **F33: Rank-sort null.** For any claim of cross-domain prediction via nearest-neighbor matching: shuffle the target variable labels within each domain, re-run the matching, compute null rho. The real rho must exceed the rank-sort null at z > 3. This catches any "transfer" that's just ordinal alignment of similarly-distributed variables.

---

### Kill 2: Trivial 1D predictor (rho=1.0 vs claimed 0.61)
**What broke:** Finding the nearest integer in domain B to a value from domain A trivially achieves perfect correlation when both domains use small integers.

**What our battery missed:** No baseline comparison against the SIMPLEST possible predictor. Our battery tests whether a signal is REAL but not whether a COMPLEX method adds value over a TRIVIAL one.

**New test needed:**
> **F34: Trivial baseline comparison.** For any cross-domain prediction claim: compute the trivial baseline (nearest-value matching in 1D on the raw target variable). The claimed method must EXCEED the trivial baseline. If it doesn't, the method adds no value — the "structure" is in the data, not in the method.

---

### Kill 3: Physics↔Math coupling (Materials↔EC rho=-0.65)
**What broke:** Any domain with a magnitude feature couples to any other domain with a magnitude feature through Megethos/log(N) matching. The phoneme system creates spurious bridges.

**What our battery missed:** No test for "does this cross-domain method produce false positives on KNOWN unrelated domains?" Our F27 checks known tautologies but doesn't test known FALSEHOODS.

**New test needed:**
> **F35: Known-false-positive control.** Maintain a list of domain pairs known to have NO genuine mathematical connection (e.g., PDG particles ↔ knot invariants, earthquake magnitudes ↔ class numbers). Run the cross-domain method on these pairs. If ANY known-false pair passes, the method is too permissive. This is the SPECIFICITY calibration we're missing (our known-truth battery tests SENSITIVITY only).

---

### Kill 4: h-R strengthening (z=-1.1 by proper permutation)
**What broke:** The initial z=20.2 was against a synthetic null (random L-values in h*R=sqrt(d)*noise) that didn't match the real data structure. The proper null (label permutation) gives z=-1.1.

**What our battery missed:** Our permutation null (F1, F24_permutation_null) always shuffles the LABELS. But for partial-correlation claims ("rho strengthens after controlling for X"), the null should be: shuffle labels, compute BOTH raw and partial, check if the DIFFERENCE (strengthening) is significant. We test the absolute level but not the differential.

**New test needed:**
> **F36: Partial-correlation strengthening null.** For any claim that a partial correlation STRENGTHENS after removing a confound: shuffle labels, compute raw rho AND partial rho, compute the difference. The real strengthening must exceed the null strengthening distribution at z > 3. This prevents false "novel residual" claims that are just statistical properties of the log-partial procedure.

---

### Kill 5: Hand-crafted phonemes (engineered universality)
**What broke:** The "universal coordinate system" was designed by a human who chose which features map to which coordinates. The "universality" is in the engineering, not necessarily in the data.

**What our battery missed:** No test for "would a different researcher's feature engineering produce the same result?" Our F20 tests representation invariance WITHIN a finding but not across DIFFERENT feature engineering choices.

**New test needed:**
> **F37: Feature engineering sensitivity.** For any finding that depends on a hand-crafted feature projection: replace the projection with (a) PCA on raw features, (b) random projections, (c) alternative domain-expert projections. The finding must survive at least 2 of 3 alternatives. If it only works with the specific hand-crafted projection, the "structure" is in the engineering.

---

### Meta-Kill: F1 permutation null fails 6/8 pairs
**What broke:** Harmonia's coupling function is indistinguishable from shuffled data for most domain pairs. The "7/8 PASS" comes from secondary tests (stability, effect size, direction) that can pass even on engineered structure.

**What our battery missed:** Our battery allows a finding to PASS on secondary tests even when the primary null (F1 permutation) FAILS. This is like declaring a drug effective because it's well-tolerated, even though it doesn't beat placebo.

**Fix needed:**
> **F1 as hard gate.** If F1 (permutation null) fails at z < 2, the finding CANNOT pass regardless of other tests. F1 should be a PREREQUISITE, not one test among many. Currently it's weighted equally with F2-F14 in our battery_unified.py.

---

## Summary: 5 New Tests + 1 Fix

| # | Test | What it catches | Example kill |
|---|------|----------------|-------------|
| F33 | Rank-sort null | Ordinal alignment of small integers | Arithmos rho=0.61 |
| F34 | Trivial baseline comparison | Complex method adding no value over nearest-integer | Phoneme transfer vs 1D matching |
| F35 | Known-false-positive control | Permissive methods coupling unrelated domains | Materials↔EC via Megethos |
| F36 | Partial-correlation strengthening null | False "novel residual" from log-partial procedure | h-R strengthening z=20→-1.1 |
| F37 | Feature engineering sensitivity | Engineered universality vs intrinsic structure | Hand-crafted phonemes |
| F1 fix | Hard gate on permutation null | Findings passing on secondary tests only | 6/8 Harmonia F1 failures |

---

## What This Means for the Battery

Before Harmonia: 32 tests (F1-F32 + F25b + F25c).
After Harmonia: 37 tests (F1-F37) + F1 hard-gate fix.

The battery's blind spot was **cross-domain prediction claims** — a category we hadn't seen before (our original work was categorical→continuous within domains). Harmonia exposed that:

1. Small-integer ordinal alignment is trivially achievable (F33)
2. Complex methods can underperform trivial baselines (F34)
3. Magnitude-based matching creates universal spurious coupling (F35)
4. Partial-correlation "strengthening" can be an artifact (F36)
5. Hand-crafted features can bake in the "universality" they claim to discover (F37)
6. Secondary tests should not override primary null failure (F1 fix)

Each of these is a NEW FAILURE MODE that wasn't in our taxonomy. The Harmonia falsification exercise produced more battery improvements than any prior round of testing.

---

*Compiled: 2026-04-13*
*Source: Harmonia adversarial review + deep falsification + h-R deep dive*

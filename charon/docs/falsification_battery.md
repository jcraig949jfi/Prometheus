# Falsification Battery: Every Attack We Tried
## Status: Living document. Updated 2026-04-04.

---

## Purpose

Before publishing anything, we need to demonstrate we tried to murder every
claim. This document maps each claim to its kill tests: what would falsify it,
what we ran, what the result was, and what's still open.

---

## Claim 1: Zeros 5-19 encode rank geometry (ARI = 0.55)

**What would kill it:**
Any demonstration that the ARI is an artifact of methodology, data processing,
or a known confound rather than genuine rank-related structure in the zeros.

| # | Attack Vector | Test | Status | Result |
|---|--------------|------|--------|--------|
| 1a | ARI is noise | Permutation null (1000 trials, shuffle rank labels) | DONE | Null ARI = 0.006. Empirical is 90+ sigma above null. |
| 1b | K-means is unstable | Vary k (2-8), random seeds (10 seeds) | DONE | ARI stable within +/-0.01 across all settings |
| 1c | Window choice is cherry-picked | Full ablation sweep z1-z25 | DONE | z5-19 is the plateau. z5-25 adds nothing. z1-4 hurts. |
| 1d | Isogeny dedup changes result | Run with and without dedup | **TODO** | -- |
| 1e | Conductor stratification is wrong | Re-stratify by analytic conductor | DONE | ARI identical (delta=0.000) |
| 1f | Normalization creates the signal | Exact Gamma unfolding | DONE | ARI changes by +0.003. Negligible. |
| 1g | Different clustering method | Gaussian mixture, spectral clustering | **TODO** | -- |
| 1h | Small sample in some strata | Remove strata with n < 10, n < 20 | **TODO** | -- |
| 1i | ARI is sensitive to rank-2 contamination | Remove rank-2, recompute | DONE | ARI drops ~0.03 but signal remains |
| 1j | Different distance metric | Cosine, Manhattan, Mahalanobis | **TODO** | -- |
| 1k | Train/test split | 50/50 random split, compute ARI on held-out | **TODO** | -- |

---

## Claim 2: The 0.05 ARI residual beyond RMT is real

**What would kill it:**
The gap between empirical ARI (0.49) and RMT simulation ARI (0.44) is
within simulation variance, or is explained by a known finite-conductor
correction.

| # | Attack Vector | Test | Status | Result |
|---|--------------|------|--------|--------|
| 2a | RMT simulation is wrong | Two approaches: naive + enhanced Metropolis | DONE | Both give ~0.44. Enhanced < Naive (surprise). |
| 2b | Gap is finite-conductor correction | ARI vs 1/log(N) regression | DONE | Non-monotonic (U-curve). Intercept = 0.37, but poor fit R^2=0.32. |
| 2c | Gap shrinks at higher N | Check ARI at N > 2500 | DONE | ARI INCREASES (0.55 -> 0.58). Opposite of correction. |
| 2d | Finite-matrix RMT predicts the gap | SO(120) gap simulation | RUNNING | Awaiting results. |
| 2e | Residual is Tamagawa | Partial out Tamagawa, recheck ARI | DONE | Explains 1.1%. Residual survives. |
| 2f | Residual is Galois image | Partial out mod-2 image, recheck ARI | DONE | Explains 0.4%. Residual survives. |
| 2g | Residual is Sha leaking into tail | Hotelling T^2 on tail, conductor-matched | DONE | p = 0.109. Not significant. |
| 2h | Residual is BSD invariants (nonlinear) | Random forest / mutual information | **TODO** | -- |
| 2i | Residual is torsion structure | Stratify by torsion, test tail | **TODO** | -- |
| 2j | 50 trials is too few for RMT sim | Run 500 trials | **TODO** | -- |
| 2k | RMT matrix size N=60 is wrong | Test N=30 and N=120 | **TODO** | -- |

---

## Claim 3: 14 mechanisms stripped (signal is unexplained)

**What would kill it:**
Any of the 14 "stripped" mechanisms is actually NOT stripped -- either
the test was wrong, underpowered, or the mechanism was tested incorrectly.

| # | Mechanism | Attack on the Kill | Status | Concern Level |
|---|-----------|-------------------|--------|---------------|
| 3a | Central vanishing (kill 1) | Ablation is obvious, not a "kill" | LOW | Methodologically sound but trivial. |
| 3b | Conductor (kill 2) | Ridge is linear; nonlinear conductor effects? | **TODO** | MEDIUM -- test with random forest. |
| 3c | Sha (kill 3) | Only 498 Sha>=4 curves, underpowered? | NOTED | Hotelling p=0.109 is borderline. Council flagged. |
| 3d | Faltings height (kill 4) | < 1% variance, but only linear test | **TODO** | LOW -- but test nonlinear. |
| 3e | Modular degree (kill 5) | Same as 3d | **TODO** | LOW |
| 3f | Symmetry type (kill 6) | ARI=0.49 within SO(even) with z=14.0 | OK | Solid. z-score is high. |
| 3g | Pre-asymptotic (kill 7) | U-curve contradicts "FLAT" claim | FLAGGED | Need to revise: slope is flat on average but not monotonic. |
| 3h | Truncation (kill 8) | Plateau confirmed with 25+ zeros | OK | Solid. |
| 3i | Inner twists (kill 9) | CM=0.87x, but Fricke=1.44x is unexplained | NOTED | Kill is on CM, not on Fricke. Fricke is still open. |
| 3j | KS normalization (kill 10) | Unfolding doesn't change ARI | OK | But Gemini argues ARI is insensitive metric. |
| 3k | Analytic conductor (kill 11) | Scale invariance within strata trivializes it | NOTED | Test is valid but trivial. |
| 3l | Sha on tail (kill 12) | Underpowered (see 3c) | NOTED | Same concern as 3c. |
| 3m | Tamagawa (kill 13) | Conductor confounding caught and controlled | OK | Careful test with conductor matching. |
| 3n | Galois image (kill 14) | Conductor-matched, 6/16 sig but ARI delta 0.4% | OK | Effect exists but orthogonal to rank. |

---

## Claim 4: BSD wall (z1 and z5-20 are disjoint channels)

**What would kill it:**
The "wall" is an artifact of linear methods, or the separation is gradual
rather than sharp, or it's trivially predicted by the explicit formula.

| # | Attack Vector | Test | Status | Result |
|---|--------------|------|--------|--------|
| 4a | Wall is linear-methods artifact | Nonlinear BSD model (random forest) | **TODO** | -- |
| 4b | Separation is gradual, not sharp | Sliding window correlation z1->z20 | **TODO** | -- |
| 4c | Wall is trivially predicted | Literature search (package 29) | SUBMITTED | Awaiting Gemini. |
| 4d | Tamagawa breaks the wall | Tamagawa partial correlation per zero | DONE | Tamagawa has TWO humps (z1-3 AND z10-16). Wall is not clean for Tamagawa. |
| 4e | Wall location shifts with rank | Test rank-1 separately | **TODO** | -- |

---

## Claim 5: Structured gap pattern (8/15 survive Bonferroni)

**What would kill it:**
The oscillation (dead zones, z17-z18 reversal) is a finite-matrix RMT effect,
or is an artifact of multiple testing, or is not replicable.

| # | Attack Vector | Test | Status | Result |
|---|--------------|------|--------|--------|
| 5a | Multiple testing | Bonferroni correction | DONE | 8/15 survive at p < 0.0033 |
| 5b | Pattern is noise | Permutation test on d-vector | DONE | p = 0.001 (0/1000 exceeded) |
| 5c | Finite-matrix RMT predicts it | SO(120) rank-0 vs rank-1 gap simulation | RUNNING | The definitive test. |
| 5d | Pattern is conductor-dependent | Stratify by conductor, check if oscillation shifts | **TODO** | -- |
| 5e | Pattern is driven by outliers | Remove top/bottom 5% of zeros, recheck | **TODO** | -- |
| 5f | Different effect size metric | Use Wasserstein distance per gap instead of Cohen's d | **TODO** | -- |

---

## Claim 6: Tamagawa two-hump spectral fingerprint

**What would kill it:**
The two-hump pattern (z1-3, z10-16) is a conductor artifact or is trivially
predicted by the explicit formula.

| # | Attack Vector | Test | Status | Result |
|---|--------------|------|--------|--------|
| 6a | Conductor confounding | Conductor-matched Fisher test | DONE | 6/16 survive conductor matching. Real but weaker. |
| 6b | Partial correlation controls | Control for log(cond) + rank | DONE | Pattern clear: r=0.25 at z1, dead z4-9, second hump z10-16. |
| 6c | Hump location is conductor-dependent | Stratify and check if second hump shifts | **TODO** | -- |
| 6d | Trivially predicted | Literature search (package 34) | SUBMITTED | Awaiting Gemini. |
| 6e | Kodaira symbol substructure | Split by reduction type, check if pattern changes | **TODO** | -- |

---

## Open TODO List (Priority Order)

### Must-Do Before Paper

| # | Test | Attacks | Effort |
|---|------|---------|--------|
| T1 | **RMT gap simulation** (running) | 2d, 5c | HIGH -- definitive null for gap pattern |
| T2 | **Nonlinear BSD (random forest)** | 2h, 3b, 3d, 3e, 4a | MEDIUM -- council demanded |
| T3 | **10,000 permutation trials on ARI** | 1a, 2j | LOW -- just increase n_perm |
| T4 | **Train/test split** | 1k | LOW -- basic ML hygiene |
| T5 | **Sliding window BSD correlation** | 4b | LOW -- visualizes the wall |
| T6 | **Torsion stratification** | 2i | LOW -- quick check |

### Should-Do

| # | Test | Attacks | Effort |
|---|------|---------|--------|
| T7 | Alternative clustering (GMM, spectral) | 1g | MEDIUM |
| T8 | Different distance metrics | 1j | MEDIUM |
| T9 | Isogeny dedup sensitivity | 1d | LOW |
| T10 | Minimum stratum size sensitivity | 1h | LOW |
| T11 | Gap pattern conductor stratification | 5d | MEDIUM |
| T12 | RMT at different matrix sizes (N=30,120) | 2k | HIGH (slow) |
| T13 | Rank-1 BSD wall check | 4e | LOW |
| T14 | Tamagawa hump conductor dependence | 6c | MEDIUM |
| T15 | Outlier removal on gap pattern | 5e | LOW |

---

## The Argument Structure

If we survive all of the above, the paper argument is:

1. **The signal exists.** ARI = 0.55, permutation null = 0.006, stable across
   k, seeds, normalization, window, and train/test split.

2. **90% is GUE repulsion.** RMT simulation ARI = 0.44. Known physics,
   novel as computational demonstration.

3. **The 0.05 residual is real.** 14 mechanisms stripped. None explains more
   than 1.1%. The residual survives every arithmetic confound we tested
   (including nonlinear models).

4. **The residual has structure.** The gap oscillation pattern (8/15 Bonferroni,
   permutation p=0.001) is [NOT/PARTIALLY/FULLY] predicted by finite-matrix RMT.

5. **Two disjoint channels.** BSD invariants live in z1. The spectral tail is
   BSD-free. Tamagawa has a two-hump fingerprint but is rank-orthogonal.

**What we DON'T claim:** We don't claim to know what produces the residual.
We claim it survives 14 stripping attempts and has non-trivial structure.

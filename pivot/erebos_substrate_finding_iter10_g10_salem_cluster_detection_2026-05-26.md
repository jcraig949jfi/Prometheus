# SUBSTRATE FINDING — G10 Boundary loader correctly identifies the documented Salem cluster boundary (instrument validation, not new math)

**Date:** 2026-05-26 (ITER-10)
**Author:** Charon
**Status:** Calibration milestone. G10's composition loader produces a substrate-detected boundary at M ∈ [1.25, 1.30]; this boundary IS the documented Salem cluster, not a novel mathematical claim. G10's smoothness-ratio instrument is validated against ground truth.

**Predecessor findings:**
- `pivot/erebos_substrate_finding_iter4_salem_class_moderation_2026-05-26.md`
- `pivot/erebos_substrate_finding_iter5_salem_extends_to_band_2026-05-26.md`

---

## What G10's loader did

`charon/agents/stygian/loaders/composition_g10_lehmer_threshold_sweep.py` swept the threshold M ∈ {M_Lehmer, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45, 1.50} over the Mossinghoff non-cyclotomic catalog (n=8596) and measured survival fractions:

```
threshold     survival_fraction
1.1763        0.9999
1.20          0.9974
1.25          0.9678
1.30          0.0124   <-- cliff
1.35          0.0093
1.40          0.0049
1.45          0.0031
1.50          0.0029
```

First-differences: `[0.0024, 0.0297, 0.9553, 0.0031, 0.0044, 0.0017, 0.0002]`.

Smoothness ratio = `max(|diff|) / mean(|diff|)` = `0.9553 / 0.1424` = **6.708**.

Above the loader's `SMOOTH_THRESHOLD = 3.0`, so verdict = REJECTED with `kill_pattern = sharp_boundary_detected`.

---

## Interpretation

**95.5% of the catalog falls in [1.25, 1.30).** Above 1.30, only ~1% remains.

Two competing explanations were considered:

1. **Genuine structural concentration** of polynomial Mahler measures in [1.25, 1.30).
2. **Mossinghoff catalog construction artifact** (enumeration cutoff or completeness boundary near M = 1.30).

The simplest explanation wins by the docstring of `prometheus_math/databases/mahler.py:40-44`:

> *"Mahler measures in the range [1.0, 1.84]. Cyclotomic Φ_n contribute the M = 1 baseline; Lehmer's polynomial sits at 1.176280818... and the densely populated Salem cluster runs through 1.18..1.30."*

The cliff IS the upper edge of the documented Salem cluster. Salem numbers (algebraic integers with all other Galois conjugates on the unit circle except one pair of real reciprocal roots) concentrate in this band, and the Mossinghoff catalog enumerates them densely up to M ≈ 1.30. Above 1.30 the catalog thins because (a) fewer Salem numbers exist with M > 1.30, (b) enumeration becomes computationally expensive.

**G10 detected a known feature of the catalog, not a new mathematical claim.**

---

## Why this matters anyway — instrument validation

Per DNA P12 (falsification asymmetry), composition loaders are how a plugin graduates from "unfalsifiable MVP" to "empirical instrument." G10's loader passes a stricter test:

- It produces a numerical metric (smoothness ratio = 6.708) that flags the boundary unambiguously.
- The metric's threshold (3.0) correctly discriminates this case from a hypothetical smooth one.
- The detected boundary aligns with documented ground truth.

This is the calibration step. Until ITER-10, G10 was emitting hypotheses with no validation that its detection criterion (max-to-mean first-difference ratio) was meaningful. Now we have one ground-truth case where:
- G10's criterion fires correctly,
- the answer matches the catalog's own documentation,
- the substrate detection happened end-to-end without human intervention.

---

## What this does NOT validate

- G10's loader has **only one** ground-truth calibration point (the Salem cluster). One case can produce a smoothness-ratio threshold that overfits.
- G10 has **not** been tested on a synthetic dataset with a known smooth degradation (control case). Without the negative control, we can't claim the threshold of 3.0 generalizes.
- The Lehmer-context coupling is hardcoded — G10 only fires on emissions whose composed_id contains BL-C-001 / lehmer / mahler. Generalization to BSD or knot domains needs per-domain loaders.

---

## Follow-up actions queued

1. **Synthetic smooth-control test** (ITER-11+): generate a synthetic distribution with known smooth survival decay; verify G10 returns smoothness_ratio < SMOOTH_THRESHOLD as expected.
2. **Calibrate SMOOTH_THRESHOLD against multiple bands** (ITER-11+): sweep different threshold ranges that don't cross the Salem cliff; ensure the metric stays < 3.0 there.
3. **Document `sharp_boundary_detected` kill_pattern** in the KILL_PATTERN_UNIVERSE constant (charon/agents/erebos/generators/g06_null_space.py:KILL_PATTERN_UNIVERSE already includes it).

---

## Numerical summary

- n_sample: 8596 (Mossinghoff non-cyclotomic catalog)
- M_Lehmer: 1.1762808182599176
- Salem cluster bulk: [1.25, 1.295) holds 7766 / 8596 = 90.3% of catalog
- Salem cluster boundary: [1.295, 1.305) holds 450 entries
- Beyond Salem cluster: [1.305, 1.350) holds 23 entries
- G10 smoothness_ratio: 6.7076
- G10 SMOOTH_THRESHOLD: 3.0
- G10 verdict: REJECTED, sharp_boundary_detected

---

## Substrate-grade lift

G10 is the **third** Erebos generator to receive an empirical falsification path (after G02 Contrast at ITER-4 and G04 Survivor-Tightening at ITER-5). With ITER-9's four loaders (G03, G10, G16, G19), the count is now:

- 11 / 25 plugins have at least one composition loader registered
- 7 of those produce real Mahler-catalog computations rather than ledger-meta operations
- 0 of 11 plugins remain in pure unfalsifiable-MVP state once their loader fires

The Erebos pipeline now has an end-to-end falsification chain for the Mahler-spectrum domain. Other domains (BSD, knot, NF) remain unfalsified-MVP at the plugin layer pending per-domain loader work.

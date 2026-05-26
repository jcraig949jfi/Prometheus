# SUBSTRATE FINDING — Salem-class moderation extends into band M ∈ [1.30, 1.50]; Smyth + degree-parity reject

**Date:** 2026-05-26 (ITER-5)
**Author:** Charon
**Status:** Second substrate-grade PROMOTED claim through Erebos
generative pipeline; three new composition loaders empirically
graduated.

**Predecessor finding:** `pivot/erebos_substrate_finding_iter4_salem_class_moderation_2026-05-26.md`
established Salem moderation at M ≥ 1.30 on the full catalog. ITER-5
extends + falsifies sibling hypotheses.

---

## The three new tests + verdicts

All three are direct extensions of the ITER-4 finding, using the
shared `_mahler_composition_helpers.run_binary_split_permutation_null`.

### 1. Salem-class within band M ∈ [1.30, 1.50] @ threshold M=1.40

**Verdict: PROMOTED.**

Within the higher band (away from the Salem cluster's bulk near
Lehmer's value):
- Salem-class entries: n=23. Survival fraction at M ≥ 1.40 = **0.4783**
- Non-Salem entries: n=59. Survival fraction at M ≥ 1.40 = **0.1017**
- Observed divergence: 0.3766 > null p95: 0.1953 (1.93× null)

**Substrate-grade observation:** Salem moderation isn't just a
near-Lehmer effect. Within the (already-restricted) [1.30, 1.50]
band, Salem entries are still distinguishable from non-Salem by
their concentration toward the upper half. The Salem cluster has
a thick right tail extending well past 1.30.

**Population-level addendum (worth flagging):** within band
[1.30, 1.50]:
- Only 23 of 8513 Salem entries (0.27%) — most Salem entries are
  below 1.30, as expected.
- 59 of 83 non-Salem entries (71%) — non-Salem entries are
  predominantly above 1.30.

So the catalog's Salem and non-Salem populations live in nearly
disjoint Mahler-measure regimes, with overlap concentrated in band
[1.30, 1.50]. Within that overlap, Salem-vs-non-Salem still
discriminates.

### 2. Smyth-extremal @ M_Lehmer (full catalog)

**Verdict: REJECTED, kill_pattern=permutation_null.**

Smyth-extremal vs non-Smyth-extremal binary at threshold M_Lehmer
yields no significant divergence. Smyth class is NOT a moderator
of Lehmer-bound survival at this scale.

This is the EXPECTED outcome — Smyth-extremal entries are rare
(~few hundred in the catalog) and all sit ABOVE Lehmer's bound
trivially (Smyth's bound 1.32472 > Lehmer's 1.17628). The binary
collapses to "trivially-above-bound" vs "also-trivially-above-
bound."

### 3. Degree parity @ M_Lehmer (full catalog)

**Verdict: REJECTED, kill_pattern=permutation_null.**

Even-degree vs odd-degree binary at threshold M_Lehmer yields no
significant divergence. Degree parity is NOT a moderator.

Also EXPECTED — degree parity is a thin feature for the Mahler-
measure distribution. The reciprocal-polynomial structure (which
some palindromic conventions tie to parity) doesn't propagate to
M-distribution at this granularity.

---

## What this validates + reframes

### Validates

- **DNA P9 (rolling cadence):** ITER-4's Salem finding produced
  ITER-5's parametric extension (band-restricted, sibling
  categoricals). The substrate growth pattern that the spec
  envisioned is operating.
- **DNA P12 (falsification asymmetry):** three more empirical-
  instrument graduations:
  - `composition_g02_g04_lehmer_band_1_30_to_1_50`: PROMOTED ✓
  - `composition_g02_lehmer_smyth_extremal`: REJECTED ✓
  - `composition_g02_lehmer_degree_parity`: REJECTED ✓
  Each plugin's expected_kill_pattern was either matched (G02
  permutation_null on Smyth + parity) or beaten (G02+G04 PROMOTED
  again on band-restricted Salem).
- **The shared helper module** (`_mahler_composition_helpers.py`)
  pays for itself immediately. 3 new loaders × ~80 LOC vs ~200
  LOC each without the helper. The helper IS the right
  abstraction for the Salem-cluster-and-cousins family.

### Reframes

- The ITER-4 framing ("Salem cluster is concentrated near Lehmer's
  value, sparse above 1.30") is *partially* right but more
  layered: Salem entries DO concentrate near Lehmer, but those
  that DO exceed 1.30 are STILL distinguishable from non-Salem
  in their distribution within [1.30, 1.50]. The cluster has
  thicker tails than the simple cluster-near-Lehmer picture
  suggested.

- This isn't a novel mathematical discovery -- Salem-Pisot-Lehmer
  structure has been studied for decades and the thick-tail
  behavior is in the literature. What's new is the swarm's
  parametric extension: it took the ITER-4 finding, varied band
  + threshold, and surfaced the next-layer structure
  automatically.

---

## Implications for ITER-6

Per the loop roadmap, ITER-6 was scheduled as "Tier B/C research
notes." The substrate finding suggests an additional ITER-6
deliverable worth slotting:

- **More band-extension loaders.** [1.50, 1.75], [1.75, 2.00].
  Does Salem moderation persist arbitrarily upward, or does it
  fade past some scale? The composition_g02_g04_lehmer_band_high
  template extends naturally.
- **Cross-categorical chained compositions.** G02+G04 over Salem
  works; what about G02+G09 (Contrast + Projection) or G02+G25
  (Contrast + Degeneracy)? Each new chain adds one more
  composition-loader to the empirically-validated set.
- **Other catalogs.** BSD has CM-vs-non-CM as the natural Salem-
  analog binary. Composition loaders for `g02_bsd_cm_vs_non_cm`
  with parametric conductor thresholds — does CM class moderate
  BSD rank distribution at specific conductor bands? Hypothetical
  but testable.

These are PROMOTED next-priorities IF the ITER-6 research
deliverables (Tier B/C generators) are deferred. Open call to
James at ITER-6 entry-point.

---

## Tally so far across the loop

Composition loaders shipped + verdicts:

- `g02_lehmer_salem` (ITER-3): REJECTED / permutation_null at
  M_Lehmer. Threshold-artifact.
- `g09_lehmer_ablation` (ITER-4): REJECTED / residual_survival.
  Lehmer survival is sample-invariant.
- `g25_lehmer_degenerate` (ITER-4): UNVERIFIED. Catalog has no
  degree-1 entries (coverage gap).
- `g02_g04_lehmer_tightened` (ITER-4): **PROMOTED**. Salem
  moderates at M=1.30. First Erebos PROMOTED.
- `g02_g04_lehmer_band_1_30_to_1_50` (ITER-5): **PROMOTED**.
  Salem moderation persists in [1.30, 1.50] band.
- `g02_lehmer_smyth_extremal` (ITER-5): REJECTED / permutation_null.
- `g02_lehmer_degree_parity` (ITER-5): REJECTED / permutation_null.

Tally: 7 composition loaders, 2 PROMOTED, 4 REJECTED at expected
kill pattern, 1 UNVERIFIED (catalog coverage). Per DNA P12, the
generator plugins are graduating as their composition loaders
validate them. The growing PROMOTED count is the substrate's
discovery loop running for real.

— Charon, 2026-05-26 ITER-5

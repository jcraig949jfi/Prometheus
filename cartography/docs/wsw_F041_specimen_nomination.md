# Specimen Nomination — F041 Keating-Snaith moment-ratio convergence

**Nominated by:** Harmonia_M2_sessionC, 2026-04-18
**Status:** NOT PROMOTED — downgraded to **calibration-adjacent** after follow-up analysis.
**Original report:** `cartography/docs/keating_snaith_moments_results.json` (Report 4 execution, 2026-04-18).
**Follow-up analyses:**
- `cartography/docs/keating_snaith_arithmetic_analysis_results.json` (F1/F4/F5)
- `cartography/docs/keating_snaith_katz_sarnak_results.json` (F3)

---

## Initial observation

`M_k(X) = mean(leading_term^k)` binned by (analytic_rank, conductor-decade), with `R_k(X) = M_k(X) / (log X)^{k(k-1)/2}` per Aporia Report 4 exponent. Slopes of `R_k(log X)` across conductor decades 10³..10⁶:

| rank | k=1 | k=2 | k=3 | k=4 |
|-----:|----:|----:|----:|----:|
| 0 | +0.164 | +0.068 | 0.000 | 0.000 |
| 1 | +0.922 | +0.877 | +0.071 | 0.001 |
| 2 | +1.929 | +2.651 | +0.277 | 0.002 |
| 3 | +2.370 | +3.649 | +0.383 | 0.003 |

Monotone increase in rank, roughly linear in `r` for k=1. That monotonicity was the seed for nominating "Keating-Snaith moment-ratio convergence rate scales with analytic_rank" as specimen F041 (Pattern-18-adjacent: family-dependent observable).

## Follow-up findings that demote the nomination

### F1 — First-moment deflation flattens all slopes

After normalizing `M_k_normalized = M_k / M_1^k` per cell, slopes of `R_k_normalized(log X)` collapse to near-zero across **every** rank for k = 2, 3, 4:

| rank | k=2 normalized slope | k=3 | k=4 |
|-----:|---------------------:|----:|----:|
| 0 | −0.010 ± 0.002 | −0.001 | ≈ 0 |
| 1 | −0.013 ± 0.002 | −0.001 | ≈ 0 |
| 2 | −0.010 ± 0.001 | 0.000 | ≈ 0 |
| 3 | −0.007 | 0.000 | ≈ 0 |

**Interpretation:** the rank-dependence in the raw k=1 slope was almost entirely driven by `E[leading_term | rank]` growing with rank — i.e. first-moment drift. Higher-moment *shape* after deflation is rank-invariant. This is classical RMT behavior, where `a_E(k)·g_SO(k)` is approximately the full rank-independent rational structure and finite-N corrections are small at these conductors.

### F3 — Katz-Sarnak low-tail sign check confirms family assignment

Pr[`L/M_1` < 0.25] per (rank, decade):

| decade | rank 0 (predicted SO_even) | rank 1 (predicted SO_odd) | Δ |
|--------|---------------------------:|--------------------------:|----:|
| 10² | 0.0058 | 0.0000 | +0.0058 |
| 10³ | 0.0369 | 0.0010 | +0.0360 |
| 10⁴ | 0.0794 | 0.0070 | +0.0724 |
| 10⁵ | 0.1073 | 0.0152 | +0.0921 |

Rank 0 has universally more low-tail density than rank 1, every decade, with Δ growing in X. This is the qualitative Katz-Sarnak signature: SO_odd's forced central zero keeps `L'` away from zero; SO_even's unrestricted central value makes small values possible. **The rank-0 vs rank-1 contrast is consistent with SO_even vs SO_odd RMT prediction**, not anomalous.

### F4 — P021 bad-prime interaction: a real sub-specimen

Joint (rank, decade, `num_bad_primes`) slopes reveal a real **rank × `num_bad_primes` interaction** at rank ≥ 2:

| rank | nbp=1 | nbp=2 | nbp=3 | nbp=4 | nbp=5 | nbp=6 |
|-----:|------:|------:|------:|------:|------:|------:|
| 0 (k=1) | 0.07 | 0.14 | 0.14 | 0.13 | 0.11 | 0.12 |
| 1 (k=1) | 0.88 | 0.84 | 0.85 | 0.89 | 0.92 | 0.63 |
| 2 (k=1) | 1.21 | 1.52 | 1.70 | 1.86 | 1.95 | 2.52 |
| 3 (k=1) | — | 1.89 | 2.25 | — | — | — |

At rank 0 and rank 1 the slope is roughly flat across `num_bad_primes`. **At rank 2 the slope increases monotonically with `num_bad_primes`** (1.21 → 2.52), and rank 3 shows the same direction where coverage allows. This is NOT predicted by vanilla Katz-Sarnak — Katz-Sarnak is about rank-parity symmetry type, not rank-magnitude × bad-prime interaction.

### F5 — Pipeline sanity PASS

Within-cell permutation leaves moments numerically identical (max Δ < 1e-10 across all sample cells). No ordering dependence.

## Revised nomination

The original F041 ("convergence rate scales with analytic_rank") is **not** a new live specimen — it is Katz-Sarnak SO_even/SO_odd manifesting in the first-moment structure, visible because of M_1 drift. After Pattern-20-disciplined stratification + first-moment deflation, the *residual* convergence rate is approximately rank-invariant, and the rank-0 vs rank-1 low-tail ordering is classical.

**What remains as a potential live specimen:**

### F041a candidate — rank-2/3 × `num_bad_primes` slope interaction

- **Observation:** at rank ≥ 2, the slope of `R_1(log X)` scales monotonically with `num_bad_primes` (rank 2: 1.21 at k=1 → 2.52 at k=6; strong, nearly 2× range).
- **Not seen at rank 0 or rank 1.** The interaction is a higher-rank phenomenon.
- **Why this is interesting:** higher-rank L-functions are NOT in the clean SO_even/SO_odd dichotomy. Rank 2+ curves have at least two central-zero derivatives vanishing, and the moment behaviour is less studied. A rank × bad-prime interaction at this scale would be a structural observation worth cataloguing.
- **Pattern 5 gate:** needs theoretical comparison against Conrey-Farmer-Keating-Rubinstein-Snaith moment predictions for `L^(r)/r!` at r ≥ 2. If CFKRS predicts the bad-prime-count interaction: calibration. If not: frontier.

**Nominate:** F041a as `conjecture_candidate`, pending Pattern 5 gate. **Do NOT** promote to `live_specimen` without theoretical comparison.

## Invariance profile (per Pattern 20 discipline)

Projections applied during follow-up:
- **P023 rank** stratification — the primary axis; revealed rank-dependent slopes.
- **P020 conductor decade** binning — revealed convergence rates.
- **P021 `num_bad_primes`** stratification — revealed rank × nbp interaction at rank ≥ 2.
- **P028 Katz-Sarnak family** (via rank-parity alias) — confirmed sign consistency.
- **First-moment deflation** (new technique; no P-ID yet) — flattens rank dependence at higher k.

Pattern 20 hygiene: every statistic reported per-cell; no pooled moment. Per-cell table in `keating_snaith_moments_results.json` has 13 (rank, decade) cells at n ≥ 100.

## Follow-ups if F041a advances

1. **Compute CFKRS theoretical slopes** for L^(r)/r! moments at rank 2 and 3. Compare to the empirical monotone-in-nbp pattern. (Pattern 5 gate.)
2. **Test rank × nbp interaction under block-shuffle-within-(rank,decade,nbp)** — does the monotone-in-nbp slope survive a tighter null? (F010 precedent.)
3. **Repeat with Euler-product-deflated `leading_term`** — compute `a_E(k)` per curve from Dirichlet coefficients (requires `lfunc_lfunctions.dirichlet_coefficients` join), divide out, see if residual is rank-invariant at all k.
4. **Inspect rank 4-5 behaviour** once F030/F033 lfunc coverage cliff is addressed. If the nbp-slope continues monotone in rank ≥ 4, specimen generalizes.

## Summary

The Report 4 pipeline is **clean**: moments computed, normalization applied, family assignment verified, pipeline sanity passed. The loud "rank-dependent convergence rate" signal dissolves under Pattern-20-disciplined deflation. One narrower specimen candidate remains (rank-2+ × bad-prime slope interaction) and awaits theoretical comparison.

Pattern 5 gate is the frontier. Nothing to promote today.

---

*End of nomination. Drafted per sessionA hand-off 2026-04-18; five follow-ups executed (F1 combined, F2 this doc, F3 distribution check, F4 P021 strat combined, F5 pipeline sanity combined). Catalog entry NOT created — specimen is not yet live.*

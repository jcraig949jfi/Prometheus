# Lehmer precision ladder — empirical convergence-vs-dps curve

**Forged: 2026-05-04 — Techne (toolsmith)**

## Setup

Path A re-verified the 17 brute-force band entries flagged
`verification_failed=True` at the original `dps=30`. All 17 converged
at `dps=60` once the polynomial was factored over Z first (`Path A`'s
`high_precision_M_via_factor`). 15 → `cyclotomic_only` (M = 1), 2 →
`confirmed_in_band` (M = 1.17628…, the canonical Lehmer extension via
(x-1)^4 × Lehmer_10 and its sign-flipped twin).

Path A's headline was a single point: dps=60 converges all 17. This
driver builds the **full curve**: convergence rate vs. precision across
`dps ∈ {30, 40, 50, 60, 80, 100}` and across two strategies.

## The empirical question

> At what mpmath precision does each entry first converge, and how
> does that vary with strategy?

Two strategies are swept:

* **direct**: `mpmath.polyroots` on the unfactored deg-14 polynomial
  with `maxsteps=200` (held constant; the ladder isolates the
  precision axis).
* **factor-first**: `sympy.factor_list` decomposes over Z, then
  `Poly.nroots(n=dps)` on each irreducible factor; Mahler measures
  combine multiplicatively.

204 root-find calls total: 17 entries × 6 dps × 2 strategies.

## Convergence-vs-dps curve (the artifact)

| dps | direct converged | direct rate | factor-first converged | factor-first rate |
|----:|------------------:|------------:|-----------------------:|------------------:|
|  30 |              0/17 |       0.000 |                  17/17 |             1.000 |
|  40 |              0/17 |       0.000 |                  17/17 |             1.000 |
|  50 |              0/17 |       0.000 |                  17/17 |             1.000 |
|  60 |              0/17 |       0.000 |                  17/17 |             1.000 |
|  80 |              0/17 |       0.000 |                  17/17 |             1.000 |
| 100 |              0/17 |       0.000 |                  17/17 |             1.000 |

**Headline `dps` at which the curve flattens to N/N (full convergence):**

* direct strategy: never reached on this ladder.
* factor-first strategy: **`dps=30`** — the curve is already flat at
  the lowest ladder point.

## Per-entry × min-dps × classification table

All 17 entries converge under factor-first at `dps=30`, the lowest
ladder point. None converge under direct at any ladder point.

| # | half_coeffs | direct min_dps | factor_first min_dps | M (factor-first) | classification | regime |
|---|---|---:|---:|---:|---|---|
|  1 | [1, -4, 5, 0, -5, 4, -1, 0] | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
|  2 | [1, -3, 1, 5, -5, -1, 3, -2] | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
|  3 | [1, -3, 2, 1, 0, -2, 1, 0]   | never | 30 | 1.1762808183 | confirmed_in_band     | FACTOR_FIRST_ONLY |
|  4 | [1, -3, 2, 2, -4, 3, 1, -4]  | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
|  5 | [1, -3, 3, -2, 1, 3, -5, 4]  | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
|  6 | [1, -2, -1, 3, 1, -2, -1, 2] | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
|  7 | [1, -2, 0, 0, 2, 2, -3, 0]   | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
|  8 | [1, -1, -3, 2, 3, 1, -1, -4] | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
|  9 | [1, 0, 3, 0, 1, 0, -5, 0]    | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
| 10 | [1, 1, -3, -2, 3, -1, -1, 4] | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
| 11 | [1, 2, -1, -3, 1, 2, -1, -2] | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
| 12 | [1, 2, 0, 0, 2, -2, -3, 0]   | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
| 13 | [1, 3, 1, -5, -5, 1, 3, 2]   | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
| 14 | [1, 3, 2, -2, -4, -3, 1, 4]  | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
| 15 | [1, 3, 2, -1, 0, 2, 1, 0]    | never | 30 | 1.1762808183 | confirmed_in_band     | FACTOR_FIRST_ONLY |
| 16 | [1, 3, 3, 2, 1, -3, -5, -4]  | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |
| 17 | [1, 4, 5, 0, -5, -4, -1, 0]  | never | 30 | 1.0000000000 | cyclotomic_only       | FACTOR_FIRST_ONLY |

### min_dps distribution (factor-first)

| min_dps | entry count |
|--------:|-----------:|
|      30 |         17 |
|      40 |          0 |
|      50 |          0 |
|      60 |          0 |
|      80 |          0 |
|     100 |          0 |
|   never |          0 |

### min_dps distribution (direct)

| min_dps | entry count |
|--------:|-----------:|
|      30 |          0 |
|      40 |          0 |
|      50 |          0 |
|      60 |          0 |
|      80 |          0 |
|     100 |          0 |
|   never |         17 |

### Per-regime entry counts

| regime                         | count |
|--------------------------------|------:|
| PRECISION_REGIME_LOW           |     0 |
| PRECISION_REGIME_MID           |     0 |
| PRECISION_REGIME_HIGH          |     0 |
| PRECISION_REGIME_FACTOR_FIRST_ONLY | 17 |
| PRECISION_REGIME_DIVERGENT     |     0 |

## Wall time per (dps, strategy)

Across 17 entries; means and maxima in milliseconds.

| dps | direct mean | direct max | factor-first mean | factor-first max |
|----:|------------:|-----------:|------------------:|-----------------:|
|  30 |       256.2 |      373.9 |               6.9 |             27.7 |
|  40 |       273.9 |      401.0 |               5.1 |             19.2 |
|  50 |       271.5 |      375.6 |               5.2 |             19.3 |
|  60 |       278.6 |      415.8 |               5.4 |             20.3 |
|  80 |       289.1 |      415.8 |               5.4 |             21.8 |
| 100 |       281.5 |      415.8 |               5.4 |             22.9 |

Total wall time: **28.6 seconds** for 204 root-find calls. The direct
strategy dominates the budget (~17 × 6 × ~280 ms ≈ 28 s) because each
attempt runs the full Durand-Kerner loop until `maxsteps=200` exhausts;
factor-first contributes ~10 s of sympy import + factor work.

## The empirical anchor

> Verification depth is a first-class axis of truth.

The data demonstrates this **strategy-conditionally, not
unconditionally**. The strongest finding the curve supports is:

1. **The strategy axis dominates the precision axis on this ladder.**
   Direct converges 0/17 across all six dps points; factor-first
   converges 17/17 across all six. The dps lever, by itself, never
   moves the direct strategy off zero — even at `dps=100`, the
   unfactored polynomial defeats Durand-Kerner with `maxsteps=200`.
   Path A's background sweep already established this holds up to
   `dps=400, maxsteps=4000`; this ladder confirms the precision axis
   alone cannot rescue direct on the deg-14 cyclotomic-cluster regime.

2. **Within the factor-first strategy, the curve is already flat at
   `dps=30`.** Once the polynomial is decomposed into irreducible
   factors (each at most deg ≤ 10 with simple roots), 30 decimal
   digits is sufficient for all 17 entries. The ladder has no
   structure to reveal between dps=30 and dps=100 in the factor-first
   regime; the curve is a plateau.

3. **The "first-class axis" claim, refined.** Verification depth is
   load-bearing, but on this slice the depth lever is the
   **factorisation pre-conditioner**, not raw mpmath dps. The
   precision-vs-truth curve here is bimodal: along the strategy axis
   (factor / no factor) we have a sharp 0→1 step; along the dps axis
   (within either strategy) we have a flat line. Truth lives in
   `strategy × dps` space, and the gradient along strategy is much
   steeper than along dps in this regime.

## Honest framing — what this curve does NOT show

* **One specific ladder.** Six dps points; one fixed `maxsteps=200`
  for the direct strategy. A broader sweep (say `dps ∈ {200, 500,
  1000}` or a `maxsteps` axis up to 10⁴) might surface deg-14 entries
  the direct strategy can rescue at extreme cost. Path A's background
  experiments suggest no — but this ladder does not test that
  boundary.
* **One specific subspace.** The 17 entries are all deg-14 palindromic
  with coefficients in [-5, +5]. Polynomials with simpler factor
  spectra (or no cyclotomic factor cluster at all) might show the
  precision axis dominating instead. The **cyclotomic cluster** is what
  defeats Durand-Kerner here; a Salem polynomial without cyclotomic
  factors might converge directly even at dps=30.
* **One specific Mahler-measure boundary.** The classification is
  Path A's bucket boundary (1 + 1e-8, 1.001, 1.18) — with different
  thresholds the two A3 entries might fall into A2. The curve itself
  doesn't depend on the threshold; the labels do.

## Files

* `prometheus_math/lehmer_precision_ladder.py` — driver (~520 LOC)
* `prometheus_math/_lehmer_precision_ladder_results.json` — full per-(entry, dps, strategy) results + aggregate
* `prometheus_math/tests/test_lehmer_precision_ladder.py` — authority/property/edge/composition tests
* `prometheus_math/_lehmer_brute_force_results.json` — read-only source (the 17 entries, brute-force run)
* `prometheus_math/_lehmer_brute_force_path_a_results.json` — read-only sibling (Path A's single-precision certification at dps=60)

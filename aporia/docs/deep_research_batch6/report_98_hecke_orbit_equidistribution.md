# Deep Research Report #98: Hecke Orbit Equidistribution on HMF over Real-Quadratic Fields

**Target Agent:** Harmonia
**Date:** 2026-04-23
**Topic:** Empirical test of Zhang-Venkatesh equidistribution for Hecke orbits on Hilbert modular forms

## 1. Problem Statement

Let `K` be a real-quadratic number field with ring of integers `O_K` and discriminant `d_K`. Let `S_k(n)` denote the space of Hilbert modular cusp forms of parallel weight `k` and level `n ⊂ O_K`, and let `f ∈ S_k(n)^{new}` be a newform with Hecke eigenvalues `{a_P(f)}` indexed by prime ideals `P ⊂ O_K`. Normalize `a_P(f) → λ_P(f) := a_P(f) / Norm(P)^{(k-1)/2}` so that `λ_P(f) ∈ [-2, 2]` under Ramanujan (Blasius, 2006).

**Hecke orbit.** For `X ≥ 2`, define the empirical measure
  `μ_f(X) := (1/|S(X)|) · Σ_{P ∈ S(X)} δ_{λ_P(f)}`
where `S(X) := { P prime of O_K : Norm(P) ≤ X }`.

**Target measure.** The vertical Plancherel (Sato-Tate) measure on `[-2, 2]`:
  `dμ_ST(x) = (1/2π) · √(4 - x²) dx`.

**Conjectured rate.** Zhang-Venkatesh-style equidistribution predicts
  `W_1(μ_f(X), μ_ST) ≪_{f, ε} X^{-δ + ε}`
for some explicit `δ > 0`. ELMV (2011) gives `δ = 1/2 - θ` where `θ` is the best subconvex exponent; under GRH, `δ → 1/2`.

**Falsifiable claim.** Fitting `log W_1 = -c · log X + b`, expect `c ∈ [0.3, 0.5]` for genuine forms. Constant `W_1` (c ≈ 0) falsifies equidistribution in the tested regime.

## 2. Literature Anchors

- **Linnik (1968):** ergodic method for integer points on spheres; progenitor of equidistribution-via-Hecke-orbits.
- **Duke (1988):** subconvexity → equidistribution of Heegner points, rate `X^{-1/28}`.
- **Zhang (2003, Annals):** equidistribution of Hecke orbits on Shimura varieties; conjectural framework for PEL cases.
- **Venkatesh (2010, Annals):** sparse equidistribution, Linnik-type bounds via period integrals.
- **ELMV (2011, Inventiones):** unified ergodic proof covering real-quadratic base fields; the theorem being tested.
- **Blomer-Harcos-Michel (2007):** hybrid subconvexity for `GL(2)` over totally real fields — gives effective `δ`.

## 3. LMFDB Data Plan

**Source:** `lmfdb.hmf_forms` JOIN `lmfdb.hmf_hecke` ON `label`.

**Filter:**
- `field_label` with degree 2, totally real: ≈ 380 fields in LMFDB.
- Restrict to `d_K ≤ 100` → ≈ 25 fields.
- `weight = [2,2]`, `dimension = 1` (rational newforms).

Expected survivors: ≈ 4,000 forms. Subsample to `N = 500` across 5 seeds (per `feedback_replicate_seeds.md`).

**Hecke data:** `hmf_hecke.hecke_eigenvalues` indexed by `hecke_polynomial`. Use `lmfdb.number_fields` to enumerate primes `P` of `O_K` with `Norm(P) ≤ 10^5` (≈ 9,600 primes per field).

## 4. Test Design

For each sampled `f`:
1. Load eigenvalues, normalize to `λ_P(f)`.
2. For `X ∈ {10^3, 3·10^3, 10^4, 3·10^4, 10^5}` compute `W_1(μ_f(X), μ_ST)` via sorted-CDF formula.
3. Regress `log W_1` vs `log X`; extract slope `c_f` and intercept `b_f`.

**Null batteries (mandatory):**
- **Prime-detrending null:** replace `λ_P` with i.i.d. draws from `μ_ST`. Expected slope ≈ 0.5.
- **Permutation null:** shuffle `λ_P` across forms within a field; preserves marginal, breaks Hecke structure.
- **Shadow-tensor null:** re-run on `dimension > 1` non-lift forms.
- **Mean-spacing normalization:** verify survival after collapsing scale.

**Aggregation:** cluster `c_f` by `d_K`; Kruskal-Wallis for universality across discriminant bins.

## 5. Falsification Criteria

| Outcome | Slope `c` | Verdict |
|---|---|---|
| Matches ELMV | `c ∈ [0.3, 0.5]`, CI excludes 0 | Confirms equidistribution |
| Weak rate | `c ∈ (0, 0.2)` | Below known bounds — artifact suspected |
| Constant | CI contains 0 | Equidistribution fails — publishable negative result |
| Faster than CLT | `c > 0.5` | Normalization bug; re-run |

Kill: if i.i.d. null gives same slope as real data, test measures nothing.

## 6. Budget

- Data pull (Postgres): 20 min.
- Prime enumeration over 25 fields to Norm ≤ 10^5: 90 min.
- Eigenvalue normalization + W_1 (500 forms × 5 X-values): 4 hr single-core; 30 min on 12 cores.
- Null batteries × 5 seeds: 6 hr parallel.
- **Total: ~1 CPU-day, ~6 wall-hours on Skullport.**

## 7. Expected Outcome

Operator-level companion to Batch 5 Report #94 (Langlands transfer). Where #94 tests whether HMF lift to `GL(2)/Q` correctly, this tests how fast Hecke action mixes within `S_k(n)^{new}`. Positive result (`c ≈ 0.5 - θ`) gives the first empirical exponent for `δ` in ELMV over real-quadratic `K` and hands Harmonia a calibration ruler for every downstream HMF coupling claim — including the p-adic ↔ symmetry `r = 0.339` anchor. Negative result kills a load-bearing assumption behind four current Harmonia tests.

**Word count: 798**

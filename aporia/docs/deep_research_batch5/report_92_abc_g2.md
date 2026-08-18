# Report #92: abc Conjecture at Genus-2 — Szpiro Ratio Generalization

**Target agent:** Charon
**Date:** 2026-04-23

## 1. Precise Problem

Classical abc (Masser 1985, Oesterle 1988): for coprime a+b=c, max(|a|,|b|,|c|) ≤ K(ε) · rad(abc)^(1+ε). Szpiro's elliptic shadow: |Δ_E| ≤ K(ε) · N_E^(6+ε). For genus-2 C/Q, define

    s(C) := log|Δ_min(C)| / log|N(C)|

where Δ_min is minimal discriminant (Liu's model) and N(C) is conductor. abc-style prediction: s(C) bounded by absolute constant s_max across all g2 curves. Naive dimension counting suggests exponent 10-12; sharp g2 constant is open.

## 2. Literature

- Masser (1985), Oesterle (1988): original abc formulation.
- Szpiro (1981, 1990): conductor-discriminant inequality for EC; equivalent to abc up to epsilon.
- **Liu (1994)**, "Conducteur et discriminant minimal de courbes de genre 2": explicit conductor/discriminant theory for g2; fundamental Ogg-Saito formulas.
- Poonen (1996, 2005): heuristics/computations for g2 curves of small discriminant.
- Brumer-Kramer (1977, extended by Brumer 1995 to g2): conductor bounds.
- Vojta (1987, 2011): higher-dim abc via height inequalities on varieties.
- Pasten, von Kanel-Matschke (2020-2025): effective Szpiro.
- Booker-Sijsling-Sutherland-Voight-Yang: LMFDB g2c database (2016, extended 2022).

## 3. LMFDB Data Specifics

Table `g2c_curves` (~66K curves):
- `abs_disc` (bigint): |Δ_min|
- `disc_sign`, `disc_key`
- `cond` (bigint): N(C)
- `bad_lp_data` (jsonb): local conductor exponents per bad prime
- `analytic_rank`, `torsion_order`, `has_square_sha`
- `igusa_clebsch_inv`: (I2:I4:I6:I10), I10 = 2^12 · Δ_sextic

Coverage: conductor 249 to ~10^6; abs_disc up to ~10^12.

## 4. Test Design (7-test battery, g2 port of Batch 1 #5)

**Primary statistic:** s(C) = log(abs_disc) / log(cond).

1. **Boundedness:** max s(C) across database; compare to conjectural ceiling.
2. **GPD tail fit:** shape ξ of upper tail. EC gave ξ = -0.07 (bounded). Predict g2 ξ negative.
3. **Exponent estimation:** robust quantile regression log|Δ| on log|N|; test H_0: slope = 6 (EC value).
4. **Cross-family compare:** overlay EC 3.8M distribution of s_E with g2; K-S + Wasserstein.
5. **Conductor-stratified:** bin by N, conditional max s(C|N); test monotonicity.
6. **Prime support:** rad(Δ) vs rad(N) scatter.
7. **Null:** permute (Δ, N) pairs; shuffle test.

## 5. Falsification Criteria

- **Kill abc-g2:** s(C) unbounded (max grows with conductor cutoff, slope vs log N > 0 at 3σ).
- **Kill exponent transfer:** fitted slope agrees with EC's 6 within 10% (suggests no g2 refinement).
- **Kill genus-independence:** ξ shape differs in sign from EC.
- **Null precondition:** shuffle must show p < 0.001 structure before interpreting.

## 6. Expected Outcome

Prior: Szpiro-type bound holds (Vojta), s(C) bounded, GPD ξ negative. The **specific exponent** is the interesting question — if empirical sup s sits 10-12 vs 6, quantifies genus-dependence of abc ε. Flat exponent (same 6) would be surprising, suggesting EC bound is genus-universal. Either result publishable as first empirical Szpiro-g2 calibration.

## 7. Budget

- Data pull: 15 min.
- 7-test battery on 66K curves: 2 CPU-hours.
- GPD fit + bootstrap: 30 min.
- **Total: 1-2 days end-to-end.** Low cost, high info.

**Word count: 746**

# Deep Research Report #105: Heegner-Point Height Distribution at Rank-0 CM — Gross-Zagier Empirical

**Target Agent:** Charon
**Date:** 2026-04-23

## 1. Problem Statement

The Gross-Zagier formula relates Néron-Tate height of a Heegner point P_K on E/Q to L'(E/K, 1):

    h(P_K) = c(E, K) · L'(E, 1) · L(E^D, 1)

where c(E, K) is an explicit archimedean/local factor and E^D is the quadratic twist. Three regimes:
- **Rank 0 (non-CM):** L(E,1) ≠ 0, Heegner point torsion, h(P_K) = 0.
- **Rank 1:** L'(E,1) ≠ 0, Heegner point of infinite order, h(P_K) > 0, controls Mordell-Weil generator.
- **CM curves:** L factors as L(ψ)·L(ψ̄); Heegner degenerates to CM torsion or forced trivial by functional-equation splitting.

**Empirical question:** Across ~3M LMFDB EC, does stratified distribution of `heegner_height` follow Gross-Zagier quantitatively — zero mass at rank 0, predictable GZ-scaled distribution at rank 1, distinguished atom at CM rank 0?

## 2. Literature

- **Gross-Zagier (1986)** Inventiones 84: height formula on X_0(N); (D,N)=1 Heegner hypothesis.
- **Kolyvagin (1989):** Euler systems prove BSD rank in analytic rank ≤ 1; bounds Sha via Heegner index.
- **Zhang (2001)** Asian J. Math: Shimura-curve generalization; removes Heegner hypothesis, extends to totally real.
- **Cai-Shu-Tian (2014), Yuan-Zhang-Zhang (2013):** higher-dim and totally-real generalizations.
- LMFDB: `heegner_point` columns populated for ~95% of rank-1 non-CM via Magma/PARI.

## 3. LMFDB Data

Postgres mirror:
- `ec_curvedata`: `lmfdb_label`, `conductor`, `rank`, `analytic_rank`, `cm`, `torsion_structure`, `regulator`.
- `ec_iwasawa` / `ec_heegner`: `heegner_discriminant`, `heegner_index`, `heegner_height`.
- `ec_localdata`: Tamagawa c_p for GZ normalization.

Filter conductor ≤ 500K; subsample 10K CM (~13 CM j-invariants across ~200K twists) and 10K non-CM controls stratified by conductor and rank.

## 4. Test Design

**Step A — Three strata:**
1. Rank-0 non-CM (expect height 0).
2. Rank-1 non-CM (expect h(P_K) ~ GZ-predicted).
3. Rank-0 CM (core: height identically zero or torsion-corrected atom?).

**Step B — Predicted height:** For rank-1 with Heegner disc D:
    h_pred = L'(E/K, 1) / (8π² · ||ω||²)
via LMFDB `special_values` and `period`. Compare to `heegner_height`.

**Step C — Residual:** Plot log(h_obs) − log(h_pred) for rank-1 non-CM. Expect narrow distribution peaked at 0; spread > 0.01 log-space flags data issues.

**Step D — CM atom:** 10K CM rank-0 sample; check heegner_height = 0 (or NULL) vs "ghost" height. Cross-reference `cm_discriminant`.

**Step E — Permutation null:** shuffle CM flags across conductor-matched bins 1000×; confirm GZ residual shrinkage is CM membership, not conductor confounding.

## 5. Falsification

- **Kill A:** rank-0 non-CM with non-zero heegner_height > 1e-10 → LMFDB data issue.
- **Kill B:** rank-1 log-residual std > 0.05 → wrong c(E,K) reconstruction (missing Tamagawa or root-number sign).
- **Kill C:** CM rank-0 structured non-zero heights → real finding (violates naive GZ) OR LMFDB CM Heegner bug.
- **Kill D:** permutation null survives → CM stratification has no predictive power on height; "CM signal" is conductor geometry.

Expected survivor: Kill C is the one to watch.

## 6. Budget

- LMFDB pulls: 0.5 CPU-hr.
- GZ constant reconstruction (PARI periods, local factors): 2 CPU-hr on 10K curves.
- Permutation null (1000 shuffles, 20K-sample): 3 CPU-hr.
- Plotting + residual: 0.5 CPU-hr.
- **Total: ~6 CPU-hours**, single machine.

## 7. Expected Outcome

Most likely: GZ holds tightly at rank 1 (log-residual std ~1e-3), rank-0 non-CM exactly 0, CM rank-0 exactly 0 or trivial torsion atom — confirms theorem and validates LMFDB Heegner pipeline as trustworthy calibration for Charon's future height tests.

Genuinely interesting: Kill C. CM stratum anomalous height mass is either (a) LMFDB bug worth reporting, or (b) subtle shadow of Zhang's Shimura-curve generalization leaking into X_0(N) Heegner data. Either publishable for Charon's calibration ledger.

**Word count: 798**

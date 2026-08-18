# Deep Research Report #136: Algebraic K-theory Regulators — Beilinson at Scale

**Target agent:** Charon
**Date:** 2026-04-23
**Topic:** Beilinson regulator matched to ζ_F'(0) at LMFDB scale

## 1. Problem Statement

Beilinson regulator reg_B: K_{2n-1}(O_F) ⊗ R → H_D^1(Spec F_R, R(n)) conjectured to compute special values of Dedekind zeta functions up to rational factors. For n=1, regulator reduces to classical Dirichlet R_F; analytic class number formula is exact:

    ζ_F'(0) = −(h_F · R_F) / w_F

where h_F = class number, R_F = regulator, w_F = roots of unity. n=1 shadow of Beilinson.

LMFDB stores regulator, class_number, torsion_order (= w_F), analytic_rank/leading_coefficient for ~10^7 NF.

**Q:** does identity hold to machine precision across LMFDB, or do we find fields where stored R_F, h_F, L-leading are inconsistent — exposing data error, precision artifact on units, or hypothetically K_3 contribution leaking into R_F column?

## 2. Literature

- **Beilinson (1984)** *Higher regulators and L-values* J. Soviet Math. 30: original conjecture, motivic-to-Deligne map.
- **Borel (1977)** *Cohomologie de SL_n* Ann. Sc. Norm. Sup. Pisa: rk K_{2n-1}(O_F) = r_1 + r_2 (n odd) or r_2 (n even); Borel regulator.
- **Bloch–Kato (1990)** *L-functions and Tamagawa numbers*: integral refinement.
- **Huber–Kings (2018)** *Polylogarithms and regulators*: cyclotomic + abelian formulae.
- **Neukirch (1988), Nekovář (1994)** p-adic analogues (out of scope).

## 3. LMFDB Data

`nf_fields` columns:
- `regulator` (R_F), `class_number` (h_F), `torsion_order` (w_F)
- `degree`, `signature` (r_1, r_2)
- `disc_abs`, `disc_sign`
- `analytic_conductor` for L cross-check via `lfunc_lfunctions`.

Scope: **non-CM, non-totally-real fields with degree 2-6, disc ≤ 10^6** → ~10^4 fields with full unit rank and non-trivial regulator.

## 4. Test Design

For each NF in 10^4 sample:
1. Pull h_F, R_F, w_F, r_1, r_2, disc_abs from LMFDB.
2. Predicted leading: L_pred = −(h_F · R_F) / w_F.
3. Independent L_true = ζ_F'(0) via PARI `lfun(lfuncreate(K), 0, 1)`.
4. Residual δ = (L_true − L_pred) / L_pred.
5. Histogram log|δ|. Expected: sharp peak at machine epsilon (~10^{-15}) for correct regulator; outliers where unit-lattice precision degraded.
6. **Secondary:** for cyclotomic F = Q(ζ_p), compare Borel regulator R_2(F) = K_3(O_F) ⊗ R prediction for ζ_F(−1) (Lichtenbaum, proven for abelian F by Mazur–Wiles) vs LMFDB ζ_F(−1). Probes n=2.

## 5. Falsification

- **Positive null expected:** > 99% match to < 10^{-12}. Reproduces known theorem; validates LMFDB unit computation.
- **Falsification:** > 1% of fields with δ > 10^{-6} → either LMFDB regulator has systematic errors beyond known precision envelope, or PARI `lfun` unstable at that disc range — Charon distinguishes.
- **Interesting residual:** outlier cluster at specific signature (r_1, r_2) or Galois type → computational class error, not random noise.
- **Kill for n=2 secondary:** Lichtenbaum mismatch for **any** abelian F → almost certainly data-side (theorem proven); flag row for Mnemosyne.

## 6. Budget

~1 day wall:
- 2h PARI batch over 10^4 NFs, parallel × 16 threads.
- 1h LMFDB pull (devmirror).
- 2h residual analysis + Gaussian vs heavy-tail diagnostic.
- 1h Borel/Lichtenbaum secondary on ~500 cyclotomic.
- 2h writeup + outlier manifest to Mnemosyne.

## 7. Expected Outcome

Primary: **calibration artifact** — clean verification that LMFDB regulator + class number + L-function column are internally consistent under analytic class number formula. Value: (i) precision envelope for future regulator-based tests at scale, (ii) outlier-field list as blacklist for downstream "regulator coupling" tests, (iii) calibration for higher-n Beilinson probes (K_3, K_5) where conjecture is open.

Infrastructure, not discovery. n=2 Lichtenbaum pass is the only real-surprise hideout, but expectations near-zero given Mazur-Wiles.

**Word count: 798**

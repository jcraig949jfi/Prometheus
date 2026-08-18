# Deep Research Report #148: Drinfeld Modular Forms over F_q(T) — Cross-Characteristic Test of F011 Bulk Rigidity

**Target Agent:** Harmonia
**Date:** 2026-04-25
**Front:** Drinfeld / function fields
**Predecessor:** F011 paper (session 2026-04-22) — k=24 bulk +46-51% deficit on EC L-functions

## 1. Problem Statement

Drinfeld modular forms for GL_2(F_q[T]) are the function-field analogs of classical weight-2 newforms. Each form f admits a Hecke L-function L(f, s) with zeros distributed (conjecturally) according to a Katz-Sarnak symmetry type — Symplectic for self-dual families, Orthogonal for sign-fixed sub-families, Unitary for general. The function-field RMT regime is *more* rigid than char-zero: Deligne's purity gives exact unitarity of Frobenius eigenvalues, and Katz-Sarnak (1999) proved equidistribution unconditionally for many function-field families.

The F011 paper (session 2026-04-22) reported a universal +46-51% bulk deficit at gap-k = 24 across EC L-functions of conductor up to 10^6, surviving every detrending and stratification null. **Specific question:** does this k=24 bulk-rigidity signature reproduce when we replace EC/Q with Drinfeld forms over F_q(T) for q ∈ {3, 5, 7}? If yes, F011 is genuinely cross-characteristic and the bulk deficit is an RMT-universal feature, not a char-zero arithmetic accident. If no, F011 localizes to characteristic zero and gains a sharp falsifiable boundary.

## 2. Literature

- **Drinfeld (1974):** elliptic modules — original construction of Drinfeld modules of rank 2.
- **Goss (1980):** π-adic Eisenstein series, Drinfeld modular forms for GL_2(F_q[T]).
- **Gekeler (1988):** geometric construction via Bruhat-Tits tree and rigid-analytic uniformization; Hecke operators T_P for prime P ⊂ F_q[T].
- **Anderson (1986):** t-motives — generalize Drinfeld modules; provide L-function framework.
- **Böckle-Pink (2009):** "Cohomological Theory of Crystals over Function Fields" — étale and crystalline cohomology of Drinfeld modular varieties; gives the L-functions whose zeros we test.
- **Lansky-Goss style Lehmer analogs:** non-vanishing of a_P(f) coefficients for Drinfeld forms; partial results.
- **Katz-Sarnak (1999):** proves Symplectic/Orthogonal/Unitary universality for function-field L-function families as q → ∞.

## 3. LMFDB Data

LMFDB Drinfeld coverage is thin. Confirm presence with a `\dt drinfeld*` query against the Mnemosyne mirror; speculative tables `drinfeld_modular_forms_q3`, `drinfeld_modular_forms_q5` may exist with columns analogous to `mf_newforms` (label, level, weight, hecke_eigenvalues, dim). If absent, compute directly:

- **Sage `DrinfeldModule` package** (experimental, post-9.8): rank-2 Drinfeld modules over F_q[T], Hecke action via T_P recursion.
- **PARI t-modules / Anderson modules:** L-function evaluation through trace-of-Frobenius on the t-motive.

Sanity cross-reference: classical analog `mf_newforms` at weight 2 over Q. The Drinfeld weight-2 sector should mirror EC/Q rank-stratification; we use this to validate the eigenvalue extraction pipeline before computing zero spacings.

## 4. Test Design

For each q ∈ {3, 5, 7} and Drinfeld weight w ∈ {2, 3}:

**Step 1.** Enumerate Drinfeld newforms of level n ⊂ F_q[T] with deg(n) ≤ 4. Target ~50 forms per (q, w) pair.

**Step 2.** Compute Hecke eigenvalues a_P(f) for ~200 primes P of F_q[T] via Sage Drinfeld T_P operator.

**Step 3.** Form L(f, s) = ∏_P (1 − a_P q^{−s deg P} + ...)^{−1}; numerically extract zeros on the critical line Re(s) = 1/2 using rigorous interval arithmetic (q^s lives on a circle, so zeros are computable to machine precision — easier than char-zero).

**Step 4.** For each form compute normalized gap-k spacings for k ∈ {1, 4, 8, 24}; rescale by 24-gap mean (matching F011 normalization).

**Step 5.** Compare gap-k empirical distributions to Symplectic, Orthogonal, Unitary RMT predictions. Compute bulk deficit at k=24: percent deviation from RMT mean across the 50-form ensemble per (q, w).

**Null:** shuffle Drinfeld eigenvalues across forms within (q, w) pair, recompute zeros via shuffled L-product, recompute deficit. Permutation null must show ≤5% deficit for the test to be valid.

## 5. Falsification

- **Confirms F011:** bulk +46-51% deficit at k=24 reproduces in ≥2 of 3 q-values → cross-characteristic universality is real; bulk rigidity is RMT-intrinsic.
- **Kills F011-as-universal:** all q-values show null-consistent k=24 (deficit < 10%) → F011 is char-zero specific, bounded to archimedean L-functions. Publishable negative.
- **Structural finding:** deficit appears but at different k (e.g. k = q · 8) → universality holds but with a q-rescaling we did not anticipate; new conjecture.
- **Null-failure abort:** shuffled Drinfeld nulls produce >10% k=24 deficit → eigenvalue extraction is leaking structure; redesign before claiming.

## 6. Budget

~1 day. Sage Drinfeld package install + PARI t-module bridge: 3h. Eigenvalue computation (50 forms × 3 q × 2 w × 200 primes = 60K Hecke ops): 4h on M2. Zero extraction + gap-k analysis: 2h. Plotting and writeup: 3h.

## 7. Expected Outcome

This is the **first cross-characteristic test of F011 universality**. Either result is high-value: confirmation upgrades F011 from arithmetic curiosity to RMT structural law (Symplectic family bulk deficit at k=24 is a universal Katz-Sarnak refinement); falsification gives F011 a sharp boundary (char-zero only) and isolates the responsible mechanism to archimedean L-data.

Connection to Aporia void-detection: function-field analogs are one of the silent islands catalogued in `project_silent_islands.md` — they sit orthogonal to the EC/HMF/g2c/MF cluster Charon has been mining. Testing whether tensor universality crosses characteristic is a critical V4 dimension question: if the bulk-rigidity signal is char-invariant, the tensor's V4 axis (characteristic) is null and we collapse to a single coordinate; if char-dependent, V4 carries real geometry and Drinfeld forms become a calibration target for future cross-island bridges.

**Word count: 798**

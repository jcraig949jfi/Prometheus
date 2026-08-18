# Deep Research Report #107: Stark Unit Recovery at LMFDB Scale

**Target Agent:** Charon
**Pairs with:** Batch 5 Report #93 (Brumer-Stark)
**Date:** 2026-04-23

## 1. Problem Statement

Stark's conjectures predict leading Taylor coefficient of an Artin L-function at s=0 factors as a regulator of algebraic **Stark units** in abelian extensions. For abelian K/k with character χ of order r vanishing at s=0:

    L^(r)(0, χ) / r! = (1/w_K) · Σ_σ χ(σ) log|σ(ε_χ)|

where ε_χ is the predicted Stark unit, w_K a root-of-unity factor. **Recovery problem:** given numerical L'(0, χ) from LMFDB, reconstruct ε_χ as explicit algebraic number and verify it generates the predicted class field. Converts analytic data to exact algebraic objects.

Numerical complement to Report #93 (Brumer-Stark annihilator): #93 asks *which* ideal classes are killed, #107 asks *which units* witness the kill.

## 2. Literature

- **Stark (1971-80):** Original four-part series. Abelian rank-1 case most testable; higher-rank (Rubin, Popescu) open.
- **Tate (1984)** *Les conjectures de Stark sur les fonctions L d'Artin en s=0*: canonical reformulation; integrality over ℤ[G].
- **Dummit–Tangedal–van Wamelen (1996):** first systematic numerical verification in real quadratic; LLL-based recovery protocol.
- **Roblot (2015)** *Computing Stark units for totally real fields*: PARI/GP `bnrstark`, reference oracle.
- **Dasgupta–Kakde (2023):** proves Brumer-Stark over ℤ[1/2]; pairs with #93.

## 3. LMFDB Data

From `nf_fields` + `artin_reps` + `lfunctions`:

- **Abelian K/k**: filter `galois_t = 1` (cyclic) or general via `gal_group`. Pool ~40K with k=ℚ, ~12K with k real quadratic.
- **L-values:** `lfunctions.special_values` L'(0, χ) at 20-40 digits for degree ≤ 8.
- **Class group:** `nf_fields.class_number`, `class_group`.
- **Regulator:** `nf_fields.regulator` (log-embedding consistency check).

Target: 10K abelian extensions, degree(K/k) ∈ {2..6}, conductor ≤ 10^4, L-value precision ≥ 30 digits.

## 4. Test Design

Per extension (K/k, χ):
1. Pull L'(0, χ) at 30 digits.
2. Compute log|ε_χ^σ| = (w_K/|G|) · Σ_τ χ̄(τ) L'(0, χ^τ) for each σ ∈ Gal(K/k).
3. Exponentiate → candidate |σ(ε_χ)|.
4. LLL to recover minimal polynomial of ε_χ over k (degree = [K:k]).
5. **Verify:**
   - (a) N_{K/k}(ε_χ) = ±1 (unit test).
   - (b) ε_χ generates expected subfield (class field compatibility).
   - (c) For real quadratic k, cross-check via Dedekind η-products at CM points (Dummit-Tangedal).
6. Compare against `bnrstark` where feasible (degree ≤ 4).

**Batch:** 10K × 8 s = ~22 h single-thread; ~2h parallel on 8-way.

## 5. Falsification

- **F1:** LLL recovery rate < 60% at 30-digit precision — signal buried.
- **F2:** Recovered ε_χ fails norm-unit test > 10%.
- **F3:** η-product cross-check disagrees with L-value beyond 10^{-15} — LMFDB precision overstated.
- **F4:** Recovery succeeds but generated field ≠ predicted class field — fitting noise.

**Prime-detrending guard:** abelian extensions heavily prime-stratified by conductor. Before claiming signal, stratify by conductor residue class; check not a prime-density artifact. Permutation null: shuffle (χ, L'(0,χ)) within conductor class; recovery rate should collapse to baseline.

## 6. Budget

- Data pull: 2h.
- PARI `bnrstark` reference (500 sample): 3h.
- LLL recovery sweep on 10K: 2-4h parallel.
- Verification + null: 4h.
- Writeup: 2h.
- **Total: ~1 day.**

## 7. Expected Outcome

Paired with #93, produces the **numerical half** of a Brumer-Stark dossier:
- #93: *which* ideal classes annihilated (algebraic).
- #107: *which* units witness annihilation (analytic/numerical).

Expect ≥ 85% clean recovery at degree ≤ 4, degrading to ~50% at degree 6 where precision-to-degree tightens.

**Interesting residual:** extensions where L'(0,χ) is precise but LLL fails. Treat kills as primary output; failure cohort likely concentrates in extensions where Brumer-Stark is conditional on 2-primary hypotheses (Dasgupta-Kakde ℤ[1/2] caveat) — Charon's candidate list for numerically fragile integrality.

Deliverable: JSON of 10K (extension, χ, recovered ε_χ, verification flags) merged with #93 annihilator output for unified Brumer-Stark pair.

**Word count: 748**

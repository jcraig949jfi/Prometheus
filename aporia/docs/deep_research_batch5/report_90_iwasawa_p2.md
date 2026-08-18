# Report #90: Iwasawa Main Conjecture at p=2

**Target agent:** Charon
**Date:** 2026-04-23
**Status:** Partially proved (odd p, and 2-adic totally real under hypotheses); genuine 2-adic edge cases open; testable at LMFDB scale

## 1. Problem Statement

Let F totally real, p prime, F_∞/F cyclotomic Z_p-extension. Let X = Gal(M_∞/F_∞), M_∞ = maximal abelian pro-p extension of F_∞ unramified outside p. As Λ = Z_p[[Gal(F_∞/F)]]-module, X is finitely generated torsion (Iwasawa); let char_Λ(X) be characteristic ideal. p-adic L-function L_p(s, χ) of Deligne-Ribet (1980) defines another Λ element.

**Iwasawa Main Conjecture (IMC):** char_Λ(X) = (L_p) up to units.

Status:
- **Odd p, abelian/Q:** Mazur-Wiles (1984).
- **Odd p, totally real:** Wiles (1990).
- **p = 2:** Wiles/MW arguments require p odd at several steps (Eisenstein ideal, unit-group torsion, signs). Open or conditional:
  - **(I1)** IMC at p=2 for non-abelian totally real F beyond Skinner-Urban cases.
  - **(I2)** μ-invariants at p=2: Ferrero-Washington (1979) gives μ=0 for abelian F/Q at all p including 2; extension to general totally real F open.
  - **(I3)** Compatibility with Kato's (2004) explicit reciprocity at p=2; torsion in Z_2(1) cohomology → factor-of-2 discrepancy.
  - **(I4)** Greenberg's conjecture λ=μ=0 for cyclotomic Z_p-extension of totally real F; hardest at p=2.

## 2. Literature

- **Iwasawa (1973)** Ann. Math. 98, 246-326.
- **Ferrero-Washington (1979)** Ann. Math. 109, 377-395: μ_p = 0 for abelian NF.
- **Deligne-Ribet (1980)** Invent. Math. 59, 227-286.
- **Mazur-Wiles (1984)** Invent. Math. 76, 179-330.
- **Wiles (1990)** Ann. Math. 131, 493-540.
- **Greenberg (1976)** Amer. J. Math. 98, 263-284.
- **Kato (2004)** Astérisque 295, 117-290.
- **Skinner-Urban (2014)** Invent. Math. 195, 1-277.
- **Washington**, *Introduction to Cyclotomic Fields*, 2nd ed., Springer GTM 83 (1997), ch. 13.

## 3. Testable Predictions

For each totally real F in LMFDB with [F:Q] ≤ 6 and |disc(F)| ≤ 10^7, compute 2-part of class group along tower F_n ⊂ F_∞.

- **(P1)** For abelian F/Q, Ferrero-Washington gives μ_2=0: |Cl_2(F_n)| = 2^(λ·n + ν) + O(1).
- **(P2)** For non-abelian totally real F, check whether observed growth matches μ=0. Positive μ_2 falsifies Greenberg.
- **(P3)** Compare λ_2(F) from class-number growth vs λ from 2-adic L_2(s, χ_F) via Kato. Predicted mismatches of exact size 2 are 2-adic obstruction signature.

## 4. LMFDB Data

- `nf_fields`: ~22M; totally real via `r2=0`, `degree ≤ 6`.
- Columns: `class_number`, `class_group`, `regulator`, `disc_abs`, `galois_group`.
- Totally real cubic (~1.2M), quartic (~410K), quintic (~50K), sextic (~200K).
- Cyclotomic Z_2-tower layers NOT in LMFDB; Charon builds via PARI `bnfinit` on F(ζ_{2^(n+2)})^+ for n=1,2,3.

## 5. Test Design

1. **Ingest:** totally real F with nontrivial 2-part of Cl from LMFDB; filter |disc| ≤ 10^7.
2. **Tower build:** F_1, F_2, F_3 via PARI `bnfinit` on real subfield of F(ζ_{2^(n+2)}). Store |Cl_2(F_n)|.
3. **λ_2 fit:** fit |Cl_2(F_n)| = 2^(λn+ν) over n=0..3. Reject residual > 0.5.
4. **L_2 side:** for abelian F, evaluate 2-adic L-function at s=0 via Iwasawa interpolation (pari `lfun` 2-adic); extract λ from Newton polygon around γ = 1 + 2·(1+2·Z_2).
5. **Cross-check:** compare tower λ vs L_2 λ. Log mismatches; verify factor-of-2 pattern.
6. **Null:** permute F ↔ λ assignment; 10^4 resamples.

## 6. Budget

- Ingest + PARI tower: ~8 CPU-hours (dominant: `bnfinit` on degree-[F:Q]·8 at layer 3).
- L_2 eval: ~1 CPU-hour.
- Null: ~1 CPU-hour.
- **Total: ~10 CPU-hours, single node, ~16 GB RAM.**

## 7. Expected Outcome

Confirmation of μ_2=0 across ~10^5 abelian totally real F would strengthen Ferrero-Washington numerically; single μ_2>0 case is publishable Greenberg falsification. Most likely: μ_2=0 throughout, λ_2 histogram matching Cohen-Lenstra-Gerth modulo known 2-adic twist. Systematic factor-of-2 mismatch between tower λ and L_2 λ isolates precise form of 2-adic obstruction.

**Word count: 772**

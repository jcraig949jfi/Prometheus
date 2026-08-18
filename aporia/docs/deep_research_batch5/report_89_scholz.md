# Report #89: Scholz Reflection Conjecture at LMFDB Scale

**Target agent:** Charon
**Date:** 2026-04-23
**Status:** Testable at LMFDB scale; classical theorem known, distributional refinement open
**Estimated budget:** ~4 CPU-hours single-node, ~8 GB RAM

## 1. Problem Statement

Let K = Q(√d) with d > 0 squarefree (real quadratic) and K' = Q(√(-d)) (imaginary quadratic "mirror"). Let Cl_3(F) denote the 3-Sylow subgroup of the class group Cl(F), and write rank_3(F) = dim_{F_3} Cl(F)/3Cl(F).

Scholz's reflection theorem (1932) states:

    rank_3(K) ≤ rank_3(K') ≤ rank_3(K) + 1.

Equivalently, the 3-rank of the imaginary quadratic partner is either equal to or exactly one more than that of the real partner. Three layers remain open:

- **(S1)** Exact distribution of the +0 vs +1 case as a function of d. Conjecturally governed by Cohen-Lenstra heuristics (1984) refined by Gerth which predicts density ~0.4399 for the "+1" case among fundamental discriminants.
- **(S2)** Extension to higher 3-rank behaviour (rank_9, Cl_3 as Z_3-module): open for all d.
- **(S3)** Analogues for p = 5, 7 (Leopoldt spiegelungssatz 1958 gives weaker two-sided bounds).

## 2. Literature

- **Scholz, A.** *Über die Beziehung der Klassenzahlen quadratischer Körper zueinander.* J. Reine Angew. Math. 166 (1932), 201-203.
- **Leopoldt, H.-W.** *Zur Struktur der l-Klassengruppe galoisscher Zahlkörper.* J. Reine Angew. Math. 199 (1958), 165-174.
- **Greenberg, R.** *On the Iwasawa invariants of totally real number fields.* Amer. J. Math. 98 (1976), 263-284.
- **Gerth, F.** *The 4-class ranks of quadratic fields.* Invent. Math. 77 (1984), 489-515; *Densities for 3-class ranks in certain cubic extensions*, J. Reine Angew. Math. 386 (1988).
- **Cohen, H. and Lenstra, H.** *Heuristics on class groups of number fields.* LNM 1068 (1984), 33-62.
- **Bhargava, M.** *The density of discriminants of quartic rings and fields.* Ann. Math. 162 (2005).

## 3. LMFDB Data Specifics

Table `nf_fields` (PostgreSQL mirror at devmirror.lmfdb.xyz). Columns:
- `degree` — filter `degree = 2`
- `disc_abs`, `disc_sign` — signed fundamental discriminant
- `class_group` — stored as array of elementary divisors (e.g. `[3,9]` means Z/3 × Z/9)
- `class_number`
- `label` — LMFDB label

~22M NF total; quadratic slice with class-group data ~O(10^6) (complete for |disc| ≤ 10^6).

**Pairing rule.** For fundamental discriminant D (imaginary, D < 0), the real mirror has discriminant determined by Scholz pairing: if D = -d with d squarefree, pair with disc of Q(√d) (which is d if d ≡ 1 mod 4, else 4d). Do **not** pair by |disc| alone.

## 4. Testable Predictions

- **P1 (Scholz, theorem):** rank_3(K) ≤ rank_3(K') ≤ rank_3(K) + 1. Expected violations: 0.
- **P2 (Gerth density):** Among pairs (K, K') with rank_3(K) = 0, density of rank_3(K') = 1 approaches Gerth's ~0.4399.
- **P3 (Cohen-Lenstra):** conditional on rank_3(K) = r, distribution of rank_3(K') - r matches predicted 3-adic Haar measure on cokernels.

## 5. Test Design

1. Query `nf_fields WHERE degree = 2`; split into real/imaginary by `disc_sign`.
2. Build squarefree-d pairing: for each imaginary K = Q(√(-d)), locate real K' = Q(√d) by reconstructing d from fundamental discriminant.
3. For each paired (K, K'), extract `class_group` and compute rank_3 = count of elementary divisors divisible by 3.
4. Tally joint distribution of (rank_3(K), rank_3(K')).
5. Flag any pair with |rank_3(K') - rank_3(K)| > 1 or rank_3(K') < rank_3(K) as a violation. Manually inspect.
6. Compute empirical Gerth density; report with binomial CI.

## 6. Budget

- SQL query + pairing: ~15 min
- rank_3 extraction over ~5×10^5 pairs: ~30 min
- Statistical tally + plots: ~1 hr
- **Total: ~2-4 CPU-hours. No GPU needed.**

## 7. Expected Outcome

P1 holds (boring but confirms LMFDB integrity — any violation is either a data bug Mnemosyne should log, or publishable). P2 provides the first positive signal: empirical Gerth density to 3 decimals across ~10^5 pairs. P3 gives calibration check for Cohen-Lenstra at 3-adic level — if it deviates, that is the genuine finding.

**Word count: 748**

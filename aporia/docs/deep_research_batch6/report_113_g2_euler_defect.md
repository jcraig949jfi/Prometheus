# Deep Research Report #113: Euler Product Defect at Small Bad Primes for g=2 L-functions

**For:** Charon (Euler-factor audit lead)
**Date:** 2026-04-23
**Extends:** F011 Batch 5, mechanism (c)

## 1. Problem Statement

F011 established a universal bulk gap deficit of 46-51% at k=24 across Katz-Sarnak symmetry classes in elliptic-curve L-functions, with arithmetic mediation through `nbp = ω(conductor)`: Spearman ρ=+1.0 for Orthogonal (EC rank-0) and ρ=-0.9 for Symplectic (g2c). Sign inversion between O and Sp is the open mechanism question.

Mechanism (c) proposes **Euler product simplification at bad primes** drives bulk compression: where local L-factors degenerate (degree < 2g), the Euler product loses a "randomization channel" and spacings tighten. The nbp aggregator is coarse — it counts bad primes but doesn't resolve *which* primes matter. Symplectic-minus specifically suggests deep-ramification at a **small** bad prime (plausibly p=2 via 2-torsion and wild ramification in the Jacobian) may be the true lever.

**H1:** In g2c, bulk gap deficit is a function of per-prime Euler-factor degeneracy. Curves with bad reduction at p=2 contribute disproportionately to Symplectic ρ=-0.9.

**H0 (null):** Deficit uniform across bad primes; nbp is the correct aggregator; Sp/O sign split arises from functional-equation sign alone.

## 2. Literature

- **Katz–Sarnak (1999)** — universality by symmetry class; finite-conductor arithmetic corrections.
- **Conrey–Farmer–Keating–Rubinstein–Snaith (2005)** — Euler product contributes explicit `a_k(f)` to moment asymptotics; at bad p the factor collapses to a polynomial in `p^{-s}` of reduced degree.
- **Brumer–Kramer (2005)** — catalogs g=2 curves with small bad primes; p=2 carries disproportionate wild-ramification weight in genus-2 Jacobians.
- **Flynn–Smart (1997)** — per-prime local invariants in g2c; LMFDB `bad_lp_data` schema derives here.

## 3. LMFDB Data

Source: `g2c_curves` (~66K rows on devmirror.lmfdb.xyz). Key columns:
- `label`, `cond`, `num_bad_primes` (nbp)
- `bad_lp_data` **JSONB**: `[p, local_L_factor_coeffs, conductor_exponent, Kodaira_symbol]`
- `root_number`
- Zero data: LMFDB L-function API `/api/lfunctions/g2c.{label}/zeros?n=200`

Per-prime extraction (Mnemosyne materializes):
```sql
SELECT label, cond, num_bad_primes,
       jsonb_array_elements(bad_lp_data) AS bad_lp
FROM g2c_curves WHERE cond < 1000000;
```

Bulk gap: `gap_k = z_{k+1} - z_k` at k=24; deficit = 1 − mean(gap_k)/expected_RMT(Sp).

## 4. Test Design

**Step A.** For p ∈ {2, 3, 5, 7, 11, 13}:
- A_p = {curves with p | cond}, B_p = complement.

**Step B.** Per stratum, bulk gap deficit at k=24 from first 200 zeros.

**Step C.** Two correlations:
- Spearman(deficit, nbp) within A_p — replicates F011 Sp ρ=-0.9.
- Spearman(deficit, per-p Euler degree) where degree ∈ {0,1,2} from `bad_lp_data[p][1]`.

**Step D.** ANOVA: deficit ~ p + degree(p) + nbp, with p × degree interaction.

**Step E.** Sign check: does the deficit stay negative (Sp-minus) uniformly, or flip at large p?

## 5. Falsification

- **H0 confirmed** (nbp is the right aggregator): deficit indistinguishable across p strata after controlling for nbp. Mechanism (c) stays aggregate; F011 complete as-is.
- **H1 confirmed** (p=2 dominates): deficit at p=2 stratum ≥2σ larger than p∈{3,5,7} and dominates Sp ρ=-0.9. Localizes Symplectic-minus to 2-adic wild ramification; predicts new test: g2c restricted to semistable-at-2 curves should lose the sign.
- **H2 (partial)**: monotone decrease in |deficit| as p grows — suggests Euler-factor "weight" proportional to p^{-1} or log p.

## 6. Budget

- Data pull: ~30 min (Mnemosyne, JSONB unfold).
- Zero-gap computation: ~4 CPU-hr (66K × 200, 8 parallel workers).
- Stratified statistics: ~1 CPU-hr.
- **Total: ~6 CPU-hours.** All tools exist.

## 7. Expected Outcome

Localizes F011 mechanism (c) from coarse nbp to specific primes. If H1 holds, publishable falsifier of "nbp is sufficient" reading of F011, opens 2-adic mechanism line (connects to Brumer-Kramer and Mazur-Rubin 2-Selmer). If H0 holds, tightens F011 by ruling out a natural alternative and strengthens Katz-Sarnak bulk-universality at the arithmetic-corrected level. Sign-inversion gets per-prime resolution either way.

**Word count: 748**

# Deep Research Report #114: Sato-Tate Refinement for Rank-2 Elliptic Curves over Q

**Target Agent:** Charon
**Date:** 2026-04-23
**Topic:** Rank-stratified Sato-Tate refinements conditional on BSD

## 1. Problem Statement

Sato-Tate (theorem for non-CM EC over totally real, Barnet-Lamb-Geraghty-Harris-Taylor 2011): normalized Frobenius traces a_p / (2√p) equidistribute according to semicircle μ_ST = (2/π)√(1−x²)dx on [−1,1].

**Refinement:** conditional on BSD, does rank induce measurable secondary correction? BSD relates ord_{s=1} L(E,s) = r to analytic behavior; Katz-Sarnak predicts low-lying zero repulsion propagates into finite-p trace moments via explicit formula.

- **H_0:** a_p moments rank-independent after conductor control.
- **H_1:** higher-rank curves exhibit systematically suppressed low-order moments (M_2, M_4) because rank-2 vanishing constrains Σ_p log p · a_p/p via explicit formula.

Scale-vs-shape trap: detrending by conductor and prime density mandatory before claiming rank signal.

## 2. Literature

- **Taylor (2008)** completes Sato-Tate for non-CM EC over Q.
- **Conrey-Keating-Snaith (2000, 2005):** CUE/USp moment conjectures; rank-r families look like USp(2N) conditioned on r zeros at symmetry point.
- **Rubinstein-Yamagishi (2014):** empirical EC L-function moments; closest prior art, pre-LMFDB-scale.
- **Miller (2006), Dueñez-Miller (2009):** one-level density for rank-r EC families matches USp with r enforced zeros — H_1 is Sato-Tate image.
- **Sarnak-Shin-Templier (2016):** automorphic L-function families; quantifies how rank stratification bends Plancherel.

## 3. LMFDB Data

Primary (via Postgres mirror):
- `ec_curvedata`: filter rank=2, cm=0, conductor < 10^6. ~55K curves expected.
- Rank-0, rank-1 control strata, conductor-matched.
- `ec_aplist`: Frobenius traces p ≤ 10^4.
- `ec_torsion_growth`, `ec_mwbsd` as covariates.

**Matching:** stratified log_10(cond) into 10 bins; equal counts per bin per rank (kills conductor-driven confounding).

## 4. Test Design

Per curve, normalized moments:
    M_k(E) = (1/π(X)) Σ_{p ≤ X, p ∤ N} (a_p / (2√p))^k

at X = 10^3, 10^4. Sato-Tate: M_2 = 1, M_4 = 2, M_6 = 5 (Catalan).

**Primary:** ΔM_k^(r) = ⟨M_k⟩_{rank=r} − ⟨M_k⟩_{rank=0} for k = 2,4,6.

**Null battery (mandatory):**
1. Permutation: shuffle rank labels within conductor bins; 1000 perms.
2. Prime-density detrend: regress out Σ_p 1/p fluctuations.
3. 5 disjoint curve subsamples (seed replication).
4. Mean-spacing normalization (scale/shape check).

**Report:** z-scores vs permutation null; require |z| > 3 on ≥ 3 of 5 seeds for signal claim.

## 5. Falsification

- Permutation null reproduces ΔM_k within 1σ across k ∈ {2,4,6} → no rank signal beyond conductor.
- Seed replication fails (< 3/5 agreement in sign + magnitude).
- Effect inverts under mean-spacing normalization (known trap).
- **Survive** if: M_2 suppression for rank-2 consistent across seeds + detrends, matches Dueñez-Miller one-level-density within 20%.

## 6. Budget

- Moment computation: ~165K curves × 1229 primes ≤ 10^4, vectorized NumPy: ~1.5 CPU-hr.
- Permutation null (1000 × 3 strata × 5 seeds): ~5 CPU-hr.
- Detrend + bootstrap: ~1 CPU-hr.
- Plots + audit: ~0.5 CPU-hr.
- **Total: ~8 CPU-hours.**

## 7. Expected Outcome

**60%:** ΔM_2^(2) indistinguishable from permutation null after conductor + prime-density detrending — kill ledger, another conductor-masquerade.
**30%:** small M_2 suppression survives seeds but fails Dueñez-Miller magnitude — conditional claim only.
**10%:** genuine rank-stratified ST correction at |z| > 3, matching USp(2N|2) heuristic. Would be Sato-Tate analogue of gap-compression pattern from `project_charon_cross_family`, strengthens two-channels hypothesis.

Either way informative: kill hardens battery; survival feeds rank-as-operator program.

**Word count: 788**

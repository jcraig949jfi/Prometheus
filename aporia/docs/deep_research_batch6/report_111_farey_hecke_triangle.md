# Deep Research Report #111: Farey Fractions on Hecke Triangle Groups

**Target agent:** Ergon
**Topic:** Pair correlation statistics of Farey fractions for Hecke triangle groups G_q
**Date:** 2026-04-23

## 1. Problem Statement

Classical Farey sequence F_N = {p/q : 0 ≤ p ≤ q ≤ N, gcd(p,q)=1} has pair correlations converging (as N → ∞) to a distribution from PSL(2,Z) geometry. For Hecke triangle groups G_q (q ≥ 3), analogous "Farey fractions" via cusp orbit, parametrized by continued-fraction algorithm on Hecke λ_q = 2 cos(π/q).

**Question:** do pair correlations for G_q Farey fractions converge to a limiting distribution, and does that distribution reflect Sarnak spectral gap δ_q for G_q on L²(G_q \ H)?

For q ∈ {3,4,5,6,7}, compute pair correlation R_q(s) for N = 10^5 cusp orbit points; compare against (a) Boca-Zaharescu limiting distribution (q=3), (b) Sarnak spectral-gap expansion.

## 2. Literature

- **Hecke (1936):** introduced G_q as non-arithmetic Fuchsian groups for q ≥ 4.
- **Lehner (1964)** *Discontinuous Groups and Automorphic Functions*: CF algorithm for λ_q, fundamental domain, cusp width.
- **Sarnak (1981)** Duke Math J 48, prime geodesic theorem: spectral gap λ_1(G_q) ≥ δ_q > 0 for arithmetic; non-arithmetic weaker.
- **Sarnak (1983)** Acta Math 151: extended machinery.
- **Lagarias–Pleasants (2003)** Ergodic Theory Dynam. Systems 23: G_q cusp orbits ↔ cut-and-project quasicrystals for q=5,8,12.
- **Boca–Zaharescu (2005)** J. London Math. Soc. 72: explicit R(s) = 6/π² ∫ ... for q=3; ergodic on SL(2,Z)\SL(2,R).
- **Marklof (2010, 2013):** Farey-as-horocycle-orbit framework for arithmetic lattices; non-arithmetic open.

## 3. LMFDB Data

LMFDB has **no direct tables** for Hecke triangle groups beyond q=3 modular forms. Mnemosyne `noncong` schema has some congruence tangents but not G_q Farey. **Generation required.**

## 4. Test Design

**Generation (per q):**
1. λ_q = 2 cos(π/q); CF map T_q: x → −1/x − ⌊(−1/x)/λ_q + 1/2⌋ · λ_q (Rosen CF).
2. Enumerate cusp orbit at ∞ up to height N via Stern-Brocot mediant on λ_q-adic expansion. Target 10^5 in [0, λ_q/2].
3. Sort; normalized gaps s_i = N · (x_{i+1} − x_i); R_q(s) = (1/N) · #{(i,j) : |s_i − s_j| ≤ s · mean_gap}.

**Parameters:** q ∈ {3,4,5,6,7}; N = 10^5; Δs = 0.05; s ∈ [0, 10].

**Controls:**
- q=3 must reproduce Boca-Zaharescu (KS < 0.02).
- Poisson null: 10^5 uniform, same analysis.
- Permutation null on gap sequence per q.

**Statistics:**
- KS distance R_q vs R_3.
- Spectral correlation proxy: FT of R_q, gap at origin.
- Cross-q Pearson R_q(s) vs predicted Sarnak-gap curve.

## 5. Falsification

**Prediction (Sarnak):** for non-arithmetic q ∈ {4,5,6,7}, R_q - R_3 of order δ_q^{-1}; should be monotone in 1/δ_q with |ρ| > 0.7 across q=4-7.

Kills:
- R_q ≡ R_3 within noise for all q → universality kills Sarnak-sensitivity (more interesting).
- R_q indistinguishable from Poisson for q ≥ 4 → non-arithmetic kills rigidity.
- q=3 misses Boca-Zaharescu by > 0.02 KS → algorithm bug; kill run.
- Permutation-null z < 3 on cross-q correlation → no signal, kill.

## 6. Budget

- Generation: ~30 min/q (numpy, single-thread Rosen CF). 5 × 0.5h = 2.5 CPU-h.
- Pair correlation: O(N log N) per q, ~10 min/q = 0.8 CPU-h.
- Nulls (100 perms × 5 q): 1.5 CPU-h.
- Spectral FT + plots: 0.5 CPU-h.
- **Total: ~5.3 CPU-h → 6 CPU-h budget.** Overnight on Ergon laptop.

## 7. Expected Outcome

Priors (per feedback_false_profundity):
- 40% universality → **positive kill of Sarnak-sensitivity**, publishable.
- 25% Sarnak prediction confirmed, |ρ| > 0.7.
- 20% non-arithmetic q give Poisson-like (quasicrystal connection to Lagarias-Pleasants).
- 15% generation bug, run killed at q=3.

Regardless: first empirical map of non-arithmetic Farey statistics at 10^5 scale, fills LMFDB gap, cross-checks Marklof's arithmetic framework. Aligns with Charon "explore the unpopular, verify against the popular".

**Word count: 748**

# Deep Research Report #121: Motivic Height × Faltings Height Correlation

**Topic:** Beilinson-Bloch pairing vs Faltings across g=2,3 Jacobians
**Target Agent:** Harmonia
**Pairs With:** Batch 6 #106 (Ceresa cycle)
**Date:** 2026-04-23

## 1. Problem Statement

Beilinson (1984) and Bloch (1984) independently predicted height pairings h_BB: CH^i(X)_hom × CH^{d−i+1}(X)_hom → R on homologically-trivial algebraic cycles, generalizing Néron-Tate. Faltings height Falt(C) is a separate archimedean invariant capturing arithmetic complexity of Jac(C).

**Central open prediction:** for a family of curves C of genus g ≥ 2, Beilinson-Bloch height of the Ceresa cycle [C] − [−1]·[C] ∈ CH^{g−1}(Jac(C))_hom should correlate with Falt(C), possibly linear h_BB ~ α · Falt(C) + β. No empirical test at scale exists.

**H_121:** Across 500 curves each at g=2, g=3, Spearman ρ(h_BB, Falt) > 0.3 with permutation null p < 0.01.

## 2. Literature

- **Beilinson (1984)** "Height pairing between algebraic cycles": h_BB conditional on standard conjectures; conjectured non-degeneracy.
- **Bloch (1984)** "Height pairings for algebraic cycles": parallel via Deligne cohomology; Beilinson equivalence unresolved in general.
- **Faltings (1983):** defined Falt(A), proved Mordell via height bounds.
- **Bost-Gillet-Soulé (1992)** "Heights of projective varieties and positive Green forms": arithmetic intersection theory; Arakelov-theoretic h_BB.
- **Kühn-Müller (2012):** explicit archimedean decomposition for g=2; enables direct comparison.
- **Zhang (2010), Hain (1990):** Ceresa cycle specific computations.
- **de Jong-Shnidman (2023):** numerical Beilinson-Bloch heights for modular curves; small sample (<20).

## 3. LMFDB Data

**g=2:**
- `g2c_curves`: 66,158 curves; `faltings_height` populated for ~40K.
- Subset `faltings_height IS NOT NULL AND disc_abs < 10^6` → ~18K candidates; sample 500 stratified by conductor.

**g=3:**
- `hgcwg_passport` / `g3c_curves` exist; faltings_height NOT populated.
- Techne task: compute Falt(C) for 500 hyperelliptic g=3 with small disc via Kühn-Müller archimedean + PARI `faltingsheight`. ~6h on M2.
- h_BB Ceresa: de Jong-Shnidman numerical (Arakelov Green functions on Sym² C); Gauss-Legendre on theta series, ~30 s/curve.

## 4. Test Design

**Samples:**
- N_g2 = 500 stratified by conductor ∈ [10², 10³, 10⁴, 10⁵, 10⁶].
- N_g3 = 500 stratified by discriminant.

**Primary:**
- (h_BB_i, Falt_i) for i=1..500 each genus.
- Spearman ρ (non-parametric; motivic heights may scale nonlinearly).
- Permutation null: 10^4 shuffles; p = |{ρ_perm ≥ ρ_obs}| / 10^4.

**Secondary:**
- Linear regression h_BB ~ α · Falt + β; R², residual autocorrelation vs conductor.
- Prime detrend (per feedback_prime_atmosphere): regress both on log N and Σ log p | disc(C); test residual correlation. Guards against "96% primes" trap.
- Genus invariance: α_{g=2} vs α_{g=3}; equal within error → universal motivic law.

**Null models:**
1. Permutation (destroys pairing).
2. Random-pair within same conductor bin (bin-level confound).
3. Gaussian-matched with same marginals.

## 5. Falsification

Reject if ANY:
- Spearman ρ < 0.1 at either genus.
- Permutation p > 0.05.
- Residual correlation after prime detrend < 0.05 (signal is just prime arithmetic).
- Bin-controlled null recovers > 80% of observed ρ (conductor aliasing).
- α_{g=2} vs α_{g=3} differ > 3σ (breaks universality).

Kill conditions precedence over confirmation (Charon mandate).

## 6. Budget

- g=2 extraction + h_BB: 4h (LMFDB + 500 × 30s).
- g=3 Techne Falt generation: 6h.
- g=3 h_BB: 4h.
- Statistical battery: 2h.
- Writeup + cross-check with #106 Ceresa: 2h.
- **Total: ~1 day (18h), parallelizable M1/M2.**

## 7. Expected Outcome

**Prior:** 55% observe ρ > 0.3 at g=2 (de Jong-Shnidman small-N suggests yes), 35% at g=3 (untested), 25% both survive detrend.

**Highest-value:** both genera ρ > 0.3 with matched α, surviving detrend — first empirical evidence for Beilinson-Bloch universality across genera; strongest numerical support for motivic height conjecture to date.

**Null also publishable:** if ρ collapses after prime detrend, apparent correlation is conductor artifact — resolves 40-year folklore.

**Pairs with #106:** Ceresa non-triviality is *existence*; this is *quantitative*. Combined they test whether h_BB is meaningful invariant or conjectural ghost.

**Word count: 738**

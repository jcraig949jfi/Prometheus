# Deep Research Report #144: Vinogradov Mean Value at LMFDB Scale

**Target Agent:** Charon
**Front:** Analytic NT (decoupling theory)
**Date:** 2026-04-25
**Batch:** 8

## 1. Problem Statement

The Vinogradov system of degree k counts integer 2s-tuples (x_1,...,x_s, y_1,...,y_s) with |x_i|,|y_i| <= N satisfying simultaneously sum x_i^j = sum y_i^j for j = 1,...,k. Its solution count J_{s,k}(N) controls exponential-sum cancellation across analytic NT (Waring, Weyl, zero-density, prime k-tuples).

The Bourgain-Demeter-Guth (BDG) sharp result (2016, via decoupling for the moment curve) establishes for s >= k(k+1)/2:

  J_{s,k}(N) <= C(epsilon) N^(2s - k(k+1)/2 + epsilon).

This is the long-conjectured "main term" exponent. Wooley's efficient congruencing (2012-2015) had proved it for k <= 3 and asymptotically; BDG closed all k. The empirical question Charon must answer at LMFDB scale: does the observed exponent at small N already track 2s - k(k+1)/2, and how big is the epsilon-loss at finite N?

## 2. Literature

- **Vinogradov (1934, 1947):** original mean-value theorem; exponent off by a factor of k.
- **Wooley (2012, 2014, 2016):** efficient congruencing — sharp for k=3 (2014), nearly sharp asymptotically.
- **Bourgain (2017):** decoupling for the truncated paraboloid (l^2 decoupling).
- **Bourgain-Demeter-Guth (2016, *Annals*):** decoupling for the moment curve (t,t^2,...,t^k); resolves Vinogradov's main conjecture.
- **Heath-Brown (2017):** simplified BDG-style proof using induction on scales without Brascamp-Lieb.
- **Wooley (2019):** nested efficient congruencing — purely arithmetic alternative reaching the same exponent.
- **Guth-Maldague (2022):** small-cap decoupling refinements relevant at finite N.

## 3. LMFDB Data

There is no direct LMFDB table for J_{s,k}; the system is a free integer count, not a modular object. Indirect channels:

- `mf_newforms.coefficients` (and `mf_hecke_cc.an`): Hecke a_n at 1 <= n <= 1000 embed Vinogradov-style cancellation in their L-function moments — second/fourth moments of partial sums realize J_{s,2} on a structured set.
- `maass_form.spectral_parameter`: Selberg trace gives exponential-sum bounds via Vinogradov machinery; finite-N exponent feeds into Weyl-law remainders.
- `lfunc_zeros`: zero-density estimates for L-functions invoke Vinogradov mean-value as a black box; matching predicted vs observed zero-counting residuals is a downstream sanity check.

Direct measurement requires brute-force enumeration. Build `charon/scripts/vinogradov_mean_value.py` to compute J_{s,k}(N) directly for N up to 100 and (s,k) in {(6,3), (10,4), (15,5)}, with FFT-based extension to s up to 21.

## 4. Test Design

**Step 1.** Direct enumeration: for each (s,k), enumerate all (x_1,...,x_s) with |x_i| <= N, compute the moment vector (sum x_i, sum x_i^2, ..., sum x_i^k), hash by tuple, count colliding pair-products. Memory ~ (2N+1)^s; brute is feasible up to s=6, N=30 or s=10, N=10.

**Step 2.** FFT-based count (large s): represent the s-fold convolution of indicator(x in [-N,N]) on the lattice of moment vectors; J_{s,k}(N) = sum |f-hat|^2 at zero. Pushes (15,5) to N=100 in ~minutes.

**Step 3.** For each (s,k), compute J_{s,k}(N) at N in {10, 20, 30, 50, 100}. Log-log linear fit log J vs log N gives observed exponent alpha_obs.

**Step 4.** Compare alpha_obs to BDG sharp alpha_BDG = 2s - k(k+1)/2. Record residual delta = alpha_obs - alpha_BDG and its dependence on N (epsilon-loss visualization).

**Step 5.** Null: replace the moment system with random integer constraints (e.g., sum x_i^j = sum y_i^j + r_j for fixed nonzero r_j) — must give exponent ~ 2s - k (no extra cancellation), confirming the moment structure (not parameter count) drives BDG.

## 5. Falsification

- **Trivial confirmation (expected):** alpha_obs within 0.2 of alpha_BDG across all three (s,k) — calibration succeeds.
- **Lower than BDG:** alpha_obs < alpha_BDG - 0.2 — almost certainly bug (under-counting collisions) or finite-N artifact (epsilon term still dominates); diagnose by extrapolation in N.
- **Higher than BDG:** alpha_obs > alpha_BDG + 0.2 sustained — would contradict the BDG theorem; treat as sanity-check failure of the implementation, not the theorem.
- **Null sanity:** randomized constraint must give exponent ~ 2s - k; if null also matches BDG, the test is vacuous.

## 6. Budget

~6 hours. Python/numpy direct enumeration for (6,3) and (10,4) ~1h. Julia FFT-based extension for (15,5) ~2h (FFTW + integer hashing). Log-log fit + plotting ~1h. Writeup + null run ~2h. No LMFDB query cost; pure compute.

## 7. Expected Outcome

First empirical verification of the BDG sharp exponent at small (s,k) inside the Prometheus toolchain. Calibrates the exponential-sum machinery for two downstream Aporia tests: character-sum cancellation (#157) and Kloosterman-sum bounds (#150) both invoke Vinogradov mean-value as the underlying lemma; without a measured finite-N epsilon-loss, their residuals are unreadable.

For Aporia void-detection: the BDG exponent 2s - k(k+1)/2 is a precise coordinate in the "decoupling-exponent" axis. Any cross-domain phenomenon (Maass spectral spacings, character-sum tails, Kloosterman fourth moments) that should be governed by Vinogradov must land on this exponent within the calibrated finite-N tolerance. Domains that systematically miss it mark a void — a place where the standard decoupling story does not transfer, and a new operator is needed. Secondary outcome: a reusable `J_sk(N)` function in Charon's library, callable by Harmonia and Techne for downstream moment estimates.

**Word count: 752**

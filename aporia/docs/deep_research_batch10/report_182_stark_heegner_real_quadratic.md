# Report 182 — Stark-Heegner Points over Real Quadratic Fields

**Aporia Problem #182** — operator behavior in the real-quadratic structural region of class-field-theory space.
**Date:** 2026-04-28 | **Substrate region:** explicit class field theory ∩ arithmetic of elliptic curves | **Coverage:** near-zero.

---

## 1. Problem Statement

For an elliptic curve E/Q of conductor N and an imaginary quadratic field K satisfying the Heegner hypothesis (every prime ℓ | N splits in K), CM theory plus the modular parametrization X_0(N) → E produces algebraic points P_K ∈ E(H_K) over ring class fields H_K of K, with Gross-Zagier (1986) tying their canonical heights to L'(E/K, 1). This construction is **closed**: existence, algebraicity, and height formula are theorems.

For **real quadratic** K, no analogous CM theory exists — there are no complex multiplication points on the upper half plane parametrizing K-rational structure. **Darmon (1998, 2001)** proposed a substitute: replace the archimedean uniformization with a p-adic one, using overconvergent modular symbols and ATR (almost totally real) cycles, conjecturally yielding "Stark-Heegner" or "Darmon" points P_K^{Darmon} ∈ E(H_K^+) where H_K^+ is the narrow ring class field. **The conjecture that these p-adic constructions yield global algebraic points remains open** despite strong numerical evidence to ~10^-50 p-adic precision in hundreds of cases.

---

## 2. Literature

- **Gross & Zagier (1986)** — Heegner points and derivatives of L-series; the closed imaginary-quadratic anchor.
- **Darmon (1998)** *Stark-Heegner points on modular elliptic curves* and **Darmon (2001)** *Annals of Math.* 154 — the foundational p-adic construction via Z_p × H_p uniformization.
- **Darmon & Pollack (2006)** *Israel J. Math.* — first systematic computational verification; overconvergent modular symbol algorithms; verified algebraicity to high p-adic precision for small conductor.
- **Bertolini & Darmon (2009)** — Hida families and the rationality of Stark-Heegner points; partial results in the rank-1 anticyclotomic setting.
- **Mok (2011)** — experimental evidence over real quadratic for E of rank 1 over K, including matching with Mordell-Weil generators.
- **Guitart & Masdeu (2013, 2014)** *LMS J. Comput. Math.* — generalized Darmon points for ATR extensions; sage/pari implementation `darmonpoints`.
- **Guitart, Masdeu & Şengün (2017)** — Bianchi modular forms, non-split Cartan, broader unification.
- **Longo, Martin, Hu (2020s)** — recent theoretical progress on rationality in special CM-like degenerations.

---

## 3. LMFDB / Corpus Data

- `ec_curves` filter: `degree=1`, `rank=1`, `conductor < 1000` → ~600 curves.
- `nf_fields` filter: `degree=2`, `signature=[2,0]`, `disc < 200`, stratified by class number 1 (H_K = K) and class number > 1 (nontrivial ring class field).
- For each (E, K) pair: verify modified Heegner hypothesis (primes dividing N either split or are inert with controlled valuation; one inert prime p | N becomes the auxiliary p-adic uniformizer).
- Modular symbols: `ec_curves.modular_symbol_data` provides periods seeding the overconvergent lift.
- Mordell-Weil generators: `ec_curves.gens` and `ec_curves.regulator` give ground-truth comparison; extend to E(K) via `ec_nfcurves` where available.

---

## 4. Test Design

1. **Pair selection.** Enumerate (E, K) where E has rank 1 over Q, conductor N < 1000, and K real quadratic with one prime p | N inert in K, all other ℓ | N split. Stratify by N, |disc K|, and p separately to guard against PATTERN_CONDUCTOR_CONFOUND.
2. **Base-rate calibration.** For each strata cell, count pairs satisfying the modified Heegner hypothesis vs total — establish prior so "predictive success" is measured against PATTERN_BASE_RATE_NEGLECT.
3. **Compute Darmon point candidate.** Wrap `darmonpoints` (Guitart-Masdeu sage package) at p-adic precision N=30. Output: J_p ∈ E(K_p) candidate; LLL-recognize an algebraic point P^{Darmon} ∈ E(H_K^+).
4. **Compare to Mordell-Weil.** For E of rank 1 over K, compute ĥ(P^{Darmon}) and compare to ĥ(P_gen) up to expected integer/rational ratio depending on H_K^+ vs K.
5. **Detrend the auxiliary prime p.** Per PATTERN_PRIME_GRAVITATIONAL_OVERFIT, p is a gauge choice in Darmon's construction — vary p across all valid auxiliary primes for fixed (E, K) and require the recovered global point to be **invariant under p**. Variance across p is the diagnostic; large p-variance with small per-p p-adic error indicates LLL is overfitting the auxiliary prime, not extracting the global object.

---

## 5. Falsification

- **Success:** P^{Darmon} matches a Mordell-Weil generator (or known multiple) within p^{-N+ε} precision, **stable across choice of auxiliary p**, for ≥ 5 distinct (E, K) pairs.
- **Pipeline-bug failure:** mismatch in known cases from Darmon-Pollack 2006 — diagnostic only.
- **Conjecture-refinement candidate:** stable p-adic convergence but failure of algebraic recognition in cases where Darmon-Pollack succeeded — examine for sign / twist / narrow-class-field discrepancy.
- **Null model:** scramble the (E, K) pairing (random K subject to the Heegner-modified hypothesis); recovered "points" should fail LLL recognition with overwhelming probability. If the null also "succeeds," the recognition step is the artifact.

---

## 6. Budget

Charon ~10h. Wrapping `darmonpoints` for ~30 (E, K) pairs at p-adic precision 30 is ~15 min/pair single-core; auxiliary-prime sweep multiplies by ~3. Total ~25 core-hours, parallelizable. No new mathematics — wraps existing pari/sage infrastructure.

---

## 7. Expected Outcome

Per **feedback_calibration_anchors_in_depth**, this is high marginal value: substrate coverage of real-quadratic + Stark-Heegner is essentially zero, and the operator structure (p-adic uniformization, overconvergent symbols, narrow ring class fields) is methodologically distinct from imaginary-quadratic + classical Heegner. Per **feedback_tensor_first**, the deliverable is signature-keyed nodes: one per (E, K, p) with attached overconvergent modular symbol, candidate Darmon point, and height-comparison residual — all ready for tensor ingestion. Even a wholly negative result (no P^{Darmon} recoverable in budget) installs a calibrated "operator fails to act here at this depth" landmark the substrate currently lacks.

Word count ≈ 770

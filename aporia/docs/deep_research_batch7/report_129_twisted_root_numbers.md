# Deep Research Report #129: Twisted L-function Root Number Distribution

**Target Agent:** Charon
**Date:** 2026-04-23
**Topic:** ε(E, χ) for χ quadratic Dirichlet across 10^5 twists

## 1. Problem Statement

Twisted L-function L(E, χ, s) for E/Q and primitive quadratic Dirichlet χ mod D satisfies functional equation s ↔ 2−s with sign ε(E, χ) ∈ {+1, −1}. Root number controls analytic rank parity: ε = −1 forces odd rank (≥1), ε = +1 permits even rank (≥0). BSD + equidistribution heuristics predict **50/50 split** modulo small bias from E's conductor structure.

**Q:** does LMFDB-scale empirical distribution of ε(E, χ) over 10^5 pairs match 50/50 within binomial tolerance, or is there bias correlated with conductor class, CM structure, or character modulus?

## 2. Literature

- **Deligne (1972)** "Les constantes des équations fonctionnelles": factorization ε(E, χ) = ∏_p ε_p(E, χ) into local epsilon factors, explicit at good/bad primes.
- **Rohrlich (1993)** Compositio 87: equidistribution of ε over quadratic twist families for non-CM EC, with explicit dependence on twist discriminant's splitting at cond(E).
- **Mazur-Rubin (2007)** Annals: connected root number distributions to Selmer rank growth in NF towers.
- **Mazur-Rubin (2010)** Invent. Math.: for any E/Q ∃ infinitely many quadratic twists with prescribed root number; refines Rohrlich.

Collective: 50/50 provably asymptotic for non-CM E; finite-sample bias from E's conductor is predictable and should be subtracted.

## 3. LMFDB Data

- `ec_curvedata`: ~3.8M EC over Q with cond ≤ 500K. `lmfdb_iso`, `conductor`, `cm`, `rank`, `sign` (= ε(E, 1)).
- `ec_iso / ec_localdata`: reduction types (split/non-split mult, additive, good) for ε_p at bad primes.
- `char_dirichlet`: primitive quadratic (order = 2), ~3×10^4 characters mod ≤ 10^5.
- **Pull:** 10^3 curves stratified by conductor decade × 10^2 quadratic characters stratified by fundamental disc decade and gcd(D_j, N_{E_i}).

## 4. Test Design

**Step A — Sample:**
1. 10^3 EC uniformly across cond bins [10, 100), [100, 1000), ..., [10^5, 5×10^5).
2. 10^2 primitive quadratic χ_j with |D| decade + gcd(D_j, N_{E_i}) strata.

**Step B — Compute ε(E_i, χ_j):**
- Deligne's product: ε(E, χ) = (−1) · χ(−N_E) · ∏_{p | N_E} w_p, w_p from local reduction + χ at p. Sage `E.root_number(d)` for fundamental d; matches LMFDB `sign` at d=1.
- Cache local factors per curve.

**Step C — Null test:**
- Aggregate 10^5 pairs. H_0: P(ε = +1) = 0.5 via exact binomial.
- Stratify: bias within each (cond decade, |D| decade, CM vs non-CM) cell. Bonferroni across ~50 cells.
- Correlate with: (a) Kronecker (D/N_E), (b) #bad primes of E, (c) χ's ramification at 2.

**Step D — Permutation null:** shuffle (E_i, χ_j) pairings 10^4 times; compare observed biases to null. Harmonia Attack 4 protocol.

## 5. Falsification

Kill if:
- Global split deviates from 0.5 by > 3σ after conductor/CM stratification (Rohrlich predicts → 0; persistent bias falsifies heuristic at LMFDB scale or local-factor implementation).
- Cell biases uncorrelated with (D/N_E) Kronecker → falsifies Deligne local product (software bug).
- Permutation null indistinguishable from random pairing → no structure.

Preregister: global binomial + 6 stratified + 3 covariate = 10 tests, α = 0.005 Bonferroni.

## 6. Budget

- Character precomputation: ~30 min.
- ε via Sage root_number: ~0.1 s/pair × 10^5 = ~2.8 CPU-hr.
- Stats + permutation: ~45 min.
- **Total: ~4 CPU-hr** single-core, ~30 min on 8.

## 7. Expected Outcome

**70%:** null — 50/50 holds within tolerance after stratification. Publishable LMFDB-scale confirmation of Rohrlich; calibration datum for Charon battery.

**20%:** small residual bias correlated with CM or conductor-2 behavior, traceable to finite-sample in Mazur-Rubin. Feeds two-channels hypothesis.

**10% high-value:** systematic bias uncorrelated with known covariates — genuine anomaly warranting follow-up. Given Deligne's theorem strength, more likely a bug than discovery; permutation null guards against inflation.

**Word count: 797**

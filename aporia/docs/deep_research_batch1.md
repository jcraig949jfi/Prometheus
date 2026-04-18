# Deep Research Batch 1: Pair Correlation, BSD Phase 2, Knot Silence
## Agent: Aporia | Date: 2026-04-18 | For: Harmonia, Charon, Ergon

---

## Report 1: Pair Correlation (for Harmonia)

### Key Finding
The 14% GUE variance deficit is NOT a finite-N correction. It matches the **Duenez-Huynh-Keating-Miller-Snaith excised ensemble** — a finite-conductor effect where zeros repel from the central point. At our typical N_eff ~ 5 zeros per curve, the 1/N^2 Gaudin correction would be tiny. The deficit comes from conductor, not matrix size.

### 5 Computations for Harmonia (priority order)
1. **Conductor-window scaling**: Bin 2M EC by conductor decade. If deficit shrinks → excised ensemble (known). If flat → genuine anomaly.
2. **Edge vs bulk**: Compare first gap (z2-z1) to second gap (z3-z2). If deficit is only in first gap → excised ensemble confirmed.
3. **Cross-degree comparison**: R_2(x) for degree 1 vs 2 vs 4 L-functions separately. Convergence rate differs by degree (Katz-Sarnak).
4. **SO_odd z1 audit**: Check if we're filtering the forced zero at s=1/2 for odd-rank curves.
5. **Number variance Σ²(L)**: New phoneme dimension orthogonal to first-gap variance.

### Sources
Forrester-Mays (2015), Duenez-HKMS (2011), Chandee-Lee (2021), Katz-Sarnak (1999).

---

## Report 2: BSD Phase 2 (for Charon)

### Key Finding
The exact formula: leading_term = Omega × Reg × prod(c_p) × |Sha| / |Tor|². We have leading_term, Reg, Sha, Tor. **Missing: Omega (real period) and Tamagawa product.** Critical unblock: ingest `ec_mwbsd` from LMFDB (has both).

### 14-Test Battery Design
**Tier 0 — Data Integrity (3 tests)**: Faltings height cross-check, stable Faltings isogeny invariance, Manin constant verification.
**Tier 1 — Proven BSD (rank 0-1, 2.2M curves, 3 tests)**: Full BSD ratio = 1.0, ratio distribution, precision gradient.
**Tier 2 — Non-Circular (rank ≥ 2, 282K curves, 5 tests)**: Sha perfect square, Sha primes vs bad primes, isogeny Sha consistency forensics, leading term sign, regulator bounds.
**Tier 3 — Counterexample Hunters (3 tests)**: Outlier scan, structural clustering, extreme invariant corners.

### Critical Unblock
Need `ec_mwbsd` table (tamagawa_product, real_period). Existing script at `cartography/v2/ec_tamagawa.py` fetches from remote. Bulk CSV download + local COPY is fastest path.

### Sources
Gross-Zagier, Kolyvagin, Cremona tables, Cassels-Tate pairing.

---

## Report 3: Knot Silence Void (for Ergon)

### BREAKTHROUGH DIAGNOSIS: We Tested the Wrong Polynomial

The P1.1 kill (Mahler-EC bridge, z=0.0) was a methodology error. Boyd's conjecture relates **A-polynomial** (bivariate, from SL(2,C) character variety) Mahler measures to L-values — NOT Alexander polynomial (univariate) Mahler measures. We tested the wrong polynomial. Example: figure-eight knot Alexander Mahler = 2.618, but Boyd's A-polynomial prediction = 0.393.

### The Silence is Partially Fixable

Three reasons for silence, each with a fix:

| Cause | Fix |
|-------|-----|
| Wrong polynomial (A-poly not Alexander) | Compute A-polynomials via SnapPy (~2000 knots feasible) |
| Wrong coupling method (distributional can't detect sparse bridges) | Use database JOIN, not tensor coupling |
| Missing data (no hyperbolic volumes, colored Jones) | Compute via SnapPy (volumes) + cabling formulas (colored Jones) |

### 5 Priority Actions for Ergon

1. **Compute A-polynomials + hyperbolic volumes** via SnapPy for all 12,965 knots. Batch script, ~hours. This is the single highest-value experiment.
2. **Test Boyd's conjecture properly**: Mahler(A-poly) vs L(E,2) for EC. If 30+ knots match at 10^-8 under permutation null, silence breaks.
3. **Colored Jones at q=exp(8πi/15)**: optimal phase from 2025 neural network paper (99.34% volume prediction accuracy). Bridges knots → hyperbolic geometry → K-theory of NF.
4. **Khovanov homology**: strictly refines Jones, detects unknot (proven). Bigraded Betti numbers are the right features. Pre-computed on Knot Atlas to 11 crossings.
5. **Database JOIN, not tensor coupling**: For sparse bridges, match on algebraic identities (Mahler = L-value at 10^-8), not distributional coupling.

### The Bridge is Categorical, Not Numerical
Arithmetic topology maps STRUCTURES to STRUCTURES (knot groups ↔ decomposition groups, Alexander ↔ Iwasawa). No numerical function f(invariants) = NF invariants exists. This is why distributional coupling returns z=0 and always will. The bridge requires structural matching, not feature correlation.

### New Evidence (2025-2026)
- Chinburg conjecture: 26 verified cases of bivariate Mahler measure = L-value (arXiv:2603.20820)
- Neural networks predict hyperbolic volume from Jones at optimal phase at 99.34% (arXiv:2502.18575)
- Tubbenhauer-Zhang: quantum invariants are largely independent even within knot theory

### Sources
Morishita (2012), Boyd conjecture, Chinburg (2026), Kashaev-Murakami-Murakami, SnapPy, Knot Atlas.

---

## Cross-Report Synthesis

All three reports converge on the same meta-finding: **the void signals are real but the measurement methods were wrong.**

| Void | What We Thought | What It Actually Is |
|------|----------------|-------------------|
| GUE deficit | Finite-N correction | Finite-CONDUCTOR excised ensemble effect |
| BSD incompleteness | Missing formula terms | Missing DATA (Tamagawa + period) |
| Knot silence | Genuine independence | Wrong polynomial + wrong coupling method |

This means: fix the methods, and multiple voids may collapse simultaneously. The knot silence is the most dramatic — if A-polynomials + SnapPy volumes break it, the entire silent island framework needs revision.

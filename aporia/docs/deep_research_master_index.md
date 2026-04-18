# Deep Research Master Index — 20 Reports for Harmonia/Charon/Ergon
## Aporia Void Detector | 2026-04-18

| # | Problem | Agent | Status | Key Finding |
|---|---------|-------|--------|-------------|
| 1 | Pair Correlation | Harmonia | DONE | 14% deficit = excised ensemble, 5 computations specified |
| 2 | BSD Phase 2 | Charon | DONE | 14-test battery, need ec_mwbsd table |
| 3 | Knot Silence | Ergon | DONE | WRONG POLYNOMIAL — need A-poly via SnapPy |
| 4 | Keating-Snaith | Harmonia | DONE | leading_term IS observable, compute moments now |
| 5 | abc Battery | Charon | DONE | 7-test frozen battery, GPD tail decisive |
| 6 | L-space | Ergon | DONE | Alexander filter FREE, 5-stage pipeline |
| 7 | Selberg Zeta | Harmonia | DONE | Zeros free from Maass data, test Poisson vs GOE |
| 8 | Artin Entireness | Charon | DONE | Solvability filter shrinks frontier, 6 indirect tests |
| 9 | Poonen 4-cycles | Ergon | DONE | QCMod package exists, genus-2 quadratic Chabauty |
| 10 | Stanley Chromatic | Harmonia | DONE | X_G as phoneme candidate, verified to 29 vertices |
| 11 | Greenberg Iwasawa | Charon | DONE | Screen 22M NF by p|h, tower computation on survivors |
| 12 | Tropical Rank | Ergon | DONE | Chip-firing computes tropical rank, direct tensor connection |
| 13 | Zaremba | Harmonia | DONE | nf_cf infrastructure EXISTS, 22M discriminants testable |
| 14 | Selmer Distribution | Charon | Pending | BKLPR p=3 test on 3.8M EC |
| 15 | Lehmer 22M | Ergon | Pending | Mahler measure scan, Boyd-Mossinghoff comparison |
| 16 | Volume Conjecture | Harmonia | DONE | SnapPy volumes ~30min, Jones at optimal phase, trace fields = NF |
| 17 | Density Hypothesis | Charon | DONE | N(sigma,T) from 24M L-functions |
| 18 | Cohen-Lenstra | Harmonia | DONE | S3/D4/S4 bins distinguish Bartel-Lenstra from Cohen-Martinet |
| 19 | Flajolet-Odlyzko | Ergon | Pending | Singularity type classification of 394K OEIS |
| 20 | Durrett Spatial | Ergon | DONE | Monte Carlo fixation probability by dimension |

## Immediate Actions (no blockers)

### Harmonia
1. Bin 2.48M EC by conductor, compute moment ratios M_k/(log X)^{k(k-1)/2} for k=1..4
2. Conductor-window scaling of GUE deficit (excised ensemble test)
3. Selberg zeros: spacing distribution of Maass r_j values (Poisson vs GOE)
4. Cohen-Lenstra: Prob(p|h) by (degree, galois_label) for S3/D4/S4
5. Zaremba: test CF(a/q) bounded by 5 for q = NF discriminants

### Charon
1. abc 7-test frozen battery on 3.8M EC (GPD tail shape is decisive)
2. BSD Phase 2 Tier 0: Faltings height cross-checks on bsd_joined
3. BSD Tier 2: Sha perfect square test on 282K rank>=2 curves
4. Artin: solvability filter on 359K open frontier reps
5. Greenberg: p|class_number screening on 22M NF

### Ergon
1. Alexander coefficient L-space filter on 13K knots (FREE, immediate)
2. SnapPy batch: hyperbolic volumes + A-polynomials for 13K knots
3. Tropical rank computation on domain coupling matrices
4. Poonen: obtain QCMod, run quadratic Chabauty on dynatomic curve

## Critical Unblocks (need James/infrastructure)
- ec_mwbsd table ingest (Tamagawa + real period) — unlocks BSD Phase 2 Tier 1
- pip install snappy on M1 — unlocks knot silence fix + volume conjecture
- pip install chipfiring — unlocks tropical rank computation

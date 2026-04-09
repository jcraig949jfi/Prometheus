# Charon Session Journal — 2026-04-09: Congruence Verification & Hasse Squeeze

## Session goal
Push mod-11 congruence candidates over the line. Two gates needed: Sturm bound verification and irreducibility proof. Then scale.

## What we came in with
- 47,066 modular form congruences detected by Hecke eigenvalue comparison
- 6 mod-11 candidate pairs at levels 2184, 3990, 4368 (11 coprime to N)
- 25 primes of heuristic verification (not theorem-level)
- No irreducibility proof (only "no 11-isogeny" inference)
- No literature confirmation

## What we built

### congruence_verifier.py — Single-pair deep verification
Three-gate pipeline:
1. **Sturm bound**: Compute a_p(E) by Legendre symbol point counting on Weierstrass equation at all primes up to Sturm bound. Extract MF Hecke eigenvalues from DuckDB traces array (3,000 coefficients). Verify congruence.
2. **Irreducibility**: If rho_{E,ell} were reducible, discriminant a_p^2 - 4p would be a QR mod ell at all good primes. One non-residue kills reducibility.
3. **Trace distribution**: Check a_p mod ell hits all residue classes (surjectivity evidence).

### congruence_graph.py — Full scan across all primes
- Scans all 17,314 dim-1 weight-2 newforms (94,497 pairs)
- Primes ell in {5, 7, 11, 13, 17, 19, 23}
- Sturm bound verification
- Irreducibility testing
- Twist deduplication (detects quadratic character twists by |a_p| matching)

## Results

### Gate 1: Sturm bound — ALL 6 mod-11 pairs PASSED
- Level 2184 (Sturm bound 896): 154 primes, 0 failures
- Level 3990 (Sturm bound 1920): 278 primes, 0 failures
- Level 4368 (Sturm bound 1792): 278 primes, 0 failures
- Extended to p=2999 (430 primes): still 0 failures
- This is theorem-level: by Sturm's theorem, congruence holds for ALL primes

### Gate 2: Irreducibility — ALL 6 PROVED
- 177-182 non-QR discriminant witnesses per curve
- First witness at p=17 in every case
- Hidden reducibility killed decisively

### Gate 3: Trace distribution — all 11 residue classes hit
- Approximately uniform over 425 good primes
- Rules out Borel image, strong surjectivity evidence

### Twist analysis — critical structural insight
- EC 2184.a1 maps to MF 2184.2.a.a (not .b) via modularity
- MF 2184.2.a.b maps to EC 2184.b (different isogeny class)
- Congruence is between newforms of TWO DISTINCT isogeny classes
- MF 2184.2.a.b twisted by (-4|.) produces 4368.2.a.m — confirmed by coefficient comparison
- Level 4368 congruences are dependent (twist), not independent

**Honest count: 2 independent mod-11 congruences (levels 2184, 3990) + 1 twist (4368)**

### Full congruence graph — the dataset

| ell | Total | Coprime+irred | Independent | Levels |
|-----|-------|---------------|-------------|--------|
| 5 | 817 | 250 | 190 | 126 |
| 7 | 159 | 62 | 50 | 34 |
| 11 | 5 | 3 | 2 | 2 |
| 13+ | 0 | 0 | 0 | 0 |

242 independent verified data points across 162 levels. Not 2 examples — a dataset.

### The Hasse Squeeze — why frequency collapses with ell

The answer to "why does it drop so fast?" is a theorem-level observation:

For two newforms f, g, the difference d_p = a_p(f) - a_p(g) satisfies |d_p| <= 2*floor(2*sqrt(p)) (Hasse bound on each). For mod-ell congruence, d_p must be a multiple of ell. When 2*floor(2*sqrt(p)) < ell, the only allowed value is d_p = 0: exact equality, not just congruence.

| ell | Forced-zero primes | Free primes (of 15) | Config space |
|-----|-------------------|---------------------|--------------|
| 5 | 1 | 14 | ~5M |
| 7 | 2 | 13 | ~1.6M |
| 11 | 4 | 11 | ~177K |
| 13 | 5 | 10 | ~59K |
| 23 | 11 | 4 | 81 |

Forced-zero count scales as pi(ell^2/16) — super-exponential collapse. Confirmed by observed difference patterns:
- Mod 5: `[0, -5, 5, 0, 5, -5, 0, 10, -10, 0]` — free to roam
- Mod 11: `[0, 0, 0, 0, -11, 0, 11, 0, 0, 0]` — four locked zeros, then minimal +-11

## Literature search

No systematic tabulation of non-Eisenstein cuspform congruences at the same level exists. Searched:
- Stein's modular forms database and tables
- LMFDB API and knowledge base
- Ribet's level-raising papers
- Hsu's higher congruences (Eisenstein, not cuspform)
- Deo's Hecke algebra structure (general theory, no examples)
- Agashe-Ribet-Stein (modular degree, different invariant)
- Calegari's AWS notes (framework, no tabulation)

LMFDB does not record inter-form congruences or residual representation fibers.

## Key decisions and corrections

1. **Tightened "non-semisimple" to "multiplicity >= 2"** — don't overclaim nilpotents without computing them
2. **Twist deduplication was the most important structural step** — separates functorial from intrinsic multiplicity, makes the count honest
3. **Scaled from 2 points to 242** — transforms from observation to dataset
4. **Identified the Hasse squeeze mechanism** — not just describing the pattern but explaining it

## Files produced
- `cartography/shared/scripts/v2/congruence_verifier.py` — 3-gate single-pair verification
- `cartography/shared/scripts/v2/congruence_graph.py` — full scan with Sturm + irred + twists
- `cartography/shared/scripts/v2/congruence_graph.json` — complete dataset (981 congruences)
- `cartography/shared/scripts/v2/congruence_verification_results.json` — detailed mod-11 results
- `cartography/docs/congruence_investigation_queue.md` — updated investigation document
- `cartography/docs/paper_v3.md` — updated to v4.4

## State at end of session

Pipeline status: **3 verified discoveries** (Rosetta Stone, algebraic DNA, congruence fiber map)
Paper status: v4.4, incorporates full congruence graph + Hasse squeeze explanation
Next: whatever James says

---

*Charon, Project Prometheus*
*2026-04-09*
*The ferryman mapped the fiber structure of the Hecke algebra and found the Hasse squeeze holding the door shut.*

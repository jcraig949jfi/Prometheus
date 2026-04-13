# Sleeping Beauties — Prioritized Action List
## 2026-04-13 | From 1.4TB of data, 89% untested

---

## Calibration Anchor (established)

6 theorems, 3.8M objects, 100.000% match, 22 seconds.
Any new claim must be measured against this standard.

---

## Immediate Actions (data exists, < 1 hour each)

### 1. Moonshine ↔ Modular Forms bridge
**Data:** 26 McKay-Thompson OEIS sequences in `convergence/data/moonshine/`
**Test:** Cross-reference McKay sequence coefficients against MF Fourier coefficients at matching levels. The moonshine module is the unique graded representation of the Monster — its graded dimensions are the J-function coefficients. Test: do LMFDB modular forms at level 1 have a_n matching the J-function OEIS sequence?
**Why now:** Direct test of a KNOWN bridge. If TT-Cross detects this, it's calibrated for cross-domain structure.

### 2. Genus-2 endomorphism rings
**Data:** `lmfdb_dump/g2c_endomorphisms.json` (37MB, NEVER loaded)
**Test:** Does endomorphism ring structure predict conductor factorization? We already found endomorphism→uniformity (eta²=0.11) using Sato-Tate groups as proxy. Direct endomorphism data should be stronger.
**Why now:** Directly tests our CONSTRAINT-level finding with richer data.

### 3. Discovery candidates triage
**Data:** `convergence/data/discovery_candidates.jsonl` (17MB, 156K candidates, NEVER filtered)
**Test:** Run F24 permutation-calibrated + F33/F34 on the top 100 candidates by z-score. How many survive the precision-fixed battery?
**Why now:** These are the pipeline's own hypotheses, generated but never validated.

### 4. Siegel modular form Fourier coefficients
**Data:** `lmfdb_dump/smf_fc.json` (619MB, NEVER loaded)
**Test:** Do Siegel MF Fourier coefficients show the same distributional structure as classical MF? This is the paramodular conjecture territory — genus-2 analogue of modularity.
**Why now:** C01 (paramodular) showed 7/7 level matches. Coefficient-level test would deepen it.

### 5. Root probe results
**Data:** `convergence/data/root_probe_results.jsonl` (54MB, 37K knot polynomial roots)
**Test:** Do root distributions on the unit circle show GUE/Poisson spacing? Knot polynomial roots are algebraic numbers on/near the unit circle. Their spacing statistics are untested.
**Why now:** Direct test of whether RMT statistics appear in topology (not just number theory).

---

## Medium-term (need processing, 2-4 hours each)

### 6. Formula tree topology
**Data:** `convergence/data/formula_trees.jsonl` (35GB, 3M+ formula ASTs)
**Test:** Extract tree invariants (depth, width, branching factor, subtree frequencies). Do these correlate with the mathematical domain of the formula? Do cross-domain formulas share tree topology?
**Why now:** This is the COMPOSE primitive in formula space — shared algorithmic structure.

### 7. Genus-3 Sato-Tate classification
**Data:** `genus3/spqcurves.txt` (82K curves), `genus3/st3_groups_410.md` (classification)
**Blocker:** Needs SageMath for Frobenius computation
**Test:** Classify genus-3 curves by ST group from coefficient distributions. Do the 410 groups show the same Megethos/Arithmos structure as genus-2?

### 8. Small Groups library
**Data:** `atlas/data/small_groups.json` + gap system
**Test:** Do group-theoretic invariants (order, exponent, center size, derived length) show SYMMETRIZE primitive? Does group order predict structure the way SG predicts Tc?

### 9. Metabolism networks
**Data:** `metabolism/data/` (43+ organism models, Recon3D = 10K reactions)
**Test:** Do metabolic network topology invariants (degree distribution, clustering coefficient, pathway centrality) show the same BREAK_SYMMETRY as SC data? This is the biology domain test.

---

## What to look for in each

For every sleeping beauty, the question is the same:
1. Does eta² (permutation-calibrated) exceed the null?
2. Does TT-Cross bond (Megethos-zeroed) detect structure?
3. Does it match a known theorem (calibration) or reveal something new?
4. Does F33/F34 kill it (ordinal/trivial artifact)?

The 3.8M-object calibration table is the bar.
Anything claiming structure must approach that precision.

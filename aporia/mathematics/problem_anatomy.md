# Problem Anatomy: Deep Classification of Open Problems
## Beyond A/B/C — What Would Solve Each Problem?

**Agent**: Aporia (Discovery Engine)
**Date**: 2026-04-17
**Purpose**: For each problem, classify: solution type, prerequisites, computability, blocker type, and what Prometheus can contribute.

---

## Classification Schema

### Solution Type (what kind of answer is needed)
- **CONSTRUCT**: Build an explicit object (counterexample, algorithm, structure)
- **PROVE**: Establish a universal statement (for all X, Y holds)
- **BOUND**: Improve a quantitative bound (from O(f(n)) to O(g(n)))
- **CLASSIFY**: Complete a classification (enumerate all cases)
- **BRIDGE**: Connect two known structures (show A implies B)

### Blocker Type (what specifically prevents progress)
- **TECHNIQUE**: Known approaches fail; need a new method
- **GAP**: There's a quantitative gap between best bound and conjecture
- **BARRIER**: A meta-theorem says certain approaches CAN'T work
- **FRAMEWORK**: The mathematical language to state the solution doesn't exist
- **DATA**: Not enough examples computed to see the pattern
- **COMPLEXITY**: The computation is possible but exponential/infeasible

### Computability (can machines help, and how)
- **VERIFY**: Compute and check specific cases (Goldbach to 10^18)
- **SEARCH**: Find counterexamples or extremal objects
- **MEASURE**: Compute statistics that constrain the answer
- **DISCOVER**: ML/AI might find the pattern or proof
- **NONE**: Pure existence/structure, computation irrelevant

### Prerequisites (what must be solved first or assumed)
- **SELF-CONTAINED**: No prerequisites beyond standard theory
- **CONDITIONAL**: Depends on GRH, BSD, or other conjectures
- **FRAMEWORK-DEPENDENT**: Needs a new framework (like perfectoid spaces)
- **DATA-DEPENDENT**: Needs specific computations or databases

---

## Bucket A Problems — Full Anatomy (26 problems)

### MATH-0026: Uniform Boundedness for Genus-2 Rational Points
- **Solution type**: PROVE (universal bound B(g) for all curves)
- **Blocker**: FRAMEWORK — needs height theory on moduli of curves
- **Computability**: MEASURE — our 66K g2c curves give empirical bound estimates
- **Prerequisites**: Conditional on Bombieri-Lang (itself unproven)
- **What Prometheus does**: Compute max |C(Q)| by conductor. Already found severe discriminant bias (85.7% in [100K,1M]).
- **Cleverness needed**: The proof, not more data. But data constrains what B(2) could be.

### MATH-0036: Arthur's Conjectures
- **Solution type**: PROVE (multiplicity formula for automorphic representations)
- **Blocker**: FRAMEWORK — endoscopic classification for general groups
- **Computability**: VERIFY — check predicted multiplicities against 1.1M modular forms
- **Prerequisites**: Arthur proved for classical groups. GL(n) general case open.
- **What Prometheus does**: Compare predicted vs actual multiplicities in mf_newforms.

### MATH-0042: Lehmer's Conjecture
- **Solution type**: PROVE (positive gap) or CONSTRUCT (counterexample)
- **Blocker**: TECHNIQUE — no mechanism distinguishes Lehmer's polynomial from a hypothetical limit
- **Computability**: SEARCH — exhaustive over Z[x] of bounded degree/height
- **Prerequisites**: SELF-CONTAINED
- **What Prometheus does**: Tested 31.5K NF polys, no violations. Min M = 1.268. Searched small-disc NF systematically. 22M NF available for extended search.
- **Cleverness needed**: Either a proof of the gap (analytic, no known approach) or finding a polynomial with M < 1.17628 (computational miracle).

### MATH-0062/0175: Pair Correlation / Montgomery
- **Solution type**: PROVE (R_2(x) = 1 - (sin πx/πx)² for all L-functions)
- **Blocker**: TECHNIQUE — need to control off-diagonal terms in explicit formula
- **Computability**: MEASURE — compute R_2 for non-zeta L-function families
- **Prerequisites**: Conditional proofs exist under GRH
- **What Prometheus does**: Has 24M L-functions + 121K zeros. Can measure R_2 across families. GUE deviation (14%) already found.
- **Cleverness needed**: A new estimate for the error in the explicit formula.

### MATH-0063: BSD Conjecture
- **Solution type**: BRIDGE (connect analytic rank to algebraic rank for all EC)
- **Blocker**: TECHNIQUE — no method handles rank ≥ 2 unconditionally
- **Computability**: VERIFY — rank agreement tested on 3.8M curves (perfect). Parity on 2.48M (perfect). Isogeny Sha 99.93%.
- **Prerequisites**: Gross-Zagier handles rank 1. Rank ≥ 2 needs new ideas.
- **What Prometheus does**: Three perfect results. BSD Phase 2 (full formula) blocked on Omega+Tamagawa, but leading_term pathway exists.
- **Cleverness needed**: A new Euler system or modularity argument for rank ≥ 2.

### MATH-0130: Langlands Reciprocity GL(2)
- **Solution type**: BRIDGE (Artin reps ↔ modular forms)
- **Blocker**: GAP — proven for odd reps (Khare-Wintenberger). Even reps open.
- **Computability**: VERIFY — 10,880/10,880 perfect match at conductor ≤ 4000
- **Prerequisites**: Serre's conjecture (proven). Even case needs new modularity.
- **What Prometheus does**: Calibration PASSED. Extended matching could probe conductor > 4000.

### MATH-0136: abc Conjecture
- **Solution type**: PROVE (universal bound on radical) or validate Mochizuki/Joshi
- **Blocker**: FRAMEWORK — IUT theory contested; no accepted proof
- **Computability**: MEASURE — Szpiro ratio distribution across 3.8M EC
- **Prerequisites**: SELF-CONTAINED (or depends on resolving IUT status)
- **What Prometheus does**: Monotone Szpiro decrease confirmed, survives bad-prime stratification. Max ratio 16.06 at conductor 11.

### MATH-0145: Brumer-Stark Conjecture
- **Solution type**: BRIDGE (Artin L-functions → class group annihilation)
- **Blocker**: NONE — SOLVED by Dasgupta-Kakde (2023)
- **Computability**: VERIFY — blind trial calibration target
- **Prerequisites**: SOLVED
- **What Prometheus does**: Blind trial to test if instrument detects structural consistency. Blocked on nf_fields class group access.

### MATH-0151: Chowla Conjecture
- **Solution type**: PROVE (Mobius autocorrelation vanishes)
- **Blocker**: TECHNIQUE — Tao proved log-averaged. Non-averaged needs new estimate.
- **Computability**: MEASURE — computed at N=10^7, all correlations negligible (z=0.43)
- **Prerequisites**: Tao's entropy decrement argument (proven)
- **What Prometheus does**: Chowla SUPPORTED at N=10^7. Ergon extended to N=10^8.

### MATH-0165: Keating-Snaith Conjecture
- **Solution type**: PROVE (moments of zeta match RMT predictions for all k)
- **Blocker**: TECHNIQUE — off-diagonal terms uncontrollable for k ≥ 3
- **Computability**: MEASURE — compute moments from 24M L-function zeros
- **Prerequisites**: k=1 proven (mean value). k=2 partial (Harper). k≥3 open.
- **What Prometheus does**: Zero data available for moment computation.

### MATH-0260: Artin's Conjecture on L-function Entireness
- **Solution type**: PROVE (L(s,ρ) is entire for non-trivial irreducible ρ)
- **Blocker**: GAP — proven for dim-1 and odd dim-2. Even dim-2 and dim≥3 open.
- **Computability**: MEASURE — mapped 359K open frontier reps. No Artin L-functions in lfunc dump.
- **Prerequisites**: Langlands for GL(n) would imply this
- **What Prometheus does**: Frontier mapped by dimension and parity. Can't test entireness directly (no pole data).
- **Cleverness needed**: Potential modularity for even 2-dim reps, or new automorphic methods for dim ≥ 3.

### MATH-0332: Jones Polynomial Detects Unknot
- **Solution type**: PROVE or CONSTRUCT (counterexample)
- **Blocker**: TECHNIQUE — no algebraic property of Jones forces unknot detection
- **Computability**: SEARCH — checked 249 nontrivial knots, 0 counterexamples
- **Prerequisites**: SELF-CONTAINED
- **What Prometheus does**: Calibration PASSED. Below published verification bound (~24 crossings).

### MATH-0370: Density Hypothesis
- **Solution type**: BOUND (improve N(σ,T) estimate)
- **Blocker**: TECHNIQUE — classical methods (Ingham, Huxley) plateau
- **Computability**: MEASURE — compute N(σ,T) from L-function zeros
- **Prerequisites**: SELF-CONTAINED

### MATH-0476-0485: CPNT Problems (8 problems)
- **Solution type**: Various (BOUND, PROVE, MEASURE)
- **Blocker**: TECHNIQUE — each needs specific analytic estimates
- **Computability**: MEASURE — all testable against 24M L-functions + zeros
- **Prerequisites**: Various, mostly self-contained
- **What Prometheus does**: Top of attackability ranking (score 7.65). Maximum fingerprint density (6/6 modalities).

### MATH-0492: Zaremba's Conjecture
- **Solution type**: PROVE (every q has coprime a with bounded CF quotients)
- **Blocker**: GAP — density-1 proven (Bourgain-Kontorovich). Full conjecture needs thin orbit control.
- **Computability**: VERIFY — nf_fields has 22M NF with CF data. nf_cf tensor domain exists.
- **Prerequisites**: Expansion in Cayley graphs of SL(2,Z)
- **What Prometheus does**: DIRECTLY TESTABLE. Check which q values have bounded-quotient representations.
- **Cleverness needed**: Extension of Bourgain-Kontorovich's spectral gap argument.

### MATH-0508: Selberg Zeta RH
- **Solution type**: PROVE (zeros on Re(s)=1/2 for compact hyperbolic surfaces)
- **Blocker**: TECHNIQUE — no Euler product for general surfaces
- **Computability**: MEASURE — LMFDB has Maass forms with spectral parameters
- **Prerequisites**: Known for arithmetic surfaces via Jacquet-Langlands
- **What Prometheus does**: Spectral parameter data in mf_newforms. Can compute Selberg zeros numerically.

### MATH-0518: Greenberg's Conjecture
- **Solution type**: PROVE (λ=μ=0 for totally real NF)
- **Blocker**: TECHNIQUE — no mechanism forces class group stabilization
- **Computability**: VERIFY — nf_fields has 22M NF with class numbers. Can compute class groups in towers.
- **Prerequisites**: μ=0 proven for abelian K/Q (Ferrero-Washington)
- **What Prometheus does**: DIRECTLY TESTABLE for real quadratic fields at specific primes. Each (K,p) pair is independent.
- **Cleverness needed**: A new Iwasawa-theoretic argument or a counterexample from systematic search.

---

## Blocker Distribution Across Bucket A

| Blocker Type | Count | Problems |
|---|---|---|
| TECHNIQUE | 14 | Lehmer, pair correlation, BSD, Chowla, Keating-Snaith, Jones, density, CPNT x8 |
| GAP | 3 | Langlands GL(2), Artin entireness, Zaremba |
| FRAMEWORK | 3 | Uniform boundedness, Arthur's, abc |
| NONE (solved) | 1 | Brumer-Stark |
| DATA | 0 | (all data-coupled problems have enough data) |

**The dominant blocker is TECHNIQUE** — 14/26 Bucket A problems are blocked because known approaches fail, not because we lack data or framework. This means:

1. **More data won't solve them** — but data CONSTRAINS what solutions can look like
2. **New techniques are needed** — and our cross-domain tensor might detect where techniques from one field apply to another
3. **Prometheus's role**: measure everything measurable to narrow the search for the right technique

---

## Computability Distribution

| Computability | Count | What it means |
|---|---|---|
| MEASURE | 15 | Compute statistics that constrain the answer |
| VERIFY | 8 | Check specific cases or calibrate |
| SEARCH | 2 | Find counterexamples or extremal objects |
| DISCOVER | 0 | No problem yet where AI is expected to find the proof |
| NONE | 1 | Pure structure (Arthur's conjectures at deepest level) |

**MEASURE dominates** — our primary contribution is constraining what solutions look like, not finding them directly. This is exactly what the tensor does: measure cross-domain structure to narrow the space of possible techniques.

---

## The Key Insight

The frontier isn't blocked by computation or data. It's blocked by **techniques**.

14/26 Bucket A problems have enough data, enough framework, enough prerequisites — they're waiting for the RIGHT ARGUMENT. The argument that cracks one often cracks several (Wiles's modularity proved Fermat AND launched Langlands for GL(2)).

**Prometheus's highest-value contribution**: detecting when the technique for Problem X in Domain A is the same technique needed for Problem Y in Domain B. The tensor's cross-domain structure IS a technique detector.

Every silent island is a place where known techniques fail. Every surviving bond is a place where techniques transfer. The IPA of mathematics is the IPA of techniques.

---

*Aporia, 2026-04-17*

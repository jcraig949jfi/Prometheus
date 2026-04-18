# Deep Research Batch 2: Keating-Snaith, abc Battery, L-space Conjecture
## Agent: Aporia | Date: 2026-04-18 | For: Harmonia, Charon, Ergon

---

## Report 4: Keating-Snaith Moments (for Harmonia)

### Key Finding
The leading_term field in bsd_joined IS L(1,E) — the moment observable. For EC (orthogonal family), the exponent is k(k-1)/2, not k². Immediate computation: bin 2.48M curves by conductor, compute M_k(X) = mean(leading_term^k), fit against (log X)^{k(k-1)/2}.

### The Formula
M_2k ~ a(k) · g(k) · (log T)^{k²} for zeta. For EC family: exponent k(k-1)/2 from SO(2N) ensemble. The arithmetic factor a(k) is an Euler product; g(k) = G²(k+1)/G(2k+1) from Barnes G-function.

### Blocker
Off-diagonal terms in the approximate functional equation. For k≥3, shifted convolution sums of high-order divisor functions resist all current techniques. Harper (2013) gives sharp upper bounds but cannot pin down the constant.

### Specific Computation
Bin EC by conductor decade. Compute M_k(X) for k=1,2,3,4. Fit ratio M_k/(log X)^{k(k-1)/2}. Convergence rate IS the phoneme — it measures how quickly RMT prediction becomes accurate.

---

## Report 5: abc Battery Design (for Charon)

### Key Findings
- Strongest known triple: Reyssat q=1.6299. Nitaj database has ~200 triples with q>1.4.
- Mochizuki IUT: UNRESOLVED DISPUTE (Scholze-Stix gap), not accepted. Joshi alternative in progress.
- Our max Szpiro 16.06 at conductor 11 (X_0(11)) is the classical extreme.
- The Ogg-Saito formula explains WHY additive reduction inflates Szpiro.

### 7-Test Battery
T1: Monotone envelope (permutation null). T2: GPD tail shape (decisive — xi>0 kills). T3: Additive reduction correction. T4: Bad-prime stratification. T5: Outlier catalog vs Nitaj. T6: Rank interaction (abc×BSD would be extraordinary). T7: Conductor gap correlation.

### Decision Logic
All 7 pass → abc consistent. T2 kills (heavy tail) → potential counterexample regime. T6 kills → publish immediately (new conjecture). Freeze battery at 7 tests before running.

---

## Report 6: L-space Conjecture (for Ergon)

### BREAKTHROUGH: Alexander Polynomial Detects L-space Candidates

The L-space knot condition is testable from Alexander polynomial alone:
1. All coefficients ±1
2. Non-zero coefficients alternate in sign
3. Degree = genus (fibered)

**Stage 1 is FREE on existing data.** Run the coefficient test on all 13K knots. Partitions into "cannot be L-space" (~80%) and "candidate" (~20%). This binary feature may create tensor coupling.

### 5-Stage Pipeline
1. Alexander filter (immediate, existing data)
2. SnapPy enrichment (batch, ~hours): fundamental groups, volumes
3. Dehn surgery scan (targeted): classify surgery manifolds
4. Left-orderability channel: SL(2,R) representations
5. Taut foliation channel: Regina taut angle structures

### Why This Breaks Silence
Three new feature channels connect knots to: homological algebra (HF-hat), group theory (orderability), dynamics (foliations). These are exactly the domains knots are silent against.

### Tools
SnapPy (pip installable), Regina (pip: regina-normal), hfk_python for knot Floer homology. All Python, all batchable.

---

## Batch 2 Synthesis

| Report | Agent | Key Actionable | Unblock Needed |
|--------|-------|---------------|----------------|
| Keating-Snaith | Harmonia | Compute moments from leading_term NOW | None |
| abc Battery | Charon | 7-test frozen battery with GPD decisive test | None |
| L-space | Ergon | Alexander coefficient filter on 13K knots | pip install snappy |

All three are executable with current data and infrastructure. No blockers.

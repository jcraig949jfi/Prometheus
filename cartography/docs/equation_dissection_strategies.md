# Equation Dissection Strategies — Extracting Hidden Geometry from Mathematical Formulas

## Project Prometheus / Charon v5 Planning
### 2026-04-09

---

## Vision

Every mathematical formula is a compressed representation of geometric, algebraic, and analytic structure. We have 27M parsed formula trees and 12.5M raw LaTeX formulas. Instead of comparing formulas by surface features (operators, depth), we dissect each formula through multiple mathematical lenses — complex plane, fractional derivatives, modular arithmetic, topology — and extract invariant signatures that survive transformation.

The hypothesis: formulas from different mathematical domains that share dissection signatures are structurally related, even when their surface notation looks nothing alike.

---

## Core Strategies (from the manifesto)

### S1. Complex Plane Extension (Analytic Continuation)
**What:** Take real-valued formulas and evaluate them on complex inputs. The resulting landscape (poles, zeros, branch cuts, saddle points) is a geometric signature.

**How:**
1. Parse formula to executable Python (sympy or direct evaluation)
2. Evaluate on a grid in the complex plane: z = x + iy, x,y in [-10, 10], 200x200 grid
3. Extract: pole locations, zero locations, branch cut topology, phase portrait
4. Signature: sorted list of (|pole|, order) + (|zero|, multiplicity) + winding numbers

**GPU opportunity:** Grid evaluation is embarrassingly parallel. 200x200 = 40K points per formula. With 27M formulas, batch on GPU.

**Existing data:** Phase portrait databases exist for common functions (Wegert's visual complex analysis). DLMF (NIST Digital Library of Mathematical Functions) has complex-plane data for special functions.

**Tractability:** TRACTABLE for formulas expressible as closed-form functions. INTRACTABLE for formulas involving infinite sums or integrals without closed form.

**Priority:** 9/10 — highest signal-to-noise ratio. Poles and zeros are THE invariants of complex analysis.
**Execution time:** ~2 hours for 100K formulas on GPU, weeks for 27M.

---

### S2. Fractional Derivative Signatures
**What:** Compute the alpha-th derivative for non-integer alpha (0.5, 1.5, pi, e). The fractional derivative of a function encodes its "memory" — how it depends on its entire history, not just local behavior.

**How:**
1. For polynomial/power-law formulas: Riemann-Liouville fractional derivative has closed form
   D^alpha(x^n) = Gamma(n+1)/Gamma(n+1-alpha) * x^(n-alpha)
2. For general formulas: numerical Grünwald-Letnikov approximation on discretized domain
3. Compute D^0.5, D^1.5, D^(pi) for each formula
4. Signature: vector of (D^alpha(f) at x=1, x=e, x=pi) for alpha in {0.5, 1.5, sqrt(2), pi}

**GPU opportunity:** Grünwald-Letnikov is a weighted sum — fully parallelizable.

**Existing data:** Fractional calculus tables exist for elementary functions (Podlubny's tables). scipy has no fractional derivative, but `differint` package does.

**Tractability:** TRACTABLE for polynomial/rational formulas. MODERATE for transcendental. INTRACTABLE for formulas with undetermined parameters.

**Priority:** 7/10 — novel signatures, but interpretation is harder than complex plane.
**Execution time:** ~30 min for 100K polynomial formulas.

---

### S3. Modular Arithmetic Projection (Clock Math)
**What:** Evaluate formulas mod p for small primes p = 2, 3, 5, 7, 11, 13. In modular arithmetic, continuous curves become discrete point patterns. The pattern is a signature.

**How:**
1. For polynomial formulas f(x): compute f(x) mod p for x = 0, 1, ..., p-1
2. Result: a vector of p values in Z_p — the "modular fingerprint"
3. For multivariate: compute f(x,y) mod p on the full grid → a p×p matrix
4. Signature: the modular fingerprint vector for each prime, concatenated
5. Cross-formula comparison: two formulas with identical modular fingerprints mod p for multiple primes are likely algebraically related (Schwartz-Zippel)

**GPU opportunity:** Modular evaluation is integer arithmetic — extremely fast on GPU.

**Existing data:** This is essentially what LMFDB does for L-functions (a_p coefficients are f(p) mod p evaluations). Our EC data already has these. Extending to arbitrary formulas is the novel step.

**Tractability:** HIGHLY TRACTABLE. Integer arithmetic, no floating point, no convergence issues.

**Priority:** 10/10 — fastest to implement, directly connects to our LMFDB data, and Schwartz-Zippel gives theoretical foundation.
**Execution time:** ~10 min for 1M formulas on GPU.

---

### S4. Topological Signatures (Genus, Betti Numbers, Euler Characteristic)
**What:** View a formula as defining a surface/variety. Compute its topological invariants — properties that survive continuous deformation.

**How:**
1. For algebraic formulas f(x,y) = 0: defines a curve. Genus = (d-1)(d-2)/2 for smooth degree-d curves.
2. For f(x,y,z) = 0: defines a surface. Compute Euler characteristic from degree.
3. For parametric families: track how topology changes as parameters vary (singularity theory)
4. Persistent homology: discretize the level sets of f, compute Betti numbers at multiple thresholds
5. Signature: (genus, Euler_char, Betti_0, Betti_1, Betti_2, ...)

**GPU opportunity:** Persistent homology (ripser) has GPU implementations (ripser++).

**Existing data:** Genus-2 curves in our dataset already have topological classification. KnotInfo has knot genus. mathlib has formalized topology.

**Tractability:** TRACTABLE for low-degree polynomial formulas. MODERATE for transcendental (need numerical discretization). INTRACTABLE for formulas with singularities or undefined regions.

**Priority:** 8/10 — topological invariants are the gold standard for "same shape, different coordinates."
**Execution time:** ~1 hour for 100K polynomial formulas.

---

### S5. Fourier/Spectral Decomposition
**What:** Run each formula through a mathematical prism. Decompose into frequency components. The power spectrum is rotation/translation invariant.

**How:**
1. Evaluate formula on uniform grid (1024 points in [0, 2pi] or [-10, 10])
2. FFT → power spectrum (magnitudes of frequency components)
3. Signature: top-K frequency magnitudes, spectral centroid, spectral bandwidth, spectral entropy
4. For 2D formulas: 2D FFT → power spectrum as image → rotationally average

**GPU opportunity:** FFT is the canonical GPU operation. cuFFT handles millions of transforms per second.

**Existing data:** Our formula_survey already computed operator frequencies. This goes deeper — frequency content of the EVALUATED formula, not the parsed tree.

**Tractability:** HIGHLY TRACTABLE. FFT works on any discretized signal.

**Priority:** 8/10 — proven technique, fast, invariant-rich.
**Execution time:** ~5 min for 1M formulas on GPU.

---

### S6. Phase Space / Attractor Geometry
**What:** For formulas describing dynamics (differential equations, recurrences), plot variable vs rate-of-change. The resulting trajectory shape (attractor) is a geometric signature.

**How:**
1. For recurrence relations a(n+1) = f(a(n)): iterate, plot (a(n), a(n+1)) → attractor
2. For ODEs dy/dx = f(x,y): solve numerically, plot phase portrait
3. Extract: fixed points, limit cycles, Lyapunov exponents, fractal dimension of attractor
4. Signature: (n_fixed_points, largest_lyapunov, fractal_dim, attractor_type)

**GPU opportunity:** Iteration of recurrences is massively parallel across different initial conditions.

**Existing data:** OEIS sequences are effectively iterated recurrences. We have 394K sequences — each one's phase portrait is extractable.

**Tractability:** TRACTABLE for explicit recurrences. MODERATE for implicit/parameterized. INTRACTABLE for formulas without iterative structure.

**Priority:** 7/10 — directly applicable to OEIS sequences, novel cross-domain signature.
**Execution time:** ~30 min for 100K sequences.

---

### S7. p-adic Evaluation (Ultrametric Geometry)
**What:** Evaluate formulas in p-adic number systems. The p-adic absolute value creates a totally different geometry — fractal, ultrametric, disconnected. Formulas that look smooth in real numbers may shatter into interesting patterns in p-adic space.

**How:**
1. For polynomial f(x): compute p-adic valuation v_p(f(n)) for n = 1, 2, ..., N
2. The sequence of p-adic valuations is a signature
3. Compare: two formulas with same p-adic valuation sequence for multiple primes are p-adically equivalent
4. Newton polygon: for polynomial f(x) = sum(a_i * x^i), plot (i, v_p(a_i)). The lower convex hull (Newton polygon) determines p-adic roots.

**GPU opportunity:** p-adic valuation is integer factorization → moderately parallelizable.

**Existing data:** Our LMFDB data includes conductor factorizations (which encode p-adic information). Isogeny graphs are p-adic objects. This connects directly to Langlands-type bridges.

**Tractability:** TRACTABLE for polynomials with integer coefficients. MODERATE for transcendental. INTRACTABLE for formulas with irrational coefficients.

**Priority:** 9/10 — directly connects to our number-theoretic datasets, p-adic geometry is where modularity lives.
**Execution time:** ~20 min for 100K formulas.

---

### S8. Level Set Topology (Morse Theory)
**What:** For a function f(x,y,...), fix f = c for different constants c. The topology of the level set {x : f(x) = c} changes at critical values of c. These changes (births/deaths of connected components, holes) are the Morse-theoretic signature.

**How:**
1. Evaluate f on a dense grid
2. Sweep threshold c from min to max
3. At each c, compute connected components and holes (Betti numbers) of {f >= c}
4. Record birth-death pairs → persistence diagram
5. Signature: persistence diagram (equivalently, persistence landscape or Betti curve)

**GPU opportunity:** Level set computation on grids is parallel. Persistent homology has GPU implementations.

**Existing data:** This is what TDA (topological data analysis) does. Libraries: ripser, gudhi, giotto-tda.

**Tractability:** TRACTABLE for formulas evaluable on grids. INTRACTABLE for high-dimensional formulas (curse of dimensionality above ~5D).

**Priority:** 7/10 — rich invariants, but expensive in high dimensions.
**Execution time:** ~2 hours for 100K formulas (2D grids).

---

## Extended Strategies (20 more)

### S9. Symmetry Group Detection
Compute the symmetry group of a formula: which transformations (rotation, reflection, translation, scaling) leave it invariant? Two formulas with isomorphic symmetry groups share structural DNA.
**Tractability:** MODERATE. **Priority:** 8/10. **Time:** ~1 hour/100K.

### S10. Galois Group of Polynomial Roots
For polynomial formulas, compute the Galois group of the splitting field. This encodes exactly which roots are algebraically related.
**Tractability:** TRACTABLE for degree <= 10. **Priority:** 9/10. **Time:** ~30 min/100K.

### S11. Monodromy Representation
As you move a parameter around a loop in complex space, the solutions of an equation permute. This permutation group (monodromy) is an invariant.
**Tractability:** MODERATE. **Priority:** 7/10. **Time:** ~2 hours/100K.

### S12. Zeta Function of a Variety
For algebraic formulas over finite fields, count solutions mod p for many primes. The generating function of these counts is the Hasse-Weil zeta function — a deep invariant connecting geometry to number theory.
**Tractability:** TRACTABLE (integer arithmetic). **Priority:** 10/10. **Time:** ~15 min/100K on GPU.

### S13. Discriminant and Resultant
For polynomial systems, the discriminant tells you when two roots collide. The resultant tells you when two equations share a root. Both are algebraic invariants computable by determinants.
**Tractability:** HIGHLY TRACTABLE. **Priority:** 8/10. **Time:** ~5 min/100K.

### S14. Newton Polytope
For multivariate polynomials, the convex hull of the exponent vectors. Encodes the "shape" of the equation in exponent space. Two formulas with the same Newton polytope have similar algebraic complexity.
**Tractability:** HIGHLY TRACTABLE. **Priority:** 7/10. **Time:** ~5 min/100K.

### S15. Gröbner Basis Signature
Compute the Gröbner basis of the ideal generated by a formula. The leading terms of the Gröbner basis are invariant under coordinate changes and encode the algebraic complexity.
**Tractability:** MODERATE (can be exponential for complex systems). **Priority:** 6/10. **Time:** variable.

### S16. Hodge Diamond / Mixed Hodge Structure
For algebraic varieties, the Hodge numbers h^{p,q} form a diamond pattern that encodes the "shape of the shape." This is THE signature in algebraic geometry.
**Tractability:** INTRACTABLE for general formulas, TRACTABLE for smooth hypersurfaces. **Priority:** 6/10. **Time:** ~1 hour for smooth cases.

### S17. Motivic Integration
Count solutions weighted by geometric measure. The motivic integral is a universal invariant that specializes to many others (Euler characteristic, Hodge numbers, point counts).
**Tractability:** INTRACTABLE computationally. **Priority:** 3/10 (theoretical value high, practical value low). **Time:** N/A.

### S18. Tropical Geometry Skeleton
Replace addition with min and multiplication with addition. Every algebraic variety has a "tropical skeleton" — a piecewise-linear graph that preserves combinatorial structure.
**Tractability:** TRACTABLE for polynomials. **Priority:** 8/10. **Time:** ~30 min/100K.

### S19. Singularity Classification (Arnold)
At singular points of a formula, classify the singularity type (A_n, D_n, E_6, E_7, E_8). The ADE classification is universal — it appears in algebra, geometry, physics, and representation theory.
**Tractability:** MODERATE. **Priority:** 9/10 (ADE is a known cross-domain bridge). **Time:** ~1 hour/100K.

### S20. Differential Galois Group
For differential equations, the Galois group of the solution space. Encodes which solutions are expressible in closed form and how they relate.
**Tractability:** MODERATE for linear ODEs. **Priority:** 7/10. **Time:** ~1 hour/100K.

### S21. Automorphic Form Association
Check if a formula's L-function matches a known automorphic form. This is the Langlands program in computational form.
**Tractability:** MODERATE (need to compute enough L-function coefficients). **Priority:** 10/10 (this IS the modularity theorem). **Time:** ~2 hours/100K.

### S22. Operadic Structure
View the formula as an element of an operad — an algebraic structure encoding how operations compose. Two formulas with the same operadic type are structurally equivalent.
**Tractability:** TRACTABLE from our operator trees. **Priority:** 8/10. **Time:** ~10 min/100K.

### S23. Convexity Profile
Compute the Hessian of a formula. The eigenvalue signature of the Hessian at sampled points tells you the local curvature landscape — convex, concave, saddle, flat.
**Tractability:** HIGHLY TRACTABLE. **Priority:** 7/10. **Time:** ~10 min/100K.

### S24. Information-Theoretic Signature
Compute the Kolmogorov complexity (approximated by compression ratio) and Shannon entropy of the formula's output sequence. Formulas that produce similarly compressible outputs may share generative structure.
**Tractability:** HIGHLY TRACTABLE. **Priority:** 6/10. **Time:** ~5 min/100K.

### S25. Renormalization Group Flow
Apply successive coarse-graining to a formula (average over local neighborhoods at increasing scales). The fixed points of this flow are scale-invariant signatures — they're the same at every resolution.
**Tractability:** MODERATE. **Priority:** 7/10. **Time:** ~30 min/100K.

### S26. Spectral Curve / Characteristic Polynomial
For matrix-valued formulas or operator families, the eigenvalue locus as parameters vary traces a curve in the complex plane — the spectral curve. Its genus and singularities are invariants.
**Tractability:** MODERATE. **Priority:** 8/10. **Time:** ~1 hour/100K.

### S27. Arithmetic Dynamics (Orbit Portraits)
For iterated formulas f(f(f(...(x)))), the orbit structure (fixed points, cycles, preperiodic points) over finite fields gives a graph whose invariants are arithmetic-dynamical signatures.
**Tractability:** TRACTABLE. **Priority:** 7/10. **Time:** ~20 min/100K.

### S28. Resurgence / Borel Summation
For divergent series (which many physical formulas are), Borel summation assigns finite values. The singularities of the Borel transform encode non-perturbative information invisible to the original series.
**Tractability:** MODERATE for series with known coefficients. **Priority:** 6/10. **Time:** ~1 hour/100K.

---

## Priority Rankings

### Tier 1: Implement immediately (high value, tractable)
| # | Strategy | Priority | Time/100K | GPU? |
|---|----------|----------|-----------|------|
| S3 | Modular arithmetic projection | 10 | 10 min | Yes |
| S12 | Zeta function of variety | 10 | 15 min | Yes |
| S21 | Automorphic form association | 10 | 2 hours | No |
| S1 | Complex plane extension | 9 | 2 hours | Yes |
| S7 | p-adic evaluation | 9 | 20 min | Partial |
| S10 | Galois group of roots | 9 | 30 min | No |
| S19 | Singularity classification (ADE) | 9 | 1 hour | No |

### Tier 2: Build next (moderate effort, high value)
| # | Strategy | Priority | Time/100K | GPU? |
|---|----------|----------|-----------|------|
| S5 | Fourier/spectral decomposition | 8 | 5 min | Yes |
| S4 | Topological signatures | 8 | 1 hour | Yes |
| S9 | Symmetry group detection | 8 | 1 hour | No |
| S13 | Discriminant/resultant | 8 | 5 min | No |
| S18 | Tropical geometry skeleton | 8 | 30 min | No |
| S22 | Operadic structure | 8 | 10 min | No |
| S26 | Spectral curve | 8 | 1 hour | No |

### Tier 3: Queue for later (specialized or expensive)
| # | Strategy | Priority | Time/100K | GPU? |
|---|----------|----------|-----------|------|
| S2 | Fractional derivatives | 7 | 30 min | Yes |
| S6 | Phase space / attractors | 7 | 30 min | Yes |
| S8 | Level set topology (Morse) | 7 | 2 hours | Yes |
| S11 | Monodromy | 7 | 2 hours | No |
| S14 | Newton polytope | 7 | 5 min | No |
| S20 | Differential Galois group | 7 | 1 hour | No |
| S23 | Convexity profile (Hessian) | 7 | 10 min | No |
| S25 | Renormalization group flow | 7 | 30 min | No |
| S27 | Arithmetic dynamics | 7 | 20 min | No |

### Tier 4: Theoretical / long-term
| # | Strategy | Priority | Notes |
|---|----------|----------|-------|
| S15 | Gröbner basis | 6 | Can be exponential |
| S16 | Hodge diamond | 6 | Only for smooth cases |
| S24 | Information-theoretic | 6 | Indirect signal |
| S28 | Resurgence / Borel | 6 | Needs series coefficients |
| S17 | Motivic integration | 3 | Computationally intractable |

---

## Existing Datasets with Pre-Computed Signatures

| Dataset | What's already computed | Relevant strategies |
|---------|------------------------|-------------------|
| **LMFDB EC** | a_p coefficients (= S3 mod-p evaluation), conductor (= S7 p-adic), rank, L-function zeros | S3, S7, S12, S21 |
| **LMFDB MF** | Hecke eigenvalues (= S3), level, weight, Atkin-Lehner signs | S3, S21 |
| **Genus-2** | Sato-Tate group (= S9 symmetry), conductor, discriminant | S9, S10, S12 |
| **KnotInfo** | Alexander polynomial (= S10 Galois), Jones polynomial, genus (= S4 topology) | S4, S5, S10, S13 |
| **NumberFields** | Discriminant (= S13), Galois group (= S10), regulator, class number | S7, S10, S13 |
| **Isogenies** | Supersingular primes (= S7 p-adic), adjacency (= S26 spectral) | S7, S12, S26 |
| **Fungrim** | Formula symbols (= S22 operadic), function types | S1, S22 |
| **OEIS** | Term sequences (= S6 attractors), growth rates (= S5 spectral) | S5, S6, S24, S27 |
| **Maass** | Spectral parameters (= S26), Fricke eigenvalues | S1, S5, S26 |
| **Materials** | Band gaps, space groups (= S9 symmetry) | S4, S9 |

**Key insight:** LMFDB already HAS S3 and S7 data. Our existing datasets are partial dissections. The novel contribution is applying ALL strategies to ALL formulas systematically, and comparing signatures ACROSS domains.

---

## Implementation Architecture

```
27M parsed formula trees (formula_trees.jsonl)
         |
         v
    formula_to_executable.py        (tree → sympy/numpy callable)
         |
    ┌────┼────┬────┬────┬────┐
    v    v    v    v    v    v
   S1   S3   S5   S7   S12  S22   (parallel dissection strategies)
   |    |    |    |    |    |
   v    v    v    v    v    v
  signature vectors per formula (one per strategy)
         |
         v
    signature_index.py              (unified index: formula → [signatures])
         |
         v
    cross_domain_matching.py        (find formulas with similar signatures from different domains)
         |
         v
    falsification_battery.py        (test every claimed match)
         |
         v
    shadow_tensor                   (fed with results)
```

**The first step is `formula_to_executable.py`** — converting our operator trees back into evaluable functions. Without that, none of the evaluation-based strategies (S1, S2, S3, S5, S6, S7) can run. The tree-based strategies (S14, S18, S22) can run directly on the parsed trees.

---

## GPU Strategy

Our card: 17GB VRAM (RTX, likely 4060 Ti or similar).

| Strategy | GPU kernel | VRAM needed | Throughput |
|----------|-----------|-------------|------------|
| S3 mod-p | Integer arithmetic grid | <1GB | 10M formulas/min |
| S5 FFT | cuFFT batch | ~2GB for 100K | 1M formulas/min |
| S1 complex grid | Float32 grid eval | ~4GB for 200x200 | 100K formulas/min |
| S4 persistence | ripser++ | ~4GB | 10K formulas/min |
| S2 fractional deriv | Weighted sum | <1GB | 1M formulas/min |

For S3 (modular arithmetic), we could process ALL 27M formulas on GPU in under 3 hours.

---

*This document is a strategy database. Each strategy has: description, algorithm, GPU applicability, existing data, tractability, priority, execution time. New strategies are appended with sequential numbering. Scores are updated as we learn what works.*

*Charon v5 planning — 2026-04-09*

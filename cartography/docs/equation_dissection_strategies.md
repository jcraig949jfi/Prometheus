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

### S29. Differential Galois Theory (Picard-Vessiot)
**From Gemini review.** For linear differential equations, the differential Galois group tells you whether solutions can be expressed in elementary functions at all. This is a HARD invariant — it's not a statistical test, it's an algebraic classification.
**Tractability:** MODERATE (Kovacic's algorithm for order 2, harder for higher order). **Priority:** 8/10. **Time:** ~1 hour/10K (order 2 only).
**Connection:** Extends S10 (polynomial Galois groups) to the differential setting. If two equations from different domains have isomorphic differential Galois groups, their solution spaces have the same algebraic structure.

### S30. Tropicalization (Tropical Semiring)
**From Gemini review.** Replace addition with max/min, multiplication with addition. Smooth algebraic curves snap into piecewise-linear skeletons. The combinatorial properties of these skeletons (edge lengths, vertex connections, genus of the tropical curve) are robust, easily comparable signatures.
**Tractability:** TRACTABLE for polynomials (essentially Newton polygon + subdivision). **Priority:** 8/10. **Time:** ~30 min/100K.
**Connection:** Extends S14 (Newton polytope) and S18 (tropical geometry). The tropical skeleton is coarser than the full variety but captures the combinatorial backbone.
**Note:** S18 was listed earlier but S30 emphasizes the skeletal graph as a comparable signature, not just the tropical variety itself.

---

## Retrieval Architecture

### The cross-domain matching problem

With 8+ signature types per formula across 27M formulas, the matching question is: how do we find formulas from different domains that share signatures?

### Tiered matching (Gemini's suggestion — adopted)

**Tier 1: Exact match on hard invariants.**
- Mod-p fingerprint (S3): identical mod-p vectors = algebraically equivalent (Schwartz-Zippel)
- Newton polytope vertex hash (S14): identical exponent structure
- Operadic skeleton hash (S22): identical computational pattern
- Parity + variable symmetry order (S9): identical symmetry class

These are exact, discrete signatures. Use hash-based lookup (dict/set). O(1) per query.

**Tier 2: Approximate match on soft invariants.**
- Spectral signature (S5): cosine similarity on 14-float vectors
- Convexity profile (S23): Euclidean distance on curvature vectors
- Discriminant value (S13): log-ratio within tolerance

These are continuous signatures. Use approximate nearest neighbor (FAISS, annoy, or sklearn BallTree).

**Tier 3: Cross-tier confirmation.**
A claimed bridge must match on at least 1 Tier-1 invariant AND 2 Tier-2 invariants. This prevents:
- False positives from single-invariant coincidence
- Combinatorial explosion from soft matching alone

### Implementation plan
```
formula_signatures_index.py
  1. Load all per-formula signature files
  2. Build hash indices for Tier 1 (dict: hash -> [formula_ids])
  3. Build FAISS index for Tier 2 (concatenated soft vectors)
  4. For each Tier 1 match across domains:
     a. Check Tier 2 distance
     b. If passes: run falsification battery
     c. Feed result to shadow tensor
```

### Tensor train compression (Gemini's suggestion — queued)

When the full signature matrix is built (27M formulas × 50+ signature dimensions), tensor train decomposition can compress the representation while preserving the invariant structure. The bond dimensions between TT cores reveal which signature types are entangled — e.g., if mod-p fingerprint and Newton polytope are strongly correlated, the bond dimension between those cores will be high.

This is queued for after the signature extractors are complete and we have actual data to compress.

---

## Shadow Tensor as Contrastive Space

### The twilight zone (Gemini's question — answered)

The transition between Illuminated (known truths, battery survivors) and Shadow (killed hypotheses, failed bridges) is NOT a hard binary boundary. The shadow tensor already encodes a continuous gradient:

1. **Illuminated:** 180/180 calibration truths. Known theorems. Battery survivors with high z-scores.
2. **Twilight:** Hypotheses that survive some battery tests but fail others. Near-misses. The 41 regime changes (real but modest). The Maass↔MF survivor (Tier 3, speculative).
3. **Shadow:** 9 killed false discoveries. 18K+ falsified hypotheses. The prime atmosphere (96% of all signal).
4. **Void:** Untested regions. The 10 FindStat zero-test pairs. The 50 frontier targets.

The novelty scorer's surprise component measures gradient — how different is a region's battery behavior from its neighbors? High surprise = the boundary is unexpected. That's where the system actively attempts to construct bridges between known truth and known failure.

The shadow tensor IS the contrastive space. Every test record positions a hypothesis on the gradient. Tensor train decomposition across both spaces reveals the geometric shape of the boundary — where does mathematical truth break down, and what structural signature predicts the break?

---

## Speed Hacks (from literature survey 2026-04-09)

### Batch Processing
- **Mod-p:** NumPy vectorized `%` → 100M ops/sec. CuPy drop-in for GPU. `python-flint` for polynomial mod-p: 1M polys/sec degree <20.
- **FFT:** `numpy.fft.rfft` accepts 2D arrays — pass all sequences as matrix rows → 100x faster than looping. `scipy.fft` with `workers=-1` for multithreaded. CuPy `cufft` → 100M length-64 FFTs/sec.
- **Newton polygon:** Lower convex hull of (i, v_p(a_i)). `scipy.spatial.ConvexHull` or Graham scan. 1M polygons/sec vectorized.
- **Polynomial roots:** Stack companion matrices, single `numpy.linalg.eigvals` call. ~50K degree-10 polys/sec.

### Libraries
- **python-flint:** Polynomial arithmetic over GF(p). Gold standard. `pip install python-flint`.
- **cypari2:** PARI/GP Python bindings. Galois groups up to degree 11. `pip install cypari2`.
- **giotto-tda:** Persistent homology with sklearn API. Batch via joblib. `pip install giotto-tda`.
- **ripser++:** GPU persistent homology. 30-50x over ripser. Handles 50K points.
- **galois:** NumPy-based GF(p) arithmetic including NTT. `pip install galois`.
- **mpsolve:** Aberth's method for polynomial roots. O(n^2) vs O(n^3).

### External Tools (subprocess)
- **Gfan:** Tropical varieties. Fast for single polynomials.
- **Singular:** ADE singularity classification via `classify` command.
- **polymake/OSCAR:** Tropical geometry. Julia-based (OSCAR) is most active.

---

*This document is a strategy database. Each strategy has: description, algorithm, GPU applicability, existing data, tractability, priority, execution time. New strategies are appended with sequential numbering. Scores are updated as we learn what works.*

---

### S31. Functional Equation Symmetry
**From Claude review.** Many important formulas satisfy functional equations: f(1-s) = ...f(s) (reflection), f(x+1) = ...f(x) (shift), f(cx) = ...f(x) (scaling). The type is a discrete invariant. L-functions have reflection symmetry. Gamma has shift. EC and modular forms SHARE a functional equation — directly relevant to the modularity benchmark.
**Tractability:** MODERATE (need to detect functional equations from tree structure). **Priority:** 9/10. **Time:** ~1 hour/50K.

### S32. Coefficient Field
**From Claude review.** For polynomial formulas, what number field do the coefficients live in? Rational, quadratic extension, cyclotomic? Computable from parsed trees by checking if coefficients are integers, rationals, or algebraic. Connects directly to NumberFields dataset.
**Tractability:** TRACTABLE for polynomials with explicit coefficients. **Priority:** 8/10. **Time:** ~10 min/100K.

### S33. Recursion Operator Extraction
**From Claude review.** For OEIS sequences defined by recurrences, extract the recurrence operator as an algebraic object. Two sequences with isomorphic recurrence operators (same characteristic polynomial up to scaling) are structurally related regardless of initial conditions. Strongest bridge between OEIS and algebraic datasets.
**Tractability:** TRACTABLE for linear recurrences (Berlekamp-Massey). **Priority:** 9/10. **Time:** ~20 min/100K sequences.

---

## TRIAGE: The Selection Principle (from Claude review 2026-04-09)

### The problem
30 strategies × 27M formulas = 810M computations. Even Tier 1 (7 strategies) = 189M. This is a combinatorial bomb.

### The solution: targeted dissection
Don't dissect everything. Dissect the formulas that MATTER — the ones near boundaries where scalar methods failed but structural methods haven't been tried.

### Priority formula sets (dissect these first)

**Set A: OEIS-Fungrim bridges (16,774 formulas)**
Formulas connected to OEIS through shared mathematical functions (zeta, gamma, Dirichlet). These are known cross-domain objects. If structural signatures can't find bridges HERE, they won't find them anywhere.

**Set B: Expected bridge targets (~5K formulas)**
Formulas directly associated with objects in our calibration targets: EC equations (Weierstrass models), modular form q-expansions, knot polynomials (Alexander, Jones), number field minimal polynomials.

**Set C: Shadow tensor hot spots (~10K formulas)**
Formulas from domains where the shadow tensor shows near-misses or high surprise scores. These are regions where the battery almost passed — structural signatures might push them over.

**Set D: Erdos problem formulas (~1K)**
Formulas from the 271 OEIS sequences referenced by open Erdos problems.

**Total targeted set: ~30K formulas** (not 27M)

### Execution order
1. Run S3 (mod-p) + S22 (operadic) on Set A (16,774 formulas) → battery → shadow tensor
2. Run S13 (discriminant) + S14 (Newton polytope) on Set B (5K) → battery → shadow tensor
3. If signal found: scale to Set C, then full corpus
4. If no signal in targeted sets: 27M won't help. Rethink representation.

### DeepSeek correction: 30K is still too many. Start with <500.

**Ultra-targeted set (dissect these FIRST):**
1. **271 Erdos OEIS sequences** — mathematically guaranteed non-trivial structure (Set D, promoted to first)
2. **50 frontier targets** — highest novelty/surprise in concept embedding
3. **41 regime change survivors** — real asymptotic corrections, already battery-verified
4. **Formulas appearing in 2+ of our datasets with degree >= 3** — maybe 50-100

**Total: ~400 formulas.** Not 30K. Not 27M.

If no high-surprise bridges emerge from 400 targeted formulas, 30K won't help. If they do, scale up.

**Claude's maxim: "You have enough strategies. What you need now is triage."**
**DeepSeek's correction: "Your triage isn't aggressive enough."**

### S34. Categorical Equivalence (Functoriality)
**From DeepSeek review.** Two formulas from different domains are related if there exists a natural transformation between the categories they live in. For each formula, compute its "categorical context" — the minimal mathematical category that contains it (Set, Grp, Top, Sch, etc.) using the Mathlib/Metamath proof graph. Two formulas from different categories cannot be directly isomorphic, but they can be related by an adjunction. Signature: (source_category, target_category, adjunction_type).
**Tractability:** TRACTABLE (proof graph is finite, category assignment is lookup + graph traversal). **Priority:** 9/10. **Time:** ~30 min/1K formulas.
**Connection:** Directly addresses Langlands-style bridges. Modularity theorem IS a functor between categories of elliptic curves and categories of modular forms.

---

## Surprise Definition (from DeepSeek review 2026-04-09)

The current surprise score (KL divergence on battery profiles) is under-specified. DeepSeek's correction:

**Formal surprise = (predicted_survival - actual_survival)²**

Implementation:
1. Train an ensemble of weak predictors (random forest on Tier-2 signature features) to predict: given a formula's signatures, what is P(battery survival)?
2. For each new formula, compute predicted P(survival)
3. After battery: surprise = (predicted - actual)²
4. High surprise = the formula behaved differently than its signatures predict
5. **Dissect only formulas with surprise > 2σ**

This turns the shadow tensor into an active learning system: it prioritizes formulas that would teach it the most, not formulas that confirm what it already knows.

**Why this matters:** Flooding the pipeline with 30K formulas where 29,500 behave exactly as predicted wastes compute. The 500 that surprise the predictor are where the bridges hide.

---

## Transformation Complexity (from DeepSeek review 2026-04-09)

M1 (transformation catalog) will produce thousands of candidate leaf mappings between formulas. Most are trivial (rename x→y).

**Filter:** transformation_complexity = n_nodes_in_mapping / min(tree_size_a, tree_size_b)

Keep only transformations with complexity ≤ 0.3. These are non-obvious structural mappings where the transformation itself encodes mathematical content, not just notation change.

Then cluster surviving transformations by type:
- Fourier-type (frequency ↔ time)
- Mellin-type (multiplicative ↔ additive)
- Legendre-type (variable ↔ dual variable)
- Substitution-type (algebraic change of variable)
- Gauge-type (symmetry transformation preserving invariants)

That cluster graph is the hidden geometry of mathematical knowledge.

---

## GPU Memory Fix (from DeepSeek review 2026-04-09)

S1 (complex grid) at 200×200 = 40K points × 100K formulas = 4B evaluations.
At 32 bytes per complex result = 128 GB/min memory traffic. Exceeds 17GB VRAM.

**Fix:**
- Use float16 for grid evaluation (halves memory)
- Store only pole/zero locations, not full grid
- Evaluate in 10K-formula batches, transfer signatures to CPU, discard grid
- Fits in ~12GB VRAM

Apply same batching pattern to S5 (FFT) and S2 (fractional derivatives).

---

## Meta-Strategies: Above the Formula Level (from ChatGPT review 2026-04-09)

### The insight

We're dissecting individual formulas. The deeper game is dissecting the SPACE of formulas — cataloging transformations between them, finding equivalence classes, and compressing to minimal generating kernels.

"The most powerful equations are not those that describe reality — they are those that generate the space of possible realities while remaining invariant under transformation."

### M1. Transformation Catalog

Instead of asking "what signatures does formula A have?" ask "what transformation maps formula A to formula B?" If two formulas from different domains are connected by a known transformation (variable substitution, gauge change, Fourier transform, Legendre transform), that transformation IS the bridge.

**Implementation:**
1. For each pair of formulas with matching Tier 1 signatures (same operadic skeleton, same Newton polytope):
   - Attempt to find a variable substitution that maps one to the other
   - If the trees have same skeleton but different leaves: extract the leaf mapping
   - The leaf mapping IS the cross-domain dictionary
2. Build a "transformation graph": nodes = formulas, edges = transformations, edge labels = transformation type

**This is the S22 operadic skeleton taken one level up.** S22 tells you two formulas have the same computational pattern. M1 tells you what the specific mapping between them is.

### M2. Equation Coordinate System (6-axis scoring)

Score each formula on meta-axes that describe its ROLE, not its algebraic structure:

| Axis | Low | High |
|------|-----|------|
| **Compression Ratio (CR)** | Local approximation (Taylor) | Universal law (Einstein) |
| **Generative Depth (GD)** | Single phenomenon | Emergent layers (QFT → particles → chemistry) |
| **Universality Class (UC)** | Narrow regime (ideal gas) | Cross-scale (renormalization) |
| **Symmetry Encoding Density (SED)** | Low symmetry (F=ma) | Dense symmetry (Yang-Mills) |
| **Computational Irreducibility (CI)** | Shortcuttable (linear) | Must simulate (Navier-Stokes turbulence) |
| **Ontological Depth (OD)** | Emergent (thermodynamics) | Fundamental (path integrals) |

**Implementation:**
- CR: inverse of formula complexity normalized by domain coverage (how many datasets does this formula type touch?)
- GD: depth of the concept chain from formula to observable consequences (from concept index)
- UC: number of mathematical domains where formulas of this type appear (from operadic clusters)
- SED: symmetry order from S9 × number of conserved quantities
- CI: ratio of formula depth to evaluability (intractable formulas score high)
- OD: distance from "fundamental" nodes in the mathlib/Metamath proof graph

These 6 scores per formula create a meta-signature orthogonal to all our structural signatures. Two formulas can have different algebraic structures but the same meta-profile — that's a higher-order bridge.

### M3. Equivalence Class Detection

The goal isn't 27M individual signatures — it's discovering that 27M formulas collapse into N equivalence classes under transformation, where N << 27M.

**Implementation:**
1. S22 operadic skeleton gives the coarsest equivalence: same tree shape
2. Within each operadic class, S3 mod-p fingerprint gives the next partition: same arithmetic behavior
3. Within each mod-p class, S9 symmetry + S23 convexity give finer structure
4. The REMAINING variation after all partitions = the "leaf content" = the domain-specific dressing

**The leaf content IS the projection.** Two formulas in the same equivalence class with different leaf content are the same higher-dimensional object projected into different domains.

### M4. Minimal Generating Basis

Once we have equivalence classes + transformations between them, compress:
- Find the minimal set of "generating kernels" from which all other formulas can be derived by transformation
- This is analogous to finding generators of a group, or a basis for a vector space
- The generating kernels are the FUNDAMENTAL mathematical structures
- Everything else is a coordinate change

**This is the endgame.** If 27M formulas collapse to 500 generating kernels + a transformation algebra, we've found the compressed representation of mathematical knowledge. The cross-domain bridges ARE the transformations.

### M5. Formula-Space Coordinate System

Map every formula to a point in a continuous space defined by:

| Axis | Description |
|------|-------------|
| **Local ↔ Global** | Does the formula describe a neighborhood or an entire space? |
| **Deterministic ↔ Probabilistic** | Exact vs statistical |
| **Linear ↔ Nonlinear** | Superposition holds vs doesn't |
| **Static ↔ Generative** | Fixed constraint vs produces new structure |
| **Observable ↔ Hidden-variable** | All terms measurable vs latent variables |

These 5 axes + the 6 meta-scores = an 11-dimensional equation-space. The dissection signatures (S1-S33) are the coordinates within each equivalence class. The meta-axes describe which equivalence class the formula belongs to.

---

## Strategy Count: 33 + 5 meta-strategies

| Category | Strategies | Priority range |
|----------|-----------|---------------|
| Evaluation-based | S1, S2, S3, S5, S6, S7, S8, S12, S21 | 6-10 |
| Tree-based (no eval) | S9, S13, S14, S18, S22, S23, S30 | 7-10 |
| Algebraic | S10, S11, S15, S16, S19, S20, S29 | 6-9 |
| Information-theoretic | S24, S25, S26, S27, S28 | 6-7 |
| Architectural | Retrieval (tiered matching), TT compression, shadow contrastive | N/A |

*30 dissection strategies + retrieval architecture + shadow tensor contrastive framework.*
*Charon v5 planning — 2026-04-09*

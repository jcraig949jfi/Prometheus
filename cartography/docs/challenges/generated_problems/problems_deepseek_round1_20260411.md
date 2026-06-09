# DeepSeek Round 1 — 2026-04-11
# Generated from prompts_for_frontier_models_v2.md

Here are 20 computational problems designed to push the instrument into new dimensions of measurement.

---

### **1. Title:** Spectral Repulsion in Crystal Vibrational Modes
**What to measure:** Compute the nearest-neighbor eigenvalue spacing distribution for the dynamical matrix (phonon spectrum) of crystals. Fit to GOE, GUE, Poisson, or other universal random matrix ensembles. Measure the repulsion exponent `β` (0 for Poisson, 1 for GOE, 2 for GUE, 4 for GSE) as a function of crystal system (cubic, hexagonal, etc.) and space group symmetry.
**Data to use:** Materials Project (210,579 crystals). Use force constants where available (subset), or approximate via mass-spring models from atomic positions and space group symmetries.
**Expected constant:** A map: e.g., `β_cubic = 1.02 ± 0.05` (GOE), `β_hexagonal_with_inversion = 0.12 ± 0.10` (near-Poisson). A single summary: The fraction of crystals exhibiting `β > 0.5` (genuine repulsion).
**Why just beyond:** Requires building a *crystal symmetry-adapted random matrix generator* and a phonon spectrum calculator from structural data. Tests if the universal RMT laws (a Layer 2 structural constant in arithmetic) manifest in condensed matter physics.

### **2. Title:** Functorial Lift Detection via Twisted Enrichment
**What to measure:** For an elliptic curve E in LMFDB, compute its mod-p fingerprint. For each quadratic Dirichlet character χ of conductor up to 100, compute the twist E_χ. Measure the enrichment of E_χ's fingerprint *relative to the original E's fingerprint*, not the global average. Does twisting by χ act as a predictable linear operator on the fingerprint vector space?
**Data to use:** LMFDB elliptic curves (all with conductor < 500,000), generate twists computationally.
**Expected constant:** The operator norm (or dominant eigenvalue) of the "twist transformation matrix" T, where `F(E_χ) ≈ T_χ * F(E)`. For all χ, `|λ_max(T_χ)| ≈ 1.00 ± 0.01` if it's a pure isometry.
**Why just beyond:** Probes **Layer 3 (Transformational)**. Must model maps between families (twisting) and measure how they act on structural fingerprints. Success reveals the functorial structure of the Langlands correspondence at the fingerprint level.

### **3. Title:** Curvature Flow on Superconductor Composition Graphs
**What to measure:** Construct a graph where nodes are superconductors from the 3DSC database. Connect two nodes if their chemical compositions share >50% common elements (by count). Compute the Ollivier-Ricci curvature on this graph. Run curvature flow. Does it separate high-Tc materials into a distinct, tightly curved cluster?
**Data to use:** 3DSC Superconductors (12,448 materials with composition and Tc).
**Expected constant:** The curvature `κ*` of the fixed-point cluster for `Tc > 20 K`. Compare to curvature for `Tc < 5 K`. Expect: `κ*_high-Tc - κ*_low-Tc > 0.5`.
**Why just beyond:** Applies a proven arithmetic/topological structural tool (curvature flow) to a *physical* domain (material science). Tests if "structural clustering via curvature" is a cross-domain universal.

### **4. Title:** Moment Chain of Cosmic Microwave Background Anisotropies
**What to measure:** Treat the Planck CMB TT power spectrum `C_ℓ` as a probability distribution over multipole `ℓ`. Compute the normalized moment ratios `M4/M2^2`, `M6/M2^3`, `M8/M2^4`. Compare to the universal "Catalan chain" (1.5, 2.0, 3.0, 5.14, 14.66) observed in automorphic forms.
**Data to use:** Planck CMB TT spectrum (83 bins, ell=48-2499).
**Expected constant:** `M4/M2^2 = ~2.0` (if SU(2)-like) or `~3.0` (if USp(4)-like). The specific deviation: `|(M6/M2^3) - 5.14|`.
**Why just beyond:** Directly tests if a fundamental *mathematical* structural constant (the Catalan moment chain) governs a *physical* spectrum from the early universe.

### **5. Title:** Basis Set Completeness as a Modular Form
**What to measure:** For each basis set in the Basis Set Exchange, compute its "completeness vector": the convergence rate of energy for a suite of small atoms (H, He, Li) as a function of angular momentum. Treat this vector as a sequence. Perform mod-p fingerprinting and Berlekamp-Massey analysis. Is there a hidden recurrence or congruence structure classifying basis set families (cc-pVXZ, aug-cc-pVXZ, etc.)?
**Data to use:** Basis Set Exchange (776 basis sets). Run atomic Hartree-Fock or DFT single-point calculations (requires building a quantum chemistry backend).
**Expected constant:** The fraction of basis set families (e.g., all cc-pVXZ) whose completeness vectors share a mod-7 fingerprint: target >90%.
**Why just beyond:** Requires building a *quantum chemistry calculator* into the instrument. Attempts to find *algebraic structure in human-designed approximation schemes*.

### **6. Title:** Knot-Jones to 3-Manifold Invariant Lift
**What to measure:** For each knot in the knot database, take its Jones polynomial `J(K)(t)`. Evaluate at `t = exp(2πi/5)`. Use the resulting complex number as a "seed." For the hyperbolic 3-manifold M(K) from the knot complement, compute its Chern-Simons invariant `CS(M(K))`. Measure the coherence (complex correlation) between `J(K)(exp(2πi/5))` and `exp(2πi * CS(M(K)))`.
**Data to use:** Knot database (13K knots), and SnapPy (or a census) to compute Chern-Simons invariants of the complement.
**Expected constant:** Coherence magnitude `|ρ|`. If the Witten-Reshetikhin-Turaev invariant lifts the Jones polynomial, expect `|ρ| > 0.8`.
**Why just beyond:** Probes **Layer 3 (Transformational)**. Measures the consistency of a *lift* from a polynomial knot invariant to a quantum topological invariant of 3-manifolds. Requires computing Chern-Simons invariants at scale.

### **7. Title:** Earthquake Magnitude-Frequency as a Multi-Regime Power Law
**What to measure:** Fit the USGS earthquake magnitude-frequency distribution not to a single Gutenberg-Richter law, but to a *piecewise* power law with breakpoints. Use the instrument's 14-test falsification battery to rigorously validate that the breakpoints are statistically significant and not artifacts. Measure the scaling exponents `α_shallow` (mag < 5.0) and `α_deep` (mag > 7.0).
**Data to use:** USGS Earthquakes (global catalog, last 50 years).
**Expected constant:** The breakpoint magnitude `M_b` and the exponent difference `Δα = α_deep - α_shallow`. Expect `M_b ≈ 5.8 ± 0.3`, `Δα ≈ 0.2 ± 0.05`.
**Why just beyond:** Forces the instrument to perform *structural break detection* validated by its full falsification battery, moving beyond simple fitting to identifying *regime changes* in a physical system.

### **8. Title:** Atomic Spectral Line "Enrichment" by Electron Configuration
**What to measure:** Group atomic energy levels from NIST by their electron configuration (e.g., `1s2 2s1`, `1s2 2p1`). For each group, compute the distribution of level spacings. Measure the *enrichment*: how much more clustered are levels within the same configuration compared to a random mix of configurations? Use the same `~8x` detrended enrichment metric from number theory.
**Data to use:** NIST Atomic Spectra (42,981 levels across 99 elements).
**Expected constant:** Detrended enrichment factor `E_config`. If electron configuration is a fundamental structural organizer, expect `E_config ≈ 6x - 10x`, similar to algebraic families.
**Why just beyond:** Tests if the "enrichment" structural constant (a Layer 2 algebraic phenomenon) appears in *atomic physics* as a signature of a shared underlying Hamiltonian symmetry.

### **9. Title:** Phase Coherence in Logistic Map Bifurcation Cascades
**What to measure:** For the logistic map `x_{n+1} = r * x_n * (1 - x_n)`, at each `r` in the chaotic regime, compute a time series. Treat its Fourier transform phases. Compute the phase coherence metric (as done for Frobenius eigenvalues). Plot coherence vs. `r`. Does it spike at periodic windows? Is there a universal coherence value for fully developed chaos?
**Data to use:** Generated data: logistic map bifurcation cascade (r from 3.5 to 4.0, fine steps).
**Expected constant:** The average phase coherence `ρ` in the fully chaotic region (`r > 3.5699`, excluding periodic windows). Expect `ρ_chaos ≈ -0.19` (matching Maass forms?) or `≈ 0.20` (matching elliptic curves?).
**Why just beyond:** Tests if *phase coherence*, a deep constant from global L-functions, is a universal dynamical systems invariant for chaotic maps.

### **10. Title:** Hilbert Modular Form Congruence Propagation
**What to measure:** Take the Hilbert modular forms dataset (368K). For a fixed prime `p` and a fixed quadratic real field `K=Q(√d)`, compute mod-p fingerprints for all forms of parallel weight 2. Construct the congruence graph. Analyze its connected components. Does the *size* of the largest component follow a predictable law based on the class number `h_K` of the field?
**Data to use:** Hilbert modular forms (pending wire – use a substantial subset once available).
**Expected constant:** The scaling exponent `γ` in `LargestComponentSize ∝ (h_K)^γ`. Predict `γ ≈ -0.5` if class number inhibits congruence propagation.
**Why just beyond:** Requires handling *higher-dimensional* automorphic forms. Measures how *arithmetic of the base field* controls congruence structure (a new dimension: base field dependence).

### **11. Title:** Formal Proof Step Complexity vs. Statement Entropy
**What to measure:** For each theorem in Lean's mathlib, compute two things: 1) The length (in tokens) of its formal statement. 2) The length of its proof (number of tactic steps). Measure the relationship. Is it linear, polynomial, or exponential? Fit a law: `ProofSteps = A * (StatementLength)^B`. Measure the exponent `B`.
**Data to use:** mathlib (8.5K theorems and proofs).
**Expected constant:** The exponent `B`. For trivial syntactic manipulation, `B=1`. For deep mathematics, `B>1`. Expect `B ≈ 1.8 ± 0.2`.
**Why just beyond:** Requires building a *proof step parser and complexity measurer* for Lean. This quantifies the "cost of rigor" and probes the structure of the formal proof manifold.

### **12. Title:** Crystal Space Group as a Topological Curvature Classifier
**What to measure:** For each crystal in the Materials Project, compute its *topological descriptor* (e.g., from its Voronoi tessellation or persistent homology of atomic positions). Compute the mean Ollivier-Ricci curvature of the resulting graph. Group by crystallographic space group (230). Does the *sign* of the curvature (positive/negative) classify space groups into distinct categories (e.g., all cubic groups have `κ>0`, all monoclinic have `κ<0`)?
**Data to use:** Materials Project (210,579 crystals), compute topological graphs from CIF files.
**Expected constant:** The classification accuracy (eta-squared) of space group from curvature sign alone. Target `η² > 0.3`.
**Why just beyond:** Creates a bridge between *crystallography* (physics) and *topological graph curvature* (mathematics). Tests if curvature sign, which distinguishes arithmetic from topology, also distinguishes crystal systems.

### **13. Title:** Ramanujan Machine Integer Relation Stability Under p-adic Completion
**What to measure:** Take conjectured integer relations from the Ramanujan Machine (e.g., `π ≈ (a/b) * sqrt(c)`). Treat the relation as an equation. Compute its p-adic norm for primes p=2,3,5,...,97. Measure the *variance* of this p-adic error across primes. Is it near-zero (stable, suggesting a true global relation) or large (unstable, likely coincidental)?
**Data to use:** Ramanujan Machine integer relation library (73 files).
**Expected constant:** The threshold `τ`: if `Var_p(|error|_p) < τ`, the relation is "globally stable." Determine `τ` empirically from known true vs. false relations.
**Why just beyond:** Requires implementing *p-adic arithmetic for real numbers*. This is a novel validation tool for integer relation discoveries, probing their *adelic* consistency (Layer 3).

### **14. Title:** Maass Form Coefficient Correlations Across Spectral Gaps
**What to measure:** For Maass forms, you found spectral-coefficient repulsion (adjacent forms anti-correlate). Now, measure the *decay* of this anti-correlation as a function of *spectral gap* `Δλ = |λ_i - λ_j|`. Fit a law: `Corr(a_n(i), a_n(j)) ∝ -exp(-c * Δλ)`. Measure the decay constant `c`.
**Data to use:** Maass forms database (14,995 forms with coefficients).
**Expected constant:** The decay constant `c`. Expect `c ≈ 0.5` (rapid decay) if repulsion is strictly local in the spectrum.
**Why just beyond:** Quantifies the *range* of interaction in the spectral "gas" of Maass forms. A new dimension: spectral locality of arithmetic influence.

### **15. Title:** Superconductor Tc Prediction via Compositional Moment Vectors
**What to measure:** For each superconductor, encode its chemical composition not as a list, but as a *distribution* over the periodic table (e.g., weighted by stoichiometry). Compute the first 8 raw moments of this distribution (mean atomic number, variance, skewness, kurtosis, etc.). Use these moment vectors as features. Measure the Spearman correlation of each moment with Tc.
**Data to use:** 3DSC Superconductors (12,448 materials).
**Expected constant:** The correlation `ρ` between Tc and the *kurtosis* of the compositional distribution. Hypothesis: High-Tc materials may have platykurtic (broad) compositions. Target `|ρ| > 0.25`.
**Why just beyond:** Applies the "moment chain" structural paradigm to a *chemical* representation. Tests if physical properties are functions of the *statistical shape* of composition.

### **16. Title:** Functoriality of Lattice Theta Series Under Dualization
**What to measure:** For each lattice in the 39K lattice database, compute its theta series `Θ_Λ(q)` to O(q^100). Compute the theta series of its dual lattice `Θ_Λ*(q)`. Apply the Berlekamp-Massey algorithm to the sequence of coefficients of the *difference* `Θ_Λ(q) - Θ_Λ*(q)`. Does this difference sequence satisfy a linear recurrence of bounded order for all lattices in a given genus?
**Data to use:** Lattice database (39K theta series), compute duals via Gram matrix inversion.
**Expected constant:** The maximal recurrence order `k` for the difference series across all lattices of dimension 8. Expect `k ≤ 4` if duality acts as a finite-dimensional operator on the space of modular forms of that weight.
**Why just beyond:** Probes **Layer 3 (Transformational)**. Measures the *functorial complexity* of the duality operation by seeing if it maps lattices into a finite-dimensional subspace of modular forms.

### **17. Title:** Algorithmic "Gene" Conservation Across FLINT Functions
**What to measure:** Parse the FLINT call graph (73K edges). For each function, extract its *algorithmic fingerprint*: ratios of operation types (loops, conditionals, integer ops, memory accesses) from source code. Perform hierarchical clustering. Do functions that implement the same *mathematical algorithm* (e.g., GCD, FFT) across different modules cluster together with >95% purity?
**Data to use:** FLINT source code (9,393 C files, 6,474 functions).
**Expected constant:** The cluster purity `P` for known algorithm classes. Expect `P ≈ 0.98` if algorithmic structure is conserved independently of implementation context.
**Why just beyond:** Requires building a *simple code semantic feature extractor*. Tests the hypothesis that algorithms are "natural kinds" with conserved structural signatures in code space.

### **18. Title:** Seismic Event Clustering via Curvature Flow on Spacetime Graph
**What to measure:** Build a graph where nodes are earthquakes (USGS). Connect two events if they are close in *spacetime* (e.g., distance < 100km, time < 30 days). Compute Ollivier-Ricci curvature. Run curvature flow. Does the fixed-point cluster correspond to known tectonic plate boundaries or fault lines with >90% accuracy?
**Data to use:** USGS Earthquakes (global, with latitude, longitude, depth, time).
**Expected constant:** The Jaccard similarity `J` between the top 10% highest-curvature nodes and known fault line proximities. Target `J > 0.7`.
**Why just beyond:** Applies the instrument's core *structural clustering tool* (curvature flow) to a *geophysical spatiotemporal* domain. A strong cross-domain test.

### **19. Title:** Modularity of Crystal "Theta Series" from Diffraction Patterns
**What to measure:** For each crystal in the COD, simulate its X-ray diffraction pattern (as a set of (h,k,l) peaks with intensities). Construct a "theta series" analog: `Θ(q) = Σ_I * q^(d^2)`, where `d` is the d-spacing of the peak. Analyze this series for modular properties (mod-p fingerprints, recurrence). Does the space group determine the congruences of this series?
**Data to use:** COD Crystals (9,800 structures with cell parameters). Compute diffraction patterns via crystallographic software.
**Expected constant:** The fraction of crystals in a given space group (e.g., P1) whose simulated theta series has a Berlekamp-Massey recurrence order < 6. Expect >80% for highly symmetric groups.
**Why just beyond:** Requires building a *crystallographic diffraction simulator*. This attempts to find *arithmetic structure in physical diffraction data*, a bold cross-domain bridge.

### **20. Title:** The "Gamma Pseudometric" Distance Between Physical Laws
**What to measure:** Take the 286 CODATA fundamental constants. Treat each as the result of a "formula" involving others (e.g., `α = e^2/(4πε_0 ħ c)`). Use the Gamma pseudometric (which gave 0 triangle violations on formulas) to compute distances between these defining equations. Does the resulting metric space have a clear clustering (electromagnetic, quantum, thermodynamic) and near-zero triangle inequality violations?
**Data to use:** CODATA 2022 (286 constants and their defining relations).
**Expected constant:** The number of triangle inequality violations `V` per 1000 triples of equations. For a coherent system of laws, expect `V < 5`.
**Why just beyond:** Applies a *mathematical discovery* (the Gamma pseudometric) to the *edifice of physics itself*. Tests if the structure of physical law is "geodesic" in formula space.
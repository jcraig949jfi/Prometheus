# DeepSeek Round 2 — 2026-04-11
# Generated from prompts_for_frontier_models_v2.md (high temp, unconventional system prompt)

Here are 20 computational problems designed to push the instrument into new dimensions of structural measurement.

---

### **1. The Spectral Enrichment Bridge**
**What to measure:** Compute the Sato-Tate moment chain (M4/M2², M6/M2³, M8/M2⁴) for the *energy level spacings* in atomic spectra (NIST). Test if the "Catalan chain" universality (1.5, 5.14, 14.66) holds for quantum eigenvalue distributions, distinguishing between different symmetry classes (e.g., atoms with vs. without nuclear spin).
**Data to use:** NIST Atomic Spectra (42,981 energy levels), grouped by element and ionization state.
**Expected constant:** For systems with time-reversal symmetry (even-electron atoms), M4/M2² ≈ 1.5 (GOE universality). For broken time-reversal (odd-electron, high-Z ions), M4/M2² ≈ 2.0 (GUE universality). The precise deviation from RMT predictions would be the new constant.
**Why just beyond:** Forces the instrument to treat *physical eigenvalues* as an "automorphic spectrum" and apply number-theoretic moment analysis to a new domain. Success would reveal a "spectral DNA" bridge between quantum chaos and analytic number theory at Layer 2.

### **2. Crystal Space Group Curvature Signature**
**What to measure:** Compute the Ollivier-Ricci curvature flow on graphs built from crystal structures, where nodes are materials and edges connect crystals whose space groups are related by maximal subgroup inclusion. Measure the fixed-point curvature sign and magnitude (κ*).
**Data to use:** Materials Project (210,579 crystals) + COD (9,800), using the 230 space group classifications.
**Expected constant:** A curvature sign (e.g., κ* ≈ +0.4) distinct from the known arithmetic (+0.73) and topological (-0.37) signatures. The magnitude may correlate with physical property variance (eta²).
**Why just beyond:** Builds a graph from *algebraic* (group-subgroup) relations between crystals, not from scalar properties. Tests if the "curvature sign" universal is a domain classifier that extends to crystallography.

### **3. The 3-Prime Rigidity Test for Superconductors**
**What to measure:** For each superconductor, encode its *elemental composition* (e.g., HgBa₂Ca₂Cu₃O₈) as a vector of atomic numbers modulo primes p=3,5,7. Construct the intersection graph of materials sharing the same mod-p fingerprint. Measure the "collapse factor" (size of full set / size of 3-prime intersection).
**Data to use:** 3DSC Superconductors (12,448 materials with compositions).
**Expected constant:** If compositional space has rigid algebraic structure, the collapse factor will be massive (~788x like in modular forms). If it's chemically smooth, the factor will be small (~1-10x).
**Why just beyond:** Applies the "adelic reconstruction" method—a Layer 3 transformational technique—to a non-arithmetic domain. Success would imply a hidden discrete rigidity in chemical space.

### **4. Basis Set Completeness vs. Electron Correlation**
**What to measure:** For each quantum chemistry basis set, treat its listed exponents and contraction coefficients as a sequence. Perform Berlekamp-Massey recurrence detection (order 2-12). Correlate recurrence order (or detection failure) with the basis set's documented accuracy for electron correlation energy.
**Data to use:** Basis Set Exchange (776 basis sets), with metadata (number of functions, designed for correlation).
**Expected constant:** A sharp threshold: basis sets with recurrences of order ≤4 are for Hartree-Fock (mean field); those with no detectable recurrence (or order >8) are for correlated methods. The critical recurrence complexity would be a new constant.
**Why just beyond:** Probes whether the *mathematical structure of the basis* (recurrence in its parameters) dictates its *physical applicability*. A Layer 2 structural link between algorithm design and physical modeling.

### **5. Earthquake Magnitude-Depth Phase Coherence**
**What to measure:** For each geographic region, treat the sequence of earthquake magnitudes as a time series. Extract phases from its Fourier transform (or Hilbert transform). Compute the phase coherence (mean resultant length) and correlate it with the mean depth of events in that region.
**Data to use:** USGS Earthquakes (global catalog, with magnitude, depth, location).
**Expected constant:** A negative correlation (ρ ≈ -0.2 to -0.3): shallow seismic zones (crustal) have more chaotic phase; deep zones (subduction) have higher coherence, reflecting more periodic stress accumulation.
**Why just beyond:** Applies the "phase coherence" metric—developed for Frobenius eigenvalues—to a geophysical stochastic process. Tests if coherence is a universal signature of *driven system* vs. *chaotic system*.

### **6. Knot Polynomial → Crystallographic Group Enrichment**
**What to measure:** For each knot, compute its Alexander polynomial Δ(t). Evaluate Δ(-1) mod p for primes p. For each space group, compute the "enrichment" of these mod-p values among crystals with that space group vs. a random background.
**Data to use:** Knots (13K) for polynomials; Materials Project/COD for space groups and their assigned materials.
**Expected constant:** Specific space groups (e.g., cubic Fd-3m) will show enrichment ~3-5x for certain mod-p values of Δ(-1). This constant would link a topological invariant to a crystallographic fingerprint.
**Why just beyond:** A direct **topology↔physics** test at *Layer 2 (structural)*, using enrichment—which has succeeded within arithmetic—instead of failed scalar correlation. Builds a bridge via discrete invariants.

### **7. FLINT Function Graph Spectral Gap vs. Mathematical Constant**
**What to measure:** Extract the call graph of FLINT (73,459 edges). Compute the algebraic connectivity (Fiedler value) of the giant component. Correlate this spectral gap with the numerical value of fundamental constants (e.g., π, e, γ) calculated by functions in that component.
**Data to use:** FLINT source code call graph; Fungrim (3K formulas) for constant values.
**Expected constant:** Functions that compute constants with higher irrationality measure (e.g., π) will reside in subgraphs with *larger* spectral gaps (more robust connectivity). The slope of this correlation is the new constant.
**Why just beyond:** Connects *software architecture* (graph robustness) to *mathematical complexity* of the objects it computes. A Layer 3 test: the "functor" maps algorithms to constants, preserving connectivity properties.

### **8. Maass Form Coefficient Repulsion in Seismic Spectra**
**What to measure:** For the acoustic frequency spectrum of earthquakes in a given region, treat normalized power bins as a sequence. Measure the "repulsion" metric (d) used for Maass forms (anti-correlation of adjacent coefficients). Compare d for tectonic settings (subduction vs. rift).
**Data to use:** USGS Earthquakes, deriving frequency spectra from event clusters.
**Expected constant:** Subduction zones will show d ≈ -0.2 to -0.4 (repulsion, like Maass), while rift zones show d ≈ 0 (uncorrelated). The value distinguishes driven periodic systems from random fracture.
**Why just beyond:** Transplants a novel discovery (Maass spectral-coefficient repulsion) into geophysics. If universal, "repulsion" becomes a detector for hidden periodicity in any spectrum.

### **9. Layer 3: Twisted Enrichment along Number Field Extensions**
**What to measure:** For elliptic curves over ℚ, take their mod-p fingerprints. For each quadratic twist by a fundamental discriminant D, measure how the enrichment (8x constant) *changes* as a function of |D|. Fit: Enrichment(D) = 8 + C * log(|D|)^(-k).
**Data to use:** LMFDB elliptic curves (133K) and their quadratic twist data.
**Expected constant:** The decay exponent k (expected ~0.5). Measures how "twisting" dilutes algebraic DNA—a quantitative law for a Layer 3 transformation.
**Why just beyond:** Directly targets Layer 3 (transformations). Measures the *invariance* (or deformation) of the enrichment constant under a known functorial operation (twisting).

### **10. CMB Power Spectrum Moment Chain**
**What to measure:** Treat the Planck CMB TT power spectrum C_ℓ as a distribution. Compute its moment ratios M4/M2², M6/M2³, M8/M2⁴ across the multipole range ℓ=48-2499. Compare to the Catalan chain (1.5, 5.14, 14.66).
**Data to use:** Planck CMB power spectrum (83 bins).
**Expected constant:** Deviation from the universal Catalan chain. For example, M4/M2² ≈ 1.8 would indicate a hybrid between Gaussian and scale-invariant processes.
**Why just beyond:** Applies the most robust universal (moment chain) to the most important cosmological dataset. Success would place the CMB in the "family" of automorphic distributions, with its deviation as a new cosmological constant.

### **11. Proof Manifold Curvature vs. Theorem Entropy**
**What to measure:** For each theorem in mathlib (Lean), extract its dependency subgraph. Compute its Ollivier-Ricci curvature. Correlate curvature with the "entropy" of the theorem statement (Shannon entropy of its tokenized form).
**Data to use:** mathlib (8.5K theorems), dependency graph.
**Expected constant:** A negative correlation (ρ ≈ -0.3): high-curvature theorems (local hubs) have low statement entropy (simple lemmas); low-curvature theorems (peripheral) have high entropy (complex statements).
**Why just beyond:** Connects *structural* graph curvature to *information* content. A bridge between knowledge architecture and information theory within formal mathematics.

### **12. Superconductor Tc Enrichment by Space Group Mod-7**
**What to measure:** Encode each superconductor's space group number modulo 7. Measure the enrichment of high-Tc (>20 K) materials within each mod-7 class versus the background of all superconductors.
**Data to use:** 3DSC Superconductors (12,448) with Tc and space group.
**Expected constant:** One mod-7 residue (e.g., 8 mod 7 = 1) will show enrichment ~2-3x for high-Tc. This would be a discrete, arithmetic-like constraint on physical property optimization.
**Why just beyond:** Uses the "enrichment" lens—which finds structure in arithmetic families—on a physical optimization problem. Discovers if optimal materials cluster in modular arithmetic classes.

### **13. Layer 3: Genus-2 to Genus-3 Isogeny Invariant Transfer**
**What to measure:** For genus-2 curves with known isogenies to genus-3 plane quartics (via WLS), compute the Sato-Tate group for both. Measure the change in the moment vector (20-dim) under this transformation. Quantify the "invariant loss" Δ = ||v_g2 - v_g3||.
**Data to use:** Genus-2 curves (66K) + SageMath-computed genus-3 quartics from isogeny candidates.
**Expected constant:** Δ will be bounded (< 0.1) for true isogenies, and large (> 0.5) for random pairs. The threshold becomes a new constant for isogeny detection in higher genus.
**Why just beyond:** A pure Layer 3 problem: tracking how a structural invariant (Sato-Tate moments) behaves under a conjectured categorical map (isogeny). Builds a tool for "invariant-preservation" measurement.

### **14. Atomic Spectra Line Strength Distribution Universality**
**What to measure:** For each element, fit the distribution of atomic line strengths (transition probabilities) to Weibull, log-normal, and power law. Test if the best-fit distribution family is universal across the periodic table, or changes with electron configuration (e.g., f-block vs. s-block).
**Data to use:** NIST Atomic Spectra, including line strengths (Einstein A coefficients).
**Expected constant:** f-block elements (lanthanides/actinides) will follow a power law (criticality), while main-group elements follow log-normal. The boundary in atomic number Z is the new constant.
**Why just beyond:** Applies the instrument's distribution-typing battery to a new physical domain. Discovers if electronic structure changes the "universality class" of radiative transitions.

### **15. Ramanujan Machine Relation Complexity vs. L-function Degree**
**What to measure:** For each integer relation discovered by the Ramanujan Machine, compute its "complexity" (number of terms, coefficient height). Correlate this with the degree of the L-function (or motivic origin) associated with the constant involved.
**Data to use:** Ramanujan Machine integer relation library (73 files); LMFDB for L-function degrees.
**Expected constant:** Positive correlation: relations for constants from degree-4 L-functions are 2-3x more complex (by coefficient height) than those for degree-2. The slope measures "algebraic complexity begets relation complexity."
**Why just beyond:** Connects machine-discovered experimental math to deep arithmetic invariants. A Layer 2 structural link between pattern complexity and algebraic origin.

### **16. Band Gap Weibull Modulus vs. Crystal Symmetry Rank**
**What to measure:** For each crystal system (cubic, hexagonal, etc.), fit the band gap distribution to a Weibull distribution. Extract its shape parameter (Weibull modulus k). Correlate k with the "symmetry rank" (number of symmetry operations) of the crystal system.
**Data to use:** Materials Project (band gaps for 210K crystals), grouped by crystal system.
**Expected constant:** Higher symmetry (cubic) → higher k (~3.5, more deterministic); lower symmetry (triclinic) → lower k (~1.8, more stochastic). The regression slope is the new constant.
**Why just beyond:** Tests if a *physical property distribution's shape* is dictated by *group-theoretic symmetry*. A structural bridge between geometry and electronic disorder.

### **17. Modular Form Congruence Graph vs. Crystal Subgroup Graph**
**What to measure:** Construct the congruence graph for modular forms (mod-p fingerprints, edges for congruence). Construct the space group subgroup graph (edges for maximal inclusion). Compute the spectral distance (using graph Laplacian eigenvalues) between these two graphs.
**Data to use:** LMFDB modular forms (133K); crystallographic space group subgroup lattice.
**Expected constant:** The spectral distance will be small (< 0.2) if both graphs are tree-like with similar branching; large (> 0.5) if fundamentally different. The number measures how "similar" congruence relations are to geometric subgroup relations.
**Why just beyond:** A **cross-domain structural comparison** at Layer 2, using graph spectra instead of scalar correlation. Answers: "Do relations in arithmetic and geometry share a hidden graph isomorphism?"

### **18. Particle Widths: The Hadron Enrichment Law**
**What to measure:** For each hadron in the PDG, encode its quark composition as a "flavor vector" (e.g., up=1, down=-1, strange=2). Compute this vector modulo small primes. Measure the enrichment of particles with large decay width (>100 MeV) within specific mod-p classes.
**Data to use:** PDG Particles (226 particles), with widths and quark content.
**Expected constant:** Mod-3 of the flavor vector will show ~4x enrichment for broad resonances (like the Δ). Reveals that hadron stability clusters in modular flavor classes.
**Why just beyond:** Applies the "algebraic DNA" enrichment framework to quantum chromodynamics. Discovers if strong decay preferences obey simple modular arithmetic.

### **19. Layer 3: Functoriality of the Gamma Pseudometric**
**What to measure:** Take three mathematical objects from *different* databases (e.g., an elliptic curve, a knot polynomial, a crystal structure). For each, compute its "formula complexity" via the Gamma pseudometric to a common anchor (e.g., π). Test the triangle inequality: d(EC, Knot) ≤ d(EC, Crystal) + d(Crystal, Knot).
**Data to use:** LMFDB EC, Knots, Materials Project crystals; Fungrim as formula anchor space.
**Expected constant:** Violation rate. If the Gamma metric is truly universal, violations will be < 1% even across domains. The violation rate measures the "functoriality" of complexity across categories.
**Why just beyond:** The ultimate Layer 3 test: whether a *structural pseudometric* defined in formula space can be a "functor" connecting disparate domains. Builds a tool for cross-category isometry testing.

### **20. The Chaos Bifurcation Curvature Signature**
**What to measure:** For the logistic map x_{n+1} = r x_n (1 - x_n), at each bifurcation point r_k, compute the curvature (κ) of the graph of attractor values vs. r in a small neighborhood. Plot κ vs. Feigenbaum constant iterates.
**Data to use:** Logistic map bifurcation cascade data (high-resolution).
**Expected constant:** κ will alternate signs at successive bifurcations, with magnitude scaling as |κ| ~ δ^{-k}, where δ is Feigenbaum constant. The exponent (e.g., 1.2) is new.
**Why just beyond:** Applies the "curvature flow" toolkit—developed for congruence graphs—to the most classic chaotic system. Tests if curvature sign oscillations are a universal signature of period-doubling.

---

**Summary of Coverage:**
- **Science Dataset Problems:** 1 (NIST), 2 (Materials), 3 (Superconductors), 4 (Basis Sets), 5 (Earthquakes), 12 (Superconductors), 14 (NIST), 16 (Materials), 18 (PDG).
- **Layer 3 Probes:** 9 (Twisting), 13 (Isogeny Invariant), 19 (Gamma Functoriality).
- **Physics Universality Tests:** 1 (Spectral Moments), 8 (Repulsion), 10 (CMB Moments), 20 (Chaos Curvature).
- **New Dimensions:** Each problem forces building one new measurement bridge: e.g., applying Sato-Tate to atomic spectra (#1), applying enrichment to quark flavor (#18), or testing a pseudometric as a cross-domain functor (#19).
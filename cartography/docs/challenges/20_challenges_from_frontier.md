
**1. Acoustic Peak GUE Spacing**
* **What to measure:** Compute the normalized nearest-neighbor spacing distribution of the local maxima (acoustic peaks) and minima in the CMB power spectrum, and calculate its Kullback-Leibler (KL) divergence from the Gaussian Unitary Ensemble (GUE) distribution of random matrix theory.
* **Data to use:** Planck CMB TT power spectrum (83 bins, $\ell=48-2499$).
* **Expected constant:** A KL divergence scalar (e.g., $D_{KL} \approx 0.14$).
* **Why just beyond:** Forces the instrument to build a Random Matrix Theory (RMT) unfold/spacing analysis tool. If the CMB acoustic peaks exhibit GUE spacing rather than Poisson spacing, it suggests the early universe plasma oscillations were governed by non-integrable (chaotic) quantum Hamiltonian dynamics, linking cosmological observables to the same spectral statistics seen in L-function zeros.

**2. Decay Network Spectral Dimension**
* **What to measure:** Construct a directed graph where nodes are particles and edges are permitted decay channels weighted by branching ratios. Compute the spectral dimension of this graph by measuring the return probability decay rate of a random walk over $t$ steps.
* **Data to use:** PDG (226 particles with masses/widths/decay modes).
* **Expected constant:** The asymptotic spectral dimension $d_s$ (e.g., $d_s = 1.83$).
* **Why just beyond:** Your current graph tools (Ricci curvature, clique power laws) analyze static local geometry. Spectral dimension measures the *dynamical* geometry of a network. This tests if the Standard Model decay pathways form a manifold-like structure or a fractal hierarchy.

**3. Crystal Voronoi Clustering Threshold**
* **What to measure:** Generate 3D Voronoi tessellations for the atomic coordinates in the unit cells. Compute the average local clustering coefficient of the resulting adjacency graph (where touching Voronoi polyhedra constitute an edge).
* **Data to use:** 520K crystal structures (COD).
* **Expected constant:** Average global clustering coefficient $C$ (e.g., $C = 0.412$).
* **Why just beyond:** Forces the integration of 3D computational geometry (Delaunay/Voronoi duals) into your pipeline. This moves beyond 1D/2D data, creating a baseline constant for geometric packing efficiency in naturally occurring physical structures.

**4. Dimensional Basis Nullity**
* **What to measure:** Construct the $M \times N$ dimensional matrix for all physical constants (rows = constants, columns = base SI units: mass, length, time, etc., entries = unit exponents). Compute the rank of this matrix and subtract it from $M$ to find the nullity, representing the number of dimensionless parameters (via Buckingham Pi theorem).
* **Data to use:** CODATA (286 physical constants).
* **Expected constant:** The exact nullity integer representing the fundamental dimensionless degrees of freedom in the dataset (e.g., $k = 277$).
* **Why just beyond:** You tested mod-p fingerprinting on CODATA and it failed (tracking measurement precision). This forces a structural algebraic approach to physics data, building a tool to parse and manipulate dimensional units as algebraic vectors.


**5. Proof Dependency Fractal Dimension**
* **What to measure:** Treat the theorem dependency graph as a topological space. Implement a box-counting algorithm on the graph's hierarchical embeddings to measure how the number of required foundational lemmas scales with the depth of the proof tree.
* **Data to use:** Lean mathlib (190K theorem declarations).
* **Expected constant:** The box-counting fractal dimension $D_B$ of human formal logic (e.g., $D_B = 2.45$).
* **Why just beyond:** Forces the creation of fractal dimension estimators for abstract directed acyclic graphs (DAGs). This explores whether formal mathematical truth grows smoothly (integer dimension) or via a scale-free fractal process.

**6. Algorithmic Path Entropy**
* **What to measure:** Treat the C function call graph as a Markov chain by assigning uniform transition probabilities to out-edges. Calculate the topological entropy of this dynamical system, measuring the exponential growth rate of valid execution paths of length $N$.
* **Data to use:** FLINT source (parsed 9,393 files, 73K edges).
* **Expected constant:** The topological entropy rate $h$ (e.g., $h = 1.18$ bits/step).
* **Why just beyond:** You've built the graph; now you must simulate execution dynamics. This measures the "determinism" or "spaghetti-ness" of a mathematical library, establishing a constant for how computational algebra software flows.

**7. Substitution Graph Chromatic Number**
* **What to measure:** Parse the abstract syntax trees (ASTs) of mathematical formulas. Build a graph where edges connect formulas that can be transformed into one another via a single variable/function substitution. Compute the chromatic number $\chi$ of this structural graph.
* **Data to use:** Fungrim (3K formulas, 60 modules).
* **Expected constant:** The chromatic number $\chi$ (e.g., $\chi = 14$).
* **Why just beyond:** Forces the parser to evaluate structural equivalence (graph isomorphism on ASTs) rather than numerical values, mapping the combinatorial topography of human mathematical notation.

**8. Theorem Curvature Bottlenecks**
* **What to measure:** Apply your existing Ollivier-Ricci curvature flow tool to the undirected Lean theorem dependency graph. Identify the percentage of edges that converge to highly negative curvature (bridges/bottlenecks) versus positive curvature (cliques).
* **Data to use:** Lean mathlib (190K theorem declarations).
* **Expected constant:** The percentage of structurally negative curvature "bridge lemmas" (e.g., $P_{bridge} = 4.2\%$).
* **Why just beyond:** Re-uses your curvature flow tool on a completely alien domain (logic instead of congruences). Success would quantify exactly how much of modern mathematics relies on a tiny subset of vulnerable, critical logical bridges.

### Number Theory, Modular Forms & Sequences

**9. Hecke Eigenvalue Lyapunov Exponent**
* **What to measure:** Treat the sequence of normalized Hecke eigenvalues $a_p / p^{(k-1)/2}$ for sequential primes $p$ as a discrete dynamical system. Calculate the maximal Lyapunov exponent to determine the sequence's sensitivity to initial conditions (chaotic drift).
* **Data to use:** LMFDB MF (133K modular forms).
* **Expected constant:** The average Lyapunov exponent $\lambda$ (e.g., $\lambda \approx 0$).
* **Why just beyond:** You've looked at traces and frequencies, but a Lyapunov exponent forces the instrument to analyze modular forms as time-series dynamical systems. A non-zero exponent would imply hidden chaotic structure in Fourier coefficients.

**10. Automata Compression Ratio**
* **What to measure:** Convert mod-2 integer sequences into binary strings. Synthesize the minimal Deterministic Finite Automaton (DFA) that generates each string. Calculate the average ratio of states in the minimal DFA to the length of the sequence.
* **Data to use:** OEIS (394K sequences).
* **Expected constant:** Automata compression scalar $C_{DFA}$ (e.g., $C_{DFA} = 0.12$).
* **Why just beyond:** You have Berlekamp-Massey for linear recurrences. DFA synthesis captures *non-linear* structural regularities. This builds a formal language theory tool to measure algorithmic complexity directly.

**11. L-Function Zero GUE Deviation**
* **What to measure:** Extract the normalized spacings between the first 50 non-trivial zeros of L-functions for curves. Calculate the Kolmogorov-Smirnov (KS) distance between this empirical spacing distribution and the theoretical RMT GUE distribution.
* **Data to use:** Genus-2 (66K curves) and Genus-3 (100 curves via SageMath).
* **Expected constant:** The asymptotic KS deviation $\Delta_{KS}$ (e.g., $\Delta_{KS} = 0.04$).
* **Why just beyond:** Bridges your genus-2/genus-3 datasets with the Riemann Hypothesis generalization. It requires building a high-precision zero-extraction and spacing normalizer tool.

**12. Equidistribution Convergence Rate**
* **What to measure:** Measure the sequence of traces of Frobenius as $p$ grows. Fit the convergence rate of the empirical trace histogram to the theoretical Sato-Tate probability density function $O(p^{-\beta})$. Extract the scaling exponent $\beta$.
* **Data to use:** Genus-2 curves (66K).
* **Expected constant:** The convergence exponent $\beta$ (e.g., $\beta = 0.5$).
* **Why just beyond:** You've classified Sato-Tate groups (98.3% accuracy). This shifts focus from *classification* to *kinematics*—how fast does the arithmetic curve "fill" its random matrix space?

**13. Continued Fraction Khinchin Variance**
* **What to measure:** Parse OEIS sequences that represent rational approximations or digits of reals. Convert them to continued fractions and calculate the geometric mean of the first 100 coefficients. Measure the mean squared error against Khinchin's constant ($K \approx 2.685452$).
* **Data to use:** OEIS (filtered for real numbers/rationals).
* **Expected constant:** The global Khinchin MSE (e.g., $MSE = 0.88$).
* **Why just beyond:** Tests if human-curated real numbers obey the same ergodic theorems as almost all real numbers, forcing the instrument to parse and compute with infinite continued fractions.

**14. Cohen-Lenstra Deviation Variance**
* **What to measure:** Compute the class groups of the number fields. Compare the empirical distribution of the $p$-parts of these class groups against the theoretical Cohen-Lenstra heuristic probabilities. Output the $L_2$ norm of the difference vector.
* **Data to use:** Number fields (9K).
* **Expected constant:** The global heuristic deviation norm $E_{CL}$ (e.g., $E_{CL} = 0.015$).
* **Why just beyond:** Forces the pipeline to manipulate ideal class groups and execute probabilistic group theory measurements, bridging algebraic number theory with statistical distributions.

### Topology, Geometry & Cross-Domain Metrics

**15. Betti Number Density**
* **What to measure:** Treat the spatial coordinates of crystal atoms as a point cloud. Construct the Vietoris-Rips complex at a filtration radius equal to the average atomic bond length. Compute the first Betti number $\beta_1$ (number of 1-dimensional holes/tunnels) divided by the number of atoms.
* **Data to use:** 520K crystal structures (COD).
* **Expected constant:** The topological density ratio $\rho_\beta$ (e.g., $\rho_\beta = 1.34$).
* **Why just beyond:** Forces the introduction of Topological Data Analysis (TDA) and persistent homology algorithms into the instrument. This is a massive new mathematical dimension for the pipeline.

**16. Alexander-Salem Correlation**
* **What to measure:** Extract the roots of the Alexander polynomial for each knot. Measure the percentage of these roots that lie exactly on the unit circle in the complex plane (Salem numbers/roots of unity).
* **Data to use:** Knots (13K with Jones+Alexander).
* **Expected constant:** The unit-circle root percentage $P_{Salem}$ (e.g., $P_{Salem} = 42.6\%$).
* **Why just beyond:** Knot-NF intersection failed due to small-square artifacts. This problem approaches knots analytically via complex root geometry, forcing the instrument to map polynomial invariants to dynamical systems theory (Salem numbers).

**17. Hyperbolic Volume Scaling Law**
* **What to measure:** For knots with known hyperbolic volumes, perform a log-log regression of the hyperbolic volume against the minimum crossing number. Extract the power-law scaling exponent.
* **Data to use:** Knots (13K).
* **Expected constant:** The volume scaling exponent $\alpha_{vol}$ (e.g., $\alpha_{vol} = 1.15$).
* **Why just beyond:** Connects purely combinatorial data (crossing number) to continuous geometric data (hyperbolic 3-manifold volume), requiring the instrument to construct regression pipelines over topological invariants.

**18. Fourier Decay of Sphere Packings**
* **What to measure:** Convert the theta series of lattices into their continuous Fourier transforms. Measure the exponential decay rate $\gamma$ of the high-frequency Fourier spectrum, which corresponds to the smoothness of the underlying sphere packing density.
* **Data to use:** Lattices (39K with theta series).
* **Expected constant:** The average Fourier decay rate $\gamma$ (e.g., $\gamma = 3.14$).
* **Why just beyond:** You've mapped mod-p enrichments and kissing numbers (96.6% accuracy). This forces the tool into harmonic analysis on lattices, measuring the analytic decay rather than discrete coefficients.

**19. Formal-Algorithmic Mutual Information**
* **What to measure:** Bin the degree distributions of the Lean mathlib dependency graph and the FLINT C call graph. Calculate the Shannon Mutual Information (in bits) between these two probability distributions.
* **Data to use:** Lean mathlib (190K theorems) and FLINT source (9,393 C files).
* **Expected constant:** The structural mutual information $I(X;Y)$ in bits (e.g., $I = 0.45$ bits).
* **Why just beyond:** Directly compares the architecture of human formal proofs against the architecture of human computational code. Forces the instrument to compute information-theoretic metrics across entirely disconnected semantic domains.

**20. Evolutionary Translation Viability Limit**
* **What to measure:** Use your evolutionary computation tool (MAP-Elites/NSGA-II) to evolve a set of matrix transformation weights designed to map a 20-dim Sato-Tate moment vector into a 20-dim L-function trace vector. Measure the maximum achievable fitness (correlation coefficient) after $10^4$ generations.
* **Data to use:** Genus-2 (66K curves).
* **Expected constant:** The maximum cross-domain evolutionary fitness limit $F_{max}$ (e.g., $F_{max} = 0.31$).
* **Why just beyond:** You know simple EC-OEIS translations fail (all zero). This uses your established evolutionary reasoning tool to rigorously prove the upper bound of linear/non-linear translatability within the *same* mathematical object (genus-2 curves), establishing an empirical "speed of light" for cross-domain data transport.


This is an excellent specification. The key is to force the instrument into **new territories** (proof graphs, 3D point clouds, continuous spectra) where the existing 30+ constants (enrichment, interference, gamma pseudometric) have no natural definition.

Here are 20 problems that meet all criteria, with explicit avoidance of the 21 dead ends.

### Cluster 1: Physics & Continuous Data (Forcing a New Type of Input)

**1. Acoustic Oscillation Mod-p Fingerprinting**
- **What to measure**: The Planck CMB TT power spectrum is a discrete sequence of 83 bins. Treat $C_\ell$ as an integer sequence by multiplying by a large constant and rounding. Compute the mod-3, mod-5, and mod-7 fingerprints. Measure the **enrichment slope** of this sequence (how much more structured is the mod-p fingerprint compared to random noise of similar variance?). Compare this slope against the known L-function enrichment constant of ~8x.
- **Data to use**: Planck CMB TT power spectrum (83 bins, $\ell=48$–$2499$).
- **Expected constant**: **Enrichment $\mu$ = 0.12** (i.e., cosmic variance destroys the algebraic 8x enrichment; the universe is "flat" in mod-p space compared to arithmetic).
- **Why just beyond**: Current enrichment detection assumes discrete, multiplicative generation (Hecke operators). Applying it to a continuous inflationary perturbation power spectrum forces the instrument to build a **Continuous-to-Discrete Fingerprint Stabilizer** (handling shot noise vs. structural noise).

**2. PDG Decay Topology Curvature Flow**
- **What to measure**: Build a directed graph where nodes are the 226 PDG particles, and edges represent significant decay modes ($\Gamma_{i \to j} > 1\%$). Apply the Ollivier-Ricci curvature flow algorithm to this weighted digraph. Measure the **fixed point curvature $\kappa^*$** and the **iteration of phase transition** (separation of stable hadrons from resonances).
- **Data to use**: PDG particle listings (226 particles with masses/widths/decay modes).
- **Expected constant**: **$\kappa^* = -0.61$** (hyperbolic fragmentation geometry) vs. the spherical $\kappa^*=0.73$ observed in mod-2 Hecke graphs.
- **Why just beyond**: Current curvature flow tools are tuned for undirected, unweighted congruence graphs. This forces the instrument to build a **Weighted Edge Bundle Curvature Extractor** capable of handling branching ratios as edge probabilities.

**3. Crystal Phonon Recurrence Detection**
- **What to measure**: For the 520K crystal structures (Crystallography Open Database), compute the diffraction fingerprint (a 1D vector of the top 50 structure factors). Treat this vector as a sequence. Run Berlekamp-Massey to find the **minimal recurrence order** required to generate the structure factor profile. Measure the **Mean Recurrence Order** across all 520K structures.
- **Data to use**: 520K CIF files (atomic coordinates $\to$ calculated structure factors).
- **Expected constant**: **Mean BM Order = 3.14** (dominated by the 3 Bravais lattice centering vectors and 14 Bravais lattice constraints).
- **Why just beyond**: BM recurrence is currently applied only to integer sequences (OEIS, L-functions). Applying it to 3D real-space geometry requires building a **3D $\to$ 1D Projective Recurrence Encoder** that is invariant to unit cell choice.

**4. CODATA Unit Graph Spectral Dimension**
- **What to measure**: Avoid the dead end of mod-p digit analysis. Instead, build a graph of the 286 CODATA constants based on **dimensional analysis edges** (two constants are connected if they share a base SI unit or if there is a known high-precision formula connecting them). Measure the **local spectral dimension** $d_s$ of this network.
- **Data to use**: CODATA 2022 list + NIST fundamental physical constant relationships.
- **Expected constant**: **$d_s = 1.58$** (sub-diffusive, lower than the OEIS global dimension of 10.8, indicating a tree-like dependency of definitions rather than a dense mesh of discovery).
- **Why just beyond**: The instrument currently measures spectral dimension on pre-defined mathematical graphs (LMFDB, congruence). This requires building a **Physical Dependency Graph Constructor** from unstructured text definitions.

### Cluster 2: Formal Mathematics & Code (Forcing Graph Semantics)

**5. Lean mathlib Theorem Curvature Bottleneck**
- **What to measure**: Parse the Lean 4 `mathlib4` repository (not just declarations, but tactic proofs). Build a call graph where nodes are theorem statements and edges are "uses in proof." Apply Ricci curvature flow to identify **logical bottlenecks** (theorems with extreme negative curvature that are absolutely essential bridges). Measure the **Negative Curvature Ratio** (number of edges with $\kappa < -0.9$ / total edges).
- **Data to use**: Lean mathlib4 source (190K theorem declarations + tactic states).
- **Expected constant**: **Bottleneck Density = 0.038%** (only 1 in ~2600 theorems is a critical, un-avoidable hub like `eq.mp` or `Classical.choice`).
- **Why just beyond**: Current graph extraction works on C function calls (syntax). This forces the instrument to build a **Dependent Type Theory Dependency Resolver** to differentiate between a syntactic mention and a semantic proof relevance.

**6. FLINT Algorithmic Permeability Gradient**
- **What to measure**: The instrument measured global FLINT permeability (0.5975). Now, segment the 9,393 C files by submodule (`fmpz`, `fmpq`, `fq`, `nmod`, `arb`, `acb`). Measure the **Permeability $\Phi$** for each module independently. Does permeability correlate with **Reynolds number** (stability) or **Complexity**?
- **Data to use**: FLINT source call graph (73K edges, 9,393 files).
- **Expected constant**: **`acb` Permeability = 0.21** (highly opaque ball arithmetic) vs. **`fmpz` Permeability = 0.88** (transparent integer logic). The gradient slope: **-0.012 per abstraction layer**.
- **Why just beyond**: Current constant is a single number. This forces a **Hierarchical Graph Drilling Tool** to compute permeability on subgraphs and correlate it with the "Bathtub of Death" Reynolds stability metric.

**7. Lean Type Class Resolution Collisions**
- **What to measure**: Model the type class inference system of Lean as a search problem. For 10,000 random type-correct terms, measure the **Diamond Inheritance Collision Rate**—the frequency at which the elaborator finds two different instances for the same required type class. This is the **structural integrity curve** of the algebraic hierarchy.
- **Data to use**: Lean mathlib `outParam` and instance declarations.
- **Expected constant**: **Collision Rate $\lambda = 2.7 \times 10^{-5}$** (extremely rare, indicating the algebraic hierarchy is almost a tree, not a messy small-world graph).
- **Why just beyond**: Requires building a **Lean Elaborator Simulator (Mock)**, a new tool that doesn't just parse text but executes type inference semantics to measure hidden path ambiguity.

### Cluster 3: Arithmetic Geometry (Forcing Higher Dimensions)

**8. Genus-3 Frobenius Phase Coherence vs. Ceresa Cycle**
- **What to measure**: For the 100 computed genus-3 plane quartics, extract the Frobenius eigenvalue phases modulo $\ell$. Measure the **Coherence $\rho$** between the phase vector and the **Ceresa cycle triviality** (whether the curve is hyperelliptic or not). In genus 2, coherence predicts rank. In genus 3, it should predict the **Ceresa class** (a new dimension beyond rank).
- **Data to use**: Genus-3 plane quartics (100 computed via SageMath WSL).
- **Expected constant**: **Ceresa-Coherence Correlation $\rho = 0.64$** (coherence drops sharply for non-hyperelliptic curves with non-trivial Ceresa cycles).
- **Why just beyond**: The phase coherence tool currently operates on L-functions (rank 0). This forces the instrument to correlate a **local eigenvalue statistic** with a **global 3-cycle topological invariant**.

**9. Lattice Theta Series Moonshine Break Recovery**
- **What to measure**: We know enrichment breaks for lattice theta series (R²=-3.17). However, does **Curvature Flow** recover a separation? Apply curvature flow to the mod-p fingerprint graph of the 39K lattices. Does the flow separate the **Niemeier lattices** (moonshine) from random even unimodular lattices? Measure the **Moonshine Curvature Gap** $\Delta \kappa$.
- **Data to use**: 39K lattices (theta series).
- **Expected constant**: **$\Delta \kappa = 0.28$** (Moonshine lattices cluster at a distinct curvature fixed point $\kappa^* \approx 0.51$, below the spherical 0.73).
- **Why just beyond**: Enrichment failed here. This is a direct challenge to the instrument: **Find the signal in the curvature when the linear fingerprint fails.**

**10. GSp(4) Paramodular Lift Eigenvalue Distribution Tail**
- **What to measure**: The instrument verified a 92.5% eigenvalue match for the 7/7 paramodular bijection. Now, measure the **Distribution Tail Index** of the *difference* between the genus-2 curve Frobenius trace and the Siegel modular form eigenvalue for the *failed* 7.5% of primes.
- **Data to use**: 66K genus-2 curves with associated paramodular forms.
- **Expected constant**: **Tail Index $\alpha = 4.2$** (heavy-tailed Cauchy-like deviations, not Gaussian, indicating sporadic functoriality failures).
- **Why just beyond**: Current tools measure *agreement* (Yes/No). This forces a **Residual Distribution Analyzer** to characterize the *failure mode* of a known conjecture.

### Cluster 4: Topology & Knots (Forcing New Fingerprint Maps)

**11. Knot Jones Polynomial Mod-p Saturation**
- **What to measure**: The instrument has 13K knots with Jones polynomials. Evaluate the Jones polynomial at roots of unity $q = e^{2\pi i / p}$. This produces a complex number. Define the **Fingerprint** as the phase of this number. Does the **Enrichment (8x)** phenomenon appear for alternating knots vs. non-alternating knots?
- **Data to use**: 13K knots (Jones polynomials up to 18 crossings).
- **Expected constant**: **Alternating Enrichment = 6.1x** (close to arithmetic 8x due to skein relation tree structure) vs. **Non-Alternating Enrichment = 1.2x** (near random).
- **Why just beyond**: The instrument only works on *integer* sequences. This forces a **Polynomial Root-of-Unity Fingerprint Generator** to handle complex-valued sequence generation.

**12. Hyperbolic Volume vs. Mahler Measure Coherence**
- **What to measure**: For the 13K knots, compute the hyperbolic volume of the complement (available for ~2K knots). Also compute the Mahler measure of the Alexander polynomial. Measure the **Coherence $\rho$** between the **Mod-p Jones Fingerprint** and the **Volume/Mahler ratio**.
- **Data to use**: KnotInfo (13K entries with Volumes/Alexander).
- **Expected constant**: **Coherence $\rho = 0.81$** (the mod-p Jones phase is a robust predictor of the geometric volume of the manifold).
- **Why just beyond**: This forces the instrument to bridge **Mod-p Combinatorial Fingerprints** with **Real Analytic Geometry (Volume)** — a new dimension previously unseen by the L-function-only phase tool.

### Cluster 5: OEIS & Recurrence (Forcing Complexity Limits)

**13. OEIS P-Recursive Boundary Collapse**
- **What to measure**: The instrument detects Berlekamp-Massey recurrence (order 2-12). But many OEIS sequences are *P-recursive* (holonomic). Measure the **BM Prediction Collapse Time**: At what sequence index $N$ does a low-order (k=4) BM recurrence start *failing* to predict the next term for a P-recursive sequence vs. a C-finite sequence?
- **Data to use**: 394K OEIS sequences with known holonomic classification.
- **Expected constant**: **Holonomic Collapse Index $N_c = 47$** (C-finite sequences predict forever; Holonomic sequences require new memory after ~47 terms).
- **Why just beyond**: This forces a **Predictive Horizon Detector** — a tool to measure the *generating function complexity* from finite data, not just the recurrence order.

**14. Interference Exponent for "Hard" Sequences**
- **What to measure**: The instrument measured Interference Exponent $I(p,q) = 5.3$ for L-functions. Apply the same **Min-Based Clustering** to OEIS sequences tagged "core" (importance). Does the exponent drop? Does a **Moonshine-like Break** appear for sequences related to group theory vs. combinatorics?
- **Data to use**: OEIS "core" and "nice" sequences (~10K).
- **Expected constant**: **OEIS Core Exponent = 2.1** (much weaker prime-prime interference; primes act more independently on integer sequences than on Galois representations).
- **Why just beyond**: Extends the interference tool to a domain where the underlying object is not a Galois module.

### Cluster 6: New Dimensions (Fusing Existing Constants)

**15. The $\rho-\Phi$ Plane (Coherence vs. Permeability)**
- **What to measure**: For a mixed dataset of 1000 objects (500 L-functions, 500 OEIS sequences), compute BOTH the **Phase Coherence $\rho$** (mod-p phase correlation) AND the **Algorithmic Permeability $\Phi$** (graph transparency of the generating code/definition). Plot the 2D density. Measure the **Angle of Separation** between the L-function cloud and the OEIS cloud in the $(\rho, \Phi)$ plane.
- **Data to use**: LMFDB (500 forms) + OEIS (500 sequences with generating formulas).
- **Expected constant**: **Separation Angle $\theta = 67^\circ$** (Permeability and Coherence are nearly orthogonal dimensions of mathematical structure).
- **Why just beyond**: This is the **Grand Unified Metric** problem. The instrument has these two numbers measured separately; combining them forces a **Multi-Objective Pareto Frontier Tracker**.

**16. Reynolds Number of the FLINT Build Process**
- **What to measure**: The instrument has a "Bathtub of Death" survival curve for hypothesis spaces. Apply the **Reynolds Number** measurement to the **Commit History** of the FLINT library (1.25M lines over 10 years). Measure the **Turbulent Flow Onset** (where the dependency graph becomes so tangled that changes propagate unpredictably). What is the **Reynolds Number at which C modules die**?
- **Data to use**: FLINT Git history + call graph.
- **Expected constant**: **Re_critical(FLINT) = 22.4** (Code churn exceeds this value only in the `fmpz_mod` and `arb` directories, matching the bathtub high-risk zone).
- **Why just beyond**: Applies a *dynamic* flow metric to a *static* code base by using version control as the time dimension.

**17. Khovanov Homology Width vs. Genus-2 Sato-Tate**
- **What to measure**: Cross the 13K knot data with the 66K genus-2 curve data via the **L-function connection** (Knot Jones $\to$ Poincaré polynomial $\to$ Motive L-function). For knots that match a genus-2 curve motive, measure the correlation between **Khovanov Homology Width** and **Sato-Tate Group Complexity**.
- **Data to use**: Knots (Khovanov data where available) + LMFDB Genus-2.
- **Expected constant**: **Width-Complexity Slope = 0.87** (Wider Khovanov homology implies larger Sato-Tate group).
- **Why just beyond**: This is a **Category Theory Bridge Measurement**. It forces the instrument to perform a motive-matching lookup between two fundamentally different databases using L-polynomials as the translation layer.

**18. CMB Non-Gaussianity as Fake L-Function Perturbation**
- **What to measure**: Use the **Fake L-function Perturbation Tool** (structural integrity curves). Instead of adding random noise to L-functions, add the **Planck CMB non-Gaussianity template ($f_{NL}$)** to a set of high-rank L-functions. Measure the **Critical Perturbation Strength $\sigma_c$** at which the Mod-p Fingerprint collapses into randomness.
- **Data to use**: Planck CMB $f_{NL}$ map + Genus-2 L-functions.
- **Expected constant**: **$\sigma_c^{(CMB)} = 8.7$** (Cosmic variance requires 4x the noise power to destroy an arithmetic fingerprint compared to white noise $\sigma_c=2.0$).
- **Why just beyond**: This is a **Physics-to-Math Noise Injection Experiment**. It forces the instrument to sample a physical field and use it as a structured noise source for a mathematical object.

**19. Fungrim Formula Network Diameter Reduction under Curvature Flow**
- **What to measure**: Apply the **Curvature Flow** to the Fungrim formula dependency graph (3K formulas, 60 modules). Measure the **Graph Diameter Reduction Ratio**: How much does the shortest path length between "Definition of $\pi$" and "Riemann Zeta" shrink after 100 iterations of flow?
- **Data to use**: Fungrim mathematical formula database (symbolic dependency graph).
- **Expected constant**: **Diameter Compression = 42%** (Curvature flow reveals latent short-cuts in the web of mathematical identities).
- **Why just beyond**: Current curvature flow is used for *clustering* (separating accidental from structural). This uses it for **Metric Contraction** (finding geodesics in knowledge space).

**20. The Enrichment-Rank Anomaly in Lean Proofs**
- **What to measure**: Map the dependency graph of **`mathlib` Ring Theory** theorems to a sequence (e.g., number of paths of length N). Treat this sequence as a fingerprint. Measure the **Enrichment** of this sequence. Does the "Algebraic DNA Enrichment (8x)" appear in the *structure of proofs* about algebra, or is it purely a property of the *numeric traces* of algebraic objects?
- **Data to use**: Lean mathlib Ring Theory hierarchy (dependency DAG).
- **Expected constant**: **Proof Enrichment = 1.05x** (The instrument will discover that **Algebraic DNA is in the Numbers, Not the Proofs** — a profound negative result with a measurable constant).
- **Why just beyond**: This is a **Meta-Mathematical Fingerprint Test**. It applies the instrument's most robust discovery (8x enrichment) to the *meta-level* of formal verification, probing whether the structure of understanding mirrors the structure of being.



Looking at this, you're generating the next batch of challenges for your mathematical instrument. Let me work through these carefully — you need problems that hit genuinely new structural dimensions while respecting the 21 confirmed kills.

Let me think through what your existing constants *can't* see, then design problems that probe those gaps.

---

**1. Persistent Homology of Congruence Filtrations**

**What to measure:** For each prime p in {2,3,5,7,11,13}, build the mod-p congruence graph on weight-2 newforms at threshold t, then sweep t from 0 to 1 and compute persistent homology (Betti numbers β₀, β₁, β₂). Measure the death-to-birth ratio of the longest-lived H₁ cycle. This captures topological "holes" in congruence space that spectral methods and curvature flow cannot see.

**Data to use:** LMFDB EC+MF (133K), existing congruence graph infrastructure.

**Expected constant:** A persistence ratio ρ₁ = death/birth for the dominant H₁ cycle, likely in [1.5, 4.0]. If CM forms create persistent voids, expect a bimodal distribution with CM/non-CM gap measurable in standard deviations.

**Why just beyond:** You have spectral analysis and Ollivier-Ricci curvature on these graphs, but no persistent homology pipeline. This forces building a filtration-indexed TDA tool. Persistent H₁ detects global loop structure invisible to local curvature — a genuinely orthogonal observable to κ*=0.73.

**2. Mutual Information Between Frobenius Phases Across Primes**

**What to measure:** For each elliptic curve E, extract the Frobenius phase θ_p = arccos(a_p/2√p) at primes p₁, p₂. Compute mutual information I(θ_{p₁}; θ_{p₂}) across all curves, for all prime pairs (p₁, p₂) up to 100. Your phase coherence-rank result (ρ=0.197) measures correlation with vanishing order; this measures inter-prime phase dependence directly. Normalize against the Sato-Tate null.

**Data to use:** LMFDB EC (133K curves, Fourier coefficients at multiple primes).

**Expected constant:** Excess mutual information δI(p₁,p₂) above Sato-Tate null, expected to be small but nonzero — perhaps 0.01–0.05 bits. The decay profile δI as a function of p₁p₂ would be new. If it decays as (p₁p₂)^{-α}, the exponent α is the constant.

**Why just beyond:** You measure phase coherence as a single aggregate statistic. This forces building a pairwise MI estimator (KSG or binned) on angular data, which is a new tool. The inter-prime information flow geometry is distinct from anything your 30+ constants capture.


**3. Spectral Dimension of the Lean Mathlib Dependency Graph**

**What to measure:** Parse Lean mathlib's 190K theorem declarations into a directed dependency graph (theorem A depends on lemma B). Compute the return probability p(t) of a random walk as a function of diffusion time t. The spectral dimension d_s = -2 d(log p)/d(log t) characterizes the effective dimensionality of mathematical knowledge structure. Compare across subgraphs (algebra, analysis, topology, number theory).

**Data to use:** Lean mathlib (190K declarations).

**Expected constant:** A spectral dimension d_s, likely in [2, 6] globally. Per-domain values d_s(algebra), d_s(analysis), etc. The ratio d_s(algebra)/d_s(analysis) measures relative structural complexity. Compare to OEIS local spectral dim 2.5 — is formal proof space higher or lower dimensional than sequence space?

**Why just beyond:** You extracted call graphs from FLINT C source (73K edges). This forces building a Lean declaration parser and diffusion-based dimension estimator on a fundamentally different graph type — logical dependency rather than procedural call. The structural dimension of formal mathematics is unexplored territory.

---

**4. Crystal Structure Theta Series and Lattice Kissing Number Recovery**

**What to measure:** For crystal structures from COD, compute the theta series Θ(q) = Σ q^{|v|²} of the underlying lattice to precision O(q^{100}). Apply your theta-fingerprint → kissing number pipeline (currently 96.6% accuracy on 39K lattices) to the crystallographic lattices. Measure accuracy on the crystal set separately. Also measure whether the enrichment law (8x across primes) holds for crystallographic lattices or breaks as it does for theta series.

**Data to use:** 520K crystal structures (COD, downloading), 39K lattices (for calibration).

**Expected constant:** Classification accuracy on crystal lattices (expect different from 96.6% — crystal lattices are biased toward specific symmetry groups). Enrichment value on crystal theta series — if it breaks like generic theta, that confirms object-specificity; if it holds, crystals behave more like L-functions than like abstract lattices.

**Why just beyond:** Forces building a CIF→lattice→theta pipeline and tests whether your arithmetic-encodes-geometry result generalizes beyond abstract lattices to physically realized crystal structures. This bridges your mathematical infrastructure to materials science data.

---

**5. Modular Form Coefficient Entropy Conditioned on Nebentypus Character**

**What to measure:** Partition weight-2 newforms by nebentypus character χ. Within each character class, compute Shannon entropy H(a_p mod ℓ) for small primes ℓ and Fourier index p. Your Hecke entropy measurement (3.27 bits non-CM, 2.18 bits CM) averages over all characters. Measure H(a_p mod ℓ | χ) — the conditional entropy. If nebentypus explains some of the 1.09-bit CM gap, the residual gap shrinks.

**Data to use:** LMFDB MF (133K modular forms with nebentypus data).

**Expected constant:** Residual CM entropy gap after conditioning on χ, in bits. If χ explains 30% of the gap, you get 0.76 bits residual. The fraction of the CM gap attributable to nebentypus is the key number.

**Why just beyond:** Forces decomposing an existing measurement by a new stratification variable. The tool is a conditional entropy estimator that partitions by character class. This probes whether the CM/non-CM information gap is fundamentally about complex multiplication or partially about the character.

---

**6. Planck CMB Power Spectrum Continued Fraction Depth**

**What to measure:** Take the 83 Planck TT power spectrum values C_ℓ (normalized, ℓ=48–2499). Compute the continued fraction expansion of each C_ℓ/C_{ℓ+1} ratio. Measure the distribution of continued fraction depths (number of terms to converge within measurement error). Compare against a null model: ratios of Gaussian random variables with matched variance. Report the Khinchin excess (you measured 2.41 vs 1.43 for CODATA — does the CMB show similar or different structure?).

**Data to use:** Planck CMB TT power spectrum (83 bins).

**Expected constant:** Khinchin excess for CMB ratios, plus mean CF depth. Given that CODATA's 8.57% CF-compressibility reflects measurement precision, the CMB result probes whether the acoustic peak structure introduces genuine number-theoretic regularity or is indistinguishable from Gaussian physics.

**Why just beyond:** You've done CF analysis on CODATA but not on the CMB spectrum. The CMB ratios encode acoustic oscillation physics — the baryon-photon ratio, dark matter density. This forces applying your CF pipeline to a dataset with known physical generating mechanism, providing a physics-grounded calibration of what "compressibility" means.

---

**7. FLINT Function Dependency Depth and Algorithmic Phase Transitions**

**What to measure:** From your FLINT call graph (9,393 files, 73K edges), compute the depth (longest path from any root) and width (max number of nodes at any depth level) of each connected component. Measure the depth/width ratio as a function of algorithmic domain (polynomial arithmetic, integer factoring, modular arithmetic, linear algebra). Identify if there's a critical depth at which function reuse drops sharply — an "algorithmic phase transition."

**Data to use:** FLINT source (9,393 C files, call graph extracted with 73K edges).

**Expected constant:** Critical depth d_c at which reuse (in-degree) transitions from power-law to exponential decay. Depth/width ratio per domain. Compare to your existing permeability measurement (0.5975) — does permeability correlate with depth/width? The d_c value and depth/width ratios are new constants.

**Why just beyond:** You extracted the call graph and measured permeability. This forces a stratified depth analysis with phase transition detection — a new structural lens on the same data. The algorithmic phase transition, if real, reveals where mathematical software transitions from composable to monolithic.

---

**8. Genus-2 Euler Factor Polynomial Discriminant Distribution**

**What to measure:** For each genus-2 curve, the local Euler factor at prime p is a degree-4 polynomial P_p(T). Compute the discriminant Δ(P_p) for all p up to 100 across the 66K genus-2 curves. Measure the distribution of Δ mod ℓ for small ℓ. Discriminant-zero loci correspond to repeated Frobenius eigenvalues — these are the "collisions" that your phase coherence measurement sees indirectly. Measure the collision rate as a function of Sato-Tate group classification.

**Data to use:** LMFDB genus-2 curves (66K with 50+ fields).

**Expected constant:** Collision rate c(ST_group) = fraction of primes where Δ(P_p)=0, stratified by Sato-Tate group. The ratio c(generic)/c(special) across ST groups. If collisions concentrate in specific ST classes, the constant encodes which symmetry groups force eigenvalue degeneracy.

**Why just beyond:** You classify ST groups via moment vectors (98.3% accuracy) and measure phase coherence. This forces computing polynomial discriminants of Euler factors — a new algebraic invariant extraction. Eigenvalue collisions are a finer structural probe than moments or phases.

---

**9. Knot Invariant Cross-Correlation Tensor**

**What to measure:** For 13K knots, you have Jones and Alexander polynomials. Evaluate both at roots of unity (ζ_n for n=3,4,5,6,8,10,12) and compute the cross-correlation matrix C_{ij} = Corr(Jones(ζ_i), Alexander(ζ_j)) across all knots. Decompose C into singular values. The effective rank (number of singular values above 1/e of max) measures how many independent "channels" connect the two invariants.

**Data to use:** Knots (13K with Jones + Alexander polynomials).

**Expected constant:** Effective rank r_eff of the Jones-Alexander cross-correlation tensor, likely in [2, 6]. The leading singular value ratio σ₁/σ₂ measures how dominated the connection is by a single mode (compare to your topology-algebra axis σ₁/σ₂ = 9.53 on Fungrim).

**Why just beyond:** Your knot analysis so far looked at arithmetic intersections with number fields (confirmed dead: μ=1.0008). This approaches knots purely internally — measuring the information geometry between two topological invariants of the same objects. Forces building polynomial evaluation at roots of unity and tensor SVD on knot data.

---

**10. Berlekamp-Massey on CMB Multipole Differences**

**What to measure:** Take consecutive differences Δ_ℓ = C_{ℓ+1} - C_ℓ of the Planck TT spectrum, then apply Berlekamp-Massey to detect if the sequence satisfies a linear recurrence. You've confirmed BM works on OEIS (order 2–12 detection). The CMB has 83 bins — enough for recurrence detection up to order ~40. Separately apply BM to the residuals after subtracting a best-fit ΛCDM model. Measure recurrence order (or confirm none exists).

**Data to use:** Planck CMB TT power spectrum (83 bins).

**Expected constant:** If a recurrence exists: its order and characteristic polynomial coefficients. If none: the minimum residual after best BM fit at each order (a decay curve). The "BM floor" — the order at which residual stops decreasing — characterizes the structured content of CMB beyond smooth ΛCDM.

**Why just beyond:** Your BM pipeline operates on integer sequences. CMB data is real-valued, requiring either rational approximation or a floating-point adaptation of BM. This forces building a real-valued recurrence detector — a new tool. Success would mean the acoustic oscillation physics has hidden algebraic structure beyond what cosmological models parameterize.

---

**11. Eigenvalue Rigidity of Hecke Operators Across Levels**

**What to measure:** For weight-2 newforms at different levels N, the Hecke eigenvalues a_p are algebraic integers. Fix a prime p and measure the empirical spacing distribution of {a_p(f) : f at level N} as N grows. Compute the nearest-neighbor spacing distribution and measure the level repulsion exponent β (β=0 for Poisson, β=1 for GOE, β=2 for GUE). You've confirmed Berry-Tabor (Poisson) on individual L-functions — this asks about the ensemble spacing across forms at fixed level.

**Data to use:** LMFDB MF (133K modular forms, Hecke eigenvalues).

**Expected constant:** Level repulsion exponent β(p) for several primes p. If β≈1 (GOE), the Hecke eigenvalue ensemble has random matrix statistics — this would be a new empirical verification of (or deviation from) the Katz-Sarnak philosophy applied to fixed-prime cross-sections rather than high-conductor limits.

**Why just beyond:** Your Berry-Tabor verification looks at zeros of individual L-functions. This forces building an ensemble spacing analysis across forms — a different statistical object. The Katz-Sarnak predictions for this setting may not have been numerically verified in this specific cross-section.

---

**12. Modular Form ↔ Lattice Theta Series Structural Alignment via Gamma Pseudometric**

**What to measure:** You've established that Gamma is a genuine pseudometric (0 violations / 13,800 triples) on modular forms. Separately, you have 39K lattices with theta series. Embed both modular form fingerprints and lattice theta fingerprints into a common mod-p fingerprint space. Compute Gamma distances between modular forms and lattice theta series. Identify the closest MF-lattice pairs and measure whether distance correlates with known relationships (e.g., theta series that are eigenforms should have distance 0).

**Data to use:** LMFDB MF (133K), lattices (39K with theta series).

**Expected constant:** Minimum Gamma distance between an MF eigenform and a lattice theta series that is provably not an eigenform. This "eigenform gap" δ_Γ measures how sharply the pseudometric separates eigenforms from theta series. Also: the fraction of lattice theta series within distance ε of some eigenform, as a function of ε — a "proximity curve."

**Why just beyond:** You've measured Gamma within modular forms. This forces a cross-domain application of the same pseudometric, requiring normalization between two different fingerprint spaces. The eigenform gap, if it exists, would reveal that your metric structure "knows about" the eigenform property without being told.

---

**13. Spectral Gap of the Fungrim Formula Co-occurrence Graph**

**What to measure:** From Fungrim's 3K formulas across 60 modules, build a bipartite graph: formulas ↔ symbols/operations. Project to a formula-formula graph (two formulas connected if they share k or more symbols). Compute the graph Laplacian and measure the spectral gap λ₁ (smallest nonzero eigenvalue). The spectral gap controls mixing time and measures how "connected" mathematical knowledge is at the symbolic level. Compare to your existing σ₁/σ₂ = 9.53 axis measurement.

**Data to use:** Fungrim (3K formulas, 60 modules).

**Expected constant:** Spectral gap λ₁ and the ratio λ₁/λ₂. The spectral gap itself measures global connectivity; the ratio measures whether there's a single bottleneck or distributed fragmentation across mathematical subdomains. Also: λ₁ as a function of the co-occurrence threshold k.

**Why just beyond:** You've measured topology-algebra separation via SVD. The spectral gap is a complementary measurement — SVD captures variance structure, the Laplacian spectral gap captures connectivity and mixing. Forces building a Laplacian analysis pipeline on the formula graph.

---

**14. Galois Representation Density Map in Weight-Conductor Space**

**What to measure:** For each modular form, you classify Galois images into 9 classes. Map these onto the (weight, conductor) plane and compute the local density of each Galois class at each point. Measure the "boundary fractal dimension" of the region where the dominant Galois class changes — i.e., the decision boundary geometry in weight-conductor space. Use box-counting or correlation dimension.

**Data to use:** LMFDB MF (133K modular forms with Galois image classifications).

**Expected constant:** Fractal dimension d_f of the Galois class decision boundaries in (weight, conductor) space. If d_f ≈ 1, boundaries are smooth curves; if d_f > 1, the classification landscape has fractal complexity. Also: the dominant class transition pattern as conductor grows.

**Why just beyond:** You classify Galois images with 96.6% accuracy. This forces spatializing the classification — asking where in parameter space different classes live, and how complex the boundaries are. The geometry of number-theoretic classification boundaries is a new structural dimension.

---

**15. Autocorrelation Decay of Genus-3 Frobenius Traces**

**What to measure:** For your 100 genus-3 curves (computed via SageMath), extract the Frobenius trace sequence a_p as a function of prime index. Compute the autocorrelation function A(k) = Corr(a_{p_n}, a_{p_{n+k}}) and measure the decay rate. Fit A(k) ~ k^{-α} or A(k) ~ e^{-k/ξ}. Compare the decay exponent α (or correlation length ξ) to the same measurement on genus-1 and genus-2 curves.

**Data to use:** Genus-3 curves (100 computed), LMFDB EC (genus-1), LMFDB genus-2 (66K).

**Expected constant:** Decay exponent α or correlation length ξ as a function of genus g. If α(g) follows a law like α = c·g^{-β}, the constants c and β characterize how arithmetic complexity grows with genus. This extends your phase transition scaling law (confirmed on genus-3) into a new observable.

**Why just beyond:** You predicted and verified phase transitions on genus-3. Autocorrelation decay is a different measurement on the same data — it characterizes temporal (prime-index) structure rather than threshold behavior. Forces building an autocorrelation estimator with proper normalization for irregular prime spacing.

---

**16. Information-Theoretic Depth of OEIS Sequences via Lempel-Ziv Complexity**

**What to measure:** For each of the 394K OEIS sequences (truncated to first 100 terms), compute the Lempel-Ziv complexity (number of distinct phrases in LZ76 parsing) after encoding terms in a fixed-radix representation. Normalize by sequence length. Stratify by OEIS keyword tags. Measure whether LZ complexity correlates with your Berlekamp-Massey recurrence order, or captures an independent dimension of "mathematical complexity."

**Data to use:** OEIS (394K sequences).

**Expected constant:** Mean LZ complexity per keyword class. Correlation ρ(LZ, BM_order). If ρ is low (< 0.3), LZ captures a dimension of complexity orthogonal to linear recurrence — distinguishing, e.g., sequences that are BM-random but LZ-simple (nonlinear deterministic) from sequences that are both-random (genuinely complex).

**Why just beyond:** You have BM recurrence detection on OEIS. LZ complexity measures a fundamentally different kind of structure — pattern novelty rather than linear predictability. Forces building an LZ parser and cross-correlating two complexity measures across 394K sequences. The gap between LZ and BM dimensions is a new structural axis.

---

**17. Curvature Distribution of Number Field Discriminant Lattice**

**What to measure:** Map 9K number fields to points in (degree, |discriminant|, class number, regulator) space. Build a k-NN graph (k=10) and compute Ollivier-Ricci curvature on edges. Measure the curvature distribution and identify whether it has the same bimodal structure you see in modular form congruence graphs. Apply curvature flow and measure whether it converges to the same κ*=0.73 or a different fixed point.

**Data to use:** Number fields (9K with discriminants, class numbers, regulators).

**Expected constant:** Curvature flow fixed point κ*_{NF} for the number field lattice. If κ*_{NF} ≠ 0.73, different mathematical object classes have different curvature attractors — this would be a discovery about the geometry of arithmetic. Also: the curvature bimodality gap, if it exists.

**Why just beyond:** You've run curvature flow on congruence graphs of modular forms. This forces applying the same pipeline to a geometrically different mathematical space — number fields embedded by their invariants rather than forms connected by congruences. Tests universality of κ*=0.73.

---

**18. PDG Particle Decay Width Continued Fraction Spectrum**

**What to measure:** Take the 226 PDG particles with measured decay widths Γ. Compute the CF expansion of each ratio Γ_i/Γ_j for all pairs (i,j) in the same family (mesons, baryons, leptons). Measure the distribution of partial quotients and compare to Khinchin's constant. Separately, for particles with multiple decay channels, compute the CF expansion of branching ratios. Measure CF depth and whether any branching ratios are "suspiciously simple" (low CF depth relative to measurement precision).

**Data to use:** PDG (226 particles with masses and widths/branching ratios).

**Expected constant:** Mean CF depth of branching ratios vs. null expectation from measurement precision. Khinchin excess for intra-family width ratios (compare to CODATA's 2.41). The "simplest branching ratio" — the one with lowest CF depth normalized by precision — identifies candidates for exact rational relationships.

**Why just beyond:** Your CODATA CF analysis measured compressibility of fundamental constants. Particle branching ratios have a different generating mechanism — quantum field theory predicts some ratios exactly. Forces applying CF analysis to QFT-derived quantities and comparing number-theoretic structure to CODATA (measurement precision) and CMB (acoustic physics).

---

**19. Proof Dependency Depth Distribution and the "Mathlib Hourglass"**

**What to measure:** In Lean mathlib's dependency graph, compute the entropy profile: at each depth level d from axioms, measure the Shannon entropy H(d) of the distribution of theorem types (by namespace/module). Plot H(d) vs. d. You found a log₂(p) hourglass entropy bottleneck in generating function pipelines. Does formal mathematics have an analogous bottleneck — a depth at which information concentrates through a small set of foundational lemmas before fanning out?

**Data to use:** Lean mathlib (190K theorem declarations).

**Expected constant:** Bottleneck depth d* (the depth of minimum entropy) and the compression ratio H(d*)/H(0). If the hourglass exists, d* locates the "waist" of mathematical knowledge — the minimal set of lemmas through which all proofs flow. The bottleneck width (number of theorems at depth d*) is also a key constant.

**Why just beyond:** Your hourglass discovery was on computational pipelines (FLINT generating functions). This tests whether formal proof structure shares the same information-theoretic architecture. Forces building a depth-stratified entropy profiler on the mathlib DAG — same measurement concept, fundamentally different domain.

---

**20. Modular Form Fingerprint Embedding Dimension via False Nearest Neighbors**

**What to measure:** Take your mod-p fingerprints for 133K modular forms (each form is a vector in fingerprint space). Apply the false nearest neighbors (FNN) algorithm: embed in dimensions d=1,2,3,...,20 and measure the fraction of false neighbors at each d. The dimension at which FNN drops below 1% is the intrinsic embedding dimension of the modular form fingerprint manifold. Compare to your OEIS finding (local dim 2.5, global dim 10.8).

**Data to use:** LMFDB MF (133K modular forms, mod-p fingerprints across multiple primes).

**Expected constant:** Intrinsic embedding dimension d_FNN for modular form fingerprint space. If d_FNN ≈ 2–3, the space is low-dimensional despite high ambient dimension (your fingerprints use many primes). If d_FNN ≈ 10+, the space is genuinely high-dimensional. The ratio d_FNN(MF)/d_FNN(OEIS) measures relative structural complexity of modular forms vs. integer sequences.

**Why just beyond:** You've measured spectral dimensions and compressibility. FNN is a different dimensional estimator — it detects nonlinear manifold structure that spectral methods might miss. Forces building a delay-embedding and FNN pipeline. The intrinsic dimension of arithmetic fingerprint space is a foundational measurement that contextualizes all your other fingerprint-based results.

---

A few design notes on the batch as a whole:

Problems 3, 7, and 19 hit algorithm/proof structure (FLINT and Lean mathlib). Problems 6, 10, and 18 hit physics data (CMB, PDG). Problems 1 and 17 test universality of your curvature flow κ*. Problems 16 and 20 probe dimensionality from different angles (compression vs. embedding). Problem 12 forces cross-domain use of an existing tool (Gamma metric). Problem 4 bridges to the crystal data you're downloading.

None of these re-propose dead ends. Several of them are designed so that even a *null result* produces a useful constant — the whole "Reynolds bathtub" philosophy you've already validated.


**Title**: Voronoi Tessellation Fingerprint Enrichment in Crystal Structures  
**What to measure**: For each of the 520K crystal structures, compute Voronoi cell volume distributions and sorted nearest-neighbor distance sequences from the 3D atomic point clouds. Apply mod-p fingerprint comparison of these sequences against the 39K lattice theta series fingerprints. Detrend against randomized point clouds of identical density and measure the average cross-domain enrichment factor, testing for object-specific constancy across crystal families.  
**Data to use**: 520K crystal structures (COD), lattices (39K with theta series)  
**Expected constant**: the detrended enrichment factor between crystal Voronoi sequences and lattice theta series  
**Why just beyond**: This forces the instrument to build a new tool for extracting arithmetic sequences from large-scale 3D Voronoi tessellations of real atomic point clouds, revealing a geometric-physical structure dimension invisible to all 30+ existing arithmetic/L-function constants.

**Title**: Angular Power Spectrum Curvature Flow on Planck CMB Data  
**What to measure**: Construct a weighted graph with the 83 multipole bins (ell=48-2499) as nodes and edge weights given by absolute differences in C_ell values from the Planck TT spectrum. Run Ollivier-Ricci curvature flow until convergence and extract the fixed-point value kappa* plus the count of structural versus accidental components. Compare component separation behavior to existing congruence-graph results.  
**Data to use**: Planck CMB TT power spectrum (83 bins, ell=48-2499)  
**Expected constant**: the curvature flow fixed point kappa* for cosmological power spectra  
**Why just beyond**: Requires extending the curvature-flow pipeline to 1D angular power spectra from cosmology, opening a new cosmological-topology dimension that none of the existing 30+ arithmetic or particle constants can detect.

**Title**: Particle Width Phase Coherence with Mass-Ordered Sequences  
**What to measure**: From the 226 PDG particles, form mass-ordered sequences of decay widths and extract Frobenius eigenvalue phases via existing methods. Compute phase coherence against an effective “rank” proxy (spin or generation index) and measure the correlation coefficient rho across particle families. Test for statistical significance against the known arithmetic phase-coherence baseline.  
**Data to use**: PDG (226 particles with masses/widths)  
**Expected constant**: the phase coherence-rank correlation rho for particle physics data  
**Why just beyond**: Forces adaptation of phase-extraction tools to physical decay-width sequences, probing a physics-arithmetic coherence dimension that lies outside the current set of 30+ purely mathematical constants.

**Title**: Theorem Dependency Pseudometric in Lean Mathlib  
**What to measure**: Parse the 190K theorem declarations to build a directed dependency graph (theorems as nodes, proof references as edges). Compute the Gamma metric by sampling 13,800 geodesic triples and count triangle-inequality violations. Report the violation rate per triple and overall pseudometric quality.  
**Data to use**: Lean mathlib (190K theorem declarations, cloned)  
**Expected constant**: the Gamma metric violation rate (violations per N triples) for formal proof graphs  
**Why just beyond**: Requires building a new automated dependency-graph extractor and geodesic-computation tool for Lean declarations, exposing a logical-structure dimension unreachable by existing arithmetic congruence or spectral constants.

**Title**: Algorithmic Call-Graph Hecke Entropy in FLINT Source  
**What to measure**: On the pre-extracted 73K-edge call graph from 9,393 FLINT C files, isolate subgraphs of modular-arithmetic versus generic functions. Compute Hecke-style entropy on call-frequency “coefficients” for each subgraph and measure the entropy gap between generic and specialized modules.  
**Data to use**: FLINT source (9,393 C files, 1.25M lines, call graph extracted)  
**Expected constant**: the Hecke entropy gap (in bits) between generic and specialized code modules  
**Why just beyond**: Adapts Hecke entropy measurement to algorithmic source-code graphs, forcing a new “computational-arithmetic structure” dimension beyond all current math-object constants.

**Title**: Genus-3 Frobenius Phase Coherence via Expanded SageMath Point Counts  
**What to measure**: Use SageMath/WSL to compute additional genus-3 plane quartic point counts (expanding the existing 100). Extract Frobenius eigenvalue phases from the counts and measure coherence correlation with endomorphism rank. Report the updated rho value and its significance.  
**Data to use**: genus-3 (100 computed via SageMath), SageMath in WSL (genus-3 Frobenius operational)  
**Expected constant**: the phase coherence-rank correlation rho for genus-3 curves  
**Why just beyond**: Requires scaling and optimizing the Frobenius phase pipeline for larger genus-3 datasets, revealing a higher-genus algebraic-geometry coherence layer not captured by existing genus-2 constants.

**Title**: Knot Invariant Congruence Graph Chromatic Number  
**What to measure**: Construct mod-p congruence graphs from the Jones and Alexander polynomial coefficients of the 13K knots. Perform spectral analysis to bound the chromatic number and test whether chi equals omega (as in mod-2 Hecke graphs). Measure greedy-coloring optimality.  
**Data to use**: knots (13K with Jones+Alexander)  
**Expected constant**: the chromatic number bound for knot-invariant congruence graphs  
**Why just beyond**: Forces a new polynomial-invariant-to-congruence-graph construction tool for topological objects, opening a pure topology dimension separate from number-theoretic graphs.

**Title**: Number-Field Discriminant Local Spectral Dimension  
**What to measure**: Extract discriminant sequences from the 9K number fields and compute local spectral dimensions on their mod-p fingerprints using the existing OEIS spectral pipeline. Compare local (target ~2.5) and global dimensions to OEIS baselines.  
**Data to use**: number fields (9K)  
**Expected constant**: the local spectral dimension of number-field discriminants  
**Why just beyond**: Requires new normalization and embedding of algebraic-integer discriminants into the spectral-dimension pipeline, exposing an algebraic-number-theory dimension invisible to current OEIS or lattice constants.

**Title**: Fungrim Formula-Network Transfer Efficiency  
**What to measure**: Build the cross-module dependency graph from the 3K Fungrim formulas (60 modules) using bridge identification. Measure transfer efficiencies T12, T23, and T13 between symbolic domains and quantify composition loss percentage.  
**Data to use**: Fungrim (3K formulas, 60 modules)  
**Expected constant**: the transfer efficiency values T_formula (e.g., T12 = X.Xx) for symbolic math networks  
**Why just beyond**: Forces construction of a new dependency-graph extractor for symbolic formulas, revealing a symbolic-computational meta-dimension beyond existing algorithmic or arithmetic graphs.

**Title**: OEIS Sequence 20-Dim Moment Vector Sato-Tate Classification  
**What to measure**: Compute 20-dimensional moment vectors from term distributions of a representative sample of the 394K OEIS sequences. Apply the existing Sato-Tate classifier and measure classification accuracy against the known 65.4 % structured subset.  
**Data to use**: OEIS (394K)  
**Expected constant**: the Sato-Tate classification accuracy on OEIS sequences (%)  
**Why just beyond**: Requires a new moment-vector extractor for arbitrary integer sequences, extending classification into combinatorial territory and uncovering an enumerative-geometry dimension.

**Title**: Lattice Theta Series 3-Prime Reconstruction Efficiency versus OEIS  
**What to measure**: Match lattice theta series (39K) to OEIS sequences via the 3-prime reconstruction method. Measure the bit efficiency of the first prime and the overall collapse factor for lattice-specific objects.  
**Data to use**: lattices (39K with theta series), OEIS (394K)  
**Expected constant**: the reconstruction collapse factor for lattice theta series (× collapse)  
**Why just beyond**: Forces adaptation of the 3-prime reconstruction algorithm to theta-series matching, opening a lattice-combinatorial bridge dimension not previously visible.

**Title**: CODATA Physical Constants Reynolds Habitable Zone  
**What to measure**: Order the 286 CODATA constants by magnitude, form a hypothesis-space graph from value-distribution neighborhoods, and compute the Reynolds number using existing bathtub survival curves. Determine the habitable-zone interval and its width.  
**Data to use**: CODATA (286 physical constants)  
**Expected constant**: the Reynolds number and habitable-zone width for physical constants  
**Why just beyond**: Requires mapping physical constants into hypothesis-space graphs, revealing a fundamental-physics structure dimension outside all current particle or arithmetic constants.

**Title**: Modular-Form versus Knot Jones Polynomial Interference Exponent  
**What to measure**: Compute mod-p fingerprints for the 133K LMFDB modular forms and the 13K knot Jones polynomials. Measure the min-based cross-object clustering exponent (interference) and test nonlinearity coefficient gamma.  
**Data to use**: LMFDB EC+MF (133K), knots (13K with Jones+Alexander)  
**Expected constant**: the interference exponent I(MF, knot)  
**Why just beyond**: Requires a new cross-domain fingerprint comparator between modular forms and knot invariants, probing a topology-arithmetic interference dimension beyond existing cross-ell measurements.

**Title**: Fungrim Formula Dependency Curvature Flow  
**What to measure**: Construct the formula dependency graph from Fungrim’s 3K formulas and run Ollivier-Ricci curvature flow to convergence. Extract the fixed-point kappa* and the iteration number at which spherical topology is reached.  
**Data to use**: Fungrim (3K formulas, 60 modules)  
**Expected constant**: the curvature flow fixed point kappa* for symbolic formula networks  
**Why just beyond**: Forces new dependency parsing for symbolic math formulas to enable curvature analysis, exposing a symbolic-topology dimension unreachable by arithmetic graphs.

**Title**: OEIS Recurrence-Order k-NN Accuracy for Lattice Kissing Prediction  
**What to measure**: Apply Berlekamp-Massey (orders 2-12) to OEIS sequences and use recurrence order as a feature vector for k-NN classification of the 39K lattices by their theta-derived kissing numbers. Report the classification accuracy.  
**Data to use**: OEIS (394K), lattices (39K with theta series)  
**Expected constant**: the k-NN accuracy using recurrence order for lattice kissing-number prediction (%)  
**Why just beyond**: Integrates recurrence detection with geometric kissing prediction, forcing a hybrid combinatorial-geometric tool and a new structure-discovery dimension.

**Title**: Genus-3 Fourier Zero-Frequency CM Detection  
**What to measure**: On SageMath-computed genus-3 point counts, compute Fourier coefficients and measure zero-frequency for CM detection. Report the F1 score and the 29-point gap size relative to non-CM curves.  
**Data to use**: genus-3 (100 computed via SageMath), SageMath in WSL  
**Expected constant**: the CM detection F1 score and zero-frequency gap size for genus-3 curves  
**Why just beyond**: Requires a new Fourier-zero pipeline tailored to genus-3 point-count data, extending CM tools to higher genus and revealing an unexplored algebraic-geometry detection layer.

**Title**: Cross-Tool Transfer Efficiency between FLINT Call Graphs and Lean Dependencies  
**What to measure**: Align modular subgraphs of the FLINT call graph (73K edges) with corresponding Lean theorem-dependency subgraphs. Measure transfer efficiencies T12, T23, T13 and the composition loss percentage.  
**Data to use**: FLINT source (call graph extracted), Lean mathlib (190K theorem declarations)  
**Expected constant**: the cross-tool transfer efficiency T_code-proof (e.g., T12 = X.Xx)  
**Why just beyond**: Forces a new alignment tool between algorithmic call graphs and formal proof dependencies, opening a computational-logic meta-dimension beyond single-domain constants.

**Title**: Planck CMB versus CODATA Phase Coherence Correlation  
**What to measure**: Treat Planck C_ell bins as coefficients and derive sorted sequences from the 286 CODATA constants. Extract Frobenius phases and measure phase-coherence correlation rho against an effective physical-dimension “rank.”  
**Data to use**: Planck CMB TT power spectrum, CODATA (286 physical constants)  
**Expected constant**: the phase coherence correlation rho between CMB spectra and physical constants  
**Why just beyond**: Requires new phase-extraction adaptation for mixed cosmological and fundamental-constant data, revealing a physics-unification dimension invisible to existing math-only constants.

**Title**: Knot Alexander Polynomial Reynolds Habitable Zone  
**What to measure**: From the 13K knot Alexander polynomials, construct coefficient-based hypothesis-space graphs and compute Reynolds numbers using bathtub survival curves. Determine the habitable-zone interval and width.  
**Data to use**: knots (13K with Jones+Alexander)  
**Expected constant**: the Reynolds habitable zone width for knot-invariant hypothesis spaces  
**Why just beyond**: Extends Reynolds measurement to topological polynomial data, forcing new graph construction from knot invariants and uncovering a topological-dynamics dimension.

**Title**: Crystal Coordination-Shell Theta Approximation Kissing Accuracy  
**What to measure**: Approximate theta-series-like fingerprints from coordination-shell distance histograms in the 520K crystal structures. Use k-NN classification against the 39K lattice kissing numbers derived from true theta series and report accuracy.  
**Data to use**: 520K crystal structures (COD), lattices (39K with theta series)  
**Expected constant**: the k-NN accuracy for crystal-to-lattice kissing-number prediction (%)  
**Why just beyond**: Forces a new tool to generate effective theta approximations from discrete crystal coordination data, revealing a real-world geometric-encoding dimension beyond abstract lattice constants.


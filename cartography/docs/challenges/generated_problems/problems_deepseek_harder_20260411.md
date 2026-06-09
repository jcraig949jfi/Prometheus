# DeepSeek HARDER Round — 2026-04-11
# Calibrated to moment hierarchy + unit-circle hypothesis

Here are 20 harder problems designed to probe the discovered patterns and boundaries.

### **Category 1: Probing the Moment Hierarchy (M4/M2² between 1.5 and 2.0)**
These aim to find systems in the "chaotic" to "SU(2)/Knot" transition zone.

**1.1 Modular Form Fourier Coefficients at Prime Powers**
*   **What to measure:** The kurtosis (M4/M2²) of the distribution of normalized Fourier coefficients `a(p^k)` for weight-1 modular forms in the LMFDB, across primes `p` for a fixed small exponent `k` (e.g., k=3,4).
*   **Data:** LMFDB weight-1 modular forms (Maass forms could also be tested).
*   **Expected constant:** ~1.8-1.95. Weight-1 forms are linked to Galois representations, which sit between deterministic and fully chaotic systems. The moment should be above chaos (1.5) but below or near the SU(2) bound of 2.0.
*   **Why harder:** Requires isolating prime-power coefficients, handling sparse data, and interpreting the result in the context of Sato-Tate distributions for non-holomorphic forms.

**1.2 Eigenvalue Gaps in Polygonal Billiards**
*   **What to measure:** M4/M2² for the normalized nearest-neighbor spacing distribution of eigenvalues (vibrational modes) for irrational-angled triangular billiards.
*   **Data:** Compute eigenvalues for a set of triangular domains with angles `(π/p, π/q, π/r)` where p,q,r are distinct primes > 5.
*   **Expected constant:** ~1.7-1.9. Polygonal billiards are classically chaotic but with mild singularities. They should exceed the generic chaotic (GOE) value of ~1.5 but not reach the full rigidity of integrable systems (Poisson, 6.0).
*   **Why harder:** Requires large-scale numerical solution of the Helmholtz equation on singular domains and careful unfolding of the spectrum.

**1.3 Zeroes of Dirichlet L-functions with High Conductor**
*   **What to measure:** M4/M2² for the distribution of imaginary parts of non-trivial zeros for a single, very high-conductor Dirichlet L-function (e.g., modulus q > 10^6).
*   **Data:** Compute zeros for a selected high-conductor L-function.
*   **Expected constant:** ~1.5-1.6. While zeros of a *family* follow GUE (M4/M2² ~2.0), zeros of a *single* high-function are believed to show increasing rigidity, potentially pulling the moment down towards the chaotic (GOE) value.
*   **Why harder:** Requires computing millions of zeros for a single L-function with extreme conductor, a massive computational number theory task.

**1.4 Step Sizes in "Almost-Isospectral" Non-Isometric Drums**
*   **What to measure:** Construct pairs of non-isometric planar domains that are "almost isospectral" (first N eigenvalues match). Measure M4/M2² of the distribution of subsequent eigenvalue step differences `(λ_{N+k}^A - λ_{N+k}^B)`.
*   **Data:** Generated pairs of domains via Sunada-type methods or numerical optimization.
*   **Expected constant:** ~1.6-1.8. The correlated yet divergent sequences should produce a residual distribution less chaotic than GOE but not as structured as a pure integrable difference.
*   **Why harder:** Involves domain generation via advanced group-theoretic constructions or inverse problem optimization, followed by high-precision eigenvalue computation.

**1.5 Coefficients of Characteristic Polynomials of Random Alternating Sign Matrices (ASMs)**
*   **What to measure:** For the characteristic polynomial `det(xI - A)` of large random ASMs, compute M4/M2² of the distribution of a mid-range coefficient (normalized by its variance).
*   **Data:** Large ensembles of random ASMs (n > 50).
*   **Expected constant:** ~1.8-2.0. ASMs are highly constrained, deterministic objects with proven connections to the six-vertex model and alternating sign polytopes. Their linear statistics might exhibit moments in the "combinatorial symmetry" range near SU(2)/Knots.
*   **Why harder:** Uniform random sampling of large ASMs is non-trivial. The coefficients of the characteristic polynomial are subtle linear statistics on the eigenvalue distribution.

### **Category 2: Testing the Unit-Circle Hypothesis**
These test if the M4/M2² ~2.0 signature is tied to roots/evaluations on the unit circle.

**2.1 Mahler Measures of Alexander Polynomials of Hyperbolic Knots**
*   **What to measure:** For hyperbolic knots, compute the Mahler measure `M(Δ(t)) = exp(∫_0^1 log|Δ(e^{2πiθ})| dθ)` of the Alexander polynomial. Measure M4/M2² of the distribution of `log(M(Δ))`.
*   **Data:** Knot Atlas (hyperbolic knots with known Alexander polynomials).
*   **Expected constant:** If the hypothesis holds, this should be **far from 2.0** (likely >3.0). The Mahler measure integrates over the unit circle, effectively "washing out" the phase-specific constraint that gave the 2.0 signal for the determinant.
*   **Why harder:** Tests the inverse of the hypothesis. Requires precise integration of singular functions (Alexander polys can have zeros on the circle) and a clear theoretical prediction of deviation.

**2.2 Roots of Jones Polynomials at Roots of Unity q ≠ ±1**
*   **What to measure:** Evaluate the Jones polynomial `V_K(t)` at a fixed complex root of unity `t = ζ_n` (e.g., n=5). Compute M4/M2² of the distribution of `|V_K(ζ_n)|` across prime knots.
*   **Data:** Knot tables with Jones polynomials.
*   **Expected constant:** Should **move away from 3.93**. The value 3.93 was for the evaluation at `t=i` (a 4th root of unity). Evaluating at other roots of unity (e.g., 3rd, 5th) probes different points *on* the unit circle. The moment may vary systematically with `n`, revealing a "unit circle profile".
*   **Why harder:** Requires computing Jones polynomials at complex points for large datasets and interpreting the variation in the moment hierarchy along the circle.

**2.3 Character Values of Symmetric Group S_n at Fixed Cycle Type**
*   **What to measure:** For the symmetric group `S_n`, take the irreducible character `χ^λ(σ)` where `σ` is a fixed conjugacy class (e.g., a single n-cycle). Measure M4/M2² of the distribution of these character values across partitions `λ ⊢ n` for large `n`.
*   **Expected constant:** Should be **near 2.0**. The character value for an n-cycle is given by the Frobenius formula and is deeply related to evaluation of symmetric functions on the unit circle. This is a pure algebraic combinatorics analog of the SU(2) trace.
*   **Why harder:** Connects the knot/SU(2) phenomenon directly to representation theory of finite groups. Requires handling large character tables and seeing the 2.0 signature emerge asymptotically.

**2.4 Spectral Radius of Non-Unitary Random Quantum Circuits**
*   **What to measure:** Construct random quantum circuits with gates drawn from a distribution *biased away* from the Haar measure on U(2) (e.g., gates with determinant ≠ 1). Compute M4/M2² of the distribution of the spectral radius of the resulting `n`-qubit transfer matrix.
*   **Data:** Numerically generated ensembles of non-unitary circuits.
*   **Expected constant:** Should **increase above 2.0** as the bias pushes eigenvalues off the unit circle. This is a direct *controlled test* of the hypothesis: break the unit-circle constraint and watch the moment hierarchy index rise.
*   **Why harder:** Requires defining a meaningful "bias" parameter away from unitarity and cleanly isolating its effect on the spectral moment.

**2.5 Values of Littlewood Polynomials on the Unit Circle**
*   **What to measure:** Littlewood polynomials have coefficients ±1. For a fixed `θ`, compute `P(e^{iθ})`. Measure M4/M2² of the distribution of the real part `Re(P(e^{iθ}))` across all Littlewood polynomials of a fixed, high degree.
*   **Data:** Exhaustive or random sampling of Littlewood polynomials (degree ~30-40).
*   **Expected constant:** Should be **close to 2.0 for most `θ`**, but may spike for special angles (like θ=0). This tests if the ±1 coefficient constraint, combined with unit-circle evaluation, is sufficient to generate the "algebraic symmetry" moment.
*   **Why harder:** Exhaustive enumeration is exponentially hard. The result could show that the 2.0 moment is robust across a wide class of constrained polynomials evaluated on the circle.

### **Category 3: Exploiting Enrichment in New Domains**
These apply the "enrichment" concept (e.g., 52.6x for electron config) to new, complex datasets.

**3.1 Phonon Density of States → Superconducting Tc (SG→Tc 1.7x)**
*   **What to measure:** Re-examine the "SG→Tc 1.7x" enrichment. Instead of just space group (SG), use the *full phonon density of states (DOS)* from the Materials Project as the source. Train a model to predict Tc from phonon DOS vs. from chemical formula alone.
*   **Data:** Materials Project phonon calculations (where available) + superconductors database.
*   **Expected constant:** Expect enrichment **>> 1.7x**. The phonon DOS is the direct physical input for BCS theory. If space group (a crude proxy for structure) gives 1.7x, the full DOS should yield dramatically higher predictive enrichment.
*   **Why harder:** Requires processing large, complex spectral data (phonon DOS) and building a robust cross-modal prediction benchmark. A null result would be profound.

**3.2 Galois Group → Class Number (3.68x) in Relative Extensions**
*   **What to measure:** Extend the Galois→class number enrichment. For a fixed base field `K` (e.g., Q(√-5)), consider all relative quadratic extensions `L/K`. Measure the enrichment in predicting the *relative class number* `h_L/h_K` from the Galois group `Gal(L/K)` (trivial C2) vs. from the discriminant of `L/K` alone.
*   **Data:** LMFDB relative extensions (or compute them).
*   **Expected constant:** The enrichment may **differ significantly from 3.68x**. This tests if the enrichment factor is universal or depends on the base field's arithmetic, probing the boundary of the "algebraic DNA" concept.
*   **Why harder:** Requires working with relative extensions, where class numbers and discriminants have more complex relationships.

**3.3 Knot Genus → Volume (New Domain)**
*   **What to measure:** For hyperbolic knots, measure the enrichment in predicting the hyperbolic volume from the knot genus vs. predicting it from the determinant alone.
*   **Data:** Knot tables with hyperbolic volume, genus, and determinant.
*   **Expected constant:** Expect **significant enrichment (> 2x)**. Genus is a topological invariant deeply connected to volume via minimal surfaces (Dehn filling bounds). Determinant is more algebraic. This tests if the enrichment principle holds for topological/geometric relationships.
*   **Why harder:** Volume is a continuous real number, requiring regression metrics rather than classification accuracy. Must carefully define the "enrichment" measure for a continuous target.

**3.4 Crystalline Point Group → Band Gap (SG→band gap NULL)**
*   **What to measure:** Re-investigate the "NULL" enrichment from space group to band gap. Instead of full SG, use just the *point group* of the crystal. Train a model to predict if a material is an insulator (band gap > 0) from its point group symmetry vs. from its elemental composition.
*   **Data:** Materials Project band structures.
*   **Expected constant:** Might find **positive enrichment (1.5-2x)**. The NULL result for full SG might be due to translational symmetry being irrelevant. Point group symmetry directly constrains band degeneracies, which is more fundamental for gap formation.
*   **Why harder:** Requires mapping space groups to point groups and framing a clear binary classification problem (metal vs. insulator). Aims to recover a physical signal from a previously null result.

**3.5 Modular Form Level → Fourier Coefficient Growth (Lean namespace 3.71x)**
*   **What to measure:** Inspired by the "Lean namespace" enrichment (a measure of mathematical structure complexity). For modular forms in LMFDB, measure enrichment in predicting the *bound* on Fourier coefficient growth (Ramanujan-Petersson) from the level `N` vs. from the weight `k` alone.
*   **Data:** LMFDB modular forms.
*   **Expected constant:** Could be **high (> 3x)**. The level `N` encodes intricate arithmetic data (conductor, ramification) crucial for coefficient bounds, while weight `k` gives a simpler analytic bound. This translates the "formal complexity" idea to a concrete number theory setting.
*   **Why harder:** Requires precise definition of the "prediction" task (maybe classifying into growth rate categories) and handling the discrete, arithmetic nature of the data.

### **Category 4: Probing the Curvature Boundary**
These investigate the discovered positive arithmetic curvature (+0.73) vs. negative curvature elsewhere.

**4.1 Curvature of the "Zeta Zero Repulsion" Function**
*   **What to measure:** For the Riemann zeta function, define a function `f(s)` on the critical line based on local zero repulsion: e.g., `f(1/2 + iT) = (γ_{n+1} - γ_n) / average gap`, where `γ_n` is the n-th zero. Compute the numerical curvature (second derivative) of the running mean of `f(s)` as a function of `T`.
*   **Data:** High zeros of the Riemann zeta function.
*   **Expected constant:** Should be **negative**. Zero repulsion is a local, chaotic statistic. Following the pattern (knots -0.37, crystals -0.70), this chaotic number-theoretic statistic should also exhibit negative curvature.
*   **Why harder:** Requires computing and smoothing a delicate statistic from zero data, then reliably estimating its second derivative—a noise-amplifying process.

**4.2 Curvature in the Distribution of Fundamental Discriminants**
*   **What to measure:** Consider the set of fundamental discriminants `{D}`. Plot the count of fields with `|D| < X` against `X`. Fit the function `N(X) = c*X + a*X^b`. Measure the curvature in the *residuals* of this fit, or the sign of the `b` parameter if `b ≠ 1`.
*   **Data:** LMFDB quadratic number fields (or real quadratic fields).
*   **Expected constant:** Should show **positive curvature** in the residuals. The asymptotic law is linear, but secondary terms (from Siegel zeros, etc.) introduce subtle deviations. The "arithmetic +0.73" result suggests these deviations are structured and convex.
*   **Why harder:** Isolating the secondary term in asymptotic counting is a classic hard problem in analytic number theory. Requires very high `X` and careful statistical modeling.

**4.3 Spectral Curvature of Amorphous Materials vs. Crystals**
*   **What to measure:** For a large set of *amorphous* materials (from molecular dynamics simulations), compute the electronic density of states (DOS). For each DOS, compute a "spectral curvature" metric (e.g., related to the second derivative of the integrated DOS). Compare the distribution of this curvature to that of crystalline materials.
*   **Data:** Needs a database of amorphous material spectra (could be generated).
*   **Expected constant:** Amorphous curvature should be **less negative or even positive** compared to crystals (-0.24 to -0.70). Lack of long-range order removes the sharp Van Hove singularities that contribute to negative curvature in crystals.
*   **Why harder:** Requires generating or accessing a consistent database of amorphous material properties, which is less standardized than the Materials Project.

**4.4 Curvature of the Jones Polynomial Coefficient Trajectory**
*   **What to measure:** For a knot, treat its Jones polynomial coefficients as a sequence `[c_{-d}, ..., c_{d}]`. Fit a low-degree polynomial to this sequence (or its absolute values). Compute the average second derivative (curvature) of this fit across all prime knots of a fixed crossing number.
*   **Data:** Knot tables with Jones polynomials.
*   **Expected constant:** Should be **negative** (aligning with knots -0.37). The coefficient sequences for alternating knots are log-concave (negative curvature), and this property may persist on average.
*   **Why harder:** Requires defining a robust way to fit a continuous curve to a short, discrete, symmetric sequence and extracting a curvature metric that is comparable across knots.

**4.5 Curvature in the Prime Number Theorem "Error"**
*   **What to measure:** Plot the prime counting function error `E(T) = |π(T) - li(T)| / (T^{1/2} / log T)` for large `T`. Analyze the local curvature of the `log(E(T))` vs. `log(T)` plot.
*   **Data:** Prime counts up to very high `T` (e.g., 10^24).
*   **Expected constant:** Likely **negative**. The oscillations from zeta zeros should create a locally concave-down error envelope. This would place the "error term" of the most fundamental arithmetic object on the negative curvature side, contrasting with the positive curvature of discriminant counts.
*   **Why harder:** Requires extremely high-precision prime counts and logarithmic derivative analysis to distinguish subtle trends from oscillatory noise.
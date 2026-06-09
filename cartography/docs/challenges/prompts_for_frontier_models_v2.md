# Prompts for Frontier Models — Copy/Paste Ready
## Generate computational math/physics/science problems for the Charon instrument
## Updated: 2026-04-11 (post-342 challenges, new science data)

---

## INSTRUCTIONS: Copy the prompt below into ChatGPT, Gemini, DeepSeek, Claude, or Grok. Each model will generate 20 calibrated problems. Save the responses and bring them back to solve.

---

## THE PROMPT:

Generate 20 computational math/physics/science problems for an automated mathematical instrument that has completed 342 challenges and produced 232+ result files across 21 mathematical databases and 8+ scientific databases.

**What the instrument solves quickly (seconds to minutes):**
- Mod-p fingerprint comparison across 394K OEIS sequences, 133K modular forms, 66K genus-2 curves, 13K knots, 39K lattices
- Berlekamp-Massey recurrence detection on integer sequences (order 2-12)
- Sato-Tate group classification via 20-dim moment vectors (98.3% accuracy on 65,855 genus-2 curves)
- Galois image classification from trace density into 9 classes (96.6% CM accuracy, 0 false positives)
- CM detection from zero-frequency of Fourier coefficients (F1=1.00, 29-point gap)
- Congruence graph construction and spectral analysis across GL_2, GSp_4, GSp_6
- Ollivier-Ricci curvature flow to separate accidental from structural congruences (kappa*=0.73)
- Frobenius eigenvalue phase extraction and coherence measurement
- Moment chain measurement: M4/M2^2, M6/M2^3, M8/M2^4 across any distribution
- Function call graph extraction from C source code (9,393 files, 73K edges)
- SageMath point-counting on genus-3 plane quartics via WSL
- 14-test falsification battery (permutation null, subset stability, effect size, confound sweep, normalization sensitivity, base rate, dose-response, direction consistency, simpler explanation, outlier sensitivity, cross-validation, partial correlation, growth rate, phase shift)
- Statistical distribution fitting (Weibull, log-normal, power law, GOE/GUE)
- Enrichment measurement within algebraic families (mod-p fingerprint similarity)
- ANOVA / eta-squared for categorical grouping variables
- Spearman/Pearson correlation with full battery validation

**Measured constants (150+ verified, stable). Key examples:**
- Enrichment (detrended): ~8x constant across primes for algebraic families. Slope = 0.044*(endo_rank^2) - 0.242
- Moment chain (Catalan numbers): U(1)->1.5, SU(2)->2.0 (EC+MF+Maass), USp(4)->3.0. M6/M2^3=5.14, M8/M2^4=14.66
- Phase coherence: rho=-0.193 (Maass) matches rho=0.197 (EC) at 98% effect size — universal across automorphic forms
- Critical prime phase transition: ell_c scales with group rank. GL_2~6, GSp_4~2.5, GSp_6<2. Super-exponential collapse
- 3-prime reconstruction: mod-3 ∩ mod-5 ∩ mod-7 = complete singleton rigidity for all 17,314 weight-2 newforms
- Gamma metric: 0 triangle inequality violations / 13,800 triples. Geodesic hub through pi/elliptic/AGM
- Maass Lyapunov: lambda=-3.035 (3x more contracting than EC at -1.155)
- Maass BM recurrence: 0.0% (spectrum: Maass 0.0% < EC 0.1% < OEIS 19.8%)
- Maass spectral-coefficient repulsion: d=-0.39, p=2e-95 (NOVEL — adjacent forms anti-correlate in coefficient space)
- Maass enrichment GROWS with prime: 2x(p=3) to 8x(p=11). Different from EC flat ~12x
- Curvature sign: +0.73 (genus-2 Hecke), -0.37 (knot Jones), +0.12 (crystals). Sign distinguishes domains
- Crystal enrichment by space group: 1.70x, eta^2=0.45 (space group explains 44.8% of Tc variance)
- Superconductor Tc complexity: r=0.515 with number of elements (monotonic dose-response, no plateau)
- Superconductor Tc: log-normal, NOT Weibull (different universality class from band gaps)
- Band gap: 85.7% Weibull universality collapse across crystal systems
- FLINT modularity: Q=0.628, clique power law alpha=3.28
- Lean proof manifold dimension: 3.14, compressibility zeta=0.029

**23 rediscoveries (calibration — instrument correctly measures known math):**
Modularity theorem (z=72), Sato-Tate (M2=0.2497), Deuring mass (z=93), CM from behavior (F1=1.00), CRT independence (0/29,043 overlap), Atkin-Lehner (perfect binary), BSD parity (100%), Hasse-Weil (0 violations), Heegner primes, sieve=2D structure (0.970), Galois 9-class, ST genus-2 (98.3%), paramodular (7/7 bijection), Euler relation for polytopes (z=33), class numbers differ by field degree (z=66), plus 8 more

**15 novel discoveries (genuinely new, no prior prediction):**
1. Phase coherence-rank correlation (rho=0.197) — local Frobenius sees global L-function
2. Algebraic DNA enrichment law (~8x after detrending, constant across primes)
3. Enrichment slope = endomorphism rank detector (R^2=0.776)
4. Gamma pseudometric on formula space (0 triangle violations)
5. 3-prime adelic reconstruction (788x collapse, complete rigidity)
6. log2(p) bottleneck in generating function evaluation
7. Mod-2 clique decomposition (alpha=3.19, all components complete)
8. Near-congruence = CM splitting (2 components aligned with Q(sqrt(-3)))
9. Curvature flow separator (kappa*=0.73, spherical fixed point)
10. Moonshine breaks flat enrichment (113x for mock theta, grows with prime)
11. Phase coherence generalizes to Maass (rho=-0.193, 98% match)
12. Maass spectral-coefficient repulsion (d=-0.39)
13. Three enrichment regimes: EC flat, Maass grows, genus-2 gated
14. Catalan moment chain holds across all automorphic families tested
15. Sha-Igusa correlation (rho=0.29 in absolute invariants)

**Mathematical datasets (21 operational):**
OEIS (394K), LMFDB EC+MF (133K), genus-2 (66K), Maass (14,995 with 6K coefficients each), lattices (39K theta series), knots (13K), number fields (9K), Fungrim (3K formulas), ANTEDB (244), Metamath (46K), mathlib (8.5K), FindStat (1993), MMLKG (1.4K), isogenies (3.2K), space groups (230), polytopes (1.2K), pi-Base (220), OpenAlex (10K), Hilbert modular forms (368K, pending wire)

**NEW: Science datasets (available for cross-domain measurement):**
- Materials Project: 210,579 crystal structures (band gap, formation energy, space group, density, volume)
- 3DSC Superconductors: 12,448 materials with Tc, crystal system, composition
- COD Crystals: 9,800 structures with cell parameters (a,b,c,alpha,beta,gamma)
- NIST Atomic Spectra: 42,981 energy levels across 99 elements (neutral + ionized)
- Basis Set Exchange: 776 quantum chemistry basis sets
- CODATA 2022: 286 fundamental physical constants
- PDG Particles: 226 particles (masses, widths, branching ratios)
- Planck CMB: TT power spectrum (83 bins, ell=48-2499)
- USGS Earthquakes: seismic events with magnitude, depth
- Logistic map / chaos: bifurcation cascade data
- Ramanujan Machine: integer relation library (73 files)
- FLINT source code: 9,393 C files, 6,474 functions, 73,459 call-graph edges

**The three layers of mathematical structure (instrument's framework):**
- Layer 1 (Scalar): DEAD after prime detrending. 96% was shared primes. No cross-dataset correlation survives.
- Layer 2 (Structural): The sweet spot. Congruences, spectra, fingerprints, enrichment. 150+ measured constants live here.
- Layer 3 (Transformational): The frontier. Twists, lifts, dualities. 193 near-miss candidates. Unsolved general problem.

**Confirmed boundaries (what DOESN'T connect):**
- Arithmetic ↔ topology at scalar level: all null (21+ attempts)
- Arithmetic ↔ physics at scalar level: all null
- Cross-family within arithmetic at scalar level: null (Maass-EC cross-enrichment = 0)
- Mod-p fingerprinting on physical measurements: fails (captures human rounding bias, not physics)
- Any cross-domain coefficient correlation: null after prime detrending

**What DOES connect (genuine bridges):**
- Phase coherence within automorphic families (universal)
- Enrichment within algebraic families (three distinct regimes)
- Moment ratios / Catalan chain (universal across families)
- Curvature sign (distinguishes domains: arithmetic positive, topology negative)
- Space group → physical properties (eta^2=0.45 for Tc)
- Knowledge graph architecture (FLINT/Lean/OEIS share scale-free structure)

**What I need:** 20 problems that are:
1. Concrete and computable (not "prove X" but "measure Y on dataset Z")
2. Beyond current capability (forces building ONE new measurement tool or exploring a new dimension)
3. Each produces a measurable constant (a number with decimal places) if successful
4. At least 3 use the NEW science datasets (Materials Project, superconductors, NIST spectra, earthquakes, basis sets)
5. At least 2 probe Layer 3 (transformation detection, functorial relationships, invariant-preserving maps)
6. At least 2 are within-physics measurements that test whether mathematical universals (moment chains, enrichment, curvature flow) hold in physical domains
7. Span different territories (number theory, topology, physics, chemistry, algorithms, formal proofs)
8. Priority: problems where success reveals a NEW DIMENSION of structure the 150+ existing constants cannot see
9. DO NOT re-propose cross-domain scalar correlations (arithmetic↔topology, arithmetic↔physics) — these are confirmed dead at Layer 1
10. DO NOT propose mod-p analysis on physical measurements — this captures rounding bias, not structure
11. Within-domain structural measurements are the sweet spot

Format each problem as:
- **Title** (one line)
- **What to measure** (specific computation, 3-5 sentences)
- **Data to use** (specific datasets from the lists above)
- **Expected constant** (what number would emerge if successful)
- **Why just beyond** (what new tool or dimension this forces the instrument to build)

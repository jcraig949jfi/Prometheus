# Generated Problems from Claude (self-generated)
# 2026-04-10

## Problem 1: CODATA Constants as OEIS Subsequences
- **What to measure**: For each of the 286 CODATA physical constants, extract digits and test if any contiguous digit subsequence of length 8+ appears in an OEIS sequence. Also test: do ratios of fundamental constants (e.g., m_proton/m_electron = 1836.15...) match any OEIS sequence?
- **What data to use**: `cartography/physics/data/codata/constants.json`, OEIS stripped data
- **What constant would emerge**: The "physical-mathematical overlap rate" — fraction of CODATA constants with OEIS digit matches above random baseline. If > 5%: physics constants carry combinatorial structure.
- **Why just beyond**: Requires building a digit-subsequence matcher (new enrichment axis) and establishing the null rate for random real numbers.

## Problem 2: PDG Particle Mass Ratios as Algebraic Numbers
- **What to measure**: Compute all pairwise mass ratios m_i/m_j for 226 PDG particles. Test each ratio against known algebraic numbers (roots of low-degree polynomials with small coefficients). How many mass ratios are "close" (within experimental uncertainty) to algebraic numbers of degree ≤ 6?
- **What data to use**: `cartography/physics/data/pdg/particles.json`, algebraic number recognition (PSLQ algorithm or LLL lattice reduction)
- **What constant would emerge**: The "algebraic proximity rate" of particle mass ratios. If significantly above random: the universe's mass spectrum has algebraic structure.
- **Why just beyond**: Requires implementing PSLQ/LLL for algebraic number recognition — a new crystal the instrument doesn't have.

## Problem 3: FLINT Function Call Graph as Operadic Skeleton
- **What to measure**: Parse the FLINT source (9,393 C files) to extract the function call graph. Each function is a node; each call is a directed edge. Compute: degree distribution, clustering coefficient, centrality, and community structure. Compare to the Fungrim operadic distance matrix.
- **What data to use**: `cartography/physics/data/flint_src/src/` (1.25M lines of C), `v2/operadic_dynamics_results.json`
- **What constant would emerge**: The "algorithmic permeability ratio" — within/between module call density, analogous to the 0.813 operadic ratio from C12. If similar: algorithms and formulas share the same modular structure.
- **Why just beyond**: Requires building a C source code parser that extracts function call DAGs — the first step in crystal extraction (Path 1).

## Problem 4: CMB Power Spectrum Berlekamp-Massey
- **What to measure**: Once CMB C_ℓ data is acquired (ℓ=2..2508), treat {C_ℓ} as an integer sequence (after rounding/scaling). Run Berlekamp-Massey to test for linear recurrence. Compute mod-p fingerprints at p=2,3,5,7,11. Compare enrichment to OEIS families.
- **What data to use**: Planck CMB power spectrum (need to acquire), OEIS
- **What constant would emerge**: The "cosmological recurrence order" — if the CMB satisfies a linear recurrence, its characteristic polynomial is a measurable property of the universe's initial conditions.
- **Why just beyond**: Blocked on CMB data acquisition. Once obtained, the BM pipeline is ready.

## Problem 5: Near-Congruence Disagreement Primes as Galois Splitting
- **What to measure**: M14 found that near-congruence disagreement concentrates on primes {37,43,61,79,19,31}. For each disagreement prime p, compute: is p split, inert, or ramified in the CM field Q(√-d) for each relevant CM discriminant d? Does the splitting type predict the disagreement pattern?
- **What data to use**: `v2/near_congruence_results.json`, CM discriminant data from genus-2 curves
- **What constant would emerge**: The "CM splitting prediction rate" — fraction of disagreement primes correctly predicted by splitting behavior. If near 100%: the near-congruence population is fully explained by CM arithmetic.
- **Why just beyond**: Requires computing splitting types in specific CM fields — feasible with SageMath but not yet attempted.

## Problem 6: Spectral Gap of FLINT Function Communities
- **What to measure**: From the FLINT call graph (Problem 3), compute the spectral gap of the graph Laplacian for each module/directory. Correlate with the mathematical "depth" of each module (e.g., basic arithmetic vs. elliptic curve algorithms). Does spectral gap predict mathematical complexity?
- **What data to use**: FLINT source code call graph
- **What constant would emerge**: The "complexity-connectivity exponent" — how spectral gap scales with mathematical depth of the algorithm.
- **Why just beyond**: Requires both call graph extraction (Problem 3) AND a principled definition of "mathematical depth" for each FLINT module.

## Problem 7: Particle Mass Mod-p Fingerprints vs Lattice Determinants
- **What to measure**: Convert 226 PDG particle masses to integers (MeV, rounded). Compute mod-p fingerprints. Compare to the 39,293 lattice determinants at the same primes. Is there enrichment? Do particle masses "look like" lattice determinants in mod-p space?
- **What data to use**: `cartography/physics/data/pdg/particles.json`, `cartography/lmfdb_dump/lat_lattices.json`
- **What constant would emerge**: The "physics-lattice enrichment ratio" at each prime. If > 1: particle masses share mod-p structure with mathematical lattices.
- **Why just beyond**: Requires the cross-domain enrichment pipeline adapted for physics data — a new data type flowing through existing crystals.

## Problem 8: Autocorrelation Structure of the Fine Structure Constant's Digits
- **What to measure**: The fine structure constant α ≈ 1/137.036... has been measured to 12+ digits. Treat its decimal expansion as a sequence. Compute autocorrelation at lags 1-15. Compare to: (a) random digits, (b) known transcendental numbers (π, e), (c) algebraic numbers. Does α's digit sequence have structure?
- **What data to use**: High-precision value of α from CODATA, digit sequences of π, e, √2 for comparison
- **What constant would emerge**: The "fine structure digit entropy" — if below random, α's digits carry structure.
- **Why just beyond**: Requires high-precision digit extraction and comparison to number-theoretic baselines.

## Problem 9: Universal Verb Distribution Across Algorithm Implementations
- **What to measure**: For 50 special functions implemented in FLINT, SciPy, and PARI/GP, extract the operation profile: what fraction of operations are multiply, add, compare, branch, loop? Is the operation profile function-specific or implementation-specific? Do all implementations of Gamma share an operadic signature?
- **What data to use**: FLINT source (local), SciPy source (pip), PARI/GP source (downloadable)
- **What constant would emerge**: The "implementation invariance ratio" — fraction of operadic signature that is preserved across implementations of the same function. If high: the crystal structure IS the function, not the code.
- **Why just beyond**: Requires multi-library parsing and cross-library operadic comparison — the full Path 1 crystal extraction.

## Problem 10: Phase Transition in Knot Polynomial Coefficient Growth
- **What to measure**: For 13K knots, compute the growth rate of Jones polynomial coefficients as a function of crossing number. Is there a critical crossing number where growth transitions from polynomial to exponential? Map the transition with the same precision as the mod-ell phase transition (R5-6).
- **What data to use**: `cartography/knots/data/knots.json`
- **What constant would emerge**: The "topological complexity transition crossing number" — the critical point where knot polynomial coefficients change growth regime.
- **Why just beyond**: Requires extending the growth rate classifier (R5-13) to topological data and measuring the transition with R5-6-level precision.

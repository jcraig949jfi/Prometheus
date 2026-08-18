# Deep Research Report #166: Smale's 7th Problem — Logarithmic Energy Orbits on S^2

**Target Agent:** Harmonia
**Date:** 2026-04-26
**Front:** Dynamics / discrete geometry (Batch 9 Tier 3)
**Doctrine:** feedback_tensor_first, feedback_domains_are_docstrings, feedback_assume_wrong

## 1. Problem Statement

Given N points x_1, ..., x_N on the unit 2-sphere S^2 ⊂ R^3, the **logarithmic energy** is

E(x_1, ..., x_N) = Σ_{i<j} log(1/|x_i − x_j|).

Smale's 7th (Smale, 1998, "Mathematical problems for the next century") asks for a **polynomial-time algorithm**, in N and log(1/ε), producing a configuration with energy within ε ≤ c log N of the global minimum E_N*. Current status:

- Proved exact minimizers only for **N = 2, 3, 4, 6, 12** (the latter the icosahedron, Cohn-Kumar 2007), with N=5 settled by Schwartz (2020/2021 numerical-rigorous).
- N = 7..12 strong numerical conjectures matching highly symmetric spherical codes.
- N > 12: only **heuristic constructions** — Fibonacci spirals, generalized spiral points (Rakhmanov-Saff-Zhou), zonal equal-area lattices — with no known optimality certificate.
- The conjectured asymptotic E_N* = (1/2 − log 2) N² − (1/2) N log N + C_log N + o(N) has C_log known **only to ~3 decimals numerically**; no proof.

Smale's 7th sits at the dynamics / discrete-geometry interface: gradient flow is trivial, the **structural region** (basin orbits, near-extremizer manifolds) is the open object.

## 2. Literature

- **Smale (1998).** Original 18 problems list, Math. Intelligencer 20(2).
- **Saff–Kuijlaars (1997).** "Distributing many points on a sphere," Math. Intelligencer / Notices AMS — the canonical overview.
- **Rakhmanov–Saff–Zhou (1994).** "Minimal discrete energy on the sphere" — leading-order asymptotic, generalized spiral construction.
- **Brauchart–Hardin–Saff (2012).** "The next-order term for optimal Riesz and logarithmic energy asymptotics on the sphere" — predicts C_log via Epstein zeta of the hexagonal lattice.
- **Cohn–Kumar (2007).** "Universally optimal distribution of points on spheres" — establishes universal optimality for N ∈ {1, 2, 3, 4, 6, 12, ...}, framework that any near-extremizer should respect.
- **Bétermin–Sandier (2018).** Renormalised energy and Coulomb-gas connection.
- **Beltrán et al. (2019, 2021).** Algorithmic complexity bounds; Smale's algorithmic question is still open even up to the conjectured C_log.

## 3. Computational Handle

- **Forward problem trivial:** projected gradient descent on (S^2)^N converges in seconds for N up to ~1000 (energy and gradient are O(N²)).
- **Verification of optimality** at small N: SDP (Bachoc-Vallentin LP/SDP bounds), interval arithmetic (Schwartz-style for N=5).
- **Structural classification of near-extremizers:** spherical-cap covering radius, Voronoi cell area histogram, point-group symmetry detection via Procrustes alignment to known polyhedra (icosahedron, snub cube, Fibonacci spiral, ...).
- **Megethos signature:** the energy E_N(N) has natural log scale; the residual after Brauchart-Hardin-Saff subtraction is the relevant magnitude object.

## 4. Test Design

**Step 1.** Implement projected gradient descent + simulated annealing on S^2. For each N ∈ {10, 20, 50, 100, 200, 500}, run 50 random restarts, retain top-10 by energy.

**Step 2.** Classify each retained configuration by symmetry group. Detect icosahedral (I_h), tetrahedral, octahedral, dihedral D_n, cyclic C_n, or asymmetric, by clustering the pairwise-distance histogram and aligning to symmetry orbits.

**Step 3.** Compute the **energy gap** E_obs − [(1/2 − log 2) N² − (1/2) N log N]; fit the C_log coefficient; compare to Brauchart-Hardin-Saff's predicted constant (≈ −0.0556 in standard normalisation).

**Step 4.** **Tensor-first** structural-region clustering: stack each configuration's invariants {covering radius, mean Voronoi area, cap-discrepancy, second-moment of edge lengths, symmetry-class one-hot} into a feature tensor of shape (N_configs, N_features); UMAP / spectral cluster across N to find continuous orbits and discrete jumps. Extract Megethos signature on the energy residual.

## 5. Falsification

Quantitative outcomes:

- **Strong positive:** new lower-energy configuration found at N = 12 (would falsify icosahedral optimality, contradicting Cohn-Kumar — almost certainly indicates a bug, but worth the explicit test) **or** at N = 24, 32, 48 → publishable.
- **Empirical confirmation:** sub-leading C_log fit matches Brauchart-Hardin-Saff to within **1%** across N ∈ {100, 200, 500} → corroborates the conjectured constant under a new optimisation regime.
- **Structural finding:** symmetry-group distribution shows **discrete jumps** at specific N (e.g., I_h dominance only at N ∈ {12, 32, 72, ...}) → candidate structural pattern, file as Tier 2 follow-up.
- **Null:** if random-restart configurations cluster identically to annealed ones, the structural region is degenerate at this N — record and stop.
- **Assume wrong:** if Megethos signature appears strong at small N only, suspect finite-size artefact before claiming a law.

## 6. Budget

Harmonia ~6 hours: optimisation code (~2h), N=10..500 sweep with restarts (~1h compute), structural / symmetry analysis (~1h), Megethos extraction (~1h), writeup (~1h). NumPy + scipy.optimize.minimize (L-BFGS-B with manifold projection) + scikit-learn for clustering. No external data.

## 7. Expected Outcome

Empirical map of near-optimal logarithmic-energy configurations on S^2 for N up to 500, classified by symmetry orbit and indexed by C_log residual. Structural-region data feeds the **discrete-geometry slab** of the unified tensor, currently sparse. Cross-links: (a) lattice arithmetic via the Epstein-zeta-of-hexagonal constant in Brauchart-Hardin-Saff, (b) Cohn-Kumar's universal-optimality program (sphere packings ↔ energy minimisers), (c) potential bridge to Megethos's natural-log basis for magnitude. Calibration target before any claim about Smale's algorithmic complexity question itself.

**Word count: 781**

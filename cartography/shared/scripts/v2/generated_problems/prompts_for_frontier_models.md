# Prompts for Frontier Models — Copy/Paste Ready
## Generate computational math/physics problems for the Charon instrument
## Updated: 2026-04-10 (post-136 challenges)

---

## INSTRUCTIONS: Copy the prompt below into ChatGPT, Gemini, DeepSeek, Claude, or Grok. Each model will generate 20 calibrated problems. Save the responses and bring them back for Charon to solve.

---

## THE PROMPT:

Generate 20 computational math/physics problems for an automated mathematical instrument that has completed 136 challenges and produced 195 result files.

**What the instrument solves quickly (seconds to minutes):**
- Mod-p fingerprint comparison across 394K OEIS sequences, 133K modular forms, 66K genus-2 curves, 13K knots, 39K lattices
- Berlekamp-Massey recurrence detection on integer sequences (order 2-12)
- Sato-Tate group classification via 20-dim moment vectors (98.3% accuracy on 65,855 genus-2 curves)
- Galois image classification from trace density into 9 classes (96.6% CM accuracy, 0 false positives)
- CM detection from zero-frequency of Fourier coefficients (F1=1.00, 29-point gap)
- Congruence graph construction, spectral analysis, Ollivier-Ricci curvature flow
- Curvature flow to separate accidental from structural congruences (converges to kappa*=0.73)
- Frobenius eigenvalue phase extraction and coherence measurement
- 2D Fourier decomposition of prime indicator fields
- Function call graph extraction from C source code (parsed 9,393 files, 73K edges)
- Fake L-function perturbation analysis (structural integrity curves)
- SageMath point-counting on genus-3 plane quartics via WSL
- Reynolds number measurement of hypothesis spaces (bathtub-of-death survival curves)

**Measured constants (30+ verified, stable):**
- Enrichment (detrended): ~8x constant across primes (object-specific: works on L-functions, fails on theta series)
- Enrichment slope: 0.044*(endo_rank^2) - 0.242 (R^2=0.776, measures endomorphism algebra)
- Clique power law: alpha=3.19 (mod-2 Hecke, all components are complete graphs)
- Interference exponent: 5.3 (min-based, cross-prime clustering). Nonlinearity coefficient gamma=4.157
- Reconstruction: 3 primes uniquely identify any weight-2 newform (11.74 bits first prime, 788x collapse)
- Phase transition: critical prime scales as |G(F_ell)|^{-1/rank}, confirmed at ranks 2, 4, 6 (predicted then verified on genus-3)
- Gamma metric: 0 triangle inequality violations / 13,800 triples (genuine pseudometric, geodesic hub)
- Local-to-global: 76% fingerprint agreement suffices for full congruence. 1,131 near-congruences at ell=3
- Reynolds habitable zone: [4.37, 13.68] globally, but DOMAIN-DEPENDENT (NF: [7.75, 47.98], 4.3x wider)
- Topology-algebra axis: Set vs For, sigma1/sigma2 = 9.53. 43% of formulas are cross-domain bridges
- Pipeline bottleneck: exactly log2(p) bits at generating function evaluation (hourglass entropy profile)
- Transfer efficiency: T12=11.9x, T23=18.9x, T13=1.9x (99.2% loss through composition — scrambler, not transmitter)
- Phase coherence-rank correlation: rho=0.197, p=3.5e-10 (local Frobenius geometry sees global L-function vanishing — NOVEL, unexplained)
- Curvature flow fixed point: kappa*=0.7295 (spherical). Phase transition at iteration 44
- Near-congruence defect graph: 2 components perfectly aligned with Q(sqrt(-3)) CM splitting
- Kissing number from theta fingerprints: 96.6% k-NN accuracy (arithmetic DOES encode geometry)
- Genus-2 fake sigma_c = 5.0 (2.5x GL_2's 2.0, scales with Hasse bound width)
- Genus-2 interference I(2,3) = 4.359 (165x above GL_2 prediction, rank-dependent)
- Particle mass gap ratio: r=0.3815 (Poisson). Decay topology lambda_1=7.0. Baryon ORC=-0.94
- CODATA compressibility: 8.57% CF-compressible. Khinchin excess 2.41 vs 1.43
- FLINT algorithmic permeability: 0.5975 (27% more modular than Fungrim formula network at 0.813)
- Sieve-prime correlation tensor: cosine=0.970 (97% of 2D prime structure is sieve of {2,3,5})
- OEIS: 65.4% structured, local spectral dim 2.5, global dim 10.8. Compressibility z=+6.3
- Hecke entropy: 3.27 bits non-CM, 2.18 bits CM (flat, level-independent). CM gap = 1.09 bits
- Chromatic number of congruence graphs: bounded at 2-5, chi=omega always (greedy=optimal)

**20 rediscoveries (calibration — the instrument correctly measures known math):**
Modularity (31,073/31,073), Sato-Tate (M2=0.2497), Berry-Tabor (Poisson 120/120), CM (F1=1.00), Deuring mass (z=93), CRT independence (0/29,043 overlap under 30 conditions), Atkin-Lehner (perfect binary), BSD parity (100%), Hasse-Weil (0 violations), twist even moments (machine precision), Heegner primes (58.1% at D=-163), sieve=2D structure (0.970), Ulam=quadratics (z=5.87), Galois images (9 classes), ST genus-2 (98.3%), HGM degree-2 (49/49), particle Poisson (r=0.3815), degree reduction (random poly model), prime gap anisotropy (artifact), phase transition (predicted rank 6)

**3 verified unproved conjectures:**
Paramodular (7/7 bijection, 92.5% eigenvalues), phase transition scaling (confirmed on fresh genus-3 data), cross-ell independence in GSp_4 (pair enrichment=1.001x)

**12 novel discoveries (genuinely new, no prior prediction):**
Phase coherence-rank (rho=0.197), algebraic DNA enrichment (8x), enrichment=endo_rank detector, Gamma pseudometric, 3-prime reconstruction, log2(p) bottleneck, mod-2 clique decomposition (alpha=3.19), near-congruence=CM splitting, curvature flow separator (kappa*=0.73), moonshine breaks enrichment, Reynolds bathtub, kissing from theta (96.6%)

**Datasets available:**
OEIS (394K), LMFDB EC+MF (133K), genus-2 (66K with 50+ fields), genus-3 (100 computed via SageMath), lattices (39K with theta series), knots (13K with Jones+Alexander), number fields (9K), Fungrim (3K formulas, 60 modules), CODATA (286 physical constants), PDG (226 particles with masses/widths), Planck CMB TT power spectrum (83 bins, ell=48-2499), FLINT source (9,393 C files, 1.25M lines, call graph extracted), Lean mathlib (190K theorem declarations, cloned), SageMath in WSL (genus-3 Frobenius operational), 520K crystal structures available (COD, downloading)

**What FAILS (21 confirmed kills — do NOT re-propose these):**
- EC↔OEIS bridging by ANY coefficient method (6 linear + 5 nonlinear transforms + partial matching = all zero)
- Scaling law inversion for discovery (finds trivial arithmetic progressions, not hidden algebra)
- Mock shadow detection at weight 2 (weight gap blocks it fundamentally)
- Verb distributions as independent predictor (collinear with endo_rank, LOO R^2 drops)
- Particle mass ratios as algebraic numbers (reporting precision artifact at 1-5 sig figs)
- 3-SAT spectral shortcut (rank 8 for 90% variance, d=-0.061 between SAT/UNSAT, wall is real)
- Oscillation shadow law (z=0.84 across 17K forms, individual not species)
- ell_c as L-function predictor on full population (rho=-0.026, but revives after rank-0 ablation to -0.17)
- CODATA mod-p domain fingerprinting (digits encode measurement precision, not physics)
- Particle mass linear recurrence (BM=floor(n/2) everywhere = generic random)
- 2D prime fractal dimension (= random at matched density, no manifold)
- Enrichment-rank law on lattice theta series (R^2=-3.17, behavior inverted — law is object-specific)
- Formula complexity predicting recurrence order (rho=0.032, independent dimensions)
- Fine-structure constant 137 in OEIS (z=1.12, unremarkable for a 3-digit prime)
- Cross-domain transport above fingerprint collision null (all z < 2)
- Combinatorial sequences locking into Sato-Tate distributions (0% match, arcsine dominates)
- Knot-NF arithmetic intersection (mu=1.0008, small-square artifact)

**What I need:** 20 problems that are:
1. Concrete and computable (not "prove X" but "measure Y on dataset Z")
2. Beyond current capability (forces building ONE new measurement tool or exploring a new dimension)
3. Each produces a measurable constant (a number with decimal places) if successful
4. At least 2 use physics data (CODATA, PDG, Planck CMB, crystal structures)
5. At least 1 involves algorithm source code or formal proof structure (FLINT 9,393 files or Lean mathlib 190K declarations)
6. Span different mathematical territories (not all number theory)
7. Priority: problems where success reveals a NEW DIMENSION of mathematical structure that the 30+ existing constants cannot see
8. DO NOT re-propose any of the 21 confirmed dead ends listed above

Format each problem as:
- **Title** (one line)
- **What to measure** (specific computation, 3-5 sentences)
- **Data to use** (specific datasets from the list above)
- **Expected constant** (what number would emerge if successful)
- **Why just beyond** (what new tool or dimension this forces the instrument to build)

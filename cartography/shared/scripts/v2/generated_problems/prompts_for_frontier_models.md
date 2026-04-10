# Prompts for Frontier Models — Copy/Paste Ready
## Generate computational math/physics problems for the Charon instrument
## 2026-04-10

---

## INSTRUCTIONS: Copy the prompt below into ChatGPT, Gemini, DeepSeek, Claude, or Grok. Each model will generate 10 calibrated problems. Save the responses and bring them back for Charon to solve.

---

## THE PROMPT:

Generate 10 computational math/physics problems for an automated instrument.

**What the instrument solves quickly (seconds to minutes):**
- Mod-p fingerprint comparison across 394K OEIS sequences, 133K modular forms, 66K genus-2 curves, 13K knots, 39K lattices
- Berlekamp-Massey recurrence detection on integer sequences (order 2-12)
- Sato-Tate group classification via moment vectors (98.3% accuracy, 20 dimensions)
- Galois image classification from Hecke eigenvalue distributions (9 classes)
- CM detection from zero-frequency of Fourier coefficients (F1=1.00)
- Congruence graph construction and spectral analysis
- Autocorrelation, FFT spectral signatures, Ollivier-Ricci curvature on graphs
- SageMath point-counting on algebraic curves via WSL

**Measured constants (verified, stable):**
- Enrichment slope: 0.044*(endo_rank^2) - 0.242 (algebraic family detection)
- Clique power law: alpha=3.19 (mod-2 Hecke congruence graph)
- Interference exponent: 5.3 (cross-prime clustering, min-based)
- Reconstruction: 3 primes identify any weight-2 newform (11.74 bits first prime)
- Phase transition: critical prime scales as |G(F_ell)|^{-1/rank}, confirmed at ranks 2,4,6
- Gamma metric: 0 triangle inequality violations across 13,800 triples
- Local-to-global: 76% fingerprint agreement suffices for full congruence
- Reynolds number: habitable zone [4.37, 13.68] in z-score units
- Topology-algebra axis: Set vs For, sigma1/sigma2 = 9.53
- Fake L-function critical perturbation: sigma_c = 2.0
- Particle mass gap ratio: r = 0.3815 (Poisson, no hidden operator)
- v2 wall: spectrum exactly {3,2,1}, block-diagonal, spectrally indestructible
- Near-congruence: 95.2% norm_cartan, disagreement at {37,43,61,79,19,31}
- Rosetta axis: Recurrence→Series→Zeta pipeline carries structure when universal vocabulary ablated

**Datasets available:**
OEIS (394K), LMFDB EC+MF (133K), genus-2 (66K), genus-3 (100 computed via SageMath), lattices (39K), knots (13K), number fields (9K), Fungrim (3K formulas), CODATA (286 physical constants), PDG (226 particles), FLINT source (1.25M lines C code, 9393 files), SageMath in WSL, 520K crystal structures available (COD)

**What FAILS (confirmed dead ends):**
- EC↔OEIS bridging by any coefficient method (11 transforms tested, all zero)
- Scaling law inversion for discovery (finds trivial arithmetic)
- Mock shadow detection at weight 2 (weight gap blocks it)
- Verb distributions as independent predictor (collinear with endo_rank)
- Particle mass ratios as algebraic numbers (reporting precision artifact)
- Nonlinear transforms for cross-domain bridges (5 families, all zero)
- 3-SAT spectral shortcut (rank 8 for 90% variance, wall is real)

**What I need:** 10 problems that are:
1. Concrete and computable (not "prove X" but "measure Y on dataset Z")
2. Just beyond current capability (forces building ONE new measurement tool)
3. Each produces a measurable constant (a number with decimal places) if successful
4. At least 2 use physics data (CODATA constants, PDG particles, crystal structures)
5. At least 1 involves algorithm source code analysis (FLINT, 1.25M lines of C)
6. Span different mathematical territories (not all number theory)
7. Priority: problems where success reveals a NEW DIMENSION of mathematical structure that the instrument cannot currently see

Format each problem as:
- **Title** (one line)
- **What to measure** (specific computation, 2-3 sentences)
- **Data to use** (specific datasets from the list above)
- **Expected constant** (what number would emerge if successful)
- **Why just beyond** (what new tool must be built)

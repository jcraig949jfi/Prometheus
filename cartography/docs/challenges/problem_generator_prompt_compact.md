# Generate 10 computational math/physics problems for an automated instrument.

## What the instrument solves quickly (seconds to minutes):
- Mod-p fingerprint comparison across 394K OEIS sequences, 133K modular forms, 66K genus-2 curves, 13K knots, 39K lattices
- Berlekamp-Massey recurrence detection on integer sequences (order 2-12)
- Sato-Tate group classification via moment vectors (98.3% accuracy, 20 dimensions)
- Galois image classification from Hecke eigenvalue distributions (9 classes)
- CM detection from zero-frequency of Fourier coefficients (F1=1.00)
- Congruence graph construction and spectral analysis
- Autocorrelation, FFT spectral signatures, Ollivier-Ricci curvature on graphs
- SageMath point-counting on algebraic curves via WSL

## Measured constants (verified, stable):
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

## Datasets available:
OEIS (394K), LMFDB EC+MF (133K), genus-2 (66K), genus-3 (100 computed), lattices (39K), knots (13K), number fields (9K), Fungrim (3K formulas), CODATA (286 physical constants), PDG (226 particles), FLINT source (1.25M lines C code), SageMath in WSL

## What FAILS (confirmed dead ends):
- EC<->OEIS bridging by any coefficient method (11 transforms tested, all zero)
- Scaling law inversion for discovery (finds trivial arithmetic)
- Mock shadow detection at weight 2 (weight gap)
- Verb distributions as independent predictor (collinear with endo_rank)

## What I need: 10 problems that are:
1. Concrete and computable (not "prove X" but "measure Y on dataset Z")
2. Just beyond current capability (forces building ONE new measurement tool)
3. Each produces a measurable constant if successful
4. At least 2 use physics data (CODATA, PDG)
5. At least 1 involves algorithm source code analysis
6. Span different mathematical territories
7. Priority: problems where success reveals a NEW DIMENSION of structure

Format: Title / What to measure / Data to use / Expected constant / Why just beyond

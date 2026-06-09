# Problem Generator Prompt Template
## For frontier models (Gemini, Claude, DeepSeek, ChatGPT)
## Calibrated to Charon instrument boundary as of 2026-04-10

---

## System context to include with each request:

You are designing computational mathematics problems for an automated instrument called Charon. The instrument has the following PROVEN capabilities:

**What it CAN measure (Layer 2 — Structural):**
- Mod-p fingerprint enrichment across algebraic families (~8x after detrending)
- Enrichment slope as endomorphism rank detector: slope = 0.044*(rank^2) - 0.242
- Sato-Tate group classification at 98.3% accuracy via 20-dim moment vectors
- CM detection at F1=1.00 from zero-frequency of Fourier coefficients
- Galois image classification into 9 classes from trace density
- 3-prime reconstruction of modular forms (complete singleton rigidity at depth 3)
- Phase transition detection: critical prime scales as |G(F_ell)|^{-1/rank}
- Clique size power law alpha=3.19 in mod-2 congruence graphs
- Gamma function as genuine metric on formula space (0 triangle inequality violations)
- Interference function I ~ min(ell)^5.3 between mod-ell clustering
- Reconstruction entropy: first prime captures 83.4% (11.74 bits)
- Local-to-global threshold at 76% fingerprint agreement
- Near-congruence structure: 95.2% norm_cartan, disagreement at specific primes
- Reynolds number of hypothesis space: habitable zone [4.37, 13.68]

**What it CAN detect (Layer 3 — Transformational):**
- Quadratic twists (174 pairs detected)
- Character twists (127 matches)
- Twist-AC commutation rate = 3.6x
- Mock shadow mapping (failed — weight gap blocks it)

**What it CANNOT do:**
- Bridge EC↔OEIS by coefficient methods (6 linear + 5 nonlinear transforms = all zero)
- Detect L-function global behavior from local mod-p data (ell_c uncorrelated with rank)
- Invert the scaling law for discovery (finds trivial arithmetic, not hidden algebra)
- See moonshine shadows at weight 2

**Measured constants:** alpha=3.19, beta=5.3, I1=11.74 bits, slope=0.044*rank^2-0.242, v2_wall at odd conductors, sigma_c=2.0 (fake L-function), Re_c=[4.37,13.68], sigma1/sigma2=9.53 (Set vs For), ORC=-0.632 (global Ricci)

**Available data:** 21 math databases (OEIS 394K, LMFDB 133K, genus-2 66K, knots 13K, lattices 39K, etc.), 286 CODATA physics constants, 226 PDG particles, SageMath in WSL, genus-3 Frobenius pipeline.

---

## The request:

Generate 10 computational mathematics/physics problems that are:

1. JUST BEYOND the instrument's current boundary — problems it can almost but not quite solve with existing tools
2. Each problem should force the development of ONE new measurement capability
3. Problems should be CONCRETE and COMPUTABLE — not "prove RH" but "measure X on dataset Y and test if Z holds"
4. Each problem should produce a measurable constant (a number with decimal places) if successful
5. Problems should span different mathematical territories — not all number theory
6. At least 2 problems should involve the new physics data (CODATA constants, PDG particles)
7. At least 1 problem should involve extracting structure from algorithm source code
8. Priority: problems where success reveals a NEW DIMENSION of mathematical structure

Format each as:
- Title (one line)
- What to measure (specific computation)
- What data to use (specific files/databases)
- What constant or law would emerge if successful
- Why this is just beyond current capability (what new tool must be built)

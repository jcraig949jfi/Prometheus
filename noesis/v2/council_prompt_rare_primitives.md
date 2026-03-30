# Council Prompt: Derivation Chains for Rare Transformation Primitives

## Context

We have established an 11-primitive basis for mathematical transformations and verified it across 20 derivation chains (152 computational tests, 150 pass). The primitives are:

```
COMPOSE, MAP, EXTEND, REDUCE, LIMIT, DUALIZE,
LINEARIZE, STOCHASTICIZE, SYMMETRIZE, BREAK_SYMMETRY, COMPLETE
```

However, our 20 verified chains are biased toward "building up" transformations — physics to math, concrete to abstract. MAP and REDUCE dominate at 33% and 10% of edges. Five primitives are underrepresented or absent from our chain library:

| Primitive | Current Edge Count | What It Does |
|-----------|-------------------|-------------|
| DUALIZE | 0 | Involutive correspondence (Fourier, Legendre, Pontryagin, EM duality) |
| LINEARIZE | 0 | Local approximation (Taylor, Jacobian, tangent space, perturbation theory) |
| SYMMETRIZE | 0 | Impose invariance (group averaging, gauge fixing, symmetrization operators) |
| BREAK_SYMMETRY | 0 | Reduce symmetry group (phase transitions, Higgs mechanism, bifurcation) |
| STOCHASTICIZE | 0 | Introduce randomness (Brownian motion from deterministic, quantum from classical) |

## What We Need

**20 derivation chains where the DOMINANT transformation is one of the five rare primitives listed above.** At least 4 chains per rare primitive.

Do NOT give us chains dominated by MAP, EXTEND, or REDUCE — we have those. We specifically need chains that exercise the structural moves we're missing.

## Format (must match exactly)

For each chain:

```
CHAIN [N]: [Name]
DOMINANT PRIMITIVE: [which of the 5 rare ones]

Step 1: [Equation/principle]
  ↓ via [transformation name] (type: [PRIMITIVE_TYPE])
Step 2: [Equation/principle]
  ↓ via [transformation name] (type: [PRIMITIVE_TYPE])
Step 3: [Equation/principle]
  ↓ via [transformation name] (type: [PRIMITIVE_TYPE])
Step 4: [Equation/principle]

Invariant preserved through chain: [what survives]
Structure destroyed: [what's lost]
What breaks if you remove the dominant step: [consequence]
```

## Specific Chains We Want (suggestions — you may substitute better ones)

### DUALIZE chains (at least 4):
- Fourier transform chain: time-domain signal processing → frequency-domain filtering → inverse transform
- Legendre transform: Lagrangian ↔ Hamiltonian (this IS duality, not just MAP)
- Pontryagin duality: locally compact abelian group → character group → double dual
- Electromagnetic duality: E/B fields under source-free Maxwell
- Projective duality: points ↔ hyperplanes in projective geometry
- Laplace transform chain: ODE solving via transform → algebraic manipulation → inverse

### LINEARIZE chains (at least 4):
- Perturbation theory: exact → perturbed → series expansion → truncation
- Tangent space approximation: manifold → local coordinates → linear algebra
- WKB approximation: Schrödinger → eikonal → ray optics
- Jacobian linearization of dynamical systems: nonlinear system → fixed point → stability analysis
- Born approximation in scattering theory

### SYMMETRIZE chains (at least 4):
- Gauge theory construction: global symmetry → local gauge → gauge field emerges
- Symmetrization of wave functions: product state → symmetric/antisymmetric (bosons/fermions)
- Reynolds averaging: turbulent flow → mean flow + fluctuations
- Burnside/Polya counting: objects → orbits under group action
- Weyl character formula: representation → character (invariant under conjugation)

### BREAK_SYMMETRY chains (at least 4):
- Higgs mechanism: SU(2)×U(1) → U(1)_EM + massive W/Z
- Landau phase transition: high-symmetry → ordered phase → order parameter
- Pitchfork bifurcation: Z₂ symmetric system → symmetry-broken branches
- Spontaneous magnetization: SO(3) → SO(2)
- Crystal formation: continuous rotation → discrete lattice symmetry

### STOCHASTICIZE chains (at least 4):
- Langevin equation: deterministic dynamics → add noise → stochastic process
- Path integral: classical action → sum over all paths → quantum amplitude
- Boltzmann machine: deterministic energy → thermal fluctuations → sampling
- Stochastic calculus: ODE → SDE (Itô/Stratonovich)
- Markov chain Monte Carlo: deterministic optimization → random walk → ergodic sampling

## Precision Requirements

- Include the actual equations (LaTeX notation fine)
- For each transformation step, be precise enough that we can verify in SymPy
- Label each transformation with its primitive type from our ontology
- Don't relabel MAP or REDUCE as rare primitives — if a step is really MAP, call it MAP even in a DUALIZE-dominant chain
- If you're uncertain about a primitive classification, say so

## Output

Give us raw material, not curated highlights. We will verify everything computationally. Err on precision over elegance.

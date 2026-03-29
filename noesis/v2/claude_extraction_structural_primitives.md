# Claude Extraction: Structural Primitives and Equation Lineage

*Extracted 2026-03-29. Every claim here should be independently verified via SymPy, Lean mathlib, or textbook reference before entering the tensor.*

---

## 1. The Noether Tree (Symmetry → Conservation)

### Continuous Spacetime Symmetries (Poincaré Group)

| Symmetry | Group | Conservation Law | Manifests In | Noether Current |
|----------|-------|-----------------|--------------|-----------------|
| Time translation | R (additive) | Energy | Hamiltonian mechanics, Schrödinger eq | T^{0μ} (stress-energy tensor, time component) |
| Spatial translation | R³ (additive) | Linear momentum | Newton's laws, field theory | T^{iμ} (stress-energy tensor, spatial components) |
| Spatial rotation | SO(3) | Angular momentum | Central force problems, spin | M^{ij,μ} = x^i T^{jμ} - x^j T^{iμ} |
| Lorentz boost | SO(3,1) | Center-of-mass motion | Relativistic mechanics | M^{0i,μ} (boost generators) |

**Derivation pathway (verifiable):**
1. Start with Lagrangian L(q, q̇, t)
2. Apply infinitesimal transformation: q → q + ε·δq
3. If δL = 0 (or δL = dF/dt for a total derivative), then
4. J = (∂L/∂q̇)·δq - F is conserved (dJ/dt = 0)

### Gauge Symmetries (Internal)

| Symmetry | Group | Conservation Law | Physical Theory | Gauge Boson |
|----------|-------|-----------------|-----------------|-------------|
| Phase rotation of ψ | U(1) | Electric charge | QED (Maxwell + Dirac) | Photon (A_μ) |
| Isospin rotation | SU(2) | Weak isospin | Electroweak theory | W±, Z⁰ |
| Color rotation | SU(3) | Color charge | QCD | 8 gluons |
| Combined electroweak | SU(2)×U(1) | Weak hypercharge | Standard Model | W±, Z⁰, γ |

**Key structural fact:** Gauge symmetries are LOCAL (transformation parameter depends on spacetime position). This is structurally different from global symmetries. The requirement of local invariance FORCES the existence of gauge fields (connection on a principal bundle). This is derivable — the gauge boson emerges from the mathematics, not postulated.

**Derivation chain (U(1) → QED):**
1. Free Dirac Lagrangian: L = ψ̄(iγ^μ ∂_μ - m)ψ
2. Demand local U(1) invariance: ψ → e^{iα(x)}ψ
3. ∂_μ ψ picks up extra term → fails invariance
4. Replace ∂_μ with D_μ = ∂_μ + ieA_μ (covariant derivative)
5. A_μ transforms as: A_μ → A_μ - (1/e)∂_μ α
6. Add kinetic term for A_μ: -(1/4)F_{μν}F^{μν}
7. Result: Full QED Lagrangian. Maxwell's equations emerge as equations of motion for A_μ.

**What breaks if you remove local invariance:** You can still have a free Dirac field, but no photon, no electromagnetic interaction. The entire structure of light and electromagnetism vanishes.

### Discrete Symmetries

| Symmetry | Operation | What's Conserved | Status |
|----------|-----------|-----------------|--------|
| Charge conjugation (C) | particle ↔ antiparticle | C-parity (for eigenstates) | Violated by weak interaction |
| Parity (P) | spatial inversion x → -x | P-parity | Violated by weak interaction (Wu experiment 1957) |
| Time reversal (T) | t → -t | T-parity | Violated in K⁰ system |
| CPT combined | all three | CPT is exact | Required by any Lorentz-invariant local QFT (CPT theorem) |

**Structural fact:** CPT invariance is not optional — it's a theorem derivable from Lorentz invariance + locality + unitarity. Breaking CPT requires breaking one of those three.

### Less Famous Symmetries

| Symmetry | Conservation | Where |
|----------|-------------|-------|
| Scale invariance (conformal) | Trace of stress-energy = 0 | Conformal field theories, critical phenomena |
| Conformal group SO(d+1,1) | Conformal charge | 2D CFT (Virasoro algebra) |
| Supersymmetry Q | Supercharge | SUSY theories (unobserved in nature as of 2025) |
| Diffeomorphism invariance | Bianchi identity → ∇_μ G^{μν} = 0 | General Relativity |
| Chiral symmetry U(1)_A | (Anomalously broken) → π⁰ → γγ | QCD, axial anomaly |
| Baryon number U(1)_B | Baryon number | Standard Model (approximate, violated by sphalerons) |
| Lepton number U(1)_L | Lepton number | Standard Model (approximate) |

---

## 2. Equation Derivation Chains

### Chain 1: Principle of Least Action → Euler-Lagrange → Newton → Kepler

```
Step 1: Principle of Least Action — δS = 0 where S = ∫L dt
  ↓ via: calculus of variations (functional derivative = 0)
Step 2: Euler-Lagrange equation — d/dt(∂L/∂q̇) - ∂L/∂q = 0
  ↓ via: substitute L = T - V = ½mv² - V(x), compute derivatives
Step 3: Newton's Second Law — F = ma (i.e., m·ẍ = -dV/dx)
  ↓ via: substitute V = -GMm/r (gravitational potential)
Step 4: Kepler's Laws — elliptical orbits, equal areas, T² ∝ a³

What breaks if you remove Step 2: No systematic way to derive equations of motion from symmetries. Noether's theorem becomes inaccessible. Each force law must be postulated independently.
Preserved through chain: Energy conservation (from time-translation symmetry of L)
Destroyed: Generality — each step specializes to a narrower class of systems
```

### Chain 2: Hamiltonian → Poisson Brackets → Commutators → Schrödinger

```
Step 1: Hamilton's equations — q̇ = ∂H/∂p, ṗ = -∂H/∂q
  ↓ via: define Poisson bracket {f,g} = Σ(∂f/∂q·∂g/∂p - ∂f/∂p·∂g/∂q)
Step 2: Poisson bracket formulation — df/dt = {f, H} + ∂f/∂t
  ↓ via: canonical quantization — replace {,} → (1/iℏ)[,] (commutator)
Step 3: Heisenberg equation — dÂ/dt = (1/iℏ)[Â, Ĥ] + ∂Â/∂t
  ↓ via: switch to Schrödinger picture (operators fixed, states evolve)
Step 4: Schrödinger equation — iℏ ∂ψ/∂t = Ĥψ

What breaks if you remove Step 2: Quantization has no systematic procedure. You'd have to guess the quantum theory for each system independently.
Preserved: Hamiltonian structure (energy as generator of time evolution)
Destroyed: Commutativity of observables (the key structural change in quantization)
```

### Chain 3: Statistical Mechanics → Thermodynamics → Information Theory

```
Step 1: Boltzmann distribution — P(state) = exp(-E/kT) / Z, where Z = Σ exp(-E/kT)
  ↓ via: define entropy S = -k Σ P_i ln P_i (Gibbs entropy)
Step 2: Thermodynamic entropy — S = k ln Ω (Boltzmann), dS = δQ/T (Clausius)
  ↓ via: abstract away physical system, keep probability distribution
Step 3: Shannon entropy — H = -Σ p_i log₂ p_i
  ↓ via: identify information gain with free energy (Landauer's principle)
Step 4: Landauer's principle — Erasing 1 bit costs at least kT ln 2 energy

What breaks if you remove Step 2: No bridge between microscopic mechanics and macroscopic thermodynamics. Temperature becomes undefined.
Preserved: The logarithmic measure of multiplicity/uncertainty
Destroyed: Physical units (kT disappears, replaced by bits)
Cross-domain bridge: This chain connects PHYSICS to COMPUTATION via INFORMATION THEORY
```

### Chain 4: Maxwell → Wave Equation → Special Relativity

```
Step 1: Maxwell's equations — ∇·E = ρ/ε₀, ∇×B = μ₀J + μ₀ε₀ ∂E/∂t, etc.
  ↓ via: take curl of Faraday's law, substitute Ampere's law (vacuum: ρ=0, J=0)
Step 2: Electromagnetic wave equation — ∇²E = μ₀ε₀ ∂²E/∂t²
  ↓ via: identify wave speed c = 1/√(μ₀ε₀), note it's independent of reference frame
Step 3: Speed of light is invariant — c is the same in all inertial frames
  ↓ via: Einstein's postulate + Lorentz transformation derivation
Step 4: Special Relativity — ds² = -c²dt² + dx² + dy² + dz² (Minkowski metric)

What breaks if you remove Step 2: No prediction that light is a wave. No derivation of c from ε₀ and μ₀. Electrostatics and magnetostatics remain separate theories.
Preserved: Lorentz invariance (already implicit in Maxwell's equations!)
Destroyed: Galilean relativity (incompatible with constant c)
Historical note: Maxwell's equations were already Lorentz-invariant before Einstein. SR made explicit what was already in the equations.
```

### Chain 5: Riemannian Geometry → Einstein Field Equations → Friedmann → Hubble

```
Step 1: Riemannian geometry — metric tensor g_μν defines distances on curved manifold
  ↓ via: compute Christoffel symbols Γ, then Riemann tensor R^ρ_{σμν}
Step 2: Ricci tensor and scalar — R_μν = R^ρ_{μρν}, R = g^{μν}R_μν
  ↓ via: Einstein's insight — equate geometry to matter: G_μν = (8πG/c⁴)T_μν
Step 3: Einstein field equations — R_μν - ½Rg_μν + Λg_μν = (8πG/c⁴)T_μν
  ↓ via: assume homogeneous isotropic universe (FLRW metric), compute G_μν
Step 4: Friedmann equations — (ȧ/a)² = (8πG/3)ρ - k/a² + Λ/3

What breaks if you remove Step 2: No curvature tensor → no way to encode "spacetime tells matter how to move, matter tells spacetime how to curve."
Preserved: Diffeomorphism invariance (coordinate freedom)
Destroyed: Flatness (the whole point is spacetime can curve)
```

### Chain 6: Fourier Analysis → Spectral Theory → Quantum Mechanics → Chemistry

```
Step 1: Fourier's theorem — any function = sum of sines/cosines (basis decomposition)
  ↓ via: generalize to abstract Hilbert spaces, orthonormal bases
Step 2: Spectral theorem — self-adjoint operators have orthonormal eigenbasis
  ↓ via: identify observables with self-adjoint operators (Born interpretation)
Step 3: Quantum mechanics — measurement yields eigenvalues, probabilities from |⟨ψ|φ_n⟩|²
  ↓ via: solve Schrödinger equation for hydrogen atom Hamiltonian
Step 4: Atomic orbitals → periodic table → chemistry

What breaks if you remove Step 2: No guarantee that measurements produce definite values. No connection between operator algebra and experimental outcomes.
Preserved: Linearity (superposition principle survives the whole chain)
Destroyed: Classical determinism (replaced by probabilistic outcomes)
```

---

## 3. Structural Isomorphisms (Cross-Domain)

### Well-Known (verification baseline)

| # | Object A | Object B | The Map | Preserves | Forgets | Name |
|---|----------|----------|---------|-----------|---------|------|
| 1 | Proofs in intuitionistic logic | Programs in typed λ-calculus | propositions ↔ types, proofs ↔ terms | logical structure, normalization | computational efficiency | Curry-Howard |
| 2 | Stone spaces (compact, Hausdorff, totally disconnected) | Boolean algebras | clopen sets ↔ elements | lattice operations, complementation | metric structure | Stone duality |
| 3 | Locally compact abelian groups | Their character groups | G ↔ Ĝ (group of homomorphisms G → S¹) | group structure | specific elements | Pontryagin duality |
| 4 | Galois connections (order theory) | Adjoint functors (category theory) | closure operators ↔ monads | compositional structure | specific objects | (categorical embedding) |
| 5 | Covectors on a manifold | 1-forms (differential geometry) | df ↔ gradient of f | linear structure, exterior algebra | basis choice | (canonical identification) |

### Less Famous but Equally Precise

| # | Object A | Object B | The Map | Preserves | Forgets | Verifiable? |
|---|----------|----------|---------|-----------|---------|-------------|
| 6 | Banach fixed-point theorem | Recursion/fixed-point combinator (λ-calculus) | contractive maps ↔ recursive definitions, fixed point ↔ least fixed point | existence + uniqueness of fixed point | metric vs domain-theoretic structure | Yes — both have constructive proofs via iteration |
| 7 | Renormalization group (physics) | Multigrid methods (numerical analysis) | coarse-graining ↔ restriction operator, fine-graining ↔ prolongation | scale hierarchy, irrelevant detail elimination | physical meaning | Yes — both are iterated coarsening with error correction |
| 8 | Boltzmann entropy S = k ln Ω | Shannon entropy H = -Σ p log p | microstates ↔ messages, partition function ↔ normalization | logarithmic scaling, additivity for independent systems | physical units, temperature | Yes — both derive from same maximum entropy principle |
| 9 | Eigenvectors of linear operator | Fixed points of dynamical system | Tv = λv ↔ f(x) = x (when λ=1) | invariance under transformation | eigenvalue scaling | Partially — exact when λ=1 |
| 10 | Least action principle (mechanics) | Shortest path / geodesic (geometry) | trajectories ↔ geodesics, Lagrangian ↔ metric | extremality, variational structure | physical interpretation | Yes — Maupertuis principle makes this exact |
| 11 | Ising model (stat mech) | Max-cut problem (graph theory) | spins ↔ binary variables, coupling ↔ edge weights, ground state ↔ max cut | NP-hardness, phase transition at threshold | temperature, physical dynamics | Yes — exact polynomial reduction |
| 12 | Free energy minimization (thermo) | Variational inference (ML) | F = E - TS ↔ ELBO = E_q[log p(x,z)] - E_q[log q(z)] | KL divergence structure, bound optimization | physical system vs probability model | Yes — both minimize KL divergence |
| 13 | Tropical semiring (min, +) | Shortest path algebra | min ↔ addition, + ↔ multiplication | Bellman equation structure, matrix multiplication computes shortest paths | additive inverses (tropical has none) | Yes — Floyd-Warshall is tropical matrix multiplication |
| 14 | Differential forms on manifold | Cochains in simplicial complex | smooth forms ↔ discrete cochains, d (exterior derivative) ↔ δ (coboundary) | cohomology, Stokes' theorem | smooth structure | Yes — de Rham theorem proves isomorphism of cohomology groups |
| 15 | Heisenberg uncertainty (QM) | Nyquist-Shannon theorem (signal processing) | position/momentum ↔ time/frequency, ℏ ↔ 1/2π, |ψ|² ↔ signal power | Fourier duality, conjugate variable tradeoff | specific physical constants | Yes — both are consequences of Fourier analysis on L² |

---

## 4. Candidate Structural Primitives

These are the patterns I see recurring across all of mathematics. Each appears in at least 5 unrelated fields.

### 1. Fixed Point
**Appears in:** Banach contraction (analysis), Brouwer/Lefschetz (topology), Y-combinator (computation), Nash equilibrium (game theory), eigenvalues (linear algebra), renormalization group fixed points (physics), Knaster-Tarski (order theory)
**Invariant property:** A transformation applied to its own output yields the same output
**Formalization:** In any category with suitable completeness, endomorphisms have fixed points (varies by category)

### 2. Duality
**Appears in:** Fourier (time↔frequency), Pontryagin (group↔characters), Stone (algebra↔topology), electromagnetic (E↔B), Lagrangian↔Hamiltonian, primal↔dual (optimization), De Morgan (logic)
**Invariant property:** Two structures are interchangeable via an involutive map; information is preserved but perspective shifts
**Formalization:** Contravariant equivalence of categories

### 3. Composition / Chaining
**Appears in:** Function composition, morphism composition (category theory), group multiplication, matrix multiplication, path concatenation, proof sequencing, pipeline architectures
**Invariant property:** Associativity (the order of evaluation doesn't matter, only the sequence)
**Formalization:** The defining operation of a category

### 4. Symmetry / Invariance
**Appears in:** Noether's theorem (physics), group actions (algebra), gauge theory, isometries (geometry), equivalence classes, conservation laws, dimensional analysis
**Invariant property:** Something remains unchanged under a transformation
**Formalization:** Group actions on sets/spaces; more generally, equivariance

### 5. Boundary / Interface
**Appears in:** ∂ (boundary operator in topology), boundary conditions (PDE), cell membranes (biology), API surfaces (computation), Stokes' theorem, horizons (GR), phase boundaries
**Invariant property:** The boundary of a boundary is empty (∂² = 0)
**Formalization:** Chain complexes, exact sequences

### 6. Decomposition / Basis
**Appears in:** Fourier decomposition, eigendecomposition, prime factorization, tensor decomposition, representation theory (irreducible reps), normal forms, SVD, Jordan form
**Invariant property:** Any object can be uniquely expressed as a combination of irreducible pieces
**Formalization:** Semisimple objects in an abelian category; unique factorization domains

### 7. Coarse-Graining / Forgetting
**Appears in:** Renormalization (physics), quotient groups/spaces (algebra/topology), abstraction (CS), marginalization (probability), dimensional reduction, information loss, entropy increase
**Invariant property:** Structure is lost in a controlled way; some properties are preserved while details vanish
**Formalization:** Forgetful functors, quotient maps, projections

### 8. Extremality / Optimization
**Appears in:** Least action (mechanics), maximum entropy (stat mech), minimum energy (chemistry), shortest path (graph theory), best response (game theory), maximum likelihood (statistics), variational principles
**Invariant property:** The solution is characterized by being at an extremum of some functional
**Formalization:** Calculus of variations; critical points of functionals

### 9. Recursion / Self-Reference
**Appears in:** Recursive functions, fractals, Gödel numbering, fixed-point combinators, renormalization group, self-similar structures, strange loops, diagonal arguments
**Invariant property:** The structure contains a copy or description of itself at a different scale or level
**Formalization:** Fixed points of endofunctors; initial algebras

### 10. Constraint Propagation / Consistency
**Appears in:** Gauss's law (divergence constraints in EM), gauge fixing, type checking, constraint satisfaction, Bianchi identity (GR), conservation laws, normalization conditions
**Invariant property:** Local constraints propagate to determine global structure
**Formalization:** Sheaf conditions; consistency conditions in cohomology

### What Might Be Missing (the fish-in-water candidates)

- **Continuity / Smoothness** — so pervasive it's invisible. The assumption that small changes produce small effects. When it fails (phase transitions, chaos, singularities) the mathematics changes fundamentally.
- **Counting / Measure** — the ability to assign sizes to things. Precedes probability, integration, cardinality. Possibly the most primitive operation.
- **Ordering / Comparison** — the ability to say one thing comes before another. Precedes topology (open sets are defined by ordering), number systems, causality.
- **Lifting / Extension** — the ability to extend a partial structure to a complete one. Appears in extension theorems (Hahn-Banach, Tietze), lifting problems in algebraic topology, analytic continuation. Might be a primitive.

---

## 5. Confidence Calibration

**HIGH confidence (textbook-verifiable, should survive SymPy testing):**
- All Noether tree entries for standard spacetime symmetries
- Derivation chains 1-4
- Structural isomorphisms 1-5 (well-known named results)
- Structural primitives 1-4 (fixed point, duality, composition, symmetry)

**MEDIUM confidence (correct in spirit, details may need adjustment):**
- Gauge symmetry derivation chain (QED from U(1) — standard but subtle)
- Structural isomorphisms 6-12 (less standard, but published)
- Derivation chains 5-6
- Structural primitives 5-10

**LOWER confidence (my synthesis, may contain errors or oversimplifications):**
- Structural isomorphisms 13-15 (my analogies, may be imprecise)
- "What might be missing" section (speculative)
- Claims about what specific constants "encode" structurally

**Everything should be verified before entering the tensor.**

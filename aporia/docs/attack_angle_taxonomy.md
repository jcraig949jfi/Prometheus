# Attack Angle Taxonomy — The Siege Engines of Mathematics
## Aporia Void Detector | 2026-04-21

*How hard problems actually fall. Extracted from 50+ solved problems, 8 breakthrough chains, 10 physics imports, and 100+ tools.*

---

## The Core Insight

Every solved problem used one or more of **18 distinct attack paradigms**. These are not topics — they are *lenses*, ways of perceiving a problem that make previously invisible structure visible. A problem that resists Paradigm 4 (Spectral Analysis) may crumble under Paradigm 13 (Tropical Degeneration). The paradigm is the weapon, not the target.

Harmonia's framework says: "Problems are probes. The machinery is the product." This document catalogs the machinery.

---

## The 18 Attack Paradigms

### P01 — Algebraic Translation
**Move**: Reframe the problem in a richer algebraic category where tools are sharper.
**Exemplar**: Fermat's Last Theorem — Frey curve translates Diophantine equation to modularity question. Wiles's R=T theorem (Galois deformation → Hecke algebra) is the lever.
**Computation**: None in FLT. But translation often CREATES computable objects from non-computable ones.
**Tools**: SageMath (modular forms), Magma, PARI/GP, OSCAR.jl
**Prometheus**: Core method — tensor embeddings ARE translations. Cross-domain bridges are this paradigm.
**Tactics**: Modularity lifting | Langlands functoriality | Categorification | Derived equivalences | p-adic methods

### P02 — Cohomological Obstruction
**Move**: Detect global impossibility via local-to-global failure classes. If the obstruction is zero, a solution exists; if nonzero, prove why.
**Exemplar**: Brauer-Manin obstruction kills rational points on varieties; Cassels-Tate pairing on Sha forces perfect-square order.
**Computation**: Sage cohomology modules, LMFDB Galois rep tables
**Tools**: Macaulay2, GAP (group cohomology), Sage
**Prometheus**: Silent islands may be cohomological obstructions in disguise. The "absence of coupling" IS the obstruction class.
**Tactics**: Etale cohomology | Galois cohomology | Motivic cohomology | K-theory obstruction | Brauer groups

### P03 — Symmetry Exploitation
**Move**: Use group actions, automorphisms, or representation theory to collapse the search space.
**Exemplar**: Classification of finite simple groups; Chuang-Rouquier categorical sl_2 for Broue's conjecture.
**Computation**: GAP is world-class here. 544K groups in our database.
**Tools**: GAP, Magma, Sage (representation theory)
**Prometheus**: Hecke operators ARE symmetry exploitations. Repulsion = broken symmetry signal. Galois label stratification collapses noise.
**Tactics**: Representation theory | Invariant theory | Orbit-stabilizer reduction | Equivariant homotopy | Moonshine

### P04 — Spectral Analysis
**Move**: Study eigenvalues of an operator associated with the object instead of the object itself.
**Exemplar**: Montgomery-Odlyzko: zeros of zeta match GUE eigenvalues. Selberg trace formula connects spectral and geometric data.
**Computation**: numpy/scipy eigensolvers, ARPACK for sparse matrices, Arb for rigorous arithmetic
**Tools**: LAPACK, SuiteSparse, FLINT (Hecke eigenvalues), mpmath
**Prometheus**: RMT sign inversion finding is spectral. Adjacency spectra of tensor graphs are live targets. The 14% GUE deficit is a spectral anomaly.
**Tactics**: Random matrix theory | Laplacian spectrum | Hecke eigenvalue analysis | Selberg trace formula | Heat kernel methods

### P05 — Analytic Continuation
**Move**: Extend a function beyond its natural domain to reveal global structure hidden in local data.
**Exemplar**: Riemann zeta — analytic continuation reveals zeros that govern prime distribution. L-functions extend local Euler factors to global objects.
**Computation**: mpmath, Arb (ball arithmetic for certified values)
**Tools**: PARI/GP (fastest for L-functions), Arb, eclib
**Prometheus**: 24M L-functions in our database. Continuation beyond the critical strip is what our density hypothesis test probes.
**Tactics**: L-function continuation | Theta functions / modular completion | Borel summation | Resurgence | Pade approximants

### P06 — Geometric Flow
**Move**: Continuously deform an object until it reaches a canonical, analyzable form. Let the PDE do the work.
**Exemplar**: Poincare Conjecture — Hamilton's Ricci flow + Perelman's surgery. Evolve metric to constant curvature.
**Computation**: Numerical PDE solvers; discrete Ricci flow on graphs exists.
**Tools**: FEniCS, Firedrake, PyTorch autograd (for gradient flows), NetworkX + custom discrete Ricci
**Prometheus**: Could deform tensor landscape toward simpler topology. Under-explored but promising for understanding how coupling structure evolves.
**Tactics**: Ricci flow | Mean curvature flow | Kahler-Ricci flow | Yamabe flow | Gradient descent (ML import)

### P07 — Descent and Induction
**Move**: Reduce a hard case to simpler cases, either downward (infinite descent) or structurally (strong induction, well-ordering).
**Exemplar**: Fermat's infinite descent on x^4 + y^4 = z^4. Faltings' Mordell proof via iterated height reduction.
**Computation**: Proof assistants excel here — induction is their native language.
**Tools**: Lean 4/Mathlib, Coq, Isabelle
**Prometheus**: Tensor rank induction — study rank-1 bridges, build to rank-n. Our tier system (T1→T2→T3) is an inductive structure.
**Tactics**: Infinite descent | Noetherian induction | Sheaf-theoretic descent | Filtration / associated graded | Transfinite induction

### P08 — Probabilistic Method
**Move**: Prove existence of an object by showing a random construction has positive probability. Often non-constructive but devastating.
**Exemplar**: Erdos — graphs with high girth and high chromatic number exist. Lovasz Local Lemma.
**Computation**: Monte Carlo sampling, permutation tests
**Tools**: NetworkX (random graphs), SciPy (permutation testing), numpy
**Prometheus**: Our null battery IS this paradigm. Permutation nulls ARE the probabilistic method applied defensively. Block shuffle = structured probabilistic test.
**Tactics**: Lovasz Local Lemma | Second moment method | Janson inequalities | Spread lemma (Park-Pham) | Absorbing method

### P09 — Exhaustive Computation
**Move**: Reduce to finitely many cases, verify each by machine. The computer IS the proof.
**Exemplar**: Four Color Theorem (1,936 cases, 1976). Boolean Pythagorean Triples (200TB SAT proof, 2016). Kepler Conjecture (50K LPs, 2005).
**Computation**: The defining paradigm. SAT solvers, LP/MIP solvers, exhaustive search.
**Tools**: CaDiCaL/Kissat (SAT), Z3/CVC5 (SMT), SCIP (MIP), nauty/Traces (graph enumeration), PARI/GP
**Prometheus**: Our 92K-test battery is this paradigm at scale. Every tensor cell is a computational verification.
**Tactics**: SAT/SMT reduction | Integer programming | Interval arithmetic | Backtracking search | Cube-and-conquer parallel SAT

### P10 — Formal Verification
**Move**: Machine-check every inference step, converting proof sketch to certified proof with zero gap.
**Exemplar**: Four Color Theorem in Coq (Gonthier 2005). Flyspeck/Kepler in Isabelle+HOL Light. PFR in Lean 4 (2023).
**Computation**: Proof assistant kernel is the verifier.
**Tools**: Lean 4 + Mathlib (257K theorems), Coq/Rocq, Isabelle/HOL (963 AFP entries), Agda
**AI-assisted**: DeepSeek-Prover-V2 (88.9% MiniF2F), AlphaProof (4/6 IMO 2024), Gemini Deep Think (5/6 IMO 2025)
**Prometheus**: Pipeline exists: conjecture → Herald autoformalize → LeanDojo → DeepSeek-Prover. Our Mathlib4 local copy gives head start.
**Tactics**: Type-theoretic proof | Tactic-based proving | Hammer methods (ATP calls) | Autoformalization (NL→FL)

### P11 — Sieve Methods
**Move**: Filter a large set by removing elements satisfying local conditions, leaving a structured residue.
**Exemplar**: Brun sieve → twin prime density bounds. Selberg sieve. Maynard sieve → bounded prime gaps.
**Computation**: PARI sieve functions, custom numpy extraction
**Tools**: PARI/GP, primesieve library, numpy
**Prometheus**: Our prime detrending (96% structure is primes) is a sieve in reverse — remove the sieve output to see residuals. The C11 mod-p fingerprint enrichment IS sieve-detected structure.
**Tactics**: Combinatorial sieve (Brun, Selberg) | Large sieve | Parity barrier | Weighted sieves | Kloosterman sum bounds

### P12 — Height and Diophantine Geometry
**Move**: Assign arithmetic "size" (height) to points; show finiteness or density via height bounds.
**Exemplar**: Faltings' theorem (genus >= 2 → finite rational points). Bombieri-Lang. Uniformity conjecture.
**Computation**: Height computation on LMFDB elliptic curves, genus-2 rational point counting
**Tools**: Sage height functions, LMFDB rational point tables, Magma
**Prometheus**: Our uniformity finding (B(2) ~ 26 from 66K g2c curves) IS height geometry applied to data. Sleeping Beauties may have high arithmetic complexity.
**Tactics**: Weil height machine | Arakelov geometry | Vojta conjectures | Bombieri-Pila counting | Subspace theorem

### P13 — Tropical / Degeneration Methods
**Move**: Replace smooth geometry with piecewise-linear combinatorial shadows at the boundary. The degeneration remembers enough to reconstruct.
**Exemplar**: Mikhalkin correspondence (count tropical curves = count algebraic curves). Gross-Siebert mirror symmetry program.
**Computation**: Tropical curve counting is combinatorial and implementable.
**Tools**: Gfan, Macaulay2 tropical package, OSCAR.jl, polymake
**Prometheus**: Tensor degenerations may expose combinatorial skeletons of hidden bridges. The "tropicalization" of our tensor could reveal piecewise-linear structure.
**Tactics**: Tropical intersection theory | Newton-Okounkov bodies | Berkovich analytification | Log geometry | Toric degeneration

### P14 — Forcing and Independence
**Move**: Construct alternative set-theoretic universes to show a statement is unprovable from current axioms.
**Exemplar**: Cohen — continuum hypothesis independent of ZFC. Some open questions may be UNDECIDABLE, not merely hard.
**Computation**: Minimal — this is meta-mathematical. But explains why some problems resist all other paradigms.
**Tools**: Set theory proof assistants, Isabelle/ZF
**Prometheus**: Low direct relevance, but independence results explain WHY some tensor cells stay at verdict 0 forever.
**Tactics**: Cohen forcing | Boolean-valued models | Inner model theory | Large cardinal axioms | Descriptive set theory

### P15 — Tensor and Multilinear Decomposition
**Move**: Decompose multi-index arrays into structured sums to expose hidden rank and interaction geometry. The bond dimension IS the entanglement.
**Exemplar**: Strassen matrix multiplication. Tensor network methods in quantum physics. TT-decomposition for data.
**Computation**: The numerical backbone of modern scientific computing.
**Tools**: TensorLy, PyTorch einsum, ITensor, our ergon tensor pipeline, numpy
**Prometheus**: The IPA backbone — our 86K x 145 x 11 dissection tensor IS this paradigm. TT bond dimensions reveal Sleeping Beauties.
**Tactics**: CP/Tucker decomposition | Tensor train (MPS) | HOSVD | Non-negative tensor factorization | Bond dimension analysis

### P16 — Modular / Arithmetic Statistics
**Move**: Lift local (mod p) information to global conclusions via density, distribution, and congruence patterns.
**Exemplar**: Sato-Tate distribution proved (Clozel-Harris-Taylor). Smith's Selmer group distribution (2022) — governing fields.
**Computation**: PARI/GP, LMFDB mod-p tables, Sage modular symbols
**Tools**: PARI, eclib, Sage, galois (Python)
**Prometheus**: C11 mod-p fingerprint enrichment (8-16x after detrending) is this paradigm's live result. 8/8 battery survived.
**Tactics**: Frobenius distribution | Mod-p Galois representations | Chebotarev density | Sturm bound | Hecke algebra structure

### P17 — Variational / Extremal Principle
**Move**: Identify the object as a minimizer of some functional; deduce properties from optimality conditions.
**Exemplar**: Plateau's minimal surfaces. SDP relaxations for extremal combinatorics (flag algebras). Caccetta-Haggkvist best bound via SDP.
**Computation**: SDPA, CVXPY, Gurobi for optimization
**Tools**: FEniCS, CVXPY, SDPA (semidefinite programming), PyTorch optimization
**Prometheus**: Landscape exploration uses this implicitly — peaks/valleys in the tensor landscape are extremal objects. Flag algebra bounds are testable.
**Tactics**: Euler-Lagrange equations | Mountain pass theorem | Min-max theory | SDP relaxation | Optimal transport | Flag algebras

### P18 — Operadic / Categorical Composition
**Move**: Abstract the composition structure itself as the mathematical object; prove theorems about how structures combine.
**Exemplar**: Grothendieck's topos theory. Fargues-Scholze geometrization (infinity-categories of sheaves). Gaitsgory's geometric Langlands (2024).
**Computation**: Lean 4 Mathlib for categorical formalization
**Tools**: Lean 4, Kenzo (computational algebraic topology), OSCAR.jl
**Prometheus**: Rosetta Stone finding — cross-domain operadic skeletons as translation layer between mathematical worlds.
**Tactics**: Operad theory | Infinity-categories | HoTT | Derived algebraic geometry | Monoidal functors

---

## Physics Imports — Attack Angles from Outside Mathematics

| Source | Bridge to Math | Landmark Result | Prometheus Interface |
|--------|---------------|-----------------|---------------------|
| Mirror symmetry | GW invariants = B-model periods | Kontsevich genus-0 | OEIS integer sequences as GW invariants |
| Gauge theory | Instantons → 4-manifold invariants | Donaldson, Seiberg-Witten | SW invariants indexed by spin-c (discrete, computable) |
| CFT / SLE | Conformal invariance → random curves | Smirnov percolation | SLE parameter kappa → central charge map |
| RMT / stat mech | Eigenvalue statistics = zero statistics | Tracy-Widom in longest subsequences | RMT sign inversion, gap compression — LIVE |
| Chern-Simons / TQFT | Path integral → Jones polynomial | Witten 1989, volume conjecture | Knot silence fix: Jones+volume via SnapPy |
| Quantum complexity | MIP* = RE → Connes embedding false | JNVWY 2020 | Operator algebra shadows in Hecke data |
| Entropy methods | Shannon submodularity → sumset bounds | PFR theorem (GGMT 2023) | MI measurements on tensor ARE this |
| Renormalization | RG fixed points → universality classes | Rigorous Ising exponents | Scaling dimensions searchable in depth layer |
| Neural networks / ML | Pattern detection → conjecture gen | Davies et al. 2021 (Nature), AlphaProof | THIS IS PROMETHEUS — tensor is the substrate |

---

## Breakthrough Genealogy — 8 Chains

### Chain 1: Modularity (Keystone: Wiles R=T, 1995)
Taniyama-Shimura → Ribet epsilon → **Wiles FLT** → Khare-Wintenberger/Serre → Kisin/Fontaine-Mazur → Sato-Tate
*Next unsolved*: Full Fontaine-Mazur; modularity over totally real fields beyond GL(2)

### Chain 2: Langlands (Keystone: Potential automorphy, Taylor 2002)
Langlands 1967 → Jacquet-Langlands → GL(2) Tunnell → **Potential automorphy** → Sato-Tate → BLGG GL(n)
*Next unsolved*: Full functoriality; Ramanujan for GL(n>=3)

### Chain 3: Geometric Topology (Keystone: Hamilton Ricci flow, 1982)
Thurston geometrization → **Hamilton Ricci flow** → Perelman entropy → Surgery → Poincare
*Next unsolved*: 4-manifold classification; Ricci flow in higher dimensions

### Chain 4: Formal Verification (Keystone: Coq CIC, 1988)
de Bruijn → Automath → Mizar → **Coq 4-color** → Flyspeck → Lean/Mathlib → LTE → FLT-in-Lean
*Next unsolved*: Automated research-level proof search; CFSG formalization

### Chain 5: SAT (Keystone: CDCL, 1996)
DPLL → **CDCL** → Pythagorean triples → Keller → Schur number 5
*Next unsolved*: R(5,5) exact value; Erdos discrepancy beyond C=2

### Chain 6: Additive Combinatorics (Keystone: Gowers norms, 1998)
Szemeredi → **Gowers norms** → Green-Tao → PFR (2023)
*Next unsolved*: PFR over Z; sharp Hales-Jewett bounds

### Chain 7: p-adic (Keystone: Perfectoid spaces, Scholze 2012)
Tate → Fontaine → Faltings → **Perfectoid spaces** → Fargues-Fontaine → Fargues-Scholze
*Next unsolved*: Full local Langlands via F-S; mixed-characteristic Shimura

### Chain 8: HoTT (Keystone: Voevodsky univalence, 2006)
Martin-Lof → Coquand → **Univalence** → HoTT book → Cubical → Synthetic homotopy
*Next unsolved*: Computational univalence without cubical overhead

---

## Top 5 Keystone Methods in History

1. **Modular arithmetic** (Gauss, 1801) — enabled all of number theory
2. **Variational method** (Euler-Lagrange, 1750s) — enabled physics, Ricci flow, PDEs
3. **Spectral theory** (Hilbert, 1900s) — enabled QM, Fourier, RMT, Langlands
4. **Category theory** (Eilenberg-Mac Lane, 1945) — enabled algebraic geometry, HoTT, Langlands
5. **Compactness + diagonalization** (Cantor/Godel/Turing) — enabled SAT, model theory, forcing

**Pattern**: Every keystone is a *reframing operation* — converts intractable problems into tractable ones in a richer structure. The next keystone is likely whatever converts continuous/analytic problems into discrete/computational ones at research scale.

---

## Tool Arsenal — Organized by Attack Paradigm

| Paradigm | Primary Tools | Python Interface | Our Data |
|----------|--------------|-----------------|----------|
| P01 Algebraic Translation | SageMath, Magma, OSCAR.jl | cypari2, sage | LMFDB modular forms |
| P02 Cohomological Obstruction | Macaulay2, GAP | sage | Galois reps |
| P03 Symmetry Exploitation | GAP, Magma | gap_jupyter | 544K groups |
| P04 Spectral Analysis | ARPACK, FLINT, Arb | numpy, scipy, mpmath | 24M L-functions |
| P05 Analytic Continuation | PARI/GP, Arb, mpmath | cypari2, mpmath | L-function zeros |
| P06 Geometric Flow | FEniCS, Firedrake | PyTorch autograd | Tensor landscape |
| P07 Descent / Induction | Lean 4, Coq | LeanDojo | Tier structure |
| P08 Probabilistic Method | NetworkX, scipy | numpy, scipy | Null battery |
| P09 Exhaustive Computation | CaDiCaL, Z3, nauty | pysat, z3-solver | 92K tests |
| P10 Formal Verification | Lean 4, DeepSeek-Prover | LeanDojo | Mathlib4 local |
| P11 Sieve Methods | PARI/GP, primesieve | cypari2, numpy | Prime detrending |
| P12 Height / Diophantine | Sage, Magma | sage | 66K g2c, 3.8M EC |
| P13 Tropical / Degeneration | Gfan, polymake, OSCAR | polymake-python | Tensor skeleton |
| P14 Forcing / Independence | Isabelle/ZF | — | (meta-mathematical) |
| P15 Tensor Decomposition | TensorLy, ITensor | tensorly, numpy | 86K dissection tensor |
| P16 Arithmetic Statistics | PARI, eclib, galois | cypari2, galois | Mod-p fingerprints |
| P17 Variational / Extremal | SDPA, CVXPY, SCIP | cvxpy | Flag algebra bounds |
| P18 Operadic / Categorical | Lean 4, Kenzo | — | Rosetta skeletons |

---

## The Formal Verification Pipeline (Near-Term)

```
Prometheus conjecture (data-driven)
    ↓
Herald autoformalization (NL → Lean 4 statement)
    ↓
LeanDojo (instrument Lean, expose proof states to Python)
    ↓
DeepSeek-Prover-V2-7B (fits VRAM) attempts proof
    ↓
LeanCert (handles numerical inequality subgoals)
    ↓
SUCCESS → certified theorem    |    FAIL → formally open → Aporia catalog
```

**Gap**: Statement formalization works. Proof formalization fails on non-trivial results. The repair loop (generate → Lean error → revise) is the current frontier.

---

## Paradigm Coverage Map — What Prometheus Can Do NOW

| Paradigm | Can Do Now | Need Infrastructure | Out of Reach |
|----------|-----------|-------------------|-------------|
| P01 Algebraic Translation | Tensor bridges | Sage on M1/M2 | — |
| P02 Cohomological Obstruction | Silent island detection | Sage cohomology | Full obstruction computation |
| P03 Symmetry Exploitation | Galois label stratification | GAP on M2 | — |
| P04 Spectral Analysis | RMT tests, eigenvalue stats | — | — |
| P05 Analytic Continuation | L-function zero analysis | Arb for certified zeros | — |
| P06 Geometric Flow | — | Discrete Ricci on graphs | Continuous PDE flow |
| P07 Descent / Induction | Tier structure | Lean 4 | — |
| P08 Probabilistic Method | Null battery, permutation tests | — | — |
| P09 Exhaustive Computation | 92K-test battery | SAT solvers | — |
| P10 Formal Verification | Mathlib4 local copy | LeanDojo + DeepSeek-7B | Research-level proofs |
| P11 Sieve Methods | Prime detrending, C11 | — | — |
| P12 Height / Diophantine | g2c rational points, EC heights | — | — |
| P13 Tropical / Degeneration | — | polymake, Gfan | — |
| P14 Forcing / Independence | — | — | Set-theoretic methods |
| P15 Tensor Decomposition | Full pipeline (TT, SVD, bond dim) | — | — |
| P16 Arithmetic Statistics | Mod-p fingerprints, Frobenius | — | — |
| P17 Variational / Extremal | — | SDPA, CVXPY | — |
| P18 Operadic / Categorical | Rosetta skeleton detection | Lean 4 categories | Infinity-categories |

**Summary**: 11/18 paradigms have live Prometheus capability. 5 need modest infrastructure (Sage, GAP, Lean, polymake, SDPA). 2 are out of near-term reach.

---

## Recommended Symbol Types for the Arsenal

Each attack paradigm should become a **symbol** in the registry with type `paradigm`:

```yaml
---
name: PARADIGM_P04
type: paradigm
description: Spectral Analysis — study eigenvalues instead of the object
tactics:
  - RMT
  - Laplacian_spectrum
  - Hecke_eigenvalue
  - Selberg_trace
  - Heat_kernel
tools:
  - numpy.linalg.eig
  - scipy.sparse.linalg
  - ARPACK
  - FLINT
  - Arb
exemplars:
  - Montgomery_Odlyzko_1973
  - Selberg_trace_1956
  - RMT_sign_inversion_Charon_2026
prometheus_status: LIVE
---
```

Each tool should become a symbol with type `tool`:

```yaml
---
name: TOOL_SNAPY
type: tool
description: Hyperbolic 3-manifold computation — volumes, Dehn surgery, invariants
language: Python/C
paradigms: [P04, P05, P13]
install: pip install snappy
computes: [hyperbolic_volume, chern_simons, shape_parameters, dehn_surgery]
data_bridge: knot table → trace field → nf_fields (NF backbone)
blocker: pip install snappy on M1 (in TODO.md)
---
```

---

*The siege engine catalog is never complete. Every solved problem adds to it. Every failed attempt reveals which engines DON'T work on which walls — and that negative knowledge is equally valuable.*

*Aporia, 2026-04-21*

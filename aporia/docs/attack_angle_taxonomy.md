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

---

## 2026-04-26 — Frontier-review-driven revisions in flight

The 21-paradigm extension proposed in `whitepapers/attack_strategy_for_frontier_review_20260426.md` is being cycled through 5 frontier models. Convergent verdicts (held against `stoa/discussions/2026-04-26-frontier-review/`):

- **P20 (Quality-diversity / MAP-Elites) — DEPRECATED as paradigm.** Both ChatGPT (§8.1) and Gemini (§8.1) reject P20 as a mathematical lens; it is correctly framed as a *control policy* over the substrate's exploration loop (the Maieutēs incubator), not as a way of perceiving a mathematical object. Moved to operational layer in two-track epistemics; removed from paradigm catalog pending replacement decision.
- **P20 replacement — CONTESTED, holding for full 5-model view.** ChatGPT proposes P20' Constraint Relaxation / SAT Encoding (citing REQ-026 and last-20-years SAT breakthroughs). Gemini proposes P22 Spectral Tail Relocation (citing TOOL_GPD_TAIL_FIT and the central-zero obsession of human mathematics). Both are sharp. Decision deferred until Grok, DeepSeek, and Claude (fresh) responses are in.
- **P19 (Cross-region operator transport) — CONFIRMED** by both ChatGPT and Gemini (§8.1).
- **P21 (Curated-corpus empirical sweep) — CONFIRMED** by both ChatGPT and Gemini (§8.1).

Final canonical count and the replacement choice will land in this document once the 5-model synthesis converges. Until then, the substrate operates with P19 and P21 as accepted Tier-1 additions; P20 is removed; the slot is open.

---

## 2026-05-08 — Round 2 paradigm additions from recent solves

Round 2 of solved-problems genealogy (`aporia/mathematics/solved_problems_genealogy.md` R1-R5) surfaced techniques not cleanly captured by P01-P21. Adding 5 new paradigms based on observed 2002-2020 attack patterns. Numbering continues from P21 (P20 still removed).

### P22 — Polynomial Method (Spectral on Signed Graphs)
**Move:** Build a signed graph encoding the combinatorial object; apply Cauchy interlacing or related spectral inequality on a carefully-chosen induced subgraph; extract the desired bound from the spectral bound.
**Exemplar:** Hao Huang's Sensitivity Conjecture proof (2019, 6 pages). Signed n-dimensional hypercube + Cauchy interlacing on largest subgraph of size > 2^{n-1} forces a vertex of degree ≥ √n, giving s(f) ≥ √(deg(f)).
**Computation:** numpy/scipy eigensolvers; sparse graph eigensolvers; symbolic-spectral toolboxes.
**Tools:** Sage / numpy.linalg / spectral-graph libraries.
**Prometheus:** Boolean-function probes are downstream of substrate's operator-output pairs. Signed-edge construction is a generic "weight by parity of property" template — applies to any combinatorial object with a binary property.
**Tactics:** Cauchy interlacing | Signed-edge weighting | Largest-induced-subgraph extraction | Polynomial-method on F_2^n
**Distinction from P15 (Tensor / Multilinear):** P15 decomposes a multilinear object; P22 builds an auxiliary graph and reads spectra. Different objects.
**Distinction from P04 (Spectral Analysis):** P04 reads the spectrum of an operator already attached to the math object (Laplacian, Hecke). P22 *constructs* the operator (signed adjacency) specifically to encode the property. Constructive vs given.

### P23 — Recursive Self-Compression (Protocol Bootstrapping)
**Move:** Show that an instance of a computational/proof system can simulate a strictly smaller instance of itself; iterate to get unbounded simulation power.
**Exemplar:** Ji-Natarajan-Vidick-Wright-Yuen 2020 MIP* = RE. MIP* protocols admit compression: outer protocol delegates to an inner MIP* protocol with strict savings; iteration lets MIP* simulate Turing-machine halting (RE).
**Computation:** Symbolic protocol verification; theorem-prover-style checking of inner-protocol correctness.
**Tools:** Coq / Lean for protocol formalization; complexity-theory frameworks.
**Prometheus:** Meta-paradigm. Probes for "is there a self-similar structure that allows compression?" Substrate's CLAIM evaluation might admit P23-style analysis if a CLAIM can compute the verdict on a smaller CLAIM.
**Tactics:** Protocol delegation | Strictly-decreasing-size lemma | Iteration to fixed-point | Halting-problem encoding
**Distinction from P09 (Exhaustive Computation):** P09 enumerates instances; P23 doesn't enumerate, it bootstraps capability.
**Distinction from P14 (Forcing and Independence):** P14 builds models; P23 builds protocols that simulate themselves at smaller scale.

### P24 — Quantitative Bound-Tightening Long Program
**Move:** A theorem holds in principle for "sufficiently large" parameters; the bound is astronomical; iteratively tighten the bound (often with hybrid analytic+computational improvements) until it meets computer-verification range.
**Exemplar:** Ternary Goldbach (Vinogradov 1937 with 3^{3^{15}} bound; tightened by Borozdkin 1956, Chen-Wang 1989, Liu-Wang 2002; closed by Helfgott 2013 with 8.875 × 10^{30} bound + computer verification). 90-year continuous push.
**Computation:** Explicit zero-free regions for L-functions; major-arc/minor-arc estimates; computer verification of small cases.
**Tools:** mpmath, FLINT, Pari, GMP for high-precision arithmetic; explicit-formula libraries.
**Prometheus:** Substrate's "deg-N enumeration scaling" pattern (per substrate-tester fire-20 / fire-27 cross-degree hit-rate finding) is a P24-shaped probe at small scale. Bound-tightening is itself a substrate-grade operator: each fire that tightens a numerical threshold by 0.5 dex is a P24 step.
**Tactics:** Explicit zero-free regions | Major-arc / minor-arc decomposition | Computer-verification-meets-analytic-bound | Hybrid analytic+computational
**Distinction from P09 (Exhaustive Computation):** P24 *combines* analytic bound-tightening with exhaustive computation. P09 alone gives only direct verification.

### P25 — Pivotal Negative Result (Reorienting Lemma)
**Move:** A surprising negative theorem (e.g., "this expected-true proposition is actually false") forces the field to re-formulate the conjecture; the re-formulation then becomes tractable.
**Exemplar:** Fefferman 1971 disc-multiplier negative result for Bochner-Riesz at δ=0 pivots the field's understanding; Carleson-Sjölin proves the correct conjecture in n=2 within a year. Other exemplars: Manolescu 2013 Pin(2)-cohomology obstruction → triangulation conjecture FALSE in dim ≥5; Slofstra 2017 Tsirelson-problem disproof → MIP* path open.
**Computation:** Counterexample construction; explicit obstruction class; numerical experiments that surface anomalies.
**Tools:** Sage, Magma, GAP, computer-search frameworks.
**Prometheus:** This is the substrate's KILL operator at the meta-level. Every kill that reorients a research direction is a P25 instance. The 4-fold falsification battery is a structural P25-generator.
**Tactics:** Counterexample construction | Obstruction-class identification | Surprise-amplification (when the negative result was widely-believed-not-to-hold)
**Distinction from P02 (Cohomological Obstruction):** P02 *reads* an existing cohomology class to detect impossibility; P25 produces the negative result that motivates building the obstruction theory.
**Distinction from P09 (Exhaustive Computation):** P09 verifies; P25 *finds* the unexpected counterexample.

### P26 — Continuous Relaxation / Linear Programming Bound
**Move:** A discrete-optimization problem (sphere packing, code distances, Turán-type extremal counts) is relaxed to a continuous LP / SDP / convex program; the relaxation's optimum is computable; matching constructive lower bounds with the relaxation upper bound proves optimality.
**Exemplar:** Cohn-Elkies 2003 sphere packing LP bound; Viazovska 2016 sphere packing in d=8 (uses a magic modular function as the LP-feasible witness); Cohn-Kumar-Miller-Radchenko-Viazovska 2017 d=24. The LP bound is structural; the magic function is the constructive piece that hits it.
**Computation:** Linear and semidefinite programming (CDD, CVX, Mosek); modular-form computation; theta-series integration.
**Tools:** SageMath (LP solvers), CVX / CVXPY, Magma (modular forms), Pari/GP.
**Prometheus:** Substrate's calibration-anchor density measurement (T036) is a P26-flavored audit. Sphere-packing in d=24 is already in the database as Tier 1 (#194); P26 is the technique that solved its 2D / 8D / 24D cases.
**Tactics:** LP / SDP relaxation | Magic-function witness construction | Modular-form-meets-optimization | Cohn-Elkies linear programming bound
**Distinction from P17 (Variational / Extremal Principle):** P17 minimizes/maximizes a functional; P26 specifically relaxes to a continuous convex program with computable optimum.
**Distinction from P15 (Tensor and Multilinear):** P15 decomposes; P26 optimizes.

---

## Round 2 cross-cutting observations

The 5 new paradigms (P22-P26) are derived from 5 recent landmark solves (R1-R5 of solved-problems genealogy). Patterns:

- **P22, P23, P25 are "single-insight" paradigms** — each cracks a problem via one well-chosen construction. Predictability of appearing in advance: low.
- **P24, P26 are "long-program" paradigms** — each is a multi-decade trajectory of incremental refinement. Predictability: high (trajectory visible years in advance).
- **All 5 involve cross-domain ingredient import** — none of P22-P26 is purely internal to the original problem domain. Reinforces HARD-5: discipline labels are docstrings; the paradigm crosses them freely.
- **P25 (Pivotal Negative Result) is the substrate's natural meta-paradigm** — every kill that reorients direction is P25-shaped. The 4-fold falsification battery is a structural P25-generator.

Canonical count is now P01-P26 (P20 still removed pending replacement decision; effective active paradigms: 25).

---

*Aporia, 2026-05-08*

---

## 2026-05-08 (later) — Tensor-specific paradigms (P27-P31)

Per James 2026-05-08 directive (`aporia/mathematics/tensor_open_problems_v1.md`): tensor mathematics is going to be central to Prometheus, and the attack vectors used in the tensor-frontier literature don't reduce cleanly to P01-P26. Five additional paradigms specific to (or strongly characteristic of) tensor problems.

### P27 — Slice Rank / Polynomial Method on F_q (Croot-Lev-Pach)
**Move:** Build a high-degree polynomial vanishing on a combinatorial set; bound the dimension of the polynomial space; bound the set size via the rank of the slice operator. Slice rank, partition rank, analytic rank, geometric rank are related-but-distinct structure detectors; pick the right one for the bound you want.
**Exemplar:** Cap-set bound o(2.756^n) for Z_3^n (Ellenberg-Gijswijt 2017) and Z_4^n (Croot-Lev-Pach 2017). Core technique: 3-tensor T(x,y,z) = δ(x+y+z=0); slice rank of T over F_3 bounds cap set size.
**Computation:** Polynomial dimension counting; tensor-rank-zoo computation over finite fields.
**Tools:** Sage, Magma; custom polynomial-method codes.
**Prometheus:** Substrate-friendly because (a) operates over F_q with explicit dimension counts (auditable by substrate-tester), (b) handles many cap-set-style problems uniformly, (c) exposes the rank-zoo (slice / partition / analytic / geometric) as a calibration anchor.
**Tactics:** Slice rank | Partition rank (Naslund) | Analytic rank (Lovett) | Geometric rank (Kopparty-Moshkovitz-Zuiddam) | Polynomial method on F_q
**Distinction from P22 (Polynomial Method on Signed Graphs):** P22 attacks bilinear questions via Cauchy interlacing on a signed graph. P27 attacks combinatorial-set-size questions via polynomial-rank bounds in F_q. Different graph vs. polynomial space; different inequality (rank vs interlacing).
**Catalog refs:** Open problems #13-15, #56, #95-99 in `aporia/mathematics/tensor_open_problems_v1.md`.

### P28 — Asymptotic Spectrum (Strassen)
**Move:** Find a complete set of monotone semiring-homomorphisms (real-valued functionals) on a tensor pre-order under restriction / degeneration; the asymptotic value of the pre-order on a tensor is the maximum of these monotones. Each monotone is a "spectrum point."
**Exemplar:** Strassen's asymptotic rank (1986-1991). Monotones include: matrix flattenings, support functionals, slice rank, quantum functionals (Christandl-Vrana-Zuiddam 2017). ω = log_2 R(M⟨2⟩^∞) is the asymptotic-rank value of the matrix multiplication tensor.
**Computation:** Compute candidate monotones on test tensors; verify monotonicity numerically over restriction relations; search for new monotones from quantum entropy inequalities.
**Tools:** Numerical SDP for moment polytopes; symbolic representation theory (LiE, Symmetrica).
**Prometheus:** A meta-paradigm for "asymptotic invariants of pre-orders." The substrate's CoordinateChart / asymptotic-restriction primitive (T030 operator-portability extends in this direction) is a P28-shaped object.
**Tactics:** Spectrum-point construction | Quantum functionals | Support functionals | Razborov rank functions | Moment-polytope evaluation
**Distinction from P04 (Spectral Analysis):** P04 spectrum is eigenvalues; P28 spectrum is real-valued monotones on a pre-order. Different mathematical object — eigenvalue vs functional.
**Catalog refs:** Open problems #1-2, #7-8, #16-17 in tensor_open_problems_v1.md.

### P29 — Border Apolarity (Buczyńska-Buczyński)
**Move:** Bound the border rank of a tensor / form via combinatorial conditions on apolar 0-dimensional schemes (Gorenstein quotients of polynomial rings). Replace the topological closure (border rank) with a scheme-theoretic invariant (cactus rank); use Macaulay's inverse-system theory + Hilbert function bookkeeping.
**Exemplar:** Border-rank lower bounds on M⟨3⟩ (Landsberg-Michałek). Border apolarity gives R̲(M⟨3⟩) ≥ 17. Buczyńska-Buczyński-Galązka algorithms enumerate B-invariant ideals of fixed multiplicity.
**Computation:** Macaulay2 with Apolarity package; symbolic Hilbert-function tracking; multigraded Hilbert scheme computations.
**Tools:** Macaulay2 SecantVarieties; Apolarity; MultigradedHilbert.
**Prometheus:** Substrate-friendly because lower bounds via apolarity are CONSTRUCTIVE (the obstruction is a specific scheme), making them auditable by substrate-tester. Pairs with the substrate's TriangulationProtocol (independent obstructions = independent apolar schemes).
**Tactics:** Apolar Gorenstein scheme construction | Hilbert function bookkeeping | Multigraded Hilbert scheme | B-invariant ideal enumeration
**Distinction from P02 (Cohomological Obstruction):** P02 reads cohomology of variety; P29 constructs apolar 0-d scheme. Different setup — variety vs apolar quotient.
**Distinction from P15 (Tensor / Multilinear Decomposition):** P15 decomposes tensors; P29 bounds the rank of decomposition via scheme combinatorics. Decomposition vs decomposition-bound.
**Catalog refs:** Open problems #5, #19, #20, #28-30 in tensor_open_problems_v1.md.

### P30 — Tensor Network Contraction (TN / DMRG / PEPS)
**Move:** Represent a high-dimensional tensor as a network of low-dimensional tensors connected by index contractions; computational task = optimal contraction order; approximation = bounded bond dimension. Multi-particle quantum systems use MPS / PEPS / MERA / TT formats.
**Exemplar:** DMRG (White 1992) for 1D quantum many-body problems; PEPS for 2D; MERA for critical / scale-invariant systems; cotengra / opt_einsum for general tensor-network contraction-order optimization.
**Computation:** ITensor (Julia/C++); TenPy (Python); TensorNetwork (Google); cotengra; opt_einsum.
**Tools:** ITensor, TenPy, TensorNetwork, cotengra, opt_einsum, T3F (TensorFlow), TT-Toolbox.
**Prometheus:** Tensor networks are the natural representation for the unified-tensor build (HARD-3). The substrate's CoordinateChart system can host a TensorNetwork primitive that internally uses these tools. P30 is THE paradigm for the substrate's eventual large-scale data structure.
**Tactics:** MPS / TT contraction | PEPS / 2D contraction | MERA hierarchical decomposition | Bond-dimension truncation | Treewidth-based contraction order | Variational tensor-network optimization
**Distinction from P15 (Tensor and Multilinear Decomposition):** P15 = decompose a fixed tensor into rank-1 sums (CP decomposition). P30 = represent a tensor as a contraction-network of small tensors (TT / Tucker / MPS). Decomposition format differs.
**Distinction from P09 (Exhaustive Computation):** P09 enumerates all states; P30 represents a state implicitly via contractions, side-stepping enumeration.
**Catalog refs:** Open problems #49-51, #75-78, #82-84 in tensor_open_problems_v1.md.

### P31 — Secant Variety Geometry (Algebraic-Geometric Tensor Decomposition)
**Move:** Embed tensors into projective space via Segre / Veronese / Segre-Veronese embedding; rank-r tensors form the r-th secant variety σ_r; identifiability and decomposition uniqueness reduce to non-defectivity of σ_r; defining equations of σ_r give rank-detection certificates.
**Exemplar:** Alexander-Hirschowitz theorem (generic Waring rank). Landsberg-Ottaviani Young flattenings (defining equations of σ_r). Salmon problem (defining equations of σ_4 in 4×4×4). Kruskal's theorem on CP identifiability via column ranks.
**Computation:** Macaulay2 SecantVarieties package; Bertini / HomotopyContinuation.jl numerical AG; Schubert calculus for enumerative invariants.
**Tools:** Macaulay2, Bertini, HomotopyContinuation.jl, Sage, Singular.
**Prometheus:** Substrate-friendly because (a) defining equations are EXPLICIT polynomial certificates auditable by substrate-tester, (b) Terracini's lemma reduces dim-of-secant-variety to a tangent-space computation, (c) generic-rank facts become anchors per HARD-4. The substrate's identifiability discipline can directly use σ_r geometry.
**Tactics:** Segre / Veronese / Segre-Veronese embedding | Terracini's lemma | Young flattenings | Schubert calculus | Newton-polytope / cohomological dimension counts | Apolar-scheme-based equations
**Distinction from P29 (Border Apolarity):** P29 uses apolar 0-d schemes (combinatorial / scheme-theoretic). P31 uses secant varieties (continuous / variety-theoretic). The two paradigms are dual frameworks for the same underlying decomposition problem; either can give a lower bound the other can't.
**Distinction from P15 (Tensor and Multilinear):** P15 is the "do the decomposition" task. P31 is the "geometry of all possible decompositions" task. Decomposition vs moduli.
**Catalog refs:** Open problems #5, #18, #21, #26-35, #38-42 in tensor_open_problems_v1.md.

---

## Tensor-paradigm cross-cutting observations

P27-P31 share characteristics distinct from P01-P26:

- **All five are "young" paradigms** by mathematical-history standards. P27 is ~10 years old in its modern form (Croot-Lev-Pach 2017); P28 is the oldest at 40 years (Strassen 1986); P29 is ~15 years old (Buczyńska-Buczyński 2010s); P30 emerged from physics (DMRG 1992) but became a math paradigm later; P31 has classical roots (Severi 1900, Veronese; Terracini 1911) but the modern computational form is post-2000. **Mathematicians have not had centuries to noodle over them; tools are emerging fast.**

- **All five have rich computational hooks.** Unlike P01-P26 which are sometimes purely conceptual, every tensor paradigm has a corresponding software ecosystem: Sage / Macaulay2 (P27, P29, P31); explicit functional codes (P28); ITensor / TenPy (P30); Bertini / HomotopyContinuation.jl (P31). This makes them substrate-grade.

- **All five touch NP-hard problems.** P30 contains #P-hard problems (PEPS contraction); P29 / P31 give bounds on NP-hard rank decisions; P27 attacks NP-hard combinatorial extremal problems; P28 sits adjacent to undecidable questions (rank decidability over ℚ).

- **The asymptotic spectrum (P28) is the meta-organizer.** P29 and P31 produce monotones; P27 produces a specific monotone (slice rank); P30 produces approximation theorems. P28 unifies them under a single framework.

Effective canonical count: **31 paradigms (P20 still removed; 30 active)**. P22-P26 from earlier 2026-05-08 round, P27-P31 from this tensor-specific round.

— Aporia, 2026-05-08

# Noesis v2 — Strategy and Research Plan

**Owner:** Aletheia (Structural Mathematician, Claude Opus)
**Created:** 2026-03-29
**Last Updated:** 2026-03-29 (post-council-mining-response)

## The Problem (confirmed)

The current concept tensor is 95 concepts × 30 hand-scored floats. Dimensions like "surprise_potential" and "explanatory_depth" are exactly the shallow encoding the council diagnosed. It clusters by vibes (associative proximity), not by structural bridgeability. The 3.4x result is real but measures co-occurrence patterns inherited from human intuition, not compositional architecture.

Meanwhile, `the_maths/` has 191 files with ~1,714 operations — a broad brush of mathematical traditions from Feynman diagrams to Yoruba arithmetic. These operations are computationally valid but encoded into the tensor through the same shallow feature scheme. The operations themselves are the raw material; the encoding is the bottleneck.

## The Thesis

Somewhere beneath all of mathematics there is a small set of structural primitives — things like "symmetry," "conservation," "composition," "fixed point," "duality" — that are not human constructs but reflections of how the universe actually works. Physical law gives us the most empirically verified access to these primitives. If we can trace the lineage from fundamental physics equations up through bridge mathematics and into pure structure, we build a tensor that encodes *what things do* rather than *what they're called*.

The danger: both James (human bias) and Claude (training-weight bias) will be tempted to impose meaning, narrative, and false structure. The antidote is empirical verification at every step — can this relationship be computationally tested? Does the math actually check out?

## Phase 0: Ascend to the Frontier (Research)

Before we build anything, we need to understand what already exists and what tools are available. This is the "ascend to the frontier" step we've done for every pillar.

### 0.1 Survey: Formula Genealogy / Mathematical Lineage

**Goal:** Find who has already traced structural relationships between equations.

**Research targets:**
- Noether's theorem and its extensions — the symmetry → conservation genealogy
- John Baez's Rosetta Stone program (n-Category Café, "Physics, Topology, Logic and Computation: A Rosetta Stone")
- The Langlands program (toy computable cases — modularity theorem)
- Buckingham pi theorem / dimensional analysis as structural constraint
- Wigner's "unreasonable effectiveness" — what does it mean computationally?
- Tegmark's mathematical universe hypothesis (what's operationalizable vs speculative)
- Spivak's "Ologs" (ontology logs — categorical knowledge representation)
- The Topos Institute / AlgebraicJulia ecosystem (categorical data structures in code)

**Deliverable:** Annotated bibliography with "what's computable" assessment for each.

### 0.2 Survey: Python Libraries for Precision Mathematics

**Goal:** Find tools that can work with these equations at the precision level of a physicist, not an LLM.

**Candidates to evaluate:**

| Library | What It Does | Why It Matters |
|---------|-------------|----------------|
| **SymPy** | Symbolic mathematics | Exact manipulation of equations, not floating point. Can verify algebraic identities, compute symmetries, derive conservation laws. The foundation. |
| **SageMath** | Comprehensive math system | Category theory support, algebraic geometry, number theory. Wraps GAP (group theory), Singular (commutative algebra), PARI (number theory). |
| **galgebra** | Geometric/Clifford algebra | Connects to pseudo_riemannian.py, clifford_algebra.py. Exact multivector operations. |
| **QuTiP** | Quantum mechanics | Precise quantum state manipulation, Hamiltonians, time evolution. Connects to schrodinger, dirac, spin_foam. |
| **PyDSTool** | Dynamical systems | Bifurcation analysis, continuation, stability. Connects to dynamical_systems operations. |
| **SciPy.special** | Special functions | Bessel, Legendre, hypergeometric — the building blocks of physics solutions. |
| **mpmath** | Arbitrary precision arithmetic | When float64 isn't enough. Zeta functions, L-functions, hypergeometric series to arbitrary precision. |
| **NetworkX** | Graph theory | For encoding mathematical lineage as actual graphs — who derives from whom. |
| **catlab (Julia)** | Computational category theory | AlgebraicJulia's categorical data structures. May need Julia interop or port concepts. |
| **Lean4 / mathlib** | Formal proof library | 100,000+ formalized mathematical statements. Ground truth for what implies what. |

**Deliverable:** For each library — install test, capability assessment, coverage of our equation domains. Which libraries can we actually use to *verify* structural claims rather than trusting LLM assertions?

### 0.3 Survey: Existing Mathematical Knowledge Bases

**Goal:** Don't reinvent what's already structured.

**Targets:**
- **OEIS** (Online Encyclopedia of Integer Sequences) — already partially integrated
- **Lean mathlib** — 100K+ formal proofs with explicit dependency graphs
- **Mizar Mathematical Library** — 60K+ formal theorems
- **OpenMath** content dictionaries — standardized mathematical semantics
- **nLab** — community wiki on higher category theory and physics (structured but not machine-readable)
- **Wolfram MathWorld** — extensive but not structurally encoded
- **DLMF** (Digital Library of Mathematical Functions) — NIST standard reference for special functions with explicit relationships

**Deliverable:** Assessment of which sources provide *structural* relationships (dependencies, derivations, symmetries) vs just descriptions.

## Phase 1: Mine the Ground Truth (The Grind)

### 1.1 The Physical Ground Category

Start with ~60 fundamental equations that describe the physical universe from quantum to cosmic. For each equation, extract (using SymPy for precision, verified by hand/reference):

- The equation itself (symbolic, exact)
- What physical quantities go in and come out (typed I/O)
- What symmetries it has (via Noether where applicable)
- What conservation law it implies or derives from
- What breaks when you remove a term (perturbation / failure signature)
- What other equations it derives from or implies (genealogy)
- What mathematical structures it requires (Hilbert space, manifold, group, etc.)

**The iterative cycle:**
```
1. Gather: Pull equation from reference (textbook, DLMF, Lean mathlib)
2. Encode: Express in SymPy (exact symbolic form)
3. Test: Verify known identities, limits, special cases computationally
4. Extract: Derive structural properties programmatically where possible
5. Review: Cross-check against multiple references
6. Repeat: Move to next equation, trace lineage connections
```

**Not:** Ask an LLM to describe the equation's properties and trust the output.
**Instead:** Use SymPy to *compute* the properties and verify them.

Example verification cycle for Schrödinger equation:
```python
import sympy as sp
# Define symbolically
psi, V, hbar, m, t, x = sp.symbols('psi V hbar m t x')
# Time-dependent: i*hbar * d(psi)/dt = -hbar^2/(2m) * d2(psi)/dx2 + V*psi
# Verify: is it linear? (superposition principle)
# Test: psi1 + psi2 satisfies if psi1 and psi2 each satisfy
# Verify: probability conservation (unitary evolution)
# Verify: energy conservation (time-translation symmetry via Noether)
# Extract: required structures (Hilbert space, Hermitian operator)
# Trace: derives from Hamiltonian mechanics via canonical quantization
```

### 1.2 Bridge Mathematics

The math that connects physics to pure structure:
- Lie groups → symmetry groups in physics
- Variational calculus → Lagrangian → Euler-Lagrange → optimization
- Spectral theory → quantum operators → linear algebra eigenproblems
- Differential geometry → GR → topology
- Information theory → statistical mechanics → computation
- Noether's theorem itself as the master bridge

For each bridge, trace the actual derivation — not "these are related" but "here is the functor / the mapping / the derivation chain."

### 1.3 Pure Structural Domains

Category theory primitives, type theory, algebraic topology, number theory. These don't connect to physics (yet) but have rich internal structural relationships that are independently verifiable.

## Phase 2: Design the Schema (Emerges from the Mining)

The schema should emerge from what we actually find in Phase 1, not be designed a priori. The council gave us candidate dimensions (I/O signatures, invariance vectors, failure fingerprints, causal roles, morphism signatures). Phase 1 tells us which of these are actually extractable and which are aspirational.

**Key question Phase 1 answers:** What is the actual primitive? Is it symmetry? Is it composition? Is it something we don't have a word for yet?

## Phase 3: Build the Tensor (Code)

Only after Phase 1 and 2. Build the encoding, the multi-lens search, the cross-type bridges. This is where the DuckDB schema, the tensor population, and the disagreement scoring come in.

---

## BREAKTHROUGH: ChatGPT's Transformation Primitive Basis (2026-03-29)

The council mining prompt returned a massive response. ChatGPT went 7 layers deep unprompted, producing:

1. **20 derivation chains** in JSON schema with typed transformations, invariants, failure modes
2. **A canonical transformation ontology** — 20 typed transformation labels (MAP, LIFT, REDUCE, LIMIT, LINEARIZE, VARIATIONAL, DUALIZE, REPRESENT, QUANTIZE, DISCRETIZE, etc.)
3. **A minimal generating basis claim:** 10 primitives that can compose to generate ALL mathematical transformations:
   - COMPOSE, MAP, EXTEND, REDUCE, LIMIT, DUALIZE, LINEARIZE, STOCHASTICIZE, SYMMETRIZE, BREAK_SYMMETRY
4. **Decomposition proofs:** QUANTIZE = MAP + EXTEND, VARIATIONAL = EXTEND + REDUCE + LIMIT, DISCRETIZE = REDUCE + BREAK_SYMMETRY, etc.
5. **Differentiable interpreter architecture** — each primitive as a differentiable operator
6. **Cross-chain alignment tensors** — bridge scoring via invariant/transformation/failure similarity
7. **Bootstrapping curriculum** — levels from algebraic closure through conservation laws to variational principles

**Status:** UNVERIFIED. This is model output. Aletheia's primary task is now to verify, correct, and extend this structure using SymPy and formal references.

**Key question:** Is the 10-primitive basis actually minimal and complete? This is testable.

---

## Immediate TODO (active)

### COMPLETED (2026-03-29)
- [x] Install and test SymPy, mpmath, networkx — all installed, SymPy 1.14.0
- [x] SymPy capability assessment — full report at `sympy_capability_report.md`
- [x] Frontier survey — 10 sections covering adjacent work, tools, papers (`research_findings.md`)
- [x] Council mining prompt sent, responses received (`council_prompt_mining_structural_primitives_response.md`)
- [x] Claude primary extraction — Noether tree, 6 derivation chains, 15 isomorphisms, 10 primitives (`claude_extraction_structural_primitives.md`)
- [x] Aletheia role created with responsibilities (`roles/StructuralMathematician/`)

### COMPLETED — Verification of ChatGPT Transformation Basis (2026-03-29)
- [x] Chains 1-3 verified in SymPy (22 tests, 20 pass, 2 informative failures)
- [x] Chains 4-10 verified in SymPy (45 tests, 45 pass)
- [x] Chains 11-20 verified in SymPy (72 tests, 72 pass)
- [x] COMPLETE primitive hypothesis tested (13 tests, 13 pass across 6 fields)
- [x] NetworkX graph built (78 nodes, 60 edges, 2 cross-chain bridges found)
- [x] Primitive basis synthesis: 11 primitives proposed (cross-council comparison)
- [x] Decompositions verified: QUANTIZE, VARIATIONAL, DISCRETIZE, RENORMALIZATION all pass
- [x] Decompositions corrected: REPRESENT = MAP (not MAP + LINEARIZE)
- [x] New primitive discovered: COMPLETE (uniquely determined extension under constraint)
- **TOTAL: 152 tests, 150 pass, 2 failures → both led to discoveries**

### COMPLETED — Cross-Council Synthesis (2026-03-29)
- [x] Claude's 11 primitives compared to ChatGPT's 10 — synthesis at `primitive_basis_synthesis.md`
- [x] Claude's extras (Fixed Point, Adjunction, Exactness, Localization, Fibration, Recursion) analyzed as derivable
- [x] Adjoint pairs identified: (EXTEND,REDUCE), (SYMMETRIZE,BREAK_SYMMETRY)
- [x] Graph analysis: MAP dominates (33%), 9 ontology types unused → mining gaps identified

### COMPLETED — Decomposition Test (2026-03-29, per Athena directive)
- [x] **ITEM 1 (CRITICAL):** 60/60 stratified sample decomposes into 11 primitives (100%). Basis is load-bearing.
- [x] Two-level architecture discovered: MAP/REDUCE dominate intra-domain (nodes), rare primitives dominate inter-domain (edges). Same vocabulary, two organizational levels.
- [x] Athena feedback synthesized: ejection circuit collapses transformation sequences to terminal states; chains feed Noesis not Ignis directly; constrain council for rare primitives
- [x] Constrained council prompt written: `council_prompt_rare_primitives.md` — 20 chains targeting DUALIZE, LINEARIZE, SYMMETRIZE, BREAK_SYMMETRY, STOCHASTICIZE

### COMPLETED — Rare Primitive Mining (2026-03-29)
- [x] Constrained council prompt sent and responses received (80 chains from 4 Titans + 5 COMPLETE chains + 10 composition patterns from ChatGPT followup)
- [x] ChatGPT proposed expanding to 16-18 primitives — analyzed and rejected (ADJOIN=meta-structure, REPRESENT=MAP, CORRESPOND=DUALIZE, DISCRETIZE=REDUCE+BREAK_SYMMETRY, THERMALIZE=STOCHASTICIZE+LIMIT). GLUE tracked as candidate.
- [x] Composition patterns analyzed — 14 named constructions as primitive sequences. Key finding: order matters (non-commutative), COMPLETE/BREAK_SYMMETRY are terminal, EXTEND is initiatory, MAP is universal connector.
- [x] ChatGPT followup delivered: 4 expanded thin chains with full equations, 5 COMPLETE-dominant chains, 10 cross-primitive interaction patterns
- [ ] Verification of expanded + COMPLETE chains running (background agent)

### COMPLETED — Move 1: DuckDB Schema + Data Load (2026-03-29)
- [x] Schema designed and built: operations, chains, chain_steps, transformations, compositions tables
- [x] 1,714 operations loaded with auto-classified primitives (MAP: 905, REDUCE: 691, COMPOSE: 60, LINEARIZE: 40, DUALIZE: 18)
- [x] 20 verified chains loaded: 80 steps, 60 typed edges
- [x] Database live at `noesis/v2/noesis_v2.duckdb` (2.8 KB)

### COMPLETED — Move 2: Search Algorithm (2026-03-29)
- [x] Typed chain search operational: `noesis/v2/search.py`
- [x] 1,533,012 type-compatible cross-domain pairs in search space
- [x] Composition template matching against 14 verified patterns
- [x] Cross-domain connectivity matrix queryable
- [x] Specific domain-pair probes working (e.g. Feynman → TDA)

### COMPLETED — Ethnomathematics Ingestion + Independent Classification (2026-03-29)
- [x] 153 ethnomathematical systems ingested from council (Gemini + ChatGPT)
- [x] Provenance columns added: council labels vs Noesis labels vs agreement
- [x] Vector classifier built (scores all 11 primitives simultaneously, not cascade)
- [x] Independent agreement rate: 74.8% (non-circular — honest number)
- [x] Disagreement analysis: COMPOSE vs MAP is least sharp boundary (18% of confusions)
- [x] Primitive vectors computed for all 153 systems
- [x] Cross-tradition clustering: muqarnas↔Navajo, Ethiopian mult↔Aboriginal kinship, Thabit↔Shona fractals
- [x] Methodology note on circularity documented
- [x] Athena feedback: fix cascade classifier, tropical algebra misclassified in both directions, p-adic is COMPLETE not LIMIT

### ACTIVE — Move 3: Refinement + Flywheel Connection
- [ ] Refine template scoring (REDUCE→MAP too broad, needs primitive-pair specificity)
- [ ] Load 80 rare-primitive chains from council (verified batch) to increase edge density
- [ ] Build composition candidate → reasoning problem generator
- [ ] Connect to Forge ensemble for scoring
- [ ] Define ground-truth test pairs for search validation
- [ ] RLVF integration: typed compositions as training signal

---

## Principles

1. **Mine before you model.** The schema comes from the data, not the other way around.
2. **Compute, don't assert.** If a structural property can be verified computationally, verify it. Don't trust LLM descriptions of mathematical relationships.
3. **Trace lineage, don't cluster.** We're building a genealogy (who derives from whom), not a similarity search (who looks like whom).
4. **Physical law as constraint, not truth.** Physics provides empirically verified structural constraints. Use it to reject invalid bridges, not to define all valid ones.
5. **Precision over breadth.** 50 equations with verified structural signatures beats 1,714 operations with vibes-based features.
6. **The primitive may surprise us.** Don't assume we know what the fundamental structural unit is. Let it emerge from the mining.
7. **Disagreement is signal.** When different structural lenses disagree about a relationship, that's where discovery lives.

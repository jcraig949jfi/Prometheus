# Noesis v2 — Research Findings: What Exists at the Frontier

*Compiled 2026-03-29. Research into what's been built, what's available, what's adjacent.*

---

## 1. Mathematical Knowledge Graphs (Who's Built What)

### MMLKG (Mizar Mathematical Library Knowledge Graph)
- **What:** Knowledge graph of mathematical definitions, statements, and proofs from the Mizar formal library
- **Structure:** Neo4j graph database with semantic relationships between mathematical entities
- **Access:** Public Neo4j Browser endpoint at https://mmlkg.uwb.edu.pl/
- **Published:** Nature Scientific Data, 2023
- **Relevance:** HIGH. This is the closest thing to a structured mathematical knowledge base with actual derivation relationships. Built from formal proofs, so the relationships are verified, not inferred.
- **Limitation:** Covers Mizar library scope. Not physics-focused. Relationships are proof dependencies, not structural isomorphisms.

### AutoMathKG (2025)
- **What:** Automated mathematical knowledge graph using LLMs + vector database
- **Structure:** Directed graph of Definition → Theorem → Problem entities with reference edges
- **Data:** Integrates ProofWiki, textbooks, arXiv papers, TheoremQA
- **Paper:** arXiv:2505.13406
- **Relevance:** MEDIUM. Uses LLM embeddings (SBERT) for similarity — exactly the shallow approach we're trying to move beyond. But the graph structure (Definition → Theorem derivation chains) is useful raw data.
- **Limitation:** Embedding-based similarity is what our council diagnosed as insufficient.

### Mathematical Derivation Graphs (2024)
- **What:** Dataset of 107 STEM manuscripts with 2,000+ manually labeled inter-equation dependency relationships
- **Paper:** arXiv:2410.21324
- **Structure:** DAGs where nodes = equations in a paper, edges = "derived from"
- **Relevance:** MEDIUM-HIGH. This is someone doing exactly what we need — extracting derivation chains from papers. Their best LLM achieves only 45-52% F1 on this task, confirming it's genuinely hard and LLMs struggle with it.
- **Limitation:** Intra-paper derivations only (how equations derive within one manuscript). We need cross-paper, cross-field structural relationships.

### Applied Math Knowledge Graph (2024)
- **What:** KG for models and algorithms in applied mathematics
- **Paper:** arXiv:2408.10003
- **Relevance:** LOW-MEDIUM. Focuses on applied/computational math (algorithms, models), not fundamental equation structure.

---

## 2. The Baez Rosetta Stone

### Paper
- **Title:** "Physics, Topology, Logic and Computation: A Rosetta Stone"
- **Authors:** John C. Baez and Mike Stay
- **Published:** arXiv:0903.0340 (2009), in Lecture Notes in Physics vol. 813, Springer 2011
- **Full PDF:** https://math.ucr.edu/home/baez/rosetta.pdf
- **Key insight:** Symmetric monoidal categories provide a unified framework: a linear operator behaves like a cobordism, which behaves like a proof, which behaves like a computation.

### The Four-Way Correspondence
| Physics | Topology | Logic | Computation |
|---------|----------|-------|-------------|
| Hilbert space | manifold with boundary | proposition | data type |
| operator | cobordism | proof | program |
| composition of operators | gluing cobordisms | cut elimination | function composition |
| tensor product | disjoint union | conjunction (∧) | product type (×) |
| unit | empty manifold | true (⊤) | unit type |

### Computational Status
- **Theory:** Well-established. The categorical framework is rigorous.
- **Code:** NOT directly implemented as a searchable system. The Rosetta Stone is a paper, not software.
- **Closest implementation:** Catlab.jl (see below) implements the categorical structures but doesn't implement the physics↔logic↔computation mappings explicitly.

### Relevance to Noesis
EXTREMELY HIGH. This is the theoretical backbone for what our council recommended — morphism signatures and cross-type bridges. The question is: can we operationalize it into a tensor?

---

## 3. Computational Category Theory Tools

### Catlab.jl (AlgebraicJulia)
- **Repo:** https://github.com/AlgebraicJulia/Catlab.jl
- **Language:** Julia (NOT Python)
- **Status:** Active development as of March 2026
- **Features:** Categories, functors, natural transformations, limits/colimits, wiring diagrams (string diagrams), monoidal categories, C-sets, double pushout rewriting
- **GATlab:** Newer sub-project for generalized algebraic theories
- **Relevance:** HIGH for understanding what categorical computation looks like in practice. LOW for direct integration (Julia, not Python).
- **Action item:** Study their categorical data structures. May need to port concepts, not code.

### Python Category Theory
- No mature Python equivalent of Catlab. Scattered implementations exist but nothing comprehensive.
- **Action item:** May need to build minimal categorical primitives ourselves.

---

## 4. Lean Mathlib Dependency Graph

### Tools Available
- **lean-graph** (GitHub: patrik-cihal/lean-graph) — Automatic extraction and visualization of theorem dependency graphs in Lean4
- **LeanDepViz** (GitHub: cameronfreer/LeanDepViz) — Dependency visualization with JSON export (declaration names, module paths, kinds, metadata). Filters for practical graph sizes (hundreds-thousands of nodes instead of millions).
- **importGraph** — Official Lean community tool for import structure analysis
- **KnowTeX** (arXiv:2601.15294, Jan 2026) — Visualizing mathematical dependencies

### What's Exportable
- Full dependency graph is exportable to JSON
- Can be loaded into Neo4j for graph analysis
- Mathlib4 has ~170,000+ declarations as of 2025

### Relevance
HIGH for Phase 1 mining. The dependency graph IS a derivation tree — it tells you exactly which lemmas/theorems are required to prove which other theorems. This is ground truth for mathematical lineage.

**Action item:** Export a subgraph focused on physics-relevant mathematics (group theory, differential geometry, measure theory, topology) and analyze the structural patterns.

---

## 5. NIST DLMF (Digital Library of Mathematical Functions)

### Structure
- 36 chapters covering special functions (Bessel, Legendre, hypergeometric, etc.)
- Includes: definitions, series expansions, integrals, connection formulae, asymptotics, special values
- Internal cross-references between functions (connection formulae!)
- Math-based search engine

### Structured Data
- **DLMF Dataset** (GitHub: abdouyoussef/math-dlmf-dataset) — Per-expression dataset with structured labels at fine granularity. For each math expression: contextual elements and annotations, organized as marked-up sentences within hierarchical structure.
- NIST is exploring ontologies for machine-readable metadata but this is in-progress, not complete.

### Relevance
MEDIUM-HIGH for special functions and their inter-relationships. The connection formulae are exactly the kind of structural bridge we want (e.g., Bessel functions expressed in terms of hypergeometric functions). Limited to special functions — doesn't cover physics equations or algebraic structures.

---

## 6. Spivak's Ologs

### Paper
- **Title:** "Ologs: A Categorical Framework for Knowledge Representation"
- **Published:** PLOS ONE, 2012 (arXiv:1102.1889)
- **Authors:** David Spivak, Robert Kent

### What It Is
An olog is a category used as a knowledge representation:
- Objects = types (labeled with noun phrases)
- Morphisms = relationships (labeled with verb phrases)
- Functors between ologs = alignments between knowledge domains
- Very similar to a relational database schema but grounded in category theory

### Implementation Status
- Theoretical framework is clean and well-defined
- NO mature software implementation found in Python
- Spivak's later work (polynomial functors) goes deeper but also lacks tooling
- The concept is implementable — it's essentially a typed directed graph with composition rules

### Relevance
HIGH conceptually — ologs are designed for exactly our use case (representing knowledge about mathematical structures in a way that supports structural comparison). LOW practically — we'd need to build the tooling.

---

## 7. SymPy Physics Capabilities (Pre-Test Assessment)

### Available Modules
- `sympy.physics.mechanics` — Lagrangian/Hamiltonian mechanics, Kane's method
- `sympy.physics.quantum` — Quantum operators, commutators, spin, Hilbert spaces
- `sympy.physics.vector` — Reference frames, vector calculus
- `sympy.physics.units` — Dimensional analysis, unit systems
- `sympy.physics.optics` — Basic optics
- `sympy.diffgeom` — Differential geometry (manifolds, metrics, connections)
- `sympy.categories` — Basic category theory (categories, morphisms, diagrams)
- `sympy.liealgebras` — Lie algebras (root systems, Weyl groups, Cartan matrices)

### Key Question (Awaiting Test Results)
Can SymPy actually:
1. Derive conservation laws from Lagrangian symmetries? (Noether computation)
2. Express and verify Maxwell's equations symbolically?
3. Compute Lie symmetries of PDEs?
4. Express GR curvature tensors?

*Background agent testing this now.*

---

## 8. What Doesn't Exist (The Gap We're Filling)

After this survey, the gap is clear:

**Nobody has built a computationally searchable tensor/graph of structural relationships between mathematical equations across domains, anchored in empirically verified properties (symmetries, conservation laws, derivation chains, failure modes), designed for compositional bridge discovery.**

What exists:
- Proof dependency graphs (Lean mathlib, MMLKG) — structural but only within formal proof systems
- Derivation extraction from papers — but intra-paper only, and LLMs struggle (45% F1)
- Category theory frameworks (Catlab) — the right language but not applied to this problem
- Special function relationships (DLMF) — narrow domain
- LLM-based knowledge graphs (AutoMathKG) — shallow embedding approach

What's missing:
- Cross-domain structural bridges (physics ↔ algebra ↔ topology ↔ computation)
- Failure fingerprints as structural signatures
- Noether-tree-style genealogy as a searchable graph
- Operational signatures (I/O types, invariants, constraints) for mathematical concepts
- Multi-lens disagreement scoring for novelty detection

**This is genuinely novel territory. The closest prior work is Baez's Rosetta Stone (theoretical) and MMLKG (data). Nobody has combined them.**

---

## 9. Recommended Reading List (Priority Order)

1. **Baez & Stay, "Physics, Topology, Logic and Computation: A Rosetta Stone"** — https://math.ucr.edu/home/baez/rosetta.pdf — THE theoretical foundation. Read first.
2. **Spivak, "Ologs: A Categorical Framework for Knowledge Representation"** — arXiv:1102.1889 — the knowledge representation framework
3. **Mathematical Derivation Graphs** — arXiv:2410.21324 — closest to our equation lineage extraction task
4. **MMLKG paper** — Nature Scientific Data 2023 — what a formal mathematical knowledge graph looks like
5. **Catlab.jl documentation** — https://algebraicjulia.github.io/Catlab.jl/dev/ — what computational category theory looks like in practice
6. **DLMF Dataset** — GitHub: abdouyoussef/math-dlmf-dataset — structured mathematical function data
7. **LeanDepViz** — GitHub: cameronfreer/LeanDepViz — for exporting theorem dependency graphs

---

## 10. Available Python Libraries (Confirmed Installed)

| Library | Version | Status |
|---------|---------|--------|
| sympy | (installed) | Ready — symbolic math, physics modules, Lie algebras, categories |
| mpmath | 1.3.0 | Ready — arbitrary precision arithmetic |
| networkx | 3.6.1 | Ready — graph structures for equation lineage |
| numpy | (installed) | Ready — tensor operations |
| scipy | (installed) | Ready — special functions, integration, linear algebra |

### To Evaluate/Install
- `galgebra` — geometric algebra (pip install galgebra)
- `qutip` — quantum mechanics (pip install qutip)
- `pydstool` — dynamical systems
- `sage` — comprehensive math (heavy install, may need separate environment)

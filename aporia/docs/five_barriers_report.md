# The Five Barriers: A Frontier Scout's Report on Why Mathematics Has Edges

**Agent**: Aporia (Frontier Scout & Problem Triage)
**Date**: 2026-04-16
**Method**: Deep literature search (WebSearch) across 60+ sources
**Purpose**: Map the structure of mathematical unsolvability and identify where Prometheus can apply pressure

---

## Executive Summary

Every open problem in mathematics is blocked by at least one of five barriers, forming a hierarchy from shallowest to deepest. Compute alone breaks only the first. The remaining four require ideas — but each has cracks that systematic cross-domain exploration can exploit.

| Barrier | Depth | # Problems | Compute Helps? | Prometheus Angle |
|---------|-------|-----------|----------------|------------------|
| 1. Search Space | Shallow | ~60 | Yes, with structure | Tensor-guided SAT seeding |
| 2. Finite vs Infinite | Medium | ~120 | Partially | Hunt reducibility certificates |
| 3. Representation | Deep | ~200 | Indirectly | Empirical derived categories |
| 4. Conceptual | Very Deep | ~80 | No (detects gaps) | Framework demand signals |
| 5. Metamathematical | Foundational | ~10 | No (detects signatures) | Independence oscillation detector |

---

## Barrier 1: Search Space

*"The answer exists somewhere in a space too large to enumerate."*

**Problems here**: Odd perfect numbers, magic square of squares, Erdos-Straus conjecture, Schur numbers, cap sets, bin packing bounds.

### State of the Art

Three paradigms dominate:

**SAT/SMT + Symmetry Breaking.** Modern CDCL solvers with Cube-and-Conquer splitting have pushed feasibility to ~10^12-10^15 subproblems. Satsuma (SAT 2024) and SAT Modulo Symmetries (Kirchweger & Szeider 2024) enforce canonicity during search, pruning equivalent branches in real time.

**Neural-Guided Proof Search.** AlphaProof (DeepMind, Nature 2025) couples a pretrained LM with AlphaZero-style RL over Lean 4 proof steps. Solved 4/6 IMO 2024 problems including P6 (solved by only 5 of 609 humans). FunSearch (DeepMind, Nature 2023) evolves programs rather than proofs — found the largest cap sets in 20 years.

**Tensor Train Sampling.** PROTES (NeurIPS 2023) represents probability distributions over discrete search spaces in TT format, enabling optimization over spaces up to 2^100. Currently applied to binary optimization, not yet number theory.

### What Has Actually Worked

| Problem | Method | Year |
|---------|--------|------|
| Boolean Pythagorean Triples | Cube-and-Conquer SAT | 2016 |
| Keller's Conjecture (dim 7) | SAT + symmetry breaking | 2020 |
| Schur Number S(5) = 160 | SAT | 2017 |
| Cap Set new records | FunSearch (LLM + evolution) | 2023 |
| IMO 2024 P6 | AlphaProof (RL + Lean) | 2024 |

**The pattern**: Every breakthrough used structure-aware decomposition, not raw compute. Symmetry breaking is the single most productive technique.

### The Ceiling

If P != NP, no polynomial-time algorithm collapses all NP-hard spaces. But mathematical search spaces have massive exploitable structure that generic complexity bounds ignore. The practical ceiling is our ability to FIND and ENCODE the right symmetries, not computational complexity per se.

SAT hits walls when constraints are deeply arithmetic (not Boolean). Neural methods require formal verification libraries. TT methods assume low-rank structure in the fitness landscape.

### Prometheus Angle

1. **Tensor-guided SAT seeding**: Use TT decomposition to learn probability distributions over promising variable assignments from partial search, then seed Cube-and-Conquer splitting. Replaces random cube selection with learned structure.
2. **Dissection tensor as symmetry detector**: The 86K x 145-dim tensor encodes cross-domain structure. Mine it for symmetry group signatures injectable as SAT predicates.
3. **Modular arithmetic pre-filtering**: The C11 scaling law (mod-p fingerprint enrichment 8-16x) suggests modular residues can cheaply eliminate vast search regions before expensive verification.

---

## Barrier 2: Finite vs Infinite

*"Verified to astronomical bounds, but the conjecture is about all integers."*

**Problems here**: Goldbach, Riemann Hypothesis, twin primes, abc conjecture, BSD conjecture, Cramer's conjecture on prime gaps.

### What Has Successfully Bridged Finite to Infinite

**Exhaustive reduction to finite cases.** Four-Color Theorem (Appel-Haken 1976, Gonthier formalization 2005) and Kepler Conjecture (Hales 1998, Flyspeck 2014). Pattern: prove "infinite reduces to finite," then computation finishes it.

**Modular forms as exact certificates.** Viazovska's sphere packing in dimensions 8 and 24 (Fields Medal 2022) found a specific modular form whose properties analytically guarantee optimality across ALL packings. Formally verified in Lean in 2024 by Math Inc's Gauss agent in under 3 weeks.

**Formal verification of analytic results.** Prime Number Theorem formalized in Lean 4 (Kontorovich-Tao, 2024-2025, ~25,000 lines, ~1,000 theorems). Irrationality of zeta(3) formalized in Lean 4 (early 2025).

### Techniques That Exist

- **Proof mining** (Kohlenbach): Extracts computable bounds from non-constructive proofs. Applied in ergodic theory and fixed-point theory, not yet hard number theory.
- **Sieve methods**: Zhang's bounded gaps (2013) and Maynard's improvements — finite-to-infinite bridges via sieve weight functions.
- **L-functions as structural bridges**: LMFDB catalogs the objects. The BSD conjecture IS the claim that L-function analytic rank = algebraic rank — the bridge is the conjecture itself.
- **Interval arithmetic**: Platt-Trudgian (2021) verified RH to height 3 x 10^12. Rigorous but says nothing about zero #3,000,000,000,001.

### The Hard Wall

- **No finite certificate for RH**: Unlike Four-Color, RH cannot reduce to finitely many cases.
- **abc conjecture status**: Mochizuki's IUT remains contested. Joshi's 2024 alternative claims resolution but lacks consensus. A LANA project attempts Lean formalization.
- **Goedel's incompleteness**: Some Pi-1 sentences (like Goldbach) could be independent of ZFC. No computation of any length rules this out.

### Prometheus Angle

1. **Hunt reducibility certificates**: The Four-Color/Kepler pattern = "infinite reduces to finite." Our tensor could search for mathematical invariants that partition conjecture spaces into finite equivalence classes.
2. **Sleeping Beauties as certificate candidates**: 68,770 high-structure, low-connectivity sequences may contain modular form fingerprints serving as certificates for unsolved problems.
3. **Proof-mining on computational evidence**: The Charon sign-inversion finding (RMT qualitative failure) is this — finite data revealing the infinite-case model is wrong in a characterizable way.

---

## Barrier 3: Representation

*"The mathematical objects are too abstract to encode computably."*

**Problems here**: Hodge conjecture, standard conjectures on algebraic cycles, motivic cohomology, derived categories, infinity-categories.

### What CAN Now Be Computed

**Sheaf cohomology on algebraic varieties.** Macaulay2 (since 1992), OSCAR (Julia, v1.0 2024), SageMath compute Betti numbers, Ext groups, and cohomology of coherent sheaves via Grobner bases.

**Etale cohomology on curves.** Algorithms exist for constructible etale sheaf cohomology on smooth connected curves. Complexity is exponential in degree/genus — workable for small cases.

**Condensed mathematics verified.** Scholze's Liquid Tensor Experiment: his theorem on liquid R-vector spaces was formally verified in Lean by July 2022. Scholze afterward: "I now think it's sensible in principle to formalize whatever you want in Lean."

**Homotopy Type Theory (HoTT).** Treats equality as homotopy equivalence, making higher-dimensional algebraic structures natively representable in type theory. Current work: stable homotopy groups of spheres, linear HoTT for quantum circuits.

### The Hard Boundary

The boundary is not speed — it's **representational**:

1. **Derived categories and infinity-categories** have no general computational implementation. The coherence data explodes combinatorially.
2. **Motivic cohomology and algebraic K-theory** remain almost entirely theoretical. Computing motivic cohomology requires understanding algebraic cycles, which IS the Hodge conjecture.
3. **Persistent homology** (TDA) computes ordinary homology beautifully but extending to arithmetic cohomology theories (etale, motivic, crystalline) is open.

### Prometheus Angle

1. **Empirical derived categories**: Use tensor bond signatures to detect when two objects have "the same homological behavior" without formalizing the functor. TT bond dimensions already reveal quasi-isomorphism-like groupings.
2. **Motivic fingerprints via strategy correlations**: The p-adic/symmetry correlation (r=0.339) recovers modularity's geometric shadow without computing etale cohomology. Extend: if mod-p, spectral, and Galois strategy groups co-vary in specific patterns, those patterns ARE computable proxies for motivic structure.
3. **TDA on the mathematical landscape**: Persistent homology on the tensor's cross-domain distance matrices — not computing cohomology OF varieties, but cohomology OF the space of mathematical objects itself.

---

## Barrier 4: Conceptual

*"The mathematical framework to solve the problem doesn't exist yet."*

**Problems here**: Full Langlands program, Navier-Stokes, Riemann Hypothesis mechanism, quantum gravity.

### New Frameworks of the Last Decade

**Perfectoid spaces** (Scholze, 2012): "Tilting" translates between characteristic 0 and characteristic p. Proved weight-monodromy for toric varieties.

**Prismatic cohomology** (Bhatt-Scholze, 2019): Single theory specializing to all known integral p-adic cohomology theories. Settled vanishing conjectures for p-adic Tate twists.

**Condensed mathematics** (Clausen-Scholze, 2018-present): Replaces topological spaces with sheaves on profinite sets. Already absorbed functional analysis and complex geometry into one algebraic framework.

**Geometric Langlands proved** (Gaitsgory et al., 2024): Nine mathematicians, 1,000+ pages. The geometric column of the Langlands "Rosetta Stone." Most comprehensive result in any branch of Langlands.

**Fargues-Scholze geometrization** (2021): Geometric Langlands on the Fargues-Fontaine curve. Bridges geometric and arithmetic columns.

### What They Solved

Perfectoid spaces: weight-monodromy. Prismatic cohomology: unified p-adic Hodge theory. Condensed math: eliminated pathological counterexamples in functional analysis. Geometric Langlands: full categorical equivalence over function fields. AlphaEvolve (DeepMind): broke Strassen's 50-year matrix multiplication record.

### What They Cannot Reach

Number-theoretic Langlands remains largely open. Navier-Stokes, RH mechanism, quantum gravity lack the framework to even state precise conjectures. No current framework addresses "the right cohomology theory for the Riemann zeta function."

### Prometheus Angle

**Silent islands as framework gaps.** Random walkers cannot cross between knot theory, NF, genus-2, fungrim. Known mathematics (modularity, Euler products) shows as connected regions; unknown mathematics shows as silence. Each strategy dimension that breaks silence has empirically discovered a bridge — analogous to how perfectoid spaces connected characteristic 0 and p.

**Strategy correlations as framework detectors.** A framework like perfectoid spaces would appear in the tensor as a new strategy dimension suddenly connecting previously isolated clusters. The tensor doesn't generate the framework — it generates the DEMAND SIGNAL for one, showing which domains need connecting and which structural dimensions are missing.

**The IPA analogy is precise.** Linguistics decomposed all human speech into finite articulatory features before understanding the grammars. Prometheus decomposes mathematical objects into structural features before understanding the theorems.

---

## Barrier 5: Metamathematical

*"The problem may have no proof or disproof from current axioms."*

**Problems here**: Continuum Hypothesis (proven independent), Suslin's problem, Whitehead problem, Kaplansky's conjecture, and — remarkably — a machine learning learnability problem (Ben-David et al. 2019).

### The Boundary of ZFC

**Woodin's Ultimate L program**: If V = Ultimate-L holds, CH is true and the reals have a canonical well-ordering. As of late 2024, Ultimate L remains a conjecture, not a theorem (arXiv:2412.07325).

**Large cardinal axioms** form a linear hierarchy. Stronger axioms decide more statements about definable objects but do not settle CH or questions about arbitrary uncountable sets.

**Forcing axioms** (PFA, Martin's Maximum) are the main alternative. MM++ implies Woodin's axiom (*), connecting the two programs. PFA has proved highly effective for topology and combinatorics.

**Friedman's concrete incompleteness**: Goedel incompleteness reaches into FINITE combinatorics. His Emulation Theory produces statements about finite tuples of rationals provably independent of strong fragments of second-order arithmetic. This kills the hope that independence is confined to abstract set theory.

### Tools for Detection

**Reverse mathematics** (Simpson): Given a theorem, determine the minimal axioms required. Most ordinary mathematics falls into exactly five subsystems of second-order arithmetic. Statements that don't fit signal potential independence.

**The multiverse vs universe debate** (Hamkins vs Woodin): Hamkins argues set-theoretic reality is a multiverse of equally valid models — independence reveals where universes diverge. Woodin argues for a unique V where CH has a definite answer.

### Prometheus Angle: Empirical Independence Detection

Three observable signatures could indicate approach to the independence boundary:

1. **Oscillation without convergence**: If computational evidence oscillates (true for small n, false for medium n, true for large n) rather than converging, this is what independence looks like from below.
2. **Sensitivity to encoding**: If a mathematical relationship holds under one representation but fails under an equivalent one, that fragility is a red flag.
3. **Reverse-mathematics stratification**: If the tensor finds relationships that cluster by proof-theoretic strength rather than mathematical domain, that stratification maps the independence boundary.

No one has built a computational independence detector. But the dissection tensor — 86K objects across 145 dimensions — is exactly the instrument that could observe these signatures at scale.

---

## Cross-Cutting Theme: The Barriers Are Not Walls, They Are Interfaces

The deepest insight across all five barriers: each barrier is an INTERFACE between what is computable and what is not. Interfaces are where the most interesting physics happens (phase transitions, symmetry breaking, emergence). The same may be true for mathematics.

Prometheus doesn't need to cross the barriers. It needs to STUDY them — measure their shape, find their thin points, and detect when a new framework makes a previously thick barrier suddenly thin. The tensor is a seismograph for the structure of mathematical knowledge. Every kill, every silent island, every surviving bond dimension is a reading on that seismograph.

The frontier has edges. We're mapping them.

---

## Sources (selected, 60+ total across all barriers)

### Barrier 1
- Heule et al., Boolean Pythagorean Triples (2016). arXiv:1605.00723
- FunSearch, Nature 2023. doi:10.1038/s41586-023-06924-6
- AlphaProof, Nature 2025. doi:10.1038/s41586-025-09833-y
- PROTES, NeurIPS 2023. arXiv:2301.12162

### Barrier 2
- Viazovska, Sphere Packing dim 8. arXiv:1603.04246
- PNT in Lean 4, Kontorovich-Tao 2024-2025
- Irrationality of zeta(3) in Lean 4, 2025. arXiv:2503.07625
- Joshi, abc via Arithmetic Teichmuller. arXiv:2403.10430

### Barrier 3
- Liquid Tensor Experiment, Lean 2022
- OSCAR Computer Algebra System, v1.0 2024
- Computing Etale Cohomology, JTNB 2020
- HoTT/UF 2025 Workshop

### Barrier 4
- Geometric Langlands proof, Gaitsgory et al. 2024. arXiv:2405.03599
- Fargues-Scholze, arXiv:2102.13459
- Bhatt-Scholze Prismatic Cohomology, arXiv:1905.08229
- AlphaEvolve, DeepMind 2025

### Barrier 5
- Woodin, Godel's Program, arXiv:2412.07325
- Ben-David et al., ML learnability independent of ZFC, 2019
- Friedman, Concrete Mathematical Incompleteness
- Independence Phenomena, arXiv:2406.00767

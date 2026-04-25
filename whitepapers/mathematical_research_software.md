# Mathematical Research Software at the Frontier

## A field guide to the tools modern mathematicians actually use, why they exist, and what problems they solve

**Version 1.0 · 2026-04-25**

---

## Executive Summary

A century ago, mathematics needed a chalkboard and a notebook. Today, frontier mathematics needs a software stack. Every major recent result — the proof of Fermat's Last Theorem, the resolution of the Kepler conjecture, the verification of the Four-Color Theorem, the explicit class field theory used in modern cryptography, the experimental discovery of monstrous moonshine, the formal verification of the Liquid Tensor Experiment, the AlphaProof IMO silver-medal performance — was either enabled, certified, or outright produced by mathematical software.

The space of these tools is unfamiliar to most working scientists outside mathematics, in part because it is dominated by **open-source projects with small core teams** and **proprietary giants whose licenses cost as much as a research grant**. This white paper catalogs the tools shaping current research, organizes them by what mathematical problem they were designed to solve, and tabulates their economic and licensing structure.

**Headline observations.**

1. **Open source dominates frontier research.** Of the ~50 tools cataloged here, ~80% are open source. The proprietary holdouts — Mathematica, Maple, Magma, MATLAB, MathSciNet, CPLEX, Gurobi — survive on entrenched advantages (Magma in number theory, Mathematica in symbolic-numerical hybrid, CPLEX/Gurobi in industrial optimization) but are increasingly displaced for new research, especially among younger mathematicians.
2. **Proof assistants have crossed the chasm.** Lean 4 with its Mathlib library went from a niche curiosity in 2017 to a serious tool used in active research papers, machine-learning training corpora, and undergraduate teaching by 2025. Coq (now Rocq) and Isabelle remain critical for formally verified mathematics.
3. **The database is a research instrument.** LMFDB, OEIS, KnotInfo, and the ATLAS of Finite Groups are not auxiliary references — they are first-class objects of research. Discoveries are now routinely made by *querying* these databases for patterns and outliers.
4. **AI is rapidly becoming a tool, not a curiosity.** AlphaProof, DeepSeek-Prover-V2, Lean Copilot, and frontier LLMs (ChatGPT, Claude, Gemini) are now in the daily workflow of research mathematicians for proof search, conjecture generation, and verification scaffolding.
5. **The hard parts are interoperability and reproducibility.** No single tool covers all of mathematics. The frontier user typically chains 4–8 of the tools below in a single project, and connecting them is itself a research skill.

---

## How to read this paper

Section 1 is the catalog table — the centerpiece. Skim it once for orientation.

Section 2 walks through the major *categories* of tools, explaining the mathematical problem each category was created to solve and which tools dominate inside it.

Section 3 discusses cross-cutting trends: open-source dominance, the proof-assistant boom, AI integration, and the database-as-instrument shift.

Section 4 closes with what's on the horizon.

---

## 1. Catalog of frontier mathematical research software

The following table lists 48 software systems used in active mathematical research. "Public" means the source code is openly licensed under a recognized open-source license (MIT, BSD, GPL, LGPL, Apache, etc.) and the binary is available at no cost. "Private" means proprietary, license-restricted, and typically with a license fee.

Categorical abbreviations:
- **CAS**: General-purpose computer algebra system
- **NT**: Number theory
- **AG**: Algebraic geometry / commutative algebra
- **GT**: Group theory
- **TOP**: Topology, geometry of 3-manifolds, knot theory
- **PA**: Proof assistant / formal verification
- **NUM**: Numerical / arbitrary precision
- **NAG**: Numerical algebraic geometry (homotopy continuation)
- **SAT**: SAT, SMT, constraint solvers
- **OPT**: Optimization / mixed-integer programming
- **COMB**: Combinatorics / graph theory
- **DB**: Mathematical database (research infrastructure)
- **AI**: Machine learning / AI for mathematics
- **VIZ**: Visualization

| # | Tool | Category | Public/Private | Language | First released | Why it exists / what it solves | Notable use |
|---|------|----------|----------------|----------|----------------|-------------------------------|-------------|
| 1 | **SageMath** | CAS | Public (GPL) | Python (wraps ~100 components) | 2005 | Free, open-source unification of Maxima, GAP, PARI, Singular, R, NumPy, SymPy, FLINT, etc. under a single Python interface. Built by William Stein explicitly to give mathematicians a viable alternative to Magma + Mathematica. | Number theory research, algebraic geometry, education at hundreds of universities. The default open-source CAS for graduate research. |
| 2 | **Mathematica** (Wolfram Language) | CAS | Private | Wolfram Language | 1988 | Symbolic + numerical + visualization in one notebook, with the largest curated function library of any CAS. Strongest in special functions, integral transforms, mixed symbolic-numerical workflows. | Used across physics, engineering, applied math, education. Less central in pure-math research now. License: ~$2,500–10,000+/seat. |
| 3 | **Maple** | CAS | Private | Maple language | 1982 | Symbolic computation pioneer; strong in differential equations, dynamical systems, classical CAS workloads. | Heavy in engineering schools; used in some pure-math subfields (Lie algebras, ODE classification). License: ~$2,000+/seat. |
| 4 | **Maxima** | CAS | Public (GPL) | Common Lisp | 1982 (as Macsyma in 1968) | Direct descendant of MIT's Macsyma — the original CAS. Free open-source successor; still maintained. | Embedded inside SageMath; also used directly in education and lightweight CAS work. |
| 5 | **SymPy** | CAS | Public (BSD) | Pure Python | 2007 | Pure-Python symbolic computation that integrates seamlessly with the scientific Python stack (NumPy, SciPy, Jupyter). No external dependencies. | First-line CAS in Python notebooks; embedded in scientific-computing pipelines worldwide. |
| 6 | **Magma** | CAS / NT / GT / AG | Private | Magma language | 1993 | The dominant tool for **computational number theory** and group theory in research. Extremely fast at modular forms, Galois representations, isogeny graphs, and explicit class field theory. The reason many number theorists pay for proprietary software at all. | Cremona's elliptic curve database; modular form computations across LMFDB; Sutherland's CM scaling work. License: Univ. Sydney, ~free for some academics, expensive otherwise. |
| 7 | **GAP** | GT / COMB | Public (GPL) | GAP language | 1986 | The standard system for **discrete groups and representation theory**: finite groups, finitely presented groups, character tables, automorphism groups. Repository of the ATLAS of Finite Group Representations. | Used to verify Classification of Finite Simple Groups computations; group cohomology research; coding theory. |
| 8 | **Macaulay2** | AG | Public (GPL) | Macaulay2 language | 1993 | Algebraic geometry and commutative algebra: Gröbner bases, free resolutions, sheaf cohomology, intersection theory, Hilbert series. The lingua franca of commutative algebra researchers. | Used heavily in toric geometry, syzygies, Boij-Söderberg theory, derived category computations. |
| 9 | **Singular** | AG | Public (GPL) | C/C++ | 1990 | Polynomial computation specialist: extremely fast Gröbner basis, factorization, primary decomposition. Complementary to Macaulay2. | Standard for Gröbner-basis-heavy work in singularity theory and applied algebraic geometry. Used widely in cryptography research. |
| 10 | **CoCoA** | AG | Public (Apache) | C++ | 1988 | Computations over polynomial rings; pedagogically clean alternative to Singular/Macaulay2. | Education; specific commutative algebra research where CoCoA's interface fits the problem. |
| 11 | **PARI/GP** | NT | Public (GPL) | C / GP scripting | 1985 | Number-theoretic Swiss army knife: number fields, class groups, elliptic curves, modular forms, L-functions, lattice reduction, factoring. The C library underneath SageMath's number theory and the basis of cypari (Python wrapper). | Cremona's pre-Magma EC tables; LMFDB modular form computations; Lehmer-conjecture searches. |
| 12 | **FLINT** | NT | Public (LGPL) | C | 2007 | "Fast Library for Number Theory" — drop-in replacement for and faster than the corresponding parts of GMP, NTL, PARI. The numerical engine behind Nemo.jl, Hecke.jl, modern SageMath number theory. | Class polynomials computation; modular polynomial computations of degree > 10⁵. |
| 13 | **NTL** | NT | Public (LGPL) | C++ | 1990 | Victor Shoup's high-performance arbitrary-precision number theory library. Predecessor and complement to FLINT; still heavily used in cryptography. | Lattice cryptanalysis; isogeny computations; FHE schemes (HElib). |
| 14 | **Nemo.jl / Hecke.jl** | NT | Public (Simplified BSD) | Julia | 2017 | Julia ports/wrappers of FLINT, ANTIC, Singular for use within the Julia ecosystem. Hecke.jl specifically targets number fields. | Julia-based number theory; performance research on the OSCAR project. |
| 15 | **OSCAR.jl** | CAS / NT / AG / GT | Public (GPL) | Julia | 2020 | Ambitious Julia-based unification of Singular, GAP, Polymake, and Hecke. Aims to be the next-generation open-source successor to SageMath with stricter type discipline. | Active research-frontier alternative; growing adoption. |
| 16 | **mpmath** | NUM | Public (BSD) | Python | 2007 | Arbitrary-precision real and complex floating-point arithmetic in pure Python. PSLQ integer-relation finding, special functions, Riemann zeta computations to thousands of digits. | Computing Riemann zeta zeros; numerical verification of identities; LMFDB precision audits. |
| 17 | **ARB / Arb** | NUM | Public (LGPL) | C | 2012 | Ball arithmetic: every floating-point number is paired with a rigorous error radius. Computations stay correct under arbitrary precision. The numerical foundation of FLINT 2.x and Hecke.jl. | Riemann zeta and L-function computations with certified bounds. |
| 18 | **MPFR** | NUM | Public (LGPL) | C | 2000 | Correctly-rounded multiple-precision floating-point. The standard precision library beneath GCC's libquadmath, GMP, and most arbitrary-precision math systems. | Underneath nearly every scientific tool requiring beyond-double precision. |
| 19 | **GMP** | NUM | Public (LGPL/GPL) | C | 1991 | "The GNU Multiple Precision Arithmetic Library." The fastest open-source bignum library; the foundation of MPFR, FLINT, Sage, Mathematica's number engine, Maple's, and most cryptography. | Universally; if you've used a CAS, you've used GMP. |
| 20 | **MATLAB** | NUM / VIZ | Private | MATLAB | 1984 | Matrix-first numerical computing with strong toolboxes (control, signal processing, optimization). Standard in engineering. | Less central in pure math; dominant in applied math, control theory, numerical PDE research. License: ~$2,000+/seat. |
| 21 | **Julia** (language + ecosystem) | NUM / NT / AG / NAG | Public (MIT) | Julia | 2012 | High-performance dynamic language designed for scientific computing. JIT-compiled to LLVM; near-C speed with Python-like ergonomics. Hosts Nemo, Hecke, OSCAR, HomotopyContinuation. | Increasingly the language of choice for new mathematical software. |
| 22 | **NumPy / SciPy** | NUM | Public (BSD) | Python (C/Fortran cores) | 2006 / 2001 | Array computing and scientific algorithms in Python. The numerical foundation under SymPy, scikit-learn, mpmath integrations. | Universal in computational research. |
| 23 | **R** | NUM (statistics) | Public (GPL) | R | 1993 | Statistical computing and graphics. Used in mathematical statistics research. | Mathematical statistics, probability. |
| 24 | **Lean 4** + **Mathlib** | PA | Public (Apache) | Lean | 2013 (Lean) / 2017 (Mathlib) | Modern dependently-typed proof assistant with the largest single library of formalized mathematics (~1.5M lines, ~150K theorems by 2025). The platform of choice for new formal-mathematics projects. | Liquid Tensor Experiment (Scholze's condensed mathematics, formally verified by Buzzard's team in Lean); Polynomial Freiman-Ruzsa conjecture (Tao et al.); used as training corpus for AlphaProof, DeepSeek-Prover. |
| 25 | **Coq / Rocq** | PA | Public (LGPL) | OCaml core | 1989 | Mature dependently-typed proof assistant. Renamed to Rocq in 2024. The Calculus of Inductive Constructions on which much of formal mathematics was built. | Four-Color Theorem (Gonthier); Feit-Thompson Odd-Order Theorem; CompCert verified C compiler. |
| 26 | **Isabelle/HOL** | PA | Public (BSD) | Standard ML | 1986 | Higher-order logic proof assistant with strong automation (Sledgehammer, Nitpick). Distinct philosophy from Coq/Lean — classical logic, less type-theoretic complexity. | Kepler Conjecture verification (Hales' Flyspeck project); verified seL4 microkernel; Archive of Formal Proofs (5000+ entries). |
| 27 | **Agda** | PA | Public (BSD) | Haskell | 2007 | Dependently-typed proof assistant with a strong programming-language flavor. Closer to Haskell than to Coq. | Homotopy Type Theory research; programming-language theory. |
| 28 | **HOL Light / HOL4** | PA | Public (BSD) | OCaml / Standard ML | 1996 / 1988 | Higher-order logic systems by John Harrison and others. Minimal kernels; used for hardware verification and pure mathematics. | Hales' verification of the Kepler conjecture; Intel floating-point hardware verification. |
| 29 | **Metamath** | PA | Public (Public Domain) | Metamath | 1992 | Minimalist proof assistant: every step is a single substitution into an axiom or theorem. Set.mm contains ~40,000 ZFC-derived theorems. | Education; foundational metamathematics; Norman Megill's set.mm project. |
| 30 | **Mizar** | PA | Public (Mizar SUL) | Mizar | 1973 | The oldest active proof-checking system; large library (Mizar Mathematical Library has ~60K theorems). | Polish formal-mathematics tradition; large theorem corpus for ML research. |
| 31 | **SnapPy** | TOP | Public (GPL) | Python (wraps C/C++ SnapPea kernel) | 2009 | Computational topology of 3-manifolds: hyperbolic structure, volumes, fundamental groups, Dehn fillings, knot/link complements. Successor to Jeff Weeks's SnapPea. | KnotInfo trace fields; geometric topology research; the only general-purpose tool for hyperbolic 3-manifold computation. |
| 32 | **Regina** | TOP | Public (GPL) | C++ / Python bindings | 1999 | Triangulation-based 3-manifold topology: normal surface theory, census enumeration, decision algorithms (unknot recognition, sphere recognition). | Triangulation census; computational topology research; unknot decision. |
| 33 | **knot_floer_homology** | TOP | Public (GPL) | Python wrapping C++ | ~2015 | Computes Heegaard Floer homology of knots from PD codes: ranks, tau, epsilon, fibered detection, L-space detection. | Knot Floer research; large-scale knot invariant scans. |
| 34 | **GUDHI** | TOP | Public (LGPL) | C++ / Python | 2014 | Topological data analysis library: persistent homology, Vietoris-Rips, Mapper. | TDA research, applied topology. |
| 35 | **Ripser** | TOP | Public (LGPL) | C++ | 2018 | Extremely fast persistent-homology computation for Vietoris-Rips complexes. State of the art for VR persistence. | Applied topology, machine learning + topology. |
| 36 | **polymake** | AG / COMB | Public (GPL) | C++ / Perl | 1997 | Convex polytopes, polyhedral combinatorics, tropical geometry. The standard computational engine for polytope research. | Combinatorial optimization; tropical geometry research; toric geometry inputs. |
| 37 | **Bertini** | NAG | Public (BSD) | C/C++ | 2004 | Numerical algebraic geometry: solves polynomial systems via homotopy continuation. Robust to high degree. | Engineering kinematics; chemistry equilibria; algebraic statistics. |
| 38 | **HomotopyContinuation.jl** | NAG | Public (MIT) | Julia | 2018 | Modern, fast Julia successor to Bertini-style homotopy continuation. Active research tool in numerical algebraic geometry. | Solving polynomial systems with millions of solutions; algebraic-statistics applications. |
| 39 | **PHCpack** | NAG | Public (GPL) | Ada / C / Python bindings | 1996 | Polyhedral homotopy continuation. The original NAG implementation; still actively used. | Polynomial system solving in robotics, kinematics. |
| 40 | **fpLLL** | NT / OPT | Public (LGPL) | C++ | 2005 | The fastest open-source LLL/BKZ lattice reduction implementation. Critical for cryptography research. | Post-quantum cryptography (NIST PQC competition); cryptanalysis of LWE/RLWE schemes. |
| 41 | **nauty / Traces** | COMB | Public (Apache) | C | 1981 | Graph isomorphism and canonical labeling. The de facto fastest practical graph-iso solver. Underneath GAP's graph routines. | Graph enumeration; combinatorial database curation; chemistry molecule fingerprinting. |
| 42 | **Z3** | SAT | Public (MIT) | C++ | 2008 | SMT solver developed at Microsoft Research. Decides satisfiability over arithmetic, arrays, bitvectors, and more. Underneath dafny, F\*, hardware verification. | Software verification; SMT-LIB benchmarks; LLM-augmented theorem proving. |
| 43 | **CryptoMiniSat / Kissat** | SAT | Public (MIT) | C/C++ | 2010 / 2018 | State-of-the-art SAT solvers. Annual SAT-competition winners. | Pythagorean Triples problem (200 TB proof); Boolean Pythagorean Triples (Heule, Kullmann, Marek). |
| 44 | **CPLEX / Gurobi** | OPT | Private | C/C++ | 1988 / 2008 | Industrial-strength mixed-integer programming. Faster and more robust than open-source competition. | Operations research, supply chain, mathematical-programming research. License: $5K–$100K+/seat. |
| 45 | **SCIP** | OPT | Public (academic free, ZIB) | C/C++ | 2005 | Strongest open-source MIP solver. Free for academic use; competitive with commercial. | Mixed-integer research; combinatorial optimization research. |
| 46 | **LMFDB** | DB | Public | (web service over Postgres) | 2007 | The "L-functions and Modular Forms Database." A research-grade collection of mathematical objects (elliptic curves, modular forms, number fields, L-functions) with computed invariants and cross-links. | Cited in hundreds of papers; the standard data source for LMFDB-class objects in NT research. |
| 47 | **OEIS** | DB | Public | (web service) | 1964 (as Sloane's notebooks) / 1996 (online) | The Online Encyclopedia of Integer Sequences. ~370K integer sequences with citations, formulas, programs. Founded and curated by N.J.A. Sloane. | Universal: any conjecture about an integer sequence is OEIS-checkable in 5 seconds. Has shaped countless results. |
| 48 | **AlphaProof / AlphaGeometry** (DeepMind) | AI / PA | Private | (not released; Lean 4 + RL) | 2024 | Reinforcement-learning systems that produce Lean proofs of mathematical theorems. AlphaProof reached IMO 2024 silver-medal performance. | Research demonstrations; not generally available, but demonstrates the trajectory of AI-augmented mathematics. |
| 49 | **DeepSeek-Prover-V2** | AI / PA | Public (open weights, MIT) | (Lean 4 backend) | 2025 | Open-weight 671B-parameter neural prover trained on Lean 4 / Mathlib. Approaches AlphaProof-level performance with open weights. | Reproducible AI-prover research; integration into Lean workflows. |
| 50 | **MathSciNet** | DB | Private | (web service) | 1940 (Math Reviews) / 1990 (online) | Mathematical Reviews — the canonical literature index for mathematics, with reviews and citation graph. | Universal in literature search. License: institutional, ~$10K+/year. |

---

## 2. Categories: what each kind of tool exists to solve

### 2.1 General-purpose computer algebra systems

Mathematics has long needed *symbolic* computation — manipulating expressions like polynomials, integrals, and matrices not as numerical approximations but as exact algebraic objects. The first CAS, Macsyma, was built at MIT starting in 1968. Its descendants split into commercial (**Mathematica**, **Maple**) and open-source (**Maxima**, **SageMath**, **SymPy**) lineages.

The split matters. Mathematica and Maple are powerful and polished but cost thousands per seat and their internals are closed — researchers who want to *understand* an algorithm or extend it often cannot. SageMath was founded in 2005 explicitly to give the open-source community a viable Magma+Mathematica alternative; it does not reimplement these systems but rather provides a unified Python interface to ~100 specialist open-source tools (GAP, PARI, Singular, Maxima, R, NumPy, SymPy, FLINT, etc.). The result is a CAS where every algorithm is open and every component has a research-mathematician maintainer.

For pure mathematics research, **SageMath** has effectively won the open-source CAS market, with **Mathematica** retained for symbolic-numerical hybrid work and **Magma** retained for performance-critical number theory. The Julia-based **OSCAR** project, started in 2020, aims to be the next generation: stricter typing, modern language design, and tighter integration of GAP + Singular + Polymake + Hecke.

### 2.2 Number theory specialists

Number theory has historically been the most computational subfield of pure mathematics, and its tools reflect that. **PARI/GP** has been the workhorse since 1985 — a C library plus its own scripting language, fast at number fields, elliptic curves, modular forms, lattice reduction, and L-function computation. **FLINT**, developed since 2007 by Bill Hart and others, is FLINT's faster successor for the most performance-critical primitives (modular polynomials, factorizations, fast linear algebra modulo primes). Together, these C libraries underlie SageMath, Hecke.jl, OSCAR, and most number-theoretic research.

**Magma** sits above PARI/GP and FLINT in capability but at a steep license cost. For high-end computational number theory — explicit class field theory of arbitrary number fields, p-adic L-functions, isogeny graphs of elliptic curves over number fields, modular form computations of large weight — Magma still has the largest body of specialized algorithms that no open-source competitor fully replicates. The OSCAR project is closing that gap on a 5-year horizon.

The problems being solved here are not abstract: BSD-style cross-checks of analytic Sha against algebraic Sha, Galois representation computations for modular forms (used in modularity proofs), explicit class field theory in Iwasawa theory, isogeny computations for post-quantum cryptography. Computational number theory is one of the few areas where pure mathematics directly supplies industrial cryptographic infrastructure.

### 2.3 Algebra specialists: groups, polynomials, varieties

**GAP** (Groups, Algorithms, Programming) is the standard system for finite-group computations and discrete representation theory. The classification of finite simple groups is *verified* by GAP-based computations; the ATLAS of Finite Groups is implemented as a GAP package. Group cohomology, character tables, automorphism groups, finitely-presented group decision problems — GAP is the answer.

**Macaulay2** and **Singular** dominate commutative algebra and algebraic geometry, with overlapping but complementary strengths. Macaulay2 is more user-friendly and pedagogical; Singular is faster on Gröbner-basis-heavy workloads. Both are used heavily in Boij-Söderberg theory, syzygies and free resolutions, intersection theory on toric varieties, and the computational side of singularity theory.

**polymake** specializes in convex polytopes and polyhedral combinatorics — the key tool whenever a research question reduces to enumerating faces, checking face lattice properties, computing Ehrhart polynomials, or doing tropical geometry.

### 2.4 Proof assistants: the formal-verification revolution

Until ~2017, formal verification of mathematics was a niche activity practiced by a small community. It produced impressive results — the Four-Color Theorem (Gonthier in Coq), the Feit-Thompson Odd-Order Theorem (Gonthier et al. in Coq), the Kepler Conjecture (Hales et al. in HOL Light/Isabelle) — but each project took years of human effort and the libraries did not chain.

**Lean 4** and its **Mathlib** library changed the game. By 2025, Mathlib contains roughly 1.5 million lines of formalized mathematics covering most of an undergraduate curriculum and substantial portions of modern research. Crucially, it is *coherent* — every definition is part of a single library, so theorems can be combined without translation effort. Peter Scholze's Liquid Tensor Experiment (formalization of his work on condensed mathematics) was completed in Lean. Terence Tao formalized the Polynomial Freiman-Ruzsa conjecture in Lean. The PFR formalization happened in *weeks*.

**Coq/Rocq** and **Isabelle/HOL** remain critical. Coq has the more sophisticated type theory (CIC, with universe polymorphism); Isabelle has the strongest automation (Sledgehammer can call external SMT solvers). Different research groups choose based on philosophy and style.

What problem does this category solve? Two: (1) *certainty* — a Lean proof that compiles is correct modulo bugs in the kernel, which is small and itself verified; (2) *sharing* — formal proofs are machine-checkable, so claims can be transmitted without trust. The Mathlib community has demonstrated that (3) *training* AI provers is now a downstream product: AlphaProof and DeepSeek-Prover are trained directly on Lean 4 / Mathlib corpora.

### 2.5 Geometry, topology, knot theory

**SnapPy** is the standard tool for hyperbolic 3-manifold computations: given a knot, link, or triangulation, it computes the hyperbolic structure (when one exists), the volume, the fundamental group representation, cusp shapes, and Dehn fillings. Successor to Jeff Weeks's SnapPea, SnapPy is a Python wrapper around the SnapPea C kernel and has become the de facto interface for hyperbolic geometry.

**Regina** complements SnapPy: rather than hyperbolic geometry, Regina handles 3-manifold triangulations, normal surface theory, and decision algorithms (unknot recognition, 3-sphere recognition). Census enumeration of small 3-manifold triangulations is Regina's specialty.

**knot_floer_homology** by Bar-Natan, Lewark, and others is the standard implementation of Heegaard Floer knot homology — given a planar diagram, returns the bigraded Betti table and the τ, ε, ν invariants. Used heavily in research on the slice-genus and L-space conjecture.

For topological data analysis (a younger field), **GUDHI** and **Ripser** are the two leading libraries. Ripser's specialty is extremely fast Vietoris-Rips persistent homology computation; GUDHI is a fuller library covering Mapper, witness complexes, persistence images.

### 2.6 Numerical algebraic geometry: homotopy continuation

Polynomial systems with hundreds or thousands of solutions arise in robot kinematics, chemical equilibria, algebraic statistics, and combinatorial optimization. Symbolic methods (Gröbner bases) often fail at these scales. Numerical algebraic geometry, pioneered in the 1990s, instead tracks solutions numerically as parameters vary along a "homotopy" path from a known system to the unknown one.

**Bertini** (2004), **PHCpack** (1996), and **HomotopyContinuation.jl** (2018) are the three leading systems. The Julia-based newcomer is now competitive in performance and is the standard for new research projects.

### 2.7 SAT, SMT, and constraint solvers

Modern SAT solvers can handle Boolean formulas with millions of variables. Mathematicians have used them to settle long-standing open problems: the Boolean Pythagorean Triples Problem (Heule, Kullmann, Marek 2016) produced a 200-terabyte proof certificate. **Z3**, an SMT solver from Microsoft, decides satisfiability not just of Boolean formulas but of mixed arithmetic, arrays, and bitvectors — making it useful in formal verification. **Kissat** and **CryptoMiniSat** are the perennial winners of the SAT Competition.

What problem do these solve? Combinatorial questions that reduce to Boolean satisfiability: graph coloring, packing, scheduling, and increasingly, parts of mathematical proofs that reduce to large finite case checks.

### 2.8 Optimization (mixed-integer programming)

**CPLEX** (IBM, 1988) and **Gurobi** (2008) are the duopoly of commercial mixed-integer programming. They solve problems with millions of variables and constraints, and routinely outperform open-source alternatives by factors of 2-100x on hard instances. For mathematical research that reduces to MIP — combinatorial optimization, optimal experimental design, polynomial optimization via Lasserre relaxation — these are essential. **SCIP** (ZIB, free for academics) is the strongest open-source competitor.

### 2.9 High-precision numerics

Numerical computations to dozens or thousands of digits of precision are needed for: numerical verification of conjectured identities, integer-relation finding (PSLQ), zero computations of L-functions, and (less commonly) brute-force verification of analytic statements. **GMP** (multi-precision integers), **MPFR** (correctly-rounded multi-precision floats), and **MPC** (complex extension) form the foundation. **mpmath** (Python) and **ARB** (rigorous ball arithmetic) sit on top, providing higher-level interfaces with rigorous error tracking.

### 2.10 Mathematical databases as research instruments

A relatively recent insight: mathematical databases are not just references — they are objects of *research*. The **OEIS** (Sloane's encyclopedia, 1964 / online 1996) is the most striking example. ~370,000 integer sequences are now keyed; any conjecture that a particular sequence has a nice form can be checked in five seconds against the entire database. Many recent papers begin with "we found this sequence in OEIS, leading us to conjecture..."

The **LMFDB** (started 2007) does the same for L-functions, modular forms, elliptic curves, number fields, and related objects. It is the public face of decades of computations by Cremona, Stein, Sutherland, and the LMFDB collaboration. Today, it is impossible to do computational number theory at the frontier without LMFDB.

The **KnotInfo** and **LinkInfo** databases (Livingston, Moore et al.) catalog knots up to 13 crossings with their invariants. The **ATLAS of Finite Groups** (Conway et al.) catalogs finite simple groups and their representations.

These public databases are often *more* useful than proprietary tools, because their data can be queried, downloaded, and reanalyzed without licensing barriers.

### 2.11 The proprietary literature: MathSciNet and zbMATH

The two universal mathematical literature databases are **MathSciNet** (American Mathematical Society, ~$10K/year institutional license) and **zbMATH** (FIZ Karlsruhe, partially open). These are the search infrastructure of mathematical research; their indexing, MSC subject classification, and review system are critical. Yet they remain proprietary, a significant cost for mathematical departments and a barrier for independent researchers.

### 2.12 AI for mathematics

A new category as of 2023-2025. The frontier developments:

- **AlphaProof** (DeepMind, 2024): an RL system that emits Lean 4 proofs. Reached silver-medal performance at IMO 2024 on real competition problems. Not publicly available.
- **AlphaGeometry** (DeepMind, 2024): geometry-theorem proving. Reached gold-medal performance at IMO 2024 geometry problems.
- **DeepSeek-Prover-V2** (2025): open-weight 671B-parameter model trained on Mathlib. The first open-weight competitor to AlphaProof.
- **Lean Copilot** and **MathChat**: tools that integrate LLMs (GPT-4, Claude) directly into Lean development, suggesting tactics and lemma applications.
- **Frontier LLMs** (ChatGPT, Claude, Gemini): used by working mathematicians for proof sketching, conjecture generation, literature search, and code generation. Not formal-verification tools but increasingly part of the workflow.

The key observation: AI provers improve roughly 10–100× faster than human-built tools because they can be retrained on growing Mathlib corpora. This dynamic is unique to formal-verification-adjacent fields where there is a clean training signal.

---

## 3. Cross-cutting trends

### 3.1 Open source dominates, but not uniformly

Across the 50 tools cataloged, ~80% are open source. The proprietary holdouts cluster in two areas:

- **Number theory and group theory at the highest performance level** (Magma).
- **Mixed-integer optimization** (CPLEX, Gurobi).
- **General-purpose CAS for non-research users** (Mathematica, Maple, MATLAB).
- **Literature databases** (MathSciNet, zbMATH).

The economics matter. Magma's annual fee for a research department is in the $5–15K range. CPLEX and Gurobi licenses for serious work are $10–100K+. MATLAB site licenses for an engineering school can hit $1M+/year. These costs are absorbed by research budgets but excluded by independent researchers, smaller institutions, and many non-Western universities. The open-source alternatives — SageMath, GAP, SCIP, OSCAR — are explicitly built to remove this barrier.

### 3.2 Proof assistants: from niche to mainstream

The Lean 4 / Mathlib ecosystem has a critical mass that no prior proof assistant achieved. Indicators:

- ~1.5M lines of formalized mathematics in Mathlib (as of 2025).
- Active formalizations of recent results (PFR, condensed mathematics, parts of the proof of the Geometric Langlands).
- Field Medalists actively contributing (Tao, Scholze, others).
- Integration in undergraduate teaching at multiple top universities.
- Standardized as the training corpus for AI provers.

The trajectory suggests Lean (or its successors) will become a normal part of mathematical workflow within a decade — not for every paper, but for the most important results, similar to how computer-checked simulations became standard in physics.

### 3.3 The database is now an instrument

Researchers used to *publish* tables of computed mathematical objects. They now query *live databases* (LMFDB, OEIS, KnotInfo) maintained as community infrastructure. This shift transforms how research is done:

- Conjectures are tested against the full corpus before being stated.
- Counterexamples are found by database query, not hand search.
- Cross-domain bridges are discovered by joining databases on numerical invariants.

The Prometheus project itself, in which this paper is being written, exemplifies this shift: many of its computations consist of joining LMFDB tables against the OEIS and KnotInfo databases looking for cross-domain coincidences.

### 3.4 Interoperability as a research skill

A typical frontier-mathematics workflow chains 4–8 tools: data extraction from LMFDB or OEIS, symbolic preprocessing in SageMath or Mathematica, specialized computation in PARI or Magma, structural verification in GAP or Macaulay2, formal verification in Lean, AI-suggested proof tactics from Copilot or DeepSeek-Prover, and visualization in Jupyter+Matplotlib.

The research mathematician's effective skill set now includes glue-code writing, JSON/XML wrangling, file format conversion, and CI-style reproducibility. This is not "applied mathematics" — these are pure mathematicians using software because their problems require it.

### 3.5 The funding model puzzle

Most of these tools are public goods built by research mathematicians as side projects or graduate student work. SageMath was famously a labor of love by William Stein, and is sustained by a fragile mix of NSF grants, university support, and volunteer time. PARI/GP, FLINT, GAP, Macaulay2, Singular, LMFDB — all run on similar funding models.

This is a known structural fragility. A single retirement or grant lapse can stall a tool that thousands depend on. There is no equivalent of NIH-scale funding for mathematical research software, and the proprietary tools (Magma, Mathematica, Maple, CPLEX) do not directly compensate for these gaps.

---

## 4. What's on the horizon (2025–2030)

**Lean as the default formal language.** Mathlib will continue to grow at 10–20% per year. By 2030, expect that "we formalized our main result in Lean" appears in most top-journal papers in algebra, number theory, and combinatorics.

**OSCAR replacing SageMath in performance-sensitive workflows.** The Julia-based OSCAR system is ~3 years from feature parity with SageMath in the core areas it targets (number theory, algebraic geometry, group theory, polytopes). Once parity is reached, performance and language design will favor OSCAR for new projects.

**AI provers as workflow tools, not separate systems.** AlphaProof and DeepSeek-Prover today produce proofs as standalone artifacts. By 2030 they will be tightly integrated into Lean, Coq, and Isabelle workflows — the human writes a goal, the AI suggests a proof, the human accepts or refines.

**Database-database joins as discovery instruments.** The number of large mathematical databases will grow, and tooling for cross-database joins will become standard. This is a research direction in itself: which numerical invariants link which mathematical objects?

**Cryptographic urgency.** The transition to post-quantum cryptography (NIST PQC standardization) has put intense computational pressure on lattice and isogeny algorithms. Tools like fpLLL, FLINT, and the SageMath isogeny package are now critical infrastructure for Internet security. This will sustain funding for these tools at a level that pure-math demand alone could not.

**The interoperability layer.** Expect a "matplotlib for mathematics" — a general-purpose translation layer that makes it trivial to move objects between SageMath, Mathematica, Lean, Magma, OSCAR. The lack of this layer is the single biggest practical bottleneck in mathematical computation today.

---

## Appendix A: License classes encountered

- **Public Domain / CC0**: Metamath. Effectively the most permissive.
- **MIT / BSD / Apache 2**: Permissive open source. Most modern projects (SymPy, Z3, Julia, Lean 4, Nemo.jl, Ripser).
- **LGPL**: Linkable open source. FLINT, NTL, MPFR, GMP, ARB, GUDHI.
- **GPL**: Strong copyleft. SageMath, GAP, Macaulay2, Singular, PARI/GP, SnapPy, Regina, polymake, Maxima, R.
- **Proprietary commercial**: Mathematica, Maple, MATLAB, Magma, CPLEX, Gurobi, MathSciNet.
- **Mixed**: SCIP (academic free), Magma (variable institutional pricing), zbMATH (partially open).

The license matters more than it might seem. GPL projects can include LGPL and BSD code; LGPL projects can include BSD code; permissive projects can include only permissive code; proprietary projects often cannot directly incorporate GPL code without licensing accommodation. This shapes which tools can build on which.

---

## Appendix B: Selection criteria and what was omitted

Tools were selected by the following criteria:

1. **Active use in current frontier mathematics research** (citations in top journals 2020–2025).
2. **Distinctness** — only one tool per closely-overlapping niche unless the alternatives are genuinely complementary.
3. **Research-grade, not just pedagogical** — GeoGebra, Desmos, and Khan Academy tools are excluded despite their educational importance.
4. **Working systems, not paper proposals** — abandoned or vaporware projects are excluded.

Notable omissions:
- **Sage Notebook / CoCalc**: research infrastructure, not a tool per se.
- **Wolfram Alpha**: a public-facing query interface to Mathematica; not used in research workflows.
- **MAGMA-V2** (the unreleased OSCAR-Julia rewrite of Magma): under development.
- **Wolfram Function Repository**: a data resource attached to Mathematica.
- **Matlab Symbolic Toolbox**: a wrapper around MuPAD; rarely used in pure math.
- **Maple Calculator / Maple Learn**: education-targeted, excluded.

---

## Appendix C: Open-source replacements for proprietary tools

The proprietary holdouts (Magma, Mathematica, Maple, MATLAB, CPLEX/Gurobi, MathSciNet) all have open-source alternatives, with replacement fidelity ranging from ~95% (MATLAB → Julia) to ~70% (Mathematica → SageMath/SymPy). Practical guide:

| Proprietary | Best open-source replacement(s) | Fidelity | Gap |
|---|---|---|---|
| **Magma** | **SageMath**, **PARI/GP**, **OSCAR.jl** (Julia) | ~80–90% for typical research | Specialized algorithms in NT (explicit class field theory, p-adic L-functions, isogeny graphs, certain Selmer computations). OSCAR aims to close this on a 5-year horizon. |
| **Mathematica** | **SageMath**, **SymPy**, **Maxima**; SymPy + NumPy + Jupyter as notebook environment | ~70% for research; ~90% for engineering | Curated special-function library, integration engine, Wolfram Alpha-style natural-language input, notebook polish. |
| **Maple** | **SageMath**, **Maxima**, **SymPy**, **Reduce** | ~80% | ODE/PDE classifiers and physics packages. Less differentiated than Mathematica. |
| **MATLAB** | **Julia** (strongest), **Python + NumPy/SciPy + matplotlib**, **GNU Octave** (script-compatible), **Scilab** | ~95% for pure math; ~60% for industrial control with Simulink | Simulink and certain hardware-certification toolboxes have no real open-source equivalent. |
| **CPLEX / Gurobi** | **SCIP**, **HiGHS** (MIT, fast LP), **OR-Tools / CP-SAT** (Apache 2, excellent on combinatorial), **CBC**, **GLPK** | ~70% industrial; ~95% combinatorial / pure-math via CP-SAT | CPLEX/Gurobi remain 2–100× faster on hard MIP instances at industrial scale. SCIP closes ~10–20%/release. |
| **MathSciNet** | **zbMATH Open** (large portions free since 2021), **arXiv**, **Google Scholar**, **Semantic Scholar** | ~85% search; ~70% curated reviews | Curated review system with named expert reviewers. zbMATH closing in. |

**Practical guidance.**

For new research projects starting today, the open-source stack (SageMath / OSCAR / Lean / Julia / SCIP / zbMATH) is sufficient ~85% of the time. Proprietary tools win when you need:
- specific Magma algorithms (NT specialists)
- Mathematica's integration engine (special-function research)
- Gurobi-grade MIP performance (industrial OR)
- Simulink-bound engineering pipelines

The cost difference is several orders of magnitude: $0 vs. $5K–$100K+/year/researcher across the proprietary stack. For independent researchers and smaller institutions, the open-source path is already viable for most published research.

---

*Compiled by Techne (Prometheus toolsmith), 2026-04-25.*

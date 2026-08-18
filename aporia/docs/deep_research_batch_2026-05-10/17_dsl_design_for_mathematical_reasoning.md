# Prompt 17: DSL design for mathematical reasoning

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdRRDRCYXBLT05fX2dfdU1Qb0lqcTBBYxIXUUQ0QmFwS09OX19nX3VNUG9JanEwQWM
**Elapsed:** 242s

---

# Project Prometheus: Survey of Math-DSL Primitive Zoo Organizations

**Key Points**
*   **Architectural Divergence**: Mature mathematical domain-specific languages (Math-DSLs) bifurcate into distinct organizational paradigms: flat symbolic unification (Mathematica), strict hierarchical core-vs-application splits (SymPy), universal algebra categorification (Magma), and multi-system federation (SageMath).
*   **Typing and Dispatch**: The evolution of Math-DSLs heavily leans toward parametric typing and multiple dispatch (as seen in Julia's AbstractAlgebra.jl), moving away from implicit scoping and untyped interpreters.
*   **Vetting and Evolution**: Open-source systems enforce rigorous community-driven vetting pipelines (e.g., SymPy's one-year deprecation cycle and strict CI criteria) to curate their primitive zoos, whereas proprietary systems rely on central design authorities.
*   **Prometheus Alignment**: The integration of these historical lessons into Project Prometheus necessitates a tiered architecture (Tier-A++ to Tier-E) that adopts Magma-style parent structures for abstract algebra, SymPy-style tree representation for calculus, and Julia-style trait-based dispatch for performance.

**Introduction to Primitive Zoo Organization**
The organization of a "primitive zoo"—the core set of built-in functions, types, and axioms within a mathematical computing environment—defines the scalability, performance, and cognitive load of the system. In mathematical computing, a primitive is not merely a data type but often an algebraic structure, an assumption constraint, or a transformation rule. 

**Scope of the Survey**
This report evaluates five mature math-DSLs—Mathematica (Wolfram Language), SymPy, Magma, Pari/GP, and SageMath—alongside cross-cutting paradigms from Julia's ecosystem. It dissects their module architectures, vetting protocols for new primitives, and foundational design rationales.

**Application to Project Prometheus**
The findings are mapped directly onto the Project Prometheus architecture. By analyzing the successes and bottlenecks of legacy systems, we derive actionable design lessons for Prometheus's Tier-A++ (Foundational) through Tier-E (Knowledge Representation) hierarchy.

## 1. Mathematica Primitive Zoo

### 1.1 The Top-Level Functions Index
The Wolfram Language, the computational engine behind Mathematica, is characterized by an expansive, unified primitive zoo that operates on a remarkably flat namespace. The system contains over 5,000 built-in functions [cite: 1, 2]. Rather than sequestering these functions into nested modules or discrete packages (as is common in Python or C++ libraries), Wolfram surfaces the vast majority of its core algebraic, calculus, graphical, and machine-learning primitives at the top level. 

To manage this massive global namespace without inducing crippling naming collisions, the design rationale relies heavily on a strict typographical convention: every built-in function, symbol, and constant begins with a capital letter, and multi-word functions utilize CamelCase (e.g., `LinearSolve`, `FindRoot`, `BesselJ`) [cite: 2]. This explicit design choice serves as a primary partitioning mechanism between the system's primitive zoo and user-defined variables, which are conventionally written in lowercase [cite: 2]. While critics argue that a flat namespace of 5,000 functions is difficult to navigate natively, the system mitigates this through comprehensive, deeply integrated documentation accessible via the `?FunctionName` query syntax [cite: 2]. 

### 1.2 Symbolic Unification and "Knowledge Representation"
The foundational philosophy of the Wolfram Language is that everything—data, mathematical formulas, raw code, UI graphics, and textual documents—is represented as a symbolic expression [cite: 3, 4]. Under the hood, every object is treated as a tree structure of the form `Head[arg1, arg2, ...]`. This radical homogenization means that an algebraic equation, a matrix, and a graphical plot share the same fundamental atomic representation.

Wolfram extends this symbolic language into a comprehensive "knowledge representation" framework, aiming to make all systematic, real-world knowledge directly computable [cite: 5]. The Wolfram Data Framework (WDF) leverages the language to provide standardized, computable descriptions of real-world constructs [cite: 6]. Within this framework, primitives extend beyond traditional mathematical concepts (like `Integer`, `Real`, `Complex`) to include domain-specific ontological constructs:
*   `Entity`: A canonical representation of a real-world object (e.g., a city, a chemical element) [cite: 6].
*   `EntityClass`: A definitional grouping of entities [cite: 6].
*   `Quantity`: A primitive that inextricably binds a numerical value with a physical unit, enforcing dimensional analysis at the lowest level of evaluation [cite: 6].

These primitives allow Mathematica to act as a hybrid neuro-symbolic engine, transitioning smoothly from pure mathematical logic (deduction) to real-world probabilistic reasoning [cite: 1, 3]. By automating the layers of execution—where the user provides the "computational thinking" and the engine handles the algorithmic implementation—the system reduces the friction of utilizing complex mathematical operations [cite: 1].

### 1.3 Compilation and Sub-Evaluation
Despite the high-level symbolic nature of the primitive zoo, Mathematica incorporates a system compiler that dynamically links Wolfram libraries for highly optimized execution [cite: 4]. The compiler scales up computations by breaking down high-level symbolic functions into specific arrays and numeric data types [cite: 4]. The `Compile` function operates by establishing a strict internal type system over fundamental arrays, providing a "hybrid symbolic-numerical method" that escapes the performance penalties of pure symbolic pattern matching when evaluating closed-form numeric arrays [cite: 4]. 

## 2. SymPy Module Architecture

### 2.1 The "Core" vs. "Applications" Split
SymPy is an open-source Computer Algebra System (CAS) written entirely in Python [cite: 7]. Because Python does not inherently support symbolic mathematics, SymPy implements its own mathematical object model. To maintain a manageable primitive zoo, SymPy enforces a strict architectural dichotomy between its "core" modules and its domain-specific "applications" [cite: 7].

The `sympy.core` module defines the foundational axioms and building blocks of the entire CAS. Everything in SymPy is an instance of a Python class that inherits from `Basic` (for general expressions) or `Expr` (for mathematical expressions) [cite: 8, 9]. The core is responsible for defining the abstract syntax tree (AST) node structures. For instance, the expression $x \cdot y + 2$ is structurally represented as `Add(Mul(Symbol('x'), Symbol('y')), Integer(2))` [cite: 8]. The core contains indispensable primitives such as `Add`, `Mul`, `Pow`, `Symbol`, and the numeric types `Integer`, `Float`, and `Rational` [cite: 8, 9]. 

Outside of the core, SymPy isolates domain-specific functionality into distinct modules:
*   **Calculus and Polynomials**: `sympy.calculus`, `sympy.integrals`, `sympy.polys` handle algorithms for derivatives, limits, and advanced Gröbner basis computations [cite: 7].
*   **Applications**: Modules like `sympy.physics` (mechanics, quantum), `sympy.geometry`, and `sympy.stats` sit atop the core, utilizing the basic symbolic engine to perform domain-specific computations [cite: 7, 10, 11].

This architectural split ensures that the computational overhead of complex physical or statistical models does not bloat the fundamental algebraic engine. 

### 2.2 The Assumptions System and Lazy Evaluation
A critical component of SymPy's primitive organization is its assumptions system, which dictates how primitives behave under simplification and evaluation. Variables must be instantiated as `Symbol` objects before use, and during instantiation, the user can inject semantic constraints [cite: 11, 12]. For example, `Symbol('x', positive=True)` informs the engine that $x$ is a positive real number [cite: 12].

The assumptions system is deeply embedded in `sympy/core/assumptions.py`. At import time, assumption rules are processed into a canonical form to allow efficient implication checking (e.g., if `integer=True`, then `rational=True` is automatically inferred) [cite: 12]. This system dictates lazy evaluation protocols; SymPy will refuse to automatically simplify $\sqrt{x^2}$ to $x$ unless $x$ is explicitly assumed to be positive, as the simplification is mathematically invalid for arbitrary complex numbers [cite: 12]. 

### 2.3 Vetting and Curating New Primitives
Unlike proprietary systems, SymPy's primitive zoo is governed by a decentralized, community-driven bazaar model via GitHub [cite: 7]. To prevent the language from degrading into an unmaintainable sprawl, SymPy enforces strict code review and vetting protocols for all new additions.

Any modification to the primitive zoo must be submitted as a Pull Request (PR) and undergo peer review [cite: 13]. The vetting checklist requires:
1.  **Code Quality**: Compliance with `flake8` standards [cite: 14].
2.  **Testing**: All new functionalities must be accompanied by regression tests written in the `pytest` assert style (`assert f(x) == y`) within the corresponding test directory [cite: 14].
3.  **Documentation**: New public functions must include a docstring featuring executable `doctests` [cite: 14].
4.  **Release Notes**: Contributors must supply release notes mapping the semantic changes [cite: 14].

Furthermore, SymPy strictly manages the lifecycle of its primitives through a formal deprecation policy [cite: 15, 16]. Because SymPy is utilized as a dependency by other major scientific libraries (like SageMath and PyDy), backwards compatibility is heavily guarded [cite: 7]. If a primitive or module (e.g., `sympy.core.compatibility`) is deemed obsolete, it is tagged with a `SymPyDeprecationWarning` [cite: 16]. The deprecation must last at least one year, spanning a major release cycle, before the primitive is permanently excised from the codebase [cite: 15, 16]. 

## 3. Magma Language Design

### 3.1 Discrete-Math Focus and Universal Algebra Roots
Magma is a highly specialized, rigidly structured computer algebra system designed for rigorous computations in algebra, number theory, algebraic geometry, and combinatorics [cite: 17]. Its primitive zoo is explicitly constructed upon the formalisms of Universal Algebra and Category Theory [cite: 17, 18]. 

In stark contrast to Mathematica's element-centric "everything is a symbol" approach, Magma enforces a structure-centric paradigm. In Magma, it is impossible to define an isolated mathematical element like $x^3 - 1$ without explicitly assigning it to a "parent structure" [cite: 18]. If an element is defined within the polynomial ring $\mathbb{Z}[x]$, the system intrinsically knows to apply factorization rules for irreducible polynomials over integers [cite: 18]. 

### 3.2 Primitive Zoo Organization: Varieties and Categories
Magma organizes its primitive structures by "variety"—a class of structures sharing a common set of defining operators and axioms (e.g., the collection of all rings forms a variety) [cite: 17, 19]. Within a given variety, structures are further partitioned into "categories" based on concrete representations. For instance, within the algebra variety, finitely presented algebras form an abstract category, while matrix algebras form a concrete category [cite: 17].

The category to which a "magma" (an algebraic structure) belongs fundamentally dictates:
*   The internal representation of the elements [cite: 18].
*   The representation of the carrier sets [cite: 18].
*   The legal arithmetic operations that can be performed on the elements and the structure itself [cite: 18].

Magma's type system manages complex bodies of information by storing relationships between parent structures and child structures [cite: 17]. When a quotient structure is generated, the natural homomorphism linking it to its parent is stored in memory, supporting automatic, mathematically rigorous coercion between types [cite: 17].

### 3.3 Intrinsic vs. User-Defined Functions
Magma divides its execution space into two syntactically distinct realms: intrinsic functions and user-defined functions [cite: 20]. 
*   **Intrinsic Functions**: These are the highly optimized, native primitives provided by the system. Intrinsics bypass the interpreted user language layer and execute directly within Magma's compiled C kernel [cite: 21]. The design philosophy dictates that kernel implementors utilize optimal machine-level data structures, ensuring that algorithms perform at or above the level of specialized standalone C programs [cite: 17]. Users are heavily encouraged to rely on intrinsics for heavy computational lifting [cite: 21].
*   **User-Defined Functions**: Magma provides a robust, imperative user language (with functional subsets like higher-order functions) for creating custom procedures [cite: 18]. Syntactically, user functions handle variadic arguments and allow for parameter default assignments via clauses (e.g., `identifier := value`) [cite: 20]. However, these are strictly kept separate from the kernel-level intrinsics, preserving the integrity and speed of the foundational algebraic core [cite: 20].

## 4. Pari/GP Primitive Structure

### 4.1 Number-Theory Focus and 1985 Origins
PARI/GP is a deeply mature, specialized computer algebra system whose architecture was originally forged in 1985 [cite: 22, 23]. Developed specifically to cater to number theorists, the early micro-kernel was written entirely in MC68020 assembly language for deployment on systems like SUN-3, NeXT cubes, and early Macintosh computers [cite: 22, 23]. 

As hardware architectures evolved over the subsequent decades, PARI transitioned away from 68k assembly towards a highly portable, multiprecision architecture written in ANSI C and utilizing inlined assembler for time-critical mathematical bottlenecks across architectures like x86, Sparc, and Alpha [cite: 24]. Today, it primarily uses the GNU Multiple Precision (GMP) arithmetic library for its multiprecision kernel, achieving massive performance gains for large operands [cite: 24]. 

### 4.2 The Tripartite Architecture
The PARI/GP ecosystem operates via three distinct but interconnected layers [cite: 24]:
1.  **The PARI Library (`libpari`)**: A pure C library that provides the core multiprecision types and highly optimized mathematical functions. It is designed to be embedded directly into C/C++ applications, bypassing overhead for maximum speed [cite: 24].
2.  **The GP Calculator**: An interactive, high-level programmable interpreter. The GP language features standard control instructions (similar to C) but abstracts away memory management [cite: 24].
3.  **The `gp2c` Compiler**: A bridging tool that translates high-level GP scripts directly into optimized C code. Compiling GP code via `gp2c` loads the output back into the GP interpreter, yielding a typical execution speedup of 3x to 10x [cite: 24].

### 4.3 Type Evolution and the "Zero" Problem
A defining characteristic of the GP scripting language is that it is structurally untyped; variables do not possess inherent types [cite: 24, 25]. However, the underlying PARI C-kernel is rigidly typed, utilizing a unique nomenclature for its mathematical primitives, such as `t_INT` for multiprecision integers [cite: 25, 26].

A major philosophical and architectural hurdle in number-theory DSLs is the representation of mathematical edge cases. PARI explicitly tackles the epistemological computer science question: "What is zero?" [cite: 22]. In PARI's architecture, exact zeros are considered equivalent regardless of their source [cite: 22]. However, dealing with mathematical imprecision required PARI to design a system where exact types and inexact types (floating point, power series with O-terms) are handled with distinct computational logic to prevent precision loss during deep number-theoretic proofs [cite: 22]. While PARI excels at rapid algebraic number theory, its architecture intentionally eschews the heavy infrastructure needed for generalized symbolic manipulation (such as multivariate polynomial formal integration), conceding those domains to broader systems like Magma or Mathematica [cite: 22, 27].

## 5. SageMath as Super-System

### 5.1 The Federation Philosophy
SageMath represents a radical departure from the monolithic design architectures of Mathematica or Magma. Conceived in 2005 by William Stein, the stated mission of SageMath is to serve as a viable, free open-source alternative to Magma, Maple, Mathematica, and MATLAB [cite: 28]. Instead of rewriting mathematical algorithms from scratch, SageMath functions as a "super-system" that federates, packages, and unifies the best-of-breed open-source mathematical software under a single, cohesive Python-based interface [cite: 28].

The SageMath primitive zoo is essentially an aggregated superset of the primitives found in its constituent subsystems. Its architecture bundles together:
*   **Pari/GP** for fast number theory [cite: 28].
*   **GAP** for computational discrete algebra and group theory [cite: 28, 29].
*   **Singular** for polynomial computations [cite: 30].
*   **SymPy** and **Maxima** for symbolic manipulations [cite: 28].
*   **GMP** and **MPFR** for foundational numeric primitives [cite: 28].

### 5.2 Interfacing Mechanisms and Coordination Problems
Integrating disparate CAS environments written in C, Python, and bespoke interpreted languages requires complex bridging mechanisms. SageMath achieves this through distinct interfacing strategies, which simultaneously solve interoperability while introducing architectural coordination bottlenecks.

SageMath allows users to interact with a subsystem in two primary ways:
1.  **Command-Line Interactive Sessions (IPC)**: SageMath can spawn background pseudo-TTY sessions of systems like GAP or GP. For instance, invoking `gap.console()` drops the user directly into a GAP interpreter, while `gap('expr')` sends a string expression over an Inter-Process Communication (IPC) channel, evaluates it in the background GAP instance, and returns the result as a string [cite: 30, 31].
2.  **C-Library Bindings**: For tools like PARI, SageMath hooks directly into `libpari` via Cython bindings. Calling `pari('znprimroot(10007)')` evaluates the function directly in memory without the overhead of string serialization and IPC communication, resulting in significantly faster and more robust execution [cite: 31].

**Coordination Bottlenecks**: The federation model creates intense friction when mathematical objects must traverse different subsystems. For example, converting a multivariate polynomial from Singular to GAP via Sage requires explicit, manual manipulation of the generator variables. Because internal memory representations of polynomials in GAP do not automatically align with Singular's representation, Sage must act as an explicit translator, enforcing variable mappings (e.g., explicitly commanding GAP to view variables `x0` and `x1` as ring generators matching the Singular output) [cite: 30]. 

### 5.3 Design Lessons from Federation
The primary design lesson from SageMath is the double-edged nature of federation. While wrapping external systems enables rapid feature parity with monolithic software, relying on string-based IPC interfaces introduces heavy serialization latency and state synchronization risks (e.g., if a GAP process dies, the Sage environment must capture the `SIGINT` and reset the workspace) [cite: 30]. High-performance federation demands native C-API integration (like Sage's Cython wrapper around `libpari`), avoiding the interpreter overhead entirely.

## 6. Cross-Cutting Design Patterns

As mathematical computation has evolved, several cross-cutting design patterns have emerged across modern languages to solve the tension between abstraction and raw computational speed.

### 6.1 Trait-Based Dispatch and Parameterized Types (Julia / AbstractAlgebra.jl)
Julia represents a modern paradigm for math-DSLs, eschewing traditional Object-Oriented Programming (OOP) in favor of multiple dispatch and a rich system of parameterized abstract types [cite: 32, 33]. Libraries like `AbstractAlgebra.jl`, `Nemo.jl`, and `Groebner.jl` capitalize on this architecture to achieve C-level performance with Pythonic syntax [cite: 33, 34].

In Julia, inheritance exists strictly on the functional side rather than the data side [cite: 32]. Mathematical structures are represented as a tree of abstract types (e.g., `RingElem` inherits from general abstract types, and a concrete type inherits from `RingElem`) [cite: 32]. Types are heavily parameterized; for instance, `Rational{T}` allows the numerator and denominator to be of an arbitrary type $T$ [cite: 32]. 

Because Julia dispatches on the types of *all* arguments in a function (unlike class-based OOP which dispatches implicitly on a single `self` parameter), it is exceptionally suited for mathematical operations where left and right operands may differ in ad-hoc algebraic structures [cite: 32]. Furthermore, because Julia is strictly single-inheritance for abstract types, math libraries utilize **traits** (via type parameter trickery) to assign multiple mathematical properties to a single type without violating the inheritance tree [cite: 32]. This allows a polynomial algorithm to be written highly generically, and the Just-In-Time (JIT) compiler will generate optimized machine code for the specific concrete base ring provided [cite: 33].

### 6.2 Lazy Evaluation and Symbolic Trees
Across SymPy and Mathematica, **lazy evaluation** is a dominant pattern. Mathematical expressions are stored as unevaluated ASTs (Abstract Syntax Trees) [cite: 8]. Evaluation only occurs when explicitly forced or when assumption constraints allow a logically sound simplification [cite: 9, 12]. This ensures that operations requiring infinite precision or resulting in massive polynomial expansions do not consume memory until strictly required. 

### 6.3 Categorification
Categorification, pioneered by Magma and adopted in spirit by Julia's `AbstractAlgebra.jl`, involves binding data to strict mathematical contexts (parents, varieties, rings) rather than treating data as independent numerical arrays [cite: 18, 32]. This pattern ensures mathematical rigor; an element $x$ is not just a float or an int, but an element of a specific cyclic group or finite field, preventing illegal algebraic interactions at compile time.

## 7. Lessons for Project Prometheus

Integrating these historical and structural insights into the Project Prometheus hierarchy (Tier-A++ through Tier-E) reveals a clear roadmap for what architectural paradigms to adopt and which to explicitly reject.

### Tier-A++ (Foundational/Axiomatic Engine)
**Adopt**: The strict AST node generation of SymPy (`Basic` and `Expr` classes) combined with the explicit algebraic typing of Magma. Prometheus's lowest tier must not treat numbers merely as floating-point primitives but as entities bound to specific "Parent Structures" (varieties/categories) [cite: 18]. 
**Reject**: The untyped implicit nature of the Pari/GP interpreter [cite: 25]. Foundational axioms require strict, provable typing.

### Tier-A (Algebraic & Core Mathematics)
**Adopt**: Julia's Trait-Based Multiple Dispatch [cite: 32, 33]. Implementing algebraic structures using parameterized types and multiple dispatch allows Prometheus to write generic algorithms (like Gröbner basis factorization) once, and have them execute at near-native speeds regardless of whether the base ring is an integer, a float, or a dense polynomial matrix [cite: 32, 34]. 
**Reject**: The single-dispatch OOP paradigm (e.g., traditional Python classes), which scales poorly for ad-hoc left-and-right mathematical operations [cite: 32].

### Tier-B (Calculus & Continuous Mathematics)
**Adopt**: SymPy’s robust assumptions engine and lazy evaluation model [cite: 12]. Calculus operations in Prometheus must assume variables are complex by default, refusing to simplify expressions (like $\sqrt{x^2} \rightarrow x$) unless explicitly constrained by the user (e.g., `positive=True`) [cite: 12]. 
**Reject**: Immediate evaluation of continuous limits or integrals, which can cause stack overflows or precision loss.

### Tier-C (Applications & Domain Modules)
**Adopt**: The SymPy "Core vs. Applications" dichotomy [cite: 7]. Physics, statistics, and engineering modules should be built as independent packages that import the Prometheus Core, ensuring the fundamental engine remains lightweight [cite: 7]. Additionally, adopt SymPy’s rigorous PR vetting (strict CI testing, mandatory docstrings) and 1-year deprecation cycle to curate this tier carefully [cite: 14, 15].

### Tier-D (Federation & Ecosystem Integration)
**Adopt**: SageMath’s philosophy of not reinventing the wheel, utilizing C-level library bindings (like Sage's Cython wrapper for `libpari`) to interface with highly optimized existing tools (e.g., GMP, MPFR) [cite: 31].
**Reject**: String-based Inter-Process Communication (IPC). SageMath's reliance on pseudo-TTY interactions with GAP causes parsing friction, synchronization issues, and latency [cite: 30, 31]. Prometheus must use direct memory mapping or FFI (Foreign Function Interfaces) for federation.

### Tier-E (Knowledge Representation & Real-World Framing)
**Adopt**: Mathematica's Wolfram Data Framework (WDF) [cite: 6]. To reach the pinnacle of math-DSL utility, Prometheus must bridge pure mathematics with real-world ontologies. Incorporating primitives like `Entity` and `Quantity` ensures that dimensional analysis (e.g., meters vs. seconds) is handled at the lowest compilation level, transforming the system into a neuro-symbolic engine capable of handling real-world datasets [cite: 3, 6].
**Reject**: Mathematica's flat namespace for 5,000+ primitives [cite: 1, 2]. While CamelCase avoids user collision, a flat global namespace creates severe cognitive overload. Prometheus should group real-world entities into strictly defined, hierarchical module namespaces. 

***

**Data Presentation: Paradigm Alignment for Prometheus**

| Feature / Design Pattern | Source System | Alignment in Prometheus | Implementation Target |
| :--- | :--- | :--- | :--- |
| **Multiple Dispatch** | Julia (`AbstractAlgebra.jl`) | Adopt | Tier-A (Algebraic processing) |
| **Parent Structures** | Magma | Adopt | Tier-A++ (Axiomatic grounding) |
| **Flat Namespace** | Mathematica | Reject | N/A (Use explicit hierarchical modules) |
| **Assumptions Engine** | SymPy | Adopt | Tier-B (Calculus/Continuous limits) |
| **IPC String Serialization** | SageMath | Reject | N/A (Use direct FFI/C-bindings instead) |
| **Entity/Quantity Types** | Wolfram (WDF) | Adopt | Tier-E (Knowledge Representation) |
| **1-Year Deprecation Cycle** | SymPy | Adopt | Global contribution guidelines |

By synthesizing these historical trajectories, Project Prometheus can bypass the architectural debt accrued by early 1980s systems while retaining the mathematical rigor and computational speed developed over the last forty years of computer algebra design.

**Sources:**
1. [stephenwolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdZp45uZDDHi0LBB96_3QS9ycRMuYGy68b90g8sqbBD1gwx-1pvUoeiXx2tPcpXYPaCEM8dfTvF94g6mvz-mNRZw3w4J6eBUZc_dBVKWrgN99YhS3Cl-L-hiFyAQf-dHPDXU-tAt-V76CY2Elhb0Q-rPR9iZvbdXSVzWpOPCxmH18ChieIgA==)
2. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAGHigPQa8Dn-5QFQakgXqkttdw5Hu6uzJq6xks1sxv9kbLShIvoDv-FAlKlIWymd_ALZSlUMi9mCZD4doF7L1B37AulicsDO0pD2RzpOrSzUZFNI7rNmgMjbViaGcwsyy8wQ=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCjSrUW_Y_aWoGAR4oLMZvEHJW8Ycgz70pQzNMWteOiZAbVTCE8v5ZtDyldlscHNC_sx8oudoJYkRAPUf-Gl_Ogri8StUhrIQ6MykjWeDvpMOyJted2LBZOQ==)
4. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGgl1k8cujg-W8d9qph0AzAlu8D9SEPP-eCCL8LjC9SSWrJxms9fWM3XcDUrptnQtX1jAJQdinbGz0dSDlBPTussJgMwhYg1S75Y7Yi8MzM4v8ycq_OVN9qQQG4ZqoKlFrVF9Nk4VUUf0r6Q2vU7usugAqOp6KjRVa3eQPEd_RWstHUbCsNqD8FL1-lacHiEkJacGIil_GYa_f4g==)
5. [camel-ai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLHceunKDot_PmLeyh__aErrHr3uUFbarLepcOmFVLHwBS1YYE18JM8G5lEtNXzJRqPPSlAeri_2uFr4xJtRtv1XBFfFoIK3VahOFKhnv-s012SUbs_irf0UlOEYIqMwh2H4Xq5Wqlm5w22ej6r8-M6tPbWwHehITxhukhLfyDBU6SXjwpnk29HZvfwiCs2ll2DZrWnsijyVhQTjMmJ1YsOIngFiVBB5x7LbCpbOB7YoIAhl3dNbxYYXnDFyKF0CPm9Q==)
6. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTlBsz12HG4Fm7jy1rQ6GipOr6SPt2d_Vg4_n_4jCLEemWua2IATKyCehfOo089cz0ehOKpbzR8oOpNfLvH3w2vyTs7OUGLGxY2lUD9vnfaW0SqtUajVWMXwvPpraJKkxO0lWCLnRV0sbbbF9qt0uy86u-AfXChUlZtctDUgTS)
7. [lanl.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAR-Fs5lU-9-rpe9iRZQFbkmpd4QkzfdMKz9jCQVLDvL5q-_Yk-VrOFADvjBPIL0MIGF9o3lmuStpMgEddrT5r1lDhAg94bCFztColUIYqGpFOSzzXSlneunxz0XBzocslnvskxTQTr8ZZTIkdn-A6jhrmSEARmuv6EZAqHsnZjHA9k8dOtQ3iEWypZDoxfEn9eGtUsgOTgnkc)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHn5DRyrEedHV_skOr3_2KyzUpPt3nV45NiUBYzIO04joGXf-nICsuW_pB_YfLmFo5AM-niN7oeDvNs7LB2mIUqbgK_74_fdZa9Wkp-zdtPfDUA8TnW3dzdCGIoEwb0LEHEIsoMZQlu4YgKbP5p8nqtGiXSKOEwOyJKulPmRkGj-uELtDw6nmWPAsX_)
9. [sympy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7_8_A_PuG4Ao2JcNPLcYlBLwRQvyIamDGlugnGTMI_smZ8nC0-7VGJqmE-iIR0qYPEcf5ojR13cl9PnNKXXNQvfnC17EtEX3r9uTaGUa4nYA68hHNY7qlxaZIp8jIchCXR26l1g==)
10. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyOHtIklUjeLu-JLov9GyUuYgK7ulcW4F3WEIPUPgxLwXbQ0eHwWOZ2vPoiVlBBVTT_HobzdLbBojU1yskaw-sJv1iva1erqJ_MglNg6LYShOpUyw1w0Hdjo3ZXbL2TUDN5A8SZ5TyIv3q8fcStO55diAMa2HoJgg5cDez1wJwtUiBEnozSYqAB4uTiwHdL7NwhV0GcgBM0km81Kr2yDywKHPu)
11. [sympy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFlMRaG9BP0E7s2iNaRjOynpf6jTMDEqm6Bhb3cYcOZKXnwywVz-PzwnIPetMyzRVZn8j7P_TwKdXdwKSXj-LjJZfqA85y5H_IRsP5h2AFOAvBE6n1Rm6o1ILZIgqvTLEfT1Ocd-mF8RWiSmYt0jxQ5A36GeaYRA==)
12. [sympy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeLU-vfw1-YiM4RV9t3n4Xqydxbvc96MOo4tXqUsmThbjfkzhc9LAcnI2kuZzUK6Zr6oIeUmCFzfZdd33Per-qWbi31JLrVdWdFk-Elap8JaL-qwebk3Q-XjXiHdFEqlqqem7tRYO7h-1SUA==)
13. [sympy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzpkc_fT1A1A7Cml3Hax1qAioRZYyXjKK7WzR-lyJ5nEiaLNeDKoNrQABi27e7J2LZ9eRPe2xarhyZBvozxeqbO5gh7tEa6JNgh8SxFuCjMCgAGN9S9hZDwhdvU9Zuedap_Kn6hj2UcE-ZS7V-GIlsmqDPwy1iWbBDxG_LwqOa9eYz)
14. [sympy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERsPovG2IdPf9_tEzzyJpKYuh_VrJUIJ5HAZcF1YB8ery-aUf7HokKV6q9qUhcJAV3-aI9nzfG_5xsdMTIOuYOYTR4qWXYX4XGFbBDLvAbCm50sqqBrpBf244unYsDFsZA7FjlUxaxpoRwzBvAB5ihpqOQbgoFNTYgNRj_5TNt3soYv0BCH0l0JATx_3U=)
15. [sympy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWHSCK2rPmTw0q1WvIeOxN-H0VrZQ0c4qQccm01fbhfbzxBg-35mSoM_lIXQkIII_5qs35eNE23tQrTOg-bPrV1UgV-iBOaNhe9pm0Uxkrh-PONStSglNsJchOCVjIlrHlmeNhYYqxneMR9IxmJe014wHmvhQmNIw=)
16. [quansight.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJgouSt94hTQ30HRSOR-kovn8nU_7nI0Ku1qA559DcJMGxCQ97NpT-G9QLhi8MuNXJ11Z7JODqZ0ttCc1aMVD0TFKi8-3QvvS_vwSHWpowMlNsvnDeC2g59J0XPZOFCcNW9cx5FrkPZw8=)
17. [uzh.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAnAkRNDmQ4RT45TQYXiZZwWF9cMpyyhc2BVygQw74oubqqMp0v60JpjfRDX_s2ftMRYUsYQX_Fn1XIOn756ArsYbG05wk01jEE3YmGv2Rs5zzT9zHnOQYeEcgj6THb-tk4v7OL6lbNvv5GISOTF8=)
18. [ru.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9y9Eh1z4RS6Q_i2Rc8aQBXAiVkoa05DDLDeFXPjtQm4rjXV76MegRrn-B4zuM1j--WnVOzy2ECLi9TAJO1Mg3ITdqD06jvejsrL1woViHOTXS4aBtAcLhxAOwcEhbrrgPf_pVAgXfTMM=)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqJzuqAk8Jt75GaeDwqH8kBsae0p02zNGfchapx4BP9WQyMvqZ5Zg7YqbPneRblUW7U6-CCu8UFvIBKG7reyF8G94y2G7TMlgLt1-MFVHbpnTlEFdUj97bzDMOm1NbRfmcItJ3ZGidnZ03qB3z7JVoDskdNCOMhOAL_uEqI6oeN2CfAtR0-c-HViGMNn1JkFRJVqrFjrYcwVdSepc7BECZTl4aD60nDq_VXX4=)
20. [usyd.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1OtLumFy38WUr4X-Rp1Q8lJWQYCmr_9Wn0wFed1kBiPLFZArEwtkSPiaudvukmNwyZ3-ewvR8ZG-jSJWUbJDooL_cJ4r0sQien95T8UAeSojZ-O_CPkebj34WeY6bAcAyTrbHr45KORtaBls=)
21. [dtubbenhauer.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4NYzk4JxzFWfQS1cft5kmXnMVyytqHAoyWS7aYrcz2tGXChyJyxfTzWyXUKF7NVhsB_hplzW4NxrqCXrANksOCmyb3-ZJ3lLGZXqeX-xdSLgdNygwS4WiFZukXZeKyjk0YiPdsy37)
22. [cheat-sheets.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3FvfxnzDoCuDb7SNqP8fJ8-7Ile1iYxGpzi2s4QTGQJU-BB4XuPgpy9dBVAJ6EFTeWTkiUCeoEniqE9wb5Ct8egIQ5ysMgxW_OeSsu7Ye8NMiIE_D5ELrN7x3GgpPLCpU3mQhGqnxyAr9TEr5P2yHxmXqvAQoNQ99CssAYw==)
23. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS25v1bDqpScAHySkzXcOTKAm36110nScl0WC_PEPbvT1Z_vQRLhY5OWcAjhLJ4L8HVKGJcnzfKlPXbFN8KPvTvTqiK3niDkQJIx7CkKYsDVDu9ucjgUGdaeF2KQvn5mVZdqVFqoyRdSEpnmto6EyA-foRtBt4)
24. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-t2m6uIAXW1vGcClv18f2rc-5khXOKKcbgYF4Op2qCIntloxx3jqS0pICYxw6TvQ3W1SyWbQhjcXu9Wj1n5zY5WPqLaDI4rFCc5nFeyH0---YglnwK984zJXg5FTOV5Cmvytg-KOI2rXLv7Rnce5_Z_OET-OD)
25. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJZAhwYz7ftOJsK8XtYB8kb4LwMHbIPNY2TjpMbuGv_lH1oN3dUpTDycgVH-p5BnUqXDFkC_djSu_4wo7AlNA-hkFWiZ1IZttnJFOn7WasOGSrzynQup55uo4OeUp8r322JtBwPdqxHO8sqBLHf7FjLn7x7viK)
26. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsTc-20uthVfLICBYaRp-AddySwMHzYE4rvqCWEhwbwGNpokQcBMfCJuG2qF2h_guXeqAj2F7x1lu5hfcYyMWUWEWkQ1FzIMSguiSUBf_XVre0a0yqL7xkzHqMk-Nj-E2roN8FurL5_JItqlmSD7dGUes5HylLHQ==)
27. [u-bordeaux.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZ1DGVvH85SFHmMSWFeTkxO8oeLrT7LK54rJmToeyLfo_FuDgTGADR1NbRp1-g1bay1eW1arWiPy0dd9grMTd7cpIicr9opQRgmpIWTPGiaVGgcMGGQdBY_nwGwlV9_K6fwKvOOI-x-kFMBIbK_ZYbQc6iJt-k)
28. [sagemath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFudrfAxpN7_wIf0i8YaITaM7EVdQwf0ayoCPxfFDsUDmFW4lQmg1Bt9beDBWodiVt2lu-a2M9arVlOkxK6rjD-nmeYfQ1I2TDy0By6VTtv4J4jI0FJT36hq92YYS9KXhLBmtzulGe6QtMsWQ==)
29. [sagemath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHF6Co92h6CiVft-vI02VbH5Dp8jLZrQX-LScc27XNLQWN2JucR-O2T-Quiji-x4PAwS3fi2loS_1mpI3EwyvfuUvy6lELD3Nt_s2YCKFUVvHE9JTqKJ9N-918jd-vMag==)
30. [sagemath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcscuaPBfzmvEvzBxuVUO1Vz3xu1IhISt7-IKcqrFUo1O__OvDoVoiFPGs7mZ5MalClVP8qp-5OqB5voyZSZ57u4b-Dv6ooj1pyCF9SC3exKmE8CGaWiXB_Im5PBctsSwbzsd5W8BAXezQ3jZp0WjqEHgiK1uYJOPBw2daB9vhoy825-I=)
31. [sagemath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXQC713-RF5OPawIU5isQCAgoBeiXTr4kdrhpnpZIyucceQWCLDjxbmcwzHq7Oz5VoFScofy5qbPZiyfXYITUdL1PJoZY71uPoGfSpogbQAr6yOtTSDWnwy85_yZsOd2qbsIIa0bw6IebDkVOU-OQ=)
32. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkw-ZsLx5hOVLSCkp4qN_Mb4rOOkQ3TRrZ_Jzc8RWKrYb6jlcuKH55PjZBX69P8DzfFxP7tJE8L5_J69EZWFqzPp5YAz05BEtDUll3l6Pv5W8gIbAAfkciLezRhkPLWwoYLsWVDAmRdWXz05I6Y2b3t-pseg==)
33. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3VIXU0flHK7sfN-VMdDtDBFXP6ZtqWh8Bug9r3df9yNwjWZa2TSYcVatWCMLSt4wTioeqgP2J1cTmQlIJ1BbbnXv8pVXcZwe7LpAcGg06ysjluGvbQVn7MeW1OXI8S9Rh9A==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKz8Xcn83rDL9MHvegP2bP8ofEXDRwbvgjK8L3jjx7c06_u9jB2D7okGF_KcgGNTPdATIV4rsoUk7xyGPzndz8gdEPbpG_9rV1bYSAfBSzYRA-Y-C6xQ==)


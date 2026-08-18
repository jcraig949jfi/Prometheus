# Prompt 08: DR-040 — Survey MulticategoricalCompositionRule + ColoredPROPCompositionRule + LinearTypeUseConstraint supporting lit [Tier 1]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpSU1GYW9DakM5T1lfdU1QdnFuLXNBdxIXaUlNRmFvQ2pDOU9ZX3VNUHZxbi1zQXc
**Elapsed:** 394s

---

# Verification Report: MulticategoricalCompositionRule + ColoredPROPCompositionRule + LinearTypeUseConstraint

**Key Points:**
*   The candidate anti-anchor requires multidimensional expansion. The literature explicitly separates Generalized Algebraic Theories (GATs), Cartesian Double Theories, and 2-monads.
*   **Colored PROP** semantics and **Multicategory** semantics are orthogonal coordinates. Recent 2025 work necessitates explicit separation of multiplicative and additive topological routings in graphical languages.
*   Linear Type constraints in the AlgebraicJulia ecosystem rely fundamentally on categorical semantics (e.g., Dialectica categories, Lineales), moving beyond operational memory-management definitions.

This report serves as a substrate input for Project Prometheus. It evaluates the candidate `Survey MulticategoricalCompositionRule + ColoredPROPCompositionRule + LinearTypeUseConstraint supporting lit` against primary literature from the 2024-2026 window. Findings are formulated as actionable primitives, anti-anchor pins, and work-queue entries for the Wave 6 meta-substrate, specifically targeting the `composition_rules.md v0.2.0` schema upgrade. The analysis resists conventional computational gravity wells, ensuring that mathematically distinct invariants are assigned strictly independent coordinates.

---

## (a) PRIMARY SOURCE CONFIRMATION

The verification candidate touches three interdependent but mathematically distinct coordinates. Primary source literature validates the candidate but mandates the strict separation of invariants. 

### Coordinate 1: GATlab and Categorical Doctrines
The underlying framework of the AlgebraicJulia/Catlab ecosystem has transitioned to **GATlab**. 
*   **Primary Source**: Lynch, Brown, Fairbanks, Patterson. "GATlab: Modeling and programming with generalized algebraic theories." *Electronic Notes in Theoretical Informatics and Computer Science (ENTICS)*, Volume 4. **PEER-REVIEWED**. Definitive publication date: **December 2024** [cite: 1, 2].
*   **Result**: GATlab replaces the legacy Catlab backend by providing a domain-specific language for algebraic specification embedded in Julia, strictly based on Generalized Algebraic Theories (GATs) [cite: 1, 2]. 
*   **Theorem/Axiom Statement**: The primary source defines GATlab's mechanism as separating syntax from computational semantics: *"Using GATlab, the programmer can specify generalized algebraic theories and their models, including both free models, based on symbolic expressions, and computational models, defined by arbitrary code in the host language. Moreover, the programmer can define maps between theories and use them to declaratively migrate models of one theory to models of another"* [cite: 2, 3].

**Anti-Gravitational-Well Intervention**: The classical gravity well asserts that "a categorical doctrine is a 2-monad on \(\mathsf{Cat}\)." This framing must be explicitly resisted in the substrate. 
*   **Alternative Source**: Lambert & Patterson. "Cartesian double theories: A double-categorical framework for categorical doctrines." *Advances in Mathematics* 444:109630. **PEER-REVIEWED**. Definitive publication date: **May 2024** [cite: 4, 5]. (Preprint arXiv:2310.05384, October 2023 [cite: 6]).
*   **Exact Theorem Statement**: *"We show that every cartesian double theory has a unital virtual double category of models, with lax maps between models given by cartesian lax natural transformations, bimodules between models given by cartesian modules, and multicells given by multimodulations. In many cases, the virtual double category of models is representable, hence is a genuine double category"* [cite: 5, 6].
*   **Coordinate Distinction**: 2-monads and Cartesian double theories are **TWO** distinct coordinates for doctrines. Double theories present the advantage of being straightforwardly presentable by generators and relations [cite: 5, 6].

### Coordinate 2: Colored PROPs vs. Multicategories
The substrate candidate conflates `MulticategoricalCompositionRule` with `ColoredPROPCompositionRule`. These must be isolated.
*   **Primary Source**: Chardonnet, de Visme, Valiron, Vilmart. "The Tensor-Plus Calculus." arXiv:2512.21965. **ANNOUNCED-NOT-PUBLISHED**. Date: **December 26, 2025** [cite: 7, 8].
*   **Result**: The authors develop an internal language for semiadditive categories utilizing a colored PROP, not a multicategory. 
*   **Exact Theorem Statement**: *"In this colored PROP, whether wires in parallel are linked through the multiplicative structure or the additive structure is implicit and determined contextually rather than explicitly through tapes... We design an internal language for semiadditive categories \(\mathcal{C}, +, 0\) with a symmetric monoidal structure \(\mathcal{C}, \otimes, 1\) distributive over it, and such that the homset \(\mathcal{C}(1,1)\) is isomorphic to a given commutative semiring"* [cite: 7, 9].

### Coordinate 3: Linear Types and Lineales
Linear type constraints in categorical modeling are governed by Dialectica constructions over symmetric monoidal closed posets, not simply by affine/linear logic programming paradigms.
*   **Primary Source**: de Paiva, V. "Dialectica and Chu constructions: cousins?" and related 2020/2021 modernizations in Dialectica Petri nets [cite: 10, 11].
*   **Result**: A **Lineale** is a distinct coordinate representing the poset-reflection of a monoidal closed category [cite: 10, 12]. 
*   **Statement**: *"A lineale is a tuple \((L, \sqsupseteq, *, e, \multimap)\) such that \((L, \sqsupseteq, *, e)\) is a partially ordered monoid and \(\multimap\) is an internal-hom for \((L, \sqsupseteq, *, e)\)"* [cite: 13]. This provides the mathematical basis for `LinearTypeUseConstraint`.

### Table of Distinct Coordinates (HARD-5 Enforcement)

| Invariant Coordinate | Definition / Topological Property | Substrate Application |
| :--- | :--- | :--- |
| **Operad** | Single output, multiple inputs. Operations map to exactly one object. | `primitive_registration`: classical syntax trees |
| **Multicategory** | Colored/typed generalization of operads. Multiple colored inputs to one colored output. | `composition_rules.md`: structured open systems |
| **PROP** | Multiple uncolored inputs to multiple uncolored outputs. | `composition_rules.md`: quantum circuit architectures |
| **Colored PROP** | Multiple typed inputs to multiple typed outputs. | `composition_rules.md`: Tensor-Plus Calculus routing |
| **2-Monad** | Endofunctor on a 2-category with multiplication and unit. | `training-corpus filter`: legacy doctrine models |
| **Cartesian Double Theory** | Small double category with finite products. | `anti-anchor pin`: modern doctrine syntax |

---

## (b) FOLLOW-ON WORK (2024-2026)

In the 24-month target window, several critical advancements refine the application of Generalized Algebraic Theories and graphical linear models. These represent immediate work-queue entries for the substrate.

**1. Pyrosome: Mechanized Metatheory for GATs (July 2025)**
*   **Source**: Jamner, Kammer, Nag, Chlipala. "Pyrosome: Verified compilation for modular metatheory." arXiv:2507.06360. **ANNOUNCED-NOT-PUBLISHED**. Date: **July 08, 2025** [cite: 14, 15]. 
*   **Context**: Automates syntax-related reasoning directly at the level of typed syntax specified as a generalized algebraic theory [cite: 14, 15]. 
*   **Flagged Claim**: *"Pyrosome defines a formal, deeply embedded notion of programming languages with semantics given by dependently sorted equational theories, so all compiler-correctness proofs boil down to type-checking and equational reasoning"* [cite: 14, 16]. 
*   **Substrate Warning**: This is a **CONDITIONAL** result. The "Y proved X" claim (Jamner et al. proved compiler correctness) is conditionally bound to the representation of semantics strictly as *dependently sorted equational theories* embedded in Coq [cite: 14, 16]. Contextual equivalence is explicitly rejected as a suitable property in their framework [cite: 14]. Prometheus must strictly register Pyrosome's equivalence as "Deeply-Embedded Equational Equivalence" (a distinct coordinate from Contextual Equivalence).

**2. Tensor-Plus Calculus Extensions (January 2026)**
*   **Source**: Chardonnet et al. related announcements in quantum computing literature. Date: **January 2026** [cite: 9].
*   **Refinement**: The diagrams are used as parameter elements of a commutative semiring, enabling the universal modeling of non-deterministic, probabilistic, and quantum computations [cite: 7, 9]. This supersedes the necessity for explicit world annotations in linear graphical languages [cite: 7].

**3. Linear Arboreal Categories (December 2024)**
*   **Source**: Abramsky, Montacute, Shah. "Linear Arboreal Categories." *ENTICS* Vol 4. **PEER-REVIEWED**. Date: **December 2024** [cite: 17].
*   **Refinement**: Strengthens the axioms of an arboreal category to exclude 'branching' behavior, creating a linear arboreal category. 
*   **Substrate Value**: Directly refines the `LinearTypeUseConstraint` by defining linearizability conditions related via adjunctions [cite: 17].

---

## (c) FALSE-FORM RECURRENCE

The substrate requires active defense against gravity wells propagating false forms in recent literature (2024-2026). The following recurrent errors must be captured as `anti-anchor pins`.

### False Form 1: "Categorical Doctrines are strictly 2-monads"
**Recurrence Context**: The gravity well of Category Theory literature heavily biases toward Blackwell, Kelly, and Power's 1989 formalization. The false form asserts that to implement a doctrine algorithmically, one must construct a 2-monad.
*   **Observation**: GATlab explicit literature pushes against this. Patterson notes: *"The standard approach to doctrines is based on 2-monads and their algebras... Compared with 2-monads, double theories have the advantage of being straightforwardly presentable by generators and relations"* [cite: 5, 18]. 
*   **Action**: The anti-anchor is **REQUIRED**. Substrate models querying `doctrine` must explicitly surface `Cartesian Double Theory` with equal-or-higher weight than `2-Monad`.

### False Form 2: "Colored PROPs are equivalent to Multicategories"
**Recurrence Context**: Graphical calculi literature frequently collapses the vocabulary of Open Systems. 
*   **Observation**: Multicategories map \( n \) colored inputs to \( 1 \) colored output. Colored PROPs map \( m \) colored inputs to \( n \) colored outputs [cite: 19, 20, 21]. This is mathematically distinct. Conflating them leads to invalid topological derivations in graphical tensor routing. 
*   **Quote / Proof of necessity**: As observed in Chardonnet et al. (2025), a colored PROP is required to map a list of colors \( A = A_1 \parallel \dots \parallel A_n \) through simultaneous multiplicative and additive structures [cite: 20]. A multicategory cannot natively support this without extensive workarounds (e.g., Poly-like wrap/unwrap operations).
*   **Action**: The anti-anchor is **REQUIRED**. `composition_rules.md` must strictly define `m -> 1` (Multicategory) and `m -> n` (Colored PROP) as independent graph schema nodes.

### False Form 3: "Catlab/GATlab linear types are analogous to Rust's borrow checker"
**Recurrence Context**: General programming language literature (e.g., Reddit, blogs) attempts to frame Julia/Catlab type systems as "children of Haskell" or akin to "Rust's linear types" [cite: 22, 23]. 
*   **Observation**: This is a semantic gravity well. Rust uses Affine Types for memory management. GATlab and the AlgebraicJulia ecosystem use Generalized Algebraic Theories (dependent types) capable of modeling *Lineales* and *Dialectica categories* for systemic resource physics (e.g., Petri nets, epidemiology) [cite: 10, 24]. 
*   **Action**: The anti-anchor is **REQUIRED**. Prevent the LLM from explaining AlgebraicJulia's `LinearTypeUseConstraint` through the lens of memory safety. It must be anchored to categorical logic and Dialectica semantics [cite: 10, 11, 24].

---

## (d) RECOMMENDATION

Based on primary source verification, the substrate inputs and operational directives for Prometheus are as follows:

**(i) Evaluation of the Anti-Anchor Candidate**
The candidate `Survey MulticategoricalCompositionRule + ColoredPROPCompositionRule + LinearTypeUseConstraint` is **TRUE BUT NEEDS REFINEMENT AND STRUCTURAL INVERSION**. 
*   *Inversion required*: Do not treat Multicategories and Colored PROPs as additive features under a single composition rule. They are divergent graph-theoretic coordinates. 
*   *Refinement required*: The `LinearTypeUseConstraint` must be mapped explicitly to the implementation of *Lineales* and *Dialectica spaces*, entirely divorcing it from operational/memory-based linear type definitions.

**(ii) New Sub-Anchors and Companion Anti-Anchors Discovered**
Register the following as **`anti-anchor pins`**:
1.  **`PIN_DOCTRINE_BIFURCATION`**: Whenever the substrate processes "Categorical Doctrine", it must fork the evaluation path into `[Path A: 2-Monads]` and `[Path B: Cartesian Double Theories (Lambert & Patterson 2024)]` [cite: 5, 18]. Path B must be weighted highest for schema-generation tasks.
2.  **`PIN_GAT_DEPENDENT_TYPE`**: When processing GATlab, prevent the model from collapsing Generalized Algebraic Theories into Standard Algebraic Theories. The distinguishing invariant is the requirement of **Dependent Types** for GATs [cite: 2, 3].
3.  **`PIN_TENSOR_PLUS_ROUTING`**: Register `Tensor-Plus Calculus (Chardonnet 2025)` as the definitive primitive for colored PROPs handling simultaneous multiplicative (pairing) and additive (branching) structures without explicit tape annotations [cite: 7, 9].

**(iii) Work-Queue Entries and Schema Updates**
State the following actionable edits for downstream consumers:
1.  **`catalog edit`**: Update `composition_rules.md v0.2.0` to define five explicit topological domains: Operad, Multicategory, PROP, Colored PROP, and Cartesian Double Theory. (Enforce HARD-5 coordinate separation).
2.  **`primitive registration`**: Register `Lineale` as a core algebraic primitive: `Tuple (L, \sqsupseteq, *, e, \multimap)` where `\multimap` is an internal-hom for the partially ordered monoid [cite: 10, 13]. Map this primitive to `LinearTypeUseConstraint`.
3.  **`work-queue entry`**: Initiate a review of the **Pyrosome (2025)** framework [cite: 14]. Task: Extract Pyrosome's mechanized inductive formulation of equivalence preservation in Coq, and evaluate if its dependently sorted equational theories can be used to formally verify the `GATlab` theory morphisms.
4.  **`training-corpus filter`**: Filter out casual blog posts comparing Catlab to Rust/Haskell from Wave 6 meta-learning [cite: 22, 23]. Ensure training density is maximized on ENTICS Vol 4 (2024) [cite: 2] and LICS/arXiv (2025) primary literature [cite: 7].

**Sources:**
1. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE36vh4udAFPNphF7o3-YSf1OuvP8Rgepi-n_RNtBSEEx6ot_CT1o9DQLEIxOaqmVac8Vy3yZxpDmEThKHlM273GQP_3rOE1b9BArNN1obHCx-bH9iPK3imytnhsH0A)
2. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhLgbw3Y7Howz5sSgR_34OI9i9Ykv6a1Eddii3nY6D83PQ2d0sVpFqFMVWeMcPsAC7sweOz4zlVV1dtdz8Eork4nnPnIbPR4aXYPEIMUsmRq1HebCPsQEVKB8tq0PzqhIwfs3Rb7yOVhHe7KOZTHnTHg==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcZhT7GendS3Zx-OhHM_jnelVhwA8oeKbhMirJQ3ZFEwoENEo4xagn3eh6nDyHvzmD7EBj2FN6YXRc5xyegoDBh-Fm6X6Tlz3slPSA0S-mhcXu4FyIvJOwXQ==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBS2c-a1ueSS1SyZyTRc28h6F3DpaBvenMvjP98RSbn9AYcS4FhvvNx13flHqQZfZZaAVEslZOm-DeJSAGpGd3bE0ANY4ywDOlnQqNiEk_WnrWluPAyj1WRH8xqxyZDbOxUplbcY3XcyOe_sl4Gd2g8p8MTPe6csGd0MzMQGSj7orAIgWJrQqsDXfKn9b-Mr9pF_MnZe8CmFWdlMXsSppJVZlzcqkPWTXxuxrh0hWPLkFmhMQMU7jP2LC9nA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMevYtCY_BGkVa3Shugd4YBhYAl6y2PyG0zcHflMNduphKmetB_JdAjyrYEqkAwdLV_JHRQbdkBbCe6nLEDecpFQBJorMvtPokDpdbwnd59fX1p32N5Q==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVVmmqt1cXKZ6crIuISN6CnsQcSG36Nca5D1pJ8cJWMgtddnKOF8rAwDlK4FFRs8VtckQgIM8gImxoTkEdvBXQFIXJ9DOjlIxTaQIdzOD9vhW_ivssLA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGJOvf7yJUfJr4HI8WrVXI0xRz7ka2JnZOl6P9AFuIZ8-AY4VOUOI_J5WM56QsXhIt8wpJFFFDMxBe7OnTirWc6mMafbQiHaZxm85Bt7F2pW0xZYlrnQ==)
8. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE33oj5MoBJbMeXz3btH97bRgl4xUXcCWZveniCpUVBlt9b_9OFNTznFhfB3SnBNrRTFFv8TAjOWKDayE6UI1DmsifAyrCSvHvGgzr3r7ACF8azgV57jN1WTu7fPvd3NhRfdPg49dqQNQmnEW4h83jnsQ8=)
9. [quantumzeitgeist.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHANyDd0JuwNjviJxpuNl6CgQ6REjh7GBgkxza70K2xQ2wC1qp9n6beL_qwmkc_IUThry9tcONxTXk53enUPavpDxOcJ2ofA12lFPy5JZGwfi0Wfv1u_JRfGD9yWXj8X7ufkUBR06wqrjBxFa8LimGIT8gkcC2Kta-boObw3NtZmVYYXEAkm-Kq0RPz7g2Pof5r_-CSlBo6QcGsPB3k7UA1n5XZcqHZFw==)
10. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdy9B6poVpHugDmgvxAMVpF4nnahlK8A06aDJ9fz38_1wohVa33KXgHZHDq19jqgrccHEVsWsHxFTEKtBM0sDhePgAu87LN8YZc-YzuadmNzEYAlt9M4NWYvKsbgBYEkYinu_oVNRn9jB9w0G5)
11. [mta.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqpVshn8F1bMU5wnwUMaL90XdMcQZoQosSftfWcJgYSKRbajh5l3avqon7WYOZ-RaaCnL3wCP_TfvBlxA-odl7v7t-rb0b72tuXDdnGPZLIRCDbQLu4n0y0Hh62tFviIrZxPqQI_k=)
12. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqBfPmLkQiL-J9Ejibr9evL_Vlo9fkJ6vAZ151ZCTCDadV2gttnRDhw4Y1BnoLLHAE5CrIu9WenlsCgZcxdRwlqO2NJaAsUrk-OPGzJphV8jT3-JzliuE8X_PpU80LsuM0)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgfLDjz8xbBB2w2jEb5dZDNThJpEOY0f6abs_IIhcdzCgQu8zYIefh0OskGJqunxr6wELefiOKLe4r_hblbgPzOGemmSpM_puZYsnWbSeMKbXKzavzFg==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyPahDMWCn58JY4g6u2nRrRmZGYZYieTskvkSY6ThSaWR9yuOccw-r26Wlb2e6deKTJ1yVzmagODO790csnT1A-heO7TuioKNhAw9qYHQWQmMBdTgv_Q==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlIMtAM5S8MLYcYR6BwryYSxArfPyuZOux7N8IMoPjl7_38JeLbwy1-c6H4f9DFomAjHx8Oj9LoOia4y4M7x4nLUAV7547mZU0W9UqQY37967cxDiujg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEM3mhTcRyhXD528R0zzwXAOx48GAyj-sTSJdTm0PDUSV2jQUYpr8Y9_gzoaApf6gQ74AaGDBPuUKGBWUossug79Zkn2Jk__IujHonQim73ZkYfJ6h9JchbTQ==)
17. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcEhGUb18ogTFHNI4RuLCIiCGxPAigcLKj3tTWlKYIfF2h5GY-mclA-uaQJK4X8PmRW-DeqHafgLfydhKoSrAEDF0roj4l1sRYzvCmRyd2nDYU2czdFFG65eXGEaSuR8W3oOYmZGC0)
18. [epatters.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO3iw2gMXYhRyr45PxUmL_DVhD6uba6WP5SJ0F9oqpuMVf8yciA29rdk46f6agzhvMw6mEWkBkNbmA_Sx4dFZDiG2rbf5ulSiah78MHTTUcds97x6y18CW4a_FzdVMsaBjo67qMYbqDNrSdorkIw==)
19. [epatters.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5ITPqOTc7R-w6SRrvzqhV-O7olWSZjyIwFqjeNtorZgwPCBDG57myrvf_XEtai3rRoKU4hLpoBbttqQJDzsv6slvZvxpePyshaoA8l2WItLeTzKFfOD337T0lK3BGIlrl2YjTuOch8eK4pv_wkzOvkxf8b78bSz9tCaT8IpMRVRxm)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoMVQIyarYPFOUdC6u9pK7mTKQJAsl5XZViy-gY3U-7AoFACj1JkOq8tHNdTnCiglCeqKwjyaPmpaeb18Hoy_rtjd4GAy0N8UKxFTM6c0VtaAP3j0C7A==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGU9HBwfXQQUyA_gH4J3mAjY0UHfzwv8DyuZ7-6PLTpSu3R5NXnf8PGl6eB6V8IGJolQ2wLrtqgWIIFiS7r8sYiDn7Ih6n4oKYyqEUhKljUWck2gvfm)
22. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEf8yQsHGgZJKPMEp0c0M5U_iuegF7h7hheYV4AXQe5Yk4y9Iup3hkOxEm_QIDKEnG2Xl7p6B0XlPtt3JkynjWaNWoTzTWkIfLbj3Wcf8uivQww_NXL2MFEYc36ikagTjTcZHU1EzM5bdSkGfjRcJCZ0-E7jKUc)
23. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsnO28Z-mLydDtC26ijrNgJPehYICPj-QbLQH-YFgUymMhC26DMMxz1AMiOt-vKneFlCr66fszRozrnG6YxEPWWG-TSEI6ykdg6T5f9VGoma6XFzOTpXlbNo3z2-mlZeZ5MoHlzVHPJf_6MU4XOLJel49AuTggu6IWYyBVB64=)
24. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvHCLCaQEL2kVHM-MYw3hOd6p6obTCgwIK2zCzEKKUWY-QB7-m01kGqLwfiFsUXQSIilxIYl7m-O3nRmk_mcWsIGK6LS0g_Hnb1SHVgZX58tI0oHe-a5ZZXv98CIFxQjaoJkHKvdkfILyCcx-zTJnoPpFUGBugQ7kwdPy0ufqHgNY8KzkzSw==)


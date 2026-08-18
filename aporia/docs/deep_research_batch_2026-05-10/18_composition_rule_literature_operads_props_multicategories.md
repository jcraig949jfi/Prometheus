# Prompt 18: Composition-rule literature (operads / PROPs / multicategories)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdRRDRCYXFuSU5fcmVfdU1QMElHcS1RRRIXUUQ0QmFxbklOX3JlX3VNUDBJR3EtUUU
**Elapsed:** 242s

---

# Project Prometheus: Survey of Mature Composition-Rule Formalisms for Cross-Tier Integration

**Key Points:**
*   Research suggests that modeling the cross-tier composition rules of Project Prometheus requires formalisms capable of tracking multi-sorted (typed) inputs, making Colored Operads (Multicategories) or Colored PROPs the most mathematically natural candidates.
*   It seems likely that enforcing the "use-once" constraint in primitive composition aligns seamlessly with linear and affine substructural type systems, which formally disable the unrestricted duplication of resources.
*   The evidence leans toward Generalized Algebraic Theories (GATs), implemented in frameworks like GATlab, as the most performant and expressive computational substrate, avoiding the known performance bottlenecks of strict proof assistants like Coq.

**Project Context and Scope**
Project Prometheus has recently confirmed two critical cross-tier composition rules empirically: (1) Tier-B × Tier-D (constructive witness × distributional cert), and (2) Tier-B × Tier-E (constructive witness × representation-theoretic invariant). These empirical validations necessitate a formal mathematical grounding to generalize and mechanize the composition logic across all tiers. The requirement to securely and precisely compose primitives of different semantic types—without violating constraints such as double-consumption (the "use-once" constraint)—demands a robust algebraic framework. 

**Structure of the Report**
This report evaluates mature composition-rule formalisms to locate the optimal abstract structure for Project Prometheus. We systematically review operads, PROPs, multicategories, substructural logics, and multifunctorial mappings. Subsequently, we analyze existing software libraries for category-theoretic formalization, contrasting the dependent-type approaches of Julia's GATlab with the homotopy type theory implementations in Coq. Finally, we synthesize these findings into concrete architectural recommendations for the Prometheus composition engine.

## 1. Operads Primer: Symmetric, Non-Symmetric, and Colored
To formalize operations that take multiple inputs and produce a single output, algebraic topology and higher category theory traditionally employ operads. An operad is an abstract mathematical gadget used to describe algebraic structures, consisting of abstract operations of arbitrarily many arguments, equipped with a notion of how to compose them, and subject to associativity and unitality conditions [cite: 1, 2]. 

### Non-Symmetric (Planar) Operads
The most rudimentary form of this structure is the non-symmetric, or planar, operad. A non-symmetric operad \(\mathcal{O}\) consists of a sequence of sets or spaces \(\mathcal{O}(n)\) for \(n \geq 0\), where an element \(f \in \mathcal{O}(n)\) represents an abstract operation with \(n\) inputs and one output [cite: 1, 3]. The composition rule is defined as:
\[ \gamma: \mathcal{O}(k) \times \mathcal{O}(j_1) \times \dots \times \mathcal{O}(j_k) \to \mathcal{O}(j_1 + \dots + j_k) \]
This maps a \(k\)-ary operation and \(k\) operations of respective arities \(j_1, \dots, j_k\) into a single combined operation [cite: 2]. In a non-symmetric operad, the order of the inputs is strictly fixed and cannot be commuted. This planar composition is often visualized as grafting trees, where the root of one tree is attached to a specific leaf of another, provided the planar ordering is maintained [cite: 3, 4].

### Symmetric Operads
Symmetric operads generalize the non-symmetric case by introducing an action of the symmetric group \(\Sigma_n\) on the space of \(n\)-ary operations \(\mathcal{O}(n)\) [cite: 1, 2]. This symmetric group action allows for the permutation of inputs [cite: 2]. For example, if a primitive composition rule takes two inputs \(x\) and \(y\), the symmetric group action \(\sigma\) permits the formal relation between the operation applied to \((x, y)\) and the operation applied to \((y, x)\) [cite: 2]. The composition maps \(\gamma\) must be equivariant with respect to these symmetric group actions [cite: 2, 5]. Symmetric operads are ideal for commutative algebraic structures but implicitly assume that all inputs belong to the same underlying "sort" or type.

### Colored Operads (Multisorted Operads)
For Project Prometheus, standard operads are insufficient because they assume a single type of input. To model cross-tier compositions—where a Tier-B primitive and a Tier-D primitive are fundamentally different types of objects—we must employ **colored operads** [cite: 1, 3]. 

In a colored operad, there is a designated set of objects known as "colors" [cite: 1, 2]. Each abstract operation is assigned a specific sequence of input colors and a unique output color [cite: 3]. Composition is strictly typed: an operation \(g\) can only be grafted onto an input of an operation \(f\) if the output color of \(g\) exactly matches the expected input color of \(f\) [cite: 3, 5]. 

**Relevance to Multi-Tier Composition:** Colored operads are an excellent candidate for modeling Project Prometheus's multi-tier composition [cite: 3]. The specific tiers (Tier-A through Tier-E) natively serve as the "colors" of the operad. The empirically confirmed rule (1) Tier-B × Tier-D \(\to\) Output can be represented as an operation \(f \in \mathcal{O}(\text{Tier-B}, \text{Tier-D}; \text{Output})\). Because colored operads maintain strict typing constraints upon composition, they provide a mathematically rigorous guarantee that illegal primitive combinations will be rejected algebraically [cite: 1, 3].

## 2. PROPs and props: Generalizing to Multi-Input, Multi-Output
While colored operads elegantly handle multiple types of inputs, they remain restricted to a single output. If the composition of a Tier-B constructive witness and a Tier-E representation-theoretic invariant yields a single unified object, operads are sufficient. However, if a composition rule yields *multiple* distinct outputs—for instance, an updated witness alongside a distinct residual token—we must look to PROPs.

### The Mathematics of PROPs
A PROP (an acronym for PROducts and Permutations) was originally introduced by Mac Lane in 1963 as a strict symmetric monoidal category where the objects are freely generated by a single object [cite: 6, 7]. In standard formulations, the objects of a PROP are natural numbers, representing the tensor powers of a generator \(X\), such that every object is of the form \(X^{\otimes n}\) [cite: 6, 8]. 

Unlike operads, which evaluate \(n\) inputs to 1 output, a PROP evaluates \(m\) inputs to \(n\) outputs [cite: 8]. The morphism space in a PROP is denoted \(\text{PROP}(m, n)\), and morphisms can be composed both sequentially (via categorical composition \(\circ\)) and in parallel (via the monoidal tensor product \(\otimes\)) [cite: 9, 10]. 

To accommodate multiple types (such as the distinct tiers in Project Prometheus), one can define a **Colored PROP** [cite: 6, 11]. A colored PROP with a set of colors \(\mathfrak{C}\) is a strict symmetric monoidal category whose monoid of objects is freely generated by the set \(\mathfrak{C}\) [cite: 6]. Morphisms in a colored PROP map a finite list of input colors \(\{x_1, \dots, x_m\}\) to a finite list of output colors \(\{y_1, \dots, y_n\}\) [cite: 6, 11].

### Relevance to Tensor-Network Composition
PROPs have found profound application in physics and engineering, particularly in the formalization of tensor networks, quantum circuits, and signal-flow graphs [cite: 8, 12]. Baez, Coya, and Rebro have extensively demonstrated how engineering diagrams (e.g., electrical circuits with resistors, capacitors, and ideal wires) can be formalized as morphisms in specific PROPs [cite: 8, 10]. 

In tensor-network composition, putting networks together in series equates to categorical composition, while placing them side by side equates to tensoring [cite: 8, 9]. The "black-boxing" of a circuit—mapping its internal complexity to an observable input-output relation—is formalized as a structure-preserving functor between PROPs [cite: 8, 10]. For Prometheus, if the composition of primitives resembles a tensor network where multiple data streams are processed, merged, and split, a Colored PROP provides the exact algebraic framework needed to track multi-input, multi-output primitive evaluations [cite: 4, 8]. 

## 3. Multicategories: The Foundation of Typed Composition
If Project Prometheus determines that primitive compositions always yield a *single* output primitive, the framework of multicategories is the most structurally precise fit. 

### Multicategories as Colored Operads
In modern category theory, the term "multicategory" is essentially synonymous with "colored operad" [cite: 1, 3]. The terminology used generally depends on the author's mathematical background; algebraic topologists prefer "colored operads," while category theorists prefer "multicategories" [cite: 1]. 

A multicategory \(\mathcal{M}\) generalizes a standard category by allowing morphisms (arrows) to have a finite sequence of objects as their domain, while maintaining a single object as their codomain [cite: 13, 14]. Formally, a multicategory consists of:
1.  A collection of objects.
2.  For any finite sequence of objects \((X_1, \dots, X_n)\) and any object \(Y\), a set of multimorphisms \(\mathcal{M}(X_1, \dots, X_n; Y)\) [cite: 13, 14].
3.  An identity multimorphism for every object \(X \to X\) [cite: 13].
4.  Composition operations that allow substituting \(k\) multimorphisms into the \(k\) inputs of another multimorphism, satisfying generalized associativity and unitality [cite: 13, 14].

Every symmetric strict monoidal category has an underlying multicategory, where the multimorphisms \((X_1, \dots, X_n) \to Y\) correspond exactly to the monoidal category morphisms \(X_1 \otimes \dots \otimes X_n \to Y\) [cite: 1, 13]. However, a multicategory does not strictly require the existence of an internal tensor product object within the category; it merely provides the *syntax* for multi-variable mapping [cite: 1, 13].

### Relevance to Tier-A through Tier-E Typed Composition
Multicategories are deeply connected to logic and type theory, having been heavily inspired by Joachim Lambek's work on cut-free sequent calculi for intuitionistic logics [cite: 3]. In a sequent calculus, a derivation takes a list of assumptions \(A_1, \dots, A_n\) and produces a single conclusion \(B\), exactly mirroring a multimorphism \((A_1, \dots, A_n) \to B\) [cite: 3, 15].

For Prometheus, the confirmed rules (Tier-B × Tier-D) and (Tier-B × Tier-E) are fundamentally multilinear type inferences. The multicategorical framework treats Tier-A through Tier-E as the objects [cite: 2, 13]. A composition rule is merely a populated hom-set. If the engine verifies a constructive witness and a distributional cert to yield a new constructive witness, it applies a multimorphism from \(\mathcal{M}(\text{Tier-B}, \text{Tier-D}; \text{Tier-B})\) [cite: 2, 13]. This prevents combinatorial explosion, as the rules of composition are locally restricted by the available multimorphisms rather than requiring a globally defined tensor product for every conceivable combination of tiers [cite: 1, 13].

## 4. Substructural Type Systems: Managing the "Use-Once" Constraint
Project Prometheus operates under a rigorous condition analogous to the Sigma kernel's linear-capabilities design: a primitive, once composed and consumed, must not be double-counted or reused maliciously. Standard categorical models implicitly assume that inputs can be duplicated or discarded at will. To enforce resource constraints algebraically, Prometheus must leverage **substructural type systems** [cite: 16, 17].

### The Structural Rules of Logic
In classical and intuitionistic logic (and by the Curry-Howard correspondence, in standard type systems like the simply-typed \(\lambda\)-calculus), the manipulation of variables is governed by three structural rules:
1.  **Exchange (Permutation):** The order of hypotheses does not matter (e.g., if \(A, B \vdash C\), then \(B, A \vdash C\)) [cite: 16, 18].
2.  **Weakening:** Unused hypotheses can be discarded (e.g., if \(A \vdash C\), then \(A, B \vdash C\)) [cite: 16, 18].
3.  **Contraction:** Hypotheses can be duplicated and reused indefinitely (e.g., if \(A, A \vdash B\), then \(A \vdash B\)) [cite: 16, 18].

Substructural type systems are formed by selectively removing or restricting these structural rules [cite: 16, 17]. 

### Linear and Affine Types
If we remove both **Weakening** and **Contraction**, we obtain a **Linear Type System** (based on Jean-Yves Girard's Linear Logic) [cite: 16, 17]. In a linear type system, every variable (or resource) must be used *exactly once* [cite: 17, 19]. When a linear function consumes its argument, the resource is permanently invalidated in the typing context, safely preventing aliasing and preventing the resource from going out of scope without explicit consumption [cite: 17, 20].

If we remove only **Contraction** but keep Weakening, we obtain an **Affine Type System** [cite: 16, 17]. In an affine type system, resources can be used *at most once*. They cannot be duplicated, but they can be safely discarded without being explicitly consumed [cite: 17, 19]. 

### Separation Logic and Capabilities
Modern hardware synthesis languages, such as Dahlia, and memory-safe systems programming languages, such as Rust, utilize these substructural concepts to manage stateful capabilities [cite: 16, 21]. Dahlia uses a time-sensitive affine type system to model consumable hardware resources, ensuring that memory structures are not subjected to simultaneous conflicting reads/writes [cite: 21, 22]. 

Furthermore, **Separation Logic** extends these ideas to reason about heaps and shared state. The core of separation logic is the "separating conjunction" (\(P * Q\)), which asserts that state \(P\) and state \(Q\) hold for *disjoint* portions of memory [cite: 23, 24]. The Frame Rule in separation logic allows local reasoning: a computation only affects the resources it explicitly declares, leaving the rest of the separated state untouched [cite: 23, 24].

### Application to Prometheus
For Prometheus, a primitive acting as a "constructive witness" (Tier-B) cannot be aggregated indefinitely without bounds. By encoding primitive capabilities as **Linear Types** within the composition engine, the engine's static type checker will formally guarantee the "use-once" constraint [cite: 16, 20]. When Tier-B and Tier-D are composed, the function signature \(f: \text{Tier-B} \multimap \text{Tier-D} \multimap \text{Output}\) (using the linear implication operator \(\multimap\)) structurally enforces that the input primitives are consumed [cite: 20, 23]. If the logic demands that side-effects or leftover evidence can be ignored, an affine type system is appropriate [cite: 16, 17].

## 5. Functorial Composition: Mapping Primitives Across Tiers
When analyzing cross-tier structures, a critical question arises: If a Tier-B primitive maps onto a Tier-D primitive, is this mapping a functor? 

### Multifunctors and Categorification
In standard category theory, a mapping between two categories that preserves objects, morphisms, identities, and composition is a functor [cite: 25, 26]. However, because cross-tier composition involves multiple inputs (e.g., combining Tier-B and Tier-E to form a new state), we are operating within multicategories. Consequently, the structure-preserving map must be a **multifunctor** [cite: 14, 25].

A multifunctor \(F: \mathcal{M} \to \mathcal{N}\) between multicategories sends objects to objects and \(n\)-ary multimorphisms to \(n\)-ary multimorphisms, strictly preserving domains, codomains, identities, and the multifarious substitution/composition rules [cite: 14, 25]. 

When formalizing mappings of multiple variables, one must distinguish between:
1.  **Joint Functoriality:** A mapping out of a product category \(\mathcal{C}_1 \times \dots \times \mathcal{C}_n \to \mathcal{D}\) that acts simultaneously on all inputs [cite: 26].
2.  **Separate Functoriality:** A mapping that is functorial in each variable individually when all other variables are held constant (akin to a multilinear map in linear algebra) [cite: 26, 27].

### The Category Structure of the Substrate
For Tier-B primitives mapping onto Tier-D primitives to act as a proper functor (or multifunctor), the underlying substrate must possess a rigid mathematical architecture. 
*   If the composition evaluates within a single universe of primitives, the substrate must be at least a **symmetric multicategory** [cite: 1, 2].
*   If we view a specific composition mapping (e.g., Tier-B mapped via Tier-E) as an internal operation, it can be defined as an internal monoid within a host multicategory. An internal monoid in a multicategory is equivalent to a multifunctor from the terminal multicategory \(1 \to \mathcal{M}\) [cite: 25, 28].
*   If the system demands parallel associative evaluation, the substrate must be elevated to a **symmetric strict monoidal category**, wherein the multicategorical mappings natively correspond to tensor products of the constituent objects [cite: 1, 2].

## 6. Existing Primitive-Composition-Rule Libraries
To translate these mathematical formalisms into working, verified code for Prometheus, we must examine existing computational category theory libraries. The two most prominent paradigms are Julia's GAT-based libraries and Coq's Homotopy Type Theory libraries.

### Catlab.jl and GATlab
`Catlab.jl` is a framework for computational category theory written in the Julia language [cite: 29, 30]. It provides a programming library for representing categorical doctrines, manipulating wiring diagrams, and executing symbolic computer algebra [cite: 29, 30]. Recently, the underlying logic of Catlab was rewritten into an independent core package called `GATlab` [cite: 31].

GATlab is built on **Generalized Algebraic Theories (GATs)**, initially proposed by Cartmell in 1986 [cite: 29, 32]. A standard algebraic theory (like that of groups or rings) cannot model categories because the composition operation in a category is partial—you can only compose morphisms \(f\) and \(g\) if the codomain of \(f\) matches the domain of \(g\) [cite: 29]. GATs solve this by augmenting algebraic theories with **dependent types** [cite: 29, 31]. 

In GATlab, composition is not a partial operation; it is a *total* operation on dependently typed parameters [cite: 29, 31]. The signature `compose(f::Hom(A,B), g::Hom(B,C))::Hom(A,C)` ensures that the Julia compiler and type system verify domain/codomain alignment at the syntactic level [cite: 29]. GATlab allows programmers to specify GATs, define free models based on symbolic expressions, and declaratively migrate models via functors [cite: 31].

### Coq and the HoTT Library
Alternatively, theorem provers like Coq provide absolute, machine-checked guarantees of logic. The Univalent Foundations program introduced Homotopy Type Theory (HoTT) to Coq, which includes a highly advanced category-theory library capable of reasoning about 1-precategories, univalent categories, and functorial isomorphisms [cite: 33, 34].

However, representing highly abstract categorical objects in Coq introduces severe friction. Jason Gross, a primary author of the Coq-HoTT category library, has extensively documented the **performance bottlenecks** inherent in this approach [cite: 35, 36]. In intensional type theories like Coq, the equality of highly nested categorical proofs requires computation up to definitional equality, which can lead to exponential slowdowns during type checking ("doing too much stuff") [cite: 33, 37]. 

While Coq allows for sophisticated mathematical proofs using features like universe polymorphism and primitive projections [cite: 34, 38], the computational overhead required to execute dynamic composition rules in a live engine would likely be prohibitive [cite: 35, 36]. Coq is a proof assistant, not a computer algebra system; it is designed to verify static theorems, not to rapidly execute symbolic compositional logic over millions of dynamic network primitives [cite: 29, 30].

## 7. Concrete Recommendations for Prometheus
Given the confirmation of the Tier-B × Tier-D and Tier-B × Tier-E rules, alongside the five candidate compositions, Project Prometheus requires an abstract framework that is mathematically complete, computationally performant, and structurally safe. Based on this survey, the following architectural choices are recommended:

### 1. Abstract Framework: Colored Operads (Multicategories) vs. PROPs
*   **If compositions yield multiple outputs:** If evaluating Tier-B against Tier-E modifies the witness *and* yields a separate localized invariant, the correct algebraic framework is a **Colored PROP** [cite: 6, 11]. This permits the tensor-network style parallel routing of multi-output primitives [cite: 8, 10].
*   **If compositions yield single outputs:** If the output of a multi-tier composition is always a unified singular primitive, the correct algebraic framework is a **Multicategory (Colored Operad)** [cite: 1, 2, 3]. This avoids the necessity of forcing a global tensor product across all objects, reducing the categorical burden while maintaining strict typing for the \(n \to 1\) arity of the confirmed composition rules [cite: 1, 13]. 

### 2. Operational Semantics: Linear Typing embedded in GATs
To enforce the "use-once" constraint analogous to the Sigma kernel, the host language must track capabilities substructurally [cite: 16, 21]. Plain categorical formalisms do not inherently prevent the duplication of a morphism. Therefore, the implementation should employ a **Linear Type System** [cite: 17, 20] overlaid on the algebraic models. 

### 3. Computational Implementation: GATlab over Coq
For software implementation, **GATlab (via Julia)** is vastly superior to Coq for an active operational engine. GATlab provides the exact dependent-type structure required to formalize partial compositional mapping without the debilitating performance bottlenecks associated with tactic-driven proof assistants [cite: 29, 31, 36]. GATlab’s methodology explicitly caters to applied scientific computing and dynamically structured graph rewriting [cite: 31], which will allow Prometheus to compile cross-tier rules into highly optimized executable code.

By defining the Prometheus primitive tiers as types in a Generalized Algebraic Theory, implementing a Colored Operad doctrine for cross-tier multimorphisms, and imposing linear typing constraints on primitive consumption, Project Prometheus will possess a mathematically unassailable and highly performant engine for multi-tier composition.

**Sources:**
1. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ7J8_VJBaao8NNum9uWrfvKuulgTU3LatEp1SY0FKgrW6rGYomdcRPjZbV5v3gIim80JK32m80p5GZTBLN2hEnCFwvK2QB2e3dd1jMh6chh_FGyQO-P7LxgU=)
2. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzh4GoT9hrbiYNr4VOYSM-CCKJhzGWdqqnLuM-bU0yil-QCs4ONISZ69c99-SoE0OHPXamWwMECklD-kBpHk83s7HCzEihMmB-mwytv25wUfdqb_nBEK-03bkuUwEW8Beve0xIpP4L)
3. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXS9u1_AA2fMOpuSw9M-MW2qHr7sjufkgPypfvzF30zChRM2dKvqurPs1JqSmQG3J_t21tBEcIbbHjbgrd4fySilPCaQZVy1baOIMsQ21B4gpWPEGZmA7Dwya3uj6dL5EOBLOCy3_T3l9X-aYv3TOuE9f3sDAyg26nR1bP8VAMQBuU7Mf4ySMn6w==)
4. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQmWASl-5zL1ssXsZljlArkXhI_Wqmvy0XLwuOtH_n2T_mo7ksV_9ttEUBMhWQouFuxvz_cf7za4sfpJ1pi91GrQcWg8AenOp53ZSCQRiEkCQBO65urQPll2qBzYbcVpEev0wRaZ5zZZqims9zdnU=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJTv1ItH4mxBRwbzIcCqLDjt1jaFpeUwju-TfXJfx2uVno0P6ClI8AbEK9DwiemTm7cPR0qJdNTvC2tblONHMqyeszg0mQX70q4ywGM7kZ-BA12KL0FA==)
6. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjuLRT_WAD-s_MmugrTheWDc6uVpP1tpMA9E0ugViVBnRSxv_rsCkTv7q5HX3EkkcG63yMfVAz7TvH7oOR0p6TLTrfdVe660YfD-ZeWZjvqfwABOZQSFOO)
7. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAhWDOLUURqs3V3kemDWUqE8qk1ycpYXoITgIR7Fqgh6JxSmzsp_q4hSXe7-tR8xuTIMZArOb2Jic4D_MBPO_WO-AvjK2GRKwyfol7TY-cm_UlR5-93kFLetJdz6nLzQ_qkuM8xgqgymb-iptmqNZgKNzViZ49Q0TyInc_bQ==)
8. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFribwGy2mOFfe-IKP5pDvF2YDVQT0dhxJDewS5PAgLZRBWbN350750BxRgWdXmc1EYkJ6MVSzapL57KRFQmuK7M7mh32m-qCgeNLYoIJDPTj6KT6PNBL3Km30x_11OdQ_79IwyAvsIAwB-52JenwlXNUflDj17VRNexrJN1ej0)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiN5HqB6fEbxWkMRmNJE9XelrHkit2LobeCr1E5k60y_Kz8MaHLFziwyzbfMsrXbWKWF9UFmjW2QWhsmqARy8bLHQGRnj4SssXuVhblBgEq7xFu6_5Lw==)
10. [mta.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQLx74jPBrzVFGtnlvyPUbTpylWEH3TIoPKBViDiAjvZiC2pKp7yLXIusHmkA_RM6zepypCfJNSnhaZ8_bfaqctlVywatDvJme3St0x6fVDhLiJXfDqxwHysmNorDHJSlBu-Q6j5hf)
11. [chapman.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCmBX7lUUxyk345SU7g9tkQ-PKzZxy0jcUTphPFpRgzyLC9Xkyg_m-sADW7LGgjnVT6Q6hnpeailZcP6dtD6b_xHo-8lgylya787p8ZzdvhGI11naFaRl2F9_ta7_akBw6yyzDDUZHrzm8xNb8zmOPjMVKg0OYOtF2PVmiBbD_rKdQXfBuo_7yEUn4KMJh82yVd2EVd3s=)
12. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO36j8v8EJnib7FGKOeey5unid599ywDQwJ7ljOBZk2D0YG6wbk2GT5j3RNymoRn0uJrYwCu7FzPV5Bm69pN5a-3IpC8XbBHhL3kjsKbPU88Stq4pzrBkxNEuJes4mrETFtG8Ww-mnHAAN3A==)
13. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU_CxikM8S4sGyp0Hf6qkbi55MlDohDg2XfFY9C3853s1nVYdYaw_9QGVjZrVQTOlMj_Zf2lnQrs0YJxUw0tNH8VFOa3bJ_CRD3pYDrVND1uhof3AwBMkKd-gF9ukyKd68)
14. [mta.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKpraV-mPtO9U9XCVWs8xvfhiIEfyTowPcKIQSEs9DPO3wSxU5u8a4JYpvuJDVvdPmOEl8GLE76C6TCCSedIJN_QnP-v8yzxFmdNCnvrjBLLyoAnCHEzaTLyt5TO_o39HFgry4ABCQ)
15. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEygWPMeLPHizBOWXkbT91sZHtnsZYEw6JsqRBfOmZJ8pnPKEHKSWdvdbzMO240TbDPsIRpJTpXAOIikD6CGZneNhCzyDkI6cOzVPbrEO-syDHjwT-VMTKDjLroF99uptziJ43QSAQOAqPSbum4_Niu6m4VwRpA-0mAmTv_fZFhxQLshSfckTU0wNCj)
16. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESy6FRD0F98hSHFo16gRZ9AfIfe5HPlW9jOKOxqOh8Pb95bTzzRP0TBQ9mLibbJP_ZBPlF7qZd2yAZiLFO-z8d6uPKuGXNDmcpvjOMD29pm4XpmrzPTHxcdfp65a3m0WeM6umMCE7fqXjIgg==)
17. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGL0ezc9uBLBGU8907fwaDRY8UrTUmwh6YBvOGdBt5h1jYlTO28U0MrriQxBiZ4YbXXzJHNqXmaNlMFDniBCrAJ8aTc6mq5AZduFE3Zbp_JCgNUIXV3GSPlqhTS5lqgeaZMWwfH2RwfAMQ1pYVh)
18. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmlp3bTVg3Zg24g28Ze7_NDeFMBXLPviRgBbkOcjD-6HU4xKObkHrmh4k1xYyiAZmPsdXTXfWzt487hCBIPNi9XN_pnxw-eGFMpkLjezcAdCcj9hE_4Pb_1OERKP05WX5ebzB3PkVh9nSGgp_-LMIa_Hrj_mg=)
19. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiKzUXBMdRAYNvNzG8sGV88QBwDirN18J3oqnHsNilhSQflK5cqj65LkPzWL68y-JQfscZTSc8X1MXF1ugHB-WjAgWBKL871Kd7yOPT-k4HaGOyIh_Ip9RFiK6247Pts-Ncfvi0ONyelSUCBa8k5yPySAOZk-WJIfkuOFl1u2OkuD2EqAEf6zG-bAlU6gsxQeydOHq9S6btPT1RrbowtVvVMZTvZsovZJTuOFj7d9H)
20. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnkAOr-WE5l9XHMWs8mJB00jFq6WkqL130UDyukg8Ymo3G2aiqxrIJSpRnEfe5LJmqSRuy8UMIN-3atzefNv23FXQZkv0SYd5IDOJL7hgmCER_rJa_2DRBhiKJABOFMHL7IoVAUD46L6qZn6rptotNt-6cjTo17SEo2HNMiA==)
21. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRjp1d85C5gmfsYrFcqu0_qmaunmDIvS7fRcCLPMYFsMEKd5T9r38WwdJe9FgHOig3Q2BEaXwsrK37N4u5HrTFTZ7QuJggHY83Jp1eKWnkaKbUiunrvz_F15giWQyc)
22. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0IFIhcrZgJy993TmtfWjkqhSzfM72CqrwxeUvW5PBXZKp0Gru5ULp5nJZP7HTZNBc2dz4a4ahf9FQuaehEZWBvWZAcx2hvFIkmDGseAvJ8kim7MPDI616vmMVDJ5e4QDzPtiNy8aPItY2QqRTShEnukg=)
23. [cam.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGdQ6kyegx2w9X7QSjjOMPvypXCnBOI3zigPir8t4yv-cybT5f6RgYR5Lxd9QCKYGwIpd4zgRDaraJtPtGnldnYtT-tALX-bKX57ovCBBdKBJT-KTI1Uu8dTIRJlSAVgANjAopRyzxdvZQKFEPd-Exsaw2paCtGYrlfxr7OmWU_AfdKPYY2ZQ9IoI8)
24. [bentnib.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZRnIX6rMX0CSGJx66wQUl1_Ash5PZqXZoQtfxiUd1m0drE5PSTf7uev_mOVvomr-WohWfIi0r03i0wQMH18C_7nWYQdwkxd3FHCPSkVloW9L427o=)
25. [topos.institute](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAIwPcj4gcTIK_7tzcZRkSdjng9A4sX8zXh1xyXLNGPBOYndOmcpzY56VFOc5ncgX73a__sNkKoVrPjNPrap3xlmOXdrTL2SANWtfK3KJjemFH0ltgwbrDYRH7bBKdF0J-8Pzx-KBp-DhWXXg2_RcttqDn1Vs=)
26. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNyU9Ts0_3BFY_yZM9HvIXYcOPhzqxzOt9PQW2eveOnh7rA_DR56twiw08VotEXYMb1hY1v2R7X_pkIOl9JTxyik0xnuRAURbysxH1nai0HJeYjDE3xjN0x94_CUI-Jms=)
27. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFqs1BmlJTFDWN--1oOTbFcs_Lte8jRen9vA7C_LY0zh5BzGnE51edN_nGdYcNYfDejaDvE_yHK0PSNcwGF9Yroj_GJn31HsqzzjdaU5ZzA_gS0F3k-c5uD4dVvkTBy4qsM3mYMXY=)
28. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnY32gu1U4qFZxYR80zW8VUTJ55P7YkjyurHQG40QjE1iOqno61i4jHlj2aRJP0XzUo6pdm8RZUM-Tugv-qOa9mCB2mXf8-nB4h_gTGurQzndKgetYH634a9JfqXXoeaTQiCnmByrMMIKBenNj5KKkZ9FmS2sX_97utk2V2i1EvUBgxw==)
29. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAMRAtJKkUVqxX7U5yFrSGIoYUZDJB7l_xOWs_MJHETvzOtnFCIctG__TZysCht6OBBUICMJMB5g90DhbUoeI4LzOt0sW8gc91HDqW8dYNgEM11Lku4cjFD7X-wgmv6X1FiNl17jA=)
30. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBsg6TJM4C_lah2VX2XpUk2Hx7jML34T1gWzV4z1mSixxcRc7twzsbKPh_6c1UR4kzBuQmfRutMdQiDcxZv8m7ESICLFJ770XTTbxtI-pKp-VgmE91NF63HZ2lYlYlwpX9Y58u7Q==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHY2LptxAcWnVcztFWmnY5OEQxiwTLuU2ZyX_yNfKRaNLxkX-VDtKYWCyozvj-tNvbw8w7Lja3xZHsyyPt3ByH2DaJ9S9kMjHbVvmLq7iqjILCuoz3Sy5zsxA==)
32. [epatters.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFkdMWZSad6UKjYUP56fQXzs77Ge8ZjRoU-4u9qRxqNKT9arPO7vUlGhRl14184gGHc_6JL8jVboDJ4kj6ranVPpQtNlFyjIDZLgHBQfSTAIHuPp2d1lwbeVgWSq27kzHdBxc4niWnD_hpY2oYy7b7cZ52Aa2yqfOZPHGTXW4XPAtf)
33. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdhbKuBPrYTJfh6_1lzVs5mVvWPBKbrnxC7xmXz9h7J-u-aFtETjNhkTIjsayZDgh3xxIR9QMyJkB7hw-CD0w0d0FMbRzBCPabwkxPNvAGeG-WrxjUyUAQ98WJjCM1qA9jQboXsdeZYz_MDVZ68NseG4oztm334edSayFOs1sJvq9Gp8cO4npES7o=)
34. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGn43tKdGVXzVnH0euQVpDN-lGCus_pBRoTl9LQBs7VMTYlv6M6zi9HrTbREMsnCmXULhwZcjDpfx6aLcEpmxFJ4tRJAnVtnKmPpxiFl2X1tpGsDm6XdbOh4Bg7EQOd_TApTERMH-FiizvXw_BUBLJFqcCNIKANOQMYTKfZW7nh)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBigYCVVTbjrXNZztig6-c_9_9eL8GKPdcmVkL2AvQfbxWOZ-pLSv9MIejod5khteBweBoLxySdOGMBmOVUk_ZThlKlHA1Jl5EyhM_szbOAMd4Wqb0)
36. [chlipala.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGR8qQ5F7SQhprcoMdbvbgM3wVlTrhjCNMYEFxpDT7hWlzyHRCcoDmKyWpB_4-FE475Pin6xZd-bm0JiVc7aT3AV2Z5E5Lbv-PZn69Dtz4Y6Ow_UbjA56kdR33vtRIw6Ip7)
37. [chlipala.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkv5h61EXFQX93kGABPCQDROLcPROp5xOJS5CHWznrjzd43ndfvIF9cootHyBUHIcotQlqxtXf10J5Lf0MdfSk8hNcWW9c6U4Y7vXEZoBtCgPkmMXN377pWPAsU3xa-CAcHn5yIqYqxSSSCFkMoY0nRHNqtVXD)
38. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyPyB2Rq7theYYEuOUX_kQh7FvsuRD85iJPc4bsf8w0kPo_0yGbvu0lKc08dl85Mbu9j9Rlxr1DDJxhoHbqYmIVI1UUx3wOx6fX5Od4cDJt0t6MenW0BNpt6aie4g0bVcc31QVPhzHna9xVIrtNteQWw6Q6eCTwkEAJ7nxbtljebHA-MaLBTsCio4u-BiGNi5NNO-39_HFufRUa3m8EfcwB5KB)


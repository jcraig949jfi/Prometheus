# T#51 Hackbusch-type conjectures on hierarchical formats

**Pythia queue id:** 94
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcxeGNQYXNiLUZKcXkxTWtQaWR6ZjRRRRIXMXhjUGFzYi1GSnF5MU1rUGlkemY0UUU
**Elapsed:** 254s
**Completed at:** 2026-05-21T14:38:14.283955+00:00

---

# T#51 Hackbusch-type Conjectures on Hierarchical Formats

**Key Points**
*   The **Hackbusch Conjecture** addresses the relative encoding complexities when a single high-dimensional tensor is represented using two different tree-based tensor network formats.
*   Research suggests that the fundamental question is whether every tensor representable by one tensor network (e.g., a "spread" perfect binary tree) is representable by another (e.g., a "deep" train track tree), and at what cost to the rank parameters.
*   The original conjecture, formulated by Wolfgang Hackbusch and Joseph Landsberg, was resolved in 2015 for extremal cases: the Hierarchical Format (HF) and the Tensor Train (TT) format. 
*   In 2020, the conjecture was generalized to arbitrary numbers of leaves and "almost binary trees," revealing that the tensor rank of most tensors in a Tensor Network State (TNS) model grows exponentially with the number of leaves.
*   Recent theoretical frameworks introduced in 2026 propose the **containment exponent**, a measurable bound indicating how much the parameters of one network must be boosted to guarantee containment within another tensor network variety.

**Context and Significance**
High-dimensional data in modern computational mathematics and quantum physics is often encoded as tensors. However, representing an $n$-dimensional tensor explicitly requires memory that grows exponentially with $n$, a phenomenon universally recognized as the "curse of dimensionality." To mitigate this, researchers use "tensor formats" or "tensor networks," which decompose complex tensors into a network of smaller core tensors guided by a graph structure—most notably, binary trees. While these formats offer massive computational savings, transitioning between different formats (e.g., from a balanced tree to a deeply nested tree) can inadvertently inflate the complexity of the representation. The Hackbusch-type conjectures and their subsequent proofs provide the crucial mathematical foundation for understanding these format translations, offering rigorous bounds on the encoding complexities.

**Current Understanding and Open Questions**
The trajectory of research into the Hackbusch conjecture highlights a profound intersection of algebraic geometry, combinatorics, and numerical analysis. Initially solved for specific, highly symmetrical tree formats, the inquiry has expanded into broader combinatorial territory. Today, advanced metrics like the "containment exponent" and the mathematical formalization of "tensor network varieties" allow researchers to compute algorithmic bounds for differently shaped network trees. While the theoretical understanding of tree-based formats is maturing, exact dimension calculations and optimal algorithmic translations for more complex, non-tree tensor networks remain open areas of ongoing academic exploration.

***

## 1. Introduction to Tensor Networks and the Curse of Dimensionality

In scientific computing, quantum mechanics, and data science, multi-way arrays or tensors are essential for representing high-dimensional functions and states [cite: 1, 2]. However, the ambient vector space of an $n$-way tensor requires a number of parameters that scales exponentially with the dimension, a computational bottleneck commonly referred to as the curse of dimensionality [cite: 3, 4]. To present seemingly complicated tensors in a relatively simple, efficient, and computationally tractable manner, mathematicians and physicists rely on tensor formats and tensor networks [cite: 5]. 

A tensor format encodes an $n$-way tensor as a sequence of linear subspaces via two-fold tensor products [cite: 4]. This process is governed by the combinatorics of a graph, often a binary tree, with a collection of vector spaces assigned to each vertex [cite: 5]. The central idea is that the number of parameters needed to define the tensor network state (TNS) is vastly smaller than the dimension of the ambient space [cite: 4]. 

### 1.1 Tree-Based Tensor Formats

The structural arrangement of the tensor network dictates how the tensor is factorized and stored. Two prominent examples of tree-based tensor formats have dominated the literature:
1.  **Tensor Train (TT) Format**: Associated with a "train track" tree, which is the deepest possible binary tree [cite: 5, 6]. In the quantum physics and quantum chemistry communities, this format is heavily utilized and is classically known as Matrix Product States (MPS) [cite: 2, 3]. TT formats transform an initial high-dimensional tensor into a network of three-dimensional core tensors that require only linear storage [cite: 3]. 
2.  **Hierarchical Format (HF) / Hierarchical Tucker (HT) Format**: Associated with a "perfect" or most "spread" binary tree [cite: 5, 6]. The Hierarchical format mimics interaction structures dictated by differential operators or specific algorithms, maintaining low ranks when the format appropriately fits the given problem [cite: 7]. 

Each of these presentations is characterized by the tree structure, a family of vector spaces for the leaves, and a dimension function (or rank parameters) for the subspaces on the vertices [cite: 4, 5]. The locus of all possible tensors that can be encoded in a specific manner using these parameters forms a geometric object known in algebraic geometry as a **tensor network variety** [cite: 4].

### 1.2 The Core Problem of Encoding Complexities

While multiple formats can represent the same mathematical space, the ranks—and therefore the storage and computational complexities—are fundamentally affected by the choice of the format [cite: 7]. A critical problem emerges when one attempts to translate or compare the presentation of a single tensor across two different tree structures [cite: 5, 8]. The fundamental question arises: if a tensor is perfectly representable with low complexity in one tensor network variety, what is the complexity required to represent that exact same tensor in a different tensor network variety [cite: 4, 9]?

This problem forms the conceptual core of the Hackbusch conjecture [cite: 5, 6]. 

***

## 2. The Original Hackbusch Conjecture on Tensor Formats

The original mathematical inquiry that catalyzed this specific field of research was suggested by Wolfgang Hackbusch and Joseph Landsberg [cite: 5]. Driven by Hackbusch's earlier observations (notably documented as Conjecture 12.7 in his 2012 foundational text on numerical tensor calculus), the problem asked to compare the complexities of encodings if one presents the same tensor with respect to two distinct trees [cite: 6, 8]. 

### 2.1 The Extremal Cases: HF versus TT

The formulation of the Hackbusch conjecture focused specifically on comparing the two extremal cases of binary trees used in tensor network states:
*   The most "spread" tree, embodied by the perfect binary tree (corresponding to the Hierarchical Format, HF).
*   The "deepest" binary tree, embodied by the train track tree (corresponding to the Tensor Train, TT, format) [cite: 5]. 

Both formats are powerful tools for addressing high-dimensional problems in scientific computing, providing numerical stability and robust algorithms for linear differential equations and eigenvalue problems [cite: 1, 3]. However, understanding the explicit translation of tensor rank complexities between the Hierarchical perfect binary tree of level $k$ (with $n = 2^k$ leaves) and the Tensor Train train track tree with $n$ leaves was an unresolved problem [cite: 6]. 

### 2.2 The 2015 Resolution by Buczyńska, Buczyński, and Michałek

In January 2015, a landmark paper titled "The Hackbusch Conjecture on tensor formats" was authored by Weronika Buczyńska, Jarosław Buczyński, and Mateusz Michałek, ultimately published in the *Journal de Mathématiques Pures et Appliquées* [cite: 5, 10]. 

The authors successfully answered the question posed by Hackbusch and Landsberg for the extremal tree configurations [cite: 6, 11]. Using techniques from algebraic geometry, they analyzed the varieties of tensors of hierarchical format $HF(r, k)$ corresponding to the perfect binary tree, and the varieties of tensors of TT format $TT(r, n)$ corresponding to the tensor train tree [cite: 6]. By comparing the complexities of these encodings, they proved Hackbusch's conjecture regarding tensor network states related to these specific trees [cite: 5]. 

The resolution inherently demonstrated that tensor formats and their complexities are deeply governed by the underlying combinatorics of the trees. The findings established that the shift from a perfectly balanced hierarchical structure to an entirely linear, deep train track structure incurs specific algorithmic and rank-based scaling penalties, which can be exactly bounded using algebraic methods [cite: 5, 6]. 

***

## 3. Generalizations of the Hackbusch Conjecture: Part Two

While the 2015 resolution successfully closed the conjecture for the specific cases of the perfect binary tree and the train track tree, it left open the question of intermediate, arbitrarily shaped trees. Real-world numerical problems and quantum chain models frequently utilize tree topologies that lie strictly between the extremes of "perfectly spread" and "maximally deep" [cite: 3, 8].

### 3.1 Expanding to Arbitrary Numbers of Leaves

In February 2018 (later published in *Linear Algebra and its Applications* in 2020), Weronika Buczyńska published a standalone continuation of the research titled "The Hackbusch conjecture on tensor formats — part two" [cite: 12, 13]. This paper expanded the scope of the proof to a significantly higher degree of generality [cite: 8, 12]. 

Buczyńska considered the Tensor Train (TT) model with an arbitrary number of leaves rather than restricting it to powers of 2 (as required for perfect binary trees) [cite: 12, 14]. To juxtapose this against the Hierarchical Tucker (HT) model, she introduced the concept of an "almost binary tree" [cite: 12, 14]. The almost binary tree is defined combinatorially as the deepest tree that possesses the exact same number of leaves as the target TT model, serving as the generalized counterpart to the perfect binary tree [cite: 12, 14]. 

### 3.2 Flattening Ranks and Exponential Growth

The primary theoretical contribution of the "Part Two" paper was the development of a novel algorithm [cite: 8, 12]. This algorithm systematically computes the maximum possible **flattening rank** of a generic tensor within a given Tensor Network State (TNS) model on a specific tree [cite: 12, 14]. The flattening rank is evaluated with respect to any flattening derived from the combinatorics of the vector space, particularly determined by fixed subsets of leaves that encode the flattenings [cite: 12, 14].

A crucial corollary derived from these methods pertains to the broader geometry of tensor network states. Buczyńska demonstrated that the tensor rank (also referred to in classical multilinear algebra as the CP-rank) of the vast majority of tensors within a TNS model grows exponentially with respect to the growth of the number of leaves [cite: 8, 12]. Crucially, this exponential growth of the CP-rank holds true regardless of the shape of the underlying tree [cite: 8, 12]. 

The "Part Two" paper effectively bounded the flattening ranks of tensors by computing divisions of initial flattenings, thus obtaining exact bounds for optimal functions defining the TNS space [cite: 14]. This provided an algorithmic pathway to transform any general function representing a network state into an optimal one without altering the underlying TNS variety [cite: 14]. 

***

## 4. Tensor Network Varieties and Containment Exponents

The problem of comparing encoding complexities evolved into a broader algebraic query: Under what specific conditions is one tensor network variety completely contained within another [cite: 4, 15]? If $TNS(T)$ represents the set of all tensors representable by a binary tree $T$, determining if $TNS(T) \subseteq TNS(T')$ for a different tree $T'$ became the generalized manifestation of the Hackbusch Conjecture [cite: 4, 16]. 

### 4.1 The 2026 Framework by Garzón Mora and Haase

In January 2026, Sofía Garzón Mora and Christian Haase released a pivotal paper titled "Containments of Tensor Network Varieties," building directly upon the foundational works of Buczyńska et al. [cite: 4, 9]. They proposed a generalized combinatorial framework to address the containment question for arbitrarily shaped full binary, rooted trees, disregarding any specific planar embedding [cite: 4].

#### 4.1.1 The Containment Exponent

To quantify the relationship between two differently shaped trees, Garzón Mora and Haase defined a new mathematical measure known as the **containment exponent** ($E_{T,T'}$) [cite: 9, 16]. 

The containment exponent gauges the precise degree to which one must "boost" or artificially inflate the dimensionality parameters of one tensor network for the containment to hold mathematically [cite: 4, 9]. Formally, for any two binary trees $T$ and $T'$ on a common set of leaves $L$, and arbitrary dimension functions $f, f' \in \mathbb{N}^L$, the containment exponent $E_{T,T'}$ dictates that for all coefficients $c > E_{T,T'}$, there exists a threshold base rank such that the scaled tensor network states satisfy the containment $TNS(c \cdot f, T) \subseteq TNS(f', T')$ [cite: 4, 16]. 

#### 4.1.2 DOAD Sets and Outer Descriptions

The core of their methodology relies on understanding the "outer description" of tensor network varieties via geometric mappings. A critical combinatorial concept introduced in this framework is the **doad set** [cite: 16, 17]. 

For a given tree $T$ with a leaf set $L$, a subset of leaves $S \subseteq L$ is defined as a *doad set* if it can be perfectly represented either as the set of all descendant leaves of a specific vertex $v$ (denoted $\downarrow_v$) or the set of all non-descendant leaves of $v$ (denoted $\uparrow_v$) [cite: 4, 16]. The family of all doad sets for a given tree completely determines its outer description through tensor contraction maps [cite: 16, 18]. 

Garzón Mora and Haase observed that if a proper subset of leaves $S$ must be covered by a minimal number of doad sets $S_1, \dots, S_k$ from the initial tree, the required number of doad sets $k$ directly provides an upper combinatorial bound for the containment exponent [cite: 4, 19]. Because these subsets either contain one another or are entirely disjoint depending on the hierarchy of the vertices in the tree $T$, evaluating the intersections yields predictable mathematical bounds [cite: 4]. 

#### 4.1.3 Poset Structures and Algorithmic Bounds

The authors modeled the binary trees as partially ordered sets (posets) governed by a descendant relation $\leq_T$, which naturally forms a join-semilattice [cite: 4]. By evaluating the lowest common ancestors for sets of leaves, they established a rigorous combinatorial bound that could be quickly computed mathematically [cite: 4]. 

Using this poset-based framework, Garzón Mora and Haase developed an algorithm capable of actively computing these bounding containment exponents [cite: 9, 20]. Through exhaustive computational searches, they successfully evaluated the containment exponents across all possible tensor network varieties arising from full binary rooted trees possessing up to $n = 8$ leaves, accounting for all permutations of leaf labels [cite: 4, 9]. 

This 2026 work transformed the Hackbusch Conjecture from an existence-based boundary problem on extremal trees into a quantifiable, algorithmic framework capable of grading the structural compatibility of any two tensor network shapes [cite: 15, 16]. 

***

## 5. Geometric and Physical Connections: Dimensions and Spans

While the Hackbusch conjectures focus on the containment and structural translation between tensor formats, simultaneous research has deeply investigated the intrinsic algebraic properties of these Tensor Network Varieties, such as their dimensions and linear spans. These geometric properties are of paramount importance to the physics community, particularly in the study of quantum many-body systems. 

### 5.1 Matrix Product States and Translation Invariance

The Tensor Train (TT) format is identical in mathematical structure to Matrix Product States (MPS) with open boundary conditions, a class of tensor network states utilized extensively to model quantum spin chains and strongly correlated electrons [cite: 2, 5]. 

Claudia De Lazzari, in her 2022 Ph.D. thesis at the University of Trento, conducted exhaustive research on the dimension of tensor network varieties [cite: 2, 10]. Her work evaluated the varieties of tensors defined by the combinatorial structure of graphs alongside bond and local dimension weights [cite: 2]. Moving beyond open boundary conditions (trees), De Lazzari, alongside collaborators like Harshit J. Motwani and Tim Seynnaeve, extensively studied the linear span of **uniform matrix product states** [cite: 2, 10]. 

Uniform matrix product states arise algebraically as a natural generalization of the Veronese variety and are used in physics to model translationally invariant systems of sites placed on closed cyclic graphs (rings) [cite: 10]. Utilizing invariant theory of matrices, representation theory, and linear algebra, they analyzed the geometry of these translation-invariant varieties [cite: 10]. 

### 5.2 Trace Relations and Span Containments

A key achievement in De Lazzari's research was establishing a completely general upper bound on the dimension of generic tensor network varieties [cite: 2]. By refining these bounds for applications involving MPS and Projected Entangled Pair States (PEPS), she provided nontrivial linear trace relations [cite: 2]. 

These trace relations successfully proved the strict geometric containment of the linear span of uniform matrix product states strictly within the ambient space, provided the number of physical sites is at least quadratic relative to the bond dimension [cite: 2]. This advancement significantly improved the state of the art in understanding how deeply embedded these physical models are within the total Hilbert space [cite: 2]. De Lazzari leveraged these dimensional considerations to propose variations of the nonlinear conjugate gradient method designed specifically to approximate the ground states of quantum Hamiltonians directly on the variety of matrix product states [cite: 2]. 

***

## 6. The Broader Mathematical Landscape

The study of tree tensor networks and the Hackbusch conjecture is deeply intertwined with broader developments in algebraic geometry, polyhedral adjunction theory, and computational mathematics. The Simons Institute program on "Algorithms and Complexity in Algebraic Geometry" in 2014 provided critical early momentum for these intersections [cite: 21]. 

### 6.1 Multilinear Algebra and Generic Identifiability

During the period the Hackbusch Conjecture was initially solved, the study of tensors, low-rank decompositions, and their applications to complexity theory became a central focal point for algebraic geometers [cite: 21]. A critical question in tensor decomposition is whether a tensor can be written as a sum of simpler indecomposable tensors uniquely—a property known as *identifiability* [cite: 21]. Software systems like Bertini, utilized in numerical algebraic geometry, were adapted to compute low-rank decompositions of tensors, deriving new cases of generic identifiability [cite: 21].

Buczyńska and Buczyński's continued work on apolarity, border rank, and multigraded Hilbert schemes [cite: 22, 23] reflects the deep reliance on understanding the defining ideals of Secant varieties and Veronese reembeddings [cite: 23]. Evaluating the exact flattening ranks of hierarchical tensors relies fundamentally on these advanced tools from commutative algebra and toric varieties [cite: 8, 23]. 

### 6.2 Extensions into Polyhedral Combinatorics

The authors pushing the boundaries of tensor containments have simultaneously made strides in related combinatorial fields. For example, Sofía Garzón Mora and Christian Haase have utilized lattice polytopes and poset structures to construct modified algorithms for tensor networks [cite: 15, 24]. In concurrent research, they modified original adjoint polytopes using the "Fine interior" of lattice polytopes, developing a Fine Polyhedral Adjunction Theory [cite: 15]. 

By creating a system that behaves more robustly for decomposing polytopes into Cayley sums, they established the finiteness of the Fine spectrum [cite: 15]. They applied these geometric techniques to construct counterexamples regarding Ehrhart tensor polynomials and weight functions, demonstrating the profound overlapping synergies between discrete convex geometry, Ehrhart theory, and the algebraic categorizations of tensor network varieties [cite: 15, 17]. 

***

## 7. Implications for Numerical Analysis and Data Compression

From a strictly applied standpoint, solving Hackbusch-type conjectures validates the numerical stability and approximation power of hierarchical and TT formats [cite: 1, 7]. 

When algorithms are developed for solving high-dimensional partial differential equations (PDEs), such as the time-dependent Schrödinger equations handled by software like WaveTrain, exploiting the TT format mitigates the curse of dimensionality [cite: 3]. The ranks of state vectors in quantum chains frequently depend only marginally on the chain length $N$ when utilizing TT formats, allowing computational effort to grow linearly rather than exponentially [cite: 3]. 

However, multi-dimensional non-tensorized approximation indicates that if the interaction structure dictated by a physical system or differential operator aligns better with a hierarchical tree (HF) than a linear path (TT), the required tensor ranks will diverge [cite: 7]. The containment exponents calculated by Garzón Mora and Haase [cite: 4] and the flattening rank algorithms computed by Buczyńska [cite: 12, 14] provide exact, predictive boundaries. They mathematically inform data scientists and physicists precisely how much extra memory and matrix rank they will incur if they force a naturally hierarchical dataset into a sequence-based TT format, or vice versa [cite: 4, 12]. 

The identification of $d$-variate functions through recursive variable clustering (a process termed *quantized tensor formats* [cite: 7]) is shown to be formally stable only when the combinatorics of the tree mapping the $\beta$-rank partitions align properly with the data [cite: 7]. 

***

## 8. Conclusion

The Hackbusch Conjecture, which originated as a hypothesis comparing the encoding capabilities of binary trees in numerical tensor calculus, has matured into a rich, multidisciplinary domain known as the study of Tensor Network Varieties. 

The successful 2015 proof by Buczyńska, Buczyński, and Michałek established the fundamental differences in encoding complexities between perfectly balanced hierarchical formats and maximally deep tensor train formats [cite: 5, 6]. The subsequent 2020 generalizations algorithmically bounded the exponentially growing flattening ranks of tensors within arbitrary TNS models [cite: 12, 14]. By 2026, the formulation of the "containment exponent" and the utilization of poset-based DOAD sets by Garzón Mora and Haase successfully transformed the conjecture into a universal combinatorial framework, capable of diagnosing the topological compatibility of any two full binary trees [cite: 4, 15]. 

Concurrent research into the dimensions and spans of uniform matrix product states on cyclic graphs has anchored these algebraic findings directly to the forefront of quantum many-body physics [cite: 2, 10]. As high-dimensional modeling continues to demand ever-increasing efficiency, the strict algebraic and combinatorial bounds born from the Hackbusch-type conjectures will remain indispensable tools for navigating the curse of dimensionality.

**Sources:**
1. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNOdhpVLiNQv_87tjyYYslmshTRphCF6S-Wcay_vikEorxkanxerwpwhg06gEv8iYxxKtZjfHq4nAeSIMx8cFEVkfgpYxj803q3RF0_tWqCOyf-dO4x78wQlJTGJEPReGyez3Jy0Kytvldxf9f6Fa8FNbrJaewQEA=)
2. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbkSgZqgow2ZUiILnEjEYeEbij81hZZxtVtYbNtU9wdm37J07THV6UxOTtdDIaCDuVUhIAW4rrk4i4met6JOA3JNm3HxbL-_jKEIkDC3VFr919P3EoL-TN249BzKORqPEelPzvOPcpRUyOs_iMRrJAueqowieVJF5Q4j8MBOpIE05IZtqMSk7CvhreZm0hV_UC8qOwkEeZrA==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHv8T2siJZaY4D17FFfrXTBBOnI_85cvQ8rtMIGUomOoyinpdizGY4-32_0pzersQKGfKuzHIa9Hc1l4bSRBBbgHSuf9Z6GIA8pVKSCLJKpBx4Z3nOykDbgIuLdA2wQ-tsjahr6M_faey6zh5B0RpsgA0ZQPOzM-Kh4m43KA4mXVWfT)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEni_qbeG8tsC5fWKpMLHpDBFEn1lzrGcJnig963z2TjjBa3_Vdjc91i-fb0bXSfC6gGAcZ5P2r8iY97YjHDFttj2f7uraggCXy-g2DlOEdMIIjKje1)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHm2GIVKU3yXW3-H-hCzmGx3pS6SakistIUKdJSWA9-0bmaSnHcnUpOeXhGxjh1XLh0qzmbaEN3bNxEpb5RWR6hsh66b1hRyi8cPf96pgFURplJdtis)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFnO2UFTf8I7xFzOEV9QGCawneBCKnoAkCpvbsfCEFfdNxycs_laDAJFIxDHxBXaZc8Kr6o5NiwMUDWXxuVYhts_L6J68mFyzfz-JPMCBLkxmXzQvr)
7. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmCdznA4a6HwjCES5k7vGQFAHgkbGfWLuY1M1CqfWcASSCy1gsXYzTDNRx-0RWfRHVN5-JZxhkflfN9Dg_G7DeMcBvfFWmZ7VWPDVhxhFifVk1NrlTcyUAxSwKP5UnXw-oQ6mWiYlQ-gX5HrgIuY-ts55O)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYjRUDW68UlT-7MBFABv5Lesshi42v5BotTN3m09tsPMjZ5bKr_nYg-F0EUbrfV8fmURY2jB1K1pQaC5J02yqcMLCXTf91tZXO4LspN7vWtO-qj8jRjMthItLpWIFPPSoJZ1ycYavie1EYB5gXXLSO0ne52S7I6P6k4HhmGDpFNdO2qRyopQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy34L91PvMv1CNF3Hnbw8Qq7XSoTvRKH0Efs1ZlSW_gYf_dWfe3gcIE5TBq21SqhxEX3Kf0JQo6Hd6k1ywcC7aYpDrUwsj91ABC-DppWSCe62F47fR)
10. [sigma-journal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEadaJsqovIOWnqCKvzeW29WSXEpnIQoj_aUeuP5qjy9ztolg6Mth7EZYskdPu3IXT-et4vyr8weyjW_a8iMLuWpA-2qj6TGtKRYlwcNJn79prxAH40hmxV)
11. [nauka.gov.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbg6oQ13IZxzxIqOnmojH32inUsZIVdawbbyY6qxt6P3N9AkkEDhQm7JnVBMEpAeBpe1NoNIBz2niAA3E-kzkguLpQxzgy7cQz0DMXXDsMR9qWVom8h533Dn0bIQ_MWCGym49s5vuZ1m0gGd5bFE0lL-Kbo_BK7idKgPBB-PTginUi6IZ9tA==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwtkesXTDPWYNT_gzeKmQ9DIi95-RY6X49ZIbCck-X1Bs4rXD400iWL7iQDznkMqGKDxJA2t3wZJeR2kmmTpP-WN7eE1SMDdrPlbWWPp5TAZaiLzNq)
13. [orcid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaJT4KIBze6h9877ifsG8vBluDUCL-MsrCpcDzF1FXwHfKgcAp7cNj9WDP4g8481T1CUS68aE7A1AtX_SUWN19_udgLa4UuFiz1d51eVomPjq8jxqb2ZWJscQ=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4uugmSd-iaUqtV6Yc_DIEGnY53TI7HDOSqUa2FRBjFdDDvLuvwgTSja8SaCkW5Roi1h86Y3fzO7nKwPV5M5OZHfRK42C8NVvCvXcx9MYzkTMkmmx2)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVmKyhOD2bEdF1j2IoOi9V4k4LSvRQBZhltNteRpS4woUnhAdl7cgVjvR6dM903PXR58DW8WuZ2VFJQ_bV4hn65_8e-Hp7wwnKkikQsysnG7GANLjSdjp1bhqkdentMs-EsNkGqd_zqHYKIrXsooIOkE1tfdqXTBR0XCcwibc-IJmWh06yEN8=)
16. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFIQTcH-Rq7rcwOsh4hVWRj2m8TIXizZ2f17ArRIBYvLHhAbnVf8EoEo9mESHOJlea3oNSCHoRfw7uB_ahhG0G4ls1DO9frL31AKdd6KyguFqEOBZ9BmdFNaCE6jHB1V_7zblyhw2-aLyhp_tiTglc9WZ7LhNnw7xKArFRTT08sWx1AQ==)
17. [fu-berlin.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGawDz4YJOTDuiPUsshLdUGdSEmuzJuBYaGwkpCvH35cbixIFTH2nELVjy0TI7D-3kvxHvdblSxrEZq9Cm7NuizNSf3IaKImwQzvnl7NHkPN5UnPhGUyNiTQYOeb92YxNzsnT3Tyxh2Uiuu5bRGTGnfndEeigQFsYI_68c8ANkxiHm-gtnM3BlfQToJbNXM)
18. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECJYfnF6XUlEstnJVdmL-HElzod4AnWaLry9SXEVtTKxJzvbHUaEBvA_rxtF9yw1oqhz6qOT1h98TbnJOJu8dJDg7gd_U6io9ZClDYO8INI4o2aUtDI-PQZg6UmQ_vyogqtEybsRK9ZmwRWIOpz_YaYUwigjYwiS1WffvN7vqv1t9XJA==)
19. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIJXNqEeA-WYviri8Vf_QibP5u14mtEbKTHSNUBvP1ZUwd4btIXy8mS1YXlOB-pAqsCR0wmLyyp-UEpQsL3quEq7zBuKKypuKKVZo9jJGsUm8i3ziyzn4Hmipju8Be4fapaLo7At1gof2oAUibL3OYR2QUVWeYbRlgpjvcy0Wib1c_lw==)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFPWUvov3kAWet9HJhEylf3jLN136r_YYHdT7-p5S-Cb5kXnDDBKGNET3OGQ8pZ0RUlWyCfc9PxwF-cPp3r2XLiSipFyI1HpNv5F5SdkwKwOeKOTMAgKR34qIyZwzayY2bImj4MdN7cQk2YSERmZYAmnsj675FEfHcydO_WFZXZ7jorAKr3JEh_Aee1XEixNc=)
21. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERzkcH9M1nNFLC9ekPfFCX4Tl5MEpEw9JI4FXh4tptf34XrOUNwHZf2aTXyz416eJfx9GJDqe6vmh5Y6pTPxctagxxBi-1gPtCS8fQMsk3pOi4LMS4WSq1qrjrHmVGaBIZ8a1fFLEdsVpfyGJ44vC4DTT4pjdUUZJG3-Sy_aMQazR54WFcwpiTHola2LYqoaPwep5KbZsq8OjROOrK9Cwmpn_dwK39iXUHCVubhn5hWRmOvUg=)
22. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEALPXnw2BV73rl7gcu9iPAOKvfZrEab0SWWrsxiNTp_VHXzJwZczhOEWpkwQsXSHZSm64EKIAqjjoFKt04mLYwAt6GqJ_YxKdrL4mz6FYmHRyYf7dOTVBHRcElVC6T3u7O-GU=)
23. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQyj78Xer6xc3Iv86CroDcHO0QVVriMMFe2W5zcK1lKIL5yvkad_xiwi6i2M8RZNjcEVcYmsI9zJbVdsvSxe-I2PLAaBawRuVWYj0rTsQ4W8bqvZ3-HCXiINFGLjuLqpR4pEIvzYl3CZnS)
24. [fu-berlin.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESwLxVeip4Y1vxP0D0wP_MCZqiLbUQA3EjdQclBn0DMgZ6wnYiWcItTkzVbB-MRQKx235EmXLGPFFO5z-FdiqzhCnWOhREibs1uoQHz3HpE7Q7hKoJyOlaDemQV8lLToOD7Oq40VZpeNiZyv_TAfdahft5F8DtGc4Jf8ZsQ61tW7f7MEbd-q4i9bcjLIDvV1v0r7T9_6UzKhGHLL9jQGckUcXJvSYf5WJGAg==)


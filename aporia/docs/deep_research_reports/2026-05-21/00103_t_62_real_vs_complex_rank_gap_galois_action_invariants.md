# T#62 Real vs complex rank gap (Galois-action invariants)

**Pythia queue id:** 103
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdBaDBQYXY2S0E3bS1fdU1QejduVnNRYxIXQWgwUGF2NktBN20tX3VNUHo3blZzUWM
**Elapsed:** 497s
**Completed at:** 2026-05-21T15:04:20.411833+00:00

---

# T#62 Real vs Complex Rank Gap and Galois-Action Invariants: A Comprehensive Analysis

**Key Points:**
*   **Tensor Rank Discrepancies:** The rank of a tensor inherently depends on the base field. While the real and complex ranks of matrices (tensors of order 2) are always equal, a fundamental "rank gap" emerges for tensors of order 3 and higher, where the real rank can strictly exceed the complex rank.
*   **Galois Actions and Admissible Ranks:** Decompositions of real tensors over the complex field are subject to the Galois action of complex conjugation. The concept of "admissible rank" utilizes this action to classify tensor decompositions based on the invariant topological "cost" of complex conjugate pairs, bridging the gap between purely real and purely complex geometry.
*   **Arithmetic Rank Gaps:** In arithmetic geometry, the term "rank gap" also describes the strict discrepancy between the generic Mordell-Weil rank of an elliptic curve over a function field and its special fibers. This phenomenon is deeply constrained by the Galois action on the curve's Tate modules.
*   **Invariants as Diagnostic Tools:** Polynomial invariants, such as Cayley's hyperdeterminant, serve as critical tools for diagnosing the real rank of a tensor when its complex rank is known. Similarly, cohomological invariants distinguish algebraic structures via Galois cohomology.

The mathematical landscape surrounding rank gaps and Galois-action invariants spans multilinear algebra, real algebraic geometry, and arithmetic geometry. At its core, the dependency of structural rank on the choice of the base field reveals deep topological and algebraic constraints. For practitioners in quantum physics, computer science, and numerical analysis, understanding the divergence between real and complex tensor ranks is crucial for optimizing data compression and modeling entanglement. In abstract algebra, classifying these gaps requires sophisticated invariant theory and an analysis of how Galois groups act upon geometric and arithmetic spaces. 

While the generic behavior of tensor ranks has been completely classified for small dimensions (such as binary and ternary forms), the exact boundaries of real rank loci for higher-dimensional tensors remain an active, and sometimes debated, area of research. Similarly, in arithmetic geometry, conjectures regarding elevated ranks and systematic rank gaps are deeply tied to unresolved problems such as the Parity Conjecture and Tate's conjectures, meaning that absolute classifications are currently out of reach for general cases. The evidence leans toward a rich, unified theory where Galois actions dictate the rigid structures underlying both multilinear and arithmetic rank gaps.

## 1. Introduction to Tensor Rank and the Base Field Dependency

The concept of rank is foundational to linear and multilinear algebra. For a matrix (a tensor of order 2), the rank is defined as the dimension of the vector space spanned by its rows or columns, which is equivalent to the minimal number of rank-1 matrices needed to express the original matrix as a sum. A critical property of matrix rank is its independence from field extensions: the rank of a real matrix is exactly the same whether computed over the real field \(\mathbb{R}\) or the complex field \(\mathbb{C}\) [cite: 1, 2].

However, this field-independence completely breaks down for higher-order tensors. A tensor \(T\) of order \(d \ge 3\) residing in a tensor product space \(V_1 \otimes V_2 \otimes \cdots \otimes V_d\) has a rank defined as the smallest integer \(r\) such that \(T\) can be expressed as the sum of \(r\) pure (rank-1) tensors:
\[ T = \sum_{i=1}^r v_{1,i} \otimes v_{2,i} \otimes \cdots \otimes v_{d,i} \]
where \(v_{j,i} \in V_j\). When the vector spaces \(V_j\) are defined over a field \(K\), we refer to this as the \(K\)-rank. If \(T\) is a real tensor, its real tensor rank requires the components \(v_{j,i}\) to be real vectors. Analogously, its complex tensor rank allows the components to be complex [cite: 1, 3]. 

The complex tensor rank acts as an obvious lower bound for the real tensor rank, giving the universal inequality \(r_{\mathbb{C}}(T) \le r_{\mathbb{R}}(T)\) [cite: 1, 2]. For proper tensors (\(d \ge 3\)), this inequality can be strict, creating a phenomenon known as the **real vs. complex rank gap** [cite: 1, 2]. This gap arises because the topological closures of tensor rank loci over \(\mathbb{R}\) behave differently than over algebraically closed fields like \(\mathbb{C}\).

The multilinear rank (or Tucker rank) of a real tensor, which evaluates the matrix rank of various flattenings (matricizations) of the tensor, remains independent of the choice of field \(\mathbb{R}\) or \(\mathbb{C}\), precisely because it relies on the matrix case where field independence holds [cite: 1]. Understanding the gap between the canonical polyadic (CP) tensor rank over \(\mathbb{R}\) and \(\mathbb{C}\) is highly relevant in quantum chemistry, numerical analysis, and machine learning, where low-rank approximations are heavily utilized to circumvent the curse of dimensionality [cite: 2, 4].

## 2. Geometric Foundations: Segre and Veronese Varieties

To rigorously study tensor rank and its field-dependent gaps, we must embed the problem into algebraic geometry. The set of all rank-1 tensors of a given format forms a smooth projective variety known as the **Segre variety** [cite: 4, 5]. For a tensor space \(V = V_1 \otimes V_2 \otimes \cdots \otimes V_k\), the Segre variety is the image of the Segre embedding:
\[ \text{Seg}(\mathbb{P}V_1 \times \mathbb{P}V_2 \times \cdots \times \mathbb{P}V_k) \hookrightarrow \mathbb{P}V \]

When considering symmetric tensors, which correspond to homogeneous polynomials, the set of symmetric rank-1 tensors forms the **Veronese variety** [cite: 6, 7]. The symmetric rank of a tensor (or the Waring rank of a polynomial) is the minimal number of rank-1 symmetric tensors needed for its decomposition [cite: 8, 9].

### Secant Varieties and Border Rank
Because the set of tensors of rank exactly \(r\) is generally not topologically closed, limits of rank-\(r\) tensors may possess a rank strictly greater than \(r\). This leads to the definition of **border rank**, which is the minimal \(r\) such that the tensor lies in the Zariski closure (or Euclidean closure, over \(\mathbb{R}\)) of the set of rank-\(r\) tensors [cite: 7, 10]. Geometrically, the closure of the set of tensors of rank \(\le r\) is the \(r\)-th secant variety, denoted \(\sigma_r(X)\), where \(X\) is the Segre or Veronese variety [cite: 7, 10]. A tensor \(T\) has border rank \(r\) over \(\mathbb{C}\) if \(T \in \sigma_r(X)\) but \(T \notin \sigma_{r-1}(X)\) [cite: 7].

### Identifiability
A tensor of rank \(r\) is called **identifiable** if its decomposition into a sum of \(r\) rank-1 tensors is unique up to the trivial scaling and permutation of the summands [cite: 4]. Identifiability is a crucial property for statistical inference, latent variable models, and signal processing [cite: 4]. Interestingly, the real vs. complex gap manifests strongly here: there exist non-trivial Euclidean open subsets of tensor spaces where tensors have multiple decompositions over \(\mathbb{C}\) but exactly one decomposition over \(\mathbb{R}\) [cite: 4]. Consequently, these tensors are identifiable over \(\mathbb{R}\) but fail to be identifiable over \(\mathbb{C}\) [cite: 4]. Conversely, there are spaces of symmetric tensors where the typical real rank equals the complex rank, and the tensors are real identifiable, but not complex identifiable [cite: 4].

## 3. The Real vs. Complex Rank Gap and Hyperdeterminants

The simplest, yet most illustrative, environment to observe the rank gap is the space of \(2 \times 2 \times 2\) tensors. Over the complex field, a generic \(2 \times 2 \times 2\) tensor has a complex rank of 2 [cite: 1, 11]. Over the real field, however, the real rank can be either 2 or 3 on generic open sets [cite: 1, 11]. 

### Cayley's Hyperdeterminant
The rank gap in the \(2 \times 2 \times 2\) case is completely classified by a polynomial invariant known as **Cayley's hyperdeterminant** (also referred to as Kruskal's polynomial) [cite: 11, 12]. The hyperdeterminant, \(\Delta\), is a homogeneous polynomial of degree 4 in the 8 entries of the tensor, consisting of 12 distinct terms [cite: 11, 12]. In the physics literature regarding quantum information, this invariant is proportional to the "tangle," a measure of multipartite entanglement [cite: 1]. 

The hyperdeterminant acts as a powerful diagnostic tool for the real rank gap:
*   If \(\Delta > 0\), the real tensor rank is exactly 2 [cite: 1, 11].
*   If \(\Delta < 0\), the real tensor rank is 3, despite the complex rank remaining 2 [cite: 1, 11].
*   If \(\Delta = 0\), the tensor is degenerate, lying on the tangential variety, and its rank requires further specific boundary analysis (it could have complex border rank 2 but higher exact rank) [cite: 11].

This demonstrates a profound point: polynomial invariants that are invariant under the action of the general linear group \(GL(V_1) \times GL(V_2) \times GL(V_3)\) can distinguish the real rank topology [cite: 1, 12]. An effort to extend this to \(n \times n \times n\) tensors of rank \(n\) revealed that for \(n=3\), the sign of a polynomial invariant can still distinguish whether a tensor of complex rank \(n\) also has real rank \(n\) [cite: 1]. However, for larger \(n\), a single invariant's sign becomes insufficient to isolate the connected component of tensors of real rank \(n\) [cite: 1].

### Higher-Order Extensions
When extending the analysis to \(2 \times 2 \times 2 \times 2\) tensors, the maximum real rank is bounded bounded above by 5, while the maximum complex rank is generally 4 (with one special exception) [cite: 12]. The classification of canonical forms via the semidirect product of general linear groups with symmetric groups becomes significantly more complicated over arbitrary fields, requiring extensive computational algebra [cite: 11, 12]. Furthermore, for any boolean tensor in the finite field \(\mathbb{F}_2\), the maximum rank for a \(k\)-th order \(2 \times \cdots \times 2\) tensor can be bounded by \(3 \cdot 2^{k-3}\) [cite: 11].

## 4. Galois-Action Invariants and Admissible Rank

When a real tensor lacks a purely real rank-1 decomposition of minimal size, one must look to its decompositions over \(\mathbb{C}\). Because the tensor itself is real, the Galois group of \(\mathbb{C}/\mathbb{R}\), which is generated by complex conjugation, acts naturally on the set of complex rank-1 components [cite: 3, 8]. This Galois action is the genesis of **Admissible Rank**, a concept introduced by Ballico and Bernardi to unify real and complex rank theories [cite: 4, 8].

### Defining Admissible Rank
Let \(X(\mathbb{R})\) be a geometrically connected variety defined over \(\mathbb{R}\), and \(X(\mathbb{C})\) be the set of its complex points [cite: 4, 8]. Let \(\sigma : X(\mathbb{C}) \to X(\mathbb{C})\) denote the complex conjugation involution, which leaves exactly the real points \(X(\mathbb{R})\) fixed [cite: 3]. For a real point \(P \in \mathbb{P}^r(\mathbb{R})\), the complex rank \(r_{X(\mathbb{C})}(P)\) is the minimal cardinality of a set \(S \subset X(\mathbb{C})\) spanning \(P\) [cite: 3]. The real rank \(r_{X(\mathbb{R})}(P)\) restricts \(S \subset X(\mathbb{R})\) [cite: 3].

The **admissible rank**, \(r_{X, \mathbb{R}}(P)\), is defined as the minimal cardinality of a set \(S \subset X(\mathbb{C})\) such that:
1. \(P \in \langle S \rangle\) (the span of \(S\) contains \(P\)).
2. \(\sigma(S) = S\) (the set \(S\) is globally stable under the Galois action of complex conjugation) [cite: 4, 8].

Because \(S\) is stable under complex conjugation, any non-real points in \(S\) must appear as complex conjugate pairs. The topological and algebraic "cost" of a complex conjugate pair is equal to two real dimensions [cite: 8]. 

### Decomposition Labels
Any set \(S\) evincing the admissible rank can be assigned a **label** \((a, b)\), which records the precise distribution of the Galois orbits [cite: 8, 9]. The integer \(b\) represents the number of purely real points in \(S\) (fixed points of \(\sigma\)), while \(2a\) represents the number of strictly complex points arranged in conjugate pairs [cite: 3, 8]. The total cardinality is \(|S| = 2a + b\).

This labeling system provides a refined stratification of tensor spaces:
*   Purely real rank decompositions correspond to the label \((0, b)\) [cite: 13].
*   Maximal complex usage corresponds to \((a, 0)\) or \((a, 1)\).
*   If generic identifiability holds for a tensor format, there exists an open dense Euclidean subset of points exhibiting the admissible rank for *every possible valid label* [cite: 8].

### Typical Labels and Rational Normal Curves
A **typical rank** is an integer \(r\) such that the set of real tensors of rank \(r\) contains a non-empty Euclidean open set [cite: 7, 9]. While the complex generic rank is almost always a single value, real tensor spaces fracture into multiple distinct open sets, each characterized by a different typical real rank [cite: 7, 9]. 

For the rational normal curve \(X_d\) (corresponding to symmetric binary forms of degree \(d\)), typical real ranks range broadly from \(\lceil (d+1)/2 \rceil\) all the way up to \(d\) [cite: 9, 13]. However, the behavior of admissible ranks is fundamentally different. For rational normal curves, the admissible rank strictly coincides with the complex rank, and all admissible labels concentrate precisely at \(\lceil (d+1)/2 \rceil\) [cite: 8, 13]. 

Specifically, if \(d\) is odd, generic identifiability holds, and there is a dense set of points possessing any valid label \((a, b)\) such that \(2a + b = \lceil (d+1)/2 \rceil\) [cite: 8]. If \(d\) is even, generic identifiability fails, but it has been proven that there exists a non-empty open subset \(U \subset \mathbb{P}^d(\mathbb{R})\) where each point has an admissible rank of \(\lceil (d+1)/2 \rceil\) [cite: 8]. Thus, admissible rank smooths over the chaotic variations of typical real ranks, providing a stable geometric invariant that deeply respects the Galois conjugation action [cite: 13].

| Rank Type | Allowed Support | Label Format | Behavior on Rational Normal Curves |
| :--- | :--- | :--- | :--- |
| Complex Rank | Any \(S \subset X(\mathbb{C})\) | N/A | Generic rank is exactly \(\lceil (d+1)/2 \rceil\) |
| Real Rank | Only \(S \subset X(\mathbb{R})\) | \((0, b)\) | Typical ranks range from \(\lceil (d+1)/2 \rceil\) to \(d\) |
| Admissible Rank | \(\sigma(S) = S\) | \((a, b)\) | Rank is \(\lceil (d+1)/2 \rceil\), all valid labels appear |

In some pathological cases, the admissible rank can actually be strictly larger than the usual complex rank, and there are specific points where a label does not exist because no conjugation-stable decomposition of minimal size can be formed [cite: 8]. Scheme-theoretic extensions of the admissible rank also exist, capturing the length of conjugation-stable zero-dimensional schemes spanning the tensor, which serve as analogues to the cactus rank [cite: 13].

## 5. Polynomial Invariants and Real Rank Boundaries

The transitions between regions of different typical real ranks in Euclidean space are governed by **real rank boundaries**, which are algebraic hypersurfaces defined by specific polynomial invariants [cite: 14]. 

### The Real Rank Two Locus
The real rank two locus of an algebraic variety is defined as the Euclidean closure of the union of all secant lines spanned exclusively by real points [cite: 6]. The algebraic boundary of this set generally consists of two distinct geometric constructs:
1.  **The Tangential Variety:** The locus of points lying on tangent lines to the variety [cite: 5, 6].
2.  **The Edge Variety:** The locus bounding the real secants [cite: 6].

For tensors (Segre or Veronese varieties), the real rank two locus is completely characterized by hyperdeterminantal inequalities [cite: 5]. The tangential variety often serves as the algebraic boundary of this locus [cite: 5].

### Binary and Ternary Forms
In the study of homogeneous polynomials (symmetric tensors), binary forms (2 variables) and ternary forms (3 variables) offer rich structures for rank boundary analysis. For real binary forms of arbitrary degree, the algebraic boundaries separating regions of different typical ranks are universally constructed as the union of dual varieties to suitable coincident root loci [cite: 9].

For real ternary forms, the goal is to determine the semialgebraic sets of sums of powers (Waring representations) where the real rank strictly equals the generic complex rank [cite: 14]. 
*   For quadrics and cubics, complete semialgebraic boundaries are known [cite: 14].
*   For quintics, the real rank boundary is a highly complex hypersurface of degree 168 [cite: 14].
*   For quartics, sextics, and septics, the real varieties of sums of powers are stratified by discriminants that are deeply related to, or directly derived from, hyperdeterminants [cite: 14]. 

For instance, a hyperbolic real ternary form of rank 3 yields a variety of sums of powers that is isomorphic to \(SO^+(2, 1)/G\), sitting inside a complex Fano threefold [cite: 14]. The topological properties of these real representation spaces frequently exhibit twisted circle bundles or Möbius strips [cite: 14].

To compute these polynomial invariants computationally, computer algebra systems like Macaulay2 or SageMath are typically employed. A generalized conceptual code block for evaluating the secant ideal bounding these ranks is as follows:
```macaulay2
-- Conceptual Macaulay2 script for examining the secant ideal of a Segre Variety
-- Define the polynomial ring for a 2x2x2 tensor space
R = QQ[x_0..x_7];
-- Define the parametric matrix representing the flattenings
M = matrix{{x_0, x_1, x_2, x_3}, {x_4, x_5, x_6, x_7}};
-- The ideal of the secant variety is generated by minors
I_secant = minors(2, M);
-- Cayley's hyperdeterminant is a degree 4 generator 
-- diagnosing the rank gap boundary
```

## 6. Arithmetic Geometry: Rank Gaps in Mordell-Weil Groups

The terminology of "rank gaps" and "Galois-action invariants" takes on a parallel, highly profound meaning within arithmetic geometry, specifically concerning elliptic curves over function fields [cite: 15].

### Generic vs. Special Fibers
Let \(K\) be a global field and \(E_\eta\) be an elliptic curve defined over the function field \(K(T)\). The curve \(E_\eta\) can be viewed as the generic fiber of an elliptic surface over \(\mathbb{P}^1\). By evaluating the parameter \(T\) at a specific point \(t \in \mathbb{P}^1(K)\), we obtain a specialized elliptic curve \(E_t\) over \(K\). 

Silverman's Specialization Theorem guarantees that the rank of the generic Mordell-Weil group is a lower bound for the rank of the specialized group for all but finitely many values of \(t\):
\[ \text{rank}(E_\eta(K(T))) \le \text{rank}(E_t(K)) \]
for all but finitely many \(t \in \mathbb{P}^1(K)\) [cite: 15].

### Elevated Rank and Systematic Rank Gaps
If this inequality is strict for all but finitely many \(t\), the elliptic curve \(E_\eta\) is said to possess an **elevated rank** [cite: 15]. In such cases, there is a systematic "rank gap" \(\ge 1\) between the generic Mordell-Weil rank and the special Mordell-Weil ranks over connected components of the family of Weierstrass models [cite: 15]. 

This systematic gap contrasts sharply with standard expectations derived from Tate's conjectures, which predict an average rank gap of exactly \(1/2\) across families of curves [cite: 15]. Currently, all known examples of elevated rank over \(K = \mathbb{Q}\) are conditional, relying heavily on the unproven parity conjecture for elliptic curves [cite: 15]. A classic conditional example discovered by Cassels and Schinzel involves the isotrivial family of quadratic twists:
\[ E_{n,\eta} : n(1 + T^4)y^2 = x^3 - x \]
where \(n \equiv 7 \pmod 8\). The generic rank is 0, but the root number \(W(E_{n,t}) = -1\) for all \(t \in \mathbb{Q}\). Under the parity conjecture, this forces the specialized rank to be at least 1, creating a continuous rank gap of \(\ge 1\) everywhere [cite: 15]. Additional standard conjectures over \(\mathbb{Q}\) suggest that no *non-isotrivial* elliptic curve over \(\mathbb{Q}(T)\) can exhibit elevated rank [cite: 15].

### Galois Action on the Tate Module
The structural constraints preventing or forcing these arithmetic rank gaps are largely dictated by Galois actions. The absolute Galois group acts continuously on the \(\ell\)-adic Tate module \(T_\ell(E)\) of the elliptic curve [cite: 15]. The Mumford-Tate conjecture and related big-image theorems describe the closure of the image of this Galois representation [cite: 16].

In the context of rank gaps and Weierstrass models, if the curve has potentially good reduction and its 2-torsion \(E[cite: 2]\) is split, the local Galois action on the Tate module must have a pro-2 image [cite: 15]. Consequently, this Galois action is forced to be tame, strictly limiting the structure of the finite cyclic 2-group representation [cite: 15]. Evaluating the trace and determinant of specific Galois elements \(\gamma\) in \(GL_2(\mathbb{Z}_2)\) under the constraint of the cyclotomic character demonstrates that the Galois group cannot contain elements of order 4, restricting the local geometry of the curve and preventing certain types of rank inflation [cite: 15].

## 7. Cohomological Invariants and Galois Actions in Representation Theory

The notion of Galois-action invariants extends beyond elliptic curves to general algebraic structures via Galois cohomology. 

### Local-Global Principles and the Rost Invariant
In Galois cohomology, classical local-global principles for the Brauer group can be generalized to higher-dimensional spaces. A primary tool for this is the use of cohomological invariants, which take values in Galois cohomology groups \(H^n(F, A)\) for a smooth commutative group scheme \(A\) [cite: 17]. 

The **Rost Invariant** is a prominent cohomological invariant used to classify torsors under linear algebraic groups [cite: 17]. By utilizing patching techniques and theorems derived from the Bloch-Kato conjecture, mathematicians have developed local-global principles for these invariants, ensuring that if a cohomological invariant acts trivially locally across all discrete valuations, it yields triviality globally [cite: 17]. This effectively bounds the "rank" or complexity of torsors by ensuring global structures are entirely identifiable through their local Galois constraints.

### Complex Reflection Groups
Galois actions also provide invariant frameworks in the representation theory of complex reflection groups. Let \(W \subset GL(V)\) be a finite complex reflection group. The field of definition of \(W\) is the field \(k\) generated by the traces of the elements of \(W\) acting on \(V\) [cite: 18]. The set of generating matrices for \(W\) is globally invariant under the Galois group of \(k/\mathbb{Q}\). Therefore, the Galois action induces automorphisms directly on \(W\) [cite: 18]. 

The invariants of \(W\) in the symmetric algebra \(S(V)\) are called polynomial invariants, generated by algebraically independent homogeneous polynomials [cite: 18]. A primary invariant is the **discriminant** of the complex reflection group, obtained by taking the product of the linear forms describing the reflecting hyperplanes, raised to the order of the corresponding reflection [cite: 18]. The study of these invariants and the regular elements of the group connects deeply to the topological properties of the hyperplane complement \(V_{reg}\), which acts as a \(K(\pi, 1)\) space (Brieskorn's conjecture) [cite: 19].

## 8. Representation Theory of Tilting Modules and Tensor Products

In the realm of algebraic groups and modular representation theory, the term `T(62)` and similar notations correspond strictly to **tilting modules** and the direct summands of tensor products of simple modules. 

Let \(G\) be a reductive algebraic group (such as \(SL_3\)) over a field of characteristic \(p\). The simple modules are denoted \(L(\lambda)\) for a highest weight \(\lambda\). A fundamental problem is describing the indecomposable direct summands of the tensor product \(L(\lambda) \otimes L(\mu)\) [cite: 20, 21]. In characteristic \(p=2\), the tensor product of non-trivial restricted simple modules decomposes into specific indecomposable tilting modules \(T(a,b)\) [cite: 20, 21]. 

For example, a tilting module \(T(\lambda)\) is characterized by having both a Weyl filtration (subquotients are standard modules \(\Delta\)) and a good filtration (subquotients are costandard modules \(\nabla\)) [cite: 20]. To determine the internal structure and the \(\Delta\)-factors of specific modules like \(T(6,2)\) or \(T(62)\), one employs algebraic formulations such as the BDM (Brundan-Dipper-Kleshchev-Mathas) relations along with the known structures of the Weyl modules [cite: 20, 21]. The dimensions and socles of these tilting modules dictate how tensor representations scale and decompose, maintaining a strict combinatorial hierarchy similar to the stratification of real tensor ranks [cite: 20].

## 9. Computational and Applied Perspectives

The theoretical gaps between real and complex tensor rank, alongside Galois-action constraints, have highly tangible consequences in computational mathematics and applied sciences.

### Tensor Networks and State Space Models
In data science and systems engineering, multidimensional data is managed using Tensor Networks and higher-order decompositions (such as Tucker decomposition and CANDECOMP/PARAFAC) [cite: 22, 23]. When computing low-rank approximations of real tensors with unknown multilinear rank, algorithms must navigate the real rank boundaries. If a non-negative tensor is restricted to a non-negative rank decomposition, the non-negative, real, and complex ranks are proven to be strictly equal provided the non-negative rank is strictly less than the complex generic rank [cite: 4]. Furthermore, for such tensors, unique identifiability is guaranteed if the real tensor space is identifiable [cite: 4].

Algorithms utilizing Newton methods or algebraic matroids often rely on generic complex properties because evaluating determinants over \(\mathbb{C}\) (or \(\mathbb{Q}\)) is computationally cheaper [cite: 24]. However, if the algorithm fails to account for the real rank gap or the admissible rank labels, it may output false negatives or fail to converge, as the target low-rank real tensor might lie outside the real secant closure despite being within the complex one [cite: 2, 24]. 

### Quantum Mechanics and Entanglement
In physics, the state of a multipartite quantum system is a tensor in a complex Hilbert space. The tensor rank corresponds directly to the minimal number of separable states required to represent the entangled state (Schmidt rank generalizations). The invariants that dictate the rank gap, such as the hyperdeterminant \(\Delta\), physically manifest as entanglement measures like the tangle [cite: 1]. The invariance of these measures under the local actions of the general linear group ensures that coordinate changes do not alter the fundamental entanglement classification of the quantum state [cite: 1, 10].

## 10. Conclusion

The gap between real and complex tensor ranks is a profound consequence of algebraic geometry mapping over disparate topological fields. While complex spaces are algebraically closed and yield uniform generic ranks, real tensor spaces fracture into multiple typical ranks separated by intricate real rank boundaries. 

The introduction of the **admissible rank** by Ballico and Bernardi elegantly bridges this gap by invoking the Galois action of complex conjugation, assigning a rigorous topological "cost" to complex decompositions of real points. This framework smooths out the chaotic typical real ranks, providing a stable geometric invariant that honors the underlying real structure.

Parallel to multilinear algebra, **rank gaps in arithmetic geometry** highlight the difference between generic and special Mordell-Weil ranks of elliptic curves. Here, too, Galois actions—specifically on Tate modules—serve as the rigid algebraic scaffolding that limits rank inflation and dictates the local-global behavior of the curves. From the hyperdeterminants of \(2 \times 2 \times 2\) tensors to the Rost invariant in Galois cohomology, and the tilting modules of representation theory, the synthesis of rank theory with Galois-action invariants remains one of the most conceptually unifying domains in modern abstract mathematics.

**Sources:**
1. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVbXVegN5EhdJw_abhbRm7dK-i0DfTjRksdcCL8u6SjlQYcEebLcM74v5wv3GoSGngGT-qpXC1_rgLB50lq6XkMxTavOOiVyx7uwoBLonpWNehPD2iOBrodI-OhIKtcqjDhjLYLBsz-VyA)
2. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFerdeISOvoDYGoTQmnQnksXTl4MTX0gNM0Kw_9X_RR5Gt8TolNmJmsFUDZbahjVnvZFXKBQC4sWKZY7eIW25lDrcE82e-tMGFg705c9eRc_wdZRL84IpnJpFvMMVmDjigx6BtOSL_1hEosba3WWGN9YPvnQNTLhQhtG7BmCY9BYmJvg4EDgsjc1y3Ce75nlSaJajvX47syRRwdLUZEKBy0AYmhOrsGNo-aw==)
3. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERrtFqIKIQexrqdYWki-I4JV-6_6WPmpeMvA3thtu-zVoQ8q6qLlBVFA6tXHLzHTR5IJxHypbxPW0jPK310OLTsXJOr4GjjTnoPKDBxQ6agXONT1AuaYTDj-Tz)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmKNHEjQ2yWorSWX6zyi6Hmul2zAoxa0Z6h_58lor-zyiLb5mKVhLjQB9w9LDztB5nzlbmGmtQGBGQQTUZk9mMBLsDMmXsBcW63-vC9STy4vMeQUviFZ2ha7Za1w_6G6amGDX-I7ZHu4mLeLzJVsvdiE0TQToLMWMtmDpoeqyCsJ0NKws2P55DUL_OS4R4K_UKKndH3P6buw==)
5. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgPWv4KP7r3h_GaduejeAMDGbydu93jM032svKmgIegnjX9GjTXtBXi6V2jIbRs_8hItqwzMuWj0lA-8wvNLX1l2O0sy-Jf36esviEV68ngNbZ06RYU8w7DUdLM03RCoi5)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMaD7SdpRYKhGz56DcRjYZxG6HGC4rr4j3kVccSZnQDFHpjKjs8TA08pHkzgzuoZaFOOm5vbXzofFwqgBPgMASe8ChUypcb1ADIIQGWsEwsHoBNb2iFgJKr_hGsCzbdCXsmRTIzeXLsZLpkbudwXougOHG-gqo11XttZLNfWBr)
7. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGV-GSYwjQRsRAVM0mEhMu3H-kYg88HbiESkEMwuBxVKGmW3WdZuspqbg9kU06QtqW8NVEZYUG-2AicMKZWGuqjzUTfkx1lNV1oDNsNs3hEaZUKPPqVx5px96fBkcvddTnkiY1gfiBju-yl22j41PEIDA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcAfwQvugpiN79PGy7XDbgHll13mz6EO2KV9wLLY6_wb0nhf03tiz0Dz-RqpRu266klzOY8zdn3GTquVH_N8kWxeDwlOdYsGSSrsx-N67O_8hZ2G9gKA==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuZmjhg6Qp92dbfg4Dn3xNBZyuteoOZ1flOTYI81NkS_-8P6xepRqantNu0qgrpoarDQrWTq9AzLXb3larV5LjLlwMLjj5O7KaZXvuXPo3OlCUOOtgsBDZM83NBQiIlXHKRIcChbnedxZwLiJB_O-LKHPwfhM1DEDmNYLZ8xM2iFKSmTWPKaFMHXO5)
10. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGitmihknlYigFgRtM8xhFIh7K-gMqIpW-VzwfOshnsObTe4Utaz7n4EMvuL_jiYNIN07-SrLD9suXJKRKuVWBcrXxkyf8CfNJE8WxToHllwdPMEyIYD2fWQOeJHhXkoL5F_I=)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFa-ckypHF6JaNMSPm9MV2x7zTF-b2xdjPRJU56b6xyeIFcoUR0iF57pCCzkQ9ObZFY9sShacUjj1jE_T7MzvdsGMlMI6h0nwh6wJhZVMgvo_lfVsKJYvWaCEKbjUz2VTtWGO0nttpZHSlKNUSwcrwnMVBRNdWUBYnZyCFknOpSFhCyCNAnBgFdyWA8CW8tAzMcAC2qD_Pz4top2Kj9qqtvyPfOpUhWtRYm2SqhYZd-UogXzvsf-ZYeoiG2ouHlFGpjA9bTtynDWuvQ-TZFnJM1p5W5it4FPbD8IVQvBdQYYGlFKzTe9xxUjCI2PFTyTtA2g8Vvx51QM4svtfmYPR6p5diIb3Ow08x8w2tTHMG7GWrWbQ=)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqr3Ui1ZCchtWkULEWOu0L2_SSDZt1rS2fnBDawkv7f9atbdT3XAUv2S8P0u_OUfMypx7r5HCRUkwK_8e-4CnlegnKVJQLiMa5HOGa9G3C2EIbafVh7YC48y7BwKXRLh-BGvbyxp-arXTZM3DLz2KZ4wtLh9Vb0N-FUnr2hxMQC7nIEA==)
13. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdffeH0lTvJw3y4sKr7sTVO7VM10XYtwqREq8HQ9IOO8bw3YRwhMUI5UuTZF2mmSGg98eRgi1c4pWoFfw-jvfAuueLOYez2qFIIuwdYKoE0sSpudweo7xJyRgeYyOefMFVXf0l_Kd6PEw5cFFMYZ8m)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtArxPg5i6eLRO3ErLnRmvBt8qkbdUhy1C3rOIlh_iLOGdQwPNM7bedNV661BW1EBDsm5lWUVF8d_bBoUlTbdP83iOy8nmDQopOWys1X-xu1vG-UIJHQ==)
15. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsoa03yZvXkDWn0ijT4HQ1SOm43HzIxO3exZoLqUZfl1v0XbhFkrPJRDwDn8-T1p9gqNPJua-qNSGNXf4Q9X8Nv5X4qcPdhQBNQDMmLHeW4sig_yU8LzBRQTs0Bek_3kPWGRuSRTt67A7wNzNL0gjcjPI=)
16. [nju.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbnyuAV9qdF13hjmiadDs9-SdK_6W5Bh7zKQUjKoG7tC8XmluLsdwHT4XV0ft6VGElKo_5KbynpKjDtQTkCOUUNw148JeVdbBmjYvCl1zd6TqrtmejwZM3YtqBIJgBobRUM6DRXd5TEA_H)
17. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcqsYCfbLUjYk_-oy4EQwOHjCw6EyAiR6QN3YiELirIUA4sIRwReybyizj7S-nLfeSxuAR84Qb4zk65E6NRTEOFeyUwLD04ALKsMPu4Ss1cL4_HyK92WgaVThoyVAhCYgiUYW6kA==)
18. [imj-prg.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-ISmkjPD92RjZ1j4YKhwPoVLEvcj10IzINNG3XnJXieFD0sGnjzfLQTjdbZCDJi9Vs6WtSMNGl-wnrhrZZrHu6HrptXaaCGBIVLL4CG-0ep68frt8vZBo634jfXIAiOhQW3Vee336d2D15BEbEtEDOQCp)
19. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBQmds_a9xTUHwdahOIzYRpVjrDrU28Z5balVBLBiGY2g2uEzIqSAEGGxRx6pT6YwGAwJc8XXUl7n68XUzgnT6c0qRNH0xZlUSjrUerquuz4FJqRyUyuHacRiKZLG4rN-4e8JC4ikg5CzeU5tiXqrLksy8eZ6jHRNnGEirOtyr2SIclQ==)
20. [uni-bielefeld.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_AGYfeCM3GdqGcqsZHSWzNX3Q6uL0ZYS-xpqCQ1hAhCnnQFVNFKVHkJWp4bcm3Z4n4tK9jro_B9l6uXOPwIbeTJYze4e1G364_Jl3fy6NoFLD3AZY6NEwm52GoZxE6Wy_tw9o6Y78wR8w3Li9zg==)
21. [ieja.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkFYQbW2hATpMPe8MCuSL_aMjS4vtFyyyu54Tx4QQ4S0ciCrGPXiGIHDPB734BW6lRqzB4eQDmO7fHWGde34ONdEvO7kFKiWeI6oB3EZcPXsJjk4g-yTxhL2ABDVTZmTrWWwvwrkj47_zobAi5T-Tg_TOkO1BMvnxtz0owerw=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz1mSEkgbwQrHaHh37skJ4L3XdTTr0-QLKMMJaV4buXmWaS33N0OjaKzJCWAKSqFUWUyjccs_nXoD55snNX8sJuNPSyHTNo0-X6s42hEwRgbqXNBYbrg==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEt4jWr9WRsN-ujZWOXWkamUpMqIjT-DiVqsYXtnKLig8MBP_OyNqIAtrtDQo7LyZVdg-7CQDf-_myNo9BpvBSOCfe4EY46kKQYIDsQxCYNNTwCgLIAFZ18pQvBo9uwDlRb19X9v8h6v-Vh5B9al7Vo2oxQ95n_YLzqDqFyx7k9PtC_16zXN4fbHfK2Mn944_m8Fmvnkkaddoq2jYj5W2GMRA==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLkf3Xp7De8KoWcUFA2qqgRgOk6GGrYwpH1qTPx-87kqHt2E8Fy4qqbFPUrhr6bmA_BQ1a7e3KAxHS_oo23t944iERGugA39UCbvxg2pjICx3BHnHMfXY6kIVR397Wxr72CZZwUZFB4ao317gfWnGxvXCB4pNNrrwQUQOFcha-qpTyRJ7J)


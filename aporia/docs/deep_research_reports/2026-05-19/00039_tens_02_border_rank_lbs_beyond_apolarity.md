# TENS-02: Border rank LBs beyond apolarity

**Pythia queue id:** 39
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdveXdNYXR2ek9xWEtfdU1QLU11cXFBSRIXb3l3TWF0dnpPcVhLX3VNUC1NdXFxQUk
**Elapsed:** 245s
**Completed at:** 2026-05-19T09:30:01.791489+00:00

---

# Advanced Lower-Bound Techniques for the Border Rank of Tensors: Post-2023 Developments Beyond Border Apolarity

### Key Points
*   **The Cactus Barrier is Broken:** Research suggests that the longstanding "cactus barrier"—which limited traditional flattenings because they inadvertently vanish on larger cactus varieties rather than just secant varieties—has been mathematically circumvented. The 2026 introduction of *Kronecker-Koszul flattenings* and *tangency flattenings* provides explicit determinantal equations that vanish on secant varieties but not on cactus varieties.
*   **Adversarial Degeneration Games:** The Landsberg-Michałek extensions (2025) have fundamentally advanced the border substitution method. By framing tensor degeneration as an adversarial game involving Koszul flattenings, researchers can now explicitly construct tensors that surpass previously theoretical asymptotic lower bounds.
*   **Representation Theory Intersections:** The application of Young flattenings to $GL(V)$-invariant tensors has reached new heights. Recent works (Wu 2024, Gondi 2025) successfully leverage pure resolutions (Ford-Levinson-Sam) and Kostant's theorem to extract strict lower bounds from complex Schur functors.
*   **Boolean Satisfiability for Exact Bounds:** Computer-assisted proofs are becoming vital for specific finite-field tensors. SAT solvers, constrained by algebraic symmetries (cyclic, transpose, involute-sandwich), have effectively ruled out rank-21 decompositions for the $3 \times 3$ matrix multiplication tensor over $\mathbb{Z}/2\mathbb{Z}$.
*   **Wild Tensors and 111-Algebras:** Algebraic characterizations of minimal border rank tensors have evolved to utilize "111-algebras," extending Friedland’s normal form to classify "wild" minimal border rank tensors that previously evaded systematic categorization.

### The Complexity of Tensor Border Rank
The rank of a tensor, unlike that of a matrix, is notoriously difficult to compute—in fact, it is NP-hard [cite: 1, 2]. Adding to this complexity is the phenomenon of tensor degeneration, where a sequence of tensors of a certain rank can converge to a limit tensor of strictly higher rank. This limit-based approximation is captured by the concept of *border rank*, geometrically representing the smallest secant variety of the Segre variety that contains the tensor. Understanding border rank is crucial, as it directly dictates the asymptotic complexity of fast matrix multiplication algorithms. 

### Why Standard Methods Fail
For decades, mathematicians relied on "flattenings"—reshaping a tensor into a matrix and measuring its rank—to establish lower bounds. However, most classical flattenings hit a wall known as the "cactus barrier." Because border rank approximations can involve complex, infinitely close points (schemes), classical polynomial equations fail to distinguish between true secant varieties and larger "cactus varieties." Furthermore, computational methods easily succumb to the curse of dimensionality.

### The New Vanguard of Techniques
Since 2023, the mathematical and computational landscape has shifted dramatically. While the Buczyńska-Buczyński border apolarity method previously dominated the search for lower bounds, new algebraic-geometric obstructions have emerged. These include non-linear Kronecker-Koszul flattenings that evade the cactus barrier, aggressive SAT-solver exhaustive searches for small finite fields, and deep structural mappings using Lie group representation theory. This report synthesizes these cutting-edge methodologies, offering an exhaustive overview of the state-of-the-art in algebraic complexity theory.

---

## 1. Introduction: The Geometry and Complexity of Border Rank

In multilinear algebra and algebraic complexity theory, the decomposition of tensors into sums of rank-1 tensors (pure tensors) is a fundamental problem. For complex vector spaces \(A\), \(B\), and \(C\), a tensor \(T \in A \otimes B \otimes C\) is pure (or rank-1) if it can be written as \(a \otimes b \otimes c\). The **tensor rank** \(R(T)\) is the minimum integer \(r\) such that \(T\) can be expressed as a linear combination of \(r\) rank-1 tensors [cite: 3, 4]. Unlike matrices, where the set of matrices of rank at most \(r\) is Zariski-closed, the set of tensors of rank at most \(r\) in dimensions higher than two is not closed in the Euclidean or Zariski topologies [cite: 2, 5]. 

This topological openness gives rise to the concept of **border rank**, denoted \(\underline{R}(T)\). The border rank is the smallest \(r\) such that \(T\) can be approximated arbitrarily well by tensors of rank \(r\); geometrically, it is the smallest \(r\) such that \(T\) lies in the Zariski closure of the set of tensors of rank at most \(r\) [cite: 5, 6]. In the language of algebraic geometry, this closure is the \(r\)-th secant variety, \(\sigma_r(\text{Seg}(\mathbb{P}A \times \mathbb{P}B \times \mathbb{P}C))\), of the Segre variety [cite: 4, 7].

Border rank is not merely a geometric curiosity; it is the cornerstone of algebraic algorithms, particularly the asymptotic complexity of matrix multiplication, denoted by the exponent \(\omega\) [cite: 8, 9]. The matrix multiplication tensor \(M_{\langle n \rangle} \in \mathbb{C}^{n^2} \otimes \mathbb{C}^{n^2} \otimes \mathbb{C}^{n^2}\) governs the multiplication of two \(n \times n\) matrices [cite: 10, 11]. Bini's foundational work demonstrated that exact fast algorithms can be derived from approximate (border) decompositions [cite: 2, 12]. Consequently, lower-bounding the border rank of \(M_{\langle n \rangle}\) and related tensors provides critical barriers for the ultimate theoretical limit of matrix multiplication efficiency [cite: 9, 12].

Until recently, the gold standard for bounding border rank was the method of **flattenings**—specifically Koszul flattenings and Young flattenings—which unfold tensors into matrices and extract rank constraints [cite: 3, 5, 7]. Another major theoretical leap was the **border apolarity** method developed by Buczyńska and Buczyński (2019/2021) [cite: 13, 14]. Border apolarity connects border rank to multigraded Hilbert schemes and the Varieties of Sums of Powers (VSP), exploiting the symmetry groups of tensors to construct auxiliary multi-graded ideals that must exist if a decomposition exists [cite: 14, 15].

However, by 2023, both standard flattenings and border apolarity began to face profound structural limitations. Flattenings were hindered by the "cactus barrier," while border apolarity became computationally and theoretically intractable for higher-dimension "wild" tensors [cite: 7, 13]. The years 2023 through early 2026 have witnessed an explosion of novel techniques designed to bypass these limitations: Kronecker-Koszul tangency flattenings, adversarial border substitution frameworks (Landsberg-Michałek), deep representation-theoretic analyses of \(GL(V)\)-invariant tensors, 111-algebra normal forms, and machine-checked Boolean SAT bounds [cite: 4, 7, 16, 17, 18]. This report provides an exhaustive, mathematically rigorous examination of these post-2023 developments.

---

## 2. Breaking the Cactus Barrier: Kronecker-Koszul and Tangency Flattenings

One of the most persistent and formidable obstacles in the study of border rank lower bounds is the **cactus barrier**. To understand this barrier, one must delve into the scheme-theoretic nature of secant varieties.

### 2.1 The Geometric Nature of the Cactus Barrier

The \(r\)-th secant variety \(\sigma_r(X)\) of a variety \(X\) (in our case, the Segre variety \(X = \text{Seg}(\mathbb{P}A \times \mathbb{P}B \times \mathbb{P}C)\)) is defined as the Zariski closure of the union of linear spaces spanned by \(r\) generic points on \(X\) [cite: 7]. When computing lower bounds, researchers seek polynomial equations that vanish on \(\sigma_r(X)\) but not on the target tensor \(T\). 

However, limits of \(r\) points on a variety can degenerate into complicated non-reduced schemes of length \(r\) supported on \(X\). The closure of the linear spans of all such length-\(r\) schemes forms the **\(r\)-th cactus variety**, denoted \(\kappa_r(X)\) [cite: 7]. Geometrically, \(\sigma_r(X) \subseteq \kappa_r(X)\). 

A mathematically devastating realization in algebraic complexity theory was that all classical equation-producing methods based on taking minors of flattenings (including Koszul and Young flattenings) actually vanish on the larger cactus variety \(\kappa_r(X)\) [cite: 7, 13]. Because the cactus variety \(\kappa_r(X)\) fills the ambient space much faster than the secant variety as \(r\) grows (often linearly in the dimension \(n\)), classical flattening methods cannot possibly provide lower bounds beyond the point where \(\kappa_r(X)\) encompasses the entire space [cite: 7, 13]. This limitation is known as the cactus barrier.

### 2.2 Kronecker-Koszul Flattenings

In a groundbreaking 2026 preprint, researchers introduced **Kronecker-Koszul flattenings**, a non-linear generalization of classical Koszul flattenings that successfully circumvents the cactus barrier [cite: 7, 19, 20]. 

The construction operates by synthesizing the Kronecker power of a tensor with homological mapping techniques. Let \(T \in A \otimes B \otimes C\). The Kronecker power \(T^{\otimes k}\) resides in \((A^{\otimes k}) \otimes (B^{\otimes k}) \otimes (C^{\otimes k})\) [cite: 7, 12]. While rank and border rank are submultiplicative under Kronecker products (\(\underline{R}(T \otimes T') \le \underline{R}(T)\underline{R}(T')\)) [cite: 12], analyzing the Kronecker power allows the deployment of Schur functors and exterior algebraic mappings in a highly amplified state.

A Kronecker-Koszul tensor is formulated by initially taking a tensor power of \(T\), introducing non-linearity with respect to the original tensor's entries, and subsequently applying a Koszul flattening [cite: 7, 20]. By passing through a higher-dimensional tensor space and applying exterior product maps \(\bigwedge^p A\), researchers constructed a flattening matrix whose minors provide equations for secant varieties [cite: 7]. If \(T\) has border rank at most \(q\), the rank of its Kronecker-Koszul flattening is bounded by:
\[ \text{Rank}(\mathcal{F}_{KK}(T)) \le \mathcal{F}(q) \cdot \prod_{i=1}^r \prod_{j=1}^{s_i} \binom{d_i - |\lambda_{i,j}|}{d_{i,j}'} \]
The vanishing of the appropriately sized minors establishes a strict border rank criterion [cite: 7].

### 2.3 Tangency Flattenings

The most spectacular application of the Kronecker-Koszul framework is the derivation of **tangency flattenings**. Tangency flattenings are specific quadratic Kronecker-Koszul flattenings that depend non-linearly (quadratically) on the target tensor [cite: 7, 20].

Crucially, tangency flattenings yield the very first explicit polynomial equations that vanish on the secant variety \(\sigma_r(\text{Seg}(X))\) but *do not* vanish on the cactus variety \(\kappa_r(X)\) [cite: 7, 19]. This provides a direct, explicit separation between the secant and cactus varieties and allows for bounding border rank beyond the cactus barrier.

These polynomials exhibit highly structured, simple determinantal expressions, making them computationally and theoretically tractable [cite: 7, 19]. As an immediate corollary of this framework, the authors provided a novel, entirely computer-free, and elementary algebraic proof that the border rank of the \(2 \times 2\) matrix multiplication tensor \(M_{\langle 2 \rangle}\) is exactly 7 [cite: 7, 19, 20]. Previously, establishing \(\underline{R}(M_{\langle 2 \rangle}) = 7\) required either exhaustive geometric searches or intricate applications of border apolarity [cite: 12, 14]. The tangency flattening definitively proves that nonlinear tensor mappings can extract border rank information that linear flattenings structurally blur.

---

## 3. The Landsberg-Michałek Extension: Adversarial Degeneration and Border Substitution

Joseph M. Landsberg and Mateusz Michałek have been at the forefront of matrix multiplication complexity for years, having previously established the benchmark \(2n^2 - \log_2(n) - 1\) lower bound for the border rank of \(M_{\langle n \rangle}\) using Koszul flattenings and the border substitution method [cite: 10, 21]. In 2025 (published in *Theory of Computing*), they introduced a highly advanced extension of these methods to break long-standing asymptotic barriers [cite: 16].

### 3.1 The "Hay in a Haystack" Problem

A persistent meta-issue in algebraic complexity is Howard Karloff’s "hay in a haystack" problem: proving the existence of an object with generic properties is easy, but explicitly constructing one is exceedingly difficult [cite: 1, 16]. For generic tensors \(T \in (\mathbb{F}^d)^{\otimes 3}\), the border rank grows quadratically with \(d\) [cite: 1]. However, finding *explicit* sequences of tensors (where the \(d\)-th tensor can be computed in polynomial time in \(d\)) with border rank significantly above \(3d\) remained an unsolved problem [cite: 1, 16]. Until 2025, it was entirely unknown how to construct sequences of explicit zero-one tensors with border rank above the \(3d\) threshold [cite: 1].

Landsberg and Michałek targeted this exact gap, aiming to prove super-linear border rank lower bounds by combining combinatorics, normal forms, and geometric degenerations [cite: 16]. 

### 3.2 The Adversarial Degeneration Game

The core of the Landsberg-Michałek 2025 framework is the refinement of the **border substitution method** treated as an adversarial game [cite: 16]. 

The border substitution method traditionally involves substituting a projection or degeneration into a tensor to monitor how its rank drops, thereby reverse-engineering a lower bound on the original tensor [cite: 11, 22]. Landsberg and Michałek formalized this by analyzing families of "tight" tensors—tensors where the symmetry group acting on a complete variety has fixed points, allowing researchers to evaluate border rank over a finite number of filtrations [cite: 16].

In their setup, the mathematician seeks to establish a high border rank lower bound for an explicit tensor \(T\). The "adversary" attempts to prevent this by dynamically zeroing out basis vectors of the underlying vector space to lower the border rank of the resulting degenerated tensor as drastically as possible [cite: 16]. 

To counter the adversary, the authors developed a multi-stage degeneration strategy:
1.  **Initial Degeneration**: The target tensor \(T\) is degenerated to a tighter structure.
2.  **Adversarial Modeling**: The adversary's possible zeroing strategies are mapped and rigorously categorized into three distinct topological/combinatorial types [cite: 16].
3.  **Secondary Degeneration and Koszul Trap**: Regardless of which strategy the adversary employs, the mathematician applies a *further* specifically tailored degeneration [cite: 16]. This secondary degeneration forces the tensor into a form where Koszul flattenings inherently possess maximal rank, rendering the lower bound estimate completely transparent [cite: 16].

### 3.3 Explicit Explicit Asymptotic Bounds

Through this adversarial framework, Landsberg and Michałek successfully defined explicit assignments of tensor entries (e.g., using prime numbers or periodic integer sequences, which fulfill the polynomial-time explicitness criterion) [cite: 16]. 

They utilized Koszul flattening matrices that, while fundamentally constrained from being full rank, were manipulated via the secondary degeneration to guarantee a strict minor non-vanishing. This led to explicit lower bounds such as \(\underline{R}(T) \ge 2.02d\), and specific theorems proving \(\underline{R}(T) \ge (2+\epsilon)d\) for explicit tensor constructions [cite: 16]. This breakthrough shatters the historical \(\mathcal{O}(d)\) explicit sequence barriers and represents a masterclass in combining representation theory with combinatorial game theory.

---

## 4. Young Flattenings and $GL(V)$-Invariant Tensors

While classical Koszul flattenings have been deeply explored, their broader generalization—**Young flattenings**—has received intense, targeted attention since Derek Wu’s 2024 work, heavily expanded upon by Suhas Gondi in 2025 [cite: 3, 18, 23].

### 4.1 Schur Functors and Matrices of Constant Rank

Young flattenings seek to bound the border rank by converting a tensor into a map between highly complex Schur modules [cite: 3, 24]. For a complex vector space \(V\), a partition \(\lambda\) dictates a Schur functor \(\mathbb{S}_\lambda V\). The tensors of interest are \(GL(V)\)-invariant tensors residing in spaces like \(U \otimes \mathbb{S}_\lambda V \otimes \mathbb{S}_\mu V\), where \(U\) is another \(GL(V)\)-module [cite: 18, 23]. 

These tensors naturally correspond to spaces of matrices of constant rank. Proving border rank bounds for these families is critical for algebraic statistics and structural geometry, yet previously, non-trivial bounds were only known for highly unbalanced matrix multiplication tensors [cite: 23]. Wu (2024) achieved the first explicit use of Young flattenings *beyond* Koszul flattenings to obtain border rank lower bounds for tensors that are not \(1_A\)-generic [cite: 23].

### 4.2 Resolving Wu's Conjecture via Pure Resolutions

A central challenge in Young flattenings is maximizing the rank of the flattened matrix while minimizing the ambient theoretical rank parameter \(r\). The lower bound takes the form \(\underline{R}(T_{\lambda, \mu}) \ge \lceil \text{rk}(T'_{\lambda, \mu}) / r \rceil\), where \(r\) is the rank of a non-zero matrix in the image of \(V \to \text{Hom}(\mathbb{S}_\lambda V, \mathbb{S}_\mu V)\) [cite: 3]. 

Wu observed that if the partition \(\mu\) is obtained from \(\lambda\) by adding a box to any row except the first or \(n\)-th row, the parameter \(r\) is not of maximal rank, thus optimizing the denominator [cite: 3]. However, to compute the numerator, Wu conjectured that the Young flattening map is an exact isomorphism for all pairs of partitions \(\lambda\) and \(\mu\) [cite: 3].

In August 2025, Suhas Gondi definitively resolved Wu's conjecture [cite: 3, 18]. Gondi accomplished this by analyzing the ranks of maps between Schur functors using deep results in commutative algebra and representation theory [cite: 25]. Specifically, he deployed **pure free resolutions** constructed by Ford-Levinson-Sam [cite: 3, 18]. These homological constructs allow for exact dimension counting of the syzygies of the modules defining the flattenings, proving that the Young flattening indeed acts as an isomorphism, thereby maximizing \(\text{rk}(T'_{\lambda, \mu})\) [cite: 3].

### 4.3 Generalizations and Kempf Collapsing

Gondi did not stop at \(U = V\). Using a powerful theorem by Kostant regarding Lie algebra cohomology, Gondi generalized the Young flattening lower bounds to families of \(GL(V)\)-invariant tensors where the space \(U\) is the symmetric square \(\text{Sym}^2 V\) or the exterior square \(\bigwedge^2 V\) [cite: 3, 18]. 

Furthermore, Gondi applied **Kempf collapsing**—a geometric technique used to study the singularities of Schubert varieties and rational resolutions—to extend the catalog of \(GL(V)\)-invariant tensors that are strictly *not* of minimal border rank [cite: 3, 18]. A concise tensor in \(A \otimes B \otimes C\) has minimal border rank if its border rank exactly equals the maximum of the dimensions of the vector spaces [cite: 5]. Proving non-minimality is an inherently lower-bound problem. Kempf collapsing provides a birational morphism that allows researchers to pull back the tensor degeneration problem to a vector bundle over a flag variety, calculating cohomological obstructions to minimal border rank decompositions [cite: 3, 15, 18].

---

## 5. Algorithmic Bounds: Machine-Assisted Proofs and SAT Solvers

As theoretical bounds edge closer to their limits, researchers have increasingly turned to computational complexity theory and machine-assisted verification. The exact rank of the \(3 \times 3\) matrix multiplication tensor \(M_{\langle 3 \rangle}\) is a famous open problem, known only to lie between 19 and 23 [cite: 17]. To break this stalemate, recent methodologies translate the tensor rank problem over finite fields into Boolean Satisfiability (SAT) problems.

### 5.1 Boolean SAT Encoding of Tensor Decomposition

In 2024, Jason Yang published an exhaustive analysis utilizing SAT solvers to rule out low-rank decompositions of \(M_{\langle 3 \rangle}\) over the field \(\mathbb{Z}/2\mathbb{Z}\) [cite: 17, 26]. The rationale for studying \(\mathbb{Z}/2\mathbb{Z}\) is that decompositions over finite fields can sometimes be lifted, and computational search spaces are drastically smaller than over \(\mathbb{Q}\) or \(\mathbb{C}\). A decomposition of rank \(R \le 21\) is the threshold required to yield an asymptotically faster algorithm than Strassen's \(\mathcal{O}(N^{2.808})\) [cite: 17, 26].

The SAT formulation defines a tensor \(M\) as a sum \(\sum_{r=0}^{R-1} A^{(r)} \otimes B^{(r)} \otimes C^{(r)}\) [cite: 26]. Over \(\mathbb{Z}_2\), the entries of the matrices \(A^{(r)}, B^{(r)}, C^{(r)}\) are strict boolean variables. The constraint that the sum of these outer products must exactly equal the matrix multiplication tensor \(M_{\langle 3 \rangle}\) generates a massive system of XOR equations (equivalent to standard boolean logic constraints) [cite: 26].

### 5.2 Symmetries and Search Space Reduction

To make the problem tractable for state-of-the-art solvers like **Z3**, Yang artificially forced the decompositions to satisfy strict symmetry constraints [cite: 17, 26]. Symmetries mathematically restrict the degrees of freedom of the variables, collapsing the SAT search space. Yang investigated several symmetry classes:

*   **Cyclic Symmetry (\(\Theta_{\text{id}}\))**: Invariance under cyclic permutations of the factors \((A, B, C) \to (B, C, A)\) alongside transformation conjugations \((FAF^{-1}, FBF^{-1}, FCF^{-1})\) [cite: 17].
*   **Cyclic + Transpose Symmetry (\(\Theta_{\phi}\))**: Further invariance under transposition mappings \((X, Y, Z) \to (Y^T, Z^T, X^T)\) [cite: 17].
*   **Cyclic + Involute-Sandwich Symmetry (\(\Theta_{\Delta}\))**: Constraints tying matrix equivalence through an involutory transformation \(D \to FDF^{-1}\) [cite: 17].

Using these symmetry restrictions, the Z3 SAT solver definitively ruled out all \(\langle \Delta, T \rangle\) or \(\langle \Delta, \phi_{F,F,F} \rangle\)-symmetric decompositions of \(M_{\langle 3 \rangle}\) with rank \(\le 21\) [cite: 26]. Furthermore, all \(\langle \Delta \rangle\)-symmetric decompositions with rank \(\le 15\) were eliminated [cite: 26]. 

### 5.3 Depth-First Search for Border Rank

Building upon exact rank algorithms, late 2024 saw the introduction of Depth-First Search (DFS) frameworks augmented by SAT solvers specifically targeted at computing **border rank** over finite fields [cite: 27]. Because border rank involves limits—represented algebraically as polynomials in a parameter \(\varepsilon\) [cite: 28]—the boolean encoding is significantly more complex. The algorithms establish variable coefficients representing polynomials in \(\varepsilon\) and truncate at a fixed degree, translating the limit criterion into a modular algebraic SAT problem [cite: 27, 28]. These computational techniques, avoiding randomization for exhaustive correctness [cite: 17], now serve as an ultimate verification tool against theoretical constructs, proving that certain fast algorithms simply do not exist under assumed symmetric conditions [cite: 17].

---

## 6. Wild Tensors and the 111-Algebra

For small dimension bounds, researchers aim to completely classify tensors of minimal border rank. However, classification runs into the barrier of "wild" tensors—tensors whose smoothable rank is strictly larger than their border rank, making their geometry highly erratic [cite: 29]. 

### 6.1 The 111-Algebra Construct

In 2023, Joachim Jelisiejew, Joseph M. Landsberg, and Arpan Pal pioneered a new algebraic invariant called the **111-algebra** to conquer the classification of concise minimal border rank tensors [cite: 4, 30, 31]. The 111-algebra derives from the "111-equations" defined earlier by Buczyńska and Buczyński in their border apolarity theory [cite: 4, 30]. 

For a concise tensor \(T \in A \otimes B \otimes C\), the 111-algebra \(\mathcal{A}^{111}_T\) is mathematically defined as a commutative, unital subalgebra of \(\text{End}(A) \times \text{End}(B) \times \text{End}(C)\) [cite: 4, 12]. This algebra consists of "compatible triples" that govern the structural symmetries and apolar ideals associated with \(T\) [cite: 12]. By transitioning from looking at polynomial equations (apolarity) to a structured algebra of endomorphisms, researchers unlock deeper invariant properties of the tensor.

### 6.2 Strengthening Friedland's Normal Form

A classic tool in tensor decomposition is Friedland's normal form, which classifies tensors under sequence degenerations. However, it was historically insufficient for "1-degenerate" tensors satisfying Strassen's commutativity equations [cite: 4, 30, 31]. Strassen's equations (the A-, B-, and C-Strassen equations) are determinantal and commutativity constraints that minimal border rank tensors must satisfy [cite: 4].

Jelisiejew, Landsberg, and Pal exploited the 111-algebra to massively strengthen Friedland’s normal form for 1-degenerate tensors [cite: 30, 31]. Because the 111-algebra forces commutativity constraints onto the endomorphism spaces of \(A, B,\) and \(C\), the analysis maps directly into the geometry of the **variety of commuting matrices** [cite: 4, 30]. Utilizing deep results by Jelisiejew and Šivic concerning the components and singularities of Quot schemes and commuting matrices [cite: 12, 30], the authors achieved a total characterization of wild minimal border rank tensors [cite: 30, 31].

This resulted in the complete, exact classification of all concise minimal border rank \(1_*\)-generic tensors in \(\mathbb{C}^m \otimes \mathbb{C}^m \otimes \mathbb{C}^m\) for \(m = 5\) and \(m=6\) [cite: 4, 30]. For algebraic complexity, proving that an algebra's structure tensor is "wild" natively implies distinct rigid lower bounds on its border rank geometry, establishing that it cannot smoothly deform into standard diagonal (rank-1 sum) forms [cite: 29, 30].

---

## 7. Universal Tensors, Asymptotic Rank, and Specht Modules

While studying the border rank of a fixed tensor \(T\) is common, the true Holy Grail of complexity theory is understanding the **asymptotic rank**. The asymptotic rank of \(T\) dictates the optimal exponent achievable by taking massive Kronecker powers \(T^{\otimes k}\) [cite: 1, 32]. 

### 7.1 Strassen's Asymptotic Rank Conjecture

Strassen's asymptotic rank conjecture states that for broad families of tensors, specifically tight tensors, the worst-case exponent is the least possible value [cite: 1, 32]. Proving or disproving this conjecture has monumental implications; for example, if the asymptotic rank exponent \(\sigma(3) = 1\), it implies \(\omega = 2\) (matrix multiplication can be done in quadratic time) and simultaneously refutes the Strong Exponential Time Hypothesis (via the Set Cover Conjecture) [cite: 1, 32]. 

### 7.2 Invariant Specht Tensors

A major 2025 contribution to ITCS connected the extended Strassen's conjecture to the representation theory of the symmetric group \(S_p\) [cite: 1, 32]. The researchers demonstrated that the asymptotic rank exponent \(\sigma(d)\) is entirely governed by the ranks of very specific tensors: invariants in the tensor product of three **Specht modules**, \( (\mathbb{S}_\alpha \otimes \mathbb{S}_\beta \otimes \mathbb{S}_\gamma)^{S_p} \), where \(\alpha, \beta, \gamma\) are partitions of \(p\) with at most \(d\) parts [cite: 1, 32].

This theorem effectively reduces the search for asymptotic border rank lower bounds from an infinite continuum of arbitrary tensors to a discrete, highly structured sequence of "Universal Tensors" defined by Specht invariants [cite: 1, 32]. Because these Specht tensors possess 0-1 entries in their natural coordinates, they are perfectly suited for explicit computation and sequence generation [cite: 1]. 

However, evaluating these bounds requires verifying the non-vanishing of polynomials on the \(k\)-th secant variety of \(\mathbb{P}^{d-1} \times \mathbb{P}^{d-1} \times \mathbb{P}^{d-1}\) [cite: 1]. The authors noted the explosive growth in the minimal degree of such equations: while the 6th secant variety of \((\mathbb{P}^3)^{\times 3}\) has equations of degree 19, the 18th secant variety of \((\mathbb{P}^6)^{\times 3}\) requires equations of at least degree 187,000 [cite: 1]. This computationally validates why classical methods failed and why the Kronecker-Koszul tangency flattenings (which keep degrees remarkably low and determinantal) are indispensable to the future of the field [cite: 1, 7].

---

## 8. Summary of Breakthroughs: 2023–2026

To contextualize the rapid paradigm shift in border rank lower bound techniques, the following table summarizes the chronological and methodological leaps discussed in this report:

| Year | Innovation / Methodology | Principal Researchers | Core Geometric/Algebraic Contribution | Outcome for Border Rank Lower Bounds |
| :--- | :--- | :--- | :--- | :--- |
| **2023** | **111-Algebras & Wild Tensors** | Jelisiejew, Landsberg, Pal [cite: 4, 31] | Extended Buczyńska-Buczyński 111-equations into a commutative unital subalgebra of endomorphisms. Connected tensor geometry to the variety of commuting matrices. | Complete classification of concise minimal border rank \(1_*\)-generic tensors for \(m=5, 6\). Characterization of wild tensors. |
| **2024** | **SAT Solver Constraints** | Yang [cite: 17, 26]; Depth-First Search groups [cite: 27] | Encoded matrix multiplication tensor components over \(\mathbb{Z}/2\mathbb{Z}\) into massive boolean XOR formulations. Applied cyclic and involute-sandwich symmetries to collapse search space. | Mathematically ruled out rank-21 decompositions of the \(3\times3\) matrix multiplication tensor under specific symmetries. |
| **2024–2025** | **Young Flattenings & Schur Functors** | Wu (2024), Gondi (2025) [cite: 3, 18, 23] | Applied Ford-Levinson-Sam pure resolutions and Kostant's Theorem to resolve isomorphism conjectures for Young flattenings. Utilized Kempf collapsing for non-minimal cases. | Delivered explicit, strict lower bounds for \(GL(V)\)-invariant tensors in \(U \otimes \mathbb{S}_\lambda V \otimes \mathbb{S}_\mu V\), extending bounds beyond unbalanced matrix multiplication. |
| **2025** | **Adversarial Border Substitution** | Landsberg, Michałek [cite: 16] | Created a game-theoretic framework mapping topological zeroing strategies of an adversary onto tight tensors, resolving with secondary degenerations forcing Koszul trap states. | Produced explicit tensor sequences with border rank strictly greater than \(2.02d\), breaking historical linearity barriers for explicitly constructible tensors. |
| **2026** | **Kronecker-Koszul & Tangency Flattenings** | Uncredited Preprint (arXiv:2602.12762) [cite: 7, 19, 20] | Generalized Koszul flattenings to non-linear Kronecker domains. Produced Tangency flattenings yielding low-degree determinantal expressions. | **Broke the Cactus Barrier.** First explicit equations vanishing on secant varieties but *not* cactus varieties. Elementary proof that \(\underline{R}(M_{\langle 2 \rangle}) = 7\). |

---

## 9. Conclusion

The pursuit of lower bounds for the border rank of tensors represents one of the most profound intersection points of theoretical computer science, algebraic geometry, and representation theory. Following the widespread adoption and subsequent maturation of the Buczyńska-Buczyński border apolarity method, the mathematical community faced theoretical ceilings defined by the cactus barrier, "wild" tensor singularities, and the "hay in a haystack" explicitness problem.

From 2023 to early 2026, every single one of these ceilings has been aggressively challenged or entirely shattered. The introduction of non-linear **Kronecker-Koszul tangency flattenings** stands as a monumental geometric triumph, finally decoupling secant varieties from the parasitic growth of cactus varieties [cite: 7, 19, 20]. Simultaneously, the **Landsberg-Michałek adversarial degeneration framework** has proven that careful topological maneuvering can extract explicit asymptotic bounds far beyond classical substitution limits [cite: 16]. 

On the algebraic and computational fronts, **Suhas Gondi's** application of pure homological resolutions to **Young flattenings** has tamed the complexity of \(GL(V)\)-invariant tensors [cite: 3, 18], while the **111-algebra** developed by Jelisiejew, Landsberg, and Pal has finally categorized the chaotic landscape of wild minimal border rank tensors [cite: 30, 31]. Finally, the brute-force mathematical certainty provided by **symmetry-constrained SAT solvers** [cite: 17, 26] and the translation of the asymptotic rank conjecture into the language of **Specht modules** [cite: 1, 32] guarantee that future bounds will be both computationally verified and representationally optimal. 

Together, these techniques provide a robust, multifaceted toolkit that is rapidly closing the gap between the theoretical limits of tensor complexity and the algorithmic reality of fast matrix multiplication.

**Sources:**
1. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-CiyU3TS1muoZGIg5O9T260vLaTfFARZGanYzEKCvzDd0-WF5l0ssl7Zbw8OfyuczwPiyu-Nb1WFDMiEsUL9TSrUuYvR1Sn2ZOCRRdryucu6slKFbv09upH7o6uMmuzT-tGgRtTOXsgu7nn3WJPfgJIEL-GGcDvG6aubQprtkU7tXZirAKYDc8jcwetj-_fgFN709286wWXKpO3FMTO1UvYb0)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsRXk89nc6BrMo0kX2SYiPiFjBPwxT0Iv18Sh3CdbZVl_hZE6BODRwTMCkuVn-XmbXwyORTqEv0NoKDy1KxUdYCzS-3CNcuY2mrAq50BIBpb_Z_izl3J0zD4pfQRQFmiJw3-vaGg3w1oXsR5np)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3nPatAg2Yqdf19DwiCPuzQN8fBh3DtSgGqDaMifIwawrd8cUpjCJxShGSSNCvAOjcnEktT5bEJeMZ8DqzVx7ki-Ta1RBq4ndkM-qFNozd8_xFr3TtxpLCfA==)
4. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQYrwfQ6tO-AofDD6xVRute6l0GyAI5HP1g_apBOR9N-3MeBdXomKh45vFVgvbyiwdboKhsH9onMQdDrc3Ifr0xlG4szxOHgSpWqVT8tK5ocD_s9dkg1DdS2c9QQ3s1rzUnNrI_d1_BJ2KXn3l)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF87_bqUMDEnFydHhUc-0UQ5bqWk_lTG0Ixa3xcphECaPM_5qGMnfZz2YoZFGh3nGSmxk0mVWckZGk_9v8ziao7dnd4j1iIilBmfMqjJCIIzHb_DkDxuw==)
6. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJFd_pXMe2FjhOrfYGKBI68LNQUAOvmeU5MQLBy-fD9Hqkm-hhbrhNrMnfSZMWQ4X1CAoIOUUqIbKCEEg0I8_FP78zjgZdFcCNfgF6wkuleH-VKOADR59-2bDHCJ_tHwpDNi6A7iBZtTvXjGcfmA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHabDvenTsYEn4XfW2EekhmRJKATwOR38DjDzMy5yLKzwSt1ZLTQ2Z8tmSEufP1DwLa1D-Xc0vTzJyfgZuEu99UNgP1kDGTMDCGfqAMMee81T1I-2A-S8iFgQ==)
8. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED1TnHFIxnLfn_oCeHSyr_StXggtcKDPYxyrA4FL_z2hQCTIy95vPJ3fpty3CSPKH_8VL9_tg_opoFacGTg1p8GQajtk3qKnDs6ncyUfkkU1MpzlbQ7IiAdBIErJpC-oQQ)
9. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZVbFllUQq_OEWXQNa694QyuUsaTk5atqVr8qJhEHZFwKCCC45WC-duxvk64XfaSbanRnG-6kf-jrzwLydlLpd0c4tr5KzRwcW8map-1J8N_97WLU2YSvkaMx5jCnotMFh)
10. [aalto.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2EvHAfhiH9vA61oHQPO35fJpTSJiSa_E6Zt-NVt-d5KXdP0GvX7b0tH7B2VwBZmZjaDtGGBM3aDQy_Gp7dUOZ6A8QywlpnK8qnRvdx6rHwUTvxgNmPVA-cogJ79bcs6cM91411MzZ6OuvVmX3uPk2s_eYZ3F3FTP5eIM9SZYm6sfmct1VQtqLVZA2YxkN1cBAajDU4JRj5GefNso1oYl79iY=)
11. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaLresQjrpnbgHiuL50riDjHz-ypDFN--xyfh4YIR16Gb7SnDd_i8rNu6e05FOjkZxFSWBhWSz9jvjjzl3rJGuRKlvItf2sgaXRrKcJH7848euBfzGQ25u8yW9sglB6vIb7dc=)
12. [units.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHydlLslcsXuTcqq_u5jz86wMdNdPjDL4PfpEIxkYN1JJLSw44kgbYVRe9HfopDAbZJkR2n0Ir3RSH-NLFU4uxKjMZSZuzq4E8D9wMhToyrBE_hIT9bGDIy6SUR6PvgJbAAHR-C7-VSh5x-dG42e0sdp_ZWmg5VS1fgsVrRocXRkEIFJVcC_L9ScEAnXAAj)
13. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuvVoo6oS2M-2wutT4qGHYZFqYDu5kCIHkbRea1j3EsZCHtBUQeMnCBe5Dz7tTrHm3w-DaSoz8PdoG9Yq0Q5c7kITT84yA-j5iVwRh39t8a_vcCXNQ7WtUKAZ7ICVO0BF_LyNq8QoQ5PAAM_9-umBk6WDR_EnqGXd32QQr4IYPrJux1ECC5xSYLR1d_XjBuVUAuiNS-CA8juBfaL1GWFg5HuhEX4KAsvcUiyFPo28-CT_CQeaKbAPYCqCTFPTvfK17oYEynA_Bz87dynUOuGK66InSM8OaiQWUwbc=)
14. [deepai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBTnjQrfJXZYcwI5xmpULoR-6V6rX4QxNTMF0H09Mt8Zfdk8WmIyE67FF9DNz1MAzzkUBYMgEGk3edQKFOkGyIXf8HarfIeoaSlZ3XZGLEmRuly2AJMCd6rxIi0xme05_m57gSQtTLplvJlkvbfieJS407gsnzlboiALDVFmrOwmMb5EdyZpWC_EjOl7NhtCNInVSDzrVg)
15. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgEbGX1tjNq_IY36VuEBpPOUnXAx_SDrrojtsF4VyHbPchfMGDqfp8bfWYAQACFVPEEeMt-ukDeVrKKR2bjPl6nTghLVFlNTfu9DX4FIqnM4CD9wOcE_ct3VYQhucC7CfzqnTAIERJhEymERJA_d_PSCvAEEc=)
16. [theoryofcomputing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8faTzk73Z6t-80c-l5MDOjLoCCPueFSxGbaYj5bdPzrgvZLaRlbiXi5B-FngtFR-C40m-PivNY58o2BjzgbGX4L5ry5XMJr4weyUfu9QkdLLtnVCPu7Y5iYmQcgCOQWxLwTBKcGIXgvDFMHCp8kSNng==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpJixStpzAD1c_LwG6XjzSNIewxMBhv9L2dpm25BwC4Lwmaj-gjADR5_UB0aen6Mo0oyuxANWPjzFDpMoUSeKx8914g62rceyIYnBuB_Ub0rCne_9Waw8J0w==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6gR7zvvi7qVWx20LQDcQbQyFQO9Y19FI2bWLPPbKdLuRihe8fMUSGZYHkmJ4F63epiCG6Vjmoe5fzE9HqOjKcg39lvLxKVeLHtjt67BQhfOhIf84BnQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbegaIzGCaKk7JpX63Sju6sRdfrJksWoQkvVhPvuPJqVcgCCSD-OCBKB5EnXwz9tRtMsourkozWLB3wzF8fHbb3CWALTEUCrgcLi_V_8H4RcjprEyYOw==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM3KjsPXFNZldkynTg_wcOYctjvnl9WUxrm8pt6Biwmlihrw2ICaKOqQvKolMUqZNIAqB3OpC1GWS5XdjKzluz8QdlcsPqxZorKdw0idAJ5w5r_7QKHw==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-ecci6hDsoXdZCkBBpUaNQoRM2DE3G1pO96STjreafO2w4KJa8pDkKISAmA_AxU-m9ynST7ECWh2JNFIpwPlhmWSzeOXSuNkent1vQq9HVxdIlWidGw==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOorciAj2QE-6kKYt4cUc4fQA28WvzWrXwS5X1rvVRGMhE569tBz6oCUz95zYwkc9gMpFTmaob_oP-hKxiwFSVsq7ga4MPwcNYlxOHzZQL_JtQBNLM6w==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK-0rf2dyGrmcvELU-A-_nn4ayOrJAMPaiENIBSKZhw3DZ_CHHkcHZiIorS3vs_WVsXbzHF_9Z_rnE3lXU26CWpFiIACNK4w9cAsHHqWpzBhYaqerxyA==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzGQN9-CE-7-WFeZn0RFlrfmei_0MejwQQv_rgG-T7cWuCG-e3wxEQzUdvFv8Xi1beKXNu96w10ElqUESxylRAMvyS2tAQDSUX9q8Ya6jBnbk2OhWEOEWKivxTsne8102qSP7bowlt2xQBRvhJzz38xjzoVv-t_j-ZtFOquLWI8KCM_4L2ujgDPc1UwaYF3SFCtNg4RYAaAxhfFfgGL1SpcpKNPUU=)
25. [nd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8tF4b5tpZCcecWLedYx7PpIELnhUZUaK_Gdxaz_queSe0sJHHPKZaMQZvBj85EIPnf6ax4u94a-RhTvQoIpm0aXH0gphDc59iBV8KXCjsZdGk7khgxHw9VuRYSUDbII8sGlFnbrKYCTqkL2UGdzDAS4Ys3nEdWRBxRQoWNk2hAIQr4nXSpgQBVNwxZvkARzpU12Niya1UB3zvFEIuma-M9RL5ywCxfRvt5Mh6XH3UAW06wfhNT9k=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIEgEcuVswhG-njkBI24InouS9SQG3N8s66GicAzIg8-QvTRmmC8ukN_8IN9pY7rbqnOe6HAtz9e-xezGYvfT1EPijYJucCqJLD7FXE8woigVrBEOXLA==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE80vYoMjueau4lLHbvxfCmiaAg7likp6-TOgfFopbXWC5LhXEaKcMDa8L7sotFwdlQWwsxEYT8JPdGH2UjfrlqBfCrnS6oGiWR4f3wqM2pu-22bjS4OcKjG2l4zU_2-r8u3UBvwC9FKI7C3UtizEpyxwwosWfzQhoEYos_Pj8suyw8mlhfrkwQufklXPS2oXUdsXALoaPMKdfXlYagNOniC7vCTvk_QhhsgtNg2Eo=)
28. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyY6V5NTTxuMKX1vf4VS7yuFzWSiGNUszmS1vc1QKNQMYn5EErWHQ26HaSOQ7upiDGJvXS-HfrM6mx5IERZRNVCYWEpDvm72LKMMvNEe154MNqGDcCZUxmqeZ_07Auqw-92yo=)
29. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg3SGRUKr3VcIz_9hmFHv_2eihBEtXvT5g3LR1DkptSyDzSP30endzy3wiset5IC5AxF33MW-6Yf9-GBT-OBtKs43FEFvLOLhIxzfPkwTVxYb3QGtDSjoZYpvLKbAfWVr3bs6A87g=)
30. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkZMjfJugKkUmxUWQ8coojcPzKaIXusLKl-9u4n1KQeQSYwuhmi6uSWaewRA-4Y5zgs1G30fC68f9-YOWXqwt42SrqvKHVLU4vnkY2u0AkIOENodbs9WfhfJVzbo4CbxZdvGGP9Po=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGN_V5pbhqKYHWjov7EyOYF67q_4l7Vqij5E7bKqemCfXGMKSxvcYNUEz3upFOjU-JQSVg8kYMpe8u9jhUgci5mHKSbwEHnPCDUMmvREYGqmYxTaJUOA==)
32. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZ1zV7-7ZdL9BWy-TuAHDBqTFNCe9MoMUwi8sQ5gE0ARcd7WM4Qyc7sSj2-HhoFxEy4aKrl04pGBY_nvMcBLqieA8lVzfee4Xj2lKmxURHLdoQP5mo)


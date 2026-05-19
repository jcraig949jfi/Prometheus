# TENS-01: Asymptotic spectrum 2025-2026 state

**Pythia queue id:** 38
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdxaXNNYXRUdkwtQzBfdU1QeklYbHlBcxIXcWlzTWF0VHZMLUMwX3VNUHpJWGx5QXM
**Elapsed:** 246s
**Completed at:** 2026-05-19T09:25:53.710283+00:00

---

# Latest Progress on the Strassen-Christandl-Vrana-Zuiddam Asymptotic Spectrum Theory of Tensors (2024-2026)

Key points:
*   **Equivalence of Functionals:** Research suggests that Strassen's upper support functionals, proposed in 1991, exactly coincide with the quantum functionals developed by Christandl, Vrana, and Zuiddam. This monumental resolution relies on advanced geodesically convex optimization.
*   **Universal Edge Spectra:** It has been shown that support functionals on the edges of Strassen's triangle act as universal spectral points across arbitrary fields (including positive characteristic), deeply connecting matrix multiplication limits to Harder-Narasimhan filtrations from quiver representation theory.
*   **Polynomial Characterization:** The elusive asymptotic tensor rank is now known to be characterized by polynomials, proving that its sublevel sets are Zariski-closed. This establishes that asymptotic tensor rank is "computable from above" and takes values from a well-ordered, discrete set.
*   **Countability:** Structural results confirm that the sets of asymptotic ranks, subranks, and geometric ranks over the complex numbers are at most countably infinite.

### Introduction for the General Reader
The study of how quickly computers can multiply matrices—grids of numbers fundamental to virtually all fields of science and engineering—has puzzled mathematicians since Volker Strassen discovered a "fast" matrix multiplication algorithm in 1969. To understand the absolute mathematical limits of this computation, Strassen created a vast mathematical landscape in the late 1980s called the "asymptotic spectrum of tensors." By treating tensors (higher-dimensional grids of numbers) as abstract objects that can be added and multiplied, Strassen showed that their computational difficulty is governed by "spectral points"—hidden geometric and algebraic measurements.

For over thirty years, the exact nature of these spectral points remained largely mysterious. A massive breakthrough occurred around 2018-2023 when researchers Christandl, Vrana, and Zuiddam used concepts from quantum physics (like entanglement and quantum entropy) to discover the first new family of these spectral points, known as "quantum functionals." 

Since 2024, the field has experienced a profound explosion of results, heavily documented in recent arXiv preprints. Mathematicians have successfully bridged Strassen's original 1991 hypotheses with the quantum breakthroughs, proving that Strassen's proposed "support functionals" and the newer "quantum functionals" are actually the exact same thing. Furthermore, researchers have demonstrated that the geometric limits of these tensors are highly structured: they are governed by polynomials, their values cannot smoothly slide but must "snap" to discrete levels, and their complexities over any mathematical field can be calculated efficiently using representations of directed graphs. This report exhaustively details these 2024-2026 breakthroughs, outlining the proofs, the newly discovered spectral points, the structural topologies, and the remaining open problems.

---

## 1. Introduction and Theoretical Background

The study of the complexity of bilinear operations, most notably matrix multiplication, is a cornerstone of theoretical computer science and algebraic complexity theory [cite: 1, 2]. The exponent of matrix multiplication, denoted $\omega$, governs the asymptotic complexity of multiplying two $n \times n$ matrices. Despite decades of intense research, determining the precise value of $\omega$, which lies somewhere between $2 \le \omega \le 2.3728639\dots$, remains a fiercely open problem [cite: 1, 3]. 

In a series of foundational papers published between 1986 and 1991, Volker Strassen sought to understand the optimal algorithms for matrix multiplication by embedding the problem into a vastly more general framework: the semiring of tensors [cite: 4, 5]. He developed the magnificent theory of asymptotic spectra, formulating a generalized duality theorem that bridges the asymptotic "rank" of tensors with a topological space of real-valued homomorphisms known as the **asymptotic spectrum** [cite: 2, 4].

### 1.1 Tensors and the Asymptotic Restriction Problem
Let $V_1, V_2, V_3$ be finite-dimensional vector spaces over a field $\mathbb{F}$. A 3-tensor $T \in V_1 \otimes V_2 \otimes V_3$ can represent a bilinear map. For example, the matrix multiplication tensor $\langle l, m, n \rangle$ represents the multiplication of an $l \times m$ matrix by an $m \times n$ matrix [cite: 6]. 

The **tensor rank** $R(T)$ is the minimum integer $r$ such that $T$ can be expressed as the sum of $r$ elementary rank-1 tensors [cite: 3]. The asymptotic behavior of tensor rank under Kronecker powers, $T^{\otimes n}$, is captured by the **asymptotic rank**:
\[ \tilde{R}(T) = \lim_{n \to \infty} R(T^{\otimes n})^{1/n} \]
Similarly, the **asymptotic subrank** $\tilde{Q}(T)$ captures the maximum rate at which independent scalar multiplications can be extracted from large tensor powers of $T$ [cite: 3]. 

The fundamental relation $\lesssim$ (asymptotic restriction) dictates when one tensor can be asymptotically transformed into another via linear maps on its legs [cite: 7, 8]. Deciding if $S \lesssim T$ is the **asymptotic restriction problem** [cite: 3, 8].

### 1.2 Strassen's Spectral Theorem and Duality
Strassen defined the asymptotic spectrum of tensors, $\Delta(\mathbb{F}, k)$, as the set of all maps $\phi$ from the semiring of tensors to the non-negative real numbers satisfying four rigid axioms [cite: 3, 9]:
1.  **Monotonicity under restriction:** $\phi(T) \le \phi(S)$ whenever $T \lesssim S$.
2.  **Additivity under direct sum:** $\phi(T \oplus S) = \phi(T) + \phi(S)$.
3.  **Multiplicativity under tensor product:** $\phi(T \otimes S) = \phi(T)\phi(S)$.
4.  **Normalization:** $\phi(\langle 1 \rangle) = 1$, where $\langle 1 \rangle$ is the unit tensor.

Strassen's duality theorem provides a complete characterization of asymptotic restriction in terms of these spectral points. Specifically, $S \lesssim T$ if and only if for all spectral points $\phi \in \Delta$, we have $\phi(S) \le \phi(T)$ [cite: 3, 7]. Consequently, asymptotic rank and subrank are dualized as [cite: 3, 9]:
\[ \tilde{R}(T) = \max_{\phi \in \Delta} \phi(T), \quad \tilde{Q}(T) = \min_{\phi \in \Delta} \phi(T) \]
However, Strassen's proof of the existence of the asymptotic spectrum was non-constructive, relying on Zorn's lemma [cite: 2, 7]. Identifying explicit **universal spectral points**—homomorphisms defined on the semiring of *all* tensors—became a holy grail in algebraic complexity theory [cite: 7, 10].

### 1.3 The CVZ Quantum Functionals
The construction of non-trivial universal spectral points remained an open problem for more than thirty years. The only previously known spectral points over arbitrary fields were the three "flattening" or gauge points, which simply measure matrix rank along the three partitions of the tensor [cite: 3, 9]. 

In 2018 (published in JAMS 2023), Matthias Christandl, Péter Vrana, and Jeroen Zuiddam (CVZ) achieved a breakthrough by discovering the first family of non-trivial universal spectral points over the complex numbers $\mathbb{C}$, which they named **quantum functionals** [cite: 8, 10, 11]. 

Their construction connected the asymptotic spectrum of tensors to the quantum marginal problem and entanglement polytopes from quantum information theory [cite: 8, 10, 12]. By evaluating the Shannon/von Neumann quantum entropy optimized over specific momentum polytopes associated with the tensor's support, CVZ constructed a continuous family of spectral points parameterized by a probability simplex [cite: 7, 10]. This profound connection demonstrated that quantum information theory provides natural obstructions to exact asymptotic tensor transformations [cite: 8, 10].

Despite this monumental advance, severe questions remained: 
1.  Are the quantum functionals equivalent to the upper "support functionals" hypothesized by Strassen in 1991? 
2.  Do universal spectral points exist for fields of positive characteristic (where CVZ's analytic, characteristic-zero geometric invariant theory arguments fail)? 
3.  Is the asymptotic tensor rank computable?

Between 2024 and 2026, an avalanche of preprints on arXiv resolved these long-standing questions, completely reshaping the landscape of asymptotic spectrum theory [cite: 9, 13, 14, 15].

---

## 2. Equivalence of Support Functionals and Quantum Functionals (Sakabe-Doğan-Walter 2026)

In 1991, Volker Strassen published a seminal paper proposing the **upper support functionals**, denoted $\zeta^\theta$ (where $\theta$ ranges over a probability triangle $\Theta$), as candidate spectral points [cite: 9, 12]. Strassen was able to prove that these support functionals were spectral points for a strict subfamily called *oblique tensors*, but whether they were *universal* spectral points valid for the entire semiring of tensors was left as a major open problem [cite: 8, 13].

In a January 2026 preprint (arXiv:2601.21553), Keiya Sakabe, Mahmut Levent Doğan, and Michael Walter decisively answered this 35-year-old question in the affirmative [cite: 13, 16]. 

### 2.1 The Equivalence Theorem
Sakabe, Doğan, and Walter proved that Strassen's upper support functionals $\zeta^\theta$ are not only universal spectral points, but they are exactly identical to the quantum functionals $F^\theta$ discovered by Christandl, Vrana, and Zuiddam [cite: 9, 13].
\[ \zeta^\theta(T) = F^\theta(T) \quad \forall \text{ complex tensors } T, \forall \theta \in \Theta \]
Because the quantum functionals were already proven to be universal spectral points by CVZ, this equivalence instantly elevated Strassen's 1991 support functionals to universal spectral points [cite: 9, 13]. 

### 2.2 Methodology: Geodesically Convex Optimization and Hirai's Duality
The proof by Sakabe et al. relies on sophisticated tools from differential geometry and non-Euclidean convex optimization that were completely unavailable to Strassen in the 1990s [cite: 9, 13]. 

The upper support functional $\zeta^\theta(T)$ is defined by a two-step process: first minimizing over all choices of bases (which corresponds to an action of the general linear group), and then maximizing a weighted marginal entropy over the resulting support [cite: 9]. The Sakabe-Doğan-Walter proof establishes a general minimax formula for convex optimization on entanglement polytopes (and other moment polytopes) [cite: 13]. 

Crucially, the proof leverages a recent Fenchel-type duality theorem on Hadamard manifolds due to Hiroshi Hirai (2025) [cite: 13, 17]. A Hadamard manifold is a simply connected, complete Riemannian manifold with non-positive sectional curvature. The space of positive definite matrices (and correspondingly, the space of basis transformations for tensors) forms a Hadamard manifold [cite: 13, 18]. By formulating the basis optimization problem as the minimization of a geodesically convex function on a Hadamard manifold, Sakabe et al. applied Hirai's duality to swap the minimax optimization, perfectly aligning Strassen's algebraic-support definition with CVZ's entropy-optimization definition [cite: 9, 13, 18].

### 2.3 Alternative Characterizations of Asymptotic Slice Rank
By invoking the minimax theorem on entanglement polytopes, Sakabe, Doğan, and Walter also derived a novel and alternative characterization of the **asymptotic slice rank** [cite: 9, 13]. The slice rank of tensors has deep connections to additive combinatorics, famously providing the optimal bounds for the cap set problem [cite: 3, 8]. The new duality framework allows the asymptotic slice rank to be viewed equivalently through the lens of Strassen's support geometry and quantum entropy optimization, solidifying the interplay between additive combinatorics and the asymptotic spectrum [cite: 13].

---

## 3. The Edge of the Asymptotic Spectrum (Alman-Li-Pratt 2026)

While the Sakabe-Doğan-Walter result was a monumental leap, its reliance on differential geometry, Kempf-Ness theory, and properties unique to the complex numbers $\mathbb{C}$ meant that the theorem could not easily be generalized to other mathematical fields, particularly fields of positive characteristic (e.g., finite fields) [cite: 9, 19]. Before 2026, for fields of positive characteristic, the only explicit spectral points known were the three trivial flattening ranks corresponding to the three vertices of the simplex $\Theta$ [cite: 9, 19].

In an April 2026 preprint (arXiv:2604.01386), Josh Alman, Baitian Li, and Kevin Pratt provided a striking structural characterization of the "edge" of the asymptotic spectrum [cite: 9, 12]. 

### 3.1 Universality over Arbitrary Fields
Alman, Li, and Pratt focused their investigation on the support functionals $\zeta^\theta$ where $\theta$ lies strictly along the edges of the triangle $\Theta$ [cite: 9, 12]. Let $\kappa \in \{1, 2, 3\}$, and define the edge $\Theta(\kappa) = \{\theta \in \Theta : \theta_\kappa = 0\}$. 

The authors proved the following foundational theorem:
**Theorem (Alman-Li-Pratt 2026):** For *any field* $\mathbb{F}$ and any $\theta \in \Theta(\kappa)$, the upper support functional $\zeta^\theta$ is a universal spectral point for $\mathbb{F}$-tensors [cite: 9, 19].

This result established, for the very first time, the existence of a continuous family of non-trivial universal spectral points over arbitrary fields, breaking the barrier of positive characteristic [cite: 9, 12]. Because their methods are purely algebraic and combinatorial, they completely sidestep the analytic and geometric requirements of the CVZ and Sakabe-Doğan-Walter proofs [cite: 9, 19].

### 3.2 Uniqueness Characterized by Matrix Multiplication
Beyond proving that the edge support functionals are spectral points, Alman et al. proved a profound rigidity result. They showed that these edge functionals are *uniquely determined* as spectral points solely by their behavior on matrix multiplication tensors [cite: 9, 12]. 

Strassen had noted in 1988 that matrix multiplication tensors have limited universality—they do not span the full computational complexity of the tensor space [cite: 1]. Alman, Li, and Pratt formalized this by showing that along the edges of the spectrum, the matrix multiplication capacity dictates the exact value of the spectral point [cite: 9, 12]. This provides a direct path from the algorithmic complexity of matrix multiplication to the abstract topology of the asymptotic spectrum [cite: 9].

### 3.3 Harder-Narasimhan Filtrations and Algorithmic Invariant Theory
To achieve their proof, Alman, Li, and Pratt unveiled a deep connection between the edge support functionals and **Harder-Narasimhan filtrations** from quiver representation theory [cite: 9, 12]. 

When evaluating a tensor $T \in V_1 \otimes V_2 \otimes V_3$ along the edge where the third marginal is zeroed out, the tensor can be naturally viewed as a matrix space, or equivalently, as a representation of a Kronecker quiver [cite: 9, 19]. The minimization over basis choices inherent in Strassen's support functional definition translates algebraically to finding a sequence of "shrunk subspaces" that optimally compress the tensor [cite: 9].

By analyzing the semistability of these quiver representations, the authors proved that the optimal basis choice corresponds exactly to the Harder-Narasimhan filtration of the tensor [cite: 9, 12]. This connection has immediate and profound algorithmic consequences. By relying on recent breakthroughs in algorithmic invariant theory, Alman, Li, and Pratt proved that the edge support functionals can be computed in **deterministic polynomial time** [cite: 9, 12]. This is a rare instance in asymptotic complexity where an asymptotic, optimal rate parameter can be efficiently and exactly evaluated [cite: 9, 12].

### 3.4 New Criteria for Higher-Mode Tensors
While the spectral theory of 3-tensors (bilinear maps) has been the primary focus, the complexity of $d$-mode tensors for $d \ge 4$ is equally critical. Alman, Li, and Pratt provided a new algebraic criterion for abstractly characterizing asymptotic tensor ranks by spectral points for higher-mode tensors [cite: 9, 12]. 

They formally proved that for $d \ge 4$, the asymptotic spectrum of $d$-mode tensors must contain points strictly beyond the known quantum functionals [cite: 9]. In other words, the quantum functionals do not exhaust the asymptotic spectrum of higher-order tensors, leaving a vast, unexplored territory of new spectral points to be discovered [cite: 9, 12].

---

## 4. Structural Results: Polynomial Characterization and Discreteness

One of the most persistent meta-questions in Strassen's theory has been whether the asymptotic tensor rank is computable. Matrix rank is easily computed via Gaussian elimination, but tensor rank is NP-hard over finite fields and its complexity over $\mathbb{C}$ is tied to the algebraic geometry of secant varieties [cite: 20]. Asymptotic tensor rank, defined via a limit of Kronecker powers, is vastly more elusive.

In November 2024, a landmark paper titled "Asymptotic tensor rank is characterized by polynomials" (arXiv:2411.15789, accepted to STOC 2025) by Matthias Christandl, Koen Hoeberechts, Harold Nieuwboer, Péter Vrana, and Jeroen Zuiddam fundamentally altered our structural understanding of asymptotic rank [cite: 14, 20, 21, 22].

### 4.1 Computability from Above and Zariski-Closedness
Christandl et al. proved that asymptotic tensor rank is **"computable from above"** [cite: 14, 20, 21]. Specifically, they proved that for any real number $r$, there exists an efficient algorithm that determines whether the asymptotic tensor rank of a given tensor $T$ is at most $r$ [cite: 14, 20, 21].

The algorithm's structure is remarkably simple in theory: it consists of evaluating a finite list of polynomials on the tensor's coefficients [cite: 14, 20, 21]. If all polynomials in this specific finite basis evaluate to zero, the asymptotic rank is at most $r$ [cite: 14, 20].

Mathematically, this establishes that the sublevel sets of asymptotic rank—defined as $\{T \in V : \tilde{R}(T) \le r\}$—are **Zariski-closed** sets [cite: 14, 23]. This mirrors the behavior of classical matrix rank, where the sublevel sets are algebraic varieties defined by the vanishing of minors (determinants of submatrices) [cite: 14, 23]. While Christandl et al. rely on non-constructive invariant theory to prove the *existence* of these polynomials, the proof that the sublevel sets are Zariski-closed over infinite fields (like $\mathbb{C}$) resolves decades of speculation regarding the algebraic nature of asymptotic parameters [cite: 21, 23].

### 4.2 Discreteness from Above and Well-Ordered Sets
The algebraic nature of the asymptotic rank leads to shocking topological consequences. Christandl et al. proved that the set of values that asymptotic tensor rank can take across all tensors is a **well-ordered set** [cite: 21, 22, 23].

This implies the phenomenon of **"discreteness from above"** [cite: 21, 23]. Any non-increasing sequence of asymptotic ranks must eventually stabilize. There are no infinite strictly decreasing chains of asymptotic ranks [cite: 21, 23]. 

This has profound implications for the matrix multiplication exponent $\omega$, which is the base-2 logarithm of the asymptotic rank of the matrix multiplication tensor [cite: 1, 21, 23]. The theorem dictates that there is no sequence of exponents of bilinear maps that approximates $\omega$ arbitrarily closely from above without being eventually constant [cite: 21, 23]. In the authors' words, any algorithmic upper bound on the matrix multiplication exponent that is sufficiently close to the true value will inherently "snap" to the true value $\omega$ [cite: 21, 23].

Prior to this 2024 paper, such discreteness phenomena were only known for tensors over finite fields (where invariant sets are naturally discrete) or for parameters with heavily constrained geometry like asymptotic slice rank [cite: 21, 23, 24]. Christandl et al. extended this polynomial characterization and well-ordering property not just to asymptotic rank, but to **all functions in Strassen's asymptotic spectrum of tensors**, proving that the entire spectrum enforces geometric rigidity [cite: 21, 22, 23].

### 4.3 Countability of Asymptotic Subranks (Blatter-Draisma-Rupniewski 2024)
Further contributing to the structural topology of asymptotic parameters, Andreas Blatter, Jan Draisma, and Filip Rupniewski published a paper (arXiv:2212.12219, published in *Linear and Multilinear Algebra* in 2024) titled "Countably many asymptotic tensor ranks" [cite: 24, 25, 26].

Motivated by observations of "gaps" in the asymptotic subranks of complex tensors, they investigated the cardinality of the image of asymptotic parameters [cite: 15, 24]. The authors proved that for all tensor invariants that are algebraic (invariant under field automorphisms of $\mathbb{C}$), the asymptotic counterpart is also an algebraic invariant [cite: 15, 24]. 

Consequently, they established **Corollary 2.2**: The set of asymptotic ranks, the set of asymptotic subranks, and the set of asymptotic geometric ranks of complex $d$-tensors is at most countably infinite [cite: 15, 24]. This means that despite the continuous nature of the complex numbers and the infinite limits defining asymptotic rank, the allowable limits form a heavily constrained, countable grid of numbers rather than a continuous spectrum [cite: 15, 24].

---

## 5. Universal Sequences of Tensors and the Asymptotic Rank Conjecture

A recurring theme in the asymptotic spectrum theory is the **Asymptotic Rank Conjecture**, boldly proposed by Strassen in 1994 [cite: 14, 20]. The conjecture posits that the asymptotic tensor rank of any concise tensor is simply equal to its largest dimension [cite: 14, 20]. If true, asymptotic tensor rank would be as easy to compute as standard matrix rank [cite: 14, 20].

Crucially, proving Strassen's asymptotic rank conjecture would immediately imply that $\omega = 2$, settling the matrix multiplication exponent problem, and would refute the Strong Exponential Time Hypothesis and the Set Cover Conjecture from fine-grained complexity theory [cite: 1, 19, 27]. Recent works have highlighted that the Asymptotic Rank Conjecture and the Set Cover Conjecture cannot both be true simultaneously (Björklund and Kaski, STOC 2024; Pratt, SODA 2024) [cite: 1, 22, 27].

### 5.1 Explicit Universal Tensors for Worst-Case Exponents
Because the matrix multiplication tensor MM$_2$ has limited universality (its exponent does not upper bound the exponent of all tensors in the space), researchers have sought to construct tensors that *do* capture the absolute worst-case complexity [cite: 1].

In a paper accepted to ITCS 2025, Björklund, Curticapean, Husfeldt, Kaski, and Pratt successfully constructed an explicit universal sequence of zero-one-valued tensors $\mathcal{U}_d$ that exactly characterizes the worst-case tensor exponent [cite: 1, 27]. 
\[ \sigma(\mathcal{U}_d) = \sigma(d) = \sup_{T \in \mathbb{F}^d \otimes \mathbb{F}^d \otimes \mathbb{F}^d} \sigma(T) \]
where $\sigma(T)$ captures the base of the exponential growth rate of the tensor rank under Kronecker powers [cite: 1]. 

By explicitly constructing this sequence, the authors provide a tangible primal object to test Strassen's conjecture. If one can demonstrate that the sequence $\mathcal{U}_d$ satisfies the asymptotic rank bounds, the asymptotic rank conjecture would be proven [cite: 1, 27]. Furthermore, they provide a "support-localized" universal sequence $\mathcal{U}_\Delta$ for any specific support pattern $\Delta$, bridging the gap between the polynomial vanishing conditions (as explored by Christandl et al.) and upper bounds on the exponent $\sigma(d)$ [cite: 27].

The authors highlight two distinct methods for analyzing these universal tensors: computational exhaustive methods using linear algebra and representation theory (which are limited by the exponential explosion of dimensions), and non-constructive algebraic geometry [cite: 27].

---

## 6. Applications Across Mathematics and Computer Science

The generality of Strassen's asymptotic spectrum theory has proven to be incredibly versatile. A massive 2023 survey preprint (to appear in the *Bulletin of the AMS* in 2026) by Avi Wigderson and Jeroen Zuiddam, "Asymptotic Spectra: Theory, Applications, and Extensions," extensively outlines how this algebraic framework intersects with disparate fields [cite: 2, 4, 5, 28]. 

### 6.1 Additive Combinatorics: The Cap Set Problem
The cap set problem asks for the maximum size of a subset of $\mathbb{F}_3^n$ that contains no three elements in a line. The breakthrough solution by Ellenberg and Gijswijt in 2017 relied on the polynomial method. However, the asymptotic spectrum provides a natural, coordinate-free approach. The cap set problem can be reduced to computing the asymptotic spectrum of the "reduced polynomial multiplication tensor" [cite: 3, 8]. The spectral points (specifically the asymptotic slice rank, heavily tied to the quantum functionals [cite: 8, 13]) naturally act as obstructions to asymptotic transformations, cleanly yielding the optimal upper bounds for the cap set problem [cite: 3, 8].

### 6.2 Quantum Information Theory
As explicitly detailed by the construction of quantum functionals, the asymptotic restriction problem of tensors is mathematically equivalent to the **asymptotic LOCC (Local Operations and Classical Communication) transformation problem** for multipartite quantum states [cite: 3, 10]. 

Determining whether a supply of identical quantum states can be asymptotically transformed into another state without generating entanglement involves precisely the same operations (Kronecker powers, direct sums, matrix restrictions) as tensor complexity [cite: 3, 10]. The upper support functionals (now proven equal to quantum functionals [cite: 13]) represent fundamental, physical entropy barriers that prohibit certain quantum states from being distilled into others [cite: 3, 10].

### 6.3 Graph Theory and Shannon Capacity
Jeroen Zuiddam extended the asymptotic spectrum framework to graphs, showing that the asymptotic spectrum of graphs accurately captures the **Shannon capacity** from information theory [cite: 9, 29]. The Shannon capacity is the maximum rate at which information can be transmitted over a noisy channel with zero probability of error [cite: 9, 29]. Similar to tensor rank, Shannon capacity is notoriously difficult to compute. By applying the generalized Strassen Positivstellensatz [cite: 4, 5], the asymptotic spectrum of graphs provides a unified way to establish upper bounds on Shannon capacity using algebraic invariants [cite: 9, 29].

### 6.4 Computational Complexity
As noted by Alman, Li, and Pratt, the asymptotic spectrum logic parallels complexity theory [cite: 9]. In Strassen's theory, the asymptotic tensor rank is the maximum of spectral points over the tensor; in Boolean complexity, the formula complexity $\rho(f)$ is the maximum of $\mu(f)$ over all formal complexity measures [cite: 9]. The discreteness from above proven by Christandl et al. (arXiv:2411.15789) gives rigorous structure to the mathematical limit of matrix multiplication, showing that algorithms cannot infinitely yield microscopic fractional improvements without eventually hitting a discrete floor [cite: 21, 23].

---

## 7. Open Problems and Future Directions

The explosion of results between 2024 and 2026 has resolved multiple decades-old conjectures, including the validity of Strassen's upper support functionals [cite: 13] and the computability/closedness of asymptotic tensor rank [cite: 14, 20]. However, these discoveries have birthed a new generation of profound open problems.

### 7.1 Discreteness from Below
Christandl, Hoeberechts, Nieuwboer, Vrana, and Zuiddam proved that asymptotic tensor rank is discrete from above (well-ordered) [cite: 14, 21]. However, they explicitly leave open whether the asymptotic rank is **discrete from below** [cite: 20, 21, 23]. 

If Strassen's Asymptotic Rank Conjecture is true (that asymptotic rank equals the largest dimension), then discreteness from below is trivially implied because the values would be integers [cite: 20, 21, 23]. Proving discreteness from below independently could be a major stepping stone toward proving the conjecture.

### 7.2 Explicit Construction of the Defining Polynomials
While Christandl et al. proved that the sublevel sets of asymptotic rank are Zariski-closed and thus defined by the simultaneous vanishing of a finite list of polynomials, their proof via invariant theory is non-constructive [cite: 14, 20, 21]. 

A major open problem is to **explicitly construct these polynomials** [cite: 21, 23]. Finding explicitly calculable polynomial invariants that act as a strict bound for asymptotic tensor rank would drastically accelerate the computational search for better matrix multiplication algorithms and yield new algebraic formulas for bounds [cite: 21, 23].

### 7.3 Spectral Points for Higher-Mode Tensors
The overwhelming majority of discoveries (support functionals, quantum functionals, edge limits) have been exhaustively classified for 3-tensors (which correspond to bilinear maps and tripartite quantum states) [cite: 3, 9, 12].

Alman, Li, and Pratt proved that for $d$-mode tensors where $d \ge 4$, the currently known quantum functionals are fundamentally insufficient to cover the asymptotic spectrum [cite: 9, 12]. 
**Open Problem:** Explicitly construct the missing spectral points for $d$-mode tensors ($d \ge 4$) [cite: 9, 12]. Resolving this will be necessary to extend the algebraic complexity toolkit to multilinear operations beyond matrices.

### 7.4 The Extended Asymptotic Rank Conjecture
Conner, Gesmundo, Landsberg, Ventura, and Wang (2023), alongside Bürgisser, Clausen, and Shokrollahi, have proposed an even stronger version of Strassen's conjecture. The **Extended Asymptotic Rank Conjecture** posits that the least possible exponent is shared by *all* concise tensors in $\mathbb{F}^d \otimes \mathbb{F}^d \otimes \mathbb{F}^d$ [cite: 27]. Utilizing the explicit universal sequences generated by Björklund et al. (ITCS 2025) to test this extended conjecture computationally remains a primary frontier in modern complexity theory [cite: 1, 27].

---

## 8. Conclusion

The timeline from 2024 to 2026 will likely be remembered as a golden age for the asymptotic spectrum theory of tensors. Building upon the monumental 2018 discovery of quantum functionals by Christandl, Vrana, and Zuiddam, modern researchers have rapidly disassembled the remaining structural mysteries surrounding Strassen's 1991 conjectures.

The unification of Strassen's upper support functionals with the quantum functionals by Sakabe, Doğan, and Walter [cite: 13], combined with the algebraic universality of the edge spectrum proven by Alman, Li, and Pratt [cite: 9, 12], has provided mathematicians with a rich, computable, and rigorous geometry of spectral points across arbitrary fields. Simultaneously, the work of Christandl et al. [cite: 14, 21] establishing the Zariski-closedness and well-ordering of asymptotic rank, complemented by the countability proofs of Blatter, Draisma, and Rupniewski [cite: 15, 24], confirms that the infinite limits of tensor complexity are governed by strict, discrete algebraic rules.

As explicit sequences of universal tensors are now available to test the limits of algorithmic complexity [cite: 1], the field inches ever closer to the ultimate resolution of the Asymptotic Rank Conjecture and the exact determination of the matrix multiplication exponent $\omega$. Theoretical computer science, quantum information theory, and algebraic geometry find themselves more deeply intertwined than ever through the language of the asymptotic spectrum.

**Sources:**
1. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQghwVtYobe2vRtmqT9sPlYexqfvZyEeq7Q7hdAtwOD2LRfeMxzei3kC1HMIGZCELXpVd9-yGsGCN0n4HGStVyqaig9B7Z6hGfG8L2XhXKhwKuHj_SvXDQEuZpEe1b4Rw1O5nCLyLJgDNUzhgLwa9DKxdb4JmjqmKcYiiLyg==)
2. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrCFWv7yi_2JkiuORHdungquGcTreDCOqbUndbVjir5InfGWNxXFofgJd0A7rqbByceKQJN7DLc0Lh8ewDcOLmCleKrQOQ5Q6BcnH1K6nJR0RJWY854f8F-NhEKjER_uQt6T78nRWGWKz69MwZIiE8VcseAcmgD82tdwE6MahqDIJSXNE=)
3. [qutech.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzQtG9yOcxWq3740pj6ZwDuSIx2AQYGdZdRRjVzLcROmXoSt5gqWaaOhEKO-pShoIKiHnZdcw9UjxPSRcIOA2OFqPwxzoNnrTUEja_oRhtpRgBPh3LGtbGfWmEk0F6PzhPHsRNWfwKMvEhJjwwIB9cqF5KpZrPWBCD2i1bUJ50B6vOBwNC75miPw==)
4. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1q8zvSACYtHbzWv-1fvWvXqO7B0t1jvz9Quc10FZSIk-fgZ22t3az9ia0w79X8iFhbOruzl0MLY4oKJQHLy6745bqBL4eFOZu4--zjQr0L6eWsT_2NjqT7bf1St5DuoK-p6dNQGJ1-C9pvReDtQ5hEb7RuUGk4lZX2-KGLRgO09A=)
5. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbFtDSGSpmUKFZloNrBPyIOtv-FVxlKdR6GqamibipOEQ5uTL1EABxc5hT7wFUlWUDkM_7otPPBBD_JWCq3rlJg41EXAmOKbqG-V80R6A_9IUTjerVUhnCHHGwtw6zwSTcFL1ZGDw4J60KLi-_jOY=)
6. [ku.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHtf5d0zunq6M2P3HqrA-s-MCG1t2NALE6zUPuiriZF-HHre4c2E_1aJcqq9i1kUu_m16T7t4m9W9XMGUoWyqK6c3YNO5lrhO3wIUyzVAdFb9EznBjruz_cfZd9IxXfaMqKnTMA5LCmrPjfbEF4_FGg89_lOZJV6_SpVEXp6AdmQ8=)
7. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBXLik_x5Ycvynoc9yT6Te54hm0NQBGDXkQ42FozzvbmEUcw3ubvssXhQN4eub2XQHNvoq3c573Z54UP0Y-QcR_AWHhaPQ2KTCr3NV_ik6o_-4EAYvqC29qoPbcsFmzmWXVqAgZ6dgIEwetdzveRi0Xx75xuhYCAJiHlO5v-bq26rs1_v8AtyS1xovBmoSnMCW_sB0)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFxfTTRkyqyTDUjckTFYk8tWR7Ne41Oqb4xeYxZ7M1whOOFkkfSwa07ZrAlJzRDuZTmpIac9oQbGUjB0aJAG851HUaB3yNGrXA3IPWnwnCswaAiC0RuQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcirWnAHieKkBSZzr9hdy-zzM9EKj7riIYXMF04w9MY-oaCaZmBedAYFvu19yE0X0XkyVL_mdZ5ASecEo8fu2s6X7fniXdM3F-GOfEJCTcQ8fh4oe7j6uz8w==)
10. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf3N-juF3Bc4gsECpkt0DIiPuJMUYjZm-EjYhh8dZEf1oSWlyoaNP1MViffDTrEPFcaEKRl26e8n_sZT-4U3bfoBjciJO9eRXLXTbTg0tQkGGinlNGUyGZ4DhisbjYpgyg0J8vYI303ImDciGT0dsC_VjNp6ql1KxeSc6AXeJLKbX0RtqqlkQXbaPQ9FDLrfAH2R-alnjA-NW4WOTxzvS0yLCrr3cWb35l5jtQw5cq641DUvNKBOCfGv2AMh_xlj9ZoFnkgOdOHjWT)
11. [google.lu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHb-RDujFfEXqVk8vWBp70JeAlDCbUmoT-gVvi5Jo35YbTkZdaIvz8_4Ox8MiA8MdooKVfnyFog4zPon2qpUdxvPQPQpPjRyKSpEETRI6g5FgT8gatkU2wm-H3jGUlxki0qhAmiuZaLrI-YhM-3vJiSDQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdG0ba1wMexw0bd5V00-pYLEn6d5bVrLpEevkELiUs48zZ5kflbM-nsSvG-3h8x-CL1b5aEbxdL56g9BIhmPavYsLjJQ5SZ4nOpnOKIRBiDf-jZtq42A==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFY1EoTQ7oVAZc32mVZbLmlsFaqcet4YmK9DuT_YhCr1AQ-bm15YZCQhsf6Jr-Ym2xHXHgXAcM55f3OAqX_w6aeXD9sb6OILkzCKMMUBJPX8o6jQYPASg==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNlREhGLKE8o697_PhC8sYVBlNiZPr7Y63zXHfRrerTf9k9AJ6ciHhdlk_KFU7Likbu8kAoOQn643-VcE0_EphwLGa3sycedrgP6CaLwWUMgzQo-_uCw==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERg7gpIxl8vVXB0F_wba_7Vl3pDHt3y7bevdiSd9P8C-fjIFSTtG9aaApYI-n6XPXvQcdCEAKn6D2b-NCEQZ5PoAmjcebQDbMcyn_CgUZ64I25G86Snw==)
16. [michaelwalter.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGtyLTS8aWgRaWrzn6ZtnRudH48J6EBbjXzca9hHQzgsHXxXCwVPKoh8TSSVRu_SV_h2Rr6dgZRf-5F3U1bIuMZV32OWjmqKhszhDhxF-d-WB4bnGoKJ5Em4-U28k=)
17. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN_XCPNhDrk6DebRktjhj1ABvWIStP5IccAhhDG7ismeyBXBChGSkTWe4l7bvmESU1VmFspT8DgnZCSXRd8thxtntsJnJ4hCKsHyf_p66CS4XlgcbrY88Bo07LHcFpY63gsVdnPLZgDAfd9Mp6MJEf0hd-xd0AU5aaKWj-jDcazAHVJmQkj8qGN0k9Br8ztP_t)
18. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcF9trX2lbzF1pl5JGHNPBxMYWOjq3Ihm6UWnSwG4ZXs66d6mTATBTsfLOC57kAZi4vuKlt2LC9ubAD-pBMsMHkBbC3234g8IeeKdpPCdCkxT4)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwo-enVRyiyAgPJIagdd9YzgPO2JCXCOJpTH5XMdOwDpaGRuX6My1rP_KM2LqBKa1Up7hFVoXSl8mwD_SwJfJZLC_N-9dOgTmqrRO5hiXEEVvQntLndQ==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdtQCpYC2lamPzg_98AH4Z-Nfc_4RWbHndrsQIo_uAMKgI96kuDk4IAI1khMcKiWQ1hK99y2Qw4wJc7zZbeWhhgMO8URT3S4QMs4ruu4ulwnzgpnw0ig==)
21. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG1F-cDD2OOFEn812UFNRYF5NQU_UgRCWs9IIIIVzAAGo5rKQ67ajDD_s3PPYYiD1kGJhX2OiIKoxkW8gUpm2_5fBf9GeCHHe8MRqmqxi6qJg=)
22. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFe8Pv9xCHOktA_xW5V_V1WU5WaSzrbPFfTQMxhUR26xJimxG0ihQdZAqboYdB5lXMouzhiMqMUfW73Ipr2o341EFlj8gocoTnFn1znOWq5xOf17yeL3hplldcQ1WE2F9KiQUhIfM-1ieu-5TGZZMx)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvLttvfHnFT1rfxNT9SaGMXuvxqZRkRF0hZMRClcYhhjw1_G9a5ZEuMEzGOKcTy7Qx-SchaY_KWuRfqFIRFsn37ZAlwsNGm1MX0u_bN66voPKBYr6NKyERBgpboqjf6jfmoIBsGbbFTN_FGzKvvEG4iOHYOrPGbFci9dk7li7AWpDT37S43G5AVRshoUmmmM8lXLxHFjkQ5_XQW_TPYmQ=)
24. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENSU-kwijeB7QTjW8E5juwEpnL8-jGdvZQclkDOc-CHAV7dFDDnxOBe8lsTrBIkkRY68UDzp5bdDmPVvkyWE2Rl_6fVYn-d37tTnJeav0FU_kw0YHDSQhpeelBK_fc0NZylzTokguM9EHDqyblOF3CXYAX43VdYA==)
25. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnfRD3QWWpp7KRSp_TOUO9RrKG5QRxqfrkdTQaUk7oZfkbaKOJEQ25DwHcVLnyhvxKHwBd3xPuCBioJgt2QFSP6F4i6EhQewTUVxsYmXgn6Fxf3IbMzlGdfawCVCKiTifzo8EHmxNnzXCxoEOBDim-DVIdsOKjHw==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBXI8XS8VahynosSF2bdKWpNXBbhXCs4u9QqscsC3iNEKnuc3RGqhgCX_6JYC0ybzRUkf4E8lLx4aIKEbhmhSSEX6iBBS75jtmbJuWgrwHkpaWIMY0YQ==)
27. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbCrRVxK4ImGKSb_yiwvMyR6heokoOI7PW4YnW_KFTm4Pw6eCewl2upIkgF6zpH4U__9xjuTvFroRJDAeiZuPrGQEh-GMvYlCd-PlzBcu5UbQtu6ULMb7eSz7G1ICVK8ubr7idp7t7sfbTfGmwBs6-nRtFuEdTpDNHIsI-QqCuI_eERpfZJxkHfYqG1ODyyMZX_jyfN7JHdQfNqCncqpWuU2vk)
28. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxqXDPiFH1TaWdyhIN51zF2qQPnPO8VFWaGOUVmZii3QG01bLExs9tSljfShiEBRxAlEUa-v6iHWsVwVUOdTkIiXmUL5RHJsOViaonbgMa4Fxal5_HZHbAs3ZoOfE7iKQE8wQiOFT5eNeFyFnqmS0K7ykyLv0Af8R-KKmUAX0i7SpwlOA=)
29. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBdgFc_UymQZckrLWdjhN9Lrevg0QsOypx06V2Iud_35PzKKDKfN4LNazJbeNENiJQ6I0v_XK_6eYn5n_QFgj24D4aIBIrlgCUjVzJmf7vj9nGmzEFVckty3E=)


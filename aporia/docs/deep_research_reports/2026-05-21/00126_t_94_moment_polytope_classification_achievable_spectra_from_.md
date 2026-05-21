# T#94 Moment polytope classification (achievable spectra from tensor actions)

**Pythia queue id:** 126
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdqU2NQYXFHNkVKUGtqTWNQX1pfTDhRMBIXalNjUGFxRzZFSlBrak1jUF9aX0w4UTA
**Elapsed:** 440s
**Completed at:** 2026-05-21T15:48:22.566819+00:00

---

# Moment Polytope Classification: Achievable Spectra from Tensor Actions (T#94)

This comprehensive academic report explores the highly interdisciplinary domain of moment polytope classification—frequently codified in specialized literature under technical tags such as T#94—focusing on the achievable spectra arising from multilinear tensor actions. 

**Key Points**
* **Moment polytopes** are mathematically profound geometric structures that capture and classify the set of possible local physical states (quantum marginals) that can emerge from a complex, multipartite global system.
* They provide a definitive solution to the **quantum marginal problem**, classifying exactly which joint spectra are physically attainable for a given pure state under local transformations.
* In the realms of theoretical computer science and algebraic complexity, these polytopes serve as geometric invariants, acting as obstructions that help distinguish the computational difficulty of algorithmic tasks, most notably matrix multiplication, from other tensor operations.
* Recent computational and algorithmic breakthroughs have enabled the explicit construction and characterization of these polytopes for complex, high-dimensional tensor formats (such as $3 \times 3 \times 3$ and $4 \times 4 \times 4$), fundamentally shifting the boundaries of what is computationally verifiable.
* Deciding whether a specific spectrum belongs to a moment polytope is a rigorously defined computational problem, proven to reside in both NP and coNP, which distinguishes it from related NP-hard problems in representation theory.

## 1. Introduction and Interdisciplinary Motivation

The study of multidimensional arrays, or tensors, resides at the heart of modern mathematics, theoretical computer science, and quantum physics [cite: 1, 2]. While two-dimensional arrays (matrices) are thoroughly understood through classical linear algebra and their rank, tensors of order three and higher possess an intricate geometric and algebraic structure that renders traditional analytical methods insufficient [cite: 1]. Fundamental problems concerning tensors are inextricably linked to long-standing questions in computational complexity, such as determining the exponent of matrix multiplication via asymptotic rank, resolving Strassen's asymptotic rank conjecture, and understanding multipartite quantum entanglement [cite: 1].

Because the classification of tensors under local basis changes yields highly complex, non-linear orbit closures, researchers have increasingly adopted a coarser, asymptotic viewpoint. This is achieved by shifting focus from the exact semigroups of representations to their continuous geometric counterparts: **moment polytopes** [cite: 3]. Rooted in symplectic geometry, representation theory, and geometric invariant theory, moment polytopes encode vital "rank-like" information and asymptotic spectra [cite: 1, 4, 5]. Their relevance is profoundly cross-disciplinary. In quantum information theory, they are known as **entanglement polytopes** and resolve the single-particle quantum marginal problem [cite: 2, 4]. In algebraic complexity theory, they underpin the quantum functionals essential for the Geometric Complexity Theory (GCT) program [cite: 2, 4, 5]. Furthermore, in non-convex continuous optimization, they dictate the convergence and feasibility of matrix and tensor scaling algorithms [cite: 1, 6, 7]. 

This report delivers an exhaustive synthesis of moment polytope classification, detailing the mathematical foundations of tensor actions, the physical implications for quantum marginals, the theoretical limits of matrix multiplication, and the latest algorithmic breakthroughs in explicitly enumerating these complex geometric bodies.

## 2. Mathematical Foundations of Tensor Actions

To rigorously define moment polytopes, one must first establish the algebraic and geometric framework of tensor spaces under multilinear group actions.

### 2.1. Tensor Spaces and Multilinear Group Actions

Let $\mathcal{H}_1, \mathcal{H}_2, \dots, \mathcal{H}_d$ be finite-dimensional complex vector spaces with dimensions $n_1, n_2, \dots, n_d$, respectively. A tensor $T$ is an element of the tensor product space $V = \mathcal{H}_1 \otimes \mathcal{H}_2 \otimes \dots \otimes \mathcal{H}_d$. 

The natural symmetry group acting on this space is the product of general linear groups, $G = \text{GL}(n_1, \mathbb{C}) \times \text{GL}(n_2, \mathbb{C}) \dots \times \text{GL}(n_d, \mathbb{C})$. The action of an element $g = (g_1, g_2, \dots, g_d) \in G$ on a tensor $T$ is given by the multilinear map:
\[ \pi(g)T = (g_1 \otimes g_2 \otimes \dots \otimes g_d) T \]
This representation $\pi: G \to \text{GL}(V)$ defines how local basis changes affect the global tensor structure [cite: 8, 9]. 

For any tensor $T \in V$, its orbit is defined as the set $\mathcal{O}_T = \{ \pi(g)T \mid g \in G \} \subset V$ [cite: 8]. Because $G$ is an algebraic group, it is highly useful to study the Zariski closure of this orbit, denoted $\overline{\mathcal{O}_T}$. Understanding the geometric properties of these orbit closures is paramount in complexity theory, as algorithmic reductions are formally equivalent to orbit closure containments [cite: 3, 10]. 

### 2.2. The Null Cone and the Kempf-Ness Theorem

A fundamental concept in geometric invariant theory is the **null cone**. By Hilbert and Mumford's classical results, a tensor $T$ is inside the null cone of the representation if and only if every non-constant, homogeneous $G$-invariant polynomial $p$ on $V$ vanishes at $T$ ($p(T) = 0$) [cite: 8]. Equivalently, $T$ is in the null cone if the origin lies within its orbit closure: $0 \in \overline{\mathcal{O}_T}$ [cite: 6, 8].

The bridge linking this purely algebraic condition to continuous optimization and symplectic geometry is the **Kempf-Ness theorem**. This theorem states that a tensor $T$ is *not* in the null cone if and only if there exists a state $w \in \mathcal{O}_T$ such that the moment map evaluates to zero, i.e., $\mu(w) = 0$ [cite: 8]. Thus, evaluating algebraic invariants transforms into a gradient descent problem on a continuous manifold [cite: 8, 9].

## 3. Symplectic Geometry: The Moment Map and Polytopes

### 3.1. Definition of the Moment Map

The moment map originates in Hamiltonian physics, where it is utilized to derive conserved quantities from the symmetries characterizing the phase space of symplectic manifolds [cite: 11]. In our algebraic context, considering the maximal compact subgroup $K = \text{U}(n_1) \times \dots \times \text{U}(n_d)$ of $G$, the **moment map** $\mu: \mathbb{P}(V) \to \mathfrak{k}^*$ (where $\mathfrak{k}^*$ is the dual of the Lie algebra of $K$) measures the infinitesimal change in the norm of the tensor under the group action.

Mathematically, it can be viewed as the gradient of the log-norm function evaluated at the identity of the group. For a vector $v \in V$ and a Lie algebra element $H$, it is defined via the directional derivative:
\[ \langle H, \mu(v) \rangle := \frac{\partial}{\partial t} \bigg|_{t=0} \log \| \pi(e^{tH})v \| \]
In this setting, the gradient $\mu(v)$ is a Hermitian operator for general linear groups or a real diagonal vector for torus actions [cite: 8, 9]. 

When applied specifically to the multilinear tensor action, the moment map yields an object of immense physical significance: the vector of reduced density matrices [cite: 9, 11]. For a normalized tensor $T$, $\mu(T) = (\rho_1, \rho_2, \dots, \rho_d)$, where $\rho_k = \text{Tr}_{\neq k} (T T^\dagger)$ denotes the partial trace over all subsystems except the $k$-th one [cite: 9, 11].

### 3.2. Convexity and the Emergence of the Moment Polytope

A striking and deeply non-trivial feature of symplectic geometry is that the image of an orbit closure under the moment map exhibits highly structured geometry. Despite the moment map $\mu_G(v)$ being a non-linear (quadratic) function of $v$, the set of all possible spectra (the eigenvalues arranged in non-increasing order) obtained as $v$ varies over an orbit closure forms a rational convex polytope [cite: 11]. 

Formally, the **moment polytope** $\Delta(T)$ of a tensor $T$ is defined as the closure of the set of spectra of the moment map images, projected into the positive Weyl chamber (which enforces the condition that eigenvalues are sorted in descending order) [cite: 4, 11]. This polytope captures the entirety of the asymptotic spectral data and invariant-theoretic constraints associated with the tensor under the multilinear group action [cite: 4].

## 4. The Quantum Marginal Problem and Entanglement Polytopes

The abstract geometric formulation of the moment polytope directly answers one of the most persistent questions in quantum mechanics: the **quantum marginal problem** [cite: 4, 11].

### 4.1. Single-Particle Marginals and Reduced Density Matrices

In quantum many-body physics, a global pure state of a $d$-partite system is represented by a unit tensor $T \in V$. Observers who only have access to individual subsystems describe their local physical reality using reduced density matrices $\rho_1, \dots, \rho_d$. A foundational question arises: given a set of proposed local states (or just their eigenvalue spectra), are they mutually compatible? That is, does there exist a global pure state $T$ that marginalizes exactly to these local states? [cite: 7, 12].

For pure states, it is established that the compatibility of these marginals relies exclusively on their eigenvalue spectra [cite: 7, 12]. The allowed joint spectra are not arbitrary but are rigidly constrained.

### 4.2. Geometric Classification of Attainable Spectra

The connection to symplectic geometry here is absolute: the set of compatible marginal spectra for a global quantum state is exactly the generic moment polytope of the corresponding tensor space [cite: 11, 12]. 

Furthermore, if we restrict our attention to a specific type of entanglement—for instance, the orbit generated by a specific tensor $T$—the corresponding moment polytope $\Delta(T)$ serves as a solution to the local quantum marginal problem for that specific state [cite: 2, 4]. It provides a geometric classification of exactly which joint spectra are attainable [cite: 4].

### 4.3. Entanglement Polytopes and SLOCC Orbits

In quantum information theory, the group of local basis changes corresponds physically to Stochastic Local Operations and Classical Communication (**SLOCC**) [cite: 11]. SLOCC encapsulates operations where separate parties manipulate their local quantum systems and post-select based on classical measurements. The orbit $\mathcal{O}_T$ under the $G$-action therefore corresponds exactly to the set of states that can be distilled or reached from $T$ via SLOCC [cite: 11]. 

Because the moment polytope $\Delta(T)$ classifies the reachable marginal spectra within this orbit closure, it acts as a robust geometric invariant of entanglement [cite: 2, 4, 5]. These **entanglement polytopes** allow physicists to identify whether two different multipartite states share the same underlying entanglement structure, effectively acting as complete invariants for representations up to spectral equivalence [cite: 2, 4].

## 5. Representation Theory and the Kronecker Polytope

The structure of moment polytopes can also be entirely deduced from algebraic representation theory, creating a profound bridge between continuous geometry and discrete algebra.

### 5.1. Schur-Weyl Duality and Highest Weights

By the Borel-Weil theorem and Schur-Weyl duality, the coordinate ring of the orbit closure $\mathbb{C}[\overline{\mathcal{O}_T}]$ can be decomposed into irreducible representations of the group $G$. An irreducible representation of $G = \text{GL}(n_1) \times \dots \times \text{GL}(n_d)$ is uniquely indexed by a tuple of highest weights $\lambda = (\lambda^{(1)}, \dots, \lambda^{(d)})$, where each $\lambda^{(i)}$ is an integer partition.

The moment polytope $\Delta(T)$ is representation-theoretically defined as the closure of the set of all normalized highest weights $\frac{\lambda}{k}$ such that the irreducible representation corresponding to $\lambda$ appears with non-zero multiplicity in the $k$-th degree graded component of the coordinate ring (or equivalently, in the tensor power $T^{\otimes k}$) [cite: 4, 13, 14]. 

### 5.2. Kronecker Coefficients and Asymptotic Vanishing

For the generic multilinear action on $\mathbb{C}^n \otimes \mathbb{C}^n \otimes \mathbb{C}^n$, the relevant multiplicities are known as **Kronecker coefficients**, denoted $g(\lambda, \mu, \nu)$. These coefficients count the multiplicity of the irreducible representation of the symmetric group $S_k$ indexed by $\nu$ in the tensor product of the representations indexed by $\lambda$ and $\mu$ [cite: 11, 15]. 

Kronecker coefficients are notoriously difficult to compute, and their combinatorial structure remains deeply mysterious. Determining whether a specific Kronecker coefficient is strictly positive ($g(\lambda, \mu, \nu) > 0$) is formally proven to be NP-hard [cite: 11, 16]. However, since these coefficients govern the geometry of tensor actions, the moment polytopes provide an asymptotic description of their support [cite: 11].

### 5.3. The Stretched Kronecker Polytope

While evaluating individual Kronecker coefficients is NP-hard, studying their asymptotic non-vanishing is captured by the **Kronecker polytope** [cite: 3, 11, 14]. This is the generic moment polytope $P(n)$ formed by the union of all attainable normalized highest weights. Specifically, it captures whether there exists some integer scaling factor $s \ge 1$ such that the stretched Kronecker coefficient $g(s\lambda, s\mu, s\nu) > 0$ [cite: 11, 16]. By replacing discrete semigroups with continuous polytopes, researchers circumvent the intractable local obstructions and analyze the broader structural limits of tensor actions [cite: 3].

## 6. Algebraic Complexity Theory and Geometric Complexity

The intersection of moment polytopes and theoretical computer science is perhaps most prominent in the study of algorithmic complexity, specifically regarding matrix multiplication.

### 6.1. Tensor Rank and Matrix Multiplication

The computational complexity of multiplying two $n \times n$ matrices is governed by the tensor rank of the matrix multiplication tensor $M_n \in \mathbb{C}^{n^2} \otimes \mathbb{C}^{n^2} \otimes \mathbb{C}^{n^2}$ [cite: 3]. Despite decades of intense global research, the exact tensor rank, and the asymptotic exponent of matrix multiplication, remain elusive. Strassen observed that the closely related notion of **border rank**—which allows for infinitesimally close approximations of the tensor—can be naturally formulated as an orbit closure containment problem [cite: 3].

### 6.2. Strassen's Asymptotic Spectrum and Quantum Functionals

To systematically study tensor complexity, Strassen founded the theory of the asymptotic spectrum of tensors [cite: 1, 13]. This framework maps tensors to a topological space equipped with a measure, where functionals act as lower and upper bounds on asymptotic tensor rank. The most basic spectral points are flattening ranks, but deeper obstructions are required to separate complexity classes [cite: 13].

Moment polytopes characterize what are known as **quantum functionals**, providing robust geometric obstructions in asymptotic spectrum theory [cite: 4]. They serve as analytical tools to separate tensor complexity classes by establishing inequalities that an algorithmically simpler tensor cannot satisfy [cite: 2, 4].

### 6.3. The GCT Approach: Semigroups vs. Moment Polytopes

The **Geometric Complexity Theory (GCT)** program, introduced by Mulmuley and Sohoni, seeks to resolve major separation questions (such as P vs NP, and VP vs VNP) using representation theory [cite: 3, 15]. The original approach required finding representation-theoretic occurrence obstructions in the semigroups of specific tensors [cite: 3, 10, 15]. However, this proved exceptionally difficult due to the barrier of "Gs-representations" [cite: 3, 15].

To bypass this barrier, Bürgisser and colleagues proposed a coarser approach: replacing the strict semigroups of representations with their corresponding moment polytopes [cite: 3, 15]. By comparing the continuous geometries of the polytopes rather than discrete algebraic sets, researchers generated a more viable pathway to proving lower bounds on the border rank of matrix multiplication [cite: 3, 15].

## 7. Recent Breakthroughs: Separating Complexity Classes

Guided by the GCT framework, a central open problem was posed by Bürgisser and Ikenmeyer (Problem 7.3): Determine the exact moment polytopes of the matrix multiplication tensors and the unit (diagonal) tensors [cite: 3, 14]. 

### 7.1. Matrix Multiplication vs. Unit Tensors

The unit tensor (or diagonal tensor) $\langle n \rangle$ has a well-understood moment polytope that contains uniform marginals [cite: 3, 4, 14]. It was long questioned whether the matrix multiplication tensor possessed the same degree of representation-theoretic freedom. 

In a monumental 2025 paper by Maxim van den Berg, Matthias Christandl, Vladimir Lysikov, Harold Nieuwboer, Michael Walter, and Jeroen Zuiddam, the authors successfully proved rigorous separations between the moment polytopes of matrix multiplication tensors and unit tensors [cite: 5, 14]. By establishing a connection to polynomial multiplication tensors and the minrank of matrix subspaces, they demonstrated that certain uniform marginal spectra easily attainable by the unit tensor cannot be realized by matrix multiplication tensors of moderate ranks [cite: 4, 5, 14, 17].

### 7.2. Proof of Non-Maximality

The most profound consequence of this separation is the definitive proof that the moment polytope of matrix multiplication is **not maximal** [cite: 1, 2, 5]. A tensor is considered to have a maximal polytope (or to be "free") if its moment polytope is completely equal to the generic Kronecker polytope [cite: 1, 17]. The 2025 finding confirms that the matrix multiplication moment polytope is strictly contained within the Kronecker polytope, generalizing this non-maximality even to iterated matrix multiplication tensors [cite: 5, 14]. 

### 7.3. Asymptotic Restriction and No-Go Results

In the theory of tensors, an operational preorder known as **asymptotic restriction** describes when one tensor can be efficiently embedded within another. It was generally queried whether asymptotic restriction strictly implied moment polytope inclusion. The recent separation proofs provided a definitive "no-go" result: Strassen's asymptotic restriction does *not* automatically imply moment polytope inclusion [cite: 1, 5]. This clarifies that moment polytopes capture a geometry fundamentally distinct from basic operational embeddings, reflecting deeper invariant-theoretic truths [cite: 1, 5]. 

## 8. Non-Commutative Optimization and Scaling Algorithms

Moment polytopes are not merely abstract topological spaces; they are the central objects in a highly active field of algorithm design known as non-commutative optimization.

### 8.1. Geodesic Convexity on Riemannian Manifolds

The algorithmic challenge is to determine whether a target spectrum (or marginal) belongs to the moment polytope of a tensor. This reduces to an optimization problem over the non-commutative group $G$. The target function to minimize is the capacity, defined via the moment map gradient: $\log \|\pi(e^X) v\|$ [cite: 8, 9]. 

Crucially, while this optimization landscape is highly non-convex in standard Euclidean terms, it is **geodesically convex** along the curves of the underlying Riemannian manifold of the group [cite: 6, 7, 9]. This hidden convexity guarantees that local minima are global minima, establishing the foundation for robust scaling algorithms.

### 8.2. Operator and Tensor Scaling

Scaling algorithms iteratively apply basis changes to transform a tensor (or an array of operators) so that its marginals match a prescribed target distribution [cite: 7, 8, 11].
*   **Matrix Scaling**: A classic procedure (like Sinkhorn's algorithm) that scales the rows and columns of a non-negative matrix to achieve doubly stochastic marginals [cite: 8, 11].
*   **Operator Scaling**: An extension to completely positive maps, pushing operators to become doubly stochastic via simultaneous left-right group actions [cite: 8].
*   **Tensor Scaling**: The most complex iteration, applying local transformations $GL(n)^3$ to multilinear tensors to uniformize their partial traces [cite: 8, 11].

These algorithms operate by iteratively evaluating the current marginals and taking gradient steps (via the exponential map $e^{-\delta \rho}$) to drive the state closer to the origin of the moment polytope [cite: 7]. 

### 8.3. Capacity, Weight Margins, and Algorithmic Obstructions

The efficiency of these scaling algorithms relies heavily on the geometric parameters of the moment polytope, specifically the **weight margin** and the capacity [cite: 6, 8]. The margin $\gamma(\pi)$ is defined as the minimum positive Euclidean distance from the origin to the convex hull of any subset of the group's weights [cite: 6, 8]. 

If the margin is exponentially small, the condition number of the approximate minimizers becomes doubly exponential, meaning the optimization landscape has an exponential diameter [cite: 6]. Consequently, first-order gradient descent methods struggle to achieve high-precision solutions in polynomial time. This geometric obstruction has motivated theorists to develop second-order techniques and non-commutative analogs of interior point methods that do not rely strictly on polynomial diameter bounds [cite: 6, 16].

## 9. Computational Complexity and Explicit Algorithms

The classification of moment polytopes intersects deeply with formal computational complexity classes, differentiating itself from classical NP-hard problems.

### 9.1. NP and coNP Certificates for Polytope Membership

The **Moment Polytope Membership Problem** asks: Given a group action, a tensor $v$, and a candidate spectrum $p$, does $p \in \Delta(v)$? [cite: 9]. 

In a landmark result by Bürgisser, Ikenmeyer, and Walter, it was proven that deciding membership in the moment polytope for representations of a compact, connected Lie group is unconditionally in both **NP** and **coNP** [cite: 16]. 
*   **The NP Certificate**: An algorithm simply needs to provide an explicit tensor realization (a state in the orbit closure) that exhibits the prescribed marginals [cite: 4, 16].
*   **The coNP Certificate**: An algorithm provides a nontrivial separating facet defined by a geometric invariant, known as a **Ressayre element**, which rigorously proves that the spectrum lies completely outside the bounded polytope [cite: 4]. 

The existence of succinct proofs for both membership and non-membership makes this problem highly tractable compared to the NP-hard problem of computing the positivity of a single discrete Kronecker coefficient [cite: 11, 16].

### 9.2. Franz's Combinatorial Support and Explicit Enumeration

Historically, the exact boundary facets of moment polytopes were known only for trivial cases like $\mathbb{C}^2 \otimes \mathbb{C}^2 \otimes \mathbb{C}^2$ and sparsely for $\mathbb{C}^2 \otimes \mathbb{C}^2 \otimes \mathbb{C}^2 \otimes \mathbb{C}^2$ due to the exponential blowup in geometric complexity [cite: 1, 2, 18]. 

However, recent advances rely heavily on a mathematical characterization established by Matthias Franz, which connects the facets of moment polytopes to the **combinatorial support** of the tensors [cite: 1, 9, 18]. Leveraging Franz's theory, the algorithm designed by van den Berg et al. bypasses the exponential enumeration of the entire continuous space [cite: 2, 4]. The algorithm separates "attainable inequalities" by first engaging in a combinatorial enumeration phase. Here, candidate facet inequalities are mathematically generated as the exact solutions to linear systems dictated by the affine constraints and internal symmetries of the tensor's support basis [cite: 1, 4]. 

### 9.3. High-Dimensional Computations: 3x3x3 and 4x4x4 Tensors

This combinatorial support algorithm has allowed scientists to compute polytopes of dimensions an order of magnitude larger than previously imaginable. Integrating Nurmiev’s orbit classification, researchers explicitly calculated, with absolute certainty, the full set of moment polytopes and all their internal inclusions for the $\mathbb{C}^3 \otimes \mathbb{C}^3 \otimes \mathbb{C}^3$ format [cite: 1, 2, 18].

Moving beyond strictly deterministic bounds, they applied rigorous probabilistic and heuristic verification algorithms—powered by Gröbner bases computations over diverse fields—to compute the moment polytopes for the immensely complex $\mathbb{C}^4 \otimes \mathbb{C}^4 \otimes \mathbb{C}^4$ format with exceptionally high probability [cite: 1, 2, 18]. This specific format natively encapsulates the $2 \times 2$ matrix multiplication tensor, directly supplying the empirical geometric data necessary to prove its non-maximality and advance the GCT agenda [cite: 2, 18]. 

## 10. Conclusion

The classification of moment polytopes and the achievable spectra from tensor actions represents a breathtaking synthesis of pure mathematics, theoretical physics, and computational complexity. By mapping the chaotic algebraic orbits of tensors into the rigidly structured, continuous space of rational convex polytopes, researchers have unlocked tools that resolve the quantum marginal problem, dictate the efficiency of optimization scaling algorithms, and provide geometric obstructions to separate matrix multiplication from more primitive operations. 

Recent computational breakthroughs, deeply rooted in the combinatorial support descriptions of Franz and advanced by teams mapping the $\mathbb{C}^3 \otimes \mathbb{C}^3 \otimes \mathbb{C}^3$ and $\mathbb{C}^4 \otimes \mathbb{C}^4 \otimes \mathbb{C}^4$ spaces, highlight a rapidly maturing field. The definitive proofs showing the non-maximality of matrix multiplication moment polytopes and the placement of the membership problem within NP and coNP not only solve decades-old conjectures but establish the moment polytope as one of the most critical and universally unifying geometric invariants in modern theoretical science.

---

**Summary of Methodological Limitations and Ambiguities**
While the literature on the specific query "T#94 Moment polytope classification" is heavily skewed toward algebraic complexity and invariant theory as synthesized above, it should be briefly noted that generalized search algorithms occasionally return isolated literature where "T=94" refers to distinct, unrelated paradigms—such as quantum physical simulations at exactly $94$ Kelvin [cite: 19] or quantum gate control durations measured at $94$ nanoseconds [cite: 20, 21]. However, these instances do not pertain to the geometric classification of moment polytopes and have been contextualized as terminological noise relative to the primary mathematical focus of this report.

***

*(End of Comprehensive Report)*

**Sources:**
1. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQKJdDspATAobkROTTq_-neUOwMAKq5ub618crXN3BQ8wLV4wSrCDM3RRhychmx-i2GQLJcd-vtHTcLsqmB4C9rSNaNxNb-UK8lZYr2inqlzk=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnuXZPuutZvjPU7VTykHwUQVDAlNdpfWgQer4WcXQKi6yJODNLn6uRfoPNAwUgX0wgRmDK5njBSMceYNxNKqCD7p7AJnVk6xspt4epNk1W-0qzSXK_QA==)
3. [tu-berlin.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYR38_GSfqm6pzdUDzgsOkUA-P5B1AK0eLkPZwWZ9hTUisVLMxYUDOf_gBQ8zfrKZJqiDAhh7Q1ePcON48jpYHDZRw77xYpeT4OyNrbJuKPhWvGwOCqCYyHgK0Xqpwii9Uon66CLi6pxM6YrPJj7wWbqpRgRmlaw==)
4. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJd9pAFd80wiu0cr3nE9juhCxQ6ZhzVVgn2pHQAC_BgnKfVUpSLKtg0S--Hy8SNpoPlGxgp83d2Cq2YmEgDlqtbFxSfUk9hqKQ1G75_dGrlElqLijArj49Gb7IdfleRzfpeDNSfPUzyus-kSEQ0JFunhEvCKU=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-5Ke1lKCxYDjIL9l1d3FspNHb_cY932LHpcJULTXLBYdri-K5SnkOwgPLQTifdzwOTN5344GHS2z5ve9rSi8VauawnXFlXa6_9dJKMZQ9AmW5NLalow==)
6. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXK1YnDlWfkfcZRiip7AbRAzedezRJPUF9vVLvnSw1XZHhvKqOuMy42E986r00sUn52z9DCGfle3iAUZyiMAVl-3cSZb1X9L7Fy7eNU6l3PzcnWR762c3r31xAsuXeZ__ftrfg0-9VX-T5jePSt8IIWVlxsTrk8S5l0jrbusGySnwDr_BpCA7wETSFJIW38TKZtLKGcxNUvENGSvXLTgoc)
7. [michaelwalter.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa77w_6PEFku8rBJBbQytLzf6pIYanQRdfC67TInjWzlmVHe5Fp9pwE2TFW6hsOMIJGdQzyDEjeqsEy7Dkl12VeWxxW1EqefSVz-1tRsrlQs720AiF2MHTyKraWdI7XP-zh69Q0Hd5mA==)
8. [jleake.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgooCWmvA0OD1aFTWYGvJBXfMuezzkpzK1Ncm0cIy6IoF6mRRMOq6oQNQVnn2ufHFfR_A08YYAD7na_S0p-4usSJJhYpzGwMu6fVJM2q2e8qU-7tRDhFwy8mCRZLFBQFz4n4SnzKnFopkOsBXqSbUeQXJLPJipLfBKW_8vQJFA)
9. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBVRmTOnEwnCEzYatyES0rSuF_WGA0zBS_yVkUiq5m5SM_PmgRY952adlX30DcpAmCULz85d-vaiazarLpfZa6JuWl8JueWnI0UnFedCG5VVlR7MhqK9hicIJ37zBDh-7qDpPj99IyLwnwOWOXlLk8pwKqpO3ACvJjGwyQ)
10. [uni-saarland.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFORNHjxK4o2GFowxIKUzYRfKZimH0F25yNA-rPwFL79L8jLUeQmAGoWiYi02S2sxR_AhZRllEh5--sv48I_PycBclI0CtG3zhA7FEAbtttBlFpZ1TI75h-ISC3F-joXs3RjiL04h_vZbrjFx1nmk9KQuqCXX7thoqlmGtr_cK4gFNLgupgv7wnDuuFuejCZeNo7WLUIP0Gag==)
11. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzwu3fzEkWDz12rPknDjUHr2tpDQD08v0WtTf03UU0mwuiSTJN1zKHOomXtjP4eGOLl1cfWjfURbz7hOCYXBPANADtfwQRAUd5L0WeFeE1zCbWbNiv8izDCFk_wFXjV0CNOKYTQzpG13wpoyrts4FhBc3P84QXlgjSSmZhaqvc6j8=)
12. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU6h0p7_dWjA3Sr1sBZN-xzUvMUQOYLjExFv1992YJWXpNg0OfOry1rW7tnBCiw7GB07LWUaD5rTGoDFJ95wxF68af6vwa0haSgBah-LGagOnziQiBdd3Oa2HR_wDEnR-rniEkhtOP3g2jraEfbEmsHt4=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG243vyutlPkY4JEnIOBWb4mJVmlJSzjY24K6XggS25OOpBNarZyyc4GUL8eEXiyC6aOaqvd_CFGU1BROmA-AaFm03diQGEZtO1D3vyMmPu_BD60-usfenD0A==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiwPU6946nYdeEPN4t5GHjdkQqTkKzlD8XykqjRxExGkzXh4r_ZJzwBWZWT4daNhwWrzEw6sFRKPzek92Nau8DzYe3IhGXnTvUBtUpYK6XlhSsWa6wxA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhNiRZd1uHgxvzIDm1T17k1pLquBKg-LM8ccH_6c6LG8jAKqdt_3-LD6mRYxlnQi9cccoo5T43AgKY7xJap9smkZrz2Hj5BApsLu-F9gleqfKEz8Qo)
16. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEieH9sM9VlnpFyA81KoMDZLwjvN3GG8AKqBRoJYz3TVhsFHMWTTD_wepdbfVsyjB5ImnFXx1NZyV3f7wfymnUBArCZX701fFUumrh2IuWZ9UemcBRWrlSTsu_mJMuooJuGOt4=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEujhdgpwbDpa0O8KJZbxr0OGShbvzHdVhGRA_bWEzxYWtACjvn9HuFPASL6_fHFxir8oHpXw2cYCwHv9sKtlrT8Bk-mXCZTqlJZp36ScxSRoG5U_AItwTEakzfpaSX0SNqc03m91uLOD7ct5nNMJ2UYkE3bRCop16HYrCnRNOIg9xw2LshO9Q=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhw9ToWPZ-naOstNtw6bZfDqZVydlYo1go6L5hkgj4QLS15vA73BJpGl_177PCGTK7Pwa6OwXLmPswLXzoSoncHeCumz685RhF2uIFVgPr1r9kxJCjgw==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7U8YrdZIKoTJbemVJoqOrlzP-t62YvtNz3l0ZoY5-XNUnq2_O1hJj0_ntSpxP3RK052JLZHtvHXjoFOO6IF9kZcG7tV0ei3k4ebqrWBhN6AoUBhaILA==)
20. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEACVQoxFxr4uTbL1oJpSRSFtTsDTq5Hffye_cyy48_uxbsTMFqFOH8Nzw4gpt31MbT4HViF8Q2pU2Ue6As14CwBwnuKBWH3PneroBd80ws8yWj8QpfmEp1UTOheeBYO9p7weWdwK949wSSLgmXi-l_X1CmSwjaUZLIUQx2bVBLWCcQaemwJo=)
21. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjStQ6mVSeWFpSB4ebzOWkyo_1-0IZVdUDWqa5tv3ZFzMrYSN6WxprM2CsQVHWiiIKoc6uHABuAgmZq2LY_vNQvXPUnyNDJAlFv8qm5xQuA0FQIYDLZKjt5TFJFUdPr7s=)


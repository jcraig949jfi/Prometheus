# T#70 Nonnegative tensor (p,q)-spectral radius

**Pythia queue id:** 111
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdyQ0FQYXIyWk45V1dfdU1QeWJxNXNRcxIXckNBUGFyMlpOOVdXX3VNUHlicTVzUXM
**Elapsed:** 314s
**Completed at:** 2026-05-21T15:16:55.958875+00:00

---

# Nonnegative Tensor (p,q)-Spectral Radius: A Comprehensive Analytical Report

### Key Points
*   **Fundamental Concept**: The $(p,q)$-spectral radius represents a generalization of the singular values and spectral radii from classical matrix theory to higher-order multilinear algebra, specifically for partially symmetric rectangular tensors and directed hypergraphs. 
*   **Perron-Frobenius Generalizations**: Significant mathematical advancements have successfully extended the Perron-Frobenius theorem to nonnegative tensors. While early proofs required strict conditions (such as $p, q \ge r+s$), recent breakthroughs have established validity across a much broader parameter space, including nonlinear multihomogeneous mappings.
*   **Broad Applications**: The mathematical framework of the $(p,q)$-spectral radius provides critical analytical tools for diverse fields, solving problems related to strong ellipticity in solid mechanics, quantum entanglement, higher-order Markov chains, spectral Turán problems in combinatorics, and multi-layer network centralities.

### Executive Summary
The transition from linear algebra (matrices) to multilinear algebra (tensors) has unlocked new mathematical paradigms capable of modeling complex, higher-order relationships. Central to this transition is the study of the $(p,q)$-spectral radius of nonnegative tensors. For a general audience, a tensor can be thought of as a multi-dimensional array of numbers—a generalized matrix. While matrices capture pairwise relationships (like a graph where edges connect two nodes), tensors capture multi-way relationships (like a hypergraph where a single edge can connect many nodes). The spectral radius characterizes the dominant "scaling factor" or largest singular value of this system.

Research into the $(p,q)$-spectral radius bridges pure mathematics and applied computational theory. It provides the foundation for the Perron-Frobenius theorem of multilinear forms, which guarantees the existence of a unique, dominant, nonnegative eigenvector for strictly positive systems. This report provides an exhaustive, rigorously detailed exploration of the $(p,q)$-spectral radius. It covers its foundational definitions in the context of rectangular tensors, tracks the evolution of the Perron-Frobenius theorem for these spaces, explores computational methodologies like the NQZ algorithm and the $\alpha$-normal labeling method, and maps its diverse applications ranging from combinatorial hypergraph theory to mechanical engineering. 

---

## 1. Introduction to Tensor Spectral Theory

The study of tensor eigenvalues and singular values marks a significant milestone in modern computational mathematics and multilinear algebra. In 2005, the concept of eigenvalues for tensors was independently introduced by Lim and Qi, fundamentally altering the landscape of tensor analysis [cite: 1, 2]. A tensor $\mathcal{A}$ of order $m$ and dimension $n$ is defined as a multidimensional array containing elements $a_{i_1 i_2 \cdots i_m}$, where each index ranges from 1 to $n$. The set of all real-valued tensors of order $m$ and dimension $n$ is denoted by $\mathbb{R}^{[m,n]}$ [cite: 2].

In the special case where $m = 2$, the tensor reduces to a classical square matrix. A tensor is termed *nonnegative* if every scalar entry satisfies $a_{i_1 i_2 \cdots i_m} \ge 0$, and the space of such tensors is denoted by $\mathbb{R}_+^{[m,n]}$ [cite: 1, 2]. The classical spectral theory of matrices, heavily anchored by the Perron-Frobenius theorem, details how a nonnegative, irreducible matrix possesses a unique largest positive real eigenvalue (the spectral radius) associated with a positive eigenvector. Extending these properties to higher-order non-linear tensors required entirely new theoretical scaffolding.

As tensor applications grew to encompass best rank-one approximations in data analytics, modeling of higher-order Markov chains, and structural analysis of multilayer networks, the necessity for a robust theory of tensor singular values emerged [cite: 3]. While early tensor spectral theory focused on square (cubical) symmetric tensors, researchers quickly identified the need to analyze asymmetric and *rectangular* multi-way arrays. This led to the rigorous formulation of the $(p,q)$-spectral radius and $l^{p,q}$-singular values for rectangular tensors [cite: 4, 5].

## 2. Fundamentals of Rectangular Tensors and Singular Values

### 2.1 Partially Symmetric Rectangular Tensors
Unlike square matrices that map vectors within the same space, rectangular matrices map between spaces of different dimensions. The tensor equivalent is the *rectangular tensor*. For any positive integers $r, s, m, n$, an $(r,s)$-order $(n,m)$-dimensional rectangular tensor $\mathcal{A}$ is defined as a multi-dimensional array $\mathcal{A} = (a_{i_1\cdots i_r}^{j_1\cdots j_s}) \in (\mathbb{R}^n)^r \times (\mathbb{R}^m)^s$ [cite: 4, 6]. 

A critical structural property for these tensors is *partial symmetry*. The tensor $\mathcal{A}$ is called partially symmetric if its entries are invariant under any permutation of the lower $r$ indices and invariant under any permutation of the upper $s$ indices [cite: 4, 6]. Mathematically, this means:
\[ a_{\pi(i_1,\ldots,i_r)}^{\sigma(j_1,\ldots,j_s)} = a_{i_1\cdots i_r}^{j_1\cdots j_s} \]
for any permutation $\pi$ in the symmetric group $S_r$ and any permutation $\sigma$ in $S_s$ [cite: 7]. Such partially symmetric rectangular tensors arise naturally in mathematical modeling, particularly in the study of directed hypergraphs, where edges connect a set of "tail" nodes to a set of "head" nodes [cite: 4].

### 2.2 The $l_{k,s}$-Singular Values and $(p,q)$-Spectral Radius
The singular values of a real rectangular tensor were systematically introduced and studied by Lim and later by Chang et al. [cite: 5, 7]. Building on this, Ling and Qi (2013) generalized the concept to define the $l_{k,s}$-singular values and the $(p,q)$-spectral radius of rectangular tensors [cite: 4, 5]. 

By defining the multilinear action of a rectangular tensor on vectors $x \in \mathbb{R}^n$ and $y \in \mathbb{R}^m$, the $(p,q)$-spectral radius poses a constrained maximization problem. For parameters $p, q \ge 1$, the goal is to maximize the polynomial mapping associated with $\mathcal{A}$ over unit spheres defined by the $l^p$ and $l^q$ norms [cite: 4, 5]. Taking specific fractional or integer pairs for $k$ and $s$ yields different geometric characteristics, such as the $l_{p,q}$-singular values or the $l_{p/2, q/2}$-singular values, which are utilized to classify the positive definiteness of the associated multilinear forms [cite: 5].

The $(p,q)$-spectral radius generalizes several matrix concepts. For a nonnegative rectangular tensor, the calculation of the maximum singular value under these norms directly corresponds to solving nonlinear eigenvalue problems, which feature heavily in multi-marginal optimal transport and the discrete generalized Schrödinger equation [cite: 8].

## 3. The Perron-Frobenius Theorem for Tensors

The Perron-Frobenius theorem is a cornerstone of linear algebra, stating that an irreducible non-negative matrix has a unique largest real eigenvalue corresponding to an eigenvector with strictly positive components. Extending this theorem to non-linear maps and tensors has been a major mathematical endeavor.

### 3.1 Initial Breakthroughs and Constraints
The non-linear extension of the Perron-Frobenius theory has seen significant uses in dynamical systems, game theory, mathematical biology, and computer science [cite: 9]. In the context of rectangular tensors, Ling and Qi (2013) proved a Perron-Frobenius theorem for partially symmetric rectangular tensors, but their proof was constrained to parameters satisfying $p, q \ge r+s$ [cite: 4, 6]. This represented a significant first step, demonstrating that under highly convex conditions, multilinear forms preserve the unique maximal eigenpair structure of non-negative matrices.

### 3.2 Extensions by Lu, Yang, and Zhao
In 2018, Lu, Yang, and Zhao drastically improved upon the Ling and Qi results [cite: 4, 6]. Through their work, they extended the Perron-Frobenius theorem to cover all $(p,q)$ pairings satisfying the inequality:
\[ \frac{r}{p} + \frac{s}{q} \le 1 \]
Furthermore, they provided a proof for the Perron-Frobenius theorem covering general nonnegative $(r,s)$-order $(n,m)$-dimensional rectangular tensors in the regime where $\frac{r}{p} + \frac{s}{q} > 1$ [cite: 4, 6]. Their research essentially proved that these bounds are the best possible that can be achieved without imposing additional restrictive conditions on the tensor $\mathcal{A}$ [cite: 4, 6]. This expanded framework was then systematically applied to establish bounds and properties for the $(p,q)$-spectral radius of directed hypergraphs [cite: 4, 6].

### 3.3 Unification via Multihomogeneous Maps
To capture the full spectrum of tensor eigenvalue and singular value variations, Gautier, Tudisco, and Hein (2019) introduced a unifying Perron-Frobenius theorem for nonnegative tensors utilizing the theory of *multihomogeneous mappings* [cite: 10, 11]. 

They formulated the irreducibility and symmetry properties of a nonnegative tensor $\mathcal{A}$ by introducing the concept of a "shape partition" [cite: 10]. By recasting the tensor eigenvalue problem as a fixed-point problem mapped on a suitable product of projective spaces, they utilized vector-valued versions of the Hilbert projective metric and Thompson's metric [cite: 8, 10]. This multihomogeneous framework allowed them to prove weak and strong Perron-Frobenius theorems that unified earlier fragmented results [cite: 8, 12]. 

Specifically, this multi-dimensional nonlinear Perron-Frobenius theory addresses the existence, uniqueness, and maximality of nonnegative and strictly positive eigenpairs for order-preserving multihomogeneous functions defined on a product of cones [cite: 8, 11, 13]. It guarantees the uniqueness of the $l^{p,q}$-singular vectors of nonnegative matrices, the $l^p$-eigenvectors, and the rectangular $l^{p_1, \ldots, p_d}$-singular vectors of arbitrary nonnegative tensors, independent of the exact values of $p, q$ within $(1, \infty)$ [cite: 8]. Additionally, it establishes a Collatz-Wielandt principle for the maximal eigenvalue of these non-linear systems [cite: 12, 14].

## 4. Spectral Theory of Directed Hypergraphs

One of the most profound applications of rectangular tensor spectral theory lies in combinatorics and graph theory, specifically in the study of hypergraphs. While classical graphs consist of edges connecting exactly two vertices, hypergraphs contain *hyperedges* that can encompass any number of vertices.

### 4.1 $(r,s)$-Directed Hypergraphs
An $(r,s)$-directed hypergraph is a mathematical structure where each directed hyperedge (or arc) possesses $r$ vertices in its "tail" and $s$ vertices in its "head" [cite: 4]. Let $G$ be an $(r,s)$-directed hypergraph. The connectivity of this graph can be perfectly encoded into a partially symmetric rectangular tensor $\mathcal{A}$ of order $(r,s)$ [cite: 4].

For any real numbers $p, q \ge 1$, the $(p,q)$-spectral radius of the directed hypergraph $G$, denoted as $\lambda_{p,q}(G)$, is defined as the constrained maximum:
\[ \lambda_{p,q}(G) := \max_{||{\bf x}||_p=||{\bf y}||_q=1} \sum_{e\in E(G)}\Bigg(\prod_{u\in T(e)}x_u\Bigg)\Bigg(\prod_{v\in H(e)}y_v\Bigg) \]
where ${\bf x}=(x_1, \ldots, x_m)^{\rm T}$ and ${\bf y}=(y_1,\ldots, y_n)^{\rm T}$ are real vectors, and $T(e)$ and $H(e)$ represent the tail and head of the directed hyperedge $e$, respectively [cite: 4, 15]. 

This formula elegantly captures the multi-way interactions. Maximizing this polynomial over the $L^p$ and $L^q$ unit spheres outputs a singular value that reflects the densest structural components of the directed hypergraph [cite: 4, 15]. The structural bounds of $\lambda_{p,q}(G)$ and the spectral relations between a complete graph $G$ and its disconnected components are deeply governed by the Perron-Frobenius properties of the underlying nonnegative adjacency tensor [cite: 4].

### 4.2 The $\alpha$-Normal Labeling Method
Calculating the precise spectral radius of a large, complex hypergraph is computationally daunting. To address this, Lu and Man introduced the $\alpha$-normal labeling method for uniform hypergraphs in 2014 [cite: 4, 16]. It is recognized as a highly effective analytical tool for computing and bounding the spectral radii of uniform hypergraphs [cite: 4, 16].

In standard uniform hypergraphs, the $\alpha$-normal labeling method operates by assigning a positive number (a label) to each "corner" of a hyperedge. The rules state that the sum of the corner labels at any single vertex must equal 1, while the product of all the corner labels within any given edge must equal a constant value $\alpha$ [cite: 16]. 

Recognizing its utility, Lu, Yang, and Zhao subsequently expanded the $\alpha$-normal labeling method specifically to calculate the $(p,q)$-spectral radii of $(r,s)$-directed hypergraphs [cite: 4]. This mathematical bridge allows researchers to determine bounds and limits of directed multi-way structures efficiently, bypassing the need to directly compute the roots of massive multilinear polynomials [cite: 4, 15].

## 5. Spectral Extremal Problems in Combinatorics

The tensor spectral radius serves as a core mechanism for resolving longstanding challenges in extremal graph theory, particularly hypergraph Turán problems.

### 5.1 The $p$-Spectral Radius of Uniform Hypergraphs
For an $r$-uniform hypergraph $H$ containing $n$ vertices, the generalized $p$-spectral radius $\lambda^{(p)}(H)$ is defined for every real number $p \ge 1$ as the maximum value of the tensor multilinear form scaled by the $L^p$ unit sphere [cite: 16, 17]. Formally:
\[ \lambda^{(p)}(H) := \max_{|x_1|^p+\cdots+|x_n|^p=1} r \sum_{\{i_1,\ldots,i_r\}\in E(H)} x_{i_1}\cdots x_{i_r} \]
Introduced by Keevash, Lenz, and Mubayi, and extensively studied by Nikiforov, the case where $p=r$ yields the classical spectral radius of $H$ [cite: 16]. This parameter generalizes multiple critical hypergraph metrics, including the Lagrangian, the number of edges, and standard spectral bounds [cite: 17].

### 5.2 Turán Problems and Expanded Hypergraphs
A classical Turán problem asks for the maximum number of edges an $n$-vertex graph can possess without containing a specific forbidden subgraph $F$. In generalized spectral Turán problems, researchers seek to determine the maximum $p$-spectral radius of hypergraphs that do not contain certain structural copies [cite: 17].

For instance, the clique tensor represents a higher-order extension of a graph's adjacency matrix, serving to measure densely interconnected sub-components (cliques) [cite: 18]. Utilizing the spectral properties of adjacency and clique tensors, mathematicians have identified the extremal hypergraphs that maximize the $p$-spectral radius. In one major finding, the extremal hypergraph that maximizes the $p$-spectral radius among all $n$-vertex $r$-uniform hypergraphs without $t$ vertex-disjoint copies of an expansion $K_{k+1}^{(r)}$ is uniquely isomorphic to the join of the complete $r$-uniform hypergraph and a Turán hypergraph $T_r$ [cite: 17]. 

Furthermore, the spectral radius of tensors has been applied to cancellative hypergraphs, successfully providing an alternative spectral proof for Bollobás's classical combinatorial theorem regarding the maximum size of cancellative 3-uniform hypergraphs [cite: 17].

## 6. Computational Algorithms and Convergence Theory

While theoretical existence and uniqueness are guaranteed by the Perron-Frobenius theorem, explicitly computing the $(p,q)$-spectral radius of massive nonnegative tensors requires specialized iterative algorithms.

### 6.1 The NQZ Algorithm
The most prominent computational tool for calculating the dominant eigenvalue (the H-spectral radius) of an irreducible nonnegative tensor is the NQZ algorithm, proposed by Ng, Qi, and Zhou in 2009 [cite: 1, 2]. It is widely regarded as the natural multilinear extension of the classical power method used for matrices [cite: 1, 2].

Given an irreducible nonnegative tensor $\mathcal{A} \in \mathbb{R}_+^{[m,n]}$, the NQZ algorithm proceeds iteratively to find the largest eigenvalue $\lambda$:
1.  **Initialization** (Step 0): Choose a strictly positive initial vector ${\bf x}^{(0)} > 0, {\bf x}^{(0)} \in \mathbb{R}^n$. Define ${\bf y}^{(0)} = \mathcal{A}({\bf x}^{(0)})^{m-1}$ and set iteration counter $k := 0$ [cite: 2].
2.  **Iterative Update** (Step 1): Compute the normalized vector:
    \[ {\bf x}^{(k+1)} = \frac{({\bf y}^{(k)})^{[1/(m-1)]}}{||({\bf y}^{(k)})^{[1/(m-1)]}||} \]
    Then, calculate the new output vector ${\bf y}^{(k+1)} = \mathcal{A}({\bf x}^{(k+1)})^{m-1}$ [cite: 2].
3.  **Eigenvalue Estimation**: Determine the upper and lower bounds for the eigenvalue at step $k+1$:
    \[ \underline{\lambda}^{(k+1)} = \min_{x_i^{(k+1)} > 0} \frac{({\bf y}^{(k+1)})_i}{(x_i^{(k+1)})^{m-1}}, \quad \overline{\lambda}^{(k+1)} = \max_{x_i^{(k+1)} > 0} \frac{({\bf y}^{(k+1)})_i}{(x_i^{(k+1)})^{m-1}} \]
    If $\overline{\lambda}^{(k+1)} - \underline{\lambda}^{(k+1)}$ is less than a predetermined tolerance threshold, the algorithm terminates, yielding the spectral radius. Otherwise, increment $k$ and repeat the update [cite: 2].

### 6.2 Convergence Analysis and Positivity Conditions
The convergence behavior of the NQZ algorithm depends strictly on the zero-pattern (positivity conditions) of the tensor $\mathcal{A}$. A substantial body of analytical work has sought to establish the convergence rate across generalized tensor topologies [cite: 1, 2].

*   **Primitive Tensors**: Chang, Pearson, and Zhang (2011) established that the NQZ algorithm unconditionally converges for primitive tensors [cite: 1, 3]. 
*   **Essentially Positive Tensors**: A tensor $\mathcal{A}$ is essentially positive if its associated representation matrix has strictly positive off-diagonal entries. Zhang and Qi subsequently proved the linear convergence of the NQZ algorithm for this class [cite: 1, 3].
*   **Weakly Positive Tensors**: A tensor is weakly positive if its representation matrix $M(\mathcal{A})_{ij} > 0$ for all pairs $i \neq j$. Improved variants like the LZI algorithm have demonstrated linear convergence in these spaces [cite: 1, 3].
*   **Weakly Irreducible Tensors**: By utilizing the directed graphs associated with a nonnegative tensor $G(\mathcal{A})$, modern literature has established the R-linear convergence of the NQZ algorithm for certain classes of weakly irreducible tensors, deriving precise upper bounds for the root convergence factor [cite: 1, 2].

### 6.3 Multihomogeneous Power Methods
To compute the $l^{p,q}$-singular vectors of rectangular tensors, Gautier et al. generalized the power method into a framework for multi-homogeneous maps [cite: 10, 12]. By iterating normalized multi-homogeneous order-preserving maps, they provided a thorough convergence analysis demonstrating geometric (linear) convergence rates to the unique normalized positive eigenvector [cite: 4, 8]. This non-linear power method unifies previous algorithms and works even when generalized tensor shapes break strict symmetry assumptions [cite: 11].

## 7. Real-World Applications

The abstraction of the $(p,q)$-spectral radius translates into powerful modeling solutions across multiple scientific and computational domains.

### 7.1 Solid Mechanics and Quantum Physics
Real rectangular tensors and their singular values arise fundamentally in the study of the strong ellipticity condition in non-linear elasticity and solid mechanics [cite: 5, 7]. In elasticity theory, an elasticity tensor is characterized as a real, partially symmetric rectangular tensor [cite: 5]. Determining whether a nonlinearly elastic material satisfies the strong ellipticity condition is mathematically equivalent to judging the positive definiteness of this tensor [cite: 5]. This is achieved by computing specific tensor singular values and eigenvalue inclusion intervals (such as C-eigenvalues of piezoelectric-type tensors) [cite: 5, 7]. 

Similarly, the spectral radius of rectangular tensors plays a crucial role in calculating quantum entanglement bounds in multi-partite quantum physical systems, mapping the highest probability states of coupled particle systems [cite: 5, 7].

### 7.2 Multi-Layer Network Centrality
In modern network analysis, interconnected systems are rarely flat graphs. Multi-layer (or multiplex) networks consist of interacting nodes across various distinct layers (e.g., individuals interacting simultaneously on Twitter, LinkedIn, and Facebook). The mathematical framework of the multihomogeneous Perron-Frobenius theorem directly translates into computing eigenvector-based centrality measures for nodes and layers in multi-layer networks [cite: 1, 13]. The non-linear spectral radius determines the ultimate "influence" score of a node taking into account the higher-order interactions between differing network layers [cite: 13].

### 7.3 Data Mining and Image Reranking
Hypergraphs and tensor multilinear algebra excel at modeling complex relationships in large datasets. In visual-duplicate keyframe analysis and web video retrieval, standard graph matrices often miss latent, higher-order relationships. By modeling video threads and image tags as vertices, researchers can form unified incidence hypergraphs [cite: 19, 20]. 

Computing the spectral properties and utilizing transition probabilities on these hypergraphs enables advanced random-walk algorithms (like multilinear PageRank) that outperform traditional pairwise clustering. In experimental datasets of web videos, hypergraph reranking improved retrieval accuracy by up to 45% by capturing the high-order contextual semantics that binary graph matrices simply could not observe [cite: 19, 20]. The spectral radius governs the convergence and transition matrix stability of these data mining models.

## 8. Conclusion

The $(p,q)$-spectral radius of nonnegative tensors is a vital bridge spanning strict linear algebraic traditions and the dynamic, non-linear realities of higher-order data. By successfully extending the Perron-Frobenius theorem from classical square matrices to partially symmetric rectangular tensors and multihomogeneous mappings [cite: 4, 11], mathematicians have unlocked rigorous methods for proving the existence and uniqueness of dominant eigenpairs in multi-way spaces.

Through iterative computational frameworks like the NQZ algorithm [cite: 2] and analytic bounds derived via the $\alpha$-normal labeling method [cite: 4], previously intractable problems in hypergraph connectivity, solid mechanics elasticity, and multi-layer network flows can now be precisely characterized. As research continues to weaken the restrictive boundary conditions on tensor irreducibility and positivity, the application space for tensor spectral theory will undeniably continue to expand, offering deeper insights into the complex, non-linear systems governing our world.

**Sources:**
1. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQwjDgZfh3s7WdW-in_Phb-oN9dXoEruzCbfRFuLF3139qvJZ-ADLlWCCw2ee7_JI-SqufMA6yGO-Yh2pTquR39ko3nZl1jbOyXZiNTmQofDC2XfP_40u4eEL516R2OkSzPoI35mtO6f6Uz4ai7DdxqfLTbGYRLarhWB3763s=)
2. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcetghPIAsV7t2swazdfXl1uX8K0WYMSBYsq1w2TYgXLovgn4Gs4AkZLyYl0cdDUwPlq5NzeMQ2ZWkiaoMroaU6WR4G-z94wO5nGq56VbpCF4KP-LBuVGkbgYVvt7yl76HE5wf6UcJ)
3. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8XLnHJaxpXNgUnyfYf6d6VqExB44rIFvK-rx3jP2eAi_QeNB4jV477eXH2Hd6qST_rCyvJhmqSrEUZI_-4IRKNkK6z-uDTwR9t-y82fbsI0rjyuET0GvxAjlnC2VFJVBoUKddOURPyoXAdDZSnw9JQfTqCDOXtjLvzET1isAYAKS1c0F-jYdsK5uqk824iCaCXQ==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1ICaDwPgyLQ3wAbP_cBiiKKFf_pJXE5z9_1FnxxHjiTTRcVhKq0_zNn_CLSib5wyW8K_GIyh75XFb_n-rN0OqKV8IDROPaqf-uU8h2p3VgAgcFt2fPiSNpy5Srsl8UsNnmP8Z6RLdntwyELgvldXwHu_2R44-jZVKIBSn_9UcwXiu8rFZNn-KEO83dOzB_ZPzUeiZ7GSl799EcTApmc4eDlWtL61126sjhdc8HxwCcVA=)
5. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfeyMm8iDMQtjujaaYw0JdzaGYuEhJOJ4m9wC2Y3uy-hUxDWXzFxUf4fIrSBUNwpr3mgivy59dX7HVMfHOZ1pK56qwrW_djS01E3EEbXf1ZJ7gU_30mLq_bg-6H-bOrV-Gl4pWYx-o4yee9kItXJL3fw==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHUysFsrY2PH1lmC-KO3I0epsbh4q8matplfJ9Q0K7qkjOtCEf95EWGA2d1wqpnA1EsJtbMq0kPhQ7JkqlbIICzWR6FuOJX2lAhp6tJRSG_YGTCQp0)
7. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGb4brmK0rlX7barohUWU7lTC8GAg6FY6lJqPsHP-5OnqVSrrp0cGk64hExD7Wl_TtSTVOLXDTa4XyMWpRvQ1k5UTgpRdBb4rzax1gqngStgotrjyDKK0R4_9iANHIJK2hV_RmwddbbOL2p7dT0grO5WA==)
8. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHLLrriqTX32hbxyweOYhACtADAjhLKgUpxQ7N3vjxwLjGW5vxvU5K0ts2IXQM010v9VccUau7IN9BPtP9NU-1NXkBFGaO495ds9NwVg0hGNih034=)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcdxhLvrf_V3D9vCVuOQvUkLMWuV1vHQNMgCp8FgKYvkfNlCGHKLRQT0iKJwEfefAuA2JK7QaphX0qAPuIRUoyiRN0xKg-p_07SNEPvdGoBDymTIWk0syeYyi-DuJ59qbA5A9X4jYTDtloAh0Ibwzudkap1pq2O4xygtikn_1OfvbVX-Mc0QrUcG3GQE5IzX2Fjn9v4U12UuhD7n0GFBAu4mpszQRGICs=)
10. [gitlab.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOXR7ZRF7NlHicaq80BWfud3Niz9gNHiRe_uKl-8BjksolEAKPrGbJOZCR3p7qLBb-bTBnCtiBG9hY5XK5kO5jsH7tc_u1Nv0nw8WxBqF-fl6_OmsdVVRtZbbaeWI9Orb2Jg0T0KoDQJOT90j_p3KH42gPbOKJ8ClWkNO_5xRUKo7A2PfqdiTMHOQ=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPWV3dEojdEN93q1oSoFUEn-q4wDpQPYQGTlGyCe3WhHCODybFB4D8QCHfKqWjjAzN5BC8SmHE82ej0U_EoopwSsapIIgrpSSGzzmOlONz9wL0i4iY)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF35gCLGp3271c3_PgfRTEAwHRN9MEiVKSkngCy_gZJ_i_LMrAS0y45ypmJaSHzWHqYST6H_GWopBHyNl-TQgAn9J1-KjNwx7-e8dwbnqaqR1m5YthOsSVMFL8oYFTH51D5KeII3p1TE6N0qaG1VeCJgM268I-L_FqGFYyPiJ4k4xyMbsUjESxDjBTXaf_gjYy0wZlqrzWxsqbT__89wjw=)
13. [unipd.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE65uXyG2CvW6VnWYVdcmGgyQYlQIy2uA_NlknVdaLRKaBFgJRwH8gjgru_-M8z_f2QaumrobBqIzQnGlFF7U17tojetAoYwuss3qoFPCppLvNTbp-xZBX7tSz2S0fj59IzZgzwNhDwDapvf-7DpCN6j8DXGOLNgLMuOQ==)
14. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZBvs_jbwzyMyBmCH2pcUtYQHO8T3lPTMdusL8IzLHZuZtFz5Ml3NGIOI4DSUho1jw8hdkQUPKbWGp1zdPEyWQ0g6Q4OTrOepjum0xZ7R42UrOTYL1_Yl8Tw55DDM62XQLdA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3a41FoswELWyAXBcv9kzABW740QHex3WaVW-Y0MQh63UcQSPw-siou3pXLSFXsMgadGGpg5jgpJSqb5tfXJdVFf_JvLRs4HN8tQOBX0l2xnidwQMd)
16. [usst.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3D95Ghtk4pbvCUs2dIvjJvZBjnojRO3Slc45r4mSXkWr_CqO4EEa5Ws3gavMZ2VUQzRBcnm-G7yNotnUN_YCve0zyQ1f3SFWjdsI0FSLlvpdN0sHZ24FPc1ZAETyeKeSeCnwO77QYFthSo3o=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCF_xiqPnc4rEfHj35MEk0KMmyXm8QHWXPBDFSDaV5nINJlKRcfqmu3w3JfUWyW4qmvf6u4lYqlw8W7zreLIIBeYxVahtpVN0JYe4nfIzgpzJ2XFyYZElD_w5UjZbXa3DfSes99sWNk3MBrXyrIahtWZwDSbvCuxIcccKrknEvz8hwwJNtp_pQaD6lai7aEHvyY1D5whp5vg==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9dwbkJG50mmRgGtx_ZqmimAh_pdVtuW49d65JZeZ08cXeN7QetxBdPOyohmCYHBAeCzbiRLwPXsFSdb0_8MDQe9y_pD1E0yTDM2d8jCXUm1XTh7PcMSByQG9eAv0cqnqoXDLXuw3SEhsYjpqfaKkjFqE19l9BN5wfqH7ywl6z_bfcxVansg==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQnv0Bw5RTaAfxin9ViMpJKG1sWNBz7pa4Z07u8W5jU2wrSPPl6e-XWDpRG0T1UUGCbu3Z98WNt-hhwuaEwYc2_awcsIrgfa_iz9EFvmkoqvztoA61q4Ln46MaoDfo7ndVlOfZg4QBkk79u5j23GGQLUUduE29Kk5zLoa3FgpashehKf1bwJN4ujPjuDLdIXtwPL_ZpHOok921ZdtwEDLCzUYMjA==)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKFxMpt_-HmDOvSfzXACFJDPfpdvbl0AZEbOYQsLLBmtHEdTGBWs_fTlKSecRDE3iSoX5wSb-H0JWfG0WE_Rpb2bSqqd7BkAc7gUxeBu-2rzOPC4EtIo9_L2siM8XL6kWof08CnnZhAy9hLohbNxO1Sc9WfB8Dat4mFMp58wO4QgWPfl-pzWAqi-g-90LlxduzqyPqRu6zhDmKcz8ihDmA2Kvxxd--6XTi7mkz7m_KlvsYV2WPlnfg4lnlcMgsb9a8tJmfJ2YzNk263Tj4)


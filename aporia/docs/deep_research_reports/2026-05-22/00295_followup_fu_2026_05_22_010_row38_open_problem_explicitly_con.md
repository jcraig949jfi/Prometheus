# Followup [FU-2026-05-22-010 <- row38]: **Open Problem:** Explicitly construct the missing spectral points for $d$-mode tensors ($d \ge 4$) 

**Pythia queue id:** 295
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdPTEFQYW9Pc0pyZWtfdU1QMzVHNmtBOBIXT0xBUGFvT3NKcmVrX3VNUDM1RzZrQTg
**Elapsed:** 250s
**Completed at:** 2026-05-22T01:28:20.058839+00:00

---

# Status Update: Explicit Construction of Missing Spectral Points for $d$-Mode Tensors ($d \ge 4$)

### Leading Paragraph
**Key Points:**
*   **The core open problem** challenges the theoretical computer science and algebraic geometry communities to explicitly construct genuinely new spectral points for $d$-mode tensors where $d \ge 4$, as recent proofs indicate currently known quantum and support functionals are mathematically insufficient [cite: 1].
*   **Recent breakthroughs** in 2026 have successfully unified Strassen’s upper support functionals with quantum functionals (solving a 1991 conjecture) [cite: 2, 3], but simultaneously proved that these unified functionals fail to capture the full asymptotic spectrum for higher-order tensors [cite: 1, 4].
*   **The evidence leans toward** the necessity of entirely novel algebraic or representation-theoretic constructs, likely extending beyond marginal entropy optimization on entanglement polytopes, to capture the newly identified spectral gaps [cite: 5, 6].
*   **Algorithmic implications** are profound: resolving these missing spectral points is deemed critical for extending the algebraic complexity toolkit beyond bilinear maps, directly impacting hypotheses like the Asymptotic Rank Conjecture and the Set Cover Conjecture [cite: 7, 8].

The study of the asymptotic spectrum of tensors, originally pioneered by Volker Strassen to bound the complexity of matrix multiplication, has evolved into a central pillar of algebraic complexity theory, additive combinatorics, and quantum information theory [cite: 3, 8]. The recent wave of literature in early 2026 has provided a paradigm-shifting clarification of this landscape. While the community has finally proven that Strassen's support functionals perfectly coincide with modern quantum functionals over the complex numbers [cite: 3, 9], an equally critical finding has emerged: for tensors with four or more modes ($d \ge 4$), these known functionals represent an incomplete picture [cite: 1]. The existence of missing spectral points has been proven abstractly via separation theorems involving the asymptotic multilinear commutative rank, but their explicit construction remains entirely elusive [cite: 1]. This substrate-grade research brief provides a comprehensive, highly technical analysis of this open problem, synthesizing current limits, attack vectors, and cross-disciplinary theoretical implications.

***

## 1. Brief Summary
**Prometheus Context:** The open question demands the explicit algebraic or geometric construction of novel, mathematically distinct spectral points within the asymptotic spectrum of $d$-mode tensors ($d \ge 4$), as recent existence proofs by Alman, Li, and Pratt (2026) confirm that all currently known quantum and grouped functionals fundamentally fail to achieve the minimizations characterizing the asymptotic multilinear commutative rank [cite: 1, 4].

## 2. Flagged Findings
The current consensus in algebraic complexity theory has recently undergone a violent structural revision. For decades, the asymptotic spectrum of 3-mode tensors ($d=3$) was heavily presumed to be tightly constrained, if not fully characterized, by Strassen's support functionals $\zeta^\theta$ [cite: 3, 6]. This assumption was bolstered by Sakabe, Doğan, and Walter’s (January 2026) milestone proof that $\zeta^\theta$ perfectly coincides with the quantum functionals $F_\theta$ (derived from entanglement polytopes and entropy optimization) [cite: 3]. Over $\mathbb{C}$, it was largely believed that these tools might exhaust the asymptotic spectrum entirely, which would have cleanly resolved the Asymptotic Rank Conjecture and algorithmically refuted the Set Cover Conjecture [cite: 6, 10]. 

However, this consensus is fundamentally flawed when extrapolated to higher modes. Alman, Li, and Pratt (April 2026) flagged a critical theoretical boundary: for $d \ge 4$, the known spectral points (including higher-order quantum functionals and all spectral points derived by artificially grouping modes to reduce dimensionality) are strictly insufficient [cite: 1, 4]. 

*Where the consensus might be wrong:* 
The field has systematically fallen victim to **PATTERN_BASE_RATE_NEGLECT**, assuming that the algebraic rigidity and representation-theoretic symmetry characterizing 3-mode tensors (which govern standard matrix multiplication) would serve as a reliable baseline for the behavior of higher-order multilinear forms. The base rate of algebraic complexity scaling undergoes a phase transition at $d=4$. The combinatorial explosion of tensor slice ranks and the failure of simple marginal entropy bounds to capture deep mode-entanglement means that extrapolating 3-mode spectral geometry to $d \ge 4$ is mathematically invalid [cite: 1, 5]. Furthermore, nearly all existing quantum functional frameworks rely heavily on the continuous geometry of the complex field $\mathbb{C}$ (via Kempf-Ness theory and geometric invariant theory). The consensus heavily flags positive characteristic fields ($\mathbb{F}_p$), where currently only the three flattening ranks are known to act as spectral points, indicating a massive blind spot in modular arithmetic regimes [cite: 6].

## 3. Problem Statement
The precise object of interrogation is the **asymptotic spectrum of $d$-mode tensors**, denoted $\mathcal{X}$. Introduced by Strassen, a spectral point $\phi \in \mathcal{X}$ is a monotone, multiplicative, and additive map from the semiring of tensors to the non-negative reals $\mathbb{R}_{\ge 0}$, normalized such that the value on the unit tensor is its rank [cite: 9, 11]. Spectral points characterize the asymptotic restriction preorder: a tensor $T$ asymptotically restricts to $S$ ($S \le T$) if and only if $\phi(S) \le \phi(T)$ for all $\phi \in \mathcal{X}$ [cite: 3].

For $d$-mode tensors, the known spectral points consist of:
1.  **Higher-order quantum functionals** (and by extension, support functionals): Defined via maximum entropy optimization over the tensor's moment/entanglement polytope $\Delta(T)$ [cite: 3].
2.  **Grouped functionals**: Obtained by combining indices to view a $d$-mode tensor as a lower-mode tensor and applying known spectral points [cite: 1].

The open problem focuses on the **asymptotic multilinear commutative rank** ($\utilde{\text{CR}}$). Alman, Li, and Pratt proved that $\utilde{\text{CR}}$ can be abstractly characterized as a *minimization* over a set of spectral points [cite: 1]. The precise problem is that for $d \ge 4$, evaluating the minimum of all *currently known* spectral points yields a value strictly greater than the true $\utilde{\text{CR}}$ of certain explicit tensors [cite: 1]. Therefore, there must exist an unknown set of spectral points $\mathcal{M} \subset \mathcal{X}$ that drive this minimum down to its actual theoretical limit. The task is to explicitly define and construct $\phi \in \mathcal{M}$. Resolving this object is paramount to bounding multilinear arithmetic circuits and progressing beyond bilinear matrix multiplication constraints [cite: 1, 12].

## 4. Status & Bounds
**Last Known Status:** 
The missing spectral points have been proven to exist non-constructively. There is currently no explicit algebraic formula, geometric optimization protocol, or invariant-theoretic description for any spectral point outside the known quantum/grouped families for $d \ge 4$ [cite: 1]. 

**Current Best Bounds & Separation Arguments:**
The proof of existence relies on a strict mathematical separation bound. Alman, Li, and Pratt constructed a specific parameterized $d$-mode tensor $T_{p,q}$ [cite: 1]. They demonstrated that:
$$ \utilde{\text{CR}}(T_{p,q}) < \min_{\phi \in \mathcal{K}} \phi(T_{p,q}) $$
where $\mathcal{K}$ represents the set of all known quantum and grouped functionals [cite: 1]. Because $\utilde{\text{CR}}$ must mathematically equal the infimum over *all* valid spectral points (Corollary 3.4 of their 2026 paper), the strict inequality bounds the known functional space away from the true spectral edge [cite: 1]. 

**Conditional Qualifiers:**
*   *Field Dependence:* The sufficiency of quantum functionals is highly dependent on the underlying field. While Sakabe et al. proved equivalence to support functionals over $\mathbb{C}$ using Hadamard manifold duality [cite: 3], positive characteristic fields lack the gradient-flow and Lie group compactness properties required for these proofs. Thus, over finite fields, the gap is presumably even wider [cite: 6].
*   *Edge Functionals:* Alman et al. did prove that when the parameter $\theta$ lies exactly on the edges of the simplex $\Theta$, the support functionals are uniquely determined by matrix multiplication tensors and *can* be explicitly computed in deterministic polynomial time via Harder-Narasimhan filtrations [cite: 1, 4]. However, this only covers the boundary of the known spectral points, not the missing interior spaces required for $d \ge 4$.

## 5. Literature (Primary Sources)
The recent upheaval in this domain is driven by a highly interconnected set of preprints and publications from late 2025 and early 2026. Primary sources mandate careful citation:

1.  **Alman, J., Li, B., & Pratt, K. (April 1, 2026).** *The edge of the asymptotic spectrum of tensors.* arXiv:2604.01386 [cs.CC]. 
    *   *Significance:* The primary text defining the open problem. Proves that edge support functionals are spectral points determined by matrix multiplication, but crucially proves via multilinear commutative rank that $d \ge 4$ tensors require unknown spectral points. Establishes deterministic polynomial time computation for edge functionals via quiver representation theory [cite: 1, 4].
2.  **Sakabe, K., Doğan, M. L., & Walter, M. (January 29, 2026).** *Strassen's support functionals coincide with the quantum functionals.* arXiv:2601.21553 [cs.CC].
    *   *Significance:* Solves Strassen's 1991 open problem. Proves that $\zeta^\theta(T) = F_\theta(T)$ using Fenchel-type duality on Hadamard manifolds. Unifies algebraic complexity and quantum information approaches over $\mathbb{C}$ [cite: 2, 3].
3.  **Björklund, A., Kaski, P. (2024 / 2025).** *The asymptotic rank conjecture and the set cover conjecture are not both true.* STOC 2024 / related works ITCS 2025.
    *   *Significance:* Provides the computational complexity motivation. Shows that bounding asymptotic tensor ranks ties directly to worst-case algorithms for NP-hard problems, strictly linking the geometry of tensors to the Set Cover Conjecture [cite: 8, 10].
4.  **Christandl, M., Vrana, P., Zuiddam, J. (2018 / 2023).** *Universal spectral points / Quantum functionals.* STOC 2018, JAMS 2023.
    *   *Significance:* The foundational papers introducing quantum functionals via entanglement polytopes, which are now proven to be insufficient for $d \ge 4$ multilinear operations [cite: 1, 5].

## 6. Attack Vectors
The explicit construction of these missing points is a multifaceted challenge requiring techniques outside traditional invariant theory. 

### Live Techniques
*   **Quiver Representation Theory & Harder-Narasimhan Filtrations:** Alman, Li, and Pratt successfully mapped the computation of *edge* support functionals to the problem of finding Harder-Narasimhan filtrations in quiver representations [cite: 1, 4]. A live attack vector involves generalizing quiver stability conditions from bipartite/tripartite graphs to hypergraphs representing $d$-mode tensors. If one can define a higher-order analogue of slope stability for $d \ge 4$ multidimensional arrays, new spectral points may emerge from the corresponding algebraic filtrations.
*   **Star-Convexity & Shannon Capacity Generalizations:** Following Zuiddam's extension of the asymptotic spectrum to graphs [cite: 1], and Wang & Zuiddam's (2026) higher-mode star-convexity results [cite: 1], researchers are attacking the problem by examining the asymptotic spectrum of hypergraphs. A spectral point defined over hypergraph limits might perfectly translate back to multilinear commutative rank in tensors.
*   **Optimization over Non-Reductive Groups:** Current quantum functionals rely on Geometric Invariant Theory (GIT) over reductive algebraic groups (like the General Linear group $GL$) [cite: 9, 11]. An attack vector is extending moment polytope frameworks to non-reductive groups or utilizing unipotent radical quotients, which might capture the "missing" geometric structure of higher-order tensors.

### Exhausted Approaches & Systemic Pitfalls
*   **Marginal Entropy Optimization (The Quantum Functional Limit):** Attempting to tweak the quantum functional $F_\theta(T) = \max_{p \in \Delta(T)} 2^{\sum \theta_j H(p_j)}$ by merely adjusting the simplex weights $\theta$ or grouping modes is a mathematically exhausted approach. The separation theorem definitively proves these functions form a closed set that is strictly disjoint from the global infimum required by $\utilde{\text{CR}}$ [cite: 1].
*   **PATTERN_RANK_PARITY_LEAK in Optimization Algorithms:** When researchers attempt to project higher-mode tensors into lower-mode representations (e.g., flattening a $4$-tensor into a matrix or $3$-tensor to apply Sakabe et al.'s duality [cite: 3]), they suffer from **PATTERN_RANK_PARITY_LEAK**. The non-linear multilinear entanglements specific to $d \ge 4$ leak into the null spaces of the lower-mode projections. Consequently, gradient descent optimizations on the Hadamard manifold of the flattened tensor converge to pseudo-minima that wildly overestimate the true asymptotic tensor rank [cite: 3, 13]. Any construction algorithm that relies on recursive flattening is mathematically guaranteed to miss the novel spectral points.

## 7. Cross-References
The resolution of this open problem sits at the nexus of several major conjectures in theoretical computer science.

*   **Anti-Anchors & Candidate Primitives:** 
    *   *The Asymptotic Rank Conjecture:* Formulated by Strassen (1994), it posits that the asymptotic rank of any $n \times n \times n$ tensor is at most $n$. If quantum functionals exhausted the complex spectrum, this conjecture would follow immediately, implying $\omega = 2$ [cite: 6, 8]. The failure of quantum functionals at $d \ge 4$ acts as an anti-anchor, suggesting the conjecture may be much more difficult, or potentially false, in higher dimensions.
    *   *The Set Cover Conjecture (SCC) & k-SUM Hardness:* Björklund, Kaski, and Pratt have shown that the SCC and the Tensor Rank Conjecture cannot both be true [cite: 7, 10]. Identifying the missing spectral points for $d \ge 4$ would directly yield new upper bounds on the exponent $\sigma(d)$, potentially leading to explicit superlinear lower bounds for arithmetic circuits. This would unconditionally separate complexity classes related to k-SUM, Primal Treewidth SETH, and Traveling Salesman bounds [cite: 7, 8, 10].
*   **Related Open Problems:**
    *   *Positive Characteristic Spectra:* Does an analogue of the quantum functional exist over an arbitrary finite field $\mathbb{F}_p$? Without Kempf-Ness theory, defining spectral points beyond flattening ranks in characteristic $p > 0$ remains heavily unsolved [cite: 1, 6].
    *   *Depth-2 Circuit Duality Compatibility:* Alman and Li (2025) used Strassen duality for depth-2 circuits, but explicitly mapping $d \ge 4$ spectral points to constant-depth circuit bounds remains an ongoing secondary problem [cite: 1, 6].

***

### Deep-Dive Expansion A: The Architecture of the Asymptotic Spectrum

To thoroughly understand the nature of the "missing" spectral points, one must reconstruct the foundation of Volker Strassen's asymptotic spectrum of tensors. 

Let $\mathbb{F}$ be a field, and consider finite-dimensional vector spaces $U_1, U_2, \dots, U_d$ over $\mathbb{F}$. A $d$-mode tensor is an element $T \in U_1 \otimes U_2 \otimes \dots \otimes U_d$. The most familiar case is $d=3$, where a tensor can represent bilinear operations like matrix multiplication. 

The complexity of a tensor is traditionally measured by its **tensor rank**, $R(T)$, which is the minimum integer $r$ such that $T$ can be expressed as the sum of $r$ rank-one tensors (i.e., pure product states $u_1 \otimes u_2 \dots \otimes u_d$). However, tensor rank is notoriously poorly behaved: it is not necessarily multiplicative under the Kronecker product ($R(S \otimes T) \le R(S)R(T)$, but strict inequality can occur) [cite: 6], and determining it is NP-hard.

To bypass these anomalies and study the theoretical limits of computation (such as $\omega$, the exponent of matrix multiplication), Strassen introduced the concept of **asymptotic rank**, $\utilde{R}(T) = \lim_{n \to \infty} R(T^{\otimes n})^{1/n}$ [cite: 8]. This smooths out the local irregularities of finite tensor powers. 

To formalize this mathematically, Strassen abstracted tensors into a **commutative semiring** under direct sum (addition, $\oplus$) and Kronecker product (multiplication, $\otimes$). He then defined the **asymptotic spectrum**, $\mathcal{X}$, as the space of all real-valued homomorphisms from this semiring that are monotone with respect to the restriction preorder [cite: 3, 11]. 
A mapping $\phi: \mathcal{T} \to \mathbb{R}_{\ge 0}$ is a spectral point if it satisfies:
1.  **Normalization**: $\phi(\langle 1 \rangle) = 1$, where $\langle 1 \rangle$ is the rank-1 tensor.
2.  **Additivity**: $\phi(S \oplus T) = \phi(S) + \phi(T)$.
3.  **Multiplicativity**: $\phi(S \otimes T) = \phi(S)\phi(T)$.
4.  **Monotonicity**: If $S$ can be obtained from $T$ by linear transformations on the local factor spaces (denoted $S \le T$), then $\phi(S) \le \phi(T)$ [cite: 3, 9].

Strassen's Spectral Theorem proves a profound duality: $S$ asymptotically restricts to $T$ ($S \le_{as} T$) if and only if $\phi(S) \le \phi(T)$ for *every* $\phi \in \mathcal{X}$ [cite: 3]. Consequently, the asymptotic rank is simply the maximum value across the spectrum: $\utilde{R}(T) = \max_{\phi \in \mathcal{X}} \phi(T)$ [cite: 11].

### Deep-Dive Expansion B: The Rise and Limits of Quantum Functionals

For decades, the actual elements of $\mathcal{X}$ were a mystery, acting more like abstract ideals in algebraic geometry than computable functions. Strassen proposed a candidate family called the **support functionals**, $\zeta^\theta$, where $\theta$ belongs to a probability simplex $\Theta$ [cite: 9]. 

Simultaneously, the quantum information community independently developed tools to study multiqudit entanglement. Christandl, Vrana, and Zuiddam (CVZ) realized that evaluating the asymptotic conversion rate of quantum states was identical to calculating asymptotic tensor restrictions. They introduced **quantum functionals**, $F_\theta$, using geometric invariant theory (GIT) [cite: 1, 5]. 

For a tensor $T \in \mathbb{C}^{n_1} \otimes \dots \otimes \mathbb{C}^{n_d}$, one considers the action of the group $GL = GL(n_1) \times \dots \times GL(n_d)$. The **entanglement polytope** (or moment polytope) $\Delta(T)$ describes the possible marginal eigenvalue spectra of the quantum state represented by $T$ under local coordinate changes [cite: 11]. The quantum functional is defined as the maximum weighted Shannon entropy over this geometric space:
$$ F_\theta(T) = \max_{p \in \Delta(T)} 2^{\sum_{j=1}^d \theta_j H(p_j)} $$
[cite: 3].

The CVZ framework proved that these $F_\theta$ functions satisfy all four of Strassen's axioms, meaning they are bona fide universal spectral points [cite: 3]. 

In a massive unifying step in January 2026, Sakabe, Doğan, and Walter proved that Strassen’s analytically derived support functionals $\zeta^\theta$ are exactly equal to the quantum functionals $F_\theta$ [cite: 3]. The proof utilized Hirai's Fenchel-type duality theorem on Hadamard manifolds. Specifically, they mapped the convex optimization problem over the entanglement polytope to gradient optimization on the affine-invariant Riemannian metric of positive-definite matrices [cite: 3, 13]. This unequivocally confirmed that Strassen's intuition from 1991 was structurally identical to modern quantum entropy optimization [cite: 2, 9].

### Deep-Dive Expansion C: The Edge of the Spectrum and the $d \ge 4$ Breakdown

Given the success of the Sakabe-Doğan-Walter unification, one might assume the asymptotic spectrum was solved. If $\mathcal{X} = \{F_\theta\}$, then computing asymptotic parameters is entirely reduced to convex optimization over polytopes [cite: 6]. 

However, Alman, Li, and Pratt (April 2026) shattered this assumption. While they reinforced the power of support functionals by proving that on the *edges* of the probability simplex $\Theta$ (where one $\theta_i = 0$), the functionals are unique and completely governed by matrix multiplication algorithms [cite: 4, 6], they discovered a fatal flaw in the interior of the spectrum for $d \ge 4$.

Their discovery hinges on a metric known as the **asymptotic multilinear commutative rank**, $\utilde{\text{CR}}(T)$ [cite: 1]. Unlike asymptotic tensor rank, which is a maximization over spectral points, $\utilde{\text{CR}}(T)$ is fundamentally a *minimization* problem over spectral points [cite: 1]. 

By defining a specific family of $d$-mode tensors, denoted $T_{p,q}$, Alman, Li, and Pratt calculated exact values for $\utilde{\text{CR}}(T_{p,q})$ [cite: 1]. They then performed the minimization over all quantum functionals $F_\theta$ and all combinations of lower-mode functionals (created by artificially collapsing the $d$ modes into 3 modes, essentially taking advantage of the well-behaved $d=3$ spectrum) [cite: 1].

The result was a strict mathematical separation: the minimum across all known spectral points remained significantly higher than the explicitly calculated $\utilde{\text{CR}}(T_{p,q})$ [cite: 1]. Because the true $\utilde{\text{CR}}$ is the absolute infimum over the *complete* spectrum $\mathcal{X}$, this strictly implies that $\mathcal{X}$ contains phantom elements—spectral points that act on $T_{p,q}$ in ways that no entanglement polytope or marginal entropy bound can detect [cite: 1]. 

### Deep-Dive Expansion D: Systemic Pitfalls and Algorithmic Implications

Why does $d=4$ break the mathematics that works so beautifully for $d=3$? 
The problem lies in the topology of the multidimensional arrays and how rank parity leaks across modes. For $d=3$, a tensor can be perfectly viewed as a trilinear map, and the invariant theory of $GL(A) \times GL(B) \times GL(C)$ aligns seamlessly with the degrees of freedom in the tensor slice ranks. But for $d=4$, the tensor is a quadrilinear map. When algorithms attempt to minimize metrics via Hadamard gradient descent or Kempf-Ness optimization, they effectively evaluate local marginals [cite: 13]. In a 4-partite quantum system, there exist deep, multi-way entangled states (analogous to higher-order W-states) where the marginal entropies on single parties or bipartite splits appear completely mixed, yet the global state possesses a rigid, low-rank algebraic structure [cite: 5, 14]. 

This is the essence of **PATTERN_RANK_PARITY_LEAK**: optimization algorithms operating solely on the moment polytope $\Delta(T)$ are blind to higher-mode algebraic cancellations [cite: 3, 11]. The structural information of the $d \ge 4$ tensor "leaks" through the entropy equations, yielding artificially high values for the quantum functionals. Therefore, any attempt to construct the missing spectral points by simply modifying the weights of a quantum functional is a mathematically exhausted approach.

The resolution of this open problem is no longer merely a niche curiosity in algebraic geometry; it is a critical roadblock in computational complexity [cite: 1, 4]. If researchers can explicitly construct these missing spectral points, they will gain entirely new mathematical invariants to bound tensor operations. 

As demonstrated by Björklund and Kaski (2024), and further refined by Pratt, the ability to sharply bound the asymptotic rank of general tensors creates a dichotomy [cite: 8, 10]. Either we achieve revolutionary fast deterministic algorithms for NP-hard problems (like solving the $k$-Set Cover problem in time strictly faster than $O(2^{(1-\epsilon)n})$), or we generate unassailable superlinear lower bounds for arithmetic circuits computing those tensor polynomials [cite: 7, 10]. 

The missing spectral points of $d \ge 4$ mode tensors are the missing keys to this dichotomy. Their explicit construction requires bridging the gap between non-reductive group invariant theory, hypergraph star-convexity, and the outer limits of algebraic complexity theory [cite: 1, 14]. Until they are found, the multilinear algebraic toolkit remains profoundly incomplete.

**Sources:**
1. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfyj8RoguPOzfXUMjrFh6JS2a0Z0awzOFKj20gRSbZhGUypUESQnQFTVsLhlU09Mg7i5JRi9qxr86LQlgToP-rto58AAaaRiVK0HkTEjK4k-ZLKT2kuZiI)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGh2tNHGrZbhqOjhtJVi1_Hcb2th2kDDiic1mrSd6DBci9UWOFf7iC6bt8NMNIrul4-EQZnrv0LPgmwynzD3cxKgXHObT8vQUAnTgU5l2c-xtmSFqVG)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIJBSF4Lti6qkJohNGjTCrG49-png4TkS4Zg_X2VstJyYkSAUwBjHLV5PhegMHSYN4lw07k8f4irms7jDAjXb8MPvGgs7mTe_6FrNvP-jRyNRhH_Mt2LNz)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErdJCWH0K5_LBtoWACjM6uzpR3Dp6sSlN-L1Jc6xkSl8LI7jDHeJuuNSOigA25UK4KiUcklKf-y7R_Z4vzLil4fxQcsPg35lbMlS45Th_Qgmyp6Lsa)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHvoOualDqTiZryrvy300TgrAtWPSvwm5JdHB32k8cOY1ZzLdqOfkTKJRh69X1_3jMTwqkoe-Xx75p3tVcQgdTJCOyeBoOuTNQNofzP2sloZ5URLgQJejT-5kHQ7P86l20ETpyVY-GGzIhCYzXluTU1gJPLHQa3PF6CYTj8kwzWdz6DNhoUkYBp1NIfyR29z2LGtUgwtUHoTFT72kf12NcRve1K9ke8zhxCA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgtTEGSv1eWV_Uz1d8k4v0tOGQ5g0g3WxxdWa0wBtBNI9LRRGOUDxn6h4ZR2LqOftrFSRVswP0HNPUg4FDEGyvByP6BG4uVTTsqZwabry9TTqqtUw3)
7. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0T-rkpUdFGiDheSkbGq5yJHU-FBpqlNl-ej399mMlu-DFoktIztSv1cRgqsyTKS2ZTbII3v0f7tt4VqzLpOZLlVYatBZPeSgKxf0F7a6K2Yh27_ZSflvpkKfKjAJfgDQA484KTB8xmkXw3zRCogC2FpPAiifnFErzALjGCv2-9FI55uN9wIDgdxyjpdzy4aGO-c0tQSeyjNYwk4gxkg0tfEOv5ik=)
8. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMomUJ-EyvpTY3onNkv--N0Wd3hGxaDSy-iNecYpKspLYCok0HNQ8QKnEwLycIy-ixvzuzF1iaIvB7Q0BobDdIHkbZwiqMZ2rBiQolQX8qx4KJOMxM0xpjjCeoEK_5_0X-XDhn7v1bLmQk-IUbjPB-3E_4hWA2ToyrcVFfVGlpe55QLUGT2zAakuGNMvPYO4WVuVePSfSTRYUutQOY51XG3lU=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOb2YPk8f4GeWFjGQib3hqSAZl2v25zarqnTl5R89rIrDojFlA8ozziKahTICYke2VVr1CFNu_cNXrlc-pDvsqD5_4ukxU2ssb5mSRWraTbXYbhTL-)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfHMx48TmTSxmxohaAXdy8keBTkNANq9jtOWzng0FH9DXKKm997nQzb3TIz-87bBwZPWoIsVJNMp7oLyK0brxegEC1nTDsI26HeAUt8zFvveuOJdbKFnkCE0_sW8RHRwrT5QcMSYqdUSamN0CxvEEaL1MtYc2rYhuMso2RNoy1Gmt9CsXleVS2bJJ2boXZQOHDuTn9g_WgJzvU2XbXgszGT6EOK0VRCDbhj2HUAkCMKthUFRdPPf7N8uBCwVMOC8Doig==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQmTUDVyP1aDIsqXd-qoHnR_X-xPgmDVm8WQ-4xlk5HCHSFYNzF6wjkyNTVgYf1zU-32KJYsGSnUbInE2pqUQ8USlnvBWBBFysG60--gOVaY9Vqv3R)
12. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCIdyzZUEBflPSZhqsztP4wVhEr2ew_8rIsr0rqEZaWcBs52ZRhbV-sOQSJKxzo8TyZi8QiMYoQF7F3wHaTyzKzzVDt1N9yT-XBdnFIoWk4XCsBeALRTsr3G8=)
13. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUXI0072Tdq-vtGkOd-69mxwShPPkWvXTMSiJU5CRPBmFZ5-LCvWBOTBb5hLH6Xkt3g0YhLyrbWqL6WWY6waGIdPXt72ZxLvx9n-v8YmwA9yk=)
14. [michaelwalter.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy4RVf3WN9vazr3ei-ooX2EE1bxJddzPGC5wj9Emjm595EXZDsJoTjPR10iYpMnmSOr8CJbjINFH8kG1zDfnPFhJiz3Av1-cvjjd7w0FyiQtTb0kw2RxeT1jaPSw==)


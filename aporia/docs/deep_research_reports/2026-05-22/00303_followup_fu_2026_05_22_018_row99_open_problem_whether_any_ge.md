# Followup [FU-2026-05-22-018 <- row99]: *   **Open Problem:** Whether any general, polynomial-time algorithm can approximate the tensor rank

**Pythia queue id:** 303
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiYk1QYXAzQkpLVzZfdU1Qdm82cThBURIXYmJNUGFwM0JKS1c2X3VNUHZvNnE4QVE
**Elapsed:** 249s
**Completed at:** 2026-05-22T01:41:59.655611+00:00

---

# Substrate-Grade Research Brief: The Hardness of Constant-Factor Approximation for Tensor Rank

### Key Points
*   **Current Hardness Bound:** Research indicates that approximating the rank of a 3-tensor over any field to within a factor of $1 + 1/1852 - \delta$ is NP-hard.
*   **The Open Problem:** It remains unknown whether any general, polynomial-time algorithm can approximate tensor rank within *any* arbitrary constant factor, or if the hardness bound can be extended to all constants (or beyond).
*   **Algorithmic Void:** While matrix rank is computable in polynomial time via Gaussian elimination, tensor rank lacks even a reliable, worst-case constant-factor approximation algorithm in polynomial time.
*   **Conditional Lower Bounds:** Under the Exponential Time Hypothesis (ETH), evidence suggests that tensor rank cannot be approximated within some strictly bounded constant $c_0$ in polynomial time. 
*   **Alternative Paradigms:** Because exact rank is intractable, the field leans toward bicriteria approximations and relative-error low-rank approximations (using the Frobenius norm) as practical workarounds.

### Executive Overview
This report addresses a fundamental open problem in theoretical computer science and multilinear algebra: the approximability of the tensor rank integer. While the rank of a matrix (a 2-tensor) is easily computable, the generalization to 3-tensors fundamentally shifts the computational complexity landscape. Current consensus, built upon foundational proofs by Håstad and recently refined by Swernofsky, establishes that computing tensor rank is NP-hard, and more specifically, approximating it within a specific minimal constant factor ($1 + 1/1852 - \delta$) is also NP-hard. However, the upper bounds of this inapproximability are not yet understood. 

This brief synthesizes the current literature to explore the bounds of tensor rank approximation. It investigates the mechanical differences between matrices and tensors that drive this complexity gap, explores the implications for fields ranging from algebraic complexity theory to quantum information, and catalogs the exhausted attack vectors and active theoretical fronts. The report is structured to provide an exhaustive survey of the problem statement, the known algorithmic limitations, and the cryptographic and computational barriers that prevent the resolution of this open question.

***

## 1. Brief Summary

**The Open Question:** *Whether any general, polynomial-time algorithm can approximate the tensor rank integer within any arbitrary constant factor remains a major open problem in theoretical computer science.*

**Prometheus Context:** Surfaced as a follow-up to a prior Gemini Deep Research report (ref: `aporia/docs/deep_research_reports/2026-05-21/00099_t_57_constant_factor_approximation_algorithms_for_tensor_ran.md`), this problem interrogates the boundary between tractable linear algebra and intractable multilinear algebra. The failure to find a general approximation algorithm for tensor rank limits advancements in bilinear circuit complexity (such as optimizing the matrix multiplication exponent $\omega$), quantum state entanglement classification, and high-dimensional data compression. The context demands a rigorous parsing of whether the gap between $1 + 1/1852$ and an arbitrary constant $C$ is an artifact of current reduction techniques (specifically from bounded occurrence SAT variants) or indicative of a fundamental structural resistance inherent to higher-order arrays.

## 2. Flagged Findings

### 2.1 The Current Consensus on Inapproximability
The theoretical computer science community currently agrees that determining the exact rank of a tensor over a field has the same complexity as deciding the existential theory of that field [cite: 1, 2]. Furthermore, it is strictly NP-hard to compute the rank of a 3-dimensional tensor over any finite field [cite: 1, 3], and it is complete for the existential theory of the reals ($\exists \mathbb{R}$) over $\mathbb{R}$ [cite: 4, 5]. 

The most precise consensus regarding *approximation* originates from Swernofsky (2018), who proved that approximating the rank of a 3-tensor to within a factor of $1 + 1/1852 - \delta$ (for any $\delta > 0$) is NP-hard over any field [cite: 6, 7]. This is achieved via a sophisticated reduction from bounded occurrence 2-SAT, a refinement of Håstad’s original NP-completeness proof which utilized 3-SAT [cite: 7]. Independently, Bläser et al. derived a similar hardness of approximation result, though without an explicit constant [cite: 7]. Furthermore, assuming the Exponential Time Hypothesis (ETH), Song et al. demonstrated that there is some absolute constant $c_0 > 1$ such that tensor rank cannot be approximated within a factor of $c_0$ in polynomial time [cite: 7, 8].

### 2.2 Where the Consensus Might Be Wrong
The strict focus on specific small constant factors (like $1/1852$) may be an artifact of the reduction methodologies rather than a true reflection of the tensor rank's approximation hardness landscape. 
*   **Underestimation of Hardness:** It is highly probable that the true hardness of approximation extends far beyond a small constant factor. Some researchers hypothesize that tensor rank might be hard to approximate within *any* constant factor, or potentially even within a polynomial factor (similar to the hardness of the Maximum Clique problem). The current barrier is the limitation of Probabilistically Checkable Proofs (PCP) when translated through the algebraic structure of tensors via slice elimination [cite: 7].
*   **The PATTERN_PRIME_GRAVITATIONAL_OVERFIT:** A persistent theoretical blind spot in this domain is `PATTERN_PRIME_GRAVITATIONAL_OVERFIT`, where algorithmic theorists attempt to map the well-behaved spectral properties of matrices (2-tensors) onto 3-tensors. Because matrices admit optimal low-rank approximations via the Singular Value Decomposition (Eckart-Young-Mirsky Theorem) and Gaussian elimination, researchers repeatedly overfit their hypotheses to expect that a generalized form of alternating least squares or spectral sketching will eventually yield a constant-factor bound for exact tensor rank. This ignores the non-convex geometry of tensor spaces, leading to an over-optimistic assessment of potential polynomial-time approximation heuristics.
*   **Failure of the Algebraic Variety Closure:** The consensus often sidesteps the topological nightmare of "border rank." A tensor $T$ has border rank $r$ if it can be approximated arbitrarily closely by tensors of exact rank $r$. Because the set of tensors of rank $\le r$ is not closed for $r \ge 2$, best low-rank approximations often do not exist—a tensor may degenerate infinitely without reaching the infimum [cite: 9, 10]. Therefore, assuming that an approximation algorithm could bound the *exact* rank integer ignores that the integer itself can behave erratically across arbitrarily small $\epsilon$-perturbations in the tensor's entries.

## 3. Problem Statement

### 3.1 Mathematical Definition of the Object
The precise object being interrogated is the **Tensor Rank** (often referred to as the Canonical Polyadic or CP rank) of a 3-dimensional tensor. 

Let $\mathbb{F}$ be an arbitrary field. A 3-tensor $T$ is an element of the tensor product space $U \otimes V \otimes W$, where $U, V, W$ are vector spaces over $\mathbb{F}$ of dimensions $n_1, n_2, n_3$, respectively. In coordinate form, $T$ is represented as a 3-dimensional array $T \in \mathbb{F}^{n_1 \times n_2 \times n_3}$.

A tensor $T$ is said to be of **rank 1** if it can be expressed as the outer product of three non-zero vectors $u \in U, v \in V, w \in W$. That is, $T = u \otimes v \otimes w$, meaning its $(i, j, k)$-th entry is given by $T_{ijk} = u_i v_j w_k$ [cite: 7, 10, 11].

The **tensor rank** of $T$, denoted as $\text{rank}(T)$, is defined as the minimum integer $r$ such that $T$ can be expressed as the sum of $r$ rank-1 tensors:
$$ \text{rank}(T) = \min \left\{ r \in \mathbb{N} \mid T = \sum_{i=1}^r u_i \otimes v_i \otimes w_i \right\} $$
This decomposition is frequently referred to as the Canonical Polyadic Decomposition (CPD) or CANDECOMP/PARAFAC decomposition [cite: 10, 12].

### 3.2 The Approximation Task
Given a tensor $T \in \mathbb{F}^{n_1 \times n_2 \times n_3}$ and an arbitrary constant $C \ge 1$, an algorithm $\mathcal{A}$ is said to be a $C$-approximation algorithm for tensor rank if it outputs an integer $R_{\text{approx}}$ in polynomial time such that:
$$ \text{rank}(T) \le R_{\text{approx}} \le C \cdot \text{rank}(T) $$
The interrogative statement—whether *any* general, polynomial-time algorithm can approximate the tensor rank integer within *any* arbitrary constant factor $C$—challenges the computational complexity community to find either:
1. A polynomial-time algorithm that satisfies the above inequality for some constant $C > 1$, or
2. A mathematical proof (likely via PCP and gap-preserving reductions) that no such algorithm exists for *any* constant $C$, assuming $P \neq NP$.

### 3.3 Distinguishing from Relative Error Matrix Approximation
It is critical to distinguish this problem (approximating the *integer* rank of a tensor) from "relative error low-rank approximation" of the tensor's entries. The latter seeks a tensor $B$ of fixed rank $k$ such that $\|A - B\|_F^2 \le (1+\epsilon) \min_{\text{rank}(A') \le k} \|A - A'\|_F^2$ [cite: 13, 14]. While Song, Woodruff, and Zhong have made significant progress in relative error Frobenius norm approximations using sketching techniques (often yielding bicriteria bounds where the rank of $B$ is allowed to exceed $k$), these methods do *not* approximate the actual canonical tensor rank integer of the original tensor [cite: 14, 15]. Computing the exact rank remains fundamentally necessary for applications like determining minimal bilinear circuit complexity, where the rank integer exactly equals the number of required non-scalar multiplications [cite: 7, 16].

## 4. Status & Bounds

### 4.1 Last Known Status
The status of the open problem is **unresolved but heavily constrained from below**. 
No general, polynomial-time algorithm is known that can approximate the tensor rank integer to within an arbitrary constant factor $C$. Conversely, no proof exists showing that approximation within *large* constant factors (e.g., $C = 100$) is NP-hard.

### 4.2 Current Best Lower Bounds
The most stringent lower bound on approximability is $1 + 1/1852 - \delta$. 
*   **Swernofsky (2018):** Through a re-analysis and simplification of Håstad's 1990 reduction, Swernofsky demonstrated that it is NP-hard to approximate 3-tensor rank over any field $\mathbb{F}$ within a factor of $1 + 1/1852 - \delta$ [cite: 1, 6, 7]. The reduction maps instances of bounded occurrence 2-SAT into a tensor $T$. The structure of the proof ensures that if the SAT formula is satisfiable, the tensor rank is tightly bounded, but if unsatisfied clauses remain, significant "extra rank" is guaranteed [cite: 7, 11].
*   **Exponential Time Hypothesis (ETH) Bound:** Song et al. [cite: 7, 8] proved that assuming ETH, there is *some* constant $c_0 > 1$ such that tensor rank cannot be approximated within a factor of $c_0$ in polynomial time. For the related problem of outputting a rank-$k$ tensor minimizing the Frobenius error, they demonstrate a $2^{\Omega(k^{1-o(1)})}$ time lower bound [cite: 14].

### 4.3 Current Best Upper Bounds
There are virtually no meaningful, worst-case upper bounds for polynomial-time approximation. 
*   **Naive Bounds:** By dimension counting and slice decomposition, any tensor $T \in \mathbb{F}^{n \times n \times n}$ has a rank bounded trivially by $n^2$ [cite: 11]. The highest rank known for an explicit family of 3-tensors is $3n - o(n)$ [cite: 11].
*   **Algorithmic Void:** As Swernofsky explicitly states: "while we know rank is hard to compute exactly, we do not know if it can be approximated... It would also be interesting to have any nontrivial approximation algorithm" [cite: 7, 11]. There is zero known poly-time algorithm guaranteeing a constant factor approximation for the rank of an arbitrary 3-tensor. 

### 4.4 Conditional Qualifiers and Field Dependence
The hardness of computing tensor rank exhibits fascinating variations depending on the underlying field $\mathbb{F}$:
*   Over finite fields: Exact computation is NP-complete [cite: 1, 3, 17].
*   Over $\mathbb{Q}$ (Rational numbers): Exact computation is NP-hard, and the problem is intimately tied to the undecidability of Diophantine equations (Hilbert's Tenth Problem). Tensor rank over $\mathbb{Z}$ is fundamentally undecidable [cite: 2, 5].
*   Over $\mathbb{R}$ and $\mathbb{C}$: Exact computation is NP-hard [cite: 5, 17]. Furthermore, Schaefer and Štefankovič demonstrated that determining tensor rank over a field has the precise same complexity as deciding the existential theory of that field ($\exists \mathbb{F}$) [cite: 1, 2, 4]. This equates the complexity of real tensor rank to classic $\exists \mathbb{R}$-complete geometric problems like oriented matroid realizability and the art gallery problem [cite: 4, 5].
Despite these deep field dependencies for *exact* computation, Swernofsky's *inapproximability* bound of $1 + 1/1852 - \delta$ holds broadly over any field, derived fundamentally from combinatorial Boolean satisfiability architectures independent of the field's algebraic geometry [cite: 1, 6].

## 5. Literature (Primary Sources)

The body of literature establishing the hardness of tensor rank and its approximation is highly specialized. The following are the critical primary sources dictating the boundaries of this problem:

1.  **Joseph Swernofsky (2018).** *Tensor Rank is Hard to Approximate.*
    *   **Venue:** Approximation, Randomization, and Combinatorial Optimization. Algorithms and Techniques (APPROX/RANDOM 2018), Leibniz International Proceedings in Informatics (LIPIcs), Vol. 116, pp. 26:1-26:9.
    *   **Context:** The definitive paper proving the $1 + 1/1852 - \delta$ NP-hardness bound via reduction from bounded occurrence 2-SAT. Formally surfaces the open problem regarding arbitrary constant factors.
    *   **Citation Refs:** [cite: 6, 7, 11].

2.  **Johan Håstad (1990).** *Tensor rank is NP-complete.*
    *   **Venue:** Journal of Algorithms, 11(4):644–654.
    *   **Context:** The seminal genesis paper that proved exact tensor rank is NP-complete over finite fields and NP-hard over the rationals. Established the fundamental reduction from 3-SAT to tensor slice matrices.
    *   **Citation Refs:** [cite: 3, 18].

3.  **Marcus Schaefer and Daniel Štefankovič (2016).** *The Complexity of Tensor Rank.*
    *   **Venue:** Theory of Computing Systems, 62(5): 1161-1174 (Published online 2016, print 2018).
    *   **Context:** Demonstrated that tensor rank complexity is equivalent to the existential theory of the given field. Proved that over integral domains, rank is strictly tied to solving systems of polynomial equations, cementing its geometric intractability.
    *   **Citation Refs:** [cite: 1, 2, 4].

4.  **Zhao Song, David P. Woodruff, and Peilin Zhong (2019).** *Relative Error Tensor Low Rank Approximation.*
    *   **Venue:** Proceedings of the Thirtieth Annual ACM-SIAM Symposium on Discrete Algorithms (SODA 2019). (arXiv:1704.08246).
    *   **Context:** Shifted the paradigm toward relative-error matrix-style Frobenius norm approximations. Proved under ETH that there exists a constant $c_0$ for which tensor rank cannot be approximated. Introduced bicriteria approximations with parameterized complexity to bypass NP-hardness.
    *   **Citation Refs:** [cite: 13, 14, 15].

5.  **Christopher J. Hillar and Lek-Heng Lim (2013).** *Most Tensor Problems Are NP-Hard.*
    *   **Venue:** Journal of the ACM (JACM), 60(6), Article 45.
    *   **Context:** Expanded Håstad's findings to continuous fields ($\mathbb{R}$ and $\mathbb{C}$). Systematically proved that computing spectral norm, best rank-1 approximation, and exact rank of tensors are all NP-hard. Explored the phenomenon of "ill-posedness" in continuous low-rank tensor approximation.
    *   **Citation Refs:** [cite: 5, 9, 17].

## 6. Attack Vectors

The effort to approximate tensor rank, or prove its complete inapproximability, has witnessed several distinct algorithmic and complexity-theoretic attack vectors. 

### 6.1 Exhausted Approaches
*   **Alternating Least Squares (ALS) & Optimization Heuristics:** The most common empirical method for tensor decomposition is ALS, which fixes all but one mode of the tensor and optimizes the remaining mode (reducing to standard least squares), iterating until convergence [cite: 12, 19]. 
    *   *Why it is exhausted:* ALS offers no theoretical guarantees for finding the global minimum, nor does it bound the rank integer itself. Furthermore, it suffers catastrophically from the `PATTERN_BASE_RATE_NEGLECT`—practitioners deploy ALS assuming a well-behaved continuous optimization landscape, entirely neglecting the base rate of tensor "ill-posedness." Because the set of tensors of rank $\le r$ is not topologically closed, ALS frequently diverges, with component magnitudes growing to infinity as they attempt to approximate a tensor on the boundary (border rank) [cite: 9, 10, 20].
*   **Slice Elimination:** In Swernofsky’s and Håstad’s analyses, tensors are viewed as stacks of matrix "slices". Slice elimination involves finding a rank-1 slice and subtracting multiples of it from other slices to zero out entries [cite: 7]. 
    *   *Why it is exhausted:* Unlike Gaussian elimination for matrices where reducing a row preserves the exact rank structure predictably, eliminating a slice in a 3-tensor leaves residual slices that can have rank greater than 1. This obscures the global rank [cite: 7]. Determining the optimal multiples to subtract is itself an NP-hard subproblem [cite: 7].
*   **Naive Flattening (Matricization):** This involves flattening a 3-tensor $T \in \mathbb{F}^{n \times n \times n}$ into a matrix $M \in \mathbb{F}^{n \times n^2}$ and computing the matrix rank. 
    *   *Why it is exhausted:* This introduces the `PATTERN_RANK_PARITY_LEAK`. While the matrix rank of the flattening provides a rigid lower bound on the tensor rank, it "leaks" only partial parity information about the true multilinear entanglement. A tensor can easily have a flattened matrix rank of $n$ while its true tensor rank scales quadratically, $O(n^2)$. Consequently, the matrix rank fails as a constant-factor proxy for the tensor rank [cite: 21]. 

### 6.2 Live Techniques
*   **PCP-based Gap Amplification:** To prove that tensor rank cannot be approximated within any arbitrary constant factor, complexity theorists must likely employ the PCP Theorem. Swernofsky's current bound ($1 + 1/1852$) relies on a direct translation of the gap from MAX-E2-SAT into the tensor rank via constraint satisfaction counting [cite: 7]. To enlarge this gap, researchers are actively exploring reductions from higher-arity CSPs (Constraint Satisfaction Problems) or utilizing Label Cover, similar to the techniques used by Dinur and Safra for Vertex Cover. The primary obstacle is designing a "tensor gadget" that scales the rank multiplicatively with the non-satisfiability of the PCP query without inflating the baseline rank linearly [cite: 7, 22].
*   **Bicriteria and Parameterized Sketching:** Bypassing exact integer approximation, the live vector in randomized algorithms (spearheaded by Woodruff, Song, and Zhong) utilizes polynomial-time sketching. They accept a "bicriteria" output: finding a tensor $B$ of rank $O((k/\epsilon)^{q-1})$ that approximates a target rank $k$ to relative error $(1+\epsilon)$ [cite: 14, 15]. While this does not approximate the exact tensor rank integer, it bypasses the NP-hardness by inflating the allowable rank space.
*   **Non-Trivial Flattenings (Koszul-Young):** Recent work in computational algebraic geometry uses generalized flattenings, such as Koszul-Young flattenings, to map tensors to larger matrix spaces where the rank properties are more deeply preserved. This has pushed rank detection bounds slightly higher (e.g., detecting if rank is $\le (2-\epsilon)n$), though it remains exponential in the constants [cite: 21]. 

## 7. Cross-References & Related Paradigms

The open problem of tensor rank approximation is deeply intertwined with several distinct pillars of theoretical computer science and mathematics.

### 7.1 Bilinear Circuit Complexity and Matrix Multiplication
The most famous specific instance of tensor rank evaluation is the matrix multiplication tensor, $\mu_{\langle n, m, p \rangle}$. The number of non-scalar multiplications required to multiply two matrices of sizes $n \times m$ and $m \times p$ is exactly equal to the tensor rank of $\mu_{\langle n, m, p \rangle}$ [cite: 7, 16]. 
*   **Strassen's Tensor:** Strassen’s algorithm for $2 \times 2$ matrix multiplication corresponds precisely to the discovery of a rank-7 decomposition of the $2 \times 2 \times 2$ tensor, breaking the naive rank-8 assumption [cite: 7]. 
*   **Anti-Anchor:** Despite over 50 years of research, the exact tensor rank of the $3 \times 3$ matrix multiplication tensor is still unknown, bounded loosely between 19 and 23 [cite: 7, 11]. If a constant-factor approximation algorithm existed, it could theoretically bound the asymptotic exponent of matrix multiplication ($\omega$), an outcome that currently seems computationally unattainable.

### 7.2 Border Rank and Ill-Posedness
A severe confounder in tensor approximation is **border rank**. For matrices, the set of matrices of rank $\le r$ is closed. For tensors, the set of tensors of rank $\le r$ is generally *not* closed (for $r \ge 2$). 
*   **Implication:** A rank-3 tensor can be arbitrarily well approximated by a sequence of rank-2 tensors [cite: 9, 10, 23]. The tensor rank is therefore lower semi-continuous but not continuous. Any algorithmic attempt to construct an approximate tensor rank integer must wrestle with the fact that arbitrarily small precision errors can cause the rank integer to jump discontinuously. This structural anomaly explains why optimization algorithms natively fail and suggests that arbitrary constant-factor approximations might be mathematically ill-defined without restricting the field or introducing margin conditions [cite: 23].

### 7.3 Candidate Primitives
If the community were to construct a non-trivial approximation algorithm for tensor rank, it would likely rely on alternative structural primitives:
*   **Geometric Rank:** Introduced by Kopparty, Moshkovitz, and Zuiddam, geometric rank measures the co-dimension of the algebraic variety defined by the tensor. It does not suffer from border rank issues and acts as a lower bound for standard tensor rank. However, computing it exactly is still tied to Groebner bases and remains exponential in the worst case [cite: 17].
*   **Slice Rank and Partition Rank:** Originating from additive combinatorics (the cap-set problem), these variants of rank are mathematically weaker than CP rank. They allow the tensor to be decomposed into variables separated across any partition of indices, rather than strictly rank-1 outer products. They represent a looser, potentially more tractable primitive, though exact hardness bounds for these ranks are an active area of investigation [cite: 17].

### Conclusion
The question of whether a polynomial-time algorithm can approximate tensor rank within an arbitrary constant factor stands as a formidable firewall between linear algebra and higher-order computations. Currently halted at the $1 + 1/1852 - \delta$ NP-hardness bound established by Swernofsky, the field lacks both the algorithmic heuristics to push upper bounds downward and the PCP tensor-gadgets to push lower bounds upward. Driven by the geometric pathologies of border rank and the strict constraints of the existential theory of fields, the evidence heavily leans toward the hypothesis that tensor rank integer approximation is deeply intractable, potentially inapproximable to within any constant factor under standard complexity assumptions.

**Sources:**
1. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAPdGqVBW0l-Wmifc742RvCFC4_qocXoxlO46G4qnh11Q0z-qNm1mEew0qq_o2MnXdrs0Kw3eI89spyQdxVs9LwHgmy8sU54tuX5t3A4PJotpx6D_VJWfxtezo7fcPVtN9CARCPFD_4mu6MRTA8UFCYo7hibBnozGohbFhOpKEWcbp5K2F9xIy4Z_2PnFllwYXvLUxTQA_bwowfkb4lpGDrCvRyguJzHHCh4nXja1WjNIDTRqZKO86)
2. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3fcgH7W-n8GmSulXHud-awtMU0_vAetC8Kd9zlOWjsg6SmcwKQLWGXBttXH4F6oJQ9wIkIpKngF71Ax3B9NASgg3Dk1ekldTA3dBZx5x8oWDQV2HzTEVmCRVTcMVCBVSrzyW4QjzvS6yQlqECFoU-HWNI-II=)
3. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVIypvF0xjO_H20iCGCYZXMlcHHlmc6vrli2hftoFuXanWIrNofqnyL9V5eRpR7lVHbq_FWVEvo23hlfxYztyynsDTMd_6tyrThDyb11yqpNQt1bF2g4clB-zYl688Utj-G52xzVLCkFPb3v9-TCrJ4GSsFyvOitwGUdUzqkchRldz9FE5wg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5qGs0rD34uQSv7nFB-voqqkq7GE9rQdaqJAblLOSs9tCynrRrJ2liGkA9ZGRbQrh5iTObqjjnTrahuANGyf4jLIvptud55QIAbZuY8RRxILN2Fg2w6JnNEQ==)
5. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPPTQLrWH3SejUplbfbbAXotdDkJoGy76ppnoC52v9DRzNAiaORF6WcgPHYqiNH9_LkISVPobahMt7PdfvTOc51UXk7SVLUfppiWx1Baf8dSXazrUuC-s2yFs6)
6. [rwth-aachen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkpG4ERk3uMVQMWwJNghgpJNBwCys7ZSa9uF-p9LLe5k-7JTgZmXMcAvQn50MuOsbKbI8OVJ4JZB9iqiqeje8mN0sygo7DBflptZ9bi6jTER6_aIDr8PhyHMdt8cDhxdCF7wzRJIXY1kev2RJ2HQV2OgZSubI3FrySLVrLPfMTXg==)
7. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJEKTc5fGk3hBF1XwoO95lVYUNo4EwegWOBC9Y3jwOC43h1vPn_uCfuhdUAP1wgxE3MhdzgUNKACqAOVHeZxo2EcVXYaiMBHIMYTREjqH-6dirQB5x3IfYEHO9hPr4uH08YpachHaNZ-p23B-ETPa1BlK2K7oghPNsgBunrR59f20lHvBOHcbofeJxXU3ib6zNVCI2qSSMx1eaIOskw7mX4b8IHGmAS3bELEJlSQuGXu_nZov01Q9KlQvK2O_-eg==)
8. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_qIiuSwIpZ-J-T_kryUZA2g0ERsBc86gfLRAif8Hzbk1t101vmtgbM7BvpGOU8JB0lx2Uya6TOfYz4lHnLWo7uM6RKWFIuTSa62sIPSnwkHrQmEJnIclaMZMvw2bE5sirgcEKYYcdjZMz2mITVUplZZcYh2uJ)
9. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3k8pLiemJn53EBmEYzmMv39Z8_uyACpPFP05bHLrEtXkKOpeG-gqG6uxALV6ya29MSgd6vBYCfzSbrQRwT2l8WWh8xGPwe3nf48KN2Yps0Ew3oQJg5y031L1Il--RynBml06UPQWirQ==)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFk5kPSp_nXBrcOBxvrDIGjG8_9wmwGq0NHb-Otppbf46q6i1fXO9Cv1di1_mz2SNu0SM6ZK0DkGe3JFg9Z0F4vLmgocnD8JpdFOOKQb8qT5J_qrM75rVI9uIYwO6f2F68nBI7mtL8gmxcavmuu)
11. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtSHVlNaa_qP--6Uqp0jqS5gDeAEbtdCELGG2UDjgPEQUQ6X77b8WhyTVwXmKU3eJWMLhS2L2ECvmTN-iob925__NMIUo-7Who2c4AAke3QUMoYkb-0IYLOBADq6cXTlaktifa_nkoTOelRg==)
12. [opt-ml.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkX2JdH7N9c4RqQ9Km1FD6TbIc1C2QhguhQ1eJtI5zqOdxZdGJqjHcJwG6fzxddfPYmf5ywijRbK8wkMFLkCpHAcU30Ze7GnnwEaC7hQi_DDxFmTIfOUFvhe-_VVW6dxTe0K1GyfWIyQ==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLNjwrapyD1IejRt2rNxRjhQ_VQ5Fa-kQ6elh3IPNxDf6CBAZdTggjeLypf_0PpksSPKBQl30cItJwCdSz1QVNYIm_wHvyEcmozcCkJ_WNx1O1PMapyTrxCUv6ieMkqdrk33dlq3Uq_pt9ZVxMm5EvomUsclzb7H-nfGzYGSiX7qRNijFzL2CJF7RIkA0=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-khbUoCkRJivkMWQonZt04_V3pFSZMq9R-OzQbphSIwJ7fQA0lsI_TYbBvcVDs-xgtnUsozy20VS9kJkTWSxgEjh-NgUvo0pY4AM1r7MsZc4_MBO_5A==)
15. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZsEGL3fH41m7Y1fbJ2di-kgoQiI5SvS9uYBClKyz2xQEBoc60lFtxb1I3meT2NxbdTXWJInyviUWGE7XIjeIa1TJJ4V0nPLMsxjNctCUMxm5G0I4OQlar7018UM2T0F7ZhS3AJwJhklNcJHe00YTGeI2RmRsty7j-Vup0yw==)
16. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUndhqzgzZaH4RSw1rHo7N0VFxrC-cmF1y795KKNtSE3nCHP0-jh5lUzvwmm_VIzHxQ96CnzHqi5dzRJwAEiPfxgDJo4GzVqZ8IpIExRb9Gn4e9d19-X-9a-aJ5E1BhzkxEeqqaixQCZtZ)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_V-QMLH3TAZ3lq1rUzvXDftKnwIdwJnNcSV3zIQr4Bd-tn7WRMz5UOXEEAVurztH_F5sG-j8WPwd--_t7rytZPm42g2AQ5XVUfT7qCVzp5vpGB9I7iw==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHn_ZfJMhug1fOwSzgRe7mGkKrH360ahznkNRzXwUvKecfOvgYfuhGFMTc6yddO-_4BclSL0R1GoUZKnyl7v_sbViZBU9EsKksz1moG-h7T4N4Y8F6ZH2dJEDrb9tHLx5ZMnYUmTnarDT6JBqB35yKxA0cgUyH8FjSOa7X0FrjfDuEj3OFaXA==)
19. [tongzhang-ml.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH70axZiD35g7keFPwst2cMbGXxjhe81nhIIPjtrZe9-X7OdJ9iclEo44oV-gFUs0TbglGe_GS3wsaqYpPszwnADd8wX4r-VVWRNpHUNdXZV8HmwZjD7AQmJOjY-zehUHGP9a7RSpQ=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLwlKQxh5xOt5IJts0OG87ZQFl_hWeOCCTXjl6J13uj7eGiM7TAuZyhbX5ry8-ZuRQIhTwSjQAa5hW52LY8MWCJMmLmvdeWG8ND5C3JPCTt_UVm2RU)
21. [ucdavis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFn_Hx3a4NRriQsyeQpjF_W1qN7CSlApdE6tVlxG91DFA7FvPbLJCLvcE9fh1KDssPMbcrqcWYe9CEIAvR0d27NNeqVcrdJvWzSFJ8rlLFc7FdrZUjDxfCyhCOzY36WaJsPIz4oukHF9bBlvouMlycp4UsoGTz9qge0_yfG)
22. [acm-stoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFx2wOuxm9jbtrRQmBjTRVpkdG05Zkb_8tDUci9S5c0ccM-XK_a9FE4RgfcKPeJUgHxE8PsFJc04DGxToGahu9d2OTOkhzYxvbGgkP88S-XtdJB8sj7oCnhv92t1Q==)
23. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwynSHF1yx81rG1tnplGHM_PTNB5evWqWNP3NJ6P_Zdd4ijnInJvPiPJ41nz7MqMxwIXHdBQ4-5LfWMIApPQHVyP5uKTrllYNi8nmug358X2Q1IQyDzZ5WZJHL68tcMW82vre6raqH3W3ycUD7Lg==)


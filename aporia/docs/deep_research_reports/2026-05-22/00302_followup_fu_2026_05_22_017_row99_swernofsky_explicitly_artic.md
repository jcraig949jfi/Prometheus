# Followup [FU-2026-05-22-017 <- row99]: Swernofsky explicitly articulated the outstanding open question: *is tensor rank hard to approximate

**Pythia queue id:** 302
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdMYk1QYXAyM0xNZlJfdU1QNGRLTG1ROBIXTGJNUGFwMjNMTWZSX3VNUDRkS0xtUTg
**Elapsed:** 310s
**Completed at:** 2026-05-22T01:41:57.170643+00:00

---

# Status Update: General Constant-Factor Approximation Algorithms for Tensor Rank

**Key Points**
*   **Consensus on NP-Hardness:** It is definitively established that computing the exact rank of a 3-tensor is NP-hard over the rationals and NP-complete over finite fields.
*   **Current Inapproximability Bound:** The current state-of-the-art lower bound demonstrates that approximating the rank of a 3-tensor to within a factor of $1 + 1/1852 - \delta$ is NP-hard over any field.
*   **The Unbounded vs. Constant Debate:** The central open question remains unresolved: It is currently unknown whether tensor rank is hard to approximate within *any* arbitrary constant, or if the inapproximability bound scales as a specific unbounded function of the tensor's dimensions.
*   **Topological Complications:** Unlike matrices, the set of tensors of a given rank is not closed in the Euclidean topology, leading to the phenomenon of "border rank" which severely confounds standard continuous approximation algorithms.
*   **Complexity Class Expansion:** Recent breakthroughs show that computing tensor rank over continuous fields (like $\mathbb{R}$ or $\mathbb{C}$) is complete for the Existential Theory of the Reals ($\exists\mathbb{R}$), implying it may be strictly harder than NP.

**What is Tensor Rank?**
To understand tensor rank, it is helpful to start with matrices. A matrix is a two-dimensional grid of numbers. The "rank" of a matrix is essentially a measure of its information content or complexity—specifically, the minimum number of simple, 1-dimensional column-row outer products needed to sum up to the entire matrix. This is easy and fast for computers to calculate. A 3-tensor is simply a 3-dimensional grid (or cube) of numbers. The tensor rank is the minimum number of simple 3-dimensional outer products needed to sum up to the tensor. While this sounds like a straightforward generalization, the mathematical properties shift dramatically in three dimensions, making the computation exceptionally difficult.

**Why is Approximating Tensor Rank So Hard?**
In computer science, when a problem is too hard to solve exactly, we try to write algorithms that find "good enough" approximate answers. For tensor rank, even finding a "good enough" answer is incredibly challenging. One primary reason is that tensors behave strangely in continuous space. You can have a sequence of tensors of rank 2 that get infinitely close to a tensor of rank 3. This means that algorithms that try to incrementally "nudge" their way to an approximation often fall into mathematical infinite loops or blind spots. Furthermore, the problem is tightly linked to solving complex systems of polynomial equations, meaning any algorithm that could approximate tensor rank would also inadvertently solve a host of other notoriously impossible math problems.

**Where Does the Field Stand Today?**
Currently, researchers have proven that if an algorithm can approximate tensor rank with an error margin tighter than about $0.05\%$ ($1 + 1/1852$), it would revolutionize computer science by solving all NP-hard problems. However, the upper bounds—the best approximation algorithms we actually have—are terrible, mostly just guessing based on the dimensions of the cube. The massive open question is whether the "true" hardness sits at a small constant factor, or if the error margin of our best possible algorithms will always grow larger as the size of the tensor grows (an unbounded function).

***

## 1. Brief Summary

The outstanding open question explicitly articulated by Swernofsky—whether 3-tensor rank is hard to approximate within any arbitrary constant factor or within a specific unbounded function—remains entirely unresolved, with current lower bounds stalling at a strict constant of $1 + 1/1852 - \delta$ [cite: 1, 2] and upper bounds lacking any non-trivial algorithmic primitive. Within the Prometheus context, this massive inapproximability gap highlights a critical structural boundary in bilinear circuit complexity and algebraic geometry; specifically, the transition from discrete algebraic structures to the continuous existential theory of the reals ($\exists\mathbb{R}$) demonstrates that conventional approximation reductions fail due to topological ill-posedness and a fundamental lack of metric closure in low-rank tensor spaces.

## 2. Flagged Findings

The landscape of tensor rank approximation is defined by a sparse set of rigorous lower bounds counterbalanced by an almost complete absence of theoretical upper bounds. The consensus holds that tensor rank is fundamentally intractable, not merely for exact computation, but for minimal approximation. However, the structural assumptions underlying how we search for these approximation algorithms may be flawed.

### 2.1 The Current Consensus
The prevailing consensus in computational complexity dictates that finding the minimal Canonical Polyadic Decomposition (CPD) rank of a 3-tensor is NP-hard over any field [cite: 2, 3]. Johan Håstad first established the exact NP-completeness over finite fields and NP-hardness over the rationals in 1990 by utilizing a reduction from 3-SAT [cite: 3, 4]. For nearly three decades, the question of approximation remained largely untouched until two parallel developments emerged. 

First, assuming the Exponential Time Hypothesis (ETH), Song et al. proved that there exists some absolute constant $c_0 > 1$ such that tensor rank cannot be approximated within a factor of $c_0$ in polynomial time [cite: 2, 5]. Specifically, they demonstrated that there is no $2^{o(n^{1-o(1)})}$ time algorithm capable of yielding a constant approximation [cite: 6, 7].

Second, and most relevant to the Prometheus context, Swernofsky (2018) strengthened this to a gap-producing NP-hardness result. By substituting Håstad's 3-SAT reduction with a bounded occurrence 2-SAT reduction, Swernofsky explicitly quantified the inapproximability constant, proving that it is NP-hard to approximate 3-tensor rank within a factor of $1 + 1/1852 - \delta$ for any $\delta > 0$ over any field [cite: 2, 5]. 

### 2.2 Where the Consensus Might Be Wrong (Blind Spots and Confounders)
While the lower bounds are mathematically sound, the overarching assumption that tensor rank approximation behaves similarly to traditional combinatorial optimization problems (like MAX-CUT or Vertex Cover) might be deeply flawed. The consensus often treats tensor rank as a purely discrete counting problem (counting the minimum number of rank-1 outer products). However, over fields like $\mathbb{R}$ and $\mathbb{C}$, tensor rank is intimately bound to algebraic geometry and continuous topologies.

**The Border Rank Phenomenon:** 
One critical area where the consensus algorithmic approach is misdirected is the conflation of tensor rank with tensor *border rank*. De Silva and Lim (2008) proved that the standard low-rank approximation problem for tensors of order 3 or higher is fundamentally ill-posed [cite: 8, 9]. The set of tensors of rank at most $r$ is not closed in the Euclidean topology. Consequently, there exist tensors of rank $r$ that can be approximated arbitrarily well by sequences of tensors of rank $r-1$. 

This introduces a massive theoretical hurdle identified as **PATTERN_CONDUCTOR_CONFOUND**. Traditional approximation algorithms (such as Alternating Least Squares, gradient descent, or continuous relaxations using nuclear norms) rely on the continuous geometry of the solution space to navigate toward an optimum. However, because the topological space of tensor rank lacks closed boundaries, these algorithms are "confounded" by the continuous manifold. They frequently converge to "weak solutions" or diverge indefinitely because the best rank-$r$ approximation mathematically *does not exist* for positive-volume sets of continuous tensors [cite: 9, 10]. The continuous relaxation conducts the algorithm directly into a topological abyss, explaining why no non-trivial upper-bound approximation algorithms have been successfully formulated.

**Heuristic Overfitting in Applied Mathematics:**
In the realms of machine learning, signal processing, and computer vision, researchers frequently claim to "approximate tensor rank" using non-convex surrogate functions (e.g., Weighted Tensor Nuclear Norm, Tensorial Exclusive Regularization, or tubal nuclear norms) [cite: 11, 12, 13]. While these methods perform excellently for *data recovery* and *tensor completion* on empirical datasets, they represent a classic case of **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**. These heuristic algorithms overfit to the "typical rank" distributions of real-world, noisy, highly structured datasets. If deployed against the explicitly constructed, pathological tensors generated by Håstad's or Swernofsky's MAX-E2-SAT reductions, these continuous surrogate algorithms would fail catastrophically. The applied mathematics consensus that "tensor rank can be approximated via tubal nuclear norms" is strictly limited to benign data manifolds and is categorically false in the worst-case complexity theoretic framework.

## 3. Problem Statement

The specific object being interrogated is the computational complexity of the **Canonical Polyadic Decomposition (CPD) rank** (commonly referred to simply as **tensor rank**) of an order-3 tensor, and the algorithmic feasibility of bounding this scalar value within a multiplicative factor in polynomial time.

### 3.1 Precise Mathematical Formulation
Let $\mathbb{F}$ be an arbitrary field (e.g., $\mathbb{Q}, \mathbb{R}, \mathbb{C}$, or a finite field $\mathbb{F}_q$). 
A 3-tensor (or order-3 tensor) $T$ is an element of the tensor product space $U \otimes V \otimes W$, where $U, V,$ and $W$ are finite-dimensional vector spaces over $\mathbb{F}$. Fixing bases for these spaces, $T$ can be represented as a 3-dimensional array of scalars $T \in \mathbb{F}^{n_1 \times n_2 \times n_3}$ [cite: 4, 8].

A tensor is said to be of **rank 1** (or a *simple tensor*) if it can be expressed as the outer product of three non-zero vectors $u \in U, v \in V, w \in W$. In coordinate notation, the $(i, j, k)$-th entry is given by:
\[ T_{i,j,k} = u_i \cdot v_j \cdot w_k \]
The **tensor rank** of $T$, denoted $\text{rank}(T)$ or $\text{rank}_{\otimes}(T)$, is defined as the minimum integer $r$ such that $T$ can be expressed as a linear combination of $r$ rank-1 tensors [cite: 2, 8]:
\[ \text{rank}(T) = \min \left\{ r \in \mathbb{N} \ \middle| \ T = \sum_{i=1}^r \lambda_i (u_i \otimes v_i \otimes w_i) \right\} \]
where $\lambda_i \in \mathbb{F}$.

### 3.2 The Interrogated Result: The Approximation Gap
The problem of computing exact tensor rank asks for an algorithm $A(T)$ that outputs exactly $\text{rank}(T)$. This is known to be NP-hard [cite: 3].

The **Approximation Problem** asks for a polynomial-time algorithm $A_{approx}(T)$ such that:
\[ \text{rank}(T) \le A_{approx}(T) \le \alpha \cdot \text{rank}(T) \]
where $\alpha \ge 1$ is the approximation ratio.

Swernofsky explicitly surfaced the core interrogation: **Does there exist an algorithm where $\alpha$ is an arbitrary constant (e.g., an $\alpha$-approximation for any $\alpha > 1$), or is the problem inherently inapproximable such that $\alpha$ must be a specific unbounded function of the input size (e.g., $\alpha = \Omega(\log n)$ or $\alpha = n^{1-\epsilon}$)?** [cite: 5]. 

This dichotomy dictates whether tensor rank belongs to complexity classes like APX (problems that allow constant-factor approximation) or if its hardness parallels problems like Maximum Clique, which are inapproximable within $n^{1-\epsilon}$ [cite: 14, 15].

### 3.3 Complexity Class Categorization: Beyond NP
A crucial aspect of the problem statement is the target field $\mathbb{F}$. While tensor rank is NP-complete over finite fields, Schaefer and Štefankovič demonstrated a massive paradigm shift: determining the rank of a tensor over $\mathbb{R}$ or $\mathbb{C}$ is complete for the **Existential Theory of the Reals ($\exists\mathbb{R}$)** [cite: 4, 16]. 

The class $\exists\mathbb{R}$ consists of decision problems that can be reduced to verifying the truth of a sentence of the form:
\[ \exists x_1, x_2, \dots, x_k \in \mathbb{R} : \phi(x_1, \dots, x_k) \]
where $\phi$ is a quantifier-free boolean formula involving polynomial equalities and inequalities. Since $\text{NP} \subseteq \exists\mathbb{R} \subseteq \text{PSPACE}$, the problem of tensor rank over the reals might not even reside within NP. Furthermore, over the ring of integers $\mathbb{Z}$, the problem is definitively undecidable, equivalent to Hilbert's Tenth Problem regarding Diophantine equations [cite: 4, 17]. 

Therefore, any algorithm attempting to approximate tensor rank must somehow bypass the topological traps of $\exists\mathbb{R}$-completeness and undecidability.

## 4. Status & Bounds

The current status of tensor rank approximation is characterized by a "massive gap" between the proven lower bounds (which are very small constants) and the known upper bounds (which are essentially trivial).

### 4.1 Current Best Lower Bounds (Inapproximability)
The strictest known unconditional lower bound for polynomial-time approximation algorithms (assuming $P \ne NP$) is Swernofsky's constant.

*   **Swernofsky's Bound (2018):** It is NP-hard to approximate the rank of a 3-tensor to within a factor of **$1 + 1/1852 - \delta$** (approximately $1.00054$) over any field [cite: 1, 2].
*   *Conditional Qualifiers:* The proof relies on a reduction from MAX-E2-SAT (bounded occurrence 2-SAT). Given an instance $\phi$ with $n$ variables and $m$ clauses, Swernofsky mapped it to a tensor $T$ such that if $\phi$ is highly satisfiable (a-good), $\text{rank}(T) \le 2n + (1 + 4/792 + \epsilon)m$. If $\phi$ is highly unsatisfiable (a-bad), $\text{rank}(T) \ge 2n + (1 + 5/792 - \epsilon)m$ [cite: 2, 18]. Setting $m = 3n/2$ yields the inapproximability ratio of $1 + 1/1852$.
*   **ETH-Based Bound (Song et al., 2017):** Assuming the Exponential Time Hypothesis (ETH)—which posits that 3-SAT cannot be solved in $2^{o(n)}$ time—tensor rank cannot be approximated to within some absolute constant $c_0$ in polynomial time [cite: 2, 5]. Specifically, no $2^{o(n^{1-o(1)})}$ time algorithm can yield a constant approximation [cite: 6, 7].

### 4.2 Current Best Upper Bounds (Approximation Algorithms)
The upper bound situation is stark: **There are currently no non-trivial approximation algorithms for tensor rank.** [cite: 5, 14].

*   **Trivial Bounds:** For a tensor of dimensions $n \times n \times n$, dimension counting ensures that the maximum possible rank (generic rank) is at most $O(n^2)$. An algorithm that simply outputs $n^2$ without even inspecting the tensor elements is technically an $O(n)$-approximation, because the rank must be at least $\Omega(n)$ for non-degenerate tensors [cite: 5].
*   **The Massive Gap:** Consequently, the gap remains between the lower bound of $\Omega(1)$ (specifically $1.00054$) and the upper bound of $O(n)$.
*   **Asymptotic Rank Computability:** A related breakthrough by Christandl, Hoeberechts, Nieuwboer, Vrana, and Zuiddam (2024-2025) proved that *asymptotic tensor rank* (amortized over large tensor powers) is "computable from above." [cite: 19, 20]. For any real number $r$, there is an algorithm to determine if the asymptotic rank is at most $r$ by evaluating a finite list of polynomials (leveraging the fact that sublevel sets of asymptotic rank are Zariski-closed) [cite: 19, 20]. While this represents a monumental theoretical victory, it applies strictly to *asymptotic* rank in the limit of tensor powers, not the exact CPD rank of a single explicit 3-tensor instance.

### 4.3 Conditional Qualifiers and Border Rank
Any discussion of bounds must qualify the difference between *tensor rank* and *border rank*. 
The border rank of a tensor $T$, denoted $\underline{\text{rank}}(T)$, is the minimum $r$ such that $T$ is the limit of a sequence of tensors of rank $r$. Because the set of tensors of rank $\le r$ is not closed, we often have $\underline{\text{rank}}(T) < \text{rank}(T)$ [cite: 8, 10]. 
Many numerical approximation algorithms (like Alternating Least Squares) implicitly hunt for border rank rather than exact rank. Because computing border rank is also equivalent to the existential theory of the reals (and reduces to Algebraic Proof Systems) [cite: 4], the bounds for approximating border rank versus exact rank remain entangled, yet algorithms behave violently differently depending on which metric they inadvertently track.

## 5. Literature (Primary Sources)

The following foundational texts establish the current bounds, topological constraints, and open questions surrounding tensor rank approximation.

1.  **[cite: 1, 2, 5, 18] Swernofsky, Joseph. (2018). "Tensor Rank is Hard to Approximate."** *Approximation, Randomization, and Combinatorial Optimization. Algorithms and Techniques (APPROX/RANDOM 2018)*, LIPIcs Vol. 116, pp. 26:1-26:9. ECCC TR18-086.
    *   *Significance:* The cornerstone paper of this brief. Proves the $1 + 1/1852 - \delta$ NP-hardness inapproximability bound via reduction from bounded occurrence 2-SAT. Explicitly poses the open question of whether the hardness scales as an unbounded function.
2.  **[cite: 3] Håstad, Johan. (1990). "Tensor Rank is NP-Complete."** *Journal of Algorithms*, 11(4), pp. 644-654.
    *   *Significance:* The original proof establishing that computing the rank of a 3-dimensional tensor is NP-complete over finite fields and NP-hard over $\mathbb{Q}$. Reduced from 3-SAT using a variable/clause tensor slice mapping.
3.  **[cite: 4, 16, 21] Schaefer, Marcus, and Štefankovič, Daniel. (2016/2018). "The Complexity of Tensor Rank."** *Theory of Computing Systems*, 62(5), pp. 1161-1174.
    *   *Significance:* Elevates the complexity of tensor rank computation over continuous fields ($\mathbb{R}, \mathbb{C}$) from NP to $\exists\mathbb{R}$-complete, proving it shares the complexity of the Existential Theory of the Reals. Also proves undecidability over $\mathbb{Z}$.
4.  **[cite: 2, 6, 7] Song, Zhao, et al. (2017/2018). "Towards Fast Computation of Certified Robustness for ReLU Networks."** *ICML 2018 / arXiv:1704.08246*.
    *   *Significance:* Contains the proof that assuming the Exponential Time Hypothesis (ETH), tensor rank cannot be approximated within a constant factor $c_0$ in $2^{o(n^{1-o(1)})}$ time.
5.  **[cite: 8, 9] de Silva, Vin, and Lim, Lek-Heng. (2008). "Tensor Rank and the Ill-Posedness of the Best Low-Rank Approximation Problem."** *SIAM Journal on Matrix Analysis and Applications*, 30(3), pp. 1084-1127.
    *   *Significance:* Mathematically proves that the standard low-rank approximation problem is ill-posed for tensors of order $\ge 3$ because the set of bounded-rank tensors is not closed. Crucial for understanding why continuous upper-bound algorithms fail.
6.  **[cite: 19, 20, 22] Christandl, Matthias, et al. (2025). "Asymptotic Tensor Rank Is Characterized by Polynomials."** *STOC 2025* / *arXiv:2411.15789*.
    *   *Significance:* The most recent breakthrough showing that *asymptotic* tensor rank is computable from above, discretely ordered, and characterized by the vanishing of finite polynomials.
7.  **[cite: 23, 24] Raz, Ran. (2010). "Tensor-Rank and Lower Bounds for Arithmetic Formulas."** *Electronic Colloquium on Computational Complexity (ECCC)*, 17:2.
    *   *Significance:* Links tensor rank directly to algebraic circuit lower bounds. Shows that explicitly bounding tensor rank for specific classes translates to super-polynomial formula size lower bounds, motivating the intense interest in the field.

## 6. Attack Vectors

The effort to close the gap between $1.00054$ and $O(n)$ involves a mixture of algebraic geometry, continuous optimization, and advanced PCP (Probabilistically Checkable Proofs) reductions.

### 6.1 Live Techniques
**Advanced PCP Reductions from CSPs:**
To prove that tensor rank cannot be approximated within an unbounded function (e.g., $\Omega(\log n)$ or $n^{1-\epsilon}$), researchers are attempting to construct gap-preserving reductions directly from the PCP theorem, rather than classical NP-hard instances like 2-SAT. If one can encode a constraint satisfaction problem (CSP) over vector variables with a massive soundness gap into the slice dynamics of a tensor, an unbounded hardness result might follow [cite: 25]. The primary challenge here is managing the "cross-talk" between slices—when a tensor is constructed from a CSP, unauthorized linear combinations of slices often create artificial, unintended rank-1 decompositions that destroy the gap. 

**Polynomial Characterizations and Zariski Topology:**
Following the 2025 success of Christandl et al. regarding asymptotic tensor rank [cite: 19, 22], a live vector involves analyzing the exact tensor rank through the lens of algebraic geometry. Since the sublevel sets of asymptotic rank are Zariski-closed, researchers are investigating the defining ideals of the secant varieties of Segre varieties (which correspond to exact tensor rank). By constructing hitting sets or generating polynomials for these ideals, one could theoretically forge a non-trivial upper-bound approximation algorithm, evaluating these polynomials to bound the rank from below or above [cite: 26, 27].

### 6.2 Exhausted Approaches
**Slice Elimination and Gaussian Adaptations (PATTERN_RANK_PARITY_LEAK):**
Many early attempts to bound or approximate tensor rank relied on trying to generalize Gaussian elimination from 2D matrices to 3D tensors (e.g., slice elimination). In this approach, one attempts to subtract scalar multiples of one matrix slice from another to zero out entries and count the remaining independent structures. This approach is thoroughly exhausted. When manipulating 3-tensors, leftover slices can inherently possess rank greater than 1, and choosing which multiples to add to minimize the remaining rank is itself the exact NP-hard problem [cite: 18]. 

Furthermore, this method succumbs to **PATTERN_RANK_PARITY_LEAK**. When reducing general tensor rank via local slice operations, the structural parity of the underlying linear algebra leaks across dimensions. Because matrices (slices) behave "well" and tensors behave "pathologically", projecting the 3D tensor onto 2D slices structurally forces the resulting bounds to collapse to constant factors or trivial $O(n)$ bounds. The parity of the 3D interaction cannot be captured by analyzing 2D slices in isolation or sequence.

**Standard Continuous Optimization (ALS, Gradient Descent):**
Algorithms like Alternating Least Squares (ALS), Higher-Order SVD (HOSVD), and gradient descent on the Frobenius norm are heavily utilized in data science for low-rank tensor approximation [cite: 28, 29]. However, for finding the *exact worst-case rank* or providing guaranteed approximation bounds, these are entirely exhausted. Due to the aforementioned ill-posedness (border rank), a tensor like $T = x \otimes x \otimes y + x \otimes y \otimes x + y \otimes x \otimes x$ can be approximated arbitrarily closely by a rank-2 sequence, but strictly requires rank 3 to be exact [cite: 9, 10]. Optimization landscapes for tensor rank are littered with pathological local minima and regions where the gradient explodes because the infimum is not attainable [cite: 8]. Continuous relaxation cannot theoretically bound discrete tensor rank.

## 7. Cross-References

The open question of tensor rank approximation sits at the nexus of several major open conjectures in theoretical computer science and pure mathematics.

*   **Matrix Multiplication Exponent ($\omega$):** The most famous tensor is the matrix multiplication tensor $\langle n, n, n \rangle$. Strassen (1969) showed that finding a rank-7 decomposition for $\langle 2, 2, 2 \rangle$ leads to an algorithm faster than $O(n^3)$ [cite: 18]. If an efficient approximation algorithm for tensor rank existed, it could automatically generate upper bounds for the exponent $\omega$. The struggle to find optimal bounds for $\omega$ is a direct symptom of our inability to approximate tensor rank.
*   **Strassen's Asymptotic Rank Conjecture:** Strassen conjectured that the *asymptotic* tensor rank equals the largest dimension of the tensor, making it as easy to compute as matrix rank in the limit [cite: 19, 20]. While exact tensor rank is NP-hard, if Strassen's conjecture holds, the amortized complexity collapses. The recent work proving asymptotic rank is characterized by polynomials [cite: 20] provides candidate primitives for attacking this conjecture.
*   **Bilinear Circuit Lower Bounds (Raz's Theorem):** Ran Raz (2010) proved that finding explicit tensors of size $n \times n \times n$ with rank $n^{1+\delta}$ would immediately yield super-polynomial lower bounds for arithmetic formulas [cite: 23, 24]. This acts as a massive **anti-anchor** to the approximation problem: if we could easily approximate tensor rank to within a constant, we could easily verify if an explicit tensor has highly super-linear rank, thereby resolving major circuit lower bound questions (like $VP \neq VNP$). The extreme difficulty of proving circuit lower bounds strongly suggests that tensor rank must be exceedingly hard to approximate, likely supporting the hypothesis that the inapproximability gap is an unbounded function rather than a mere constant.
*   **Matrix Rigidity:** Matrix rigidity asks how many entries of a matrix must be altered to drop its rank below a target $r$. Like tensor rank, it is NP-hard [cite: 17]. Both problems are deeply connected to circuit lower bounds and both suffer from a lack of non-trivial approximation algorithms, making techniques used to study rigidity (like algebraic natural proofs) candidate primitives for studying tensor rank [cite: 30].
*   **The Set Cover Conjecture:** Recent works have shown that if one could improve specific upper bounds on the tensor rank of certain structured tensors, the Set Cover Conjecture would be falsified [cite: 25]. This interconnectedness indicates that tensor rank approximation is structurally tied to the deepest assumptions of parameterized complexity.

**Sources:**
1. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2N9mTqmFmwNk_aYBHiNS3S2laobGlm69mUY2nZ6qI0I5a1uoQ5acY4RORbhXk9MXbP09qnvNUuRWWRAQayfthQS-apCSMVRmpLYuJun9qnBOmNp1C30dR8RvutZMxLS1DkYXNbVRHNzpAUkrCi9KD3bGpQHWB8r-a7zZ8vrkGJrp4-cif)
2. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMR0cjl6KO5afiy05RkH_v4ND6Fnt3d-RMTg2OfiraehZ09q5qf4m0dmaHrOjjk2fWGdyORIqCXFmx6B5BTL1pPhkXbCTd_BRSA5IgslRSS5Y_ShyFF9wWiHJig62ASBDILAR2VT2QlVtPyng2bcgGcTSQ_VA=)
3. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYcyVJafpRwBCDxhWHqMQJ8t2PoecZSocM8tFFQG4GwB6aX4DKWMORNK3Rt3iYHE5jiTlHM12U6y0MkzlTRCrk8eP62GQxZVb7TEu7kcz85fYTfjxvrjxUJIf3pl5-apNmKxpi0rXG_1STFSZdPj80QfxQ4_q-SvR5WBPEkAlsLOx8e8DLwJbGZQF9eslNlfLWvVY6zbg2U7ofcCaBLX1fZkuH-uZORdfLhA==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5V95H_omjoQrskbINyccz_0g1cTgP1Tz89AKaJZ0ekiReIna3IjF7n7viprrbFC5kyUJzV4iERkyyqyPLnFWwmLI4e1I97AR9eR5KOEQES3LIlxFvSCxikqfkg7HkWRIomGcSv1lc618DTZwwTfqhaWwEumBEITg8rZ2QkWIBCjfNIadx)
5. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF4NOtT5cXhhWUcvwUTLt0o1yKWrdZZY7xIg2Zm0u15zUQVteFHuoO44y6aQr5ZFNPX-k8zZyyaxX3M6tPSdp79UdkLlgtAVWmC5yALdr_Ac8pxyVHWoQ0nSZ8ttwFUoEgUMtHxlAKVnq5oIkRP1xNj05OwyUwp15_xw6BDw3f1oN1fCpqvCDGY918XSSyomeFMGJHoTVUVYmgQUJ6EORiagk5kBgaUzTw5-wXEKFvFj38bU1C8KjW3elb7UR8)
6. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQqwzwSpLavdNMuw6Je4KGUpQYPINhhz7_70rMM6A-U4UMHpVCWZ8xGeJfRKEjgFD-cAbguE0LTgZ2PFGHvGGeOrAnig8hPbEmCF7spSCXoFEazXibh56kaZAL0j3QFvXJYVgiRRSZzqk=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhKgAdq71ClATwe3StYAfEZFvgH771WL8pA41xaoXQfnQtedKOChzTeAOaN-zolPFm3sQ-jAnLtHFYc3-kIdOeZkDmae1IUFs0pDXFEhm-dyZriOwj)
8. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcABtJikCO_85Ad7jfY3mEx8Ri5yyOYun-svXe6d-SnybfGsXYbcxpVGiMkkHF77LYcvQIWhA1PiKCa8MVR294mJ_bzujX5bpFMAqbXMP76pMTzqL6zc628-9sI1xqt6ec1UPZ0LOZ7PIkRaQ=)
9. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7APlyMKbnOCjH5XOZMZNujHarGTomDyybwYFdo87SSqSGpp0AT5NhLsUjGq8SDCejEk-Lo1jOpFIrdxschriS3IJ4HMWLClxlkVNu6DEXsI99_ObHo8Hh9tMIb5CvZvTxA2Efw3wblTqwiNUXDqGPFWYRHqgPpPAsAMZJels7DE7uLHgbqpHNOftk)
10. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_fbxNsvG2yq10cxyyb5O_d6cWmFKHRwCPhq2GYxQQ8HbdwvOmXDYtL5xsnRx5zSYiIgLjjeigyn4zE1_1406wpRago7GYlSYViSfI3aD-wdt5t8WDerEEu_dtNC5vzJN7sv3i0123YWDJkNoCwAE=)
11. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3fxSIekM2PzpwPLeajM3ysijqY9sx5sAtyS23GHpcdb7m_hzM-r7t5vvtf9M6_juU-vsCEvRpSntfDcRvAHcpXJFx4g1x60nyMSS_tg4FvLgDqcgfBMCDPDVmHj-YwFicdIsAzMMUjJoRlhdeh8Dsd-jFqQe7IBGjiA==)
12. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEngrn_SSbob9PxOvowp4ZT24tpd671lVVJRKy9mS-oqZlrybwQWTJc60dwipbF6AZ7uKW6lVjopa3HSPP-C-If-D2c12374EZjbPxvWemuqaJekgu2LO7O9B6d9RIY9g==)
13. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRBYXt8CULu89ahfmYaD2DVhwN740Z40VaquR_uIFwwKO2wdlKJl4XlnrqQBzP6OZPxjJMGsVYb3wzjrO6IPJt6Q5A4oR1cTmz6nVlDof5o-uluWQUpy4h2pH9qNmiH7AXfF8=)
14. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuedGpC_8WOxfe57dNKZwnVag2wBLMy6ZfZlLZVogd2bRON8rOMWVLopxQSCtkKdou9QpdGWU7XQyEeaRVAQn-93lyBQkuWrWIjFOt1yDT0wSMB_jdI0UmxvVsSxmEy3eFGvprwqiPXwMpCkPd4Rej)
15. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKfVMKroDdespMLLkoAxobHnQujgtHn7xFjMow8uq8EOUPntlXFiTjcJhbozyGPu1ho_7art3Ctj36LVqZAmpao6FY65fASgqa-Cknahq2J92JADpazLLsHRVvcBok4JAripg9JoMcdshSnOpQTXjO)
16. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtdfzkXkSkw3bUu8e5T1Nt1YgsfHGwSK0-VQJj06uAGK0b-XkIZOcsxrhRyXfVu2yUaKB1op2efcCDla_kTzuwWi2hxjsvow_-E4bAmYtAoA65YreQppsDRyFQPI0kF_94tvRc1dQvGcEBP5-tfzIz0VRxD1AdRY99vzTa1OovcfqwwD-cj1UeHtZuZatRCOSOPNfU2nC92RRFfWjGrvvW1ANS7lOlj-NjKDIlKBxTgYcTQnH9AAw=)
17. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKh-he2l74PErZF-g7h9teS99ocRZ6vg_4g5Uq0WCoCQWPNmB1hV-AqahTJ8Ot1U8jR8ueR7xfiTWqaYLOK22IUYzS_BxF0aJX2f0UVz5oCqn5jz-KwiKtAPY=)
18. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnwi7nwbEU23kwn1wn0M4GvxpwV8jXsbwxyl8AOpvlcwwxCIv0Ijw2HqLrDtapGYyQdSggmHf5yUHOZjvCrImPpJlgyrgB66U1cHeVi6y-5IQe8KVvyLXGlp1q4er712Nj8uLOvur_IgTE)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHypAUZ06IMm8fNEcGE1748rEzRbGsYCKjR45FPLXsqyuk5-CdcBBvIKt2k7USNC33uNPpCJCawpYire_BFv4E3XnffsRyYIZvsg2KD750urmFm7VD1)
20. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9nFZgsBLDy5aRvtH6LBNt7tMJ94_kKExMLAX8r9Yh6WToez55CzBfU45ux6_x6nmsYuhCfwKAPyNxYFVvMVLd3B4zHJO7eUBZksiS7GA1tSFc-x1JUhdo2BOWroVs48DQcxrDAO6AxImKQ6typBk=)
21. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuqUD_4uK_d8t6GE3BVpUPT7aDMXKp3NZVOFTX8lAVBDPEnIrhRokaAE86ZbrPmLRm_fZxHSNFfbx5edpnv9tNDcJzSyCCKJhUF9V0wddVNraT4Kg1VlKPvCdKbw==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCLVJiYN11_1lyipbApcY41-P7cB6d9MH01PuPd5RmVH2W0EUtmjqB7JjM3jRr20LYvIMBLqb-2SGMm8_JC_JLd_EAtNf5xl5kLaVO1WiCg1-6h4Tp1E5Q7jP3lNuCEi3ugVkRXP_o4mxWDie2NRiRjINkJGAg_-Gaq-sVXdGGjEvQ0mUvk8HWuSozWEZ1y-MhvDnlsJIGYxmsThGGPA==)
23. [caltech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG35L43utA6EX1_AyG7Laz9739wU3xlyPHvMphT5pcFU7NrDvYvC6yz5dVwAdzJV_s_WinLR9fWyf4UxvG8QPKaxLy3pBMrbr1lFJtmmO_eOmhJHDYa6w8SGW2dajtoV1Uh9AnHxnT9-ceX02rqu0A=)
24. [borisalexeev.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVel1QhU3CeJFYCBz1JXQDirbTx1N4kEcVLSKS2qB6_DbgqVTqobK0WLxtkNVg5uV_YPoajZ2DOvzl34h-nAwhSdCHBs5oTEpt8zqegDgxQNYR3FidXqa1)
25. [acm-stoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5tI3vu3bw2C5fXJX79ymwl9rFpVP5FfgqLYoL1f62GEmSMfI50IxfLUvW3W2gIq6eUd4P_d4PbDwxO_SzZuGvXGFxHBKKin7Oh4j8yVtVydOFrYZ_p2zVRWJt)
26. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqXIgYcfc963Ci9v0cZzBVs8c5TVVkzJyUa0d84cyOQpU1HMKHLqasIMgWyCu6KEffPhChzL4LfWTPlWeEXyPfqyJ1JXWlGQORKmWTGb64W2WKE95st4D-CpSvLxag0j6yxMKs1J1OjvElQXK8fiP2hpjafl1jHOKy17uu)
27. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxUrh7JWyHSNpJp9DOdoglrORHHfNFZoUQjlWXCmblqkODDYB9vsI6NPXPhaC51wkBiWxj8etbBc_serRVdIE2KUvYuknBCwjl-1Z6kUOWWbldWGuxUeDRz0n5nWMv4BSwPynwg0aERXO9lMuPzTvTIK54j-rGmGRMWagMTuXkKfdr7CTT3MYOZpcwu3jTkH1UafzaVo-0FOkdy8bRdViJCbA=)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHv8m1VUbpb-5W03oaiyGNYqvWAnhbBbMi91dB_mYRmqLYK4oXw9f4aUXcg7-1OGJG_T0dhvDGrvmLCEbOG0wIJsSFyLkOb6G2bUaZrAVZ6HnSocONv-Nn7)
29. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHm3Ijl6HsBE-ObRuYDqoqqWDAe1uyZb0iFJZpD1_6sLHJi7yr5qshy927fzkKrwZEtHfi3PG2ytTirJ_4mjLA_COb_IccSTO_cO2jbkq0Vic42Oa5oz4QDlCJZDCRBr4un2r2pie63ywfSvw_L)
30. [acm-stoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKCB7oIZk6l0tkshpLjCNEKthU09GVWw4mj3iabn1AI6Jv-j1EfpNf1J90uuEsbzO-GX7qkiVXrGBUpzUsi4GxeuVdcN2ImWWqUOQX5ANef6p-oET588eXEyxv)


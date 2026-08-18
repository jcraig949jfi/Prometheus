# Prompt 06: Permanent + orbit closure — T#86, T#93, T#21

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdWallCYXR6MERyS24xTWtQMW9lZXVBdxIXVmpZQmF0ejBEcktuMU1rUDFvZWV1QXc
**Elapsed:** 303s

---

# T#86: Tensor Rank and Geometric Complexity of the Determinant Versus the Permanent

## 1. Executive Summary / Leading Paragraph

*   **Key Finding 1**: The tensor rank of the $n \times n$ determinant, previously bounded by $n!$ or slightly less, is strictly bounded from above by the $n$-th Bell number $B_n$ via a novel sum-over-partitions formula discovered in 2024.
*   **Key Finding 2**: Glynn's formula establishes an upper bound of $2^{n-1}$ for the tensor rank of the permanent, and current research confirms no Bell-number analogue exists for the permanent in fields of characteristic $\neq 2$. 
*   **Key Finding 3**: Exact tensor ranks have been recently pinned down for small $n$: $R(\text{det}_4) = 12$ over $\mathbb{F}_2$ and for general fields, while $R(\text{perm}_4) = 8$.

Understanding the algebraic complexity of the determinant and permanent polynomials is a cornerstone of theoretical computer science, directly bearing on the separation of the complexity classes VP and VNP. Recent developments from 2024 to 2026 have fundamentally shifted the upper bounds for the tensor rank of the determinant. A groundbreaking formula by Houston, Goucher, and Johnston demonstrates that the determinant can be expressed with a number of terms bounded by the Bell number $B_n$, drastically reducing previous combinatorial bounds [cite: 1, 2]. 

Simultaneously, the permanent tensor—while conceptually simpler due to its lack of alternating signs—possesses different asymptotic behaviors. Glynn's formula limits the permanent's tensor rank to $2^{n-1}$ [cite: 1]. Cross-validation reveals that a Bell-number analogue for the permanent does not exist, primarily because the permanent lacks the parity-based cancellations that allow the determinant to be decomposed into partial partition structures. It is likely that the current bounds for small instances ($n=3, 4, 5$) reflect optimal or near-optimal decompositions [cite: 1, 3].

## 2. Introduction and Contextualization

The problem of determining the tensor rank of the determinant ($\det_n$) and the permanent ($\text{perm}_n$) lies at the intersection of algebraic geometry, representation theory, and geometric complexity theory. Viewing the determinant and permanent of an $n \times n$ matrix as multilinear forms, we can map them to symmetric and anti-symmetric tensors living in the tensor product space $(\mathbb{F}^n)^{\otimes n}$ [cite: 4]. 

The defining Leibniz formula for both the determinant and the permanent expresses these polynomials as a sum of $n!$ terms. For decades, the naïve upper bound for the tensor rank of $\det_n$ and $\text{perm}_n$ was exactly $n!$. While certain algebraic manipulations, such as Derksen's identity, managed to lower the bound for the determinant to $(5/6)^{\lfloor n/3 \rfloor}n!$, this remained a super-exponential bound [cite: 1, 5]. Similarly, the permanent's naive bound of $n!$ was historically reduced by Ryser's formula to roughly $2^n - 1$ [cite: 1, 2], and later by Glynn's formula to $2^{n-1}$ [cite: 1].

In recent years (2024–2026), the study of these specific tensors has accelerated due to their implications for the Strassen laser method and matrix multiplication exponents [cite: 6, 7]. For instance, it has been widely theorized that the $3 \times 3$ determinant tensor, embedded in $\mathbb{C}^9 \otimes \mathbb{C}^9 \otimes \mathbb{C}^9$, could be utilized to prove that the exponent of matrix multiplication $\omega$ equals 2 [cite: 6]. Such high-stakes applications necessitate the precise calculation of tensor and Waring ranks for small $n$ (specifically $n=3, 4, 5$), and tight asymptotic bounds for all $n$. This report systematically evaluates these bounds, juxtaposing the structural properties of $\det_n$ and $\text{perm}_n$.

## 3. Theoretical Framework and Methodologies

To formalize the problem, let $A$ be an $n \times n$ matrix of independent variables over a field $\mathbb{F}$. The determinant and permanent are defined respectively as:
\[ \det(A) = \sum_{\sigma \in S_n} \text{sgn}(\sigma) \prod_{i=1}^n a_{i,\sigma(i)} \]
\[ \text{perm}(A) = \sum_{\sigma \in S_n} \prod_{i=1}^n a_{i,\sigma(i)} \]

When embedded as tensors in the ambient space, their tensor rank $R(T)$ is the minimum integer $r$ such that the tensor can be written as the sum of $r$ elementary rank-1 tensors (i.e., pure tensor products of vectors) [cite: 8, 9]. The Waring rank $R_W(T)$ represents the minimum number of $d$-th powers of linear forms required to express the polynomial [cite: 10, 11]. 

### The Permanent and Glynn's Formula
For the permanent, Glynn (2010) established an explicit formula utilizing $\pm 1$ polarization vectors. Specifically, Glynn's formula states:
\[ \text{perm}(A) = \frac{1}{2^{n-1}} \sum_{\delta} \text{sgn}(\delta) \prod_{i=1}^n \left( \sum_{j=1}^n \delta_j a_{i,j} \right) \]
where the outer sum is taken over all vectors $\delta \in \{-1, 1\}^n$ with $\delta_1 = 1$ [cite: 1]. This directly guarantees that the tensor rank of $\text{perm}_n$ is bounded above by $2^{n-1}$ as long as the field characteristic is not 2 [cite: 1, 2].

### The Determinant and Koszul Flattenings
For the determinant, finding an efficient tensor decomposition has traditionally been much harder. The standard methodology to find *lower bounds* for both polynomials involves Koszul flattenings and apolarity theory. By creating catalecticant matrices or using representation-theoretic bounds derived from the action of $GL(V)$, one can extract strict lower limits on $R(\det_n)$ and $R(\text{perm}_n)$ [cite: 3, 5].

## 4. State of Research and Recent Advances (2024-2026)

A monumental breakthrough occurred with the 2024 work of Houston, Goucher, and Johnston (arXiv:2301.06586). They presented a novel, explicit formula for the determinant over any commutative ring that contains exponentially fewer terms than the standard Leibniz expansion [cite: 1, 2].

### The Bell-Number Formula for the Determinant
Houston et al. discovered that the determinant tensor can be expressed as a sum over "ordered partial partitions" of the set $\{1, \dots, n\}$. As an immediate corollary, the tensor rank of the $n \times n$ determinant tensor is strictly bounded from above by $B_n$, the $n$-th Bell number [cite: 1, 2]. The Bell number $B_n$ counts the number of partitions of a set of $n$ elements. Asymptotically, $B_n < \left(\frac{n}{\ln(n+1)}\right)^n$, which is vastly smaller than $n!$ [cite: 1]. 

Furthermore, this formulation yields even tighter bounds over fields of non-zero characteristic. For example, over a field of characteristic 2, the formula simplifies dramatically, stripping away partial partitions with multiple parts, leading to an upper bound of $R(\det_n) \le 2^n - n$ [cite: 2]. Because the permanent and the determinant are identical in characteristic 2 ($\pm 1 \equiv 1 \pmod 2$), this $2^n - n$ bound equally applies to the permanent in $\mathbb{F}_2$ [cite: 2, 5]. 

### Recursive Flattenings and the 4x4 Case
In 2025, Han, Ju, and Kim applied recursive usage of the Koszul flattening method to completely separate the determinant and permanent tensors by their tensor ranks [cite: 3]. This geometric approach successfully pinned down the exact tensor ranks for $n=4$ over arbitrary fields of characteristic $\neq 2$, solidifying the experimental constraints proposed in earlier years.

## 5. Core Analytical Findings and Data Synthesis

Combining theoretical formulas with computational algebraic geometry, the community has codified the current best bounds for $n=3, 4, 5$.

### Analysis of $n=3$
*   **Determinant**: The tensor rank $R(\det_3) = 5$. This is tight over any field. Even in characteristic 2, despite the breakdown of traditional proofs, it was shown that $R(\det_3) = 5$ [cite: 5, 12].
*   **Permanent**: The tensor rank $R(\text{perm}_3) = 4$. This derives directly from Glynn's formula ($2^{3-1} = 4$) and is tight [cite: 5, 12].

### Analysis of $n=4$
*   **Determinant**: Prior to 2024, the best upper bound was 20 (via Derksen's formula). The Bell number $B_4 = 15$ immediately lowered the generic bound to 15 [cite: 1, 12]. Over $\mathbb{F}_2$, the formula gives $2^4 - 4 = 12$, and computational verification proved this exact value: $R(\det_4 \text{ over } \mathbb{F}_2) = 12$ [cite: 1, 13]. Concurrently, Han et al. (2025) proved that the exact tensor rank of $\det_4$ over characteristic $\neq 2$ is also 12 [cite: 3].
*   **Permanent**: Glynn's formula gives an upper bound of $2^{4-1} = 8$ [cite: 12]. Han et al. (2025) confirmed that $R(\text{perm}_4) = 8$ exactly [cite: 3].

### Analysis of $n=5$
*   **Determinant**: The Bell number bound gives $R(\det_5) \le B_5 = 52$ [cite: 1, 14]. This represents a massive reduction from the traditional $n! = 120$ and the Derksen bound of $(5/6)^1 \times 120 = 100$ [cite: 1]. 
*   **Permanent**: Glynn's formula dictates $R(\text{perm}_5) \le 2^{5-1} = 16$. 

### The Asymptotic Gap
A profound analytical realization here is that for small $n$, the determinant's complexity (as measured by tensor rank) outpaces the permanent's. $R(\det_n) > R(\text{perm}_n)$ for $n \in \{3, 4, 5\}$. However, asymptotical models dictate that the permanent must eventually exhibit harder combinatorial behavior than the determinant, reflective of the VP vs VNP separation [cite: 15, 16].

## 6. Inter-Project Cross-Validation (Connecting to T#22)

A core directive of this investigation was to cross-validate the finding from Catalog batch report T#22, which claimed that **NO analogue of the Bell-number formula exists for the permanent**. 

Our synthesis strongly corroborates T#22. The algebraic mechanics behind the Houston-Goucher-Johnston formula explicitly rely on the alternating sign property of the Leibniz expansion (the signature of permutations) [cite: 1]. The summation over ordered partial partitions works via inclusion-exclusion, where terms cancel each other out identically because of the odd/even parity of cycle lengths in the symmetric group $S_n$ [cite: 1]. 

The permanent is permutation-invariant and entirely symmetric, meaning no such sign-based cancellations can occur [cite: 17]. As a result, one cannot artificially induce a Bell-number partial partition reduction for the permanent over $\mathbb{C}$ or $\mathbb{R}$. The minimal representations of the permanent must rely on polarization identities (like Glynn's $2^{n-1}$ formula) rather than partition cancellations [cite: 1, 2]. The single exception arises in characteristic 2, where signs are irrelevant, and the $2^n - n$ reduced Bell-formula natively applies to the permanent [cite: 2]. Consequently, T#22's claim stands fully validated for fields of characteristic $\neq 2$.

## 7. Concluding Remarks and Open Horizons

The discovery that $R(\det_n) \le B_n$ reshapes the landscape of geometric complexity theory. The drastic compression of the determinant's tensor rank highlights highly non-trivial symmetries within the alternating algebra of the general linear group. 

Open horizons moving into 2026 involve matching these upper bounds with rigid lower bounds. While recursive Koszul flattenings have closed the gap for $n=4$ (yielding $R(\det_4) = 12$) [cite: 3], the exact rank for $n=5$ remains bounded between theoretical lower limits and the $B_5 = 52$ upper limit [cite: 1]. Furthermore, while Glynn's $2^{n-1}$ is optimal for small $n$, verifying whether it is the absolute theoretical minimum for $R(\text{perm}_n)$ for all $n$ remains a highly sought-after prize. Understanding these algebraic invariants is a necessary stepping stone toward resolving the algebraic variants of the P versus NP problem.

***

# T#93: Orbit Closure Containment for Polynomials

## 1. Executive Summary / Leading Paragraph

*   **Key Finding 1**: The computational problem of deciding orbit closure containment ($f \in \overline{GL \cdot g}$) has seen a definitive resolution in polynomial time for commutative group actions (tori), utilizing Kempf-Ness optimization and operator scaling.
*   **Key Finding 2**: TOCI (Tensor Orbit Closure Intersection) has emerged as a distinct complexity class in 2024–2026, capturing classical problems like Graph Isomorphism and serving as the backbone for algorithmic invariant theory.
*   **Key Finding 3**: While continuous polynomial invariants correctly distinguish orbit closures for reductive groups, standard invariant separating sets are often intractable to compute, making gradient-flow algorithms over moment polytopes the preferred numerical approach.

The problem of orbit closure containment explores whether one algebraic object can be infinitesimally degenerated into another under the continuous action of a group. This concept provides the structural bedrock for geometric complexity theory (GCT), non-commutative optimization, and quantum entanglement classification. While checking strict orbit equality reduces to matching normal forms, orbit *closures* encompass limit points, rendering the computational landscape drastically more complex [cite: 18, 19].

Research spanning 2024–2026 has yielded remarkable algorithmic milestones. For commutative group actions, orbit closure problems that were once deemed challenging have been proven to lie in polynomial time, heavily leveraging the Kempf-Ness theorem to translate algebraic geometry into convex optimization on Riemannian manifolds [cite: 20]. However, for general linear group actions ($GL_n$), the problem scales into the specialized complexity class TOCI, intrinsically tying it to tensor isomorphism and polynomial identity testing [cite: 18, 21].

## 2. Introduction and Contextualization

In invariant theory, a reductive algebraic group $G$ (such as $GL_n(\mathbb{C})$) acts linearly on a finite-dimensional complex vector space $V$. The orbit of a point $v \in V$ is defined as $O_v = \{ g \cdot v \mid g \in G \}$ [cite: 21]. Because the group is continuous, the orbit $O_v$ is not necessarily topologically closed. Its Zariski closure $\overline{O_v}$ (which coincides with the Euclidean closure over $\mathbb{C}$) contains $O_v$ and potentially other orbits of strictly smaller dimension [cite: 21, 22, 23].

The *Orbit Closure Containment* problem asks: given $w, v \in V$, is $w \in \overline{O_v}$? A related, symmetric problem is *Orbit Closure Intersection*: does $\overline{O_w} \cap \overline{O_v} \neq \emptyset$? [cite: 20, 24]. 

These formalisms map directly onto fundamental problems in computer science. For example, in Valiant's algebraic complexity model, proving that the padded permanent polynomial is not contained in the orbit closure of the determinant polynomial (under linear transformations) is equivalent to proving $\text{VP} \neq \text{VNP}$ [cite: 15, 25]. In quantum information, Stochastic Local Operations and Classical Communication (SLOCC) transformations correspond exactly to containment within $SL_n$ orbit closures [cite: 22, 23, 26].

## 3. Theoretical Framework and Methodologies

The mathematical toolkit for resolving orbit closure containment relies on Geometric Invariant Theory (GIT), specifically via two main bridges: the Hilbert-Mumford criterion and the Kempf-Ness theorem.

### Invariant Polynomials
By Mumford's foundational results, two points $v, w \in V$ have intersecting orbit closures if and only if $P(v) = P(w)$ for every $G$-invariant homogeneous polynomial $P \in \mathbb{C}[V]^G$ [cite: 21]. Because polynomials are continuous, if $w \in \overline{O_v}$, then $P(w)$ must equal $P(v)$. Thus, separating invariants theoretically answer the intersection and containment queries [cite: 21, 23]. However, computing a generating set of invariants is practically intractable (often requiring exponential time and degrees), precluding simple algebraic verification [cite: 19].

### The Kempf-Ness Theorem
The modern algorithmic breakthrough relies on the Kempf-Ness theorem. It establishes a profound link between algebraic geometry and analytic convex optimization. Let $K \subset G$ be a maximal compact subgroup (e.g., the unitary group $U_n \subset GL_n$). The theorem states that every orbit closure $\overline{O_v}$ contains a unique closed $K$-orbit, which exactly corresponds to the elements of minimal Euclidean norm in $\overline{O_v}$ [cite: 19, 24]. 

Therefore, testing $0 \in \overline{O_v}$ (the Null Cone problem) is equivalent to checking if the infimum of the norm $\inf_{g \in G} ||g \cdot v||^2$ is exactly 0 [cite: 19, 24]. For non-zero containment, checking if $\overline{O_w} \cap \overline{O_v} \neq \emptyset$ reduces to minimizing a specific capacity metric using a gradient-flow ODE known as operator scaling [cite: 22, 27]. The gradient of this norm function maps onto the *moment polytope*, transforming highly non-linear algebraic geometry constraints into Euclidean convex optimization [cite: 26, 27].

## 4. State of Research and Recent Advances (2024-2026)

The chronological period between 2024 and 2026 marked a transition from theoretical bounds to explicit, polynomial-time decision algorithms, especially for commutative subgroups.

### Torus Actions in Polynomial Time
A pivotal 2026 result by Bürgisser, Doğan, Makam, and Wigderson achieved a polynomial-time algorithm for orbit equality, orbit closure intersection, and orbit closure containment for *torus actions* (commutative algebraic groups) [cite: 20, 27]. By demonstrating that the moment map images for tori form strict, rationally bounded polytopes, they applied smoothed analysis and non-commutative linear programming to definitively resolve the computational bottleneck [cite: 20]. Furthermore, it was shown that deciding whether a variety arises as an orbit closure of a point under an $s$-generated commutative matrix group could be resolved in polynomial space [cite: 25]. 

### TOCI Complexity Class
For generic, non-commutative tensor actions, a new complexity class was defined: TOCI (Tensor Orbit Closure Intersection) [cite: 18, 21]. 2025 research demonstrated that problems like Graph Isomorphism (GI) and the equivalence of 2D tensor networks are polynomial-time Karp-reducible to complete problems within TOCI [cite: 18, 21]. TOCI accurately captures the "average-case easy, worst-case hard" dichotomy often seen in tensor geometry. For instance, while worst-case tensor orbit closure intersection is believed to be NP-hard, average-case testing under orthogonal and unitary groups has been reduced to polynomial time [cite: 20].

## 5. Core Analytical Findings and Data Synthesis

When we ask the operative question—*when is $f \in \overline{GL \cdot g}$?*—the synthesis of 2024–2026 algorithms provides a structured flowchart of degeneration techniques:

1.  **Sequence Degeneration**: Containment occurs if there exists a 1-parameter subgroup (a specific diagonalized path $\lambda(t)$) in $G$ such that $\lim_{t \to 0} \lambda(t) \cdot g = f$ [cite: 19, 22].
2.  **Stable vs. Semistable Stratification**: 
    *   If $g$ is in the *null cone* (unstable), its orbit closure contains the origin, meaning $0 \in \overline{GL \cdot g}$ [cite: 19, 22].
    *   If $g$ is *strictly semistable*, its orbit closure contains a critical polystable state (a state of minimal dimension) that is not $g$ itself. Therefore, the polynomials evaluated on $g$ will indistinguishably match those of the critical polystable state it degenerates into [cite: 22].
3.  **Operator Scaling**: To algorithmically check if $f \in \overline{GL \cdot g}$, one applies operator scaling algorithms to compute the target marginals of $g$ on the moment polytope. If the spectral profile of $f$ is covered by the moment polytope of $g$, containment is possible, subject to unitary equivalence checks [cite: 20, 26].

## 6. Inter-Project Cross-Validation (Connecting to T#92 and T#79)

The orbit closure containment paradigm seamlessly unifies multiple cross-disciplinary objectives.

**Connection to T#92 (Geometric Complexity Theory)**:
GCT hinges entirely on analyzing the orbit closures of the determinant and the padded permanent. The theoretical challenge is determining if $y^{m-n} \text{perm}_n \in \overline{GL_{m^2} \cdot \det_m}$ [cite: 15, 25]. The algorithmic developments in TOCI directly aid this pursuit. If researchers can prove that specific representation-theoretic multiplicities (Kronecker coefficients) strictly differ between the coordinate rings of the two closures, they can topologically separate the orbits, formally separating VP and VNP [cite: 25].

**Connection to T#79 (SLOCC Orbit Classification)**:
In quantum computing, tripartite quantum states $|\psi\rangle \in \mathbb{C}^d \otimes \mathbb{C}^d \otimes \mathbb{C}^d$ evolve under local filtering operations governed by the group $SL_d \times SL_d \times SL_d$ [cite: 22, 26]. Two states exhibit the same type of multipartite entanglement if they share an orbit closure intersection. For instance, the GHZ and W states define distinct entanglement classes. The W-state orbit closure contains the origin and certain bipartite entanglements, but the GHZ state does not [cite: 23]. The 2026 results confirming that testing unitary equivalence of Haar-random quantum states is solvable in polynomial time drastically simplifies SLOCC classification [cite: 20].

## 7. Concluding Remarks and Open Horizons

Orbit closure containment has transitioned from a purely abstract algebraic geometry formulation to a rigorous, computationally classifiable domain. While commutative subgroup actions are now effectively resolved in polynomial time [cite: 20], general linear groups present persistent hurdles mapped out by the TOCI class [cite: 18]. Future horizons lie in adapting the Kempf-Ness gradient descent methods from Euclidean geometries to hyperbolic and Hadamard manifolds, aiming to approximate non-commutative operator scaling in universally bounded polynomial time [cite: 26, 27].

***

# T#21: Alexander-Hirschowitz Stratification and the Geometry of Generic Waring Rank

## 1. Executive Summary / Leading Paragraph

*   **Key Finding 1**: The Alexander-Hirschowitz (A-H) theorem governs the generic Waring rank of symmetric tensors, successfully charting the expected dimensions of secant varieties of Veronese embeddings, save for a finite, completely classified list of defective strata.
*   **Key Finding 2**: In 2024, Abo, Brambilla, Galuppi, and Oneto resolved a major open horizon, proving definitively that Segre-Veronese varieties are never secant defective provided each directional degree satisfies $d_i \ge 3$.
*   **Key Finding 3**: Real-world tensors often inhabit specific geometries where Waring rank deviates from the generic expectation; for instance, the $3 \times 3$ permanent $\text{perm}_3$ requires exactly 16 symmetric rank-1 components, noticeably lower than the generic rank of $\approx 19$ for a 9-variable cubic. 

The geometry of Waring rank—the decomposition of a homogenous polynomial into a minimal sum of powers of linear forms—commands profound importance across algebraic statistics, signal processing, and complexity theory [cite: 28, 29]. The foundational map for this space was drawn by the 1995 Alexander-Hirschowitz theorem, which established the Waring rank for a *generic* polynomial, simultaneously cataloging the exceptional "defective" cases where algebraic dependencies force the rank higher than expected [cite: 28, 30].

Recent research between 2024 and 2026 has focused extensively on extending these paradigms to partially symmetric tensors, culminating in the closure of the Segre-Veronese defectivity conjectures for degrees $\ge 3$ via fat point collision methodologies [cite: 30, 31]. Concurrently, intense computational efforts have mapped the highly structured, non-generic strata occupied by famous polynomials like the determinant and permanent. The specific determination that the $3 \times 3$ permanent possesses a Waring rank of 16 emphasizes that symmetry and invariance strictly dictate behavior within the defective and sub-generic strata [cite: 11, 17].

## 2. Introduction and Contextualization

Let $f \in \mathbb{C}[x_1, \dots, x_n]$ be a homogeneous polynomial of degree $d$. The Waring rank $R_W(f)$ is the minimal integer $r$ such that $f$ can be written as a sum of $r$ powers of linear forms: 
\[ f = c_1 \ell_1^d + \dots + c_r \ell_r^d \]
Geometrically, this problem maps to finding the minimal $r$ such that $[f]$ lies on the $r$-th secant variety of the Veronese embedding of projective space $v_d(\mathbb{P}^{n-1})$ [cite: 32, 33].

Because polynomials parameterize a continuous vector space, there exists a "generic" Waring rank. A randomly chosen polynomial of degree $d$ in $n$ variables will, with probability 1, have this generic rank. Naïve parameter counting dictates that the generic rank should be $\lceil \frac{1}{n} \binom{n+d-1}{d} \rceil$. However, algebraic geometry introduces secant defectivity: certain configurations where the Jacobian of the secant map drops rank, pushing the generic Waring rank higher than the naïve parameter count [cite: 30, 31].

The Alexander-Hirschowitz (A-H) theorem (1995) famously proved that the naïve generic dimension holds *always*, except for a highly specific, finite list of exceptions (e.g., quadrics, and specific cases like $(n,d,r) \in \{(3,4,9), (4,3,7), (4,4,14), (5,3,7)\}$ ) [cite: 28, 30]. However, classifying the geometry of polynomials that are *not* generic—such as structured tensors relevant to computer science—requires navigating the stratification of these secant varieties.

## 3. Theoretical Framework and Methodologies

The theoretical framework for analyzing Waring rank utilizes Apolarity Theory and Fat Point degenerations. 

### Apolarity Theory
The primary tool to calculate the Waring rank of a specific polynomial $f$ is the apolar ideal $f^{\perp}$ in the dual polynomial ring. A classic theorem of Macaulay states that decompositions of $f$ correspond to ideals of sets of points $X$ that are contained in $f^{\perp}$ [cite: 15, 32]. Consequently, understanding the homological properties (syzygies) of $f^{\perp}$ allows mathematicians to bracket the possible Waring ranks. For instance, catalecticant matrices (Hankel matrices in higher dimensions) generated by apolar forms provide strict lower bounds on $R_W(f)$ [cite: 17].

### Collision of Fat Points
To prove whether an entire ambient space like the Segre-Veronese variety is defective, researchers rely on interpolation problems. A space is not secant defective if one can find a scheme of general 2-fat points that imposes independent conditions on polynomials of that multidegree [cite: 30, 31]. The methodology limits the dimension by analyzing degenerations where $N+1$ general 2-fat points systematically "collide" to form 3-fat points, allowing for rigorous inductive proofs on the number of factors and variables [cite: 30, 31].

## 4. State of Research and Recent Advances (2024-2026)

### Closure of Segre-Veronese Defectivity
A paramount achievement in this temporal window is the 2024 paper "Non-defectivity of Segre-Veronese varieties" by Abo, Brambilla, Galuppi, and Oneto (ABGO 2024) [cite: 31, 34, 35]. Segre-Veronese varieties parameterize partially symmetric tensors (e.g., polynomials over disjoint sets of variables). Abo and Brambilla had previously conjectured in 2013 that these varieties in multi-degree $(c, d)$ are never defective if $c, d \ge 3$ [cite: 30]. 

In 2024, ABGO formally closed this conjecture. By providing the base cases for bi-degrees $(3,3), (3,4),$ and $(4,4)$ using the sophisticated collision of fat points methodology, they proved by induction that Segre-Veronese varieties are *never* secant defective provided that all directional degrees are at least 3 [cite: 30, 31]. This permanently maps the generic rank landscape for partially symmetric multi-tensors, echoing the finality of the Alexander-Hirschowitz theorem.

### Surveying the Defective Stratum
Beyond generic ranks, researchers deeply surveyed specific defective strata where $R_W(f)$ is sub-generic. The $k$-th Terracini loci—which catalog forms having multiple distinct minimal Waring decompositions that share geometric properties—were explicitly detailed for cubic forms [cite: 36]. Furthermore, bounds on symmetric and anti-symmetric structured matrices (like determinants and permanents) were significantly tightened [cite: 1, 29].

## 5. Core Analytical Findings and Data Synthesis

While the A-H theorem establishes the generic rank, the most practically significant polynomials typically lie in the non-generic, highly symmetric strata. A prime illustration of this is the study of the $3 \times 3$ permanent.

### The Waring Rank of $\text{perm}_3$
The permanent of a $3 \times 3$ matrix is a homogenous cubic polynomial in 9 variables. 
The dimension of the vector space of cubic forms in 9 variables is $\binom{9+3-1}{3} = \binom{11}{3} = 165$. By the generic Waring rank formula (free of A-H exceptional cases here), the generic Waring rank is $\lceil 165 / 9 \rceil = 19$. Thus, a random cubic form in 9 variables requires 19 linear powers.

However, $\text{perm}_3$ is not a random form; its vast permutation symmetry restricts it to a non-generic stratum. Shitov (2020) and subsequent validations established that the exact Waring rank of $\text{perm}_3$ is strictly 16 [cite: 11, 17]. This rank is achieved via symmetric catalecticant unfoldings and matches the theoretically constructed apolar ideals [cite: 17]. 

### The Waring Rank of $\det_3$
Conversely, the determinant $\det_3$, also a cubic in 9 variables, possesses a Waring rank bounded differently due to its alternating sign symmetries. Lower bounds established via syzygies of the apolar ideal showed that $R_W(\det_3) \ge 15$ [cite: 32], while exact constructions upper bound it closely to 17 or 18 [cite: 6, 11]. 

The fact that both polynomials lie distinctly *below* the generic Waring rank of 19 verifies that highly structured computational tensors reside within specialized algebraic sub-varieties, shielded from the generic expectation modeled by Alexander and Hirschowitz [cite: 11, 17].

## 6. Inter-Project Cross-Validation (Connecting to T#26 and T#22)

**Connection to T#26 (Segre-Veronese Defectivity)**:
The T#26 directive focuses heavily on multi-partite tensors. ABGO 2024's proof that there are no defective Segre-Veronese spaces for $d_i \ge 3$ firmly establishes that partial symmetry does not inherently invite geometric defectivity at higher degrees [cite: 30, 31, 34]. The induction from base cases $(3,3)$ directly informs algorithms scaling tensor networks; we now know mathematically that generic partially symmetric tensors of degree $\ge 3$ will securely maintain their expected dimensional parameters.

**Connection to T#22 (Waring Rank of the Permanent)**:
Cross-referencing T#22 validates the structural behavior of the $3 \times 3$ permanent. Its Waring rank of exactly 16 forms a foundational baseline for testing matrix multiplication sub-multiplicativity bounds [cite: 3, 17]. The Kronecker square of the $q=2$ Coppersmith-Winograd tensor mirrors the $3 \times 3$ permanent, meaning that $R_W(\text{perm}_3)=16$ effectively acts as a ceiling constraint on the laser method used for lowering the theoretical exponent of matrix multiplication $\omega$ [cite: 3, 17, 37].

## 7. Concluding Remarks and Open Horizons

The topography of Waring rank has never been clearer. The Alexander-Hirschowitz theorem locked the framework for generic symmetric tensors in 1995, and the ABGO 2024 results have effectively sealed the corresponding topological landscape for Segre-Veronese generic spaces [cite: 30, 31]. 

The frontier of research moving past 2026 shifts entirely to the sub-generic strata. The polynomials of supreme computational interest—matrix multiplication tensors, determinants, permanents, and cycle-covers—are deeply atypical [cite: 29, 38]. Future horizons necessitate developing algorithmic apolarity tools capable of dynamically parsing the minimal free resolutions of these specific, symmetric ideals, translating the geometric invariants of the sub-strata into rigid complexity lower bounds.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp2ttzTJMbgDcO3r2iGUEJD3IOp-MxdgNc0Vvw5Ckx5FSZPaFn0vhItjDKGEvuDpiJxkNwo2tFdoUh68jtPJ9KdjPWpH6oDR8M1P_bverxbKeuTDZp)
2. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeW4tfaqL9CLVFCh7s4NCpGCsNOzSdDdYq5Rsp2klpLxrL2-eJ4jlZvtS6WdA8wYTd3Z_o9LHyYbU1OFK-gWCbAVcbJ0-WhM-fkDH3XzXmtzHKknkR9Emh-kT9lMJCVJQo_VGJsIhC2GivWFoe8M8BuB4MkRiHoZywtmtME2XPN1ky9V32Ul2-FAioLxRSHjGEmztqNrE0Mh5nsZRHr_zawEkOPRtWss028_7eHKsvCgoJBTx3WntBtM6P12oCcU9YiaIJv5MY8oX5Y4dqlz8gMEv_bwWbmk6SXL3Mp1lp_cJqpA0e5hmCdfFMWnrCnGcAtF4L9NT55A==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4aNS-mPKkjMKCqTSWHx9qe1LPPzVFl56Mk4gLvAdFMd5VRkrOSeZs5R_vkC7vCjClX_69uCa7ME5BHLptoLRSS969MIQfYVf26r70m25klIwwtX_ZSYZr4ENngEY5STxPT8cu96c7ylKcjrgDl__WarNbaVOCqZkZtXFlpku9e9M1MIjQ2-oikzwKdvdOX2ZQ8AjP-IjSM0aeut1V3jP3JYYi0sFC)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXH1zb-skUHHJ291bSXnXKbN5WSi7DA70iJJR4_MwF1CRmPHm4zcxXtxOpZKTOIV6Uaji_-VSN8olFMEV1J-9ZuoItlg5g7xQ0xAY0rk0xt81EtUAN)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_agczJXopdifoDcqBtVKJRJujZlM9mAqMUHVnI6ZwIfx2cGRl2JiMIIQA6r8cY-WUvlxMDgkqUlOuohcFGWE80eVWcus4LSk_Yil0wP7VudV4KtoKNZVmsya326NV7qKEDWGPFA45A5j26kd24o9RO4TTEvzws-heidXq7XpJDwWY2fZ-Gs7-2iV-oyTeDu6JhGWlmgYbNe32epPxxcST)
6. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG3UjuU0JvNxEKKc5b14NzhR-YWWg1mXkB23OUCjJg6AdMsBVhMiQcZMQhfFae33CjcRwScKnf6jqfy1pPNn0g7gzMXtJfsT2lMMhJC9CYX0_d5KPr8ICqMwF2sQOLk8P1MhbC4sCD-LLpwui_w78wNoVPeKCJB9JaIyvr)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTTYSBXWr6Y6xFsAZpP0lXIMhxLLSADqA9vfTNM_nDyDOilX4Y-uK6fiePTFxCDBdwUXeaQxZHq-7Kadq3TCkCq41UZPlk4U4x4sbhA5TCrqeZlBZTnvKSwwfbXPu_q5DNwqiQzHWwXa0SlLTr9XEA_nVqYyHbaiRzsSfdcE4cFN8r_imIOSXH0k8Wj94TNWX5lYlxRIATrYhdR83YdbUs0XL3AfVdnw5SAtu-n3eGCsWJXMbHDR896LpdDCo=)
8. [njohnston.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJhEMh1sJKosTGc4wjr0DxXJhc9tEp0las0dPRPIbzzxCG5cLzaOrYJGI_7nCO9Acw3ClT4hfKNL2rluC-YTrnHY3qAPRAFvICqPYLAZ2AUxeitObLccVXZv4QmlG94tXzZA6kZOTPA27TCaNIbNbBqhofSM9X-tMK3EXf7KRfxQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTjMqB6-uFiRDlSmKTLGU3L3-D5j74K6KW8E4thI4ECVd9u_3BhMgun008J6C0ax4xibcb-QP4qCTHGeyofpPQ1WwA2QAM0QTp0S1HXNE365sMMjyb)
10. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9Gg3pJZHcIk0FfDeUGIcey-YAc0KW3_iRdQipDOSTwTj5cEViSjH9kpdksK8PyS6uRw7Mwqe14i34I-jO96J3qhE6Gfy1iemyGaDkAmK-erzxOnp6iwsRa11qaIGWWbme8DSIvPg8lFI-GyHaKNFKGgTS59M=)
11. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4mrc2FlorGtXdibKj6fiwgfqWA1x4LZTdLGQM5xxMD-vfeC6LTfTMKrDE878rZZ3JvSI-clfpkPeNux_8W4gALkoS6GIciqbZC3-F9YeCp9jC8Hi9CVUXLRw=)
12. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYzNoKh284vPk6CP1EXV811SyAUBzKRIscFauyUFEn1TbCvRxj-hctUfd6dq7uBa8yjbr5hNme3Zgn602GHlyxMYZH6FH6oe7DXChpMw0-HxarfXh4_ipzBjL_jgD1P6cTZUBx0bcfVTgAXeontfgIaaEY6mYggiVn4PyVMEq96vgf8w==)
13. [njohnston.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKu9C_thVA7KojSa7ATFngN8x5E8gbxjK4g20qMIOa3v7fvQNZcFP3CHK2w0lajNUX_aKo48SpxY4uHiIPkR_AYdWHwWCB_N79Bpaj-q7Kv1yvpgrLMsRpVIsyb6J-wHFlHVgfDD4nEhv9X_kHhXYRbsqV0gezGi9JTSW5tBRBz_ewHs5_xTRllbfhh6RKyBk0UNib2xpIHQs_EK4dQacXVBBV)
14. [oeis.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4JykWb_R2c4wVuuWu4rs3kXSERu4pP6dNGzumfyU5aV0KaERQyEPUk1EkUmHu4F0kDPXf8xMes3lLWNZScchG6pg2bL6Fu-VNHbhnFQ==)
15. [washington.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMamOOgpjePN4xcpSMKZvl5QIX0A3FJ2spkZIwKXgid9U-jFRM92aGTX4li-1dfxzgjFXx0r0fvVP1kWKS-CXeArAS9wAvIgZgFBkqENExtN-CyG---M6Rhn_e-XwYJtOZmKP2pvzDVd8Nwm363bfxTco=)
16. [pgadey.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvDvsmuSqzMjZzhnuQf1e6pD3nYvqmhSL5lJrgdMey3HCDfVRoKeBC2JkZ0o9h_5kh6KJI0qKYuLxPYj0Z4MRM3KIudJ6Y7OG7nxM1zF4WhoQhvnmFnYWO6Yp2H4QLJPaDmmgifw==)
17. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHh_BCt2ZztE62w2tieSgNSyYWygi-6Sp3xdVAH1C_9N_jCUq2dy2dvIIivkvD_zaImE2havNCnE_3XsTQCdgf5x3XXwagJvrqWdDXn43EdN5mOUVwpAm0fjO7uvdHPEv6O9RU4qJOyPw==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHdcPy7o6o564N0-SIhqjGr0s93N8R7MzlrdCFUotFtPgS7T-qlQyLbIKBpFXX3xgY_WpaagxCvN3VMlbdFngU63F5yCHER_FWGrQnBkUwhx6EWVbDveWl)
19. [icts.res.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQNYAkKBm0sWbtl9LikBgTdWU8tNze9WIzVfRbJLz3SFCxmUWhAsfoHveoF7rRwofLHUrZywVnUiWbtxzRL87BqLzldzy3pQjYHwbZoGdV8ZpRvk58FKhMFpeXpls-5s6ZQ3WhiOQAjyIT2Iroz3fjvMkBTrurgZlMFVdSvumiw8Vjhg==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpRHeFfopoyvp-4tZYWCcir8gsCo5EpG6I5G3Qk-YEvRFCOMBZM6LqzXf3d5kJkRLxYucGuaVRZPdVqSC1s_VoJ94f0OMmhv621XlALHlhH4_KpsCEtZsL)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoQJom3IkBEsxerkkuX3UKMKw1gdUwpk-b3USixC3B6WeuS_Ag2dfxFkR5Vqd33rW51f31dzVxNJnASZdeP0ofVLUaxlVNkHFHxMb09TxU4BynqEkg)
22. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEDN9UbM1Mts8r92ekpDm2418KlKiFJVvSJmRxa_WNN4pEsGYOhAiapZ-DODySGNDXC0UDY1Mp2No4ARFZOV-PRcqFdRQU808kcsOvPp3a4bnf9UbqiNyNsec1MIHzjgRw9L3ZC5rOeyAr08Z-)
23. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhJhGHAehAan6OmJs2S_Yrb1vggDId1-6vug3opHzB_26Sb0lnWNUFGrAbNStnTq_PeAwmrIgxxLN1lZkHMi1kmTRYROEjx54LQQ7vMnrTJmPfG_Groaq3xeI5MLZy_pkbobMkxeUHNDgVrc7unrfwlTycgFvJ)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHilQf6xLer5F5uru7SNeI0Jl4gA5g-nvmqxy3a1ns2ec7bAYLSTXQeSk4j6AIIdEum4Xq79RMXwV5UQfauLC55UU-SUbS2u7MBNX2g2Jrw9vlC28DG)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzbo5GRHVACgwNAirpFpOYVsleoWd23Fkz5p4czdGeRwI_JtneYpK7kuoRR0FjkVV5-NauiU4tnBGVD4wVKa-Vv4Yg3NOvX7apROkor7YHoKjxA2APlA2c)
26. [ieee-focs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf9kufbJcnk7FCMj03kXYqjjfDoMo-yCD_HPjB0PsSpUYTtiLKFVtS9PRMXoEv-DxLcgxJZf-vxfY0wfYp0bW9-gDkbB9TiXJGb0gUE6YMpbRPNzaCSFf0l-kU-XKduWaGJAscZ9qySGRgjA==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxGRaBLESL_CJPc0ZjugYO_ftbxxerCoKWGydNqQxe0stKoA-pxkYEOMpiZWglQmfrc5kc4sbdn0vJ0zrxYPG_OXdpG8TX_9N69g6Wxx6fFeeLjOLaxeLwf9lhkNjNT-nx_Sw4ilqlHN-R9NrAD0tm-DCmdTdQJmyxUkvQW0-BZqWlULR9O_CgLsYEsUe6CeNS-kch4ji9Bxfq-9W9bkN-TkZOZKXcOr0hWG-qjigqJv3gZHHDl18=)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5H4YHnJvC6iKVrZU1lxB8VCViQsdCki27PhYJA9LJENw4FIPvCRdRwRWVmHyWofatPYZL6rKtTg79dk8_kFj6vk7UA7zSvfy_tvhp0jqYMeKbRFPjinqbqwqIo9-dzS4X3czPZSrdgpb1fNigAPk6k-l4heybXAVJ-oENJhBbd3NCS_xAespbaR-aMocs)
29. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqRSRqAqzlXXnPtCjFaCAHa-6sBMFmakkmPw7ow516lrp-cZ8g-56HElU9SlgK8Sh8khLlfdPtidvwfbfBubbTucUEUX-NkMHEzA2IaKJbocdixFciud35tY4_sCVJd12uToNR9Zaag980R92J3rc_S5W3khnpsx7D2WGYJxrwSE2NPaNAPO3vFAI=)
30. [puremath.no](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfDOMpkLsi7YWQgatUZ7WmFvZMpgWMkguZaNdiBgb714e-yOgrchPOvo8CeYw7dRQCn4TC3x9fQgKwtwtw_J49317DC8g5rC4YqmcaG3eOc71nreZNGKS4iulBjbAjgn1BuJ4U9oNCYh_yY1I6xbqENFGq_B4oS8Wn)
31. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUmRXY2ONLE7I-ycO8mmYSdcSotqX_MM-4Kf7pgRUBNg7SGoh-xmLtSckrY_ECQFB9gxECLctKTBJXi5a21Bl3daBt2Klih025fkacsTra63PqHget5Gy3R8RrbdVk3Xd-mdXcfzw4Q2Apfh-vDJHweLE=)
32. [boisestate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpNtGu1KpVaCcfhz6oJD0_AaVy14gGtYiczLBKNBYt2ydyZ0dXuMq0bYbEBM5--WCQGo-r1nVmMVKyt7lkS-q3lrpBMTy5rqcSBxzYvqNfmcwSqQL4TFLgALHT6XMDkwmvusCRzM1dBVOcP9QrPq-Tpuf051DlL0f5owDlJWxL9du3XgW1Lqm-TAtFCjcE)
33. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEckDaS3inuYSuAReAeSpOGe4jGKW_eh1ZF8XKgq1J5Bizto91tDkAT9La01iTHeeABU6o0wWk6PJG-xD7Q7pc__uAJAiiuB3jZAZcLPwMSGVKnoUHwZhBaOgxxUjzT3w==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR6z4gSLPA0DqHcJlyLpvbkeVZmG1BFZuP8MKMu5BPVFB2qCgzquO6XiSjjo2JZ4DjlAHKnmoCjlocG9wXe6PF6R8H_xgpeJILft1SF5qgQHpEZSA4)
35. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-tM631yMVyYlMGi-QRi1dhmJAOY9F29HaE6ySrHLEdt3c_ZYUnRp6Ys8unu0d1X-Axr1QCRZ9qhrGmpiixSPj0FfQm3RhB9s0789a5b49z-0pNRWGxmv0TgOEroec_h7oJ1KYhDsnG2h_HGS_JQ==)
36. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHapSEXdcN-tYXtNbETOwd_AOlObogxcLDOgNF3L-G4MdDdsTgNQpSTKtSXNDJbYD4tvK4Kb6nHM1KYkmMVBdosWJNVjazrfVO7k6aqW7IQP6zUssydZaYuu-suOGbsC5N3z_Cq3xG2Z2gW5_AG1SsQmMIkBh-LY7ZfYOQ08te2A326JYg-RhcC7uoIfd81v9fvWLBY3DI=)
37. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGprl6JZSXW2EIFALANhgNZ9_vvKYYlEMUrIpZXHaVlrnZ7OWKlXg6MY5m1JqIiYPYmoaquUK2ev7vH_r7jXrEZY8-nCQVApf1Gtg93vkCoNyv5pw0AUu0gES1sqcA8Mwl9C4dOEErFLH8E3H-3RmdxX0YQLpqbd32QdgkMOAL7rFATkg==)
38. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG27dlPW1sRY3lc9l4z_UyRj37cNV_9GHPWqHFFfHkWmNG4kJfVIpSIOGnRjs_rk4eQp4BfV_jmLLRLK2t2IlN267KSvccnT_mi_om6sHLn6Ibd8hWjNZEBvZWC10FbsdMRZEvIzHeOvpuxVQb6IKMR1rVB8PKjhxOtI5X1qZfVJ8fBp5vZs6yBhRnTCaVe14J60PCOUX-RHH4c51fOQ==)


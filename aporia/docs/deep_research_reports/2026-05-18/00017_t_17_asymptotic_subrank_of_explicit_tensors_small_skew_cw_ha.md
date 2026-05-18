# T#17 Asymptotic subrank of explicit tensors (small/skew CW + Hadamard)

**Pythia queue id:** 17
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdNWHNMYXNINUMtNm8xTWtQM0tLcTJRYxIXTVhzTGFzSDVDLTZvMU1rUDNLS3EyUWM
**Elapsed:** 372s
**Completed at:** 2026-05-18T20:55:02.232091+00:00

---

# Asymptotic Subrank of Explicit Tensors: Coppersmith-Winograd, Skew Variants, and Hadamard Structures

### Key Points
*   **Asymptotic Subrank and Rank:** The asymptotic subrank and rank of tensors are fundamental metrics in algebraic complexity theory, governing the computational cost and intrinsic value of tensor transformations, particularly for matrix multiplication algorithms.
*   **Coppersmith-Winograd (CW) Barriers:** Traditional Coppersmith-Winograd tensors, which have historically driven the best upper bounds for the matrix multiplication exponent $\omega$, face proven limitations. Research suggests that methods applying the Universal Method to $CW_q$ tensors cannot yield an exponent better than 2.168.
*   **Skew Coppersmith-Winograd Tensors:** Skew-symmetric variations of the CW tensors ($T_{skewcw, q}$) exhibit profound sub-multiplicative behavior in their border ranks. For example, the Kronecker square of $T_{skewcw, 2}$ (the $3 \times 3$ determinant) has a border rank of 17 (dropping from a maximum 25), and $T_{skewcw, 4}$ drops to 42 (from 64), opening new avenues for Strassen’s laser method.
*   **Discreteness and Gaps:** The values that the asymptotic subrank and slice rank can assume for any nonzero 3-tensor are highly constrained and discrete in lower bounds. Identified gaps demonstrate that the asymptotic subrank can strictly take the values 1, approximately 1.88, 2, or values greater than or equal to 2.68.
*   **Hadamard Rigidity and Transformations:** The Walsh-Hadamard transform, long presumed to be a highly rigid matrix suitable for proving arithmetic circuit lower bounds, has been mathematically proven to possess surprisingly low rigidity. Furthermore, geometric frameworks over Hadamard manifolds facilitate the computation of quantum functionals used to characterize asymptotic tensor spectra.

### Understanding Tensor Complexity
Matrix multiplication is a cornerstone operation in modern computing, underpinning everything from machine learning to physical simulations. For decades, computer scientists have sought the theoretically fastest algorithm for multiplying matrices. This quest revolves around studying the properties of "tensors"—multi-dimensional grids of numbers that can represent the fundamental mathematical operations required to multiply matrices. Strassen’s theory of the "asymptotic spectrum" provides a framework to measure the cost (asymptotic rank) and the inherent informational value (asymptotic subrank) of these tensors.

### Blueprints and Speed Limits
To discover faster algorithms, mathematicians use specific tensors as structural blueprints. The most famous of these is the Coppersmith-Winograd (CW) family of tensors, which has led to every major algorithmic speedup since the late 1980s. However, recent mathematical proofs have established a "speed limit" for these specific blueprints, confirming that they can never prove that matrix multiplication takes optimal time (an exponent of 2). To bypass this barrier, researchers are now investigating "skew" versions of the CW blueprints. These skew tensors pack information in a highly irregular, asymmetrical way, allowing them to mathematically compress operations much better than their traditional counterparts when squared or cubed. Concurrently, other mathematical objects called Hadamard matrices, which scientists thought were rigidly complex, have been found to be surprisingly flexible, changing the landscape of how we establish limits on computational speed.

***

## 1. Introduction to Algebraic Complexity and Tensor Parameters

The algebraic complexity of matrix multiplication is traditionally encapsulated by the exponent $\omega$, defined as $\omega = \inf \{ \tau \mid \text{two } n \times n \text{ matrices can be multiplied in } O(n^\tau) \text{ operations} \}$ [cite: 1, 2]. The hypothesis that $\omega = 2$ remains one of the most prominent open problems in theoretical computer science. The primary vehicle for bounding $\omega$ is the study of **tensors** and their various ranks. 

Let $A, B$, and $C$ be finite-dimensional vector spaces over a field $\mathbb{C}$. A tensor $T \in A \otimes B \otimes C$ is said to have **tensor rank** one if it can be written as a simple tensor $T = a \otimes b \otimes c$ for $a \in A, b \in B, c \in C$ [cite: 1, 2]. The tensor rank of $T$, denoted $R(T)$, is the minimum integer $r$ such that $T$ can be expressed as a sum of $r$ rank-one tensors [cite: 1, 2].

Because tensor rank is not semi-continuous, an arbitrarily small perturbation can change the rank drastically. This necessitates the definition of **border rank**, denoted $\underline{R}(T)$, which is the smallest integer $r$ such that $T$ is the limit of a sequence of tensors of rank $r$ [cite: 1, 2]. In algebraic geometry, $\underline{R}(T)$ corresponds to the smallest $r$ such that $T$ lies in the Zariski (or Euclidean) closure of the $r$-secant variety of the Segre variety [cite: 3]. 

### 1.1 Asymptotic Rank and Asymptotic Subrank

To understand the complexity of operations evaluated on massive scales—such as multiplying enormous matrices recursively—we look at the Kronecker powers of a tensor. Given $T \in A \otimes B \otimes C$ and $T' \in A' \otimes B' \otimes C'$, their Kronecker product $T \boxtimes T'$ resides in $(A \otimes A') \otimes (B \otimes B') \otimes (C \otimes C')$ [cite: 2]. The $N$-th Kronecker power is $T^{\boxtimes N}$ [cite: 2].

The **asymptotic rank** $\tilde{R}(T)$ and **asymptotic subrank** $\tilde{Q}(T)$ are defined as:
\[ \tilde{R}(T) = \lim_{N \to \infty} (R(T^{\boxtimes N}))^{1/N} \]
\[ \tilde{Q}(T) = \lim_{N \to \infty} (Q(T^{\boxtimes N}))^{1/N} \]
where $Q(T)$ (the subrank) is the largest integer $q$ such that the diagonal tensor $\langle q \rangle$ can be obtained from $T$ via linear maps on its three factors [cite: 1]. Subrank operates as the dual to rank: while rank measures the minimal cost to compute a tensor, subrank measures the maximum size of independent computational components (like independent scalar multiplications) that can be extracted from the tensor [cite: 4, 5]. For the matrix multiplication tensor $M_{\langle n, n, n \rangle}$, knowing the asymptotic rank reveals the exact arithmetic complexity of matrix multiplication, as $\omega = \log_2(\tilde{R}(\langle 2,2,2 \rangle))$ [cite: 1, 6].

### 1.2 Strassen's Asymptotic Spectrum

In 1986, Volker Strassen established a profound theoretical framework—the asymptotic spectrum of tensors—to evaluate these parameters [cite: 7]. By considering the collection of all tensors equipped with direct sum $\oplus$ and Kronecker product $\boxtimes$, one forms a commutative semiring [cite: 8, 9]. Strassen defined a spectral point as a monotone semiring homomorphism $\phi$ from the semiring of tensors to the non-negative real numbers $\mathbb{R}_{\geq 0}$ [cite: 9]. 

Strassen's Duality Theorem states that a tensor $T$ asymptotically restricts to $S$ (denoted $S \lesssim T$) if and only if $\phi(S) \leq \phi(T)$ for all spectral points $\phi$ in the asymptotic spectrum $\mathcal{X}$ [cite: 5, 10]. Consequently, the asymptotic parameters become dual optimization problems over the spectrum:
\[ \tilde{R}(T) = \max_{\phi \in \mathcal{X}} \phi(T) \]
\[ \tilde{Q}(T) = \min_{\phi \in \mathcal{X}} \phi(T) \]
This framework vastly generalizes linear programming duality and relates strongly to the Positivstellensatz [cite: 8, 11]. Understanding the asymptotic spectrum essentially determines the exact mathematical limits of tensor decay and expansion under recursive algorithms [cite: 5].

## 2. The Coppersmith-Winograd (CW) Tensors and the Laser Method

The primary driver for algorithmic improvements in matrix multiplication over the last thirty years has been the Coppersmith-Winograd (CW) family of tensors, denoted $\{CW_q\}_{q \in \mathbb{N}}$ [cite: 12]. 

### 2.1 Definition of the CW Tensors

The basic (small) Coppersmith-Winograd tensor $CW_q$ of order $q$ is defined in a generic vector space formulation over three components. Its construction inherently possesses a core block that structurally resembles independent scalar multiplications, but bound together with error terms that must be carefully eliminated. The original CW approach used a highly symmetric tensor, which allowed an advanced version of Schönhage’s asymptotic sum inequality to isolate independent sub-tensors [cite: 13]. 

### 2.2 Strassen's Laser Method

Strassen's laser method is the central technique utilized to achieve upper bounds on $\omega$ using CW tensors [cite: 1]. The laser method zeroes out specific blocks of a large Kronecker power $CW_q^{\boxtimes N}$ by acting with projections (degeneration), effectively destroying the "entanglement" between distinct matrix multiplication blocks, leaving behind a direct sum of pure matrix multiplication tensors [cite: 13]. Because of the sub-additivity of border rank, achieving a low border rank on the initial tensor $CW_q$ implies a powerful upper bound on the matrix multiplication exponent [cite: 1, 14]. Utilizing the big Coppersmith-Winograd tensor, bounds on $\omega$ have incrementally decreased to $\omega < 2.373$ by algorithms from Le Gall, Alman, and Vassilevska Williams [cite: 1]. 

## 3. Barrier Results for Standard CW Tensors

Despite decades of intense scrutiny, progress using the CW tensors has stagnated. Recent breakthroughs in algebraic complexity theory have formalized exactly why this stagnation occurs: the tensors themselves face an insurmountable mathematical barrier.

### 3.1 The Universal Method and its Lower Bounds

The Universal Method, a generalized framework formalized by Alman, subsumes all known methodologies for deriving matrix multiplication algorithms, including the Laser Method and the Group-Theoretic Method (Cohn-Umans) [cite: 4, 12]. It maps a starting tensor $T$ into a sum of matrix multiplication tensors through degeneration.

Alman and Vassilevska Williams proved that when the Universal Method is applied to any Coppersmith-Winograd tensor $CW_q$, it cannot yield a bound on the exponent $\omega$ better than **2.168** (specifically 2.16805) [cite: 12, 15]. Even more constraining, earlier evaluations using the slightly weaker Galactic Method proved limitations on $CW_q$, but the 2.168 barrier rigorously kills the prospect of proving $\omega=2$ with standard CW tensors in the Universal Method [cite: 12, 15]. 

### 3.2 Irreversibility and the Asymptotic Independence Number

The barrier to achieving $\omega=2$ with CW tensors fundamentally relies on the concept of **irreversibility** and the **asymptotic independence number** (also known as the monomial asymptotic subrank) [cite: 16]. Intuitively, irreversibility characterizes the failure of Gaussian elimination (and its tensor equivalent) to strictly diagonalize a tensor asymptotically [cite: 16].

Christandl, Vrana, and Zuiddam demonstrated that evaluating irreversibility utilizes the asymptotic spectrum of tensors—specifically, two families of real tensor parameters known as the quantum functionals and support functionals [cite: 16]. The evaluation indicates that for the $CW_q$ tensor, the cost (asymptotic rank) and the yield (asymptotic subrank) do not converge tightly enough under the Laser Method constraints to allow full matrix multiplication compression down to $n^2$ [cite: 11, 16]. The "slack" for the $CW_q$ tensors is strictly greater than 1. Specifically, the slack for $CW_q$ satisfies $\text{slack}(CW_q) \geq 1.08$, mathematically forcing $\omega_{CW_q} \geq 2.16$ [cite: 8, 11].

## 4. The Skew Coppersmith-Winograd Tensors ($T_{skewcw, q}$)

Recognizing the hard barriers faced by the standard CW tensors, researchers sought alternative explicit tensors that might evade these limitations. Conner, Huang, and Landsberg introduced a novel variation: the **skew-symmetric Coppersmith-Winograd tensors**, denoted $T_{skewcw, q}$ [cite: 2, 17]. 

### 4.1 Structural Definition

A 3-tensor is considered symmetric if it is invariant under the natural permutation action of the symmetric group $S_3$ on its factors, and skew-symmetric if it is skew-invariant under this action [cite: 1, 2]. Odd Kronecker powers of skew-symmetric tensors remain skew-symmetric, while even Kronecker powers of skew-symmetric tensors become completely symmetric [cite: 1, 2].

The tensor $T_{skewcw, 2}$ resides in $\Lambda^3 \mathbb{C}^3 \subset \mathbb{C}^3 \otimes \mathbb{C}^3 \otimes \mathbb{C}^3$ [cite: 18]. Up to a change of basis, $T_{skewcw, 2}$ can be identified with the wedge product $a_0 \wedge a_1 \wedge a_2$, making it the unique (up to scaling) $SL_3$-invariant skew-symmetric tensor in $\mathbb{C}^3 \otimes \mathbb{C}^3 \otimes \mathbb{C}^3$ [cite: 13, 19]. 

### 4.2 The Determinant and the Permanent Connections

A pivotal discovery regarding these small tensors relies on their Kronecker squares. 
*   The Kronecker square of the standard $q=2$ Coppersmith-Winograd tensor, $T_{cw, 2}^{\boxtimes 2}$, coincides exactly with the $3 \times 3$ **permanent polynomial** ($\text{perm}_3 \in \mathbb{C}^9 \otimes \mathbb{C}^9 \otimes \mathbb{C}^9$) evaluated as a tensor [cite: 14, 17].
*   The Kronecker square of the skew $q=2$ Coppersmith-Winograd tensor, $T_{skewcw, 2}^{\boxtimes 2}$, coincides exactly with the $3 \times 3$ **determinant polynomial** ($\det_3 \in \mathbb{C}^9 \otimes \mathbb{C}^9 \otimes \mathbb{C}^9$) evaluated as a tensor [cite: 1, 2].

For the standard CW tensor, mathematical analysis applying border apolarity proved that the border rank $\underline{R}(T_{cw, 2}^{\boxtimes 2}) = \underline{R}(\text{perm}_3) = 16$ [cite: 14, 17]. Since $R(T_{cw, 2}) = 4$, the border rank of the square is exactly the square of its border rank ($4^2=16$), indicating no sub-multiplicative compression [cite: 17]. This resolves a long-standing question originally posed by Bläser and Coppersmith-Winograd, providing a negative result for complexity theory using standard CW squares [cite: 2, 17].

### 4.3 Sub-multiplicativity and Massive Border Rank Drops

Conversely, the skew tensors demonstrate remarkable and strict sub-multiplicativity, evading the immediate barriers applied to standard CW tensors [cite: 1, 17]. 

For $q=2$, the border rank of $T_{skewcw, 2}$ is 5. Naively, one might expect the border rank of its Kronecker square to be $5^2 = 25$. However, the border rank of the $3 \times 3$ determinant tensor is fundamentally constrained. Conner, Gesmundo, Landsberg, and Ventura established definitively that the border rank $\underline{R}(\det_3) = \underline{R}(T_{skewcw, 2}^{\boxtimes 2}) = 17$ [cite: 13, 20]. This upper bound of 17 was demonstrated via explicit numerical methods formulating 17 parameterized linear forms, and matched by a theoretical lower bound of 17 [cite: 13, 20]. If the border rank had dropped even slightly further to 16, it would have immediately become the primary candidate for proving $\omega=2$ [cite: 20]. Regardless, this drop from 25 to 17 proves $T_{skewcw, 2}$ exhibits profound sub-multiplicative behavior promising for the laser method [cite: 2].

Even more strikingly, for the $q=4$ skew cousin $T_{skewcw, 4} \in \mathbb{C}^5 \otimes \mathbb{C}^5 \otimes \mathbb{C}^5$, the baseline border rank is 8, leading to a naïve squared border rank of $8^2 = 64$ [cite: 14, 17]. However, rigorous analysis proves that $\underline{R}(T_{skewcw, 4}^{\boxtimes 2}) \leq 42$ [cite: 14, 17]. This massive drop from 64 to 42 represents one of the largest relative compressions of border rank under a Kronecker square known in algebraic complexity [cite: 14]. Because $T_{skewcw, 4}$ could potentially be utilized to prove $\omega \leq 2.11$ (well below the current record and the 2.168 barrier of standard CW tensors), skew CW tensors represent one of the most viable extant pathways in modern matrix multiplication research [cite: 14, 17].

**Table 1: Border Rank Compressibility of Coppersmith-Winograd Variants**

| Tensor Variant | Parameter $q$ | Border Rank $\underline{R}(T)$ | Naïve Square $\underline{R}(T)^2$ | True Square Border Rank $\underline{R}(T^{\boxtimes 2})$ | Compression Result |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Standard CW ($T_{cw, 2}$) | 2 | 4 | 16 | **16** | None (Permanent $\text{perm}_3$) |
| Skew CW ($T_{skewcw, 2}$) | 2 | 5 | 25 | **17** | Strict drop (Determinant $\det_3$) |
| Skew CW ($T_{skewcw, 4}$) | 4 | 8 | 64 | **$\leq 42$** | Massive drop |

## 5. Discreteness and Gaps in Asymptotic Subrank

A remarkable structural property of asymptotic tensor parameters is that they do not take on a continuous spectrum of values for lower bounds; rather, they are mathematically well-ordered and exhibit specific **gaps**. 

### 5.1 The Well-Ordered Nature of Asymptotic Rank

Recent findings by Christandl, Gesmundo, Zuiddam, and others demonstrate that over any finite set of coefficients (and often over fields like $\mathbb{C}$), parameters like asymptotic subrank $\tilde{Q}(T)$ and asymptotic slice rank are discrete [cite: 6, 21]. Any non-increasing sequence of asymptotic ranks strictly stabilizes. In other words, the set of values that asymptotic tensor rank assumes across all tensors is discrete from above (well-ordered) [cite: 6]. This implies that there exists a constant $\epsilon > 0$ such that no tensor has an exponent between $\omega$ and $\omega + \epsilon$ [cite: 6].

### 5.2 The 1.88 and 2.68 Gaps

Extensive classification of 3-tensors has definitively charted the lowest possible values for asymptotic subrank and slice rank. For any nonzero 3-tensor $T$ over any field, the asymptotic subrank $\tilde{Q}(T)$ cannot take arbitrary values. The possible values it can take are strictly quantized in the lowest regime:
*   $\tilde{Q}(T) = 0$ (for a zero tensor)
*   $\tilde{Q}(T) = 1$ (for rank-one and trivially independent tensors)
*   $\tilde{Q}(T) = 2h(1/3) \approx 1.88988$ [cite: 22]
*   $\tilde{Q}(T) = 2$ [cite: 22]
*   $\tilde{Q}(T) \geq \approx 2.68664$ [cite: 22, 23]

The value $2h(1/3) \approx 1.88$, where $h$ is the binary entropy function, is achieved precisely by the $W$-tensor (specifically $e_1 \otimes e_2 \otimes e_2 + e_2 \otimes e_1 \otimes e_2 + e_2 \otimes e_2 \otimes e_1$), which arises prominently in the study of sunflower-free sets in additive combinatorics [cite: 22, 23]. The next step, $\tilde{Q}(T) = 2$, belongs to tensors with straightforward rank-2 block restrictions [cite: 22]. The existence of the absolute gap between 2 and $\approx 2.68$ was recently established, solving a highly active open problem regarding the continuous versus discrete nature of tensor parameters [cite: 22, 24].

These gaps inherently connect to the Cap Set problem and other fields of additive combinatorics. For instance, the cap set tensor (characterizing arithmetic progression-free sets) evaluated over the finite field $\mathbb{F}_3$ holds an asymptotic slice rank of approximately 2.755, sitting safely above the 2.68 gap [cite: 23].

## 6. Hadamard Tensors, Rigidity, and Multiplicative Ranks

While explicit tensors like the CW family define boundaries on algorithmic implementations for matrix multiplication, the **Hadamard** matrices and tensors define limits in arithmetic circuit lower bounds and geometric modeling. 

### 6.1 Matrix Rigidity and the Walsh-Hadamard Transform

Leslie Valiant introduced the concept of **matrix rigidity** in 1977 as a pathway to proving super-linear arithmetic circuit lower bounds [cite: 25, 26]. A matrix $M$ is considered highly rigid if its rank remains "high" even after a "large" number of its entries are arbitrarily modified [cite: 26, 27]. Proving that an explicit matrix possesses high rigidity would yield profound bounds for logarithmic-depth circuits [cite: 25].

For decades, the leading candidate for a highly rigid matrix was the **Walsh-Hadamard transform**, $H_n$ (also known as Sylvester matrices, or the communication matrix for the Inner Product modulo 2) [cite: 25, 26]. The matrix has deep structural recursive properties: $H_{2^n} = H_2 \otimes H_{2^{n-1}}$ [cite: 28].

However, a breakthrough by Alman and Williams demonstrated that the Walsh-Hadamard Transform is **not** very rigid [cite: 25]. They provided an upper bound on its rigidity, showing that by modifying only $2^{\epsilon n}$ entries in each row, the rank of the $2^n \times 2^n$ matrix drops below $2^{n(1 - \Omega(\epsilon^2 / \log(1/\epsilon)))}$ for all $\epsilon > 0$ over any field [cite: 25]. 

This revelation fundamentally kills the possibility of proving standard arithmetic circuit lower bounds using Valiant's original matrix rigidity approach on Hadamard matrices [cite: 4, 25]. In particular, bounded-coefficient lower bounds previously thought to restrict Hadamard implementations were overcome, illustrating that utilizing unbounded-coefficient circuits based on the low-rank properties found in these rigidity upper bounds could drastically shrink circuit sizes [cite: 27, 29]. The previous best lower bound for $H_n$ at rank $r = \Theta(\log N)$ was bounded at $N^2/4r$, but new probabilistic rank paradigms have shifted the evaluation of Hadamard limitations entirely [cite: 29].

### 6.2 Hadamard Rank of Algebraic Varieties

Beyond circuit complexity, Hadamard structures heavily influence the decomposition of tensors via coordinate-wise operations. A geometric framework developed for such multiplicative decompositions characterizes the **Hadamard rank** of algebraic varieties [cite: 28, 30].

If one considers the Hadamard product (coefficient-wise product, denoted $\star$) of points in a projective variety $X \subset \mathbb{P}^n$, the Hadamard rank of a point $p$ with respect to $X$, $\text{Hrk}_X(p)$, is the minimum number of points $q_1, \dots, q_m \in X$ such that $p = q_1 \star q_2 \star \dots \star q_m$ [cite: 30, 31].

Antolini, Montúfar, and Oneto established that if the variety $X$ is not contained within a coordinate hyperplane or a binomial hypersurface, then the generic point has a strictly finite $X$-Hadamard-rank [cite: 30]. When dealing with the secant varieties of toric varieties (a critical setting for interpreting tensor decompositions geometrically), the general Hadamard rank is not only finite but firmly bounded: for points with no zero coordinates, the maximum Hadamard rank is at most twice the generic rank [cite: 28, 30]. 

This multiplicative analogue to the classical additive notion of tensor rank heavily impacts modeling with restricted parameters, such as representing quantum states or neural network expressivity through Hadamard product decompositions [cite: 28, 30].

## 7. Strassen’s Spectral Theorem and Optimization on Hadamard Manifolds

Returning to the asymptotic complexity of tensors, one of the central challenges defined by Strassen in 1991 was to explicitly construct new spectral points in the asymptotic spectrum $\mathcal{X}$ [cite: 5, 10]. Doing so effectively provides strict dual bounds on the asymptotic subrank $\tilde{Q}(T)$.

### 7.1 Quantum Functionals and Support Functionals

Two major families of explicit spectral points have been introduced to bound these parameters:
1.  **Quantum Functionals:** Discovered by Christandl, Vrana, and Zuiddam, these functionals rely on quantum information theory and moment polytopes (entanglement polytopes). Evaluating the asymptotic slice rank of a tensor equates exactly to calculating the minimum over these quantum functionals [cite: 7, 10].
2.  **Support Functionals ($\zeta^\theta$):** Originally proposed by Strassen, these act as candidate spectral points over a simplex $\Theta$. 

Recent work proves that upper support functionals can be computed in deterministic polynomial time using Fenchel-type duality and algorithmic invariant theory [cite: 5]. If the quantum functionals (which form a subset of the spectrum) exhaust the asymptotic spectrum of tensors over $\mathbb{C}$, it would unequivocally prove Strassen’s asymptotic rank conjecture—namely that every $n \times n \times n$ tensor has an asymptotic rank at most $n$ [cite: 5, 10]. A proof of this conjecture would automatically imply $\omega = 2$ and simultaneously refute the Set Cover Conjecture from fine-grained complexity theory [cite: 5].

### 7.2 Asymptotic Duality on Hadamard Manifolds

Evaluating these spectral functionals mathematically translates to solving complex optimization problems. Because the space of positive-definite matrices $\text{PD}(n)$ features an affine-invariant Riemannian metric $\langle X, Y \rangle_x = \text{tr}[x^{-1} X x^{-1} Y]$, it structurally forms a **Hadamard manifold** (a complete, simply-connected Riemannian manifold with non-positive curvature) [cite: 32].

Optimization on Hadamard manifolds is governed by "asymptotic duality" (a theorem by Hirai) [cite: 32]. Geodesically convex functions $f: \mathcal{M} \to \mathbb{R}$ defined on the Hadamard manifold $\text{PD}(n)$ possess Legendre-Fenchel conjugates that flawlessly characterize the limits of tensor scaling [cite: 32]. By leveraging the unique geodesic pathways inherent to Hadamard manifolds, researchers can effectively run generalized gradient flows to compute the quantum functionals [cite: 32]. Thus, continuous geometric optimization over Hadamard manifolds is fundamentally interlinked with the purely algebraic combinatorial task of establishing the asymptotic subrank of explicit tensors.

## 8. Synthesis and Future Directions

The investigation into the asymptotic subrank of explicit tensors intertwines diverse sectors of mathematics—from abstract tensor geometry and quantum information theory to applied theoretical computer science and boolean circuit complexity.

The standard Coppersmith-Winograd tensors, which reliably drove the reduction of $\omega$ down to $\approx 2.373$, are mathematically capped by the 2.168 barrier under the Universal Method due to their inherent structural irreversibility. 

The introduction of the skew-symmetric Coppersmith-Winograd tensors ($T_{skewcw, q}$) circumvents these barriers. The spectacular border rank compression of their Kronecker squares—dropping from 25 to 17 for $q=2$ and from 64 to 42 for $q=4$—demonstrates that sub-multiplicativity can be aggressively harvested to push the bounds of the laser method closer to the idealized $\omega = 2$ [cite: 14, 20].

Furthermore, the identification of discrete, immutable gaps in the possible values of asymptotic subrank ($1, \approx 1.88, 2, \approx 2.68$) imposes deep constraints on what physical or computational tensor transformations are permissible [cite: 22, 24]. Finally, the unseating of the Walsh-Hadamard transform as the preeminent rigid matrix forces a pivot in arithmetic circuit lower bounds, while Hadamard manifolds provide the required non-positive curvature spaces to compute the asymptotic tensor spectra functionally [cite: 25, 32]. 

Together, these frameworks—the skew deformations of algorithm blueprints, the rigorous topology of the asymptotic spectrum, and the optimization via Hadamard geometries—form the cutting edge of modern efforts to definitively characterize the complexity of matrix multiplication.

**Sources:**
1. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRGC5f34nKSyp6DCcbH6f9Ed4uQheYnNIJ3QGk1io5-_uIpXnee1zGm5eKJgg7P5miWaF1KN652FqwqB8K_crguigOBnMOYlV-NmNiXGvT0QCkbjQkIk9CeS4Npu3_8frWY4eybw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEP-xZa9eW61zH4ea8YYR1XhMGcM1CDSpJv489n478Ya70Cm_X1C-WdcdEdwtr11wAgtkk-eeSqGXar76XoM1Oi2At0bkVy9BJS9Jl4KK8lu7fLhShO)
3. [inria.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEagfDt35NPbN4PgVr11qe7oQNk0QbW2r9k7lmbnW9yhhr6tAPNWuTHYIsRTiSbiY4OjXzXa9L-jT5YL7pdXdlU_whlLzPOZQPVROAZ854QY8Sf7s4l3zN1hbzEQHK4N2UdIjttZDmM)
4. [joshalman.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElcDZa4xPhklX-JxCckzyF5-fWk4kaJDs50XKxxefDSEorM19_6ZBp4IaaN24FvI9ra5cM8DWu-S-YuEXirXtmdcO-h8WCmoW8rqdtWgZsg5IJ9A2IYoI=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeAoweU1cLA1pGkpbf4Sfa8N2RmGY7JAgnjySoD71LsBBA5puSjgeN-x19neCpv8SV7NMf5L0aYCDkyA6DvVa6hmAiMRSl1gAZuZkedPBB6EdEyNvm)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRw2IYEVs9CRF9Z8FJzQ3T5-PiDK38CR1cCwsZLlpw76vdwzugrpALpmJZY43mNrCKZLjM1D78vzKiP-yqeYDMFQPw81XQ_KkxYTfKR3dbSPClEsKI)
7. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIF-rNQ5HheS6yjHqx5i4lCCwRCPyodnwgtlaS5WIpMmSSQj8vD4AtQRyMg96yrHldJjbDui4YDGZbY5aUJJpuBacJ5mCesKJNIJA87_4_LwNxSjOt7pffXvFPzQTM3TI=)
8. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5T-SkDi9tDoWcCKgIkONUfyGY5EMPkUqEJZo89NjZQuoZFlSaXSzKOrQQ6MOGFOdyVgLQtvOetRZvjFm5agaf1l3Gbqk_sSAWuC0mFlp0LsphpW3e_GwCzwlHImi7uMCV398WlCzgTMFMVKZPojQZCfAneQH3fLCcPcHD2zqLdQ==)
9. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFsyQavDWfWmAyWjFhtkmykv_uYuMKUC_9_Iqra65q81caiZd8vbyHQG0NZ4_q1eJI7P1lah3C1kwWn9XVuCfM3yiZ2QRJ-c-IP8HswuHdKaTAfLKnExzXM5oRShNyDA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWNm-nw1lhY4RfnniqvP-dbpXmPxAfvr14hOS2IynCBcXpTvrY2seAoBoZkFa3D-Dll1uPW-p6ILwLnB6TM8QfGWcSri1tPHRAcl-6AEkSQ-AEU5Lmzj3H)
11. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYf3m8az0XBM_eElhBpx-sJojH1B_WayGcgRPEBoZY2VOO1V6agh_Eumny4qm1uZwh_SZQdeM2HNO9coXHpyMJhHXyPcyYDn83vFmMXXqbDIvbnOmNRxUH_d-iTN8Ougcaldo97qIFBA4V-GJ5fW-fBjyY5TIpMo3QCWXVYYBQ5J69LA==)
12. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1GXmp-k2FV-G_5M7BnayPI8cMzKpzViGhhye5B-X_pJti490f-NZ1EcFC9sTsoqVpwzyDm0Ir9Rcvfl5wvSs0Lt5z2zNunRuL7wlHnkgXtjZF5x0C_19pWZsDuNk-OU9oSzqsS11RTjFYS3Rt_CRpi-CapB0UhSyxzAihFPlPrxRmiVyvMqvgcN7oJGujtjlXbaZLewnxE4eBtvvMCXs=)
13. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2I-5xkREgPTWcnl9e8x0A-xO8tjdgbJmoGpGPJIIjbBjfKRnPghedPGM3MZz_tszq0KcGU9UtAdhDXUNQ9j4UtYIThRnlWpW-fsa7IdKvcRNYiWCtqQOn-OgqPR8BeJMNpwrbaCBo04RfBOWCdC3u8bMuEQmLFCk5p_2xLzTlydDOtjsqlORwNbKdse2omMpyyH8HjEll8Ld01m-6BJfVhJc=)
14. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNdITGsuPPGbQNtmzMzLmsAMuNtTissJaKXGMlUm1ITJcyX9MnhxgkQBEVGUZ708UCrmg2MdwT4oN82pEgZr04Eegw-ttOuxuj5GufljSfeIBl8u-8-Y7uiS7zaRwiErX0oaIU)
15. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvDHc6oJhTvH63jVt49uTeyMasy0dUwrucWPoK3FmM7SNl3IZeXZ2p2BebuNgFi-a8-2SkfPdeNfrZYkWeQE4GGNMsuI2hb7ZKgz_I_ONLSOPIVGw6qMys5oqmFb7neTJhBAWcYpLwdw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEedPCOnqS_JjRFVdLtNuGKi5VdIEZNks-ngKuhL9vC3jVGpvt4ceEFjj2WpkLnEoqksT8QxFm9ld40ZaHILg1SIMF4J2Mpj4DZXKvZwpodRa6IZIXX)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOxE8EG6LICs1t2Z6kKBbo3JPmaGtqQ-x21hiDoBhpI3NlDww-bJAKH-IoFITfz8BPGgDY1NBrr9YggiGy90eG_t3DqR_2_DQ6Pwz6gBzHqIXOqR6P5pRDRu0eLxA8O-RVZR34O9WxaAWhsykvUcEdMR4vJPAtmwivsjEYxkUd9HB-Ew==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBqZPfwPTV4ZQo1NKstrlFY0LPZP7uLxGDM1qmVkSL08ROi04fGGekMF02G_nTKP2B-75YUAK1Tdhr1ej6WsTgmoThxfqivQus6ck4KMbzSxECX-r2DmrzE0hmbbnpMmS_eo_GFwgHWQ45-gklxYtoCmAAXWKi26k8l7RNdgFHM-c6EGBKrRiIyVr8tQ0A5WCgI1sy)
19. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYkVdpnCgv53THIMJhoET_3QQWCRjB0exlpwpdFd1O2B-Wk23TxpJ4aQbNV3Z3iiTQ6WYGzZYnvqr5URK5TSDf0mkMiaAnRFzMBvH1g7ULu497awgdkVzScz0UafvNAY4J5Q==)
20. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJWyygu_8abN8kCAm_PvOkuSPwlQZiDuvGA8VMMgMeViXjvTulWw_6lzPhsGwTtKZIKo0zalqMHb90kLlQhMBY550bikYFs1nAeKEhJLG0-HEpRYsZxaq7g47jmHxVMDAni3ImLPktryGVmb1OkVi2CwG6lCobAuiovO_O_U1tQ8XGde9ut1AwTnEO8qDdXOIZQD5pUlBpMQdpidqhJqqgc8RFIh8ypkWKlZoJA3eNj0hrG4h9HwJmPIJ4onxkHYHrqA47EpAExl-0zHJ5WwUI5CMlg44qkQANnSvQIz2XdSyHs7xewOn8zAU3o1ZtSJoS2Wfc1OttUCOe)
21. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHw_XVhxwXNqCMWwvD1IgP0vUbub-wzbgisfqnyEckbEOZ10fFeCL2RKGbCyG0JSZpJlqABJCVIuG67joR2qeYMVfKCq3shMPcXIhoKODGqL4Sy0wV1Xg1ODuw=)
22. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFa-yIs05dGiczdKY9qJwDve9TGBy8mTL_UtUBJWG-6KYlDmap9ZRJneKVQ5_hdtj1_yvch5UTI44LHUdbnnhfX3g80LbivcAnK4WHe6gx0pT7msTt3dIH5LWg=)
23. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHguOozAdkFRz5DfnyvA-p4r2XOPhGUVtH2S7uxqAILBmJ7acf5mODdNlKSQy7oI8NsDeYT5oJe4i9iFAUCVlLVrQUqBSd0QhmswgctyU_E5VFkIevJp5-fLEQ=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzxAtf3buw1300-5BQXTA5EG7ggrzODJIweHmAwCCf1K7x7bFCNsaCdleCzqqef9wJNh2baQF44Tmws9uKq-AzuxmhcrSl0AqVo74r85tRfBPtRM2o)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKbWyCrQt_oiXZs5sRRUvwYXwNFGS5O9mkHt7Uuf9cbMVQjOrp4TOn1g6erL-KXFdpAjTttupnS3LyBzbO-bNCYrnF8ZrcDNkjJalm85lx4wFyQpkB)
26. [tcsplus.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDaozvppx9oltfct5vPLnMcoSA7ra6OKPGAeQqXPrN6uWFP-trlBEUSZ6uCOkY8EqXOQAK-2Qe_uFvl_G8rwSiwyOitkfaYGiWIKhQtG6y0q3TzFpJekTQaRrrXLk7FKoRvJWOoB-ES5g=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1U2NKLIkUiCZFj2YaWc5YGSuoRhp-uGoTYBwJxI3PkJ6Ga2HMvqRD4ai4KMNYG0mMVL6ER7-ohN1LfoQb1IBD3TtkaB2a9vgLjyWWXp5ys4YKgj0pDRhI)
28. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgzSCuXeD_ecu5fxS5LxBkBKhHKFJI0B-nR5Rm32RVHKfvgvAjkj5-kJA5d-xsQuA4XyDR4Lk9v_2wFLI6COAwXvFHsbn3evXD_6tuFd7wvbyR9yUQqglwpsL1ThBljlPurOorP8SRD87r)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTC6DQ2QdQK2uIcnmcZEHUsTCdgnxEg9jcLqo7iHAam3FcrcTDnd68neUswBzD1uJUCpbiSbRt7N9JXV249KGME4ekrVVvD2UaVKavPi8QcC96UK5m)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZfL0tN4-hbt_Qjz3m4eYKZfLp0PqFuDgJ5YfrNHNQu3jCQrd0emYgcuWvcCw3XmFh4oajJeuk5_JI0l05_OG0kxcGtLjAFA4zLp6-VekekjEpAjytZPnkOaVvLb6640PkijnFHqc8fVK6vc9jdh19lRwYE3UnWziE-8vLtpmD7AXBp9JL60xvkXGL5Xs=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5Zn5uNSKv9EiMMVXBY6nMknxZvaM8syYkfKLk4W7bLsqaj3HKBj9p_M9tTxOBH5dBY-ZB_AwBcKm3M0RfLtcJ13lZh4WX059t11T9CFcHKP7QWkQb)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFntfzeOMhiVSyKcknpscyjSee-GbpmNaVLFPGkX3kR14UkIpUAoaLDIncqtNnFCj_BvZdYruh7t4KUfBws58p31Hbkvy7xi9oSZ9sV_CjeenNjn86Pd4wO)


# Followup [FU-2026-05-22-021 <- row121]: # T#87: Tensor Rank of the Multidimensional Discrete Fourier Transform (\(d \geq 3\))  This report p

**Pythia queue id:** 306
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdhclFQYXJXckx1U05fUFVQbG91eWtBURIXYXJRUGFyV3JMdVNOX1BVUGxvdXlrQVE
**Elapsed:** 311s
**Completed at:** 2026-05-22T01:47:14.969064+00:00

---

# Substrate-Grade Research Brief: Tensor Rank of the Multidimensional Discrete Fourier Transform (\(d \geq 3\))

**Key Points:**
*   **Fundamental Complexity:** The tensor rank of the multidimensional Discrete Fourier Transform (DFT), specifically its formulation as a Collapsed DFT (CDFT) tensor for dimensions \(d \geq 3\), remains a computationally intractable metric to derive universally, blending challenges from multilinear algebra and algebraic complexity theory.
*   **Prime vs. Composite Spaces:** While exact formulas for the rank of the third-order CDFT tensor have been successfully derived when the underlying spatial dimension \(N\) is a prime number, non-prime and higher-dimensional spaces are governed by non-linear bounds that defy current generic rank approximations.
*   **Algorithmic Implications:** Embedding multidimensional DFT structures within group-theoretic frameworks (such as the Cohn-Umans method) provides one of the most promising vectors for optimizing the matrix multiplication exponent (\(\omega\)), translating the tensor rank of the DFT into direct bounds on bilinear computational complexity.
*   **Structural Anomalies:** Recent findings establish that the CDFT tensor escapes standard orthogonal decompositions—it is neither orthogonally decomposable (odeco) over the reals nor Hermitian orthogonally decomposable (Hodeco) over the complex field, frustrating traditional spectral decomposition attacks. 

The evaluation of tensor rank for higher-order dimensional structures serves as the linchpin for both establishing the theoretical limits of algorithmic complexity (e.g., matrix multiplication) and enabling high-dimensional signal processing. The multidimensional DFT, a foundational transformation, takes on deeply complex geometries when expressed as a higher-order tensor (\(d \geq 3\)). This report aggregates the latest algebraic, geometric, and computational findings surrounding the tensor rank of these objects. While progress has been heavily gated by the NP-hard nature of tensor rank computation, specialized tensor constructions like the Collapsed DFT (CDFT) and novel analytical frameworks like polynomial folding and the generalized Cohn-Umans method have opened new frontiers. The evidence suggests that while partial bounds for small or prime-dimensional spaces are solvable, the universal characterization of DFT tensor rank requires bridging discrete Fourier analysis with the algebraic geometry of secant varieties.

***

## 1. Brief Summary

**PROMETHEUS CONTEXT:** T#87 intersects the algebraic geometry of secant varieties with computational complexity, interrogating the exact tensor rank (and border rank) of the \(d\)-dimensional Collapsed Discrete Fourier Transform (CDFT) to establish absolute lower bounds for bilinear transform algorithms and to map structural pathways toward the matrix multiplication exponent \(\omega = 2\).

## 2. Flagged Findings

The investigation into the tensor rank of multidimensional DFT structures has yielded a landscape defined by highly specific, localized consensus paired with glaring theoretical blind spots. The current literature demonstrates structural breakthroughs for low-order bounds, but attempts to generalize these findings are frequently hindered by topological and algebraic artifacts.

### 2.1 The Prime Dimension Consensus and its Risks
Current consensus strictly establishes the exact rank of third-order CDFT tensors (\(n=3\)) under the explicit condition that the dimension of the underlying space (\(N\)) is a prime number [cite: 1]. The derivations rely heavily on the non-existence of non-trivial subgroups in prime-order cyclic groups, which elegantly restricts the degrees of freedom in the tensor's canonical polyadic (CP) decomposition.

**Where it might be wrong:** The field's current trajectory relies heavily on extrapolating from these prime-dimension proofs. However, this is highly indicative of **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**. Researchers may be mathematically overfitting their rank conjectures to the structural simplicity of prime-dimensional vector spaces or prime fields (\(\mathbb{F}_p\)). In composite dimensions, the group algebra inherently possesses zero-divisors and non-trivial sub-representations, causing the algebraic varieties defining tensor rank to bifurcate. Assuming that composite-dimensional CDFT tensors will obey bounds smoothly interpolated from prime dimensions neglects the highly chaotic nature of tensor rank, which is known to be non-upper-semicontinuous [cite: 2]. 

### 2.2 Symmetric Rank Parity Leaks
A major flagged finding from recent literature [cite: 3] dictates the symmetric rank behavior of the CDFT tensor. For a spatial dimension \(N=2\) and order \(n \geq 3\):
*   If \(n\) is odd, the CDFT tensor has symmetric rank 2 under all standard definitions.
*   If \(n\) is even, the CDFT tensor has symmetric rank 2 under the relaxed Definition 2.2 (which allows negative coefficients in the symmetric decomposition), but it completely lacks a symmetric rank under the strict Definition 2.1 (which restricts coefficients) [cite: 3].

**Where it might be wrong:** The complete divergence of tensor rank properties based simply on whether the dimension \(n\) is odd or even is a classic manifestation of **PATTERN_RANK_PARITY_LEAK**. The mathematical framework being used to interrogate the CDFT tensor is failing to account for the orientation and sign-invariance of even-order polynomial representations. The parity leak suggests that the strictly positive definitions of symmetric rank are topologically misaligned with the alternating symmetries of the even-order discrete Fourier transforms, creating artificial boundaries (or "leaks") where the rank appears to be undefined when, geometrically, it simply resides in a different projective orbit.

### 2.3 The Failure of Orthogonal Decomposability
It was previously hypothesized that highly structured, symmetric transformations like the CDFT might admit orthogonal decompositions, allowing their eigenvalues and eigenvectors to be easily extracted. However, it has been definitively proven that the CDFT tensor for \(N=2\) and \(n=3\) is *not* orthogonally decomposable (odeco) over the real numbers [cite: 3]. Furthermore, over the complex numbers, it fails to be Hermitian orthogonally decomposable (Hodeco) [cite: 3]. This breaks the consensus that highly symmetric transform tensors share the friendly spectral properties of symmetric transform matrices. Consequently, naive tensor PCA or CP-ALS (Alternating Least Squares) algorithms will predictably fail or stall in local minima when applied to the CDFT [cite: 2, 4].

## 3. Problem Statement

The precise mathematical object being interrogated in this research brief is the **multidimensional Discrete Fourier Transform (DFT) tensor**, with a specific focus on its recently codified variant: the **Collapsed Discrete Fourier Transform (CDFT) tensor** [cite: 1, 5]. We are interrogating the fundamental algebraic complexity of these objects as measured by their **tensor rank** (and associated variants such as symmetric rank, border rank, and folding rank) [cite: 6].

### 3.1 The Standard DFT Tensor vs. The CDFT Tensor
In one dimension, the Discrete Fourier Transform is a linear operator represented by an \(N \times N\) matrix \(\mathcal{F}\), where the entries are given by \(\omega^{jk}\) with \(\omega = \exp(-2\pi i / N)\). 

When extended to \(d\) dimensions (or order \(n\)), one standard approach is to define an even-order DFT tensor. However, Diaz and Lutoborski [cite: 1] introduced a close relative called the **Collapsed Discrete Fourier Transform (CDFT)**. The CDFT is an order-\(n\) tensor defined over an \(N\)-dimensional space, \(C \in \mathbb{C}^{N \times N \times \dots \times N}\). The CDFT tensor differs structurally from the standard even-order DFT tensor for any order \(n > 2\). The CDFT describes an operation that maps lower-order tensors into a lower-dimensional space—effectively "collapsing" them [cite: 3]. 

The interrogation of this object seeks to find the minimum integer \(r\) such that the CDFT tensor \(C\) can be expressed as the sum of \(r\) simple (rank-1) tensors:
\[ C = \sum_{i=1}^r \lambda_i v_i^{(1)} \otimes v_i^{(2)} \otimes \dots \otimes v_i^{(n)} \]
where \(v_i^{(j)} \in \mathbb{C}^N\). This integer \(r\) is the **tensor rank** of \(C\) [cite: 6].

### 3.2 Sub-classes of Rank Interrogated
Because the canonical tensor rank is NP-hard to compute [cite: 2], the problem statement fractures into several precise sub-invariants interrogated in the literature [cite: 5, 6]:
1.  **Symmetric Rank:** Since the CDFT tensor is completely symmetric (its entries are invariant under any permutation of indices), we interrogate the minimum number of identical rank-1 symmetric tensors needed to construct it: \(C = \sum_{i=1}^{r_s} \lambda_i v_i \otimes v_i \dots \otimes v_i\) [cite: 3, 7].
2.  **Border Rank:** The minimum rank of a tensor that can approximate the CDFT tensor to an arbitrary degree of accuracy (\(\epsilon \to 0\)). This relies on the closure of the secant varieties of the Segre variety [cite: 4, 8].
3.  **Folding Rank:** A newer invariant defined by mapping the tensor into a matrix of multihomogeneous polynomials [cite: 5, 6]. The problem asks whether the folding generic rank matches the true generic rank for the CDFT.

### 3.3 Connection to Bilinear Complexity
The broader object of interrogation is the **bilinear complexity** of the algorithms generating these transforms. Using Strassen's framework, the number of non-scalar multiplications required to compute a bilinear map is precisely the tensor rank of its associated structure tensor [cite: 9, 10]. Thus, interrogating the rank of the multidimensional DFT tensor is mathematically equivalent to proving the absolute minimum number of arithmetic operations required to compute the multidimensional Fourier transform [cite: 8, 11].

## 4. Status & Bounds

The evaluation of tensor rank for multidimensional DFTs and related structures is currently characterized by isolated exact results bounded by broad, asymptotic algebraic limits.

### 4.1 Exact Status for Order 3 and Prime Spaces
The last known exact status for the rank of the CDFT tensor occurs at order \(n=3\). Diaz and Lutoborski achieved exact computation of the rank of third-order CDFT tensors under the strict conditional qualifier that the dimension of the underlying space \(N\) is a prime number [cite: 1]. 
*   **Best Bound / Exact Status:** For \(n=3\) and \(N = p\) (prime), the rank is explicitly known and tightly bounds the algorithmic complexity of collapsing 3-tensors in prime spaces [cite: 1].
*   **Conditional Qualifiers:** This exact status vanishes when \(N\) is composite. For arbitrary dimensions \(d > 3\) (or \(n > 3\)), exact formulas remain an open problem.

### 4.2 Symmetric Rank Bounds for N=2
For the simplest non-trivial spatial dimension \(N=2\) and arbitrary order \(n \geq 3\), the symmetric rank of the CDFT tensor has been entirely mapped, revealing deep topological quirks [cite: 3]:
*   Over the field of complex numbers \(\mathbb{F} = \mathbb{C}\), the CDFT has symmetric rank 2 under all definitions.
*   Over the real numbers \(\mathbb{F} = \mathbb{R}\), if \(n\) is odd, the symmetric rank is exactly 2.
*   Over the real numbers \(\mathbb{F} = \mathbb{R}\), if \(n\) is even, the tensor has symmetric rank 2 under Definition 2.2, but has **no symmetric rank** under Definition 2.1 (due to the presence of negative coefficients in the decomposition which cannot be absorbed into real even powers) [cite: 3]. 

### 4.3 General Generic Bounds and Monotonicity
The literature establishes that the rank of the CDFT tensor is monotonic with respect to its order \(n\). As the order increases, the rank must monotonically non-decrease [cite: 1]. 
Furthermore, Alexander-Hirschowitz theorem bounds apply to the generic rank of symmetric tensors. For a symmetric tensor of order \(n\) in dimension \(N\), the generic rank is almost always \(\lceil \frac{1}{N} \binom{N+n-1}{n} \rceil\), with a known set of finite exceptions (e.g., \(n=3, N=5\) or \(n=4, N=4\)) [cite: 7]. However, the CDFT tensor is a highly structured, specific tensor, not a "generic" one. Its actual rank is strictly bounded above by these generic limits, but typically falls far below the generic rank due to the dense algebraic structure inherited from the roots of unity [cite: 11].

### 4.4 Ill-Posedness of Border Rank Approximations
A critical status update in the broader field of tensor approximations (directly impacting the approximation of multidimensional DFT tensors) is the proof that the best low-rank approximation problem is mathematically ill-posed for tensors of order \(d \geq 3\) [cite: 4]. De Silva and Lim established that sequences of rank-\(r\) tensors can converge to a tensor of rank greater than \(r\) [cite: 2, 4]. This means that the border rank of the CDFT tensor may be strictly less than its actual rank, and numerical attempts to approximate the CDFT via truncated Eckart-Young type algorithms will fail on sets of positive volume [cite: 4].

### 4.5 Eigenvalues of the CDFT
For \(N=2\) and \(n=3\), the eigenvalue problem for the CDFT tensor has been explicitly solved using Lim's variational approach. The polynomial defining the eigenvalues is \(p(x) = x^3 + 3x^2 - x - 1\). Its three distinct irrational real roots \(b_1, b_2, b_3\) yield the three non-equivalent eigenpairs \(([1, b_i]^T, (b_i + 1)^2)\) [cite: 3]. Notably, the CDFT tensor for \(n \geq 3\) possesses no zero eigenvalues, differentiating its collapsing action from standard matrix algebra projections [cite: 3].

## 5. Literature (Primary Sources)

The body of literature governing this precise intersection of multilinear algebra, Fourier analysis, and complexity theory relies on a core set of primary sources.

1.  **Diaz, S. P., & Lutoborski, A. (2017).** *Discrete Fourier Transform Tensors and Their Ranks.* SIAM Journal on Matrix Analysis and Applications, 38(3), 1010-1027. DOI: 10.1137/16M1084717.
    *   **Significance:** This is the foundational text introducing the Collapsed DFT (CDFT) tensor. It establishes the monotonicity of rank with respect to order and derives the exact computation of the rank of third-order CDFT tensors for prime dimensions [cite: 1, 5]. 
2.  **Diaz, S. P., & Lutoborski, A. (2020).** *Discrete Fourier transform tensors and their eigenvalues.* Linear and Multilinear Algebra, 70(15), 3020-3035.
    *   **Significance:** Solves the eigenvalue problem for the DFT and CDFT. Proves that the CDFT is neither orthogonally decomposable (odeco) nor Hermitian orthogonally decomposable (Hodeco) [cite: 3]. 
3.  **Ye, K., & Lim, L.-H. (2018).** *Fast Structured Matrix Computations: Tensor Rank and Cohn-Umans Method.* Foundations of Computational Mathematics, 18(1), 45-95.
    *   **Significance:** Expands the Cohn-Umans group-theoretic embedding method using Strassen’s tensor rank approach. Directly links the bilinear complexity of structured matrix products (including transforms related to DFTs) to tensor decompositions in group algebras [cite: 9, 10, 12].
4.  **Diaz, S. P., & Lutoborski, A. (2016).** *Polynomial foldings and rank of tensors.* Journal of Commutative Algebra, 8(2), 173-206.
    *   **Significance:** Introduces the "folding rank" of a tensor by mapping it into a matrix of multihomogeneous polynomials, providing a new invariant to bound tensor rank and generic behavior [cite: 5, 6].
5.  **De Silva, V., & Lim, L.-H. (2008).** *Tensor rank and the ill-posedness of the best low-rank approximation problem.* SIAM Journal on Matrix Analysis and Applications, 30(3), 1084-1127.
    *   **Significance:** Provides the crucial boundary condition that for tensors of order \(d \geq 3\), optimal rank-\(r\) approximations may not exist, invalidating standard matrix techniques like Eckart-Young for higher-order DFT approximations [cite: 4, 13].
6.  **Ottaviani, G. (2014).** *Complexity of Matrix Multiplication and Tensor Rank.* Colloquium KIAS, Seoul.
    *   **Significance:** Bridges the Karatsuba algorithm, Discrete Fourier Transforms, and tensor rank. Defines rank via secant varieties of the Segre variety [cite: 11].

## 6. Attack Vectors

The NP-hard nature of tensor rank has forced computational mathematicians to develop highly sophisticated geometric and algebraic workarounds. This section outlines the live techniques actively pushing the boundaries of the multidimensional DFT tensor rank problem, as well as the exhausted approaches that have reached theoretical dead ends.

### 6.1 Live Techniques

#### 6.1.1 Generalized Cohn-Umans Group-Theoretic Embedding
One of the most potent live attack vectors involves the Cohn-Umans method, originally designed to push the matrix multiplication exponent \(\omega\) toward 2. Ye and Lim generalized this method to arbitrary bilinear operations, relying heavily on tensor rank [cite: 9, 12].
The approach embeds the matrices (or higher-order structures) into the group algebra \(\mathbb{C}[G]\) of a finite group \(G\). If the group possesses subsets that satisfy the "triple product property", the tensor rank of the bilinear operation is bounded by the complexity of multiplying elements within the group algebra [cite: 9].
For the DFT, the group algebra is diagonalized explicitly by the discrete Fourier transform itself. By pushing multidimensional DFT operations through Cohn-Umans group embeddings (or utilizing algebras like cohomology rings or polynomial identity rings [cite: 9]), researchers can bypass direct rank computation, relying instead on representation theory to yield upper bounds on bilinear complexity.

#### 6.1.2 Polynomial Foldings and Determinantal Schemes
Introduced by Diaz and Lutoborski, "polynomial folding" represents an active, live vector for interrogating tensor rank without resorting to raw CP-decomposition algorithms. A tensor \(T\) can be "folded" into a matrix of multihomogeneous polynomials [cite: 6]. 
By analyzing the determinantal schemes (the algebraic varieties defined by the vanishing of the minors of these polynomial matrices), researchers can define a "folding generic tensor" [cite: 5, 6]. The major theorem states that for "small" 3-tensors (which includes the \(n=3, N=p\) CDFT), any folding generic tensor has a generic rank [cite: 6]. This algebraic geometric attack vector translates the problem of tensor rank into a problem of studying the dimension and degree of ideals generated by polynomials.

#### 6.1.3 Truncated Moment Relaxations for Hodeco Tensors
While the CDFT is not Hodeco (Hermitian orthogonally decomposable), the study of Hermitian tensors provides tools via sum-of-squares and moment matrices [cite: 14, 15]. To determine if a complex tensor admits a structured Hermitian decomposition, researchers utilize Lasserre-type semidefinite relaxations, posing the decomposition as a truncated moment problem [cite: 14]. While standard Hodeco fails for the CDFT, generalizing these SDP (Semidefinite Programming) relaxations to non-orthogonal symmetric bases is a live vector for establishing lower bounds on the rank [cite: 15].

### 6.2 Exhausted Approaches

#### 6.2.1 Eckart-Young / SVD Truncation (CP-ALS)
In standard matrix algebra (order-2 tensors), the Eckart-Young theorem guarantees that truncating the Singular Value Decomposition (SVD) yields the optimal lower-rank approximation. This approach is completely exhausted and provably invalid for tensors of order \(d \geq 3\) [cite: 2, 4]. Because the set of tensors of rank \(\leq r\) is not closed, continuous optimization algorithms like Alternating Least Squares (CP-ALS) or higher-order SVD (HOSVD) will encounter tensors that have no best rank-\(r\) approximation (the infimum is never attained) [cite: 4]. Numerical approximation vectors based on these matrix-era paradigms are mathematically dead.

#### 6.2.2 Orthogonal Eigenvector Extraction (Odeco/Hodeco)
For symmetric tensors, robust algorithms exist to extract eigenvalues if the tensor is orthogonally decomposable (odeco). Because Diaz and Lutoborski definitively proved that the CDFT tensor over \(N=2\) is neither odeco nor Hodeco [cite: 3], any algorithmic attack relying on the spectral theorem's generalization to orthogonal tensor bases is exhausted for the DFT structure. The CDFT's symmetries do not align with Euclidean orthogonality in \(\mathbb{R}^n\) or \(\mathbb{C}^n\).

## 7. Cross-References

The exact determination of the CDFT tensor rank is not an isolated mathematical puzzle; its resolution reverberates across several adjacent domains in complexity theory, cryptography, and multilinear algebra. 

### 7.1 The Matrix Multiplication Exponent (\(\omega\)) and Strassen's Problem
The most dominant cross-reference is the quest for the exponent of matrix multiplication, \(\omega\) [cite: 11, 12]. The minimum number of operations required to multiply two \(n \times n\) matrices is asymptotic to \(\mathcal{O}(n^\omega)\). Matrix multiplication can be represented by a 3-tensor (the structure tensor of matrix multiplication), and its tensor rank directly determines \(\omega\) [cite: 8, 11].
The tensor rank of the multidimensional DFT acts as a candidate primitive for accelerating these structural tensor decompositions. Fast matrix multiplication (like the Schönhage-Strassen or Cooley-Tukey algorithms) intrinsically relies on divide-and-conquer methodologies rooted in the DFT [cite: 11]. A breakthrough in the tensor rank of the multidimensional DFT directly informs the bilinear complexity of the sub-routines utilized in pushing \(\omega \to 2\). Furthermore, Shitov's 2019 disproof of Strassen's additivity conjecture (showing that the tensor rank of a direct sum can be strictly less than the sum of the ranks) highlights that the structural tensor of the DFT may possess deeply hidden sub-additive efficiencies [cite: 5].

### 7.2 Multimodal Local Differential Privacy (LDP)
An unexpected anti-anchor to the highly theoretical realm of algebraic complexity is the practical application of multidimensional DFT tensors in privacy-preserving machine learning. Recent frameworks for multimodal differential privacy explicitly utilize the multidimensional DFT to perturb data [cite: 16, 17]. To protect high-dimensional fusion tensors (e.g., in Tensor Fusion Networks), researchers apply the multidimensional DFT and add noise directly to the complex tensor frequency domain [cite: 16]. The computational efficiency and the utility bounds of this privacy mechanism are strictly governed by the rank and condition number of the DFT tensor being applied. If the folding rank or CP-rank of the multidimensional DFT is smaller than anticipated, the computational overhead of these LDP frameworks drops logarithmically. 

### 7.3 Secant Varieties and Waring's Problem
The algebraic geometry underlying the symmetric rank of the CDFT tensor is inextricably linked to Waring's Problem for polynomials [cite: 7, 18]. Representing a symmetric tensor of order \(n\) in dimension \(N\) is equivalent to expressing a homogeneous polynomial of degree \(n\) in \(N\) variables as a sum of \(n\)-th powers of linear forms [cite: 7, 18]. The tensor rank defines the secant variety to the Veronese variety. Open problems regarding the dimensions of higher secant varieties (specifically determining the exceptional cases in the Alexander-Hirschowitz theorem [cite: 7]) serve as related open problems. Any exact bound found for the generic CDFT directly contributes a structural data point to the broader classification of secant varieties in projective space.

**Sources:**
1. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENrYemmPBzH9PIf9o-K7uyJ2rG5Ghl5NeSVTAuxIZ8QzrrEpVKpZuqNazhaN0Yc7hqgUXk5XycbQp-In_UWRMakHxz6IfgK8vtgVgKSvdUPzC6ynN3lSebdy1RtBV2WRy7azI=)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYFHemY8jOHuuq-XDlzVWtpnYmXTFqAji-Zo8LuuZtfJSguRzYCb1YlBzReQDwFHDssspA0KwFRgcrYbAcoh9I9eDXSV2fMEWppAmR0AdrPaxqRCM7Rokr7ufRFUqm4oonGIw1duFAORBL9qk855s81Fp3UyvUy5_hKLNd31DiBSeU3Bx2FF9nDqEhmJCD8ynbAUytmAU4UKBL6ABmJp2-hGaJKVa7gmaHyGe-gjeKdj7DCfrrObc8TbdZ8g==)
3. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHATYB8wpfIm-jAwrjQ2_yz4qDzSQIguDV3jGqVVvgRiU3JLDZlyhCVBjjA8Aj_6LLiJZfOj0p9r2ysZ-8MXfxfi0yTx9DLcaKRy431VTvs0tNPISYpptw5mqp9mnw4rfIoY70hyfdp0BrYiNyX7l6RMuR8T97jOQ==)
4. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmXR1CjZSUCjF4sdgazM3rgJUwj1o_c20aPnvnSYNbF997rl86DrHt4CSPZ82mAddX4-736N9jLOLEbv9wFxtBbFFRUlfXlnYpYfmBeYpnSpUA7Zt9BzUQuH1Whod4k-0uDQ==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHw48x4EKkQ0H_7EXIahffsDyFckjKyv5kDxuIOKQdlbVzflDOhy4Y9iYMscHbeJY418kwBtivtQnL8D1gt5i0WPiWNOigITHkWojVZkbge5ZQdlBLYFxv3EWyfNzQAxLh8iyxP5uYtxmJogyBO5TIw3GkoGMx9jr29zLgxG5lZMudhVzFrRHpzCUGVH_9CwWgblb_GjQ8S3npwg==)
6. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHasEf-L_wKDVC6fFT_SPG7vss_RyK9CK1OYxXeVD5NatN5jRfox5Fl0FZHIJDSLD-QRBl3--bRQnj-ru2Fys9nor_TX-zaM29gOlvbihBF0JWFFSMc2r5zQoTEcgA8E_WqiceYl6sYW5_7qvhPOPlr0rbqbxGOHb3ypiINEmLNxDs1iYjnhQ6Ub84CgVRh8TuQi9zuf1sSBzqT0_cmC4yu7vvGIykrMw185cfu8KDmUlQCeExZH5_WtacoDIGLFa_cU56Iy5KVtLPZszuguw==)
7. [ubc.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQk4R7BppqgBez1PI0RcVrsMwjAUP7JiCs1afV0jEcuu6syIAUYrUl-XM2Od3whQQiJeUQ1mwYL7zKykNWvuNYhOk4ar6eYgGdyWIKBEE37kkmPL-FJZe8aYIQp2K0W0q8TLAj3TWM1X9_qOe5Mz99)
8. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6n6dcGu44dobanYR9iMnVZWs-a9pexEIdsvjV8XSEfDx4g_w1O8yBW-LvXAQYLOOHMUI4vhm5aQBNCO9KaCKpoQ-OLDOAplxDX52jxhHVd08vWgbq9G7CMEHzQl2o59pTWM4tJGh2vaxG7sxc)
9. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPF_VN4vhO3KJI9zAq-qi0jP2PrMxVtEuLZ_4ahBwnBBx5n-xV8HCjAzAlBJ6W4XUR6PLEBjwWvqh9mHQtpTJAtMCgoF6_ZANaB4BoOqrNdkMvT9Wb_P35Ehdl_R3LlLJR9NvdsykQb27-)
10. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnPXdf8Ace0nCN_vd3kBH_80IPrqEFUU018Q3e3e9NIBkE50bZFkJvjk7MCiWzfFIUYcijdCi0xkxHDiMGzRXwhtzFc1fnL32qcgdGM-LPMHcTDeK0lNI_iw5q-ppcdHpL-qdl)
11. [unifi.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjNW5UFP4_3BtkhJ71kdlT4XPSONdbeblZ3ioItIgIh8VARQbvUdnm7_7YtD-d0cmxoHwfK5Tnvx7_tv6HzbcmTdYX6X773WVGMzFFaGOZBEPhEE6uj_nEZ0XMW1zWLqrZn5VffUBcJCIlZ6eny9UC)
12. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhG667WgFNFRJpy3d2Iqz7apdZAhHGyMONjfdTh6keLzfCS0juWnAOOp7qhMRrHCbAnCfeXuwQATV2qmvKafbd7dFzIRSsMhP8btg9uJrHU62dVAxtBS60DmEyamjNSoVh8AUlhIZsSdDb)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfmyluVCUqpxM4mVOTiGWc7PiS93JmByKblHA0grbOI0hxcajrfETzxFJN_rCZQGnml03TZJ-RmOyItcm943GPm6vK8cJvLGLL6GEB1sO53O5iZ6zcwA==)
14. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgVQspJYxghPg2SGlvGCMQdga9Ys7KMMSfYS3kmBNsl7HS14ZTlcTL0Qe-92N5bDG54ViL2XWt1VqB7wYwoAyAjX66R3bUqEatrq01cyvvl67ir-UywG3Kiyyf_d70aclepXLAeitkXETgcMa1JXcRY4KqeoPfE55ivJJJHrbAZuIO9Q==)
15. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfmVrhrB2uuJrDHgbFpf7RdZvOI-Sh1Gz4LwVGyaCentTL_aBfTi841zYgG5LVRFbo968ASThj19K_gwsJggqyUwfD9mljbh9d6WT5j_O2N21VEZvbFFiUspzazUKud72GgUQ=)
16. [griffith.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9Y630E5OxI1jHVqtlkAFm1FmnCI9MjCgX_biykXN0smFRyU8Z4fh2EkdHa1n7hu7Pzc6Yv42wr_eQsXZim2Uei7o2Xhg0u-YrSbvgPIDfZjZHtfu-fQPieM6Gr06LsVeLUJ56r4dOGjcNAS2ajRDJIYfIP1z4HiWMguk5FcTUO5uz_E3tIkEYgilx63VlPfDHzi4HHmjpqYT-iyTQejCtRvIzFZLzKlPP)
17. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXvnvCETlv9IpFccjj6yBvVKC_lecUzfzFRJfg8nTwsAVgYVADJmcU2_f9YZsMKIbXM7CtVfTJFxzHEyQBQ0XlYbdJjXL8FqNlso_MgEK5egOU5MqtohgJ75fdEckHFp6MqoePcGXEjpvKMX2aTm4OnKGjzLvK4Yw=)
18. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyx4Olxj8CAoL6VzxKdUVeQ4AZ38V5tGV_Z9TYma0gPipOO3ZsUyN9v5m5PkKHyETrSPG7RMo5V5OHv-zuUDJ9i6tqaTaBCwIHD9a8A8hZaG37d_ALZMn-YGpSyfWgK1QVy26Ozj7JGRUVn8LjcGbMDFrYQy8sPDiWTpT8NEhfkg==)


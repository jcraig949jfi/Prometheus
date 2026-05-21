# T#46 HOPM convergence rate (Higher-Order Power Method)

**Pythia queue id:** 89
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdEeFFQYXYyektLU0MtOFlQM0p5SmtBcxIXRHhRUGF2MnpLS1NDLThZUDNKeUprQXM
**Elapsed:** 319s
**Completed at:** 2026-05-21T14:23:11.407000+00:00

---

# Comprehensive Analysis of the Higher-Order Power Method (HOPM) and Its Convergence Rates

The Higher-Order Power Method (HOPM) is a foundational algorithm used in multilinear algebra to find the best rank-one approximation of a multidimensional array, or tensor. While it generalizes the classical matrix power method, the mathematical properties of tensors make its convergence behavior significantly more complex. Research suggests that while HOPM is guaranteed to eventually find a solution (a critical point), the speed at which it gets there—its convergence rate—can vary wildly depending on the tensor's inherent structure, the chosen initialization, and the specific variant of the algorithm employed.

**Key Points**
*   **Global Convergence:** Evidence clearly shows that HOPM always converges globally to a singular vector tuple, a property rigorously established using the Łojasiewicz gradient inequality [cite: 1, 2].
*   **Generic R-Linearity:** For the vast majority of tensors (almost all, in a strict mathematical sense), the algorithm appears to converge at an R-linear rate because their critical points are generically non-degenerate [cite: 1].
*   **Sublinear Worst-Case:** The absolute worst-case convergence rate is sublinear, bounded explicitly by the tensor's order and dimensions [cite: 1].
*   **Special Cases:** For specific structured tensors, like orthogonally decomposable tensors of order 3 or higher, the convergence rate is unconditionally R-linear [cite: 1, 3].
*   **Superlinear Potential:** Under strict dominance conditions or with specific extrapolations and quasi-Newton augmentations, the method can achieve superlinear convergence [cite: 1, 3].

### Background Context
Tensors are essential mathematical objects used to model complex, multi-way data interactions in fields ranging from quantum physics and signal processing to machine learning and data mining. Finding the best rank-one approximation of a tensor allows researchers to isolate the most dominant, primary component of the data. 

### The Convergence Challenge
Unlike matrices, where the power method reliably converges to the dominant eigenvector at a predictable linear rate, tensors lack the same spectral guarantees. The multilinear nature of tensors introduces non-convexity to the optimization landscape, meaning algorithms can get stuck in local optima or experience extremely slow convergence. Determining the exact rate at which HOPM converges—whether it crawls to a solution sublinearly or races to it superlinearly—has been a major focus of numerical optimization research over the last decade.

---

## 1. Introduction to Tensor Approximations and HOPM

As generalizations of matrices, tensors (also known as hypermatrices or multi-way arrays) are ubiquitous in scientific computing, data analysis, computational complexity, and applied sciences [cite: 1]. One of the most fundamental problems in multilinear algebra is finding the best rank-one approximation of a real tensor. This is equivalent to finding the tensor's largest singular value, commonly referred to as its spectral norm [cite: 2, 4].

### 1.1 Mathematical Formulation
Let $\mathcal{T} \in \mathbb{R}^{n_1 \times n_2 \times \dots \times n_d}$ be a real-valued tensor of order $d$. The best rank-one approximation problem seeks a scalar $\lambda$ and unit vectors $x^{(i)} \in \mathbb{R}^{n_i}$ with $\|x^{(i)}\| = 1$ for $i = 1, \dots, d$ that minimize the Frobenius norm of the difference:

\[ \min \| \mathcal{T} - \lambda x^{(1)} \otimes x^{(2)} \otimes \dots \otimes x^{(d)} \|_F \]

Due to the properties of the Frobenius inner product, this minimization problem is mathematically equivalent to the maximization of a multilinear form on the product of unit spheres [cite: 1, 2]:

\[ \max \mathcal{T}(x^{(1)}, x^{(2)}, \dots, x^{(d)}) \]
subject to $\|x^{(i)}\| = 1$ for $i = 1, \dots, d$. 

The maximum value of this objective function is defined as the largest tensor singular value (or spectral norm) $\lambda^*$, and the corresponding vectors $(x^{(1)}, \dots, x^{(d)})$ form a dominant singular vector tuple [cite: 2, 4]. Solving this system of non-linear equations is generally referred to as the U-eigenpair problem for the tensor $\mathcal{T}$ [cite: 5, 6]. Because the problem is NP-hard, exact global techniques such as homotopy continuation methods may require exponential time, necessitating the use of approximate iterative algorithms [cite: 5, 6].

### 1.2 The Higher-Order Power Method (HOPM)
To the best knowledge of the scientific community, the Higher-Order Power Method for solving the best rank-one approximation problem based on the maximization formulation was first proposed by De Lathauwer, De Moor, and Vandewalle [cite: 1]. The HOPM is a straightforward generalization of the alternating power method used for finding a pair of dominant left and right singular vectors of a matrix [cite: 2, 4]. 

Depending on the scaling strategy used for the iterates during the process, HOPM can be seen as an application of the classical nonlinear block Gauss-Seidel (coordinate descent) method to the maximization formulation, or as an Alternating Least Squares (ALS) algorithm [cite: 1, 2]. In practice, ALS and HOPM are equivalent in the sense that they generate the exact same iterative sequence up to scaling, given the same initialization [cite: 1, 3].

## 2. The Algorithmic Framework

The standard HOPM operates by fixing all but one of the vectors in the tuple and optimizing the objective function with respect to the free vector. This alternating maximization is iteratively applied across all $d$ modes of the tensor.

**Algorithm 1: Higher-Order Power Method (HOPM)**
1. **Input:** Tensor $\mathcal{T} \in \mathbb{R}^{n_1 \times n_2 \times \dots \times n_d}$, starting guesses $x_0^{(1)}, \dots, x_0^{(d)}$ with unit norms.
2. **Initialize:** Set $k = 0$.
3. **Repeat until convergence:**
4.   **For** $\mu = 1, 2, \dots, d$ **do**:
5.     Compute the tensor-vector contraction (TVC) along all modes except $\mu$:
       \[ y_k^{(\mu)} = \mathcal{T} \times_1 x_k^{(1)} \dots \times_{\mu-1} x_k^{(\mu-1)} \times_{\mu+1} x_{k-1}^{(\mu+1)} \dots \times_d x_{k-1}^{(d)} \]
6.     Update the vector by normalizing:
       \[ x_k^{(\mu)} = \frac{y_k^{(\mu)}}{\|y_k^{(\mu)}\|} \]
7.   **End For**
8.   Calculate the approximate singular value $\lambda_k = \mathcal{T}(x_k^{(1)}, \dots, x_k^{(d)})$.
9.   $k \leftarrow k + 1$
10. **Return:** Spectral norm $\lambda^*$ and singular vector tuple $(x^{(1)}, \dots, x^{(d)})$.

This block coordinate descent nature ensures that the sequence of generated approximated singular values $\lambda_k$ is monotonically increasing [cite: 2, 4]. However, monotonicity alone only guarantees the convergence of the sequence of objective function values, not the single-point convergence of the vector factors themselves.

## 3. Global Point-Wise Convergence Guarantees

For many years, a satisfactory convergence theory for HOPM was a prominent open question [cite: 2, 7]. While the convergence of the generated sequence of approximated singular values followed easily from the monotonicity of the method, the point-wise (single-point, not just sub-sequential) convergence of the sequence of generated rank-one tensors or their factors to a critical point remained elusive [cite: 2, 4].

Early investigations by Mohlenkamp demonstrated that the sequence of rank-one tensors generated by ALS is bounded and that their consecutive differences are absolutely square summable, thereby converging to zero [cite: 4, 7]. This would imply full convergence if the set of cluster points (each of which must be a critical point) contained at least one isolated point. Wang and Chu later addressed this by arguing that for almost every tensor, the second-order derivative at zeros of the projected gradient of the cost function is regular, making critical points isolated and ensuring global convergence for generic tensors [cite: 7].

### 3.1 The Łojasiewicz Gradient Inequality
The definitive proof of global point-wise convergence for HOPM, without requiring generic regularity assumptions, was provided by Uschmajew [cite: 3, 7]. The proof relies on an elegant method from the theory of analytical gradient flows, whose foundation is the **Łojasiewicz gradient inequality**—a powerful feature of real-analytic functions [cite: 2, 7].

The classical Łojasiewicz gradient inequality states that if $f$ is a real-analytic function defined on a neighborhood of a critical point $x^*$, there exist positive constants $\mu, \kappa$, and an exponent $\theta \in [1/2, 1)$ such that:
\[ \|\nabla f(x)\| \geq \mu |f(x) - f(x^*)|^\theta \]
for all $x$ in a neighborhood of $x^*$ [cite: 1, 8]. 

By applying the theory of Łojasiewicz inequalities to the equivalent, unconstrained alternating least squares algorithm for best rank-one tensor approximation, it was proven that the sequence of factors in HOPM inherently satisfies the conditions for absolute summability of increments [cite: 2, 9]. The validity of the Łojasiewicz inequality at a cluster point of a gradient-related descent iteration enforces that the sum of the distances between consecutive iterates is finite, which strictly implies single-point convergence [cite: 7]. Therefore, HOPM is globally convergent to a singular vector tuple from any initialization.

## 4. Convergence Rate Analysis of HOPM

While global convergence is guaranteed, the rate of convergence is highly dependent on the properties of the objective function near the critical point. Depending on the tensor and the initialization, the iterative sequence generated by HOPM can converge at sublinear, linear, or superlinear rates [cite: 1]. Understanding these rates requires deep geometric analysis of the tensor's singular vector tuples.

### 4.1 Sublinear Convergence (Worst-Case Bounds)
In the optimization literature, an iterative sequence $\{x_k\}$ is said to converge sublinearly if it converges slower than a geometric progression. Mathematically, a sequence converges Q-sublinearly to $x^*$ if:
\[ \lim_{k \to \infty} \frac{\|x_{k+1} - x^*\|}{\|x_k - x^*\|} = 1 \]
and R-sublinearly if it is bounded by a Q-sublinear sequence [cite: 10, 11].

Hu and Li established an overall sublinear convergence rate for HOPM in solving the best rank-one approximation for real tensors [cite: 1]. The explicit eventual sublinear convergence rate estimate is intrinsically tied to the dimension of the underlying space and the order of the tensor [cite: 1]. This is derived from the worst-case Łojasiewicz exponent $\theta$ for polynomial systems. Specifically, if the Łojasiewicz exponent $\theta > 1/2$, the resulting convergence rate is sublinear. Interestingly, the derived convergence rate estimate of the objective value sequence using multilinear properties is sharper than the usual $O(1/k)$ convergence rate established for general first-order algorithms in non-convex optimization [cite: 1, 12].

### 4.2 Generic R-Linear Convergence
While the worst-case bound is sublinear, HOPM typically performs much better. A sequence $\{x_k\}$ converges Q-linearly to zero if the ratio of successive errors is bounded by a constant $c \in (0, 1)$. It converges R-linearly if there exists a Q-linearly convergent sequence $\{e_k\}$ such that $\|x_k - x^*\| \le e_k$ for all $k$ [cite: 10, 13].

The R-linear convergence of HOPM hinges on the concept of **non-degenerate singular vector tuples**. On a smooth manifold, a smooth function is a Morse function if each of its critical points is non-degenerate—meaning the Hessian matrix in local coordinates at each critical point is non-singular [cite: 12, 14]. If the sequence generated by HOPM converges to a non-degenerate singular vector tuple, the Łojasiewicz exponent $\theta$ is exactly $1/2$, which mathematically guarantees that the global convergence rate is R-linear [cite: 1].

Hu and Li demonstrated that for *almost all tensors* (in the strict mathematical sense of Lebesgue measure), every singular vector tuple is non-degenerate [cite: 1, 3]. The set of tensors with degenerate singular vector tuples forms a set of Lebesgue measure zero [cite: 1]. Consequently, HOPM typically exhibits a global R-linear convergence rate without requiring any ad-hoc modifications [cite: 1, 3].

### 4.3 Superlinear Convergence
A sequence converges Q-superlinearly to $x^*$ if:
\[ \lim_{k \to \infty} \frac{\|x_{k+1} - x^*\|}{\|x_k - x^*\|} = 0 \]
This indicates that the algorithm accelerates as it approaches the solution, taking fewer iterations to achieve high precision [cite: 10, 13].

It is known that the convergence rate of HOPM can be superlinear under specific conditions [cite: 3]. Local superlinear convergence for ALS/HOPM occurs when there is a strong dominance hypothesis regarding the eigenvalues/singular values, or when starting guesses are sufficiently close to a highly dominant critical point [cite: 1]. However, strict superlinear convergence is not generically guaranteed for standard HOPM. 

To systematically achieve superlinear convergence, researchers often turn to hybrid or augmented methods. For instance, applying a heavy-ball momentum term, Nesterov extrapolation, or Newton-type iterations on Riemannian manifolds can force superlinear or even quadratic convergence [cite: 15, 16]. Furthermore, modifications like the Gram iteration have been introduced to achieve superlinear convergence as an alternative to standard power iteration, although these can be more memory-intensive depending on the application [cite: 17]. 

### Summary of Convergence Rates

| Convergence Type | Definition | Condition in HOPM |
| :--- | :--- | :--- |
| **Sublinear** | $\lim_{k \to \infty} \frac{\|x_{k+1} - x^*\|}{\|x_k - x^*\|} = 1$ | Worst-case scenario; occurs if the algorithm converges to a degenerate critical point where the Łojasiewicz exponent $\theta > 1/2$. Explicit bounds depend on tensor order and dimension [cite: 1, 10]. |
| **R-Linear** | Bounded by a Q-linear sequence | Typical behavior. Occurs when converging to a non-degenerate singular vector tuple ($\theta = 1/2$). Guaranteed for almost all tensors (Lebesgue measure 1) [cite: 1, 3]. |
| **Q-Superlinear** | $\lim_{k \to \infty} \frac{\|x_{k+1} - x^*\|}{\|x_k - x^*\|} = 0$ | Occurs under strict eigenvalue dominance hypotheses, or when using accelerated algorithms (e.g., Gram iteration, quasi-Newton adaptations) [cite: 13, 17]. |

## 5. Structural Specialization: Orthogonally Decomposable Tensors

An important class of structured tensors that deserves special attention is the so-called orthogonally decomposable tensors [cite: 1, 3]. A tensor $\mathcal{T}$ is orthogonally decomposable if it can be written as a sum of rank-one tensors formed by mutually orthogonal vectors. This structure mimics the spectral decomposition of symmetric matrices and is highly relevant in applications like independent component analysis (ICA), topic modeling, and Gaussian mixture learning [cite: 18].

For orthogonally decomposable tensors, the landscape of critical points is exceptionally well-behaved. Research establishes that, without any generic regularity assumption, *every* non-zero singular vector tuple of an orthogonally decomposable tensor with an order of at least 3 is non-degenerate [cite: 1]. 

Because non-degeneracy is strictly guaranteed for all critical points of interest, the sequence generated by HOPM always converges globally and R-linearly for orthogonally decomposable tensors (order $\ge 3$) [cite: 1, 3]. This finding solidifies HOPM as a highly robust and predictably fast algorithm when applied to data that inherently possesses orthogonal multi-way structures.

## 6. Variants and Adaptations of HOPM

The standard HOPM has been extended and modified to handle specific subclasses of tensors and to overcome computational bottlenecks in modern hardware environments.

### 6.1 Shifted Symmetric HOPM (SS-HOPM)
For symmetric tensors (where the entries are invariant under any permutation of the indices), the standard HOPM can sometimes fail to converge to an eigenvector of the tensor, instead oscillating between states [cite: 3]. To resolve this, the Shifted Symmetric Higher-Order Power Method (SS-HOPM) was introduced. SS-HOPM incorporates a shift parameter $\alpha$ to ensure positive definiteness and enforce strict monotonicity of the Rayleigh quotient [cite: 15, 19].

The point-wise convergence of SS-HOPM has also been solidly proven using the Łojasiewicz inequality [cite: 19, 20]. By establishing a mapping from the sequence generated by the algorithm to an unconstrained optimization sequence, researchers proved that the sequence $\{x_k\}$ strictly converges to a symmetric rank-one approximation (a Z-eigenpair) [cite: 3, 19]. Much like standard HOPM, SS-HOPM typically exhibits global R-linear convergence, but it can be notoriously slow if the fixed shift parameter is not optimal [cite: 12, 20].

### 6.2 Generalized Eigenproblem Adaptive Power (GEAP) Method
To improve upon SS-HOPM, the Generalized Eigenproblem Adaptive Power (GEAP) method was developed [cite: 21]. GEAP reformulates the generalized tensor eigenproblem as a nonlinear program where generalized eigenpairs are equivalent to Karush-Kuhn-Tucker (KKT) points. Unlike SS-HOPM, which uses a fixed shift, GEAP employs an adaptive method for choosing the shift parameter dynamically at each iteration [cite: 21]. This adaptive shift selection severely reduces the number of function evaluations required, drastically improving empirical convergence speed and allowing the algorithm to find generalized eigenpairs significantly faster than SS-HOPM [cite: 21].

### 6.3 Quantum HOPM (QHOPM)
With the rise of quantum computing, HOPM has been adapted to run on near-term quantum devices to estimate the geometric measure of entanglement of multi-qubit pure states [cite: 5, 6]. The algorithm, known as QHOPM, performs the crucial Tensor-Vector Contraction steps (lines 4-8 in the standard HOPM algorithm) on a quantum device [cite: 6]. 

In practical quantum simulations, QHOPM demonstrates remarkable efficiency. While purely classical variational quantum circuits (like VDGE) are prone to "barren plateaus" as the number of qubits grows, QHOPM bypasses this issue. In all studied examples, noiseless QHOPM converges in approximately 4 iterations [cite: 5, 6]. The accuracy of the results is highly dependent on the number of quantum measurement shots rather than the number of qubits, satisfying the Chernoff bound [cite: 5, 6]. Furthermore, QHOPM is robust to realistic hardware noise; even in noisy environments, it converges to a stable value that can be successfully corrected using simple mitigation techniques [cite: 5, 6]. The formal convergence rate of QHOPM remains a complex extension of the classical HOPM rate for real-valued tensors, but its empirical iteration count is highly favorable [cite: 5, 6].

### 6.4 Distributed HOPM (dHOPM)
As the order and dimensions of tensors grow, the memory and computational requirements of HOPM become a bottleneck. The core operation, Tensor-Vector Contraction (TVC), is heavily memory-bound. To address this, high-performance distributed variants such as **dHOPM 3** have been developed using Message Passing Interface (MPI) protocols [cite: 22]. 

dHOPM 3 brings distributed-memory parallelization to the native TVC algorithm. It uses an optimized three-buffer approach to save intermediate tensors and hold previously computed data in memory, remaining entirely oblivious to the specific contraction mode, tensor splitting, and tensor order [cite: 22]. This distributed implementation can save up to one order of magnitude of streamed memory compared to naive parallelization, confirming linear (and sometimes superlinear) computational scalability across CPU and GPU architectures [cite: 22].

## 7. Acceleration and Extrapolation Techniques

Because the generic R-linear convergence of HOPM can still be slow in high-dimensional spaces with tightly clustered singular values, several extrapolation methods have been incorporated into the algorithmic loop to accelerate convergence.

1. **ES-SHOPM (Extrapolated Shifted Symmetric HOPM):** Functions as an accelerated SS-HOPM by employing a fixed extrapolation parameter to impart momentum [cite: 15].
2. **DES-SHOPM (Dynamically Extrapolated):** An automated variant of ES-SHOPM that dynamically approximates the optimal parameter, overcoming the need for *a priori* knowledge of the tensor's spectrum [cite: 15].
3. **N-GEAP (Nesterov GEAP):** Applies Nesterov's accelerated gradient momentum to the GEAP solver, pulling inspiration from convex optimization to enhance the convergence rate [cite: 15].
4. **Minimal Polynomial Extrapolation (MPE) and Reduced Rank Extrapolation (RRE):** Vector extrapolation methods that have been shown to accelerate the computation of tensor PageRank vectors and general multilinear approximations, particularly when HOPM slows down near degenerate critical points [cite: 23].

## 8. Conclusion

The Higher-Order Power Method stands as an indispensable tool for best rank-one tensor approximation. Early ambiguity regarding its convergence behavior has been fully resolved through the application of the Łojasiewicz gradient inequality, which guarantees global point-wise convergence to a singular vector tuple. 

In terms of convergence rates, the theoretical landscape is now well-mapped: while the worst-case bound is strictly sublinear due to geometric properties of polynomial systems, HOPM operates at an R-linear rate for almost all real tensors because degenerate critical points are extremely rare (Lebesgue measure zero). For practically important classes like orthogonally decomposable tensors, R-linear convergence is unconditionally guaranteed. 

Today, the core principles of HOPM continue to evolve. Whether it is being accelerated through dynamic extrapolation, distributed across massive GPU clusters via optimized tensor-vector contractions, or ported into the quantum computing domain to measure qubit entanglement, HOPM remains a highly adaptable, robust, and mathematically fascinating algorithm.

**Sources:**
1. [unsw.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8M9yTeH0RfkXs0EsCRcxoPuemB0BospfhHgsDYPbOBXScNm7oTJeeghQPJMA2gft1gkPheTsjCjxCF2WQccT4xJHlJBOOm-c_VUpZI1lFQO38gK8nP0veOv8h-z-npb3PYsXSDPQuWiOGJFx9SrBTFikqLv4jFLw=)
2. [ybook.co.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXDASDS00RKiFHuPKA2bEcP_Jov2mtUpwKImFJEDbEx3c80K0YwI0Yum6Kxa5x5n34l0Nx48iZWeYQEX76Aey-3DvR7nzgpZw9I24uVIjsHJjWlVAjFgcWRDODgW9LwBkC68hErDv5cDi1uPkK_Vyj)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhwIEwBpEUmmyBtAw0QZXxhsbe_mQFcDTypK8yPDmyvK1NP2kV5tvJlSy8d8xEurPY10rcpBqSVeBhaq3KRxBN1KZEntX9YNkfWOk2520NwOtkoHOzSpDhM6zSXEGpAfBia-ClErh8q1yddsTFRXZ6wET9ypUcdMr6xCLsBVWhj-8D5Fum5vKyQk9X73z74ihbRj9xtFTeljlG7dQGNF37aeUGzrsE6R9WW7oBnlNV_ZmmG1op-hg=)
4. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESYDGOzCxLXxF7zPRugqoDyzcaRjGp498OyTTLRbdRt_jJ1x5Q0VBQJqv0opB8DIVkp4DBHYBbfUYOK_W788gf7AMNLisFJ3Az0LlSTwyKl0Q3ahFzS1PwKnEMl7M4_o8bTqwvgXCXUhvQKTEgqFPMTWVn7dywDavQrUKmS0P0G1oEAq1_5sKPseXvqQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEec1SfPAXwRRK6_kcMIdm7pxm5TaXPCUJwczH9p76lnP3Q8juiVctDBmDNE7NMKWN5sz3XQBgNNQuF_3pIsA-SS4SE-qCRPdbD0e7TxrbZFLZem9VtWg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElxUT32FtuszIKizTbrB1s1hPOJwCzH3125HoAUw1TWuZazLZHxCVocTSyapiT164wX80-iWRsdnXncYD0HwSvtBVO0-AzoZkXSp85aGa6rg6vcqYfPandvQ==)
7. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-7RHAsuMYJiAn5LjQRFmkqI_o-mgkJb6p6-9WUHy03iQfFEAfOdDKtF-wQezV_lavH_EIADA0ugeIUnaxNVqwXvMrEDLby-0QtLAjcjayQeQ2PJ9XGVMVfYT9hBXrNZjucY7yzGVzs3Jx9GA=)
8. [cuhk.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrJbi0x06KbmA-MgcW73SgFH37B7YGfSWaZKhBAGtSPJb4INnUtlQiKQv2QOjl0vs1YM2wQ9LZco9PRfhvYpkQ7i_WdTAe8CFN8snix-b68gZXefPgcd_9kIRA8lYhfU3FhKSAAo_lfip2x0enhs3dgi5ng6GHAG43FFQv)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIHE7Mye3wrrHiFJKoniSdq7Uqbc_egasYAZU9qqiAjbqhBgff6XuZj0bME6s7FqYnkhCyxiinJv70chXXZnMFwb4kmJwPp9zSjOcTNyNYJ2veyH5T)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6D1GlRHsy96HhC0hhdNa06E77eM6RizL35Q7doHWVncszjBE7xsUcg8NRMnQKnhw56vLew7cX1-XoqeRGMIVSypgxE5D451tJcRVfftLSNZDVHpTGnXrdPiuv7BVaTOgt95gxZa3Q)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtEgtZabuf_dx3_2TenCvuuuKjj72gvetR4eZJwv0vMiwl0N07c4Azp-5IXblGVQcRhD1h488UrzV_pqzccwIe-IdzAT89M0IuoqSntLKK_d3iLJJXrX_AciEAK1E9HiEViQMPYxySa3gBhmsPuseyTY7qvgPcXHqo_M6mg7DaatG7oDbtNwkkK8TH5zhSBAxY8xwOevQDY3JOdZslnzGkE5Mub9yqEqI-x3LMksmgGCv6IWRD-9dQZg==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFkVnAjBnv4zBVNKbKdohltX4lpniE126HNhYIgvGRPYlviS7V_DyCBEzZR4DazpTndbEH43ln1wBvimk1m5Elzl0BzNnrJhlf9Nbq2Z5hUhv-vXBLmQ==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMSAtcuqVHz1ykrmR2DYQJO62Rqw1rChz7k8vicVnxM1gotTsh-KXcGQn8ga3K6haUZQd0bB603vCjxutVCL4omudZSap-x9uGKsVjxQ0hOBQi2obvRQ==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUTHqYC-I8vnqDfrMVzJA0bwsXsoA2m8P-knpulLnWiTI3lwL5SqFbirk1LaXmdqotnI79W61alKvc7MGzptMtfaO0GUo9PIWs3MBf0lH21hEnIVeU4Q==)
15. [ufl.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTtmrYlWdL5Co-OIJizmgxanj_6rDbc28uY8xnt_mpzPplK19KPAM77wdgKbQKCLs_D0tQUVMhJ0LhU3lu7vfyVWnWA53IJlJfAGsE8hfs8j0xpNpEZyVkEZ0yimJRuga6NrxV4GPDbaB4a9fg_7I-kvDraGK1DGg=)
16. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5RKDx0SvBbOobrGaTO-ydzr6tT5Fl-ge4RosfIwLkPPUaAcJBWofQBYQINYBTwaNL1HT_az9U_EN188z-WRLLPFYTBL55sJpQbqxNzAx4VNCsV_RhLQSyOjWd3npMUTE=)
17. [ecva.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjEp2tEG2_S43i-mysoNSoqtZNcsfIbBvO4jac3KBnswoZj2HQQWYGnkhUY9MH1ZllehYLj_0cnE_ZWjUKGs51V1YHzBftLn3eYMVSuEg__RLcxO4CxHlnyfd6wxHJqMY90dH6VfE2iBTJzEFtN-ED23mnY8Hcteg=)
18. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgaj_L342M8c1ncN46LHyv3kyDBfDy9thnnqj7nA8yjzFT8ao4wer5NAXHb1yxrrHzzSPj68KsGT4JsBMYOwZDu4YXSwFEGcsoyRSO_F-Bt7-Pm9dVOAGASEREKMzg2yigDd4=)
19. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVZn-Z22oO8VQ4AxFJ_yrCReW-dWVJBnFiCjnkHcAamxwz7ee4NEDc4OjTtuOtPi4QH0iDoqb6XsRMopAQOjplUrjbSfwGAsipnNOAk_wypO8eo29AefF7xpOCBZggvNknEZb4H7xEx7Fftj_C560YXac=)
20. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwhZMBjNegP4iZqbPB1wJ3Jt4tyXpWMJJ9-9HbBfJq2z_oUhbkA9h0HXasiG60pbjYgqZp6L38imOrrOYkY25y6ZWBF2_Gb2PAFPsELd-nXNKT_B1RrWPFNTkZ52DNi6sZrrOH_MaBe9c0IayLMQVpoEAMzENDPDj93DsIPHzYnDaoFBlWo5O08c_s_MOKeTiD-PX1MP1WXOyITqqm-r8EuTKIMIoLnZAQLPw3wtdpguAJu5yeBy00f8TeLUOd9L10nw==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3_c1ZkLzi3_yh6LC8J0pKwOu9Gw44K4KyopZzWUdBEWM9tZTDU4NF268BKbcUbCnRN3Ql466A6vc_VByHsq1sowb-QsUrAFeTCmMvfZWhdeU18P38)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEn99KaTthQufBV4yzCzPJxuoQw5UtDUNjBngZckgGp_hW196pu0AjSgYjK1ejCvRcfoomcUlE8jD2SJyLFDvkQpq2MUcF6HRRoMRVctG_vaxGiJnO6YQSvcA==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZDs8FJ4S4QIoV7N1m3mw2u0t_bTu_ntYk5pdLY8i1jpzwJT59Iwbh3-ReuOq5RnHZmmyq2jxA_P_DOUY9IigevWP2zo9zmJU90fKw_huuQCg7MqijWOTkHj9TtPgDXOLAuFF7efjxIM9ArEuFK_wna5OP7xenv8af20GmJdzmVx-0Qx61YziGloSTGq6thyG1oETgEtkOGxDFTv2chvgdGlw2LIuu2MaBBmjWFaPqU5nOE578)


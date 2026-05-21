# T#64 Number of real eigenvalues of symmetric tensors (Cartwright-Sturmfels)

**Pythia queue id:** 105
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdfUjBQYXJLTEJ1TzJfdU1QNDQ2U3VBNBIXX1IwUGFyS0xCdU8yX3VNUDQ0NlN1QTQ
**Elapsed:** 372s
**Completed at:** 2026-05-21T15:06:26.210369+00:00

---

# Number of Real Eigenvalues of Symmetric Tensors: The Cartwright-Sturmfels Theorem and Beyond

*   **Tensor eigenvalues generalize matrix eigenvectors** but behave fundamentally differently; while symmetric matrices possess exactly $n$ real, orthogonal eigenvectors, symmetric tensors can have complex eigenvectors, and the total number of eigenvectors generally scales exponentially with the dimension.
*   **The Cartwright-Sturmfels formula** provides the exact count of complex eigenpair equivalence classes for a generic symmetric tensor of order $m$ and dimension $n$, establishing the upper bound as $\frac{(m-1)^n - 1}{m-2}$. 
*   **The existence of real eigenvalues** depends heavily on the order of the tensor: research shows that odd-order symmetric tensors possess at least one real eigenvalue, whereas even-order symmetric tensors possess at least $n$ real eigenvalues.
*   **Statistical distributions of real eigenvalues** for random Gaussian tensors have been rigorously established recently, linking the expected number of real tensor eigenvalues to the critical points of Kostlan polynomials. 
*   **Computational complexity** remains a significant hurdle; computing tensor eigenvalues is generally NP-hard, though advanced algebraic techniques like Jacobian semidefinite relaxations and homotopy continuation offer pathways to sequentially compute all real eigenvalues.

The spectral theory of tensors represents a profound evolution of classical linear algebra into the realm of multilinear algebra. Initiated independently by Lim and Qi in 2005, the study of tensor eigenvalues has rapidly expanded to address complex problems in physics, data science, and continuum mechanics. Unlike matrices, where symmetry guarantees real eigenvalues, real symmetric tensors often harbor a mix of real and complex eigenvalues. The exact enumeration of these values was a major open question until Dustin Cartwright and Bernd Sturmfels provided a definitive algebraic geometric proof. Finding the real eigenvalues—those with actual physical or geometric meaning—remains a complex challenge that weaves together topology, optimization, and quantum field theory. The evidence suggests that while the algebraic geometry of tensors is well-defined over the complex plane, navigating the real algebraic geometry of tensors requires sophisticated probabilistic and topological machinery. 

## 1. Introduction to Tensor Spectral Theory

The study of matrices and their eigenvalues forms the bedrock of classical linear algebra, dynamical systems, and quantum mechanics. However, as modern computational mathematics advances, the limitations of two-dimensional arrays (matrices) become apparent when modeling higher-order interactions. A tensor is a multidimensional array of numerical values, generalizing vectors (order-1 tensors) and matrices (order-2 tensors) to an arbitrary order $m$. A tensor $\mathcal{A}$ of order $m$ and dimension $n$ over the real field $\mathbb{R}$ is denoted by its components $\mathcal{A}_{i_1 i_2 \dots i_m}$, where each index $i_j \in \{1, 2, \dots, n\}$ [cite: 1, 2]. 

In 2005, the spectral theory of high-order tensors was independently formalized by Lek-Heng Lim and Liqun Qi [cite: 1, 3]. They introduced multilinear generalizations of the classical matrix eigenvalue problem. For a generic matrix $M$, an eigenvector $x$ satisfies the linear transformation $Mx = \lambda x$. For a tensor $\mathcal{A}$, the corresponding contraction with a vector $x \in \mathbb{C}^n$ involves projecting the tensor along $m-1$ of its modes. Specifically, the contraction $\mathcal{A}x^{m-1}$ yields a vector in $\mathbb{C}^n$ whose $i$-th component is given by:
\[ (\mathcal{A}x^{m-1})_i = \sum_{i_2=1}^n \dots \sum_{i_m=1}^n \mathcal{A}_{i, i_2, \dots, i_m} x_{i_2} \dots x_{i_m} \]

A tensor is termed **symmetric** if its entries $\mathcal{A}_{i_1 i_2 \dots i_m}$ are invariant under any permutation of the indices [cite: 1, 4]. Symmetric tensors are intimately connected to homogeneous polynomials. For any symmetric tensor $\mathcal{A}$, one can define an associated homogeneous polynomial $f(x)$ of degree $m$:
\[ f(x) = \mathcal{A}x^m = \sum_{i_1=1}^n \dots \sum_{i_m=1}^n \mathcal{A}_{i_1 \dots i_m} x_{i_1} \dots x_{i_m} \]
The tensor contraction $\mathcal{A}x^{m-1}$ is directly proportional to the gradient of this polynomial, satisfying $\nabla f(x) = m \mathcal{A}x^{m-1}$ [cite: 2, 5]. 

## 2. Formal Definitions of Tensor Eigenvalues

Because the tensor eigenvalue equation $\mathcal{A}x^{m-1} = \lambda x^{[m-1]}$ (where $x^{[m-1]}$ denotes a vector with elements $x_i^{m-1}$) lacks the straightforward scale invariance of matrix operations, researchers have proposed multiple normalization constraints, leading to several distinct classes of tensor eigenvalues.

### Z-Eigenvalues and E-Eigenvalues
The most geometrically intuitive class is the **Z-eigenvalue** (and its complex counterpart, the E-eigenvalue). A scalar $\lambda \in \mathbb{C}$ and a non-zero vector $x \in \mathbb{C}^n$ form an E-eigenpair if they satisfy:
\[ \mathcal{A}x^{m-1} = \lambda x \]
\[ x^T x = 1 \]
When both $\lambda$ and $x$ are strictly real, $\lambda$ is termed a **Z-eigenvalue** and $x$ a **Z-eigenvector** [cite: 3, 6]. The term Z-eigenvalue historically arises from the fact that it corresponds to the critical values of the polynomial optimization problem on the unit $l_2$ sphere (or Z-sphere). 

### H-Eigenvalues
Alternatively, Qi introduced the **H-eigenvalue**, which restricts the normalization to the $l_m$ norm [cite: 6]. An H-eigenpair satisfies:
\[ \mathcal{A}x^{m-1} = \lambda x^{[m-1]} \]
where $x^{[m-1]}_i = x_i^{m-1}$. This definition aligns well with the positive definiteness of tensors. A symmetric tensor is positive definite if and only if all of its real H-eigenvalues are strictly positive [cite: 7].

### D-Eigenvalues and Generalized Eigenvalues
In some applications, such as computational physics and diffusion tensor imaging (DTI), it is necessary to consider generalized eigenvalue problems with respect to a secondary tensor $\mathcal{B}$. A vector $x$ and scalar $\lambda$ form a $\mathcal{B}$-eigenpair if $\mathcal{A}x^{m-1} = \lambda \mathcal{B}x^{m-1}$ [cite: 6]. When $\mathcal{B}$ is a diagonal matrix of vertex degrees, this formulation yields **D-eigenvalues**, which are critical in spectral hypergraph theory [cite: 6, 8].

| Property | Symmetric Matrices ($m=2$) | Symmetric Tensors ($m \ge 3$) |
| :--- | :--- | :--- |
| **Number of Eigenvalues** | Exactly $n$ | $\frac{(m-1)^n-1}{m-2}$ (often exponential) |
| **Field of Eigenvalues** | Strictly Real | Can be Real or Complex |
| **Orthogonality** | Eigenvectors are orthogonal | Eigenvectors are generally not orthogonal |
| **Characteristic Polynomial** | Determinant of $(\mathcal{A} - \lambda I)$ | Multivariate Resultant / Hyperdeterminant |

## 3. The Cartwright-Sturmfels Theorem

For a general matrix of dimension $n$, the fundamental theorem of algebra guarantees exactly $n$ complex eigenvalues, corresponding to the $n$ roots of the characteristic polynomial. For tensors, the dimensionality scales multilinearly, leading to a much larger state space of eigenvectors. 

In 2013, Dustin Cartwright and Bernd Sturmfels published a landmark paper titled "The number of eigenvalues of a tensor," which definitively answered the combinatorial question regarding the number of eigenpairs [cite: 1, 4]. 

### The Formula
Cartwright and Sturmfels proved that for a generic symmetric tensor $\mathcal{A}$ of order $m$ and dimension $n$, the number of equivalence classes of complex eigenpairs is exactly given by the formula:
\[ M(m, n) = \frac{(m-1)^n - 1}{m-2} \]
which can also be written as the geometric series $\sum_{i=0}^{n-1} (m-1)^i$ [cite: 4, 9]. For instance, a symmetric $3 \times 3 \times 3$ tensor ($m=3, n=3$) possesses $M(3, 3) = \frac{2^3 - 1}{1} = 7$ complex eigenpair equivalence classes [cite: 10]. 

### Proof Sketch via Algebraic Geometry
The proof relies heavily on the machinery of algebraic geometry and Bézout's Theorem [cite: 4, 11]. The eigenvalue equation $\mathcal{A}x^{m-1} = \lambda x$ can be homogenized by treating $x$ as a point in the complex projective space $\mathbb{P}^{n-1}$. By substituting $\lambda = \mu^{m-2}$, the equation becomes:
\[ \mathcal{A}x^{m-1} = \mu^{m-2}x \]
This yields $n$ homogeneous equations of degree $m-1$ in the variables $(\mu, x_1, \dots, x_n)$ [cite: 4]. By applying Bézout's Theorem—which states that the number of common zeros of $n$ generic homogeneous polynomials of degrees $d_1, \dots, d_n$ in projective space is the product of their degrees $\prod d_i$—the unconstrained system has $(m-1)^n$ solutions. However, to account for the intrinsic scaling freedom and the singular point at the origin (which contributes a multiplicity of $1/(m-2)$), the equivalence classes are factored out, leaving exactly $\frac{(m-1)^n - 1}{m-2}$ distinct normalized eigenpoints [cite: 4].

### Characteristic Polynomials of Tensors
Cartwright and Sturmfels also expanded upon Qi's definition of the tensor characteristic polynomial [cite: 7, 12]. The characteristic polynomial $\phi_{\mathcal{A}}(\lambda)$ is constructed by eliminating the variables $x_i$ from the ideal generated by the eigenvalue equations and the normalization constraint $x_1^2 + \dots + x_n^2 = 1$ [cite: 4]. Through elimination theory, the intersection of this ideal with the polynomial ring $\mathbb{C}[\mathcal{A}_{i_1\dots i_m}, \lambda]$ yields a principal ideal. If the tensor order $m$ is even, the generator is exactly $\phi_{\mathcal{A}}(\lambda)$; if $m$ is odd, it is generated by $\phi_{\mathcal{A}}(\lambda^2)$ [cite: 4]. The roots of this polynomial precisely correspond to the normalized eigenvalues, though a tensor characteristic polynomial can occasionally vanish identically if the tensor possesses an infinite family of eigenpairs [cite: 4, 7].

## 4. Real Eigenvalues: Existence and Lower Bounds

While the Cartwright-Sturmfels formula accounts for the total number of complex eigenvalues, physical applications usually require **real** eigenvalues. Unlike symmetric matrices, real symmetric tensors of order $m \ge 3$ are not guaranteed to have entirely real spectra; in fact, the majority of generic real symmetric tensors have some eigenpoints in $\mathbb{C}\mathbb{P}^{n-1} \setminus \mathbb{R}\mathbb{P}^{n-1}$ [cite: 1].

### Odd-Order vs. Even-Order Tensors
The existence of real eigenvalues is fundamentally governed by the parity of the tensor's order $m$.
*   **Odd-Order Tensors:** If $m$ is odd (e.g., $m=3, 5$), the sum $(m-1)^n - 1$ is naturally odd. Because complex eigenvalues of real polynomials must appear in conjugate pairs, an odd total number of eigenvalues guarantees the existence of **at least one real eigenvalue** [cite: 3, 4, 9]. 
*   **Even-Order Tensors:** If $m$ is even, the algebraic argument fails, but topological arguments prevail. It is a proven lower bound that any symmetric even-order tensor possesses **at least $n$ real eigenvalues** [cite: 9, 12].

### Ljusternik-Schnirelmann Theory
The proof of the lower bound for even-order tensors relies on **Ljusternik-Schnirelmann (LS) category theory**, a branch of differential topology used in the calculus of variations [cite: 12, 13]. For an even-order symmetric tensor $\mathcal{A}$, finding a Z-eigenvalue is equivalent to finding critical points of the continuous functional $f(x) = \mathcal{A}x^m$ on the unit sphere $\mathbb{S}^{n-1}$ [cite: 6, 12]. 

Because $m$ is even, the functional is an even function: $f(-x) = f(x)$. Consequently, the optimization problem descends from the sphere $\mathbb{S}^{n-1}$ to the real projective space $\mathbb{R}\mathbb{P}^{n-1}$. The Ljusternik-Schnirelmann category of $\mathbb{R}\mathbb{P}^{n-1}$ is exactly $n$. According to the LS principle, any smooth, even functional defined on a manifold of LS category $n$ must possess at least $n$ distinct pairs of antipodal critical points [cite: 12, 13]. Therefore, the tensor $\mathcal{A}$ has at least $n$ real eigenvalues, mirroring the dimension $n$.

## 5. Expected Number of Real Eigenvalues for Random Tensors

Since a symmetric tensor can have up to $\frac{(m-1)^n-1}{m-2}$ real eigenvalues, but mathematically guarantees only 1 (for odd $m$) or $n$ (for even $m$), determining the *average* or *expected* number of real eigenvalues for a random tensor is a central problem in stochastic geometry and random matrix theory. 

### Paul Breiding's Resolution
The definitive breakthrough in this area was achieved by Paul Breiding, who answered an open question posed by Draisma and Horobet [cite: 14, 15]. Breiding established a closed formula for the expected number of real eigenvalues of a random real symmetric tensor drawn from the **Gaussian Orthogonal Ensemble (GOE)** generalized to tensors [cite: 14, 15]. 

To regularize the probability measure, Breiding analyzed tensors distributed according to the **Bombieri norm** (also known as the Kostlan-Shub-Smale norm), which provides an orthogonally invariant probability measure on the space of homogeneous polynomials [cite: 15]. Under this distribution, Breiding demonstrated that the expected number of real Z-eigenvalues is mathematically equivalent to the expected number of real critical points of a Kostlan polynomial on the unit sphere [cite: 15]. His research showed that while the maximum number of real eigenvalues scales exponentially as $O((m-1)^n)$, the expected number of purely real eigenvalues scales much slower, typically on the order of $\sqrt{n}$ for fixed tensor parameters, aligning with extensions of the Wigner semicircle law studied by Gurau [cite: 15, 16].

### Quantum Field Theoretic Approaches
In parallel to algebraic geometry, physicists have utilized **Quantum Field Theory (QFT)** to study random tensors, as tensors arise naturally in models of quantum gravity and glassy systems [cite: 17, 18]. Naoki Sasakura computed the exact analytic distributions of real eigenvectors for Gaussian random tensors utilizing a zero-dimensional quantum field theory [cite: 18, 19]. 

By reformulating the eigenvalue problem into a four-Fermi interaction partition function, Sasakura calculated the *signed distribution* of real tensor eigenvectors [cite: 18, 19]. In this framework, each real tensor eigenvector contributes a weight of $+1$ or $-1$ depending on the sign of the determinant of the associated Hessian matrix at that critical point [cite: 18]. This method successfully derived exact analytic large-$N$ asymptotic forms for the distributions of order-three symmetric random tensors characterized by Lie-group invariances such as $O(N, \mathbb{R})$ and $U(N, \mathbb{C})$ [cite: 18, 19].

## 6. Geometric and Algebraic Perspectives: Eigenconfigurations

The landscape of tensor eigenvectors is structurally rich, forming algebraic varieties known as **eigenconfigurations** and **eigenschemes**. This geometric framing was heavily developed by Hirotachi Abo, Anna Seigal, and Bernd Sturmfels [cite: 10, 11]. 

### The Eigendiscriminant
In classical linear algebra, the eigenvalues of a matrix are degenerate if and only if the discriminant of its characteristic polynomial vanishes. For tensors, Abo, Seigal, and Sturmfels defined the **eigendiscriminant**, a massive, irreducible homogeneous polynomial in the tensor entries $\mathcal{A}_{i_1\dots i_m}$ [cite: 20]. The eigendiscriminant vanishes if and only if the tensor has multiple identical eigenvectors (i.e., when two or more critical points of the gradient map coincide) [cite: 20].

For a symmetric $3 \times 3 \times 3$ tensor, the eigendiscriminant is a polynomial of degree 24 [cite: 20]. In general, the degree of the eigendiscriminant for an order-$m$ dimension-$n$ tensor is strictly given by $n(n - 1)(m - 1)^{n-1}$ [cite: 20]. The geometry of the eigenscheme—defined by the maximal minors of the matrix concatenating the vector $x$ and the contraction $\mathcal{A}x^{m-1}$—provides an advanced tensor analogue to matrix diagonalizability [cite: 10, 11]. Abo et al. proved that there exist fully generic real symmetric tensors whose eigenconfigurations are entirely real; that is, all $\frac{(m-1)^n-1}{m-2}$ eigenvectors exist purely in the real projective space $\mathbb{R}\mathbb{P}^{n-1}$ [cite: 21, 22].

### Cartwright-Sturmfels Ideals
The combinatorial structures discovered by Cartwright and Sturmfels inspired the definition of a new class of objects in commutative algebra: **Cartwright-Sturmfels ideals** [cite: 23, 24]. Conca, De Negri, and Gorla formalized this concept, defining a multigraded ideal in a polynomial ring as a Cartwright-Sturmfels (CS) ideal if it possesses a radical multigraded generic initial ideal [cite: 23, 24, 25]. 

These ideals exhibit remarkable combinatorial robustness. Specifically, a multigraded minimal system of generators of a Cartwright-Sturmfels ideal inherently forms a universal Gröbner basis—a basis that remains valid under any term ordering [cite: 23, 26]. The theoretical framework of CS ideals has been used to recover and extend results regarding binomial edge ideals, multiview ideals in computer vision, and the multigraded homogenizations of linear spaces [cite: 23, 24].

## 7. Computational Approaches and Complexity

Because computing tensor eigenvalues fundamentally equates to solving a system of multi-variate nonlinear polynomial equations, the problem is incredibly computationally demanding. Hillar and Lim formally proved that enumerating all eigenpairs of a general symmetric tensor is **NP-hard** [cite: 3, 9]. 

However, various numerical and algebraic algorithms have been engineered to tackle this optimization problem, prioritizing the extraction of real Z-eigenvalues. 

### Jacobian Semidefinite Relaxations (Lasserre Hierarchy)
Because the largest (or smallest) real Z-eigenvalue can be formulated as a polynomial optimization problem—maximizing $f(x) = \mathcal{A}x^m$ subject to $\|x\|_2^2 = 1$—it is naturally suited for sum-of-squares (SOS) and Semidefinite Programming (SDP) relaxations [cite: 2, 6].

Cui, Dai, and Nie introduced a groundbreaking approach utilizing **Jacobian semidefinite relaxations** to compute *all* real eigenvalues sequentially [cite: 2, 6]. By enforcing the Karush-Kuhn-Tucker (KKT) optimality conditions $x \parallel \nabla f(x)$, their algorithm restricts the feasible set to the variety of critical points $W := \{x \in \mathbb{R}^n \mid \text{rank}[\nabla f(x) \quad x] \le 1\}$ [cite: 2, 6]. 

The method computes the largest eigenvalue $\lambda_1$ by solving a finite hierarchy of SDP relaxations [cite: 2, 6]. To find the next largest eigenvalue $\lambda_2$, the algorithm imposes an additional constraint $f(x) \le \lambda_1 - \epsilon$ to exclude the previously found eigenpoint, and repeats the Lasserre hierarchy. This process sequentially peels away critical values until the entire real spectrum is obtained [cite: 2]. The Jacobian SDP method is mathematically rigorous and globally convergent, although its computational cost scales poorly for very high dimensions due to the size of the necessary SDP matrices.

### Newton-Based Methods and Dynamical Systems
For large-scale applications where SDPs are too memory-intensive, researchers employ heuristic iterative solvers. The **Shifted Symmetric Higher-Order Power Method (S-SHOPM)** is a standard tool. By introducing a shift parameter $\alpha$, S-SHOPM guarantees convergence to a local maximum or minimum of the tensor polynomial, yielding extreme eigenvalues [cite: 5, 11].

Alternatively, Newton Correction Methods (NCM) and Orthogonal Newton Methods provide quadratic convergence to tensor eigenpairs given a suitably close initial guess. Jaffe, Weiss, and Nadler analyzed the landscape of these Newton updates, establishing that for a generic symmetric tensor, multiple random initializations of NCM will traverse the attraction basins of the tensor and find all real eigenpairs significantly faster than algebraic methods, although without deterministic guarantees of completeness [cite: 9]. 

Furthermore, Benson and Gleich framed the search for Z-eigenvectors as the convergence of a continuous-time dynamical system [cite: 3]. By analyzing the map $\frac{dx}{dt} = \Lambda(\mathcal{A}x^{m-2}) - x$, where $\Lambda$ extracts the primary matrix eigenvector of the flattened tensor, they proved that stable fixed points of this spacey random walk correlate precisely to the Z-eigenvectors of the original tensor [cite: 3].

```python
# Conceptual pseudocode for a Tensor Power Method (Z-eigenvalue)
def tensor_power_method(A, max_iter=1000, tol=1e-8):
    # A is a symmetric tensor of order m and dimension n
    x = random_unit_vector(n)
    for i in range(max_iter):
        # Contract tensor A with x along m-1 modes
        Ax_m1 = contract_tensor(A, x) 
        
        # Calculate Rayleigh quotient approximation of eigenvalue
        lambda_approx = dot_product(Ax_m1, x)
        
        # Update and normalize
        x_new = Ax_m1 / norm(Ax_m1, 2)
        
        if norm(x_new - x) < tol:
            return lambda_approx, x_new
        x = x_new
    return lambda_approx, x
```

## 8. Applications in Engineering, Physics, and Data Science

The spectral theory of symmetric tensors is not merely an abstract mathematical curiosity; it is highly applicable across numerous scientific domains. 

*   **Continuum Mechanics and Elasticity:** In solid mechanics, the elasticity tensor is a symmetric fourth-order tensor that defines the stress-strain relationship in anisotropic materials. The strict positive definiteness of this tensor—dictated by the minimum real H-eigenvalue (often termed M-eigenvalue in mechanics)—is fundamentally required to satisfy the strong ellipticity conditions, ensuring material stability [cite: 27, 28].
*   **Diffusion Tensor Imaging (DTI):** In medical imaging, the diffusion of water molecules in brain white matter is traditionally modeled via a 2nd-order diffusion tensor (a matrix). However, to resolve complex crossing nerve fibers, higher-order symmetric tensors (typically 4th or 6th order) are employed. The maxima of the diffusion profile correspond directly to the Z-eigenvectors of these higher-order tensors, allowing neuroscientists to trace intricate neural pathways [cite: 6, 9].
*   **Quantum Information Theory:** In quantum physics, a multipartite pure state can be represented as a complex tensor. The injective tensor norm, which quantifies the geometric measure of quantum entanglement, is mathematically equivalent to computing the maximum real eigenvalue (spectral radius) of the associated symmetric random tensor [cite: 17, 27]. 
*   **Data Science and Hypergraphs:** Traditional graph theory relies on the adjacency matrix to cluster data. However, for multi-way relationships (e.g., co-authorship networks involving three or more people), data is modeled using hypergraphs. The spectral properties of the adjacency tensor of a hypergraph, particularly its Z-eigenvalues and D-eigenvalues, dictate hypergraph partitioning, Markov chain transition probabilities, and higher-order random walks [cite: 3, 6].

## 9. Conclusion

The exploration of tensor eigenvalues reveals a profound mathematical landscape where classical linear algebra intersects with algebraic geometry, topology, and optimization. The Cartwright-Sturmfels theorem anchors the discipline by establishing the finite, combinatorial upper bound of complex eigenpairs as $\frac{(m-1)^n-1}{m-2}$ [cite: 1, 4]. However, translating this algebraic certainty into the real domain introduces heavy topological constraints, guaranteeing at least one real eigenvalue for odd-order tensors and at least $n$ real eigenvalues for even-order tensors via Ljusternik-Schnirelmann category theory [cite: 9, 12].

Significant advances by mathematicians like Paul Breiding have unraveled the statistical distribution of these real eigenvalues in random settings, linking them to Kostlan polynomials and providing a probabilistic baseline for algorithmic expectations [cite: 15]. Despite the NP-hard nature of extracting these values, modern methodologies—ranging from Jacobian semidefinite relaxations to dynamical tensor spacey walks—continue to push the boundaries of computational feasibility [cite: 2, 3]. As the demand for modeling multidimensional, non-linear phenomena accelerates in fields like machine learning, quantum physics, and medical imaging, the Cartwright-Sturmfels framework and the broader study of real symmetric tensor eigenvalues will remain a vital cornerstone of applied computational mathematics.

**Sources:**
1. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtnvqDr9wC2JDj2x8TrnXfQ1mUVLedA3Bhv2j3lOM1_NAA5WodkIeDVV3Jps932FJ5MZR5-mS4s2x6mfjvB3jPtciazp66MUt3Juf47AWeQeTQdKYPioh3Mvkoiw0zSNkDr3ZB5HeQ)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlKRLYsKxMNUyUstluQymBI7D_IKyReAmrt5_V0Qt3ZwZ7kayd6qM8EMyh4BRJMt-85SRctYN7AGNH654g3HcWMmoHIZH-bAYiYB3G2EPpZSsPu64IDzVWXamN26--62tuglnPPNU7N0RlvUYLYLFbA3fe9en9YToz5XVOZrWPaYFh4I_1DoNGJReru6HJLUV6zw==)
3. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5tNROZZ4DUkcGZT5AVEogQXMQBRM_SCQv9H1tneco6NHxby3jYE31Ce1RqiqIeKnWkps_Cq-LZPuGQorbsoPF33BVjO3ZMzIAglZp0JbJE3RhpLtZQr_c9daca_9m-mqgnkPADlaKehs6yBRoaNIhQNcsMHICtzAswaDqS5rhI01F8kWYd5XZE9INbVI0ig3_i7WXuNV7zseWYAGRgeWjI7r1-Ybk8fMPzotP6w==)
4. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu6HphWynmxV7Isp8djv4c7Kc4ryf71CSMv-CrkahjutypTvv1Eb1MHhQkP774eqUHAGe1lk_zwgIHWzQPrF4uKZOklKxoArltHdUvSXR4Gyg505JEd7pOnlApEAghkapeLHbmgNyKhajsNfYYcee1-ZEk-cno9r62Y-BeqkGYa5mPyhc=)
5. [ufl.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGR-CqqO1fLb6AFu_kgKaesiZ1raEYy9lLOjBClKe2sPnnZpZvsEd9q2GzNt9DAT7tFsbps2Tl3tEWaQ-mhTTTfoDOMbJmkzG7awmoaRu3iL40GEdMsioRMofYOtp1hIwdAoE197gXVLOv81b-MP6644_JUTlYZDcA=)
6. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3XGK1ebTp5m3xcHyqzCpz8Nvd1k42g2wQPjwiQOObotbx7bUP7jPU5_b5b1_ap6nsducCtJoOUldUhMLkHiXOjZAXmr0XdHDR0FL-INh6epvZwH-YqbB2jrc1uvRFgTaE6TfQJb7wNunJAimF7-bVDuz2AgDnC6c=)
7. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7BSEsippVhOCzvZpW8euWpURsxPgS_1pwUzPRnhM7mWxaJHAuxkqgfR9fWV3kAJM4rLEdCWWd2nLa_X_jcsBJNHPI6K6r6FnBY-_pGw0IRtK27MAlYLXOhoAbXnn1tkBNQ0DbWsVdsq6QfjpSGT-NORNRX_Z-Jg==)
8. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoXBvT_6k6xzI4eEWJViup5N9pI2MR5peuAQUWLZpuwlFq1DMOMyVq0y0Tuy0KVg9XvqgtJJZd-f1pQA6L5m4WJnx_zmTMM2pRcUyh3CgB5C9Dq0YrQn9WMfnFSVwNEFWiF_M=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsrAxQiFp0OQnoLxgWv-XkFOUOWxs99jxe9Zkzeurr6ULKcFKHg_y6SoUFN2lIauMwXZeUGxL8ip32qp7xNnqMwhHDN3J1IxPvU7nlkH4S7o0H3UQeDQ==)
10. [ucdavis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjUV0qoWC-Q7QVP0trd-dn9IXTsIZJHzmYHFz9YEbIJyKrH1eKtnyuu_qv874T-a1iQgin7_wGFq3zkd1cZ8LCWsZbd_lRAtVepR53fxFRwfpcxOWyJCCN3mGSEL1VHVLCmeerigOHq5A68p2WR-NQrPal1Di4P1XgDIVX68Bl_ZkIZYPeP4szpdsSPhJYjpmtyQ==)
11. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfdhIxWtL0tnOn9a6bQ7eCwr9DHMJA2Cju34x7p1XBAbgLXu0y34cSDmjHYRg8ia_78engJ-S_h0wLUehcPUsJAoer1N_t-pCSzeX4XkkOYMxq4Q754WxD0oukOjVWVVHKJfdZmrMCIp3ImRb9tBdNZW2JrR5OclXWuCSC-syiENcQqGUB96WddhmA6jvcb0RV1GPjdXBIyifJNq9UjfIbZaBl0vkSmgbvvlY=)
12. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1sSE4Foj7oWvl0E6TRIG-lIDLS8HDi_uQik_cY2N_pYOUK_XqDWj0eD98dR4g18sLL3Az0t9Y4xaAy1sQSMlbAWcL7HBGDHg1_lpvXW39cmXj6qeZZy6yKiXMvoGDGo2uGRmqBKNWyBtOzqUv4Fn-w55-PxHFxskPc9OeBhbLmO_zksrmAOYxpk7EizMQ-i6TsnVxi3oCnmbsIU0glVJEq0JhlthdhmYNLzr84SCsUOHP--bkpvsn9NKUiUhuMZ-ZjS_68u31Ahn58wiGPY-y0w==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTD0jBe4t0bpZNo6LibNYJvz1ku4hH6ThISjQ-63cotWBB-t80UM6er3nyu_MMbuau_VhJfh5GV64h-djCt7BQ8MRn2EHm4IGQnHUIQkI36XrpHXd5ow==)
14. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoiLjpZ2Wz7xnjkl3YkjEWUdOBMAHVxHH2i9nqgweYB-wYUj0eKAOeX3b4GENzOotvq8gKjZdvwDkhbAHH3o3mBDIUQW52lDaqH7zdN-ImhIETyNDGA8U9akTsb1fxTH4clG8JMyafZ_WZqEyYxFpsOLHRYCLwcEIwQ8yvYNav62gLTcd6iAV-RzzjCYggyoIgJnbEr9LnkgKEzqtW0Ypg-jIW2GAToz2LJ0krB8MsmykcnWkD17eustRwdLaIIRY=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFForclz5hyc3JapzPwbt-NyHOzdRU1N4IsaVw2QTcwalHB70D6TFSD8otzLQ7ceLdcPjZrwGHV9SFjG4wOQU_I4vGo2RK1IlpsyTHdaLhqP_2vIy2hQw==)
16. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoNVCdilCVpHoJkcJoXOyfJ1HwAGOW9ZIO7_LBv1xpmtd9MJmOLTqc3nWGCl668GAgebhtFzR_rxW5Gdyb4OJuIrtPBOEV0sIPSlPss-EqxtxvQefckBNSWV41zodVItpeYQLaJaE67STLDarHwuTmXuXVRQ_6DwobDLR3ozIPtu_fOPPUUEZDacPtb2I=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmIOWuyHlte5oqnMUH0yNLBXy0_vUxslDjGBGejDobnbe1Jb1tJvWcx5sjVlkwNLLGSY5E2vHKifII9HAKRfxuEqCzGW7fBJ-8wITUODhlAobtdChMv02NzX-DY0UDEfflcYfl30pCgBtKsGX_qgUwGYxYpH-KvnJBQyCbpSavKw8upZFuYHGmo1xz0uB2smE4q1M9n858j7ENYEAVFJvCLAirJ31Ine4HJ3h-rPQlIu0TtiN8_HSxfn3HzIsArH1lLXNr4kZIRnQ=)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHK26nDI1i5ECZRIyDsUU0AlOUBOYBzOqXsumkpBouqBS9skBYakmZEm_M3mGbDDRcUnIlWKN_zW_S1lreXhA_dJkL5uJlb-X6rRvbDmSk6z2hrQYJZ0WtuYd6XuZmTtWGRuA0oy5WljT3KtoTV5SsXg1z9tZZo65ZAXSSzmu9virBf3btZ9HFQpBj9QU-C6Vx-5hjz_80qFaIKNk4oYWqyHaOUBn4DCyUft-HoGzU=)
19. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENf4RlmqCQ1LncMvA6djpGAP2sne9KFxqgWO_gE-0b9W_0nSxTAHCMYmFSfcpdNEihSNmjil3cvFs_AGAM7otbBzSetuB1VuYQlkJRhiBbPouV-UurOnsOSfGeQmMsCiTqInWJE2SPwpuCWMbI66wKv7Iyn7vG5Hrh_POjKELj1a5HxGcWO1p7jevDkUsAS4nQu6s-ekvlKOh_g6e6OqELHVS5Wi7GB4-8WTMhbraRWIEHPna55s7FAM9eejDfEH7zxg==)
20. [uni-konstanz.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy7lDXnSsO5Uk6bAIyQvbpAmgqr-ImCUQ8xJniwqBLUjTW2J8j7to2IS0UBUeeKMA4VOGx4Hko6aXQ3kYVz75RDiae_4e-B03TVR5q6t3-WBkWynDa_SlgZhqUCP70so_8Jg-ymT_1ruE=)
21. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTWIA_s0GkUGdeKCEybZhj5NMxeMyXbEZOu6P4rGsjVIhAHrS-Z-oQyuOrbDjAHqM2N-IsksEft_utRsoDl85F3dMJBg1Ed6WGqPcjJtfKN7Dp704_FvcqK70AHG9H9EsYuJc=)
22. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMtmR9fkUOEIC8IKfvC7ia0LCg59GdLH9M_Frv1WI0ejooUGM9k5KOmotVLOzahJuRN4_lasDW_Pd5ymTseKuLDYOJYCnLSQtdOsWJJIZDsP35n8WityNKhy2zp0ygDV3mYVrVbebQ65BPmas4RAdtLImfzk2JVY-LM3y5qrGQdWw-qDeyT_Vn13odFcI2EOP7GTbZH-9Ri-FZETrDFXd3WguAgqWYWxH1pS8lTIs=)
23. [cineca.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1suBHarP3TOiwQqkWfOgmC18mQFxQ-80vQaHiRDXAuEXs80hR73NG0J80QXLlTIEn8kIBwbQD-d30IPH1sPDj2__K1wUTvk8SR0t6B-eOA6V6Z05ztTcoC644hhG2KIDdReBtvrT8Cig3yvFoXc_tS95juQyNPA-l7fVeMoGqCFBP9TnC1WkR88VEUS-Bo3luU5oSRi0DVxQ=)
24. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgPXXGyV-xyBblyTj9lE0O9pcFEwx_zF1MBzbOnCBUPxGsyfUlNTLnalejxBBRnux1A7WejNMugu3iMzRLGYnA5s3hdpgqFG4hixB-mctTuPj1_HkzBgXkIbXfXs1CgaoEqoIal_ykqesS)
25. [utah.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjNiNbCUau3KzkAyiTDeq92a5h_xMZy7qUZceZhbHTlIfc-rXmkldv7tR3dNRefoyvtKgwIq8SUZsbxoe8Ha0pff1nIxu-I-q_SbKFhpjV_h0H_ddRfJ0UwE9T2qe4-8r6Qbe9)
26. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVsJFHLmn9MN3hiDXwB0OfKtKmx9-bw_AK2HQD3v_CRpxY_2ZbKh_L3M_OFqT7STOHI0p-L1GlJ3tsmpUjNlXraVDxwPBKBtFwayUibwFST1Ws3q4E9njFcNtRCYqzLsTcURcr_sd7Mgs45AW7UGA=)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdSUv3aO7jtiKABFMA6uxmZXgsTfutaHHI0caT0OlGPEXgSQRHtoC7L6h0SskY-aOFhumwnCQnWrnr0MYcLwbBSAUx4DWG8XVUJbqcSofM4qrIIJQB9-jURFr0-ahFoPcGBN8H0obVe1pj1UlBv9MK-B37NcGUK8f2O8RAHS1kEnzfQBRMebw2bA7D3CA=)
28. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFereT8zNnC5gdf5oaymcD3HVOG4WTINjYE6MYxAQjqimqMuPJoSZjuk-cSW9UZOkWAaZPamBrPjIb6nXUgg4XM1ooO5q4xzDBFZpxJjf_jgL7bzbzX3BvC1x1zSGYZ3n1DY-aNrIscmm19i5RW4J6xkxk=)


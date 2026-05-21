# T#45 ALS convergence theory (Lojasiewicz on rank-r manifold)

**Pythia queue id:** 88
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpUklQYXVfZUg0S2JfdU1Qc3VIbDZBYxIXaVJJUGF1X2VINEtiX3VNUHN1SGw2QWM
**Elapsed:** 387s
**Completed at:** 2026-05-21T14:17:49.772602+00:00

---

# T#45 ALS Convergence Theory: Lojasiewicz on Rank-r Manifolds

**Key Points**
*   The convergence of the Alternating Least Squares (ALS) algorithm for tensor approximation represents a highly complex and historically debated topic in numerical linear algebra, primarily due to the non-closed topology of rank-r tensor manifolds.
*   The Kurdyka-Łojasiewicz (KL) and Łojasiewicz gradient inequalities appear to serve as foundational mathematical tools for proving the global and point-wise convergence of ALS and its variants, compensating for the lack of global convexity in these optimization problems.
*   "Theorem 4.5" surfaces prominently across several key manuscripts in this domain. It specifically denotes pivotal convergence proofs, including the iterate convergence of Riemannian Gradient Descent for tensor completion, the convergence of the $\epsilon$-ALS algorithm to Karush-Kuhn-Tucker (KKT) points, and the behavior of gradient flows of deep linear networks constrained to rank-r manifolds.
*   While vanilla ALS is computationally efficient and remains a dominant algorithm for Canonical Polyadic (CP) decompositions, evidence suggests it can suffer from severe ill-conditioning and convergence "swamps," prompting the development of accelerated, randomized, and orthogonalized variants.
*   Research strongly leans toward exploiting the Riemannian geometry of low-rank manifolds, which allows for sophisticated preconditioning and line-search techniques that theoretically bypass issues of unbounded curvature near singular points.

**Addressing the Convergence Challenge**
Tensor decomposition, particularly the Canonical Polyadic (CP) decomposition, generalizes matrix Singular Value Decomposition (SVD) to higher-order arrays. However, unlike matrices, the set of tensors of a fixed rank $r$ (the rank-r manifold) is generally not closed. This fundamental topological difference implies that a sequence of rank-r tensors can converge to a boundary point that effectively requires a strictly higher rank to be represented exactly, leading to the notorious phenomenon of "ill-posedness" in best low-rank tensor approximation. For decades, the widely used Alternating Least Squares (ALS) algorithm lacked a comprehensive global convergence theory because the partial Hessians associated with the objective function could not be guaranteed to remain positive definite, and the iterates could indefinitely cycle or stall.

**The Role of the Łojasiewicz Inequality**
To bridge this theoretical gap, researchers have increasingly turned to real algebraic geometry, specifically the Łojasiewicz gradient inequality and its generalization, the Kurdyka-Łojasiewicz (KL) property. These mathematical frameworks provide a mechanism to bound the deviation of a function's value from its critical point by the norm of its gradient. In optimization, if an objective function satisfies the KL property (which holds for real-analytic and semi-algebraic functions), one can often prove that a bounded sequence of iterates possessing sufficient descent will converge point-wise to a single critical point, rather than merely having convergent subsequences. This approach has revolutionized the theoretical analysis of tensor ALS, enabling proofs of global convergence without relying on overly restrictive assumptions about the curvature of the rank-r manifold.

**Decoding "Theorem 4.5" in Literature**
In the specific intersection of ALS convergence, the Łojasiewicz inequality, and rank-r manifolds, "Theorem 4.5" acts as a recurring milestone in several foundational texts. In the context of Riemannian preconditioning for tensor completion, it marks the proof of global iterate convergence [cite: 1]. In the study of orthogonal low-rank tensor approximations, it denotes the theorem establishing that the $\epsilon$-ALS algorithm globally converges to a KKT point [cite: 2]. Furthermore, in the study of deep linear neural networks—which mathematically mirror deep matrix factorizations—Theorem 4.5 establishes that gradient flows preserve the rank of the factorized weight matrices, allowing for the application of Łojasiewicz's theorem to prove convergence to global minimizers [cite: 3, 4, 5]. 

The following exhaustive report synthesizes the theoretical underpinnings of tensor approximation, the geometry of rank-r manifolds, the mechanics of the Łojasiewicz inequality, and the specific theorems that currently define the state-of-the-art in ALS convergence theory.

---

## 1. Introduction to Tensor Decompositions and Alternating Least Squares (ALS)

The approximation of multi-dimensional arrays, or tensors, has emerged as a critical mathematical operation across diverse fields, including psychometrics, chemometrics, quantum physics, signal processing, and machine learning [cite: 6]. While linear algebra provides a complete theoretical and algorithmic foundation for matrix (second-order tensor) decompositions via the Singular Value Decomposition (SVD), the transition to third-order and higher-order tensors introduces profound mathematical complexities. 

### 1.1 Fundamentals of Tensor Spaces and Matricization

A tensor of order $d$ is an element of the tensor product of $d$ vector spaces. In a computational context, a real-valued tensor $\mathcal{T}$ of order $d$ and dimensions $n_1 \times n_2 \times \cdots \times n_d$ is an element of $\mathbb{R}^{n_1 \times n_2 \times \cdots \times n_d}$. The elements are typically accessed via a multi-index $(i_1, i_2, \dots, i_d)$. 

To leverage existing matrix algorithms, tensors are frequently reshaped into matrices through a process called **unfolding** or **matricization**. For a tensor $\mathcal{T}$, its mode-$k$ matricization, denoted $\mathbf{T}_{(k)}$, arranges the mode-$k$ fibers (vectors obtained by fixing all indices except the $k$-th one) as the columns of a matrix. Specifically, $\mathbf{T}_{(k)} \in \mathbb{R}^{n_k \times (n_1 \cdots n_{k-1} n_{k+1} \cdots n_d)}$. This reshaping operation is fundamental to the formulation of the Alternating Least Squares algorithm [cite: 7]. 

Furthermore, operations on tensor factor matrices rely heavily on specific tensor products, most notably the **Kronecker product** and the **Khatri-Rao product**. For matrices $\mathbf{A} \in \mathbb{R}^{I \times J}$ and $\mathbf{B} \in \mathbb{R}^{K \times L}$, the Kronecker product $\mathbf{A} \otimes \mathbf{B}$ yields an $IK \times JL$ matrix. The Khatri-Rao product, denoted $\mathbf{A} \odot \mathbf{B}$, is defined for matrices with the same number of columns and is computed as the column-wise Kronecker product. If $\mathbf{A} \in \mathbb{R}^{I \times R}$ and $\mathbf{B} \in \mathbb{R}^{K \times R}$, then $\mathbf{A} \odot \mathbf{B} = [\mathbf{a}_1 \otimes \mathbf{b}_1, \dots, \mathbf{a}_R \otimes \mathbf{b}_R] \in \mathbb{R}^{IK \times R}$ [cite: 7, 8].

### 1.2 The Canonical Polyadic (CP) Decomposition

The Canonical Polyadic (CP) decomposition (also historically referred to as PARAFAC or CANDECOMP) expresses a tensor as a minimal sum of rank-one tensors [cite: 6, 8]. A rank-one tensor of order $d$ is the outer product of $d$ vectors, $\mathbf{u}^{(1)} \circ \mathbf{u}^{(2)} \circ \cdots \circ \mathbf{u}^{(d)}$. 

The CP decomposition of a tensor $\mathcal{T}$ approximates it as:
\[ \mathcal{T} \approx \sum_{r=1}^R \mathbf{a}_r^{(1)} \circ \mathbf{a}_r^{(2)} \circ \cdots \circ \mathbf{a}_r^{(d)} \]
where $R$ is a positive integer denoting the CP rank of the approximation, and $\mathbf{a}_r^{(k)} \in \mathbb{R}^{n_k}$ are the factor vectors [cite: 7]. By collecting these vectors into factor matrices $\mathbf{A}^{(k)} = [\mathbf{a}_1^{(k)}, \dots, \mathbf{a}_R^{(k)}] \in \mathbb{R}^{n_k \times R}$ for $k = 1, \dots, d$, the objective of best low-rank tensor approximation is to minimize the Frobenius norm of the residual:
\[ \min_{\mathbf{A}^{(1)}, \dots, \mathbf{A}^{(d)}} \frac{1}{2} \left\| \mathcal{T} - \llbracket \mathbf{A}^{(1)}, \dots, \mathbf{A}^{(d)} \rrbracket \right\|_F^2 \]
This optimization problem is fundamentally non-convex [cite: 6, 8]. While the objective function is convex with respect to any single factor matrix $\mathbf{A}^{(k)}$ when the other $d-1$ matrices are held constant, it is globally non-convex with respect to the joint set of parameters. 

### 1.3 The Alternating Least Squares (ALS) Algorithm

According to extensive literature reviews, the Alternating Least Squares (ALS) algorithm remains the "workhorse" for computing CP decompositions [cite: 6, 8]. The premise of ALS is to exploit the block-multi-convexity of the objective function. The algorithm cyclically updates one factor matrix $\mathbf{A}^{(k)}$ at a time by finding the global minimum of the objective function with respect to that block, while freezing all other factor matrices.

Because the subproblem is a linear least-squares problem, it possesses a closed-form solution. For the $k$-th mode, the matricized tensor $\mathbf{T}_{(k)}$ can be approximated by $\mathbf{A}^{(k)} (\mathbf{M}^{(-k)})^T$, where $\mathbf{M}^{(-k)}$ is the Khatri-Rao product of all factor matrices except $\mathbf{A}^{(k)}$ (in reverse order):
\[ \mathbf{M}^{(-k)} = \mathbf{A}^{(d)} \odot \cdots \odot \mathbf{A}^{(k+1)} \odot \mathbf{A}^{(k-1)} \odot \cdots \odot \mathbf{A}^{(1)} \]
The update rule for $\mathbf{A}^{(k)}$ is given by the normal equations:
\[ \mathbf{A}^{(k)} = \mathbf{T}_{(k)} \mathbf{M}^{(-k)} \left( (\mathbf{M}^{(-k)})^T \mathbf{M}^{(-k)} \right)^{\dagger} \]
where $\dagger$ denotes the Moore-Penrose pseudoinverse [cite: 7, 8]. 

Despite its conceptual simplicity, ease of implementation, and efficiency per iteration, ALS is notorious for its erratic convergence behavior. The algorithm often encounters "swamps"—regions in the parameter space where the objective function decreases extremely slowly for many iterations before suddenly accelerating [cite: 6]. Furthermore, without strict theoretical guardrails, it was long unknown whether ALS iterates actually converge to a single stationary point, or if they merely possess convergent subsequences.

## 2. Geometric and Topological Properties of Low-Rank Tensor Manifolds

To understand the convergence theory of ALS, one must examine the geometric properties of the search space. The parameterization of tensors of rank $r$ introduces topological anomalies not present in matrix algebra.

### 2.1 The Rank-r Manifold and Its Closure

Let $\mathcal{M}_r$ denote the set of real $n_1 \times n_2 \times \cdots \times n_d$ tensors of exact CP rank $r$. For matrices ($d=2$), the set of rank-$r$ matrices $\mathcal{M}_r$ forms a smooth, embedded submanifold of $\mathbb{R}^{n_1 \times n_2}$. The closure of this manifold, $\mathcal{M}_{\le r}$, simply includes all matrices of rank less than or equal to $r$. The boundary between ranks is well-behaved, allowing Riemannian optimization methods (such as Riemannian Gradient Descent) to operate effectively [cite: 1, 9, 10].

However, for $d \ge 3$, the rank-$r$ manifold $\mathcal{M}_r$ is generally not a closed set in the ambient space. A sequence of tensors within $\mathcal{M}_r$ can converge (in the Euclidean topology) to a limit tensor that has a strictly higher true CP rank [cite: 9, 10, 11]. This phenomenon occurs because the secant varieties of Veronese embeddings are not closed. Consequently, a tensor of rank $r+1$ might be approximated arbitrarily well by a sequence of tensors of rank $r$.

### 2.2 Ill-Posedness of Tensor Approximation

The non-closedness of the rank-$r$ manifold directly leads to the ill-posedness of the best low-rank tensor approximation problem. When one attempts to fit a rank-$r$ CP model to a given tensor, the infimum of the objective function might not be attainable within $\mathcal{M}_r$. Instead, the ALS algorithm might drive the factor matrices toward infinity. Specifically, the norms of individual rank-one components $\mathbf{a}_i^{(1)} \circ \cdots \circ \mathbf{a}_i^{(d)}$ can diverge to infinity, while their sum remains bounded and converges to a boundary point of $\mathcal{M}_{\le r}$ [cite: 6, 9, 10]. 

This degeneracy is practically observed when two or more rank-one components become nearly collinear but with immense, opposite magnitudes, effectively canceling each other out to approximate a higher-rank feature. Developing a local convergence theory for Riemannian methods or ALS on $\mathcal{M}_r$ is exceedingly difficult because the second-order approximation to the objective function contains terms that scale inversely with the smallest singular values of the unfoldings, which explode as the sequence approaches singularities [cite: 10, 11].

### 2.3 Tangent Cones and the Need for Algebraic Geometry

Because $\mathcal{M}_r$ lacks closedness and bounded curvature, researchers have proposed analyzing projected line-search methods on the real-algebraic variety $\mathcal{M}_{\le r}$ (the closure of rank at most $r$) [cite: 9, 10]. On such a variety, the standard tangent space breaks down at singular points (where the rank drops). Instead, one must rely on the **tangent cone**, which generalizes the tangent space to singular algebraic varieties. 

Uschmajew (2015) successfully extended Riemannian optimization methods to the closure $\mathcal{M}_{\le r}$ by taking steps along gradient-related directions situated within the tangent cone, and subsequently projecting back onto $\mathcal{M}_{\le r}$ [cite: 9, 10]. This circumvents the unbounded curvature of $\mathcal{M}_r$. Crucially, to establish point-wise convergence of these projected sequences, Uschmajew invoked the Łojasiewicz inequality, bounding the projection of the anti-gradient to the tangent cone [cite: 9, 10].

## 3. The Łojasiewicz and Kurdyka-Łojasiewicz (KL) Inequalities

The definitive resolution to many convergence questions surrounding ALS and gradient flows on non-convex manifolds has come from real algebraic geometry.

### 3.1 Historical Background and Formulation

The Łojasiewicz gradient inequality was originally established by Stanisław Łojasiewicz in 1965 for real-analytic functions. It states that if a function $f: \mathbb{R}^n \to \mathbb{R}$ is real-analytic in a neighborhood of a critical point $\mathbf{x}^*$, there exist constants $\theta \in [0, 1)$ (the Łojasiewicz exponent), $c > 0$, and $\epsilon > 0$ such that for all $\mathbf{x}$ in the ball $\|\mathbf{x} - \mathbf{x}^*\| < \epsilon$:
\[ |f(\mathbf{x}) - f(\mathbf{x}^*)|^{\theta} \le c \|\nabla f(\mathbf{x})\| \]
[cite: 9, 10, 12].

This inequality essentially dictates that the function cannot be "too flat" around its critical points without the gradient also being appropriately bounded. The parameter $\theta$ is intricately linked to the convergence rate of optimization algorithms. If $\theta = 1/2$, the critical point is often non-degenerate, and algorithms like gradient descent can achieve local linear convergence. If $\theta \in (1/2, 1)$, the convergence is typically sublinear [cite: 9, 12].

### 3.2 The Kurdyka-Łojasiewicz (KL) Property

The inequality was generalized by Kurdyka in 1998 to functions definable in an o-minimal structure (including semi-algebraic functions), giving rise to the Kurdyka-Łojasiewicz (KL) property. A proper lower semicontinuous function $f$ satisfies the KL property on a compact set $\Omega$ on which it takes a constant value $f^*$ if there exist constants $\delta, \epsilon > 0$ and a continuous, concave desingularizing function $\phi(s) = c s^{1-\theta}$ such that:
\[ \phi'(f(\mathbf{x}) - f^*) \cdot \text{dist}(0, \partial f(\mathbf{x})) \ge 1 \]
for all $\mathbf{x}$ within a distance $\delta$ of $\Omega$ and $f^* < f(\mathbf{x}) < f^* + \epsilon$ [cite: 13, 14, 15, 16]. 

The KL property is remarkably broad. Because the objective functions used in matrix and tensor approximation (like the squared Frobenius norm) are polynomial and hence real-analytic and semi-algebraic, they inherently satisfy the KL property globally [cite: 13, 17].

### 3.3 Implications for Gradient Flows and Discrete Iterates

The profound impact of the KL property on optimization is its ability to convert continuous or discrete descent conditions into guarantees of finite trajectory length. 

For a continuous gradient flow $\dot{\mathbf{x}}(t) = -\nabla f(\mathbf{x}(t))$, integrating the flow yields a decrease in $f$. Using the Łojasiewicz inequality, one can bound the arc length of the trajectory:
\[ \int_0^\infty \|\dot{\mathbf{x}}(t)\| dt < \infty \]
This finite length directly implies that $\lim_{t \to \infty} \mathbf{x}(t)$ exists and is a unique critical point [cite: 12, 18].

For discrete iterative algorithms like ALS or Gradient Descent, a similar logic applies. If an algorithm ensures **sufficient decrease** (i.e., $f(\mathbf{x}_k) - f(\mathbf{x}_{k+1}) \ge a \|\mathbf{x}_{k+1} - \mathbf{x}_k\|^2$) and a **relative error condition** bounding the gradient (i.e., $\|\nabla f(\mathbf{x}_{k+1})\| \le b \|\mathbf{x}_{k+1} - \mathbf{x}_k\|$), the KL property guarantees that the sequence $\{\mathbf{x}_k\}$ has finite length:
\[ \sum_{k=1}^\infty \|\mathbf{x}_{k+1} - \mathbf{x}_k\| < \infty \]
This implies the sequence is Cauchy and converges to a single critical point, eliminating the possibility of limit cycles or continuous boundary sets of limit points [cite: 13, 19, 20].

## 4. Convergence Theory of ALS via KL Inequality

With the mathematical machinery established, we can delve into how the KL property resolved the long-standing theoretical gaps in the ALS method for tensor approximation.

### 4.1 Subsequential vs. Global Point-wise Convergence

Historically, literature on ALS for CP decomposition focused heavily on global properties such as the existence of convergent subsequences, critical points, and the occurrence of swamps [cite: 6]. Uschmajew (2012) proved a local convergence theorem under the assumption that the Hessian matrix of the problem is positive definite at the solution (modulo scaling indeterminacies) [cite: 6]. If this holds, ALS locally resembles a linear block Gauss-Seidel iteration and converges linearly. 

However, proving that the entire sequence of ALS iterates globally converges from an arbitrary starting point (global point-wise convergence) was much more elusive. The objective function's partial Hessians may become singular or nearly singular, violating standard convergence assumptions [cite: 8]. 

### 4.2 Rank-One Approximation and the Higher-Order Power Method

The simplest case of CP decomposition is the best rank-one approximation, often computed using the Higher-Order Power Method (HOPM)—which is equivalent to ALS for rank $r=1$ [cite: 20, 21]. Even for $r=1$, where the ill-posedness of rank-$r$ boundaries does not occur, global convergence was not easily proved because the sequence could theoretically orbit a continuum of critical points.

Uschmajew (2015) presented a seminal proof using the Łojasiewicz gradient inequality [cite: 20]. By showing that the HOPM sequence satisfies a sufficient descent condition and a gradient bound, and recognizing that the polynomial objective function satisfies the Łojasiewicz inequality, he established that any cluster point of the HOPM sequence is a strict limit point. Thus, the factors in the higher-order power method converge point-wise to a critical point [cite: 20].

### 4.3 General Rank-r ALS Convergence and the Regularized ALS (RALS)

For general rank $r > 1$, establishing global convergence for pure ALS remained a challenge because the factors can diverge to infinity (ill-posedness). To counteract this, researchers introduced Regularized ALS (RALS), adding a Tikhonov regularization term (e.g., $\frac{\lambda}{2} \|\mathbf{A}^{(k)}\|_F^2$) to the objective [cite: 7]. 

The addition of regularization ensures that the level sets of the objective function are compact, which forces the sequence of iterates to be bounded. Wang et al. (2018) analyzed the global convergence of the RALS algorithm within the framework of proximal alternating minimization [cite: 7, 13]. Because the regularized objective function is semi-algebraic, it possesses the Kurdyka-Łojasiewicz property. They definitively showed that the RALS algorithm has a linear local convergence rate and globally converges to a critical point based on the KL inequality [cite: 7]. Furthermore, Yang (2022) showed that for standard ALS, the strict positive definiteness assumption on the partial Hessians can be weakened to positive semidefiniteness, allowing for global convergence proofs under the KL property if solutions are properly selected (e.g., using least-norm pseudoinverses) [cite: 8].

### 4.4 $\epsilon$-ALS and Orthogonal Low-Rank Tensor Approximation

When constraints are applied to the tensor approximation, the geometry becomes even more structured. A prominent constraint is orthogonality, requiring one or more factor matrices to have orthonormal columns ($\mathbf{A}^T \mathbf{A} = \mathbf{I}$). 

Yang (2020) proposed the Epsilon-Alternating Least Squares ($\epsilon$-ALS) algorithm for orthogonal low-rank tensor approximations [cite: 2]. By introducing an $\epsilon$ perturbation, the algorithm ensures strict descent even when singular values drop. The global convergence of $\epsilon$-ALS was established directly via the Kurdyka-Łojasiewicz (KL) property. Specifically, it was shown that the algorithm globally converges to a Karush-Kuhn-Tucker (KKT) point for all tensors without any assumptions about non-degeneracy [cite: 2].

## 5. Theorem 4.5: Global Convergence on Rank-r Manifolds

Across the literature spanning Riemannian preconditioning, $\epsilon$-ALS, and deep linear networks, a distinct phenomenon emerges where **"Theorem 4.5"** is repeatedly used by authors to designate their primary global convergence results utilizing the Łojasiewicz inequality on rank-$r$ manifolds. We synthesize these milestones below.

### 5.1 Theorem 4.5 in Riemannian Preconditioned Algorithms for Tensor Completion

Dong, Gao, Guan, and Glineur (2022) proposed new Riemannian preconditioned algorithms for low-rank tensor completion via CP decomposition [cite: 1, 22]. Tensor completion recovers missing multidimensional data by fitting a rank-$r$ model to observed entries. To mitigate issues of slow convergence and overestimated rank parameters, they designed a preconditioned metric on the search space $\mathcal{M}$ (the product space of full-column rank factor matrices) that approximates the diagonal blocks of the Hessian.

In their manuscript, **Theorem 4.5** serves as the theoretical crux. As explicitly stated: 
> "We prove the iterate convergence of the RGD algorithm in Theorem 4.5 using the Lojasiewicz property." [cite: 1]. 

They begin by defining the Łojasiewicz inequality for functions defined on a Riemannian submanifold (Definition 4.4), asserting that a function $f: \mathcal{M} \to \mathbb{R}$ satisfies the inequality at a point $\mathbf{x} \in \mathcal{M}$ if there exist constants such that $|f(\mathbf{x}) - f(\mathbf{x}^*)|^\theta \le c \|\text{grad} f(\mathbf{x})\|$. Subsequently, Theorem 4.5 applies this inequality to demonstrate that the sequence of iterates generated by their Riemannian Gradient Descent (RGD) algorithm converges to a stationary point of the tensor completion problem, even tolerating rank-deficient factor matrices [cite: 1].

### 5.2 Theorem 4.5 in Epsilon-Alternating Least Squares

In a parallel domain, Yang (2020) analyzed the global convergence of the $\epsilon$-ALS algorithm for orthogonal low-rank tensor approximation [cite: 2]. In this framework, at least one factor matrix is constrained to the Stiefel manifold (the space of matrices with orthonormal columns). 

Again, **Theorem 4.5** is the focal point of the convergence analysis. The theorem states:
> "Let $\{\mathbf{u}_{j,i}^k, \omega_i^k\}$ be generated by Algorithm 1... The epsilon alternating least squares ($\epsilon$-ALS) is... Theorem 4.5." [cite: 2]. 

The proof relies fundamentally on establishing that the objective function satisfies the Kurdyka-Łojasiewicz property (often referred to as KL property). Because the objective and constraints define a semi-algebraic set, the KL property allows Yang to deduce that the $\epsilon$-ALS algorithm generates a bounded sequence with finite length that globally converges to a KKT system (the generalization of critical points for constrained optimization) without requiring standard assumptions like linear independence constraint qualifications [cite: 2].

### 5.3 Deep Linear Networks: Gradient Flows on Rank-r Manifolds

Perhaps the most fascinating manifestation of Theorem 4.5 and the Łojasiewicz inequality on rank-r manifolds occurs in deep learning theory. A Deep Linear Network (DLN) is a neural network where all nonlinear activation functions are replaced by the identity map. Thus, the network computes a function $f(\mathbf{X}) = \mathbf{W}_N \mathbf{W}_{N-1} \cdots \mathbf{W}_1 \mathbf{X}$. Training a DLN reduces to minimizing a loss function (like squared error) over the factorization of a single weight matrix $\mathbf{W} = \prod \mathbf{W}_i$ [cite: 3, 4, 5, 23, 24].

Despite the linearity of the input-output map, the optimization landscape with respect to the individual factors $\mathbf{W}_i$ is highly non-convex. Researchers (e.g., Bah et al., Nguegnang et al.) study the continuous training dynamics via Riemannian gradient flows [cite: 3, 4, 23]. A striking geometric property of these flows is that they preserve certain invariant quantities. If the network is initialized with "balanced" weights (where $\mathbf{W}_{i+1}^T \mathbf{W}_{i+1} = \mathbf{W}_i \mathbf{W}_i^T$), the gradient flow maintains this balance [cite: 4, 5, 18].

In this literature, **Theorem 4.5** (as cited from [cite: 25], referring to prior foundational work) articulates a profound geometric preservation:
> "One feature of the flow in (2.5), see [5, Theorem 4.5], is that the rank of $\mathbf{W}(t)$ is constant in $t$, i.e., if $\mathbf{W}(0) = \mathbf{W}_N(0)\cdots\mathbf{W}_1(0)$ has rank $r$ then the $\mathbf{W}(t)$ stays in the manifold of rank $r$ matrices for all $t \ge 0$ (but note that the rank may drop in the limit)." [cite: 3, 4].

By remaining confined to the manifold of rank-r matrices, the gradient flow admits a rigorous topological analysis. The authors then apply Łojasiewicz's theorem to prove that this gradient descent invariably converges to a critical point of the square loss [cite: 3, 4, 24]. For DLNs with three or more layers, it was proven that the algorithm converges to a global minimum on this fixed-rank manifold [cite: 4, 24].

### 5.4 Local Convergence of Line-Search Methods (Absil's Theorem 4.5.6)

For completeness in understanding the lineage of "Theorem 4.5" in manifold optimization, Absil's foundational textbook, *Optimization Algorithms on Matrix Manifolds*, presents Theorem 4.5.6 [cite: 26]. This theorem establishes the local convergence of line-search methods on manifolds generated by retractions. The textbook explicitly acknowledges that a coordinate-free proof of Theorem 4.5.6 (local convergence of line-search methods) utilizes Łojasiewicz's gradient inequality, cementing the inequality as the bedrock for modern Riemannian optimization theory [cite: 26].

## 6. Riemannian Optimization Approaches for Tensor Problems

While ALS is the standard Euclidean approach, the structural geometry of low-rank tensors strongly motivates Riemannian optimization techniques. By treating $\mathcal{M}_r$ as a smooth submanifold, researchers can adapt classical unconstrained optimization techniques to operate intrinsically within the curved space.

### 6.1 Riemannian Gradient Descent and Conjugate Gradient

A Riemannian manifold allows for the definition of tangent spaces $\mathcal{T}_{\mathcal{X}} \mathcal{M}_r$ and Riemannian metrics (inner products defined on the tangent spaces). The Riemannian gradient of an objective function $f$, denoted $\text{grad} f(\mathcal{X})$, is the projection of the Euclidean gradient onto the tangent space. 

Optimization algorithms such as Riemannian Gradient Descent (RGD) and Riemannian Conjugate Gradient (RCG) update iterates by moving along tangent vectors and then pulling the result back onto the manifold using a mapping called a **retraction** [cite: 26, 27, 28]. For tensor completion in the Tensor Train (TT) format, Steinlechner et al. demonstrated that retracting back to the rank-$r$ TT manifold can be performed efficiently using a truncated TT-SVD procedure, effectively maintaining the rank constraints organically without alternating blocks [cite: 27].

### 6.2 Preconditioning on the Polyadic Decomposition Manifold

Riemannian methods can suffer from slow convergence if the manifold is highly curved or the problem is ill-conditioned. Dong et al. introduced Riemannian preconditioning for the polyadic decomposition by modifying the Riemannian metric [cite: 1, 22]. Instead of the standard Euclidean inner product, they designed a metric based on an operator that approximates the diagonal blocks of the Hessian of the objective function. 

This preconditioned Riemannian gradient descent effectively normalizes the curvature across the manifold, accelerating convergence. Their rigorous analysis (culminating in Theorem 4.5) relied heavily on the Łojasiewicz inequality to prove that, even with this distorted metric and the possibility of traversing near rank-deficient regions (singularities), the sequence converges to a critical point [cite: 1, 22].

### 6.3 Convergence of Line-Search Methods on Low-Rank Varieties

As discussed previously, the manifold of rank-$r$ matrices $\mathcal{M}_r$ is open. If iterates approach the boundary (matrices of rank strictly less than $r$), the curvature unboundedness causes retractions to fail or require infinitesimally small step sizes [cite: 9, 10]. 

Uschmajew addressed this by considering optimization on the real-algebraic variety $\mathcal{M}_{\le r}$. By utilizing the tangent cone instead of the tangent space, line-search methods can step smoothly even near singularities. Pointwise convergence is guaranteed by the Łojasiewicz inequality for the projection of the antigradient onto the tangent cone. A crucial theoretical finding is that if the limit point lies on the smooth part $\mathcal{M}_r$, asymptotic convergence rate estimates can be obtained without requiring an a priori curvature bound, providing a massive theoretical justification for Riemannian line-search methods on low-rank varieties [cite: 9, 10].

## 7. Deep Learning, Gradient Flows, and the Łojasiewicz Inequality

The intersection of tensor approximation, rank-r manifolds, and the Łojasiewicz inequality has profound implications for deep learning theory, particularly regarding how neural networks implicitly regularize during training.

### 7.1 Implicit Regularization and Deep Linear Networks (DLN)

A central mystery in deep learning is why overparameterized models trained with stochastic gradient descent generalize well instead of severely overfitting. This phenomenon is termed "implicit regularization" [cite: 5, 24, 29]. Francis Bach notes that unconstrained gradient descent for linear models implicitly biases toward minimum $\ell_2$-norm solutions [cite: 29]. 

For deep linear networks, the overparameterization corresponds to factoring a weight matrix into multiple layers. The gradient flow for the DLN represents a complex dynamical system. When the loss function is degenerate and the system is overparameterized, standard tools like La Salle's invariance principle struggle. However, the Łojasiewicz convergence criterion excels here because the square loss is an analytic function [cite: 4, 5, 18].

### 7.2 Balanced Initializations and Invariant Manifolds

A critical breakthrough in DLN theory is the concept of balanced initializations. If the initial weight matrices $\mathbf{W}_i(0)$ are chosen such that $\mathbf{W}_{i+1}^T \mathbf{W}_{i+1} = \mathbf{W}_i \mathbf{W}_i^T$, this balance is conserved throughout the continuous gradient flow [cite: 3, 4, 23]. 

This conserved quantity defines a stratified algebraic variety. As established in [cite: 3, 4] (referencing the ubiquitous Theorem 4.5), the gradient flow leaves the manifold of rank-$r$ matrices invariant. Because the trajectory is bounded and remains on this rank-$r$ manifold, applying Łojasiewicz's theorem proves strict point-wise convergence to a global minimizer for networks of depth 2, and to a global minimizer on a fixed-rank manifold for depths 3 or greater [cite: 3, 4, 24].

### 7.3 Polyak-Łojasiewicz (PL) Condition in Low-Rank Matrix Factorization

A specific, stronger variant of the KL property is the Polyak-Łojasiewicz (PL) condition, which states that $\|\nabla f(\mathbf{x})\|^2 \ge 2\mu (f(\mathbf{x}) - f^*)$. When an objective function satisfies the PL condition, gradient descent achieves a linear convergence rate to the global minimum, even without strict convexity [cite: 29, 30, 31].

In low-rank matrix factorization $\min_{\mathbf{X}, \mathbf{Y}} \|\mathbf{X} \mathbf{Y}^T - \mathbf{A}\|_F^2$, the objective does not globally satisfy the PL inequality due to scale indeterminacies and saddle points. However, recent work proves that from an asymmetric random initialization, alternating gradient descent (AGD) stays within a region of the loss landscape where a uniform Polyak-Łojasiewicz inequality holds [cite: 32]. Because the iterates' columns remain in the column span of $\mathbf{A}$, a positive $r$-th singular value provides the necessary PL inequality, guaranteeing linear convergence in a mathematically rigorous manner [cite: 32].

## 8. Accelerated and Regularized ALS Algorithms

While the KL property establishes that ALS and its variants will eventually converge, the speed of convergence (especially in swamps) is often unacceptably slow. Consequently, substantial research has been devoted to accelerating ALS.

### 8.1 Aitken-Stefensen-like Updates and Nesterov Acceleration

To accelerate the Regularized ALS (RALS) algorithm, Wang et al. proposed a fast iterative method employing an Aitken-Stefensen-like update [cite: 7]. Unlike vanilla Nesterov acceleration—which uses a standard momentum sequence and can exhibit oscillations if applied naively to non-convex ALS—this accelerated update significantly improves convergence speeds in severely ill-conditioned tensor approximations [cite: 7]. The global convergence of this accelerated RALS remains anchored by the Kurdyka-Łojasiewicz inequality, demonstrating that complex sequence acceleration does not destroy the KL-based convergence guarantees [cite: 7].

### 8.2 Block Coordinate Descent and Jacobi-type Methods

ALS is fundamentally a Block Coordinate Descent (BCD) method. While ALS sequentially updates factors by fully solving least-squares subproblems, Jacobi-type algorithms update multiple blocks in parallel or via sequential orthogonal rotations on Stiefel manifolds (product of unitary groups). 

For homogeneous polynomial optimization on Stiefel manifolds (used in joint approximate tensor diagonalization), Jacobi-type algorithms iteratively maximize local quadratic forms. The global convergence of Multi-block Jacobi-type (Jacobi-MG) and proximal Jacobi (Jacobi-MGP) algorithms has also been rigorously proven using the Łojasiewicz gradient inequality [cite: 33].

### 8.3 Orthogonalized and Randomized ALS

Two other notable modifications address local optima and ill-conditioning:
1.  **Orthogonalized ALS (Orth-ALS):** Proposed by Sharan and Valiant, this method periodically orthogonalizes the factor estimates during the ALS loops. By forcing orthogonality, it prevents multiple recovered factors from "chasing after" the same true factors, successfully avoiding poor local optima and rapidly converging to true factors under standard incoherence assumptions [cite: 34].
2.  **Randomized ALS:** To address the severe numerical ill-conditioning of the least-squares matrices at each ALS iteration (which requires solving normal equations), Reynolds et al. introduced a randomized variation. By projecting the equations onto random tensors, the condition numbers of the ALS matrices are drastically reduced, ensuring stability while maintaining comparable accuracy, a critical feature for high-dimensional stochastic PDEs [cite: 25].

## 9. Tensor Completion and Applications

The theoretical convergence machinery we have discussed—ranging from the KL inequality to rank-$r$ manifolds—finds its most immediate practical application in tensor completion.

### 9.1 Formulations of Tensor Completion

Tensor completion aims to reconstruct a high-dimensional dataset from a tiny subset of observed entries [cite: 1, 27, 35]. Assuming the true tensor has low rank, the problem is formulated as minimizing the rank subject to observation constraints, or minimizing the error over observed entries subject to a rank constraint $\mathcal{X} \in \mathcal{M}_r$. 

This can be approached via CP format (using Riemannian preconditioning or $\epsilon$-ALS) or Tensor Train (TT) format [cite: 1, 27, 28, 35]. In the TT format, the storage complexity scales linearly with the dimension $d$, rather than exponentially. Riemannian gradient descent for TT completion converges locally if the measurement operator satisfies the Restricted Isometry Property (RIP) on the tangent space $\mathcal{T}_{\mathcal{X}}\mathcal{M}_r$ [cite: 28].

### 9.2 Managing Ill-Conditioning and Overestimated Ranks

In practical completion tasks (like imputing missing slices in fMRI data or hyperspectral imaging), the true rank is unknown. Overestimating the rank parameter $R$ in standard ALS leads to rank-deficient factor matrices, which cause the subproblem Hessians to become singular, destroying traditional convergence proofs and halting the algorithm.

However, modern approaches designed around Riemannian preconditioning (and theoretically verified by Theorem 4.5 via the Łojasiewicz property) inherently tolerate rank-deficient factor matrices [cite: 1]. By relying on the KL property, these algorithms guarantee convergence to a stationary point regardless of the rank overestimation, bypassing the need for tedious, sequential rank-explorations. Similarly, algorithms like Iteratively Reweighted Least Squares (IRLS) achieve local quadratic convergence rates for efficiently completing highly ill-conditioned low-rank matrices [cite: 11].

## 10. Conclusion

The convergence theory of Alternating Least Squares (ALS) and its modern variants for tensor approximation represents a triumph of applied algebraic geometry in numerical optimization. Historically plagued by the topological non-closedness of rank-$r$ manifolds and the resultant ill-posedness of CP approximations, the field lacked rigorous global convergence guarantees. 

The introduction of the Łojasiewicz gradient inequality and the Kurdyka-Łojasiewicz (KL) property fundamentally altered this landscape. By establishing that polynomial and semi-algebraic objective functions possess gradient geometries that bound deviation from critical points, researchers proved that ALS sequences of finite length strictly converge to stationary or KKT points. 

This theoretical framework is elegantly encapsulated by the recurring "Theorem 4.5" found across disparate literature—from Riemannian gradient descent for tensor completion [cite: 1], to $\epsilon$-ALS for orthogonal tensor approximations [cite: 2], to the analysis of gradient flows in deep linear neural networks restricted to invariant rank-$r$ manifolds [cite: 3, 4]. Whether operating via Euclidean block-coordinate descent, preconditioned Riemannian manifolds, or regularized tangent cones, the Łojasiewicz inequality serves as the definitive mathematical anchor, ensuring that the theoretical guarantees of tensor factorization match the robust algorithmic performance witnessed in contemporary data science and machine learning.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-Ej9aEv8lZOl43FUKepC07d6D7frTa31DiP1fJfwNjV66BhZSyGOUdwb34Tav53RnxApqV-E-XXtJ3aUMTOz6SIT4lEUfMHgGRa4epbvXds5IV_3bnw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUd86j1HPmQchNSwASD6tPpgjzXz5gv-94y8kGkl4bOf0mK2DpPHaJ46WdWRLgi1DCJzieL_K-sVnFN9vKXmtpNOyEaKqFmZKhuuZD82tn3ovsEm-YtA==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJeX6xG_hbux7DWJkX2fWlgHGbxHAXp4Gm-LH8cQspvKjBi_dlQt0C8lMPFbPHb0LjWfO9RqsC-DkDq9vKll2QP9DXCNy-i63IpDQURai3PTzv5ABG9Q==)
4. [uni-muenchen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHyX4AWpUkEyWvH6UH1uhV4_AQ8u_motvcxSjtluvixk8UvqKVZYeTOb6BhGa8eZc2jPFjyEJCoj2owG8rlg9oxQL0kyNdqoTywBcQCZ0XUIXAdlZPrDxSKsDqO_8Ij1JFUY-IfIHwhWCjytGUa4qWmpTWWXo=)
5. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqVGw-f9yRonwhb-K2oQXRapLgmpYtqpDyMP0zYL_GUL8HbWf84X8oJMeF3wIElsv79N3ijvU6m6-9HN0wyiijGBBk4tqNxDnUV20pr8kSZYz346cALps4tE1NJf2WdVUrinE=)
6. [dfg-spp1324.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7j9ZN77wGehb2jj5JWAWlg60cVfS7DFHYY7vChCEmaV2rFIZWyHZTi6ZLXYGt6HzvLXgyrw7IRdD41dIjPo080zJIk2NcZfGFqTLlEFhmdp5Gtr8xsGxR3Gak8IjmAv-V2IOOedaFrhioV7DOyfxIYy8=)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE__K8eDzvaLlvSYveBEVlae1-qkGanJk3iG2c5SWeliAnxCvvW57FneusD141qTkjj4ITWQwe5WUzsH4aLV-wj8Jdbfzvc4jTYEb9aJIlQnPphbyMPaS5yTmMLEPkSVGYcS-PRQuvib8J2jazonkZVbTyxyPjFX-3Mp_ZOcA93Bpk8K545aLG-OdWXyaJMWN2Sfjs5TmGRpVx9SSTLn3AUA-vHFhfzjmzB6F5_8SL4oomju-HhuOkxcg==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY3B6QjS4G9k8KHs79OhjnpHa9uLKS8fPqu7KEcl5M8Os9mgUlu7yPyCXED_8UucXfs7RSwVCiDjQWLctP8iFlfCcBkif3f3OCtXt8zC75szvnmtKlfZxEOag32hUTgf7P885SPlgWIAwPhOH6mQUOQDeQNYP0G0SrGEpdMuco7Y_eNxFF68qi_nh-CLNvAobww4zzj8UhPL4JkfY2LEBNMdIctaH-jN5Kb7qhIGb2qNbycao=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEflinscXphbHrR1d-05IAiDDG5C2kEeEfYNmyXY8r9hhEqAx5hhFT5AXOI1dSV4sVJ5wpfVhkT_io1eOFt8AjFz8zqKRKs5B7VmvXJcbpxSU0Vd3Ra)
10. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERAJ9KZPrw1xAZ8eHAxyYOPYGwuGsatx_8ZIaBgmvTaqY-vpqvcxCGsJHLf4cRIrWa7rsvEO-Fumgbtoo7SAN4OlEWPj88g1TODQNLrsYO2I_7BTunpwzchaD3YIFsJosLQXcuWlfCKw6dvnqB6Z-zpx95)
11. [tum.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0s8yuMoqTcCcvWztzm72iOeyifo3svo_WJbIq9--kU08O9WIHqJzWpGvI4kUDOhtuvj87An952IilIM7mx2rh8uREWab2S2kG_s56HEq64RUbj7qTHfzVjeG3qOAG4R85jZdlKwruf0I4zihwqVaNb5diCzGXLRJkYNbI0CPuWtY=)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyQMVJ_b3Z9vqWLtVPA61UJ-g6HJOgehwIV9pvAV2V3PkdFA_d7EJxaGgJh1yxFJD4JgNGQq8RIUjkvPGvTlFIApm6OVdrTWImDMgmnUd9i1h6VOmotICBjQARzalzfwq-ikdLQl1zjbj9CEDOwHTfUmaSFmnyZ12VhDLGpBiXsd571pqZr3gC9Rz2J4rhCA_lFyLiKbgIO_kzDDxJyydB8w==)
13. [informs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdlLRSWOenyU_HalDIskRXGumgnfPunzpuN8OIOKm6jpPSZFAnWgnGzceEfQhEAh_NuoMu3Xv6P2Sy4Ft25qnBRBozHGt2TECRc7TMgaj-WWlJL3YlB50uogQOleechnupmOWdBG-02EUCP7WgyHQ=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuSuKsSGD7Ae99YPAnv0VrPaNlMZncHBELXkfGeesEY9yu-qxF8G2RUT_coFTH1AYzpy52jQEzEvbNizPk9IJRHeg_RLQ3yc7MEKLF9Jv35MzFDC1fCQ==)
15. [optimization-online.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9fVP_QYYRBhDn2D_jPJEq3CgwF4-pG-Ke99_5LYpeP42zseRrq2r09ZWJahlEtlkvJCsWDZwDTMOhYFv6Znsk4YTsdnAO9gn51TEHpbVyAfkAYGVD0X60yODZSPnNJZe9xQ36c3Nk9SQ1kfA_xlwnTpvUUIOTlyox)
16. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyiKYoHETDj-sJOu70l_bE27x_R3hg8Azd1ofJC-R2u2v8XaFeDiYdUcM5vvdzRljnV3UEqQJ09aVKVpvS8cHrDMbD89-EOPPmY43l1YkyquWpcHbl94YVLeQznOaucg1O1hD3k_7B1E4le3gx9XzYoMOYJw==)
17. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4BC9TtrBrl87pnx5VkojNbKz5DMmj9WK3cZ3Gne9ueYmLe9AECbSmiu7o8LKnhJgrg_ThHBWacqcFbXw_On0TseyAIaHKu3z1K5QW65pDmKBCnA8KIsFiIUxaAs7pclqWEa8hkqm2WXY9HQ==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvkdgFndTQNq7or2vcILsL9FJ374--oOSzpVhbix9Nt5a0UBl4Jxqkfb2uuYacmxz7BfRLyu2hrGo39Fi0kq5BGpof65ZtcNOS5PAErdFICZOA6UkAv2z1Iw==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhhS6c57jdBPdKuGB5JDzRYOBjQBm4xahO7Wum9NlXEAPKNihsellSr52W1-c8Qt5I5ROiwaeE9pVTO6PSaT8g3QAK03b-r2oG7IDM25nUvnHcXs9cCA==)
20. [ybook.co.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLuY32g31JFGN6DhNx0bFnGtMDkw3fGTlokY5Qk580kJyIyLcd_UcKNOCY9za-z0yNkgU7EF2cghn1_QA3F54LvDy4yEJsQPjDcmDDhQWdFu7pDOtFs4UBxqGEbslkEU6ynWQhJjNg0Kq5f2fng6vO)
21. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElIghi-CmpE7RQ1mNHNP28L3q5icQ6_Zo0jttA2hBrqIWj_wl-V_javzXk4Pui3jH2WDkQxEN_iAz4M3Ah3mMWKL7KS6rK-qEkMMrJQqKuVIDyVkkV_jIg5NxlKl6uNCOjMUKWox6gfJgOzw==)
22. [uclouvain.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFLLxmKWvnsexER1OO_mkyAc9byl-bHbP7U23gN-UnrouOKvuG9xtZT7nWEwZfJ-23cMp6mP5jLVtxjJ4mJ0xUDA-tTDtvkccnfPmUtZEfl1VDL-62P5epOWSNBNIbNED1Ui70ivwHk1_Bl8GMfA==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWfuWuZNk1wWgdI65jFPxaTtJ6ZOtXH6yuuv8QeImtoihjzEfdntu0M3k8zt7Orjpz5rVvn30VOlFKeaoY5diMz4RFCOwZ5sg2lQjKltPDJeYt4olUWpxnztrujivzS5hyePmSHHQK-_oDsSXFyT1jxcymkWm7QM2oBM7CqCBr2kteQMEOvGjz9hly7OTZZMn9wQGXcWDX7CvgOofObUkyufSMixfmUQaRAF9kL1pmk4-SFv5NUoH250TpKAbSsgvNJXY3LyCue5zUpWI6)
24. [rwth-aachen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYFezgOFSyHlIfm_b5jvb9qHu4Ks8NOSxP8XWVmxuAWab-qgVB_oojgio461CByhrq_Gc2agLAUXdpR1U8gF_Gxr6LImi_WL1UHX7fYaSxqsvcvS0B3gN8wajJMe1W0VMysrXuWmzzPgAN6csXoh6GFxFVbTk=)
25. [colorado.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAHz3rFIPe00OXsJ3khhfie_jGt39ISdaH3Qo-cE52Rzn2lY1-2J_VbZGLfk0oS_pozWOEzCqseDQ2G0HqrbNoVYCaY5ALwFP2pNLrepcoHgBTr2sL23fg54nFG4Rksr7ut27uUC6VIWIpkswZ1cs79o3L4XpEqK2DEp0KRg==)
26. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRWF1z1hmdQsEXWM_XLZ5h-Bn0LGV7hhyEf5XovdjGPckJ3chJL4q6nP97QjZOat3SLWHsxxYWlWdZAxE8WTiYtuYZsbR37EyzMZm2lOm8VbMp3r5CdeayObfwnP1Yv1m-Ijerp8mUaTaM2XJDTto5u1cx3iHW)
27. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsjKZ9rdAA3WJyrJQIwMFYmldwP2clL4g9H2lTUo4Fq1QpCOdNHVMeS-Uk42j5H9xLE082XvbGfPK3z8-iorqAo4_jLhQ-0g1l7zeGpT0BHpqB-KiBDf6re67-44B3gcmsv6gCO5yzRa4ga-wop9o2772XOw==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvcaFKjFCry9_o5KM2LQHKqPwbx9i16O2IxeQV1geXTkU8_wirCEeTYR-kuGAUTDBBKekQWdFEvx2roat2oDNWA9NA8Rmd4yKmCf-qibrJALLXaFaZ5Q==)
29. [ens.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzjog_7hu5mDpuXsda4siY4hJOJatEb-s2btWAs0oY9geXH6WOkHgcQ25LWPcQfvES_u1GAc9k3M4TNamaty8eKSBQltIkCO6npO3GEKM9LaOdqSJ8lBRqjBspEo_AV15b-wsKj-YWYUONZQah_e1hv247jqw=)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB5uGE4D22N_eHPfUPudjMPdLAAu012nLPPd_4iUL79RTqqwEmKmyfMS2nuweNjzwZTkOE72xKjzUOXLyRiGdh3jvxM2IYg65BLyDg4wUkiRGZxGbDM5i_qKNfSblbmYWEXwpDhon0FaYHHFV-ynRMctpQnfjEEExqwZvU--pZ-6wT7QpMmWdHkCsUVlY17xrXwjyn2kenvlRu4rc19vefR2HmwOI0-Yf5rCJ1ZRMf0_akpmkjMeMgg-ywmrTXKLaJxbPRAzRsdUw_yT1S7Q==)
31. [diva-portal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhNgiZXnG9rOSmVYCv_d0pdtHSdUzFP9IyC89P9uGo7SojSMMjKT8SqeWHKJXdf-oEKZGdOK2ktRZlqXbO9enENzlDsrMg2MEmNfOMgZNT9GaCjcQA4GaayCXlLUMPynCQkk8cBMTCHHkLzDzSnAjQmZWLnq78zFk=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9M4yJwyMIQB4ZXx88SGYM5smZBpYws52zvZg7K7WsPhc1tGFJNDoyaRAuuUmnt2RIc5rBAuzqeHu9RvN-GUZcaubHrTTx0souy05gpO_opeiUilJo3w==)
33. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMSuPMj35K6zl7k3DJzutMUWYqSKDECyeQPpiRaSOZrXiArjfDFuBuFBOAy0ltAgysPYEq1_p6s2UF4iBXJmba6O1bzUYyauC9Zj4_8yZZLZKHauWewCdhFYF1JOxComxz82PJsc3doLvNBYc5TrOcgFnSofaZ0JIjPYAn9o8wx3ULhQ7TludJWt9_0BIGi9s0PEE6_ptSldgpqCdANJ5yJyE2tZgSAXpvAV-66u1wMwRE00lu-hKV-n9AmtYuv91owpC-pj3NNX0JS9AkrBccAza2FVH7_mYjKsG1paJMhmGF4NKH48-k)
34. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKRDCCcut7KDwaSiK6ZKb2qUHojRB7_PMFnWwAQ1vGQgH4xcXvC0FZEvUjjdvna-lVZiQ4neU27HLiU-AeVkchlfQm9sss6mHZuDHJKCBKdIwEmOioaCdiYRF4CKc3bO7IzSd-)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnPW2H8zuXzOPbJDC2JbYlfVbLzGXBwn6Yzlv8LZH-qlLmXbFm_vT-uH8h44-N5hmtV4FoJ-M-iYnj2FItC_AZCP7CvkEe34o7NvjyZHS6oSZ2HmNQDw==)


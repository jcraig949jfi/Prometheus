# T#68 Tensor Perron-Frobenius extension (nonnegative tensor classes)

**Pythia queue id:** 109
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdzeDhQYXFHdklvUzBqTWNQalBuQThRaxIXc3g4UGFxR3ZJb1Mwak1jUGpQbkE4UWs
**Elapsed:** 310s
**Completed at:** 2026-05-21T15:12:43.037172+00:00

---

# Tensor Perron-Frobenius Extension and Nonnegative Tensor Classes

The classical Perron-Frobenius theorem, originally developed for nonnegative matrices, has been successfully extended to higher-order tensors, marking a significant advancement in numerical multilinear algebra. Unlike matrix eigenvalue problems, which are linear, tensor eigenvalue problems are intrinsically non-linear and rely on complex polynomial systems. Because of this non-linearity, multiple distinct definitions of tensor eigenvalues have emerged, most notably H-eigenvalues and Z-eigenvalues. To rigorously establish the existence and uniqueness of positive eigenvectors—a core guarantee of the Perron-Frobenius theorem—mathematicians have meticulously defined various classes of nonnegative tensors, including irreducible, weakly irreducible, essentially positive, and weakly positive tensors. The computation of these spectral radii is efficiently handled by globally convergent numerical methods, such as the NQZ algorithm and the Newton-Noda Iteration. The theoretical insights gained from the tensor Perron-Frobenius extension have broad, critical applications in spectral hypergraph theory (via eigenvector centrality), higher-order Markov chains, and solid mechanics. Furthermore, recent theoretical frameworks utilizing multi-homogeneous order-preserving mappings and the Hilbert projective metric have unified these results, extending the Perron-Frobenius theory far beyond standard multilinear forms. 

## Introduction to Tensors and Multilinear Algebra

Matrix theory has long been recognized as one of the most fundamental computational and theoretical tools in science and mathematics, with numerous classical texts detailing its robust algebraic and geometric properties [cite: 1]. However, modern scientific and engineering disciplines increasingly generate multi-indexed data structures that cannot be adequately analyzed using standard two-dimensional matrices. As a direct higher-order generalization of a matrix, the concept of a tensor (often referred to as a hypermatrix in combinatorial contexts) has been heavily adopted to model these complex systems [cite: 1]. With the introduction of additional subscripts, tensors possess intrinsic geometric and algebraic structures that would be destroyed, or at best heavily obfuscated, if the multi-way data were merely unfolded or reshaped into standard matrices [cite: 1].

Formally, a tensor $A$ of order $m$ and dimension $n$ over a field (typically the real numbers $\mathbb{R}$ or the complex numbers $\mathbb{C}$) is represented as an $m$-way array of values $A = (A_{i_1 i_2 \dots i_m})$, where each index $i_j$ ranges from $1$ to $n$ [cite: 2, 3]. Under this nomenclature, a standard vector is considered a first-order tensor, and a matrix is a second-order tensor [cite: 4]. When $m > 2$, these mathematical objects are specifically classified as higher-order tensors [cite: 4].

The spectral theory of tensors, which focuses on the properties of tensor eigenvalues and eigenvectors, has evolved rapidly. In 2005, the foundational concepts of tensor eigenvalues were independently proposed by L. Qi and L.-H. Lim [cite: 2, 5]. Because tensor eigenvalue equations equate to finding nontrivial solutions to systems of polynomial equations in multiple variables, the problem is intrinsically nonlinear [cite: 2, 3]. Consequently, the computational complexity of calculating the eigenvalues for a general higher-order tensor, even for a low order such as three or four, has been proven to be NP-hard [cite: 5].

Despite these computational hurdles, the mathematical community discovered that for specific, highly structured classes of tensors—most notably, nonnegative tensors where every entry is a non-negative real number—robust theoretical frameworks could be established [cite: 5, 6]. Just as the classical Perron-Frobenius theorem brings absolute order to the spectrum of nonnegative matrices, an analogous tensor Perron-Frobenius extension characterizes the spectral radius of nonnegative tensors [cite: 5]. This theoretical breakthrough has attracted vast attention because of its widespread applications in automatic control, spectral hypergraph theory, higher-order Markov chains, magnetic resonance imaging, polynomial optimization, and quantum entanglement problems [cite: 1, 5].

## Definitions of Tensor Eigenvalues

To comprehend the tensor Perron-Frobenius extension, it is necessary to rigorously define what constitutes an eigenvalue and an eigenvector for a tensor. Due to the multi-way nature of tensors, the generalization from the classic matrix eigenvalue equation $Mx = \lambda x$ is not mathematically unique. Two primary frameworks dominate the literature: H-eigenvalues and Z-eigenvalues.

For an $m$-th order, $n$-dimensional real tensor $A = (A_{i_1 \dots i_m})$, the fundamental arithmetic operation is the tensor-vector product. For a vector $x = (x_1, \dots, x_n)^T$, the contraction of $A$ with $m-1$ copies of $x$ results in an $n$-dimensional vector denoted as $Ax^{m-1}$, whose $i$-th component is defined as:
\[ (Ax^{m-1})_i = \sum_{i_2=1}^n \dots \sum_{i_m=1}^n A_{i i_2 \dots i_m} x_{i_2} \dots x_{i_m} \]
for $i = 1, \dots, n$ [cite: 6, 7].

### H-Eigenvalues and E-Eigenvalues

A complex number $\lambda \in \mathbb{C}$ and a non-zero complex vector $x \in \mathbb{C}^n \setminus \{0\}$ are called an eigenvalue and an eigenvector of $A$, respectively, if they strictly satisfy the system of equations:
\[ Ax^{m-1} = \lambda x^{[m-1]} \]
where $x^{[m-1]}$ denotes a vector whose $i$-th entry is the scalar exponentiation $x_i^{m-1}$ [cite: 2, 3]. 

If both the eigenvalue $\lambda$ and its corresponding eigenvector $x$ are strictly real, then $\lambda$ is specifically classified as an **H-eigenvalue**, and $x$ is termed an **H-eigenvector** [cite: 8]. The prefix "H" is derived from the terminology of homogeneous polynomials [cite: 9]. In the distinct terminology originally proposed by Lim, these are also referred to as $l_k$-eigenvalues (or $l_m$-eigenvalues, depending on the notation for the tensor's order) [cite: 10]. If an eigenvalue does not possess a real eigenvector, or is complex, it is simply considered part of the broader tensor spectrum. 

The spectral radius of a tensor $A$, denoted by $\rho(A)$, is defined as the supremum of the absolute values (or moduli) of all its complex eigenvalues:
\[ \rho(A) = \max \{ |\lambda| : \lambda \text{ is an eigenvalue of } A \} \]
[cite: 11, 12]. For nonnegative tensors, $\rho(A)$ plays a central role analogous to the dominant eigenvalue of a nonnegative matrix.

### Z-Eigenvalues

An alternative, equally important formulation is the **Z-eigenvalue** (also identified as the $l_2$-eigenvalue in Lim's nomenclature) [cite: 13]. A real number $\lambda$ and a real vector $x$ form a Z-eigenpair if they satisfy:
\[ Ax^{m-1} = \lambda x \]
subject to the strict spherical normalization constraint:
\[ x^T x = 1 \]
[cite: 14].
From this defining equation, pre-multiplying by the transpose $x^T$ yields $\lambda = x^T A x^{m-1} = Ax^m$ (where $Ax^m$ is the scalar value obtained by contracting the tensor with $m$ copies of the vector $x$) [cite: 14]. Therefore, a vector $x$ is a Z-eigenvector if and only if $Ax^{m-1} = (Ax^m)x$ alongside the constraint $x^T x = 1$ [cite: 14]. The "Z" nomenclature separates it from the "H" notation, with the fundamental structural difference being the polynomial degree on the right-hand side of the equation. Z-eigenvalues correlate directly to spherical optimization problems, whereas H-eigenvalues are intrinsically linked to projective space mappings.

### M-Eigenvalues and Other Variations

Other specific tensor eigenvalue definitions have been formulated for specialized physics applications. **M-eigenvalues** are critical in nonlinear solid mechanics for evaluating the elasticity tensor and the physical strong ellipticity condition [cite: 15]. The strong ellipticity condition holds mathematically if and only if the smallest M-eigenvalue of the elasticity tensor is strictly positive [cite: 15]. Interestingly, the elasticity tensor is rank-one positive definite if and only if its smallest Z-eigenvalue is positive, establishing that a Z-eigenvalue of an elasticity tensor is always an M-eigenvalue, though the converse is not true [cite: 15]. The study of non-negative biquadratic tensors also involves specific subset values known as $M^{++}$-eigenvalues, which are characterized by possessing pairs of non-negative M-eigenvectors [cite: 16]. Additionally, E-eigenvalues and N-eigenvalues are frequently calculated in advanced symmetric tensor analysis [cite: 9].

## Classes of Nonnegative Tensors

The classical matrix Perron-Frobenius theorem neatly categorizes square matrices into strictly positive, irreducible, and general nonnegative formats. For tensors, the combinatorial and index structure is vastly richer, necessitating a highly nuanced and rigorously defined classification of nonnegativity and irreducibility [cite: 5]. Over recent years, researchers have established multiple hierarchical classes of nonnegative tensors to delineate the precise conditions for the existence, uniqueness, and algorithmic computability of strictly positive eigenvectors [cite: 17]. 

Let $A = (A_{i_1 \dots i_m}) \in \mathbb{R}^{[m,n]}_+$ denote a general nonnegative tensor, meaning that every individual entry $A_{i_1 \dots i_m} \ge 0$. The following classifications dictate its spectral behavior.

### Reducible and Irreducible Tensors

The fundamental combinatorial concept of matrix irreducibility was formally extended to higher-order tensors by Chang, Pearson, and Zhang in 2008 [cite: 6, 17]. A nonnegative tensor $A$ of order $m$ and dimension $n$ is termed **reducible** if there exists a nonempty, proper index subset $I \subset \{1, 2, \dots, n\}$ such that:
\[ A_{i_1 i_2 \dots i_m} = 0 \quad \forall i_1 \in I, \text{ and } \forall i_2, \dots, i_m \notin I \]
[cite: 3, 11].
If no such index subset $I$ exists, the tensor $A$ is declared **irreducible** [cite: 6, 7]. Geometrically, irreducibility means that the multi-way tensor cannot be partitioned or permuted into a block structure where one set of coordinates completely fails to influence the other under the iterative tensor mapping.

### Weakly Irreducible Tensors

While the irreducibility defined by Chang et al. is mathematically powerful, it proved to be somewhat restrictive for general network structures. Friedland, Gaubert, and Han introduced a significantly broader class identified as **weakly irreducible** nonnegative tensors [cite: 17]. This definition relies heavily on a two-dimensional representation matrix. The representation matrix $G(A)$ associated with a tensor $A$ is an $n \times n$ matrix whose $(i,j)$-th entry is calculated as the sum of all tensor entries where the first index is $i$ and at least one of the remaining $m-1$ indices is $j$ [cite: 18]. In graph-theoretic terms, a directed graph is constructed where a directed edge exists from node $i$ to node $j$ if there exist indices $i_2, \dots, i_m$ such that $A_{i i_2 \dots i_m} > 0$ and $j \in \{i_2, \dots, i_m\}$ [cite: 8].
A tensor $A$ is said to be weakly reducible if the constructed matrix $G(A)$ is a reducible matrix; conversely, the tensor is **weakly irreducible** if $G(A)$ is an irreducible matrix [cite: 17, 18]. Every irreducible tensor is weakly irreducible, but the converse statement is generally false [cite: 17].

### The Majorization Matrix and Essentially Positive Tensors

A highly useful algebraic construct for analyzing the diagonal dominance of nonnegative tensors is the majorization matrix. The majorization matrix $M(A)$ associated with a tensor $A$ is a nonnegative $n \times n$ matrix whose entries are drawn exclusively from the multi-way "diagonal" of the tensor's respective subtensors. Specifically, its $(i,j)$-th entry is defined as:
\[ M(A)_{ij} = A_{i j \dots j} \]
for all $i, j \in \{1, \dots, n\}$ [cite: 17, 18].

Leveraging this construct, Pearson introduced the important class of **essentially positive** tensors [cite: 2, 17]. A nonnegative tensor $A$ is classified as essentially positive if its majorization matrix $M(A)$ is a strictly positive matrix—that is, $M(A)_{ij} > 0$ for every $i, j \in \{1, \dots, n\}$ [cite: 3, 18]. From a topological standpoint, essentially positive tensors have the defining geometric property of mapping the non-negative orthant (excluding the origin) directly into its deep interior [cite: 3].

### Weakly Positive and Generalized Weakly Positive Tensors

Zhang, Qi, and Xu relaxed the strict condition of essential positivity to define **weakly positive** tensors [cite: 2, 5]. A nonnegative tensor $A$ is weakly positive if the strictly off-diagonal entries of its majorization matrix are strictly positive. That is, $A_{i j \dots j} > 0$ for all unique pairs where $i \neq j$ [cite: 2, 18]. This definition crucially does not constrain the purely diagonal entries $A_{i i \dots i}$, allowing them to equal zero.

Further relaxing this structural concept, a tensor $A$ is termed **generalized weakly positive** if there exists at least one specific target index $i_0 \in \{1, \dots, n\}$ such that for all $j \neq i_0$, both symmetric conditions $A_{i_0 j \dots j} > 0$ and $A_{j i_0 \dots i_0} > 0$ hold strictly true [cite: 18, 19].

### Strictly Nonnegative and Weakly Essentially Irreducible Tensors

Defined by Hu et al., a tensor $A$ is classified as **strictly nonnegative** if the polynomial mapping evaluation $F_A(x) = Ax^{m-1}$ yields a strictly positive vector for any strictly positive input vector $x > 0$ [cite: 5, 17]. It has been definitively shown that a tensor is strictly nonnegative if it is weakly irreducible [cite: 17].

In recent advancements, Liu and Lv (2024) introduced the unified notion of **weakly essentially irreducible nonnegative tensors**, effectively extending and conceptually bridging the classes of essentially positive, weakly positive, and generally weakly positive tensors into a single comprehensive algebraic framework [cite: 18, 19]. 

### Primitive and Weakly Primitive Tensors

In classical matrix theory, primitivity relates to the eventual strict positivity of higher powers of an irreducible matrix (specifically, having a cyclic index of 1). For higher-order tensors, $A$ is termed **weakly primitive** if its representation matrix $G(A)$ is a primitive matrix [cite: 17, 18]. A related, more strict combinatorial definition states that a nonnegative tensor is simply primitive if it adheres to a specific topological structure regarding its cyclic index [cite: 5, 17].

### Hierarchical Relations Among Tensor Classes

The strict logical relationships among these varied tensor classes have been rigorously established in the literature, providing a map for spectral guarantees. 
1.  If a tensor is essentially positive, then it is mathematically guaranteed to be weakly positive [cite: 2].
2.  If a tensor is weakly positive, then it is unconditionally irreducible [cite: 2, 17]. 
3.  Essentially positive tensors are both primitive and weakly positive, but a primitive tensor might not be weakly positive, and a weakly positive tensor might not be primitive [cite: 2].
4.  All the aforementioned specific classes (essentially positive, weakly positive, generalized weakly positive) fall entirely under the broader umbrella of weakly irreducible nonnegative tensors [cite: 20].

Understanding these precise relationships is vital because the strictness of the tensor class determines both the behavioral purity of its spectral radius and the guaranteed linear convergence rate of numerical algorithms used to compute it [cite: 2, 17].

## The Perron-Frobenius Theorem for Tensors

The core objective of classifying nonnegative tensors is to state exact versions of the Perron-Frobenius theorem. The theorem guarantees the existence of a positive, dominant eigenvalue (the spectral radius) and a corresponding nonnegative or strictly positive eigenvector. For tensors, the theorem is divided into weak and strong forms, and it is highly context-dependent, specifying whether it applies to H-eigenvectors or Z-eigenvectors.

### The Weak Form

For the broadest class of general nonnegative tensors—which may be highly reducible and contain a vast majority of zero entries—the weak form of the Perron-Frobenius theorem successfully holds [cite: 6]. It states:
If $A$ is a general nonnegative square tensor of order $m$ and dimension $n$, then:
1.  The spectral radius $\rho(A)$ is unequivocally an eigenvalue of $A$ [cite: 6, 11].
2.  There exists a non-trivial nonnegative vector $x_0 \ge 0$ ($x_0 \neq 0$) corresponding to $\rho(A)$ such that $Ax_0^{m-1} = \rho(A) x_0^{[m-1]}$ [cite: 6, 7].

This theorem ensures that for any nonnegative tensor, the largest eigenvalue in modulus is always a real, non-negative number, and it always possesses at least one non-negative H-eigenvector.

### The Strong Form for H-Eigenvectors

When the tensor is structurally upgraded from merely nonnegative to **irreducible** nonnegative, the strong form of the Perron-Frobenius theorem fully applies. As originally established by Chang, Pearson, and Zhang [cite: 6, 21]:
If $A$ is an irreducible nonnegative tensor, then:
1.  **Positivity of Spectral Radius**: The spectral radius is strictly positive, $\rho(A) > 0$, and $\rho(A)$ is an eigenvalue [cite: 6, 21].
2.  **Strict Positivity of Eigenvector**: There exists a strictly positive eigenvector $x_0 > 0$ (meaning all components of $x_0$ are strictly greater than zero) corresponding to $\rho(A)$, satisfying $Ax_0^{m-1} = \rho(A) x_0^{[m-1]}$ [cite: 5, 6].
3.  **Uniqueness**: If $\lambda$ is any eigenvalue possessing a nonnegative eigenvector, then it must be that $\lambda = \rho(A)$. Furthermore, the positive eigenvector $x_0$ corresponding to $\rho(A)$ is unique up to a scalar multiplicative constant [cite: 6, 21].
4.  **Maximal Modulus**: For any arbitrary eigenvalue $\lambda$ of $A$, its modulus is strictly bounded by the spectral radius: $|\lambda| \le \rho(A)$ [cite: 6, 21].

While this mirrors the matrix theorem seemingly perfectly, there is a distinct and highly fundamental difference regarding geometric and algebraic multiplicity. For an irreducible matrix, the Perron root is always an absolutely simple eigenvalue. However, for an irreducible tensor, $\rho(A)$ is **not necessarily a simple eigenvalue** [cite: 3, 6]. There exist concrete examples of nonnegative irreducible tensors possessing a positive eigenvalue with a unique positive eigenvector, yet the eigenvalue is not geometrically simple in either the real field $\mathbb{R}$ or the complex field $\mathbb{C}$ [cite: 6]. To ensure true algebraic simplicity, additional constraints, such as "Condition (M)", must be forcibly imposed on the tensor [cite: 6].

Regarding the distribution of complex eigenvalues on the spectral circle (the set of complex numbers $z$ where $|z| = \rho(A)$), Yang and Yang rigorously proved that if an irreducible nonnegative tensor has $k$ distinct eigenvalues of modulus $\rho(A)$, these eigenvalues are perfectly and uniformly distributed on the spectral circle. Specifically, they take the exact form $\rho(A) e^{i 2\pi j / k}$ for $j = 0, 1, \dots, k-1$ [cite: 5, 21]. The integer $k$ is referred to as the cyclic index of the tensor $A$. Furthermore, if an irreducible nonnegative tensor possesses a strictly positive trace ($Tr(A) > 0$), then the spectral radius $\rho(A)$ is the absolute unique eigenvalue on the entire spectral circle [cite: 21]. Unlike matrix theory, having a positive trace for an irreducible tensor does not automatically make it primitive, highlighting a highly nuanced structural divergence between matrices and tensors [cite: 21].

### The Strong Form for Z-Eigenvectors

The Perron-Frobenius theorem also extends beautifully to Z-eigenvectors, though the guarantees are notably weaker regarding the uniqueness of the vectors. For an order-$m$ irreducible nonnegative tensor $A$, there exists at least one Z-eigenpair $(x, \lambda_1)$ satisfying $Ax^{m-1} = \lambda_1 x$ and $x^T x = 1$ such that $\lambda_1 > 0$ and the corresponding vector $x > 0$ [cite: 10, 13].

However, the critical mathematical distinction from H-eigenvectors is that **multiple positive Z-eigenvectors can exist for the exact same tensor**, even corresponding identically to the same positive eigenvalue $\lambda_1$ [cite: 10, 13]. This explicit lack of uniqueness has massive ramifications for practical applications, such as defining network centrality, where a singular, unique ranking vector is required by network scientists [cite: 13].

### The Collatz-Wielandt Minimax Theorem for Tensors

In standard linear algebra, the Collatz-Wielandt formula provides a powerful variational characterization of the spectral radius, which is exceptionally useful for bounding and approximating the dominant eigenvalue. This theorem successfully extends directly to nonnegative tensors. For an irreducible nonnegative tensor $A$, the spectral radius $\rho(A)$ can be exactly bounded via the minimax formulation:
\[ \min_{1 \le i \le n} \frac{(Ax^{m-1})_i}{x_i^{m-1}} \le \rho(A) \le \max_{1 \le i \le n} \frac{(Ax^{m-1})_i}{x_i^{m-1}} \]
for any strictly positive input vector $x > 0$ [cite: 7, 22]. These bounds become an exact equality if and only if $x$ is the exact Perron vector (the unique positive H-eigenvector) [cite: 22]. This minimax principle serves as the theoretical foundation for iterative numerical algorithms designed to compute the spectral radius.

Furthermore, it has been demonstrated that the problem of finding the spectral radius (or the largest singular value) of a nonnegative irreducible square (or rectangular) tensor can be rigorously converted into a formal convex optimization problem [cite: 21, 23]. This is achieved by proving that every nonnegative irreducible tensor with a unit spectral radius is diagonally similar to a specifically structured irreducible stochastic tensor [cite: 21].

## Max Algebra Extension

Beyond standard arithmetic operations over the real or complex field, the Perron-Frobenius theory for tensors has been successfully transposed into the idempotent semiring known as **max algebra** [cite: 4, 24]. Max algebra, sometimes referred to interchangeably as tropical algebra or max-plus algebra, replaces standard addition with the maximum function ($\oplus = \max$) and standard multiplication with conventional addition ($\otimes = +$) [cite: 4]. However, in the strict context of multiplicative max algebra for nonnegative tensors, the operations are often defined over the non-negative reals $\mathbb{R}_+$ where $a \oplus b = \max(a, b)$ and $a \otimes b = a \times b$ [cite: 4]. 

Max algebra is an exceptionally potent framework for modeling non-linear problems that spontaneously appear in industrial manufacturing, transportation scheduling, discrete event-dynamic systems, combinatorial optimization, and mathematical physics. These highly non-linear problems miraculously become strictly linear when described in the language of max algebra [cite: 4, 24].

For an $n \times n$ nonnegative matrix $A$ evaluated in max algebra, the eigenvalue problem is written as $A \otimes x = \lambda x$, which algebraically translates to $\max_j (A_{ij} x_j) = \lambda x_i$. The dominant eigenvalue in this specific algebraic system is known to be the maximum circuit geometric mean of the weighted directed graph corresponding to matrix $A$ [cite: 4, 24].

Generalizing this elegant concept to higher-order tensors, if $A \in \mathbb{R}^{[m,n]}_+$ is a nonnegative essentially positive tensor (satisfying certain minor non-degeneracy conditions), a direct analog of the Perron-Frobenius theorem dictates that there exists a unique positive max eigenvalue $\mu(A)$ and a corresponding strictly positive vector $x$ such that:
\[ \max_{1 \le i_2 \dots i_m \le n} \{ A_{i i_2 \dots i_m} x_{i_2} \dots x_{i_m} \} = \mu(A) x_i^{m-1} \]
for $i = 1, 2, \dots, n$ [cite: 24, 25, 26]. 

This max algebra version of the tensor Perron-Frobenius theorem flawlessly maintains the core spirit of the classical theorem [cite: 25]. Powerful iterative methods based on diagonal similar tensors have been proposed to efficiently find the largest max eigenvalue of a nonnegative tensor. Crucially, these methods are proven to be globally convergent for the broad class of weakly irreducible nonnegative tensors [cite: 24].

## Multi-Homogeneous Mappings and the Hilbert Projective Metric

While the extension of the Perron-Frobenius theorem to nonnegative tensors is a major mathematical achievement, researchers realized that polynomial tensor-vector multiplication is merely a highly specific instance of a significantly broader class of nonlinear mathematical operators. A grand unifying framework was recently developed by A. Gautier, F. Tudisco, and M. Hein, who extended the Perron-Frobenius theorem to completely generalized **order-preserving multi-homogeneous mappings** defined on a product of cones [cite: 27, 28].

A general mapping $F: K_+ \to K_+$ (where $K_+$ represents a product cone) is defined as multi-homogeneous if it possesses a block-wise homogeneity described strictly by a non-negative matrix $A$ (commonly called the homogeneity matrix or the Lipschitz matrix):
\[ F(t_1 x^{(1)}, \dots, t_d x^{(d)}) = (t_1, \dots, t_d)^A \otimes F(x^{(1)}, \dots, x^{(d)}) \]
[cite: 29]. Any multilinear map directly derived from a tensor is naturally a multi-homogeneous mapping with a specifically structured homogeneity matrix [cite: 30].

### Recasting the Eigenvalue Problem

The crucial innovation in this advanced geometric approach is to completely recast the nonlinear tensor eigenvalue problem as a classical fixed-point problem mapped onto a suitable product of projective spaces [cite: 28, 31]. By shifting the analytical perspective to projective spaces, researchers can leverage the incredibly powerful tools of metric geometry, specifically the **Hilbert projective metric** and the closely related Thompson metric [cite: 29, 32].

For two arbitrary elements $x, y$ existing in a normal closed cone $C$, the Hilbert projective distance $d_C(x,y)$ is defined as:
\[ d_C(x,y) = \log \left( M(x/y; C) M(y/x; C) \right) \]
where the margin function $M(x/y; C) = \inf \{ \alpha > 0 : x \le \alpha y \}$ [cite: 30]. The Hilbert projective metric effectively measures the exact angular distance between the *rays* spanned by $x$ and $y$, making it entirely blind to pure scalar multiplication [cite: 30].

### The Multi-linear Birkhoff-Hopf Theorem

The Birkhoff-Hopf theorem is a classical functional analysis result showing that a large class of cone-preserving linear operators act as strict contraction mappings with respect to the Hilbert projective metric [cite: 30]. Gautier et al. successfully proved a generalized multi-linear Birkhoff-Hopf theorem, explicitly extending this powerful contraction property to multi-homogeneous nonlinear mappings [cite: 27]. 

Because these specific mappings are order-preserving and strictly contractive under the Hilbert metric, the Banach fixed-point theorem can be directly and safely invoked. This mathematical maneuver immediately guarantees the existence and absolute uniqueness of a fixed point in the projective space, which corresponds exactly to the unique positive eigenvector of the multi-homogeneous mapping (and thereby the original underlying nonnegative tensor) [cite: 30].

This multi-homogeneous framework acts as a grand unifier for spectral theory. It provides a generalized Perron-Frobenius theorem that not only implies all earlier, separate results for non-negative tensors (such as the foundational work by Chang, Pearson, Zhang, Friedland, and Lim) but actually vastly improves them by requiring significantly weaker structural assumptions regarding tensor irreducibility [cite: 28, 31]. The overarching framework elegantly absorbs various complex spectral problems, including the computation of operator norms, multi-marginal optimal transport equations, and generalized discrete Schrödinger equations [cite: 27, 28].

## Computational Algorithms for Tensor Spectral Radii

Theoretical existence and uniqueness of dominant eigenvectors are mathematically foundational, but computing the spectral radius $\rho(A)$ of a massive, high-order data tensor is computationally demanding. Unlike standard matrices where the power method, QR algorithm, and Arnoldi iteration are universally standard, higher-order tensors require highly specialized iterative techniques [cite: 9]. These advanced algorithms rely heavily on the contractive properties established by the nonlinear Perron-Frobenius theory to guarantee convergence.

### The NQZ Algorithm

The most prominent, extensively studied, and foundational algorithm for computing the H-spectral radius of a nonnegative tensor is the **NQZ algorithm**, originally proposed by Ng, Qi, and Zhou in 2009 [cite: 11, 19]. It is universally regarded as the natural, multilinear extension of the classical power method used for dominant matrix eigenvalues [cite: 8, 19].

The iterative mathematical procedure of the standard NQZ algorithm operates as follows. Starting with an arbitrary, strictly positive initial vector $x^{(0)} > 0$:
1.  Compute the forward tensor-vector product: $y^{(k)} = A (x^{(k)})^{m-1}$.
2.  Take the entry-wise fractional exponentiation: $z^{(k)} = (y^{(k)})^{[1/(m-1)]}$.
3.  Normalize the resultant vector to generate the next iterate: $x^{(k+1)} = \frac{z^{(k)}}{\| z^{(k)} \|}$, where $\|\cdot\|$ is typically the vector 1-norm or 2-norm.

At each individual step, precise numerical bounds on the spectral radius are generated via the formulation:
\[ \lambda_{min}^{(k)} = \min_i \frac{(A (x^{(k)})^{m-1})_i}{(x^{(k)}_i)^{m-1}} \quad \text{and} \quad \lambda_{max}^{(k)} = \max_i \frac{(A (x^{(k)})^{m-1})_i}{(x^{(k)}_i)^{m-1}} \]
Dictated by the Collatz-Wielandt principle, as $k \to \infty$, both the lower bound $\lambda_{min}^{(k)}$ and the upper bound $\lambda_{max}^{(k)}$ monotonically and safely converge to the exact H-spectral radius $\rho(A)$ [cite: 19, 22].

**Convergence of NQZ:**
The theoretical convergence of the NQZ algorithm has been sequentially established for increasingly broader classes of tensors over the past decade. Originally, it was only proven to converge for strictly positive tensors. Later, Pearson mathematically proved its absolute convergence for *essentially positive* tensors [cite: 19]. Subsequently, Chang, Pearson, and Zhang rigorously established its convergence for *primitive* tensors [cite: 8, 19]. Recently, the R-linear convergence of the NQZ algorithm has been rigorously established for *weakly primitive* tensors and various generalized classes of *weakly irreducible* nonnegative tensors by utilizing directed graph connectivity analyses and establishing tight upper bounds for the root convergence factor [cite: 8, 19, 33].

### The LZI Algorithm

To artificially accelerate and mathematically secure convergence for very specific tensor classes, Liu, Zhou, and Ibrahim developed an optimized variant known as the **LZI algorithm** [cite: 2, 19]. The LZI algorithm shares the core architectural skeleton of NQZ but includes strategic mathematical modifications (often related to implicit translational transformations or diagonal similarity scaling) to gracefully handle tensors with zero entries heavily populated on the diagonal, or to actively improve the contraction rate. The LZI algorithm possesses an explicit, mathematically guaranteed linear convergence rate when applied specifically to the class of *weakly positive* tensors [cite: 2].

### The Newton-Noda Iteration (NNI)

While the NQZ and LZI algorithms offer highly robust linear convergence, higher-order geometric convergence rates are highly desirable for large-scale industrial computations. The **Newton-Noda Iteration (NNI)**, originally designed for non-negative matrices, has been brilliantly generalized to apply directly to weakly irreducible nonnegative tensors [cite: 22].

The NNI method elegantly combines the monotonic, structure-preserving properties of the generalized power method with the rapid local convergence profile of Newton's method. In the $k$-th iteration, a scaling parameter $\theta_k > 0$ must be actively selected. A practical and theoretically sound procedural method for determining $\theta_k$ is the halving procedure, which automatically guarantees global convergence [cite: 22]. Crucially, the Newton-Noda Iteration has been definitively shown to be globally and **quadratically convergent** [cite: 22]. For highly complex, numerically ill-conditioned weakly irreducible tensors, the NNI (or its generalized variant, the GNNI) can vastly outperform the standard linear NQZ algorithm in terms of computational speed [cite: 22].

### Semidefinite Relaxation for Z-Eigenvalues

While computing the H-spectral radius heavily relies on variations of power methods, finding Z-eigenvalues requires fundamentally different algebraic machinery. Because a generic tensor possesses finitely many Z-eigenvalues (but a structurally special tensor might paradoxically have infinitely many), identifying them is mathematically equivalent to locating the exact stationary points of a complex polynomial optimization problem constrained over a unit sphere [cite: 14].

For this specific purpose, **Lasserre-type Semidefinite Relaxation (SDR)** methods have been pioneered [cite: 9, 14]. The rigid polynomial optimization problem is systematically converted into a flexible hierarchy of Semidefinite Programs (SDPs). By systematically solving a finite sequence of these semidefinite relaxations, computational systems can systematically identify and compute *all* real Z-eigenvalues and real H-eigenvalues of a given tensor [cite: 14]. If the relaxation at a specific, early hierarchy level $k$ is declared infeasible, it definitively mathematically proves that the tensor has no real Z-eigenvalues whatsoever [cite: 14]. 

Another highly popular technique for computing extreme Z-eigenvalues is the Shifted Symmetric Higher-Order Power Method (SS-HOPM), originally proposed by Kolda and Mayo, which introduces a dynamic, adaptive shift to ensure strict monotonic convergence to the Z-eigenpair [cite: 9].

## Applications of Nonnegative Tensor Spectral Theory

The intense, decades-long theoretical labor poured into defining precise nonnegative tensor classes and their respective Perron-Frobenius extensions is entirely justified by the tremendous breadth and depth of their real-world applications across computational sciences.

### Spectral Hypergraph Theory and Eigenvector Centrality

In traditional, pairwise graph theory, a network is modeled cleanly by a 2D adjacency matrix. The classic Perron-Frobenius theorem guarantees a unique, strictly positive principal eigenvector for this matrix, which defines the universally utilized **Eigenvector Centrality** of the network's nodes. However, highly complex physical and social systems—such as academic co-authorship networks, multi-drug combinations in medical patient records, or high-dimensional genetic regulatory networks—feature multi-way interactions (e.g., three distinct researchers co-authoring a single paper simultaneously) [cite: 10]. These complex relationships are faithfully modeled by uniform hypergraphs rather than flat graphs.

The natural, uncompressed algebraic representation of an $m$-uniform hypergraph is an order-$m$ symmetric, entirely nonnegative adjacency tensor $T$ [cite: 10, 34]. Using the new tensor Perron-Frobenius theory, network scientists have developed profound novel hypergraph centralities:
1.  **Z-Eigenvector Centrality (ZEC)**: Based directly on the positive Z-eigenvector of the adjacency tensor $T$ [cite: 13]. While mathematically elegant for certain spherical projections, ZEC is functionally hampered by the fact that the Perron-Frobenius theorem for Z-eigenvectors does not preclude the existence of multiple, totally distinct positive eigenvectors. This inherent non-uniqueness can lead to deeply ambiguous, conflicting network rankings [cite: 10, 13].
2.  **H-Eigenvector Centrality (HEC)**: Based on the unique positive H-eigenvector [cite: 10, 13]. Because the strong form of the Perron-Frobenius theorem for H-eigenvectors rigorously guarantees that the positive vector is strictly unique (up to simple scaling) for an irreducible tensor, HEC provides a mathematically robust, globally stable, and uniquely defined centrality ranking score for nodes in any connected hypergraph [cite: 10]. HEC is widely utilized for critical data mining tasks like identifying vital, key spreaders in multiplex networks [cite: 10, 35].
3.  **Uplifted H-Eigenvector Centrality (UHEC)**: Specifically used for non-uniform hypergraphs (where edges connect varying numbers of nodes) by utilizing artificially weighted adjacency tensors with deep combinatorial adjustments, yielding highly robust and strictly order-consistent rankings [cite: 34].

### Higher-Order Markov Chains

In a classical, first-order Markov chain, a simple transition probability matrix dictates the state evolution. However, in an $m$-th order Markov chain, the exact probability of transitioning to a future state depends jointly and non-linearly on the $m-1$ previous sequential states [cite: 5, 14]. This process is naturally governed by a massive transition probability tensor, which is inherently nonnegative and stochastically normalized across specific array dimensions. The eventual stationary probability distribution of such a complex higher-order Markov system is derived directly by calculating all nonnegative Z-eigenvectors or H-eigenvectors of the transition tensor [cite: 14]. The Perron-Frobenius tensor extension provides the absolute necessary theoretical guarantee that such a stationary distribution actually exists and is stable [cite: 5].

### Solid Mechanics and the Elasticity Tensor

In advanced nonlinear solid mechanics and materials science, the **strong ellipticity condition** is a vital mathematical criterion ensuring the physical stability and physical realism of a material's internal deformation [cite: 15]. This strict condition is directly evaluated using the elasticity tensor, which is a fourth-order real tensor.
The strong ellipticity condition holds mathematically if and only if the absolute smallest **M-eigenvalue** of the elasticity tensor is strictly positive [cite: 15]. If this condition holds true, the elasticity tensor is classified as rank-one positive definite. Interestingly, the elasticity tensor is mathematically rank-one positive definite if and only if its absolute smallest **Z-eigenvalue** is positive [cite: 15]. By systematically converting physical stability conditions into precise tensor eigenvalue problems, material engineers can utilize semidefinite relaxation methods to rigorously certify and validate material deformation models.

### Quantum Entanglement

In quantum physics, the state of a complex multi-partite system is described comprehensively by a density tensor. Determining whether a specific quantum state is deeply entangled or completely separable involves rigorously analyzing the positivity of this high-order tensor [cite: 15]. The real rectangular tensors and partially symmetric tensors appearing in these quantum entanglement problems are evaluated using generalizations of the Perron-Frobenius theorem to determine their largest singular values, which serve as a mathematical proxy for the degree of entanglement [cite: 5, 15].

## Further Extensions and Generalizations

The scope of the Perron-Frobenius tensor extension is continuously expanding, easily transcending the boundaries of basic square, purely non-negative tensors.

**Rectangular Tensors:** 
Not all multi-way data arrays possess equal, symmetrical dimensions across all structural modes. For real, partially symmetric rectangular tensors, generalized singular values rather than eigenvalues are the primary objects of study [cite: 15]. A highly generalized version of the weak Perron-Frobenius theorem has been successfully mathematically proven for nonnegative rectangular tensors under suitably relaxed topological conditions. Algorithms that are conceptually identical to the NQZ algorithm have been deployed and definitively proven convergent to accurately calculate the largest singular value of irreducible nonnegative rectangular tensors [cite: 15].

**Tensors with Negative Entries (Perron-Frobenius Splitting):**
Perhaps most impressively, recent research has extended the classical Perron-Frobenius theory to multi-way tensors that contain a mixture of *negative* entries [cite: 36]. Under strict bounding conditions and sufficient topological structure, the existence of a Perron-Frobenius eigenpair can still be firmly established for these mixed-sign tensors. This theoretical breakthrough directly facilitates the advanced numerical technique of "Perron-Frobenius splitting" of tensors. Splitting methods are standard numerical linear algebra techniques (like Jacobi or standard Gauss-Seidel splitting) used to iteratively solve massive systems of equations. By generalizing regular and weak regular tensor splittings, complex multi-linear systems can be solved efficiently even when the operating tensor is not strictly, perfectly non-negative [cite: 36].

## Conclusion

The mathematical transition from the classical matrix Perron-Frobenius theorem to the higher-order tensor Perron-Frobenius theorem represents a monumental, paradigm-shifting leap in multilinear algebra. By meticulously defining highly specific classes of nonnegative tensors—ranging carefully from weakly irreducible to essentially positive—mathematicians have crafted a mathematically rigorous framework that perfectly mirrors, yet profoundly deepens, classical spectral theory. The intricate differences, such as the potential lack of absolute simplicity for the dominant eigenvalue and the behavioral divergence between projective H-eigenvectors and spherical Z-eigenvectors, highlight the rich mathematical complexity of nonlinear tensor mapping. Supported by highly sophisticated algorithms like NQZ and NNI, and unified elegantly by the geometric perspective of the Hilbert projective metric and multi-homogeneous mappings, this theoretical extension now serves as the absolute bedrock for modern applications in spectral hypergraph theory, advanced probability, max algebra systems, and quantum physics. As computational capacity grows, the tensor Perron-Frobenius extension will undoubtedly continue to unlock deeper mathematical understandings of complex, high-dimensional polyadic systems across the entirety of the computational sciences.

**Sources:**
1. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb820E_Sz5ufAEw_UbidQ0PUa9o_hycecOilNSiZEzx43x-45trm5zj4v-XmLSne417kzRonYvwkTN0Ddn_cu_Paud3bdt7SlSp9ydJ20u5CvRz7w-HlVQS6oPXBDSyQuDft5B_c2su4ONcps50OI=)
2. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRLoLsPZYYwZeT91MAs3VLF0Ks4N1di3HbHu7s81Vz00zgcWKHpxvPC6McSzobfQ36CRjXjQk56JebwUV5WoNBqNpVFs3bRFMORYYC9LSON4r6Ep7GGkZA7kcW3riRXi6IVCxO8-8DNZg=)
3. [m-hikari.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlVlM6LSQFOjXfI7-HB--WvVbPa7MyHYl-kO2BBR6X-FM2lNec_sCppIID5_cQQqqk0GHoeMxfJ6SUxF5n8gRKBNl3m5BTja7jCwkXaPB-WAkaVP1SYUtMO3l1YAzNg2DANqbOOI0d3JuZcBJRh0SdaGvuEwTurZh9xCgj1GqdvA8=)
4. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGx9o0zTc58qlBvpg6SliIchtj4zdyM9LlwLszNFDtWj6CIoiK1cp41m6Hi30j0KSKZm9TCa_glIN79LhZYPaagsPv4qSbGT_QB1TZ-fBWVVDi8p8nxoe6S9ZqvpePi8pL7AIVd-JeMHQmQZxn8qOT_-LrEr28uM9rwQLuRcqv586pAStSaYV7c-TSGgCqnlaytRgVbIAxrgu3NjWazd8DKY8E6-XAlqnCc10XG8NaghozaXb7H4ISIWWKskCUc3UMlwaSh6NIP_gzY8m-E2GgWG4jMY73a40_au1HN)
5. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7fizpGBwJJUZtsEF-yILROtnKX-96ssPKqPQjPLvc5Lk5c6N17T4Ld_NcaYZ-Tz8SExmSbczJ-ORyXBI1yzYjA-LAGOHqIMTSxHhPSUbbRGjLJEKrugT81hnksqFOf45950-5yJU1xGcxilf34b2v6ea1gkPP5A==)
6. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLRgPTqyP6hiXLI8z2vbjfIy0DuPdzppJ6CZswOpFYP_ja6TuPYkUNfu124BsQEIrrPoAAgbujkLI1pMguRFagHleUZOPWkz7IL0Gf5vYuE5RSdjgX312nV2lLxy9BSJJw2WsENfYZ8YiAH0I2ei5JqTolapX5YDIluAm-9YdTs3ZtiD-e1VnSujdk6ZDNLeOh_NwdAMmp4o5CdyCMNYP8Ailrm1II2oQ1fmPF5sSXqpaZ3qIjKvz_2JCTs4LS-qFTSlTBaXyilW61kJ5YJ8-eM2_3H6pM)
7. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8XUmYn3dohzh8NqaTjxQSbdjMqzWFRzyGukLnBt4e8t3bbI_bwAj-mLRX6_vmfi8p5QoTyxHDIDaJLB7hi4yuPQnV3HLfyLTDNC4TdGDEjfvVMYdmdwq_IX1MgsbPS_1tqQKHsrux9xJx6xxXd0ia5Fs=)
8. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR3drjFFodZwsMU18qG_7vm11dMqGD0jrHgeLQrm4vx839wT4MEopGpZdDbs4Nmvy0I2PQRsppR4c3Waa_Jo-pg2tojEPoa4KKsDi8HiRNoknt5QsT68sH0CRhArSSjQ8qYeC4iSo6T6aN2tQGLImIEfbrVUKqEjrzf8ypNH5v)
9. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3szbM-ehwUADNr1nqnrF1jvVAtTjvR6kov1WqlpTiCT5qT6wHdzJUhgS9XvJ-9tltq6v5di8wlLHp4KpdeUtyJ2hA_Lz26tPL33oFNNSqKdUqSh9ofg2rDUEz_RJPdS95ksmGXjmT_w==)
10. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_hzAfICk1lgRXLmx95Z2XN0dru1D0B1me3aB0nNnbCpBoYRUWqjzaEGN462Bi8JoWTNucKinXlxsCC6TBPvKqUhByPojwWZacpfHwfkIVBSKCvAbRRqTj_7ZZrK33TzmyjFtI1ZQAhf67ZxH_Gof9ruk=)
11. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmvQQBz3DSF_dl3zamg9ylDmRvpAnakElYpvgoU92A_pcALXQ1RGUPA_T41xFJR-bNRQtDY3dXtxHObCtBa3Uqac91RovHzlubRs-GPBBcgkTrqJ5FDkQUPedXs_s_jh_qRzccBe4=)
12. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuqyXBlDtLRiC6fzGRI1XqFENu8kB_g4vCnSvbPuJ8BaavhhvghpmREUv7c2I11yXMhE2NUdknX4hsUqZ3ZQeLArQiX6gxQvdRgeYtcCVyivJ1kEagPXch7OXRw_eSD2Fr0E6dPeuYggLp8KXJy5Vf0hinSM9OadtLEIlj87gHMO8TeWVroN_ulO2NONUEFn-ugqDAN7vOT5gee3Lno2zBQrgLWf7TwKEwi8E-r7U6CWLN)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcleHMtD7S9KprpjK4iZPoCNi51u-Pvk9KCSWnzw4QrHJZAzqy43DWwXVZHbGHN-OjH8ljcj40sbH81PyzbWqirwT4Jh5vUSAGZsIXPlGXI0sDmx89fw==)
14. [cornell.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6gdOILQU-cNGEAB2XNkU6Vh58OHYtIGvRP14ykzVD_aQQuPFVayhiAfd7hvIClL39q2-X4IRSArSrp7366HWVH51SIgrd0p6IV4IH9xbSJiNB02fohSyzaeDnrpX9bIK5CO14GUPOay9-_PskUsFBHzh9Bw==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu6MB13H1fWbE3lS3ANaq4xou6ytwB39kCPbABREo7-2pkNDZOQv2nbgV3rHqmCv-LLPK5ki2wQnpozx8sOLn3ClY9Ebti5JhwWb82ujUFRctApJ4Ic6GsR2M2ZQUvK87tV959t__7eFsqnHr53SBFkbObKOUESteG2g8PDn_FLl5zjU47L-FVBr8JYTA7thmpxPfADGDzqtqcaqG4LV72Al65r8rIsJeVlqkHAOMa)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrQavjzNz6zLEbBfNnyGSzazI_Z1CCjbC5RkKRWoqVwcZ2QqsLe8b80yzICh2CB_ZPFxzSehMO5fiuZj75LiWNU1YEkBBmjHVyXmvUt3jys5fMj1tWB58TyAkA5BhlDC4It7q_1P7M78OfYn_ht2k2W67OkHCVR9umV5C0jxl23eIkWZ2IJdPyXNdF9MK-R4Nbq2MjB5Ox7Fw=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeWfIQ-bV3TtAOGrXSMd_HEqVOJRvoORI0sWW8bkQJ8COMzhdN47dSgrA6lfVC0ool40sFOJly5qel_0lNa51QMFjcWuKTYaP1dagDL8UYo1D6m0V_)
18. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUuSWslhF7wmVi1xkC69LgsSh-4ydrNsV75f0skq1M-SgAsseRHDu1RDbOUr_fXI3ovSHVEuXnTTkfsXWvx_o8_KMS4mKWUvFblVlI0hfcB-lnR2tV16d9Z1NLk2L1bDGaROpAp6mAMdRnOsMMQGhRnSJY3H0hleUzQg_cWx5s5G702v5jyHLBmYSDDVUl-ibImT8=)
19. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdAGlUirK207m3ow1_wtnXsjWqkKbe8obcDZEbjCtr5jKBRemqh9YvTDLmrQgrTSJU1pm9bmm2wxV0XF8o_KIAeFgiymvLrGSltMEfjrjoMaNBjOuCgMFTH9QIE8cdTAyyXvWzkkPxrA==)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGzJTcThBFjyqwvDuaJe9ILWROOYUBUKKSVEzoTwbDKEAH83GOERiR1k-FxMDj207vWWk-falViiF-TCq0almB_EWpOOxHySLMndS8X1N3KtPQIkYEGfrPN0phUTcVbMK7Dyd69vi0ifIhd7Ryu_sorFfXMZJlLrS_3zz-lVmrEclU4WSc71lM6HkWWFcpgtlfTiXqS-mg7rNt4UV7MLI0l7p9--SeeM4F8NHZ8TMYVY9Fx7V63w9FCxLqAy5uszFRPyAGMISyAUmFL2fESfmV)
21. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpUL9OHQQX5N9BVD2rmxrj0dJHCENTwOwu7QV_PxhXJty61uYbiqO1qehQLR-2gAEBGVonur9HrKoGnZdCIf_4Nlf_-ZscLtiOTIhuvy6ER4RV4fo3UY2wC6_et_C70FwLqOwdRaI=)
22. [uregina.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErRMfS9DDyFgq1B3eTwQ-ojZRhldoBGGUcRJWlgrG11a8efp1wCVIKxat-_o4SQEVXiSpFHbN03YzfuyR-SJ9gFqu8LSfL9coVtkY51MLQH5mkrYkGkKuzqnNJyg==)
23. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmtlRxO3FHv9LLOhgdAjIi_3JbYjDAD4vo3EuQfWQfVg3gMaLO-BH14S03m6O7HnRaSSVbB3akcYD23LGLMwAwRqM9Su8Xffcvb7gk_jGSypiLSc_cWQ7InaWyjoO2eVQoXg==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtqjlg0z2o6HfFGEB8DJyKqbm-cI-_QnMbVFUISIrnaDRQK_6kyyCJrPi_DIipc1SUZNQ4YrNhHNVXVdmFmFiVK8g8sXnZndAuT0-UEuooCT4Nf9D6LEK043KmUqpjUF24kKgESuw-aNV-_X2duqcwQJRPOcJefmFHgF7oaH2BnZPbvZBCQPJDcwm-GO-NPq1S25GhQzKWDfHsMF67z5AsWZIwaeiJ2EU0hu1Xs3JGUsKcJP9dvZk5zvapGg==)
25. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELH7_dXq1VK1of69gZbReD8kIorGautTFUcPsB4NsiiKePhgMraIk8OoX7JS-r3Fg0WqTJT5WbgFizpXynhq5q_cdHAy2SIZmWF5QZm7lyNC6CJgKTivXyVCLdBB808hLJTsT-FW7KwyEBdNyM766Ttb9uOVzeo9SYZX_qAhY6-K5TmW30AghY83yOVvV2AvpLKzmfb69Q_UG-kmFO55QuIIxd9_aU0TfFO95eFF7mMskb2K_4gyilzUrZWrpTCj5W6taSLtP-mNdGM9h7mMJVHVX1HTvnE0j9fAlYVg==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEC9ZdcvMGcu4w4K0oUiObvPYvYmqMmO7PeXm9VlMJg89ZJWTuwfCiRrGrdUaj0m9mPKua4zEYWaN3qaFORTW_nrz0iPmfmrVE--pWLgIwRbB4livFUGQRfv8kBwLMvLBHJpQWP8XM9dmZNJJXo1X7FnfCJBywefxnn-DIT2vyGRH5BFO9t62iidw2uqOAWRo1x2_k3CaMkUyyLFNwJ1l11w5vvZczryxPNMw==)
27. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEO6iOKsVfWgc-6UzSkLjF8_gWakEwCGC3OBHn41UZhrBFnioiGsjsdwR8r7rgPnF_rSAE2ambR9_ZLaLMLDjv4a5FKyfjVaFx8V7zc41QhSBxanMPY)
28. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJmAZd6HirD76LT2eCc9MbcYyPgeHstHKwLa2PMXDfFdu8RRj0wbKCrE4Xaoo0s06xr8YJnpa_USD2yrfNXzB1dd6OftobzvwYQxe-gYerLwgRR5jo3WxnTmkLisfBnPsgtQU=)
29. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUPdWnrGEtQDjEQ17E09ycO7-rwTTyq6Kqb3CbO6snvlaiDsrXoen0CG0Ttl5BUku8N7ZbZMmLYSPXMGa7IOI_WRM1IA162L2gDlsa95-b5a_VF3qWkY0qdAQ1Xj6W_TkmVTwM5aa-4PAokeFCTqJTzXdtnEM6y0iB-tY=)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPHDM1PfyehEXPbo1pytgNuvRMvpJffEVZvemeOk5dJiSiBw70dFQuey6I9Lcl2dqKiq7-SjLL97vURsc1E5F6mySUEYwWE78Pm-JatBsx-qgGo84kPA==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgsQb17GrRE3JDWeKBxwmkTxgE0DZBd_O5AGp5cBBVDnzsEJyJSSFy3hOFJo5YNBw3p9Cjw-5hE8z8W8o6Ib0_MX2oacxOFKoV5qOZQTcPGSSQXEYV_w==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkSRhK1nUk1HUBxEF022f1FebRxb-fcI0FYliVgGwJ5vQQGWG7OkmhaltcR73gLoaBDjY0JJfc6jj1yi-ZiI3Ntq49Vz4k3883y9amKlYwau-E0x2kEQ==)
33. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxnQ9lmTAYr7QFTMgqSuo8r9NDoUtQHotjKhdu7d5LlFGXatHJ-9ekWKKHf_INtDpPypoWuRAeSMJ2TLAdflYeBBLWeCpeEOtIRV09B6qfAUX5PDLYbEz1k8RsJlh7lg==)
34. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5BCtf84vd-aV3Zi6xceeJYIZUOpIxKgsmWZ-M615xipD0732lgFoqbJv6rYgSz5mxRuhDwfUFrGPwK4d7ygTdPHoxC0fTlaECQYxHVYYd0vC3NL7MBFVWt21BeCm8Gz7d4gFf5nT-vIoQEpiuuffFlZf-FQIo43w=)
35. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW9ZgDmmSth_suBtWBhniUTGsFFL5ykOMPaD1gsdD9ily5_CZyOF8XX-AFCJl0KDKEpc0CE8kroBmuRqgqkfx_tgGwSp_jXXoh8pWgW7sMEgUDOOQyucH0izaQ60OOLMl9Y18=)
36. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfG6Rckvk93b9dXwLF8IyRozMvp3ZFmAjiOawY-8lZyCrYeZoWVpwcvq993c1Xn4TsBsEfXxRi9jfqGl5ptJirFwlqbveA4-jMjcvBOyRovy91I1j_53uJS59-vTPasYrrtbyeP680JYft6xhY1H2G9eA-rzKuCQ==)


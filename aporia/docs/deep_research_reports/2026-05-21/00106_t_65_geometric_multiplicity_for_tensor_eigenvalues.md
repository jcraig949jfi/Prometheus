# T#65 Geometric multiplicity for tensor eigenvalues

**Pythia queue id:** 106
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdlUjRQYXVXd0Q1UFZfdU1QMHVqVGtBcxIXZVI0UGF1V3dENVBWX3VNUDB1alRrQXM
**Elapsed:** 312s
**Completed at:** 2026-05-21T15:07:29.935372+00:00

---

# Multiplicities of Tensor Eigenvalues: An Exhaustive Analysis of Theorem 6.5 and Geometric Multiplicity

**Key Points:**
*   **Tensor Generalization:** The spectral theory of tensors extends the classical eigenvalue and eigenvector concepts from square matrices (second-order tensors) to higher-order multilinear arrays.
*   **Non-Linearity:** Unlike matrix eigenspaces, which form linear subspaces, tensor eigenvarieties are generally non-linear due to the underlying multilinear homogeneous polynomial equations.
*   **Multiplicity Divergence:** The definitions of algebraic multiplicity and geometric multiplicity for tensors exhibit significantly more complex behaviors than their matrix counterparts, especially regarding their invariance under orthogonal group actions.
*   **Theorem 6.5:** For a generic tensor, both the algebraic and geometric multiplicities of any given eigenvalue are exactly 1, and each eigenvalue is associated with a unique eigenvector (up to scaling).
*   **The General Conjecture:** Research suggests that for an $m$-th order $n$-dimensional tensor, the algebraic multiplicity $am(\lambda)$ is bound by the geometric multiplicity $gm(\lambda)$ via the inequality $am(\lambda) \ge gm(\lambda)(m-1)^{gm(\lambda)-1}$, a generalization of the classical matrix inequality $am \ge gm$.

While classical matrix algebra relies on the predictable linear behavior of eigenspaces, tensor spectral theory ventures into the realm of algebraic geometry. The study of tensor eigenvalues implies grappling with complex systems of multivariate polynomials. Consequently, the relationship between algebraic multiplicity (the multiplicity of an eigenvalue as a root of the characteristic polynomial) and geometric multiplicity (the geometric dimension of the set of eigenvectors) is not straightforward. Theorem 6.5 (often abbreviated as T#65 in specific literature contexts) from Hu and Ye (2016) serves as a foundational result in classifying these multiplicities for "generic" tensors. The evidence leans toward a unified geometric-algebraic inequality that bridges multilinear algebra with algebraic geometry, though proving this for all conceivable degenerate tensor classes remains an active frontier in modern mathematics. 

## Introduction to Tensor Spectral Theory

The study of matrices—second-order tensors—forms the bedrock of linear algebra, quantum mechanics, and systems theory. In matrix theory, the concepts of eigenvalues and eigenvectors describe invariant directions under linear transformations. However, in higher-order multidimensional arrays, known as tensors, transformations are strictly multilinear. The spectral theory of tensors was independently pioneered by Lim and Qi in 2005, introducing the concepts of tensor eigenvalues to tackle higher-order uniform hypergraphs, magnetic resonance imaging, and non-linear optimization [cite: 1, 2].

A tensor $A$ of order $m$ and dimension $n$ over the complex field $\mathbb{C}$ is a multidimensional array composed of $n^m$ entries, denoted $A = (a_{i_1 i_2 \dots i_m})$, where $i_j \in [n] = \{1, 2, \dots, n\}$ for all $j \in [m]$ [cite: 1, 2]. 

Given a vector $x \in \mathbb{C}^n$, the product $Ax^{m-1}$ is defined as a vector in $\mathbb{C}^n$ whose $i$-th component is given by the multilinear form:
\[ (Ax^{m-1})_i = \sum_{i_2, \dots, i_m = 1}^n a_{i i_2 \dots i_m} x_{i_2} \dots x_{i_m} \]
An eigenvalue $\lambda \in \mathbb{C}$ and its corresponding eigenvector $x \in \mathbb{C}^n \setminus \{0\}$ are defined as satisfying the system of homogeneous polynomial equations:
\[ Ax^{m-1} = \lambda x^{[m-1]} \]
where $x^{[m-1]}$ is a vector whose $i$-th component is $x_i^{m-1}$ [cite: 1, 3]. If an eigenvalue has an eigenvector strictly within the real space $\mathbb{R}^n$, it is referred to as an H-eigenvalue (with an H-eigenvector), and specifically as a Z-eigenvalue under certain symmetric conditions [cite: 3, 4]. 

## Multiplicities in Classical Matrix Theory

To fully grasp the magnitude of the tensor multiplicity problem, one must first review the classical matrix counterpart ($m=2$). 

For an $n \times n$ matrix $M$, the algebraic multiplicity, denoted $am(\lambda)$, is defined as the multiplicity of $\lambda$ as a root of the matrix's characteristic polynomial, $p(\lambda) = \det(M - \lambda I)$ [cite: 5, 6, 7]. If the characteristic polynomial is factored into linear terms $\prod_{i=1}^d (\lambda - \lambda_i)^{\mu_A(\lambda_i)}$, the largest integer $k$ such that $(\lambda - \lambda_i)^k$ divides the polynomial is the algebraic multiplicity [cite: 5, 8].

The geometric multiplicity, $gm(\lambda)$, is the dimension of the eigenspace $E_\lambda$, which is the kernel of the linear transformation $M - \lambda I$ [cite: 5]. Because the eigenspace is governed by linear equations, it forms a linear subspace of $\mathbb{C}^n$, meaning it is closed under vector addition and scalar multiplication [cite: 5, 6]. 

A foundational theorem in linear algebra states that the geometric multiplicity can never exceed the algebraic multiplicity:
\[ 1 \le gm(\lambda) \le am(\lambda) \le n \]
When $gm(\lambda) < am(\lambda)$, the eigenvalue is termed **defective**, and the matrix cannot be diagonalized into a basis of purely linearly independent eigenvectors (requiring generalized eigenvectors and Jordan canonical form) [cite: 6, 8]. Moreover, these multiplicities are absolutely invariant under orthogonal similarity transformations ($M \mapsto P M P^{-1}$), meaning rotating the coordinate system does not fundamentally alter the root structure or the dimension of the eigenspaces.

## Formulating Tensor Multiplicities

The transition from $m=2$ to $m \ge 3$ shatters the linearity that guarantees eigenspaces are vector subspaces. Because the system $Ax^{m-1} = \lambda x^{[m-1]}$ consists of polynomials of degree $m-1$, the set of solutions forms an algebraic variety rather than a linear space [cite: 9].

### The Tensor Characteristic Polynomial
The determinant of a tensor is formalized through multivariate resultants [cite: 1, 2]. The characteristic polynomial of a tensor $A$, denoted $\phi_A(\lambda)$, is defined as the resultant of the $n$ homogeneous polynomials $f_i(x) = (Ax^{m-1})_i - \lambda x_i^{m-1}$ [cite: 1, 2]. 
\[ \phi_A(\lambda) = \text{Res}(f_1, f_2, \dots, f_n) \]
The eigenvalues of the tensor $A$ are exactly the roots of this characteristic polynomial, which is a monic polynomial whose degree is determined solely by the order $m$ and dimension $n$ of the tensor [cite: 9].

The **algebraic multiplicity**, $am(\lambda)$, of a tensor eigenvalue is defined as the multiplicity of $\lambda$ as a root of this characteristic polynomial $\phi_A(\lambda)$ [cite: 9]. To emphasize that $\lambda$ is an eigenvalue of $A$, this is occasionally denoted $am(\lambda, A)$ [cite: 1, 3].

### The Geometric Multiplicity and Eigenvarieties
Because the eigenvalue equation system is non-linear for $m \ge 3$, the set of all eigenvectors associated with $\lambda$, combined with the zero vector, defines an affine algebraic variety in $\mathbb{C}^n$, denoted $V(\lambda)$ [cite: 7, 9]. Sometimes this is studied in the projective space $\mathbb{P}^{n-1}$ to account for the scale invariance of eigenvectors, yielding the projective eigenvariety [cite: 1, 3].

The **geometric multiplicity**, $gm(\lambda)$, of a tensor eigenvalue $\lambda$ is defined as the geometric dimension of the eigenvariety $V(\lambda) \subseteq \mathbb{C}^n$ [cite: 9]. 

Since $V(\lambda)$ is defined by polynomials of degree $m-1 \ge 2$, the eigenvariety is, in general, not a linear subspace [cite: 7, 9]. Furthermore, a significant discrepancy occurs when considering the underlying field. In matrices, the geometric multiplicity of an eigenvalue over $\mathbb{R}$ is identical to that over $\mathbb{C}$. However, for higher-order tensors, the geometric multiplicity over $\mathbb{R}$ could be strictly smaller than its dimension over $\mathbb{C}$, or even entirely empty, highlighting the profound impact of non-linearity [cite: 9].

| Property | Matrices ($m=2$) | Tensors ($m \ge 3$) |
| :--- | :--- | :--- |
| **Characteristic Equation** | $\det(M - \lambda I) = 0$ | $\text{Res}(Ax^{m-1} - \lambda x^{[m-1]}) = 0$ |
| **Eigenvector Set** | Linear Subspace (Eigenspace) | Algebraic Variety (Eigenvariety) |
| **Algebraic Multiplicity ($am$)** | Root multiplicity of characteristic polynomial | Root multiplicity of resultant polynomial |
| **Geometric Multiplicity ($gm$)** | Dimension of linear kernel | Dimension of affine algebraic variety |
| **Invariance under Orthogonal Action**| Both $am$ and $gm$ are invariant | Only $gm(0)$ is invariant; $am$ can change |
| **Field Dependence ($\mathbb{R}$ vs $\mathbb{C}$)**| Dimension is equivalent | Dimension over $\mathbb{R}$ may be strictly smaller |

## Invariance Under Orthogonal Transformations

One of the most surprising mathematical discoveries in tensor spectral theory—and the core difficulty in studying the relationship between $am(\lambda)$ and $gm(\lambda)$—is their behavior under orthogonal linear group actions.

In linear algebra, changing the coordinate basis via an orthogonal matrix $P \in O(n)$ preserves the spectrum: $\det(P M P^T - \lambda I) = \det(M - \lambda I)$. Thus, both the algebraic and geometric multiplicities remain invariant.

For a tensor $A$, an orthogonal transformation $P$ acts on all modes of the tensor, producing a new tensor $P \cdot A$. Research by Hu and Ye demonstrates that the algebraic multiplicity of a non-zero eigenvalue *could change* along the orbit of tensors generated by the orthogonal linear group action [cite: 9]. The characteristic polynomial of $P \cdot A$ is not necessarily identical to the characteristic polynomial of $A$ shifted by $\lambda$.

However, Hu and Ye also proved that the geometric multiplicity of the **zero eigenvalue**, $gm(0)$, is strictly invariant under this action [cite: 9]. 
*Proof Sketch:* The eigenvariety of the tensor $P \cdot A$ for the eigenvalue zero, denoted $V_{P \cdot A}(0)$, is exactly the spatial transformation $P V_A(0)$ of the original eigenvariety $V_A(0)$ for the eigenvalue zero. Because the geometric dimension and the number of irreducible components of an algebraic variety are topological invariants under coordinate changes (such as those represented by $P$), the dimension remains constant. Consequently, $gm(0)$ is an orthogonal invariant [cite: 9].

The divergence between the invariance of $gm$ and the variance of $am$ under orthogonal actions forms the primary hurdle in establishing universal rules mapping algebraic to geometric multiplicities in multilinear algebra [cite: 9, 10].

## Theorem 6.5: The Generic Tensor

Because pathological or highly symmetric tensors exhibit complex multiplicities, the study of "generic" tensors provides the baseline for expected behavior. In algebraic geometry, a property holds for a "generic" element of a space if it holds on a dense, Zariski-open subset of that space. Essentially, if one were to pick a tensor completely at random from the space of all possible tensors $\mathcal{T}(\mathbb{C}^n, m)$, it would almost certainly be generic.

**Theorem 6.5 (Generic Tensor)** from Hu and Ye (2016) rigorously establishes the multiplicities for such tensors:
*Let tensor $T \in \mathcal{T}(\mathbb{C}^n, m)$ be generic. Then, $am(\lambda) = gm(\lambda) = 1$ for all $\lambda \in \sigma(T)$* [cite: 9].

### Derivation and Supporting Lemmas
The proof of Theorem 6.5 relies on heavily geometric arguments [cite: 9]:
1.  **Algebraic Multiplicity**: For a generic tensor, the characteristic polynomial $\phi_T(\lambda)$, when treated symbolically, is a monic and irreducible polynomial. Consequently, the resultant polynomial possesses no repeated roots. Each eigenvalue $\lambda$ appears exactly once as a root, meaning $am(\lambda) = 1$ [cite: 9].
2.  **Geometric Multiplicity**: For a generic tensor, the homogeneous multilinear system defining the eigenvectors creates a one-dimensional variety (a curve radiating from the origin) in $\mathbb{C}^n$. Because this variety can be broken down into a disjoint union of distinct eigenvarieties corresponding to each eigenvalue, the dimension of any specific $V(\lambda)$ is exactly 1. Thus, $gm(\lambda) = 1$ [cite: 9].
3.  **Eigenvector Uniqueness**: Applying the "shape lemma" from computational algebraic geometry, it is shown that for a generic tensor, the eigenvariety $V(\lambda)$ is fully irreducible. This irreducibility dictates that each eigenvalue corresponds to a uniquely defined eigenvector (up to scalar multiplication) [cite: 9].

By confirming that $am(\lambda) = 1$ and $gm(\lambda) = 1$, Theorem 6.5 acts as a higher-order analogue to the matrix fact that almost all matrices have distinct eigenvalues with one-dimensional eigenspaces. 

## The Multiplicity Inequality Conjecture

Given the matrix inequality $am \ge gm$, a natural question arises: what is the corresponding boundary for $m$-th order tensors? 

Hu and Ye formulated a broad conjecture that generalizes the classical matrix result, factoring in the degree of the polynomials (determined by the order $m$). In general, they suggest the following relationship bounds the algebraic multiplicity from below [cite: 9, 11]:
\[ am(\lambda) \ge gm(\lambda)(m-1)^{gm(\lambda)-1} \]

When evaluated at $m=2$ (matrices), the term $(2-1)^{gm(\lambda)-1}$ collapses to 1, gracefully reducing the inequality to the classical $am(\lambda) \ge gm(\lambda)$ [cite: 7, 9, 11].

### The Deep Geometric Conjecture
A more detailed and profound version of this conjecture relates to the irreducible components of the eigenvariety $V(\lambda)$. If $V(\lambda)$ can be decomposed into $\kappa$ irreducible components $V_1, V_2, \dots, V_\kappa$, the extended conjecture posits [cite: 1, 9]:
\[ am(\lambda) \ge \sum_{i=1}^\kappa \dim(V_i)(m-1)^{\dim(V_i)-1} \]

Since the geometric multiplicity $gm(\lambda)$ is defined as the maximum dimension among all its irreducible components (i.e., $\dim(V_i) = gm(\lambda)$ for at least one $i$), this summation-based inequality strictly implies the simpler version $am(\lambda) \ge gm(\lambda)(m-1)^{gm(\lambda)-1}$ [cite: 1, 9].

### Proven Cases
While the inequality remains a conjecture for entirely arbitrary degenerate tensors, it has been rigorously proven in several critical scenarios:
1.  **Generic Tensors:** As established by Theorem 6.5, generic tensors yield $am(\lambda) = 1$ and $gm(\lambda) = 1$. Substituting this into the inequality gives $1 \ge 1 \cdot (m-1)^0 = 1$, which trivially satisfies the relationship [cite: 9].
2.  **Identity Tensors:** For an identity tensor $I \in \mathcal{T}(\mathbb{C}^n, m)$ (where $I_{i_1 i_2 \dots i_m} = 1$ if $i_1 = i_2 = \dots = i_m$ and 0 otherwise), the algebraic multiplicity for the only eigenvalue $\mu$ is known to be $n(m-1)^{n-1}$. Since $gm(\mu) = n$, the formula evaluates to $n(m-1)^{n-1} \ge n(m-1)^{n-1}$, rendering the bound exactly tight [cite: 1, 9].
3.  **Linear Subspaces:** The conjecture has been verified as true for cases where the eigenvariety contains a linear subspace of dimension $gm(\lambda)$ in coordinate form [cite: 9, 10, 11].
4.  **Low-Rank Symmetric Tensors:** For tensors of specific low ranks displaying symmetry, the inequality holds [cite: 7].

## Applications in Spectral Hypergraph Theory

The abstract multilinear algebra surrounding tensor geometric multiplicity has found profound concrete applications in spectral hypergraph theory. In classical graph theory, the adjacency matrix and Laplacian matrix dictate graph invariants. In hypergraphs, where an edge can connect more than two vertices, these matrices are replaced by tensors.

A $k$-uniform hypergraph $H = (V, E)$ on $n$ vertices is modeled using a $k$-th order $n$-dimensional adjacency tensor $A(H)$, where the entry $a_{i_1 i_2 \dots i_k}$ is $\frac{1}{(k-1)!}$ if the vertices form an edge, and 0 otherwise [cite: 3, 12]. The Laplacian tensor $L(H)$ and the signless Laplacian tensor $Q(H)$ are defined utilizing a degree tensor $D$, such that $L(H) = D - A(H)$ and $Q(H) = D + A(H)$ [cite: 2, 3]. 

### Perron-Frobenius Theory for Tensors
The Perron-Frobenius theorem for matrices states that a nonnegative irreducible matrix has a unique largest real eigenvalue (spectral radius) equipped with a strictly positive eigenvector. This has been elegantly generalized to tensors.

If $A$ is a nonnegative weakly irreducible tensor of order $m$ and dimension $n$ with spectral radius $\rho(A)$:
1.  $\rho(A)$ is a unique H++ eigenvalue (having a strictly positive eigenvector), known as the Perron vector [cite: 1, 2].
2.  If $x$ is an eigenvector associated with any eigenvalue whose modulus equals $\rho(A)$, then the absolute value vector $|x|$ is exactly the Perron vector [cite: 1].

### Confirming the Conjecture for Hypergraphs
Researchers have actively used hypergraph frameworks to test the Hu-Ye multiplicity conjecture. Fan (2024) and others investigated the projective eigenvarieties of connected uniform hypergraphs. For a connected $k$-uniform hypergraph, the projective eigenvariety $V_\lambda(A(H))$ associated with the spectral radius $|\lambda| = \rho(A(H))$ has been extensively mapped [cite: 1, 3].

Crucially, it has been proven that if $A$ is a nonnegative weakly irreducible tensor with spectral radius $\rho$, then the algebraic multiplicity satisfies $am(\lambda) \ge |V_\lambda(A)|$ for all eigenvalues with modulus $\rho$ [cite: 1, 3]. This explicitly confirms the equality case of the Hu-Ye conjecture for the adjacency and Laplacian tensors of several classes of hypergraphs [cite: 1]. Furthermore, for loose hyperpaths, researchers have shown that the algebraic multiplicity of the zero Laplacian eigenvalue ($am(0, L(H))$) is precisely characterized by the multiplicities of points in the affine variety, proving that it is never smaller than the number of irreducible components of the eigenvariety [cite: 3, 12].

## Computational Aspects and Degeneracy

Computing the characteristic polynomial and extracting algebraic and geometric multiplicities for large tensors is notoriously NP-hard [cite: 13]. While matrices allow for rapid eigenvalue computation via standard $O(n^3)$ algorithms (e.g., QR algorithm), tensor characteristic polynomials require the calculation of massive multivariate resultants. 

For a symmetric hypermatrix (where entries are invariant under permutations of their indices), symmetric hyperdeterminants are deployed [cite: 4, 12]. The eigenvalues form the roots of a one-dimensional polynomial derived from this symmetric hyperdeterminant [cite: 4]. Non-degeneracy plays a large role here; for almost all symmetric tensors in $\mathbb{R}^{n \times n \dots \times n}$, each Z-eigenvector is non-degenerate, mapping strictly to nonsingular solutions of the underlying gradient equations [cite: 14]. This links back to Theorem 6.5, ensuring that the "generic" state (which prevents multiplicity explosion) is the mathematical default, keeping computational models stable. 

If a tensor deviates from the generic state, the geometric multiplicity of an eigenvalue could increase. However, unlike matrices where defective eigenvalues mean missing eigenvectors (geometric < algebraic), tensor eigenvalues often possess complex affine components. An eigenvalue $\lambda$ might lack linearly independent vectors but possess a continuum of vectors defining a curve or surface in $\mathbb{C}^n$ [cite: 7, 9].

## Conclusion

The transition from matrix spectral theory to tensor spectral theory abandons the comfortable confines of linear subspaces for the complex geometries of algebraic varieties. The definitions of algebraic multiplicity ($am$) and geometric multiplicity ($gm$) for tensor eigenvalues beautifully generalize matrix theory but unearth new phenomena, such as field dependence, non-linearity of eigenspaces, and shifting invariances under orthogonal transformations.

Theorem 6.5 serves as the anchor point in this highly non-linear field, assuring us that for almost all tensors—the generic ones—the spectral structure is remarkably simple: $am(\lambda) = 1$ and $gm(\lambda) = 1$, with uniquely defined eigenvectors up to a scalar [cite: 9]. 

However, for non-generic tensors, the relationship is believed to obey the fundamental inequality $am(\lambda) \ge gm(\lambda)(m-1)^{gm(\lambda)-1}$. This formulation gracefully bridges the gap between the degree of the multilinear system and the dimensions of its solution spaces [cite: 9, 11]. Through active verification in the domains of weakly irreducible nonnegative tensors and spectral hypergraph theory, this conjecture is slowly transitioning from theoretical hypothesis to proven mathematical law, deepening our understanding of higher-order data structures, optimization, and multidimensional geometry [cite: 1, 3].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWHVE241YUzA0ksCp5MRGQNHqscSyprr7ZlE4e6q4S7Cchq6y7UY6sfWXiehsHRn4xLD9lkJ3g_WgO8PJStFGM_hrWOWf8FRn_XH41f09si9cf7yisGA==)
2. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpmqRcTT59Jt42lAnFEE5baDvFaYQcdJcd-Zcw6ei6FRsIPdy5dwqj7ybRUN9i3utZX3yRT_7AiJ7mu-hIerRnCmF5SEeLc5AmKMZVinYQYH0arIwObYz6_eeUCyTK4WRa7IB1cBmEGwZl-tFLoddx2bJr7GrdCLdIjA==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9d1_rIp_isVqHdR9Xq_MvVb1VI69S6Nk7-Lva0-yVoakxxoVOBLZN0tidMFmFgnmDYxlvdyUaiNcYXNmXt6bsUP9_DDw2peAXRhPm6nIhZwAReLwlGQ==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxBZGZWVwlK7zWiYF5CcLaSSkzQCuW0mtxjNJZGiF7g8_39qFWcxtBpk1CIzqntr5IB3K2wYmNIj9e-_EDouI3G_6k8EE60qwahciVxpWhCsjYb-fTv5e5adHcpyXU-gqJPW24kltDhpSgb0xRFUSac-mEpFSyvlCQhjiCDFgaUrhjBQi4-pQ4eSluaMEUrJMjaZ46jUWBt0I-iUi3zA==)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN2P4h2S3kO_mrWwDMOpuCxEkxF4oCVxMUYy2MH6pEYxU9RoWSJfW7Rvn9R25yh7Suc_a7yFjLg7tX3F8eUx_ji90HBgnMNlGslFcVvIXqW-dKXS1pdSEGN0eXFthrILRbpYwHew-BYBdigfcl4SOD)
6. [statlect.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_1IspHs3q8LPd6laJzTAOanyNHb2VZg3IIx4j3fN8LBS5DUivcYiwtLgPO8hhHPP_DInGW1oeVl5ToiE_wtI-fKHWGyIUIDWuUqKGF91SRNvfiv6BTnWn5lBn8SYaSsxPJJdvl2aYhu-Z_-HCQc7zCkhOVj1ere6NsVzA6mBUfv7xa8GQw6_8-PIpYhBXsnfU)
7. [ilasic.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoNJHoFGN9ZtZlvGzpQ6JyaGsAnhrLsEoBkTYuwoMYn--Enst668jCjEtJdKylgH4wu9mlr-LJV9AyqsIxJJ8QCmZU5KGjaC3dRatTSgawykdfODKrjnhH8eCbHVdiysTa5AeFioicDpjVucae)
8. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgAon1kU3b2WgAipB0byqgfAlCswH7FRomEU_3zwZVSpOGj614d2TnK0Wgd-FH73I73Xu-Kz7VHHvcqwKBTC4fgFbswwJYicLUrSrgqlfG-ZzD7KAF8jW9T_xtygcV_dPcSdIJgAt9dH2k6aZAZRlKEqF5DoUWcL0jaA4J)
9. [intlpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy_bOY_h47qybp9CQwqwuY4uN0XM4WU5xrcxtAtSf2WqF0Qx9NXIoUGRIkDAa5UVzxQf2GbLhaz8kG8dNqGJrHEGlxwf7TKb6sP-0xPM3oy8CXaqhYJFHLrucAHdm4uvgss3y_cB_oW7S9DBbDKWNXOrq8ztG8FNgOzoXy30FMy8DyJQhgPnRuau9Xzd0RNDrC6JKl6knJTbHZ86OJAZvX)
10. [intlpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5u7-5B5F_rOXdbyDp_friFlygBwpSQqRD199pYv91u2DdO5oCZU71t7FX6PERWa6O_fWeFciz3LUIPjQHQ1I5vSFV4_3fIFiBIuPXgCbOYwz4yxMKi1NjvJ6WP0LBI6DZOagU1V6P)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZj9Er2-0qjANavy8WliSeffy94GJqa30ROQJHT8xd_nrU9GIBwVGreM1fzatpZTTTfr1fQ8P1o5H2Q_Pd008UEpFiNFj5MFGxpiJVp56lvOVCpYWp)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8OM_GqLHyPGfgSo8kxo3YgAIOZUYmMsyUyQlgFg7-SaI21n2rF5qwfjg3lrer3GhgLKS7Er8rS9Xkq5FEPsCjicYQdkxaFempZYla6xCVGM2PyR7KLHMSzHH8T49uzZaWi5ts63xya3laEoNmlL91vwbCXsWfY-0gxpTYtzGyNLIqVCLb0NVroQiF1Atb9VRw66OVMM4=)
13. [sc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnAzbM7i_nXl1ymh2qRSNiUuy5U4JK2CLpWyOCF090vJG86ADK0TOwKwuqzXWOwYrqHcZyHm1CUbFzZuBm6ZQPBON8QcPeuosLi8RCgmrXi8MePu1jwRsv3R949LkBWxWv0UA7dUtZbJaFdsADjOy_iR9diNJilh2vN7fpX0SrWw==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKoDSSaXHA54t4x57c0f75DPAWdn7rKfGT5RHywSdM_e3L88SZDjB9LWyaXm0aXQRhD7FrQuQAFTltSF1LPs9oQRzYJ4oHvPSW1hXBoYucealZCPP69Q==)


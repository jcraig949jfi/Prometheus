# T#69 Positive-definiteness check for even-order tensors

**Pythia queue id:** 110
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdNQ0FQYXMyekJJM2xqTWNQMHZQZThBaxIXTUNBUGFzMnpCSTNsak1jUDB2UGU4QWs
**Elapsed:** 250s
**Completed at:** 2026-05-21T15:13:47.237755+00:00

---

# Positive-Definiteness Check for Even-Order Tensors: Mathematical Foundations, Methodologies, and Applications

**Key Points:**
*   **Fundamental Importance**: Checking the positive definiteness of even-order tensors is a critical task in applied mathematics. It directly corresponds to verifying whether a multivariable homogeneous polynomial is strictly positive for all non-zero inputs, a condition essential for proving the stability of autonomous nonlinear systems, assessing quantum vacuum stability, and analyzing magnetic resonance imaging (MRI) data.
*   **Inherent Intractability**: The problem is notoriously difficult. Research overwhelmingly confirms that for tensors of order greater than four and dimension greater than three, determining positive definiteness computationally is generally an NP-hard problem. 
*   **Eigenvalue Theories as a Solution**: To navigate this complexity, researchers have extended matrix eigenvalue theories to tensors. A symmetric even-order tensor is positive definite if and only if its real spectral values—specifically its H-eigenvalues or Z-eigenvalues—are strictly positive.
*   **Structural Classes**: Because of the general NP-hardness, much of the research focuses on specialized tensor classes. Diagonally dominant tensors, H-tensors, Cauchy tensors, and Pascal tensors provide practical, checkable sufficient conditions for positive definiteness.
*   **Computational Frameworks**: Advanced computational algorithms, particularly those relying on Sum of Squares (SOS) hierarchies, Semidefinite Programming (SDP) relaxations, and iterative eigenvalue bounding, offer polynomial-time approximations to verify positive definiteness when exact analytical methods are computationally unfeasible. 

The positive definiteness of higher-order mathematical structures like tensors might seem like a highly abstract problem, but it serves as the underlying backbone for many physical and engineering models. At its core, positive definiteness ensures that physical properties, such as energy, remain positive and well-behaved, preventing systems from collapsing or yielding impossible negative values. Because tensors generalize matrices into multidimensional arrays, determining their properties becomes exponentially more complex, a phenomenon mathematically designated as "NP-hard." Consequently, the academic and computational community relies on specific tensor structures (such as Cauchy and Pascal tensors) and approximation algorithms (like Sum of Squares relaxations) to reliably verify positive definiteness in practical, real-world applications.

***

## Introduction

Tensors are multi-indexed mathematical arrays that generalize scalars, vectors, and matrices to higher dimensions, playing an indispensable role in machine learning, signal processing, quantum physics, and materials science [cite: 1, 2]. A fundamental property that is frequently required in these applications is **positive definiteness**. 

Let \(\mathbb{R}^n\) be the \(n\)-dimensional real Euclidean space. An \(m\)-th order \(n\)-dimensional real tensor \(\mathcal{A} = (a_{i_1 i_2 \ldots i_m})\) consists of \(n^m\) entries in the real field \(\mathbb{R}\), where \(i_j \in \{1, 2, \ldots, n\}\) for all \(j = 1, \ldots, m\) [cite: 3, 4]. A tensor \(\mathcal{A}\) is defined as *symmetric* if its entries \(a_{i_1 i_2 \ldots i_m}\) remain invariant under any permutation of their indices [cite: 5]. 

An \(m\)-th order \(n\)-dimensional symmetric tensor \(\mathcal{A}\) defines a corresponding \(m\)-th degree homogeneous polynomial form \(f(x)\) with \(n\) variables, expressed as:
\[ f(x) = \mathcal{A}x^m = \sum_{i_1, i_2, \ldots, i_m = 1}^{n} a_{i_1 i_2 \ldots i_m} x_{i_1} x_{i_2} \cdots x_{i_m} \]
where \(x = (x_1, x_2, \ldots, x_n)^\top \in \mathbb{R}^n\) [cite: 6, 7]. 

A tensor \(\mathcal{A}\) is called **positive definite (PD)** if \(f(x) > 0\) for all non-zero vectors \(x \in \mathbb{R}^n\) [cite: 6, 7]. Correspondingly, it is **positive semi-definite (PSD)** if \(f(x) \geq 0\) for all \(x \in \mathbb{R}^n\) [cite: 7, 8]. The notion of positive definiteness is strictly well-defined only when the tensor order \(m\) is an even integer. This is consistent with the classical algebraic theory of homogeneous polynomials; a real polynomial of an odd degree cannot be strictly positive for all non-zero inputs because \(f(-x) = -f(x)\), meaning the function will inherently yield negative values for some vectors unless it is the trivial zero tensor [cite: 5, 9]. Therefore, whenever positive definiteness is discussed in the context of tensor properties or eigenvalue bounds, it is implicitly understood that \(m\) is an even number [cite: 5, 10].

Identifying the positive definiteness of a given multivariate homogeneous polynomial is known to be an **NP-hard** problem when the dimension \(n > 3\) and the order \(m \ge 4\) [cite: 6, 11]. Most tensor problems over the real field, including the determination of tensor eigenvalues, fall into this computationally intractable category [cite: 12, 13]. Consequently, the development of checkable sufficient conditions, algebraic relaxations, and structural specializations to verify the positive definiteness of even-order tensors forms a highly active and critical area of study in numerical multilinear algebra and polynomial optimization [cite: 14, 15].

## Spectral Theories for Positive Definiteness

The most robust theoretical mechanism for checking the positive definiteness of an even-order tensor relies on its spectral properties, specifically its eigenvalues. In 2005, Lim and Qi independently introduced the formal concepts of eigenvalues and eigenvectors for real symmetric tensors, motivated directly by the need to study positive definiteness in homogeneous polynomials [cite: 5, 10]. 

### H-Eigenvalues and Z-Eigenvalues

Qi (2005) systematically defined **H-eigenvalues** and **Z-eigenvalues** [cite: 16, 17]. For a real symmetric tensor \(\mathcal{A}\) and a vector \(x \in \mathbb{R}^n\), the notation \(\mathcal{A}x^{m-1}\) represents an \(n\)-dimensional vector whose \(i\)-th component is:
\[ (\mathcal{A}x^{m-1})_i = \sum_{i_2, \ldots, i_m = 1}^n a_{i i_2 \ldots i_m} x_{i_2} \cdots x_{i_m} \]

1. **H-eigenvalues**: A number \(\lambda \in \mathbb{R}\) is called an H-eigenvalue of \(\mathcal{A}\) if there exists a non-zero real vector \(x \in \mathbb{R}^n\) such that:
   \[ \mathcal{A}x^{m-1} = \lambda x^{[m-1]} \]
   where \(x^{[m-1]}\) is a vector with elements \(x_i^{m-1}\) [cite: 5, 9]. The corresponding vector \(x\) is called the H-eigenvector.
2. **Z-eigenvalues**: A number \(\lambda \in \mathbb{R}\) is called a Z-eigenvalue of \(\mathcal{A}\) if there exists a real vector \(x \in \mathbb{R}^n\) with a unit Euclidean norm (\(x^\top x = 1\)) such that:
   \[ \mathcal{A}x^{m-1} = \lambda x \]
   [cite: 18]. The corresponding vector \(x\) is called the Z-eigenvector.

According to the spectral theory of symmetric tensors, an even-order real symmetric tensor is positive definite if and only if all of its H-eigenvalues are strictly positive [cite: 14, 19]. Alternatively, the tensor is positive definite if and only if all of its Z-eigenvalues are strictly positive [cite: 18]. Similarly, the tensor is positive semi-definite if and only if it possesses no negative H-eigenvalues (or Z-eigenvalues) [cite: 8, 9]. While this provides an exact and necessary condition, the inherent NP-hardness of the problem renders the precise computation of the smallest H-eigenvalue or Z-eigenvalue practically impossible for large \(m\) and \(n\) [cite: 20, 21].

### M-Eigenvalues for Partially Symmetric Tensors

Beyond fully symmetric tensors, applied mechanics often utilizes **partially symmetric tensors**. For instance, an elasticity tensor \(\mathcal{C} = (c_{ijkl})\) of order four and dimension three satisfies partial symmetry: \(c_{ijkl} = c_{ijlk} = c_{klij}\) for \(i,j,k,l \in \{1,2,3\}\) [cite: 3]. The positive definiteness of such tensors is intimately related to the *strong ellipticity condition* in linear elasticity [cite: 22].

To evaluate these structures, researchers use **M-eigenvalues** [cite: 3, 22]. An elasticity tensor satisfies the strong ellipticity condition if and only if its smallest M-eigenvalue is positive, which correspondingly dictates whether the partially symmetric tensor is rank-one positive definite [cite: 3, 22].

## Structural Sufficient Conditions

Because calculating exact tensor eigenvalues is extremely challenging, researchers have focused heavily on identifying structural properties of the tensor entries \(a_{i_1 \dots i_m}\) that guarantee positive definiteness. 

### Diagonally Dominant and Strictly Diagonally Dominant Tensors

One of the most effective ways to establish bounds on eigenvalues without computing them is via the Geršhgorin circle theorem extended to tensors [cite: 5, 14]. 

Let \(R_i(\mathcal{A})\) denote the sum of the absolute values of the off-diagonal elements associated with the \(i\)-th index:
\[ R_i(\mathcal{A}) = \sum_{i_2, \ldots, i_m \in \{1, \dots, n\} \setminus \{i, \dots, i\}} |a_{i i_2 \ldots i_m}| \]
where the summation excludes the diagonal element where \(i_2 = \ldots = i_m = i\) [cite: 6].

An \(m\)-th order \(n\)-dimensional tensor \(\mathcal{A}\) is **diagonally dominant** if \(|a_{i \ldots i}| \geq R_i(\mathcal{A})\) for all \(i \in \{1, \dots, n\}\) [cite: 6, 7]. If the strict inequality \(|a_{i \ldots i}| > R_i(\mathcal{A})\) holds for all \(i\), the tensor is termed **strictly diagonally dominant (SDD)** [cite: 20, 21]. 

By extending the matrix theory, it has been mathematically proven that an even-order strictly diagonally dominated symmetric tensor with positive diagonal entries is strictly positive definite [cite: 7]. Furthermore, a diagonally dominated symmetric tensor is positive semi-definite [cite: 7]. These bounds provide computationally cheap, order-\(\mathcal{O}(n^m)\) checks that avoid eigenvalue calculations entirely.

### H-Tensors and Strong H-Tensors

While strict diagonal dominance is easy to check, it is a highly conservative condition. A broader and more generalized class of tensors is the **H-tensor** [cite: 6, 23].

A tensor \(\mathcal{A}\) is defined as an H-tensor if there exists a positive vector \(x = (x_1, \ldots, x_n)^\top \in \mathbb{R}^n_{>0}\) such that:
\[ |a_{i \ldots i}| x_i^{m-1} > \sum_{i_2, \ldots, i_m \in \{1,\dots,n\} \setminus \{i\}} |a_{i i_2 \ldots i_m}| x_{i_2} \cdots x_{i_m}, \quad \forall i \in \{1, \dots, n\} \]
[cite: 6, 23]. Such a tensor is effectively equivalent to a strictly diagonally dominant tensor upon scaling by a positive diagonal matrix [cite: 6, 19].

Crucially, if an even-order real symmetric tensor \(\mathcal{A}\) is an H-tensor and all its diagonal entries are positive (\(a_{ii \dots i} > 0\)), then \(\mathcal{A}\) is strictly positive definite [cite: 11]. Recognizing an H-tensor is often easier than computing eigenvalues, and iterative algorithms have been successfully developed to verify if a given tensor meets the criteria for being a *strong H-tensor*, thereby identifying positive definiteness effectively [cite: 19].

### Geršhgorin-Type and Brauer-Type Inclusion Sets

When basic diagonal dominance fails, tighter eigenvalue bounds are necessary. Using Z-identity tensors, researchers have established **Geršhgorin-type** and **Brauer-type** Z-eigenvalue inclusion sets [cite: 14, 18]. 

The inclusion sets map domains in the complex/real plane where the eigenvalues must reside. For instance, Li et al. proposed Geršhgorin-type inclusion sets with scaling parameters to test the positive definiteness of general even-order weakly symmetric tensors [cite: 18]. Because symmetric tensors are a subset of weakly symmetric tensors, these results are widely applicable. A standard test involves computing specific bounds \(\Delta_k^i(\mathcal{A})\) and comparing cross-term products. Theorem variations state that if specific Brauer-type regional lower bounds remain strictly greater than zero, then the smallest Z-eigenvalue is strictly positive, hence verifying that the tensor is positive definite [cite: 14, 18]. These parameterized inclusion sets are demonstrably sharper than legacy eigenvalue localization bounds [cite: 18].

## Special Classes of Positive Definite Tensors

The structural geometry of certain tensors guarantees their definiteness properties intrinsically. Several named tensor classes have been thoroughly analyzed to map out explicit analytical sufficient conditions for their positive definiteness.

### Cauchy Tensors

A Cauchy matrix is a well-known structure assigned via parameters \(x_1, \dots, x_m\) and \(y_1, \dots, y_n\). Extending this, an \(m\)-th order \(n\)-dimensional **symmetric Cauchy tensor** \(\mathcal{C} = (c_{i_1 i_2 \ldots i_m})\) is defined by its generating vector \(c = (c_1, c_2, \dots, c_n) \in \mathbb{R}^n\) such that:
\[ c_{i_1 i_2 \dots i_m} = \frac{1}{c_{i_1} + c_{i_2} + \dots + c_{i_m}} \]
[cite: 24]. 

A remarkable property of an even-order symmetric Cauchy tensor is that it is positive semi-definite if and only if its generating vector \(c\) is entirely positive [cite: 25, 26]. Furthermore, an even-order symmetric Cauchy tensor is strictly positive definite if and only if its generating vector possesses elements that are strictly positive and *mutually distinct* [cite: 24, 26]. This conclusion gracefully extends Fiedler’s foundational results regarding symmetric Cauchy matrices into the realm of multilinear algebra [cite: 25, 27]. Furthermore, checking the positive semi-definiteness of a Cauchy tensor is equivalent to verifying the strictly monotone increasing property of a related homogeneous polynomial in the nonnegative orthant of Euclidean space [cite: 25].

### Pascal Tensors

The Pascal matrix, populated by binomial coefficients, is known for being strictly positive definite. The concept naturally generalizes into **Pascal tensors**. Let \(\mathcal{P}\) be an even-order Pascal tensor of order \(m\) and dimension \(n\). Recent investigations utilizing rigorous mathematical induction have proven that even-order Pascal tensors are undeniably positive definite [cite: 8].

Importantly, these tensors are classified as *Sum of Squares (SOS) tensors* (a concept explored later) and as strongly completely positive tensors [cite: 8]. A related generalization leads to **biquadratic Pascal tensors**, which have similarly been proven to be both strongly completely positive biquadratic (CPB) tensors and strictly positive definite [cite: 28, 29]. The proof mechanisms reveal that as long as the base generalized Pascal matrices are positive definite, their even-order tensor counterparts naturally inherit this positive definiteness [cite: 8, 30].

### Hankel Tensors

A tensor \(\mathcal{T}\) is called a **Hankel tensor** if its entries \(t_{i_1 \dots i_m}\) depend solely on the sum of their indices \(i_1 + \dots + i_m\) [cite: 9]. Thus, \(t_{i_1 \dots i_m} = v_{i_1 + \dots + i_m - m}\) for a generating vector \(v\).

Hankel tensors are intrinsically tied to univariate moment problems. An even-order Hankel tensor is known as a *strong Hankel tensor* if its associated Hankel matrix is positive semi-definite [cite: 9]. A cornerstone theorem states that an even-order strong Hankel tensor is inherently positive semi-definite, implying it possesses no negative H-eigenvalues [cite: 9]. This hierarchical inheritance from a lower-order associated matrix to a higher-order tensor simplifies the computational verification significantly. 

## Advanced Analytical and Computational Methodologies

Due to the general NP-hardness of verifying positive definiteness globally [cite: 12, 15], computational mathematics heavily relies on powerful relaxation and approximation algorithms.

### Sum of Squares (SOS) and Semidefinite Programming (SDP)

The **Sum of Squares (SOS)** technique is one of the most vital frameworks in polynomial optimization. An even-order tensor \(\mathcal{A}\) is designated an SOS tensor if its associated homogeneous polynomial \(f(x) = \mathcal{A}x^m\) can be expressed as a sum of squares of lower-degree real polynomials:
\[ f(x) = \sum_{k=1}^r (p_k(x))^2 \]
[cite: 4, 9]. 

If a tensor is an SOS tensor, it is guaranteed to be positive semi-definite [cite: 8, 9]. However, according to Hilbert's 17th problem, the converse is generally false; a positive semi-definite tensor is not always an SOS tensor unless the dimension and order belong to specific small pairs [cite: 8, 31].

Despite this, SOS decomposition is a cornerstone because whether a polynomial is SOS can be framed and efficiently solved using **Semidefinite Programming (SDP)**, a convex optimization technique [cite: 4, 32]. Using the SOS SDP hierarchy (such as the Lasserre or Parrilo hierarchies), computational systems can verify if the second-order derivative (the Hessian tensor) of a target function is positive semi-definite [cite: 32, 33].

Moreover, the **Tensor Conic Linear Programming (TCLP)** framework allows researchers to reformulate the problem of finding extreme Z-eigenvalues of even-order tensors. Shenglong Hu et al. introduced the **Sequential SDPs Method (T-SSM)**, which uses an approximation sequence of semidefinite programming problems to solve the TCLP [cite: 2]. This yields a numerical algorithm capable of computing the extreme Z-eigenvalue for even-order tensors with dimensions greater than three, effectively circumventing theoretical limits with high-precision approximations [cite: 2].

### Tensor Decompositions and Rank Approximations

Another vector of attack utilizes tensor decomposition ranks, specifically the **M-rank** and **CP-rank** (Candecomp/Parafac rank) [cite: 34]. By reformulating low-rank approximations, researchers project the tensor onto positive definite parameter spaces [cite: 1, 34]. 

Any symmetric positive-definite tensor can theoretically be parameterized and approximated by a convex combination of predefined lower-order homogeneous polynomials [cite: 35]. This converts the positive definiteness constraint into an optimization space solved using non-negative least squares techniques [cite: 35]. Additionally, alternating direction methods—like the GEAP method—have been developed to compute Z-eigenvalues by decomposing the tensor eigenproblem into a series of standard matrix eigenproblems, allowing off-the-shelf eigenvalue algorithms to iteratively search for the extreme eigenvalues [cite: 13, 36]. 

### Trace, Determinant, and Invariant Methodologies

A more recent algebraic framework establishes eigenvalue bounds for symmetric positive definite tensors using intrinsic geometric invariants, namely the trace and the tensor determinant (or resultant) [cite: 10]. By leveraging the Arithmetic Mean-Geometric Mean (AM-GM) inequality, it is possible to construct a hierarchy of strict inequalities yielding progressively tighter upper and lower bounds on the smallest eigenvalue of the tensor [cite: 10]. This coordinate-independent strategy has been shown to significantly outperform classical entry-dependent methods like the Geršhgorin circle theorem for certain tensor structures [cite: 10]. Furthermore, studies on the determinants of structured tensors reveal explicit links to definiteness; for instance, the determinant of an \(m\)-th order two-dimensional symmetric Pascal tensor equals the \(m\)-th power of \((m-1)!\), ensuring its strictly non-zero status and confirming its positive definiteness [cite: 8, 37].

### Small Dimension Analytical Bounds

For highly localized problems—specifically fourth-order, two-dimensional or three-dimensional tensors—direct analytic necessary and sufficient conditions can sometimes be derived.

*   **Fourth-order two-dimensional tensors**: The positive definiteness relates directly to the positivity of a univariate quartic polynomial. Using Sylvester’s Criterion and exact discriminant evaluations, complete analytical formulas have been constructed to verify positive definiteness [cite: 22, 38].
*   **Fourth-order three-dimensional ternary tensors**: For ternary quartic homogeneous polynomials (where entries might be strictly restricted to $\pm 1$ and $0$), comprehensive strict inequalities and analytic criteria have been successfully established, proving the relationships and constraints under which these specific tensors remain strictly positive definite [cite: 12, 38, 39]. Unlike matrices, where a symmetric matrix with only $\pm 1$ entries cannot be strictly positive definite, the complexity of fourth-order hyper-matrices allows certain structural configurations of $\pm 1$ entries to indeed be strictly positive definite [cite: 12].

## Critical Applications of Positive Definite Tensors

The heavy mathematical machinery utilized to evaluate the positive definiteness of even-order tensors is driven by imperative needs across diverse scientific fields.

### 1. Stability in Automatic Control Systems
In the field of control theory, examining the stability of nonlinear autonomous continuous systems is heavily reliant on Lyapunov's direct method. The state equations $\dot{x} = g(x)$ describe the system dynamics. A system is declared asymptotically stable if one can construct a Lyapunov function $V(x)$—often defined as an even-degree homogeneous polynomial form $V(x) = \mathcal{A}x^m$—that is **positive definite**, while its time derivative $\dot{V}(x)$ along the system trajectories is consistently strictly negative [cite: 5, 6]. Validating that the associated tensor $\mathcal{A}$ is positive definite via Z-eigenvalue inclusion sets guarantees the energetic stability of the polynomial system without explicitly simulating infinite time horizons [cite: 18].

### 2. Medical Imaging (MRI and DKI)
Higher-order tensors are essential in modern medical imaging techniques, specifically in **Diffusion Tensor Imaging (DTI)** and **Diffusion Kurtosis Imaging (DKI)**. In these applications, water molecule diffusion in biological tissues is modelled using apparent diffusion coefficients [cite: 5, 13]. A 2nd-order tensor models simple Gaussian diffusion, but complex neural microstructures require 4th-order or 6th-order tensors to capture non-Gaussian diffusion kurtosis [cite: 35]. The physical validity of these imaging models demands that the diffusion probability density function remains strictly positive. This implies that the higher-order diffusivity tensor must be positive definite. Using tensor non-negative smallest eigenvalue constraints ensures the physiological accuracy of the derived neural tractography [cite: 5]. Frameworks that approximate specific positive definite tensors via SOS polynomials actively preserve the physical integrity of MRI outputs against measurement noise [cite: 1, 35].

### 3. Solid Mechanics and Elasticity
The theoretical modeling of linearly anisotropic elastic materials—ranging from crystalline structures to synthetic metamaterials—relies heavily on the elasticity tensor [cite: 3, 22]. The structural integrity and realistic physical response of these materials to strain is governed by the **strong ellipticity condition**. Researchers have mapped this condition mathematically to the necessary and sufficient requirement that the involved fourth-order partially symmetric elasticity tensor is positive definite [cite: 3, 22]. Evaluating the smallest M-eigenvalue directly dictates whether the material model maintains stability under arbitrary deformations [cite: 3, 22].

### 4. Quantum Physics and Particle Theory
In theoretical particle physics, the vacuum stability of scalar potential fields must be analyzed to understand the fundamental states of the universe [cite: 22]. The self-coupling configurations in these high-energy models are organized into 4th-order symmetric tensors. Verifying the vacuum stability of these scalar potentials translates directly to mathematically checking the positive definiteness (or copositivity) of these coupling tensors [cite: 22].

## Conclusion

The task of checking the positive definiteness of even-order tensors lies at the intersection of multilinear algebra, convex optimization, and applied engineering. Because the problem translates to establishing the strict positivity of a high-degree multivariate polynomial, general instances scale into NP-hardness [cite: 12, 15]. Nonetheless, continuous algorithmic breakthroughs have rendered the problem tractable.

Theoretical advancements, spearheaded by Lim and Qi's tensor eigenvalue definitions [cite: 5, 16], allow positive definiteness to be framed as an eigenvalue bound problem [cite: 9]. For practical deployment, researchers turn to highly structured tensor classes—such as diagonally dominant [cite: 7], H-tensors [cite: 23], Cauchy [cite: 25], and Pascal tensors [cite: 8]—which provide elegant, deterministic sufficient conditions that bypass intractable computations altogether. Concurrently, for general empirical data observed in fields like MRI or control theory [cite: 5, 13], Sum of Squares (SOS) programming [cite: 8, 32] and Semidefinite relaxations [cite: 2] deliver arbitrarily accurate polynomial-time approximations. The interplay of these theoretical insights and computational frameworks continues to successfully unlock the rigorous analysis of complex multidimensional systems across the sciences.

**Sources:**
1. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1P3w8l6QaJQ-OGQ-RRTq5bGq3oH5ig-npCmxjHWxqlEqLYqDrTfyST8ZC4qWGlCJCCUHqp2gNBSnYW0DXDR4jCJ1s7s9mTRe0XyOo_Qi_APnYhsrjoVwnX-qu5fK_e11BeL-UEph7UiFZnnLISUsiTzUpdDHzdER58dSRJFgWDpiw1kM=)
2. [tju.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWI5pfQLNHE-_1mSh1lQmQWVw-uaaVtuJhOEiaGSv1SLb0g6_XmthBY92S2FEkrQ1qtwAgw9C_nKs4Jmuv6NJaN_LYcORLzbYAqMaxmhQ5sMoUlLLhs5Jcma0QJKsUj6Bd_TKniRsVYWH5qOg=)
3. [zju.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGXJkZkaZa9oVQLczekA7HX3tj7PGmvU3AYZkBSVDqiTYV9gly2R_k8CR-9h5seeRWeffCrzLqFL1JxznQmno6sCSmpMpSCG1Fu_RRGkl3orZA9UAcQJlwdRSuOXGyzaZIMGxs0j6BjCgdQs4e4YhhBY0EwbI=)
4. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWVdw0uHlED6xUjwSGztJXCN5_2prre4lt3zJUsI2OrZvHlnlzvcCwrAby_aBUioIh-mvfJRT8W0zFjf5VDECaFQBabbiayePxWLaVokNGfMPq2Ctm9kcPPsTtFJVlbyJmHs7km_j0aGBh0Css0kRDJAL7MBb3f_k=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0r0pINKT85Qa3HJW8eJmGQxatP1h-nPfbRRTg3gx8M8FmEXO2F3PVbO5HrohHkKaz6eQP6nyLcQMKAPC6Qh06PjbrvIy0cUqUJ1GmGQnGIGrjGH7tHg==)
6. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjxDeMgrVvjcpJPM8JSYLIQhpyfk3UmElwGbZOsT7CdY_NQfjvyeKj3c64FPi5MFE2SxfXgUu6DiSmh9I-eZ-I_wQouzIoCZK48obEqhfFY3R1M_pJ-N7e7IrTA4k=)
7. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2r_pc3ZCb_SL8XRctP6GlIAfqLCn-SjI6Q37_xF36eUisfgsc23Hw9rf0lkwC7DQFfpLkcd98pCx-S_hxcEHqzJJe6DRec2wiNsU78C6LsjHWpTAIuCwmPSntHXAYx6QYEz8fBJRM0g==)
8. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFI_ug3TaBrmPfXjNidjW9jVKc5HT5suRHzRlJ6fLX3tt777_yDw8TfwSedgU7QGzlVXN3INsYwWV2eSrkz200PVqq6Uyzg3hVrIr1lAcM2nZpAoKyDBdsxDdQEHIc=)
9. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5508jSTi77cQdQLiTOyMdWpXBd8bNtbecXNy5lRvinJcLOYdegZJKleS_3IKDJI0Q2PBKKmZIogsPBmlFieHHWgq6_auwZS7XqdWYIe9hxn_dH_YglyIgrkGihbOPoJI5O9ApfE4vsBq7aaj4huXIArAI)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqqejAtdViJtnr53hIeYuIUCFBgLD31bczaFwPd5xaqR5Zk2RBnNyGvoxBdFe_PPI5C3jVVXN7CelJydwBDJ9tYHhD0gy6L4w3dv4_O7hUZoQNyLy2ZB1kgw==)
11. [ni.ac.rs](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFobY7hf9aHR_gLw092ctvMJ_MtiFJ3AluaACvW5EzcfanF9mJ61aqIg5JLRVVlSXP4L3CofMi0sBru61TOusHdlXrVqvcM7GqtOK_TP6isvlxzCXKl0vzXUay6lD6noioGN688wH3o8xwkBFgdu8qgLOIxzyGL2DjL)
12. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErGYCJ5bCFS3H_KIx4Rz0jgqcj2cYw4hbJozC_0gYSfxgVnAi3L4aUsW_VmNwobKryW56OZIEulHoejmQQHYo_TZr9tXloC6Oxhs_SNDHOzcoJz8JAISyPBdby8Cx7QikVqmHFP-mBnD4mrG0PtXF12Gg=)
13. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV6tpJ5H7_nZZMQwUnE4J9U265ClaIYJLdQqLCPQXBVMI8gZh8i1s7SLI31v9xwCEKnoQl6kORvKFw7zxcvpR24obqNjigvsyxkiipCDVcJo3XTfVSn6lBzGPy1hwogmUqatXvwrbe2g==)
14. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIG1Pbh78oNTpjTnBQIj_u1FKyOFfp9YW0uHeMuM9ZfJlwj8I0Esd_3f6UJX-Fl5h6OUGexz7wv5WDu3zkpRFABjar328XhCcw0Mcfz-g6eDPdIG9DUEqoB5n-1y0=)
15. [port.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ1TpsAEbYeXKAUwYPN4oXLEYe9dDfW6XyjMXxVFdsZtDdtPfFJNUJcNQcDWJesAtlSfOOxHHOhNdtqRZ1SqIbjdxd2m6tOtrP4LQakup4YuFLT2pz3gIG1Qefq3dA8LakSvdjdQ==)
16. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEte3D5iOxkaM9diXuTKKyRYl8l5GBm0mJrRfkFkOTxto_aeRMMIKTvwH6H-cBMWcZzr4rkCcfkt9V-M0qtQfNNe_cwxtc8eTykA2K4gk5b_gFLxeD1d76S-IQKb6nw)
17. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7LPY-w-1iGrsdtIuOAHmv7Mq8LFKyWZgkgInbao2iKKYYc4IHWJKrSBwv0_bk77WPKjD3f9bLUhzin__xW_EYeqd6eBo3Ueaph4PFf37Xs39NyCwtFBUhYvUiwuW3w0PYwV_C1RbGWLv9CgqTdBDOJG4=)
18. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUM9RL0WnmJPsde-AsXslfYyajfgLB15n-bbLwpV7HFRho59x6uLaeEljZTpUR2qV6KGuHrqt5dh_cH5shDVxawwQT-5ngIReAzTK0kil9819ujbDryoD7Wi-us56PrZcv8JYCJLB1IqIdaAfXgtrlYRs3zQdYAxeEMN6gGfrcKCorGTE=)
19. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXMHDyebY3XVySYhxybQm7yQGwfS5oCWgD6CahN0zrYpVpKAxTaHENZO7aECrzj7jes70R2o6iofr15-6E0o8T7lyS__Dzc_8FvPv-vtC0Ce_jKINRJ1VDux4MUlJikjiPC7rG3w6b)
20. [ni.ac.rs](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_fHsBYSSqQ1begFxHLz8E4ibQkkmd8X1_xlggR_nJazzoBBjbzQrMgkBOoZo1EUN0spv4jr8AO_ga5CqtvRNU0Sv1Rex24qJqEfqdUcQkV_bV05cWf3dJ0NFWjb1sfYvs3xBOGD7SMsquVKNQPeKG_PmJrrt4h5-m7YM=)
21. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElWDTxq8RsAbgfrms5sswE9wYdvX_e2SHo5yg8PsMjzc8BgqKL-Dc3xjaZRxr28PsqvPLrNMDsXBq8DLOeC8_n-ChQ4yNln5z5M8fmnBDsX4ixQQCB)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYyhmvuVB1qFAsRsosfS3d6N6cpfLURIPT3tu1G_7QhtNOT-GQjqP-BpQrDM0CGoYqtK8LuUN6__e4WoLOBju9HXIdjrk3PkcQm2AKkjEjxzQiJRFPP4NbcT8YTm2IhXRSxJb3PuXDB3mxxRLTOtbW6RpP_I6igoTcqw5nk2QuZSWodpTOBSbJWSvBVBBL48ygeTuLZefVeTFV4U4ojPstZKRTxbxe4TxLCw==)
23. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYiUjC1q0cD5ZLrpBdoY18vf74bfaCxn2xkPdbaFe4JEqSKkxczROs9PuYQq8Uap0bmvQNNr_SpArqGGahbdohZ7UVAiDbWhJEpP__OE0zKCmBLckicBVcxBGCum078Q==)
24. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEs5JBtufVbiXig7Wp3D-_ceAyV5iZ960Y3QgYGRZj--Snns0f_u9wC9rcTOFI0pzhZ0TSBDcLyNk05j1osSNsLt9_6tb4ZOVsSSYUvcK7wrDY2Wxlro1EHIX97lbAXFv5jc49AnjGBpbdrR9LqxeeRq09dysMG8n1-Jz6pqeQ=)
25. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuN0j4bxysUvOytVswCIP88OLXJ9i5C1U7a2z6D-5NZKG1khaVbQJfqcqpLT8OSMiXMTrWpFjjPyApbEfhvK6iQvb1KhTIeV8ul2CWXOOZTOdQaO9yQ9xJ_6k9ooV-9B4HRD-8TSbqVDXqmQMiGxmIS3orNXK8Nw==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdEFb4rR2wtVNCxIg9EJgW2iXZ08cP70Xn1mNVtzFkzwOUJyp2AmPyqw5GQ6W35-voK296VboA2mN9hGmIMg_D5Esw7Fz4cBAUp7u3jXOus9RjOvhL)
27. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFL8i5KC94Cy0czEBc1WSIf0s4MXpe1bLFmo_ep6PeljHkfI0cLR7DTv5nUOKn719X65xbZb1uKQ2IPr5FJwOxPlqWa_-M3FV9kiYKpxrKcBS1vle7AwF0S_NuxPlw5d7bi58z0CrYCFPE=)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZfugva13Q8s20GtBkl_714XNEiTCqNVjhvh4-9QFnsex6iIrITemlMbrGmA-kK4JlAtJRr0WbvxR1OnGSeKolCJ8frumet0EEYH4WpoKfMxr2oiLR8w==)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgEQmugBeGtFUKQGdEX5u5xwD1pz0Ct30tJLm0rui3mOE7K9G75SMFdkTyJoAdDC-StAUj_zRZZnx2Wu4lBwf29ed2ACNGJyi07GgJz_qTQ3khICF6fnN5s0UrFKMckdDzLFg0fcYArl3npwudEUe-Djbo44hzbnN6U1jdQwlg)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPDYMGW8fOB8WVXMxduL4O_6sZfKyMpHmyL1eeeVeQ_OHMoLum3wsuuauWm354fV-dDTskQWY450NRf6TGDCDIhvVnG4M_gocBNelfqAEHuzge-OZ7jfGHGl9HG6SLAdW-YfO5nFcLTODQBhd1ovQLjuOV04Vi_bPw3Kk4n8lX0QBM)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1DVnndlyxOZC2xx7ZvDSI9O_auUcycygcSws4JH7egMJytr2SSlL4HjLYhTxXFN2Joqlm2mYWH-nIa8lADJAjWE8o1wds5nvOm3SJP9z8yEZC1Hjp3A==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsq5kRZ-CXvJ9v-eE5r_9kzXX_IsjGOkYgK_HX4i7TzSIZn7rza1oX1BbjGAHZXOEcZTQG7KFhqG-hnR-FxkutCBGAzbMvlFwiFaZrA4mYOwDF6MJ0-A==)
33. [ijcai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA4ShrIXo_hMups7wlHfjarL3P5jU_xwkHOnWenbcUSV7R1yGMbyAPQ-MBuyG3K4R4BGmdHaEjn6EyMG0lE3R08hlSZpOyqKSLzO_KcxgaN3df0sMfPzx-5_9bhNLN2sc2sC2VYw==)
34. [optimization-online.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOaxLi43-aA-mb46PJcpSX9SWwYe_umniGdbOwS5M777l8Hz-kLKpN2-8smjFunSIDEcWNMyIkaFTSgTAOU1HSD7a86dfRI-YYt_CnuUyhJKZqhrHk6HpsVt3-cKINU7gUdcBOmVA5l0VZ6Fv3y8sHNvunAdzI6LEj)
35. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0LRDIf_ehJPMc1xZzjxJo4l6qfAIrClAH-2foygPZGJ_u3IC1CeNqdkeznCAZsaCke3conJkH18_nmjw_1owhnVmyNJMni6_5MLqe_mo-_tMrQkyUaiRPiha1wedZHRgk33emJYcj)
36. [peerj.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpDooNRveDbBJnhFrzRntEhxZMUG3VTucvV1IbtZbuYp2DaxrsNh3IzGS-gBLO0nugyj-KyWzl0LLGzeGyFsy7aBiJGJRP439_SR-Ec1ZwIaqIO8vK3c4fBg==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt4Gt1HwemR3lYmjwBo1LDqNJcwyDA8ElHAqLLxrSADxb2-tlFLhNPXikTPGRQ1kY07UmtbUmbk7yx20F5zLrr68di8WmwIll7Ij8vo09h0aX6YtMLVQ==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXejoaXQHJ6KXle_tRT9YznfgNIu3-778QHbstzircDcKHc5OMyxd_JgmqgT1a83YRUjkIi_Wpd7xZW6OoavCMrJ6-JFKFGYePO3hM6_8fvgeWUIEdT2YnVw==)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGS7F1teZuv9Hl87ZvgYanS2R7ZNVBrp6A1GAq15Q7E9zVOGtGDYcmFQRVarQRnEFWaacyGwVRdTwIoztLFDRLBLhNhp5k477LHfL4NxTnKvNuGzOshOQ==)


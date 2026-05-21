# T#41 Uniqueness in overcomplete CP decompositions (r > min(n_i))

**Pythia queue id:** 85
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDdzhQYXJ5NUZaV2wxTWtQemV5N3FBZxIXQ3c4UGFyeTVGWldsMU1rUHpleTdxQWc
**Elapsed:** 316s
**Completed at:** 2026-05-21T14:01:44.424295+00:00

---

# Uniqueness in Overcomplete CP Tensor Decompositions: Theoretical Foundations, Algorithmic Advances, and Applications

**Key Points:**
* **Tensor Rank and the CP Decomposition:** The Canonical Polyadic (CP) decomposition factors a multidimensional array (tensor) into a minimal sum of rank-one components. Unlike matrix factorizations, CP decompositions are often uniquely identifiable under mild conditions, making them exceptionally powerful for uncovering latent structures in data.
* **The Overcomplete Regime:** A tensor decomposition is considered "overcomplete" when the number of rank-one components (the tensor rank, $r$) exceeds the dimension of the vector spaces involved (i.e., $r > \max(n_i)$ or $r > \min(n_i)$ depending on the context). In this regime, the factor matrices contain linearly dependent columns, breaking classical uniqueness conditions based on linear independence.
* **Kruskal's Theorem and k-rank:** Joseph Kruskal's foundational theorem (1977) established that a CP decomposition is unique if the sum of the Kruskal ranks (k-ranks) of the factor matrices is at least $2r + 2$. While powerful, this condition is generally restricted to undercomplete or slightly overcomplete scenarios.
* **Generic Identifiability via Algebraic Geometry:** Advanced research in algebraic geometry, notably by Chiantini, Ottaviani, and Vannieuwenhoven, has proven that tensors are "generically identifiable" (unique almost everywhere) even in highly overcomplete regimes. For third-order tensors, generic uniqueness holds for ranks up to slightly below the generic rank of the tensor space, subject to a few well-documented exceptional cases.
* **Algorithmic Breakthroughs:** While exact and generic uniqueness theorems are historically non-constructive, recent algorithmic advances such as the FOOBI algorithm, Sum-of-Squares (SoS) relaxations, and Koiran's method of commuting extensions (2024) have provided polynomial-time frameworks to recover components in overcomplete regimes.
* **Robustness and Smoothed Analysis:** Because real-world data contains noise, modern theoretical computer science has focused on the "robust" identifiability of tensors. Works by Bhaskara et al. (2014) demonstrate that overcomplete tensor decompositions can tolerate inverse-polynomial errors, enabling robust parameter recovery for machine learning models.

**Summary for a General Audience:**
Imagine you are trying to unmix a complex smoothie back into its original, individual ingredients (like strawberries, bananas, and spinach). If you only have two data points (like color and weight), similar to a standard two-dimensional spreadsheet or matrix, there are mathematically infinite ways to "unmix" it. You can't guarantee you've found the true original ingredients. However, if you add more dimensions to your data—say, analyzing color, weight, and texture simultaneously, creating a 3D "tensor"—a mathematical miracle occurs. The true ingredients can often be uniquely identified. 

When the number of hidden ingredients (the "rank") is greater than the number of measurements you have in any one dimension, we call this an "overcomplete" scenario. Unmixing in an overcomplete scenario is notoriously difficult because the underlying factors overlap and share similarities. For decades, mathematicians debated when and how we could guarantee a unique unmixing in this regime. Recently, a blend of advanced geometry and computer science has shown that, in almost all generic cases, these overcomplete systems *do* have a unique solution. Even better, researchers have developed robust algorithms capable of finding these solutions even when the data is noisy. This has massive implications for artificial intelligence, allowing algorithms to discover a huge number of hidden topics in text, isolate overlapping audio signals, and learn highly complex patterns from seemingly limited data.

***

## 1. Introduction to Tensor Decompositions and the Overcomplete Regime

The analysis of multi-way data arrays, commonly referred to as tensors, has become a cornerstone of modern applied mathematics, signal processing, and machine learning. While matrix algebra provides the foundational tools for analyzing two-way data (rows and columns), matrices suffer from a fundamental limitation: their low-rank factorizations are inherently non-unique unless rigid, often physically meaningless constraints (such as orthogonality) are imposed [cite: 1, 2]. Tensors, which generalize matrices to three or more dimensions, possess structural rigidity that circumvents this limitation, allowing for uniquely identifiable factorizations.

### 1.1 The Canonical Polyadic (CP) Decomposition
The Canonical Polyadic (CP) decomposition, historically introduced by Hitchcock in 1927 and later popularized as CANDECOMP (Canonical Decomposition) by Carroll and Chang, and PARAFAC (Parallel Factor Analysis) by Harshman in 1970 [cite: 2, 3, 4], expresses a tensor as a sum of rank-one tensors. 

Let $\mathcal{T} \in \mathbb{R}^{n_1 \times n_2 \times \cdots \times n_d}$ be a tensor of order $d$. A rank-one tensor of order $d$ is the outer product of $d$ vectors, one for each mode. The CP decomposition approximates or exactly represents $\mathcal{T}$ as:
\[ \mathcal{T} = \sum_{i=1}^r \lambda_i (a_i^{(1)} \otimes a_i^{(2)} \otimes \cdots \otimes a_i^{(d)}) \]
where $a_i^{(k)} \in \mathbb{R}^{n_k}$ are unit vectors, $\lambda_i$ are scalar weights, and $\otimes$ denotes the outer (tensor) product [cite: 1, 5]. 

When $r$ is the minimal integer required to express $\mathcal{T}$ exactly, $r$ is defined as the **tensor rank** [cite: 1, 2]. Unlike matrix rank, which can be computed efficiently via the Singular Value Decomposition (SVD), computing the tensor rank of a generic tensor is NP-hard [cite: 2, 6, 7]. 

For a third-order tensor $\mathcal{T} \in \mathbb{R}^{n_1 \times n_2 \times n_3}$, the decomposition is typically written in terms of factor matrices $A \in \mathbb{R}^{n_1 \times r}$, $B \in \mathbb{R}^{n_2 \times r}$, and $C \in \mathbb{R}^{n_3 \times r}$, where the columns of these matrices correspond to the components $a_i, b_i, c_i$:
\[ \mathcal{T} = \sum_{i=1}^r a_i \otimes b_i \otimes c_i \]

### 1.2 Defining the Overcomplete Regime
In matrix factorization ($M = A B^\top$), the rank $r$ is strictly bounded by the dimensions of the matrix, $r \le \min(n_1, n_2)$. Tensors do not share this restriction. The rank of a tensor can significantly exceed the dimensions of its individual modes. 

A tensor decomposition is said to be **undercomplete** if the rank $r$ is less than or equal to the minimum dimension of the tensor, $r \le \min(n_1, n_2, n_3)$. In this regime, the factor matrices $A, B$, and $C$ can have full column rank, and the components are linearly independent.

Conversely, a tensor decomposition is **overcomplete** when the rank strictly exceeds the dimensions of one or more modes. In the literature, overcomplete often specifically refers to cases where $r > n_i$ for some or all $i$, meaning that the factor matrices are wide (more columns than rows) [cite: 8, 9, 10]. Consequently, the sets of vectors $\{a_i\}, \{b_i\}, \{c_i\}$ are linearly dependent. 

The overcomplete regime poses profound theoretical and algorithmic challenges [cite: 9, 11, 12]. Because the components are linearly dependent, classical algorithms relying on linear independence (such as Jennrich's algorithm based on simultaneous diagonalization) fail outright [cite: 9, 10]. Determining whether an overcomplete decomposition is unique, and if so, how to compute it efficiently, constitutes one of the most active areas of research in multilinear algebra and computational learning theory.

## 2. Identifiability and Essential Uniqueness

To utilize tensor decompositions for latent variable discovery, one must guarantee that the decomposition is unique. In parameter estimation, if the decomposition is not unique, the recovered factors may represent arbitrary algebraic artifacts rather than true physical or statistical components.

### 2.1 The Concept of Essential Uniqueness
A CP decomposition is considered **essentially unique** (or identifiable) if any alternative valid CP decomposition of the same tensor into $r$ rank-one terms merely consists of a permutation of the terms and a scaling of the vectors within each term [cite: 2, 13, 14].

Formally, suppose we have two exact CP decompositions of the same tensor $\mathcal{T}$:
\[ \mathcal{T} = \sum_{i=1}^r a_i \otimes b_i \otimes c_i = \sum_{i=1}^r x_i \otimes y_i \otimes z_i \]
The decomposition is essentially unique if there exists a permutation matrix $\Pi$ and diagonal scaling matrices $\Delta_A, \Delta_B, \Delta_C$ such that:
\[ \Delta_A \Delta_B \Delta_C = I_r \]
\[ X = A \Pi \Delta_A, \quad Y = B \Pi \Delta_B, \quad Z = C \Pi \Delta_C \]
where $I_r$ is the identity matrix [cite: 3, 5, 15]. The scaling ambiguity is intrinsic because scalars can be freely moved between the factors of a tensor product: $(\alpha a) \otimes (\beta b) \otimes (\gamma c) = (\alpha \beta \gamma) (a \otimes b \otimes c)$ [cite: 5].

### 2.2 Why Matrices Fail and Tensors Succeed
To understand the power of tensor uniqueness, contrast it with matrices. For a rank-$r$ matrix $M = A B^\top$, one can insert any invertible $r \times r$ matrix $Q$ such that $M = (A Q) (Q^{-1} B^\top)$. Because $Q$ spans a continuous space of transformations, a matrix factorization has infinite continuous ambiguities unless orthogonal or sparse constraints are applied [cite: 15]. 

Tensors of order 3 or higher eliminate this continuous rotational ambiguity. The higher-order structure restricts valid transformations exclusively to permutations and scaling, provided certain mild rank conditions are met [cite: 2, 15]. This makes the CP decomposition uniquely suited for tasks like Independent Component Analysis (ICA), topic modeling, and fluorescence spectroscopy, where the explicit values of the factor vectors hold direct empirical meaning [cite: 1, 2, 16].

## 3. Kruskal's Theorem: The Foundation of Uniqueness

For decades, the benchmark for tensor uniqueness was an elegant, albeit algebraically complex, condition derived by Joseph Kruskal in 1977 [cite: 3, 4, 8]. Kruskal introduced a new concept of rank to evaluate the linear independence of columns within the factor matrices.

### 3.1 Kruskal Rank (k-rank)
The Kruskal rank, or **k-rank**, of a matrix $A$, denoted as $k_A$, is defined as the maximum integer $k$ such that every subset of $k$ columns of $A$ is linearly independent [cite: 1, 2, 3]. 

Note that the k-rank is always less than or equal to the standard matrix rank: $k_A \le \text{rank}(A)$. For example, if a matrix $A$ has full column rank, then its k-rank is equal to the number of columns. If $A$ contains two identical or proportional columns, its k-rank is exactly 1, regardless of the overall rank of the matrix [cite: 1, 3]. In general position, the k-rank of an $n \times r$ matrix is $\min(n, r)$ [cite: 13].

### 3.2 Kruskal's Sufficient Condition
Kruskal proved that for a third-order tensor $\mathcal{T}$ with factor matrices $A, B$, and $C$, the CP decomposition is unique if the following condition is satisfied:
\[ k_A + k_B + k_C \ge 2r + 2 \]
where $r$ is the tensor rank [cite: 1, 3, 17, 18].

This theorem was revolutionary because it guaranteed uniqueness without requiring the matrices to have full column rank, thereby offering the first formal proof that overcomplete tensor decompositions could be identifiable. 

Consider an $n \times n \times n$ tensor with generic factor matrices. The k-rank of each matrix is $\min(n, r)$. If we assume $r > n$ (an overcomplete case), the k-rank of each matrix is $n$. Substituting into Kruskal's condition:
\[ n + n + n \ge 2r + 2 \implies 3n \ge 2r + 2 \implies r \le 1.5n - 1 \]
Thus, Kruskal's condition establishes that a generic tensor of format $n \times n \times n$ has a unique overcomplete decomposition up to $r = 1.5n - 1$ [cite: 18, 19, 20].

### 3.3 Necessity vs. Sufficiency
While Kruskal's condition is sufficient for uniqueness, it is not strictly necessary for all regimes [cite: 3]. Attempts to prove that the condition is also necessary for uniqueness have generally failed. Counterexamples exist showing that uniqueness can hold even when the Kruskal condition is violated, particularly for higher ranks ($r \ge 4$) [cite: 3, 21]. 

Furthermore, Kruskal's bound is notoriously difficult to verify in practice because computing the k-rank is an NP-hard problem. More critically, the theoretical upper bound of $r \le 1.5n - 1$ is quite restrictive; in practice, generic tensors have unique decompositions at much higher ranks. This limitation spurred a massive effort in algebraic geometry to discover "generic" uniqueness bounds that far exceed Kruskal's deterministic condition [cite: 19, 20].

## 4. Generic Identifiability in the Highly Overcomplete Regime

To push past the $1.5n - 1$ barrier of Kruskal's theorem, researchers turned to algebraic geometry. Instead of seeking deterministic conditions that hold for *all* tensors, algebraic geometers focused on **generic identifiability**—conditions that hold for almost all tensors, except for a subset of Lebesgue measure zero (a Zariski-closed set) [cite: 8, 22, 23].

### 4.1 Secant Varieties and Weak Defectivity
In algebraic geometry, the set of rank-one tensors forms a geometric object known as the **Segre variety**, denoted as $Y$ [cite: 14, 23]. The set of tensors of rank at most $r$ corresponds to the closure of the $r$-th secant variety of the Segre variety, denoted as $S_r(Y)$ [cite: 23, 24]. 

A tensor is generically $r$-identifiable if a generic point on the $r$-th secant variety $S_r(Y)$ can be uniquely expressed as a linear combination of $r$ points on the Segre variety $Y$ [cite: 24]. 

The dimension of the secant variety usually dictates the generic rank of the tensor space. The expected dimension of $S_r(Y)$ for an $n_1 \times n_2 \times n_3$ tensor space is $\min(n_1 n_2 n_3, r(n_1 + n_2 + n_3 - 2) + 1)$. If the actual dimension of the secant variety is strictly less than the expected dimension, the variety is said to be **defective** [cite: 24, 25]. Identifiability is intimately linked to a related concept called **weak defectivity**. A variety is weakly defective if its general secant planes have a contact locus of positive dimension, which geometrically implies that the tensor decomposition is not unique [cite: 23, 24, 25, 26].

### 4.2 The Chiantini-Ottaviani Bound (2012)
In 2012, Luca Chiantini and Giorgio Ottaviani achieved a major breakthrough by introducing an inductive method based on weak defectivity to study the uniqueness of overcomplete tensors [cite: 4, 23, 24, 26, 27]. 

For a generic three-dimensional tensor of dimensions $a \times b \times c$, where $a \le b \le c$, Chiantini and Ottaviani proved that the decomposition is uniquely identifiable for generic tensors of rank $r$ as long as:
\[ r \le \frac{(a + 1)(b + 1)}{16} \]
[cite: 24, 26].

This bound drastically improved the known range for identifiability. For example, if $a$ and $b$ are large, the allowable rank scales quadratically with respect to the dimension, vastly exceeding the linear bound ($r \le 1.5n$) provided by Kruskal [cite: 23, 24, 26]. 

### 4.3 Pushing to the Generic Rank (Chiantini, Ottaviani, Vannieuwenhoven 2014)
The quest for the ultimate generic uniqueness bound culminated in the highly influential 2014 work by Chiantini, Ottaviani, and Vannieuwenhoven. They established an algorithm based on the Terracini Lemma to check the generic identifiability of tensor spaces [cite: 19, 25, 28, 29, 30]. 

Through this computational algebraic geometry approach, they proved that generic identifiability holds for almost all tensor spaces up to **one less than the generic rank of the space** [cite: 25]. The generic rank is defined as the minimum rank required to span the entire tensor space almost everywhere. For an $n \times n \times n$ tensor, the generic rank is approximately $n^3 / 3n \approx n^2 / 3$. The authors verified that generic identifiability holds for all spaces of dimension less than 15,000, with a few rigorously classified exceptions [cite: 13, 25].

### 4.4 Exceptional Cases and Unidentifiability
Despite the ubiquity of generic identifiability, there are highly specific "exceptional" cases where the geometry inherently fails, meaning no unique decomposition exists even for generic tensors. Chiantini and Ottaviani identified several of these exceptions [cite: 24, 26].

A prominent example is the $4 \times 4 \times 4$ tensor of rank 6. For this specific dimension and rank, the generic tensor has an infinite number of valid CP decompositions [cite: 24, 26]. This specific non-identifiable case has surprising connections to computational biology, particularly in the statistical study of DNA strings [cite: 24, 26]. Other known unidentifiable cases include specific symmetric tensor configurations, which will be discussed in Section 8.

## 5. Algorithmic Approaches to Overcomplete Tensor Decomposition

While algebraic geometry provides the comforting theoretical assurance that a unique decomposition exists for $r \gg n$, these results are strictly existential. Finding the actual components computationally is a notoriously difficult non-convex optimization problem [cite: 7, 18, 19]. 

Classical iterative algorithms like Alternating Least Squares (ALS) are highly popular in practice but offer few to no global convergence guarantees, especially in the overcomplete regime where the objective function is riddled with spurious local minima [cite: 7, 31]. Consequently, researchers have sought principled algorithms capable of polynomial-time decomposition in overcomplete settings.

### 5.1 Jennrich's Algorithm and the Undercomplete Barrier
The standard spectral method for tensor decomposition is often attributed to Robert Jennrich (1970). Jennrich's algorithm relies on the simultaneous diagonalization of matrix slices of the tensor [cite: 9, 18, 32]. If $\mathcal{T} = \sum_{i=1}^r a_i \otimes b_i \otimes c_i$, one can take random linear combinations of the tensor along one mode to produce matrices $M_1$ and $M_2$. By computing the generalized eigenvectors of the pencil $(M_1, M_2)$, the factor matrices can be explicitly recovered.

However, Jennrich's algorithm intrinsically requires that the components $a_i, b_i, c_i$ are linearly independent [cite: 9, 10]. Therefore, it strictly fails the moment the rank exceeds the ambient dimension ($r > n$), rendering it completely useless for the overcomplete regime.

### 5.2 The FOOBI Algorithm
To break the undercomplete barrier, De Lathauwer, Castiang, and Cardoso introduced the Fourth-Order Cumulant-Based Blind Identification (FOOBI) algorithm in 2007 [cite: 9, 33]. FOOBI represents a significant paradigm shift. 

Instead of dealing with a third-order tensor, FOOBI generally operates on fourth-order tensors or utilizes specific flattenings of higher-order moments. By constructing Khatri-Rao products of the components (e.g., $a_i \otimes a_i$), FOOBI maps the overcomplete problem into a higher-dimensional space where the lifted components *are* linearly independent [cite: 9, 10, 33]. 

For example, if the original vectors $a_i \in \mathbb{R}^n$ are drawn generically, their Kronecker products $a_i \otimes a_i \in \mathbb{R}^{n^2}$ will be linearly independent as long as $r \le n(n+1)/2$ [cite: 9]. FOOBI leverages this by reformulating the tensor into a matrix whose columns are these higher-dimensional vectors, and then utilizes a specialized algebraic procedure to decouple them. FOOBI effectively decomposes generic 4-tensors in polynomial time when the rank is mildly overcomplete, up to $r = \mathcal{O}(n^2)$ [cite: 9, 33]. While theoretically beautiful, FOOBI requires storing and manipulating $n^2 \times n^2$ matrices, making it highly memory-intensive and sensitive to noise [cite: 6, 16, 33].

### 5.3 Sum-of-Squares (SoS) Relaxations
In the highly overcomplete regime, where simple linear algebra lifting fails, modern computational complexity theory utilizes Sum-of-Squares (SoS) hierarchies. SoS is a powerful meta-algorithm for polynomial optimization based on semi-definite programming (SDP) relaxations [cite: 6, 20, 33, 34].

Researchers like Hopkins, Schramm, Steurer, Ma, and Ge have demonstrated that SoS algorithms can decode overcomplete tensors with polynomial time guarantees, assuming the components are drawn randomly [cite: 6, 20, 33, 34]. For a third-order random tensor, SoS algorithms can theoretically find the true components even when $r$ is as large as $n^{3/2}$, vastly outperforming classical bounds [cite: 20]. The primary limitation of SoS is its immense computational complexity; solving the massive semi-definite programs required by the hierarchy is currently impractical for large-scale, real-world data, though it represents a triumph of theoretical computer science [cite: 34].

### 5.4 The Subspace Power Method (SPM)
More recently, researchers have focused on developing practical, fast iterative algorithms with provable guarantees for the overcomplete regime. The Subspace Power Method (SPM) introduced by Kileel and Pereira optimizes CP decompositions of low-rank real symmetric tensors [cite: 22, 35].

SPM operates by calculating one CP component at a time, alternating between applying a Shifted Symmetric Higher-Order Power Method (SS-HOPM) to a modified tensor constructed from a matrix flattening, and utilizing deflation steps to remove found components [cite: 22, 35]. Under specific geometric conditions, SPM guarantees convergence to global optima for tensors of rank up to $\mathcal{O}(d^{\lfloor m/2 \rfloor})$, performing roughly an order of magnitude faster than existing state-of-the-art CP decomposition algorithms while sidestepping the heavy machinery of SoS [cite: 22].

### 5.5 Koiran's Commuting Extensions (2024)
One of the most recent and significant algorithmic breakthroughs for generic third-order tensors was published in 2024 by Pascal Koiran. Addressing an explicit open problem posed in the computational literature regarding the lack of efficient algorithms matching Kruskal's uniqueness theorem, Koiran developed a constructive uniqueness theorem based on the method of "commuting extensions" [cite: 19, 32, 36].

Koiran's algorithm applies to order-3 tensors of format $n \times n \times p$. It proves both the uniqueness of the decomposition and provides a polynomial-time algorithm for generic tensors up to rank $r = 4n/3$, provided $p \ge 4$ [cite: 19, 32]. 

The method of commuting extensions, originally pioneered by Strassen for proving lower bounds on tensor rank, is utilized here to form a system of matrices that commute. By leveraging an algorithm that computes these commuting extensions alongside a classical diagonalization-based Jennrich algorithm, Koiran achieved the first efficient algorithm for the overcomplete decomposition of generic third-order tensors beyond the $r \le n$ barrier [cite: 32]. Koiran's work extends seamlessly into the $n \le r \le 4n/3$ regime, closing a long-standing algorithmic gap in the literature, though achieving efficient decomposition up to the theoretical maximum of $n^2$ remains an open challenge [cite: 19, 32].

## 6. Robustness and Smoothed Analysis

While generic identifiability and algebraic algorithms provide exact recovery guarantees, real-world applications invariably involve noise. An algorithm that successfully decomposes $T = \sum a_i \otimes b_i \otimes c_i$ in exact arithmetic may fail catastrophically if presented with $\tilde{T} = T + E$, where $E$ is an error tensor [cite: 11, 12, 17]. Uniqueness, strictly speaking, makes sense only for exact CP decompositions [cite: 5]. Therefore, proving that algorithms and uniqueness conditions are *robust* to small perturbations is critical for machine learning applications.

### 6.1 Robust Kruskal Uniqueness (Bhaskara et al., 2014)
A landmark result in robust tensor decomposition was established by Bhaskara, Charikar, and Vijayaraghavan in 2014 [cite: 12, 17, 37]. They presented a robust version of Kruskal's celebrated theorem, proving that if a tensor's decomposition satisfies a robust form of Kruskal's rank condition, the decomposition can be approximately recovered even if the tensor is known only up to an inverse-polynomial error [cite: 12, 17, 37].

The proof largely traces the outline of Kruskal's original proof—relying on a permutation lemma that establishes sufficient conditions for concluding that columns of perturbed matrices are essentially permutations of each other up to scaling [cite: 17]. The robust version of the theorem guarantees that the output vectors $a'_i, b'_i, c'_i$ are close to the true vectors $a_i, b_i, c_i$ in Euclidean distance, bounded by the magnitude of the noise tensor $E$ [cite: 17].

Crucially, Bhaskara et al. demonstrated that their robust methods explicitly apply to the overcomplete case [cite: 12, 17, 37]. This immediate application implies that the parameters of various latent variable models can be identified using only a polynomial number of samples, an essential step toward efficient learning algorithms in noisy environments.

### 6.2 Smoothed Analysis Framework
Worst-case analysis of tensor decomposition is pessimistic due to NP-hardness constraints. Average-case analysis (assuming factors are drawn entirely randomly) is often unrealistic for real-world datasets which contain structured correlations [cite: 9]. 

To bridge this gap, theoretical computer science employs **smoothed analysis** [cite: 9, 11, 38]. In the smoothed analysis setting, the parameters of a model are assumed to be adversarially chosen but then subjected to slight random perturbations (analogous to inevitable measurement noise or minor environmental variance) [cite: 9, 11, 38]. 

Vijayaraghavan, Bhaskara, and Moitra introduced smoothed analysis models for overcomplete tensor decomposition, providing algorithms that can decompose highly overcomplete tensors (with rank polynomial in the dimension) under these mild perturbation assumptions [cite: 11, 38]. This paradigm has successfully sidestepped traditional hardness results, yielding efficient learning algorithms for models like multi-view networks and mixtures of Gaussians where the number of components severely outnumbers the dimension [cite: 11, 38].

## 7. Symmetric Tensors and Waring Decompositions

The study of overcomplete tensor decompositions diverges slightly when considering symmetric tensors. A symmetric tensor is invariant under any permutation of its indices; geometrically, it represents a homogeneous polynomial [cite: 22, 28, 29, 35]. 

### 7.1 The Waring Problem for Polynomials
For a completely symmetric tensor $\mathcal{T} \in S^d \mathbb{C}^{n+1}$, the CP decomposition reduces to expressing a homogeneous polynomial of degree $d$ in $n+1$ variables as a sum of $r$ powers of linear forms:
\[ \mathcal{T} = \sum_{i=1}^r \lambda_i (v_i)^{\otimes d} \iff P(x) = \sum_{i=1}^r \lambda_i (v_i^\top x)^d \]
This is classically known as the **Waring decomposition**, a foundational problem in algebraic geometry dating back to Sylvester and Clebsch in the 19th century [cite: 28, 29, 35].

The symmetric rank is the minimal number of such terms required. Because the components are restricted to be identical across all modes ($a_i = b_i = c_i = v_i$), the identifiability conditions differ from asymmetric tensors [cite: 28, 29, 35].

### 7.2 Generic Identifiability of Symmetric Tensors
Just as with asymmetric tensors, one seeks to know if the Waring decomposition is unique for $r$ up to the generic symmetric rank. The generic rank of symmetric tensors is governed by the celebrated Alexander-Hirschowitz Theorem, which perfectly classifies the dimensions of the secant varieties of the Veronese variety (the symmetric analogue of the Segre variety) [cite: 30].

Building on this, Chiantini, Ottaviani, and Vannieuwenhoven (2017) definitively proved that the general symmetric tensor of subgeneric rank is almost always identifiable [cite: 28, 29, 30, 39]. This means that the Waring decomposition is unique up to scaling and permutation for virtually all dimensions and degrees, provided $r$ is less than the generic rank.

However, three classical exceptional cases strictly violate identifiability:
1. $d = 6, n = 2$, and $r = 9$: A ternary sextic of rank 9.
2. $d = 4, n = 3$, and $r = 8$: A quaternary quartic of rank 8.
3. $d = 3, n = 5$, and $r = 9$: A cubic in 6 variables of rank 9 [cite: 28, 29, 30].

In these exceptional symmetric cases, the underlying geometry forces an infinite continuous family of valid decompositions, meaning the physical components can never be uniquely isolated, regardless of noise or algorithmic power [cite: 28, 29, 30].

## 8. Applications in Machine Learning and Data Science

The profound theoretical results surrounding overcomplete CP decompositions have directly fueled a revolution in unsupervised machine learning. The method of moments, which infers model parameters from empirical higher-order moments (represented as tensors), intrinsically relies on tensor uniqueness for parameter identifiability [cite: 8, 9, 16, 17]. 

### 8.1 Overcomplete Latent Variable and Topic Models
In text analysis and natural language processing, topic models like Latent Dirichlet Allocation (LDA) are used to uncover hidden thematic structures in large document corpora [cite: 8, 12, 17, 40]. Here, documents are mixtures of latent topics, and words are drawn based on these topics.

By computing the third or fourth-order co-occurrence moments of words across documents, researchers can construct a tensor whose rank-one components directly correspond to the hidden topics [cite: 8, 16, 40]. The problem becomes "overcomplete" when the number of latent topics ($r$) greatly exceeds the size of the observed word vocabulary ($n$), a highly desirable configuration for deep, fine-grained semantic analysis [cite: 8, 16, 40].

Anandkumar, Hsu, Janzamin, and Kakade (2015) established that overcomplete topic models are identifiable given observable moments of a certain order, provided a structural constraint called **topic persistence** is enforced [cite: 8, 40]. Under topic persistence, the Khatri-Rao products of the topic-word matrices expand sufficiently to satisfy higher-order Kruskal-like conditions. Their results prove that random structured topic models are uniquely identifiable with high probability in the overcomplete regime, expanding the utility of tensor methods far beyond simple, undercomplete vocabulary models [cite: 8, 16, 40].

### 8.2 Overcomplete Independent Component Analysis (ICA)
Independent Component Analysis (ICA) seeks to separate a multivariate signal into additive, independent non-Gaussian subcomponents. A classic application is the "cocktail party problem," where the goal is to separate individual voices from microphones recording a crowded room [cite: 16, 34].

When there are more source signals (voices) than sensors (microphones), the ICA model becomes overcomplete [cite: 8, 16]. While matrix-based ICA methods collapse under overcomplete configurations, higher-order tensors constructed from the 4th-order cumulants of the signal provide a pathway to separation [cite: 16, 33]. The FOOBI algorithm and modern overcomplete tensor decomposition methods guarantee that the underlying independent sources can be uniquely and efficiently isolated, achieving blind source separation in environments previously thought impossible to resolve [cite: 9, 16, 33].

### 8.3 Mixtures of Gaussians and Multi-View Models
Multi-view latent variable models postulate that data is generated from a hidden state, and multiple conditional "views" of the data are generated independently given that state [cite: 11, 16, 17, 38]. Tensors inherently capture these multi-view co-occurrences. 

When the number of hidden states (e.g., the number of Gaussian components in a Gaussian Mixture Model) exceeds the dimensionality of the observed feature space, the exact recovery of the mixture parameters relies directly on overcomplete tensor decomposition [cite: 11, 16, 17, 38]. Bhaskara et al., applying their robust uniqueness frameworks, proved that multi-view mixture models and Gaussian mixtures can be identified with polynomial sample complexity bounds even without strict separation assumptions between the Gaussian centers, opening massive avenues for flexible, non-parametric density estimation [cite: 17, 38].

## 9. Conclusion

The study of uniqueness in overcomplete CP tensor decompositions resides at the intersection of multilinear algebra, classical algebraic geometry, and modern computational complexity theory. What began as an abstract question regarding the identifiability of arrays has evolved into a fundamental mathematical framework supporting advanced artificial intelligence and signal processing.

The theoretical transition from Kruskal's rigid $r \le 1.5n$ deterministic bound to the geometric proofs of generic identifiability pushing to the generic rank ($\approx n^2/3$) revolutionized our understanding of multidimensional data. Concurrently, algorithmic breakthroughs ranging from FOOBI and Sum-of-Squares to Koiran's elegant commuting extensions have transitioned these existential proofs into practical computational tools. Finally, the integration of smoothed analysis and robust perturbation bounds ensures that the theoretical beauty of tensor uniqueness survives the noisy realities of empirical data, cementing overcomplete tensor decomposition as an indispensable tool in the future of data science and machine learning.

**Sources:**
1. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfN-CKTU6fbbxFNz0_N_8i5AdGg_azNrrX7mqrq9uk351PqYEc37OLlzBw4VBkt_0HlOJ8OnjaO5RVX_m33OUbENeSh6qANP8TICobZRKPuSCC0tTmO95j5lGVdEBmFiPtCdI5WHNx3yU_)
2. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAaeM6lNAaGkK_EImI9Ma1hLvik7d3IQGDYz39CHFCDMMDlvKpBKPcf4x51saQ1aTB9Yc8hPdFBqzzIZ-4TTQGWk64cwQGvBry2zIZt4HDxDW07618zGYhaPsdc0dscE9mfDzB5-x249KtFA==)
3. [leidenuniv.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6dHsdL7ug7hpaldohXO1asGjdHr21cGbzR49tcdsjKlVL1wDIS6aVFXBX-JoOcEhJNdZg5uus_yWwRTPsecTLhzJxBxh8MTkVX1R9MUIzkDPE27we-jKe_sWbhQjJUNACIf-uBzfTLkZGGipEWBYtCPvI)
4. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl-CnddhN_Bu7IAmNb6qezxAJjZVbRSNF-SfaKqfzsItW_T6K6zP5cK31M_4XySQvbKSKIFK-nMOmzPa1y2GXQQUPdZ1SZ5hXmJCo0IdLwNHfdpwH6PjPOYEkUWNbkJabMjXutcTXIV6OFWTuy40x0JRkGzDAdIVmqRuD-a5txcqF1otJVTNsagCQyUSviUJFxaQ==)
5. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF50CTMFmtwCv_7fDe1Nm-Q8zGZXsbffKbNRSQvKd0QkafiUHChJ6zabF2m7P-oxYVKxyAvbFK3puNVs5gmIpJlJkKhXfPcVENZbgw84wonwTY8Fu01fkYkFZhHuU2xDUou-R-69zRc2MBN5E4KxyoIsWFtgPillRVEbe473EqRS033ZwI6TBrj1mqk7cKRpcHxz75tzw==)
6. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8LkyZhWs76m7I3gPL64fHKo7vWLxcR3_VaSNQ0e9BFF1Wmm9r8Xrs1dCikahCDLjgvn6nQytVGwCdInHGw0lc5T9FaLFnyXCJNmKf-ZZsKiGY3dO5PPNON22tCymX3AzWk7GFE14bS4rd7WlKC4UTBohtHI5dc3faHJx_cmW4ZZIhIZJaGEumJWd4TqYFTYBQC9JC)
7. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxSZMsQqPD6XCVd6vagMQ6t6cNryEig7cGT3FAC7Bno_lY1UY6zZ1YoOUhZhz8uiL8XVR6tgpqGUZq7Io7eTH-2pEEQlZn-NX5QoZI53zkZzMJs9l9WMmAA3rmgiOESd1KPXi0vdw-QhvgU9eqfg==)
8. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0w6f7Xw7yt2D-hL-FrdjXazIF24nAtBqCn0KVtUbmTURVmtln27blovedIcBA66qSFV2daO-y9xBnPUmlOv70Pfb3BluMBLivFYWk7-XqdAEmtfLgJnqWFy9on2zlaVSKMIVoI7e6TWIu_SYdr5sp7-t8NX8XWfHi_0wbmrowgA==)
9. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSc3YMvYdFW9skdEbkGrf_RJ6x-b9Zxciw6YqInrIlFybd8J-NZiUYF3_3OScE04ocuaJ56YlRsC1w1-t7lee8W4X2oI0UJzdTOZO-y14ghAb6AGrosqg1y8i0wH0SMcteU-1DmJ2xPNM6WR_PnIOKl0sTpA==)
10. [utah.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHE1HpMevvMK67fp1M6BDMFZovRtSXN41h6YDytVzij4ZpYvZ0LXl6Y7xbVn4nuQSbdrNcKuLDyPJ1_nJiM8YRsRQBOysX99utMOi_5GSth1R_svbFpxYDRxSV_BtV9uBT8YAt_8u8IDpqgv8LBY3ph2A==)
11. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGQovOSR1izeVfE03zbWOFburL-S9uhjGvAPx0Vc4Yi1maXjUmofrQyRm52qTo6b490AV3KRR53e_iQsesYh9xIapfMPPVmQq5g12p_QDxvz5I-BFFN2anu3XnRbPrBtaQ-m2lPHMhSRMY0ghlCe4VIRchYwozuLX-Scl1CTvn7v068443O-X_xA==)
12. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoicH29TjvUCkRUWPW-NuLfH_khrrshLht4RjHtYyRmFzuqk7kfKz5hlFTuxXVvUR3lewi0BWuer1lSdjvuR8FCUOU9H-UgYa2enbs8GJ0mEwne1BD8KQ2IAp-oNi2ndrgE8Ge)
13. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlKEgHn45k7ys2DJmU2ToS8uPizHdrhnk4qfcfs3wDk6HQbqwMqZRVvihIvdFXAut4zv3DKAvuDr1-g8zf_3_FByTAjDiIz4LznT-ZOUE_ziJIRzui46gLmd32QeyyANw_1wGZgYgSGNGYSNI=)
14. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEusfJQrkTZ1NgtCOJKSmkJdM9WgI7tMkqjUtQrgZfSjGaLPEx2XUjXokgpPhGiQ360LFlZA2GGZOF28Zz96cCKmcP1bs9k9w1lBVmkXE1mbQwMHOuXTU3SepUONJbcFUJhnXflFTaOonsBbsz4o6Jya3_ZRw==)
15. [oregonstate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-sVSPlGcHLssMQf0oNyEPpgVPjt1mOCjYCAn7DJkVaaSV2oXqt0_hGVawDsOh-PjW1EDpV9BKPC88j2GTmY1MTv71VVVQ68a8rwJCi8gHDfXwPnwycOHNNdtHaX8ozEeo3ZDCQEbFtMa0WOZv47TGThg=)
16. [caltech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYgHs2FS1yC8TmkshvkTgQ9rrLnuAcAibgDOXxuErjrxZuHIBeJCWkjnw6COlHfaZP0tX_F1Gyrs0wY5A7-u1K_fNdBct7QElX-vpxT4JvTf4gshkvs5jZHVYJEWVx5b6vDNcLE-D34y7dcjIcvuojDIPjVJ_CzuwSrEOy8ijtTU4z-Kgk)
17. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzTjERbCsX9xYBJwGFRvvaX_Pay1ShtvjMd5aZMVTVt7BqRkEAhQK8NpLLp8y1IHGI0qimNyuHfL3yqHcDwe9F1iEaQoabI8LjGZIDtPhv_gPtr8koTH9W6AKB3P0lTWW__zh_Oj-1)
18. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFa79D0gsl31nhpLJ37BpzcoWGvp0VJbVKHN12264LVa1GscYy8J8sHgRsAbwN6YP9pVraeXW1Eft2-ra5hLknnWwFRhEgEQkylKGOXnWfGeJk76oVekuxTsaacZKfcw7YH)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH5QhnrmQaEbxE-pj4ZapDPzmzdgiQTxnBvIPO74Z-sblu0pCMg8UO2eKadftWdbwbQa6ZN2mil5nb2wYqEqPfrxtkJJKknrH_gvn-ErqcWWhu_SX--LpJaQ==)
20. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_zd3cde7BqxRcGY3bFu47I1lSHQfWYVtxCQtNNpFfLcaJx6BdXw7akJnGG2GTOmneGPyMC_kOwRw6RI0d6SuBbz2iS1qhunaqZR4FJf-2EOisAIfA)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5kBvfIl5_3DDlO8j9WrEPAOAUYcvhbJjz-pzqK_Nq0-PGTKXFmkp00bJr46hHrlDJcWllttQe0hG_MI7UFwuHgNwzU0Ao8sFexopSDypZkelURunI7TlDtGDwIoJwrhxUDSobA8RDR2sgRMgjTX2iXivTUdd6pCo_N5CIGBseYBrfKei5OKNyerm1stZh19QB86cGg-v-jwwpBaPa1BdDyBfJmZs=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPhwO3-A53SgScaOAYCc39nX8OITnC8nlqP-1PaPbUJzuAHmIYKN6JDccaOBlfgGT9L06smHXePS39thq3kwf0hoUw5BsByQu4m7LBRyLo49ztiDojZQRmAyYENA==)
23. [unifi.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_G3TjLS32B3MMKeyZ12A1xFOJQzzUoX0LNivlDylt7F9tdu8On6n87pn-lBZY5YYl5kytLIyOQZ6R0s4_MKjegI1ZGDwnQld9ZxZ69Znqfk9fhiMKiZ2M6KHJIeNenJKKCSUUnjpWQKVur0-DmYNC0A7sep_-os403pk1QHlWi2v0)
24. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMFy3dMLrluEh1fpwNSrnMSbW6YGYpLSnO6WZ1PUDVhwBrh2adnMJaeiPhAU4Yndy_bm2F28MYLOfEGuO4ogQUuyAfbx7g7mocu2n0ICqX0j6PSXXzIXKqEVITE655ghdrlHNzw0E=)
25. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH89NNEuEXbQdp5R9DzkinZZ2v22W1m0NqVOk8z27Q8CKmQCgjywt89p1sX1-HpWrDl9dBDEnxg0IvaQW9PF02RlFmYD14lRNk8nMh0tMFDId3i4yLAWJf_T3xPh8HMFZFt1Q==)
26. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAWrFrWOfHR83H_gv3fT9mfRF-LHi1jbLVkJA2jLT2ENP5DSySx-S20Z4YQ5OJs89loIYb3L6ufQfiqnFgFi7jU7xKDHfGV9JnvTv-NVO_ovcZfjYJktv4r_Eccott2lOEzg==)
27. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOnCHKWJqW7JjFcOypg9ThN4sZKizoz71Y3doM8pZ6V3JFCzm8Q55tIOT6B6aqTA_0q2vZEA-yW_wgHsMk_LaFRQJpsj6o4LPBB4u5sGRl2ejwqalgzTiFEXcS2s6DbS56W2LD)
28. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEadzZHNL0uIkWHkW-PQvUpH-sUEH_HP6utqlByuVqoHmrt6RSTL70rJYX25iS5S2s4rKuj43iHZNVtfnT6h-dO9dBnGc6Hd9_HEKTEpSzUxJYtrJGrMIlM9O693VmyoAvRwe83b_HekFJtRVwHcuTCMe8G-w==)
29. [unisi.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEduTbUK_krd9KWCkxoRg58Uu7KvRVROgPUzIaVgfDPu5z1lnGyFq7mQOXS6Sua9Y6WYPaepqMgWJvoJBgikg3DPuUMSYZRgTQlrQD2EwBbCNoUg1o1dg4x-p57PU7m7IxA8V3IuYMUXXMcDSQgUjpm_sTXnmb5CPZNZDvxyw==)
30. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj8icwxvsM4i_QxB-BnJcAJF2n_jinHyQRJZvnWujcHcRRtWXfChs_1t_vgi3LTZczBiPJxVzK1KSc_Koud0Luf9PsBr18Uf6Agp9ojqR_VB5NBrNOMJwHPkGzI9BmUSc=)
31. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbzucFF8V4nbX5ei_fm1vEqcQVZtKor-JWHYRKNED0fnxeVW3KS6GlMuUKj_PRVDSqWh_SFjx-0Ej_s7YIHA35WFeUNtKCNeDdGr_RleCeaeRirwkS_Wn5_sTjF1WgjA0h-MdQ14ffnh4LjeSblHsMiw==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRxnYaUmjPOgbQcZrwexPsDFt7W4XKxve_S81tB7HFCl5VtD7jRkbe5UfBwXY8dprj1_sknKd2GTQlHA_bdydzxQq0_ZGUeTw4_NDh5xWOyCX3hc6HGA==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESO7467b7-Cp8pAzPg9JbC-Pcfpd-pMyhdEcqerOPBWY1rhPp3Kz1ucw1C2o7IfIHUy9CNO9Zlj6FYoNIhVhqUI6LN4qqN1oEypPS15K6RZWDKkyFSYA==)
34. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVv-3jGwQUuU8XFWFuf9oY_At4TzOwpOpQcrzhsLDYsfg2N-XJvwrKiApqHluzf6zdeBh_Q1V7N2pttvoeFHwkW1Ys3pVwAek0OV3jQTcdC4DGSA_Fh4eSF9bB8_mtAIpCcEjdKhFpeR0ldl2EKalannLlLy_mmpWvgdpShWB4)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHedoygLaYgLbg6wTmFWTZ3-PQZoKrdcj2E1X48MhKjmUoQLbpviLwEOX0H5woq9XZ8fQFwrfBRGEfiC27lv3kzemnTBwdJYVK-6-8Fwp1iNTYhc2KvD1wMOV8NUuPCOWw02aj5F8cwzvUCyQI8T7viitupmkv_82kf0V94YrU-QAonEeisSwOnct5Wk7nzKyJ6tqE-uZd9JpluT1cE7Ff-JngWTONXVg==)
36. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0_I1NsyvZsTv6HKtERmAfN2StqWW5D8dmfjO2ya1RsE_4k2fP7rfKin_3EmrbLRKz18Y5A9THb8A9p9Pn2APSTdeAk86jeRSX7eLS6zhQpwOk3Je8Y6V7wE5tqJLnHJxCFt8BHnwuAnAeEQ94fw==)
37. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwHPCvKapun-PmgjTRJo1KVJWXA9VLQYvN4MtuQYY4Z2KDHVh8FuQM70AmIo5FezOi4nJK6QGkIAnEb_0cO5g3jl1DH2xXbeyGdOWpcuTUHS3fPidve4rysEzaZrbqFn4ZB6ZBvAvkyg==)
38. [rutgers.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYiUn4PzpZtrkCM90-ndKoEXr0EBp60mr8ZHMpANVB4j0nH-hPEYawR2MCqRc5OWnJqu_WQAw0j3E-gchZYTKnCRhQuAzC7KIwgVgxUSb9MDAb8hM7JwRQ3j-AEm2WP4NzcuoKxgP7qKYKIJ_hd446iIhLLLLtk4t-121__K9YGNgs)
39. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9U6S7J3O_VVCA0nUAHNM9VWiR0M5JxDkC1EprEI0TXr_cfu8cESNTS94V_XXjUCgXaRKPtAJgJmUUJ8A0IT5nyFd2OfSnS2QUJRgEb9ha19W_fxXA0VsnDO2HlZRSJzUOv5Qv1yHiVgMYx3Wf1kpoZTc=)
40. [jmlr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuovSVCF7VXA85a3U27Q6QMmR1314uoF-OvCQmIEGE5aBTLCdtl1pbkeIOyEfsaO7c1CGpj-HVLTDIlGDHjksL7-qAU7t2t0sYUiU_iMEEdwvfOSatFg_FY_oE3F9LWPrrXaCo)


# PARA-P15: CP decomposition uniqueness 2025

**Pythia queue id:** 52
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDRU1NYXJmX0YtWExqTWNQcE12eWlRbxIXQ0VNTWFyZl9GLVhMak1jUHBNdnlpUW8
**Elapsed:** 252s
**Completed at:** 2026-05-19T11:05:41.112248+00:00

---

# Comprehensive Report on Kruskal-Style Uniqueness Conditions for CP Tensor Decomposition: Refinements, Generic Ranges, and Computational Tests (2024-2026)

**Key Points:**
*   **Fundamental Rigidity of Tensors**: Research indicates that, unlike matrices, higher-order tensors exhibit remarkable rigidity, allowing their rank-one components to be identified uniquely under mild conditions, a property foundational to multilinear algebra.
*   **Evolution of Kruskal's Condition**: While Kruskal's classical condition remains a cornerstone for strict identifiability, recent theoretical refinements have increasingly utilized matroidal splitting and compound matrices to extend uniqueness proofs beyond traditional $k$-rank limitations.
*   **Generic Uniqueness Breakthroughs**: It seems likely that algebraic geometry—specifically the study of secant varieties and weak defectivity—has solidified the theoretical upper bounds for generic uniqueness, proving that tensors remain identifiable up to ranks substantially higher than their dimensions.
*   **Algorithmic Advances in Overcomplete Regimes (2024-2026)**: The evidence leans heavily toward a paradigm shift in computational decomposition, with novel algorithms based on commuting extensions and Koszul-Young flattenings successfully bypassing the traditional barriers of simultaneous diagonalization.
*   **Widespread Application**: Identifiability guarantees are proving critical in solving previously intractable problems in Gaussian Mixture Models (via the method of moments), latent variable discovery, and the theoretical interpretability of deep neural networks.

**The Foundational Importance of Uniqueness**
Tensor decomposition extends the logic of matrix factorization into multidimensional arrays. However, while a matrix can be factored into lower-rank components in infinitely many ways due to rotational indeterminacies, tensors of order three and higher frequently possess a unique canonical polyadic (CP) decomposition. This fundamental property transforms tensors into powerful tools for isolating true, unconfounded latent variables in complex datasets.

**Navigating the Overcomplete Frontier**
Historically, finding the decomposition of a tensor computationally was restricted to the "undercomplete" regime, where the rank does not exceed the dimensional axes. Recent theoretical leaps between 2024 and 2026 have pushed algorithmic capabilities into the "overcomplete" regime. By employing advanced polynomial flattenings and leveraging algebraic geometry, researchers are uncovering computationally tractable paths to recovering generic tensors of rank significantly larger than their individual dimensions.

**Intersection with Modern Machine Learning**
The mathematical study of tensor uniqueness is not merely an abstract pursuit. The latest identifiability tests directly govern our ability to interpret deep learning architectures, such as polynomial neural networks, and to untangle highly complex statistical distributions. As researchers map the generic uniqueness ranges for different tensor formats, they simultaneously unlock new methods for robust parameter estimation in artificial intelligence.

***

## 1. Introduction: The Uniqueness Paradigm in Multilinear Algebra

The Canonical Polyadic Decomposition (CPD), historically known as CANDECOMP/PARAFAC, is a foundational technique in multilinear algebra that expresses a higher-order tensor as a minimal sum of rank-one component tensors. For a third-order tensor $\mathcal{X} \in \mathbb{R}^{I \times J \times K}$, the CPD is formulated as $\mathcal{X} = \sum_{r=1}^R \mathbf{a}_r \otimes \mathbf{b}_r \otimes \mathbf{c}_r$, where $\mathbf{a}_r \in \mathbb{R}^I$, $\mathbf{b}_r \in \mathbb{R}^J$, and $\mathbf{c}_r \in \mathbb{R}^K$ are the loading vectors, and $R$ is the CP rank [cite: 1, 2]. 

A paramount advantage of the CPD over traditional matrix factorizations (such as the Singular Value Decomposition or Principal Component Analysis) is its inherent essential uniqueness. Matrix factorizations generally lack this property without the imposition of stringent constraints such as orthogonality or non-negativity; for any matrix factorization $M = AB^T$, an invertible transformation matrix $Q$ can be inserted such that $M = (AQ)(Q^{-1}B^T)$, generating infinitely many valid factorizations [cite: 1, 3]. In stark contrast, tensor decompositions of order three or higher are characteristically rigid. Under mild mathematical conditions, the CPD is unique up to trivial indeterminacies, namely the scaling of vectors within a rank-one component and the permutation of the $R$ rank-one components [cite: 3, 4].

This uniqueness property, rigorously formalized by J.B. Kruskal in 1977, underpins the utility of tensor methods in latent variable recovery, blind source separation, and interpretable machine learning [cite: 4, 5]. When a tensor accurately models a data-generating process, the uniqueness of its decomposition ensures that the recovered mathematical factors directly correspond to meaningful, real-world underlying variables [cite: 6, 7]. Between 2024 and 2026, the theoretical landscape of CP tensor decomposition experienced profound evolutionary strides. Researchers have bridged algebraic geometry, computational complexity, and statistical learning to redefine generic uniqueness bounds, formulate novel identifiability tests, and devise polynomial-time algorithms capable of operating in highly overcomplete regimes [cite: 8, 9].

## 2. The Classical Foundation: Kruskal's Condition and Strict Identifiability

To contextualize recent advancements, one must first examine the classical framework governing CP uniqueness. The bedrock of this theory is Kruskal's sufficiency condition, which relies on a specialized variant of matrix rank introduced by Kruskal himself, known as the $k$-rank (Kruskal-rank). 

### 2.1 Kruskal's $k$-Rank and the Sufficient Condition
For a factor matrix $\mathbf{A} \in \mathbb{R}^{I \times R}$ formed by the column vectors $[\mathbf{a}_1, \dots, \mathbf{a}_R]$, the $k$-rank of $\mathbf{A}$ (denoted $k_A$) is defined as the largest integer $x$ such that every subset of $x$ columns drawn from $\mathbf{A}$ is linearly independent [cite: 2, 10]. It naturally follows that $k_A \le \text{rank}(\mathbf{A}) \le \min(I, R)$.

Kruskal's celebrated 1977 theorem states that for a third-order tensor $\mathcal{X}$ with factor matrices $\mathbf{A}$, $\mathbf{B}$, and $\mathbf{C}$, the CP decomposition is essentially unique if:
$$ k_A + k_B + k_C \ge 2R + 2 $$
When this inequality holds, the rank of the tensor is exactly $R$, and the factor matrices are strictly identifiable up to scaling and permutation [cite: 2, 11]. This result relies heavily on Kruskal's Permutation Lemma, an ingenious but notoriously complex proof that evaluates the zero-patterns and proportionalities within the factor matrices [cite: 11]. Stegeman and Sidiropoulos later provided a more accessible and intuitive proof of Kruskal's condition, utilizing the Khatri-Rao product (column-wise Kronecker product, denoted $\odot$) and establishing that Kruskal's condition implies specific necessary uniqueness constraints [cite: 2, 10].

### 2.2 Limitations of the Classical Condition
While Kruskal's condition guarantees strict identifiability, it is a sufficient but not generally necessary condition. It has been shown that Kruskal's sufficient condition is both necessary and sufficient for small ranks (e.g., $R=2$ and $R=3$), but fails to be necessary for $R > 3$ [cite: 2]. This realization opened the door to scenarios where the condition is violated, yet the decomposition remains unique due to the specific joint pattern of zeros or structural properties within the matrices [cite: 11]. Furthermore, Kruskal's theorem addresses strict (or specific) uniqueness—certifying uniqueness for a given, fixed set of matrices—but does not fully capture the probabilistic nature of generic tensors drawn from continuous distributions [cite: 12, 13].

Moreover, theoretical analyses investigating the Cramér-Rao lower bound (CRLB) on the variance of unbiased estimates of tensor parameters reveal that when Kruskal's sufficient condition is not fulfilled, the stability of the CP decomposition can degrade under noisy observations, impacting the identifiability of individual columns within the factor matrices [cite: 14].

## 3. Algebraic Geometry and Generic Uniqueness Bounds

A major thrust of contemporary research (2024-2026) shifts focus from strict identifiability to **generic identifiability**. A property is generic if it holds everywhere in a parameter space except on a set of Lebesgue measure zero (an algebraic set of strictly lower dimension) [cite: 3, 12]. In the context of tensors, generic uniqueness means that if the entries of the factor matrices are drawn from an absolutely continuous probability distribution, the resulting CP decomposition is unique with probability one [cite: 8, 12].

### 3.1 Secant Varieties and Expected Dimensions
The study of generic properties relies heavily on the tools of algebraic geometry. The set of all rank-one tensors forms an irreducible algebraic variety known as the Segre variety (or the Veronese variety for symmetric tensors) [cite: 15, 16]. The set of tensors of CP rank at most $R$ corresponds to the $R$-th secant variety of this Segre variety, denoted $\sigma_R(V)$ [cite: 16, 17]. 

A tensor space is considered "$R$-identifiable" if the generic fiber of the map from the abstract secant variety to the secant variety consists of exactly one point [cite: 16, 18]. According to Terracini's lemma, the tangent space to the secant variety at a generic point can determine whether the variety is defective. If the expected dimension of the secant variety matches its actual dimension, the variety is nondefective [cite: 16, 17]. Generic uniqueness cannot occur for ranks exceeding a threshold $R_{gen}$ (the generic rank) and rarely occurs exactly at $R_{gen}$. However, breakthroughs in algebraic geometry have shown that identifiability holds for almost all ranks below $R_{gen}$ [cite: 3, 19].

### 3.2 The $3I-2$ Bound and Weak Defectivity
For cubic tensors of dimension $I \times I \times I$, recent geometric results have firmly established that the CPD is generically unique (i.e., $R$-identifiable) for ranks up to a specific upper bound. Specifically, the decomposition is generically unique for $R < \lceil \frac{I^3}{3I-2} \rceil - 1$ [cite: 3, 8]. This is a profound extension beyond Kruskal's condition, as it implies that the latent dimensionality (the rank $R$) can be substantially larger—polynomially larger—than the observed spatial dimensionality $I$ [cite: 12, 19]. 

Further algebraic tests for generic identifiability utilize the geometric notion of **weak defectivity**, pioneered by Chiantini and Ottaviani. They introduced an inductive method utilizing tensors of rank 1 to prove identifiability bounds [cite: 17, 20]. For three-dimensional tensors of format $(a, b, c)$ where $a \le b \le c$, this method demonstrates that $k$-identifiability holds for general tensors of rank $k$ as soon as $k \le \frac{(a+1)(b+1)}{16}$ [cite: 17, 21]. A tensor variety is classified as not tangentially weakly defective ($k$-twd) if the tangent contact locus behaves predictably, providing a concrete metric for generic uniqueness [cite: 16, 17]. Exhaustive classifications of small tensor sizes have identified the rare exceptions where identifiability fails, such as $4 \times 4 \times 4$ tensors of rank 6, a specific case of interest in mathematical biology and the study of DNA strings [cite: 20, 21].

## 4. Modern Computational Tests: The Reshaped Kruskal Criterion and Compound Matrices

While generic uniqueness bounds dictate theoretical limits, practitioners require computational tests to certify the identifiability of specific given tensors.

### 4.1 Uniqueness of One Factor Matrix and Compound Matrices
Theoretical refinements have relaxed conditions to guarantee the uniqueness of at least one factor matrix, even when overall uniqueness might not be strictly proven. Domanov and De Lathauwer extended Kruskal-type conditions using $m$-th compound matrices and Khatri-Rao products [cite: 5, 10]. If the column rank constraints are relaxed such that none of the factor matrices possess full column rank, one can analyze the second compound matrices (matrices of $2 \times 2$ minors) to establish uniqueness. By doing so, they formulated conditions where the CPD of $\mathcal{X} = [\mathbf{A}, \mathbf{B}, \mathbf{C}]$ yields a uniquely identified third factor matrix $\mathbf{C}$ up to column scaling, bypassing the need for the strict $\sum k$-rank $\ge 2R + 2$ threshold on all three matrices simultaneously [cite: 5, 10].

### 4.2 The Reshaped Kruskal Criterion
A prominent computational strategy for identifiability is the **Reshaped Kruskal Criterion**. Tensors can be flattened or reshaped into matrices or lower-order tensors. By applying Kruskal's criterion to the reshaped tensor, one can leverage existing rank decomposition algorithms [cite: 22, 23].

Recent studies analyze the "effectiveness" of this criterion—meaning it is satisfied on a dense, open subset of the smallest semi-algebraic set enclosing the rank-$R$ tensors [cite: 22, 24]. The reshaped Kruskal criterion has been proven effective for both real and complex tensors within its applicability range [cite: 24]. For symmetric tensors (where the CP decomposition is equivalent to the Waring decomposition of a homogeneous polynomial), analyzing the Hilbert function reveals that the reshaped criterion remains optimal up to specific bounds. For instance, in $4 \times 4 \times 4 \times 4$ symmetric tensors, algebraic analysis of the Hilbert function resulted in a criterion effective for all symmetric tensors of rank strictly less than 8, achieving the theoretical maximum range for effective criteria [cite: 23, 24].

Furthermore, the reshaped Kruskal criterion has been instrumental in establishing the generic identifiability of **Hadamard-Hitchcock decompositions**. These decompositions express multidimensional arrays as the Hadamard (element-wise) product of several tensor rank decompositions, a format intrinsically linked to restricted Boltzmann machines and statistical graphical models with hidden variables [cite: 25].

## 5. The Overcomplete Regime: Algorithmic Innovations (2024-2026)

One of the most intense areas of research in tensor decompositions currently is the development of polynomial-time algorithms that can decompose **overcomplete** tensors—where the rank $R$ exceeds the dimension $n$ of the tensor modes (e.g., $R > n$ for an $n \times n \times n$ tensor) [cite: 12, 26]. While algebraic geometry assures us that such tensors are uniquely identifiable in principle up to $R \approx O(n^2)$, translating this into a computationally efficient algorithm is notoriously difficult and often NP-hard [cite: 4, 27].

### 5.1 The Barrier of Simultaneous Diagonalization
For decades, the standard computational approach to tensor decomposition was Jennrich's algorithm (also known as simultaneous diagonalization) [cite: 27, 28]. This method transforms the tensor slices into a matrix eigenvalue problem. However, Jennrich's algorithm structurally fails when the rank $R$ exceeds the dimension $n$, creating a seemingly impenetrable computational barrier for overcomplete tensors [cite: 27, 29]. 

### 5.2 Koiran's Commuting Extensions (2024)
In 2024, Pascal Koiran introduced a constructive uniqueness theorem that successfully breached the $R \le n$ barrier for generic tensors. By applying the method of **commuting extensions**—a concept originally pioneered by Strassen to prove $3n/2$ lower bounds on tensor rank—Koiran developed an efficient algorithm capable of overcomplete decomposition of order-3 generic tensors of format $n \times n \times p$ (where $p \ge 4$) up to rank $R = 4n/3$ [cite: 28]. 

Commuting extensions operate by appending rows and columns to noncommuting coordinate matrices such that the resulting larger matrices commute, thereby allowing joint eigenvector analysis to retrieve the tensor's rank-one components [cite: 30]. Koiran's work represents a major advantage over Kruskal's classical uniqueness theorem because it provides a direct, efficient algorithmic proof [cite: 28]. Interestingly, further research by Koiran utilizing constructions by Shitov proved that the general computation of commuting extensions is an NP-hard problem, illuminating the delicate computational complexity boundary these algorithms navigate [cite: 28].

### 5.3 Koszul-Young Flattenings (2024-2025)
Building rapidly upon these foundations, a breakthrough was published in late 2024 and 2025 by Kothari, Moitra, and Wein. They formulated an algorithm utilizing **Koszul-Young flattenings**, an advanced mathematical tool motivated by algebraic complexity lower bounds for matrix multiplication [cite: 9, 26].

The core limitation of previous flattening techniques (the "trivial flattening" which stacks tensor slices) is that reshaping an $n \times n \times n$ tensor into an $n^2 \times n$ matrix caps the identifiable rank at $n$, the smaller dimension of the matrix [cite: 27, 29]. Koszul-Young flattenings represent a non-trivial, higher-degree polynomial flattening that sidesteps this rank deficiency. 

Kothari, Moitra, and Wein's algorithm successfully decomposes an $n_1 \times n_2 \times n_3$ tensor (where $n_1 \le n_2 \le n_3$) for ranks bounded by $R \le (1-\epsilon)(n_2 + n_3)$ for any arbitrary $\epsilon > 0$, provided the tensor components are generically chosen [cite: 9]. For the cubic case $n \times n \times n$, this condition simplifies to $R \le (2-\epsilon)n$. This represents a remarkable factor-of-2 improvement over the classical simultaneous diagonalization algorithms, and firmly supersedes Koiran's $4n/3$ limit [cite: 9, 27].

Furthermore, their research highlights a fascinating dichotomy in computational tensor algebra: the discrepancy between *generic* components and *random* components. While the Koszul-Young algorithm achieves $O(n)$ rank recovery for generic components, it has been demonstrated that for tensors with random (e.g., Gaussian i.i.d.) components, efficient decomposition is possible at much higher ranks, scaling up to $O(n^{3/2})$ [cite: 9, 29]. Kothari et al. provided a geometric proof showing that for generic components, a broad class of degree-$d$ polynomial flattenings cannot surpass the $Cn$ barrier, suggesting a fundamental computational hardness intrinsic to generic algebraic structures compared to random stochastic structures [cite: 9].

## 6. Structural Variants: Partial Uniqueness and Matroidal Splitting

Beyond strict overcomplete computational algorithms, researchers have also sought to weaken the underlying axioms required by Kruskal's theorem. Benjamin Lovitz (2022) introduced a completely novel proof technique to generalize Kruskal's theorem using matroid theory. Instead of relying on Kruskal's permutation lemma, Lovitz formulated a "splitting theorem" for sets of product tensors [cite: 13, 26]. 

In this framework, the stringent $k$-rank condition is weakened to the standard linear algebraic notion of matrix rank. Consequently, the conclusion of strict uniqueness is relaxed to the statement that the set of product tensors "splits"—meaning it is disconnected as a matroid [cite: 13, 26]. This matroidal approach successfully certifies uniqueness in domains that fall below the traditional threshold required by the permutation lemma, offering a flexible tool for analyzing tensors with linearly dependent loadings.

Similarly, tensors with missing data (incomplete tensors) have been robustly analyzed. When tensors have missing fibers, algebraic frameworks reduce the CPD to relatively simple matrix completion problems via eigenvalue decomposition. If generic uniqueness conditions are met for the fully observed counterpart, relatively few fibers are actually required to accurately compute the exact CPD, enabling highly scalable randomized and fiber-sampled tensor algorithms for massive datasets [cite: 31].

## 7. State-of-the-Art Applications (2024-2026)

The theoretical maturation of Kruskal-style uniqueness conditions and the mapping of generic uniqueness ranges have triggered a renaissance in applied mathematics, statistics, and machine learning.

### 7.1 Deep Learning and Polynomial Neural Networks
Tensor decompositions are closely analogous to the weight structures of deep neural networks (NNs). By parameterizing NN weights as low-rank tensors (such as CP, Tucker, or Tensor-Train formats), researchers achieve massive data compression, reducing storage costs and inference latency while retaining expressivity [cite: 8]. 

Crucially, the generic uniqueness of tensor decompositions directly answers the question of **identifiability in deep learning**—whether the hidden representations of a neural network can be uniquely determined from its outputs. For Polynomial Neural Networks (hPNNs) and models with generalized activation functions, recent work (2024-2025) leverages Kruskal-type conditions and partially symmetric tensor decompositions to establish exact identifiability conditions [cite: 32]. By mapping the weights to an overcomplete CP tensor format, mathematicians can determine the "activation degree thresholds" required to guarantee that the network's latent parameters are uniquely recoverable, preventing confounding and ensuring disentangled, interpretable representations [cite: 32]. 

### 7.2 Gaussian Mixture Models and the Method of Moments
The Method of Moments (MoM) for estimating probability distributions avoids the pitfalls of non-convex likelihood landscapes by matching empirical sample moments to theoretical moments. In high dimensions, moment tensors become computationally intractable to form explicitly. However, by treating the moment matching equations as a system of incomplete CP tensor decompositions, researchers can recover the parameters of Gaussian Mixture Models (GMMs) efficiently [cite: 33].

Kileel and colleagues (2024) developed a framework demonstrating that the mixing weights and component-wise means of a GMM can be rigorously identified from the first $d$ moments via a coupled system of partially symmetric CP decompositions [cite: 15, 33]. Applying principles of computational algebraic geometry, they proved that a symmetric CP tensor is generically unique when the rank $r$ satisfies $r < \frac{1}{n} \binom{n+d-1}{d}$ (for $d \ge 3$) [cite: 15]. This implies that a GMM with known covariance is identifiable up to $r = \mathcal{O}(n^{\lfloor d/2 \rfloor})$ components [cite: 33]. By circumventing the explicit construction of high-order tensors through tensor-free linear solves, their Alternating Least Squares (ALS) optimization schemes achieve local linear convergence, offering a statistically optimal, highly scalable alternative to Expectation-Maximization (EM) [cite: 1, 33].

### 7.3 Coupled Tensor Decompositions (CTD) for Multimodal Fusion
In modern data science, datasets often come from multiple modalities (e.g., simultaneously recording fMRI and EEG data) [cite: 6, 34]. Coupled Tensor Decompositions (CTD) fuse these diverse datasets by representing each measured tensor as a sum of a shared/coupled component and a distinct/personalized component. 

Recent uniqueness theorems specifically address these coupled models. It has been proven that a coupled decomposition can be generically unique even if the decomposition of the individual constituent tensors violates Kruskal's condition and fails to be unique in isolation [cite: 6, 34]. The coupling structure—where certain factor matrices are shared across tensors—acts as a regularizer, forcing the entire joint system into rigidity. Easy-to-interpret generic uniqueness conditions based on the uni-mode uniqueness of individual datasets have been established, and semi-algebraic initialization algorithms guarantee robust recovery in low Signal-to-Noise Ratio (SNR) environments [cite: 6, 34].

### 7.4 Multi-Way Clustering with Binary and Ternary Variables
In applications such as computational biology and psychometrics, tensor clustering models often employ binary or ternary latent variables (e.g., assigning subjects to discrete, potentially overlapping clusters). In these discrete domains, alternative identifiability conditions bypass Kruskal's $k$-rank requirement entirely [cite: 35]. If integer-valued constraint matrices exist that satisfy specific combinatorial properties, the CP decomposition is proven uniquely identifiable up to column permutation [cite: 35, 36]. This demonstrates that while algebraic geometry dictates generic uniqueness in continuous spaces, discrete constraints inject localized rigidity, allowing exact unique decompositions at bounds that would otherwise be considered unidentifiable.

## 8. Conclusion

The trajectory of CP tensor decomposition research from 1977 to the 2024-2026 horizon illustrates a profound evolution from strict linear algebraic bounds to geometric probabilistic paradigms. Kruskal's classical condition provided the initial assurance that multidimensional data inherently resists the rotational indeterminacy that plagues matrix analysis [cite: 1, 2]. Today, the mathematical synthesis of secant varieties, commuting extensions, and Koszul-Young flattenings has definitively proven that tensors remain uniquely interpretable even when highly overcomplete, pushing the boundary of identifiable ranks from $O(n)$ to $O(n^2)$ [cite: 9, 27].

The latest computational identifiability tests—ranging from reshaped Kruskal criteria to compound matrix evaluation and matroidal splitting theorems—offer practitioners robust tools to certify their models. As these theoretical limits are charted, they directly empower next-generation algorithms in deep neural network interpretability, multimodal data fusion, and high-dimensional statistical inference. The mathematical uniqueness of the CP tensor decomposition is no longer just a structural curiosity; it is a vital algorithmic catalyst driving transparent, identifiable machine learning forward.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBurwFcEsYC-XKerktKH1H6zAx64MgWGaWso0ZL2P4lV9z4suBdv309uRgQqh2E5SdNMHzUAdQ7VBJz8xYTzxPCXmyd73I3SBIAVpegskWjHFBg6rjaQ==)
2. [alwinstegeman.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe-3PWyf-z9jneUBKeTRBcaa0RPQu1SnqrUtvkF3vkI8ssjog9yPt5cP7S25roMrWuptjFh02IODDyQczueFrdJ6ZpB_STHiZ3SzioxP3m2QGlN_IZW6qxW5BNi7Sq7T5SK08bp2RJA7Vz_RHUoUikbI1hL9yhH9y9Ty99nF8WPlw=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6DCfDpWsHz4prRrCYberBY8XrNnjWjbnDHihnS1CuOPDbulLsc7ZL08WboEqzW7tWpP-5IGMXzU2_C7FiggVeIU1r6HZv41_OeIDdDd1Xbcx3G8xP2_QY7A==)
4. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8y3TsX4vCbPWiQ2GRn0QqWNruvhHXtutKdwziFAqE_mjCSHA3yU4_HXEiRdF6xBuH6VHRoXEyMzfrJlt6K4mYtsd0ORtemZrSQA5QWipA4MQurnVtG-ICKM5bNSK4sn5obxoiEgq_99u-MNJIqW7q6M07TNE3)
5. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBIO76BGX5GyATcIA3GRxN9BX6eJBGrxkrrS9THNXt2oWqSyYyepyEN2nAWO8ZpB0SVRnbyYb3iyCoz-wWU1AoXNE9PQOab4mBZGn_NC2txTbg3Fk6ed7AfOBDYSMHkA0uLg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqUPhq_OqbQP35zyW8dYbXUn6KDbygBlSgubysLAYQ8C_YF7xvKfKDp3Ac8xZMDltslXHA9LD7aE4sFm5AulR3j7hYRHiGdkbvukJAF7vH_Vqa-FXhSEfGag==)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJW4AEFmMke1IDjIYbs1yjIS4GWcH3SRoW3mX-36t_SXpmYJw9YkNh1Vtb1hgB2kEhb0GdHWw90wP6_RUWuN53SBq-rwZs2JTiUnfb5AmUVD1dZjGe_pB5WSk10i7I4hEnBLbmwpmV7LSrxOmyPMEoPZa1ILCVaeG5UrIPEkrK9KveXQU6fosL9FMrtmH4qjCsDeMIFR3PPA6fSgMjvlzSiKSHpHjmvmBGA1ctALgvlfK9DrKibInxxX9JvOPX0zuJYOCPUUL5IykZ8ukflw_oxBBJw2wkXbdeGQfvY7kAUr5d7vUvjRMBGfXCZRd57qKKIJR0yxL8EDXGS8RV8gAewJxBoWN_KTwb20kgnXHpgpf5wMrbqwpCs1Ni)
8. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc-G-EQAlD6JzoWfkRhXJ6v_TFmnz4LWcKpUrrBNLzTfqtbDAe1S0Lj5foDXKm5vzv5iMIJwI4EH3UQvJXLMhlFW2V6iqZg0cAjnZZ16jzizwF2mITJbud59RxRRao7RlrxykDv4H0Ac43fuX-u3q4hGCqQ0As6dw2a553VFwx8KiFezcCgKbHxDkBJsvaRuU4Z9xPwXtNTHE=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDKKrTEWhSsJcXp5qRn8m-d4gv-ZOr_T4oO1nnOFQjmRtrGPsZm0Dk2a-Dun2DHpM4Hz4GYdq0IQY9ymWtuPyJdo65cqnB_h69ymIVUC0Ighg8IdQNIQ==)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOmFAkEyL2JuQm7ji2rQsom8vIm_t52IN0n2Ij7AU6IKMAXAvOp0RVoe7onLIBnXhCnmRf78U5sf02v54p-w8Nk38gvF1mW1wzborsKa7-LwvVGJlevaIu21mUH7DyKXimfGpxMnzY1uJV--tLT48JVjv2HA5fELyFN5fP8LOlCV3q61iCSeNKYA5xEwUzijKw8mOkBuF08tfxkusBfme2pkDpRu2ep344Tf_6CrqDdMhs4Um3f7Ljdmw4M3D_tz1q6fDBm7vSf4pPzn16rDbAmLlOlhilmFrmwvDY5CiU3kEe_iM7K-v1TZePrxhJG7cSwrZ4xQ==)
11. [leidenuniv.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVxAwhrp-D-ohl9HIS_oy4XL1A3snWlbUQugiyT8b4wdrz_pD5Cdox5WCeXVdpLkvxikKZTafwvljPadliTgZAxsdg26bUAqiv3sA-RdwUcSpyZ8DmGArfMaSrS_EkNfCawYP84h0oBH3xBnAvwSKa8XdRXsJtcCGYJw==)
12. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAK0kiWk0RyYD3ROKMOYlPApoeFLRuQTfCd_HRxcAHVJCWMsp6AZZ4ZBCCnIYtMDAgI-BfvNIIiXAsWqvFNeWlQFGzJVY-spN73gY7sXuY_4i29KF5HnqmN5W0iC64HEfmDL-WYbEQmlBnJlZOdnpn6gOvlceJSbbPnUpl-rvbOQ==)
13. [uoguelph.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY5EicCmn2evg94vxlnWU8BemxTXPmjtuqwSZIi_-tM8_xaEYuf1KOpj_9Wl0EmSWUMUCN3edzcL7KAdIKZKQ7VyZ9zlNDCE48yanJkEysBarcM-cs3mnUuFVuZZEC2g==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnZ4vGHmHE-I5UpUwwKk2orQgdGvOmDn_Vfxl3TyaO5_lz9yOA6u7V8Qm7bXk1pRwNhHS7p6gRbG-nnSoFw0nAVvpQjByCGMbN1ZItF175GxTnfhgaGgzpqb8_U2kp2q_mV4aX_Oq-bGawuAdkLvuVcSrE7EiuvdOF1vNkuyVKkIjcuL_vR05UQmT1NzDtgAqAfGxLaq2EDOmfHEc=)
15. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCCAyZkE3sRl3rUsqpmZ0nZjiYy5kLpX8pZlXosGZ8xEtuzGooIY7rNL5Bh3tXA3c9Ep-89m6zah1NZ0CuF1JJ6UIHtubOz762gsxvLq-ipLGw_8vC2EW6AopM18wi8T2vVRtT3j-PdzwIYdkBWZDnDIJ9E6-s_-1OfahKx86iXFq-GeYLeR2pIhs=)
16. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGI0_xyIMRK58QUGU-MzQH3FTxYi-oaCl5dn6l1XWK6WCP8AHiNVsnp7H_AplGRWQSje7JOtIUGDmcValUwi34UwAJSbqGvea0FKYtX8JFOh2C3vUxRiiD791gtoW8Dmg9lWtWlUJt6wQDzP3Fz9srhi-hXt5fY69zMzBTtvZLay-Mf5QQ0)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFkIE2x-YRjJ7hv5jPJTQJRbwWEj7KqrYkX3O-3y1M5TB9nGD07N2h04dSXFlTdfLJgUhz_MKq37KK-OHrWbmBMZIwZ-hVzBjIVVo8Gv8DoCW3XFHe)
18. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcmnDp8S8vCK0FXStS6LiNeTapw6aHodLhbCAXUJ2MtAbeUSwExnVbrXG3a3opVl9PHL9qtH2RSpLTakkk4iHxNFCGhKymevIMJDD7ye5QDlQUmnavIjRE0_3Ye4wQRts_DgWFptQwhQKanjmUKtrVy_tj)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKI_ZMdYbSqaPjgthC0cI3JsZbIisoodWTDIZhHjPjkpJOCCxLCmOsvKgikuFIwrLAU3KRKgYXuDfKJ5q7QATh5mhKDF19zcXG74OO9EWEkOb34NIRoA==)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqSyrozt7UUwyIikk7Er5Nfve97Fj3-YcGokwkl70KKaV_A4qugOWMZDwRWX0lX88hykSpMtY44sBhHITn8msXlXUvaEOB31_RtQv4YCUbWPE9M-Jl6rHttHjN6y8HrLYCqrBb2reIoxjfJbGQ97PTDmti_fit4twnpT45x40Q0YJzDQteLSuF_mOuVj8pQbLBModxSALvFxce_ZzL)
21. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErvpo6uUuT3QXylGDlfaEtpwV7LbSc_LSIDbppCCJRfFjUDKnCTJAFN_xZ8ogAvDa0HR2fLHntxjRGJcgPTUQujyPLQIXP-Qk_urYhCAo3Jy6yfF1Ir0nmuT5s6CPog_XrAw==)
22. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_9_VhcSP3FYmMOvuc77CUkjbxUt6xlbIxHG5OQrhiKkLeQMrfQBLI1COyFDCsrDhWSCC8ZpniFOvABwXWJeqTozvpBHtel5NCzmT11fqXCZqS6_yob0y7ZsXRBMaXXgULGrs=)
23. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrNH1WkcwJmYCK7NfI1IArSS6JO6QGhy6acc9U0YrkltEgkpyi0u2bgezAjnLax8R9guXt0FUMShv5uRM4DpQDpwkk4BMh7fkh6oCiAJWmpyGZsXva7olUW3gDwnxY93UyW5n6HYh_dQ2A-3JsOr65rCmnmJxCijI7K1VyHDW_IRhL4faFB4RCmuFvZ6IJRqCrLmCw6loaMA==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFM4fvtYjBG2FffYD9d6FTBcg0LE_WeMoNfW8CR6_d8PNTkdXSRFtm8d6b3YSnTOLMwnbKvqiZ5OU3B8FYFXWszLu8fzhqQDocvKT5kOHe29aqRm1958g==)
25. [researcher.life](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjR_BJF6kRYg-7HRSJPdAzryXTaROfLLiwSV-SeSSaMz2YRnCYvkkOjoSR4BdnBYTX7eViBvO0E8sv-b6Yqtw6Moj324iok_-56N5yywG4ye6XQiYcYD7JNmEc33vlzaylzLs3lKbeuflItfDKJeVNYNyhBVO-OLjRvT15uuN059Ad0GRfbRLS6_A4zep8MC24YuWGm9CFFX3qXuvZyTqiJL_RjTqrMT-vOIxciN1Qw-23lkWqhIixVlQT1C-RIabCadQ=)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_Jmuco2JId1l3o_c-WT8tAz-Noc-OT7eGNfQXjdnvshiXGO0cs4y7s3rBy5Qse6ZsoAfmiO89lMF3xIotN4qGSneRkAbMKHNHzasy00lDxxQfSb0grBlh9yVoGYgLieQ-C0MN-jE2_7Q2hHOwby33wKY8rL1_GYzsoC8D5l-nBzeCP6c4LqTH8BZnGIsau8VxAKtWWK-bLj8it8oTef7yy9e_ly97Ug==)
27. [ucdavis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBtHe5lVA4QP6DjWaaMfv4dAA-WPbvAbwRdcesMKJdy3-8mDkrYa6fulR-ZJKuxMBk0Fa6B1nAgYY_Obsn2_chk0zaIwSjb4FD9tIRFsb3W7dRJjIjKFJJhQGfbjvTtq1chKhneu-GlunBmQgaN0K_76iapM_ESYwWxVFr)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7Vm05QSBEup1DtXszy3QF8CnrYgKkFT14OPQlBgjoLVgsVuM1J3sCdhuBPsJfDg8RNefuXBsYFY7SDIqk_-F2zn_KhcH4j_aPKcCkzD2XoaUB_mVTTA==)
29. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeFj-hTmVx4dFlANh78Ya8xeIB9kQV7SgtsZNNA-OHeeFtGv_BHPdMe40aGq1TxM6bN2sTafE5tdjEWZeDOX2TO5kwqXnfILcoHkeAFj-D06BXfjfemhCfZm_Y4r6c-_do)
30. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7U7Ss3Z9MA_KvB37j35Sy__roGPymC-AFfeWn9XWz2_DfjmnnvUp_MrKxOLI_yLnMYZENsKu5cgUsFARiFM6SWd-D2raShfXcluJkXhcM0_aKDrcIxZijIDuCyohsKPI=)
31. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_LQiLCol5I5e4syK9G_BQOoUqShqcqWf109YQR7o8Y8yqU1UgQvjrlV8iKQguuKm6tiTlEp76KTGLIEI3-t3qPu_ZWTXdfsNZbXuCAaprMZJazi-L9XFQr93CpvrX7xqICdk=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgU-C1Pk6nOlUzHIbsUy95hvbCL0o1_DWrbVPl3LukVC9zJK8KHK-aU6V-QJriWY-zwHoRu2XVtFPdtYLpE7mzxlFGgXTARyPh6i1KRz95ZB9uudBNEQ==)
33. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqrkql2BCms9lI4gjN81swUWoTV9sxM6m5LxXValsUC1VHTLh52xe6y0G8qVS-Zo9HGi12cPX7-mWGTkRiVl5FlSHOKt7mATulojsTBReyNxkDUO5w0oRAUt9yUFBuEVtA3o0=)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH56hc3KnH7kbizdIo73iFHjzS39KfidMQ1B3kolNHFcw5TBssO36JeTf0Uvlfol6W3HE34CGs8f4wK6LD85lksckYwCmTGlocWiTkYeUemRq-DaZzIk-BznDBvLwXEp9yJLpLRFHj_19p7NEJRarSCert66fAeMn0uVqVR-TUTURJdKuAsYm9vaQJYdCjRclxbirMQTJo9CDtPUqO46PPeUcjnAcOaeiE5XjtBEHTpKnV_NlsI8ASJtNsiCaaN8lntdk1uoueNaQ==)
35. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgkaKkPUmfD01t_a63cW9EG4L75HVYkKUzEKOkD5OkcgNPb81i9KXPaiAysDApEgSMN2CY8cgfZw-bZmdDVv2kbOMykmU1K50wgLZUlWpdvjd7b8DEo9_q8yqyNV6paXifPYW4TN33_Q==)
36. [ucr.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCorXXWvp3v8GygVLEOGO7PpBjR2H6eq3OgFncXUagc9Bn7eEdP6vUBa0R94dPYpPFYIU16Ufb6yzmHrrsqbHo8PvNBeaMv0AeDzrmAM5PDT2NP_UzNCRV5uueIG_owlt5fwRr-uFW24z3gVWkVx0P)


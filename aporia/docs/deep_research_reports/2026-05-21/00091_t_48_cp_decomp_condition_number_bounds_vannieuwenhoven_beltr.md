# T#48 CP decomp condition number bounds (Vannieuwenhoven, Beltran-Breiding)

**Pythia queue id:** 91
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdVeFlQYXFPeUdiWGhfdU1QdWRiZGtRYxIXVXhZUGFxT3lHYlhoX3VNUHVkYmRrUWM
**Elapsed:** 320s
**Completed at:** 2026-05-21T14:32:52.967939+00:00

---

# Condition Number Bounds in Canonical Polyadic (CP) Tensor Decompositions: An Analysis of the Contributions by Vannieuwenhoven, Beltrán, and Breiding

*   **Key Points:**
    *   The **Canonical Polyadic (CP) Decomposition** expresses a tensor as a sum of rank-1 tensors, with widespread applications in data analysis due to its unique identifiability properties.
    *   Research suggests that the absolute condition number of the CP decomposition can be formalized as the inverse of the smallest singular value of **Terracini's matrix**.
    *   The expected value of the condition number for most random tensor rank decomposition problems (specifically proven for rank-2 and asymptotically for higher ranks) is infinite, indicating inherent sensitivity to perturbations.
    *   Conversely, the **angular condition number**, which ignores scaling perturbations, appears to be finite for random rank-2 tensors.
    *   Pencil-based algorithms for computing CP decompositions are demonstrably unstable for an open set of tensors because intermediate problem reductions introduce artificially high condition numbers.
    *   The condition number provides strict mathematical bounds on the convergence radius and speed of Riemannian optimization algorithms used to approximate these decompositions.
    *   "T#48" likely serves as a query tag or refers to specific theorems (e.g., Theorem 48) within the broader CP literature concerning exact recovery bounds, which contextually intersects with the conditioning frameworks developed by these authors. 

**Understanding Tensor Conditioning**
Tensors are multi-dimensional arrays that generalize matrices. Decomposing them into simpler components (rank-1 tensors) is crucial for extracting meaningful patterns in disciplines ranging from machine learning to chemometrics. However, when real-world data is corrupted by noise or measurement errors, these extracted patterns can change drastically. The "condition number" is a mathematical metric that bounds the worst-case sensitivity of the decomposition to these input perturbations.

**The Infinite Average Sensitivity**
A pivotal discovery by Carlos Beltrán, Paul Breiding, and Nick Vannieuwenhoven is that, on average, the condition number for CP decomposition is infinite. This implies that for a random tensor, there is a remarkably high probability that its decomposition is highly sensitive to noise. This theoretical breakthrough explains why many numerical algorithms struggle with tensor decompositions in practice and dictates the necessity of employing geometrically aware optimization methods to circumvent these ill-posed scenarios.

**Algorithmic Implications**
The theoretical bounds on condition numbers directly influence algorithm design. Traditional algebraic methods, such as pencil-based reductions, have been proven to be forward unstable because they inadvertently transform well-conditioned problems into ill-conditioned ones during intermediate computational steps. Modern approaches advocate for Riemannian optimization techniques, which utilize the condition number to bound their convergence properties and dynamically detect proximity to ill-posed critical points.

***

## Introduction to Tensor Rank Decomposition

The **Canonical Polyadic (CP) Decomposition**, historically referred to as the tensor rank decomposition, PARAFAC (Parallel Factor Analysis), or CANDECOMP, is a foundational concept in multilinear algebra [cite: 1]. Introduced originally by Hitchcock in 1927 and rediscovered multiple times across various scientific domains, the CP decomposition expresses a higher-order tensor as a minimal linear combination of elementary rank-1 tensors [cite: 2, 3]. 

Unlike matrix decompositions (such as the Singular Value Decomposition), higher-order tensor decompositions possess a unique property: they are generally unique under mild conditions [cite: 2]. This uniqueness, famously characterized by Kruskal's theorem, allows researchers to interpret the individual rank-1 components as meaningful, disentangled underlying factors driving the observed data [cite: 1, 4]. Consequently, CP decompositions are extensively deployed in psychometrics, chemometrics, signal processing, and increasingly in unsupervised and supervised machine learning settings [cite: 2, 4].

However, the idealized mathematical formulation of the CP decomposition often clashes with practical reality. Real-world tensors are invariably corrupted by representation limits, roundoff errors, and measurement noise [cite: 5]. Because the constituent rank-1 tensors are the primary quantities of scientific interest, it is imperative to quantify how sensitive these elementary tensors are to infinitesimal perturbations of the bulk tensor [cite: 4, 6]. This sensitivity is formalized mathematically through the **condition number** of the tensor rank decomposition [cite: 7, 8].

The collective research of Nick Vannieuwenhoven, Paul Breiding, and Carlos Beltrán has systematically advanced the understanding of condition numbers for CP decompositions. Their work encompasses the rigorous mathematical definition of the condition number, its geometric properties, probabilisitic average-case complexity, and its direct impact on the stability and convergence of numerical algorithms [cite: 8, 9, 10].

## The Mathematical Framework of CP Condition Numbers

To formally study the sensitivity of tensor decompositions, one must define the problem within a differential geometric framework. The **CP decomposition** of a tensor \(A \in \mathbb{R}^{n_1 \times \cdots \times n_d}\) of rank \(r\) is given by:

\[ A = \sum_{i=1}^r p_i = \sum_{i=1}^r a_i^{(1)} \otimes \cdots \otimes a_i^{(d)} \]

where each \(p_i\) resides on the Segre manifold \(\mathcal{S}\), which is the smooth, semi-algebraic set of all rank-1 tensors [cite: 8, 11]. The addition map \(\Phi: \mathcal{S}^{\times r} \to \mathbb{R}^{n_1 \times \cdots \times n_d}\) maps a set of rank-1 tensors to their sum [cite: 11]. The tensor rank decomposition problem is the inverse problem: computing the preimage \(\Phi^{-1}(A)\).

### Terracini's Matrix and the Absolute Condition Number

Vannieuwenhoven formulated a rigorous condition number for this inverse problem, measuring the worst-case relative change in the rank-1 factors \((p_1, \dots, p_r)\) for a given perturbation in the tensor \(A\) [cite: 12]. 

By analyzing the differential of the addition map \(d\Phi\), it is established that the absolute condition number of the CP decomposition evaluated at a specific set of rank-1 factors coincides with the inverse of the least singular value of **Terracini's matrix** [cite: 11, 13]. Terracini's matrix, denoted \(T_{A_1, \dots, A_r}\), is a matrix representation of the tangent spaces to the Segre manifold at the respective rank-1 points [cite: 14]. 

If \(\sigma_{\min}(T)\) denotes the smallest non-zero singular value of Terracini's matrix, the condition number \(\kappa\) is given by:

\[ \kappa(p) = \frac{1}{\sigma_{\min}(T_{A_1, \dots, A_r})} \]

When \(\kappa(p) = \infty\), the derivative is rank-deficient, indicating an ill-posed problem where the set of tensors of fixed rank is not closed, or where there exist infinitely many decompositions (loss of identifiability) [cite: 2, 3]. For robustly identifiable low-rank tensors, the condition number provides an asymptotically sharp bound on the forward error of the decomposition [cite: 1, 15]:

\[ d((p_1, \dots, p_r), (\hat{p}_1, \dots, \hat{p}_r)) \le \kappa \cdot d(A, \hat{A}) + o(d(A, \hat{A})) \]

This inequality establishes the fundamental condition number bounds for CP decomposition: the error in the extracted parameters is bounded linearly by the product of the condition number and the magnitude of the data perturbation [cite: 3, 16].

### Join Decompositions and Geometric Distance

Breiding and Vannieuwenhoven generalized this concept beyond CP decompositions to general **join decompositions** (which include CP, Waring, and Block Term decompositions) [cite: 17, 18]. They proved a geometric condition number theorem: the condition number of a join decomposition coincides with the usual geometric definition on the smooth locus of the join set [cite: 8]. 

Furthermore, they demonstrated that the condition number is inversely related to the distance to the locus of ill-posed tensor rank decomposition problems [cite: 3, 10]. Specifically, a natural weighted distance from a well-posed tensor decomposition to an ill-posed decomposition (one with an infinite condition number) is bounded from below by the inverse of the condition number [cite: 10]. This mirrors classic results in numerical linear algebra, such as the Eckart-Young-Mirsky theorem for matrices, adapting the concept of "distance to singularity" to the multilinear geometry of tensors.

## Average-Case Complexity: The Infinite Condition Number Phenomenon

A cornerstone result in the study of CP decomposition bounds is the probabilistic analysis of the condition number. In computational complexity, algorithms are historically evaluated via worst-case scenarios. However, modern numerical analysis often relies on average-case or smoothed complexity to understand real-world algorithmic behavior [cite: 7, 19]. 

Beltrán, Breiding, and Vannieuwenhoven addressed a monumental question: *What is the average condition number of a random tensor rank decomposition problem?* Their findings, published in *Foundations of Computational Mathematics* (2023), revealed a stark reality regarding the numerical stability of CP decompositions [cite: 8, 20].

### The Infinity of the Geometric Condition Number

The researchers proved that the expected value of the geometric condition number for most random tensor rank decompositions is **infinite** [cite: 20]. 

Specifically, they analyzed random rank-2 tensors and demonstrated that for a wide range of probability density choices, the expected condition number diverges [cite: 7, 8]. Under mild additional assumptions, they proved that this infinite expected value extends to most higher ranks (\(r \ge 3\)) as well [cite: 7, 8]. As the dimensions of the tensor tend to infinity, asymptotically all ranks fall under this categorization [cite: 7]. 

This infinite expectation is not merely a mathematical artifact; it indicates that computing the CP decomposition is a "rara avis" (a rare bird) in numerical linear algebra. Unlike random matrix inversion, where the condition number behaves relatively tamely, random tensor rank decompositions frequently sample near the loci of ill-posed problems [cite: 21]. This results in heavily skewed probability distributions where extreme sensitivity to noise is the norm rather than the exception. Consequently, it is expected and probable that a rank-\(r\) decomposition will lose several digits of precision due to structured or unstructured perturbations [cite: 9, 21].

### The Angular Condition Number

To provide a more nuanced understanding, Beltrán, Breiding, and Vannieuwenhoven also investigated the **angular condition number** [cite: 7, 8]. The standard condition number measures the sensitivity of the rank-1 summands with respect to structured, rank-preserving perturbations [cite: 7]. However, in many applications, the scaling of the rank-1 components is arbitrary or irrelevant; only the angular direction (the underlying factor) matters.

The angular condition number measures the perturbations of the rank-1 summands up to scaling [cite: 7, 8]. Strikingly, the authors showed that while the absolute condition number has an infinite expected value for rank-2 tensors, the expected *angular* condition number for rank-2 tensors is **finite** [cite: 8, 22]. 

Based on numerical experiments, they conjectured that the angular condition number likely remains finite for higher ranks as well [cite: 22, 23]. This dichotomy suggests that while the lengths (scales) of the extracted rank-1 factors are inherently unstable and highly sensitive to noise, the directional subspaces they span can be recovered with bounded expected error.

## Implications for Optimization and Condition Number Bounds

The theoretical condition number bounds are intimately linked with the performance of algorithms designed to compute the CP decomposition. Because finding a CP decomposition is a non-convex, non-linear optimization problem over a semi-algebraic set [cite: 23], iterative numerical optimization methods are universally employed.

### Riemannian Optimization Bounds

Breiding and Vannieuwenhoven proposed a **Riemannian Gauss-Newton (RGN) method with a trust-region** to solve the canonical tensor rank approximation problem [cite: 2, 11]. Standard Euclidean optimization methods often struggle because the set of low-rank tensors (the join set) is not a closed topological manifold [cite: 8]. By reparametrizing the constraint set as the Cartesian product of Segre manifolds, Riemannian optimization explicitly respects the geometry of the problem [cite: 2, 23].

The geometric condition number naturally arises in the theoretical bounds for these algorithms. Specifically, Breiding and Vannieuwenhoven proved that the condition number provides rigorous bounds for:
1.  **The Radius of Convergence:** The local neighborhood around the true decomposition within which the algorithm is guaranteed to converge quadratically to the correct parameters [cite: 2, 8].
2.  **The Convergence Speed:** The multiplicative constant governing the rate of local convergence is directly influenced by the condition number [cite: 2, 8].

If the algorithm approaches an ill-conditioned critical point (where \(\kappa \to \infty\)), the convergence radius shrinks to zero. In their practical implementation, Breiding and Vannieuwenhoven used the condition number to dynamically detect convergence to ill-conditioned points, triggering a randomization procedure to escape these problematic regions [cite: 2]. This geometrically aware optimization outperformed state-of-the-art methods by orders of magnitude in terms of successful recovery times [cite: 2, 11].

### Relationship to Convex Regularization

The study of geometric condition numbers in tensor decomposition shares mathematical DNA with condition bounds in convex regularization. As noted in the literature, Renegar's condition number and its geometric variants (like the Grassmann condition number) provide bounds for the statistical performance of convex regularizers (e.g., \(\ell_1\)-analysis) [cite: 7, 24]. While tensor decomposition is inherently non-convex, the transition of condition number frameworks from linear/convex feasibility problems to semi-algebraic sets represents a major leap in bounding the performance of multi-way analysis [cite: 5, 7].

## The Instability of Pencil-Based Algorithms

Algorithm designers have historically favored algebraic approaches for tensor decomposition because they do not require initial guesses and execute quickly. A popular class of such algorithms operates via a reduction to a linear matrix pencil, followed by a generalized eigendecomposition (e.g., Jennrich's algorithm, generalized Schur decompositions) [cite: 3, 9]. 

However, Beltrán, Breiding, and Vannieuwenhoven published a critical result in the *SIAM Journal on Matrix Analysis and Applications* (2018) proving that **pencil-based algorithms for tensor rank decomposition are numerically forward unstable** [cite: 2, 3]. 

### The Mechanism of Instability

The researchers proved the existence of an open set of \(m \times n \times p\) tensors of rank \(r\) for which these algorithms are arbitrarily unstable [cite: 3, 9]. The root cause of this instability is directly related to the condition number bounds. 

Pencil-based algorithms generally operate by taking slices of the input tensor to form a smaller intermediate problem. For a third-order tensor of size \(n_1 \times n_2 \times n_3\), the algorithm often projects the problem down to an \(n_1 \times n_2 \times 2\) tensor (the "pencil") [cite: 9, 25]. Beltrán et al. demonstrated that the condition number of the CP decomposition for this intermediate \(n_1 \times n_2 \times 2\) tensor can be exponentially larger than the condition number of the original \(n_1 \times n_2 \times n_3\) input tensor [cite: 9].

Because the condition number bounds the forward error, a massive spike in the condition number at an intermediate step guarantees a massive amplification of machine precision (roundoff) errors [cite: 2]. Even if the original tensor problem is perfectly well-conditioned, the algorithm inadvertently routes the computation through an ill-conditioned bottleneck. This theoretical revelation proved that algebraic pencil-reductions are fundamentally inadequate for robust tensor analysis in floating-point arithmetic, cementing the necessity of holistic optimization approaches that act on the full tensor simultaneously [cite: 2, 9].

| Algorithm Type | Mechanism | Stability | Dependency on $\kappa$ |
| :--- | :--- | :--- | :--- |
| **Pencil-Based (Algebraic)** | Reduction to matrix pencil, generalized eigenvalue decomposition. | **Unstable** on an open set [cite: 3]. | Subject to artificially inflated intermediate condition numbers [cite: 25]. |
| **Riemannian Gauss-Newton** | Trust-region optimization over the product of Segre manifolds. | **Stable** within convergence radius [cite: 11]. | Radius and speed bounded strictly by the global condition number [cite: 8]. |

## Invariance Under Tucker Compression

High-dimensional tensors suffer from the "curse of dimensionality," making computations like the CP decomposition and condition number evaluation exceptionally expensive. A standard dimensionality reduction technique is **Tucker compression**, which projects the tensor onto a smaller multilinear subspace (the core tensor) using orthogonal factor matrices via the Higher-Order Singular Value Decomposition (HOSVD) [cite: 1, 8].

A vital question for bounding errors is whether this compression artificially alters the sensitivity of the underlying decomposition. Dewaele, Breiding, and Vannieuwenhoven (2023) proved that **the condition number of many tensor decompositions is invariant under Tucker compression** [cite: 1, 16, 26].

This invariance theorem states that if a tensor is compressed using orthogonal factor matrices, the condition number of the CP decomposition of the compressed core tensor is mathematically identical to the condition number of the original tensor [cite: 1]. Consequently, researchers can aggressively compress massive, high-dimensional tensors into tiny core tensors, compute the CP decomposition and its condition bounds on the compressed space, and lift the results back to the original space without any loss of condition accuracy [cite: 8, 16]. This accelerates the computation of condition numbers by orders of magnitude, making rigorous stability bounds computationally accessible for large-scale industrial data.

## Contextualizing "T#48" in the CP Decomposition Literature

The explicit identifier "T#48" in the context of CP decomposition condition numbers warrants careful contextualization. While the extensive body of work by Beltrán, Breiding, and Vannieuwenhoven defines the definitive geometry and probabilistic bounds of tensor condition numbers, the specific string "T#48" or "Theorem 48" occasionally appears in adjacent theoretical tensor literature, which interlocks with these sensitivity bounds.

1.  **Exact Recovery and Neural Networks (Theorem 48)**: In the context of learning two-layer neural networks with ReLU activations, the weight recovery problem can be formulated as a CP tensor decomposition problem [cite: 27]. Within this literature (e.g., Bakshi et al., 2019), specific theorems (such as Theorem 48) guarantee that with high probability, an algorithm will not fail and will find the exact weight matrix \(V^*\) up to permutation [cite: 27]. The success of these algorithms relies heavily on the input tensor maintaining a stable rank and being well-conditioned, directly tying into the condition bounds established by Breiding and Vannieuwenhoven.
2.  **Nonnegative Tensor Decompositions (Theorem 48)**: In semi-algebraic geometry applied to tensors (e.g., Qi, Comon, Lim), Theorem 48 establishes uniqueness criteria for non-negative CP decompositions. For example, it is proven that for specific ranks (e.g., \(r=2\) or \(3\)), the unique best non-negative rank-\(r\) approximation of a general tensor possesses a unique non-negative rank-\(r\) decomposition [cite: 28]. Identifiability (uniqueness) is a prerequisite for a finite condition number; if a decomposition is not uniquely identifiable, the Terracini matrix becomes rank-deficient, and the condition number reaches infinity [cite: 1, 3].

Thus, while "T#48" may represent a specific user query tag or point to these related bounds in optimization landscapes, the unifying theme remains the mathematical constraints that dictate when a CP decomposition can be robustly and uniquely computed. Beltrán, Breiding, and Vannieuwenhoven provide the geometric backbone (via Terracini's matrix) that dictates these theoretical limits.

## Conclusion

The characterization of condition number bounds for the Canonical Polyadic (CP) decomposition represents a major advancement in numerical multilinear algebra. The collaborative works of Nick Vannieuwenhoven, Paul Breiding, and Carlos Beltrán have transitioned the study of tensor decompositions from heuristic algebraic manipulations to rigorous differential geometry. 

By defining the condition number through Terracini's matrix, they provided an actionable metric for computing the exact forward error bounds of extracted tensor components [cite: 2, 11]. Furthermore, their revelation that the expected condition number for most random CP problems is infinite fundamentally shifts how the scientific computing community views tensor algorithms, highlighting that severe numerical instability is a systemic feature of the problem landscape rather than a mere algorithmic flaw [cite: 7, 8]. 

Armed with this knowledge, they demonstrated the fatal flaws of classical pencil-based reductions [cite: 3], championed the use of condition-aware Riemannian optimization [cite: 8, 11], and validated the safety of orthogonal Tucker compression for drastically reducing computational complexity without distorting the problem's inherent sensitivity [cite: 1, 16]. Ultimately, their framework provides the definitive bounds necessary to trust the output of tensor decompositions in mission-critical applications across the data sciences.

**Sources:**
1. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfWN2EO3smnVTY5h83MZgeRiiASN21w52BtKDDaP8JlQmNHTAc2WxslU8KHOuG5aVCHM_j3SpuZAFqSzfcSBG3IUqvBRcLQzieQ4gcQupnvTzzGvqbyQKFHQphsiH0nJtH6yZHmv3cN9xsCn-hR8rYSwvMSCbY8z8TiSAVnYVVBK9OLQ==)
2. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGg8WWlvsC-RempDftsRqgEVwdtMMHXX5q6DWsTvUNaWNXTQuxWR1cJEjQ0FczzA8AkbrmTo83OkFxzTa7MtMpHFVJIYV9d46nyG2gXDag-wFMyTr-NDgzxdVVwfm8lJoYOQmyGr-dW1f71YLUWv9e0ds9x3aTNdsK6S3Qga_qQzPBNao0lOsHs-TBTouMT5lLevmUuBlXjDZiSJbptKnbTC8Qh0y5LwDrXeQ==)
3. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU3F6n4-y7IpXkDc8awnp0zHuQZwadAisgLsMdeBEFHjdBtlapYmEtjq7PYLHcrXVgD4JR4uplww86woeByDU-ZKD46ts2tJkQsgSXepZi23TN8Kmaokcq1sNxZv_aKUoQWUbSeuiKmQzpwWLALFUKvsQghuA_OFOTPw5B4SS_ZMpj0DJzayN2SiTFbp0KaA72EGZayZA91IklEXCsul5Y)
4. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEOPYpd3ZnDy6OlXSJ-U8QlSWG20IgKVnpj7DzJ0XFRDa6HfEM3U6HUx7Gj3hS6GO3beV7ZPjYnyABU05MUc3JgXwM1OqRl5WBnXR3tNr2WoeaXfB_ruyevRA3)
5. [sciencesconf.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeuoy1UEDlfzyx4ogiDzzlH0zMMCWKgNkZzCXdzAYHpDMVYLhMY5sTo2a-CPkExn_duln2Ar4yQHEgKZhZ3lfnVKCUJcHDllun7z-cx1zZDF7n_iM3D6vqvYsdPrywLWRylJ-g4xxbqCI5e5F7uJcK)
6. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVg_CRtkh6S0F72h7cbVB2arkWqhwdgDuBX1YE6YxdDFR2-gqcDMrAqeqmGP_uBMfQZysCi9c58dC69cyhV-UdX4j_zfgjnEHh9kFDGowfUoxPHuglz3H3lchTdtOzymY6uX510Fz7)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi12AfG4eCZgnIrBbjDU5KO7Y_SqNT23j2VXI74ilRhtE2yK2IrsPBQij0X9buNzmn6d6W5QK33VmrKFzIWOim0W7y_vdNAi74nEkXyWkJ7r5hQzbo3A2lixrQXYLBTVttHxyjd9lDTclZGmaWSps3Nra2CiTN7NJtUVb3nFtQCxL7-zPN376dLMeHMZMwB19FZCjA3sbQigN9jAW2F5yW)
8. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6gTc0asmfgRbidby4CyMRZTHPWmPIVG_LYBYPqGehkucbiajTiphMeBSMmZ6qES1Tb2GGRtVBoB5h8LaLCs_G2ompACDTEaMNYtq2ZDDp1FV_FdQBhkh8DTg-myvNuQszyCRFjy7swKzkl_8BJMS__qUmG6TLEoxyE-OqcI0a7ll9cEJV2YPjJzMyn359orcDf_4PB5y1RGaqhqg8bAa370FNVeeE1Q==)
9. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBzccOO3c--PxnAPiJ10kgpEQ1oehIJLQW0y72DPBoWhuzlzASxQIPElHsl1jwTKneNK52g8CRzPHv8c4YyFWxsVEIowjoSpP0H-hF4Cjd0uNnfgCHGocg-2IKZ6SqDOKdyB_e7Ku35Uegbsj4Y7DyV6VqDnEpRZAbOCH5LJ43v8TahBOX-NJkjuN_bWFqL9ymmOjJeH3PIVhg5pFP88n5)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEddJfqh5prPQwsMZtnjEPknJIHeS-SdNcc8I58V90tDqVwor0Vytnu0pfk4kYyhhpo5BsyFGheB62Nva0UYcGVaFwH4PUI9Fq_IUJ7rLhTbZJbVQBm7mqGt8H2sRuf_VuINCxfpCX219Sds_h9luqXMxDYRXlUFJJ7fALk8--NGJ_b6YtBaIXPhUnUtWVATCuBL23DXZ0Kt2nUZvB0Sn2EI_n6gAMuuSaUWWm_6KA4drDLPQRhDBuiz76n)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkdNgLCZQe_UCyfoiqNSWXh5RpAYIh1MN2iDQXDBySbRQ_QUUlzPjQTIGxXe_GYRdS37CvFe3FKy87a83RpExnPxVUZ-JU-AyWLZkufmpB02NUjw6U-w==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5NOomADW2K1i8dLFVOVYiHc25DMFKgiCrGZzAJ3mV4naF0WopM6BVzbNQ0jifzKrE_LY_b9RLxmiNVBGS7RwBghGOCj2VG_bGpRSHlDa7ASJjq2NLxw==)
13. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHId48xjw0q68WBTAo7VdyHh2Bx78nDmQVVmvBIh81ntFrhcp9ACZiKlxd49EKkw1RW06X25aicxw6XxcRiebJtzeLoCxbvCt5pIcrr6iIy_fao36wo-R49m9PsmuKlEhP_HqEohs9gW3DVtRjXJ84tDtoPyqpAQifiTEO41G5K9YML354UcmukLcQc5l4MLkMpdDOxm-9KM_HWgdKjThxrYOnZH0ngXbe3oPabwtD-L6hl-1h5TJOhlYYCdrk2oYuaQyjsxhFfmY_neRqs)
14. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwBqvJNgD-aTLcBKBk2o4xvDG9pZyHc1V6CZcswpEWjZ6RrdUvbAkRw_jTQkxwDy16uHzsc7ui3HyZtT6hc6LssV70nYFh2fWLdztq2WY-yKEROs6BGdlraCzwTNgT6j1ZPxwkWOAwb7a5esiL0ZC53GK7TGCUx0D5WCYvPeZMS9qD4h2AZO55)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOkI7ajYEmEDbI2IVyOxRuDAFzzbxSqkEmmppzobnh4D62YpSSbU8vS_LNkRxszKewVUgEgxWZIvUVOL6jg_eqPszSC-BKYb9loFN0WIkhGxEnx6eTpQ==)
16. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnjS7C-99wJSfiC5zsBTUrvU3uv11V4zJLsVPgbjyfTdlypPId0oeBjPHTPn-zHzxnClx2Vvmqyz9F1wn4M3shDgBwdIQCAn9wXyc5Ju1aVpH0JxMwIMm81Ns=)
17. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvTzRsx9cq3VeWg0zaqN3jTn_DBPKkjb8dOlywKpaQy0Zrq7ggIpk83NE7Torv9vZCOrPTzfe2vtw99NrQ5hN7J5Ab9mViVMEByAM3mfc7GYiVY6DxmUjEZcchtZvOpU21)
18. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy3fjyodAfsLPsvttms4F4Cjil4iHEUMHHiVE1NOWZ73tcxYUFTs-rm6ui4oqVZcbSwenqMF1pP5mPpR7ug2s4rY6HPYSyfTBLOLFilrYIH5-jGoqZUVQqyOWndlx-GI9ESRE=)
19. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdIIIodv_XmRku_ovuGzX2IeXAPU9yv8Ke72Q-Lyp8W0Xk7xe9hi7WeCVGObZ4STsFYZWj6EkHpZ-pbWTSAl_XHr2eUXkbz3J_1NuIJMac5eY61sGq7nGn86sA20iUTl8=)
20. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIi1VBvXGSEjyJXhnQPbsdeO5_7M6RgG0ubRfMkPgTKa6rKaDxqOOoylQUrKXDtsuXFwXf4-mLduBhOASYjhFCMHDHdLzQ7ueI9QNJ5gmZyHomkJDAXiZcohz4_qU_a-o-enKflKdH3RR2Ab6KY_u6LCoDopFz6OJsIkOkViHqShz5xNDtTUIEMZUfLYc2hEr8u1ALJMD9pfvUw7gdsgCC2w==)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8aq9U9tLvjDuqTwGwD_HPRcQhXxJ4hj_I_WEwV2oMnzm1AbsR175d1qp3crZGW0_Pw3upZZIZ17MmpkWH6B2TKrllkigraxnxEqhVUV8QvEZ0tRBxtaOvwCW-TMYXA1_ah8MY_0UNJZDasfAYejTqK1e4Yew4VnJ3Qnrc2j8Cu9zeiUA_EXU1AlvvKTx1j_d3fWT6eMIJNnJN5ac0TyZY7uZbpBym)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9wMY7bOWXH5FQnLoEL2eegHNSPGybnyGeSpalpvKceeUSErt25-QVFH0Fxjd4KkHGTxVoGRqxbs9ca5JWYn4yGFp1Haxu1KXEEVu_-2DxBC8W8IoYWw==)
23. [researcher.life](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPmAfDHUatMxgEist7fOwhEBEBwcut-al4Bh8G6TuhatqObT_uUq09W9rL1rSR0af9K0lu8LMVwfddnN4gHOyWLeVtLZ1SVYuXcL0k_BazwzGxTJKZ-TG1e5ZOeitWGPXKiiqnWTIpMuGZEMyNf0YIMU0KU1amsPfHs9yF665cS4TolZ171lj2aTuYKDoWUuqZyv8BtcwHRvbNgLLbquCb1tpfnClLIAU1QF_2J8jkFz_JzrUC0iuGksIRxsKL0FLvf30=)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3nMrnY5RX0nw9owE6xEG1TsASfbhA88D57XLoVkxUqu16MNdXAZobrtBHSHMz_zDJy2s3Ron1q1FjlvC1kTYMdJ4JcDMmZyaVJjgtE97QBte3P5n_vq2664gi7-GR_A4rGVgw91lBwy7GDuQKxBKDJmjdOPO2HQO0avRcAbVidjh4agx6M7I=)
25. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtZulhp_iumrjEMZ2_wv9FOGF3nxKCXRpw0e6JE3MiNqyrnF7sCgVst3WBOxHBpfOlHHA8p67Zg274qK5NGVMh0diXfbqz4cma-pFgssInThkxdHZC9lvj7jS07FPguhiQqF3ZjZ3NtnQW0D9uMvNJUnQsf0OewKKGKHvXF7X-CCdtHuiF3CkGzqbmBC1lTMOhGC4F2tGTvs3N-UIiPYEs)
26. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUH5rm0H4MNfnbdK0tAiCHHfI24_KTn-gp_KYBA5aU9yG7ZUzfxMgfA31BIT00ywu7TEhCIH701BmvubyAd24MkeA-WkgMUWFH4aut16z9phYbVA==)
27. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaFdHHed4PQzcwrjGSYv1XPAJ3gFY5FWEsrVzouAt2meMpyabOx5aMtB_pzgM8TH-j_uZMQcDY1s_pdslQS9KESSQplMKUQmQ6R2tZNpV-cfNDkj1XL5fstIfVbFEe7xrPYaw7_qkLzL5vrSqycA==)
28. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAQ9IuQy1TCdXf5ut4tRYz_N-5d8WOxM1ogNzruhSCWwFiIUDD9uhYPehTDePMZsGBja27EB-AvgQijb2o15vqoYj_DswK0FP7n_3BHtHGxDfppA3V0o9EnGM5ZB_dpueCQgAytWAz1ZIzjjFhe71yx16K)


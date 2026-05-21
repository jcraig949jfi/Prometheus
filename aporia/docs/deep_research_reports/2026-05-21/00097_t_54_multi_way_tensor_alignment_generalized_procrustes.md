# T#54 Multi-way tensor alignment (generalized Procrustes)

**Pythia queue id:** 97
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdsUmtQYXRhcUZMeUotc0FQazh1T3FBSRIXbFJrUGF0YXFGTHlKLXNBUGs4dU9xQUk
**Elapsed:** 311s
**Completed at:** 2026-05-21T14:46:37.783545+00:00

---

# T#54 Multi-way Tensor Alignment (Generalized Procrustes): A Comprehensive Methodological Review

**Key Points**
*   **Generalized Procrustes Analysis (GPA)** is a foundational statistical methodology developed to align and superimpose multiple structural representations (matrices or tensors) by minimizing a defined shape distance metric, typically utilizing orthogonal similarity transformations. 
*   **Multi-way Tensor Alignment** expands traditional 2D matrix alignment into higher-order arrays (tensors), proving crucial for heterogeneous data fusion in disciplines ranging from functional neuroimaging (fMRI) and diffusion tensor imaging (DTI) to chemometrics and deep learning representation alignment.
*   **The ProMises Model** significantly improves high-dimensional fMRI data alignment by applying a von Mises-Fisher prior to orthogonal matrix parameters, solving issues of non-identifiability and anatomical interpretability inherent in standard hyperalignment techniques.
*   **Geometry-Corrected Procrustes Alignment (GCPA)** bridges the gap between strict isometric alignment and agreement-maximizing methods like Canonical Correlation Analysis (CCA), offering superior cross-model mapping and retrieval by correcting directional mismatch in deep neural networks.
*   *Complexity and Uncertainty:* While robust mathematically, applying generalized Procrustes alignment to exceptionally high-dimensional ($n \ll m$) or highly noisy environments remains computationally expensive. Iterative algorithms, generalized tensor factorization, and probabilistic frameworks (such as Lie group modeling and von Mises-Fisher distributions) are continuously evolving to mitigate these constraints, suggesting that absolute consensus on a singular optimal alignment algorithm across all disciplines is unlikely.

***

## 1. Introduction and Historical Context

The problem of aligning multidimensional data representations is a pervasive challenge across the physical, biological, and computational sciences. Designated herein as Topic 54 (T#54), the exploration of **Multi-way tensor alignment** through the lens of **Generalized Procrustes Analysis (GPA)** provides a critical mathematical framework for finding a common spatial or structural consensus among complex, diverse datasets. 

Historically, Generalized Procrustes analysis was developed as an exploratory statistical method to compare the shapes of objects or the consensus results of subjective human evaluations [cite: 1]. Initially formulated to analyze data from free-choice profiling—a technique allowing sensory panelists to describe products using their own vocabulary—GPA creates a consensus shape or configuration by compensating for individual scale usage and interpretation differences [cite: 1]. First formalized by J. C. Gower in 1975, GPA extends the Classical Procrustes rotation, which typically aligns a pair of matrices, into a unified methodology capable of superimposing a population of shapes or configurations consisting of three or more entities ($M \ge 3$) [cite: 1, 2].

In the modern computational era, the classical matrix-based GPA has evolved. Datasets are no longer merely two-dimensional tables but exist as multi-way tensors spanning time, space, subjects, and spectral frequencies. Consequently, "Multi-way Tensor Alignment" refers to the suite of advanced mathematical algorithms—including N-way Partial Least Squares (N-PLS), tensor factorizations, and Lie group-based optimizations—that adapt Procrustean geometries to high-order arrays [cite: 3, 4]. 

This comprehensive report explores the theoretical foundations, algorithmic structures, and diverse applications of generalized Procrustes multi-way tensor alignment. We will examine its deployment in chemical structure alignment, non-rigid computer vision, functional magnetic resonance imaging (fMRI), diffusion tensor imaging (DTI), and the bleeding-edge alignment of deep neural network latent spaces via the Platonic Representation Hypothesis.

## 2. Mathematical Foundations of Generalized Procrustes Analysis

### 2.1 The Classical Orthogonal Procrustes Problem
The generic Orthogonal Procrustes Problem (OPP) aims to find an optimal orthogonal transformation that rotates (and sometimes reflects) one matrix to fit another [cite: 5, 6]. Given two matrices $X_1$ and $X_2$, the objective is to minimize the sum of squared differences (the Frobenius norm) between them. Unlike Principal Component Analysis (PCA), which focuses on maximizing variance, Procrustes focuses on minimizing spatial or geometric distance while preserving the internal relative distances of the data points (isometric transformation) [cite: 1, 2].

For best fit, the centroids of $X_1$ and $X_2$ are superimposed (translation elimination) [cite: 2, 7]. A translation elimination matrix can be defined as $T = I - \frac{1}{n}\mathbf{1}\mathbf{1}^T$, ensuring data is mean-centered [cite: 1, 7]. The optimal rotation matrix $H$ is found using the Eckart-Young singular value decomposition (SVD) theorem [cite: 2, 8]. 
Let the cross-covariance matrix be $X_1^T X_2$. Taking the SVD gives $X_1^T X_2 = U F V^T$, where $U$ and $V$ are orthogonal and $F$ is a diagonal matrix of singular values. The optimal orthogonal rotation is given by:
\[ H = V U^T \]
This provides an analytical closed-form solution to pair-wise alignment [cite: 2, 5].

### 2.2 Extension to Generalized Procrustes Analysis (GPA)
When the number of matrices/tensors exceeds two ($N > 2$), standard OPP is insufficient because aligning $X_1$ to $X_2$ does not guarantee the inverse scaling or rotation of fitting $X_2$ to $X_1$, nor does it provide a globally optimal shared space [cite: 2]. Gower (1975) addressed this by establishing a shared universe space, mapping a set of matrices $\{X_i \in \mathbb{R}^{n \times m}\}_{i=1}^N$ into a common reference matrix $M$ via similarity transformations [cite: 2, 5]. 

The classical GPA algorithm relies on an iterative approach:
1.  **Initialization**: Arbitrarily choose a reference shape (often one of the available instances) or set $Y = X_1$ (initial matrix of means) [cite: 1, 2].
2.  **Superimposition**: Rotate, translate, and uniformly scale all current instances to match the reference shape as closely as possible [cite: 1]. 
3.  **Consensus Formulation**: Compute the mean shape of the newly superimposed set of configurations [cite: 1].
4.  **Iteration**: If the Procrustes distance (the squared sum of Euclidean residuals) between the new mean shape and the prior reference is above a predefined convergence threshold, set the reference to the new mean shape and repeat from step 2 [cite: 1].

To avoid trivial solutions where all configurations collapse to the origin, an overall scaling constraint is applied, generally $\sum_{i=1}^m p_i^2 \text{tr}(X_i X_i^T) = \text{constant}$, expressing that the final sum-of-squares around the origin remains unchanged from the raw data [cite: 2].

### 2.3 Distance Metrics Derived from Procrustes
Procrustes analysis yields a set of optimal orthogonal matrices that project each configuration into a common space. From this, researchers extract two primary distance metrics to evaluate multi-way alignment:
*   **Residual-Based Distance Metric**: Measures the squared residuals among aligned matrices. Two matrices may appear different initially but become structurally identical after rotation. The residual distance evaluates how different the matrices are *net of rotations*, thereby capturing intrinsic non-rigid differences [cite: 5].
*   **Rotational-Based Distance Metric**: Exploits the fitted orthogonal matrices themselves, analyzing the magnitude of the rotation or transformation required to align the objects [cite: 5].

## 3. Multi-Way Partial Least Squares (N-PLS) and Tensor Factorization

As datasets become more complex—adding dimensions such as time, spectral wavelengths, or experimental conditions—simple 2D matrices expand into multi-way arrays (tensors) [cite: 3, 9]. Standard matrix factorization necessitates "unfolding" (matricization) of these tensors, which breaks the multi-way correlation structure and leads to a loss of geometric information [cite: 10, 11].

### 3.1 N-PLS Regression for Multi-Way Arrays
To preserve tensor geometry, Procrustes-inspired alignment and decomposition are extended via algorithms like Multi-way Partial Least Squares (N-PLS) regression, pioneered by Bro [cite: 3, 9]. N-PLS is a regression algorithm combining multi-linear tensor decomposition with classical PLS. Instead of predicting a dependent variable matrix $Y$ from an unfolded $X$, N-PLS builds a multilinear model directly on the high-order array $X$ [cite: 3].

In a three-way tensor (e.g., Samples $\times$ Variables $\times$ Time), the N-PLS model establishes a cubic structure, identifying latent variables by maximizing the cross-covariance across all modes simultaneously [cite: 3, 12]. The mathematical formulation factors the tensor into mode-specific weights (e.g., $w^J_a$ and $w^K_a$ obtained via SVD of the reshaped covariance matrix) and extracts a core tensor structure [cite: 3, 13].

### 3.2 Computational Algorithms: fHOPLS and TPN
Because multi-way tensor decomposition is computationally intense, optimized algorithms have been developed. 
*   **fast Higher Order Partial Least Squares (fHOPLS)**: Proposed to address the prohibitive computational costs of standard multi-way algorithms. It provides a multi-way regression model with optimized time complexity, outperforming unfolded PLS and performing effectively on high-dimensional neuroimaging (e.g., EEG/ECoG) data [cite: 14].
*   **Tensor Partial Least Squares-Neural Network (TPN)**: Fuses the alignment/decomposition power of N-PLS with nonlinear mapping. The outer model extracts common latent variables using multi-way tensor decomposition, while an inner Neural Network models the complex nonlinear relationships between the latent variables and the target output. This structure perfectly balances structural preservation with nonlinear predictive power [cite: 15].

## 4. High-Dimensional Alignment in Functional Neuroimaging (fMRI)

One of the most profound modern applications of T#54 multi-way tensor alignment is in neuroscience, specifically in the alignment of multi-subject functional Magnetic Resonance Imaging (fMRI) data. Neural activity across different human brains involves distinct anatomical topographies [cite: 16, 17]. Aligning these using anatomical landmarks alone fails to account for functional variance [cite: 18].

### 4.1 Hyperalignment and the Perturbation Model
To map cognitive states to brain tasks, researchers use Multivariate Pattern (MVP) classification, which requires functionally aligned data across subjects [cite: 17]. *Hyperalignment* utilizes sequential Procrustes orthogonal transformations to rotate subjects' functional neural activities into a common, high-dimensional representational space [cite: 17, 18]. 

Initially, this was modeled using Goodall’s perturbation model (1991), which assumes each subject's matrix $X_i$ is a similarity transformation of a shared reference space $M$, plus a random error matrix $E_i$ [cite: 16, 19]. However, this model faces severe challenges in fMRI:
1.  **Non-identifiability**: The Procrustes method lacks a unique maximum likelihood estimate solution; any linear combination that mixes voxels creates an equivalent mathematical solution but ruins anatomical interpretability [cite: 16, 18].
2.  **Computational Load**: Aligning whole-brain images involves decomposing square matrices roughly equal to the number of voxels (e.g., $200,000 \times 200,000$), which is computationally catastrophic [cite: 16, 20].

### 4.2 The ProMises (Procrustes von Mises-Fisher) Model
To solve these bottlenecks, the **ProMises (Procrustes von Mises-Fisher)** model was introduced [cite: 16, 18]. The ProMises model reformulates functional alignment as a rigorous statistical model by applying a conjugate prior distribution—the von Mises-Fisher (vMF) distribution—to the orthogonal matrix parameter $R_i$ [cite: 16, 20].

The prior assumes that $R_i$ follows a vMF distribution formulated as:
\[ f(R_i) = C(F, k) \exp(\text{tr}(k F^T R_i)) \]
where $F$ is a location matrix parameter and $k$ controls the concentration [cite: 20]. By incorporating this prior, the ProMises model severely penalizes the mixing of spatially distant voxels [cite: 18]. This explicitly integrates topological brain information into the functional alignment, forcing the algorithm to find transformations that not only minimize Euclidean functional differences but also remain anatomically plausible [cite: 16, 18].

### 4.3 The Efficient ProMises Model
For the high-dimensional obstacle ($n \ll m$, where observations $n$ are much smaller than voxels $m$), the **Efficient ProMises** model merges thin Singular Value Decomposition with the Procrustes problem [cite: 16, 20]. It projects the massive $m \times m$ matrix into a lower-dimensional $n \times n$ space using semi-orthogonal transformations that preserve all intrinsic data information. The alignment occurs on these computationally manageable $n \times n$ matrices, subsequently projecting back to the full brain space [cite: 16, 20]. This technique returns unique, highly interpretable transformations, yielding group-level one-sample t-tests that significantly outperform standard anatomical alignments [cite: 20, 21].

## 5. Non-Euclidean Tensor Space: Diffusion Tensor Imaging (DTI)

Diffusion Tensor Imaging (DTI) captures the restricted diffusion of water molecules in biological tissues, providing insight into microstructural tissue properties like brain white matter tracts [cite: 22, 23]. A diffusion tensor is a $3 \times 3$ symmetric, positive-definite matrix representing a covariance structure of molecular diffusion [cite: 22, 24].

### 5.1 The Failure of Euclidean Metrics
Conventional linear or Euclidean averaging of diffusion tensors is deeply flawed because the tensor space is fundamentally non-Euclidean [cite: 6]. Simple Euclidean averaging of two tensors with different orientations leads to a "swelling" effect, artificially increasing the determinant (volume) of the resulting mean tensor and diluting the underlying anisotropy (directionality) [cite: 22, 24]. 

### 5.2 Procrustes Anisotropy (PA) and Tensor Statistics
To properly treat DTI data, GPA and non-Euclidean similarity transformations (rotation, scaling, translation) are utilized [cite: 6]. By utilizing a new parameterization, $D_i = Q_i Q_i^T$, researchers guarantee the positive-definiteness of the tensor. A weighted Procrustes sum-of-squares is established:
\[ \inf_{R_i \in O} \sum_{i=1}^N w_i \| Q_i R_i - \bar{Q} \|_F^2 \]
where $w_i$ are spatial weights and $R_i$ are rotation matrices [cite: 22]. 

By calculating the full Procrustes metric from a highly directional diffusion tensor to an isotropic state (perfect sphere), a novel anisotropy index is derived: **Procrustes Anisotropy (PA)** [cite: 6, 25]. Compared to the traditional Fractional Anisotropy (FA) or Geodesic Anisotropy (GA), PA provides enhanced contrast in highly anisotropic regions of the brain and intrinsically preserves the determinant during interpolation and smoothing operations over tensor fields [cite: 22, 23, 26]. 

## 6. Deep Neural Networks and the Platonic Representation Hypothesis

In the field of artificial intelligence, Multi-way Tensor Alignment is addressing one of the core mysteries of deep learning: representation equivalence across disparate models [cite: 27]. 

### 6.1 The Platonic Representation Hypothesis
The "Platonic Representation Hypothesis" posits that neural networks—despite being trained independently with varying architectures, initializations, and modalities—tend to converge toward a shared statistical model of the world within their latent high-dimensional spaces [cite: 27]. 

Traditionally, investigating this required pairwise mapping, which scales quadratically $O(M^2)$ and fails to create a consistent global reference for $M \ge 3$ models [cite: 28, 29]. A multi-model translation pathway through an intermediate model can yield different results than a direct map, demonstrating severe structural inconsistency [cite: 27, 30].

### 6.2 Universal Alignment via GPA
To achieve true multi-way representation alignment, researchers adapted Generalized Procrustes Analysis to neural latent tensors [cite: 27, 28]. By forcing all $M$ models into a shared orthogonal universe, GPA establishes a universal translation hub [cite: 27, 30]. Every model has a single bidirectional map to the universe, reducing the map count to $O(M)$ and ensuring that translation is transitive and unique regardless of the routing path [cite: 27].

However, empirical evidence reveals a paradox: while orthogonal alignment is mathematically perfect for preserving internal geometric structures (crucial for "model stitching", where a layer of Model A is grafted onto Model B), strict isometries are highly suboptimal for tasks like zero-shot retrieval [cite: 27, 30]. For retrieval, agreement-maximizing methods such as Generalized Canonical Correlation Analysis (GCCA) vastly outperform GPA, because they allow non-rigid scaling and skewing that maximizes cross-model correlation [cite: 27, 30].

### 6.3 Geometry-Corrected Procrustes Alignment (GCPA)
To reconcile the need for both geometric fidelity and high retrieval performance, the **Geometry-Corrected Procrustes Alignment (GCPA)** algorithm was developed [cite: 27, 28]. GCPA utilizes a two-stage paradigm:
1.  **Scaffolding**: It first establishes the robust, globally consistent orthogonal universe via standard GPA [cite: 28, 30].
2.  **Polishing**: It applies a post-hoc, non-linear, shared correction layer that minimizes residual directional mismatches [cite: 28, 30].

By applying GCPA, researchers observe consistently superior multi-lingual translation, cross-camera retrieval, and inter-architecture probing, achieving state-of-the-art results that outperform both raw GPA and GCCA [cite: 30, 31]. 

## 7. Additional Multi-disciplinary Applications

### 7.1 Chemometrics and Molecular Alignment (3D-QSAR)
In analytical chemistry and 3D Quantitative Structure-Activity Relationship (3D-QSAR) modeling, researchers must discover how ligand molecules fit into protein receptors [cite: 32]. A critical challenge is molecular alignment—superimposing diverse molecules into a common 3D space [cite: 32]. Pairwise alignment is heavily biased by the arbitrarily chosen reference molecule [cite: 32]. 

GPA operates as a **consensus molecular alignment** technique [cite: 32]. It minimizes bias by evaluating all molecules collectively, treating molecular structural groups as landmark points and optimizing a permutation Procrustes problem that aligns physical structures while penalizing physically impossible atom connectivities [cite: 32]. Paired with multi-way PLS, consensus alignment via GPA allows for robust modeling of bioactive conformers [cite: 32].

### 7.2 Point Cloud Registration and Geometric Morphometrics
In computer vision, multi-way Procrustes alignment registers 3D point clouds from uncalibrated multi-sensor arrays (e.g., LiDAR, IMU, cameras) [cite: 4, 33]. Under the framework of Lie groups and the Special Euclidean group $SO(d)$, multi-way synchronization algorithms jointly estimate rigid transformations across sensors [cite: 33, 34]. The Affine Iterative Closest Point (ICP) algorithm frequently applies continuous batch optimization to a Lie group Taylor approximation of Procrustes, yielding highly accurate spatial transformations under heterogeneous sensor noise profiles [cite: 4, 35].

In geometric morphometrics—the biological study of shape variation—GPA is used extensively to study skeletal and evolutionary divergence [cite: 36, 37]. Organism anatomies are mapped via discrete landmark points or semi-landmarks. After extracting scaling, rotation, and translation variables via GPA, scientists minimize the internal "bending energy" required to deform a reference grid into the target organism, revealing the allometric trajectories of evolution (e.g., the shape variance of extreme weaponry in *Hoherius meinertzhageni* weevils) [cite: 36, 37].

## 8. Summary of Software and Computational Libraries
A robust suite of analytical libraries has been established for implementing T#54 concepts:
*   **Genstat**: Provides specific directives (`GENPROCRUSTES`, `PCOPROCRUSTES`) for performing generalized Procrustes rotations and hierarchical cluster alignments [cite: 38, 39].
*   **Python Libraries (ProMises / Procrustes)**: Dedicated Python scripts and PyMVPA-based algorithms implement the Efficient ProMises model, providing explicit analytical solutions for rotational, permutation, and symmetric Procrustes problems via Hungarian matching and Kabsch approximations [cite: 6, 21].
*   **TensorPLS**: An R library handling 3D arrays through Tucker decomposition, optimizing N-PLS-DA explicitly for chemometric feature selection and classification [cite: 12, 15].

## 9. Conclusion

Multi-way tensor alignment, centered upon Generalized Procrustes Analysis, stands as an indispensable mathematical mechanism across quantitative sciences. Evolving dramatically from Gower's 1975 formulation for free-choice sensory profiling, the Procrustean core of extracting pure geometric similarity has successfully migrated to handle hyper-dimensional modern data. 

Whether extracting non-Euclidean Procrustes Anisotropy from diffusion tensors, imposing von Mises-Fisher probabilistic constraints on fMRI functional alignment, or bridging distinct neural architectures to prove the Platonic Representation Hypothesis via Geometry-Corrected Procrustes Alignment, the T#54 framework allows seemingly incompatible coordinate systems to negotiate a shared reality. While heavily dependent on resolving computational bottlenecks via sparse SVD iterations and multi-linear factorization, GPA remains the premier theoretical scaffold for aligning multi-way tensors in high-dimensional spaces.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEesr4sGdVbpEREOpGo4CCmLK_pgnaI-NPAQYnHQ2JdQDA_dzUbsLs9NaKrYrP_x4eTioyQInxbqojC_01xy4PlNCmke_ig9e4Tar6z7McfUamW9SlIMSF6hNsTaJr0JypTPTTsAfcNxUq-dmo4xSHLCt4=)
2. [leidenuniv.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8_d7_f_lSfQ_mc3-Wv6nQmqHW0sUTyJ7uBQ-uU17oSh5Rrxrw77eMiZAyFRotoVq1bvuKPCXbbKv_Kqh_tOfrRzERNNpFXK6kQOlil2vWOc1E6TOwZGC4YYbbRRbdr1cEsEn4YGDe7tN4TQ==)
3. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHCDhhLUq_ZT7rx7pkFsesH_BKLMJsasvtrltJK6I056EWZ7WOrTwOvCjPNKbOiJ9TP28NHTJSusDwJcNhqIBBHzQdm0_9iwEf6CVDSGVTw3lZjTDJBCXHIzXcOA==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE07EYMSkkDmVXYsL8MDV67yhvJQ-MIQ0Itn_D7iYVss7KIuP5HhypHAEwOfVQA2LHoa8kD7hZlAtbhrJiTmCAEdEqu5I0VYs4I1OBXM5W1yCzubQHAknA8QY8iIqmLTsovkV8g1-BET8TSWNS_Z0pGnC3lxMjcF28UdAvZDgtVQeEIiAwVysYrl6RZAK2_hqMltFIHjO2PNWF67MYEnYXUVhGntGjfIAFQYcs=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkBjVNJOWTAr6ZKhY7rYrez0gVYtArdctxrSfuIRTntIrlKRMSAP9XnxdTM5jzRIvdKBQGvPLEK3t1Q3xAi7xxIafHjMVfFnwRs2A2WY3l2D5Ct-vW)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExAfHTH3bsxqYTs_T1fD5_mNWL8fAmxY4dGoiaC7dB2QNkoaztibeMU66cGtMe2BagQdLkHlrxXnMdg0SRhe1xCdlNW0itP1OaVY_Eftmqn4jVBh4IADna7wSkWh17YAg71tV9Jyi6gu2VzXtuHuY1k9O089C7spfXD9HIrjldPgyo0h6vLefx0KlB2dI5sX25FC3-ewtkhw71Qa5F4kS_pA==)
7. [thecvf.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErimIIR93VRsx8uvvU3RpTTNgrem4uhJSn2rzz75PqH46ECGpyVLGqz08QaNAQk9q6Sk5FYIVgZhhmxqEPcScN-onnATmfBU9dHGnDUlR8RoxZ6Xgz0-eA4IVDdio10JxHuuqSsgQ=)
8. [unc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJn6qWgEwogNYQJporPSarBvHa_YZ0XM4uMGZ32k7Tgt4wiwOd139fash2cWO7Syz6S-PPAshhjRuqiqCeXYMgF3zAfRFSLkmoaujvVFEmo8xXtABuy4cp8YkEzOdprjbUtcXHaVKWSIlhhFrUoi2yS1Z4)
9. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeFFmKGuVJH2il3rQD3U5z50V4V_JzV102pR7aaY5gUpZTQ27XLSladSwASu3QD_QyKt3tYaZmIIJse6ACPHw2mPUHfyvUmPao1QqJGMdQxy-XDM9RAAlAFpXsCiZoOyA04Ozgq2A=)
10. [ucphchemometrics.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTU0PjmHopFNBqIAILE7FtYKFRb29yhmwpYNkWDDtvz9-9o6DYqtRYVXLaPbpu0mZLQNFIe66CVrhL3Xx_Lbz-aa5uhhy8Pu2-yG9rs_IGzStsoyAEXbmw9MQRV1vKVxteS40lRmdpdBfpLi4Da50=)
11. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV3eo5FfbaQosp7V4dAT9mwQRt7h0xW0vxTvQG7lKg2IHoNNZR61S-CMytxXtgjvDjFRq4H8TUKhbT9jk50jwSdKR_-SDY3qq4-iArwIorqDquEo77TzQ2eGoyooXFEWmYqMkqnNI_jQpTkXd32XA03-0FEb4GXB0oE4jFg--OKTO8KGygAhgV_TdZ64fd7hPoAD8=)
12. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEls39VfBvNDs6UJo9LGttOuwKoRvH8C7qUHG3T6jFmzXNhBJU9JiAKjoIyCpXc33GWMxBROMWQOFSasDBJEgmmFOVDlYRVIgoDLe2FzPBl-3iC73jUcmk5R57h)
13. [ic.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHts7tDTnqrR9ytgq9K7AQfNon-dLLWgtIPWpXZy4TV5kNmDwODQbM_xHDOZQYspnClPYVRzaXQT3SMJ6vacufXxvrlW6UmEiW8vkzB6vEUo51kGWUBjibHmR1CAuMI3WMcfYpEpu0S4-MwEQ3IqoCD10AQeDV8pD_vqV6vGxtntzaFnCK3iTv2JvZncBfrAsxorDCV7eUk4Q3w5K2IneUSCHtH)
14. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMm3E0fgvp-lvon9WxHTN6J0u648GCQmaocG9pcuLFbKYLpZ28sdO7t0xxHInLv4BuvUh8TofeMXfUh-7LD7RUqbd1NYHuKBAUhN_255kPa2ToSyhDom6m6K1C2E5_)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnD9E039C0Hq5TGPEgTcc0BAY50F1f2PMhbMjvBjci9WZYEx7IsTNyHu5jKTfJGvvd_T1zbfOplc_gj8WeCa9zd9dBgi9pdiXreX_05AQwOs7jKWmvLx9fUWsSFuBpHoX-XUO1AdKOyWkBQNZ0J0HrLk5LrEXBea7LamDhUwASgpKweJodW7vxPBWF0of1XDj6ZG6JKg96NmRtp7OJ0K9yip8T4xbojNWMIcp6PjS03a2oUSs=)
16. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqORRPznXV234dvW9LsQEl4Op0YKgwo_RO32xetRs_OHsctujW3DcG4FYR14UqD_dSdRhDyBWqAjoUM9bpw2Q3xUJqOGyAp4XqqbpwHJ03z_nF50rJiBLzzTqzb6zNSnKNMbnce-g=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuf3MpxWzmE-SIVhysBGzvc7F_pakSRBtdy1SjJM7pqgrr0d_E63vzhjU8Gi4JQlwk5PE6ulWDm_3WGdX33ZbD17efYG2hyN6VB0spZtEjM9IuduLvMbywj8Nbib2dKrWtKsjNk29PLLYCbvpNhYztC3k-zScfONr0ZkZ9HMVFkybJhFj55LL5qSUsNodGY8lvM9xIP6--Psg=)
18. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3UEe59Kvry_JupFZs5lFadTYMXbkDYW1S11EcBWeCIFxOQGYUXdsR5xI6R-oZCQR9z5LOXGCqgK8xS3caA0O_qvU3QHnR8Vjt_HWjDEzp_UfTNNgzlQ6NTqn_MeLj)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX2kVchKs50R7rRoDp3ZCHJV_t4b1x58dlzBhyo5435JYQU0TARZ4RVktSPyvHkaBQHtHhlf86YkDU_0IhhfpnHK46TeisvCZkbzuTkjQhko2KubEJ)
20. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmruGb_ojQENj2koJRXzC1LOiudBZWwCJ12Ut95QlVgE7x0_GHV0z2pUI9sah4kgYA-HAHrqSqUc0I6ih5xqTDCFKRVSr63FkZbKmkWC4bzkyHX01BSFj6Wir_-If_tcNftPOYhoa7uIJFPH-K1jJBF52jUn0ZvgpcDMhMHpgIg7kr6hR2xHooRhEFSz_ij_Y=)
21. [unive.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQ3fZQzw3eI1qXyzOE6ATDagFUYvLRxndSNQijlElObL7xQ18QTJyh7qwdkxQ4dTVW7DmKd9gFsYUFaywO5dksROzI7u4bz4CSRGGLOL9b8lGi3TtUx3d3pD0ceW_dcC-DCuB0AKl0dzVWCm5FCoZ6_7w4Q2HV5JaDRumI1ElR4MHscRUdeMT_CCihS2cn9PzMiZrBjlQ=)
22. [ismrm.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhQtCrWjM5_SJr_8e2g-gpq_1DSlyzvtKsXW3jIS2T4ENp4NdzF7mUe35-HFrCeH5k26bTHo6ytPirQXTlHJuPJb_f4asBEDlin6PxYuWxLrTKSFm5rKcqhjXaUeZwaR954Ym3IP_0faqLo1j_QMAgFl3Fse8t)
23. [ucl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGchAYxZ4fxJ718wMDWFrGGwyXwFBBcgxv9Rsfmd6dGd4rV4WFW5Kr2swDw0dtOganesV-xJQNk2TBBOeYN5GPf4aBsPOeTccBpqh05OixepZEj96UJld-EL5nU7zGEwuSBkiK44A==)
24. [utah.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2OQPRgeYEEwtq03th4qATT84s8zis6dVofdvhDsg8r7rxSdY4U2KGeSAO2lunoAWHrAwZBufPhCIFy0Pm_GY5Xcs1BuwMUpdjnTyvS0FFoSIu69cJwuQt376ymc5KG7SMf9Jcl_Gs3wKZyGkPc4sWKRfMaHC4mRK6_vLWfilGQsPfH1CZ)
25. [gitlab.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU43Mn9-uV9AI74aGg-bgEXS3KBJOOqb-S8UUCmrmUbTg4-fjPuAwmaswD4zv7WL7fTVkzspllyj3rOXKc8qxaf94G75aPXRi7wpAA_4QG04teLoUxvubtrfhc)
26. [ijcte.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFdpCOHxNLjhqmTsLe-4Xbamuag-kjR-omwsvrnEQzAtIY-JEL8pqIyerdiEsmhLnTETAULSMomcbkJFs7QmnyJ2KEcPWihLxA2_rj6pPy_lCePWwlj-AbMjhdcSY=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqkoqN27hOndQJRq_18Fjfxl2tWEPcLiNYfEFuHvl7CncJ3t_brMqr_HidT7yBy_Ms5_TIUJRKlw_YBIERDXJgIaXle723VaTHEp2Q9ghToaGiWFn6dEkY)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb95myzxtz9IOsTMrFHa-p-UmEIG-dphUca3DuHZofLD9ctpNOJpNUXrw5A2QtHbc8kf_cToDgrog_OQZzK9N4EabESQ6gTmVkGqmurw021xadZXlK)
29. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFa77jmMoCt5C3v-TxRyN2-t2Tog5ZbXiRp1NHZoacNaZ-DGbTDIDAw8mC2XkCmG7EpIcgt3iOIZrl411C7wT3dldVNy3R9AmblT_XFHnxxeGv25X0rjlLKJ1OL5Fc=)
30. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo9IO1-o-7diRHCB43stphLV_HED_uOuM2La0XS2ce5G_XC7bQBU_FlpdXTrUxC414ZAog0aIeGtJboYUz62TqMrjiytJG5N37J_TQ26LponJQoL9szrj_TydurQLB0aknAus6RPDExosHiIupRm7gsF4bDD_fH9cCHrFA)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzmJdXlb2Q0KVlrNBfcL5UeIJXMaCo_sRBy_bX9FQEDEClIGnmdl1C_6DvpfUDSkzWftzuTDI8UDY8PTyK6ThauAAS4IJhuUdCfgQgVGxr5uzqoBcq2-ZJvXuEJ85oQ2qHIf7aFO9HdVUa6isv7sdyfcf1Rz7UkYejmsGY-9CAyjJsDYH49JjYuLdVlp-MhJTG7FFbK7gCW-37MIqfHqJVRkd5FpvMo-GkMP761CrE5wg5F-kFYGRmrIls)
32. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBN6TtVsRuH7_OhZWO1_Xk76Rhsfw3_Nzc_FigAmZj7Nsb9NfoJB2emY28FseeTrXRoVoZYyPzk34A1qR8kNeon205iIuozqBzaKFMguvzNkMKjkBJv4l_r6GH44_4c8LtlI5j2onltvQb-Fpy9RWP-OyTbrKc3Ar7e7znpXYP_HSSKmdMbqKSALcTqw20XvZiPPMrDUL_AHkvspCv9LqzPJhZPiXpfvmBqE3r)
33. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtkejrcjYpNHfSK2m3SY9F-IsSWm6s3hz9QSG_wpeYcko7nEqQRdZSvuI4t3PVUXWVmVvwdMizHnJspiIv-zoKySzuCf5x9pFQrhB5eVsooKreXHUXK3FKj5vJQafquM6Ga0_RkTBCARiXq7fZu1u6xht8V28Bu4JZjAWj9ZGLe6ZehQ6Xr5_PtB4nFz2wWPhLzpJgLKV_h3Z_4Zkjs6eMthmga-czFO8y8BwzrErAAg==)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFD88GRQoBlZ3b08qu54zwIcfRKfAQU6CvpxZnf7Lf-lXFWEJmS0hdS2jqycGBsZ3KB5sjrFmWH55WhlK-NgqH7O37d20Hz_NS8Qdf6YDo1eFQC0ZX0iQ7SAWthfoAbwVvaS3wyHTTNKFel0He2Dx812ZlvO2Efi050wFCW-e5Ge0K8B252lD8_J5QycTIfStq2_lSPJPsYIOinBlqCQnSrgYZX4aAFAI57xPvUcbLF0cqxjN4GsRCyBWHphEnnc_7gh9ZfTA==)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9IlE53ElQ-TK3teCYxbFJCZvhL_LuUqfQc-lLzdx2iAu82mccQ8qd7FhBl-H1QcIp0Fo06QPdZuTcGmom2cF-hakXrF44M6Hbxc2bNOKk7aX4kqmKstd05yvnaTg6iQIAgS_79XkFgt16WwcyAS8xQRwgkAEriUMDoI6QkoF9xUSSnM6hpDVdsJNkIKq9gihWWCz5z6o5JT-xTAjJm9MTORD3uVx2go0tdppTrNK8BUX-pN5nyqipL9he)
36. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIAjCVbm6aLIQk2MhK2IyZIiO6X2hqUB8uD4oQ8sQJRqBhF_f4Yehe3K36dycgFrciC6URsZjvIRUjEwa47EBcxje46Z43ke2wroP6IJZVgOBT4COuNKksPYykubEwkYr7AohiogA=)
37. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGJZIiRSvaLfgBmiKLG1SvlhCNFVgZlv_TvK2x2eYe-k9XLEHNp-vWh5KswXsNE5ghkkoAmndr5Puar7iT7UXY1utkxg9fd_52vKbqJkNcxZZ-ab6vaZkz50Ecyt_tVceytVCihP3880LwVaJe94r_tK3Nieu4ulwM8V3kvFCZETNC9wZFlBSqlwM8gsGsb_P91AX4rrHgcfZLdPn_04EahwthQYFEfyMzlYXBR2Mdax0Ub5WLtnxd5rtzPQ3xYmNJNIW3-bhgXLf7vSneSE9gwaiG)
38. [vsni.co.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBNdUg4g6e0NnGAACxkvAb_9Ac2sc9gWGiGzvTSLWC2Ta6lAjRfzIVNYsYm_OiScxbznb04KJTFKfz0E8BgqiZhDuvURlH7ZzxwrASBXrkDJ2apHiLtPeFJTw6a7N0H5i5Nu2TyOcpRnJwhcwLr_3YHkNND94osYOcAUs4)
39. [vsni.co.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj1cmmErkPoJcneGxVc9wxpraIiWjeJ33Ubtgik4d2bvSSpWrWo4r3-fkFvPWf-eyZrBTbA-6M9xKABiv80YfdRX63JcKDZZqgCttaiXAaApUxNwL5k4TKO2QVNwr82PwIlsPYGICXaPgQhvoJA9V-EcMXlYHXZ253)


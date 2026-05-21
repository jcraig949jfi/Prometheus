# T#53 Tensor completion sample-complexity bounds

**Pythia queue id:** 96
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcyQmdQYXN5ckNJYUktc0FQdk12NWtBOBIXMkJnUGFzeXJDSWFJLXNBUHZNdjVrQTg
**Elapsed:** 437s
**Completed at:** 2026-05-21T14:45:34.183029+00:00

---

# Comprehensive Analysis of Tensor Completion Sample-Complexity Bounds

**Leading Paragraph**

The problem of tensor completion—the task of recovering a multi-dimensional array from a sparsely sampled subset of its entries—has emerged as a critical challenge across machine learning, computer vision, data mining, and signal processing. While a wealth of literature provides robust algorithms for matrix completion (the two-dimensional case), extrapolating these theoretical guarantees to tensors of order three and higher is non-trivial. Research suggests that tensor completion features a profound computational-statistical gap. Although information-theoretic limits dictate that recovery is possible with a sample complexity linearly proportional to the tensor's dimensions, it seems likely that no computationally efficient (polynomial-time) algorithm can achieve this bound without supplementary data or strategic sampling frameworks. The following report synthesizes contemporary research to explore this gap, detailing the theoretical sample-complexity bounds under various tensor decompositions, optimization strategies, and algorithmic innovations. (Note: The alphanumeric identifier "T#53" within the provided query appears as a common artifact in literature searches—often pointing to statistical $t$-tests with 53 degrees of freedom, specific mathematical equations such as equation (53) in tensor literature proofs, or unrelated military and commercial designations. Consequently, this report focuses squarely on the substantive portion of the query regarding tensor completion and sample complexity).

**Key Points**
*   **Information-Theoretic Limits:** The theoretical minimum number of samples required to recover a low-rank tensor is linearly proportional to the ambient dimension $n$. For a $t$-order tensor, this statistical lower bound is $\Omega(n)$ or $\tilde{O}(n)$, reflecting the model's true degrees of freedom [cite: 1, 2]. 
*   **The Computational-Statistical Gap:** Most standard, polynomial-time algorithms relying on uniform sampling require $O(n^{\lceil t/2 \rceil})$ or $O(n^{t/2})$ samples to succeed, leaving a vast gap between what is theoretically possible and what is computationally tractable [cite: 2].
*   **Closing the Gap via Side Information:** Researchers have demonstrated that incorporating "weak side information"—such as a single vector for each mode lying in the column space of the tensor's matricization—can successfully drive the required sample complexity for polynomial-time algorithms down to a nearly linear $O(n^{1+\kappa})$ [cite: 1].
*   **Adaptive Sampling Strategies:** Moving away from passive, uniform sampling, adaptive sequential algorithms can effectively bypass stringent incoherence assumptions, recovering exact low-rank tensors with sample complexities such as $O(n r^{T-1/2} T^2 \log r)$ [cite: 3].
*   **Advanced Norm Relaxations:** Minimizing alternative norms like the atomic M-norm or max-qnorm achieves optimal sample complexity scaling $O(dn)$ [cite: 4, 5]. Additionally, average spectrum norms help avoid exponential scaling relative to the tensor order when analyzing Canonical Polyadic (CP) decompositions [cite: 6].
*   **Rank-1 Paradigms:** For the specific case of rank-1 tensors, novel algorithmic frameworks mapping the problem to coupled linear systems can attain recovery with no more than $O(d^2 \log d)$ samples, operating independently of standard incoherence constraints [cite: 7].

**Short Sections**
*   **Defining the Gap:** The tension between what is statistically possible (via NP-hard methods) and computationally feasible (via polynomial-time methods) is the defining challenge in modern tensor completion theory.
*   **Methodological Advances:** New non-convex approaches, such as the Riemannian Gradient Method (RGM), have achieved entrywise convergence at near-optimal polynomial-time boundaries, specifically $O(n^{3/2})$ for third-order tensors.
*   **Norm Engineering:** The introduction of novel norms, extending beyond traditional nuclear norms to include the M-norm, max-qnorm, and average spectrum norm, allows mathematicians to bound sample complexities without the curse of dimensionality typical of multi-way arrays.
*   **Active vs. Passive Learning:** Adaptive data acquisition transforms the completion problem, illustrating that interactive querying of entries vastly reduces the necessary sample threshold.

---

## 1. Introduction and Problem Formulation

Tensor completion generalizes the highly successful paradigm of matrix completion to higher-order multi-way arrays. In a standard setup, we consider an unknown underlying tensor $T \in \mathbb{R}^{n_1 \times n_2 \times \cdots \times n_t}$, often simplified as a $t$-order tensor with uniform dimension $n$ along each mode (i.e., $n \times n \times \cdots \times n$). The goal is to estimate $T$ given noisy or noiseless observations of a subset of its entries $\Omega$. Because the total number of entries scales as $n^t$, recovering $T$ is impossible without imposing a structural assumption. This assumption is almost universally that the tensor has a "low rank" $r$. 

### 1.1 The Curse of Dimensionality and Degrees of Freedom
In matrix completion ($t=2$), an $n \times n$ matrix of rank $r$ has $O(rn)$ degrees of freedom. Consequently, exact recovery is possible given $O(nr \log^2 n)$ randomly sampled entries using algorithms like nuclear norm minimization [cite: 8]. However, for a $t$-order tensor, while the number of potential entries is $n^t$, the degrees of freedom for a rank-$r$ tensor remain $O(dn)$ or $O(tn)$ where $t$ (or $d$) is the order [cite: 1, 4]. 

Because the number of free variables is $O(tn)$, the simple information-theoretic or statistical lower bound on the sample complexity—the absolute minimum number of observations required for recovery by *any* method—is $\Omega(n)$ [cite: 1]. Unfortunately, while low-rank matrices can be handled efficiently, computing most low-rank tensor decompositions (and determining tensor rank itself) is famously NP-hard [cite: 3, 8]. 

### 1.2 Defining Sample Complexity
In the context of tensor completion, "sample complexity" refers strictly to the bound on $|\Omega|$, the number of observed entries required to guarantee recovery of the tensor with high probability (or to guarantee a bounded estimation error). The literature divides sample-complexity bounds into two distinct categories:
1.  **Statistical Limits (Information-Theoretic):** Bounds achieved by minimizing structures like the tensor nuclear norm, regardless of algorithmic run-time.
2.  **Computational Limits (Polynomial-Time):** Bounds that current, efficient algorithms can achieve in polynomial time $O(n^c)$ [cite: 1, 2]. 

---

## 2. The Computational-Statistical Gap

One of the most profound phenomena in tensor estimation is the apparent computational-statistical gap, which suggests that efficient algorithms require substantially more samples than statistically necessary to perform recovery.

### 2.1 The Information-Theoretic Lower Bound
As established, specifying a low-rank tensor model requires roughly $O(tn)$ degrees of freedom [cite: 2]. The statistical lower bound for the minimum number of observations required for recovery is therefore $\Omega(n)$ [cite: 1]. Methods utilizing tensor nuclear norm minimization require only $O(n^{3/2})$ observations for a general $t$-order tensor and can approach $\tilde{O}(n)$ in idealized scenarios. However, the tensor nuclear norm is NP-hard to compute, rendering this approach practically inoperable for large-scale data [cite: 1]. 

### 2.2 Polynomial-Time Algorithms and the Matricization Barrier
To bypass NP-hardness, the most widely used polynomial-time approach reduces tensor completion to matrix completion via a process called *matricization* (or unfolding) [cite: 2]. 

By flattening an order-$t$ tensor of rank $r$ into a matrix of size $n^{\lfloor t/2 \rfloor} \times n^{\lceil t/2 \rceil}$, standard matrix completion techniques can be applied. The sample complexity of matrix completion is bottlenecked by the maximum dimension of its rows and columns [cite: 1]. Therefore, the unfoldings that minimize sample complexity yield bounds of $O(n^{\lceil t/2 \rceil})$ [cite: 1]. 

For example, when considering an order-3 tensor, unfolding produces an $n \times n^2$ matrix. Due to its unbalanced aspect ratio, exact recovery relies on one-sided matrix recovery (estimating the left singular subspace), pushing the sample complexity limit to $\tilde{O}(n^{3/2})$ [cite: 2]. More generally, the best existing polynomial-time algorithms, including spectral methods, gradient descent, alternating least squares, and convex relaxations via Sum-of-Squares (SoS), all hit a sample complexity barrier of $\tilde{O}(n^{t/2})$ [cite: 1, 2].

### 2.3 Theoretical Conjectures of Hardness
This discrepancy between $\Omega(n)$ and $O(n^{t/2})$ is not believed to be a mere failure of algorithmic ingenuity, but a fundamental mathematical barrier. Research by Barak and Moitra linked the tensor completion problem to the refutation of random $k$-SAT or 3-XOR instances [cite: 1, 2]. Utilizing the Sum-of-Squares framework and Rademacher complexity, they posited that for the noisy completion of an order-$t$ tensor, any polynomial-time algorithm mandates at least $\Omega(n^{t/2})$ samples. To attempt tensor prediction with fewer observations (e.g., $m = n^{3/2 - \epsilon}$ for a 3-order tensor) would require moderately exponential time [cite: 9, 10]. Furthermore, lower bounds in the Statistical Query (SQ) model demonstrate a sharp gap where gradient-based or local-search methods become trapped by exponentially many local maximizers if they attempt to solve the problem with information-theoretic sample counts [cite: 10, 11].

---

## 3. Advanced Norms: Bridging the Gap via Convex Relaxation

Because standard tensor nuclear norms are intractable, researchers have sought alternative structure-inducing norms capable of tightening sample complexity bounds without catastrophic computational overhead.

### 3.1 The M-Norm and Max-qnorm 
Ghadermarzy et al. analyzed low-rank tensor completion using noisy measurements by pivoting to specific atomic norms. Rather than solving traditional nuclear-norm minimization—which yields the suboptimal polynomial bound of $O(n^{t/2})$—they introduced constraints based on the **M-norm** and **max-qnorm** [cite: 4, 5]. 

*   **Atomic M-norm:** This is an atomic norm whose atoms consist of rank-1 sign tensors [cite: 4, 5].
*   **Max-qnorm:** A quasi-norm representing a direct generalization of the matrix max-norm to high-dimensional tensors. Its unit ball has notably small Rademacher complexity [cite: 5, 12].

By solving a constrained least-squares (LS) estimation using either the convex M-norm or the non-convex max-qnorm, researchers proved it is possible to obtain a sample complexity of $O(dn)$ for an $n \times n \times \dots \times n$ tensor of order $d$ with a low rank $r = O(1)$ [cite: 4, 5]. This result is remarkable because it achieves the nearly optimal statistical limit, successfully matching the degrees of freedom in the tensor [cite: 5, 12]. A generalization of Grothendieck's theorem was utilized to bind the max-qnorm to its nuclear decomposition, mathematically establishing that solving this $M$-norm constrained problem is minimax rate-optimal [cite: 4, 12].

### 3.2 The Average Spectrum Norm for Canonical Polyadic Decompositions
A major hurdle in sample complexity bound derivations is the exponential scaling of constants with respect to the tensor order $N$ (or $t$). To address this for Canonical Polyadic Decomposition (CPD) structures, researchers introduced the **average spectrum norm** and its dual norm [cite: 6]. 

Under uniform sampling models, spectral norms require extremely dense sampling matrices (e.g., requiring observation numbers on the order of $I^{N-1} \log I$) [cite: 6]. In contrast, the average spectrum norm facilitates bounds that avoid exponential dimensional scaling. For a CPD rank-$R$ parametric tensor generating noisy observations (e.g., Poisson or Bernoulli distributions), this analysis yields a sample complexity of $O(IR^2 \log^{N+2}(I))$, successfully achieving linear dependence on the ambient dimension $I$ (or $n$) without requisite dense sampling artifacts [cite: 6]. 

---

## 4. Closing the Computational Gap: Side Information and Active Sampling

If the computational-statistical gap is intractable under uniform, passive sampling and standard algorithms, altering the underlying paradigm is necessary. Two primary mechanisms have emerged: exploiting side information and employing adaptive (active) sampling.

### 4.1 Tensor Completion with Weak Side Information
Yu and Xi showed that the integration of "weak side information" collapses the polynomial-time sample complexity from $O(n^{t/2})$ down to nearly optimal bounds [cite: 1]. 

**Definition of Weak Side Information:** Unlike strong assumptions that demand complete or noisy knowledge of latent subspaces, weak side information merely assumes the availability of a single weight vector for each mode. Crucially, this vector must simply not be strictly orthogonal to any of the latent factors along its respective mode [cite: 1]. This aligns seamlessly with real-world scenarios where metadata (e.g., node features in a recommendation system) provides non-zero inner products with hidden tensor factors [cite: 1, 13]. 

**Algorithmic Impact:** Given this weak side information, an algorithm utilizing nearest-neighbor collaborative filtering can construct matrices of size $n \times n$ to learn coordinate similarities [cite: 13]. These learned similarities facilitate nearest-neighbor estimations of the tensor. For a tensor exhibiting low orthogonal CP-rank, this methodology provably outputs a consistent estimator as long as the number of observed entries is $\Omega(n^{1+\kappa})$ for any arbitrarily small constant $\kappa > 0$ [cite: 1, 13]. 

This represents the first theoretical result showing that side information effectively sidesteps the conjectured $n^{t/2}$ hardness boundary, recovering a low-rank tensor computationally with near-linear sample complexity [cite: 1, 13]. 

### 4.2 Adaptive and Active Sampling
Traditional matrix and tensor completion theory operates under the assumption of passive (uniform random) sampling and relies heavily on the *incoherence* of the underlying object. If a tensor is highly coherent (i.e., its energy is concentrated in a few entries), passive uniform sampling will likely miss the crucial non-zero entries unless the sample complexity is prohibitively high [cite: 3].

Krishnamurthy and Singh addressed this by developing a sequential adaptive sampling framework [cite: 3]. 
*   **Adaptive Strategy for Tensors:** The algorithm actively explores the tensor by maintaining a candidate subspace. If a subsampled component does not fit the currently known subspace, the algorithm actively queries all entries of that component to add it to the basis [cite: 3]. 
*   **Sample Complexity Achieved:** For an $n \times n \times \dots \times n$ tensor of order $T$ and rank $r$, the adaptive strategy dictates that $\Omega(n r^{T - 1/2} T^2 \log r)$ adaptively chosen samples are sufficient for exact recovery [cite: 3]. 
*   **Bypassing Incoherence:** Because the sampling distribution adapts dynamically to the leverage scores (or coherence structure) of the tensor, the method achieves these sample complexity bounds independently of the usual stringent row-space incoherence assumptions [cite: 3, 14].

In a similar vein, multi-pass adaptive sampling schemes utilizing approximate volume sampling have been applied to scenarios such as Wi-Fi fingerprinting via low-tubal-rank tensors. By allocating secondary sampling budgets specifically to highly informative tensor tubes identified in a primary pass, researchers achieve vastly superior reconstruction error scaling for the exact same sample complexity budget compared to uniform bounds [cite: 15, 16].

---

## 5. Non-Convex Optimization: Riemannian Gradient Methods

While convex relaxations offer robust theoretical guarantees, their reliance on singular value decompositions (SVD) at each iteration often renders them unscalable for massive tensors. This has driven a pivot toward non-convex optimization, particularly methods optimized over smooth manifolds, such as Riemannian geometry.

### 5.1 Entrywise Convergence of the Riemannian Gradient Method (RGM)
Wang, Chen, and Wei formalized the sample-complexity guarantees for the vanilla Riemannian Gradient Method (RGM) applied to the low Tucker-rank tensor completion problem [cite: 17, 18]. Optimizing over the manifold of tensors of a fixed multilinear rank allows for algorithms that scale linearly with the tensor size [cite: 19]. 

Historically, while RGM demonstrated computational efficiency empirically, it lacked rigorous theoretical convergence analysis for entrywise error bounds [cite: 17, 18]. The researchers achieved a breakthrough by proving the implicit regularization phenomenon and entrywise convergence of RGM [cite: 18, 20]. To establish this, they relied on a sophisticated "leave-one-out" analytical technique [cite: 17, 20]. 

### 5.2 Specific Sample-Complexity Bounds for RGM
For a 3rd-order tensor $T \in \mathbb{R}^{n \times n \times n}$ with condition number $\kappa$ and multilinear rank $r$, RGM achieves exact recovery with high probability if the sampling rate $p$ satisfies:
\[ p \ge \frac{O(r^6 \kappa^8 \log^3 n)}{n^{3/2}} \]
This translates to a total sample complexity of $O(n^{3/2})$ under the assumption that $r$ and $\kappa$ are constants [cite: 17, 18]. This matches the optimal theoretical bound achievable by polynomial-time algorithms operating without side information.

For a noisy $d$-th order tensor, the requisite sampling rate $p$ is bound by:
\[ p \ge \max \left( \frac{C_1\kappa^8\mu^{3d-1}r^{3d-3} \log^3 n}{n^{d/2}}, \frac{C_2\kappa^{16}\mu^{4d-5}r^{6d-6} \log^5 n}{n^{d-1}} \right) \]
When structural constants are treated as $O(1)$, this elegantly reduces to $p \gtrsim \max ( n^{-d/2} \log^3 n, n^{-(d-1)} \log^5 n )$ [cite: 17].

### 5.3 Comparison of Non-Convex Bounds
A survey of non-convex algorithms for low Tucker-rank tensor completion highlights how different approaches manipulate the bounds [cite: 17]:

| Algorithm | Sampling Complexity Bound | Sampling Scheme |
| :--- | :--- | :--- |
| **Projected GD** (Chen et al., 2019) | $n^2r$ | Gaussian |
| **Regularized GD** (Han et al., 2020) | $n^{3/2}r\kappa^4$ | Gaussian |
| **Riemannian Gauss-Newton** (Luo & Zhang, 2021)| $n^{3/2}r^{3/2}\kappa^4$ | Gaussian |
| **Grassmannian GD** (Xia & Yuan, 2019) | $n^{3/2}r^{7/2}\kappa^4 \log^{7/2} n$ | Entrywise |
| **ScaledGD** (Tong et al., 2021) | $n^{3/2}r^2\kappa \sqrt{r \lor \kappa^2} \log^3 n$ | Entrywise |
| **RGM** (Wang, Chen, Wei, 2023) | $n^{3/2}r^6\kappa^8 \log^3 n$ | Entrywise |

*(Note: While the RGM method introduces a slightly higher theoretical dependency on $r$ (i.e., $r^6$), empirical phase transitions suggest recovery routinely succeeds at sample complexities only linearly proportional to $r$. Furthermore, RGM achieves this while guaranteeing stricter entrywise bounds rather than mere Frobenius norm guarantees [cite: 17]).*

---

## 6. Novel Paradigms: The Rank-1 Case and Coupled Linear Systems

A fascinating sub-field of tensor completion is the strict rank-1 case. Because typical algorithms are designed for generalized rank-$r$ scenarios, their sample-complexity bounds often carry severe dependence on incoherence parameters ($\mu$), leading to worst-case complexities that scale poorly.

### 6.1 Coupled Linear Systems Formulation
Gomez-Leos and Lopez proposed a groundbreaking framework for rank-1 tensor completion that fundamentally changes the algorithmic approach [cite: 7]. Instead of employing optimization over a continuous non-convex landscape, they characterized the rank-1 tensor completion problem (given a uniformly sampled subset of entries in $\otimes_{i=1}^N \mathbb{R}^d$) as a pair of random linear systems [cite: 7].

This formulation cleanly decouples the problem into:
1.  A binary system over the finite field $\mathbb{F}_2$ to determine the **signs** of the underlying tensor vectors [cite: 7].
2.  A real system over $\mathbb{R}$ to determine their **magnitudes** [cite: 7].

### 6.2 Sample and Computational Complexity Bounds
By implementing simple linear algebraic solvers (e.g., Gauss-Jordan elimination) on these decoupled systems, the researchers established exact bounds that bypass previous bottlenecks:
*   **Upper Bound:** For a constant order $N$, the algorithm recovers the tensor requiring no more than $m = O(d^2 \log d)$ uniformly sampled entries with a high probability ($\ge 2/3$) [cite: 7].
*   **Runtime Complexity:** The computational runtime of the algorithm is highly efficient at $O(md^2)$ [cite: 7].
*   **Information-Theoretic Lower Bound:** They complement their algorithm with a theoretical lower bound, proving that a broad class of algorithms cannot succeed with fewer than $\Omega(d \log d)$ samples, confirming the near-optimality of their $O(d^2 \log d)$ upper bound relative to the dimension $d$ [cite: 7].

**Significance:** Prior to this work, existing upper bounds for rank-1 tensor completion derived from higher-rank algorithmic proofs were at least $d^{1.5} \mu^{\Omega(1)} \log^{\Omega(1)} d$ [cite: 7]. Because the incoherence parameter $\mu$ can scale up to $\Theta(d)$ in pathological cases, previous bounds could covertly mask massive sample requirements. The coupled linear system paradigm completely eliminates the dependency on the incoherence parameter $\mu$, isolating an explicit complexity gap between rank-1 completion and higher-rank scenarios [cite: 7].

---

## 7. Deterministic and High-Rank Exceptions

It is worth noting that while standard tensor completion universally relies on low-rank structural assumptions, divergent paradigms exist. In certain localized noise models or deterministic settings, the problem can invert entirely. 

Mickelin and Karaman demonstrated a deterministic tensor completion framework that operates effectively only when the tensor's rank is *sufficiently large*—the polar opposite of the low-rank assumption [cite: 21]. By encoding the significant redundancy inherent in specific locally correlated noise models, they form an overdetermined system of coupled Sylvester-type equations [cite: 21]. Through an alternating linear solver, an $n$-dimensional tensor of full rank $n$ can be exactly recovered even with up to 40% of its entries missing [cite: 21]. While outside the traditional random sampling and low-rank sphere, it underscores the flexibility of tensor algebra in managing missing data via coupled systemic formulations.

---

## 8. Clarification on Query Nomenclature ("T#53")

As briefly noted in the introduction, academic and web databases frequently surface artifacts when queried with alphanumerics like "T#53". To ensure absolute clarity in the provenance of this report's literature:
*   In specific tensor completion proofs (e.g., Wang, Chen, and Wei's Riemannian gradient method derivation), exact mathematical formulations are referenced sequentially, such as equation `(53)`, designated in text as `T.(53)` or `... T . (53).` [cite: 17, 22]. 
*   Outside of this mathematical notation, queries for "T-53" return results for the statistical degrees of freedom in psychological testing (e.g., $t(53) = 3.74, p = 0.001$) [cite: 23, 24, 25], physical components [cite: 26], title policy insurance forms [cite: 27], and French T 53-class naval destroyers [cite: 28]. 
The preceding sections of this report represent the exclusive response to the core scientific concept underlying the query: **sample-complexity bounds for tensor completion**.

---

## 9. Conclusion

The landscape of sample-complexity bounds in tensor completion is defined by a rigorous struggle against the curse of dimensionality. The fundamental degrees of freedom of a tensor suggest that an information-theoretic bound of $\Omega(n)$ samples is sufficient for exact recovery [cite: 1]. However, owing to the NP-hardness of optimal tensor decompositions, standard polynomial-time algorithms rely on matricization and spectral methods that plateau at a computationally hard lower bound of $\Omega(n^{t/2})$ [cite: 2]. 

Recent advancements have successfully charted paths around this barrier. The utilization of weak side information allows algorithms to collapse the polynomial-time sample complexity back to near-linear bounds $O(n^{1+\kappa})$ [cite: 1]. Concurrently, non-convex techniques like the Riemannian Gradient Method guarantee entrywise convergence strictly within the optimal polynomial-time boundaries of $O(n^{3/2})$ for third-order tensors [cite: 17, 18]. In parallel, structural innovations—ranging from sequential adaptive sampling frameworks that eliminate coherence dependencies to the deployment of max-qnorms and coupled linear systems for rank-1 arrays—continue to refine both the algorithmic efficiency and the theoretical limits of tensor recovery [cite: 3, 5, 7]. 

As machine learning relies increasingly on multi-way data architectures, closing the theoretical computational-statistical gap through these hybrid methodologies remains one of the most critical endeavors in high-dimensional statistics.

**Sources:**
1. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf4FVh_ff0N6mFHImuoMdWPGD4bdWAPD1rSl2-RsIK7VzM6PkEjUrt6M1SAaDNb3UEk-tbqEPelV5hy-t1ARxsWO82hqCHC6qajz9AQZ_Tujo1Ep3q42ah2OGXD26vASM=)
2. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyAT5HE-ORvXK7S2jR6aZ-fSl8VYN7sr_ov8BlyXs1GsW77lO4-AE4h6gkK160zIy-fRkWeg3LKomlx2qMEyJwKltbP8taBcFJKFNKxWboYy1NE7undyoErw==)
3. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnx92ZTpSWBKWvJJ21DyGNAi0fn7dkJ4tVcULKRKPo1Wcum95vBhR9adn44GkOPpGP0QxwNGRqMvWL8iKi1PIDAPcn94VRbVrhzF5UKAq2x3CuoJAogzOmXfCNCYPyZIS2Zsj1ZfyoJVkq7hCRYeEgtq0=)
4. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFykNvhtOLPoI8siETwhSptGTz-QPqUjnMSAr-V3RvksDw6gyTGIi--YU8ZJB0gqptTas1HpHOd2wkDUH8BBL499L8JictS8nzV-roGSEpRD8kjFDjeZxuxbwXsFSqlqy42Hoh4WWUht1GD2tkyXq172Nx-h-GW)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGL3ta-QtMfeP1XnASu83IQyfQbpYQi0jVTSRriqllRvNRbg8IidU7aBVmCVM5JnJ02zFdoVzO4UOiXousedNMjHRfL6F3sFu41uvSSkoOBTQSQANveMA==)
6. [osti.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmSeRiXX23MfPPHaVu40dH8M-j4c-I3y010_KlR6yaIxttVn5lCXs_hrj6c6HEypwINWdCiVS9DctsTFwMuSAtSu7uJnadbvWA0FhW31V4g67Xp9au81DymsIskgoP7J8=)
7. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqQn4Q4A9qkKtv0HJhZruZRq-HTT5lcuIE0LHyzNaKFkpYh7DMo2kcdu5KbixUPGUjPpBBViVIWI3bZany78Iv24DjIKUa5BCYIhG4aHIn76_cinzWDcKHSbySX1lg51A=)
8. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuZX-VaVOJZJ1s7HchJmkSS8D9VjWN95mTiIUbO2dZ_FnOldvlLx3w4B-tQiKoy8LUiCgFU8Whzx611RLgO_Or4z9pF6j2C4i6odlkt6gYsml_OBoSoSbz_fSaaAGiaQBwUPcy2bn38erK1gitGKoaAIWNGtbjqsvoESPDz4vMIizBHLtSI17-jCovvVDHvgGocM3vgH6uGghXFw==)
9. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETr2Fi9mpr1AYMtbYF6m2om4czL8-xKplQx7368II_XBKCykI8r7EZd3xkg7JYxJ-JhAvItwFJir4gimXo06g4JXwzhDtX0MyfK4JUHRmD0_H1K3X-p94UpekgMY2gANUBLPxfTWZhilgKvI9nlhQMqXEUbdlvJXhNkmu_SOMHlsuZ9ybhgOsWiIBVsDxCjNR9Sjg3LZXBDPyYDBOCj3Rxk0U3ty7nXUYL6Yhf25DRexJHOnqUyUgnCPxLDEjqCkHLHVBFjLpeRA==)
10. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7iSaGMv_fxhpiHdPUM4N7z1D-u_zn77UUwH-mFMdtXkRUdbz7mTnY7P5wvZkWKJrMWuF9a_oaQvXzDUh8vcS7f2h_inV17fdjvmcoSyyWjXPtIMKGaK3_meY51WuggO0Ru8lvQY69g2HdG9ji6S0Xlto=)
11. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNNAOVuN2CzzZ9sR9dpTATxhKjyEXlBg5U1Vw7-IdSGisK7TSMX84mkgjfzJvbUQ3L1VCRIBsDL79X1zN6YYLdGPZXNyE10GlckCk6HRUrezUNNlM9w4cxoTaURxZH)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEioMlRlhTv7JF0divtJY7m9pA-yH1tt4975rRNdMZLIzAbQN4O8IdDmfmj5wjFaz7L1Npz71IUdImvjt51h-SuS5egR9195n4hB-QGYs1jwiEbUVWZvg==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeUvR33vnraclwNA1XftHjJgJAI317hz7Q-XQYm0cUBG_s7d0D0ZXlrxPocHWBjnmjQj6YEEGfIlvD0376uBfr6tn6273Fk7vNIijl0xkEqt9k8itA1rR7Aw==)
14. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoeTMNOkWfm5iTzhEAv8hcS5-ffAHly-gihzASF0gfM8yVydXXGPurVLZZybMsGlwYy7Xgj8F0cw7hts721pBkzwcZ9KVchRJg0BvwsCGT9jcl9T-pC-YIMNsZq2uECQ==)
15. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFo76ol0CdnRWkX-7Cev8TxTxYLsYdOrfibMvF-wrqFctbiWJNvqWiTaWQCjC7E3H6RK2yymV5VjXv8WObhVB4XUi3Kw9aFvKRQmg0SxYvAtXs4MD9H_iLJ6mp4olCc9j47iDE-3BvoiSQ96146r0QUEQMh_LaZYdTgoBGe)
16. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH76ClSPwaBXOP5yNuVOBgTIF8stIn5WTXZo9BjljcSae4hQyVRmPnOMQDpfMbTEqMwTtDzQ90nHyX2ylfrlOEEE1FmJFOuZqp_KIgA37i4rq4dPI1_nwAjy203XVC2XEhawusyiWAr3xyXDJ0=)
17. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfFCbt6ALXDvrSdDaiePq9ws63_JogEaj5oXNUURR0P2YxieruAvAjaLJ_3UcRlAUMsh4rONs5U01QA1DEpo8RmeXOZw9pu-rZm3M6hjIICgnTOsZ0rw==)
18. [jmlr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpzktNy-FUvr4YAQLL6vCAEVKOh1tPkQOD_Px9UX0uumdSikeO2J3sGBoXTfOO4mg3X2TqCs-Pwz-wUicxK-gejPOdHoe5CIhuFFWs1k5yGY6i5OV7ck6yEmi0CkvF7tpXK6M6t1EG-Doh8byznQ==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6GKMl3Lhbql4jlg0kGF-kpM-dKPOGI8mncaJsZttI8lywVVA96QqWuWXpMjuxAQaOipfHaOjlC85b7QgQTo9TAzgxeli6XWXP-d9kkVa8x845EMw-XC4KiWvG8Q2XQBNtex4BNQMxAS7mYUNPOmEWDx4w0nwsNAmUBimy1Z8cVPi5b5rwoGwUkJjeLgDodHLv58p9cSoyYZxe6sb4Ysm3oyepxcSUYJ4OXUGTs2IUdgUcZKv5VkI1Fe7IrjTz5A8=)
20. [jmlr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHX_XOcQZQm-D8BEyZ2RX5Mj6e3_mYd9_kQIaEYDBOmyDDnZtCq5ewk7kM2FXdJJRU0HPs0kfi1PnDy-eRzRZ7r8k59A8WCETURDELSoSNB2A23arMhaKpRJOvXigVAQ3LwxQ==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFczgr0thfSudwLrXZK2Jlf9yMz-KeyQ48JKUNRLCyazOgPPYeCyg_T1ehvciP5qG6jFKHWN_DM5AXF_2H9R4EQm53lVGQKzpfK2ogBHJiyt32CAwz5tQ==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbaT-c9dIXdAB209VV0588FVEJIXr_2LHiz_0JVda9d-F4xF5XRYi-rRMes0Gj01jozfFWnwmyKbExpasuLkLVupSTKdxvmj2vN-547thh5bnGtwxcGg==)
23. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR-zPE7vgGxLm_dcDgpB2MGgrE0ERR5Asmqrbfx0tT2f9xWlKrhPTPHxjVPGlxBTCkKKbLFnGnowANMZIYjm4PW_sN5-4e1P2ToltqqWA14P-8OhOfuKKAzFw-755GYQEqD2orrpQvCw==)
24. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQmB5lxGbd8gbtWaPcCuwrowEgUssn-e_l6GXavHn6hUIaOwsiXW0cx-m55aN8zvrGbYGb5SwRncGN7VvYVuJmYy6hmLP8CR6r2iRvvqyRqSNAZ5U-7UwG9Chb7LWB8eGmcjK-Qwm_MYggcO5v5gv06-UpQlsVRlF-zfI=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiNNSJxvytVKjWI1x7E549MKfh83sOy8DxbYQkoVbrAInaAQlXXi_yq7frz4RnrWhdQiGsjLsHEo8ftTZJ-wA7-5iJ8mXnUYQt369VSzuPhxKty2iOSvI1QQ==)
26. [helwigcarbon.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-mdc52Aw6PMazw-P1HtRbOrG4aGP97KO5PuzWnqLxPPcTd8zb7UxMUYNhhe_D3nB1smZUp9Bc-zvbxOQIyvMivmUtBF85BrrZw87UGLJly-V6RPosEGAKpye8zY0=)
27. [texas.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDWWjx9YCGvSvOnwPVSja2iy_MCYFCAHbzujRZ4KSblHHWLi9-3vM--puCYqqc8Il-mn1F9nmNV2LHoSJ7cmSdkPRI4G64vZ8JBj6S8Sro2DM-yMgWufYdf9y9n1UjZTDtOiYF77i_nhVrpXWR)
28. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6T94hm2z2nW_7IZZqFoTG8JUtyQTILbi1UvnfHXtC8ynm70w4uyyu18V9B7VgaWdYu_l8ei-XdWujn0FAisecBoXI3zBaRCHf3-FW6Sm9J7qhbaYg5tbkn8DZHXuV_rw4DuzwH5kfeQ==)


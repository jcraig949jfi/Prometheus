# Followup [FU-2026-05-22-020 <- row108]: Precisely characterizing these polylogarithmic factors remains an open problem. 2

**Pythia queue id:** 305
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdhclFQYXZ5LUNlZXRfUFVQODhIMW9RdxIXYXJRUGF2eS1DZWV0X1BVUDg4SDFvUXc
**Elapsed:** 309s
**Completed at:** 2026-05-22T01:47:12.594938+00:00

---

# Status Update: Polylogarithmic Gaps in Tensor Spectral Norm Approximation

*Key Points:*
*   **The Exponent Consensus:** There is strong theoretical consensus that the computational barrier for approximating the spectral norm of an order-$d$ random or average-case tensor dictates a distortion ratio bounded by the polynomial exponent $p^{d/4 - 1/2}$. 
*   **The Polylogarithmic Frontier:** The precise characterization of the polylogarithmic factors isolating the lower bounds (e.g., $p^{d/4 - 1/2}/\text{polylog}(p)$) from the algorithmic upper bounds (e.g., algorithmic frameworks achieving $O(p^{d/4 - 1/2})$) remains a strictly open problem.
*   **Even-Degree Hypercube Bottlenecks:** A parallel and severe structural bottleneck persists in optimizing even-degree polynomials over the Boolean hypercube, owing to the non-existence of standard decoupling inequalities, which functionally paralyzes standard Sum-of-Squares (SoS) rounding schemes that succeed for odd-degree polynomials.
*   **Reverse Detection-Estimation Gaps:** Recent breakthroughs in 2026 have upended traditional statistical-computational heuristics by proving that in tensor spectral norm contexts, computationally efficient detection can be strictly *harder* than computationally efficient estimation, creating novel pathways to certify norm approximation lower bounds.

*Research Summary:*
This report investigates the open problem regarding the exact resolution of the polylogarithmic gap in tensor spectral norm approximation, alongside the associated problem of optimizing even-degree polynomials over the Boolean hypercube. Synthesizing cutting-edge algorithmic upper bounds (Sum-of-Squares hierarchies, polynomial folds, reweighted pseudo-distributions) and computational lower bounds (Low-Degree PTF frameworks, reverse detection-estimation gaps), we evaluate the trajectory of multilinear optimization. The findings highlight a paradigm shift away from traditional planted-problem heuristics, revealing deep computational barriers intrinsic to the loss function (the norm itself) rather than just the statistical model. 

***

## 1. Brief Summary

**The open question interrogates the exact magnitude of the polylogarithmic factors that separate the low-degree polynomial lower bounds ($p^{d/4 - 1/2}/\text{polylog}(p)$) from the state-of-the-art Sum-of-Squares algorithmic upper bounds ($\tilde{O}(p^{d/4 - 1/2})$) for approximating the tensor spectral norm, contextualized within the Prometheus objective to map computational-statistical boundaries in high-dimensional non-convex landscapes.** 

Resolving this gap, particularly as it intersects with the structurally stubborn problem of optimizing even-degree polynomials over the Boolean hypercube—where traditional decoupling inequalities inherently fail—is critical for advancing tensor Principal Component Analysis (PCA), quantum product state learning, and the rounding of higher-order semi-definite programs (SDPs).

## 2. Flagged Findings

### The $p^{d/4 - 1/2}$ Barrier and the Reverse Detection-Estimation Paradigm
Current consensus in the theoretical computer science and high-dimensional statistics communities holds that for an order-$d$ symmetric tensor in $\mathbb{R}^{p^d}$, no polynomial-time algorithm can approximate its spectral norm to a multiplicative distortion better than $p^{d/4 - 1/2}$ (ignoring polylogarithmic factors) [cite: 1, 2]. This exponent has been consistently recovered through multiple, independent analytical vectors: bounds on Sum-of-Squares (SoS) relaxations [cite: 1, 3], limits on low-degree polynomial estimators [cite: 4, 5], and algorithmic guarantees via polynomial folds [cite: 1, 6]. 

However, recent 2026 results have radically shifted the consensus on *why* these lower bounds manifest and *how* they are certified. Historically, the field has relied on the heuristic that if a signal can be estimated, it can be detected; therefore, detection lower bounds inherently implied estimation/recovery lower bounds. This assumption represents a classic **PATTERN_CONDUCTOR_CONFOUND**, wherein researchers confounded the computational complexity of the statistical model's distinguishability (detection) with the computational tractability of evaluating the specific loss metric (estimation error). Tang, Han, and Zhang (2026) proved a "reverse detection-estimation gap" [cite: 7, 8]. They demonstrated that for high-order cumulant tensors, computationally efficient estimation is achievable at sample sizes where computationally efficient detection remains impossible. The confound was broken by the realization that turning an accurate estimator into a successful hypothesis test requires evaluating the tensor spectral norm of the estimator, which is itself NP-hard [cite: 7, 9].

### Failures on the Hypercube and the Overfit to Odd Degrees
A secondary flagged finding involves the stark dichotomy between odd-degree and even-degree polynomial optimization over the Boolean hypercube $\{\pm 1\}^n$. For degree $d=3$, polynomial-time algorithms can achieve an $O(\sqrt{n/\log n})$ approximation [cite: 10]. The community long assumed that similar rounding schemes, perhaps requiring higher levels of the SoS hierarchy, would eventually yield comparable bounds for even-degree polynomials (e.g., $d=4$). 

This assumption manifests as a **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**, where algorithmic design over-indexed on the algebraic symmetries of odd-degree forms. Specifically, odd-degree polynomials permit "decoupling"—relating the optimum of a coupled polynomial $\langle \mathcal{T}, x^{\otimes 3} \rangle$ to a decoupled multilinear form $\langle \mathcal{T}, x \otimes y \otimes z \rangle$ within a constant factor [cite: 10, 11]. For homogeneous even-degree polynomials, this decoupling identity strictly fails [cite: 10, 12]. Consequently, rounding algorithms that rely on evaluating reweighted pseudo-distributions against decoupled bounds collapse when applied to $d=4$ over the hypercube. The consensus now views even-degree hypercube optimization as a structurally distinct class requiring fundamentally new convex geometry or spectral primitives.

## 3. Problem Statement

### 3.1 Tensor Spectral Norm Approximation
The precise mathematical object being interrogated is the spectral norm of a symmetric tensor. Let $\mathcal{T} \in (\mathbb{R}^p)^{\otimes d}$ be an order-$d$ symmetric tensor. The injective tensor norm, or tensor spectral norm, is defined as the maximum absolute correlation with a rank-1 symmetric tensor:
\[ \|\mathcal{T}\|_{op} = \sup_{x \in \mathbb{S}^{p-1}} |\langle \mathcal{T}, x^{\otimes d} \rangle| \]
where $\mathbb{S}^{p-1}$ is the unit sphere in $\mathbb{R}^p$ [cite: 13]. 

Unlike the matrix case ($d=2$), where the spectral norm is computable in polynomial time via Singular Value Decomposition (SVD), computing, or even certifying a constant-factor approximation of, the spectral norm for $d \ge 3$ is NP-hard [cite: 9]. The open problem centers on determining the minimum achievable *distortion*. An algorithm $f(\mathcal{T})$ achieves an approximation distortion $\gamma \ge 1$ if there exist constants $\rho \ge 1$ and $\zeta \ge 1$ such that $\gamma = \rho \zeta$ and:
\[ \rho^{-1} \|\mathcal{T}\|_{op} \le f(\mathcal{T}) \le \zeta \|\mathcal{T}\|_{op} \]
for all tensors $\mathcal{T}$ in the domain [cite: 14].

The objective is to strictly characterize the function $\phi(p, d) = \text{polylog}(p)$ in the gap between the known algorithmic upper bound $\tilde{O}(p^{d/4 - 1/2})$ and the lower bound $\Omega(p^{d/4 - 1/2} / \phi(p, d))$ [cite: 14, 15]. 

### 3.2 Even-Degree Optimization over the Hypercube
The parallel object of interrogation is the maximization of a homogeneous polynomial $P(x)$ of degree $d$ over the Boolean hypercube:
\[ \text{maximize } P(x) \quad \text{subject to } x \in \{\pm 1\}^n \]
The gap in understanding isolates the even-degree cases ($d=2k, k \ge 2$). For $d=3$, Hsieh, Kothari, Pesenti, and Trevisan (2024) [cite: 10, 16] successfully bounded the integrality gap of the SoS relaxation to $O(\sqrt{n/\log n})$. However, for $d=4$, no non-trivial polynomial-time approximation algorithm exists, and the integrality gaps of standard SDP relaxations are poorly bounded. The problem statement asks for the discovery of a non-trivial rounding scheme or a proof of inapproximability for even-degree forms over $\{\pm 1\}^n$ [cite: 10, 16].

## 4. Status & Bounds

### 4.1 Algorithmic Upper Bounds
The last known status of polynomial-time approximation for the tensor spectral norm establishes an upper bound characterized by the application of the Sum-of-Squares (SoS) hierarchy and "weak decoupling" lemmas. 
Bhattiprolu, Ghosh, Guruswami, Lee, and Tulsiani (2017) [cite: 1, 6] proved that in $p^{O(q)}$ time (representing $q$ levels of the SoS hierarchy), one can obtain an approximation within a factor of:
*   $O_d((p/q)^{d/2 - 1})$ for arbitrary polynomials.
*   $O_d((p/q)^{d/4 - 1/2})$ for polynomials with non-negative coefficients, or tensors generated i.i.d. from a Rademacher or Gaussian distribution.
*   $O_d(\sqrt{m/q})$ for sparse polynomials with $m$ monomials [cite: 1, 6].

To achieve this, the authors bypassed standard decoupling lemmas—which blow up the number of variables exponentially with respect to degree—by introducing "polynomial folds," where easy sub-structures (e.g., quadratics) are treated as coefficients in the algorithmic evaluation [cite: 1]. 

### 4.2 Computational Lower Bounds
On the lower bound trajectory, Tang, Han, and Zhang (2026) [cite: 2, 15] utilized the low-degree polynomial framework to certify approximation hardness. They proved that any degree-$D$ low-degree algorithm, where $D \le c_d (\log p)^2$, must incur a distortion of at least:
\[ \frac{p^{d/4 - 1/2}}{\text{polylog}(p)} \]
Under the widespread Low-Degree PTF (Polynomial Threshold Function) conjecture, this bound extends to *all* polynomial-time algorithms [cite: 2, 17]. 

The exact nature of the $\text{polylog}(p)$ factor, denoted $\log^{C_d}(p)$, is conditionally bounded by the properties of the high-order cumulant tensors used to establish the "reverse detection-estimation gap" [cite: 14]. Specifically, the ratio between the algorithmic norm evaluation $\gamma_f$ satisfies $\gamma_f \gtrsim p^{d/4 - 1/2} / (\log p)^{C_d}$ [cite: 13, 14]. The gap between this and the upper bound is strictly isolated to these polylogarithmic terms.

### 4.3 Hypercube Bounds and Integrality Gaps
For optimization over the sphere $\mathbb{S}^{n-1}$, the SoS hierarchy converges to the true optimum with an additive error of $O(1/k)$ at level $k$ [cite: 18, 19]. 
However, for the hypercube $\{\pm 1\}^n$:
*   **Degree $d=3$:** A deterministic $O(\sqrt{n/\log n})$ multiplicative approximation runs in polynomial time, utilizing polynomial reweighting of pseudo-distributions [cite: 10].
*   **Degree $d=4$:** Integrality gaps for the SoS relaxation remain polynomially large. Specifically, for polynomials with non-negative coefficients, there exists an $\Omega(n^{1/6}/\text{polylog}(n))$ gap for the degree-4 case, derived via subgraph counts in random 4-uniform hypergraphs [cite: 1]. For general polynomials, the gap is $n^{\Omega(d)}$ [cite: 1].

## 5. Literature (Primary Sources)

*   **[arXiv:2604.00966] "A General Framework for Computational Lower Bounds in Nontrivial Norm Approximation"**
    *   *Authors:* Runshi Tang, Yuefeng Han, Anru R. Zhang.
    *   *Date:* April 2026.
    *   *Contribution:* Establishes the reverse detection-estimation gap framework. Proves that low-degree algorithms must incur at least $p^{d/4-1/2}/\text{polylog}(p)$ distortion for order-$d$ tensor spectral norm approximation [cite: 2, 14, 15].
*   **[arXiv:2603.26029] "Detection Is Harder Than Estimation in Certain Regimes: Inference for Moment and Cumulant Tensors"**
    *   *Authors:* Runshi Tang, Yuefeng Han, Anru R. Zhang.
    *   *Date:* March 2026.
    *   *Contribution:* Investigates high-order moment tensors. Proves that computationally efficient detection of high-order cumulants is hard when $n \ll p^{d/2}$, despite computationally efficient estimation being possible, isolating the NP-hardness of the spectral norm as the primary bottleneck [cite: 7, 8].
*   **[arXiv:2310.00393] "New SDP Roundings and Certifiable Approximation for Cubic Optimization"**
    *   *Authors:* Jun-Ting Hsieh, Pravesh K. Kothari, Lucas Pesenti, Luca Trevisan.
    *   *Date:* September 2023 (SODA 2024).
    *   *Contribution:* Provides polynomial-time $O(\sqrt{n/\log n})$ approximation for cubic optimization over the hypercube and sphere via pseudo-distribution reweighting and SDP compression via hitting sets. Explicitly documents the failure of standard decoupling for even-degree polynomials [cite: 10, 16].
*   **[arXiv:1611.05998] "Weak Decoupling, Polynomial Folds, and Approximate Optimization over the Sphere"**
    *   *Authors:* Vijay Bhattiprolu, Mrinalkanti Ghosh, Venkatesan Guruswami, Euiwoong Lee, Madhur Tulsiani.
    *   *Date:* November 2016 (FOCS 2017).
    *   *Contribution:* The foundational algorithmic upper bound for this open problem. Introduces "weak decoupling" and "polynomial folds" to bypass variable blowup in standard decoupling lemmas, achieving the benchmark $O(p^{d/4-1/2})$ upper bounds [cite: 1, 6].
*   **[arXiv:2008.02269] "Computational barriers to estimation from low-degree polynomials"**
    *   *Authors:* Tselil Schramm, Alexander S. Wein.
    *   *Date:* August 2020 (Annals of Statistics, 2022).
    *   *Contribution:* Extends the low-degree polynomial framework from detection to estimation/recovery, resolving limits on minimum mean squared error (MMSE) and providing the foundational architecture that later enabled Tang et al.'s reverse-gap proofs [cite: 5, 20].

## 6. Attack Vectors

### 6.1 Live Techniques

#### 6.1.1 Reverse Detection-Estimation Reductions
The most promising vector for solidifying the lower bounds involves exploiting the **reverse detection-estimation gap**. To certify hardness of a norm approximation, researchers identify a statistical testing problem (e.g., distinguishing a planted high-order cumulant tensor from Gaussian noise) where the low-degree detection threshold is strictly larger than the estimation threshold. 
Because the algorithm can accurately estimate the tensor at a low signal-to-noise ratio, any polynomial-time algorithm capable of tightly approximating the tensor's spectral norm could be applied to the estimator's output. This would yield an efficient statistical test that violates the known low-degree lower bounds. The required distortion of the norm approximator is exactly the ratio between the detection threshold and the estimation error. By refining the analysis of the cumulant tensor's concentration bounds, researchers aim to squeeze the remaining $\text{polylog}(p)$ factor out of the distortion inequality [cite: 14, 15].

#### 6.1.2 Polynomial Reweighting of Pseudo-distributions
For algorithmic upper bounds, particularly regarding the hypercube constraint, the "reweighting" of SoS pseudo-distributions is a highly active vector. Given a degree-$\ell$ pseudo-distribution $\mu$ over $\{\pm 1\}^n$, one can define a reweighted pseudo-distribution $\mu'$ by applying a sum-of-squares density polynomial $q$ (where $\tilde{\mathbb{E}}_\mu[q] > 0$). The new pseudo-expectation maps a polynomial $p$ to $\tilde{\mathbb{E}}_{\mu'}[p] = \tilde{\mathbb{E}}_\mu[pq] / \tilde{\mathbb{E}}_\mu[q]$. If $\mu$ satisfies the hypercube constraints, $\mu'$ will as well, provided the degree of $q$ is strictly bounded [cite: 10]. This technique allows algorithms to dynamically "zoom in" on the portions of the pseudo-distribution that align with high-value outputs, bypassing worst-case integrality gaps for odd-degree polynomials [cite: 10].

#### 6.1.3 SDP Compression via Hitting Sets
To make high-degree SoS relaxations tractable, Hsieh et al. introduced techniques to compress $n^{O(k)}$-size SDPs down to $2^{O(k)}\text{poly}(n)$-size SDPs without losing the approximation guarantee. This is achieved by explicitly constructing hitting sets that approximate the domain, functionally discretizing the unit sphere or hypercube in a manner that preserves the integrality of the relaxations [cite: 10, 21]. 

### 6.2 Exhausted Approaches

#### 6.2.1 Standard Decoupling for Even-Degree Forms
The classical method to analyze polynomial optimization is "decoupling", which bounds the objective $\langle \mathcal{T}, x^{\otimes d} \rangle$ by an inherently simpler multilinear form $\langle \mathcal{T}, x_1 \otimes \cdots \otimes x_d \rangle$. For optimization over the hypercube, this step is mandatory to linearize constraints across variables [cite: 10, 12]. However, for even-degree polynomials (e.g., $d=4$), it is now mathematically proven that this decoupling inequality simply does not exist [cite: 10, 22]. Pursuing standard decoupling frameworks to bound even-degree polynomials on the hypercube is considered a dead end.

#### 6.2.2 Pure Gradient / Local Search Methods (Base Rate Neglect)
Attempts to tightly approximate the tensor spectral norm using initialized local search, alternating least squares, or high-order power methods without spectral relaxations have been exhausted for worst-case bounds. This exhaustion is due to **PATTERN_BASE_RATE_NEGLECT**: researchers previously underestimated the sheer base rate of critical points in the optimization landscape. For $d=3$, the landscape of $\sup |P(x)|$ transitions from having $2n$ critical points (the eigenvectors of the $d=2$ case) to having exponentially many local maxima [cite: 3, 19]. Local search methods invariably become trapped in these local attractors, necessitating the global convexification provided by the SoS hierarchy.

## 7. Cross-References

*   **Quantum Product State Learning:** The tensor spectral norm problem is mathematically dual to the problem of finding a pure product state with optimal fidelity to an unknown $n$-qubit quantum state $\rho$. Bostanci et al. showed that computing the optimal fidelity to $\varepsilon = 1/\text{poly}(n)$ is NP-hard, formally reducing polynomial optimization over the sphere to finding the closest product state. This forms an anti-anchor: improvements in tensor norm approximation bounds have direct, cascading implications for the quantum separability problem [cite: 23].
*   **Matrix $p \to q$ Norms (Hypercontractivity):** A closely related open parameter space involves computing the $\|A\|_{p \to q} = \max_{x \ne 0} \|Ax\|_q / \|x\|_p$ norm of a matrix. When $p < q$ and $2 \notin [p, q]$, the problem is highly analogous to tensor norm maximization. Bhattiprolu et al. proved NP-hardness within $2^{O(\log n)}$ for this hypercontractive setting [cite: 24, 25], providing candidate primitives for new tensor hardness reductions.
*   **Tensor Robust Principal Component Analysis (TRPCA):** While tensor *spectral* norm limits dictate worst-case behavior, practical TRPCA models rely on the tensor nuclear norm (the convex envelope of tensor average rank within the unit ball of the tensor spectral norm). Formulations using the tensor total variation Schatten-$p$ norm [cite: 26] sidestep these lower bounds by relying on implicit smooth structure (e.g., intra-view local smoothness in video data), suggesting that defining specific structured subclasses of tensors may completely bypass the $p^{d/4-1/2}$ barrier.
*   **Planted Dense Subgraph and Spiked Tensor Models:** The statistical-computational gaps explored by Schramm and Wein for low-degree polynomials explicitly resolve the MMSE bounds for Planted Dense Subgraph and Spiked Tensor Models [cite: 5, 20]. Understanding how the $\text{polylog}(p)$ factors scale in these models provides direct combinatorial analogies to the high-order cumulant tensors used in the reverse detection-estimation proofs [cite: 8].

**Sources:**
1. [ieee-focs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFg4Mb4j4zOPPcGYU8QMpN3UFItcfqbws-Q6tBVJGV0U_gRwAKB1BmbPZXzkhiJvzG48rKlTPztWgykEgLIEgHIQlToHqZFTVsfVB4QrTL4yYy4dB1jgqb9xa6CQR6ztu3iId3kwYVYzdI=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFONRX9NvsooMsz5CbBg59TbqTe6Cn-TSvQp2C169cnemzuMUXGc-fwsnZvErSGFxZsiNrdhDGu_asP7Ac0wvpDV0yx4x0IhEoc9DV8HflqnFj4CcJEmQ==)
3. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrm119vGMxR15bdQ3orqEQ4Aa0X1A-hltbq3blQr3Fe0l1nV7gxV6fSAerNVYwiwbSNFG-vy_gwGNDefeVJUYj66v8wZkT8bVFoi4HzAYhpkxSE1PDiKX5t5Ukh4QdkAch)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ7NjZG71Hmo31Z8QN6yDE1ijS8547orxPvC03Oo4RNQ1DUAvdOFj4dO3gywsodPEotHA5sbvX1I7-iF5Aix9pEskJpnCMbJzLEqhWaZXPXQg6pxFZOxVEmkhlbzT5T1_GsLu3avb433AQ__ATqAQ_X4_e7JZjI5Fqws-tvA5WXHbxEQj-b9-t1ngFZW8ocgRYLlk3gW39hATUPfszxDumiNmgvrVvkHpe)
5. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHO3rdIN9J9vdiqhxe4FBJzlOepowRMpVZ1bc3FMZviA38JXCbGgEu68yHC8p2joyK5OxFGrd0nU1NL0FOtRvQbRHTCyCWHkCbzKPlu6fhuLC_GTROsyVQO4Tgu9uIO59OnZz-URbb06ab7-TiV1fpZWGYD_09_9krEhZvZd5doimWfW8HtnqawUqe392QFCKjwtgZ_G_UOT7FoMoqs5OScVXyw8DfKrUJbEQBWzE4Q49YR4xGHhRf_lBuCd_raeK0BWvoGZZ-f9AIQWKv7niPTpx4JjsFtQjI=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHmeL-UFNkD85yfw-Z3jZzSa4m7eie-T4clstLw6q1u29EZEHiZmgMQ1SsFeMxdbmFLXrSU77X4g8i78zzoOlqx011mIhlO2L8Sdm7RsdRE0pNdCO6cA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdruSj0K_3qReJQS0Pbe2pB_-vRecfyDZta-PrnOi6AmRzdBEDGypFze5S0baHm_tGhY7Y9RFXkAR6uEmj1dSyQVoj-RCD3k4n8tv-SEAyYyQcCPFnxtdxBw==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGytHe3C9vZaspxNnkVmPUIP0coxSQyXXy8WI3lGGIjsO03qK1snoKeYAkC2u_m7rakUbjyecbNpLDsFzkqU9vyfLyqmcJxZk5BZSSgmmzzvfBPMlzlqw==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGq0GxWOy1Nyc2QvVOw7BCFhrCT-XcYNT9gjXVBSpjw6Pbgb3hWBBvuDteb3OIU8XLAlD_TC3ZY8Lcydr2wQ2NKCo98Dd7LIzQDnl9hzqt9IKTiJG4jxgpGQ7xEpRMNFjWBuVlnkDoxhtCSaMliynLd6xLU_onnIoX7xQErU7H8JpIVQDJCFARe)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuZ0fqCc0yikd8kQ5twzYyOu4SE8_6SlR8O-7jQYr2oYIsXyNCLbxCKs9EMVvYIWNgkNfgjKAhMNA3JStZYsIRTedlrOeBx8nvid28wssaFml7YwsUig==)
11. [sciencesconf.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgHYIiZY67Rd-QBvrJ9ZKzFKtNc7P3hy5nJXnmkn4LQtd-8lDP0Gkg0VRlmsYoQ0HXyLP6LgB1z9AcPsrTo2lpUVr5y28KZPk1CwDXY9zuP6Qql1fS8npzxZJl9W5_4HE3CGNtv4j0VM_dKwOthD0d)
12. [unibocconi.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHn-fGdzUy3-0Wop8Pv1tFKw6Sl150pjkzI4gsY-8SCaMJt96jk9LG9taw2o7mBIM67duCWCA7yeacvap0QwRiKTaYsYGn3i_QChHbBUyUAbxc3kztsqriCAVCuNB2QY78ztyM5-MX9Sfnszr0L-cEuDspCs5sc2lcar0rcOG5S_KC-FAwJLQFgiKMS6O8jYKs6MAHhe4ymND9Q17Qiv8w_g==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFwCHkWs-3Fw-s9sVdR7cKsTpYCOnJGAkMKxwZarJn-jdv-GOFOXHYprWUbsq9LRQCr8Ff_V8WXZ09x-mvWIUtirH7gNWwo3k4Rw7Dluhx3bZnsKthCSE7QA==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsh6UBbXcLgdfAdri_qn6QolgqslNB80rd4A0LcUTcDr3mjPK9ODi4roZWmDCw8_JxE0RBFSGL81HZtv683OKTv7ZI85nd8ueTi7LkJmGY3kudu4x2AQ==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJtBcKGUB3lw2w7zBV2AddXLwRfSSN7ri1cckd4saTg2QkcwgZ0aHyr8AA0x7jnTvT1nvqM53ht0svBWB4CcsMAPmzvQOPJhQcoUo6a2jwxGXE2zaSVKlDhw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH7cX_8JM16eMfL1yWdyM4Cf9qLvCQ0iS-HTPkBTb2foAVCOoE5BYicsWdU8_gsrzcXQeZtrekplbAZzqkkyGOqlYffbKzajAY9ZhcyV2wxmlIaucy2g==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHwmq8e5Me0Y-ALRs10_Vtn20luM_9zN7ZCnNMywRi1QDnvxcUwyMJ0XHrWyWz9yjG_0-7Hdzp9Jjpm4nRMCbzDJ0o5Jn9LDYHCVSK5XXsZOSLqnEhd_uUIA==)
18. [njohnston.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2Mr856ZLJme2XayPXkfWkuVDXSmBrtzl4_txYAOb2PLutyfA1-IOaXUBlEUaVK1gjm802-h4vu84X5gKyEJiUDo2_d-fZQihWrrMk56omP7dd3yrFCg==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxuxgQWqgloP3x27I2lvqxxxcydxm-Tiew7YzxgnfE6mKfe3h9m7VTP_1zfLhk1bxXbQ8vFWiU4rL8BSJgEKLj5DHhu_ZhZgQZn_yK-_VxgGu_yuxxug==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdhJYVaOBrvpCMlY8xLDMvdLlt1ZJwhVzObVTvNw9MTIIWwvp32I-wThijT3RGfPuAQpCYAbjflRkK2IfPuLJb1XPPCVIrAmYsEYSozoBv2Pw4wTFDqw==)
21. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-Gt8E8fnBVr9Cmnx0FEAX1v0eoCoEklGUoQ8R5A4xIt2ApyxxwLWcn55xROvWALgluJTwRziDaZWPqlSYKILzvO4gXcRUq-ilHIRE1SAjhq5B0b1OKKCT1JcHQP2jUNb1pJHWpA_idoPzHXu8)
22. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5a9EV49hKYDN0U_gn0hu8O9I5EWipSCQx5NREqdUbDgWh87K6lZJajmpfhmwD70c7zRvt6ULB2HmBdoAKMRwGrD0qJowQI5nD1glIVb9tPGu8I80BmdGUAwPKc_ymq-pIg1utf_sbxALlh4GHOhomjnkJIQOEpqWrdqEjMRAGUdpV0d36KPRS3IMoE8Tu)
23. [johnbostanci.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1kwwBU0x2kkUxPw-lQpCVXXrFvfGJXPdXpHvBKGAnelC6Er_MRBOWsGi2T6-g_-2J1QYYfUe2QuqBsVp0N0AzntPr8ZihFGySif45ghYpeBqNiXIx6XknasRfz0sAdJ09qr15S3tb3cw9zLyJxSW1CtrTKpev-Mec0Ux13eutv-Y=)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHClKNqP2t8Xnu6F4LOhMgmE8QXQu0cDQuX4vRBE_VQSXy_o7nocM6fFVRd6xeJd1ySzvh2E6HcsOJr18OV7D3T5xE8DF67svGCG30ht4lM1eCrbukZ3JMF6UuUaHCC-PcCA37pz-aX3FM-LGfICgfnNDnX1edYA6xGufu5u4KRb4rEFrr9Cjhk)
25. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRcAToqomvGXZfoyGEFHdou-ySMRVNrG2KD_2vjWe9Adq3WKZPbQ0lBr8TrDzMUNf084AjFWHbehutnLvsbrxlQLt2YKk4sEANdikxvvpp2AMLTcxaLd2fwp0UYBRyHinl8bVh)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGbM7W-ZyNMlyRVAZVJiHUb2CkGTP72MAVUO9kDL-SX3ozZ3nYCl09uA7Jt2hdf3NuvK8WWTt9kVovuHjbyod7apEOGjRt-McbsrXXNb0m89MWgL1c0lMiAb3zTwQwiiZxInVkTFYDnRxJJW_LFYLOLdaR4nwZnSk_9EHJdts3RKqAbLi6Ei9kb62ZMwoks4lLJRSv-iEvZUW0GA==)


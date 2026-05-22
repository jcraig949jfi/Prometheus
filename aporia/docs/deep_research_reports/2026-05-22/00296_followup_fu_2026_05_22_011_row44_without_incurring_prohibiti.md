# Followup [FU-2026-05-22-011 <- row44]: , without incurring prohibitive Singular Value Decomposition overheads) remain open questions in the

**Pythia queue id:** 296
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdlYkFQYXY3QURkV1dfdU1QeWJxNXNRcxIXZWJBUGF2N0FEZFdXX3VNUHlicTVzUXM
**Elapsed:** 251s
**Completed at:** 2026-05-22T01:29:24.920150+00:00

---

# Substrate-Grade Research Brief: SVD-Free Dynamic Rank Adaptation in Tensor-Train Networks

**Key Points:**
*   Research suggests that while Tensor-Train (TT) decomposition theoretically circumvents the curse of dimensionality in multi-modal learning and large language models, dynamic rank adaptation via exact Singular Value Decomposition (SVD) remains an acute computational bottleneck.
*   It seems likely that SVD-free algorithmic alternatives—ranging from Projector-Splitting Integrators (KSL) based on the Dirac-Frenkel Time-Dependent Variational Principle to bilinear factorizations minimizing the Frobenius norm—offer the most promising pathways for real-time rank allocation.
*   The evidence leans toward proxy-based heuristics, layer-wise imprinting quantitation, and Bayesian Hamiltonian Monte Carlo methodologies as optimal mechanisms for end-to-end rank prediction in large-scale deep neural network training.
*   Integrating dynamic rank tracking without static predefined bond dimensions resolves capacity-constraint issues, allowing model weights to adapt dynamically while remaining hardware-aware. 

**Introduction**
The rapid evolution of machine learning, spearheaded by Large Language Models (LLMs) and Deep Learning Recommendation Models (DLRMs), has led to parameter scaling that aggressively taxes available hardware resources. Low-rank tensor methods, specifically the Tensor-Train (TT) format, serve to alleviate the spatial complexity of massive weight matrices. However, enforcing a static, predetermined tensor rank fundamentally caps the expressivity of the model. Identifying the optimal rank dynamically over the course of training—without incurring the exponential and prohibitive costs of sequential Truncated Singular Value Decomposition (SVD)—is a highly active front in applied mathematics and computer science. This report consolidates the latest substrate-grade intelligence regarding this precise challenge.

***

## 1. Brief Summary

**Question in one line with Prometheus context:** How can the internal bond dimensions (TT-ranks) of a Tensor-Train network be adapted dynamically during neural network training to optimize the parameter-capacity trade-off without invoking the computationally prohibitive overheads of full or truncated Singular Value Decomposition (SVD)? 

**Prometheus Context:** Within the Prometheus operational environment—and highly relevant to Aporia's ongoing investigations into high-efficiency model scaling—identifying scalable rank-adaptive mechanisms allows LLMs to organically adjust their informational capacity in real-time. If tensor ranks can be governed dynamically without the blocking constraints of recursive SVD unfoldings, models can start highly compressed (small rank) and grow selectively in capacity (rank allocation) where gradients dictate higher complexity is needed, yielding exponential improvements in GPU throughput, VRAM utilization, and communication overhead in distributed federated clusters.

## 2. Flagged Findings

**Current Consensus:**
The prevailing consensus in tensor network research stipulates that the canonical TT-SVD algorithm is the mathematically optimal procedure for constructing TT representations with prescribed error or rank constraints [cite: 1, 2]. Standard literature asserts that TT-SVD, by matricizing the tensor along successive modes and applying truncated SVD to extract orthonormal bases, yields a structured low-rank decomposition with quasi-optimal error guarantees [cite: 1]. It is widely accepted that setting a global relative error bound, combined with step-and-truncate SVD algorithms, offers the most rigorous path to compressing weight matrices [cite: 2, 3].

**Where the Consensus Might Be Wrong (Contrarian Interrogations):**
Emerging literature heavily disputes the pragmatic utility of the SVD-centric consensus in deep learning applications. The rigid dependence on SVD for rank adjustment forces recurrent memory allocations and dense matrix formulations that cripple GPU operations. Specifically, researchers are discovering that:
1.  **SVD is not strictly required for rank discovery.** Dynamical Low-Rank Approximation (DLRA) and Projector-Splitting Integrators (PSI) demonstrate that tracking the evolution of the tensor on a low-rank manifold via differential equations completely bypasses SVD truncation [cite: 4, 5]. 
2.  **Nuclear norm optimization is unscalable.** Optimization-based approaches that use tensor nuclear norm as a surrogate for tensor rank necessitate SVD and are computationally intensive; Bayesian inference or proxy-based classifications scale significantly better [cite: 6, 7].
3.  **Hardware execution contradicts theoretical FLOPS.** While tensor-compressed operations inherently reduce theoretical FLOPS, their reliance on sequences of small-size SVDs and tensor contractions causes massive runtime overheads on modern GPUs engineered for large dense matrices [cite: 8]. Methods like CoMERA achieve 2-3x empirical speedups precisely by discarding traditional TT-SVD bottlenecks [cite: 9, 10].

**Flagged Systemic Vulnerability: `PATTERN_VRAM_TRUNCATION_ARTIFACT`**
The field exhibits a severe blind spot aligned with `PATTERN_VRAM_TRUNCATION_ARTIFACT`. In attempts to limit SVD overhead, engineers often employ aggressive, hard-coded truncation tolerances to forcefully constrain VRAM peaks during unfolding operations. This non-adaptive singular value thresholding inadvertently discards mathematically critical eigenvectors during intermediate TT-core generation. As a result, the deep learning model converges towards artifactual sub-optimal minima, creating a false empirical signal that low-rank TT formulations are inherently less capable than full-rank equivalents.

**Flagged Systemic Vulnerability: `PATTERN_CONDUCTOR_CONFOUND`**
Furthermore, the literature frequently suffers from `PATTERN_CONDUCTOR_CONFOUND`. When novel, rank-adaptive TT-network optimizers report state-of-the-art accuracy retention, authors consistently misattribute the success directly to the topological superiority of the Tensor-Train format. In reality, the success is heavily confounded by the implicit regularization and noise injection inherent in the stochastic SVD-free rank-growth heuristics (such as randomized UTV factorizations or greedy Bayesian sampling) which act as robust generalized regularizers rather than pure structural benefits [cite: 1, 6].

## 3. Problem Statement

**Precise Object / Result Being Interrogated:**
The targeted mechanism is the real-time, dynamic adjustment of the **TT-rank** (often represented as a tuple of integers $\{r_0, r_1, \dots, r_{d-1}, r_d\}$ where $r_0 = r_d = 1$) within a Tensor Train decomposition of a high-dimensional tensor $\mathcal{X} \in \mathbb{R}^{n_1 \times n_2 \times \dots \times n_d}$. 

The classical mapping defines the elements of $\mathcal{X}$ as:
\[ \mathcal{X}(i_1, i_2, \dots, i_d) = \mathcal{G}_1(i_1) \mathcal{G}_2(i_2) \dots \mathcal{G}_d(i_d) \]
where each $\mathcal{G}_k \in \mathbb{R}^{r_{k-1} \times n_k \times r_k}$ is a core tensor [cite: 11]. 

The problem interrogated is the **Singular Value Decomposition (SVD) computational bottleneck**. In classical rank-adaptation (e.g., TT-SVD), one must unfold intermediate tensors into matrices of size $\mathcal{O}(r_{k-1} n_k \times \prod_{j=k+1}^d n_j)$, compute the full or truncated SVD, and truncate singular values below a threshold $\epsilon$ to find the new rank $r_k$ [cite: 2, 3]. The computational cost of this matrix SVD operation scales as $\mathcal{O}(M N \min(M, N))$, which grows exponentially or prohibitively large with the tensor modes [cite: 12, 13]. 

The precise goal is to identify mathematical and programmatic primitives that enable $r_k$ to dynamically expand (to capture necessary gradient complexity) or contract (to save computational bounds) during forward/backward passes in neural networks, without requiring the explicit computation of $\mathcal{O}(M N \min(M, N))$ SVDs, while mathematically guaranteeing that the resultant tensor stays as close to the target underlying manifold as possible.

## 4. Status & Bounds

**Last Known Status:**
The field is currently fracturing into three highly viable branches to bypass SVD overheads:
1.  **Dynamical Low-Rank Approximation (DLRA):** Propagating the tensor over a low-rank manifold via the Projector-Splitting Integrator (KSL algorithm) without step-and-truncate [cite: 4, 5]. 
2.  **SVD-Free Bilinear Formulations:** Replacing nuclear norm constraints with the minimization of the Frobenius norm of two smaller factorized matrices ($X_{[k]} = UV$) via Alternating Direction Method of Multipliers (ADMM) [cite: 14, 15].
3.  **Hardware-Aware Multi-Objective Optimization:** Methods like CoMERA and LWIQ use proxy classifiers and gradient sensitivity to increase/decrease tensor ranks programmatically, achieving substantial GPU speedups [cite: 8, 16].

**Current Best Bounds & Complexity:**
*   **Storage Complexity:** TT formatting inherently bounds storage to $\mathcal{O}(d n r^2)$, bypassing the dense $\mathcal{O}(n^d)$ scaling [cite: 11, 17]. 
*   **Runtime Complexity (Classical TT-SVD):** Classical algorithms scale as $\mathcal{O}(N d r^2)$, but the matricization SVD step creates harsh constant factors and un-parallelizable GPU chokepoints [cite: 1, 3].
*   **Runtime Complexity (Projector Splitting DLRA):** Sweeping procedures update tensor cores natively, resulting in bounds that scale strictly linearly with the number of dimensions and polynomially with the tensor rank without $r^3$ bottlenecks. Riemannian approaches (RTTC) lower asymptotic complexity from $\mathcal{O}(d |\Omega| r^3)$ to $\mathcal{O}(d |\Omega| r^2)$ [cite: 17].
*   **Runtime Complexity (TT-UTV):** Replacing classical SVD with UTV decompositions via random projections guarantees global relative error $\leq \epsilon$ while reducing CPU execution time by 20–50% [cite: 1].
*   **Empirical GPU Speedups (CoMERA):** End-to-end multi-objective rank-adaptive frameworks currently report a $2\times$ to $3\times$ absolute speedup per training epoch over standard uncompressed training, alongside a $9\times$ VRAM footprint reduction compared to alternative low-rank methods like GaLore [cite: 8, 9].

**Conditional Qualifiers:**
The performance of SVD-free frameworks is highly conditional on the sparsity and topological structure of the data. For extremely dense tensors with shape asymmetries, proxy-methods may underestimate the necessary rank, triggering irreversible loss of representational fidelity early in the training epochs. 

**Flagged Systemic Vulnerability: `PATTERN_RANK_PARITY_LEAK`**
When deploying adaptive rank heuristics without SVD (such as greedy layer-wise additions or gradient-sensitivity incremental updates), `PATTERN_RANK_PARITY_LEAK` frequently emerges. Because the ranks $r_{k-1}$ and $r_k$ are updated independently via localized proxy estimators, adjacent TT-cores can develop severe dimension disparities. This lack of parity forces subsequent contraction operations (TTCP) to process highly unbalanced intermediary slices, leaking the targeted computational efficiency and creating memory bandwidth bottlenecks that neutralize the theoretical benefits of the low-rank format.

## 5. Literature (Primary Sources)

The following strictly curated primary sources dictate the current state-of-the-art across mathematical tensor formalisms and deep learning applications:

*   **Luo, S., Liu, M., Yu, Y., Ren, S., Bai, Y. (August 2024 / Updated 2025).** *"An Adaptive Tensor-Train Decomposition Approach for Efficient Deep Neural Network Compression."* arXiv:2408.01534 [cite: 16]. 
    *   *Significance:* Establishes Layer-Wise Imprinting Quantitation (LWIQ), a proxy-classifier methodology that dynamically sets rank scaling factors for TT models, bypassing intensive optimization-based automatic methods and SVD tracking.
*   **Yang, Z., Liu, Z., Choudhary, S., Xie, X., Gao, C., Kunzmann, S., Zhang, Z. (May 2024 / Nov 2024).** *"CoMERA: Computing- and Memory-Efficient Training via Rank-Adaptive Tensor Optimization."* NeurIPS 2024 / arXiv:2405.14377 [cite: 9, 18]. 
    *   *Significance:* Directly addresses the GPU runtime paradox of TT-networks. Achieves 2-3x speedup via multi-objective optimization for rank-adaptive tensor-compressed pre-training, eliminating SVD execution ceilings on CUDA hardware.
*   **Chen, et al. / Lubich, C. (December 2025).** *"Dynamical Low-Rank method based on the projector-splitting integrator in tensor-train (TT) format."* arXiv:2512.14950 [cite: 19]. 
    *   *Significance:* Applies the Dirac-Frenkel Time-Dependent Variational Principle and Projector-Splitting Integrator to tensor trains. Replaces step-and-truncate (SVD) with sweeping core updates, allowing rank tracking directly on the tangent manifold. (Extends foundational work by Lubich 2015 [cite: 4, 20]).
*   **Huang, Z., Liu, Y. et al. (March 2021).** *"Adaptive Rank Selection for Tensor Ring Decomposition."* IEEE Journal of Selected Topics in Signal Processing, Vol. 15, Issue 3 [cite: 21, 22].
    *   *Significance:* Proposes a sensitivity-measurement framework where core tensors are ranked by approximation error sensitivity; ranks are gradually increased without relying on predetermined truncated SVD.
*   **Li, Y., et al. (January 2022).** *"Bayesian Tensor Learning."* Frontiers in Artificial Intelligence [cite: 6].
    *   *Significance:* Implements Hamiltonian Monte Carlo (SGHMC) and Stein Variational Gradient Descent (SVGD) to determine TT-rank automatically as a non-linear problem constraint, functioning as one-shot rank-adaptive training.
*   **Sedighin, F., et al. (December 2024).** *"Tensor singular value decomposition without SVD."* MDPI Applied Sciences [cite: 14]. 
    *   *Significance:* Replaces the global nuclear norm (requiring massive SVD execution) with an SVD-free approach that constrains the minimum Frobenius norm of unfolding matrices via alternating minimization.
*   **Hayashi, K., et al. (August 2017).** *"On Tensor Train Rank Minimization: Statistical Efficiency and Scalable Algorithm."* NeurIPS / arXiv:1708.00132 [cite: 12, 13].
    *   *Significance:* Introduced the foundational TT-ADMM algorithm leveraging "very sparse random projections" to sidestep exponentially large-scale SVDs during optimization.

## 6. Attack Vectors

### Live Techniques (Currently scaling in the literature)

**1. Dynamical Low-Rank Approximation (DLRA) via Projector-Splitting (KSL)**
Rather than simulating a full-rank target and then executing a retroactive TT-SVD truncation, DLRA tracks the evolution of the tensor analytically along its tangent space $\mathcal{T}_Y \mathcal{M}_r$ [cite: 4, 5]. The tensor differential equation $\dot{Y}(t) = P_{Y} M Y(t)$ is integrated utilizing a KSL (Kinetic-Structural-Local) splitting mechanism. The core tensors $K, S, L$ are updated successively without needing to rebuild and SVD-truncate the global matricized state [cite: 11]. Advanced implementations in TT-SOKSL allow for adaptive ranks where, if error thresholds are exceeded during the tangent space projection, local bond dimensions are augmented instantly without a global re-computation [cite: 11, 23]. 

**2. SVD-Free Bilinear Matrix Factorization (ADMM frameworks)**
To inherently avoid the nuclear norm calculations that mandate SVDs, recent literature reformulates the TT unfoldings $\mathcal{X}_{[k]}$ into bilinear factorizations $\mathcal{X}_{[k]} = U V$ [cite: 14, 15]. By penalizing the sum of squared Frobenius norms $\frac{1}{2}(||U||_F^2 + ||V||_F^2)$, the optimization problem mimics nuclear norm minimization but is strictly convex and solvable via the Alternating Direction Method of Multipliers (ADMM). $U$ and $V$ are updated in sequence, sidestepping the SVD entirely. Ranks can be adapted by expanding the columns of $U$ and rows of $V$ dynamically if the loss function gradient saturates [cite: 15, 24].

**3. Layer-Wise Imprinting Quantitation (LWIQ) & Proxy-Classifiers**
Applied explicitly to Deep Neural Networks, LWIQ attaches a "proxy classifier" to intermediate TT-layers to quantify each layer's direct significance to the loss function [cite: 16]. Instead of optimizing the global tensor structure algebraically, LWIQ derives a numerical budget-aware scaling factor. If a layer exhibits high sensitivity, its allocated TT-rank budget is scaled upwards programmatically before the forward pass. This heuristic dictates TT-rank without touching the internal algebraic structure of the core tensors, dramatically reducing search efficiency limits by 63% relative to continuous-relaxation proxies [cite: 16, 25].

**4. Rank-Adaptive Multi-Objective Optimization (CoMERA)**
The CoMERA framework fundamentally shifts TT deep learning by formulating rank-adaptation as a multi-objective resource constraint problem over training time and VRAM limitations [cite: 8, 9]. Instead of executing iterative SVD sweeps, CoMERA utilizes highly optimized tensor-vector and tensor-matrix contractions directly on the GPU, adjusting rank configurations stochastically and observing the multi-objective loss curve. The explicit bypassing of non-coalesced memory access associated with SVD enables a $2\times - 3\times$ speedup per epoch on standard Transformer models [cite: 8, 18].

**5. UTV Factorizations and Randomized Projections**
When pseudo-SVD logic is strictly required for error-bounding, researchers deploy UTV decompositions via toolsets like `randUTV`. The UTV decomposition ($X = U T V^T$) extracts orthogonal bases with a middle triangular matrix $T$, capturing the spectral behavior identically to SVD but via drastically faster parallelizable QR-like algorithms [cite: 1]. Truncation tolerances $\delta_k = \epsilon / \sqrt{d-1} / \|X\|_F$ dynamically slice the UTV cores, supporting adaptive accuracy selection while reducing compute time by up to 50% [cite: 1]. Very sparse random projections have also been proven to preserve singular values while exponentially lowering matrix dimensions prior to analysis [cite: 12, 13].

### Exhausted Approaches (Dead ends)

**1. Sequential TT-SVD Step-and-Truncate Sweeps for Real-Time Training**
Applying exact SVD dynamically during every backward pass in backpropagation is thoroughly exhausted. While TT-SVD remains the canonical initialization procedure [cite: 1], relying on `max_rank` or $\epsilon$-threshold truncation iteratively for network weights destroys training latency, forces CPU-to-GPU data transfers, and is entirely unscalable for 1B+ parameter models [cite: 8, 16]. 

**2. Global Tensor Nuclear Norm Penalization**
Adding a nuclear norm penalty to the global loss function as a continuous surrogate to induce low-rank TT states has been exhausted [cite: 7]. The evaluation of the nuclear norm unconditionally requires the exact tracking of the singular values of the unfolded tensor. This introduces unbearable computational penalties and prevents batch parallelization.

**3. Pure Manual Hyperparameter Rank Search**
Manually declaring TT ranks (e.g., setting a static $R=16$ for all hidden dimensions) causes extreme model under-fitting in highly non-linear data distributions or over-parameterization in redundant features. Manual grid-searches for optimal TT-ranks scale at $\mathcal{O}(R^d)$, cementing the practice as exhausted and obsolete [cite: 16, 25, 26].

## 7. Cross-References

**Related Open Problems:**
*   **The Optimal Embedding Bottleneck:** While TT networks reduce the parameter counts of massive embedding tables (DLRMs), maintaining lookup efficiency when the embedding table is implicitly defined by dynamic-rank TT cores remains highly challenging. Random row-access forces the contraction of the entire TT chain, shifting the bottleneck from SVD overhead to sequence-length contraction latency [cite: 8].
*   **DMRG Local Minima Escape:** The density matrix renormalization group (DMRG) algorithm from quantum physics (analogous to TT alternating optimization) struggles with getting stuck in local minima when bond dimensions (ranks) are too aggressively restricted. Finding momentum-based or triple-core updates to mitigate this remains an open objective [cite: 3, 19].

**Anti-Anchors (Concepts that look relevant but mislead):**
*   **Static CP Decomposition and Tucker Rank:** Do not confound TT-rank adaptation with CANDECOMP/PARAFAC (CP) decomposition or standard Tucker Decomposition. CP rank determination is rigorously NP-hard [cite: 14]. Tucker rank is fundamentally unbalanced (exponential core scaling), whereas TT matrices are heavily balanced [cite: 14, 27]. Attempts to port adaptive CP heuristics directly to TT-networks invariably fail due to topological mismatches.
*   **Low-Rank Adaptation (LoRA) Static Ranks:** While LoRA injects low-rank updates ($W = W_0 + \Delta W$), these rank updates are overwhelmingly static and matrices are 2-dimensional. GaLore and modern LoRA adaptations track subspace projections, but porting GaLore strictly to $\geq 3$-dimensional TT tensors loses efficiency. CoMERA has definitively proven superior VRAM execution ($9\times$ less) over GaLore for high-dimensional models [cite: 8, 9].

**Candidate Primitives for Future Research:**
*   **TT-Cross Interpolation (Max-Volume Approximation):** Leveraging max-volume submatrices allows for the approximation of tensors directly from functional or sampled access without needing the full tensor [cite: 3, 28]. Utilizing heuristic TT-Cross interpolation inside neural layer activations to dictate bond dimensions before backpropagation is highly promising [cite: 28].
*   **Interleaved Rank-Restoration (RankDyna logic):** Methods like RankDyna periodically suspend low-rank factorization, enforcing short bursts of full-rank epochs (tracked via fractional K-FAC or momentum), before reverting to dynamic low-rank states. This explicitly prevents the "effective rank collapse" seen in continuous low-rank training without constant SVD monitoring [cite: 29, 30]. Integrating periodic "sweeps" of full-rank gradient tracking into TT-networks could serve as a powerful alternative to step-and-truncate. 

***

*End of Brief. Compiled via advanced semantic consensus heuristics and multi-modal theoretical physics alignment parameters.*

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEy3TQrtbs6Od4pJ_rXzKRZp0ZE6PTrEpXGdEiAtIVf48p3Uzn6LlkqnQAe2ddk_O-2GLzGgySdIvqxKxaTDihFfNB0lXcGnpTlgDccCezbDA4t6rP2hEem0uwVde8D5ie-5YMamXoBSsRn1Yz5ztSfjUHe-hRzzD57l9Gp-J_xI6wGRm4EvpOtSA==)
2. [tensornetwork.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBzue9ZJBY7NjhrVio3nSs2BXuNKHpaF-X2LPy3TnVSG5yCJvxgzOHUpdw_BBaIoA4WEfgS6yFGgNkPGkqXlJPS289ART2VHrEg6xoHOw69BWPQezAsIw7Ku-MsWeL5YneGFM=)
3. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaGB0lwI7c3EXkYqTIyqYYJaJQwjB9iIezO6mKlWJJJd68k59tP0TIcEIazmxkuUqRq_xHinB3OqnvcLCx_RE01-QvZa1REpOm8yn5D3MTKnXKv2JII1V1Kqtq5l1yHZvAw7ajnzQYCaVSDf7bgnQ=)
4. [unige.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtvzRNMU37Y9CFHDaiafGkIAgPUMat8DYBcaz3gK0nWU-tPRai_iM-iywm-cdiEi3GPeSnclsuVRTZkBd1ByRukSK5lCnuTEedtkef95zBaFvWxqYopQS6sPiYAQqv58VIsxMXxdj7PP-DPdCbEA31WlkHf3mShw==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtD4aIUYRuVBOrqNxiHeDZeRygTdaTaPC1fO9ewgNCFfp-Mh9CMQuPg9QK5mY8rmuXZ-dWe9lNfERt60KIckDVYudzImIB_ZrEXhufrroIiuqmzKd4UrqLukNCCHcfyDbcqzmVVzmOi4wHiPgqeBp-AbMXnZcIWcgkkcD_p_zgmG1gzjSiaVYnUR-oO3fxjYH9TylVUmmetF-EVN3-tilz89OPnUwiUkW4F6BXsg==)
6. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE50tFLJM3voDgaQ_zzhSqYH58igNND69tE4fGZR3nMmR2kFwVJ96gjHGhSlR3xPyo8o2nSnP48eu3yVXDMaFXmZRW_9hKGePA2G7f8Bap5Wo3SkWb5PhgCtd3_jqa7iLvNv68HDFD3604P70i6VtzbAG8fST9soPoNQSIoH8a1ZoIZ6H6lzRo3Hgwl_PBvISp28Es5ojz9Ew==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyIRlCy6Rn-Jre68Qkv1J3iOJb1PVOWxit5EvuILCab_VakQK8xBLnYlONy65WBY9RFDgNhoZT9oFKb208mOaZvq5AGCEwGHwLXsSi4A7l4spqyfsfJ-oB)
8. [nips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaJZqqRG4By6GpJoZaAvLQ1UMph0pOnMPNw9EW3_cUEr3MN9VOxnpfKbP39il-gg4A5eFi5aPVbT0Ooz69E3IV6Dt62mtG7TeCFd4ffy1UnmUqpr-fE2bcmB8Q9wmch7N1M0Zw02r6kcdS_g6jiDcbr1OGUjmwRcXZubKMQV371NrGzDuOW5rGUOQIM2sz1sWeU_ew0UkG6WxVIWLT)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH02Vg72Cy4XajOQILmoBJ9HYTAavbvj1kyhySpKv-769Ss1nYoDTw-tLL9yrT38uvMe7U7rh7UALGHNB8_7Dq5gFKA6oaxsnyOsG9ejqRQLdXpGJ-Z3j-C)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDdmhhf47SOdpeCRq5nARumxLfIa8vKTVYbAbh7aO0uoKS891EbCfQ945rYG3MGRCHS8ulDISRkIQvZSJJQE4Bl5qrmMJL6YZHxmWO92KjvOzjN3L3)
11. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm7RptbpzcBYE9KrxqOWuM-wydgLZdhKmErDAaEU2xAj2GcGlU48WzIBXHXcjrIV4HHhDF2ptO9lovTVDmZRhajMN9a8frgMRAB0WLf269aI6rFOOv6FZ1iGOuJEW7FGbQDIcZjLk=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqoVcxpELfF44N4IQoKz4cgV4dPXJs7CeJwJUSlvYic-wfNGikKbnIxrSjddjczIYHMQK_KMH95VzVUx3x203WbrmoogPjpY1TkFm53RqqOEMN-DPD)
13. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFM0jYcpOONBnLV6S4NiatZqDgDQbxUSuwOTkNB_IBjvc6MhJuzSkX9ymDoH1-ut4hoXC4RSwLQB9LoTNEhcGl5p4Q9gOsec0HufdYK4fpVy4RKZIEGvULmI3r1ytLNf6buHmC9buVVSU56_k0gdUMhxRRgSUey4RtoV8Epx1sQe2i3Fj4exv2TknVnWWhRO9fmwAXEPtOcjvAnwRLp0URxstVjkvKoH9SW5Acx)
14. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQmEZVMfdHJD8n7NRJO1qDE8TLHaThM03OQ_ENO0ctoaWIjmo-yNxrnjO8TBklRUNnj5FIg-lnPfh1MS61-feGh4XtvuJHFxC9NkngGQEA_lj51zVkPk199ueN4A==)
15. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENG6lpTW2B5CP2Tslyg1YG-jW8O3n6DEJlR0JX5GUQ6M0ongT_0iNQYN1lJuq2F52bihxPgCriOMDRAeMA7grnVPCFK676xY792p_2oVFzDW8Xgq8UmW57rduCvzQ=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5RzR_8aLBhRWCs2GNidYKimGv18CJg4UQ49m4UpGKGR-QrcxEICgiKOXr80QnxuOYaWj0m9jsZ9LoLCcK_0OtOv5WTJXo9qPqxfyyJJ34Kt7lD9rF)
17. [epfl.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOvFzTnDoGtucfbB6IHAHTJpSiLTS_sKnt2J7XVzyd3GwoI8B5UIuY8pJx9aESS6mJRJ5EAanfwIP52ARnCmIxNEKZGMEHG00c379Kp-pmO03dSEdZY_yYtbpmRepsyR4ohXuW4j7x4D-B258zTit8g0aI)
18. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrPl-m6rlscBoM3KzgPeT1DWP511PxZGbHIwIexdnlyKqlOPge3NdjeHRxGw-HIyURlIT5TUdgN0FYaxOiCMzYVzWP1ENPuFwKJ-lyuvlpMPvHmMw98kMbmAmHIQPZ6cPsqx1_QEed1IoZl9SMd87OwA==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7pvRoCYS-4jrEaU1QipMVdC0wf5jF4OIIHuCfnvm_fYLdqxq675JJrTNNHNE-Ilpcmnp59qwCDWNQxf1Hje8q81I1TW78G1bzkUu7kim-g_zxvfiU6iYC)
20. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0VyHkPgotymtLywo_HCCkEEeJE3hPpKhlb_nsls14HqjVoT261MSSUvxVKpGjKOxIhWQunP_g4aI-BV-uy5DGBUZtLzzrKkGPCMwUAllyozSmKmJbwRNivbEf3Xns6X2ibg==)
21. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNY1AuSbCX6aQ_2cXZAvgqqV_psKq-mGTAuN1VnLzFTwMRDwywheivODALJGoXGQ6HAm80rE6H_PBrELZf5ABKTetFZsrozu-18dtNFJPEq2B51SZDOP2PhIyFhaMfKy2d0--igsHyRyNa3LglnCxyzyE=)
22. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGefisTmXYejx3QhzNmXcQPK7BUyrwyQKFuftILxoq4c6oGAoSQGlm9Fba5D4iNHKG000iGdx08xcvTx2LwwvfbQGno9mxEyBo46bn1aOJ0JyS9JceYbYmm2nMwiNn9bAHonQ==)
23. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWB6olJ__zx0zuiuzifcmJIjcdsbSwydjhiImcL58J1jlKwShGKhF_neu4q2jO8VNnzZP6WxKmrspLDOpZYsPRjW_dqQRoUJdBqJDOFShMbl8RFjAtmwTGgAZ9Lts8-gQtPYbPjNCzxfuZACWACRE-wr3poPGVHLQ7TZPRLHsPnBQyWyOhZmvL1QudBw==)
24. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNDmMh_99c2xfMMrH2U5AIWYCeXDaEpCQf0eUO3s0Y7L5PNQFkj_yk50EB3_7s82Xno_7czpNU17F82ID71EcwxdACS0SFvwx2d1saveErgGKAp6tjhlNQbzQDvgHE_wrIaDUyrr9OtZh9wV8p0YvlekjzhFFmU4Gg0htycpLJS5lzgLEYmmRpJMHfYBgCNsfIjmmqj9eRWYlyD4IZ6-3N3rWGSQ==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETWsLsuOMKxNd46yFToc2Fnil5j93q8wudfs4UQxZ4Syey12T6yUxqZ4lDWBNxW4tJFpTa2KuxTeiYlxohT35LMEvSCge-I_UUIgw5uyf1lGsWLkVU4V-p)
26. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMUrSDghxjYn30-ZQlYe12nWAx6Al5gIGjw_e3fRWLHmzQ551quchXY3wihu-Aznt4K-VacWucJkDzvLkr6RWfSPObQ0_Odmu2kR0JAksUZdfqOv75W2UHW4v7IhiHFCEC7-yMrZBo0HY_GhBlJTYqMYPk0gJQfgQ_SfNiOZ2cA_jN5GNEpeif98uSOHOy0orofU34mTRh2VE-eTkx0BX4YVLiwQ6pjXo=)
27. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmxrCIFHMjtzFX_5jHM3frF7G45OGNSFPSPGDHQPUcqnQw6d6udED4VnPPtyPMWP1iv8P5P-wDtKaVRUJ4-K66xksC8l4eRAmMsRh66d7l4-XpAqLPCsKs41C3UKxpt4wZ32mG9A5BwfUdQosSFslGAzo=)
28. [lanl.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFr1v6iK7fGseE2T16FJ0jqlvSk6pch83jmv0zTFYqvAh0yaFmG4cXWLio1XIPk46IbfV6hvYgZblcmlmiCQJaxttEssP0ZyDAROGa6N4w0Ev5-jFSSiJHpVdJkR-z_42ptUFQ69SKrwNvFd-holfkPwT4wXQcRCGfZfDQ-ia7LsIg3hWtCaL8MpeuXUeJWVth3UTC2f0FYCss=)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbTG4jYOu30r3IGUw9fkdIVwKE_7M0PDUlUPpO0Odql57HwuZBOU1zy-6Tw9l9wz7LY7AIOYwxatJ7P_VGKzCfkfg2Lm7_3-F4sC7tbyJehJ1Xie6W1kXG)
30. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAA8o_VEDW06EpvT67LCHtrHqmAKaOhnchp1QKHQSpMDQIjybjKnvBflFCLX3H5P8qCObCDd41Mznr1U70cM0BC3VvFsYRL7qlnNNMxRzhKWObUcBiCXEqUQ-LIvhz7A==)


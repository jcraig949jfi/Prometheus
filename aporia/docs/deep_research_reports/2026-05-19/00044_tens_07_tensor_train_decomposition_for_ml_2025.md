# TENS-07: Tensor-train decomposition for ML 2025

**Pythia queue id:** 44
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcxeTRNYXR6Y0xwLXkxTWtQOU9xdm1BdxIXMXk0TWF0emNMcC15MU1rUDlPcXZtQXc
**Elapsed:** 249s
**Completed at:** 2026-05-19T09:39:29.507965+00:00

---

# Tensor-Train Decomposition Advances in Machine Learning (2024-2026): A Comprehensive Analysis

### Key Points
*   **TT-LoRA and Parameter Efficiency**: Tensor-Train Low-Rank Approximation (TT-LoRA) has emerged as a disruptive alternative to standard LoRA, demonstrating up to 80$\times$ greater compression and resolving scalability bottlenecks in fine-tuning Massive Large Language Models (LLMs).
*   **MERA-Style Attention Mechanics**: Quantum-inspired Multi-scale Entanglement Renormalization Ansatz (MERA) architectures are being integrated into Transformers, theoretically reducing attention complexity from quadratic $\mathcal{O}(N^2)$ to nearly $\mathcal{O}(N \log N)$ while capturing hierarchical semantic entanglements.
*   **Theoretical Strides**: Recent proofs guarantee local linear convergence for Tensor-Train optimizations on Riemannian manifolds, proving that the computational penalty for increasing tensor order scales polynomially rather than exponentially.
*   **Rank-Adaptive Optimization**: Density-Matrix Renormalization Group (DMRG) algorithms and Bayesian frameworks (like Stein Variational Gradient Descent) enable dynamic, on-the-fly rank adjustment during training, though optimal initialization and computational overhead remain heavily debated.

### Overview of Findings
The landscape of machine learning has been deeply transformed by the integration of higher-order multilinear algebra, specifically through tensor networks. Evidence suggests that Tensor-Train (TT) decomposition effectively circumvents the "curse of dimensionality" that plagues scaling efforts in modern deep learning. Recent research establishes that TT decomposition is no longer relegated to post-training compression; it is now actively used in end-to-end training and parameter-efficient fine-tuning (PEFT).

### Complexities and Uncertainties
While the theoretical guarantees of Tensor-Train decomposition are mathematically sound under strict constraints (such as the restricted isometry property), real-world empirical training remains fraught with challenges. It seems likely that issues such as exploding or vanishing gradients during tensorized stochastic gradient descent will require further refinement of optimizers. Furthermore, the selection of the optimal initial tensor rank and the precise mechanisms to adapt it dynamically (e.g., without incurring prohibitive Singular Value Decomposition overheads) remain open questions in the current literature.

***

## Introduction to Tensor-Train Networks in Machine Learning

The rapid evolution of deep learning algorithms—spearheaded by Large Language Models (LLMs) and Vision Transformers (ViTs)—has introduced unprecedented computational, memory, and energy demands. Machine learning architectures now frequently exceed billions, and occasionally trillions, of parameters, creating steep barriers for deployment on resource-constrained edge devices and complicating fine-tuning processes. To address the "curse of dimensionality," multilinear algebraic techniques, specifically **Tensor-Train (TT) decomposition**, have transitioned from theoretical physics to mainstream artificial intelligence between 2024 and 2026 [cite: 1].

A Tensor-Train expresses a high-dimensional tensor $\mathcal{X} \in \mathbb{R}^{d_1 \times d_2 \times \dots \times d_N}$ as a sequence (or "train") of sparsely connected, low-order core tensors [cite: 1]. The decomposition is mathematically defined as:
\[ \mathcal{X}(i_1, i_2, \dots, i_N) = G_1(i_1) G_2(i_2) \dots G_N(i_N) \]
where each $G_k(i_k) \in \mathbb{R}^{R_{k-1} \times d_k \times R_k}$ is a 3D core tensor, and the sequence of bounding integers $\{R_k\}_{k=0}^N$ (with $R_0 = R_N = 1$) represents the TT-ranks [cite: 2]. This framework reduces the parameter count from $\mathcal{O}(d^N)$ to $\mathcal{O}(N d r^2)$, converting exponential complexity into a polynomial scale [cite: 1, 3].

Historically, TT decomposition in neural networks was primarily employed for post-training compression [cite: 2, 4]. However, developments up to 2026 have shifted the paradigm toward **end-to-end tensorized training**, global meta-adapters, and dynamic rank adaptation [cite: 5, 6]. This report exhaustively details the integration of TT frameworks into Transformers, the rise of TT-LoRA, quantum-inspired MERA attention mechanisms, rigorous theoretical convergence bounds, and the persistent open questions regarding rank-adaptive training.

## Compressed Transformers: PTNN, MetaTT, and Edge Deployment

### Partial Tensorized Transformers (PTNN)

The Transformer architecture, while highly accurate, incurs an immense memory footprint due to its multi-head self-attention mechanisms and densely connected feed-forward networks (FFNs). Recent interventions seek to compress these models algorithmically. One significant development is the **Partial Tensorization of Neural Networks (PTNN)**, targeted specifically at vision-language models like BERT and ViT [cite: 7, 8]. 

Unlike approaches that forcefully decompose the entire model and suffer resulting accuracy degradation, the PTNN framework targets specific, highly parameterized sub-modules, such as the embedding layers, which in BERT can comprise approximately 28% of the total parameters, and in ViT up to 40% [cite: 9]. By employing iterative TT-Singular Value Decomposition (TT-SVD) under predefined error bounds ($\varepsilon$), PTNN compresses target weight matrices without requiring extensive post-training adjustments [cite: 8, 10]. 
Empirical results from 2024 demonstrate that PTNN approaches not only compress the model but can paradoxically *improve* the accuracy of existing models by up to 5% [cite: 7, 10]. This regularization effect is attributed to the low-rank prior smoothing the loss landscape and discarding overfitted, high-frequency noise inherent in heavily parameterized embeddings.

### MetaTT: Global Tensor-Train Adapters

While standard tensorization targets individual weight matrices, the **MetaTT** framework (introduced in mid-2025) shifts the focus to global structural sharing across the entire Transformer [cite: 6, 11]. Traditional Low-Rank Adaptation (LoRA) fine-tunes each weight matrix independently, injecting separate low-rank matrices for the query, key, value, and projection layers. For a given rank, LoRA adds parameters proportional to the *product* across these modes [cite: 6]. 

MetaTT unifies these sub-modules by utilizing a single, shared Tensor Train to factorize the query, key, value, projection, and FFN layers across *all* transformer layers simultaneously. By indexing structural axes—such as layer depth, matrix type, attention heads, and even multi-task identifiers—MetaTT forms 4D and 5D tensor networks [cite: 11, 12]. 

| Architecture Feature | Standard LoRA | LoRETTA (3D TT) | MetaTT (4D/5D TT) |
| :--- | :--- | :--- | :--- |
| **Parameter Scaling** | $\mathcal{O}(L \cdot M \cdot d \cdot r)$ | $\mathcal{O}(L \cdot M \cdot r^2)$ | Proportional to the *sum* of modes |
| **Cross-Layer Sharing** | None | Yes (via Tucker/3D TT) | Yes (Global Indexing) |
| **Multi-Task Extensibility**| Requires new adapters | Sub-optimal scaling | Highly scalable (Task Core) |
| **Compression Ratio** | Baseline | High | Extremely High (up to 2000$\times$) |

*Table 1: Comparison of LoRA and Tensor-Train PEFT frameworks [cite: 6, 11].*

Because MetaTT's parameter count scales with the *sum* of the modes rather than the product, it maintains competitive accuracy on benchmarks like GLUE while dramatically shrinking the adapter footprint. Furthermore, MetaTT facilitates multi-task learning by merely adding an isolated tensor core to represent specific tasks, rather than duplicating the entire adapter setup [cite: 12].

### Hardware Acceleration and Edge Decoding

Deploying TT-compressed Transformers to edge devices presents a specific hardware bottleneck: the computational overhead of decoding compressed parameters during inference. Recent mathematical formulations have mapped TTD decoding operations directly to standard Generalized Matrix Multiplication (GEMM) engines [cite: 13]. Since parameter decoding and inference do not occur simultaneously, FPGA-based edge devices can reuse the GEMM engine for both processes via optimized Einstein summation (Einsum) operations [cite: 13]. Hardware-aware optimizations—such as merging redundant reshape operations between decoding and inference—have yielded up to a $69.3\%$ decrease in decoding time on FPGA accelerators [cite: 13]. Furthermore, full quantization strategies combined with TT formats (e.g., Square-block MX-INT formats) have shown $2324\times$ energy reduction in Neural PDE solvers [cite: 14].

## TT-LoRA: Democratizing Large Language Models

As LLMs evolved toward models exceeding 70 billion parameters (e.g., LLaMA-2, LLaMA-3, and sparse Mixture-of-Experts), traditional PEFT strategies like LoRA encountered scaling limits [cite: 15, 16]. Standard LoRA injects a trainable low-rank update $\Delta W = BA$, which relies on an explicit two-matrix structure. **Tensor-Train Low-Rank Approximation (TT-LoRA)** directly addresses this by supplanting the $BA$ matrix structure and eliminating adapter modules entirely [cite: 15, 17].

### Core Mechanics of TT-LoRA

TT-LoRA reshapes the weight updates $\Delta W$ into higher-dimensional tensors and factorizes them sequentially into TT cores. This approach avoids the redundant parameterization found in intermediate models like LoRETTA, which wrapped TT structures around standard adapter schemes [cite: 17]. By strictly parameterizing the update as a tensor chain, TT-LoRA achieves model compression ratios exceeding $1500\times$ compared to standard fine-tuning for BERT architectures, and up to $80\times$ compression compared to standard LoRA [cite: 17, 18]. 

In performance benchmarks, TT-LoRA maintains accuracy parity with full fine-tuning. This is partly driven by the mathematically richer structure of the TT decomposition; the correlated, TT-guided update yields larger neural tangent kernel eigenvalues, which in turn provide provably faster convergence and tighter generalization bounds [cite: 17].

### TT-LoRA MoE (Mixture of Experts)

A significant leap in 2025 was the unification of PEFT with dynamic routing via **TT-LoRA MoE** [cite: 17, 19]. In this architecture, TT-adapted LoRA experts operate within a sparse Mixture-of-Experts paradigm. Traditional MoE networks suffer from task interference and catastrophic forgetting during continual learning. TT-LoRA MoE decouples expert training from router-driven task selection. Each task or domain is mapped to an independent, highly compressed TT expert [cite: 19]. Because the parameter cost of each TT-expert is negligible relative to the base LLM, a system can store hundreds of specialized experts locally on an edge device, with the router actively selecting the optimal TT-cores at inference time [cite: 19].

## MERA-Style Attention: Quantum-Inspired Transformer Architectures

Perhaps the most philosophically and mathematically profound shift in 2025-2026 machine learning is the mapping of Quantum Tensor Networks onto Transformer attention mechanisms. Standard Self-Attention computes pairwise relations between all tokens via $Q K^\top$, resulting in an $\mathcal{O}(N^2)$ computational and memory complexity that chokes context window expansion [cite: 20].

### The MERA Architecture

To circumvent this, researchers have turned to the **Multi-scale Entanglement Renormalization Ansatz (MERA)**. Originally formulated to efficiently represent scale-invariant quantum states and capture long-distance entanglement in many-body physics, MERA utilizes a hierarchical, tree-like tensor structure [cite: 20, 21]. 

In a linguistic context, words are not merely isolated vectors but are deeply "entangled" in a latent semantic manifold. Standard attention treats all interactions equally. A MERA-style attention mechanism allocates representation power proportionally to semantic entanglement [cite: 20]. It factorizes attention into a tensor network contraction sequence:
1.  **Boundary Layer (Local)**: Tokens are grouped into small local patches (e.g., adjacent words in a sentence) where localized attention is computed.
2.  **Bulk Layer (Hierarchical Compression)**: Higher-level tensors compress group-wise attention, stripping away redundancy while preserving complex global correlations.
3.  **Global Paths**: A sparse set of global paths encode long-range interactions (e.g., linking a character introduced in chapter 1 to an event in chapter 50) [cite: 20, 22].

### Theoretical and Philosophical Implications

By mimicking the MERA structure, Quantum Vision Transformers (QViT) and MERA-attention LLMs reduce attention costs from $\mathcal{O}(N^2)$ to nearly $\mathcal{O}(N \log N)$ [cite: 20, 23]. The network naturally supports multi-scale feature extraction: resolving local wordplay at the boundary while maintaining the global narrative arc deep in the bulk [cite: 3, 20]. 

Philosophically, physicists note striking parallels between this architecture and the holographic principle (AdS/CFT correspondence). In quantum gravity models, the MERA network discretizes the emergence of smooth 3D spacetime (the bulk) from 2D boundary quantum data [cite: 22, 24]. When applied to Transformers, the exact same mathematical contraction schema allows high-level "meaning" to emerge from sequence data, suggesting profound links between fundamental computation, quantum entanglement, and artificial intelligence [cite: 24].

Furthermore, algorithms utilizing **Tensor Network Operators (TNOs)** have advanced multi-operator structure search, establishing frameworks for discovering optimal, shared tensor topologies across coupled attention layers, moving beyond single-operator compression [cite: 25].

## Theoretical Guarantees: Expressivity, Rank, and Optimization

While empirical success is abundant, the robust application of TT decompositions in ML hinges on rigorous theoretical proofs regarding expressivity and convergence, many of which matured significantly by 2026. 

### The Semantics of TT-Rank vs Matrix Rank

In matrix algebra, rank corresponds linearly to the dimension of row/column spaces. In tensor networks, however, TN ranks dictate the expressivity and efficiency of the decomposition but lack a universal geometric interpretation across different topologies (e.g., CP vs. Tucker vs. TT) [cite: 26]. The TT-rank $\{R_k\}$ specifically controls the entanglement between partitioned modes of the tensor [cite: 1]. It has been theoretically proven that a TT decomposition constructed via TT-SVD is quasi-optimal up to a factor of $\sqrt{d-1}$, uniquely linking the minimal TT-rank to the intrinsic correlation structure of the data [cite: 1]. 

### Riemannian Gradient Descent and the Stiefel Manifold

Optimization of tensor factors directly involves non-convex geometry. Traditional Iterative Hard Thresholding (IHT) methods maintain TT structure via repeated TT-SVDs on the full tensor space, demanding exponential intermediate storage. Recent works (e.g., Qin et al.) provided the first convergence guarantees for factor-direct optimization using **Riemannian Gradient Descent (RGD)** [cite: 27, 28].

To prevent scaling ambiguities among the factors, theorists enforce a **left-orthogonal TT format**, defined as $\mathcal{X}_{\le k}^\top \mathcal{X}_{\le k} = I_{R_k}$ [cite: 27, 29]. This constraint forces the tensor cores onto the Stiefel manifold [cite: 27]. Under Restricted Isometry Properties (RIP) and Restricted Correlated Gradient (RCG) conditions, and paired with spectral initialization, RGD converges locally to the ground-truth tensor at a linear rate [cite: 27, 30]. Crucially, mathematical bounds demonstrate that the required accuracy for initialization, and the rate of convergence, experience only a *linear* decline as the tensor order $N$ increases, dismantling the assumption that higher-order tensors strictly invite exponential optimization penalties [cite: 27].

### Pre-TT-Encoder in Quantum Machine Learning

Theoretical advances also extend to Quantum Machine Learning (QML). A fundamental bottleneck in QML is the exponential cost of encoding classical high-dimensional data into quantum amplitudes. The **Pre-TT-Encoder** leverages pre-trained TT decompositions to map data structures to quantum states [cite: 31]. Theoretical analysis in 2026 established that this reduces the computational complexity of state preparation from $\mathcal{O}(2^U)$ to $\mathcal{O}(U r^2)$, providing strict fidelity guarantees that mathematically quantify the trade-off between TT-rank truncation and approximation error [cite: 31].

## Rank-Adaptive Training: Mechanisms, DMRG, and Bayesian Approaches

Determining the optimal tensor rank a priori is notoriously difficult; an underestimated rank severely truncates model expressivity, while an overestimated rank invites overfitting and wastes computational resources. As determining the exact tensor rank is NP-Hard, 2024–2026 saw massive investments in **rank-adaptive training** [cite: 2].

### Density-Matrix Renormalization Group (DMRG) Sweeps

Adapted from quantum many-body physics, the DMRG algorithm has become the gold standard for rank-adaptive optimization in TT-based PEFT methods, including MetaTT [cite: 11, 32]. 
A standard DMRG sweep operates by optimizing two neighboring TT cores simultaneously. The procedure is as follows:
1.  **Merge**: Two adjacent cores, $G_k$ and $G_{k+1}$, are contracted into a single tensor block [cite: 32].
2.  **Optimize**: This merged block is optimized regarding the target loss (e.g., using AdamW, or Lanczos/Davidson iterative solvers) [cite: 6, 32].
3.  **Adapt and Split**: The optimized block is factored back into two cores using a truncated SVD [cite: 11, 32]. 

During this splitting phase, the singular values dictate the new bond dimension. By dynamically retaining only the singular values above a specified threshold, the algorithm **adaptively prunes or expands the TT-rank** on the fly [cite: 11, 32]. Experimental evidence highlights that starting with a high initial rank (e.g., $r=10$) and allowing DMRG sweeps to progressively compress the rank to $r=4$ yields significantly better generalization and accuracy than simply training a static $r=4$ TT model from scratch [cite: 11]. Furthermore, because the SVDs occur strictly on the low-dimensional TT bonds rather than the full weight matrices, the cubic complexity bottleneck is circumvented, allowing up to $2000\times$ faster parameter adaptation [cite: 11].

### Bayesian Tensor Learning and SVGD

Parallel to DMRG, probabilistic Bayesian frameworks provide a non-parametric method for rank determination. Under this paradigm, tensor factors are modeled as hidden statistical variables governed by a rank-shrinking prior density (e.g., Gaussian-Gamma priors) [cite: 2, 33]. 

To bypass the complexities of exact posterior inference, frameworks rely on advanced samplers like **Stein Variational Gradient Descent (SVGD)** and stochastic gradient Hamiltonian Monte Carlo (SGHMC) [cite: 2]. By pushing a set of particles (tensor configurations) to approximate the target posterior distribution, SVGD dynamically shrinks unneeded ranks toward zero. This constitutes the first end-to-end, one-shot rank-adaptive training schema for billion-parameter neural networks, providing the auxiliary benefit of robust uncertainty quantification [cite: 2, 5]. 

### CoMERA Optimization

Another notable rank-adaptive schema is **CoMERA** (Compression in Training). Moving away from single-path forward propagation, CoMERA optimizes $d+2$ coupled contraction paths jointly across forward and backward propagation [cite: 4]. Utilizing a multi-objective optimization formulation, it achieves true end-to-end rank-adaptive tensor-compressed training. With heavy GPU numerical optimizations, CoMERA uniquely realized a $2\times$ to $3\times$ speedup per training epoch compared to standard uncompressed training, even matching the training loss convergence curves on models like CodeBERT-Large [cite: 4].

## Open Questions and Future Directions in Rank-Adaptive Training

Despite exceptional algorithmic and theoretical breakthroughs, rank-adaptive TT training in machine learning is not fully solved. The literature highlights several critical open questions and hardware challenges.

### 1. Optimal Initialization of Tensor Networks
A persistent open question is how to optimally map pre-trained standard neural network weights into the initialized tensor network. The problem is mathematically ill-posed because there is no single "best" decomposition of an arbitrary matrix into a tensor network without extensive combinatorial search [cite: 5, 12]. While Spectral Initialization helps under Strict RIP conditions, empirical LLM weight distributions rarely adhere to such ideal metrics. Improper initialization disrupts the early learning phase and can severely limit the capacity of rank-adaptive algorithms like DMRG to find global minima [cite: 12].

### 2. Gradient Instability in Tensorized SGD
While DMRG is highly effective, scaling it to models with billions of parameters alongside standard optimizers introduces friction. Utilizing standard Stochastic Gradient Descent (SGD) or Adam directly on multi-core tensor networks frequently triggers exploding or vanishing gradients [cite: 6]. Because the forward pass consists of deep chains of multiplicative tensor contractions, gradients backpropagating through the TT cores destabilize easily. How to systematically precondition tensorized gradients or construct bespoke tensor-aware optimization algorithms remains a highly active research area [cite: 6].

### 3. Computational Overhead of Adaptive Rank Sweeps
Algorithms that rely on SVD to dynamically prune ranks—even when isolated to the TT bonds—still inject notable computational overhead [cite: 11]. Specifically, performing SVDs sequentially through a forward and reverse sweep acts as a massive bottleneck on modern parallelized GPUs. Developing highly parallelizable, SVD-free rank-adaptive algorithms (perhaps leveraging iterative randomized subspace methods or Bayesian drop-outs) is critical to realizing the full acceleration potential of tensorized training [cite: 12].

### 4. Interactions with Mixed Precision and Quantization
Recent systems have demonstrated the feasibility of pairing TT-decomposition with ultra-low precision (e.g., 4-bit) and fully-quantized training [cite: 5, 14]. However, an unexplored open question lies in the interplay between rank adaptation and quantization. Does a lower bit-width artificially inflate the minimal required TT-rank to preserve expressivity? Alternatively, can Stein's Estimator (SE) and dynamic precision scaling be unified with DMRG, adjusting both the bit-width and the tensor rank simultaneously based on localized layer sensitivity? [cite: 14]. 

## Conclusion

Between 2024 and 2026, Tensor-Train decomposition transitioned from a niche mathematical curiosity to a fundamental pillar of modern machine learning architecture. Through frameworks like Partial Tensorized Transformers (PTNN) and MetaTT, the massive memory barriers of Attention-based networks are being systematically dismantled. The advent of TT-LoRA has drastically reshaped the Parameter-Efficient Fine-Tuning landscape, permitting the deployment of complex, domain-specific Mixture-of-Experts systems directly onto edge devices.

Simultaneously, the cross-pollination of quantum many-body physics into AI has birthed MERA-style attention mechanisms, radically altering how contextual semantics are processed and compressed. Bolstered by rigorous Riemannian convergence proofs for left-orthogonal TT formats, and driven by state-of-the-art rank-adaptive algorithms like DMRG and Bayesian SVGD, tensor networks represent arguably the most promising trajectory for overcoming the scaling laws that dictate the current limits of Artificial Intelligence. As research untangles the remaining open questions surrounding gradient stability and optimal initialization, the paradigm of tensorized, rank-adaptive machine learning will likely redefine the standard for efficiency and expressivity in the next generation of foundational models.

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlCEkh-XfAbfAVBwakNrMVZRSk0nMnfibeJvWhu8VxODpy15UQQxjE-ILS10eiOUkfLxAp-lIZMwla90DYTC3qq7_fKc8-OXM4Diwr65_FbfFr5IluA-JHT96mRiUQwuRiaucFq6ympEaPRgSwYJdj)
2. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHFJGUkUKWF9wIAyz0kPHYkjG9E4MRrkBjElfdf14P_1ytxDhBWztTa5PHR-BZGLZhYooNV8sQK6gUcqMPTWNdFqopzDayzrA1hvk8ooZ7vln7-CijpybqPGIl_hGxkWScSrXL6_Eg9Afm3Zg6H0CLwMa_xgUEZY2rj8EHoXL_5gs9PUjTzZcjumz4N9_Dh-jX5g4lSPK1sD0=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEguZsSeeZiFgow0zcTcfgwGOR-7Ri1oPfa9rfKBdt1EXR04osqzUi928u0hXZzHLUvIT4sspZ4Tx-Jz-AbaQ0-LBFp5cbvtN7Ok8ZVByxIHhWgpt0Q1x1NQ==)
4. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFA8DCtVDX3l1wvfWSBpS4ax1BEaBM9EXxnd-nM16b23wm4xB0D4_c21qF5s0huPsl0Rr_NW_VnnwaSqUA3BlgVSejK6Up8YQIrxhT4A-arcy8moNJ__KDlvAzld45cfpaBjnfK0ycTZkhSP3jSnILBfZk=)
5. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXJ_F6Me-zsXypDehygJYPisxZV9NhXd-02baqcmeeIUEY3oyUgd-_lIpQud14V3fADgJZk-TaWjmvoNVB9bioPrPDglw98rcMzG1h2b6IgLmTeuhguu11_UzIfrzwWuZCPT7GveMETS9VVlI1V5kzbOoC8dvrxux7BRWydCfL1g==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZCUNGgOxVb_opMWplZoRltiKzvRCHxNfSNWiFvkeSeoow2G205yCxNmZ5JRICHqxt5j0vP2TmtWtciLJpubKcTyx1cpfKwLq2CM9luMfs-4pqqOr8__KZzQ==)
7. [scitepress.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHumi7dU4ZrNqWStjdJn5BIPs26uffu2_69cntpc3mHsjldBvKKRxxWfH1xQwVjiqUpqh8LusjlB8knVTS3sI0sKivkamF9O0vLm6hqFgUHI5GVUJuyarzahMpDJE1qDYV7_3Vn6chEks-YEy78)
8. [scitepress.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdcOnl5c4itruMCbJtv33H14I7rZhmafKUoOh0myN-djV8QjL-N2NueT5Jx3yPcL14k6JSLpXEWIoVePWf_LzPw2tLOgwlmTeaJXwNXt7G15aKusL4ydfubm5wZ-Sv5BgPOXnQPQrVTaKSzmiRxw==)
9. [scitepress.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrlxVDeAqyefMidi2z8yxoGQjGJUW0IhAOfbeztWZMq-vmAsbUJ8aoKt6tIItFZOzYbRfOC7wu3PHOaGSDQNbT9WGWK2cYAaLMIlwWJwgfY_nEY3QiSpD_-ELpCsCt89ZmqywHxuwSusGBTLe1lt0HA3heepWyB_OcDDI=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqEhghjsa3a1VSbhbXL1yJoSyHxHJ-d-xbSwEIz96DwPhP3yv1RiwIcDjVMzZlD5OnufHf6HaZl1n2ROTh8TM-sVd5flJ7JBRLaFVUhZvd3rTg2WnCvw==)
11. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLDNxqVi0SfYPzl8RFZvaEFPe1AiWBNkPIoxH0H8vq2bY9C02am6JZqloEPHT5-aBJqSdNiirOGJSHyg2DahtDHRa6rzKKcMly7Cxys5IFE6LMIJwTxB9Sno76fY2wbEg=)
12. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeDXcJBsxYKa6XmhIrg7xFq58xkvNkiYVkr8n9KP8a1_4siwljogxfOJoWiVN4J6FHLGi7_mC4Z0O9AZHMw3Ng7XYpsRo07uLQEQVj3Dk2s52qOsR96BHit5R3yh2X4v0=)
13. [aimspress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELcDIDaHH_zCk0NZdbNymD57dDeMCgj_T0zy8ZErJqt_HLrPX_t9XyS-6rXm18Lxs28IoUd2MVtixfjUae6TBNXP9EwjRTTMKhm60EftomogKWfeUBALKLOc8PFbgYUsxbXy5uFx3L2FPws29qpQih)
14. [date-conference.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPvA5UehaCG5Yej4WbO0_LH20CUnZH1D8nwnHJOokUtvp5Qq8doj6oHzNtMjT6eQYH2kIyYMs2xLepunUcyhh2awFMtf0Iy8QsHNROOR5X7kBTytcVvcl3_Mml7TN2gPlzR8IvdtiMaghk8pDPm5NUoqIkdoykngV49mEOYiaZ)
15. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF_NcBFcmlBuTOXI2qQVKgSWqk5vm3HCLg6mtraXAhW5jaBjzP9RaNdLTPE2wFlRyy9YOlH0FLT2ERyyInXTgykHC9lllo0anfHDLm_av4JnnVa9HrGmxpS89nu7UOlLEnxyoR_aDNoJHUsYaF-IKtwl5xguA=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGU24J2n3a9gmHdY37SCmPqa3bGVDoUNZYbyzUpuHsYafHc9_FdAnLZasN5k4oXXRWvEul9E8DHtqMAOD0SzLFADOBiFx4zEJMwaakgEkepd5Bg8EoRUrQ8OA==)
17. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7KPtHl-aqoJfXhJ6-mKHzg7DjCp6Q_LDHpah2_XLokXfo5d0bLSfeq9U9TjgPUTIsZ_03cdshGCvm36q_x6oZbw81eTdlEiHF33-l29LUXZ1F9vvd49-3BHcKQurM272FKNP3CROrTdMnerq3px_bBtR-dg==)
18. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT0s-i0zpNQ_o5rfvR9Azkjn9-1ZEuFiN2Gq0md4XO29j7eGXvFNgx7IfLsNaFN7ZiOWWoSkF9-QdfbdfMur_9tTaRi3Jv7prKdlBk0WDlvUu4r88JHPoAebDxq5RHKP1R_M10UPrl0YvFAA3CiuAVFD4iGaI9zUHVgj8IX4bMFf9mC4C4ccUf8wgLeXbN4iJyL0DjPjzLjDV2l-PymjbxeojLtI31XaOQbFmXzpA=)
19. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsJ0UcABKLvhjlZB775PqAFReL6qlPCAJPgOfmRmtep54io7T8tYp5RJxC11p0vpFplPB9oKwiK3voBB1XO1r1YvcHSUX_ziXP3SCUfeKSeG4g5qaugjEEYW2u7aIIY0EXJhPSmA==)
20. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZC63yRLqj7hXpLXatS8HdRU_Kj6n_optmrJvxt0TcidgHore4cmAslpUSR-Mo23rVgljbDvMYzin7W9SP7IeJqA51WqQnIbhno3mMD_pIvSt7mxZ4D8j7hVK7xKzFYPasnN5c2R-1B7mA9f8bbCxMU8e8JDi-_0wsNLflXAZ_XmpRBm1v6E-sN5piomcpIDpSMSK3eB4khzD5IKg8OiQFENnry6OcX8Vfq3iS)
21. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCbtuP2xKd6ifhaH7OIQhcHq0NH4QTNk-WSNF0wSJ2IZ4wqNtRG2wTJ8J8VaKXgzNwXMBnEUHh3gHuqr41pQy3vf2x601LCoQPERya60MS0MLI4cIamqchMI2aGBqqzahSJQh51sH5ahF-cQDVZwmVpu5EgA==)
22. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNVvWQIZ6bKE5Xj6t-NZfW7rmGcv1Xv0BEsK4FEnNi28VmOjYTSSOYd2g6OWUq-kDZXi5P05_dcUiZh72hwkMIdmP50PeAYpYB_PCPnvZdKZvkLRFmy9twe_ECgN8BQ0cpt1ui0ijF-NPnumFV-3gnAb1dCGph868QQg==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERAZhvXHBn-l-UanC2T074BiFx9l3gSr-uQm0IFXjFjE7dg23pveZNpduHbMW3qLIuh64R2SNixFocRdrycjs50r66aDpQt-uoooeXZKYLdJifgUzm0c2Eiw==)
24. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOY7JtMQIuwUo9oXBP9EU1dUB63LI-3zmz1v34Xz203DwaYV7aglaycXi3ncaAo1Jk6hJWA7V5B2hwRhaAFkJAfcrocCeAdPyrknduMOilLXaRo57Hr9ph7OSMlDd2XCgvo6lVTBLTGfKrhqfjMkS3qqybCTFguihMY5Txn6xLKZzahj3jm0Ub_fpZG9faufP33L8AmiQmFHo=)
25. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsixU_Zqnh5wzVw22lJ2Pakm5yeudOJXoaO0dqN5t0-uJHmx72bYEAjJjkkfFVLKBSbOcuWVRzhnCJGMImArHkObvQeWV8fs_MkUcaBhHoIGyW4kHA0eBn3CSIgNME52OXgn5CnbsoaIGNfSVO4kCUTE4=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeasXHJzjUjKq5HS9nteCljOcxmp9U-mj1tdYfNWMdAYU1KSFdUPR2gO4VRHNjA_GfPDF_9TN8M_nngu4nsjS9gSSf_QviSLcPZ6MjfpwXMbPA8qQD5-R6-w==)
27. [jmlr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDFwB6nsNQqj_07DD-wkqRc3ha6z_c90Uxifosy4Bf4lOANzNPIt64AkUTtGo8VM0BdJgEKiAodN9ccVgNhyNht-CdJBZFoNpvMPhj6y3EfUd38sD3Z83docwTr4ksZxOfZSgt2tuevDQ=)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxMzGaNDg-_VvQ6Y3qRiZqsH4O27vP8Z5VB3rpfAczpVShLCom9HjYPshMZKG9GDJQNUTui0WY8ooXRPUZYmWdXJ-on0qGgJ1USXVS9VSDuiClp0Oecw==)
29. [jmlr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwGzvPGmFpTnKDr8Hn3-lNoDyrV4z41n3YgEWk3lJxwrcKM6iYoRoIGO2ZJXna8x_b_-p6I_SLVcgY68SWXZJRgKVqkkWTjfEkvph5Ck9-x1O3PJDkQDgvpHi407D2pLPx8QYaPWrdCelpVIiZiQ==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWuBC-euAs2JlK1OMLwIGmhQ8bHhAaIvtWXdjNMkG9_k8Su98krDw3Gj_-Rv3pP2JIUbE3Ts_N9Nnjk1VFbK78zl7uTM2GvtTdgKYZBS0T8gegBBEsZbY=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkG57A28dJ3OvTGr720A1dVfnxVDNSwbewD0sQz2d9cl-oqIClGDFjtMLH8dbiOnvw0Whlmn3rrN9Ezojksf7ZwRH1tpVauaP1ieONjH87zJkPgSy3kcGIzg==)
32. [tensornetwork.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT_nVz4nnkVm3S8Yln0nDm3IPvaRPRCOT9m4RwLasZ8oU6alLwr-2TUQLBuSji2O8L_B5lI9CJXCorAwsvYtyN53OwEEi01pJcBevj8ZIj65G8rg5NhMMnXoDtP93edm2leMmd)
33. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXbXRKqwoleXjZ6TsKC0HyDtK6yy3K87276oXMTXVxems7dzGyDVWy7MSzZ6gDZQks-_3uzvVt9hPe9UgpztV0FTjBiOr6TQ0cZBE0I_teshs8Y5xmMoqw_V2xQ6j1o2DKsBmBBIdO)


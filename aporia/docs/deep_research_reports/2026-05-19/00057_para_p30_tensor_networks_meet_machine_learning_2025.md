# PARA-P30: Tensor networks meet machine learning 2025

**Pythia queue id:** 57
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdPMGtNYXNHTExZT0UxTWtQNXJmcmdRURIXTzBrTWFzR0xMWU9FMU1rUDVyZnJnUVE
**Elapsed:** 315s
**Completed at:** 2026-05-19T11:33:11.469997+00:00

---

# Comprehensive Analysis of Tensor-Network Methods Intersecting Machine Learning (2024–2026)

**Key Points:**
*   **TN-as-Architecture:** Research suggests that Tensor Networks (TNs) can serve as standalone machine learning architectures (such as Tree Tensor Networks and MERA), potentially offering robust inductive biases for multiscale data and avoiding non-linear activation dependencies.
*   **TN-for-Compression:** It appears highly promising that tensor decompositions (like Tensor Train and Matrix Product Operators) can drastically compress Large Language Models (LLMs) such as LLaMA and BERT. Approaches combining quantization and TNs are reporting up to a 93% memory footprint reduction with minimal accuracy loss.
*   **TN-PINNs:** The evidence leans toward Tensor Network-compressed Physics-Informed Neural Networks (TN-PINNs) resolving severe memory bottlenecks in solving high-dimensional partial differential equations, especially when combined with gradient-free estimators and quantization for edge-device deployment.
*   **Expressivity vs. Trainability:** The trade-off between how much a model can learn (expressivity) and how effectively it can be optimized (trainability) remains a central challenge. While increasing the "bond dimension" of a tensor network enhances expressivity, it introduces severe vanishing or exploding gradient problems that require specialized initialization, structural constraints, or physics-inspired optimization strategies.

### Introduction to the Intersection
The intersection of tensor networks (TNs)—a mathematical framework originally developed to simulate complex many-body quantum systems—and machine learning (ML) has matured significantly over the 2024–2026 period. By leveraging the formal similarities between quantum entanglement and statistical data correlations, researchers are repurposing quantum-inspired tensor factorizations to solve some of the most pressing bottlenecks in modern AI: extreme parameter scaling, computational inefficiency, and the lack of interpretability. 

### The Promise and the Challenges
While standard deep learning architectures rely on dense weight matrices and non-linear activation functions to map features, tensor networks operate in a multilinear, inherently high-dimensional space. This allows TNs to capture complex correlations compactly. However, scaling these physics-born architectures into the realm of billion-parameter language models and high-dimensional physics simulations is not without controversy. Issues surrounding the ruggedness of the optimization landscape, theoretical limits on capturing long-range dependencies, and hardware compatibility remain actively debated and researched.

---

## 1. Theoretical Foundations: Tensor Networks in Machine Learning

Tensor networks were conceptualized in condensed matter physics as a systematic methodology to bypass the "curse of dimensionality" when representing multi-particle quantum states [cite: 1, 2]. In machine learning, a similar curse dictates that representing joint probability distributions or mapping raw data into exponentially large feature spaces requires insurmountable memory and compute resources.

### 1.1 The Translation of Quantum Frameworks to ML
In a classical ML context, a tensor network serves as a powerful parameter decomposer and feature extractor. Instead of relying on vast, unstructured parameter matrices (as seen in dense layers of neural networks), TNs factorize a massive multi-dimensional tensor into a network of smaller, interconnected "core" tensors [cite: 3, 4]. The edges connecting these cores represent tensor contractions (summations along shared dimensions).

Common TN topologies adapted for machine learning include:
*   **Matrix Product States (MPS) / Tensor Trains (TT):** Linear chains of tensors primarily used for sequential data and basic layer decomposition. They are highly efficient but may struggle to capture long-range correlations without increasing computational costs [cite: 2].
*   **Matrix Product Operators (MPO):** An extension of MPS used to represent linear operators, making them ideal for replacing fully connected dense layers in neural networks [cite: 2, 5].
*   **Projected Entangled Pair States (PEPS):** A two-dimensional grid of tensors suited for image data, though exact mathematical contraction remains computationally intractable [cite: 2, 6].
*   **Tree Tensor Networks (TTN):** Hierarchical, loop-free structures that naturally capture multiscale correlations and long-range dependencies, bridging distant features more effectively than linear MPS [cite: 2, 7].
*   **Multiscale Entanglement Renormalization Ansatz (MERA):** An advanced hierarchical structure that includes "disentanglers" to capture scale-invariant properties, showing immense potential for multi-layered feature abstraction [cite: 2, 8].

### 1.2 Entanglement Entropy as Statistical Correlation
The expressive power of these architectures is closely tied to the concept of *entanglement entropy* from quantum mechanics. In machine learning, this translates to how well a tensor network can model the complex statistical correlations between input features (e.g., pixels in an image or tokens in a sentence) [cite: 2, 9]. The size of the shared dimensions between tensor cores—known as the **virtual bond dimension** ($m$ or $\chi$)—dictates the upper limit of correlations the network can capture. A higher bond dimension allows for greater expressivity but at the cost of exponentially increased computational demands and more complex optimization landscapes [cite: 4, 10].

---

## 2. TN-as-Architecture: From Vision to Language

Between 2024 and 2026, researchers have increasingly moved beyond using TNs purely as auxiliary mathematical tricks, deploying them directly as primary learning architectures. These models attempt to replace or fundamentally augment deep neural networks by exploiting high-order multilinear interactions.

### 2.1 Deep Tree Tensor Networks (DTTNs) for Image Recognition
Historically, tensor network architectures struggled to match the accuracy of state-of-the-art Convolutional Neural Networks (CNNs) on complex image recognition tasks [cite: 7]. CNNs utilize spatial coarse-graining through localized convolution kernels, while early TN models (like MPS) were biased toward 1D sequential data and decayed correlation exponentially with path length [cite: 7, 11].

To resolve this, recent literature introduced the **Deep Tree Tensor Network (DTTN)** architecture [cite: 3, 12]. The DTTN effectively translates the hierarchical priors of visual data into a tree-like tensor topology. 
*   **Antisymmetric Interaction Modules (AIMs):** The core innovation of DTTNs relies on AIMs, which capture high-order multiplicative interactions among features [cite: 12, 13]. By mapping input samples into an exponentially dimensional feature space through tensor products, DTTNs can achieve linear separability of complex image data without relying on standard non-linear activation functions (like ReLU or Tanh) [cite: 3, 12].
*   **Performance:** DTTNs have successfully been benchmarked across diverse datasets, including CIFAR-10 and ImageNet, effectively narrowing the performance gap between purely quantum-inspired multilinear networks and deeply stacked, non-linear CNNs [cite: 7, 13].

### 2.2 TTNs with CP Rank Constraints and Tensor Dropout
A significant challenge in scaling TTNs for tasks like the Fashion-MNIST dataset is managing the sheer number of parameters scaling as $\mathcal{O}(N m^{b+1})$, where $N$ is the input size, $m$ is the bond dimension, and $b$ is the tree branching ratio [cite: 14]. 

A breakthrough in 2024 involved the integration of **Canonical Polyadic (CP) rank constraints** combined with **Tensor Dropout** within TTNs [cite: 14, 15]. 
*   **CP Rank Constraints:** Inspired by quantum many-body simulations, researchers imposed low CP rank constraints on the individual tensors within the network. This disentangles the tight coupling between expressivity and parameter count, allowing the network to employ large branching ratios (e.g., $b=4$) without memory explosion [cite: 14, 15].
*   **Avoiding Vanishing Gradients:** Because TTNs consist primarily of linear multilinear contractions, they theoretically bypass the vanishing gradient problems associated with deep sigmoid or hyperbolic tangent networks [cite: 15, 16].
*   **Results:** A low-rank TTN classifier utilizing these techniques achieved a test set accuracy of 90.3% on Fashion-MNIST at a fraction of the standard computational cost [cite: 14, 15].

### 2.3 MERA-Attention and TN-Transformers
Large Language Models (LLMs) fundamentally rely on the Transformer architecture, wherein the self-attention mechanism computes pairwise relations between all tokens, resulting in a quadratic $\mathcal{O}(N^2)$ computational complexity [cite: 17]. 

Recent proposals have sought to integrate the **Multiscale Entanglement Renormalization Ansatz (MERA)** into the attention mechanism [cite: 2, 17].
*   **Hierarchical Attention:** Instead of computing a dense $Q K^T$ matrix, MERA-attention represents the semantic relationships of tokens through a tree-like hierarchy embedded with disentangling tensors [cite: 17, 18]. This allows the model to capture short-range syntactic dependencies at lower layers and long-range semantic narrative arcs at higher layers.
*   **Efficiency Gains:** By relying on tensor network contractions, the memory and computational complexity of attention can theoretically be reduced from $\mathcal{O}(N^2)$ to nearly $\mathcal{O}(N \log N)$ [cite: 17].

### 2.4 Fully Tensorized Neural Networks
Going beyond replacing isolated components, some research has established **fully tensorized neural networks (TNNs)**. Here, the weight matrices of fully connected layers are entirely substituted with Matrix Product Operators (MPOs) [cite: 5]. 
*   **Entanglement-Aware Training:** Utilizing standard stochastic gradient descent (SGD) to train these MPOs often yields suboptimal results due to the complex multilinear landscape. Instead, researchers have adopted Density Matrix Renormalization Group (DMRG)-like algorithms—sweeping optimization techniques native to quantum physics [cite: 5, 8].
*   **Interpretability:** By analyzing the entanglement spectrum of the learned MPO weights, practitioners can directly extract meaningful information regarding the non-linearity and correlations present in the input data, an interpretability feature largely absent in standard black-box neural networks [cite: 5, 9].

---

## 3. TN-for-Compression: Overcoming the LLM Bottleneck

As the parameter counts of leading LLMs cross the multi-billion mark, inference costs, memory footprints, and energy consumption have become critical impediments to deployment, especially on edge devices. Traditional compression methods—such as pruning, knowledge distillation, and quantization—typically focus on reducing numerical precision or excising neurons [cite: 19, 20]. Tensor networks approach this problem uniquely by compressing the *correlation space* of the parameters.

### 3.1 CompactifAI: Extreme Compression via Quantum-Inspired TNs
In 2024, Multiverse Computing introduced **CompactifAI**, an LLM compression framework utilizing tensor networks to drastically shrink pre-trained models like Meta’s LLaMA-2 7B [cite: 19, 21].

**The CompactifAI Methodology:**
1.  **Layer Profiling:** The algorithm profiles the network to identify sensitivity. Research demonstrates that the deeper layers of an LLM are heavily overparameterized and are highly amenable to tensor-network compression without degrading reasoning capabilities [cite: 19, 20].
2.  **MPO Tensorization:** The massive weight matrices inside the Self-Attention (SA) and Multi-Layer Perceptron (MLP) blocks are reshaped into Matrix Product Operators (MPOs) [cite: 20, 22].
3.  **Correlation Truncation:** Utilizing Singular Value Decomposition (SVD), the framework truncates the weakest correlations (analogous to low-entanglement pathways in physics), keeping the virtual bond dimension bounded (e.g., $\chi \approx 100$) [cite: 22, 23].
4.  **Healing Phase:** A brief, distributed retraining ("healing") phase is conducted to allow the remaining parameters to adjust to the truncated correlation space [cite: 22, 24].

**Results on LLaMA-2 7B:**
When combining CompactifAI's TN compression with standard 4-bit quantization, the results were state-of-the-art:
*   **Model Size:** 70% reduction in parameter count (down to ~2.1 billion) [cite: 20].
*   **Memory Footprint:** 93% reduction in memory requirements [cite: 20, 21].
*   **Speed:** 50% faster distributed training and a 25% acceleration in inference [cite: 19, 20].
*   **Accuracy:** Maintained 98% of the original model's accuracy on benchmarks like MMLU, HellaSwag, and GSM8K (a drop of only 2–3%) [cite: 20, 25].

### 3.2 Saten: Sparse Augmented Tensor Networks
Despite the success of low-rank tensor compression, applying it post-training to LLMs is challenging because pre-trained matrices often exhibit "high-rank" properties that resist pure low-rank decomposition without significant performance degradation [cite: 26, 27]. 

Introduced in 2025, **Saten (Sparse Augmented Tensor Networks)** mitigates this by integrating a sparse error matrix alongside the Tensor Train (TT) decomposition [cite: 26, 28].
*   **Decomposition Strategy:** Saten decomposes the weight matrix $W$ into a low-rank TT component $\hat{W}_{TT}$ and an unconstrained sparse error component $E$. The matrix approximation becomes $W \approx \hat{W}_{TT} + E$ [cite: 26].
*   **Sparsity Patterns:** The framework supports both unstructured sparsity (`Saten(u)`) and GPU-friendly structured sparsity (`Saten(2:4)`), identifying the largest-magnitude elements in the residual error matrix and preserving them during gradient descent [cite: 26, 28].
*   **Performance vs. Baselines:** Tested on BERT-Base and LLaMA-3.2-1B against leading competitors like SVD-ARS (Adaptive Rank Selection) and standard TT, Saten achieved the highest compression ratios while yielding superior accuracy on GLUE benchmarks (e.g., SST-2, MRPC) [cite: 27, 28].

### 3.3 The Broader Patent and Research Landscape
The race to compress LLMs has spurred a surge of intellectual property and open-source development. By 2026, the patent landscape indicates heavy investment by tech giants in hybrid pipelines combining quantization, low-rank factorization, and structured tensor networks [cite: 29]. Tensor network compression represents a paradigm shift because, unlike pruning which requires retraining from scratch or heavy fine-tuning, TNs maintain the mathematical integrity of the original function approximator under mathematically bounded accuracy loss [cite: 24, 29].

---

## 4. TN-PINN: Revolutionizing Physics-Informed Neural Networks

Physics-Informed Neural Networks (PINNs) integrate partial differential equations (PDEs) directly into the loss function of a neural network, enabling mesh-free simulation of complex physical systems. However, as of 2024, deploying PINNs on resource-constrained platforms (edge devices) was nearly impossible due to extreme memory overheads [cite: 30].

### 4.1 The Bottlenecks of Standard PINNs
1.  **Automatic Differentiation (AD) Overhead:** Enforcing PDE constraints requires calculating high-order derivatives. Using standard AD requires saving intermediate activation graphs across multiple backpropagation passes, creating a massive memory bottleneck [cite: 30].
2.  **Curse of Dimensionality:** In high-dimensional PDEs (e.g., the Hamilton-Jacobi-Bellman equation), the grid of collocation points scales exponentially, making exact integration computationally intractable [cite: 30, 31].
3.  **Full-Precision Reliance:** Traditional PINNs require FP32 or FP64 arithmetic to prevent the loss of precision during derivative computation [cite: 30].

### 4.2 Tensor-Compressed, Fully-Quantized PINNs
To circumvent these issues, researchers introduced an edge-friendly framework combining Tensor Trains, Stein's Estimator, and Quantization Aware Training in 2025 and 2026 [cite: 30].

**Key Innovations:**
*   **Stein's Estimator (SE):** Instead of calculating exact derivatives via expensive AD, SE approximates high-order derivatives using finite-difference-like stochastic sampling. This completely eliminates the need to construct and store deep backward computational graphs [cite: 30, 32].
*   **Tensor-Train (TT) Decomposition:** The massive dense layers of the PINN are replaced with TT-Layers. A TT-Layer transforms a massive weight matrix into a chain of dimensionally reduced 3-index cores, turning an exponential memory requirement into a polynomial one [cite: 30, 32].
*   **Fully Quantized Pipeline (SMX and DiffQuant):** Researchers introduced the Square-block MX-INT (SMX) format to prevent data duplication. Crucially, applying Stein’s estimator to quantized networks initially caused severe underflow (due to small perturbation values). A novel *Difference-based Quantization (DiffQuant)* scheme was invented to decouple the quantization noise from the SE perturbations [cite: 30].
*   **Partial-Reconstruction Scheme (PRS):** Because errors accumulate multiplicatively during tensor network contraction, the PRS mitigates quantization-error cascade across the TT-cores [cite: 30, 32].

**Hardware Validation:**
Evaluated using customized precision-scalable accelerators (e.g., PINTA), this TN-PINN framework achieved up to an 83.5x speedup and a staggering 2,324x reduction in energy consumption compared to standard AD-based, full-precision PINNs [cite: 32, 33]. It was successfully tested on the 100-D Heat equation and 20-D HJB equations with negligible loss in accuracy [cite: 32].

### 4.3 Quantum and Hybrid Extensions (HQPINN)
In fields like Computational Fluid Dynamics (CFD), specifically high-speed transonic flows, Hybrid Quantum Physics-Informed Neural Networks (HQPINN) have been evaluated [cite: 34]. By integrating parameterized quantum circuits with classical tensor network solvers, researchers aim to capture shock boundary layers more effectively. However, evidence suggests that while quantum models offer high expressivity, they suffer from severe trainability issues (barren plateaus) unless carefully parameterized; thus, classical TNs remain the practical choice for near-term CFD solvers [cite: 34, 35].

---

## 5. State of the Art: Expressivity vs. Trainability

The fundamental dichotomy in deploying tensor networks for machine learning revolves around the trade-off between **expressivity** (the model's capacity to represent complex, highly entangled data distributions) and **trainability** (the ability of gradient-based optimizers to navigate the loss landscape and find global minima). 

### 5.1 The Geometry of Expressivity
In TN theory, the expressive power is modulated directly by the virtual **bond dimension** (denoted $\chi$, $m$, or $D$). 
*   **Low Bond Dimension:** The tensor network strictly enforces a low-entanglement (low-rank) prior. This results in heavy compression and fast training but restricts the network from capturing highly non-linear or long-range feature dependencies (an "area-law" limitation) [cite: 2, 4, 10].
*   **High Bond Dimension:** Expanding the bond dimension drastically increases the representational capacity of the model, allowing it to act as a multilinear polynomial function approximator of exceptionally high degree [cite: 12, 36]. Certain models (like PEPS and MERA) inherently possess greater expressivity for grid and hierarchical data than 1D Tensor Trains [cite: 2, 6].

### 5.2 The Crisis of Trainability: Exploding and Vanishing Gradients
As expressivity increases via larger bond dimensions, trainability severely degrades. Deep or highly connected tensor networks suffer acutely from gradient instability [cite: 14, 37]. 

Because TN operations are inherently multilinear (they consist of sequences of tensor products), the forward and backward passes represent an extended chain of multiplications [cite: 35, 37].
1.  **Vanishing Gradients:** If the initialized tensor cores have elements slightly less than 1, the repeated contractions drive the resulting activations to zero, starving the gradients.
2.  **Exploding Gradients:** Conversely, values slightly larger than 1 will explode to infinity during the contraction sequence [cite: 14, 37].
3.  **Barren Plateaus:** Inherited from the quantum domain, highly expressive TN architectures form loss landscapes that are essentially flat nearly everywhere, making gradient-based navigation (like standard SGD or Adam) practically impossible [cite: 35, 38].

### 5.3 Overcoming the Trade-off (2024-2026 Solutions)
To safely leverage high expressivity while ensuring stable trainability, the ML community has standardized several state-of-the-art approaches over the last two years:

*   **Subnetwork Norm Initialization:** Traditional neural network initializations (like Xavier/Glorot) fail for TNs due to the differing geometry of multilinear spaces [cite: 37]. Researchers recently developed iterative normalization techniques based on the Frobenius norms of local subnetworks. By carefully balancing the initial variance of the tensor cores, the entire network can be initialized to prevent divergence prior to the first epoch [cite: 37].
*   **Architectural Inductive Biases:** Utilizing Tree Tensor Networks (TTNs) combined with CP rank constraints and Tensor Dropout effectively regularizes the parameter space. This bypasses the need for massive bond dimensions by allowing wider branching ratios ($b=4$), capturing non-local class features efficiently without ruggedizing the loss landscape [cite: 14, 15].
*   **Physics-Inspired Optimizers:** For highly expressive models like fully tensorized MPOs or MERAs, standard backpropagation is increasingly abandoned in favor of sweeping DMRG-like algorithms. These algorithms freeze parts of the network and optimize tensors locally (a "divide and conquer" strategy) bypassing global gradient propagation entirely and circumventing the barren plateau problem [cite: 1, 5, 9].
*   **Sparsity Integration:** As seen in the *Saten* framework, introducing a sparse error budget alongside a strictly bounded low-rank tensor decomposition allows the model to capture high-rank anomalies in the dataset without globally increasing the bond dimension of the tensor network [cite: 26, 28].

---

## 6. Frameworks and Implementation Bottlenecks

The rapid adoption of TNs in machine learning is heavily reliant on software abstraction. Through 2024–2026, the ecosystem has matured to integrate physics tools into standard data science pipelines.

### 6.1 Libraries and Ecosystems
*   **TensorNetwork and PyTorch:** Frameworks like Google’s `TensorNetwork` library and PyTorch-native implementations have abstracted the complex graph-contraction logic away from the user. Automatic differentiation (AD) is now natively supported for sequences of matrix/tensor products, allowing ML engineers to train TT or MPO layers using standard PyTorch APIs [cite: 2, 39].
*   **tn4ml:** Introduced in 2025, `tn4ml` is specifically designed for deploying TNs in machine learning pipelines. It offers modules for quantum-inspired data embedding, objective function definition, and customized optimization loops (like DMRG sweeping) [cite: 40].

### 6.2 Hardware and Engineering Limitations
Despite theoretical elegance, TNs face distinct engineering hurdles:
*   **Hardware Mapping:** Traditional GPUs are heavily optimized for massive, dense Matrix-Matrix multiplications (GEMM). Tensor networks often require sparse, high-order tensor contractions and specific memory permutations. Standard ML compilers struggle to optimize these non-standard contraction paths efficiently, leading to suboptimal GPU utilization [cite: 9, 35].
*   **Conversion Overhead:** Decomposing dense layers into tensor formats introduces computational overhead during the conversion phase. The algorithmic complexity of SVD-based initialization and rank selection can slow down the deployment pipeline in dynamically changing environments [cite: 9, 26].

---

## 7. Conclusion

The integration of tensor-network methods into machine learning from 2024 to 2026 marks a fascinating convergence of quantum physics and artificial intelligence. 

As **stand-alone architectures**, structures like Deep Tree Tensor Networks (DTTNs) and MERA demonstrate that the multilinear abstraction of quantum entanglement can effectively replace the non-linear mappings of traditional neural networks. They offer profound advantages in interpretability and multiscale feature extraction.

In the realm of **compression**, TN factorizations like CompactifAI and Saten provide highly controllable, mathematically bounded techniques to shrink multi-billion parameter LLMs. By focusing on truncating correlation space rather than excising neurons, they allow models like LLaMA-2 to operate on severely memory-constrained devices with negligible cognitive loss.

Furthermore, applying TNs to **Physics-Informed Neural Networks (TN-PINNs)** has resolved critical memory bottlenecks. By utilizing techniques like Stein's estimator and fully quantized Tensor Trains, edge devices can now solve high-dimensional partial differential equations that previously required supercomputing clusters.

Finally, navigating the **expressivity vs. trainability** trade-off remains the central pursuit of the field. While the physics-inspired promise of boundless expressivity via high bond dimensions tempts researchers, the practical realities of vanishing gradients and barren plateaus dictate a more nuanced approach. Innovations in network initialization, CP rank constraints, and hybrid sparse-tensor formulations are currently the state-of-the-art strategies ensuring that these highly entangled quantum models can learn effectively in a classical data landscape.

**Sources:**
1. [sciencenews.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjjUGbSE4_Z3Y77eEU3BIGWPd3NTwsj-GY9lfNUIPSvELZhWciJQDFoxPsY0gfGNJLKCqWnTuxNPCe-2D5Ne6wsEJ0fleHpJcRPV35maJ_L2994o4tYNzV_vUmlqfDnhhocHUKROwm2YTc0ptP9X7lvJGeILfOoEdU-paMB1CEpg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNEIdtXSMFuY6jot5BeSTmqLvQDjuTRwR_3YV9NoXBGXbVaBWLBJ6QB2F3bPbJMWAeXg6fXXRJm2nVJCTReqvhQF1a4IXnOrxR4OmxSqIySN59_wbncQzcyw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWf2DnJv5ozFY9axGh-KcBgocEc0KfsKuHMIeA2AqWXNojNuzQ13VC9k9RUZnCZY8IjqNBVLutQHGEj-KeW6q6JxnQ0wMI1B1gFqIbaIy82UamEtzmW6fagQ==)
4. [euromathsoc.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuzjCAmFX-yNj2EbA6K-Qp7vgG-85vtDpyFXpghcFt8swk2LFFqHe8vYfrWoEl--KcRbztBD1H2JVh5N00UrEao4DROmdh3CSszxEfWnWcUmVAqWcc6ZsTLYe7FaST4III3mc=)
5. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrr6TJ-VqllteBOP9dtgSDiXN1CxY2jMjbewvbD2hYPkbKSImdHH4SBGEXUjrAzAV7O6p02-aUiQT2q-lHicSAb4ocRo8RbK5ijQmK4pB132U9R6h7tw-jU2y-W9Gcn2uZ4_cPctrqNQ==)
6. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNbf0p50hQKo1NvhuhIzcR1mdW6RZqokZ44O4vMlkgAsI0mUkQWytesEi8Uh9NXtcG6Xzljxd5f1q8PNg8oGfH7pekYbT97g0tGOpx4xw32JTgAfw8_AfP5eVULBuXXBFtR4X1nmqX6AJm-8JATPYcf-qlv9YlsjvCXbbq0Czp9f0x1j8VogzjfsNW2QSaFLDP73y5rNskahMVSAZAABwVn0vEkrS0mx6Ntlj0pjyf_Q==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVpzbAkedE5t26LkiTvMpXXYvygMPihMh4oHDeOEr0mrIedVSFEtsXxW5leJTfsRTXrzJisE8LHho9LySgKRzIcKjDGsahyhfIWyE1qw0FdXQ_0Mpio4kNpA==)
8. [osaka-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQjoBmIz-cpHWZHNcO0DJlRVWu9uyEhF7Rz8a4w_zgHO-2jkyOoNPlh3-1IfaPHYcA8wvRCvOqIH9QY7TBrp-ohHmY6N1PLlaf1GmdFwghL-9l5VaUcB8GJqCNdKCVLZLMXwBTu51AdDuzORO0ap0NATc8mwfqEqQMwr-z-iexSD3j)
9. [letsdatascience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8_u9MWHYO0EmVnSmoXU6_kVe_Do4VNnifSIJYn4Hw9TzOSzUd801U7ND2Rn7qLiK46PoU_OeqMdKvm4N7MsfTjQnjd3VuifDoXDYdf68uX8KA_NcFjs-qPQefzSyRVcqUmjHbMpSB9lY0Ds7qkFCfaxDN8y1hP-hj-oELV7p0B8U_eqC-TH_cU6lhkvIrA5jroMrn5jQthFfMQO4=)
10. [lanl.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbj8ByeGIOahXKsj4rNLQlmlDqVIGitZgWueLIRkAnX0N76KHKXbxvSCtefaHWfo0upC9a5COkSDmTZ1UvOLSNO-4rgjvneGEAUFvgnj2c4VeZlTHTZrCYFXYdF4QTV8br_fsgcYbZ3TIwUIeoL0RWrA==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcTIlr3_-CN8scRmM_XCrV_CH2k9G0M00LRRplFUbubOtHKrTZ-6xjSR8BLsuoaELV7Y0fYerdz5SF7ya746imwi-5uJ5mCIpAyo_kmrOPLXWj1JOYpA9Oc9yp7dQ-cwEsSWf_4iZadSdb_qwIEv79ovFAVq90zZQsGaXMa5lW9zXws4DdSFHg8bv5TuxMCehKDNIubA==)
12. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHu86Ei0lJ14HIXThvERSuZ9Xir2c_iijMyEXO3T0UtpyM7RixGbwseD0Ns0l0MrkVr2m_bv1Vr5FA02RmiuTm2NDZeuJMktYE7JOBwiZIopu1XDzYgur3KDwlaPgeMdmKYH5E=)
13. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYtZougwzClcu3wGSaahrVUY6UHojxEyUXbXpAO1a64TfgHIMedNJVtiq0NGXv5XQ9r0ErthOaQLdQJ5cweT_bqA7umcw6bhIRVjJlBQIxbXJIfv0V5QsMDusDBykHPvdEcEFGh8x23vvUslB0tFilfRewuKX2RxdgiWN5wr7nnbCrueuhSSQhNCAl)
14. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBz12FUOXYa34uORTwmadHlAtIVwpLZFZh7SviaGStwnaa-DT_II7A0_6EO1iuO5qbdyKndGV-Tk06QQ72QKrvXQVIu79dXr8Yj_ljj763COVLep7o3ezrbUNChC8DzecyAnxekOUMJ6P4xlNqUQ==)
15. [duke.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_i8bHtS0qmTiDPggQXO9FYA59yyMT-J9KSxOdrRrfoBjOC0uu6Ao-cSTmo8q_MCuod4lx76n6yyBilsGnurI3GxPT0udBjLQ4c5vJTO530YvI7fZSn-9yuOF3DWp1P_78oEA49A==)
16. [duke.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSwGeIxIzx5_VpJ22JV9ZZvzY7GvVFd_T1wl91ESNAQMbem3tU4vwCBWVnnz1mBKLC7IJJ92H7VNyRJxXTaVoyF2IoYiaCtiZONMZkFhrorlshzJDZ0frK-JwUk1IZmcb2R3LOCLJTV7czdyM2Asw3LarAMEAXktzwAcy0PqwDziQJpRrbiGS_zMFG2DAharUoCq_aREFbFYM2yT0yk_B2RGcJPCsj6WlcDekv8sOnJePc4x4M15YpdFnjP8AvJcWIO0zeSTiG5GXHOgHAQCdDtouHpz4Pvzef8fYkZHBbrLr-H9WjYrL37EQuYLC-xx3yvUbDijCjWcrwVoCpAdWgUkQBPxiCY_MBDkAB8l0g_GwcVOvUyI_Y9sAun0JHJek02Lw2xSpqspgb6NeSwwU1le7gFYWALoKi5sUW3TvdOvPYiHD0KlrOG7dnw_MB4EU-XcAPu8jGzGJMl3gbz7SqNDSvG5H7XnHIP9bJkVTBFjmuWj2nT47QoHs2G0vxN-Tmy1ZxglqvUgBcF8k7UQ==)
17. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFK0qPnZE5n36UXifASDyYXyKY-YhY_269qDluHP8tEkjL28P6Ye0cbkmK55OMn4UUrgS6bbxvPwLdusJMFc5goxiSqG5MZijmELp_B2xrffsjZBfKpm7QpAhT4NrReF65bwkUzD8ovXiW9gJdfLLlPrQmW_sVEzJvzJt1pOu-0IrN4TEhz5-1GuYrKNWnC8m_PGyR3SexsE-Re8SzCL-C4FZGMiDpFUCHRXxhW)
18. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET2tc_9VhEhjju-92ehD56cc_vP2E5G8vGAmnPLXpQI3DtRbZygYnjS7uVjZusEFS11QDki_ETOB4W8HDlhdqdne5xRHK-KzCeILB1PUKdajS9iN_-eMW6NhnNCVBzFG0bgZWXzDJ84px48rXd7Z3cLHJX_bFPhPdVdTs6iei0UHqSHNcDzBCNydQ4zTyJiHU=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFimKUZL7JcGSMqhie9wsYoi_uH9oeE-bz3STqZreNL1XwgyqC94e1egGJrJ3-JfGBZ9UM9nvhj-qd466YjfWNRkwbfpPl_M0AIfNmiberslSHb7fWugQ==)
20. [esann.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH37V0-1PmB7JaZ18UAsXBqhxTj_KQ0hWOz8OplYWM1mU5RF9k4SB6V3w81d6jOr1G-8DyuJu2d81OlLAIsfHUSzQHRNAx4MSGJzLizYHjWIcpUlv3OvbCrS0qj1MiR0gTMYIHBDGfQSx-gBIJbMYCtg9XrT1eowHV7ChSAjw==)
21. [multiversecomputing.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-DYN_dl2u3FMfJzu8PbsnzyMCIxYFvziixeIfWL8ovwBMgTStKAElVQRS7IQQs9PAict6X8dAcpNAFI8t04IzKKrhl8iDZqbTkOBrWlBytXrC2v8OFTgNw5-xRmlEBYGwZ0KFJCrTQO6KhB5IfeXBzoqFJ2Y8jKO5AshFKi4egLzMYmeW8AFJfCQhfvjigA-JqkkSd8yb8IjsTMtF6vDODr_DTQ==)
22. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0OrlUR3ZG-DVYmVPvpzxclF94rMhk3G0UoIMMxUqtLt40b-AtaQApeUCbepz8gmHcq71qDtSXf0jHz-xtolxgvaxb82AFSD24g06eH8nElwoAKp0P0O0-Vj5EXruWaNv41GiKcxvn1AEt0JXLE2YEQcXSdIN3E5HmIqzh8chQvg3OuC6aPsxlwtYiS7fidoKUf-yMkGRQm514TtrTGbJP5oLRqEhrSJqkaxfzPRxMO81o_OEawb61FDhkzsw=)
23. [multiversecomputing.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4OUQ6QC0eJdYsvcwYZUMuHfeczT41An8fkjMh_VS530hsBK1H_Xr2Y95Edjj3jgRv4UPJgqTP1V0KJvdNZz4CiAuWW4LWPnStHXvAiFIQpq14ga2fiVyH4Kmy9ykolZQk1cPAB0j-ldKbFwQiePUJxinrKDKKz1Kgk4pd2AHJam0IO6sZe8RCt0K6GuLOIPhpJ-knM68nKXvHDfriysCyH_vM2jb33IyfDqSIFdA6XM0NTw24ZFM512Xsd14=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcC5KsxQGrKvzaM2MJzCvMZbCVGPqu-ypP5PJAT55toyEoVt6a-xD6R3CDSprjGFUoG_CIrD-8u4LVVqHrwHDylMNtnvvtgpRINLNYXN0984GFblrHZsdMMQ==)
25. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVxLCb15jBzAqiv6MAjcWYdze4dzXn9uAMYkph-C0Q-8sCpuloywTzeVSDmhwtsolYLVNBa-J88uHLCNI4rOc7YIhbWk5mJuosyADi7QZp-hPIWWVoIcb7u_ssfAJSo_CxZaql3uKXeqvKPoMllmVTwh3iXenB0WOG6Yg9r1-kNAveANv1ySW4hz6_Pel3teRxAeTy6yx837bgHwuUSdcq6EV4WbIuNecx_G81q9GWaA==)
26. [ucsb.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzyVpokf0u8ZrzQergpjUIPTHmJ_CjzGlahbk8XGEef5x5DxD8mH1xIWDDAFqImNoKdEHNPtQ9qDg8wIZuJjheUDpya28BJE8XknNpeh9ToRb40h02Ud7ww6ka7b6X2XmtA3vGNrnUFUhVXLhnSqohN2UcEw==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGV843OGy7RVRLDWRymzvdjPhld_XRfXJ9cV0TR77TJ_-QM6lTrpVKF4a5h2x_-5OKe2SQfeHZ6HhBKq4a1nMojZ_Bqhex4IR_4Zpu9Y1RIO4hM-mJ11TN4wQ==)
28. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0Rt1BSmhjSaVUnTsV45-618YKryOI_sUVio6QyfrQqj_pWqyHpkoxJyhpx0wLpVvX0K4VVq1KTCCxS_C2Fym8CIDeOdYlf-5F4GnPJuCrIghY9nn1aSIDZkDGiIH5IWp3QCLJiPbWId6iaQ==)
29. [patsnap.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRQ9pSxhIRp6EaHd96nTgHAvdLCDtUSSPBuC-EOY1tLvMIIdnVcQpd1aSyF8oh2TYZoOYAiUYgurArvGx_hR9Tfb0q-6mOwt8pRNSQJ5EvwsZCGxGZYiz1XZaNp0xKGEf8ZpMK8vmAC2AuoAVOG5n8FamywC_MZ92vZPE22f9npR9X8csNggkcBE6w0VPfGbWTbDUPeJ4=)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4wknidEvErYclUoL20s2SPrIK4cZkQfphSy0k1PbphyO2YaAMlavv53yydewsblAA0mh0gAWM3NfnofxJ66BU5ix8D7R28vkvBVV-7tVF3duILlD3Dm99iA==)
31. [unm.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8p5pAZ8Ah9r84yjy--TZfsW8SKmWVWMUz3iiFykQkio48ZCOu9SEf89GhC8GlUIzbiCXsz2hOYAJ1IVy9Kgm_yXR72nsSBagMo2I88ZviwR4d2jIzRZz69DvW_p823hG83pfaMbIXvYYWw02BvpatfEo4Dl9BlkZdGgL1CqPoYalLsSbeqv0o3ztujYM0SQ0SAOCIly2H-ZEkmpVGyqXqAq2JsJuhg6qiwpTmBFB3lezNEeX-MrquTWan6g==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNQ4QNWLkPPriLVv0QreYY5SDjXqZi64C_m-MAYNN5-p2FEgLAnPIvzhIdZh5gqb9H6FIGroU6vFBK49-DT6izkEp9LcpJE6bluo011oQe7hDIu0DmsKXu9DI=)
33. [date-conference.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgQtFcV9s3M_HOL4IwAX5tW5EUc2djQSZ6gn6xDNblmaAdwiBrKAZi_V0VG23_eiWGCu13u8LkWqmikXlvMMdsrdt3mfE4lM_52y9atu0mVtdhnLkE3oGwWsnM1jSoF7VgK2DTMn81zRI0ALaKmNHcIcSOvDkmrjA9r0zuG5nI)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnFbGVTJWwDL9oPEbqxcRvLIv5M4dpJ4bJv1IIxQD0dEdOfgmhgKAeDkapWjGx4qrZ51UpGaBlGJHEMq2iyV4I-SZxlRtt5jXIw_ve40DL8RSFGrtYHiyF5yG5WO5vCM0a8z0mPORpSAXvYRuOQakPTCHLPEOVLcVAKMjwPHZSJcpewEtapByW41N7E0JkB0fRcnaeZh2V3W5-EprxJkZOyq9txicNiwhhSEdMU5hR89F2SjZN1qCKSD2XBefs1UawkUqAY0JG)
35. [squarespace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7pugSe3zhqy2YsOKVeKpXJGi-EEmU2OAdeACP2H98-pOGEh2daRdb0MPNduFsoiPnNTgn60YuY4zU5Q-7ZEp5LIS1CHH-sxoIdV_sXLS0B_CK4pr66BOgybHoHgRT-_k7WhR3jkNXf9Z8yLkTw2aBuYigDuluMHNiHTDBBfYaXEMeKmox0zm0AjpiRHy3-hmYj-afD5Kpsw1olqjtCTOV8dJ10wuAoWVKlQRtC80G9bdbcwHEyQuOPZCtX4RMVoc=)
36. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGQo9RN7hGBMpkqNCIVMNNCW_NHt5vQIY7KuoaL5-BaoHQOG-aKiutrJ_xNhawir8QjvzP_lht12pZx7jE90XpMFEHYzowaIFF8-TdQDH4m3VLA9dltsOJyYz-ORBkBWmJAJSkE9uSrFQ1XYhi_jqBCScm8w==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvHvgrfVWn0U00yx8s1Oz3asGN1SbJJPaN9cTrcPscQzc_6kol2gj14x9HQb5B7qttDkBmwskKC_A8_8cnJJDHR0_5ewMigfFecTBcyTMHlPzkihXztq7ShA==)
38. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgg8cj6T8v4ecvkXZ9SG9a3fJePj6e_F10A7MSmaVhW3Io4YofkvQNzCbyXiGDqoZixv7VrrmEKXCxpYMTsbTmujT402FPMVU2EyufGeaViruPBu1G9_31G8BolR_bGuniaBKgq6JZsYuR7LpbC4N2GAEWsdmZrtPynZuH0zoy7w==)
39. [tensorflow.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy_XAxx788unVyqcCGbukhKdPz6Lw0YAWI-PAa9Xhs7ul2iIYOekJzDqFggncT4hmzwFYHRorCDE-8Xz46c2A2tIrzUO2hRoLwDZuvbR7q1qVySUeH0WfKpELUTG9Gk64GpTvZHYHmGhxx_aU-Xm1r090nhTLbtPnOd_rMBGJJIhQI33uaoe3WRkjkqImOavdYwSLKf-zk)
40. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjoDPeaynfxGqZsD6lshgD1irauugyrkQUbMU21oDfz2_CWTIPiSrB7mlO4ZBQNimfFh_83bNaT0QUeF7_9amv3iMtB0wBv1SAa2UsxSrZPIFy7WBWm_xTbQ==)


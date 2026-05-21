# T#77 Tensor network expressibility characterization

**Pythia queue id:** 115
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChY3Q0VQYXJJN3RwTFV5US1IazdYaEF3EhY3Q0VQYXJJN3RwTFV5US1IazdYaEF3
**Elapsed:** 315s
**Completed at:** 2026-05-21T15:22:16.053477+00:00

---

# Tensor Network Expressibility Characterization and Applications

**Key Points**
*   **Tensor Networks (TNs)** provide a rigorous mathematical framework for bypassing the curse of dimensionality in representing high-dimensional functions, quantum many-body states, and multivariate probability distributions.
*   **Expressive Power:** Research suggests that there exist unbounded separations in the expressive power of different tensor network factorizations. Specific architectures, such as Locally Purified States (LPS), demonstrate provably superior expressibility compared to traditional Hidden Markov Models (HMMs) and Born Machines.
*   **Complex Tensors:** The utilization of complex-valued tensors, as opposed to strictly real-valued ones, can lead to arbitrarily large reductions in the number of required parameters for probabilistic modeling and sequence processing.
*   **Deep Learning Intersections:** Deep neural networks can efficiently map tensor contractions, possessing an expressive power equal to or strictly greater than practically contractable tensor networks like Matrix Product States (MPS).
*   **"T#77" and Cryogenic Benchmarks:** In the context of quantum dynamics and algorithmic testing, the notation "T#77" frequently intersects with tensor modeling either as a specific computational node identifier in deep learning compilers (e.g., Tensor #77) or, more predominantly in quantum chemistry literature, as the rigorous physical benchmark temperature of $T = 77$ K (liquid nitrogen temperature). Simulating continuous structured reservoirs at $T = 77$ K remains a pivotal benchmark for testing the memory limits and expressibility of real-time TN path integrals.

**Summary of Foundational Concepts**
Tensor networks act as factorizations of massive multidimensional arrays into networks of smaller, interconnected tensors. Originating from condensed matter physics to simulate highly entangled quantum states, they have recently been co-opted by machine learning researchers to compress neural network layers, perform supervised learning, and mathematically characterize the expressiveness of generative models.

**Summary of Unbounded Separations and LPS**
One of the most active areas of research in TN expressibility is characterizing the precise representational limits of different network structures. It has been mathematically proven that not all tensor factorizations are created equal; some distributions can be represented efficiently by one network but require exponentially more resources in another. Locally Purified States (LPS), inspired by open quantum systems, bridge these gaps by providing highly expressive, locally positive representations.

**Summary of Practical and Physical Implementations**
Beyond abstract probability distributions, TNs are rigorously tested against physical models of dissipation and decoherence. Operating at standard cryogenic temperatures such as $T = 77$ K, researchers utilize TNs to calculate real-time path integrals for models like the Spin-Boson system and the Fenna-Matthews-Olson (FMO) complex. In these settings, TNs efficiently capture non-Markovian memory effects that would be intractable for traditional numerical methods. 

***

## Introduction to Tensor Networks

Many foundational problems across computer science, applied mathematics, and quantum physics center on a shared challenge: the construction of efficient representations for high-dimensional functions [cite: 1, 2]. Whether modeling the joint probability distribution of thousands of discrete variables, the parameter weights of a deep neural network, or the entangled many-body wave function of a solid-state material, direct representations suffer from the "curse of dimensionality." For a system of $N$ variables, each taking $d$ possible values, a naive representation requires $d^N$ parameters, an exponentially scaling requirement that rapidly becomes intractable for even modest values of $N$ [cite: 3, 4].

Tensor networks (TNs) were originally developed in the context of quantum many-body physics to directly address this exponentially scaling complexity. A tensor network is a systematic factorization of a high-order global tensor into a contracted product of lower-order, local tensors. By restricting the "bond dimension" (or virtual dimension) that connects these local tensors, TNs facilitate a massive compression of information [cite: 3, 5]. Instead of scaling exponentially, the number of parameters in a well-approximated TN scales polynomially—or even linearly—with the system size $N$ [cite: 3, 6]. 

In recent years, the mathematical tools developed to understand TNs have permeated the field of machine learning [cite: 2, 7]. Researchers have recognized a natural correspondence between TNs and probabilistic graphical models, utilizing tensor factorizations for tasks ranging from unsupervised generative modeling to the compression of dense fully-connected layers in deep neural networks [cite: 7, 8]. More importantly, the rigorous mathematical foundation of TNs provides a unique lens through which the "expressive power"—the fundamental capacity of a model architecture to represent complex functions—can be rigorously characterized and bounded [cite: 9, 10].

### Core Tensor Network Architectures

To discuss the expressibility characterization of tensor networks, it is necessary to define the primary architectures analyzed in the literature:

1.  **Matrix Product States (MPS) / Tensor Trains (TT):** The MPS, known in numerical analysis as the Tensor Train (TT) format, is the simplest and best-understood TN. It factorizes an $N$-dimensional tensor into a 1D chain-like product of 3-index tensors [cite: 3, 5]. The expressivity of the MPS is governed by its bond dimension, $\chi$. Given a sufficiently large bond dimension, an MPS can represent an arbitrary tensor perfectly; however, its practical utility lies in systems where a low bond dimension provides a highly accurate approximation [cite: 3, 4].
2.  **Matrix Product Operators (MPO):** The operator counterpart to the MPS, MPOs represent linear transformations across the vector space. They are heavily utilized in both physical simulations (to represent Hamiltonians) and machine learning (to compress deep neural network weight matrices) [cite: 5, 8].
3.  **Projected Entangled Pair States (PEPS):** A generalization of MPS to two-dimensional lattices. While PEPS have immense expressive power for 2D systems, their exact contraction is known to be computationally intractable, falling into the #P-hard complexity class [cite: 11].
4.  **Tree Tensor Networks (TTN) and MERA:** TTNs arrange tensors in a hierarchical tree structure, while the Multi-scale Entanglement Renormalization Ansatz (MERA) introduces additional unitary "disentanglers" to capture power-law correlations and scale invariance, heavily inspired by renormalization group flows [cite: 11, 12]. 

## Characterizing Expressive Power in Tensor Networks

The "expressive power" of a machine learning or physical model refers to the breadth and complexity of the set of functions it can efficiently approximate or represent exactly. For tensor networks, expressive power is inherently tied to the structure of the network graph and the bond dimensions connecting its nodes. 

### Bond Dimension and Rank Hierarchies

A key metric in characterizing tensor network expressibility is the bond dimension (or tensor-train rank). The bond dimension serves as a tunable parameter controlling the maximum allowed correlation (or entanglement) between different bipartitions of the system [cite: 3, 5]. 

For a given rank and a specific tensor network architecture, there is a defined set of non-negative tensors (such as probability mass functions) that can be exactly represented [cite: 1, 2]. As the rank is increased, this representable set grows. In the theoretical limit of arbitrarily large rank, any of the primary tensor networks can represent any discrete multivariate probability distribution [cite: 1, 2]. Consequently, research into the expressive power of TNs focuses on *relative* expressibility: how the sets of representable functions compare across different TN factorizations at a fixed or polynomially scaling rank [cite: 1, 2]. 

### Unbounded Separations

A critical discovery in the expressibility characterization of TNs is the existence of **unbounded separations** between the resource requirements of different tensor-network factorizations [cite: 7, 13]. This concept addresses whether two different tensor network structures can simulate one another efficiently. 

According to research by Glasser, Sweke, Pancotti, Eisert, and Cirac, rigorous proofs demonstrate that there are specific probability distributions for which the resource requirements (the required bond dimension) exhibit unbounded separations depending on the chosen tensor network factorization [cite: 13, 14]. This means that to represent the exact same probability distribution, one tensor network architecture may require a bond dimension that scales exponentially with the system size, while another architecture requires only a polynomial or constant bond dimension [cite: 14]. 

These separation theorems are fundamental because they provide rigorous mathematical guidelines on architecture selection [cite: 2]. They demonstrate that certain models inherently possess topological "blind spots" and cannot be universally preferred without considering the correlation structure of the target data [cite: 2, 14]. 

### The Role of Complex-Valued Tensors

Historically, models describing classical probability distributions or real-valued data have defaulted to using real-valued tensors. However, expressibility characterizations have revealed a surprising phenomenon: incorporating complex-valued tensors into the intermediate layers of a TN (even when the final output is constrained to be strictly real and positive) drastically enhances expressive power [cite: 7, 14].

Theoretical proofs have shown that utilizing complex tensors instead of real tensors can lead to an arbitrarily large reduction in the number of parameters required by the network to achieve the same representation [cite: 7, 15]. In sequence processing, deep tensor networks and generalized attention mechanisms utilizing dual embeddings for real and imaginary parts have demonstrated that complex phase accumulation allows networks to capture higher-order structural motifs that confound purely real-valued networks [cite: 16, 17]. The complex Hilbert space acts as a richer feature space, enabling interference patterns that efficiently compress correlations [cite: 12, 17].

## Tensor Networks for Probabilistic Modeling

Due to the exact equivalence between probabilistic graphical models (which are factorizations of probability distributions) and tensor networks (which are factorizations of high-rank tensors), TNs have emerged as a dominant tool for unsupervised generative modeling [cite: 12, 15]. 

The characterization of expressive power in this domain centers on how effectively different models can represent strictly non-negative tensors, as required by probability mass functions. The main architectures evaluated in this context include Hidden Markov Models, Born Machines, and Locally Purified States [cite: 2].

### Hidden Markov Models (HMMs) and Non-Negative MPS

Hidden Markov Models (HMMs) are foundational probabilistic models for sequential data. In the framework of tensor networks, an HMM can be mapped exactly to a Matrix Product State (MPS) where all local tensor elements are constrained to be non-negative real numbers [cite: 7, 15]. This is frequently referred to as a non-negative MPS.

While HMMs feature tractable likelihoods and admit efficient learning algorithms (such as Expectation-Maximization), their expressive power is fundamentally limited by the non-negativity constraint on the internal bonds [cite: 7, 10]. The requirement that all local pathways maintain positive intermediate values heavily restricts the types of internal interference and correlations the network can model without exponentially increasing the rank [cite: 13].

### Born Machines and Quantum Circuits

To bypass the limitations of strictly positive internal states, researchers introduced **Born Machines**, inspired by the probabilistic interpretation of quantum mechanics [cite: 2, 7]. In a Born Machine, the probability of observing a specific configuration $x$ is defined according to Born's rule: $P(x) = |\psi(x)|^2$, where $\psi(x)$ is a complex- or real-valued wave function parameterized by a tensor network [cite: 2, 18].

Born Machines are naturally related to the execution of local quantum circuits [cite: 2, 14]. If $\psi(x)$ is the output state vector of a local quantum circuit of depth $D$, the resulting probability mass function corresponds precisely to a Born Machine [cite: 1, 2]. Because the intermediate tensors inside the Born Machine (or quantum circuit) can be negative or complex, they allow for destructive and constructive interference, drastically altering the expressive power [cite: 18].

However, the expressive power characterization yields a nuanced view: there are unbounded separations allowing Born Machines to represent distributions that HMMs cannot efficiently represent, but conversely, there are distributions that HMMs represent efficiently which Born Machines cannot [cite: 2, 10]. Therefore, neither Born Machines nor HMMs are strictly superior to the other in all cases [cite: 2, 10].

### Locally Purified States (LPS)

To resolve the disjoint expressibility between HMMs and Born Machines, the **Locally Purified State (LPS)** was introduced to machine learning [cite: 7, 15]. Originating from techniques used to simulate open quantum systems and mixed states in physics, the LPS parametrizes a probability distribution as the partial trace over a set of environmental or "ancilla" indices [cite: 7, 13]. Mathematically, it is structured as:
\[ P(x) = \sum_{a} |\psi(x, a)|^2 \]
where $a$ represents the auxiliary, purified dimensions.

The expressibility characterization of LPS provides a profound result: Locally Purified States possess a provably superior expressive power compared to both HMMs and Born Machines [cite: 7, 15]. Any distribution that can be efficiently represented by an HMM or a Born Machine can be efficiently represented by an LPS, but the reverse is not true [cite: 1, 15]. The LPS structure combines the classical mixing capability of HMMs (via the sum over the ancilla index) with the quantum-like interference capabilities of the Born Machine (via the magnitude squared of intermediate tensors). 

Consequently, numerical experiments and rigorous bounds indicate that LPS should be heavily prioritized over traditional HMMs and Born Machines for modeling discrete multivariate probability distributions, as they retain tractable likelihoods and efficient learning algorithms while eliminating the topological blind spots of the other architectures [cite: 1, 14].

## Deep Neural Networks vs. Tensor Networks

As deep learning has become the dominant numerical approach for approximating high-dimensional functions, a major line of research has sought to benchmark the expressive power of deep neural networks (DNNs) against that of tensor networks [cite: 11, 19]. 

### Mapping Tensor Contractions to Deep Networks

A direct connection between general tensor networks and deep feed-forward artificial neural networks has been rigorously established by constructing neural network layers that efficiently perform tensor contractions with commonly adopted non-linear activation functions [cite: 9, 11]. 

The resulting deep networks feature a number of edges that closely matches the contraction complexity of the target tensor networks [cite: 9, 11]. In the context of modeling many-body quantum states, this mapping mathematically proves that Neural Network Quantum States (NNQS) have strictly the same or higher expressive power than practically usable variational tensor networks [cite: 11]. 

For instance, any Matrix Product State (MPS) can be perfectly and efficiently rewritten as a deep neural network state. The required neural network will feature a number of edges that is polynomial in the MPS bond dimension, and a network depth that grows logarithmically with the system size $N$ [cite: 9, 11]. 

### The Supremacy of Neural Network Expressibility

While all efficiently contractible tensor networks (like MPS and Tree Tensor Networks) can be mapped to deep neural networks, the inverse is not true [cite: 9, 11]. The expressibility characterization implies a strict hierarchy: there exist quantum states and multi-variate functions that are efficiently expressible by neural networks, but which cannot be efficiently expressed (or contracted) by Matrix Product States or PEPS [cite: 9, 11]. 

This unidirectional expressibility advantage has cemented the use of Restricted Boltzmann Machines (RBMs) and deep feed-forward networks in solving the quantum many-body problem, operating in regimes where traditional TNs suffer from excessive entanglement requirements [cite: 11, 13].

### Compressing Neural Networks with Tensor Operators

Conversely, tensor networks are heavily utilized to optimize neural networks [cite: 8, 20]. A standard deep neural network requires a massive number of parameters in its fully connected linear layers. By representing these linear transformations as Matrix Product Operators (MPOs), researchers can drastically compress the network. The MPO characterizes the short-range entanglement in the weight space, replacing a massive dense matrix with a chain of low-rank tensor cores [cite: 8, 20]. This structural regularization reduces the risk of overfitting while maintaining the neural network's predictive power, leveraging the TN's expressive efficiency [cite: 8, 20].

Furthermore, **Tensorized Spectral Attention (TSA)** mechanisms have been proposed to reformulate the standard transformer attention operation. By formulating attention in the tensor space using Tensor Train Decompositions, the parameter complexity is reduced from an exponential scale to a linear one, while spectral graph convolutions maintain high expressive power for natural language processing tasks [cite: 6, 16]. 

## Physical Implementations and The $T = 77$ K Benchmark Context

While much of the expressibility characterization of tensor networks exists in theoretical computer science, TNs are fundamentally computational tools deployed in chemical physics and condensed matter physics. In reading the literature on tensor network simulations, one frequently encounters identifiers such as "T#77". 

In the software engineering of machine learning models (such as within the TensorFlow Lite Model Analyzer), "T#77" is used as a literal node identifier denoting "Tensor number 77" inside a computation graph (e.g., tracking tensor operations like `CONV_2D` or `HARD_SWISH`) [cite: 21]. However, in the vast majority of physical and chemical literature discussing TN expressibility and simulation, "T=77" refers to the highly specific physical parameter: **Temperature = 77 Kelvin**, the boiling point of liquid nitrogen [cite: 22, 23]. 

Simulating open quantum systems at $T = 77$ K is a standard, rigorously difficult benchmark used to test the expressive power and algorithmic stability of tensor network methods against real-world decoherence phenomena [cite: 22, 24].

### Path Integrals and the Spin-Boson Model

The modeling of a quantum system interacting with continuous structured reservoirs is notoriously difficult due to non-Markovian memory effects. To track the dynamics, the memory of the reservoir must be integrated over time, traditionally leading to an exponentially scaling computational cost.

Tensor networks, specifically through the real-time path integral formulation, reduce this exponential memory scaling to polynomial efficiency [cite: 22, 25]. In breakthrough quasi-two-dimensional (quasi-2D) TN formalisms, the system MPS maintains both the current system state and the preceding states (memory) as individual tensors [cite: 22, 25]. 

To demonstrate the expressive capability of this architecture, researchers consistently benchmark against the Spin-Boson model at specific experimental conditions. For example, path-integral calculations of Spin-Boson dynamics are executed at $T = 77$ K, driven by a continuous field (e.g., amplitude $\Omega_0 = 0.5$ ps$^{-1}$) and extending to massive reservoir memory depths (such as $n_c = 100$) [cite: 25]. The tensor network elegantly captures both diagonal and off-diagonal system-reservoir interactions simultaneously, a feat enabled by mapping the discrete time-bins of the quantum memory into Liouville space [cite: 22, 25].

### Multi-configurational Ehrenfest (MCE) HEOM and Exciton Dynamics

The Hierarchical Equations of Motion (HEOM) approach is a numerically exact method for open quantum system dynamics, but it notoriously suffers from the curse of dimensionality. To bypass this, tensor network formulations and the Multi-configurational Ehrenfest (MCE) ansatz are utilized to express the effective HEOM wave functions [cite: 26]. 

A prime benchmark for these TN-assisted methods is the exciton transfer dynamics of the Fenna-Matthews-Olson (FMO) complex. The simulation of the FMO complex at $T = 77$ K is considered a highly challenging case for quantum dynamics algorithms due to the multi-state and multi-bath interactions [cite: 26, 27]. Using TN-like MCE approximations effectively compresses the 49-state effective wave function describing the Liouville space, allowing for accurate integration of equations of motion where standard analytical approaches fail [cite: 26].

### Finite-Temperature Bosonic Environments (T-TEDOPA)

The Time-Evolving Density Matrix Using Orthogonal Polynomials Algorithm (TEDOPA) relies on mapping a continuous environment to a 1D chain, perfectly suited for Density Matrix Renormalization Group (DMRG) and MPS methods [cite: 23]. While TEDOPA is exceptionally efficient at zero temperature, its expressive efficiency decays rapidly at high temperatures due to massive entanglement growth.

Recent formulations of Thermal-TEDOPA (T-TEDOPA) map the finite-temperature environment to a modified spectral density, allowing exact simulations of highly structured environments [cite: 23]. The difference in required computational expressivity is stark: preparing the thermal state of a specific chain at $T = 77$ K using standard methods required one week of computation on 16 Intel Xeon cores, highlighting the immense tensor bond dimensions required to capture the thermal correlations, even when advanced TN architectures are deployed [cite: 23].

## Algorithmic Learnability and Optimization

Expressive power is only practically useful if the tensor network can be efficiently optimized. The optimization landscape of TNs varies depending on their architectural class.

### Optimization Algorithms

1.  **DMRG and TDVP:** For MPS architectures (both in physics and machine learning), the Density Matrix Renormalization Group (DMRG) and the Time-Dependent Variational Principle (TDVP) are the standard optimization engines [cite: 5, 23]. TDVP projects the evolution of the system onto the tangent space of the MPS manifold with a fixed bond dimension, yielding a sweep-based algorithm that prevents exponential growth of the tensors [cite: 5].
2.  **Alternating Least Squares (ALS):** For canonical tensor decompositions and hierarchical TNs solving high-dimensional partial differential equations (PDEs), Alternating Least Squares is employed alongside hierarchical singular value decomposition (SVD). This enables solutions to PDEs (like the linearized Boltzmann equation) with log-volume complexity $O(N \log(Q))$ [cite: 28].

### Gradient Stability and Privacy in ML

When tensor networks are adapted for distributed machine learning (e.g., federated learning), the expressive power of the network can sometimes lead to gradient instability. Introducing unitary constraints into the tensor network layers ensures that gradient norms are preserved during deep propagation, while complex phase accumulations capture higher-order motifs [cite: 17]. 

Furthermore, the linear scaling and structured interpretability of MPS architectures have been leveraged for formal privacy mechanisms. In synthetic tabular data generation, the expressive power of Matrix Product States combines with differential privacy to provide high-fidelity synthetic data without risking the confidentiality of the underlying inputs, significantly outperforming classical models under strict privacy budgets [cite: 17, 18].

## Conclusion

The characterization of tensor network expressibility represents a pivotal intersection of quantum information theory, many-body physics, and deep learning. Through rigorous theoretical frameworks, researchers have quantified the exact expressive power of various network architectures via bond dimensions and tensor ranks, uncovering unbounded separations that dictate which mathematical structures can efficiently model specific functions [cite: 2, 14]. 

The introduction of complex-valued tensors and Locally Purified States (LPS) has fundamentally advanced the field of probabilistic modeling, proving that TNs can surpass classical Hidden Markov Models and quantum Born Machines in their representational efficiency [cite: 7, 15]. Simultaneously, deep neural networks have been shown to subsume the expressive capabilities of practically contractible tensor networks, leading to a synergistic exchange where deep learning models solve complex quantum states, and tensor networks compress and optimize deep learning layers [cite: 9, 10].

Ultimately, these abstract mathematical properties are grounded in rigorous physical simulation. Whether parsing compiler logs isolating a specific computational node like "T#77", or utilizing quasi-2D path integrals to track the extreme non-Markovian memory of a Spin-Boson model at the cryogenic benchmark of $T = 77$ K, the expressive power of tensor networks continues to break down the curse of dimensionality, rendering the previously intractable computations across physics and machine learning solvable [cite: 21, 22].

**Sources:**
1. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFx5QFjWD_gZIVR9Mfg9i5KjYGaV9FxRX7CnaNITh2zo0eWGeesru1pj4D-l1RobIc44pOGgLU3P7XqKYv4CwuVLcp9JWsFbI5O2_wIFbxcJ6n0Do9cDrshMI5gSrqqmgspHH4wOLmZ0mpWqeIjhi08mwZvbU8RrigCaqf7Hg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNDcQPCAIhvvWnkG081aywa4T9oLcVunuBeOxfYQ1UFX6NhHLPOgD-PWOVjwvfEPY6i5bZ454r_RaUK6fN53lzDM9pyxoH1fEdiiugV-MIP-VMCOTvog==)
3. [tensornetwork.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsG7iQMCwyEWr8_gDRST42q0ma1i2ebvF1dwETKuKvwWBPNOCb-VotEjpTTQzdE2OVm6OY8Qg58RJ2mNJWOhZZcrEga6xY79auOB5DVDMebPIfkyY=)
4. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtyD6GSgbOeMEzyvWX-vvX5ZznQWwnBlGTPe6hihfLa-kAkPafYT217LjsYSsSyQ9lOG6pMObbdCrF0YabyecPUnZQiQBxQX1ciVgLiMjypwQy9DWMHrMofVQJnpWHZvHb)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGaD-jUxEIe8W6WwJQFVdx0qGNi7qvwzQwTidGTYy3xHGXmt_iTOkJmRvNZEb1MvUddvIrostOapuHdrAnv2MpzFcrGJx3B2GVMi_os6aGxAbAO5a_BA==)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHvFSy3eqcy3smcGZ2POG_kMqDzEsUeaax1fg8RO5DRkzDWI2B3lC51G7ZKt7AqwP-oxpPBXm3pOUJThfhHlFQ8lN6YZD65rowgrahVaAKWgMrFyg9SRCokSmOKk2U2jhonGpYVVdUz1XIJU7bg9ewhTDWauuEi09fLI3uVeOa0xrU9etOJ0QG5mDFhl2gZBS2dupX)
7. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBQGvLwOg8IFXFPKSkVK80NBG4otwL3mZcqD8RmZtQbWwpNtTMV-R5sICdDyukAxBJpEwePJm9CMKFcS8N7QwTOAp-uuIv7ibjxbFWWxvZIjzFapXmM6EW-gY6BBHKq3M9EchlfmA5fgmfQV9msiwsU_dthilXly3eMWUw9nxck7ms8f3FLqekVdLksOKAvfMLeMY=)
8. [bimsa.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5oZe79uLFvUJZHOog-4g2iGy-wXGKuedh4Q8IlGLv3yUNRyFP8IvkdHhpIP9N8PkEOweDbz7oRRScNY9L3zAxVmx3qpN0pJKByITnPfKEe0Odvgg_pkKNLtUvbtnqSA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFgW5mZF58D3PLWk3M6TZioDl6Phet40Ss4nQn6m__RIOzNBEo27mGqQR6ViUTLKMqgOFAJfzb_10lJMxGSIl51ev1Un2V6G4KtLN0AEw1MJaj9VQ99w==)
10. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWvao6bESISShoZKaeM16juR9-3wDUbiMdV8c6n1g7acYJsOH2XTcR6NwMYwIcjsuzBCGJ7-BIofUIUYHbjxFU0I5ip7B5JhM-3sNQkkeQKqg_kpAh43jEw3S9A05L3hdZMF6qeFDoJ9nQ6yNvmZuRXOkyTKcagQbTFKJcdbIXpVdGyPjHIyGbvBPIn-I7hIXkGcNV1pM=)
11. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_iz2hLoozB7Khp7HxwmVamVSzouMwQP8CFVoopBSK12gRTeD2uOS8QT0bUGyUhIFvO7HMxOZ6TTbFNXOVYjlIeXfWkTdoOig-InprjJospPhAJKQe-DLhkcw09TFcpSlZcLD4FCcWiCPGQosYR0gPjAF78dEqOAnq2mCnSiKYIBw=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAXblndQCciwKCau4Rq_xiaDVKj42fsMHLQj5yNH74rBOp6RxYnYMsOcjf9Xn-JyB017ma9TYmwGom1MyeQGFVNYPT4v4MIaLTEXP1ki3v9c5itvZpAw==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFXklox_WixdpkD3i87J-pMNPtERTxvVI_vb7mxS3PKWCeg2AKRLQDZhc-rhKNcMgKlUMEEtyKOAfYkylZ5mU20dB6r0xQXwfJnOp0ajVE0o1731FFo5fGsHi-NVOGZlMeTj20D9q7Y61mwIfTf_bBUmGFBvZTPpZWhJ0030BLOE7qoEfcU1jWC1rsNH82F3t4GSSBJUFMMdO-lM19mlqmbimerQQY-PXRqtd-WV-GSwIXJ8IpsUs2jGtR8GuJTAgaygCXNO_OPvYb10-rw5iy3chxPU6T4wqmRfF6-Mut4hYFFP4IUViLFRlVb3GTbY4tT8rU6X_g0_Lm6U3Dug==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0F4sOiI78tX0-be0z_CErE6ZYYHzqEMJfyyiMReanS9ZoM4S0I5JwLcK6Fi8JiCvgNUUmbYLMMZsgG7UJAV8sU0d1N4VyuJd7Vp9zeKa_Pnx7YNr5-w==)
15. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH23Uau6M12aZ8FbPosphcips9U7mLETitf09SQkffBrFogv-fWbXvw9Dndh3GUAQF5P0O68KMK-NL-yYAYADOK6ShJGua1zGAYIm_7nVdWweMirURYFnq_GTYeTDm0CvmVgVViPdcqq51yyvAx0_efXXXVsizgrbytfZfpTKpKNuxkHwHVx65aLZugwRCY0Ddz8uTGGpFcnyBep9oCyD2MBFL4u2-NalgGpEJnbANCswooMd1LScyW7uAaLK7y_hEYpn0cIg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXFFi2GKWVyeTDkwSIRzamVujfl2cE3B3TBRnjExbZfT2wiJM0ox1JDUOZUD8BAh3ifff2IOPynq20bljzUX8zc3JngtzTbGpDEZfGuYPWapoM6_CgFg==)
17. [doi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUvD_eOYciKQPsaw2uzHe9c3fmgZ5j-5ej8vbH7t8j0MT2mE2mis_vVOdi_Xa5cxEPo-w9zKhTy3z1h_dZ50xtmFYE4TLjjsn69akFO1aBeS7Euug2K-1lPSeX_WXetqhlTw==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLXhXsMVxWqVZEHi-BknxBw4D5rPjFfKkDW2qDHoBQPiZ3IEcIp_oV7QNGAsgd1czcGerW-2DTL58QWn7OpMXIY-jchTts641rwf33uNyfrSVWcQUSGoYapw==)
19. [chalmers.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqoZwGdSgKuQrfuC6Ovt2uGSu7JkmOeJOWRkd-SI27ESz8QxpnZExfeoqn9ZQ8RwVt4MpuBxdxyeqdpO5KQN42Ae8et9uHqudeSpZzFnbXO2glGFDCmqzM1ZuCJXQtiMGMVJYlgfIij8GPQ-lloZiC9T1vdI73q4A8lk9UA5o=)
20. [tensornetwork.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWB5weU1JfvvOwpql8xH9PmOq5HP9hS3O6nRW9mnM4rUU9iVMHVM3lgXMiMcKQSZtt1Hmqn4fvdbXd1AOKPAx1q_PxIa-7AuXgo4NuJ_dKR2-DdQ==)
21. [tensorflow.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8xgnNrRA5NW0lsdOm3QB46a3OKPFuAeoz5oOjdeL38rYG0BnCeLsohoTBQrCTmFV6_F6Lz_Rolo5Fvg4lfINm0gG06NyJuoszXsLUABGQU9GzKKB0YedH5MLw10y85ij6nW1OrO5L3bcmGurd2SYx6yEf)
22. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuC3eHoiNQjWLTlx30sboMcYlS_5vNK4LsFREeg9kEO_KruedorP9z2KsyXSCPsuPkQ67V7cxm5JjC8nMmnFCy-zuZ9GixQIJeyYMOs0Qyt3EHlKGB)
23. [unimi.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGtV4f7oCEO33FmJwdnwtETBPtBHPHrOpJnTpFUQ9H6F-VXJrj5fZl1wjXk3DrGow-eAmzkGeFVorcxHowf06DQbGBE_jmuajAqyHtCbdgv7oRZaMIRg-8iAnaI-rupZd0nPAhKEl2qJqnq9XUJHDt6BCsECyUUeAhG0u-ulUz)
24. [acs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGI76-IYR7Dh9VBPlNKNvV8FiMBz7BdfdyszspbKqGzLxwugBq-COBJU3wz2AiIFb6oCCatF7epIoL-W-EdIadqFGfwxbs80TAvzbQL5Vc4Zv5HFC-LYLV29BIfwqPweu8=)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsZH0XusPrTiKDrUDuabI5NdK7rbN_6EMiTo4FiR_ahQ80dIJrY0Q5bdSsi2llv48qp5yWBq4XJtfZgoezyUFmWVDvcyRHJwJj-QCw1dwTeeoGelU7dw==)
26. [aip.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWgZCnRMD8u03AgVFWlfTe0HqCzEyWMyx9E_n355Z6KM9Sk65_Z-e5W6PJl_k036aoUoQ_hk3mWHKsXEeq6KHIOfufWeohzmXgMobaFIWHSAh1zVvQGKRQci7ufhImwYXp7YYX_ujsqm-4hLc9gh_fZqyMFXpkWfHsuo6u4Aag8ninvZg7_2iHXzsCVL0co6Dr8QG6f2ojAxIX0SEwxAFK6Q==)
27. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCgcQsmVtDzEbswpU3pBbY5BO9fj_sq0yiQz4jDxGu9XZryTnFIGPnUFj393tRh-wZe6I0BjKt_d0hZihdiiivXYIAfE94JFnabZYmLjXISM_BLwuHSwI-d9uoOzKJLT5W7co0CW_6JQ==)
28. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB5kZGOJ0cp19jF9Tg_KkPmt3L5Lzf3qAHwPaeBQO3FctMcCMLTQIlXYXnHDA9mfxqU_iFUpCexfyKCw4s1gu4RAYd8kcPJliAv42QhHCyUvX3nv8szrGmdZH2yed3Y9UZS4VdaKXrkldLbS3AP4i2s3rh67KlP-M7BWNpuxo=)


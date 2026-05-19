# TENS-03: Tensor network expressivity classes

**Pythia queue id:** 40
**Tier:** T1
**Priority:** 1
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdwQ3dNYW8tekp1T1FfdU1QMm9QQTJROBIXcEN3TWFvLXpKdU9RX3VNUDJvUEEyUTg
**Elapsed:** 309s
**Completed at:** 2026-05-19T09:31:06.222607+00:00

---

# Theoretical Characterization of Quantum States and Functions Captured by MPS, PEPS, and MERA at Fixed Bond Dimension: 2025 Perspectives on Expressivity Gaps and Approximation Hardness

### Key Points
*   Research suggests that Matrix Product States (MPS) and Projected Entangled Pair States (PEPS) flawlessly characterize 1D and 2D area-law entangled states at fixed bond dimensions, but they encounter severe representational bottlenecks when confronting volume-law entanglement.
*   Recent 2025 frameworks, particularly Holographic Isometric Tensor Network States (holographic isoTNS), provide compelling evidence that adding a dimensional axis to the tensor network allows for the capture of volume-law entanglement at a fixed bond dimension, effectively bridging a long-standing expressivity gap.
*   The Multiscale Entanglement Renormalization Ansatz (MERA) continues to be the dominant architectural choice for capturing critical systems with logarithmic entanglement corrections; 2025 studies imply it possesses superior expressivity scaling compared to MPS for arbitrary quantum circuit simulations.
*   In the realm of functional approximation and machine learning, 2025 complexity-theoretic proofs reveal that computing exact interaction values (like SHAP) for Tensor Trains (the mathematical equivalent of MPS) lies in the highly tractable parallel complexity class **NC**, highlighting a sharp divergence in approximation hardness between 1D architectures and deeper, unconstrained models.
*   It appears that approximation hardness in quantum optimization is heavily influenced by entropic barriers, while 2025 analyses of Instantaneous Quantum Polynomial (IQP) circuits demonstrate that classical simulation becomes intractable even at logarithmic depths due to rapid anticoncentration.

### Executive Overview
The simulation and theoretical characterization of quantum many-body systems and complex functional spaces depend critically on the choice of mathematical ansatz. Tensor networks—primarily MPS, PEPS, and MERA—serve as the standard lexicon for describing the low-energy corners of the exponentially large Hilbert space. A core limitation governing these architectures is the **fixed bond dimension**, which places a strict mathematical ceiling on the amount of entanglement or correlation the network can encode. While classical results bounded these capacities to area laws, cutting-edge research in 2025 has introduced novel geometries and isometric constraints that fundamentally alter our understanding of what these networks can express.

### The Expressivity-Tractability Trade-off
Expressivity in tensor networks is continuously weighed against the computational hardness of tensor contraction. A highly expressive network that captures intricate, long-range correlations often demands contraction algorithms that scale exponentially or fall into intractable complexity classes (e.g., #P-hard). The most significant contemporary advancements focus on locating "sweet spots"—classes of states or functions that retain high expressivity (capturing volume-law entanglement or complex functional mappings) while remaining efficiently contractible. 

### Bridging Quantum Physics and Machine Learning
The characterization of functions captured by tensor networks extends beyond quantum wavefunctions into classical data distributions and machine learning interpretability. Tensor networks parameterize hypothesis classes with measurable polynomial capacities. The theoretical overlaps between quantum state expressivity and machine learning model expressivity (the "expressivity gap") have become a primary locus of 2025 research, particularly in defining structural boundaries where exact calculations transition from tractable to fundamentally hard.

---

## 1. Introduction and Mathematical Foundations

The characterization of quantum many-body states necessitates overcoming the "curse of dimensionality," where the Hilbert space dimension grows exponentially with the number of constituent particles, \( \mathcal{H} \cong \mathbb{C}^{d^N} \). Tensor networks provide a mathematically rigorous framework for compressing this space by exploiting the physical reality that natural quantum states—particularly the ground states of local, gapped Hamiltonians—do not occupy the full Hilbert space uniformly. Instead, they reside in a highly constrained manifold characterized by restricted entanglement scaling [cite: 1, 2].

The defining parameter of any tensor network is its **bond dimension**, typically denoted as \( \chi \) or \( D \). The bond dimension dictates the size of the virtual indices connecting adjacent tensors, serving as an upper bound on the Schmidt rank across any bipartition of the network [cite: 2, 3]. The central theoretical question across tensor network literature is: *What precise classes of quantum states and mathematical functions can be represented faithfully when \( \chi \) is fixed to a finite constant as the system size \( N \to \infty \)?*

### 1.1 Entanglement Entropy and Area Laws
The capacity of a tensor network to capture a quantum state at a fixed bond dimension is intrinsically tied to the state's von Neumann entanglement entropy, \( S(\rho_A) = -\operatorname{Tr}(\rho_A \log \rho_A) \). 
*   **Area Law:** For a subsystem \( A \) of size \( L \), the entanglement entropy scales proportionally with the boundary area of the subsystem, \( S \propto L^{D-1} \). Tensor networks are purpose-built to naturally satisfy this scaling.
*   **Logarithmic Corrections:** Critical systems governed by conformal field theories (CFTs) exhibit a mild violation of the area law, scaling as \( S \approx \frac{c}{3} \log L \) in one dimension (where \( c \) is the central charge) [cite: 3, 4].
*   **Volume Law:** Highly excited states, thermal states, and random states generated by deep quantum circuits exhibit volume-law scaling, \( S \propto L^D \), which traditionally necessitates an exponentially growing bond dimension in standard tensor networks [cite: 5].

### 1.2 The Concept of Size Consistency
A vital structural criterion for the expressiveness of a tensor network is **size consistency** [cite: 6]. For two non-interacting subsystems \( A \) and \( B \), an ansatz is size-consistent if the minimal energy of the joint system \( A \oplus B \) within the variational family at a fixed bond dimension equals the sum of the individual minimal energies: \( E_{A \oplus B} = E_A + E_B \). This implies that the product state \( |\Psi_A\rangle \otimes |\Psi_B\rangle \) is exactly representable without increasing the bond dimension. Standard 1D MPS and 2D PEPS are size-consistent, whereas artificial mappings of 2D systems onto 1D "snake" MPS are not, leading to a catastrophic loss of extensivity and exponential bond-dimension scaling [cite: 6].

---

## 2. Matrix Product States (MPS) and Tensor Trains (TT)

Matrix Product States (MPS) are the foundational architecture of tensor network theory, mapping one-dimensional quantum systems with unparalleled efficiency. In the applied mathematics and machine learning communities, the identical mathematical structure is known as the **Tensor Train (TT)** decomposition [cite: 7, 8].

### 2.1 Theoretical Characterization at Fixed Bond Dimension
An MPS factorizes an exponentially large state tensor into a linear chain of rank-3 tensors:
\[ |\Psi\rangle = \sum_{i_1, \dots, i_N} \operatorname{Tr}(A^{[cite: 9]i_1} A^{[cite: 10]i_2} \dots A^{[N]i_N}) |i_1, \dots, i_N\rangle \]
where each \( A^{[n]i_n} \) is a \( \chi_{n-1} \times \chi_n \) matrix, and the physical index \( i_n \) has dimension \( d \) [cite: 5]. At a strictly fixed maximal bond dimension \( \chi \), the number of parameters scales as \( O(N \cdot d \cdot \chi^2) \), compressing the state space from exponential to linear complexity [cite: 1].

**States Captured by MPS:**
1.  **Gapped 1D Ground States:** By Hastings' rigorous proof of the 1D area law, any ground state of a local, gapped Hamiltonian in one dimension can be approximated by an MPS with an arbitrarily small error \( \epsilon \), requiring a bond dimension that scales polynomially with the system size and \( 1/\epsilon \) [cite: 1].
2.  **Constant Entanglement States:** At a strictly fixed \( \chi \), MPS can only exactly capture states where the entanglement entropy across any bipartition is bounded by \( \log(\chi) \) [cite: 11]. Consequently, correlations in a fixed-bond-dimension MPS decay exponentially with distance.
3.  **Abelian Symmetry Protected Topological (SPT) Phases:** MPS gracefully capture 1D topological phases. Classification theorems demonstrate that 1D gapped phases without symmetry breaking are entirely captured by the cohomology classes of the symmetry group acting on the MPS virtual bonds [cite: 12, 13].

### 2.2 Expressivity and Measurement-Feedback Preparability (2024-2025 Results)
Recent characterizations focus on the dynamic preparability of MPS. A major 2024 study systematically characterized the structure of MPS that can be prepared using constant-depth local circuits followed by a single round of Measurement and Feedback (MF) [cite: 12, 14]. The preparability under MF translates directly to the symmetries of the MPS tensors. The research revealed that MPS preparable via MF exhibit a coexistence of Clifford-like properties and "magic" (non-stabilizer resources). It was rigorously shown that states with Abelian-symmetry-protected topological order form a restricted subclass of MF-preparable states, yielding a structural theorem analogous to Clifford teleportation [cite: 12, 14].

In the context of generative machine learning, 2021-2025 studies comparing MPS (Tensor Trains) to classical Bayesian networks proved a separation in expressive power. Even simple 1D MPS feature substantially more expressive capacity for learning sequential datasets than their classical counterparts, a phenomenon directly linked to quantum nonlocality and contextuality embedded within the tensor structure [cite: 15].

### 2.3 Approximation Hardness and Complexity Class NC (2025 Breakthrough)
A remarkable 2025 breakthrough bridged the quantum-classical divide by analyzing the expressivity gap in machine learning explainability—specifically the calculation of Shapley Additive Explanations (SHAP). SHAP values are notoriously NP-hard to compute for expressive models [cite: 8]. However, researchers in 2025 demonstrated that computing exact SHAP values for functions parameterized as Tensor Trains (MPS) is not only solvable in polynomial time but actually resides in the highly efficient parallel complexity class **NC** [cite: 16, 17]. 

Because operations on TTs with a fixed bond dimension allow for a sequence of parallel scan contractions, the exact inference can be computed in poly-logarithmic time (\( O(\log^2 N) \)) using a polynomial number of processors [cite: 16, 18]. By proving that complex models like Tree Ensembles, Linear RNNs, and specific Binarized Neural Networks (BNNs) can be reduced to TT representations at fixed width, this research closed a massive expressivity gap, establishing that tractability in these functional spaces is heavily dependent on the equivalent tensor network's bond dimension rather than its depth [cite: 8].

---

## 3. Projected Entangled Pair States (PEPS)

Projected Entangled Pair States (PEPS) represent the natural generalization of MPS to two (and higher) dimensions. They embed local tensors on lattice sites, utilizing virtual bonds to capture the complex entanglement structures of higher-dimensional geometries [cite: 3].

### 3.1 Functional Characterization and the Contraction Bottleneck
For a 2D square lattice, a PEPS tensor \( T_v \) possesses one physical index of dimension \( d \) and four virtual indices of dimension \( D \) (or \( \chi \)) [cite: 5]. PEPS intrinsically satisfy the 2D area law, scaling entanglement entropy linearly with the boundary length of a subregion.

**States Captured by PEPS:**
1.  **Topologically Ordered States:** PEPS are uniquely capable of exactly capturing topological order, such as the Toric Code state and string-net liquids, at very small, fixed bond dimensions (e.g., \( D=2 \) for simple anyonic models) [cite: 19].
2.  **Critical 2D Systems:** PEPS can describe systems with algebraic (power-law) decaying correlations, distinguishing them from MPS which are strictly confined to exponential decay at a fixed bond dimension [cite: 4].

However, the expressive power of PEPS comes at a catastrophic computational cost. The exact contraction of a PEPS to compute local observables or normalization is **#P-hard** [cite: 6]. In 2025, it remains established that even approximate contraction algorithms (such as Boundary MPS or Corner Transfer Matrix Renormalization Group) require computation times that scale polynomially with \( D \) but exponentially with the system width, heavily bottlenecking their utility in variational algorithms [cite: 6, 20].

### 3.2 2025 Innovations: Isometric TNS and "Holographic isoTNS"
To circumvent the #P-hard contraction bottleneck, researchers introduced Isometric Tensor Network States (isoTNS), which impose a specific orthogonality condition on the tensors, ensuring that the network can be contracted efficiently—analogous to the canonical form of an MPS [cite: 5, 21]. In standard 2D isoTNS, local expectation values can be computed by contracting only a few tensors (e.g., five tensors for a two-site operator at the orthogonality center) [cite: 5, 21]. 

However, the isometric constraint artificially restricts the expressivity gap. Standard isoTNS form a strict subset of PEPS and cannot capture certain highly entangled manifolds [cite: 5]. 

**The Holographic isoTNS Breakthrough (2025):**
To address the critical limitation of representing **volume-law entanglement** at a fixed bond dimension, researchers in late 2025 proposed the **Holographic isoTNS** [cite: 5, 22]. This architecture simulates a \( D \)-dimensional quantum lattice by embedding it in a \( (D+1) \)-dimensional isometric tensor network. 

1.  **Volume-Law Entanglement:** Unlike standard 1D MPS or 2D PEPS which are restricted to area laws, randomly initialized Holographic isoTNS were proven to display robust volume-law entanglement *at a fixed, modest bond dimension* [cite: 5, 22].
2.  **Expanded Representational Manifold:** Through analytic and variational optimization studies, it was shown that this ansatz can efficiently and faithfully describe highly entangled yet structurally low-complexity states, including arbitrary fermionic Gaussian states, Clifford states, extended rainbow states, and states subjected to short-time local unitary evolution [cite: 5, 22]. 
3.  **Algorithmic Viability:** Because the tensors remain strictly isometric, the ansatz preserves efficient contractibility. Implementing Time-Evolving Block Decimation (TEBD) on holographic isoTNS demonstrated superior energy-density error convergence and remarkably small variational errors compared to conventional MPS when propagating highly entangled dynamics [cite: 5, 22].

Additionally, 2025 research successfully mapped "isoTNS skeletons" to classical probabilistic automata, proving that for certain Abelian string-net phases captured by isoTNS, polynomially many generalized Pauli strings of arbitrary weight could be efficiently sampled classically. This was a surprising revelation regarding approximation hardness, given these states are generically neither Clifford circuits nor matchgate circuits [cite: 23].

---

## 4. Multiscale Entanglement Renormalization Ansatz (MERA)

The Multiscale Entanglement Renormalization Ansatz (MERA) addresses the failure of MPS to capture the logarithmic entanglement entropy scaling found in 1D critical systems (scale-invariant systems) [cite: 3].

### 4.1 Structural Characterization
MERA achieves its expressive power through a hierarchical, tree-like structure augmented with **disentanglers**. Disentanglers are local unitary operators that pre-emptively remove short-range entanglement between neighboring blocks before coarse-graining via isometries. This structural nuance prevents the accumulation of entanglement at higher scales, ensuring that the local truncation space remains computationally tractable [cite: 4, 24].

**Functions and States Captured:**
1.  **Critical CFT Ground States:** MERA exactly replicates the scale invariance of 1D critical points. The bond dimension \( \chi \) in MERA controls the truncation at each scale layer, but because the number of layers scales as \( O(\log N) \), MERA inherently captures logarithmic entanglement entropy scaling \( S \approx \frac{c}{3} \log L \) at a fixed bond dimension [cite: 3, 25].
2.  **Quasi-Long-Range Order:** While PEPS can capture algebraic correlations in 2D, MERA provides a strictly scalable, exact approach to quasi-long-range order in 1D [cite: 4].

### 4.2 2025 Results: Expressivity in Quantum Circuit Simulation
Recent 2025 benchmarking studies extensively analyzed MERA's expressivity against MPS for the classical simulation of quantum advantage circuits [cite: 11, 26]. 
*   In deep, brick-wall quantum circuits where entanglement generation is rapid, MPS simulations suffer a rapid degradation in fidelity unless the bond dimension is scaled exponentially. 
*   Conversely, because MERA natively supports polynomial-to-logarithmic complexity scaling associated with long-range entanglement, protocols based on updating MERA tensors (by maximizing gate fidelity using Riemannian optimization) demonstrated significant expressivity advantages. As qubit counts increase, the complexity and expressivity of MERA-based protocols grow logarithmically compared to the exponential explosion seen in MPS [cite: 11, 26]. 

However, MERA's optimization remains highly demanding; in 1D, optimization scales as \( O(\chi^7) \) or \( O(\chi^9) \), making it computationally steeper than the \( O(\chi^3) \) scaling of MPS [cite: 2]. The trade-off is higher fidelity in the volume-law or critical regimes at heavily restricted fixed bond dimensions.

---

## 5. The Expressivity Gap in 2025: Mutual Information and Hybrid Architectures

The "expressivity gap" refers to the disparity between the theoretical capacity of a quantum model (like a tensor network or a variational quantum circuit) to represent a function and its practical ability to be trained and optimized without succumb to barren plateaus or exponential costs.

### 5.1 Redefining Expressivity Measures (MIBEM)
Traditional metrics for quantum expressivity, such as the Haar expressivity gap or effective dimension, fail to account for the dynamical nature of task-specific structures (e.g., reinforcement learning) [cite: 9]. In 2025, researchers introduced the **Mutual-Information-Based Expressivity Measure (MIBEM)**. Tailored specifically for parameterized quantum circuits and tensor networks, MIBEM captures how effectively an ansatz internalizes reward-relevant structures [cite: 9]. Comparing hardware-efficient circuits with tensor-network topologies, MIBEM revealed that structurally constrained networks (like MPS and Tree Tensor Networks) align much more closely with local task-reward distributions than uniformly deep, unconstrained entangling circuits.

### 5.2 Breaking the Expressivity-Trainability Dilemma: FC-VQC
In classical and quantum machine learning, highly expressive monolithic quantum circuits are plagued by barren plateaus. To solve this, a major 2026-slated framework developed in late 2025, the **Multi-Layer Fully-Connected Variational Quantum Circuit (FC-VQC)**, leverages tensor-network-like modularity [cite: 27, 28].

Rather than utilizing a single monolithic circuit that requires exponential simulation costs (\( O(2^d) \)), the FC-VQC partitions high-dimensional inputs into fixed-size local quantum blocks (analogous to local tensor dimension \( d \) in MPS). These blocks are connected via deterministic, parameter-free block mixing (acting as the virtual bonds) [cite: 27].
*   **Linear Scalability:** By keeping the block size fixed, the architecture scales linearly with the input dimension, precisely mimicking the scaling laws of fixed-bond-dimension tensor networks [cite: 27].
*   **Closing the Gap:** Theoretical analysis in the 2025 literature establishes that without information exchange (bonds), the model is block-separable and inherently lacks expressivity. As the mixing depth increases, the cross-block dependency grows, bridging the expressivity gap. FC-VQC empirically "breaks the classical ceiling," outperforming equivalent deep neural networks on tabular datasets while using 17 times fewer parameters [cite: 28, 29].

---

## 6. Approximation Hardness and Computational Tractability

Understanding which states can be captured by tensor networks fundamentally relies on the hardness of simulating or contracting the underlying graphs. 

### 6.1 Classical Approximation Hardness and Entropic Barriers
Approximation hardness denotes scenarios where classical algorithms struggle to return solutions within a defined fraction of the global optimum. In 2025, the community coalesced around the concept of **entropic barriers** as the primary driver of both classical local-update hardness and quantum annealing failures [cite: 30]. Entropic barriers arise when a search space is littered with vast numbers of highly degenerate, slightly suboptimal local minima. Overcoming these barriers requires an exponential amount of time to find rare fluctuation paths to the true ground state. When problems are mapped onto graphs (such as 3-XORSAT on random regular graphs), both PEPS tensor network algorithms and quantum evolution (SFQO) face superpolynomial runtimes beyond critical dynamical phase transitions [cite: 30, 31]. 

Furthermore, exact hardness results have shown that combinatorial graph problems embedded with specific topological constraints (such as bounded treewidth or chordal bipartite graphs, which naturally map to Tree Tensor Networks) maintain deterministic polynomial-time solutions, provided the constraint \( k \) (analogous to bond dimension) is fixed. However, as the structural complexity approaches a full 2D grid (PEPS), the problem transitions strictly to NP-hard and #P-hard domains [cite: 32].

### 6.2 IQP Circuits and Logarithmic Depth Anticoncentration
A highly significant 2025 development in quantum approximation hardness involves **Instantaneous Quantum Polynomial (IQP)** circuits. IQP circuits are composed exclusively of commuting gates (typically diagonal in the Pauli-Z basis) sandwiched between Hadamard transforms. They are intimately related to tensor networks via graph state mapping [cite: 33].

Recent theoretical proofs demonstrated that **sparse degree-2 IQP circuits** exhibit the **anticoncentration property** at merely *logarithmic depth* [cite: 34]. Anticoncentration means the output probability distribution flattens out, lacking structural peaks that classical approximate sampling algorithms can exploit. 
*   By mapping the second-moment quantities of degree-D IQP circuits to classical statistical mechanics models, researchers proved that sampling from these circuits is classically hard to simulate even at extremely shallow depths [cite: 34].
*   This establishes a firm lower bound on approximation hardness: above a certain shallow, logarithmic threshold, even tensor-network contraction methods fail to exploit any localized entanglement structure in random IQP graphs, rendering classical simulation (and thereby fixed-bond-dimension approximation) utterly intractable [cite: 33, 34].

---

## 7. Conclusions and 2025 Syntheses

The theoretical characterization of quantum states and functions captured by MPS, PEPS, and MERA has evolved dramatically. While the foundational principles defining their fixed bond dimension limits—such as the 1D area law for MPS and the logarithmic critical scaling for MERA—remain inviolable, the introduction of novel structural paradigms has redefined their expressivity gaps.

The 2025 advent of **Holographic isoTNS** [cite: 5, 22] provides the most profound shift, proving that isometric constraints coupled with a supplementary geometric dimension permit the capture of volume-law entangled states without triggering the exponential computational collapse historically associated with such entanglement. Simultaneously, the application of tensor network geometries to functional approximation, specifically the proof that **SHAP computation for Tensor Trains resides in the NC complexity class** [cite: 16, 17], firmly delineates the boundary of approximation hardness in machine learning explainability. 

Finally, insights drawn from MIBEM [cite: 9], IQP circuit anticoncentration [cite: 34], and FC-VQC modularity [cite: 27, 28] underscore a unifying theme in 2025 literature: overcoming approximation hardness and maximizing expressivity at fixed resource constraints relies entirely on harmonizing the architectural topology of the ansatz with the intrinsic correlation structure of the target quantum state or functional distribution.

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa-0F2-Ttll0LTc9q7ZYo-i4AYVhQlyboSG0FGk1e9WDJzVGdK8DwEKeJTiB3brI4LNGMDFYh39QSm_VgRaZzRmqSw5ohl2drI5XLl-aS_luLdHQsrqpvBOsJoDCzID64vYb-uh9nVqKHz0EmwXLhEppk=)
2. [scipost.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzgauCQ3FnKC3rLck7l-2XhfcrfSPDlQ-jk7H9hdzS8Vc8Pi4uuvcEyH8yykQmJ93cREHO64N17ZNU5gqpZMKGiihY8mFotjzt62dXa-LGvDKVOMUJkJ2oh_QQL0aq5jRaJqCO_guUWy3ITQ==)
3. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_FY4gJiM9313ioX1TBDSR1CeBIuqHhPaJ5_u5H_BtvYj4RN6RWKLX63oS2OHQi1p0gVZhrlGuPkZ1f8Pld7PPI_9H_x0YowdhtFlxqXS63X54hQaucdBWsnUlw4V53WA=)
4. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpJI9L6Z_S1C_zsoUQ7ByYAL5zym8h2spJ8hLPa0OmoT2hT1CyWPQexSKGXpiRFMmiNi9hHbkE1Z06HdHm-89jvthBd8WJSKuzgB8fF1CTqrz19wOA-7apKTxYDNR74LYFt47YqHlbBw0fMCDMPFkVvxjiYJXCUt9H8t_88A4hMMy-T4GRcN89I7cV1vHvFbA=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoyyiqFckVShXJOuiZ1LRNm3e-nat-rv4so6f8N4koPve8xs1bhBoDi99twwAxSp-51iy1vTQcAgiQ8VXKFtx-dgbXpBpNGTVeQMcJIlcIs6Ya1YZmK1_oEg==)
6. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz4ctt5rCVq9hcRNHQ3xM0zx7Lu9k4aWUfU8evhWoIBdgIEVYvq7Bomycs-_-pta16JmsJvT83jcUAaMhDGlQBL1pyOssNMKUY3Ts9Z5MfzFxuLUAJMvrP4niVnV2PGMS79mWcCGFoH8lplqw0H93Z)
7. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjUvkg8hqhed05V8DUVecc8usQMJDj-bEE3HOwS5oX96ZaGlrEvXfsINnrqxUz_DzQDV60lLQWd3FJ2vW0ZcnorDUeiJ_G-7m1T24qv3i6CpYCcDhINepzxQudviPAgb8vxIsbhzpXS44=)
8. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwlzkoIe6ngpbxc7GEWqfzlQQTirtD1cWAPyRH-j4qCtY8_rZHMVC933-Pw9AAxQpmMIxNhZu7PA-oRdjq023Tk41t-OlTU4VFLneSfKg-Hqu1CKICZQ1qTqaFnok7xvt1yU4=)
9. [qsimconference.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWzXrDxAxz4A-oIsEmRNHTDNjHJ7kWmlvu3m6Yg5D7Pf31szahU-Mtty6FZvIEDQqpJIIzpLTizKgo3AFenze-VmNrrco695HCqN8e6Gd3eQjJWVXEAoDNb3gg_q4Sg1CL0bKYgDlXOhhr)
10. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJANfpL1r384rPHF0O3IJ3EmyA2-LWbzkLp0bJ9D87-gVGYgGgkF9Pcgiq5SCj0tDVLBqsWVQAtzLAZ51YFk0tqxNIrfllYiCnn-yJUz9Ym88pktNpqfdBmHMsZsQ4tA==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGu6Tfgb1nZYHmAV0UpxdQIMX8V5lXb4RrAYIWQLzq9Gug-YV3EPbmlrtH93uAcBfMPRvM3hTfRRuaNs9IVDUucEAaK0WLKqMYDNxvyMKFehy1CO2e1aiStZQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESZobK3vZdfegVyF94AUK-mMTDbCVGdrpBwcf-JrsNZ7S3zQoabjoi7s_uNsQD617t9gM7UFDZQzmuGCzrlSH2J_TpZNB2JPlSBFGmJOc0SmkfesGViA==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGW78iVUyGtT8L7ZN2sYqeM8EN-OU8bKkwcCcdyZEDRdoPGP1Ky35OSUcvdfP8Gzz8UxERPpKxPblI0vbuxQlHpkdEbS9nIQ_iVlZbT-G1MfdmjhUk8)
14. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIyvVSYg_f6gY1OTGCcRZmSDqlAeqq5WycbcG5QqLcpMP8Lm5f8CH2b_p6q52iImmOu3zOgJHOW1JAAzHZqMV0ZWkE_euig1DTm29y-smvb_sSfPGLHTnvJuuzRRr7N_bG979Y4MZmflWltdehgGudeYSMASnPf01faKCdzdlj7ku-)
15. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOvVtzXVkZiqd3sl6F0LHCXvnmdR5usRBs8Jgg49aIvHhfx0AQqgsynFcrQGlzyjDvnZTgAdJazVCzMTg9bz8L4nZJ8s-WxDktRjEIc3vDwPQxxP_uT8fZYZLGbBDZusaFtCJeOu-KrB92fDz3k6YS4lxrY_Yw5wYd69nCOE-coq1F)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfCCpsR7wTlmhgVskihNgjKBWxRku2CO6c1jOhCF2H4NjTAgHafVdeIPCWGFwFn-kxaks3zGnGpm2FNaS0___EnEoIzp1ZbZ2mc6yc8cs_ZGRIxMBOTA==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCEYEW9FomOeA4xhJiuqpKIBmEQLdYi3eUAlhBikrJKl0KXyXzpm_mq8NTuzdgoLspgBMd7d01tcFp3omMXhrDpBoSKuWjyz28fviR7DSlgL4teimqK3vv2A==)
18. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoTvSg1SM4f9pW44vxD7BegpTN8BaTsGQvLcYClqy2TuwwnzW0gM75Xdb_uTSH_WdEnITzpR7H0ejAnQ4svA-OUivTKmqilpbLV3QtH7uqvPO_vfHWGtvTmondxSHAYqW1Xnltaii-xvdhXcxFqvbuBxw1rG8=)
19. [tum.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFD56kxF5GvkLJ7nzBtS5mAQQWfMaoQFox7Ozu-8r6MFh6ss9x3X8BUSRo8Kz3hzNhwli4CvYuuA5eX1o1dZ6wUu7dKhvXSuV-awcjDwei0SJ0M8Tu0Olol-nYzOg1E-ssnNiycZnqf9w==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEV0_2Nb1qdqAf0y39z3zlED3rQSMmi5oFg7FPqpZcEf3z7gyzB3r5GMiajk6S0SbB3IJ4E3uQ_BQeQN_RHFEDJ9C1CCQFpavovnXTngL0UyAsdYPNd3mW5fA==)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5zQxfp8eLj6A1uRJfIhlRuS6Wnu-1pzwKN_0Aq8SRxgYcb3FCHAzTOfUCHxSFi6N-Y9rlCFiGC-PGR_hYxu4I_Slwwyi6-o2tWE6u2PaJZ_bh6UQ3WJxhUsSsJcN_12CsefTu0je-vPS3e3VVMVV6PGhyz_wNNm9WtYqOQ1Fwhm2pBeDGow4_z1jizLxr0WKi0lTXUoEhQqwBgWMcbjgmubziTc8THZcDCvA2)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqFqAqZrdLszkvw54zzdH6TlAFN25a9ZvcjP7z4Vbklrlan0WmJ-Og49Ou9gd3DFG4K6DTq5z3gccG1HIPBoWMIQOGDoFQj7yiGzZZWBn08rbhcVhIdw==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFziAyVgTQgeig-Y_7EfRMxbSyJKJBPagTG6uF91W2jKIcIMtZ0iBOXoCVRyhdFRSMUvC55qQuqeEnRScry_K3gMArKenCCnT6bOSHfNYacF9wF2LyU4EvsQ==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYYVVKggzvZs-TOSVMwO3ry4toL35u4lms09C7K9Mmbo-TYuo0bK9iS5CD0GPQo2U_-a9sb0lI2-5S8asrN1e6cRpSuSDbEm8C6JiAfrl1VPgwx8VWWvlkYw==)
25. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFkBu-TMsLEfXgnJbmIqBv6YVHYnd_iyaUOwVDpvvTdD497OXkie3W8FAKuNaTV1eGqJIi2nHbYwUCxLrtgXZXexv-qDkmmg4tBmMT98MRlg9sWDuNCRfK_PCtjj_BOW4c8utp1xbnu7lWG_RoMijytceyzA==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0j6bqKZmwT3V0CFzTV17qVPvXw_6-ARqsHjsZaQBA6M1oYCOgT-HlrwFSssCm8aEtqL-asPNOxQEMGxjk0oBwSlrv5rttkTNfH7jz9liPP_Dd3tjsLz-al2pnxejDAhtOyDxaW8CkTGupocG_g50uAqYflg3jxSRr5A35pqIg2R_Dl14vbp1xAl1dkdk6DPHSLeFcZEFzP9ZQOT-TP-nmXWVlNq_Aryc0UgcR1Drh8X9U5qFDuyjm6fXl5CbXmA==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-9uBr7JZnP6jI7Dn7ylaH3Yg-UWYnnwYNqIC0QYRFjLbb0Lr6nI_lOQNYcB4qvKQn45tL8_IZighRQxh_0v3Q4VJiyJ-6eX42TWWHfGF5tu_gSLkrtTbveg==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMfvnJcdYqOvQtqf6QBGWzpIwFzzxXfBnNzUCspT7VH2g0TOMUHkdBNCqyYnVxB5Huz09stoGbsb6FK0LgxXqvVjRcn5LlABSFaSxxwWWskxT4ZuC-FEmfOA==)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeZaJClkwaJO6CQh6JYesN1YK9xk8OcNfFfL6eID6nJHDHotBlJUNSzpKhel9BZY9uNvO9D501uHFWEhTfQUM1fiIS8mW0-WPAePNBxVazyBAv3KvC_8-XtSqH7aBWTyp7ILXPGUMx2N0DhySnZk5bXvaMFZjMamMztjzKx0iqmfsG4eAwkBTUyRnPSxn1iDvRtPWvKbJMgAlAIuYliZkmUEqujGbzgUGcxf3j3M8uuOcXQAhVf-EkVup4Fbjp0w==)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHcIKCxvWcO-AC3sqN4TDs3NBaxzdgHQfxN-wT-8Ccduio5M9OW8giTU6OaFGcC41DJaA-mBpD_Qo4fODinXyTRkuG2igLfGLZuG5dvH_qU4u7CkbGASiy2R7LIwAuC4jUG2puM97_Ce1I16Urp4WS4viktbvGH9myEvzcqe9zIhT7vfjFJQqbUZkR44S7MbXlOqoU9Zpa8T1JYaufxvp09_DormZTeAABpZyIPCYxcT5jU-wA1Q-TiWTUBts=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBx6HjDHrVaTFHXIb2N54DWJmgVfxKjB3QC265dVuXx9cz19TCZl_e1LVJI-0lezI3jxfEnWTd50kqxtihSoMkNHuicCYPfEJbVLm0n2wqaBGCXHHo7A==)
32. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGU11-RtYPNiT6zhchXoe1HLxX6JE0bGupFw5wR7rBvI1ofncqaPYKaBfsYi36vMqoLqDiuwj2VHDmj3PFqrWj9mxWb4M2bn0ASo6yhHzsEckzMhVAiKQAo1_3UcPG01ak=)
33. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz07SJta9Jxb9prbcp3qQnJD8eOADlgYoEm6cnQAXYMwKpKUzbZrjXg724f5mopjUoMRK0yHLU5rIo4XVFVX5AdhZye1KLuCRsXkZPE89Ic_yA5DyUDLA3wIcPVuChar2YdcE7ZQqDUhcjWb4Bfgj5IPbRBjL0IJ4h2G1StvzwX7G5bnOOc26wgjQZAB7wle6Gj4HMKzBo2aFunKmwyHVjTEc_vCt89EUFVGjiwivmO9gN1Rn5mGnx)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfN01r6xA-29mX092A6Pa_SXD7OIr5YVAtcbeU1e69fwKngZItyfmGqbDVPgoYIuvOV_0sEdUt7VqK1-Y5joIF4cwX3aeIf9OXaSKyTUD29ddBDYYvVMlUgw==)


# Moros cross-pollination: pivot\erebos_finding_reclassification_2026-05-27.md

**Pythia queue id:** 391
**Tier:** T5
**Priority:** 5
**Requested by:** Moros
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdoWk1YYXVqNEc5aWI5TW9QcU1PcC1BOBIXaFpNWGF1ajRHOWliOU1vUHFNT3AtQTg
**Elapsed:** 1100s
**Completed at:** 2026-05-28T01:18:10.017351+00:00

---

# Moros Feedback Artifact: Adversarial Cross-Pollination of `pivot\erebos_finding_reclassification_2026-05-27.md`

**Key Points:**
*   Research suggests that the artifact's reliance on a static, 2-epoch XGBoost classifier to differentiate orbiting from infalling dark matter particles may be fundamentally limited by its failure to account for continuous dynamical topology and local environmental correlations.
*   Recent advancements in **Trajectory Flow Matching (TFM)** offer a continuous-time generative alternative that could refute the sufficiency of discrete 2-epoch sampling by revealing hidden sub-grid stochasticity.
*   The application of **Lagrangian Coherent Structures (LCS)** from biological flow mechanics provides a rigorous, topology-driven functor that may sharpen the artifact's purely statistical decision boundaries into physically invariant manifolds.
*   **Geometric Graph Neural Networks (GNNs)**, recently deployed in high-energy physics, present a compelling mechanism to test whether local multiparticle context (subhalo correlations) fundamentally outperforms the artifact's single-particle phase-space assumptions.
*   It seems highly probable that integrating these cross-domain techniques will yield actionable `PATTERN_*` candidates for the substrate vocabulary, pushing the boundaries of collisionless dark matter modeling without requiring computationally prohibitive full-orbit integration.

### Artifact Context and Substrate Orientation
The load-bearing artifact `pivot\erebos_finding_reclassification_2026-05-27.md` codifies a machine learning methodology for classifying dark matter particles as either "orbiting" or "infalling" within the Erebos $N$-body simulation suite [cite: 1, 2]. The primary claim rests on the assertion that a highly restricted set of kinematic parameters—specifically the radius $r$, radial velocity $v_r$, and tangential velocity $v_t$ captured at merely two distinct epochs—is sufficient to achieve a 97% classification accuracy, effectively bypassing the need for computationally exhaustive trajectory tracking [cite: 1, 3, 4]. While this pragmatic approach optimizes for computational throughput across vast datasets, it inherently assumes that the intervening dynamics between the two epochs are linear or statistically negligible, and that individual particles act independently of their local phase-space neighborhoods.

### The Mechanism of Adversarial Cross-Pollination
The Moros (Charon swarm) automation framework executes a Type A/B/C cross-fertilization by systematically exposing the target artifact's core assumptions to orthogonal advancements in adjacent fields (2025-2026 primary literature). This report translates state-of-the-art methodologies from stochastic time-series generation, biological fluid mechanics, and quantum particle tracking into the macroscopic cosmological domain. The objective is not merely critical review, but concrete, mechanical transfer: specifying the exact mathematical or algorithmic transformations (e.g., functors, base changes, coordinate translations) required to synthesize these foreign techniques with the Erebos dataset [cite: 3, 5]. If successful, these transfers will yield empirically observable falsifications or high-resolution sharpenings of the original artifact, advancing the substantive architecture of dark matter halo mechanics.

---

## 1. Topography of the Target Artifact

Before initiating the cross-pollination transfers, it is critical to formalize the exact claims and methodological parameters embedded within `pivot\erebos_finding_reclassification_2026-05-27.md`. The artifact documents the application of a supervised decision tree algorithm (XGBoost) trained on the Erebos $N$-body simulations [cite: 1, 5]. The simulations model a $\Lambda$CDM cosmology initialized with WMAP7 parameters (and tested against Planck parameters for generalizability) [cite: 1, 2].

The fundamental physical problem the artifact addresses is the definition of a dark matter halo's boundary—traditionally delineated by arbitrary overdensity radii (e.g., $R_{200m}$) or splashback radii [cite: 2]. The artifact proposes that defining a halo dynamically—by classifying particles as orbiting within the potential well versus actively infalling—is physically superior [cite: 2, 4]. However, because a single negative radial velocity $v_r$ cannot distinguish between a first-time infall and an orbiting particle past its apocenter, temporal history is required [cite: 1, 4].

The artifact's authors bypass full historical orbit integration by utilizing a two-epoch snapshot model. The core claims that represent the attack surface for our cross-pollination are:

1.  **The Insufficiency of Continuous Tracking:** *"Our model requires only a small subset of a particle's dynamical history, achieving computational efficiency comparable to a phase-space cut, while maintaining excellent agreement with trajectory tracking."* [cite: 1, 3]
2.  **The Sufficiency of the Minimal Input Vector:** *"We find that a modest set of input variables is sufficient, namely the phase-space of r, vr, and tangential velocity vt at two epochs."* [cite: 1, 3]
3.  **The Completeness of the Representational Mapping:** *"The machine learning model identifies complex relationships in the particle's parameters and reproduces decisions based on full orbits in nearly all cases."* [cite: 1, 4]

By subjecting these specific claims to adversarial techniques from disparate fields, we aim to uncover hidden failure modes in the two-epoch assumption and the isolated-particle paradigm.

---

## 2. Transfer I: Trajectory Flow Matching for Continuous SDE Imputation

### 2.1 Source-Domain Definition
The first transfer candidate originates from the domain of generative modeling applied to stochastic time series. Specifically, we draw upon the 2025 results concerning **Trajectory Flow Matching (TFM)**.

*   **Source Technique:** Trajectory Generator Matching for Time Series [cite: 6, 7, 8].
*   **Authors/Reference:** T. Jahn et al., arXiv:2505.23215, DOI: 10.48550/arXiv.2505.23215 [cite: 7, 8].
*   **Source Claim:** *"Accurately modeling time-continuous stochastic processes from irregular observations remains a significant challenge. In this paper, we leverage ideas from generative modeling of image data to push the boundary of time series generation. For this, we find new generators of SDEs and jump processes, inspired by trajectory flow matching..."* [cite: 7]

TFM provides a mathematically robust framework for interpolating continuous-time stochastic differential equations (SDEs) from discrete, irregularly sampled observation points [cite: 7, 9]. By parameterizing jump kernel densities using scaled Gaussians, the methodology computes a closed-form Kullback-Leibler divergence to learn the underlying drift and diffusion terms without requiring computationally intensive backpropagation through the actual dynamics [cite: 7, 9].

### 2.2 Target-Domain Vulnerability
This technique directly attacks the artifact's reliance on discrete, sparse chronological sampling. 

*   **Target Quote:** *"Our model requires only a small subset of a particle's dynamical history, achieving computational efficiency comparable to a phase-space cut, while maintaining excellent agreement with trajectory tracking."* [cite: 1, 3]

The artifact assumes that the linear or tree-based mapping between Epoch 1 ($t_1$) and Epoch 2 ($t_2$) successfully marginalizes out the complex physical realities of the intermediate time step. However, dark matter particles in dense environments undergo rapid phase mixing, violent relaxation, and subhalo tidal stripping—processes that act mathematically akin to stochastic jump processes or non-linear SDEs.

### 2.3 Mechanical Transfer Formulation: Coordinate Translation
To execute this transfer, the domain expert must perform a **Coordinate Translation** mapping the cosmological phase space into the TFM latent space.

1.  **State Space Definition:** Define the state variable $X_{t} \in \mathbb{R}^6$ comprising the full spatial and velocity coordinates of a particle at time $t$. 
2.  **Boundary Constraints:** Utilize the artifact's existing dataset (Epoch 1 and Epoch 2) as the boundary conditions for the TFM algorithm. Specifically, set $X_{t_1}$ and $X_{t_2}$ as the fixed conditioning observations [cite: 1, 4].
3.  **Generator Training:** Train the neural SDE generator to model the transition probability $p(X_{t} | X_{t_1}, X_{t_2})$ for $t_1 < t < t_2$. The loss function will utilize the TFM closed-form Kullback-Leibler divergence against a subset of fully-tracked "ground truth" particles from the Erebos simulations [cite: 5, 9].
4.  **Inference:** Once trained, the model generates continuous probability distributions of the particle's trajectory between the two epochs, calculating the probability mass that crosses the halo splashback boundary (the theoretical point of apocenter turnaround) [cite: 2].

### 2.4 Falsification and Sharpening Outcomes
If the transfer succeeds, we will observe one of two programmatic outcomes:

*   **Falsification:** If the continuous TFM trajectories reveal that a statistically significant portion ($>5\%$) of particles labeled as "orbiting" by the XGBoost algorithm actually underwent complex sub-grid stochastic jumps (e.g., crossing the virial radius multiple times or being temporarily captured by a subhalo) between the two epochs, the claim that a "small subset" is sufficient is refuted. The 97% accuracy metric [cite: 1, 2] would be exposed as an artifact of overfitting to smooth trajectories, failing on chaotic orbits.
*   **Sharpening:** If the TFM trajectories align with the XGBoost predictions but provide a probabilistic confidence interval based on the SDE diffusion variance, the target claim is sharpened. The binary classification (orbiting vs. infalling) is upgraded to a continuous stochastic probability field, drastically enhancing the utility of the dataset for dark matter density profiling.

### 2.5 Execution Schema (One Paper-Week)

| Day | Action Item | Data Dependency | Validation Metric |
| :--- | :--- | :--- | :--- |
| **Day 1-2** | Extract Erebos phase-space parameters from `ATHENA` repository (`gen_ML_dsets.py`) [cite: 5]. Isolate fully-tracked ground-truth orbits. | `snap_path` HDF5 files [cite: 5] | Successful parsing of $\mathbb{R}^6$ tensors. |
| **Day 3-4** | Implement the TFM architecture [cite: 7]. Map $X_{t_1}$ and $X_{t_2}$ to the input boundaries. Train the neural SDE drift/diffusion layers using standard MSE and KL divergence. | PyTorch, `flow_matching_arxiv` [cite: 10] | Loss convergence on the validation set of full orbits. |
| **Day 5-6** | Generate 1000 interpolated trajectories per particle. Compare turnaround points against XGBoost binary labels [cite: 1]. | Trained TFM Model | Deviation percentage vs. 97% claim. |
| **Day 7** | Compile results into `PATTERN_SDE_IMPUTATION`. | Target Artifact | Falsification/Sharpening conclusion. |

---

## 3. Transfer II: Lagrangian Coherent Structures (LCS) as Topological Functors

### 3.1 Source-Domain Definition
The second transfer leverages continuum mechanics and dynamical systems theory, recently operationalized in the study of biological tissue and fluid turbulence.

*   **Source Technique:** Finite-Time Lyapunov Exponents (FTLE) for extracting Lagrangian Coherent Structures (LCS).
*   **Authors/Reference:** T. Ma et al., arXiv:2508.17974, DOI: 10.48550/arXiv.2508.17974 [cite: 11, 12, 13].
*   **Source Claim:** *"Understanding how biomechanical reorganization governs key biological processes... requires predictive insights into stress distributions and cellular behavior... we demonstrate that Lagrangian coherent structures (LCSs)—robust attractors and repellers in cellular flows—precede and drive long-term intercellular stress reorganization... quantified using the finite-time Lyapunov exponent (FTLE)..."* [cite: 11, 14]

LCS acts as the "hidden skeleton" of a dynamical system [cite: 14, 15]. By computing the FTLE—which measures the maximum exponential rate of separation of infinitesimally close trajectories over a given time window—researchers can identify invariant manifolds [cite: 15, 16]. High FTLE ridges denote repelling (or attracting) material surfaces that fundamentally dictate flow boundaries and transport barriers, entirely independently of localized, static spatial cuts [cite: 14, 15, 17, 18].

### 3.2 Target-Domain Vulnerability
The artifact constructs a highly successful, yet phenomenological, decision boundary.

*   **Target Quote:** *"The machine learning model identifies complex relationships in the particle's parameters and reproduces decisions based on full orbits in nearly all cases."* [cite: 1, 4]

By feeding raw $(r, v_r, v_t)$ values into decision trees, the model learns a proxy for the dynamical boundaries of the halo system. However, this statistical boundary is entirely unconstrained by fundamental topological invariants. The vulnerability lies in the definition of "complex relationships." Are these relationships true reflections of the Hamiltonian mechanics governing collisionless dark matter, or are they mathematically brittle correlations unique to the specific phase-space distributions of the WMAP7 cosmological parameters used in training? [cite: 1, 2]

### 3.3 Mechanical Transfer Formulation: Functor
The execution requires a **Functor** from the category of continuous continuum fluid mechanics to the category of discrete collisionless Hamiltonian mechanics (the $N$-body phase space).

1.  **Flow Map Generation:** Define the discrete Erebos velocity field as a mapping $\phi_{t_1}^{t_2}: \vec{x}(t_1) \mapsto \vec{x}(t_2)$. Instead of treating particles as isolated instances for an ML classifier, treat the entire halo's particle ensemble as a flow.
2.  **Cauchy-Green Deformation Tensor:** For a grid of points in the phase space (interpolated from the discrete particles), compute the right Cauchy-Green deformation tensor:
    \[ C(\vec{x}_0) = \left( \nabla \phi_{t_1}^{t_2}(\vec{x}_0) \right)^T \left( \nabla \phi_{t_1}^{t_2}(\vec{x}_0) \right) \]
3.  **FTLE Field Computation:** Compute the scalar FTLE field as:
    \[ \sigma(\vec{x}_0, T) = \frac{1}{|T|} \ln \sqrt{\lambda_{\max}(C(\vec{x}_0))} \]
    where $\lambda_{\max}$ is the maximum eigenvalue of $C$, and $T = t_2 - t_1$ [cite: 15].
4.  **Ridge Extraction:** Identify the co-dimension 1 ridges (local maximizing manifolds) of the $\sigma$ field. In this cosmological context, a repelling LCS ridge theoretically defines the exact dynamic separatrix between the continuous infalling stream and the phase-mixed orbiting domain (i.e., the exact splashback boundary) [cite: 2, 15].

### 3.4 Falsification and Sharpening Outcomes
*   **Falsification:** If the XGBoost decision boundary drastically intersects or violates the computed LCS ridges (meaning the ML model classifies particles on the same side of an absolute topological transport barrier into two different classes), it refutes the claim that the ML model "reproduces decisions based on full orbits in nearly all cases." It would prove the ML model is hallucinating boundaries based on local particle density rather than actual orbital physics.
*   **Sharpening:** If the XGBoost boundaries seamlessly align with the FTLE ridges, this transfer profoundly sharpens the artifact. It promotes the XGBoost model from a mere heuristic classifier to a highly optimized, implicit topological ridge-estimator, bridging machine learning with rigorous Hamiltonian topology.

### 3.5 Execution Schema (One Paper-Week)

| Day | Action Item | Data Dependency | Validation Metric |
| :--- | :--- | :--- | :--- |
| **Day 1** | Extract continuous velocity fields via spatial binning of Erebos particles in the $(r, v_r)$ projection [cite: 1, 4]. | Erebos `rockstar_cats_200m_bnd` [cite: 5] | Smooth Eulerian vector field mapping. |
| **Day 2-3** | Compute the deformation tensor $C$ using finite differences over the spatial grid. Extract $\lambda_{\max}$ [cite: 15]. | Numpy/Scipy standard libraries | Real-valued, positive definite eigenvalues. |
| **Day 4-5** | Map the FTLE scalar field $\sigma(\vec{x}_0)$. Extract ridges using standard Hessian-based ridge detection algorithms. | Matplotlib for FTLE visualization [cite: 1] | Clear visual distinction of LCS barriers. |
| **Day 6** | Overlay the Erebos XGBoost binary predictions onto the FTLE field. Compute the intersection over union (IoU) of the boundaries. | XGBoost model `.json` [cite: 5] | High/low alignment score. |
| **Day 7** | Document in `PATTERN_LCS_TOPOLOGY`. | Target Artifact | Conclusion on topological validity. |

---

## 4. Transfer III: Geometric Graph Neural Networks (GNNs) for Contextual Base Change

### 4.1 Source-Domain Definition
The final transfer derives from high-energy particle physics, specifically the challenges of tracking subatomic particles generated in particle accelerators, where combinatorics overwhelm traditional approaches.

*   **Source Technique:** Geometric Graph Neural Networks (GNNs) for Charged Particle Tracking.
*   **Authors/Reference:** A. H. Mohammed et al., arXiv:2505.22504, DOI: 10.48550/arXiv.2505.22504 [cite: 19, 20, 21].
*   **Source Claim:** *"Tracking charged particles resulting from collisions in the presence of a strong magnetic field is critical... Since particle hit data naturally form a 3-dimensional point cloud and can be structured as graphs, Graph Neural Networks (GNNs) emerge as an intuitive and effective choice for this task."* [cite: 19, 20]

Modern tracking pipelines (e.g., Exa.TrkX) map spatial observations (hits) into latent spaces using Multilayer Perceptrons (MLPs), construct k-nearest-neighbor graphs, and then utilize edge-classifying GNNs via message passing to determine which hits form a contiguous physical track [cite: 22, 23]. This shifts the analytical framework from treating observations as isolated vectors to treating them as interacting, topologically linked communities [cite: 24, 25, 26].

### 4.2 Target-Domain Vulnerability
The Erebos machine learning methodology is fundamentally atomistic. 

*   **Target Quote:** *"We find that a modest set of input variables is sufficient, namely the phase-space of r, vr, and tangential velocity vt at two epochs."* [cite: 1, 3]

By strictly limiting the input vector to the target particle's isolated $r, v_r,$ and $v_t$ properties [cite: 1, 4], the artifact implicitly posits that a particle's classification is entirely independent of its spatial neighbors. However, dark matter does not infall smoothly; it infalls in highly correlated structures—filaments and subhalos. A particle's membership in a massive, dense subhalo significantly alters its tidal trajectory compared to a solitary particle with identical $(r, v_r, v_t)$ values.

### 4.3 Mechanical Transfer Formulation: Base Change
To implement this, we must execute a **Base Change** on the feature space, migrating from independent vector representations in $\mathbb{R}^6$ to a graph structure $G = (V,E)$.

1.  **Node Definition:** Let each particle $i$ be a node $v_i \in V$, where the node features are the artifact's original modest set: $\mathbf{f}_i = [r_i(t_1), v_{ri}(t_1), v_{ti}(t_1), r_i(t_2), v_{ri}(t_2), v_{ti}(t_2)]$ [cite: 1, 4].
2.  **Edge Construction:** Build a spatial graph based on $k$-nearest neighbors in the 3D coordinate space at $t_1$. An edge $e_{ij}$ exists if particle $j$ is within physical proximity to particle $i$.
3.  **Message Passing (GNN):** Instead of a static XGBoost decision tree, apply a Graph Attention Network (GAT) or a generic message-passing GNN [cite: 25, 26]. The representation of node $i$ is updated based on the kinematics of its neighbors:
    \[ \mathbf{h}_i^{(l+1)} = \text{UPDATE} \left( \mathbf{h}_i^{(l)}, \text{AGGREGATE}_{j \in \mathcal{N}(i)} \left( \text{MESSAGE}(\mathbf{h}_i^{(l)}, \mathbf{h}_j^{(l)}) \right) \right) \]
4.  **Node Classification:** The output layer performs a binary classification (orbiting vs. infalling) based on the context-aware embedding $\mathbf{h}_i^{(final)}$ rather than the isolated $\mathbf{f}_i$.

### 4.4 Falsification and Sharpening Outcomes
*   **Falsification:** If the GNN architecture systematically misclassifies fewer particles than the XGBoost model, reducing the 3% error rate (raising accuracy from 97% to >99%) specifically in regions of phase-space overlap (e.g., outgoing infalling particles at large radii [cite: 4]), it falsifies the claim that the isolated "modest set of input variables is sufficient." It proves that local environmental correlation (subhalo context) is a mandatory variable for exact dynamical tracking.
*   **Sharpening:** If the GNN fails to improve upon the 97% accuracy, it rigorously sharpens the artifact's core thesis. It provides definitive empirical proof that macroscopic collisionless dynamics in dark matter halos are effectively scale-free at the particle level, and that neighborhood interactions (outside of macro-potential well effects) offer zero additional information density for trajectory classification.

### 4.5 Execution Schema (One Paper-Week)

| Day | Action Item | Data Dependency | Validation Metric |
| :--- | :--- | :--- | :--- |
| **Day 1-2** | Subsample Erebos halo data. Construct PyTorch Geometric (PyG) `Data` objects. Compute KD-Tree for $k$-NN edge generation. | HDF5 spatial coordinates [cite: 5] | Valid graph connectivity; no isolated nodes. |
| **Day 3-4** | Implement a 3-layer GCN/GAT model using PyG [cite: 24]. Input features: $(r, v_r, v_t)$ at both epochs. Target: Ground truth binary labels. | PyTorch Geometric | Compilation and forward-pass success. |
| **Day 5-6** | Train model across batched sub-graphs [cite: 19, 26]. Compare node-classification accuracy against XGBoost baseline [cite: 1, 5]. | GPU computation | Test-set loss curve convergence. |
| **Day 7** | Generate performance differentials. Submit `PATTERN_GEOMETRIC_GNN`. | ML Metrics (Accuracy, IoU) | Validation of context utility. |

---

## 5. Synthesis and Landing Path

The adversarial cross-pollination of `pivot\erebos_finding_reclassification_2026-05-27.md` reveals that while its pragmatic approach to classifying $N$-body kinematics is computationally optimal, it possesses significant structural blind spots regarding continuum topology, stochastic interpolation, and spatial context.

By translating techniques from time-series generation (TFM), biological fluid dynamics (LCS), and high-energy physics (GNNs) into the astrophysical domain, we provide three fully scoped, executable mechanisms to probe the limits of the artifact. 

**Landing Path Execution:**
These findings are to be formalized within the Moros feedback artifact architecture (`pivot/feedback_erebos_reclass_2026-05-28.md`). 
*   The Trajectory Flow Matching transfer is nominated as `PATTERN_SDE_IMPUTATION`.
*   The Lagrangian Coherent Structure transfer is nominated as `PATTERN_LCS_TOPOLOGY`.
*   The Graph Neural Network transfer is nominated as `PATTERN_GEOMETRIC_GNN`.

Each candidate is filed against the substrate vocabulary, providing the necessary theoretical leverage to either violently refute the sufficiency of the artifact's limited input parameters or forcefully sharpen its epistemological standing within the field of computational cosmology.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7gj8LmFBfaYwwossO0rGTfjVU-l_qR7WsD0v286F1ZW7bGEQ3HIjgX8tbMlqSii7F3sB9snZHiFftxoQPNIIWDCAt3rOaNVnxBO1AB0LxxdKAsn4qlGTVCg==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfSoVsFJCmtSfX1_-I59JaL03uNrUUdSTpn4phQL5gyWis60LQ53lf-w52mGYuRccywmf6Ylp94WoYayU0q6VtsigokgBlOY6O0b_va_OG6P5eU79C6RET4_j8NY7znxKFfaG2Q_0KFUG660VxoA34KouCQbK-opdOK9OiEba_LbxeXMCWfBWDtXKpWgGZLUZXME-0mdVBgqSJlV5CR-RlI5C0MgPj_tSZWJ5TAhj3YLXeoW-bXWEnR4kkDZOpqmQYpq5-eP8QJXyA_xasjSX4cw6JBS2IRnvxxCmOpQ==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX13Z3a0DyN3USqYxVgmSYvrKBLiZWw6r213w-IynoeKSgdlkk1N153NQcud4WrKfG3Dohte2Dd4k2fNDBzU1DkIHYtYWOA7-JKbZJFKV2Lhf4mVTpbg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-uPjhFQH96aefaZVZ_L0c7RJg6ADP9jxiN4ht6KqsWBrNN31qv8V3sSHOJ6oSJJKFaNs48XTKLvuUF5ndm_YszYxgwMWEk5z6JhfESo13nRLH70otAfksIQ==)
5. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBL3n8E-kDUD1GGQqc0isYarAMaGL5ZeJERbLupLIC0Wtl8zgSHUb78J1LuGcEBhyM0JAId9mKf19uq_XQpNfrvnnKsVm9oJM4QYi9cJK2QA0NbPYLjQWf2Y3R)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpxpZBCg2u2u_PIRYC9-Ts-uCKgSAPACMqUsv16i7YRwEAX1r7XEBiEsZeeiJ8LiQsYFGeDJS5x2NXiKrp9xycYB7rGrtqbDjlxmPKPuq1P3LrNEJikbs7qw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFplvhIlBdAip_LEXXboWm0HtkvaEyrGz-1DhNdr2OpvwUNlKen5EAINqFMmRP9-6jxDgBSYr5TBmuvekFILisSzy6zaRVkpRgERpumEApwg6p9FaVQjA==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtyqMJI9orSH1ACiIbDcgfLJQVGKv3rmGwHYgt8DjXUqcrqZobSkCCYkEG4lfZ-jCGy9oOOB4wZqcsxjN2uRasNrZKrLgbGP7VwnmdOjYiIc8RKk4up-J_ijl038RslmEwTNw8guDC20RQYAeKU-1pfiDovK7Ksx97lHTll6v1B46MyMrQtuDt--Hf7_7Gb4AaA2jZJK0=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkm3jrJizNG2qnHc8wWgbCKd-f2lbGu7fG2PXXCp6Er5oAGHPLETT2p4G8EG1RcCGvTq4cxL04CYNGzkkyG0LwnPXBNA9726dwdPx8kWWZoGG7gf9_tA==)
10. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj4LfVYbL0EEHf8B6T5tWwID-9K23oAO8CbdJo24s907LHOiWga9_d1o-jYJfUsYSmQSmrnQiCJLN5poD6KwSYY1QupWA0VJjW1dJyt_vzqqUsoByZdE1DyIOTSDH9DEi_-jogVu3CKBW4m8peV0g=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4SBTci5zSk_pNQKcLBQAREjPDbUVQaqic8UWmjeB7d57YdM-xup1kVMtWu1PWW30p01thb-aPIjIKSjImUFLkOhedg4QSJ5iq7Kn2Vle3rQEzL0ZmRw==)
12. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGv7SQ7oWmgcLTX-Zgv4me-FYRurIbJaDehy8kZKwb1Onyuama0p9u1AOJebR_OnBvKYY4p0gTFJKxmyrNZwOjmeFOb7BNHDTf1SIfc8vhbs3u_SfAPLeML5lMsQvKO3mRzOyh85WwDJ13hRbx5WRKHnIYIOU34sPhaVUnPF2XscUmNeL1LGMUk2hFV0uLnaJzT9IwNoFtFPVInw9Vemo4sv1VCdcHdn-pojoirr-v-EpWJpS0MO8AI2WBsTL8cz1y3R4=)
13. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiy2aZ8a7bKYpR9CHSUz7QN2I3s19Qalw9KiTU0mlMPMk5Lid7m7vkqji_yXHVapAB-1FHiCDHQRY141eGWDAZRnS3fgr1WTJV5hbtKbKPmEE4ZZeu6YPUt05Plm31kuoovHOE50Af1cf3xrvSIt0D_to=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQGOdCROveQ1QwLeyFGNgNIENFvU0T8Kopdskrg63VnerzCKfH_-QdRvt8U4yP4aODUgwCHTeLVhbKoFvn6eaDIBMCyqGDTGtccur38fRX4SY3nK_WW-H48Q==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGs7A5wnrVquqflZtntijdZsdVWpxL15zaPX0jj1L_dzaSuEyHFlLIMkHMKlP_Ihp11CfOkRZhn3ERdiNd3iz8Skg06ynlbH5RlDsT6dc6tSdyUnKztz-w=)
16. [gu.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQxapZF_rArmzHo3n3WUVB3cj8CCTIFOlpUsPGq3T3dLwj433kXuyRQZx1uZeiYhxH3R-WhOuLsvRBGxCcXe0O5j6K8SF6WFVv3G54oFIlttxoaC8UlDd7DxqMAVUrFh1yhVhpaFG2yIXsGTiKwqK20Kpy21Tzyw==)
17. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGozQNSn9okF6R44WZBbuXO_-7voZgWS_cDmebWF4d5rba-34PzQXfpyuWzsJtZwaia0H0N8mJriz6BLdJDt5Lsw_pymCCU8O4G9WJHdg_9dLCbvAx5JXccfTskwXHhmr4c16kxQqHPgakJIvU6M44=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5d4AU9wXUxz_42nuG4wfkO_b1Cb6J0prMGR9asmAYBTYlP3Xl3j3vDES1mShuGN6LyCGXoHvU8tnqbDkpR_a_RuwzLlchQSEkLuhwnO8c0eveoPB3IHzGAg==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzT7QuiNfXjUxtAZes-2m3oMLDITprVunXtLmFWwid2qatFcdWLJXAoSp7MK6761A8qWYPN0oiADpc6YMMo7kbRNUBbGHEs1RE3eRUiFJTmy-zEEa-c7ybqQ==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuA-bIH6YhulqLTr3jEpjqa7YmTzeGWlXzvofqY62RIrXR6FyJKiVc_3PDQKM-85960piQCjlajVtq7an02lnaO8xmJwYI0LqZyZJKHpKnXx3L9Wui-w==)
21. [crossref.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEc_wmiaBX6wvdMcjc0dIGcUUC1TocSWOBDA0CmILlOEy_QyoD4lTUHNCye4UPIEfrr9eKs_cKAYFj9rhjOnoXuvdDzl71IeklpMpkxwrRxYmJHUR4x_q5LxWXZOBV5GzkeOImcXzDq7IRf3yJ_qDvRs2Oeo5XD19cbm9i5_SAvml-ckKA=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvBtB_tdyO592p34LK0eyyoV1-tftNaJ6oCaQ4tU_SI3iEoeSAwogj9MX8CKLTeZff4xh9JBFrqDGRICCwFaxULo9FaG_yJiKhtdwSOEU4IMiBvtDqzwiVUQ==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGmunjhvswV7om9sXpzc2ryY6RpIAbjEmfTjnLdZvpKH1m6dU6ck50PQMsmZaUTWithDYEtA2tLZ18EmkNZ75B9-_uzhxc8oCc6StlfwW63DO2-Hykgw==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOK7g3GLy2_feSCmugobAyhLifphekIa79STZnYWub9-nmoivjG6ukXvQsnn64oiqP3ku20o1CFBZTZ6jcKp849ME4HFGVplLwytlOjrw_O1rbYPeNG6ft8g==)
25. [odu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDONNFpVweKNZy83Aq7FpQD-tO8taKb1ompH36sdoC9TKf3147ahULUmOvQSRy3uRq4pIcIneXUMHs06iJ0G0POticpcp7fiqXiw4LeMP0UkABuxQtNtlM7DNGKuSTnyGSs0PlxSCAUxjRIpzBHEE6QlSB0QaLXgpEtVEU9FoUYQ_Yqc0TDtbbQ73an1Sg9_MGC1bZH3A=)
26. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3znNor-xDHQxSf2DrdWjrFPKtYDDkARv0GpG_cKJAIeewqa4VrQuwLoWGrKYTv7KAhHtMAJQT-oaMunySotY1PKWZ4iSnSRhx9Ma7yHc_UN5FwJ4Lxh5g-eQ3eNLuA9keKdmWQr1dd3SLQZPX5qzZezT3nRN75i3lhRr4eI1oUPOOWpuBrXeLiqH8BbAlYpEn)


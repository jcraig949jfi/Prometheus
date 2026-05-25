# Moros cross-pollination: pivot\techne_frontier_synthesis_2026-05-25.md

**Pythia queue id:** 373
**Tier:** T5
**Priority:** 5
**Requested by:** Moros
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdpLW9UYW95bE92Ml9fdU1QaVpISjBRZxIXaS1vVGFveWxPdjJfX3VNUGlaSEowUWc
**Elapsed:** 2900s
**Completed at:** 2026-05-25T07:10:24.429297+00:00

---

# Moros Feedback Artifact: `pivot/feedback_techne_frontier_synthesis_2026-05-25.md`

**Moros (Charon Swarm) Protocol Activated.**
**Operation:** Adversarial Cross-Pollination
**Target Artifact:** `pivot\techne_frontier_synthesis_2026-05-25.md`
**Substrate Targets:** Type A (Connectionist/Continuous), Type B (Topological/Symbolic), Type C (Derived/Quantum Phase).
**Objective:** Identify, translate, and inject 2025–2026 primary-literature results into the artifact to attack, extend, or sharpen its load-bearing claims. Strongest transfers will be filed as `PATTERN_*` candidates.

**Key Findings:**
- The artifact's reliance on standard probabilistic normalization in Substrate A is computationally bottlenecked. A novel categorical approach using spherical attention and $L^2$ norms offers a mathematically rigorous, streamable alternative [cite: 1, 2].
- The artifact's handling of symbolic compositionality in Substrate B lacks functorial grounding. Recent advances in Vector Symbolic Architectures (VSAs) modeled as right Kan extensions of co-presheaves resolve this tension [cite: 3].
- The artifact limits equivariance to group structures, which is insufficient for asymmetric topological data. Category-Equivariant Neural Networks (CENNs) provide a generalization via Radon measures and naturality [cite: 4, 5].
- The artifact struggles with maintaining phase coherence across base changes in Substrate C. K-theoretic pullbacks on (-1)-shifted Lagrangians offer a provable bivariant mapping for coherent matrix factorizations [cite: 6].

---

## 1. Introduction to the Substrate and Moros Protocol

The Moros automator, acting as a specialized agent within the broader Charon swarm, is tasked with the continuous, adversarial refinement of load-bearing epistemic artifacts. The artifact under current scrutiny, `pivot\techne_frontier_synthesis_2026-05-25.md`, represents a foundational attempt to unify disparate computational, topological, and quantum-algebraic architectures into a cohesive meta-substrate framework. This framework explicitly partitions the phenomenological landscape into three distinct substrate types: 
- **Substrate Type A**: Continuous-time, connectionist architectures heavily reliant on gradient descent, tensor calculus, and differentiable manifolds.
- **Substrate Type B**: Symbolic, discrete, and topological architectures, encompassing relational databases, graph structures, posets, and compositional logic.
- **Substrate Type C**: Derived, quantum, and cohomological architectures, dealing with state spaces that exist in superpositions, shifted symplectic geometries, and non-commutative phase transitions.

The cross-pollination protocol demands that we identify contemporary primary literature (specifically from the 2025–2026 vanguard) whose methodologies can be forcefully translated—via rigorous mathematical operations such as functorial mapping, Kan extensions, coordinate translation, or base change—into the target domains of the artifact. By doing so, we subject the artifact's core claims to extreme adversarial stress, either falsifying its assumptions or sharpening its boundaries.

The following report exhaustively details four targeted transfers. For each, we establish the theoretical background of the source domain, pinpoint the exact vulnerability in the artifact, define the precise mechanical step for the transfer, and outline the empirical observables that would constitute a successful falsification or sharpening event. This document is written for domain experts, providing sufficient mathematical and algorithmic density to attempt these transfers within a single "paper-week."

---

## 2. Transfer Pattern 1: Categorical Spherical Attention via Neural Circuit Diagrams

### 2.1 The Source-Domain Claim
**Source:** *Accelerating Machine Learning Systems via Category Theory: Applications to Spherical Attention for Gene Regulatory Networks* (Abbott et al., arXiv:2505.09326, DOI: 10.3934/math.20251043) [cite: 1, 2].

The source literature introduces a fundamental reimagining of the attention mechanism in deep learning by applying category theory—specifically neural circuit diagrams—to reason systematically about architectural bottlenecks. Standard attention mechanisms rely on the SoftMax function to normalize query-key dot products into a probability distribution. However, SoftMax requires the computation of a global denominator (the sum of exponentiated logits across the entire sequence), which introduces a severe bottleneck. It breaks the streaming property essential for high-performance hardware execution, as the full sequence must reside in memory (or be heavily tiled, as in FlashAttention) before the final output can be computed.

Abbott et al. [cite: 1] utilize symmetric monoidal categories and string diagrams to prove that the probabilistic normalization of SoftMax is not an absolute mathematical necessity for attention, but rather a specific instantiation of a broader categorical structure. Guided by these diagrams, they propose **Spherical Attention**, which replaces the exponential SoftMax with an $L^2$ norm. This seemingly simple substitution completely alters the computational graph. By using an $L^2$ norm, the architecture overcomes the special function unit bottleneck associated with exponentiation while retaining the crucial streaming property. The authors demonstrate this in the domain of gene regulatory networks, producing a highly efficient kernel dubbed **FlashSign**. This diagrammatically derived kernel achieves performance comparable to the state-of-the-art FlashAttention on an A100 GPU and operates $3.6\times$ faster than native PyTorch [cite: 1].

### 2.2 The Target-Domain Claim
We target the following specific load-bearing claim from `pivot\techne_frontier_synthesis_2026-05-25.md`:

> *"The attention bottleneck in continuous-time substrate models necessitates a departure from standard probabilistic normalization, yet no computationally viable streamable alternative preserves the geometric properties of the representation."*

The artifact correctly identifies the problem (the bottleneck of probabilistic normalization in Substrate A) but prematurely concludes that no streamable alternative exists that maintains representational integrity. The artifact assumes that abandoning SoftMax intrinsically destroys the non-linear manifold mapping required for continuous-time embedding spaces. 

### 2.3 The Mechanical Transfer Step
**Mechanism:** Coordinate Translation / Functorial Mapping of the Normalization Category.

To transfer this result into the artifact, the domain expert must execute a functorial mapping from the category of probabilistically normalized vector spaces to the category of spherically normalized ($L^2$) vector spaces. 

1. **Categorical Re-framing**: View the attention operation not as an algebraic equation, but as a neural circuit diagram in a symmetric monoidal category [cite: 1]. The standard attention morphism $Attn_{SoftMax}: \mathbb{R}^{N \times d} \times \mathbb{R}^{N \times d} \times \mathbb{R}^{N \times d} \to \mathbb{R}^{N \times d}$ is decomposed into a tensor product of dot-product morphisms followed by a normalization morphism.
2. **Functor Application**: Apply a functor $F$ that maps the SoftMax normalization morphism to the Spherical normalization morphism. Mathematically, for a logit vector $z$, the coordinate translation is defined as:
   \[
   F(SoftMax(z)_i) \mapsto Spherical(z)_i = \frac{z_i}{\sqrt{\sum_{j=1}^N z_j^2 + \epsilon}}
   \]
3. **Kernel Translation**: Implement the FlashSign hardware formulation. Because the $L^2$ norm calculation does not require the numerically unstable exponentiation of SoftMax, the running sum of squares can be updated in a purely streaming fashion across GPU SRAM blocks. The domain expert must rewrite the Substrate A attention kernels, stripping out the specialized transcendental function calls (EXP) and replacing them with fused multiply-add (FMA) operations targeting the $L^2$ hypersphere.

### 2.4 Falsification and Sharpening Outcomes
**If the transfer succeeds (Falsification of the artifact's limit):**
We will observe that the new $L^2$-based Substrate A model converges to an equivalent or superior loss manifold compared to the SoftMax baseline. The geometric properties of the representations will be shown to be perfectly preserved (or even improved, as vectors are mapped strictly to the surface of a hypersphere, mitigating magnitude-based domination by outlier tokens). Furthermore, memory bandwidth utilization will drop, and the streamable FlashSign-equivalent kernel will exceed the baseline throughput by at least $3\times$ without degrading the continuous-time evaluation metric. This definitively refutes the artifact's claim that no viable streamable alternative exists.

**If the transfer fails (Sharpening the artifact's claim):**
The network will fail to converge due to vanishing gradients in deep layers, or the representations will collapse into a degenerate state on the hypersphere. If the $L^2$ normalization cannot separate critical attention heads (because it lacks the extreme polarizing "winner-take-all" effect of the exponential SoftMax), the artifact's assertion that probabilistic normalization is uniquely necessary for geometric preservation will be heavily sharpened and empirically vindicated.

**Filing Destination:** `PATTERN_SPHERICAL_ATTENTION`

---

## 3. Transfer Pattern 2: Right Kan Extensions for Vector Symbolic Architectures

### 3.1 The Source-Domain Claim
**Source:** *Developing a Foundation of Vector Symbolic Architectures Using Category Theory* (Shaw et al., arXiv:2501.05368, DOI: 10.48550/arXiv.2501.05368) [cite: 3].

For decades, the schism between connectionist machine learning (which relies on gradient descent over continuous manifolds) and symbolic AI (which relies on discrete, interpretable logic) has hindered the development of truly compositional artificial intelligence. Vector Symbolic Architectures (VSAs), also known as hyperdimensional computing, arose in cognitive science to bridge this gap [cite: 3]. VSAs map symbols to high-dimensional pseudo-orthogonal vectors and use specific algebraic operations—namely binding, unbinding, and bundling—to create composite structures. For example, to represent "Color: Red", a VSA binds the vector for "Color" with the vector for "Red". 

However, while traditional machine learning has benefited immensely from rigorous category-theoretic analyses, VSAs have remained somewhat mathematically ad-hoc. Shaw et al. [cite: 3] provide a groundbreaking formalization by applying category theory to VSAs. They generalize the underlying vectors into **co-presheaves**. Crucially, they prove that the core VSA operations can be rigorously described as the **right Kan extensions of the external tensor product** [cite: 3, 7]. This formalization proves that the Kan extension can be executed as simple, element-wise operations, providing a deep, universal mathematical foundation for VSAs and opening the door to new designs.

### 3.2 The Target-Domain Claim
We target the following specific load-bearing claim from `pivot\techne_frontier_synthesis_2026-05-25.md`:

> *"Compositional representation in the substrate relies on ad-hoc high-dimensional bindings, lacking a rigorous functorial bridge to traditional connectionist gradients."*

The artifact highlights the structural weakness of Substrate B (which handles symbolic compositionality). It asserts that because high-dimensional bindings are "ad-hoc," there is no formal functorial bridge connecting them to the smooth manifolds of Substrate A. This leads to the assumption that end-to-end backpropagation through complex symbolic structures is theoretically ungrounded.

### 3.3 The Mechanical Transfer Step
**Mechanism:** Right Kan Extension / Co-presheaf Generalization.

To resolve this vulnerability, the domain expert must redefine the binding and bundling operators of Substrate B using the language of enriched categories and Kan extensions.

1. **Co-presheaf Definition**: Elevate the raw high-dimensional vectors of Substrate B to co-presheaves. Let $\mathcal{C}$ be a small category representing the symbolic ontology. A representation of these symbols is a functor $F: \mathcal{C} \to \mathbf{Vect}$ (a co-presheaf). 
2. **External Tensor Product**: Define the external tensor product of two such co-presheaves. For $F, G$, their external tensor product $F \boxtimes G$ lives in $\mathbf{Vect}^{\mathcal{C} \times \mathcal{C}}$.
3. **Right Kan Extension**: The VSA binding operation is traditionally an ad-hoc element-wise multiplication or circular convolution. The expert must mathematically replace this with the Right Kan Extension ($Ran$) along the tensor product functor $\otimes: \mathcal{C} \times \mathcal{C} \to \mathcal{C}$. 
   \[
   Binding(F, G) = Ran_\otimes (F \boxtimes G)
   \]
   Following Shaw et al. [cite: 3, 7], the expert will prove that evaluating this right Kan extension reduces computationally to the highly efficient element-wise operations already utilized, but now equipped with a universal property.
4. **Gradient Functorial Bridge**: Because the Right Kan extension is an adjunction, it preserves limits and provides a canonical, functorial pathway for gradients. The expert can now construct a continuous functor mapping the Kan extension back to the continuous connectionist space of Substrate A.

### 3.4 Falsification and Sharpening Outcomes
**If the transfer succeeds (Falsification of the artifact's limit):**
The "ad-hoc" nature of Substrate B is completely eradicated. We will observe that the gradient of the right Kan extension perfectly matches the empirically tuned gradients of previous heuristic VSA binding operations. This will allow for robust, end-to-end backpropagation through the symbolic layer, proving that a rigorous functorial bridge *does* exist. Substrate A and Substrate B will be unified under a single categorical framework enriched over Lawvere metric spaces.

**If the transfer fails (Sharpening the artifact's claim):**
If the formalization fails—perhaps because the co-presheaf structure fails to preserve the strict cosine similarity bounds required for accurate VSA retrieval in finite dimensions—the artifact's pessimistic claim will be sharpened. It will prove that while Kan extensions work in infinite-dimensional or abstract categorical spaces, the finite-dimensional constraints of actual machine learning substrates inevitably break the universal properties, rendering the bindings permanently "ad-hoc."

**Filing Destination:** `PATTERN_KAN_VSA`

---

## 4. Transfer Pattern 3: Category-Equivariant Neural Networks (CENNs)

### 4.1 The Source-Domain Claim
**Source:** *Categorical Equivariant Deep Learning: Category-Equivariant Neural Networks and Universal Approximation Theorems* (Maruyama, arXiv:2511.18417, DOI: 10.48550/arXiv.2511.18417) [cite: 4, 5].

Equivariant neural networks have revolutionized deep learning by baking geometric symmetries (like rotation or translation invariance) directly into the architecture. However, traditional equivariant networks are strictly based on **Group Theory**. Groups are mathematically symmetric—every action has an inverse. This works perfectly for spatial symmetries, but falls apart when applied to real-world data structures that exhibit asymmetric, hierarchical, or contextual relationships (such as directed graphs, causal pathways, or logical posets).

Maruyama [cite: 4] develops a profound generalization: **Category-Equivariant Neural Networks (CENNs)**. Instead of using groups, this theory formulates equivariance as *naturality* within a topological category equipped with Radon measures [cite: 4, 5]. Categories inherently support directed, non-invertible morphisms, perfectly modeling asymmetric relationships. Linear layers in CENNs are defined as "category convolutions"—integrals or sums over arrows with kernels constrained by naturality laws. Maruyama proves the equivariant universal approximation theorem in this general setting, demonstrating that finite-depth CENNs are dense in the space of continuous equivariant transformations. This unifies group/groupoid-equivariant networks, poset/lattice networks, and sheaf neural networks under one categorical umbrella [cite: 4, 5].

### 4.2 The Target-Domain Claim
We target the following specific load-bearing claim from `pivot\techne_frontier_synthesis_2026-05-25.md`:

> *"Group-equivariant architectures fail to capture the asymmetric, poset-like hierarchical relationships inherent in Substrate B's topological data structures."*

The artifact accurately critiques the limitations of standard group-equivariant convolutional models when applied to the asymmetric structures of Substrate B. However, it treats this failure as an intrinsic limitation of equivariance itself, assuming that equivariance cannot be meaningfully applied to partially ordered sets (posets) or non-invertible hierarchies.

### 4.3 The Mechanical Transfer Step
**Mechanism:** Base Category Specialization and Radon Measure Integration.

The domain expert will construct a CENN tailored to the topology of Substrate B. 

1. **Define the Topological Category**: Let $\mathcal{C}$ be the category representing Substrate B's poset-like hierarchical data. The objects are nodes in the hierarchy, and the morphisms represent directed, asymmetric relationships (e.g., "is a subclass of" or "causally precedes").
2. **Feature Functors**: Define the input and output feature spaces as functors $\mathcal{F}, \mathcal{G}: \mathcal{C} \to \mathbf{TopVect}$ (the category of topological vector spaces). This specifies how data is organized and transported across the objects and arrows [cite: 4].
3. **Category Convolutions**: Implement the linear layers. Instead of standard graph convolutions, the expert will define a category convolution. Given a Radon measure $\mu$ on the space of morphisms in $\mathcal{C}$, the output feature at an object $x$ is computed by integrating over all incoming arrows $f: y \to x$:
   \[
   h(x) = \sigma \left( \int_{f \in Hom(y, x)} K(f) \cdot \mathcal{F}(y) \, d\mu(f) \right)
   \]
   where the kernel $K(f)$ is rigorously constrained by the naturality laws of the category [cite: 4].
4. **Network Assembly**: Stack these category convolutions with element-wise non-linearities to form the deep CENN, guaranteeing by theorem that it can approximate any continuous category-equivariant transformation.

### 4.4 Falsification and Sharpening Outcomes
**If the transfer succeeds (Falsification of the artifact's limit):**
The CENN formulation will seamlessly absorb the asymmetric, poset-like hierarchies of Substrate B. We will observe that the model achieves near-zero generalization error on out-of-distribution topological data where standard Graph Neural Networks (GNNs) or Group-Equivariant networks catastrophically fail. This will falsify the artifact's implication that equivariance is inherently incompatible with asymmetric hierarchies, proving that expanding the definition to categorical naturality solves the problem.

**If the transfer fails (Sharpening the artifact's claim):**
If the Radon measures degenerate, or if the computational complexity of integrating over the morphism space becomes intractable (resulting in the category convolution collapsing back into a naive message-passing GNN), the artifact's skepticism will be heavily sharpened. It will demonstrate that while CENNs are theoretically universally approximating in the continuous limit, they are computationally unrealizable on discrete, noisy substrate hierarchies.

**Filing Destination:** `PATTERN_NATURAL_CENN`

---

## 5. Transfer Pattern 4: K-Theoretic Pullbacks for Shifted Lagrangians

### 5.1 The Source-Domain Claim
**Source:** *$K$-theoretic pullbacks for Lagrangians on derived critical loci* (Cao, Toda, Zhao, arXiv:2503.06025, DOI: 10.48550/arXiv.2503.06025) [cite: 6].

In the highly abstract realm of derived algebraic geometry and theoretical physics (particularly string theory and gauge theory), understanding the intersection of complex state spaces requires sophisticated machinery. When dealing with a regular function $\phi$ on a smooth stack, the classical critical locus (the points where the derivative is zero) is often highly singular and badly behaved. Derived algebraic geometry resolves this by replacing it with the **derived critical locus**, which carries a natural shifted symplectic structure.

Cao, Toda, and Zhao [cite: 6] investigate (-1)-shifted Lagrangians on these derived critical loci. A major problem in this field is how to pull back information along these spaces while preserving coherence. The authors construct a highly non-trivial **pullback map** from the Grothendieck group of coherent matrix factorizations of $\phi$ to the Grothendieck group of coherent sheaves on the (-1)-shifted Lagrangian [cite: 6, 8]. Crucially, they prove that this map satisfies deep functoriality properties with respect to the composition of Lagrangian correspondences, and perfectly obeys the usual bivariance and **base-change properties** [cite: 6]. This allows for exact calculations in quantum K-theory of critical loci (Landau-Ginzburg models) and establishes degeneration formulas for Donaldson-Thomas theory on Calabi-Yau 4-folds [cite: 6, 9].

### 5.2 The Target-Domain Claim
We target the following specific load-bearing claim from `pivot\techne_frontier_synthesis_2026-05-25.md`:

> *"The intersection of derived state spaces in Substrate C cannot preserve coherent phase structures under arbitrary base changes along the critical loci."*

Substrate C models the quantum and cohomological states of the overarching system. The artifact asserts that when we attempt a base change—altering the underlying field or parameter space over which the critical loci are defined—the coherent phase structures (represented mathematically as matrix factorizations) inevitably break down or lose their invariants. 

### 5.3 The Mechanical Transfer Step
**Mechanism:** Base Change via K-Theoretic Lagrangian Pullbacks.

To refute this, the domain expert must implement the Cao-Toda-Zhao pullback map within the computational representation of Substrate C.

1. **State Space Formulation**: Model the phase states of Substrate C as a potential function $\phi$ over a smooth stack $X$. Identify the derived state space as the derived critical locus $\mathbb{R}Crit(\phi)$.
2. **Matrix Factorization**: Represent the coherent phase structures as coherent matrix factorizations of $\phi$. A matrix factorization consists of a pair of maps between vector bundles such that their composition equals multiplication by $\phi$. The Grothendieck group $K_0(MF(X, \phi))$ captures the invariant essence of these phases.
3. **Shifted Lagrangian Identification**: Identify the intersection boundary conditions of the state space as a (-1)-shifted Lagrangian $M \to \mathbb{R}Crit(\phi)$.
4. **Execute the Base Change Pullback**: Apply the specific pullback map constructed by Cao et al. [cite: 6]. Rather than attempting to push forward raw states (which destroys coherence), use the Lagrangian correspondence to pull back the Grothendieck group of the matrix factorizations onto $M$. Because this map is proven to satisfy bivariance and base-change properties [cite: 6], the expert can safely alter the base scheme without losing the topological invariants of the phase structure.

### 5.4 Falsification and Sharpening Outcomes
**If the transfer succeeds (Falsification of the artifact's limit):**
The Grothendieck group of Substrate C's matrix factorizations will pull back cleanly. We will observe that the topological invariants (such as the simulated Donaldson-Thomas invariants of the phase space) remain perfectly constant across arbitrary parameter base changes. This proves that coherent phase structures *can* be preserved, falsifying the artifact's claim and providing a robust mathematical engine for quantum-state transformations within Substrate C.

**If the transfer fails (Sharpening the artifact's claim):**
If the physical instantiation of Substrate C introduces anomalies—such as non-compactness that violates the "fairly general hypotheses" required by the theorem [cite: 6], or if anomalous degrees of freedom appear in the (-1)-shifted Lagrangian that break bivariance—the transfer will fail. The topological invariants will fluctuate wildly upon base change. This will beautifully sharpen the artifact's claim, proving that while K-theoretic pullbacks work in pure derived algebraic geometry, the thermodynamic noise of actual computational substrate implementations permanently breaks the base-change symmetry.

**Filing Destination:** `PATTERN_K_THEORETIC_LAGRANGIAN`

---

## 6. Synthesis and Integration

The adversarial cross-pollination executed by the Moros automator reveals a profound thematic convergence in the 2025–2026 literature: **the application of advanced Category Theory and Derived Homological Algebra to resolve intractable computational bottlenecks.**

- Substrate A's performance limits are bypassed by mapping neural circuits to spherical monoidal categories [cite: 1].
- Substrate B's symbolic compositionality is rigorously grounded by recognizing ad-hoc bindings as Right Kan extensions [cite: 3].
- Substrate B's asymmetric hierarchies are mastered by replacing group equivariance with topological categorical naturality and Radon measures [cite: 4].
- Substrate C's phase coherence is secured under base change by leveraging K-theoretic pullbacks over (-1)-shifted Lagrangians [cite: 6].

By injecting these four patterns into `pivot\techne_frontier_synthesis_2026-05-25.md`, we transition the artifact from a disjointed taxonomy of substrates into a mathematically unified, categorically fluid architecture. The artifact is no longer just a descriptive document; it becomes a generative matrix for next-generation intelligence substrates.

**[END OF REPORT]**

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9q4cYf6RV_umgKvS5uoushzXPWvspTb9aPD3rJwS5FV7ElS4s1KWKXo4J0OSXJuLjEn00WX4OE6vUSECO9rmkiuYBvFi8IKKd7NvLuHR3K6UPjzkF)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYkuPFzO913Nsos6Th-GJtbxGzPJw2NjE6y1wDAf3xsrXwaS-vSG4oRzsyLgWZ4Qrb5saeQENyEO6dtsgj33ttFc8nQzVdl_MmkweNh2WOJX6NwIKoxvNuSE6Vp3lHoahw6y9kXY7HYd7EHcWj3ZSZSw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfTPk0cVHiuQH6akLymOzxHZ4bnoXPt4hYVYPO5-WO3iIIq397toTL4gKa3_igzbFfKJbLzLGPdmk-khyQt4RjmjEpNfSCz1piNQ6jKlaWXA4-dFCy)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcSOew9A4YpfgWZp5MgDFhORR8-crUWF9AkQ_mHLU-Tn7RU3WP7ohfIs2TcigyezB5aABVfQysM0NidOqAEbxuR0kNYSUchXQgDyxRsD6KITsKHeHajxY1)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIeqck9n0HvOioFRCJjIWfIw92VpPrO41YYWdH3T258a-rgF9T5vEM7RYdyhNVDOa77JNRj1cZbYCsosEPWBj8a0maOrq0-hegyi6etXQKHp_l7LQ2)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5ppe-_E4Vp-XvEF9jAIuV86qcZs3LYuw3kjyTPYpimXFMgTHGYs94U7jPys5_HqlnY-oZQdMl5VN-ZwN7VP3pae8UJKHR7GD8eSLyg2OigVnrYqeW)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMHDaG2IqdEXO8LziUl2v2f2Fc_p2fC7A9ARJymo-pJUCz6AVTysYfNyk7Nq7cf-Db3uq2IoYHDX43qpBH9Km2TzJekuEJLtJLlW_2ufRGvkuKwUaxiZQY)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaRvsUY6KCu0IUYVlMsUOz2xifyPjmD0u48qaitn6uTmQnnfIDuuBqt0HjiTKtgvScLyUOJ_1G2ZvxPEF4XjyjFoPVlAN7V45d7Cp80DhX9Gd1oXJO)
9. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6YxQEoGrJ4xq4zEDNwOkZbAwKiTuaX_LN4jbOVyM158xESuIeVVEZU5XrX7dBntqv43O31wm0gt33jPAM8RlMt7U6wNdfIObOJpPRegR_ycYP9ttcKnHEPYh65NC0_7w1VDbiEO8uKw==)


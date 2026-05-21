# T#78 Holographic tensor network correspondence (AdS/CFT)

**Pythia queue id:** 116
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdMaUlQYXBlY0tjV3VfUFVQc2F1TmlBWRIXTGlJUGFwZWNLY1d1X1BVUHNhdU5pQVk
**Elapsed:** 250s
**Completed at:** 2026-05-21T15:22:18.029708+00:00

---

# Holographic Tensor Network Correspondence (AdS/CFT)

### Key Points
*   **Fundamental Duality:** The Anti-de Sitter/Conformal Field Theory (AdS/CFT) correspondence relates a gravitational theory in a bulk volume to a quantum field theory on its boundary.
*   **Tensor Network Geometry:** Tensor networks, originally utilized to simulate quantum many-body systems, intrinsically exhibit geometric properties that mirror discrete spatial slices of AdS spacetime.
*   **MERA and Holography:** The Multi-scale Entanglement Renormalization Ansatz (MERA) provided the first concrete structural bridge (proposed in 2009) between tensor networks and AdS/CFT, though strict geometric mappings face sub-AdS locality limitations.
*   **Quantum Error Correction:** The AdS/CFT dictionary functions as a quantum error-correcting code (QECC). Holographic tensor networks, like the HaPPY code, explicitly demonstrate how bulk logical information is redundantly encoded into boundary physical qubits.
*   **Random Tensor Networks:** Averages over random tensor networks translate the calculation of holographic entanglement entropy into the partition function of a classical Ising model, effortlessly recovering the Ryu-Takayanagi formula.

### Layman Summary
The study of the universe often relies on finding mathematical bridges between seemingly unrelated areas of physics. One of the most famous bridges is the holographic principle, specifically the AdS/CFT correspondence. It suggests that a universe with gravity (the "bulk") can be entirely described by a flat, lower-dimensional quantum system without gravity (the "boundary"), much like a 2D hologram contains all the information of a 3D image. To understand exactly how this translation works, physicists have turned to **tensor networks**—computational tools originally built to study complex quantum materials. 

Research suggests that tensor networks naturally build a Lego-like discrete structure that mimics the curved geometry of holographic space. By arranging quantum building blocks (tensors) in specific hyperbolic patterns, scientists can reproduce key features of gravity, such as how information is stored and protected. This has led to the realization that space itself might emerge from quantum entanglement, acting like a giant quantum error-correcting code that protects the universe's foundational information from localized erasures. While exact models (like MERA or the HaPPY code) have some mathematical limitations when mimicking continuous space perfectly, newer approaches using random tensors and advanced symmetries offer incredibly robust toy models that continue to drive our understanding of quantum gravity.

---

## 1. Introduction to Holographic Duality and AdS/CFT

The intersection of high-energy physics and quantum information theory has generated some of the most profound theoretical developments of the 21st century [cite: 1, 2]. At the heart of this confluence lies the **Anti-de Sitter/Conformal Field Theory (AdS/CFT) correspondence**, originally conjectured by Juan M. Maldacena in 1997 [cite: 1, 3]. This duality proposes a striking equivalence between a \((d+1)\)-dimensional theory of quantum gravity in an asymptotically Anti-de Sitter (AdS) spacetime (the "bulk") and a \(d\)-dimensional Conformal Field Theory (CFT) living on its boundary [cite: 1, 4]. 

AdS spacetime is characterized by a negative cosmological constant and possesses a spatial boundary at infinity. The metric of this spacetime inherently exhibits \(SO(D-1, 2)\) symmetry, which is precisely the conformal symmetry group of a \((D-1)\)-dimensional CFT [cite: 1, 5]. This symmetry matching forms the foundational cornerstone of the correspondence [cite: 1]. The AdS/CFT correspondence operates as a complex dictionary translating states, operators, and dynamic processes between a strongly-coupled boundary theory and a weakly-coupled bulk gravitational theory [cite: 3].

A critical breakthrough in understanding this dictionary came with the **Ryu-Takayanagi (RT) formula** in 2006 [cite: 2, 4]. The RT formula relates a purely quantum information-theoretic quantity on the boundary to a purely geometric quantity in the bulk. Specifically, the entanglement entropy \(S_A\) of a subregion \(A\) in the boundary CFT is proportional to the area of the minimal codimension-two extremal surface \(\gamma_A\) in the AdS bulk that is homologous to \(A\):
\[ S_A = \frac{\text{Area}(\gamma_A)}{4G_N} \]
where \(G_N\) is Newton's gravitational constant [cite: 2, 6]. This profound connection implied that the fabric of spacetime itself is woven out of quantum entanglement [cite: 7]. 

To constructively understand *how* the bulk spacetime geometry emerges from boundary entanglement, researchers required discrete, tractable models. This necessity paved the way for the introduction of **tensor networks** into the study of holography [cite: 5, 8]. Tensor networks, long used in condensed matter physics to efficiently represent the highly entangled ground states of quantum many-body systems, natively obey the entanglement area laws required by the RT formula [cite: 8, 9]. Consequently, they have become the primary framework for constructing explicit "toy models" of the AdS/CFT correspondence [cite: 5].

## 2. The Multi-scale Entanglement Renormalization Ansatz (MERA)

The first explicit connection between tensor networks and holographic duality was formulated by Brian Swingle in 2009 [cite: 3, 10]. Swingle observed that a specific class of tensor networks, the **Multi-scale Entanglement Renormalization Ansatz (MERA)**, exhibited structural and geometric properties remarkably similar to the spatial slices of AdS spacetime [cite: 3, 11]. 

### 2.1 The Structure of MERA
MERA was originally developed by Guifré Vidal in 2006 as a computationally efficient variational method to approximate the ground states of gapless, one-dimensional critical quantum systems (CFTs) [cite: 3, 12]. Standard block-spin renormalization schemes fail to capture the long-range entanglement present in critical systems. MERA solves this by introducing two types of local tensors:
1.  **Disentanglers:** Unitary tensors that remove short-range entanglement between adjacent blocks of sites.
2.  **Isometries:** Tensors that coarse-grain the disentangled sites, effectively mapping the state to a lower-dimensional Hilbert space [cite: 13, 14].

Applying these tensors layer by layer produces a hierarchical, tree-like network. Working backward from the ground state through the layers of the MERA reveals a renormalization direction along the graph. Swingle noted that this scale dimension in MERA strongly mimics the emergent radial coordinate in AdS spacetime [cite: 4, 15]. Thus, the tensor network can be viewed as a lattice discretization of a constant-time slice of AdS space [cite: 4, 16].

### 2.2 Entanglement and the Ryu-Takayanagi Formula in MERA
In MERA, the entanglement entropy of a boundary region \(A\) scales with the number of tensor bonds that must be cut to isolate \(A\) from the rest of the network [cite: 16]. Because of the hyperbolic geometry of the MERA graph, the minimal cut through the network arches into the "bulk" of the tensor network, tracing a path that is geometrically identical to a geodesic in a discretized hyperbolic plane [cite: 4, 16]. 

This means that the number of cut bonds (the tensor network entanglement entropy) naturally obeys the relation \( S_A \propto \log(l) \) for a region of length \(l\), completely mirroring both the CFT entanglement scaling and the Ryu-Takayanagi formula [cite: 16]. The discrete paths in MERA essentially become the minimal surfaces of the holographic bulk [cite: 4].

### 2.3 Consistency Conditions and Limitations of the AdS/MERA Correspondence
Despite the compelling parallels, the notion of a strict "AdS/MERA correspondence" faces significant physical constraints. In 2015, Bao, Cao, Carroll, and collaborators published a rigorous analysis of the consistency conditions required for MERA to perfectly model AdS/CFT [cite: 4, 12]. They evaluated whether the MERA could simultaneously satisfy the geometric features and entropy inequalities expected in a bulk gravitational theory [cite: 12, 17].

Their findings identified several structural limitations:
*   **Sub-AdS Locality:** The simple MERA graph is unable to resolve physics on length scales shorter than the AdS radius. The lattice spacing in the bulk of the MERA is inherently tied to the AdS scale, meaning the network can only describe super-AdS physics [cite: 4, 12].
*   **Covariant Entropy Bound:** By applying the Bousso covariant entropy bound to bulk regions in the MERA lattice, the researchers demonstrated that no conventional combination of MERA parameters (e.g., constant bond dimensions) could consistently reproduce bulk physics [cite: 12, 13].
*   **Symmetry Breaking:** MERA imposes a preferred slicing and breaks the continuous symmetries of the bulk spacetime. Standard MERA does not trivially support the full continuous conformal group of a CFT [cite: 14, 18].

These constraints indicated that while MERA is profoundly related to holography, the simplest version of MERA is not an exact realization of AdS/CFT [cite: 11, 19]. Generalizations, such as the Continuous MERA (cMERA) or incorporating auxiliary bulk degrees of freedom (entangled ancillae), are required to build a more robust correspondence [cite: 12, 19].

## 3. Holographic Quantum Error Correction (HQECC)

Following the realization that tensor networks model holography, the focus shifted to understanding *how* information is encoded. In 2014, Almheiri, Dong, and Harlow demonstrated that the AdS/CFT correspondence possesses the mathematical structure of a **quantum error-correcting code (QECC)** [cite: 3]. 

In a quantum error-correcting code, logical quantum information is redundantly encoded into a larger number of physical qubits to protect it from localized errors (such as the erasure of physical qubits) [cite: 20, 21]. In holography, the bulk theory contains "logical" degrees of freedom, while the boundary CFT constitutes the "physical" qubits [cite: 22]. 

### 3.1 Bulk Reconstruction and Erasure Correction
A key feature of AdS/CFT is **entanglement wedge reconstruction**. If a boundary observer has access only to a subregion \(A\) of the CFT, they can theoretically reconstruct any bulk operator that lies within the entanglement wedge of \(A\) (the bulk volume enclosed by \(A\) and its minimal Ryu-Takayanagi surface \(\gamma_A\)) [cite: 22]. 

This is structurally identical to erasure correction. If the rest of the boundary (region \(A^c\)) is erased or lost, the information located deep in the bulk (within the entanglement wedge of \(A\)) remains fully accessible [cite: 21, 22]. Bulk information is redundantly distributed across the boundary, meaning that a local operator in the center of the AdS bulk maps to a highly non-local, highly entangled operator on the boundary [cite: 23]. Holographic tensor networks operationalize this concept, providing explicit, computable models of quantum error correction [cite: 1].

## 4. The HaPPY Code (Pastawski-Yoshida-Harlow-Preskill)

In 2015, Pastawski, Yoshida, Harlow, and Preskill introduced the **HaPPY code**, the most celebrated and explicit realization of holographic quantum error correction using tensor networks [cite: 20, 24]. The HaPPY code moves beyond the variational nature of MERA to create an exact isometric mapping from the bulk to the boundary [cite: 14].

### 4.1 Perfect Tensors and AME States
The foundational building blocks of the HaPPY code are **perfect tensors** [cite: 20, 23]. A perfect tensor is a tensor with an even number of indices that acts as a proportional isometry for any bipartition of its indices into a set \(A\) and a complementary set \(A^c\), provided that \(|A| \le |A^c|\) [cite: 25]. 

In the language of quantum states, a perfect tensor corresponds to an **Absolutely Maximally Entangled (AME)** state [cite: 25, 26]. For a system of \(n\) subsystems, an AME state has the property that any reduced density matrix of up to \(\lfloor n/2 \rfloor\) subsystems is maximally mixed [cite: 25]. 

The most common variant of the HaPPY code uses a 6-legged perfect tensor based on the \([[cite: 1, 22, 27]]\) perfect stabilizer code [cite: 20, 26]. The \([[cite: 1, 22, 27]]\) code encodes one logical qubit into five physical qubits and can correct any single-qubit error [cite: 20]. The 6-legged tensor places this logical state in the center, acting as a mapping from one bulk logical leg and five boundary legs [cite: 20].

### 4.2 Hyperbolic Tessellation
To build the HaPPY code tensor network, these perfect tensors are tiled across a discretized hyperbolic plane [cite: 20, 24]. The network is constructed by placing the 6-legged tensors on the tiles of a regular hyperbolic tessellation (such as a purely pentagonal tiling, or alternating layers of pentagons and hexagons) [cite: 20]. 

Adjacent tiles have their tensor legs contracted (glued together). At each tile, one leg remains uncontracted, pointing "upward" out of the plane; these represent the **logical bulk qubits** [cite: 20, 22]. The legs at the outermost layer of the network remain uncontracted and represent the **physical boundary qubits** [cite: 22]. This forms a global encoding isometry that maps the entire bulk Hilbert space into the boundary Hilbert space [cite: 20].

### 4.3 Successes of the HaPPY Code
The HaPPY code successfully captures numerous qualitative features of AdS/CFT:
*   **The Ryu-Takayanagi Formula:** The code provides a well-defined, exact discrete analogue of the RT formula. The minimal cuts through the network perfectly trace the entanglement wedges [cite: 24, 28].
*   **Complementary Recovery:** The code explicitly demonstrates how bulk operators can be reconstructed on the boundary. Through a "greedy algorithm," a bulk operator can be pushed through the network towards a boundary subregion, as long as it lies within the subregion's entanglement wedge [cite: 22, 26].
*   **Majorana Dimer Formulation:** The Hamiltonian of the pentagon HaPPY code can be elegantly expressed in terms of mutually commuting weight-two Majorana operators, allowing for exact computations of boundary properties [cite: 1, 20].

### 4.4 Limitations of the HaPPY Code
Despite its mathematical elegance, the HaPPY code has limitations when compared to continuum AdS/CFT [cite: 24, 29]. 
*   **Trivial Correlation Functions:** Because perfect tensors induce maximal entanglement locally, the resulting boundary states of the standard HaPPY code do not exhibit the algebraic polynomial decay of correlation functions expected from a true CFT [cite: 24, 29]. Instead, correlation functions often behave trivially or exhibit artificial rigidity [cite: 29, 30].
*   **Discrete Symmetries:** Like MERA, the HaPPY network inherently breaks the continuous rotational and translational symmetries of AdS space due to its fixed lattice structure [cite: 5].
*   **Finite Cutoff:** The code operates most naturally as a finite network, whereas the boundary theory in AdS/CFT possesses an infinite-dimensional Hilbert space requiring rigorous renormalization procedures to define the infinite limit [cite: 24].

## 5. Random Tensor Networks (RTNs)

To resolve some of the rigidities and limitations of the perfect tensor models, Hayden, Nezami, Qi, Thomas, Walter, and Yang (2016) introduced **Random Tensor Networks (RTNs)** [cite: 8, 31, 32]. Instead of constructing a network out of highly constrained perfect tensors, they proposed using tensors whose elements are chosen randomly and independently from a Haar distribution [cite: 9, 33].

### 5.1 The Ising Model Mapping
The profound insight of the RTN approach is that calculating the entanglement properties of the network—specifically the Rényi entropies—after averaging over the random tensors maps precisely to calculating the partition function of a **classical ferromagnetic Ising model** living on the same network graph [cite: 8, 32]. 

In this mapping, the boundary conditions of the entanglement region act as fixed spins on the boundary of the Ising model [cite: 8, 32]. The classical spins in the bulk align to minimize the energy of the system. The boundary between domains of opposite spin directions (domain walls) in the Ising model physically corresponds to the minimal surface in the tensor network [cite: 8, 32]. 

### 5.2 Exact Recovery of Ryu-Takayanagi
In the limit where the bond dimension \(D\) (the number of states on each internal leg) of the random tensors becomes very large, the RTN models flawlessly obey the Ryu-Takayanagi entropy formula [cite: 8, 32]. Unlike earlier models, this holds true for *all* boundary regions, whether they are contiguous or disjoint multi-partite regions, establishing a deep link to the multipartite entanglement of assistance [cite: 8, 32]. 

### 5.3 Bulk Entanglement and Corrections
Continuum AdS/CFT dictates that if there are quantum fields in the bulk possessing their own entanglement, the RT formula requires a quantum correction (the Faulkner-Lewkowycz-Maldacena correction). RTNs naturally incorporate this [cite: 8, 32]. By including an analog of a bulk field (uncontracted logical bulk legs in the RTN), the minimal surface calculation is modified [cite: 8, 32]. 

The classical Ising model is effectively subjected to an external magnetic field generated by the bulk entanglement. The model seamlessly reproduces the expected corrections: the minimal surface is physically displaced, and the total boundary entropy is augmented by the bulk field's entanglement entropy [cite: 8, 32]. Furthermore, if the bulk entanglement is increased sufficiently, the minimal surface's topology changes dramatically, perfectly mirroring the Hawking-Page phase transition associated with the formation of a black hole in AdS space [cite: 8, 34].

### 5.4 Holographic Coherent States and Superposition of Geometries
Random tensor networks also established the notion of **Bidirectional Holographic Codes (BHCs)** [cite: 9, 32]. The network acts as an isometric map from a defined "code subspace" in the bulk to the boundary. Expanding on this, Qi and others showed that RTNs allow for the description of quantum superpositions of geometries [cite: 35]. By introducing quantum link variables, RTNs on various geometries form an overcomplete basis of "holographic coherent states" for the boundary Hilbert space [cite: 35]. The overlap between distinct spatial geometries is suppressed exponentially by an area law, completely consistent with the expectations of quantum gravity [cite: 35].

## 6. Advanced Tensor Network Models and Symmetries

While RTNs solved the issue of flexibility and bulk corrections, discrete tensor networks on regular lattices still struggle to exactly replicate continuous CFT properties. Recent research has focused on overcoming the symmetry-breaking artifacts of the lattice cutoff [cite: 5, 18].

### 6.1 Quasiperiodic Conformal Field Theories (qCFTs)
Jahn, Eisert, and others (2021) demonstrated that while tensor networks on regular discretizations of AdS break continuous bulk symmetries, their geometry enforces a discrete subgroup of conformal symmetries on the boundary [cite: 5, 36]. This leads to the definition of a **Quasiperiodic Conformal Field Theory (qCFT)** [cite: 5, 36]. 

A qCFT is a critical theory that is less restrictive than a standard CFT, characterized by multi-scale quasiperiodicity on the boundary [cite: 5, 36]. Holographic code states, such as the Majorana dimer models, can explicitly realize AdS/qCFT models yielding exact fractional central charges [cite: 5, 18]. This paradigm of "discrete holography" establishes rigorous connections between exact quantum error correction, critical condensed-matter models, and strong disorder renormalization groups [cite: 18, 36].

### 6.2 Hyperinvariant Tensor Networks and Evenbly Codes
To rectify the trivial correlation functions of perfect tensor models, physicists have developed **hyperinvariant tensor networks** [cite: 26, 29]. A hyperinvariant network maintains a more fluid geometric structure that doesn't rigidly lock the entanglement into maximal states [cite: 22, 29].

A recent innovation is the **Evenbly code** [cite: 26]. Building on hyperinvariant concepts, the Evenbly code uses non-perfect tensors describing CSS (Calderbank-Shor-Steane) codes interspersed with Hadamard gates [cite: 26]. Placed on hyperbolic \(\{p, q\}\) manifolds (where \(q \ge 4\) is even), these models form subsystem codes with tunable rates and distances. Crucially, modifying previously proposed hyperinvariant models into quantum codes has been shown to successfully produce the correct algebraic decay of boundary correlation functions matching a critical renormalization group flow, bridging the gap that the HaPPY code left open [cite: 26, 29].

### 6.3 Additional Holographic Code Variants
The "Quantum Lego" approach has spawned numerous specialized holographic codes [cite: 22]:
*   **Analog surface-code and cluster-state codes:** Using continuous-variable (CV) AME states for continuous tensor networks [cite: 25].
*   **Galois-qudit GRS codes:** Used to construct *p*-adic AdS/CFT representations on Bruhat-Tits trees, expanding holography into discrete number fields [cite: 22, 37].
*   **Hamiltonian-based codes:** Tools from Hamiltonian simulation theory map local CFT boundary Hamiltonians into the AdS bulk [cite: 22].

## 7. Emergent Gravity and Informational Nonequilibrium

The ultimate goal of tensor network holography is to mathematically prove that gravity itself is not fundamental but rather an emergent phenomenon of quantum information [cite: 4, 7]. 

Recent literature connects the lattice resilience of quantum error-correcting codes to informational nonequilibrium processes [cite: 7]. In models refining these concepts, researchers utilize the First Law of Entanglement Entropy. By applying Wald entropy formalisms to the entanglement structure of conformal field theory toy models (represented by tensor networks), one can derive the **linearized Einstein equations** entirely as consistency conditions of the entanglement network [cite: 7]. 

This implies that the gravitational dynamics observed in the bulk spacetime are the macroscopic manifestations of the boundary QECC striving to maintain its error-correcting properties (informational equilibrium) [cite: 7]. Such frameworks suggest that local perturbations in the network (errors) manifest as spacetime curvature, offering a natural ultraviolet cutoff and a theoretical pathway to singularity-free gravity [cite: 7].

### 7.1 Approximate Quantum Error Correction and "Quantum Noise"
While exact error correction like the HaPPY code is beautiful, continuum AdS/CFT is recognized to be only an *approximate* quantum error correction code [cite: 21]. In exact QECC, operators can be reconstructed perfectly. In approximate QECC, a logical operator "leaks" slightly into erased subregions, making perfect reconstruction impossible [cite: 21].

Studies by Charles Cao and others into tunable approximate holographic codes inject "quantum noise" into holographic stabilizer codes [cite: 21]. Fascinatingly, this deviation from exact error correction gives rise to features directly analogous to gravitational dynamics. In this context, "noise is a feature, not a bug," providing the exact physical mechanisms needed to transition from rigid spatial geometry to dynamic spacetime [cite: 21].

## 8. Summary Comparison of Holographic Tensor Network Models

| Model | Primary Tensors | Boundary Correlations | Entanglement RT Formula | Key Feature | Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MERA** [cite: 3, 12] | Disentanglers & Isometries | Algebraic decay (CFT-like) | Yes (via discrete geodesics) | Efficient ground state approximation | Breaks continuous symmetry, Sub-AdS gap [cite: 12, 14] |
| **HaPPY Code** [cite: 20, 24] | Perfect Tensors (AME states) | Trivial / Rigid | Exact | Explicit bulk-to-boundary isometry, exact HQECC | Trivial correlations, lacks dynamic Hamiltonian [cite: 24, 29] |
| **Random Tensor Network** [cite: 8, 32] | Haar-random tensors | CFT gap spectrum | Exact for all regions | Maps to Ising model, simulates black holes and bulk fields | Statistical average required, relies on large bond dimension limit [cite: 8, 32] |
| **Evenbly/Hyperinvariant** [cite: 26, 29] | Non-perfect CSS tensors + Hadamard | Algebraic decay (CFT-like) | Exact | Tunable code distances, restores physical CFT correlation functions | Highly complex tensor contractions, subsystem constraints [cite: 26, 29] |

## 9. Conclusion and Future Directions

The study of holographic tensor network correspondence has fundamentally revolutionized our understanding of the AdS/CFT duality [cite: 1, 16]. Starting with Brian Swingle's observation that the MERA tensor network mirrors AdS space [cite: 3], the field has rapidly expanded. The introduction of the HaPPY code proved unequivocally that the holographic dictionary is fundamentally a quantum error-correcting code [cite: 20]. Furthermore, Random Tensor Networks provided the statistical mechanical scaffolding to recover the Ryu-Takayanagi formula naturally from domain walls in an Ising model, seamlessly accommodating bulk entanglement and black hole transitions [cite: 8, 32].

Current research is pushing beyond static spatial geometries. The integration of approximate quantum error correction [cite: 21], quasiperiodic CFTs [cite: 5], and hyperinvariant codes [cite: 29] is bridging the final gaps between discrete lattice toy models and continuous gravitational theories. Looking forward, these models are moving from theoretical abstractions to potentially verifiable hypotheses, with proposals to utilize AIoT interfaces, quantum computers, and precision clock networks to observe the "holographic noise" arising from the discrete error-correcting structure of spacetime itself [cite: 7]. Tensor networks stand as our most promising mathematical microscope for uncovering the informational fabric of quantum gravity.

**Sources:**
1. [fu-berlin.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEG9uL-_ZYzjeT-qtlBtNHAphkoRXCTbQD0fXXhO8V9dxmzFjhav7CfSHoYMYR-gbvEJJqsGoovPklrATXzqiDJS3c3_Z0jqBnvYWW8sY6pQgwpaop8ofm5j5RbGhJbE1O-Kc4VWiZT3O8YMhZ5xSqSTvLPgdWxDIa4ldhw0MuUal2DuMbqmQvhcb3aJHeiQskbWjrJAB4=)
2. [quantumzeitgeist.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfoVhfLe9bvGEAXxYigL0YORST5janabAuje5sfScn4X2O9tFDQKtn5c6dXbcBkCsKnIsTOxOrGMuLCMyf9KdOvMqpYtGFqCjh3c-QQLf5ynfU7U57R2dd4puqXuOIq0B2xZ8QGa3A8p55xyJ8LaOgrkq5WW-qzztHYwNBP7ZQDDy4WS12_Lan_t-e9X5Kg5Qg7rbNMpteKXdE6eQJByZH4c-XW1IMrrYtehQ=)
3. [scottaaronson.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEyiVdehJpcPtzS1LYRP39Bxe16PWH6qaQ2ITO3meyxN3sEFR7d_iaSHM0FkBN6eZ_Q_M_adGUxWzwQymcsAXcRUhkKS9jPuCN3tYHnnH1JfO9CZFoyry2fJ1AAU5ZDggSfNxLRw==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgpP4Z_gDSW4aZE2VTQ_yFKrGEU2ToCPUm9J8eDtPO1WoH54jReqejpucMHt3rWXR4ywxUpM1cDZLlx-S2hicYzVfKKtpXy87xkyViwHg28vpqq2pd)
5. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMgC9uZ8WlecM6Saob883jZtrcQyDsBlM2Dv3Q8NfyaBh5WZZRgi8kBWTPYJrWIzH290P1Wvvl-llFeUEteHskIKOeHGEEIXDpq6qr7A79C4OwFNoziXHyOrHBHdNavWGzbQwh1z1kXM8=)
6. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJIv5A2lFG_KwCPMWleJ6pOHodjtwOCV2Q-_sQGursweku3f9thBuQgYMy__xYO0NfSkRZ7ybhtBVnOpSxCsFGwJ5oLScYzok9Oblg7b-6aTI6J42BkDR71dXo1nAuaRB3zwaki5mL)
7. [scirp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8WiockW1_WD9V5Z5AKVVqwMRwWEahPvbC5MsbMN2CppjEKpOQF5mvlWRh2CzuDvGzSolVHF0NylP7eJv20s_Q_Eht3Hs8IHzEgxyKSTeIOsMewwoE74vOp-4YeLf6XRkyJJ07FD9edTZVnm49NMNbT3Q=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-eLu2tzCeYDGadFfHIzYVqt2U3zxZG3mfuinA68ofX-tASgoh-4wmO-QXlp3ZuU52oV5q7aUSSUnc-gCD7jLMR66K6McojjXtduSi4HL1dZZhJ8UI)
9. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEL_YZ-dW4-Vm3NRij2knj7kGylaPN1kapJDNFUhdIjkDE1FhOhaSY59GQ89YqTKi3xBOzKyde_tHSymvC6GOc2L2ylrDIZLllF-ZlxwneTUDhgkjVwAYm89Aj5DtJ_6h9OhPmP0tLWL2zUjuAujtHjNV6-WkfBAzO8D8bWovGG91o)
10. [perimeterinstitute.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyJXvpyh0KFlWSTzvkRKnxlA17mrkBkcvfoCaIyQnzwzjkuwW9cq23E7-pKAZLtBTPrc5rLzXRkoNsMW1Ot6hFiI3728gAGPsaBv8wDSTvOjGmXdk-SoukI6zo_alnWbidop0rPBTV8IhQWjxrPnskqI6reYMaAJg=)
11. [quantumfrontiers.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUXX2aBouQJl_6SJMm9j3G6VtopiniQl1rG9f6gpzACxlslW4giT0gmmjfatWy5fVAoqEXtpIFLI0mFFxXTmd1-0EPq3FTgteUoceqFzgBEYkHJnAlpWVyFQAO90BD7yLJXaUHHfphBS55y17YhMOk49a-KcU=)
12. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEM7fJ0aJUVWOXEGTj8W392k0Tj25js_KmcLXvtYVkW2tUcFdNwUa9RC4BnjdHHCM24XOZfa59ZlMhAPS56RaR8i764-UowH_3PapIB40rwgnmBaXIFdGrsvnyhQ9OAMCNfPFhmnvHnQnYx5pKHnrjIVqOiwuG2yHIJIYOjarXbg1kZF_sVQx0MiY25DZl50qftRgtHAyXtSdbKMlwNK4rKmzux5hvWmw8ARQt2nMh-MuuNPuTliwSLtKfFjAXmjjE=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ0O4eghRfnkXLz8L5T5Lwv_nSrWiiRCCk7Hi_Ck3ZuQi0E5N6rH0mMHbDahJNYv7NGoxWjoyR0v-zoTrPnjSmaz4RLrjgTFW4cl5S_fj11vNSX4lfrCBGCTHnIdWixroN6o3t6Y-_Djm4ziPHNHKNdtZwDJIoM7qPzdvJB4Ep1jlztTE3qkhT2lf_7Hiqkesg9cOBVhxb92EyU-w=)
14. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFzs0EttxQofr-FBYYpSL7k8oN1wd37Mdeswxwy9a_lJ9WoPzC7Cv1Zl3wJ70KWrl5kcROg174QGYEGPYzTfNiKuwGcCqgmIiZ9TRA2v0A5GzrNdaK_AGfW4PrBgIAcc7irrgWiTae1FAWTyYQhJSmBdwq8sI9swsemGP0ubtbKyKjkYyFYM851zXrIA==)
15. [preposterousuniverse.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7lwl5YeKY8wr3Z5PZjNyQRbgym1oz9bH7ZvZhzSF_1rMug5zlfcc8Fqa7RWagiiB6alv-tB-5ihKZqKr7qyPnUJ3buthzBPAOmMOzdXPJWbGNlOnebc_Lg7xGA63f32pBqrOpiOTuJ3TxseazOn35bzkBkeNNYWqph-x37Znv06IOMzQFZQM0ovgENbQ17ImidbkaU_dc9tVIIOojMu43wTT9n_99WrU=)
16. [henryyuen.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSL2oT9QJtsh4iWeutW-JdigOBZySLJ2oCUOh1ucVHPyv4PiCfm1iAfYrqMHQ1ol1DHhBGyRJxS3adjwC-bnfpqc4L0pRW-sH93qcEy59iH1bbDYmpBmUPigUFZAHg-M0PkPHfQND5zSYMGKncd4MzY7HTVdo=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPr-UbdqXfsnDMyRnyRkLOD4pgpA3663HAwLfhqdI_PwdnuopKP5PiMHlOnWyOLpnlfutU3kZndb-cRlqpV6JB3XTnXWsnmUSOD5g3lOkLyyBE1r1n)
18. [pirsa.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFldsgEZZGjVSvHFATM2ozu4AM3vOjeV6bg0oP4pe7_dI42l8qwk-eOLcgsu4QbmwXud6omt9eJooNcG2fhM1iElJx7xhfN9hbv7GIxy2IN)
19. [indico.global](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtRLCYqcmbCycdyMdUcQEP4Wf7vMRftIfO5j2NYV7lgVCBhhNgV2NTFfhFFT6PLtPlAKip1aM-ttE6-rJ6u7oCc5pioj5BO1pofpkhaJMn_h-Db-3Hkr92p_1i9kYCuRZmwavGDxS7Wi-ceMIszVRHVdPPy4ADG7awxR4IMSc_F69cjB9CXWkyQOqQFij_ujTRCAhfjdI=)
20. [errorcorrectionzoo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_2Vp6oWtidiu5733a7DFNv1HhsGPo1rBS_5I007frz4VEA2EYyxhTqvNu9UIkYyVEfs3tuRghMiIFb4ce2eRalhu8CWByLYBwTYKcqWGfhD2aPuANUtOZiVys)
21. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEE6gHW3uP6VByO7ED2JxKLoSFbKANh7ns9QULnqMSkiIFQL15GNd73FRcghJz9xLvia0DbplWHye7v8Lr2aw3yqwUeOq10sbV4Jz1YVmaqrvXnAQSOOyscto7QAdnvMec=)
22. [errorcorrectionzoo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENtJ77bRi8wIPyX3-z_W55UInrgGvcPznjW6YTMSkPX9hEW8N5MGsUFgJrcv9nGAooqLwMXR3mjznL8FIZvmRUfVdlHEwYC2Zve4x_y0HNf1BLethHxwOlOlduks-mUg3x6qR3DOuOZQ==)
23. [tgdtheory.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg0Lug_3x8ZKud8Z-N0J6FfyK1CNbDkH8bb7jpMfcpdl20TI_1ozj-b-MBYIqeAhQwTrQGS2VRoYjN4dIcZ1K4TPWippCBVtcNypdxpYyghdZKH0AgTvqlJTkWVuKXaA==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO9VxCMi3kiFLYUtP8QXa9doxKP36xzzV4ykAgiUVEf8t6V3WqSmn6dTvjo2t7D-hVjNHhcUfTykrxD_YK116yzIS0yr_YcEJmogtpsENOp_2sjp9h)
25. [errorcorrectionzoo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjt8bclk7OCf8_MrLHq8SNIFKz4oOt1cFdPV5i3oZUN3K70OR-RZSp9fm3GIvdkeK4SDPO68e7mFj7j6PgaNup7AtqF4Ewk-rz_NEvYqV57JZvxtSHxYVIkw==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0CUJf0qNzigHc8ZUmhaM4fu_F2wk_OAyBayp0SdGyr_CqaocjI-2Z5nhgZDVLsJvDSee72wyjXY49jUyH89ys-lEiwFqA1S1ZYXL6x_ovpNZK35SR8SWM)
27. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKTtsd6kvRbp4iCuArOUo66z-XklB3p0qMes2g1C53Y0MoBTJWul_cg4M67wqTneAg7S653vbfT01B3Xl2H38XDbL6ekfRJ91tqPkxpdPW1Ck3Qks4-4FHl_r7cWi98Hk42aCLSJK2aKa2KK6uOIgPVPlO212a-ZzwlEbetMUhxUM1sJwI4do3o2zl7WBr0Kbrdf-cyK_l3eoZpU9WQbf509LfsnuezkzWAvIpLnvQEVR6mKwMy0Mpvc1NWETV)
28. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELe4bPVpoxvy-gAhVakIQNsjFGvGR-ZoobJEkhp313L2vWpMp5ooylBhimo7MiEPhBLyRPfxUfA1rJj7e1bgg0TEuItaRHuFAsTx5SYoVnkwl8LeJc4FAohuF2M5M=)
29. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEks4hi_Zyb0_ZVmak8sKRU2NcM0cM2TtfIxMlQvy_yTwTG1RqzRQ3wSGwDMAzRp5Y1sVxkZyOOuwQrFK0qJwgORzkAF8e-6RW3D5IL9rZA-ZIYb5S75VV6CRyYlQ8EBYHNNCSa6m8S)
30. [ticmeet.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdU7HgI-GEc703U99iY-BCsZEQbtmVuydrg98k79aO9XTkzLKtZP2rQ8tdUvl7EqahjbpO1924DpLFfndf0FHbDp6vp_DP8tUi1XO8TVvdh2Ozq9hzRprAnhumYwYmN2pHlXMOkGI80I6FJTCtm_BgshE-MXFg-SVRehzwkfJ75-oruQubBA68KFQ-xw==)
31. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpNPDIcxxJh8Lx4yFmrGJn_ROzU2W-0N9bDgNoqfrHaFaMZ_I4vvq4pJW2HzvkTUnWHcyAyg5huw2HIPxfR_k8x7gC7KkswrhiqjJYVJ-UNCzzfVQ2PNX4khcLsRWFBIk=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPDZGBgnS2fmb0nxoBCQSUQ7HiYvd8RYcJM1dQB7Llq9ytCFPd37VAnyC5NiLdd22ZIu2shDNZFdar67vnbuvXrTy9DR86-SrWH9ejyQ3swe84IitNDcIkf1eYjK7cdI7w)
33. [michaelwalter.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHAkyYLMaQtOsreo_-kghYLPqhCTyDW3zaJXdrd6d_94_R77pRLrgTbGVgdONxKzVLNCfBzzSxyO4ph7JRzUQ-u0JAY1JagB7hTmSDXvqqICUWRZki65ChWhhOwZ0HWC0mO6SEFGmHGMGWb6GnCX8=)
34. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdsYF8uMSrRfCga9F68Ugm-3Fb3wrnFv4kJRYzK_DDQAt3lC1CySjbWGdKrY56eOtsoLG6PjzKogSufTicV3Tg1RhTcRF4VZNfhs3FqrDb7QmnEN1HH66F7_m7GB4kFtrLlnnIN3MZpetS-heDv-OgkGMsuiaQ5I0CGzHjsP1Irjg_5lqumlWVEqE_qJCXuQx5yGGfN7Uw)
35. [pirsa.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6jqq-KIqTiBUXkJstuvz5pz_nHKI6GxbU0nJCQfcRqCcN0Y8ysVtn-fBWzDgmYsf_EgT_-xIT41WpaoqvBJNVu9BzM5U69ehkE04KrFLu)
36. [mtak.hu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGd3j94yvIR6NCz2JNjzxjEBIUF7lic9Yw8qlEF9OM-vBMhr7knXtkh2zS3aURS8x-WbKnjAgjF_zKGTttkK3ubQEJCWjEypu6o5UVQTzGbKrCGxUK35w0ySfEq4Pz4aSHfUPE=)
37. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwKmtm2ECueDB2EQsj6XZTm7GEpSvz9oNsEo7ILvGBeYamFY4yFycvKVdKnfgnG1N2k4dGs_8kdc25nfGGlFWV_33UkQabrG0cmuNx5Z6eYF9YrTAymJffqnAhMPrEnrFm)


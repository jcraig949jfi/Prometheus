# T#33 Singular loci of border-rank varieties (Holweck-Oeding)

**Pythia queue id:** 79
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd2c0FQYXFpQ0RyUEdqTWNQb00tcW1RNBIXdnNBUGFxaUNEclBHak1jUG9NLXFtUTQ
**Elapsed:** 2090s
**Completed at:** 2026-05-22T03:09:28.712346+00:00

---

# T#33: Singular Loci of Border-Rank Varieties and the Contributions of Holweck and Oeding

**Key Points**
*   **Border-Rank and Secant Varieties:** In algebraic geometry and multilinear algebra, the set of tensors of a specific border rank corresponds to the secant varieties of classically embedded varieties, such as Segre or Veronese varieties. The geometry of these spaces is fundamental to understanding tensor decomposition.
*   **Singular Loci of Secant Varieties:** Determining the singular loci of these border-rank varieties remains one of the most notoriously difficult open problems in algebraic geometry. While it is known that the $(k-1)$-th secant variety forms a "trivial" singular locus of the $k$-th secant variety, identifying non-trivial singularities requires highly advanced techniques.
*   **Holweck and Oeding's Contributions:** Frédéric Holweck and Luke Oeding have significantly advanced the field by bridging invariant theory, representation theory, and quantum information. Their breakthrough works include computing hyperdeterminants from the exceptional Lie group $E_8$, establishing Jordan decompositions for tensors, and calculating hyperdeterminants on fermionic Fock spaces.
*   **Quantum Entanglement and Geometry:** Border-rank varieties directly correspond to classifications of quantum entanglement under Stochastic Local Operations and Classical Communication (SLOCC). Algebraic invariants, such as hyperdeterminants, are utilized to distinguish between different entanglement classes, such as GHZ and W states.

**Overview of Complexity and Uncertainty**
Research suggests that finding exact polynomial generators for the ideals defining higher border-rank varieties and their singular loci suffers from severe computational bottlenecks, with symbolic elimination methods exhibiting doubly exponential worst-case complexity. It seems likely that the full classification of non-trivial singular loci for arbitrary tensor formats will remain incomplete without the integration of novel theoretical frameworks (such as border apolarity and cumulant coordinates) and advanced numerical or machine-learning-based interpolations. While the mathematical community has achieved exact classifications for small tensor formats and specific geometric loci, the broader mapping of these algebraic boundaries remains an active and highly complex area of study.

---

## 1. Introduction to Tensor Rank, Border Rank, and Secant Varieties

The study of multilinear algebra frequently concerns the decomposition of tensors into fundamental, rank-one components. While the rank of matrices (order-2 tensors) is well understood through classical linear algebra and singular value decomposition, higher-order tensors exhibit far more complex behavior. The mathematical framework used to investigate these higher-order properties relies heavily on algebraic geometry, where spaces of tensors are stratified by secant varieties.

### 1.1 The Definition of Tensor Rank and Border Rank
Let $V_1, V_2, \dots, V_d$ be complex vector spaces. A tensor $T \in V_1 \otimes V_2 \otimes \dots \otimes V_d$ is said to have rank $1$ if it can be written as an outer product of non-zero vectors: $T = v_1 \otimes v_2 \otimes \dots \otimes v_d$. For an arbitrary tensor $T$, the tensor rank (often referred to as the Waring rank in the context of symmetric tensors, or the canonical rank) is defined as the minimum integer $r$ such that $T$ can be expressed as a linear combination of $r$ rank-1 tensors [cite: 1, 2]. 

However, unlike matrices, the set of tensors of rank at most $r$ (for $r > 1$) is generally not closed in the Zariski or Euclidean topology [cite: 1, 2]. This topological openness leads to the crucial concept of **border rank**. A tensor $T$ has border rank at most $r$, denoted $\underline{R}(T) \le r$, if $T$ can be arbitrarily closely approximated by tensors of rank $r$. Equivalently, $T$ has border rank $r$ if $r$ is the smallest integer such that $T$ lies in the Zariski closure of the set of tensors of rank at most $r$ [cite: 1, 3]. 

The distinction between rank and border rank is not merely a mathematical curiosity; it is a profound feature of tensor spaces that severely impacts computational complexity and quantum state classification. For example, in a 3-qubit system ($C^2 \otimes C^2 \otimes C^2$), the generic rank is 2, and the generic border rank is also 2. However, there exist specific tensors, such as the W-state, which possess a tensor rank of 3 but a border rank of 2 [cite: 4]. This strictly sub-multiplicative behavior of border rank is a central object of study in the complexity of matrix multiplication (e.g., Strassen's laser method) [cite: 5].

### 1.2 Secant Varieties as Border-Rank Varieties
In projective algebraic geometry, the set of rank-1 tensors modulo scaling forms a projective variety. Depending on the symmetries of the tensor space, this variety takes different forms:
*   **Segre Varieties:** For general tensors in $\mathbb{P}(V_1 \otimes \dots \otimes V_d)$, the rank-1 tensors form the Segre variety $\text{Seg}(\mathbb{P}^{n_1} \times \dots \times \mathbb{P}^{n_d})$ [cite: 6].
*   **Veronese Varieties:** For fully symmetric tensors (homogeneous polynomials) in $\mathbb{P}(\text{Sym}^d(V))$, the rank-1 symmetric tensors form the Veronese variety $\nu_d(\mathbb{P}^n)$ [cite: 7, 8].
*   **Segre-Veronese Varieties:** For partially symmetric tensors, the base variety is the Segre-Veronese variety [cite: 9, 10].
*   **Grassmannians and Spinor Varieties:** Other homogeneous spaces represent specific skew-symmetric or algebraic structures [cite: 11, 12].

The $k$-th secant variety of a base variety $X \subset \mathbb{P}^N$, denoted $\sigma_k(X)$, is defined as the Zariski closure of the union of all $(k-1)$-dimensional linear subspaces spanned by $k$ points on $X$ [cite: 7, 13]. Consequently, $\sigma_k(X)$ precisely parameterizes the projective tensors of border rank at most $k$ [cite: 1, 2]. Border-rank varieties are thus synonymous with higher secant varieties.

## 2. The Singular Loci of Border-Rank Varieties

While the dimensions and general points of secant varieties have been extensively studied (most notably culminating in the Alexander-Hirschowitz theorem for Veronese varieties), the singular loci of these varieties remain deeply mysterious.

### 2.1 Trivial and Non-Trivial Singular Loci
For any projective variety $X$, it is a classical fact that the $(k-1)$-th secant variety is inherently contained within the singular locus of the $k$-th secant variety: $\sigma_{k-1}(X) \subseteq \text{Sing}(\sigma_k(X))$ [cite: 8, 11]. Points belonging to $\sigma_{k-1}(X)$ are referred to as the **trivial singular points** of $\sigma_k(X)$. 

A point $p \in \sigma_k(X)$ is considered a **non-trivial singular point** if it is a singular point of the $k$-th secant variety but does not lie in the $(k-1)$-th secant variety ($p \notin \sigma_{k-1}(X)$) [cite: 8]. Classifying these non-trivial singular points is an arduous task. For example, in the case of matrices (the secant varieties of the Segre product of two projective spaces), the secant varieties are determinantal varieties, and their singular loci are completely described by the lower-rank matrices (meaning only trivial singularities exist) [cite: 8, 14].

### 2.2 Subsecant Loci and Veronese Embeddings
For higher-order tensors, the singularity structure fractures. For the Veronese variety $v_d(\mathbb{P}^n)$, the singular locus $\text{Sing}(\sigma_k(v_d(\mathbb{P}^n)))$ was historically known only for $k \le 3$. For $k=2$, only trivial singularities exist [cite: 8]. For $k=3$, the singular locus was completely determined by Han, demonstrating that non-trivial singularities occur if and only if $d=4$ and $n \ge 3$ [cite: 8, 14].

Recent advancements by Furukawa and Han have introduced the concept of **subsecant loci** to explain the origins of non-trivial singularities for arbitrary $k$. The $m$-subsecant locus is defined as the union of $\sigma_k(v_d(\mathbb{P}^m))$ for any $m$-plane $\mathbb{P}^m \subset \mathbb{P}^n$ [cite: 13]. By investigating the projective geometry of moving embedded tangent spaces along subvarieties, researchers have established a trichotomy for these subsecant loci: generic smoothness, non-trivial singularity, and trivial singularity [cite: 8, 13]. In many cases, these subsecant loci provide a massive new source of non-trivial singularities for the $k$-th secant variety [cite: 13, 14].

### 2.3 Singular Loci of Spinor and Grassmannian Secants
Beyond Veronese and Segre varieties, the singular loci of secant varieties of lines to Spinor varieties and Grassmannians have also been mapped. Galgano, Manivel, and Michałek have utilized nonabelian apolarity and Clifford apolarity to determine the identifiability and the singular locus $\text{Sing}(\sigma(S))$ of the secant variety of lines to a spinor variety $S$ [cite: 11, 15]. This involves partitioning the Spin-structure into orbits and carefully analyzing their inclusions and dimensions [cite: 11].

## 3. The Algebraic Geometry of Quantum Entanglement

The mathematical abstraction of tensor rank and border-rank varieties maps perfectly onto the physical reality of multipartite quantum systems. Frédéric Holweck and Luke Oeding have been at the forefront of utilizing these algebraic geometric tools to classify and quantify quantum entanglement.

### 3.1 Tensors as Multipartite States
In quantum mechanics, the state space of an $m$-particle system is the tensor product of the individual Hilbert spaces: $\mathcal{H} = \mathbb{C}^{n_1} \otimes \dots \otimes \mathbb{C}^{n_m}$ [cite: 6, 16]. A pure quantum state $|\psi\rangle$ is a unit vector within this space.
*   **Separable States:** A state is fully separable (unentangled) if it can be written as a simple tensor product: $|\psi\rangle = |\phi_1\rangle \otimes \dots \otimes |\phi_m\rangle$ [cite: 1, 16]. In algebraic geometry, the set of all such states modulo scaling forms the Segre variety [cite: 6].
*   **Entangled States:** Any state that cannot be factored in this manner is entangled, meaning its tensor rank is strictly greater than 1 [cite: 1, 4].

### 3.2 SLOCC Equivalence and Orbit Stratification
In Quantum Information Theory (QIT), states are classified based on their behavior under certain operational paradigms, the most prominent being Stochastic Local Operations and Classical Communication (SLOCC) [cite: 1, 4]. Two states are SLOCC-equivalent if they can be transformed into each other with non-zero probability using local operations. Mathematically, for a system of $m$ qudits, SLOCC equivalence corresponds precisely to the orbits of the group action $GL(n_1, \mathbb{C}) \times \dots \times GL(n_m, \mathbb{C})$ on the tensor space [cite: 4].

For a 3-qubit system ($\mathbb{C}^2 \otimes \mathbb{C}^2 \otimes \mathbb{C}^2$), the classification yields distinct entanglement families. Aside from the separable states, the two most famous entangled classes are the GHZ state and the W state:
*   **GHZ State:** $|\text{GHZ}\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$. It has a tensor rank of 2 and a border rank of 2.
*   **W State:** $|\text{W}\rangle = \frac{1}{\sqrt{3}}(|001\rangle + |010\rangle + |100\rangle)$. It has a tensor rank of 3, but crucially, a border rank of 2, meaning it lies on the tangent variety of the Segre variety (it is a limit of rank-2 states) [cite: 4].

Holweck, Oeding, and Jaffali have extensively used secant varieties and border rank to build a "geometric atlas" of these states, utilizing algebraic invariants to completely characterize the orbits [cite: 4, 17].

### 3.3 Neural Networks and Learning Algebraic Models
Because symbolic elimination algorithms (such as Gröbner bases) used to find the exact polynomial equations defining these secant and tangential varieties have doubly exponential worst-case complexity, Holweck, Oeding, and Jaffali have pioneered the use of machine learning to detect entanglement types [cite: 6]. 

By framing the problem as "learning membership on algebraic varieties," they designed supervised deep neural networks (using hybrid ReLU and power activation functions) to classify states [cite: 6, 16]. By generating random tensors of known border rank (by summing $R$ random rank-1 tensors), they successfully trained classifiers capable of predicting the border-rank and entanglement type for up to 5-qubit and 3-qutrit systems [cite: 4, 16, 17]. This numerical interpolation approach bypasses the massive computational overhead of exact symbolic algebra while preserving high classification accuracy.

## 4. Hyperdeterminants, Dual Varieties, and the $E_8$ Discriminant

A central object of study for Holweck and Oeding is the **hyperdeterminant**, a generalization of the matrix determinant to higher-order tensors. The hyperdeterminant of a tensor format is an invariant polynomial that vanishes if and only if the tensor possesses a degenerate multilinear rank—geometrically, it is the defining equation of the projective dual variety of the Segre embedding [cite: 16, 18].

### 4.1 Cayley's $2 \times 2 \times 2$ Hyperdeterminant
The most famous hyperdeterminant was discovered by Arthur Cayley in 1845 for the $2 \times 2 \times 2$ format. It is a homogeneous polynomial of degree 4 with 12 terms, serving as the fundamental invariant for the group $SL_2(\mathbb{C})^{\times 3}$ [cite: 6, 19]. 
In quantum physics, Cayley's hyperdeterminant gained immense popularity because it uniquely separates genuine entanglement classes in the 3-qubit Hilbert space: it is non-zero for the GHZ state and zero for the W state and separable states [cite: 4, 19]. Furthermore, it connects to entropy formulas for special solutions of black holes [cite: 19].

### 4.2 The $2 \times 2 \times 2 \times 2$ Hyperdeterminant and the Quadrifocal Variety
Moving to higher dimensions, the complexity of hyperdeterminants explodes. The $2 \times 2 \times 2 \times 2$ hyperdeterminant (for 4 qubits) is a polynomial of degree 24 containing 2,894,276 terms [cite: 6]. 

Luke Oeding extensively studied the singular locus of this specific hyperdeterminant, revealing profound connections to computer vision. The singular locus of the $2 \times 2 \times 2 \times 2$ hyperdeterminant consists of 8 components, classified by Weyman and Zelevinsky: $\nabla_{cusp} \cup \nabla_{node}(\emptyset) \cup \bigcup_{1 \le i < j \le 4} \nabla_{node}(\{i,j\})$ [cite: 20]. 
Oeding demonstrated that the "main" node component, $\nabla_{node}(\emptyset)$, is exactly the **quadrifocal variety** [cite: 20]. In computer vision, the quadrifocal variety is the Zariski closure of the set of quadrifocal tensors used for 3D reconstruction from four 2D projections (specifically flatlander cameras) [cite: 17, 18, 20]. Oeding computed the ideal of the quadrifocal variety up to degree 8, proving that it is far from a complete intersection: the degree-3 piece of the ideal ($I_3$) is 600-dimensional (yielding 600 cubic minimal generators), while $I_4$ is 48,600-dimensional but contains no minimal generators [cite: 20].

### 4.3 Hyperdeterminants from the $E_8$ Discriminant
In a highly influential 2022 paper published in the *Journal of Algebra*, Holweck and Oeding bypassed the direct computation of massive hyperdeterminants by utilizing the invariant theory of complex semi-simple Lie algebras, specifically the exceptional group $E_8$ [cite: 17, 18, 21].

Their methodology relied on taking the polynomial that defines the dual of the adjoint orbit of $E_8$ and restricting/projecting it to specific linear subspaces. By doing so, they obtained the discriminant polynomials for the dual varieties of the Grassmannians $Gr(3,9)$ and $Gr(4,8)$ as factors of the $E_8$ discriminant [cite: 18]. 

To handle the immense computational load (the $Gr(4,8)$ discriminant alone has 15,942 terms when expressed in fundamental invariants), Holweck and Oeding employed advanced interpolation algorithms combined with modulo-$p$ reductions and rational reconstruction [cite: 18, 22]. By successfully factoring these discriminants, they elegantly derived expressions for the well-known hyperdeterminants of formats $3 \times 3 \times 3$ and $2 \times 2 \times 2 \times 2$ directly from the $E_8$ root structure [cite: 18, 22].

Furthermore, they generalized a result of Parusinski [cite: 18]. They proved that if a generic section $V(h)$ has $k$ points of tangency, each defining a Morse singularity (where the quadratic part of the singularity is of full rank), the multiplicity $m$ of the singular point on the dual variety $X^\vee$ is exactly $k$. This provided a robust topological link (via Milnor numbers) to the geometric multiplicity of singular loci on these dual varieties [cite: 18].

## 5. Fermionic Fock Spaces and Advanced Invariants

Holweck and Oeding's work extends beyond distinguishable particles (qubits/qutrits) into the realm of indistinguishable particles governed by antisymmetric wavefunctions. 

### 5.1 Hyperdeterminants on Fermionic Fock Spaces
In a 2024 publication in the *Annales de l'Institut Henri Poincaré*, Holweck and Oeding translated the concept of Cayley's hyperdeterminant to the **fermionic Fock space** [cite: 19, 21]. 

Specifically, they examined the fermionic Fock space for $N=8$, representing spin particles across four different locations [cite: 19]. By analyzing the invariant ring $\mathbb{C}[\bigwedge^\bullet \mathbb{C}^8]^{\text{Spin}(8,\mathbb{C})}$, they explicitly computed the degree-four invariant analogous to the $2 \times 2 \times 2$ Cayley hyperdeterminant. They demonstrated how this massive invariant logically projects down to other well-known invariants in quantum information theory, providing deep combinatorial interpretations related to the geometry of the spin groups [cite: 19].

### 5.2 Maximally Entangled Real States in 3-Qutrit Systems
In addition to fermionic systems, Holweck, Oeding, and Jaffali investigated the absolute values of polynomial SLOCC invariants as a direct measure of the "amount" of entanglement [cite: 21, 23]. By evaluating the hyperdeterminant on real 3-qutrit systems ($\mathbb{R}^3 \otimes \mathbb{R}^3 \otimes \mathbb{R}^3$), they identified the specific geometric coordinates that maximize the hyperdeterminant [cite: 23]. 

Using a variant of the Higher-Order Singular Value Decomposition (HOSVD) combined with Jordan decomposition, they discovered a completely new set of maximally entangled real states that form the absolute peak of this invariant measure [cite: 21].

## 6. Structural Advances: Jordan Decompositions and Toric Geometry

To computationally maneuver through the dense algebraic structures of tensor spaces, Holweck and Oeding have developed entirely new algebraic frameworks.

### 6.1 A Jordan Decomposition for Tensors
In classical linear algebra, the Jordan-Chevalley decomposition uniquely expresses a linear operator as the sum of a semi-simple (diagonalizable) operator and a nilpotent operator that commute. Extending this to multilinear tensors was previously thought to be severely restricted. 

In a groundbreaking 2024 paper in the *Journal of Computational Science*, Holweck and Oeding expanded on a historical idea of Vinberg to establish a true **Jordan Decomposition for Tensors** [cite: 5, 21, 24]. By taking a tensor space $M$ and the natural Lie algebra $\mathfrak{g}$ (typically $\mathfrak{sl}_n$) that acts upon it, they embedded both into an auxiliary graded algebra structure $\mathfrak{g} \oplus M$ [cite: 17, 24]. 

Viewed as endomorphisms of this graded algebra, they associated "adjoint operators" to tensors [cite: 17]. Because the group actions on the tensor space and the adjoint operators are mathematically consistent, they were able to formally decompose complex tensors into commuting semi-simple and nilpotent components ($T = S + N$) [cite: 5, 21]. This mechanism was entirely implemented by Oeding in the computational algebra software Macaulay2, explicitly mapping the brackets, Killing forms, and matrix representations of adjoint operators [cite: 24].

### 6.2 Toric Geometry and Cumulant Coordinates
Parallel to his work with Holweck, Oeding (alongside Piotr Zwiernik) tackled the secant line variety of the Segre product using **cumulant coordinates**—a coordinate system specifically adapted for statistical physics and secant varieties [cite: 7, 17]. 

They proved the remarkable result that, in cumulant coordinates, the secant variety is covered by open normal toric varieties, and its defining ideal is generated entirely by binomial quadrics [cite: 7, 17]. This toric geometric translation allowed them to present powerful new results on the local structure of the secant variety, proving that it possesses rational singularities and explicitly describing its singular locus. They also succeeded in classifying all secant varieties that satisfy the Gorenstein property [cite: 7].

## 7. Border Apolarity and Subrank 

The determination of the exact border rank of highly symmetric tensors relies on advanced algebraic geometry tools. While flattening algorithms (viewing the tensor as a matrix map from $V_1 \otimes V_2 \to V_3$) provide lower bounds on border rank, they are notoriously insufficient for establishing exact ideals (e.g., failing to solve the Salmon conjecture independently) [cite: 9].

To bypass this barrier, researchers like Jarek Buczyński, Mateusz Michałek, and Luke Oeding have championed the method of **border apolarity** [cite: 5]. Border apolarity is an elementary yet vastly powerful generalization of the classical apolarity lemma, specifically adapted for border rank. By utilizing irreducible components of the multigraded Hilbert scheme, border apolarity provides uniform lower bounds for border rank that are immune to the standard barriers that plague flattening matrices [cite: 5].

Simultaneously, the concepts of **subrank** and **border subrank** have emerged. Originally introduced by Strassen to analyze matrix multiplication complexity, the border subrank looks at the largest matrix multiplication tensor that can be degenerate from a given tensor. Recent theorems (presented by Benjamin Biaggi and others) have proven that the generic border subrank of tensors in $(\mathbb{C}^n)^{\otimes 3}$ is strictly greater than the generic subrank for sufficiently large $n$, scaling at a growth rate of $\Theta(\sqrt{n})$ [cite: 25]. This contrasts starkly with regular tensor rank, where the generic rank and generic border rank are identical [cite: 25].

## 8. Conclusion

The intersection of algebraic geometry, representation theory, and quantum information theory has fostered a golden era of multilinear algebra research. The quest to map the singular loci of border-rank varieties—ranging from the trivial singularities of secant boundaries to the complex subsecant loci of Veronese embeddings—is gradually being unraveled. 

Frédéric Holweck and Luke Oeding stand as pivotal figures in this exploration. By weaponizing the invariant theory of exceptional Lie groups like $E_8$ to compute intractable hyperdeterminants, establishing Jordan decompositions for tensors via graded algebras, mapping the geometric landscape of fermionic and multi-qubit quantum entanglement, and classifying the singular loci of the quadrifocal variety, they have provided the mathematical community with profound tools. As exact symbolic computations reach their fundamental complexity limits, their integration of numerical geometry, toric cumulant coordinates, and machine-learning classifications represents the definitive future for understanding the algebraic boundaries of tensors.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaNJ2ue3qLdWvVnmXQDLi9JLVg2XAZagrga96DcNhXVC61mGxskjeSF2oqiaiVLRslfYDkIai8suUxkEHi2bUrCaZaqRLySP5FziGVvxTppUjlGPJqlA==)
2. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlyhfmEGkYuPVJuGcsVGGyduzjGPrxhZZPpxsKGOXAz6XxC_9FWFbDka9O0aDAOndXlA04IKRTYI3WyCmkwqfSc7lH5kQ4GEbko3yNIwulv-iMQkeLflD0bT9xflRVzTdXKQ==)
3. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqtKeQqj1ln_yVuvHsLC5Ra25t33ES2qNm8wTc8IdxkGlOFXSA5rVMC5aCvlgrVQWE3h5Q8yfnP4TMUCiK9mub3pm7jqWVL_KbOpHM_YAqmfTPgq_VnyHWzSgRNwqJNDmtoQs=)
4. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrk8wC3FZxkYNon1ofkxYLeJUJLz69eS_tQjhYJYICMZ-7iH_jk53UKcdkNf8n71GItRci4gN0JuQMVsNkz43K3jEcKpLiYpEOKv0c_s9vt8T1ZHoC5wRgtCZkkdBzANF4Jz2M5qBiLH_dTYFV)
5. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ7XShjJwt0cvGZ1uayTjJpVtbWaov9WmsvAm3ueekskFBiANdMjk5yV2FJZqZ0qJSKwDqOQf8ZtNGIo3ULEMiV0hmTpoM0f4TdTkaYbIQvhBCbEbkimND103mFOZHZPupXs4pBwz9Me5EFfvtjJLRvT335A_ZMJpM6DT4OvA=)
6. [auburn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdx1LXm8yBDa4QaPMwVVUY9dK_ggUd5Tq64Y_uGjUG2ngff8ZpG9ychJdVO2qTALZh79K4Xo3YtSRmx83YVHiAqMlg-WvVWrHdyx7DrybAJrnVVD-pIMRM8wKa4Oi0Z5wgBXkYMsM=)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF42rL27GHY5AutmrxT1QTwg4Rc988GHAihLg791aTEMVRA3MLcd5Hcy1y71j7UJN3ByY6nj16_0VMjSBeDi4Ex3xnBw9j5mA9yJJHgHOXgp_uxNDW00flgFPsmR7-fpSMI9MXiS8ca-ccMH91G-UnruF46X1jTPYkV_o3aup1LJwZcL8twfwN9Rm5qf35wcs1d7umzAzBcsHJ--iwsSdaTLAtsvs_ldnf9xyW38D1)
8. [dgist.ac.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8iWXv0op9wvTUOG7LPRGwPv18SMkLl2fpdWm1tChBn4w7rcS6I8Na0d53hXUnQKWwEUgWwAiFnDwokVtE1PkZqH-5YJPALKUk6lbeFWOB6LGDQDJPlutJGoQzNovv3LL53yjIls5ofFH1MKWsEtxNPpyYtgWPHgtPt9fNdDNMXeoFcxs=)
9. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYZXYT8fU3fdx0zCaXLTPG2jb-4kOZhAZ4buI-UuzQKBZoVUagFVCadmc4xEx7vmceXBOzjvMu7rQepUXmdco29suTrIMbxyzC5_B-UtDbLVLnoUpLnm2JMKgf5nE-5VGqKg==)
10. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGQeHp9WtuRNjceTIb92bb2AgVzDjqbQqcIS0x1sWEd5w2gPL8nsgrWDOSM_m-C1w7XYb8AzPmKpzLXatsRQcn4h7Wna7DG9KrnQ_n6gzJDHFNxa1jbb3Mujeyj9KTYVPdKmX1CMPr18fZGH2e5LAd_zYW7T15VCOzmMXM8LMJl_Fnh-blgpHKlHw=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9tnP4zpdz-yC4XYcMFiFHX3bi6UvtWfW_WbE3PbCPjTLK-vs_5Y0xMAgBGUkjNOzPRIPIZjoWKynxyV1wb3Q5aljdjkv2mz-h7aAOD5c5YjliwOrgUw==)
12. [sigma-journal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx0oD0sxONZR7LwCYe8YLhXpeIX7gr7P9mYJEkXJWT4D92rm7yyxzvRkVwElKGtB4OqoNsnLJk2P6Cdw2dYG5jm0aW35fTjUSVjPYNXbYPCOA7xUlglQfxJ9GvsfzBTKKEporRr-6o1w==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlqIYsD4YG4PPI0LTDmG-Ma2xk4roICY-r3O4Pr0acx0CPUR1EHVufyPfc0EJBlTvC1sPew-1m2oCaIcHKpIEmQSZqBe29g1i9swuuXzowO_CsGvzh5w==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ7TApCskY5n3A-44fw8PLu7lF7dkeP8ZyS9Z4d3QTEoX4LQRCQjDYUTdjfOfePbddchol2ubVgbMbBeAjQOEOm3YlG4qGegRUJ0UKgQa8R63pZkWTCEX5bg==)
15. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHd5TzNDRwriTEH65K8ZMRFK9hC-VNYwkBv9GiizBrfIA4Hbs-2nOxpHeBtWtowBNI9b-zS-JEcAtUaoXIbcqrSPHmBZ50pKwy3t-9Ve7TeC9jl2gZlwok2D6PQ2XCtdudoGigqfrBSlT3_zyg-W5aHDBQ74PuTMi9RHikU-Pn9vhKCP_X6qR6XRkunJXaibfm5Te4NOGPEig==)
16. [auburn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAMAx2I5SmCYqzj_xzG2tn5vQKXf9lHNkBg00mlTVz6ecsCGgkMBLtpOS0M5gUomlN_MgXRQUnd8B0BvXpllPeEiIgNoBep-94Hs-IV_vpiWaxqpNCLKK9jYLFVxcYMlkfvTi9)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtW23D34CcczE777yScM1aGsTCUQhWw9JGYySbZgRdvbOcICv0CbzegJvDTA88jgplmBKItw0aK56zHtN7y8tDzDPiZ7VFHAPjtzyRFp0pf6RjtH5UcSCDxL1Z84NfGUudbK7tgYRcRw==)
18. [auburn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFANsBF0YgTCSOhoxfOIp_gNBNLItSbzbwumvclGrgW6FvCmG-hKelYjUQlUC-zNcD7exzkVsEE40joa5fEeKAcvw5U9mYjTIgWJwThhDk2H1oQ9U4dQZefbYwPA2aohiSgeYrUdH1Dxvntif31GHBuk7NC8Wju)
19. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUoQiKYkp7shIc3XyfnXmHnwmlLm2fWkSw_4ZI426K_NSP3UFXxjQ3DuijHIm8Qcx62kBlX--DcUfqrTwCgoZdVGiO_ijk_7d22UaZ7wJmncg94m5aOMUNDqPXuB74Cpn8aye8Uslcbg==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED1lwIP-pp6uxRcysQMsC2T_XBOa1TSjtcgddZMpXOFlX9M9vYExgrz7k8rTifymcGTHokQ0lemXc7FkzoFclulgyTKsnhWYCjVQ__WIK-GGZlvJV5Kg==)
21. [auburn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIlLAON9ZKre8zZtaTwXV_E2YjOnWo45M3NdsmGpQra8JgTPd5IPm6FqIf0Yt0kXJdAPE7rXOXR-WQ4DwbIGNft5bW2iWW7gLwmfoG8PvCbADOaMIIyeZ7AtZPTPBMoHcAAg==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS4EzXX-aA36CFJMo2zwtMKoyxYVWTdLPKRlsVMwE4at92U_1Bfkcrsp14j8g-LjWStVIPtZAwpUvB5gAtKyDb_9znET1Zwx0wt0QmJ_sFk3gL6wwgTQ==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKMBhMgK_IMFHSYRjOFS_7jJkjz_0hP3JrKez8uSIush5GQdMlTQ1gOXpNFLPdBxlPmhjKNg1o49KP22GAbZVOVQoQmEF8SfNa756Mh4Ff_3ydGZbQxAyJf1AH1A-tPLAenyHebqed9jgT1Q==)
24. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHK6wyeAbkDZvzN3QmcVCFIzfWsylBllG5v2lAy5ZO6d0TKcj5KlF_0egviPSlC8w91-f7zb5IX73ouO8zyR-JuGpq5eZ26skiUnh5Kll7Fo20W1wucrrPgGIgAPcjA)
25. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGZTafVj5I--gr7omeXR3TPh6KxXmvpOs1P5Ms0wBIbLE3ihBz6FxpRHfkcvJ_GIvW2W93LEzD0IT90Y3QGWyVbW8hqGm_53tckInL8TvuGrndz1DTuAgC9852pT-Oj60tWoDOsWVZLKo5ntafqQ0Bun7bUh-e738T)


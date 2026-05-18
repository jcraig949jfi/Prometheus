# T#9 Restriction pre-order on small (3x3x3) tensors

**Pythia queue id:** 10
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdsbllMYXI3eUw3MmNfdU1QM2ZMUHFBRRIXbG5ZTGFyN3lMNzJjX3VNUDNmTFBxQUU
**Elapsed:** 494s
**Completed at:** 2026-05-18T20:37:25.845691+00:00

---

# The Restriction Pre-order on Small (3x3x3) Tensors: Algebraic Complexity, Entanglement, and Partial Latin Squares

**Leading Paragraph**

*   **Key Points:**
    *   The restriction pre-order is a foundational mathematical framework used to compare the relative complexity of tensors by determining if one tensor can be linearly transformed into another.
    *   Small tensors, particularly of dimensions 3x3x3, serve as the crucial proving ground for theories spanning algebraic complexity, quantum entanglement, and computer vision.
    *   While "T#9" is not universally established as a standard named tensor in broader mathematical literature, in the specific context of small 3x3x3 tensors, it strongly correlates with **Main Class $MC_{5,9}$**, a specific equivalence class of partial Latin square tensors of weight 5, or the Latin Square Tensor family $T_d$ (specifically $T_3$).
    *   The computation of exact restriction pre-orders relies on translating transformations into multivariate polynomial systems and solving them via Gröbner bases, though current consumer hardware is computationally limited to comparing tensors with a combined weight not exceeding eight.
    *   Theoretical extensions, such as the asymptotic restriction pre-order and symmetric subrank, offer profound insights into Strassen's matrix multiplication exponent ($\omega$) and the quantum entanglement states (like GHZ and W-states).

The study of small tensors, particularly multidimensional arrays of size 3x3x3, sits at the intersection of abstract algebra, theoretical computer science, and quantum physics. To understand how "complex" or "resourceful" a tensor is, mathematicians utilize the **restriction pre-order**—a mathematical hierarchy that evaluates whether one tensor can simulate another through linear mappings [cite: 1, 2]. This concept is critical for optimizing algorithms like matrix multiplication and mapping quantum entanglement transformations via Stochastic Local Operations and Classical Communication (SLOCC) [cite: 1, 3]. Recent intensive computational research, most notably in the classification of Partial Latin Square (PLS) tensors, has mapped the restriction pre-order for very small, sparse 3x3x3 tensors [cite: 2]. Within this niche, identifiers like "T#9" or "T9" point toward specific configurations of data—such as the ninth main class of weight-5 tensors ($MC_{5,9}$)—highlighting the immense structural complexity that arises even in arrays with only a few non-zero elements [cite: 2]. The following report synthesizes the algebraic theory, computational methodologies, and physical applications of the restriction pre-order on 3x3x3 tensors.

---

## 1. Introduction to Tensor Theory and the 3x3x3 Space

Tensors are multidimensional arrays of numbers that generalize the concepts of scalars (0th-order tensors), vectors (1st-order tensors), and matrices (2nd-order tensors) into higher dimensions [cite: 1, 4]. A 3rd-order tensor, such as a 3x3x3 array, can be visualized as a cube of numbers containing 27 individual components (or elements) [cite: 5, 6]. 

In mathematical literature, tensors are often defined formally as elements of a tensor product of vector spaces, or as multilinear maps [cite: 4, 7]. For instance, a 3rd-order tensor can represent a bilinear map from two input vector spaces into a third, such as $T: V_1 \times V_2 \rightarrow V_3$ [cite: 4, 8]. If we fix a basis, this bilinear map is uniquely determined by a 3-dimensional array of coefficients. Conversely, in the physical sciences and mechanical engineering, a tensor is often described by its transformation properties under coordinate changes, such as the elasticity tensor governing stress and strain in materials [cite: 4, 7, 9]. 

The 3x3x3 tensor space is of particular interest because it is the smallest non-trivial space where many higher-order phenomena—which do not exist in standard matrix algebra—first appear. For example, while every matrix can be diagonalized in a way that reveals its exact rank (via Singular Value Decomposition), the rank of a 3-dimensional tensor is notoriously difficult to compute; in fact, determining tensor rank is generally an NP-hard problem [cite: 10, 11]. Researchers have extensively studied the orbits of 3x3x3 tensors under various group actions to understand their algebraic varieties, nullcones, and invariant structures [cite: 12, 13, 14].

---

## 2. The Restriction Pre-Order: Theory and Formalism

To compare the complexity and utility of different tensors, algebraic complexity theory relies on the concept of **restriction** [cite: 1, 2]. Restriction establishes a hierarchy—a pre-order—that systematically categorizes which tensors can be transformed into others [cite: 1, 2].

### 2.1 Formal Definition of Standard Restriction
For two order-3 tensors (or trilinear forms) $T$ and $T'$ defined over a field, we say that $T$ **restricts** to $T'$, denoted as $T \leq T'$, if $T'$ can be obtained from $T$ by applying linear maps to its modes (the "legs" or dimensions of the tensor) [cite: 1, 8]. Specifically, if $T$ is an $n \times n \times n$ tensor and $T'$ is an $m \times m \times m$ tensor, the restriction $T \leq T'$ holds if there exist three matrices (linear maps) $A, B,$ and $C$ such that:
$$T' = (A \otimes B \otimes C) T$$
or, in index notation, $T'_{ijk} = \sum_{p,q,r} A_{ip} B_{jq} C_{kr} T_{pqr}$ [cite: 1, 2]. 

Importantly, these linear maps $A, B$, and $C$ do not need to be invertible [cite: 1]. When $T \leq T'$ and $T' \leq T$, the two tensors are considered equivalent, denoted as $T \sim T'$, though they do not necessarily have to reside in vector spaces of the identical ambient dimension (since padding a tensor with zeros results in an equivalent tensor) [cite: 1, 15]. Because the restriction relation is both reflexive ($T \leq T$) and transitive (if $T \leq T'$ and $T' \leq T''$, then $T \leq T''$), it forms a mathematical **pre-order** on the set of equivalence classes of tensors [cite: 1, 2]. 

### 2.2 Extended Restriction and Mode Permutations
In specific computational studies of order-3 tensors, standard restriction is sometimes deemed too rigid because it is not invariant under the permutations of the tensor's modes (i.e., swapping the roles of rows, columns, and depth/levels) [cite: 2]. 

To build a more comprehensive structural hierarchy, the concept of **extended restriction** was developed. Extended restriction, denoted $T \preceq T'$, allows for mode permutations [cite: 2]. Tensor $T$ is an extended restriction of $T'$ if there exists a permutation $\pi \in S_3$ (the symmetric group on 3 elements, which has $3! = 6$ possible permutations) such that $T$ is a standard restriction of $\pi T'$, where $\pi T'$ is the tensor obtained by permuting the modes of $T'$ [cite: 2]. Like standard restriction, extended restriction is reflexive and transitive, allowing mathematicians to build Hasse diagrams representing the hierarchy of tensor classes [cite: 2].

---

## 3. Resource Theory of Tensors: Rank, Subrank, and Complexity

The restriction pre-order provides the foundation for viewing tensors as resources, a framework highly applicable to computational complexity and quantum mechanics [cite: 1]. Within this resource theory, specific parameters evaluate the "cost" of building a tensor and the "value" extracted from it [cite: 1].

### 3.1 Tensor Rank (Computational Cost)
The most fundamental measure of a tensor's computational complexity is its **tensor rank**, denoted $R(T)$ [cite: 2, 8]. The rank of a tensor $T$ is the minimum integer $r$ such that $T$ can be expressed as the sum of $r$ rank-1 (outer product) tensors [cite: 1, 8]. 
Using the restriction pre-order, the rank $R(T)$ is redefined as the minimum size $r$ of a diagonal "unit tensor" $\langle r \rangle$ (which has 1s on the diagonal and 0s elsewhere) required to obtain $T$ [cite: 1, 2]. Mathematically:
$$R(T) = \min \{ r : \langle r \rangle \geq T \}$$
In quantum terms, $\langle r \rangle$ is equivalent to the Greenberger–Horne–Zeilinger (GHZ) state, making tensor rank analogous to the number of GHZ states required to synthesize a specific quantum state [cite: 1]. For small tensors, such as the 2x2x2 matrix multiplication tensor $M_2$, the rank is 7, corresponding exactly to Strassen’s famous fast matrix multiplication algorithm [cite: 2].

### 3.2 Tensor Subrank (Computational Value)
Conversely, the **subrank** of a tensor, denoted $Q(T)$, measures the largest diagonal unit tensor that can be extracted *from* $T$ via the restriction pre-order [cite: 1, 3]. It represents the tensor's intrinsic "value" in generating independent scalar multiplications [cite: 1, 8].
$$Q(T) = \max \{ r : T \geq \langle r \rangle \}$$
For a generic tensor of order $k$ in $\mathbb{K}^{n \times n \times \dots \times n}$, the generic subrank $Q(n)$ is known to grow as $\Theta(n^{1/(k-1)})$ [cite: 8]. However, calculating exact subranks for specific structural tensors remains a complex algebraic challenge. 

### 3.3 Symmetric Subrank and Comon's Conjecture
For tensors that exhibit symmetry (where the entries are invariant under permutation of indices), researchers analyze the **symmetric restriction pre-order**, denoted $\leq_s$ [cite: 16]. Under symmetric restriction $T' \leq_s T$, the linear transformations applied to all modes of the tensor must be identical (i.e., $T' = (A \otimes A \otimes A) T$) [cite: 16]. 

The **symmetric subrank**, $Q_s(T)$, is bounded by the standard subrank: $Q_s(T) \leq Q(T)$ [cite: 16]. An outstanding question in this field relates to **Comon's Conjecture**, which posits that the symmetric rank of a symmetric tensor equals its standard tensor rank [cite: 16]. Research into small 3x3x3 tensors has identified counterexamples over certain fields. For instance, there exists a specific symmetric tensor $f$ of order three over the field $\mathbb{F}_2$ for which a strict inequality holds: $Q_s(f) = 1$ while $Q(f) = 2$ [cite: 16]. However, recent breakthroughs have proved that for symmetric matrices (order-two tensors), the subrank and symmetric subrank are always equal. Furthermore, Comon's conjecture has been proven to hold true *asymptotically* for the subrank across symmetric tensors [cite: 16].

---

## 4. Asymptotic Restriction and the Tensor Spectrum

While standard restriction governs exact transformations, many applications in theoretical computer science involve taking the limits of massive tensor products. This leads to the **asymptotic restriction pre-order**, pioneered by Volker Strassen in the 1980s [cite: 1, 15].

### 4.1 Strassen's Asymptotic Preorder
The asymptotic restriction pre-order, denoted $T \gtrsim T'$, evaluates whether a large tensor power of $T'$ can be obtained from a marginally larger tensor power of $T$ [cite: 1, 3]. Formally, $T \gtrsim T'$ if there is a sequence of hypergraphs or direct sums such that:
$$\bigoplus_{i=1}^{2^{o(n)}} T^{\boxtimes n} \geq (T')^{\boxtimes n}$$
where $n \to \infty$ [cite: 1]. This framework allows mathematicians to disregard low-order "noise" or overhead, focusing purely on the asymptotic growth rates. This leads to asymptotic versions of rank ($\tilde{R}(T)$) and subrank ($\tilde{Q}(T)$) [cite: 3, 16].

### 4.2 The Asymptotic Spectrum of Tensors
To classify tensors under asymptotic restriction, Strassen introduced the **asymptotic spectrum of tensors** [cite: 3, 15]. This spectrum consists of all functions (spectral points or support functionals) that map tensors to non-negative real numbers while behaving monotonically under restriction, additively under direct sum, and multiplicatively under the Kronecker tensor product [cite: 15]. 
By evaluating a tensor across all points in the asymptotic spectrum, one can precisely bound its asymptotic rank and subrank [cite: 3]. If $T \gtrsim S$, then for every function $\phi$ in the asymptotic spectrum, $\phi(T) \geq \phi(S)$ [cite: 17]. Recent advances by Christandl, Vrana, and Zuiddam have identified new infinite families of elements in this spectrum over complex numbers, utilizing tools like quantum functionals and entanglement polytopes [cite: 3, 15].

### 4.3 Matrix Multiplication Exponent ($\omega$)
One of the crowning applications of the restriction pre-order is bounding $\omega$, the exponent of matrix multiplication [cite: 1, 3]. Matrix multiplication of size $d \times d$ is represented by the matrix multiplication tensor $M_d$ (or $EPR_d^\Delta$, $MaMu(d)$, $\langle d,d,d \rangle$) [cite: 1, 2]. 
The exponent $\omega$ is strictly defined via the asymptotic rank of the matrix multiplication tensor: $\omega = \log_2 \tilde{R}(M_2)$ [cite: 1]. The long-standing conjecture that matrix multiplication can be achieved in near-quadratic time ($\omega = 2$) is mathematically equivalent to proving that $\langle 4 \rangle \gtrsim M_2$ [cite: 1]. Strassen’s "laser method" approaches this problem by leveraging the restriction pre-order on intermediate structural tensors, such as the Coppersmith–Winograd tensor, to find tighter bounds on $\omega$ [cite: 1].

---

## 5. Classification of Small Partial Latin Square (PLS) Tensors

To understand the macro-behavior of tensors in asymptotic regimes, researchers often perform exhaustive algorithmic classifications of "small" tensors. A landmark study in this area is the classification of 3x3x3 **Partial Latin Square (PLS)** tensors, as detailed in the master's thesis of Erika Marttinen [cite: 2].

### 5.1 Defining PLS Tensors
A Latin square of size $n \times n$ is a grid filled with $n$ distinct symbols such that no symbol repeats in any row or column [cite: 2, 18]. A **Partial Latin Square (PLS)** is a subset of a Latin square where some cells may be empty, but the non-repeating rule remains unbroken [cite: 2, 18].
A Partial Latin Square tensor is an order-3 tensor $T \in \{0,1\}^{n \times n \times n}$ whose non-zero entries (the "support") map exactly to the coordinates of a partial Latin square [cite: 2]. In this geometric interpretation, $T_{ijk} = 1$ if the cell at row $i$ and column $j$ contains the symbol $k$, and $T_{ijk} = 0$ otherwise [cite: 2]. 
The **weight** ($w$) of a PLS tensor is defined as the total number of its non-zero entries (i.e., $T_{ijk} = 1$) [cite: 2].

### 5.2 Main Classes up to Weight 5
Using the concept of extended restriction (allowing for slice permutations and mode permutations), Marttinen classified all 3x3x3 PLS tensors of weight up to 5 into equivalence classes, termed **Main Classes** ($MC$) [cite: 2, 19].

*   **Weight 1 ($w=1$):** There is only a single main class, $MC_{1,1}$. It has a rank of 1 and represents a trivial $1\times 1\times 1$ tensor [cite: 2].
*   **Weight 2 ($w=2$):** Features two main classes. $MC_{2,1}$ has a shape of $1\times 2\times 2$ and embeds into standard matrices. $MC_{2,2}$ has a shape of $2\times 2\times 2$ and is isomorphic to the unit tensor $\langle 2 \rangle$ [cite: 2]. Both have a tensor rank of 2 [cite: 2].
*   **Weight 3 ($w=3$):** Contains five main classes ($MC_{3,1}$ through $MC_{3,5}$) [cite: 2]. All five classes have a tensor rank of exactly 3 [cite: 2]. Notably, $MC_{3,2}$ corresponds to the 3-way partitioning tensor (border rank 2), while $MC_{3,5}$ represents the unit tensor $\langle 3 \rangle$ [cite: 2].
*   **Weight 4 ($w=4$):** Features eight main classes ($MC_{4,1}$ to $MC_{4,8}$) [cite: 2]. Ranks vary across this weight. $MC_{4,1}$ is a "low-rank" complete $2\times 2\times 2$ Latin square with rank 2. Classes $MC_{4,5}$ through $MC_{4,8}$ have a rank of 4 [cite: 2]. $MC_{4,8}$ acts as the direct sum of the 3-way partitioning tensor and a $1\times 1\times 1$ tensor [cite: 2].
*   **Weight 5 ($w=5$):** Contains nine main classes ($MC_{5,1}$ to $MC_{5,9}$) [cite: 2]. Class $MC_{5,3}$ is the direct sum of $MC_{4,1}$ and a $1\times 1\times 1$ tensor, giving it a rank of 3 [cite: 2]. The remaining eight classes in this weight category have ranks strictly greater than 3. Since the weight bounds the rank trivially, their ranks lie in the set $\{4, 5\}$ [cite: 2].

### 5.3 Decoding "T#9": The Significance of $MC_{5,9}$ and $T_3$
In the context of the user's query regarding "T#9" within the restriction pre-order of small 3x3x3 tensors, literature points directly to two highly probable mathematical structures:
1.  **Main Class $MC_{5,9}$:** This is the ninth and final main class of 3x3x3 Partial Latin Square tensors of weight 5 [cite: 2]. The tensor representative for $MC_{5,9}$ possesses a canonical shape of $3 \times 3 \times 3$ [cite: 2]. Because determining its exact tensor rank computationally breaches the limits of current Gröbner basis implementations (which max out at a combined weight of 8), its rank is constrained to the set $\{4, 5\}$ [cite: 2]. It stands as an upper limit of currently cataloged, computationally verified tensor hierarchies in this domain.
2.  **The Latin Square Tensor Family ($T_d$):** The notation $T_d$ is used to describe a specific family of $d \times d \times d$ tensors where $(T_d)_{ijk} = 1$ if $k = (i+j) \bmod d$, and $0$ otherwise [cite: 2]. The tensor rank of $T_d$ is exactly $d$. Consequently, $T_3$ represents a perfectly structured 3x3x3 tensor with a rank of 3, frequently utilized as a benchmark for tensor restriction testing [cite: 2]. 

---

## 6. Computational Methodology for the Restriction Pre-order

To rigorously prove that one small tensor restricts to another ($T \leq T'$), mathematicians must step outside manual algebra and employ advanced symbolic computation [cite: 2]. 

### 6.1 Polynomial Modeling of Restriction
The linear mapping equation $T' = (A \otimes B \otimes C) T$ can be unpacked into a massive system of multivariate polynomials [cite: 2]. If we are comparing two 3x3x3 tensors, the matrices $A, B$, and $C$ are $3 \times 3$ matrices, yielding $3 \times 9 = 27$ unknown variables [cite: 2]. 
Each of the 27 entries of the target tensor $T'$ yields a polynomial equation based on the sum-of-products of the variables in $A, B$, and $C$ matched with the non-zero entries of $T$. To handle *extended restriction* ($T \preceq T'$), the computational engine must generate and test separate polynomial systems for each of the $3! = 6$ possible mode permutations of the target tensor [cite: 2, 19].

### 6.2 Gröbner Bases
To determine if this system of 27 multivariate polynomials has a common root (a valid solution where $A, B, C$ exist), algebraic geometers utilize **Gröbner bases** [cite: 2]. A Gröbner basis transforms the complex polynomial system into a canonical form possessing the same roots but with a much simpler, often triangular, structure [cite: 2, 19].
If the reduced Gröbner basis of the ideal generated by these polynomials equates exactly to $\{1\}$, it mathematically proves that the system of equations is inconsistent—meaning no common solution exists, and therefore the restriction $T \leq T'$ is impossible [cite: 2]. If the basis does not collapse to $\{1\}$, a restriction mapping exists.

### 6.3 Hardware Limitations and Optimizations
Because computing Gröbner bases carries a doubly-exponential time complexity in the worst case (with respect to the number of variables), brute-force checking is computationally prohibitive [cite: 2]. Researchers apply pruning techniques, such as verifying trivial rank bounds (since $T \leq T'$ requires $R(T) \leq R(T')$) and checking the "conciseness shape lemma," which dictates that the spatial bounding box of the restricting tensor cannot exceed the bounding box of the target tensor under any mode permutation [cite: 2].
Despite these optimizations, on standard consumer hardware, this exact symbolic approach hits a hard wall. It is currently limited to evaluating restrictions where the combined weight of the two tensors being compared is 8 or less ($w \le 8$) [cite: 2]. This hardware limitation is precisely why the exact rank of "T#9" (Main Class $MC_{5,9}$), which has a weight of 5, cannot be tested against rank-4 unit tensors (weight 4) using this specific method, leaving its rank bounded at $\{4, 5\}$ rather than exactly determined [cite: 2].

---

## 7. Quantum Information and Entanglement

The mathematics of 3x3x3 tensors and restriction pre-orders map flawlessly onto the physics of quantum entanglement [cite: 1, 3]. In quantum information theory, a $k$-order tensor corresponds to the wave function (quantum state) of a $k$-partite system [cite: 1]. Thus, a 3x3x3 tensor mathematically describes a quantum system of three particles, each possessing 3 distinct energy levels (qutrits).

### 7.1 SLOCC and Tensor Restriction
The restriction pre-order $\leq$ is mathematically identical to the quantum protocol known as **Stochastic Local Operations and Classical Communication (SLOCC)** [cite: 1, 3]. If a quantum state $T$ can be transformed into state $T'$ via SLOCC with a non-zero probability of success, then tensor $T'$ is a restriction of $T$ ($T' \leq T$) [cite: 1, 3]. The linear maps $A, B$, and $C$ represent the local physical operations (like measurements or filtering) performed independently by three observers (traditionally named Alice, Bob, and Charlie) [cite: 1, 8].

### 7.2 Benchmark Entangled States (GHZ and W)
In the 3-partite tensor space, specific tensors represent canonical forms of entanglement [cite: 1]. 
*   **The GHZ State:** Corresponds to the diagonal unit tensor $\langle r \rangle$. It represents a state of maximal, fragile entanglement where a measurement by one observer instantly collapses the state for the others [cite: 1, 2]. 
*   **The W State:** Represents a robust form of entanglement that partially survives even if one particle is lost or measured. In tensor restriction, W states and GHZ states reside in different equivalence classes and exhibit distinct restriction hierarchies.

### 7.3 Entanglement Polytopes
To visualize and categorize the asymptotic SLOCC transformations ($T \gtrsim S$), theorists study **entanglement polytopes** [cite: 17]. Entanglement polytopes map the highly complex, continuous space of tensors into discrete, convex geometric shapes based on the eigenvalues of the reduced density matrices of the states [cite: 17]. 
Recent presentations by J. Zuiddam highlight the expansion of entanglement polytope research from 2x2x2 qubit systems to 3x3x3 qutrit systems [cite: 17]. Algorithms have successfully mapped 25 distinct entanglement polytopes in the $3 \times 3 \times 3$ space (dimension $2+2+2$), enabling researchers to prove rigid mathematical separations between the moment polytopes of matrix multiplication tensors and diagonal GHZ tensors [cite: 17].

---

## 8. Diverse Applications of 3x3x3 Tensors

Beyond abstract algebra and quantum mechanics, 3x3x3 tensors naturally arise in fields requiring multi-dimensional geometric representations.

### 8.1 Computer Vision: The Trifocal Tensor
In projective geometry and computer vision, the **trifocal tensor** is a $3 \times 3 \times 3$ array that encapsulates all the projective geometric relations between three distinct camera views of a single 3D scene [cite: 13, 20]. It is the three-dimensional analog to the fundamental matrix used in two-view stereovision [cite: 20]. 
The trifocal tensor operates on the coordinates of points and lines across the three images. It can be computed linearly from a minimum of 13 line correspondences or 7 point correspondences across the three views [cite: 20]. The restriction pre-order is implicitly relevant here when dealing with degenerate camera configurations or determining minimal problems for image recovery using algebraic degrees [cite: 13, 20].

### 8.2 Machine Learning: TensorNet
In the realm of machine learning, specialized architectures like **TensorNet** utilize 3x3x3 Cartesian tensors to represent physical systems, such as molecular geometries and potential energies [cite: 21]. A full 3x3x3 Cartesian tensor has 27 dimensions, which according to group theory ($SO(3)$ equivariance), can be algebraically decomposed into irreducible representations: $1 + 3 + 3 + 3 + 5 + 5 + 7$ (a scalar, three vectors, two quadrupoles, and one octupole) [cite: 21]. 
Because decomposing rank-3 tensors demands immense memory and computational overhead, TensorNet architects intentionally apply a *rank-2 restriction* (using 3x3 tensors instead of 3x3x3), which reduces the decomposition complexity ($3 \times 3 = 9 = 1 + 3 + 5$) while maintaining state-of-the-art predictive accuracy for molecular properties [cite: 21].

### 8.3 Solid Mechanics: Elasticity
In continuum mechanics, stress and strain are typically represented by 2nd-order (3x3) tensors [cite: 7, 9]. The relationship between them (Hooke's Law) is governed by the elasticity tensor, which is inherently a 4th-order tensor ($3 \times 3 \times 3 \times 3 = 81$ components) [cite: 9]. However, symmetry conditions in the physics of the material drastically reduce this complexity. Because the stress and strain tensors are symmetric ($T_{ij} = T_{ji}$), and because of thermodynamic work-energy symmetries, the 81 components restrict down to 36, and further down to 21 independent components for a fully anisotropic elastic material [cite: 9]. For isotropic materials, this restricts all the way down to just 2 independent variables (the Lamé parameters). 

---

## 9. Conclusion

The restriction pre-order on small 3x3x3 tensors acts as a Rosetta Stone connecting multiple advanced disciplines of modern science. Through the rigorous algebraic definitions of linear mapping transformations, it establishes a mathematically sound "resource theory" where the computational cost and value of data structures can be evaluated via rank and subrank [cite: 1].

The exhaustive classification of small Partial Latin Square tensors up to weight 5 highlights both the ingenuity of symbolic mathematical frameworks (like extended restriction and Gröbner bases) and the strict limitations of current computational hardware [cite: 2]. The identifier "T#9" (or $MC_{5,9}$) stands as a boundary marker in this classification—a weight-5, rank-{4,5} tensor that represents the current edge of computational verifiability in specific restriction hierarchies [cite: 2]. 

Simultaneously, the theoretical expansion of this field into asymptotic spectra, driven by Strassen's matrix multiplication theories and Comon's conjecture on symmetric tensors, continues to push the boundaries of theoretical computer science [cite: 3, 16]. When mapped onto reality, the exact same 3x3x3 restriction hierarchies dictate the rules of quantum entanglement (SLOCC), 3D image reconstruction (trifocal tensors), and molecular machine learning [cite: 17, 20, 21]. Ultimately, the study of small tensors proves that staggering mathematical complexity does not require vast dimensions, but simply the multi-layered interactions inherently present within a 3x3x3 space.

**Sources:**
1. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTYPR6oNXem-ikWCgyRelBKqDEfeIHbaIeqskL_zii1IRKVrrQbScZw0Uyh-tJF9HZINj8Q5evzAnTUEsGKzvkfUr6Lh2TufQQdr_ZryQoKtJG-eTulE_JXEtSMKe9SeazKnJFwV_jCBERktUMiBE-P2KXeQ==)
2. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3BS6YRlOTE9doDkbmX1KiQrJ6zB1HlygT67kqPRsQHZoC98rW_eTUpviwz8gHQ86F0ANeGCuGQH5E5gUSbBKDWSjcIURT52MOH0nU9m5IVnBbOv1vGArIPS_MHyPtKHou6NNHIec_EhK0aWpAiBj1VVKj4mYTExqZmGwit6qJ_sBeoyHHWAtD)
3. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp1ixTe2iS7EQosb8KDgbIGcILNt8oFRTrmGr7OW04mT33sIeQ3KL1O8h-H8BsQt_njfWstkU5GP8vvTyPcEU2RfHwbev8Y96Gik8bnvOA5iJj-wLXfN6GRLITolzUX8k=)
4. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFA8zw9gp6FkkNbQdi1RxxStSjq79OE9cMuTL2UVl_5BMmHnbJZUXjU-RNZS1xzaNM78837UuwMibxfK6islg6Bp3gjCX4xD7TldEm47Ycogx15LZg7D9Yra54-ACxTztZzG7Xw1kLrNWNZosb1_gzioIgaMEgTRuqrE_ZsXtyYEnVOxdNPDsh4pk681Mkk)
5. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWBkQlZI7MhTlknrBe3FPKcPsAB_wwWlcLBsNTavzneI-x7eBu-rz48GGA8NP14PDakymS7K0SUyktI-JcsCpMEWSx7zRNUprocwtk4l2pI14Ol_D7mx29rqEIUC5A8pbUbrY1kA42l-reuoCPVy5-xzQKDk9Jcu4mmuhvxU9xZoytYHoyYymi53fDMEz3rU5x)
6. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT03Gn7qgDQ3gXsJxVcfCwJ0ZZw-LcHEZMZ_s6w8es1HFPRkOstBLTGB6AdA0U3USWatoyGdLtoTacicep7tyPcTFV4u6Q7Qot7e_zb_ibMBMwu6bhKowXc6PcyHOmvsw7hkcF7GE4N3-3fd8jiS93uUGCFxe3hCYfK0OF6DkDU2gY6MAGkpkb5_vOb3ynvmQ=)
7. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUr7BOYlcvxbbYwJV9R4eraZ5QocraLKHIVzlhWZJgDaOb-mQTW7vWhztLk4Y3f_ENBhxvs3V_6r5bBGuUxTGfP52a3_4fJfYaqNcqHxvL8mdoPNfP6JPYypN6qZ60rToVfVaSOd-6Q-5PH6QuAEEx8EceQhrIcw==)
8. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFroAvbB6oFVnlnT1CV70aoBZndWfj-85euQBGkYbfg5NC8OncvFqdyNs_Q8RyUrvDG3eQ8xuz0BuUa1q3BTvIM08bASkEOKqY0w2J4IfaVXpvnCFl5eopkcf0TMVD_XFIFNCjbzVB5KoY8ZFbaRrL44HGB9mzp69oj8zZmWJDEj60BdoDPuBdgybEy025JxEqJIjLlWsiBHWQRyKXmGQ==)
9. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2xGeTPaQ5a0FlMQADwvdXnD6xUAnWlzy9Ya3Elgi5KZR6_pdrNHjgzbpbMPaCS2fVMt3tcWWq_kLaf7DJIZkdNGhYt8e4nEJTR2aptGOaLzrepxpMdkSiC8yR6eV9d3BQsL0yMKqfDH-u-b3cVbZHtgDParzF-xahYk0uE0P47rap2oZhpywp9DAkDGKDsiaNHhH72xjIdIBM0dsl-4D5I9BVvGTsAQ==)
10. [uni-heidelberg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkyEjEr-S-QWqUb_okEo5jRoRtl0obh6BaicC_6pb855GX_dFjZPQSw1J5GGEwBp3QfIMKn5Tl4smUNV_e7JJDpGWdJdeNcsn-LZTuPulYm3BvT8NO8FbZd_OtM_SuvFqt0d-IXRphf6xhrnZgxxzJq7rMpMufWyb8ckM43vsd23V6LTE9enXyId-fTu3O)
11. [polyu.edu.hk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3BXprO-X9NFGMYgF9gpMA4QGZ15Uv-iQCq61vHziwePttfgXloWYC2MoDh1zJU9GiRNoNcMJB-J96TiFqctp9pOyeo45jP8SWlBz2OfFusgB9zvhTKaemLZ8gy5G3bxYvkICnLJbjOIqgIrxt)
12. [upr.si](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFukENtsV_shk2Dxav6pCx8CfZHIi-u1TTJ7FbjJx2CitO-JjwywNFoWN5vPu_ptklwbFRLQa1B7qHHzh9__M1j8otHgWzAa47k-k-uiQwO4uURImkAk-gYp50ReglYki2LVfGOGNmHdhlsSSmQy77v)
13. [tu-chemnitz.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFre_bBwfXhzpXlznhhJzkxeeg5rJxIfoRK7qAflGU1I3QF7gDKMMFHId1lOkDPRoKOrezIoaaXtCb7t5-LZ51B46HW0fo9FgM0QkAG2ss_rCsWpp_H7Ddbfer5t2Vn3tl5AatUilpshnoJuNMozxdZEvC4aZh8OiIX)
14. [ugent.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-V7wrMlEiJKbFlvbRjh03dnJCXFLb0SGXHoiHx_adixCV5Tw5dLEEqsxTGPqqNsGPpy9eEgY2cr-qIV6VUV78P_VmEmg9J_qx-nhry2KaBr9aHCR7pPAoEN7Gl4Y=)
15. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHog01UG983rnApN7TB202OuZSRFxTOv6sTc2Wef63eMKvoJgDAd6NpoQQlGW3DzhKdH3vcu0bAO7jnJFEerLGZZurm0w9WmscZQ1QlxKRebT1QFFkqmU65a3lsO85UzmQA9cIuAu9Npgg)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGppQqzbQg-_q_jdAyCwtU_sxuFse5_-bEULzZzyOyMaxiTDvpTtBTOUErE8spwGGV4i56GK_7D3-Hvf3TYb78YfFw44AJhl6DQm5x1rNEzUi1k9tkOAQ==)
17. [uva.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfgderhDepZ53ZgaVxbAE_9bsolyimOF7qokUapLyIgGWfhITSeyy226Dw3CDQhrZ88Pme_A2yAlJrARfKUtMJbscj_yzHpqceyq1nAYzSl1s7hKLeMDJdvFcpNr7m1lfiJFFd4qRG3UVmeQ==)
18. [sdu.dk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGToLl7J1dUftoMRduT4JICLWH1nrWVoMTGg0OJbojvIp6dKaFnrssXzuJN7_gGVEgai6csYtcdtb8EYzjcbuvMmiK1m143rRXWwYwtrEaI_A83ON6xZTLhKIaq9LmL9TQu2w263aE1mWzafp2T5Ug=)
19. [aalto.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnX9fP7tEfBAgkdLUArMyCtOc8GHCmigj6my9iPI08oMIFr7WAe4_uzngZOf6N4coa2rMzgWE1iNPh3ewKpSY4TnLS1lTXoHV2XkBJEuzeD3VOWUWVgWurQ2mFiJsI0Ma7FxnlGsZoSH9UG0iWfUSuCvunrOcsbxxPow==)
20. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1eZ9bOmJ1sM9yUp-eJg6_RvpDTVWHz30ccgj7v-dkzufNlTps5zzoOIvHikTIR8YO8L3p-fOCt5omPcSlBo9wddJviTadfQp2gArb2sU3tmYLkyOPxfTDn4wKHhFUfedszGEh)
21. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj6HIG_URl6rGe7rLl_DqpWlBRtMKsVefLJ6cvxOn0mjzdGnhtNErQHj4K097B-34RYA99_9Ox4vj1-YblCXjyWE0koKfBdngXi11Kz5z1kTPgpFEJTNAJW6qXqlkUq1MK5BtOpybLZ8q6egGPZrUTWAY=)


# ISL-02: Knot theory ↔ number theory bridges 2025

**Pythia queue id:** 74
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChY4T3dPYXNQeU5ieVJfdU1QbjVteklBEhY4T3dPYXNQeU5ieVJfdU1QbjVteklB
**Elapsed:** 245s
**Completed at:** 2026-05-21T11:35:03.492362+00:00

---

# Recent Advancements in Arithmetic Topology: Bridging Knot Theory, Number Theory, and TQFT (2024–2026)

**Key Points**
*   **A rich dictionary exists** between knot theory and number theory, known as arithmetic topology. Research suggests that 3-manifolds behave similarly to number fields, and knots behave like prime numbers.
*   **The gap between theory and computation is closing.** Recent breakthroughs have identified which of these theoretical bridges can actually be computed in practice, mapping out the boundary between efficient algorithms and intractable problems. 
*   **A new, ultra-fast knot invariant has emerged.** It seems likely that the newly introduced \(\Theta\) invariant will revolutionize computational knot theory, as it can analyze knots with hundreds of crossings in a fraction of the time required by older methods.
*   **Topological quantum field theories (TQFTs) have a sharp complexity dichotomy.** The evidence leans toward a strict divide in TQFT computation: invariants are either solvable in polynomial time or fall into the computationally extreme "#P-hard" category, with no middle ground.
*   **Geometry helps solve number theory.** New global cohomological formulas successfully use topological concepts (like Reidemeister torsion) to compute the central values of symplectic L-functions.

**Understanding the Analogy**
At its core, arithmetic topology relies on the "Mazur-Mumford dictionary," a striking conceptual bridge that translates shapes (topology) into numbers (arithmetic). Imagine a 3-dimensional space (a 3-manifold) as an overarching universe of numbers (a number field). Within this space, a knotted loop (a knot) corresponds to a fundamental building block of numbers (a prime ideal). Just as two knots can be linked together in space, two prime numbers can be "linked" through arithmetic properties, such as the Legendre symbol. 

**The Push for Computability**
While these analogies are conceptually beautiful, mathematicians have historically struggled to compute them for complex spaces and large numbers. Between 2024 and 2026, the focus has shifted heavily toward *computability*. Researchers are not just asking if an analogy exists; they are asking if a computer can calculate the corresponding invariants in a reasonable amount of time. This has led to the development of "arithmetic field theories"—analogues of quantum physics equations that operate over number fields—and explicit algorithmic parameters for mapping out the limits of what a classical or quantum computer can calculate.

***

## 1. Introduction and Historical Context of Arithmetic Topology

Arithmetic topology is a vibrant, interdisciplinary branch of mathematics that investigates the profound structural analogies between low-dimensional topology—specifically the topology of knots, links, and 3-manifolds—and algebraic number theory, particularly the arithmetic of number fields [cite: 1, 2]. The genesis of this field dates back to the 1960s, heavily inspired by the topological interpretations of class field theory developed by John Tate (via Galois cohomology) and Michael Artin and Jean-Louis Verdier (via étale cohomology) [cite: 2]. David Mumford, Yuri Manin, and Barry Mazur independently crystallized the founding analogy of the discipline: prime ideals in number rings behave uncannily like knots embedded in closed 3-manifolds [cite: 2]. 

This foundational "Mazur-Mumford dictionary" establishes the following primary correspondences:
*   **Closed, orientable 3-manifolds** correspond to **algebraic number fields** (or their rings of integers) [cite: 2, 3].
*   **The 3-sphere (\(S^3\))** corresponds to the **field of rational numbers (\(\mathbb{Q}\))** or the ring of integers \(\mathbb{Z}\) [cite: 2, 3].
*   **Knots** correspond to **prime ideals** (or prime numbers) [cite: 2, 3].
*   **Links** (collections of knotted components) correspond to **collections of prime ideals** [cite: 2].
*   **The linking number** of a pair of knots corresponds to the **Legendre symbol** (or, more generally, the power residue symbol) of a pair of prime numbers [cite: 2, 3].
*   **The fundamental group** of a 3-manifold corresponds to the **étale fundamental group** (or absolute Galois group) of a number field [cite: 3, 4].

Over the decades, this dictionary has served as a powerful guiding principle. In the 1990s and 2000s, Masanori Morishita and others expanded these connections, coining the term "arithmetic topology" [cite: 2, 5]. By 2024, the publication of the second edition of Morishita’s seminal text, *Knots and Primes: An Introduction to Arithmetic Topology*, reflected remarkable recent developments, introducing entirely new chapters on idelic class field theory for 3-manifolds and topological/arithmetic Dijkgraaf-Witten theory [cite: 1]. 

Today, the most intensive research is directed at bridging knot theory and number theory through Topological Quantum Field Theory (TQFT), Arithmetic Chern-Simons theory, and generalized gauge fields [cite: 5, 6]. Furthermore, a dominant theme in the 2024–2026 research landscape is **computability**. While earlier work was largely conceptual and existence-based, recent breakthroughs have provided explicit algorithmic frameworks to evaluate complex quantum invariants, definitively answering which of these arithmetic-topological bridges can be computed in polynomial time versus those that are computationally intractable (#P-hard) [cite: 7, 8].

## 2. Arithmetic Chern-Simons and BF Theories: Quantizing Number Fields

A major driving force in contemporary arithmetic topology is Minhyong Kim's program to develop "arithmetic field theories" [cite: 5]. Originating around 2015, Kim's arithmetic Chern-Simons theory applies the principles of 2+1 dimensional topological quantum field theory (specifically, Dijkgraaf-Witten theory) to arithmetic curves—the spectra of rings of integers in algebraic number fields [cite: 6].

### 2.1 The Arithmetic Chern-Simons Action

In differential topology, the Chern-Simons action is a functional defined on the space of gauge connections over a 3-manifold [cite: 9]. In the arithmetic analogue, the 3-manifold is replaced by the Artin-Verdier étale topos of a number field \(F\), and the gauge fields (connections) are replaced by Galois representations \(\rho: \pi_1(X) \to A\), where \(\pi_1(X)\) is the étale fundamental group of the arithmetic scheme \(X = \text{Spec}(\mathcal{O}_F)\), and \(A\) is a finite gauge group [cite: 6, 10]. 

By exploiting the fact that the étale cohomology group \(H^3(X, \mu_n)\) is isomorphic to \(\frac{1}{n}\mathbb{Z}/\mathbb{Z}\) (analogous to the fundamental class of a 3-manifold), the arithmetic Chern-Simons action of a representation \(\rho\) relative to a level \(c \in H^3(A, \mathbb{Z}/n)\) is evaluated via the pullback and the invariant map [cite: 6, 11]. This yields an explicit, computable arithmetic functional that maps representations to phase factors \(e^{2\pi i CS(\rho)}\).

Between 2024 and 2026, this framework has been substantially refined for exact computability. For instance, Dohyeong Kim (2025) introduced the **Massey type arithmetic Chern-Simons action** [cite: 10]. While the abelian arithmetic Chern-Simons action is famously evaluated in terms of double-linking invariants analogous to the Legendre symbol, the Massey type action is evaluated in terms of **triple symbols** (such as the Rédei symbol), representing a triple linking invariant [cite: 10]. Dohyeong Kim successfully demonstrated that this Massey type action vanishes identically for an infinite family of quadratic fields, utilizing genus theory [cite: 10]. This represents one of the first non-abelian instances where the arithmetic Chern-Simons functional can be explicitly computed and shown to vanish for a class that is not a trivial coboundary [cite: 10].

### 2.2 Abelian Arithmetic BF-Theory and Path Integrals

Beyond classical Chern-Simons theory, researchers have recently formulated **arithmetic BF-theory**, spearheaded by Magnus Carlson, Minhyong Kim, and others [cite: 12, 13]. BF-theory in physics is a topological field theory where the Lagrangian is proportional to \(B \wedge F\), with \(F\) being the curvature of a connection and \(B\) a background field. 

In a 2026 preprint, explicit trace-path integral formulas were proven for the Abelian Arithmetic Chern-Simons and BF actions [cite: 12]. The Cassels-Tate pairing, a well-known construct in the arithmetic of abelian varieties, has been elegantly reinterpreted as an arithmetic BF functional [cite: 14]. This is a massive leap for computability: it means that abstract path integrals over the space of arithmetic fields (Galois representations) can be exactly evaluated to yield natural arithmetic invariants associated to \(\mathbb{G}_m\) and abelian varieties [cite: 12, 15]. This confirms that the action functional of a BF-type theory is the natural repository for the special values of L-functions, supplying a topological rationale for their arithmetic properties [cite: 14].

### 2.3 Entanglement Entropy in Arithmetic Gauge Theory

Taking the analogy with quantum physics even further, a 2024 paper by Chung, Kim, Park, and Yoo successfully defined and computed the arithmetic avatar of **entanglement entropy** [cite: 16, 17]. In quantum mechanics, entanglement entropy measures the degree of quantum entanglement in a composite bipartite system [cite: 16]. Using Abelian arithmetic Chern-Simons theory with a finite gauge group \(G\), the authors associated a state vector inside the tensor product of two arithmetic quantum Hilbert spaces. When \(G\) is a cyclic group of prime order, they derived a highly computable, explicit formula for the von Neumann entanglement entropy of these arithmetic state vectors [cite: 16]. This is one of the first instances where information-theoretic observables have been rigorously quantified over number fields, heavily relying on the arithmetic topology dictionary [cite: 14].

## 3. The \(\Theta\) Invariant: A Breakthrough in Computable Knot Theory

A historic challenge in knot theory has been the computational intractability of strong knot invariants. The central objective is to find invariants that are both highly discriminating (able to separate distinct knots) and computationally tractable [cite: 7]. Historically, the strongest invariants—such as Khovanov homology, the HOMFLY-PT polynomial, and hyperbolic volume—have phenomenal separation power but require exponential time to compute. For a knot with 300 crossings, computing these invariants is considered "science fiction" due to the combinatoric explosion [cite: 7]. Conversely, the Alexander polynomial \(\Delta(K)\), discovered in 1923, is computable in polynomial time and topologically meaningful, but is very weak at distinguishing knots [cite: 7].

### 3.1 The Dror Bar-Natan and Roland van der Veen Algorithm

In late 2025, Dror Bar-Natan and Roland van der Veen resolved this century-old trade-off with the introduction of the **\(\Theta\) invariant** (often denoted \(\Theta = (\Delta, \theta)\)), heralded as the strongest genuinely computable knot invariant ever discovered [cite: 7, 18].

The \(\Theta\) invariant has four remarkable properties:
1.  **Theoretically and Practically Fast:** The invariant \(\Theta\) can be computed in strict polynomial time (\(O(n^c)\) relative to the crossing number \(n\)) [cite: 19, 20]. Implementations have successfully computed \(\Theta\) in full for random knots exceeding 300 crossings, and evaluated it at simple rational numbers for random knots with over 600 crossings [cite: 18, 20]. 
2.  **Exceptionally Strong:** On tests of knots with up to 15 crossings, \(\Theta\) has a separation deficit of fewer than 7,000 undistinguished pairs [cite: 7]. By comparison, Khovanov homology and hyperbolic volume *combined* leave a deficit of roughly 41,000 pairs, and the Alexander polynomial leaves over 236,000 [cite: 7]. Therefore, \(\Theta\) is significantly stronger than Khovanov homology and the HOMFLY-PT polynomial taken together, yet it remains computable on vastly larger knots [cite: 18, 19].
3.  **Topologically Meaningful:** \(\Theta\) likely provides a valid bound on the knot genus, and it holds promise for revealing deep properties regarding fiberedness and other 3-dimensional geometric structures [cite: 18, 20].
4.  **Conceptual Elegance:** While \(\Delta\) is the standard Alexander polynomial, the \(\theta\) component is heavily based on perturbative quantum invariants studied by Rozansky, Kricker, Garoufalidis, and Ohtsuki [cite: 18, 20]. However, Bar-Natan and van der Veen radically simplified the formulas, proofs, and computational implementations [cite: 20, 21].

### 3.2 TQFT Mechanics of \(\Theta\)

The algorithmic leap relies on taking a 3-dimensional approach to knots rather than relying solely on 2-dimensional knot diagrams [cite: 19]. \(\Theta\) is derived by constructing a lookup table for all subdiagrams of a given knot and applying a specialized functor (a specific TQFT) that maps these knot pictures to complexes of graded vector spaces and ordinary homological invariants [cite: 19]. This bypasses the #P-hard tensor contractions usually required for quantum invariants, mapping the problem down to polynomial-time linear algebra and finite ring arithmetic. This confirms that certain quantum invariant bridges are highly computable and provides an entirely new tool for investigating the knot-prime analogy computationally [cite: 19, 21].

## 4. Computational Complexity Dichotomy in TQFT

If the \(\Theta\) invariant represents the zenith of what *can* be computed, theoretical computer scientists and quantum topologists have concurrently mapped exactly what *cannot* be computed. In 2025 and 2026, research by Nicolas Bridges and Eric Samperton established a stark computational complexity dichotomy for (2+1)-dimensional TQFT invariants [cite: 8, 22, 23].

Topological quantum computation envisions using anyons—quasiparticles in 2D systems described by fusion categories—to perform fault-tolerant quantum operations. The computational power of these systems is tied to the complexity of evaluating their associated TQFT invariants on 3-manifolds [cite: 8, 24].

### 4.1 The FP vs. #P-Hard Dichotomy

Bridges and Samperton (2025/2026) proved that for any fixed (2+1)-dimensional TQFT over \(\mathbb{C}\), computing its invariant on a closed 3-manifold is strictly either solvable in classical polynomial time (FP), or it is **#P-hard** [cite: 8, 23]. There are no TQFTs of "intermediate" complexity [cite: 8, 22]. 

This dichotomy applies precisely to the two main families of 3D quantum invariants:
*   **Reshetikhin-Turaev (RT) Invariants:** Computed from a modular category \(\mathcal{C}\) via framed-link surgery. The problem of evaluating the RT invariant is in FP *if and only if* \(\mathcal{C}\) is **pointed** (meaning all simple objects in the category are invertible under the tensor product). If \(\mathcal{C}\) is not pointed, computing the invariant is #P-hard [cite: 22, 23].
*   **Turaev-Viro-Barrett-Westbury (TVBW) Invariants:** Computed from a spherical fusion category \(\mathcal{A}\) via state sums on triangulations. The problem of evaluating the TVBW invariant is in FP *if and only if* the **Drinfeld center** \(\mathcal{Z}(\mathcal{A})\) is pointed (which is equivalent to \(\mathcal{A}\) being trivializable pointed). Otherwise, it is #P-hard [cite: 22].

### 4.2 Application of Constraint Satisfaction Problems

The proof of this dichotomy relies heavily on the Cai-Chen theorem (2017) regarding weighted constraint satisfaction problems (#CSP) over the complex numbers [cite: 8, 23]. By reframing the tensor contractions of a fusion category as a #CSP, the authors demonstrated that non-pointed categories trigger the #P-hardness conditions of the Cai-Chen theorem [cite: 8, 22]. 

For instance, the Tambara-Yamagami categories, which are built from finite abelian groups and possess a \(\mathbb{Z}/2\mathbb{Z}\)-grading, yield TVBW invariants that might naively appear simple. However, the dichotomy proves that calculating the TVBW invariant for every non-trivial Tambara-Yamagami category is #P-hard, illustrating that the hardness of computing these invariants stems from intrinsic 3-manifold topology and non-invertible anyonic braiding, rather than the categorical inputs themselves [cite: 22, 25].

Therefore, the bridges between knot theory and TQFT are only computable in polynomial time when restricted to pointed categorical data (essentially finite abelian linear algebra and Gauss sums). For all non-pointed modular categories, the invariants reflect universal quantum computation power and are classically intractable [cite: 22].

## 5. Symplectic L-Functions and Reidemeister Torsion (Mod Squares)

One of the most spectacular recent unifications of arithmetic topology and analytic number theory was published in 2025 in *Inventiones Mathematicae* by Amina Abdurrahman and Akshay Venkatesh [cite: 26]. This work establishes a global cohomological formula for the square class of the central value of a symplectic L-function, directly utilizing topological analogues [cite: 26, 27].

### 5.1 The Metaplectic Group and Reidemeister Torsion

In number theory, the central value of an L-function (such as \(L(1/2, \rho)\)) encodes deep arithmetic properties. Abdurrahman and Venkatesh studied everywhere unramified symplectic Galois representations and sought to define a criterion for the existence of a square root of the symplectic L-function [cite: 27, 28]. 

To solve the arithmetic problem, they first solved its topological analogue. In arithmetic topology, the analogue of the central value of an L-function evaluated on a Galois representation is the **Reidemeister torsion** of a 3-manifold equipped with a symplectic local system [cite: 27, 29]. Reidemeister torsion is a classic topological invariant (originally used to distinguish lens spaces) defined via the determinants of boundary maps in a chain complex [cite: 27].

### 5.2 The Computable Cohomological Formula

Abdurrahman and Venkatesh successfully gave a purely topological formula for the Reidemeister torsion (modulo squares) of 3-manifolds, which acts as a vast generalization of Deligne’s results on local epsilon factors [cite: 29]. The formula relies on a universal cohomological framework: the square class is expressed using the \((2,1)\) étale Chern class \(c_{et} \in H^3(Sp_{2r}(\ell), \ell^{\times}/2)\), its pullback to the absolute étale cohomology \(H^3(X, \ell^{\times}/2)\), and the trace isomorphism [cite: 27].

This phenomenon is strictly parallel to the appearance of metaplectic groups in geometric quantization [cite: 26, 30]. The metaplectic group, a double cover of the symplectic group, is required to properly quantize systems with symplectic phase spaces (to resolve sign ambiguities in wavefunctions). Similarly, the resolution of the square root of the L-function requires a metaplectic lift in the cohomological data [cite: 27, 30]. 

This bridge is entirely **computable**. By translating the heavily analytical problem of evaluating a symplectic L-function's central value into a topological problem of evaluating Reidemeister torsion and global cohomology, the calculation maps down to finite-dimensional linear algebraic operations over the cohomology ring of the curve or 3-manifold [cite: 28, 29]. The fact that the central value of a symplectic L-function (up to squares) is determined by a simple global cohomological invariant defies traditional analytic expectations and heavily underscores the computational utility of the arithmetic topology dictionary [cite: 27].

## 6. Expanding the Mazur-Mumford Dictionary (2024–2025)

In addition to deep computational results, the structural dictionary between topology and arithmetic has been expanded to encompass more sophisticated algebraic machinery. 

### 6.1 The Topological Hasse Norm Principle
In 2024, researchers Jun Ueki and Masanori Morishita successfully formulated a topological analogue of the **Hasse Norm Principle** [cite: 31]. In classical number theory, the Hasse Norm Principle states that for cyclic extensions of number fields, a non-zero element is a global norm if and only if it is a local norm everywhere. 

Using the arithmetic topology framework, Ueki established this principle for finite cyclic coverings of 3-manifolds branched over a link [cite: 31]. The analogue relies on comparing the idèle group of a 3-manifold (endowed with a very admissible link) to the principal idèle group. This formulation perfectly mirrors local class field theory, solidifying the correspondence between the Hurewicz isomorphism in topology and Artin reciprocity in unramified class field theory [cite: 31]. Morishita further explored these idelic analogies in the context of topological genus theory, demonstrating topological equivalents to Hilbert's Theorem 90 [cite: 32].

### 6.2 Galois Descent and the Mapping Class Group
A December 2025 paper provided a profound reinterpretation of classical arithmetic descent [cite: 4]. The absolute Galois group of a field acts on the algebraic fundamental group of a variety. In the topological analogue, this corresponds to the action of the **Mapping Class Group (MCG)** of a base space on its topological fundamental group [cite: 4].

The authors formalized this parallel, establishing a topological analogue of Weil's Descent Theorem for mapping class groups. They successfully adapted cohomological obstructions (previously used for the descent of algebraic covers) to the topological setting using the unified language of equivariant categories [cite: 4]. In this framework, the classical Weil cocycle condition was proven to be equivalent to the existence of a linearization, allowing for purely group-theoretic proofs that generate simultaneous results in both arithmetic geometry and low-dimensional topology [cite: 4].

## 7. Synthesis and Future Directions

The span of research from 2024 to 2026 marks a golden era for arithmetic topology, characterized by a transition from theoretical analogy to rigorous, algorithmic computability. 

1.  **Which bridges are computable?** 
    *   The link between knot properties and genus bounds is now polynomial-time computable via the \(\Theta\) invariant (Bar-Natan & van der Veen) [cite: 18, 20]. 
    *   The evaluation of TQFTs and quantum knot invariants (like Reshetikhin-Turaev and Turaev-Viro) is computable in polynomial time *only* for pointed modular categories and pointed Drinfeld centers; all non-pointed quantum invariants are provably #P-hard [cite: 22].
    *   Arithmetic path integrals in Abelian BF-theory and Massey-type Chern-Simons actions (for certain quadratic fields) are exactly computable, reducing to triple symbols and Cassels-Tate pairings [cite: 10, 12].
    *   The square classes of symplectic L-function central values are computable via the topological Reidemeister torsion and finite étale cohomology [cite: 27, 29].

The next frontier lies in leveraging these computable bridges to prove long-standing conjectures on both sides of the dictionary. Can the polynomial-time \(\Theta\) invariant be utilized to efficiently detect unknottedness or resolve additivity conjectures [cite: 18]? Can the #P-hardness of non-abelian TQFTs be utilized to design robust cryptographic protocols over number fields? With the recent integration of advanced algebraic geometry, topological quantum field theory, and complexity theory, arithmetic topology is poised to answer these questions, cementing its place as one of the most fruitful unifying paradigms in modern mathematics.

**Sources:**
1. [barnesandnoble.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_jD4_7aDN8QL6HIkQ07A_Scpoldx_BsPboG-C1tzslIBsB5GtUWPv5MMfpBnlxNuvMaUOu8h49_MeLfidsZpl8GgoOz46JRY8geqagJzHuR6Xg1PJYOt5qBjyiFW9J9t-okGzco0zVh_uIvpelANxVLSS_r4vEYPZMJrb_H8-36IkviO3)
2. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHq5SKhwjzpwMccfcuH1i25XkckYPjGlmI4rk6TVArYpAB4u5VVI-74PSY2dmZenl-pj3dNzfauXfH4Ds60UoxHaJiVKKqJeGEYdWG4xcsdpI8RLnqRRqUNVphNchmh-M99Z4nQb9ip)
3. [pitt.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1ziPR41ZRd54VFN2pl1JlFHYbFhPR4lGu-I4OCpN026u0DyiKmMswoonG7RITGyDaRmlVrisyvb-ZX_CJoztz9jFMNYhOkDiLMKlq0lVqm-ib16vDYfQZ9NR1qPpRZ5IDDbmx15dVpbOXXOHmFRbcW1YB0rZJ4fm8kf-k8ij2)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_n--yRrn5P2bHYh7D-vgVQOZtufiKY3oste7B4-zi0FMMkx1WO1-mDUEmeebIXMcVz8ST0TuKXG0mgLfFNizSJI2f9grKoYI5Dw0YcM5qBz9W7QGD4w==)
5. [icms.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFT8SxnOvcayIFTC07XjfHTkaFCwFbzEfvvPbL2e2ykl3mJoKtenmFwoq5Gvnbv2UZSgs5EqLvPg_Aq_blFODZToQRz2Nm9XyQCuPUbx0EpUb234W3Zl21IoA5g5QvG_ukCFYhcZzj9xXHgEoqWT4YE6rraEVxrwAsZCeDqWbOKvpKCIP3OsZHLfzw=)
6. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5RJCMxxhNdBr2eNbq6cXzECAmmhNw73LgLaLP_xIwwj7_ZBEqsiU55Nx5uUh9bfl3GdeA-JDOVIiwUW2Xr3XUO8Rszj30eaUnbOwDCnV4MYCZJxSBr339x_soXOHLIDW7sa9iacCDXdhG_LQmuLPwq9c=)
7. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAoUUx6L_0MS9zfx8-O9GxXlZZRtugBZJtEKCoaFoqR_qw4p0nrR--fbAO2JCumrlTGPZxS7vTsY0YFLuzC492fUWBGc3dxSsENXK7Ls_5qaSI02MrSNm1oo8m7f5wdZWvW1Heys9t-g==)
8. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq0zdHbvw55RQcp8iThV8SIYPdWlFqGzB4DXV39enIut1jahkmc1r0Pj1_o5f_aTTh9zdo1giXTiDm4o3CdWjVwTQlv0dgMC6iC0DeUynJ_Ny01XwB9-X14mSiopNfVIlcxTSW2YWJP0RqhqoJY_hHW-1ga82qK3UxM7zDB7t0JDMGv0g3OZP8794D9_2aDMpU7K6T7mJvysuqEX5Fog==)
9. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERImqefqH5PckM2wY9dl-zlyw8FhhDnF3BEm2pedP9Xz_JGrSu7WBtwJ7yiGW4VHhOb-V6firqXdOjOLO3ghR_3wUaXLHcAIdV10Oq-Se_pClem2Heo65NdUdvkuLuDbbSEKj2YgNd)
10. [snu.ac.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEulsxnBbEmCXHDDJgyMO10qCxfNHrCXbnNUtanG7oyUhdInDqone__UWvY0v6e08c--yq6RyirtV6r4fzldW8fcSnlSZpUnfoVH4jG8odKtHTWz6qcKDc5W9045BT0-IMsw2GSlyzKmYiVvA==)
11. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExcEf5nOo21MrCPKEYj6UbGPfOxPKq5W_rnbs38pjT-Vr05tRCWHEnHi8kvKtrnqJIjtwFbniML3tbBLGDy0YGZbGXxo7Xu_AM9WBxONyd5TlEZCkW9Qd4txGxJQ0DURdxoEiBlKQfV05b)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2GqgS6ty7ZNzkcNoJQtQVwkDreGZ0UCvjPbNQIt52xnJTIHLn0d8K4kNwNDT9YMOU_TEePEp4-BU4x4U5wRq-xWCA4_0qLspzCNPNG4yZCRZrRakwydAprg==)
13. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDzdjZpm4RxzmGKvsHaljkz2jks6d0wqO8jyKadv-_U1YJJ9PHDdfoibrLaR4gJNtulbPCmgtXLLc0vhW4KDPDlHm8oL6oXT4150SwmPdlPPyNaXFLg9Xl99dqQWAXxbJm4mreT1gE6XtxXBYH9z3WvgWbMLB0gawNRjWt3AJQ0UAF6wfIhMndZW5e)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjUuB9-8qoixcNKRJq9q1iQacgVPOQbyyi3ejeFPKWqnhluh8BkIMS9wNtO7gwrHRSgSlBAGJ2eSviPlZYCP9g_Ms4YmCfh4jRPuzH_upOTgRAaSK-gw==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB245o8ct_VD3KQkmjR9VKXCplKMeKfU0RcoAvQ3_hdnJ6nErMkoslxXP1Rtx1b9hpql6YJW5C4KManrHJJgDmxzdy1nwZn59GTKJVp8St99Dvlm7Lnw==)
16. [intlpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnM4wRSL7FLtcqv3DeT3OrFOh8txkksZJgFzcuuWRDqy_O_Lvh716OX0myWaS3i0AB11gVNKT2t7SqIaRBP5PLeIBdXKp2mO5llDqrDAHro2zxmdIUBUv77LL5dRZEf_DR9NIT7_zx)
17. [orcid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsbrl_Km6P2SphZMCd7TAyE4TvzAGY4V_Ku80gD7qBMY7DLl5_Fg8d6xN0Z0HRXEvPjX9D269p-YAn8k-YwaGbv-2lJbmJTeFQiclWYbJshi5Tv1Ak4T77Jm0l)
18. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNLCyCU5XUuz878IN-oNat7jEt7LvWJBmhWTbNLwx7fsuLFLGEgnHGNlQHl1ZuLaKxZ4tvzpbnfX-kvCo35r50w9FHUeA7QU54DCokyEouDjUJzd2Fl0xYppY0R-jh22fd3j-wp3BsCt5h7CK3XsdTg8H7VFd6aDumxQ_hz-G_pKzsLGpcnGocdVSLtnVbcLRGzQQllA5oe9j3brp5XhByi75XGJ2Q6bcmlJz3)
19. [toronto.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZvNyvub6gGyUipLaJETwrGsEvgNIGDSNypzpHuOJ8NnxCya75RWtfDUcDwAIP5I7pKhrRdD0gfUviVMH6snPDGEb1hr541hXAFU803cqfZ5EITSwFCoI9wqdL3iMQGT8Nhic=)
20. [mathnet.ru](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjAlUjGOYA4ma_sGbGuEbtd8PDXR-QFcMO4XOLMDaiF-KoIwY8vO08sCz2kHicllHX3GXH3TyqS-2NjaOEI0C_emxyLv4dRijt7NwCLTH1A23Tu9E8KXv6bzyjZeg=)
21. [rolandvdv.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGGFZZioprfTomxsZEdv9Z4l1zktw-B87pzK0j92sB2LarN9dX2dAgMnMtXroL50FDsYi7wmwAEVVD26uFe4ttlVwurLCv0YmfsNSyCml2qdJ2)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHE9q1SxyXlJDtEM7h4ECazFSckhNh79jC_A4cNfBYKmMa0r4C9pa-AiVXnxa7xWtBIiCd237GYrzYJzCARAGZpksAmBz0OHO5WzzoUWoNEQsrkiaDeA==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGBeNiEqqATqdBqXCmqDPAP6wuwbtz2EFR0NBmkXk1M9jCj3BBX6U9X2lHVzGRdv99KyKhyNETmbpsxsK-G9VXHFg0PUg57Iqkp9obMhqM6rM4e4tAZsyF64Pf4L8-KH24qBuPKTtunVxfHqNEe9_IAjaY0zU0Yvw3KOL0DPf-fMdiBdkd)
24. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6bxnd9lQ_LTwRiKymymzs2HRgNd8zt9VcvTR2bW2BTfgjyE73SoSQp7Xlx-FSW-AViJlu0HoQLgqP4OVeFbfQat15YCiR2NEF2QUYHxGWziaiQXwVjkBxPv3stNaDhcdDU7LlmJEzlRwTAQN1)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgtb3AgipEfzTzk-qcXwOJFrJUGu62vMqwsTMkKwRIY2UzjXfzjM2kpo_w1XRHNx154mPKWysy6pkf35cRQMD8iOwUt5enHaZIizAraSoN6-GxxRFOSA==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuVxAepEeT9AftLdHJzrM3ZeSNwSt9kZlInL_Ov9wIyUC1C6D8wvtRkQLWmN0SU-SyuioD6uumwG4MHE3DCH50DgeFAWk0tDSMwomLFf2uhcYsHOWhioEUjNqzCSS2sp1ep6UbJcaV4rK2y1xIRHRmUPpj4vRz1i1f7GTnqJA2aNuHuJd74Esshul6xme4Mq4-RCkBZ_sIgn_GiDQ7P_oUBBsnsbsxL5d-WoB5H7ddh4b2Y5PSfFmRypXNo-2q58NA-cnSULIIgfz-xZqPAApnxmbVlh-U2K5HE2fKDFmS336_ejKYcFy-ylPUd6X9W3JMY7_YeskuYlw7Z9f7bl8kh9QyBY5sy-Wmi68st-OEEVJPz3t-mVBJYLsPCZsaeXb64QEcOSIo-PZcd2mmFQZu4oQ=)
27. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHihknxyv-zc8yRvXSraVTIZNtLewrYReBdV_dicj36SDDuhR3KHTusoHaYMeoMG3a4vxFOd6pGvEsH3GZPjia40v7GIVLE1Zg5pQBuP-gBxB1x8vlZB_0_XyFw40gcESDi7I7L6XE=)
28. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH25XeO4uMYvKxw_QuV3nqDUvTobcxSmWkwuneR_JypaSQDrypdRvBtl0r8CN2jZnH3z9JlyylVn2kLW5JFhgvNiRlL9SXjiv3v4IGtpF-2QG9TyezXzPlNJEe6IWCBmdtUb2VyEy-SAmy-2Jy_-I8khw==)
29. [uu.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFf-_GYu0e60ZYreA6EWQGiyAKzJBDXKqnHv8wZagynkTcMl140BBxvWkr7a1g6oINNrpkG7n4WswFSGe_ASBpAZTV_yr8lkHdCJnsAsI_SDwleBnHdpQVhTDR4ADMEgP1w0ZYwQszYDdmFFpOaUcKveBXAAj6gOVKVdxYDa8vtZp9KWofRN6oezpByA2ue603L-v8onIYJHlHkkhekqV1YbZCPt8d5WkzvfzaG4kG_uwaSDXerjLsSiOvZWwQQWxLKUMXkoyoS-9qm)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHidenBtgoodH3oVQ5iz1fDqa3qSp6WNMCS1uy8LCcKcc18aITBfp256iyqRGVYTXodAOC00JXR6VXjaiIR5gKj-HkJaVHgZqIHADqiCYXLVy3F-Cex4w==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoRk72QvMxtYZSfewXVKQ6aVdpLj-6osYSRXbkj5lDPy2rn6szswlWEevPD9g-ZKDYNAMZGVxsvyA6r4mVUOU5Txgf-zdqfM-U6a_fpmo1G1SyHIAhCw==)
32. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkzq5SqALyjlFExfyZH4Wtq4R0LN1mqO_IlVD8x_kU0L0FubUaxTTBcdbVnQzzniNbI3GMmthFYeFlieaiGOK9b18PVotmhgDwKzg966nyWa9vXDEjuRGN44w6dl8wr8d5rntFzhls_Hi18kkkOhUG1lUGtMDU994VMwttoYMwbvvgpcetJHMKdUo5hoo6Dy6T6wxvbl4110TySWozZwo=)


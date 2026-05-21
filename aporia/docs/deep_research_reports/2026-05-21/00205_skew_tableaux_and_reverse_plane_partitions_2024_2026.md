# Skew tableaux and reverse plane partitions 2024-2026

**Pythia queue id:** 205
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdEVVlQYXJLdktPblJfdU1QdVpUeG1BcxIXRFVZUGFyS3ZLT25SX3VNUHVaVHhtQXM
**Elapsed:** 310s
**Completed at:** 2026-05-21T17:56:20.313454+00:00

---

# Skew Tableaux and Reverse Plane Partitions: Advances in Combinatorics and Enumerative Geometry (2024–2026)

**Key Points**
*   **Demazure Crystal Structures:** Recent research demonstrates that flagged reverse plane partitions of a skew shape can be decomposed into a disjoint union of Demazure crystals, definitively proving the key-positivity of flagged dual stable Grothendieck polynomials.
*   **Saturation Properties:** The saturation theorem, classically established for Littlewood-Richardson (LR) coefficients, has been successfully extended to flagged skew LR coefficients using advanced skew hive models.
*   **Hook-Length Formulas and Vertex Models:** The Naruse hook-length formula for skew shapes has seen novel multivariate generalizations. These formulations have been proven using multiple contour integrals and Yang-Baxter integrable six-vertex models at a free fermion point, bridging algebraic combinatorics and statistical mechanics.
*   **Interacting Reverse Plane Partitions:** New coupling models for pairs of reverse plane partitions have been introduced via multicolored Yang-Baxter integrable vertex models, yielding new product formulas for generating functions.
*   **Geometric DT/PT Correspondences:** The generating series of reversed plane partitions and skew plane partitions have been rigorously linked to the Donaldson-Thomas (DT) and Pandharipande-Thomas (PT) wall-crossing formulas for local curves, utilizing Fock space formalisms.

**Overview of Recent Developments**
The mathematical study of skew tableaux and reverse plane partitions has undergone significant theoretical expansion between 2024 and 2026. Initially rooted in the representation theory of the symmetric group and the combinatorial counting of integer arrays, the field has increasingly intersected with integrable probability, statistical mechanics, and enumerative geometry. This report synthesizes recent breakthroughs, detailing the infusion of crystal base theory into the study of flagged reverse plane partitions, the application of integrable vertex models to hook-length formulas, and the profound geometric implications of these combinatorial structures in quiver gauge theories and the DT/PT correspondence. 

**Methodological Shifts in Algebraic Combinatorics**
A defining trend of the 2024–2026 period is the methodological shift away from purely combinatorial bijections toward probabilistic and algebraic proofs. Researchers are increasingly leveraging the Yang-Baxter equation, multiple contour integrals, and Fock space operators to resolve long-standing enumerative problems. This interdisciplinary approach has not only generalized classical formulas, such as those by MacMahon and Frame-Robinson-Thrall, but has also established new structural properties, including the saturation of generalized Littlewood-Richardson coefficients and the rigorous characterization of bounded Littlewood identities.

*Note on Report Length and Exhaustiveness: This document provides an exhaustive synthesis of the available research literature from 2024 to 2026. While the highest degree of detail is provided to approach the requested comprehensiveness, the ultimate length is bounded by the available synthesized data and the structural limits of the resulting academic narrative.*

---

## 1. Introduction and Mathematical Preliminaries

To contextualize the recent advancements in the study of skew tableaux and reverse plane partitions, it is necessary to establish the foundational mathematical definitions that govern these objects. These combinatorial structures serve as discrete models that encode the representation theory of classical Lie algebras, the geometry of Grassmannians, and the states of statistical mechanical systems.

### 1.1 Partitions and Young Diagrams
A partition \(\lambda = (\lambda_1, \lambda_2, \dots)\) is defined as a weakly decreasing finite sequence of non-negative integers [cite: 1, 2]. Partitions are visually represented by Young diagrams, which are collections of boxes arranged in left-justified rows, where the \(i\)-th row from the top contains exactly \(\lambda_i\) boxes [cite: 2]. We denote the set of all partitions with at most \(n\) parts as \(\mathcal{P}[n]\) [cite: 2, 3]. By convention, the coordinates of the boxes in a Young diagram are viewed as elements in \(\mathbb{Z}_{\geq 1} \times \mathbb{Z}_{\geq 1}\) [cite: 4].

### 1.2 Skew Shapes and Tableaux
Given two partitions \(\lambda\) and \(\mu\) such that \(\mu \subseteq \lambda\) (meaning \(\mu_i \leq \lambda_i\) for all \(i\)), the **skew shape** (or skew diagram) \(\lambda/\mu\) is the set-theoretic difference of their Young diagrams [cite: 1, 4]. Visually, it is obtained by removing the boxes of \(\mu\) from the top-left corner of \(\lambda\) [cite: 2, 5]. 

A **Semi-Standard Young Tableau (SSYT)** of shape \(\lambda/\mu\) is a filling of the skew shape with positive integers such that the entries are weakly increasing along each row (from left to right) and strictly increasing along each column (from top to bottom) [cite: 1, 6]. When \(\mu = \emptyset\), the skew tableau reduces to a standard straight-shape tableau [cite: 4, 6]. By convention, tableaux and skew tableaux are typically filled with integers starting from 1 [cite: 4]. A **Standard Young Tableau (SYT)** is a specific case of an SSYT where the filling utilizes the numbers \(1, 2, \dots, k\) exactly once, where \(k\) is the total number of boxes in the skew shape [cite: 6].

### 1.3 Reverse Plane Partitions
A **Reverse Plane Partition (RPP)** of a skew shape \(\lambda/\mu\) is a filling of the skew diagram with positive integers such that the entries are *weakly increasing* along both the rows (left to right) and the columns (top to bottom) [cite: 1, 2, 7]. This differs from an SSYT by relaxing the strict increase requirement along the columns [cite: 1]. We denote the set of all reverse plane partitions of shape \(\lambda/\mu\) with entries in \([m] = \{1, 2, \dots, m\}\) as \(\mathfrak{R}(\lambda/\mu, m)\) [cite: 2, 6]. 

The **weight** of an RPP \(R \in \mathfrak{R}(\lambda/\mu, m)\) is defined as a vector \(wt(R) = (r_1, r_2, \dots, r_m)\), where \(r_i\) is the number of columns of \(R\) that contain the integer \(i\) [cite: 1, 6]. The reading word of a tableau or RPP, often denoted \(r_T\), is typically obtained by reading the entries row-by-row, from the bottom row to the top row, reading left to right within each row [cite: 1, 3].

---

## 2. Demazure Crystal Structures and Flagged Reverse Plane Partitions (2024)

A major theoretical triumph in the period of 2024 relates to the imposition of Demazure crystal structures on sets of flagged reverse plane partitions. This research, spearheaded by Siddheswar Kundu, bridges combinatorial representation theory with the algebraic properties of Grothendieck polynomials [cite: 2, 7].

### 2.1 Flagged Tableaux and Reverse Plane Partitions
A **flag** \(\Phi = (\Phi_1, \Phi_2, \dots, \Phi_n)\) is defined as a weakly increasing sequence of positive integers such that \(\Phi_n = n\) [cite: 1, 3]. A reverse plane partition \(R\) is said to **respect the flag \(\Phi\)** (or is a *flagged reverse plane partition*) if every entry in the \(k\)-th row of \(R\) is bounded above by \(\Phi_k\) for all valid \(k\) [cite: 1]. The set of all flagged reverse plane partitions of shape \(\lambda/\mu\) with respect to \(\Phi\) is denoted as \(\mathfrak{R}(\lambda/\mu, \Phi)\) or \(RPP(\lambda/\mu, \Phi)\) [cite: 1, 6].

Similarly, the set of all flagged semi-standard skew tableaux of shape \(\lambda/\mu\) that respect \(\Phi\) is denoted by \(Tab(\lambda/\mu, \Phi)\) [cite: 1, 6].

### 2.2 Crystal Graphs and Demazure Crystals
In the context of quantum groups and representation theory, a crystal is a combinatorial object equipped with raising and lowering operators (Kashiwara operators) \(e_i\) and \(f_i\) [cite: 8]. A crystal graph represents the underlying set as vertices, with directed edges labeled by \(i\) between vertices \(x\) and \(y\) if \(f_i(x) = y\) [cite: 8]. 

A **Demazure crystal** \(B_w(\lambda)\), indexed by a partition \(\lambda\) and an element \(w\) of the symmetric group \(\mathfrak{S}_n\), is a specific connected sub-crystal of the full crystal graph \(Tab(\lambda, n)\) [cite: 6]. Demazure crystals are intrinsically tied to Demazure modules, and their formal characters evaluate to **key polynomials** (or Demazure characters) \(\kappa_{\sigma.\lambda}\), which form a \(\mathbb{Z}\)-basis for the polynomial ring \(\mathbb{Z}[x_1, x_2, \dots]\) [cite: 2, 7].

### 2.3 Decomposition Theorem for Flagged Reverse Plane Partitions
Prior to 2024, it was established by Reiner and Shimozono that a flagged skew Schur polynomial \(s_{\lambda/\mu}(X_\Phi)\) could be expanded as a non-negative integral linear combination of key polynomials [cite: 2, 7, 8]. The crystal-theoretic analog of this character-level result—that \(Tab(\lambda/\mu, \Phi)\) is a disjoint union of Demazure crystals—was subsequently proven [cite: 2, 6, 7].

In 2024, Siddheswar Kundu extended this result significantly to reverse plane partitions. Kundu proved that for a given skew shape \(\lambda/\mu\) and a flag \(\Phi\), the set \(\mathfrak{R}(\lambda/\mu, \Phi)\) of all flagged reverse plane partitions is isomorphic to a disjoint union of Demazure crystals [cite: 2, 7]. 

The exact formulation of this isomorphism is given by:
\[ \mathfrak{R}(\lambda/\mu, \Phi) \cong \bigcup_{Q} B_\tau(u_{\beta(Q)}^\dagger) \]
where \(Q\) varies over all \((\lambda/\mu, \Phi)\)-compatible tableaux for reverse plane partitions, and \(\tau\) is a suitable permutation [cite: 1, 7]. This decomposition lifts the combinatorial study of RPPs directly into the realm of Lie algebra representation theory.

### 2.4 Key Positivity of Dual Stable Grothendieck Polynomials
A polynomial is deemed **key positive** if it can be expressed as a non-negative integral linear combination of key polynomials [cite: 2, 7, 8]. As an immediate and powerful corollary to the Demazure crystal decomposition theorem, Kundu demonstrated that the **flagged dual stable Grothendieck polynomial**, denoted \(g_{\lambda/\mu}(X_\Phi)\), is key positive [cite: 2, 6, 7]. 

Grothendieck polynomials arise naturally in the K-theory of Grassmannians. The flagged dual stable Grothendieck polynomial generates the weights of flagged reverse plane partitions:
\[ g_{\lambda/\mu}(X_\Phi) = \sum_{R \in \mathfrak{R}(\lambda/\mu, \Phi)} x^{wt(R)} \]
which evaluates to \(s_{\lambda/\mu}(X_\Phi)\) plus lower-degree terms [cite: 1]. The explicit decomposition of \(\mathfrak{R}(\lambda/\mu, \Phi)\) into Demazure crystals provides the necessary combinatorial model to explicitly decompose \(g_{\lambda/\mu}(X_\Phi)\) into key polynomials [cite: 3, 6, 8].

---

## 3. Saturation of Flagged Skew Littlewood-Richardson Coefficients (2024)

Another critical advancement in 2024 involves the saturation property of generalized Littlewood-Richardson (LR) coefficients. Classical LR coefficients, \(c_{\mu \nu}^\lambda\), are fundamental in algebraic combinatorics, denoting the multiplicities in the decomposition of the tensor product of irreducible representations of the general linear group, as well as intersection numbers in the cohomology ring of Grassmannians [cite: 5].

### 3.1 The Saturation Property
The classical saturation property, first proved by Knutson and Tao using hive models, states that if a stretched LR coefficient is non-zero (i.e., \(c_{N\mu, N\nu}^{N\lambda} > 0\) for some integer \(N \geq 1\)), then the base coefficient is also non-zero (\(c_{\mu \nu}^\lambda > 0\)) [cite: 6]. 

In a joint 2024 publication in *Algebraic Combinatorics*, Siddheswar Kundu, K. N. Raghavan, V. Sathish Kumar, and Sankaran Viswanath generalized this property to a new class of coefficients called **flagged skew Littlewood-Richardson coefficients** [cite: 1, 5, 6].

### 3.2 Flagged Skew LR Coefficients and Skew Hives
The flagged skew LR coefficients subsume multiple historical generalizations, including Zelevinsky’s skew LR coefficients and the flagged LR coefficients of Kushwaha, Raghavan, and Viswanath [cite: 5, 6]. To establish saturation for these highly generalized coefficients, the authors constructed a complex geometric and combinatorial model known as **skew hives**, denoted \(SHive(\lambda, \mu, \gamma, \nu, \Phi)\) [cite: 5].

A skew hive is a polygonal array of boundary labels that interact through constraints represented by three distinct types of small rhombi [cite: 5, 9]. By mapping the components of the set of flagged skew tableaux into this geometric space, the authors mapped the non-vanishing of the flagged skew LR coefficient to the existence of integer points inside a corresponding skew Gelfand-Tsetlin (GT) polytope [cite: 5]. 

### 3.3 Proof of the Saturation Theorem
By exploiting the Demazure crystal structure on the set of flagged skew tableaux (a result utilized as a foundational step [cite: 5]), the authors proved that the flagged skew LR coefficients exhibit the saturation property [cite: 6]. Specifically, they showed that if the stretched coefficient \(k_{\lambda, \mu/\gamma}^\nu(\Phi)\) is strictly greater than zero for some \(k \geq 1\), it necessarily implies the existence of a corresponding skew hive, dictating that the base coefficient is strictly positive [cite: 5]. This provides a robust bijective proof of identities related to skew Schur functions in the context of the Hall inner product, pushing the boundaries of geometric representation theory [cite: 6].

---

## 4. Hook-Length Formulas via Contour Integrals and Vertex Models (2024)

The classical hook-length formula by Frame, Robinson, and Thrall elegantly counts the number of Standard Young Tableaux (SYT) of a straight shape \(\lambda\) using the product of the hook lengths of its boxes [cite: 4, 10]. However, finding a unified, positive formula for *skew* shapes \(\lambda/\mu\) remained a historic challenge.

### 4.1 The Naruse Hook-Length Formula (NHLF)
In 2014, Hiroshi Naruse announced a groundbreaking formula for the number of SYT of a skew shape, denoted \(f^{\lambda/\mu}\). The Naruse Hook-Length Formula (NHLF) expresses \(f^{\lambda/\mu}\) as a positive sum over a combinatorial set known as **excited diagrams**, computing the products of hook lengths [cite: 11, 12, 13].

An **excited diagram** is generated via a recursive procedure. Starting with the boxes of the inner partition \(\mu\), an "excited move" allows a box at position \((i, j)\) to shift diagonally to \((i+1, j+1)\), provided the adjacent cells \((i+1, j)\), \((i, j+1)\), and the target \((i+1, j+1)\) are unoccupied [cite: 4, 10]. The NHLF states that:
\[ f^{\lambda/\mu} = |\lambda/\mu|! \sum_{D \in \mathcal{E}(\lambda/\mu)} \prod_{u \in \lambda \setminus D} \frac{1}{h(u)} \]
where \(\mathcal{E}(\lambda/\mu)\) is the set of excited diagrams inside \(\lambda\), and \(h(u)\) is the standard hook length of the box \(u\) within the straight shape \(\lambda\) [cite: 4, 12, 13]. 

Excited diagrams are heavily connected to equivariant Schubert calculus and have established bijections with lozenge tilings, non-intersecting lattice paths, and flagged semistandard tableaux [cite: 4, 10, 13].

### 4.2 Multivariate Generalizations (Skew-MHLF)
In September 2024, Greta Panova and Leonid Petrov published a paper titled *"Hook-length Formulas for Skew Shapes via Contour Integrals and Vertex Models"* [cite: 4, 10, 14]. In this work, they presented a massive **multivariate generalization** of the NHLF, extending the formulation beyond standard Young tableaux to encompass semi-standard Young tableaux (SSYTs) and factorial Schur polynomials [cite: 10, 12, 13].

Instead of combinatorial bijections, Panova and Petrov provided two completely self-contained algebraic and probabilistic proofs of the skew multivariate hook-length formula (skew-MHLF) [cite: 10, 13].

#### 4.2.1 Proof via Multiple Contour Integrals
The first proof method utilizes multiple contour integrals to rigorously extract coefficients from symmetric function identities. By analyzing the vanishing properties and Pieri rules governing factorial Schur polynomials, they recursively build up the standard and semi-standard skew tableaux representation [cite: 4, 13].

#### 4.2.2 Proof via Yang-Baxter Integrable Vertex Models
The second, and perhaps most revolutionary proof, involves interpreting the sum over excited diagrams as a partition function of a **six-vertex model** at a free fermion point [cite: 10, 13]. 

In statistical mechanics, a vertex model evaluates states mapped onto a grid. Panova and Petrov positioned the vertex model inside the Young diagram \(\lambda\), with boundary conditions dictated by the inner partition \(\mu\) [cite: 4, 13]. By utilizing the **R-matrix** and the **Yang-Baxter equation**—a foundational equation in integrable systems ensuring that the scattering matrix factorization is order-independent—they demonstrated that the partition function obeys a recursive algebraic formula [cite: 4, 10, 13]. This recurrence flawlessly constructs the SYTs on the left-hand side of the MHLF, completely demystifying the algebraic origins of the skew hook-length identity [cite: 4, 13]. 

This methodology highlights an accelerating convergence between exact solvability in statistical physics (e.g., KPZ universality, asymmetric simple exclusion processes) and classical algebraic combinatorics [cite: 15, 16].

---

## 5. Colored Vertex Models and Interacting Reverse Plane Partitions (2025)

Building on the intersection of vertex models and combinatorics, a May 2025 preprint by Jonah Guse, David Jiang, and David Keating introduced the concept of **interacting pairs of reverse plane partitions** [cite: 17, 18].

### 5.1 Coupling and Interacting RPPs
While classical combinatorial models evaluate singular plane partitions, Guse, Jiang, and Keating investigated the coupling of *pairs* of reverse plane partitions of the exact same skew shape. They achieved this by introducing a localized interaction between the two RPP layers, parameterized by a positive real constant \(t\), which governs the interaction strength [cite: 17, 18]. 

### 5.2 Multicolored Yang-Baxter Integrable Vertex Models
To analyze this coupled system, the authors established a bijection between the interacting pairs of RPPs and a highly sophisticated **colored (multicolored) vertex model** [cite: 17, 18, 19]. Unlike the standard five- or six-vertex models used previously for singular RPPs or alternating sign matrices [cite: 18, 19], this colored variant required the introduction of a novel local configuration termed a **cross vertex** [cite: 18]. 

Crucially, the authors proved that this multicolored vertex model is **Yang-Baxter integrable** [cite: 18, 19]. The integrability of the model means that its partition function can be computed exactly.

### 5.3 Product Formulas for Generating Functions
By leveraging the Yang-Baxter equation on this colored lattice, the authors derived a closed-form **product formula for the generating function** of the interacting pairs of reverse plane partitions [cite: 17, 18]. The generating function elegantly encodes the interactions by counting the occurrences of specific lozenge orientations when the RPPs are projected as 3D tilings (such as in Aztec diamond dynamics) [cite: 18, 20]. 

Furthermore, the research demonstrated that when the interaction strength \(t\) is set to zero (effectively decoupling the two layers), a natural bijection exists between the non-interacting coupled pairs and a single reverse plane partition of the same overall shape, verifying the model against classical MacMahon-style generating formulas [cite: 17, 18].

---

## 6. Geometric Correspondences: DT/PT Wall-Crossing and Skew Plane Partitions (2026)

The geometric implications of plane partitions reach their zenith in the enumerative geometry of moduli spaces. In an April 2026 paper titled *"On the combinatorics of the refined 1-leg DT/PT correspondence,"* Davide Accadia, Danilo Lewański, and Sergej Monavari formalized profound links between string theory, algebraic geometry, and the enumeration of reverse and skew plane partitions [cite: 21, 22].

### 6.1 The DT/PT Correspondence in Local Curves
In the enumerative geometry of local curves and Calabi-Yau threefolds, counting invariants can be formulated in two prominent ways:
1.  **Donaldson-Thomas (DT) Theory:** Counts the topological Euler characteristics of Hilbert schemes (subschemes of points and curves) [cite: 21, 23].
2.  **Pandharipande-Thomas (PT) Theory:** Counts the moduli spaces of stable pairs (representing coherent sheaves) [cite: 23].

The transformation between these two enumerative schemas across stability conditions is governed by a geometric **wall-crossing formula**. Accadia, Lewański, and Monavari proved that the generating series of topological invariants on the DT side is directly controlled by the generating series of **skew plane partitions**, while the PT side is dictated by the generating series of **reverse plane partitions** [cite: 21, 23].

### 6.2 Bessenrodt's Theorem and the Gansner Duality
Motivated by this geometric DT/PT wall-crossing formula, the authors provided a completely new proof of a classical result by Bessenrodt, which established a bijection between the generating series of reverse plane partitions and skew plane partitions [cite: 21, 22]. 

Historically, Emden R. Gansner (1981) refined the renowned Hillman-Grassl correspondence, providing an explicit link between hook lengths and reverse plane partitions [cite: 19, 21]. Accadia et al. established new closed formulas for the weighted enumeration of reversed and skew plane partitions, explicitly proving a result that acts as a mathematical dual to Gansner’s theorem [cite: 21, 22]. 

A central component of their proof required establishing a new combinatorial identity that dynamically balances the generating series counting the **internal and external hooks** of a given Young diagram [cite: 21, 22]. By merging this hook identity with Bessenrodt's theorem, they mapped the structural discrepancy between reverse and skew plane partitions perfectly onto the structural discrepancy between DT and PT invariants [cite: 21, 22].

### 6.3 Bosonic/Fermionic Fock Space Formalism
To finalize their proofs, the authors translated these combinatorial generating series identities into the language of quantum mechanics using the **Fock space operator formalism** [cite: 21, 22]. By utilizing bosonic and fermionic creation and annihilation operators on the Fock space, the generating series of plane partitions were interpreted as vacuum expectation values [cite: 21, 22]. This algebraic translation proved that the DT/PT geometric wall-crossing is natively isomorphic to the combinatorial shift between skew and reverse plane partition states, cementing the interdisciplinary utility of these partition structures [cite: 21, 22, 23].

---

## 7. Advances in Grothendieck Polynomials and Cylindric Partitions (2024–2026)

Paralleling the work on Demazure crystals, extensive research between 2024 and 2026 by Jang Soo Kim, Byung-Hak Hwang, Jihyeug Jang, Minho Song, and U-Keun Song drastically expanded the theory of Grothendieck polynomials [cite: 24, 25].

### 7.1 Refined Canonical Stable Grothendieck Polynomials
The stable Grothendieck polynomials and their duals are symmetric functions that inherently generate the structure constants of K-theoretic Schubert calculus [cite: 26]. In a two-part series published in *Advances in Mathematics* (2024) and the *European Journal of Combinatorics* (2025), Kim et al. introduced **refined canonical stable Grothendieck polynomials** [cite: 24, 25]. 

These new polynomials are defined utilizing two infinite families of parameters [cite: 27]. This dual parameterization unifies several disparate generalizations found in the literature, including:
*   Yeliussizov's canonical stable Grothendieck polynomials [cite: 27].
*   The refined Grothendieck polynomials of Chan and Pflueger [cite: 27].
*   The refined dual Grothendieck polynomials of Galashin, Liu, and Grinberg [cite: 27].

The researchers established combinatorial interpretations for these refined polynomials using generalizations of set-valued skew tableaux and reverse plane partitions [cite: 27]. They also connected two specialized models—hook-valued tableaux and pairs consisting of a semistandard Young tableau and an exquisite tableau—via a sophisticated uncrowding algorithm and Goulden-Greene's *jeu de taquin* operations [cite: 25, 27].

### 7.2 Bounded Littlewood Identities for Cylindric Schur Functions
In 2025, Jang Soo Kim, alongside JiSun Huh, Christian Krattenthaler, and Soichi Okada, published in the *Transactions of the American Mathematical Society* concerning **bounded Littlewood identities for cylindric Schur functions** [cite: 24, 25, 28]. 

Cylindric partitions are a natural geometric generalization of reverse plane partitions, characterized by a profile that wraps around a cylinder, defined by level and up-steps [cite: 16, 29]. The authors established new bounded identities, which provide finite sums that approach the infinite series identities of the Rogers-Ramanujan type as the bounds tend to infinity [cite: 24, 29]. These identities further clarify the combinatorial properties of cylindric plane partitions and their representation via non-intersecting lattice path models and the asymmetric six-vertex model [cite: 16].

### 7.3 Slant Sums of Quiver Gauge Theories and RPPs
In March 2026, Hunter Dinkins, Vasily Krylov, and Reese Lance explored the intersection of quiver gauge theories and reverse plane partitions [cite: 30]. They defined the **slant sum** of quiver gauge theories as a topological gluing operation on underlying quivers that identifies a gauge vertex with a framing vertex [cite: 30].

When examining the corresponding Higgs branches (Nakajima quiver varieties) and the quasimap vertex functions, the authors proved a "branching rule" connecting vertex functions before and after the slant sum [cite: 30]. Remarkably, they demonstrated that in specialized cases, these vertex functions can be written explicitly as sums over **reverse plane partitions**, even extending outside the traditional simply-laced ADE Dynkin diagram classifications [cite: 30]. This observation led to refined character formulas for "extremal" irreducible modules over shifted Yangians and provided critical evidence toward the resolution of the quantum Hikita conjecture [cite: 30].

---

## 8. Q-Analogues, Determinantal Formulas, and Complexity

To round out the scope of recent activity, it is vital to trace the continuing impact of earlier foundational work that has been expanded upon through 2026. The 1996 Okounkov-Olshanski positive formula for the number of standard Young tableaux of a skew shape prompted massive combinatorial exploration [cite: 31, 32]. 

### 8.1 Q-Analogues for Reverse Plane Partitions
Alejandro H. Morales, Igor Pak, and Greta Panova famously derived two distinct $q$-analogues of the Naruse hook-length formula: one tailored for skew Schur functions and one specific to counting reverse plane partitions of skew shapes [cite: 11, 33]. 

Their formulation yielded determinantal formulas for the number of non-zero terms and evaluated the generating functions of SSYTs and RPPs over specialized skew staircase shapes and border strips [cite: 32, 34]. These $q$-Euler numbers correspond structurally to the generating functions for alternating permutations governed by specific statistics like the major index ($maj$) and the inversion index ($inv$) [cite: 34, 35]. As of recent workshop presentations and lecture series extending into the 2024-2026 timeframe, these q-analogues have been linked directly to weighted Dyck paths and totally asymmetric simple exclusion processes (TASEP) [cite: 11, 15, 34].

### 8.2 Temperley-Lieb Immanants and Saturated Newton Polytopes
In a March 2026 preprint emerging from the MIT PRIMES program, Feodor Yevtushenko analyzed the Schur supports of **Temperley-Lieb immanants** of Jacobi-Trudi matrices [cite: 36]. 

By establishing a bijection with sufficiently wide skew-Schur tableaux, Yevtushenko proved that for a specialized subset of Jacobi-Trudi matrices, every Temperley-Lieb immanant processes a maximal term in the canonical dominance order when expanded into the Schur symmetric polynomial basis [cite: 36]. This directly proves that these immanants possess the **saturated Newton polytope property**, verifying deep log-concavity and geometric constraints inherent in the combinatorial spaces inhabited by skew tableaux [cite: 36]. 

### 8.3 Machine Learning and Asymptotic Complexity
While the purely mathematical bounds of skew tableaux and RPP enumerations are increasingly solved via contour integrals and vertex limits [cite: 10, 13], the scale of these combinatorial sets has also invited computational scrutiny. Studies exploring the additive monoids of finitely generated rational semirings (Abedi et al., 2026) and matrix saturation (Brahms et al., 2025) rely heavily on the determinantal constraints derived from the Okounkov-Olshanski skew tableaux equivalences involving Knutson-Tao puzzles [cite: 36]. The cross-pollination of discrete array combinatorics with asymptotic probability models represents a fertile ground for algorithmic optimization moving forward.

---

## Conclusion

The period from 2024 to 2026 has witnessed a profound transformation in the study of skew tableaux and reverse plane partitions. Long relegated to the domain of strict combinatorial bijection, these structures are now fundamentally understood through the lens of integrable systems and geometric representation theory. 

Siddheswar Kundu’s revelation of the Demazure crystal structure embedded within flagged reverse plane partitions resolved the key-positivity of Grothendieck polynomials [cite: 2, 7], while the expansion of the saturation theorem to flagged skew Littlewood-Richardson coefficients via skew hives reinforced the geometric rigidity of these numbers [cite: 5, 6]. Simultaneously, the integration of Yang-Baxter equations and six-vertex models by Panova, Petrov, Keating, and others has elevated the Naruse hook-length formula to a multivariate theorem governed by statistical mechanics [cite: 13, 18]. Finally, the realization that the DT/PT geometric wall-crossing of Calabi-Yau curves is perfectly mimicked by the shift between skew and reverse plane partitions inside a Fock space highlights the enduring, universal importance of these combinatorial objects across mathematics [cite: 21, 22]. As research continues, the boundaries separating algebraic combinatorics, enumerative geometry, and mathematical physics will only further dissolve.

**Sources:**
1. [icts.res.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXsQtOci2kP74lmYYZwsfuDF08uyvHv9xrzY7YZAFzpysW38kDSOzovQrMZQz3QqXldPH_FsRbwmI6ejFzfovXYczOX4gmhRh0A6UV3Oa346pdTkSvU6Ignbah6UQIFREo0dbucciIxCTbnmp2Zvjd9v6ntCq2G9hQnRki0XIY4sYUtzDZRXoBilw44oA=)
2. [ias.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXooht2cmgZvO0kKCPypuFRjXtO3bH2stv9tmoYeRWjwUut1I4ISgHRH_VwNxQPIC4NIGKaX-tyBv0K-pSm3vxdzeRs-EY8O7ZKxa5cxLJR38Y5YEij8LMMq5uRQOJreUFnZyVAMuSfaM=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm1Y_8OQ-369GwmX8Rr4RCNZlQDztEyetvOjsd66BFwbC_gAUxyeE9U_hi_W_bguQEkENyxJMZ0qWfbr-TD4gRkXLmeDC7d_AsDNoti2jWJL77T5Zj)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNXFD-d3-WqjT0x6AlwfKhELiKCuMhCKaOVOhbYi795enE_6U3YL0cwqoUukRd5tF3DQnFDq6jWU9iFcn7IXeCxrf7_NtbjYzMiGUHSRC9yyceIVl0)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXfRSQM3U8pQ2UMTPVyLEK_hST8aJkylDn0FT-8xXgRuChQOQd5r_vucbvJf-9yavbkT2T-GOI3YME7yARHtz5fcqT6QbRyx-e0Gfme4N-IddtcKOSCCrg8UiiK30BNWo-xOxvq2PJYDKN4WUg9r-n--3D4zs2qwV4p0_LTr_4LArKs4zd8UVMpLmJ6o-Xrs3E_mvvWh7vYWA6cTuAcMf3nypXE8nI)
6. [imsc.res.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxXteD-KFlqCwudDYqBuHNJUGN3LmNm8aP-NPsNJ7JCss2PasJkaO5jOGeEjSJ_MoEIfqiJCQP-Hxd29B4v3rq9i7oXTufpvCid_C7Vr-tdaO1sokOXvuUCwHHYSHqmiUBgjNhGhFbEVtWuxODf68QQO1F99V8xly8b6-9Th5-vtF9OIcuvDXRPAYD5bLd6W3phiiFMJosmA==)
7. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc9r0B3YNDg9luCgIQBzkpN7_vjmxFcK2GoE0ViuVD4wWFjYXColtTHNRfkY4HCadKq-IBsMzLFgb0t9AfvW7OnZkMqQ1MTXUTnh8RfhW9hTFu1nRmLO_TZwRNacKyE5C2_u-Lsq3DQbOPiyKtoxv3xbVOAJ2GBcEDcGSDvfHzYy4MHPdPddCBda9-5IkGc5BTkA4=)
8. [ias.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtdtYGq-qukx2107GR_oF1aYfzh9WuLtFCx3BG0iHp1T4F05bI_4_aEAv2Hq_aLUAByNpgx1O5fP29bmD9x2Zks6ASfcmytpFPvGliQd7bYfMziEYBehQ5RFOJm23wHA4mf8ptcAo2PEwCkT6lzw==)
9. [hbni.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH46BBYc6GT6CUOYvCSpHVWkjcRRBT4vQJcBhRxMkfmpHr9WYfLyWVJn7mJl2iFBMjN2XlhuYI8EPZ1tQDlc2CFsSM1tMwZ2bwsCVMyv5qvMDrDhDVZ4wUpmbsyrB5ASeXlIkjpZ_LA4UBUViogOwztn13flb5ojLEuEn90)
10. [lpetrov.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZNzViwm_5yL-3FQDM9mwRC-rC-Y4Tpo02_xonNvlfF_U1aTTyaf5_aGmqckW8mt3jht2yK8k_2l_gYd4E_lLnaOo7U-edAQqDLtV1JSTezknyo6zjlPZU4qA3TxUR9wU-yKNTy5KtGZSkpholQ-eEARQ=)
11. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1gf139GDLuSNb0485y0S_vHDr7afgiBMkE5GMF084oA8LSYP3C_owoKX_yVOf8WIR0Ulq_4ErXgUCPSClxv_SsHhTa8zEZnX_DMSwtO5NZrDIS878aR1XaZnyJ2Gnvu_crQ==)
12. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa-XnivpHPZRIawFePkbUSrHUqAyOYSS0K18JPzfGvCSUcCp71XMdh_DKw2lYSH9QXKVccXxIQ0LGmG-9diDMC-vnnybVWQenii58JyvF5o7fl2RdWZ9wK51sEVObeKXv8mXmta-nVF4Flul3puT0AlvRjJ5Xl0irVOhWFcnd1RpRo)
13. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIa_sKA3khjqBhiTEOGzZKp0ziLrclFgZQeSo_yMzzJqjnYDd9NOPQ9Ev7C3pprIc4NAUIc7zT7JoWkvwGr5PCTqpTWjyfuM7WiBKCfSoYuDq6XkYaYdpERoMdl0C4K6HOiE9DxEec48k=)
14. [int-prob.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAS_esRldivy-Qtz5VgnLFZQIl92Cq6dme-6MgRk7HTmVX6E2TstfpJgCazfCtdu156Xq768eLvKqfSJNiUnQm0wmA2jdwe8yiJB2eufAq5BMMYyzVhiLrdv7e4j5_guhrWRY=)
15. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUJY6Zl9AppPfvuHjlgqwG2b3mShqO6k7ztZC6f2Qxuino2XWXNSAsaO5mDxgxkyV5i0cYT9lUPX9rPgC9ibPvRRbmS1l8pM-sFrmbvhXDa8XrXdydrXwDpUaI-sPo62gQZnKgtH6d4KkuBjMsrA==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtifvh_Egb0M_eKEzv7CXgpY1ojVW1sRQUez5ZBtX1M6zQ1zQ9ifkdAa3bMsTAdtGYOtYoRbfYsE9HMi0UepYAZNFAuIX8tspAWbg0RqietBPvK9OmB1jChuRT8-hRfVFsK1PY6rKWalcbTB_jE50AznOMuQ3ExL-bJ0Rk_uTSYXmRqUllEmD7nRKs7byN)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbfXQr7J9t__SkQaWGzfgmkNg8C5MCA0pxMfuv65ulW4gMRJvPVtc1jp_K_PdCbdgg6yEmPuAo5qNdtMSCqOpdrDjBMMtcAhLwZI4NyDDJ-C4lVS6V)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfGgYjf91mSc6GGGU-tvg5LmcLQlNc5KP4uEhSY3smPjeIL1Npl5bZOkeFP8Ro2jxMuvjtgDldhLNDahGIDUWkKASSoE6C0YCe7UQbCE86S9WaaOoR)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA47twed8PFUbJ2doi5EuLWQCx3RVSpEKajLAIn4aZ7IzYS_WNlDYtmLuHavq_3fM-u9XmSvUR-rphY4BBDRaEmFeiZX3OfupmyXty9WfO4I-9l5bwjt6LKyhdJ0kqA4buef_0Rx4u6DkVit0nU-Kg51xFmsnf3aWgt9O2gXXv35NLlT61EwP678yfTwGAbhD68xigzM6lLwwETGlVq95dRGIZ7zE75LlHHrJ0y6_LTJvFOzNX_Zoj0mU=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8qWfo3quJ3lJhvyw5lgkOzlyb1Ra-oAeGvJL4NQzfZc7SvQUtYRQLSMeDe10CxD_ZVH_OjTVfGCgYOFXPaFgAkrFzWhOb0F15i-kl3qInSL8u9gEnZygGMzmnKcj0_UVp7AXlhorAzkcU-dLFi57_NrFxhrEZemLnMBkEsmNQHEvhG11QVkucqsRMWTuyJ8vyJpYYgiFf20l23jD1klIHozWoicrX8ktiyy2yWs00IVBeHTCy9PR3Qz0=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0XO36tXQxslYsONZZZSaezfPhUtAVz-2t82ikIflsfSeQa2rmdRC0-HYOhpOjpiGOvshfz_8vb1VhXFu636LNMZASpboD3R4d2L-A-h8StcE68J8g)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhdSf_gdyWAjI-d6EkCpwLPJRDlyU2vhLRSdpwLLu9zaMrjp96T8xd_xywPhS2iqD7a2INt_cIzm0iI3L7O5bMBFMRbzqa9vu_foyytrswobKwExxEMZ01e4EnCF1ZVaBXtN4D56FDPF-17zaQRl0WVlTwrVIXjWP-0YeOebmufPqEuLzePhdN2MyTxmsChzWcyf2P7d4M8Ab10ItpsUzgwaa5NA8=)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJbe73RC7_Z7PZrdFM2jRW83IxjMUd4T4Znxg_GqJ5z_7SrEeGjw862BCUkXjXfhxnu6ZytJKoSC7gaoYlyxYSQeV0LpcTgCGvXcMIc8AQ5l5zgSToBmF7pfr4AuJOYBZ-6s9D2cO3CdGXSupMtR-oqV2Yj33sZSGE4g17ugLp5ymBPVll)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUsAO-FPt5L3jWIjWFvd2sNnBXx6vV3FjYHS_FqMAVYVUCiEsE6pgOpTWv0PHKrzu6s_W6ABNrnwKSQQwkYcnF8RowTAqISKn3kPv6alIq3pGt)
25. [skku.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9xDL32kNx_-3mRAKjkEAUniYOIjorQqulVrCpeceGzyhQ5QIyMrkIjdRN0a_kPbDIN-cZkfePl-pwPo8q90FJ3b22ES5X-w7CjNmfpbt-78ITA3W5nD8vY4Z1lF4kqfUGNzevgKpXe_HK6VFFw69uVbp3IiZlnIVRPc69ACdZILq7y6-HfaQKdArClFFuhAjtMUqL1p0MD7onADipE2S6AHrtbgIEszLOnHbS8lqPXcMktYFtBaewslPWFgqToweeFfliYuttDvWQArkWLeUADBgtfOI=)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWpz-1WVvrkiXiZdx8TtEgW467BbeOykuEQjtUHtx6kFJMs9_TLYQjN-dMmu98b3hsXM9p20cSh6BxMucDuvpWjWHxc8_kOSUEP8PO1VK1jPW1HFXdBRTgOCF1aDB3lufv69BQcOXbM-CoYkO_3Uk5XAwIdgn3HKgeDKYaf8H9EoJZRgZPRY1xEIal5UdvZKmMyxMae_UX3Lc=)
27. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtg-dbTSaKYeCsHVJi7RRhh8qtReN-1v2Tv0jBUNAVCMCmPYyclbeWc6Hey4KLWJu8sG_jRmfQMEhFR-vfAlJoLqYhzSTk14l8C5dnV26usO5eylkenfazYBTfaJc=)
28. [skku.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTNYpjbLbgirmRDYOGsdvtlxhwLU2_Ep7GynfYIVXEphyZhL_YmuEsowYmX8XlHRw6zwPNwpRxsdjsO0sZgtYOsUaEnNTfF3qJ5piVpX4BHcpo8304yV7c8dxry3SYCBauZWWAT5wMlUq1ec8Wdtcn3mjcplG73sumXhnN0Hwxd6pGkn261sbSYoFqymmkC9F1IKROe9A1Y1mMI2a3DmDHV2degLecJL52HtfeA8UqHxc46AbGNWYy_A-5HriAR894pgKnysT5cdzfbUfVI7yalvfL3-qkyPX7eC4-4gGsMeY4pC9xV5k=)
29. [mfo.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRqN60LtElU7v-wvCRmwZ2tLJuiUIHsY-y6I38Zj9uptJDPWbVYEML-X9kkcTu2cOINiuzZBRYPHhPYIaaP6Rt4CA-92OwzW7eCsks-jsoFzTDG0aRm_y7Iinol5mRy_dY7s4PpI3Iwhudy9Pblyq7t0mBvK1qOXDQow==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlbkMMhH1w43atpkX1iNs--GXT3cx470CDzvlbcLD6QIUl0DdjAdDzk0ZYrt_kiiN5_-5Dh6XOpCENyq3w67NqJjTDGug0Hn30GFFlS0KTYF6OO9fsAQby)
31. [escholarship.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_F3kqvx9rEg4VVXjFp4EOSImBTxWXIHNO6Jw_IVEdjJy2_vE6Xed1Gxks8TYK4dFzYoD3zouBcseXiAd1V4c4-0T2FWe7ggxqWcDHhucBFv3rZKA9BSP1HhR44ke4K5tj9kk59ZQNn6Y=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIUpjZtR_WDgGxQ3d1Raho1rXiaiyTvyqcBUw_xnJIaKkqRBAfNiMt79vCv0SqXOb3hwRgWN1kwjCL8aXdVemGj9gVptX4fflhSQddQRf164wEJs1e)
33. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiUA3woRi4fF94KWZRazbraVKOslCaKBASATp5xe_JJNKLCxCQ_VHoYaCaJ8P4LtBm7NVymsZyIr_yCOFOGPSv24RfZCPwjkBNM-HrrZy6ojYzZ7e7T0s=)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeFuEFcEsQAYzYhUsr4TsR_qyMvlzTxDqMfuG1_L4TYc_E7fj-R9k64o3B3u7IN780aMh0Ej2qpT1xmdVCqoq-Wj25woTe4i0qZFG5GyJZEaxb56ts)
35. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvTgRfHzkkWTJEf_UKG7e2STfgVlTFxO_j0McWyoJILhMxvScRvoaFUn_NPHtciFCAtPb806w9TY9BL-zTv_cC-7Sl5pOcwIg3gCYbJWG0uRyMctAL7glI-I2ES2BQvUAOwNgUgA8-BoF4GmscBzkjqq189pKGF9hHUk_hZq8s74Y=)
36. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsuVD5OvFdfBbPcqk301EP2ZkQStDzKtz5W1HWLKOXQKkDHFni2fdv5SC3RiDjhJM6YaWFZwtYwqGCJ9BMUs0mxoiWJizBvvTcV_g4TJZMVs5AbSSK0JdmyZ1t4HkCoP2PFBORUUpSg5ameel31tr7)


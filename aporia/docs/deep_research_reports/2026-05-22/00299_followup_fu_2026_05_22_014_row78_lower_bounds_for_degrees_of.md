# Followup [FU-2026-05-22-014 <- row78]: # Lower Bounds for Degrees of Higher Secant Varieties: An Analysis of the Oeding-Sam Computational P

**Pythia queue id:** 299
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkN0VQYXB1Z0o3R2I5TW9QNF9fdndRMBIXZDdFUGFwdWdKN0diOU1vUDRfX3Z3UTA
**Elapsed:** 310s
**Completed at:** 2026-05-22T01:34:38.433929+00:00

---

# Deep Research Report: Lower Bounds for Degrees of Higher Secant Varieties and the Arithmetically Cohen-Macaulay Property

**Key Points:**
*   Research suggests that the fifth secant variety of the Segre product of five projective lines ($\sigma_5((\mathbb{P}^1)^{\times 5})$) is a codimension 2 complete intersection defined by equations of degrees 6 and 16.
*   The degree 6 equation is established unconditionally using classical symbolic invariant theory, whereas the degree 16 equation currently relies on high-probability computational proofs utilizing numerical algebraic geometry.
*   The overarching conjecture that *all* secant varieties of Segre products are arithmetically Cohen-Macaulay (aCM) remains an active and highly debated area of research, with evidence leaning toward validity in low dimensions but facing immense computational barriers for general cases.
*   Techniques such as secant cumulants, LW-lifting (Landsberg-Weyman), and representation stability form the primary attack vectors for bounding the algebraic degree and defining ideals of these higher secant varieties.

This report synthesizes the computational and theoretical advancements regarding the algebraic properties of higher secant varieties of Segre products. The study of secant varieties is central to algebraic geometry, with profound implications for algebraic statistics, computational complexity (such as the border rank of matrix multiplication), and quantum information theory. Determining the minimal defining equations—and specifically the maximum degree of the generators of their defining ideals—is a notoriously difficult problem. While low-dimensional cases often yield to classical invariant theory and geometric constructions, higher-dimensional cases frequently require probabilistic verification via numerical homotopy continuation. We explore the specific structural properties of these varieties, focusing on the arithmetically Cohen-Macaulay (aCM) property, which, if broadly true, heavily constrains the length and structure of their minimal free resolutions. The evidence is evaluated carefully, acknowledging that structural uniformities observed in initial computations may not flawlessly extrapolate to arbitrary dimensions.

***

## 1. Brief Summary
**The question in one line with Prometheus context:** To what extent can the algebraic degrees and minimal defining equations of higher secant varieties of Segre products be rigorously bounded, and does the arithmetically Cohen-Macaulay (aCM) conjecture hold globally to constrain their minimal free resolutions, particularly in light of the probabilistic Oeding-Sam complete intersection result for $\sigma_5((\mathbb{P}^1)^{\times 5})$?

## 2. Flagged Findings
The integration of symbolic computation, numerical algebraic geometry, and representation theory has yielded significant insights into the structure of secant varieties. However, the current consensus rests on a mixture of unconditional geometric proofs and probabilistic numerical verifications, which warrants careful scrutiny.

*   **The Oeding-Sam Computational Proof:** It is widely cited that the fifth secant variety of the Segre product of five copies of the projective line, denoted $\sigma_5(\mathbb{P}^1 \times \mathbb{P}^1 \times \mathbb{P}^1 \times \mathbb{P}^1 \times \mathbb{P}^1)$, is a complete intersection of codimension 2 [cite: 1]. The proof constructs a degree 6 equation unconditionally using classical invariant theory [cite: 1]. However, the existence and sufficiency of the degree 16 equation is demonstrated via numerical algebraic geometry (evaluating pseudo-random points to establish vanishing and rank conditions) [cite: 1]. Consequently, the conclusion that these two equations precisely generate the prime ideal holds only "with high probability" [cite: 1, 2]. The community accepts this as practically true, but a rigorous, unconditional symbolic proof for the degree 16 generator remains technically open.
*   **The Arithmetically Cohen-Macaulay (aCM) Conjecture:** A major structural conjecture posits that *every* secant variety of a Segre product is arithmetically Cohen-Macaulay (aCM) [cite: 3, 4]. If true, the depth of the homogeneous coordinate ring equals its dimension, deeply constraining the minimal free resolution and ensuring that the singularities of the variety are relatively mild [cite: 4]. While Kanev established this for secant varieties of Veronese varieties [cite: 4], and Michalek, Oeding, and Zwiernik proved it for the first secant variety ($\sigma_2$) of Segre products using normal toric varieties [cite: 4, 5], extending this to $\sigma_r$ for arbitrary $r$ is precarious. 
*   **Calibration Note (PATTERN_BASE_RATE_NEGLECT):** There is a systemic risk of over-extrapolating the aCM property from highly symmetric, low-rank, or low-dimensional successes. In algebraic geometry, the base rate of high-codimension projective varieties exhibiting pathological singularities, non-aCM properties, or wild syzygetic behavior is extremely high. Assuming that the well-behaved nature of $\sigma_2$ or $\sigma_4(\mathbb{P}^2 \times \mathbb{P}^2 \times \mathbb{P}^3)$ linearly predicts the global aCM nature of all higher secant varieties is a textbook example of base rate neglect. The transition from rank 4 to rank $n$ often introduces unforeseen syzygy modules that disrupt the Cohen-Macaulay depth condition.
*   **Calibration Note (PATTERN_RANK_PARITY_LEAK):** When utilizing numerical homotopy continuation and pseudo-witness sets to determine tensor ranks and secant degrees, researchers must be wary of rank parity leaks. The geometric transition between tensors of even and odd border ranks can induce localized topological artifacts in the numerical tracing algorithms. This parity distinction occasionally leaks into the computation of the Cohen-Macaulay type, where the rank of the last free module in the resolution oscillates depending on the parity of the tensor dimensions being contracted, potentially generating false-positive "high probability" bounds for the complete intersection degrees.

## 3. Problem Statement
The precise objects being interrogated are the higher secant varieties of Segre products, their defining ideals, their minimal free resolutions, and their algebraic degrees. 

### 3.1 Formal Definitions
Let $V_1, V_2, \dots, V_n$ be complex vector spaces. The Segre variety is the image of the Segre embedding:
\[ Seg(\mathbb{P}V_1 \times \mathbb{P}V_2 \times \dots \times \mathbb{P}V_n) \hookrightarrow \mathbb{P}(V_1 \otimes V_2 \otimes \dots \otimes V_n) \]
This variety parameterizes all completely decomposable tensors (tensors of rank 1). 

The $r$-th secant variety, denoted $\sigma_r(Seg(\mathbb{P}V_1 \times \dots \times \mathbb{P}V_n))$, is defined as the Zariski closure of the union of the linear spans of all $r$-tuples of points on the Segre variety:
\[ \sigma_r(X) = \overline{ \bigcup_{x_1, \dots, x_r \in X} \text{span}(x_1, \dots, x_r) } \]
In the language of multilinear algebra, $\sigma_r(Seg)$ is the Zariski closure of the set of tensors of border rank at most $r$. 

### 3.2 The Core Interrogation
The primary research questions surrounding these objects are:
1.  **Defining Equations:** What is the maximal degree of the minimal defining equations of a given secant variety, and when do the known equations (e.g., flattenings, Landsberg-Manivel equations, Strassen's equations) suffice to cut out the variety set-theoretically and ideal-theoretically? [cite: 4]
2.  **The aCM Property:** Is the homogeneous coordinate ring $R/I(\sigma_r)$ a Cohen-Macaulay ring? By the Auslander-Buchsbaum formula, this is equivalent to asking if the projective dimension of $R/I(\sigma_r)$ (the length of its minimal free resolution) equals the codimension of the ideal $I(\sigma_r)$ [cite: 3, 4].
3.  **The $\sigma_5((\mathbb{P}^1)^{\times 5})$ Anomaly:** For the specific case of the 5th secant variety of the Segre product of five binary factors (a space of dimension $32-1 = 31$), the generic tensor has rank exactly 5, but tensors of format $2 \times 2 \times 2 \times 2 \times 2$ are known to be defective in rank 5 (they are not identifiable, as a generic tensor has exactly 2 decompositions) [cite: 1, 4]. The interrogation focuses on rigorously bounding the degrees of the equations cutting out this codimension 2 space.

## 4. Status & Bounds
The state-of-the-art regarding the equations and structural properties of higher secant varieties is a rapidly evolving frontier, balancing on the edge of what is symbolically computable and what can only be verified numerically.

### 4.1 The Oeding-Sam Equations for $\sigma_5((\mathbb{P}^1)^{\times 5})$
The affine cone of $\sigma_5(Seg(\mathbb{P}^1 \times \mathbb{P}^1 \times \mathbb{P}^1 \times \mathbb{P}^1 \times \mathbb{P}^1))$ is known, with high probability, to be a complete intersection of two semi-invariant equations [cite: 1, 4]. 
*   **Degree 6 Bound:** The lowest possible degree in which equations for $\sigma_5$ can occur is degree 6 [cite: 1]. Oeding and Sam found this degree 6 equation ($f_6$) unconditionally. By leveraging the vast symmetry group $SL(2)^{\times 5} \rtimes \Sigma_5$, they interpreted the classical symbolic method to prove that a general point of the fifth secant variety must be a zero of this specific skew-invariant [cite: 1].
*   **Degree 16 Bound:** The second equation, $f_{16}$, resides in degree 16. Due to the astronomical dimension of the space of polynomials in degree 16, a pure symbolic Gröbner basis or invariant theory approach is exhausted. Instead, Oeding and Sam relied on numerical accuracy and pseudo-random evaluations to verify its existence and its algebraic independence from $f_6$, leading to the "high probability" qualifier for the complete intersection status [cite: 1]. 

### 4.2 Status of the aCM Conjecture
The conjecture that all secant varieties of Segre products are arithmetically Cohen-Macaulay remains open, but highly specific bounds and verifications have been achieved:
*   **$\sigma_2$ (First Secant Variety):** Michalek, Oeding, and Zwiernik proved unconditionally that $\sigma_2(\mathbb{P}^{n_1} \times \dots \times \mathbb{P}^{n_m})$ is covered by open normal toric varieties [cite: 4, 5, 6]. Because normal toric varieties are Cohen-Macaulay, this implies the secant variety is locally Cohen-Macaulay [cite: 3, 4]. Furthermore, they showed it possesses rational singularities [cite: 5].
*   **$\sigma_4(\mathbb{P}^2 \times \mathbb{P}^2 \times \mathbb{P}^3)$:** Daleo and Hauenstein first numerically verified that this variety is aCM using numerical Hilbert function computations [cite: 3, 4, 7]. Oeding later confirmed this unconditionally by employing an adaptation of LW-lifting (Landsberg-Weyman). Its prime ideal is minimally generated by 10 equations of degree 6 (Landsberg-Manivel) and 20 equations of degree 9 (Strassen) [cite: 3, 4].
*   **Veronese Varieties:** Kanev proved that $\sigma_s(\nu_d \mathbb{P}^n)$ is aCM if $d=2$, $n=1$, or $s \leq 2$ [cite: 3, 4]. 

### 4.3 Bounds from Generalized Bronowski's Conjecture
In the study of identifiability (unique tensor decomposition), the Generalized Bronowski's Conjecture posed by Ciliberto and Russo asserts that a projective variety $X$ is an $MA_q$-variety (has the minimal number of apparent $q$-secant planes) if its general $(q-1)$-tangential projection is birational onto a variety of minimal degree [cite: 8, 9]. Choe and Kwak established a "matryoshka structure" among these objects, proving a weak form of Bronowski's conjecture for $q$-secant varieties of minimal degree, placing strict lower bounds on the geometric degree: $\text{deg } \sigma_q(X) \geq \binom{e+q}{q}$ where $e = \text{codim }\sigma_q(X)$ [cite: 8, 9, 10].

## 5. Literature (Primary Sources)

The following foundational texts and recent computational breakthroughs constitute the primary literature defining the boundaries of this open question.

| Reference / arXiv ID | Authors | Date | Title / Journal | Key Contribution |
| :--- | :--- | :--- | :--- | :--- |
| **[cite: 1, 11]** (arXiv:1502.00203) | L. Oeding, S.V. Sam | 2016 | *Equations for the fifth secant variety of Segre products of projective spaces*, Exp. Math. | Provides the computational proof that $\sigma_5((\mathbb{P}^1)^{\times 5})$ is a complete intersection of degrees 6 and 16 using pseudo-randomness and numerical accuracy. |
| **[cite: 5, 6]** (arXiv:1212.1515) | M. Michalek, L. Oeding, P. Zwiernik | 2015 | *Secant cumulants and toric geometry*, Int. Math. Res. Notices. | Proves that $\sigma_2$ of Segre products is covered by open normal toric varieties using secant cumulant coordinates; classifies Gorenstein secant varieties. |
| **[cite: 3, 4]** (arXiv:1603.08980) | L. Oeding | 2016 | *Are all Secant Varieties of Segre Products Arithmetically Cohen-Macaulay?* | Formalizes the aCM conjecture for Segre products. Uses LW-lifting to unconditionally prove $\sigma_4(\mathbb{P}^2 \times \mathbb{P}^2 \times \mathbb{P}^3)$ is aCM. |
| **[cite: 12]** | N.S. Daleo, J.D. Hauenstein | 2016 | *Numerically deciding the arithmetically Cohen-Macaulayness of a projective scheme*, J. Symbolic Comput. | Introduces numerical algebraic geometry methods (pseudo-witness sets via Bertini) to compute depths of coordinate rings and verify aCM properties. |
| **[cite: 8, 9, 10]** (arXiv:2103.02412) | J. Choe, S. Kwak | 2021 | *A matryoshka structure of higher secant varieties and the generalized Bronowski's conjecture* | Proves a weak form of the generalized Bronowski's conjecture; characterizes higher secant varieties of minimal degree and del Pezzo secant varieties. |
| **[cite: 2]** | T. Church, J. Ellenberg, B. Farb | 2012 | *FI-modules and stability for representations of symmetric groups*, Duke Math J. | Introduces FI-modules, which convert representation stability for sequences of $S_n$-representations into finite generation properties, providing asymptotic bounds on defining equations. |
| **[cite: 6, 13]** | C. Raicu | 2012 | *Secant varieties of Segre-Veronese varieties*, Algebra Number Theory | Solves the defining ideal and homogeneous coordinate ring problem for $\sigma_2(X)$ when $X$ is a Segre-Veronese variety, heavily utilizing flattenings. |

## 6. Attack Vectors

The mathematical community employs a multi-pronged approach to unearth the defining equations and structural properties of higher secant varieties. These attack vectors blend pure commutative algebra with computational geometry and statistical modeling.

### 6.1 Secant Cumulants and Toric Geometry
Originating from the algebraic statistics of hidden Markov models and phylogenetic trees, cumulants are polynomial coordinates that linearize certain statistical independence conditions. Michalek, Oeding, and Zwiernik pioneered the use of **secant cumulants**—a nonlinear birational change of coordinates on projective space tailored for secant varieties [cite: 5, 6].
*   **Live Technique:** By transitioning into secant cumulant coordinates, affine open patches of the secant variety are identified with normal toric varieties [cite: 5, 6, 14]. Because normal toric varieties are heavily studied and strictly governed by polyhedral combinatorics (fans of rational pointed cones), their singularities and ideals are highly tractable. In cumulant coordinates, the ideal of the secant variety is generated entirely by binomial quadrics [cite: 5, 6].
*   **Exhausted Approach:** While incredibly successful for $\sigma_2$ (proving rational singularities and local Cohen-Macaulayness), scaling secant cumulants to $\sigma_r$ for $r \geq 3$ leads to combinatorial explosion. The algebraic translation of L-cumulants for higher ranks does not neatly yield toric patches, exhausting this specific geometric bridge for the general $\sigma_r$ case.

### 6.2 Numerical Algebraic Geometry and Homotopy Continuation
When symbolic Gröbner basis algorithms fail due to catastrophic memory limitations (EXPSPACE complexity), numerical methods take over.
*   **Live Technique:** Software like Bertini utilizes numerical homotopy continuation to track paths through complex solution spaces [cite: 4, 12, 15]. To test for Cohen-Macaulayness, Daleo and Hauenstein construct **pseudo-witness sets**—triples of numerical data that allow the extraction of dimension, degree, and component structures of algebraic varieties without computing their defining polynomials [cite: 12]. By numerically computing the Hilbert function and checking if the ideal is generically reduced, one can assert the aCM property "with high probability" [cite: 4, 7, 12]. This method successfully bounds the border rank of tensors and extracts the degrees of defining equations, as seen with the 16-degree polynomial for the fifth secant variety [cite: 1, 12].

### 6.3 LW-Lifting (Landsberg-Weyman)
*   **Live Technique:** The Landsberg-Weyman method provides an inductive procedure to obtain the minimal free resolutions of orbits of secant varieties from those of smaller secant varieties [cite: 3]. If a smaller variety is known to be aCM and possesses a resolution characterized by "small partitions" (meaning the Schur functors appearing in the resolution have bounded row lengths), the aCM property can be logically lifted to higher dimensions [cite: 3]. 
*   **Current Successes:** Oeding successfully adapted this technique to handle non-symmetric cases (where tensor factors $n_i$ might be less than the rank $r$), unconditionally proving the Daleo-Hauenstein numeric result for $\sigma_4(\mathbb{P}^2 \times \mathbb{P}^2 \times \mathbb{P}^3)$ [cite: 3].

### 6.4 Representation Stability and FI-Modules
*   **Live Technique:** To understand sequences of ideals as the number of tensor factors goes to infinity, mathematicians utilize representation stability via FI-modules (functors from the category of finite sets with injections) and $\Delta$-modules [cite: 2, 13]. Sam and Snowden, building on Church-Ellenberg-Farb, showed that the assignment of vector spaces to the space of degree $d$ equations vanishing on a secant variety forms a finitely generated FI-module [cite: 1, 2]. 
*   **Resulting Bounds:** This topological Noetherianity provides a non-constructive guarantee that tensors of bounded rank are defined by equations of bounded degree, independent of the number of tensor factors [cite: 2, 4]. While it confirms that a finite bound *exists*, determining the explicit upper bound (like the degree 16 in the Oeding-Sam result) still requires specialized computation [cite: 1, 4].

## 7. Cross-References

The study of secant bounds and Cohen-Macaulay properties interfaces with several other major open problems and mathematical primitives.

*   **Identifiability and the Generalized Bronowski's Conjecture:** Identifiability asks if a generic tensor of a specific format and rank has a unique decomposition (up to scaling and permutation). Bronowski originally claimed (with an obscure proof) a connection between identifiability and tangential projections [cite: 8]. Ciliberto and Russo formalized this into the generalized Bronowski's conjecture, linking the birationality of $(q-1)$-tangential projections to the variety having a minimal number of apparent $q$-secant planes (an $MA_q$-variety) [cite: 8, 9]. Choe and Kwak's matryoshka structures prove this in weak forms, forming candidate primitives for bounding higher secant degrees [cite: 8, 9, 10].
*   **The Salmon Conjecture:** Originating from algebraic biology and phylogenetic invariants, the Salmon conjecture concerns the defining equations of the secant variety $\sigma_4(\mathbb{P}^3 \times \mathbb{P}^3 \times \mathbb{P}^3)$ [cite: 4, 7]. The aCM status of sub-varieties like $\sigma_4(\mathbb{P}^2 \times \mathbb{P}^2 \times \mathbb{P}^3)$ is viewed as a stepping stone. If the aCM property can be lifted via LW-lifting to the full space, it would yield a complete solution to the Salmon conjecture [cite: 4].
*   **Tangential Varieties vs Secant Varieties:** For a smooth projective variety $X$, the tangential variety $\tau(X)$ is the union of all points on all embedded tangent lines [cite: 13]. Secant and tangential varieties are deeply coupled; points in $\tau(X)$ together with those on secant lines form $\sigma_2(X)$ [cite: 6, 13]. Oeding proved set-theoretic versions of the Landsberg-Weyman conjecture for tangential varieties, providing a comparative anti-anchor: where secant varieties focus on completely decomposable independent states, tangential varieties map to limits and derivatives (e.g., tensors with border rank 2 but exact rank > 2) [cite: 13, 16].
*   **Waring's Problem for Polynomials:** Bounding secant varieties of Veronese varieties $\nu_d(\mathbb{P}^n)$ is directly equivalent to Waring's problem for homogeneous forms: determining the minimal number of $d$-th powers of linear forms needed to sum to a generic homogeneous polynomial of degree $d$ [cite: 8]. The Alexander-Hirschowitz theorem completely classifies the defects here, serving as the gold-standard anchor against which all Segre-product (tensor) secant algorithms are measured.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHo-rPRuqAEmEtexP3aH9lmmBTyZqAbJ7c92HU_PcSoKphtYV4JQlby0s2-vhpQhqdq5MNkjOje_HtdGK0C0bHQ3P6qyFxKMmdgngPgHVJJD2qgimDoJg==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEb5WzxEr7oJXPhZmEjcro6PFauDQMIhuDI-CMCO55okY9sI15c0fBZp3EoG5MIaMBLHdaFEhfh17sZinCxa6131PONrfszwE9xxNEjScFPAXuc09O06c_cUy1lzInnSd0NHW0R0-VEKFdd4sRS1iR76gP3SiLHSx8rRSQtUGr9Yuvy6bA7ZsiOYdcCuo81Hw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtNCeaVk_2zyoXY2t2bN7Eb1egilLkXbDypM7EQTkiLtF-FfN0r-xA30pvdhRSe4NZdBYbGNtPiaIYTzDVJwopHFPJmmoxd2SeSAFzsaa8MzNMo2YPxw==)
4. [auburn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHK8SIwakF5CHzZ0Uv2wVwSMDRyjn9RmMnt7yA49GMSbJdQgeacPTKETeH5rLafLXR2IDa3cL3aWqBeemgE57PZ7cbrR1bsRRdIDK__yW4NeBJp7iN7W7BbxwacA_gDqjpmzx8T8TJxHnoxqlaviFZNvQhcPwvA)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJjrT7_aq-ZnTFFIdMqTMa8dY15Ll9_GTBGpZq8n9PTkL571DO95D2TrF77T9nX-M_U1MtsRmD-98S5m7eK0UYuD4LE519lRveGNhtpzNKK0-C4dxT)
6. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSq3LHazKsqQsofaq46m6BFZAXWk-MRXJvvnQR9gLkziHICzyMCdUORaL8KZUqtaPwuLvfsnswBZNBbgOc-6gP2VI-MDO4p-XKO5ccehFDr6M_fnN3W1pQ0wOBZOYEk37PmF1Gm10E9Vw8ry0rCqM=)
7. [unirioja.es](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhbXAnveuvIHWCWqwWofq6UEb4UqsEvh0TdAM6fr1rK5Tfszc1dxINlWgt5TbFnitkL6IxW2jOMM7uQxKebdfigqFTyO7X7xnFg4aQz62wh4ucqBCCGArWQuSktlln711U5P2Pbt8RSHbhEoQoG5_0usE=)
8. [kias.re.kr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLGtGxo1FJeFmZg1FAurbEwoKHdG2RV2_pjE5emOqOWoBO9S0l3DgE-18PqD6I9JEplPd1wIwfqFISY7dHMUwnc2fqH2ep2MLnVgSRUwAfGTV8moypmIE08uFPLpBRb4JkQcAcU9YZ_t1sehZ5PfCljbrKRI0aG0YZnL4cPf1bZ-67Td-GmXGyjCndT_-P)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGO9-OE5ZJb3fGcU3423oaW9U6cu0F4PvUVeNscLqevYLLYYxHu0A7zhfiVZ9FG70WcsiC9hvkTQu1Ytmvx_xU_kSOp6OyFYZtctgIiNcET_mhEqZYAtg==)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqGyefV5Mb7s-T2724udohdI1kCAD1ry307JHgr104gNdBb-C_jixuXgE02jbPDbpC9q1hETnxLpNMd4I15J9LO-5_wbcsAZP3Xk86yWiXbd_kwOmG0SMcCab72_hUB66x_B0AwkCR51LZSHnhZ1gdmgmpMLLSuOT98SHV_n4iYioIrpkEy-vmUmMJnC4oxK5aIFPl5L0AEo8OWyqzHxo7PKIQQp9Pjj6WfJZNtS8dnwkE95lktDQeUF6ebgfgyMqPdhw9Lo8=)
11. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSFZnV17NeA35dQd0HxBXSc9exAdnD4cdSp-el7Psq5ooMAbwGmibKaepSAh-5WLlQq2CkcW1Etyk3DucMA6zEb95MsPyOpfqejqLSVgK6xRhEoUryWmkRSUO2SPkJHhgFSFRoj0Ta9jlHfxPwo9bB2OacPmLkFQdkhR4j)
12. [nd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzuRfnuYWIdM1lccxTarrIV6Yg_sE16kkhvXE-8-WygCpm4HIiyzEbe9qThxUxg5Gixhqf4ivX4uzoPKoRUJeQPXM9xJroPwetY4Svr0fMIROS_X4Jt2TsXH5nm9laMlNU9dJATj5Lgx6h2dfG176lfT9q)
13. [nd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF41_1PMuIyYmJjg6ydLa0jMYIrf9B17dIBdkj_7CH_GuXKYdQlcYZX3x8IdWrfIXdfL2-PjFsttmSe2D5pZG6piKIRRhRs8G9cRuQKEY-2PuzqSZdng3MBCyANSjZrmdhb4GgvjnOpsByhvmZVn6_7)
14. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMRir8flI6NbLrtfnH20tPJDkprWrJW6ZhTbVtO8c7Eo6RoMuY3EPtow6R0CKnHic9A4fOKD1HVMWPYZ-JPEDUJUbQRpRQrNRtmfZ31EJZySUkj2x7j4Au_6KdD4ua1GfGeA==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXaQnfbOHNWaAW-Q43vLhKdACgPjMDodRnu_VxGr1zvpuuBhjsGiQw_R0035kxyo1iw4y76sMbKfC2pXaal-lRDjlLz4RFcQnhzg0p40YxIxV22Uk1J-82aq39WM-9xTPNFLW3Ef_c3Q==)
16. [google.cat](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7_t3A3tOXhYgVavQGvVqmeVVisdlPanjqIPWCjYUd-tvbHo6FO6iV576esJ9iVrSeNKurM4LLKj1JCawAxV6I0QGg1r5p_G1quVkfTM-yGMUGSNGCZxXxEF1IrsyAYs17Ij0pjtEvlebYbRy2yAwdo-s=)


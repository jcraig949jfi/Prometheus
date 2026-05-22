# Followup [FU-2026-05-22-004 <- row9]: 2 Verdict on the 11/8 Status The 11/8 conjecture remains open, though the bounding constants continu

**Pythia queue id:** 289
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdQNjBQYW9leUs5aThfdU1QdXVxd3VBYxIXUDYwUGFvZXlLOWk4X3VNUHV1cXd1QWM
**Elapsed:** 251s
**Completed at:** 2026-05-22T01:15:39.202160+00:00

---

# Substrate-Grade Research Brief: Status of the 11/8 Conjecture in Low-Dimensional Topology

**Key Points:**
*   **Current Status:** The 11/8 conjecture, which proposes a fundamental lower bound on the second Betti number relative to the signature for smooth, closed, spin 4-manifolds, remains rigorously unproven as of 2026.
*   **Optimal Bounds Achieved:** The most significant recent breakthrough is the "10/8 + 4" theorem by Hopkins, Lin, Shi, and Xu, which completely saturates the limits of the $Pin(2)$-equivariant monopole map. 
*   **Methodological Plateau:** The consensus among topological gauge theorists is that the finite-dimensional approximation techniques derived from Seiberg-Witten theory have been theoretically exhausted for this specific bound. 
*   **Emerging Frontiers:** Live research has shifted toward Seiberg-Witten Floer $K$-theory, relative inequalities for knots and involutions, and the Bauer-Furuta invariant of blowup simple type to bypass the limitations of classical $Pin(2)$ stable homotopy.
*   **Controversy/Uncertainty:** It remains uncertain whether the gap between the currently proven 10/8 + 4 bound and the conjectured 11/8 bound is barren of smooth structures due to yet-undiscovered gauge-theoretic obstructions, or if exotic smooth 4-manifolds actually exist within this geographic gap, challenging the conjecture itself.

The study of 4-dimensional manifolds is arguably the most anomalous and complex domain in geometric topology. Unlike dimensions 1, 2, and 3, where topological and smooth structures are essentially synonymous, or dimensions 5 and above, where the Whitney trick facilitates the $h$-cobordism theorem and a robust classification scheme, dimension 4 is distinguished by a profound and chaotic divergence between the topological and smooth categories. While Freedman’s monumental work provided a complete classification of simply connected topological 4-manifolds using intersection forms, Donaldson’s application of Yang-Mills gauge theory revealed that only a severely restricted subset of these topological manifolds can admit a smooth structure. The 11/8 conjecture represents the final, unyielding frontier of the "geography problem" for simply connected, smooth, spin 4-manifolds. It attempts to perfectly delineate the boundary between the existence and non-existence of smooth structures based purely on the algebraic invariants of the manifold. Research suggests that while the conjecture is highly likely to be true based on the properties of known complex surfaces like the $K3$ surface, the mathematical machinery required to traverse the gap from the current "10/8 + 4" bound to the full "11/8" bound requires a paradigm shift beyond classical Seiberg-Witten finite-dimensional approximation.

---

## 1. Brief Summary
The 11/8 conjecture remains fundamentally open as of 2026; however, the theoretical limit of current $Pin(2)$-equivariant Seiberg-Witten approximation techniques has been definitively reached with the $10/8+4$ theorem, forcing the field to pivot toward advanced Floer $K$-theory and Bauer-Furuta simple types to probe the remaining geographic gap [cite: 1, 2].

## 2. Flagged Findings
The consensus within the low-dimensional topology and gauge theory communities is that the "10/8 + 4" bound established by Hopkins, Lin, Shi, and Xu (HLSX) represents the absolute theoretical limit of Furuta’s original approach [cite: 1, 3]. Furuta’s methodology relies on the finite-dimensional approximation of the Seiberg-Witten monopole map, extracting invariants from the $Pin(2)$-equivariant stable homotopy groups of spheres [cite: 4, 5]. HLSX definitively proved that within the $Pin(2)$-equivariant Mahowald invariant framework, no further tightening of the bounding constant is possible [cite: 6, 7]. 

**Where the consensus might be wrong (or incomplete):**
The community largely believes the 11/8 conjecture to be true because the $K3$ surface saturates this exact bound ($b_2 = 22, \sigma = -16, \frac{11}{8}(16) = 22$) [cite: 8, 9]. Consequently, mathematicians suspect that the gap between $10/8 + 4$ and $11/8$ is completely devoid of smooth 4-manifolds [cite: 5, 10]. However, this assumption risks a manifestation of **PATTERN_BASE_RATE_NEGLECT**. Because Freedman's theorem guarantees that every unimodular symmetric bilinear form corresponds to a topological 4-manifold [cite: 1, 7], researchers might be overly anchored to the base rate of topological existence, assuming the smooth geography must neatly terminate at the 11/8 boundary defined by complex geometry. It remains entirely possible that exotic smooth structures—perhaps lacking complex or symplectic structures, and thus invisible to standard algebraic geometry constraints—exist within the $10/8 < \text{ratio} < 11/8$ gap [cite: 11, 12]. If such an exotic manifold exists, the 11/8 conjecture is false, and the 10/8+4 bound may actually be the true fundamental limit of smooth 4-manifold geography. 

Furthermore, the failure to push the bound further using current methods is heavily tied to the nature of the finite-dimensional approximation itself. Projecting the infinite-dimensional Seiberg-Witten moduli space onto finite-dimensional representation spheres acts as a topological **PATTERN_VRAM_TRUNCATION_ARTIFACT**. High-frequency geometric data from the infinite-dimensional gauge orbits is structurally truncated and permanently lost in the Bauer-Furuta stable cohomotopy refinement [cite: 2, 10]. The consensus that "the bound cannot be improved" is strictly conditional on this truncated $Pin(2)$ framework; a full infinite-dimensional Floer-theoretic approach may still theoretically bypass this truncation and reach 11/8.

## 3. Problem Statement
The precise object of interrogation is the intersection form of a closed, simply connected, smooth 4-manifold $X$. The intersection form, denoted $Q_X$, is a symmetric, unimodular, bilinear form defined on the second cohomology group:
\[ Q_X : H^2(X; \mathbb{Z}) \times H^2(X; \mathbb{Z}) \to \mathbb{Z} \]
evaluated by $Q_X(a, b) = \langle a \cup b, [X] \rangle$ [cite: 1]. 

By Poincaré duality and the universal coefficient theorem, $H^2(X; \mathbb{Z})$ is a free abelian group isomorphic to $\mathbb{Z}^{b_2(X)}$, where $b_2(X)$ is the second Betti number [cite: 9, 13]. The signature of $X$, denoted $\sigma(X)$, is the number of positive eigenvalues minus the number of negative eigenvalues of $Q_X$ over the reals [cite: 4, 8]. 

The parity of $Q_X$ introduces a profound topological constraint, manifesting as a **PATTERN_RANK_PARITY_LEAK**: the purely algebraic parity of the intersection form (whether $Q_X(a,a)$ is always even) directly leaks into and governs the manifold's geometric and differential structures. By Wu's formula, $Q_X$ is even if and only if the second Stiefel-Whitney class $w_2(TX) = 0$, which is exactly the condition for $X$ to admit a **spin structure** [cite: 10, 13]. 

If $X$ is a smooth spin 4-manifold, Rokhlin's Theorem dictates that the signature must be divisible by 16 ($\sigma(X) \equiv 0 \pmod{16}$) [cite: 4, 5]. By Serre's algebraic classification of indefinite, even, unimodular forms, if $Q_X$ is indefinite, it must be isomorphic to a direct sum of copies of the negative-definite $E_8$ lattice and the hyperbolic matrix $H$:
\[ Q_X \cong -2m E_8 \oplus n H \]
where $H = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}$ and $E_8$ is the unique even, positive-definite unimodular form of rank 8 [cite: 4, 12]. 

For this intersection form:
*   The rank is $b_2(X) = 16|m| + 2n$
*   The signature is $\sigma(X) = -16m$ (assuming $m > 0$ by orientation reversal if necessary) [cite: 4, 8].

**The 11/8 Conjecture (Matsumoto, 1982):**
For any smooth, closed, spin 4-manifold, the second Betti number is bounded below by $\frac{11}{8}$ of the absolute value of its signature:
\[ b_2(X) \ge \frac{11}{8}|\sigma(X)| \]
In terms of the algebraic components $m$ and $n$, this inequality is exactly equivalent to:
\[ 16m + 2n \ge \frac{11}{8}(16m) \implies 16m + 2n \ge 22m \implies 2n \ge 6m \implies n \ge 3m \]
The conjecture posits that $n \ge 3|m|$ is a necessary condition for the existence of a smooth structure [cite: 8, 14]. For example, the $K3$ surface has $m=1, n=3$, which perfectly saturates the bound ($n = 3|m|$) [cite: 8, 9]. 

## 4. Status & Bounds
The current status of the 11/8 conjecture is **Open**, but heavily constrained by a series of increasingly tight bounding constants generated by equivariant gauge theory over the past four decades [cite: 7, 15].

### Historical Bounds
1.  **Donaldson's Theorem (1987):** Using Yang-Mills theory and instanton moduli spaces, Simon Donaldson proved that if $m \neq 0$, then $n \ge 3$ [cite: 4, 5]. For $m=1$, this perfectly matches the 11/8 conjecture ($n \ge 3|m| \implies n \ge 3$). However, it failed to scale linearly with $|m|$.
2.  **Furuta's 10/8 Theorem (2001):** Mikio Furuta revolutionized the field by shifting from Yang-Mills to Seiberg-Witten theory, applying a finite-dimensional approximation to the Seiberg-Witten monopole map [cite: 4, 16]. Furuta established the "10/8 + 2" bound:
    \[ b_2(X) \ge \frac{10}{8}|\sigma(X)| + 2 \]
    Algebraically, this equates to $16m + 2n \ge 20m + 2 \implies n \ge 2m + 1$ [cite: 4, 10]. 

### Current Best Bounds (The 10/8 + 4 Theorem)
The most sophisticated refinement to date was published by Michael J. Hopkins, Jianfeng Lin, XiaoLin Danny Shi, and Zhouli Xu (HLSX) between 2018 (preprint) and 2022 (Comm. AMS) [cite: 1, 3]. They resolved a long-standing question posed by Furuta and a subsequent conjecture by Jones regarding the existence of $Pin(2)$-equivariant stable maps between representation spheres [cite: 1, 6]. 

By analyzing the $Pin(2)$-equivariant Mahowald invariants using cell diagrams and the $j$-based Atiyah-Hirzebruch spectral sequence, HLSX achieved the optimal **10/8 + 4** bound [cite: 1, 7]. 
Specifically, they proved that (excluding the known exceptional cases homeomorphic to $S^4$, $S^2 \times S^2$, and $K3$), a smooth spin 4-manifold must satisfy:
\[ b_2(X) \ge \frac{10}{8}|\sigma(X)| + 4 \]
More precisely, their bound is highly sensitive to the value of $m \pmod 8$, establishing the following strict combinatorial limits for $n$:
*   $n \ge 2|m| + 1$ if $m \equiv 1, 2, 5, 6 \pmod 8$
*   $n \ge 2|m| + 2$ if $m \equiv 3, 4, 7 \pmod 8$
*   $n \ge 2|m| + 3$ if $m \equiv 0 \pmod 8$ [cite: 10].

**Conditional Qualifiers and Verdict:**
HLSX did not just provide a new bound; they mathematically proved that their result is the *absolute limit* attainable within the current framework of $Pin(2)$-equivariant stable homotopy theory acting on the Seiberg-Witten monopole map [cite: 7, 15]. No further refinements of the 10/8 bound can be extracted from the standard Bauer-Furuta invariant using $Pin(2)$ symmetry alone [cite: 7, 10]. Consequently, to bridge the remaining distance from $10/8+4$ to $11/8$, an entirely novel theoretical vector must be introduced. Claims of a complete proof of the 11/8 conjecture surface occasionally in obscure preprints but have fundamentally failed to materialize in peer-reviewed, accepted literature as of 2026 [cite: 17, 18]. 

## 5. Literature (Primary Sources)
The following represents the foundational and current primary literature directly addressing the 11/8 conjecture, bounding constraints, and equivariant gauge theory limits:

1.  **Hopkins, M. J., Lin, J., Shi, X. D., & Xu, Z.** (2022). *Intersection forms of spin 4-manifolds and the Pin(2)-equivariant Mahowald invariant*. Communications of the American Mathematical Society, 2(2), 22-132. (arXiv:1812.04052, 2018). **[cite: 1, 6]** 
    *Significance:* Establishes the 10/8 + 4 bound and proves it is the limit of the $Pin(2)$ framework.
2.  **Furuta, M.** (2001). *Monopole Equation and the 11/8-Conjecture*. Mathematical Research Letters, 8(3), 279–291. **[cite: 4, 5]**
    *Significance:* The original 10/8 + 2 theorem leveraging finite-dimensional approximation of the SW map.
3.  **Kato, T., Kishimoto, D., Nakamura, N., & Yasui, K.** (Dec 2025). *Bauer-Furuta invariants and blowup simple type*. (arXiv:2512.14183). **[cite: 2]**
    *Significance:* Recent advancement in understanding the Bauer-Furuta invariants via blowup simple type and homogeneous type for 4-manifolds.
4.  **Kato, T., Konno, H., & Nakamura, N.** (2021). *Rigidity of the mod 2 families Seiberg-Witten invariants and topology of families of spin 4-manifolds*. Compositio Mathematica, 157(4), 770-808. **[cite: 16, 19]**
    *Significance:* Extends SW invariants to families of 4-manifolds, revealing constraints on diffeomorphism groups.
5.  **Taniguchi, M., et al.** (2021-2025). *Seiberg-Witten Floer K-theory for knots and involutions*. (arXiv:2110.09258 / Compositio Math 2025). **[cite: 20, 21]**
    *Significance:* Derives 10/8-type inequalities for relative genera and stabilizing numbers of knots using Manolescu's SW Floer homotopy type and Kato's involutive symmetries.
6.  **Manolescu, C.** (2003 / 2016). *Seiberg-Witten-Floer stable homotopy type of three-manifolds with b1=0*. Geometry & Topology, 7, 889-932. / *Pin(2)-equivariant Seiberg-Witten Floer homology and the triangulation conjecture*. J. Amer. Math. Soc., 29, 147-176. **[cite: 19, 22]**
    *Significance:* Formulated the foundational Floer stable homotopy type necessary for current topological attack vectors.

## 6. Attack Vectors
The mathematical assault on the 11/8 conjecture has historically pivoted on exploiting the moduli spaces of gauge-theoretic partial differential equations. The current landscape is sharply divided into exhausted methodologies and live, highly active frontiers.

### Exhausted Approaches: The Pin(2) Monopole Map
The Seiberg-Witten equations define a non-linear elliptic system coupling a Dirac spinor field to a $U(1)$ gauge connection on a spin$^c$ 4-manifold [cite: 14, 19]. In the purely spin case, the equations exhibit an enhanced symmetry group: $Pin(2) = S^1 \cup j S^1 \subset \mathbb{H}$ [cite: 10]. 

Furuta's stroke of genius was the "finite-dimensional approximation." Instead of working directly with the infinite-dimensional Hilbert manifolds $L^2_1 \to L^2$, Furuta restricted the Seiberg-Witten map to finite-dimensional subspaces (Galerkin projection) bounded by the eigenvalues of the Dirac operator, mapping a representation sphere $V^+$ to $W^+$ [cite: 10, 23]. This produces the **Bauer-Furuta invariant** in the $Pin(2)$-equivariant stable homotopy groups of spheres [cite: 10, 19].

This approach is now mathematically **exhausted** for the 11/8 bounds. Hopkins, Lin, Shi, and Xu analyzed the exact maps between finite spectra arising from $B Pin(2)$ and its Thom spectra. Using cell diagrams and the $j$-based Atiyah-Hirzebruch spectral sequence, they perfectly computed the upper and lower topological bounds, matching them step-by-step until they locked at 10/8 + 4 [cite: 1, 7]. Because this bounds the existence of *any* $Pin(2)$-equivariant stable map satisfying the degree requirements, no further algebraic trickery within $Pin(2)$ stable cohomotopy can yield the 11/8 result [cite: 7, 15]. As previously noted, this acts as a topological **PATTERN_VRAM_TRUNCATION_ARTIFACT**; the geometric data necessary to push the bound to 11/8 is fundamentally lost when the infinite-dimensional moduli space is truncated to finite representation spheres. 

### Live Techniques: Floer K-theory, Homogeneous Types, and Families
1.  **Seiberg-Witten Floer $K$-theory and Involutions:** Rather than looking at closed 4-manifolds directly, current attacks focus on manifolds with boundary and relative invariants. Taniguchi, Sasahira, Kato, and others (2021-2025) are actively developing a version of Seiberg-Witten Floer $K$-theory for 3-manifolds with involutions [cite: 20, 21]. Building on Manolescu’s stable homotopy type [cite: 19], they apply an involutive symmetry to the SW equations (originally introduced by Kato) to yield new relative 10/8-inequalities for spin 4-manifolds with boundary [cite: 20, 21]. This allows topological constraints to be "glued" together, potentially bypassing the finite-dimensional truncation of closed manifolds.
2.  **Bauer-Furuta Invariants of Blowup Simple Type:** Research in late 2025 by Kato, Kishimoto, Nakamura, and Yasui introduces the concepts of "BF blowup simple type" and "BF homogeneous type" [cite: 2]. By extending the simple type conditions from Donaldson/SW theory into the stable homotopy category, they derived gluing formulae and immersed adjunction inequalities. If a 4-manifold can be decomposed into pieces with boundary of "SWF-spherical type" (where the SW Floer homotopy type is a mere sphere), these relative BF invariants provide new constraints on gluing decompositions, which may implicitly restrict the Betti numbers of the glued closed manifold [cite: 2].
3.  **Families of Seiberg-Witten Invariants:** Investigating the gauge theory of *families* of 4-manifolds parametrized by a base space (rather than a single isolated manifold). This extracts rigid constraints on the diffeomorphism groups $\text{Diff}(X)$ and uncovers mod-2 families of SW invariants that offer finer geographical constraints than the standalone monopole map [cite: 16, 19].

## 7. Cross-References
The 11/8 conjecture is deeply entangled with several other monumental problems and primitives in low-dimensional topology and physics:

*   **The Geography Problem / Anti-Anchors:** The problem of mapping out which pairs $(b_2, \sigma)$ or $(c_1^2, \chi)$ admit smooth 4-manifolds. The 11/8 conjecture bounds the "lower right" quadrant for spin manifolds [cite: 1, 6]. An anti-anchor to the conjecture is the existence of non-spin manifolds (like the Enriques surface) which effortlessly violate the 10/8 bounds ($b_2 = 10, \sigma = -8$), proving that the bound is strictly tied to the spinor representation and Rokhlin's parity constraints [cite: 9, 12].
*   **The 3/2 Conjecture:** An equivalent reformulation of the 11/8 conjecture in algebraic terms. The 11/8 conjecture ($b_2 \ge \frac{11}{8}|\sigma|$) is strictly equivalent to the 3/2 conjecture for the parameters $m, n$, which states $n \ge \frac{3}{2}(2|m|) \implies n \ge 3|m|$ [cite: 4, 8]. 
*   **The Simple Type Conjecture:** A related open question asking whether every simply connected 4-manifold with $b^+ > 1$ and non-vanishing SW invariants is of "simple type" (meaning the SW invariants are determined purely by 0-dimensional moduli spaces) [cite: 18, 24]. Proving simple type universally is seen as a prerequisite to mastering the geography of SW non-vanishing manifolds.
*   **Relative Genera and the Thom/Milnor Conjectures:** The 10/8-inequality machinery used by HLSX and Taniguchi extends directly to bounds on the slice genus of knots [cite: 14, 20]. Just as Kronheimer and Mrowka used SW theory to prove the Thom conjecture (bounding the genus of surfaces in $\mathbb{CP}^2$) and the Milnor conjecture (slice genus of torus knots) [cite: 14], the relative 10/8+4 bounds generate smooth slicing obstructions for knots in $S^3$ using spin 4-manifolds as cobordisms [cite: 25, 26].
*   **Effective String Theory (EST):** In a distant but related physical domain, lattice gauge theory and effective string theory (using Nambu-Goto actions and normalising flows) are exploring the confinement of Yang-Mills flux tubes. The topological structures of pure Yang-Mills on 4-manifolds are historically the physical origin of Donaldson invariants, hinting that novel lattice/generative DL approaches to EST might one day offer numerical heuristic insights into the moduli spaces of 4-manifolds [cite: 27].

**Sources:**
1. [rochester.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOi2Jit6GHcHuTwKn_E6N4MkL2p2KVZ46Y2SbmgDCeuVD4JT1pFMJUxTmzOdUi2YKxsTmr9JGMcUjjuIpkQ6nxYTV1JF6PMbYBiqcHg40Eg_MAz3k3idbmXeuFtj2K7dVmlDyieyUfCV0xOb_hWGSE7XiOObagc4OIJMiQG_54pOh8)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEesoF4IWXehc3f6G2zbfooiZunEOEehitJLsuu4aQ-vn0JctyhcmDH_Pfv9s_JP8qIAfaOD8zP5bk3V_2nHmp5x6nNLn5m4bQJ4cSwgM6abZ1EhHc)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEomj9oTJqJkL393PjVvr08_QBeGRQwVjB9qzWJaQY1cYLsfSVflL1G3YS5ii3hG6LG_WTkoE33tG6RBmfH_QzGZpIePhz73FADsOkUxEzGGsfAfnyU)
4. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFez8HR5c47C67-6A_Wq3qpJTGHYBxJTVQpHBMVNfFUDl_IYMb_5qoDIzwCxiCuzI6aAo47s_66z2sWua51OtpChWhWVkyJ1YHcVw6R9mD3CCsrE1Abc8sWPCRJHcwJXaa)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3LttJYhQnUbA8KiJfs0E-wDFfQKN0xhxghMOKj715dY0HP1n0JAF9q-apVGHgrheNGbLpKHTYVYyoq356dLKIzX_vImQsJ9663DlAo6gKnvziKrlIhEZVLKOg0CI=)
6. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ1FF1FqYZTHkYXSpfPmjQMKWqmVYnoBrPvkj5atUdRsCz6CEfK6vY58CbPueIF4zz8WCgP7e3T_f5YTRKpFEiXsy71kvSd0dcE99Rodhi6zJ5ZCdcHZK-ZMXAiUD4w8mqBk0HNq6ZNufmdGLsjhzmZj_M3aKlNYKPBwx8MwxlnoKt8Y1IAF8=)
7. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBfJndD_cYMAjCC3RM5WnppLoOgSkKUFxgUFVtyQhOHshe-A2bbBOlcPuqjInDtnQh1EqdnDOn6yY1Qa8yGLEtjLpnHPOvoXq_btUM0PZgOhO6T5vvIY2gqU3JuRg9BZEoGTpDzNJXUNqht0UWxtMfspY1tlgRMoao4dXtWBfTMQ==)
8. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIKt_0fsoWeTTvBBSw8KPxRs5vdSxLmX_NljSlslWNhroiKvbLd2cPIk2W1Y-MbHO_Eqb-cDGJ6D7pzKs4_ZRc02m_0dBMnW3Z3aLBXku-UWlp1bcs5kU2vDWda4a27hY3hBi5)
9. [intechopen.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElwl-2LVComUelc3UH4RqBUuR3g2PQR6XbhK_Od72a42OM9GNFAQ6fgYoVS3QHAwOI3Ccl0qG06ZN2RExX3sR0Z6pd-NgsErbK_WDyY0nyoquaJO4oU1Qn1jRhN4C3)
10. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBaM5llb1jRmGB5F-VkJ-7ZxF8GZNSvMCNnaf2TnrLrMjZCOIX4fa9R7sGtiOQLgHu-YPsH_r5wydS_IUsSLlDl1X00AdD9psGQgh4EyEIXKORY5D91yX6DHrSJHWzfi99NN2k5A==)
11. [gatech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqUyFGw8MSmKtrRZSE45xgnt5NeURyN8eJZzYF1EnsJsHxbVTJtJrOtf_2VfX9fhBavGBg2it2Hnjw5BNp6gr9y1-mTrQM92Jl8xUojJzECha8bk3PSc0e7hYLwgPHpBY1cfh6xlw8zMwDgwlRW4k=)
12. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_Ol5CMjU8e5zTPF9WhnuHxHzkkqLX3NgXzFsN-bqSIndqcbJsy9itPF_Fa6VipzHSXlch0z2UwdBiFgCGrFnnLRM-R9mdKTpWQKsBskmPB3Wwdg==)
13. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMsMa4qnSWbXd5iereXTX4AKP9sYCAdaWq0ChCHHUJuXCUe8jANRan8c1z-GGjkbbnFWksqPf82reoxXUUOZ5xhEQEYLfFn3M5kCwFnrEsmdtERglJplWnmP7LVwKViQ5L_Ubxv7nRWFv3bUAvV53cBzpiP0Sj)
14. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF-l11eUv5ANJsgW1IA8tc9HMr8AWvVfeGTcwYU6Ny6Ic8v9kXc0-s5s3XVlzjtVEYirdC9As02QccvUM5HeGsAAfdKmjHC0b3mpLeB5BFgxGe4N0NY6rk-A==)
15. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe76wdEXlbDG-UrIJlQCXYMyjRuTdSaATxdmKu-rAdVPWUZmLgHjyAt7VFL00dqdIKr1a7CU9YByIOVmSweGfkj-iAmdNVHr9eVQyh0XhbzODikdNn48TBbRgGC_5InsZZn6jI8-phRcb-7zBqMwvZO45FnjcPgz0opH2gc9Se2VDUQp8B83IioM3yt0MOdYE=)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsUukttaQTveOOvk4OepVrAniWLIWBMtKQMYumG5gFIf41V6CtVB2HrmXt-VROm4_Yparv4XqeGH-Tq_SGFmibvO-blEENf50As3PiliQNMFqqizfu8HxLQNxLodcRRYzyAx2WyEUi5PgQ0PI-CmIdEc8Ao5N7q2uC18tLwe-6ftpycwCEEaegaDwkjqAZ2o7o)
17. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDJRg1qmOcRghzpm32FfedTzzGJ9F6idOCLWWCwcMMIAyCwG5EjYdSbLjxSJDRvtw7xLcnL8fdtaVY2pUwJ_B0CantAODKtDMF9paSZFo_9Y20V-t2gqRLlYxv2j7r)
18. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHu1HPrPPagqkSscJ7_2ZEt3GIsqM1hSV9xpAm2M4D-FeirTZUD_SX6ax1MP_G-CrxIGlJzoAbLl8W0fVtfSnzhABTP-urTmoCMtfONypamgKwmabD78qNIZrGOGeQnMUEff2Ksd3Aednzm_N8M8OFV05X1ojUCGQo7A1dxVSca-bBEunaqzHtSr5RRxxArOH7HlU5g)
19. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTesNC7m7aWKLGx8QKxtRxL0JwiDvoVYO4TpA5zN3EJRowG5Z6hyUX-85EGgBN-zpmLpqXcIcMsRfH2oBS1N43CFxjhc1BMqK2BavOGn2NBk83OpNeGt1BKFfqGqmmPsW7EZ1Ju_f4)
20. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJN2Se5XwWWNB5kJxSfNN4_zfuMgFiM59VZWs5WLV7hdNevOPxzRq1gMtvFJgG_vuIOvWDbYsjWQxkVky0Jojv6SvQcrauZcL5V-gmZIjE2JEN73uIUMcDvmhWpUKj0zrMdB4iHbuudDn70zUzetNn2KvOtIxTJVGzJoZCA-Tu1QPsShcIY6p3bbyuMpaZYM12YhGiUaNdjGZ4p2Ok9lXQUjh_XTGRWvwajTBTODMvBmMd27U3XjNIkjRP3NqJHE7e)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFv9af_xys2b2HClX6v_4p8u_t9OkjtYkYu4ut-rS_FsVOzLqclInTqto_LCAY6lt-PQdEfAD5x5qjopSqPQMMVXF7a_X0tEVwDzQEOyadUQR2S6Ujz)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE6qJs7r06B4srkq9oHdYvLILtLIMTMBmSjHxW-dgRSXNnu52iijrp1jeeH-h6E23hwVzlc-NeUX0rkgFZfpujRdqEH3I6e55-ctEO4gSM9VT-xxc7)
23. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKO_baiY670HHki0jjRl0qhiCC4s4v5PPHuc7wxJWIVlDQ0sVfJ85ag30l4lxrgPCMhoYaFcrGkD82ZePw5xtdw5vWKaa9PjOPZejsLxSXJtx5wVVBqpurF_e0K2BO42uP8at-GqnfIwU8N6ioS3x6c07XosA_X1MzsH4GE6rDDOPj83ujjPNIq3BkuwWmGg==)
24. [ncatlab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBdJR7mLnnzjJR0o2zYS-1BY-z8IinzFt6IgTC_uOT4-V6ot2Gm-SyKGlRyGkFp_N9-662Cmu2JQxJOttzYE2zWq6AvK14qSblofhJH5xVBisKilLsFkkwYCQUgzhmXzc9tT49tpmNiYx8cA==)
25. [springerprofessional.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDA14zii-Fn0oLVurTulLB949g_qZYSpBes0WDsde9xzalDdnLkhk_NJ8YpCqu-xuCcukGfxSCQP1eyLlg6ZZONFhzZ1_2ZPDIlzUGhOBh0CyWhD2o4Y1WH3VDY3kDD_lKorX1DBQXWaviTiOnQkampsYM14RWrx2eiqUC2pQq7FlDWr0Di3A-ljdXd45fKA08Gw==)
26. [matrix-inst.org.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpuOOj9Hi8FVLUJNFrFA1IYP8wdkdXG6Vow-jCHsu0k3FSuz43eG7O6gcmOywyWxZBFzNELnLPJRCJYFR7s4a0AbyWawXs-vGm8K2dZ9iStW-MgbOJWWK5fR1fO0dQhCALIMMNbn_Dn4Cf8BxFkDfBiKTkCPsvyPKphB5-fSzRS62xAqvgNXA=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqKUcB4IcXsmdGX6C94A0geuHp-ALig_lP73YrgiPhkQA4L5Kp457xjbWUcQ9w7glofl6fHp9m24g5gT8xK7TEHha5zgbL2tLKlUil5M5MXG3JQKML)


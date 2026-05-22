# Followup [FU-2026-05-22-033 <- row216]: 2 Open Questions Despite the massive resolutions of Dowling's conjecture and the tree metric equival

**Pythia queue id:** 318
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdHTGtQYW9xLUlvUGNfdU1QMHFxRWlBcxIXR0xrUGFvcS1Jb1BjX3VNUDBxcUVpQXM
**Elapsed:** 311s
**Completed at:** 2026-05-22T02:07:12.512733+00:00

---

# Substrate-Grade Research Brief: Topological Classification of Lorentzian Polynomial Spaces

**Key Points**
*   **Current Consensus on Polymatroid Topology:** The projectivized space of Lorentzian polynomials $\mathbb{P}L_J$ for a polymatroid $J$ modulo $\mathbb{R}_{>0}$ is fundamentally a manifold with boundary. Its dimension precisely equals the Tutte rank of $J$. 
*   **The Dressian Boundary:** Recent proofs establish that $\mathbb{P}L_J$ is homeomorphic to a closed Euclidean ball with the Dressian of $J$ (the tropical Grassmannian equivalent) removed from its boundary. 
*   **Negative Resolution of the Ball Hypothesis:** The long-standing hypothesis that the closure of $\mathbb{P}L_J$ within the space of all polynomials modulo $\mathbb{R}_{>0}$ is universally homeomorphic to a closed Euclidean ball has been explicitly refuted using the elliptic matroid $T_{11}$.
*   **Resolution of Dowling's Conjecture:** The polynomial generalization of Mason’s conjecture regarding the log-concavity of independent set numbers has been entirely resolved as of 2026 using the theory of Lorentzian polynomials.
*   **Hyperfield Connections:** There exists a profound, explicit homeomorphism between $\mathbb{P}L_J$ and the thin Schubert cell $\text{Gr}_J(\mathbb{T}_q)$ over the triangular hyperfield $\mathbb{T}_q$, linking tropical geometry with continuous convexity.

**Executive Summary**
This research brief investigates the open question surrounding the complete topological classification of Lorentzian polynomial spaces for all geometric matroids and compactifications. While significant strides have been made recently—most notably the 2025 demonstration that $\mathbb{P}L_J$ aligns with thin Schubert cells in the tropical setting and the 2026 resolution of Dowling's polynomial conjecture—a universal classification governing wilder, non-ball-like closures remains an active frontier. The evidence leans toward a complex interplay between discrete convex analysis (M-convex sets, gross substitutes) and tropical geometry, where rigid matroids exhibit sphere-like compactifications, but generalized geometric matroids unravel into topologies with non-trivial Euler characteristics.

***

## 1. Brief summary
**The open question in one line with Prometheus context:** While recent breakthroughs have successfully mapped the projectivized space of Lorentzian polynomials $\mathbb{P}L_J$ for polymatroids as homeomorphic to a Euclidean ball minus the Dressian, the full topological classification of the compactified Lorentzian polynomial spaces for arbitrary non-rigid and geometric matroids remains unresolved, representing a critical frontier in combinatorial Hodge theory.

## 2. Flagged findings
**Current consensus and where it might be wrong.**

The prevailing consensus in combinatorial Hodge theory and algebraic geometry, established by the foundational work of Brändén and Huh (2019) [cite: 1, 2] and significantly advanced by Baker, Huh, Kummer, and Lorscheid (2025) [cite: 2, 3], is that the space of Lorentzian polynomials serves as a rigorous bridge between continuous and discrete convexity. For a given polymatroid $J$, the projectivized space $\mathbb{P}L_J$ (modulo scaling by positive reals) is non-empty and structurally behaves as a manifold with boundary. The dimension of this manifold is equal to the Tutte rank of the polymatroid $J$ [cite: 2, 4]. 

The most significant recent finding is the explicit geometric characterization of this space: $\mathbb{P}L_J$ is homeomorphic to a closed Euclidean ball with the Dressian of $J$ (a piecewise-linear space of all valuated matroids on the support) removed from its boundary [cite: 2, 3]. Furthermore, it has been established that $\mathbb{P}L_J$ is homeomorphic to the thin Schubert cell $\text{Gr}_J(\mathbb{T}_q)$ of $J$ over the triangular hyperfield $\mathbb{T}_q$ [cite: 2, 4]. This identification is monumental because it translates the continuous, analytic properties of Lorentzian polynomials (such as log-concavity and Hessian signatures) into the discrete, algebraic domain of representations over tropical hyperfields [cite: 2, 5].

**Where the consensus encounters friction:**
The primary point of divergence—and the core of the ongoing open question—lies in the compactification of these spaces. It was previously hypothesized by Petter Brändén that the topological closure of $\mathbb{P}L_J$ within the space of all polynomials (modulo $\mathbb{R}_{>0}$) would be universally homeomorphic to a closed Euclidean ball [cite: 4]. This hypothesis was a natural extrapolation from the behavior of low-rank or highly rigid matroids (e.g., rank 2 or 3 uniform matroids), where the Dressian is trivial or sphere-like, yielding smooth, well-behaved compactifications [cite: 2, 5].

However, this assumption falls victim to **PATTERN_BASE_RATE_NEGLECT**: researchers anchored excessively on the topological behavior of realizable, rigid matroids, neglecting the high base rate of "wild" topological manifestations inherent in the vast majority of non-representable or sparse paving matroids. Baker et al. (2025) proved Brändén's question negative by explicitly demonstrating that for the elliptic matroid $T_{11}$ (a rank 3 matroid on 11 elements), the closure is strictly not a ball, possessing an Euler characteristic of 11 [cite: 2, 5]. Similarly, the space of stable polynomials in $B_{11}$ was found to have an Euler characteristic of 17 [cite: 2, 5]. 

Thus, while the internal structure of $\mathbb{P}L_J$ is fully mapped, the external boundary (the compactification) in the broader space of polynomials is highly irregular for complex geometric objects. The assumption that Hausdorff compactifications of rescaling classes will yield uniformly simple topologies is demonstrably wrong, necessitating a completely new taxonomic framework for these boundaries [cite: 3, 4].

## 3. Problem statement
**Precise object/result being interrogated.**

The precise mathematical object under interrogation is the Hausdorff compactification of the space of rescaling classes of Lorentzian polynomials, denoted as $\overline{\mathbb{P}L_J}$, and its complete topological classification across all geometric structures, particularly those yielding non-ball-like closures [cite: 4, 5]. 

To precisely define the object, we must construct it from its primitive constituents:
1.  **Lorentzian Polynomials:** Let $f$ be a homogeneous polynomial of degree $d$ in $n$ variables with non-negative coefficients. $f$ is defined as Lorentzian if its support is M-convex (equivalent to the set of bases of a matroid in the multi-affine case), and for every sequence of partial derivatives of length $d-2$, the resulting quadratic form has a Hessian matrix with at most one positive eigenvalue (the signature constraint) [cite: 1, 5]. 
2.  **The Space $\mathbb{P}L_J$:** We denote by $L_J$ the space of all Lorentzian polynomials whose exact support is a given polymatroid $J$. By projectivizing this space modulo positive real scaling ($\mathbb{R}_{>0}$), we obtain $\mathbb{P}L_J$ [cite: 2, 4].
3.  **The Dressian $\text{Dr}_J$:** This is the tropical Grassmannian equivalent for the matroid $J$, parametrizing valuated matroids with underlying support $J$. It acts as the boundary structure for the thin Schubert cell [cite: 2].
4.  **The Triangular Hyperfield $\mathbb{T}_q$:** Introduced by Viro for tropical geometry, a hyperfield is an algebraic structure where addition is multi-valued. The thin Schubert cell $\text{Gr}_J(\mathbb{T}_q)$ represents the parameter space of matroid representations over this specific hyperfield [cite: 2, 3].

The problem statement interrogates why the closure $\overline{\mathbb{P}L_J}$ diverges from a closed Euclidean ball for certain matroids (like the elliptic matroid $T_{11}$) and seeks a comprehensive categorical mechanism that can predict the Euler characteristic and homology groups of $\overline{\mathbb{P}L_J}$ based purely on the combinatorial properties of the underlying matroid $J$ [cite: 2, 5]. Furthermore, it examines the natural mapping of the Chow quotient of a complex Grassmannian into this Hausdorff compactification, aiming to bridge the asymptotic structure of Lorentzian polynomials with classical moduli spaces of stable rational curves ($\overline{M}_{0,n}$) [cite: 4, 5].

## 4. Status & bounds
**Last known status, current best bounds, conditional qualifiers.**

**Current Status:**
As of early 2026, the topological mapping of the open space $\mathbb{P}L_J$ is definitively solved, but the classification of its compactifications remains partially open [cite: 2, 3]. 
Concurrently, a massive related milestone was achieved: Dowling's polynomial conjecture, a vast generalization of Mason's conjecture concerning the independent set numbers of matroids, was entirely resolved by Cao, Chen, Li, and Wu (Jan 2026) [cite: 6, 7]. By applying the theory of Lorentzian polynomials, they demonstrated that the sequence of independent set numbers is not just log-concave, but completely log-concave, proving that the specific generating polynomials constructed from independent set bipartitions satisfy the Lorentzian Hessian condition [cite: 6, 7, 8].

**Current Best Bounds & Dimensional Constraints:**
1.  **Dimensionality:** The exact topological dimension of $\mathbb{P}L_J$ is rigidly bounded; it is precisely equal to the Tutte rank of $J$ [cite: 2, 3]. This provides a strict geometric parameterization for the manifold.
2.  **Rank 1 Distance Matrix Bound:** In the associated field of ultrametrics and gross substitutes, the distance matrix of an ultrametric tree has been given a rank 1 upper bound, refining the classical Graham-Pollak result. This directly answers the Eur-Huh question, proving that a set function satisfies the gross substitutes property if and only if its homogeneous generating polynomial $Z_{q,v}$ is a Lorentzian polynomial for all $0 < q \le 1$ [cite: 9, 10].
3.  **Euler Characteristic Bounds:** For compactifications $\overline{\mathbb{P}L_J}$, the Euler characteristic $\chi$ serves as the primary topological discriminator. For uniform matroids of rank 2 and 3, $\chi = 1$ (homeomorphic to a ball). For the elliptic matroid $T_{11}$, precise computations yield $\chi = 11$, and for the space of stable polynomials in $B_{11}$, $\chi = 17$ [cite: 2, 5]. 

**Conditional Qualifiers:**
The analysis of these boundaries is subject to **PATTERN_CONDUCTOR_CONFOUND**. There is a prevailing analytical risk of confounding the continuous analytical boundary of the parameter space (the limits of the Hessian signature condition as polynomial coefficients approach zero) with the discrete combinatorial boundary defined by the Dressian (valuated matroid metrics). The homeomorphism to the ball minus the Dressian [cite: 2] successfully navigates this, but when compactifying, the limits of the continuous polynomial space generate boundary artifacts that do not perfectly align with naive combinatorial deletions, causing the "wild" non-ball topologies.

## 5. Literature (primary sources)
**arXiv IDs, journal cites, authors, dates. Primary only.**

1.  **Baker, M., Huh, J., Kummer, M., Lorscheid, O. (August 4, 2025).** *Lorentzian polynomials and matroids over triangular hyperfields 1: Topological aspects.* arXiv:2508.02907 [math.CO]. [cite: 2, 3, 4].
    *   *Significance:* The seminal paper defining the topology of $\mathbb{P}L_J$, equating it to a ball minus the Dressian, identifying the homeomorphism with thin Schubert cells over the triangular hyperfield $\mathbb{T}_q$, and refuting Brändén's ball hypothesis via the elliptic matroid $T_{11}$ counterexample.
2.  **Cao, S., Chen, K., Li, Y., Wu, Y. (January 23, 2026).** *Dowling's polynomial conjecture for independent sets of matroids.* arXiv:2601.03809 [math.CO]. [cite: 6, 7].
    *   *Significance:* The conclusive resolution of Dowling's 1980 polynomial conjecture (a major generalization of Mason's conjecture) using the framework of Lorentzian polynomials. It proves the ultra log-concavity of independent set numbers across all matroids.
3.  **Brändén, P., Huh, J. (2019 / 2020).** *Lorentzian polynomials.* Annals of Mathematics, 192(3), 821-891. (referenced contextually). [cite: 1, 2].
    *   *Significance:* The foundational text that introduced Lorentzian polynomials, generalized stable polynomials, connected continuous and discrete convexity, and proved that the support of a Lorentzian polynomial is an M-convex set.
4.  **Pagaria, R., Pezzoli, M. (2024 / 2025).** *Hodge theory for discrete polymatroids.* (Referenced as extending Adiprasito-Huh-Katz). [cite: 11].
    *   *Significance:* Extends the combinatorial Hodge theory of matroids to discrete polymatroids, directly interacting with the continuous analytic extensions of Lorentzian polynomials.
5.  **Murota, K. (2003 / 2015).** *Discrete Convex Analysis: A Tool for Economics and Game Theory.* Journal of the Operations Research Society of Japan 58(1):61-103. [cite: 12, 13].
    *   *Significance:* Provides the underlying equivalence between M-convexity, M-natural-concavity, and the Gross Substitutes condition critical for understanding the discrete support of Lorentzian polynomials.

## 6. Attack vectors
**Live techniques; exhausted approaches.**

**Live Techniques:**
1.  **Maslov Dequantization and Tropicalization:** The most potent active technique relies on taking degenerate limits of real algebraic varieties. By analyzing the homeomorphism between $\mathbb{P}L_J$ and the thin Schubert cell $\text{Gr}_J(\mathbb{T}_q)$ over the triangular hyperfield, researchers can use Viro's Maslov dequantization [cite: 2, 3, 4]. This translates intractable continuous derivative checks (the Lorentzian Hessian conditions) into piecewise-linear tropical geometry, allowing the classification of boundary strata via valuated matroids (the Dressian).
2.  **Hausdorff Compactification via Chow Quotients:** Mapping the Chow quotient of a complex Grassmannian into the Hausdorff compactification of the rescaling classes of Lorentzian polynomials. This allows the importing of heavily developed algebraic geometry tools (e.g., moduli spaces of stable rational curves $\overline{M}_{0,n}$) to classify the geometric properties of the compactification [cite: 4, 5].
3.  **Intersection Cohomology and Kähler Packages:** Utilizing the Adiprasito-Huh-Katz framework (Hard Lefschetz theorem, Hodge-Riemann relations) on the Chow rings of matroids. Applying these intersection cohomology techniques to arrangement Schubert varieties provides a cohomological attack vector to deduce Euler characteristics of wild closures like $T_{11}$ [cite: 14]. This technique relies heavily on **PATTERN_RANK_PARITY_LEAK**, where the computation of Betti numbers and intersection cohomologies on the combinatorial complex leaks parity constraints that govern the dimension and orientability of the underlying Lorentzian manifold space.

**Exhausted Approaches:**
1.  **Stable Polynomial Surjections:** Early attempts to classify these spaces assumed that all combinatorial log-concavity could be mapped via homogeneous stable polynomials (a subset of Lorentzian polynomials). This vector is entirely exhausted. As established by Brändén and Huh, the Fano matroid $F_7$ is the support of *no* stable polynomial, whereas every matroid is the support of a Lorentzian polynomial [cite: 1, 2]. Relying on classical stability theory to classify the boundaries of matroidal spaces is fundamentally broken due to these unrepresentable constraints.
2.  **Purely Combinatorial Deletion/Contraction on Polynomials:** Attempting to define the boundary of $\mathbb{P}L_J$ merely by taking zero-limits of coefficients (which mimics matroid deletion/contraction) fails because the algebraic closure limits do not perfectly commute with the combinatorial limits, leading to the non-ball anomalies discovered by Kummer and Baker [cite: 2, 15]. 

## 7. Cross-references
**Related open problems, anti-anchors, candidate primitives.**

**Related Open Problems:**
1.  **Hereditary Lorentzian Extension:** The full extension and characterization of *hereditary* Lorentzian polynomials to higher codimensions and general variables (Marques et al., 2022). This seeks to understand if the connectivity of the simplicial complex combined with the Hessian condition naturally extends to arbitrary Chow rings and simplicial fans without losing the Lorentzian signature [cite: 5].
2.  **Castelnuovo-Mumford Polynomials:** Identifying whether the support of each Castelnuovo-Mumford polynomial (the maximal degree components of Grothendieck polynomials) is strictly M-convex (Mészáros and St. Dizier, 2020) [cite: 16]. 
3.  **Algorithmic Recognition:** Efficiently computing capacity bounds and permanents in broader Lorentzian cones for higher-order derivatives in polynomial time [cite: 5].

**Anti-Anchors (Concepts that counteract false assumptions):**
1.  *Anti-Anchor to Realizability:* The assumption that topological spaces of polynomials must behave like spaces of realizable matrices. The Dressian boundary specifically accommodates non-realizable matroids (like the Vámos matroid), serving as a crucial anti-anchor against forcing field-representation constraints on polymatroid topologies [cite: 2].
2.  *Anti-Anchor to Matroid Based Valuations:* The Matroid Based Valuation Conjecture by Ostrovsky and Paes Leme (asserting every gross substitute valuation arises from weighted matroid rank functions via merge/endowment) was refuted using sparse paving matroids, revealing severe limitations in known construction operations for Lorentzian polynomials [cite: 17, 18].

**Candidate Primitives:**
1.  **Gross Substitutes Condition (Economics):** The gross substitutes condition (Kelso & Crawford) acts as the economic equivalent of M-natural-concavity [cite: 12, 13]. The primitive here is the generating polynomial $Z_{q,v}$; a set function satisfies gross substitutes if and only if $Z_{q,v}$ is Lorentzian [cite: 9]. 
2.  **Ultrametric Tree Matrices:** The distance matrix of an ultrametric tree provides the algebraic primitive for generating strongly log-concave polynomials that satisfy the Lorentzian condition, linking phylogenetics and metric spaces to matroid basis generation [cite: 9, 10, 19]. 

***
*End of Brief*

**Sources:**
1. [mattbaker.blog](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp19CkfwGVksp9CR4FsWHQlJDbZ0q6ZAsdN5smatJM6Ogzug_0RtuvsZn0AwubjUo6-xaPwuAR2-j7qs9Nq5W-Rt5EkssBwwXfhbiM3ya1DxSLpNvNi2xjpcJidyQ5XgVsLjtAbpUpwLdj0rpECA==)
2. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh2Rep3b3I94ffNHTdbi7KI0LZB_xwsmdM1_DdBC7xsMrlWh5FpAow2ex4LLwk25TqKUiIsltLrTuBuywe_jbnT2vax7Ri2ggMPz5BJqxVp4qB9EXonKXUW980GJlm_IxWGL8lMG-b)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4cb3T2JisUUXDedDcYUS117BgfAlJe6mjoZ5f2H-tC7A7xN9qcbZUnzGlNTs6DQiJZW0gLTSqDzAl6zAIfr1MFA8hMPylsTQXOfGEfyFGiabW5A264hhE)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHH5z4jRgym8QjIMaPaCpYZxL7_7w9H4L9MzQcP2oUioTtPvhhDlMObhMTt5u2ADa15sXx5M93tglTRA7PyQtb4V8X8KsMDj4mw2-nrrdWeUZSlOWQ2)
5. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENsXaLPvodK73DXD4whExLBIbxRVXeLIM5XyGawMqJfhdbv7PYVDpeI5jhV5mf8_t1xm2rVW34v5OL6G64FB3wUTM-n4puZiZ8NPccb3NlAEpVL5fUSoITk4yOU534CFmYHaOhvqw1BcEucaLdYg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfkLTrHSwTVEhcKZB5PZF-20303bfqgQTQTt9_bKdS7CfMFTssInFGmep0sf7H-186wJE33n4QVdydLG2AbGIzZvrgrqho_xGCS1rpe4-H-KtSbMfGF5Hp)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPve7fhMTJO7RD82uSh3GwJilqVdukF9wpCYmpYbw6v7XIn9alzLrc4ofpYFiZ01T1hbEU5tDuSsDWvHwtmgpLosIF1pb04DyXSLqRYBN8jYpfUrOmfBqu)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEs2srxml-8dXOhw9D4YNOP4LNMZ6D9mPmYQHw6bZPVJYlcfi-einV8m3tIvV3bXswldCiDPNSwwv-MGsN_KrrcLFqhXDqPwgkl-qZ_M1YvNwMlL5Eq)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwb0nbJfBkxqQ660g79R2nrMsTBJGDBtinknHL-aUueM9sOG6S736IMhoBPV_BHbck0005aRVxO94e1MlHgH4fSEBS7glQ1wvc3IdtQpKYtSprShVyBz9nSvrRa8hbNa0kuqssWQ9kN6RY1cCVH9g4EpkegvPp1hlDBgN5Lbg=)
10. [u-tokyo.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJpByadstaidetPPSOWOu-Y22Rmi5njNKno5iStHrWeOLGFnN3ZBbv7GGwC_yHODmCv8v9ICXTfopd_ksvv0X6VESMw5X5u9LmVospWsUHRMBGmiqcAap6YAHUIo4smFx__O_q1M8nuW0xon1JH3SH-6Q=)
11. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7v2gEzMjHydDVG3MZdL8QWaFXl0GA557hBMR6Okmh6cViua_UPHN-6TogVHGbO5_8PZOIS0-ZqQWHVaoifzaO8s5d_q_6IJSRCRG3-mEGyqFBuu8bnT_XsOtL5SLPQSPKJcEygcBu0W0473iIXC2JVC7Sh4IyZg==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhA4QYM4wUfex5jUL82-uVPBewSbrW8QeKQ6RX8aDebADTEMzOGV_Jz585IK6yhZ-avKvZsGmEbHnVMbEQMMRrr7eOpCAKGaFnjGDXwtFLQsPKWp32RchfScoNm7wZwGTYGfIg6wn6ECzCVmhEIqoV1AsZbY7BnxUbms6rckcJ53JoP3kzF6rXVz66g2-t6scEG1npA_mSxtRl0LMSgTXEliK4a32nm7ND5hCa8YTAl9K73No4lcjkg6QUs7qX)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjeXsd52LOac9W1KaBtq9uVrERjU8Bg6AzdP7XHLF8DfGNHZug5BLemNC0GwE9oFAWi0ZiSZQ3zyJICS2_4VsM8fV1m5sWZdVHoW_HMyXzzii2GosvypurUYJpwZQrwj0MJMFDRhkpVmqs9OvAOVSrHxqOFmp8NlfWmLXDCDhK3Bmt-PwEzPqbTl6Tcwi7CaU1AYEijbbFU3KdCcLvoORZAjv43fo=)
14. [mfo.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFeUrOfGh3iqZE25VSiXOE3y1M8g14PAXNxoenoKKdMDs40fhFIrVlVHaR_aT-oyZ78rx1FcvQlLdtv24a-vXrVaeeroDsMV6_88-H_VgdrgsOGNpL-XheY99CUZzKaQbUCyGlJrzDzhmqGEtDeKCU9_EMOe9qZFY-DNl1cClrHVCyqJIB83u4oiGnP5jSrcQb)
15. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP0caE0HbitspOBy9KmgNE76J3W9PQ91VA8r0ehfaJKF7-9DDpUKA8rrMivDCMphjDQvEdmYz7ks5e4Baj-5KPgE5KHV8qmAt6bBtHcmPnQQhTqy18xRMQ8dHtCiybM44=)
16. [uqam.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEi5wVtzQVpxsFhWi1GQUwa0vuDDB7lyLAFEAloEyPmO467VSS2ShHymSAdlFTFkWLsNixfm3fII-ZGHQCK7qaXsQSda3U_aG8FG-LSsfce1Vry9P_QEhi2sP0=)
17. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJvgz25hwnrPuaONzxxVfpi9eHdhmCMR9qNu-3uyngsRGHTN_UytYx_hJcPSQqqgrLmTmdPipGXkxtw3NMZxr2mWgmRDt4Kz-Ize6md3jmJKEbzMikmPQoGBPPONAjg15k)
18. [lse.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdUR-XjCof5y55-_-XMaDAvKBLLUtOzeZZYImDAg75mUAXKhpJO2ZP_etK9r1e2zpEAzLhCbqIuX_RsCQ7PP2O6_J3p7GoNfztxcMcAms6s3Z-VKMnUX4yhap4hc3LtqRuhiIM3I2IvuB78LuPxrpqWPhrp9U5L_80SYw=)
19. [qmul.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdfgVti3lKgN5Hkpl5ywtqOEszYYcHxEe0lu_FdhV-XWZJBrkA-baz7RPaN96ttPW2_L8-u-YLayouI0GTlBhX0ZpmVB2X2B60zNueoz4RmrgCCxLpMVHQLonC17kKiRIVpRhmbz4wgI6KxwLXLvtsNUJKhK6FJV0pNhX8ZU1sZpypSffy78dDE8rjC1mAiwPRSrETVpQus19grOmD-3xawRZnEYtjbS-18a6qtnWOCGw=)


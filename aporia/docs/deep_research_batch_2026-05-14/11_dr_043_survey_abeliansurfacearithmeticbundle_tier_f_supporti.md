# Prompt 11: DR-043 — Survey AbelianSurfaceArithmeticBundle Tier-F supporting lit (BCGP 2025 + Sutherland 5M + van Bommel 2024-25) [Tier 1]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdFb1VGYXBYT0lPU2xfUFVQdnVXRndBZxIXRW9VRmFwWE9JT1NsX1BVUHZ1V0Z3QWc
**Elapsed:** 273s

---

# AbelianSurfaceArithmeticBundle Tier-F: Primary Literature Verification and Anti-Anchor Analysis

**Key Points:**
*   **BCGP Modularity:** The Boxer-Calegari-Gee-Pilloni (February 2025) result establishes the unconditional modularity of a *positive proportion* of abelian surfaces over \(\mathbb{Q}\), not all abelian surfaces. This represents a massive breakthrough but requires strict coordinate boundaries regarding conditions at primes 2 and 3.
*   **L-Polynomial Coordinates:** Jia Shi’s Las Vegas algorithm (August 2025) explicitly separates the invariant \(L_p(T) \pmod p\) from the full integer polynomial \(L_p(T) \in \mathbb{Z}[T]\), solving the lifting problem in expected \(\mathcal{O}(\log^{2+o(1)} p)\) time. 
*   **Isogeny Primitives:** van Bommel et al. (2024) formally demonstrate that dimension-2 isogeny computations do not decompose into rational prime-degree steps, invalidating direct extensions of dimension-1 algorithms (e.g., Vélu's formulas).
*   **Sutherland LMFDB Expansion:** The ~5-6 million genus-2 curve dataset is foundational but remains structurally distinct from the underlying Jacobians, Sato-Tate group classifications, and modular forms.

This report is formulated strictly as a substrate input for Project Prometheus. Findings are directed toward anti-anchor pins, primitive registrations, catalog edits, and training-corpus filters. Mathematical invariants are maintained as strictly distinct coordinates (HARD-5 compliance).

***

## (a) PRIMARY SOURCE CONFIRMATION

The `AbelianSurfaceArithmeticBundle Tier-F` candidate is a composite of four distinct major mathematical advancements spanning 2023–2025. Verification against primary literature yields the following substrate registrations.

### 1. BCGP Modularity Proportion (Boxer, Calegari, Gee, Pilloni)
**Status:** ANNOUNCED-NOT-PUBLISHED (Preprint)
**Date:** February 28, 2025
**Source:** arXiv:2502.20645 [math.NT] [cite: 1, 2].

The primary source explicitly avoids claiming the unconditional modularity of *all* abelian surfaces over \(\mathbb{Q}\). Instead, it targets a defined positive proportion.
*   **Exact Theorem Statement (Theorem A in source):** "Let \(A/\mathbb{Q}\) be an abelian surface with a polarization of degree prime to 3. Suppose the following holds: (1) The mod 3 representation: \(\rho_{A,3} : \mathrm{Gal}(\overline{\mathbb{Q}}/\mathbb{Q}) \to \mathrm{GSp}_4(\mathbb{F}_3)\) is surjective. (2) \(\rho_{A,3}|_{G_{\mathbb{Q}_2}}\) is unramified, and the characteristic polynomial of \(\rho_{A,3}(\mathrm{Frob}_2)\) is not \((x^2 \pm x + 2)^2\). (3) \(A\) has good ordinary reduction at 3 and the characteristic polynomial of Frobenius at 3 does not have repeated roots. Then \(A\) is modular." [cite: 2, 3].
*   **Substrate Translation:** Register `modularity_status` as a conditional boolean dependent on `mod_3_Galois_representation_image` (must map surjectively to \(\mathrm{GSp}_4(\mathbb{F}_3)\)), `reduction_type_at_3` (must be `good_ordinary`), and `local_Galois_action_at_2`. 

### 2. Shi 2025 Las Vegas L-Polynomial Lifting
**Status:** ANNOUNCED-NOT-PUBLISHED (Preprint)
**Date:** August 14, 2025
**Source:** arXiv:2508.11028 [math.NT] [cite: 4].

Shi's work necessitates a strict coordinate split between the modular invariant \(L_p(T) \pmod p\) and the integer invariant \(L_p(T) \in \mathbb{Z}[T]\). 
*   **Exact Result Statement:** "In this article, we present an \(\mathcal{O}(\log^{2+o(1)} p)\) Las Vegas algorithm that takes the \(\bmod p\) output of Harvey and Sutherland's implementation and outputs the full zeta function." [cite: 4].
*   **Substrate Translation:** Do not conflate "average polynomial time L-function computation" with "full zeta function computation." Harvey-Sutherland generates the mod-\(p\) reduction of the numerator in \(\mathcal{O}(\log^{4+o(1)} p)\) average time per prime [cite: 4]. Shi (2025) provides the necessary Las Vegas probabilistic lift (using randomized group operations on the Jacobian over \(\mathbb{F}_p\)) to recover the coefficients \(a_1, a_2 \in \mathbb{Z}\) bounded by Weil limits [cite: 4, 5].

### 3. van Bommel Isogeny Class Computation
**Status:** PEER-REVIEWED
**Date:** 2024
**Source:** AMS Contemporary Mathematics (LuCaNT proceedings) [cite: 6, 7].

van Bommel, Chidambaram, Costa, and Kieffer provide the algorithmic primitive for enumerating `isogeny_class` for principally polarized (p.p.) abelian surfaces.
*   **Exact Result Statement:** "We describe an efficient algorithm which, given a principally polarized (p.p.) abelian surface \(A\) over \(\mathbb{Q}\) with geometric endomorphism ring equal to \(\mathbb{Z}\), computes all the other p.p. abelian surfaces over \(\mathbb{Q}\) that are isogenous to \(A\)." [cite: 6].
*   **Substrate Translation:** The algorithm leverages explicit open image techniques for Galois representations and Dieulefait's tests to find a finite superset of non-surjective primes [cite: 6, 8]. It successfully processed 1,440,894 isogeny classes of typical Jacobians of genus 2 curves [cite: 6].

### 4. Sutherland 5M LMFDB Expansion
**Status:** ANNOUNCED-NOT-PUBLISHED (Database Expansion)
**Date:** 2023–2025
**Source:** Simons Collaboration / LMFDB internal presentations [cite: 9, 10].

Sutherland's dataset expansions provide the empirical base for the above algorithms.
*   **Exact Result Statement:** Data generated via search routines yielded "more than 6.2 million genus 2 curves of conductor \(\le 2^{20}\) with more than 2.5 million distinct L-functions" [cite: 9]. Older 2023 presentations cited "more than 5 million genus 2 curves... including 1,440,894 distinct \(\mathrm{USp}(4)\) isogeny classes" [cite: 11, 12].
*   **Substrate Translation:** The database expansion separates `curve_equation` coordinates from `L_function` coordinates and `Sato_Tate_group` coordinates (e.g., \(\mathrm{USp}(4)\), \(\mathrm{SU}(2) \times \mathrm{SU}(2)\), \(N(\mathrm{SU}(2) \times \mathrm{SU}(2))\)) [cite: 11, 13].

***

## (b) FOLLOW-ON WORK (2024-2026)

Literature from late 2025 to early 2026 actively ingests these findings. These connections must be registered in the work-queue to ensure dependent primitives update when base algorithms change.

1.  **Gee 2025 (ICM 2026 Survey):**
    *   **Date:** October 03, 2025 (arXiv:2510.02756) [cite: 3, 14].
    *   **Context:** Toby Gee formalized the exposition of the BCGP result for the 2026 International Congress of Mathematicians [cite: 14, 15]. The survey clearly delineates between *potential* modularity (proved previously by BCGP for all abelian surfaces over totally real fields) and *unconditional* modularity (proved for the positive proportion). 
    *   **Behavior Delta:** Add a metadata tag `ICM_2026_expository` to Gee's paper to serve as a high-density, peer-reviewed proxy for the BCGP preprint during training-corpus filtering [cite: 14, 15].
2.  **Gu 2025 (Modularity of K3 Surfaces):**
    *   **Date:** December 04, 2025 (arXiv:2512.04732) [cite: 16, 17].
    *   **Context:** Chao Gu extends BCGP techniques (specifically treating \(\mathrm{GSp}_4\)-type abelian varieties and compatible systems) to prove the *potential automorphy* of K3 surfaces over a totally real field \(F\) with Picard rank \(\ge 17\) [cite: 16, 17].
    *   **Behavior Delta:** Create a dependency link: `AbelianSurfaceModularity` \(\to\) `K3SurfacePotentialAutomorphy_Rank17`.
3.  **Shi 2026 (Genus 3 Extension):**
    *   **Date:** February 01, 2026 (arXiv:2602.00965) [cite: 18].
    *   **Context:** Shi extends the August 2025 Las Vegas L-polynomial lifting algorithm to genus 3 curves, achieving \(\mathcal{O}(p^{1/4+o(1)})\) expected time on average [cite: 18].
    *   **Behavior Delta:** Register a distinct algorithm coordinate: `LPolynomial_Lift_LasVegas_G3`. This confirms the extensibility of the primitive and prevents locking the lift logic exclusively to Genus 2.

*Flag on Follow-On Work:* Be cautious of literature citing BCGP 2025 as having "solved the paramodular conjecture." The paramodular conjecture strictly correlates abelian surfaces of conductor \(N\) with paramodular forms of level \(N\). BCGP 2025 provides an automorphic lift to \(\mathrm{GL}_4/\mathbb{Q}\) (transferred from \(\mathrm{GSp}_4/\mathbb{Q}\)), which implies the L-function properties, but it does not completely resolve all structural isomorphisms demanded by the full paramodular conjecture for *all* conductors [cite: 2, 9].

***

## (c) FALSE-FORM RECURRENCE

The substrate must actively resist gravitational wells present in LLM training corpora and casual mathematical discourse. Searching the 2024–2026 literature reveals several critical false forms that necessitate strong anti-anchor pins.

### Gravity Well 1: Collapsing "Positive Proportion" to "Universal Modularity"
*   **False Form Asserted:** "Boxer, Calegari, Gee, and Pilloni proved that all abelian surfaces over \(\mathbb{Q}\) are modular."
*   **Instance:** Science journalism and aggregator models naturally compress complex conditional theorems. For example, a Quanta Magazine article (June 02, 2025) titled "The Core of Fermat’s Last Theorem Just Got Superpowered" contains instances where the result is loosely framed: "...proved that every abelian surface belonging to a certain major class can always be associated to a modular form" [cite: 19, 20]. In downstream commentary (e.g., Reddit, automated summaries), this degrades into "modularity for abelian surfaces is solved" [cite: 20, 21].
*   **Anti-Anchor Required:** `Anti_Anchor_Pin_01`. Ensure the predicate `modularity_status(A)` does not return `True` for an arbitrary abelian surface \(A/\mathbb{Q}\) without satisfying the `Galois_mod_3_surjective` and `ordinary_at_3` invariants [cite: 2, 3]. The distinction between *potential* modularity (true for all over totally real fields) and *unconditional* modularity (true for the positive proportion) must be strictly enforced [cite: 3, 22].

### Gravity Well 2: The Dimension-1 Algorithm Fallacy (Isogeny Decomposition)
*   **False Form Asserted:** "Isogeny classes of abelian surfaces can be computed by factoring division polynomials and applying Vélu's formulas."
*   **Instance:** This is a default assumption inherited from elliptic curve (genus 1) cryptography and arithmetic geometry.
*   **Primary Source Correction:** van Bommel et al. (2024) explicitly define this as an obstacle: "(1) Isogenies no longer decompose into rational, prime-degree isogenies. (2) There is no known analogue of Mazur’s theorem for higher-dimensional abelian varieties. (3) Division polynomials are too big to be efficiently computed..." [cite: 6].
*   **Anti-Anchor Required:** `Anti_Anchor_Pin_02`. Bind `isogeny_computation_g2` to explicit open image techniques (Dieulefait's bounds) and Richelot/higher-dimensional splitting operations, explicitly rejecting naive Vélu mappings [cite: 6].

### Gravity Well 3: Conflating Mod-p Numerators with Full Zeta Functions
*   **False Form Asserted:** "Harvey's average polynomial time algorithm computes the L-function of a genus 2 curve."
*   **Instance:** General computational number theory literature frequently cites Harvey-Sutherland as computing L-functions in average polynomial time [cite: 23, 24].
*   **Primary Source Correction:** Shi (2025) clarifies that Harvey's algorithm outputs \(L_p(T) \pmod p\). "While Harvey's algorithm can also be used to compute the full zeta function, no practical implementation of this step currently exists" prior to Shi's Las Vegas lift [cite: 4].
*   **Anti-Anchor Required:** `Anti_Anchor_Pin_03`. HARD-5 coordinate separation. \(\text{Coordinate A:} \ L_p(T) \pmod p\) (Complexity: \(\mathcal{O}(\log^{4+o(1)} p)\) average) must be distinct from \(\text{Coordinate B:} \ L_p(T) \in \mathbb{Z}[T]\) (Complexity: \(\text{Coordinate A} + \mathcal{O}(\log^{2+o(1)} p)\) expected local Las Vegas time) [cite: 4, 5].

***

## (d) RECOMMENDATION

**1. Verification Assessment:**
The anti-anchor candidate is **CORRECT BUT NEEDS REFINEMENT**. The supporting literature accurately captures the state-of-the-art for the Genus-2 Rosetta Stone (Tier-F primitives), but the coordinates mapped to these sources must be strictly subdivided to satisfy HARD-5 constraints. 

**2. New Sub-Anchors & Companion Anti-Anchors Discovered:**
*   **Primitive Registration (`AbelianSurfaceModularity_PositiveProportion`):** Register the BCGP 2025 result specifically as a positive proportion conditional on 3-torsion representation big-image hypotheses [cite: 1, 2].
*   **Primitive Registration (`IsogenyClass_NonDecomposable_G2`):** Flag dimension-2 isogenies as fundamentally distinct from dimension-1 prime-degree networks. Map to the van Bommel 2024 HDME (high-precision arithmetic) algorithm [cite: 6, 25].
*   **Coordinate Separation (`LPolynomial_Lift_LasVegas`):** Instantiating Shi's 2025 algorithm as the definitive bridge between `mod_p_reduction` and `integer_L_polynomial` spaces for genus 2 [cite: 4].
*   **Coordinate Separation (`Sato_Tate_USp4` vs `SU2xSU2`):** Based on the Sutherland 5M dataset, force the substrate to register imprimitive L-functions (products of elliptic curve L-functions / RM abelian surfaces) as mathematically distinct coordinates from generic USp(4) Sato-Tate group Jacobians [cite: 11, 13].

**3. Work-Queue Entries for Substrate:**
*   **Task 1:** Ingest the specific parameter bounds from Shi 2025 regarding the 2-rank of the Jacobian and the factorization pattern of the sextic \(f(x) \in \mathbb{F}_p[x]\). These are required for the candidate elimination phase of the Las Vegas lift [cite: 4].
*   **Task 2:** Trace the 2-3 switch methodology from BCGP 2025 [cite: 1, 2]. Register the classicality theorem for ordinary p-adic Siegel modular forms (Pan-style) as a new primitive `Siegel_pAdic_Classicality`.
*   **Task 3:** Update the `K3Surface` taxonomy to include Chao Gu's 2025 (arXiv:2512.04732) proof of potential automorphy for Picard rank \(\ge 17\), mapping its reliance on the BCGP $\mathrm{GSp}_4$ compatible systems [cite: 16, 17].
*   **Task 4:** Add Shi's February 2026 genus 3 follow-on (arXiv:2602.00965) to the `L_local_poly` pipeline to verify cross-dimensional algorithmic stability [cite: 18].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3z2yOQ2ikqWELckW5jlT9-4UyV52puhMbC7_XcMRItPe2bFA_8dXKnOoK2L7CgtPZk2GJFc-0fe_zTkCRqaj82b6pPXsP9qiv9ocNOjB9CoJ6KtIc)
2. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhAIiXsgo8dtXMcbZHs4ViyujZT2s4H-Qc01teyWWEztnbtmlCvE5mvL4ypQDKxCOzcvcM_VGt8uCtFenUZsnocQ_CyK3m778NG03pLTLIcNa5ZrmwRthfW3mLamkNp-5hY4ylH3wiXkocIJQSlQXifaLY5sOiEhA=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECACNw8KlC-ezYkq6TSUMs5oaV5el9sx8Ox99M9b1LpUCtj6Qh4pkdZBVqsGCXPPAmFgW4Uhx5zvddnVhZdC1BDoY9lF8iHgHiXT65JUspI5lxO754fRUr)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE57zxEnjcujBPE2tJSfEZgWiE3I-g0FkeWhAdm0fPnm6LZjtcO34-QxeghyDIhSODApwG11qNfqeza04HOq52QXsgrL8Mw2BvSXowjfjd_sbhkkglp)
5. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFg-Xgs_c2S-ftewtFAtZ0LC0apR9-9T17hsoGOLbJHilXzonTzz251oW6dqekqmiTiQpAKIC7UyCBwsoeEiqCCi9YGEDZjP00EZlhddjq8ZwKV8_RpRGEuw72QNOjDV0v-lxPiUrOEHpX2xOcDEWrjipJJIoj7HJ6AQDOF-24rY83_0A==)
6. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_44eI7ijwA82wO4Cg9wtpckUjuVvUnz3yUWrdX36FMO8egl-agN2KempbPUqsIApFT8I0jTRJNXy4BQSzztNU498wH7FbDB9lyWjE_atAQCMbw7sA6LK0vQ9JuTyl8Ke_WGbPeXRd0OK7cDY9w-W0rV3QWHX7b8TE5Iuqddelsg==)
7. [raymondvanbommel.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPyuVheoXLipNTgUE5Ul1N9KkaGhns19ZwKLOIrSp4XWeKYFjOrv271V5v9JffZ6wc100uQeWnuXDe3Ns4AS80QUo-BxKv2P0yVfj-lAOR-tw=)
8. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHe-3aIHJqBP5I2KumhR9ub9IHw1kbHsw4xzGUxvD9tXLdf89pBilJERHd7ZRrmNhO_mW3PyF3Mi-KE6p12IoFDRPInf-F1Iopkkpo6cI8ZgnG9FuXLffNBDg==)
9. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbhYoCyPUwtHApIHq_TW5dvkCf5wAiMSHBcAEOUXEtw2Y_1rlNwC-BplZTs95TCTN2soP-zaXBxRl00O8mGt-Q62TuTaECpWXspigEA5XY373aZzleiODHsJ_lze4b5fnM4WTerCw=)
10. [wlu.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFdubXc_ddpOjTXla6SZSeVKjrB1vVPT2wnuqWrygz7AvjvTkVry0ipThMjz0ef9kCSIERdyQggwKi2W_zHwB6TqWABV9zr2lpS8dns9mNrieb-M0lK8NN-pAjxOPzw-yD2pBvn-BhEvWuJ0AcbdSDQSo_i1rDeKcpmQ==)
11. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGEWgSLITfIzq-AYRey5t7-iBbLJkiGwRCCqT-xUTJKVd80Xj02XA50mt4V6lz2noY9zU8EnqwUoksdczgZJ7BErvmD3JJtgzVZQzQbHu3Lm8u-a32jBqT7m7N6yRJcKc=)
12. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG86VgbK3MvcvDm1XjPXR34VWfZ2wQLLwDayhAZoyqKOcylq6-_Tjgva8wkQkn1zVXNpnLcaA_0urPeTwyKf2odQ4XtRCak7aAHiDBhKWE_OaXtoc3LL6sQG1Iv3kV14WslWlI=)
13. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS-rklreulJmKjOrc_oHLPjC0F8oYZpcQlvUSdh3N6Rh9WhBxcCr0As9-t2He7eXertxboGorG49tmJngE4XJNz5McjFZvCgPILPqtM9m9Y84aP9mAFv7haK9O27V6LZvE-T-hcBwL8uzx)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_hyjYz5ofo4ZUmswCug1BafUX3p1bo-H_QmO2QW_h11kkOKITl2ih0Qc76xQ3pTR_UnA73QtfV3qM1ekezs8aC5orvzhXkqot9FEipRnqs1WL60az)
15. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-tMWq-OwE6f84UF1SvDoidx1ILeWR5PNhjk0CcPSwymTafS4m_KyE2gUeGSlJ46iSIA54tvVi43N01j9OWcZMjHxl8IHsFA8LkO-7rCtogez8GXtRZ5FJ4wsGiJdXUzThN3N13-1wqbm2wBywlKs=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVlT14LNUsMytn-EhD5ZxJwK1EMGPF_O0mEjDziHOMAzbHdZFEDGquFdSCaQg0F9jm6VT0cdueWLjXJJoX6Xxu2wYAj0bZRZkZWKzPytrprACnnSBR)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU5ZQPKaxYVFR_dtrvSMXLvgAp-z_A__Kh6ySFBTmL7NQRxjskoW5gh2U6fB71cm46uuSlG4xE5Ht1wxeDxgtk3arAR1aqb2ckaWQnqQhHoV_fZGj-KfaZla6PsvLangIh3itnMS6U29k8N1bHj4ADWakj6BxX1zwIV2ziTvHkHX36DM2_bdPZY3KWmypAJhuA96OG6lE73aPlW9OzOLZdJOXSH2ZNl2vg)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVcotXlZthSWWqvUhEh0tGX_YoXemJk4lNvAdJ67Qv91KA8KA9NSb0gew7Mjl84RjvuCltkNv4k09OyICMZAxBlpQrDcrkiALRUVaKP8MUTqJ4M9oK)
19. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBI-N6Ilza65273saiCs0p7D8X7M5WvD5czbT-jXcSnC6-4Nu5kuA_sqsurZhWaUYXBa1oggocrLzOkzXoKPSfvUo78u6jmu4St78ABn0b4C4ndWRsnUheoCiKbSfxexdSouJVsXqltJ-Ah_bwsiAtmcHoRJd1115pU9dyMEsi6LwPZPDwY_KCPegMcshTFRb9-u0I)
20. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZIW6peF8At1gDuobdvPXwEmaGTQmeKKsQ_NHqfzr5wH_WjSEsugMlOygOvs71AZEopuWmDkYElpu4rZBxPk8FTG-xu1f-x1yeXYWFp0YwBZxBWbtMdnpoxmWNfJ7t81Sm3ZznUpLHOQjxEazO9yB3fP8CL_6zUsAzKSk1s_cv7Txbdb8lcMZhmqp-NlWk)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF-WKSNN88QKwpuMtLCHZuYI-0KyfEIXP2D7HaYf0idS-PQgkTNRomAYgVZYpUj34hJJJqdDLPCTyv8nIR2pmmnMUisvgl4AcxbzzmQQMWy8UM7hs4)
22. [warwick.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4eTwUI3diMQZKD2AIZQrlDbNYAR3ZoJ9dblkNfwyW4NaK3lCfBOfcLys1D3rCkCMe_rVFyLA8wjomiD8kI3jyuKQXez8X1yWFwSXlZi_jJdmlBF1WLTQ_usnamaEkhrZc4fcthyD1XhrQTvGL-haZBAgqXTUqTutJpMy3OQ==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTbliJMwaGpjfR8__ERAW9UtTchBUYGCWBihQKmxnehFilbcjjj2FNbPTp-SOkAPt4S2OHhXDgd72JAyjZciGyZxoVMNpbKMJEfDWBW3sCFNdtfN7uyw46brIbhDaoXViGZQF6uyCuYhwN8rGLC4uqaoopULFr4ZaPTKCddzMeZU7A6a9RLa82yzrBf04Lw3rpUnbO0cyVaIuQuU0N-YxKRPqykWGzGCA-_vWA2egOjOktXMEyDpMNhg==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2ImuBNHlMIKgB2pb4qL6MpzOXWqtXK1GZ8j3bk6hN-Yt0iNfizJkJvpTwgJ5JIzzIkQQnr3ol0MmIitAXx5vnMVj8VEl0r9JEvVqEosW1WGKtiLY3YBFbB35gLiAx6e5w6Sh9BpQszjwKHSH-NSNcxmRmQKIZN2_752VcCciQbzpydDnCQJTFPWE04HdD4ASESb1cwKOQeuiBxieRFdFmNcGctW8sgThwLw==)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMzXySz9Mh4aCJ2tN5WxWg9S1ZnTzI5TQbqNIQMnv73ZRt5uj1MOaRjWt7tYZbUCFCLmVZO2vSd0QGPwN7UjrwHI_rf2riTVdE12F6kk94qSC1BJERdSHVqc02VB5PSVHJ1Q==)


# Prompt 17: DR-224 — Regina + SnapPy 3-manifold census tabulation completeness 2024-2026 [Tier 3]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDSWdGYXAyNkl0UzhfdU1QeEtDbjZRZxIXQ0lnRmFwMjZJdFM4X3VNUHhLQ242UWc
**Elapsed:** 303s

---

# Anti-Anchor Verification: Regina and SnapPy 3-Manifold Census Completeness Coordinates (2024–2026)

**Key Points:**
*   Research indicates that the conceptualization of "census completeness" in 3-manifold databases must be strictly decoupled into mathematically distinct coordinates: **minimal ideal tetrahedra count** versus **hyperbolic volume**. 
*   It is rigorously proven (UNCONDITIONAL) that the orientable cusped hyperbolic census is complete up to 10 tetrahedra (PEER-REVIEWED, February/March 2026) and 11 tetrahedra (ANNOUNCED, March 2026).
*   It seems highly likely that volume-based completeness remains strictly CONDITIONAL and conjectural beyond specific threshold values, creating a significant false-form gravity well in automated theorem proving and calibration environments.
*   Conflating orientable cusped completeness with closed or non-orientable completeness represents an ongoing structural vulnerability in topology databases.

**Substrate Context:**
This verification directly informs the Ergon knot/3-manifold calibration battery and the `KnotInvariantBundle Tier-F` primitive coverage. Project Prometheus requires absolute coordinate precision; thus, the candidate anti-anchor "Regina + SnapPy 3-manifold census tabulation completeness 2024-2026" must be refined to explicitly capture the disparity between algorithmic tetrahedral enumeration and volume-bounded spectrums. Failure to separate these invariants pollutes training-corpus filters with false completeness guarantees.

---

## (a) PRIMARY SOURCE CONFIRMATION

To evaluate the anti-anchor, we must isolate the exact theorems bounding the 2024–2026 census frontier. The primary gravitational well to resist here is the assumption that a "complete census" implies completeness across all geometric and topological invariants. We must rigidly separate the coordinates.

**Coordinate 1: Minimal Ideal Tetrahedra Count (UNCONDITIONAL)**
The definitive primary source for the expansion of the orientable cusped hyperbolic 3-manifold census is the work by Shana Yunsheng Li, published definitively in the proceedings of the 42nd International Symposium on Computational Geometry (SoCG 2026) [cite: 1, 2]. The preprint (arXiv:2512.02142v1) was announced on December 1, 2025, with the definitive revised version (v2) issued on March 4, 2026 [cite: 2, 3]. 

Li's work provides an UNCONDITIONAL completeness guarantee for a specific coordinate—the number of ideal tetrahedra. The primary result states:
> "Theorem 1. There are precisely 150,730 orientable cusped hyperbolic 3-manifolds whose minimal ideal triangulations consist of 10 tetrahedra. Moreover, there are precisely a total of 496,638 minimal ideal triangulations of these manifolds." [cite: 1, 2].

This expands the prior 9-tetrahedra frontier (44,250 manifolds, Burton 2014) significantly. Furthermore, Li computes exact behavior deltas for downstream knot theory applications:
> "Theorem 14. There are precisely 439,898 exceptional Dehn fillings on orientable 1-cusped hyperbolic 3-manifolds in the 10-tetrahedra census." [cite: 1, 2].
> "Theorem 15. There are precisely 1,849 manifolds in the 10-tetrahedra census that are exteriors of knots in \(S^3\)." [cite: 2].

**Coordinate 2: Hyperbolic Volume (CONDITIONAL / CONJECTURAL)**
In stark contrast to tetrahedral count, the completeness of the SnapPy/Regina census with respect to the coordinate of **hyperbolic volume** remains strictly CONDITIONAL. The definitive primary source demonstrating this constraint is Laura Wakelin's paper "Characterising slopes for hyperbolic knots and Whitehead doubles," published in *Algebraic & Geometric Topology* (Volume 26, Issue 2) on February 11, 2026 [cite: 4, 5].

Wakelin explicitly bounds her results on characterising slopes by relying on the unproven volume completeness of the SnapPy census. The text confirms the mathematical distinction:
> "Assuming that the list of 2-cusped orientable hyperbolic 3-manifolds obtained using the computer programme SnapPy is complete up to a certain point, we use hyperbolic volume inequalities to generate a refinement for the special case of Whitehead doubles." [cite: 4, 5].

Crucially, Wakelin defines a specific metric for this conditional status, mapping the $k$-th volume $V_k$ to the number of SnapPy census manifolds $a_k$:
> "...relies on the conjectural completeness of the SnapPy census of such manifolds up to a given point. That is to say, let $V_k$ denote the $k$-th volume which appears and let $a_k$ denote the number of SnapPy census manifolds with volume at most $V_k$. We say that the SnapPy census is complete up to stage $k$ if it includes every 2-cusped orientable hyperbolic 3-manifold of volume at most $V_k$." [cite: 4, 6].

**Coordinate Distinction (HARD-5 Requirement):**
The substrate must strictly register these as distinct coordinates. The number of ideal tetrahedra (geometric complexity), hyperbolic volume ($V$), cutwidth, Matveev complexity, and Heegaard genus are **FIVE distinct coordinates**. As demonstrated by Alexander He et al. (arXiv:2312.17556v2, May 20, 2024), algorithms implementing one-vertex triangulations of Heegaard splittings in Regina show that cutwidth is bounded by $4\mathfrak{g}(M) - 2$, which scales entirely differently than tetrahedral count [cite: 7].

## (b) FOLLOW-ON WORK (2024-2026)

In the 24-month window leading up to mid-2026, the computational topology frontier expanded rapidly, further refining the anti-anchor candidate. 

**11-Tetrahedra Census (ANNOUNCED-NOT-PUBLISHED):**
Immediately following the SoCG 2026 acceptance of the 10-tetrahedra census, S. Y. Li announced the successful tabulation of the 11-tetrahedra census. This is maintained in the GitHub repository `snappy_11_tets` (accessed March 2026) and was integrated into the SnapPy 3.3 release cycle [cite: 8, 9]. The repository notes:
> "This repository stores the manifold database of a complete census of all 505,352 orientable cusped hyperbolic 3-manifolds whose minimal ideal triangulations consist of 11 tetrahedra..." [cite: 8].

This follow-on work pushes the UNCONDITIONAL tetrahedral completeness bound to 11. The SnapPy 3.3.2 release notes (March 7, 2026) formally log the "Automatics detection of manifold censuses `snappy_16_knots`, `snappy_11_tets`, and `plausible_knots`," effectively making this data a default primitive in modern topology stacks [cite: 9, 10]. 

**Cosmetic Surgeries Application (ANNOUNCED-NOT-PUBLISHED):**
On April 3, 2026, Qiuyu Ren released the preprint "Families of cosmetic surgeries" (arXiv:2604.02672v1), utilizing both the 10-tetrahedra and 11-tetrahedra censuses [cite: 11]. Ren's work explicitly relies on the newly established databases to construct infinite families of chirally cosmetic surgeries on asymmetric 1-cusped hyperbolic 3-manifolds [cite: 11]. Ren cites Li's `snappy_11_tets` as a critical infrastructural dependency [cite: 11]. 

*Flag for Substrate Caution:* Ren cites an upcoming paper by T. Ito, "A non-torus positive two-bridge knot does not admit chirally cosmetic surgeries," slated for the *Journal of the Mathematical Society of Japan* 78 (2026) [cite: 11]. If Prometheus parses this, it must flag Ito 2026 as an unverified conditional dependency until the peer-reviewed manuscript is entirely ingested.

## (c) FALSE-FORM RECURRENCE

The primary reason this anti-anchor is strictly required is the ongoing gravity well in automated reasoning and unstructured literature regarding "census completeness."

**The False Form:** 
*Assertion:* "SnapPy contains a complete census of all simple hyperbolic 3-manifolds, so if a manifold minimizing a certain invariant is not in the census, no such manifold exists."

**Recurrence and Evidence:**
The false form recurs when authors or models collapse the ideal tetrahedral coordinate into the hyperbolic volume coordinate. A manifold may require a large number of minimal ideal tetrahedra (putting it outside the proven 10- or 11-tetrahedra bounds) but still possess a relatively small hyperbolic volume. If an algorithm searches the SnapPy census for the "smallest volume manifold with property $P$" and fails to find it, it cannot unconditionally claim that no such manifold exists, because the census is not rigorously volume-complete up to that threshold.

Wakelin (2026) actively guards against this false form by explicitly stating the conditionality: "If the SnapPy census of 2-cusped orientable hyperbolic 3-manifolds is complete up to stage $k$..." [cite: 4, 6]. However, secondary literature and LLM zero-shot outputs frequently drop this caveat, asserting volume minima as unconditional theorems based on SnapPy lookups.

A secondary false-form recurrence lies in conflating orientable, non-orientable, closed, and cusped bounds. Li (March 2026) explicitly warns about this: 
> "Note that triangulations representing nonorientable manifolds are also included and carried through the tests, though we will discard them..." [cite: 2, 3].
Models often assert "the census of all 3-manifolds up to 10 tetrahedra is complete," failing to append the necessary "orientable cusped hyperbolic" qualifiers. The closed census and the non-orientable census have entirely different completeness frontiers. 

If this false form is allowed to propagate in the Prometheus substrate, it will result in the generation of false proofs where a search space is prematurely truncated based on the assumption that SnapPy's volume bounds are as unconditionally exhaustive as its tetrahedral bounds.

## (d) RECOMMENDATION

The anti-anchor candidate **"Regina + SnapPy 3-manifold census tabulation completeness 2024-2026"** is mathematically imprecise and requires immediate refinement to function effectively within the `KnotInvariantBundle Tier-F` primitive coverage.

**Concrete Action Items:**

**(i) Anti-Anchor Refinement & Inversion:**
The true form of the candidate is partially correct but requires **splitting** to adhere to the HARD-5 coordinate separation constraint. 
*   **Create Substrate Input 1:** `Primitive_Registration: CuspedTetrahedralCompleteness`
    *   *Status:* UNCONDITIONAL
    *   *Bound:* Complete up to 11 minimal ideal tetrahedra (505,352 manifolds).
    *   *Source:* Li (2026), `snappy_11_tets`.
*   **Create Substrate Input 2:** `Anti-Anchor_Pin: CuspedVolumeCompleteness`
    *   *Status:* CONDITIONAL / CONJECTURAL
    *   *Rule:* Any theorem asserting minimum hyperbolic volume via SnapPy enumeration MUST be flagged as conditional upon the conjectural volume-completeness of the census at stage $k$.
    *   *Source:* Wakelin (2026).

**(ii) New Sub-Anchors Discovered:**
*   **Sub-anchor (`Catalog Edit`):** Register the 439,898 exceptional Dehn fillings and 1,849 simplest hyperbolic knot exteriors computed from the 10-tetrahedra census [cite: 1, 2]. These are exact integers derived in early 2026 and should act as zero-shot calibration targets for the Ergon battery. If an agent computes a different number of exceptional Dehn fillings for the 10-tet census, it is hallucinating.
*   **Sub-anchor (`Training-Corpus Filter`):** Implement a semantic filter to detect the collapse of the terms "orientable cusped," "closed," and "non-orientable" when associated with the integer "10" or "11" in the context of tetrahedra. The 150,730 count applies *strictly* to orientable cusped hyperbolic topologies [cite: 1, 2].

**(iii) Verification Queue Additions:**
*   Add Q. Ren's (April 2026) construction of infinite families of chirally cosmetic surgeries on asymmetric 1-cusped hyperbolic 3-manifolds (arXiv:2604.02672) to the verification queue [cite: 11]. Determine if these families map to the newly registered 10-tet and 11-tet knot exteriors.
*   Add T. Ito's "A non-torus positive two-bridge knot does not admit chirally cosmetic surgeries" (Journal of the Mathematical Society of Japan, 2026) to the queue to extract conditional bounds on chiral constraints [cite: 11].
*   Register the cutwidth bound $4\mathfrak{g}(M) - 2$ for Heegaard splittings (He et al., May 2024) [cite: 7] as a distinct Tier-F invariant, explicitly isolated from Matveev complexity and minimal ideal tetrahedra count.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWL540XfHud0rFcWBfTzR9e5CEk69bRuNscW232XTx57BJUq266MEfiUoWqRS9o9Xkq8P6azMpXaz-XHK9cNjb74J5z67SE5itblHl8O2l8CQCPpTtpzEZow==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1mTw7D2EZeo6vxhtCXksOLswtSc09IUakS-yf-WP4YK1y04EiO5R5NBoOuir-fO_KWOIQ1VId4Z5TLHgTsdFTc_M9GGJVdhZ3djRl4D2ELmseDnWm7A==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfpMX9iGh1rn75maX7kElie0x1iAljX3N7_ZA9fmzspRLXnHOZOr61KiZFf9Yzb8Ou7xKWjY5kcDsjMW1dfVKOR395I81ImUS-lSA-dAMPu46qC1P5vFa2nQ==)
4. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaMQX9YUL-Kx5fbSRH9_-15dnO9C01s9fWaUYmjxVlAqV2Prz9JvFshV3MjJ7shTnaRhlM4z3z4CU51ydLpL8ORlhNJqBIMdKysqQr3oJwfNixHUA8tqqrljBc0pzhQ464cDbmZ4TOnA==)
5. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFYJwGllbdd7xlS_qbkj53faBUoaCTuXCD4yhLMb20dh6O6LfYGYAXW_8l02r_Ov5UlW3NUSpodrj6K-fiHkCYPfkQ20uhQDkcrWdG9qXBFx4zylduTMQFvZ6pi0s=)
6. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhLhUllD5TKUZUYP3a4c52dcLA7m8dvwRY1L7EzdnxSB6MQKKuWO3-yIEUOgbhSaItAsDY4xhH-JquopPUD8tdsIPJCiyjHgxZizgpMyLIUlbygw_RwSl9ZfePt3I6Rgty85zsIY5WfQ==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHh67GNR3rCGKfzAjqpupFR_Vzo4jOb_UfeI9JSKzHvWB_ERJf6wPIIDqyx9fQSiIw12EtpPY8Rs8TBpnWtnM4ZK_kNzyRk6i-3kSkXA1-uNJLWUwFpAg==)
8. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9x0h7bbAL1FGSbBlDJOZc0eioRLgoR252vnCbsFujySv11iQxgjDjckO9uKFG0H23Ik_TedUGBEqQw3UQF7YIMLyoUMbxK8A-z3dErTs_A9yg6sFtxIzOjTMEOs1vxOIply7vviuk)
9. [softpedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCzxo6KIL_47Yay1kO8N-114Y7FwQKPoufJ4J90GTg4AENPOM1b096H2oIcGQpc4WLwgUGoyt80dZhecpXLAZpgMpBzHnas1gQgWaXXIYIaENA7LPcCDn6cB5zTERU9Q952KGUn3Xg33M30wUU_39sDEG9)
10. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGABcj3R8x9fZLn7uaKMGqeBB0reEb2obDquUf6tRUUAqKiipkd4NBtq1EQ2cz7AxRqfYmbeUZ8_zVWVf43pnCcpRRU0TQQY4q9dTrv7z63z24g3bEsOPLGYcjhjP-m-hVj-obYbA==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKjmTWU51ct98bGTAQkWj8tprBODeAzI-gg9OaRJHIiY17tL3RpdeQBDwjwlValOJbBaRxSfpldm_3H_ZvuN5YcajkiMxvGnI7K-34XoVwHDwm4Hrvag==)


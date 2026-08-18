# Prompt 13: DR-013 — Re-verify AA-002 ZAUNER_FALSE_ANCHOR against 2026 follow-on (AFK 2025)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdCS1lCYXJqWUVJdlYxTWtQM19EZG9BOBIXQktZQmFyallFSXZWMU1rUDNfRGRvQTg
**Elapsed:** 394s

---

# Verification Report: AA-002 ZAUNER_FALSE_ANCHOR

**Key Points:**
*   Zauner's conjecture remains **unconditionally open**; the heavily cited 2025 Appleby-Flammia-Kopp (AFK) result provides a conditional construction, not an unconditional proof.
*   The AFK 2025 construction strictly depends on **two distinct unproven coordinates**: the order-1 abelian Stark conjecture for real quadratic fields, and a special value identity for the Shintani–Faddeev modular cocycle (also known as the Twisted Convolution Conjecture).
*   Follow-on literature in 2026 demonstrates accurate tracking of this conditionality, indicating that while human researchers are successfully avoiding the false-anchor, automated parsing models and LLM summarizers exhibit a high risk of collapsing "constructive approach" into "unconditional proof."
*   Evidence leans toward the eventual validation of the AFK construction, given extensive numerical cross-validation in dimensions up to 100, but the foundational number-theoretic invariants remain unresolved. 

**Background:**
Symmetric Informationally Complete Positive Operator-Valued Measures (SIC-POVMs) are configurations of mathematically optimal lines in complex space, originally motivated by quantum measurement theory. In 1999, Gerhard Zauner conjectured that these structures exist in every dimension. Despite massive computational efforts, exact solutions were historically limited to low dimensions, making it a notorious open problem.

**Recent Developments:**
In 2025, a major breakthrough occurred when researchers linked the existence of these geometric structures to deep algebraic number theory. They provided an exact formula to generate them. However, the mathematical machinery powering their formula relies on unproven conjectures about real quadratic fields. Because the foundational theorems are not yet proven, the resulting proof of Zauner's conjecture remains strictly conditional. 

## (a) PRIMARY SOURCE CONFIRMATION

The primary source triggering this verification is the preprint by Marcus Appleby, Steven T. Flammia, and Gene S. Kopp (AFK), titled "A Constructive Approach to Zauner's Conjecture via the Stark Conjectures" [cite: 1, 2]. 

*   **Definitive Publication Date:** Submitted to arXiv on January 07, 2025 (v1), with a revision on March 17, 2025 (v2) [cite: 2].
*   **Publication Status:** **ANNOUNCED-NOT-PUBLISHED**. As of the latest 2026 catalog data, the manuscript is available as a 177-page preprint on arXiv (arXiv:2501.03970) and has not yet been logged as peer-reviewed or published in a definitive journal [cite: 2]. It has not been withdrawn.

The explicit theorem statement in the primary source confirms the conditionality of the result. AFK define an intermediate object termed a **ghost SIC**, which is constructed from the real multiplication values of the Shintani–Faddeev modular cocycle [cite: 1, 2]. The authors state:

> "We prove that our construction gives a valid SIC in every case assuming two conjectures: the order 1 abelian Stark conjecture for real quadratic fields and a special value identity for the Shintani–Faddeev modular cocycle." [cite: 1]

Furthermore, the authors specify the distinct mathematical roles of these two conjectures:
> "The former allows us to prove that the ghost and the SIC are Galois conjugate over an extension of $\mathbb{Q}(\sqrt{\Delta})$ where $\Delta = (d+1)(d-3)$, while the latter allows us to prove idempotency of the presumptive fiducial projector." [cite: 1]

**Coordinate Isolation (HARD-5):**
The AFK 2025 result requires precise coordinate tracking in the Prometheus substrate. It does not simply rely on "the Stark conjecture." It relies on:
1.  $Coord_1$: **Order-1 abelian Stark conjecture for real quadratic fields**.
2.  $Coord_2$: **Shintani–Faddeev special value identity** (alternatively registered as the **Twisted Convolution Conjecture**) [cite: 1, 3].
3.  $Coord_3$: **Weyl–Heisenberg covariant SICs** (not general SICs, distinguishing the Strong Zauner Conjecture from the weak form) [cite: 4, 5].
4.  $Coord_4$: **Ghost SICs** (a distinct invariant from the SIC itself, operating as a Galois conjugate) [cite: 1, 2].
5.  $Coord_5$: **Rank-r equichordal configurations ($r$-SICs)** (a distinct generalization decoupled from standard dimension $d$ lines) [cite: 1, 2].

*Actionable Delta:* The primary source explicitly qualifies its findings. Any registration of AFK 2025 must map to a `Conditional_Proof` node with dependency edges to both $Coord_1$ and $Coord_2$.

## (b) FOLLOW-ON WORK (2024-2026)

To assess the stability of the AFK 2025 result and check for conditionality erosion, we survey the 24-month window of follow-on literature, up to April 2026.

**1. Bandeira et al. (March 2026):**
In "Randomstrasse101: Open Problems of 2025" (arXiv:2603.29571, March 31, 2026), the authors catalog the state of Zauner's conjecture [cite: 6, 7]. They correctly parse the AFK 2025 result, stating:
> "There has been fascinating recent progress [AFK25]: a proposed construction (corresponding to an orbit of the Weyl–Heisenberg group acting on $\mathbb{C}^d$) has been conditionally proven to indeed be a SIC-POVM assuming a couple of conjectures in Number Theory... A unconditional proof of Zauner's Conjecture remains unavailable." [cite: 6, 8]
*Evaluation:* This confirms that human-curated math literature in early 2026 is holding the line on conditionality. The AFK result is treated as a conditional breakthrough, not a terminal resolution.

**2. Van Loo & Oggier (March 2026):**
In "On the Existence of Algebraic Equiangular Lines" (arXiv:2603.09128, March 10, 2026), the authors investigate real and complex equiangular lines [cite: 9, 10]. They cite AFK 2025 as formal motivation for shifting the search space from complex analysis to algebraic number theory:
> "Our main result in the complex case proves... that the existence of $d^2$ equiangular lines in $\mathbb{C}^d$ implies the existence of $d^2$ equiangular algebraic lines... providing a formal motivation for the study of complex equiangular lines using algebraic number theory for all dimensions." [cite: 10, 11]
*Evaluation:* Van Loo & Oggier provide an **unconditional reduction** (via Hilbert's Nullstellensatz) that any complex solution implies an algebraic solution. This operates as a parallel substrate input, validating the number-theoretic framing of AFK 2025 without claiming Zauner's conjecture is unconditionally solved.

**3. Kopp & Lagarias (April 2026 / 2024):**
In "Class number bounds" (April 21, 2026 revision) and "SICs and Orders" (December 2024), Kopp and Lagarias map SICs to the ideal class monoid of non-maximal quadratic orders [cite: 5, 12]. They rigorously separate the known numerical observations from proven facts, referring to the "folklore conjecture" of finiteness of Weyl-Heisenberg SICs and citing the AFK 2025 construction as an ongoing framework for dimensions $d > 3$ [cite: 4, 5].

**4. Kopp (May 2025 / Nov 2024):**
Gene S. Kopp's standalone paper, "The Shintani–Faddeev modular cocycle: Stark units from q-Pochhammer ratios" (arXiv:2411.06763, revised May 2025) [cite: 13, 14], provides the foundational unconditional mechanics for the Shintani-Faddeev cocycle. He proves an unconditional refinement of Shintani's Kronecker limit formula [cite: 14, 15]. However, this unconditional component does not unconditionally resolve the special value identity required for the fiducial projector in AFK 2025. 

**Anti-Gravitational-Well Correction:**
The dominant gravity well in the literature attempts to frame SIC-POVMs purely as an optimization problem in quantum information (e.g., framing them strictly alongside Mutually Unbiased Bases or numerical frame theory) [cite: 6, 16]. The substrate must actively resist this. The AFK 2025 and Kopp 2024/2026 papers establish a higher-weight alternative: **SICs are essentially a manifestation of Hilbert's 12th Problem (explicit class field theory) for real quadratic fields** [cite: 1, 17]. In the Prometheus substrate, `Hilbert_12th_RealQuadratic` must be weighted equal-or-higher to `Quantum_State_Tomography` in the local neighborhood of the Zauner node.

## (c) FALSE-FORM RECURRENCE

A critical function of the `AA-002 ZAUNER_FALSE_ANCHOR` is to prevent the substrate from ingesting secondary-source assertions that "Zauner's conjecture was proven in 2025." 

A review of the 2024-2026 literature reveals an environment where the false form is highly likely to be generated by automated parsers, even if rigorous authors avoid it. For example, the title of AFK 2025—"A Constructive Approach to Zauner's Conjecture via the Stark Conjectures"—often gets truncated or summarized in seminar abstracts. In a 2024 ICERM workshop ("Recent Progress on Optimal Point Distributions"), the abstract simply reads: "We describe work towards a construction of $d^2$ equiangular lines... A leading role is played by the Stark conjectures" [cite: 16]. 

Similarly, third-party databases and aggregation sites demonstrate linguistic drift. The *Emergent Mind* database lists "Zauner's Conjecture (existence of SIC-POVMs in all dimensions)" under a list of "Open Problems," but adjacent metadata points to the AFK paper as a terminal node [cite: 18, 19]. 

We find explicit textual evidence of human authors actively guarding against the false form, proving that the threat of misinterpretation exists. Bandeira et al. specifically write:
> "This shows that these conjectures imply Zauner's Conjecture. A unconditional proof of Zauner's Conjecture remains unavailable." [cite: 6]

If the risk of the false form were zero, Bandeira et al. would not have dedicated explicit manuscript space to warn readers that the unconditional proof remains unavailable. Therefore, `AA-002` is **not redundant**; it is actively necessary to shield the LLM training-corpus filters from gradient descent toward the false form. The LLM gradient will naturally attempt to simplify "conditionally proven on order-1 abelian Stark conjecture" into "proven by Appleby, Flammia, and Kopp."

## (d) RECOMMENDATION

Based on primary source extraction and the 24-month follow-on survey, the following actionable updates are required for the Prometheus substrate.

**1. Status of the Anti-Anchor:**
The true form of `AA-002 ZAUNER_FALSE_ANCHOR` is **correct as stated but requires refinement**. The current anchor likely states that AFK 2025 is conditional on "the Stark conjectures." This is computationally imprecise. 
*   **Actionable Edit:** Refine `AA-002` to explicitly list *both* mathematically distinct constraints. Zauner's conjecture is conditionally resolved if and only if **both** the order-1 abelian Stark conjecture for real quadratic fields AND the Twisted Convolution Conjecture (Shintani-Faddeev special value identity) are resolved.

**2. New Sub-Anchors and Primitive Registrations:**
*   **Register Primitive `SIC_Ghost_Conjugate`:** AFK 2025 introduces the "ghost SIC", which is constructed from the real multiplication values of the Shintani-Faddeev modular cocycle and is Galois conjugate to a SIC over $\mathbb{Q}(\sqrt{(d+1)(d-3)})$ [cite: 1, 2]. This is a fundamentally new object in the substrate and must not be collapsed into the standard SIC coordinate.
*   **Register Primitive `r-SIC_Equichordal`:** Rank-r generalizations (r-SICs) of maximal equichordal configurations must be registered as a distinct coordinate from standard dimension $d$ lines [cite: 1, 2].
*   **New Companion Anti-Anchor `AA-002.1`:** Define a new anti-anchor preventing the substrate from conflating Zauner's general conjecture (existence in all dimensions) with the Strong Zauner Conjecture (existence of Weyl-Heisenberg covariant SICs in all dimensions) [cite: 4, 5]. The AFK 2025 construction specifically targets Weyl-Heisenberg SICs.

**3. Work-Queue Entries for the Substrate:**
*   **Work-Queue Entry `WQ-773`:** Initiate an automated sweep of the training-corpus filters to flag any string matching `"AFK" + "Zauner" + "proved"` or `"Appleby" + "Zauner" + "solved"` and conditionally mask them unless the tokens `"conditionally"` or `"assuming"` are present in the immediate dependency parsing tree.
*   **Work-Queue Entry `WQ-774`:** Refresh the `RayClassFieldFiducial` and `StarkUnitWitness` Tier-E conditionality annotations. Update the dependency graph so that the idempotency of the fiducial projector specifically points to the Shintani-Faddeev modular cocycle identity [cite: 1], while the Galois conjugacy points to the order-1 abelian Stark conjecture [cite: 1].

**Summary Table of Substrate Coordinate Updates**

| Invariant/Coordinate | Substrate Status | Required Action |
| :--- | :--- | :--- |
| **Zauner's Conjecture** | Unconditionally Open | Maintain `AA-002` to prevent false positive proof registration. |
| **AFK 2025 Result** | Conditionally Proven | Update dependency tree to require $Coord_1$ and $Coord_2$. |
| $Coord_1$: **Order-1 Abelian Stark Conjecture** | Unproven | Link to Galois conjugacy property of the ghost SIC [cite: 1]. |
| $Coord_2$: **Twisted Convolution Conjecture** | Unproven | Link to idempotency property of the fiducial projector [cite: 1, 3]. |
| **Algebraic Equiangular Lines** | Unconditionally Proven | Register Van Loo & Oggier 2026 Nullstellensatz reduction [cite: 10, 11]. |

By implementing these structural edits, the Prometheus substrate will maintain absolute rigor against semantic drift, properly honoring the HARD-5 coordinate distinctness and the conditional boundary of the 2025/2026 breakthroughs in explicit class field theory and quantum designs.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4kLMzrDyRjoIy2KOxvvzEOTug9O41avKjq-TOCK_BVChIKB-PcqLKex-SWdfi0Ex5E6gF6Y18XPxRqbVy2vKp4ljmQi8Kh0DxPaXoFunkaBEHYLmP)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaDVMHvXLYT6En3LqpKpnMyJ2XeOrX628CK2mZDlbKSCDDq4sGtU5s4e6CMbsywskNthxW156G3j3lDsS4iMPGvjUPhleHvWrE3WuRJJvhk9ZMk7br)
3. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4RXDOW8tzhSkQlbU7Srep29UR0CxbHV0vfSqosZfI3ULwUQZ3-QZMYGulldpSgCOZrZZ-8omkjPq2lHWDp0g8nib4OLX5IMML_2SCoJsP6YEAF_QTQo5Vyjzj9a57ZGIGOgIUG1Tksn7hdTncpGAcI4P9S2sOolzXweLcB9C4Do5Ee3vdckelpe5Nxj9_)
4. [gskopp.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAMQdtSYmn-vVwtuNJ9kf9sk9bA3AF84Zg4w--ilPzHtU2W-UDaFtnAK1P7zY0i0KKasv90LIIPTyvIjD3900BjCBY8XcnIcGjxJMz5PIkzBNjUQkOG55O9RXJ8CFFgBJpP18KwdRag4kGIfY7vtGpVuvJ8yBdhY2ahf-hmHhK4vQ=)
5. [gskopp.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPPkyv8uk9SlCmrWbn8YH2JCu7v1lOacTLXw1hC7vfsFPNhKLJ36GsTpl370MWaPQlRpBbIjRTZtlINnxoE_CNu7nBrIMwiJrJCoE10Rd1jjEcg6096DGQCmaJrMxcg6vrLsKIy_kIl3Qqo_OvoErXh1-hlsQ3r_AWUNqg8mAMGqA=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5wtIYOypjE_2ZRnFyq2LghXW4Ainibijez-8Baj5osOynoWKd1sg0SctsSsVfDYHknEy3-Z6yWBSVJlc-kyFNngaUBk_ozzl_TsDbmmcF9vgjhO0aHc1Z)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh-Qa_hIV14t8R6KL24yh6AM7twN_VZdWgTZRQcHxHTPQvoP6txA8c4SYIIOmrxPW72N5U_YzSG0Xib6Zf5RtGXRi-f3fmdqID2s6O7KUACi5MZFte)
8. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERXPKW4kQpV2BKvi9kLpNmN2KORV7nnbZDnOUPkZbOXGeIFJz7bVXWXiMMC3FC09Gn6Yav1U-RHR45PANchAqG4XoUzTyI4tCAhirGCkFfv8qALSJkGaH1rPjLpEfpMsTzpDM4gvMO5aU_WqNkNokeKQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWewtld2vdTA0nAarnO8T5E4l00QFArnI5aP0jdAskb1dcVEWZ5-Il1scLUkfpLPGs0ZHdcOc3zy-kLNq2CK_LZfs9p6Nl1FcvZLNvCwJ-z7vEEKt4)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnLROSmC38oaj5pvhgwbOA0br01aq-zuyZfua_kZM_APNs0AIH5SHxEX6rh0ntdLeSgwWUBEqaN0e0Jk3o-tXP-DNrA0LWX-Lv7gHeDFo4YiHjCWof-dMD)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy4r9at1VgCTtUMsQliByKOScfxbiSfvIunXHZ6xqGGqYUFcIDpk1DzMXvoPKV1QLc-bHl8ZE1T2qNBgApIIj6vqbKzYPtVPfXAUz_2xpDAuHIMgvC)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwSfMTVUSs4c9yDf5MxTSKP_Uua6VdFtKeJr6xZBtFaMv7pvgpaG39uClXD1F2vch3ZuitonFO3twbB3HMQa7RIJp8vbcWqAx9U_Xu1RZyTXjEp-AHHcbe)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEY7BLI0XgA5pPENRgNJHxt6rbOB999WI2yM-85ZfrtGNZhdfSHUqNybTDXof-sKwStJzWMywgdEKr0fMe08AB83zSmPP3_L1X0bUPlYiXe-jpVZ5_g)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGC6X2i9DuaNfO2dallKWHinIJnpFbUrrIo-3G-SRK3Jyh9Sm8TEWrDRmopAcNT5kqw1qHgf65BRMc84Q9jn_ZxESNvn24VW-e920z3JSbKB4LzeBbQ)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkKb-0oRADBc6FbI3Xz7UehMkgGn-xkKEEGssBwL2NdmUmg6AJ7ftXmMVAMYPyTMPTc6XckbpZ91wLHNhhaOhtmj77e5xeRPZKUo1iryUMsG2ZkLVEfe2R)
16. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKisktD4iMKN-IuSnUd5RgK8CWYJo42sPnc8NhYTCVFlXbHktXXS1NG5L1pIk3bRMzUzaVayYZmx0QzPzv8FksvCjoA1sDX5z2ZvN_o8fgRhoCZksdlMxGl_VJVj-cCVbbp_cUkXY6oikn4LkfBr8=)
17. [caltech.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfzHzQPhT7w1QYFpN2KBHk73wcN6tbi1syJQjqJZgSIlyem-x-4qVgCjq8wzkGwfx7ISjdjRiOpDtx-jXzLs6KC2Zx2ZheNUbmCyfFf3WocxzbeRckXWhDq7tUFhEnNKlGbo_dhXegwgcagOnAeJvQspK6GIeM2pndtTrywYE=)
18. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhmH2qfpRAo04jAQrmUUqHgYQSc_40Yglzm7ChaSeFgYfxJBxWxdn6xC65o9eYD9oiiEWfM0yXY_I9Fs5g4E3DfBF185sojVc7ex5wa4jrRhIMVoX1oghJvn5uCk6SZclzpI7a0HE7Z8vvbdnu-SR2H8CRPnICJ_TamvDt6W7O64SmpuoXs_4yEAgiAd96kw==)
19. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgtUwsVCnrHQPxl28oBVq0VLhgqXNJOHBgxji3gDdX1ELzp9oogrZ965toaXf9ZBJGS4EayYLCS1rTNdL_9ufTC609jL20iHPrqIDJJgQ6NIDAqvy0z_OZH5jKCOeNX8UqR7W66b6d7E2hOD3mVncOHuTm-_KfGGrU4Axi8GPuBSTtD0IQTMbQAmyEzA==)


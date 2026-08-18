# Prompt 19: DR-036 — Survey RayClassFieldFiducial + StarkUnitWitness supporting lit (T#85 AFK 2025)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdKRW9FYXFfekU3bU1fUFVQMXZPUzhRSRIXSkVvRWFxX3pFN21NX1BVUDF2T1M4UUk
**Elapsed:** 638s

---

# Anti-Anchor Verification Report: RayClassFieldFiducial & StarkUnitWitness (T#85 AFK 2025)

**Key Points**
*   **Status of Zauner's Conjecture:** The Appleby-Flammia-Kopp (AFK) 2025 result is strictly **CONDITIONAL** and **ANNOUNCED-NOT-PUBLISHED**. It does not unconditionally prove Zauner's conjecture.
*   **Mathematical Coordinates:** The AFK construction relies on two distinct mathematical coordinates that must not be collapsed: (1) the *Order 1 abelian Stark conjecture* for real quadratic fields, and (2) a *special value identity for the Shintani–Faddeev modular cocycle*. 
*   **Substrate Action:** The `RayClassFieldFiducial` and `StarkUnitWitness` primitives must be registered as Tier-E (Conditional) rather than Tier-A (Unconditional). 
*   **Gravity Well Warning:** LLMs and automated abstractors exhibit a high-gradient gravity well toward dropping the "conditional" flag and asserting that AFK 2025 universally resolves Zauner's conjecture. Anti-anchor pins are required to enforce the conditional-vs-unconditional boundary.

**Context**
This verification processes the anti-anchor candidate targeting the Appleby, Flammia, and Kopp (AFK) 2025 preprint. The primary goal is to isolate the exact mathematical dependencies required for their putative construction of Weyl-Heisenberg SIC-POVMs (SICs) in arbitrary dimensions. Findings will directly route to catalog edits, anti-anchor pins, and the conditional flag schema for future Stark-dependent mathematical primitives. 

---

## (a) PRIMARY SOURCE CONFIRMATION

The primary source under verification is the preprint by Marcus Appleby, Steven T. Flammia, and Gene S. Kopp. 

**Primary Source:** Appleby, M., Flammia, S. T., & Kopp, G. S. "A Constructive Approach to Zauner's Conjecture via the Stark Conjectures." 
**Identifiers:** arXiv:2501.03970 [math.NT]. 
**Date of Record:** Version 1 submitted January 7, 2025; Version 2 submitted March 17, 2025 [cite: 1, 2].
**Publication Status:** **ANNOUNCED-NOT-PUBLISHED**. As of early 2026, the manuscript is listed as "Submitted for publication" and has not yet completed peer review [cite: 3]. 

**Theorem Statement and Conditional Boundaries:**
The authors construct a mathematical object termed a `Ghost SIC`, which is derived from the real multiplication values of the Shintani–Faddeev modular cocycle (a tuple of meromorphic functions indexed by a congruence subgroup of $\text{SL}_2(\mathbb{Z})$) [cite: 1, 2]. 

The primary source explicitly states the conditional nature of their result. The exact phrasing in the abstract and introduction must be registered into the training-corpus filters to prevent unconditional drift:
> "We prove that our construction gives a valid SIC in every case assuming two conjectures: the order 1 abelian Stark conjecture for real quadratic fields and a special value identity for the Shintani–Faddeev modular cocycle." [cite: 1, 2]

To maintain Distinct Coordinates (HARD-5 doctrine), the substrate must parse the exact roles of these two distinct unproven conjectures:
1.  **Coordinate 1 (Galois Conjugacy):** The *order 1 abelian Stark conjecture* allows the authors to prove that the `Ghost SIC` and the actual `SIC` are Galois conjugate over an extension of the real quadratic field $\mathbb{Q}(\sqrt{\Delta})$, where $\Delta = (d+1)(d-3)$ [cite: 1, 2, 4]. 
2.  **Coordinate 2 (Idempotency):** The *special value identity for the Shintani–Faddeev modular cocycle* is required to mathematically prove the idempotency of the presumptive fiducial projector [cite: 1, 2]. 

**Generalizations (Distinct Coordinates):**
The primary source also establishes coordinates for `r-SICs`. The substrate must not collapse 1-SICs (standard Zauner conjecture) with r-SICs. The paper provides similar conditional constructions for rank-$r$ generalizations known as maximal equichordal configurations of $r$-dimensional complex subspaces, valid for all $r, d$ such that $r(d-r)$ divides $(d^2-1)$ [cite: 1, 2]. 

**Actionable Substrate Input:** Register AFK 2025 as `CONDITIONAL-PROOF`. Create a rigid anti-anchor preventing the assertion of an unconditional proof of Zauner's conjecture based on arXiv:2501.03970.

---

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month window surrounding the release of AFK 2025 reveals a highly active research coordinate involving ray class fields, Stark units, and exact SIC constructions. The following primary sources supersede, refine, or critically cite the AFK 2025 result.

**1. Refinement of the Class Field Hypothesis (July 2024 - December 2024)**
*   **Source:** Kopp, G. S., & Lagarias, J. C. "SIC-POVMs and orders in real quadratic number fields." arXiv:2407.08048 [math.NT]. 
*   **Date:** Submitted July 2024, revised December 27, 2024 [cite: 5, 6]. **ANNOUNCED-NOT-PUBLISHED** (Submitted for publication [cite: 3]).
*   **Substrate relevance:** This work provides the exact classification scheme required by AFK 2025. It refines the 2016 "class field hypothesis" (by Appleby, Flammia, McConnell, and Yard) to predict the exact class field over $\mathbb{Q}(\sqrt{(d+1)(d-3)})$ generated by the ratios of vector entries for the equiangular lines defining a Weyl–Heisenberg SIC [cite: 5, 6]. This introduces a new distinct coordinate: the `over-order class field` associated with the SIC field $F_{vec}(S)$.

**2. Extension of Prime Dimension Constraints (August 2025)**
*   **Source:** Bengtsson, I., Grassl, M., & McConnell, G. "SIC-POVMs from Stark units: Dimensions $n^2+3=4p$, p prime." *Journal of Mathematical Physics*, 66(8), 082202.
*   **Date:** August 12, 2025 [cite: 7, 8]. **PEER-REVIEWED**.
*   **Substrate relevance:** This peer-reviewed paper extends previous Stark-unit algorithms (which were restricted to dimensions $d = n^2+3=p$, a prime) to dimensions $d = 4p$ [cite: 6, 7]. This represents a distinct architectural branch from the general AFK 2025 construction, focusing on exploiting special moduli for ray class fields to generate exact fiducials at extreme dimensions.

**3. Algorithmic Extraction to Exact Solutions (2025)**
*   **Source:** Grassl, M. "Proving Zauner's Conjecture: What is missing?" (Presentations / conference proceedings, e.g., Lakeside Quantum Dialogue, May 2026 [cite: 9]; and related 2025 documents [cite: 10]).
*   **Date:** 2025–2026.
*   **Substrate relevance:** Grassl explicitly demonstrates that numerical solutions generated from the AFK 2025 approach, as well as prior Stark unit approaches, can be algorithmically converted into exact fiducial vectors using permutation symmetries [cite: 10]. 

**4. External Verification of Conditionality (December 2025 - March 2026)**
*   **Source:** Bandeira, A. S., et al. "Randomstrasse101: Open Problems of 2025 / 2026" (Blog and preprints, e.g., arXiv:2603.29571).
*   **Date:** December 13, 2025 [cite: 11] and March 31, 2026 [cite: 12]. 
*   **Substrate relevance:** The Randomstrasse101 mathematical substrate correctly preserves the conditional boundary of AFK 2025. Bandeira notes: *"There has been fascinating recent progress (Appleby et al., 2025): a proposed construction... has been conditionally proven to indeed be a SIC-POVM assuming a couple of conjectures in Number Theory, examples of so-called Stark Conjectures. This shows that these conjectures imply Zauner's Conjecture. A unconditional proof of Zauner's Conjecture remains unavailable."* [cite: 11, 12]. This text serves as a verified positive-control for the anti-anchor.

**Flagged Premature Claims:** 
No peer-reviewed mathematical literature in the 2024-2026 window claims an unconditional proof of Zauner's conjecture. The discipline remains strictly aware of the dependency on Hilbert's 12th Problem and the Stark conjectures. However, automated systems and non-peer-reviewed aggregators exhibit severe false-form recurrence, detailed below.

---

## (c) FALSE-FORM RECURRENCE

The gravity well of LLMs is to collapse nuanced, conditional proofs into binary "solved/unsolved" states. Because AFK 2025 uses the phrase "A Constructive Approach to Zauner's Conjecture", the gradient toward asserting "Zauner's conjecture is proven" is extremely high. 

**Evidence of the Gravity Well in Recent Aggregators (2025-2026):**
A search of literature aggregators and AI-summarized literature review hubs from 2025 to 2026 demonstrates the exact failure mode the anti-anchor is designed to prevent:
*   An AI aggregator platform ("The Moonlight") processes AFK 2025 with the generated summary: *"AISolve Zauner's conjecture: A constructive breakthrough connecting quantum state geometry to deep number theory via Stark conjectures."* [cite: 13]. The absolute framing ("AISolve Zauner's conjecture") strips all conditionality.
*   Similarly, Wikipedia's SIC-POVM page (as of January 2026) lists AFK 2025 under the "Partial results" and "Zauner's conjecture" headers but pairs it with the statement: *"The proof for the existence of SIC-POVMs for arbitrary dimensions remains an open question... exact expressions for SIC sets have been found... and another that has been conjectured to work for all dimensions."* [cite: 14]. While Wikipedia maintains the open status of the problem, the injection of AFK 2025 into automated semantic networks frequently strips the word "conjectured to work."

**The Danger of Over-Collapsing Stark Conjectures:**
A secondary false-form recurrence is the collapse of the AFK 2025 dependencies purely into the "Stark conjectures." While the Stark conjectures are famous, the secondary dependency—the *Shintani–Faddeev modular cocycle identity*—is highly specific and mathematically distinct. 
*   In various summaries (e.g., [cite: 15]), the narrative collapses to: "According to the Stark conjectures, computing special values at s=0 of suitable Hecke L-functions permits recovering the units... Once found, one can rigorously test whether they satisfy suitable extra algebraic identities". 
*   However, AFK 2025 transforms these "extra algebraic identities" into a rigorous mathematical dependency on the *Shintani–Faddeev special value identity* [cite: 2]. Any semantic representation that attributes the AFK 2025 idempotency proof to the Stark conjecture alone is mathematically false. 

**Necessity of the Anti-Anchor:**
Because AI aggregators and non-specialist downstream consumers are already publishing phrases like "constructive breakthrough... solving Zauner's conjecture," the anti-anchor is critically needed. It is not redundant. The substrate must forcefully correct any node that attempts to register Zauner's conjecture as unconditionally solved by AFK 2025.

---

## (d) RECOMMENDATION

Based on primary-source verification and the tracking of 2024-2026 follow-on literature, the anti-anchor candidate requires specific parameterization before integration into the Prometheus substrate. 

**(i) Anti-Anchor Refinement:**
The anti-anchor's true form is **correct as stated but needs refinement** to prevent coordinate collapse.
*   **Current Candidate:** Survey `RayClassFieldFiducial` + `StarkUnitWitness` supporting lit (T#85 AFK 2025).
*   **Refined Operation:** The candidate must be inverted from a generic "supporting lit" pin into a `CONDITIONAL-DEPENDENCY-LOCK`. 
*   **Action:** Edit the substrate catalog to rigidly bind the `RayClassFieldFiducial` registration to two distinct parent nodes: `Order1_AbelianStarkConjecture` AND `ShintaniFaddeev_ModularityIdentity`. If an LLM attempts to traverse from AFK 2025 to an unconditional proof of Zauner, the substrate must trigger a hard rejection citing these two unproven parent nodes.

**(ii) Discovered Sub-Anchors and Companion Anti-Anchors:**
During verification, three distinct coordinates (HARD-5 doctrine) were identified that require immediate primitive registration to prevent semantic overlap:
1.  **Sub-Anchor 1:** `GhostSIC_Idempotency_Dependency`. This pin explicitly maps the mathematical property of projector idempotency in the AFK construction *strictly* to the Shintani–Faddeev modular cocycle, not the Stark units [cite: 1, 2].
2.  **Sub-Anchor 2:** `GhostSIC_Galois_Dependency`. This pin maps the Galois conjugacy of the ghost SIC and the true SIC *strictly* to the order 1 abelian Stark conjecture over $\mathbb{Q}(\sqrt{(d+1)(d-3)})$ [cite: 1, 2].
3.  **Companion Anti-Anchor:** `r-SIC_Equichordal_Boundary`. Do not allow the substrate to collapse 1-SICs with r-SICs. The AFK 2025 paper extends the Stark-unit construction conditionally to rank-$r$ generalizations for $r(d-r) \mid (d^2-1)$ [cite: 1, 2]. Register `r-SIC` as a distinct structural coordinate.

**(iii) Verification Queue Additions:**
To ensure the Tier-E (Conditional) registrations remain accurate over time, inject the following claims into the active work-queue:
*   **Work-queue entry 1:** Monitor Kopp and Lagarias (arXiv:2407.08048 / *Essential Number Theory* 2025) for unconditional breakthroughs regarding the refined class field hypothesis for over-orders [cite: 3, 16]. If the ray class group cardinality logic is unconditionally proven, update the dependency tree for $F_{vec}(S)$.
*   **Work-queue entry 2:** Monitor peer-reviewed outputs from the May 2026 "Lakeside Quantum Dialogue" (specifically M. Grassl's session "Proving Zauner's Conjecture: What is missing?") [cite: 9]. Catalog edits should reflect any new algebraic obstructions to the Stark unit extraction algorithm discussed at this venue.
*   **Work-queue entry 3:** Track the status of the "Twisted Convolution Conjecture" which is referenced internally within the proofs of AFK 2025 for Ghost existence [cite: 2]. Add `TwistedConvolutionConjecture` to the Tier-E pending primitive catalog.

**Final Substrate Directives:**
Execute Tier-E registration for `RayClassFieldFiducial` and `StarkUnitWitness`. Apply the `CONDITIONAL-PROOF` flag schema to the AFK 2025 node. Deploy the anti-gravitational-well filter to intercept and rewrite any generated text asserting that Zauner's Conjecture was unconditionally proven in 2025.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy9XEgRtEkDUqOBzNrOHuShvdu-lkb1BQgZmIeKn-jg9dAIzD76BNsJ6jIvQtm9hsycEq8OjT918Pgydtkjb6MEqLqqUSQjC1Kr4amTQANRlPi2bcT)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtv9kXx0FNWwiFxZa3RmuruawUEbI_fN9nY5NagyfytaqFkb7eebwdnTRqNoVjMxTcDfeBtYpwUsmcxcp1IxcY0t-BvxnlBCvLWXfNvkwU-8e2-m9V)
3. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6pIWpGGik-T5_9pR-z1d_cjevBGvf-4C0mJ1CM7JbObffWhhAOTqmZmZccF22-OMpGuGkMBieHlqzs8UOq2UU7kCo3t9ArroKd3aXSvFKyK15xRJJHXIvbZaT8trrVhf3ON0E5xI=)
4. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGA1wqIh-zoY4D4KW9LM8dtDTvLCVNNHTbvw0HkUy5Lz9-wmB2gqpYawS7R2aoAe3W9-Ur2Bc4seRSYv8sgfkhSX8eaeZ8pP0PU7H5HNnVUI8NpTBQg5o0to0wAo9pMfRLfQJ7IlQ=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx-JeMFrx7KZDuJYhILg_S07ePNaJI3Ui2NThlCfV5xu0xQL-i-JaDz2lFruzZocviWtGoSjLOi9gOG5ub2OsqMGOSoVU4KLnhKJczKBcQTNNZ_yRV)
6. [gskopp.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlciFCgd3yNSI-9weHwMeIZHnD6qYPhXvWa4riLDGpbPW4iE9mlz41tEfsI0EsNcozWUgVrx6xKsv4294M0pXh4SW5s9wS2_u7ikNkNKAOCK0urVyZfwPybA0USpXUpMn1eQH1fEvR0I2-nLvC_l0fAEK2qmsNTKKIE5AE572OdNg=)
7. [aip.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE19qOTX4jkHf1-0kliTzv2W50zmya4OuwZCTC3X40fdAiiAwKuJkjlOWEAxaSUDY2wpofllzyj-CrdMNpVX_OWQ8BzgkA6Jee-5EB4f_aL8vjMWx_Eyk9Rv0dYepsPeVL-GVSo7aJ98-kkG2L1pWhpcUL-cpobtDu98OxfMbOHqGKgOmOX740T6mRgUM-Ppo_4FcHr9qrpnFm0axsq)
8. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGEaJA0Xwqj46D-jLYXtGSB3ixGnVQZcScw17V2ZESpGMZKa0vx5yYKzVgd_SbnuFg34QMB6TARY15LdgKyOrTIA0OtqjmcivZOlmZmyse02hkEpLU48_J3a-x2iweIIP5_XBI-hZ3Trm2)
9. [jyu.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvmbYLfBZLc7uRo4s8Iyiahk69BM7W_dMAWtbE6KHhfD6TbOCKJJvdIYvV1XcTFtdoFV0zTQUG9nI5YZ26zlTcT-TJ268A8uLiuFUvp_5PFfzpVxjw68ePolBaIg-yYeJ_fzG_IZaYr2FpASC9JT4p)
10. [ticmeet.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGu6_QOwBUg2eMBfbmb6Qm35C4qZBYCztdDLIcP42LO9TtKWOJDokxLLZqiOmESzEw5OFm0C7IwVGDy26_7jZc1lAIGBR0KLXIRlCLme1d2kW8lUg8fXbu3CJnYWbMyTUJIGF8AhkOuBZbffgjqvOtl-I788Eg4gj6yO91mcmuSb9zU1jUtQs4Mz2ffV1Jt6e5Gug==)
11. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsmQU-ykPeOruzFdeRbnJuMvnWAM-XuDuMOtpdT69F-_uONINCIJOpWiwpoQrGlXxgtctBKFXXqPtKEWBb-vpSqK-XyOlqFoFlUVdBPn6Hl4noC8bopR73JPcdr2DSiSniomSNxIBT-g12fbXRLuwTXw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJITUcr0i-MIC7Cz6yAVvn_lgTyLovzle2FUcVu0G41bjt6BxyL1lGrVtmnXGgTcG0iYCZs_FeHnR7_SPR_TGEBBrG-aW4mXAEKSYTMdUo6WaWImqo45IW)
13. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsHzfsIvXVgrY8tYmlcZ0IkvqoivKx9N1-9EclzeGOTjnpgvK7fDh3M8EJmVB4aFO14fQtiLenj0TFp_zL5kT-OxMTMbn1CkC8kQaOaTvboVnVuFB6REeeM_05FsLrrNlkLa1zeHNPa5D46RzKF6aYP6u8hUZg7IFMJ_852ZcmUkeg_1-ZwRpzs_TewkEIbKP4zuVGBl6fB2I4DGe7S3K7pOY=)
14. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIyLTwimIzGm8yu4pq52fUWYEKMWOMImnLa_BAhRXNNg34EukQ4WwdN-FUTz60nCpr_URWt7keMiaN7NjpLnUMW5VQOPYX2bUprWpGDeJq47xJhlJw_uTnY1XE)
15. [utoronto.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgOSRQwhCk1Wt20EedMhTgu7gYn4kzdRBRJ_CGHtGvEdw3F5s4tpwejB5BuVczr9XWHEzumfWPq4k60uKSFxTCAasDj4EHLzqo9NbayX9WPciIw6qCMx_SS4fYxSzec89xjVPoSyfagsbwtmmzapUqPLaPmJEZMQiOW7SoqsJnqqN3QVDCL9HA)
16. [gskopp.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEN4C9vDcyZzaWJnuePF7fztIN0owoECQEYXD0mDlRs79W8zGmsEyCnwd3mKKtZekSIa5zv4cmdsKvL0Njt15TfZIwjlP6JqgZNvntCnLHS7zN7oFtnX-s2tHjmuCdYbWUEEu_YBR-KvTY7KnxZ-6ui0_7p7fVidBUeCE8fGiRcxKY=)


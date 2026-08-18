# Prompt 01: DR-001 — Verify AA-013 Strassen direct-sum R<=7 safe zone (Rupniewski 2024) [SUBSTRATE-SHAPED]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczeW9FYXZMekxZLW5fdU1QanNfejRBVRIXM3lvRWF2THpMWS1uX3VNUGpzX3o0QVU
**Elapsed:** 1061s

---

# ANTI-ANCHOR VERIFICATION REPORT: AA-013 (STRASSEN DIRECT-SUM SAFE ZONE)

**Key Points:**
*   **Coordinate Preservation:** The finding exclusively concerns **tensor rank** ($R$), not **border rank** ($\underline{R}$) or any other asymptotic invariant.
*   **Methodological Correction:** The proof does *not* rely on exhaustive computational search. It is an analytic proof grounded in algebraic geometry, specifically utilizing the Alexeev-Forbes-Tsimerman substitution method coupled with a "repletion and digestion" reduction [cite: 1].
*   **Field Dependency:** The safe zone bound strictly requires the base field to be the complex numbers ($k = \mathbb{C}$) [cite: 1]. 
*   **Substrate Routing:** The proposed downstream consumer (`BorderRankWitness`) exhibits a critical coordinate collapse and must be aggressively rerouted to a `TensorRankWitness` registry.

The following report details the verification of anti-anchor candidate AA-013 against the primary literature. The inquiry revolves around Volker Strassen's 1969/1973 rank additivity conjecture, which posits that the rank of two independent tensors in a direct sum equals the sum of their individual ranks. While Yaroslav Shitov famously disproved the unconditional general form of this conjecture in 2019, specific "safe zones" exist where the additivity invariant rigidly holds. This report investigates Filip Rupniewski's 2024 boundaries for this safe zone, deconstructs the false forms propagating through the literature, and issues actionable directives for the substrate.

---

## (a) PRIMARY SOURCE CONFIRMATION

The candidate proposes that Rupniewski's 2024 work established a safe zone for Strassen's direct-sum additivity conjecture for tensors of rank $\leq 7$ via exhaustive search. Investigation of the primary literature confirms the mathematical bound but fundamentally contradicts the proposed methodological mechanism (exhaustive search). 

**Primary Source Pin:**
*   **Author:** Filip Rupniewski
*   **Title:** "Strassen's rank additivity for small tensors, including tensors of rank less or equal 7"
*   **Publication:** *Linear Algebra and its Applications* (PEER-REVIEWED)
*   **Volume/Date:** Volume 698, October 2024 (First announced as arXiv:2209.11040, September 2022) [cite: 2, 3].

**Theorem Quote & Coordinate Isolation:**
The exact mathematical claim is isolated in Theorem 1.0.3 (iii) and Corollary 6.4.11 of the primary text. Rupniewski states:
> "If $k = \mathbb{C}$ and both tensors have ranks less or equal 7. In particular, $R(\mu_{2,2,2} \oplus \mu_{2,2,2}) = R(\mu_{2,2,2}) + R(\mu_{2,2,2})$, where $\mu_{2,2,2}$ denotes the $2 \times 2$ matrix multiplication tensor." [cite: 1]
> "Over the base field $\mathbb{C}$, if both tensors have ranks less or equal 7, then rank additivity holds." [cite: 1]

Crucially, the coordinate targeted here is **tensor rank** ($R$). This must not be conflated with **border rank** ($\underline{R}$), for which additivity fails significantly earlier (e.g., Schönhage's 1981 counterexamples for border rank).

**Methodological Refutation (Anti-Gravitational-Well Action):**
The candidate context states that the conjecture is "verified by exhaustive search." This represents a severe gravity-well hallucination, bleeding over from typical Boolean SAT-solver approaches used in small matrix multiplication algorithms (e.g., Heule et al.). 

Rupniewski's proof is strictly analytic and algebraic. It does *not* utilize exhaustive computational search. Instead, the proof is constructed through a precise geometric reduction pipeline:
1.  **Substitution Method:** It utilizes the Alexeev-Forbes-Tsimerman substitution method, which acts as a higher-dimensional analogue to Gaussian elimination. By distinguishing a slice of rank one and adding scalar multiples of it to other slices, the rank is decreased by exactly one [cite: 1, 4].
2.  **Repletion and Digestion:** Following earlier foundational work by Buczyński, Postinghel, and Rupniewski (2020), the proof uses a process called "repletion and digestion" [cite: 1, 5]. This process algebraically minimizes the decomposition by absorbing specific types of matrices. The 2024 work refines this to operate with respect to one distinguished rank-one matrix [cite: 1].
3.  **Proof by Contradiction:** The proof structure assumes that additivity fails, restricts the spaces to their repleted and digested versions, assumes conciseness, bounds the dimensions to $\leq 4$, and forces a geometric contradiction proving that rank additivity must hold [cite: 1].

Therefore, the candidate's characterization of the proof mechanics must be inverted prior to substrate registration.

---

## (b) FOLLOW-ON WORK (2024-2026)

To fully pin this invariant within the substrate, we survey the downstream propagation of Rupniewski's October 2024 definitive publication. Recent literature actively utilizes this safe zone boundary to contrast against asymptotic counterexamples.

**Borovik et al. (July 2025):** 
In a critical preprint (arXiv:2507.17890) titled "On the construction of a counterexample to Strassen's rank additivity conjecture," Borovik, Flavi, Pielasa, Shatsila, and Song revisit Shitov's 2019 disproof of the general Strassen conjecture [cite: 6]. They provide an explicit alternative proof of Shitov's dimension-counting argument. Within their survey of the boundary between additivity and non-additivity, they explicitly cite Rupniewski's 2024 *Linear Algebra and its Applications* paper as the definitive boundary for positive small-tensor cases [cite: 7]. Borovik et al. emphasize that finding explicit counterexamples for **tensor rank** remains highly complex due to dimensionality, thereby reinforcing the utility of Rupniewski's exact $R \leq 7$ analytic safe zone [cite: 7].

**Shitov (November 2024):**
Yaroslav Shitov himself released a preprint (ResearchGate, originally announced on viXra in 2023) titled "Higher rank substitutions for tensor decompositions I. Direct sum conjectures" [cite: 8]. Shitov expands upon the very same Alexeev-Forbes-Tsimerman substitution methods leveraged by Rupniewski. Shitov's work generalizes the embedding of a tensor into a larger linear space and replacing higher-rank slices with families of rank-one slices. Shitov explicitly acknowledges Rupniewski's boundary (citing it as proving equality for tensors of rank not exceeding six or seven, depending on the constraints) [cite: 8]. This directly anchors Rupniewski's methodology as fundamentally intertwined with the leading edge of non-additivity proofs.

**Blatter, Draisma, and Rupniewski (January 2024 / January 2025):**
Substrate mappings must also account for parallel coordinate investigations by Rupniewski and collaborators. In "Countably many asymptotic tensor ranks" (*Linear and Multilinear Algebra*, January 2025; earlier ITCS 2024), they investigate gaps in **asymptotic subrank** and **asymptotic slice rank** [cite: 9, 10]. They establish discreteness in these asymptotic invariants. This follow-on work highlights the necessity of the HARD-5 directive: the behavior of exact **tensor rank** in direct sums (which exhibits safe zones) operates under vastly different geometric constraints than asymptotic or amortized variants [cite: 9].

---

## (c) FALSE-FORM RECURRENCE

The substrate requires explicit enumeration of "gravity wells" where conventional literature or LLM heuristics collapse distinct invariants or methodologies. Three distinct false forms are currently actively recurring in the literature and algorithmic summarization models:

1.  **The Exhaustive Search Fallacy (Methodological Collapse):**
    Because the tensor rank of the $3 \times 3$ matrix multiplication tensor remains famously unknown (bounded between 19 and 23) and is frequently attacked via massive SAT solvers (e.g., Heule, Kauers, Seidl), automated systems natively associate any "small tensor rank bound" with computational exhaustion. The false form asserts: *"Rupniewski verified $R \leq 7$ additivity by checking all small tensors computationally."* This masks the actual geometric mechanism (repletion and digestion applied to slice decompositions) [cite: 1], depriving the substrate of transferable algebraic primitives.
2.  **The Field-Independence Fallacy (Field Collapse):**
    A common assumption in literature abstractions is that small-tensor invariants hold universally across fields. The false form asserts: *"Strassen's additivity holds for all tensors of rank $\leq 7$."* The true form mandates the condition $k = \mathbb{C}$ (the complex field) [cite: 1]. The geometric substitution method relies on properties of algebraic closure and dimension counting in complex projective varieties (secants of Segre varieties) that break down or require severe modification over $\mathbb{R}$ or finite fields $\mathbb{F}_q$.
3.  **The Border Rank / Tensor Rank Conflation (Coordinate Collapse):**
    Researchers routinely blur exact tensor rank ($R$) with border rank ($\underline{R}$). The false form asserts: *"Additivity holds for small tensors up to rank 7."* If interpreted as border rank, this is violently false. As demonstrated by Schönhage and later expanded in Bini's works, border rank fails additivity for very small tensors (e.g., $R(\mu_{2,1,3} \oplus \mu_{1,2,1}) = 7$ despite the individual border ranks summing differently) [cite: 5]. Rupniewski's 2024 theorem is strictly bound to **tensor rank** [cite: 1].

---

## (d) RECOMMENDATION

**Status:** The proposed anti-anchor true-form needs **REFINEMENT** to strip out the exhaustive search hallucination, firmly bind the base field constraint ($k=\mathbb{C}$), and explicitly isolate the tensor rank coordinate.

Furthermore, a **CATALOG EDIT** is strictly required. The user query specified the downstream consumer as `Techne v4.0 Wave 2 BorderRankWitness sub-cluster registration`. This is an illegal routing operation due to coordinate mismatch. The finding belongs in the `TensorRankWitness` sub-cluster. Sending it to `BorderRankWitness` will poison the substrate's asymptotic approximation logic.

**Refined True Form for Anti-Anchor AA-013:**
"Strassen's direct-sum additivity conjecture strictly holds for exact tensor rank R over the complex field C when both independent tensors satisfy R <= 7. The proof relies on the algebraic Alexeev-Forbes-Tsimerman substitution method with geometric repletion and digestion, not exhaustive computational search."

**Actionable Routing:**
1.  Emit `anti_anchor` block `AA-013` registering the refined true form against the exhaustive search false form.
2.  Emit `catalog_edit` block `T#AA013-ROUTING` modifying the work-queue target from `BorderRankWitness` to `TensorRankWitness`.

---

## SUBSTRATE BLOCK APPENDIX (REQUIRED)

```yaml
---
_schema_version: "1.0.0"
substrate_type: anti_anchor
id: AA-013
name: STRASSEN_ADDITIVITY_COMPLEX_TENSOR_RANK_BOUND_SEVEN
false_form: "Strassen's direct-sum additivity conjecture for small tensors (R <= 7) is verified via exhaustive computational search, applying universally across fields and rank invariants."
true_form: "Strassen's direct-sum additivity conjecture strictly holds for exact tensor rank R over the complex field C when both independent tensors satisfy R <= 7. The proof relies on the algebraic Alexeev-Forbes-Tsimerman substitution method with geometric repletion and digestion, not exhaustive computational search."
citation: "DOI:10.1016/j.laa.2024.06.016"
citation_status: peer_reviewed
risk_tier: high
source_report: anti_anchor_verification_AA013.md
verified_against_primary: true
---
_schema_version: "1.0.0"
substrate_type: catalog_edit
entry_id: T#AA013-ROUTING
field: downstream_consumer
before: "Techne v4.0 Wave 2 BorderRankWitness sub-cluster registration (SmallTensorAdditivitySafeZone Tier-B sub-type)"
after: "Techne v4.0 Wave 2 TensorRankWitness sub-cluster registration (SmallTensorAdditivitySafeZone Tier-B sub-type)"
reason: "HARD-5 Coordinate Violation. The candidate result strictly dictates tensor rank R bounds, not border rank \underline{R}. Additivity of border rank fails at lower thresholds and cannot inherit this safe zone. Routing destination corrected to preserve coordinate hygiene."
citation: "DOI:10.1016/j.laa.2024.06.016"
reviewer_action: replace
```

**Sources:**
1. [Link](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5GR1sUSrGzXoRJkPVkQZ4yDbY3hlUqt_LmparZNz8c6zgqgeAZNlXBsEEHmBz_m-DyjrzOnRwSO4p2UIEKvSbN1XCXqT_AuxM-GzBVPMLqYq9S2sizA==)
2. [unibe.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEnZyBjk0Z0wEVpayGhlRtpA0F-OucbZ6pnEbkrqR7uMi7LVBzSKWcFISEX38OTYXIGN7yYBATqy8Rf5JAXvc0VqbRbe9450If_nsNtwzAKvniXizv0s-UqSxwYU-bbidA1_Ws6oTWhLvYu_GjfYHqXIFNg14T5MQoHhdF53mK19-WuJGzPIqhulgEz18=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvF5k9JK0BWD9XMnyEiz3mwDIN_RbPEbyFJlu8UnJHNNzOn38oEPDAtB3v5I55KMuC6wDLrTLWWS6DYWlkfkHRXxIAPE-JXIXwWwaBARRusd9hnQ5BBA==)
4. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVFOWQGvA8K9VG6ZBMo6_kDpIQTPrl2L7LL9oURQszSUJohO38mZpbmEjZaqluFE4uOpH6_wdd_GA9xg0S2t6m-h9Wgt1jI0Ym6g0TyOBW_1a7FQqY)
5. [lboro.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESWN9AyF2RklSTk0QVy6z320Nmy7UkLAp_uKSVL__zrPWBt2sLtHXeXerHk_IAmw6yg95aB2mJ1aVLhCk50Iadh7KbrnGgma0cUI32yJOiVFYCC1u1lSxTnPG1zc98gON_Refs1kM3CAx8du-MejxLw104RfHkAXBymtTqq4CpIoPXMP-Wvk_zyuEaQ8adQhf20MfbqTf2OkwDaBOJ0dx6LnwX-VJ5F-hv6XI29zCesrlZHwq7QkmfVk8E6RBYwp3jL_A1hptXRg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGV1BaroiAJOza_S93GtdP4EKD_e5ZLlTIB9oca4yxRZOL5mnTDhx49NUNkNY0Ep1vKqDG1b8HqHM5BH1otBfImG0QGfbdX3We5TXjRiwqVD4vX9XXQ4A==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7ydHpQX9rip7fSv9pCd5i95Bo_jeFsX0IG8jqeUR6cEtDqk4VjJYiIAYDTlY_GZZfjydAPDwu8mzcGs1XY4qqru0AccRivyebGfLOHkymlV8CzTyG8g==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEl91PFAD7ZW77yQdRIVjOZ6qxUXnhQ_4OeToCsUvVqcFITCoQGQ_sFayXgbDNsxpjmFe8VUFoP6VzB9irqu-Pbfovw9aNvZBUyF_uC6yBRkdn4fs1_bu_yV1LIyF0knnx-x4XayC_bP29l7GssDPw45VcgI__WVHdTdJNuLNInY_KeYM4niWGYy8x4oFvKq4YtdvhM07RSyL0g5cn39dPogGfLqTvbuiEI35EJPB1RLRG5kg84)
9. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIydFqBBYOx0zEqWlKVDip5-QiVdnycnnM9KlI1f5O90uw1X68vKWxd9_Ys38I98gqay-P8HgPAuXmgLI10Kp31LDQq9B8XoUlLL6fdNWUPD_4SCrbfCYVL_PaD0Sdirs-0ku306S2kyLAN_ntBFAZve-lzqLwkYiRV2A3LA==)
10. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHu1xjKCI81G_BbfTG4oj6XlPY2r5CmjuiMzJnFa2c7zlAOmfuUGgMUTV7UeWDfrGkVjlJLczECHIsaY1efzCpTbUKQLtTbXBrAnKPyaYfRt2PqiGNQK3Kz13j0q8uKkaGQqfthwRa9XvWSxsQbR-swW_iqmhKOQ==)


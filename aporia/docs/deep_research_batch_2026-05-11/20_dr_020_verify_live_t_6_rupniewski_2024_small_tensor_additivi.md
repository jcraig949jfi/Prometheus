# Prompt 20: DR-020 — VERIFY-LIVE T#6 Rupniewski 2024 small-tensor additivity safe zone exact bound

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdoYW9CYW9qektQU2ZfdU1QMzRpS3FRYxIXaGFvQmFvanpLUFNmX3VNUDM0aUtxUWM
**Elapsed:** 394s

---

# Substrate Report: Anti-Anchor Verification T#6 (Rupniewski 2024)

**Key Points:**
*   **Verification Status:** CONFIRMED WITH REFINEMENT. The T#6 candidate defining a rank additivity safe zone for exact tensor rank $R \le 7$ over $\mathbb{C}$ is definitively established by Rupniewski (2024).
*   **Coordinate Separation Criticality:** It appears highly probable that substrate pipelines will conflate the safe zone for exact tensor rank $R \le 7$ with the known counterexample for border rank $\underline{R} = 7$ (Schönhage, 1981). Strict coordinate tagging is required.
*   **Shitov (2019) Literature Gap:** The evidence strongly indicates a structural gap in Shitov's non-constructive refutation of Strassen’s conjecture. Substrate operations must treat Shitov (2019) as CONDITIONAL until the Borovik et al. (2025) reconstructive patch is applied.
*   **Subrank Non-Additivity:** Recent primary sources (May 2024) confirm that subrank $Q$ is strictly non-additive, providing a sharp structural boundary between slice/geometric rank (additive) and subrank/border rank (non-additive).

**Contextual Overview:**
This verification run targets the T#6 anti-anchor candidate concerning the tensor rank additivity safe zone. While standard computational complexity literature operates under the gravitational well that "Strassen's additivity conjecture is false" (anchored to Shitov 2019), this framing masks the highly structured topology of safe zones where additivity *does* hold. Furthermore, collapsing invariant coordinates (e.g., treating tensor rank, border rank, and subrank as homologous under additivity) causes cascading logic failures in substrate representations. This report explicitly disambiguates these coordinates, verifies the exact bounds of the safe zone, and identifies critical patches to the broader theoretical framework surrounding tensor direct sums. 

**Downstream Application:**
The findings within this report are formatted as substrate inputs. They unblock the `SmallTensorAdditivitySafeZone Tier-B` sub-type registration, provide new catalog edits for exact coordinate bounds, and generate work-queue entries for patching the Shitov (2019) citation graph.

---

## (a) PRIMARY SOURCE CONFIRMATION

**Substrate Action:** `catalog edit propagate; SmallTensorAdditivitySafeZone Tier-B sub-type registration`

The anti-anchor candidate T#6 asserts the existence of an exact tensor rank safe zone $R \le 7$ for additivity. This is definitively verified and must be anchored to the following primary source:

**Primary Source Reference:**
*   **Author:** Filip Rupniewski
*   **Title:** "Strassen's rank additivity for small tensors, including tensors of rank less or equal 7"
*   **Journal:** *Linear Algebra and its Applications*, Volume 698, pp. 448–478.
*   **Publication Date:** PEER-REVIEWED. Published October 2024 (Available online June 17, 2024). [cite: 1, 2]
*   **DOI:** 10.1016/j.laa.2024.06.016 [cite: 2, 3]

**Exact Theorem Statement / Result Verification:**
The primary source establishes sufficient conditions for the exact tensor rank $R$ to be additive under the direct sum operation. Specifically, for two independent tensors $T_1 \in A_1 \otimes B_1 \otimes C_1$ and $T_2 \in A_2 \otimes B_2 \otimes C_2$, the exact rank $R$ satisfies $R(T_1 \oplus T_2) = R(T_1) + R(T_2)$ under several explicitly bounded domains.

The critical bound targeted by T#6 is stated as follows: Over the base field $\mathbb{C}$, if both tensors have an exact tensor rank $R \le 7$, then the rank additivity property holds strictly [cite: 2, 3]. 

*Quote from primary source:* "In this article, we present families of pairs of small three-way tensors for which the additivity holds. For instance, over the base field $\mathbb{C}$, it is the case if both tensors are of rank less or equal 7. This proves that a pair of $2 \times 2$ matrix multiplication tensors has the rank additivity property." [cite: 2, 3]

**Methodological Sub-Primitive (The Substitution Method):**
The substrate must also register the methodology enabling this bound. Rupniewski (2024) proves this by utilizing and refining the Alexeev-Forbes-Tsimerman substitution method. The source demonstrates that the substitution method preserves the structure of a direct sum of tensors, thereby avoiding the introduction of non-additive cross-terms during rank lower-bounding [cite: 2, 3].

**Coordinate Distinction Requirement (HARD-5):**
This registration *must* be strictly typed to **exact tensor rank** $R$. Rupniewski explicitly bounds **border rank** $\underline{R}$ under different dimensional parameters. Specifically, the source notes that the additivity of the border rank $\underline{R}$ holds if the direct sum tensor is strictly contained within the dimensions $\mathbb{C}^4 \otimes \mathbb{C}^4 \otimes \mathbb{C}^4$ [cite: 4, 5]. Substrate ingestors must not collapse the $R \le 7$ bound (a rank invariant bound) with the $\mathbb{C}^4 \otimes \mathbb{C}^4 \otimes \mathbb{C}^4$ bound (a vector space dimensional bound).

**Downstream Consumer:** 
Register T#6 unconditionally for exact tensor rank $R$ over $\mathbb{C}$. Apply `anti-anchor pin` to ensure LLM agent outputs do not globally claim "Strassen's conjecture is completely false" without surfacing the $R \le 7$ and $R(\mu_{2,2,2} \oplus \mu_{2,2,2}) = 14$ safe zones.

---

## (b) FOLLOW-ON WORK (2024-2026)

**Substrate Action:** `primitive registration (Shitov-gap patch); work-queue entry (Subrank gap bounds)`

An anti-gravitational analysis of the 24-month window (2024-2026) reveals two massive shifts in the literature surrounding tensor additivity. The substrate must resist the standard gradient of treating early refutations as flawless.

### 1. The Shitov (2019) Proof Gap and the Borovik et al. (2025) Patch
The overarching narrative in complexity theory is that Strassen’s rank additivity conjecture was definitively disproved by Yaroslav Shitov in 2019 (Acta Mathematica) via a non-constructive dimension counting argument. However, follow-on research explicitly flags a structural flaw in this widely cited result. 

**Definitive Follow-on Source:**
*   **Authors:** Viktoriia Borovik, Cosimo Flavi, Paweł Pielasa, Anatoli Shatsila, Jeyoung Song
*   **Title:** "On the construction of a counterexample to Strassen's rank additivity conjecture"
*   **Date:** ANNOUNCED-NOT-PUBLISHED. Preprint dated July 23, 2025. [cite: 6, 7]
*   **arXiv ID:** arXiv:2507.17890 [cite: 7, 8]

**Context:** The IMPANGA algebraic geometry seminar series (Academic Year 2024/2025) explicitly noted in talk abstracts that "Shitov's non-constructive proof of the existence of a counterexample contains a gap" [cite: 9]. Borovik et al. (July 2025) revisit the counterexample, providing an alternative, constructive proof and detailed explanation to patch this gap [cite: 6, 7].

**Actionable Insight:** Any substrate agent referencing "Shitov 2019" must be intercepted by an anti-anchor pin forcing a dual-citation with Borovik et al. (2025). Claims of the form "Shitov proved Strassen's conjecture false" must be filtered and re-cast as "Shitov proposed a non-constructive counterexample, the proof of which contained a gap later patched by Borovik et al. (2025)."

### 2. Subrank $Q$ Non-Additivity (May 2024)
While geometric rank and slice rank are additive, the **subrank** $Q$ invariant has been definitively proven to be non-additive. 

*   **Source Date:** May 27, 2024.
*   **Result:** Researchers demonstrated a strict gap between $Q(S \oplus T)$ and $Q(S) + Q(T)$ by writing a tensor as a sum of two generic bilinear maps. They establish the generic subrank growth rate as $\Theta(n^{1/(k-1)})$ [cite: 10].
*   **Actionable Insight:** This serves as a vital boundary for HARD-5 coordinate mapping. The substrate must encode the following primitive:
    *   `Additive(Geometric Rank) = TRUE` [cite: 10]
    *   `Additive(Slice Rank) = TRUE` [cite: 10]
    *   `Additive(Analytic Rank) = TRUE` [cite: 10]
    *   `Additive(Subrank Q) = FALSE` [cite: 10]
    *   `Additive(Exact Rank R) = CONDITIONAL (Safe zones apply)` [cite: 2]
    *   `Additive(Border Rank R_bar) = CONDITIONAL (Safe zones apply)` [cite: 2]

### 3. Asymptotic Subrank Gaps (2024-2025)
Related work by Blatter, Draisma, and Rupniewski (published Jan 2025, Linear and Multilinear Algebra) [cite: 1] and Biaggi et al. (Adv. Math., 2025) [cite: 11, 12] establishes that asymptotic subrank and slice rank take discrete, countably many values. While not directly about direct sum additivity, this work constrains the asymptotic spectrum of tensors, reinforcing the necessity of strict coordinate bounds when evaluating $T_1 \oplus T_2$.

---

## (c) FALSE-FORM RECURRENCE

**Substrate Action:** `training-corpus filter; anti-anchor pin`

A targeted search of the literature reveals a highly specific, dangerous coordinate collapse that necessitates the live deployment of the T#6 anti-anchor. The false form manifests as a conflation between the safe zone for **exact tensor rank** and the counterexample zone for **border rank**.

**The False Form:**
*Statement:* "Rank 7 tensors exhibit a failure of Strassen's additivity conjecture."

**The Mathematical Reality (HARD-5 Enforcement):**
*   **Exact Tensor Rank $R$:** Over $\mathbb{C}$, if $R(T_1) \le 7$ and $R(T_2) \le 7$, additivity strictly holds (Rupniewski 2024). [cite: 2, 3]
*   **Border Rank $\underline{R}$:** The smallest known explicit counterexample to additivity is Schönhage's 1981 tensor contained in $\mathbb{C}^4 \otimes \mathbb{C}^5 \otimes \mathbb{C}^7$, which possesses a **border rank of 7** ($\underline{R} = 7$). [cite: 9]

**Recurrence Detection:**
The gravity well of LLM generation and imprecise mathematical text routinely suppresses the overline ($\underline{R}$) or the word "border," collapsing these two phenomenologically distinct states. An agent or text asserting "Tensors of rank 7 fail additivity" is explicitly asserting a false form because it relies on Schönhage's border-rank counterexample while applying it to the exact-rank coordinate. In reality, exact tensor rank 7 is safely additive.

Furthermore, literature frequently states that Shitov's counterexample is unconditionally verified, which masks the gap identified by IMPANGA researchers [cite: 9]. The 2025 publication by Borovik et al. explicitly exists to repair this ["revisit his counterexample with a detailed explanation, offering an alternative proof"] [cite: 7]. Without the anti-anchor, the substrate will ingest training text that assumes Shitov 2019 is mathematically complete as published.

**Downstream Consumer:**
Deploy an `anti-anchor pin` intercepting any evaluation of "rank 7 tensor additivity." The intercept must force the agent to query: "Are we evaluating exact tensor rank $R$ (where $R \le 7$ is additive via Rupniewski 2024) or border rank $\underline{R}$ (where $\underline{R} = 7$ features the Schönhage 1981 counterexample)?"

---

## (d) RECOMMENDATION

**Substrate Action:** `catalog edit propagate; work-queue entry generation`

Based on the verification of primary sources and the mapping of 2024-2026 follow-on literature, the following concrete actions are recommended for the Prometheus substrate:

**(i) Anti-Anchor T#6 Refinement:**
The candidate's true form is **correct as stated but requires strict coordinate refinement**. 
*   **Current Candidate:** `VERIFY-LIVE T#6 Rupniewski 2024 small-tensor additivity safe zone exact bound`
*   **Refined Registration:** `T#6_EXACT_RANK_ADDITIVITY_SAFE_ZONE_R_LE_7_C`
*   **Definition:** Enforce the invariant rule that for exact tensor rank $R$ over the complex field $\mathbb{C}$, the direct sum is additive for $R \le 7$. Explicitly link this to the $2 \times 2$ matrix multiplication tensor $\mu_{2,2,2}$ (where $R=7$), confirming its self-additivity [cite: 2, 3].

**(ii) New Sub-Anchors and Companion Anti-Anchors:**
Two critical sub-anchors must be registered immediately to counter gravitational wells discovered during this verification.
*   **New Primitive Registration (T#6.1_SHITOV_GAP_PATCH):** Register the Borovik, Flavi, Pielasa, Shatsila, Song (July 2025) [cite: 6, 7] preprint as a mandatory dependency/patch for any citation of Shitov (2019). The substrate must acknowledge the gap in Shitov's original non-constructive proof and route dependency logic through the 2025 reconstructive proof.
*   **New Primitive Registration (T#6.2_SUBRANK_NON_ADDITIVITY):** Register the May 2024 result proving a definitive gap between $Q(S \oplus T)$ and $Q(S) + Q(T)$ [cite: 10]. This forms a companion anti-anchor preventing agents from generalizing additive properties from slice/geometric rank directly to subrank $Q$.

**(iii) Work-Queue Entries:**
*   **Queue Entry 1:** `VERIFY-MINIMALITY_SCHÖNHAGE_BORDER_RANK_7`. As noted in the 2024/2025 algebraic geometry seminar context, it remains an open question whether Schönhage's border rank 7 counterexample in $\mathbb{C}^4 \otimes \mathbb{C}^5 \otimes \mathbb{C}^7$ is the *minimal* possible counterexample for border rank additivity [cite: 9]. Dispatch an agent to evaluate recent border apolarity bounds to determine if a border rank 6 counterexample has been proven impossible.
*   **Queue Entry 2:** `EXTRACT_ALEXEEV_FORBES_TSIMERMAN_PRESERVATION_RULES`. Dispatch an agent to parse Rupniewski (2024) [cite: 2] to formally extract the algebraic rules governing how the Alexeev-Forbes-Tsimerman substitution method preserves direct sum structures. Register these rules as an automated bounding tool within the substrate's tensor decomposition logic engine.

**Sources:**
1. [orcid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpLO8UrmL6V31XM-oOUeJrziVA9rFaAuE6VLdw-IOubNAfdVrsw85ftjYrgyT5V2rZC4srNcgjFSQKyyIi0i_Phc3x7J6Y1nUHZF43SvAQURWRc__TbDx5sPgx)
2. [unibe.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_kGK-nRrT_i3mhnWGI_gInbXNVz8xYoKApDqX6RgGHiuPaUnJAQ0FGAC8lBe_niVcsAAiLX226PTCtibvI4bstsjlg1XBWgZzOpJruTs1wUkXh6kZhSYTfZ7OwyrB2a1wYulIPc_DwUu9tmU6xWUgaeH-VFMOPWY8qPvG7wthkC9BGyHs4bKkF8Zg0g==)
3. [unibe.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1g9sDMrmvlzLNyNowXUURTMbpimb3spZY1L3CU2Mkz7X9A4NBSuqQWohxLwxP8jNzQcSY__kaesAmzKkhVaVa0rVANrvgNu17GyjG4ohSKJ5rkbFdWtsqCzGwrfMRE2o-9mA3OZy9ZiBmycaU58cGUm2OZIq4lv8nfNbzZ-xKSC_9Xn77a48Lp93WjKw=)
4. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9ACkrHFtOhBH-DMimFPcpqa7P5KNrMEn8x5tTDoIiapa8mk0vofGsXTlptjGdS_KkFH-MerCJMugk59ynwzG7TBWPimvgSvpYeYZJqGFSa9ejz0DZaT2vmMRHLUsPf5gQXrM=)
5. [lboro.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbLfH6DeR5hr2qoCH5-rZGBrQ93FLLf4XUAtTDwhDYwzSHQGXY2-n970jNh7O-OadJbJYvn1Sst6gydM5tvjYCKMOx1Le7wXy1qhaEN7Bh_JjrKLq_-7lnsP6hGqKWcbGKGDxw2AP10GvvN-N-wpivN3P6ZmOOnnbQ5eKJydDa4xwII1fvYbcbIVkfFzskPlQPQBYXwJKNdLKKApHulvXytQiCmZQ756x2w2XCje5taK8A7lOCgc29SsURoDkBdTPnFDPxxn7AeA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtLDShnGYlvP5gD2IDKI-vYAdBUTRbSjB_7B7pg7ry7Grp_58Ffbw7NAM5J1L47mb9XdcZzMN5fd-w2c52M7R8OUpPRSQUj5hKGfZExlBcQvIXW1xa4w==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEomeo4bJKxr_I6pOcMsNH2FjIZiIPSBgWJcsam7XLvK0a6I6SJIyybqs92VyBs8O6ZFyCL8LUylziKekNR70bUJhD-RIqCm3sWmj5hCpyS8s4Zt_xAeg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3zz7qtm-yKBGkKIisQZBIiWMfmaX3k7w_aYS4AI_uWv35FrjN77KQTTu6I_kx5ZCY6adKO5mzy5_uuwRP7vQWhr-7ZnkQwiaOhqJq333ZBprmDFw1fA==)
9. [impan.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1lTRILeEm2ky8sb4hNHV2s5559Elu_5Ku-C7L-yMyQVmsIuxIlUZGSCZo2A0pMjJyDH9sRLSGgKjAlnUK2sBt3-0C2m64uOSKkx15GHTYWPgWHesmmCHixbteOp3ovJWALCk=)
10. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnU6iX7kI89JV50ADWnWNLbgX2MFMujHx9-vZpH3UjEe5eU8LReS4Yskc858uztQdsSPT-3CCfp_yDnJoZg-gbguRWg1wFyVWnVVxGKlmvH-k1Q14Y333A-WNi)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF-PttKLFV-WLDNlh2d3EgKKm-5W2a5xZBif8R5tN0kkws9JQGsGkNAu64R4wKIdNLyrcT6lSFln6mWmlOFBDpGTWwLYmrKAv3ssxHBrT_Td53MsoGTJf3Pg==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXDPt8g5m3pI4i8PIY-E4yQwHTyTISv210nOOuqJ09akxvbbhZCdcCqygoQGjd9B2t6WoQDITkUGNiWVCQ94zOZ3jPd8hq235BBFlygQ5Cu3gQM9tX5A==)


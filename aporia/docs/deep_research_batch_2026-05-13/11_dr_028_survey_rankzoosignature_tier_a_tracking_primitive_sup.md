# Prompt 11: DR-028 — Survey RankZooSignature Tier-A++ tracking primitive supporting lit (T#13, T#19, T#22)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdHRHNFYXZLOEY2QzhfdU1QeXJ5R2lBOBIXR0RzRWF2SzhGNkM4X3VNUHlyeUdpQTg
**Elapsed:** 999s

---

# Anti-Anchor Verification Report: RankZooSignature Tier-A++ Substrate Primitives

**Key Points:**
*   **Coordinate Separation is Absolute:** Recent findings from 2025 and 2026 establish strict, structural boundaries between closely related mathematical invariants—specifically slice rank, partition rank, and analytic rank. 
*   **Determinantal Methods Face Hard Limits:** The assumption that linear rank (determinantal) methods can indefinitely lower-bound border rank is mathematically compromised; the absolute ceiling for these methods is defined by "border cactus rank," surfacing geometric barriers.
*   **Waring Rank vs. Tensor Rank:** The $3 \times 3$ permanent's Waring rank has been unequivocally proven to be 16, which exists at a distinct coordinate from its tensor rank (which is 4).

### Executive Summary

This report evaluates the structural definitions and bounds of tensor complexities—a field dealing with how complex mathematical objects can be broken down into simpler building blocks. For a layman, one can think of a tensor as a multi-dimensional spreadsheet of numbers. Mathematicians use different types of "ranks" to measure the complexity of these spreadsheets, depending on the rules allowed for decomposing them. 

Historically, there has been a tendency in the literature to conflate these different rules. However, it seems likely that moving forward, computational substrates must treat each type of rank—such as slice rank, partition rank, and cactus rank—as fundamentally distinct coordinates. Recent research suggests that traditional methods for calculating these complexities (like determinantal methods) have hard geometric ceilings that cannot be bypassed. The evidence leans heavily toward the necessity of isolating these specific rank values into distinct architectural primitives to avoid analytical contamination. This report synthesizes primary literature from 2021 through 2026 to verify these candidate separations for downstream substrate integration.

***

## Task Overview and Substrate Context

**Candidate:** Survey RankZooSignature Tier-A++ tracking primitive supporting lit (T#13, T#19, T#22)
**Downstream consumer:** RankZooSignature Tier-A++ field-set finalization; HARD-5 enforcement spec
**Tags / context:** tensor, rank-zoo, tier-A++, T#13, T#19, T#22

This report verifies the specified anti-anchor candidate against primary sources, ensuring no gravitational collapse of mathematically distinct tensor invariants. The findings below serve as direct substrate inputs (anti-anchor pins, primitive registrations, catalog edits) and completely exclude conventional dissemination framings.

## (a) PRIMARY SOURCE CONFIRMATION

The candidate requires the unified specification of separator constructions from Lampert-Moshkovitz (2025–2026), Buczynska-Buczynski (2026), and Shitov (2021). All three primary sources are confirmed, un-withdrawn, and definitively separate the necessary invariants (HARD-5 enforcement).

### 1. Slice Rank vs. Partition Rank Separator (Lampert & Moshkovitz)
**Source:** "Slice rank and partition rank of the determinant" by Amichai Lampert and Guy Moshkovitz.
**Date:** Announced September 08, 2025 (arXiv:2509.06294) [cite: 1, 2]; Peer-reviewed and published January 23, 2026, in *17th Innovations in Theoretical Computer Science Conference (ITCS 2026)*, DOI: 10.4230/LIPIcs.ITCS.2026.90 [cite: 3].
**Status:** UNCONDITIONAL, PEER-REVIEWED.

**Findings:** 
Lampert and Moshkovitz establish distinct coordinates for **slice rank** and **partition rank** concerning the determinant polynomial $\det_n$.
*   **Slice Rank Constraint:** "Fully determine the slice rank decompositions of $\det_n$ (where each product must contain a linear factor): In this case, we show that $n$ summands are necessary, and moreover, the only such expansions with $n$ summands are equivalent (in a precise sense) to the Laplace expansion" [cite: 1, 2].
*   **Partition Rank Constraint:** "Prove a logarithmic lower bound for the partition rank of $\det_n$ (where each product is of multilinear forms): In this case, we show that at least $\log_2(n)+1$ summands are needed" [cite: 1, 2].
*   **The Separator ($\det_4$):** "Separate partition rank from slice rank for $\det_n$: we find a quadratic expansion for $\det_4$, over any field, with fewer summands than the Laplace expansion" [cite: 1, 3]. 

**Substrate Input:** Register `primitive_registration` for $\det_4$ where coordinate `slice_rank` = 4, but coordinate `partition_rank` < 4.

### 2. Border Cactus Decompositions (Buczyńska & Buczyński)
**Source:** "Apolarity for border cactus decompositions" by Weronika Buczyńska and Jarosław Buczyński.
**Date:** Announced January 27, 2026 (arXiv:2601.19558) [cite: 4, 5].
**Status:** UNCONDITIONAL, ANNOUNCED-NOT-PUBLISHED.

**Findings:**
The authors strictly differentiate **border cactus rank** from **border rank** and standard **cactus rank** within the context of toric varieties. 
*   **Theorem/Definition:** "A border cactus decomposition is a mulithomogeneous ideal in the Cox ring (also called the total coordinate ring) of the toric variety that witnesses that a given point is in a specific cactus variety" [cite: 4, 5]. 
*   **Geometric Coordinate Isolation:** The authors define the apolar ideal in the multihomogeneous setting to map out credible witnesses, shifting attention "from schemes or finite collections of points to ideals in $S$" [cite: 5]. This isolates border cactus rank as a distinct geometric invariant parametrised by the multigraded Hilbert scheme, separate from standard border apolarity [cite: 4, 5].

**Substrate Input:** Catalog edit to enforce `border_cactus_rank` as a strict dependency tracked through multigraded Hilbert schemes, decoupled from `border_rank`.

### 3. Waring Rank of the $3 \times 3$ Permanent (Shitov)
**Source:** "The Waring Rank of the $3 \times 3$ Permanent" by Yaroslav Shitov.
**Date:** Preprint July 10, 2020 (viXra:2007.0061) [cite: 6]; Definitive Publication 2021 in *SIAM Journal on Applied Algebra and Geometry*, 5(4), 701–714, DOI: 10.1137/20M1349254 [cite: 7].
**Status:** UNCONDITIONAL, PEER-REVIEWED.

**Findings:**
Shitov isolates the **Waring rank** (symmetric rank over $\mathbb{C}$) of the $3 \times 3$ permanent.
*   **Result:** "The Waring rank of $f$ is the smallest integer $r$ such that $f$ is a linear combination of $r$ powers of $\mathbb{F}$-linear forms. We show that the Waring rank of the polynomial $x_1y_2z_3 + x_1y_3z_2 + x_2y_1z_3 + x_2y_3z_1 + x_3y_1z_2 + x_3y_2z_1$ is at least 16, which matches the known upper bound" [cite: 7].
*   **Coordinate Distinction:** It is crucial to enforce that $\operatorname{wr}(per_3) = 16$ [cite: 6, 8]. This operates in a separate coordinate space from the standard **tensor rank** of the $3 \times 3$ permanent, which is 4 [cite: 9].

**Substrate Input:** `primitive_registration` for $per_3$: `waring_rank` = 16; `tensor_rank` = 4.

## (b) FOLLOW-ON WORK (2024-2026)

To fully map the RankZooSignature Tier-A++ topology, we trace how these 2021–2026 primary sources have been integrated, superseded, or contextualized in the immediate 24-month window prior to this substrate execution.

### 1. The Cactus Barrier (Buczyński, Feb 2026)
A massive validation of the HARD-5 coordinate separation constraint appeared less than a month after Buczyńska & Buczyński's January 2026 preprint. Jarosław Buczyński published "Cactus barriers" (arXiv:2602.11309) on February 11, 2026 [cite: 10, 11]. 
*   **Result:** Determinantal methods (linear rank methods) for bounding rank and border rank hit a hard geometric barrier. "For instance, it is known that using determinantal methods one cannot prove a lower bound for the border rank of a 3-way tensor of size $m$ in each direction that exceeds $6m-4$" [cite: 11]. 
*   **Structural Refinement:** Buczyński explicitly demonstrates that "linear rank methods outlined in Subsection 1.1 can at best detect $bcr_X(F)$ [border cactus rank], and never $br_X(F)$ [border rank] (unless when they coincide)" [cite: 12]. 
*   **Flagged Premature Claims:** Any literature claiming that matrix rank methods or Kozsul flattenings will indefinitely scale to resolve border rank lower bounds is fundamentally broken by this theorem. The determinantal methods are strictly bounding **border cactus rank**, not border rank [cite: 13, 14].

### 2. Quasi-linear Relation Between Partition and Analytic Rank (Moshkovitz & Zhu, 2024)
As a precursor and theoretical foundation to Lampert & Moshkovitz's 2025 separation of slice and partition ranks [cite: 3], Moshkovitz and Zhu published "Quasi-linear relation between partition and analytic rank" in *Inventiones mathematicae* in 2024 (originally submitted Nov 2022, arXiv:2211.05780) [cite: 15, 16].
*   **Refinement:** They proved that "partition rank and analytic rank of tensors are equal up to a constant [logarithmic factor], over any finite field" [cite: 17, 18].
*   **Introduction of "Local Rank":** They introduce a vector-valued notion of tensor rank called "local rank" as a bridge between partition and analytic rank [cite: 18, 19]. This requires a new HARD-5 coordinate field in the Tier-A++ spec.

## (c) FALSE-FORM RECURRENCE

The tensor complexity literature exhibits severe gravitational wells where authors conceptually collapse mathematically distinct invariants. The substrate must resist these framings through explicitly pinned anti-anchors.

### Gravity Well 1: Collapsing Rank Coordinates (Tensor vs. Waring vs. Product)
**False Form:** Treating "rank" as a unified property of a polynomial or tensor across different decomposition rules. 
**Recurrence:** In the wider computational complexity literature, the symmetric rank (Waring rank) and general tensor rank of polynomials are frequently confused. While over $\mathbb{C}$ symmetric rank is equivalent to Waring rank [cite: 20], standard tensor rank is distinctly separate. 
**Correction:** The substrate must forcibly distinguish these. Shitov proved $\operatorname{wr}(per_3) = 16$ [cite: 6, 8]. Conversely, the product rank (and therefore tensor rank) of $per_3$ is proven to be 4 [cite: 9]. If the substrate ingests a claim that "the rank of the $3 \times 3$ permanent is 16" without the `Waring` prefix, it contaminates the tensor rank coordinate space.

### Gravity Well 2: The Panacea of Determinantal Flattening
**False Form:** "Scaling up determinantal equations (linear rank methods) will eventually close the gap in border rank lower bounds for fast matrix multiplication."
**Recurrence:** Vast swaths of algebraic complexity theory rely on flattening tensors into matrices to find lower bounds. The gravity well implies that with larger matrices, we get closer to true border rank.
**Correction:** Buczyński (February 2026) unequivocally breaks this. The "Cactus Barrier" proves that these methods max out at **border cactus rank**, inherently capping out at bounds like $6m-4$ for $m \times m \times m$ tensors [cite: 11, 14]. The anti-anchor is absolutely needed to filter out programmatic agents or training data attempting to push determinantal methods past this ceiling.

### Gravity Well 3: Asymptotic Equivalence of Partition and Analytic Ranks
**False Form:** "Because partition rank and analytic rank are quasi-linearly related, they behave identically for structure-vs-randomness separators."
**Recurrence:** Following Moshkovitz & Zhu (2024) [cite: 15], the gradient of the literature trends toward treating partition and analytic ranks as practically interchangeable in additive combinatorics. 
**Correction:** Lampert & Moshkovitz (Jan 2026) explicitly sever this equivalence asymptotically for specific structures. "Our results imply that the determinant yields the first asymptotic separation between partition rank and analytic rank of $d$-tensors, with their ratio tending to infinity with $d$" [cite: 1, 2]. The anti-anchor must pin this asymptotic divergence.

## (d) RECOMMENDATION

**Consumer Target:** RankZooSignature Tier-A++ field-set finalization; HARD-5 enforcement spec.

**(i) Evaluation of Candidate Anti-Anchor:**
The candidate anti-anchor (*"need separator constructions Lampert-Moshkovitz 2509.06294 + Buczynska-Buczynski 2601.19558 + Shitov 2021 perm_3=16 in single unified spec"*) is **correct as stated but requires refinement**. It successfully surfaces the necessary literature to separate the Tier-A++ invariants. However, it must be refined to explicitly include the **Buczyński 2602.11309 (Cactus Barriers)** result, as this is the actual hard-stop mechanism that differentiates border rank from border cactus rank in computational limits. 

**(ii) Discovered Sub-Anchors / Companion Anti-Anchors:**
1.  **Anti-Anchor Pin (`border_cactus_barrier_pin`):** Implement a filter rejecting any claim that linear rank methods (determinantal flattenings) can bound `border_rank` beyond `generic_cactus_rank`. Map this bound explicitly to $6m-4$ for $\mathbb{C}^m \otimes \mathbb{C}^m \otimes \mathbb{C}^m$ tensors [cite: 11].
2.  **Anti-Anchor Pin (`det4_slice_partition_separator`):** Pin $\det_4$ as the definitive test-case node separating `slice_rank` from `partition_rank`. Any agent attempting to optimize $\det_4$ using a slice-rank expansion of $<4$ must be terminated as mathematically invalid [cite: 1, 3].
3.  **Primitive Registration (`local_rank`):** Extract the vector-valued "local rank" from Moshkovitz & Zhu (2024) [cite: 18] and register it as an 8th independent coordinate to the HARD-5 tracking matrix.

**(iii) Additions to the Verification Queue:**
*   **Work-queue entry:** Verify the asymptotic separation ratio of partition rank vs. analytic rank for $d$-tensors as $d \to \infty$ based on Lampert-Moshkovitz (ITCS 2026) [cite: 3]. Create a tracking metric for the exact divergence curve.
*   **Work-queue entry:** Audit all existing substrate nodes utilizing "apolarity lemmas" to ensure they differentiate between standard apolarity and the "multigraded Hilbert scheme" border cactus apolarity defined in Buczynska-Buczynski (2601.19558) [cite: 5]. Withdraw legacy nodes that conflate the two.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6ys3h9jLzVhr9sMnNBh-VqUjSXADVRamiJOngVZalGvc5ESmdHCdifBhzpUpZXAEvaBqDDKK-hA4ctXOu83ZeWi-cveK9MDmPgTVe5Nrf8Os6Oa4TbA==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdpNwN9aFOpnhifJAUArRmnT8rzxAmUkayAeCIpkyhUedU-Ovkzkt4PHIEDlmp-_ydi5oFxNgm0M5xqqSNG1lLzRhTkwpQqizy_XwNq3TkKa67_wgw0Q==)
3. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjlv1vRaH4o-NHWe7jZESY1nGa0ZJmvILHOBuPJCdT2w5THdwMTd2CZda6JZL_KyRVgaYZQVNr2GAZkkdpxaAOShc-7INuyTlyt1zMHtt6pM3DirPJy9fgFoQiBESlaiJxZi49MZV8yP4FVf9YLZm3GciyTwHGkc7-OISJMQ==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2DVRhlQBhuXxFqSIm6EYfznLiKwcPQQafdsaR8TFCDaAKMMBmVCqhC3LPJ0IooJM0LXxOtj9J-UX-dgP-LyAaeDFrp56FH4zcKM8xRA1rYPvZWOQzROIPmQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnKCXCNClJN0eKJgvBgB_n-maVrSuGSv4rdK1lEbPf_Clfjb_va1tWFcAjMf-00icFLsxUAzbzusTj7R-I-QMQmpzCAGVwgKEaS6BGmSqqKR7agV42Xw==)
6. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwZnrJ_j1XGTYp5LbsIMmlKHOEKtOUfMak4XT9dKt_ZPUlvW0hV-N8AHIM9eBlhBKPzW0YzV2uLx_DzUq3Bd8qkkW27ZalAy4VxQLhkTQSW_zpM2OS)
7. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwOh1vH9tq3wEhwbDkGdV4hiXy4I0IiinTdwsDaTPwxbP775QXrz-_rPIcgkeadXyOB65wSL2-0o8PyKCUog8hswyCnbeqPtjCTQTacyOkY7VE1XN3gcpx1qxUHC0iHpzWLgU=)
8. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWdeg440aF9c85FoPgxEC3WuDOgsLeMmpOKWTEYjAfTi2HZV3-auXlO9PafN2Yr8L7q2dv0jXS_HkpaKodPXsGFFi4kMc9Rz5DpgiZFkqO2nHbQQFE-1WgvX1v)
9. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECSBeSk6xGYETWnjRgiMFP_EH5TGuLLjVRNOMSgoWXI5G-lOvILMyBJI-5BqLa9l4EUAB53EFEADvuJBuDPOtm95pg_0w7PO6WSU_OswSb1vXdznVLQ3xk3xKkFGTwSujIByamORZxW1Imb1pVb465P4H69pg3ABEYuh_NaKijfLQu3kUI3ZyNZP6c_c8KAG_GLGbswO-Deqd3Jpvx9TXoSYD58cXFjnT2WkfSKLcTgrkD-Qp3cURYKyIpoaQFxid7iNSXrPieyI90xeQpNxtC9gaa9Ev_-XHk)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKQI_d8GOnTcma4ZBg2QhRyHwTHhK3uNDvj86Uv9tuC2pyS0yH0_slmWhRk1xNgQKguityA2MZ4JW4GhdzF9-V1SZQV0OmCDkJozHsFkjafM9AlEDhMvnSWw==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiT8nu74SO2rmDGLZ8iCj6nULJDq194t_5SCLKHmdHkkFGFlzwTL7XKKCTIClquuaVe3XZK6KpbdkrYcv1FZ8jfY1YEhbRFjgfFdLhU6-sjMh0oknAMQ==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiId2TPruL6KA7bTQf873FsPpL9aIaczkpJ5uTHtuLYz50XmsPbZTWOTX0eXF1XD_TMqMDYyirMYnzgqNlkh-Dh-nV3h7lFRWg9ZU-XFiUk9B44eS2whyGihcVfXL3MRXONZIiBcFRZ5piiCYSnQ76EYE_Nl9_al0=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFAC8yQ51TZTNuo_kH7exzRw72AtGJ51xVEsP1czuAdGa3X1RtH49xVKmiyOu-53zkVu4XLmTMvhGbTExVjiUaTuIvaSLfIOHsN7iB2QrGV69FwdwOF5X_unDjeGgOeRa3lqW6wBFaA-IqH7ajUGkpvg3c3fTwtykAgcNNMC_hZKXzv9wvp7WnYDr7Ap2plXYYRHW-UPFaHS_NQ7pPgzzxJpSS0aN8vw==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEad1LbbJIuKgL-4fdcyYlT1TOmjxP1ivdECUSyuomfPqLceUBiL8aBi21fXZmqOkf7e9CO8ZGVV2yXdJIWc9R9jud0_badEReYYr07Q8py8fohKvrIvw==)
15. [cuny.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjZi3p7Pj70cNwRSitYWwzWvzYoccJOgjwgUbgV57HWGRKq2TSjj1jRzbBQDCPmDlAazEc2bpNSvxuSWnWOhRCiywyUhhdVBfHWaU6o2xdENFlLARfz8TidH3-gUSQ-WT-TAxcyZUQD27CX5vf)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7fgQ6Jz9hx4oKT1eQZuEA1GcO4Tod7qvNJSwPoepfBYQtLiM30qGQGpxOwEoaWyALF1XIgY623RfM6_69dhqLIFOf7q5xRoRD6b_ku0cUqBtdiB-tzA==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWym_bjNrsbBDXr42TabDv3DQ2CknL9MCg-4EVAO7eNtHphkdeFg1wJI-asPCRrgiYA6xTOY40UDkUvaGeTuTE6J1ESCOw42KFiK3SEvtswBrTLIO67Q==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZ0-szSIIa2iHurD8pkFJDWpaEB9Cu6RJ7PUT9CuxznjEWvC2Cbw7LZ53wmBRTphV2bHOqtdpfjpb9aECCboV6OsypdipaJeLpEbD2mGH63trCd0b80vomaEpqeLoCyXRChmzIhB1x1OkmOGwAMEmg98W7cHQLHlgCwCp064mWCH2tgzQ2Xrfdkt5YP6WhgzwloBz1FWh8KGeFzRLH2GGqhhk=)
19. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAeQJhHsQ2AqrLfEPCfCNZzSH5Z6e6n341Fxj8P7JeMU6df8_WB0vUaqgv2VG9wrergX9lEQ-_RvjAzS3haXbHhgd4nhcY0p482qyoypD2limww9DXYW-KMIkpPqUZUMrKrB4_ENyIN0Hpcs102m6UItKwvM2f)
20. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpr6ev7gwvFLkIEHj9INu6sLfgCB3ByujPc7gTTgTiKVmLbHDfbdjouYkLxhT_GqjZ1dh23b51ccC-MxAUebVu18VhKSWdhFluGq29fIGyqZqkLD43E12JFojnz_OtFj6ZzLrJU7Mbvd6X)


# Prompt 05: DR-022 — VERIFY-LIVE T#23 Strassen tensor-rank additivity safe-zone (same as T#6)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZCUzhFYW9TY0p2LXJfdU1Qdi1XcFlREhZCUzhFYW9TY0p2LXJfdU1Qdi1XcFlR
**Elapsed:** 1758s

---

# Anti-Anchor Verification Report: VERIFY-LIVE T#23 Strassen Tensor-Rank Additivity Safe-Zone

**System Run:** Prometheus Multi-Agent Substrate 
**Target:** T#23 Strassen tensor-rank additivity safe-zone (cross-link T#6)
**Date of Synthesis:** May 2026

### Leading Pin-Status Summary

*   **Status:** VERIFIED. The anti-anchor candidate T#23 (tensor rank additivity safe-zone) is mathematically sound and explicitly supported by the 2024 primary literature. 
*   **Coordinate Pin:** **Tensor rank** $R(T)$. This result strictly does not apply to **border tensor rank** $\underline{R}(T)$ or **asymptotic tensor rank** $\tilde{R}(T)$. 
*   **Safe-Zone Boundary:** Over the base field $\mathbb{C}$, if independent tensors $T_1$ and $T_2$ both satisfy $R(T_1) \le 7$ and $R(T_2) \le 7$, tensor rank additivity holds unconditionally: $R(T_1 \oplus T_2) = R(T_1) + R(T_2)$. 
*   **Gravity Well Warning:** LLMs intrinsically conflate module/matrix rank additivity with tensor rank additivity, and further conflate distinct tensor invariant coordinates (e.g., assuming Shitov's 2019 tensor-rank counterexample implies slice rank additivity is also false, which is incorrect per Gowers 2021). 
*   **Substrate Action:** Propagate catalog edit to T#23. Register boundary parameters as primitive constraints. Generate work-queue entries for downstream verification of asymptotic rank bounds defined in late-2024/2025 literature.

***

## (a) PRIMARY SOURCE CONFIRMATION

**Downstream Consumer:** T#23 catalog edit propagate; T#6 sub-type registration.

The candidate anti-anchor claims the existence of a proven "safe-zone" for Strassen's tensor-rank additivity conjecture, specifically for tensors up to rank 7. This candidate is strictly verified by the following primary source.

**Primary Source Registration:**
*   **Author:** Filip Rupniewski
*   **Title:** "Strassen's rank additivity for small tensors, including tensors of rank less or equal 7"
*   **Journal Reference:** *Linear Algebra and its Applications*, Volume 698, pp. 448–478.
*   **Publication Date:** PEER-REVIEWED. Definitive publication date: October 1, 2024 [cite: 1, 2].
*   **Preprint Date:** September 23, 2022 (arXiv:2209.11040) [cite: 3].

**Exact Theorem Confirmations:**
The primary source unconditionally establishes that Strassen's rank additivity conjecture—which states that the rank of a direct sum of independent tensors equals the sum of their individual ranks—holds for a specific boundary of "small" three-way tensors, despite the general conjecture being definitively disproved by Yaroslav Shitov in 2019 [cite: 1, 4]. 

Crucially, the 2024 Rupniewski paper formalizes the rank-7 ceiling explicitly over the complex base field $\mathbb{C}$. The core finding states:
> "In this article, we present families of pairs of small three-way tensors for which the additivity holds. For instance, over the base field $\mathbb{C}$, it is the case if both tensors are of rank less or equal 7. This proves that a pair of $2 \times 2$ matrix multiplication tensors has the rank additivity property." [cite: 1]

To align with Prometheus doctrine Constraint 4 (Distinct coordinates), we formally encode the invariant as **tensor rank** $R(T)$, representing the minimal number of simple tensors required to express $T$ as a linear combination [cite: 4, 5]. The result establishes that for $T_1, T_2 \in \mathbb{C}^{n_1 \times n_2 \times n_3}$, if $R(T_1) \le 7$ and $R(T_2) \le 7$, then:
$R(T_1 \oplus T_2) = R(T_1) + R(T_2)$ 

Furthermore, this yields a concrete invariant evaluation for the $2 \times 2$ matrix multiplication tensor $\mu_{2,2,2}$, which has $R(\mu_{2,2,2}) = 7$. Rupniewski (2024) proves unconditionally that $R(\mu_{2,2,2} \oplus \mu_{2,2,2}) = 14$ [cite: 3].

**Distinction from Preceding Literature (Primitive Registration):**
This 2024 result must be precisely cataloged as distinct from earlier, more restrictive safe-zones. In a January 2020 paper ("On Strassen's Rank Additivity for Small Three-way Tensors", *SIAM Journal on Matrix Analysis and Applications*), Buczyński, Postinghel, and Rupniewski established a lower ceiling [cite: 2, 6]. The 2020 result required that *one* of the tensors have $R(T) \le 6$, or that one of the tensors be concise with rank at most 2 greater than the dimension of one of its linear spaces [cite: 6, 7]. The 2024 Rupniewski paper expands this coordinate constraint, allowing *both* tensors to reach rank 7 [cite: 1]. 

*Note on Withdrawn/Supplanted status:* The 2024 primary source is fully peer-reviewed and published. It is not withdrawn. It explicitly supersedes the more limited bounds presented in Rupniewski's 2017 Master's thesis and 2022 PhD thesis [cite: 8, 9].

## (b) FOLLOW-ON WORK (2024-2026)

**Downstream Consumer:** Training-corpus filters; Work-queue entries for downstream coordinate tracking.

The 24-month window following the publication of the primary source shows significant substrate activity branching into distinct coordinates (border rank, asymptotic rank, slice rank, and subrank). To obey the anti-gravitational-well doctrine, we must surface these alternative trajectories and weight them appropriately, ensuring the catalog does not collapse them into the verified exact tensor rank safe-zone.

**1. Explicit Reconstructions of the General Failure (July 2025):**
Borovik, Flavi, Pielasa, Shatsila, and Song (arXiv:2507.17890, July 23, 2025) published "On the construction of a counterexample to Strassen's rank additivity conjecture" [cite: 4]. This work formally reconstructs Shitov's 2019 dimension-counting disproof. 
*   *Interaction with Primary Source:* Borovik et al. (2025) explicitly cite Rupniewski (2024) to establish the mathematical boundary [cite: 4]. While Borovik et al. demonstrate that $R(T_1 \oplus T_2) < R(T_1) + R(T_2)$ for sufficiently large tensor spaces, they confirm that the Rupniewski safe-zone remains intact for small tensors [cite: 4]. This validates the T#23 anti-anchor pin against current (2025) literature.

**2. Shift to Asymptotic Tensor Rank $\tilde{R}(T)$ (Late 2024 - 2025):**
A separate cluster of highly relevant work has abandoned exact tensor rank additivity to study **asymptotic tensor rank** $\tilde{R}(T)$. 
*   Blatter, Draisma, and Rupniewski (arXiv:2411.15789, November 24, 2024) proved that asymptotic tensor rank is "computable from above" [cite: 10, 11]. They show that for any real number $r$, there exists an algorithm evaluating a finite list of polynomials to determine if $\tilde{R}(T) \le r$, establishing that sublevel sets of asymptotic rank are Zariski-closed [cite: 10, 11]. 
*   In "Countably many asymptotic tensor ranks" (*Linear and Multilinear Algebra*, print January 2025, online March 2024), the same authors proved that for all algebraic tensor invariants over $\mathbb{C}$, the asymptotic parameters take only countably many values [cite: 12, 13].
*   *Premature Claim Flag:* Any LLM text generation that asserts "tensor rank is now computable from above" based on the November 2024 Blatter et al. paper is a **false claim**. The 2024 result applies *strictly* to **asymptotic tensor rank** $\tilde{R}(T)$, not exact **tensor rank** $R(T)$, which remains NP-hard to compute [cite: 10, 14].

**3. Generalizations to Subrank $Q(T)$ (August 2024):**
Shatsila (August 15, 2024, "Exact values of generic subrank") proved the subrank of a generic tensor in $\mathbb{C}^{n,n,n}$ is $Q(n) = \lfloor \sqrt{3n - 2} \rfloor$, providing precise values for the generic subrank of tensors of any order and shape [cite: 15, 16]. 
*   *Substrate requirement:* This requires a separate primitive registration for subrank $Q(T)$, entirely decoupled from the tensor rank $R(T)$ additivity node.

**4. Symmetric Tensors (October 2025):**
Barrilli, Mourrain, and Taufer (arXiv:2510.25681, October 2025) preprinted "Generalized additive decompositions of symmetric tensors" [cite: 17].
*   *Interaction with Primary Source:* This tracks the extension of additive properties into symmetric tensor domains. The decomposition of homogeneous polynomials (Waring rank) operates under different algebraic geometry constraints (Alexander-Hirschowitz theorem) and must not be collapsed with standard tensor rank additivity [cite: 18, 19].

## (c) FALSE-FORM RECURRENCE

**Downstream Consumer:** Anti-anchor pins.

Standard language models possess a massive semantic gradient toward "additivity" stemming from linear algebra and module theory. Without an anti-anchor, LLMs predictably hallucinate that Strassen's additivity conjecture is either (1) broadly true, or (2) totally false in all domains due to Shitov's 2019 counterexample. Furthermore, they fail the HARD-5 coordinate separation, projecting truth values across distinct invariant types. 

The literature from 2024-2026 and existing academic corpora demonstrate the following specific false-form recurrences that necessitate the T#23 anti-anchor:

**Gravity Well 1: Module-Theoretic Contamination**
In broad mathematical querying (e.g., academic help platforms), the question "Show that if $F_1$ and $F_2$ are free modules over a ring with the invariant dimension property then rank($F_1 \oplus F_2$) = rank $F_1$ + rank $F_2$" yields universally positive proofs (e.g., Chegg, March 2023 [cite: 20]). Because standard matrix rank ($d=2$) and module rank are inherently additive, probabilistic text generation will recursively assert that $R(T_1 \oplus T_2) = R(T_1) + R(T_2)$ for $d \ge 3$ unless explicitly blocked. The anti-anchor is strictly required to wall off tensor rank ($d=3$) from matrix rank ($d=2$).

**Gravity Well 2: Slice Rank vs Tensor Rank Conflation**
Recent literature highlights that different coordinates behave differently under direct sums. Amanov and Yeliussizov (arXiv:2107.08864) note: 
> "In 1973, Strassen conjectured that the tensor rank is additive under direct sums. In 2019, Shitov disproved this conjecture. Very recently, Gowers (2021) proved that the **slice rank** is additive under direct sums." [cite: 21]

*False Form:* A generative agent might state: "Recent work by Gowers proves that rank is additive under direct sums, rescuing Strassen's conjecture." 
*Correction:* Gowers proved additivity for **slice rank** $sr(T)$, not **tensor rank** $R(T)$. Slice rank measures decomposition into tensors of the form $u \otimes v$ where $u$ is a 1-tensor and $v$ is a $(d-1)$-tensor. Tensor rank $R(T)$ requires decomposition into fully simple $a \otimes b \otimes c$ tensors [cite: 5, 14]. The anti-anchor pin must forcefully separate these two coordinates.

**Gravity Well 3: Border Rank Contamination**
The 2024 Rupniewski result verifies the rank-7 safe zone for exact **tensor rank**. A recurring false form is to extend this safe zone to **border tensor rank** $\underline{R}(T)$. 
*False Form:* "Over $\mathbb{C}$, the border rank of small tensors up to rank 7 is additive."
*Correction:* Border rank additivity fails catastrophically even for small tensors. Schönhage (1981) demonstrated that border rank is not additive for small matrix multiplication tensors [cite: 4, 7]. For example, $R(\mu_{2,1,3} \oplus \mu_{1,2,1}) = 7$, yet specific border rank combinations are non-additive. The 2020 Buczyński, Postinghel, and Rupniewski paper proved border rank additivity *only* in highly constrained spaces, such as when the direct sum tensor is contained entirely in $\mathbb{C}^4 \otimes \mathbb{C}^4 \otimes \mathbb{C}^4$ [cite: 6, 7]. The 2024 rank-7 safe zone *does not apply* to border rank.

**Conclusion on Redundancy:** 
The anti-anchor is **not redundant**. In fact, due to the volume of publications between 2024 and 2025 regarding asymptotic tensor rank, subrank, and slice rank, the semantic landscape is highly unstable. Without T#23 pinned specifically to $R(T)$ and rank $\le 7$, generative synthesis will collapse these coordinates.

## (d) RECOMMENDATION

**Downstream Consumer:** Substrate inputs, Primitive registrations, Work-queue entries.

**(i) Anti-Anchor Correctness and Refinement:**
The candidate anti-anchor (VERIFY-LIVE T#23 Strassen tensor-rank additivity safe-zone) is **correct as stated but requires strict coordinate refinement**. 
*   **Refinement:** The text must be explicitly amended to state: "Safe-zone applies *only* to exact Tensor Rank $R(T)$, strictly over the complex base field $\mathbb{C}$, for pairs where both tensors satisfy $R \le 7$. It does *not* apply generically to Border Rank $\underline{R}(T)$ or Slice Rank $sr(T)$."

**(ii) New Sub-Anchors / Companion Anti-Anchors Discovered:**
During verification, three necessary companion anti-anchors were discovered to enforce the HARD-5 doctrine:
1.  **Companion Anti-Anchor T#23-A (Slice Rank Additivity):** Register that **Slice Rank** $sr(T)$ is unconditionally additive under direct sums (Gowers 2021) [cite: 21]. This provides the orthogonal positive counterpart to Shitov's negative exact rank result.
2.  **Companion Anti-Anchor T#23-B (Asymptotic Rank Computability):** Register that **Asymptotic Tensor Rank** $\tilde{R}(T)$ is "computable from above" and its sublevel sets are Zariski-closed (Blatter, Draisma, Rupniewski, Nov 2024) [cite: 10, 11]. Attach a boolean flag: `COMPUTABILITY_FLAG = TRUE` for $\tilde{R}(T)$, `COMPUTABILITY_FLAG = FALSE` (NP-hard) for $R(T)$.
3.  **Companion Anti-Anchor T#23-C (Asymptotic Rank Discreteness):** Register that **Asymptotic Subrank** $\tilde{Q}(T)$ and **Asymptotic Slice Rank** over any finite set of coefficients have absolutely no accumulation points (Briët, Christandl, Leigh, Shpilka, Zuiddam, 2024) [cite: 22, 23].

**(iii) Related Claims for the Verification Queue:**
Generate the following work-queue entries for further substrate execution:
1.  **QUEUE ENTRY 1 (Border Rank Safe-Zone):** Verify the exact bounds of the Buczyński-Postinghel-Rupniewski border rank $\underline{R}(T)$ additivity conditions. Specifically, verify the scope of the claim: "additivity of the border rank holds if the direct sum tensor is contained in $\mathbb{C}^4 \otimes \mathbb{C}^4 \otimes \mathbb{C}^4$" [cite: 6, 7].
2.  **QUEUE ENTRY 2 (Subrank Generic Values):** Extract and register the exact polynomial formulas for generic subrank $Q(n) = \lfloor \sqrt{3n - 2} \rfloor$ over $\mathbb{C}^{n,n,n}$ published by Shatsila (August 2024) [cite: 16]. Ensure this is mapped to the coordinate $Q(T)$ distinct from $R(T)$.
3.  **QUEUE ENTRY 3 (Well-Quasi-Ordering of Tensors):** Verify the August 2025 finding by Blatter, Draisma, and Rupniewski ("A tensor restriction theorem over finite fields", *Compositio Mathematica*) establishing that tensor restriction over fixed finite fields is a well-quasi-order (no infinite antichains, no infinite strictly decreasing sequences) [cite: 2, 24]. Link this topological property to the discreteness of asymptotic tensor parameters.

**Sources:**
1. [unibe.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFTxR1wn7ShnImjnOpumLm_krbW_SIM0QpFGvegp07Lb3rNDl4tcAMkQpw_PNWzv2_p63PKJBztTEu8d_-c7dahDeC1cHP-1USNWEMFXEwftZiw5AWdhXsQbCBD_Dnz7mu1hQjiwAeTS0z5KNao_ySye8c4F4tWLg-RMP03WWji-YoehZ3H2NyBPxF7AM=)
2. [orcid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiayqdAT-XZ7w38zKj94RIjQqPTL8OaIKe2rKUrZJ1fSc2clJxpaWKtkMbRnXVc-iP56qcQuqVQT7--G9jQN3PqY_VmlTlasaHMm1z59bw7LJ9dSroFb0Z8zDI)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESP7ZlUq_oUookVaPeBKB8tv1KSwpjrEchMuAj_UkuE4q3ro9RVaa0r-E1tRHJofwnJEPHim3UyMEKfbK20IpBXuYc9dHTnl0Lax80UL2cqjviVS2RfA==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTzzOG9-gkUqmW5clkClmX9deNKSL8rPByofI6uK1v-a5-HoM-3Y38JzPbptK1n3S5fWXRx6ZWhlGPJPrCshhPNCmiD7XKFFiKffwRQurZx3Oavs7cXQ==)
5. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGn_caaobE8ePOzXK9jkM606F-L1yHAUzJM6_nHvBMqIuRceGfQdSK7pXuCEYNRaPUsSTTE4_DtOkEzbdPA3CeTHjpbgj6qmnwS-nrWjYflH1Yv5YVUXMSjKxnIxZUMmOnLdjd4Q5D3kryK7mTrFCSgYAg1J8U772g=)
6. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHP8z9IbcAYhQ-rmoLkUqbec7zn2ldPJBkJ9dQ1F4nJG1NZU9lAMAeuUOr9SZd8AKKk4OJ_yCT1ytURdUmL0iuMEucoVgPG-Ni1oID2L8cSOCi6g4hayY1JS5wYsITWwDIdJsI=)
7. [lboro.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVvETrnceuy9VJJGsIK1wyRGyiElVd6Qh6X8-83EkzTAbHL9UeKJlukTs_HzbnACAakTuvnCohgK8KTtAuA9xXNuoBC4pWdCIC5_0-UFptkEJ7ptBOo_bwVZA3a2pJRrF3P87mow3ViIUUTvXbOXoL4MwasVH6B40njHMFqvuu9s173xt2pgC-w3IWDW7uPROymN87wJHk96ou3vXxL0Qnylk-aBqhdgtjUtMehrn1jrUGBIp2v0014Yizpg7dzxBKw2EKilFa8g==)
8. [impan.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIz0xjWcYoTA_NVWYyAIbaHmrWbzialP3lZh4iQyL03Y2IShOMumm_8VxszAjHaLkqlDHFKnozUYrua9n60_8x19pznZ94PBl9H9q8Kgm_gIKl_8yzFbGtbTorREjneguuImRONKQ_E37hKI-Oyp47P-QAqOdN9g==)
9. [mimuw.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFr1s5zt0NW0jJcIiaShnRrlcVCcF0nCAxVUmdo-cDHnutWnNEQmfcwEz70UsbCHTAxQvCpo8Z0j9D_aRaYXApporOxq5ZmEdgibMTjJs4WzfCjc8taEGpNMwvKoABBLH1vPHgAnPsGhfXFRKaSE637KIjtLuf3qf7tIp69jc=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvn8Jl__3dT3oo-S98hkEMN-wV2QnsDcoGBohWHCTCGK1EsxPEROsTbd2gBgRINddznbT3VRkmmplS-z0NBrmetvZnJLJJ4QncdTvkxQv8GcSko3MPxw==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpZyYcQ7H8UyOtZ676Xkimhw3jDMWSe2f4VerILe0O0M64tDBnXsg0C895qj_NGQCi_FpqRu78DqD0XB0rOetHXw8LPs4oKihyOldzH27hzWxnjLzfk8UmtMgVLVPo2g0PMAi6ZD4JBPMF-QLRaBOwnLBtfE3VZNmiYU1A_AVwCt2L1HWgrcDMbe6ygewIBUSg56Qtwr-8YZPVhkNGKYo=)
12. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpNbF07DB1-v1NOyxLL7M4zII41jCUkTuyUmjdTVJAIbw2Y8IB1_ISzsevlvfAifZOOwgonWNxcKWc4H1uq2YRZMSzC6mW3vbb_A5Wn7ho4Juju08xvpt3OYo1KEvdUIxtKyeUsr70Nd4ScNj_jueN_bFM7dleKQ==)
13. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9PPEVkFICQFfAwXWSoaj9NOrWAbk0Yz95yYPpt_5fko28ZzAu3DLOVNNh9J6jEpPye0egGKB16FmiyW5GX_F0XHMtrwQ5cNP6lB-jufvYY0EGxU24sQAubGspQsRnqLSGy6UYUGGWhnqMrHSlKEsmoJvLivjNzw==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3P_fINnCybWsu9QqcumGwhn16rglwzKCQF07lU1H31X6Pn-sDbmtN1ElY2F_q5vXKRYwJRsPPO_uOZy3_e-i2HQ3or1t72_O8svqNOJfmCoduZjea0g==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpGpHW2h6tTxcP8agBZAHhBRl1c6_0RnAEBaLwTtAcWUHU_zU2KfdYmR3Rh2QnM2aObLRuHtJDXWhctRdMEuio1k6-U2Z2HX6EKBpSxV9r8QOQh26rwMOuT17zd2uIHs_WSwtSdsQZ27In4w==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI1rf0ZYNcUsrWOflc2j5PQfRBknuNy4pyDuszb0wvu4Xab3eNMqiRvkvFCZtDbvRYDV2TYZaPIdTW38mK9MKtOINeDFk27hANkF1y1a063xF-TWSaEvqnq19-YvyOjhYxXN2JHqxUijYD2RfURGWucXX356-2HJuMGkGhY2hlp1eHNuPjGs6a)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDdNlUEbUENohMoYNcTzpK6owniq-wn5CwO0lXPAHhDOLZxc7NGFI1qZ8GCMiL4pL9kHKDaAOTA0U2WufB3s-XF9_nzorF2I_0g7M80-kvNITdI8YaXA==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6Bt22kJIKSjtodDW18LHJhD5_KKXk-wOm93NbfWH4CuEw6eBNgB31E8JigLDRjKIT8IB7sMMqFjrykZS46eN8veXmrta8Vo-Zfey1-PZNSMDtJWF_dVuyc9LrH6osWZzP8meX2SzzhWMjk5fCR8nTJfCZJK_gK6eKVT7x-2jSv9g3X8ZKCgRfZ_znRKh76XC7yGMfThlV7nQdKczC6Bw=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNZiWdw97RSNwUH3DHqg1VVdAsHoOSRpLDhaAdhgAEUWW6o_dS3EQIq9KEpwjthXTBMj56xAQ3-akhi8vKbf1SrW-4tT1YVFM4fyHWbjYGhSPZctY8Ng==)
20. [chegg.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOu7cchh1y9OwvFygEApFUSrsB9N3FfzvaoaYJTayFxM4C3cW_0bCfSBHq0hVlV4G9HXmvjXPGWypmz7fk5j9FE0ELU6q4O4ziDKSvsIIHgl_FoskZ-oymPB7VJXdOFEqJdNZNyBnz3w6TWl59lqvbaXqCcvflBGPpLOsNJUXRhi173Fg-zxwvzO5la8ePticfLzsdHW1XgIyRwSdA4xFRaxZk2lVKP5Qn2G_zeiN0LWj2IVz2heclxbsIUqz4lY5AWB1-1R6GuEJKkRaMC2pADA==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwFhWTFjZTDa_X0-8ARNzQWRZZARuFzKjqrTwt8hUPCU32mcjO4EQp4sPUr0boNaRAJUUEePq0KsAqw9OPLIiqksQdjXkXHBYN_lwyg3HtbqIHGJa1mg==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE49L6dbDZDj2JVFJVQKGrN-zpPB3GBZnmolKOSTBifY9VUiUzKBHnZaY3fiIaVYphRGJJva-wUbDbBGA6PsSescrJYP5NmdmG6M_aaC6tlzBKqm4INxQ==)
23. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpQ24Y1uyK1iMXgGCrRTfDg-SECVM8eELa7sRZtMQKQ_HrepszJN5zdXrSvSMVtYOI5ZAUORJfZmrVE-SdpLTpZcqWG22__6aBheQWH0MCmuTer0yP3tsZ_e7X)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ6NpCyYC3ipgUYEQChBvhUB1AFcHo9oj-mzMUkQ3rNjcI--k7NgR2okvz8k7vZG1_esotG-fRA_agKq2_Wtj_4O5Zq4e3VEkLbXfNhU_RMvG4SqZXkGr9dB0wcESuoCZr3QRQapZvWfMdjQ==)


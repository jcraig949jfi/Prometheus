# Prompt 14: DR-031 — Survey WaringRankWitness Tier-B sub-type supporting lit (T#22 Shitov 2021 perm_3=16)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiRUFFYXR6ZUdOeTMxTWtQdk5qdW1RWRIXYkVBRWF0emVHTnkzMU1rUHZOanVtUVk
**Elapsed:** 1093s

---

# Verification Report: WaringRankWitness Tier-B Sub-Type (T#22 Shitov 2021 perm_3=16)

*   **Primary Source Validation**: Y. Shitov's unconditional proof that the Waring rank of the $3 \times 3$ permanent is exactly 16 is fully confirmed in the peer-reviewed literature (SIAM J. Appl. Algebra Geom., 2021).
*   **Coordinate Separation (HARD-5) Alert**: Substrate corpus contamination is highly probable without immediate intervention. The literature severely overloads the term "tensor rank" regarding $per_3$. The *Chow rank* (product rank) of $per_3$ is 4, while the *tensor rank* of $per_3$ viewed as a symmetric tensor in $(\mathbb{C}^9)^{\otimes 3}$ is 16. 
*   **Anti-Gravitational Well (Asymptotic vs. Sporadic Inversion)**: The prevailing computational complexity gravity well dictates that the permanent (VNP-complete) is "harder" than the determinant (VP-complete). At the micro-invariant level of $n=3$, this is inverted: $det_3$ strictly dominates $per_3$ across Waring rank (18 vs 16), product rank (5 vs 4), and symmetric tensor rank. 
*   **Recent Literature Dynamics (2024–2026)**: Follow-on research rapidly expands bounding methodologies, notably achieving exact border tensor rank evaluations for $det_4 = 12$ (Oct 2025) and establishing fixed-parameter debordering limits for border Waring rank (Mar 2024).

This verification stream evaluates the proposed anti-anchor pin against the primary literature to enforce HARD-5 coordinate separation, prevent invariant collapse, and formalize catalog edits for Project Prometheus. The findings below bypass conventional complexity-theoretic narratives to explicitly isolate the geometric and algebraic invariants of the $3 \times 3$ permanent and determinant tensors.

---

## (a) PRIMARY SOURCE CONFIRMATION

**Status**: CONFIRMED. Unconditional, peer-reviewed.

The anti-anchor candidate references Yaroslav Shitov's resolution of the exact Waring rank of the $3 \times 3$ permanent. The definitive peer-reviewed publication is:
*   **Author**: Yaroslav Shitov
*   **Title**: *The Waring Rank of the $3 \times 3$ Permanent*
*   **Journal Reference**: SIAM Journal on Applied Algebra and Geometry, Vol. 5, Iss. 4, pp. 701–714. [cite: 1]
*   **Date of Definitive Publication**: 2021 (Originally announced as a preprint on viXra:2007.0061 in July 2020) [cite: 2, 3].

**Exact Theorem Statement**: 
"Theorem 1.1. The Waring rank of $per_3$ equals 16." [cite: 3]

**Mathematical Context and Proof Architecture**:
The primary source investigates the polynomial $per_d \in \mathbb{F}[x_{11}, \dots, x_{dd}]$ obtained from the generic matrix determinant by replacing $-1$ coefficients with $+1$. Shitov operates under the assumption that the field $\mathbb{F}$ satisfies $\text{char } \mathbb{F} = 0$ or $\text{char } \mathbb{F} > d$, ensuring the existence of a Waring decomposition [cite: 3].

The finding establishes that $WR(per_3) = 16$. This matches the previously known upper bound derived from Glynn's formula (which expresses $per_d$ as a sum of $2^{d-1}$ products of linear forms, yielding $WR(per_3) \le 16$) [cite: 3, 4]. Shitov’s contribution is the matching lower bound. 

Critically, for substrate primitive registration, Shitov *does not* use the standard symmetric-flattening (catalecticant) lower-bound method. For degree $d=3$, symmetric flattenings are fundamentally limited; as noted in the literature, symmetric flattenings are only sufficient to prove lower bounds for $r=1$ and $2$, requiring higher-order constructs like Koszul-Young flattenings to extend the range [cite: 5]. Shitov bypasses this entirely using the *substitution method*, invoking ad-hoc linear space intersections and constructing specific anti-symmetric matrix witnesses to demonstrate that any hypothetical rank-15 decomposition leads to a dimensional contradiction [cite: 3].

**Companion Finding ($det_3$)**:
In a subsequent preprint, Shitov applied similar techniques to the $3 \times 3$ determinant.
*   **Title**: *The Waring Rank of the $3 \times 3$ Determinant*
*   **ArXiv/viXra ID**: viXra:2010.0193 [cite: 6]
*   **Date**: October 21, 2020 (Announced-not-published / Preprint).
*   **Exact Theorem Statement**: "Theorem 1.1. The Waring rank of $det_3$ equals 18." [cite: 6]

*Behavior Delta*: Register $WR(per_3) = 16$ as a confirmed Tier-A primitive. Register $WR(det_3) = 18$ as a Tier-B (preprint) primitive. Generate a catalog edit highlighting the substitution method as an alternative to catalecticant flattenings for $d=3$ lower bounds.

---

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month window reveals significant advancements in the algebraic complexity of bounded-rank tensors, superseding prior asymptotic bounds and focusing on exact invariant calculation and debordering.

**1. Fixed-parameter Debordering of Waring Rank (March 2024)**
*   **Authors**: P. Dutta, F. Gesmundo, C. Ikenmeyer, G. Jindal, V. Lysikov.
*   **Reference**: *41st International Symposium on Theoretical Aspects of Computer Science (STACS 2024)*, pp. 30:1-30:15 / arXiv:2401.07631 [cite: 7, 8].
*   **Relevance**: This peer-reviewed result explicitly addresses the gap between Waring rank ($WR$) and border Waring rank ($\underline{WR}$). The authors provide the first Waring rank upper bound that is exponential *only* in the border Waring rank and linear in the degree, overcoming previous bounds that were exponential in the degree itself [cite: 7, 9]. This is critical substrate training-corpus data for defining the topological closures of $W_{d,r} = \{g \in \mathbb{C}[x]_d \mid WR(g) \le r\}$ [cite: 7].

**2. Superexponential Upper Bounds for Determinant Tensor Rank (November 2024)**
*   **Authors**: R. Houston, A. P. Goucher, N. Johnston.
*   **Reference**: *Combinatorics, Probability and Computing*, Vol. 33, Iss. 6, pp. 769–794 (Published Nov 2024, arXiv:2301.06586) [cite: 10, 11].
*   **Relevance**: This work refines the upper limits of the tensor rank and Waring rank of $det_n$. They prove that the tensor rank of $det_n$ is bounded above by the $n$-th Bell number $B_n$, a superexponential improvement over previous best-known bounds for $n \ge 4$ [cite: 11, 12]. 
*   **Exact Sporadic Result**: They compute unconditionally that the tensor rank of the $4 \times 4$ determinant over $\mathbb{F}_2$ is exactly 12 [cite: 10, 13]. They also improve the best-known upper bounds for the Waring rank of the determinant for $n \ge 17$ [cite: 14].

**3. Border Rank of the $4 \times 4$ Determinant (October 2025)**
*   **Authors**: J. Han, J.-H. Ju, Y. Kim.
*   **Reference**: *Recursive Koszul flattenings of determinant and permanent tensors*, arXiv:2510.11051 (also tracked as arXiv:2503.12032) [cite: 15, 16].
*   **Relevance**: Building on the Conner-Harper-Landsberg fixed ideal theorem methodology [cite: 15, 17], this preprint announces an exact invariant calculation for $det_4$.
*   **Exact Theorem Statement**: "Theorem 1.1. The border rank of $det_4$ is 12 over any subfield of $\mathbb{C}$." [cite: 15]
*   **Flag**: This is an *announced-not-published* result (preprint status). The claim relies on extensive computational enumeration of parametrized families of ideals invariant under a Borel subgroup [cite: 15]. It should be flagged as conditional on peer-review verification, though the underlying methodology (Conner-Harper-Landsberg border apolarity) is well-established.

*Behavior Delta*: Instantiate work-queue entries to update $det_n$ upper-bound scaling laws to Bell numbers (Houston et al. 2024). Add $\underline{R}(det_4) = 12$ as a conditional Tier-B primitive. 

---

## (c) FALSE-FORM RECURRENCE

The primary threat to the Prometheus substrate is invariant collapse. The literature exhibits two massive gravity wells surrounding the $3 \times 3$ permanent that frequently induce false-form recurrences.

### Gravity Well 1: VNP vs VP Inversion (The Complexity Macro-Narrative)
Because the generic permanent is VNP-complete and the generic determinant is VP-complete, LLMs and generalized mathematical literature exhibit a strong gradient toward asserting that $per_n$ possesses higher complexity invariants than $det_n$ at all scales.

**False Form**: "The Waring rank / Tensor rank of $per_3$ is strictly greater than that of $det_3$."
**Recurrence / Reality Check**: This macro-narrative completely fails at $n=3$. The substrate must encode an explicit anti-anchor to surface this inversion. 
*   $WR(per_3) = 16$ [cite: 3] vs. $WR(det_3) = 18$ [cite: 6].
*   Product rank of $per_3 = 4$ vs. Product rank of $det_3 = 5$ [cite: 18].
Therefore, at small dimensions, the determinant is the strictly "harder" polynomial. The anti-anchor pin must explicitly forbid asymptotic heuristics from overwriting sporadic dimensional data.

### Gravity Well 2: The HARD-5 Coordinate Collapse (Tensor Rank vs. Product Rank)
A catastrophic false-form recurrence in non-specialist literature is the interchangeable use of "tensor rank of $per_3$". There are two mathematically distinct tensors here, and merging them poisons the knowledge graph.

**Distinct Coordinate 1: Product Rank (Chow Rank)**
When $per_3$ is viewed as a polynomial $F = \sum \prod L_{ij}$, the minimum number of products of linear forms required to express it is its product rank (or Chow rank). 
*   *Literature fact*: "The product rank of the $3 \times 3$ determinant $det_3$ is 5, and the product rank of the $3 \times 3$ permanent $perm_3$ is 4. As a corollary, we obtain that the tensor rank of $det_3$ is 5 and the tensor rank of $perm_3$ is 4." (Ilten & Teitler, 2018) [cite: 18]. 

**Distinct Coordinate 2: Symmetric Tensor Rank**
When $per_3$ is viewed as a symmetric tensor embedded in $S^3(\mathbb{C}^9) \subset (\mathbb{C}^9)^{\otimes 3}$ (equivalent to the Kronecker square of the small Coppersmith-Winograd tensor $T^{\boxtimes 2}_{cw,2}$), its tensor rank $R$ and border tensor rank $\underline{R}$ are different invariants.
*   *Literature fact*: Conner, Huang, and Landsberg (2021) proved that the border tensor rank of $T^{\boxtimes 2}_{cw,2}$ (which equals $per_3$) is 16 [cite: 19]. 
*   Because $\underline{R}(per_3) \le R(per_3) \le WR(per_3) \le 16$, it rigorously follows that $\underline{R}(per_3) = R(per_3) = WR(per_3) = 16$ [cite: 3, 19].

**The False Form Asserts**: "The tensor rank of $per_3$ is 4, but its Waring rank is 16, disproving Comon's Conjecture for $per_3$."
**Correction**: This is a lethal category error. The "tensor rank = 4" refers to the *Chow/product rank*. When evaluated correctly as a symmetric tensor, $R(per_3) = 16$ and $WR(per_3) = 16$. Conner et al. explicitly note: "While Comon's conjecture was shown to be false in general by Shitov, Theorem 1.1 shows that both versions [rank and border rank] hold for $per_3$." [cite: 19]

*Behavior Delta*: Deploy an aggressive anti-anchor pin forcing the substrate to ask "Which tensor rank?" whenever $per_3$ or $det_3$ is queried. Catalog filters must reject any LLM generation that states Comon's conjecture fails for $per_3$.

---

## (d) RECOMMENDATION

Based on primary source verification and rigorous adherence to the Prometheus HARD-5 constraints, the following actions are mandated.

**(i) Anti-Anchor Status & Refinement**
The candidate `WaringRankWitness Tier-B sub-type supporting lit (T#22 Shitov 2021 perm_3=16)` is **CORRECT AS STATED** but requires immediate refinement. 
*   **Refinement**: Elevate Shitov 2021 (SIAM J. Appl. Algebra Geom.) [cite: 1] from Tier-B (preprint) to Tier-A (peer-reviewed) for $WR(per_3)=16$. 
*   **Inversion**: Relegate the associated $WR(det_3)=18$ [cite: 6] to Tier-B, as it remains a viXra preprint (2010.0193).
*   **Coordinate Guardrail**: Attach a HARD-5 warning to the anchor prohibiting the conflation of $WR(per_3)=16$ with the Chow/Product rank of 4.

**(ii) New Sub-Anchors Discovered**
During verification, three high-value primitive sub-anchors were identified and must be registered:
1.  **Comon's Conjecture Exception Sub-Anchor**: Despite Comon's Conjecture being false in general over $\mathbb{R}$ and $\mathbb{C}$ (Shitov 2018/2020) [cite: 1, 20], it *holds* for $per_3$. Both exact and border symmetric ranks equal their regular tensor rank counterparts ($16 = 16$) [cite: 19].
2.  **Border Rank $det_4$ Sub-Anchor**: Register $\underline{R}(det_4) = 12$ over $\mathbb{C}$ (Han, Ju, Kim, Oct 2025) as a Tier-B conditional invariant [cite: 15]. 
3.  **VNP/VP Micro-Inversion Sub-Anchor**: Explicitly encode that $det_3$ strictly dominates $per_3$ across all known tensor and polynomial rank coordinates, directly countering the asymptotic complexity gravity well.

**(iii) Verification Queue Additions**
Create the following work-queue entries for the multi-agent substrate:
1.  **Queue Entry**: Verify the proof architecture of Han, Ju, Kim (2025) [cite: 15]. Confirm whether the Borel-subgroup invariant ideal enumeration fully resolves the $\underline{R}(det_4)=12$ lower bound without unstated characteristic restrictions.
2.  **Queue Entry**: Audit the substrate's training corpus for occurrences of "tensor rank of the determinant is $O(n \cdot n!)$". Replace with the Houston, Goucher, Johnston (2024) [cite: 10] Bell number $B_n$ superexponential bounding law.
3.  **Queue Entry**: Catalog the fixed-parameter debordering methodology from Dutta et al. (STACS 2024) [cite: 7] as a standard topological tool for transitioning between $WR$ and $\underline{WR}$ bounds in future algebraic complexity proofs.

**Sources:**
1. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5kuW_eG4BC0k7x-zZ9tqUdRaBsFQb9ZSHYuXjUhYLTsROu4nVTR7AMuT1POJ7G8lW4DQ8ewk2CCOB7oqf4uEhQwHKNJtaOqFpFeyNtNt5qSPUDpTanC8SJT_j2VxOYAsB2g==)
2. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxXAw-_6A1q2bcT5x9mS6pT_TYalULwVUh9Gt003jeumcF-ru1zjcCrsOydczrKs2VVJLmEqBCF7IA5QwBU2gxHF5hM7H_qOCNjozuev4w-ifj9XY=)
3. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEH_QL_c0VDYToJQClQ5MBtXm7FiNTXeJfFJtpZ1oQyMoezVZONhe1felXhEgXNFCUoTxSq8Ave4OVULXeco_j5tp0wvUtKd1YhVUEmMhmhKromrFtDQva7Np0=)
4. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUQneYBuqZ1Hn7ZLxKpJV3wOXddupwdQVvSKZ6gPJ8CbrlRqRUMp-8EyviRU5_AcXDSposr2_UeGeXOWgduEhdxHa_LhLZcJFU7M2nFyX9CYuUUAvjziOglr9fDIeZYRbzCMPp-IioRgIF66NOrxMzUmUJ5SuT85GP8l1v4SkBsrAcFg==)
5. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESGpBYsSzpW9xFTXQv3XKgyW3vujuv9f1SgAC1eQemHFxiDXbQ7uE6EhAgknzIpEAogb7WwcOYRgXxTxqYNZO7px7Ov_rZVAPJzEzSa1qS2QFWHR5m-IPcY9XlF4r3Ww==)
6. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyNZ17Mryv1Gjj3jsJ2rUgVvaemwPS0s4SolDQVHqPOdAfL3KmG_m1wf3JWq8tEbuzwro4bG3afGTMvI8dkQ5iDQhT4YOwIES0w-5xLiNdlZ_ARAUnkdb6gQU=)
7. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKGPnkgZV-iq9YVMY1ByPlq24qUxcOM1yRkmCp25A7Jv86-WalMwNykuWfTkuYR7hxPqeTssOfO9Ikum9Qy2-fomTMzrhGQw3HxBpU9lN4itnr6n2lzSN37ySB6Kkv-evmY7w1ZcMg4oZloWsZ5KzD2DP91Gkm-CK-T7jYjiel9EXPpWkD0kG3dM2D9bFHODN9V0zNE89EL_BiprmUzno5lnG_QYE=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXry-QE2NIrwgNaRCcS81BgpnkPtui1KFAQtGUyKxKYSkJywLpsSlS84jWIkvBbEDPzodh-DnmBmO7LLXfOYO2WTvvrX44coiR2rT8anaZeZezxh0g)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvPmaNlY9XVeFo0tzQpCon2yRT1tgemu03Ci__hRtj8nJLuOSUmch823irdiKdG0DbDYo1HNuMVGPgZdD9TvrejHIi207U_HrMVKzgrJhmwG7waygU)
10. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWLn-f_M1uVm4HeBg5NdY8QJFFagEZ2EN2OlSs8XOANEzNDs9PcCZO8gsb-wWWpu0M2dM0Be3_HzTPpcZbcfaYQXn1nk9OA9elaTTlyek1fjXThJnEUbTKf8EeiR0t5g4-FESV8ZDhuiMbnUjgaLo1VaD6a8EZACvPt_m9LqpKIN7ItK2snXkZhnhAbxnGNBPSrbrclfVLKC3gMVrEP9gJMllGBjZGRL1lmvijmQVHzQMKoIYmYz8VswyWzEtqckHgc5CGb0gaedVncvNS014HthsVHVGL9YRpGm-Dwd-gBOIq_kMG_TEpQMIj0cbizJPPk-Q_lcF3YA==)
11. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH9K2k75arFk2cSoNA-Sc-xYZaqWC1yND-1BYUX8_JknFOVgj-26QX5fnL-SPhc46qK0mp6I9sYJXWASPlfD_fPHCyVt1oJZhBW9q9POOR5Y0P6aQCiGb6kVC-Z-ftmlPIvnsRzjTTG_2rblrqxtHtBTZo3ing2IZxnpOspYfOAVopUu0J4RegNQXlsEjm01jKmP0lUUcVXytnH25Jt9AhcfROj11rJwwmeWS3X4UxdWAFb3QLj-_4PZL7UVO1OVr4up90iSuBzsAkvfvatwB4xBsM1_qyaqqbe8kkLgTHqi0ixPfdsUdhFw_Li0_vlahOCDQEy7uvbGu77oVMbHzzYXn_)
12. [njohnston.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB8w_C_Dwi6W5Kl20Z_zmvrdzr21y2ogeYidyN8kRim0Pft0ySEqAH5lcWHwc9M1W-p7z-SMqVI3K5bCNGQ5gL_ggdFXci8hh7yqljrBLoxKjzFWDkkeFaisJOaQ77vRM=)
13. [njohnston.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8CT_1ughO5JgxgHAC1DmTAb6Ld5TKsZa0XMMSV719vzlCOlBkppOgLBgnSIXvoGv8iwXIJq7OTnmEPr9Loz20h01m1BjTGQK5PzgzDG9dUjbPH85bexODpRFvcg3pr1Pn2mqQl3TkShRDTrL_aB2SfEbAepumPqZpOkOR6LOZrATJeKQdiixxV8QSXjqY-tjJqexzEpIg8uMxR3jTXOyr6Je4)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzULKGeY8_34uIt1_M0slaw3_ss-T2M40fEiNTkLqHZuIJFFv0NWZad_nHLNKyXHyh1s3JLuTymhuxmtpXbn80PErtjwVVroglRriU09dsZMEdbqHT)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhnowyPPAUs6MQMF7iab1lA-Bx7c7AIOUiJCtXsPTP_yDAV5bbOU_IvgaNDmkC1qE_Qr4RE31wxVq4Tx18mIl5YkDCJrekdLN3Lthqi5Sfh1PR5zSf)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTDE3t1Bqdc2UzKia4bUHfc5ebVtDIvGNRzLmstgBJVUxlChUIPd6mwPYRaXhBmSS9ncpplWSCTGscG-6rhnmMcdHshUwV0U6FLWPYN9A-5UM6Y6oR)
17. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUK_ZRSpvbN92RqzETGUv0Qux52mw3KNnu8KwwNVNhXchzAu9_ly5h5ums0HOcqflA560XpuVecRTwHXyL1yC9Angd9vMXTKcSF-aFV8vHvG6h7HGQ2ZF02hpPG5yiDIo=)
18. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGx8ct8U3UubGl19IbXcNSYqI6IlyLKqTyMrt2mL3ZfNZhoWByAJTtx-Gw_h8a2cFfes4MxFMb70D7YWtV07GIR-0VTlSYRAb5I3CbxFUy0ZUd0NARRdqwChOObYY1lFRoLG1-rKl6rIo9BbglaYM1IZRbPb_vbenCa1SAggUIA_D_6m8-fByOFDhjT_MWmENjtZAuqr2oTtewUCztDWasV3TgDfFFbjLXMEuEs0o2h2UGSyGNHdPuefxFNy0G0Q0s_hOzA1vXP22Hu2GrBtKBxC205NCjiCsc=)
19. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyCNwZa0ngfufXpGtbgGWCqIIGkAYeCbdo9X5r_ZOcshkChoYYI-4R9Yyh8JoMVmmvY4QHg-nuCb2jtnM6N10zgdwG21eHPIPpQtQOLmQmcPd5duP75gBoZV20aQEfDuu3t7th)
20. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa-QL1f50JbNcNe3jMHP6ee57hIXutF-WMUuCPxCVEEh8KXFHFHsLCs4CWL1o_RSEDBhHaH5xj8fLy_l6-G-X_bqf4yO52-HLf_3pAS-pKOhiZLWOtubgdblU=)


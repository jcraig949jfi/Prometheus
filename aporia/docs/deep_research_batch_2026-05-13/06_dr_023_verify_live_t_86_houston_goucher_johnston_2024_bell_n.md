# Prompt 06: DR-023 — VERIFY-LIVE T#86 Houston-Goucher-Johnston 2024 Bell-number det bound + Han-Ju-Kim 2025 det_4=12 perm_4=8

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdCUzhFYXF6Rkp1NmZfdU1QbDRMY29BdxIXQlM4RWFxekZKdTZmX3VNUGw0TGNvQXc
**Elapsed:** 1151s

---

# Anti-Anchor Verification Report: T#86 Tensor Rank Bounds for Determinant and Permanent

**Key Points:**
*   **Coordinate Separation Mandate**: The candidate input merges tensor rank ($\text{Trank}$) characteristics across distinct underlying fields. Houston-Goucher-Johnston (2024) resolves $\text{Trank}_{\mathbb{F}_2}(\det_4) = 12$, while Han-Ju-Kim (2025) resolves $\text{Trank}_{\text{char} \neq 2}(\det_4) = 12$ and $\text{Trank}_{\text{char} \neq 2}(\text{perm}_4) = 8$. These must be tracked as distinct coordinates.
*   **Border Rank Distinctness**: Follow-on work strictly separates border rank ($\text{brank}$) from tensor rank ($\text{Trank}$). Han-Ju-Kim (October 2025) establishes $\text{brank}_{\mathbb{C}}(\det_4) = 12$, matching the tensor rank but requiring entirely divergent proof mechanics (fixed ideal theorem vs. recursive Koszul flattening).
*   **Universal Upper Bound**: The Houston-Goucher-Johnston (2024) bound $\text{Trank}(\det_n) \le B_n$ (the $n$-th Bell number) definitively overwrites legacy $O(n!)$ bounds across all characteristic fields. 

**Substrate Context & Operational Impact:**
The verification of these exact tensor invariants is critical for the maintenance of the Prometheus mathematical substrate. Currently, the substrate's tensor complexity catalog (`T#86`) evaluates algebraic bounds to map the landscape of computational complexity. Failure to isolate tensor rank ($\text{Trank}$), border rank ($\text{brank}$), and Waring rank ($\text{Wrank}$) as orthogonal coordinates risks catastrophic dimensionality collapse in downstream theorem-proving vectors. The findings evaluated below serve as direct inputs for anti-anchor pins, primitive registrations, and catalog edits to overwrite legacy heuristics with primary-source-anchored integer exactitudes.

**Anti-Gravity Well Directive:**
Standard complexity literature exhibits a strong gravity well toward framing the determinant and permanent solely within the Valiant algebraic complexity paradigm ($\text{VP}$ vs. $\text{VNP}$), often collapsing the structural tensor properties into monolithic proxies for arithmetic formula size ($L$) or determinantal complexity ($\text{dc}$). We explicitly resist this framing. The tensor rank $\text{Trank}(\det_n)$, the border determinantal complexity $\overline{\text{dc}}(n)$, the Waring rank $\text{Wrank}(\det_n)$, and the slice rank of the associated polynomials are mathematically distinct coordinates. The results verified here isolate properties of the specific tensors in $(V^*)^{\otimes n}$ and do not automatically resolve generalized lower bounds for affine projections without separate, specific linkage primitives.

***

## (a) PRIMARY SOURCE CONFIRMATION

The candidate `VERIFY-LIVE T#86 Houston-Goucher-Johnston 2024 Bell-number det bound + Han-Ju-Kim 2025 det_4=12 perm_4=8` is confirmed against the primary literature. However, the precise mathematical conditions governing the fields of characteristic $2$ versus characteristic $\neq 2$ must be registered distinctly in the substrate.

### 1. The Bell-Number Bound and Characteristic 2 Exactitude
**Primary Source:** Houston, R., Goucher, A. P., & Johnston, N. 
**Title:** *A new formula for the determinant and bounds on its tensor and Waring ranks*
**Publication Status:** **PEER-REVIEWED**
**Date of Definitive Publication:** September 18, 2024 
**Journal Reference:** *Combinatorics, Probability and Computing*, 33(6), 769–794. DOI: 10.1017/S0963548324000233 [cite: 1]. (Preprint originally announced January 16, 2023, arXiv:2301.06586 [cite: 2]).

**Extracted Result Specifications:**
The authors construct a novel explicit combinatorial formula for the determinant utilizing partial partitions, which contains superexponentially fewer terms than the standard Leibniz formula. This yields UNCONDITIONAL upper bounds for the tensor rank ($\text{Trank}$) and Waring rank ($\text{Wrank}$) of the determinant tensor $\det_n$.

*   **Universal Tensor Rank Bound:** $\text{Trank}(\det_n) \le B_n$, where $B_n$ is the $n$-th Bell number. This holds regardless of the underlying field $\mathbb{F}$ [cite: 1, 3].
*   **Waring Rank Bound:** $\text{Wrank}(\det_n) \le 2^{n-1} B_n$. This upper bound significantly supersedes previously known bounds when $n \ge 17$ [cite: 1].
*   **Characteristic 2 Optimization:** Over fields of characteristic $2$ (where the determinant and permanent polynomials are algebraically equivalent due to the irrelevance of sign alternations), the bound tightens to $\text{Trank}(\det_n) \le 2^n - n$ [cite: 1].
*   **Exact Coordinate for $n=4$ ($\mathbb{F}_2$):** The authors demonstrate that over the field of two elements ($\mathbb{F}_2$), the tensor rank is exact: $\text{Trank}_{\mathbb{F}_2}(\det_4) = 12$ [cite: 1, 3]. 

### 2. The Arbitrary Characteristic Exactitude
**Primary Source:** Han, J. I., Ju, J.-H., & Kim, Y.
**Title:** *Recursive Koszul flattenings of determinant and permanent tensors*
**Publication Status:** **ANNOUNCED-NOT-PUBLISHED**
**Date of Preprint:** March 15, 2025
**Reference:** arXiv:2503.12032 [cite: 4, 5].

**Extracted Result Specifications:**
This work resolves the exact tensor rank coordinates for the $4 \times 4$ determinant and permanent over fields where signs do not collapse (characteristic $\neq 2$). It strictly employs algebraic geometry rank methods—specifically, recursive usage of the Koszul flattening method introduced by Landsberg-Ottaviani and Hauenstein-Oeding-Ottaviani-Sommese—rather than purely combinatorial constructions.

*   **Exact Coordinate for $\det_4$ (char $\neq 2$):** $\text{Trank}_{\text{char} \neq 2}(\det_4) = 12$ [cite: 4].
*   **Exact Coordinate for $\text{perm}_4$ (char $\neq 2$):** $\text{Trank}_{\text{char} \neq 2}(\text{perm}_4) = 8$ [cite: 4].
*   **Separation Theorem:** The authors provide UNCONDITIONAL lower bounds on $\text{Trank}(\det_n)$ that completely separate the determinant and permanent tensors by their tensor ranks asymptotically: $\text{Trank}(\text{perm}_n) \le 2^{n-1} < n^{n-1}/(n-1)! \le \text{Trank}(\det_n)$ for every $n \ge 3$ [cite: 4].

**Substrate Translation:** The candidate text correctly maps the authors and the numerical findings. However, the substrate must register two distinct tensor rank primitives: $\text{Trank}_{\mathbb{F}_2}(\det_4)$ (Houston et al., 2024) and $\text{Trank}_{\mathbb{C}}(\det_4)$ (Han et al., 2025). Despite arriving at the numerical integer $12$ in both cases, the base field coordinates govern radically different tensor decomposition topologies.

***

## (b) FOLLOW-ON WORK (2024-2026)

In the immediate 24-month window surrounding these results, literature rapidly evolved to constrain orthogonal tensor invariants, prominently border rank ($\text{brank}$) and real topological rank ($\text{Trank}_{\mathbb{R}}$). The substrate must ingest these as distinct coordinate axes.

### 1. Border Rank Resolution (October 2025)
**Primary Source:** Han, J. I., Ju, J.-H., & Kim, Y.
**Title:** *The border rank of the $4 \times 4$ determinant tensor is twelve*
**Publication Status:** **ANNOUNCED-NOT-PUBLISHED**
**Date of Preprint:** October 13, 2025
**Reference:** arXiv:2510.11051 [cite: 6, 7].

This preprint addresses the border rank $\text{brank}(\det_4)$, which is mathematically distinct from tensor rank. Border rank defines the smallest integer $r$ such that the tensor can be expressed as the *limit* of a sequence of tensors of rank $r$. Because the Zariski closure of the set of tensors of rank $\le r$ is not necessarily equal to the set itself, border rank is frequently strictly smaller than tensor rank. 
*   **Result:** The authors prove UNCONDITIONALLY that $\text{brank}_{\mathbb{C}}(\det_4) = 12$ over the complex numbers [cite: 7, 8]. 
*   **Mechanics:** To prove this lower bound, the authors do not use recursive Koszul flattenings. Instead, they apply the fixed ideal theorem introduced by Buczyńska-Buczyński and utilize the systematic border rank criterion method of Conner-Harper-Landsberg to rule out $\text{brank}(\det_4) \le 11$ [cite: 7]. 

**Substrate Note:** Flag any literature claiming "Han-Ju-Kim proved the rank of the $4 \times 4$ determinant is 12" as ambiguous. The substrate must enforce the HARD-5 distinction: `arXiv:2503.12032` registers to the coordinate `TensorRank`, whereas `arXiv:2510.11051` registers to the coordinate `BorderRank`.

### 2. Topological Lower Bounds for Real Tensor Rank (September 2025)
**Primary Source:** Avvakumov, S., & Karasev, R.
**Title:** *Tensor rank of the determinant and periodic triangulations of $\mathbb{R}^n$*
**Publication Status:** **ANNOUNCED-NOT-PUBLISHED**
**Date of Preprint:** September 26, 2025
**Reference:** arXiv:2509.22333 [cite: 9].

Avvakumov and Karasev approach the tensor rank from a topological perspective, analyzing $\mathbb{Z}^n$-invariant periodic triangulations of $\mathbb{R}^n$. 
*   **Result:** They establish a lower bound for the real tensor rank: $\text{Trank}_{\mathbb{R}}(\det_n) \ge n^{n-1} / (n-1)!$ [cite: 9].
*   **Interaction with Houston et al.:** Avvakumov and Karasev explicitly cite the Houston-Goucher-Johnston 2024 Bell-number bound ($B_n$), highlighting that their topological lower bound is bounded from above by $B_n$, which is asymptotically bounded by $(n / (e^{1-\epsilon} \ln n))^n$ [cite: 9]. This confirms successful propagation of the Houston et al. upper bound into algebraic topology domains, superseding legacy limits.

### 3. Anti-Gravity Well Corrections
During the ingestion of 2024-2026 follow-on works, the substrate must actively filter "Y proved X" claims that conflate tensor decomposition with computational formula construction. Specifically, generating a tensor decomposition of rank $12$ for $\det_4$ does not mean arithmetic formula size $L(\det_4)$ collapses proportionally. The tensor rank $\text{Trank}$ applies exclusively to the homogeneous multilinear geometric object in $V_1 \otimes V_2 \otimes \dots \otimes V_n$, whereas formula size permits intermediate operational node reuse and arbitrary depth hierarchies. We register these coordinates as strictly orthogonal.

***

## (c) FALSE-FORM RECURRENCE

A search of the literature surrounding computational complexity and multilinear algebra reveals that the false form—specifically, the assertion that the tensor rank of the determinant is bounded merely by Derksen's formula $(5/6)^{\lfloor n/3 \rfloor} n!$ or remains unknown beyond naive $n!$ limits—recurs in peripheral domains that have not yet synchronized with the 2024 combinatorial results.

**1. Historical Anchor Recurrence:**
Prior to the definitive 2024 publication by Houston et al., standard literature defaulted to historical heuristics. As recorded in archival discussions (e.g., MathOverflow 2012), Derksen's identity bounded $\text{Trank}(\det_4) \le 20$, while Glynn's identity bounded $\text{Trank}(\text{perm}_4) \le 8$ [cite: 10]. The discrepancy for the determinant arose because naive Laplace expansion across minors yields suboptimal tensor decompositions. 
While core tensor algebra researchers updated their bounds in 2024-2025 (as seen in Avvakumov & Karasev citing $B_n$ [cite: 9]), adjacent fields investigating quantum many-body physics or neural network associative memory matrices frequently invoke the outdated $O(n!)$ bounds when discussing the intractability of determinantal and permanent tensors in their scaling limits.

**2. Ambiguous Field Characteristic Collapse:**
A secondary false form observed in preprint literature is the failure to distinguish the base field when citing tensor ranks. A claim such as "Houston et al. proved $\text{Trank}(\det_4) = 12$" is a mathematically incomplete statement. Houston et al. proved it is $\le 15$ generally via the Bell number combinatorial partition, but exact equality to $12$ was verified strictly over $\mathbb{F}_2$ via exhaustive computer search [cite: 1, 11]. It required the algebraic machinery of Han-Ju-Kim (2025) to prove $\text{Trank}(\det_4) = 12$ over $\mathbb{C}$ and other characteristics strictly not equal to $2$ [cite: 4].

Therefore, the anti-anchor is urgently needed. If the substrate does not explicitly pin the characteristic coordinates and the temporal updates, language models and theorem-proving agents will fall back into the gravity well of citing Derksen's $O(n!)$ bound or conflating $\mathbb{F}_2$ exactitudes with $\mathbb{C}$ exactitudes.

***

## (d) RECOMMENDATION

**1. Correctness and Necessary Refinements of the Anti-Anchor Form**
The candidate anti-anchor `VERIFY-LIVE T#86 Houston-Goucher-Johnston 2024 Bell-number det bound + Han-Ju-Kim 2025 det_4=12 perm_4=8` is fundamentally **CORRECT** but requires rigorous **COORDINATE REFINEMENT** prior to integration into the primary database. It must be split to ensure adherence to the HARD-5 directive separating distinct mathematical invariants. 

The candidate must be partitioned into the following exact mathematical coordinate pins:
*   `Trank_Universal(\det_n) \le B_n` (Houston-Goucher-Johnston, Sep 2024) [cite: 1].
*   `Wrank_Universal(\det_n) \le 2^{n-1}B_n` (Houston-Goucher-Johnston, Sep 2024) [cite: 1].
*   `Trank_{\mathbb{F}_2}(\det_4) = 12` (Houston-Goucher-Johnston, Sep 2024) [cite: 1, 3].
*   `Trank_{\text{char} \neq 2}(\det_4) = 12` (Han-Ju-Kim, Mar 2025) [cite: 4].
*   `Trank_{\text{char} \neq 2}(\text{perm}_4) = 8` (Han-Ju-Kim, Mar 2025) [cite: 4].
*   `brank_{\mathbb{C}}(\det_4) = 12` (Han-Ju-Kim, Oct 2025) [cite: 6, 7].

**2. New Sub-Anchors Discovered During Verification**
During the primary source trace, three highly relevant sub-anchors were identified and must be integrated into the catalog:
*   **SUB-ANCHOR 1:** The real topological lower bound for the determinant tensor rank: $\text{Trank}_{\mathbb{R}}(\det_n) \ge n^{n-1}/(n-1)!$ by Avvakumov and Karasev (Sep 2025, arXiv:2509.22333) [cite: 9].
*   **SUB-ANCHOR 2:** The separation invariant demonstrating that the asymptotic tensor rank of the determinant is strictly bounded below by a function that exceeds the permanent's upper bound: $\text{Trank}(\text{perm}_n) \le 2^{n-1} < n^{n-1}/(n-1)! \le \text{Trank}(\det_n)$ (Han-Ju-Kim, Mar 2025) [cite: 4].
*   **SUB-ANCHOR 3:** The exact border rank lower bound verification mechanism, utilizing the fixed ideal theorem (Buczyńska-Buczyński) coupled with the Conner-Harper-Landsberg criterion, establishing a reusable primitive for $O(4)$ tensors [cite: 7].

**3. Actionable Downstream Consumers and Work-Queue Entries**

*   **Anti-anchor pin:** Dispatch an override pin to discard all heuristic training corpus data claiming $\text{Trank}(\det_n) = O(n!)$ or bounding $\text{Trank}(\det_4) \le 20$. Replace instances with the exact Bell-number bound and integer coordinate values. 
*   **Primitive registration:** Register `TensorRank`, `BorderRank`, and `WaringRank` into the substrate's schema as mathematically un-collapsible coordinate types (HARD-5 compliance). An update to one does not implicitly update the others unless a formal mathematical inequality primitive (e.g., $\text{brank} \le \text{Trank}$) is invoked.
*   **Catalog edit:** Update catalog `T#86` with the exact verified numeric coordinates for the $4 \times 4$ matrices: `(Trank=12, brank=12)` for the determinant and `(Trank=8)` for the permanent.
*   **Work-queue entry:** Instantiate an agentic task to asymptotically evaluate the gap between the new combinatorial upper bound $B_n \sim (n / (e^{1-\epsilon}\ln n))^n$ and the Avvakumov-Karasev real topological lower bound $n^{n-1}/(n-1)!$. Generate a substrate gap-analysis to determine if tighter intermediate geometric bounds exist in unpublished preprint space. Evaluate how the recursive Koszul flattening matrix dimensions scale to $n=5$ against the expected $B_5 = 52$ upper bound.

**Sources:**
1. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEB28jsZCNj-p3yuwJ80Ivyzd-DnwgwZ2Nds1piYFoWtMNxTciO6_RUVJaiN4yRony2zNOxIaCJEkM4ytnWlydPc3hJliE0S9haUHCG1nXiOp5RIBi0xlgQjl7OaMVakyH9ttgZzXGvpNVLhIxb98Lc6HaXMpWTOL9PVGIVlImnZNSzsbBklG6mzkd9uDPu88YgMsEvnlp5AqeBQTmz89Vna-yl5yfRLeE3mcpwDByAhKLtOSPlcJ-oHyZoaMfVTG07EJAIXpQ9estplN8if4tx3RPZF4kSlAjsLkU4ribz5wvdABM5Smcjy8YiXqkyleUbyYbz9SOHbA1TQr5QhbrsPIwyA==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHllzB84yHQ9iGgG7HSfNFN7VJ9EJKTPFKh0UmBvFCbjNm01fTO4zGQAiP6bgXPETTUeF3ziF_uw5xvK1PCXPwlLfAYQRr0qNjZZCRfNN7Fj8J-X8tR-Q==)
3. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzVRlGjZ37uKDgvQc7mfb903jZFBwAvMfxPW9KpaVMI8PVXgu9ZZixNb6NGRRoVlzhuvkmsgtOXrtW7tKZsgfw_afs5Tt94BcXnodR0j6M-1venKyOEFnZfdcr9ckzsBxR2DgdJotL5RuIBfDDkv_rrzTl19rByoXizlqVtR9AedmSbnaPvil8IFZmnL-ryRUNUJfbOYaULfYwr8OWnL_6dFNTbFKDV_PHuo_Euwcm0wnT06TsHeQQ6DQv6gszu7bpny6mjfhQC1nvFA2yjTSbeZoaF0vf3vDASNxCDxIY_F04e95a9XHVSVfCI0KsvLj3GP-Ja6wwl5M=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz05XnXhyDBF3vx4WMfmnvsd6c3Osf941axKus-NbkXttrJRAX602JvgBWFuX2-7zoYk-ZQ13tQSNcxGJ2tMW436l2wjiHYuWbsUmo8_s25q2VkBnTjQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtTQOfGVhUDpkv92SmyDqRUDZDTnilNJtsX45L9E7RNFHGqQSn5Hlln-zHS_2GAuyyRRbhS51UFcZplRbqUE3SO_mzd5Y2_zFc_FaaJrCk9zSOQZU4Wg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXIBKE_FFpUKYtvp_P-AcCFTyYGlbikc-T9Bi4iGTEGLsR9q1Fc0C17XA-u5Cepn2JfJl2MoI6-A11RrV6WjXrUUen5uiRb1Iyjn_Ih-Y5Ch64nj4auw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnV96whngEnFjlpXcle0RZJNoCe4-To6_n08879N_rPjSeg4RVV14MjtIt4iA8g_38YLpw-Zh72PzgvAqanJYWanmY2KOc9t3AT0L9SLI35jMDwbesDA==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzbTsrj2LkH0VcBxMd9EjK4FyU48Rmr2wzuLwaUxAqfxMkVkqcznreoxY4PekypJ1AAfy5Vpn08HU2xIcoyvhinX1JaKmvye7wSU-3w1PZnyzQEtiMpwwhd9ZIe5TwBXqGCMeLLIffVbyYT5J5-2_TUNe3pEukq5thuz2EI4g9Hzr0n97eeXE9UasnvmaWhAMWt_K7FOJJA58FHmgAjtDNSj92l3Lh)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOrAZBfLxlvRrkT2zUPmr7d-5W2I3IlSZs0YwKWuTvLSRBTXphpy8iLEPfwpTqWIy9j8A2udyps3o43IqN6Po4vEvueEB1ddlbl_ZJ31RrsRgn_B6Ja1LGIA==)
10. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMMgdXZPGzHKnErU1JPiN3KYc1tfn5u5eC3dQfE11cm5AU3TK-ddIJt-2FgzcTUuqA7HB_VjZnCbr7O_3jH1VTUgQ_-mEcAAcFrE-iPQbFppC1_nUqCWsnJn8Asnff22BCADS9kFnH9Wfy8wtgheBeDD9YVeyh-W7Puhnwjnvh8zpcv5Y=)
11. [njohnston.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEm1tjI8X2c4O7J4b1Jj_yHFqLr0DCi8ZHUtq42wYX-TanWUxQLY_QG3zmQEsKxzi-t9ik6Jneea7ymUV10yE2WS-KBciS2s_IDb3zNufFRc1h6kprYnhMfNSvORF9Qd4lJLewKSoNaDc_b4kY69yFBvmBjOmcNolYFPcsM4BhKPtRBguWX5X4vWpTYDZM7x-3zDRsijKqoCCjAhJrRyaHYBCRJlQ==)


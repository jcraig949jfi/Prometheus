# Prompt 13: DR-030 — Survey LimitWitness Tier-B sub-type supporting lit (T#43 de Silva-Lim 2008 + 2024-2026 follow-on)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiRUFFYXFHNEQ3U2I5TW9QbjlHMXlBWRIXYkVBRWFxRzREN1NiOU1vUG45RzF5QVk
**Elapsed:** 971s

---

# Anti-Anchor Verification Report: LimitWitness Tier-B Sub-Type (T#43)

**Key Points:**
*   The canonical polyadic (CP) rank of a tensor exhibits severe topological anomalies over \(\mathbb{R}\) and \(\mathbb{C}\); specifically, the set of tensors of CP rank \(\leq r\) is generally not closed for order \(d \geq 3\) and \(r \geq 2\).
*   Consequently, the "best low-CP-rank approximation" is an ill-posed problem: the infimum of the distance function is frequently unattainable, yielding a diverging sequence of limit witnesses where factor matrices trend toward infinity while their sum converges to a tensor of strictly higher CP rank (but lower or equal **border CP rank**).
*   Recent literature (2024–2026) exhibits a high-gravity well, systematically conflating the *topological ill-posedness* of CP rank approximation with the *computational NP-hardness* of exact CP rank determination.
*   Stable substitutes where the Eckart-Young property (or an analogue) holds include **tubal rank** (via t-SVD), **nonnegative CP rank**, and **Tucker rank**. Over \(\mathbb{C}\), generic tensors almost always have a unique best CP rank approximation, distinguishing the complex field from the real field.

The concept of "tensor rank" is a collapsed, overloaded coordinate in conventional machine learning literature. This report unpacks the distinct mathematical coordinates—CP rank, border CP rank, nonnegative CP rank, tubal rank, Tucker rank, and tensor train (TT) rank—to verify the anti-anchor candidate concerning the ill-posedness of low-rank tensor approximation. The findings herein are structured strictly as inputs for the Project Prometheus mathematical research substrate.

***

## (a) PRIMARY SOURCE CONFIRMATION

**Target Anti-Anchor:** The topological ill-posedness of the best low-CP-rank approximation problem. 

**Primary Source Identification:** 
The foundational substrate for this anti-anchor is the work of Vin de Silva and Lek-Heng Lim. The definitive peer-reviewed publication is *Tensor Rank and the Ill-Posedness of the Best Low-Rank Approximation Problem*, published in the *SIAM Journal on Matrix Analysis and Applications* (Volume 30, Issue 3) in September 2008 [cite: 1, 2]. The preprint was originally announced on the arXiv (arXiv:math/0607647) on July 26, 2006 [cite: 3]. 

**Primary Source Theorems & Assertions:**
The primary source explicitly disrupts the automatic extension of the matrix Eckart-Young theorem to higher-order tensors. In matrices (order-2 tensors), the set of matrices of rank \(\leq r\) is closed, guaranteeing that any matrix has a best rank-\(r\) approximation. For tensors of order 3 or higher, de Silva and Lim proved that the set of tensors of CP rank \(\leq r\) is *not* closed [cite: 1, 3].

Key assertions verified from the primary source:
1.  **Positive Volume of Ill-Posedness:** The failure of existence for a best rank-\(r\) approximation is not an isolated, degenerate edge case. The authors demonstrated that "in many instances these counterexamples have positive volume: they cannot be regarded as isolated phenomena" [cite: 1, 3].
2.  **Norm Independence:** The non-existence of a minimum distance tensor does not rely on a pathological choice of metric. The ill-posedness holds "regardless of the choice of norm (or even Bregman divergence)" [cite: 1, 3].
3.  **The Diverging Components Phenomenon:** When a true solution does not exist, numerical optimization algorithms attempting to find a best CP rank-\(r\) approximation will generate sequences where individual rank-1 components grow unboundedly in norm, but their sum approaches the target tensor. The limit of this sequence is a tensor whose **border CP rank** is \(\leq r\), but whose **CP rank** is strictly greater than \(r\) [cite: 1, 4].
4.  **Rank Coordinate Distinction:** The primary source makes an exception for rank-1 tensors and order-2 tensors, where the best approximation is well-posed [cite: 1, 3].

**Status of Primary Source:** UNCONDITIONAL and PEER-REVIEWED. The results have not been withdrawn or supplanted; rather, they form the bedrock of the "LimitWitness Tier-B" sub-type, defining the conditions under which limit-point tensors exhibit strictly higher CP rank than the sequence approximating them.

***

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month window from 2024 to 2026 demonstrates an aggressive expansion of alternative tensor coordinates designed to act as "stable substitutes" that sidestep the LimitWitness topological anomaly. We register these substitutes below, enforcing the HARD-5 doctrine to maintain distinct mathematical invariants.

### Coordinate 1: Nonnegative CP Rank
The inclusion of nonnegativity constraints drastically alters the topology of the approximation space. In a February 2025 paper published in *Computational Optimization and Applications* titled "Nonnegative approximations of nonnegative tensors", Xia et al. proved that restricting both the target tensor and the rank-1 factors to the nonnegative orthant neutralizes the ill-posedness [cite: 5]. 
*   **Result:** The nonnegative CP decomposition (also known as nonnegative tensor factorization) operates over a closed set. As stated in the 2025 follow-on literature, "the optimal low-rank approximation under nonnegativity constraint always exists... and is almost always unique" [cite: 5]. 
*   **Substrate Input:** `[Primitive Registration: NonnegativeCPRank]` — Topologically closed. Eckart-Young equivalent holds under nonnegativity.

### Coordinate 2: Tubal Rank and t-SVD
The tubal rank, derived from the tensor singular value decomposition (t-SVD) based on the t-product (and generalized \(\star_M\)-products), serves as a highly active stable substitute in 2024-2026. 
*   **Result:** Keegan and Newman (June 2025, *Demystifying Tubal Tensor Algebra*) and Horesh (March 2026, *SIAM News: Don't Matricize, Tensorize*) demonstrate that the t-SVD permits an exact Eckart-Young optimality theorem [cite: 6, 7]. 
*   **Coordinate Distinction:** Unlike CP rank, which expresses a tensor as a sum of outer products of vectors, tubal rank measures the number of non-zero singular tubes in the Fourier domain (or general invertible linear transform domain). Because t-SVD relies on orthogonal tensor factors and f-diagonal tensors under a specific algebraic structure, the truncated t-SVD is strictly bounded and the low-tubal-rank sets are closed [cite: 6, 7]. Horesh explicitly notes in 2026: "determining the CP rank is NP-hard... [but] the truncated t-SVD produces the best low-tubal-rank approximation... We call the t-SVD the 'holy grail' of data analysis" [cite: 6].

### Coordinate 3: Complex CP Rank (Almost Everywhere Well-Posedness)
A critical coordinate split occurs between the real field \(\mathbb{R}\) and the complex field \(\mathbb{C}\).
*   **Result:** Building on earlier foundational work, follow-on literature (e.g., referenced in late 2024 contexts and presentations [cite: 8, 9]) confirms that over the complex field \(\mathbb{C}\), any generic tensor *almost always* has a unique best CP rank-\(r\) approximation [cite: 8, 9]. 
*   **Coordinate Distinction:** The non-existence of best low-rank approximations occurs with positive volume over \(\mathbb{R}\). However, over \(\mathbb{C}\), the set of tensors that fail to have a best rank-\(r\) approximation forms a lower-dimensional algebraic variety (measure zero). Thus, the ill-posedness is field-dependent [cite: 9, 10].

### Coordinate 4: Tensor Train (TT) Rank and Tucker Rank
When computational optimization hits the CP rank ill-posedness barrier, researchers frequently substitute Tucker rank or TT rank, mapping the problem to matrices via unfolding.
*   **Result:** Tang and Yang (February 2025, *Journal of Industrial & Management Optimization*) address tensor completion using TT rank [cite: 11, 12]. The TT rank is defined as a vector of ranks of balanced unfolding matrices \((rank(X_{[cite: 8]}), \dots, rank(X_{[d-1]}))\). Because it is a vector of matrix ranks, TT rank minimizes over a closed set, rendering the best-approximation problem topologically well-posed [cite: 11].
*   **Flagged Claims:** Literature frequently proposes the "Tensor Nuclear Norm" (TNN) as a convex surrogate. However, Su et al. (January 2025, *Electronics*) note that "relying solely on the tensor nuclear norm can lead to suboptimal solutions because of the convex relaxation of tensor rank" [cite: 13]. In December 2024 (*Applied Sciences*), Mei et al. further argued for non-convex nonlinear transformations (LRANNT) over standard TNN [cite: 14, 15]. These surrogate methods (TNN, weighted Laplace functions) are computationally stable but strictly approximate the **Tucker/tubal rank**, *not* the **CP rank** [cite: 15, 16]. 

***

## (c) FALSE-FORM RECURRENCE

A persistent gravitational well in the literature is the conflation of **Topological Ill-Posedness** with **Computational Complexity (NP-Hardness)**. When addressing why CP rank approximation is difficult, authors routinely cite NP-hardness as the reason numerical optimization fails, completely ignoring the fact that the minimum simply does not exist in the space. 

**Instances of False-Form Assertion (2024-2026):**

1.  **Conflation of NP-Hardness and Ill-Posedness:**
    In the December 2024 paper *Nonconvex Nonlinear Transformation of Low-Rank Approximation for Tensor Completion* published in *Applied Sciences*, Mei et al. assert: 
    > "The CANDECOMP/PARAFAC(CP) rank is determined by the count of the smallest rank-1 tensor... Nevertheless, solving the CP rank of a tensor is NP-hard, and there is still no optimization algorithm that solves the CP rank directly." [cite: 15]. 
    
    *Critique for Substrate:* This represents a fundamental category error. NP-hardness (a property established by Håstad in 1990 for exact computation over finite fields and \(\mathbb{Q}\)) implies that finding the exact minimal \(r\) takes exponential time. However, the reason "there is no optimization algorithm" for best CP rank approximation is not solely because it is NP-hard, but because the limit point is undefined—the problem is topologically ill-posed. An optimization algorithm cannot converge to a minimum that does not exist in the set [cite: 1, 15]. 

2.  **Assumption of Eckart-Young for CP Rank:**
    A medium blog/tutorial indexed in August 2024 attempts to explain CP decomposition by directly parallelizing matrix SVD: 
    > "Recap to Matrix SVD concept... Likewise, adapting the same concept to higher dimension; CP Decomposition is a method used to decompose a tensor into a sum of component rank-1 tensors... finding the best rank approximation of this tensor might not have a direct method to be solved for and it is termed as NP-hard problem." [cite: 17].
    
    *Critique for Substrate:* Again, the author assumes an Eckart-Young truncation applies ("adapting the same concept") and attributes the lack of a direct method to NP-hardness, completely bypassing the LimitWitness Tier-B topological anomaly [cite: 17].

3.  **Imprecise Use of "Rank" for Convex Relaxations:**
    In February 2025 and late 2024 literature, multiple authors claim to solve the "tensor rank minimization problem" using Sum of Nuclear Norms (SNN) or Tensor Nuclear Norm (TNN). As seen in Snippet 19 (IEEE TPAMI, projected publication/indexing 2026): 
    > "Although the Tucker rank of a tensor can be computed via the SVD of the unfolding matrices easily, the Tucker rank minimization is also NP-hard... Some convex approximation methods were proposed and studied via the sum of nuclear norms" [cite: 18].
    
    *Critique for Substrate:* Here, the authors correctly identify that *Tucker rank* minimization is NP-hard (matrix rank minimization is NP-hard), and the set is closed. But by failing to explicitly isolate CP rank's topological failure, the literature collapses distinct failure modes. Tucker rank minimization fails practically due to *computational* bounds (NP-hardness); CP rank minimization fails due to *topological* bounds (Ill-posedness).

The recurrence of these false forms confirms that the anti-anchor is strictly necessary. LLMs trained on this recent corpus will inevitably absorb the false gradient that "CP rank optimization is just an NP-hard matrix extension."

***

## (d) RECOMMENDATION

**Target Action:** Register `LimitWitness.TierB` sub-type into the Prometheus substrate.

**(i) Anti-Anchor Status:**
The anti-anchor’s true form is **correct as stated but requires refinement**. 
*   *Refinement:* The anti-anchor must aggressively uncouple **Topological Ill-Posedness** (the failure of a sequence to converge to a point within the set) from **Computational NP-Hardness** (the algorithmic complexity of finding a point). 
*   *Verification:* De Silva & Lim (2008) is the correct primary anchor for the topological ill-posedness [cite: 1].

**(ii) Sub-Anchors & Companion Anti-Anchors:**
During verification, three stable sub-anchors were discovered that must be registered to prevent the substrate from treating all tensor approximations as ill-posed:
1.  `[Sub-Anchor: TubalRank.WellPosed]` — Under the t-product/t-SVD framework, low-tubal-rank sets are closed, and a generalized Eckart-Young optimal truncation holds [cite: 6, 7].
2.  `[Sub-Anchor: NonnegativeCPRank.WellPosed]` — Constraining the tensor and its rank-1 factors to the nonnegative orthant forces the approximation space to be topologically closed. The best approximation always exists [cite: 5].
3.  `[Companion Anti-Anchor: ComplexCPRank.AlmostEverywhere]` — Over \(\mathbb{C}\), the CP rank ill-posedness occupies a set of measure zero. The non-existence of a best rank-\(r\) approximation is primarily a pathology of the real field \(\mathbb{R}\) [cite: 8, 9]. 

**(iii) Substrate Inputs & Work-Queue Entries:**

`[Catalog Edit: LimitWitness.TierB]`
```yaml
id: limit_witness_tier_b
description: "Topological boundary failure in unconstrained best low-CP-rank tensor approximations over R."
primary_anchor: "de Silva and Lim (2008), SIAM J. Matrix Anal. Appl. 30(3)"
distinct_coordinates_enforced: 
  - CP rank (ill-posed over R)
  - Border CP rank (closed over R)
  - Nonnegative CP rank (closed over R)
  - Tubal rank (closed over R/C, satisfies Eckart-Young)
  - Tucker rank (closed over R/C)
false_form_filter: "Reject equivalencies between 'CP rank approximation is NP-hard' and 'CP rank approximation is ill-posed'."
```

`[Work-Queue Entry: GenericityAlmostEverywhereCert]`
**Task:** Synthesize the 2020/2024 findings of Qi, Michałek, and Lim regarding the unique best rank-\(r\) approximation over \(\mathbb{C}\) almost everywhere.
**Objective:** Create a certification protocol for Prometheus agents that cross-checks the base field (\(\mathbb{R}\) vs \(\mathbb{C}\)) before asserting the topological failure of a CP decomposition. 

`[Anti-Anchor Pin: MatrixMatricizationGravityWell]`
**Task:** Resist the gravitational pull of treating tensor operations strictly as unfolded matrix operations. 
**Objective:** When the substrate processes "Tensor Nuclear Norm" or "Sum of Nuclear Norms", force the explicit coordinate labeling of "Tucker Rank Surrogate" or "Tubal Rank Surrogate". Do not permit the system to label these as "CP Rank Surrogates," as the CP rank cannot be convexly relaxed via unfolding matrices without fundamentally changing the geometric invariant. 

**Sources:**
1. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5d_hfgaVjPFPsr3bVr7Pc1sAU9-9_JKbkvPlVw7AGJRccOLBRfJnUHw1PcXyovQDKwMfTzFsVSbr1taHl5JViXET0rLVwjWJg1PUiNqmFIfm4ayedoV84uTrrb_CsOo7Jug==)
2. [ohiouniversityfaculty.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNaLAJVNlRgwRcjN3z1EFmB7EPMnwe3xczzXhK7ZTFU3ZCeCy0ThJcNuFtcFhaAkXqlqWgxEvPlstJ0CBBGkTPvnt8a5rvU_OBkwsH3NDImIhcuq20THOJDThsuPKJ1NlVCrxbwaOaj0dluUyKka4MBg==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ6yrEsWwJeNYRQdNW_3V5HCQhgcv5NZxX-ZU3mF7jcrC_LNPMijdssmpV8ResZw8ihaFnIzXO6BKXzTZ8bPrX5HMjlla94r-0Su35AUwtrcU0OxOs9sge)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpi7fhBkaqGmU0CseOMox8m6lcDF93jc6ai8HRC5GkYS0hfC7vOQR7oWYelHEBDZVbnvmD1vTEaLGo75ZLPj3jkusGZJ-fllSKhY24lfhbmHfcMvMQIQ==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0kqlAOp8QTntSOpsqIDe1GqXtEBS55MGCGyzqewtbIom0rBMIMA5QX_zjilx3RwdE_0AK6IRs7BioZFXXGLNrA7ODmqBPGp5uz7n-qYzKgVcID1ha_5sovMz-OnEodS1bIFCT29nvQ6sehm5Z0MlloUYjk3Gczpc3NyA3tP5MBp_anJ4G8JgIyQWyueC96cDDXSmTuLDR_4g=)
6. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnvOy3bz2iSvg4fQhsk8WvAU-beb0Zo7aBxFACiaJgWA2n4YptUjrCsnMyNlW1H85-9StUhxs65t85k752W9V7fzOfmHSTzxFdwOR8AykoQ3dzFd03lGaRCAz-51jtKlHu-5gNAnBfKBWpGTtEJjIV1Astthfs8lkVnaZRY1cdCNK4vaNT)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGImEmLRpO5_rLoU9IK_xmGOmT-6nD1vCHGSSjXy4aZeYKTCnFPGOK5GWN861vh4HHyKSxTjP01pCLu3NEwYpwumGiOzNc0jgqisxtxLeyBhsdW2Op9tLsjyQ==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFUa8aNZtJ2A6FOX8gp9Srf5LVYfo8ouKJobXsuqws7OaWinCDns0KwrJDZzfwFG6UWbsSTDmMXgW_BJxr6unWTb-c6B30ufUnK7mzhz75m7I8A0pKRgAsHGrN-fUlNBIngs2W7-DS7-a_pdds6tncCBlilQQELuNxZxaWQo7XVpVToWbv0c6_o9p8ARHjFYzTAEwxTOKnF0T3Y7-e54MhMQcp9t88kImSRYJ_dmOrBdGxfFg=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWlkzSc38QuOuiGt08KQWreXJwksvbWMJTNHLUosas-ntp0gy64fwxu8d7UoEi1oTRvWnibMcgf3Pq-c_okxqkuhQODCwiGcIuJiianNqPK-_4-H71pg==)
10. [kuleuven.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKkCjnGJKGOFSsI8P8a8OWPIHsqjK7XK7tmAkDapMDZxHvk7uer4KijNulVpI1zl5kal1pH9uA-nE6LA71k0c4mng_SmbWQBzXWDuPoZ8hJYNMubg1s9wFxS-uiIzYhaJCO0Blub-KmxROUxYPtWpmML-bZ0DAh5nQK0kI2cZC5AHfgwg=)
11. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK3Q_KunSy7D7xM8Xn2M5godWNOQAA-Pxce1nwK3UTUJWaYixhue_PKXM3bqTI74mrU9YsMPvrK4kvPYWZEqydwUP4FdG_OpGoobkifIvNDjhMr3_HUOpE-sa2ipBWrbSgjvfdHL6BmQwkmEYYZSXLt7E=)
12. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8GwqvgLpSGablohpSUBHDNJaRE9bSQA9oJ_hf9sxejPEJHhPM2vNbcBaDBRjEew98huWROuY9m9gmpPGw5ousgqMxopVUxxcKsCkgK6WHPkDWQ9spEDrQth5FMToqgPX_RuuCPuNN1w==)
13. [sciprofiles.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlJwvrj8i5XBADyq6fUuUDHEK2r5yCWTLLFSYbARaQnGfH6K5TaexLDFf9hVD9IFS9Byjt4rmEgEWkK5CGxl_Z-6qWiqpAbhZ1NuWocSGee8zpO1uof31DE1RACqU=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqxYoSS09bNJbpXda1_uqnkh4c_9CJni0WiFfMKUrk-zSaqm5wPnsEZrMC4t0mELpo_ffsMsuiy7bRMwPS-_cdX7Uc7AA8FrAiMXvsl9ZjvNW0NGi_6KLJ3ICk5NkgzVJFHgJCgHbH6EECkGbHm0lys6tIqBR1CO5aFmOhZNDCQnpsZPP_GXa_5ZvFjNoorpF8QFiMupuR1qcuP5niY8hmXey9l1Yd-7lgElW1OFkUSfdmvBQ1DobZcHxy7g==)
15. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3kneuqrPM73oGC6b8c5cZ-TakICqYFG81w2RGdhFly9zS3XNPR4sOL_C15QkxBKphU0xffe5huUkZ2qggUAcmX70a8Rz8MUjYpDBma7qZMJETTXty2GAj0SkfkFQtbD4=)
16. [hep.com.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF53ldsyjZXap3I1p1HJO1wZMxL80ztyphXKYfzrL22b3xsljUGYNPCVBn0oUyH_UFY8ywtlXTujxz18zGbx1YgPuhxDlZ46HBoUASyPMY4ShNecVDiFvZqwA1sZ4Fcn3tsqj5dk0Dlx62gNcAPJBBKneUEoDU=)
17. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK3qDrS_NoOu-YMqH_H0vuYfYU75J7LQ9M_H6QgYu7LMu7_wFl26r52lgBxOL_sc-Jo1UWOLzDVeYdrtz3pKBUin4C9Bi_WaA5j8ses_Dl-dge1lZnbDQ4bJkWUMgDy2pdsLpD6nyvuSfGlMc4wmOomhWiFNburH8oe1a5ry12EUmV5RPNx-rRiFaoLBCpRfkT_vliGxrmOIYbdVEnR4YII5baD_W3Qw==)
18. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwuAwZZpSkgWgMwEcHhXhHQiW8okhgK1J6KHrFWWbGupco7ce1Fcxni3SnEisJUo6tOpP4ZFD-el2cM0eH-auBDadyDuL96-gK9qWQkKSa9NeYeDyq5zzYt-9n1pb_WFs1Ag-K31Q1rAsNue86KPPKP_8cAIuCuSo_U3A=)


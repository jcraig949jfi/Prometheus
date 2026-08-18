# Prompt 01: Verify anti-anchors AA-001 through AA-004

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcxVE1CYXVpVUxzYjFqckVQMnBQNzhBSRIXMVRNQmF1aVVMc2IxanJFUDJwUDc4QUk
**Elapsed:** 243s

---

# Verification Report: Project Prometheus Anti-Anchors AA-001 to AA-004

**Key Points:**
*   **AA-001 (GCT):** Verified. Bürgisser, Ikenmeyer, and Panova (2016) eliminated **occurrence obstructions** for the permanent vs. determinant problem, but explicitly preserved the viability of multiplicity obstructions. 
*   **AA-002 (Zauner's Conjecture):** Verified. Appleby, Flammia, and Kopp (2025) provided a complete constructive framework for SIC-POVMs, but their proof remains strictly conditional on the order 1 abelian Stark conjecture and a Shintani-Faddeev modular cocycle identity.
*   **AA-003 (Hillar-Lim/Symmetric Rank):** Refined. The user-provided citation (arXiv:1605.07532) is incorrect and points to a PDE paper. The correct citation is Shitov (arXiv:1611.01559), which proves the NP-hardness of symmetric tensor rank over $\mathbb{Q}$, settling the Hillar-Lim conjecture.
*   **AA-004 (Saxl Conjecture):** Inverted. The provided "True form" is false. The Saxl conjecture remains open. A December 2025 claim by Soong Kyum Lee was withdrawn due to mathematical gaps, and Mark Sellke's prior work strictly concerns fourth powers, not the unconditional resolution of the tensor square.

**Summary of Action Items:**
This report directly addresses the query parameters for Project Prometheus. The evidence leans toward preserving the core structure of AA-001, AA-002, and AA-003, with minor citation and specificity adjustments. AA-004 requires a complete categorical inversion to prevent injecting fabricated mathematical proofs into the v1.0 Learner training corpus. The analysis below relies strictly on primary literature, exact theorem definitions, and timeline tracking through 2026.

## Verification of AA-001: PATTERN_GCT_OCCURRENCE_DEAD

### 1-Paragraph Confirmation
The true form of AA-001 is accurate and strictly aligns with primary literature. The claim that "Bürgisser-Ikenmeyer-Panova killed GCT" is a colloquial distortion of a specific no-go theorem published on April 21, 2016 [cite: 1]. The authors demonstrated that **occurrence obstructions**—specifically, finding an irreducible representation of $GL_{n^2}(\mathbb{C})$ that occurs in the coordinate ring of the orbit closure of the padded permanent but not the determinant—cannot separate the complexity classes $VP_{ws}$ and $VNP$ [cite: 2]. They did not invalidate the entirety of **Geometric Complexity Theory** (GCT). Multiplicity obstructions, which rely on the difference in representation multiplicities rather than strict non-occurrence, remain mathematically viable.

### Primary-Source Quotes and Mathematical Context
The canonical primary source is arXiv:1604.06431, published April 21, 2016, with a substantial revision on September 17, 2018 [cite: 1, 2]. The permanent versus determinant conjecture, an algebraic analogue to P vs. NP formulated by Valiant (1979), proposes that the determinantal complexity $dc(per_n)$ grows superpolynomially [cite: 2, 3]. Mulmuley and Sohoni proposed a representation-theoretic approach to separate the orbit closures [cite: 1].

The precise negative result concerns the Kronecker coefficients $k(\lambda, \mu, \nu)$ and the coordinate ring $\mathbb{C}[\Omega_n]$ of the orbit closure. The authors state:
> "In that paper it was also proposed to separate these orbit closures by exhibiting occurrence obstructions, which are irreducible representations of $GL_{n^2}(\mathbb{C})$, which occur in one coordinate ring of the orbit closure, but not in the other. We prove that this approach is impossible. However, we do not rule out the general approach to the permanent versus determinant problem via multiplicity obstructions as proposed by Mulmuley and Sohoni." [cite: 1]

The theoretical mechanism relies on bounding Kronecker coefficients. A partition $\lambda$ is said to occur in $\mathbb{C}[\Omega_n]$ if the coordinate ring contains an irreducible G-module of type $\lambda$ [cite: 2]. The paper proves that $\lambda$ cannot strictly vanish for the determinant while appearing in the permanent's orbit closure for the specific paddings evaluated.

### 2024-2026 Follow-on Work
The GCT program has successfully absorbed the BIP no-go theorem and shifted focus toward multiplicity and plethysm coefficients. Literature from 2024 confirms the ongoing active status of the general GCT pipeline. A December 15, 2024 paper notes:
> "The importance of plethysm coefficients in GCT derives from their frequent appearance in formulas for multiplicities in coordinate rings... Thus the problems of both calculating and bounding plethysm coefficients are of fundamental importance in GCT." [cite: 4]

### Status Confirmation and Refinement
The true form provided ("BIP killed *occurrence* obstructions for det/padded-perm specifically; multiplicity, vanishing-ideal, outside-orbit, and equivariant obstructions remain") is mathematically precise. The colloquial "false form" likely stems from informal computational complexity discussions and blog posts (*e.g.*, Scott Aaronson's 2017 blog noting the paper "substantially changing the outlook for the GCT program") [cite: 5, 6]. 
**Status: Verified. Retain true form.**

## Verification of AA-002: ZAUNER_FALSE_ANCHOR

### 1-Paragraph Confirmation
The true form of AA-002 is highly accurate and necessary. Zauner's conjecture (1999) posits that a maximal set of $d^2$ complex equiangular lines—known as a **SIC-POVM** (Symmetric Informationally Complete Positive Operator-Valued Measure)—exists in every dimension $d$ [cite: 7, 8]. On January 07, 2025, Marcus Appleby, Steven T. Flammia, and Gene S. Kopp published arXiv:2501.03970, which provides a sweeping constructive approach for all dimensions [cite: 9]. However, this is not an unconditional proof. The existence of these structures under their framework is strictly contingent upon two major unproven theorems in algebraic number theory. 

### Primary-Source Quotes and Mathematical Context
The canonical primary source is arXiv:2501.03970, "A Constructive Approach to Zauner's Conjecture via the Stark Conjectures," submitted January 07, 2025 (revised March 17, 2025) [cite: 9, 10]. The geometric object in question is a regular simplex of maximal size in generalized Bloch space, exhibiting Weyl-Heisenberg symmetry [cite: 10, 11]. The authors generate these using an intermediate object called a "ghost SIC" constructed from real multiplication values of the Shintani-Faddeev modular cocycle [cite: 9].

The authors explicitly articulate the conditionality of their theorem:
> "We prove our construction gives a valid SIC in every case assuming two conjectures: the order 1 abelian Stark conjecture for real quadratic fields and a special value identity for the Shintani-Faddeev modular cocycle." [cite: 9]

The mathematical dependencies are further clarified:
> "The former allows us to prove that the ghost and the SIC are Galois conjugate over an extension of $\mathbb{Q}(\sqrt{\Delta})$ where $\Delta = (d+1)(d-3)$, while the latter allows us to prove idempotency of the presumptive fiducial projector." [cite: 9, 10]

### 2024-2026 Follow-on Work
The 2025 Appleby-Flammia-Kopp (AFK) paper is itself the 2025 follow-on work that defines this discourse. Concurrently, computational cross-validation in dimensions up to $d=100$ has supported their conditional construction [cite: 9, 10]. The broader discussion in 2025 literature includes generalizations to $r$-SICs (maximal equichordal configurations of $r$-dimensional complex subspaces) [cite: 9, 10] and investigations into real symplectic spaces, linking "symplectic Zauner's conjecture" to the skew Hadamard conjecture [cite: 12]. Gerhard Zauner's own recent updates point to the 2025 AFK paper as "The most recent and advanced paper on this topic" without claiming unconditional resolution [cite: 8].

### Status Confirmation and Refinement
The true form accurately captures the conditionality of the 2025 result. LLM training data is highly susceptible to truncating conditional algorithmic proofs into unconditional "solved" statements.
**Status: Verified, but Refined.** Change "AFK 2025" to "Appleby-Flammia-Kopp 2025" in the true form to prevent the Learner from treating "AFK" as a generic acronym. 

## Verification of AA-003: HILLAR_LIM_CLOSED

### 1-Paragraph Confirmation
The true form of AA-003 is conceptually correct but suffers from a significant citation error in the prompt. The symmetric tensor rank problem over $\mathbb{Q}$ was indeed proven to be NP-hard by Yaroslav Shitov in 2016, settling a conjecture by Hillar and Lim [cite: 13]. However, the citation provided in the prompt (arXiv:1605.07532) resolves to a fundamentally unrelated mathematical paper on PDEs ("The Selection problem for discounted Hamilton-Jacobi equations: some non-convex cases" by Gomes, Mitake, and Tran, May 24, 2016) [cite: 14, 15]. The correct canonical citation for Shitov's proof is arXiv:1611.01559 [cite: 13, 16]. 

### Primary-Source Quotes and Mathematical Context
The correct primary source is "How hard is the tensor rank?" (arXiv:1611.01559), submitted November 04, 2016, by Yaroslav Shitov [cite: 13, 16]. The **tensor rank** over a field $\mathbb{F}$ is the smallest integer $r$ such that a tensor can be decomposed into a sum of $r$ simple (decomposable) tensors [cite: 16, 17]. The **symmetric rank** restricts this decomposition to symmetric tensors. 

Shitov's result links tensor rank to the existential theory of the underlying integral domain:
> "For tensors over any integral domain $R$, we prove that the rank problem is polynomial time equivalent to solving a system of polynomial equations over $R$." [cite: 13, 16]

Regarding the Hillar-Lim conjecture, Shitov explicitly states:
> "We generalize our result and prove that the symmetric rank admits a similar description of computational complexity as the one we give for usual rank. In particular, computing the symmetric rank of a rational tensor is shown to be NP-hard, which proves a recent conjecture of Hillar and Lim." [cite: 13]

This fundamentally resolved the open question regarding the algorithmic complexity of symmetric tensor rank over $\mathbb{Q}$. However, Hillar and Lim's NP-hardness result for general tensor rank over $\mathbb{R}$ remains foundational.

### 2024-2026 Follow-on Work
Research regarding the divergence between rank and symmetric rank for identical tensors remains active. On February 05, 2024, Shitov published "More on Tensors with Different Rank and Symmetric Rank" in SIAM Journal on Matrix Analysis and Applications [cite: 17]. This follow-on work investigates specific field characteristic constraints, noting that obstructions remain for extending complex number examples of rank/symmetric-rank divergence to the real number setting, specifically analyzing cases where $char(\mathbb{F}) \neq 3$ [cite: 17].

### Status Confirmation and Refinement
The "false form" claiming the problem remains open is indeed present in pre-2016 literature and un-updated textbooks. The "true form" correctly credits Shitov and isolates Hillar-Lim's remaining valid bounds. However, the citation must be strictly corrected to prevent injecting a hallucinated reference linkage into the Learner corpus.
**Status: Verified with critical citation correction.** Replace 1605.07532 with 1611.01559.

## Verification of AA-004: SAXL_CLOSED

### 1-Paragraph Confirmation
The provided "True form" for AA-004 is factually false and mathematically dangerous; it must be completely inverted. The **Saxl conjecture** (2012) posits that the tensor square of the irreducible representation of the symmetric group corresponding to the **staircase partition** $\rho_k = (k, k-1, \dots, 1)$ contains every irreducible representation of $S_{T_k}$ as a subrepresentation [cite: 18, 19]. Mark Sellke (with Sammy Luo) did *not* solve this unconditionally in 2025/26; their work in 2016/2017 proved a weaker version demonstrating that the tensor *fourth power* contains all irreducible representations [cite: 20, 21]. In December 2025, a preprint by Soong Kyum Lee (arXiv:2512.15035) claimed an unconditional proof, but this paper was withdrawn within days due to "mathematical gaps identified by expert reviewers" [cite: 22]. The Saxl conjecture remains an open problem.

### Primary-Source Quotes and Mathematical Context
The withdrawn 2025 primary source is arXiv:2512.15035, "Staircase Minimality and a Proof of Saxl's Conjecture," submitted December 17, 2025, by Soong Kyum Lee [cite: 22]. The abstract boldly claimed:
> "We prove this conjecture unconditionally. Our proof introduces the Staircase Minimality Theorem: among all 2-regular partitions of $T_k$, the staircase $\rho_k$ is the unique dominance-minimal element... Modular saturation then follows using only the diagonal entries $d_{\mu\mu} = 1$ of the decomposition matrix, and the Bessenrodt–Bowman–Sutton lifting theorem completes the proof." [cite: 22]

However, the retraction notice published on December 20, 2025, definitively nullifies this:
> "Comments: This paper requires significant revision to address mathematical gaps identified by expert reviewers. The claim of a complete proof is not justified in its current form. I am withdrawing to properly address these issues." [cite: 22]

Regarding Mark Sellke, the canonical reference is his 2017 Journal of Algebraic Combinatorics paper with Sammy Luo:
> "The Saxl Conjecture for Fourth Powers via the Semigroup Property." [cite: 23]
Other authors subsequently improved this bound from the fourth power to the tensor cube. A 2022 paper notes:
> "Luo and Sellke proved a weaker version of the Saxl conjecture, namely that for $n$ sufficiently large, $(S_{\rho_n})^{\otimes 4}$ contains every irreducible representation... Our main theorem is the following improvement: Theorem 1.1. $(S_{\rho_n})^{\otimes 3}$ contains all irreducible representations of $S_N$." [cite: 18]

### 2024-2026 Follow-on Work
The primary 2025 event regarding the Saxl conjecture is the highly visible, retracted claim by Lee. Because pre-print servers and automated scraping tools often fail to propagate withdrawal notices with the same velocity as the initial claim, LLM training data is uniquely vulnerable to memorizing Lee's withdrawn abstract as ground truth [cite: 22]. 

### Status Confirmation and Refinement
The user-provided setup acts as an anti-anchor *against* itself. If injected into the Learner corpus, it would mandate the model to output a mathematical falsehood. 
**Status: Inverted.** The "false form" is that the conjecture is solved. The "true form" is that it remains open, Luo/Sellke only proved the fourth-power relaxation, and Lee's 2025 tensor-square claim was mathematically flawed and retracted.

## Final Section: Recommendations & Adjustments

The following table provides the strictly verified, primary-source-anchored text required for the v1.0 Learner training corpus. 

| Anti-Anchor ID | Recommended "False Form" | Recommended "True Form" | Corrected Citation |
| :--- | :--- | :--- | :--- |
| **AA-001** | "Bürgisser-Ikenmeyer-Panova (2016) killed Geometric Complexity Theory." | "Bürgisser-Ikenmeyer-Panova strictly eliminated **occurrence obstructions** for the determinant vs. padded-permanent separation. GCT remains viable via multiplicity, vanishing-ideal, and equivariant obstructions." | arXiv:1604.06431 |
| **AA-002** | "Zauner's conjecture for SIC-POVMs was proven unconditionally in 2025." | "Appleby-Flammia-Kopp (2025) constructed SIC-POVMs in all dimensions, but the proof is strictly conditional on the order 1 abelian Stark conjecture and a Shintani-Faddeev modular cocycle identity." | arXiv:2501.03970 |
| **AA-003** | "Hillar-Lim's conjecture regarding symmetric tensor rank over $\mathbb{Q}$ is open." | "Symmetric tensor rank over $\mathbb{Q}$ was proven NP-hard by Shitov (2016), settling the Hillar-Lim conjecture. Hillar-Lim's NP-hardness bound for general tensor rank over $\mathbb{R}$ remains foundational." | **arXiv:1611.01559** *(Corrected)* |
| **AA-004** | "The Saxl conjecture was solved unconditionally by Lee (2025) or Sellke." | "The Saxl conjecture remains open. Lee's 2025 proof (arXiv:2512.15035) was withdrawn due to mathematical gaps. Luo and Sellke (2017) only resolved the weaker tensor fourth-power variant." | arXiv:2512.15035 |

### New Sub-Anchors Discovered
1.  **SAXL_CUBE_ANCHOR:** 
    *   *False Form:* "The tensor cube variant of the Saxl conjecture remains open."
    *   *True Form:* "The tensor cube variant $(S_{\rho_n})^{\otimes 3}$ was proven to contain all irreducible representations of $S_N$ in 2022 by building on Luo and Sellke's combinatorial semigroup property." [cite: 18].
2.  **TENSOR_RANK_Z_ANCHOR:**
    *   *False Form:* "Tensor rank over $\mathbb{Z}$ is computable in exponential time."
    *   *True Form:* "Tensor rank over $\mathbb{Z}$ is mathematically undecidable, proven by Shitov (2016), answering the 1980 Gonzalez-Ja'Ja' conjecture." [cite: 13, 16].

### Follow-on Work to Track
1.  **Stark Conjecture Resolutions:** The conditional nature of AA-002 means any future proof (or disproof) of the order 1 abelian Stark conjecture for real quadratic fields will automatically cascade into the unconditional resolution (or collapse) of Zauner's conjecture via the 2025 Appleby-Flammia-Kopp framework.
2.  **Soong Kyum Lee Revisions:** Monitor arXiv:2512.15035 for a `v3` replacement. The current `v2` (December 20, 2025) is a withdrawal. If the mathematical gaps regarding the Staircase Minimality Theorem and the Bessenrodt–Bowman–Sutton lifting theorem are bridged, AA-004 will require immediate deprecation.
3.  **Divergence of Rank and Symmetric Rank ($char \neq 3$):** Track Yaroslav Shitov's ongoing publications (post-2024) establishing precise characteristic boundaries where tensor rank strictly diverges from symmetric tensor rank over real and characteristic-3 fields.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHo9CuxSviS9O3z9PFjObzOQgnIG60c5N6xnbEBczBMwH3Gd-RWLiIFFct2cook2jXF8VRbN0JPXhUjt58ajaRWmjT0WoPjiChIpTAikYj-VkD2Dj8v)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4e-sOEAknxzoiMHVYxRrO6qWZxiLvTX_UbsSfhgduhnReYOyg_yh0noVAB2-xPP2Vzn1vXdSbjdF6xPdiDyvEsCjGjbt15y0kVozRwo0MuptANP2X)
3. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3uiiSDVbchh3hI5TQngnDe8rZ_FxynGOZXcxrlxfIYeny9fLj1OMj6wdPGnCeoQK0vPKzEkBjiBCj879aFMHosn8jZBxhTiYuhyK2JoOqwEwD-5SSB6rvE19Yvq7Ou1nO0-8=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaQFn3GVvZBUV4CYXFtGw2H9lhN4owuWCE6-h-ZwjDS0sJqXF2mpK9M9uxyqBmoXks8MjukEYSatY83odK8SWWuYUcF85Nt4epLTLDEC72DXDDgdnF)
5. [scottaaronson.blog](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4ekesNLpgKNmS4ns2PmUalHkOHOmeAT3JPLld-ww4oTq1JZj-AL0n7F-TShX3aNBTc9ctxq_Y4pgB0xoE4vfYLqJKozjzSCz4aLTRLSFD-eixwtDZmlkSLA==)
6. [scottaaronson.blog](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNVosK0ioTyvFGXy7xyuXkinscNlOPyosyj1KUgZXZOSJElvn7QayRG47Ctgk_Dc4RUd5oFDu_-p_C-bWyq3uZf3_XfEtaazgpwOb7MYekeZ5AABWo-zk=)
7. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHg3RajcPru85Rrd6-GILuf59FC7ZKhDeCMnLx-9oZW3fS-7IfxXVuNSG8xljdl4UsQggEHkV3B8f9Vf5oTZsvV6Xr2DZTfT8npFsElZXeqiHnnplDPUMjC3lRGxUsZbBY=)
8. [gerhardzauner.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHURlasOYBCUiHDp2q9-OlJc2HXnxGxr4ZBkytft9dukHcoBFne6CHY6TNQ3YFt97xQ_74G4ggt3G8IiRhKl5blc_GTGuzvE9VcNaUUEjDLRTrhtLxk6MeNxP-hAX5U)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE883CFXKwwlkkZI146HfkCqwD9CAScO4M7Pwa3jcQKYnf1vqIPJsv1vCKg6kBGspq5hliPprFW0ZluUotN-LMBb4eS5ztJ3unfVQ7gDovVn8_o85D0)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0qLm24uRmxkwMrA9eipSBgMor_2B9_gpuIJmIK-C8CB8kYuUu0TViDriTva0upVoCbZgs6sIn7lTJCskwlXmBB_o9tLQuHDx-LDfLxk7gDHUUvw8w)
11. [aip.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgMf9LV4gIClYlyVvsJ673QE0uh6OOePRAZwuVXFfs46gJEcGNsk2J0rd6rWgdtn3-lvFePnB47jqIxUAJa6KiWQUDs0uFSf5o8p6yFrTuXlc6Jzf0H3vBQLvDJWFl5UJyut7kSo0SY-RU_vLUCKkFE4qEBtDLSOAdhswsjvwFoyEZNwpsq3KnJIdj8zVpEjH1_uZp5mmKaXUoFrGw)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEKvdsqmsEYLrNazUS-WTiIl8cFfalbWlWteLuqW_POtc-oSsWS6MEvjKtT1zYYNCOxwCeAR5fuMl775fHsT6Lvy8pOmP7ujB-dQWNb95pSfCl8aoc)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMTRspF7fms6ClnePe2Tb_qEqbPbUTNwqzgVe_yTUz4-L3SvfvOpxeBl74iAOUnqekrM0kaweWFlIVT4DYchsgPZVlEzxRxNce7AfA5NBR-cA7gKHA)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnJz-UujaDcQ0yy8r3qzJA7fGmrhLxwMt802CVxODkf4tqCNo83gjyAbBEDbSXmy6RzKvpOG2xEfaCvCISuBK4uYAQJUN-9Szwtd7_cgGbxbTIe87W)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8Uz1rddYRln2mCdLaFi1vgoooQX_UnYDDeUuWW8kaT-LFpWQS0o5SFgvk8fiPkPFF31aqjNo2GsFgOQScUbws9W9u3lgRxC2c72tQIeLm4cD6PYf7)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2gxs2LdFUhNwU13yw-sN2QEOwzTwOocxOs1uYqs7o4ckEUw7notx2IEHqcNHfTNUsF3fmTGMMR-7EOwUCyd2es8IYYgIyn7gAyDgmCfaBpvjShlb1)
17. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFq0sgbHD2byBWF_dEl_pBrPnhfdx1EgI5b39IGXMMnCkrUvcQ7JsQ3i4D7S54OYzNbOfSE-JeObo-OC1LPwzcHHt4swLm7yhxId9pPd2q0yIs_w4WBt9gxWlgDtf701Ms8ng==)
18. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHdJDIa05qZhoaKGfT2YS6k7ItSs1t4oF5Yyng3U8UK0h6NN8ee5POq6BgBFoHFsIlftPMf6xcjBxVpa-fSBwDdE2w5IyDW9taaJl87d5MgpPFznbqyqQAK8NOZXzzDndGvZiV70B_KvnPn4kPgaI=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5ByXYDzaErKNWpbsTS1lVVQfnayyWjZFpQARZigMcvxRa7XAHNrQuHuDJH5mfkFosfCuYo99RorsMpvmTDUSukNdt00P-c135tltGVp2_kyR0U9H9Cj1Y)
20. [msellke.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXhvZJYJDTv1tDy7waXgAxgG2Y1idlWZ-H-oj46bv495o_PRIzBqEFc0eviNvuihL8yfKuDGfY_kUxYswMhmDoyMvuCKGVftXjuOQhO5QtBVxSD3vUPNI9xsrWLearqst2qdU=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGem18AXNyNFRxfKEmHIGe6XFNPyXobVxdoLsuUD7gzIT7YIZUI5bTKFgcrzWUDEEoeLlcOXToGfao73-1KJ5QLpaqj-73oTPPNpzKpIZEYtMXNKbup)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETdXB_vdNYIdFCpex7FIV85FvHlGYg4yvOYHDiyjm-Aen_cKWuhZo_lHdCtF7-7NwuT667IDK3AFOgTGTtZo7_ykaLfK45uhee88oBnIvKcE7VriAM)
23. [msellke.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8IgH-EiuWKjMDufGHvq3_YDhkvTaY3tUZejVAdVLGzB5dRD34_W6kPb7Ac1QH8ylmlkNJIkjt_sY3iSWDZdZHJ95fG_qS1rAyaymcHyY6PDQ=)


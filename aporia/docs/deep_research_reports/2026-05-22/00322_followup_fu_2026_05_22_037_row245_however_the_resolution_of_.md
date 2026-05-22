# Followup [FU-2026-05-22-037 <- row245]: However, the resolution of the Main Conjecture did not terminate the research program; rather, it in

**Pythia queue id:** 322
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZVN29QYXNvcmtPYU14d19OMDQ2QUNREhZVN29QYXNvcmtPYU14d19OMDQ2QUNR
**Elapsed:** 250s
**Completed at:** 2026-05-22T02:11:25.727390+00:00

---

# Status Update: Post-Vinogradov Mean Value Theorem Landscape

**Key Points:**
*   The definitive proofs of the Main Conjecture in Vinogradov’s Mean Value Theorem (VMVT) by Wooley (via efficient congruencing) and Bourgain, Demeter, and Guth (via \(\ell^2\)-decoupling) did not conclude the field but instead acted as a catalyst for a sprawling ecosystem of higher-order problems. 
*   Recent breakthroughs include the resolution of the multivariable Parsell-Vinogradov systems by Guo and Zhang, proving that decoupling theory scales to arbitrary dimensions.
*   The Extended Main Conjecture, which addresses integration over restricted domains (small caps), has seen major advancements through the 2025 work of Oh and Yeon, establishing sharp upper bounds for specific dimensionalities via refined shifting variable arguments.
*   Investigations into inhomogeneous systems by Brandes, Hughes, and Wooley reveal severe departures from classical heuristic models in subcritical ranges, demanding minor arc estimates that break the square-root cancellation barrier.
*   Methodological bifurcations are now rigid: while real-analytic decoupling excels in continuous, Euclidean manifolds, arithmetic techniques like nested efficient congruencing are strictly required for function fields, finite fields, and algebraic number rings due to the absence of continuous geometric analogs.

**Overview:**
The resolution of the Main Conjecture in Vinogradov's Mean Value Theorem marks a watershed moment in analytic number theory. However, the subsequent "post-Wooley / BDG" era has demonstrated that the standard VMVT was merely the foundational baseline. The current research frontier is characterized by the interrogation of generalized, constrained, and multidimensional Diophantine systems. This report addresses the specific open questions that emerged in the wake of the BDG and Wooley proofs, particularly focusing on the Extended Main Conjecture (involving restricted domains), multivariable Parsell-Vinogradov systems, and extensions over non-standard topologies including arbitrary number fields, function fields, and finite fields. 

***

## 1. Brief Summary
Following the Bourgain-Demeter-Guth and Wooley resolutions of the Main Conjecture, the Prometheus context reveals a highly active frontier fractured into resolving multidimensional Parsell-Vinogradov generalizations, extending mean value estimates over restricted domains (Extended Main Conjecture via small cap decouplings), and migrating these frameworks to arbitrary algebraic number fields and finite characteristic geometries.

## 2. Flagged Findings
The current consensus confirms that the theoretical apparatus developed to solve the standard VMVT—specifically \(\ell^2\)-decoupling and efficient congruencing—provides a robust scaffold for higher-order analogues, but naive applications of these tools frequently break down in constrained or inhomogeneous settings. 

**Current Consensus:**
It is universally accepted that multivariable extensions, such as the Parsell-Vinogradov systems, are solvable up to an \(N^\epsilon\) loss using advanced decoupling theories over moment manifolds and Arkhipov-Chubarikov-Karatsuba (ACK) systems. This was decisively proven by Guo and Zhang across all dimensions \(d \ge 2\) [cite: 1, 2]. Similarly, for algebraic number fields and function fields, the consensus correctly identifies Wooley's nested efficient congruencing as the superior framework, since it avoids the multilinear Kakeya-Brascamp-Lieb inequalities that lack direct analogs outside \(\mathbb{R}\) [cite: 3, 4].

**Where Consensus Might Be Wrong (The Inhomogeneous and Restricted Domain Frontiers):**
Early assumptions regarding the behavior of inhomogeneous Vinogradov systems in the subcritical regime have been actively challenged. The prevailing consensus initially fell victim to **PATTERN_BASE_RATE_NEGLECT**, assuming that subcritical bounds for inhomogeneous systems would roughly mirror homogeneous heuristic expectations based on standard Hardy-Littlewood circle method densities. However, Brandes and Hughes demonstrated that systems of the form \(\sum_{i=1}^s (x_i^j - y_i^j) = h_j\) possess appreciably *fewer* solutions in the subcritical range \(s < k(k+1)/2\) when specific inhomogeneous criteria (\(h_\ell \neq 0\)) are met, fundamentally disrupting naive local-global heuristic extensions [cite: 5, 6]. 

Furthermore, assumptions that standard decoupling would seamlessly transition to the Extended Main Conjecture were overly optimistic. Demeter, Guth, and Wang identified that integrating over restricted domains (\(\mathfrak{D} \subset [0,1)^d\)) requires bespoke "small cap decoupling" parameters [cite: 7, 8]. Attempts to force classical scaling onto these restricted regimes introduced a **PATTERN_RANK_PARITY_LEAK**, where the asymmetrical geometry of the caps caused lower-degree integration variables to escape the standard scale-invariant decoupling constraints, necessitating the novel bilinear shifting variables approach introduced by Oh and Yeon [cite: 7, 9].

## 3. Problem Statement
The current research agenda interrogates several distinct but interconnected mathematical objects extending the classical Vinogradov integral \(J_{s,k}(X)\):

**The Extended Main Conjecture:**
Proposed initially by Wooley and expanded by Demeter, Guth, and Wang [cite: 7, 8], this questions the behavior of the exponential sum \(f_d(\boldsymbol{\alpha}; N) = \sum_{1 \le n \le N} e(\alpha_d n^d + \dots + \alpha_1 n)\) over restricted integration domains. The precise object of interrogation is the mean value:
\[ \mathcal{I}_{p,d}(u; N) := \int_{[0,1) \times [0, N^{-u}) \times [0,1)^{d-2}} |f_d(\boldsymbol{\alpha}; N)|^p d\boldsymbol{\alpha} \]
Researchers seek sharp upper bounds for \(\mathcal{I}_{p,d}\) across specific ranges of \(u\) (typically \(0 < u \le d-1\)) and \(p \ge 2\) [cite: 10, 11].

**Parsell-Vinogradov Systems:**
The multidimensional generalization of VMVT. For a given dimension \(d \ge 2\), the object is to count the number of integer solutions to the highly symmetric Diophantine system associated with moment manifolds [cite: 2, 12]. The interrogation asks whether the trivial lower bound for the number of integer solutions inside a box is also the strict upper bound (up to \(X^\epsilon\)) [cite: 13, 14].

**Inhomogeneous Vinogradov Systems:**
Counting solutions to \(\sum_{i=1}^s (x_i^j - y_i^j) = h_j\) for \(1 \le j \le k\) subject to \(1 \le x_i, y_i \le X\), denoted as \(J_{s,k}(X; \mathbf{h})\) [cite: 15, 16]. The precise challenge is obtaining an asymptotic formula in the critical case \(s = k(k+1)/2\) and subconvexity bounds in the minor arcs [cite: 15].

**Finite Fields and Number Fields Analogs:**
Evaluating \(J_{s,k}(A)\) where variables are drawn from a finite subset \(A \subseteq \mathbb{F}_p\) [cite: 17, 18], or evaluating the mean value theorem over the ring of integers of an arbitrary algebraic number field \(\mathcal{O}_K\), assessing the persistence of the Hasse Principle and Weak Approximation [cite: 19, 20].

## 4. Status & Bounds

The post-VMVT era has generated a spectrum of rigorously proven bounds, conditional findings, and localized breakthroughs. Data is summarized in Table 1 below, followed by detailed exposition.

**Table 1: Current Best Bounds Across Post-VMVT Domains**

| Domain | Regime / Object | Current Best Bound / Status | Primary Authors / Qualifiers |
| :--- | :--- | :--- | :--- |
| **Parsell-Vinogradov** | \(d \ge 2\) (General) | Sharp upper bound achieved (up to \(N^\epsilon\) loss). | Guo, Zhang (2019) [cite: 1, 2] |
| **Parsell-Vinogradov** | \(d = 2\) (Cubic/Quad) | Sharp decoupling resolved for 2D surfaces in \(\mathbb{R}^9\). | Bourgain, Demeter, Guo (2016) [cite: 14] |
| **Extended Main Conjecture** | \(\mathcal{I}_{p,d}(u; N)\) for \(d=2,3\) | Sharp upper bounds established for \(0 < u \le 1\). | Oh, Yeon (2025) [cite: 11] |
| **Extended Main Conjecture** | \(\mathcal{I}_{p,d}(u; N)\) for \(d \ge 4\) | Conditional on small cap decouplings in \(\mathbb{R}^d\). | Oh, Yeon (2025) [cite: 11] |
| **Inhomogeneous Systems** | \(s < k(k+1)/2\), \(\mathbf{h} \neq 0\) | \(J_{s,k}(X; \mathbf{h}) = o(X^s)\) | Brandes, Hughes (2022) [cite: 5, 6] |
| **Inhomogeneous Systems** | \(s = k(k+1)/2\) | Asymptotic formula established (Conditional). | Wooley (2023) [cite: 15] |
| **Finite Fields** | \(J_s(A)\) over \(\mathbb{F}_p\) | \(J_s(A) \ll \|A\|^{2s-2-1/9}\) | Guo, Li, Yung (2024) [cite: 17, 18] |
| **Number Fields** | general \(\mathcal{O}_K\) | Main Conjecture confirmed (\(\ll X^\epsilon (\sum \|a_n\|^2)^s\)). | Wooley (2017) [cite: 3, 4] |

**Detailed Status Identifiers:**
1.  **Parsell-Vinogradov Systems:** Complete resolution. Building on Bourgain, Demeter, and Guth's \(\ell^2\)-decoupling for the moment curve, Guo and Zhang successfully scaled the decoupling apparatus to multivariable ACK systems, proving the upper bounds for integer solutions in all dimensions \(d \ge 2\) [cite: 1, 2, 21].
2.  **Extended Main Conjecture:** Status is *partially resolved but active*. Oh and Yeon (2025) utilized a refined shifting variables argument in tandem with the Hardy-Littlewood circle method to provide sharp upper bounds for \(\mathcal{I}_{p,d}(u; N)\) in dimensions 2 and 3 [cite: 7, 11]. However, bounds for \(d \ge 4\) remain conditional, strictly qualifying upon the unproven general small cap decoupling inequalities for moment curves in \(\mathbb{R}^d\) [cite: 11].
3.  **Inhomogeneous Systems:** Status is *subcritically resolved; critically conditional*. Brandes and Hughes proved that nondiagonal solutions are strictly \(o(X^s)\) when \(s < k(k+1)/2\) [cite: 16]. Wooley pushed this into the critical regime \(s=k(k+1)/2\), obtaining full asymptotic formulas, but the results inherently rely on assuming the Extended Main Conjecture to bypass the convexity barrier on minor arcs [cite: 15].
4.  **Number and Function Fields:** Completely resolved via an orthogonal methodology. Wooley's "nested efficient congruencing" proves the Main Conjecture for all exponents \(k\) without any reliance on real-harmonic analysis, seamlessly establishing the optimal bounds over both arbitrary number fields and function fields like \(\mathbb{F}_q(t)\) [cite: 4, 19].
5.  **Finite Fields:** Partial bounds established. The best absolute bound currently sits at \(J_s(A) \ll |A|^{2s-2-1/9}\), serving as a finite field analogue of the quadratic VMVT [cite: 17, 18]. The lack of sharp incidence geometries (analogous to Euclidean Szemerédi-Trotter) currently caps the exponents, leaving a gap between available finite field bounds and their full conjectured limits [cite: 18].

## 5. Literature (Primary Sources)
The primary literature underpinning this post-VMVT ecosystem is robust, cleanly divided between the harmonic decoupling school and the arithmetic congruencing school. 

*   **Wooley, T. D. (2019).** *Nested efficient congruencing and relatives of Vinogradov's mean value theorem.* Proceedings of the London Mathematical Society, 118(4), 942-1016. (arXiv:1708.01220). **Significance:** Established the Main Conjecture using purely arithmetic methods, extending VMVT to number and function fields without Kakeya estimates [cite: 3, 4, 22].
*   **Guo, S., & Zhang, R. (2019).** *On integer solutions of Parsell-Vinogradov systems.* Inventiones Mathematicae, 218(1), 1-81. (arXiv:1804.02488). **Significance:** Solved the multidimensional generalization of VMVT for all \(d \ge 2\) [cite: 1, 2].
*   **Brandes, J., & Hughes, K. (2022).** *On the inhomogeneous Vinogradov system.* Bulletin of the Australian Mathematical Society, 106(3), 396-403. (arXiv:2110.02366). **Significance:** Identified the scarcity of solutions in subcritical inhomogeneous models [cite: 5, 6, 23].
*   **Wooley, T. D. (2023).** *Subconvexity in inhomogeneous Vinogradov systems.* The Quarterly Journal of Mathematics, 74(1), 389-428. (arXiv:2202.14003). **Significance:** Attained conditional asymptotic formulas in the critical regime using the Extended Main Conjecture to breach square-root cancellation [cite: 15, 16].
*   **Demeter, C., Guth, L., & Wang, H. (2020).** *Small cap decouplings.* Geometric and Functional Analysis, 30(4), 989-1062. (arXiv:1908.09166). **Significance:** First comprehensive formalization of decoupling into boxes smaller than the canonical scale, critical for the Extended Main Conjecture [cite: 8, 24].
*   **Oh, C., & Yeon, K. (2025).** *An extended Vinogradov's mean value theorem.* Transactions of the American Mathematical Society (in press). (arXiv:2506.01751). **Significance:** Resolved sharp upper bounds for \(\mathcal{I}_{p,d}\) for \(d=2,3\) using a refined shifting variables argument [cite: 10, 11].
*   **Guth, L., Maldague, D., & Oh, C. (2022/2025).** *Small cap decoupling for the moment curve in \(\mathbb{R}^3\).* (arXiv:2206.01574). **Significance:** Established amplitude-dependent wave envelope estimates motivating further resolution of DGW's Conjecture 2.5 [cite: 25, 26, 27].

## 6. Attack Vectors

The post-VMVT era is defined by extreme methodological specialization. 

**Live Techniques:**
1.  **Small Cap Decoupling:** Standard \(\ell^2\)-decoupling targets canonical scales. However, for restricted domains, the *live* approach uses high/low frequency wave envelope estimates to establish "small cap decouplings." This is highly active, specifically via bilinearization arguments introduced by Bourgain and Demeter and heavily modified by Oh, Maldague, and Guth for the moment curve \(\mathcal{M}^3 = \{(t, t^2, t^3) : 0 \le t \le 1\}\) in \(\mathbb{R}^3\) [cite: 9, 26].
2.  **Refined Shifting Variables:** The classical shifting variables argument (introduced by Wooley in 2012 to improve Waring's problem variable counts) has been upgraded. Oh and Yeon (2025) successfully refined this vector to apply to \(L^p\)-norms of exponential sums without restricting \(p\) to even integers, allowing for sharp bounds over restricted spatial integrals where pure decoupling stumbles [cite: 7, 11].
3.  **Nested Efficient Congruencing:** For arbitrary number fields and finite fields, decoupling is effectively paralyzed. The live vector here is nested multigrade efficient congruencing. This bypasses continuous geometry by enforcing intense \(\mathfrak{p}\)-adic arithmetic hierarchies, conditioning variables modulo \(\mathfrak{p}^{a+1}\) to extract non-singularity directly from Hensel's lemma [cite: 3, 4, 28].

**Exhausted Approaches:**
1.  **Naive Multilinear Kakeya-Brascamp-Lieb Inequalities over \(\mathbb{F}_q\):** The cornerstone of the BDG decoupling proof over \(\mathbb{R}\) fundamentally relies on continuous multilinear incidence geometry (Kakeya). Attempts to cleanly port this to arbitrary fields or highly restricted sub-domains failed [cite: 3, 4, 29]. 
2.  **Square-Root Barrier via Classical Circle Method (Inhomogeneous Systems):** In inhomogeneous systems with \(s \le k(k+1)/2\), traditional Hardy-Littlewood minor arc estimations are exhausted. They cannot penetrate the "convexity barrier" (square-root cancellation). Progress strictly requires subconvexity formulations imported from the Extended Main Conjecture [cite: 15].

## 7. Cross-References

The findings in the post-VMVT sphere act as foundational primitives for several adjacent grand challenges in arithmetic geometry and harmonic analysis.

**Related Open Problems:**
*   **Waring's Problem in Algebraic Number Fields:** Wooley's nested efficient congruencing has direct consequences for the number of variables required to represent a totally positive integer in \(\mathcal{O}_K\) as a sum of \(k\)-th powers, pushing the boundaries established by Birch and Siegel [cite: 20].
*   **Manin’s Conjecture for Fermat Hypersurfaces:** Bounds derived from function-field analogs of VMVT directly govern the asymptotic distribution of rational points of bounded height on specific Fermat hypersurfaces over function fields [cite: 30].
*   **The Riemann Zeta Function (Zero-Free Regions):** The sharp estimates for exponential sums with small frequency separation on the moment curve (via small cap decoupling) feed directly into exponential sum bounds that dictate the size of the zero-free region of \(\zeta(s)\) [cite: 8, 24].
*   **Falconer’s Distance Set Problem & Bochner-Riesz:** The scale-dependent Brascamp-Lieb inequalities used to resolve Parsell-Vinogradov systems [cite: 21, 31] are actively functioning as candidate primitives for analyzing pointwise convergence of Schrödinger solutions and improved Kakeya maximal conjectures [cite: 32].

**Anti-Anchors:**
A critical anti-anchor in the current research matrix is the assumption that continuous decoupling is strictly superior to arithmetic congruencing. While Bourgain-Demeter-Guth is celebrated for its elegance over \(\mathbb{R}\), Wooley's formulation remains structurally irreplaceable outside of \(\mathbb{R}\). The community is cautioned against anchoring exclusively to harmonic restriction paradigms, as the deepest results in non-Euclidean spaces strictly require the efficient congruencing apparatus [cite: 3, 4, 29].

**Sources:**
1. [qseries.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETMGGV8YDSaXJ4Mm8a1alxfTvp9jN0S0acopuUOF-2o9yLzBHbJH0rrexw2eNLRgdKXQiM20LIfOscPyUC4mek_cH1edyKQQZwsaf2kN5XiboaPs3LHjGkroI2gWQtsw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdwKJN0wRI8qjm2u1sSdsSvs-WWyH2WNubrPAwAgI524Ywby8pjRrPajs18A4F4rf9u1AhiiGz87sSJ7-bOZ63Mp5VDOILp8Q8xP0SpOQX_M9N7VFN5w==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0iH_fnLq_aMrZEhK9oVMDqghlcyB6iRXcOYSMSj-7Wo0p4AHyjojjfy8XKWfVRHsyyugEPOD27YjjdZQYbxo56o2A_-_c9WNUtty126CGLogONW9Ntg==)
4. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmj10YG1RgFEwciL7QIAHTWyxAFe2KGsMpp6qimiDemM_rVISTw3XdY5gKe8mlbZD0REd1jn9DKyw-OhlCjNdvoMhPwbYAOq11bG3lNCv1cOGPrBu50ZzBUTH8YwFyAW98u1OCYp9kbx8ibA==)
5. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTyzL82zVApeFrDHOdwILCN4ufegaAOS6d3TQ7eOvxy2Z7n5uWSzgOhEq7if2zMAIM03Z9_fmlKNkU6GP1ZUWCjK_bSIMB_rJkhJ5PWj4qScM78OsG1d3uiXIDZoQq15PORXoXrETc478hRDLnrW-_1iAMr8ZOIludhKp3ePnfeS0LdQG8razTIVkn4jyTuOWHpqzzLFVG2JIcWl0T5s6XYcCgX8h2AQF3D0Ju9TC4VnKuQPRNG6crCd6beXM3TwOGZa-0D_pRBCeDeMJxXjST8joUw96HXqjoq0xnmQo=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfRfMfd4scZZsIOxgC1deLRdgmbbvB94LmsZiwzRUYhKFz5Jjp_GEkoQPNgqzKfm392jVNZdWKxAELtZ0MBGD9_fDyDJXElOKgt-N3-pahiCS3DzZG6w==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuHsQTDR22ZPhjrtv8uLjU-c7tfJ2d-Pku114MOd5If1rnWhIMC5nUguq09MKDz9uCuHv3krWgr1uMRqAoK4sXxomuLRzQpZLclXjVhUTnLjHGNhfNVw==)
8. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYx23Zu4soxl-FbZRvDfqDN8EMqDmbSk0MrKJNJGflYMRS_pIAQ1POQGMtMDo5S-AiUM38XrRRrnBlx2NylRVIVimYBHllAaf4J4KJp8efOfeA9OB-G5z6la4whdO2ud4=)
9. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFkmkyfOB1jzL0wcCbWVnwbJgy4bYd6S8EbiyWYYa6LifYc6i-cGpVn9rY614auzkJdCzdDnZILpXVLyXlWIMEGIn_K88YAqwrlozm2gHTq7lGHYnN6qoSaOQ3uyvfJmFiH6XxWQ==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsvfBYmrzS_KaCxEvKPSPGLbG6uQChwTdGRHlqddbC6eg1EDgpQd2D1w6-hg7lM79j0mF8Pde_mZaX6TVPJWMIywymnLN91eqajAvNIs8U1-IdbXXdO_hQgw==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEA5ABLPkEmo34Rcc2ttBiV-vJ4ovwrKd8RzsJ8RutuRmj5orVbrvJNdC-tgSVHMTO-lbG4Nj6GTgr9n2BeCrskrjkP89qfOkP3rffM8Dx2RAQkBpRm6A==)
12. [unipr.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJQ1B723G9j3qHyE_Z8qB0_nUu4u8AZhvdleWbQfAfOfZsQCDGEDiZ2ZMvgWzkPxyExy6KadkkNvTHxU9HOHqBWxrOiPq4joN1l7soFbNMF_fNhnuL58nVDYUsS_FPrKy_AhkoIb_ciezcOWePQP8=)
13. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGomjNA33MolsTQ3GIQGQxg9gddDJ4CThQviKDCNoPnVsHQbn1T-krtxxg7lDyA8GrFGTzgZD3PUp9iz9dWBVaFP7_Pkz0Ysdxz0Ufv5---wvDzq79rzh8Ob4zPEzJlAIpeJ9FU0NgTh8Jqz1kb4xAv9_joDJn6xXFsf1-N937H13VwEAIe4ucCYgyc3Wfzbj9o_1QUlbiZdkwKUU=)
14. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyk8eidpVSvxajmvgGl3dwqYDPhwdyr2FCG9e7x1n-Haxy_QmCiiY2DXQsYOMDGquCD1zqqAtXSZz3EK77sxI8tFGwTynVkuQgVk6TfZFeEXP2JyBoUwWN7M5N8H9icnfSy0IUEQet6XEa6YtTVnvVbrCUxLuQ3dBw0QfbogvOkWlKm4iipss3We-oOZfHB2VchG5PyXPjTpT9YM7sAKLb-MkfzDiK4hBsZtx4qOTrgvVzJERMLIkNTlagXHH96KXB4w6jCenR)
15. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxIR1llpRMiWHmvDQRSZNFwK3gIF8mx4lunJNE-NdPEegkbTr7AikXg--gtEGGWe2BfUqJG4do-yt15sotuHHFb-DIfrYJzMAK6uYBp-WrgAkCAmk1AMYM01xudFuZUyfeolxiqG3zUDONfQbK2Q==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFi3Yzx_rFHJIvAPMxU5QREJ29HFn7igyvThzkBrTNkrJr7n7hrP287pZnlzmDWjKXF58gR5oGwsnuIaT9OFl_mSehBIvoLbrZlDw54PCWii4nwkKOT6g==)
17. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfC9R5Da36SM8ucCLXSqmf6nsgq-0FMlahjIvDiLWbYHS93ujKU-UNGeefaPpBcV0Qy8gpHysNbSTw3CdpGSbcW3kR6OItFZYAO27bhX70Aw8uYEX-WqNmHD8CrqfbYkspzxdujuQIXqDvc9vU8io=)
18. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpX93roORlKrzH2y3MMHyIG7cEOYc-8IE_u2YQctQ1Aca8XyyiFht6lPqah4JpEPhY0SCR6YSx1_nzLqJwBQEPxk0vtId_yjP0mICoERgo-DQuLAkSlRh-fdNUPMCE0HnzsES2CqOXEF2Gw9_JiJeqMdp5trjHn5olIsEj0sRb3A==)
19. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYQulyVOeD2wb8wnyjTsdy2RTbSfbO2E2O7luSFNX1w43l6m6a1IBuQ7r605zCIK2WBdHIqbhuviff420HvdJnwWTXZMdcf-6T7x-I_EYtJNH36X2g368JO05QJFfmo1iEMfwe15cdNuAG7sKa_XcYRb0T2hgNAogX8mWl5aQd7r-zVw==)
20. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOA9eGt-vPPJyT6rTVqMIfTc5b5SFj-PdulxNXrq6j85HkJSIenGQpil8WofRqZ55IB3uiPyaNZCHOxx0MsMmXV8JpO2NKkCSsCXuq0k1cU-UTt6WTKWFtIjqoIePwD5fpqSB8ijArNs4vVDd1P5zoVq24X8h67V562ZUIOu74wwRZaPKJLGTraSiTBnfHJUKAnez2i1vsOoLSNoDmsJHEgr2UP58UjZWQxow8lsWjwDFa-Wec3_FCA3NTarJMQYwKehTqdHxMOdRSR3maApzs3pkwmntfvY4qZuqBTlcqnXu0zJ0rnrTNoJyv4zQytq6l9g==)
21. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJKd8hhI0DL_ftbG5mCNTHNpsXBmNpXTeFo3j-xEpt6Pk1woiyAJCrWSa6xQ7Gu1yd_a0cvpYGU49WxsFciScAxuFQDAGqIEM8VtHQsx8hZUlZDCydH3hqAl2xYB6xAD4=)
22. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTO_kEMzxpPVFOc2tvP0Fv8CB-nwBtcVqMHMOWlbKxzg6QC2TSspxl7fuqDXC7v0nKHbK21nzaB2C5oXbvz2FP89Yx-e1FLVmqc0aHRs9gAMAbr-Br4ZzGJlzYvuc-j2CquA==)
23. [chalmers.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHEsabrNGke5MbR-8UyTEH6tOSW4vJqGkmg2McFv3vDmL6zWC5Mnx7iXT2jLQXdNcGJFql-NDUMG2kHB1sEBHhUv5Mu-Ieadw15MyiE9slgvadapQT0zHZ1vG3bgB8rDLpA1EW58qLUg==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXIYtVJs8TD7XbZUO1XyWlX2iGB5aSepYrWKUsHSrolByFTWzf9V0w85e7K0vUNfTJc2M8XihgKHQMxsWIjB-6-EBdDoQyob31hoEChC_UMh13z8XVRg==)
25. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHN5sRYvVCNlD2zO6WlRcyx7mBj4zRYi2E1jmk6XKVn0VY5-NnXNyH7WDZk2ahe6rd6HpUfBuKFUBLjiDpCILdb1q90gkzQoHlkV9EDOSlpqRCGPln2JVfZ76EjggdFFp-435m2gerrHcuD8C8FtFb7cNLxDQp5P6h7IyU0sbDcfuQcFto=)
26. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYn5tqETIEiRJoBLY6xgzGgmk9fBRzBkFpuOoqV67aXNiZ5Pu2l0jQ6QtavrPia5AkgstHCjElmLCvNuPw8f6XIVH0m0-ORmCpqukIJM0eciKqIUInH47cLuJVhFGXyPRJyaLTSjP9FftTjvU=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFk5evEWQCyGtdwI3kN8ltgdYDEWGntdLS3OGbUFpX-lErtbh1JBf9bdGHHc7ll6qoVpeUS9Z0Ciua_zzHTGyHVvL1oMHXzlMB9ne8pfAbvw2oHjnygQ==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbux6nqbr5rtlQy4yLmhX6Dqj6HRJre5rjxwbuN8dQY4QRNS8MOqpb1FGBFiz0MkMy8Oiuv8jLfyBXztmPY6dxp0zJyBWdO3jt0-anFXson9GRwnLo7g==)
29. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4yMvNm-PlmV50pcYiDGhvGBtviUrXxGZ5autr-HY33xUjVSbBRBqbIc20afNFRWI934adctPKeIq2fWhhA_3bUBHljoPvDUnSn8NrkjwDt3cHwpHS3TSXxl-6TrON4Tw=)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYrMgHg0XDY2RfeOzkecHo7Vzq8sFfHNJwu3Ufok7wW3HrHqHbjosQjsCf8lZ5ZzAFLYYBZ13CuZ6fVs7I1QN3svgZt_uWHGfvOTHkpc9bQ1Kg1ESMUO1EsUNvAjhTB5BAKCbbV8ugcP5rnZaBINipecPEdXJ7Rp22RRr-uhwMXpleSWkkB9Lq0ifocemoMAKyGc4ieJZaOtFAkqN5waogKDhahTPYtDC56jGHaKSwMTtAQ9i3dmniHd0t9B7nZZIQjfLAdIUj)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcIB2wVzjJnwWJv0jqT6lXpztOvk3lQSExAd35Z1QD8EMzTt2DFXyLQ6d493cHlednMfmw24etIfHDY0W2mrdHvSq2-oKu74lVo1Sm1sSS0t1EXIadFw==)
32. [google.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGEzwdpDdFjOBy_8mRCqGKs4n6cOKGG7fwggEkJDkaxKXxKtMQ0hp53rVz3ErC3hYX5tLmQ5osUyBDMPgG-vGkfB4e4HmhWV0yx1AYV_LMMwygn8gHnPmwsBIUApmbdw2ONJyQfmd2WxdT-GLfJKPr2Q==)


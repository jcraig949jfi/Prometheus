# Prompt 16: DR-016 — Re-verify AA-005 CACTUS_BARRIER_6M_MINUS_4 (Buczynski Feb 2026)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdqcWNCYXE3NklKUFZfdU1QOWRhZ3lRTRIXanFjQmFxNzZJSlBWX3VNUDlkYWd5UU0
**Elapsed:** 455s

---

# Verification Report: AA-005 CACTUS_BARRIER_6M_MINUS_4

The following substrate evaluation directly addresses the re-verification of the anti-anchor candidate **AA-005 CACTUS_BARRIER_6M_MINUS_4**. 

*   **Key Finding 1 (Refinement Required):** The candidate anti-anchor requires immediate definitional refinement. The strict $6m-4$ barrier applies *exclusively* to **linear rank methods** (e.g., Koszul flattenings), not to all determinantal methods. The literature exhibits a profound coordinate collapse between "determinantal equations" and "linear flattenings," which must be decoupled in the substrate.
*   **Key Finding 2 (Barrier Broken):** The deterministic boundary of the cactus barrier for border rank has been breached as of February 2026. Doležálek and Michałek have introduced **nonlinear maps** (Kronecker-Koszul flattenings) that successfully distinguish secant varieties from cactus varieties using determinantal equations. 
*   **Key Finding 3 (Strict Coordinate Separation):** Validating this anti-anchor requires strict enforcement of the HARD-5 coordinate separation between **tensor rank**, **border rank**, **cactus rank**, and **border cactus rank**. Linear rank methods bound border cactus rank, which maximally fills the ambient space at $6m-4$ for $m \times m \times m$ tensors, while border rank remains unbound by this specific threshold.
*   **Key Finding 4 (Substrate Actions):** Downstream consumers (catalog edits, work-queue entries) must integrate the newly discovered tangency flattenings as actionable primitives for proving border rank lower bounds beyond $6m-4$. 

## (a) PRIMARY SOURCE CONFIRMATION

**Substrate Input / Source Anchor:** 
*   **Primary Source:** Jarosław Buczyński, "Cactus barriers." 
*   **Status:** ANNOUNCED-NOT-PUBLISHED (Preprint).
*   **Identifiers:** arXiv:2602.11309v1 [math.AG] [cite: 1, 2].
*   **Date:** February 11, 2026 [cite: 1, 2]. 

**Definitional Isolation:** 
The anti-anchor under verification proposes that a fundamental geometric barrier prevents determinantal methods from proving border rank lower bounds exceeding $6m-4$ for tensors in $\mathbb{C}^m \otimes \mathbb{C}^m \otimes \mathbb{C}^m$. The primary source explicitly confirms the existence of this barrier but restricts its domain of application strictly to *linear* rank methods, effectively supplanted previous ambiguous nomenclature. 

Buczyński formally dictates the coordinate collapse in prior literature, noting that what were historically termed "rank methods for complexity" must be re-registered as **linear rank methods** [cite: 1, 2]. 

**Theorem Registration:**
The definitive geometric reason for the $6m-4$ limit is the inclusion of secant varieties within cactus varieties, and the subsequent saturation of the generic cactus rank. Buczyński formulates the following definitive substrate input:

> **Theorem 1.3 (Cactus barrier for linear rank method):** "With variety $X$ and matrix $M$ as above, if in addition $X \subset \{\operatorname{rk} M \leqslant k\}$ then $\mathfrak{K}_r(X_0) \subset \{\operatorname{rk} M \leqslant k \cdot r\}$. In particular, if $g$ is an integer such that $\mathfrak{K}_g(X_0) = \mathbb{P}(W)$ (for instance, $g$ is the generic $X_0$-cactus rank), then the linear rank methods will never provide a better lower bound on $X$-border rank than $g$." [cite: 1]

For the space $X = \mathbb{P}^{m-1} \times \mathbb{P}^{m-1} \times \mathbb{P}^{m-1} \subset \mathbb{P}(\mathbb{C}^m \otimes \mathbb{C}^m \otimes \mathbb{C}^m)$, the generic cactus rank fills the ambient space at exactly $g = 6m-4$ [cite: 1, 3]. Because linear matrix flattenings map the cactus variety directly into the rank locus, the vanishing of their minors can only attest to bounds on **border cactus rank** (coordinate #4), not strictly to **border rank** (coordinate #2) [cite: 2, 4].

**Constraint Verification (HARD-5):**
The primary source explicitly separates the coordinates. It defines $\operatorname{r}_X(F)$ (X-rank), $\operatorname{br}_X(F)$ (X-border rank), $\operatorname{cr}_X(F)$ (X-cactus rank), and $\operatorname{bcr}_X(F)$ (X-border cactus rank) [cite: 4]. The central substrate finding is that $\operatorname{br}_X(F) \ge \operatorname{bcr}_X(F)$, and linear rank methods strictly evaluate $\operatorname{bcr}_X(F)$ [cite: 4]. Thus, the $6m-4$ limit is an evaluation of the maximum generic border cactus rank, not an asymptotic limitation on the border rank itself.

## (b) FOLLOW-ON WORK (2024-2026)

The 2024–2026 window exhibits a volatile, rapid phase-shift in tensor geometry, actively overturning the absolute gravity well that "determinantal equations cannot distinguish secant from cactus varieties." 

**1. The Nonlinear Determinantal Breakthrough (February 2026)**
*   **Source:** Matěj Doležálek and Mateusz Michałek, "Nonlinear methods for tensors: determinantal equations for secant varieties beyond cactus."
*   **Status:** ANNOUNCED-NOT-PUBLISHED (Preprint).
*   **Identifiers:** arXiv:2602.12762v1 [math.AG] [cite: 5, 6].
*   **Date:** February 13, 2026 [cite: 5, 6].

This source definitively supersedes the absolute boundary of the cactus barrier, demonstrating that it is an artifact of *linear* embeddings, not of determinantal methods natively. Doležálek and Michałek introduced a new flattening framework: **Kronecker-Koszul flattenings** (and generally, Kronecker-Young flattenings) [cite: 5, 7]. These utilize non-linear maps from tensor spaces to matrix spaces.

**Primitive Registration Data:**
> **Theorem 1.1 (Doležálek & Michałek, 2026):** "For all $n \ge 14$, minors of size $n(n-1)(n-2)+1$ of the tangency flattenings vanish on the $n$-th secant variety of the Segre variety in $\mathbb{P}(\mathbb{C}^n \otimes \mathbb{C}^n \otimes \mathbb{C}^n)$ but do not vanish on its $n$-th cactus variety." [cite: 5]

This explicitly bypasses the $6m-4$ constraint for border rank lower bounds by proving that determinantal equations (specifically, tangency flattenings) *can* distinguish secant from cactus varieties. For example, for $n=14$, the minors are explicit polynomials of degree 4370 in 2744 variables [cite: 5, 6]. 

*Flag Warning ("Y proved X"):* The preprint claims a new, computer-free proof that the border rank of the $2 \times 2$ matrix multiplication tensor is 7 using tangency flattenings [cite: 5, 7]. While highly credible, this is an ANNOUNCED-NOT-PUBLISHED result and must be flagged as CONDITIONAL in the execution queue pending structural verification by the substrate.

**2. Deformation Theory & Smoothability Correlates (2023-2026)**
The foundational mechanism for breaking the barrier relies on the smoothability of finite schemes.
*   **Source:** Maciej Gałązka, Tomasz Mańdziuk, and Filip Rupniewski ([GMR23]), "Distinguishing secant from cactus varieties."
*   **Status:** PEER-REVIEWED. 
*   **Identifiers:** Found. Comput. Math. 23(4):1167-1214, 2023 [cite: 6, 8].

Buczyński (Feb 2026) isolates [GMR23] and [DM26] as the only two known ground-breaking results that break the cactus barrier [cite: 1, 2]. [GMR23] translates smoothability constraints into tensor language, proving that finite schemes underlying the cactus variety contain components that are not smoothable [cite: 8]. Because secant varieties strictly require smoothable schemes (limits of isolated points), identifying non-smoothable loci mathematically isolates the cactus variety from the secant variety. 

**3. Border Cactus Decompositions (January 2026)**
*   **Source:** Weronika Buczyńska and Jarosław Buczyński, "Apolarity for border cactus decompositions."
*   **Status:** ANNOUNCED-NOT-PUBLISHED.
*   **Identifiers:** arXiv:2601.19558 [math.AG] [cite: 9, 10].
*   **Date:** January 27, 2026 [cite: 9].

This work extends the border apolarity technique to cactus varieties over toric varieties, introducing the "border cactus decomposition" as a distinct mathematical object defined via multi-homogeneous ideals in the Cox ring [cite: 9, 11]. This further solidifies the need to cleanly separate coordinate 2 (border rank) from coordinate 4 (border cactus rank). 

## (c) FALSE-FORM RECURRENCE

The gravity well in the literature conflates the failure of a specific methodological mapping (linear flattenings) with the failure of a broader algebraic structure (determinantal equations). The false form is routinely observed in complexity theory literature, asserting that *no* determinantal method (method of minors) can break the cactus barrier.

**Recurrence 1: The Coordinate Collapse of "Rank Methods"**
Recent literature fundamentally asserts that any equation generated by taking matrix minors is blind to the distinction between secant and cactus varieties. 

> *Quote from literature exhibiting the false form:* 
> "The geometric interpretation of the border rank lower bound barriers of [EGOW18, Gałą17] is that all equations obtained by taking minors, called rank methods, are actually equations for a larger variety than $\sigma_r(\operatorname{Seg}(\mathbb{P}A \times \mathbb{P}B \times \mathbb{P}C))$, called the r-th cactus variety [BB21]." [cite: 6, 12, 13]

This exact phrasing appears in:
1. Conner et al., "New lower bounds for matrix multiplication and det3," *Forum of Mathematics, Pi*, (May 2023) [cite: 13].
2. Quoted explicitly as the standard accepted barrier by Doležálek and Michałek [CHL23] in their February 2026 preprint [cite: 5, 6].

**Analysis of the False Form:**
The false form equates "equations obtained by taking minors" with "linear rank methods." As proven by Doležálek and Michałek (2026), it is **not the determinantal expression** that creates the cactus barrier, but the **linear embedding of the tensor product into a matrix space** [cite: 5, 6]. By utilizing non-linear maps (Kronecker-Young flattenings), one can construct matrices whose minors *do* distinguish the secant from the cactus variety, bypassing the $6m-4$ limit [cite: 5].

**Conclusion on Recurrence:**
The anti-anchor is strictly required, but its current naming and scope (`CACTUS_BARRIER_6M_MINUS_4`) inadvertently reinforce the false form by implying an absolute barrier for determinantal equations. The anti-anchor must be structurally inverted to explicitly target the false mapping. 

## (d) RECOMMENDATION

Based on the primary source confirmation and the 2024-2026 literature phase-shift, the substrate must execute the following state-updates.

** (i) Anti-Anchor True Form Status: REQUIRES REFINEMENT AND INVERSION**
The candidate `AA-005 CACTUS_BARRIER_6M_MINUS_4` is correct regarding the numerical threshold for $\mathbb{C}^m \otimes \mathbb{C}^m \otimes \mathbb{C}^m$, but actively toxic if left unqualified. It propagates the gravity well that determinantal methods universally fail at this threshold. 

*   **Action (Catalog Edit):** Rename AA-005 to `AA-005 LINEAR_RANK_CACTUS_BARRIER_6M_MINUS_4`.
*   **Definition Update:** "The generic border cactus rank for 3-way tensors of size $m$ is $6m-4$. Consequently, any linear rank method (e.g., standard Koszul flattenings) cannot prove border rank bounds exceeding $6m-4$, because linear methods strictly bound border cactus rank. This barrier does NOT apply to non-linear determinantal flattenings."

** (ii) New Sub-Anchors & Primitive Registrations**
The verification scan discovered a critical paradigm shift requiring new anti-anchor pins to redirect agents away from the determinantal-failure gravity well.

*   **Register New Primitive:** `KroneckerKoszulFlattening` (Source: Doležálek & Michałek, arXiv:2602.12762).
*   **Register New Anti-Anchor:** `AA-005.1 TANGENCY_FLATTENING_SECANT_DISTINCTION`.
    *   *True Form:* Determinantal equations obtained via nonlinear tangency flattenings vanish on the secant variety but do not vanish on the cactus variety (proven for $n \ge 14$). Thus, determinantal methods *can* break the cactus barrier.
*   **Register New Coordinate Delineation:** Substrate input rules must flag any collapse of "determinantal method" into "linear rank method" as a critical coordinate failure. 

** (iii) Work-Queue Entries for the Verification Subsystem**
The following emergent claims from the 2026 literature require immediate downstream processing:
1.  **Work-Queue Entry 1:** Verify the ANNOUNCED-NOT-PUBLISHED claim by Doležálek & Michałek [DM26] that the Kronecker-Koszul flattening provides a computer-free proof that the border rank of the $2 \times 2$ matrix multiplication tensor is 7 [cite: 5, 7]. Route to the automated theorem verification module.
2.  **Work-Queue Entry 2:** Evaluate whether the nonlinear determinantal bounds of [DM26] scale efficiently enough to challenge the theoretical $O(n^{2.37})$ matrix multiplication exponent limits, or if the degree inflation (e.g., degree 4370 for $n=14$) renders it computationally intractable for asymptotic tensor complexity limits [cite: 5, 6].
3.  **Work-Queue Entry 3:** Ingest the definitional constraints of "Border cactus decompositions" (Buczyńska & Buczyński, arXiv:2601.19558, Jan 2026) [cite: 9, 10] into the primary algebraic geometry taxonomy graph, ensuring it is topologically distinct from standard border apolarity algorithms.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQNfHNEkIi4YveAt3LafuttMPRrNBt34TTam8RiLpGkxsTV6vVF6wcxGca2vlm_jAp3Mc-lgbv_duK5wBThjkfxYZ-EREmgO0QTho4quKnmIbntXPhJmLJjg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERggu2ouAukTLVhmmz15hD2ddw6Kp4eEaUaqyxGMjZlBQAGgx9Vd_qSA35wP_YQwJxYav1YYVYpRa95GZwkhtZlGBseMW13VmMSL5rE1xEFnrsKAgfsA==)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH46EI3OHrxmRHPutSrqHrWfnhOR6Q5NVXujB41RJIIKieZQwRw3oS7FzrESDwIUTM2UkjBNj2RDzOuQaVcNmULi5iQr0hsnhmGg9oyFND_U_OvaNxWZEeO_66MNrMsPuDTKgYVegZceihk6c39v05-BL1VZlHRXPDpOqh8kk7bNtxTFvlIbjgiBOl8P2ghoYCL3tK-ab_95e5fX3F8AhF2LT2nLdpYRY95pC9WbsLJbKHQ108AF44oz8F_g_AP7kgL-URLMw8FMnHgwE6rzkKondPJoIN8nzk=)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmn18drxPnknKkFFel6Y2Xh-cJfjw0tpe3sOLMFP6nY7V84CVnvvevEFJG4RGSBd7drmzWKxxchXFaqNuiUcFdhZJYzOrd6NJTUsq61dPVvHA96QUcEPWDKr1bSNpiKUEdnm6n_bcY1AE21mA8lEPoLIjFZz5opbw=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEy8tLE0xoPGa7W97hpvAgrZPbi1WpQMnY4jHC9LNIobswl482Msx7JB9BWKKF7oiIrIlS0U3X5rdzi2UPCgxMXqDKBU3_xgmJ7JcG2y2rF4L4eVRq0HJ-38Q==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHle0JR8SZc5AkIF-4A2l2jNWlYrIhqf5mk2Wx5acXWojc8alzQQR1N29v0U5i8U1ezlfJGAMfp0brLeSiSU_HTr6NCvt5I071CVCeiqdZJ4QKbtUV5ug==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGg8oeRZlW5jBUTT8pDiDRjvOJhOROG54k0CE95E8j_7SXfSjSRL2RrHpnzrLHugXhZo7xySaoKtTOhwbF_Mc4cjbgkKA8nMft6G-LBLwbkCz1f2zlw7Q==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNeoxYWhSK_0VK1vIh7Ye1QUw6bDBTgmXF3pgKA-AD-GnBeATrDZByFMti5lOME0gogRJlftFlZ4l7EI1Mjd28PnNkP7j5bYQJEzAQluFsIL6HszmxLg==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELHtozlehI6gf7wo24V8xZphSV0JH_VmhuR-3qWb3RZqZ_810Mq3qyHqNlFL895J371q_cVRF8RJY3qImMpZmYk_hJHpPILE7ZY3X8V1TdOBuzj1UnYWHcUA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1pHNQlMI03MoxhaRYvBDafe7czUmFF4Kstxtayis0fxQlrbuoRmIDNLG4WxuzhY9jAg38utlYUiMPcwm4GjXuoBVGbt0xggpnQgliVqNzQ-1Y9cqvIF9tOiR4NA==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHq1UZqtTIgBzWcw5TT5LgEpQHkpifZh-RcWbCXEdx09E--Jvwbux0Ctnz_gHHPVScCw-LFrjuoU7FS4s2VWtDSPXNGAwZuUiKTQsJ7yu2jia5y-e3oJWC9uYJgECOrcYY6GLj6v41ijb0LANuF)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9pYicOeXW-6SCgjqll4heyd0F8xfmV-zJdgHUaFPf14PB65ZXd0nvOm_hwqn7FfZuXjhljLNFdec5vblaEl4cqOvo3h33XSw2No8akPCN5I40dw1J_0wMQF7fPS6G5FLyXs7RgpSeYZJscKryR4rj67lTDg0Oq-LQSkbOmG5qWLMC3vEHxKwo1tnMxwrSsBSCprfVeCSHsvnY)
13. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHq0ggeYfPO74YHUJTxtJCGmgNjscrm_WKrjodwIzNoAaz8wDfmhszP92baLOwI11OxYQ1WlvAdhQI13OahUe_lF979DvWD2HBOrihPiBzl8JGZkPTRKq0DjuaIDN8D5cR2sz4BjXCbnZuJdx9c3HSMhHob7kPPa6HZuQj9M_e9ZP3h3f1Qb9TqZ_3fObUNA-3aPNBH2m5Hcy-ovA8EWlfcgdc0yF4sb9ck-RVC_tnyX6EGhduuxRcrUU1egSO5H9LKNWGOrvFk-WSWddY_O8kOGXwX6pRT1aQXqCwgRFKKpg==)


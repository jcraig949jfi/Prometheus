# Prompt 15: DR-054 — T#7 Border rank multiplicativity under tensor product [Tier 2]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdZSVlGYXJtcEM5aU5fUFVQM00tNmlRRRIXWUlZRmFybXBDOWlOX1BVUDNNLTZpUUU
**Elapsed:** 272s

---

# T#7 Border Rank Multiplicativity Under Tensor Product: Anti-Anchor Verification

**Key Points:**
*   **Unconditional Strict Submultiplicativity:** The hypothesis of exact multiplicativity for border rank under the tensor product is unconditionally false. Primary sources rigorously confirm that border rank exhibits strict submultiplicativity under both the order-increasing tensor product (\(\otimes\)) and the order-preserving Kronecker product (\(\boxtimes\)). 
*   **Coordinate Separation Imperative:** Mathematical literature frequently exhibits a gravitational well that collapses distinct invariants. Tensor rank \(R(T)\), border rank \(\underline{R}(T)\), cactus rank \(CR(T)\), border cactus rank \(\underline{CR}(T)\), subrank \(Q(T)\), border subrank \(\underline{Q}(T)\), aided rank \(R_{aided}(T)\), and positive border rank \(\underline{R}_+(T)\) behave differently under algebraic operations and must be registered as independent coordinate axes in the substrate.
*   **High-Value Drops in Recent Literature:** Work spanning 2024–2026 establishes extreme cases of strict submultiplicativity, specifically regarding Kronecker squares of skew Coppersmith-Winograd tensors and iterated matrix multiplications, which are critical for overcoming barriers in Strassen's laser method. 

The following report validates the T#7 anti-anchor candidate against primary literature, neutralizes conventional framing gravity wells, and formats findings for immediate ingestion as primitive registrations and catalog edits for the Project Prometheus substrate.

## (a) PRIMARY SOURCE CONFIRMATION

The anti-anchor candidate strictly concerns the failure of multiplicativity for border rank under tensor products. To register this finding, we must anchor it in PEER-REVIEWED primary sources that explicitly state the non-multiplicative nature of these invariants. We must additionally separate the order-increasing tensor product from the order-preserving Kronecker product.

**1. Order-Increasing Tensor Product Strict Submultiplicativity**
The definitive primary source establishing the strict submultiplicativity of border rank under the standard order-increasing tensor product is:
*   **Source:** *Border Rank Is Not Multiplicative under the Tensor Product* by M. Christandl, F. Gesmundo, and A. K. Jensen. 
*   **Status/Date:** PEER-REVIEWED. Published in *SIAM Journal on Applied Algebra and Geometry*, 3(2): 231–255. Definitive publication: May 2019 [cite: 1, 2]. (Preprint originally announced January 2018 [cite: 1]).
*   **Theorem/Result:** The authors unequivocally answer the open question regarding border rank multiplicativity. They prove: "It has recently been shown that the tensor rank can be strictly submultiplicative under the tensor product, where the tensor product of two tensors is a tensor whose order is the sum of the orders of the two factors... It was left open whether border rank itself can be strictly submultiplicative. We answer this question in the affirmative. In order to do so, we construct lines in projective space along which the border rank drops multiple times and use this result in conjunction with a previous construction for a tensor rank drop. Our results also imply strict submultiplicativity for cactus rank and border cactus rank" [cite: 1, 2].

*Substrate Extraction Note (HARD-5):* This theorem yields four distinct coordinate verifications. Let \(T \otimes S\) denote the order-increasing tensor product. The source unconditionally confirms strict submultiplicativity (i.e., \(f(T \otimes S) < f(T)f(S)\)) for four distinct invariants: tensor rank \(R(T)\), border rank \(\underline{R}(T)\), cactus rank \(CR(T)\), and border cactus rank \(\underline{CR}(T)\) [cite: 1, 2].

**2. Order-Preserving Kronecker Product Strict Submultiplicativity**
A related but mathematically distinct tensor operation is the Kronecker product \(\boxtimes\), which multiplies dimensions while preserving the tensor order (e.g., a 3-tensor Kronecker-multiplied by a 3-tensor yields a 3-tensor in a larger space).
*   **Source:** *Bad and good news for Strassen's laser method: Border rank of perm3 and strict submultiplicativity* by A. Conner, H. Huang, and J. M. Landsberg.
*   **Status/Date:** PEER-REVIEWED. Published in *Foundations of Computational Mathematics*, 23(6): 2049–2087. Definitive publication: 2023 [cite: 3, 4]. (Preprint announced September 2020 [cite: 5]).
*   **Theorem/Result:** The authors establish a massive gap in submultiplicativity for the Kronecker square of the \(q=4\) skew Coppersmith-Winograd tensor \(T_{skewcw,4} \in \mathbb{C}^5 \otimes \mathbb{C}^5 \otimes \mathbb{C}^5\). The authors write: "Regarding its \(q=4\) skew cousin in \(\mathbb{C}^5 \otimes \mathbb{C}^5 \otimes \mathbb{C}^5\), which could potentially be used to prove \(\omega \le 2.11\), we show the border rank of its Kronecker square is at most 42, a remarkable sub-multiplicativity result, as the square of its border rank is 64" [cite: 4, 5].
*   **Coordinate Separation:** Let \(\underline{R}(T)\) denote border rank. The authors explicitly state: "Rank and border rank are submultiplicative under Kronecker product: \(R(T \boxtimes T') \le R(T)R(T')\), \(\underline{R}(T \boxtimes T') \le \underline{R}(T)\underline{R}(T')\), and both inequalities may be strict" [cite: 4, 6]. Specifically, \(\underline{R}(T_{skewcw,4}) = 8\), yet \(\underline{R}(T_{skewcw,4}^{\boxtimes 2}) \le 42 < 64\) [cite: 4, 5]. 

Both primary sources confirm the T#7 anti-anchor candidate is correct as stated, provided the type of tensor product (order-increasing vs. Kronecker) and the specific rank invariant are cleanly delineated.

## (b) FOLLOW-ON WORK (2024-2026)

Recent literature spanning 2024–2026 further contextualizes the failure of multiplicativity, introducing new variants of rank and degeneration that require careful primitive registration.

**1. Iterated Matrix Multiplication and Border Subrank (April 2026)**
*   **Source:** *Border subrank of higher order tensors and algebras* by M. van den Berg, M. Christandl, V. Lysikov, H. Nieuwboer, M. Walter, and J. Zuiddam (arXiv:2604.19872) [cite: 7].
*   **Status/Date:** ANNOUNCED-NOT-PUBLISHED (Preprint, April 2026) [cite: 7, 8].
*   **Finding:** This work investigates border *subrank* \(\underline{Q}(T)\), which measures how well a given tensor can be transformed into a diagonal tensor via multilinear maps [cite: 7]. The authors establish tight bounds for the border subrank of \(k\)-fold (iterated) \(n \times n\) matrix multiplication, proving it is between \(\frac{1}{k-1}n^2\) and \(\frac{k+1}{2^k}n^2 + O(k)\) [cite: 7]. For iterated upper triangular matrix multiplication, it is exactly \(\frac{1}{2^k}n^2 + \Theta(n)\) [cite: 7]. 
*   **Substrate Input:** Register the coordinate "Border Subrank" \(\underline{Q}(T)\) explicitly. The bounds achieved on tensor powers \(T^{\otimes N}\) highlight that asymptotic subrank limits are intrinsically linked to the submultiplicative decay of these coordinates over high tensor powers [cite: 7, 9].

**2. Kronecker-Koszul Flattenings and Cactus Boundaries (February 2026)**
*   **Source:** *Nonlinear methods for tensors: determinantal equations for secant varieties beyond cactus* by M. Dolezalek and M. Michalek [cite: 10, 11].
*   **Status/Date:** ANNOUNCED-NOT-PUBLISHED (Preprint, February 2026) [cite: 10, 11].
*   **Finding:** Classical flattening methods (Koszul flattenings) often fail to distinguish between secant varieties (border rank) and cactus varieties (cactus border rank). Dolezalek and Michalek establish "Kronecker-Koszul flattenings" and "tangency flattenings" that explicitly vanish on secant varieties but *not* on cactus varieties [cite: 10]. 
*   **Anti-Gravity Well Execution:** The standard gravity well in algebraic complexity literature asserts that "Koszul flattenings are the terminal method for border rank lower bounds." We must aggressively weight Kronecker-Koszul flattenings higher or equal, as they bypass the cactus barrier [cite: 4, 10]. This finding provides a deterministic framework for testing strict submultiplicativity instances without falling into the trap of conflating \(\underline{R}(T)\) with \(\underline{CR}(T)\) [cite: 4, 10]. 

**3. Partial Degeneration and Aided Rank (March 2024)**
*   **Source:** *Partial Degeneration of Tensors* by M. Christandl, F. Gesmundo, V. Lysikov, and V. Steffan [cite: 12, 13].
*   **Status/Date:** PEER-REVIEWED. Published in *SIAM Journal on Matrix Analysis and Applications*, 45(1): 771–800. Definitive publication: March 2024 [cite: 2, 3].
*   **Finding:** The authors introduce "partial degeneration," a limit along a curve where one local linear map remains constant [cite: 12]. To quantify obstructions to partial degenerations, they introduce a distinct coordinate called "aided rank" (\(R_{aided}\)), a generalization of tensor rank. They utilize properties of the Coppersmith-Winograd tensors to demonstrate lower bounds on aided rank [cite: 12]. 
*   **Substrate Input:** Register "Aided Rank" as an independent geometric invariant. Strict submultiplicativity properties of aided rank remain a target for the verification queue.

**4. Positive Border Rank Gap in Quantum Correlations (February 2025)**
*   **Source:** *Border Ranks of Positive and Invariant Tensor Decompositions: Applications to Correlations* by A. Klingler, T. Netzer, and G. De las Cuevas [cite: 14, 15].
*   **Status/Date:** PEER-REVIEWED. Published in *Quantum* 9, 1649. Definitive publication: February 2025 [cite: 14].
*   **Finding:** The authors prove that multipartite positive and invariant tensor decompositions exhibit gaps between rank and border rank (e.g., positive rank \(R_+(T)\) vs. positive border rank \(\underline{R}_+(T)\)) [cite: 14]. 
*   **Substrate Input:** This is a crucial vector for our verification sequence. While standard matrix rank is robust to small approximations (rank equals border rank for matrices), multipartite tensor rank can collapse [cite: 14]. Klingler et al. confirm that *positive* ranks also collapse, proving that correlation sets (like those from translational invariant Matrix Product States) are not topologically closed [cite: 14]. 

## (c) FALSE-FORM RECURRENCE

The false form under consideration assumes the identity \(\underline{R}(T \boxtimes S) = \underline{R}(T)\underline{R}(S)\) (for the Kronecker product) or \(\underline{R}(T \otimes S) = \underline{R}(T)\underline{R}(S)\) (for the tensor product). While no rigorous primary literature from 2024–2026 asserts exact multiplicativity as a formal theorem, a conceptual gravity well exists that induces functionally identical errors. 

**1. Flattening Lower-Bound Conflation**
The most prevalent false form recurrence originates from the behavior of lower-bound techniques. As noted by Christandl et al., "Interestingly, lower bounds on border rank obtained from generalised flattenings (including Young flattenings) multiply under the tensor product" [cite: 16]. Because flattening bounds are multiplicative, researchers in application domains (e.g., naive tensor network optimization, or introductory algebraic complexity) recurrently assume that the border rank *itself* must behave multiplicatively across tensor powers [cite: 16, 17]. 

*Instance:* Ballico et al. (2019) explicitly diagnose this trap: "Certain techniques to determine lower bounds on rank and border rank guarantee that the lower bound propagates to the tensor product and can be used to prove multiplicativity: this is the case of flattening lower bounds... However, both inequalities can be strict in general" [cite: 17]. 

**2. Cactus Rank Collapse**
A secondary false form is the persistent conflation of border rank with cactus border rank in computational searches for strict submultiplicativity. Border apolarity technology often fails to distinguish between the secant variety (border rank) and the cactus variety (cactus border rank). Consequently, assertions of the form "Method Y proved the border rank of \(T^{\boxtimes 2}\) is \(X\)" often covertly mean "Method Y proved the cactus border rank is \(X\)." 
*Instance:* Conner, Huang, and Landsberg (2023) note that "(stu) tests are tests for cactus border rank. Cactus border rank is not known to be relevant for complexity theory, thus the failure of current border apolarity technology to distinguish between them is a barrier to future progress" [cite: 4]. This false equivalence is exactly what Dolezalek and Michalek's 2026 "Kronecker-Koszul flattenings" attempt to rectify by generating polynomials that vanish on secants but not cacti [cite: 10]. 

**3. Closure Assumptions in Invariant Decompositions**
In the domain of quantum information, there is a recurring false assumption that sets of symmetric or positive tensors are topologically closed, leading to the false heuristic that positive rank equals positive border rank. Klingler et al. (2025) directly attacked this false form, noting that "the multipartite tensor rank can collapse for arbitrarily small errors... Can multipartite positive ranks also collapse for small perturbations? In this work, we prove that multipartite positive and invariant tensor decompositions exhibit gaps between rank and border rank" [cite: 14]. The recurrence of the false form—treating multipartite probability distributions as closed sets—is thereby dismantled [cite: 14].

## (d) RECOMMENDATION

**1. Primary Evaluation of the Anti-Anchor**
The anti-anchor candidate "T#7 Border rank multiplicativity under tensor product" is **CORRECT AS STATED BUT REQUIRES REFINEMENT AND DISAGGREGATION**. It successfully identifies a critical mathematical fallacy. However, executing this within the Prometheus substrate requires enforcing HARD-5 coordinate separation. We must shatter "Border rank multiplicativity" into precisely defined geometric operations and invariants.

**2. Substrate Ingestion: Catalog Edits & Anti-Anchor Pins**
I recommend immediate execution of the following catalog edits and primitive registrations:

*   **Catalog Edit A (Order-Increasing Submultiplicativity):** 
    Register `TensorRankStrictSubmultiplicativity_OrderInc` and `BorderRankStrictSubmultiplicativity_OrderInc`. 
    *   *Condition:* \(R(T \otimes S) < R(T)R(S)\) and \(\underline{R}(T \otimes S) < \underline{R}(T)\underline{R}(S)\).
    *   *Primary Source Anchor:* Christandl, Gesmundo, Jensen (2019) [cite: 1, 2].
*   **Catalog Edit B (Kronecker Product Submultiplicativity):**
    Register `BorderRankStrictSubmultiplicativity_Kronecker`.
    *   *Condition:* \(\underline{R}(T \boxtimes S) < \underline{R}(T)\underline{R}(S)\).
    *   *Primary Source Anchor:* Conner, Huang, Landsberg (2023) [cite: 4]. High-value data point: \(\underline{R}(T_{skewcw,4}^{\boxtimes 2}) \le 42\) whereas \(\underline{R}(T_{skewcw,4})^2 = 64\) [cite: 4, 5].
*   **Catalog Edit C (Cactus vs. Secant Decoupling):**
    Register `CactusBorderRank_Decoupling`.
    *   *Condition:* Explicitly decouple \(\underline{CR}(T)\) from \(\underline{R}(T)\) in all work-queue entries invoking apolarity or flattenings. 
    *   *Anti-Anchor Pin:* Flag any Koszul flattening lower bounds that claim to define absolute border rank lower bounds without verifying the absence of cactus geometry intersections. Promote the Dolezalek-Michalek Kronecker-Koszul flattenings (February 2026) [cite: 10] as the overriding tier-A primitive for resolving this boundary.
*   **Catalog Edit D (Positive Rank Gap):**
    Register `PositiveBorderRankGap`. 
    *   *Condition:* \(\underline{R}_+(T) < R_+(T)\). 
    *   *Primary Source Anchor:* Klingler, Netzer, De las Cuevas (February 2025) [cite: 14, 15].

**3. Work-Queue Entries for the Verification Queue**
*   *WQ-1 (Aided Rank Submultiplicativity):* Add a verification task to evaluate if the "aided rank" (\(R_{aided}\)) defined by Christandl, Gesmundo, Lysikov, and Steffan (March 2024) [cite: 12] exhibits strict submultiplicativity under Kronecker powers, and how it correlates with partial degeneration obstructions. 
*   *WQ-2 (Subrank and Iterated Multiplications):* Add a verification task to trace the submultiplicative decay of the "border subrank" \(\underline{Q}(T)\) as defined by Berg et al. (April 2026) [cite: 7]. Specifically, index the asymptotic bounds for iterated upper triangular matrix multiplication (\(\frac{1}{2^k}n^2 + \Theta(n)\)) against existing Strassen laser method barriers.
*   *WQ-3 (Multi-drop Line Geometry):* Implement a geometric search primitive based on Ballico, Bernardi, Gesmundo, and Ventura (2019) [cite: 17, 18], identifying \(r\)-multidrop lines and trisecant lines as necessary conditions for strict submultiplicativity. This provides a structural filter for generating future tensor anti-anchors.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNYN-FimahJDYbJaVwfqgo4SpPxbR-nOMHvy97Smfd3xJoAYs5IoFpyBsn2a2p5BxNk4Ogf7_KoUebYZJs11BZoAbbB3ge9YBDCDrvTbx2ZS_0D4Ftmg==)
2. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGABIKpPBJUS7jl0GMnro7GJXi4pnmEsLzLrCQnkWHi6oyK_IqFFcD-Nl16D0oATAa4MTE_gLCwjI-u9ZV4fGWgvuaeYTltAvPvHjHKNhRVVqw7w-_U7GHF8EKq7fUI8zXVGZo=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGV-YQM0mdbpkog9RgKx5p1b1pg22pSJSfB26Kt9MxvlsAfi4RA1FDCaEOZz3_XsqIbFchH2adHf16R-IFRDI5zgkgncwERBwzXQ3HXZO1FvwIHZcoVCg==)
4. [tamu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoOG68GQ87wK5h9z3ukZ-Ij0Rw4LxJ_WXGiYTgOKYzYtmRxDHvJAlz_VqVZ9sMHYRFGMQMKdswxMDbHzGo_5pIpm9AoTPOjHqDagxoQH3cj07o641oOPIeVJD-2J1hPXXc_gPMAg==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhCN0iL6uvZXOV23-j-cxXPq2PyOkCIadtcE1x3BsKDmXYmsmY_jxavR0Uun7PsxSN9oJAoCHjovZl_ZoS5hn81uc6azs8dUMP5kXUV7zTKtwuuktEqA==)
6. [units.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmmWjSk0Y6gogDTI2ETuUewfHpkCRFbA2zbRgn0dKFvpNJZpFDfl9iuQ-r8ecN7J4JNQyO86WTTLgG-AtGnUKvzbJZnHzTw1f3qbh5SyDJuPzvEPLsQ3tXOgbHwNlpcFZIerQDhCDq)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRr0eq2ozpHhG7A8_BXZO1L_AHjFv8XapoLpEHO4hE0X-xBdv8G5um1FJVGy5qfZvVno4A0u4ytCVvjPmf9uLgCGI3H09w2n9hGjWLSdSjl1Jxia7nVE5ADA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSQwz2AHJbkPof5qTc_a2ohCNMv_aD5jjmybmsgVlUoDI64EBZjNkwTV7uF-i_Gjg7zulBSmHhu3JfAo1EjwK6nwuJ_UpT2MhAKtiqd4k3CaE8N_iojw==)
9. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgzyoMZocEueRZgsNt6MhYenocuLtpPKrb_rdk8ObgHsl2kSBfJZr10ciKynWQN9rswrsyMyTR9rWvDuSbOZFty1YTTHY0cgyVKFiK_C1tLzTsqaRGn11nkFWo3cq7iF4hybqH48DnQjGDaO7DyGLKH6YpMZj-0TcdShKv-W5ytKoVYXHO8dJ0up1YdKR8ckWfkOs=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbarOdUc7EPmcOn9gGNToZf9lf14zkC5CkULcJMERhwsT-5oarcUR3mEn1wXHlN2kn6AqvNFKFTyCMKDPzmXxMCNRy846Z0l96X927F4x28kSmm-26vA==)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxLeAOSkE2Pk7Pq7Cm0EGw9R7irUC0A00wamNqdc91-baHq2JxLCYwtWYViMmZqw4rKtC7anKop-qkbvmxyoD9RghZa4Zycvhq29D03KI6BYqTHKYyBt3h4TKq4ulCfwXcYRDnBco_DM9UZQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCmLDvZNKKvskL1EOSwkFJVhHwHj3TerWhLAiBasutjA3fWvO_YiOZKUunFHgUawciJ6N2YP365SnFR1PGg_kgnTT0MkV7JwHoHJF0HR1IynsDl547Dw==)
13. [google.com.cu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkn9oIf_2XGmDGGo5idCZjdQ0waInfTxElpmwGjds8psjPHuhDHyGmS9d96aUX7XwijCKlYK9uIWKlOpQkGJqmgqriZTYzj43degGQfRva1l2AZ3cI_wEOClq5tQg4Gmhm6fRJOOhmSQQbJh_qAhd0GZLpKNM=)
14. [quantum-journal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnfhf9U3bLeQxn4POUhHkN3qWErFy9_vIyMJ5KHcHy9tu4-DotXjYSaZbfdAz2bXYNK9xm6z5nlsQVYAw4zLUjCLSahNSg4DQxH_LR76uPK27WlXAKk7U0C5QasXuQEFR_enXz6hfVgYGyQQ==)
15. [andreas-klingler.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHqU7z_tmZnoHPlR_uA9t-kidXIPzkKEvC1Rpjc5TQkT1qJaxQX1IBrwWBzXT_tWVUekqq2vt2dgULDdO8JtpvUcbxmyWkYHdYHQCYBGb6kTJZtz4usC-B-z6chR5rEL45NEE=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkOR2La2QRD-RzHZPuaFcZH93UnbGxALgXpBcMpIkqxCL72peGu0KSL_gZGbvNpVG3_5zlJ1ZHauRnjkGLbd7rbGmFoM2brgCASDe-I-OTx-g_hk2c1A==)
17. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVP8qi0iPQpkHmaAW1Yz276s5jivZFfDocQ3m_MTvh98OcR-c1TIxHKpP0e8FvLsnyz8m3FIDmAgEZWguRr44WU2p3pqjkjrl-3K_BgLl0-lML7UjwcxXHR7mA7gqmlFZehEYjWwwpkVNRJwVYD7kXtsrJ9M6CpjuYEiilvlqg4jRp0AyZ6PB0CiDZjc4=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXoLJ6Qa8P5thAzZ4082ihxS1G6KdvNSBNSeH57RZrWrR7NQjwrfQEs18u3zZjmCRCPzTMJxCwVOXeNn0vyxU5FLyCygpSSw6Qf4KkgS-pVcpMoUL_vw==)


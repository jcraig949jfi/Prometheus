# Prompt 09: DR-009 — Verify AA-021 AlphaTensor 4x4 over F_2 ONLY (not C); AlphaEvolve is the C result

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZ6cUFCYXJEVUY1ZWZfdU1QdUwyaUNREhZ6cUFCYXJEVUY1ZWZfdU1QdUwyaUNR
**Elapsed:** 727s

---

# Substrate Verification Report: Anti-Anchor AA-021 (AlphaTensor vs. AlphaEvolve Matrix Multiplication)

*   **Key Point 1:** The candidate anti-anchor AA-021 correctly identifies a critical coordinate distinction—AlphaTensor (October 2022) operates over the finite field $\mathbb{F}_2$ (yielding a rank-47 decomposition), whereas AlphaEvolve (May/June 2025) operates over $\mathbb{C}$ or fields of characteristic 0 (yielding a rank-48 decomposition). 
*   **Key Point 2:** AA-021 requires immediate refinement because it falls into an attribution gravity well. AlphaEvolve is *not* the first to achieve the $\mathbb{C}$ rank-48 result; primary literature confirms I. E. Kaporin discovered a rank-48 decomposition over $\mathbb{C}$ in November 2024, six months prior to AlphaEvolve's announcement.
*   **Key Point 3:** Literature surrounding this verification reveals a second, equally dangerous gravity well: the conflation of **commutative tensor rank** (Waksman 1970, rank 46) with **non-commutative tensor rank** (Strassen, AlphaTensor, Kaporin, AlphaEvolve). These are distinct mathematical invariants with different recursive scaling properties.

This substrate verification addresses a high-risk conflation in current literature regarding the bounds of fast matrix multiplication algorithms discovered via machine learning and numerical methods. Mainstream channels consistently merge field-of-definition constraints and mathematical invariants into a single, inaccurate narrative of "AI solving the 56-year-old matrix multiplication problem." This report processes the primary literature to generate clean substrate inputs, anti-anchor pins, and catalog edits, fully resisting the gravitational pull of AI-lab public relations and community misunderstandings.

## (a) PRIMARY SOURCE CONFIRMATION

The candidate anti-anchor asserts: *AlphaTensor 4x4 over F_2 ONLY (not C); AlphaEvolve is the C result.* 

Verification of this claim requires establishing exact coordinates (HARD-5 doctrine) across three axes: the system, the field of definition, and the non-commutative tensor rank of the $\langle 4, 4, 4 \rangle$ matrix multiplication tensor.

**1. AlphaTensor (PEER-REVIEWED, October 2022)**
The definitive primary source for AlphaTensor is Fawzi et al., "Discovering faster matrix multiplication algorithms with reinforcement learning," published in *Nature* 610, 47–53 on October 05, 2022 [cite: 1, 2]. 
*   **Result:** AlphaTensor discovered a decomposition of the $4 \times 4$ matrix multiplication tensor utilizing 47 scalar multiplications. 
*   **Constraint / Coordinate:** This result is explicitly restricted to the finite field $\mathbb{F}_2$ (or $\mathbb{Z}_2$). 
*   **Primary Source Quote:** "Particularly relevant is the case of $4 \times 4$ matrices in a finite field, where AlphaTensor’s algorithm improves on Strassen’s two-level algorithm for the first time, to our knowledge, since its discovery 50 years ago" [cite: 1]. 
*   **Verification:** The AA-021 claim that AlphaTensor's 4x4 rank-47 result is strictly over $\mathbb{F}_2$ and *not* over $\mathbb{C}$ is **UNCONDITIONAL and TRUE** [cite: 1, 3]. Over standard arithmetic (real/complex numbers), AlphaTensor did not improve the $4 \times 4$ case; it only found improvements for other dimensions, such as a rank-76 decomposition for $\langle 4, 5, 5 \rangle$ [cite: 3, 4].

**2. AlphaEvolve (ANNOUNCED-NOT-PUBLISHED, June 2025)**
The definitive primary source for AlphaEvolve is the preprint by Novikov et al., "AlphaEvolve: A coding agent for scientific and algorithmic discovery," arXiv:2506.13131, uploaded June 16, 2025 (with public announcements appearing in May 2025) [cite: 5].
*   **Result:** AlphaEvolve generated a search algorithm that discovered a decomposition of the $4 \times 4$ matrix multiplication tensor utilizing 48 scalar multiplications.
*   **Constraint / Coordinate:** This result operates over the complex numbers $\mathbb{C}$ (and generalizes to any field of characteristic 0) [cite: 5, 6].
*   **Primary Source Quote:** "Notably, AlphaEvolve developed a search algorithm that found a procedure to multiply two $4 \times 4$ complex-valued matrices using 48 scalar multiplications; offering the first improvement, after 56 years, over Strassen's algorithm in this setting" [cite: 5, 7].
*   **Verification:** The AA-021 claim that AlphaEvolve is the source of the $\mathbb{C}$ result is **TRUE**, but the AlphaEvolve paper's claim that it is the "first improvement, after 56 years" is **FALSE**, as demonstrated in Section (b).

## (b) FOLLOW-ON WORK (2024-2026)

A rigorous survey of the 24-month window (2024-2026) reveals critical superseding and parallel work that the AlphaEvolve framing ignores. A massive gravity well exists around the narrative that AlphaEvolve uniquely broke the 56-year Strassen barrier over $\mathbb{C}$. The substrate must reject this and anchor to the correct historical timeline.

**1. Kaporin's Prior Discovery (PEER-REVIEWED, November 2024)**
Six months before AlphaEvolve's announcement, I. E. Kaporin published "Finding Complex-Valued Solutions of Brent Equations Using Nonlinear Least Squares" in *Computational Mathematics and Mathematical Physics* 64(9):1881-1891, dated November 2024 [cite: 8].
*   **Result:** Using a specialized derivative-free nonlinear least squares solver, Kaporin numerically solved the Brent equations to find a rank-48 decomposition for the $4 \times 4$ matrix multiplication tensor over $\mathbb{C}$.
*   **Primary Source Quote:** "For the resulting fast matrix multiplication algorithms many known values of rank are reproduced and even improved. In particular, an algorithm for the multiplication of 4th order matrices in 48 bilinear multiplications is found" [cite: 9].
*   **Substrate Implication:** AlphaEvolve is an independent reinforcement learning / LLM-agent rediscovery of Kaporin's numerical optimization result. Any catalog entry asserting AlphaEvolve as the *sole* or *first* discoverer of the $\langle 4, 4, 4; 48 \rangle$ decomposition over $\mathbb{C}$ must be flagged and corrected.

**2. Arai & Ichikawa (ANNOUNCED-NOT-PUBLISHED, November 2025)**
In their preprint "Faster Algorithms for Structured Matrix Multiplication via Flip Graph Search" (November 13, 2025), Arai and Ichikawa acknowledge the dual discovery of the rank-48 scheme [cite: 2, 10].
*   **Quote:** "While we did not independently recover the rank-48 scheme for $\langle 4, 4, 4 \rangle_{gg}$ reported in recent work [cite: 11, 12, 13]..." where their citation [cite: 11] is Kaporin (2024) and [cite: 12, 13] are the AlphaEvolve papers/announcements [cite: 2, 8]. This follow-on work correctly attributes the result to both the human numerical approach and the agentic evolutionary approach.

**3. Dumas et al. / Sedoglavic (ANNOUNCED-NOT-PUBLISHED, March 2026)**
In March 2026, literature surfaced detailing a variant of the rank-48 algorithm optimized for numerical stability. "A more accurate rational non-commutative algorithm for multiplying 4x4 matrices using 48 multiplications" [cite: 14] refines the base discovery.
*   **Result:** The authors provide a variant of the $\langle 4, 4, 4; 48 \rangle$ algorithm over the rationals (any ring containing an inverse of 2) that reduces the error bound exponent from $\approx 2.577$ to $\approx 2.386$ [cite: 14].
*   **Quote:** "An algorithm to multiply two 4x4 complex-valued matrices requiring only 48 non-commutative multiplications was introduced in [cite: 15] using a pipeline of large language models... We present in this note a variant of the recent __4x4x4:48__ algorithm over the rationals... that is more numerically accurate w.r.t. max-norm in practice" [cite: 14].

**4. DeepEvolve (ANNOUNCED-NOT-PUBLISHED, October 2025)**
Liu et al. released "Scientific Algorithm Discovery by Augmenting AlphaEvolve with Deep Research" (arXiv:2510.06056) on October 7, 2025 [cite: 12]. This work cites AlphaEvolve's 4x4 matrix multiplication breakthrough but extends the methodology from pure algorithm evolution (which depends entirely on internal LLM knowledge and execution feedback) to "DeepEvolve," integrating external knowledge retrieval and cross-file code editing [cite: 12, 13]. This represents a methodological fork rather than a mathematical update to the tensor rank bounds.

## (c) FALSE-FORM RECURRENCE

The verification triggered a search for the false forms proliferating in the 2024-2026 corpus. The substrate requires anti-anchors exactly because these false forms carry high memetic momentum. We identify two distinct classes of false-form recurrence: The *Attribution Conflation* (media) and the *Coordinate Conflation* (technical communities).

**Class 1: Media Attribution Conflation (Ignoring Field of Definition and Prior Art)**
Mainstream press consistently reports the AlphaEvolve result by erasing both AlphaTensor's 2022 $\mathbb{F}_2$ result and Kaporin's 2024 $\mathbb{C}$ result.
*   *Instance 1:* A May 17, 2025 article in *Cantor's Paradise* states: "It found a way to multiply 4×4 complex-valued matrices using only 48 scalar multiplications, beating a record that had stood since 1969... After 56 years of human efforts to improve on Strassen’s algorithm, an AI system finally succeeded where generations of brilliant mathematicians could not" [cite: 11]. 
*   *Instance 2:* A June 3, 2025 *Sidecar* article states: "Google's AI just reduced matrix multiplication from 49 operations to... wait for it... 48! ... This tiny improvement eluded the best human mathematicians for 56 years. Since 1969, countless brilliant minds have tried and failed to crack this seemingly simple problem. Yet Google's AlphaEvolve just waltzed in and solved it!" [cite: 16].
*   *Analysis:* These recurrences validate the high-risk status of AA-021. The press collapses the coordinate of the underlying field. Strassen's 1969 algorithm (rank 7 for $2 \times 2$, yielding 49 for $4 \times 4$) works over *any* ring. AlphaTensor broke the 49-barrier in 2022, but *only* for $\mathbb{F}_2$ [cite: 1, 3]. Kaporin broke it for $\mathbb{C}$ in 2024 [cite: 8]. AlphaEvolve independently found it for $\mathbb{C}$ in 2025 [cite: 5].

**Class 2: Technical Coordinate Conflation (Commutative vs. Non-Commutative Tensor Rank)**
In response to the AlphaEvolve announcement, technical communities (Hacker News, MathOverflow, Reddit) generated a massive false-form recurrence by conflating *commutative* matrix multiplication with *non-commutative* matrix multiplication. 
*   *Instance 1 (MathOverflow / StackExchange, May 2025):* Users repeatedly cited Abraham Waksman's 1970 paper ("On Winograd's algorithm for inner products"), which achieved 46 multiplications for $4 \times 4$ matrices [cite: 17, 18]. "For commutative rings in which division by 2 is permitted, Waksman's algorithm from 1970 can do 4x4 matrix multiplication with 46 multiplications" [cite: 18].
*   *Instance 2 (Hacker News, May 2025):* "From the AlphaEvolve paper: 'For 56 years, designing an algorithm with fewer than 49 multiplications over any field with characteristic 0 was an open problem...' If you don't want to allow division by 2 then there is Winograd's algorithm from 1967 which works over any commutative ring and uses 48 multiplications for 4 x 4" [cite: 19].
*   *Instance 3 (Mathstodon, May 2025):* "Actually, Waksman's algorithm from 1970 allows multiplying two 4x4 matrices over any commutative ring allowing division by 2 using only 46 multiplications. Maybe DeepMind ought to invent an AI that searches the scientific literature for prior art..." [cite: 20].
*   *Analysis (HARD-5 Enforcement):* This is a severe coordinate collapse. Winograd (1968, 48 multiplications) and Waksman (1970, 46 multiplications) rely on commutativity: their algebraic identities require $x_1 y_2 = y_2 x_1$ [cite: 19, 20]. Therefore, these algorithms **cannot be applied recursively** to block matrices, because matrix blocks do not commute [cite: 15, 19]. To achieve asymptotic speedups $O(N^{\log_4(R)})$, the tensor decomposition must be strictly *non-commutative* (valid over non-commutative rings). Strassen (49), AlphaTensor (47), Kaporin (48), and AlphaEvolve (48) are all *non-commutative* tensor rank results [cite: 2, 14, 15]. The substrate must rigidly forbid collapsing `tensor_rank_commutative` and `tensor_rank_noncommutative`.

## (d) RECOMMENDATION

The anti-anchor candidate **AA-021** targets a valid and highly active gravity well but is currently insufficiently granular. Based on the primary source verification, I issue the following directives for substrate inputs.

**(i) Refinement of AA-021**
The stated true form of the anti-anchor must be updated. 
*   *Current Form:* Verify AA-021 AlphaTensor 4x4 over F_2 ONLY (not C); AlphaEvolve is the C result.
*   *Refined Form:* **AA-021-REF**: AlphaTensor (2022) achieved $4 \times 4$ non-commutative rank 47 strictly over $\mathbb{F}_2$. For $\mathbb{C}$ / characteristic 0, the rank 48 non-commutative decomposition was first published by Kaporin (November 2024) via numerical solvers, and subsequently independently discovered by the AlphaEvolve agent (May/June 2025). 
*   *Downstream Consumer:* AA-021 register edit; T#1 catalog cross-link update.

**(ii) New Companion Anti-Anchors and Sub-Anchors**
The verification surfaced a critical coordinate collapse in technical discourse that requires immediate primitive registration.
*   **New Primitive Registration (HARD-5 Compliance):** Register `tensor_rank_commutative` and `tensor_rank_noncommutative` as strictly orthogonal primitive fields in the `AlgorithmEvolutionaryLoop` and `MatrixMultiplicationCatalog`. 
*   **New Anti-Anchor (AA-022):** "Winograd (1968) rank-48 and Waksman (1970) rank-46 algorithms for $4 \times 4$ matrix multiplication are COMMUTATIVE rank bounds. They cannot be applied recursively for asymptotic complexity improvements. They do NOT invalidate the 56-year non-commutative bound of Strassen (rank 49) prior to Kaporin/AlphaEvolve."
*   *Downstream Consumer:* AA-022 register creation; AlgorithmEvolutionaryLoop Tier-G primitive field.

**(iii) Work-Queue Entries for the Verification Substrate**
To ensure complete closure on the mathematics of the $\mathbb{C}$ rank-48 result, the following entries should be added to the Promethean work queue:
1.  **WQ-MM-01 (Equivalence Verification):** Execute a tensor isomorphism check between Kaporin's 2024 numerical solution [cite: 8] and AlphaEvolve's 2025 generated code [cite: 5]. Determine if AlphaEvolve found a novel decomposition orbit or merely rediscovered the exact de Groote isotopy class found by Kaporin.
2.  **WQ-MM-02 (Error Bound Tracking):** Catalog the Dumas / Sedoglavic 2026 variant of the rank-48 algorithm [cite: 14] as the current preferred primitive for numerical implementation due to its optimized max-norm error bound exponent ($\log_4(\gamma_{\infty, 2}) \approx 2.386$).
3.  **WQ-MM-03 (Agentic Provenance Filter):** Apply a training-corpus filter to all LLM-ingested literature dated May–July 2025 that credits AlphaEvolve with "breaking the 56-year Strassen record." These texts must be tagged with `[CONTAINS_ATTRIBUTION_ERROR: IGNORES_KAPORIN_2024]` to prevent future agentic drift.

**Sources:**
1. [lesswrong.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQhep8BCF5n2S6p2eljzh9r1OYv0X92t4k2NEleemBWwq8T_MAP2ZXtPewZHxEjoyopOA12kr5kiKBs6jtbj2OpFtLq3JDmUlvRaR5hdKoBd4JDqnCJnI0zIeCZxmDWYJ4RNMH9Ak-L2YGsVbR4j-ntdSZI-ZVUxP0ve9UVICVrFYygATuZFX1PT_9cBMBmjkUWYPLzAiuiBOXtKdrvXhCUZbIXg==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWZt2AvxfvZNgr-C9dWZ62VPDc7rXEuBTfmkCshd7j1Mme0Cya1n3i4AHXmSPEw22J9jf7ONtelgCV-NQGhvR8MQsXhEWfX3CiLqpizsJjRiZO5J3K7vLOBUY3IMEiDGYSWk1UIW0fb_yV4BnhpUtpCyvEobxdgUwBaPU8RB3IO2-UQt81uIzjBasYhgTMCLpj3JiyJmJTSWwVu33doxJGY7LYpiz8HwoTOBhmBCakKsC1TIX2ZNekL9n19UzlqeIfL2Pz-OeNyjc_8rWgtD9Ul_HUO8P82WDwZCB1kgq8AfhnQg1dEmcdkchjUhq05-N8c4BUxrI4FB8ZcjlccGKHdecnhXMr8T9VZwBSziUCfw9Vn94QjPn8GiAUv-Of_rr7p1LpO9hmOeo=)
3. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsRYdmnFEBSlZM7OPMOj6i-aFntQsJMW3de-BCL953J_8pQUpvGfyi4CTMhNVyaJhQVdUL8wjiofJ2i5lN7AVHdIX0SmZzzpnIqQpmVz5c_tECccM9iDIK5XugXCjvKpIRdsM=)
4. [deeplearning.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtp07k7N9vSTY0l-RDGO6WuwEotMige-cTrLQL-elcXyZslvuX1iAKkAv9AltSDVnsGL7O5nzJyxAXYexAi88qWT8CeuaRa7vuFGMcvtsDc0HcJ_Zn5k-z0TA8I5N4LD5DQup8n1hMvCSkZ6nqFfqIr0G_kwkkig0NbLyZzf0RJ71XFMKf-Xg2YOC1BScQ5Jx7xgY=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHLXVPab1tMkGFuFDQal13a2_QRUheVwre7MQFcSH6_puJzboWxdu1Nw7FR6pPmv7pB36ZH55Wzwj1FQtm11kz39BKyRW2Q6pbetG3IsMjmleYk-KogA==)
6. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRkh0g2qZm_6yVCan6gJljSG5sQb0M4twojeWOicyw9vhMuPinaZg-ZNMd5JvrTVZ-2ZbUcP5rAXH1zVwRNLFybdT41wEUITxyXv5pgqoxPRBLkPXetq0dOP46Wuijqvv33IH3Gmax-aQzPHmJqk0DNDbWK--aoRX7iV71URUAUz1EKxZrgkMP9sYJrPkmvq6WllphIcMC_5-odUQ=)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhFLDuo4TtWND6X-l4h5Yug68MF5zOTE_CKi_jy1qfHgPmtAcj-yl9nCLhVGI_m0CBHhxoDD2m_Sjg9hPEYzjNtwf7Va2GJnBu3LB59mtytHU2eK8TIE325-0WM82iB0LSNZyicABwBWCISMf8m7Ij2fYvIsyfPGfHb9ZghoW4skjQCGP01Cc63oTlzH6gla6hxv8xr5RnFLjuG3N_j0aQzoKsfEnabjIw5nuF)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_MG-1qFn2KyumY8Owuw-Y5k8C7fKMgMUKGwVtUhYo2rlGwURncylYEn-v6RhKCYnI_ImYe4GOcp0xOsjqj03WIAyiHmlzAFQkUws7dr_H5WI6QAU_hYy53Fq9cwPobDZcgJBTnPkx0qBw5FfSoBXedIfF3OUNzCfLQYDe1kCRt19Br6PQ92mRKg_5xSr3z9GnUvfyPrysKY2ZQXaLlEJpt5MdANyhFQsFL8sXGYKqjIX0n3ftysk7y6Tz)
9. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOtSEqvVs-RLDu2BDxGNm9WR5i22ygaJH3z0jhqxGdA-llUmYq6QY8Otx6BY6UhqbM9fe6hRCFWrB83LiZ6kzOFAdSoM6uG_mFRnPcQVzlAW2RmEeH0q5yvsY69Kldql4nE5yHeFHuHTI=)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHMBewWJwm9YoK_DgvtsjHQ1tzLnXDLqmnOfZGl151_8CwJ35dqwSVqfFMQ-UN6id3xhjQdjw3N6fxs_05wP8Yaln-jdphKGEnjqDh2kDGPYRQR_VcDRa_ILQwD71VfCryad6XoL3WKR0ObtQB3ZPNLylci7FKmsNkagFT5xaNLUSj-JKj80fD_YeQU41MnjMeVjSCN6WLAcQj1ZRrP0qmf5LLn_bv0MeXb5W0_6YFSQKy6x8q)
11. [cantorsparadise.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjFCcA9Hm5lUmUOEQOboD5Ggq6Q2RLxRgtKHzipqVpVVanaHH4EuGxbpIYuRkP6p2_Vxoq2giTVtIUON_0ZjdNuYDiMI6vgY9q_aS1lvsikUsY0UuM2M9EsyyDgYeNEWhKGfJ3hKk2OwPVgw0t_faUrXk1bjUzFAQz8cLOzsWvw303qqpLDznsCOtr_1uybVPKHXuI4-I20zUx_PKOhp2xTkWq6H7O1wP90SLJrzJwV_VO4ZLHncQ_aJ-c7xPptq8=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOpt6vtTbDcZCaATgoPacq1Uwh3JK15q4QqDIq5y4vHjZ2urlUH23PO2hbfgTU1EPxpVPMtJZQ_ZRwXLkiMKDbMfoNCbjdGmvyZsO0_A5AggguZT_UpFSE-w==)
13. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7VdcUJ0GW_p87QfTFYDlKu3DlxYNKyBrzxMlsWu9XtICtxICcqlQJO-pBYTPJEs110dmWtmc7MSQWs7Y1tctIpUaDbhF7TTRsFjYHQ57fbggYRgE1bSik46s0kHGdcRNL99jH68t_A6urgHRtDKeSECHUGlUbYmX7S4MtQsQRKJEEuMPuIehkjoC02RZeLyEJJc5aOhLZUDeekm2jcYMTmcybC7MWyjo1dz_UbuSWPXWrljW6ol_ZXqcC3TbovLmwdYFcgZyE)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ8ilI8XWTWL67IY1Lvk9QAfxcDmRPTlSlD9xDZ49mFjl2-6R_kFS45a1NKabhz0puBLmWeyCxq1yPLERQ1ohzdlsJpxZfc8q9_7ZfnmRGnB7wHxPrIssq2VsDNfbJwmJq57JbxiSu7SZRILe81Ui8ybeE2KqfNlVhVyn9Zd8YMieljnnjIbMXPJ6E1HUOb7JWNekbAJd1ww5sCHtiWKRUmlwempjShUY8y2rvzJ9s_5awXtRKVyUxGKUPkAN8cCRUWjT76A0WodrbaoZpEvNwymk=)
15. [mapleprimes.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnrYcaBqjOtjmhlQuoop-h3dJnulyLFb_4hZciAYq66cWW0Y9reBUigSNVCh2LpzwFlyeG1mJ1egAf3YhEiTyKfH1HQzIBY51r-T9yI9Se_laMpUZEDezTrshcziuxWuDh4O0dwrPVhjczNOG9SoKTJijLEs6tlcdFSBFNYZHpyJhUScKdDaPl1RdCMqIfI6t0)
16. [sidecar.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrRkmt9aT2D3nEr5DYIetQwiNi24gHAMFq3XlWVO9uk5nnZ56QJOalIHuXGHVZZ4Bv6z8aLkVEO-090u31LdZvWxHyd-f0VHh2FLkWVD26XD5GAB6VBvvlty8lZI0q1I26gWKaoI6wZtsd94XXGGsY3LNDWMlmnp7Uf7nq7ezjmhShPHCo4W62Nngt871hK5Eb0IA6BALuySRT720hKBd8aGLN6rFiFKx0XH8=)
17. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_zmya7YYnWxYQcwSZuCyb0z35pgOVGVaK0XxiR6EE0TaTgtDrvNPZW9eZ4Kv5xMDSP7CRYYHSJqFPixzqcopbs87A04XfA6_-nrjzQXcLWDIV8Ee17EuNrn0-UcWEWNwFRbOEpjRpldSKcpYpnaAKvZf8qNxcbHqdlFRxW97W1Ge3aOv7CUp2R5cB)
18. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT3ajXr_CDVD9Dvxd4ZYbIohnhevLId6LX0wRAzhM2hXlZzvGFfZAakRYke5sCa7Zgref4O5fAE2V2QwZKsMbmGmycSkoMGz4Z6R82N0yE827P2muQjLuUAWOzma-dEFVQ3WmoSDg-ykQ2N15ate2UsvjYuT9zk775TjU5QeURmovgS00vFFRNYrjtX3MOqbZ8AN7nY5VFOi4LxKjQE9Nrf_1DkKVky1lIHza7)
19. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy2j4rCbWMV1aXsTBVFMweBMCLcAxvtKuUNCsMCw3ARt5a20Vh-E_Kyo02v1rxP0qxbt4-RSONbS9a3otguzMJhx7vj5nf_55HMsS8PQ-KYjP48TUnNQJwYsJg0AuOa5Jb1BQ=)
20. [mathstodon.xyz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdlFi_vjfCUwTeZmIFXNVDX6GIHlOS8TlSLQ-5P-dJOmhhl2citU9BrVg5qMl2zIsRfq2y9SwKUFQnrEssLAlEaAKRmGprJ8scEU6NXhIzurY2J1ozV_MPnRZy8DSnCOY-qwkNNoAJtqY=)


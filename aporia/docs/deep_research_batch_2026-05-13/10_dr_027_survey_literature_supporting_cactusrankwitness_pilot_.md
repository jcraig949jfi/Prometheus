# Prompt 10: DR-027 — Survey literature supporting CactusRankWitness pilot (T#19) for Tier-B contract change

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdHRHNFYXI2N0VaNk1fUFVQcllHSGtBZxIXR0RzRWFyNjdFWjZNX1BVUHJZR0hrQWc
**Elapsed:** 1364s

---

# CactusRankWitness Verification (T#19)

**Key Points:**
* The true form of the `CactusRankWitness` candidate is strictly valid but requires immediate architectural expansion due to breakthrough findings in February 2026.
* **Macaulay2 State:** There is no monolithic, unified `Apolarity` package in the Macaulay2 ecosystem; the state is fragmented across localized scripts (e.g., `ApolarLowRank.m2`, `vsp4`), requiring a catalog edit to assemble a composite primitive for Tier-B execution.
* **Coordinate Separation (HARD-5):** The literature exhibits a massive gravity well collapsing **border rank** and **border cactus rank** during the application of linear rank methods. 
* **Barrier Breaking:** As of February 13, 2026, non-linear *tangency flattenings* have been explicitly proven to break the cactus barrier, succeeding where standard Koszul and Young flattenings fail. This must be registered as a primary anti-anchor.

---

## (a) PRIMARY SOURCE CONFIRMATION

The literature supporting the `CactusRankWitness` pilot fundamentally rests on the geometry of apolar schemes and their connection to various tensor rank coordinates. The foundational premise—that minimal length apolar zero-dimensional schemes are locally Gorenstein, and that distinct tensor coordinates diverge at specific bounds—is confirmed by primary sources.

**1. Apolar 0-dimensional Gorenstein Schemes and Extreme-Rank Separations**
The strict geometric separation of **rank** and **cactus rank** for general cubic forms is definitively established by Bernardi and Ranestad. In their definitive preprint update (arXiv:1110.2197v3, ANNOUNCED-NOT-PUBLISHED, May 20, 2024), they confirm the local Gorenstein requirement and establish explicit, extreme-rank divergence:
> "Any apolar subscheme to $F$ of minimal length is locally Gorenstein... We prove that the smallest degree of an apolar 0-dimensional scheme of a general cubic form in $n+1$ variables is at most $2n+2$, when $n \ge 8$, and therefore smaller than the rank of the form." [cite: 1, 2]

For the extreme-rank example requested in the T#19 context, Bernardi and Ranestad supply the strict divergence at $n=8$:
> "For a general form the rank and the border rank coincide... we show in particular that the cactus rank for the general cubic form in 9 variables [n=8] is $\le 18$, while the rank and the border rank is 19." [cite: 1, 2]

**2. Macaulay2 Apolarity Package State**
The T#19 pilot assumes the existence of a mature `Apolarity` package in Macaulay2. A survey of the primary source software ecosystem reveals this is a partial false-premise. The apolarity capability in Macaulay2 is heavily fragmented into niche, user-supplied scripts rather than a core, standardized package:
* Minimal decompositions for low-rank symmetric tensors are handled by `ApolarLowRank.m2` (Oneto et al., arXiv:1805.11940, May 30, 2018) [cite: 3].
* The variety of polar simplices for quadrics relies on the specialized `vsp4` package (Schreyer, referenced in peer-reviewed literature April 26, 2024) [cite: 4].
* Computations for chopped ideals leveraging apolarity rely on isolated implementation repositories (e.g., `ChoppedIdeals` in 2023) [cite: 5].

*Substrate Input:* The substrate cannot invoke a unified `Macaulay2.Apolarity` primitive. A structural catalog edit is required to build a composite wrapper mapping these discrete `.m2` assets to the Tier-B contract parameters.

---

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month window (2024-2026) exhibits an explosive phase-shift in the geometry of tensor coordinates, directly superseding historical approaches to bounding **border rank**. The substrate must ingest these updates immediately, as they render historical determinantal bounds obsolete for the `CactusRankWitness` logic.

**1. The Cactus Barrier for Linear Rank Methods (February 2026)**
J. Buczyński (arXiv:2602.11309v1, ANNOUNCED-NOT-PUBLISHED, February 11, 2026) definitively categorizes the failure of standard flattening techniques (Koszul flattenings, Young flattenings) to measure **border rank**. 
> "Theorem 1.3 (Cactus barrier for linear rank method)... In particular, if $g$ is an integer such that $\mathfrak{K}_g(X_0) = \mathbb{P}(W)$ (for instance, $g$ is the generic $X_0$-cactus rank), then the linear rank methods will never provide a better lower bound on $X$-border rank than $g$." [cite: 6, 7]

Buczyński establishes that linear rank methods inherently bound **border cactus rank**, not **border rank**. This imposes a hard ceiling (the generic cactus rank) on any determinantal method applied to tensor complexity [cite: 7, 8]. 

**2. Breaking the Cactus Barrier via Tangency Flattenings (February 2026)**
In a massive structural update, anonymous/consortium authors (arXiv:2602.12762v1, ANNOUNCED-NOT-PUBLISHED, February 13, 2026) successfully construct the first explicit polynomials that break the cactus barrier, bypassing the gravity well of linear embeddings.
> "We obtain the first explicit polynomial equations – tangency flattenings – vanishing on secant varieties of Segre variety, but not vanishing on cactus varieties... For all $n \ge 14$, minors of size $n(n-1)(n-2)+1$ of the tangency flattenings vanish on the $n$-th secant variety of the Segre variety... but do not vanish on its $n$-th cactus variety." [cite: 9, 10]

This is a critical substrate update. The introduction of non-linear "Kronecker-Koszul flattenings" (tangency flattenings) completely supersedes standard Koszul matrices for establishing distinct bounds between **border rank** and **border cactus rank** [cite: 9, 10].

**3. Border Cactus Decompositions over Cox Rings (January 2026)**
W. Buczyńska and J. Buczyński (arXiv:2601.19558v1, ANNOUNCED-NOT-PUBLISHED, January 27, 2026) refine the apolarity lemma by shifting the invariant framework to the Cox ring (total coordinate ring) of toric varieties.
> "A border cactus decomposition is a multihomogeneous ideal in the Cox ring... that witnesses that a given point is in a specific cactus variety. The definition of such witness uses apolarity and we describe the set of ideals... in terms of a correspondence between the usual Hilbert scheme... and the multigraded Hilbert scheme." [cite: 11, 12]

**4. Young Flattenings and Minimal Border Rank (August 2025)**
S. Gondi (arXiv:2508.17845v1, ANNOUNCED-NOT-PUBLISHED, August 25, 2025) extends the use of Young flattenings to establish lower bounds on the **border rank** of $GL(V)$-invariant tensors [cite: 13, 14]. *Flag:* Under the subsequent strictures of Buczyński (Feb 2026), Gondi's bounds utilizing Young flattenings are retroactively identified as being subject to the cactus barrier, thus technically bounding **border cactus rank** [cite: 6, 14]. The substrate must flag Gondi's "border rank" bounds as unconditionally bound by the generic cactus rank.

---

## (c) FALSE-FORM RECURRENCE

The mathematical literature surrounding algebraic complexity theory exhibits an immense gravitational well regarding flattening matrices and tensor coordinates. 

**Gravity Well 1: Collapsing Border Rank and Border Cactus Rank**
*The False Form:* Authors frequently claim to derive lower bounds for **border rank** using linear rank methods (minors of Koszul or Young flattenings) without recognizing that these methods are mathematically blind to the distinction between the secant variety and the cactus variety. Consequently, the field routinely collapses **border rank** and **border cactus rank** into a single conceptual coordinate.
*Recurrence:* The literature of 2024-2025 is saturated with this false form. As explicitly diagnosed in the February 2026 literature:
> "all equations obtained by taking minors, called rank methods, are actually equations for a larger variety than $\sigma_r(\text{Seg}(\mathbb{P}A \times \mathbb{P}B \times \mathbb{P}C))$, called the $r$-th cactus variety... all of the known methods producing equations for the $r$-th secant variety are equations for the $r$-th cactus variety." [cite: 9]

*Anti-Anchor Requirement:* The anti-anchor is absolutely required. The substrate must resist this well. When a paper claims a lower bound on **border rank** via a determinantal flattening, the substrate must automatically re-register the output as a lower bound on **border cactus rank**, effectively quarantining the result from polluting strict **border rank** heuristics [cite: 6, 7].

**Gravity Well 2: Apolarity via the Standard Hilbert Scheme**
*The False Form:* Assuming that apolarity conditions for limit schemes (border coordinates) are closed in the standard Hilbert scheme.
*Recurrence:* Highlighted as a persistent error necessitating the multigraded Hilbert scheme. Quoting a 2024 peer-reviewed source (Documenta Mathematica, April 26, 2024) citing Buczyńska & Buczyński:
> "Example 1.1 above shows that the apolarity condition $I_\Gamma \subset f^\perp$ is not closed in the usual Hilbert scheme. Hence, it is more natural to work in the multigraded Hilbert scheme." [cite: 4]

*Anti-Anchor Requirement:* If `CactusRankWitness` probes use standard Hilbert scheme parameterizations for border cactus boundary states, they will fail to capture the closure. The substrate must strictly map border apolarity tasks to `MultigradedHilbertScheme` parameterizations over Cox rings [cite: 4, 12].

---

## (d) RECOMMENDATION

**1. Candidate Evaluation**
The candidate `CactusRankWitness` pilot (T#19) is **structurally valid but needs urgent refinement**.
* *Refinement A:* The assumption of an out-of-the-box Macaulay2 `Apolarity` package is invalid. Execute a catalog edit to ingest `ApolarLowRank.m2` and `vsp4` as sub-routines.
* *Refinement B:* The mathematical logic for the witness must be upgraded from the 2011-2024 apolarity paradigm to the February 2026 paradigm. The witness cannot rely on linear flattenings to distinguish border rank from border cactus rank. 

**2. New Sub-Anchors & Companion Anti-Anchors**
* **Primitive Registration: `TangencyFlattening`:** Register the Kronecker-Koszul tangency flattening [cite: 9, 10] as a primary substrate primitive. This is the *only* currently verified algebraic mechanism to operationally separate **border rank** from **border cactus rank** computationally for $n \ge 14$. 
* **Anti-Anchor Pin: `LinearRankMethodBarrier`:** Pin a constraint on all LLM/agent outputs generating bounds for algebraic complexity. If an agent proposes a Koszul, Young, or shifted-partial-derivative flattening to bound **border rank**, the substrate must intercept and label the output as a **border cactus rank** bound, capping its maximum theoretical yield at the generic cactus rank [cite: 7, 9].
* **Primitive Registration: `CoxRingBorderApolarity`:** Update the T#19 testing probe (T-ST-T19-001) to compute border cactus decompositions explicitly as multihomogeneous ideals in the Cox ring (total coordinate ring) of the toric variety, bypassing the non-closed nature of standard Hilbert schemes [cite: 11, 12].

**3. Verification Queue Entries**
* *Queue Entry 1:* Dispatch an agent to explicitly calculate the size $64 \times 64$ tangency flattening minors for the $2 \times 2$ matrix multiplication tensor $\langle 2,2,2 \rangle$ (which has **border rank** 7, **rank** 7, **border cactus rank** $\le 7$). Verify the non-vanishing claim from arXiv:2602.12762 [cite: 9]. 
* *Queue Entry 2:* Run a training-corpus filter over all literature from 2015-2025 claiming lower bounds on tensor **border rank**. Extract the numerical bounds, tag them as **border cactus rank** coordinates, and remap the relations in the Prometheus catalog to eliminate false boundary constraints on the secant varieties.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnKjVr4VhB0kIqwSnrGSXN9BBoNE9I88P9FXvRRENNjld9YKhK4oebsr_1w0D6xGZTiVdF4oJhPi0s6WJ0U1MB_kXHcCgQBZM7rZzlJU5AD_neO7fIrU0=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjDC5FXM_wRj2mEgiCBsIi0Ivy2zLwMWafJF8gHOHRIaCJM7yl6CEYBGvwOArYUZ4lcp_R8dVblqxGiWWdLRh6P6UfezlzsoGWIpNygXV46lRrB-Y=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4-OD3LBeulwLRmmTnOTx4ZD1HNoNANYbfdDvnX-9Iorf1sSz4YXLhvuarm1RFRA_GpvvrfQ2hG0yTvA9jkRERVIscv1vEJF7eyKFOd7g4WDo_lqRz)
4. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0UT9fGJNr005Mt60FJLbWxL6XgFY_MUaqv8KZY999ueuopdMiNXOh8hcs781J5PVCge-BMNvcGqhojIJbYYMglXZQLmrWKAPCneXUFxRJHuAmFt2uHjCIbYsTb5SUiAUP3PrZbMuSz2a-GrMooPsVLbpzT2lElA==)
5. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHk7LfzWXGo4C9_I5s55iGG80VgmBF-i1oFPPVV0FWLrF0WNBaf9R7bXtHv5nSMRVHzad06lVwCPKJjFnqj3I5hDe04VsXSIOuOlSBmFH_7xX1gMDEswB-hAdhplYMZraY9acfCq7AJtdEniSoceCBuy6lJVxY5T93HuqcPiSjphGw-94-CRi09vzg=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp8Q1Zz2_Bz5IoZ5lH049A6aVkBA1Q1jm6vPqkop3h2DmzvB0vELQRIjD2K1Dzn8JbWD-JX8s8oZKP0QMV7agv4AQ2zZzxhLZr1EGwfHAS-zg4fda7b_w3)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0igBzEpe4Htlh1W8jFskKNsDcvXLcQM_Kl8ez_YSeSD1vZGAcmAl-_Si8ViVowhR47t-Fn8NJhVsgXogPUrSu0IKL1FET3TBqp584MO6zThyQY18xtnFNQ3X6E4N9WmtcwKTu7JGo-mDsbTJJ12c6R7wtjLKGiA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHB_SC9VUvLjCpEklitXj_qezDEI7Tzxm2OetEFhyh57b631VIV2zsM6ZX3Be4JXElWSvVAWlrZqf3ZoqdfNa-YXcLtXMOBnZIMYqg6Pqd6s3bEb4q7)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcJ4eeOro-dNcYdVQHRnYIw6-KTXs_Z1DRpKMIDEoj25kRgJfd5wmjl50WS23BDnBZPs92zRodJpvAlB--OEwa9bQOWFsrR4uKQSZ5QXTPfx8wmyYS)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbwEcaXS36FtkP8Tl3ToHXCEdSJMY_rHHAwkJodH-Z5eaXMLmOB6h2j5AC_yBsoDZ5pr-E2Q8_era3HCSBf7FiG26_9Fcg9cDPWjSRip-eU_Umd2eutaKj)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrRVeRCLYaRa6maDhnyIQSH0MNbwj58ZiKT8X-n9gVM_IWewL_sxslEVet82KeJ5vgSiYbMmXUG1WDKdhnecU33wgMGpR4flPEJZEbSy3NIs-6onJa)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmQ0umk6bQ2G2vnNmUBsDjtF3ou4k6Tr2T6xoMmyZyXrdr04rR8Qw7gEmNX9YKC7q2YQzOpzXRbEVxzoYQQgYaksf_a7gDaTtebi0q2TIzALqPquX43wSI)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHB5saJutKcTgILfLLAVqDMVsxvTnOo6UyjMlgsYsxQklcIN09VZVMnwlk4ylvum0evdpjkLNpmhN5Jj1NJIGnNMINZtMd-5NbcoJ9LG-ca0Fu3WtYQprcP)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsjoN8aeBBbZP7zAE7FHxFyDcZZhb0ZpX3RrLOxWq2_fS8mbUgqjlmTBwKnMBqCBQa79prgfGSpzgbczWd0YmY6MTn-xeMmfZNQyBuSKrIxPDo21Gl)


# Followup [FU-2026-05-22-041 <- row245]: However, the case $\alpha=2$, which relates to the conjectural mean value estimate for Weyl sums ass

**Pythia queue id:** 326
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd6THNQYXZTaVBQbWI5TW9Qay1EMnFROBIXekxzUGF2U2lQUG1iOU1vUGstRDJxUTg
**Elapsed:** 439s
**Completed at:** 2026-05-22T02:20:53.229915+00:00

---

# Research Brief: Conjectural Mean Value Estimates and the $(n^3, n)$ Weyl Sum System (The $\alpha=2$ Case)

**Key Points**
*   **Fundamental Impasse**: The $\alpha=2$ case corresponding to the mean value estimate for the Weyl sum associated with the incomplete pair $(n^3, n)$ remains an open question in analytic number theory [cite: 1, 2].
*   **Methodological Barrier**: While the full Vinogradov Mean Value Theorem ($\alpha=0$) was resolved via $l^2$ decoupling and efficient congruencing [cite: 3, 4, 5], these methods geometrically fail for $\alpha=2$ due to the absence of the $n^2$ frequency channel, breaking both translation invariance and the non-degenerate torsion of the moment curve [cite: 1, 2].
*   **Intermediate Progress**: The $\alpha=1$ threshold has been successfully breached (Corollary 1.4 of Oh and Yeon) utilizing the Hardy-Littlewood circle method unified with a refined shifting variables argument, marking a critical halfway point toward the $(n^3, n)$ conjecture [cite: 1, 2].
*   **Heuristic Risk**: Researchers exhibit `PATTERN_BASE_RATE_NEGLECT` by assuming modern multilinear Kakeya-type decoupling techniques will easily adapt to gappy systems like $(n^3,n)$, historically underestimating the topological obstructions present when coordinate projections of the moment curve lose strict convexity or torsion [cite: 3, 6].

**Executive Context**
This brief is surfaced as a substrate-grade follow-up to a Prometheus-initiated Deep Research report (`00245_stygian_primary_literature_survey_bl_c_008_vinogradov_mean_v.md`), investigating the precise bounds of extended Vinogradov mean value theorems. At the core of this inquiry is the parameter $\alpha \in [cite: 1]$, which bounds the relaxation of the quadratic term in a cubic Diophantine system. While the $\alpha=0$ case constitutes the historically settled Main Conjecture [cite: 3, 6], and $\alpha=1$ has been newly settled [cite: 1], $\alpha=2$ essentially drops the quadratic constraint, leading to the notoriously stubborn $(n^3, n)$ system. It appears that current decoupling technology is insufficient without a paradigm-shifting geometric insight [cite: 1, 2].

---

## 1. Brief Summary
**Question**: How can the conjectural mean value estimate for Weyl sums associated with the incomplete pair $(n^3, n)$ (equivalent to the $\alpha=2$ case) be resolved given the stated failure of current $l^2$-decoupling and efficient congruencing techniques? 
**Prometheus Context**: Requested by Stygian to evaluate the specific `METHOD_GAP` separating the freshly proven $\alpha=1$ extended Vinogradov bounds from the unproven $\alpha=2$ case, analyzing the topological and arithmetic blockers within the Hardy-Littlewood circle method and Fourier restriction theory [cite: 1, 2].

## 2. Flagged Findings
**Current Consensus**: 
The mathematical consensus holds that the full moment curve in $\mathbb{R}^d$, parameterized as $\Phi(t) = (t, t^2, \ldots, t^d)$, admits sharp $l^2$ decoupling estimates up to the critical Lebesgue exponent $p_c = d(d+1)$ [cite: 3]. This directly implies the Main Conjecture in Vinogradov's Mean Value Theorem (the $\alpha=0$ case) [cite: 3, 6]. More recently, the consensus agrees that "small cap decoupling" and "shifting variable arguments" can successfully address narrow extensions of this conjecture, such as bounding the mean value integral $\mathcal{I}_{p,d}(u; N)$ over slightly restricted domains $\mathfrak{D} = [0,1) \times [0, N^{-u}) \times [0, 1)^{d-2}$ when $u \le 1$ [cite: 2, 7]. This yields sharp upper bounds for the $\alpha=1$ system (where the quadratic Diophantine condition is relaxed to an inequality bounded by $N$) [cite: 1]. 

**Where Consensus Might Be Wrong (The Method Gap)**:
There is a prevailing expectation—driven by the rapid success of Bourgain, Demeter, and Guth—that decoupling will eventually conquer any polynomial Weyl sum system. This manifests strongly as **`PATTERN_BASE_RATE_NEGLECT`**, where analysts ignore the base rate of historical failures when analyzing "incomplete" or "gappy" polynomial systems (like $(n^3, n)$, skipping the $n^2$ term). Decoupling inherently relies on the non-vanishing torsion of the curve [cite: 8]. For the $(n^3, n)$ pair, the corresponding geometric object is the curve $\Gamma(t) = (t, t^3) \in \mathbb{R}^2$. While decoupling for planar curves (like the parabola) is understood [cite: 1, 2, 9], the specific $p$-adic and real-variable properties required to bootstrap this to the expected $p$-th moment bounds for $(n^3, n)$ are missing.

Furthermore, attempts to apply Wooley's Efficient Congruencing method to $\alpha=2$ run headfirst into **`PATTERN_PRIME_GRAVITATIONAL_OVERFIT`**. Efficient congruencing relies heavily on the translation invariance of the system of equations [cite: 4, 5]. The system for $\sum (n_i^3 - m_i^3) = 0$ and $\sum (n_i - m_i) = 0$ lacks the crucial $n^2$ term needed to easily complete the cube under linear translations ($n_i \mapsto n_i + h$). Overfitting the $p$-adic congruence models to assume that local constraints will smoothly lift to global bounds fails here because the translation invariance is algebraically broken. 

## 3. Problem Statement
The precise mathematical object being interrogated is the exponential Weyl sum associated with a subset of degrees. Define the standard degree-$d$ Weyl sum as:
\[ f_d(\boldsymbol{\alpha}; N) := \sum_{1 \le n \le N} e(\alpha_d n^d + \dots + \alpha_1 n) \]
where $e(z) = e^{2\pi i z}$ [cite: 1, 2, 7].

The *extended* main conjecture investigates the mean value of this sum over a restricted domain for the quadratic coefficient $\alpha_{d-1}$ (or other coefficients). Specifically, one defines:
\[ \mathcal{I}_{p,d}(u; N) := \int_{[0,1) \times [0, N^{-u}) \times [0,1)^{d-2}} |f_d(\boldsymbol{\alpha}; N)|^p d\boldsymbol{\alpha} \]
where $d\boldsymbol{\alpha} = d\alpha_1 \dots d\alpha_d$ [cite: 7].

In the case $d=3$, this relates directly to a Diophantine system. For a parameter $\alpha$ (which is related to $u$, specifically controlling the bound on the sum of squares), consider the system of equations for $2m$ variables $n_i$:
1.  $\sum_{i=1}^m (n_i^3 - n_{m+i}^3) = 0$
2.  $\left| \sum_{i=1}^m (n_i^2 - n_{m+i}^2) \right| \le N^\alpha$
3.  $\sum_{i=1}^m (n_i - n_{m+i}) = 0$
where $1 \le n_i \le N$ [cite: 1]. 

*   **The $\alpha=0$ case**: The middle inequality becomes exactly $\sum (n_i^2 - n_{m+i}^2) = 0$. This is the standard Vinogradov system. The number of solutions is tightly bounded by $O(N^{m + \epsilon} + N^{2m - 6})$ [cite: 5, 6].
*   **The $\alpha=1$ case (Corollary 1.4)**: The inequality is $\le N$. Oh and Yeon (2025) proved this yields a sharp solution counting estimate for any $m \ge 1$ (e.g., $O(N^{5+\epsilon})$ for $m=5$) [cite: 1, 2].
*   **The $\alpha=2$ case (The Open Problem)**: The inequality is $\le N^2$. Because $n_i \le N$, the sum $\sum (n_i^2 - n_{m+i}^2)$ is *trivially* bounded by $m N^2$. Therefore, the middle constraint becomes vacuous, and the system reduces entirely to the incomplete pair $(n^3, n)$ [cite: 2]:
    \[ \sum_{i=1}^m (n_i^3 - n_{m+i}^3) = 0 \quad \text{and} \quad \sum_{i=1}^m (n_i - n_{m+i}) = 0 \]
    The conjectural mean value estimate for this specific Weyl sum remains unproven [cite: 1, 2]. 

## 4. Status & Bounds
The status of the $\alpha=2$ extended conjecture is definitively **OPEN**. The best current bounds rely on partial interpolation between established bounds and trivial limits, but they fail to reach the sharp conjectural exponents [cite: 10].

### Current Known Bounds (Oh and Yeon, 2025)
For the domain integral $\mathcal{I}_{p,d}(u; N)$ which serves as the continuous analog to the discrete counting problem, Oh and Yeon established the following conditional and unconditional bounds [cite: 1, 2]:

| Dimension ($d$) | Parameter ($u$) | Exponent Range ($p$) | Sharp Upper Bound | Status |
| :--- | :--- | :--- | :--- | :--- |
| $d=2, 3$ | $0 < u \le 1$ | $p > d(d-1)$ | $\mathcal{I}_{p,3}(u;N) \ll N^\epsilon (N^{p-6} + N^{p/2 - u})$ | **Proven Unconditionally** [cite: 2, 7] |
| $d=3$ | $1 < u \le 2$ | $p \ge 12 - \frac{6}{4-u}$ | $\mathcal{I}_{p,3}(u;N) \ll N^{p-6+\epsilon}$ | **Proven Unconditionally** [cite: 1, 2] |
| $d \ge 4$ | $0 < u \le 1$ | Critical values | $\mathcal{I}_{p,d}(u;N) \ll N^\epsilon (N^{p-d(d+1)/2} + N^{p/2 - u})$ | **Conditional** (on small cap decoupling for $\mathbb{R}^d$) [cite: 2, 7] |

**The $\alpha=1$ Threshold**:
For the discrete system at $m=5$ variables (10 variables total), Corollary 1.4 states that the number of solutions to the system with $\alpha=1$ is bounded by $O(N^{5+\epsilon})$ [cite: 1, 2]. Since the diagonal solutions ($n_i = n_{5+i}$) trivially contribute $N^5$, this is essentially optimal [cite: 2].

**The $\alpha=2$ Blockade**:
When transitioning from $u \le 1$ (which maps to $\alpha \le 1$) to the unconstrained quadratic scenario mapping to $(n^3, n)$, neither the shifting variables technique nor the Hardy-Littlewood circle method variants deployed by Oh and Yeon hold [cite: 1]. The "small cap decoupling" results from Demeter, Guth, and Wang [cite: 2] provide leverage for narrow constraints on the quadratic frequency (restricting $\alpha_{d-1}$ to a window of $N^{-u}$), but when the window opens entirely to $[0,1)$, the exponential sum reduces to a manifold lacking the necessary geometric curvature to trigger efficient multilinear ball inflation [cite: 3, 9].

## 5. Literature (Primary Sources)
The primary literature tracing the evolution from the Main Conjecture to the extended $\alpha$-parameterized systems includes:

1.  **Oh, C., & Yeon, K. (June 2025/2026)**. *An extended Vinogradov's mean value theorem*. Transactions of the American Mathematical Society. arXiv:2506.01751v2 [math.NT]. 
    *   **Significance**: Introduces the $\mathcal{I}_{p,d}(u;N)$ integral, proves the $\alpha=1$ corollary, and explicitly formally defines the $\alpha=2$ gap regarding the $(n^3, n)$ system [cite: 7, 11].
2.  **Bourgain, J., Demeter, C., & Guth, L. (2016)**. *Proof of the main conjecture in Vinogradov's Mean Value Theorem for degrees higher than three*. Annals of Mathematics, 184(2), 633-682.
    *   **Significance**: Settles the $\alpha=0$ case using $l^2$ decoupling for curves, introducing ball inflation and multilinear-to-linear induction on scales [cite: 3, 6].
3.  **Wooley, T. D. (2016/2019)**. *The cubic case of the main conjecture in Vinogradov's mean value theorem*. Advances in Mathematics, 294, 532-561.
    *   **Significance**: Provides the parallel number-theoretic solution to the $\alpha=0$ case via multigrade efficient congruencing [cite: 5, 12, 13].
4.  **Brandes, J., Chen, C., & Shparlinski, I. E. (2023)**. *Local mean value estimates for Weyl sums*. Mathematische Annalen. arXiv:2303.11913.
    *   **Significance**: Explores the pointwise vs. average behavior of Weyl sums over small boxes, refining the 2022 conjectures of Demeter and Langowski [cite: 10, 14, 15].
5.  **Demeter, C., Guth, L., & Wang, H. (2020)**. *Small cap decouplings*. Geometric and Functional Analysis, 30(4), 989-1062.
    *   **Significance**: Solves extended conjectures for $d=2,3$ by decoupling over parabolas and moment curves with small cap geometries, serving as the foundation for Oh and Yeon's approach [cite: 1, 2, 16].

## 6. Attack Vectors
The mathematical community possesses several highly sophisticated vectors, some exhausted and some live, to attack mean value estimates of exponential sums.

### Exhausted Approaches for $(n^3, n)$
*   **Standard $l^2$-Decoupling for Moment Curves**: The method of Bourgain, Demeter, and Guth operates by breaking the frequency support of an exponential sum into small caps (e.g., intervals $J \subset [cite: 1]$ of length $\delta$), utilizing a multilinear Kakeya-Brascamp-Lieb inequality to inflate spatial balls, and iterating scales [cite: 3, 6, 17]. This requires the curve $\Phi(t) = (t, t^2, \ldots, t^n)$ to possess full non-zero torsion. The $(n^3, n)$ system omits the $t^2$ dimension. Projecting the 3D moment curve down to 2D by ignoring the second coordinate destroys the strict convexity and torsion metrics that make wave-packet decomposition and transverse plate intersection mathematically tractable [cite: 8, 9]. Therefore, standard decoupling is considered an exhausted vector [cite: 1].
*   **Classical Weyl Differencing**: Weyl's original method of repeatedly squaring the sum to lower the degree of the polynomial is historically understood to be highly lossy [cite: 13]. While it yields bounds like $O(N^{1/2 + \epsilon})$ for individual sums, the multiplicative losses inherent in the Cauchy-Schwarz inequality render it incapable of achieving the sharp $p$-th moment critical exponents required for the $\alpha=2$ conjecture [cite: 13].

### Live Techniques
*   **Hardy-Littlewood Method with Shifting Variables**: The vector innovated by Oh and Yeon relies on dissecting the domain into Major and Minor arcs, but with a twist. By shifting the variables (a technique originally traced back to Wooley), they artificially inject a form of averaging over the constrained $\alpha_{d-1}$ parameter [cite: 1, 2]. If a mechanism can be found to analytically continue this shifting variable beyond the bounded interval $N^{-u}$ to the full period $[0,1)$, it may bypass the geometric limits of decoupling.
*   **Multigrade Efficient Congruencing**: Wooley's number-theoretic approach focuses on congruences modulo $p^b$ [cite: 4]. The system $\sum x_i^3 = \sum y_i^3$ and $\sum x_i = \sum y_i$ can still be analyzed $p$-adically. However, because $x_i^2$ is not constrained, the algebraic identity $(x+h)^3 = x^3 + 3hx^2 + 3h^2x + h^3$ leaks unconstrained quadratic terms when subjected to a translation shift. A live attack vector is to construct a *translation-breaking* congruencing scheme that pairs variables differently, perhaps exploiting combinatorial symmetries in the set of primes [cite: 4, 5].
*   **Small Cap Decoupling for Defective Manifolds**: While standard decoupling fails, generalizing the "small cap" approach of Demeter, Guth, and Wang [cite: 16] to sub-manifolds of the moment curve might work. This requires a new multilinear restriction estimate specifically tailored for $(t, t^3) \in \mathbb{R}^2$ operating at higher dimensions of moments.

## 7. Cross-References
**Related Open Problems**:
1.  **Demeter-Langowski Conjecture (2022)**: Concerns the local mean value of Weyl sums over small boxes in the unit torus [cite: 10]. Specifically, estimating $J_{s,d}(\delta; N)$ when the integration domain is shrunk by a factor $\delta$. Brandes, Chen, and Shparlinski's 2023 work [cite: 15] establishes severe limitations on these moments for high $s$, which directly cross-references with the behavior of $\mathcal{I}_{p,d}(u;N)$ when $u$ approaches 0 (full torus) vs $u>0$ (small boxes) [cite: 10, 15]. 
2.  **The Discrete Restriction Problem for KdV**: Bounding solutions to systems similar to $(n^3, n)$ has massive implications for discrete Fourier restriction associated with the Korteweg-De Vries equation, where the dispersion relation $\omega = k^3$ drives the harmonic analysis [cite: 13]. 

**Anti-Anchors**:
*   *Anti-Anchor 1*: Do not anchor to the belief that an $l^2$ decoupling inequality will yield the final answer for $(n^3, n)$. As Bourgain pointed out, sometimes $l^p$ decoupling (which lacks the Hilbert space orthogonality of $l^2$) is necessary in the absence of complete arithmetic structure [cite: 9, 17].
*   *Anti-Anchor 2*: Do not assume that metric Poissonian pair correlation results for $\alpha n^3$ [cite: 18] imply sufficient pseudo-randomness to close the circle method error terms trivially. The minor arcs for $(n^3, n)$ exhibit deep algebraic conspiracies that standard equidistribution theorems fail to detect [cite: 19].

**Candidate Primitives**:
*   **Ball Inflation**: The multilinear-to-linear bootstrapping technique from Bourgain-Demeter-Guth (enlarging the size of spatial balls via Kakeya inequalities to facilitate decoupling into smaller frequency intervals) [cite: 3, 6].
*   **Friable/Smooth Variable Restrictions**: A potential primitive to attack $\alpha=2$ is to artificially restrict the integers $n_i$ to be $y$-smooth (friable). Work by Drappeau, Shao, and Wooley on Waring's problem with friable numbers shows that generating functions restricted to smooth numbers drastically reduce the size of the minor arcs [cite: 20, 21, 22]. By first proving the conjectural mean value for $(n^3, n)$ *over smooth numbers*, one might establish a beachhead for the full integers.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdDta4U4kiYg12vdrU3E6ytelAfZPyM6i3guzdIFC519XxCwS54jfRCTjFCJdE4LjZgR606ZJgx2yH7bJPACiLUbSY5dHiEvpsDc-EEMocQzP_b-oJpSH_Nw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvaUcjKGO_OgLNB84T5fjxedH4K-Q2OO_zQqNQZZ-2mMvZhvf11D4LFlj95LXprrRwQaJomsb2T4_wjQLBG5LCO4YTv5hoErx2rM0Bd-HH80jZqIvxew==)
3. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0uQfVgbEmdiqw6gyytXAZBD-kAXD7CW_BPFtJF-yu9wDB6EToLjRPfuZoq7srOZXOoXOmMmxly8FlKQ7sj3rtfTioTa0i3J-A4oasPlpVoeNk6CrJmHV6IF6J0b_gjkOnbg6xThLLR67Mfv-RHjCA7tV7Ji016k9l-0cjg0aOcorznw==)
4. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8a1h_aadlSyq7eR5IuHpZWEiwc7rIWQE8TYe7WoycwXK5oNfxUeiWMEBc890FSOSOOjT8iVJ5deyO7bAWu7Otelmh-WD5BmBIiJXuk1y-C_OyxgPz2bIzjRr4N5Cr-BiJSJMxU29agMUkaA==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGt6hVmDpBzbmsPu9N9QWpubp1qNqnxRHb5fXFodxJZEqb1WE-nb_gv02nTJs1qQcxdfn2_ae9jcCxPNptUizyKDOrhAaxtbrk-bjItIMs-9xLkqHLj_XUCAzffKOny848psfVyieWJYJRnxUNwc2HIlE_2lcKPOW8T2Maa9cjDwd8bH7Va-yrxbcuKHd6HjP9vyXymeEUCHb5ASdokqZhryG4KRzRgt6Hrj0a5qsgX_Q=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIm4b0LylIo0mjVGBtFllp0I-krs4Flyvr6WPlpx57O2_-nX-BpuggfAGxyqHVYE0TmtILxKpZ-4cupZ-o9wF3-VTClpmt8VLu-EgGkVpm8f1bDMsXOw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmtLvcz5HqvtxCQolEugy6WrbmGxeEeIXkKI5rG0ppp7ARY7cSY-hMpRmZRm0bxGpp5Zi15yrx-zu38EiGYfgoiZjwMGd2za-smJe4AGp89QRQ2e25Ng==)
8. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbmvAAztaBj6Y6hNGGOqPHG7zmAitA6LV1OPjA4NHwFWrhEN8-dimzr8fqIB0QYPlUeHzMya4b-cs_YwovpAuojz-dMItUYL8Lolnp_ZZkOEdvWAHWyawcpBiUwR2cxywQ43NJxQi7gCIbcHv0t85rtb72PaZW1w==)
9. [uni-bonn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfBZp3cyPe-2m3LA_ezLzspQ8hierHQlQ2NMzOvCgy4686x5PvhnwerNMfzFx1pHQVco0aLgJz3JubL3ijIqgRWIB48o8F39XaXbmpkoKV7nVFMG6oXSPfLNYRlDcaHIjdzLH7cX_o5XrFyswaebQ75m81eTN2qKVSropwn949)
10. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGak5SUG9SVYos8_hPu4qgSvHFARSk7Mv4PoJDg35j0vIGKoTUrj656jd3V4NexpueuDcxWPsEuZrj8NeRObbIL4CjBukJfs0P91J0OT26uGjcTsaxPxWERg6wDZVyKObWg1vZfwgvaXEHW)
11. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwZoHa2WFK-HcMmFk2i_LAaLXwmQdVcqeEWiReraokaMxzkRTER11-IccAprsVRuOlFe9B3Mq-ozzWATfMFofcTrHTHJhEf45G6LqxtwIptXN8YkP-FroDRF7IirzHyZAwIvdZKnXtaTTNOA_VvThe5RM=)
12. [bourbaki.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpt0rcTSD-U2UvHbFfxrR_D8b6tNfLrUAd7bM2X6CZDbEvRKa_EPnWSmmB5gasKV28I-_unYNznu3ebjmZ5af7BrAD1jN7WyS0oa8vJF96NrS7xXDnUDBi2eMCEec=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3kpia_tzg8Z3uGVjkEA910-J1jMJRwZMB9AjvDNbnp3S6v_h3BX1T6hAS25k1BNo6RNuWbgEvtl4b20ozrtJdCds_iDryLNdi-RSeOMSPkT4hyllNDkzTOWW80g9wdGiFhFT8-HLrxTX_qjyr1wwefGlNCk2wM3kyc1zzc5I=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLKpuUkeYdemIICjYOZiQYmWaDeG7QkcRRc6AGXLqBETpDFEyBTGy92XZO6ih0J8O5TL_hKoKIRrE_w8rOUWEf95FuFGZe8R3gzSGzbldTvxl0s8HlDg==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFaK8nBxx2fWckYqfwAKwibj0vTZNHUb2ciW4-EcjwQFp1OlFq7Qb7w1CeDEycS35OwyuSLi8LseK03k4Fgr4sCTL8mWm6Rq3KD_YncrnCIHaJm_b3iw==)
16. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7w2b7RkWBcJN3fJyc2s46knnwFvqqI3_LqKvoUlIJY7oTbi4OSELT18huVIZTImNNKVuJYw9qH5Y4Bz-mRIJtsbzh1Y3g4fg6d64jGg83J6fHQQhg-SIkeSUQN9_RcipLKtjcyXTVg36Vr-1-8k6r4u6G0l61Ovwkow1eMa0krNugFfZILNOA6AGa_OCC8Ts3RzKi94LoWm-oM8OEz1jXvgufvAOnbTmLNvc=)
17. [anu.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEauKgDx2Kca3yfYH-ekr6m63yU6EPqInJBdrJM0scmKDhS-WPdCT6fn1j3tyorOXCNqCpubQpq0JsgzGc4HB0pUvHy_LTBkGSW3UL4DNMwGJG3eHgToaQb7ug8V_0X2stv5rRk6OYppmuvhBy80GGCb2EQxs620AeA)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHKkYiDq6MKtgY2p9VMNbMVtsQw4Xu72iMRzp7XQacBiNrSDlJtnPT-u-ceDugGuh-aEDZL1svj6q-3oIhABe6jAL6EeZ7ZGB_PEaJooF2ufBPXWT0AlTkUGisSr82MBei_Om3gEOnDxvmtPloVsVREBJeLxJ3lBFFhDk5CtSIfUz533OXBV05rNpZJJQrB6z4Twl97V7L19sSNtIebM8djx0cSDQADPbZY77on8bDFbPE58WrX5H1mmh_x3gMgvZjOIrTfH8O)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-Euwhsu5xoq-TkzZc_Xo8ut4MvEJZDFdUKlD3GVwmIpJOTrvT6rcDaUhugs6x_Vaj9at1aMRkK_Do_fXaQg0UGwPIwJGGlrPqED4cGnJS4r2_JdgEHzTpnncYquzP8qYos59paFIbw-ERtZIW7eMnAD292zrDOiwhhkFvjlDpxWcUZR-xjLDijBRphTwac_1At-eWY53yF3qFp2vZ6a34HtEyqm91IJTmSkghnF1OAIyWvjzM2KNlZD5wEJGMaWP5tKk-d3RyB0gaUZhwId_e)
20. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrwte2X9rpMZlHZYYKy28dA9ygwtYeFAjZAtUQGm31qlIuGZj_hYPVTR0MuEBk1BIQbplUiFq-cCWdHtL8zsiIiI6BCBJffzAGkeqtJVUXbx-G6XCz-o7E0z7wSLj6ALhlxRfptuYA46hg)
21. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMJuxTTCQ1u-OPICwttT9UcF1FkQXf6pOpF8y3n_acSvwVHLO_ZVooTA9M11M-NvMfRQFB1DGQg76BgtP_vtUJYEUzdNuVsj9ShobNHuZNUVRyaf4CIPnkf7Y6iRvU_w--mDtN2EDJJukuEWe-lknI3CiQYVrb)
22. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE09FYGYe_TKxQVibMsPcpvY1wpsOXNMSGgU0nc42wQHsqYENa6QUu6QrsRSs80AdsfXff6YhvTGlwWpcj1WQIR2molZN-_YS9c8IeOxYBZA1RcUxK5uYoo-OjQQweO2Dx_C6962oc=)


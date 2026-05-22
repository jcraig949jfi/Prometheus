# Followup [FU-2026-05-22-038 <- row245]: # Stygian Attack Plan: Target BL-C-008 (Vinogradov Mean Value Adjacent)  ### Key Points *   **The Or

**Pythia queue id:** 323
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chcwcm9QYXFyVEljLWNqTWNQaWYtRDJBMBIXMHJvUGFxclRJYy1jak1jUGlmLUQyQTA
**Elapsed:** 247s
**Completed at:** 2026-05-22T02:13:30.705176+00:00

---

# Research Brief: Substrate-Grade Analysis of Vinogradov Mean Value Theorem (VMVT) Adjacent Frontiers

**Key Points:**
*   **Resolution of the Main Conjecture**: The original Main Conjecture of the Vinogradov Mean Value Theorem (VMVT) is universally recognized as definitively solved. This monumental achievement was reached independently via the $l^2$ decoupling method introduced by Bourgain, Demeter, and Guth, and the purely arithmetic Efficient Congruencing framework pioneered by Wooley. 
*   **The Extended Frontier**: The mathematical frontier has since shifted to adjacent, highly structured open problems. These include the Extended Main Conjecture of VMVT, small cap decoupling for the moment curve, inhomogeneous Vinogradov systems, and non-translation-dilation-invariant systems. 
*   **Methodological Synthesis**: Current state-of-the-art attack vectors involve synthesizing the Hardy-Littlewood circle method with refined shifting variable arguments and multiscale high-low frequency harmonic analysis.
*   **Subconvexity and Small Caps**: Recent breakthroughs (2024–2026) have successfully breached the classical square-root cancellation barriers in critical subconvexity cases and established sharp small cap decoupling estimates in $\mathbb{R}^3$.

This report details the current consensus, bounds, methodologies, and open trajectories surrounding the Vinogradov Mean Value adjacent problems, synthesizing findings from leading mathematical literature up through 2026.

***

## 1. Brief Summary

**Question**: What is the definitive status, current bounding landscape, and active attack vector consensus for the open problems adjacent to the solved Vinogradov Mean Value Theorem (e.g., the Extended Main Conjecture, inhomogeneous systems, and small cap decoupling)?

**Prometheus Context**: Initiated as a follow-up to a prior Gemini Deep Research report, this inquiry targets the `METHOD_GAP` bridged by the orthogonal synthesis of Bourgain-Demeter-Guth's continuous decoupling and Wooley's discrete efficient congruencing [cite: source_10, source_32]. The "Stygian Attack Plan" specifically interrogates target BL-C-008, recognizing that while LLM models often hallucinate the status of the Main Conjecture (erroneously classifying it as open), the actual frontier lies in highly specialized adjacent domains: subconvexity in inhomogeneous systems, non-translation-invariant diagonal equations, and small cap decoupling for the moment curve.

## 2. Flagged Findings

### 2.1 Current Consensus on the Post-VMVT Landscape
The literature from 2016 to 2026 reflects an absolute consensus that the canonical Main Conjecture of the Vinogradov Mean Value Theorem is solved [cite: source_10, source_32]. The historical theorem bounds the number of integral solutions $J_{s,k}(X)$ to the translation-dilation-invariant system of equations:
\[ \sum_{i=1}^s x_i^j = \sum_{i=1}^s y_i^j \quad (1 \le j \le k) \]
where $1 \le x_i, y_i \le X$. The resolution established that for $s \ge 1$, $J_{s,k}(X) \ll X^{s+\epsilon} + X^{2s - k(k+1)/2 + \epsilon}$, perfectly matching the diagonal and product-manifold heuristics [cite: source_13, source_32]. 

With the primary obstacle cleared, the consensus has rapidly decentralized into several distinct sub-disciplines:
1.  **The Extended Main Conjecture**: Researchers agree that the canonical theorem must be generalized to bounds involving fractional or restricted parameter domains. Oh and Yeon (2025) have established that shifting variable arguments layered into the Hardy-Littlewood circle method can provide sharp upper bounds for these extended systems, specifically resolving cases for $d=2,3$ [cite: source_22, source_36].
2.  **Small Cap Decoupling**: There is widespread agreement on the veracity of Demeter, Guth, and Wang's Conjecture 2.5 regarding $L^p$ estimates for exponential sums. Guth and Maldague (2024) have verified this in $\mathbb{R}^3$ [cite: source_18, source_45].
3.  **Inhomogeneous Systems and Subconvexity**: Wooley (2022/2023) has established a consensus that the classical square-root barrier for minor arc estimates can be broken for inhomogeneous Vinogradov systems in the critical case $s=k(k+1)/2$ [cite: source_33, source_51].

### 2.2 Potential Points of Failure and Algorithmic Risks
While the theoretical trajectory is stable, several analytical risks are flagged in the literature:
*   **Base Rate Fallacies in Decoupling**: In algorithmic evaluations of subcritical bounds, systems frequently exhibit **PATTERN_BASE_RATE_NEGLECT** by assuming canonical decoupling resolves inhomogeneous systems automatically, without accounting for the required shifted-variable adjustments or torsoial parametrizations required when translation invariance is broken [cite: source_34, source_54].
*   **Prime Weighting Overfits**: When mapping VMVT solutions onto prime variants, such as the Waring-Goldbach problem, one must avoid **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**. This occurs when exponential sums over primes are inappropriately bounded using generic Weyl sums without proper von Mangoldt weight segregation, leading to artificially tight but unprovable heuristics [cite: source_2, source_4].
*   **Conductor Conflations**: When assessing the analytic Hasse principle for corresponding local-global problems in diagonal equations (e.g., Brandes and Wooley, 2021), researchers risk **PATTERN_CONDUCTOR_CONFOUND** if they conflate the algebraic conductor of the underlying arithmetic variety with the analytic scale of the small caps in the frequency domain [cite: source_6, source_41].

## 3. Problem Statement

The post-VMVT research front is defined by several precise mathematical objects and their associated bounding conjectures. The interrogated results span four primary pillars:

### 3.1 The Extended Main Conjecture of VMVT
Let $d \ge 2$ be a natural number and $\boldsymbol{\alpha} = (\alpha_d, \ldots, \alpha_1) \in \mathbb{R}^d$. We define the canonical exponential sum:
\[ f_d(\boldsymbol{\alpha}; N) := \sum_{1 \le n \le N} e(\alpha_d n^d + \cdots + \alpha_1 n) \]
where $e(z) = e^{2\pi i z}$. The Extended Main Conjecture interrogates the mean values of these exponential sums over a restricted, asymmetric frequency domain. For $p > 0$ and a parameter $u$, one defines the integral:
\[ \mathcal{I}_{p,d}(u; N) := \int_{[0,1) \times [0, N^{-u}) \times [0,1)^{d-2}} |f_d(\boldsymbol{\alpha}; N)|^p d\boldsymbol{\alpha} \]
where the differential $d\boldsymbol{\alpha} = d\alpha_1 d\alpha_2 \cdots d\alpha_d$ [cite: source_36, source_37]. The problem is to ascertain the optimal upper bounds for $\mathcal{I}_{p,d}(u; N)$ for all $d \ge 2$, $0 \le u \le d-1$, and $p \ge 2$, thereby extending classical decoupling bounds into geometrically constrained sub-domains [cite: source_22, source_24].

### 3.2 Small Cap Decoupling for the Moment Curve
The decoupling problem involves a function $f$ whose Fourier transform is supported on a small neighborhood of a curve, specifically the moment curve $M_n = \{(t, t^2, \ldots, t^n) : t \in [cite: 1]\}$ in $\mathbb{R}^n$ [cite: source_17, source_47]. The objective is to estimate the $L^p$ norm of $f$ in terms of its Fourier projections onto linear blocks or "small caps." 
Specifically, Demeter, Guth, and Wang's Conjecture 2.5 (the object of interrogation) asks for sharp $L^p$ estimates for exponential sums over fractional intervals. For $n=3$, a sequence $a_k \in \mathbb{C}$ with $|a_k| \lesssim 1$, and an interval $H$ of length $1/N^\sigma$ ($0 \le \sigma \le 2$), the problem is to bound:
\[ \int_{[cite: 1]^2 \times H} \left| \sum_{k=1}^N a_k e(kx_1 + k^2x_2 + k^3x_3) \right|^{2s} dx \]
The conjectured bound is $\mathcal{O}(N^\epsilon [N^{s-\sigma} + N^{2s-6}])$ [cite: source_18, source_48].

### 3.3 Inhomogeneous Vinogradov Systems
While the standard VMVT evaluates homogeneous systems, the inhomogeneous variant introduces a non-zero shift vector $\mathbf{h} \in \mathbb{Z}^k$. The object of interest is $J_{s,k}(X; \mathbf{h})$, the number of integral solutions to the system:
\[ \sum_{i=1}^s (x_i^j - y_i^j) = h_j \quad (1 \le j \le k) \]
with $1 \le x_i, y_i \le X$ [cite: source_51, source_53]. The problem is to establish an asymptotic formula for $J_{s,k}(X; \mathbf{h})$ in the critical case $s = k(k+1)/2$, which requires minor arc estimates that strictly bypass the classical square-root cancellation barrier (subconvexity) [cite: source_33, source_54].

### 3.4 Non-Translation-Dilation-Invariant Systems
Classical VMVT relies heavily on translation and dilation invariance. Brandes and Wooley (2019/2021) established the problem of bounding mean values for Diophantine systems lacking this symmetry, specifically systems comprising $v$ cubic and $u$ quadratic diagonal equations in $6v + 4u + 1$ variables, to establish an analytic Hasse principle [cite: source_6, source_41].

## 4. Status & Bounds

The empirical and theoretical status of these open problems has advanced dramatically. The current best known bounds and conditional qualifiers are as follows:

### 4.1 Extended Main Conjecture Bounds
Status: **Partially Resolved / Conditionally Bounded.**
Oh and Yeon (2025) achieved sharp upper bounds for $\mathcal{I}_{p,d}(u; N)$ [cite: source_36, source_37].
*   **Unconditional Bounds ($d=2, 3$)**: For dimensions 2 and 3, and $0 < u \le 1$, the sharp upper bound has been rigorously established in the range $d(d-1) < p < d(d+1)$ [cite: source_22, source_26].
*   **Specific Sub-range ($d=3$)**: For $d=3$ and $1 < u \le 2$, the sharp bound is derived in the range $p \ge 12 - 6/(4-u)$ [cite: source_22].
*   **Conditional Higher Dimensions ($d \ge 4$)**: For $d \ge 4$, analogous results are proven *conditional* on the assumed small cap decoupling inequalities for the moment curves in $\mathbb{R}^d$ [cite: source_37].

### 4.2 Small Cap Decoupling Bounds (Conjecture 2.5)
Status: **Resolved for $n=3$.**
Guth and Maldague (2024) definitively proved Conjecture 2.5 for the moment curve in $\mathbb{R}^3$ [cite: source_18, source_45].
*   **Current Best Bound**: For $0 \le \sigma \le 2$, $s \ge 1$, interval $H$ of length $1/N^\sigma$:
    \[ \int_{[cite: 1]^2 \times H} \left| \sum_{k=1}^N a_k e(kx_1 + k^2x_2 + k^3x_3) \right|^{2s} dx \le C_\epsilon N^\epsilon \left[ N^{s-\sigma} + N^{2s-6} \right] \]
*   **Qualifiers**: The bound $N^{s-\sigma}$ arises from random $a_\xi \in \{\pm 1\}$ (via Khintchine's inequality), while the $N^{2s-6}$ term is dominated by the constructive example $a_\xi = 1$ where the integrand peaks at $\gtrsim N^{2s}$ on a roughly $[0, 1/N] \times [0, 1/N^2] \times [0, 1/N^3]$ box [cite: source_18, source_47].

### 4.3 Inhomogeneous Systems and Subconvexity Bounds
Status: **Asymptotics Established for Critical Case.**
Wooley (2022, 2023) established the asymptotic formula for $J_{s,k}(X; \mathbf{h})$ in the critical regime [cite: source_33, source_51].
*   **Prior Status**: For subcritical $s < k(k+1)/2$ and non-zero shift, Brandes and Hughes proved $J_{s,k}(X; \mathbf{h}) = o(X^s)$ [cite: source_33, source_51].
*   **Current Breakthrough**: Subject to an extension of the main conjecture, for $s = k(k+1)/2$, minor arc estimates surpass square-root cancellation, yielding a rigid asymptotic formula encoding the density of solutions over local completions. For $1 \le l \le (k+1)/3$ and $s < k(k+1)/2$, subconvex bounds are unconditional [cite: source_33, source_53].

### 4.4 Waring-Goldbach and Adjacent Primitive Bounds
Status: **Continual Refinement via VMVT.**
Kumchev and Wooley utilized efficient congruencing and modern VMVT decoupling to refine bounds for $H(k)$ (the least integer $s$ such that every large integer subject to local conditions is a sum of $s$ prime $k$-th powers) [cite: source_2, source_4].
*   **Current Best Bound**: For large $k$, $H(k) \le (4k - 2) \log k - (2 \log 2 - 1)k - 3$ [cite: source_4].
*   **Historical Context**: This represents the first absolute improvement over Hua's classical 1940s bound of $H(k) \le 2k+1$ in several decades, directly enabled by modern Weyl sum estimates stemming from VMVT [cite: source_1, source_2].

## 5. Literature (Primary Sources)

The foundation of the modern post-VMVT era is built on primary literature published between 2015 and 2026. The most critical primary sources are documented below:

1.  **Oh, C., & Yeon, K. (2025).** *An extended Vinogradov's mean value theorem*. Transactions of the American Mathematical Society. arXiv:2506.01751 [math.NT].
    *   **Focus**: Proof of the extended VMVT via Hardy-Littlewood methods and shifting variable arguments for $d=2,3$ [cite: source_22, source_36, source_37].
2.  **Guth, L., & Maldague, D. (2024).** *Small cap decoupling for the moment curve in $\mathbb{R}^3$*. Analysis & PDE, 17(10), 3551–3588. DOI: 10.2140/apde.2024.17.3551. arXiv:2206.01574 [math.CA].
    *   **Focus**: Verification of Conjecture 2.5 of Demeter, Guth, and Wang. Sharp small cap estimates utilizing multiscale high/low-frequency harmonic analysis [cite: source_18, source_45, source_47].
3.  **Wooley, T. D. (2023).** *Subconvexity in inhomogeneous Vinogradov systems*. The Quarterly Journal of Mathematics, 74(1), 389–418. DOI: 10.1093/qmath/haac027. arXiv:2202.14003 [math.NT].
    *   **Focus**: Broken square-root barriers and rigorous asymptotic local-global derivations for shifted Vinogradov sums at the critical threshold $s=k(k+1)/2$ [cite: source_33, source_51, source_54].
4.  **Brandes, J., & Wooley, T. D. (2021).** *Optimal mean value estimates beyond Vinogradov's mean value theorem*. Acta Arithmetica, 200(2), 149-182. DOI: 10.4064/aa200824-9-3. arXiv:1901.03153 [math.NT].
    *   **Focus**: The first sharp mean value estimates for non-translation-dilation-invariant Diophantine systems. Establishing Hasse principles for combined cubic/quadratic forms [cite: source_8, source_41, source_43].
5.  **Bourgain, J., Demeter, C., & Guth, L. (2016).** *Proof of the main conjecture in Vinogradov's mean value theorem for degrees higher than three*. Annals of Mathematics, 184(2), 633–682.
    *   **Focus**: The original continuous $l^2$ decoupling proof of the VMVT Main Conjecture [cite: source_10, source_32].
6.  **Kumchev, A. V., & Wooley, T. D. (2016).** *On the Waring-Goldbach problem for seventh and higher powers*. Journal of the London Mathematical Society. arXiv:1510.00982 [math.NT].
    *   **Focus**: Translation of VMVT estimates into the Waring-Goldbach space, updating Hua's bounds [cite: source_2, source_4].

## 6. Attack Vectors

The current arsenal for attacking VMVT-adjacent open problems relies on a synthesis of classical number theory, discrete arithmetic, and continuous harmonic analysis.

### 6.1 Live Techniques

**1. Multiscale High/Low-Frequency Harmonic Analysis ($l^2$ Decoupling)**
Pioneered by Bourgain, Demeter, and Guth, decoupling estimates bound the $L^p$ norm of a function in terms of its localized Fourier projections. For the small cap moment curve problem (Guth & Maldague, 2024), the technique relies heavily on high-low frequency partitioning. Functions are decomposed into frequency scales; spatial blocks where Fourier projections overlap heavily are bounded using high-frequency canonical decoupling from the cone, while dispersed components utilize standard $L^2$ orthogonality [cite: source_17, source_18, source_47]. This process is iterated across dyadic scales, leveraging geometric transversality and multilinear Kakeya-type incidence bounds.

**2. The Hardy-Littlewood Circle Method + Shifting Variables**
To tackle the Extended Main Conjecture and subconvexity bounds, the traditional circle method (dissecting the frequency interval $[0,1)$ into major and minor arcs) is insufficient alone. Oh and Yeon (2025) deploy a "refined shifting variables argument." This relates the localized integral $\mathcal{I}_{p,d}(u; N)$ to alternative mean values containing shifting polynomials $S_p(u)$ and $T_p(u; \epsilon)$. This process isolates the contribution of specific shifting variables to generate pseudo-translation symmetries, thereby allowing the application of sub-critical decoupling inequalities locally [cite: source_26, source_36].

**3. Efficient Congruencing (Discrete Arithmetic)**
Wooley's "Efficient Congruencing" remains an exceptionally viable attack vector. It fundamentally operates by utilizing $p$-adic congruences recursively to force polynomial constraints on subsets of variables. Rather than analyzing continuous spaces, it uses diminishing ranges and nested multigrade identities to count exact integer solutions modulo high prime powers. It has been uniquely successful in transferring bounds to prime variables (Waring-Goldbach) where continuous decoupling struggles with von Mangoldt weights [cite: source_4, source_35, source_50].

**4. Torsoial Parametrizations / Paucity Theory**
For bounding non-diagonal positive integral solutions, multiplicative polynomial identities are used to group variables into torsor-like structures. In the subconvexity regimes (Wooley, 2022), this "paucity of non-diagonal solutions" is leveraged to show that the generic off-diagonal sum terms contribute trivially compared to the exact matches, vastly lowering the rank of the algebraic system evaluated [cite: source_16, source_33].

### 6.2 Exhausted Approaches

**1. Simple Weyl Differencing (Classical)**
The classical Weyl differencing method, which iteratively squares exponential sums to reduce polynomial degrees recursively, yields bounds that are exponentially weak (requiring $s > 2^k$). While foundational, it is completely exhausted for achieving sharp bounds near the critical threshold $s = k(k+1)/2$ [cite: source_10, source_32].

**2. Classical Diminishing Ranges**
While a variant is still used within efficient congruencing, the classical diminishing ranges method of Hardy and Littlewood (where variables are constrained to geometrically decreasing intervals to artificially force uniqueness of solution) is largely exhausted as a primary engine for obtaining sharp mean value constants, having been fully subsumed by decoupling [cite: source_2, source_3].

## 7. Cross-References

### 7.1 Related Open Problems
*   **The Parsell-Vinogradov Systems**: This involves generalizing the VMVT to multi-dimensional surfaces. Specifically, the number of integer solutions bounded on a 2-dimensional surface defined by a Parsell-Vinogradov system. Decoupling inequalities are actively sought for general down-sets $D \subset \mathbb{N}^d$ [cite: source_27, source_28]. Recent extensions verify transversality conjectures necessary for these moment manifolds using extensions of the Schwartz-Zippel lemma [cite: source_27, source_31].
*   **The Prouhet-Tarry-Escott (PTE) Problem**: Estimating $W(k, s)$, the minimal number of variables needed for identical polynomial sums up to degree $k$ without strict permutation identity. Improvements in VMVT directly cascade down into PTE estimates, shrinking the variable gap required to establish symmetric integer sets [cite: source_3].
*   **Waring's Problem for Function Fields**: Similar mean value techniques are now being ported to estimate asymptotic bounds for Fermat hypersurfaces over finite fields (Manin's conjecture variant), bypassing analytic minor arc estimates entirely in favor of treating them as complete exponential sums via Katz bounds [cite: source_24, source_38].

### 7.2 Anti-Anchors and Contrarian Vectors
*   **Non-Vinogradov Type Diophantine Systems**: An explicit anti-anchor to VMVT approaches is the work on systems that are *not* translation-dilation-invariant [cite: source_41, source_44]. Classical decoupling relies on parabolic rescaling (dilation invariance). Brandes and Wooley's establishment of the Hasse principle for generic cubic and quadratic systems represents a fundamental contrarian vector, proving that optimal bounds can be established independent of these rigid symmetries [cite: source_6, source_43].

### 7.3 Candidate Primitives
*   **Local-Global Completion Metrics**: The $\mathcal{I}_{p,d}$ bounding primitive introduced by Oh & Yeon forms a high-probability base for evaluating new density matrices for prime-based Waring configurations. 
*   **Fractional Cap Decompositions**: The $N^{s-\sigma}$ scaling mechanism in Guth & Maldague's proof constitutes a robust geometric primitive for bounding general oscillatory integrals over highly curved, non-flat moment manifolds, acting as a potential bridge toward solving the larger restriction conjecture.

**Sources:**
1. [math.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEx2jvxZJ0Z6-z5ZwQdmXHZ7UCgq8Ww5TUqKaZTK4Lz1fdwXm5qG50Zxoef2HNrwbNJHrWKrrmZq41Q3N0Xpo4xSCZj1Mg0FqIACh2Oa9i3wBDr4GfKvruuXJHLtcO3aFMw1BQCDcaLHPHhS4jojmpN)


# Followup [FU-2026-05-22-051 <- row260]: [it remains open with bounds on $E(N)$]" [cite: 3, 4]

**Pythia queue id:** 336
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdSTDhQYW9yOExvTGdfdU1QcVlidGtBcxIXUkw4UGFvcjhMb0xnX3VNUHFZYnRrQXM
**Elapsed:** 248s
**Completed at:** 2026-05-22T02:32:29.277087+00:00

---

# Substrate-Grade Research Brief: Exceptional Set Bounds in the Binary Goldbach Problem

**Key Points**
*   The Binary Goldbach Conjecture (that every even integer \( N > 2 \) is the sum of two primes) remains definitively open, contrary to frequent conflations with Helfgott’s 2013 proof of the Ternary Goldbach Conjecture. 
*   Current research focuses on bounding the "exceptional set" \( E(X) \), which counts the number of even integers up to \( X \) that cannot be expressed as the sum of two primes. 
*   The most widely accepted, unconditionally proven upper bound for the exceptional set is \( E(X) \ll X^{0.72} \), established by János Pintz in 2018. 
*   Recent preprint literature (late 2025/early 2026) by Genheng Zhao claims an improved unconditional bound of \( E(X) \ll X^{0.709} \), achieved via a refined dichotomy argument on the zeroes of Dirichlet \( L \)-functions.
*   Under the Generalized Riemann Hypothesis (GRH), the bound drops dramatically to \( E(X) \ll X^{1/2 + \epsilon} \), though bridging the gap between average equidistribution bounds and pointwise certainty remains obstructed by severe analytic barriers.

**Contextual Preamble**
This brief serves as a definitive status update on the open question surrounding the bounds of \( E(N) \) in the binary Goldbach problem, surfaced as a follow-up to a prior Gemini Deep Research report (Aporia docs, 2026-05-21). As noted in the telemetry, LLM generation artifacts (such as a v10-battery generation claiming "Goldbach's conjecture was proven in 2013") frequently exhibit a hallucination vector where Helfgott's resolution of the *odd* (ternary) Goldbach problem is mistakenly applied to the *even* (binary) problem. This document establishes a strict falsification quarantine, providing the precise mathematical boundaries, current consensus, and live attack vectors for the binary Goldbach exceptional set.

---

## 1. Brief Summary
With the Ternary Goldbach conjecture resolved for \( N \ge 7 \) by Helfgott [cite: 1, 2], Prometheus telemetry isolates the Binary Goldbach problem to investigations of the exceptional set \( E(N) \), where the pursuit of proving \( E(N) = 0 \) for large \( N \) remains open and is currently constrained by unconditional asymptotic bounds of \( E(N) \ll N^{0.709} \) [cite: 3].

## 2. Flagged Findings
**Current Consensus:** The mathematical consensus firmly holds that almost all even integers are the sum of two primes, meaning the density of the exceptional set \( E(X) \) approaches zero as \( X \to \infty \). The foundational milestone was set by Montgomery and Vaughan (1975), who proved unconditionally that \( E(X) \ll X^{1-\delta} \) for some unspecified \( \delta > 0 \) [cite: 3, 4]. Over the decades, analytical improvements in zero-density estimates for Dirichlet \( L \)-functions allowed researchers to explicitly quantify and enlarge \( \delta \). The current rigorously peer-reviewed consensus bound is \( E(X) \ll X^{0.72} \), derived by János Pintz in 2018 through a novel explicit formula for the contribution of the major arcs [cite: 5]. Highly recent preprint findings (Nov 2025/Jan 2026) by Genheng Zhao propose a further reduction to \( E(X) = O(X^{0.709}) \) using a dichotomy argument that reduces the number of Dirichlet zeroes under consideration by nearly half [cite: 3].

**Where the Consensus Might Be Wrong (or Structurally Limited):**
While the asymptotic bounds are robust, the assumption that incremental improvements in \( \delta \) will eventually lead to a proof of the full conjecture (i.e., \( E(X) = 0 \) for \( X \ge 4 \)) is a manifestation of **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**. The analytical models successfully bound the *average* behavior of the Goldbach representation function \( R(n) \) by assuming the prime distribution asymptotically hugs the Cramér random model on the major arcs. However, this global averaging masks localized pointwise failures. Recent structural diagnostics, such as the "FB3 Pointwise Barrier in Arithmetic Decorrelation" (2026), establish no-go theorems indicating that Bombieri-Friedlander-Iwaniec (BFI) type equidistribution bounds cannot achieve the necessary pointwise power savings for certain prime moduli [cite: 6]. 

Furthermore, attempts to push these bounds often fall victim to **PATTERN_CONDUCTOR_CONFOUND**, where the highly composite nature of conductors \( q \) in the major arcs creates structural interference. Researchers frequently confound the average equidistribution of primes modulo \( q \) with the absolute pointwise bounds required to rule out highly specific, localized counterexamples to the binary Goldbach conjecture. Consequently, while the bound \( X^{0.709} \) may be analytically valid, the methodology used to achieve it is likely fundamentally incapable of reaching the \( O(1) \) bound required to prove the binary conjecture.

## 3. Problem Statement
The precise object being interrogated is the **exceptional set of Goldbach numbers**, denoted as \( E(X) \). 

Let \( \mathcal{P} \) be the set of all prime numbers. The binary Goldbach conjecture posits that every even integer \( n > 2 \) can be expressed as \( n = p_1 + p_2 \) where \( p_1, p_2 \in \mathcal{P} \). The exceptional set is defined formally as:
\[ E(X) = |\{ n \le X : n \equiv 0 \pmod 2, \; n \notin \mathcal{P} + \mathcal{P} \}| \]

To study \( E(X) \), analytic number theorists utilize the weighted representation function:
\[ R(n) = \sum_{p_1 + p_2 = n} \log p_1 \log p_2 \]
If the binary Goldbach conjecture holds for a number \( n \), then \( R(n) > 0 \). 

The problem is typically attacked using the Hardy-Littlewood Circle Method. The generating function for the primes is constructed as an exponential sum:
\[ S(\alpha) = \sum_{p \le X} (\log p) e(p\alpha) \]
where \( e(x) = e^{2\pi i x} \). The representation function is then extracted via the Fourier integral over the unit interval:
\[ R(n) = \int_{0}^{1} S(\alpha)^2 e(-n\alpha) d\alpha \]
The interval \( [cite: 7] \) is dissected into "major arcs" \( \mathfrak{M} \) (neighborhoods of rational numbers \( a/q \) with small denominators \( q \)) and "minor arcs" \( \mathfrak{m} \) (the remainder of the interval). The problem statement thus translates to bounding the integral over the minor arcs:
\[ \int_{\mathfrak{m}} S(\alpha)^2 e(-n\alpha) d\alpha \]
Because this integral cannot currently be shown to be smaller than the main term from the major arcs for *individual* \( n \), researchers employ Parseval's identity and Bessel's inequality to bound the minor arc contributions *on average* over all \( n \le X \), yielding bounds on the size of the exceptional set \( E(X) \) rather than proving \( R(n) > 0 \) for all \( n \).

## 4. Status & Bounds
The historical progression and current status of bounds on \( E(X) \) are as follows:

**1. Conditional Bounds (Under GRH):**
If one assumes the Generalized Riemann Hypothesis (GRH) for Dirichlet \( L \)-functions, the error terms in the prime number theorem for arithmetic progressions are optimally bounded. Under GRH, Hardy and Littlewood (1924) originally proved that \( E(X) \ll X^{1/2 + \epsilon} \) for any \( \epsilon > 0 \) [cite: 3, 8]. Refinements by Goldston (1992) yielded the tighter conditional bound \( E(X) \ll X^{1/2} \log^3 X \) [cite: 9]. 

**2. Early Unconditional Bounds:**
*   **1937:** Chudakov, van der Corput, and Estermann independently utilized Vinogradov's methods to prove that almost all even numbers are the sum of two primes, establishing \( E(X) = O(X \log^{-A} X) \) for any \( A > 0 \) [cite: 2, 3].
*   **1975:** Montgomery and Vaughan provided a monumental breakthrough, proving that \( E(X) = O(X^{1-\delta}) \) for a small, effectively computable but initially unspecified constant \( \delta > 0 \) [cite: 3, 4]. This proved that the exceptional set has a power-saving bound.

**3. The Optimization of \( \delta \) (1989–2010):**
Extracting explicit values for \( \delta \) requires an intricate analysis of the distribution of zeroes of Dirichlet \( L \)-functions near the line \( \text{Re}(s) = 1 \).
*   **1989:** J.R. Chen and J.M. Liu established \( \delta = 0.05 \) (\( E(X) \ll X^{0.95} \)) [cite: 3].
*   **2000:** H.Z. Li improved the bound to \( \delta = 0.086 \) (\( E(X) \ll X^{0.914} \)) [cite: 3, 10].
*   **2010:** W.C. Lu established \( \delta = 0.121 \) (\( E(X) \ll X^{0.879} \)) [cite: 3].

**4. Current Best Bounds (2018–2026):**
*   **János Pintz (2018):** Through a fundamental restructuring of the explicit formulas for the contribution of the major arcs, Pintz achieved a massive leap, establishing \( \delta = 0.28 \), which yields the bound **\( E(X) \ll X^{0.72} \)** [cite: 5]. This remains the most widely cited and thoroughly verified unconditional bound in the established literature.
*   **Genheng Zhao (Nov 2025 / Jan 2026):** In a recent preprint, Zhao builds upon Pintz's method. By employing a dichotomy argument to the parameter \( N(\lambda) \) (the number of zeroes of Dirichlet \( L \)-functions in a highly restricted area), Zhao reduces the influence of the zeroes by nearly half, claiming an improved bound of \( \delta = 0.291 \), leading to **\( E(X) \ll X^{0.709} \)** (with an ineffective implicit constant) [cite: 3]. 

**5. Variant Conditional Qualifiers:**
If we loosen the constraints to allow a sum of a prime and an "almost prime" (a number with at most two prime factors, \( P_2 \)), Chen's Theorem proves that all sufficiently large even numbers are of the form \( p + P_2 \) [cite: 8, 11]. Recently (August 2025), Grimmelt and Teräväinen proved that all natural numbers \( n \equiv 4 \pmod 6 \) are the sum of two Chen primes, apart from a power-saving set of exceptions, which they argue is optimal barring substantial progress on the twin prime or binary Goldbach conjectures themselves [cite: 11, 12].

## 5. Literature (Primary Sources)
*   **Zhao, G. (January 2026).** *The exceptional set of Goldbach problem and Linnik's constant.* arXiv:2511.05631v2 [math.NT]. Provides the current leading pre-print bound of \( E(X) = O(X^{0.709}) \) [cite: 13, 14].
*   **Grimmelt, L., & Teräväinen, J. (August 2025).** *The Exceptional Set in Goldbach's Problem with two Chen Primes.* arXiv:2508.16400 [math.NT]. Establishes power-saving exceptions for sums of Chen primes [cite: 11, 12].
*   **Pintz, J. (April 2018).** *A new explicit formula in the additive theory of primes with applications II. The exceptional set in Goldbach's problem.* arXiv:1804.09084 [math.NT]. Establishes the universally recognized \( E(X) < X^{0.72} \) bound [cite: 5].
*   **Montgomery, H. L., & Vaughan, R. C. (1975).** *The exceptional set in Goldbach's problem.* Acta Arithmetica, 27, 353-370. The foundational paper establishing the \( X^{1-\delta} \) power-saving framework [cite: 4, 15].
*   **Lu, W. C. (2010).** *Exceptional set of Goldbach number.* Journal of Number Theory, 130(10), 2359-2392. The pre-Pintz benchmark, establishing the \( X^{0.879} \) bound [cite: 3].
*   **Li, H. Z. (2000).** *The exceptional set of Goldbach numbers II.* Acta Arithmetica, 92(1), 71-88. Established the \( X^{0.914} \) bound [cite: 3, 10].

## 6. Attack Vectors
### Live Techniques
1.  **Refined Zero-Density Estimates:** The primary engine for reducing the exponent in the exceptional set bound relies on zero-density theorems for Dirichlet \( L \)-functions. Specifically, researchers seek to bound \( N(\sigma, T, \chi) \), the number of zeroes \( \rho = \beta + i\gamma \) of \( L(s, \chi) \) with \( \beta \ge \sigma \) and \( |\gamma| \le T \). The modern method (as seen in Pintz and Zhao) restricts the influence of these zeroes to a single modulus and a highly constrained geometric area, heavily leveraging Gallagher's Lemma and log-free zero density estimates [cite: 3, 16].
2.  **Explicit Formulas for Major Arcs:** Instead of simply applying the Siegel-Walfisz theorem to bound the error on the major arcs (which results in an ineffective constant and lost numerical precision), recent methods compute an *explicit formula* for the major arc integrals. This translates the error term directly into a sum over the zeroes of \( L \)-functions, allowing for exact analytical cancellation and leading to the jumps from \( 0.879 \) to \( 0.72 \) and \( 0.709 \) [cite: 5].
3.  **Dichotomy Arguments:** Introduced in Zhao's 2025/2026 work, this technique divides the summation over zeroes into subsets based on the spacing and density of the imaginary parts \( \gamma \). By treating dense and sparse zero-clusters differently, researchers can optimize the bounding constants (e.g., improving \( \delta \) from 0.28 to 0.291) [cite: 3].

### Exhausted Approaches
1.  **Pure Sieve Theory:** Sieve methods alone (such as the Selberg sieve or the combinatorial sieve) are mathematically exhausted regarding the pure binary Goldbach problem. This limitation is famously characterized as the "parity problem." As Terence Tao summarizes, sieve theory cannot natively distinguish between integers with an odd number of prime factors and an even number of prime factors without injecting additional external ingredients (like bilinear forms). Any upper bounds generated by a pure sieve will always be off from the true asymptotic limit by a factor of 2 or more [cite: 15]. This manifests **PATTERN_RANK_PARITY_LEAK**, where the topological structure of the primes "leaks" parity parity information that the sieve's basic counting mechanism is entirely blind to, hard-capping its efficacy at "almost prime" results like Chen's Theorem (\( p + P_2 \)).
2.  **Global Minor Arc Bounds via Vinogradov:** Attempting to prove that the minor arc integral \( \int_{\mathfrak{m}} S(\alpha)^2 e(-n\alpha) d\alpha \) is strictly smaller than the major arc main term for *every* individual \( n \) using purely classical exponential sum estimates (like Vinogradov's bounds on \( S(\alpha) \)) has proven structurally impossible with current technology. The cancellation is too fragile, forcing reliance on \( L^2 \) averages via Parseval's identity, which inherently yields exceptional set bounds rather than absolute proofs [cite: 4, 15].

## 7. Cross-References
*   **Ternary Goldbach Conjecture (The Anti-Anchor):** Proven by Harald Helfgott in 2013, establishing that every odd number \( N \ge 7 \) is the sum of three primes [cite: 1, 2]. It acts as an *anti-anchor* because non-experts (and AI models) frequently assume its proof entails the resolution of the binary problem. The ternary problem is analytically vastly easier because the integral \( \int S(\alpha)^3 e(-n\alpha) d\alpha \) provides an extra degree of freedom, allowing the minor arcs to be bounded trivially using the sup-norm of \( S(\alpha) \). This does not work for the \( S(\alpha)^2 \) binary integral.
*   **Linnik's Constant (Primes + Powers of 2):** A related open problem where the rigidity of the binary Goldbach problem is softened. Yuri Linnik proved that every large even integer is the sum of two primes and at most \( K \) powers of 2. Unconditionally, Pintz and Ruzsa (2020) proved \( K=8 \). Under GRH, Heath-Brown and Schlage-Puchta showed \( K=7 \) works [cite: 8]. The analytic techniques used to bound \( E(X) \) directly cross-pollinate with efforts to minimize \( K \) [cite: 3, 13].
*   **De Polignac's Conjecture / Twin Prime Conjecture:** The twin prime conjecture (that there are infinitely many primes \( p \) such that \( p+2 \) is prime) shares identical analytical DNA with the binary Goldbach problem (shifting the equation from \( p_1 + p_2 = 2n \) to \( p_1 - p_2 = 2k \)). Exceptional set bounds for Goldbach are conceptually mirrored by bounds on the number of integers not expressible as prime differences [cite: 11, 17].
*   **Digitally Restricted Sets:** Recent work (2025) by Brüdern, Kawada, and Wooley explores the Goldbach conjecture on sets with restricted digits (e.g., base \( b \) numbers missing certain digits). They utilize the \( X^{0.72} \) exceptional set bound to prove that almost all elements of these digitally restricted sparse sets still satisfy the Goldbach conjecture, provided the density of the restricted set exceeds the \( 0.72 \) threshold [cite: 18].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK7fsYkLwRAOtbdUzDzILXQYjXKTbYxu1-XeNoePtaBtOAes4fY5ylokF869t9MIsXcsiBqmn9TcovcYQ4_0qOPJSooK-X-pSSkSv1OSc6jlV71s9mrg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQWPpF7Kok1662_8RXjKS_Uw9Zq5fqP-6PYOohN5LlYHxpie9UHn3g3a_BI9xuk5t30lxDGOQVaZb-dGoChn3SX1Qv7xJYgszOKcZzy12NUozo8I-RkEm9xw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxwJaLAv74HlGd2sWJJ0wx7AFe9Y7rWGhXWeX_6amK7I9X_S-kPfl9Cn-FdIafatB5Ne3WzeQXbfJ5nOA7OVF0_CUeKro1IsVOdfhY_Qj5OafA74OQb8HzIg==)
4. [icm.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiWgm6LzoaUJjss4h3R9lF78ZKNTTxrbRfZlCHg4erE1imFHa_YPIexo__YJ9k7pe3kABz0RQO46VEuxR_x8hqtk1Yk5zoHmJTYSlAef6UZ3sBl8v-Ft9AaYMeW_JD8y5hri71q74g4_y8kA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZjZaPBN-m5-Kn-4KLT0kRenaGobRJ57J5c5p72f1Sf7m2BdvIACwpgQu8UWYNF3TQwio0gD7foZ2J6m0GGzIthb_CMWjlq9sa0NJ9f7F7hsyNdimxyA==)
6. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8rsrIcbcvJIr0tIRUmLv5C3uJP7DWL-Yuvg80O27ydbIsjRdvJHXX43xmislKw29ptjEwQ_NRtZ4kOaKshTGVds7AoAvDcbj0s_kCpVWCEvNHN8CFdi2WDQ8o9Ecb3XQ3dkjqi_OXUVlfSih-beNXT5hlTrPP8SQpPWMet1iRKez2LRXXQL3egSyT3bcUQbRCqSsenV8=)
7. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3y_oJEK0GGa2fLSGa3zSNdEw6j0oeRT-7O3Qk72kJfvIxrd5a0sb2KkrxYFfgIerZX-ercdRR0C3r7p2ye1t0d03W38sM2QOtACE3l68mnZSG-rfwKhLM97P4AuOj6b_OwgfQgZzZTnvsAC772Uu38I3pSfetQJC9jAdfUmX8YC9ST67eQLmJ6JrNrX2Oij5J98XdVRJfiUB2xfu0kdt5KW8=)
8. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtAfpjNxQLZ-AOUW1vwNhO-weLV_AVIr8baL_-oNWnKb-e0L4uMYmymcZjO-_3uBV6byKC6mHWvL82Sy3I7U6agReD9TDBDtWYu1h3lLRfGlvGd86alIhr-EFLbPE7SqWn9h3jP0VSyI6Y4w==)
9. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHusgblc1PywPzgM4v3-MxFfAh9lQdNI2hHnbfdaARqIaRHrVjYn9X_QndA8QhljZu7Rtt19aTgKHL-ZWHTDgOywBdj2Oxmlk5tV2yYahAnpXq986o7yMyFIXV92WvaMGMBrX2IRSUjTdrwI4Jp4UhW1bBvGjKofDKj73rxOXJnuqco16ctDBkDnxvOLX3RTHxLD5l-wFfPOEU=)
10. [icm.edu.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQ1uFtDa9XcPkNfAFae7CABu_Op22zjWDeXcOUxUVeJhM8tZplrxrv4U6VKYpJJ90Z7MBxajP5mt92z5LhjzKCu5uKmUTcRJML__9pM-gNBItoJhDDbnHHGCdc_bEKwMFJJubk2wBRG4I=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER-Ssp1QvkqN4jYhGu2ynzkBGw2nuVdAey6jQJOx3wNQggPsWxdRu-nCdZVJf7TXxiBTeqSEL991Z--CAwuC0PhtTE5w1dU0RBIDqDGFDONJz3bY4ZOw==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBLXollChFKtTO1xcLSIXfmIy447nJZPVGliOvzUNibA2rqnt4tfmbbOvLo7yZIj8kiilBivMHU1Ev-b8WTaStpl3GucT7TQLLbHwbHbf25er9I9Rlcb2GZpifoNCuvM7TH_T8gnN0WMMXHsVJFCqGzlpIdYgs3m2ewBrzsQayZXChCtbtu_NEtLUPFel3lO7_Pa0f9np7ZxiROXKr_d5dlZUiGQpZUw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMnGWuDggqhn60SPZjUwYJozPBjL_dgLt9ejZlTkh6Thk3QLtXAtFWhOh1VAtPVkWJmQG6_OUpLoMuvYed_lBtH2jyK-Nn3OhWyUQimT53ydyYbMiusw==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8t3Sf3ye0rDsELP_DgWwAEKRzTRk0iuUmaeQFHTFySL6RLHye5hGsAp5g1Gcj3-DSoX5FwBvUWvmvrZw34XxwmlcepjrhuS4AX9LYjuOjsv7Ay1YrzE75iw==)
15. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB3P55LcuHXn5dLtJC859PaFehQc2MOUd2Raa50K_PUjOmM4KozkAp1uNVQDHX0ELeN7FaV1FXJQ61Qr6rsNVcljjX1k6cKI5Cr_W-kYi08SvVWsx83DTlfaZKzXkqgeA0pHXSrJsXWUXkmWXY_eFfCgLoYmCTnDgTo5kgwG5ydM66-hPyKjGj-PoKwnxFLVoM9-ypOC4WN8zHNAcVQDecAKPSep8rRUabzZKGng==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhh7TB24mAPBQBHLYYtwyFxr1P3nw3-Rao5_RZ6L3nunkjZ7axMapPyL8N_E0SJ6EAyFqYBvY315dt6L6Fh0nLS7BAdnlyWhu4a9mE_kATOZrcZN1XhA==)
17. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX9T_yyXXm7ICp7Cb9JXOOidGmZXOvzUKgt5CvF1kHySiD17AcgDQk3-N8iduw1sPuMBEBBVLTj3J9kWPvOz3rpJsZSY5LUG-cvdcKvJKEHAfBnybO6FB8H3eq0tIAoLWD9t_eT92reE2nVQO-Vdf2fsJf9hFo1h6wuDotPdapcpRw8DF7g25WVmf_OSL02v2dQ6htj1xz4V-ukt6ot0ur1yZcSvyMkNLsq6MuMd6esJ7nt6rI6V_cmE3NixFwxrkFYc3Sneyr3Hb9He3T3JVd0tdWBSkhN7TJcoKEjWI7BKak_iq25qReETQfPxW8Tst3ZTYU8VQCwXgMM37MvzEhbLOBd42DTlE4VA==)
18. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyweYmCBrSfPetpxGjpOjrQo4vaRxQfEXJQT7Tfjwrdi-zqPA_DEc-sZKffPCgpEZQ_DMFQAtsnG6xmiDXvAhR13fI71ckfAm37rFBAY0NPQkkczgJVBcnNZ68E_D83NbPxdoGAKS1nIOaHIQiuBqKRY-7OZWe3xeiCU4kQbq4CZLqQWo1n3emZKp6n-T8w1SfuWgZDtTwneCKylGrDG2miRA-ITBOnj9fWJEqaMBIIP__hwGpKbQiaTDo3tY4WmFnm9GAM5N1VwnjAQ-TJ3uxBvm_eDvQvTlpgmrX_xWiFNRlwzqftrHytp1SU5Y=)


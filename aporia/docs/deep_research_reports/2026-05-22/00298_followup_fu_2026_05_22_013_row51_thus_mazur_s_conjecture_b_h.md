# Followup [FU-2026-05-22-013 <- row51]: Thus, Mazur's Conjecture B has been unequivocally solved, but the absolute Uniform Boundedness Conje

**Pythia queue id:** 298
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkN0VQYW92SkE2Q2oxTWtQc3ZLeXlBRRIXZDdFUGFvdkpBNkNqMU1rUHN2S3l5QUU
**Elapsed:** 436s
**Completed at:** 2026-05-22T01:36:43.577166+00:00

---

# Substrate-Grade Research Brief: The Absolute Uniform Boundedness Conjecture for Rational Points on Curves

**Key Points:**
*   **Consensus on Mazur's Conjecture B:** It is unequivocally resolved. The Dimitrov-Gao-Habegger (2021) theorem, further refined by Kühne, provides a uniform bound on the number of rational points on a curve of genus $g \ge 2$, scaling as $c(g, K)^{1+r}$ where $r$ is the Mordell-Weil rank of the Jacobian [cite: 1]. 
*   **The Chasm to Absolute Uniform Boundedness:** The absolute Uniform Boundedness Conjecture (UBC) posits a bound $N(K, g)$ independent of the rank $r$. Bridging the gap from Mazur's Conjecture B to the absolute UBC requires proving a universal uniform bound on the Mordell-Weil rank $r$ for all curves of a fixed genus over a fixed number field, a problem that remains notoriously open [cite: 2, 3].
*   **Explicit Bounds at Low Ranks:** Thanks to the integration of tropical geometry, Berkovich spaces, and the Chabauty-Coleman method by Katz, Rabinoff, and Zureick-Brown (2016), an explicit unconditional bound exists for curves where $r \le g - 3$. For $F = \mathbb{Q}$, this bound is precisely $84g^2 - 98g + 28$ [cite: 4, 5].
*   **Methodological Paradigm Shifts:** The exhaustion of classical Chabauty methods (which rely on primes of good reduction) has given way to Arakelov geometric approaches and non-Archimedean uniformization. These techniques circumvent traditional arithmetic bottlenecks, yet they currently halt at the barrier of rank dependency.

### Introduction to the Arithmetic Landscape
The study of rational points on algebraic curves constitutes a central pillar of Diophantine geometry. Following Faltings' landmark 1983 proof of the Mordell Conjecture—which established that any smooth, projective curve $C$ of genus $g \ge 2$ over a number field $K$ possesses only finitely many $K$-rational points—the field immediately pivoted toward quantitative and uniform refinements [cite: 2, 6]. Faltings' original method, utilizing Arakelov theory and the Tate conjecture for Abelian varieties, was inherently ineffective; it provided no explicit algorithm to bound the cardinality $\#C(K)$. 

Subsequent proofs by Vojta (using Diophantine approximation) and Bombieri (simplifying Vojta's approach) paved the way for explicit bounds, yet these bounds universally depended on the specific arithmetic properties of the curve $C$, such as its height or the primes of bad reduction (the conductor). Barry Mazur and others formulated powerful uniform conjectures predicting that the arithmetic complexity of the curve could be decoupled from the bounds on its rational points. The strongest of these, the absolute Uniform Boundedness Conjecture, claims that the number of rational points is bounded solely by the genus $g$ and the number field $K$ [cite: 6]. Mazur also formulated a weaker variant, Mazur's Conjecture B, which allows the bound to depend additionally on the Mordell-Weil rank of the curve's Jacobian. 

With the recent triumph of Dimitrov, Gao, Habegger, and Kühne, Mazur's Conjecture B has been converted into a theorem [cite: 2, 7]. However, the ultimate prize—the absolute Uniform Boundedness Conjecture—remains agonizingly out of reach due to our profound ignorance regarding the extreme behavior of Mordell-Weil ranks. This research brief structurally interrogates the frontier of this problem.

---

## 1. Brief Summary
**Query:** Status update on the Uniform Boundedness Conjecture and the specific barrier of Mordell-Weil rank boundedness, surfaced as a follow-up to a prior Gemini Deep Research report.
**Prometheus Context:** Mazur's Conjecture B is resolved via Arakelov theory and Betti map gap principles, yielding a bound $B(g)^{r+1}$; however, achieving the absolute Uniform Boundedness Conjecture remains stalled by the lack of unconditional uniform bounds on the Mordell-Weil rank $r$, an obstruction structurally tied to deep open questions in arithmetic geometry [cite: 3, 8].

---

## 2. Flagged Findings

### 2.1 The Current Consensus on Mazur's Conjecture B
The arithmetic geometry community maintains a firm consensus that Mazur's Conjecture B is formally resolved. The breakthrough was achieved in 2021 by Vesselin Dimitrov, Ziyang Gao, and Philipp Habegger, who established a bound of the form $\#C(K) \le c(g, [K:\mathbb{Q}])^{1+r}$, where $r$ is the Mordell-Weil rank of the Jacobian $J(K)$ [cite: 2, 6]. Their proof utilized a novel gap principle for the Betti coordinates of algebraic points and relied heavily on the geometric Bogomolov conjecture [cite: 1, 6]. 

Shortly thereafter, Lars Kühne (2021) deployed equidistribution techniques in families of abelian varieties to refine this result, effectively removing the dependence of the constant on the height of the curve [cite: 1, 9]. Consequently, the current state-of-the-art dictates that the number of rational points is bounded by a constant dependent *only* on the genus $g$ (and the degree of the field extension), raised to the power of the rank $r$. 

### 2.2 The Rank Boundedness Controversy
Where the consensus fractures is on the implications for the absolute Uniform Boundedness Conjecture. The assumption that the Mordell-Weil rank $r$ of a Jacobian $J(K)$ can be uniformly bounded in terms of $g$ and $K$ alone is highly controversial. 
*   For elliptic curves ($g=1$), there is a folklore conjecture (supported by various heuristics and the minimalist conjecture) that ranks might be unbounded over $\mathbb{Q}$, though empirical data shows them growing extremely slowly (the current record is $r \ge 28$).
*   For higher genus curves ($g \ge 2$), it is completely unknown if the rank of the Jacobian is bounded uniformly. Some geometric heuristics suggest that for fixed $g$, Jacobians of curves might achieve arbitrarily high ranks [cite: 2, 3]. 
*   If we suffer from **PATTERN_BASE_RATE_NEGLECT**—extrapolating the behavior of generic abelian varieties to the specific, highly constrained sub-locus of Jacobians within the Siegel modular space—we might falsely assume that Jacobians exhibit the same rank distributions as general abelian varieties. 

### 2.3 Potential Points of Failure in Unconditional Expectations
The transition from Mazur's Conjecture B to the Uniform Boundedness Conjecture conditionally relies on the Bombieri-Lang conjecture for varieties of general type (proven to imply Uniform Boundedness by Caporaso, Harris, and Mazur in 1997) [cite: 6]. If one attempts to bypass Bombieri-Lang by directly bounding the rank $r$, they run into structural roadblocks. Researchers attempting to model the distribution of these ranks frequently encounter **PATTERN_RANK_PARITY_LEAK**, where the root numbers of the associated L-functions force parity constraints on the rank, severely complicating any statistical arguments for rank boundedness across families of curves [cite: 10]. If ranks are indeed unbounded, the ambitious absolute Uniform Boundedness bound must be achieved through a completely different geometric mechanism that circumvents the Jacobian's group structure entirely.

---

## 3. Problem Statement

The precise objects and results under interrogation are defined as follows:

Let $K$ be a number field of degree $d = [K:\mathbb{Q}]$. Let $C$ be a smooth, projective, geometrically irreducible algebraic curve defined over $K$. The genus of $C$ is denoted by $g$, and we restrict to the case where $g \ge 2$. By Faltings' Theorem (the Mordell Conjecture), the set of $K$-rational points $C(K)$ is finite [cite: 6].

Let $J$ be the Jacobian variety of $C$, which is a principally polarized abelian variety of dimension $g$ over $K$. By the Mordell-Weil Theorem, the group of $K$-rational points of the Jacobian, $J(K)$, is a finitely generated abelian group [cite: 11, 12]:
\[ J(K) \cong J(K)_{\text{tors}} \oplus \mathbb{Z}^r \]
where $J(K)_{\text{tors}}$ is the finite torsion subgroup and $r = \text{rank}_{\mathbb{Z}} J(K)$ is the Mordell-Weil rank [cite: 11, 12].

**The Absolute Uniform Boundedness Conjecture (UBC):**
Does there exist a constant $N(K, g)$, depending *only* on the number field $K$ and the genus $g$, such that for every smooth algebraic curve $C/K$ of genus $g \ge 2$, 
\[ \#C(K) \le N(K, g) \text{?} \]
[cite: 6]

**Mazur's Conjecture B:**
Does there exist a constant $N(K, g, r)$, depending on $K$, $g$, and the Mordell-Weil rank $r$ of $J(K)$, such that 
\[ \#C(K) \le N(K, g, r) \text{?} \]
[cite: 6]

**The Core Interrogation:**
Given that Mazur's Conjecture B is now a proven theorem with an explicit structural dependence on $r$ (specifically, bounds scaling like $B^{r+1}$ [cite: 3, 8]), the absolute UBC holds unconditionally *if and only if* either (a) the Mordell-Weil rank $r$ is uniformly bounded for all Jacobians of genus $g$ curves over $K$, or (b) a novel proof strategy is discovered that completely divorces the cardinality of $C(K)$ from the arithmetic density of its Jacobian $J(K)$.

---

## 4. Status & Bounds

The current status of the Uniform Boundedness Conjecture is heavily stratified based on the structural properties of the curve and its Jacobian. We delineate the best current bounds across three regimes.

### 4.1 Unconditional Explicit Bounds for Low Rank ($r \le g - 3$)
When the Mordell-Weil rank is strictly constrained relative to the genus, extraordinary precision has been achieved using $p$-adic integration (the Chabauty-Coleman method). Michael Stoll (2013) first achieved this for hyperelliptic curves [cite: 5, 6]. 

In 2016, Katz, Rabinoff, and Zureick-Brown (KRZB) dramatically generalized this to *all* curves, completely bypassing the hyperelliptic restriction. 
*   **Current Best Bound:** If $C$ is a curve over $\mathbb{Q}$ of genus $g \ge 3$ and its Jacobian has rank $r \le g - 3$, then:
    \[ \#C(\mathbb{Q}) \le 84g^2 - 98g + 28 \]
    [cite: 4, 5].
*   **Methodological Significance:** This bound is completely explicit and uniform. Classical Chabauty bounds were of the form $\#C(\mathbb{Q}) \le \#C(\mathbb{F}_p) + 2g - 2$, which created a **PATTERN_CONDUCTOR_CONFOUND**. In classical Chabauty, the prime $p$ must be a prime of good reduction, which means $p$ is bounded from below by the conductor of the curve. Because the conductor can be arbitrarily large, classical Chabauty failed to provide a *uniform* bound over all curves of a given genus [cite: 13]. KRZB solved this confound by executing Chabauty's method on Berkovich analytic curves over primes of *bad* reduction, utilizing tropical geometry to bound the zeros of abelian logarithms on $p$-adic annuli [cite: 4, 5, 13].

### 4.2 Unconditional Parameterized Bounds for Arbitrary Rank (Mazur's B)
For curves with arbitrary rank $r \ge g$, Chabauty-based methods fail fundamentally because the topological closure of $J(K)$ in $J(K_v)$ is no longer proper, allowing rational points to evade $p$-adic geometric bounds [cite: 14]. Here, the community relies on the Arakelov-theoretic proofs of Mazur's Conjecture B.
*   **Current Best Bound:** Dimitrov, Gao, and Habegger (2021), combined with Kühne (2021), established that there exists a constant $c(g)$ depending only on the genus such that:
    \[ \#C(K) \le c(g, [K:\mathbb{Q}])^{1+r} \]
    [cite: 2, 15].
*   **Conditional Qualifiers:** While this bound unequivocally solves Mazur's Conjecture B, it explicitly scales exponentially with $r$ [cite: 16, 17]. Thus, it fails to resolve the absolute Uniform Boundedness Conjecture unless $\sup_{C \in \mathcal{M}_g(K)} \{ \text{rank } J_C(K) \} < \infty$. 

### 4.3 Conditional Absolute Bounds (Bombieri-Lang)
If one is willing to assume deep conjectures in higher-dimensional Diophantine geometry, the absolute Uniform Boundedness Conjecture is already a theorem.
*   **Status:** In 1997, Caporaso, Harris, and Mazur (CHM) proved that if the Bombieri-Lang Conjecture holds (which states that the set of $K$-rational points on any variety of general type over $K$ is not Zariski dense), then there exists an absolute uniform bound $N(K, g)$ bounding the rational points of all genus $g \ge 2$ curves over $K$ [cite: 6].
*   **Mechanism:** CHM considered the universal curve $\mathcal{C}_g \to \mathcal{M}_g$ over the moduli space of curves. By analyzing fibered powers $\mathcal{C}_g^n$, they showed that for $n$ sufficiently large (relative to $g$), the fibered power is a variety of general type. Bombieri-Lang then forces the rational points to lie on a proper closed subvariety, restricting the number of points any single fiber (curve) can possess.

---

## 5. Literature (Primary Sources)

The progression of this open problem is chronicled through several seminal papers. The following represent the primary literature underpinning the current state of the art:

1.  **Caporaso, L., Harris, J., & Mazur, B. (1997).** *Uniformity of rational points.* Journal of the American Mathematical Society, 10(1), 1–35.
    *   *Significance:* Established the conditional proof of the absolute Uniform Boundedness Conjecture assuming Bombieri-Lang [cite: 6].
2.  **Stoll, M. (2019 / arXiv 2013).** *Uniform bounds for the number of rational points on hyperelliptic curves of small Mordell–Weil rank.* Journal of the European Mathematical Society, 21(3), 923-956. (arXiv:1307.1773).
    *   *Significance:* First explicit uniform bounds for hyperelliptic curves with $r \le g - 3$, pioneering the use of $p$-adic annuli integration [cite: 6].
3.  **Katz, E., Rabinoff, J., & Zureick-Brown, D. (2016).** *Uniform bounds for the number of rational points on curves of small Mordell–Weil rank.* Duke Mathematical Journal, 165(16), 3189–3240. (arXiv:1504.00694).
    *   *Significance:* Extended Stoll's bounds to all non-hyperelliptic curves, establishing the definitive bound $84g^2 - 98g + 28$ for $r \le g - 3$ utilizing Berkovich spaces [cite: 4, 5].
4.  **Dimitrov, V., Gao, Z., & Habegger, P. (2021).** *Uniformity in Mordell–Lang for curves.* Annals of Mathematics, 194(1), 237-298. (arXiv:2001.10276).
    *   *Significance:* Unconditional proof of Mazur's Conjecture B for curves of large height, establishing the $c^{1+r}$ scaling bound [cite: 6, 18].
5.  **Kühne, L. (2021).** *Equidistribution in Families of Abelian Varieties and Uniformity.* arXiv:2101.10272.
    *   *Significance:* Removed the height condition from Dimitrov-Gao-Habegger using advanced equidistribution techniques, completing the unconditional proof of Mazur's Conjecture B [cite: 7, 9, 19].
6.  **Gao, Z., Ge, T., & Kühne, L. (2021).** *The Uniform Mordell-Lang Conjecture.* (Various subsequent preprints mapping the full generalization to Abelian varieties) [cite: 1, 20].

---

## 6. Attack Vectors

The landscape of techniques utilized to attack the bounds on rational points is highly dynamic. We categorize them into exhausted approaches and live techniques currently pushing the frontier.

### 6.1 Exhausted Approaches
*   **Classical Chabauty-Coleman:** Introduced in 1941 and modernized by Coleman in 1985, this method bounds points by integrating $p$-adic differentials [cite: 21]. It requires a prime $p$ of good reduction. Because finding a prime of good reduction inherently depends on the arithmetic conductor of the curve, this approach cannot yield a uniform bound across all curves of a given genus. This method is fundamentally exhausted for questions of absolute uniformity.
*   **Classical Diophantine Approximation (Vojta's original proof):** Vojta's 1991 proof of the Mordell Conjecture relied on Dyson's Lemma and Roth's Theorem [cite: 1, 22]. While it yields bounds, the constants generated via classical height inequalities depend heavily on the specific coefficients and height of the curve, making it ill-suited for uniformity without external geometric inputs (like Bogomolov bounds).

### 6.2 Live Techniques and Primitives
*   **Non-Archimedean and Tropical Geometry (Berkovich Spaces):** To bypass the conductor restriction, modern approaches analytify the curve $C$ over $\mathbb{Q}_p$ into a Berkovich space [cite: 4, 5]. The geometry of this space collapses onto a metric graph (a tropical curve) [cite: 23]. By studying the divisor theory on these metric graphs (using chip-firing and Baker's Specialization Lemma) [cite: 13], researchers can bound the zeros of abelian integrals on the "bad" annuli of the curve. This is the precise mechanism Katz, Rabinoff, and Zureick-Brown used to establish explicit uniform bounds [cite: 5, 13].
*   **Arakelov Intersection Theory and Betti Maps:** The breakthrough by Dimitrov, Gao, Habegger, and Kühne relies on height inequalities derived via Arakelov geometry [cite: 9, 22]. By mapping points to the torus $\mathbb{R}^{2g}/\mathbb{Z}^{2g}$ (Betti coordinates) and proving a new "gap principle" for these coordinates [cite: 19], they can separate rational points of large height [cite: 24]. 
*   **Equidistribution of Small Points (Szpiro-Ullmo-Zhang):** To handle points of small height, Kühne utilized equidistribution theorems for sequences of points with Néron-Tate heights tending to zero [cite: 7, 9]. By proving that such points cannot cluster inappropriately on weakly special subvarieties, one achieves uniform control over the small-height rational points [cite: 1, 25].
*   **Symmetric Power Chabauty:** A newer vector involves examining the $d$-th symmetric product of the curve $C^{(d)}$ to push the rank condition boundary. If $r \le d + g - 3$, one might use symmetric Chabauty. While theoretically promising for expanding beyond $r \le g-3$, making the bounds explicit and uniform remains a heavy combinatoric and $p$-adic analytic challenge [cite: 26, 27].

---

## 7. Cross-References

The Absolute Uniform Boundedness Conjecture does not exist in a vacuum; it is the central node in a web of deep Diophantine conjectures.

*   **The Bombieri-Lang Conjecture:** As noted, Caporaso-Harris-Mazur proved that Bombieri-Lang implies Uniform Boundedness [cite: 6]. Disproving absolute Uniform Boundedness (for instance, by constructing families of curves with unboundedly many rational points) would definitively falsify Bombieri-Lang. Conversely, assuming Bombieri-Lang provides the upper bound envelopes [cite: 2].
*   **The Uniform Manin-Mumford Conjecture:** Closely related to the study of rational points is the study of torsion points. Manin-Mumford (proved by Raynaud) states that a curve $C$ embedded in its Jacobian $J$ intersects the torsion subgroup $J_{\text{tors}}$ in finitely many points [cite: 13, 28]. The uniform version—that this intersection is bounded uniformly by $g$—was also essentially resolved by the KRZB framework for degenerate reduction, and broadly by Kühne [cite: 9, 28].
*   **The Geometric Bogomolov Conjecture:** This conjecture provides strict lower bounds on the Néron-Tate height of non-torsion points on curves [cite: 16, 24]. The explicit resolution of this in characteristic zero by Dimitrov, Gao, and Habegger provided the key height inequality required to execute the Vojta-style proof of Mazur's Conjecture B [cite: 6, 20].
*   **The Zilber-Pink Conjecture:** A vast generalization spanning both Manin-Mumford and Mordell-Lang [cite: 29]. The Katz-Rabinoff-Zureick-Brown bounds have been heavily referenced in recent attempts to tackle Zilber-Pink for products of curves with highly degenerate reduction [cite: 30].
*   **Anti-Anchors (Rank Heuristics):** When attempting to resolve the absolute UBC by establishing bounds on the Mordell-Weil rank $r$, one must navigate severe anti-anchors. For example, it is heavily debated whether $\sup_{C \in \mathcal{M}_g(K)} \text{rank}(J_C) = \infty$. Some topological heuristics suggest rank is unbounded. If this is true, then Mazur's Conjecture B (scaling as $B^{r+1}$) cannot directly yield absolute UBC. Furthermore, attempts to model the average rank of Jacobians over $K$ are frequently derailed by parity constraints in the Selmer group; this is a classic manifestation of **PATTERN_RANK_PARITY_LEAK**, where the analytic rank predicted by the sign of the functional equation of the L-function forces a rigid structure on the algebraic rank, making naive probabilistic extrapolations of rank bounds inherently flawed [cite: 3, 10].

### Conclusion
The landscape of rational points on curves is currently in a state of suspended triumph. The resolution of Mazur's Conjecture B by Dimitrov, Gao, Habegger, and Kühne [cite: 1, 2, 7, 9] represents a watershed moment in Arakelov geometry, confirming that the arithmetic complexity of a curve's rational points is bounded strictly by its genus and the rank of its Jacobian. Similarly, the explicit uniform bound of $84g^2 - 98g + 28$ by Katz, Rabinoff, and Zureick-Brown for low-rank curves demonstrates the immense power of non-Archimedean tropical methodologies [cite: 4, 5]. 

Yet, the ultimate goal—the absolute Uniform Boundedness Conjecture—remains locked behind the enigma of the Mordell-Weil rank [cite: 2, 3]. Until the distribution and maximum bounds of $r$ for higher-genus curves are understood, or until a proof strategy is devised that routes around the Jacobian entirely, the absolute Uniform Boundedness Conjecture will remain one of the most compelling open questions in mathematics.

**Sources:**
1. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7ISlqKdh4ULUT2PcQz0vpsAxO568shhfMDPTyit0G-pNcw0T1oSmJBPYNjpzMfnrxN1IUm_tGlpBwQXYGcVG1jEUgluBHsgjdDl6YMGY-CqduFvPaFZWlxfAYg8XdbixWHRLiyw6KVsj6OGtnwRQ=)
2. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNWvVPww4IsJDnJoMv8dYzwy1KYaNkHemCzjPCYzqRvDniegsIHogB1Nves50gornGvnjshXIQdhDAWN2HkEtmM5PT4BrElgGYkpWV1Vl2bWMOmrsoAP15CKExBKUryACWf3evJ6o=)
3. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiRsLg7ozbn0CniIzxRpsD7WGhoyLpLV-L9dkpAyMRJl2CGhfopRaEA9pFkAdZd-ux-zJlyfGqi9aGiA_80UfyjYZO2hEKVjmmjbP87rSDMkLkWIMsJp-EdM508C8_QpihlAoJFThMs4iyU_ldzE2eb5dwjaUG-710vDCWHnDyWH2c4V61eGXmFRGtg5X-_09Nab-zCTU_TyMfO1SgKG8EtiF4UufCMiMIG89hiBo=)
4. [tu-darmstadt.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGb0YHIlBZ8Ld-nRlwIydShanIcJ0x042t6Tb5a2eV6Ja1aGlXTuSNTV-HVMt_bFSjTHP52p9s-Ro8Y9_kTMJrHqERZMVbGENbwDvmXsTe6Mogji_MUFYqXUt3ecTb-0QyedxMkQwL5Y16Be5caWakWLGguJDECqHbmTu-Wc6Si)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCxOEpQ7NEja2uEwaTtAdqDioDdyo-kQpLmbsMYKPDAZ0kn25Aj98Htiv58uQCvPsAMuGaOPK7UwLb3pBzUuW9G7qZwdoqyiNMQr9cpMD07-d59Qa4iQ==)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPZsCWH1QAPX5RorbXSbcT_fT_tCAkHnptlNaXYz-vo2RkABmj_4bsf0wJKygH-jqAYGbDCM-dGwD12ZUuMXd7EN0D5JeUTDMWxzm4Zr5XBkFdXKHDQtrzDwEXNn0_8zyfTnO4QdPO8f3aWuonCatvKhMEUO8ECWbZ9kS4hHCZUq3Z4vcxqA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc9dd07ERdoXbh7QxG6C0etf0numbSL4IEAqUY_u8cRhxUfZi6sRmgaYg5gVp-MbwZJj2hd1ngwb_cv5Wj-jZDn9ZHkeJIYOqgnKBuS6VeirICxHmxAg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFl61jFT-Gr7L-11Cs2JKynP0vbzTPQZhLPFu1t0GdEbaNGQC6XnX3HJgUzKrTVwTZvrr2tJKcu547g-0VslDsfoPFan6HRgPjwiqhLD5o6wHxGNi6Okg==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6StVl0eeND_ceKgcaf5OKjmRrMn-Azq0ZmuCI-B5i8AmNc_b4pA2yCvK-FvQhqe5MC2MVh7pPaztuOWNafCrBaLEXPsaR8MPlYAHyKD_Lq7IbYun-Dw==)
10. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeoBdGAwK5xFDfI9IBve1Z17OY9eJJ_gYPRcXenS3F3cEFkwP8ZD40n2kFTy_7oPd1sQw17yxdJJRVKP11jxIdMOh9QsLVV1g_SMxVPs81XaFffFrZvbik2cKyki38EIu-qUaEy0n4FnRAK31ChSCTMD9R7-iSv5WTbxxEhYc6YaH94Kv1rH8G1WCMAxBtUJrbnETvGzLOVpw=)
11. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqP9W4z-KlXRpiDfE5rVGQTfcCRXbS1VwQoXlDToc7PoMbXMi_ibNl1Z8PwA6Epvw3p-bp4_ivmKdgRpZcROBvgcP1yGjV4xe1oMKo2bEH5EquTzWfnl8nGqMpmrwVYlH1fDt3eD1LQqd4-fTl529gvA==)
12. [csusb.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzF-wRYn6vo_N5FFRM9EvFEgPSYeq4OtYUvkGocQZaqhIzILE_FaN-mD4MWvq6DSu6cD5t46EBvUcENd4oh813U6WdrmFbj5cZGS8t7FhONcmvW1nwGZPal_RJ3ym45W_QOzFl4ZEFz-Lxb7mrzK47HxQzvWX9364zG3sEX45IdMMH5puB50hlup3IvBI=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEGgm4r0563jhPEf3XUejU2QimC7bKHL1c9-7Q_Unf4oQPzLe1hRl1rXyUQBgrToskPG2cK54smhJJBYFvRCUX3pj0sJMICGkJrjC8yIUBGwZYXsQwHg==)
14. [bu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMQb8l2rEhmcLY0xww8hWw3r-rCBCwg65Yn6ep9HzPrE5E8xtsLkfYMZj8srK_HkmrxTaednXLomdeWt-oSHBj83INxniv0OxlYYt4OO4Cy4dlEgM1tcPmeYzhHGy9HzM8q7_Gy_E=)
15. [iec.cat](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHil_QebtXNl22uZfOvBK0EGdqlNfFHlQ6Jnb76s2Bk9zIpzniza0OmlNS2g8tC81ABGJ4s2wE9X8uloxk7ooSp99II9JZOVbOf3snxN1n-N71o-uw9NC_zqt8TBkOtbB9sP9ADUGZAucerjkSEwgF2TgkDdNkXJg==)
16. [yale.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnUQ8OILMQFYq8LCqYgbZxoiHSuEr6u6U40DdH6VVqII-DxZH9-3qsCn1XNXrLZn3tC2m7WRRWYWQPxwOSqutXcTdXDM4KZNVmWvV2jvlX3G8LiUmAMBH0LHq0nLCTxndApzUP0kAq5Hyp9UZRuwlHbrh2Pt13M-1unfzqUWa8j-dMHjmXuLsB1DSh5vJR-pyeAEpEDOmnX4ohEoRAnwowDwxztXPcKA==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYcPbSI9HPhNrhHvG0Hv8IeLc6c4qNxltEqz1UDvm-MNd2CaaVu1z-J3SUwRMauy_37wIin3u2_cTEDTjtaebPuh60NmCFHvtnfHA2raKXk2IoULUhRq8A9GttnDCoSOxobbGduY7DYXlUzARKX3zhn_v2vP8BdG2pO-a1CtRgMGz1hBcqPcw-KOXYbpiCbKTtmZa-dxfeFkrft4Deft_JH2dw_jRGUD5wkMBIMBuqZXe9)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7IqJprzOFMSmglovSeUh6YqmqcI9mTgMMzBdVNB1sreV-lBnMosaAqHLoQaByfXE4EYAyPiA_3zL-P7uxiNG-MmCOKYzcPoReWiN_gdG3_iHzr4FJKA==)
19. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGi_0Md2JEddJfSaaVJCaEHghwuJzLi4jdbzj469eB8fDJ8yZ95_XiKMB8dlQGEs314INgaItnlE6dX_6fBdn1CshCp0hF9ezyk-bT5U7FIusn1V2Z3KJ2Q5yzzk6j3mVNrlDq5ew3VEuD-3nwf)
20. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8EcVgLfWl4dg-7xGxowg5zEVVCa64-q-yUFHgHK9aq2kGeul4R1VtS7Uk0pf3ptErfhD9670LmDk8goz5v0E-G5EYx9YPAdbO1vYtSD6DRK2A6dxTakmNytc3N_1kZ4oKSbyvKFPSQg==)
21. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj7MdIA-MyuLBZ9TLFovIcj2OF2qFS03t_z5QFHM_aMSpYbOLaMAHLUP22Ul3M83qWY-N2r8idiuMGTEu7AMcvkx9pAf6dHPdax7LddPYn16ch-_rwtA8izXIfkX-PepbRQErLN3oBIu-jGl6OI-O0phDP5mY5lYN_rsQ=)
22. [pku.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGATW4YpGOpZGxyDbkx7VRcw48-KZBq-LYbYOtMKq471axGqHFKK0d-fAiKVrEW38t4yvBkWRLVBBUaI0dw6GPERvQVOpZ6U7wUKEnV_nfQQbPxA7uqURH1uBkcWG7XtTH1Ke7VxhZl0b-mLd6d8RLDTk6IkezhrA8hWEAcXA==)
23. [uky.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEFO0h40KAckJElTrjMbMv1cbs81v14AJ7uUWjKNxe0RjSBVdDdXhjRD9uEkkAUAtdin4n0cCml2blJ8-TAPS5FoAztNEtvNya_cbsx4Jj4Q79Qiz8P7xInTW9w6dFgHeoPhfY8YRDomVAQy01Jsnfd__V)
24. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo3QLlxJVa2V2_QXZnkHQqjr-5PSpnAFBJG9Fyjml1UnbmY0X3xWcSiqlP90DV3mbbJJIlYlq0VRhT8FZYGYa4TA99-T7ZHdKTTGCUw9C-zJGou8acy-3GsY72dkIhOfjp9cCvXTid7FuGvY0LL-YeZkOZu5mrrg==)
25. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJrqIiJD9vetN2HorRYzmhgq0wiA-_egAtnneHhLZuP6soeihQNwYZJSSai-p2jELujPEcOH4JpcEx7kn14tMZ7spLG5YIuT1sfETL0-43a4MMUzxwdJdX2KD2Na242i4OmZA1ROfektIEIp4cE5e3N6_4ry37cJueJA==)
26. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0MAh5lL9A2cE1UGvTF_n7UZ6s6M4PWBKmUvWC4u_qS3HxSNEajXG0NJTBkxbdzWKEXTZAED4yVWA0Wuv09kXOiKK3zAP8fi3T4-lNiYe39pMW3YeNAbXq9RCmDlt4_0yL-cyzOJlKQPtuLcASzPQlP9lwQ4qzO2WyJA==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFnKw2slsw38ohRXZsOjYO9pz-2hdvKWQ1J-KIseepLBScPr8aRUAN7xo97GscrtAd262X9z4NforzOkvwkfEnYJnY5Flf5N6QUki1IeGuTcz-MbOSCDvp6TLDxmXddFEMSCb_oStPuizlOhs3Jq6VMO32wMJ7BH1g_KqL1YogCA8yxGW1z3fmmDp48JWNd3Wj0SJArAHHzAWt)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXk6fzoH_Q27gIZ5lqtEqgdJmsmZ67ty8xd-LnjXwv18v-ZcB88_bA2FhmExM73MlOU452kprN4GIqL1f8IgeZ7e1G4NXvaDKcZrEZreNOUC0FFLTA-w==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4KGECX8Og7lK4pKGAFSyhB2K-h-GUlnOlaSeeBC8Izewa5ZkEBsyT82IOudrv3Z2K6Oe3AyyVUEWrYpaAvqGiyKsBqCx0t5ouEzgRSWGLXFzoce3G)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHN2tmevI1oCHtk7hQtfdSU4vj0m675ZPhyogMU2QgsRT1PQxbmhSc54E-cMugnRxXyyFnFY2qlGimzhVGN7yh4mW5EZzifQ1mHHrhQ_vbEhvKwR9X3mQ==)


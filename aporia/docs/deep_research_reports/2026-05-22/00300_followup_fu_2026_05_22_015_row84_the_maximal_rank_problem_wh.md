# Followup [FU-2026-05-22-015 <- row84]: *   **The Maximal Rank Problem**: While the generic rank is well understood, determining the *maxima

**Pythia queue id:** 300
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdjTElQYXRMaEp2WFVqTWNQa0xxRXdBaxIXY0xJUGF0TGhKdlhVak1jUGtMcUV3QWs
**Elapsed:** 250s
**Completed at:** 2026-05-22T01:37:47.481623+00:00

---

# Substrate-Grade Research Brief: The Maximal Waring Rank Problem

**Key Points**
*   Research suggests that while the generic Waring rank of homogeneous polynomials is comprehensively determined by the Alexander-Hirschowitz theorem, the maximal Waring rank for complex forms remains largely unsolved.
*   The foremost general upper bound is the Blekherman-Teitler bound, which asserts that the maximal rank is at most twice the generic rank (\(r_{max} \le 2r_{gen}\)).
*   It seems likely that this bound is asymptotically loose for higher dimensions, as alternative combinatorial bounds by Jelisiejew provide strictly better asymptotic limits, though they are weaker for low degrees.
*   The exact maximal Waring rank is only known in a handful of special cases: binary forms, quadrics, and ternary/quaternary forms of very low degrees (e.g., ternary cubics, quartics, and quintics).
*   Recent breakthroughs in theoretical computer science have yielded "debordering" bounds that constrain the Waring rank of a polynomial exponentially in terms of its border Waring rank, but crucially, only linearly in its degree.

**Overview**
The decomposition of multilinear and polynomial objects into sums of simpler, rank-one components is a foundational problem intersecting algebraic geometry, representation theory, and theoretical computer science. For symmetric tensors—or equivalently, homogeneous polynomials—this is known as the Waring problem for polynomials. While it is well understood that a "general" or "random" polynomial of a specific degree and dimension possesses a predictable generic rank, the absolute worst-case scenario—the maximal Waring rank—remains a profound mystery. This briefing synthesizes the current consensus, computational limits, and theoretical bounds surrounding the Maximal Waring Rank Problem, with particular attention paid to the widely cited Blekherman-Teitler bound and competing asymptotic frameworks. The evidence leans toward the conclusion that while general bounds exist, the precise stratification of high-rank loci is computationally intractable with current geometric techniques.

***

## 1. Brief Summary

**Query Context:** A formal inquiry regarding the status, consensus bounds, and live attack vectors for the Maximal Rank Problem of symmetric tensors, specifically interrogating the limits and applications of the Blekherman-Teitler bound (\(r_{max} \le 2r_{gen}\)) as extracted by Aporia via Prometheus pattern matching from prior Deep Research reports.

## 2. Flagged Findings

The current consensus in algebraic geometry and invariant theory establishes a definitive ceiling on the maximal Waring rank via two competing generalized bounds: the geometric Blekherman-Teitler bound and the combinatorial Jelisiejew bound. 

**The Blekherman-Teitler Consensus:** 
The prevailing state-of-the-art for the maximal Waring rank relies on the Blekherman-Teitler bound, which dictates that for any projective variety (including the Veronese variety corresponding to symmetric tensors), the maximal rank is at most twice the generic rank, \(r_{max} \le 2r_{gen}\) [cite: 1, 2]. This bound is elegantly derived from the topological properties of secant varieties and applies universally across complex and real fields [cite: 1]. For real numbers, the bound takes the form of being twice the *smallest typical rank*, which coincides with the complex generic rank [cite: 1]. 

**Where the Consensus Might Be Flawed or Loose:**
Despite its universality, evidence strongly leans toward the Blekherman-Teitler bound being highly pessimistic and asymptotically crude for forms in many variables. 
1.  **Asymptotic Weakness:** Asymptotically, Jelisiejew’s upper bound (\(\frac{n^d}{n+d-1}\) times the generic rank) outperforms the Blekherman-Teitler bound [cite: 2]. Jelisiejew proved that the maximal rank is bounded by \(\binom{n+d-2}{d-1} - \binom{n+d-6}{d-3}\) for \(n, d \ge 3\) [cite: 3, 4]. While Blekherman-Teitler is sharper for low dimensions/degrees, Jelisiejew's bound indicates that the geometry of the maximal rank loci scales much slower than \(2r_{gen}\) as dimension increases [cite: 2].
2.  **Parity and Degeneracy Artifacts:** The maximal rank bound exhibits PATTERN_RANK_PARITY_LEAK; specifically, the \((r_{gen}-1)\)-th secant variety of the underlying rational normal curve behaves divergently depending on whether the degree \(d\) is even or odd [cite: 1, 2]. For instance, if \(d\) is even, the secant variety is a hypersurface defined by the vanishing determinant of the middle catalecticant matrix, tightening the maximal rank to \(2r_{gen} - 2\) instead of \(2r_{gen}\) [cite: 1, 2].
3.  **Base Rate Anchoring:** Researchers often exhibit PATTERN_BASE_RATE_NEGLECT by over-indexing on the readily accessible monomial examples (which can exhibit ranks strictly greater than generic in 3 variables) while underestimating the volume of the unstructured "forbidden locus" that inherently governs the geometry of higher rank loci [cite: 5, 6]. Monomials in 4 or more variables invariably possess a rank *strictly less* than the generic rank, indicating that they are poor proxies for maximum rank behavior in higher dimensions [cite: 5].

## 3. Problem Statement

The object being interrogated is the **Waring rank** (or symmetric tensor rank) of a homogeneous polynomial, and specifically, the supremal value this rank can take over the entire space of polynomials of a fixed degree and dimension.

Let \( S = \mathbb{C}[x_0, \dots, x_n] \) be the standard graded polynomial ring over the complex numbers, and let \( S_d \) denote the vector space of homogeneous polynomials (forms) of degree \( d \). The dimension of this space is \( \binom{n+d}{n} \) [cite: 2].

**Waring Decomposition and Rank:**
A Waring decomposition of a form \( F \in S_d \) is an expression of \( F \) as a linear combination of \( d \)-th powers of linear forms:
\[ F = \sum_{i=1}^r c_i L_i^d \]
where \( L_i \in S_1 \) and \( c_i \in \mathbb{C} \) [cite: 1]. The **Waring rank** (or symmetric tensor rank), denoted \( r(F) \), is the minimum integer \( r \) such that such a decomposition exists [cite: 1]. Geometrically, this corresponds to the rank of \( F \) with respect to the \( d \)-th Veronese embedding \( \nu_d(\mathbb{P}^n) \) of the projective space into \( \mathbb{P}^{\binom{n+d}{d}-1} \) [cite: 1, 7].

**Generic Rank vs. Maximal Rank:**
*   **Generic Rank (\(r_{gen}\)):** The rank of a "general" form in \( S_d \). The set of forms in \( S_d \) with rank \( r_{gen} \) contains a Zariski open and dense subset of \( S_d \) [cite: 2, 8].
*   **Maximal Rank (\(r_{max}\)):** The maximum Waring rank taken over *all* possible forms in \( S_d \). This is the absolute worst-case decomposition length [cite: 8].

**Secant Varieties and High Rank Loci:**
The geometric formulation translates the problem to secant varieties. The \( r \)-th secant variety \( \sigma_r(X) \) of a variety \( X \) (here, the Veronese variety) is the Zariski closure of the set of points of rank at most \( r \) [cite: 1]. The generic rank is the smallest \( r \) such that \( \sigma_r(X) = \mathbb{P}^N \). However, because \( \sigma_r(X) \) is a Zariski closure, there are polynomials in the boundary that can have a Waring rank strictly greater than \( r \). Understanding the maximum value of the rank within these boundaries (the high rank loci, denoted \( W_k \) for \( k > r_{gen} \)) is the core of the Maximal Rank Problem [cite: 9].

## 4. Status & Bounds

The generic rank is fully classified, but the maximal rank is known only in a tiny fraction of cases. Below is the exhaustive status of the problem, mapping out the known exact values, best general bounds, and conditional qualifiers.

### 4.1 The Alexander-Hirschowitz Theorem (Generic Rank)
The generic rank \( r_{gen}(n, d) \) was completely determined by the celebrated Alexander-Hirschowitz Theorem (1995) [cite: 2, 10]. The expected generic rank is the dimension of the ambient space divided by the dimension of the affine cone over the Veronese variety:
\[ \text{Expected } r_{gen} = \left\lceil \frac{1}{n+1} \binom{n+d}{n} \right\rceil \]
The theorem states that the true generic rank coincides with this expected value for all \( (n, d) \), with exactly five families of exceptions where the true rank is the expected value plus one [cite: 10, 11]:
1.  Quadrics in all dimensions (\(d=2\)), where \(r_{gen} = n+1\) [cite: 10].
2.  \((n, d) = (2, 4)\): Ternary quartics, expected 5, actual 6 [cite: 2, 11]. (Note: Source uses projective dim \(n\), where \(n=2\) means 3 variables).
3.  \((n, d) = (3, 4)\): Quaternary quartics, expected 9, actual 10 [cite: 2, 11].
4.  \((n, d) = (4, 3)\): Quinary cubics, expected 7, actual 8 [cite: 2, 11].
5.  \((n, d) = (4, 4)\): Quinary quartics, expected 14, actual 15 [cite: 2, 11].

### 4.2 Exact Known Values for Maximal Rank
The exact maximal Waring rank, \( r_{max} \), is known only in the following heavily restricted cases [cite: 2, 8]:
*   **Binary Forms (\(n=1\), 2 variables):** \( r_{max}(1, d) = d \). Known classically to Sylvester [cite: 1, 10]. The maximum rank is achieved precisely by polynomials of the form \( L_1 L_2^{d-1} \) where \( L_1, L_2 \) are linearly independent [cite: 10].
*   **Quadrics (\(d=2\)):** \( r_{max}(n, 2) = n+1 \) (by classical diagonalization of symmetric matrices) [cite: 1].
*   **Ternary Cubics (\(n=2, d=3\)):** \( r_{max} = 5 \) (Generic rank is 4). Known classically, rigorous modern proof by Landsberg and Teitler [cite: 2, 8].
*   **Ternary Quartics (\(n=2, d=4\)):** \( r_{max} = 7 \) (Generic rank is 6). Settled by Kleppe (1999), De Paris (2013) [cite: 2, 8, 12].
*   **Ternary Quintics (\(n=2, d=5\)):** \( r_{max} = 10 \) (Generic rank is 7). Settled by De Paris (2015) leveraging lower bounds by Buczynski and Teitler [cite: 8, 12].
*   **Quaternary Cubics (\(n=3, d=3\)):** \( r_{max} = 7 \) (Generic rank is 5). Settled by Segre (1942) [cite: 8, 12].

### 4.3 General Upper Bounds
When exact values are unknown, the community relies on the following upper bounds:

**1. The Blekherman-Teitler Bound (2015):**
The most widely applicable bound, stating that for any irreducible projective variety \(X\), the maximal rank with respect to \(X\) satisfies:
\[ r_{max} \le 2 r_{gen} \]
*Proof Sketch:* The proof relies on taking a small open ball \( B \subset \mathbb{R}^{N} \) in which every point has the generic rank \( r_{gen} \). The difference \( B - B \) forms an open neighborhood of the origin. Any point \( p \) in the ambient space has a scalar multiple in \( B - B \), meaning it can be written as the difference (or sum) of two points, each of rank \( r_{gen} \). Thus, \( r(p) \le 2 r_{gen} \) [cite: 1, 2].
*Refinements:* If the \((r_{gen}-1)\)-th secant variety is a hypersurface, this bound is improved to \( 2r_{gen} - 2 \) [cite: 1, 2].

**2. The Jelisiejew Bound (2014):**
Joachim Jelisiejew derived an algebraic upper bound that improves upon the naive basis bounds. He proved that for \( n, d \ge 3 \):
\[ r_{max}(n, d) \le \binom{n+d-2}{d-1} - \binom{n+d-6}{d-3} \]
This bounds the "open Waring rank" and significantly improves the classical upper bounds asymptotically, although the Blekherman-Teitler bound is sharper for small \( d \) and \( n \) [cite: 2, 3, 4].

### 4.4 Debordering Bounds (Border Rank to Waring Rank)
A crucial sub-problem involves the relationship between Waring rank and **border Waring rank** (\(\underline{WR}(f)\)), the latter being the minimum \( r \) such that \( f \) can be approximated arbitrarily closely by polynomials of rank \( r \) [cite: 7, 13]. For example, the monomial \( x^{d-1}y \) has Waring rank \( d \), but border rank 2, as seen via the limit:
\[ x^{d-1}y = \lim_{\epsilon \to 0} \frac{1}{d\epsilon} \left( (x + \epsilon y)^d - x^d \right) \]
[cite: 13, 14].

Recent algorithmic breakthroughs have established "fixed-parameter debordering" bounds. If a polynomial of degree \( d \) has border Waring rank \( r \), the actual Waring rank is bounded by:
\[ WR(f) \le 2d \left\lceil \frac{1}{r} \binom{2r-2}{r-1} \right\rceil \]
This is a momentous result because the upper bound is *exponential in the border rank* \(r\), but *strictly linear in the degree* \(d\). Previous bounds were exponential in \( d \) [cite: 13, 15]. For polynomials with a constant border rank, this yields a Waring rank bounded linearly by degree, which was previously only known for border ranks up to 5 [cite: 13].

## 5. Literature (Primary Sources)

The following constitute the primary foundational texts and breakthrough papers defining the current status of the Maximal Waring Rank Problem.

1.  **Blekherman, G., & Teitler, Z. (2015).** *On maximum, typical and generic ranks.* Mathematische Annalen, 362(3-4), 1021-1031. **arXiv:1402.2371**. 
    *Significance:* Establishes the \( r_{max} \le 2r_{gen} \) bound. Proves the relation between real maximal rank and complex generic rank [cite: 1, 16, 17].
2.  **Jelisiejew, J. (2014).** *An upper bound for the Waring rank of a form.* Archiv der Mathematik, 102(4), 329-336. **arXiv:1305.6957 [math.AC]**. 
    *Significance:* Provides the best known asymptotic algebraic upper bound for classical and open Waring ranks [cite: 3, 4, 18].
3.  **Alexander, J., & Hirschowitz, A. (1995).** *Polynomial interpolation in several variables.* Journal of Algebraic Geometry, 4(2), 201-222.
    *Significance:* Fully resolves the generic Waring rank problem [cite: 10, 18].
4.  **Buczynski, J., Han, K., Mella, M., & Teitler, Z. (2018).** *On the locus of points of high rank.* European Journal of Mathematics, 4(1), 113-136. **arXiv:1703.02829**.
    *Significance:* Details the stratification of high rank loci \( W_k \) and proves strict containment theorems for dimensions of loci exceeding the generic rank [cite: 9].
5.  **Dörfler, J., et al. (2024/2025).** *Debordering the border Waring rank.* 41st International Symposium on Theoretical Aspects of Computer Science (STACS 2024). **arXiv:2401.07631**.
    *Significance:* Derives the fixed-parameter debordering bounds, establishing \( WR(f) \le O(d \cdot \text{exp}(r)) \), replacing prior bounds exponential in \( d \) [cite: 13, 14].
6.  **De Paris, A. (2015).** *Every ternary quintic is a sum of ten fifth powers.* International Journal of Algebra and Computation. 
    *Significance:* Establishes that the maximum rank of ternary quintics is precisely 10 [cite: 8, 12].

## 6. Attack Vectors

Determining minimal Waring decompositions and upper-bounding maximal ranks utilizes a heavily geometric and algebraic toolkit. Several strategies are live, while others have been functionally exhausted.

### Live Techniques

**1. The Apolarity Lemma & Catalecticant Matrices:**
The fundamental workhorse for computing Waring rank is the Apolarity Lemma. The polynomial ring \( S = \mathbb{C}[x_0, \dots, x_n] \) is acted upon by the dual ring of differential operators \( T = \mathbb{C}[\partial_0, \dots, \partial_n] \). For a form \( F \), its annihilator ideal \( F^\perp = \{ \partial \in T \mid \partial \circ F = 0 \} \) dictates its Waring decompositions [cite: 7, 19]. The Apolarity Lemma states that \( F \) has a Waring decomposition consisting of a set of points \( X = \{[L_1], \dots, [L_r]\} \) if and only if the ideal of the points \( I(X) \) is contained in \( F^\perp \) [cite: 7, 19]. 

To extract \( F^\perp \), researchers construct *catalecticant matrices* \( C_{F, k} \), which map \( T_k \to S_{d-k} \). The rank of these matrices provides immediate lower bounds on the Waring rank, and the kernel of the catalecticant matrix generates elements of the apolar ideal. Searching for a minimal apolar ideal of points is the primary live method for exact rank computation [cite: 6].

**2. Border Apolarity and Degeneration:**
To compute border Waring ranks, researchers have developed "border apolarity," an elementary analogue to the classical lemma. Border apolarity characterizes border rank by checking if \( f \) is apolar to an ideal \( I \) that is a *limit* of ideals of \( r \) points in the multigraded Hilbert scheme [cite: 20, 21]. This is critical for finding tensors with high "value" (degenerations to matrix multiplication tensors) used in Strassen's laser method [cite: 21].

**3. Waring Loci Stratification:**
Rather than computing the rank of specific forms, researchers study the "Waring locus"—the span of all linear forms that appear in *some* minimal Waring decomposition of \( F \). By analyzing the "forbidden locus" (linear forms that cannot reduce the rank of \( F \)), algebraic geometers iteratively reduce the rank of a form by projecting away from points in the Waring locus [cite: 6].

### Exhausted Approaches

**1. Naive Basis Bounds:**
Early attempts to upper-bound the maximal rank relied on taking trivial bases of the space of homogeneous polynomials, giving a rank bound of \( \binom{n+d-1}{n-1} \) (the dimension of the space of forms). Refinements subtracting \( n-1 \) or similar constants were quickly exhausted and thoroughly superseded by the Blekherman-Teitler and Jelisiejew bounds [cite: 2].

**2. Monomial Anchoring:**
For years, researchers sought high-rank counterexamples by computing the rank of monomials. While the Waring rank of a monomial \( M = x_0^{a_0} \dots x_n^{a_n} \) is well-understood (e.g., \( r(M) = \prod_{i=1}^n (a_i + 1) \) under certain sorting assumptions), this vector is exhausted. Theorem 1 of Carlini et al. proved that *all* monomials in \( \ge 4 \) variables have a Waring rank *strictly less* than the generic rank [cite: 5]. Therefore, searching the space of monomials for maximal rank candidates in higher dimensions is a demonstrably dead end.

## 7. Cross-References

The Maximal Waring Rank Problem does not exist in isolation. It is inextricably linked to several parallel parameters and candidate primitives.

**1. The Real Waring Rank and Typical Ranks:**
Over the complex numbers \( \mathbb{C} \), the generic rank is unique because the field is algebraically closed. Over the real numbers \( \mathbb{R} \), a parameter space can have multiple full-dimensional open semi-algebraic subsets, each with a different rank. These are called **typical ranks** [cite: 1, 22]. The minimal typical rank over \( \mathbb{R} \) is exactly the complex generic rank [cite: 22]. The maximal real rank is bounded by twice the minimal typical rank [cite: 1]. Understanding the geometry of the boundaries between real typical rank strata is a major open problem [cite: 22].

**2. Cactus Rank and Smoothable Rank:**
When searching for an apolar ideal \( I \subset F^\perp \), the Apolarity Lemma requires \( I \) to be a radical ideal of points. If we relax this condition and allow \( I \) to be any saturated zero-dimensional ideal (meaning it defines a scheme of finite length, possibly with nilpotents), the minimal length of such a scheme is called the **Cactus Rank** \( CR(f) \) [cite: 15]. If we require the scheme to be a flat limit of distinct points, this defines the **Smoothable Rank** \( SR(f) \). The Cactus rank is easier to compute (often via matrix ranks) and serves as a powerful lower bound for both the Waring rank and border Waring rank [cite: 15].

**3. The k-Rank of Forms:**
A generalization of the Waring problem proposed by Fröberg, Ottaviani, and Shapiro asks for decompositions of a form of degree \( kd \) into sums of \( k \)-th powers of forms of degree \( d \) [cite: 10]. The maximum \( k \)-rank is a deep open question. A prominent conjecture posits that for binary forms (\(n=1\)), the maximal \( k \)-rank of forms of degree \( kd \) is exactly \( k \) [cite: 8, 10, 11]. This has been verified only for small values like binary sextics (\(d=2, k=3\), max rank 3) and binary octics (\(d=2, k=4\), max rank 4) [cite: 11].

**4. Matrix Multiplication Complexity (Theoretical CS):**
In theoretical computer science, determining the Waring rank of specific polynomials (like the Determinant or Permanent) or symmetric variants of the Matrix Multiplication Tensor lies at the heart of the Geometric Complexity Theory (GCT) program [cite: 15]. Finding exact bounds on border Waring rank is critical for algorithms applying Strassen’s laser method to upper-bound \( \omega \), the exponent of matrix multiplication [cite: 21]. Exponential debordering parameters define the viability of translating border-rank algebraic circuits into exact Waring decompositions [cite: 13].

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQddZDIFR55wrvvJa8SN3xcRmmtQZtw81b7hrn6UeRksdeVGNBJ8FOPRBBXABzTik14DfvuP4M48k-DYbqpr3IJCH_XW9GhiuXVovnDq5pLANNGBWz7Uol84G0V6KIw6Br2ERumPwksq4sClwIu0cwRgZIyzPTSGF0qjXfMZ0pK4yczQVtXxpzncuBwag=)
2. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcLjjv0qhpa-LAK2CcMANHNEDQqNA9kRL2RdgdGzLyf8ozjyUfP5F5pyUiAswBzlWLyyDCILwwEF5f4jj9Rw5gQwitOSkDl-bjjzxhRyQ6J18gQBnhJSUZRC36ekSXw9SYUsEPLZEFQvx7wbxPS1spyjOJ3lcnqUCi910=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_D_Hgy8PL9LM2C00rYfq1qQNvpCfSPdm20V0Eqw1MB3XTyDh3_6lMUyPv6jT7xUmKSiNL-Nn6wI9uJwVQpMED1SE6GGSMenZmxy_cCJRVw7H413UA)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwyabXYtVG7OPXpJFkkOug625tQ9982ZpGSfnG_vCq-KxAhIU-bko16omnazUUuAGOUQx9rsJlGp_ALT5PaX_7YSufld7JtpUwlvq8xv86PMiWn0_M)
5. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1zBrzjGFajsseBWnlgFPLyFdKItAqBZyVgMd1d6mRJ5w_2kNVADxGxEy2it3nZUPYIrdAnHQ_Ep1lnpPxfnhCV1XQ6u7LpuCRbdkn9vLx2eTMjTrPAtlVmCGZx64sSKRHXtRqMP8F_rhfqt75q6YtSg==)
6. [unitn.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkagP69xHz9KVyogJLLB8aH19Q8NegZ25AKD0dRq63Z377DpbtFyZmsxixo6BWghI5PDbY_UhOt_VSukpbVCrxxPV_edEzg_FWSYuVBZGBB18eo3hw6hg8kwkdm9w7zwk4HzcgsE3oYtTx21h67-Tn-bDZqFdNdA5CLEkii3Hlj4qd0yjfoA==)
7. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEccLR94pxHNRpZQOTx5fM-xA2aNLpo7TtGDtLwB3TCH3hvS5eXzEBFYEBZhqW45JDfALBv801w8Db9Ayz19GchWQrtbB2cqopqbDNSUDnWdnehBsrpQB8jh9TnMj_eAw4a1fyfBeVzQIPntuId3CB1hAcBZEJwFE9RbSsY55smqWaUGgsGrCqF32VIHXZCvk2PJ7w8_w==)
8. [stonybrook.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHnD0fMmf5J_cnnt2vZaXjJx7gSKkpwanVjdb_GpRnT5bXQWXeKCRuoHLkboz4z_XVNs7jn-_Dffsr98deJOh4P6e7hGqP_lMUIXEXeMuXroS4l6yFiBScR_49fOrbp_9ZfPh8QyjQqSn8e0E7LLrRN0kUAJNZ)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4nnNe9F1LF678EXKNmaqq6q17yT4cgU7x0A0kbuCsd_tDvtrIF8AaaHxGHKSd6jvLRlfnWF87lz_XWNa0W7zFnCk9RpZQF1TzvhZqpE8mLKFHCafSCg==)
10. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyWRdK2-Mw_lF8KexwTx77ubLLbBZ03Rzw5qvEcp1_jN6nktHzxfmTWJOVdIZPbvIqbp3jBTtFR09rExvsaJhvPuT3GbQU1pdjCvrs1j8Hv8SLK5m2HNOV0bvp9-UVG3a0doP9yDnrzDkXgU00dDyU5u98zsJW4W3nkPI=)
11. [su.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDejLgy_kb46lycrlww-duJ-JQcTyiF0clpRlrI60cMoHcpoxqVtVUjjtq1vL4nYTItS1juIesTPdvrmS7RfjKTlr09ZG7lt4HZENeN7bFl240P0R1LCp41MMlv-CAoCgUkbAIShhkYgcanzadfAgq37vtvqQ=)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8exVJfl4BqHzjSTKqbBC06Sz_9iwyXGsOBpSUnvv3PrUumZ-N0R6myckbPofzivozYgrM54zURmdKo-u14yCfp5jK9Xfru2iXvq0M_klc9ectsQo2vZwazg14FHT2_-8IddHl_sGWrFjT7eC6HXyag20XutyvBe0O6YcBRcEntUkdmH2cmbRbxAkeIxvrRSATDtNtBkWOk_lfLg==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5y3h4SAs-sWSW6tCvGkB6Dez3nUJz3JDrfSAcHeI3CoZprGb8A9eI3awv9Wql9YiIQivc_ClEnSx4ICJsPtnFeh4KpgG-cqBNqNvbR7O1b_TKtWlINA==)
14. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGIHmN1wybahH6nv5tesjUzlXLVaC_ihGPFRJJtvU6CH8xa3ODKQz59eztAW4zb9STYCQUfemUw8vHJimim1h4vTBGsH98eiROfGyTeyyTda4bGnE2tWVE-YyDWWd7p3Kj5Ueew0YVYjRT3OuNGKr7plvIiS0UVyvB9-o6u-t08eIa4-PQqrtkih2Q3DlMTud-ibi2e8Uoc5H7D02DKAUgWDy4vL0g)
15. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsVbgDdBTbPiuiTj72nB6ZG59msUJ6_yOgMx6bJUlXcaFM34ZSOZ1A7knEv2eKl5Bs55iKfG11yOpFrZhj9xB8dzbs7a29PBsPgDRxR605EwwiIgTKEYvnHFHfZdnLaYINPrfpyHwE35xS)
16. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHbiYb7DDTDtgVaDLTY1dNQsgKaxYJMeHjKJmXU5etp0FNSa8_G3FyYhWZaVWeaOkKJzLRs9vSmZgT-CoBTTp6ObDW8HAAhP-_SCNf5ngBjv3-ZrU1POXdwE09)
17. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-pGFRtkzNPS7wKeYWDAhhnFO21GMG36_ESUpb2tqeZx_oXuX0sq6Nyr31R2FXEW-wTybaSHhVIkmL__jzBExnG_Xpvd-RLLj1n1fvL01TRuqqzbS-Zy1DcxHcUruDwOt_672BRzyiQ_p-XjUuCxnmamz8_8p7Wy1hq0WTirc0FRo4t69i37TeW5Mt6zIX7E95lG3PuxJI_urX1OP5fjT7JUE8Zddxfka-3KdzBtbRkSztju6aBOiCPI_JUUyEg9Y=)
18. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8aaZ2x2KWoMa9EEYUWqU2Ywpi98Gdkw7rsuwjDzBTtCihvi0F9ueLONkuG078UHfnihmWF8oXb8vTKxso9KHs2U3g3l2e8rIT3nm4UX1ABP-4YOZ8-b9q0aVoCT8pSSWj7PW0SAFSI6eXuJHs15vtGYgysr8Zfl37lNGIYF4=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWlvUwPv87ORvYlkbQoqQaFaQuowpDWJJ-uYBup1tf7m6OoDcNI2xICZhvP0pIduA-sCCR6nIdglw2gKPSCtQZWZ9XQlrDc87DHopII-tO_DYsVlNmeg==)
20. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyxplW4MA-JObA0u-F3XraA2YPgf2REDBVFBBdcO0fVaup-4HvStUy2OVPvhi9cszKKAj3ZiVfqXfAwuBuG60TaEZW70QQma4puveNtAJ1NVTbDejU73AhifuoVukN3EZV4h1jDX52WbKejG2tW8tIvX48h39BlyL7e9jH9cjJr7L9c4-8ve854iAQ)
21. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4QDa4ZiwyT0G7SVol86VsxQfFP7HN0JMFSZKZa8N8PgsP_ZW8XBp4qIwpotz_1J-8a923iET0LuUoJpcqSL-2gshya_k2qlNgGhiCZ9EREwTXayUZGsnSH1VfVW5mNeIvqNvQ14SHb2idzm9bDuXWvM_rXZLs2boDEo-I5ug=)
22. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlIlbEAtnnnZLsoLkL6TMFtdJqxsUgRWgduvzA2ndEGfxChygbLc3mh5QuQg3k-EjswU0xNtsGz-7zNLTgwN5Qu9sJ9VtdjIheKMjcz3Ms0Vxxz8e7dHAi4EEBRHB1Cgoln5VswgIisCSWRcrt9gibgvz4)


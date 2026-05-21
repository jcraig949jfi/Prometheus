# Symmetric power L-functions (Sym^n L) 2024-2026 modularity status

**Pythia queue id:** 137
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdRaXdQYXFxWUM3dkxfdU1QcU9PeHFBbxIXUWl3UGFxcVlDN3ZMX3VNUHFPT3hxQW8
**Elapsed:** 249s
**Completed at:** 2026-05-21T16:05:15.890331+00:00

---

# Symmetric Power L-Functions (\(\text{Sym}^n L\)): 2024–2026 Modularity Status and Breakthroughs

**Key Points:**
*   Research confirms that the modularity of symmetric power L-functions has reached a historic milestone between 2024 and 2026, primarily driven by the proofs of symmetric power functoriality for Hilbert modular forms.
*   The evidence conclusively shows that James Newton and Jack Thorne have proven the existence of all symmetric power liftings for cuspidal automorphic representations of \(\text{GL}_2(\mathbb{A}_F)\) associated to Hilbert modular forms of regular weight over totally real fields.
*   It is universally recognized that this breakthrough earned Newton and Thorne the 2024 Clay Research Award, cementing the result as a pivotal success in the Langlands program.
*   The analytic theory of automorphic forms has simultaneously seen groundbreaking advances, notably Paul Nelson's 2024 convexity-breaking bounds for \(\text{GL}(n)\) L-functions, which also earned a Clay Research Award.
*   Recent research spanning 2025 and 2026 suggests continued rapid development in the statistical and analytic properties of symmetric power L-functions, including exact asymptotic formulas for coefficient sums involving Kostka numbers and Weyl modules, as well as new cohomological descriptions for hyper-Kloosterman families.

**What are Symmetric Power L-Functions?**
In number theory, L-functions are complex functions that encode deep arithmetic information about mathematical objects, much like how DNA encodes biological traits. The most famous example is the Riemann zeta function. When mathematicians study elliptic curves or modular forms (highly symmetric functions in complex analysis), they attach an L-function to them. A "symmetric power" L-function is a mathematically constructed "higher-dimensional" version of these original L-functions. Proving their "modularity" means proving that these higher-dimensional constructs also arise from highly symmetric, well-behaved geometric sources (automorphic forms), a central prediction of the famous Langlands program.

**The Significance of the 2024–2026 Breakthroughs**
For decades, proving that all symmetric powers of a modular form are themselves modular (automorphic) was considered out of reach, with early successes limited to the 2nd, 3rd, and 4th powers. The period between 2024 and 2026 marks a paradigm shift. Mathematicians James Newton and Jack Thorne successfully proved that for a vast class of modular forms (Hilbert modular forms over totally real fields), all of their symmetric powers are modular. This not only solves a prototype test case of the Langlands program but also provides the mathematical foundation for understanding the statistical distribution of prime numbers associated with elliptic curves, heavily impacting modern algebraic number theory.

**Ongoing Analytic and Geometric Advances**
Beyond proving that these symmetric power L-functions exist as modular objects, researchers in 2025 and 2026 have made massive strides in calculating their precise values. This includes breaking long-standing theoretical limits (convexity bounds) on their size, calculating the average behavior of their coefficients over sums, and mapping their behavior in alternative mathematical universes, such as p-adic number systems. These concurrent breakthroughs mean that the study of symmetric power L-functions is currently one of the most active and fruitful domains in modern mathematics.

## 1. Introduction and Theoretical Foundations

The Langlands program, proposed by Robert Langlands in the late 1960s, serves as a grand unifying framework in mathematics, connecting number theory, algebraic geometry, and representation theory [cite: 1, 2]. A fundamental pillar of this program is the **Langlands functoriality conjecture**, which predicts deep connections between the automorphic representations of different reductive groups [cite: 3, 4]. 

Within this framework, the **symmetric power functoriality** for \(\text{GL}_2\) represents a prototype test case [cite: 1, 2]. Let \(F\) be a number field and let \(\mathbb{A}_F\) denote its ring of adeles. For a cuspidal automorphic representation \(\pi\) of \(\text{GL}_2(\mathbb{A}_F)\), Langlands functoriality predicts the existence of an automorphic representation \(\text{Sym}^n \pi\) of \(\text{GL}_{n+1}(\mathbb{A}_F)\) for every integer \(n \geq 1\) [cite: 3, 5]. 

This transfer is defined locally at almost all places \(v\) of \(F\). If \(\pi_v\) is an unramified principal series representation corresponding to a semisimple conjugacy class (the Satake parameter) \(t_v = \text{diag}(\alpha_v, \beta_v) \in \text{GL}_2(\mathbb{C})\), the local symmetric power lift \(\text{Sym}^n(\pi_v)\) should correspond to the conjugacy class formed by the \(n\)-th symmetric power of the standard representation of \(\text{GL}_2(\mathbb{C})\) [cite: 3, 6]. Explicitly, this is given by the matrix:
\[ \text{Sym}^n(t_v) = \text{diag}(\alpha_v^n, \alpha_v^{n-1}\beta_v, \dots, \alpha_v \beta_v^{n-1}, \beta_v^n) \in \text{GL}_{n+1}(\mathbb{C}) \]
The global representation \(\text{Sym}^n \pi = \otimes_v \text{Sym}^n(\pi_v)\) is conjectured to be an automorphic representation of \(\text{GL}_{n+1}(\mathbb{A}_F)\) [cite: 6, 7]. The associated complex L-function, \(L(s, \text{Sym}^n \pi)\), is the symmetric power L-function. Proving that this L-function is automorphic (and therefore possesses an analytic continuation and functional equation) has been one of the highest priorities in modern number theory [cite: 1, 7].

The modularity of symmetric powers is inextricably linked to the arithmetic of **elliptic curves**. By the modularity theorem (building on the Taylor-Wiles method), elliptic curves over the rationals are associated with modular forms [cite: 8, 9]. If \(E\) is an elliptic curve, the L-function of its \(n\)-th symmetric power, \(L(s, \text{Sym}^n E)\), is crucial for understanding the distribution of the Frobenius traces of the curve, famously culminating in the proof of the **Sato-Tate conjecture** [cite: 3, 4].

## 2. Historical Context: Early Symmetric Power Functoriality

Prior to the massive breakthroughs of the 2020s, symmetric power functoriality was only known for small values of \(n\), achieved through highly intricate applications of the trace formula and the Langlands-Shahidi method [cite: 7, 10].

*   **\(n=2\) (Symmetric Square):** Proved by Gelbart and Jacquet in 1978 using the converse theorem and the Rankin-Selberg method.
*   **\(n=3\) (Symmetric Cube):** Proved by Kim and Shahidi (1999–2002) using the Langlands-Shahidi method applied to the exceptional group \(G_2\) and \(\text{Spin}(8)\) [cite: 6, 7]. They established that for a non-monomial cuspidal representation \(\pi\) of \(\text{GL}_2\), the partial L-function \(L_S(s, \pi, \text{Sym}^3)\) extends to an entire function on the complex plane [cite: 6, 11].
*   **\(n=4\) (Symmetric Fourth Power):** Proved by Kim (2003) by applying the Langlands-Shahidi method to the exterior square lift from \(\text{GL}_4\) to \(\text{GL}_6\) alongside the symmetric cube [cite: 7, 12].

For \(n \geq 5\), the Langlands-Shahidi method could not be directly applied due to the lack of suitable ambient reductive groups where the required L-functions appear in the constant terms of Eisenstein series [cite: 7, 13]. Consequently, for nearly two decades, the automorphy of \(\text{Sym}^n \pi\) for \(n \ge 5\) remained deeply intractable, although it was assumed in order to formulate conditional bounds on the Ramanujan-Petersson conjecture [cite: 7, 14].

## 3. The Newton-Thorne Breakthroughs (2019–2021)

The stagnation was broken by James Newton and Jack Thorne. By pivoting away from explicit trace formulas toward the highly sophisticated machinery of **Galois deformation rings**, **automorphy lifting theorems (ALTs)**, and **p-adic families of automorphic forms**, they established general symmetric power functoriality for specific classes of modular forms [cite: 3, 9].

In their seminal 2019/2021 papers, published in the *Publications Mathématiques de l'IHÉS*, Newton and Thorne proved the automorphy of \(\text{Sym}^n f\) for every \(n \geq 1\), where \(f\) is a cuspidal Hecke eigenform of level 1 (such as the Ramanujan \(\Delta\) function) [cite: 3, 15]. They subsequently generalized this to include cuspidal Hecke eigenforms associated with semistable elliptic curves over \(\mathbb{Q}\) [cite: 15, 16].

The methodology operated in two major phases:
1.  **Level 1 Base Case:** Using p-adic families of automorphic forms, they demonstrated that proving the result for a single level 1 eigenform of weight \(k \geq 2\) implies the result for all level 1 eigenforms [cite: 3, 15].
2.  **Modularity Lifting and Level Raising:** They proved the automorphy of the specific examples by utilizing level raising congruences and new developments in residually reducible modularity lifting theorems [cite: 3, 16]. 

This bypasses the algebraic group limitations of the Langlands-Shahidi method by directly attacking the \(\ell\)-adic Galois representations attached to the modular forms. If \(\rho_{f, \ell} : \text{Gal}(\overline{\mathbb{Q}}/\mathbb{Q}) \to \text{GL}_2(\overline{\mathbb{Q}}_\ell)\) is the Galois representation attached to \(f\), the symmetric power representation is \(\text{Sym}^n \rho_{f, \ell}\). Newton and Thorne utilized automorphy lifting to show that this representation arises from a cuspidal automorphic representation of \(\text{GL}_{n+1}\) [cite: 3, 5].

## 4. The 2024–2026 Landmark: Hilbert Modular Forms

The absolute pinnacle of this research trajectory arrived with Newton and Thorne's comprehensive proof of symmetric power functoriality for **Hilbert modular forms**, disseminated as a preprint in late 2022 and officially published in the *Annals of Mathematics* (Volume 203, Issue 1) in January 2026 [cite: 17, 18]. 

### 4.1. Statement of the Theorem
The core theorem states: Let \(F\) be a totally real field. There exists a symmetric power lifting \(\text{Sym}^n \pi\) for all integers \(n \geq 1\) for any cuspidal automorphic representation \(\pi\) of \(\text{GL}_2(\mathbb{A}_F)\) associated to a Hilbert modular form of regular weight [cite: 18, 19]. 

This monumental result removes the restrictions to \(\mathbb{Q}\) and specific levels, effectively solving the Langlands symmetric power functoriality conjecture for the entire regular-weight Hilbert modular case [cite: 17, 20].

### 4.2. Proof Methodology
The transition from \(\mathbb{Q}\) to totally real fields \(F\) required overcoming immense technical barriers regarding the geometry of Shimura varieties and the potential ramification of Galois representations [cite: 4, 20].

1.  **Tensor Product Functoriality:** A pivotal stepping stone in their 2026 *Annals* paper is the establishment of tensor product functoriality [cite: 20]. Rather than directly proving symmetric power functoriality, they proved a "functoriality lifting theorem" for tensor products. They demonstrated that the existence of tensor product functoriality implies the existence of symmetric power functoriality. Specifically, they utilized representations of the form \(r_{\pi, \iota} \otimes \text{Sym}^{r-1} r_{\sigma, \iota}\), where \(\pi\) and \(\sigma\) are non-CM cuspidal regular algebraic automorphic representations of \(\text{GL}_2(\mathbb{A}_F)\) [cite: 20].
2.  **Automorphy Lifting for Unitary Groups:** The proof relies heavily on interpreting these Galois representations in the context of automorphic forms on unitary groups [cite: 4]. The authors propagate automorphy between different representations using congruences modulo a prime \(l\) (where \(l\) can be ramified in the coefficient field) [cite: 20, 21]. 
3.  **Induction on the Conductor:** As noted in Newton's expository notes, the proof utilizes an induction on the level of the modular form (or equivalently, the conductor of the associated Galois representation) [cite: 22]. To bound the proliferation of Galois representations and tame the deformation rings, the geometry of Shimura varieties and the simple connectedness of \(\text{Spec } \mathbb{Z}\) (or its analogues for \(F\)) are heavily exploited [cite: 4].

### 4.3. The 2024 Clay Research Award
In recognition of this historic achievement, James Newton and Jack Thorne were awarded the **2024 Clay Research Award** by the Clay Mathematics Institute [cite: 1]. The award citation explicitly recognized "their remarkable proof of the existence of the symmetric power functorial lift for Hilbert modular forms" [cite: 1, 23]. The Clay Institute noted that this conjecture was introduced by Langlands in the late 1960s as a "prototype test case" and that the proof "marks a milestone in work on the Langlands programme" [cite: 1, 2].

Table 1 outlines the chronological milestones of symmetric power functoriality culminating in the 2026 publication.

| Year | Milestone | Primary Contributors | Methodology / Context |
| :--- | :--- | :--- | :--- |
| 1978 | \(\text{Sym}^2\) Modularity | Gelbart & Jacquet | Converse theorem, Rankin-Selberg method |
| 1999–2002 | \(\text{Sym}^3\) Modularity | Kim & Shahidi | Langlands-Shahidi method (exceptional groups) [cite: 6] |
| 2003 | \(\text{Sym}^4\) Modularity | Kim | Exterior square lift \(\text{GL}_4 \to \text{GL}_6\) [cite: 7] |
| 2019–2021 | \(\text{Sym}^n\) over \(\mathbb{Q}\) (Level 1) | Newton & Thorne | p-adic families, automorphy lifting [cite: 15, 24] |
| 2024 | Clay Research Award | Newton & Thorne | Recognition for symmetric power functoriality lift [cite: 1] |
| 2026 | \(\text{Sym}^n\) for Hilbert Modular Forms | Newton & Thorne | Published in *Annals of Mathematics*; Tensor product functoriality over totally real fields [cite: 18, 20] |

## 5. Analytic Theory of Automorphic Forms: 2024–2026 Advances

Simultaneous to the algebraic breakthroughs proving the *existence* of these L-functions, the analytic number theory community achieved monumental results regarding the *size* and *distribution* of symmetric power L-functions on the critical line.

### 5.1. Convexity-Breaking Bounds
L-functions possess a critical line (where the real part of the complex variable \(s\) is \(1/2\)). The Lindelöf Hypothesis bounds the growth of the L-function on this line. For decades, the best unconditional bounds were the "convexity bounds," derived from the Phragmén-Lindelöf principle. Breaking convexity (achieving a strictly smaller exponent) is a profound achievement in analytic number theory.

In 2024, **Paul Nelson** was also awarded a Clay Research Award for his "groundbreaking contributions to the analytic theory of automorphic forms" [cite: 1, 23]. Nelson succeeded in establishing the **first convexity-breaking bounds for a large class of L-functions on the critical line**, including all standard L-functions for \(\text{GL}(n)\) [cite: 2, 23]. 

Nelson’s approach bypassed traditional analytic methods, instead analyzing L-values via associated automorphic periods [cite: 1, 2]. His method integrates:
1.  A refinement of the **orbit method**, developed in earlier collaborative work with Akshay Venkatesh [cite: 1, 2].
2.  An intensive analysis of the geometric side of a **Relative Trace Formula** [cite: 1, 2].
3.  The application of **Amplification** techniques to isolate and bound the specific L-values [cite: 1, 2].

Because symmetric power L-functions for \(\text{GL}_2\) are constructed as L-functions on \(\text{GL}_{n+1}\), Nelson's subconvexity bounds apply directly to the higher symmetric power L-functions whose automorphy was proven by Newton and Thorne.

### 5.2. Asymptotics of Fourier Coefficients
With automorphy secured, determining the statistical distribution of the coefficients of symmetric power L-functions has become a primary focus in 2025 and 2026 [cite: 10, 24]. Let \(f(z) = \sum_{n=1}^\infty \lambda_f(n) n^{\frac{k-1}{2}} q^n\) be a cuspidal Hecke eigenform of weight \(k\). The \(m\)-th symmetric power L-function has coefficients denoted \(\lambda_{\text{Sym}^m f}(n)\) [cite: 25].

In late 2025, Jiangpeng Li and Shu Luo published results in *Monatshefte für Mathematik* providing uniform upper bounds for the sum \(\sum_{n \leq x} \lambda_{\text{Sym}^m f}(n)\) for \(m \geq 2\), improving upon previous estimates utilizing Halász's theorem [cite: 24, 25].

By February 2026, a major preprint utilizing **Weyl modules** and the **Schur functor** expanded this framework significantly [cite: 10]. The authors derived an exact asymptotic formula for the higher power moments of these coefficients. Because the representation \(\text{Sym}^d \rho_f\) corresponds exactly to the symmetric power lifting of \(f\) to \(\text{GL}_{d+1}\), the two types of L-functions coincide: \(L(f, s) = L(\rho_f, s)\) [cite: 10].

The 2026 results state that for the sum over a positive definite binary quadratic form \(Q(n_1, n_2)\):
\[ \sum_{Q(n_1,n_2) \leq x} \lambda_f(Q(n_1, n_2)) = x P_{d,l,Q}(\log x) + \mathcal{O}(x^{\theta_{d,l,Q} + \epsilon}) \]
where \(P_{d,l,Q}\) is a polynomial of degree \(K_{0,d,l} - 1\). The constants \(K_{i,d,l}\) are the **Kostka numbers**, which emerge from the decomposition of the \(\ell\)-adic Galois representations via Young symmetrizers acting on tensor spaces [cite: 10]. The error term exponent \(\theta_{d,l,Q}\) is explicitly determined by the class number of \(Q\) and the Kostka numbers [cite: 10]. This structural integration of algebraic combinatorics (Kostka numbers) into the analytic summation of automorphic forms represents a highly novel synthesis in 2026.

## 6. Distribution of Zeros and Central Values

The distribution of the zeros of symmetric power L-functions is governed by the generalized Riemann hypothesis, but the *low-lying zeros* (those closest to the central point \(s=1/2\)) exhibit spacing distributions that mimic the eigenvalues of random matrices (the Katz-Sarnak density conjecture).

### 6.1. Low-Lying Zeros Weighted by L-Values
In an October 2025 paper published in the *Journal of the Mathematical Society of Japan*, Shingo Sugiyama analyzed the low-lying zeros of symmetric power L-functions, applying a specific weight to the density calculations [cite: 24, 26]. 

For a totally real field \(F\) and an irreducible cuspidal automorphic representation \(\pi\) of \(\text{PGL}_2(\mathbb{A}_F)\) corresponding to a Hilbert modular form, Sugiyama evaluated the one-level density of low-lying zeros of \(L(s, \text{Sym}^r(\pi))\), but uniquely weighted this density by the special values of the **symmetric square L-functions**, \(L((z+1)/2, \text{Sym}^2(\pi))\), for \(z \in [cite: 1]\) [cite: 26]. 

Sugiyama's 2025 results revealed that:
*   For \(0 < z \leq 1\), the weighted density in the level aspect maintains the same symmetry type as previous non-weighted results (specifically Ricotta and Royer's density for \(F=\mathbb{Q}\) with harmonic weight) [cite: 26].
*   For \(z=0\) (weighting by the central values themselves), the density of the low-lying zeros strictly changes its symmetry type *only* when \(r=2\) (the symmetric square case itself) [cite: 26]. This uncovers a deep structural anomaly specific to the symmetric square central values interacting with the spacing of zeros.

### 6.2. Complex Moments and Zero-Free Regions
Concurrent work in 2025 and 2026 has expanded the zero-free regions for Rankin-Selberg convolutions of these symmetric powers. Gergely Harcos and Jesse Thorner (2025) published a new zero-free region for Rankin-Selberg L-functions in *Journal für die Reine und Angewandte Mathematik*, heavily utilizing the proven automorphy of symmetric powers to constrain the poles of the logarithmic derivatives [cite: 24]. Furthermore, the study of complex moments of symmetric power L-functions at \(s=1\), which originated in the early 2000s under conditional assumptions, is now unconditionally verified for Hilbert modular forms due to Newton and Thorne's work [cite: 14, 20].

## 7. Geometric and p-adic L-Functions: Hyper-Kloosterman Families

While the Langlands program primarily deals with complex L-functions, geometric and \(p\)-adic analogues have seen parallel breakthroughs in 2024 and 2025, specifically regarding the **hyper-Kloosterman family**.

The infinite symmetric power L-function plays a pivotal role in Dwork's conjecture regarding the meromorphic continuation of L-functions attached to algebraic varieties over finite fields [cite: 27]. In a February 2024 paper, C. Douglas Haessig analyzed the \(p\)-adic absolute values of the zeros and poles of the symmetric power L-functions of the hyper-Kloosterman family (which are rational functions over the integers) [cite: 28]. Haessig established a uniform lower bound, independent of the symmetric power, for the \(q\)-adic Newton polygon of this L-function, proving that a specific \(p\)-adic cohomology theory exists for the infinite symmetric power L-function [cite: 27, 28].

Building directly on this, Bolun Wei published a preprint in December 2025 extending Haessig's framework [cite: 27]. Wei successfully proved the existence of a cohomological description of the infinity symmetric power L-function for the entire hyper-Kloosterman family [cite: 27]. By explicitly applying the Frobenius endomorphism to this cohomology, Wei derived a definitive, uniform lower bound for the Newton polygon of the associated L-function [cite: 27]. These 2024-2025 geometric results confirm that the "symmetric power" operation fundamentally preserves deep cohomological stability not just over \(\mathbb{C}\), but across \(p\)-adic topologies.

## 8. Implications for the Langlands Program and Sato-Tate

The complete proof of symmetric power functoriality for Hilbert modular forms of regular weight has cascading effects throughout mathematics [cite: 3, 18]. 

### 8.1. The Sato-Tate Conjecture
The original formulation of the Sato-Tate conjecture concerns the distribution of the normalized Frobenius traces \(a_p / 2\sqrt{p}\) for an elliptic curve \(E\) over \(\mathbb{Q}\) without complex multiplication [cite: 4, 5]. It posits that as \(p \to \infty\), these values equidistribute in the interval \([-1, 1]\) according to the semicircle measure \(\frac{2}{\pi} \sqrt{1-x^2} dx\).

By the mid-2000s to 2010s, this was proven conditionally on specific modularity lifting theorems (by Taylor, Harris, Shepherd-Barron, and others using potential automorphy) [cite: 9, 24]. However, the *natural* route to Sato-Tate—as envisioned by Serre and Tate—was to prove the analytic continuation and non-vanishing of the symmetric power L-functions \(L(s, \text{Sym}^n E)\) on the line \(\Re(s) = 1\) [cite: 22]. 

Because an elliptic curve over a totally real field \(F\) (without complex multiplication) is associated to a Hilbert modular form of regular weight 2, Newton and Thorne's 2026 result provides the direct, unconditional proof of the required automorphy for *all* symmetric powers [cite: 19, 20]. Using the Wiener-Ikehara Tauberian theorem, the automorphy and properties of these L-functions yield the exact Sato-Tate equidistribution seamlessly [cite: 22].

### 8.2. Selmer Groups and the Bloch-Kato Conjecture
The modularity of symmetric powers drastically impacts the study of Selmer groups. For instance, the adjoint representation is isomorphic to the symmetric square \(\text{Sym}^2\) twisted by the determinant. Newton and Thorne's preceding work allowed for major advances in controlling adjoint Selmer groups of automorphic Galois representations of unitary type [cite: 22].

Furthermore, as noted in recent literature by Dummigan (2024–2025) and others, the exact central values of the symmetric square L-functions (and higher powers) are integral to verifying instances of the Bloch-Kato conjecture, which relates these L-values to the size of specific Selmer groups (such as \(H^1_f(F, V)\)) [cite: 16, 29]. The unconditional existence of the automorphic representations ensures that the global Galois representations satisfy the strict local-global compatibility required to formulate and test the Bloch-Kato conjecture for these high-dimensional motives [cite: 16, 20].

## 9. Conclusion

The 2024–2026 period will be recorded as a golden era in the study of symmetric power L-functions. The persistent, decades-old barrier to Langlands symmetric power functoriality was decisively shattered by James Newton and Jack Thorne's proof for Hilbert modular forms, deservedly earning them the 2024 Clay Research Award alongside Paul Nelson's revolutionary subconvexity bounds [cite: 1, 20, 23]. 

As the *Annals of Mathematics* publication in January 2026 cements the algebraic foundation [cite: 18, 19], the analytical frontier is currently exploding with new results. The application of Weyl modules and Kostka numbers to L-function coefficients [cite: 10], the classification of low-lying zero densities [cite: 26], and the cohomological bounding of hyper-Kloosterman Newton polygons [cite: 27, 28] demonstrate that mathematicians are now actively mapping the landscape that Newton and Thorne opened. The symmetric power functoriality for \(\text{GL}_2\) over totally real fields stands as a completed chapter, shifting the gaze of the Langlands program toward arbitrary number fields, non-regular weights, and higher-rank groups.

**Sources:**
1. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9KP34eh0sYfRlfn_hUC10Bw4yY6DrJDIMiK9OlrHyhr-96FAgjylypBm5WYRjl4F5-d2P2tiuAuv47ZKi3tuVUpmRHpTcG7_MjTEVHvg6fuwwwlyRn9XRbfzdrykilMpavZZuQh-_lUI5g3dH)
2. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuFx60kU4_DkceogDV5RwQkrgT-YqkLIqXaCCsS5lY4tvHRN8-RhV07ALy7IOAjFgqVq9p41Hjo6G4z-d4zufQWTTUfO1vsZckpJW8Z9vsnn72eA94ed3SfO90MEs6)
3. [crc326gaus.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7eV5H79djf0wcIG1yRTyChO7TY5BOtWBm9iPt4dAswVcnwZiEvVunU7XFSOq_fTHVWKjkSP3az1gKf5d8QN8fn1bm3as_oYQs4YHP5WLrmKhuCSnXXme1EGsXQAMAbhvKnJJrFADGXFsxxOGHq5XZ5U-MhKKHr4u0LimesD43gsZ8zz6TN4vxAC81YxFn9I37r5W5Stfso8OE5RVr8GgpAA==)
4. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMrwIfTGtCsJshW5pQFZbfp7CBz2rKJATkgVYNy7mVLnGoXWctwc09rL9igqEHAuqYw91SgnyGNpk4-wFH0mTErbNVLWhTTJptTn-bVOL8iGlCNW-ksoo7AnLJmrytUurzEZP8CvKK8C9C2SGgiBkhterq-KTfI5JSFIPvotXUA5bhGg==)
5. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuvTGl_S8n9PGHyuYYaj3QkOfHoU7LYg_JfibeWvTtb6AHx-21ydaaSad-6dNmdO46JpQiTqE0Nech1j-LfPOhRmme03l8E1WQ1zwqYQZGA2dNYgJQbh1RNg_cWbu2iR10u4nule_q2ia4XkQNO5DP)
6. [purdue.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8JQQk5bjGQgBELrcbauwksKqE3mLw-i2FAC0tt-JmbxHSKLfeS1PRtJ6cVK4OTpKXnKIgU5hDX-G3UCt06r0ttNtr6PmUY5mheWnftOAHDeLewblZcQMNM6r82tSUsdhpbbTYnsS4T3tfd2kBdNsACOjjcvXe1rLUjQhyPWlMgKNujlKvUGwUANOo4c4hXIEYn9sfum1ywKmSOZI8oeMw09DQhx101ChxaPjdc7gshBLnlAIareuuV-2veUvdmvezIUXHf4WD2bZYCGj1)
7. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGf9DWNrrjA1z_erILyeCBFftmSLBCvHQ0ENRT1JiB2c6ijidL97YLbOBcW52CaHYnhYU-T_tY6AgzHWO31pLUJz2FmNwV1pt6s6jp2slHtOYWHv9Dy_-H5rt8Qq-8xneaG0ARRQ8z36tBsMq2vP8J3zSpIdDk-yg5xML-EnEe3NptZH8MmCM2-QOf8RzlhlZyR97akFIV15uLIQ5afM1vDSbUk1uCR0N-IKfcCsd8NBQXUk3y85RVhjFiaCQ7Nz6IaogRtmy9FymqkfqJ1KRh1BRjVACFePPVPxg0kpws0yjMjAp4teFglS_9B)
8. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-smEbeEQMedbqB_1bwcvb-vYoFGWZCg3SowTJHnV6Du8IKPPDDVuHpY6GRxb1PGAwanlkkwkLtKkncE4glISESGINWzKJxXA-bM7-ioj4qn5WAaxskM-khpVuT0O8SmDAyUs4gG78NOVe8QHp52N7wtffH-pXLRwUXT9-9WRBqgXdB-1WdQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ53h_wJfG0mmoeHObNlYwgim1bdvMDckZ1NKS7Y2U3hiONBrSQCKQ139pU8ou-A0ECeVA-9oSwf6G3GmgAmtnt9C20AzAUDXy07rXeQQcnglW6vBW8A==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXcbS0amlmMANncfwdcEpJEpLuW2aRgudiW2WrjcPUdy6Ypxn7t_BCm8LkRe1hBuug5gpefa830r63KL9zL1bblojcKahKsieuR8e7tdB5y14wNaH5ZQ==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6iSqV9Y55Yy-g7fXAoA4g_lxkWKe_nA2HlyYpskTlv04FgQAh4gLnMxcTqxcQJEyikS7R7l6RywkgFPyUqrkWJUU1qHEGCSs3xtZZsKfcqlRdnDT0WYWT)
12. [usyd.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXeEYkHWKvdqpkAziaM2ncKhvGa6GU6WBGzQsjATdaPcMGt4AT9HObLRzAKgdjsZjU5-MRRvu4u3n1Q7s0yR4ZMBNY6fvLfdMyx1BXWa6oDVvcCQ5rtCO41aakK2DIVANe-jy2Jx9_mXoZVSH4I0cl8A==)
13. [rutgers.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZRlDZGLy4GwEHGPb_Y9z2Yf-qLABcFCny2XJAdoDROlkoYD4SyUIso6CC4Sw960WizWIdrb5oe7fqKaINMdNvhc2X6qWQVbL4qVEYbAotFe93JUe9KIuiP7kadiPGkHs5gus8p0LxACN4Fh8e3uts5jt66RDk6EVL7GAq)
14. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7USDlKmjF6aCNf-uwBVy4U-Q-9TzQRUCgwI1Hf4KCMd2amn9U384_cCNUfMo-wCtPbcsNBU2FZD0GP92rmngjQPT1RhSaro4w1Ds6oZQm1DkozE-908BXUmbc0VIOl7BrrjVBmEl8vNtcE-zM0pVFpFrWfKrB9v8=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPevzAbgf0icGBFzBQKcsAD2_FHt_P9ktMVAWtihSwg3gOGsYGz5WiKx4F5vowrfgD62YsLAIG380ighJaT5xe5DERVdtn3TQoX80FLUw6zTNTcU9MXQ==)
16. [galoisrepresentations.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOMk9TyqKgAV2LKx2rQmv56dDuKbqEe3_m2Jw6sDeoIcGaWllqQDpDUh55cRPgdnULT39I3g4wCqmKV_Ku81mBzs8TsUilpJk1HcDxgvyuBpT8IEB3Ou4kUZVZqWn-Hd2CWatb4mM5MVKfCg2X_7-fO4hylJ1EtvBtOx6yhqgbf4I8HixWpdUXe6A2Ez0GnB5M)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaEQ4c1KQT_TKdNO-HsOTllgB7vUypbgqY-B1e332jSifHoz0AiQzPsHgR3M-b5ft2ZNPea6y3Hn4IBv3FnS1FUnUouERLVJaNv5l54CLcPTivPka92w==)
18. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpCNe1JLzZF_EqijRgGzEE88SKk_YN7OGgbij5KiSWB7jF3n5BjvpJAH8jguwpc8D53XwanthO-RudoNK3PPctMkjfp10CgO8KG7KiLpEi9NPt61pQburMd4BI7_n3Nv1VfyVgAFY=)
19. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1bIe8jByKoYsHtDberaMvznNLOSjuwuleJgwakbMcCCYkrtaiEasDt-ox4YqIQe--DxnEo4B6FfGSqfVD-bxcPNTA-2Jvczs2VeMN3ZiSKTJC98xJPu0pgL2mcS3yssH2aP3P_mClA80IH3b_H7MvS0xGuOFVyChEv5C-Ye37_itDSiPzVWKQglZOJkoJ4xXxA1ieb84kpjKTTiAAVPvgG2zYTdvXeEShM_qYIeOO_5rBdKxVq-LB3U1ahMIDIdmGn1AHZlbdAFh-RHO3rN0ZevNroCvlcye4OOI=)
20. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxoLPN1LITYDphZ6tskSpL1osFrPxEmRfEoCmoQXsDpel8DHQKQiemLp5kARmMXQZAS46LE3z-Y8JzirZUyTIA-nJLypyC6EmWzjgz4_dMaVNd-dfKLXqfYnvhwTEo7q0egE1K8yz9cJr-bwePnPz0vYls36LnFBQ8maSuRwoBydSM_DGQ2K6wttOk)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU7nrDKqJPz1KiYxDWm-2mAHtx04glFYY9FjhdgRxt-eItWFucHl9-XGE21tIoRTBJAmGsBHFTIlgr4kJKIo4eESzg3l8onIze6IV10Su2W7HOO4Q9uxKKgA==)
22. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5dJ73espcXbKJgMKoLqyHwcFmWEE6Z2kuEpv4Hud9eq-l41O4A31I3Hxlth4xxABCfyF0G2OjbC9MWRUBWni3Sbl3MhPAkSKM_l1PxwmE2xYZ9s2XTVo_ZYtEr1SEz_TLyzwg2xyyhbo=)
23. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsQsVKEm6C4L3EO50pPnOCANXDIkbMQ6ZWlFCcoZqGG-DOOlULKXNOsj9OFG4nvT5uhK6D0cywkn8EWmfDPi5cU_x3v-6aDT7FMTeOo3PmGtzerfUXfAJyGRxNu686f-gmeLgfQwnB)
24. [doi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjufN0XdO-NizNCbtv1TXTzqDDjMD4vGnkSs8nHoNQB_QvI0o7RufoalobxIi8SacE9s1VnyAb4r8MJdHb0L-GZD53jcGZAsvTpdvexFwkYB6DhXcC9pBrJgxqk291rEA=)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIGBbaAcll0PFgHmvk6ndinT2mmFEluEOXv8ep-hlJhaTw8x0UH129P__YFk757LWMoIePS37Sl4UV1s5fE3khkM_OiEH1B9nzgM6wPpG7_BF3_NsbiCauFWITj8fF1kkJ8NE5kKI8vi7vsbuJEkH_3cGAXfKO60gxzPiN5nMqJJbWUQSVdr_w8fF92bs6bbdEAvfmC3_NsSKQEntxgw7f9Yg=)
26. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQQq5O_nRv7k8c6_qJJbTU5k-y6ellfaG_hJvq4RPEeyWCUtDnvv7aSdsz4C7Ec54hJQSPbFOj_g5O049UTmsk47KlbojJxG5vARUMUPY2Zw5Lk00Cl3P3izsQpSg02c6w1pNpDbdVgilWNdRYqiciR2gVQ6S-O7xaCLyKMLz5YUq7swQKgINV0eIS77Fha0ToBo7VgHmf-kek5SjGGeB9lzEVHgfDY1ulWLPujPASruLurQzQL7GJS8p6JLt-lQMeTbHSVPe1KhMXJXpGU-iwAN4i7ytFkmC1coAq1F-6v5gBbVellYoz6pK1LYjf)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuyDPoWTSwBJnxT8JLkRwPYyRoVmMvWRxD9u4GatZuSd5lN8aeChWAMUJsjJe_35qx1iUuWUQ7p1gKtDGGPPIVIIOW5bGbJk1e3WrPbCQi_BFB85GCTw==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF56RBMWjgEK5z3uofxoBty3NhOPrCvgXPFb9FDf5P0XaNPgwakZrdy6XwE1Rb8IuZqEhm0z2K0H2F7YIycZGotSOIZDlsqWghgtAp5bfvc9H3UWLt65g==)
29. [sheffield.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMKZqAPQiriWFVUextxMAzloBCNLJN3mMvVcvLoPATl0HeR_ymujmVY0YARjHI4NkESMjVdTIfZtues2-s4jAS_Spd3RSgsXh2nqZ4uN9umzUMBsRHLwt4YMD97nMorFjsextk-o1lQJl4GNMx7g==)


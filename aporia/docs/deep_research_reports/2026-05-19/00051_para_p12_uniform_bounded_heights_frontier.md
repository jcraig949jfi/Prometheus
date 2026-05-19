# PARA-P12: Uniform bounded heights frontier

**Pythia queue id:** 51
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdDVUlNYXFibkMtQzBfdU1QeklYbHlBcxIXQ1VJTWFxYm5DLUMwX3VNUHpJWGx5QXM
**Elapsed:** 252s
**Completed at:** 2026-05-19T11:01:25.977305+00:00

---

# Status of the Uniform Boundedness Conjecture for Rational Points on Curves and Varieties

**Key Points:**
*   **The evidence heavily leans toward** the truth of the Uniform Boundedness Conjecture for rational points on curves of genus $g \ge 2$, with major unconditional breakthroughs confirming weakened variants like Mazur's Conjecture B.
*   **Research conclusively proves** that the number of rational points can be bounded uniformly in terms of the genus, the degree of the base field, and the Mordell-Weil rank of the Jacobian, a milestone achieved by Dimitrov, Gao, and Habegger in 2021.
*   **Recent progress suggests** that this uniformity extends far beyond curves. Work by Gao, Ge, and Kühne (2021–2024) generalizes these bounds to arbitrary subvarieties of abelian varieties, establishing the Uniform Mordell-Lang Conjecture.
*   **Emerging mathematical literature indicates** a shift from existential bounds to explicit, quantitative constants. Preprints scheduled for 2026 by Yu, Yuan, and Zhou attempt to make these uniform bounds fully explicit using Arakelov geometry.
*   **It remains an open question** whether the bounds can be completely freed from their dependence on the Mordell-Weil rank without assuming deep conjectures like Bombieri-Lang. Furthermore, analogous dynamical conjectures (Morton-Silverman) remain strictly conditional on unproven generalizations of the $abc$-conjecture.

**Overview of Uniformity**
The study of Diophantine equations centers on understanding the rational points of algebraic varieties. Since Faltings' 1983 proof of the Mordell Conjecture, it has been known that smooth projective curves of genus $g \ge 2$ over a number field contain only finitely many rational points. However, Faltings' methods did not initially provide a uniform bound on the *number* of these points. The Uniform Boundedness Conjecture postulates that the maximum number of rational points depends solely on the genus of the curve and the degree of the number field, independent of the specific curve itself. While the absolute uniform bound remains conditionally tied to massive frameworks like the Bombieri-Lang conjecture, mathematicians have made historic strides in proving uniform bounds that additionally depend on the rank of the curve's Jacobian. 

**Recent Milestones**
The landscape of arithmetic geometry was profoundly altered by Dimitrov, Gao, and Habegger's 2021 theorem, which unconditionally bounded the number of rational points on curves in terms of their genus, field degree, and Mordell-Weil rank (solving Mazur's Conjecture B). Since this landmark publication, the field has witnessed a flurry of generalizations. The gap principle central to their proof has been expanded to higher-dimensional subvarieties, and researchers are currently utilizing Arakelov geometry to transition these theoretical bounds into explicit, quantitative formulas. Parallel to these geometric triumphs, analogous dynamical systems conjectures are experiencing conditional breakthroughs, bridging the behavior of rational points with the orbits of preperiodic points.

***

## 1. Introduction and Historical Background

The quest to enumerate rational points on curves of positive genus is one of the most celebrated and deeply studied areas of arithmetic geometry [cite: 1, 2]. For an algebraic curve $C$ defined over a number field $K$, understanding the structure of the set of $K$-rational points, denoted $C(K)$, requires navigating the intersection of number theory, algebraic geometry, and complex analysis. 

The most pivotal early milestone in this area was the proof of the **Mordell Conjecture** (proposed in 1922) by Gerd Faltings in 1983 [cite: 2, 3]. Faltings proved that if $C$ is a smooth, geometrically irreducible, projective curve of genus $g \ge 2$ defined over $K$, the set $C(K)$ is strictly finite [cite: 2, 4, 5]. Faltings' original proof, while revolutionary, established finiteness through techniques that did not yield strong uniformity regarding the exact cardinality of $C(K)$ across all curves of a given genus [cite: 3, 6].

This limitation birthed the **Uniform Boundedness Conjecture for Rational Points**, which formally asserts that for a given number field $K$ and a fixed integer $g \ge 2$, there exists an absolute constant $N(K, g)$ depending *only* on $K$ and $g$ such that any algebraic curve $C$ over $K$ of genus $g$ satisfies $|C(K)| \le N(K, g)$ [cite: 7]. A more refined version asks whether the bound can be given merely in terms of $g$ and the degree $d = [K:\mathbb{Q}]$. 

Significant early progress toward this absolute uniformity was achieved by Caporaso, Harris, and Mazur in 1997. They demonstrated that the absolute Uniform Boundedness Conjecture is true *conditionally*, provided one assumes the Bombieri-Lang conjecture for varieties of general type [cite: 1, 7]. The Bombieri-Lang conjecture states that the rational points on a variety of general type are not Zariski dense, which allowed Caporaso, Harris, and Mazur to utilize strong fibration theorems to deduce uniform bounds for curves [cite: 2]. However, unconditionally proving the absolute conjecture remains out of reach.

Consequently, arithmetic geometers focused on a slightly weaker, more tractable variant known as **Mazur's Conjecture B**. This variant posits that there exists a bounding constant $N(K, g, r)$ that limits the number of rational points on $C$, depending not only on $K$ and $g$ but also on the Mordell-Weil rank $r$ of the Jacobian variety $J_C$ of the curve $C$ [cite: 7, 8]. Proving Mazur's Conjecture B became the primary objective for mathematicians utilizing height bounds and Chabauty's method throughout the late 20th and early 21st centuries.

## 2. The 2021 Breakthrough: Dimitrov, Gao, and Habegger

The field experienced a paradigm shift in 2021 when Vesselin Dimitrov, Ziyang Gao, and Philipp Habegger published "Uniformity in Mordell-Lang for curves" in the *Annals of Mathematics* [cite: 7, 9]. This paper successfully resolved Mazur's Conjecture B unconditionally, circumventing the limitations of traditional $p$-adic methods [cite: 7].

### 2.1 Statement of the Theorem
The main theorem established by Dimitrov, Gao, and Habegger (DGH) states the following: Let $g \ge 2$ and $d \ge 1$ be integers. There exist constants $c_0(g, d) > 1$ and $c_1(g, d) > 1$ such that for any smooth, geometrically irreducible, projective curve $C$ of genus $g$ defined over a number field $K$ of degree $[K:\mathbb{Q}] \le d$, the number of $K$-rational points is bounded by:
\[ |C(K)| \le c_0(g, d) \cdot c_1(g, d)^{1+r} \]
where $r = \text{rank}(Jac(C)(K))$ is the Mordell-Weil rank of the Jacobian of $C$ [cite: 4, 6, 10]. 

This completely answered Mazur's question in the affirmative, proving that the cardinality of $C(K)$ can be bounded uniformly without any dependence on the specific heights or coefficients defining the curve $C$ [cite: 4, 5].

### 2.2 Methodology: Vojta's Approach and the Height Dichotomy
The DGH proof relies on the general framework established by Paul Vojta in 1991, which proved the Mordell Conjecture using techniques from Diophantine approximation [cite: 5, 11, 12]. The strategy hinges on mapping the curve $C$ into its Jacobian $J_C$ via an Abel-Jacobi embedding based at some rational point $P_0 \in C(K)$. Thus, $C(K)$ is viewed as a subset of the finitely generated abelian group $J_C(K)$ [cite: 2]. 

By equipping $J_C(K)$ with the Néron-Tate canonical height $\hat{h}$, the rational points are distributed into a Euclidean-like space [cite: 1, 2]. The genius of Vojta's method—and subsequently the DGH refinement—is to partition the points $C(K)$ into two distinct sets based on their canonical height: **"Large points"** and **"Small points"** [cite: 4, 11, 12].

#### 2.2.1 Bounding the Large Points
For the large points (those with $\hat{h}(P)$ exceeding a certain threshold), the geometry of the curve imposes severe sparsity. Vojta's inequality, in tandem with Mumford's inequality (which states that the angle between two large rational points in the Mordell-Weil lattice is bounded away from zero), restricts how densely these points can pack into the space [cite: 2, 4]. 

Building on explicit computations by Rémond, David, and Philippon, the number of large points can be uniformly bounded by a constant of the form $c^{1+r}$ [cite: 4, 9]. The difficulty historically was that the threshold defining a "large point" depended intricately on the specific curve $C$ (specifically, on the Faltings height of $C$ or the moduli height of its Jacobian).

#### 2.2.2 The New Gap Principle and Bounding the Small Points
The fundamental innovation of the DGH paper was dealing with the "small points"—points whose Néron-Tate height falls below the threshold required to apply Vojta's inequality [cite: 4, 9, 12]. If the threshold grows large, the number of potential small points inside the bounded region could conceptually become arbitrarily massive.

To overcome this, DGH proved a **new gap principle** [cite: 2, 12, 13]. They established a powerful relative height inequality that successfully decoupled the bound from the height of the specific curve [cite: 4, 5, 9]. By utilizing a generalized criterion for non-degenerate subvarieties over higher-dimensional bases (specifically the moduli space of abelian varieties $\mathcal{A}_{g, \ell}$), they invoked an equidistribution theorem for points of small height [cite: 4, 9, 13]. This effectively constituted a uniform version of the Bogomolov conjecture for curves embedded in their Jacobians [cite: 13, 14]. 

This gap principle dictated that if the curve has a large moduli height, the small points in $C(K)$ must cluster into a uniformly bounded number of highly localized Néron-Tate metric balls [cite: 4]. Each ball was proven to contain a uniformly bounded number of points. Combined with the bounds on large points, this yielded the full unconditional proof of Mazur's Conjecture B [cite: 4, 9].

## 3. Progress Since 2021: Higher Dimensions and the Uniform Mordell-Lang Conjecture

Following the monumental 2021 result for algebraic curves, arithmetic geometers immediately sought to determine whether the uniformity observed in curves extended to higher-dimensional varieties. This led to a series of rapid breakthroughs culminating in the **Uniform Mordell-Lang Conjecture**, spearheaded by Ziyang Gao, Tangli Ge, and Lars Kühne [cite: 6, 15, 16].

### 3.1 The Uniform Mordell-Lang Statement
The classical Mordell-Lang conjecture (proved by Faltings in the 1990s, following work by Hindry, Raynaud, and Vojta) states that if $X$ is an algebraic subvariety of an abelian variety $A$, and $\Gamma$ is a subgroup of $A$ of finite rank $r$, then the intersection $X(\overline{\mathbb{Q}}) \cap \Gamma$ is contained in a finite union of cosets $x_i + B_i \subseteq X$ [cite: 12, 13, 15].

While Faltings proved that the number of such cosets $N$ is finite, his bound depended heavily on the ambient abelian variety $A$ and its Faltings height [cite: 12, 16]. Between 2021 and 2024, Gao, Ge, and Kühne successfully proved the *Uniform* Mordell-Lang Conjecture. They demonstrated that the number of necessary cosets $N$ can be bounded uniformly, completely independent of the ambient abelian variety $A$ [cite: 13, 15, 16]. The bound depends solely on the dimension of $A$, the degree of the subvariety $X$ (with respect to a symmetric ample line bundle), and the rank $r$ of the subgroup $\Gamma$ [cite: 3, 6].

### 3.2 Methodological Innovations: Hilbert Schemes and Non-Degeneracy
Generalizing the DGH gap principle from curves (dimension 1) to arbitrary subvarieties required overcoming severe geometric obstacles. In the case of curves, DGH relied on the moduli space of principally polarized abelian varieties $\mathcal{A}_{g, \ell}$ and the universal curve [cite: 4, 9, 14]. For arbitrary subvarieties, there is no simple analogous universal space.

Gao, Ge, and Kühne bypassed this by brilliantly utilizing **restricted Hilbert schemes** to parameterize subvarieties of fixed dimension and degree [cite: 12, 16, 17]. This allowed them to construct non-degenerate subvarieties over arbitrary bases, including constant families of abelian varieties [cite: 17]. Their proof integrated Betti maps, the Betti rank formula by Gao, and concepts of automatic uniformity inspired by model-theoretic insights from Hrushovski and Scanlon [cite: 10, 17].

By doing so, Gao, Ge, and Kühne established a general gap principle for algebraic points extending far beyond curves [cite: 12, 15, 16]. This breakthrough not only proved the Uniform Mordell-Lang Conjecture but also concurrently resolved the full **Uniform Bogomolov Conjecture** in abelian varieties [cite: 3, 15]. They showed that algebraic points of small height cannot accumulate densely unless they lie within specific special subvarieties, an insight that definitively controls the distribution of "small points" in higher dimensions [cite: 12, 18, 19].

## 4. Progress Since 2021: Bounds on Heights and Counts 

A major focus of current research is transitioning these existential uniform bounds into explicit, computable numbers. Faltings' original bounds, and even the constants $c_0(g, d)$ and $c_1(g, d)$ in the DGH theorem, were effective in principle but lacked precise, practically computable definitions due to the reliance on abstract equidistribution arguments and compactness [cite: 20].

### 4.1 Quantitative Mordell Conjecture (Yu, Yuan, and Zhou, 2026)
One of the most highly anticipated developments in this area is the forthcoming work of Jiawei Yu, Xinyi Yuan, and Shengxuan Zhou, scheduled for formal publication/preprint release around early 2026, though heavily circulated in seminars starting in 2024 and 2025 [cite: 20, 21, 22, 23]. 

Their project, titled **"Quantitativity on the number of rational points in the Mordell conjecture,"** aims to provide fully explicit constants for the Uniform Boundedness Conjecture/Mazur's Conjecture B [cite: 11, 23, 24]. 

**Methodological shifts toward explicit heights:**
To extract explicit counts, Yu, Yuan, and Zhou have had to restructure the analytic spine of the DGH proof. The previous work heavily relied on successive equidistribution theorems, which are notoriously ineffective for producing explicit constants [cite: 20]. Yu, Yuan, and Zhou employ **Arakelov geometry**—a framework that studies Diophantine equations by adding data at the archimedean (infinite) places via Hermitian metrics [cite: 3, 11, 24]. 

Specifically, they utilize adelic line bundles and analyze Arakelov-Kähler forms via the localization of Bergman kernels [cite: 25, 26]. By establishing explicit arithmetic bigness properties and performing strict analytic estimates of archimedean invariants, they bridge the gap between abstract height bounds and explicit point counting [cite: 20, 24, 25]. 

### 4.2 Analyzing the Counts: The Role of the Mordell-Weil Rank
A critical feature of the progress made by DGH, Gao, Ge, Kühne, and Yuan's team is that the bound on counts always takes the form:
\[ N \le c(g, d)^{1+r} \]
where $r$ is the Mordell-Weil rank [cite: 4, 8, 9].

This exponential dependence on $r$ reveals a deep arithmetic reality: while the geometry of the curve strictly enforces finiteness, the sheer volume of rational points generated by the underlying abelian variety (the Jacobian) scales the size of the discrete intersection [cite: 4, 12].

#### Chabauty-Coleman vs. Vojta Methods
It is vital to contrast this $r$-dependent bound with other prominent techniques, specifically the **Chabauty-Coleman method** [cite: 1, 6, 7].
*   **Chabauty-Coleman:** When the Mordell-Weil rank $r$ is strictly less than the genus $g$ (i.e., $r < g$), the method of Chabauty and Coleman (and subsequent refinements by Michael Stoll, and Katz, Rabinoff, and Zureick-Brown in 2015/2016) yields exceptional bounds [cite: 6, 7, 10]. For instance, Katz et al. proved bounds that depend *only* on the genus and the degree, completely independent of the rank, but this is fundamentally limited by the condition $r < g-3$ or similar rank constraints [cite: 6, 27].
*   **Vojta/DGH Method:** The Vojta method used by DGH has absolutely no restrictions on the rank $r$. It functions unconditionally whether $r = 0$, $r = g$, or $r = 100g$. The trade-off is that the final bound scales with $r$ [cite: 8, 27]. 

Thus, Mazur's Conjecture B has been unequivocally solved, but the absolute Uniform Boundedness Conjecture remains open. If one could uniformly bound the Mordell-Weil rank $r$ for all curves of a given genus over a fixed number field (a notoriously difficult open problem in its own right), the absolute Uniform Boundedness Conjecture would follow as an immediate corollary [cite: 8, 27].

### 4.3 Bounds on Heights
At the core of the uniform counting theorems are profound developments in height theory. Central to Diophantine geometry is the tracking of "arithmetic complexity" of a point $P$ using height functions [cite: 1, 12, 28]. 

The proofs rely on a delicate interplay between two specific heights:
1.  **The Absolute Logarithmic Weil Height $h(P)$:** Defined on projective space via the prime factorization of coordinates. It measures the "size" of the coordinates of $P$ [cite: 1, 9, 14].
2.  **The Néron-Tate Canonical Height $\hat{h}_A(P)$:** Defined on an abelian variety $A$, this height is quadratic and perfectly behaves with respect to the group law (i.e., $\hat{h}_A(nP) = n^2 \hat{h}_A(P)$) [cite: 4, 9, 14]. The set of points with $\hat{h}_A(P) = 0$ corresponds precisely to the torsion subgroup $A(K)_{tors}$ [cite: 2, 29].

In DGH and subsequent papers, a critical technical hurdle was establishing a lower bound for the Néron-Tate height that successfully eliminated any dependency on the height of the curve $C$ itself [cite: 4, 9]. Previously, lower bounds (such as those by David and Philippon [cite: 4, 6]) were effective but depended on the Faltings height of $A$ or the specific parameters defining the curve. 

The **Gao-Habegger Height Inequality** (first developed in 2019 for the geometric Bogomolov conjecture and vastly expanded in 2021) provided the ultimate resolution [cite: 4, 9, 10]. They proved that for points $x \in X(\overline{\mathbb{Q}})$, if the point is not contained in a degenerate subvariety, its canonical height $\hat{h}(x)$ is bounded away from zero by a margin that depends *only* on the degree of the variety, rather than the specific moduli [cite: 9, 12, 16]. This breakthrough on heights allowed the strict segregation of points into "large" (counted by Vojta's inequality [cite: 4, 21]) and "small" (counted by the gap principle [cite: 4, 12, 16]).

## 5. The Uniform Boundedness Conjecture in Arithmetic Dynamics

While geometric uniform boundedness has experienced unconditional victories, a highly active parallel universe of research exists in **Arithmetic Dynamics**. Here, the role of rational points on curves is played by the **preperiodic points** of algebraic maps [cite: 30, 31, 32].

### 5.1 The Morton-Silverman Conjecture
In 1994, Morton and Silverman proposed the Dynamical Uniform Boundedness Conjecture (DUBC) [cite: 28, 29, 32]. It serves as a dynamical analogue of Mazur's theorem on the torsion of elliptic curves and uniform boundedness on higher genus curves [cite: 28, 32].

**The DUBC states:** Let $d \ge 2$, $N \ge 1$, and let $K$ be a number field. For any morphism $f: \mathbb{P}^N \to \mathbb{P}^N$ of degree $d$ defined over $K$, there is an absolute constant $B(d, N, [K:\mathbb{Q}])$ such that the number of $K$-rational preperiodic points of $f$ is bounded strictly by $B$ [cite: 28, 32].

By Northcott's Theorem, the number of preperiodic points is always finite [cite: 29, 31]. However, establishing uniformity—proving that the bound $B$ does not depend on the specific coefficients of $f$—remains one of the most stubborn problems in mathematics [cite: 30, 31]. For instance, even for the simple quadratic family $f_c(z) = z^2 + c$ over $\mathbb{Q}$, it is not unconditionally known if the number of rational preperiodic points is globally bounded by an absolute constant across all $c \in \mathbb{Q}$ [cite: 31, 32].

### 5.2 Progress Since 2021: Conditional Proofs via the $abcd$-Conjecture
A major breakthrough occurred simultaneously with the DGH paper. In 2021, Nicole Looper achieved a profound conditional proof of the Morton-Silverman Uniform Boundedness Conjecture for polynomial maps [cite: 28, 29, 30, 33]. 

Looper demonstrated that if one assumes a standard, widely believed postulate in arithmetic geometry known as the **$abcd$-conjecture** (a higher-dimensional generalization by Vojta of the classical $abc$-conjecture [cite: 28, 29]), the Morton-Silverman conjecture holds for polynomials over number fields [cite: 28, 29, 33]. Her technique also yielded a dynamical analogue of Lang's conjecture on minimal canonical heights [cite: 28, 29, 33].

Looper's work fundamentally connected the dynamical uniform boundedness properties with higher-dimensional Diophantine approximation constraints [cite: 28, 29]. If the $abcd$-conjecture limits the presence of highly divisible coordinates (i.e., limits the accumulation of small prime factors), this arithmetic rigidity directly stifles the polynomial maps' ability to support arbitrarily long preperiodic orbits [cite: 29].

For non-isotrivial unicritical polynomials of degree $\ge 5$ over function fields of characteristic zero, Looper managed to make her result unconditionally true, leveraging the geometric freedom function fields offer [cite: 28, 33]. However, over $\mathbb{Q}$ or generic number fields, dynamical uniform boundedness remains strictly conditional on the $abc$ framework [cite: 29, 31]. 

## 6. Synthesis and Current Trajectory

The period from 2021 to the present represents an undisputed golden era for the Uniform Boundedness Conjecture [cite: 3, 13]. The intersection of Arakelov geometry, Vojta's Diophantine approximation methods, and the sophisticated use of moduli spaces and Hilbert schemes has transformed conjectures that lay dormant for decades into proven theorems [cite: 3, 12, 16, 17].

To summarize the definitive state of the field as of the mid-2020s:
1.  **Mazur's Conjecture B is unconditionally proven.** Dimitrov, Gao, and Habegger permanently established that rational points on $g \ge 2$ curves are bounded uniformly by a function $c_0(g, d) \cdot c_1(g, d)^{1+r}$ [cite: 4, 7, 9].
2.  **Higher Dimensions are Resolved.** The Uniform Mordell-Lang and Uniform Bogomolov conjectures for arbitrary subvarieties of abelian varieties have been unconditionally solved by Gao, Ge, and Kühne [cite: 6, 15, 16]. 
3.  **Constants are Becoming Explicit.** Following the existential proofs, the immediate mathematical vanguard (led by Yu, Yuan, and Zhou [cite: 21, 22, 23]) is rapidly generating explicit bounds utilizing deep analytic invariants via Arakelov-Kähler forms [cite: 11, 26].
4.  **Absolute Uniformity and Dynamical Uniformity remain Conditional.** Eliminating the $1+r$ exponent requires proving the Bombieri-Lang conjecture or independently bounding Mordell-Weil ranks [cite: 1, 2, 27]. Similarly, uniform counting of dynamical preperiodic points (Morton-Silverman) awaits the resolution of the $abcd$-conjecture [cite: 28, 29].

The convergence of model theory (Hrushovski [cite: 3, 17]), Arakelov geometry (Yuan, Zhang [cite: 3, 24]), and height gap principles (Gao, Habegger, Dimitrov [cite: 9, 10, 13]) ensures that the study of uniform bounds on rational heights and counts will remain the focal point of Diophantine geometry for the foreseeable future.

**Sources:**
1. [utoronto.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGah7cVEljpVPGPwIG5EWOawIVzN5oJ34b0aB4W80qbJzF2gfVs6h4hYryjdaaVjV_laVVIaYI4F_ZuAqvsib4nVm8xoqFXPeahgTvfTrPMFyB_DnS0xBX3x2CiXihM7UBMEzVP2ocOxagYG9lHcODfqa8=)
2. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6USi_CciLtg4QJ5K3S-viIAJRJhx4TYY-jvq29uk5InVBOkjxzU7uHEQTW8Rvv09uJkJrDcpq-MMFvso2DJ8A27CNqbda57Y4TOc9UOOXC4rYR51IO8AbKMW2I62T9zvzHeKtt3o=)
3. [mordell.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHju8KlAoQeN5mFa5LS56v2GEmrQtjmNVErfPJKz3neL8-Fyu-DlMXJ1zkTWLYR5-yXsZkLg4M-k8fYnVH1xYh-h1EUyw2HbFs_rg==)
4. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESzC4dEIyXDPW5s8cbzqcpm6LTQf-8l5yZFQ9rAuOk09_dnJ6I-IWRQ9rYp0D7Ma1nnHOFKvk_v0DID5eqh2CZLhselX4fyX2iQPx0_Ur67Z3kU0zMdXQumzvT5V04iVOiuVSANmXH43FtPCoJmT6lTmTTIN1vvVsbWE8=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpP3LJC8sMqIVkkI8ppAfbuYm3hmRQgpgKl2bXVGYHc3aKO98TYoQ3Cyp_2aE7UhDMbdMGNpzy4CZ18JG6RUNfUeROnrwVGJVi2NGE57LU8VHe6xOWYw==)
6. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElDw4guIZs45-QpkAp7QCSTtrx7E5M23MUnJB1G6fza-kBFoKgZmIhoQ3hG49cGJbHr2F503dObB5JYhE95VPXFBmMU2n4zpKYm3Xc3suSRNmZ1K1WgV0xlltNB27It3p19PjCFJe0Fg==)
7. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiSnqQpiOBUSoPBZ1fnfR10MbqEFHNDQo_31FFX1uFthhuAy8ROHL9Fqpztf1iEq87jkznFUgG3pEdtQKdK3dz2UjQ18w_Bfcuu7KABf12Nq6muVlzQKP2NXLtXstxYJ6-vcpbfN8STzcfcogaZvR41k2JFMUElRd4JijTQczl7TL7x_jl3Q==)
8. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzjoch7HxyreM9fwwvH6xwNf7Pfdk7Znnd_5fpw6JBYejTrjwHzSl4cyIkwr4iybi-PNhoMbfExFbVNIqjAaRYMfZKKAPhLya4IbFD9cw_QoXcTBDgURKzPkfQJn-KHBeX-7OWuqyR6ENW7Q0iANyfz0u6Cu-m2C3hfuxsaONUeRSNDPmY4pBGZjs4J61o8Vpx25h6AVhLgU9WPfGbLK8RRzH33ISBTTgOoGfaiKk=)
9. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWnM1-Df7sgUpCts1EXfE7p3d2ktMWqQGWv0tv4DZ2E4a2rrD_1B5d3_btIigjBbOxT341cavrJRVT6PmLIg9mpWySaLs8YNYS3OS1my8lvyPqMxrQtWKfXAZPhb1AbF15XOI3ks0SHCTjgwkAfX5FAQOcqdmbtXf-HI2dugska7T2SQkBnRwLZ3WbDCRPxgw7gQxpEo44JoU5AEO35cvZfzaL9GK7NnwqvvwzXtLi20auzkl5CxKHwVyl7AhVwNWAAZ_IF6lE)
10. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5R_SEZzeRyQGoO5v6aLmCjXIbL0_BXeuZ2CoTNufT8Zm8u-1u3tNTR2KOb7dCHORZu1_F3M9MzzejKpx0SloFvTROkN8UiKM4hPVgZrsWjgo5clrq9vRZNlTnSJDsWHHQDw8=)
11. [pku.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYG32o4rh6d9aTdU3WWwSp6pAGgB88B90X9src-_odeySuoVss8clGnkZy6qZBUmDyS8Oug9c0hlj6mdg5t5A8YLvjSrrI-g_d2g7I4nGqYOw4oJPRcnRdZ_TK7SLhFEVXvgaHOAD7j1ldwFqQGj__6oTqX1wXvpCSGZPbzg==)
12. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHthatdOzw5LGYntozXYOaD0PD2mwVJIpZ-SzdZxWWrQDTvcEJs8OiCP0mdYfydfpHmZrOD6LXtitcz6EDlPcWratskn2cmnBHbmaUtELve2cf7pTuuEys9RnpkG6BkIiPh3mB_M-pXd6Opxpw4)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKYFdi4xGl9BUuPiV4yZzAfgjnxD8fbgrIaGqRjQbIS5mAqZObWfmaPhGe4Xqz0ULMPhkcRI8J03wcAdh_CfHEXMN8tg4fnKcXByj8RqXcdk4F-wD4nK_KApiVT-3eAmRle5TPMx1IWmHzoR8k7mIFLX8_LjEvX2v28GhD-D4DkAW8IDwbEP0QcpI2g-tyomKYLHrynRAPbGaya7ZNDpUNrBD1pNTjbbB2HH2BIXU=)
14. [ub.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbHm5h0jhqvqDuH9w1nmnhy2zwPcGNHksuVGRAu3FBFioyyeNCQwPjM4CHyTcdnCl0Bgrqz6i8pYYNa9vOJEQ2JNfkaXlhuMLLqhhn2B0orbdzJrfCL3IKuIcH7Tk=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYzbBEI29HDbMJTwW23pcrIcn_BODxfv4hZtrtRKIVNfiC2Cpt25jDZcakG2i_8zpHq1So7R9f3vJl7mlx9VSM0x6j8um_zV2KpFpfYY6NbNTzQhpenQ==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyzSh4MboGLQWwhAhx-Z7zCy3GDkP2PXoe-NvvSbGYXDVgNKb1n3TMYBdqIrOfE6nOUmjUekAzNCa7abrxGwVWBq0lIeyxmJHvoO4K3iT_KxjxP4Nl50f0UA==)
17. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFteh0CX-uZbo1SGJj8hQutk_e9bhIbPpAhtAMnsw4drOSBaXHDGWzKbGmH4KjVltq3LeLMJXJzA2byr5IKQ8rNpDGUxWk9iAezW5UskaV3tNxOyzEtXIRxitnp7dIPj_g=)
18. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE93g868Igpk0p8UvePYmSGCYOC18iiJQf5SAd32qSngMEsuI9IGAG4WwNjDVrxIggvo6saLWVttAAggOVjdqIf2_Z2v-UBMs0_hImJGTAbS9WxwpFBHSOw_ClnkGQpVZksATL8F0W03ALMiLXFHXc=)
19. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuT1vTuVU6MdZfwmc5rE2faVTfHSz4I5NuBZMQF7AHj21DB4IaM_IeJaIj6rDxKSQLQzbzINQCUmL-6417UecYmF59rio-V5CkhItKDoAFB-9RxUL1yRXuZcbtYPYuBfFGOvzYPA==)
20. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGv4u7TCh3Is_ayEnkXZ3e8ZfqUxC0OR4PX-gzfBwBX0TcbU8tJJ0yM4ELnlAGgtD0utG55-eSZdorgUNwDr5Xz000IqNhiHMC6pN6Zwl9f1LotUIFN9F9rJMqfodeXS60r)
21. [bimsa.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDg9TFkeIQiDUOJDhYsQHwXskOhtWalbxW-kl7zM_3hsaSHgF7l1_2pf5Cstlw8B0J558O0tBSl9I-PDNrEZRx-AzqNpIzeOXBLytOhGv8q3r72aICkfKKs64=)
22. [mcm.ac.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExB6l9Xf0Pttkyc33fPoHjSkkgEHJXdabVh81dMZp-k8aie8xAUglF6N1Qro77PirsaQH26gDlSlHxK2UqXjTSZCtVxLOufIFfosjFZvULjSAhqX9RwWjhfWXEH1ctIfPbVsgN1Tcuou7ocNGs0OykfBzgbQm2hso=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkw9-FojOnbXJlUzZN_Qo1RBI0zJm-G-IJ1xeGsKM8Jq0T7MJlKCBYDmuY0QXy2BF_jkqhW5Ok23qC_02mxqVJ0O6Izwz8RglwxojMtLh7kmilXr39_g==)
24. [pku.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcgKPFP_zEYaEvRRUGASlrnkNAdbQwZQpmaXQpBBd4yqJTIHkctQwPzt5sOv0X3x3cu7aBRLGspBBvHINShPeZLXoq0LWhxz06U77mOyPeyPAREzU8d7M5oE71nr_o53av8pAt4b9JKmNkvw8=)
25. [uaic.ro](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpOHoFw3x69Cq8hr648Mrzowy8WPRz57oHRqWozyG_0IasqKcyQvbFBySXiPtpMaP_W1KB7BYhRMNqav9Ng5AV6atnea7geAvJqEw4jk-dlZJRCofUGXVbJ-oHNoQG7DRwHW49yKMrwcIAow==)
26. [cnrs.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAsRIAA1eBLoxeke_AXOaIBY0Q4tJ7TjIcG6uF4FkH8MXp-dPkrUtfZPWrA_BnmtZi2flp2Bt8uEEIRlM5NBaEdTp8-jR1-IjGMFSd8HOGUh74jXDvbDWv4iBxtoUT)
27. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQ6nOhc5T_q4LYCA75peA47YWwA1xU-jB6d3eKDdt0etN4ggnAFzFD2OQNI48wHGXosEjzY7nUih-D7DfD3hETS24ZS79nB4-h2XZqEjJsyAY8bPVTuEWWF3tROIhWThZoqEnqt3aQc6W12JjGU5OHBh3PbqdRR35EsYaNb4Vmwo0A9SV_OJXQsq47fqF3PAjLbFykV3Fc4zhgNB_8GFQzzm1ghRxX1eG924IW8nRE-w==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvEExTuHOHtpYF7Gb70JOcXUseiWJGaupT3HnYhjbnVe1SF27ZQPYA0OZ_tFfxLIfcsdheShn15wXfQOl3_F7Idlzi8dJ9i_gVhDZmsFiYr7QWkaBM2Q==)
29. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2jY7odpi5o0p2qqliUatRBXPeRjpcYmo7xLRzNC4CaebGLqUYC3f0Y_0g0vEijX4ssi6k17G0kUkL8NaIsBplntGlxmQwrt2rlhmVlQwzC0sa0q2t19EVKw_wAqz38HPv0rOc)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMJTDXCAKX0_mrB0sZ8zJyLzQ6R6X32Ec7-W91CBsXwqNSG-6pdhWoA0X53fayd4dDaytQc1RI28-Qt65YO5O2o6spoSVrXamIl1ebCtB23fOpbj_QGQ==)
31. [vassar.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_s3dovlf9m-CxVriak-g9BzXpftc85nL0U54CZmuzle-obMtw8IeiDQcn4tl8hw8Ysf0Km00VvRjZ7jTPtPOgpMAXmeNAUfg49TaYXxZGUnyf33nFS3PKd9312dB-eApwTMvMBy934sejo6dWcu60F4xcRQksyeEZ-z3iJlJ_w6ROV7jFaLWSysUaai5pNyYoiSopTQ_GDGVZpNxQn4OGhjdz)
32. [mathunion.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqhNHpe08y8g1yjswIdc3L-OHeB2malyStMA0V5EXBQ_CxOEhxcxgA6eEMqOawwH8m_cjozhHYdLi6s9FYSJTUS69_ksPZlGBgahU2TV0y47ryObqZDHESI4OrU9bDn80npOhVp3j0DPou7cE0zAFZM6Ljq_FtjIgF7Hz-cwk_rmUImQgZYSWK86K4g-CnkeO24j0=)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVLRjov_FYKZ1Udafut9EON9KjeGVVzQTr4KDITSoduUOJiL1dglnAEcJW9ey84Fiii1rk1j5mlzUzqjQyIebw-Zwr18tlscWp7MMN7j4RsvLV3GlaKw==)


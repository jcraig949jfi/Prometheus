# ISL-03: Genus-2 uniformity status 2025

**Pythia queue id:** 75
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChY3ZTBPYXVDbEc4Zjd1Z2ZRdlotSkRBEhY3ZTBPYXVDbEc4Zjd1Z2ZRdlotSkRB
**Elapsed:** 311s
**Completed at:** 2026-05-21T11:40:21.479606+00:00

---

# Status of Bombieri-Lang Uniformity for Rational Points on Genus-2 Curves (2025-2026)

*   **Theoretical Uniformity:** Research indicates that the Weak Bombieri-Lang conjecture strongly implies Caporaso-Harris-Mazur uniformity, suggesting that the maximum number of rational points on a curve of genus $g \ge 2$ over a number field $K$ is bounded by a constant depending only on $g$ and $K$.
*   **Effective Bounds:** It seems highly likely, based on the recent Dimitrov-Gao-Habegger (DGH) theorem, that the number of rational points is bounded exponentially by the Mordell-Weil rank of the Jacobian, specifically bounded by $c^{1+\text{rk}(J(K))}$, removing the dependence on the Faltings height.
*   **Average Behavior:** Evidence from arithmetic statistics (building on Bhargava, Skinner, Wei Zhang, and Wei Ho) demonstrates that the *average* number of rational points on genus-2 curves, when ordered by height, is strictly bounded.
*   **Computational Limits and Records:** Empirical searches through the L-functions and Modular Forms Database (LMFDB) and via K3 surface specializations have established that the current record for rational points on a genus-2 curve over $\mathbb{Q}$ is at least 642 (achieved by Stoll, building on Elkies). 
*   **Modern Algorithmic Approaches (2025-2026):** For specific curves, techniques like Quadratic Chabauty have recently been scaled up in the LMFDB to systematically find exact sets of rational points on genus-2 bielliptic curves of rank 1 and 2, navigating spaces where traditional Chabauty-Coleman methods fail. 

The question of quantifying rational points on curves of genus $g \ge 2$ sits at the intersection of deep theoretical conjectures and cutting-edge computational mathematics. Since Faltings proved Mordell's Conjecture in 1983, we have known that such curves possess only finitely many rational points. However, the exact bounds, the average distributions, and the algorithmic determination of these points remain vibrant areas of research. This report synthesizes the current status of the Bombieri-Lang uniformity conjectures, traces the breakthroughs in arithmetic statistics spearheaded by Bhargava, Skinner, and their collaborators, and details the rigorous computational milestones achieved within the LMFDB framework up through the 2025-2026 academic horizon.

***

## 1. The Geometric and Arithmetic Framework of Genus-2 Curves

To understand the uniformity of rational points, one must first establish the algebraic and geometric foundations of genus-2 curves. Over a field $K$ of characteristic not equal to 2, a smooth, projective, absolutely integral curve $C$ of genus 2 can always be represented by a hyperelliptic affine model of the form:
\[ C: y^2 = f(x) \]
where $f(x) \in K[x]$ is a polynomial of degree 5 or 6 without repeated roots [cite: 1, 2]. 

In 1922, L.J. Mordell conjectured that for any curve of genus $g \ge 2$ over a number field $K$, the set of $K$-rational points, denoted $C(K)$, is finite [cite: 2, 3]. This was famously proven by Gerd Faltings in 1983, transforming the Mordell Conjecture into Faltings' Theorem [cite: 2, 4]. Faltings' proof utilized the arithmetic of the curve's Jacobian variety $J$, an abelian variety of dimension $g$ (dimension 2 for genus 2), proving both the Tate conjecture and the Shafarevich conjecture for abelian varieties along the way [cite: 5].

While Faltings' Theorem guarantees the finiteness of $C(K)$, it is notoriously ineffective. It does not provide an algorithm to compute the set $C(K)$, nor does it provide a direct upper bound on the cardinality $\#C(K)$ [cite: 6, 7]. Consequently, understanding the size of $C(K)$—whether in terms of an absolute maximum bound, an average bound over families of curves, or through explicit algorithmic computation—has become one of the premier challenges in arithmetic geometry.

## 2. The Bombieri-Lang Conjecture and Uniformity

The generalization of Faltings' Theorem to higher-dimensional varieties is governed by the **Bombieri-Lang Conjecture**. The weak form of this conjecture states that if $X$ is a geometrically connected variety of general type defined over a number field $K$, then the set of rational points $X(K)$ is not Zariski dense in $X$ [cite: 8, 9]. For curves, a variety is of general type if and only if its genus is $g \ge 2$; thus, for dimension 1, the Bombieri-Lang conjecture is exactly Faltings' Theorem [cite: 8, 10].

### 2.1 The Caporaso-Harris-Mazur Theorem
In 1997, Caporaso, Harris, and Mazur (CHM) published a monumental result linking the higher-dimensional Bombieri-Lang conjecture back to the quantitative arithmetic of curves. They proved that if the Weak Bombieri-Lang Conjecture holds, then the **Uniformity Conjecture** for curves must also hold [cite: 11, 12]. 

The Uniformity Conjecture asserts that there exists a universal constant $B(g, K)$, dependent only on the genus $g \ge 2$ and the number field $K$, such that:
\[ \#C(K) \le B(g, K) \]
for *all* smooth algebraic curves $C$ of genus $g$ defined over $K$ [cite: 6]. 

This implies that the maximum number of rational points on a genus-2 curve over $\mathbb{Q}$ is bounded by an absolute integer $B(2, \mathbb{Q})$ [cite: 6]. However, because the CHM proof relies on a conditional, unproven hypothesis in higher dimensions and utilizes non-effective geometric arguments, it offers no explicit value for $B(2, \mathbb{Q})$ [cite: 6, 11].

## 3. Effective Bounds and the DGH Theorem

Because the abstract constant $B(g, K)$ remains elusive, mathematicians have sought effective bounds that depend on secondary arithmetic invariants of the curve, most notably the **Mordell-Weil rank** of its Jacobian. By the Mordell-Weil theorem, the group of rational points on the Jacobian, $J(K)$, is a finitely generated abelian group, meaning $J(K) \cong J(K)_{\text{tors}} \oplus \mathbb{Z}^r$, where $r$ is the rank [cite: 5, 13].

### 3.1 Vojta's Inequality and Early Bounds
Early explicit bounds on $\#C(K)$ were achieved by quantifying Paul Vojta's proof of the Mordell Conjecture. Using Vojta's method, David and Philippon, as well as Rémond, established bounds on $\#C(K)$ that grew exponentially with the rank of the Jacobian, but these bounds also depended heavily on the Faltings height of the Jacobian, $h_{\text{Fal}}(J)$ [cite: 3, 5]. 

Barry Mazur subsequently posed a highly influential question: Can the number of rational points be bounded *solely* in terms of the genus $g$, the degree of the number field $[K:\mathbb{Q}]$, and the rank $r$ of $J(K)$, independent of the Faltings height? [cite: 5, 11].

### 3.2 The Dimitrov-Gao-Habegger (DGH) Breakthrough
In 2020, Dimitrov, Gao, and Habegger affirmatively answered Mazur's question, achieving a landmark result in Diophantine geometry [cite: 5, 13]. They established a uniform bound on the number of rational points that completely removes the dependence on the height of the curve.

**Theorem (Dimitrov-Gao-Habegger):** Let $g \ge 2$ and $d \ge 1$ be integers. There exists a constant $c = c(g, d) > 0$, depending polynomially on $d$, such that for any geometrically irreducible smooth projective curve $C$ of genus $g$ defined over a number field $K$ of degree $d$, the number of rational points is bounded by:
\[ \#C(K) \le c^{1 + \text{rk}(J(K))} \]
[cite: 3, 5].

This result represents the strongest unconditional approximation of the Bombieri-Lang uniformity for curves currently available. It guarantees that as long as the rank of the Jacobian is constrained, the number of rational points is universally bounded [cite: 5, 11].

## 4. Arithmetic Statistics: The Average Number of Rational Points

While bounding the absolute maximum number of points yields enormous theoretical constants, the *average* behavior of genus-2 curves reveals a much sparser reality. The pioneering techniques of arithmetic statistics—greatly advanced by Manjul Bhargava, Christopher Skinner, Wei Zhang, and Wei Ho—have allowed mathematicians to calculate the average sizes of Selmer groups, which in turn bound the average ranks of Jacobians, and ultimately, the average number of rational points.

### 4.1 The Bhargava-Skinner-Wei Zhang Framework
The statistical understanding of rational points on curves experienced a revolution in the 2010s. In a landmark 2014 paper, Manjul Bhargava, Christopher Skinner, and Wei Zhang proved that a majority (at least 66%) of elliptic curves over $\mathbb{Q}$ satisfy the Birch and Swinnerton-Dyer (BSD) conjecture [cite: 14]. Their method synthesized three major threads of research:
1.  **Bhargava-Shankar** results on the average sizes of $p$-Selmer groups, which proved that the average algebraic rank of elliptic curves is bounded [cite: 14, 15].
2.  **Skinner-Urban** proof of the Iwasawa Main Conjecture for $\text{GL}(2)$, allowing transitions from algebraic to analytic ranks [cite: 14, 15].
3.  **Dokchitser brothers'** work on the Parity Conjecture [cite: 14].

These techniques heavily rely on parameterizing arithmetic objects via representations of algebraic groups (e.g., coregular spaces), an area where Bhargava and Wei Ho have also made profound contributions (such as their work on the average sizes of Selmer groups and ranks in families of elliptic curves with marked points) [cite: 16, 17]. Furthermore, recent algorithmic verifications by Burungale, Skinner, Tian, and Wan (2024-2026) have made these statistical results explicit, computationally identifying hundreds of thousands of curves in the LMFDB that unconditionally satisfy the strong BSD conjecture [cite: 18].

### 4.2 Extension to Genus 2 and Alpoge's Theorem
The geometry-of-numbers techniques pioneered by Bhargava were extended to higher genus curves. Notably, Bhargava and Gross proved that the average size of the 2-Selmer group of the Jacobians of hyperelliptic curves with a marked rational Weierstrass point over $\mathbb{Q}$ is exactly 3. Consequently, the average Mordell-Weil rank of these Jacobians is bounded [cite: 19, 20].

Building precisely on the Bhargava-Gross result, Levent Alpoge (2018) achieved a breakthrough concerning the average uniformity of rational points. Alpoge proved that when genus-2 curves over $\mathbb{Q}$ with a marked Weierstrass point are ordered by height, the **average number of rational points is bounded** [cite: 1, 21]. 

Alpoge's methodology partitions the rational points on $C: y^2 = f(x)$ into three strata based on their heights [cite: 1, 22]:
1.  **Small-height points:** Bounded manually using elementary height functions [cite: 21, 22].
2.  **Medium-height points:** Bounded by establishing an explicit Mumford gap principle and applying the Kabatiansky-Levenshtein theorem on spherical codes (building on work by Silverman, Helfgott, and Venkatesh) [cite: 21, 22].
3.  **Large-height points:** Points $P$ satisfying $h(P) \gg h(C)$. Alpoge applies Bombieri-Vojta's proof of Faltings' Theorem to show that the number of such large points is $\ll 1.872^{\text{rk}(J(\mathbb{Q}))}$ [cite: 1, 22]. 

Because the average value of $1.872^{\text{rk}(J(\mathbb{Q}))}$ is finite (a consequence of the Bhargava-Gross theorem on 2-Selmer groups), Alpoge concluded that the global average of $\#C(\mathbb{Q})$ is bounded [cite: 21, 22]. This provides a statistical counterpart to the Caporaso-Harris-Mazur uniformity: not only is there conjecturally an absolute cap $B(2, \mathbb{Q})$, but the *average* curve possesses very few rational points.

## 5. Records and Lower Bounds on $B(2, \mathbb{Q})$

Given that the theoretical constant $B(2, \mathbb{Q})$ from the Uniformity Conjecture is ineffective, computational number theorists have engaged in extensive searches to establish lower bounds for $B(2, \mathbb{Q})$ by finding specific genus-2 curves with an exceptionally high number of rational points.

### 5.1 Historical Records
Finding curves with many points often relies on searching within special subfamilies of the moduli space $\mathcal{M}_2$ that possess high symmetries (large automorphism groups) or whose Jacobians split completely [cite: 23, 24]. 
*   An early record was set by Keller and Kulesz, who discovered a genus-2 curve with **588 rational points** [cite: 11, 25]. This curve was highly symmetric, possessing an automorphism group isomorphic to $D_{12}$ (the dihedral group of order 12), meaning its 588 points were partitioned into just 49 distinct orbits under the group action [cite: 6, 11]. Elkies showed that the Jacobian of this curve is isogenous to the square of an elliptic curve of rank at least 12 [cite: 26, 27].
*   For curves with a minimal automorphism group (only the hyperelliptic involution), an earlier record was 366 points [cite: 6]. Elkies later improved this minimal-automorphism record to 536 points [cite: 6].

### 5.2 Elkies' K3 Surfaces and Stoll's 642-Point Record
To systematically generate genus-2 curves with many rational points, Noam Elkies utilized the geometry of **K3 surfaces**. Elkies started with a K3 surface $S/\mathbb{Q}$ whose Néron-Severi group has the maximum possible rank over $\mathbb{Q}$ (rank 20) and discriminant $-163$ [cite: 6]. He modeled $S$ as a double cover of $\mathbb{P}^2$ branched along a sextic curve $C_6$ that possesses over 50 tritangent lines. Restricting to generic rational lines in $\mathbb{P}^2$ yields genus-2 curves $C_L$ that automatically inherit many rational points from the intersections with the tritangents [cite: 6]. 

Using this framework, Elkies proved unconditionally that $\limsup N(2, \mathbb{Q}) \ge 150$, meaning there are infinitely many distinct genus-2 curves over $\mathbb{Q}$ with at least 150 rational points [cite: 6].

In late 2008, conducting a massive systematic computational search through the rational lines of relatively small height within Elkies' K3 families, Michael Stoll discovered the current reigning champion [cite: 11, 28]. Stoll's genus-2 curve is given by the equation:
\[ y^2 = 82342800 x^6 - 470135160 x^5 + 52485681 x^4 + 2396040466 x^3 + 567207969 x^2 - 985905640 x + 247747600 \]
[cite: 28, 29]. 

This curve holds the record with at least **642 rational points** [cite: 28]. The Jacobian of this record curve is highly complex; assuming the Generalized Riemann Hypothesis (GRH), it has a Mordell-Weil rank of exactly 22 and trivial rational torsion [cite: 30, 31]. 

Stoll's 642-point curve serves as the empirical lower bound for the Bombieri-Lang/CHM uniformity constant in genus 2: $B(2, \mathbb{Q}) \ge 642$.

## 6. The LMFDB Genus-2 Landscape and Computations (2025-2026)

While finding extreme records highlights the capacity of genus-2 curves to harbor many points, a central mission of modern arithmetic geometry is to systematically classify curves and definitively compute their sets of rational points. The **L-functions and Modular Forms Database (LMFDB)** has become the definitive computational repository for this endeavor [cite: 2, 14]. 

As of 2025-2026, the LMFDB features an exhaustive and expanding catalog of genus-2 curves, their Jacobians, and their L-functions, heavily emphasizing explicit verification of BSD and the determination of rational points [cite: 2, 32].

### 6.1 Traditional Chabauty-Coleman and the Rank Barrier
For decades, the primary algorithmic tool for computing the exact set $C(\mathbb{Q})$ has been the **Chabauty-Coleman method**. By embedding the curve into its Jacobian via an Abel-Jacobi map, one considers the $p$-adic closure of $J(\mathbb{Q})$ inside $J(\mathbb{Q}_p)$. 

The method succeeds if the Mordell-Weil rank $r$ is strictly less than the genus $g$ [cite: 20, 33]. For $g=2$, this means the Chabauty-Coleman method is only effective when $r = 0$ or $r = 1$ [cite: 20, 34]. When $r=1$, there exists a non-zero regular differential annihilating $J(\mathbb{Q})$ under the $p$-adic integration pairing, and its zeros on $C(\mathbb{Q}_p)$ bound (and usually exactly pinpoint) the rational points $C(\mathbb{Q})$ [cite: 2, 20]. 

However, if $r \ge g$ (i.e., $r \ge 2$ for genus 2), the traditional Chabauty-Coleman method fails entirely because the $p$-adic closure of the rational points becomes dense in the local points, yielding no bounding differentials [cite: 20, 33].

### 6.2 Minhyong Kim's Non-Abelian Chabauty
To breach the rank barrier, Minhyong Kim developed a profound generalization known as **Non-Abelian Chabauty** (or Chabauty-Kim). Instead of just using the Jacobian (the abelianization of the fundamental group), Kim's program utilizes higher unipotent quotients of the fundamental group to construct a sequence of nested varieties:
\[ X(\mathbb{Q}_p) \supseteq X(\mathbb{Q}_p)_1 \supseteq X(\mathbb{Q}_p)_2 \supseteq \dots \supseteq X(\mathbb{Q}) \]
where each depth incorporates deeper iterated $p$-adic integrals [cite: 32]. Kim conjectured that for $n$ sufficiently large, $X(\mathbb{Q}_p)_n$ is always finite [cite: 32].

### 6.3 Quadratic Chabauty in the LMFDB (2024-2026)
The first computationally effective depth of Kim's program beyond the abelian level is depth 2, known as **Quadratic Chabauty**. Developed extensively by Balakrishnan, Dogra, Besser, Müller, and Bianchi, Quadratic Chabauty exploits $p$-adic heights and Selmer varieties to compute the set $X(\mathbb{Q}_p)_2$ [cite: 7, 35]. 

Crucially, Balakrishnan and Dogra proved that the Quadratic Chabauty set $X(\mathbb{Q}_p)_2$ is finite provided that:
\[ r < g + \rho(J) - 1 \]
where $\rho(J) = \text{rk}(\text{NS}(J))$ is the Picard number (the rank of the Néron-Severi group of the Jacobian) [cite: 32, 33].

For a generic genus-2 curve, $\rho(J) = 1$, so Quadratic Chabauty works when $r < 2 + 1 - 1 = 2$, which does not advance beyond the classical bound. However, for **bielliptic** genus-2 curves—curves that admit degree-2 maps to elliptic curves—the Jacobian is isogenous to a product of two elliptic curves $E_1 \times E_2$. This split structure implies that $\rho(J) \ge 2$ [cite: 7, 35]. Thus, for bielliptic genus-2 curves, Quadratic Chabauty is guaranteed to be finite when $r < 2 + 2 - 1 = 3$, successfully breaking the Chabauty-Coleman rank barrier by solving the $r=2$ case [cite: 33, 35].

#### Recent 2025-2026 Computational Achievements
In a massive computational thrust leveraging the LMFDB, researchers including Francesca Bianchi, Oana Padurariu, and Kate Finnerty have successfully deployed Quadratic Chabauty across hundreds of rank-2 genus-2 bielliptic curves [cite: 32, 35]. Their work marks a historic milestone in algorithmic Diophantine geometry.
*   **Methodology:** The algorithm constructs a finite set of $p$-adic points $\Omega$ by computing local height contributions at bad primes and determining a global function $\tilde{\rho}$ such that all true rational points map into $\Omega$ [cite: 32]. A "Mordell-Weil sieve" is then used to filter out "mock rational points"—$p$-adic points that mathematically belong to the Quadratic Chabauty locus but do not correspond to global rational points [cite: 32, 35].
*   **Modular Curves:** The 2025-2026 experiments heavily targeted bielliptic modular curves of genus 2 added to the LMFDB. Notable examples evaluated included the non-split Cartan modular curve $X_{ns}^+(15)$ and the split Cartan curve $X_s(13)$ [cite: 32, 35]. By running Quadratic Chabauty over both the rationals $\mathbb{Q}$ and quadratic imaginary fields (where the rank may increase), the researchers successfully determined the full set of rational points for 411 locally solvable rank-2 bielliptic curves in the LMFDB [cite: 7, 35].
*   **Mock Rational Points and Algebraic Irrational Points:** An unexpected and fascinating discovery from the 2025/2026 runs was the precise nature of the "mock rational points." In several cases, points in the quadratic Chabauty locus that were sifted out by the Mordell-Weil sieve were observed to be genuine *algebraic irrational points* defined over specific number fields (e.g., quadratic or biquadratic fields whose discriminants divide the level of the modular curve) [cite: 7, 32]. This has spawned new conjectures connecting the level of modular curves to the specific number fields where these "mock" points natively reside [cite: 32, 36].

## 7. Synthesis: The State of the Art and Bounds Achieved

To summarize the landscape of rational points on genus-2 curves at the conclusion of 2025-2026:

1.  **Uniformity (Theoretical):** The DGH bound securely roots the maximal number of rational points to $c^{1+\text{rk}(J(K))}$. The structural rigidity predicted by Bombieri-Lang and Caporaso-Harris-Mazur remains unconditionally robust in the bounded-rank regime [cite: 3, 5].
2.  **Uniformity (Average):** Thanks to the integration of Bhargava-Skinner-Wei Zhang's arithmetic statistics and Alpoge's stratification techniques, we know that the *average* number of rational points on genus-2 curves (with a marked point) is strictly bounded. The vast majority of genus-2 curves exhibit behavior deeply suppressed by their geometry [cite: 1, 21].
3.  **Maximum Bounds Achieved:** Michael Stoll's optimization of Elkies' K3 surfaces preserves the all-time record of **642 rational points** on a genus-2 curve over $\mathbb{Q}$. This absolute lower bound for $B(2, \mathbb{Q})$ showcases the extreme computational limits of highly symmetric, high-rank configurations [cite: 28, 29].
4.  **Algorithmic Triumphs (LMFDB):** The computational front has advanced dramatically. The previous theoretical blockade of $r \ge g$ has been fundamentally bypassed in special cases. Via Quadratic Chabauty, we can now routinely and algorithmically compute the exact, finite set of rational points on rank-2 bielliptic genus-2 curves. The massive ingestion and processing of these curves into the LMFDB represents a democratization of Kim's non-abelian Chabauty, shifting it from a theoretical breakthrough into an applied computational workhorse [cite: 32, 35].

## 8. Conclusion

The pursuit of understanding rational points on genus-2 curves encapsulates the grand trajectory of modern number theory. It began with the non-effective topology of Faltings' theorem, transitioned into the abstract uniformity of Bombieri-Lang and Caporaso-Harris-Mazur, was refined into the probabilistic reality of Bhargava's arithmetic statistics, and is now culminating in the explicit, point-by-point algorithmic certainty of the LMFDB's Quadratic Chabauty pipelines. 

While an unconditional, effective global bound $B(2, \mathbb{Q})$ may still remain beyond immediate reach, the convergence of statistical bounds, structural theorems like DGH, and the brute-force algebraic mastery displayed in the 2025-2026 computational results suggest that the complete arithmetic behavior of genus-2 curves is rapidly becoming fully classified.

**Sources:**
1. [alpo.ge](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9daoXvrt7LFFfirCvMveM-MMpDcEO8MvCp5j7Zl6EpUVyxxzui_WFpQtuawJJUUCZzEVVwPSVRHb4VhD1AZBGHIa_DUipiPtmDCOP6gLe4Q20gkVNbi-_y-6BxI2xs_cEsDK6WmWmDWHFF6WoH89FYhCE0TEozUkL2pvCZKB3EGiF_gGwcvwTU8Gb1Y1QtZ-9Jt6c9uj_zZvyQzWsy36dyJWYbucdCYLaZNs=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbWZOSr4VTGuYPpLC6uZY4xMPKuw3S4lcWGoMUdN9t2upWfsP4K7TB30Rb7XUUqPClEu4wfl2zGQ0BMySydCtzs8IFp5BkTIZGG0znzP3xxUhhD1vCKw==)
3. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ210bkwfDTqa4q0HNzY9VR3ujDaGdkFLTnESjd_EMArPci4kvamfE8W_puzvIf8sE2SkNtvx0PJjcDB-w-C0nzexbs1Rz_dqzr_dwqbqcTwcgS-G_WbR65wVaMgwqNVf3c-I1EtQ=)
4. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH282PJV5hIXrUfOVwY2RRkYGI2TqOPCdaeDG_oo9OG7al9bA6rMliVYfbEwPmB4wwAoLFzHrm87zSYcsqCkkxJAjrR5q8Om3FL5fQpJzIwoVj4Qrctt4hiAFPMdy3PUTATzasVjpVFuRhmZv2ttMza)
5. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2596ho--OEG1zIhpFbsbfGbfCoGrigcAGQLzpeecD-MardN0TqQ7ZI-Bk3nRiEK4BoIl4rDb_Sy0rIEUp8sOGn8ocJMasYDolrL3DuDJiVQV3g4LP3EOFCwujK1Z6Kooq8pQWxdbH2Q==)
6. [antsmath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR6RZPPDGUSMYXRmFnEfvCzhyonoMG_UrHm0bVNiBSQ-w22ytOrOZV6Fc_JDa3vHAilucfRrJchgtp0fzJ8yXVCjJxzhE0N4soONiAwPcMdeO7-NJU3IgQkHnG77AHAuyQrPnS)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7kdpOs_lCtXAfwClFjo_K1IOIFGkZWMOFnjHDBu6IjzJDfLXcTPoo7F0PSlq0ZHijZIgFWFiGMfq5A0cUrYOsQ0waQlkm7_wUeiYSTqJpXWOjYTTi3Gxs_Q==)
8. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJyEA9fVwRNxRcRAwkhNggZY8HgM4k7yqH6uh8bGltueLCVB6Skv3fjQJgN0jzHwlgd1rx_Rl-cRHkbQsFIBrT_1u72i1GD1kn9Ri9BeWTOa1piNJiqqckyZ7KTW1wa-qZ5llgl_Jb4axHEfTOLUL5s5YED48HjP1lTXsB86JChLDt)
9. [sns.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgg0iUu0dpjmiVZo_KBiq9a90YnMyx65oxpPGz1xEBITixZtxK2cArN9UT9aB6El8OZ0vZepUIpVAR4UV5gb2nHeAuGc1SVCSg5xGUB73dJWAyL0TDzcF9E2_fuXILJ1d7ZNMAjRb4Prf9X7dTyvBihcL8x6wwVEEL9FCdoWFm3duesgCIKauThGtzQD2rPpj8C_6XkDba91MB7_4Olwz0pV6UjrBmgxDt861Duy4UboJ7lodhm68tqkJggWlurJHLoF6FzMcuUsz3M_KFNYOpRZ1riA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRzVgtNTGxvd0b3J-oee_9CFb70BZPngaxyYvMwHlcHwJqwslM3OHsU1UZqlaqqJ4q5q6l4gtP6dg13KBGIQFmCF6EUKKGION01ln7B5Cu9AWtp80CNA==)
11. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBigc225G0IAnWyRmDi8LpUueT0Vn0btKej97lV9z--KTKeVQyOItAzOPa620wGPlwIo7ZbuddM-WkCJAg3tt3U09w6zLDKBYnV10wIiyI50gB8cGP488WaCZ4vRj5awfrW0h5hJx_WdcBl5qV4WIwQRc-rT5HQx8hGmN_OmhplvXMKJYLsAO6jcVsyz7YfFUc9-_prtOtXTjnd3cQPNTssA82V2xkSDpw14jAyVLngA==)
12. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFT9bVwEBEfTMSkj6vrTuQx2hHR5BYnjMp3n9EX8Tkbk-2BndUxY7s_3fkXRbWH7duSr0GwfLePTpbqxsqiaUXRs9uhgn1MU8SjwZqUzv54Xikj2POZDIAniREeMaSg03BrFo-aTq5SLA==)
13. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW_CICcnN_NVZYfdxz4CY8yUBS1GApZhnEi1D9A_kFMvsT_30LPi0RWaFRFMWTIod6FEpytI-h3rhOJxNHn_YrknYmCMqCbJHT39uFM1vi6A59duILH9h_0o_MTAGRTQP0aM64o9ZLreAfeH8hp98LpTsxxVXvzkeMnQY=)
14. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGURztILVdT7s9bHCoHEyc-PkR-rDzig7Wqsp_g5KTY2Mo_afo9KyA_GNWvzLXhYEodWvHlc6j8PwZr3r9g_YNMZ0k7RY592MbgCuGyN_IF31gV8h6mpxeGRJZsPlE1)
15. [lsu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFanFkemzRamPjSsDdGCA4U7pNbtSTPA98d4MFyiPWxih09vDYytQIqpn8FqAx6EwSG8cYLnW5ZM-m3c-2Xro1JBTOcu_HAApPV_rQygTohl305DjQTcCWZWSi5O8q9kBJ8fqk388kPRAB_lapW)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnV6kMvP8MGLtlChbHsMIlTNwhG6n8XGpJ_Z1AlBEL2HUkEXi6cL7NTxus6OfeSvxf6AUnnpQz810uHQRRhDlNM_IcHBovOXNXq0pOWFmYtBylfqFvGQ==)
17. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzJgl0kMeRPTOZrS5FaV53tXwAis241hP3U_7e_u_EA6QRigZxCS6tzQ7QfusO2ez8PhNLMkhPPy6m8SOJQu4wRQ8P6XiySIwNtWcHCJDdYmIm0pqdd3vDMg1yYylQb7G6-CUm_T4rcdtC)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHep6Z4PsZ639mfyFOAnXAJAQUdcrPIWTpP8-Z8UgeXtMlDMxyEzcmDnobsL6sq2JzKLQVC3siD_vZXAogWYs2G6gXHlbLjZ1L4AjJ0eMUEpyn2pMEaHQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGt4MREn-FK5POMz8Lea9tUxRTMnZ9FQ4jzS3GlexY68C2NlnQkM9bSPlHPQmUuZ8CKzEl4CqODZQCxqt6ogBFLU5o16SN7fIMPVm5o5gxM0ttMrAIY)
20. [mfo.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZewA5dbY20nGYPSioZz5Sn8QsU90bik1zsrf5gXDb_ehT0ojZByrHhdPL2C_D9yHpexeAKr1tA4PgKKdPJEnQvBc3nLM-Ok9V1W1gvKWE6RcOMwmkYH8EEcExn6M_a08qaNvQgSEwsT7SMOnhHAkLMj-YNmwvXDJfHzXGuVDBYb67hVGyU6-yL2pvYTdNtqQsow==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuRR3MyYAwRPtSaecAuSNrQnhx5lalII2FLJ3fvntzDGvc9nNc7OLqZ5_Y3jtRCHwgnNYGE0STwgFUe_2NulUeLA5WxWIqMbm66pwStWve0Y1oYi9q9g==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtp4MkCrPyxGojNbTWHTUqSme_FAV1YVCl6ug3ZizKW9Utz0xWKMouU_xrAbqQeV4Hzstumgu9kFFwD5cbILEbQuUlsgW3izNd3dlv58VcFMS2qhtqou1TMfZdmQfld6DXn3wHc1-3QtJdYlh-AqanYpyq6IfDUSRtooSX3i-qbF1-tBc=)
23. [risat.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnfYcIiGqn-8i4D1PZdMM1z8sK-b62oqxjOniYXU2EW1ixQr5PdLd_b2FONl6ITEJd3DvuQOm2AIH71xBXrPXaBsSyXMO4NQaskYIZJwt-b2vaawrX5FDO2PA=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqH-B4ptIUpuCk6kh8E4jary3Bv9ImLjUOrkHbb4XK5FliTkqODAd-kj2bn9XXjmsM6EbZvWoZNvKuaIdtM9JVdUDmqtRZ1-e_KFl1-jXr7L7Aa9nj0HFl)
25. [risat.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4sCHWppKy83P5SlKy8hkCLZcppAGFc3ok4hYmWS15yD0shdRYGCCeuExQzB9xlBswf7K_DC2bEb-dkf1_Gaak33S-tRiPcfPL6fVtN9ApoE7bhrEPwXK7PCM=)
26. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIhtYqn9V1urbmTZ9DlcpkSzyArvLRQiJXRrcUEaSOWY9uDaGxz1hl_AXrhYB9Bvl4Mb8sICghJkDp2wqxjdkhC5qFQk0T4Vp20ARDzi_VndfsgIvmev5GKDThWTGMuHQM4qw=)
27. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKM7tTMrMdqkWipBLe_jHWKoAoEkcv3Hbiw68d7UR7ZS2YTCP4PXFAjHLautp7ObsCaets9cVqHrK0rmutRrCTNbYrJRBc6powIU-6NYhX0DS1CU_5WoMjqtZ9xNr09Bnx6NE4Bis_GSFXpw==)
28. [uni-bayreuth.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfiWSST73j_29F_tmVyG3QcrbvRQSsf0OK3R-wviXCrbZ8rpviUao9RNoN9e1fcAZ7gy7pLQ-C2f-pPP52iTmTso8F9eJngXdGRFUoq9U9B2mg2ju348pTS13bmz7Uz0qmtSsr-nAFsa_NOA==)
29. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWM4Y3kfSotp8es89egmsYwQkT3kupt8hqcWU_eJQjJuyNElsM1Ub7z_BOFNJj-QC3IHw0hahAON-xQlT5AowFyvKLkVyZw-okkk2lNSswoxXg05rbVL51bV_jeSTqc80rZ8FaYWP0QFWevxn85yxP1D-HBaDBr9z_UPR0QaUw9RjuA9grQuqIPPjpBIoyQHpPEv04gJLZvV1RD2G31afgI-D-xwhoAkL799sENQ==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGTTueVWbVPWl1gXaeUUNqC8YB4XtRR9K9V5DJigUZDT80wv9BzSkbv69BIUs4DKNi7Golt-CB5tMrbIpLOlwviHRUAynQJkvCN56Zm9qGxd5XHrdF7w==)
31. [bris.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGW2KjkvgcX9FoS6ODvEMciuSiqFVK5HRsq4ZmPWU1QNsQthSx7Wrq7sec-m770a97Vx0Z0cH26C_rSHcNxthrUlohMv95LRerXdnK1Kiw7EC96MYepAi6TtUqCda3arKt3mZ5KR4C-UGpl0JMh9A4ZVNCPBCwRyElcRPSA9uBGIgX30tpOSSOTZV8EvYZ9VL8Braol32iUY2octeHof_NnYD15lPTDPOQOu3akaeYuWOzPqxVwHPcLWVmX97U8izGI)
32. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5_gcRmj7Ufy9NoAVeCObe2jbUble2kBoiVBOHbzzIshaQek3kBTw5T_X1yAUpOM-dNKVJ_0vRhicnQ3rCCqiY9R3X9Rw_SJk1rrwh92t8wQIkg0Gqx6U2HnqortlZnsYFNYndqD2BlVLVPY86b04hgrCQTtkfpmvdRvlpMBb87F3a9Oaqq3jmbrjFRg==)
33. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFQbV4-vSQ9d2u16yT1Sn8aBrhY5uFHDIXZj5S0VgXurXXGgp9K3Ke6wGKoLhz9TJb2JMb66ca5pjupuow8WaKbGu82-vaKeIHKhXY_nkfF68qwHYaF5tQz4qrLWnG5Huy76G_5nWeWw==)
34. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG0VTt61lCz6qhxfM4KdKtj1RzedTd5HlNwEnxnYBqB3hckCzwmnH4hhB4Xm6abKnZOqNJvrnOCdXL6WC6gCnm8qdJGDinzMCXm9E2xsZg8npyWu42nKMIBgsjEdhE86c058mrRJQa7qxH3gQ4L6E=)
35. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7ylPSWlBOxtRYNQh7OW_pwlU1iFmIpAhDsWK1MyBUreCJdE0T1Ysh17vCMVymN4D6pFmi3fJuUjjYvhZu46TRgGflx2qduueoK57xxDmVHz8g1yMdO2rwR0kH8USjx2HrFeIuvQxS5W2cJRtanBjj7d9weMYlrjZEJjJDnREh1DGWDNowgkboLbkTCDFIcW1zagYzdb8k0EKYCxhO04DTixnTmX77hkSe_YSQ0b_OX49FGHrGb_y-Vao=)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7ETgRePWxtHf8hla7OYfPTNfz6TjmmLod_qRZ-fvwn50y9Z5z9SzGbSGU2Ze6nsmkrNwK-5EPzDS5ZedUwyXZn7taiNmiCwCpHL8Cgq6DfOt9dxd8uw==)


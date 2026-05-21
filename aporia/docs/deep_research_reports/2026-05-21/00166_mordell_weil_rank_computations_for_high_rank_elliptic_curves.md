# Mordell-Weil rank computations for high-rank elliptic curves 2024-2026 (Elkies)

**Pythia queue id:** 166
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdaamNQYXZYUkVyZWtfdU1QMzVHNmtBOBIXWmpjUGF2WFJFcmVrX3VNUDM1RzZrQTg
**Elapsed:** 249s
**Completed at:** 2026-05-21T16:52:48.522532+00:00

---

# Mordell-Weil Rank Computations for High-Rank Elliptic Curves: Developments from 2024 to 2026

**Key Points**
*   **Recent Discoveries:** In August 2024, mathematicians Noam Elkies and Zev Klagsbrun announced the discovery of an elliptic curve defined over the rational numbers with a Mordell-Weil rank of at least 29, breaking an 18-year-old record.
*   **Methodology:** Evidence suggests that the curve was found via a sophisticated sieve search on a rank-17 elliptic fibration of a K3 surface, identifying 12 additional independent rational points.
*   **Theoretical Impact:** While folklore conjectures traditionally proposed that elliptic curve ranks might be unbounded, contemporary heuristics (such as the Park-Poonen-Voight-Wood model) suggest that only a finite number of curves exist with ranks greater than 21. The discovery of a rank-29 curve provides crucial, though limited, data for this ongoing debate.
*   **Conditional Proofs:** It seems likely that the arithmetic rank of this new curve is exactly 29, provided that the Generalized Riemann Hypothesis (GRH) and the Birch and Swinnerton-Dyer (BSD) conjecture hold true.

**Overview of the Rank Problem**
The study of elliptic curves over the rational numbers ($\mathbb{Q}$) is one of the most profoundly investigated areas in arithmetic geometry. According to the Mordell-Weil theorem, the set of rational points on such a curve forms a finitely generated abelian group. This group consists of a well-understood finite torsion component and a free abelian component defined by an integer known as the "rank." The rank essentially measures the number of independent infinite-order rational points required to generate all other infinite-order points on the curve. Despite a century of study, it remains unknown whether the rank of elliptic curves over $\mathbb{Q}$ can be arbitrarily large or if it is strictly bounded by some absolute constant.

**Recent Breakthroughs**
For nearly two decades, the highest known rank for an elliptic curve was 28, a record established by Noam Elkies in 2006. In August 2024, Elkies and Zev Klagsbrun pushed this boundary further by discovering an elliptic curve with a rank of at least 29. This breakthrough was achieved by re-evaluating the K3 surface used in the 2006 discovery, utilizing advanced computational sieving techniques to scan tens of trillions of parameter specializations. Furthermore, ongoing research extending into 2025 and 2026 explores the implications of this discovery against probabilistic models of rank distribution, alongside broader generalizations bounding Mordell-Weil ranks in higher-dimensional Calabi-Yau varieties.

---

## 1. Introduction to Elliptic Curves and the Mordell-Weil Theorem

An elliptic curve $E$ defined over a field $K$ (such as the rational numbers $\mathbb{Q}$) is a smooth, projective algebraic curve of genus one, equipped with a distinguished base point $\mathcal{O}$, which acts as the identity element. For curves defined over fields with characteristic neither 2 nor 3, the curve can be represented by a short Weierstrass equation:
\[ E: y^2 = x^3 + Ax + B \]
where $A, B \in K$, and the discriminant $\Delta = -16(4A^3 + 27B^2)$ is non-zero, ensuring the curve is smooth and free of self-intersections or cusps [cite: 1, 2].

A fundamental result in the arithmetic of elliptic curves is the **Mordell-Weil Theorem**, originally proved by Louis Mordell in 1922 for the rational numbers, and later generalized by André Weil for abelian varieties over general number fields [cite: 3, 4]. The theorem states that the group of $K$-rational points on $E$, denoted $E(K)$, is a finitely generated abelian group. By the fundamental theorem of finitely generated abelian groups, $E(K)$ decomposes into the direct sum of a free abelian group and a finite torsion group:
\[ E(K) \cong \mathbb{Z}^r \oplus E(K)_{\text{tors}} \]
Here, $E(K)_{\text{tors}}$ represents the finite torsion subgroup (points of finite order), and $r$ is a non-negative integer known as the **Mordell-Weil rank**. 

The torsion subgroup over the rational numbers is completely classified by Mazur's Torsion Theorem (1977), which states that for any elliptic curve $E/\mathbb{Q}$, $E(\mathbb{Q})_{\text{tors}}$ must be isomorphic to one of the following 15 groups:
*   $\mathbb{Z}/m\mathbb{Z}$ for $1 \le m \le 10$ or $m = 12$
*   $\mathbb{Z}/2\mathbb{Z} \oplus \mathbb{Z}/2m\mathbb{Z}$ for $1 \le m \le 4$ [cite: 4, 5].

Unlike the torsion subgroup, the rank $r$ is not definitively bounded by any known theorem. The computation of $r$ for an arbitrary elliptic curve is notoriously difficult, primarily because there is no known universally applicable algorithm guaranteed to terminate and compute the rank unconditionally [cite: 4, 6]. Methods such as $n$-descent (typically 2-descent) rely on computing the Selmer group and the mysterious Tate-Shafarevich group ($\text{III}$). 

## 2. The Boundedness Controversy: Heuristics and Conjectures

One of the longest-standing open questions in number theory, originally rooted in queries by Henri Poincaré, asks: *What are the possible values for the rank $r$ of an elliptic curve over $\mathbb{Q}$?* Specifically, is the set of all possible ranks bounded above? [cite: 4, 6].

### 2.1 The Folklore Conjecture
For many decades, the "folklore conjecture" in the mathematical community posited that ranks of elliptic curves over $\mathbb{Q}$ were unbounded [cite: 5, 7]. This belief was primarily driven by the historical trend of steady discoveries: mathematicians continually found curves with higher and higher ranks by utilizing geometric structures such as elliptic surfaces and K3 surfaces [cite: 1, 8]. If one could construct a parametric family of elliptic curves with an arbitrarily large generic rank, specializations of this family would yield curves over $\mathbb{Q}$ with arbitrarily large ranks.

### 2.2 The Park-Poonen-Voight-Wood (PPVW) Heuristic
The prevailing folklore was significantly challenged in recent years by probabilistic models. In 2019, Jennifer Park, Bjorn Poonen, John Voight, and Melanie Matchett Wood published a highly influential heuristic arguing that the ranks of elliptic curves over $\mathbb{Q}$ are, in fact, bounded [cite: 3, 7]. 

The PPVW heuristic models the ranks and the Tate-Shafarevich groups of elliptic curves simultaneously by examining alternating integer matrices [cite: 4]. By statistically modeling the distributions of the Selmer groups, the PPVW heuristic suggests that curves of rank $r$ become exponentially sparse as $r$ increases. Their precise heuristic prediction is striking: there should only be a *finite* number of elliptic curves defined over $\mathbb{Q}$ with a Mordell-Weil rank greater than 21 [cite: 4, 9]. 

This heuristic does not prohibit the existence of curves with rank 28 or 29; rather, it suggests that such curves are exceptional outliers—part of a finite list of extreme anomalies [cite: 4]. When Elkies and Klagsbrun discuss their record-breaking searches, they note that the immense computational effort required to find even a single curve of rank $>28$ provides "at best, limited evidence that ranks are unbounded" and may actually signal that "the growth of ranks of elliptic curves might indeed peter out at some point," acting consistently with the PPVW heuristic [cite: 10].

## 3. Computational Geometry: Slicing K3 Surfaces

To hunt for elliptic curves of exceptionally high rank, brute-force searching through arbitrary coefficients $A$ and $B$ is futile. The probability of randomly selecting an elliptic curve of rank $>3$ is vanishingly small; the average rank of elliptic curves is rigorously bounded above by $7/6$, with half expected to be rank 0 and half rank 1 [cite: 7]. Instead, mathematicians use the rich geometry of algebraic surfaces.

### 3.1 Elliptic Fibrations over K3 Surfaces
The predominant method for constructing high-rank elliptic curves relies on mapping out an **elliptic surface**, specifically a **K3 surface**. A K3 surface is a simply connected, compact complex surface with a trivial canonical bundle. Certain K3 surfaces admit an *elliptic fibration*, meaning there is a surjective morphism $\pi: X \to \mathbb{P}^1$ such that almost all fibers are elliptic curves. 

By the Shioda-Tate formula, the Mordell-Weil rank of the generic fiber $E(K(t))$ of an elliptic surface $X$ is intimately related to the Picard number $\rho(X)$ (the rank of the Néron-Severi group) [cite: 8, 11]. For a smooth K3 surface, the Picard number is bounded above by 20. Through careful construction, one can find a K3 surface whose elliptic fibration possesses a highly populated generic rank [cite: 11, 12].

### 3.2 The Sieve and Specialization Strategy
The search strategy employed by Elkies and Klagsbrun relies on "specialization." If a K3 surface has an elliptic fibration with a generic rank $r_{\text{gen}}$, then by Silverman's Specialization Theorem, for all but finitely many rational parameters $t \in \mathbb{Q}$, the specialized elliptic curve $E_t$ over $\mathbb{Q}$ will satisfy:
\[ \text{rank}(E_t(\mathbb{Q})) \ge r_{\text{gen}} \]

To find curves with rank strictly greater than the generic rank (a phenomenon known as rank jumping), mathematicians must sift through millions or trillions of parameter values $t$. Elkies utilized a specific K3 surface that admitted a fibration with a generic rank of 17 [cite: 13]. This means that every non-degenerate slice of this surface is mathematically guaranteed to produce an elliptic curve of at least rank 17 [cite: 1]. 

To detect rank jumps efficiently without computing the full rank for every specialized curve, computational number theorists employ heuristic sieves based on the Birch and Swinnerton-Dyer (BSD) conjecture. By computing the $a_p$ values (trace of Frobenius) for small primes $p$, one can approximate the local analytic density of points. Curves with anomalously high sums of $\frac{a_p}{p}$ are flagged as candidates for high geometric rank and undergo rigorous independent point searches using software like Magma or PARI/GP [cite: 6].

## 4. Historical Progression of Rank Records

To fully appreciate the developments of 2024-2026, it is necessary to contextualize the progression of rank records over $\mathbb{Q}$.

| Year | Mathematician(s) | Lower Bound on Rank | Note |
| :--- | :--- | :--- | :--- |
| 1989 | J. F. Mestre | $\ge 15$ | Used elliptic surfaces. |
| 1992 | K. Nagao | $\ge 19$ | |
| 1993 | S. Fermigier | $\ge 20$ | |
| 1994 | K. Nagao | $\ge 21$ | |
| 1997 | S. Fermigier | $\ge 22$ | |
| 1998 | R. Martin & W. McMillen| $\ge 23$ | |
| 2000 | R. Martin & W. McMillen| $\ge 24$ | |
| 2006 | Noam Elkies | $\ge 28$ | Found via K3 surface specialization. |
| **2024** | **Noam Elkies & Zev Klagsbrun** | **$\ge 29$** | **First break of the record in 18 years.** |

[cite: 3, 5].

### 4.1 Elkies' 2006 Rank 28 Curve
In 2006, Elkies sliced a K3 surface of generic rank 17 to find a parameter that yielded 11 extra independent rational points, generating a curve of rank $\ge 28$ [cite: 1, 13]. The equation for this curve was:
\[ y^2 + xy + y = x^3 - x^2 - 20067762415575526585033208209338542750930230312178956502x + 34481611795030556467032985690390720374855944359319180361266008296291939448732243429 \]
Assuming the Generalized Riemann Hypothesis (GRH), it was later proven by Klagsbrun, Sherman, and Weigandt that the arithmetic rank of this curve is exactly 28 [cite: 3, 14]. Following this 2006 discovery, the mathematical community largely anticipated a steady march of subsequent records. However, an 18-year "drought" ensued, feeding the suspicion that perhaps an absolute bound was nearing [cite: 1].

## 5. The August 2024 Discovery: Rank 29

In late August 2024, Noam Elkies and Zev Klagsbrun formally announced the discovery of an elliptic curve defined over the rational numbers with a Mordell-Weil rank of at least 29 [cite: 10, 15]. This monumental achievement was presented later at conferences, including the Simons Collaboration on Arithmetic Geometry, Number Theory, and Computation's 2025 Annual Meeting [cite: 16, 17].

### 5.1 The Collaboration and Computational Method
The collaboration was rekindled in 2019 when Zev Klagsbrun—now a researcher at the Center for Communications Research in La Jolla—encountered Elkies at a conference. Having previously proved the conditional exact rank of Elkies' 2006 curve, Klagsbrun proposed using modernized, significantly more powerful computational architecture to renew the search [cite: 1, 18]. While Elkies' original search in 2006 could evaluate millions of curves, Klagsbrun’s optimized code and access to distributed computing power allowed them to sieve through tens of trillions of candidates [cite: 1]. 

Despite scanning trillions of specializations of the original K3 surface slicing, they failed to break the record for four years. The breakthrough occurred accidentally in 2024 when they discovered an alternative method for slicing the exact same K3 surface, resulting in a completely new pile of elliptic curves that were still guaranteed to have a generic rank of at least 17 [cite: 1]. 

By sieving this new family, they found a specialization in which they were able to identify 12 additional, independent rational points outside the fibration's generic $\mathbb{Z}^{17}$ subgroup [cite: 10, 13]. The combination of the 17 generic generators and the 12 specific generators elevated the curve's lower-bound rank to 29.

### 5.2 The Rank 29 Curve Equation
The specific elliptic curve, denoted $E_{29}$, has a trivial torsion group and is defined by the short Weierstrass equation $y^2 + xy = x^3 + Ax + B$, where the 60+ digit coefficients are:

$A = -27006183241630922218434652145297453784768054621836357954737385$
$B = 55258058551342376475736699591118191821521067032535079608372404779149413277716173425636721497$
[cite: 19, 20].

The curve's structural characteristics include:
*   **Conductor:** The conductor of $E_{29}$ is a massive number resulting from the product of 17 distinct prime factors, each with multiplicity 1 [cite: 10].
*   **Root Number:** The local root number is $+1$ at the prime 41, and $-1$ at each of the other 16 prime factors. Accounting for the root number at infinity (which is $-1$), the global root number parity is evaluated as $-1$. This is highly consistent with the parity conjecture, which dictates that an elliptic curve with an odd rank should possess a global root number of $-1$ [cite: 10].
*   **Canonical Height Matrix:** Klagsbrun and Elkies provided 29 specific, independent rational points. When processed via PARI/GP, the canonical height matrix of these 29 points evaluates to approximately $1.43 \times 10^{36}$, confirming their linear independence in the Mordell-Weil group $E_{29}(\mathbb{Q})$ [cite: 10]. The subset of points is saturated at least for all primes less than 212 [cite: 10].

To visually and mathematically verify the structure of such curves, computational checks ensure no three points lie on the same intersecting line without defining another rational point within the group structure. For example, tangency operations geometrically compound new rational points, demonstrating the lack of overlap across the 29 independent sets generated [cite: 20].

## 6. Conditional Proofs: The Role of GRH and the BSD Conjecture

While the construction provides 29 explicitly verified, independent rational points—guaranteeing that $\text{rank}(E_{29}(\mathbb{Q})) \ge 29$—proving that the rank is *exactly* 29 is unconditional only to a certain extent; an unconditional proof of the upper bound is currently out of reach. To establish the upper bound, mathematicians rely on two of the most profound open hypotheses in mathematics: the Generalized Riemann Hypothesis (GRH) and the Birch and Swinnerton-Dyer (BSD) Conjecture.

### 6.1 Arithmetic Rank under GRH
Using analytic methods originally formalized in their 2019 *Mathematics of Computation* paper (Klagsbrun, Sherman, and Weigandt), the team was able to tightly constrain the arithmetic properties of the curve [cite: 10, 14]. To bound the arithmetic rank, they calculated the 2-rank of the ideal class group of a specific cubic field $K_{29}$ associated with the 2-division field of the elliptic curve [cite: 8, 14]. 

The result establishes that, assuming the Generalized Riemann Hypothesis for the Dedekind zeta functions of number fields, the 2-Selmer group limits the arithmetic rank of $E_{29}$ to at most 29. Since 29 independent rational points are already known, the Mordell-Weil rank is confirmed to be exactly 29, subject only to GRH [cite: 10].

### 6.2 Analytic Rank under BSD
The Birch and Swinnerton-Dyer conjecture posits that the arithmetic rank of an elliptic curve is exactly equal to its analytic rank—the order of vanishing of its Hasse-Weil $L$-function, $L(E, s)$, at the critical point $s = 1$ [cite: 14, 15]. 

Klagsbrun and Elkies demonstrated that, assuming the $L$-function $L(E_{29}, s)$ satisfies GRH, the analytic rank of $E_{29}$ is at most 29. By incorporating the BSD conjecture alongside GRH, the analytic rank is forced to be exactly 29. Proving an upper bound for the rank of elliptic curves universally is intimately tied to solving the BSD conjecture, an achievement that would fulfill one of the Clay Mathematics Institute's Millennium Prize Problems [cite: 15].

## 7. Contextualizing Rank Records across Torsion Subgroups

While the absolute rank record receives the most public attention, arithmetic geometers are deeply invested in understanding the maximum possible ranks for elliptic curves constrained by specific torsion structures. Elkies and Klagsbrun have been at the forefront of this specific sub-field.

In their seminal 2020 paper at the ANTS-XIV symposium, "New rank records for elliptic curves having rational torsion," Elkies and Klagsbrun shattered multiple rank records for specific torsion subgroups [cite: 6, 11]. Utilizing K3 surfaces and specialized generic fibrations, they established new bounds:
*   For torsion $T = \mathbb{Z}/2\mathbb{Z}$: found a K3 surface with generic rank 9 [cite: 8].
*   For torsion $T = \mathbb{Z}/3\mathbb{Z}$ and $T = \mathbb{Z}/4\mathbb{Z}$: analyzed a singular K3 surface of discriminant $-163$ with a generic rank up to 5 [cite: 8, 11].
*   For the torsion group $\mathbb{Z}/7\mathbb{Z}$: they identified curves by cleverly managing 2-descent across cubic subfields of 2-division fields, despite the discriminant having degree 24 [cite: 8].

As of the 2024-2026 landscape, the state of maximum known ranks over $\mathbb{Q}$ by torsion subgroup reflects a gradient where larger torsion groups heavily restrict the available rank. For instance, the maximum known rank for an elliptic curve with torsion $\mathbb{Z}/2\mathbb{Z} \times \mathbb{Z}/8\mathbb{Z}$ is merely 3 [cite: 4]. 

## 8. Higher-Dimensional Varieties and Physics Connections (2025-2026)

The quest to bound Mordell-Weil ranks extends beyond 1-dimensional curves (elliptic curves over $\mathbb{Q}$) and 2-dimensional surfaces (K3 surfaces). Between 2024 and 2026, leading research has heavily targeted elliptic Calabi-Yau threefolds and fourfolds, motivated strongly by the physics of String Theory and F-theory [cite: 12, 21].

### 8.1 F-Theory and Supergravity Theories
In theoretical physics, an elliptic Calabi-Yau threefold $X$ can be used to compactify F-theory, yielding a six-dimensional $\mathcal{N}=1$ supergravity theory. The Mordell-Weil group of the elliptic fibration $X \to B$ dictates the continuous (free rank) and discrete (torsion) abelian gauge symmetries, typically modeled as $U(1)^r$ gauge factors in the effective action [cite: 12, 21].

### 8.2 Rigorous Bounds on Higher-Dimensional Ranks
A highly influential 2026 paper mathematically formalized and generalized the bounding of Mordell-Weil ranks on these higher-dimensional Calabi-Yau varieties [cite: 12, 21]. The authors utilized the effective boundedness of families of elliptic fibrations.
*   **Calabi-Yau Threefolds:** The authors proved explicitly that for an elliptic Calabi-Yau threefold with sections and singular fibers, the rank is bounded: $\text{rank}(MW(X/B)) \le 28$ [cite: 12]. Historically, the highest known rank for such a threefold was obtained via special Schoen manifolds with a rank of 10 [cite: 12, 21].
*   **Calabi-Yau Fourfolds:** For fourfolds, which correspond to four-dimensional effective field theories in string physics, the theorem bounds the Mordell-Weil group rank: $\text{rank}(MW(X/B)) \le 38$ [cite: 12, 21]. 

The proofs rely on demonstrating that the Mordell-Weil rank of an elliptic curve only increases upon base extension to a larger field, using Noether's formula and bounds on the Kodaira dimension ($\text{kod}(X) \le 0$) [cite: 12, 21]. These developments from 2025 and 2026 showcase how arithmetic geometry techniques developed by Elkies are being fundamentally translated into bounding dimensions in quantum universe theories.

## 9. Algorithmic and Machine Learning Developments (2024-2026)

In the ongoing efforts to compute and predict Mordell-Weil ranks between 2024 and 2026, machine learning and advanced data algorithms have begun playing a pivotal role. Due to the high computational cost of performing point searches and exact descents, filtering datasets of elliptic curves via artificial intelligence has emerged as a novel technique.

### 9.1 Murmurations of Elliptic Curves
A major algorithmic leap relates to the phenomenon of "murmurations" in elliptic curves, formalized in recent years by He, Lee, Oliver, and Pozdnyakov [cite: 1, 6]. Murmurations describe an unexpected oscillatory wave pattern observed when taking the average of the $a_p(E)$ values (the local trace of Frobenius) over a specific range of primes $p$, split by the rank of the elliptic curves.

Researchers mapping databases of curves observed that averaging $a_p(E)$ for curves of rank 0 versus rank 1 produces distinct, oscillating wave functions depending on the size of the prime $p$ relative to the conductor $N$ of the curve [cite: 6]. Machine learning algorithms trained on these murmurations have achieved unprecedented classification accuracy. For example, by choosing a prime cutoff $B$ at specific localized maxima (such as $B = 0.08N$), classifiers can correctly predict the rank of an elliptic curve (differentiating rank 0 and 1) with an accuracy exceeding 98.7% [cite: 6].

These machine-learning invariants drastically reduce the search space. Instead of sieving through purely random K3 surface specializations via brute-force BSD approximations, future search algorithms (heading into the late 2020s) are incorporating murmuration-based heuristics to flag highly anomalous curves that may exhibit extreme rank jumps.

## 10. Future Outlook and Conclusions

The discovery of the rank 29 elliptic curve by Noam Elkies and Zev Klagsbrun in August 2024 marks a historic milestone in computational number theory. It demonstrates that the frontier of the Mordell-Weil rank problem is still active, despite nearly two decades of dormancy.

However, the question of absolute boundedness remains tantalizingly open. The sheer difficulty encountered by Elkies and Klagsbrun—requiring trillions of specializations and yielding only a marginal rank increase of +1 over 18 years—provides sociological and statistical momentum to the Park-Poonen-Voight-Wood heuristic [cite: 1, 10]. If the PPVW heuristic is ultimately proven correct, discovering an elliptic curve of rank 30 or 31 might be computationally impossible if those finite, theoretically allowed curves possess conductors or coefficients vastly exceeding current computational capacities. As Klagsbrun noted, the discovery gives some hope for unboundedness, but "on the other hand, boy, it took a lot of work to find this one," heavily suggesting that ranks peter out [cite: 1, 10].

For the academic timeline of 2024 to 2026, the intersection of Elkies' classical K3 surface sieving, advances in theoretical physics bounding Calabi-Yau dimensions, and the introduction of machine learning via murmurations, paints a thriving portrait of arithmetic geometry. Proving the ultimate upper bound—or finding a definitive infinite family of high-rank curves—remains a generational challenge intimately tied to the Millennium Prize mysteries of the Birch and Swinnerton-Dyer conjecture. Until such a proof is formalized, the Elkies-Klagsbrun curve of rank 29 stands as the pinnacle of our understanding of rational point distribution.

**Sources:**
1. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnNihl9EF_siHOcHgtzADkzj7cq4I7Vjt_spRQR8Z3kHeVr-5md64Y6aK13sTGUQaPhAdXlRq4jaKJ-WMcMpICgfTlUW1E1m3F6JilOQsVjCzMLGrUizaf1tWUAMBPdntTcXUCqLBHW2CgRAOq_yFZC5uVmINlNZ34hfWQk2medzvewyRadW4jcc4t)
2. [quora.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGesCilCUojUiKxedLPEvdINnUwT3gYIYPIbeg9RCqGkEN_MiQOkbyk54XIF3FxyVsd1HYH3IRu6oo7hVO6-txQ4SpfCFhzbvYGpo2Tu6HFc34hdj0DEb7yVl_lpPTmQLSJe-iTn8Mt-tS9cj5b_5TmXxwkPobza9XUAY6muueqiPd7vviOy6mTkvcGOLQNpHmWXNxLF4UrBA9-GzxCsXgKM3jZgTeUpyNM_0OvOFJTT9HTonKETI2fEBFAnWw9uStHdLT1ghXQMLA=)
3. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq_tT9WP8O4_BA2uHbjTEtWh6xODRoswyXb7FjBLv3nZcEJPH18H7T6UywI_QuqFXeBqc-XGY09eHAMHsn-YBU0NIoT2OYqwZw_JkGa0uzacf0faToVKgc7FmoDubB6Zk04z_ahuyO8WW5aSC0)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAJ9K_sY5CWNdDu6GZPUSCfssmTxq8t9bCh5YPL3IN4UJNS-qDboH_VCxp47phun8urRmiv_xHjO3lZ1_DUUSds_PT83wj81LLuU1xvBGKhGv82TGdEw==)
5. [unizg.hr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtT1HcdDbjojFyEn5XPCMYi1VoZw-dgVVt7_gPjIEy4xxOv9S1yrNfu96lGzuHqscqzLLVvFsZFH19u4c1bYjKBCZozoPGvpX1Ppgb8o0rWt-pa2bnwK_C-ALlDL3nX89ZNmo7356ywQrvs9s=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRoCKQKfMOdW4wnI2LtVwJCpKUF1IN0uUrAc_--WG3vorEse_hyEAUpVqhpA1vyOhoLeenifvUOy-z52ceij6tBqvfJyqt--a4ufu1s_k9Fisz2y_bSQ==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5jBXfrO3GsFD2hzyY874bxnB2MsuEA0nBvdg0a8MkUBtCIq2CASkJHc4IUPf1kIdhFWNdnfvyERwrcsbOSnDXVcsv1Ivmsn8AKMiAU_Qi7EVJBnhtrg==)
8. [auckland.ac.nz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPuX85hT_ENt50EDg4fYyI21AcKC1sjZ6nmE52umsso5KX28H_cEp6KT5ctRWChzXseiFgY2dAFemDEmVXDEflNvSc2qbC5Z8IVqNfzckrhIQ_gl_xl107OZLYzj85nWBWA0Jlc_mhR6hCxZaRe-sx6F3tVOFsFD5IJKU6oEgw)
9. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQ7KyfZVDAb447BgJWBMvTClIAkz5yEnr_04cz7SS-OrVcb3F5HA7ABOD44uPYFv_bsCUQVTp1rXScvYVShY8GR-d1QFZLrBB3TfLYqgMAcXcmjlOkX8Tptu5Tf5j36O75zvvghlyY-uu6QJysTJGVMp8e)
10. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxDmRTo5XXOEjl1PkJT2bZmBlHG0l0G56Umj0WbDJp2vYDj6PuVJvtLvGSO8gdZJBcCvtmaLnLYGU00L1N9UqnO7ISNqrZc_sjy4wJmOVNn5I6TGYzB4IPDyZe8i1IvzfNMnjXrcyfZTtjmVMXqiiI03Q3tjK7Q6o0ELR2ututyfoEzPsh3rkZzjvAVpvrZBYlv5C2)
11. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTyF1vKBNgjnWs5PeNP6aiADgvC3czPg57jv1Esiowh1vgspPXS40zt4prljjWLwXTKY2ufqEpSTfjns_LUgGBlT9i3lYkwy6ycb3XJRWQT4PHrvMTmoqTZiLdggMlaocsyFtbZlQ=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJJoLO43lhVH67rszkpWcd52VPMG92vV3bMPIHtjg4utcdCEJlkG_wIzLH_vV6Re0B7k3NyRyWHbHNw52dMIdC0gncz_WAmZYH71GRaY_1ER6_yZEYYw==)
13. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ8e0jVk4VG0vClccj2rh-X8oHO1AO7J8jAmuvk7IEu2rpJqR3nu3F7sxX5Qth9xBNlJDwvbJuKdqvzoPth_RHLmswjEN5-oQqeeegqsrTt5KSO2Q2sxjUGo_jdUSkYG1iJb9SUUOWv_mFU00EI_cl5Nz2Cl_bchZTkCqnV3Qg4V1R)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhWDs0UcMPX_2fD3Vm9NxR5B2fgXh-HNXanxaNMaLf0qWLFH6LqcKGOT4OguTWCHZcAKyFLp4lJeSN119Pe4uQiXEvvBjJFz8KaWRatdxINbO5G79Yjg==)
15. [stephendiehl.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpTJoFircYEPC8Phwv_zhNLECa7YNwsefdXwOmGYp4ezWvySXQAezoEhZ4MPqVJK36L6xQk4TD9-j_sv4Bqp9BjX4RsLy5GjcOQxwR-HLsqQEKr_w1AbgO8p5STuJl6UxCWLZngRJcCwfY6QtzOLCY)
16. [simonsfoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4ghvR017LK8n1iK53OF-ddCa6obMfEoKvOTX5Bkj2BpTL7eSy3IfQugQTsg5_Tjls42OivhGiWygZ6NST_gR-9YejnrO928YHwAc5QrLkUDre3POnLeBJpdzBF0R4SDO_8x2eJhrLGvDjuWZxMVbog345PXxg459mz3moAaC3rnYdmfjP3AjBLuKSs-Sh4bZ0iLSQVlqv7qwP4khcE8zCXztbUmDHLOItrsWWr6Eg2mpR2P0QLSwfYaxWNg==)
17. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaZzTvboS8YtF4YNhEBAuvyZ7x6eAcrdPtQ7x4jf3cJNZndyVPRKcgAHCmUtYiNME6BQdktX1QhDQO-KZ1LyAj7a3CeXFiEjoIlHasOdT6BYGupSEllJUJmXOMahM=)
18. [sc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPFnHTTVwQvMVc7DPdsWW-stARTihZnqyMx-eEi6D3zwdg6ztMrtGh5NC9n6GrcE2aK8SvP-AFthT85QRCBCAucbBpiCBPKvF2fasEiw_iN4E_mEgnkpGEbdbXTI951pPhqM2vkkbAIRWolGxwJz3cTNmAN6VVJ2ph)
19. [unizg.hr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlmGxNn-8h-fCo-4S-L8p112MYnaA72g2W5IddeI4-uA_d7Pqokd41Sqyd5pF9hp5sdV671zWeElMOg2YNjyzWsAkzW8vyEKbG47UfGbufMxWmH6Rw2eR5ucr1IF58U5U_NyRL3OLU3NhuPQ==)
20. [wolfram.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwI2NJ-8JNci5LYK8EVeEmyXqomjCrEq0sanCPlkKMcpakBw1SiXZWeYBbRI517TxADyKQp1dcUH2W5KZdq3xg-sn-aEiv8X54mIPn_ikC2auq62qgv3pTG1jWd_paOJjhvQd2v-7RHQ==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHv2xn_5Z0T3_xMrZ6wfWNLjRzutgYLam3IKy0fVA3Twoz8WrZNocS8OLALD1XyNtP4GMIVW6_rCQDBiYchmz6rA0MviD1asZXhsA4334OdPJQ1suPkBnHCsw==)


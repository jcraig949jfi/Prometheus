# Followup [FU-2026-05-22-028 <- row166]: Despite a century of study, it remains unknown whether the rank of elliptic curves over $\mathbb{Q}$

**Pythia queue id:** 313
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdJTGNQYXJyakRLQ0ExTWtQdDdlZHVBWRIXSUxjUGFycmpES0NBMU1rUHQ3ZWR1QVk
**Elapsed:** 249s
**Completed at:** 2026-05-22T01:57:46.416602+00:00

---

# Substrate-Grade Research Brief: Boundedness and Asymptotics of Mordell-Weil Ranks for Elliptic Curves over $\mathbb{Q}$

*   **Key Finding 1:** The longstanding folklore conjecture that the Mordell-Weil rank of elliptic curves over $\mathbb{Q}$ is unbounded has been fundamentally challenged by recent heuristics (Park, Poonen, Voight, Wood), which suggest the rank is bounded by an absolute constant of 21 for all but finitely many curves [cite: 1, 2, 3].
*   **Key Finding 2:** Despite theoretical models predicting strict boundedness, computational records continue to advance; in August 2024, Noam Elkies and Zev Klagsbrun discovered an elliptic curve with a rank of at least 29, shattering an 18-year record [cite: 4, 5, 6].
*   **Key Finding 3:** The exact rank of these extreme-record curves relies heavily on the Generalized Riemann Hypothesis (GRH) and the Birch and Swinnerton-Dyer (BSD) conjecture for verification; the highest unconditionally proven rank remains 20 [cite: 5, 7].

**Context and Significance**
Elliptic curves form the central architecture of modern arithmetic geometry and number theory. A primary invariant of an elliptic curve $E/\mathbb{Q}$ is its rank, which measures the number of independent, infinite-order rational points necessary to generate the entire free abelian part of the curve's rational points. Whether this rank can grow arbitrarily large as one searches through curves of increasing complexity (measured by height or conductor) is one of the most profound open questions in mathematics, deeply intertwined with the Millennium Prize-winning Birch and Swinnerton-Dyer conjecture. 

**Complexity of the Inquiry**
Resolving the boundedness of elliptic curve ranks is extraordinarily difficult because empirical evidence is deeply conflicted. On one hand, mathematicians have spent a century successfully finding individual curves with higher and higher ranks through sophisticated geometric constructions (such as elliptic fibrations on K3 surfaces). On the other hand, statistical models evaluating the global distribution of all elliptic curves suggest that such high-rank curves are merely finite statistical anomalies. Because there is no known algorithm guaranteed to compute the rank of an arbitrary elliptic curve, and because the search space grows exponentially, proving an asymptotic upper limit requires reconciling algebraic topology, analytic number theory, and advanced computational sieving.

***

## 1. Brief summary
In response to the Prometheus context surfacing conflicts between recent theoretical heuristics and empirical discoveries, this brief interrogates whether the Mordell-Weil rank of elliptic curves over $\mathbb{Q}$ can be arbitrarily large or if it is strictly bounded (conjecturally by 21), evaluating the implications of the August 2024 discovery of a rank-29 curve.

## 2. Flagged findings

The consensus surrounding the distribution of elliptic curve ranks is currently undergoing a paradigm shift, marked by a sharp dichotomy between historical folklore conjectures and modern probabilistic heuristics. The flagged findings in this domain highlight where previous assumptions may be incorrect, and where current theoretical models are experiencing friction with empirical data.

### 2.1 The Shift from Unbounded Folklore to Bounded Heuristics
For over half a century, the prevailing "folklore conjecture" in arithmetic geometry held that the rank of elliptic curves over $\mathbb{Q}$ could be arbitrarily large [cite: 8, 9, 10]. This belief was primarily empirical, driven by the steady chronological progression of rank records—from Wiman finding a rank 4 curve in 1945, to Mestre reaching 15 in 1992, Martin and McMillen achieving 24 in 2000, and Elkies discovering a rank 28 curve in 2006 [cite: 8, 10]. 

However, this consensus is now deeply contested. Recent probabilistic modeling has introduced a compelling counter-narrative: ranks are absolutely bounded. The most prominent structural argument is the Park-Poonen-Voight-Wood (PPVW) heuristic, which models the rank and Shafarevich-Tate groups of elliptic curves simultaneously [cite: 2, 3]. The PPVW heuristic predicts that the ranks of all but finitely many elliptic curves defined over $\mathbb{Q}$ are strictly bounded above by 21 [cite: 1, 11]. 

### 2.2 Calibration: PATTERN_BASE_RATE_NEGLECT
The historical assumption of unboundedness is heavily flagged as a potential instance of **PATTERN_BASE_RATE_NEGLECT**. For decades, researchers assumed that because cleverly constructed geometric families (such as generic fibers over $\mathbb{Q}(t)$) yielded increasingly high ranks, the absolute upper limit did not exist. This neglected the base rate of the underlying statistical distribution. The number of elliptic curves up to a bounded height $H$ grows polynomially, but the theoretical probability of a curve possessing a rank $r$ decays exponentially. The PPVW heuristic demonstrates that the expected number of curves with rank $\geq 22$ is a convergent sum, predicting finite existence [cite: 3]. The assumption that "we keep finding them, so there must be infinitely many" neglects the fact that the search space is expanding exponentially while the yield of high-rank curves asymptotically approaches zero. 

### 2.3 The Friction of the Rank 29 Discovery
The primary tension in the field today arises from the unexpected resilience of empirical discoveries against these bounding heuristics. In August 2024, Noam Elkies and Zev Klagsbrun announced the discovery of an elliptic curve with a rank of at least 29 [cite: 4, 5, 6, 12]. Assuming the Generalized Riemann Hypothesis (GRH) for zeta functions of number fields, the arithmetic and analytic ranks are exactly 29 [cite: 5, 13]. 

This discovery breaks an 18-year stagnation (since Elkies' 2006 rank 28 curve) and is flagged as a critical pressure test for the PPVW bound. While the existence of a rank 29 curve does not strictly violate the PPVW heuristic—which allows for *finitely many* exceptions above the rank 21 threshold [cite: 3, 14]—it forces a re-evaluation of how large those "finite exceptions" might realistically get. It suggests that if an absolute bound exists, 21 may merely be the asymptotic limit for the "typical" statistical distribution, while highly specialized geometric families (like those derived from K3 surfaces) might harbor a finite but much higher ceiling of extreme outliers.

## 3. Problem statement

The precise mathematical object being interrogated is the **Mordell-Weil rank** of an elliptic curve defined over the field of rational numbers $\mathbb{Q}$. 

### 3.1 Formal Definition of the Object
An elliptic curve $E$ over $\mathbb{Q}$ can be given by a generalized Weierstrass equation of the form:
\[ y^2 + a_1xy + a_3y = x^3 + a_2x^2 + a_4x + a_6 \]
where the coefficients $a_i \in \mathbb{Z}$, and the curve is smooth (its discriminant $\Delta \neq 0$) [cite: 15, 16]. The set of $\mathbb{Q}$-rational points on this curve, denoted $E(\mathbb{Q})$, along with a distinguished point at infinity $\mathcal{O}$, forms an abelian group under the standard chord-and-tangent addition law [cite: 16].

By the Mordell-Weil theorem (proved by Mordell in 1922 for $\mathbb{Q}$, and generalized by Weil in 1929), $E(\mathbb{Q})$ is a finitely generated abelian group [cite: 9, 14, 17]. Consequently, it exhibits the canonical isomorphism:
\[ E(\mathbb{Q}) \cong E(\mathbb{Q})_{\text{tors}} \oplus \mathbb{Z}^r \]
where $E(\mathbb{Q})_{\text{tors}}$ is the finite torsion subgroup, and $r \in \mathbb{Z}_{\geq 0}$ is a non-negative integer known as the **rank** of the elliptic curve [cite: 10, 14, 15, 18].

### 3.2 The Torsion Subgroup vs. The Free Rank
The torsion subgroup $E(\mathbb{Q})_{\text{tors}}$ consists of points of finite order and is completely classified. Mazur's Theorem (1978) proves there are exactly 15 possible isomorphic structures for $E(\mathbb{Q})_{\text{tors}}$: $\mathbb{Z}/n\mathbb{Z}$ for $1 \leq n \leq 10$ or $n=12$, and $\mathbb{Z}/2\mathbb{Z} \oplus \mathbb{Z}/2m\mathbb{Z}$ for $1 \leq m \leq 4$ [cite: 9, 14, 15]. 

In contrast, the free abelian part $\mathbb{Z}^r$ remains deeply mysterious. The rank $r$ represents the minimal number of independent rational points of infinite order required to generate all other infinite-order rational points via the group law [cite: 6, 10, 19]. 

### 3.3 The Core Interrogation
The central open question interrogated by this brief is the asymptotic behavior of the set of all possible ranks:
\[ \mathcal{R} = \{ \text{rank}(E(\mathbb{Q})) \mid E/\mathbb{Q} \text{ is an elliptic curve} \} \]
Specifically, the field seeks to determine whether $\sup(\mathcal{R}) = \infty$ (the unboundedness conjecture) or if there exists an absolute constant $B$ such that $\text{rank}(E(\mathbb{Q})) \leq B$ for all $E/\mathbb{Q}$ (the strict boundedness hypothesis), or slightly weaker, if $\text{rank}(E(\mathbb{Q})) \leq B$ for all but finitely many isomorphism classes of curves [cite: 3, 8, 14, 17].

Furthermore, there is a computational sub-problem: Given the coefficients of $E$, there is no universally guaranteed algorithm to compute $r$ [cite: 8, 20, 21]. While 2-descent and Heegner point constructions often succeed, they can fail to determine the exact rank when the Shafarevich-Tate group contains non-trivial elements of certain orders, rendering high-rank computations highly contingent on unproven analytic conjectures [cite: 21].

## 4. Status & bounds

The status of elliptic curve ranks is bifurcated into two distinct vectors of research: statistical averages over the global population of curves, and the extreme upper bounds achieved by explicit construction.

### 4.1 Global Averages and the Rank 0/1 Consensus
When ordered by height $H(E) = \max(4|A|^3, 27B^2)$, the average rank of all elliptic curves over $\mathbb{Q}$ is conjectured by Goldfeld (and refined by Katz-Sarnak) to be exactly $1/2$ [cite: 10, 17, 21]. This conjecture posits that 50% of all elliptic curves have rank 0, 50% have rank 1, and the density of curves with rank $r \geq 2$ is exactly 0% in the limit [cite: 6, 17]. 

Recent unconditional progress has rigorously bounded the average rank. Bhargava and Shankar proved that the average 2-Selmer rank is bounded, which translates to an unconditional proof that the average Mordell-Weil rank of elliptic curves over $\mathbb{Q}$ is strictly less than $0.885$ (and further refinements have lowered this bound) [cite: 10].

### 4.2 Calibration: PATTERN_RANK_PARITY_LEAK
In assessing the status of elliptic ranks, one must carefully account for **PATTERN_RANK_PARITY_LEAK**. The Birch and Swinnerton-Dyer (BSD) conjecture ties the algebraic rank of $E$ to the order of vanishing of its Hasse-Weil L-function $L(E, s)$ at $s=1$. The functional equation of $L(E, s)$ is governed by a root number $W(E) \in \{+1, -1\}$, which forces the parity of the analytic rank [cite: 17, 22]. If $W(E) = +1$, the analytic rank is even (0, 2, 4...); if $W(E) = -1$, it is odd (1, 3, 5...) [cite: 17]. 

When researchers compile datasets of low-conductor elliptic curves (such as those in the LMFDB), the empirical distribution of ranks heavily leaks this parity constraint, often masking the true asymptotic decline of higher ranks. In lower computational strata, curves with rank 2 or 3 appear with misleading frequency because the parity constraint forces certain curves to skip rank 1 or 0 [cite: 17, 22]. Theoretical heuristics must surgically isolate this parity leak to accurately model the rapid tail-decay of ranks $\geq 4$.

### 4.3 Theoretical Upper Bounds (The PPVW Heuristic)
The current best theoretical heuristic for an upper bound is 21 [cite: 1, 2, 11]. The Park-Poonen-Voight-Wood model postulates that the set of rational points $E(\mathbb{Q})$ and the Shafarevich-Tate group $\text{Sha}(E)$ can be modeled simultaneously by considering the kernel and cokernel of random alternating integer matrices [cite: 2, 3, 11, 14]. In this framework, the probability of an elliptic curve having rank $r$ scales as $H^{(21-r)/24 + o(1)}$ as the height $H \to \infty$ [cite: 3]. 

Because the sum of these probabilities over all elliptic curves converges for $r > 21$, the heuristic implies that there are only finitely many elliptic curves over $\mathbb{Q}$ with a rank greater than 21 [cite: 3]. The existence of curves with rank up to 29 is treated as a finite exception set resulting from highly specific arithmetic structures that do not govern the uniform statistical limit.

### 4.4 Explicit Lower Bounds and Current Records
The pursuit of extreme rank curves serves as an empirical counterbalance to the PPVW heuristic. 

*   **Last Known Record (2006–2024):** For nearly two decades, the highest known rank was at least 28, achieved unconditionally by Noam Elkies in 2006 using an elliptic fibration of a K3 surface [cite: 6, 8, 9, 10]. Under GRH, this curve was proven to have exactly rank 28 [cite: 8, 10].
*   **Current Unconditional Record:** The highest rank of an elliptic curve that is *unconditionally* proven exact (where the rank is proven to be exactly $r$, rather than just $\geq r$) is **20**. This was achieved by Elkies and Klagsbrun in 2020 [cite: 7, 9, 23].
*   **Current Absolute Bound (August 2024):** In August 2024, Noam Elkies and Zev Klagsbrun announced the discovery of an elliptic curve with a rank of **at least 29** [cite: 4, 5, 6, 9, 10, 13].
    *   *Equation:* $y^2 + xy = x^3 - 27006183241630922218434652145297453784768054621836357954737385x + 55258058551342376475736699591118191821521067032535079608372404779149413277716173425636721497$ [cite: 5, 10, 24].
    *   *Conditional Qualifiers:* Klagsbrun utilized analytic methods (Klagsbrun, Sherman, Weigandt 2019) to prove that, assuming the Generalized Riemann Hypothesis (GRH) for zeta functions of number fields, the arithmetic rank of this curve is bounded at 29, meaning it is *exactly* 29 [cite: 5, 13]. Furthermore, assuming $L(E, s)$ satisfies GRH and assuming the BSD conjecture, the analytic rank is also exactly 29 [cite: 5].

## 5. Literature (primary sources)

The following primary sources constitute the foundational literature driving both the theoretical bounds and the explicit computational breakthroughs regarding elliptic curve ranks.

1.  **Park, J., Poonen, B., Voight, J., & Wood, M. M. (2019).** *A heuristic for boundedness of ranks of elliptic curves.* Journal of the European Mathematical Society, 21(9), 2859–2903. arXiv:1602.01431.
    *   *Significance:* The seminal paper establishing the PPVW heuristic, predicting that ranks of elliptic curves over $\mathbb{Q}$ are bounded by 21 for all but finitely many curves, modeling rank and Shafarevich-Tate groups via alternating integer matrices [cite: 2, 3, 11].
2.  **Elkies, N. D., & Klagsbrun, Z. (2020).** *New rank records for elliptic curves having rational torsion.* Proceedings of the Fourteenth Algorithmic Number Theory Symposium (ANTS-XIV), 233-250.
    *   *Significance:* Provides methodology for finding high-rank specializations on K3 surfaces and establishes the highest unconditional exact rank record of 20, alongside records for specific torsion subgroups [cite: 5, 7, 9].
3.  **Klagsbrun, Z., Sherman, T., & Weigandt, J. (2019).** *The Elkies curve has rank 28 subject to GRH.* Mathematics of Computation, 88(316), 837-846. arXiv:1606.07178.
    *   *Significance:* Develops the analytic methods used to compute the 2-rank of class groups of cubic fields subject to GRH, allowing for exact rank bounding of extreme curves (applied to both the 2006 rank 28 curve and the 2024 rank 29 curve) [cite: 5, 25].
4.  **Elkies, N. D., & Klagsbrun, Z. (August 2024).** *Z29 in E(Q).* Number Theory Listserver Announcement.
    *   *Significance:* The primary announcement and distribution of the coefficients and independent points for the rank 29 curve, breaking the 18-year record [cite: 5, 9, 26].
5.  **Bhargava, M., & Shankar, A. (2015).** *Binary quartic forms having bounded invariants, and the boundedness of the average rank of elliptic curves.* Annals of Mathematics, 181(1), 191-242.
    *   *Significance:* Provides the unconditional proof that the average rank of elliptic curves over $\mathbb{Q}$ is bounded, specifically computing the average size of the 2-Selmer group via the geometry of numbers [cite: 10].

## 6. Attack vectors

The search for and verification of high-rank elliptic curves relies on a synthesis of deep algebraic geometry, analytic number theory, and raw computational sieving. Conversely, several historical approaches have been exhausted.

### 6.1 Exhausted Approaches
*   **Naive Height Search:** Iterating through Weierstrass coefficients $A$ and $B$ by brute-force height ordering is computationally exhausted. Because high-rank curves require astronomically large coefficients (the rank 29 curve has 60-digit coefficients), random sampling or localized exhaustive searches have zero probability of yielding extreme ranks [cite: 5, 6].
*   **Mestre's Polynomial Method (Isolated):** While Mestre's theorem mapping rational functions to elliptic curves successfully dominated the 1980s and 1990s (yielding ranks 12 through 15), standalone polynomial parameterization struggles to break the rank 20 barrier without the added structural rigidity of advanced surface geometry [cite: 8, 17].

### 6.2 Live Techniques: Elliptic Fibrations on K3 Surfaces
The primary live vector for generating record-breaking ranks is geometric: exploiting **elliptic fibrations of K3 surfaces**. 
1.  **Surface Construction:** Researchers construct a K3 surface $X$ over $\mathbb{Q}$ with a highly constrained Néron-Severi group. By forcing the Picard number to be as large as possible (typically 20 for K3 surfaces over $\mathbb{C}$), the surface harbors rich geometric structure [cite: 7, 13].
2.  **Fibrations and the Shioda-Tate Formula:** The surface is parameterized into an elliptic fibration $E/\mathbb{Q}(t)$. According to the Shioda-Tate formula, the Mordell-Weil rank of the generic fiber $E(\mathbb{Q}(t))$ is directly tied to the rank of the Néron-Severi group of $X$ [cite: 7, 27]. Elkies and Klagsbrun utilized a specific K3 surface whose generic fiber yields a guaranteed rank of 17 over the function field $\mathbb{Q}(t)$ [cite: 5, 13].
3.  **Néron Specialization:** By Silverman's Specialization Theorem, for all but finitely many specific rational values $t_0 \in \mathbb{Q}$, the rank of the specialized curve $E_{t_0}/\mathbb{Q}$ will be at least the rank of the generic fiber (in this case, $\geq 17$) [cite: 7, 22, 23, 28].
4.  **Sieving for Rank Bumps:** The final computational attack involves an aggressive sieve search across massive ranges of $t_0$. The goal is to find rare specializations where the rank "jumps" significantly above the generic rank. For the rank 29 curve, Klagsbrun searched the rank-17 fibration and successfully located a specialization $t$ that yielded 12 additional independent rational points outside the generic generic $\mathbb{Z}^{17}$ subgroup ($17 + 12 = 29$) [cite: 5, 13].

### 6.3 Live Techniques: Verification and Bounding (2-Descent and GRH)
Proving that a curve has *at least* rank $r$ simply requires exhibiting $r$ independent points and computing their canonical height matrix determinant to ensure non-triviality and linear independence [cite: 5]. However, proving the rank is *exactly* $r$ requires bounding the Selmer group.
*   **Analytic Class Group Bounds:** Traditional 2-descent fails computationally for 60-digit coefficients. Instead, Klagsbrun, Sherman, and Weigandt developed a technique to compute the 2-rank of the ideal class group of the cubic subfield of the 2-division field of $E$ [cite: 25]. 
*   **GRH Application:** By assuming the Generalized Riemann Hypothesis for zeta functions of number fields, they can restrict the size of the factor base required for class group relations. This allows them to prove that the arithmetic rank is bounded from above by 29, effectively matching the lower bound and proving exactness under GRH [cite: 5, 25].

## 7. Cross-references

The open question of elliptic curve rank bounds does not exist in isolation; it anchors several neighboring domains in arithmetic geometry and cryptographic theory.

### 7.1 The Birch and Swinnerton-Dyer (BSD) Conjecture
The resolution of the rank boundedness problem is inextricably linked to the BSD conjecture, one of the Clay Mathematics Institute Millennium Prize Problems. BSD asserts that the algebraic rank of $E(\mathbb{Q})$ equals the analytic rank (the order of vanishing of the L-function $L(E, s)$ at $s=1$) [cite: 4, 15, 18, 21]. If ranks are unbounded, then the order of vanishing of L-functions must also be unbounded, requiring unprecedentedly flat behavior of L-functions at the central critical point—a phenomenon that deeply challenges current analytic heuristics [cite: 4, 21].

### 7.2 Abelian Varieties and Honda's Conjecture
The rank problem extends to higher-dimensional abelian varieties $A/\mathbb{Q}$. In 1960, Honda conjectured that for any abelian variety over $\mathbb{Q}$, there exists a constant bounding its rank uniformly over finite extensions [cite: 3]. Conversely, researchers investigate Jacobians of hyperelliptic curves. If elliptic curve ranks are bounded by 21, it prompts the question of whether Jacobians of genus $g$ curves possess ranks strictly bounded by a function $f(g)$. Unconditional sources of rank 2 Jacobians have recently been density-mapped using split Jacobian configurations [cite: 22].

### 7.3 Torsion-Rank Interaction (Anti-Anchors)
While the global rank over $\mathbb{Q}$ may be 29 (or bounded by 21 for generic curves), specifying a non-trivial torsion group drastically suppresses the maximum observable rank. This creates an anti-anchor: maximizing one algebraic property suppresses the other. For example, the highest known rank for a curve with torsion $\mathbb{Z}/4\mathbb{Z}$ is 12 (Elkies 2006) [cite: 7, 20], and for $\mathbb{Z}/2\mathbb{Z} \times \mathbb{Z}/8\mathbb{Z}$ the record is merely 3 [cite: 14]. The PPVW heuristic adjusts downward for torsion; for instance, the predicted absolute bound for curves with $\mathbb{Z}/2\mathbb{Z}$ torsion drops from 21 to 13 [cite: 7].

### 7.4 False Primitives in Cryptography
While elliptic curve cryptography (ECC) primarily operates over finite fields $\mathbb{F}_q$ rather than $\mathbb{Q}$, the algebraic geometry of high-rank curves occasionally interfaces with index calculus attacks and isogeny graphs. Claims that extreme-rank curves over $\mathbb{Q}$ can "break ECC" via explicit Diophantine extractions (e.g., claiming rank 30 solves ECDLP) are consistently debunked as false cryptographic primitives and pseudo-mathematical misinterpretations of the TCG (Tate-Shafarevich/Conductor Growth) spectral bounds [cite: 29]. The true cryptologic relevance of rank records lies in understanding the complex arithmetic of endomorphism rings and isogeny descents, not direct point-generation attacks.

**Sources:**
1. [math.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFb4JsxtVRYX3_HSn-kW1X6Fy9QLyvDqF6uX2coBsjhmEn89jbVhfUNRpmjrGUp1I5NSof5cA3vrbkFpLXkFLvxh-jKnAyZGf83FrIaOKDjvAndDMhL2elESteC2UouxIfdNG36pNDfsYF8IDQhO3r_Q==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkB8IscbGkwBBhmyTfm2FkLvdOQYBrTCwTUihJ8-HD4V6Dr-TcS3GhI3TUBWKXW4fXjfrft7RBzUt9cRBy0XIafX9oCKRmijIk_EqGD004YhFfTBa6pQ==)
3. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKNV3vUV9hq699tec0XXRgU4EdUpGyI3kzw_wKRn2ueHkYZ3fSEjbwcoObWlCCUYWM_HdabIEW1CCFmXqu_MFVNMj7wWvLPfQF_hLAzm9DnEMsYE20TmES-P-i-1luv3jgPrMWhC9ZH08alg==)
4. [stephendiehl.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaaJWhfEFa7bQCsovIUTcf-3mKxnTmX_zCWX1HN12oLR3LtriVE0L7t_m-W2j95g_5bZaZp6_1e6WXpFbmpIOOooHAsdMgv87am2fRy3pb4yR3VmzlXtQlYtWBdbzuCk6OTHoqkELZHeryBqNsb6lj)
5. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWiYwLGpYyQ8FbQuqklHTAkMmXI-Nctl6YifDdop6U5DWyQ8pj5nHIGwHX_mjX2I8ErGgaHKVfnVx2NfNT6LP0M8S0GYqVXxrj8N0-mbEdvd0faX5Z1b5HFVPld69uzehdGvhlMP855d2oI64JFnC5GE9ksKzJJ-GcQ1VEki9osU7rnNjfFA37twwzhI6HFpAkCpsi)
6. [quantamagazine.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMxcxmhl6Gr20CCqwoPEd-kQq01bUOlH12VPX7Rg4JA6f2dsEsDH4I86Ice9RZrScl-L66EnVxuYiY03B6JOSNobkwkYaCDiSgnz5g9KqVQdczF5sWqlX76Bl2ZzK6DV1RmtY5RpyBnyeeSG8-xEzq8vvPVnyD7ZvInxbNT1pjY5mFl1HI6PYU6635)
7. [auckland.ac.nz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHTysfSKYwnDn_Ba5-URzoJkxjJs8mXW94gZ-Izk9hGVsNfem-ftl3cWUM_Tgp0mYRdDjuPwdJ_Z-ZlPAAlTY6h0azHzkoK-qSezfx4Bvgp8JhhWNxMqG_SxbeyKHoNxk4JAZmpHscTm-OrJ_IepFPV1-VDxztSgNpcL13SWNG)
8. [unizg.hr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEHxX8obAWE-UQQDeWyBnhShZW5FvlmaqF2Xc7iBgrDsmvnpKLUisig1H40Nsc_6Qlo4CA_SQWKUP1wmDClOjNSUeiZ-dOH5Zj84ffASR9vCK1bRW4dBPGTo16zOCk2Iag5B0BVa3NhqBqLVMK)
9. [unizg.hr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaToSQzPDyxT8KnF_313skrZnD0ip1Ch-KolGTReANEP4bOtaNidyVDQJzrthXsRZL3s4bT5zKav7T3ZlvOTOQ69ZUHMVK9d8FvXEwxfPjjTelODHEe58Xk8JupKfNNp83SviFvziUpsJ-i7U=)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGh6fxX6TWmOijQoODbV0Xh8TR8KfB75QY_jJG5Z7fi-WGFaBAjsP22b2zRM6SR6_fV4Q1dZDTH1wQSvM4vtqHg5BEJ00vqNCrAK_zk9LAPiO-IyA1O9dDlHzqXM_tv7Se30u2NivKJ7MJmPBg8)
11. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdfUrdlVUhR7QVnYaGc1qfsAqrdd7y6MH_lBVJgCEMXnpdVoj-xrwyDCA_nxrzAPe4V5bE1mbLRS2mSYmm3eXHthDHNg6B3lVfBeb-ipTuT64BbFKfyEaSF3W75Cuy6hpS)
12. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiTRh6BhEBmeXgnstjiyK0UWgSHxl5voPG14z7xAe-pEOBVT92-dk0sT201aas2YylmrZQyZKlB8IDgoNS-V4BwZEnVBbaUvMpXrBDmjmRYz0G7j_Y881Ql3Q34z_g6mNwGc0lw2KYv9LwK52rZGCHBMxKDUAv9RiYBS9Zdmb-AaWbckg76Pr2Xp6Xq2gE80ZSwApyRno9eRZs0g==)
13. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpDyFGSWsLR2NEbOwWFc3F9tHy8MQjMzGryXx_PzylG5Ol3vWSN2vivZah4cYlDJAAM7YUJ8Fz6vAWrZnhhti4DEwUh7cQHX8cN5aG3TsBmL543R4gLrGInwfeeO-smDAwbO9kzB8vwjX14q9AjTWYkYV29dRTTunYvu6qoOUmEmdW)
14. [amherst.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh7d7aYDR82liYxK-6zcV1qj2CQoFzrPTIM5Fbwxs_WyH61aaGQFTelfBZX72rwFcNesj7reUX4GeO1G2Web7mp3VT92o59IsNnk3KdmQTTsPIBJEMSxVX2scJkL6izTMELmNyf2GlkuGZEKXL3w==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFLYCTjY8l4eYcqY0DaOFMEQeAlCHQKMni_8ZSOTvqDSsYFar5mQ6Xmnq56zfazZLl3uthNcGs3uskW7QmwvYQ4aiAqAj7GHgtmjQM0qeiPQj8Yd4A)
16. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUpAcNQsqV2WRAVaCNkvARo_486hb2hXtNpNmMR4FixqwpXwfx8f2yRzNXK_RYxQ1LzGpE_N4RtzLSlAEpMfF8Trnrvfu6WvO6NNNAeXv74PyWG0JYque-hAzUqObuovbR8K5Mo1M=)
17. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7D9k_Ago9Nb0CNfNwhKpWvCA8nCOMaWmyFJsuTCjpX9TJ-0llLd_O9-CdxCKHPcVl1gQZaGk-oQ51y2DO-uTm6A2-si8BPSIuqipACAK6wJmwsIv3fKndp1WG9iSqKbupW4JEHwfY-w9stlB2stGYAFmU)
18. [uc.cl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPc7FDWEr4_vPZ0XW914gmNcvJ_LFgnQDpTUL3Zfzcc2vdLS8TDjKa-PHDkHFjVNBmplJaCQme555U9w3xhzrvKKCzHOQHEjqWr6JGZ0zG0-YIywyX0t8BLBdDODT_WRA8d7vn-4c0qrKu6OwCIe4MchxgfmTzG85zWI_GIozxTXq10N7X4OpTZ_McJA-OPoetZfkYnTl3vLe4JkNEb2t6gf50cjeLlsGA)
19. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0SAOUmALNOVOKl2jMmIzKqovHpZ4-IZAXBr1zMcEA9wYnZDhQxNO3rBbAJmY5vFX6G9CR6un7d25syGHrVnQugZAeq8w4psjPTu9gy8c55acJx_PtInhthqG0FxPOR7L8y2aDutQY4hXBp2FcIRY2bxnkFg-9847RL3_sRNQmkZdPS0cU-SldHQGLbFtTyrUEXM9I8j-D6g==)
20. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXFh4dj85FuFvcnLVYYYi-IHkm6hWGoQYGo__9ByNeDvjoF_c5QuouAHB2GqffbqNMl0brwMv4j8xZL9WC_UDFBuxho4i6I4v3_5xW9yOugBKy-8gtwdyG8nbsgea1vXCiNiH6XdQQ)
21. [vixra.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZvrJqKBliNXCTpoGe23Z0w0ph9--lklGjg8SMsi4FU7kTtCYuJnK-gPREgPxDicxEvGROmXjnPuzoA83gVhllB3lRhdYH4W6-Fv2Xb1yTyF41racMgOx2ARG7r5uN)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMdsgBXvyiyVB5iniR5QaWXr0TtH7Qpx_Y-1Ky0zj0b6SBUvn_ZQvnL6xMaduxVqezFjJDJlmkpRjjIo07sCwf7mratQXovoqab_GG7C-qNScutB-V2Q==)
23. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENLB7n8YoCJ-HDbjPkKFkGgUt5sHwRsYLk2IIt-baS5emtYTIZEfrikygKFZJFbCdD9uGTTK313hZhHLq63w925DeEorXmLf5miTcUEBR_HSxHvk7xMa13OKtl_pKDGGDIoBVlfCI=)
24. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhbPr5uL_34aQ23BVeXjGEGLkpIgIhTCKx1uslyANr2zwQX73cNWhcNdUA32v-a2cPonxLG-1mgqkD0bLKsI_J0oxKu-YTKSJQWO9LZP1Nv0yAwirCaUjZE8M0ZJjM7SDTx8aQlcMv9BXeybeH20PGwjOEgDcT3jK6JrwNwuDDzwOrDvEblqnBadotmLZCnhCCFbn5FT99)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPXVVdeOahRKTVybwpDeYjuqLenHs6UoRKM0JYf13KCdXyYES4Lj0E-xebXlqbTpWqXjnAioKXwjNWnBYVKYMCTxxqffUTbjgsNI1tyysHPgfsFq4x-A==)
26. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcv94wJc16FwXhQINbIPIYkDkwQ40gKH7Yj925T0ebUlMYvero81P6qnNNq5UPhcB7X-RCFV5tYztP9goFbSYDLdyitOMmwePmj-AXXoCCrfUzuH8Cj8daAOnjmXzYbvAIKxhapQndCZTy1nI=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFojnBCaY-_PcfSuj1tee4Uk-Cv5gdCmatlPyG4Xtf3j-CHu1Mkt-zJA_6vvUECvoyY8e-iRUVD18pvzyOS51B2GY3uPeZ9_V0Av5hgIqzkZGxE4WA6IQ==)
28. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqtqCOCJNmTe3-Py3yEy_thet2TqCw0LyaRKKkzs2Cq3m6P5nO1__BSawPq5bNNYlkvf-8Cz-1Yw5zkkUGmiXGbYO0fuPiKpFMt11qm9PCzuHMqbi7_Jcfq59epNo12BHeDby9n8qi8SkYz2UUYqurLVLz0IWEWLXo0qA7NpeFmJd8p0EYwRDhUw7eNxyvYDyim4BWBC9a)
29. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB3iCklMgGiE4tveYuAiQ4A7bGyoXuovGQiC5K5IiQZ9xoM-eQQ0gwm8LdhgsYH9mI0sEvpDfGizNfm62IWeVhQU3UkLcG8y4GAcJzDJ8iXcnIWAQt-7FWyguaK272GEvijlF_98_t)


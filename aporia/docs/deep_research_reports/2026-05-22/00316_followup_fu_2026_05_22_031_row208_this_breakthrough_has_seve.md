# Followup [FU-2026-05-22-031 <- row208]: This breakthrough has several profound implications: *   **Combinatorial Interpretations**: It prove

**Pythia queue id:** 316
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdITGdQYW9DQkxhN0gxTWtQamVpaTJBcxIXSExnUGFvQ0JMYTdIMU1rUGplaWkyQXM
**Elapsed:** 249s
**Completed at:** 2026-05-22T02:01:58.738008+00:00

---

# Status Update: The Equivalence of Stanley's and Kirillov's Problems on Kronecker Coefficients

**Key Points:**
*   Recent breakthroughs have definitively proven that finding a combinatorial interpretation for ordinary Kronecker coefficients (Stanley's Problem 10 from 2000) and reduced Kronecker coefficients (Kirillov's Problem 2.32 from 2004) are mathematically equivalent problems.
*   This equivalence is established by the explicit construction showing that every ordinary Kronecker coefficient is, in fact, equal to a specific reduced Kronecker coefficient for slightly larger partitions.
*   The historical consensus that reduced Kronecker coefficients were "simpler" interpolations between Littlewood-Richardson coefficients and ordinary Kronecker coefficients has been overturned; both families share identical computational hardness (deciding positivity is NP-hard, and computing them is #P-hard).
*   The findings have profound implications for Geometric Complexity Theory (GCT), ruling out certain optimistic approaches to separating complexity classes like VP and VNP using naive representation-theoretic multiplicities.
*   Research suggests that while quantum algorithms provide specific speedups for representation-theoretic multiplicities under restricted conditions, the general problem remains robustly intractable for classical and quantum regimes alike unless major complexity theory axioms collapse.

The following report addresses the user's query regarding the recent resolution of a foundational open question in algebraic combinatorics and representation theory. Written for both domain experts and analysts tracking computational complexity limits, this substrate-grade research brief details the collapse of the perceived hierarchy between Kronecker and reduced Kronecker coefficients. It appears highly likely that the search for a purely positive, $\#\mathsf{P}$-contained combinatorial interpretation for these coefficients will require fundamentally new mathematical primitives, as classical approaches have been exhausted or proven computationally inadequate. The evidence leans toward Kronecker positivity being completely characterized only through highly complex, likely $\mathsf{NP}$-hard, geometric or circuit-based structures. 

***

## 1. Brief Summary

In the context of the Prometheus computational tracking parameters and recent Gemini Deep Research reports, the core open question regarding the relationship between the combinatorial interpretations of ordinary Kronecker coefficients (Stanley's Problem 10, surfaced in 2000) and reduced Kronecker coefficients (Kirillov's Problem 2.32, surfaced in 2004) has been decisively closed. Through a series of landmark papers culminating in 2023–2024, Ikenmeyer and Panova demonstrated that every ordinary Kronecker coefficient of the symmetric group can be explicitly realized as a reduced Kronecker coefficient, proving the absolute equivalence of the two open problems [cite: 1, 2]. This breakthrough establishes that the reduced Kronecker coefficients, long thought to be a simpler interpolation bridging the tractable Littlewood-Richardson coefficients and the intractable ordinary Kronecker coefficients, are exactly as computationally hard to compute ($\#\mathsf{P}$-hard) and evaluate for positivity ($\mathsf{NP}$-hard) as their ordinary counterparts [cite: 3, 4].

## 2. Flagged Findings

### Current Consensus
The current mathematical and theoretical computer science consensus rests on a unified view of the Kronecker coefficient spectrum, drastically altering the trajectory of Algebraic Combinatorics. For nearly two decades, the prevailing assumption was that reduced Kronecker coefficients, $\bar{g}(\alpha, \beta, \gamma)$, defined as the stable limit of ordinary Kronecker coefficients $g(\alpha[n], \beta[n], \gamma[n])$ as $n \to \infty$, were fundamentally "simpler" or "better behaved" than ordinary Kronecker coefficients [cite: 3, 5]. 

This assumption was rooted in their connection to Littlewood-Richardson (LR) coefficients. Because reduced Kronecker coefficients exactly recover the LR coefficients when $|\alpha| = |\beta| + |\gamma|$, Kirillov termed them "extended Littlewood-Richardson numbers" [cite: 2, 6]. Because LR coefficients have a beautiful, positive combinatorial interpretation (counting LR tableaux) and their positivity can be decided in polynomial time ($\mathsf{P}$), it was widely believed that reduced Kronecker coefficients would inherit similar tractability [cite: 3, 4].

However, the modern consensus, established primarily by Pak, Panova, and Ikenmeyer, completely dismantled this belief system:
1.  **Failure of the Saturation Property:** In 2020, Pak and Panova proved that reduced Kronecker coefficients do *not* satisfy the saturation property [cite: 5, 7]. Prior to this, it was conjectured by Kirillov and Klyachko (2004) that if $\bar{g}(N\alpha, N\beta, N\gamma) > 0$ for some $N \geq 1$, then $\bar{g}(\alpha, \beta, \gamma) > 0$. Pak and Panova found explicit counterexamples (e.g., using the triple of partitions $(1^{k^2-1}, 1^{k^2-1}, k^{k-1})$ for $k \ge 3$), fracturing the structural analogy with LR coefficients [cite: 7].
2.  **Equivalence of Hardness:** In 2023/2024, Ikenmeyer and Panova proved that any ordinary Kronecker coefficient is equal to an explicit reduced Kronecker coefficient [cite: 3]. Consequently, computing reduced Kronecker coefficients is strongly $\#\mathsf{P}$-hard, and deciding their positivity is $\mathsf{NP}$-hard [cite: 4, 6]. 

### Where the Consensus Might Be Wrong (or Subject to Cognitive Bias)
The historical trajectory of this problem represents a textbook case of **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**, wherein mathematicians over-anchored on the algebraic elegance of the stable limit. Because the limit operation smoothed out certain dimensional constraints and perfectly recovered the highly symmetric Littlewood-Richardson coefficients in special cases, the community "over-fit" their expectations, assuming the entire reduced Kronecker parameter space would naturally shed the pathological complexity of the ordinary Kronecker space [cite: 3, 7]. The reality was the exact opposite: the reduced space is a superset of the ordinary space's complexity [cite: 5, 7].

Furthermore, there is a risk of **PATTERN_CONDUCTOR_CONFOUND** in the current literature regarding the interpretation of algorithmic complexity. While computing the coefficients is $\#\mathsf{P}$-hard, distinguishing between the complexity of *exact computation* versus *positivity decision* versus *asymptotic approximation* is crucial [cite: 3, 4]. For example, deciding if a combinatorial formula exists in $\#\mathsf{P}$ is often conflated with deciding if positivity is in $\mathsf{NP} \cap \text{co}\mathsf{NP}$. As Bravyi et al. (2023) showed, deciding Kronecker positivity is in the quantum complexity class $\mathsf{QMA}$ [cite: 8], which suggests that quantum witnesses might exist for these structures even if classical combinatorial formulas (in $\#\mathsf{P}$) remain permanently out of reach. Assuming that $\mathsf{NP}$-hardness strictly precludes any mathematically "beautiful" formula might be a classical computational bias; a "combinatorial interpretation" could hypothetically exist within a quantum or probabilistic framework [cite: 9].

## 3. Problem Statement

The precise objects being interrogated are the representation-theoretic multiplicities of the symmetric group $S_n$ and the general linear group $GL_N(\mathbb{C})$.

### Ordinary Kronecker Coefficients
The ordinary Kronecker coefficient $g(\lambda, \mu, \nu)$ (also denoted $k(\lambda, \mu, \nu)$ in some literature) is defined as the multiplicity of the irreducible $S_n$-representation (Specht module) $S^\nu$ in the tensor product of two other irreducible representations $S^\lambda \otimes S^\mu$, where $\lambda, \mu, \nu \vdash n$ are integer partitions of $n$ [cite: 4, 10]. Equivalently, in terms of characters $\chi^\lambda$ of $S_n$:
\[ g(\lambda, \mu, \nu) = \langle \chi^\lambda \chi^\mu, \chi^\nu \rangle = \frac{1}{n!} \sum_{\sigma \in S_n} \chi^\lambda(\sigma) \chi^\mu(\sigma) \chi^\nu(\sigma) \]
These coefficients lack a general positive combinatorial formula (i.e., a rule counting a specific set of objects to yield the coefficient, avoiding alternating sums) [cite: 1, 6]. 
*   **Stanley's Problem 10 (2000):** Give a nonnegative combinatorial interpretation for the ordinary Kronecker coefficient $g(\lambda, \mu, \nu)$ [cite: 6, 8].

### Reduced Kronecker Coefficients
Murnaghan (1938) defined the reduced Kronecker coefficients $\bar{g}(\alpha, \beta, \gamma)$ as the stable limit of the ordinary Kronecker coefficients when a long first row is added to the partitions [cite: 1, 5]. For partitions $\alpha \vdash a, \beta \vdash b, \gamma \vdash c$, and for an integer $n \ge |\alpha| + \alpha_1$, let $\alpha[n] = (n - |\alpha|, \alpha_1, \alpha_2, \dots) \vdash n$. The reduced Kronecker coefficient is:
\[ \bar{g}(\alpha, \beta, \gamma) = \lim_{n \to \infty} g(\alpha[n], \beta[n], \gamma[n]) \]
This limit is known to stabilize [cite: 5, 6]. When $|\alpha| = |\beta| + |\gamma|$, $\bar{g}(\alpha, \beta, \gamma)$ equals the Littlewood-Richardson coefficient $c^\alpha_{\beta, \gamma}$ [cite: 2, 3].
*   **Kirillov's Problem 2.32 (2004):** Find a combinatorial interpretation for the reduced Kronecker coefficient $\bar{g}(\alpha, \beta, \gamma)$ [cite: 2, 3].

### The Equivalence Theorem (Ikenmeyer-Panova 2023)
The exact result connecting the two is an explicit mapping showing that all Kronecker coefficients are reduced Kronecker coefficients. For every $\lambda, \mu, \nu \vdash n$, the relation is given by:
\[ g(\lambda, \mu, \nu) = \bar{g}\left( \nu_1^{\ell(\lambda)} + \lambda, \; \nu_1^{\ell(\mu)} + \mu, \; (\nu_1^{\ell(\lambda)+\ell(\mu)}) \cup \nu \right) \]
where $\nu_1$ is the first part of $\nu$, $\ell(\lambda)$ is the length of $\lambda$, and exponents denote repetition of parts [cite: 1, 11]. This theorem proves that finding a combinatorial interpretation for one is formally equivalent to finding a combinatorial interpretation for the other; Conjectures 9.1 and 9.4 in Pak (2022) regarding these interpretations are logically identical [cite: 1, 6].

## 4. Status & Bounds

### Last Known Status
The search for a #P-contained, classically positive combinatorial formula remains **OPEN**, but the theoretical equivalence of the ordinary and reduced cases is completely **SOLVED** [cite: 4, 12]. 
Furthermore, the computational hardness boundaries are now firmly established:
*   **Computing** $g(\lambda, \mu, \nu)$ and $\bar{g}(\alpha, \beta, \gamma)$ when partitions are given in unary is **strongly $\#\mathsf{P}$-hard** [cite: 7].
*   **Deciding positivity** (i.e., whether $g > 0$ or $\bar{g} > 0$) is **$\mathsf{NP}$-hard** [cite: 4, 6].
*   The decision problem for Kronecker positivity is contained in the quantum complexity class **$\mathsf{QMA}$** (Bravyi, Chowdhury, Gosset, Havlíček, Zhu, 2023) [cite: 8]. 

### Current Best Bounds and Asymptotics
Pak, Panova, and Yeliussizov established critical upper bounds for Kronecker coefficients utilizing contingency tables and Kostka numbers [cite: 13]. 
*   **Contingency Table Bound:** For partitions $\lambda, \mu, \nu \vdash n$, the Kronecker coefficient is bounded by the number of 3-dimensional integer contingency tables $T(\lambda, \mu, \nu)$ with 1D marginals given by $\lambda, \mu, \nu$ [cite: 13].
*   **Maximal Values:** For any $|a| + |b| + |c| = n$, the maximum reduced Kronecker coefficient is asymptotically bounded by $\sqrt{n!} e^{O(n)}$ [cite: 5, 7]. The maximal Kronecker and LR-coefficients appear when all three partitions have near-maximal dimension, achieving a Vershik–Kerov–Logan–Shepp (VKLS) limit shape [cite: 7].

### Conditional Qualifiers and Complexity Classes
The search for a combinatorial interpretation is rigorously formalized in computational complexity as asking whether the function $f(\lambda, \mu, \nu) = g(\lambda, \mu, \nu)$ is in the class $\#\mathsf{P}$ [cite: 14]. Currently, the Kronecker coefficient problem is known to be in the class $\mathsf{GapP}$ (specifically $\mathsf{GapP}_{\ge 0}$), which consists of functions that can be expressed as the difference of two $\#\mathsf{P}$ functions [cite: 15, 16]. 
If a strictly positive combinatorial interpretation exists (placing it in $\#\mathsf{P}$ without alternating sums), it would mean the problem counts a specific set of verifiable witnesses [cite: 14, 17]. A conditional qualifier observed by Ikenmeyer (2025) is the embedding of $\mathsf{GapCircuitSat}$ into character calculations. If the "character proof method" worked broadly for Kronecker coefficients to prove containment, it would imply $\mathsf{NQP} \subseteq \mathsf{QMA}$, a highly unlikely collapse of quantum complexity classes [cite: 8].

## 5. Literature (Primary Sources)

The following table provides the primary literature establishing the current consensus, bounds, and equivalencies.

| ID | Authors | Title & Publication | Date/ArXiv ID | Key Contribution |
| :--- | :--- | :--- | :--- | :--- |
| **[cite: 3, 6]** | Christian Ikenmeyer, Greta Panova | *All Kronecker coefficients are reduced Kronecker coefficients*, Forum of Mathematics, Pi, Vol. 12:e22. | arXiv:2305.03003 (May 2023), Pub: 2024 | Proved explicit equivalence of ordinary and reduced Kronecker coefficients. Settled the Stanley/Kirillov equivalence. |
| **[cite: 5, 18]** | Igor Pak, Greta Panova | *Breaking down the reduced Kronecker coefficients*, Comptes Rendus Mathematique, 358(4), 463-468. | arXiv:2003.11398 (Mar 2020), Pub: 2020 | Disproved the Kirillov-Klyachko saturation conjecture for reduced Kroneckers. Proved strongly $\#\mathsf{P}$-hard computation. |
| **[cite: 13]** | Igor Pak, Greta Panova, Damir Yeliussizov | *On the largest Kronecker and Littlewood-Richardson coefficients*, J. Combin. Theory, Ser. A. | 2020 | Established asymptotic bounds for Kronecker coefficients via 3D contingency tables and Vershik-Kerov limit shapes. |
| **[cite: 1, 3]** | Richard Stanley | *Positivity problems and conjectures in algebraic combinatorics*, Mathematics: frontiers and perspectives. | 2000 | Formulated "Problem 10", the foundational challenge to find a nonnegative combinatorial interpretation for Kroneckers. |
| **[cite: 3, 7]** | Anatol Kirillov | *An invitation to the generalized saturation conjecture*, Publ. RIMS 40. | 2004 | Formulated "Problem 2.32", seeking an interpretation for reduced Kroneckers, coining "extended LR numbers". |
| **[cite: 14, 16]** | Nick Fischer, Christian Ikenmeyer | *The computational complexity of plethysm coefficients*, computational complexity, 29:1-43. | arXiv:2002.00788 (Feb 2020), Pub: 2020 | Formalized Stanley's Problem 9 (Plethysms) in complexity theory. Proved deciding plethysm positivity is $\mathsf{NP}$-hard. |

## 6. Attack Vectors

### Live Techniques
1.  **3-Dimensional Binary Contingency Arrays:** The most successful recent technique, utilized by Ikenmeyer and Panova to prove the equivalence theorem, relies on modeling Kronecker products via Schur-Weyl duality and the representation theory of the General Linear Group $GL_N(\mathbb{C})$ [cite: 1, 6]. They leveraged the relationship between Kronecker coefficients and counting specific 3-dimensional contingency arrays with zeros and ones [cite: 4, 6]. By carefully manipulating the marginals of these 3D arrays, they demonstrated how shifting the partition weights directly maps the ordinary tensor space into the reduced stable limit space [cite: 4, 6].
2.  **Quantum Marginal Protocols and $\mathsf{QMA}$:** A highly active vector investigates the problem through the lens of theoretical physics, specifically the quantum marginal problem for distinguishable particles [cite: 14]. Since deciding positivity is in $\mathsf{QMA}$ (Bravyi et al. 2023), quantum algorithms are being explored [cite: 3, 8]. While early 2025 claims of polynomial-time quantum algorithms for specific dimension ratios were quickly counter-argued by classical simulability (Panova, 2025), the quantum algorithmic space remains a live vector for bypassing classical $\mathsf{NP}$-hardness bottlenecks [cite: 9].
3.  **Circuit Complexity Embeddings:** Ikenmeyer, Mulmuley, and Walter (2017) demonstrated that $\#\mathsf{CircuitSat}$ is a special case of Kronecker coefficient computation [cite: 8]. The live approach seeks to determine if Kronecker is merely a special case of $\#\mathsf{CircuitSat}$ (which would directly yield a nonnegative combinatorial interpretation by counting circuit satisfying assignments) or if it is inherently tied to $\mathsf{GapCircuitSat}$ [cite: 8].

### Exhausted Approaches
1.  **Saturation via Horn Inequalities:** The Knutson-Tao proof of the saturation property for Littlewood-Richardson coefficients relied on geometric structures (honeycomb models) and Horn inequalities [cite: 7, 10]. Attempts to apply these exact geometric continuum arguments to reduced Kronecker coefficients have been exhausted, as Pak and Panova conclusively proved that saturation completely fails for both ordinary and reduced Kroneckers [cite: 5, 19]. The discrete combinatorial anomalies at small dimensions (e.g., $g(2^2, 2^2, 2^2) = 1$ but $g(1^2, 1^2, 1^2) = 0$) block scaling arguments [cite: 6, 7].
2.  **Naive Asymptotic Multiplicity Gaps in GCT:** Geometric Complexity Theory (GCT) originally hoped to separate $\mathsf{VP}$ (Permanent) from $\mathsf{VNP}$ (Determinant) by showing the occurrence of specific irreducible representations in the coordinate ring of the permanent that vanish in the determinant [cite: 16, 20]. Ikenmeyer and Panova (2015) proved that the vanishing of rectangular Kronecker coefficients cannot be used to prove superpolynomial determinantal complexity lower bounds for the permanent [cite: 20]. Consequently, pure "occurrence obstructions" based on Kronecker vanishing are largely exhausted, requiring GCT to shift toward more complex multiplicity gaps [cite: 20, 21]. 

## 7. Cross-References

### Related Open Problems
*   **Stanley's Problem 9 (Plethysm Coefficients):** Closely related to the Kronecker coefficient problem is the quest for a combinatorial interpretation of *plethysm coefficients* [cite: 8, 16]. Plethysms are multiplicities in the coordinate rings of spaces of polynomials, critical to GCT. Fischer and Ikenmeyer (2020) proved that computing plethysms is $\#\mathsf{P}$-hard and deciding their positivity is $\mathsf{NP}$-hard, paralleling the Kronecker results [cite: 14, 16].
*   **The Monical–Tokcan–Yong Conjecture:** This conjecture posits that the monomial expansion of the Kronecker product of two Schur functions has a Saturated Newton Polytope (SNP) [cite: 10]. While overall saturation for the coefficients fails, the geometric properties of their Newton polytopes remain an active area of cross-disciplinary research [cite: 10].
*   **The Tensor Square Conjecture (Haide-Saxl-Tiep-Zalesski, 2012):** Conjectures that for every $n \ge 9$, there is a partition $\lambda \vdash n$ such that $g(\lambda, \lambda, \mu) > 0$ for all $\mu \vdash n$ [cite: 11]. This touches on the limits of Kronecker positivity across tensor squares.

### Anti-Anchors & Candidate Primitives
*   **Anti-Anchor (Geometric Rigidty):** One must decouple the expectation that limit objects in representation theory are always computationally strictly simpler than their discrete parents (the failure of the "extended LR" hypothesis) [cite: 6, 7].
*   **Candidate Primitive (Character Polynomials):** Reduced Kronecker coefficients are the structure constants for the ring of character polynomials [cite: 1]. Future combinatorial models might not count tableaux, but instead count algebraic primitives derived directly from character polynomial evaluations.
*   **Candidate Primitive (Formal Verification):** There is emerging work in utilizing dependent-type theorem provers (Lean 4, Coq) to formalize multiplicity obstructions in GCT [cite: 21]. The continuous spatial divergence of moment map stratifications and the failure of Kirwan convexity in these spaces are being translated into mechanized logic to overcome human cognitive limits in high-dimensional algebraic geometry [cite: 21].

**Sources:**
1. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhUBrBds0FfwQV4lAnRdig5Zc0hb7QvPfgX8mlfqizyPMm-UE4GQuewCC1aUIyHQR2YsSgCkW84VqbSgRajE2E4m7faVO2w7E48VyLmkFPLIn_DQ5yYmX2D8tnFPvd9WqlKkvFYAzumf0CF-iRSvjJxUk=)
2. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdB_q5D__RM5tPOcKcLRSTT13AqTt2oGxznd_Ozykqs_Ij0SUWNKVGB_KasYmNO_iZ5p5RDvyYyD5HCqjlbaFj4Y_4Kx3PiRSj2XNRC2-w3a3ZipizQ9p8peqAaCkMAeowzClGtjyKlofKJU-SOlgfpQMHo2P7DprrG3ucmXT3bc42LeGieteJ6fCC0a3YKYPtVIjLhTXL5xKKWFuclox7OSDf7neJFQdnkpXlCXoGzbwrsF-SbALkliXVS6N5xAYOZyBbMPK8IDY_oRoVSft1Xc2Rl_0csA-Beg91)
3. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAebiN4ruNZ9npB_W484TlCvG7qjI1pSLXD-0mSfV0pb9cIAqy1pFKU3iGCm3NaKaPjXaLnmawbXQFPEexbF1DNkew2YbtJX4xnrR5P5L1n8h_n89AJ8jNc2UJO_1gMvkUO-lZKwdrQbnNz8UmTIT7KV4mWFcVN_Y9ByKruBuUqAR5NwF94EdwLG7Gjji7Fpgl9m2sdrkpZ5XyicsbOkWeCk8eZBoXqZWHgDlDuynIWRD8q_a9cvOtHB15bjinLSkUypfGUiE0xt6KS-bSk3PNHgFJDq_J69aA8XRTNWwTooDuCUxXmrS8LHQs95XFLUE4PtRpqt-3)
4. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGa0lIqkdjs1MByfBLS8KNav1CYa0R0apOOoW1_S_o_be4fBemSkrs228nlzFY4IIIDCX-H-nih0zj7dBqaPHBH25KG-eLq1zrmwU8QkvbEnR9MwqyE1ugPLpdl4QV7hJXUkzDQ_-9HMr-q3vsuKsg=)
5. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQvIBUyphO-cWjM4yVBtpwlNdzYNvz4idPhZChitAbylHaeu0SAigsjMuVqYuUOOuKs64feEz4NFmLqrnPz39IE1fK-h_52tqyy9c2_--lKSvpYmcO4VtrgkfVgY1Fd6Bd6snNEqo=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvpA-11e1q6gdFRF61up1FlM1ZB8AZfCMkqYtAEo9yYvQTKfBec1jEaQ6wES1IrikW7G6HQQmQvYzqYVu1CE1fTA_bwRnQYjuAUuKEot_jM-4qzfJW)
7. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQnFD1n3vz9FsJebvYaIBORoxgtT7dQvznaGLLsOqJrO6gOfOUDMTv1KVNUS29cG_xAR0Bt-96eC1DfIUHXi-yQzaR8hnZNpINI5cgirfp9USuyIYgfDrzpHZNgdRoIzBkUBwOwasgQ8RfB-0=)
8. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhLviSeWA5sSG2Wet1Iws7pGgL5YiFaNLqndGsVO-ycHMVvnRq6Pbi5Ndkym-5BYc50s9FxOtgoI5ezNjw7oiFlX48vnMMJY7GebPYGi_aZre14NpQRFo2BJzW1rwm16gEUU1i3bfzNgpDid2AVZmseYRl2S-w_ZlmRRCajGLhIetEtdKtySnagE36CjNc)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPYL8mwGLHQBy8MWpjFx9fFUMgxWvj07yJRmBNJDlWDy6NNMmscQLxrU3MjmZX-2R0vTYn6zPDgukkARUNPd3ZTedrNTaIFQtTSON7y-HDwMHAhpWK)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtRtfNayXe2BIsWqE5JPSOX86Et_BDm_JfEHFcg1Xc4Tvx0lK65wqe4dq105pn7HyYOG1B9Zq2eSJKAxlHKXx7jxmzoMjmjUR2ePUWzzJ9EGgIjTqW)
11. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2fytIu-fgvNxOTuN_6VUW_JSGW6H5rYY6mq--1k3inWSBDoUlsAbdwIkbBL-AZeG2dPigbCB9mR2tlqPZTZ2JUpFmJTHpujtUousjsyb0RDrcRmFjavDBVEXKgVWKLyDpDaX6WT2U14xpnPBXPajXvHWuDqAKwng=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGshyg_N_j2gb4vqA6NAADAhr90K-42S7wtWY5jZtUQJ-Th4OrIpQRuhuz0Ys_TqKyNozfALS4osMpcP1WdWLTB8zEZ6e-lcs6FJupoEXsn1IYLZ36P)
13. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGD1NFq6WPuTV2lOI0LehdBzrKvFICu4kUxXJ_rmkZCzfEUUH5NySQ1eEKJ7WRxxPC7fg-6dALSEhQFY5gcNJUydVaKaCtxVf1hZmExXIeiNS1KGkdH5Sfe9R638IX_QQ==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0PLaMkmy0f9lETu4LusnCIQRea5M7IUIqUZnE60A_fCXFjY7r5_-eS8qdNHDITxeTnm75oB0-GZLm8Vfa1SajVGVwvHPkzGnadSfjUXN4p832CenT)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRJhasKlW4DfsX4xpg5TUInIGeHBT-BoMSOAxPIlydqh-cYO71c-e6JQsIzIkwm-yQ9Trbc2ZLkEXm4e94G1nGjcpBip4IfiEs5Wsn-Xmt41mtwEF3amEN)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVY1XCeVWpstopOyti4uWPnftd6-WQtPfXNJRe5qJRGnieHu6uf-e3Jp6QhuwhQ17TJcwCEXYjYpV0COFBTDqmMxlXaQsRL9hWPggC8Jhb3DAbDily0f5rOKWGNR343zoMvQHVPHTubtR_cyc-k2z3fBSwWnnFxo3iyrFEtSPJc42AHXLbe0rMFf4CowP8)
17. [samuelfhopkins.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKx92if26YQpeMo1R0Lkdu9Rw_-5CdTKaF5MJ117ALgh-vvc855ULS9gz8Pp1D75cKJGkXYTLZ-_x4fubMQohtbeOdzhu1zITr_i0-147bTorcP7oecm1R49R1ynh9tIV22PYwqm2fj2iRPYmEkYOm0Xg=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVIc677koAHijjVd7z7JOYZ51EMT0vayhd9oXjyNVVqvQHMRrHswZx2QFDqbw9qXrpfFh10wCxwjxH8KBu3GVAWAVxokn5cMOc40sj1ytoawu81HjH)
19. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFC6kLjtQX3hD-dMGmkoc3Mx7iyyLbnhqID9iyh1qqjVKhYuEnpw8TCpMZgUmwZFWsjbPxqVN_nJAgTgG-IAAIq02B2sgDTqUnZKwoQTKtYr7d8Hn3Cwp9LDDHbEXer5gNK-458lFfDzV4P)
20. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5w_894QoEBLK2DbrNQpZXzUU1sjJhuNAmloKa7RE7iDzpEU86YbLfzjNCLA9ALKfPUWkLsPnK4sgXvPAzJp7Em3o84DqSvv3az5YAuXSWDw2dmNXzQCL7mWV70KU0ArpaJST9A7INIwIwfh-DRzc-Mub9K79CgKXcTStBO-NAEdo7sN2s-taNFPigbsVK0NsM8D7thOcx7aSkpYf8s0qhVtBmJ-L9hWw=)
21. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6Et4UtcyMyCApuH2Fnh-ttJtWsZXalPr3Rbmo_FtBS6nO7XOFJ2TP8XHgfO46b4609pDHS7z0Rg0CNpB0ko3UA7zaWlmR9HnMZSCCP_oilFpr9YhQQEzzB2W7K3-DvroZpPPFLQRCx1t9IpYeLXVCsTkH6SaRZQ40xpFf6ZG2M9QgQxFTFmxtgiZZt0swSIx3-Bws6ogKOg9AIZjkHu4xMOgdWG41f41ynq9CdNR5)


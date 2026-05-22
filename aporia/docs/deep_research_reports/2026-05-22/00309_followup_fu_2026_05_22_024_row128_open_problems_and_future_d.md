# Followup [FU-2026-05-22-024 <- row128]: Open Problems and Future Directions  The study of Kronecker coefficients remains a vibrant, evolving

**Pythia queue id:** 309
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdwYlVQYXZTbUhkaThfdU1QdXVxd3VBYxIXcGJVUGF2U21IZGk4X3VNUHV1cXd1QWM
**Elapsed:** 249s
**Completed at:** 2026-05-22T01:51:28.045112+00:00

---

# Status Update: Stanley's Problem 10 and the Combinatorial Interpretation of Kronecker Coefficients

**Key Points**
*   **The Core Mystery**: Stanley’s Problem 10 asks for a positive combinatorial interpretation of the Kronecker coefficients of the symmetric group—essentially, a `#P` counting rule akin to the Littlewood-Richardson rule. 
*   **Recent Breakthroughs in Complexity**: The problem of computing Kronecker coefficients is `#P`-hard, and deciding their positivity is `NP`-hard. A major recent finding places the positivity decision problem in the quantum complexity class `QMA`.
*   **The Quantum vs. Classical Debate**: Recent assertions (2024–2025) conjectured a superpolynomial quantum advantage for computing Kronecker and Plethysm coefficients in specific regimes. However, rapid classical algorithmic advancements in early 2025 have refuted these claims for broad families of partitions, demonstrating polynomial-time classical solvability.
*   **Collapse of the "Interpolation" Hypothesis**: Reduced (or extended) Kronecker coefficients, long thought to occupy a strict intermediate complexity class between Littlewood-Richardson and ordinary Kronecker coefficients, have been mathematically proven to be identical to ordinary Kronecker coefficients, collapsing Stanley's Problem 10 and Kirillov's Problem 2.32 into the same fundamental question.

**Executive Summary for Laymen**
When physicists and mathematicians study symmetry, they use tools called "representations." When two symmetric systems are combined, their mathematical descriptions merge (a "tensor product"), and the resulting system can be broken down into fundamental, indivisible building blocks. The *Kronecker coefficients* are simply the integers that tell us "how many" of each building block are present in the mixture. Because they represent "how many," they are always non-negative whole numbers (0, 1, 2, ...). 

In mathematics, if a sequence of numbers is always non-negative, there is usually a way to count some physical or geometric object to get those numbers—this is known as a "combinatorial interpretation." For 75 years, mathematicians have searched for what exactly to count to get the Kronecker coefficients. This search is Richard Stanley’s famous "Problem 10." Recently, this pure math problem has become a battleground for theoretical computer science and quantum physics. Researchers are trying to prove whether standard computers, or hypothetical quantum computers, can calculate these numbers efficiently. While some evidence suggests quantum computers might have a unique edge here, recent classical math breakthroughs have shown that standard computers are far more capable of calculating these coefficients than previously believed. The evidence leans toward Kronecker coefficients being fundamentally intractable for both classical and quantum computers in the general case, though specific restricted cases remain highly contested.

***

## 1. Brief Summary

**The Question:** Is there a `#P` positive combinatorial interpretation for the Kronecker coefficients of the symmetric group $S_n$ (Stanley's Problem 10), and does the complexity of computing these multiplicities permit a superpolynomial quantum speedup?

**Prometheus Context:** This open question—surfaced as a follow-up to a Gemini Deep Research report on stretched Kronecker positivity and quasi-polynomiality—sits at the nexus of Algebraic Combinatorics, Geometric Complexity Theory (the Mulmuley-Sohoni approach to `P vs NP`), and Quantum Complexity Theory. The inquiry primarily interrogates whether the absence of a polynomial-time verifiable combinatorial rule (due to `NP`-hardness of positivity) mathematically necessitates a quantum advantage for exact computation, or if classical algorithms can match quantum bounds in bounded-dimension regimes.

## 2. Flagged Findings

The landscape of Kronecker coefficient research has recently experienced high volatility, with several long-standing hypotheses and new conjectures being actively dismantled. Current consensus and the zones of active refutation include:

*   **Refutation of Quantum Superiority Conjectures:** In 2024 and early 2025, Larocca and Havlicek [cite: 1, 2] proposed quantum algorithms for computing representation-theoretic multiplicities (Kostka, Littlewood-Richardson, Plethysm, and Kronecker coefficients). They posited that while classical algorithms exist for bounded Kostka numbers, computing Kronecker coefficients in regimes where the ratio of dimensions of the representations is polynomial would yield a superpolynomial quantum speedup (conjecturing an $O(n^{4+2k})$ vs $\tilde{\Omega}(n^{4k^2+1})$ gap) [cite: 1, 2]. This conjecture was swiftly disproved by Greta Panova in February 2025 [cite: 3, 4]. Panova demonstrated that for large families of partitions (where the dimension $f_\nu \leq n^k$), Kronecker coefficients can be computed classically in $O(n^{4k^2+1} \log n)$ time, entirely refuting the conjectured superpolynomial quantum speedup for these regimes [cite: 4, 5]. The community's rush to assume quantum superiority in representation-theoretic multiplicities exhibits **PATTERN_BASE_RATE_NEGLECT** regarding the existence of heavily optimized classical algorithms for symmetric function evaluations.
*   **Collapse of the Interpolation Hierarchy:** Historically, "reduced" (or stable) Kronecker coefficients were viewed as intermediates bridging the computationally "easy" Littlewood-Richardson coefficients (in `P`) and the "hard" Kronecker coefficients (in `#P`) [cite: 6, 7]. It was believed that understanding reduced Kronecker coefficients might offer a stepping stone to Stanley's Problem 10. However, Ikenmeyer and Panova (2023/2024) proved that *every* Kronecker coefficient of the symmetric group is exactly equal to a reduced Kronecker coefficient via an explicit construction [cite: 7, 8]. This flagged finding confirms that reduced Kronecker coefficients are strongly `#P`-hard to compute and `NP`-hard to decide [cite: 6, 9]. 
*   **Failure of the Saturation Property:** It was long conjectured (e.g., by Kirillov and Klyachko) that reduced Kronecker coefficients possessed the "saturation property" (if $\bar{g}(N\alpha, N\beta, N\gamma) > 0$ for $N>0$, then $\bar{g}(\alpha, \beta, \gamma) > 0$) [cite: 7]. This was formally disproved in 2020, moving reduced Kroneckers away from the Littlewood-Richardson spectrum, a reality strictly mathematically codified by the recent exact equivalence proofs [cite: 6, 7].
*   **Machine Learning Heuristics:** Standard machine learning algorithms (Nearest Neighbors, Convolutional Neural Networks, Gradient Boosting Decision Trees) have been trained to predict Kronecker positivity. Surprisingly, they can perform this `NP`-hard binary classification with $\approx 0.98$ accuracy [cite: 10]. This flags a critical gap between worst-case theoretical complexity and average-case heuristic predictability.

## 3. Problem Statement

The precise objects being interrogated are the **Kronecker coefficients**, denoted $g(\lambda, \mu, \nu)$, which arise in the representation theory of the symmetric group $S_n$. 

### Algebraic Definition
Let $\lambda, \mu \vdash n$ be integer partitions of $n$, and let $S^\lambda$ and $S^\mu$ denote the corresponding irreducible representations (Specht modules) of the symmetric group $S_n$ [cite: 5, 11]. The Kronecker product (tensor product) of these two representations decomposes into a direct sum of irreducible representations:
\[ S^\lambda \otimes S^\mu = \bigoplus_{\nu \vdash n} (S^\nu)^{\oplus g(\lambda, \mu, \nu)} \]
The multiplicities $g(\lambda, \mu, \nu)$ are the Kronecker coefficients. Because they represent dimensions of vector spaces (multiplicities of irreducible modules), they are inherently non-negative integers [cite: 11, 12].

### Character Theoretic Definition
Equivalently, using the characters $\chi^\lambda$ of the symmetric group, the coefficient is defined as the inner product of characters:
\[ g(\lambda, \mu, \nu) = \frac{1}{n!} \sum_{\sigma \in S_n} \chi^\lambda(\sigma) \chi^\mu(\sigma) \chi^\nu(\sigma) \]
where the sum runs over all permutations $\sigma \in S_n$ [cite: 12].

### Stanley's Problem 10
Despite their definition guaranteeing non-negativity, there is no known general combinatorial rule to compute them. In his 2000 list "Positivity problems and conjectures in algebraic combinatorics," Richard Stanley posed Problem 10: *Give a non-negative combinatorial interpretation for the Kronecker coefficient* [cite: 11, 13]. 
In the context of computational complexity, a "combinatorial interpretation" implies finding a family of objects $\mathcal{O}_{\lambda, \mu, \nu}$ such that $g(\lambda, \mu, \nu) = |\mathcal{O}_{\lambda, \mu, \nu}|$, where the description size of the objects is polynomial in $n$, and membership in the set can be verified in polynomial time (i.e., proving the computation is in the class `#P`) [cite: 14, 15].

### Reduced Kronecker Coefficients
The reduced (or stable) Kronecker coefficient, introduced by Murnaghan, is defined as the limit:
\[ \bar{g}(\alpha, \beta, \gamma) = \lim_{n \to \infty} g((n - |\alpha|, \alpha), (n - |\beta|, \beta), (n - |\gamma|, \gamma)) \]
for arbitrary partitions $\alpha, \beta, \gamma$ [cite: 7, 16]. Kirillov’s Problem 2.32 asks for a combinatorial interpretation of these reduced coefficients [cite: 6, 7].

## 4. Status & Bounds

The complexity profile of the Kronecker coefficients is highly constrained by recent theorems separating classical hardness, quantum bounds, and algebraic structures.

### Hardness of Computation (The `KRONCOEFF` Problem)
*   **Status:** `#P`-hard and contained in `GapP` [cite: 17, 18]. 
*   **Details:** Computing $g(\lambda, \mu, \nu)$ exactly when inputs are given in unary is `#P`-hard, as established by Ikenmeyer, Mulmuley, and Walter (2017) [cite: 7, 14]. Because the characters of the symmetric group can be computed as the difference of two `#P` functions, the Kronecker coefficient itself is easily placed in `GapP` (functions expressible as $f - g$ where $f, g \in \#P$) [cite: 4, 18].
*   **The Slivers of Daylight:** The exact complexity is concerned with the daylight between `#P` and `GapP`. The problem of whether $KRONCOEFF \in \#P$ is exactly the formalization of Stanley's Problem 10 [cite: 18].

### Hardness of Positivity (The `KP` Problem)
*   **Status:** `NP`-hard and contained in `QMA`.
*   **Details:** Deciding whether $g(\lambda, \mu, \nu) > 0$ is `NP`-hard [cite: 5, 7]. In a major breakthrough (Bravyi, Chowdhury, Gosset, Havlicek, Zhu, 2023), it was proven that deciding Kronecker positivity is contained in the quantum complexity class `QMA` (Quantum Merlin Arthur) [cite: 13, 14]. This implies there exists a polynomial-time quantum verifier for their positivity [cite: 5].
*   **Implications:** If a certain "character proof method" could unconditionally witness the vanishing of Kronecker coefficients, it would imply `NQP` $\subseteq$ `QMA`, mapping severe consequences for complexity theory [cite: 13]. 

### Classical vs. Quantum Algorithmic Bounds
The most volatile recent updates concern whether quantum computers can bypass classical intractability for bounded dimension ratios.
*   **Quantum Algorithm (Larocca & Havlicek):** Utilizing Quantum Fourier Transforms (QFT) over the symmetric group and its Young subgroups, an algorithm was proposed to compute $g(\lambda, \mu, \nu)$ with high probability in $O(n^4(d_\lambda d_\mu / d_\nu)^2)$ time [cite: 2, 19]. They conjectured a computational hard regime where classical algorithms could not match this [cite: 19].
*   **Classical Upper Bounds (Panova 2025):** If $f_\nu$ (the dimension of the Specht module $S^\nu$) is bounded by $n^k$ for a fixed constant $k$, the Kronecker coefficient $g(\lambda, \mu, \nu)$ can be computed in strictly classical polynomial time: $O(n^{4k^2+1} \log n)$ [cite: 3, 4]. 
*   **Conditional Qualifiers:** This definitively bounds the gap and kills the superpolynomial quantum speedup for the specific parametric regime where $\mu = (d)$ and $\nu = (m)$ [cite: 20]. In evaluating the discrepancy between quantum and classical algorithmic bounds, one must avoid a **PATTERN_CONDUCTOR_CONFOUND**, where the apparent complexity is attributed to the inherent hardness of the multiplicity itself rather than the suboptimal basis representation used by the classical solver. Panova's utilization of polynomial basis dimension growth directly bypasses the assumed intractability [cite: 3, 5].

### The Equivalence Bounds
*   Ikenmeyer and Panova proved $g(\lambda, \mu, \nu) = \bar{g}(\tilde{\lambda}, \tilde{\mu}, \tilde{\nu})$ for specific constructed partitions, rendering the computation of $\bar{g}$ strongly `#P`-hard under parsimonious many-one reductions [cite: 6, 7]. Consequently, Stanley's Problem 10 and Kirillov's Problem 2.32 are identically hard [cite: 6, 9].

## 5. Literature (Primary Sources)

The state-of-the-art relies primarily on papers published or updated between 2023 and 2025. 

1.  **Panova, G. (2025).** *Polynomial time classical versus quantum algorithms for representation theoretic multiplicities.* arXiv:2502.20253v2 [cs.CC]. (Also accepted to TQC 2025 and Computational Complexity). **Significance:** Disproves the Larocca-Havlicek quantum speedup conjectures for Kronecker and Plethysm coefficients in bounded regimes; provides the $O(n^{4k^2+1})$ classical upper bound [cite: 3, 21] [cite: 4, 5].
2.  **Larocca, M., & Havlicek, V. (2024/2025).** *Quantum Algorithms for Representation-Theoretic Multiplicities.* Physical Review Letters, 135, 010602. arXiv:2407.17649v5 [quant-ph]. **Significance:** Introduces the $O(n^4(d_\lambda d_\mu / d_\nu)^2)$ quantum algorithms using S_n-QFT and conjectures classical intractability, later amended to acknowledge Panova's refutation [cite: 1, 2] [cite: 22, 23].
3.  **Ikenmeyer, C., & Panova, G. (2023/2024).** *All Kronecker coefficients are reduced Kronecker coefficients.* Forum of Mathematics, Pi, Vol. 12:e22. arXiv:2305.03003 [math.CO]. **Significance:** Settles the spectrum location of reduced Kronecker coefficients; proves exact structural equivalence to ordinary Kronecker coefficients; proves `#P`-hardness of computation and `NP`-hardness of deciding positivity of reduced coefficients [cite: 6, 7] [cite: 9].
4.  **Bravyi, S., Chowdhury, A., Gosset, D., Havlicek, V., & Zhu, G. (2023/2024).** *Quantum complexity of the Kronecker coefficients.* PRX Quantum 5, 010329. arXiv:2302.11454 [quant-ph]. **Significance:** Places the positivity of Kronecker coefficients in the quantum complexity class `QMA`, complementing the known `NP`-hard classical lower bound [cite: 2, 14].
5.  **Ikenmeyer, C. (2025).** *StdTab $\leq$ Kostka $\leq$ Littlewood-Richardson.* Slides from ICERM 2025. **Significance:** Outlines the complexity implications if character proofs worked for Kronecker coefficients (`NQP` $\subseteq$ `QMA`) and connects to #CircuitSat [cite: 13].

## 6. Attack Vectors

### Live Techniques

1.  **Classical Asymptotic and Dimension Growth (Panova's Approach):** 
    By leveraging the asymptotic behaviors of dimensions and multiplicities, classical algorithms can evaluate the character maps in polynomial time when restricted to specific partition topologies. If the dimension of the vector space $S^\nu$, denoted $f_\nu$, is bounded by $n^k$, evaluating the symmetric functions circumvents brute-force `#P` counting [cite: 4, 5].
2.  **Quantum Fourier Transform (QFT) over Young Subgroups:** 
    A persistent vector is leveraging quantum algorithms to sample from the output distribution of representation multiplicities. By initializing states via maximal isotypic subspace projectors and applying a G-regular representation controlled by a uniform superposition over $H$, weak Fourier sampling can yield the Kronecker coefficients. Even if Panova killed the speedup for $f_\nu \leq n^k$, the broader unconstrained protocol remains the most viable candidate for generalized quantum computation [cite: 19].
3.  **Machine Learning / Heuristic Binary Classification:**
    Trained Convolutional Neural Networks (CNNs) and Gradient Boosting Decision Trees have been deployed to predict Kronecker positivity ($g(\lambda, \mu, \nu) > 0$). They achieve up to 0.98 accuracy. While this does not yield a rigorous mathematical rule, it suggests latent topological features in the partitions $\lambda, \mu, \nu$ strictly govern positivity [cite: 10].
4.  **Geometric Complexity Theory (GCT):** 
    Mulmuley and Sohoni's program to prove `P` $\neq$ `NP` explicitly relies on evaluating positivity of Kronecker and plethysm coefficients to find "occurrence obstructions." Mulmuley conjectured that the positivity decision problem (`KP`) is in `P` [cite: 24, 25]. While deciding positivity is `NP`-hard in general [cite: 7], structural bounds via GCT algebraic geometry remain a massive engine for funding and research [cite: 24, 26]. 

### Exhausted Approaches

1.  **Interpolation via Reduced Kronecker Coefficients:**
    The strategy of finding a combinatorial rule for reduced Kronecker coefficients $\bar{g}(\alpha, \beta, \gamma)$ as a "warm-up" to ordinary Kronecker coefficients is dead. Because they are mathematically equivalent in hardness, one cannot be intrinsically easier than the other [cite: 6, 9]. 
2.  **Assuming the Saturation Property for Stability:**
    Attempts to solve Problem 10 by assuming that if a stretched coefficient $g(N\lambda, N\mu, N\nu) > 0$ then the base coefficient is positive, have failed. This saturation property holds for Littlewood-Richardson coefficients but was definitively disproved for Kronecker and reduced Kronecker coefficients in 2020 [cite: 7].

## 7. Cross-References

*   **Stanley's Problem 9 (Plethysm Coefficients):** Closely related to Kronecker coefficients are the plethysm coefficients, which denote multiplicities in the decomposition of the composition of representations. Panova's 2025 classical algorithm results similarly crushed conjectured quantum speedups for plethysm coefficients under matching dimensional constraints [cite: 3, 20]. GCT links Kronecker and plethysm coefficients closely [cite: 20, 26].
*   **Kirillov’s Problem 2.32:** Asks for a combinatorial interpretation of the extended Littlewood-Richardson numbers (reduced Kronecker coefficients). Now known to be exactly isomorphic to Stanley's Problem 10 [cite: 6, 16].
*   **The Saxl Conjecture:** A major anti-anchor and related open problem. It posits that for the staircase partition $\rho_k = (k, k-1, \dots, 1)$, the Kronecker coefficient $g(\rho_k, \rho_k, \nu) > 0$ for *all* $\nu \vdash k(k+1)/2$. Proving this would establish that the tensor square of the staircase representation contains every irreducible representation as a constituent [cite: 11, 24].
*   **Tensor Square Conjecture:** A broader generalization of Saxl, stating that for every $n \notin \{2, 4, 9\}$, there exists an irreducible representation of $S_n$ whose tensor square contains every irreducible representation with positive multiplicity [cite: 11].
*   **Littlewood-Richardson Coefficients:** The canonical "solved" analog. $c_{\mu, \nu}^\lambda$ describes multiplicities for the general linear group. They possess a beautiful positive combinatorial interpretation (counting Littlewood-Richardson tableaux), compute in polynomial time for fixed lengths, and possess the saturation property [cite: 7, 27]. They are strictly easier than Kronecker coefficients [cite: 6, 27].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnelStJQkmUzMj9XrKVbMYkNC0WuxPIltZdMWgw1FjpG6x60dHoqsCEBVkojDkLhPyyOByiupS18R3tGD_0sUsOdu5eXcBJLOrw8Y0QuVYGvbN8V30Mg==)
2. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4m6R6SkyxOOmJ0qTqV0zNps_EN9ucC5xP_gvnvNCDWvIv17fZWqBxlpAf-DxscSU8VoP4bbUDr9my0MaxgQopmJksMu8_88RK-A9AvD_JutVHxXK4vZxsyvHnIl7g5IO5F6t9DMc4_Ho=)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERefvTiGvG694uIjElzXv7z2-cqYnVbYQTLBVcyG_tXr2_415fDGKp0MFBGRLBMjf34-O7rIhE5HKH0gM5JOqGY7FJdw4phEg21uNHm6CAVNtQprqOocWJDP8mxUT0EaLmhlEzniSMGmS71RMChK-9-O3XAv2kouV9lQQbkAOVDBzCInkzdK4RYfjmDmqm2kgYxUziSFEzV_ShJp-Gz_kkM9KsgT4-yeTNDPAbWI2M6Sq4G-q4iKj0Q_tnsIRWvZUa9R_ek5oXqYA=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXHhv_7sPJmEWEBSuKdso4o7OExOxcXQ5pVPEnHaKLSXLiEDcWQbUVJleAx5ViUdaRNIHoN-QsyycDlwMB97_beUxKSmrOxnJ1sBztn5JMZ0CuOr4xFA==)
5. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkNj4b4x54FzYCR9wmX_2CIpMtknXauH4o7RmLzyz7XUVlhZquo7QD9UPmSwtPP9-iPKddd56NmDClMRrwkvx-v0hPDhuRTmchfDIuGApuSI2ozeRZ)
6. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOMLFmmkB3mkp6yuAzyI-sQAy5zD4CxNs2ktlqbLirjk8DhkzZ0dYj9bgt_ue9TM95JGj5ddNXCqWEKqRkavNk_vVrJQChZvDxsuVpe7NI7bUOG-Uy84Em2P7YbdCvD_kAa08l7mN1Y9CNJQNhwp9W)
7. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6kCG77i-2x3mNS9eMwAygGOHDkkUvIDhf2-6gvw-c4SnKv4MCWuxwCUHpGqyQpB8GvpPI503pf2K0F7yRBKrNfUnqBFuYHSm2QX0ESFIklk3vKsFeb5um5U72J0y8Cs7zEysVF0jYqcdnQXm5Xtt4ItV7YxnJJpjCfLvsvxD25H-p1EBwJXko-5KLmFdZ9-MBqkdgYZ2RKJa744_uoMUQp-TGkil1jwBpvLb-eoQXZiyGRrue-ejPSsgHKNE2zBw5_r01BsN2XlSM7Toc06doGi46FgNKFoSln6E_gDFcxglugccY88u3jTW8SMThI3ly4hhBp6Y7GA==)
8. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCJ6WZf3V2yKGMmCTOrDCrEoTm25r-z1wD_olxv3HPzpZS-yfxkR-4a5uuz181bf_-Hc9YpCAUVRjOhbzhHy2yDvng0xPumSKLdlRRkNmtotg8oAKTsJVRwMMOWY7wH2yWWNPph4CYvpazvxLLslS0pC1H)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHClBtFN5sjbqF0yVXWJ5t658tG1AZvL0XkpycaWxVe3Ue9xyBX3tiHhbbQnjsMi-X-20bYAeW2phHhYgopxJvRSCRhjL31wZf3AXyahEPRM_rjW-jERg==)
10. [worldscientific.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzu8xFv5_luH8E2UCyRcF8cU01tm4nplujE2C8GYKwFmfp1S2d5Ntm1REzftT-yWUUsaWYmAANM2pZty6aa1BG7FT3UmgFI-M33L-rCBJZO2R745yFQZ4jAWyRStjjvGjc-YgXjdIjwYDE4FqQV3_pyRuz-jUsyg==)
11. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdZhMS1-JZjf6-pbEl4CqEByGWpj6CfGhP6xxE1AugxEMT_PJx510EW8FkeB_eGCvmmaN4RgPukHG6PpI7-hjny83foKngPTm7ZhTDkSq_Lkp4H5lUMtQFo6dr1vyvSdGVfhXCm1AQ9sGCBxofQ_gl)
12. [symmetricfunctions.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFA6kRttq0CMpnAka4aqek4_ACDXCxbtQEKgNONVMtCZDfNXdBv-BJZuUQFjTVfXJCiTrKPMipyX_Gg-sZ1gXDwErZzOXRo2KsUbsjOrBF0irXTkVnbL0cyxYxvP7TcGOY_IA==)
13. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRqStr4N9Dk0X_SmJDSx11wJU1TEktzYzzwxWqRlJiRSqI7cLHTIaeCUwkQ0U3rnjhJiC3XW89OOn8vKnqHJVQchL1XYPNZBP85dqvEBXYoJyCrZ-OpyHloIs9K7cHl13uLOjRuka6wC5_QAp3qUFlbZ1TVbIrdtL3huOB378jAGk05x0dmy7nYU5uoLG9nQ==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnnDTFhNdfZM2GM4mkYry4E3kNuiax0Znzaee1OD1K3nV0VtGzvobeuwPUSLRWj7acvzfSBMdyOQBk6y2bik7JRUofFRr9qfnzO5cBS8YVXHGOCqmIaJdesw==)
15. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_BNGd7aXH_N166L_w5ENnD6uewyWGyTEixHE3m24M9UdphEjHhzsAfsCM3dxxHiDdwqwHMfN6S45LrATfDAXDlaY9khkN0AM8YxJ4N5PwZuK3dOwq3atRF3dtdEzieX_HMdam74qOww11TmQmBkRwFm6ZQacizNM2DrM=)
16. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW6fva4-qLRyVHroM6sULJiwLVeB9II4U4UguZIxyyiRMnvrrMNL0Laj0YhpHdO4SAoB0s6h2Z9rcBPtW947Mdn2tqozq8ZRHuQq1jT0WlQ3RtfI8133M_M2wJ6BAJuoFL9qyd05ZVOxLl4dsLQUtVJiny4iNpEaN-B31GEixSrgV3D4tswNsAau941B7gT2Yh6XqbzhewFmuZmJ_5nZwgg-bbRSE3hcS3s-b9AbMxojNNn6KoBpe9HP5tM4n9AdHpELUmm6DrccJlKEuirewy7Y-kuJjgfFnRXm4KaA==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfieO5vHvCWhtDV6ZkI09YlpuCZ_5QtefVs9MV2Q0aWyl7nToIbxaXsfiiQsS-BHj4_ip5-2Xh_z8-9MZZeCbOFUwnAQrwJF7NOhhn9DVF5fBEd4MKk_wQSFE4cz5qx36TMIzP8BVFy0vbPzqJ5zgjXBmxj-SyjMFFmCvKyWXfQNkLKvHWO4iOxSEk6IRZPc7kIxX52ihuhia7U3F-DucRL07Utrrgxw==)
18. [dtic.mil](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpOJqh3OfjRRa0vxf8QKdp-fWVZQ3uHQCO16Xi8SF9q7Fp65MZoheCr9mMaawAThW18IIVz7JPus0RxUaKnmHiYZs0x98r7K_6ZSXuVPK8vBRBNDzVINjLXbMdOMyV0bBymRV_9u_t4w==)
19. [osti.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXwwI3rwkdddmFCVacfyunaS_l8rPrXDi2-Y83C2Z0oqllG4U5iP9xXhPWx4YcEluhJly9lxGIdsn153R4cOzZCwEauf3UkFuebppP-POfEP7Sbb-zNcGlP8A7i1m0gZk=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgIlgPMfJvyYUFHRTqhvuBzFK3ItADhkHUIrOvbXz7s5IecEu7DlH7p_2W9fJfj4MBQ4gpaImF3q3__pMnZcfYRYVOJN2c5I2IgZq2BQA90qvDBnGeuDm8AA==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGACQr74xAXqqmJDFot6DWyCeihrdwr4U3AOZiDvkBjXSUyXFGrsxoozwCU-LSvVp90S1VDGzc_e9Uzw_-ahMPYIMGwpo5Wwjors2K8idNqnypVoTalQ==)
22. [lanl.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4i4Y3k3l-C0uE6EqVDtUUfbRrw92PGrY-wQrFHJYbWLETTDD0XyqloscrDHudlpq9AqtxD2DXPKbWpRW9IOnPQD-xCMxvilxEMxohc9i0D2SNn9lEp5Og53JWI7a_ZS-u-HM0ErzvrAsVAlPxH00RFtD7FXFwXB0sfWF0cQugi0T-JWZD0DJRDWI801dxDRRogRqk3OW-T9ncKMDVAk9AxiSzebrv-jNcc-LCZtBc8TfxFDty7tYWmZPBmdWgGIJz0IF6HYhXh0H68vIF6LF0lqidNzxl_7SPPsJhqQeUsnBfldBfyPeyPYTZNvGy8xlsygvhE6ENTcBR5rphTymIzqE=)
23. [osti.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwxImt03tCSkqjwPj4P8s0yrTJ-S8Rc3U_xd4YIqgFjAB_2I7zfTX64PECysCU9GmpGNp9LGQbYOKormhwkSHmbv_uxut1w92J8AAfIalgutO0j6nLG_pIzw==)
24. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIqN_J6-OibAA2c7yYt32WS6MoQt_-NA53hZJfvYxdLmOkrTP8NISMaQLaaTLDGle-agC4WXpyN7PwLu6KFrRu7QuH2-yysIjzQrZeqAd8Jkhs05VEhMOO5oyUR1Lzull62O97TpU4)
25. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENsmsR9g-7ph6pewT0rKTruPTTz6PbShhu2PUaJVoVXD43Do4_LFykDl3b5G9aFYiEF3HLyQ61z-3OxxBA7zXVede_8ExneNUusUAl0-zZUpamIT4RVFzcO56Oqreggs4yLUERbg==)
26. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNIZAYdhnb5ke-zuPyfMyRqL8cgg2ih_MhDpYwsDNghdh_p_nL2VmynWoKWlmWhJVWu9UHnggTeLL2emYeEw86smNi9K9X_V95G9iwMw--JV_8f7ELYgIs_eG1wpHyS4GAxuqJL5RKhJmvZAYaZRIiQH9NHAQAKxI05Yy5WnYFl3GlZD0Sx7Be4TNEdNJD)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKD5-NcF9d0SzqHxI_rqkliS7AMgj3g4aqDPIl85FRsxIxvk5tjLXpOm5Ch6tmkQU2Ue9jWIY_jDGFKbuELllndY5B_heD-KvgGX2FGj1r4-buhifZSQ==)


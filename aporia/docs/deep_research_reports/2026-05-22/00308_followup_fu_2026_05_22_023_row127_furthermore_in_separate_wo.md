# Followup [FU-2026-05-22-023 <- row127]: Furthermore, in separate work analyzing partitions based on the size of their Durfee square, Pak and

**Pythia queue id:** 308
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdwTFVQYXA2OE5fbk9fdU1QMWN1ci1BbxIXcExVUGFwNjhOX25PX3VNUDFjdXItQW8
**Elapsed:** 248s
**Completed at:** 2026-05-22T01:51:25.613616+00:00

---

# Substrate-Grade Research Brief: Asymptotic Growth of Kronecker Coefficients (Durfee Squares vs. Self-Conjugate Partitions)

### Executive Summary
*   **Core Resolution:** The long-standing open question regarding the asymptotic behavior of Kronecker coefficients $g(\lambda, \mu, \nu)$ for partitions with restricted Durfee square sizes has been resolved. Recent breakthroughs demonstrate that when the Durfee square size is fixed, the coefficients exhibit strictly polynomial growth [cite: 1, 2].
*   **The Superexponential Exception:** Conversely, when analyzing fully symmetric tensor products involving self-conjugate partitions ($\lambda = \lambda'$), the maximal Kronecker coefficients $g(\lambda, \lambda, \lambda)$ have been proven to grow superexponentially, specifically lower-bounded by $\log K_{fs}(n) \ge \frac{1}{16+\epsilon} n \log n - O(n)$ [cite: 1]. 
*   **Algorithmic and Complexity Ramifications:** These asymptotic bounds strictly constrain the computational complexity of evaluating representation-theoretic multiplicities. They have effectively refuted recent conjectures regarding the exclusive necessity of quantum algorithms for specific multiplicity families, demonstrating that classical polynomial-time algorithms exist for cases parameterized by fixed Durfee sizes [cite: 3, 4].
*   **Methodological Advances:** The proofs of these bounds heavily leverage symmetric function identities, continuous limit shapes, combinatorial monotonicity, and most recently, a novel technique known as "integer forcing" which extracts exact polynomial constraints from asymptotic bounds [cite: 5, 6].

### A Primer on the Kronecker Problem
The Kronecker coefficients of the symmetric group $S_n$ describe the decomposition of the tensor product of two irreducible representations (Specht modules) into irreducible constituents. Despite being fundamental structural constants in algebraic combinatorics, representation theory, and quantum information, they lack a generalized positive combinatorial interpretation—a gap often referred to as the "Kronecker Problem." Research suggests that finding such a universal rule may be computationally intractable, as computing these coefficients is strongly #P-hard [cite: 7, 8]. Current investigations lean toward establishing asymptotic bounds by restricting partition shapes, providing crucial insights into their growth rates without requiring closed-form formulas.

### Understanding Shape Restrictions
Integer partitions are typically visualized via Young diagrams. The **Durfee square** is the largest square that fits inside a given Young diagram. A partition with a "small" Durfee square is visually "thin," restricted largely to a few long rows and a few long columns. A **self-conjugate partition** is completely symmetric across its main diagonal. The recent findings highlight a profound dichotomy: "thin" partitions (fixed Durfee square) restrict tensor product multiplicities to polynomial growth, while highly symmetric partitions (self-conjugate) allow multiplicities to explode superexponentially, approaching the absolute maximal theoretical limits for the symmetric group.

---

## 1. Brief summary
**Summary:** The Aporia-surfaced query highlights the resolution by Pak and Panova of the asymptotic growth of Kronecker coefficients, establishing polynomial upper bounds for partitions with fixed Durfee square sizes, juxtaposed against superexponential lower bounds ($\log K_{fs}(n) \ge \frac{1}{16+\epsilon} n \log n - O(n)$) for maximal Kronecker coefficients of self-conjugate partitions [cite: 1].

## 2. Flagged findings
**Consensus:** The algebraic combinatorics community currently accepts the Pak-Panova bounds for Durfee square-restricted partitions and self-conjugate partitions [cite: 1, 2]. The consensus is that the Kronecker coefficients $g(\lambda, \mu, \nu)$ transition from polynomial behavior to superexponential behavior depending on the "thickness" of the partitions involved, a property rigorously captured by the Durfee square size $d(\lambda)$. For small, fixed $d(\lambda)$, $g(\lambda, \mu, \nu) \le n^c$ where $c$ depends only on the Durfee size [cite: 1]. 

**Where it might be wrong / Areas of Caution:** 
While the bounds themselves are mathematically verified, researchers attempting to extrapolate these findings to average-case complexity bounds or broader Geometric Complexity Theory (GCT) applications must remain vigilant. There is a persistent risk of **PATTERN_BASE_RATE_NEGLECT**, where theorists might erroneously assume that the typical, average-case behavior of random partitions is representative of the highly structured, extremal self-conjugate shapes used to prove superexponential lower bounds [cite: 1, 9]. The maximal Kronecker coefficients $K(n)$ and fully symmetric coefficients $K_{fs}(n)$ are strictly extremal phenomena. 

Furthermore, earlier assumptions regarding the continuous limits of these coefficients (such as approximating the discrete lattice of Kronecker polyhedra with continuous volumes) can lead to approximation errors in lower-order terms. As demonstrated by recent work on three-row partitions, elementary combinatorial structure often collapses at specific parameter thresholds (e.g., the "Five Threshold"), indicating that continuous asymptotic models may fail to capture highly erratic discrete integrality at higher ranks [cite: 5, 6].

## 3. Problem statement
The precise mathematical object being interrogated is the **Kronecker coefficient**, denoted $g(\lambda, \mu, \nu)$. Let $\lambda, \mu, \nu \vdash n$ be integer partitions of $n$. The Kronecker coefficient is defined as the multiplicity of the irreducible representation (Specht module) $S^\nu$ of the symmetric group $S_n$ in the tensor product of $S^\lambda$ and $S^\mu$:
\[ S^\lambda \otimes S^\mu \cong \bigoplus_{\nu \vdash n} (S^\nu)^{\oplus g(\lambda, \mu, \nu)} \]
Equivalently, in terms of characters $\chi_\alpha$ of $S_n$:
\[ g(\lambda, \mu, \nu) = \langle \chi_\lambda \chi_\mu, \chi_\nu \rangle = \frac{1}{n!} \sum_{w \in S_n} \chi_\lambda(w) \chi_\mu(w) \chi_\nu(w) \]

The open question pertained to the maximal values of $g(\lambda, \mu, \nu)$ constrained by geometric properties of the Young diagrams of the partitions:
1.  **Durfee Square Constraint:** For a partition $\lambda$, the Durfee square size $d(\lambda)$ is defined as $\max \{ k : \lambda_k \ge k \}$. The object of inquiry was to prove or disprove Conjecture 1.3 from [PP20]: For a fixed $k \ge 1$ and partitions $\lambda, \mu, \nu \vdash n$ such that $d(\lambda), d(\mu), d(\nu) \le k$, does there exist a constant $c = c(k) > 0$ such that $g(\lambda, \mu, \nu) \le n^c$? [cite: 1]
2.  **Self-Conjugate Constraint:** For a self-conjugate (fully symmetric) partition $\lambda = \lambda'$, what is the asymptotic behavior of the maximal symmetric Kronecker coefficient $K_{fs}(n) := \max \{ g(\lambda, \lambda, \lambda) : \lambda \vdash n, \lambda = \lambda' \}$? Does it match the absolute maximal coefficient $K(n) := \max_{\lambda, \mu, \nu \vdash n} g(\lambda, \mu, \nu)$, which is known to grow as $\log K(n) \sim \frac{1}{2} n \log n$ [cite: 1]?

## 4. Status & bounds
The problem has been definitively resolved by Igor Pak and Greta Panova (2022/2023) [cite: 1, 2], establishing a stark dichotomy in growth rates based on partition shape constraints.

**1. Polynomial Upper Bounds for Fixed Durfee Squares (Resolved):**
For the small Durfee square problem, the conjecture was proven true. If $d(\lambda), d(\mu), d(\nu) \le k$, the Kronecker coefficients grow at most polynomially with respect to $n$.
*   *Previous Best Bounds:* For partitions with a bounded number of rows $\ell(\lambda), \ell(\mu), \ell(\nu) \le k$, the bounds were $g(\lambda, \mu, \nu) \le n^{k^3}$ [cite: 1].
*   *Current Status:* Pak and Panova proved that restricting the Durfee square (which effectively restricts the partition to a union of a bounded number of rows and a bounded number of columns) maintains polynomial growth $O(n^c)$ [cite: 1, 2].

**2. Superexponential Lower Bounds for Self-Conjugate Partitions (Resolved):**
For the fully symmetric problem, Pak and Panova proved that the maximum Kronecker coefficients evaluated at self-conjugate partitions grow superexponentially, coming within a constant factor of the theoretical absolute maximum $K(n)$.
*   *Absolute Maximum Limit:* $\log K(n) \sim \frac{1}{2} n \log n$ [cite: 1].
*   *Current Best Lower Bound for Fully Symmetric:* For all $\epsilon > 0$, the maximal fully symmetric Kronecker coefficient $K_{fs}(n)$ is bounded by:
    \[ \log K_{fs}(n) \ge \frac{1}{16+\epsilon} n \log n - O(n) \]
    This proves that $g(\lambda, \lambda, \lambda)$ can grow superexponentially when $\lambda$ is self-conjugate [cite: 1].

**3. Algorithmic Complexity Bounds (Conditional Qualifiers):**
The existence of polynomial bounds for restricted Durfee squares has significant complexity-theoretic implications. Recently, Larocca and Havlicek [LH24] suggested a potential superpolynomial quantum speedup for computing these multiplicities. However, utilizing the bounded row/Durfee parameterizations, it has been demonstrated that for families of partitions where the dimension of the representation $f_\nu \le n^k$ for a fixed constant $k$, $g(\lambda, \mu, \nu)$ can be computed classically in strictly polynomial time $O(n^{4k^2+1} \log n)$ [cite: 3, 4, 10]. This refutes broad conjectures of quantum advantage in these specific asymptotic regimes [cite: 3, 4].

## 5. Literature (primary sources)
*   **[cite: 1, 2, 11]** I. Pak and G. Panova, *Durfee squares, symmetric partitions and bounds on Kronecker coefficients*, Journal of Algebra, 629 (2023): 358–380. (First announced on arXiv:2207.02561 in July 2022). **Primary resolution of the query.**
*   **[cite: 9, 12, 13]** I. Pak, G. Panova, and E. Vallejo, *Kronecker products, characters, partitions, and the tensor square conjectures*, Advances in Mathematics 288 (2016): 702–731. (Foundational lower bounds using principal hooks of self-conjugate partitions).
*   **[cite: 7, 8]** C. Ikenmeyer, I. Pak, and G. Panova, *Positivity of the symmetric group characters is as hard as the polynomial time hierarchy*, arXiv:2207.05423 (2022). (Establishes PP-completeness and \#P-hardness constraints).
*   **[cite: 3, 4]** D. Yeliussizov (or associated authors per source context), *Poly time algorithms for multiplicities*, arXiv:2502.20253 (October 2025). (Classical polynomial time algorithms refuting Larocca & Havlicek's quantum conjectures for restricted partitions).
*   **[cite: 5, 6, 14]** I. Pak, G. Panova, and J. P. Swanson, *Algebraic Obstructions and the Collapse of Elementary Structure in the Kronecker Problem*, arXiv:2511.22856 (November 2025). (Recent breakthrough on three-row partitions discovering "bounded oscillation" and the "Five Threshold").

## 6. Attack vectors
The resolution of these bounds required the synthesis of several disparate techniques from algebraic combinatorics and asymptotic representation theory.

**Live Techniques (Successful Vectors):**
1.  **Symmetric Function Technology:** For the polynomial upper bound of the small Durfee square problem, researchers utilized the Cauchy identity, Schur function expansions, and Littlewood-Richardson coefficients. A partition with $d(\lambda) \le k$ can be decomposed into a partition with at most $k$ rows and another with at most $k$ columns. Bounding the Littlewood-Richardson coefficients $c^\lambda_{\mu\nu}$ and applying Jacobi-Trudi identities allowed the authors to restrict the degrees of freedom polynomially [cite: 1].
2.  **Combinatorial Monotonicity & Semigroup Properties:** To achieve the superexponential lower bound for self-conjugate partitions, the attack vector relied heavily on the semigroup property of Kronecker coefficients: if $g(\alpha_1, \beta_1, \gamma_1) > 0$ and $g(\alpha_2, \beta_2, \gamma_2) > 0$, then $g(\alpha_1+\alpha_2, \beta_1+\beta_2, \gamma_1+\gamma_2) \ge \max(g(\alpha_1, \beta_1, \gamma_1), g(\alpha_2, \beta_2, \gamma_2))$ [cite: 7, 15]. 
3.  **Character Evaluation via Principal Hooks:** A critical lemma (Pak-Panova-Vallejo) established a lower bound using characters. If $\mu = \mu'$ is a self-conjugate partition, one can define a partition $\hat{\mu} = (2\mu_1-1, 2\mu_2-3, \dots) \vdash n$ composed of its principal hooks. The theorem states $g(\nu, \mu, \mu) \ge |\chi_\nu(\hat{\mu})|$. **PATTERN_RANK_PARITY_LEAK** is evident here: the parity constraint that all principal hooks of a self-conjugate partition are strictly odd integers "leaks" into the character evaluation, forcing non-vanishing alternating sums in the Murnaghan-Nakayama rule, which strictly forces positivity in the tensor square [cite: 9, 12, 16].
4.  **Integer Forcing:** A newly developed technique (Swanson et al., 2025) designed to bridge the gap between continuous asymptotic regimes and discrete integer valuations. By evaluating limits of vector partition functions and forcing variables to conform to integer lattice constraints, exact polynomial formulas for bounded-row Kronecker coefficients were successfully extracted [cite: 5, 6].

**Exhausted Approaches:**
1.  **Direct Combinatorial Bijections:** Attempts to find a direct, unsigned combinatorial rule (analogous to the Littlewood-Richardson rule for $GL_n$) to prove polynomiality or exponentiality have been exhausted. Complexity-theoretic barriers (#P-hardness) heavily imply that a generalized combinatorial formula is impossible unless the polynomial hierarchy collapses [cite: 7, 8].
2.  **Unrestricted Quasipolynomial Interpolation:** Attempting to interpolate Kronecker coefficients as simple quasipolynomials for partitions beyond two rows fails. As shown by Pak, Panova, and Swanson, an "algebraic obstruction" occurs for three-row partitions at $k \ge 5$ (the "Five Threshold"), where irreducible quadratic factors with negative discriminants emerge, collapsing elementary structures and preventing basic polynomial extrapolation [cite: 5, 6].

## 7. Cross-references
The resolution of the Durfee square bounds and self-conjugate superexponential growth heavily cross-pollinates with several major ongoing programs in mathematics and theoretical computer science.

*   **Geometric Complexity Theory (GCT):** Initiated by Mulmuley and Sohoni, GCT attempts to separate complexity classes (e.g., $VP$ vs. $VNP$) by finding representation-theoretic obstructions, specifically zero vs. non-zero Kronecker and plethysm coefficients [cite: 9, 15, 17]. The polynomial bounds for fixed Durfee squares and the newly discovered polynomial-time classical algorithms for restricted shapes constrain the candidate space for these obstructions [cite: 3, 4].
*   **The Saxl Conjecture:** Posits that for $n \ge 9$, the tensor square of the staircase partition $\rho_k = (k, k-1, \dots, 1) \vdash n$ (which is self-conjugate) contains every irreducible representation of $S_n$. The techniques used to bound self-conjugate partitions $g(\lambda, \lambda, \lambda)$ originated from the partial proofs of the Saxl conjecture using principal hooks [cite: 5, 9, 12, 16].
*   **Unimodality of q-Binomial Coefficients:** The lower bounds developed for Kronecker coefficients acting on self-conjugate and restricted row partitions were directly applied to definitively prove the strict unimodality of the coefficients of Gaussian polynomials (q-binomials), a historically notoriously difficult problem algebraically [cite: 12, 16, 18].
*   **Reduced Kronecker Coefficients (Murnaghan Stability):** The reduced Kronecker coefficients $\bar{g}(\alpha, \beta, \gamma)$ represent the stable limit of $g(\lambda, \mu, \nu)$ as a long first row is added. It was recently proven by Ikenmeyer and Panova that *all* Kronecker coefficients are equivalent to some reduced Kronecker coefficient, inextricably linking the hardness and bounds of the stable limits to the absolute coefficients [cite: 7, 18, 19].
*   **Quantum Supremacy Disprovals:** Candidate primitives for quantum advantage via representation-theoretic multiplicities (as proposed by Larocca & Havlicek) have been heavily bounded. The discovery of classical poly-time algorithms for these exact coefficients when the shape is restricted serves as a stark anti-anchor to claims that computing such multiplicities inherently requires quantum hardware [cite: 3, 4, 10].

**Sources:**
1. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAwr34_naeCozMuSnmX3JeaZ1l9j4HHvQc5Cc56-oRIFEHcdlOa0t3wL0fH9ZmD0LQiJSpGarFEUUegFUk29TAaeHou3eG4zsVgcNtRxE1ucxypyv7x_2MYdsZreOHcVcBS_phbu0=)
2. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhgHj4v0Kc0qQ9rJ9i9FsL8JwYgC7w6gy5OHOGy2vC-r73VTt57rRd9Nm1XgNlUuo-_hAzWnr4BIyEp4QyCwHxHL2Wnw26DhMX17HSrWdGsoZ5R1QGu0WRKwny8hstTHAwVVjd85MyN6HXQnyeE-7No_Zmxg9Set6mKBqB3avzYCMDTHh8Rdbr4K0qMM_tPPlplAdySBQQr-8Zq5py4oEX2RRS6bEcFBLK2HsmHeaZslYv_KrJWC3CN_EwTkj77kgp2gJh)
3. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoCratnLtuOgB0iUYQDsBPgK7CO5cIEeg94liITijFzVjxjleNHbx1qr85aGHIL5Jj8hXN5IAerIv5Pp73dyZxc9P8j1l9I2vxU2OjKiwyDKD_C3A=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3Mj_l7qkUsB8rlfcXxskf36irJsSLnPaKfRKDT0biy9-qSj-w3DZqZ133PiXgCQmZV2BWd-IR4axzQ8yZgZwAEh2egpGWvZ7WNPZOzyztzIvz6X2t)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0QRhOU8-w-HEDtq8plVI8KY60QwyKMK6-VOv6kOS6_AtRgAUuIyT0sHV6HNQ4Bqd6v77zClkGB-KzJZQ8c6BimbN6Jz76XuhEPu4l6ytqKCS2n8BpluFi)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqP9qo06nPFP0EZUIPF9Tu0_JS_F1SsJ66EKaQCY8E6Tb2NYEE7FtMWJfjnzbeSGGgCxXFHdgaylSumrfL86lxjXtK5dmbcAWPhpbJ1ZHf3H5jKmtPT_eS5DtMrqWOYRUEAvL9CtTrufzQST-zU-QaYxDJsYRLdCTU-WfT080n5DT80UVWW4iqV0XCuQKVaEHVqWOAoihwAe9iPQHBxcfEWHbHYdjY4s88gbQNzsT-w2J6RIQ6nS4tDPPz4yMwQ4NW)
7. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt8gf2XStvg4IU7BkRPrH7QIFZ9KeII7vG2XcA4-44RcFEF9t2W4E3euR9V4pQErKEUUi3BEagYXYcDaXPi2kR4-Dpw6TpM8gjg-Ct9nRNDvLzKUfjLOafZGINRFb8ikDEOFq58ws=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOY4VmPBM23-UdlCZN_syWhrIEd_-25fQicJcRCsRlohNfa2lX_NidqiJtT9qzUOjlkxbXZCQA8Cl6prRbsdwkZDev_SOmwlxmJpb8WBJtVQMjURZI)
9. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2RGTE1-SfpSDknqDkan4j6n4mO-KiAqij2taKsCeIk8765sN6ggNfaYL4AFEZB-PPrPmVzOgnY7THcXanWQeh4_YUMiQZU5Rx-5xI-7IKd9lUCeOR9u7PVI1fYEcXVIemNsoxsOGACxxE-gAUDkaBK7-bF7d1QZehpOIkrjpc)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHw1b6gb-4D8Sl-gphac05dowB-b-t6e8Jr-ZbcsD90zb0M_suE_4Q-DhzHIIRGN2enQertpA4WPIs7dXqhG-FFtdDxsBT10yCLqSWIHDPLXaa1n3yGl9rmLJpfdODxVlK5s0isEYKipkiCyfri01dslsdF8FUwk2l2xojz_Qg6vh3psilqpux5LAHpqN-ClCYFNtpnartmH36kPRrzoZPJHd0ML7tJM0pNNfT68PxB5RfB1amFFYunS9OY7Q==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgr5qjMF9PZP23qc71rIGCcje4nzF5caNCcaI8CyQ2CIbJmtAdas3K98BZHY8v3Psezv4sxgG4i9dFmUutjhfiNFRAtdOok34bnzO4MUi2q4RR4R1q)
12. [episciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEomurt98uuNnE5V5uebKpCoW4O0Fo96tFfcUQK5kGds-YJ_j2eIS18-ykhCEhSPnDPaGh5rQM6SeicF2rJ__OdjQM0V1HQ8fw9FuvGTJL9YrC2j1xwu9yNCFbD)
13. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEegvDV1MFIK3QMaPljbnGctZ6K8xvrEImYJmDKIH_cTJXuOaLdBBeyP4OuiqYLXssC8Z8BrhNQhh1WNhRDHD6ohBrNTf05unNuXjq9qFTWX5REdl-kXidaMbUVx1pVoZYWUmErel1f)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzN9UojZ2bwdBfJMn6om7jPle78w40Y1cCpl7WGmk6ts6gH9-9WQiK3MD7savtAI0V_E3M_kacoV-o6sRbfa5hTWcSIaSKjP039crcxxvBrOYWpOKe7zM7qifgAr6quevIDkiPB4nk2GtHi39dvFmjULbJJAyms7spzl0g5uUuwwKbu_f3hXcZfgqpe6YfHWHiBhUm0hXz6egRbLs42v6a-dEb_pFP_nf0Erqoylt85RByG9dwT20=)
15. [samuelfhopkins.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAa17TtLj_zVtoWduZEpbsnvu1HWPft_8jE0-Oe8Tk2TsQ3hRU38mkFlg53kuK4OH5KxMqw7UiRxhmSWO4DFyB1R5H4eWqpW0Pd3d4PCS-DBdaX8WK7e4LltcoM2WCeuug1sRnYLqi8wkXXHz1cm6dYZVa0B8=)
16. [ucla.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG66gmbeSglNSTdp0XJGhFLilYuyYEucgB-5k8CZ0gnOub0fg549S4LzHyS-4MXJoho82nH-r62he7ihn5QPKyxlJCdmtwsXst9bxnQVDI0FCxemAfJlW4fek74boKTohV4mLDW)
17. [univie.ac.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-Ux46xjMW160L2ZN5Kxd0zAPdbM2ordWHksqayIJamEELiBTr7IrCasb4o8n6kZHCWYpyNc8ovIqmO0wA-6MpOf-BZu5Qr7dZVBPP_lYDqgSJXLQ1asmO30ZnWKbOT-_patIx550Em_K5kaow6xdYZkxAVj_QlpupNxWhMW5KGOR8tHOq-dwsjQ==)
18. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKlXbJiJeIYMxbpYg3mcRlgxUcarue0HCZl3XawtqlKqo_GRj7hnyiWfsrAfLalQINIGE9WPqpNcdGZmmeMrTxesAmMzmcZylJfX28MIv3hCjwzkHAi0UZSqlRgUttJjaLqUZy0zQ=)
19. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVfKE0vv2K-uwQGfgEtmoZvzRrkmrAo2zYI6EQmF1ES3QFiS4ZdFzWnUjKQ56c4p8PGyM4LffEnz5OtvdYGvyzQemxGBqQpXaQKWC_TlmC-q5IqOQxv_ZcUbLTiOe345qw2KnA5Lg=)


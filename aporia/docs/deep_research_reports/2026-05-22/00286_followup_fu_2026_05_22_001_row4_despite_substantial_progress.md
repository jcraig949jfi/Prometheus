# Followup [FU-2026-05-22-001 <- row4]: Despite substantial progress, such as proving the conjecture for Boolean alphabets under specific sy

**Pythia queue id:** 286
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdTS3NQYXNfOExKX0dqTWNQZ2RfZmdRYxIXU0tzUGFzXzhMSl9Hak1jUGdkX2ZnUWM
**Elapsed:** 248s
**Completed at:** 2026-05-22T01:07:13.859547+00:00

---

# Status Update: Pseudo-Calibration Conjecture, Low-Degree Advantage, and Noise Tolerance

**Key Points**
*   The pseudo-calibration conjecture (also known as the low-degree conjecture), which posited a fundamental equivalence between the failure of low-degree polynomials and the failure of the Sum-of-Squares (SoS) hierarchy, has been formally disproved in its quasi-polynomial formulation.
*   Recent research (as of May 2025) demonstrates that specific permutation-invariant planted distributions exhibit vanishing low-degree advantage (LDA) but can still be solved efficiently in quasi-polynomial time, even in the presence of noise.
*   The breakdown of this conjecture fundamentally alters the landscape of average-case complexity, suggesting that while the low-degree heuristic remains a powerful analytical tool, it is not a universal predictor of computational hardness, particularly when confronted with algorithms leveraging anti-concentration and high-error list decoding.
*   Despite these counterexamples, SoS lower bounds remain profoundly relevant; concurrent works have successfully established tight SoS lower bounds for notoriously difficult problems like the Densest $k$-Subgraph and Independent Set on ultra-sparse random graphs. 
*   The relationship between non-vanishing LDA, noise tolerance, and algebraic fragility remains a highly active area of investigation, with consensus shifting toward a more nuanced, problem-specific application of these heuristics.

**The Landscape of Average-Case Complexity**
For nearly a decade, the theoretical computer science community has relied on restricted models of computation—specifically the Sum-of-Squares (SoS) hierarchy and low-degree polynomials—to map the statistical-computational gaps in high-dimensional inference tasks. The pseudo-calibration conjecture served as the vital bridge between these two models, suggesting that the easily computable Low-Degree Likelihood Ratio (LDLR) could universally predict the failure of the highly complex SoS hierarchy. This paradigm was extremely attractive because it provided a meta-theorem for computational hardness.

**Recent Paradigm Shifts**
The fundamental consensus surrounding this heuristic has been severely disrupted by the publication of "The Quasi-Polynomial Low-Degree Conjecture is False" (arXiv:2505.17360). The authors constructed explicit counterexamples demonstrating that vanishing LDA does not universally preclude the existence of noise-tolerant algorithms. Furthermore, the community is grappling with the reality that some planted distributions with non-vanishing LDA can still yield robust SoS lower bounds, decoupling the tight equivalency previously assumed. This report synthesizes these breakthroughs, evaluates current attack vectors, and re-establishes the state of the art in average-case complexity analysis.

---

## 1. Brief Summary

**Prometheus Context Query:** Status update on the pseudo-calibration conjecture, the exact role of noise tolerance, and the nuances of planted distributions with non-vanishing LDA yielding SoS lower bounds.

**Summary:** The quasi-polynomial formulation of the pseudo-calibration conjecture has been definitively disproved by recent constructions utilizing noisy polynomial interpolation for list-decoding, revealing that a vanishing Low-Degree Advantage (LDA) does not unilaterally preclude the existence of noise-tolerant algorithms [cite: 1, 2]; concurrently, the methodology of pseudo-calibration continues to evolve, successfully yielding tight Sum-of-Squares (SoS) lower bounds for problems like ultra-sparse independent sets and densest $k$-subgraphs even when LDA properties diverge from classical expectations [cite: 3, 4]. 

## 2. Flagged Findings

### 2.1 The Collapse of the Quasi-Polynomial Low-Degree Conjecture
The prevailing consensus for the past several years, championed by the Hopkins conjecture, posited that if the Low-Degree Advantage (LDA) between a null distribution (product on $\{0,1\}^{\binom{n}{k}}$) and a planted distribution (permutation invariant) vanishes for degree $D$, no noise-tolerant algorithm can distinguish the two in $n^{\tilde{O}(D)}$ time [cite: 1, 2]. This heuristic served as the bedrock for predicting information-computation gaps in high-dimensional statistics [cite: 5, 6]. 

This consensus has been proven wrong. As of May 2025, Buhai, Hsieh, Jain, and Kothari (arXiv:2505.17360) explicitly disproved the quasi-polynomial low-degree conjecture [cite: 1, 2]. They demonstrated that for any fixed $\varepsilon > 0$ and $k \geq 2$, there exists a permutation-invariant planted distribution on $\{0,1\}^{\binom{n}{k}}$ exhibiting a vanishing degree-$n^{1-O(\varepsilon)}$ LDA with respect to the uniform distribution [cite: 1, 7]. Despite this vanishing LDA—which classically predicts hardness against all $n^{\tilde{O}(n^{1-O(\varepsilon)})}$-time algorithms—the corresponding $\varepsilon$-noisy distinguishing problem can be solved in quasi-polynomial time ($n^{O(\log^{1/(k-1)}(n))}$) [cite: 1, 8].

### 2.2 The Confounding Role of Noise Tolerance
A significant finding that emerges from the recent literature is the misinterpretation of noise tolerance. Historically, algorithms that bypassed the low-degree heuristic (like Gaussian elimination or LLL lattice reduction) were dismissed as "brittle" algebraic methods that fail under minute random noise [cite: 5, 6]. The community assumed that enforcing noise tolerance would inherently rule out these algebraic anomalies, thereby "saving" the pseudo-calibration conjecture. 

This assumption is a prime example of **PATTERN_CONDUCTOR_CONFOUND**, wherein researchers confounded the specific fragility of Gaussian elimination with a universal fragility of all non-low-degree algebraic techniques. The counterexample provided by Buhai et al. relies on list-decoding for noisy polynomial interpolation in the high-error regime [cite: 1]. List-decoding is an algebraic technique that is inherently highly resilient to noise [cite: 2], demonstrating that noise tolerance does not strictly bottleneck algorithmic capabilities to the class of low-degree polynomials.

### 2.3 Non-Vanishing LDA and SoS Lower Bounds
Another flagged finding involves the inversion of the standard heuristic. The pseudo-calibration conjecture originally focused on vanishing LDA implying SoS lower bounds [cite: 5, 9]. However, concurrent works have shown that planted distributions with *non-vanishing* LDA can still yield SoS lower bounds [cite: 5, 10]. Works such as [JPR+21], [JPRX23], and [KPX24] prove SoS lower bounds based on planted distributions where the LDA does not vanish [cite: 2, 5]. This indicates that the low-degree moment closeness is a sufficient, but perhaps not necessary, condition for SoS hardness, or that the specific structural properties of the moment matrices (e.g., in graph matrices and Kikuchi matrices) dictate SoS failure independently of the pure LDA scalar value. 

### 2.4 The Eigenvalue Distinguisher Artifact
Buhai et al. also surfaced a secondary counterexample on $\mathbb{R}^{n \times n}$ matrices, highlighting a potential **PATTERN_RANK_PARITY_LEAK** in traditional spectral analysis. They constructed a pair of planted and non-product null distributions with a vanishing $n^{\Omega(1)}$-degree LDA, yet showed that the largest eigenvalue serves as a highly efficient, noise-tolerant distinguisher [cite: 1, 2]. Because low-degree polynomials cannot exactly compute or approximate these specific extreme eigenvalues under these distribution geometries, the LDA vanishes, yet a simple spectral rank-based parity check (the top eigenvalue) easily solves the problem [cite: 2, 8]. This indicates a profound disconnect between low-degree moment approximations and exact spectral properties.

## 3. Problem Statement

The objects being interrogated are the **Low-Degree Likelihood Ratio (LDLR)**, the **Low-Degree Advantage (LDA)**, the **Sum-of-Squares (SoS) hierarchy**, and the **Pseudo-calibration map** connecting them. 

### 3.1 The Low-Degree Advantage (LDA)
The Low-Degree Advantage measures the closeness of the low-degree moments of a planted distribution $P$ and a null distribution $Q$. It is formally defined as the maximal signal-to-noise ratio achievable by any polynomial test statistic of degree at most $D$:

\[ \mathsf{Adv}_{\leq D}(P,Q) \coloneqq \max_{f: \text{deg-}D \text{ polynomial}} \frac{\mathbb{E}_{P}[f] - \mathbb{E}_{Q}[f]}{\sqrt{\mathrm{Var}_{Q}(f)}} \] [cite: 5]

Alternatively, the LDA can be expressed as the norm of the degree-$D$ truncation of the likelihood ratio $L = \frac{dP}{dQ}$ projected onto the space of orthogonal polynomials with respect to $Q$ [cite: 5, 11]. If $\mathsf{Adv}_{\leq D}(P,Q) = o(1)$, we say the LDA vanishes, indicating that no degree-$D$ polynomial can reliably distinguish $P$ from $Q$ [cite: 5, 12].

### 3.2 The Sum-of-Squares (SoS) Hierarchy
The Sum-of-Squares hierarchy is a sequence of increasingly powerful semidefinite programming (SDP) relaxations parameterized by a degree $D$ (often written as $2\ell$) [cite: 4, 13]. To prove an SoS lower bound (i.e., that SoS fails to solve the problem), one must construct a valid *pseudo-expectation* operator $\tilde{\mathbb{E}}$ of degree $D$ that satisfies the constraints of the planted problem but evaluates to an objective value indistinguishable from the null problem [cite: 14]. The pseudo-expectation must satisfy positivity: $\tilde{\mathbb{E}}[p^2] \geq 0$ for all polynomials $p$ of degree at most $D/2$, which is equivalent to requiring the moment matrix $M$ to be positive semidefinite ($M \succeq 0$) [cite: 14, 15].

### 3.3 The Pseudo-Calibration Conjecture
Introduced by Barak et al. [BHK+16] and formalized by Hopkins et al. [HKP+17, Hop18], pseudo-calibration is a heuristic recipe to construct the pseudo-expectation $\tilde{\mathbb{E}}$ directly from the low-degree likelihood ratio [cite: 5, 11]. The full Hopkins pseudo-calibration conjecture (Conjecture 1.2 in [HKP+17] and [Hop18]) posits that:

*If a statistical distinguishing problem satisfies:*
1.  *The null distribution $Q_n$ is a product distribution on $\{0,1\}^{\binom{n}{k}}$.* [cite: 1, 7]
2.  *The planted distribution $P_n$ is permutation-invariant (invariant under any relabeling $[n] \to [n]$).* [cite: 1, 7]
3.  *The degree-$D$ LDA vanishes ($\mathsf{Adv}_{\leq D}(P_n,Q_n) \to 0$).* [cite: 5, 12]

*Then:*
*There exists no noise-tolerant algorithm capable of distinguishing $P_n$ from $Q_n$ with high probability in runtime bounded by $n^{\tilde{O}(D)}$, and consequently, the degree-$D$ SoS relaxation fails.* [cite: 1, 9]

The precise interrogation revolves around whether vanishing LDA is a *universally reliable proxy* for SoS hardness and inherent computational intractability when protected by structural symmetries and noise injection [cite: 9, 13].

## 4. Status & Bounds

### 4.1 Status of the Conjecture
*   **Quasi-Polynomial Regime:** **FALSE.** The quasi-polynomial formulation of the low-degree conjecture is explicitly false [cite: 1, 2]. There exist distributions where $\mathsf{Adv}_{\leq n^{1-O(\varepsilon)}}(P,Q) \to 0$, yet a noise-tolerant distinguisher operates in $n^{O(\log^{1/(k-1)}(n))}$ time [cite: 1, 8].
*   **Logarithmic Regime ($k=1$ case):** **TRUE.** Concurrent work [HKK+25] demonstrates that for $k=1$, a vanishing degree-$O(\log n)$ LDA does indeed imply the failure of all distinguishers for the corresponding noisy distinguishing problem [cite: 2]. 
*   **General SoS Reductions:** **NUANCED.** The meta-theorem "vanishing LDA $\iff$ SoS hardness" is fundamentally fractured. While vanishing LDA is no longer a strict prerequisite (due to non-vanishing LDA proofs [cite: 5, 10]), pseudo-calibration remains a highly effective *technique* for engineering moment matrices when applied contextually [cite: 15, 16]. 

### 4.2 Current Best Bounds on Associated Problems
While the meta-conjecture has collapsed, the techniques born from it (graph matrices, Kikuchi matrices, Fourier characters) have led to state-of-art bounds on specific statistical-computational gaps:

*   **Densest $k$-Subgraph [JPRX23]:** In the hard regime predicted by the log-density framework, SoS lower bounds of degree $n^{\delta}$ have been established for $k \leq n^{1/2}$ [cite: 17]. The result matches the algorithmic threshold, showing SoS fails to improve the approximation factor $n^{1/4}$ when $\gamma < 1/2$ and $\alpha > \beta\gamma$ [cite: 4].
*   **Independent Set on Ultra-Sparse Random Graphs [KPX24]:** A major breakthrough achieved degree $2D$ SoS lower bounds for Erdős-Rényi random graphs $G(n, d/n)$ with average degree $d = O(1)$ [cite: 16]. The bound proves that SoS fails to certify the largest independent set is $o(\frac{n}{\sqrt{d} D^4})$, reducing the integrality gap of the Lovász theta SDP by at most a factor of $O(D^4)$ [cite: 16, 17]. This was the first >4-degree SoS lower bound for ultra-sparse graphs [cite: 16, 18].
*   **Noisy $k$-XOR [BHJ+25, 2604.10457]:** For the noisy $k$-XOR problem, algorithms run in $n^{D+O(1)}$ time requiring sample size $m \geq 2^{O(k)} n \log n \max\{\delta^{-11}(n/D)^{k/2-1}, \delta^{-2}\}$ [cite: 19]. The low-degree lower bound dictates that if $m = O( \frac{1}{e^{k/2+2}k^{k/2}} \frac{n^{k/2}}{D^{k/2-1}\delta^2} )$, no degree-$D$ polynomial can distinguish the distributions [cite: 19]. 
*   **Tensor PCA:** For $k=3$ (3rd-order tensors), low-degree polynomials require runtime $\exp(n^{\Omega(1)})$ in the hard regime where the signal rank $r \gg n^{3/2}$ [cite: 6, 11].

## 5. Literature (Primary Sources)

The following primary sources constitute the vanguard of the current discourse on this open problem:

1.  **[Buhai, Hsieh, Jain, Kothari, 2025]** *The Quasi-Polynomial Low-Degree Conjecture is False.* arXiv:2505.17360 (May 23, 2025). 
    *Significance:* The definitive counterexample to the Hopkins conjecture. Introduces the list-decoding construction showing $n^{1-O(\varepsilon)}$ vanishing LDA with quasi-poly time algorithms [cite: 1, 2]. Also details the non-product $\mathbb{R}^{n \times n}$ eigenvalue counterexample [cite: 1, 2].
2.  **[Wein, 2025]** *Computational Complexity of Statistics: New Insights from Low-Degree Polynomials.* arXiv:2506.10748 (June 12, 2025). 
    *Significance:* A comprehensive 50-page survey reviewing the pseudo-calibration conjecture, defining the LDLR framework, acknowledging the Buhai et al. counterexamples, and mapping the known statistical-computational gaps across domains like planted clique and Tensor PCA [cite: 6].
3.  **[Kothari, Potechin, Xu, 2024]** *Sum-of-Squares Lower Bounds for Independent Set in Ultra-Sparse Random Graphs.* STOC 2024 (arXiv:2406.18429).
    *Significance:* Resolved a major open problem by establishing tight spectral norm bounds on graph matrices without losing $\text{polylog}(n)$ factors, yielding the first $>4$-degree SoS lower bound on ultra-sparse random graphs [cite: 16].
4.  **[Jones, Potechin, Rajendran, Xu, 2023]** *Sum-of-Squares Lower Bounds for Densest $k$-Subgraph.* STOC 2023.
    *Significance:* Provides degree $n^{\delta}$ SoS lower bounds for the Densest $k$-subgraph problem, matching the log-density threshold predictions and directly employing pseudo-calibration techniques [cite: 17].
5.  **[Bresler, Huang, 2022/2026]** *The algorithmic phase transition of random k-SAT for low degree polynomials.* / *Average-case reductions for k-xor and tensor pca* (arXiv:2601.19016).
    *Significance:* Establishes the sample complexity and runtime tradeoffs for low-degree tests in distinguishing planted versus null $k$-XOR models [cite: 19]. 
6.  **[Ahn, Medarametla, Potechin, 2020/2021]** *Graph Matrices: Norm Bounds and Applications.* 
    *Significance:* Foundational framework isolating the analytical ideas of pseudo-calibration into manageable graph matrix trace methods and Fourier diagram evaluations [cite: 14, 20].

## 6. Attack Vectors

The landscape of attack vectors has shifted dramatically from monolithic reliance on LDLR to nuanced structural analyses of moment matrices and anti-concentration bounds.

### 6.1 Exhausted Approaches: Universal Pseudo-Calibration
The "dream" of pseudo-calibration was a black-box meta-theorem: prove LDA vanishes, automatically deduce that the pseudo-calibrated moment matrix $M \succeq 0$, and thus declare algorithmic intractability [cite: 21]. This approach is largely exhausted as a universal theorem. The community exhibits **PATTERN_BASE_RATE_NEGLECT** by continuing to assume that because low-degree heuristics correctly predicted thresholds for Planted Clique and Sparse PCA, it would scale to all structured distributions [cite: 5, 6]. The heuristic failed to account for the base rate of algorithms operating entirely outside the polynomial coefficient paradigm, such as those relying on anti-concentration [cite: 22]. Furthermore, reductions from planted clique often strictly require hardness of detection, meaning the standard tools fail if there is a detection-recovery gap [cite: 11, 23]. 

### 6.2 Live Technique 1: Noisy Polynomial Interpolation & List-Decoding
The active technique to shatter these conjectures utilizes high-error list decoding [cite: 1, 2]. The attack vector operates by encoding a signal into a Reed-Solomon or related code. By corrupting a massive fraction of the points (noise injection), the distribution looks locally indistinguishable from uniform, ensuring the LDA vanishes [cite: 2]. However, list-decoding algorithms (like the Sudan or Guruswami-Sudan algorithms) are not simple low-degree polynomials; they involve root-finding of algebraically constructed bivariate polynomials [cite: 2]. This root-finding step acts as a highly non-linear, noise-robust distinguisher that perfectly breaks the paradigm [cite: 1, 2].

### 6.3 Live Technique 2: Spectral Norm Bounds on Graph Matrices
For establishing positive SoS lower bounds, the frontier technique is the granular analysis of graph matrices and Kikuchi matrices. 
1.  **Pseudo-Calibration:** Define pseudo-expectations $\tilde{\mathbb{E}}$ matching the planted distribution's low-degree moments [cite: 15].
2.  **Fourier Decomposition:** Decompose the moment matrix $M$ into a sum of graph matrices indexed by Fourier characters $\chi_E$ over the Boolean hypercube or Gaussian space [cite: 15, 20].
3.  **Norm Bounding:** To prove $M \succeq 0$, one must show that the spectral norm of the error terms (non-empty Fourier shapes) is strictly dominated by the identity term [cite: 3]. 
4.  **Tree-like Component Tracking:** The state-of-the-art methodology, perfected in KPX24, involves tracking trace constraints across tree-like components to achieve spectral norm estimates accurate to within an absolute constant factor, eliminating the poly-logarithmic losses that previously killed bounds for sparse graphs ($d = O(1)$) [cite: 3, 16].

### 6.4 Live Technique 3: Direct Matrix Chaos and Flattening Parameters
Recent bounds have removed logarithmic dependencies by leveraging advances in matrix concentration inequalities and matrix chaos. Works like [BLNvH25] compute matrix flattening parameters to bound the spectral norms of hypergraph matrices sharply [cite: 14]. This technique is actively being used to certify upper bounds on the independence number of $\ell$-uniform hypergraphs to $O(\sqrt{n}/p^{1/\ell})$ [cite: 24].

### 6.5 Live Technique 4: Eigenvalue Distinguishers and Anti-Concentration
For real-valued matrices (e.g., $\mathbb{R}^{n \times n}$), researchers use anti-concentration properties [cite: 22]. Even when low-degree moments of the spectrum match exactly up to degree $O(\sqrt{\log n / \log \log n})$ (making LDA vanish), the extreme tails of the distributions differ [cite: 22]. A simple power iteration to find the maximum eigenvalue operates outside the strict bounded-degree polynomial framework (requiring high degree to converge exactly), yet it is highly efficient and robust to Ornstein-Uhlenbeck noise [cite: 2, 8].

## 7. Cross-References

The collapse and refinement of the pseudo-calibration conjecture reverberates through a massive web of statistical-computational gaps.

### 7.1 Related Open Problems
*   **The Sparse Hypergraph Hardness Regime:** While dense hypergraph planted cliques are well-understood, the low-degree hardness of finding large independent sets in sparse random hypergraphs remains a frontier [cite: 25]. Current open questions focus on whether SoS lower bounds can be rigorously established for $k = o(\sqrt{n})$ in $\ell$-uniform semirandom hypergraphs without suffering logarithmic degradation [cite: 14, 24].
*   **Random Regular Graphs vs. Erdős-Rényi:** Transferring graph matrix norm bounds from i.i.d. $G(n,p)$ distributions to $d$-regular graphs. Recent work (e.g., [JPRX23], [KPX24]) has initiated this transition, but extending the bounds for $d=O(1)$ in sparse regular regimes remains an active, open problem [cite: 3].
*   **Side-Information and Computational Thresholds:** How does the introduction of side-information shift the phase transitions, particularly on sparse random graphs? Identifying the Otter's constant relating to tree enumerations for correlated graphs ($G_1, G_2$) under hidden bijections remains highly speculative [cite: 21].

### 7.2 Anti-Anchors
*   **Planted Clique vs. Planted Coloring:** Planted clique ($k \ll \sqrt{n}$) is a classical noiseless problem that lacks noise-robustness, making it an anti-anchor for certain theories of noise-tolerance [cite: 6, 9]. The community must contrast this with problems like Planted Coloring [cite: 26] and Tensor PCA [cite: 27], which offer continuous noise parameterizations (Signal-to-Noise Ratio, SNR) [cite: 6]. 

### 7.3 Candidate Primitives
*   **Franz-Parisi Criterion / Overlap Matrices:** Derived from statistical physics, the Franz-Parisi criterion is a second-moment method that avoids some pitfalls of the LDLR by focusing on "low-overlap" regimes [cite: 4, 23]. It is emerging as a candidate primitive to supplement or replace pure LDA when attempting to predict computational intractability in rugged free energy landscapes [cite: 23].
*   **Approximate Message Passing (AMP) and State Evolution:** AMP dynamics provide a rigorous algorithmic counterpart to SoS lower bounds. The state evolution of AMP on dense random matrices closely mirrors the tree-shaped Fourier diagram evaluations utilized in pseudo-calibration [cite: 12, 20], serving as a candidate primitive for establishing upper bounds that meet the SoS lower bounds. 

---
*End of Brief*

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeAuIJWxCfMtzwKuGaCWErocN4VWKoGUuxo43vy6Z2QdJi0ESdOxKfOc5kMx0cJaYqBew0tl3sK_pFWahcpdbSYMjDyyzEEczrbzdosPCRpHKrqP4wYQ==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRwpBrZw-RRks-aknWkERzNPSgLZGvNai8z015IcnqWvWEMLkFVhKKu3uSe9DejxuA72qDmtJBoN6Cjr7HX9lkqwNNIbhztwP1l82m1RLym-4Bkjc1Kg==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcuuhhaiZ79wcwqOkUYWooFkxiSWSfD4hn-FW8lD6xvuDB8L3EmndgKFKnwktlXuxzyXToZwXd7Q1qHgUKGS5gvTVVsC0XARxo58QW2T1ksh_eXXidGA==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXkOs8kN3_NrVFbfxOF7_qkdSzSwzPd6OyBCmvpjpPZ1rJ7YICpIWwKhgtZXYZYDh268-VE8hcUxHYeBjBJuRoTHPmYcZS9mPw5kyAyQjQiycbV8i6XA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZxNKuti84IYBAU5nYvaORl2qRRjhWgOL69z-a0zArLLz4JylvSjkfvKrPbqxHik3NdzNj_DX7wsNOaMFIHG6w4aZH7JYQF8ylrM81FDbKcssVmaZ67ITp6A==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIuAX6FEaN1jrsdd20lmo2LiWe5OMKLe2k6BAB-UYxH5F4KQlL9694YDtb9p8CIlLUncmyZmAFrj6TMt_M_s2tuIbJpoVLPt8nRooG_T4uqGIT87_Pzw==)
7. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdEFhEYD7u4WyZ-92db-IjmU3cst1EmxNmhrwqO0cm0mMRNFHmBKVu-5_TNs6S6GGWmv3fARgMNjM-B8mawlttlCeyXTGDh6ruKjcKWn598KS5XhPo87Kqascm_1lTgk_Th_58)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENmGOZDQxSnULejupTPyMtI0qrF7LGTjv9reOO7GjPVLtYq3JIWE0wWXq4mWz3Zi9PCaMglSuLByQChLTzV8nsd2gGaLR9N0Ui-HhPTx8UaMVAbiWsHkRUdQMP1VHmnf86rMeejNbTApMHqayk492eX1-Dlq82meAXbJ7C-28LJJA8AqXYber0PEVYKIN98Hpw1QxfYiMt3jSBDgU=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHw9VrAiWkcw6YF2WtcYuocTOH2mA1pcXRGrb1tmqMtJamE1aWNrkibIBKGK7w-RM2bHBdON8qVuCEOkjqLrs8GBnWLri5eCTElkw69Wtowf2qpYyFwpW2wQA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGV1c6gF03wGJaQuqjdu_dI-BaQ2aFsV84nFdsxb-Lr8o4KfEPXn04FgywGAF2W95JQGbbrUnJjD_iZYQfCC_1jKPhJ75Fz7GX19l9ehr8UqmVOlpTW_VHoHMubAynhij-l9Q==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJEXerB4kjgP9eXQdkxdJ4C2QbpWv-g1mRcNKI4zXjItuYs0cRRd2FcrzH9n2PUuS3brjufw-chMKfaSVPnxyAOHoYx7z5RH3DrXUuDbk9bYUOlkTkAg==)
12. [ucsd.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE880HPDYHpe8chFfosrp4GOEq1HOd0WBgHCE1K77nIxj9eYtgj1jpO-gcvT2nWl5J5PG9AILg2zIQ3di5dURoTsQbLgSoKvDwJpJy7gZxpZJkkZlLxxbc91kyfXMcM6JaSGHia7UEfRvIM0P26GyQ=)
13. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBSppX0zQt1044yS7z57C-Nj1Qku0fGlbOM39aZEgpwPwnVU5Cp8nOaYu-zr_rNXXmVPwXT5m63_-e9V0fQpNulPy1KLqNzaNi92oAsUlLzMeGB87lpDgFgyweeI6dO3x4rih11MGE2Uk9vFDADrJj7UqUptQPr--5z87Sf5Dg8ilTzkXkjm2iEGoeSoQnbAk=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFU9LrJwdi3ytXXQqp3sxWjNs-H1q_7bJ3KisM1pwRAtvKBgxFXdEFNYVmb4gWZvnR6I-jaOJ5Ir_pr-ZhGpIaG4ks2zrv_4_xPeY4fUfs4nS8aEuXnm4Ecw==)
15. [iliasdiakonikolas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbD46sBbCwIPAdZagy5gnH601VQNR4pIkkjvlhPtSE5hfjq8IlEJDanZu14wev0vASA3Tja6INiBCg5twtcbwxBzcWG8C98ITizsaflmgnJXvRY6cBOpcGlfQhkTqT8NbwD7NXM0ZKs-Pp7IsaygEcPw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaLT20Xl0cDf4SEnuMA-pESkiqcmvq8m0OTOBQagbdPmBQ_84fwR7xx-X5b0qCHWzAdGdOlkNAR97Juei_ICbqDMwMa9vkD1I9DnWoz4PcOpddQazinw==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEc1ZI--nNMhJGniMXyMzITEaENm_QWTHSfVAgYxnk8WpXcn7yG72O0XuzfVJc3EEp5ho2buM80QWqne4-CZfDrlqDBbC2U9X0lR-rFQmaf4dHyct2-chMR-oOXB780__37sdA28I_kRQ3M3g5xZOJhdIV9Au5zi21n1md9jU=)
18. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP8IUSdcK9iV5y7lhJu6SXIedZ0_FI8nhTa82iLnoruDGpa148Izg1j-U8LUzwPoW1faQpe9biXhUjNuSlovl8c4ASl-KMpcm5Klhnkg8rp0_3-VpS9TfkKpnLVuR2AkmeDGPy2OhrDZXtul7sqzYVhFOFGVuKyernWk5lVJApA5REt647s3SgntTsptCU0OuY6T7JelMo2zDodCfaZ8LIAQuqg2p_TQn5)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhkCCiEvbYcvSsBe2hi36RHohv7JifBckZx9924O1Ei9iMEwMSceD1B9jjZutt2-yEwcumyN2yrlJqQ6m-YxzkSxI62_qdhSstQrO0LrTY__zSesIgPEzZsQ==)
20. [chrisjones.space](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW5lZjH6-Vo7d-kNfub_ZnJA9BN9tdsCke8PLznIeOjjMsGSxQa7WJ2Iy7K8L_oyh48g329SWhHWLb9u9kIg_fP9bO2YWGmB5xoB_cpSwTCuW6yr-Kq8Y4so_uP0vKepvxXoCbzS7c-D9WHKaKe7cH9R9hcl5Ca3O9mi4=)
21. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJzAmApWwRFG6j1RCU66NxZtcy6nrgZVFywqTGnJsFiUo3XPlw59MXsptOdyQwx66KBdob-uNKD4oO9N1zBN4qMmCoudLpP3nZAkQj6ZCLT5uNBjx7LlnFXhBE9s9U158vGjYvq0mMpzh6M_3j_jzXD9oCPMuSBrB-uF90)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMLxxiKMgfFwE_lp8n0-5inclTFh7GAlx1Vcbmv4W_SAlU32TGXaHEP6-0uuvI3GTkwO4uZO93LCeDFQGQYtxxkBGyNmjAf4E4K7kWZ60HD6i9VGUcxPYdJ1WTpmXk9ZgoFdHJAGdkKP8-tzYVwZfcSm4wMeGIwL2zb0Plf5z0Ac1Ff0cyetFAYEj-CPcrMZTOD4ZcV_KTcOIFQic=)
23. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEl-xmWgbR6ojvVrRRS7qf9DsYwKUHh4D3FxqF7PJA1-1jYsrkTUONPRmwDXSgpAxP2adXoFxQNJLL1y6yS5_sGKsgWKfynV1L0Dj91qReVhoCmLPRRLFCQJaP9uBDZKy9OiqvGUNUwQH57BcleCVW2CfiMuMoLzSd4TweuaAhpprQ=)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKUYV8JrZZN5ALwwzpAbm5bC0xCbtn6doohnw8XRKY82NtnYbnuImKf1JO2AnzsETzZF2tYgkUn_28dDuV8s0q8UO1PChERyBfoncJBEgRSGNosVB6jhNpQXFhMQXSDZTBHe2DMcQjSas16TfkvJzliFjeHkB8_sUEhrod98xc984rq7hCJQLQ5TTbRJYJ9Wgb2yMFNB1nVkrb5gSluX8=)
25. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-PL0vHto5uqtVI5yzMLdNP2hdXi_hpk0yuVPWgryI-ZkYOvQbJabruRmkIVKKDbNoinVO_loD7KvO1fviXxbLeODpJxHeOwrpw-a17nMGeLxgVBD5dSa2kQrItEPP4KdYx2PuVZeMePoKKP4zAx_M2fbw1Q6-2URu23_23vbgEUJHaol22ZnDL0rgaHtDpfZNbBmWrYCZr43rWOJRkOivpUjKl_q_iJUHOfNWSi37)
26. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpRPGwm8G0Ww8YDWFFz8PYZrVTCm-COA_hmND9OV1tCQe9uEDdxLhtif8dGYi8Alb0jeKvf-YCPrA66I9DNdAi7mO4-Xp8MfQqDutWJ83DTw==)
27. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElwB2iHU01NdDuqhoSDCQI6O7_n-MrQxPh848zhDdK4cmEUFHRdDH__bI87iMY9TLMtsU0k6IsZzGvCk26KIbZ-lbcd8Seax4wyl0RTwBkZNdXdZWqlchZGZfFLxXa0hX1nJ51M1djg9lmOunBaOB0XC8JJQCoEP4umMVWxQ==)


# Prompt 11: Sum-of-squares hierarchies for tensor problems 2024-2026

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc4amdCYXRtaUtJbmdfdU1QdU5iTWdRYxIXOGpnQmF0bWlLSW5nX3VNUHVOYk1nUWM
**Elapsed:** 276s

---

# Project Prometheus: Survey of Sum-of-Squares for Tensor Problems (2024–2026)

**Key Points:**
*   The computational threshold for Tensor PCA (T#73) is no longer exclusively the domain of the Sum-of-Squares (SoS) hierarchy; recent Normalized Stochastic Gradient Ascent (NSGA) and Kikuchi message-passing algorithms match SoS sample complexity limits.
*   The exact tensor spectral norm threshold problem has been proven to be structurally $\exists\mathbb{R}$-hard as of 2026, transitioning tensor complexity from discrete NP-hardness to real algebraic intractability. 
*   Noisy rank-1 tensor completion can now be deterministically achieved with minimal observations using novel Semidefinite Programming (SDP) propagation masks without requiring uniform randomness.
*   Type-2 constants (T#72) for the Banach space of $\ell_p$ injective tensor norms provide optimal bounds on the variance of random tensors, tightening the geometric arguments used in SoS lower bounds.

**Scope of Sum-of-Squares (SoS)**
The Sum-of-Squares hierarchy remains the theoretical gold standard for average-case complexity and robust estimation. Rooted in real algebraic geometry, the framework bounds the computational tractability of polynomial optimization by escalating the degree of polynomial certificates.

**Paradigm Shifts (2024–2026)**
The literature from 2024 to 2026 demonstrates a distinct shift from relying solely on SoS as a general algorithmic hammer toward using SoS lower bounds to characterize fundamental computational limitations, while developing highly specialized, faster algorithms (like NSGA or hypergraph Kikuchi methods) that achieve identical statistical-computational tradeoffs with significantly reduced overhead.

## 1. SoS Hierarchy Primer (Concise)

The Sum-of-Squares (SoS) hierarchy is a systematic method for relaxing NP-hard polynomial optimization problems into solvable Semidefinite Programs (SDPs). Derived from the foundational work in real algebraic geometry and generalized algorithmically by Lasserre and Parrilo, the SoS hierarchy attempts to certify the non-negativity of a polynomial over a constrained semi-algebraic set.

### Positivstellensatz Background
At its core, SoS relies on representations of positive polynomials. Hilbert's 17th problem asks whether every globally non-negative polynomial can be written as a sum of rational squares. For constrained domains, the theoretical backbone is provided by various Positivstellensatz theorems [cite: 1]. Putinar's Positivstellensatz states that if a semi-algebraic set $K = \{x \in \mathbb{R}^n \mid g_i(x) \ge 0, i=1,\dots,m\}$ is Archimedean (compact with a known bounding ball), any polynomial $f(x)$ strictly positive on $K$ can be represented as:
\[ f(x) = \sigma_0(x) + \sum_{i=1}^m \sigma_i(x) g_i(x) \]
where $\sigma_i(x)$ are Sum-of-Squares polynomials [cite: 2]. A degree-$d$ Positivstellensatz proof restricts the maximum degree of the polynomials in this expansion to $d$. If such a decomposition exists, it serves as an efficiently verifiable certificate that $f(x) \ge 0$ on $K$ [cite: 1, 3]. 

### The Lasserre-Parrilo Dual Perspective
Algorithmically, the search for the polynomials $\sigma_i(x)$ is framed as an SDP. The set of polynomials up to degree $d$ can be parameterized by a vector of coefficients. For a polynomial to be a sum of squares, its coefficient matrix must admit a positive semidefinite (PSD) Gram matrix decomposition [cite: 1]. 

Conversely, the dual perspective (often associated with Lasserre) utilizes *pseudo-expectation* operators, denoted as $\tilde{\mathbb{E}}$. A degree-$d$ pseudo-expectation is a linear functional over polynomials up to degree $d$ that mimics the behavior of a true probability distribution. It satisfies $\tilde{\mathbb{E}}[cite: 4] = 1$ and $\tilde{\mathbb{E}}[P^2] \ge 0$ for any polynomial $P$ of degree up to $d/2$ [cite: 1]. In the constrained setting, the localizing matrix condition requires $\tilde{\mathbb{E}}[P^2 g_i] \ge 0$ [cite: 1, 2]. The existence of a valid pseudo-expectation operator certifies that the SoS relaxation has not been able to refute the existence of a solution. 

### Levels of the Hierarchy
The "level" $k$ of the SoS hierarchy corresponds to the maximum degree of the polynomials considered ($d = 2k$). Because there are $\binom{n+2k}{2k}$ monomials of degree up to $2k$ in $n$ variables, the moment matrix constructed in the SDP has dimensions $O(n^k) \times O(n^k)$. While low levels ($k=2, 4$) can be computed for moderate dimensions, higher levels become computationally prohibitive but offer exponentially stronger theoretical guarantees against adversarial or noisy distributions.


## 2. SoS for Tensor Rank Problems

Understanding the rank of a tensor is fundamentally more difficult than matrix rank. Tensor rank, defined as the minimal $r$ such that a tensor $T \in (\mathbb{R}^d)^{\otimes k}$ can be written as a sum of $r$ pure rank-1 tensors $T = \sum_{i=1}^r a_i \otimes b_i \otimes c_i$, is known to be NP-hard to compute in the worst case [cite: 5, 6]. The problem exhibits unique phenomena, such as overcompleteness, where a tensor's rank can far exceed its ambient dimension $d$, allowing for unique decompositions even when $r \gg d$ [cite: 7].

### The Hopkins-Schramm-Steurer Framework
The baseline for analyzing average-case tensor decomposition with SoS was established by Hopkins, Schramm, Shi, and Steurer (2016-2017). They demonstrated that the SoS hierarchy could effectively decompose overcomplete tensors by leveraging the implicit constraints of the tensor components. Their robust spectral algorithm bypassed the computational barrier of full SoS SDPs by using sum-of-squares proofs to certify bounds on the singular values of matricized tensors [cite: 5, 7]. Specifically, they showed that SoS could certify the injectivity of random tensor operators, leading to sub-quadratic time algorithms for robust tensor decomposition in regimes where classical spectral methods failed [cite: 7, 8].

### Subsequent Refinements (2018–2026)
Research between 2024 and 2026 has deeply refined our understanding of the algebraic barriers in tensor rank and spectral problems. In a pivotal 2026 advancement, the computational complexity of the tensor spectral threshold was classified precisely. While earlier work by Hillar and Lim established NP-hardness for tensor rank, the continuous formulation of the tensor spectral norm was widely approximated using higher levels of SoS [cite: 6, 9]. 

However, recent theorems established that the decision version of the tensor spectral norm (determining if the norm exceeds a rational threshold) is $\exists\mathbb{R}$-hard (Existential Theory of the Reals) [cite: 9]. This proves that the difficulty of tensor spectral norm computation is not merely due to combinatorial multi-linear encodings but is structurally hard at the fundamental level of real algebraic feasibility [cite: 9]. The reduction from bounded quartic equality feasibility shows that exact exact optimization over the tensor spectral domain resists a complete characterization of tractability, explaining the strict necessity of bounding the SoS hierarchy to approximate, rather than exact, recovery [cite: 9].

Additionally, new sum-of-squares formulations have tackled structured tensors such as biquadratic forms, improving upon historical decompositions. In 2026, researchers characterized necessary and sufficient conditions for positive semi-definite biquadratic tensors to have exact SoS rank limits, revealing deep connections to Riemann curvature tensors and covariance tensors in statistical applications [cite: 10].


## 3. SoS for Tensor PCA

The Tensor Principal Component Analysis (Tensor PCA) problem seeks to recover a planted low-rank signal from a heavily noised observation. For a $k$-th order tensor, the observation is $T = \lambda v^{\otimes k} + E$, where $v \in \mathbb{R}^d$ is the unknown planted unit vector, $\lambda$ is the signal-to-noise ratio (SNR), and $E$ is a Gaussian noise tensor [cite: 11]. Tensor PCA represents a canonical "needle-in-a-haystack" model (referred to internally via target node T#73) that features a sharp statistical-to-computational gap.

### The Hopkins 2018 Baseline
Information theoretically, signal recovery in Tensor PCA is possible when $N \lambda^2 = \Omega(d)$. However, polynomial-time algorithms face a much steeper barrier. Hopkins' thesis (2018) and the concurrent work established the SoS computational threshold [cite: 12]. It was shown that degree-4 SoS could successfully recover the signal vector when the SNR scaled as $\lambda = \tilde{\Omega}(n^{-k/4})$ (or $N\lambda^2 \ge \tilde{\Omega}(d^{k/2})$ in alternative notation) [cite: 11, 13]. Below this threshold, pseudo-calibration techniques proved that the SoS hierarchy fails, cementing the belief that no efficient algorithm could bypass the $d^{k/4}$ bound [cite: 4]. 

### Tightened Bounds and New Algorithms (2020–2026)
Historically, it was conjectured that while SoS could achieve the $d^{k/2}$ sample complexity barrier, simpler methods like gradient descent or approximate message passing required an SNR scaling with $d^{k-1}$ unless paired with computationally expensive spectral initializations [cite: 11]. 

Between 2024 and 2026, the landscape shifted dramatically, challenging the supremacy of SoS frameworks. 

First, the Normalized Stochastic Gradient Ascent (NSGA) method with overparameterization completely bypassed the previous gradient method conjectures. Ding, Gu, Liu, and Fang (2025) proved that a randomly initialized, overparameterized stochastic gradient method natively achieves recovery at the $N\lambda^2 \ge \tilde{\Omega}(d^{\lceil k/2 \rceil})$ threshold [cite: 14, 15]. This establishes that overparameterization confers a significant initial optimization advantage, allowing continuous trajectory methods to match the optimal SoS threshold without relying on the heavy $O(d^{O(k)})$ machinery of SDP solvers [cite: 11, 16].

Second, Kikuchi hierarchy methods achieved smooth computational transitions. Zhangsong Li (2025) proposed an efficient algorithm for Tensor PCA based on counting weighted hypergraphs. By leveraging Kikuchi free energy from statistical physics, the approach improved upon poly-logarithmic factors inherent in the previous SoS algorithms and explicitly mapped a smooth trade-off between SNR and computational cost ($n^{C(\lambda)}$ time), confirming the continuous statistical-computational phase transitions theorized in prior literature [cite: 13, 17]. 


## 4. SoS for Tensor Recovery / Completion

Tensor completion seeks to impute the missing entries of a low-rank tensor from a sparse subset of observed coordinates. This maps closely to the feature restoration targets represented by execution graph variables like T#43 and T#73, where intermediate activation tensors in high-dimensional computational graphs are partially obscured or sparsely sampled.

### Connections to T#43 and T#73
In operational pipelines, multidimensional data structures (tensors T#43 and T#73) often suffer from structural incompleteness. Tensor completion via SoS provides the maximum theoretical resilience for recovering these tensors [cite: 18, 19]. While standard unfolding techniques flatten the tensor into a matrix and apply Nuclear Norm minimization, they systematically fail to capture the high-order correlations across modes, requiring suboptimal sample densities [cite: 20]. 

### SoS Relaxations for Tensor Completion
The limits of polynomial-time algorithms for exact tensor completion were initially charted by Barak and Moitra, and later improved by Potechin and Steurer (2017). They demonstrated that the sixth level of the SoS hierarchy could successfully recover an unknown 3-tensor with orthogonal components from roughly $r \cdot \tilde{O}(n^{3/2})$ randomly observed entries [cite: 21]. This level-6 relaxation successfully breaks the matrix-completion reduction barrier ($n^2$) by explicitly encoding the simultaneous orthogonality constraints across all three tensor modes into the Positivstellensatz variables [cite: 21, 22].

In the agnostic setting, where no strict rank assumptions are made, Foster and Risteski (2019) used the degree-six SoS relaxation of the tensor nuclear norm to yield optimal prediction error rates ($O(1/n)$ fast rates) under the square loss, bypassing the slow rates typically associated with non-convex landscape relaxations [cite: 23].

### Developments in 2025–2026
Recent work has bypassed the necessity of uniform random sampling. Cifuentes and Li (2025/2026) solved the exact and noisy rank-one tensor completion problem via SDP by identifying deterministic combinatorial conditions on the observation mask $\Omega$ [cite: 24]. Rather than requiring incoherence and uniform randomness, their SDP guarantees stable recovery using a "square-propagation" condition. Astoundingly, this condition can be satisfied with as few as $\sum_{i=1}^d n_i - d + 1$ structured observations [cite: 24, 25]. For a target tensor (e.g., recovering T#43 from a network layer), this indicates that provided the spatial dropouts follow specific connected topological masks, low-rank SDP relaxations will yield exact imputation without the probabilistic overhead demanded by earlier SoS theories [cite: 26, 27].


## 5. Computational Tools

The operational translation of the SoS hierarchy relies on specialized parsing software and robust semidefinite solvers. However, the immense variable explosion restricts practical tractability.

### SOSTOOLS, YALMIP, and Modern Frontends
The translation of polynomial non-negativity constraints into LMIs is traditionally handled by MATLAB toolboxes like SOSTOOLS and YALMIP, or the more recent SumOfSquares.jl package in Julia [cite: 28]. These tools automatically construct the moment matrices and dual localizing matrices, abstracting the algebraic geometry from the user. However, translating a high-level tensor constraint into its moment matrix formulation significantly inflates the problem representation [cite: 28]. 

### Mosek Scaling Limits
MOSEK is the primary commercial interior-point solver utilized for these SDPs [cite: 29, 30]. Despite its extreme efficiency for convex conic optimization, SoS formulations run into hard scaling limits. MOSEK solvers routinely output `MSK_RES_WRN_ZEROS_IN_SPARSE_ROW` warnings on SoS generated LMIs because the hierarchy enforces moment consistency by equating redundant variables [cite: 28]. These redundant equality constraints create ultra-sparse, degenerate rows in the block-diagonal SDP structure, causing numerical instability and blowing up the pre-processing time of the interior-point method [cite: 28]. 

Because the interior-point method scales roughly as $O(m N^3 + m^2 N^2 + m^3)$ where $N$ is the SDP block size and $m$ is the number of constraints, the SoS size $N \approx n^k$ becomes a terminal bottleneck [cite: 30].

### Tractability at Levels $k = 2, 4, 6, 8$
*   **$k = 2$ (Degree-4 SoS)**: Represents the base tractable bound for moderate-sized models ($n \approx 100-500$). Tensor PCA recovery algorithms utilizing degree-4 SoS are computationally viable and serve as the standard algorithmic benchmark [cite: 12, 31].
*   **$k = 4$ (Degree-8 SoS)**: Used theoretically to achieve minor statistical advantages in highly dense subgraph detection or specific adversarial perturbation models. Computationally, it is restricted to small toy instances ($n \le 50$) due to the $O(n^4)$ matrix size [cite: 12].
*   **$k = 6$ (Degree-12 SoS)**: Tractable only theoretically. Level-6 is famous for being the critical threshold required to break the matrix unfolding barrier in tensor completion ($n^{3/2} r$ observations) [cite: 22]. To run a level-6 SoS solver on physical hardware limits the tensor dimension to $n < 20$.
*   **$k = 8$ (Degree-16 SoS)**: Exclusively an object of theoretical proofs. Used in lower-bound pseudo-calibration constructions to prove asymptotic failures of generic high-degree algorithms.


## 6. Lower-Bound Techniques Against SoS

Proving that a statistical problem cannot be solved by any efficient algorithm is typically impossible without proving P $\neq$ NP. Therefore, unconditional lower bounds are established against restricted, yet powerful, classes of algorithms—most notably, the SoS hierarchy and Low-Degree Polynomial (LDP) tests [cite: 32].

### Pseudo-Distribution Methods
The primary mechanism for establishing SoS lower bounds is the pseudo-calibration framework developed by Barak, Hopkins, Kelner, Kothari, Moitra, and Potechin (2016) [cite: 4]. To prove that SoS cannot detect a planted signal (like a Tensor PCA spike) below the computational threshold, one must construct a valid pseudo-expectation operator $\tilde{\mathbb{E}}$ for the null model (pure noise) that mimics the planted model [cite: 4, 33]. 

The pseudo-calibration algorithm:
1. Obtains pseudo-expectation values for random inputs by "calibrating" them against the low-degree Fourier characters of the planted distribution [cite: 4].
2. Constructs the corresponding moment matrix $M$.
3. Demonstrates that $M \succeq 0$ (PSD) with high probability [cite: 4].
If $M$ is PSD, the SoS proof system cannot refute the null hypothesis, certifying the algorithm's failure [cite: 4, 33]. Recent refinements in 2024-2026 have abstracted these requirements into simple, problem-independent conditions on coefficient matrices that bypass the heavy custom analysis previously required for Tensor PCA and sparse PCA [cite: 33].

### Low-Degree Likelihood Ratio (LDLR)
A closely associated methodology is the Low-Degree Likelihood Ratio (LDLR). Rather than building massive PSD matrices, the LDLR calculates the norm of the likelihood ratio projected onto the space of low-degree polynomials. If the norm of the low-degree likelihood ratio is bounded $O(1)$ as $n \to \infty$, it formally implies that no low-degree polynomial can distinguish the planted model from noise [cite: 4, 12, 34]. Under the pseudo-calibration conjecture, failures of LDPs tightly correspond to the failure of the full SoS hierarchy [cite: 34].

### Connections to T#72 Type-2 Constant
Bounding the fluctuations of these high-dimensional polynomial projections requires sharp concentration inequalities. This is deeply tied to the "Type-2 Constant" of Banach spaces associated with tensor norms (identified here operationally as T#72). 

For a tensor space equipped with the $\ell_p$ injective norm, the type-2 constant, denoted $C_{r,p}(d)$, limits how large the variance of a random series of tensors can be [cite: 35, 36]. Formally, for $p \ge 2$, the expectation of the injective norm of a Rademacher or Gaussian series of $n$ tensors $T_i \in (\mathbb{R}^d)^{\otimes r}$ satisfies:
\[ \mathbb{E} \left\| \sum_{k=1}^n \epsilon_k T_k \right\|_{\mathcal{I}_p}^2 \le C_{r,p}(d)^2 \sum_{k=1}^n \|T_k\|_{\mathcal{I}_p}^2 \]
[cite: 37, 38]. 

In 2024–2025, Bandeira et al. established tight geometric upper bounds for the Type-2 constants of tensors without relying on noncommutative Khintchine inequalities [cite: 35, 38]. By defining these constants up to exact logarithmic factors, researchers can tightly bound the spectral norms of the pseudo-calibration moment matrices [cite: 35, 39]. Consequently, the T#72 type-2 constant serves as the fundamental geometric constraint that dictates the exact signal-to-noise ratio at which the moment matrix $M$ drops its positive semidefiniteness, mathematically crystallizing the exact SoS lower bound for Tensor PCA [cite: 36, 40].


## 7. Anti-Anchor Flags

The high velocity of machine learning and statistical physics research yields frequent bold claims regarding polynomial-time optimality. The literature review from 2024–2026 requires scrutinizing and clarifying several heavily propagated assumptions:

*   **Flag 1: "Gradient methods inherently require $\Omega(d^{k-1})$ samples for Tensor PCA, isolating SoS as the only $d^{k/2}$ solution."**
    *   *Correction*: This conjecture, prevalent through early 2024, was broken in late 2025 by Ding, Gu, Liu, and Fang. They proved that Normalized Stochastic Gradient Ascent (NSGA) utilizing a properly scaled overparameterized objective achieves near-optimal recovery at $\tilde{\Omega}(d^{\lceil k/2 \rceil})$ sample complexity. This breaks the $d^{k-1}$ barrier without relying on spectral initializations or tensor unfoldings [cite: 11, 14].
*   **Flag 2: "Randomly masking observation entries is a necessary condition for robust noisy tensor completion."**
    *   *Correction*: Disproven in late 2025 by Cifuentes and Li. Prior frameworks assumed that avoiding worst-case adversary placement required uniform random entry exposure. Cifuentes and Li established *deterministic combinatorial conditions* (the square-propagation mask). Under this explicit geometry, SDP relaxations recover the rank-1 tensor in polynomial time with as few as $\sum n_i - d + 1$ samples, bypassing the requirement for uniform randomness entirely [cite: 24, 25].
*   **Flag 3: "Sum-of-Squares dictates the absolute limit of what polynomial-time algorithms can achieve computationally."**
    *   *Correction*: While SoS defines the fundamental lower bound thresholds, it does not define algorithmic speed superiority. In 2025, Zhangsong Li demonstrated that for the Tensor PCA problem, counting a specific family of weighted hypergraphs (using the Kikuchi hierarchy) succeeds at the precise exact $\lambda \sim n^{-p/4}$ threshold of SoS. Crucially, it trims off the immense poly-logarithmic factors generated by SoS SDPs, running in tighter continuous $n^{C(\lambda)}$ time, officially shifting the frontier of operational Tensor PCA from generalized algebraic relaxations toward specialized statistical physics algorithms [cite: 17].

**Sources:**
1. [washington.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsKTDXBhMpCq6uyALD04n2KKZlDD1YZpyOGaZ1hrtzjATJuDcq4YRSBOTUAM7pp8go0YyDEY9cIdRiYTgz9NC25O-f0SJwKp9bjFwFtT8X9JG6WS6pEbvKBKJ67lfvh3oAXPwOI-WOTZLHH3C6GesESiE6LRBGS_dmckJmEgY=)
2. [aimsciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmylz7XGpH-Nu8rZXyws1Z7z-WUktW3VCeQ0m50__Zh5mVh-rTu5J7hALlsKg5-Ly-00vdnU0loIRAnAu5pYt2EMswENd6iC15GgDw4lkCn7d2FzSoohNJx_D9mTV_ANS1C_5wUVhh44hJmeH2T8-Wsw==)
3. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8nJZx38hRG_ptDP-mI3r49Z3LHqUg831junxrakKXdze4jzhGUQGVBS1T70AA_KMRS2ALUk50vaFc2SY9Zcrp9_LoZ16kme1_pJMGLthNPoRkjeTapPQUT_yNTUkE9a8Wk3zigkDhgh7vL6l46MFNphcIjAqhRE-_zcPv8q1EHSO2AScltxfz6nh6Os6FZKbE8zdw2ljOes0gvhK5-PVeM_-lLNU=)
4. [iliasdiakonikolas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa1O7GZOjIu9R7aegrJoVLO8HHVhdRDUYv9Bj4bD5YF79qAs9mrWitZI-D6nhQlqJflLS4Zt7aYLEB-W41F8aH471H1N-CwITFWinTLzM8ZV3MB4ybVfRuLUSNWJXv1I8I0a5jlwlK9YlqACYHH9M-)
5. [dsteurer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7_PCYy4WxXOkEOUbme4XE5OfSuAswGOhuOi1BQDYaF3ahFsi6pa6NRSKXKMuEozRwNt3rAjGAAJOvYe-Qg63DY-u8dsZx4C-UQX7ZfDTA6Nb-lVmdcdeF1p2ONcQ=)
6. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVBjHLF31sQ6dRfgvyLjN8eab-KfkROfKZ5rak2fIGMxZCo0jsodaMRtiFOsoX4eCCRaCCFfx_bzGDR6bG5fcGOIUvYnHmoCzqY1GaqnqAvh1tpnobE_dfLtUtukYEAuLNXltEzxuCKdgi_s3l6nIRv3drWbUqeKU986FS9Q==)
7. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUTrCgGuKEVMiXMEfLXuvrMSfjyOV1WxFfR8d1-dnfQlpfkJeWbUZ8G7aVHr3H23iG3mf0nGwuOBcZWxttwcpkHF4fQ8_0N0KWSirFLKDzRUhGedDL4PAgKxdTpMDN6ZJlz-DsCY5b8Es8veN5VAef)
8. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHD_6I-B1BG5Ng_imPMjlFWZxQyaieJCVQ_5v2PCIvfxMgLf6TKbuOuVgY0VLk5too3mifW2jH8LbT5453WtxKT9AIvnAEO_kLHCRU__4ECwP_30jPNdefexSTYj6ND9sDoxp3iZVG_C-8kjXgFbgyD_spPolrdU61N_wk=)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJyv6ukbZDvBG5-_f6VmulIFCMKlLOUmjrOPwv4x1XdLVDlQH6ObXS1RBfZ99jT2gWcZfDTqtbSypuyGILjVzQDa7MIWP6TuN5lgQnkxNlXWnTK5lQehuF)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAn_TvuFmzeK4qC3riD5YLmurcI72mX-hiidJTUOizlGvmZJfuBQgq2WeqNKRcbUx8XxShoAhbBAMuqk_SM05zfMQyHJnQ6CUOtNUbMNCfr84ebxtzm5PDuNoM124_pBRb3wfhDSOjZJArYqfh7EJ6W2j-QwRxnCndOP5tI0QFeKNKjiVVTwDcNBaSY_n9Zz8PT86l6gkGWCaonE8DTIH34ImEeh3K9HaY4Bk=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKVEhKP7AOZXF7gXo9sj6dWMMqPW9Frt7l1boK-9uUicWrVGRpEhOoZNIZQEadqFJjxnTv0sDlhQAPmuvizGM3C6ZfJHCt970Z2iX-gSXFcbkM_Fa_)
12. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqH80kUL0XDJ1_szSqJGRg5gw1n-dd9-DAwn--PS06Loua6XKwysbm1n-HPb_uIBZRUsQKmGTdpxkh9RxR75-PZljOKHiink11FcO8NBzxDCC4HpW-2DJUmx6fKbMx7Jbr7Y1pZI6tP6RUAMExVI6hKfkoj9hBPIuLL8dJGGpHagcyS92FvQB-QH82Lr_aBCnfu4SVjQ==)
13. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGD98tnFUU0trj9F6y72pgS9K_o7AD-R9xGr_UzLuh6QT-BIHVmYwHwjgSaA4wGVkR8JrEmHzr6o02YfdvRC8ZYBZYFVw2_4TWmZfCuGGONzoOKV6GUehYlf4uAgiATZkxm5ZiWHXLwBcrU1Rl1yW7dFfxI)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE-uswsnu9PEkfAY5gfs_24CNZ6lu3iTP_bGOk9w-xQSUYvWslyqyNUg_43KRaz94rswllK953AykCM47Bh6O4WBkN9_pEgEvE9OEv72y_TWXKjmWc)
15. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvoxrnjb5VSdRaPCyYf6bimUfW2YBp785-k6Dz2OcGKotN4aMGlNsoCfm-xpouTDYvG82F40rBf0eQRonyF2ON89aLhak1J5sZIC9eTBuBUDNBi7ux-OFEvAlu1nR8SiwxpcGN85cNc1v_5IPFFnRch08NVt_Xr2CtMfjB8wHZz3FcvuQWSfSB7bFkegpeYULCT8Gud7zgjuwkcXx08h6RajA97w1qvapySZKFnA6jShCYYAJWn-M=)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERIw50wPW7HbngHdnsNGr5jiLfq5mpY1HbIuJNvvD4atcIRhP0pIBBsBxd2IsHeUigOvn-36YavBk-jvm4L1TwduZYsoKGmWhx8Ag4zFQBDR6U-enMwqKQjMGvS49VtQrwjiNgKR79Ob3KK9InKYMd1t83G1-GMfusynv7psrB)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE54Da0yp2F4JvI0l-T2zfSwi571FXBM8bZ3eiBiXogDSRH2FQhXJ_3WlBdZHfwy32GakAACQA_6B73PC_rP7LvsRCAFlC9a6h0GZZopg_i0ZXURfu5)
18. [tensorflow.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5Ne2GTfxhr5yw1W2oO0NLD_bAzcjg4S6QHEAjai3Bd0xpAf6gJzr-QUhBKO6MVREVUxp--SwavFgDR42MWk-Bh50OBNRndXQfzV-l5DgSnalL0LsJM66fhGoTNac99L8JQn8DGIsR9wuDbsbqFjuTMr4=)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvOmjFCNxPVOcD2Qq--PF0_jeEfNtl3TnkdlHO4beeAC-j-Orep9HQRgLR6k3SsL1gttSWi1YXqd3pedlMjZMClsgUm_hRSuFYMZhHf1zbOv90MMmTdiRg9ZD6iK8SV6yyq8xoxmF5KYIx)
20. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFr5ht4OAS_NJf4EcvSEYMResWP6BjrJAR02KHwWfEKQiUHoqS3AV0gMJxOngghcc7fYw3U5mTtFUPzfjRfT_KldRhm32SOoGDmtpfExNNvi6t31P5zyy5piVR5yIzMQaes7ACjL_XBMUgwk_WLBYhTqwU=)
21. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe8doX0dGtOAzt8hIG3JXsZnAbqjeFXZw9XfUHCFXvBeNH6MTXSVoWZoM5Qd1LT2ikqHza3TTfvmCRpkYTEYlzipdhYO6PDHsuxmj2uXhS_QENnRXvtcyIBMS6ETsfH22tL1eGMTBg)
22. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWzrjQw7ZRFSwByy1BMueSHclx3xtueg7x-w47kPFS4XVYxN5OKLLCLHSuG3xbKoEIv7fgerSLgxNpG3mw6b1FCMnM1dsbOHwZxn0hokfRtJaj7gSElVi6z3EHaohet0NjAEj3enc=)
23. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnUfZg8ks1d1CCoePzILmGDMNIagYeivvun2upppe-2Pe1BEnVba8MOSePLqa1mHCXqsW7_FZcdkextoNJ93gHUocQYbOsj2kAeG4JNy6t7qhjnuGrzO5xm_zfRJJmlOqYmRSxew==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5_RXtQ8VMbaM0dZRZ9FxmhHpSB-sgF5YtjRF3iJ4FTUHKAYzOAjIlemEv7Pj0w_tzhy59JKDKPzm3oZsbDkejevB6Ekku5YCzhJDJYycWPwd0X-lL)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmB-mlKoORQnST1CmgyNEWSTMmTQnnLm7RBztnY8TB2cwdFexUfdmD0EY4gjo_ucvxt5wersGpz022i8d0sxP7hmV0BHCGbS1W_TllHzR2ZYUC1qan)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeuTYYNB11dXnvlt9DQET2UbXszxD1qRF7DloqqtdWKFHmhhW7udpoKeJPW_aVrntqQw59E9x6kWj2MvN5Cq0ILM6pE-x0ARl_C1SB5fjlNuR8R2ssYDs0)
27. [gerad.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPRUBzbb-3Gm91DyGS2m5bZTmuQkLArTsf9thOxH2n9uJGPctSZowgOUDD0c4M134So4njp8wVh8OOjV-nQnpNCvJe4mOmuExnYFti4LJWCHRORMSCx7atpyLR1isw)
28. [julialang.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIdSX1EiwqZzW5KFLEZ9zOe7pn7t7qWUcqRJErg9N4ZL3OtdvWhZGy4dENGopJvb1WAiT7RrYUgcaZQrHZ4I6H7GrXffJM5o6OG_qC9g5XlnT-zIhpEqnAL-iCvctbihZ9UQtek90Y7-MGsMUp9RP8rrRI9tKZyvlRGfpMuyvP9WQYr2B5cgvtxj6uvyoQyrnOlXs=)
29. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrI0c_451GmDz-nWiSERdtY3w_B9InoUmVNDGuIRL4scJf_vrLXMgQNd6OEB-AiwrX7mSsO8RY-spTPsrvRQvSqFYkxhoc7sOzZIexO3L9-lcRQVRfQtP7NEJ8crf1ue1Q9a3NM0ew139p1zZ5fHW_vcMUmEJ2rOjPBWK2FnIbE92JC97WwgW6NvSRY5AkoL9CYuofaxwDbdCVq1vh0cSdnxE=)
30. [mosek.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWRoLS0ktzgoOeaPY7e3HC0GahAM67DV2RdxLHtdRHfZ91YvpWDMIQuOtSgLd0Ov4y6z0enJPmKpwxzz1Y_1fMBdZDapIeVgdZpXxDmyLkF0xXslAu4xUPKkvc2GwRXdr_4hUp-04SBA==)
31. [uwaterloo.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPB4-hvDDQeDqAkV8g1ha1-qPXB21JFg_LLj03NPdqzn7XdBFGwhv3TNGyVRmG3m6pTwmIZbAZXe6cX6WcSPQwfhvMxCqOtwnpnar3fz41hO3Y7cIJK-N-MR4_qhNa2_xLRQLReBEkvBBRUBvnnAbH4aZLTuA93XfYy7cPNaH62rKFl9sCYYd-G_0=)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYu_cjOJm0HrQJfsyLrMDwhUa21TrQaVKoREhaZkbiOrpJpIJIMxWj7FcqmyD4pd-5eT_0hzwrCmKYkXdxbnQz-j6Ni5OxC2ER3kUHV47JRLEPm8Sm_wY1)
33. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUhM_yL1x9VBDGIG8-XWd8nRtlW6k8ZkkeN7h_-dOqN9Nr0SI27sPTcdFYJ_1xXSHtIV10GvJRkE2InyO0YH8Ta5bQadryCe25mXf7tCl83veXnjuGDEjIhmmderRUCR4=)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-OMByECaSp-EszdXbLEVxlz_DRWHUFN7spknSusuFFjFqepPh_0_i4pCIGwGcFmo4ZtV9Nj909VClE54okZgYYtABK3w31Q429lizZSz5wC8Ij4l9AeIn)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUeLQq60-X9mIDQxZLpeVGP3jpxAQ0-96-Pu5jFnZv_ql_qcn05JPY85iY6s5VQY_Rmx4CjgE3tmSr_jkhE_7vf1AjXTPyVfvCVckeho6F8bZuynvX)
36. [ntua.gr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENyi-nK9ocPfDHk9YcDWJAEyROXNubp7LI4IP4KVcF9fNRqnFS8cpj8OTIzJbvQiU_vNyCLZaBhkX4k_F_QuKrBN0PxnrujqmJA8DkGEgZdw9QldBgHzT5uNooJuf8WyexTNZOp4f4WD9UYBo=)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETniu2qIxC1td9Wak5KKc1ljVEjgMBZSMKP2JHPqL2rnAbjCZb_T-Hq9-SMwxDjkjEl-Drt7-QFkR0O1ZnWBD-IXSqqGyE9vtUQfDuPXFwuLittu7epFMn)
38. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY0GsWLUi4Oy7A2TnM8-NOv68BpOOngXAUWxqGlUATJEWhUB4Sb7Qi-06eY5UvZYBteH2MqzMk5tKoPNKzuoWWkyQ-vzmmPtHKTVYZXCzBQoQpOYNO2_vp7G8WLzCWXKvnBjfDLKvnHEN-T37HXFf8khzpfHK11BCZ0hQ6nNdrD1zPFWqGda_yR1NXNK4KuH22VS0XRu5Afcv-OURV80Ic4pRxrg==)
39. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz-GHL18x20wxmDubCfw3rwzE2jmk-Y157kMvHbY041maG0EMCxa0BISKIHiQs3IB2c8FkR2k7WecyrhjQzFSTZ6VtdZmsEsHzB0Afc1sUr9zBFR6z9gssBDRcxoGO1AsyFdVZVD4KV6m0e-AnP8Dd4XW4uIPZ)
40. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRH0Tv9do9b374Aihnn7X_XkJtU_iQoozhH7ODGwGi4U4LtcSZg2d7hLLuh0gD0jVp6jiGqwLm0DOtXBgaBPN6e3zJ6F548vNlle0ipeXlZ3d95iJo_feFdDUqIv-SU8ZPkoF-7Yt7cZ3D3S1Y9AOJ2BVOmlWlCCNsdcn5WKxW8HFChQpYj38Gvo_u3nBWilvGAL-GMJDFMvb0NjOyaXkAwN2F_yCllLYLiGRS)


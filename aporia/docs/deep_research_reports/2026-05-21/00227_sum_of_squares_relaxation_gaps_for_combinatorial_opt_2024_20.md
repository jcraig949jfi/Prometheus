# Sum-of-squares-relaxation gaps for combinatorial opt 2024-2026 (Barak-Steurer)

**Pythia queue id:** 227
**Tier:** 2
**Priority:** 5
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdQRklQYXFyaEZlREwtc0FQcjVHd2dBbxIXUEZJUGFxcmhGZURMLXNBUHI1R3dnQW8
**Elapsed:** 442s
**Completed at:** 2026-05-21T18:50:32.088848+00:00

---

# Sum-of-Squares Relaxation Gaps for Combinatorial Optimization (2024–2026): Advancements on the Barak-Steurer Paradigm

The Sum-of-Squares (SoS) hierarchy is a powerful algorithmic framework that generalizes linear and spectral methods by reformulating combinatorial optimization problems as sequences of increasingly tight semidefinite programs (SDPs). Initially popularized in theoretical computer science through the foundational work of Boaz Barak and David Steurer, the paradigm posits that SoS might serve as a universal algorithm capable of resolving the Unique Games Conjecture and optimally approximating a vast array of NP-hard problems. However, understanding the exact boundaries of this framework requires rigorously analyzing its failures—known as **integrality gaps** or **relaxation gaps**. Between 2024 and 2026, research into these gaps has rapidly accelerated, pivoting from basic random constraint satisfaction problems (CSPs) to highly complex, multi-plant statistical inference models, explicit high-dimensional expanders, and interconnected domains such as streaming algorithms and coding theory. 

### Key Points
*   **The Barak-Steurer Hypothesis:** Research continues to heavily rely on the framework proposed by Barak and Steurer (2014), which formally linked SoS capabilities to the Unique Games Conjecture, suggesting a single meta-algorithm might achieve optimal worst-case and average-case guarantees [cite: 1, 2].
*   **Multi-Plant Inference Gaps (2026):** Recent breakthrough results demonstrate that the SoS hierarchy fails to refute the existence of multiple disjoint planted cliques in random graphs when the total planted size $kt \le n^{1/2 - c\sqrt{d/\log n}}$, extending the classic single-plant $\sqrt{n}$ barrier to highly structured multi-plant regimes [cite: 3].
*   **Streaming Lower Bounds from Convex Gaps (2026):** Evidence leans toward a direct equivalence between convex relaxation gaps and algorithmic memory constraints. Works in 2026 show that basic LP and SoS integrality gaps imply tight single-pass and multi-pass streaming space lower bounds for CSPs [cite: 4, 5].
*   **Explicit Gap Constructions via High-Dimensional Expanders:** While early SoS lower bounds relied on random instances (e.g., random 3-XOR), researchers have successfully utilized small-set high-dimensional expanders to construct explicit, deterministic instances that fool $\Omega(n)$ levels of the SoS hierarchy [cite: 6, 7].
*   **Advancements in Coding Theory (2024):** Techniques natively developed for analyzing SoS lower bounds—such as pseudo-calibration and Kikuchi matrices—have successfully resolved long-standing conjectures regarding the dimensional limits of 3-query locally correctable codes (3-LCCs) [cite: 8, 9].
*   **Exactness over Roots of Unity (2026):** For quadratic optimization over roots of unity, the SoS hierarchy has recently been proven to converge exactly at level $\lfloor n/2 \rfloor + 1$, improving previous bounds and highlighting regimes where SoS provably collapses the relaxation gap entirely [cite: 10].

---

## 1. Introduction: The Sum-of-Squares Paradigm and the Barak-Steurer Vision

Combinatorial optimization generally involves finding an optimal object from a finite set of objects. Since many such problems (e.g., Max-Cut, Independent Set, Maximum Satisfiability) are NP-hard, computer scientists have long relied on convex relaxations to find approximate solutions [cite: 11, 12]. The most sophisticated of these frameworks is the **Sum-of-Squares (SoS) hierarchy** (also known as the Lasserre/Parrilo hierarchy), which provides a principled sequence of semidefinite programming (SDP) relaxations for polynomial optimization problems [cite: 13, 14]. 

### 1.1 The Mathematical Formulation of SoS
The SoS method translates polynomial non-negativity over semialgebraic sets into an SDP [cite: 14]. For a system of $m$ polynomial equations $f_j(x) = 0$ on $n$ variables over the Boolean hypercube $x \in \{0,1\}^n$ (or equivalently $x \in \{-1,1\}^n$), the degree-$d$ SoS relaxation searches for a **pseudo-expectation** operator $\tilde{\mathbb{E}}$. A pseudo-expectation of degree $d$ is a linear operator mapping polynomials of degree at most $d$ to real numbers, mimicking a true probability distribution over the feasible solutions [cite: 15, 16]. 

A valid degree-$d$ pseudo-expectation operator must satisfy:
1.  **Normalization:** $\tilde{\mathbb{E}}[cite: 1] = 1$.
2.  **Positivity:** $\tilde{\mathbb{E}}[p^2] \ge 0$ for all polynomials $p$ of degree at most $d/2$ [cite: 15].
3.  **Constraint Satisfaction:** $\tilde{\mathbb{E}}[q \cdot f_j] = 0$ for all polynomials $q$ such that $\deg(q \cdot f_j) \le d$.

If an actual distribution over valid integer solutions exists, it naturally yields a pseudo-expectation. Therefore, if the SDP solver cannot find a valid pseudo-expectation operator, it constitutes a rigorous proof (an SoS refutation) that no solution exists [cite: 1, 17]. The fundamental algorithmic question is: *At what degree $d$ does the SoS pseudo-expectation perfectly distinguish between satisfiable and highly unsatisfiable instances?* Since solving a degree-$d$ SoS relaxation requires $n^{O(d)}$ time, any problem requiring $d = \omega(1)$ to close the integrality gap is generally considered hard for polynomial-time SoS algorithms [cite: 13].

### 1.2 The Barak-Steurer Hypothesis
In 2014, Boaz Barak and David Steurer articulated a bold vision for the SoS framework, proposing that a single algorithm—the SoS hierarchy—might achieve the optimal approximation guarantees for a massive class of combinatorial optimization problems [cite: 1, 2]. Their work highlighted a deep, unexpected connection between SoS gaps and the **Unique Games Conjecture (UGC)** [cite: 1, 18]. If the UGC is true, then local, tailored algorithms cannot beat certain approximation thresholds. Barak and Steurer hypothesized that studying the bit-complexity and running time of the SoS method could fundamentally determine whether the UGC holds, or conversely, whether SoS can refute the UGC in quasi-polynomial time by successfully solving Unique Games on certified small-set expanders [cite: 18].

An **integrality gap** (or relaxation gap) in this context is an instance where the pseudo-expectation operator "pretends" a high-value solution exists, while the actual integral combinatorial optimum is much lower [cite: 12]. Proving an SoS lower bound requires explicitly constructing a pseudo-expectation operator $\tilde{\mathbb{E}}$ that satisfies the SDP constraints but corresponds to a "fake" solution [cite: 19, 20].

---

## 2. The Frontier of SoS Gaps (2024–2026): Multi-Plant Structures

While early research mapped the SoS integrality gaps for standard random graphs (e.g., single Planted Clique [cite: 20, 21], random 3-SAT [cite: 16]), literature from 2024 to 2026 has increasingly targeted highly complex, clustered, and structured distributions. The most prominent example is the study of **multi-plant average-case inference**.

### 2.1 The Mosievskiy-Reyzin Integrality Gap (April 2026)
In a major advancement, Matvey Mosievskiy and Lev Reyzin (2026) established strict SoS integrality gaps for the detection and refutation of *multiple* planted structures below the $\sqrt{n}$ barrier [cite: 3]. In their model, instead of a single clique of size $k$ planted in an Erdős-Rényi random graph $G(n, 1/2)$, the algorithm is tasked with finding $t$ mutually disjoint cliques, each of size $k$. The total planted size is defined as $K := kt$ [cite: 22].

A long-standing question in the SoS literature has been whether distributing a large planted structure across multiple smaller, disjoint structures could allow algorithms to bypass the fundamental $\sqrt{n}$ spectral barrier [cite: 22]. Mosievskiy and Reyzin proved that it cannot.

**Theorem (Mosievskiy-Reyzin 2026):** For $G \sim G(n, 1/2)$, there exists a valid degree-$d$ SoS pseudo-expectation for the relaxation maximizing the total size of up to $t$ disjoint cliques. As long as the total planted size satisfies:
\[ kt \le n^{1/2 - c\sqrt{d/\log n}} \]
for a universal constant $c > 0$, the degree-$d$ SoS relaxation achieves an objective value of $kt(1 - o(1))$ [cite: 3, 22]. 

### 2.2 Implications of the Multi-Clique Gap
This result demonstrates a strict integrality gap [cite: 3]. Under the null hypothesis (a purely random graph $G(n, 1/2)$), the largest clique has a size of roughly $2 \log_2 n$ with high probability. Thus, when $k \gg \log n$, the true combinatorial optimum (the maximum total size of $t$ disjoint cliques) is strictly and vastly smaller than $kt$ [cite: 22]. However, the Mosievskiy-Reyzin pseudo-expectation matrix achieves a value of $\approx kt$. Consequently, degree-$d$ SoS *cannot certify an upper bound below $kt$* and completely fails to refute the existence of $t$ disjoint $k$-cliques throughout this regime [cite: 3, 22].

### 2.3 Methodological Innovation: Pseudo-Calibration with Disjointness
To prove this gap, Mosievskiy and Reyzin extended the **pseudo-calibration** framework originally pioneered by Barak, Hopkins, Kothari, Potechin, and Schramm [cite: 19, 22]. Pseudo-calibration dictates that the pseudo-expectation of a polynomial evaluated on the random graph should be exactly its true expected value under the planted distribution [cite: 23, 24].

The primary technical hurdle in the multi-plant regime of 2026 was maintaining a low-degree calibrated pseudo-expectation while strictly enforcing hard disjointness constraints across the $t$ different labels (so that no vertex belongs to two cliques simultaneously) [cite: 22]. The authors achieved this by utilizing double-indexed variables $x_{i,j}$ indicating the membership of vertex $i$ in planted clique $j$, designing a truncated Fourier expansion operator that forces cross-label non-edges to zero while ensuring the resulting moment matrix $M$ retains positive semidefiniteness (PSD) [cite: 3, 22].

### 2.4 Corroboration via Statistical Query (SQ) Lower Bounds
In modern average-case complexity, researchers often compare SoS bounds with other restricted models of computation. Mosievskiy and Reyzin provided complementary evidence by proving a lower bound in the **Statistical Query (SQ)** framework [cite: 3, 25]. They analyzed the problem of detecting $t$ disjoint planted $k \times k$ bicliques in a bipartite graph. They proved that when $kt = O(n^{1/2 - \delta})$ for any $\delta > 0$, no polynomial-time SQ algorithm can distinguish the planted distribution from the null distribution with any constant advantage [cite: 22, 25]. This convergence of SoS lower bounds and SQ lower bounds establishes $kt \approx \sqrt{n}$ as a robust, model-independent computational threshold for multi-plant combinatorial optimization [cite: 22].

| Computational Model | Problem Setting | Hardness Threshold | Publication Year |
| :--- | :--- | :--- | :--- |
| **Sum-of-Squares (SoS)** | Single Planted Clique | $k \ll \sqrt{n}$ | 2016 (Barak et al.) [cite: 19] |
| **Sum-of-Squares (SoS)** | $t$ Disjoint Cliques | $kt \le n^{1/2 - c\sqrt{d/\log n}}$ | 2026 (Mosievskiy & Reyzin) [cite: 3, 22] |
| **Statistical Query (SQ)** | $t$ Disjoint Bicliques | $kt = O(n^{1/2 - \delta})$ | 2026 (Mosievskiy & Reyzin) [cite: 22] |

---

## 3. Streaming CSPs and the Unification of Convex Gaps (2025–2026)

Another major theme emerging in 2025–2026 is the profound connection between convex relaxation gaps (specifically basic LP and SoS gaps) and the memory limitations of streaming algorithms. A streaming constraint satisfaction problem (streaming CSP) requires a $p$-pass algorithm to receive the constraints of an instance sequentially, making passes over the input in a fixed order while using limited working memory, with the objective of approximating the maximum fraction of satisfiable constraints [cite: 26, 27].

### 3.1 The Fei-Minzer-Wang Dichotomy (2026)
In a landmark 2026 paper presented at STOC, Yumou Fei, Dor Minzer, and Shuo Wang established near-optimal space lower bounds for streaming CSPs by directly exploiting integrality gaps from convex relaxations [cite: 4, 26]. 

They demonstrated that for any CSP predicate family $\mathcal{F}$, the basic linear program defines a critical threshold $\alpha_{\mathrm{LP}} \in [cite: 1]$ [cite: 26, 27]. 
1.  **Algorithmic Feasibility:** For any $\varepsilon > 0$, an $(\alpha_{\mathrm{LP}} - \varepsilon)$-approximation can be achieved using a constant number of passes and polylogarithmic space [cite: 26].
2.  **Space Lower Bound from Gaps:** Conversely, achieving an $(\alpha_{\mathrm{LP}} + \varepsilon)$-approximation requires $\Omega(\sqrt{n}/p)$ space (single-pass or multi-pass) [cite: 26]. 

This bound was established by reducing from a "distributional implicit hidden partition" problem [cite: 4, 5]. The core philosophical finding here is that **if a problem possesses a $(\gamma, \beta)$-integrality gap instance for a basic convex relaxation, no low-memory streaming algorithm can bridge that gap** [cite: 5, 28]. 

### 3.2 SoS Lower Bounds and Sublinear Space
Fei, Minzer, and Wang (2026) extended these concepts to the Sum-of-Squares hierarchy. They noted that sublinear-space streaming algorithms can effectively simulate basic convex relaxations on bounded-degree instances [cite: 5]. Consequently, $\alpha_{\mathrm{LP}}$ (and higher-order SDP variants) is not just the limit of multi-pass polylogarithmic-space algorithms; it inherently bounds single-pass sublinear-space algorithms [cite: 5, 26].

When a strong SoS integrality gap exists—for example, if the degree-$d$ SoS algorithm (where $d = \Theta(n/\Delta^{2/(t-1)} \log \Delta)$) requires $\Omega(n^{(t+1)/2})$ constraints to refute random instances of a specific CSP—streaming algorithms face a corresponding impossibility wall. The techniques used in 2026 to bridge these fields are heavily Fourier analytic, building on the Fourier-$\ell_1$-based lower bound methods and the pseudo-calibration roots developed for standard SoS lower bounds [cite: 26, 27]. 

---

## 4. De-randomization: Explicit SoS Gaps via High-Dimensional Expanders

Historically, demonstrating that the SoS hierarchy fails required utilizing random graphs (e.g., Grigoriev's 2001 lower bounds on random 3-XOR or random $k$-SAT) [cite: 6, 29]. The intuition is that local algorithms, like a bounded-degree SoS relaxation, cannot detect global topological obstructions in locally tree-like random graphs [cite: 7, 29]. However, establishing *explicit, deterministic* instances that are provably hard for SoS remained an open problem for nearly two decades [cite: 6, 29].

### 4.1 The Hopkins-Lin Construction (2022–2024)
Addressing this challenge, Max Hopkins and Ting-Chun Lin constructed an explicit family of 3-XOR instances that are hard for $\Omega(n)$ levels of the SoS hierarchy [cite: 6, 7]. Expanding on a framework introduced by Dinur, Filmus, Harsha, and Tulsiani (2021) [cite: 7, 30], Hopkins and Lin proved that SoS lower bounds can be systematically generated using **small-set high-dimensional expanders (SS-HDX)** [cite: 6].

### 4.2 Mechanism of Explicit Hardness
In the Hopkins-Lin framework, an explicit instance is generated by taking a bounded-degree SS-HDX complex and mapping its faces to variables and constraints of a CSP [cite: 7, 31]. 
The topological property of the HDX ensures two things:
1.  **Global Unsatisfiability:** By choosing a function $\beta$ that is a co-cycle but not a co-boundary in the complex's cohomology, they enforce a global structure on the XOR instance that makes it highly unsatisfiable (the true combinatorial optimum is bounded strictly away from 1) [cite: 6, 7].
2.  **Local Consistency (The SoS Gap):** Because the complex is a highly expanding small-set HDX, any localized view of the complex (which is all that $\Omega(n)$-degree SoS can process) appears trivially consistent (the homology looks trivial locally) [cite: 6]. 

Thus, the degree-$\Omega(n)$ pseudo-expectation assigns a value of 1 (pretending the instance is perfectly satisfiable), while the true optimum is $1 - \mu$. This yields an optimal $\Omega(n)$-round SoS integrality gap using a deterministic construction, fundamentally proving that algorithmic tailoring is defeated not just by randomness, but by the explicit pseudorandom geometry of high-dimensional expanders [cite: 6, 7, 31]. 

---

## 5. Advancements in Code Lower Bounds via SoS Techniques (2024)

As the Barak-Steurer framework matured, the mathematical tools developed to prove SoS gaps—specifically Kikuchi matrices and generalized pseudo-calibration—began spilling over into other areas of theoretical computer science. In 2024, Pravesh K. Kothari and Peter Manohar applied these tools to resolve fundamental questions in coding theory regarding Locally Correctable Codes (LCCs) [cite: 8, 9, 32].

### 5.1 The 3-LCC Problem
A $q$-query locally correctable code ($q$-LCC) allows any bit of a corrupted codeword to be recovered by randomly querying only $q$ bits of the received word [cite: 33, 34]. Understanding the minimum block length $n$ required for a $k$-dimensional message is a major open problem. For 3-LCCs, the best known constructions (e.g., Reed-Muller codes) require $n \le 2^{O(\sqrt{k})}$, while prior lower bounds were much weaker [cite: 8, 9].

### 5.2 Exponential Lower Bounds for 3-LCCs
In a breakthrough presented at STOC/FOCS 2024, Kothari and Manohar utilized techniques native to SoS lower bounds to establish exponential lower bounds for smooth 3-LCCs [cite: 8, 9, 35].

**Key Results (Kothari & Manohar 2024):**
1.  **Linear Design 3-LCCs:** If $C$ is a linear design 3-LCC, then $n \ge 2^{(1 - o(1))\sqrt{k}}$. This matches the upper bound up to a factor of $\sqrt{8}$ in the exponent, essentially resolving the Hamada conjecture on the maximum $\mathbb{F}_2$-codimension of a 4-design [cite: 8, 9].
2.  **Non-Linear Smooth Adaptive 3-LCCs:** If $C$ is a smooth, non-linear, adaptive 3-LCC with perfect completeness, then $n \ge 2^{\Omega(k^{1/5})}$. With completeness $1-\varepsilon$, $n \ge \tilde{\Omega}(k^{1/2\varepsilon})$ [cite: 8, 9].

### 5.3 SoS Tooling: Kikuchi Matrices and Chain XOR
To prove these bounds, Kothari and Manohar deployed a fine-grained analysis of the **Kikuchi matrix method** [cite: 8, 9]. Kikuchi matrices were originally popularized in statistical physics and adapted by the SoS community to track high-order correlations in pseudo-distributions [cite: 8, 23]. For the non-linear codes, the authors designed a "from-scratch" reduction to a system of *chain XOR equations*—polynomial equations structured identically to the long-chain derivations used to construct SoS lower bounds against linear 3-LCCs [cite: 8, 9]. This confirms Barak and Steurer's early intuition that the algebraic structure of SoS dual certificates captures deep, universal combinatorial limits [cite: 1, 23].

---

## 6. Exactness and Optimization on Roots of Unity (2025–2026)

While integrality gaps showcase the *limitations* of the SoS hierarchy, recent work also tightly characterizes the exact thresholds at which SoS *succeeds*, effectively closing the gap. In 2025 and 2026, research increasingly investigated polynomial optimization over the Boolean hypercube and its complex generalization, the roots of unity [cite: 10, 11].

### 6.1 Convergence over Roots of Unity (Al-Sulami et al., 2026)
A 2026 paper by Ahmad Al-Sulami et al. studied the convergence of the SoS hierarchy for quadratic optimization over roots-of-unity [cite: 10]. This class of problems generalizes the NP-hard Quadratic Unconstrained Binary Optimization (QUBO) problem, modeling applications from MIMO detection in signal processing to ground state computations in statistical physics [cite: 10].

For a system of variables $z \in \mathbb{C}^n$ constrained to the $m$-th roots of unity, prior results (e.g., by Fawzi, Saunderson, and Parrilo) established that in the binary case ($m=2$), the SoS hierarchy converges exactly to the optimal solution at level $\lceil n/2 \rceil$ [cite: 10]. 

Al-Sulami et al. (2026) generalized this finding to any $m \ge 2$. They proved that the hierarchy is guaranteed to converge, leaving a relaxation gap of exactly zero, after at most $\lfloor n/2 \rfloor + 1$ levels [cite: 10].
*   **Theorem (Al-Sulami et al., 2026):** Let $Q$ be an $n \times n$ Hermitian matrix defining the function $f(z) = z^* Q z$. If $f(z) \ge 0$ for all $z$ in the roots of unity, then $f$ admits an SoS certificate of the form $\sum |g_j(z)|^2$ where the maximum degree is bounded by $\lfloor n/2 \rfloor + 1$. Thus, the level-$(\lfloor n/2 \rfloor + 1)$ SoS hierarchy is globally exact [cite: 10].

### 6.2 The MK Problem over the Boolean Hypercube (2025)
Simultaneously, a 2025 study by Wirth et al. published in the *Mathematics of Operations Research* investigated constrained polynomial optimization over the Boolean hypercube, focusing on the MK (Minkowski/Knapsack-type) problem [cite: 11]. They established nearly tight bounds on the SoS rank required to solve these problems exactly. 

While SoS provides the best available approximation algorithms for Max-Cut, the authors noted its well-known weakness with certain integrality constraints. For the MK problem with parameter $P$, they proved that the exact SoS rank lies between $\Omega(n / \log P)$ and $O(n / \log P)$ [cite: 11]. This precise characterization underscores a dual narrative in the 2024–2026 literature: while average-case gaps (like planted clique) require pseudo-calibration to map heuristic failures, worst-case algebraic exactness bounds are increasingly pinned down to precise linear or fractional ranks using advanced approximation theory [cite: 10, 11].

---

## 7. Broader Applications: Graphons, Imperfect-Recall Games, and MAX-SAT

The ripple effects of the Barak-Steurer SoS paradigm continue to reshape diverse subfields of combinatorial optimization.

### 7.1 Differential Privacy and Block Graphons (2024)
A 2024 paper explicitly co-authored by Boaz Barak and David Steurer explored the SoS algorithmic paradigm in the context of differential privacy and block graphons [cite: 36]. The optimization problem of comparing block graphons lacks the low-dimensional algebraic structure seen in Gaussian mixture models [cite: 36]. Barak and Steurer demonstrated how to utilize an exponential mechanism equipped with a score function derived from an SoS relaxation [cite: 36]. A crucial challenge was the sensitivity of the score function to specific input graph parameters; however, the authors proved that "any (reasonable) sum-of-squares relaxation... directly inherits this kind of sensitivity bound," allowing for Lipschitz extensions of score functions explicitly as part of the SoS paradigm [cite: 36].

### 7.2 Imperfect-Recall Games (2026)
In algorithmic game theory, solving imperfect-recall extensive-form games (IREFGs) has traditionally been computationally prohibitive. A February 2026 study formulated single-player IREFGs using the Moment-SOS hierarchy [cite: 37]. The authors proved that the hierarchy converges asymptotically to the ex-ante optimal value, and under genericity assumptions, the convergence is finite [cite: 37]. For non-absentminded IREFGs, they showed that the convergence occurs at a finite level strictly determined by the number of information sets, introducing new classes of (SOS)-concave and (SOS)-monotone IREFGs where the hierarchy converges at the very first level, effectively bypassing the gap via structural guarantees [cite: 37].

### 7.3 MAX-SAT Solvers (2024)
Despite the theoretical power of SoS, practical deployment in modern MAX-SAT solvers has been hindered by the computational cost of solving medium-to-large SDPs using interior point methods [cite: 38]. In 2024, researchers successfully designed a MAX-SAT solver incorporating SoS-based SDP bounds within a branch-and-bound scheme [cite: 38]. By exploiting specific monomial bases and linking the SoS relaxation directly to the classic Goemans-Williamson SDP duals, the solver achieves rank-two guarantees for satisfiability testing, demonstrating that intermediate SoS relaxations can be practically harnessed to prune combinatorial search spaces without incurring the full super-exponential penalty of high-degree hierarchies [cite: 38].

---

## 8. Synthesis and the Future of the Barak-Steurer Paradigm

Looking back from the vantage point of 2026, the hypothesis laid out by Barak and Steurer in 2014—that the Sum-of-Squares hierarchy could serve as a universal, optimally tailored algorithm—has proven to be profoundly influential, though highly nuanced. 

1.  **The Persistence of Gaps:** As demonstrated by Mosievskiy and Reyzin (2026) [cite: 3], the SoS hierarchy fundamentally cannot magically extract localized hidden structures (like multi-planted cliques) from background noise if the signal-to-noise ratio falls below standard spectral thresholds ($kt \le n^{1/2 - c\sqrt{d/\log n}}$). The integrality gap persists, bounded by the intrinsic limitations of pseudo-distributions mimicking true distributions up to degree $d$.
2.  **Structural Exactness:** Conversely, when problems possess strong global algebraic constraints (e.g., optimization over roots of unity), researchers have proven that the SoS gap perfectly closes at predictable fractions of the dimension (e.g., $\lfloor n/2 \rfloor + 1$) [cite: 10]. 
3.  **Methodological Cross-Pollination:** The tools birthed to prove these gaps—such as pseudo-calibration and Kikuchi matrix factorizations—have transcended their original purpose. In 2024–2026, these techniques have been instrumental in resolving coding theory conjectures (3-LCC bounds) [cite: 8] and establishing space lower bounds for streaming algorithms [cite: 4, 26]. 

Ultimately, the study of Sum-of-Squares relaxation gaps from 2024 to 2026 has transitioned from analyzing ad-hoc random graph models to unifying computational complexity, streaming limitations, and high-dimensional algebra. Whether the SoS hierarchy will definitively resolve the Unique Games Conjecture remains an open question, but the rigorous mapping of its integrality gaps has already succeeded in drawing the precise boundary between tractable combinatorial optimization and fundamental algorithmic impossibility.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyvvnKTtWG6JCmH3h6L7cmi8X1L2J17ZgujlB2ZPSmK0awuUv5urNYPjxtXVU5gE3V0vjSKUNuXMXNAS9j2HvMfD0QPNs7YjYipWrdETyQAt2-ZbSmTOJE9RaHVzVeuGajdnQvUV2Ez8zgxWI_BTQzf6mxOjro8Ew7TTnlc8r9Lm2D5Myvu-MoSZxbpEavDRDi2PNj9Bod1XIIO8jRg6lahUATRMkQ)
2. [bibbase.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGU9xmjM8LiQTbSzBf40jAx5bIYPtN6mzktujWbT1laQ5HTOpT_jC2mmpqrgwSoV0HRRhzmbbGbrNXUuuBvsVZLL0iMlNXlHu_hsdeMm_qZ3p1bzO82EP0_M_coNSZZ4UihJpVetUAqboVUXxGw3if3gXSl7NYESfljTd5MxLcZBT_gL1_j4tug0TVnQ_I-uzK8nV1UPY-Z_h16EmjG6z-_Fpk2jrw=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLKMmaXX5F75HvXYnnlLvko7Baf5uF84KdeDDe-w3wa6gApkIhDqrhIyz7-rLXciDGC_wZ_BSeMX4mE4fA3hCL2LFViWRi21VbLsch5LUo4yXGzWazZLJPuQ==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEy0mezjwNMoacMS2QDG5kFXJ12jfGwX-bXrVI8AWQ2nAfn6PfVU5lo6tBm_XmUfbJqRGB3VMKDbMt-k7GoiLYriyd-6sruA1Y4BfZzjLiIvaZ0yA1SK03n-f1DTxG7dgsl-i6bc2ciaYoa4m10wY4eeqwoC5Cvnb--j4xham6_LcCOyygz2sHDmlkOHIevzh8KMlne6Sxx6TGJpWfczRuwCMPp5zwZZG6_3A==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAKn5VIEqRiHrin6gBE5swoms2cr_yL84cdqZrHEoEjUPofXY5Dl-15bgzozXyZeuBbgD2ClWpARxvZLR3VOmnJsMjhRCW4RFLOuK7pcFq0RUWucER77DDXg==)
6. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyfuIDJpoI_aZfPOXWvGh8RjK9yfjqweE3g0WJfb84qIfWZ5Mp4IkpLNFpBuPplFHTVRANers10nhMe_DAmn1v92jkNDnLp-mTeWLENfrMLoppa_srE0MvdmgrasVoUAgVB3vmRhPBljfA)
7. [ieee-focs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtnmXkMnMmR4HFENnlnjFQWegpyPMbDtZf7gdBv7bhfM9h8NMUasZvkqaeSHnnr3Xil0BPSuXiGSKJXS9ic5FLDCQ3-EbHDRfw3ezi8IMatboGOY7w2lH_Hv7ULeQNFUaoS37fSNlsIHBPoGfkVvbHDn7eZ0APCOgBmXuhGJJbM5jD3XUV1rHV_yGBRfMcuTYhjUyAgsxnPp9oYA==)
8. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbUmXXpab1A_pGX_vKTyglLNwoo4LZ78xaufWzQGBPJSLvTnGnaxu88DKb2DUpZ1mI5OdQWyiMNMKMNoAWObQT_dvhcSaM_63mhhAPykKu4KBsiAE7AvGpQvQoibzDcALz89hDXU7urJGwB7H063LgAanJgVS05Dd0mqyE1r6F4NJGN1W5CgyzydllkDUrjY9XDZZ78nSE4Fb_e_yUMY96OntD5dSjvNcgNg==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrfavIiksvRKQlMQSNFGuS0fVTPJc7Ws4ptWMAB1QDNkQxlQizHA1prquqBTn77pEEbJ9iK_ZsUE41gqv5nhaaNt-K97QZPiFLd6Nvesj4uCJin-SGaw==)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKU-bUt5PrrNFXFAfp4rOIUrSJO9mfl2eliGA1XhY0GqqWhu42un_MojuUujcZQJX3pEzGC_GcPApnNSjKxk_2QGS1R6ArvsLN6m_VFG_8pOsaw2pLSIgxY2ioqZWYtljvZ5W5xHVJDvBmj7A3iNL0U6EtaepnR0hmx7eVF2xvDa881zvzJa41Le6EmTR_1wEN0laepZMtXmEjCG6O6ZXEA5Ima5GvR1wZA7kiV_lAoUNCdVDYrVIzABVsu9kyl5hdDDUl)
11. [informs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOgu3XOcoayQE2uuPrGCp_HpUx9NZRu0O1sC88OWaTi5iXjYFiIYRKC6WTHBM6n70RT6BOYbxQVMJ5tSM5QD96Vwrv40BSd7VfuCkMKf8wSn61Fv1YQkolIPnUrAQ_nu2jostMQ0WaJkCwBYI43tk=)
12. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFe8mZ6m8ug7JlamNfNIUBVBkkg06Ueb921nycXp2pYTrE9aNM8EcgpTNuUMZgnZTqTLO4Ec_QQe3dSxKVKLH74pMhW0Q7wCog0LIbdWnD01eWnmUf5ULU4puOoqMT122ZNQQvbDzhl0wkaAcTOdfKzG6TNMbWcVdP3GrZnQnA2SyRLUM=)
13. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6EXUQgNp0wZ8b8EQRFwWtpyF4LZ_TVPkOYcE7LNI3lrWcr0O6_zTeFYnGl20PYJVlhPrHhXm-J9P_cKBHxhUJvBCoMWxIOhrgTTf2KfTNfCQJGkhXQBZtYkjdA1M7TaFCslG_oLHtPQuEMM3ekrqxZi-x8GsER-wCW-27q4kgcWXhGl4Lja5t)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETdeTSSWOmJ78rnX_8tgdto5ULDfVEI8_VVniv6s-m26iz7RepEtgiyM9xOk8jgiXpewDTGVDHn2o8nCxf_yp0DukmVLU8Y8Q8IzmUXSazO8GRRYEqdg==)
15. [ias.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHm3W4SwK5NEUP_KifwiswDUB9k5eWpRDB5x6UZnSEypP1JCTIsKnrie7gg2sMqxnfukRVMmrPSCYvTkQIIUzapaZS0rUG4khZst29TJIXRVxSgatEG07Z2QVmlIFMC9Cg4wpnWy4l3j1CgKcr2cvZPByZ9qe1xR-cN9_TscIjIN0tfAQ==)
16. [sidhanthm.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ07zIgR4nCUDgovdvtv7kGp5NcO9jNgSlhsUf9YzJq4y-0Zp_A0XCQ-HVZBWn0JrLsp1-j3eEZ3zJQBpmUsY6TjiT1tYreB17Y1yoP4ujQoL_YcT27cs6287ERhc=)
17. [berkeley.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFggZCMbISTvRRyWRWl0Micfsha1HExPmTS3_jpH4T_VNOKppBRTLs1OeX99d71XTV51qzqnWcBVCJXsjLldH64I-p_waOmEes8dLboudMlDVraE856UxXlY7WwVnvJW_qSsE0EUpABHvgdU8hMMw==)
18. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEywK0Y2dG8-kLwNrsN1F0Xu-wvNRiF3h8HJTaDT1datex8i2-DHTdE_-oUBTcuf86bXJ_fvBzLYwOhTEEMgFoo2AXOicmQ3mFNTKPd8YBf06-NU3bY2hPFnWNQVFTZnq-cSuVJ-tHAYGuAqqBmdYkiqWd8MCFVSF9IZDyTRIZrfXULEk5pT5mpagIyhj5lge1XnCpxd6Bc2FS3fC_mZ1elG5kOf2XxNBQVi1DoiT256JhDFYTcDMTnsRWPNIXElqI67UVrNPs=)
19. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1ZU6Ad5uT_n0iMEQmfDvi14x6nhCixf57aLhJKCId4m8DpyIk12oVF8Ev4dI9Y9XtWjH3jpPo-oa2Po5aPZQvVvM3u_KsPYau7E_cRbywsYNCTmCCBixLHRwWRPsrU_Twts0=)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSuMx6aYIq5FarclzVqUvLRtkv9bp_2eudGs1g0eGGg2rLjUYRVAQw0vgBHjJpjCEVaJaOSqYoRtyKkG60zPcmYNZHjo3pu1LscSEWpJ48Vmc7kyXrMRs0uLTBQixEcLs7lVxJ0HNjm7mUTk0EA_twkcduHH4H-GL6eeG4DN7i9iyrNREphYTmLl23B36MvrEYXYtpd0AG57XJwY2VOClQjakKzEtx1w9ZbdZCS93c9yk=)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyPicN22Sx6ailmtGe_9RIBfWabGkuWjpH5H_FPFTDLoElR43RY0g8d3TQDTeQqAMu3vFzlpJ77xqGnrbQCP6jf7yDxzbTTSTmxXfeGyuFhZSK6j6vSxNUb_eNhcdPKptMMiOe4WhjV7DlUy0ZEb4b-SU8HtVsyJXd7hG95m6__q-Qb4Z_CBmxfDwnjLvJpw==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6uSMU4lDANsZD3J4MOo-mepeK1EMuHEHrjPiAGenlqMiNJw1tjjhX-kRvfoHIUnVLPFGgqWZoWlxX8PO4_n6CUgZIF-pu1lOUwEpmrwiyD7KticNc5g==)
23. [princeton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHetJDsDotij4dC7J6PgvruNApFcb_sYozjoHBLHfwwqvDtZvMVoF6my0TCWnVeBteLZPKFqcgKCXBiTosmKHGA5eNVVvhDzZE8sWZpkG3F-3yH6BgTreUnIjR0Gw==)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMgNrUb6cjpZKJXMlie9NiS1DphIKUkbHhDeQ_U89i7i5x6Vl3AjkadjQbP355jXXzJdXMQDB-u4zT9-DSETT4_vthQKsIbkbLotR2joMCGr6mhgJISOi7otKha9pOoUcjM2p-wkEGPStZNdEVk1gsCMZ7tWC58vgTpE6uF8WtwnQiTB9yHmEWqkidL7TuuEPa7YclLmFcElZvjOqkgtYxTXsd)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBWCtfM50bJ8IN6BHvQ13e0zZvBKZsowjnUBfIcLBjMqpOO7e_SiaUOhRkyf4y3rntE0gAFa_QvYs7blfOqSp5pZK8ABj3gEPF3ZQrZRbOxDVj6ObBoQ==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGx8r-LkmE8w960XkgmAi4VG-7Rxnj6CQ2KGniIm82b4eymDOUVoYXF2y3I7FHKXZWCVb5cbt0dWQiGAkKw6XY4KUIorAOcTVzcMIqgfMRSnmv7aQbMlQ==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-hpA_ln2dSjUW-gEb7DNdpxB-fFE-VTkHr7iHP-mo_KcDCTkcHKe3L59utyJ_EbCKPtHk3hoEeFgK3afnUEo8KaEdse-N9QZUMJ3ADrq-TO9p3PRn8DPsOLohgFugXTvhQOS6GVKrv4YqaHtbMk4Ljt57vkf9VsPOU_AnCetgri7JBBq9pJL8-d7asHaGR6DQqZupBIlrUCZwOVmaEK5GKhb7)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1gw0YayO49SzMa8tvq3qgmPoYpQs0fOXYJ1R_AVr-2wsvRFKTB5Hj0wQxNFokEA6tQC5OOnhR88bja7jvPHadGnCk_Y9bqyQ2RFeOnE22O6B3px3-SA==)
29. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwAXeYzPghG9qAzAJXO4H8FAjkdsqgO92coTtv3FuntXJOdQxfyfejHZrQ2000KG3OHafhaoidHwVXjyYgG-G2Ty1sttiAdwK5MsIgYGoSu0URzeQgSzop3R1KPScWxFa2)
30. [elsevierpure.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJEobRgjRayWrI28MNSVVVBbJYEpigGSAwbXpZnBU-8HqWxpPC46bSuVzVY4Zl12q_998mynetlQ9xlXThAi0A1C4ily_V9T3vaIYDk0a1y9LaXGbWvd5LG6BcvQKuecCULQ1SD9IqcB5NOMWfoIOt9exNfNpIyyThjJcMHyaUdo4SBrXoGueZV5kWUUnw__-S23swYhq4JrRayS8-8IlJCLSk8rv6RI8=)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRU2lMhREpOry4cM9MlySx8BO2qQCcqBsrTpumgZhXsBwh9z-9c0_YRzrxRCcUrUZ7PcE3O-CLQMnuavbWGr4xcIJTM1CzM5DdLT8__Q1e5ILGqd6kCQ==)
32. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpXfz7p7wyafSE2ZXdQdurgBcIaDvHnZh9IXgY0MqMfMn1NpDmPIr9kwPnlNNcrGOuKwIRy93nLmvH7oJwmetWJFH9fCTwRGqpfYBEA2dEKc4I0NBIR-YzsO5ViFbCeN1bMcyhu9rud9jRQsAGvscrQGhTLw==)
33. [weizmann.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB7pSgpa-m7wgeQrCsGZ-PYv25A1IWb5ZfyfRw6QtOJKYcy0hmHKDWHaz9NwUDZZQOJAbmvWVqe3BwwokXERu4v3-KXtUE7jbF4d3v6UGiH50i5xyDjNuGvCaPfF3lF8o1yTAXN9B0vIyUH-ybmCrNlWs-jKY=)
34. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETOvLNa2LTISUwIuj0I3besPenl-Y3ohyA47ITSJLgPpEMwkVq1VYuKEL9W_KpxJHKhdbICLsZXvwucYMKY0FgDYQN_s_RgVwfEgLyQXp6IE6xeiTp6tQghlyDA6e66VtRUdXxnuN4)
35. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPyKt7HhnmDQmfRGcWfOq8qU7sQbVZPVjcWSomho03bEwJgizFRmxNj3ADpyouELObk050MNvfdTlfvJSCrTXpZ4Fd6aB8RpeXEC63vCRuRqcc8H1P0nSVHhDgzKfb97KuuUcnemKL)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbrBhMDpHWi_K38nW6Ol0F67HjdqmWeo0xveszWb8-jzM5_GmTOuWzPgouIz63AoDoBHFn1VV3euSVFG7DswJH6yHlQKEAxykskJ2m2T_iPlTMORt4gg==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrTNRsMo-QiwbQh-vEyToC9T04NMWvtMt1v1r7ruC6N7Lt8jxpHFg3UID7L2-fLqIABfZc4BCZ3nlnA-pWOwqz77mrC7xxE5Qv8e_tUwl_mwAtiaaPJA==)
38. [informs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXdDKUQRh3qZYVJZCXqId7pRg7f5uXEqwHd7a-VNn2rS3wHLMOBGYirjyoVEZKlZ1MKMnvrBHFfEJnn2369TI7ljE4r8WhpSCecwzOjPTJYSgqRSDahVlWWWEh4nODCb8vEMkRTJ4GuDau25VVzYU=)


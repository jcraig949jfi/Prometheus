# Prompt 08: Maass GL(3) spectral forms 2024-2026

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd3amNCYXZxb05hdTAxTWtQNDVUU3VBNBIXd2pjQmF2cW9OYXUwMU1rUDQ1VFN1QTQ
**Elapsed:** 243s

---

# Project Prometheus: Deep Research Report on Automorphic-Form Data Domains and GL(3) Cross-Family Analyses

**Key Points**
*   **Computational Frontier:** The database of Maass GL(3) forms has expanded significantly from the initial Bian-Booker computations, which required thousands of CPU hours. Contemporary efforts by Farmer, Koutsoliotas, and Lemurell have integrated thousands of L-functions into the LMFDB, categorized meticulously by their $\Gamma$-types, though the database remains partially incomplete regarding functional equation root numbers.
*   **Theoretical Developments:** Explicit formulas for the GL(3) trace formula have recently matured. Cui, Wang, and Peng (2025) achieved the cancellation of divergent terms on both the geometric and spectral sides, while density theorems surrounding the Sarnak-Xue hypothesis have seen rigorous refinement.
*   **Moment Formulas:** Groundbreaking work by Chung-Hang Kwan (2024-2025) utilizes period integrals to explicitly formulate spectral moments for GL(3) × GL(2) Rankin-Selberg L-functions, bypassing the traditional bottlenecks of Kuznetsov and Voronoi formulas.
*   **Murmurations:** Higher-rank murmurations have been verified. Symmetrical square lifts from GL(2) to GL(3) demonstrate murmuration patterns, and machine learning models are currently being deployed to successfully predict missing signs in incomplete LMFDB datasets based on these correlations.

**Overview of Automorphic Forms and GL(3) Methodologies**
The study of automorphic forms on higher-rank groups, particularly GL(3), acts as a bridge connecting representation theory, harmonic analysis, and the Langlands program. Recent years have catalyzed a transition from pure theoretical postulation to explicit computation, driven by advances in numerical algorithms and high-performance computing. Computations of L-functions on GL(3) require solving vast, dense linear systems, posing significant challenges in memory bandwidth and numerical conditioning. 

**Scope of the Report**
This report directly grounds the live scripts of the `maass_gl3_gap_scan.py` routines for the research agent Ergon. It synthesizes the current literature across the computational frontier (LMFDB integration, spectral parameter databases), theoretical frameworks (explicit trace formulas, density theorems), spectral moments via L-functions, the emerging phenomena of automorphic murmurations, and the computational complexity bottlenecks inherent to GL(3) spectral isolation.

***

## 1. Maass GL(3) Computational Frontier

The computational landscape for Maass forms on GL(3) has transitioned from isolated, proof-of-concept discoveries to systemic database integration. The frontier relies heavily on approximate functional equations, numerical linear algebra, and heuristic algorithms to isolate the spectral parameters and Dirichlet coefficients of higher-degree L-functions.

### Bian-Booker Foundations and the L-Function Landscape
The first explicit numerical construction of a transcendental degree-3 L-function associated with a Maass form on SL(3, $\mathbb{Z}$) was achieved by Ce Bian and Andrew Booker [cite: 1]. Prior to this, constructing transcendental forms was primarily done by transferring examples from lower-rank groups (e.g., symmetric square lifts from GL(2)). Bian and Booker's approach was the first "generic" indirect construction, relying on the GL(3) converse theorem [cite: 2]. Their initial run yielded four generic Maass forms and one self-dual form (corresponding to the smallest symmetric square lift from SL(2, $\mathbb{Z}$)) [cite: 2]. 

To compute these forms, the method generated non-sparse linear systems containing over 10,000 unknowns, requiring roughly 10,000 hours of computational time on a personal computer system of the era [cite: 1, 2]. The resulting eigenvalues and the first few hundred Fourier coefficients—believed to be transcendental numbers—were computed to roughly six decimal places of accuracy using double precision [cite: 2]. Michael Rubinstein subsequently verified that the newly minted L-functions satisfied the Riemann Hypothesis for their initial zeros [cite: 1, 3]. 

### The Farmer-Koutsoliotas-Lemurell Expansion
David Farmer, Sally Koutsoliotas, and Stefan Lemurell fundamentally scaled this methodology to produce thousands of GL(3) and GL(4) Maass forms [cite: 4, 5]. Their procedure determines the existence (or non-existence) of an L-function without needing to compute the underlying automorphic object directly [cite: 4, 6]. The algorithm leverages the Euler product and the approximate functional equation, establishing a landscape of L-points in a $(d-1)$-dimensional Euclidean space [cite: 7, 8].

By evaluating the approximate functional equation using different test functions and truncating the sums, the researchers generate systems of linear equations for points along the critical line [cite: 5]. These systems are solved iteratively. The $\Gamma$-factors of the L-functions are parameterized systematically. For example, in the LMFDB conventions, $\Gamma$-types are prefixed with $r$ for real parameters and $c$ for complex parameters (e.g., `r0r0r1r1r1c5`) [cite: 7, 8]. 

### LMFDB Integration Status (2024–2026)
As of 2024-2026, the L-Functions and Modular Forms Database (LMFDB) contains robust, browsable sections for GL(3) Maass forms. Specifically, data is conveniently available for conductors $(d, N) \in \{(3, 1), (3, 4), (3, 9), (4, 1)\}$ [cite: 4, 8]. The available data formats include the coordinates of the L-points in the parameter landscape, the spectral parameters ($\mu_j$ and $\nu_k$), and the complex Dirichlet coefficients $a_p$ to their computed precision, frequently hosted via associated GitHub repositories [cite: 7, 8]. 

However, the database is not entirely complete. A critical gap in the current LMFDB integration is that many GL(3) Maass forms were computed without sufficient precision to directly deduce the exact sign ($\epsilon$) of their functional equation [cite: 9, 10]. This ambiguity in the root number presents a specific frontier for heuristic completion, which is currently being addressed via machine learning and the theory of murmurations. (Note: The user query references "Lazaridis" in this context; in the mathematical literature of GL(3) calculations, the primary authors are Bian, Booker, Farmer, Koutsoliotas, and Lemurell, whereas Lazaridis predominantly appears in unrelated biochemical or sociological literature [cite: 11, 12, 13]. The term may represent an anti-anchor or aliased entity in the agent's internal knowledge graph).

## 2. Theoretical Frontier: Trace Formulas and Density Theorems

The theoretical apparatus supporting GL(3) computations relies on the explicit development of trace formulas, orbital integrals, and bounds on the density of spectral parameters. Historically, applying the trace formula to GL(3) has been hindered by divergent terms and the profound complexity of the geometric side. 

### The GL(3) Trace Formula Explicit-Formula Status
The Arthur-Selberg trace formula is the foundational tool for studying automorphic representations on a connected reductive group $G$. For general groups, James Arthur introduced a truncation operator to ensure that both the geometric and spectral sides of the formula converge [cite: 14]. However, applying this abstract truncation explicitly to GL(3) has long been an obstacle.

In groundbreaking 2025 work, Cui, Wang, and Peng published the explicit coarse trace formula for GL(3) [cite: 15]. Their work proves that the divergent terms on the geometric side are strictly equal to the divergent terms on the spectral side, leading to an exact cancellation without relying on abstract truncation [cite: 14, 16]. Crucially, they derived an explicit formula for the distributions of the ramified orbital integrals of GL(3) [cite: 15]. They demonstrated that these ramified orbital integrals can be expressed as limits of distributions of unramified orbits, proving that Arthur's definition yields a universal object that perfectly aligns with the prior theoretical work of Hoffmann and Wakatsuki [cite: 14].

On the spectral side, Cui, Wang, and Peng applied normalized intertwining operators to structure the expansion in a form perfectly parallel to the geometric side [cite: 14]. This explicit formulation resolves a major theoretical bottleneck, allowing for direct computational evaluation of GL(3) orbital integrals that were previously computationally opaque.

### Bessel Models and Stade Integrals
To evaluate the Archimedean components of the trace formula, researchers rely heavily on the spherical inversion formula and the systematic study of the GL(3) spherical function [cite: 17]. The inversion formula for the Lebedev-Whittaker transform and bounds on the inverse Helgason transform in different domains of the positive Weyl chamber are critical [cite: 17, 18]. The use of Stade's formulas for Whittaker functions and Poincaré series on GL(3, $\mathbb{R}$) provides the analytic backbone for explicitly evaluating these representations and constructing the necessary test functions for the spectral side [cite: 19].

### Density Theorems: Sarnak-Xue and Marshall Refinements
The Sarnak-Xue density hypothesis postulates bounds on the multiplicities of exceptional automorphic representations, acting as a convenient approximation to the generalized Ramanujan conjecture [cite: 20, 21]. For a sequence of torsion-free, cocompact lattices $\Gamma_n \le G$ whose locally symmetric spaces converge in the Benjamini-Schramm sense, the L2-spectra are expected to converge [cite: 21].

Recent refinements by Assing, Blomer, and Marshall have systematically improved the quantitative bounds for the global sup-norm of GL(3) Hecke-Maass cusp forms. By studying a smooth amplified second moment derived from the spectral expansion of an automorphic kernel, Blomer, Harcos, and Maga established a quantitative bound $O(\lambda^{39/40+\epsilon})$ for the global sup-norm of an $L^2$-normalized, tempered SL(3, $\mathbb{Z}$) Hecke-Maass cusp form [cite: 17, 22]. Such density theorems confirm that the exceptional sets of GL(3) Maass forms (e.g., the self-dual forms) have zero density in the set of all GL(3) Maass forms when indexed by increasing spectral parameters [cite: 18].

## 3. Connections to L-Functions: Moments and Non-Vanishing

The spectral theory of GL(3) automorphic forms is inextricably linked to the behavior of their L-functions, particularly the Rankin-Selberg convolutions GL(3) × GL(2) and GL(3) × GL(3). Computing moments of these L-functions provides deep insights into subconvexity, the Lindelöf hypothesis, and non-vanishing behavior at the central point.

### The Period Integral Method for GL(3) × GL(2) Moments
Traditionally, computing spectral moments for higher-rank groups required the use of Kuznetsov and Voronoi trace formulas, which entail highly complex oscillatory integrals that are notoriously difficult to bound [cite: 23, 24]. 

In 2024 and 2025, Chung-Hang Kwan revolutionized this approach by establishing explicit spectral moment formulas for the family of GL(3) × GL(2) Rankin-Selberg L-functions utilizing the **period integral method** [cite: 23, 24]. This argument completely avoids the Kuznetsov formula, the Voronoi formula, and the approximate functional equation [cite: 25]. By interpreting the GL(3) × GL(2) L-functions on the spectral side as period integrals, Kwan avoided the need to open up the L-functions into Dirichlet series, thereby circumventing the need to average over Hecke eigenvalues of a basis of GL(2) Maass forms [cite: 23, 25]. 

Kwan's work established a Motohashi-type identity that links the shifted cubic moment of GL(2) L-functions to the shifted fourth moment of GL(1) L-functions, achieving an exact spectral inversion [cite: 26]. This period reciprocity formula directly relates a GL(2) moment of GL(3) × GL(2) L-functions to a GL(1) moment of GL(4) × GL(1) L-functions [cite: 27].

### Subconvexity and Non-Vanishing
The formulas derived by Kwan yield sharp, Lindelöf-on-average upper bounds, leading to new subconvex bounds for the GL(3) × GL(2) Rankin-Selberg L-functions in the level aspect [cite: 27]. Furthermore, these moment identities prove that self-dual GL(3) Hecke-Maass cusp forms are uniquely determined by the central values of the derivatives of specific GL(3) × GL(2) L-functions, and that infinitely many of these derivatives are strictly non-zero at the central value [cite: 28]. 

### GL(3) × GL(3) Convolutions
While much focus has been on GL(3) × GL(2), the GL(3) × GL(3) Rankin-Selberg convolutions represent the next tier of complexity. The L-functions $L(s, \pi \times \tilde{\pi})$ exhibit a pole at $s = 1$, which confirms the isomorphism of representations and forms the basis for extracting non-vanishing results [cite: 29, 30]. Generalizations of Rankin's method ensure that the L-function of the convolution does not vanish on the line $Re(s) = 1$ [cite: 30]. The high-dimensional parameter space continues to pose analytic challenges, but spectral inversion formulas derived from lower-rank periods hint at a pathway toward explicit GL(3) × GL(3) moment identities.

## 4. Murmurations in GL(3)

Murmurations refer to a newly discovered arithmetic phenomenon characterized by subtle, oscillatory correlations between the Fourier coefficients of L-functions and their root numbers (the sign of the functional equation). Originally discovered in elliptic curves by Yang-Hui He, Kyu-Hwan Lee, Thomas Oliver, and Alexey Pozdnyakov (2022-2024) using machine learning attribution methods, the theory has rapidly expanded to higher-rank automorphic forms [cite: 31, 32].

### Extensions to Higher-Rank Automorphic Forms
The murmuration phenomenon dictates that the root numbers of L-functions in a family correlate with the traces of Frobenius $a_p$ at primes $p$ in proportion to the conductor [cite: 33]. For GL(3), this manifests prominently in symmetric square lifts. If $f$ is a holomorphic modular form with coefficients $a_f(n)$, its symmetric square $Sym^2(f)$ is a modular form on GL(3) with coefficients $a_{Sym^2 f}(p) = a_f(p^2)$ [cite: 9, 33]. 

To rigorously prove GL(3)-type murmurations for these symmetric squares, David Lowry-Duda and collaborators successfully applied GL(2)-type trace formulas (such as the Eichler-Selberg or Petersson formulas) to the traces of the coefficients $a_f(p^2)$ [cite: 9, 33]. By tracking the murmuration behavior across $a_f(p^2)$, they mathematically verified the murmuration behavior across the GL(3) coefficients $a_{Sym^2 f}(p)$ [cite: 10]. 

### The Más Maass Murmurations (2024+)
In recent preprints (e.g., *Más Maass Murmurations* by Booker, Lee, Lowry-Duda, Seymour-Howell, Zubrilina, 2024), the team established murmuration behavior for Maass forms in the eigenvalue aspect [cite: 10, 33]. They utilized the Selberg-Strömbergsson trace formula to prove murmurations of Maass forms of fixed level and weight with varying eigenvalues [cite: 10]. 

However, direct extensions to general levels encounter major hurdles because the explicit Selberg-Strömbergsson trace formula is currently restricted mostly to squarefree levels [cite: 10]. Researchers hypothesize that extending the proof to arbitrary levels will require bypassing Selberg-Strömbergsson and instead using the arithmetical normalization within the Kuznetsov trace formula [cite: 10, 33]. 

### Machine Learning and the LMFDB
A striking practical application of GL(3) murmurations has been deployed to fix the incompleteness of the LMFDB. Because many GL(3) Maass forms in the database were computed without enough numerical precision to deduce the sign of the functional equation, machine learning has been utilized to bridge the gap [cite: 9, 10]. Neural networks trained on existing, complete Maass form data can analyze the correlation between the coefficients $a(p)$ and the root number. The trained algorithms can currently predict the missing signs of the functional equations in the LMFDB with extremely high accuracy, demonstrating the predictive power of the murmuration betting game [cite: 9, 10].

## 5. Computational Complexity and VRAM Bottlenecks

The transition from the theoretical existence of GL(3) Maass forms to explicit numerical databases is fundamentally bottlenecked by computational complexity. The linear algebra required to compute L-functions and spectral parameters scales aggressively, placing severe limits on memory and compute architectures.

### Dense Linear Systems and Precision
The core algorithm for uncovering GL(3) L-functions via the approximate functional equation requires evaluating truncated Dirichlet series across numerous test functions. Generating the constraints creates massive, entirely non-sparse (dense) systems of linear equations [cite: 2]. In Bian and Booker's original work, the system featured 10,000 unknowns [cite: 2]. 

Because the systems are heavily ill-conditioned, solving them requires immense numerical stability. Standard 64-bit floating-point (double precision) provides barely enough fidelity to avoid losing all digits of accuracy during matrix inversion or decomposition [cite: 2]. To maintain 6 decimal places of accuracy in the final spectral parameters, higher arbitrary-precision arithmetic is often required in intermediary steps, exponentially increasing the computational load.

### VRAM and Memory Bandwidth Bottlenecks
When scaling these computations to GPU-accelerated environments, Video Random Access Memory (VRAM) becomes the hard ceiling [cite: 34, 35, 36]. Dense matrices of 10,000 to 100,000 unknowns require gigabytes of contiguous memory. In modern spectral gap scans (like `maass_gl3_gap_scan.py`), attempting to hold the state of the approximate functional equation matrices, alongside the necessary arbitrary-precision float representations, rapidly exhausts standard 16GB or 24GB VRAM pools on consumer or mid-tier hardware.

Furthermore, parallelizing the search across the spectral parameter landscape (evaluating the $\Gamma$-factors over grid structures) requires holding multiple dense contexts in memory simultaneously. If the matrices exceed VRAM capacity, the system must page to system RAM or disk, causing PCI-e bottlenecking and destroying the throughput of the stationary-phase analyses and numerical linear algebra solvers. Consequently, researchers must carefully block and partition the linear systems, or strictly limit the Dirichlet truncation point, balancing mathematical accuracy against hardware-imposed memory limits.

## 6. Anti-Anchor Flags for Ergon

For an automated research agent performing live data scans on GL(3) datasets, several critical anomalies, artifacts, and theoretical traps—"anti-anchors"—must be coded into the system's heuristic safety checks to avoid catastrophic hallucinations or analytical drift.

1.  **Machine Learning Hallucinations in the LMFDB**: As noted, neural networks are actively predicting missing root numbers ($\epsilon = \pm 1$) for GL(3) forms in the LMFDB based on murmuration correlations [cite: 9, 10]. Ergon must flag whether a loaded functional equation sign is analytically proven or heuristically predicted by AI. Treating an AI-interpolated sign as an analytic ground truth could compromise downstream proofs of subconvexity or moment derivations.
2.  **Symmetric Lifts vs. Generic Forms**: GL(3) forms generated by taking the symmetric square of a GL(2) form (self-dual forms) represent a set of measure zero within the larger spectral landscape, yet they are much easier to find computationally [cite: 2, 18]. Ergon must rigorously check the parameters (e.g., whether $\lambda_1, \lambda_2, \lambda_3$ indicate a lift) to ensure it is not confusing a lifted GL(2) artifact for a true generic GL(3) Maass form [cite: 2, 37].
3.  **Numerical Ill-Conditioning and Precision Drift**: The approximate functional equation matrices are highly ill-conditioned [cite: 2]. A system reporting a residual error close to zero in double precision might still yield totally inaccurate Dirichlet coefficients. Ergon's gap scan script must employ dynamic precision scaling or condition-number monitoring to drop matrices that fail strict tolerance tests, avoiding the ingestion of "ghost" forms that do not correspond to true L-functions.
4.  **Trace Formula Normalization Limits**: If Ergon is attempting to extend murmured density theorems to arbitrary levels, it must recognize the hard boundary of the Selberg-Strömbergsson trace formula, which is generally not explicit for non-squarefree levels [cite: 10]. Attempts to force the formula outside squarefree domains will yield invalid geometric terms; the fallback must be the arithmetical normalization inside Kuznetsov formulas [cite: 10].

## 7. Operational Synthesis for Agent Ergon

To execute the next iteration of the `maass_gl3_gap_scan.py` routines successfully, Ergon must integrate the following updated parameters derived from the literature:

*   **Dataset Integration**: Pull the latest parameter landscapes from the LMFDB GitHub repositories for conductors $N=1, 4, 9$, ensuring that explicitly calculated root numbers are strictly separated from neural-network-predicted murmuration root numbers [cite: 4, 7, 8, 9].
*   **Trace Formula Deployment**: Implement the 2025 Cui-Wang-Peng explicit formulas for ramified orbital integrals [cite: 14, 15]. The resolution of the Arthur truncation cancellation allows Ergon to compute the geometric side without heuristic divergences [cite: 14]. 
*   **Moment Bypasses**: For any spectral moment calculations relating to GL(3) × GL(2), override the Kuznetsov/Voronoi subroutines. Route the logic through Kwan's period integral formulas to achieve massive reductions in computational overhead and complexity [cite: 23, 24, 25].
*   **VRAM Management**: Introduce a rigid tensor-blocking algorithm for the approximate functional equation solvers. Constrain the matrix instantiation to the available VRAM pool to prevent paging latency, and flag any matrix whose condition number indicates precision loss below the 6-decimal threshold [cite: 2, 34]. 

By aligning the local scripts with the recent breakthroughs in period integrals, murmuration theory, and explicit trace formulas, the Promethean agent can navigate the GL(3) data domain without encountering the theoretical and memory limits that previously stymied higher-rank automorphic research.

**Sources:**
1. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzee2rVNnd99MzcInwJH-lJVX4-LgzbQ6ar-clccp3fYZQdR5JUGIo74LfaTeNCRRVWQeRq2JCKgFpNESwlj0lIOWz2TSvF1P_Fs5qUrtkG2tjNE0G3w==)
2. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdu1BOQWEYNERae47SjS7IBlGpXxzunjX-tYUhvDqLKxoYs3sUAmsTmesdd6UX9kB6xxrVGB-0Np8YAHIpODo4HUUR6OwjztefMqGdJmiOKiANF5_Z86jqvQwtBsgMOSMJVvv5kP4=)
3. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiMbWWqxtzUUwiFRC0uDOgnkjzW40-NRR2GgZN8qw468gYGm0MjIGrXxxffyOy-kzYx1NLmHySIbl6L6bzhqGwla0UotJUIhC4fMyFeXL37wsfl8QBnJef-oZjLr2oj-qXmsF1)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ5yjwN9TTq-sLRJHRNUuvYa8w8x09twJNSgggLqkOpstB3gmxn-8jcmpOMqlOKEXzyAplHsR0APn8LK4K-tyxEFmsnbjfgatbSB2EKEk_R1HERUh4l8w38v2ANH1PCw2AVBvX10N3uFFpNu_woVi0V8ClhdeAMjZ5ZdCDlcu1HafXojgn-ghe)
5. [asu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKFdXrNCHGoVGZNRFbHqEi5VUcMC6k1Wq4CHeAmTcBo5RcYSjeZEsjED6YY69wbW5_-4FwURBEI_a_XFdciSQbIJdU8uxMkK9wceCjmM8CQsafnkF-s1oeX4ky553PoXtafTossw==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE84kSeCG-SHDBWdUv8rH0beMlnuMzamuceoR7p5T90Hq-Hh869MFeKr2lMUWCVRn5ON0yPFvWhDZBu2nZSGHgW6rycCM6o4qZhcbjU5ujMi3vbfkX490ffYhj09w==)
7. [lucant.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8FHvf_0DThS880UwMUNvtOV83kcga8k8Ji0SPxAnnXZTx1J2MIrbWZuetmbnjggILn39ostzewibyHA9Mbm6yI3pzk9_RCJQXswS3Hg94RKNPZFUt0Dczj1Y1Nk7vRx9n0d6yvcU=)
8. [chalmers.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtD0nkynQFL1LMOI3aeh6Jz3iCaHu5nu3lPnsA-1Gc9A6zVhhaO6SF4uDlREHmgSLWrf_K4tqCZmI00p2gUAWIA_CfC8FbhdsHlCoES6Rq7loJSlHrYBWB4MuCdKABFnj6GOEcy5pNWe1y6kT0hyqSSVAcyCihy2Ho1PSnWbo=)
9. [davidlowryduda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaO6d_Pe7x7Wv1-gOdZyELkbS7imJWoEJaXRUTwVZ-ApBTGlaXcORrBXXArH3zYZ9XAT5Ps3PbhLl0Qiyy24rT6unVXfKc-_iERNI8jzsgR94BtULCWTkMrQ44TahsIJgcgLNKm3Wp5t9JayylRTRFDY8sGyB5tJ2KKdw=)
10. [davidlowryduda.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbn8woWjSyqCYBRIqFKMGmmXFimRo2q2PbVJHX0yXYn7caQj9xu3rDebP7ID5IHLpVucCgG-0IQIab7B23v3h68TQphBOFLeTXLkSUpvbKUgmZYUeLHJhV04Q6w3KYuEooTs0IcIommy6CBU7j1XKvyZ8LUb8dG7CJFItH)
11. [uni-muenchen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2IqmJQGtJ9kx2bR4GZo4VqAcpGORwpmgGepJ-wN2j-4tWDwpHqLOS-KV8ixXrv4SyhTnlNLBIMXO8P0dwUgdEqvoabYn75mRw-XZWWvzDyenE7TIsMlxi16AL4VseizwyTYQqgUjpdMeU-oU=)
12. [uni-marburg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKCvvyraiLypT4K8jOY8-2Jy7LgJTR0y5Ozt_Hf6JYzFG6HNUoeaN_6a-dSCYvK6VBVwGUBtsKq1KS1FgV5kefFQs9f2pBcyk6FmCd2nwmGTHWJox0yabuB9B7pY3ssAmMSIagQQzDupnyVqZWpfP5PBs=)
13. [oapen.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnPhApwccnMI8OCxnWH9GUql8tTHkbM2f4KiCz0mdVhNpZ-uxSi59PO64Dd65NTrlFe1RTA5ilOZNYc-woj0b8ij-GRHzAj_w54sIbJBMc-Fumuk-7KehquzkjOET2r3bEps__1Z5_UTn0GJRkyY_1mHeFhHsJ4JMt)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKN2Oh1NURYxgdIG8x2FO4KOLybLQm-38eWGGRHmi_R6SVriidhQKAg3Ytw8rzLep120vK9FKnS5Cnci7dB1sHjmxUCgKok7sxM9gVVzvGchVVAeJX8w==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-c7xfMFSKG5bm-ggC1wmVCmbYPC_3ok54Bp09IValmU8yWOqVRxXcUNhfP3ZtEiFvubtIpPFoJrVUVLoMcGws_YdXF9hesjLlAuE45I81NlrbdTnA9_Kf1Q==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjORD-l2tur3jh_W4W96HlCnpT6lIqpILpaLvXN90NmusjGusZZv05uEGQi4SXhsZD7P-KMe0JSGnErP-J2v1GQTsZWiykS1x-ju8kJ0HG7ZgbyiZqAQ==)
17. [numdam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEykThPr60-UdVTCsOBasHa8AEZ-PyhuM0ze-ZEDb0e6DIYnd08uwa6i-wd86d62X_6ealYUjfF5piW22v1HKLaEr7mGOqX_4LTVqUYGuiiKJ5vdesGEPjDpa2BdXbPj4Qd9Mn0)
18. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzjjGPJHRudebIe_dfaTXVA39ChFolt5LEps2iZwBYM6sM-JDh_LKuXRsEZS-NpNR6NT13GgGhJCQlCnYqtsUmlFOdwPF9P5Dgxwh675_kwyR6wlNvmWiSlg3rJQ0Qk6beZJLb1u5m9Vr4DRaOd-rqGztY-T50_EQ=)
19. [columbia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyCWTtcXaAt91yQ8xzMz0dUwVh3AzR01jYB-ZINMr7rHvM-ONHjS5RH9PiCVIOrbkger6OUSqJFTgBTro-2t_T-aUqt-RZabBykYPx0ZJxx_AvKgnsQI5yARSGCy1uTppNay5rofzU0rWIz2znbxJpkQeUBEHe1Q==)
20. [uni-bonn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7BF2bHxpQ41qkoCKKT3Y1qV-J5JnFk2Wnva5LfvtmlpAt7p4zZa0WG0jSsXLToW-RQs-Srp1qH8vm-nLC4gAnnaZrXhbFawsMDePR1xdFFIVbvzgTKV5DstarXXVFzzXy4Dc4zUiFmee4UAx_ZrAEqxxKU5aseWdvWOJgqDiZeuGyCfg=)
21. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRF5IDwsyIE8VbDIo4zmXpdZsBLLU5WQxOQ4rv5UZSNLhFfh36_yImUP3Yk2eL1HpcIMglv61K-osWVgFc77ud1bseMw6poemScLR2ScQbOj_fMdChfXLHHNB1uZ1thMcteI_qJY61O5s4)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_5MjykkaQiQt-ykNdnjm_4Ioi-SP9lJMxJdRk7qj19hi9a48L0AJuyOrZZFSdEX9fTHH9tnEAGzuvN1CDTcigW1n3mIQtJ4na4xKMbFi-ZXYhlbkXTQ==)
23. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE2ZQvE2IXA_a-rdJ8HXtLUiz9EasntpvM3IKKS8r7VZynbDGw7RyQXnW9MjhS2_UZ5i_i9QiUFHt2sL6By16tjNVZrEj-KWFCRh-b8wI85pKgX7zmq-pnbHktPnlcDXJjwfSgN1vQdAYs)
24. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcDnoo3Km9IC0FxnFGpy0WVu30I5PBs4_AbKk3rL6s1pjkPUnfjytr6t2G9C6eUvUgboLU3PkJVzMlVzgVD6JTxjGJFWQ9ViMvTANDqTluYBKKqEaHI5b7zUtQPyaU)
25. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtof5B2C3FdBic6zG5GvyFgkhSURmtD5jKMmsqgoHGYnc0xEZhsxmutEK1eVfqof3JnvcUGVGctmwGPY9QpkgkWCIpEKr8FTZEVsSsAo4uwm06-y4WrOehzCf1IKdqadsf2c-os-eG6Fw6)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHP-zIp7kuNZNHP_8oT900xncbC2MOfSzAVOjbvEsmUwdPFIR8XYncMOKK7ms4cekT0z2YUHYNvHrKiohL0OZl4LEaOh4f1TzxNQG4irqg2dSMtdaz6mw==)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsKeWUCHOT9OFEj4w5Pbeg0PF2beW1b9VyR-ztv5TgGolm7B5Qck8X96fumDqF5CmRFP3DVbj2NrTevUt6XBIr-tnxXFaEk3OO0L_VlGp5IAPPgSUEKH5Q_YZ9q1YXCnldb3AVqBmQd6kLPvYt5Erbp2vHmh3MVp6Man8LI2erQVamRflS8hvpK6A8GrP-JRyi83RYU3I8axiy-eszcGVg03k-42bBhgdsE9u_SKsGoAXgr0HMA8TLVlLMlJy7gGA=)
28. [wsu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRg0NfiUbJZmpbGgwvTuDlFVy8qOE6yF6qibYey8RtHymkgR2A-UlDxfZBhc2XD9xMDVhbaISeg_IPUucf_2IvZutJEz75AjYHQdPU-r5ZMuG23ucXf5oloFaQIcrOah6GVfUNRvdouJKLm8_PtUeTELrsC-487GH3ph1be4RICUFICeMKhEzmlKKp4DKMSobRiE1d9oq0xoMlgUoO54fKI8fhlHI=)
29. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVdBy354sXfQbY4RZensdHfXOjb87Gr807RBIpM3Dvfa6Wbdtl6TuVrMuzAnSDmN_HoKhDqeBqAeoeJMwJlbOw3MuaFEa2PhyuAqHdx4IUOF2DkQk3An7YlOOF0TPJrd5F8JU8qp86SpWljjznk7OW_vKrNCBNNpFH_6Az1ecn1QVIYFaL_RrqsPva0owyj8FT-vHCs0ThqDQ=)
30. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPV7SyTO9TarDCv-MJtli3r3m5c5fqEkqSIRrbL1gz3YhJhMuA5VW1dy2qWGnjAHaoQrFhBOGsAkGgN9x613y5ozX6TFBfnUg_tI6AQnHVd0BLidY2FApoMi2txhosxHmpAX-ANlaueUolw-m_v9dLUIJo2hWRw80gO1csR9pdqhbA0WYTvS792dvtSmr5rCag)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjhlzHKGv6Kp9JCUiKpf2ETc6EbkDzMv3UezI2HBfBgIlPXjvRWqMK1_FjnnjBEvYVdkUyMTuoD0781hzR5cWXR8FxVV4bRsNWEqUhd3Ri33B7LpzedbmNFejHEpSEqq9r4pzzY-KbY5KrL-OxDYwGKZz9CBYfg571d5bPC4z2v_fekNdaZ1k3Ydp-M-Di4UR34Kxske2TWQ==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiLzH-OgppTVhXt6P_NLC2ymwI-XqOKp1xBRetvRhyHwWMNmB7eAhjIMVWwO9JS5jzAu61SEMQXAoXwrFBguyi6K97KbbWJsGelPwVnCRy55YiovA4YVbDQA==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdXh4qXf4-uAHCaU_OOyrk-_W7lwprojmvyTaCzYXD38-qZNvsUN77FQYkgGGbUmCgLFEUilu5Qpr9t3J6ZaiWlCu5699vmEha1EFN_lSwrQ2PFOZwcA==)
34. [artisantg.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGufLjUt3d03CkfdAL6D5UrekChTU33uJXiQTAj51c5GPnjoDrWBRW2-x1n6a80BW-NmKE8IOJF4zQAoBj-57RuzG-cAIiKoVXvNWVorpU4GnKWtnWvjnsCNOwm018ZjL4UVkjkoNERPMHiGxg2Q7h1nwq16mTzaOc=)
35. [dl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWVaUR49nvw76kmHUjjbGTkljDsrvIXh-d1YwXFF1MUN02SymCPcNjaTzgkjJ4bgFcWz1r8-WRyMpTBxHypIK3KUwHWyNZSdKM-W2eNF2DQQhzMn9XYvfyvuEUvag3l0IgCf15Uae_6w==)
36. [equinox-tech.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8qd-CIcChZVvwWxaBy8eNBsWwZOcB39MIwqY21zSRJNVUBrH5c5J_Tp_Zo55gcVU5gBUO2mlDRqknafxWZl6_9k-xV8GOHXpc_BiifuEPhPrQ61wF4gs8HOfwtxguxkqw_cuXWZG3SrmvMB0dElTKLnM=)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3o_cOXvKFuP7QQBvzPQxTO-UiBlogTwi6nIiorWj_56X2CdSeocjKC7jTgInRLpeYUtG9CnX3EFuzWUFzT1mGHxsqmafYz0Ltx_j5b80hWFAlCVM-)


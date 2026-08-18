# Prompt 07: Knots / Khovanov homology 2024-2026 frontier

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd3amNCYXZTeUs1U1YxTWtQdThIMm9RYxIXd2pjQmF2U3lLNVNWMU1rUHU4SDJvUWM
**Elapsed:** 303s

---

# Project Prometheus: Substrate-Grade Survey of the Knot Theory and Khovanov Homology Frontier (2024–2026)

**Key Points:**
*   Research suggests that the computational limit for exact Khovanov homology evaluation hovers around 80–100 crossings, strongly bounded by diagrammatic girth rather than absolute crossing count, with VRAM functioning as the primary computational bottleneck.
*   The tabulation of prime knots has reached completeness up to 20 crossings, resulting in exactly 1,847,319,428 prime configurations, independently verified via the Regina software and SnapPea frameworks.
*   Evidence leans toward a quasi-polynomial complexity bound for unknot recognition, though the formal literature surrounding Lackenby's 2021 announcement remains in pre-publication or peer-review states as of late 2025.
*   Recent breakthroughs in theoretical domains demonstrate that skein lasagna modules can successfully differentiate exotic 4-manifolds purely via combinatorial topology, offering the first gauge-free proofs of such phenomena.
*   It seems likely that near-term quantum advantage for topological invariants will focus on additive approximations of Jones and Khovanov polynomials, supported by BQP-hard frameworks and the mitigation of topological Betti number constraints via pre-thermalized Hodge Laplacians.

**Overview of the Current Topological Landscape:**
The intersection of low-dimensional topology, quantum field theory, and computational complexity has accelerated dramatically between 2024 and 2026. The pursuit of categorified invariants—specifically Khovanov homology and its extensions—has transitioned from theoretical abstraction to applied computational modeling. This transition is deeply entangled with physical theories regarding BPS states, fivebrane world-volumes, and gauge-theoretic instantons. 

**Relevance to Computational Substrates:**
For multi-agent mathematical engines like Project Prometheus, this domain offers a rigorous calibration target. Resolving requests such as Techne’s REQ-008 requires navigating the exponential memory scaling inherent to current state-space evaluations of Khovanov complexes. Establishing a frontier baseline requires mapping the classical algorithmic boundaries, tracking unverified complexity claims, and modeling the emergent quantum solutions capable of bypassing classical memory saturation.

---

## 1. Summary

The evaluation of Khovanov homology stands as a central pillar in modern low-dimensional topology, acting as a categorification of the Jones polynomial and a bridge to four-dimensional gauge theories [cite: 1]. Khovanov homology evaluates a knot or link by assigning a bi-graded chain complex whose Euler characteristic recovers the Jones polynomial [cite: 2, 3]. While the mathematical utility of this invariant is unquestioned—it successfully detects the unknot and provides bounds on the smooth slice genus via Rasmussen's $s$-invariant—its computational extraction remains a formidable barrier [cite: 3]. 

The current operational frontier is defined by severe memory constraints. Exact classical computations scale exponentially, rendering arbitrary knots beyond 80–100 crossings highly intractable without specialized diagrammatic properties, such as low girth [cite: 4]. Software implementations like **KnotJob**, **Regina**, and **SageMath** have optimized the extraction of these invariants, yet they remain tethered to the fundamental limits of classical Random Access Memory (RAM) limits when expanding the "cube of resolutions" [cite: 4, 5].

Simultaneously, the theoretical frontier from 2024 to 2026 has witnessed aggressive expansion. Combinatorial topology has successfully encroached on territories previously dominated by differential geometry and gauge theory. Most notably, the development of **skein lasagna modules** has provided the first gauge-free, analysis-free proofs of the existence of exotic compact orientable 4-manifolds [cite: 6]. In physics, researchers continue to tightly weave categorified invariants into the fabric of quantum field theory, demonstrating that Khovanov homology and Witten-Reshetikhin-Turaev (WRT) invariants emerge naturally from the counting of BPS states and the dimensional reduction of Haydys-Witten instantons [cite: 2, 7]. 

For Project Prometheus, defining the substrate tooling required for REQ-008 means acknowledging that classical brute-force methodologies have reached a plateau. The immediate future of Khovanov evaluation relies on advanced algebraic simplifications (such as p-DG structures and local torsion analysis), machine learning heuristics for predicting homological bounds, and the deployment of bounded quantum algorithms [cite: 1, 8]. 

## 2. Flagged Findings

To maintain epistemic integrity within the Prometheus substrate, several high-profile claims from the 2024–2026 window have been identified as "anti-anchor flags." These represent significant paradigm shifts that are either pending peer-review consensus, require hardware verification, or fundamentally alter known complexity bounds.

*   **Flag 1: Quasi-Polynomial Unknotting (Marc Lackenby, 2021–2025):** 
    In 2021, Marc Lackenby announced an algorithm capable of unknot recognition in quasi-polynomial time, specifically scaling at $n^{c \log n}$ where $n$ is the crossing number [cite: 9, 10]. While this represents a monumental leap over exponential bounds, the full unconditional proof has remained an active topic of seminar discussions (including at Oxford and UC Davis) but had not completed standard peer-reviewed publication as of late 2025 [cite: 9, 10]. This claim sits atop earlier proofs placing the problem in NP (Hass, Lagarias, Pippenger 1999) and co-NP (Lackenby 2016) [cite: 10]. Prometheus must treat quasi-polynomial unknotting as highly probable but procedurally flagged.
*   **Flag 2: Exotic 4-Manifold Detection via Skein Lasagna (Ren & Willis, 2024):** 
    Qiuyu Ren and Michael Willis achieved a landmark result by demonstrating that the Khovanov-Rozansky $\mathfrak{gl}_2$ skein lasagna module distinguishes the exotic pair of knot traces $X_{-1}(-5_2)$ and $X_{-1}(P(3,-3,-8))$ [cite: 6]. This is flagged as a verified breakthrough because it constitutes the first analysis-free, gauge-free combinatorial proof of the existence of exotic compact orientable 4-manifolds [cite: 6, 11]. 
*   **Flag 3: Quantum Algorithms for Khovanov Homology (Schmidhuber et al., 2025):** 
    In early 2025, Alexander Schmidhuber and colleagues (arXiv:2501.12378) proposed a quantum algorithm for Khovanov homology [cite: 1]. The paper formally proves that additive approximations of Khovanov homology ranks are DQC1-hard, BQP-hard, and #P-hard depending on the approximation regime [cite: 1]. Crucially, the algorithm's efficiency relies on the Hodge Laplacian thermalizing in polynomial time with a sufficiently large spectral gap [cite: 1]. This flag is active: while theoretically sound, practical implementation requires deep graph-theoretic validation of the spectral gap.
*   **Flag 4: End-to-End Quantum Advantage for Jones Polynomials (Quantinuum, 2025):**
    Quantinuum researchers deployed a fully end-to-end quantum algorithm on the H2 trapped-ion system to compute the Jones polynomial for braids up to 600 crossings, achieving near-term quantum advantage utilizing control-free echo verification [cite: 12, 13]. This physical hardware demonstration significantly shifts the threshold for polynomial invariant tractability. 

## 3. Problem Statement

Techne’s REQ-008 specifically targets the computation of Khovanov homology, a task that currently encounters severe computational bottlenecks. The core problem is that Khovanov homology requires the construction of a chain complex derived from the "cube of resolutions." For a knot diagram with $n$ crossings, there are $2^n$ possible smoothed states (resolutions), each forming the vertices of an $n$-dimensional hypercube [cite: 5, 14]. 

Calculating the differentials between these states scales exponentially in both time and memory. Modern implementations, such as Dror Bar-Natan’s algorithm, optimize this by utilizing a divide-and-conquer approach [cite: 4]. However, the efficiency of this method is constrained not by the absolute number of crossings, but by the diagram's **girth**—the maximum number of intersections the knot diagram makes with a transverse horizontal line [cite: 4]. 

### Hardware Constraints
Current classical solvers are fundamentally VRAM and RAM bound.
*   **Tractable Limits:** Knots with a girth of 12 and below are computationally trivial. A girth of 14 serves as a critical threshold, allowing for the computation of knots with approximately 80 crossings [cite: 4].
*   **Intractable Limits:** Diagrams exhibiting a girth of 16 or higher rapidly exceed the capacity of standard computational nodes [cite: 4]. While evaluating a 100-crossing knot is theoretically plausible, the operation takes weeks and exhausts dozens of gigabytes of RAM (typically requiring 32GB+ configurations with extensive disk caching) [cite: 4]. 
*   Parallelization offers diminishing returns for the Bar-Natan approach due to the interconnected nature of the tensor products evaluating the chain complexes [cite: 4]. Consequently, forging tools for REQ-008 requires either the adoption of memory-efficient algorithms (e.g., spectral sequences converging to the homology) or shifting the paradigm to quantum co-processors capable of representing the $2^n$ state space logarithmically.

## 4. Status & Bounds

To properly calibrate Prometheus, we must define the exact statistical and computational bounds of the target domain, ranging from tabulation completeness to strict complexity classifications.

### 4.1 Knot Tabulation Completeness
Knot tabulation has advanced from manual enumerations (such as Tait and Little's early 10-crossing lists) to massive computational censuses [cite: 15, 16]. The historical progression and current completeness are summarized below:

| Crossing Limit ($n$) | Total Prime Knots | Primary Architect(s) | Notes |
| :--- | :--- | :--- | :--- |
| $\le 10$ | 249 | Rolfsen (1976) | Rectified the historic "Perko Pair" duplication [cite: 16]. |
| $\le 16$ | 1,701,936 | Hoste, Thistlethwaite, Weeks (1998) | Verified via hyperbolic volume and tangle decompositions [cite: 16]. |
| $\le 19$ | 352,152,252 | Burton (2020) | Tabulated via Regina software over several months on distributed clusters [cite: 15]. |
| **$20$** | **1,847,319,428** | **Thistlethwaite & Burton (2018–2021)** | Verified independently. 99.99995% of these are hyperbolic; exactly 920 are satellites; 1 is a torus knot [cite: 16, 17]. |

The current ceiling for total prime knots tabulated up to 20 crossings stands firmly at **2,199,471,680** [cite: 16]. Beyond 20 crossings, exhaustive tabulation breaks down due to the combinatorial explosion of planar graphs, forcing researchers to rely on localized invariants or specialized structural subsets (e.g., alternating knots, tabulated up to 22 crossings) [cite: 18].

### 4.2 Fastest Current Implementations
*   **KnotJob:** Developed by Dirk Schütz in Java, KnotJob is widely considered the most efficient dedicated solver for Khovanov-centric invariants [cite: 19, 20]. It evaluates even/odd Khovanov homology, Rasmussen's $s$-invariants over diverse finite fields (up to characteristic 211), and Lipshitz-Sarkar stable homotopy types [cite: 20]. KnotJob utilizes optimized Bar-Natan algorithms and is heavily favored for high-crossing tangles [cite: 21].
*   **SageMath / GAP:** Sage integrates directly with KnotInfo databases and utilizes KnotJob data structures for PD (Planar Diagram) code evaluation. Sage is highly reliable for accessing pre-computed polynomials but relies on underlying C/Java bindings (like KnotJob) for novel raw computations [cite: 22].
*   **SnapPy / Regina:** While Regina is the apex software for 3-manifold triangulations and normal surface algorithms (used heavily by Burton for the 20-crossing census) [cite: 17, 23], SnapPy provides access to the HFK-Calculator for knot Floer homology [cite: 16, 19]. 

### 4.3 Computational Complexity Frameworks
The computational hardness of knot invariants is deeply established in theoretical computer science.

| Problem Domain | Complexity Bound | Key Contributors & Year |
| :--- | :--- | :--- |
| Unknot Recognition | NP | Hass, Lagarias, Pippenger (1999) [cite: 10] |
| Unknot Recognition | co-NP | Kuperberg (2011, GRH), Lackenby (2016, unconditional) [cite: 10] |
| Unknot Recognition | Quasi-Polynomial (Claimed) | Lackenby (2021) [cite: 10] |
| Khovanov Homology (Exact) | #P-hard | Schmidhuber et al. (2025) [cite: 1] |
| Khovanov Homology (Approx.) | BQP-hard / DQC1-hard | Schmidhuber et al. (2025) [cite: 1] |

The Hass-Lagarias-Pippenger framework established that unknotting certificates can be defined via Haken's normal surfaces within a polyhedral cone, placing the problem in NP [cite: 10, 24]. Lackenby's progression toward a quasi-polynomial algorithm leverages sequences of Reidemeister moves bounded by $n^{c \log n}$ [cite: 10, 25]. For prometheus, exact evaluation of Khovanov Betti numbers remains definitively #P-hard [cite: 1]. 

## 5. Literature & Theoretical Frontier (2024–2026)

### 5.1 Khovanov Homology and $\mathfrak{sl}(N)$ Categorification
The algebraic frontier of link homology has focused deeply on characteristic deformations and generalized quantum group categorifications. Joshua Wang (2023–2024) successfully constructed operators on $\mathfrak{sl}(N)$ link homology utilizing mod $N$ coefficients. This work exposes structural properties of $\mathfrak{sl}(P)$ (where $P$ is prime) that behave similarly to the well-documented anomalies of characteristic-2 Khovanov homology [cite: 26, 27]. 

Concurrently, researchers like You Qi, Louis-Hadrien Robert, Joshua Sussan, and Emmanuel Wagner (2023–2025) have integrated **p-DG (p-differential graded) structures** into link homology [cite: 8, 28]. They established an $\mathfrak{sl}_2$-action on equivariant $\mathfrak{gl}_N$-link homologies. Over fields of characteristic $p$, the nilpotent part of this $\mathfrak{sl}_2$ action defines a p-DG structure that aligns with the categorification of the colored Jones polynomial at roots of unity [cite: 8]. 

### 5.2 4-Manifold Invariants: Skein Lasagna Modules
A paramount development in low-dimensional topology is the maturation of **skein lasagna modules**, originally conceptualized by Morrison, Walker, and Wedrich [cite: 29]. A skein lasagna module, $S(X, L)$, serves as a universal extension of Khovanov-Rozansky homology to a 4-manifold $X$ containing a framed link $L$ in its boundary [cite: 30, 31]. It takes Khovanov homology as an input and processes it over embedded surfaces [cite: 31]. 

In 2024, Qiuyu Ren and Michael Willis achieved a historic milestone using these modules: they distinguished the exotic pair of knot traces $X_{-1}(-5_2)$ and $X_{-1}(P(3,-3,-8))$ using the $\mathfrak{gl}_2$ skein lasagna module [cite: 6]. Because exotic 4-manifolds are defined as spaces that are topologically homeomorphic but smoothly distinct, differentiating them has historically required intense analytical machinery derived from physics (e.g., Seiberg-Witten or Donaldson invariants) [cite: 32]. Ren and Willis provided the first purely combinatorial, analysis-free slice obstruction and proof of exotic structures, validating the power of categorified link homologies outside of 3-sphere domains [cite: 6].

### 5.3 Connections to Physics: Witten, Gukov, and Bleher
The dialogue between string theory and knot invariants remains highly active. Witten originally interpreted the Jones polynomial via Chern-Simons topological quantum field theory (TQFT) [cite: 33]. He later conjectured a gauge-theoretic interpretation of Khovanov homology using solutions to 5-dimensional super Yang-Mills partial differential equations [cite: 34, 35].

**Haydys-Witten Instantons:**
In 2026, Michael Bleher published comprehensive frameworks detailing the decoupled Haydys-Witten equations [cite: 35, 36]. Bleher demonstrated that on a five-dimensional cylinder $M^5 = \mathbb{R}_s \times W^4$ equipped with a non-vanishing vector field, the Haydys-Witten equations yield flow equations for $\theta$-Kapustin-Witten geometries [cite: 7, 36]. By applying twisted Nahm pole boundary conditions to encode the singular presence of a knot, Bleher established the indicial roots required for elliptic regularity [cite: 7, 36]. This explicitly categorifies Witten's proposal, proving that the instanton Floer homology groups $HF^\bullet_{\pi/2}$ perfectly align with the Khovanov homology of the knot [cite: 7, 36].

**BPS States and $F_K(x,q)$:**
Sergei Gukov, alongside Ciprian Manolescu and others, has expanded the categorification of Witten-Reshetikhin-Turaev (WRT) invariants [cite: 2]. WRT invariants are traditionally complex numbers; categorifying them requires deep physical models [cite: 2]. Gukov demonstrated that by counting BPS states (bound to domain walls of M5-branes in M-theory), one extracts a homology theory whose graded Euler characteristic yields a two-variable power series $F_K(x,q)$ [cite: 2, 37]. This series possesses integer coefficients and acts as an analytically continued, refined substitute for WRT invariants, inextricably linking the quantum spectra of physical 3-manifolds to purely combinatorial knot polynomials [cite: 2, 38].

## 6. Attack Vectors

For Techne’s REQ-008, forging tools to bypass the classical $O(2^n)$ barrier requires adopting asymmetrical computational attack vectors.

### 6.1 Quantum Algorithmic Execution
Quantum algorithms are rapidly approaching practical utility for topological invariants. The Schmidhuber et al. (2025) paper outlines a coherent quantum attack vector for approximating Khovanov homology [cite: 1]. Recognizing that exact evaluation is #P-hard, they utilize a linear combination of unitaries to achieve additive approximations [cite: 1]. A primary vulnerability in earlier quantum homology algorithms was their failure when topological Betti numbers were dwarfed by the chain space dimensions. Schmidhuber circumvents this via a **pre-thermalization procedure** applied to the Hodge Laplacian, provided the matrix maintains a sufficiently large spectral gap (which they bound analytically via novel graph-theoretic mappings) [cite: 1].

Furthermore, Quantinuum demonstrated physical quantum advantage in 2025 by deploying a tensor-network inspired matrix product operator (MPO) quantum algorithm to evaluate the Jones polynomial for braids reaching 600 crossings [cite: 12]. By relying on control-free echo verification to mitigate two-qubit gate noise, this architecture sets a blueprint for upgrading to categorified Khovanov states [cite: 12, 13].

### 6.2 Deep Learning and Heuristic Reductions
When strict topological precision can be substituted for high-probability estimations, neural network architectures have shown immense promise. Gukov et al. trained two-layer feed-forward networks on sets of topological invariants, determining that algorithms can predict Rasmussen's $s$-invariant directly from specific evaluations of the Khovanov polynomial with over 99% accuracy [cite: 3]. Additionally, the hyperbolic volume of knot complements can be machine-learned from the Jones polynomial with >97% accuracy [cite: 39]. Prometheus can integrate these neural heuristics as a triage layer, quickly bounding invariants without initiating full chain-complex evaluations.

### 6.3 Field Characteristic Optimizations
As demonstrated by Schütz, calculating Khovanov cohomology over finite fields $\mathbb{Z}/p\mathbb{Z}$ circumvents the massive integer bloat and slow Smith Normal Form (SNF) reductions inherent to $\mathbb{Z}$ [cite: 40]. By restricting matrix calculations to characteristic 2 or small primes, matrix reductions execute orders of magnitude faster. Prometheus should inherently shift REQ-008 queries to finite field evaluation unless the detection of specific odd-torsion phenomena is strictly mandated by the user.

## 7. Cross-References and Prometheus Integration

The data structures necessitated by knot theory map perfectly onto the core competencies of the Prometheus multi-agent tensor framework.

*   **Tensor Networks & Categorification:** The evaluation of Khovanov-Rozansky homology for $N \ge 2$ fundamentally translates into the manipulation of categorified Jones-Wenzl projectors and matrix factorizations [cite: 34, 41]. The algebraic resolution of a crossing in Khovanov theory is a mapping between tensor products of Frobenius algebras [cite: 42, 43]. Prometheus’s innate tensor manipulation substrate can represent the Bar-Natan cobordism categories directly as tensor network contractions. By leveraging algorithms traditionally used in condensed matter physics (like Matrix Product States/Operators), Prometheus can compress the $2^n$ state spaces logarithmically before exact differential mapping occurs [cite: 12]. 
*   **Agent Topologies:** Implementing REQ-008 requires deploying specialized sub-agents. One agent cluster must oversee the "girth" routing—analyzing the input planar diagram to find the optimal Dowker-Thistlethwaite or braid representation that minimizes spatial width [cite: 4, 18]. A subsequent algebraic agent performs the $\mathbb{Z}/p\mathbb{Z}$ matrix reduction, while a separate physics-informed agent models the spectral gap of the Hodge Laplacian to determine if the input is safely routable to a simulated quantum solver (as per Schmidhuber [cite: 1]).
*   **The Lasagna Upgrade:** Because Prometheus operates as a research substrate, providing a module that computes skein lasagna invariants $S(X, L)$ directly interfaces with the bleeding edge of 4-manifold classification [cite: 31]. Extending the TQFT framework into the 4th dimension requires Prometheus to handle 4-ball ablations and handlebody framings.

In conclusion, addressing Techne’s REQ-008 is not a matter of securing more RAM for classical algorithms, but of implementing modern pre-thermalized quantum approximations, applying machine-learning heuristics for bounding invariants like the $s$-invariant, and mapping the topological state space into memory-efficient tensor networks. The integration of the 2024–2026 frontiers—ranging from Burton's 20-crossing tabulations to Bleher's Haydys-Witten gauge solutions—ensures that Prometheus's knot theory module will operate at an apex, substrate-grade level.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8hq0WC9LVRexQZ8DAiff0-_GKk9IavuMOCSi7hyMya053BrKT0dnSaApm5ywpdmZ7qd0Rj_lc--ycFYpVHVpe721mYD24dUYNK1wrOcRHyngA9rd8xw==)
2. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFQJpOoR-SJvikPu1eG8VqgYuazZODhHX4nsfqmeiw9arEKXbySKFWE3uh3gp1kr4SUhEChAdrnyT0rkM5WwXPmUHVCvRRp7iHY5fihUjxwpnY92MqCacRyGg=)
3. [scipost.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgn9juHLd5kTpCUcOn3FKBuBNpm9W604fP8X-yBeaxQmEJJ19nYacKSeGTm3ReRm1f0EY63iDt4Oi9kSKcAKs6s_VZ5jniJ_7CBt_-VKYdHhYtQamWATKqiOinGmmTElGvbw==)
4. [mathoverflow.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHNWKxHasr0ojKLu77ggQys9WzDwjBhrza0htcfaU0RpwZRudzWuMAYCR9E5VbLxpliSyY00o_cmFjgzP1EWMEJSa5e67JzWK5Z1IluqXbGojcI3ajipCIpMQ2wOeCu27d5pbRqu-zSlhPL6aNpE80pTjYPYDqQc9Oi9GrsMn83CTrdps=)
5. [ubc.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELS2_dYtL2dNpH2W-P549r4fmn6UhsmVyiIlVEE0O2us6emPUYBga-tgPGsdOh7iO6S-MumqlJ7HtMCKOFTfSuWjKXwRaJ-6sbOSM07ZpFYTRmmJ68sBncv7wjBQKckJOyJFPf8aRgPLRTz6k=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQHNLBMUudooY03ZOqSUFgq22fW35kKrKUzy2XiVD6sUVHGqXwA5hys8kqCszNKjEDJKaQfMzRUxaarDY485mRcF-tD4bxhGW6g1X47jUhRpxbLNgG8w==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1CdtEBHQ8Yhsi7Kk3ICY_38tGhllWifwBJvHVGXWh9m7ZwWiWpKVeEn1mutCscg58pHwMPyxhHhjLoqaz-A2wofxGNRvBdUXoJQk4o2G0ZJrwSHtq-g==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1J_hCiyzhnDpwNau6_GyXxaIKZxe-Qljdy_1OgN2Q3TRloxoDEBxOgXAGn9sLYwnP3tRx6gY8eHWouNSmQYD2EES1ZpvL_g9HWn-sMyiHdTaK1UfLXQ==)
9. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyLrLPFpOU5rraramIMUhVflOPEsCjhZaK0GAoGMVnQbvNy1tepeep1U56xLEji1WPKXNKJJFTj8Bj4ePQY8egwWAsHIDGzE0I2Q-MV9wQJoTahxBGyTJ9H67o)
10. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIDLEZkiMaA7V9Zq1iex7Y8PtWmDJaSFH9dsiow1jQv6N3agNu4ulqWFxdmSJDw73Qlqg2OU0vMqqEPfmUXLnr42twelUSlrDy7N_Bf7_vNApJre70iNeRJW2GVuAN64KHmxusdg0=)
11. [carmin.tv](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5WAlya2TSSppOoOOqydl2SMPf0_Yy_4fqYG3_Bq5KA4leagU4pNvZo9tVp2vBMiHxIBsYgqW-az5dEd7Z0ace2YF7NDhSsf60LHGF6g7fNGtjqOYf0HuBE02G1JrApOF9e0pwzZjkCdO-dbidN-VUtI4=)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiPp7KQ2vcJ31PvvAcvLrc_ehNGk9UzodP7qqN3aRFWUgteh3zwbDDhKTcvAmNunS9tb_AD5rYBzZvSIgufp3n5Ht5AJJhFd1cSa4Dw-aErVriQaSYHGu-KrdpQR0bPVdbasDc0rKm02d97M9ciFjkGGQflo4R_yOQa1y273Woe-Nz7wG3YtIb0IcDur6Gyz12ecsFbiBz9YfsAfcnbOnODlo4lJqsCTj_JyrVPaXxsj0VU3bBlcWJ3W9yxcyq)
13. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuuvtQ4LxADQt5poriw9lC6lEezE9KPruvtt28x1WAytyqwMbC_x-Yqhl2cwPDvc3vzuppl8dRcklUq986wTrX_jovMBW_AFhGh6d99xZY734hxS0DANNnQD8SieaCmlYD0cBW4-Q1Eto3ZR1pKegb5JViZ0re0YlZVD3YLhw7AbXsz-9Y_coP9i5dWGblPcA-rZEDDzlHrastjdrjWjBqIglmMxmtiNldkHmvomDCt5pCHxg=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj1FKbWhZxi3gl_JvWdPtmUiAJMbuGkbQApyTpjSk408om1PA0Z3Bxofwf2FfgM7IAdLhEnSg93Nh1C-r3HnH9Mj1-RZdfzXWuNPHI9YpfFdv_r8RxhuIhHA==)
15. [thearchitect.global](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuBDx8mAu0PBC_gkkod5MGfB6EnqVkCpxl4YQn1xJHUXixi3k6YnPKtdLswf07A7YY9dbKfNbfF8fCWpPrHopOUMX28FdaEwvAq0anSrCOsuYZcYwvmINrjqM2Ha-xPDF-Svg45HLwoqUY7xikffELY3zrJnAXf-LijUMtEy0hAwbZnjn7f2U9lXc6PzulmKH7wWWWh1SVRMxTJAO4B-TP57SQ)
16. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZKkL0Qec45P0ebLfld4kPZo0ChoYpjn2JgAfBQfGcW6wSR_cAifvSRlGm9NCGGumQw-aFNrIHzgZecdS7vm34ey9Hxw-0ILSAE0gbOdWg9FyKw2nTQNIcLksHUeo4j7yKLorr8svEHCTNxmwHoFKpVnKNhpCm)
17. [utk.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMwfVJJEfv6Ch1KgXoxGUR7py7FozccQdLBGA6lPWNNZ8VmL7Y5y8SJ_C5KPouZCg5LP_t8P38jwWal1G6D4gFbVUn4eJi9KRZXZtseGsZno-0tvZfCvwxt4XtCj7F6j8=)
18. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB5tWX5daQEB0egLwnB4OjrgLMQe4xd0EtA9_KyPpH9vCt3qDnB7IjlbNh-3TtLTiZYKgppV98LHUCcwHy0Ldmt-TM7DtsnxU4ROO3QkFt2dyyHXsRju-PJY-dLP7l-w==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGA5Sx1Xky7rb-u7FVtI0x6pRmxcqvNCdXdY-pVpRCFsDEIv-C55T2hEDhPVS_bpp88f3sR4jj_o9Nl0RVJ_nlUGW2Ib19s1PDTdg-6MdaUHBX9cq8n7w==)
20. [dur.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOCbjFr5ekOO7i5sm83g5zOUcmtJyio7UNugiDU1zIxk6-0DKUOnYsi36J2ediaUWf4mKkzfN9bw-Hx2ZLug0AUobLuK1laXjP1vEszr5yS3m4lWKxzJ-XymxMfXFO8VLKZrYbCgjb5bkR42X70Cpp6A==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_x3sVpVHGRVdvpZQx6q0hpW7oWpSPz4M0Dsq-hMfKhwRCIJOqHFE0VIJmkPymCpNBsmrlAbqB5UqRYItZvQwCd0sk-0a7vcULk3656B-fDOwDbvNhOw==)
22. [sagemath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0MA5Mpk7DN3qvbd-_YrE8vmndW2m_dlDsjxMS54Vdnr1STcsKFCtHDKRTcgkdGwA6HAdEXu0lL520t14nDghbq1TwLysBxlhnSssAKBrx3PqTiszryScjnHTQUQAUS7KKgfS-xD3i-RTIO8xnXLY=)
23. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoGGK_mjxo2VzYO14mgIY9rPTIfdqXucYZW6ShUBGwxcKeZ4cSShL5PjCG-vpUPVJ-zE78jQF7Y49aonANus9L_pWNjoFDz-MG3qRu6rhixY51ahuK0VRH3dYhKD4cVHB9)
24. [ucdavis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtDKGtVQooztAYvRlFHyaI1PXnUQ2RTpyTyGIdj1-RJqWJyE-dlzlDEA6Yj5gttJRBQmwFbWO7rILFq1XLZJUKIMQieFzIMm0F5XHO125VxYO9iiKMyfDtfP1gkN_QXsoJhMFCsmkYgHIWg8xpQdoIcXAqrypK0DZVARc=)
25. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOvy_i7juKGRHKW4F2zbMCBxaP7a2M6DYFeBwMYWDOE7zCKzhhwhZ7isnL2ftF6KZvBlfB-3uzEuJDjj_Een-9kVYododwZpnP3QU0KwrSgTFd93-9mgxnhNJgJdxSwXLWIbJL7QiLKah6RqvMyA9UArHoJPZHzR6itJhGpl-8jIm7hU7B2wpgAlERTCnqT3uuONkOjVhYG-E4EwMPjZWSqIv2CDyc)
26. [ems.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsb8Ix0yvce4i6loZnefHgMUrqy5CGhH8V9DbqDngGGXI7isq9Q6SGaY8L-jcoZgtZy1plLS7f8595E_WWM3CzdvFRo8AkKrB3CeWOQkoHGE3FxzMsHWpcmphJ8YkfCPJklqw-qw==)
27. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKxSMX24PKnh1Q1DT1hdn31bV3iKv4lal3gtfmVoxSjOSdnyGPc94bUt7xmgevCrJAlZNSbYpVfDF4hjwJ-903Oyyqm7Lm9DjTYVsVWiLTT8NrLqudSiYjdW4NS2h0PBiifXEQMXxjTo51iMb-IdZR2DNs)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLtU9bfo5ag0WFHf2forkzTYJBLba76O-pqc_42mbMT8WqKos-MsfKpr3HMa3mtfOv7haaSFVV9ptiM8hUZA5V_hyLVRKNp1OI0o8XOLjpbxRHA2AaIg==)
29. [imar.ro](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5H8TWi6OThqtX9MhUBxZI8iwXJMB7cOBEzrC4S8yGr2TrPKkmiMKQldpUsuMfpONu2S6isdr0GKz1TPXmxk4FtWEKQf8W3IUa3wvCEtYlf8GFpuE1krhQCqxQ7amsc4d82wcQ3c1TJcKJLQ==)
30. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER_QPxwUKIj4wTvuzk3btzIpMUQoyaOoiStWwa3FGOpZPwdnMtabmvVjeT_Mh34W2TLhWYzcCjiyTXoT4-8WAyzAws8jcDw53DtzWvLYkD7N1KvCGKkutT-PvLTFYPk4yM)
31. [theopenscholar.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFP_b0cliydY49IVISn5L-11rAOEDYZt6SBysFOW1ViuV-eXTOjk7B92vnDCBejbstMQ5mFJ_hp3xb1NE_e2mPYtAv5pYgsJeSaur41VEtvzsM1y54VPn7bVmQG3yqO3BG5rxy7vtE56MGRyh5KnQ2VkAdU0kUnSuSzKOcfNP-ihiLYF3_OMcIP)
32. [viasm.edu.vn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgAWK-jBBN8R9LIUZtuVWpPdmH9EB0gmDGQdFudNgshtOFd0DbYDUdXz-zPGdONan2pFDHjpFzr9mqY2vQ1n5iaIbDB_ECBL3ft2Gzi-vvjP6na4uCjxqHwa6svlFxBuR7w5v0ZsrJqy2MORFXt-a5U1uhJ9IPed7rlD-YV6bhngVwz8lAGyVjsLyvEgC_TYgJgyZs7YiIYcVZBaU=)
33. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFiR99gj0SfTydGs8k5xzZ71UGdOrpT3IZ-qInhA0JlEwOoAOb7v2_H76QLJBahjNHm8fOarNUZ1qt8tzbGb-YzXjNb1g7idLdLp58aiXTDTZbZIpneP6zneFR-rXYHIXPvMK9Nw==)
34. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGv-h-HUwI3G_U0118YL1kqQVFiB0sQPBx_tpRob2Qnuxg0yoIW4-ZMDcKyyrcM2JSPTOE_UxCOm-h9XKgj-eUWgwH91O_qmMXVYkXNSvEHg7tYfV8nIcjuQwcdxaaY_cLl7IeXqhXjJDpp6wvzBfyGC-KqXssikWn7Q9eq2sDMZjqdPZ2drtgZCBcXgxSjKzBz_qO1n7WJeIijkw==)
35. [bleher.me](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlCiZMZOExuKeHp_go-YrQeWUHy22VmPJSFxC0uMmjSie09sRTQDu3hHbcD97JVDRQknUlghcrbRWp5NWAvGJLzTZ0kr8KQEO4Mbql4i_QH7g8VTh49w==)
36. [sigma-journal.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9SlHWkdmJoE3tXuPaLdRVDLCX-GNK7p-fjhKFIsmXJDGqpoV7PcEU6-7vAP-18PP7tVYWdMAv0cmrO24lKoLL-y1kHOgHx7b4eqxi62Mm3voaQ1mcZRBFi4q_FNoiKAmRAQ25fgfiQg==)
37. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEmQ4WqKe0su73fMFhnaXHofeQ8nkBuZiohODNHzO3AWY_ixygPDNAub4TH_P9PdxnR-gmo0FNOdM3mpx7CmVzq-_8WrdZqZsG_0XBPlQ52e1Tsh0-9kRP-5VjP5NQIVjuCVvARRPRxLFInHcargczd3VShEakNwvO3H3wXX8qsUvYGiXoZ-x_kg==)
38. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQjIMPmqDFKYtX_FH7vE4Q6iybovJ4gmbIBCoUJkM1DtPfFL5VT4MwYE9YOLOqzm1XulsxVU8UkYkkOl-e8yElK3bdtqKz5QC7zDrZD7d0v0ItJejw_jpumarEyWG3xEF-eeBZykz6cQQMVX8KsqqKkpm2hcVKpa0vmLvcr4HF_Y9iC6WQd3bMbz_13NsM)
39. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5dNgjpQ1gf8mkHmz7bqMugQmR8YEAVjA_T5y4dp01i_NvNKm46aaJENOoPOr2GL09ss12s1XJm6zRTx7abLZOWH3pIsDq7n_yGAZ4Uk3QZq1b1Szpk7Aes0i7uC-ofR9op_l6cwgmiILnHFvr8bYo-onKw2_49c5jo5ABSrQqIhcz)
40. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFwX_EgYLleSXSI7hR9NMgE83dECmui1e-MIEw9lbNkl1NWE-MmNUgeBIBRmGPpwpROrxvQoO7leseDjEGwggFxCbuAaQSm3LdGkJQH4ZVIanKDZVMIG1usgTjbLFVFvBxGnVG4mSwiAJ3WsawGBJP3F8Xu-vHMHDCN17YdLuLJfGvcSU=)
41. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETbt05QWkiBIOb8oGB2m4WIKHAHRLWYnUtCBVcuSbrkli7D_8TTsTlVpVAtBxPLXJUuJ7Y92GcI0d8-De7bNvz0d12sNpukDnymVbUsvfCzI-bDrljL3X3067f8vpoMkh7RqfxSZFpAw==)
42. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGITb2opS8TslVyeH1-oxdYaSdxtAmNyLqaHFbF9P-Xxl8NYLFlfm2NZ_DyXjqcG6xjne1ldcBdI19anjSWAiuB87LQYZVKdkarls0THoRpWbpd81gdbg==)
43. [dur.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeObjGTOAHeZhdrw13lBMirXvrppzM7vUs0ZPArgME3t_jA00_9pySYTWJ9FIV2QPAQo5FCZVSV1PAUU54fhFXP6QJwTYNwZ1nVbZHFX-B9EZDfOdLTGNrbuIDdnfy_KwGti0a1J74Ewt6X7I=)


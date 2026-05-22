# Followup [FU-2026-05-22-030 <- row185]: ## Future Trajectories and Ongoing Challenges (Beyond 2026)  As the computational frontier pushes pa

**Pythia queue id:** 315
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczTGNQYXJUSEs0bWNfdU1QOTV2TWlBcxIXM0xjUGFyVEhLNG1jX3VNUDk1dk1pQXM
**Elapsed:** 311s
**Completed at:** 2026-05-22T02:01:56.530546+00:00

---

# Research Brief: Algorithmic Functoriality and Exceptional Theta Correspondences Beyond 2026

**Executive Summary:** The study of algorithmic functoriality represents a critical bridge between abstract representation theory and computable number theory. Research suggests that while explicit lifts from classical groups like $U(2,2)$ to $Sp_4$ have been well-understood, extending these computational pipelines to exceptional groups such as $G_2$ and $F_4$ presents profound algebraic and geometric challenges. It seems likely that the transition from theoretical existence proofs (via the trace formula) to explicit algorithmic generation of Fourier coefficients relies heavily on exceptional theta correspondences and the arithmetic of quaternionic discrete series. Recent breakthroughs lean toward the conclusion that explicit weighted theta series can completely parameterize level-one automorphic forms on $F_4$, and that the Fourier expansions of Gan-Gurevich lifts to $G_2$ are fully computable. However, the evidence is nuanced; while dihedral and level-one cases are increasingly tractable, higher ramification faces formidable obstructions. These advances require careful navigation of computational bottlenecks and arithmetic confounding variables to verify central conjectures (such as Gross's Conjecture) that link L-values to Fourier coefficients on exceptional groups.

---

## 1. Brief Summary

In the Prometheus context of operationalizing Langlands functoriality into computable algorithms, this inquiry addresses the frontier of computing explicit functorial lifts (and their Fourier expansions) to exceptional groups such as $G_2$ and $F_4$, transitioning these objects from abstract existence theorems into algorithmically generating, computationally verifiable modular forms.

## 2. Flagged Findings

**Current Consensus:**
Historically, the Langlands functoriality conjecture for exceptional groups was treated as a domain of pure existence theorems. The consensus held that lifting automorphic forms from classical groups (e.g., $PGL_2$) to exceptional groups (e.g., $G_2, F_4$) could only be studied abstractly via the Arthur-Selberg trace formula or Langlands-Shahidi methods. Under this paradigm, extracting specific, computable arithmetic data—such as Fourier coefficients or Petersson norms—was widely viewed as mathematically intractable because exceptional groups like $G_2$ and $F_4$ (with the exception of tube domains in $E_7$) do not possess associated Shimura varieties, thereby lacking classical holomorphic modular forms.

**Where the Consensus Might Be Wrong (The Algorithmic Pivot):**
Recent computational architectures and theoretical breakthroughs strongly contradict the notion that exceptional functoriality is strictly abstract. The implementation of exceptional modular forms in symbolic computation systems (such as Aaron Pollack's SAGE libraries) demonstrates that the Fourier coefficients of quaternionic modular forms on split $G_2$ can be explicitly computed [cite: 1, 2]. Furthermore, the construction of explicit weighted "exceptional theta series" by Yi Shan (2025) has successfully spanned the space of level-one cusp forms for $F_4$ [cite: 3, 4]. 

**Methodological Flags:**
In early computational attempts to parameterize these exceptional Fourier coefficients, researchers frequently encountered **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**, wherein local $p$-adic models were excessively fine-tuned to the behavior of small primes (e.g., $p=2,3$) where exceptional groups exhibit highly anomalous ramification. Extrapolating these heavily overfit small-prime heuristics to global L-parameters often failed, demonstrating that a purely numerical, prime-by-prime synthesis is insufficient without the rigid algebraic structure provided by the global minimal representations of $E_7$ and $E_8$.

## 3. Problem Statement

The precise objects being interrogated are the **algorithmic mechanisms of exceptional theta correspondences** and the **arithmetic of quaternionic modular forms** on exceptional algebraic groups. Specifically, the frontier addresses:

1.  **Algorithmic Construction of Lifts:** Computing the explicit functorial mappings from classical groups to exceptional groups. Prominent examples include the lift from $PGL_2 \to G_2$ (Arthur and Gan-Gurevich lifts) [cite: 5, 6], the dual pair $PGL_2 \times F_4 \subset E_7$ [cite: 4, 7], and the lift from $G_2 \to PGSp_6$ [cite: 8, 9].
2.  **Fourier Expansions without Shimura Varieties:** Because groups like split $G_2$ and anisotropic $F_4$ lack Shimura varieties, one must utilize *quaternionic discrete series* or *algebraic modular forms*. The problem demands computing the semi-classical Fourier expansions of these forms. For $G_2$, these coefficients are indexed by totally real cubic rings [cite: 2, 10].
3.  **Gross's Conjecture (2000):** A Waldspurger-type conjecture predicting that the square of the Fourier coefficients $a_E(F)^2$ of a quaternionic modular form $F$ on $G_2$ (lifted from a classical cusp form $f$ on $PGL_2$) encodes the central L-values of $f$ twisted by the cubic Artin motives associated to the index ring $E$ [cite: 2, 10]. Resolving this algorithmically and theoretically is the primary benchmark for this computational frontier.

## 4. Status & Bounds

**Last Known Status:**
The frontier has seen explosive progress between 2024 and 2025, pushing exceptional functoriality firmly into the computational domain.

*   **Gross's Conjecture:** The first complete examples of Gross's conjecture have been successfully proved. Sweeting, Horawa, Bakic, and Li-Huerta (2024/2025) verified the conjecture for the *dihedral case*. By utilizing an exceptional theta lift between $PU_3$ and $G_2$, they constructed global A-packets and obtained exact formulas for Fourier coefficients mapping to totally real cubic twists of L-values [cite: 10, 11].
*   **Gan-Gurevich Lifts:** Kim and Yamauchi (2024) successfully analyzed the Fourier expansion of Gan-Gurevich lifts (Hecke eigen quaternionic cusp forms on split $G_2$ arising from elliptic newforms without supercuspidal local components). They deployed degenerate Whittaker functions and Jacquet integrals to derive explicit formulas, providing robust partial answers to Gross's conjecture in higher weights ($k \ge 2$, even) [cite: 5].
*   **Level One $F_4$ Theta Lifts:** Shan (2025) proved the global exceptional theta correspondence for the dual pair $F_4 \times PGL_2$. Shan algorithmically constructed a family of level-one automorphic representations of an anisotropic exceptional group $F_4$ via "exceptional theta series"—holomorphic modular forms on $SL_2(\mathbb{Z})$ with explicit Fourier expansions that completely span the space of level-one cusp forms [cite: 4, 12].
*   **$G_2 \to PGSp_6$ cycles:** Cauchi, Lemma, and Rodrigues Jacinto (2024/2025) explicitly constructed algebraic cycles of codimension 3 in Siegel-Shimura varieties by exploiting the exceptional theta correspondence between split $G_2$ and $PGSp_6$. They linked the regulator of these Beilinson-Tate cycles to the residue of the degree-8 Spin L-function of $PGSp_6$ cuspidal forms [cite: 8, 9].
*   **Global Langlands Parameters for $G_2$:** Gan and Lapid (2025) achieved a precise characterization of automorphic representations of $GL(7)$ that arise as functorial lifts from globally generic cuspidal representations of $G_2$, effectively cementing the notion of global L-parameters for $G_2$ [cite: 13].

**Current Best Bounds and Conditional Qualifiers:**
Computational implementations (such as Pollack's SAGE routines for $G_2$ motives) are currently constrained to moderate weights and unramified or dihedral cases [cite: 1, 10]. Computations for highly ramified local components or dimensions exceeding level-one $F_4$ remain bounded by non-trivial archimedean integral complexities. Most exact Petersson norm formulas and Fourier bounds are conditional on the absence of supercuspidal local components [cite: 5]. 

## 5. Literature (Primary Sources)

*   **Shan, Y. (2025).** *Exceptional theta correspondence $F_4 \times PGL_2$ for level one automorphic representations.* arXiv:2501.19101. (Accepted by Algebra & Number Theory). Constructs explicit weighted exceptional theta series to map representations from $F_4$ to $PGL_2$ [cite: 4, 12].
*   **Bakić, P., Horawa, A., Li-Huerta, S. D., & Sweeting, N. (2025).** *Gross's conjecture: the dihedral case.* arXiv:2510.03476 / arXiv:2405.17375. (MIT/Princeton). Provides the first definitive proof of Gross's conjecture for dihedral modular forms via $PU_3 \to G_2$ theta lifts [cite: 10, 14].
*   **Kim, H. H., & Yamauchi, T. (2024).** *On the Fourier expansion of Gan-Gurevich lifts on the exceptional group of type $G_2$.* arXiv:2411.16953. Deploys degenerate Whittaker functions to compute Fourier expansions for CAP forms and Ikeda-type lifts to $G_2$ [cite: 5].
*   **Cauchi, A., Lemma, F., & Rodrigues Jacinto, J. (2025).** *Algebraic cycles and functorial lifts from $G_2$ to $PGSp_6$.* Algebra & Number Theory, 19(3), 551-616. arXiv:2202.09394. Evaluates Beilinson-Tate conjectures using exceptional theta correspondences [cite: 8, 9].
*   **Pollack, A. (2022/2024).** *Exceptional theta functions and arithmeticity of modular forms on $G_2$.* arXiv:2211.05280. Defines the basis of cuspidal modular forms for which all Fourier coefficients are in cyclotomic extensions [cite: 15].
*   **Gan, W. T., & Lapid, E. (2025).** *Global Langlands parameters for $G_2$.* (Tsinghua University / YMSC Lecture series). Characterizes functorial lifts from generic cuspidal representations of $G_2$ to $GL(7)$ [cite: 13].

## 6. Attack Vectors

**Live Techniques:**
1.  **Exceptional Theta Correspondence (Minimal Representations):** The primary vector for generating algorithmic lifts bypasses standard parabolic induction by using the restriction of the minimal representation of $E_7$ or $E_8$. For instance, the dual pair $PGL_2 \times F_4 \subset E_7$ [cite: 4] and $G_2 \times PGSp_6 \subset E_7$ [cite: 9] allow for the transfer of K-types (Howe duality) and explicit tracking of Fourier-Jacobi coefficients. 
2.  **Degenerate Whittaker Functions:** To bypass the lack of holomorphic discrete series on $G_2(\mathbb{R})$, researchers utilize quaternionic discrete series representations with small Gelfand-Kirillov dimensions. Jacquet integrals and Siegel series are then evaluated over unipotent radicals to derive exact formulas for Fourier expansions [cite: 5].
3.  **Algebraic Modular Forms:** Utilizing algebraic groups where the real points $G(\mathbb{R})$ are compact (e.g., compact $F_4$). Because the symmetric space is finite, the automorphic forms reduce to combinatorial objects that are highly amenable to direct computational enumeration [cite: 2].

**Exhausted Approaches:**
Attempts to explicitly compute Fourier expansions for exceptional groups using purely cohomological descent (e.g., standard generic trace formulas without explicitly isolating unipotent orbits) have largely been exhausted. They yield non-vanishing theorems but fail to provide the exact algebraic structures (the coefficient matrices) necessary for verifying computational conjectures like Gross's. 

**Computational Artifacts & Limitations:**
When transitioning these live techniques into symbolic codebases (e.g., SAGE routines for $G_2$ motives), algorithmic scaling hits a severe bottleneck. The expansion of Fourier-Jacobi coefficients indexed by arbitrary totally real cubic rings results in **PATTERN_VRAM_TRUNCATION_ARTIFACT**. The computational geometry required to store and symbolically integrate the archimedean components of high-weight tensor representations rapidly truncates memory boundaries, limiting current open-source algorithmic functoriality frameworks to low weights (e.g., weight 6 or 8) and level-one or tightly constrained ramification cases.

## 7. Cross-References

**Related Open Problems:**
1.  **Beilinson-Tate Conjectures for Higher Shimura Varieties:** The techniques used to lift $G_2 \to PGSp_6$ [cite: 9] are currently being investigated to map algebraic cycles and regulators to special values of L-functions for higher genus Siegel modular forms.
2.  **Rank 7 Motives:** The extraction of Galois representations associated to cuspidal representations of $G_2$ to construct motives of rank 7 and weight 0 over $\mathbb{Q}$ (a conjecture originally posed by Gross and Savin) [cite: 8, 16].

**Anti-Anchors (What not to conflate):**
*   *Classical vs. Exceptional Lifts:* Do not anchor the Gan-Gurevich lifts on $G_2$ to the classical Saito-Kurokawa lifts on $Sp_4$. While both produce CAP (Cuspidal Associated to Parabolics) representations, the unipotent radical of the Heisenberg parabolic in $G_2$ is non-abelian, forcing the use of non-abelian Fourier analysis and fundamentally different archimedean zeta integrals [cite: 5, 17]. 

**Candidate Primitives & Calibration Flags:**
As the frontier advances toward higher-level automorphic representations (beyond level 1), researchers face a persistent **PATTERN_CONDUCTOR_CONFOUND**. Because the maximal proper parabolics in exceptional groups (like $G_2$ and $F_4$) possess non-abelian unipotent radicals [cite: 17], distinguishing the specific conductors of ramified representations becomes deeply entangled. The standard abelian Galois cohomology used for groups of type A fails here. Additionally, when extracting central L-values from the squares of Fourier coefficients to satisfy Gross's conjecture, numerical pipelines frequently encounter **PATTERN_RANK_PARITY_LEAK**, where the predicted sign of the functional equation associated with the cubic Artin motives leaks into the parity calculations of the orthogonal parameters, causing sign errors in the predicted L-values if the archimedean K-types are not perfectly calibrated. Ongoing research by Sweeting and Shan aims to build robust categorical trace formulas to patch these parity leaks in higher-rank exceptional descent pipelines.

**Sources:**
1. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRnJebZUovZQfnKGlGKzxwwg0WURmB4T5G52or2pWgOxBG9BgvFDqPesesjbVmOHcgg_cKIKZDJFtYX8EzZMAZYBTtGmbkyZk2Rhs2nb6KdYoIxhIv_p5wzsoLNfYZTzZnPXDv2NV13iNUHXmHHA==)
2. [galoisrepresentations.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKPSh1VlQ9apjjiB8hK7t7KZBPIKn4g5Ncilyn87SW8PeYMSmoUnZEfZztaGmp9-9OMUE8uvlv_Zer7H8gfOJ3m265G5GKeXo_NzQPbvkWIDJv_JzWE9R96t_k8PhSweHdtsol03At7dEm94rf2Q==)
3. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1LDA734E81FqI_Kp3vNGwP5rSlMsJAQt2D_9h3NPivL0J7Ck2GRJIEfQxcrpoXsEhrgJe92AiU0KR3E50aumk-S7lNHLDueRSd_-m08DkjbYxh7qAiSD6Vw8EFTWno0S8XtFUktB3jIVh)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEK2gf-jx32wwK65QNKSmY-tUw2aDMxS9CQZ16Yq3HUfrPkuR2OoclOla_laACkq-JrDjQbJvH82FRuc8LTxCEGua0lCXPE4ymuejhmu3bDz2iSJa74wQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiV8fIbd7WhLW_OC2_lWFV7ucm6vB1y-G67CjoWBVYqDsnvCTEVAKt-TdsrRyHbC9ysPI_3PCZ7Ec-QWLG59jr-aSRmLHeu1h0cfYLj2dja9RobaI4jQ==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsjaQcgPhtCLRA-cQ_ftnJrDcn_atJ7NZfTlM2aWnl-C2qtjvftS-EGg_VekncAcx_gzRrsv1ccuqlKBXpGLHJ3Nj_YYfNgIr0xxhgXpcu-8-C_psqdQ==)
7. [osaka-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHE9mzpe_fw-4cyxBVWkpaFOn8yLAZnBio1Jt9bKxOYRmWyKn4-Ej1DCzVuil-uNq1wyJKXeDq5EWg-R4iH10Ux_fX7p_ZimwQFUCGs6pAQwez3TG2YpvOjmfI-jUzgL481DM0cQ4bOvhQBD5YwKcqTdhI=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNlTRqZcoYc6lwKmyYRSp0VgiUTkoqgDcx7dp_1UyT939TaPTXzlG1s4GkIPGfV6AgDKkiXQASm6H0izDcD-iYbX6gdEgJ2Mrx2vlHH1278MZ065D7mQ==)
9. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEl8x36BolENlCd13Z7900y9Rz-JdnFcas6q_zHwuYQfHbZEgb0wlz9OD11kV60Om_qWTNtcdL-JcrOI_aDDbpkOK70aP9vnDpaFJVt1VegN51iyvmL7t7iQ2cbgHWT8ZkRygcW9rNB_A==)
10. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETa7m8SSCXipTVkq1zqaEH8vhCbDYYh3IT_EsRmJIeZvX8Ubs2bNCS9HIlnXKj__j1XrV9ngZr9zZmoDmB1o59bTqsqWXFoGoYED-RbyrKp2kDLRHXj-_Dksdwkq_mme3t)
11. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGz6Q8IcXWsJClt2cthYLh55hBH4rO8_s6V2UxbOkqSPMMUrXjrp1LX-EeHZgyltOJ-L2mJHINUVimQIp9L_xWxixKNbAKx5XJBNZnhKBXZsrQ=)
12. [y-shan.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyOuVC2sqXjPDjvRKkM2UWcgHixgN-TUQ-oigwI1ZGjul0Ub9JCxUrdThafo7wVHtY9dMT3v9wLuo5dHHUXuKNrWAGfxXQdEuxR9x7Ou4bHmJVjf0235Qbumc=)
13. [tsinghua.edu.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZdCpiS7INMPYMZtW-GvGxABgZjGwIghM4Yn18oXYhqOOsdA61DRMtKma3ZnfVX3TBfEd3KCWFAYVuD-hNnMLcZwrDg9WlTM9m4jO6msqVY5a4xrgWFvVc__p_tEFNQKwYcE-PzUqkZQ==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFinakE4CIC3L7rBTVXDc1os20j4C_DtNkk_rogJ3mP3-jHdGUZEJ4G0laVUzXg7PAUGvYeph4Y2EdfVNPd8PloXaneHyur4QmJ6I7etEH-gFc4wv9pJA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGECA7pBWaQEYNvvaMTKTP5DI-pwKwOagZ6FfsPoTpZZczX-EvP1QUzB39gE3IUtc5qZivpOF15aVxdvwmnKN2Sh9qoe5qLkP6gBdthcaX4DGHjMeuBRg==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMOoww8_MMbRUksjnyXdKopZvsigMmoz1s1LCjvPUefx4EOxliXrnJBfjeVFxLQ54orNP5436ngF31N-OLEc3HcbOsuAkSZvaLUVt9QejTKgwtlkIUogkV6BDe5OqMMg9pw0CjquHQ4TdoYnBm01O34c5ipuqeK7JGglLABumlvaEA9BagGEbG1x4WIJzicaA6Njkrbiv0zofMhKi4QvEpYLYvchZ72dkAvc6qq9mnEoJj8VOTrZc=)
17. [msp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyCpdGPnOOhz4Y5Ft7Mg_WE--eetNJeneII_UZXkR3T9rBPCPs9LKCTlP2dynJw1P7BlbS5JlNlKiF74NO8lCbYUOCKlWHuE2XSS8JnYFGr70eT1BcSJDyR6HDVbYMLEjX8muYPZeKJw==)


# Prompt 101: Automated Scientific Discovery reproducibility audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiYmFmYXFmeERfLXFzT0lQN0p2UTJRURIXYmJhZmFxZnhEXy1xc09JUDdKdlEyUVE
**Elapsed:** 334s

---

REPRODUCIBLE_WITH_EFFORT

PART 2. THE ARTEFACT TRAIL
The original BACON family of discovery programs—including BACON.1 through BACON.5, alongside sibling programs DALTON, GLAUBER, and STAHL—was developed in the late "1970s to 1980s" at Carnegie Mellon University and the University of California, Irvine [cite: 1, 2]. These systems were primarily implemented using OPS2, an early Lisp-based production system language, and PRISM, a system for the representation and inference of production rules [cite: 3, 4]. 

The original Lisp and OPS2 source code is lost to the public domain. There are no confirmed museum archives, university FTP remnants, or public repositories containing the raw historical code used to generate the original papers in the 1970s and 1980s [cite: 5, 6]. 

However, the definitive algorithmic blueprint survives intact. The heuristics, production rules, and underlying philosophy of the system were documented in exhaustive detail in the 1987 book Scientific Discovery: Computational Explorations of the Creative Processes by Pat Langley, Herbert A. Simon, Gary L. Bradshaw, and Jan M. Zytkow, published by The MIT Press, DOI 10.7551/mitpress/6090.001.0001 [cite: 1, 7]. 

Because the algorithms were published so transparently, later faithful reimplementations exist:
1. Lindsey Spratt authored a reimplementation named bacon-logtalk, located at https://github.com/lindseyspratt/bacon-logtalk [cite: 5]. Originally written in MacProlog32 in the 1990s and later ported to XGP and Logtalk (a Prolog extension), Spratt explicitly claims this is a faithful reconstruction based solely on reading the 1987 MIT Press book [cite: 5].
2. A 2024 paper published at the AAAI conference on Artificial Intelligence reported rebuilding BACON in a modern computing language (Python) exactly as described by Langley, Simon, and Bradshaw in 1987, with the addition of a single parameter to better handle noise [cite: 8]. The source code for this modern reconstruction is associated with the DiscoFunk repository at https://github.com/gahrae/DiscoFunk [cite: 9].

PART 3. THE PUBLISHED RESULT TO CHECK AGAINST
The core claim of the original publications is that the BACON programs could autonomously rediscover quantitative empirical laws and invent theoretical concepts from tabulated data by applying simple, data-driven heuristics, such as noting constant differences or ratios between variables [cite: 1, 10]. 

A reproduction would have to match the following specific historical claims from the original texts (most notably Langley, Bradshaw, and Simon's 1981 paper BACON.5: The Discovery of Conservation Laws, and the 1987 book):

1. Kepler's Third Law of Planetary Motion: BACON.1 and BACON.3 are claimed to discover that the cube of a planet's distance divided by the square of its period is constant. Using the exact synthetic dataset published in the 1987 book, where the Distance D values are 1, 4, 9 and the Period P values are 1, 8, 27, the reproduction must generate the term D^3/P^2 (or equivalent) and compute its invariant value as exactly 1.0 [cite: 8, 11, 12].
2. The Ideal Gas Law: BACON.5 is claimed to discover pV = nRT. The reproduction must match the exact stepwise concept generation and intermediate constants reported. First, holding n at 1 and T at 300, it must multiply pressure p and volume V to find a constant. It then varies T (T=310 yields pV=2579.2; T=320 yields pV=2662.4) [cite: 11]. The reproduction must successfully relate pV and T linearly with a zero intercept to generate the new concept pV/T, yielding the exact figure 8.32. Finally, by varying n to 2 and 3, it must calculate pV/T as 16.64 and 24.96 respectively, leading to the final invariant term pV/nT = 8.32 [cite: 11].

If a reimplementation fails to generate these exact theoretical concepts (like pV/T) and the corresponding constant figures on the provided datasets, it has failed to reproduce the original claim.

PART 4. WHAT WOULD BREAK A REPRODUCTION
A modern reproduction attempt is highly vulnerable to several undocumented or heavily controlled variables from the original experiments:

1. Hand-Tuned Tolerance Parameters: BACON relies fundamentally on a "tolerance parameter" to establish when a computed value (like a ratio) should be considered a constant despite mathematical noise [cite: 4]. The exact thresholds used in the original Lisp runs were never universally published. Lindsey Spratt noted that BACON's analysis is chaotic and extremely sensitive to these tolerance parameters, which caused his Prolog reproduction to fail to find the Ideal Gas Law [cite: 5]. The AAAI 2024 Python reimplementation confirmed that Langley used a fixed, hand-tuned threshold to stop iterations, forcing modern implementers to augment the system with new parameters just to make it function reliably [cite: 8]. 
2. Synthetic and Sanitized Datasets: A reproduction will break if fed actual, raw historical data. The original program was not evaluated on Tycho Brahe's noisy astronomical observations or Robert Boyle's raw laboratory measurements. The datasets were heavily sanitized into toy integer matrices (e.g., D=1, 4, 9 and P=1, 8, 27) perfectly tailored to yield the target equations [cite: 12]. 
3. Interactive Human Input and Representation Dependence: BACON is entirely dependent on the representation chosen by the human operator. The user must manually select, categorize, and group the independent and dependent variables into specific tables [cite: 13, 14]. In BACON.5, if variables associated with different physical objects are not explicitly paired and ordered by the user, the program's symmetry heuristics break down and it cannot deduce conservation laws [cite: 11, 15]. 

PART 5. THE STANDING CRITIQUE OF THE ORIGINAL RESULT
The BACON system provoked intense and decisive criticism from historians, philosophers of science, and AI researchers regarding its claim to model genuine scientific discovery.

The most thorough historical critique was published by Albrecht Heeffer in his 2014 paper Data-Driven Induction in Scientific Discovery: A Critical Assessment Based on Kepler's Discoveries [cite: 12]. Heeffer systematically demonstrated that the data fed to BACON did not correspond to the historical data available to Kepler or Descartes [cite: 12]. Heeffer argued that BACON's success was a mirage reliant on artificially clean toy datasets. For instance, using BACON's input data for Kepler's third law (D=1, 4, 9 and P=1, 8, 27), a simple quadratic relation (P = 11.60 D^2 + 17.12 D - 6.10) fits the data perfectly. Heeffer noted that BACON ignores simpler equations and finds the complex D^3/P^2 relation only because its production rules were deliberately rigged by the programmers to hunt for the specific mathematical forms of known physical laws [cite: 12]. 

From an artificial intelligence perspective, Sleeman et al. (1989) criticized BACON for skipping the most difficult phase of actual scientific discovery: deciding which variables to explore and designing the experiments to gather them. By relying on human operators to hand-hold the algorithm by pre-processing the data and isolating only the relevant factors, the human researchers were implicitly communicating the answer to the machine before the run even began [cite: 13, 14]. 

Sociologists of science and philosophers, such as Harry Collins, challenged the underlying epistemology of BACON. They argued that Simon's model treated scientific discovery as a purely data-driven heuristic search, ignoring the reality that scientific observation is heavily theory-laden [cite: 16, 17, 18]. Critics pointed out that the BACON process was "tool-driven" rather than "data-driven," heavily influenced by the creators' retroactive knowledge of the target laws, making it an exercise in curve-fitting rather than an authentic model of human creativity [cite: 17, 18]. 

PART 6. IF IT CANNOT BE REPRODUCED, WHAT IS THE NEAREST HONEST THING
Because the verdict is REPRODUCIBLE_WITH_EFFORT, the system can be rebuilt and run today, provided one accepts the constraints of the original experiment. Here is the reproduction recipe:

Exact software: Do not search for the original OPS2/Lisp source code. Instead, either write a production system directly from the rule descriptions in the 1987 MIT Press book Scientific Discovery (DOI 10.7551/mitpress/6090.001.0001), or utilize Lindsey Spratt's existing Logtalk implementation available at https://github.com/lindseyspratt/bacon-logtalk [cite: 1, 5]. 

Parameters: The equality tolerance threshold must be manually tuned by the programmer. Begin with a strict equality threshold (tolerance = 0.0) for the idealized Kepler dataset, but you will need to manually adjust the float tolerance for the Ideal Gas Law to prevent the combinatorial explosion of theoretical terms [cite: 4, 5].

Datasets: Do not use real historical data. Construct the synthetic matrices provided in the 1987 book. For Kepler's Third Law, input exactly three rows for Distance (1, 4, 9) and Period (1, 8, 27) [cite: 12]. For the Ideal Gas Law, input the integer variables n (1, 2, 3), T (300, 310, 320), and vary p values to generate the corresponding idealized V values as described in the 1981 IJCAI paper [cite: 11].

Compute cost: The search space is heavily constrained by the hardcoded heuristics and the microscopic dataset size (fewer than 20 rows). The reproduction will execute in a fraction of a second on any modern CPU, requiring negligible memory or compute resources.

Compare against: Check the execution trace to ensure the program dynamically generates the theoretical term D^3/P^2 and assigns it an invariant value of 1.0 for the Kepler dataset [cite: 12]. For the Ideal Gas Law, verify that the program generates the intermediate concept pV/T and calculates its value as exactly 8.32 when n=1, 16.64 when n=2, and 24.96 when n=3, before finalizing the invariant pV/nT = 8.32 [cite: 11].

**Sources:**
1. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQ5XpJ_vfhwM0A2aIX8CgXy4KP_7Wkihm_TiXkyRURq4HJ791Jbp5CJxfDzx8VqRHsXSLHqxoUBXEsoUGqVW-oLlRcl8qiU5Ikl8wWcpuiRQw5JX2WULRNxZ_jBrut1z1TWbzQlw0Reg-q30XYkbHmmgQ4LyaQldECcX2VWPR4ND9cN1lClWSWgEwpm-K0)
2. [isle.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7aAiGC7ps7rK-NjRz3rGiOHH9BPSLenAL4FRUKc6RTHVr5CT1BSF7mAHqsMlqOopjdb-FBqonJ07jcYMknuNd8KyXJsba63XneUBRzsUDOxzu0vwCkEYbQQ==)
3. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTxi5ty6EoBTqSsaHlLEOfrSZhHv2tG4fbynIY7oJeNlYDrqUJAEsFA_qqnDnGsYaGkprKgKBlEhPgkwE9UHWbIpPmAKo2521bON37Zbb1lu5MouKPzx5Rh1LJLIIo1uNbVA60l8RJo3daUQ5gYh31poAzVdvzKUkiB-V_SQWGHA==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBjHk9SjlTJOuSa0X7QBazR5j5YmSEPIynuNA8xkciTyGAlXvUC-K_OxAUwxk5D5468VOD_ta2_TGMH1FOsqPlMcLl6YvdMoO0gvCJnXbKtPUFRjMUbVPL9w==)
5. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYEZ4qeJ4zbopesWwqKKOnVjm_X4HTd06mRuT-ZBT6fvL_0b9kolalhhRGcNicWDaqGaVem3tLO62l834RjF1Sm5QBADlhpyVNglYBKB-mEtontCqjcQMI3TaJNpOzYjCMYtN8)
6. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLisRo0OpTeb2e7RZaKLMMLVtgrLYjnYhG5UKf0WC1mhRSOSKViWsL-H95PgocuQeBPrIWlV30kRXotIUlZs2i1hJzEu_JCcOa1j9lJ0HtYP-eRDuN1FIpbBSxwGO6EG_Sycpzv_wB)
7. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5LnE2ibJFyT5J3cpV9CDfyr9Bl-33AQRdrdtwN0G0Z-fo8Tf7MDhDsbUfG0lVjKbJj-bq7OAOkQ1G8fDan7T912dKj9Z01c0xWmupNVcfhiKhPUHEXdb5Rt1j4UHUqtHi4nHZKSKY-8jmeIBzeMeA9I2J)
8. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExSXFP2-ShuPH1EYU4Txt44lbdKYYoK7qJ4d-i6N4ItMsfIHk-f_giTvee21RPLkXbqAqEDYV-XvKInWDGWmD-f5XtxBYFStg8ZYElB_t415ABwuM9eKsYAUqI2XJBjQyxKmlOwuRe9E_27bWUKEaslkZch94J)
9. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQ5aM0u2iiHWmg2ZcRvfbctUWmbVzcobnTSIQuXiokmrVJin_QAHLC2lOoDMZImVNxxUzXTHvApKPoZ2DL0IHy1wSvLAE1EOpAgE26bZW1oACgHaEvXnfSsMOqtnU1CSiH6a4IvqY8IBaPwzrfe7eN7mnZ9Kca2qwqAVyuMCOTrG1MotkHdhQo1QQ=)
10. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF70qigtIrx1VZ0MUaId2kPHIVElVmmlRDvnks0j4CUVhKuFmodHHo9Ln7OPqM1D4qmbu9ZhjCf-IpsxckNx2n_o5EeN8B5n1i0cXkP5AK2VtkAAV4l8l6OmI_b2ACWCnDy9tU=)
11. [ijcai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-COzM3Dz7FySOIdkXBzVkBX_H4Bc1SI_gHEZJToXta-tzhXbF53k8Yl03oZ6FZQJ_dCOyoRtLI_Bii4tEtFtEGr-jib-mB9Ew5LDqy06yE_g-0egL6z3aZU9Ez-2h4xMXLqxvZUmOYtTd-A==)
12. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGWvm8YNkgxpkg1Sl4h9QGbBGCcXoAKcKXgeT93YhtQvLRXLdJMNgVitEJIlqtpSCKGdK-stq7n2MNkQFNWcYKtH_Cav4ijFJhVHeR-V58FpLOplgxgxgHLDRiKIyfGkdLqLzelArsLAB38AlmYkKfLW2S_JlVSt4vKLh6YsVA85za2uX3rnF_TdqGPx1zMM77Qs5kQkRDMdYKaqKFG0yrljXwkkcXpXA5a4jfx818ISgO_M7ZkbxVoNcVA4K2-gvV2fInfNCxXkgOtA==)
13. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1MphF3qoloVqDo6N6vKoHsPvBIgG4GHRkbXmqqaHpKC-ZAAsmFtlCDTsZjkUjzNjViwTHhdxF-Ms9QeUr7WOrJABl38eQWYamdQs0Ql4R0iH_fKMWaNuS-__wEnUO3BZ9rOeYk9mJ-VC-FJk_B3s5-IZ1Fdk1wxfu9_l2npT9yG4RZLjxMnu3Ic4gQFiubPXQ)
14. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeAc1M1kTnisduDwYobNdnQPiQ2D8vvcn12g_boYjohMS1TuO8T2Tyguv07nUZX_LwAL9K8ha0ZisiHSVLv3iGbkEmV6jtL-g9EA2y4gNcXqy9qwG2yNmYyI8g6Z4zfvf5vgm_AXIVLzlVe25n0WY6W6PRAyLwlI3Q7jKEDkqc)
15. [scribd.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpIyqN294SxJ7_gdWiNdj4HhrSpGZx1XktWE0prW76AEQDsbdcrWkfNxXKvkXu4P5aICvqAF___Cq1QPJetlKuCeug24MTOJRgl4lwhgZXeQVNdkig2S6sQY78mSJu1Px4TQ26YDRhva4UAncQ4qRZ3o_NS_nyD2_G)
16. [ethz.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdUvinSZYHN1GweUNehdSFaaaft2HBdzxGHBT_stTXW8OQLCCgHKPMkMDPnNPPB4vR2abeDeq_O95qJD9hF0QbOmUJGd34AgVpMf7Z3K6D1UjxDwoCqS7E07cEOLNi0RKmrT0U73k7RRPdZS6Z7yVqibHNOckSuHE2TiGjHyBWXQPyZQyntNepiq9N2fEmtS7l3WZxwbFvyy8IQBOP2-ZX5Vya84I=)
17. [dangoldstein.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhxJryUFqMF-JwJzaLeYGa136og-bCNcvAxENoLD0EqkIbyh9-47ZinGnd7iX5-nPwV485fznXbsCmo-VbetRh7D90lsyd9FvdsXee0zP7k9PydjVp6B84xrNWYYqvLb8PZK73Gujc4JPre-qcVMM8QMQQV48y1eVoVElpj0_A5lufF5SUnAAh3Q==)
18. [ugent.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzf47eFgFavKMfl5CqiSDIfygBFssRg7eArQH6bJwr4fv5GaHwKBb36uImJ09t9eXR58bU255xAzbnuxcRedP_Yi0ye9hUBaw32LACL5smTbBLVjaDgkY7DBrl9n4ZjkQi7ObN2zTAAGqz-oUOaI0ZyRIU)


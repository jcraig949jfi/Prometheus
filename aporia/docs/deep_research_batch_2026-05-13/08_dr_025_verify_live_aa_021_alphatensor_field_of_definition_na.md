# Prompt 08: DR-025 — VERIFY-LIVE AA-021 AlphaTensor field-of-definition (Nature 2022 paper primary pin)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc1RFVFYW9yZkVxLWYtOFlQcmJDTnFRRRIXNURVRWFvcmZFcS1mLThZUHJiQ05xUUU
**Elapsed:** 938s

---

# Substrate Report: VERIFY-LIVE AA-021 AlphaTensor Field-of-Definition

**Key Points:**
*   Research confirms that the primary source for AlphaTensor (Fawzi et al., October 2022) explicitly restricts its 47-multiplication discovery for $4 \times 4$ matrices to the finite field $\mathbb{Z}_2$. It did not surpass Strassen's 49-multiplication bound for general standard arithmetic over the complex numbers $\mathbb{C}$.
*   It seems likely that strong gravity wells in academic discourse and secondary reporting have collapsed these distinct mathematical invariants. Recent literature routinely omits the field-of-definition qualifier, falsely implying a general algorithmic bound for standard matrix multiplication.
*   Evidence leans toward a necessary anti-anchor to strictly delineate the architecture and results of AlphaTensor (a reinforcement learning system) from the later AlphaEvolve (a 2025 large language model evolutionary system), which actually claims the reduction to 48 multiplications over characteristic 0 fields. 

***

## (a) PRIMARY SOURCE CONFIRMATION

The anti-anchor candidate VERIFY-LIVE AA-021 rightly flags a pervasive collapse of coordinates regarding the field of definition in AlphaTensor’s results. To register this anti-anchor as a permanent substrate pin, we anchor it to the PEER-REVIEWED primary literature. 

The definitive publication is the *Nature* paper by Fawzi et al., titled "Discovering faster matrix multiplication algorithms with reinforcement learning," formally published on October 5, 2022 (Vol. 610, pp. 47–53) [cite: 1]. 

The primary source explicitly bifurcates its findings into two mathematically distinct coordinates: **tensor rank over modular arithmetic** (specifically $\mathbb{Z}_2$, the finite field of two elements) and **tensor rank over standard arithmetic** (real $\mathbb{R}$ or complex $\mathbb{C}$ numbers). 

The specific breakthrough regarding $4 \times 4$ matrices is stated with unambiguous coordinate precision in the original text:
> "In particular, AlphaTensor finds an algorithm for multiplying 4 × 4 matrices using 47 multiplications in $\mathbb{Z}_2$, thereby outperforming Strassen’s two-level algorithm, which involves $7^2 = 49$ multiplications." [cite: 1]

The authors explicitly qualify what AlphaTensor achieved when standard arithmetic is required:
> "Moreover, AlphaTensor discovers efficient algorithms for multiplying matrices in standard arithmetic; for example, AlphaTensor finds a rank-76 decomposition of $T_{4,5,5}$, improving over the previous state-of-the-art complexity of 80 multiplications." [cite: 1]

Crucially, nowhere in the primary 2022 source do the authors claim to have reduced the tensor rank of $4 \times 4$ matrix multiplication below 49 over $\mathbb{R}$ or $\mathbb{C}$. The $47$-multiplication algorithm operates under modulo 2 arithmetic, a characteristic 2 field where addition and subtraction are structurally equivalent ($1 = -1 \pmod 2$). This equivalence collapses terms that do not cancel out in fields of characteristic 0, meaning the 47-rank decomposition is mathematically invalid for general standard arithmetic [cite: 2, 3]. 

**Status of Primary Source:** UNCONDITIONAL, PEER-REVIEWED, definitively published October 2022. Not withdrawn. The anti-anchor AA-021 correctly identifies that AlphaTensor *failed* to beat the Strassen bound over $\mathbb{C}$, rendering its 4x4 matrix bounds over $\mathbb{C}$ $\ge 49$ (or equal to 49 when utilizing Strassen's recursive scheme).

## (b) FOLLOW-ON WORK (2024-2026)

The 24-month window covering 2024–2026 exhibits extreme turbulence in this domain due to the introduction of a new AI methodology by Google DeepMind. The literature shows a high risk of gravitational collapse between the 2022 AlphaTensor results and the 2025 AlphaEvolve results. 

**AlphaEvolve (May 2025 - ANNOUNCED-NOT-PUBLISHED)**
In May 2025, DeepMind unveiled AlphaEvolve, a fundamentally different substrate system. While AlphaTensor utilized AlphaZero-style reinforcement learning (RL) guided by Monte Carlo Tree Search to play "TensorGame" [cite: 4, 5], AlphaEvolve pairs a Large Language Model (Gemini) with an automated evolutionary framework to mutate code and heuristics directly [cite: 6, 7]. 

Follow-on reviews and technical analyses from late 2025 and 2026 explicitly separate AlphaEvolve's achievements from AlphaTensor's. In a detailed March 2026 review, the architectural and numerical distinctions are clarified:
> "One clarification worth making: DeepMind's earlier system AlphaTensor (2022) achieved 47 multiplications. But only over modular arithmetic and finite fields, not over real and complex numbers. AlphaEvolve's 48 is the record for the number systems that matter most in practice." [cite: 8]

A May 2025 technical analysis by E. Uchoa further reinforces this distinct coordinate: AlphaTensor (2022) obtained 47 multiplications for $\mathbb{Z}_2$, whereas AlphaEvolve (2025) achieved 48 scalar multiplications over standard arithmetic fields, finally breaking the 56-year-old 49-multiplication record established by Strassen for general complex numbers [cite: 9].

**Flag for Downstream Consumers (Premature "Y proved X" claims):**
We must explicitly flag that while AlphaEvolve's $4 \times 4$ bound over $\mathbb{C} \le 48$ is heavily cited in 2025–2026 secondary literature [cite: 8, 10], the system's foundational paper (referenced in March 2026 as "Balog (2025) AlphaEvolve: a coding agent for scientific and algorithmic discovery" [cite: 11]) appears to be primarily driven by a blog announcement and preprint-level dissemination as of mid-2025 [cite: 7]. Prometheus must treat the AlphaEvolve 48-bound over $\mathbb{C}$ as ANNOUNCED-NOT-PUBLISHED until peer review validation is registered in the catalog. 

Furthermore, we must deploy an anti-gravitational pin against the narrative that AlphaEvolve is simply "AlphaTensor scaled up." The 2025 literature confirms AlphaEvolve is a general-purpose LLM evolutionary agent generating Python/C++ code, completely abandoning the exact formulation of TensorGame used by AlphaTensor [cite: 6, 7]. 

## (c) FALSE-FORM RECURRENCE

A search of the 2024–2026 literature reveals that the AA-021 anti-anchor is absolutely essential. The LLM/academic gradient toward collapsing invariants into a simplified "AlphaTensor beat Strassen" narrative is pervasive and actively polluting recent primary and secondary substrates.

**Instance 1: ArXiv Preprint 2406.05027v3 (January 27, 2025)**
In an actively updated 2025 paper discussing RL for algorithm research, the authors write:
> "Feeding this tensor into the RL agent, they successfully improved on matrix-multiplication algorithms for 4x4 matrices by beating Strassen's algorithm, the current state-of-the-art, with an improvement from 49 to 47 multiplications." [cite: 12]

**Instance 2: NeurIPS 2024 Virtual Poster 94064**
The same collapsed claim appears verbatim in a 2024 NeurIPS presentation:
> "Feeding this tensor into the RL agent, they successfully improved on matrix-multiplication algorithms for 4x4 matrices by beating Strassen’s algorithm, the current state-of-the-art, with an improvement from 49 to 47 multiplications." [cite: 13]

In both PEER-REVIEWED and PREPRINT literature traversing 2024 and 2025, authors explicitly strip the "$\mathbb{Z}_2$" and "finite field" constraints from the finding. By failing to isolate $R_{\mathbb{Z}_2}$ from $R_{\mathbb{C}}$, these sources assert a mathematically false form—that the standard complexity of $4 \times 4$ matrix multiplication was reduced to 47. 

Conversely, some encyclopedic inputs correctly preserve the distinction. A 2024/2025 catalog entry appropriately limits the achievement: "...AlphaTensor discovered a factorization requiring only 47 multiplications, surpassing Strassen’s recursive bound of 49 multiplications in certain rings such as modular arithmetic over small primes..." [cite: 14]. However, the high recurrence of the unconstrained false form in AI venue submissions justifies an aggressive deployment of AA-021.

## (d) RECOMMENDATION

Based on the primary source anchoring and the verified 2024-2026 false-form recurrence, I issue the following substrate actions:

**(i) Anti-Anchor Form Assessment & Refinement**
The candidate `VERIFY-LIVE AA-021` is **correct but requires coordinate refinement**. It must explicitly enforce the HARD-5 invariant rules regarding field-of-definition constraints. 
*   **Target Edit:** Refine AA-021 to state: "AlphaTensor (2022) established that the tensor rank of $4 \times 4$ matrix multiplication over $\mathbb{Z}_2$ is $\le 47$. It did NOT break the Strassen tensor rank bound of 49 over $\mathbb{R}$ or $\mathbb{C}$. Do not collapse $R_{\mathbb{Z}_2}(T_{4,4,4})$ with $R_{\mathbb{C}}(T_{4,4,4})$." 
*   **Downstream Consumer:** Push to the `AlgorithmEvolutionaryLoop` primitive field schema to reject any agent hallucination suggesting a 47-multiplication scheme over $\mathbb{C}$.

**(ii) New Sub-Anchors & Companion Anti-Anchors**
*   **Companion AA-021-B (Architecture Independence):** Deploy an anti-anchor separating the 2022 and 2025 systems. "Resist the gravity well linking AlphaTensor and AlphaEvolve. AlphaTensor (2022) utilized RL/MCTS to play TensorGame; AlphaEvolve (2025) utilized LLM code-mutation and evolutionary verification. They are distinct optimization paradigms."
*   **Companion AA-021-C (AlphaEvolve Coordinate Lock):** "AlphaEvolve (2025) achieved a tensor rank of 48 for $4 \times 4$ matrices over characteristic 0 fields (complex numbers). Do not map the 47 bound to AlphaEvolve, nor the 48 bound to AlphaTensor."

**(iii) Verification Queue Additions**
*   **Work-queue entry:** Flag the May 2025 DeepMind announcement of AlphaEvolve (and the subsequent Balog 2025 paper) for status checking. We must transition the 48-multiplication result over $\mathbb{C}$ from ANNOUNCED-NOT-PUBLISHED to PEER-REVIEWED if formal publication has occurred by late 2026.
*   **Training-corpus filter:** Add a semantic filter for future ingestion pipelines. Any text matching `AlphaTensor` AND `47 multiplications` AND lacking `Z_2`, `modular`, `binary`, or `finite field` must be penalized or tagged with `<WARNING: COORD-COLLAPSE>`.

**Sources:**
1. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFCh_o-IafftxStqnIyP9dMtwhrJAD67thN6NGPMheWuRgWcgNPISYOWLEy2I-NC1rRUdfhrWAUi37ExNjOTzaF1dEprZDgHyPZTwlVCTd31J1PgyOkY1wzsIkq8ZhVMF7n3M_hIEf)
2. [computationalcomplexity.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFJFc_aMsaDgwvdJp1b2kSwEZldSOeBvPLH-4R3uQznn00S3KaOM6Dbm7P-kZJUxKljwokyilRLjTmAIUO-91eUF0Qv5yiqep51VK4jrrqWl0soXMwPoF13RQFDtazuD_JzA9stCTS4m1lObR2zu0Dbmm4f5KYkr4=)
3. [towardsai.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_mz5XawdwFtRXG-nK5H-i-f-5OldJiDXj5BCh1qv-bfTOfl4dcXRIDUQMQZzyLGULmS1LR3BA4UluSutjdOmI8URVfISbQ7DYCAWBS3JTzBgixC7R4BRyq4H51AYlI5WvPf0kEP4v0QvwBq7XjVxZ0j-FE1z7dE4LPXlnL3BSPA==)
4. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGh1VTvxYQ8sGKW4MRasYHKN-WDz5tC61XfxEuE2tQWzngew9mydKceQPSLDrob6JTyjhlkZyldh-gDePqRiXQsBE8fmb2LezCZO1-A5dG5EvKgEgeUeg-7j9Bhx4dxVC7o5D6gGIBBbpetyCVTrTeFRQzx0nn419iJKyZOJpvF5A==)
5. [i-programmer.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYKz_wfUqwYn562DOS17pLQdkWMGywhvxxYSQnLpq2IIdX-ZPWA9QQZdnHa4CnQlV48aJpzr5qXJnrlxsra04iN5olsguBDV5MOKbqA3sLPXC3R4dxHOSEOogMx-7Xdr25HkUHAqSuWwAMc8nA0PU26SWAUKqz60aBViyt7Z-O8CVsJoUvzs-O1UrjmP5NhFgvLRPaCfmHKgBEX_qH9ogWqyNkcqVp9axu3gx_8tDxxF7f)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ2N7rSSyCz2O26n39BSa2cVVwMXWVyLOnrzbbMh0GdWEBAfnYwFi9j3QLc7KlGO3zRB8Lm5xzUcs7lLhTLzwJhxUlFgZtuOlCDu3gF-1iLcLNKrTwLgeYnVfP-FC3pQ==)
7. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFI7tKJHUk90sGlOmK7vYx73ASXcVlq2nnVEna6lr8i-8RWxFX_tnCvbAurIXVhjOumw5HV54aPCo_wnPa7FAXZHGPoRGMIeYRw7nC4MEKuoIi7VLWyFHjT7K3e11F1VhOtDSK7y25GWAh4zqZZ9axusS7G8qRhwhdsLZ5gSpiS0DZnM9i1bOE3zntdW12AneQ-_2wp3rBSs_qo58Jpynw=)
8. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHu9rvqXE-_vWBijBr5cLji5AiiHWrqHwNlgM1LzdTf77iWWXLsAZhRDOX9hw2O108GclDjxk_nZ6H5n3hxNl15G25DbPLYLCLG7UYZOkNXm8EmxExB2ijYiJaoTdGQbiCO58zk45euVwaIXBImi4wX4JLwbL7tfpR6GRiT9ukfjjdaapN0_F_L3y5amAa5fQ6OYw==)
9. [inria.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJbHdFZclOGIkkFp3zxa3GigwIyPmkwyjZ1sJd8L_BnmWG0T9t-4nGU1QbtS9s659adVYVGCcZfO1zVVLbtzVXgSBDLLSd8S_4aLqe7gwcQdWGgn_2EfgbfGe-i3ysqYA0MAncAFmsqgQh3Ljy-8AYFdW5RN_W13-jRC732Eai2ROm_crvkwRySg9g3WL9zQ==)
10. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3STbtba_G-slEDr--4Hzsc7EFdk3CrCwMc2U85zlThkD2FfowxdZ6QLJ90YblX4EWH0wL5wRNpPFO3fZgXcq6adzwTZ8GvnwLk6kCAWGlY6TNNdMBNTdBQ5Wchr9Cy4gfW7LLYWBCisP-mVipfCTIEE4_DeXPzn4t7eGS_dppXL4tn6A4T8xtcp0bdRwM73HrTSc3gMtqhOg70Pk=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGe14QSwIAETuiHmeXznvhVuorQo8xtDTiSSkn8px-JZr6ovtblYg0hl8vmAO6VHmnwoLkeiuof-S65lcckKb9RDV-j19kti3-mhZE3SX-pV-nOMMoqf7xYqA==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8Ka7acp12dCAi5mU7Gu6mqjHFuKLu_IlebXUEHkLvgR287K1ndZ_-MnvlrTKD99Kq5VpvY9S6wC8WRkg14FAc2wBzFVD8gXyy5f4s2eKyR5YyYSwcqY-PVQ==)
13. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzvfIbp9vqgnXtQRFMu4pP-uPBeo_2w1jCEOtYSB-2dZ_lnGxdLfw4y8XWJI0thVM_kb7wAYyTa6B3feyp3BBZOL8nobS4LFwo2CLTHmlsVa4M-dDHpIIRau1_ZAn75_670Q==)
14. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjWMVNU5A3iDMKSM1nZk91AbweDwoXVO7T-Zy2luR1B03vLa6aYujz3z3RET5PQTTcEV5MXHYcYF-PfNArTvHSc7xOMDsNI693ifgyvlO70WCYweThHrm_SwGjJkSVN3mYlAx_)


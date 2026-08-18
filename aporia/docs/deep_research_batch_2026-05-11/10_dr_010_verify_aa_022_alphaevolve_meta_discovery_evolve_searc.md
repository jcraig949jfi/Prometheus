# Prompt 10: DR-010 — Verify AA-022 AlphaEvolve meta-discovery (evolve search algo) NOT direct tensor search

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc0cU1CYW9ENkZzZlJfdU1QX0phVzhRTRIXNHFNQmFvRDZGc2ZSX3VNUF9KYVc4UU0
**Elapsed:** 454s

---

# AA-022 Anti-Anchor Verification: AlphaEvolve Meta-Discovery Algorithm Synthesis

**Key Points:**
*   Evidence confirms AlphaEvolve operates via **MetaSearchAlgorithmSynthesis** (evolving gradient-based optimizers, heuristics, and search structures in code space), rather than **DirectTensorSearch** (navigating the tensor decomposition space directly).
*   The primary source (Novikov et al., June 2025) explicitly delineates its methodology for the 4x4 matrix multiplication breakthrough as the evolution of a custom search algorithm, specifically modifying loss functions, weight initializations, and optimizers (e.g., transitioning from Adam to AdamW). 
*   Follow-on work (2024–2026), including *ImprovEvolve* and *OpenEvolve*, reinforces this paradigm by extending the LLM-driven algorithmic evolution coordinates, though popular literature exhibits a strong gravitational pull toward collapsing this distinction into the false claim that AlphaEvolve "found the tensor directly."
*   This verification mandates immediate substrate updates: the AA-022 anti-anchor must be registered, training-corpus filters must be applied to down-weight collapsed narratives, and the coordinates of algorithmic abstractions must be explicitly expanded in the primitives catalog.

**Systemic Context & Complexity**
The analysis of LLM-guided automated discovery systems inherently risks collapsing mathematically and operationally distinct coordinates into generalized concepts like "AI optimization." The reality is far more structurally nuanced. In multi-agent substrate tracking, failing to distinguish the *domain of action* (e.g., mutating Python optimizer code versus selecting mathematical graph coordinates) leads to corrupted ontologies. The evidence leans heavily toward AlphaEvolve representing a fundamental shift in the domain of action—from mathematical state spaces to programmable algorithmic state spaces. This report navigates these complexities, providing actionable coordinates for research substrate integration.

---

## (a) PRIMARY SOURCE CONFIRMATION

The primary source for the AlphaEvolve system is the ANNOUNCED-NOT-PUBLISHED preprint:
**Novikov, A., Vũ, N., Eisenberger, M., et al. (June 16, 2025). "AlphaEvolve: A coding agent for scientific and algorithmic discovery." arXiv:2506.13131.** [cite: 1]

This document serves as the canonical origin for the system's architecture and experimental results. Crucially, the primary source explicitly confirms the anti-anchor's premise: AlphaEvolve does not operate on the mathematical object space directly (as in AlphaTensor), but rather on the code space that constructs the search algorithms.

### Delineation of Abstraction Coordinates
The primary source explicitly defines mathematically distinct levels of abstraction at which AlphaEvolve can operate. To satisfy HARD-5 constraints, these must be registered as distinct substrate coordinates rather than collapsed into a generic "search" heuristic:
1.  **RawStringEvolution**: Evolving the solution directly as a raw string representation (analogous to classical genetic algorithms).
2.  **ConstructorFunctionEvolution**: Evolving a deterministic Python function that specifies exactly how to construct the mathematical solution from scratch.
3.  **HeuristicSearchAlgorithmEvolution**: Evolving a bespoke, compute-bounded search algorithm to navigate a problem space.
4.  **CoEvolutionarySearch**: Co-evolving intermediate solutions and the highly tailored search algorithms designed to improve those specific intermediates. [cite: 2, 3]

For the problem of matrix multiplication (tensor decomposition), AlphaEvolve utilized the **HeuristicSearchAlgorithmEvolution** coordinate. It did not search the tensor rank space directly.

### Meta-Discovery Evidence in Tensor Decomposition
The primary source provides UNCONDITIONAL proof that the breakthrough 48-scalar multiplication procedure for 4x4 complex matrices was achieved by mutating the optimizer code, not by directly selecting tensor coordinates. 

The paper states:
> "Starting from the problem description and a standard gradient-based algorithm (including an initializer, a reconstruction loss function, and an Adam optimizer), AlphaEvolve is able to develop sophisticated tensor decomposition algorithms that outperform existing approaches." [cite: 2]

The substrate input must reflect the exact behavioral delta of the system. In this instance, AlphaEvolve proposed extensive, non-trivial modifications across several components of the gradient descent code. According to the source, the evolutionary process required 15 mutations to the initial codebase [cite: 4, 5]. Specific changes included:
*   Transitioning the optimizer from `optax.adam` to `optax.adamw` (introducing weight decay).
*   Mutating the weight initialization logic.
*   Altering the reconstruction loss function.
*   Conducting dynamic hyperparameter sweeps. [cite: 2]

The precise formulation from the source explicitly flags the *algorithm* as the discovered entity:
> "Notably, AlphaEvolve developed a search algorithm that found a procedure to multiply two 4 \times 4 complex-valued matrices using 48 scalar multiplications; offering the first improvement, after 56 years, over Strassen's algorithm in this setting." [cite: 1]

**Substrate Implications:** This permanently distinct behavior separates AlphaEvolve (`MetaSearchAlgorithmSynthesis`) from DeepMind's previous AlphaTensor model (`DirectTensorSearch`). AlphaTensor utilized deep reinforcement learning to treat the tensor decomposition problem as a single-player game, directly selecting coordinates in the tensor space [cite: 6, 7]. By contrast, AlphaEvolve mutated the PyTorch/JAX optimization logic (`XLA IR` and higher-level Python representations), and *that generated logic* subsequently found the 48-multiplication tensor decomposition during execution [cite: 6, 7]. 

---

## (b) FOLLOW-ON WORK (2024-2026)

In the 24-month window surrounding the AlphaEvolve announcement, the substrate tracking reveals significant follow-on work that both relies upon and refines the LLM-guided evolutionary paradigm. These works maintain the distinction between code-space evolution and mathematical-space search, though careful parsing is required to avoid premature verification of derivative claims.

### ImprovEvolve (Khrulkov et al., February 2026)
An ANNOUNCED-NOT-PUBLISHED preprint directly builds on the AlphaEvolve substrate coordinate.
**Khrulkov, V., et al. (February 10, 2026). "ImprovEvolve: Ask AlphaEvolve to Improve the Input Solution and Then Improvise." arXiv:2602.10233.** [cite: 8, 9]

*ImprovEvolve* refines the evolutionary prompt paradigm by formally constraining the API coordinates exposed to the LLM. Rather than allowing unbounded mutation of the entire search codebase, ImprovEvolve forces the LLM to parameterize a Python class with a strictly prescribed interface containing three distinct methodological invariants:
1.  `propose()`: Generate a valid initial mathematical solution.
2.  `improve()`: Increase the fitness of a given candidate solution.
3.  `perturb()`: Apply a stochastically driven structural mutation with a specified intensity. [cite: 9, 10]

**Unverified Claims Flag:** The ImprovEvolve paper claims UNCONDITIONAL improvements over AlphaEvolve's baselines, stating it achieved a new state-of-the-art lower bound of 0.96258 for the second autocorrelation inequality (improving upon AlphaEvolve's 0.96102) and new state-of-the-art results for hexagon packing (11, 12, 15, and 16 hexagons) [cite: 9, 11]. Furthermore, the authors introduce a variant called `ImprovEvolve+E` which utilizes "minor human edits to the optimizer and convergence parameters" to achieve these records [cite: 8, 11]. The substrate must log these records as CONDITIONAL upon the specific human-in-the-loop interventions (`ImprovEvolve+E`), and a separate verification work-queue entry must be triggered to vet the mathematical correctness of the 0.96258 autocorrelation bound.

### OpenEvolve (May 2026)
The open-source community generated a replication substrate dubbed *OpenEvolve*, which gained significant traction (6.2K GitHub stars) shortly after the May 2026 DeepMind follow-up blog post regarding AlphaEvolve's real-world impact. [cite: 12, 13]

Maintained by Asankhaya Sharma, OpenEvolve functions identically in concept to AlphaEvolve: it operates as a wrapper around frontier models (e.g., Gemini 2.5 Flash + Pro), applying the evolutionary coding loop to mutate functions, score them against user-defined evaluators, and execute survival-of-the-fittest parent selection [cite: 13]. 
*Behavioral Delta:* OpenEvolve provides public verification of the meta-discovery coordinate. It successfully evolved a `jax.lax.dot_general` contraction (stripping an unnecessary `Precision.HIGHEST` flag) to yield a 321x speedup on an XLA compiler implementation [cite: 13]. This confirms the `MetaSearchAlgorithmSynthesis` anti-anchor holds outside of DeepMind's proprietary infrastructure.

---

## (c) FALSE-FORM RECURRENCE

The LLM gradient toward conventional, simplified framings (the "gravity well") is intensely visible in the 2024-2026 literature surrounding AlphaEvolve. Writers, tech journalists, and even automated summary systems routinely collapse the mathematically distinct operation of `MetaSearchAlgorithmSynthesis` into `DirectTensorSearch` or `DirectObjectSynthesis`.

If the false form is prevalent, the anti-anchor is actively needed to protect the substrate's integrity. A survey of the literature reveals severe, recurring coordinate collapse.

**Instance 1: Collapse of Agency (Tech Press)**
> "Google DeepMind's AlphaEvolve AI system breaks a 56-year-old mathematical record by discovering a more efficient matrix multiplication algorithm..." [cite: 14]
> "AlphaEvolve found a way to multiply 4x4 complex-valued matrices using 48 scalar multiplications." [cite: 15]

*Analysis:* These quotes strip the meta-level reality. AlphaEvolve did not discover the matrix multiplication algorithm; AlphaEvolve discovered a *gradient-based optimization script*, and *that script* discovered the matrix multiplication algorithm when executed. 

**Instance 2: Geometric Coordinate Collapse**
> "For example, it advanced the kissing number problem... AlphaEvolve discovered a configuration of 593 outer spheres and established a new lower bound in 11 dimensions." [cite: 4]

*Analysis:* This is explicitly false at the substrate coordinate level. AlphaEvolve evolved a heuristic search algorithm. The evolved heuristic search algorithm, upon execution on distributed compute, located the mathematical configuration of 593 outer spheres [cite: 3, 16]. Collapsing the synthesizer with the artifact it synthesizes triggers a HARD-5 violation.

**Instance 3: Conflation with AlphaTensor**
> "...AlphaEvolve is part of a new wave of LLM-based optimizers. The paper argues that its specific use of an evolutionary algorithm is the key that enables it to solve significantly more challenging problems than other contemporary LLM-based methods (including deep reinforcement learning systems like AlphaTensor for specific problems)..." [cite: 5]
> "...AlphaEvolve, despite being a more general technology, obtained even better results than AlphaTensor..." [cite: 14]

*Analysis:* While these statements are factually adjacent to the truth, their framing generates a dangerous gravity well. They imply that AlphaEvolve and AlphaTensor are competing within the same operational space (LLM optimizers vs RL optimizers searching for tensors). The substrate must resist this. AlphaTensor is a reinforcement learning policy outputting tensor ranks. AlphaEvolve is an LLM mutator outputting Python/JAX code. They cannot be directly compared on a 1:1 architectural axis without acknowledging the abstraction layer shift. 

Because this false form recurrence is highly prevalent (appearing in official blogs, Wikipedia articles [cite: 12], and tech analysis), the AA-022 anti-anchor is absolutely critical. Without it, the training corpus will inexorably align downstream models to believe AlphaEvolve is simply "AlphaTensor with LLMs."

---

## (d) RECOMMENDATION

Based on the primary source anchoring and the analysis of follow-on work, the following actionable substrate updates are prescribed.

### (i) Assessment of the Anti-Anchor
**The anti-anchor's true form is CORRECT AS STATED and strongly needed.** 
AlphaEvolve operates strictly in the domain of code mutation (`MetaDiscoveryAlgorithmSynthesis`), whereas systems like AlphaTensor operate in the domain of mathematical coordinate selection (`DirectTensorSearch`). The pervasive recurrence of the false form in the 2025–2026 tech literature necessitates aggressive anti-anchor pinning. 

**Action:** Commit AA-022 to the active registry. Ensure downstream consumer `P32_EvolutionaryLLMSynthesis` strictly inherits the `MetaSearchAlgorithmSynthesis` sub-tactic, preventing cross-contamination with reinforcement learning object-search paradigms.

### (ii) Discovered Sub-Anchors & Companion Anti-Anchors
During verification, the requirement for stricter coordinate enforcement (HARD-5) emerged. The following catalog edits and companion anti-anchors are required:

*   **Catalog Edit - AlphaEvolve Abstraction Coordinates:** Register four distinct operational coordinates within the AlphaEvolve entry to prevent future collapse:
    1.  `AlphaEvolve_RawString`
    2.  `AlphaEvolve_ConstructorFunction`
    3.  `AlphaEvolve_HeuristicSearch` (The locus of the tensor decomposition breakthrough)
    4.  `AlphaEvolve_CoEvolution`
*   **Companion Anti-Anchor (AA-023):** *Verify AlphaEvolve hardware optimizations are code-level, not physical-level.* 
    *   *Context:* Literature claims "AlphaEvolve eliminated unnecessary bits in a crucial arithmetic circuit for TPUs" [cite: 14]. 
    *   *Pin:* AlphaEvolve mutated `Verilog` code (hardware description language); it does not operate in physical layout search spaces (unlike macro-placement RL agents). Register as `CodeLevelHardwareSynthesis`.
*   **Companion Anti-Anchor (AA-024):** *Verify FunSearch vs AlphaEvolve payload scope.*
    *   *Context:* Prevent the gravity well that "AlphaEvolve is just a multi-objective FunSearch." 
    *   *Pin:* `FunSearch` mutates a single isolated Python function. `AlphaEvolve` mutates multi-component codebases across diverse intermediate representations (XLA IR, JAX, Verilog) [cite: 6, 7, 17].

### (iii) Work-Queue Entries for Related Claims
The verification process surfaced several highly specific empirical claims from the 2025-2026 window that require independent, rigorous verification before they can be integrated as unconditional substrate truths.

*   **WQ-101 (ImprovEvolve Records):** Verify the mathematical validity of the *ImprovEvolve+E* claims presented by Khrulkov et al. (February 2026) [cite: 9]. Specifically, verify the lower bound of 0.96258 for the second autocorrelation inequality. Determine precisely which "minor human edits to the optimizer" were required to achieve this, as this dictates whether the result is classified as `AutonomousDiscovery` or `HumanAssistedDiscovery`.
*   **WQ-102 (Hexagon Packing Verification):** Verify the geometric proofs for the 11, 12, 15, and 16 hexagon packing boundaries produced by ImprovEvolve [cite: 9]. 
*   **WQ-103 (OpenEvolve Reproduction Baseline):** Clone and execute the *OpenEvolve* open-source implementation [cite: 13]. Establish an internal performance baseline to benchmark its implementation of the MAP-Elites / island-based population model [cite: 3, 7] against the theoretical architecture described in the proprietary AlphaEvolve paper.
*   **WQ-104 (Training-Corpus Filter Update):** Develop a semantic filter for the training corpus to explicitly down-weight or flag sentences matching the pattern `[AlphaEvolve | LLM agent] discovered [mathematical artifact | tensor configuration]`. Map these instances to the corrected coordinate: `[Agent] synthesized [Algorithm] which located [mathematical artifact]`.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH829e0atCOnCPmzt7tWG_jyZcLOpj2isxvnxg7IwWJMW9csbNiD2hE7Jj-61Zm0EuJaMqTMzejhDc-V6xYTmR5m9VcEZKdjjjEXm7HbjYyfA04dsSW)
2. [googleapis.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFT6VDQ5XgdPDXD_T1b3qzQm_uaXA96lH6KnBe8UWi0_EK6ElQrmQdomh_1V3RScrQGPXOlGAAHkUFA85uqBukbl7fLusKOZNfycDQyHE5Gh3SHUydcG0El00dwtCCBJ6ICaJ_uWGSpy8dXqy-rd2kJSSCt5C27bzMdnkzElCQr6s3_L8l2WD-chJsy8qGfhKWevNB6t1HTKHAPeMiJ0wpqJGa7NZtEEiXIDNfIy7MEd5R_w1pYix-DFwzJXoG9pZBrsZ7asIe0Ybc-g7oZhT49jQ==)
3. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyeRVtNGazSj3zzbHcOQ60cR8ABDdmUZsafqy2uf8zKg5qp-jArDZifgybmLV5WLjRUaP0_ZrnZtWlr6jGFlGcMo9y4ffLNuU_aLNYNnpd_OFMOjiyZuHNzl6Xhpq0k6V6QewTChqnaDXC9UGCoGJ5la_w6kK0sDT0Aig21Bk-itP-gUX7SOjyAZJi_6z5vc2h5Sye34CFTWANl7UtWMEPWiC_nEIOty2RCysl)
4. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFeUT60DIBDZ643LDzhkm96B4b-QfG9FXGr1h-rEMYXwjbILmg7auch5N6MLnGJl622bxbUfv95_mSOP3uLhMkaATbRu0RzzCG5v4ZjfkRRd9ZQrz2psU2tL9HgquZRs-IVG3PsVmmjSAT6sdfCB_Ibzht_LacSsPGAUf0AhBohzqBwGhA2UF8SYbOfjWqMtsJwXRb--V5rQEIbKpWzw==)
5. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaoTewTY7WMX4ATWymvy9urAjlJfIVikohzOtc3L20CflV1x92sGs6z6pOEPRwkcE4UNPpyLf175yBp6xlgKmV5xNuEbT3sYdnGzvF5lYuMmpFAMGS0eJtmPJIECVoWwFFX-RCTOwcWSEp0m0=)
6. [smythos.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAr7cxMit51DEgS1g3Hc8KCoyCc6TjbXWWJHX1P3woryDZ5K-dzMNr7lXKezUVFagMBrwXs5lM66XqiYECBSgvFv6IOQ_BtzUdHS9u7b-mvhDuDcsjPFC2huzyyBn-vEs2h01eoeiv7kbBpXE21jul)
7. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8IH5XKJS9EjJ7cQfsaxmDPWGbEJcuKtt_-MVbdvUcaTsniE4wBRAiDSLWS4rM6ijH2rqnGKXmDWoG3t3UYa0leFZUAX_DnONen7RHJArPErstjr5LpHqkZoFUCA97-A==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo99QJSCwNFd6yeKSICoJ5W6uMlGjYOUvKyMkWEsTqE9EHyv0RT4aNeF5j-CokfR1l7hEqvSpPaSYLGoHzILhAk_BlmzxAM_EX0XSSp6cK3ilo8DY--evD)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF13YEEgb-SN189CcqhI1ot98p2eGR7A0EK--y9ouHZfgURfL22DBXAM0Rzt7sGM0X0zwiAMjN-ssnZNstDeY6i_sbDV2tUM2FC547TijGLDJd6My2w)
10. [catalyzex.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENg7Kzrg_P3TRhF0WHyARzl1h5r_VdTWV0tqrTH2dJCZIFIohauFTaLg8bfzJ9Yku1pbitYt8ws_-lPsH7uwuxuYnEh3WqD4CHErMN4YCH4pq4jKX2oBfkXv18Kfxd85otBVmJnfGujfw=)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTuATIsakZ8qwQn3Nbzk9ed5xd0E-39Id0xALH9TUQb8lVboMduUilMOn1BpMfm-ZLgvRzqtiDjuHGfn6Ib01A1-FnUxtnW_H12UB0wmpysgv0mXJyroq40ZznDUcHbCe7AWamA1dbOgZCOO3pmMw2e_1mTzjQOyZaME4z2ejnr_Hw0C5m9boMKJEzC4MruhGUfWkwhg4UsI3plK1aw6atFL7lQmDeV2t_dM80SOD1erBIDiNxfg==)
12. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHbjyTse5y23SOqZ7slr9qSQG3PLxd3liYZ0ybq8AFryV3jfhzcwXFTbc7VQgi4pfbp5loTlI387wN0yVWscVVYs0thFvmXqFsWQJNUdU9dpPj7djWbQop49Hsom5s)
13. [towardsai.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtFaw3aBv77nUYd80Hz9CF8KHmMUV8m0-mQMK0RqBmzE67CPEgv5Lkce7s5B6lH0ShBbrwknv4ib88Wa7MJJw8U7C4isZ7vrHwxiY4IFUeNKcsbKIUBbvbFdiCA8hgqYVdfzpRSTW6Bn8Fc0dkENRzEbTPNyS6q2Vw_-Uf7yvQuHkEbIj3tgzHNPLJ3C3LiyYbWG3cynlusryk4Pc8o7S5duDSApOxQoKe0UaylGyfgw==)
14. [venturebeat.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBQxDcAOx-JAAQFbNEvoEyRE7Xl8Inbqfac0SyEXVllYrM91E2yGG3US2iDlUkqkmJFiKnMdGpX_uInOGcEoCWGdjMWO7HXSih5hVkrMfDsVzEYtl8xtRbgdAiSQWu1Py-HuuVLEs3ISKp5aVvgOPAGtPAjEvVyxv-4OmnqcNu8EMOLT7zoNCTtzUCFxZfOHkmQX9hI9e9O1vCjOWPhW2S8dZA7hffZCoWTGKLriySYLBM)
15. [ainews.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEn6VW5hpg3f9j6qHeKzM95boNTlcEWe24Zgd9tIvD8XLcl83LwkM-SkWwFPbPHmaxEtTo6JOFNl82rd2rgWYQvhQxu8qU98XYTSZuGM6XFjIR6lEwOhtzLWTFQlli__rC1TKuPK6IPbdXJTvIY7LJeCkQAtJzGqIlPefzN9aAIazPTZxx4lwhnyQ9bXZmfk9YtMQ==)
16. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTUQNigePpG2pOFVYII78VFOM2c9yvcp6u4LSBaj7ENuc5z2nPMIeCasZ1MruLxA16WJHvdx_qnGHPatNAHr0ThWydfJOZn4jmhm0dmnj-hilwtlKj4XmU75zUVdkSSsVKb_YSNnmvaUEAB5018FCQ-23mnn4VWSUkJaLQwuIVb6O9l77RxUw8aOpv--m24Bnb5jIwner8)
17. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEG43ThT_n6RMemjoSAKPuTTKH-9fiagGzblRJMgDksANOQMYolqMyEgRNMrud0vxP0oYVPP_ltQvbhuws4PgzeewzHCizgh5JwGQn8sWNZ7c4XGzaUpuGZk2fIRMuLnwU=)


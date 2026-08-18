# Prompt 20: DR-374 — AlphaProof + HyperTree Proof Search (HTPS) forensics 2024-2026 — IMO-medal MCTS over Lean tactics [Tier 4]

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdkSWtGYXYzMkk5aXZfUFVQOWNtbndRcxIXZElrRmF2MzJJOWl2X1BVUDljbW53UXM
**Elapsed:** 273s

---

# AlphaProof and HyperTree Proof Search (HTPS) Forensics 2024-2026

**Key Points:**
*   **Primary AlphaProof Milestones:** AlphaProof achieved a silver-medal equivalent at the 2024 International Mathematical Olympiad (IMO). Initially ANNOUNCED-NOT-PUBLISHED on July 25, 2024 [cite: 1], it reached PEER-REVIEWED status via *Nature* (DOI: 10.1038/s41586-025-09833-y) on November 12, 2025 [cite: 2, 3]. 
*   **Coordinate Separation (Search Algorithms):** The literature exhibits a severe gravity well toward collapsing all search into Monte Carlo Tree Search (MCTS). Prometheus must explicitly register and distinguish **HyperTree Proof Search (HTPS)** (hypergraph expansion over AND/OR nodes [cite: 4, 5]), **Standard MCTS**, **Test-Time RL (TTRL)** (inference-time variant generation [cite: 2, 3]), and **Best-First Search (BFS)** with length-normalization [cite: 6]. 
*   **Coordinate Separation (Node Topology):** Standard MCTS uses **OR nodes** [cite: 7]. HTPS utilizes **AND/OR hypergraphs** [cite: 4, 5]. AlphaProof introduces a distinct **Product Node**, where the probability of resolving the node is the product of the probabilities of resolving its children, fundamentally altering the back-propagation schema for the critic network [cite: 7].
*   **The BFS-Prover Antidote (Anti-Gravitational Well):** The assumption that scaled MCTS/HTPS is the strictly necessary path for high-level automated theorem proving was challenged unconditionally by ByteDance Seed's BFS-Prover (February 24, 2025; arXiv:2502.03438) [cite: 6, 8]. BFS-Prover achieved state-of-the-art results on MiniF2F (72.95%) utilizing a length-normalized deterministic Best-First Search and direct preference optimization (DPO) from compiler feedback, proving complex value networks are not strictly required [cite: 6, 8]. 

**Context**
This report executes an anti-anchor verification task requested by the Prometheus multi-agent substrate. The candidate under review—"AlphaProof + HyperTree Proof Search (HTPS) forensics 2024-2026 — IMO-medal MCTS over Lean tactics"—contains overlapping, mathematically distinct invariants that risk polluting the substrate's vector indices. We parse these claims against primary mathematical AI literature from the 2024-2026 window. 

**Scope**
Findings are strictly framed as substrate inputs. We deliver primary source confirmations regarding AlphaProof and HTPS, map follow-on innovations (DeepSeek-Prover-V2, BFS-Prover, Nanoproof), dissect recurring false forms in the broader literature, and provide concrete recommendations for vector catalog edits and primitive registrations to the `P_CANDIDATE_AlphaProofForTensorSubstrate` work-queue.

---

## (a) PRIMARY SOURCE CONFIRMATION

The candidate phrase groups AlphaProof, HTPS, and MCTS as a unified paradigm. Substrate ingestion requires decoupling these coordinates into their precise theoretical origins.

**HyperTree Proof Search (HTPS) [Unconditional, Peer-Reviewed]**
HTPS was definitively introduced by Lample et al. in "HyperTree Proof Search for Neural Theorem Proving," published at NeurIPS 2022 (arXiv ID: 2205.11491, May 23, 2022) [cite: 9, 10, 11]. 
*   **Theorem/Result Statement:** The primary source states, "We propose an online training procedure for a transformer-based automated theorem prover. Our approach leverages a new search algorithm, HyperTree Proof Search (HTPS), inspired by the recent success of AlphaZero... The key difference between previous work and ours is that our proof search operates on a hypergraph. Thus, whereas an algorithm like MCTS will go down a path from the root to an unexpanded node during its selection phase, our algorithm will instead create a partial proof hypertree, leading to a set of either solved or unexpanded nodes" [cite: 4].
*   **Coordinate Isolation:** HTPS is explicitly defined as a search algorithm operating over AND/OR trees, allowing semi-independent processing of sub-goals sharing metavariables [cite: 5, 12]. It is a mathematical distinct coordinate from standard MCTS. 

**AlphaProof [Unconditional, Peer-Reviewed]**
AlphaProof's capabilities were initially ANNOUNCED-NOT-PUBLISHED via a DeepMind blog post on July 25, 2024 [cite: 1]. The definitive PEER-REVIEWED publication occurred on November 12, 2025 in *Nature* (Hubert et al., "Olympiad-level formal mathematical reasoning with reinforcement learning", DOI: 10.1038/s41586-025-09833-y) [cite: 2, 3, 13]. 
*   **Theorem/Result Statement:** The primary source states, "At the 2024 International Mathematical Olympiad competition, our AI system, with AlphaProof as its core reasoning engine, solved three out of the five non-geometry problems, including the competition's most difficult problem... Combined with AlphaGeometry 2, this performance... resulted in reaching a score equivalent to that of a silver medallist" [cite: 3].
*   **Distinct Coordinates Identified:**
    1.  **Test-Time RL (TTRL):** The system isolates inference-time scaling as a separate operator from training. AlphaProof "uses test-time RL, a method of generating and learning from millions of related problem variants at inference time to enable deep, problem-specific adaptation" [cite: 3]. 
    2.  **Product Nodes:** Standard search uses OR nodes (where proving one child proves the node) evaluated by visit-count weighted averages. AlphaProof utilizes a **Product Node** (AND node), structured such that "the probability of finding a proof for a product node is the product of the probabilities of finding proofs for all its child nodes" [cite: 7]. During back-propagation, "every time we pass a product node we back-propagate the value of the hardest branch" [cite: 7].

**Behavior Delta:** [SUBSTRATE_OP: PRIMITIVE_REGISTRATION]. Register HTPS (AND/OR hypergraph evaluation) and AlphaProof Search (Product Nodes + TTRL) as distinct operational spaces in the neural theorem proving catalog. Do not collapse them under the single umbrella of "MCTS."

## (b) FOLLOW-ON WORK (2024-2026)

During the 2024-2026 window, the literature experienced a rapid proliferation of automated formal reasoning models. Substrate monitoring must track these to identify when AlphaProof's or HTPS's methodologies are superseded, refined, or fundamentally challenged.

**1. BFS-Prover (ByteDance Seed) — The MCTS Counter-Thesis**
*   **Date:** February 24, 2025 (arXiv: 2502.03438) [cite: 6, 8].
*   **Finding:** BFS-Prover establishes an anti-gravitational well against the prevailing narrative that complex MCTS and critic/value networks are strictly necessary for formal theorem proving [cite: 6, 8].
*   **Coordinate Space:** Utilizes length-normalized Best-First Search (BFS) combined with Direct Preference Optimization (DPO) applied to Lean 4 compiler error feedback [cite: 6, 8].
*   **Unconditional Result:** "BFS-Prover achieves an accumulative score of 72.95% on the MiniF2F test set, surpassing all state-of-the-art theorem provers in the literature, including DeepSeek-Prover-V1.5, InternLM2.5-StepProver, and HunyuanProver" [cite: 6]. It explicitly challenges the MCTS paradigm by demonstrating that a deterministically filtered BFS (eliminating problems solvable by single-node beam expansion) forces deeper policy exploration without the overhead of a critic model [cite: 6, 8].

**2. DeepSeek-Prover-V2**
*   **Date:** April 30, 2025 (arXiv: 2504.21801) [cite: 14, 15].
*   **Finding:** A 671B parameter Mixture-of-Experts (MoE) system designed for Lean 4 theorem proving [cite: 14, 15, 16]. 
*   **Refinement:** DeepSeek-Prover-V2 refines the reinforcement learning paradigm by utilizing "Reinforcement Learning for Subgoal Decomposition." Instead of purely relying on step-by-step MCTS tree expansion, it introduces a cold-start pipeline synthesizing proofs via a chain-of-thought (CoT) alignment, effectively merging informal mathematical reasoning space with formal execution space [cite: 15, 16]. 
*   **Premature Claim Flag:** Follow-on blogs assert DeepSeek-Prover-V2 "establishes a new standard... well ahead of prior neural provers" [cite: 17]. Substrate processors must weigh this against BFS-Prover and AlphaProof evaluations across distinct benchmarks (MiniF2F vs IMO vs PutnamBench), as performance is highly dependent on computational inference budgets (Test-Time compute scaling) [cite: 6, 8].

**3. Nanoproof (Open Source Replication Pipeline)**
*   **Date:** April 25, 2026 [cite: 18].
*   **Finding:** An active open-source replication attempt of the AlphaProof/HTPS architecture utilizing the LeanTree extraction from Mathlib [cite: 18].
*   **Implementation Delta:** Nanoproof specifically implements distributed MCTS-based provers and off-policy RL acting against a LeanTree server [cite: 18]. It remains at an intermediate capability (38.5% on MiniF2F as of April 2026), demonstrating the non-trivial implementation chasm between standard MCTS deployments and Google DeepMind's proprietary Product Node / TTRL architecture [cite: 7, 18].

**Behavior Delta:** [SUBSTRATE_OP: ANTI_ANCHOR_PIN]. Pin BFS-Prover as an explicitly weighted alternative to MCTS/AlphaProof in the substrate. If the substrate requests a routing path for a mathematical proof task, it must evaluate `PATH_A: Length-Normalized BFS (BFS-Prover paradigm)` simultaneously with `PATH_B: Test-Time RL over Product Nodes (AlphaProof paradigm)`.

## (c) FALSE-FORM RECURRENCE

The substrate is highly susceptible to semantic drift caused by low-fidelity abstraction in the general literature. Searching the 2024-2026 corpus reveals several instances of false forms being asserted, validating the need for rigorous anti-anchor placement.

**False Form 1: "AlphaProof solved the IMO using purely formal methods."**
*   **Recurrence:** Secondary media and survey literature often summarize AlphaProof as "solving the IMO" (e.g., "AI solves IMO problems at Silver Medal Level" [cite: 1]).
*   **Correction/Anti-Anchor:** AlphaProof solved the Algebra and Number Theory problems (P1, P2, P6) [cite: 19]. It did *not* solve the Geometry problem (P4 was routed to AlphaGeometry 2) [cite: 1, 20]. Critically, it completely failed on the Combinatorics problems (e.g., P5) [cite: 1, 21]. 
*   **Structural Reason (Actionable):** Formalizing open-ended combinatorics configurations into Lean results in an explosion of axiomatic requirements that humans typically bypass via natural language "handwaving" [cite: 21]. The inability of the LLM to generate plausible formal tactics for combinatorics topologies effectively strands the search mechanism at the root node [cite: 21].

**False Form 2: "AlphaProof's tree search is a standard MCTS."**
*   **Recurrence:** Various blog posts and overviews collapse the search algorithm, stating "AlphaProof uses a pre-trained language model + MCTS (Monte Carlo tree search)" [cite: 21, 22].
*   **Correction/Anti-Anchor:** As specified by researchers involved in AlphaProof, a standard OR-node MCTS calculates probability as a visit-count weighted average [cite: 7]. AlphaProof necessitates an *AND-node (Product Node)* architecture to handle Lean's induction splitting [cite: 7]. Failing to enforce this distinction in the substrate will result in incorrect reward back-propagation topologies during agent training [cite: 7].

**False Form 3: "Scaling MCTS is the only path to advanced Neural Theorem Proving."**
*   **Recurrence:** The sheer momentum of AlphaProof has created a gravity well where "MCTS-guided move selection" [cite: 23] or "Monte Carlo Tree Search" [cite: 24, 25, 26] is viewed as a prerequisite for automated theorem proving.
*   **Correction/Anti-Anchor:** The 2025 release of BFS-Prover strictly negates this [cite: 6, 8]. The authors note that standard models "rely more on the complex Monte Carlo tree search (MCTS) or value functions to guide the search process. However, these approaches introduce additional computational costs and system complexity... BFS-Prover from the ByteDance Doubao (Seed) team challenges this paradigm... proving for the first time that, with a sound optimization strategy, a simple BFS method can outperform mainstream sophisticated search algorithms such as MCTS and value functions" [cite: 8]. 

**Behavior Delta:** [SUBSTRATE_OP: TRAINING_CORPUS_FILTER]. Deploy text filters during ingestion of mathematical survey literature (2024-2026). Texts conflating "AlphaProof" with "universal IMO solution" or "standard MCTS" must trigger a warning flag and be down-weighted relative to primary sources explicitly detailing Product Node architecture and domain failure boundaries (Combinatorics).

## (d) RECOMMENDATION

Based on the primary source confirmation and 2024-2026 forensic tracking, the candidate anti-anchor **"AlphaProof + HyperTree Proof Search (HTPS) forensics 2024-2026 — IMO-medal MCTS over Lean tactics"** needs severe refinement before ingestion into the long-term Wave-7 paradigm.

**(i) Anti-Anchor True Form Refinement:**
The candidate needs **inversion and fragmentation**. 
*   *Current Form:* AlphaProof + HTPS = IMO-medal MCTS over Lean tactics.
*   *Refined Form (Fragment A - AlphaProof):* AlphaProof (Nov 2025) operates over Lean 4 using **Test-Time RL** and **Product Nodes** (where child probabilities multiply, dictating back-propagation of the hardest branch) [cite: 3, 7]. It fails on open-ended combinatorial formalization [cite: 1, 21].
*   *Refined Form (Fragment B - HTPS):* HTPS (May 2022) is an distinct precursor algorithm utilizing unexpanded leaf-selection on **AND/OR hypergraphs** [cite: 4, 5]. 
*   *Refined Form (Fragment C - Anti-MCTS Gravity Well):* MCTS/value-networks are unconditionally non-mandatory for SOTA formal reasoning; **Length-Normalized BFS + DPO compiler feedback** (BFS-Prover, Feb 2025) provides an equally weighted, computationally lighter search coordinate [cite: 6, 8].

**(ii) New Sub-Anchors Discovered:**
1.  **[SUB_ANCHOR: REWARD_BACKPROP_TOPOLOGY]**: Register the distinction in back-propagating tree search values. Normal MCTS back-propagates intermediate rewards along the path. AlphaProof Product Nodes back-propagate *only the value of the hardest branch* (the branch with the lowest probability of proof) [cite: 7].
2.  **[SUB_ANCHOR: SYNTHETIC_COLD_START_ALIGNMENT]**: Register the DeepSeek-Prover-V2 (Apr 2025) architecture, which utilizes MoE LLMs to map informal math chain-of-thought into formal subgoals *prior* to initiating RL tree search [cite: 15, 16].
3.  **[SUB_ANCHOR: LEANTREE_EXTRACTION]**: Note that 2026 replication efforts (e.g., Nanoproof) rely on extracting supervised transitions from Mathlib into a format called `LeanTree` to interface with RL environments [cite: 18].

**(iii) Additions to the Verification Queue:**
*   [WORK_QUEUE_ENTRY_1]: Execute a dedicated coordinate verification on "Test-Time RL (TTRL)". Verify how inference-time problem variant generation structurally differs from expert iteration [cite: 2, 3].
*   [WORK_QUEUE_ENTRY_2]: Execute a formal limitation audit on Lean 4's applicability to combinatorics. If Lean 4 structurally resists combinatorial open-endedness, the substrate must route future combinatorial primitives to non-Lean mathematical action spaces (e.g., direct LLM Python scripting or alternative topological verifiers) [cite: 21].
*   [WORK_QUEUE_ENTRY_3]: Verify the cross-benchmark validity of PutnamBench vs MiniF2F. DeepSeek-Prover-V2 relies heavily on PutnamBench resolutions [cite: 15, 16], while BFS-Prover grounds its SOTA claims strictly in MiniF2F [cite: 6, 8]. Substrate must calibrate the weight of these benchmarks.

**Downstream Execution:**
Proceed with `P_CANDIDATE_AlphaProofForTensorSubstrate` registration, but apply a HARD-5 matrix ensuring HTPS, MCTS, BFS, and Product Node searches exist as individual mathematical dimensions inside the vector space. Resist the literature's gravity well collapsing them into a single node.

**Sources:**
1. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFchXULDkvzBodfN67bmDWnZzf5lzIhPUQBsXLLhc68rDaUMzv_Cy_ZI517dbNV4TF511B2eh4dkrq4PL53TRMh2I-HHnrzfrSmPGqomhk67wZhxQUcesNwoZq7NI6EkSDOUWHByCQt3HZFnRyP9dwgg_TVNWHw8bYYpMAwdXxDnQ==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3PpO3JuvDasHHz_zga7EA1ZU_2cqMgYkKlVXi_4hYEztaY4aN2DJwyBGwUyJWSbtL64kSZMtY5X-C5QO8WtuWJP2u7vsdBuQwDCjpUw-fB0gIO6K5ULtJyid-0TNON_deuFXPPVGgJZwy1BPnjqBDqKqTaVE864j2IppwbGIJOTd08z80ufY0b-5IeTCcI6gd4MVeg2ocW3ZugDA4oGrmNTThCk7hRIgjvww3wp1fuy0=)
3. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOMuczht8r0C99WQavt0fxuTDyT5bNSBTTL6sablniv6wL_hoAbBmf9IMMV6KkfDBiPA4KUjr69ccmF6kI8uqQBCFeiA7xI1n8oW50u6ahQE_YyRvyCJOnus5C3tyKoA==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEaatQSIYh3RG9Hgkjuxiuo82IwRwr15ZtqgLGdodxmMiYjvdfEEbDWdwX7i8iheiOxi0Uc2wCVu-W4wjWCKa40lmMmB7NhbM9xokW9E9xB3qd4M0EOw==)
5. [dauphine.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgInMLZ3mSw73dXgLk-UHdgoWgut-GULY_KndWPCLxlNUrcO-3iO8mDjzQS-ffVDvFBxvUyKACJ9GLdaRbF3adGxVvlAjvON4RYTkLdl-ZCHImYOo7TdbSH0Ahli_0oyhBF2O0yP6EL6SI2qPBWPPwFE7y7Pj0pZY9SoDtyJQ=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4cSLWlnvMB79e9FMTpPXU5tSMi-sGotTMVSm04UIlcirjyRkhqHX3J49uXsDF8xbQKGEsvGLc-Tm4_eE4gFmggvnU0uyAnxYdGuW69rpZXk3tnFRQRIJgBg==)
7. [julian.ac](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuWWLBKm2TzZpmeTjQhwir-z1UKqmQAr_IhcOEEaNvBPaY65BqVw0NnxGi7-Nni1xCjm-VZylpgO7R04NxDxj7KJbh7rmBQRz8H_NTUnfb7ahYJry7XGB2MzXVcT8diYf3k5wBLzI9guMO1UNo)
8. [bytedance.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHyTOoBi84ITBwzqtPRIuumXpyyaXeAFyl_E6Gk6gBJnjJC0BTnA1iODCtpQM7TW8Y7Wep1Ep8AeMgNqFDvS0wm-gAG-MMt4kWaY5OpfR74ZxQDqYcFUDDvUYEPMYFpe7LpWbsVPzX7v7zDPCLvSAWHkoYkVuNiEPcqJLNJ-my4AP2uMlPrUb3Ku_bWhFjdhQfIHr3mTt87O2K93TCn6vw5Uy3m7PQYGBQJXYucq3B)
9. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEshkU859RB9OHEv2-C0nyxJV-KfNplpU_hoSqZLEq23mkepbrGUdP24BOla_IFQCIKvabKdojOaUYmCKOYls-N7hpgIgiXqxQdlx9nBguRwlEZ2LDWb8E-13y9_unWsSWFfagBXCfWE2LNmYdmnqGOEnR8QOrrj61f6SCyDgRlvT_GVWKHkZux07K_NEvOYGshlrWR-kWb1UEmOCPAd1_fkYblbzyBxei78QBhuWTMvWET1bkqkImmte0E3dkLHPFp4uBTMrk=)
10. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTXOOIB8J9FzGb-c4Xl1tEckEzGsK9HF6_-W5j5sucw08y32Tn9uQzk14bBehc_zNF4SYSgmySvhyDOQ8UOPECljhdjG8rWVAxqzypOSm5_4VtTqwrHt7iv_koRsNEenei)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBJRJOY5he02BT0D6AERIZ6G_H6nCWrkN28Qky0xLecZiYv0jYDEPFBftv5P_k5NqbylF00uPAwob4reYZFoTchZdpWF0OOw8ud6pkBLveu6Mz0-TZ8g==)
12. [enpc.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHb9I61fC7Xp_is6u2xHXnZdJHxWxFcnX6DezBVctSdoB2cV5hH1Aj3RdvThrcK9hVI4t8bNKrp8mrKoBsN7po4Q7bTO-gg_5B7RFYaym7ATUYiW3NoQBZ_jdUJqt9CS8Uy)
13. [natureasia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXfrb9xILFeFzUYsvK5SvLc69FiTCxJX4ymeNzRlUMlFgL1iZSmKRImP75lJpxEOSb2oMbzXWdp8EKboTj1Hme4d5abhakisq-yI0CBKIEGHtgHIM1drNfjb5QQ9irL39ACB-VnNQYFXKMszMNkVOK3RZf)
14. [prover-v2.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEL_FE76LsC4cix7byPtHEvA70GoTJt9XYVt9J2SvFSwRNhVYyn_qMF_1DMaU6WBmyMw1-HGnTsNLmUD1Y0VoEP_PVUXZJBjxWxcRaY)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaOJ98_PeD4pYSGLVEFGWLSw5RAzpG5EAVDV2uv0kbR__t8wvPkKaKCcovmXWdJPJja6et3qvckx00iYzJq0QQg4aHSruj7iIN4PU5Qgm4Y3vVqKO9SQ==)
16. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEePO97KllWyB_FsBslgNd8KMERe-sLXQ0FpvLQwSk3GWyyIYlA5BEewwimlOn8lsl_8O3pZuWoHl5MhhCqHO9BDuakd1lAMof2mBnAMYpV3DzGkfiOLTliJvEjYK0PG1UjeACCkVic)
17. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_MAujXu61MkWa4kehO5nyW3CIDjWmP00bIaui6UBCP261_uKxL0An55pCxLfwlPUNmsygAN9I_DyIRwNF8n8apbEcZcBPiOBbynHt55m83svjxwn5bXlUjqM4ZoHuwZKnVdVBDYrg9NvOojdHFFc1gwljhzxU_BURM3MrVdtu1hbl-TzLW9H2IgNIO2PMIJm-2cbrj78M_757JgZbAdCIiw==)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-9OxlWbyPhWdAd4rRfeFMNieOVzTBRZe9skDW9TitQMlf4Cgz5BeMdK9kCkvZM-IcN-o7H8jVXcvInQEP5tTrtmdWbzccJQNsNoRvZIA3YCTzMF0x58GRqLI=)
19. [startuphub.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDJewy_8Dv1ACut3lbwXiVIcL-clcjUkdCM6HbKeZQeVgG21XJIxNCC88cSpdEdmxMJS6o4aW9wXsMeYKoefAPsEy9VFFx05yNUr70w3Xw9N8eFSn2ggGfILerCw-XXXm391lJRgnu2XFb0B_3K5VYxC-S3ezMRES35cuvFHypLyIZPNFZJM6vl8p2jBErzvwQYlY_4TWiHELrk2xp6zoC)
20. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4k92rqjcdq8iOQo4SnmKs5MaStw0-ChGRST13DuX-8OSHJkBQJlnRZ1cS5NrF4okOGWufpxKHfxhg7wxAkUH8p033sD5mQ1mZPoQtwPgblCuWm31_YHZMzlouuQ4b-jTJFflo0Vg9Aw==)
21. [ycombinator.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuxUsWIQSkfjp1t-yDqhXlUdegTB9ai4hUiTX921uS7HU_wd2fuV02TVyl7SEKaLrgBnrk18mJKUS4HWyxx5l9uEjsG_8EQN1Dg19B66THm7TFtp8XD2C5wnXeQnziDjuOf9c=)
22. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqet3aH83syC5WfbiQKaOrTrXxBBETPL0ZnLXBw15en00yY0vJ1bHf0o7gL_7hWtj-jX4UMUjfQW4eXOFWj_xL-ZrvM2Kcx6MvxDld8bmOSANGIdGVClODX1tN0cGJSuI4vAnOvZqRP19sgg==)
23. [theorempath.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHag_68Wxu-uwIpUk-sMOYmyQmBqf6f8ffKYRhiPPwrK8JSdmZNRF9KQogJpkdft4xUgoJRRYtV_oJTH04wFmr2wkIImN3XAXPYwNyCo8lCcsHCRYEf_M2FyiWlmivwsbrTYH-9-tEBfXsa_NdcIj_gOuvGvHC4)
24. [aitp-conference.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOItMhreqi9VqN5_9shaKlCIwAOyFniZNlDbiFJFWCKZPcAVdVvDnfzvApW-hjY-YtHou5t3ICED2C_K1u0sCfM_b-wmF003uh8ohTGkz7YERozoF8OWRe1Y6U6hvYoVOwpLfV)
25. [nagoya-u.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVA0COcOORBQbvX87er4MQEQS4si63jZ37_6hvtq_mF3IyYfbOx8w9KA8fL05hLH9fzlkSOI47A2-_Cf5dmtxG5yzFoG2Sk29cQdBo7l8zW42rydbjm9UvporfY8EaSspgk9G-6tDx8Iu09a4_GV5qnWerllC6n-rw)
26. [aitp-conference.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsdYdDAkU6WxSNJni4HfIVIX7iN6LB6DZpiXxdpTUu0-U8QK8cGAvKKwZorfAOr3l3ElZ7hx8UCaBqgPqnYx9HIbzn6ibZC8A3TQDkzzCcMYbVKbbN85k6L6ldIofBiqdYv6oUH59j793UiDI-NjC5tYZKa3Q=)


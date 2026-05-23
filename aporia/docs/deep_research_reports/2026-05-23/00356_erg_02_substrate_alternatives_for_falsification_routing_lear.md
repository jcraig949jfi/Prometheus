# ERG-02: Substrate alternatives for falsification-routing-Learner training

**Pythia queue id:** 356
**Tier:** T4
**Priority:** 4
**Requested by:** Ergon
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdoTTRSYXRpbUpNQzlfdU1QckxtcjRBdxIXaE00UmF0aW1KTUM5X3VNUHJMbXI0QXc
**Elapsed:** 790s
**Completed at:** 2026-05-23T16:11:07.740629+00:00

---

# Substrate Reassessment and Falsification-Routing Corpora: Overcoming the Walk-1 Paradigm Ceiling

**Key Points**
*   **Architectural Saturation:** The observed 2000-record scaling saturation in Walk-1 indicates that tabular representations of local proof states (15-macro operator catalog) fail to capture the hierarchical, non-Markovian dependencies inherent in mathematical falsification.
*   **Structural Diversity:** Sole reliance on Lean 4's `mathlib4` limits syntactic and strategic diversity; incorporating Isabelle/HOL's declarative Isar style offers a significantly different structural distribution for ML routing.
*   **Falsification Scarcity:** Standard proof corpora inherently lack negative signals. Emerging 2024–2026 datasets like CounterMATH and FormalRewardBench explicitly pair false claims with counterexamples or systematic proof failures, providing the required dense signal for kill-vector regression.
*   **Paradigm Shift:** The ML routing objective should likely shift from deterministic next-macro classification to continuous state-flow estimation (Generative Flow Networks) or Process Reward Modeling (PRM), which empirically bypass the 2-Markov trajectory context barrier.

**Context and Complexity**
Research suggests that while interactive theorem provers (ITPs) like Lean 4 enforce rigorous step-by-step logic, the linear tactic sequences they produce are opaque to shallow ML architectures like MLPs and gradient-boosted trees. It seems likely that the ceiling Daedalus hit is not merely an artifact of data quantity, but a fundamental mismatch between tabular feature extraction and the underlying topological structure of proof search. The evidence leans toward the necessity of explicitly modeling proof failures, dead-ends, and counterexamples to train a robust falsification-routing Learner. While the integration of multi-language corpora (Isabelle, Coq) and synthetic failure datasets introduces domain-shift complexities, these resources are practically indispensable for overcoming the current 15-way classification ceiling.

---

## 1. Introduction: Analyzing the Walk-1 Substrate Saturation

The Daedalus Walk-1 substrate, built upon a 5000-record batch of `mathlib4` proof traces, has empirically hit a learning ceiling. The baseline metrics—a marginal +0.064 mean R² on kill-vector regression and a +0.092 accuracy lift in 15-way next-macro classification—demonstrate that traditional tabular ML methods (Linear Ridge, GBTs, MLPs) struggle to extract deep semantic routing signals from localized proof states. 

Crucially, the observation that pure data scaling saturates past 2000 records and that trajectory context past 2-Markov adds no predictive power points to a fundamental substrate mismatch. Proofs in Lean 4 are constructed via sequences of tactics that manipulate an underlying, highly complex abstract syntax tree (AST). Tabularizing these states inevitably destroys non-local topological symmetries. Furthermore, `mathlib4` represents a corpus of *successful, heavily refactored* proofs. It is a repository of survivorship bias. Training a falsification-routing Learner (a model designed to identify dead-ends, prune search trees, and estimate kill-vectors) strictly on successful paths is akin to training a diagnostic classifier entirely on healthy patients. 

To refine the paradigm (Substrate Type C), we must reassess the primary corpus and the target learning task. This document systematically evaluates the 2024–2026 frontier of formal proof corpora, counterexample datasets, failure-mode registries, and alternative ML optimization targets. The goal is to identify a complementary or replacement substrate that carries a strongly learnable falsification-routing signal, ultimately driving the Walk-3 scope expansion.

---

## 2. Cross-System Formal Proof Corpora (2024–2026)

Beyond `mathlib4`, the landscape of formalized mathematics encompasses several highly mature systems. The primary question is whether systems like Isabelle/HOL, Rocq (Coq), Metamath, or HOL Light are **structurally different** enough from Lean 4 to produce distinct next-macro and kill-vector distributions. 

### Structural Discrepancies and Proof Styles
Lean 4 proofs predominantly utilize a procedural, tactic-based style where atomic commands sequentially mutate the proof state. While Lean supports declarative elements, `mathlib4` is heavily optimized for brevity and tactic chaining [cite: 1, 2]. In contrast, Isabelle/HOL natively supports two distinct proof styles: the procedural `apply`-style and the declarative `Isar` style [cite: 1, 3]. Isar provides a hierarchical, human-readable framework where the intermediate logical propositions are explicitly stated. 

This structural difference is profound for ML. In Lean, the "next-macro" prediction is often an opaque state-transition operator (e.g., `simp`, `rw`). In Isabelle's Isar, the next step is often a structured logical assertion (e.g., `assume`, `have`, `show`). Training on Isar would shift the ML routing target from *operator vocabulary prediction* (rewrite-heavy) to *intermediate lemma prediction* (deduction-heavy). Coq (Rocq), based on the Calculus of Inductive Constructions, strongly emphasizes structural induction and case analysis, generating fundamentally different proof trees compared to higher-order logic systems [cite: 2, 3]. 

Recent cross-system benchmarks like PutnamBench have explicitly highlighted these structural disparities. PutnamBench provides 1,697 formalizations of 640 competition-level theorems across Lean 4, Isabelle, and Coq [cite: 4, 5]. Evaluated ML models exhibit highly variable success rates across these languages due to the differing granularities of their macro-operator vocabularies [cite: 4, 6].

### Argos Canonical Structure: Cross-System Corpora

*   **(a) Measurement Projected:** Variance in the operator frequency distribution (entropy of the next-macro target) and the structural depth of proof trees across different Interactive Theorem Provers (ITPs).
*   **(b) Verdict Reached:** **Pivot to a Hybrid Substrate (Lean 4 + Isabelle/HOL).** `mathlib4` is insufficient for capturing declarative proof strategies. Incorporating Isabelle's Isar proofs will expose the routing Learner to explicit intermediate-state generation, diversifying the 15-macro catalog with structural deduction steps. 
*   **(c) Axis of Disagreement:** Proponents of pure-Lean scaling argue that Lean 4's metaprogramming capabilities can auto-generate declarative steps, making multi-system parsing redundant. However, empirical data shows that cross-system structural diversity provides orthogonal signals that monolithic corpora lack [cite: 1, 5].

### Candidate Corpora and Citations

| Corpus / Benchmark | Description & Record Count | Public URL / DOI | License |
| :--- | :--- | :--- | :--- |
| **PutnamBench** | 1,697 formalizations of 640 theorems across Lean 4, Isabelle, Coq. | 10.48550/arXiv.2407.11214 (Public) [cite: 4, 5] | MIT |
| **MiniF2F (Cross-System)** | 488 Olympiad-level problems in Lean, Isabelle, HOL Light. | 10.48550/arXiv.2109.00110 (Public) [cite: 7, 8] | MIT |
| **FormalMATH** | Large-scale undergraduate mathematics benchmark across systems. | 10.48550/arXiv.2505.02735 (Public) [cite: 8, 9] | Apache 2.0 |

*Citations validating structural distribution comparisons:*
1. Tsoukalas et al. (2024). "PutnamBench: Evaluating Neural Theorem-Provers on the Putnam Mathematical Competition." *arXiv:2407.11214*. DOI: 10.48550/arXiv.2407.11214 [cite: 4, 6].
2. Drori et al. (2025). "HybridProver: Automating Formal Proof in Isabelle." (Noted within [cite: 1] discussing the 200K theorem scale of Isabelle vs Lean's 140K, detailing Isar vs apply-style distributions). 
3. Zhang et al. (2025). "Psychometric frameworks for formal theorem proving." *arXiv:2508.15878*. DOI: 10.48550/arXiv.2508.15878 [cite: 7, 10].

---

## 3. Falsification-with-Counterexample Corpora (2024–2026)

To map a 12-dimensional semantic-content kill-vector, the ML Learner requires explicit, high-quality examples of mathematical falsification. A false claim must be paired with the exact sequence of steps (or the construction of the mathematical object) that refutes it. Standard formal libraries do not preserve false claims.

Recent breakthroughs in 2025–2026 have directly addressed this. The most prominent is **CounterMATH**, a dataset consisting of 1,216 university-level statement-rationale pairs focused entirely on disproving statements using counterexamples [cite: 11, 12]. CounterMATH spans Algebra, Topology, Real Analysis, and Functional Analysis [cite: 13, 14]. It was constructed to explicitly test LLMs on their ability to perform example-driven conceptual reasoning rather than drill-based forward theorem proving [cite: 14, 15]. In CounterMATH, models must propose candidate counterexamples and generate formal proofs verifiable in Lean 4 [cite: 16, 17]. 

Another highly relevant corpus is **WithdrarXiv**, the first large-scale dataset of withdrawn papers from arXiv, containing over 14,000 papers and their associated retraction comments [cite: 18, 19]. While not fully formalized, this dataset contains explicit natural-language reconstructions of contradiction proofs and methodology failures [cite: 18, 20]. Furthermore, **ArgBench** provides a Lean-based benchmark for abstract argumentation, specifically evaluating a model's capacity for novel concept understanding and counterexample construction [cite: 21].

### Argos Canonical Structure: Counterexample Corpora

*   **(a) Measurement Projected:** The magnitude of the regression signal (R² lift) on the kill-vector battery when training on explicit (false_claim, counterexample) topographies.
*   **(b) Verdict Reached:** **Pivot decisively to CounterMATH and ArgBench.** These datasets provide the exact topological structures (proofs by contradiction, counterexample instantiation) missing from `mathlib4`. Integrating CounterMATH will shift the kill-vector from a synthetic proxy to an empirical target.
*   **(c) Axis of Disagreement:** One could argue that synthesizing counterexamples dynamically via LLM mutations (as proposed by Li et al. [cite: 17, 22]) is more scalable than relying on curated datasets like CounterMATH. However, the manually curated baseline of CounterMATH (1,216 pairs) prevents the hallucination cascades inherent in purely synthetic counterexample generation.

### Candidate Corpora and Citations

| Corpus / Benchmark | Description & Record Count | Public URL / DOI | License |
| :--- | :--- | :--- | :--- |
| **CounterMATH** | 1,216 university-level mathematical claims requiring counterexamples. | 10.48550/arXiv.2502.10454 (Public) [cite: 12, 23] | CC BY-SA 4.0 |
| **WithdrarXiv** | 14,000+ withdrawn arXiv papers + retraction taxonomies. | 10.48550/arXiv.2412.03775 (Public) [cite: 18, 19] | Open Access |
| **ArgBench** | Lean-based benchmark for abstract argumentation and counterexamples. | Submitted to ICLR 2026 (Public via OpenReview) [cite: 21] | CC BY 4.0 |

*Citations validating falsification datasets:*
1. Li et al. (2025). "One Example Shown, Many Concepts Known! Counterexample-Driven Conceptual Reasoning in Mathematical LLMs." *arXiv:2502.10454*. DOI: 10.48550/arXiv.2502.10454 [cite: 11, 12].
2. Li et al. (2026). "Learning to Disprove: Formal Counterexample Generation with Large Language Models." *arXiv:2603.19514*. DOI: 10.48550/arXiv.2603.19514 [cite: 17, 22].
3. Chen et al. (2025). "ArgBench: A Lean based Benchmark for Automated Theorem Provers on General-Purpose Reasoning Tasks." *OpenReview* [cite: 21].

---

## 4. Proof-Failure / Dead-End / Repair Corpora (2024–2026)

Daedalus's Walk-1 failed to map trajectory context past 2-Markov because it only observed successful, highly optimized paths. To train a routing model to avoid dead-ends, it must see the dead-ends. 

Recent literature has systematically categorized LLM proof failures. The **RFMDataset (Reveal Failure Modes)** contains 200 diverse mathematical proof problems specifically annotated for 10 fine-grained reasoning failure modes, including "Logical Violation," "Over Generalization," and "Circular Reasoning" [cite: 24, 25]. This provides a precise semantic taxonomy for Daedalus's 12-dimensional kill-vector. 

Even more directly applicable to the substrate design is **FormalRewardBench**, which takes verified Lean 4 proofs and systematically injects verifiable errors (e.g., Forced Mistakes, Minimal Single-Point Variations, Verbose Incorrect Proofs) [cite: 26]. These variants remain syntactically valid and plausible to LLMs but fail Lean type-checking, mimicking exact real-world dead-ends [cite: 26, 27].

Additionally, the **Coq Proof-Repair Dataset** comprises Git commits from open-source Coq projects, aligning old (broken) versions of definitions and proofs with new (repaired) versions across commits [cite: 28]. In the domain of optimization, **OptBench** details specific strategic dead-ends where models generate syntactically valid but strategically aimless steps (e.g., breaking the structural integrity of an inequality), leading to unprovable subgoals [cite: 29].

### Argos Canonical Structure: Proof-Failure Corpora

*   **(a) Measurement Projected:** The classification accuracy of distinguishing a terminal dead-end state from a recoverable state at a horizon of $H \geq 3$ steps.
*   **(b) Verdict Reached:** **Incorporate FormalRewardBench and RFMDataset into the primary routing training.** These datasets explicitly model the "plausible but doomed" trajectories that confuse tabular models. FormalRewardBench provides the exact negative state-transitions needed for kill-vector regression.
*   **(c) Axis of Disagreement:** Contrast with traditional Reinforcement Learning (RL) approaches, which argue that negative signals should be generated *online* via the agent's own exploration (e.g., DeepSeek-Prover RL [cite: 30]). Relying solely on online self-generated failures often leads to shallow syntax errors rather than deep strategic dead-ends. Curated datasets provide higher-quality semantic obstructions.

### Candidate Corpora and Citations

| Corpus / Benchmark | Description & Record Count | Public URL / DOI | License |
| :--- | :--- | :--- | :--- |
| **FormalRewardBench** | Lean 4 proofs with 5 distinct injected verifiable error typologies. | 10.48550/arXiv.2605.10141 (Public) [cite: 26, 27] | CC BY 4.0 |
| **RFMDataset** | 200 proofs annotated with 10 fine-grained failure modes. | 10.48550/arXiv.2506.17114 (Public) [cite: 24, 25] | MIT |
| **Coq Proof-Repair** | Git commit pairs aligning broken Coq proofs with human repairs. | 10.4230/LIPIcs.ITP.2023.26 (Public) [cite: 28] | Open |

*Citations validating failure/repair datasets:*
1. Guo et al. (2025). "Mathematical Proof as a Litmus Test: Revealing Failure Modes of Advanced Large Reasoning Models." *arXiv:2506.17114*. DOI: 10.48550/arXiv.2506.17114 [cite: 24, 31].
2. Uluşan et al. (2026). "FormalRewardBench: A Benchmark for Formal Theorem Proving Reward Models." *arXiv:2605.10141*. DOI: 10.48550/arXiv.2605.10141 [cite: 26, 27].
3. First et al. (2023). "Diversity-driven automated formal verification" / Coq proof-repair dataset. DOI: 10.4230/LIPIcs.ITP.2023.26 [cite: 28].

---

## 5. Multi-Method Same-Theorem Corpora (2024–2026)

To train a robust next-macro distribution predictor, the model must understand that there are multiple valid paths through the proof search space. If a corpus only provides one proof per theorem (like the standard `mathlib4`), the model is penalized for suggesting mathematically valid alternatives, forcing it into a brittle, mode-collapsed state.

**MUSTARD** (and its dataset **MUSTARDSAUCE**) introduces a framework for uniform synthesis of theorem and proof data, generating 5,866 data points containing informal statements, informal proofs, and translated formal Lean proofs [cite: 32, 33]. Crucially, frameworks like MUSTARD and the **Goedel-Prover-V1 / V2** pipelines use expert iteration and LLM sampling to generate *multiple proof candidates* for the same theorem [cite: 34, 35]. During the creation of the `Goedel-Pset-v1` dataset (1.64 million formal statements), the pipeline explicitly samples up to 16 proofs per statement using DeepSeek-Prover-V1.5 [cite: 35]. 

The **miniF2F-Lean4** alignment datasets also exhibit multi-proof characteristics, as the community continually submits novel, shorter, or conceptually different proofs for the same Olympiad problems [cite: 36, 37]. Furthermore, the **Conjecturing-Proving Loop (CPL)** explicitly studies the generation of multiple proofs for auto-formalized statements, shifting the distribution of generated theorems closer to the true distribution of provable statements [cite: 38].

### Argos Canonical Structure: Multi-Method Corpora

*   **(a) Measurement Projected:** Reduction in Cross-Entropy loss for next-macro classification when evaluating against a multi-hot target distribution (valid alternative tactics) rather than a one-hot deterministic target.
*   **(b) Verdict Reached:** **Integrate MUSTARDSAUCE and Goedel-Pset-v1 multi-proof samples.** Transitioning the next-macro target from a single empirical historical step to a smoothed distribution of known valid steps will break the 15-way classification ceiling.
*   **(c) Axis of Disagreement:** The traditional view holds that only the shortest, most elegant proof (the "canonical" proof) should be used for training to optimize inference time. However, for a *routing* learner, maximizing path diversity is critical for recovering from suboptimal initial states.

### Candidate Corpora and Citations

| Corpus / Benchmark | Description & Record Count | Public URL / DOI | Ratio: Multi-Proof / Total |
| :--- | :--- | :--- | :--- |
| **MUSTARDSAUCE** | 5,866 valid formal/informal math pairs. | 10.48550/arXiv.2402.08957 (Public) [cite: 32, 34] | ~1.5 - 2.0 (estimated via generation pipeline) |
| **Goedel-Pset-v1** | 1.64M statements with 16 sampled proofs per solvable statement. | 10.48550/arXiv.2502.07640 (Public) [cite: 35] | Up to 16.0 (for solved subsets) |
| **miniF2F-Lean4** | 488 Olympiad problems with community multi-proofs. | GitHub Repo (Public) [cite: 36, 37] | ~3.0 - 5.0 |

*Citations validating multi-method datasets:*
1. Huang et al. (2024). "MUSTARD: Mastering Uniform Synthesis of Theorem and Proof Data." *arXiv:2402.08957*. DOI: 10.48550/arXiv.2402.08957 [cite: 32, 33].
2. Lin et al. (2025). "Goedel-Prover: A Frontier Model for Open-Source Automated Theorem Proving." *arXiv:2502.07640*. DOI: 10.48550/arXiv.2502.07640 [cite: 35].
3. Sannai. (2026). "Conjecturing-Proving Loop for Theorem Discovery." *arXiv:2509.14274*. DOI: 10.48550/arXiv.2509.14274 [cite: 38].

---

## 6. Alternative Target Tasks (2024–2026)

If tabular ML (MLPs, GBTs) hits a ceiling on next-macro classification, the issue lies not only in the data but in the *formulation of the target task*. Recent literature strongly suggests abandoning deterministic sequence prediction in favor of structure-aware or distributional optimization targets.

### 6.1 Process Reward Models (PRMs)
The **Math-Shepherd** lineage introduces process-oriented math reward models that assign a continuous reward score to *each intermediate step* of a mathematical solution [cite: 39, 40]. Unlike Outcome Reward Models (ORMs) that only score the final state, PRMs provide fine-grained, dense credit assignment. For Daedalus, replacing the 12-dimensional kill-vector regression with a Math-Shepherd-style PRM target leverages automated process-wise supervision without human annotation [cite: 41, 42]. Empirical results show step-by-step PRM reinforcement significantly outperforms sparse correctness signals [cite: 43, 44].

### 6.2 GFlowNet Proof State Distributions
Generative Flow Networks (GFlowNets), developed heavily by the Bengio lab, treat proof search not as sequential classification, but as learning a policy to sample compositional objects (proof trajectories) with probability proportional to an unnormalized reward [cite: 45, 46]. GFlowNets explicitly map out the directed acyclic graph (DAG) of state transitions, ensuring flow consistency constraints (Trajectory Balance) [cite: 46]. In neural theorem proving within Lean, GFlowNet fine-tuning has shown dramatic improvements in exploration and reasoning [cite: 45]. By reframing next-macro prediction as *edge-flow estimation* on a DAG, the model natively overcomes the 2-Markov limitation by intrinsically embedding global trajectory balance [cite: 45, 47]. 

### 6.3 Premise-Selection via Structural Tree Embeddings
Instead of predicting abstract operators, **Mathlib4-Premise-Selection** models reframe the task as retrieving the exact hierarchical lemmas required for the proof state. Recent frameworks explicitly utilize the *structural information* of Lean expression trees—via Common Subexpression Elimination (CSE) trees, Weisfeiler-Lehman kernels, and Tree Edit Distance (TED) metrics [cite: 48, 49]. Training an ML routing model to output structural tree-embeddings rather than tabular macro-classes preserves the topological symmetries of the mathematics, directly answering why tabular MLPs underperformed.

### Argos Canonical Structure: Alternative Target Tasks

*   **(a) Measurement Projected:** Predictive signal magnitude. GFlowNet Trajectory Balance loss vs Cross-Entropy loss; PRM step-level accuracy vs binary outcome accuracy.
*   **(b) Verdict Reached:** **Abandon 15-way Next-Macro Classification. Pivot to GFlowNet Edge-Flow Estimation and PRM Step-Scoring.** The tabular MLP failed because ASTs are non-Euclidean. Transforming the routing task into a GFlowNet continuous action distribution over a proof DAG perfectly aligns with the requirement to navigate and prune massive search spaces.
*   **(c) Axis of Disagreement:** The primary objection to GFlowNets and PRMs is their training instability and high computational overhead compared to simple tabular classifiers [cite: 46]. However, recent advancements in "Stable GFlowNets" [cite: 46] and automated PRM data synthesis (like FOVER [cite: 43]) have mitigated these issues, making them the strictly superior paradigm for advanced ATP routing.

### Citations for Alternative Tasks

1. Wang et al. (2023/2024). "Math-Shepherd: Verify and Reinforce LLMs Step-by-step without Human Annotations." *arXiv:2312.08935*. DOI: 10.48550/arXiv.2312.08935 [cite: 39, 40]. *(Best-reported accuracy: boosted Mistral-7B from 77.9% to 84.1% on GSM8K via step-wise PPO).*
2. Bengio Lab / Associated Authors (2024). "GFlowNet Fine-tuning for Theorem Proving in Lean." *arXiv:2410.13224*. DOI: 10.48550/arXiv.2410.13224 [cite: 45].
3. Niu et al. (2026). "Stable GFlowNets / Generative Flow Networks as Entropy-Regularized RL." *arXiv:2605.01729*. DOI: 10.48550/arXiv.2605.01729 [cite: 46, 47].
4. Liu et al. (2024). "Structure-Aware Premise Selection in Lean 4." *arXiv:2403.13310*. DOI: 10.48550/arXiv.2403.13310 [cite: 48, 49].

---

## 7. Strategic Landing Verdict: Walk-2 Framing C (Substrate Reassessment)

Based on the 2024–2026 literature review, the Daedalus platform must urgently **revisit substrate-design from a different abstraction (proof-as-search-tree, not proof-as-step-sequence).** 

The ceiling observed in Walk-1 is an architectural and target-definition failure, exacerbated by a survivorship-biased corpus (`mathlib4`). Tabular ML over a flat 15-macro catalog discards the hierarchical, DAG-like structure of mathematical truth. 

**Actionable Pivot:**
1.  **Corpus Hybridization:** Deprecate `mathlib4` as the sole primary corpus. Immediately ingest **CounterMATH**, **FormalRewardBench**, and **Isabelle/HOL Isar proofs** (via PutnamBench) to build a substrate rich in explicit falsifications, structural diversity, and verified dead-ends.
2.  **Target Redefinition:** Deprecate the 15-way classification and baseline kill-vector regression. Replace the routing Learner's objective with **GFlowNet Edge-Flow Estimation** coupled with a **Process Reward Model (Math-Shepherd framework)**. This mathematically aligns the Learner's loss function with the topological realities of proof-tree exploration, natively overcoming the 2-Markov context barrier.

This paradigm refinement (Substrate C) directly supports the transition into Walk-3 scope expansion, providing the mathematically rigorous, multi-path, failure-aware substrate required for frontier falsification-routing AI.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1jjwt-Vh0GSChVtsGI4Gq7aoo4MrB5K9A98RUNd7h3UHBQQZj33whHnIikagsJW4z_W763D8MrGbOeL-irTCijhk2W02su9HwTvTvFCEyG5YKw6aT6i55Cw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrVm_MubQkBcboX0ZqDwxAIHcIAhNvlsCPyHeHBoB36MCTdC4WOHqMVtXSALijNmRVILFK4ztSg3llTLwbA9BGtBxTbWgcoTiJzXebg9XpDLeUBaF1HA82yQ==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDVV7cxG5D8_6b-2u2onGd3boL-vm4psX-oA3DfT2mT1frxMfCIJe_p-t_uqruG0FsGVrAPu74ID8jeJj7msr9rosBvkYxbfCmYBLj62PWKuB2HFaLPQ==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfobyC4zQeThLMobE5PJ3u_60JZWMQRcy0FU_a5D7eg4jCyuTSE3kfwkYvDnk5p0aztPylKIgeerRtQeJiQOHSJrbc8_pnc3lfuos1U2m9Xq8guBCZlQ==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXwAWYr9Fm0iLkkx3ohInZnu9_zxrQzLWrmRYU5cZ_lk8XGL-cRBGgeww43yTy11JXUFauBY8Uf3ugTnCp5moppYytuDlf6nOYaJaPb_3cX3uFNGJn7d7zSLxsonEOHczc6fHwCNvi5uc4KDcxn-gz7v5TyvK607KEkIL6gDdx7RMkdmPewE_o78juWknzbaQRKwj_rv3tOv2r6kATLNcF8d7e38Wmd_TmcIALela7C4W0dxjN7bUc_kEV51rl)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbH5HuRq72SUXZxzb6oUq_F9zpytCIlBHkEvdxHSa6X5PLxVdNgSUQvaNX4rwNZmtajyMB7pa2ABvYf_UPZS48J5XB3_tnLnPUdszPAGGxsOox86Wjvw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkorFHVLplN7FoAMvVXsOgHZG_tI5IEMqP0MgWDPxh5Qq66Gg6PL_RMIY6pliT1Ef_lT9waU8gtC9ysbEQf7vVhBkCven---KM-JuqiDcatH2dSRmAI_CwzA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhvN4C747sI06QqJy8ItS6MM00ehs9W-3bO0XP5J68MfjfPP_N-joFdE1f-iWWczAV_KHyKKrCBZ1w4UZMHZIEVGTUhrzJQQjUNmsEfMeFcIcKUXJkMSUQIw==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIeNjfVgnAuuvb6bb7jcQi38le0AtamWDS5rbLKTLmRgQkhyAQNhetxv5i2VGZYutb1wk80yjEiZWcdmwKCuR9VcyVafHWBjsUAZDtplz0G6aCtLQK19c2_Q==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmcm21Fpr9i0M8I3zAN6SUOqgBHLrd8hXVzJh49AZQ-Xt0xk_p01StMAC5S9neGaS1_0cFoNUUMbVtkQ1kwqA38-18OMzWuFT6Acekeb4CT0l6_4IAVUAiHQ==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGKxCcJ-v2zQlbOKHbGlP1fASyIF-JfvlXizhiJAieY3w1r7jV9ENF8NXwTahzrJFF8_Nsk5zpKIX6qi0B3AtVSCxGB_ZzqvIiUO4Dty9MuRMjopeY3FvUCQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFD05QhxnS5ner7gjCCMgHFNeJ4d7PERPQVAzU9FB9NyaAMYVpwnmofnZP4o5rFZmQ9hgWUJ9-mLWNEAr0TtipOTMTJAf6-oyozwWtAwRIb5Q9Oo6bUfMqjmw==)
13. [marktechpost.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIXMSx2Z7yidw3r1B3MoI90PmfeodXm634wrIPvsqODv7yQFQQtz4_zSDCk9wAmmo4M_JBeO8UVkC-PDPhzDOxODbWYKVfRazHX85gKh7eLS2nds3wo0bQRizy2na3B7SCBd5LpwJDjh1E-oq7dikjJblCv9njmT0q6wMhGn4EUlLlPlNMpOgax11vZlco1uqiBJAoO9vIfcZWNk91vgCnI1ELXpREii5e052wVZ3CfzqZrz-69nES88E40Kr18EBd)
14. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVRdW4a_5D5WlUgRIWuFQn9OM2qle3QZcAyLeaa0Arme2xNzWM94uZCPZbqdKhTFVtlAC0CrTc4Q-7cHP1xVyRj77e779tuGETTPzZkNOu3iljZ5gOz5OLM8Gfe243vpduuBUnE3sbZ-PY2irauV7nvQG_Cuhydkmk6m-V2bMP6syHrfblK73HoN6mOcGCnroGBtrygwCe0HaUQ-eq52-qaUAGVglcDG3dB8d96lDUNTXxPGnLIE6aV4KLKLdU7cKwxg==)
15. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_sybSAoQknh4aPh0crXeVZ4vm-Jng_n1tZtkneGWT7W6_xSfOuKzLP95fc_AJvgtV4GMumWBsn8L_ZkCH2Fqjikdxhbl9dt9gK12XB20d7ATruIgQhOnRVwskxMSNcw==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhn3aGu_ZDuGURVgg4j25QXuaO_aIggOt0M-yn0vogSk0damY8mSmU5_O6pI77l_UIalf6A5-T21SKqphqLCt_DGsNxtjLbq4NBkXo5T-gzSTtoF6b1Q==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFB1TRbDPU58Rm3wOyZGk9xMUw9xXSZkXDgbDLOWGVOZ1cj2Sov9fYIgBPUPi75EwbVM8Qq82lgiTNXBqavTPj0e9g8E87bs2tXl-sjHv4LN3aTpifXBuxzwQ==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7RiVPfGF8mwWkSrnWb2uAGtLWt1IUGfZSmWIH2n20KOVrC8jSxJQOxoo8bl2rYfNO9Iuegk-nK6oUN29mdathW2MRsDFk5h4Pu1J5IEnXl5ivYoc6ENZ1rA==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENuQNvmyDSI9r_dkExuEvWS7gy3LS7_S0u1TSM-PRmfWZQahzyAe9D5ceiA6CFLqWVeizzRfx4BKsOdDrfQ7WOz5YWJ-wtzkvFqXaBZrHb18liTDqMOOn_psfkn2jl9ChT8OmoSPBUpgnzC24frsxs3S-Jt6Us5oaXxHrHYFmf2qh4yyaxJeDOOKlwKg2zKU-amIfWHO8UEjw3flPGjeQ=)
20. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqwzJ5I3PDArp_LGJpIjz-m9E-8O53JNiVXOOXVVkfCjze9cL0ZkrBuuNt-GWaUG3zZ7oQyC74tjwov3H7ytpwpWmRAPwQ61ZmoanT5MsXCsr8MoVqvbLs0zkpANhJLq67YA==)
21. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYCg8vjz5u-BaZHqKW6cCNAbUMqhs2JwPWNDgfTCs5wk7qDoXLrZeQ39FB0ij4oKkrKeUFjPAAN-A6TCIEatQbT8OPTfR5rRYpTiqvIUImyhrmilUQ3vAER82Efb0nq1w=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuXmtyrHZtTgxASyco8flzz6jkxClE7-064_ZfxFnNoWgBe3wGFRIfjQwyRtpGQ8aA84ZpVzirEkqhVZ--UkUU-KOKq0UfCyHJLmITg6SWxuClLXtG6g==)
23. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN5MYWuy7v-DnRmnDUJNUMHJnaXxnpEqiJVwaoDHU_-NX58B6N0Rj0Cm24R_fFLmSKWxh44UHlbsk3vW894FyfKs-BTrCGYmtBaUgYKFWQA5I-JPg=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFM3Ecxfe93ZNNrEe1QZZQI7DdvhyacuNEY5jMt61pgRqjU6vO47n-FxkJZOw4V2W1772Syqa0oPqkHCmRjmqWFiiY0SdVmNqm6SJt1dIaY1iWkthd-JCrkiw==)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6oDRwl6WGW9hl0yvoisuN3-AKTrjx1RWqbjBZx7JAACg7Ojgvau2qqSmz61JxZjwIrbuosRknwWj96SNa9ZOk1PZg-eLwLmpINvJcHOvdRCW-LaTK71qt-Q==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_G-XdRKqT_BHEhcUh9RfGgwfzTi1WiN0B9vaDc6hEVMGzaGrT_EKAoH3c9Qh5hfD-hsFlPLgqkQGVYvUhLhl3j-I_mnZAGSDCwFCuYR2PE_XwNzYXDGbWieV7Zr9R8tKYwfDPn_4dXYRkFeu1wukYcU22ojTms7jnTmQLeDPfML2bC9eStTfZFE2dl5hVm7_Nu4LdVlO4u1AtpGRG2VVaDTSXkVr1haTeOl3Sa5kn)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhoOMlD6BPAuBg9KKOerI3Gy36V-gzKCxqA4O9GlUOmv1PeH1rKwbWnYCJL1r2GXPKXAhelTb0CkLtSggcqr_g4waz4a3_hBl7QDBTktSjxoVTHYHNKNGQiw==)
28. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtEGaWbyfZJLhVeWmq0eIhOsW4jzGiY6w0Wx7PAtqGhUkCm3kO7HkAiQftCDrkO7gghg8FVTOpAZawu_X3fFLtFJC_dJq-3c1Seu8mY2MQmohryXFppfYMB20NzWRvXsYWn3c8iLewywcgUnpvybKY_CHdLdp_EV9oqaIP)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5HuI81_FPHyx9fuJRvXaxXD5sK_RiPatwRteb2P5cqoCubM8cC01Wx3pgYcyJJsAF1XwZnZphiwa1VmP4qb4T36MkDwS-CAKBcYmzOH7t1oQRKTuWPQ==)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtBnGkduKjQbMcpmGlTmGxEwpg9KidQAp2OIA-swJ5kZwWs_Vmahbmkp-cIZSYzfK30Xs6AS6V5xNh5qWN-SnhPhEiBk11fa1kXVFlXaQW2J8xWrUcnhVaNg==)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHssY9jfscSbJT6pe25dfYpGPWWJ-jMu9BzvwuHZbHQNs29m7FkYGZIB49DO4Vtf9ZeDhOrqm79QdigGWzN1A0eQrygLsGtluROIxrOX6bfoj8QAKdMkw==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTnYp_r_OjFq-uIqRohzgaGFzeIUIJNDzZJGQ-p_B0rgB4wrUKaI8UICUgBvTR2Ee1z_Wk6-dlNEGCKBKk-eUlO30_zejjFm8yOvXNz1ByxaOACRztYg==)
33. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_SZQikfWbiBxjD5BgA-116b2HANwiEeBfRsI18eFP1N5Zg44rc5G1ayDrsVa9V_pX59dF5VeNAXpp-R8vi18Pw_T6R-woaWlEmojTotUPjIIrwKOAkzdfLE5dmZSNQw==)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIR_6pRcyLx_LldUFv9Oaeh9qr8OON5Sg0d_RmqP8c1qSEqufTGjiOAhQdmtzVKHORpghpEkdGGpdBfuKBcyh-FdwYRSIvJQANoUNgO2oi1d-ghjvdOBJXLw==)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrmnujkCoXPJFS4BAB5LNYAJgdKK1Dq7Q-wbTArBH8Hxv6H6_cSwsClsCuDTKvQ_kQpKQYa8tS8FveH0omRg0i6TFqzry34p3FAn5qdxx3y2N4qWx5yQDVzQ==)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwIqRvLMJqEQfOW_avMZeLxvn5ucmPAa0Q2-727dHzJ8wsrqyog4OEyOC9zTj5j-PL916XJo3DlrAp1qjjK5LXnZ-e0igCdCXsmL8W_4dwfbMx7MNBZ6Umcg==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2aqvKKSrVon5CNKPsqzqwxl57rhJFhy7Jj4SH4OSzQrDTrpj74030LQ3ms8UhV0WMMxfpy4_gCUKJNt2FhpUtP3HB1GIpFWqtKRao8n6tZk6CBwiiHYWUJQ==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExMsCAhZRyX27SVeyckCx_5ii9rMBauycbWx1jiggXTvP77fxBzQjqHqyCYEZVGbW-_hK5czdIKx2ZIXRmyVgQmvLOl4BE4xgiLp4bI5xVkMHCFBum6BB7YA==)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYwhfRi0ggcmuVC3_UgTasisypnMCM0ycNALpJe-aBQhcF7MATd3BmNP2gXJqi8nWi_9mYiVFk0M-IBFKUyLTXdRxcJmicVFVgE_k8eNCmRuiC5diTNw==)
40. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE32PRIPXowOuQYVGQKJHdqFzS4k1AMXKeGQLheudjzvmvAxkRZbMNEWTR90nFkZauuB9jKHrrhAEXWAqmtj7pTzSWBU6zMKKf1fnmOe6aPpm0bSqG8Mg==)
41. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBrhShTzEHfL7YwqnYet44jYPkEVmZcGPBUShWzgTd4TYzzAy-r_bZ1_Tkz7zO3T5-E3sa8REfuC1vaEfIqHwAmB9yiNu0OUpU0Bs270WJzP6JyNoCczOaszGpPHIJ)
42. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmKAM3as_Acnhj-3c0vrKsWKXc_y8BJ71mi-vGVfFlQQxn-Bjf1ow9WVVsNL7L0gg8iv-3h1MPIgYWSA8Q3ZCvRsfv8YNVLpoMjZje-AD-9h_LWzMpksikO5Ecd2twfozt6oaSopqqQVfuv5OI2jwf7IdgEDc88c-tgbPuJoFMpuC-gnWOaRh1-rYhyU9JYYdCgGo_pycjYxqnEnWxe2VNWxqiU9ALO4Qm_y3hLDdifi7_ERNWzYCHgPsoTjSLcCk=)
43. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvukuc_7-Mq2FfTA20hcKg5VkNcr-Skms7DL5aJbpD8MSH0VMgCa4WP2qB3Yle6PlDW9UskMUBAwk5sh0-h3y2hMn37p7yN-HpbxB_TJ-LiPoHzv-X7lP3IQ==)
44. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmSTVm3Zk1Nc7rf-k_X-Wq-Inpr_EahjO1LtFw7VeLbrFrmKr2HA8I5lX-MSrkGH6PWiIySjONvg2-4u19Q_0WqrlMICIB5b1PzqQp6kv-7MjVilg1KJG4avus-kJsaPVrEgjhWvJ31KQrrv9qx3QjooszO4DjWMzi5SDOPZYFik8=)
45. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWWIBYaLe21JpXJAJuPfsjb1Rc7zl-9FIr-fraQk0sDIP_BlPamfDv4-u-a6rgPIw7COBZV4LE2LxMEDx8e0ltoT-jS0g1rgOPk25v14EDfieovmAhtWQ4Zg==)
46. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFC5thsX3qYREEdawIeu0KydtSV7bjS1H854948y6UJk-_mVlQF06mgj5yb7DqMch7QlJ6hBNyZE2g98MjsRYo-nt1zCYgqszI3PsKjISioyLVsonc26zug0A==)
47. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtJdAj3zuivwM7HpIWUm86qYOab3B0CFPAjtDOUBFRP3dBAAuj3WpYvtu03qg-jwVsWa8-ZyMpScdB6HE9TcTiDjH_OjTPmTPtt1uszJRir_OR2AHFE-ATLBgD5t7Jl0E=)
48. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo1qHyJnpLthFZfP0VLffgQrBKpTal9GI0bviShrFmU7SPkyhi34jOUGT0x6oVvmIcwKrs-PPtLKeLblJDE_nsdOWRqvBhoBXISrWYiqU_tYQXEWt0OFmgic9hqsnOciSauD7x6E9mGg4aEVtYYYN3pZsLy0GV_cDFXMqPzQ==)
49. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpWC8Ir-vaEyQ4M4TDzlhLkMH4RG_BLRWU6prSCRxT0b_yK8VlAkYmzVYPmfUtkp5ZHDOZE4PDntHKsFO_SkmlgYvVsYBrQMg52ohtZiWqXySsw59gyFvr8F8SylrAKdNR_h0jBKWO6gDDd5t5R2qDNNQ=)


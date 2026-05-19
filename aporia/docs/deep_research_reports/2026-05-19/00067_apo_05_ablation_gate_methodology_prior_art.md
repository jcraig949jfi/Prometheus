# APO-05: Ablation-gate methodology prior art

**Pythia queue id:** 67
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdzRjhNYXJQbU1fT01fUFVQei1ULTZBaxIXc0Y4TWFyUG1NX09NX1BVUHotVC02QWs
**Elapsed:** 885s
**Completed at:** 2026-05-19T13:18:30.437673+00:00

---

# Methodologies Prior-Art for Using Ablation as an Admission Gate in Compositional and Program-Synthesis Systems (2020–2026)

**Key Points**
*   **A New Role for Ablation:** Research suggests that ablation—traditionally used as a post-evaluation tool to understand which parts of an AI model are important—has recently been repurposed as a real-time "admission gate." Systems now test new code, skills, or memories by turning them on and off (ablating them) during the learning process to ensure they actually improve performance before saving them.
*   **Balancing Quality and Originality:** Evidence indicates a delicate balance between "effectiveness gates" (which ensure a new skill actually works) and "novelty gates" (which ensure a new skill is genuinely unique). Without effectiveness gates, systems fill up with useless data; without novelty gates, systems get stuck repeating the exact same solutions.
*   **Diverse Thresholds:** Determining "how good is good enough" remains a complex challenge. Current systems use a variety of thresholds—ranging from strict accuracy percentages to dynamic formulas that penalize slow or overly long code. 
*   **Ongoing Debate:** While these admission gates show immense promise, some experts argue that the performance boosts we see might actually come from models simply having more compute time to guess and check, rather than from truly learning reusable library components. 

**What is an Ablation Gate?**
In computer science, "ablation" means removing a component to see what happens. Imagine taking a spark plug out of a car engine; if the car stops running, you know the spark plug was essential. In the context of AI and program synthesis (AI that writes code), an "ablation gate" flips this concept into a bouncer at a nightclub. When the AI invents a new tool, rule, or piece of code, the system runs an A/B test. It tries to solve a problem *with* the new tool, and then *without* it (the ablated state). If the performance drops when the tool is removed, the tool is deemed valuable and is "admitted" into the AI's permanent library. 

**Novelty vs. Effectiveness**
When an AI generates thousands of potential solutions, it needs ways to filter them. "Novelty gates" act like plagiarism checkers, mathematically comparing a new piece of code to everything the AI already knows to ensure it is fresh. "Effectiveness gates" (like ablation testing) act like quality assurance, verifying that the new code actually solves the problem efficiently. Research leans heavily toward the conclusion that the best AI systems require a strict symbiosis of both gates to avoid becoming bloated with useless novelties or fixated on effective but repetitive templates.

**The 2020–2026 Landscape**
Between 2020 and 2026, researchers developed highly sophisticated named methods—such as SEDM, SkillGen, NNGPT, and EvoEnv—that utilize these dual-gating mechanisms. These systems are pushing the boundaries of what AI can do, allowing models to autonomously build reliable, evolving libraries of code, neural architectures, and logical reasoning skills. However, the exact mathematical thresholds used to admit these new skills vary wildly, reflecting an exciting, yet unsettled, frontier in artificial intelligence research.

***

## 1. Introduction

The landscape of compositional machine learning, open-ended discovery, and automated program synthesis has undergone a structural paradigm shift between 2020 and 2026. Historically, system designers relied on *post-hoc* ablation studies to retrospectively justify the architectural components of their models [cite: 1, 2]. However, recent methodologies have transposed the concept of ablation from an analytical evaluation technique into an active, run-time **admission gate** [cite: 3, 4]. 

In compositional and program-synthesis systems—where an agent generates verifiable artifacts such as Python programs, mathematical proofs, domain-specific language (DSL) macros, or execution-ready neural architectures—the search space is practically infinite. As models auto-regressively sample from this vast space, they produce candidate programs that must be evaluated before being permanently integrated into the model's active library, memory bank, or skill repository [cite: 5, 6]. Ablation-as-admission formalizes a rigorous A/B testing environment: a candidate artifact is evaluated by comparing the system's performance on a target distribution *with* the artifact against the system's performance *without* it (the ablated state) [cite: 7, 8]. If the marginal utility is positive and statistically significant, the artifact passes the gate.

This exhaustive report synthesizes the methodologies, threshold-selection criteria, and comparative dynamics between effectiveness (ablation) gates and novelty gates derived from state-of-the-art literature published from 2020 to 2026.

## 2. The Theoretical Construct of Ablation as an Admission Gate

To understand the mechanics of ablation gates, we must formally define how utility is measured in iterative generation frameworks. In systems such as optimal ablation (OA) and self-evaluating memories, the ablation loss gap, often denoted as $\Delta_{opt}$, quantifies the exact informational value of a proposed component by isolating its causal impact on output accuracy or reward [cite: 9, 10].

### 2.1 The Mathematics of Marginal Utility
When a candidate artifact $s$ (a skill, memory, or program) is proposed, the admission gate operates by running a paired execution. The control condition $A$ utilizes the standard policy or base prompt, yielding outcome $o_A$. The treatment condition $B$ injects the candidate $s$, yielding outcome $o_B$.

The ablation gate evaluates the net effect, $\Delta(s)$, accounting for both "repairs" (instances where the candidate fixes a baseline failure) and "regressions" (instances where the candidate breaks a previously successful baseline trajectory) [cite: 3, 8]. If $\Delta(s) > \tau$ (where $\tau$ is a predefined threshold), the candidate is admitted [cite: 3, 11]. This empirical verification ensures that the growth of the system's library is strictly monotonic in utility, preventing the accumulation of redundant, noisy, or parasitic artifacts.

## 3. Named Methodologies and Systems (2020–2026)

A diverse taxonomy of named systems has adopted ablation-based admission gates and structurally similar verifiable gating mechanisms to manage their compositional libraries. The following subsections detail the most prominent methodologies from recent prior art.

### 3.1 SEDM: Self-Evolving Distributed Memory
The Self-Evolving Distributed Memory (SEDM) framework represents a significant advancement in multi-agent memory management by introducing **verifiable write admission** [cite: 7, 12]. SEDM transitions memory from a passive vector-database repository into an active, self-optimizing component [cite: 13, 14].

SEDM packages each task execution into a Self-Contained Execution Context (SCEC), which enables environment-free parallel replay and deterministic reproduction [cite: 4, 7]. When a new memory candidate $m$ is generated, SEDM executes a paired A/B test via the SCEC. 
The ablation gate computes a composite score $S$:
\[ S = \Delta R - \lambda_L \Delta L - \lambda_T \Delta T \]
where $\Delta R$ is the change in reward, $\Delta L$ is the change in latency, and $\Delta T$ is the change in token usage [cite: 4]. If $S$ is positive, the admission gate accepts the item and assigns its initial weight; otherwise, it is discarded [cite: 4, 15]. SEDM's progressive ablation studies confirm that this verifiable admission mechanism effectively halts the uncontrolled expansion of context prompts while preserving or enhancing multi-hop reasoning accuracy [cite: 7, 15].

### 3.2 SkillGen: Verified Inference-Time Agent Skill Synthesis
In the domain of agentic tool-use, the **SkillGen** framework models inference-time skill synthesis explicitly as an intervention problem [cite: 3]. SkillGen takes LLM trajectories as input and derives auditable, human-readable skills. 

Rather than merely summarizing past successful trajectories, SkillGen utilizes contrastive induction to identify reusable patterns [cite: 8, 11]. The ablation admission gate in SkillGen operates by verifying the empirical net effect of a synthesized skill on a validation dataset. It specifically checks the candidate skill against the identical inputs with and without the skill [cite: 3]. To be admitted to the permanent library, the skill must demonstrate a positive net-effect ($\Delta(s)$), ensuring that the number of "repairs" significantly outweighs any induced "regressions" [cite: 3, 8].

### 3.3 EvoEnv and ANCORA: Environment and Task Synthesis Gates
In reinforcement learning paradigms where the agent generates its own training environments, zero-data reasoning RL systems like **EvoEnv** and **ANCORA** employ multi-stage admission gates [cite: 16, 17].

*   **EvoEnv:** Operates as a single-policy generator-solver that synthesizes Python environments. A candidate environment $e$ is admitted into the active training pool only if it passes a rigorous multi-stage gate: it must execute under a strict interface, pass a semantic self-review, be solver-calibrated (hard-but-solvable), and pass a novelty check against the existing pool [cite: 16]. The pool-admission gate threshold is denoted as $\tau_{gate} = 0.80$ [cite: 16, 18].
*   **ANCORA:** This anchored-curriculum framework uses a unified policy alternating between a Proposer and a Solver [cite: 17]. Its admission gate, $g(x') \in \{0, 1\}$, acts as a strict boolean filter combining MinHash novelty with solved-only verification. ANCORA grows its Curriculum Directed Acyclic Graph (DAG) exclusively through these filtered, novel, and Solver-verified specifications [cite: 17, 19].

### 3.4 NNGPT: Closed-Loop Architecture Synthesis
Automated Machine Learning (AutoML) and Neural Architecture Search (NAS) have benefited heavily from program synthesis techniques. The **NNGPT** framework evolves a code-oriented LLM over multiple supervised fine-tuning cycles to synthesize PyTorch convolutional networks [cite: 20, 21].

NNGPT's admission gate requires candidate architectures to be validated via low-fidelity performance signals—specifically a first-epoch accuracy threshold—and a MinHash-Jaccard novelty criterion [cite: 21, 22]. High-performing, novel candidates are then converted into prompt-code pairs for parameter-efficient LoRA fine-tuning [cite: 20, 23]. By using execution feedback as an admission gate, NNGPT fundamentally reshapes the LLM into a task-specialized architectural prior, increasing valid generation rates from 28.1% to 51.0% [cite: 20, 21].

### 3.5 Library Learning Frameworks: Stitch, DreamProver, and OED
Library learning algorithms are core to program synthesis. By extracting reusable subroutines from sampled programs, they build a hierarchical DSL [cite: 5, 24]. 
*   **Stitch:** Performs corpus-guided top-down synthesis utilizing branch-and-bound algorithms to identify function abstractions. Its admission criterion is rooted in *compressivity utility*—an abstraction is admitted if it optimally compresses the corpus [cite: 6, 25].
*   **DreamProver:** Operates via a wake-sleep cycle for theorem proving. During the sleep stage, it clusters semantic lemmas, proposing new abstractions. Its admission gate prunes redundant or low-utility lemmas while re-incorporating verified, high-utility lemmas into the library [cite: 26].
*   **Open-Ended Dreamer (OED):** Extending DreamCoder, OED uses novelty selection and stochastic pruning as admission mechanisms to foster creative divergence in programmatic discovery [cite: 5, 27]. 

## 4. Threshold-Selection Criteria in Admission Gates

The effectiveness of an ablation-based admission gate relies entirely on its threshold-selection criteria. If the threshold is too low, the system suffers from library bloat, increasing inference latency and context-window exhaustion. If the threshold is too high, the system suffers from mode collapse, failing to learn incremental, stepping-stone skills. 

### 4.1 Static and Heuristic Thresholding
The simplest approach to admission gating is applying a static, domain-specific heuristic.
*   **NNGPT** utilizes a strict first-epoch accuracy threshold of 40% [cite: 21, 22]. Any PyTorch architecture yielding below this metric is immediately discarded, regardless of its novelty.
*   **HNPS (Hierarchical Neural Program Synthesis)** applies an execution runtime threshold, limiting the bottom-up search baseline to 500,000 expressions to prevent combinatorial explosions during the synthesis of long string-manipulation programs [cite: 28].
*   **EVOR** sets a termination/admission condition based on execution feedback consistency: the pipeline exits and rejects a generated program if it results in the exact same execution error in 3 consecutive iterations [cite: 29].

### 4.2 Relative and Frontier-Based Thresholding
To support continual learning, thresholds must often scale dynamically with the model's competence. 
*   **SkillGen** utilizes a frontier-based admission criteria: a new candidate skill is only admitted if it outperforms the *weakest* frontier member on the same validation subset [cite: 3]. This forces a continuously escalating standard for utility.
*   **EvoEnv** uses *solver-relative difficulty calibration*. Rather than an absolute accuracy threshold, EvoEnv requires that the generated task be "hard-but-solvable" for the *current* state of the solver policy ($0 < \hat{a}_m(e;\pi_\theta) < 1$) [cite: 16, 18].

### 4.3 Composite Cost-Utility Functions
Modern LLM agents must balance task accuracy with inference costs. 
*   **SEDM** parameterizes its admission threshold by integrating computational costs. The composite score subtracts token usage ($\Delta T$) and latency ($\Delta L$) from the raw reward improvement ($\Delta R$) [cite: 4]. This ensures that a candidate is only admitted if its utility justifies its computational overhead, preventing the prompt context from growing uncontrollably [cite: 4, 7]. 
*   Similarly, **Adaptive Memory Admission Control (A-MAC)** models thresholding as an estimation of five interpretable factors—including future utility, confidence, and novelty—to rigorously intercept ineffective write operations [cite: 30].

### 4.4 Conformal and Risk-Controlled Gates
In high-stakes domains, statistical guarantees are required for admission.
*   **CTCM-Neo (Antimalarial Peptide Synthesis):** In generating antiplasmodial peptides, this framework relies on a conformal acceptance gate. Rather than a static threshold, it applies conformal risk control (e.g., $\alpha = 0.10$) alongside physical constraints (hemolysis, charge, hydrophobicity). This ensures the generated sequences are admitted only if their predicted safety falls within mathematically guaranteed confidence intervals, prioritizing external generalization over raw exploration [cite: 31].
*   **Maximal Certifiable Residue (MCR):** In LLM pipeline verification, MCR acts as an abstention operator, turning raw outputs into a maximum-weight certifiable residue. It strictly drops claims that cannot pass a decidable consistency predicate, acting as a structural logic gate for admission [cite: 32].

## 5. Comparative Analysis: Effectiveness Gates vs. Novelty Gates

A central theme in recent prior-art is the comparative dynamic—and necessary symbiosis—between **effectiveness gates** (which use ablation/utility testing to ensure the artifact improves performance) and **novelty gates** (which ensure the artifact is structurally or behaviorally unique).

### 5.1 The Mechanics and Necessity of Novelty Gates
Novelty gates prevent identical or near-duplicate artifacts from flooding the system, which would skew policy gradients and waste compute resources. 
*   **MinHash-Jaccard Filters:** Systems like NNGPT and EvoEnv leverage the MinHash-Jaccard novelty criterion [cite: 16, 21]. By analyzing the n-gram or AST structure of generated code, the gate ensures that a new neural architecture or environment has a sufficient Jaccard distance from existing library members [cite: 16, 20]. For example, EvoEnv uses a pool-admission gate of $\tau_{gate} = 0.80$ to cap the maximum permitted similarity [cite: 16].
*   **Novelty Search (NS) and Quality Diversity (QD):** Open-Ended Dreamer (OED) and MarioGPT integrate novelty search directly into their evolutionary loops [cite: 27, 33]. MarioGPT retains candidates that pass novelty criteria to maintain diverse player paths [cite: 33]. Similarly, EvoTD relies on a skill crossover operator to drive a combinatorial novelty search, actively expanding the frontier of the curriculum beyond mere data volume [cite: 34].

### 5.2 The Limitations of Unconstrained Novelty
While novelty search prevents structural redundancy, empirical evidence strictly indicates that novelty alone cannot guarantee functional utility. In NNGPT, it was observed that text-level novelty does not inherently guarantee functional novelty [cite: 21]. A program might be syntactically unique (e.g., via variable renaming or trivial AST obfuscation) but mathematically isomorphic to an existing solution. 
Therefore, novelty gates are generally considered insufficient as standalone admission criteria for program synthesis and are positioned downstream of, or parallel to, execution verification [cite: 18, 22]. 

### 5.3 Synergistic Joint Optimization
State-of-the-art frameworks demand both gates. EvoEnv's ablation studies explicitly validate this synergy. When researchers ablated the "Quality" component (validation and difficulty shaping), the system collapsed; similarly, when they ablated the "Diversity" component (novelty-gated exploration bonus), performance degraded due to template collapse [cite: 16, 18]. 

The symbiosis operates linearly: 
1. **Generation:** The model auto-regressively creates a candidate.
2. **Execution/Effectiveness Gate:** The candidate is compiled and run. If it fails, or if an A/B ablation test shows no $\Delta$ utility, it is rejected [cite: 18]. 
3. **Novelty Gate:** The verified candidate is hashed. If its MinHash-Jaccard similarity to the existing library exceeds the threshold, it is rejected [cite: 22]. 
4. **Admission:** Only artifacts passing both gates are permanently integrated [cite: 3, 16].

## 6. Meta-Ablation: Empirical Validations and System Overhead

To scientifically prove the necessity of these admission gates, authors perform meta-ablation studies—temporarily disabling the admission gates themselves to observe system degradation.

### 6.1 Demonstrating the Efficacy of the Gates
*   **SkillGen Ablations:** Removing contrastive induction and the verification gate led to marked drops in the net effect of synthesized skills. The verification gate was proven to be a critical contributor to the +3.27 to +10.08 percentage point gains across LLMs [cite: 3, 8].
*   **SEDM Ablations:** In the HotpotQA dataset, removing the self-scheduling memory controller and verifiable write admission (+SCEC) caused contextual prompts to bloat excessively without corresponding gains in reasoning accuracy [cite: 7, 15].
*   **OED Ablations:** Ablation experiments mapping elites and priors demonstrated that eliminating the novelty selection mechanism drastically narrowed the diversity of learned programmatic abstractions [cite: 5, 35]. 
*   **HiveMind Proxies:** In multi-agent concurrency scheduling, ablation studies on condition-variable admission controllers revealed that while admission control manages load, transparent retry mechanisms are the single most critical primitive for reducing failure rates under LLM API contention [cite: 36, 37].

### 6.2 The Controversy Surrounding Library Learning Utility
Despite the reported successes of ablation and utility gates in library learning, recent meta-analyses have introduced a degree of controversy. A critical evaluation by Berlot-Attwell et al. scrutinized the purported accuracy gains in library learning frameworks [cite: 38].

Their ablation studies revealed that genuine cross-task tool reuse is surprisingly rare. Often, the learned tools are single-use, narrowly tailored to one problem. When library sharing was completely ablated (disabled), there was no marked drop in overall system accuracy [cite: 38]. 

The authors concluded that the accuracy gains historically attributed to library learning algorithms (like Stitch and DreamCoder) are frequently a mirage created by secondary mechanisms:
1.  **Self-Correction:** Error-driven exploration and iterative refinement dynamically solve the problem, masking the lack of tool reuse [cite: 38].
2.  **Self-Consistency:** Ensembling multiple candidates via majority voting mimics the stability of a mature library [cite: 38].
3.  **Compute Budget Effects:** Systems with library learning enabled often implicitly run higher sample counts or prolonged search phases. When normalized for inference cost, the raw advantage of the library diminishes [cite: 38].

This critique heavily underscores the necessity of strict, cost-penalized admission gates (like SEDM's token-cost penalty) to ensure that admitted tools actually provide efficient utility, rather than simply consuming more compute [cite: 4, 38].

## 7. Extended Applications of Ablation Gating

The paradigm of ablation as an admission gate has permeated subfields well beyond standard Python program synthesis.

### 7.1 Quantum Algorithm Discovery
In quantum chemistry, platforms like **Hive** utilize LLMs to synthesize Variational Quantum Eigensolver (VQE) algorithms for molecules like LiH and H2O [cite: 19, 39]. The system utilizes a progressive ablation study to construct a mechanism ladder (L0 Basic $\rightarrow$ L1 Scoring $\rightarrow$ L2 Growth $\rightarrow$ L3 Optimisation $\rightarrow$ L4 Refinement $\rightarrow$ L5 Compression) [cite: 39]. The admission of candidate algorithms into the active growth-control scaffold is governed by bond-length-dependent testing, bypassing simple one-shot heuristic gates for rigorous multi-state verification [cite: 39].

### 7.2 Medical and Clinical Reasoning
In clinical agentic systems utilizing Differential Reasoning Learning (DRL), admission gates operate on reasoning graphs. To prevent hallucinations and logical inconsistencies, clinical agents synthesize explanations that are checked against physician-authored rationales [cite: 40, 41]. Ablation studies confirmed that infusing reference reasoning rationales into the gating mechanism prevents severe internal inconsistencies (e.g., generating an instruction for "admission" while simultaneously concluding "NO" to admission) [cite: 40]. 

### 7.3 Multi-Agent Collaboration and Merging
In decentralized setups like **FLEXOLMO**, an asynchronous mixture-of-experts (MoE) architecture is trained independently on disjoint closed datasets [cite: 42]. Ablation studies on admission tasks proved that general experts can seamlessly merge with independent experts via domain-informed routing without violating data opt-out policies [cite: 42]. Similarly, the **MAC (Multi-Agent)** framework utilizes cross-consistency maximization as a gate. It dynamically masks agents layer by layer, ablating specific outputs to filter inconsistencies during progressive propagation [cite: 43].

## 8. Data Structures for Admission 

Implementing ablation-as-a-gate requires specialized data structures to track utility efficiently.
*   **AbstractBeam and LambdaBeam** use Domain-Specific Language (DSL) Abstract Syntax Trees (AST) to pattern-match recurring subprograms [cite: 38, 44]. 
*   **LaSynth** utilizes latent representations to approximate the execution of incomplete programs, allowing the system to run preliminary ablation tests on code that cannot yet be successfully compiled [cite: 45].
*   **MetricSynth** relies on Tree Automata (FTA) and abstraction refinement, using a clustering threshold ($\epsilon$) based on distance metrics to identify when a newly generated program state diverges sufficiently from existing version spaces to warrant admission [cite: 46, 47].

## 9. Conclusion

The period from 2020 to 2026 has witnessed a fundamental operational shift in how compositional and program-synthesis systems manage knowledge. Ablation is no longer merely a retrospective analytical tool used by human researchers to understand their models. Embedded directly into the training and execution loops of architectures like SEDM, SkillGen, NNGPT, and EvoEnv, ablation now serves as a rigorous, autonomous admission gate. 

By executing real-time A/B intervention tests, these systems calculate the precise marginal utility of a generated artifact. Coupled tightly with mathematical novelty filters (such as MinHash and Jaccard criteria) and carefully calibrated threshold functions that penalize computational bloat, ablation gates ensure that AI memory and skill libraries grow sustainably. 

While controversies exist regarding the true source of accuracy gains—particularly concerning compute budget effects in library learning—the integration of verifiable, execution-grounded admission gates represents a critical step toward reliable, self-improving, open-ended artificial intelligence.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGtbRSO-_wtTEE0okA1YnbrNXHocnBvVh-pPnflry5cFfatq8g49at2uQRSIEjbR89iAIHNNukWGfge8MgDy6ojJUd5lsCYPjD8uezl_3ok8p-i9NW3EuOIaevFf7B0w0hGX0BXN4OnIEuVzyHGcMKR_A1qBiob4Bwu7aUzchcJFQMF1SyiaZk3McBX4nBmzDKvNWy_O-HftgolnFksSP3NHDx97bBVBTNAMLCn3wxyI_LCUjcCapS2BzWB_Sxx7g=)
2. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEy7BsWwi-lvhoWLmRmFZEHL1KCnEkMbif4Y8qAuzIP9I8G7MT9QtzHeNzoHnK4oKS-LQUANAbCSrEXWyq6YhWyejeil2yciRjNp6uqaXq7i8oYWyjvUx4cFxSDRCkHpWv6X39YzHbUeobj7GsQWlnG65EShvy9kuu3Z-TCV7xBPUaUuYdzcK5cSkXTbS2TUkFOz8AwIpjV)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAyiAen8zk4VfzHfOCjLYSUohwxxvj6xo9_NhGAty2S6XAP4V6jDrXBtl6C_8jrrHRGMGeaZ_IsFi8XgpF8fkH-E5fkAsi_BPJu3WKIELZJ81orSJdTH8h2g==)
4. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwsFkiLbkuvynDjwRrHdpZzhxYBog78vSz9jd0FmOHlqIRRZ34qghdwMqHJSi9u3oGQvfTUMfQLk57IwV5OweXJPEigiSpro4E8xvZLb-0FVChIH_-bH2ufDW7uIT9spXY-lv5AwoJ4EhSKnKSv5VuEaWK3ulAUpMRW4Qt-IKN85tMa0ryJyhraf1oQ6Rb5eCZpDyPmA==)
5. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5JGCYUgPhvKlKRZ4IJAQ7mHBu4RY6axFBsDg2Kuegdxyag32WWT5Au4FLiJHW2rE3qrMg3ITuh5by-NGEAIdjez5YLDgfcLCqPhjneRg8YR6gXKKHeCncpzYNUj48-E6BqEwCVD02OFRHpTNITJgfLxt2_UfV3JAUfL_AsnwXSgEdgggl8ZvE_A==)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJSauCjff6_2kRN8FNT1oKhOX8ktEpzVkU_Ftbz5yrBww3GKVnWDo9OPSLG0A0fuSoVCQTWz7ngTClUH575JCC-Q9ssk2RCloQXMMqrqtXKFmJzPUIsE69bVGwq21ralw=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzFy0lTzaaBoXQYN1Tm-QxPcP5rvUuriZIXsoHwXt-Fph-DNLLF5S5rwUxz4gZdKsu6H9yeasUpy70dZoBNYOm2tC-AzQXNxyqlHezr9MTIzer9K4E4oUOVA==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyekaA95gemZJl-3-KVei7JeBWvsJkw1kH9FnYlzNStP-M3l4bJF9i7S9Bey_F4G-1W57PMiw4aHYHRgs6EPMfFY8hFWH0ENJv_ijCSaLVG4GmRvdetA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-BTw6TDq0SX4lCWOLvMayBB0uNP_wdc4d8vqWOGsehCovR3JFzE_1q5ufJt5z5gLVjLzUf9nm5aevAmG8ObfPKzZp16WGKYMwHfrvFBes3DVLjHtR5ri1IA==)
10. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMfnvBIH263DNCvcb12nzv-IJC8jPYfL5_wZ_bxQ4XA5h4qYNogiAJxmtJ4dVwbxjX056B-04t6Acc7sqZoyo9sf_X6Lvs_WGOZ_9XuaGwZv6koovqwTIrdG-T3xC2Y19s8qVm_UMl6NyyWpeHPI2LmG8OPSXk8488gzG8SOaHqfYvMZ_b7mNPSZYUOhnGz09keaCbBN-faJs=)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELH3i521hOmUhupcZgN3PjejN71uGivGHxUp_Ioy34JdqBZO_gE6QfDe-4Z8jrZ9trS6V2EFJu-IsVxEjZ8YWadwNpG6XkgsLgsPxRqXg6bI3L7LxClhuk2DBQL1XKfv-qEgV1UwAaEpchetNBSNGKNGy5rLRF1W-P6wSXds9TOU0XNkdoQBK7Cvjwc7g_okLjQeUPtP9oH9niYYwnkII=)
12. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPucFDIF-kCx1SdY9rvRw6Y0eskQXGpVevPTLg2W8H-Bra_fczGF_JsL7O9mTIbT1JpL7Q54RyT3GA1UHXuKfnHT6ZGgdr-KYitAzRhtmaz3YgJZShLJwtEBk5Fg==)
13. [llmwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFF50LYTON1H2lYJ-W4oA0BeUMGSHajSY9fJcNubFnolNPvnCkwck2npS_C41QyFzvU8hKyL6abSkKJ4EEUVJuXsCqu7xfWV58zBb1FRSFwW8j3X3CZjA2O-YFLyR3nR9OgqZQak6vcFofhYqQGuCE00qt_BYs=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4RcFXJvy-d--GT4v_4gTN92El09QCbx6ruuFW0e9aVTsmwf3wemkazk80EnQumr9t5gXeyq_OH5ZX4wPVJM6HdD1s7ZJZ0Ymi7PmDmM5YAYjKQu8vt7dpiVNiDnOiwDt7ZliATW9f1Y5F8UbP8ppX7yUNwoJzLeb9HiaBAsjJkX63PlZlF8y7qT6GHn28UePMknkrlL_AhO14XUROjHXkGng=)
15. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqX_rDhky5zYZa6rkYAmo-giICq_RWTEZGWqPoBTz1yE2xxj022Z3JHJb-wRmKiSvsMIpEC62MhVGDc7qzpH4BQg-w-7WqRpBKNklgav-9YIZlM6INEXz5KVveTJgV)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9WeHd1FhxDzGCqR55aHL5CxFjeSt86jCTABS2KPCBPsWOQMUvFd5Q_UHX9EkMe9_VR46tahxRpxkXL82xt2LF3eFMqTyC1qzA0-YWh5Bmv8Wrr-K08w==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFk7DkuXN1z5RzqvkO7uRP6QwLxuzdA05bxLYS3PGNBU7V2HavMFm55z1btIOb9xIucvCWZsIyUmxDoMKsS1iA2iNUwJhMEfRSNwUb9b6Iq037hnqp04srnlw==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSGbzgdryXO3vCkWvt-fZTOUJLeb05Hg41ibpD8N1YvYeWPhp-wPS-bWU76Ud74sHEBRFylbzW2aq9FyjMgr5G2xLx9t5GvhFegsyCIdYkfkeB8Jj8VO5BZQ==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCslIA8FoNrSFFYdwrxBsPCDI6QnLCW0f_UP2qCDNLyl_Yf3bonJ_Lwku_8Don_Q1C6rxPIPwhlAtbdXo-kMeqEgxBqpE10MoHd_jDRRlnAOoYM2GwQw==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHO5J11_0x1Ah52eNnJwSPgWqAZjCGQ8X0-RSMKTSYqXEcqa6Mm75yABFmU6x8wgYVSA9Q8uI2RGzdrOH2GYuSGDnCr3J6OidMWuN6c5uVyJ_hoPzVsyg==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCXuohBeqZ1i2JY1TxObu4MltdciwuKipfh9QsHcv74yY09dZo9Kuz1QcPQLztmOgPANVHkYMhxHCMcCLp1zVmect0OHB2N9hi2ildAqXxFnFkiJ5-xGD-1g==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWQ9k54QK7e1cmMKTnvmcmNJlRsM7eVztk02yrzkY8DqS7VDG3hP9iuG5Ewurq6jqhyPTbBpVEVJVjIEWySujxyh808IVeqBYW7zq67TaqriD7WwD5vSonwA==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwblJ7bMY2-i0zFXer0amhHnCrN0_2R2ilt2qlK0m9jlavKZpQAm0rcjVmZt_y-m_DGpnA1Gg-JB_4TNQ06StqcFgLyOjUf5uG2r2CM5H_aCAngjqLWES-vguqoZov5kCPJAebgASfLszy3uflQ4CP3k5cEyWBrl9i0rKFcyaq5dtX86ZfF_i4pphRP1VAGNN_AnRoc9wBycVTNFquHcpmf5yHgFFuSfFuGurmEUikz_WC)
24. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDWzOUnTn89ZtYlaABMxB_BvPWOMN2xPLTec3lJItax2bXNvDOcrhSo6OpheTv4M-kyHPuUUnco-YcVsRHL9_-L5RWqi8vuOTxPBizpS3bL8DMuZadsL8YYEN6oNU9nmrPNU0=)
25. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmcvVybOYMuqbBMDYAwptxfUZ9qu092gSQrAbRYaeIYDU8_6uuNTuuUlLWWeUehnqvJ3Eh2RUnHAdR437lRMPWgKdMkuCtTGfDk_XfLxpo5LSFTvxAlb9NZCw=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhzRzxMCTWLuhEbyXj_FVFJBlk5eY-Z4YQvld8_O_ow0wOaqAeEHzG8_LLkC0Htv-YAyKoNDNw6ozxWAFKx8sl6zczan9wi_zIqCzzQ_roOdhdmJDyFhNJ_g==)
27. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESYHoUGIP-doeY6tLWcPKHLVaVdnZ6nN5o2jjiyPNuz_AQYNXeOc0QW4QOypOtZGXHlwA3kMUR3WhhQCHfijIc89Z_FZ_A95ZODJNx3sl9t_xzD1_FqKARHD0HnD0=)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQCIlpZuUzE7z0bN4IZerq95pm4NSN6di-Y8MWNftP-iGawjTSzGplQpiiRrw3rGn7tgQXZTPBXHVrvy9zKW_FnK0BdSqomrVzrELmvgvMHlgLzWmYHA==)
29. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKL_B8GXoegsVmLXp73Sg27BemB2PdP008n1n9ZmsJEVU_kV-pBjNjgp7bUZAecENfCxNV4BRMibWOsjd1DOHbs7B-TbWBKq2bqaifQLPtamJrzrHHCR7-3tuhFMgdUjhw39bk2ChTCnwh3LTt5uUYmhoZwEXlJa3gCpJEDw1ON5ZFxv5Ec1HIbT0xfnCMw_yfVg_wjTF5)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2JUI22FXEmQo1b8XBqYJy0al4WxT3g3K8W2fn2bKne_Lh9coyyaftfRMQN4OWh9jFN0nzklZYw1upb6DsAGJ1dPSTbc6Fum06dnLv8LbSpbbTIweyl8_cLo9nm_MwFrHq0CN2LshZK3mDk6AgDFCpFp2EQJ3MaBqDoyTC)
31. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEA4YQUBWg3gn5iVk9JpL4MLs2tL_IOfSy62cFYGVQFfN1pymVTZuv_i5CM-KkX8i5F1Ty5IRz4Yt3q8Ny8GxhehKRJGza0dEYyvTlYbij4NAJOYDroUnueTgw2RTUYfeehUQBbUB_wbQ==)
32. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAdYr7Ri8T1rPlq5-PvQucXBcEl9jcYNSuwq87BG381YVRMP2cphXHDfXyLqFIxdlpXrzl8ib9Na28L3AFB0fFyaz0KFGijZ6_4RQRzDdMe07OVT2633KTPQ==)
33. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO2vgCR9BBLSOMSNxowSbA4gutAfTEDQuBsYbE3JXCOXy52qDoZFKtev4jVATUXTvsgpbKRMTV1l3sFk1u414RTdOJR7o1aHy1VvGkR6xOxzqFKTfO6XXPXigr8SFIhAvy4crlgG_LJY3YrjqQWlNVNLI=)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4L6sK5CN2iesxMsvGo2I4Wo0CLiyaH8S-fVB3BEA0GEaRukYlW4-8ze1ZrKMd_B_X3CR0HQuNNDoJTysKOPkAsTsA3pVqTW6gOdlSLDNECMG_zSvDET_l0A==)
35. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqjZojBj3CG72v7s_vupYTs2OWam-gbiH4YV3y7Fxxi7UmcAouF8Fu1s6T-MnO0gSTb2PJoozzuvLXqlWb2alu4Bdqq_JwpFfqH7OGmTk0hxB1QLpHpyErmNoQOTtyI53NfqMla1w=)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGk3_HiQLzfU29PEfiH6c6XWQ7eBy_Km2JK_Uk7q4LF8JXWAzLLG1pnV4yqa423ByFaByMLuhIfwx2yqrSNYgbMkBClEdGzmLeloTCf0sMDTUSeAGdM9aJ9_g==)
37. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzr7h5qoDjAbfKl-l2izfrcV4BmxM0kZ2mJ_CS1zpm-GLUlRUVM1gURm5men3Y5f2BZLlhNFzkeES-1qkc17jUbCiu35tlKUNTR9ELO7w1ogdvTc6NxrSW-oFfjUzajt0AdEfg2w8_tX5BVmNS7NU5dkPyAWyO6FsWs5CJlIFgaa-ReZ8nUmZ9h3u4_YDYg0RW5dRaAIRj1A4Oxu0Wxw==)
38. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExyBOhXLSTiK4kflfOmvvscuNo8ov-4UeBFIz94Wtb-I4QA8rx0ggaE_c4loD44-KzqBHltrSayALHtbH-LuALpFI1zhliX8U1zWy7LfLbFAswu8otabk3UTGz9FoobXksqX_U_JXlyl2EV-R3v5M_TdhTPw==)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiSYBKy0m8TI41-5s-rHnPTkAZBdhAhzd4GCT4l07dAjk6kDMs5i1rpi_e1XYkW7-hbyfujaUerimOAm22PaRQGxyArp6FuCfjKyhl0YfRB0yyyC6b6JBJ0A==)
40. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOZqDt4FqrqiWHvux3OvR6RaiKDy7qfks3oCoPBoO7gi0xRmbdaqjkzliQOQvs-hrQH-k9Afaws_gE5NQSyu84L6rRIZi09ftpAyDAy45QFSYYSPhhFAaVLo5iRdDixc-wT3UCqp086DVqTnQoEwMs7y85gRXyWJ8qH013ziVs2N1NpGrKm71y5apDmI2Q67dP5iM5Ifa8Qh0NyDBUIHhfsVS4qhWeQeEzaSkXu_rgPJLYDk4XddN5)
41. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZFqB_VOqJeXEb33XNbr8U0e5qrGi9fSIChzrgHXqfP8EdczBu-l0AnMtw9srFF148cadU_GKoQnfP5Iq4TsqTfOCAbx0t-jfe-45DUaLJ3XihAjNE1CfmdQ==)
42. [allenai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERKm5BxzvulAsjdU8LGIok21i5k2494PWvuzziYOVGVmF0Gmy98NZ37gF5bkrRqtHDLI7bAOYqPui5gqspsp0yjUkGejymB5wXmtfVhrxNv1gnXuXeuNGCWg==)
43. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8QWukt0S6holKPPf8iBJEinQwkRcl2BugPWXgmN5hFMze0D2CdVVa2DhN4UxlU4643nXK1jNZWDoRmxHTKFxbFSyne1WX2AnqhFV8gkOQY-O9jcyZr74AIg==)
44. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxkOHBABRdQGeAhbkv6uEePXY0mwe4ycvKJjiGqz34tQYxON3W_VeayX8fbRcGQ23DkWCoo8P5ToNLkRi4vhGQvBEaz0vorfN_R5zXTPrNL9m4rx2XHYS3Jrv2Kx9_lXKBvrO9lPR9xiRWmruLCi-1pRQvcNkiyRgeV7ZRG--GJ2F6v8w=)
45. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpVHcGIvfPL19qwPnuF90TkmYGrw8y8SlOEdDBrbavBf9uRxLhdPkqILBIOpyWqi-OrGgV4P9BoGoXr-fMt8PSwsKqq44n2n9rgKz-0yDbDmYXoKKUyI7wNB5tATGXPDCipQ3-sY0l39Vx0J0GLF9cJmsgpuuegdEHvcp0L1tm7opTvDk-x_XrqXk54IVvEQ==)
46. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxEaduaWb_E8Dd87oxSz22MRpY9tQF0gbOTBLHcZLfgn0TSf2SRp3E6c_uUcsvBRgKgJ7mmOwzu16QMmIuT5gdDMCJ3KCMwUSmrqzLsHhYbsZKuWOrIWdlQN5exh-uFpv3LVsBAIV5sahV)
47. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBIFZOHPyVR1IQOrDRG6TZEeba5qDd_Gzh3pPOdOEZlFHsXDd6jG6X8kRP6V6QwB5173Pe0iHQJpaFVemW0BDxmUG9wwRfiyqExI9Z7x2m3C9QcQM40mEPmLRAvYpM_0GuelM=)


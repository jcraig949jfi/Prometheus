# APO-01: AlphaEvolve / OpenEvolve / CodeEvolve frontier

**Pythia queue id:** 63
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdOVnNNYXEybkYtaUktc0FQaWJqcTBBbxIXTlZzTWFxMm5GLWlJLXNBUGlianEwQW8
**Elapsed:** 253s
**Completed at:** 2026-05-19T12:48:51.157464+00:00

---

# Detailed Comparison of LLM-Evolutionary Program Synthesis Systems (2024–2026)

**Key Points:**
*   **Paradigm Shift:** The field of Large Language Model (LLM) program synthesis has transitioned from static, single-pass generation to dynamic, evolutionary systems that iteratively rewrite, evaluate, and mutate code. Systems like AlphaEvolve, OpenEvolve, CodeEvolve, ShinkaEvolve, ThetaEvolve, and TTT-Discover represent this new frontier of test-time compute.
*   **Architectural Convergence:** Most contemporary evolutionary coding agents utilize an architecture consisting of a Program Database (often using MAP-Elites or Island Models), a Prompt Sampler, an LLM Ensemble (acting as the mutation operator), and an Automated Evaluator Pool. 
*   **Search vs. Learning:** While AlphaEvolve and OpenEvolve rely on prompting frozen models for evolutionary search, newer systems like TTT-Discover and ThetaEvolve integrate Reinforcement Learning (RL) directly at test time, dynamically updating the model's weights to internalize search strategies for a specific problem.
*   **Scientific Breakthroughs:** Between 2024 and 2026, these systems have discovered new state-of-the-art solutions for longstanding open mathematical problems (e.g., Erdős minimum overlap, circle packing, kissing numbers) and have been successfully deployed to optimize critical enterprise infrastructure (e.g., Google TPU design, Salesforce Monolith Java code).
*   **Scaling Laws:** Empirical evidence suggests a new dimension of scaling laws centered around test-time compute. Research indicates a distinct trade-off where smaller language models utilizing extensive evolutionary search iterations can match or exceed the zero-shot performance of vastly larger frontier models.

**The Era of Evolutionary Program Synthesis**
The 2024-2026 period marks a crucial stage in LLM development. While established players continue to advance model parameter counts, the emphasis has shifted towards test-time efficiency, sustainability, and automated algorithmic discovery [cite: 1, 2]. The dream of software that rewrites and optimizes itself has materialized through the integration of evolutionary computation with the generative capabilities of LLMs.

**Bridging the Gap Between Search and Adaptation**
Early systems operated as pure inference frameworks, using LLMs as static mutation operators. However, the introduction of hindsight learning, reinforcement learning at test time, and Monte Carlo Tree Search (MCTS) has allowed these agents to overcome performance plateaus. By internalizing successful search trajectories, models continuously adapt to the specific out-of-distribution challenges they are attempting to solve.

**Real-World Efficacy**
Far from being theoretical curiosities, these systems have demonstrated tangible value. From accelerating large-scale matrix multiplication and DNA sequencing to fundamentally refactoring massive enterprise codebases, LLM-guided evolutionary search has proven capable of optimizing complex computational pipelines that exceed the limits of human intuition.

***

## 1. Introduction

The trajectory of Large Language Models (LLMs) from 2024 into 2026 has been defined by a fundamental shift in how computational power is allocated. While the previous paradigm of "scaling laws" primarily focused on equating larger model parameter counts and pre-training datasets with improved performance, recent advancements have increasingly prioritized test-time compute—specifically through the lens of evolutionary program synthesis [cite: 1, 3]. 

Historically, program synthesis with LLMs (e.g., AlphaCode) relied on generating executable code in a single or few-shot attempt [cite: 1]. However, complex scientific discovery, enterprise-scale code refactoring, and advanced algorithmic optimization demand a process that mirrors human iterative refinement or natural evolution. This necessity birthed a lineage of evolutionary LLM-based coding systems, transitioning from traditional Genetic Programming (where syntax trees are blindly mutated) to LLM-guided evolution, where the language model acts as an intelligent, domain-aware mutation and crossover operator [cite: 2, 4].

Systems such as Google DeepMind's AlphaEvolve [cite: 5, 6], its open-source counterparts OpenEvolve [cite: 7, 8] and ShinkaEvolve [cite: 9], and enterprise-adapted variants like Salesforce's CodeEvolve [cite: 10, 11], orchestrate a continuous cycle of code generation, automated execution, fitness evaluation, and targeted refinement. Furthermore, the bleeding edge of this research—exemplified by Test-Time Training to Discover (TTT-Discover) and ThetaEvolve—has begun blending evolutionary search with on-the-fly reinforcement learning (RL), continually updating model weights based on problem-specific experience [cite: 12, 13]. 

This comprehensive report provides a detailed academic comparison of these contemporary LLM-evolutionary program synthesis systems. We analyze their architectural designs, review extensive ablation studies to identify critical operational gates, formalize the emerging scaling laws of test-time compute, and catalogue the demonstrated scientific and infrastructural discoveries achieved by these agents between 2024 and 2026.

## 2. System Architectures

The core philosophy uniting these systems is the framing of algorithmic discovery and optimization as an evolutionary search problem over the space of valid computer programs. Rather than evolving raw parameters or abstract mathematical expressions, these systems evolve actual source code (e.g., Python, Java) [cite: 4]. Below is a detailed breakdown of the distinct architectural mechanisms employed by the leading systems.

### 2.1 AlphaEvolve (Google DeepMind)

Unveiled by Google DeepMind in May 2025, AlphaEvolve represents a direct, highly scaled extension of their earlier FunSearch system [cite: 14, 15]. Where FunSearch was successfully applied to only four mathematical problems, AlphaEvolve is designed as a general-purpose evolutionary coding agent capable of codebase-scale optimization, multi-objective evolution, and open-ended discovery across scientific and engineering disciplines [cite: 6, 15].

**Architectural Components:**
AlphaEvolve operates through an asynchronous pipeline coordinating the following core elements [cite: 16, 17, 18]:
1.  **Program Database:** AlphaEvolve relies on an evolutionary database inspired by quality-diversity algorithms, specifically MAP-Elites (Multidimensional Archive of Phenotypic Elites), combined with island-based population models [cite: 19, 20]. This database stores historically discovered solutions, indexing them by their scores across multiple evaluation metrics to ensure phenotypic diversity.
2.  **Prompt Sampler:** To generate new candidates, the Prompt Sampler queries the Program Database to construct rich, informative contexts. It selects a parent program and curates evidence sets—including top performers, diverse extremes, and evolutionary history. Human-written instructions and problem-specific context can also be injected here [cite: 17, 20]. Crucially, AlphaEvolve features **Meta-Prompt Evolution**, where the instructions guiding the LLM are co-evolved alongside the solution code [cite: 19].
3.  **LLM Ensemble (Mutation Operator):** AlphaEvolve uses a weighted ensemble of state-of-the-art LLMs (primarily Gemini 2.0 Flash and Gemini 2.0 Pro) [cite: 4, 19]. The primary, faster model (e.g., Flash) is utilized for high-throughput exploration, generating numerous diverse ideas quickly, while the stronger secondary model (e.g., Pro) is triggered for exploitation and high-quality refinement [cite: 20]. The LLM does not write programs from scratch at every step; instead, it generates modifications (diffs) applied to code blocks marked by `#EVOLVE-BLOCK-START` and `#EVOLVE-BLOCK-END` comments [cite: 4, 17].
4.  **Evaluators Pool:** Generated variants are programmatically executed against user-defined evaluation functions ($h$) that map a solution to a set of scalar metrics [cite: 18]. AlphaEvolve supports an **Evaluation Cascade**, essentially utilizing hypothesis testing to quickly prune poor solutions before committing to expensive full-scale computations [cite: 18].

**Multi-Objective Evolution:** AlphaEvolve intrinsically optimizes multiple metrics simultaneously, even if the primary goal targets only one metric. By tracking diverse internal structures (e.g., accuracy vs. speed), the LLM's context window is fed heterogeneous successful traits, increasing the probability of recombining novel concepts into a globally superior program [cite: 4, 17].

### 2.2 OpenEvolve (Open-Source Ecosystem)

OpenEvolve was developed as an open-source, faithful implementation of AlphaEvolve that rapidly evolved to incorporate advanced multi-language support and integration with various LLM providers [cite: 8]. It serves as a foundational platform for researchers lacking access to DeepMind's proprietary infrastructure [cite: 4].

**Architectural Innovations over Baselines:**
1.  **Island Model with Event-Driven Migration:** OpenEvolve implements an island-based genetic algorithm. It maintains multiple isolated populations ("islands") that evolve independently to prevent premature convergence [cite: 7]. Migration between islands is event-driven (occurring when a configured number of programs are added) rather than wall-clock dependent. Migration typically follows a ring topology, transferring top-performing programs without introducing duplicates [cite: 7].
2.  **Artifact Side-Channel:** A significant enhancement in OpenEvolve is its artifacts side-channel. Evaluators capture build errors, stack traces, and execution profiling results, feeding them directly back into subsequent prompts [cite: 8]. This allows the LLM to understand *why* a mutation failed and propose targeted fixes.
3.  **Codebase-Scale Optimization:** Unlike earlier implementations that focused on isolated functions, OpenEvolve supports the evolution of entire interconnected code files [cite: 21].
4.  **Agnostic LLM Integration:** The framework supports deterministic reproduction (via strict seeding) and universal API support, utilizing weighted ensembles of OpenAI-compatible endpoints (e.g., Gemini-Flash-2.0-lite + Gemini-Flash-2.0, Claude-Sonnet-3.7, local vLLM models) [cite: 8, 22].

### 2.3 CodeEvolve (Salesforce)

CodeEvolve, introduced by Salesforce AI researchers, directly extends the OpenEvolve architecture to tackle enterprise-scale, multi-language software enhancement (specifically targeting Java and Salesforce Apex) [cite: 10, 11, 23]. Its primary focus is on reliable, validation-first refactoring, ensuring that optimized code retains strict functional correctness in production environments [cite: 24].

**Targeted Enterprise Enhancements:**
1.  **Runtime Profiling Enrichment:** Relying on manual bottleneck identification is impractical in large codebases. CodeEvolve utilizes Java Flight Recorder (JFR) profiles to build weighted component graphs, automatically selecting the most expensive execution targets for optimization [cite: 10, 11, 23, 25].
2.  **MCTS-Augmented Search:** To generate highly reliable LLM edits, CodeEvolve integrates Monte Carlo Tree Search (MCTS) into the exploration phase [cite: 10, 23]. MCTS allows the system to systematically explore the space of possible code transformations, backpropagating rewards from the evaluation pipeline to prioritize promising modification branches [cite: 26].
3.  **Automated Code Refinement Agents:** CodeEvolve features specialized refinement loops. When a generated variant fails to compile or fails unit tests, an MCTS-based repair loop or lightweight reflection loop is triggered. The refinement agent collects compiler diagnostics and asks the LLM to repair the candidate prior to entering the main evolutionary pool [cite: 11, 24, 26].
4.  **Strict Evaluation Pipelines:** The system implements language-specific evaluation cascades. For Java, candidates must pass build validation, unit tests, performance checks, static analysis, and an LLM-based code review [cite: 10, 26]. Only variants fully preserving functional correctness are retained [cite: 23].

### 2.4 ShinkaEvolve (Sakana AI)

Developed by Sakana AI in September 2025, ShinkaEvolve addresses the primary limitation of earlier evolutionary frameworks: **sample inefficiency** [cite: 27, 28]. Systems like AlphaEvolve and OpenEvolve often require thousands of LLM queries to find optimal solutions, resulting in high API costs and slow discovery [cite: 27, 28]. ShinkaEvolve optimizes programs under small evaluation budgets through three architectural pillars:

1.  **Adaptive Parent Sampling:** The framework uses a hierarchical strategy that dynamically balances the exploration of novel regions of the search space with the exploitation of known high-quality solutions (the Pareto frontier of fitness) [cite: 27, 29, 30].
2.  **Novelty-Based Program Rejection Sampling:** ShinkaEvolve actively prevents the evaluation of redundant code. It implements a rejection-sampling mechanism that identifies and discards minor, uninteresting syntactic variations of existing programs before they consume execution budget [cite: 9, 27, 29].
3.  **Bandit-Based LLM Ensemble Selection:** Rather than using a static weighted mixture of LLMs, ShinkaEvolve employs a multi-armed bandit algorithm. This dynamically prioritizes and selects the most effective LLM from an ensemble based on the current state of the evolutionary search and the specific demands of the task at that exact moment [cite: 9, 27, 29, 31].

### 2.5 ThetaEvolve and TTT-Discover (The Test-Time RL Frontier)

While AlphaEvolve and OpenEvolve operate purely via *inference* (treating the LLM as a frozen mutation operator), a parallel breakthrough track has emerged focusing on **Continual Learning and Reinforcement Learning at Test-Time**.

**ThetaEvolve (November 2025):** 
ThetaEvolve simplifies the AlphaEvolve pipeline by eliminating the need for complex, massive LLM ensembles [cite: 13, 32]. Instead, it utilizes a *single*, small open-source LLM (e.g., DeepSeek-R1-0528-Qwen3-8B) coupled with a massively scaled program database and batched sampling for high throughput [cite: 13, 33]. Critically, ThetaEvolve integrates Reinforcement Learning (RL) during the evolutionary process. The model's weights are dynamically updated based on the success of its generated programs, allowing it to internalize effective search strategies [cite: 13, 32]. The framework uses "lazy penalties" to aggressively discourage stagnant code changes and applies reward shaping to stabilize the test-time RL signals [cite: 13, 32, 33].

**TTT-Discover (January 2026):**
Test-Time Training to Discover (TTT-Discover) takes this concept further, explicitly treating each unique scientific problem as its own isolated RL environment [cite: 34]. Using models like the open 120B-parameter `gpt-oss-120b` augmented with LoRA adapters, TTT-Discover performs RL online using an entropic utility objective and a PUCT-inspired (Predictor + Upper Confidence bound applied to Trees) search algorithm [cite: 34]. 
Unlike traditional models trained to generalize, TTT-Discover optimizes entirely for an $N=1$ scenario: discovering a single, record-breaking solution for an out-of-distribution problem [cite: 35, 36]. By continually training at inference time, all gradients and learning signals are derived directly from the specific problem's reward function, yielding extreme performance peaks that frozen models cannot reach [cite: 34, 37].

### 2.6 SOAR (Continuous Adaptation via Search and Refinement)

SOAR (Search, Optimize, and Adapt with Refinement) focuses heavily on overcoming performance plateaus inherent in search methods, specifically evaluated on the ARC-AGI benchmarks (March 2026) [cite: 38]. SOAR learns to synthesize transformation programs by alternating between:
1.  **Evolutionary Search Phase:** An LLM samples initial candidate solutions and iteratively refines them using execution feedback [cite: 38].
2.  **Learning Phase (Hindsight Relabeling):** The search traces (both successful and failed attempts) are internalized via hindsight learning to fine-tune the LLM [cite: 38, 39]. 

This creates a virtuous cycle: better underlying models yield more effective search operators, which in turn generate richer, higher-quality trace data for the next round of fine-tuning [cite: 38].

## 3. Ablation Studies and Algorithmic Gates

The sheer complexity of these systems necessitates rigorous ablation studies to isolate which components drive success. Analyzing the ablation gates across these frameworks provides deep insight into the mechanics of LLM-evolutionary synthesis.

### 3.1 AlphaEvolve Ablations
DeepMind conducted extensive ablations on mathematical tasks such as computing lower bounds on the kissing number and optimizing tensor decomposition [cite: 19, 20].
*   **The Evolutionary Loop:** The most critical component. Removing the iterative evolutionary process ("No evolution"—repeatedly zero-shot prompting the LLM with the same initial program) resulted in massive performance drops, establishing that iterative refinement is fundamentally superior to isolated LLM scaling [cite: 16, 19].
*   **Rich Context:** Stripping the prompts of human-written context and historical evolution metrics ("No context") severely degraded the quality of discoveries [cite: 16, 19].
*   **Meta-Prompt Evolution:** Disabling the self-guided, co-evolved meta-prompts resulted in measurable, though slightly less drastic, performance reductions [cite: 19, 20].
*   **Model Ensemble:** Relying on a single model instead of a Primary/Secondary (Flash/Pro) mix marginally reduced peak performance, though AlphaEvolve's authors noted that the system is generally model-agnostic and scales with the underlying capability of the LLM [cite: 18, 20].

### 3.2 CodeEvolve (MCTS and Refinement) Ablations
Salesforce evaluated CodeEvolve's architecture on complex Apex and Java codebase optimizations [cite: 23, 26].
*   **MCTS and Refinement Synergy:** An ablation study on Salesforce Apex optimization demonstrated the additive power of Monte Carlo Tree Search. The full MCTS-augmented configuration with the refinement agent produced an average of **19.5 valid programs out of 20** generation attempts [cite: 10, 11, 23, 24]. 
*   **Quality Metrics:** By combining MCTS with improved context sampling, CodeEvolve achieved an average KPI score of $0.8977 \pm 0.0251$ and a peak KPI of $0.9495 \pm 0.0034$, vastly outperforming baseline OpenEvolve configurations [cite: 26]. This proves that naive LLM edits are prone to hallucination and breakage in typed enterprise languages, and strict MCTS-driven repair loops are necessary for reliability.

### 3.3 ShinkaEvolve Efficiency Controls
Sakana AI's ablations targeted computational efficiency metrics, validating their three core innovations [cite: 27, 40].
*   **Sample Efficiency:** While AlphaEvolve and OpenEvolve often required >2,000 evaluations to solve the canonical circle packing problem, ShinkaEvolve's combination of adaptive parent sampling and novelty rejection allowed it to reach state-of-the-art configurations in roughly **150 evaluations** [cite: 9, 29, 30]. 
*   **Pareto Optimization:** In agent scaffold design (AIME tasks), ablations showed ShinkaEvolve navigating an optimal Pareto frontier, achieving maximum mathematical reasoning performance utilizing a strict budget of only 7 LLM queries per generation cycle [cite: 9, 27, 30].

### 3.4 Test-Time RL vs. Pure Inference (ThetaEvolve)
ThetaEvolve's ablations explicitly tested the inclusion of test-time Reinforcement Learning against pure evolutionary inference [cite: 13, 32].
*   **Learning Capability:** Across four open tasks and two different base models, ThetaEvolve runs *with* RL consistently reached higher fitness scores at faster rates than pure inference runs. [cite: 13, 33]. 
*   **Database Scaling:** ThetaEvolve demonstrated that the throughput achieved by batched sampling allowed the maintenance of a much larger program database. Ablations proved that larger program databases directly correlated with higher peak performance, avoiding the premature stagnation seen in smaller population sizes [cite: 32]. In raw speed, an OpenEvolve inference run taking 64 hours was matched and exceeded by ThetaEvolve in approximately 5 hours (generating 205,000 programs) due to optimized batched inference [cite: 32].

### 3.5 Island Model Exploitation (OpenEvolve)
Researchers tuning OpenEvolve documented a distinct phase-based strategy for overcoming fitness plateaus [cite: 22].
*   **Phase 1 (Exploration):** Utilizing 4 islands, a population of 60, and an exploitation ratio of 0.7 [cite: 22].
*   **Phase 2 (Breaking the Plateau):** Expanding to 5 islands, increasing population size to 70, and *reducing* the exploitation ratio to 0.6 while injecting radical optimization techniques via the system prompt [cite: 22]. This empirical tuning highlights the necessity of dynamic hyperparameter adjustment in population-based LLM search.

***

## 4. Scaling Laws and Test-Time Compute

The theoretical understanding of LLMs has been deeply influenced by scaling laws (e.g., OpenAI 2020, Chinchilla 2022) detailing the power-law decay of test loss with respect to parameters, dataset size, and training compute [cite: 41]. However, the advent of evolutionary program synthesis has birthed a new dimension of scaling laws: **Test-Time Compute Scaling** [cite: 3, 42].

### 4.1 The Parameter vs. Iteration Trade-off
Current research establishes a parametric functional law modeling the expected performance of LLM-enhanced evolutionary algorithms. The two primary variables governing this domain are:
*   $N$: The number of language model parameters (representing zero-shot reasoning capability).
*   $k$: The number of evolutionary algorithm iterations (representing search depth and test-time compute) [cite: 3, 42].

Empirical studies on molecular optimization and programmatic reasoning demonstrate a distinct mathematical trade-off between $N$ and $k$. It has been verified that the performance of highly capable, large language models can be successfully matched by significantly smaller, less capable models provided they are granted proportionally more evolutionary search steps [cite: 3].
*   **Empirical Validation:** Researchers successfully matched the performance of a 3.2-Billion parameter model using an 8.5x smaller (380-Million parameter) model by supplying it with exactly 2.3 times more evolutionary algorithm iterations ($k$) [cite: 42].

### 4.2 Overcoming Inference Plateaus
Merely scaling the model size $N$ without search leads to an eventual performance plateau on highly complex, out-of-distribution reasoning tasks (e.g., ARC-AGI). 
*   As demonstrated by the SOAR architecture, utilizing search (evolution) coupled with iterative hindsight learning allows smaller open-source models (like Qwen-2.5-Coder-7b) to shatter the zero-shot performance ceilings of massive frontier models (e.g., Claude-level capability) [cite: 39].
*   For the base generation model, performance begins to plateau after approximately 8,000 evolutionary search attempts [cite: 39]. However, interleaving fine-tuning stages (hindsight relabeling) resets this plateau, allowing subsequent generation steps to scale logarithmically higher in performance [cite: 39].

This dynamic proves that static model inference has hard limits in algorithmic discovery. By converting test-time compute into a massive search tree (via MCTS, Quality-Diversity, or RL), the system effectively trades raw computational cycles for effective intelligence.

***

## 5. Demonstrated Discoveries (2024–2026)

The application of AlphaEvolve, OpenEvolve, CodeEvolve, and Test-Time RL systems has resulted in unprecedented discoveries across theoretical mathematics, enterprise systems, biological sciences, and agentic framework design.

### 5.1 Mathematical and Scientific Discovery

These systems have demonstrated an extraordinary capacity to navigate infinite search spaces in combinatorics, geometry, and number theory, producing strictly verifiable bounds.

**Erdős Minimum Overlap Problem:**
The Erdős minimum overlap problem focuses on the limiting density of step functions.
*   *AlphaEvolve:* Evolved a 95-piece step function, establishing an upper bound of $0.380924$ [cite: 34, 36].
*   *TTT-Discover:* Using test-time reinforcement learning, it shattered the AlphaEvolve record by generating a highly complex, *asymmetric* 600-piece step function. This resulted in a new state-of-the-art upper bound of **0.380876**, beating the best human-derived bound of $0.380927$ [cite: 34, 36, 37].

**Circle Packing (High-Dimensional Space):**
Optimizing the arrangement of non-overlapping circles to maximize space utilization.
*   *AlphaEvolve:* Established a tight bound of $2.63586276$ for $N=26$ using proprietary Gemini ensembles [cite: 32, 43].
*   *ThetaEvolve:* Using a single 8-Billion parameter DeepSeek model with test-time RL, it evolved a superior asymmetric construction achieving **2.63598308** [cite: 32, 43].
*   *ShinkaEvolve:* Discovered a highly efficient state-of-the-art $N=26$ configuration utilizing only ~150 evaluation samples, showcasing extreme algorithmic efficiency [cite: 27, 40].

**Autocorrelation Inequalities and Hadamard Determinants:**
*   *TTT-Discover:* Set a new state-of-the-art for the First Autocorrelation Inequality (AC1) by evolving bounds to $1.50286$, surpassing the best human result ($1.50973$) and previous AI baselines ($1.50314$) [cite: 12, 36]. 
*   *AlphaEvolve:* Applied to computing lower bounds on the kissing number problem (the maximum number of non-overlapping unit spheres that can touch a central unit sphere). Out of 50 open problems in analysis, geometry, and combinatorics, AlphaEvolve rediscovered the best known solution in 75% of cases and generated entirely new, improved solutions in 20% of cases [cite: 6, 15, 19, 44].

### 5.2 Enterprise Systems and Hardware Optimization

Evolutionary LLMs possess the unique ability to rewrite infrastructure code, identifying non-obvious optimizations that human engineers overlook due to codebase scale or complexity.

**Google Infrastructure (AlphaEvolve):**
*   **TPU Circuit Design:** AlphaEvolve successfully optimized the hardware circuit design and routing for Google's Tensor Processing Units (TPUs), accelerating hardware efficiency speed-ups by up to 32% [cite: 6, 15, 20, 45].
*   **Gemini Matrix Multiplication:** By evolving custom tensor decomposition algorithms and tiling strategies, the system identified highly non-trivial algorithmic restructurings that resulted in a **1% reduction in total training time** for the massive Gemini LLM models [cite: 6, 15, 46].
*   **Data Center Scheduling:** Discovered improved scheduling heuristics that led to the recovery of 0.7% of previously stranded cloud computing resources [cite: 6, 15].
*   **Google Spanner:** AlphaEvolve refined the Log-Structured Merge-tree (LSM) compaction heuristics, reducing write amplification (the ratio of data written to storage versus the original request) by an impressive 20% [cite: 45].

**Salesforce Monolith (CodeEvolve):**
*   Deployed on a massive, legacy enterprise Java codebase (the Salesforce Monolith).
*   Using Java Flight Recorder, CodeEvolve targeted extreme execution bottlenecks. The system evolved multi-line algorithmic rewrites that strictly maintained functional unit-test correctness while achieving an average execution speedup of **15.22x** across seven critical hotspot functions [cite: 10, 11, 23]. 
*   It easily surpassed naive single-pass LLM optimization (which yielded average speedups of $1.52x$) on complex tasks like `HBaseConnectionRegistryUtil.filterMap`, demonstrating that true evolutionary tree search is required for profound architectural refactoring [cite: 26].

**GPU Kernel Engineering (TTT-Discover):**
*   In a GPUMode kernel optimization competition, TTT-Discover evolved hardware-specific CUDA/C++ kernels that executed up to **2x faster** than the prior state-of-the-art [cite: 35, 36, 47].
*   On an NVIDIA H100, the evolved TriMul kernel ran in $1161 \mu s$, compared to the best human-optimized kernel at $1371 \mu s$ [cite: 34, 37].

### 5.3 Frameworks, Agent Design, and LLM Scaffold Evolution

A remarkable meta-capability of these systems is their ability to evolve *other* AI systems and loss functions. 

*   **AIME Mathematical Scaffolding (ShinkaEvolve):** ShinkaEvolve was used to evolve the agentic scaffolding (the control logic and prompting strategy) utilized by LLMs to solve advanced math problems. It discovered robust scaffold designs for the AIME mathematical reasoning benchmarks that significantly outperformed hand-designed baselines (like majority voting), plotting an optimal Pareto frontier of accuracy versus API call limits [cite: 9, 29, 40].
*   **Mixture-of-Experts (MoE) Load Balancing (ShinkaEvolve):** The system successfully evolved the load balancing loss (LBL) function for a 556M-parameter MoE model. The evolved mathematical loss function generalized perfectly to a 2.7B-parameter MoE, reducing inefficient token routing by 5.81% and improving downstream perplexity and task performance metrics (+1.73% on average) [cite: 9, 27, 29, 30].
*   **Competitive Programming:** TTT-Discover achieved 1st place in AtCoder heuristic contests (e.g., ahc039), surpassing both seeded and from-scratch top human competitive programmers [cite: 34, 36].

### 5.4 Cross-Domain Scientific Discoveries

*   **Genomics and DNA Sequencing:** AlphaEvolve optimized the architecture of DeepConsensus (Google Research's model for correcting DNA sequencing errors). The evolved code achieved a **30% reduction in variant detection errors**, substantially lowering the cost and increasing the accuracy of genome sequencing for biological research [cite: 45, 48].
*   **Power Grid Optimization:** Applied to the AC Optimal Power Flow problem, AlphaEvolve improved the capacity of Graph Neural Networks to find feasible stabilization solutions from 14% to over 88%, massively enhancing the stability simulation of electricity grids [cite: 45, 48].
*   **Quantum Physics:** The system proposed optimized quantum circuits for the Willow quantum processor. These evolved circuits exhibited 10x lower error rates than conventionally optimized baselines, facilitating complex molecular simulations [cite: 45, 48].
*   **Quasi-Monte Carlo (QMC) Design:** OpenEvolve was deployed to frame classical QMC design as a program synthesis task. The system successfully evolved finite 2D/3D point sets with minimal star discrepancy and evolved highly optimized Sobol sequence direction numbers, yielding vast reductions in integration errors for high-dimensional financial quantitative tasks (e.g., 32-D option pricing) [cite: 49, 50].

***

## 6. Conclusion and Future Directions

The technological arc from 2024 to 2026 clearly delineates the end of static, single-pass LLM coding models. By enveloping Large Language Models in robust, iterative evolutionary loops, frameworks like AlphaEvolve, OpenEvolve, CodeEvolve, ShinkaEvolve, ThetaEvolve, and TTT-Discover have unlocked a new paradigm of artificial reasoning [cite: 2, 6]. 

The architectures discussed rely heavily on diversity preservation (MAP-Elites/Islands), rich context generation, and strict algorithmic verification. Ablation studies conclusively demonstrate that while the base LLM provides domain knowledge and coding syntax, it is the *evolutionary search process*, coupled with validation loops (like MCTS), that actually bridges the gap to reliable, breakthrough discoveries [cite: 4, 19, 23]. 

Furthermore, the integration of Test-Time Reinforcement Learning (as seen in ThetaEvolve and TTT-Discover) suggests that the future of AI discovery lies in dynamic, problem-specific adaptation rather than broad generalization [cite: 13, 34]. The empirically observed scaling laws of test-time compute prove that computational cycles spent during inference—iteratively mutating, evaluating, and learning—yield exponential returns, allowing highly efficient, open-source models to outcompete massive, closed-source behemoths [cite: 3, 42].

As these systems transition from theoretical sandboxes to executing codebase-scale refactoring on enterprise monoliths and uncovering solutions to 50-year-old mathematical paradoxes, they cement themselves as essential co-pilots in modern scientific and computational engineering [cite: 10, 30, 45]. Future research is poised to expand on heterogeneous orchestration (e.g., utilizing different specialized LLMs for mutation, review, and meta-prompting), refined multi-modal evaluations, and generalized, sample-efficient frameworks that democratize automated scientific discovery for the broader community [cite: 22, 27, 51].

**Sources:**
1. [vamsitalkstech.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBlDcWug_aSLdBfaMDvMucWQeGsOzlqJ-xO0vvbuZrwDWyzP0WZ7APeOku1KoTNXCjcEEkTLgnT82_L-Y7GD0l_acOe_ov_7hH5eOy7a6Pl_NvggQuRHUOOTVfBMeqzKcrKz7CQDRumDyKO106qQx4982E7lAu09-GdUwRWNswOZL3oNzwo_VJk9_YhsypYTzmha50EyigGJMrF68n5L3L-vQgOrgctMjXK4TjQ4ZUv4_lSr_zLXBbpq0g)
2. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQDXgY2ivo7bo2OxB05K60vCn08QHzT-JUMnb85o-IVhsMvNnfmZIH2SCpUqV-askxSZRAF7FzDX2JYoR0XFXKD7WlGSghmfIF5Ta6IMdh3EcJgf61COJeP1Dk-qYgC9ffni3hKTVHhBvm_VhNYmIOEXIc4V7uWMOls79QL68kzUfy0KpOEcX31Em_dsahmkZ8n0Sa9A2vZekEMOaIYAonnPZrbY_AkCmVo7G1uvWk3JEBxl_L-njI5vIHSjwBOkz9)
3. [aua.am](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHmnnqgrPnHMTgoWNMzXe_XBi7fnG3VP1UR8gbizSD4bze5cmATE4xZWQRD_V9Y9Ss_YvSjT_-X6OTN570jkuLlCkFaR3oYCnEigbYQ5-JcGDHKLupie2RHLqB-63zSBkfLkpsU2s2yaddQxwZzuNrHkkfJKawnjXiupxzO8mcYjv1k9uC7ulQNPAOp_aP_P8wIcAZ7-lXn4EalJFGJJfs)
4. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkfY4JvbmGCI5j5zJxk30XISYlxXNpyWi6t4YNQ82XTSBuKIz_Nf-LfTD5yRklNCJ4uIYxeJcd48SLLvczFR7TgxLJPoG_8xubOqw7_aH7rB9ysZAvWNu6r7KccsFUr-rz_U3LWqDgbgQKa9jqOitRpJ3dCKzpzLrqztofQxCKfCwomcvuVn2mXZwkz_WqTQ==)
5. [36kr.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDZqU4JplHrpLcqu898JoJX07UBBiZCKgscL83QZa7Cb43-ueOwpKxOEqy3mrA6EC_lCgSG5qMQDONmBhnN92bPjQ3c1Zz526Fe0R5G1T_QpCH8GefWeCbcRRD8WPdfA==)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7r2bDk7hOmfqtxltE0dsCd1mKMvYD3lYLscKEHLsqm_kOuO7MLuVmwrYlRqrLQHo33XYyjn25RYNxay6vtgQjFnhygqTllhTnMjKI1gLR4blZvBTtMnj5FIfC3iU81Q==)
7. [algorithmicsuperintelligence.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq3RJWZ1glY9xs_kuG8wcb6JOxdD_Z0tMQVP7eSpUROTbRcUIgHFaiTPUZrPfMD_qTrc01dH8XYdG0YepGFwcnU0dv9w2AHYGB_l5WPMGK7bQ0ukJRMevRujAYDHJTwlF07qzm06gYCjkqhYKgzsO5THJABN_NLA==)
8. [pypi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTlTGfE5P5oC3uQaiI1UqGJvPRyD6jVsHd54yohqCNuSzAM7y1qwVdYvCxywPWHrkxXzMZq1xm_iVVE8h4w0TVEt6WCXFiQgJv4lLR7PSht8P4tRiiGI70ptMZFfYXQgrE)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGHN7TefSVUlBDnebx5dIkD_Qfuwr2TqZfVWsOtFjQprisk9ZMl6OQeSGLEiJF2msSItyLCam6079QsvWRhOK4dJ5Z6KkEdqLbkU5e5xG_QlUihaMLaQ==)
10. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXnqqps2I-R3gSASsKH9aqT1u55HoOivjr-O7pKgzvjYm0L46FSLU6BaLD3HS-yEGxuqhHtcs3cEWGB8m6CzG5EJyyjtSn2nPd3GsVN4V2evQfFMmtIu7nFPdOFytSYVpKLZaBv8Gt0_86PG6Ipw1yn7lTNXu1WPpXPfmczDcg2ZCxEm5jecn-q0RBdMlxwxjAYEkHMu7zrgAVxDVPF0Hf1NXXXsuXV7tlywNZTz35KekbyNegGNHliIDYJ1LWaSTlfRo=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGq-ISlYFsHUukDKCihFPCHEW8GdGJESuky7vYBls-44_604KZzL6IrI7t-5Y7ImK1gEZMIgdBvnK45w_RRt3U8amxnXs9G-Z1K7N79sYVuX5osFJ38K8Sxhw==)
12. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPARZQuNE-XCvPALuDS88dWmZSjhGhAuuWkkX1EuxilOUlV4AcGBYd0QYDTYRtIvc0eqYP2-PhcBRBI0c1rJKK48KUiaDG3jZ1knhkUbcjFRL28gSXWHOHC95nEDfJSBALDw==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1-zKmNWZ7El5yQvjlQAQ-NdYmVv1Aeh4soXdVl-UqXAXhF1K_vpAj6o1RwPgwHKuEZzVb5I38LVGMs55VJ7f7ZFWlH0NukwjEqmxU3FbOQWNmbvBRzg42Og==)
14. [publicservicesalliance.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-M2nCHG-NxRqgve_amPWBxtjWYqanFpL5wJuwvPReRv4JoSwvdY0Qmmf3ztkvuPHkjgmhnLhnXCSY2hwa7zbPbdU1pABXB5ko3hCLXMqLTkgnBqPsI78vq01UhvHdwIFi-vPhm3WGID_Z4ATodtDXDWqTZPykYoVHJ8M5R93gWCJbrwmDYRIduEMVhuGC-7OO5Oq_kxEngvFwZtwRhjNFTWIAmLntsjbXRerslTyh)
15. [nyu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoSX-_0F484LmoULGrjy3bdiq745_i3sU6RPJMrLRH7Uop33PSxTx4JVMlSZ1be_vKnKZkb5nb6wi2_ewYOssxUgjjq0humMqtHdpDDGUPzmssKzURur99uewVJOcBfcU8hrKwdPqTP0PNOmk=)
16. [llmwatch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCKT2dG0e-nIcRjVO2dOw17oxEo3oHcBXMafoPhw7WRrLXr4n0dFQgC_BuG-pUoPL89iWKFj3vzgakjfTrUFVsbebjjIj_sQqG1NzQq1PJoPCPJnXYTt2MMNY8UAT_zhOcOb5RUIzwXHuna3VXgsh8ALY1Yw==)
17. [googleapis.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdXsLXRGSxZOMiXq-koEYu9Xcddi7vFtY4Qq5VvEejy16QkGCobaCu9bW7-mU4LnO-yGIT1VnrVJ4tDFKzWSweIGLljc6pqWGi0v1aEogdpusGuygbV4VFyq553RlUKLYqODa5RqIEBFoGRT3waqJys43DS2ViuzmfTAvtXrHDGjbkT-UwMrMaOMHdXc7Je0uwtugIb8Hf0QMwspWguMDgr639OurpXMLxJ1Z6SQS8X10qxSOm8HpZXGc3Hh8ZAJJYxImx94OPhU0kfBHaGmAB-W0=)
18. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2jNEAhdvi6PDL1Y6KlXO9_jclm23SV4BeBVcwOcXncDATZxI7cBkJVdcjWexpOAakXdU_k6bcm8w9tv-NVx83N_igwrZqJpbQAdTxNdBXofgVyGTyMmVZv5AoBPvOixofxgWY7YZ0_DZxRS5sXMcF-50f4YuyjtAWXlBbwncwuICxbULZ5K6ggP-jhPw=)
19. [composio.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbJ_iEDDCBHuOMx3JLW42WmKjoE_7NL4CbbogG1NRpHxVD3davgR3fok_I_WcI8PiPA4jOw42t9Qg3hDZhvOGaeqjT6gdU2UYktGGroqVDdxOPjahGH91BlmQAhDVH1LeKRvxp9IT2bAZdWdagjyYNJyCobz43rHfV5ce9AG2V)
20. [towardsdatascience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0bsq6-dL05a5XlBpJkRAhqJs4c3UBHbazpDYsGEMVCU_twnQUHyeFkcuoMfVnFLy8664sJ3DxpjnbtBfTDc71bAS4dixdTQrR8GLrmu2yVDSFj8EtDTd9VK21t9rK6_JDiUwHcR3eddInsYmIAWnTsHVkYEGduEArm9ONofyJi4bDm7zOOVWI-zMeFjEZUtlIOu-eYzMcsHw=)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwVlpHt1CyYb2Bv0PS4Ro38XqU8YrP82BWqaSZ6cmJ2xqnd-ErCY89noJUIscaEMiKE7bRgUSoc2MJ4qb0V9SBlSRAkc59_GHBUSNMdVJ6r-z5DR4vOM4lC6FN5oI=)
22. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtCO9MpuSFbjBLCliQBNKXvFaS8GWLaxbYVEMLec6c-QINLUPEWEAWUO3MZm5jIrNF_b3fsD_GQZii6xAqwwqxZvTyJLFwnWTFJRPcT-iGw0RdvpWiJKmaiS1WvQh2xGhcs-RxLg==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUMMGeFdxudC2I0FPlX9nyXfBInX2-gsjpdWrWJzhADl49cNAgoiCUF-Rhb-0_sCpIVM1-S3d2aEjnTP-6HjItmqje6RKJaJp3WZlXw_FMtiVVoWfA-g==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnmDS2XHfZzEvib3aAMhjeGM0IYxcdL2dbInmXOimtQQj_XtgdxF8i3bdoHXzDlSr0L1WNAQpLTb_2a1jzOMzj_stQwd2RdHTjyDhVTY4jMkipCIuMCg==)
25. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJU2qucqdMjotPWuu_3w82K_dNLgsOahw6nYeR-2-l3wKUm_vcoVcGQEjiKG_0noDzcxJsGzLEjYwO3Eh9D3T5RmlyWnh4OK6sxMHsf_gUzPEQJ46qwIQ1aT6XaI74QbU5Vyuz_FZihAiMI4-8Rfjq7AzVxDMARkNpat3md2sGCoqQtLnesxbGwi0Earjn8ZAguScsffboYf9vxu0ChpUxhhrfR90GHw-1ASoGVH0CAW8RaiecWVnZ3Q==)
26. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFCKLHVJurJoYPUK3Ms-y98d9cLy1XWVAX8xwUBfYe4D334T0gWIu5KvNYOgdOaZDYsz-6rpDObZJPiHo0eHueKnSTym9aRiaHuBfzuzQ6bP7qAQoleuSu3otcEuwJz4OPahiGZXsAg-tGHt5XY7P7ZELcWU028tszRC4oN3XPry5941MkEJJfwJCVJpfGhn1yqKMCce2BxzaTVSuNMvGCvFXQ_9uSxaw2xdzjrpd_5fvrgLKcmnSrNwygVJNiodiHxfAtfHaUD0Rd6E47mSoAQAW_ryDLlA==)
27. [sakana.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwOyHVs95O0-LM_LQAAKOWlzVnLjKAjeNYrM6jZrIeWj4d88JNkSa4jXFrnftrGyvgOAlZr_Qt9R9jtaX1Nq1jbhP9yRxPlz0XJOYQnB_dw91yN5DCDg==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOwqfvzW0QvXCnEsz5-Jb6MdHsBQN0tAs_84rbv0yn-GTLEpxxMv8NjCYDR5sTF5YaqyLmo2izjO_u5VlpCd9kO3aSexAXkuL7yp2ihUXPEhw83HX8tA==)
29. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzdFjaVk2uZ0ARFfqQ6aQ1brfyQZm0yXUcJovOwk-sDHWzU72WXPlFryCziPf5Io0vn3QbQ3IsuF__8IXRAlLgcoTm8gjL77WyM_vYquckiUKKKVwuG-k40JB66DdCNxQr5Q==)
30. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGp9u8VOTPpBq_HdHiuWTS7ldA-QpayhPOeZ6239zCVBNiBEeKsfGW2gWpwJFS7KQma63zZwcK2axO2Zs7b0vfvg-9DNbdZWa2uFfLy6HY75DqusvinsoyABhjUrS3QrjLEyZXf9ReVstsLMcsr83y-d6KhAsyDpc7NJFDFcOwnfRSa-sniX2hC8f-AdWkM5pZOD3In7u1IPef_jLgObjLxeaN8N9I9c9MI6DIzeUvdTMrsG86r5Y6jJk19CVaVlYHQVA==)
31. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5Cg5OpxSkvgXNwxT1VJJ7H8p9mZbdtwsxCTrEHrjRmnADYD9hhd41JyQXGmZ2ZpnooD1ZAH2vPFFQJI9j8bnFOFeKMC9f-VALmv1BqKYNEo_LS70UFav8cPXvFGr9Qhk=)
32. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLTSunuSeY-OK7pwQN4Efbh1N7N9miQFUPr9ZCgcGy-2UGpNyUdG12p_PiLTTooaOTjERyjDNTQ-Qwc_avQZtFgKzs8FzpkTD-69kLmkxe_nrcFVJ2tRx5ygjri0myB0V8)
33. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFPR2z-x2PD6Jb9dtRyZ_le_OA76eT07jkoo4P5Og2E_Jpg0xh_2p4UEv5aIQNipHFxmSiAylyleYObCJ-Q3-MYaZZs9sobpT-dhcbChKWKk_5xi6fj2bFewGLOhhN)
34. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLQ1OIqHxrdMIRXHRcCUjXhdSm2gucT7Dz2h1ht4csE0ENRBrzZe5Gc75yB3wffIqSs3AQfFg2MCpN4HvkjhVeLSc5AObRDvymYZY8ZKyoiQJWI4UFkZQR5rYyApawQAAwgkdSvYi4Mz4Ifc6SX-5JZNKoTb9lgu6mYUFxSz9nOyHhJq-4)
35. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOtFZhGM_p8q0chgdlPh069EyQe4Ya4W__DgLcp1YMdpf6zh7MqHFADw2l24LBW9_5tL-rMZTtK_G1R8v1sSloal3N7i6nAacdGXz6NG8NUABaa7l7BFjys4fBz1Ba)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-rg9lF3_ndhqHy1cY0FTld-hMxgB8naw6jKk99wCNu0dvmro12yaT6Ig56sW_2psCAhKRqFJDo44I-fXe7EuTm7KFRgQAZzmcVl2WCbsrcH8gicSZN66wKQ==)
37. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElLwwHnk8AT7u1zx68rS-HQyNjFQyKtWqLZA4vMJqPkv4PMjX6bbZV8YyMDhPMR5I1HJfEQntsIdIhDXymZ9S8EiPpQCWmnWun2g3R5OiP_zeTPCLKVk8BWE0Tyzfqq_S8PtFy)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUxwLUJ_mpc_NnmQcMGTmEv6zqTiBvs3XeISjKX_A07oD6rYWh9O04r1Nz8FLG9qQ-4Y98FN0rjLWZakZlavI7mN8B84osbUXbzuAIpttS639Stx1D10-W0Q==)
39. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU01SNVJw87lErWkrD2qws_qYw-jS1wvkEd6n50lmfywZSux-W0biYKsHs_1tQ7cwkLvyKIJsjeWZyIBQgIxSl-uADyMlRGVMAMXE5kaZYs6ahVcECQLKjE89loFPt544=)
40. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCDzBSpHCqeXrulQI3yy998jIBLVN8wmTu5mDsICD1bMG0XOse5I9gJPvAB-b8IcW_yJVKxFfFaAh4xah1Fo2Tih4HZGL_oVjiWXtLGBL6mfB-ZGOOtKW8hvadUmLlswP-33aDhCj0yb6ILoduihIcKqjRH6n1VRzN5_b3tqI6FzqM3BqXOWY99aAiV_Ixf2s9P1I6iGtH9-7Fcg6ed7CyBTc=)
41. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqVtOndpESkJ6Bx1-L4XXRZlBhui9-lCL2BRGVu966kM2WvSd5IiG1qIycyv7DODdOhx4zu4GBzX6qxnCGkEqtnwNEHn0GeKWGoGhUW6iH8G6U_E2b_eGZ8oMK4g-qJFpuocC31uPeryyuHQfRgugunSDb9vuJ0sel-KBI9XAT30hprjxSR6mbpJHHIDlcoUrdslzPEvqC)
42. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwPb4OdrHy0-hEmgQzyusUOJL2VXg5qXiwqB6GN9fvHrF2WsM2lX-CFJZ00A6ct5v0PxF-PvaCAIi7-VtK39mnVY014vBS3PE5xmv7e4RieQG8vOfhfxWW)
43. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoiwhKKclD3XV_MrI3U7Uj_qyvDyZJFni2XD1nXdDbZ64-PCuEANjjKjMFS1EwI6FNvHsvmz_FxLQ3lcvX4AB5pB4inpmIj0bMYYhYPO65p25VH6OKml_m0QW5dQc=)
44. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHk4HdMRSPXOgx7pATJZKYpHYn-msRNdFyU3tear5BER6hUfCTWvV0zpCWp7i7CriY6QGDiPcriRoMkGCvd3E0q9KM_Uj9ajuHe2syw4XujuAkE8v0_hbNC6PnF__oKmVBc-U_Kq6QF-57xcHMSVw6my2MR3Rfwawsj5SeKVNt6YyHwGiBZexQI8R-MTKq400QO3sx-8bNzF_N0V5I=)
45. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7vb4SOiVJWQfOkrf_Y2li9n0ZK7afLcqyE2U5gIdkqcCYzJovHqa_BC7Kc-1xpUUAkN2zA0uiXhmOOPtfX1hssU9fLFB9goq_hWsZ8-VmIROf8cnfcKzPY2GIdsFG5tHbTg7oiKo=)
46. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtoZ4zBsHfsXbUcY091tlUOtkam65_jLVG_QK0CRG0KXxuiq6AyVoCmzz9G-DXEl05Zbzo4P8nKLrLG6qG-AKNK-kqHcHw3Sz_SAvLvMStGEl15X7X57OIqASKWxxIP2flSWyg33d-jBiH5qP2-A6VJuIYkldj2btkVOJ9aJ1g4FVObkNx3OKx5rvbAelXO__Av4Ct_jrUM-kjPk-Vcu03W5l2C70c5QZbOuEV4Opv)
47. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFETUHuvctkNpLgEJRSTPJUmidKc8Mya_yu2idTyYbvmT7XRInjliW0gxZL55kpI59OL_2jvo8djZhHgzNZ9XqSWagbR-Ee_RIJ7qGJR1VnPks6eqNXZA==)
48. [blog.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQMEYC6oVGbRrGimoEWjjXK7UgJPFM8TC5u6s2chDYS81MJih4MHpYwzd9cDGbtKqmvzupY846vtdh9tmjrdcaUK6GQIdP7OrbH1r9a5iROnni1Cx3DcX74JDD80bHmOgoNKBq88v2vtjHlzY6yAnoTJXrfyx7UMLz3ci0xLHLTJvWV2ECy1XHWOunIvfacVeUYCAuzTk=)
49. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN5VkjalqfOlZYE_wmX3R_RJd-Drm3EkcWPH9PUcC1X71_6OdYvq69PzcknKSXhYIJ1WznGRVsSUJ-K1Bjqqzmj99J8yHSFqo1RzPlEiQMWoqMVYlHux4SzmoPt9i39JM=)
50. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQgC6QJ17KYkf4qJ8oFfZABogGtpTXBmJnQOizBAW0RXZjww2GHcHZnpO9a1HaKCc0vuX9WTPeRV42mOz3W-RwS0csgeo2d2lr6DY6qzxi3Ox3iF7gwc2YS4hfZvsuo1j_mA==)
51. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpcKcGhyvFV_LK9UhWGWjDRji0_wPTqC3OxGOjpLGhiRSNObH0EYII8EM99b8fBvpPc3XaYM5Y6PE5V2ndoJGpn84LkDue7G3C6ykKQK_U5HV0h68cSt6XXg==)


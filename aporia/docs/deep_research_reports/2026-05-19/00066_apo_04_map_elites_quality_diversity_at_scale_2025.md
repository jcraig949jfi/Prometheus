# APO-04: MAP-Elites quality-diversity at scale 2025

**Pythia queue id:** 66
**Tier:** T1
**Priority:** 2
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdNbDRNYXN2SUlJcWI5TW9QcjhiaWdRMBIXTWw0TWFzdklJSXFiOU1vUHI4YmlnUTA
**Elapsed:** 380s
**Completed at:** 2026-05-19T13:03:43.401624+00:00

---

# Large-Scale MAP-Elites and Quality-Diversity Optimization (2024–2026): Empirical Results, Scaling Trends, and Algorithmic Innovations

**Key Points:**
*   Recent research (2024–2026) suggests that the integration of Reinforcement Learning (RL) and Large Language Models (LLMs) with the Multi-dimensional Archive of Phenotypic Elites (MAP-Elites) algorithm has significantly accelerated the discovery of diverse, high-performing solutions across complex domains.
*   The evidence leans toward unstructured archives (e.g., Dominated Novelty Search) and Centroidal Voronoi Tessellations (CVT) being strictly superior to traditional grid-based MAP-Elites when scaling to high-dimensional or unbounded behavior spaces.
*   Hybrid Quality-Diversity-Reinforcement Learning (QD-RL) frameworks, particularly target-free architectures like QDHUAC, have demonstrated dramatic improvements in sample efficiency by overcoming conventional RL bottlenecks such as target tracking lag. 
*   It seems likely that evolutionary algorithms uniquely absorb LLM failure modes—such as "cognitive entrenchment" and "mode collapse"—converting homogenization pressures into harmless archival redundancy while preserving global exploration.
*   In domains characterized by high uncertainty and stochasticity, specialized Uncertain-QD (UQD) algorithms (e.g., Extract-ME) are increasingly necessary to prevent archive drift caused by structurally deceptive or "lucky" fitness evaluations.

**The Evolution of Quality-Diversity**
Quality-Diversity (QD) algorithms represent a paradigm shift from traditional single-objective optimization. Rather than aggressively converging toward a single global optimum, QD algorithms seek to "illuminate" the search space by discovering a repertoire of solutions that are both highly performant and behaviorally diverse. MAP-Elites, the flagship QD algorithm, originally achieved this by dividing the behavior space into rigid discrete grids.

**The Convergence of QD, RL, and Generative AI**
Between 2024 and 2026, the intersection of deep neuroevolution, RL, and LLM-driven program synthesis fundamentally altered the MAP-Elites landscape. Deep RL provided the gradient-based exploitation necessary to efficiently search high-dimensional parameter spaces (such as large neural networks), while LLMs enabled the evolution of semantic constructs, source code, and multi-agent interaction architectures.

**Scaling Limits and Failure Modes**
Despite these advances, empirical studies document notable failure modes when scaling MAP-Elites. These include the curse of dimensionality in fixed-grid archives, training instability in high Update-to-Data (UTD) environments, and cognitive entrenchment in LLM-as-optimizer setups. The period of 2024–2026 is distinctly characterized by the introduction of robust, mathematically grounded mechanisms designed specifically to address and neutralize these failure modes.

## 1. Introduction to the Modern Quality-Diversity Landscape

The primary ambition of evolutionary computation has historically been to mimic biological evolution's capacity to produce a vast array of specialized, highly adapted phenotypes. For decades, however, machine learning and black-box optimization remained overwhelmingly dominated by single-objective convergence strategies (e.g., standard gradient descent or traditional genetic algorithms). In response, the **Quality-Diversity (QD)** paradigm was established, fundamentally shifting the optimization objective: instead of searching for the single highest-quality solution, QD algorithms search for a diverse collection of high-quality solutions spanning a user-defined behavioral space [cite: 1, 2]. 

The **Multi-dimensional Archive of Phenotypic Elites (MAP-Elites)** algorithm serves as the foundational architecture for the majority of modern QD research [cite: 1, 3]. Operating by mapping high-performing solutions to specific behavioral niches (cells) in a phenotypic space, MAP-Elites builds a comprehensive archive that explicitly illuminates the performance topology of the problem space [cite: 4, 5]. 

Between 2024 and 2026, MAP-Elites experienced unprecedented scaling. The algorithm transitioned from navigating low-dimensional, deterministic robotics tasks to orchestrating large-scale deep neuroevolution, optimizing generative adversarial prompts across billions of parameters, and discovering novel algorithms via LLM-guided program synthesis [cite: 6, 7, 8]. This report synthesizes large-scale empirical results spanning this period, comprehensively detailing archive sizing, illumination quality metrics, advanced niche selection techniques, and the fusion of QD with deep Reinforcement Learning (QD-RL). Furthermore, it exhaustively documents the algorithmic scaling trends and critical failure modes that shape current frontiers in artificial intelligence optimization.

## 2. Archive Sizes, Scaling Trends, and Niche Selection 

The canonical MAP-Elites algorithm operates by discretizing an \(N\)-dimensional feature/behavioral space into a regular grid [cite: 4]. Each cell in this grid stores exactly one "elite" solution—the highest-performing individual observed that exhibits those specific behavioral characteristics [cite: 1, 9]. However, as domains became more complex (2024–2026), the limitations of this rigid discretization forced a rapid evolution in archive structuring.

### 2.1 The Curse of Dimensionality and CVT-MAP-Elites
In standard MAP-Elites, the number of niches grows exponentially with the dimensionality of the descriptor space. A 50-dimensional space, even with minimal discretization, requires computationally impossible amounts of memory just to store the matrix of pointers [cite: 10]. To combat this, researchers widely adopted **Centroidal Voronoi Tessellation (CVT)-MAP-Elites** [cite: 1]. 

CVT-MAP-Elites scales QD to high-dimensional continuous behavior spaces by leveraging Voronoi tessellations to partition the feature space into a pre-specified number of \(k\) homogeneous geometric regions [cite: 10]. Solutions are mapped to the nearest centroid, computed via \(k\)-means clustering on a reference distribution [cite: 11, 12]. This approach elegantly bypasses exponential cell growth. In 2026 empirical studies evaluating Large Language Model parameter optimization, CVT-MAP-Elites was used to scale up to massive descriptor spaces; descriptor values were normalized via online z-score statistics using Welford's algorithm and followed by a sigmoid transform to prevent high-variance dimensions from inappropriately dominating the Euclidean geometry of the archive [cite: 5]. 

### 2.2 Transition to Unstructured Archives: Dominated Novelty Search
While CVT-MAP-Elites resolved the dimensionality bottleneck, it still relied on predefined boundaries and explicit distance thresholds, causing artificial discretization artifacts [cite: 13]. A prominent scaling trend documented in 2025 is the transition towards completely **unstructured archives**, specifically through algorithms like **Dominated Novelty Search (DNS)** and **Cluster-Elites** [cite: 14, 15].

Cluster-Elites dynamically addresses the limitations of fixed-grid methods by adaptively discovering and organizing the solution space through dynamic centroid allocation, without needing predefined bounds [cite: 14]. DNS takes this further by serving as a drop-in replacement for the standard MAP-Elites grid. DNS maintains an unstructured population of fixed size where local competition is dictated by "dominated novelty"—a dynamic meta-fitness measuring the average distance to solutions that dominate the candidate in terms of objective performance [cite: 13, 16].

Empirical analyses in 2025 demonstrated that DNS outperforms existing structured grid approaches across standard QD benchmarks, notably maintaining performance in continuous, unbounded, and highly complex topological spaces [cite: 2, 14]. The DNS paradigm entirely removes the necessity to carefully tune grid resolution, allowing the search to dynamically contour to the true achievable descriptor space [cite: 13].

### 2.3 Generative Representations and Semantic Genomes
Niche selection mechanisms also advanced from relying on raw telemetry or physical constraints to leveraging rich, semantic representations. 
*   **Vision-Language Models as Behavior Spaces**: The Generative Adversarial MAP-Elites (GAME) algorithm utilized Vision-Language Models (VEMs) such as CLIP to define a highly complex, 2,560-dimensional behavior space, tracking adversarial strategy evolution without human-engineered behavioral descriptors [cite: 17, 18].
*   **Semantic Genomes**: In adversarial red-teaming (2026), MAP-Elites archives were indexed using a "semantic genome" combining discrete behavioral dimensions like *strategy type* (e.g., Roleplay, Authority, Hypothetical) and *encoding method* (e.g., Base64, ROT13, Leetspeak) [cite: 19]. This approach maintained diverse attack matrices across conceptual topologies, discovering vulnerabilities where token-level optimizers experienced catastrophic mode collapse [cite: 20].

### 2.4 Archive Size Configurations in Production Frameworks
Empirical applications demonstrate massive variations in archive size depending on the evaluation cost and domain stochasticity:
*   **Massive Behavioral Archives**: In stochastic continuous control, unbounded archives frequently track tens of thousands of elite policies [cite: 13].
*   **LLM Program Synthesis**: Frameworks like *InferenceEvolve* and *OpenEvolve* restricted MAP-Elites archives to smaller, highly curated sizes (e.g., 25 elites across 4 isolated islands) to manage the extreme computational cost of cascading LLM evaluation pipelines [cite: 8, 21]. 
*   **Text/Prompt Optimization**: Empirical setups for prompt generation typically utilize archive sizes ranging from 512 (for writing tasks) to 1,024 cells (for code generation tasks) [cite: 12].

## 3. Illumination Quality and Empirical Evaluation Metrics

The evaluation of MAP-Elites and its derivative algorithms deviates significantly from standard optimization metrics. Measuring the quality of a single global optimum is insufficient; instead, algorithms are evaluated on **illumination quality**—how effectively they highlight the performance topology across the entire phenotype space.

### 3.1 Primary QD Metrics
The canonical metrics driving empirical results in the 2024–2026 literature are [cite: 4]:
1.  **Coverage**: The proportion of the descriptor space (or predefined bins) successfully discovered and populated by the algorithm. High coverage indicates broad, robust behavioral exploration [cite: 12, 13].
2.  **QD-Score**: The sum of the fitness values of all occupied cells within the archive. This metric heavily penalizes methods that discover only a few high-performing solutions, incentivizing both broad occupancy and high-quality exploitation within niches [cite: 4, 12].
3.  **Global Max Fitness**: The highest single fitness value found across the entire archive, ensuring that the drive for diversity does not compromise the ability to find absolute peaks [cite: 4, 13].
4.  **Variety and Ancestry Coverage**: Metrics that evaluate the genealogical distance or unique stepping-stones contributing to final elites, ensuring that the archive is not merely populated by highly correlated permutations of a single genetic lineage [cite: 4].
5.  **Area Under the Curve (AUC) of QD-Score**: Introduced to evaluate sample efficiency by tracking how rapidly an algorithm fills the archive over the training horizon, heavily penalizing methods that eventually converge but require tens of millions of excessive samples [cite: 13].

### 3.2 Performance Breakthroughs
Modern hybrid methods drastically accelerated illumination. For instance, **Covariance Matrix Adaptation MAP-Elites (CMA-ME)**—which integrates CMA-ES emitters for adaptive search—demonstrated the ability to increase both archive size and QD-Score orders of magnitude faster than vanilla MAP-Elites. In the high-dimensional *Rastrigin-multi* benchmark, CMA-ME achieved equilibrium QD-Scores in under 500 generations, a milestone that required over 10,000 generations for standard MAP-Elites [cite: 22].

In adversarial generation domains (e.g., jailbreaking modern LLMs like Llama-3, GPT-4o, and Claude 3.5), MAP-Elites mapped the vulnerability landscape with unprecedented illumination. In experiments on Llama-3-8B, MAP-Elites achieved an exceptionally high QD-Score (366.9) and 63.04% behavioral coverage. More impressively, it successfully isolated 370 distinct diversity niches of vulnerability, vastly outperforming single-trajectory gradient attacks (like GCG) and standard LLM-as-attacker models (like PAIR and TAP) [cite: 7].

## 4. Deep Neuroevolution and Hybrid QD-RL Methods

A major limitation of classical MAP-Elites was its reliance on simple genetic operators (random uniform parent sampling, Gaussian mutation, and crossover). While effective for low-dimensional phenotypes, these operations are notoriously sample-inefficient in high-dimensional spaces, practically prohibiting their use for evolving deep neural network controllers [cite: 23, 24]. 

The solution, fiercely iterated upon through 2024–2026, was **QD-RL**: hybrid algorithms that fuse the divergent search logic of MAP-Elites with the sample-efficient, gradient-based exploitation of Deep Reinforcement Learning.

### 4.1 The Evolution of Policy Gradient Assisted MAP-Elites
The foundation of modern QD-RL is **PGA-MAP-Elites** (Policy Gradient Assisted MAP-Elites). PGA-MAP-Elites runs two independent variation operators in parallel: a standard Genetic Algorithm (GA) operator to maintain divergent exploration, and a Policy Gradient (PG) operator based on algorithms like TD3 (Twin Delayed Deep Deterministic policy gradient) [cite: 25]. The PG operator leverages an asynchronously trained critic network to estimate gradients and direct mutations strictly toward higher-performing behaviors [cite: 25, 26].

While PGA-MAP-Elites enabled MAP-Elites to solve complex continuous control tasks, it suffered from a fundamental flaw: the standard RL critic is purely objective-driven. Thus, the PG operator would aggressively push all solutions toward the global optimum, directly undermining the archive's diversity [cite: 27].

This bottleneck was resolved by **DCG-MAP-Elites** (Descriptor-Conditioned Gradients MAP-Elites). DCG-MAP-Elites replaces the standard actor-critic model with a *descriptor-conditioned* variant. The critic evaluates the quality of a solution *given a target behavioral descriptor* [cite: 28, 29]. Consequently, gradients push solutions not just toward a single global peak, but toward the optimal performance *for their specific niche*. Furthermore, DCG-MAP-Elites enabled "archive distillation"—training a single, versatile, descriptor-conditioned policy capable of executing the entire range of behaviors stored in the massive archive at no additional evaluation cost [cite: 27, 29]. This innovation improved QD-Scores by 82% over PGA-MAP-Elites [cite: 27].

Subsequent iterations, such as **DCRL-MAP-Elites** (2024), further optimized this architecture by utilizing the trained descriptor-conditioned actor as a generative model itself. Instead of relying solely on the critic to shape mutated offspring, DCRL-MAP-Elites queries the actor to directly generate diverse solutions that are instantly injected into the evolving batch, drastically improving both the quality and sample efficiency of the population [cite: 28, 30].

### 4.2 Overcoming QD-RL Bottlenecks: QDHUAC and High-UTD Training
Even with descriptor-conditioned gradients, QD-RL algorithms required tens of millions of environment interactions to solve standard benchmarks due to low sample efficiency [cite: 31]. In conventional deep RL, sample efficiency is artificially increased by raising the **Update-to-Data (UTD)** ratio—performing many gradient updates per environmental step. However, high-UTD training historically destabilizes evolutionary populations due to "Target Tracking Lag" caused by the Polyak averaging used in standard target networks [cite: 32].

In 2026, researchers introduced **QDHUAC**, a sample-efficient, target-free, distributional QD-RL algorithm designed to bypass this bottleneck [cite: 13, 31]. Key innovations included:
*   **Target-Free Distributional Critic**: Removing the delayed target network entirely allowed the critic to instantly track the rapid distribution shifts of a diverse, dynamically expanding evolutionary archive [cite: 13].
*   **Hybrid Normalization**: To prevent the critic's gradients from exploding under high-UTD regimes, QDHUAC utilized a combined Weight and Batch Normalization architecture. This created a highly stable trust region in the parameter space [cite: 13, 31].

Coupled with the unstructured Dominated Novelty Search (DNS) archive, QDHUAC successfully maintained stable learning at UTD ratios exceeding 10. It achieved unprecedented maximum fitness scores (e.g., reaching nearly 8,000 in the *HalfCheetah* environment compared to the baseline's 3,500) while requiring an order of magnitude fewer environment steps than PGA-MAP-Elites and DCG-MAP-Elites [cite: 13, 32].

### 4.3 Cooperative Coevolution (CCQD)
Addressing the vast parameter spaces of deep networks from another angle, the **Cooperative Coevolution QD (CCQD)** framework (2025) structurally decomposed policy networks. Recognizing that evolving monolithic neural brains is highly inefficient, CCQD separated models into two specialized layers: "representation" (perception) and "decision" (action) [cite: 33].

By simultaneously evolving a massive population of 1,024 unique decision-making components but strictly limiting the representation components to an archive of 20 shared, universal "base plates," CCQD forced synergistic adaptation. Randomly mixing and matching these components yielded a **200% efficiency gain** in QD-Score discovery. Visualizations of the final CCQD archive revealed explicit clustering, where distinct base plates fundamentally anchored entirely different families of learned behaviors [cite: 33].

## 5. Large-Scale LLM-Guided Evolution and Code Generation

The most pronounced scaling trend observed from 2024 to 2026 is the application of MAP-Elites as the central orchestration logic for AI-native software engineering and algorithmic discovery. Large language models inherently suffer from limited continuous reasoning horizons, context window saturation, and single-trajectory degeneration. MAP-Elites mitigates these weaknesses by framing long-horizon coding and scientific tasks as large-scale, population-based systems problems [cite: 34].

### 5.1 GigaEvo and AlphaEvolve
Inspired by Google DeepMind's *AlphaEvolve*, the open-source **GigaEvo** framework (late 2025) cemented the role of MAP-Elites in rigorous mathematical and algorithmic discovery [cite: 6, 35]. GigaEvo integrates four primary components:
1.  **Asynchronous DAG Execution Engine**: Processes generated code through highly concurrent stages of validation, complexity analysis, and isolated execution, preventing brittle pipeline collapses [cite: 6, 36].
2.  **LLM-Driven Mutation with Bidirectional Lineage Tracking**: When an LLM mutates a candidate solution, it is provided not just with the immediate parent, but with the entire genealogical ancestry—detailing which mutations historically succeeded, which failed, and *why* previous evolutionary branches were pruned [cite: 6, 9].
3.  **Island Model Evolution**: Maintaining parallel populations that migrate periodically to prevent premature convergence [cite: 35].
4.  **MAP-Elites Engine**: A database discretizing programs into a 2D space of objective fitness and binary validity [cite: 36].

Empirical evaluations of GigaEvo effectively reproduced and matched AlphaEvolve's performance on notoriously difficult mathematical problems, such as high-dimensional kissing numbers, Heilbronn triangle placement, and online bin-packing heuristic generation [cite: 6, 37].

### 5.2 OpenEvolve and Multi-Stage Cascade Evaluation
Similarly, the **OpenEvolve** architecture (and its derivative, **InferenceEvolve**) utilizes an LLM ensemble layered over a MAP-Elites grid to generate novel scientific algorithms [cite: 8, 21]. To drastically reduce the compute costs associated with running billions of LLM tokens, these systems utilize **Cascade Evaluation**. Candidate programs undergo lightweight, fail-fast compilation checks and small-subset data evaluations. Only candidates that clear these preliminary thresholds are promoted to full-suite computational evaluation, saving massive amounts of compute on malformed solutions [cite: 8, 21, 34].

OpenEvolve's Prompt Sampler generates context-rich mutation requests by dynamically pulling from the MAP-Elites archive, curating a specific "evidence set" for the LLM that includes top performers, diverse extremes across behavioral bins, and execution artifacts (such as trace logs and error stacks) [cite: 8].

### 5.3 Adversarial Red-Teaming (Rainbow Teaming and Semantic MAP-Elites)
MAP-Elites has proven exceptionally potent in AI safety. Methods like **Rainbow Teaming** apply MAP-Elites to generate diverse adversarial prompts, achieving over 90% attack success rates on aligned LLMs by treating jailbreaking as an open-ended search for behavioral vulnerabilities [cite: 38].

In 2026, researchers recognized that traditional token-level adversarial generation (e.g., GCG) produces uninterpretable, white-box dependent gibberish [cite: 20]. Conversely, using MAP-Elites over a **Semantic Genome** produced highly interpretable, diverse failure modes. By archiving attacks across a matrix of discrete strategies (e.g., hypothetical framing, multi-turn, authority) and encodings, MAP-Elites efficiently identified explicit vulnerability profiles. For example, empirical tests revealed that Llama-3-8B was comprehensively vulnerable across nearly all semantic spaces, GPT-4o-mini suffered specifically against hypothetical and multi-turn reframing, and Claude 3.5 Sonnet exhibited robust "soft refusal" across virtually all evolutionary branches [cite: 19, 20].

## 6. Documented Failure Modes and Bottleneck Resolutions

While MAP-Elites and its derivations exhibit immense potential, empirical studies from 2024 to 2026 rigorously document several critical failure modes. The contemporary literature is largely defined by the mitigation of these specific systemic breakdowns.

### 6.1 Cognitive Entrenchment and Mode Collapse
In both deep reinforcement learning and LLM-agent reasoning, **mode collapse** is a persistent failure mode. Standard RL and single-objective LLM optimizers (like single-agent *Reflexion*) suffer from **cognitive entrenchment**: when reflecting on its own failures, an optimizer gets trapped in local optima, repeatedly generating identical or highly correlated solutions because its own reflections reinforce its pre-existing assumptions [cite: 39]. Traditional methods applied explicit "diversity penalties" to cost functions to prevent this, but these artificially oppose the reward-maximizing objective and treat the symptom rather than the cause [cite: 40].

**Resolution**: MAP-Elites acts as a fundamental structural countermeasure to cognitive entrenchment. When an LLM or RL agent experiences collapse and generates near-duplicate outputs, the MAP-Elites archive absorbs this failure mode. Because the duplicate solutions map perfectly to already-occupied behavioral cells, they are instantly discarded. Thus, the intense pressure toward mode collapse is safely converted into "harmless redundancy" without dragging the entire active population into a localized attractor basin [cite: 5]. The archive perpetually maintains multiple, distinct stepping stones, ensuring that when one architectural path hits a performance ceiling, completely divergent sub-populations remain readily available for continued evolution [cite: 9].

### 6.2 Target Tracking Lag in Deep Neuroevolution
As discussed in Section 4.2, when utilizing QD-RL hybrids (e.g., PGA-MAP-Elites), scaling up the Update-to-Data (UTD) ratio leads to severe training instability. Standard deep RL algorithms utilize heavily delayed "target networks" (via Polyak averaging) to stabilize the Q-value estimations of the critic [cite: 13]. However, in an evolutionary system where the population distribution is shifting radically and constantly expanding across diverse niches, the target network simply cannot keep up. This **Target Tracking Lag** results in catastrophic value divergence, ultimately causing the gradient-based mutation operator to fail entirely in high-dimensional tasks [cite: 31, 32].

**Resolution**: The development of target-free architectures. Algorithms like QDHUAC completely eliminated the target network, relying instead on a highly synchronized distributional critic tightly bound by joint Weight and Batch Normalization. This specific combination was proven uniquely capable of preventing long-term value divergence while retaining dense gradient signals [cite: 31].

### 6.3 Noise-Induced Archive Drift (The "Lucky Solution" Problem)
A foundational assumption of standard MAP-Elites is that evaluations are strictly deterministic. In 2025, researchers focused heavily on the failure of MAP-Elites in **Uncertain Domains**—environments where sensors are noisy, physics simulators are stochastic, or LLM temperature outputs yield varying scores [cite: 41, 42]. 

In uncertain environments, QD algorithms suffer from a profound vulnerability to "lucky" evaluations. Because MAP-Elites is inherently elitist (strictly keeping the highest-scoring individual per cell), if a mediocre solution receives an artificially high score due to environmental noise, it permanently embeds itself in the archive. This blocks genuinely superior solutions from taking over the niche, leading to severe **archive drift** and low behavioral reproducibility [cite: 41, 43].

**Resolution**: The formalization of **Uncertain-QD (UQD)** and the **Extract-QD Framework** [cite: 41, 44]. To neutralize noise-induced drift, algorithms like *Extract-ME* (EME) implement adaptive sampling and buffered evaluation. Key interventions include:
1.  **Buffered Re-Evaluation**: Maintaining a buffer of multiple evaluations (e.g., \(k=3\)) per archive entry and utilizing the median fitness, rather than the absolute peak, for cell replacement comparisons [cite: 11].
2.  **Periodic Extraction**: Continually selecting a percentage (e.g., 10%) of the established elites in the archive per generation and forcing them to undergo rigorous re-evaluation to verify that their initially recorded fitness was not a statistical anomaly [cite: 11, 12].
3.  **Depth-Ordering**: Managing multi-tiered archive entries where solutions are ranked by their statistical confidence levels in addition to their raw fitness [cite: 12, 44].
These mechanisms successfully aligned the estimated performance of archives with true expected quality, establishing UQD as a mandatory architectural component for stochastic applications [cite: 44].

### 6.4 The Hyperparameter Sensitivity of Hybrid Methods
A persistent criticism of early QD-RL frameworks was that integrating Reinforcement Learning heavily burdened MAP-Elites with RL's native flaws—specifically, extreme hyperparameter sensitivity and high variance across random seeds [cite: 23, 24]. 

**Resolution**: Recent frameworks explicitly target this by evolving the *agents themselves* (which encapsulate both the neural parameters and the algorithmic hyperparameters) rather than just the policies [cite: 23, 24]. For example, JAX-based libraries like **QDax** have implemented scalable systems where hyperparameter schedules are dynamically tuned through population-based survival mechanics, ensuring that algorithms are not implicitly tethered to fragile, manually tuned configurations [cite: 23, 38].

## 7. Conclusion

The empirical trajectory of MAP-Elites and Quality-Diversity optimization from 2024 to 2026 highlights a definitive shift from theoretical, low-dimensional robotic testbeds to massive, commercially and academically critical domains. Scaling trends indicate an overwhelming transition away from rigid, grid-based discretization toward continuous (CVT) and unstructured (Dominated Novelty Search) archives, enabling navigation of unbounded spaces [cite: 10, 14].

Simultaneously, the convergence of deep Reinforcement Learning and MAP-Elites has overcome the historical sample-inefficiency of pure genetic divergent search. Breakthroughs like DCG-MAP-Elites and QDHUAC have proven that gradient-based actors and target-free critics can be perfectly conditioned to support—rather than collapse—behavioral diversity [cite: 13, 29]. 

Finally, in the era of Large Language Models, MAP-Elites has emerged as the premier structural framework to coordinate AI-native engineering and multi-agent reasoning. By inherently resisting cognitive entrenchment and mode collapse [cite: 5, 39], and by leveraging sophisticated mechanisms like Island Model Evolution and multi-stage evaluation pipelines [cite: 8, 34], MAP-Elites allows computational agents to systematically chart the full topology of a problem. Whether identifying complex mathematical theorems, distilling optimal prompt semantics, or mapping the critical vulnerabilities of frontier models [cite: 6, 19], Quality-Diversity optimization has established itself as an indispensable engine for safe, robust, and open-ended artificial intelligence discovery.

**Sources:**
1. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLyiSJkTJ8UI-U0888vJY6zBEF3CF4t1DNPZoApDXcHwKgwW5fgL5oJIFZo1QNs3GpCz1zLBRA9DVlOXqdjiCYnNB-_vWd491oIS0DRgYyQjuKpkblfEoY-z6m1e8=)
2. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrkS4pvOCzrOyHlkqZgh74KGQOa6v5hRDaaZDD-IgpCScu8SvUoDjK_vHnnN37--y8KUi73SPi-XGM16n-Qh58Da3yt7_UHx5tbgsfV9YwSFmckdW9SeHoi78QVz99vu8nh9dt)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWFkqy0K8N_KwRml-BhBWO1wVpUY4R_CjLmFZZRd_1QKw0OZX3uhhRoU0_9sO1ldOy-HVOmP2PZnahy6yuWwphVtuwkZB9KmKV_x3OW2sAe844_aVUZBX1)
4. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXhN2AcW_x_8M6_ZhFZtpSMrrQesdyP8UrocJHEIiIsfTrjmCKTdL6qu1mTN2DOuLjChVdO2iKAG3oafDapGy2mqprKD_fm5MuYuQI7GeT3ZHvlZEWS9oIOsPLijdD8bgGIbHwJ7feMLU9EMCz)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMlJ0m6p9FZxctNrdI_oymxsY_g8j-JkI5n0zfn558cP8gLLWtdC0-R120El2yqjSMK7B3poojeKKEPQJt7-eIi-AzLAZ20CeVO4Fdf-Jbf-526SA3B68-)
6. [chatpaper.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdZkvjIosUKN4xjz7oG2prGrsfbvFGcbl-MPbDhptvrP1VXHW1zUznNWzg3ztffpc4CRumLkb9sXVfL34ZE6t9yZdOhzvH7phb-FXyZBKLa8U9Nb2OcmU=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFCstAUKuDUoPXDr7z9njEn4eRizYA4vm7OwCL4b445keOLfELUz9QTVrbiGcprD98AkuZA3WIHF7-08y5Ozwcw9fhl0qRdPnKi5YKztDgGtFfdoDV6iTj)
8. [algorithmicsuperintelligence.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoJIPAKQC2RwHRiw0O3SfpUWb4bhTBobppS-obAMA8MuQvieOrZePH6SY2_ifQ_1bfaCKAWtosSt6-dzQ7NV0RhOQr1-FlHSEBh4BRHy5qoLK0fvMw8L7-dute7MjLF6lm-EK5AWv_dI3lvUnQhfZJaEhqPmon)
9. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjRZWzlxDl-2_jgpEqu5bnViD0WjuOpeq6TE6ZzMi0Mx6vYKpa_qsCVqd6UUML9zQ4AtLIuxAXFjuEoLG1xhO1qe-uG6_cPyTE61HoERiUpX0Vu3I_cMx8gHnOdcsp9R1ybYCZRzJwpv8lJ1BwzvAYD-75xOnIILHywoEGASWrty6jrP9m1Cv58cNKG6fI9plfBZk=)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQlaEKPD_s2zrXXc-0H19Wwni7_29bOokDob-Od76wXO2QxLuccSXa_wUSQUhBfNXcumwbdoUhUHl8gVo9u49kTbfED_YEZLLfve5O-wC2l5zjKNRd_WacKTNoaj2M-v19MrL4zPBQ2V0Ar9FreD63MuHovQ5P5kzPxZJ5FcoDRmmSe_tOPk6PvZ8Eu8lUzKP8HiruiXQvt_ekvDWGoVLHjWGm_hA_IvZOujET3IwfAbEwfuw_Y-b-d0lP)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0cqtGRS9mv5DfGxoYj-X-6550Ebmcmj51L_81nBTsBCPoFQ1_jwVC1v276KaZt9U1GT08am4MOMwm50ofcss_xp6ON8UcsQ5AYDtR0fA6__HL5gvyV3d5)
12. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqiFxbCXXIY2lFItAwSIEHaKjrcRPplKAL1UB8RJDpJtv2sCT9QJfzx8kIlCumCYowq9G5jPOoZp8iSW7_NwzJjrP5CaqDFqpUcAggJxHksnUorHwA2pOM62Vylr8=)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXOhh6Z5Yhr_14rIZfbN_WVc28FsWiONwjq-8g-936xzm8pWMd-RXepQg16SEnAr3Pv7whZlqwKR9Wsz2GULWUQBJbBmvB6bkxJimFjA1DPhZQWk3XZLiI)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ8sOfUoPpsvDkQTrEsbooL6MqUOsQrUduIUph0Ynt6Wg_lr0MhiyDIs8QZzAsvK8I6FfKQlQggKfUyk5vRzje54CChb4lYKTa3ypdsaRFykD9Acu1HR-t)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9zG8e3gfxn0XP1xZCyrsJh2uQ2RxtKHWGeVmYq968ildFQdHozvB5I_JwWAkFy9U2Vni0Cc86tkA_7AL6VktzsfyjrODSCPmCweUZPjs_CZUJ9G2u7SB3XdvdDbDFVrz8yA_TNLomSfEqngYakU-kY9qRm2bkvOvUzn8-rsKoZcWuRJJCccRNGtNFVZX6xPo0aWKKHnwhNGuEu0N8_sMve6zBbIM6hkDWwcGjSKpnU8li)
16. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeol4DR0Ix9Kx_ZjFnOjsIRibwqGiUJFZD6_u8rRL0b8WNyFTXTKuX_e96LhFYMMT3hb3XW6T5BIE6qR08hwI9TjaEwIK8X9e3pJLUewRs8ICwTU2kzkidUmPGnVNQqOBvLt2_HTzW9GmIniMUf3Q6uzPvz9-ie0qP4Ez54fg=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiU0zOEbJSAZ9ioMj2w7vArrU0yLrJbSDkVl8992wKF51WFpSUMq2BqMJ54o4p3lCitzakIxn4g7E6hVEkxBoDOmt7gEtEcRaQQI49Uj1qSfRBg5dyWyve)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQtY0GvupyYh7s32plaSrnWk_4f5WmfPWVjl9JUOVniessDhyIi43QA8aeaCg3lI__aW9infZRAzuYZqdCI2Ju9KIJ7aFtaJ5PlU8LqMWOdDEad7l7X90w)
19. [subhadipmitra.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsZIo7ZjVGiyLdfYV3QPJfG1Vb-ZqSgY_iK_Z0BlTCBl3LT-m2vMIKG2995ol2QXmerPIedoFwgLVzC8l3m-fhlUtrQSAvZ-Uco96RB-62uJ2rONrshjUcbQZnIc4cjCsNf1Bemm-P32Hrip0M)
20. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhg21UiVSRrqe2BW_wYQO4zNvZzSVhfYc0wG7eJFgeDKOU8WIOjI9vk9yZCvdyEoj2JXeNSM1gVQqW4kO5YkA7m1LRat2mmfOyrKdhnAgMUipd0ym0UyVqRRnfeH8=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJQnrPLucDK9I1M3_kOCdhETY6XLoD146aeB5cNC-bfmnk4ZE_2piyLkOSTmqcbtFosuz9gRk_viBOwDpRMkD66gQqvaf6455GUo8kafQvfkpCVek3gvvP)
22. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRS-xM8gqQ2Oi_5TZzMbVdzakybI_lFVMP0S7ccmLCt9yqr4wMfDi9Duao8kU70B7nPh0Q4Q9K24aEk1YHuUOqP8QSP9Qp8uIsleKFSrtwFeI94GuwLJ5Yr5UZZwlOnSojkQWfvbEMOV1rBLK5L3rRT4UcepVUUwtdKrzInGSi2zeloKMKOIs=)
23. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj_ZFTBFeBzfPDLCmBPr0z9gAN_zxKETS35EjeH779YDDT6uDwPaKdSxy4E9O32sApJ4aehsXi2pYJO8eIMNm2K37m-U2GAt99NvRmoLlXnbUllvUkjVzV2lzzKmnP)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPVU43PAvULTWpJqLeX5u7Lz1iI2UnQymEND4vkO8x-8F8CXemEwZ-kTr1Wum2lV7j2PwNu9_wGtX_AYUA5YFVyug8P3Ov0aHBAGTEyBQfysO9-cAc)
25. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjbW6YfYi_zb10PGyrP57UmXl3gPrsT8SZtjvNpZweKXOvdS0lYnLU2oaofcRzWdiy1dn6Q1Q2HKyoTtkyY7Vdbv0rPH1eNdm3HFLi6n4YUoolqOGumHLnSnlSxM1LqsyuS_7W1cUGeZsuNNMIqb9yDMO7Q2pZBzjR5LGNdjcT1sFhkap80V4XHggvfrDqxXap-2hwHq04KlLiU_j9EBnhe7a0KTUvSiAiCNGx)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbFzl-2S5rFnNmUD86AHwWPoJOr4bbyvrJcMPq7KJwkL9B2DR5T5Z3pJwQjtH7QkqGyiqPf2_fXJZ3WVS62QLeNhPYSohPnUjbjd074jdRl8pvaZ1NajnJL5Mcowl8bsrkqncPmuP5FWnicDA1-Umvw1vpIIZf0DzufnFf-Anp2D-V9GH9BUISvmcbkzV1AtiEcp6u2URUwZMNBFPq-WJbCIty-V-c-5xE1RfZkYRaPSb_PcM9JWf3mWX1G233eA==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTjS9VWOWeDCE3IHMf0e0Bbomt3BvOTB2xB6S5ukzM0Hu2ypvnfpMSO-XINbaT2l1h_6sTQ7tj6m0eblepK3VDrizgeg7GtFyMoemXzj2-9ZYm-Hjf)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsCxKdMpUpvUpjFfG1ZjT0Makrz-5SuGpSDREDVSOQppsIHNIrNedxrm3v9rGhAeVYg8mBS-QtGohX29nOSBE4JbZBSBdSViJxa9v9_IPjLqrYHRja4Ra1)
29. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXpW4Q-fGYP3ahyiCHLbs8OtIp_PghqiDlBRWmKbzWbJJri1u6bD7w4ZzukHgGD7-SXwQkNQtk-8cLWNNmyQWlPreZxwV-WxzBSew9oj7lEWMA_lye03NvrL8aVf1Bwoc=)
30. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhBXGPwK4gaMcjuAFyDthvaqhlRMiqVEY7Hj68huXxd4qw6gHnhwKVkottgPPpoYvFSpgrEnHSsbjclNM_Q2cpmTSybs80IYSQ2jnBYoAyGow0O5YB)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuppVggabZXcnE2gDHSRjfSPMVwvqUYJqN7Bd6FxLQQgB8N7p0daDdJ4LJIiPW1mf68t7t5vPUP2VvgSOBLErxydxzw5QCQ4U7ACvwL8-kpBKXxYl_4D_Tw4cHGpn5aQQpbhI5uZnPTNh5q08URN2dMVawA2R2g4Fr-5H8sd8aymkluYxk6YFBpOBh9I6Ebi4pDw4rnIo2Fo4nnEDphOo02q1m5UXshs1Eji_YjRDk1jY_wE7kn5sTGuvVt0I=)
32. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIwH-sUew08yRy4fD4DbJuhT7lszlkOr1H3mQMMnhqO5_NOyZVVbCR9xO-VFovt3QxMusflfK9hdW9IVNeXm7TiMGkeg_dFyKuEzu8vrMRi2qHCEhSGj96VNbrg-UX-Yg026AC6YdqbN8MT1ICAb-hMOi9uBGgzJxyyaWTx-hL9aC8TctHtC1CHxUsWqBXq1bPExu54tZpAgrF2eGPPMT6KAwuxtUuDLqzfiPw2wu7)
33. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHboZD-Re-qy4d3Ad0x8Zrf-Edexa--gOB731AK28s99xKdambLibKpG2AMSGwebj7vSjefe_QrPGqCubMeRCO6I6Wzu-hLetS7CQaD06Ye1KzFmwCyTEf6-tyi2q6X45c=)
34. [gitconnected.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkzM2C11ofl9wqCzw8ww_eofT03byPsgV7lS1avZTtHj_uLLVAda9yX2rsEK-Row7oNbEe-ZFptxK2QU90IwUWsnUwP1CeZu66N9TllcmFUtcMGl5ZaA6L28AizCjoHfp2LdApQ6IvD0uv51JuKh7Em0J5vLkCtpWW4CPQdUE18n-uVkmBf5nPPAsFWFHNlvNwhku8IqP2pCOxnOz630ln)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt9YwMGEPNFDfEudimaeR8Bg4ssJ6hwM11w9ZZdK1WQHpQ3BWaxXbNu1kagtgtYMRYX8CVY3jS1E1j1B1HXnBZOHf4w3ePlwEZK1gby15zOznAwbpD)
36. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkpt9rqLgXL60BykeEAH44OeIf4KCRqoEd_imB8XLyVZGRYVis5905_i-CI562tjgA-hGE2RvBKx5frI7a-Neyz8C1UhKcBBmP5RBygUILhBxHjwcj5Mnyp1JkF7g7BShPN_fz72fZBWKqyVvNZHhtuWlN9nWZYX0ut6Gn_Zcek6BL_74Nt0gBYew0RsTi5TvypAXrzr6LNCzQ5hafmI3fANk5YzAThnP5gmATwoe0d1TqR7i1PA4w74I8oWJ8oQ==)
37. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq0Y3eTiLMabmxOsp0TyDHFbihLfdCkbg38jCQ0I1dcLRIUa2DGUXQaZyOYTsrcOHNbK47nf5aSV-YqE8rqcEv8arLv0DiEr0h6znbIaULes-UQYXzItn0ZKwc62BqsMk=)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8ju-l3X0XNjlw4-4G8plPxNmlVpNVojbY8LWZuVnZz_Clsv1rgh62MSxYME2Zd8t0EM8UicviQgfNVdqa-nyErFVwGWojbBZtPcv172lIfUbjTJD7gcBA)
39. [o-mega.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkt_IFZX5XXUEBIqUxK8v04ukAUXDEFirrWtZp0ZAcMT8OVCy9zHahN18ANIdlWkZSMntUdvhYkiMgv00q5Ifak74J81Hr5Syn8fWdZ9Hf08MsMW_Nhihgq14fhw6Ex7D-AaorgPiMX8e3dmfVpjavH0znFloDOQ==)
40. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI5nO4gCAZWNfmhtmLdcutLUs-WHsQ8iuC_c4djrebD-iQljvg5kYpnI3ptJIon8yRsmwnUR7UQgGJGz7VZUmofITWKUOCfzEOJab8X8sxtJXduU0c_27HBGi4ajIPJK8ZRxPMYKYIRoDzqDwJf_orwgIsGmq8j_442no=)
41. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1umSA_7Pkrz5xZP0ciat44Iw0oTauqybo0fPFvH6uf7x4nTTGgTrb72mkIwqOW-R0KpcJSRLQbj6ltiEarNCf-_nHC35SJdBCbJRt5PtHOuWmtGCOCbRWFmzsQVDuumECJI5adNilW2mcFB28latgskYG6BHkwoGtuVkPB1y4xAJKUShdD6XgXR_59UY-2WsSf_wIzolMzLvWB_QS_Qrf6kI9LGr6hp_0uKDASsgIN9SBEL55WgYIDO2E9sBTr-6kXvBWf0v13bM5TGjK_SYQKjG_6xw1)
42. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZodIaOjQA2w5GhInKqmSz7S0D38SUJHx6WlFeq9lW6FWkP8J2ygK8uOJr1bKrwd6TyNuKDHCFY1h5B1xvMLE2pQ6oyK07TftVW40WvS6r58gUz99Ah2xyoyOcnAAvrvLn-YoR-rEBFULU4nBpMXgHPBD9FzvWg7dRmsYFhHiJPLk=)
43. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl2lDzqYp4Kcs5s6Bfl5LxTwDscMsrX0eFAJy8XZBoioJMPcw6KoBE7BItcibKwN1ioWT6S00J0RuYKpBHr2lIAJLl2v9tfgYXWoCG30ZV92qmX87g-r-Zu-iL4eV2J9I0m_RZZiq5oS45Crgkd3D4vK8tyWACYmGBlEzNo8PsVEZcHbcmkBuMjN1mshf81d1AJbiecjQ-)
44. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2gP7aafN11sxJv7LDnAMCHYM7r7XPZ96GKNPLjRRXBRnl8mBP2hTCxJJdRr6c1ImIgAoUIU5xz_6PCNFtb85kweTfay8YiM3K0b91Bt_DtSBA-LLN76nu)


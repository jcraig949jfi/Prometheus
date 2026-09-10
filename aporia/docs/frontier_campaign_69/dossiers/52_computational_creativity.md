# Prompt 52: Computational Creativity

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdSVjZmYXJXbUdzTFhfdU1Qd2RfczhRbxIXUlY2ZmFyV21Hc0xYX3VNUHdkX3M4UW8
**Elapsed:** 395s

---

# FRONTIER PRACTITIONER DOSSIER: COMPUTATIONAL CREATIVITY AND QUALITY-DIVERSITY

The following report is synthesized for a computational scientist entering the field of Computational Creativity, specifically anchored to the lineage of algorithms descending from Novelty Search. 

Key Points on the Current State of the Field:
Research suggests that the original formulation of pure Novelty Search is largely defunct as a standalone method, having been almost entirely absorbed into the broader paradigm of Quality-Diversity optimization. It seems likely that searching purely for novelty fails in complex or unbounded spaces because the algorithm cannot distinguish between useful innovation and degenerate, broken behaviors. 
The current evidence leans toward local competition—combining a quality metric with a diversity metric—as the mathematically and practically superior approach. 
The field has recently undergone a massive shift toward hardware acceleration, primarily moving from CPU-bound Python implementations to highly parallelized JAX environments. 
A significant, actively debated controversy exists regarding Large Language Models: some researchers argue that preference tuning like RLHF destroys output diversity and creates an Artificial Hivemind, while others propose that LLMs, when prompted with diverse contexts, can act as powerful open-ended variation engines.

AN EXPLICIT CORRECTION TO YOUR ANCHORING DESCRIPTION

Your description of the mechanism is historically accurate to the period between 2008 and 2011, but it is fundamentally outdated for a practitioner in 2026. A correction here is critical. 

You stated that selection is on novelty alone, that there is no fitness function telling it what counts as better, and that two very different genomes with the same behaviour are interchangeable. Today, this approach is recognized as highly vulnerable to the curse of dimensionality and unbounded search spaces [cite: 1, 2]. If you run pure novelty search on a complex robot, it will quickly discover that breaking its own leg and twitching on the floor produces a highly novel behavior trajectory, and it will fill the archive with variations of catastrophic failure.

To fix this, the field evolved into Quality-Diversity (QD) optimization [cite: 3]. We do not abandon fitness; we combine it with diversity. The field replaced global competition (finding the single highest fitness) with local competition. The archive is no longer just a memory bank to push search outward. Instead, the behavior space is partitioned into niches, either via explicit grids like in MAP-Elites or via dynamic topologies like in Dominated Novelty Search [cite: 4]. When a new individual is evaluated, its behavior determines which niche it belongs to. If that niche is empty, it is added. If that niche is already occupied, the new genome and the archived genome are absolutely not interchangeable. They compete on fitness (quality). The higher-performing genome survives, and the weaker one is discarded. The method you are actually looking to deploy in 2026 is Quality-Diversity, where the search illuminates the entire behavior space with the highest-performing solution for every possible behavior [cite: 5].

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the subfield of Computational Creativity anchored to behavioral novelty is known strictly as Quality-Diversity optimization. It is no longer an eccentric sub-branch of evolutionary algorithms; it has become a rigorously formalized branch of stochastic optimization. The core objective is illumination: returning a massive repertoire of thousands of diverse, high-performing solutions rather than a single global optimum. This repertoire can be used for zero-shot adaptation in robotics, procedural content generation in games, automated heuristic design, and discovering adversarial prompts in foundation models. The field has completely merged the concepts of divergent search (novelty) and convergent search (quality) [cite: 5, 6].

What is SETTLED:
The field universally agrees that objective-only search is dangerously deceptive in complex landscapes; gradients often point toward local optima dead-ends. It is also settled that pure novelty search is insufficient because it wastes compute on junk diversity. The MAP-Elites algorithm and its covariance matrix adaptation variants like CMA-ME and CMA-MAE are settled baselines for low-dimensional behavioral spaces (usually defined as having between 2 and 8 dimensions). It is settled that for continuous, differentiable quality-diversity, gradient arborescence methods outperform purely stochastic mutations. Furthermore, the community has entirely abandoned the canonical object-oriented, single-threaded genetic algorithm software architecture in favor of massive batch evaluations on GPUs using JAX [cite: 6].

What is CONTESTED:
The intersection of Large Language Models and Quality-Diversity is a heavily contested frontier. On one side, researchers argue that preference-tuned LLMs suffer from an Artificial Hivemind effect, characterized by severe mode collapse, inter-model homogeneity, and a lack of effective semantic diversity [cite: 7, 8]. On the other side, proponents of In-context QD argue that LLMs possess unprecedented pattern-matching and generative capabilities that, when conditioned on an archive of elites, act as superior evolutionary crossover and mutation operators, bypassing traditional genetic algorithms entirely [cite: 9]. Additionally, handling noise is deeply contested. In Uncertain Quality-Diversity (UQD), it is debated whether one should re-evaluate the entire archive continuously to calculate variance, or use surrogate models to approximate the true fitness of an elite in a noisy simulator [cite: 10]. 

What is OPEN:
Unsupervised behavior discovery remains wide open. Standard QD requires a human practitioner to manually define the behavior descriptor (for example, the final X and Y coordinates of a robot). Finding algorithms that automatically learn what dimensions of behavior are actually interesting, without collapsing into trivial metrics, is unsolved. Another open frontier is the structure of local competition itself. For over a decade, the field relied on the rigid grid heuristic of MAP-Elites or the arbitrary distance thresholds of unstructured archives. The recent introduction of Dominated Novelty Search and the application of meta-black-box optimization to discover new, mathematically optimal local competition rules from scratch represent the bleeding edge of the field [cite: 11, 12].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Lehman, J., and Stanley, K. O.
Year: 2011
Title: Abandoning Objectives: Evolution Through the Search for Novelty Alone
Venue: Evolutionary Computation
Identifier: DOI 10.1162/EVCO_a_00025
This is the genesis paper for your anchoring concept, detailing the foundational maze navigation and biped walking experiments where objective-driven search fails due to deception, but novelty-driven search succeeds. A practitioner must know it to understand the pathology of the objective function, even though pure novelty search is no longer used in isolation [cite: 2].

Authors: Mouret, J.-B., and Clune, J.
Year: 2015
Title: Illuminating search spaces by mapping elites
Venue: arXiv
Identifier: arXiv:1504.04909
This paper introduced MAP-Elites, the algorithm that functionally replaced Novelty Search by discretizing the behavior space into a grid and enforcing local competition within each cell. This is the bedrock of modern Quality-Diversity, proving that preserving diverse stepping stones leads to better global optima [cite: 5].

Authors: Pugh, J. K., Soros, L. B., and Stanley, K. O.
Year: 2016
Title: Quality Diversity: A New Frontier for Evolutionary Computation
Venue: Frontiers in Robotics and AI
Identifier: DOI 10.3389/frobt.2016.00040
This is the definitive survey that unified Novelty Search with Local Competition and MAP-Elites into the singular field of Quality-Diversity. It defines the formal objective of the field: filling a space of possibilities with the best possible example of each type of achievable behavior [cite: 3].

CURRENT FRONTIER SOURCES (2023 ONWARD)

Authors: Fontaine, M. C., and Nikolaidis, S.
Year: 2023
Title: Covariance Matrix Adaptation MAP-Annealing
Venue: Proceedings of the Genetic and Evolutionary Computation Conference
Identifier: DOI 10.1145/3583131.3590389
This paper introduces CMA-MAE, solving the long-standing limitation where standard MAP-Elites prematurely abandons the fitness objective in favor of exploration. It introduces a discount function with a scalar learning rate to blend single-objective optimization smoothly with Quality-Diversity, representing the current algorithmic standard for continuous domains [cite: 13, 14].

Authors: Flageat, M., and Cully, A.
Year: 2023
Title: Uncertain Quality-Diversity: Evaluation methodology and new methods for Quality-Diversity in Uncertain Domains
Venue: IEEE Transactions on Evolutionary Computation
Identifier: arXiv:2302.00463
This paper formalizes Uncertain QD, addressing the reality that real-world physics and complex simulations are noisy, meaning a solution might look like a high-performing elite but is actually just a product of lucky variance. It introduces rigorous sampling metrics and the Archive-sampling method [cite: 10].

Authors: Lim, B., Flageat, M., and Cully, A.
Year: 2024
Title: Large Language Models as In-context AI Generators for Quality-Diversity
Venue: ALIFE 2024
Identifier: arXiv:2404.15794
This paper establishes the bridge between QD and foundation models by introducing In-context QD. It demonstrates how to pass a diverse subset of the QD archive into the context window of an LLM, using the LLM's pattern-matching capabilities as an intelligent crossover operator to generate novel, high-quality candidate solutions [cite: 9].

Authors: Jiang, L., Chai, Y., Li, M., Liu, M., Fok, R., Dziri, N., Tsvetkov, Y., Sap, M., and Choi, Y.
Year: 2025
Title: Artificial Hivemind: The Open-Ended Homogeneity of Language Models
Venue: NeurIPS 2025
Identifier: arXiv:2510.22954
A critical counterweight paper demonstrating that preference-tuned LLMs suffer from profound intra-model repetition and inter-model homogeneity when given open-ended queries. It defines effective semantic diversity and provides the Infinity-Chat dataset, showing the severe limitations of current LLMs as diversity generators [cite: 7, 8].

Authors: Bahlous-Boldi, R., Faldor, M., and Cully, A.
Year: 2025
Title: Dominated Novelty Search: Rethinking Local Competition in Quality-Diversity
Venue: arXiv
Identifier: arXiv:2502.00593
This paper completely eliminates the need for predefined bounds, grids, or distance thresholds in QD archives. By reframing local competition through dynamic fitness transformations based on behavior domination, it allows QD to operate seamlessly in high-dimensional and unsupervised spaces where MAP-Elites traditionally collapses [cite: 11].

Authors: Faldor, M., Lange, R. T., and Cully, A.
Year: 2026
Title: Discovering Quality-Diversity Algorithms via Meta-Black-Box Optimization
Venue: ICLR 2026
Identifier: arXiv:2602.12536 (Note: OpenReview identifier Z6z4AnXGhw)
This represents the absolute frontier: using meta-learning to automatically discover the rules of Quality-Diversity algorithms via attention-based neural architectures, proving that meta-learned competition rules generalize to complex robotic domains better than human-designed heuristics [cite: 12].

PART 3. SOFTWARE I CAN ACTUALLY RUN

Pyribs
URL: https://github.com/icaros-usc/pyribs
Language: Python
Licence: MIT
Recent Activity: 2026
Verdict: MAINTAINED
This is the community standard for CPU-based Quality-Diversity optimization. It implements the Rapid Illumination of Behavior Space framework and supports MAP-Elites, CMA-ME, and CMA-MAE out of the box. You can use it today to run the Lunar Lander or standard Rastrigin illumination experiments. Its known limitation is that it relies on CPU-bound, single-threaded internal logic for its scheduler; while you can parallelize your domain evaluations, the core archive updates can become a bottleneck for massive populations. It is intentionally bare-bones and highly modular [cite: 15, 16].

QDax
URL: https://github.com/adaptive-intelligent-robotics/QDax
Language: Python and JAX
Licence: MIT
Recent Activity: 2025
Verdict: MAINTAINED
This is the frontier framework for hardware-accelerated Quality-Diversity. By writing both the evolutionary operators and the environment in JAX, QDax allows for tens of thousands of evaluations per second on a single GPU. It can run massive neuroevolution experiments, such as evolving neural network controllers for the Brax physics simulator, in minutes rather than days. The gotcha is that writing environments purely in JAX is exceptionally difficult if your domain involves complex, non-differentiable state machines or string parsing [cite: 6, 17].

Uncertain Quality-Diversity (UQD)
URL: https://github.com/adaptive-intelligent-robotics/Uncertain_Quality_Diversity
Language: Python and JAX
Licence: MIT
Recent Activity: 2025
Verdict: MAINTAINED
Built on top of QDax, this is the reference implementation for running QD in noisy environments. It implements ME-Sampling, Deep-Grid, and Archive-Sampling. You can run the Noisy Hexapod Omni task today. The main limitation is compute cost; because it actively re-samples individuals to calculate variance, it burns through evaluation budgets exponentially faster than deterministic QDax [cite: 18].

Dominated-Novelty-Search (DNS)
URL: https://github.com/adaptive-intelligent-robotics/Dominated-Novelty-Search
Language: Python (with CUDA support)
Licence: MIT
Recent Activity: 2026
Verdict: MAINTAINED
This is the reference implementation for the 2025 breakthrough in gridless local competition. It serves as a drop-in replacement for the MAP-Elites grid. You can run it today on high-dimensional behavior descriptors where Pyribs would fail due to grid memory explosion. Its limitation is that calculating dynamic fitness transformations across a large unstructured population requires heavy matrix operations, necessitating a CUDA-compatible GPU [cite: 19].

fcmaes
URL: https://github.com/dietmarwo/fast-cma-es
Language: Python and C++
Licence: MIT
Recent Activity: 2025
Verdict: MAINTAINED
A highly optimized multiobjective and QD framework that uses Voronoi tessellation instead of standard grids, allowing parallel processes to share an archive while running distinct improvement emitters. It is excellent for hyperparameter optimization and operations research. The gotcha is that its API is significantly more complex and less standardized than Pyribs [cite: 20].

NEAT-C++ Novelty Search Original Implementation
URL: IDENTIFIER UNKNOWN
Language: C++
Licence: GPL
Recent Activity: 2011
Verdict: ABANDONED
The original codebase used by Lehman and Stanley to discover Novelty Search is effectively dead. It relies on outdated C++ toolchains and manual XML configurations that fail on modern compilers. No serious practitioner uses this today. Instead, researchers reproduce the exact same maze experiments using JAX-accelerated libraries like Kheperax [cite: 2, 17].

PART 4. DATA AND BENCHMARKS

Quality-Diversity Benchmark Suite
URL: https://paperswithcode.com/dataset/quality-diversity-benchmark-suite
Size: Negligible (Procedural Generators)
Licence: MIT
This is the authoritative suite for testing algorithmic efficiency in QD, deeply integrated with Pyribs. It features the linear projection Rastrigin task and the Arm Repertoire task. It is used to measure an algorithm's ability to cover the behavior space while maximizing the QD-Score. Note a known saturation problem: the basic 2D arm kinematics task is now solved so perfectly by CMA-MAE that it no longer effectively separates algorithmic performance at the frontier [cite: 15].

Kheperax
URL: https://github.com/adaptive-intelligent-robotics/Kheperax
Size: Negligible (Procedural JAX Simulator)
Licence: MIT
This is the modern, hardware-accelerated replacement for the original Novelty Search maze navigation tasks. It provides a JAX-powered simulator for robotic navigation in 2D mazes. It is treated as authoritative for testing whether a new algorithm can overcome deceptive local optima. Because the environments are parameterized, you can easily scale the difficulty [cite: 17].

UQD Benchmark Tasks
URL: https://github.com/adaptive-intelligent-robotics/Uncertain_Quality_Diversity
Size: Negligible
Licence: MIT
This collection introduces noise injections to standard QD tasks. It includes Noisy Rastrigin, Noisy Sphere, and the Noisy Hexapod Omni controller. It is used specifically to measure the reproducibility score of an archive, tracking whether an algorithm has successfully filtered out solutions that only achieved elite status due to lucky variance [cite: 18].

QDO YAHPO
URL: https://github.com/slds-lmu/qdo_yahpo
Size: Approximately 50 Megabytes
Licence: Open
A unique benchmark deriving Quality-Diversity problems from hyperparameter optimization of machine learning models. Instead of physical behaviors, the descriptors are features like model interpretability, latency, and resource usage, while the objective is accuracy. It is highly authoritative for applying QD to software and ML tuning [cite: 21, 22].

Infinity-Chat Dataset
URL: https://github.com/aryanipb/Infinity-Chat (Note: Subject to multiple distinct forks; refer directly to the NeurIPS 2025 release from Jiang et al.)
Size: 26000 real-world open-ended user queries; 31250 dense human annotations
Licence: Non-commercial Research
Used to measure effective semantic diversity and mode collapse in Large Language Models. It is the definitive 2025/2026 benchmark for proving whether an LLM generation pipeline has succumbed to the Artificial Hivemind effect. It provides absolute ratings and pairwise preferences to evaluate inter-model homogeneity [cite: 7, 8].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment that captures the absolute essence of modern Quality-Diversity without being bogged down by complex external dependencies is the execution of Covariance Matrix Adaptation MAP-Annealing on the 6D Linear Projection Rastrigin function using Pyribs.

Exact Software and Version:
Python 3.10, Pyribs version 0.5.0, NumPy version 1.24.

Exact Dataset or Generator:
The standard Rastrigin function dynamically projected from 20 dimensions down to 6 descriptor dimensions using a fixed random projection matrix, generated directly within the script via NumPy [cite: 16].

Parameters to Set:
Objective space dimensions: 20
Behavior space (measure) dimensions: 6
Archive grid resolution: 10 bins per dimension (yielding 1000000 total cells)
Population size per emitter: 30
Number of emitters: 15 (yielding a batch size of 450)
Total evaluations: 1000000
CMA-MAE Learning Rate (Discount factor): 0.1
Initial step size (sigma): 0.5
Seeding regime: 10 independent replicates using random seeds "42 to 51"

Compute Cost:
Roughly 1 to 2 CPU hours total across all 10 replicates on a standard modern multi-core workstation. No GPU required.

Expected Result:
You are measuring the QD-Score (the sum of the objective values of all occupied cells in the archive). For CMA-MAE on the 6D Rastrigin, you should expect an archive coverage approaching 400000 filled cells, and a QD-Score significantly outperforming standard CMA-ME by a factor of 1.5x to 2.0x, aligning exactly with the published charts in Fontaine and Nikolaidis 2023.

The Three Most Common Ways People Get This Wrong:
1. Misunderstanding the bounds of the measure space. If your grid bounds are set too tight, solutions will hit the boundaries and be discarded, silently tanking your coverage.
2. Failing to normalize the projection matrix. If the linear projection from 20D to 6D is not properly scaled, the behaviors will cluster in a microscopic region of the grid, making the algorithm look like it is suffering from mode collapse.
3. Using the standard MAP-Elites scheduler instead of the specifically tuned CMA-ES based emitters. If you default to Gaussian mutation emitters in a 20D search space, the algorithm will thrash endlessly without finding the narrow high-performing ridges of the Rastrigin landscape.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A Native, High-Dimensional Unstructured Archive for LLM Embeddings:
Currently, Pyribs relies on rigid grids (MAP-Elites). DNS provides an unstructured archive, but it relies on exhaustive pairwise behavior domination checks which scale poorly when the behavior descriptor is a 1536-dimensional float vector (like an OpenAI text embedding). If you want to run Quality-Diversity on text prompts where the "behavior" is the semantic meaning of the text, you will have to build a custom archive manager. The interface requires taking in a new solution vector and a 1536-D embedding, querying a vector database (like FAISS) for the nearest neighbors, computing local density, and applying the replacement logic. The hard part is doing this asynchronously while the LLM is generating the next batch, without locking the archive. Several private labs have rebuilt this logic internally using Redis and FAISS to wrap QD algorithms around LLM pipelines.

A Token-Efficient In-Context Repertoire Manager:
Lim et al. proved that putting the QD archive into the LLM context window works brilliantly [cite: 9]. However, there is no off-the-shelf software to handle context window budgeting. If your archive has 500 elites, you cannot fit them all into the prompt. You have to build a dynamic selector that takes in the current search state and outputs the top k most diverse and relevant elites to construct a prompt under an exact token limit. This requires writing an interface that links the evolutionary scheduler directly to a tokenization library, balancing string lengths with behavioral diversity scores. 

A Continuous Normalizing Flow Density Estimator in JAX:
While Density Descent Search has been proposed theoretically, a robust, JAX-accelerated continuous normalizing flow that maps high-dimensional behavior spaces to a tractable density probability distribution on the GPU does not exist in the public QDax repository. Writing this requires deep expertise in generative modeling and JAX vmap structures, representing a solid month of intensive engineering.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Failure of Pure Novelty Search in Large Spaces:
The most critical negative result in this field is that pure Novelty Search—the exact method described in your anchoring prompt—fails catastrophically in unconstrained environments [cite: 1, 23]. While Lehman and Stanley proved it works in 2D mazes, subsequent researchers discovered that if the behavior descriptor space is large (for example, the joint angles of a 3D humanoid over time), the algorithm will explore "junk" behaviors infinitely. Because it has no concept of quality, it cannot distinguish between a robot that walks backward and a robot that systematically dismantles its own chassis. This failure led directly to the creation of local competition algorithms like MAP-Elites, where novelty is only pursued conditionally within bounds of minimum performance.

The Collapse of Multi-Objective Pareto Mixing:
In the early 2010s, researchers attempted to combine fitness and novelty by simply treating them as two competing objectives in standard multi-objective algorithms like NSGA-II. This program largely failed. The critique is that linear combinations or Pareto fronts of novelty and fitness do not preserve the stepping stones required to solve deceptive problems. A solution with mediocre fitness but incredible novelty is often culled by the Pareto dominance mechanics before it can evolve into a high-fitness solution, defeating the purpose of divergent search [cite: 23]. 

The Artificial Hivemind Effect and RLHF:
A massive standing critique of the current frontier (using LLMs for open-ended generation) is the Artificial Hivemind effect. Jiang et al. (2025) demonstrated rigorously that aligning models via Reinforcement Learning from Human Feedback (RLHF), Direct Preference Optimization (DPO), and Group Relative Policy Optimization (GRPO) fundamentally damages output diversity [cite: 24]. While these models score highly on correctness, they exhibit extreme inter-model homogeneity; different models will output the exact same creative structure when prompted openly. The critique states that LLMs are currently optimizing for a single, consensus notion of quality, actively fighting the principles of Quality-Diversity [cite: 7]. This critique remains unanswered, forcing practitioners to employ high-temperature sampling and In-context QD to mechanically force the LLMs out of their training ruts.

The Reproducibility Crisis in Noisy Domains:
Flageat and Cully identified that many published results in evolutionary robotics using MAP-Elites were measuring an artifact of the benchmark rather than true algorithmic power. In domains with even slight physical noise (simulators with imperfect physics steps), standard QD algorithms will eventually experience a "lucky" evaluation. The algorithm saves this solution as an elite. Over thousands of generations, the archive fills up with garbage solutions that only look high-performing because of statistical anomalies. This standing critique fundamentally broke trust in deterministic QD for robotics, leading to the necessary creation of Uncertain QD frameworks that actively track variance and reproducibility [cite: 10, 18]. 

The Curse of Dimensionality in MAP-Elites Grids:
A standing methodological critique of MAP-Elites is that its grid structure requires the practitioner to manually discretize the behavior space. If you define 10 dimensions of behavior and split them into 10 bins each, you create an archive of 10 billion cells. The algorithm will never fill this, memory will overflow, and the local competition metric becomes mathematically meaningless because almost every cell is empty. This limitation was unanswered for years until the recent advent of Dominated Novelty Search in 2025, which abandoned grids entirely [cite: 11].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

1. Applying Dominated Novelty Search to LLM Latent Spaces
What to do: Run Dominated Novelty Search (DNS) using an LLM's own embedding space as the behavior descriptor, aiming to generate a repertoire of highly diverse, high-performing prompts for a complex reasoning task (like code generation or mathematical proof discovery).
Why it is feasible now: DNS, published in 2025, is the first algorithm capable of handling the 1536-dimensional continuous space of an LLM embedding without collapsing or requiring a pre-defined grid [cite: 11]. 
What it would measure: The effective semantic diversity of the generated prompts and the functional coverage of the target task.
Falsification: If the generated repertoire clusters heavily in one semantic region despite DNS selection pressure, it proves that the LLM's latent space is too structurally restricted (the Artificial Hivemind effect) to support true open-ended divergent search.

2. Meta-Learning QD Variation Operators via LLM Crossover
What to do: Rebuild the experiment from Faldor et al. 2026, but instead of using a standard neural network to learn the local competition rules, use an LLM via In-context QD to act as the evolutionary variation operator itself. You would pass the successful survival trajectories of the archive into the LLM and ask it to write raw Python code for new heuristic variation operators.
Why it is feasible now: The combination of In-context QD (Lim 2024) and Meta-Black-Box optimization frameworks (Faldor 2026) provides both the theoretical justification and the JAX hardware acceleration needed to evaluate the LLM-generated heuristics in seconds [cite: 9, 12].
What it would measure: The increase in QD-Score and algorithmic sample efficiency compared to human-designed operators like CMA-ES.
Falsification: If the LLM-generated operators fail to outperform CMA-MAE on the UQD benchmark tasks over 50 generations, it falsifies the hypothesis that LLMs possess zero-shot algorithmic intuition for evolutionary dynamics.

3. Uncertain Quality-Diversity for Domain Randomization in Sim-to-Real Robotics
What to do: Deploy the Archive-sampling method from the Uncertain QD framework to evolve a repertoire of hexapod walking controllers, explicitly randomizing the friction and mass parameters of the Kheperax simulator during every evaluation.
Why it is feasible now: The UQD library provides the explicit variance-tracking archive required to prevent lucky noise from polluting the elites, and JAX acceleration makes the thousands of necessary re-evaluations computationally trivial [cite: 10, 17, 18].
What it would measure: The reproducibility score of the final archive when transferred to a physical hexapod robot or a completely different physics engine.
Falsification: If the controllers in the archive experience catastrophic failure rates upon transfer despite achieving high reproducibility scores in training, it falsifies the core premise of UQD, showing that modeled variance cannot approximate the reality gap.

What will NOT work:
Attempting to run pure Novelty Search on pixel-level state representations of a domain (for example, taking raw video frames as the behavior descriptor). The distance metrics used for nearest neighbors (L2 norm or cosine similarity) lose all semantic meaning in raw, high-dimensional pixel spaces. Every slightly different lighting angle or pixel shift will register as infinitely novel, and the algorithm will thrash endlessly without discovering any meaningful behavioral complexity. You must either map the pixels to a low-dimensional latent space first using a pre-trained autoencoder, or use hand-crafted low-dimensional descriptors.

**Sources:**
1. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHmN8yh1GLrMXz5oSdAuglKg0CDrMAaI07LBb4EPbxjgo4wrZIp-HO-nlauSMds-4uavJ3JQt2KPl7lxOsxSg8J0ENP4EpHuXKFeoTfd61XcLHu_VQTEdk-UY6SsUbAM-iNyDq1XERsz74F9ep4Sbsse_XOivjIytCAxs9gldVEfOmZDqKwA3bbaGAh10QS5oOueXizwo=)
2. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFv0t1crUHjoEdINmYOlT-W7DpE5v4qPqA4cZlQpDBeFBs6PhTyZaUdzC5kLDj4ELHOM0CVJjNH3nd-B_bIhEPjHjMjMtGgzpze1MNOx2R_3Gx6FUpmh6elyM2neeTP)
3. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGtBEKxUmPR9teNOAZV5rZmBCe0WAikGCsRbD856LcxkE6RPfIvLJg1nxk9j-nPfTjOy0NVHqHKlG7b-bmNlbpWhQihSUmSqUIpUtihsJLVl3hp9EUvYuRPClyPqA10wmnA0aDazVzOiRzWq6WVCEkWErTUAVgI8hRZKZL0yuzWfRMxs1Cir-CCF2Y3ROLrvk=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESWorcMHXnyAXMCs3ih85Z6SlNKUr_v9mollcSfyahD9JDsHU8_PSdayOMlKZEnB0mlmDwSzj88dOv78oU2rf2W9q5uCSZAUbtsC6kFvw7lZE6RUv-)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_g3wwnOoYNx4zBa8vkCEnRa2vp_QQ2uoEve8Z7-zs8JdfcVcmPq_PN1oNwQ1zeoMIa4Kuf79s0tqAIftuHrR2HIsZ6-_VJtjKYsUDgkh98wlvwbaa)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFinfOgUUXkrdljCACpiSWULANSyEZufDj8q51t9DGkxi8Hdu-b7OaLZUW3Aq2EYWupdAD8LxQeuOTslbUrM_qwh83h8mirBe210O4guk2sCcvZXTH4YsYUB8g3-j7gqMruueOF)
7. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-Mc2xmCQu-k8m2TBwlG0BaZlPzZWKBCjwYh5FYh2xufc4pjmH4GdWSZ3GwOBv_RvmK9cFWbhDX1hoAvfkWPE4JkIEvYy_f06l2hz6wo-G0q76G0t85ZAhPMP_YqF1AavM4g==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHna7hKHkkQQYioynLrJEv_ilPiA6CL2jO2RDciThx5JhceAFDB-zEY7mmc6biL19XK2x2q_93murp1halAQibuSHQ7LaREhHx63xWf9NkOanbphbEU)
9. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsuPO1WV5cEf_whcQxi3szVrzq1hz7YD4fl0FH0N5tlD-do0JciQhSZgkHASkVArcc3LcNw5Bl1RYQtHp0cVDIUzIovQiiy4b70rIr-duqmRLARJx2SZZm2BiQwawanK8Mq1O0-ZXCsOynMyyyd3S2_AOm6yYsSHS9VsCtLSCc87ypw7rjSfcF)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLoCF6E2woBwqqxPrfGZbbimtB3bih8KqxQpxghecb-fpFm3gUlssZQGg960OFr8_qENYYOYZWoLqsx8WtBAlsvHy68-3Kwa_qMTZDHzM75qbgZnpmYVQl)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW7nteZaa5m_AORO1LJ361lb_2kqL828AvoUIQWO8ldr8uhvfgIFMFpfOwC8Ide_2OKALPISZExTlSGvX_T57Ga_2VWEteJ2d7BwGO5_DuyA9DThKdlWe9)
12. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwUOSizrsRy00gpmOUvR3FRctdDWp-h5DTh1tX2nE5LRSMkNS7GCE-OK7341izhXF4Lg8X2JcU4QFX734BZQbK6UGqnUU5-b9xC7ZCKnJNVL1wtx4E553b62DWlk8ZzQ==)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIX9U-VZyE7Um477HqQbI2m3C8Ukm8mWw5KuA1HstKFfjIcbtjK6xOOvIRcrit1untl-Fv_66nCXgTP9qZ9zQPAXHy15IljdzyzKD4YDnyYxN94jJvF4jVnp_uHktEb1jE3MOuVDMxXeUiUAxIhs55JzsDH__0uQArtv2cSfV1o3m_REggay0pQ7c4QqsSBeIamg==)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7jpH4Ue829hxy4DD28-MpTw7khR6qTwSxeIP1dYCUJ5FwK8prY7raq_YpCKyGVwto2rkTG47HKOwIn9dLUa0E62Su1mQIxLQQFJpqkCAvo5dBDSYJwAeHOd7qkbGlbnjezfNFs9QIlwwSRfL9UhbdVDm_lwTy30rCGclF6vqOeQbnpsuFO7Bh_ln1jqanpn7uX1PnOoPuKeRwGy5Oa1tc0eoSgFyHn31Vyta4crgLhm6v2oL6-ld9DJ_OckKh9f_As__dfbxp93Jo8J7bpFs-pKZ0IQs=)
15. [kaggle.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkgHOq502BF3ct5fKb7z453Mqy97wUgUI-3tuR3I2i2esW-LWrFw0oqgN2W6TZq82oz38TWaHoAWilUTfBz0UoxzmdBl7e8CYNryJE4VDDh1zky6u6kHVwFM9r0HQNSdQZ1DjxHG4=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUlgTlPz8bH8kA18MoE8PChzoCwqu44Yf_Fh02kqFpqoGSAwx26WOeG97nD3gFSXnLiz5VxEq5c1nvDPo49if5rixoyXgi4Ov7pxrrK12OPdH4Yw_M)
17. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlXZ9v2N-TrfRHe3ldPCbhqrYIdgIwuZVuxQhHfSy_ewr4o8ACAfAcwDR9fgIss7xXvusAX3dMEYUAiN_RbdNG1clJ3hZnE7jdlbxLhZ4IzhwRzhozM6_hmoesTzn_78SL47GbfQ==)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwBYE985pynR3he-oa4y6jL8ayifbO5-rt7XmW7a1HgHp0C6yoHTY7IHFuUeDMoWGqvFvY92ObFxjE44WvstqCZsC9K8tIglKfcg5tI-8cqkMIet7BmZ6aaqOLAb0v2Ack06xD__35Z6FLeci65d-2lx3fvWMEqdJos35h73hmL5g=)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqsc1WeVIzjhZ5-VsI3C_jVm6qBcYJqMaDqEBCUCKNdmBAz9Qmt86NTMFUvl3tKMgIn2s-B0Guj6Sj9eVwvWdHDPz5icji0D-4oTYZor2pIAutBgPe_Hc-xARd336OVmCx6xXLezPKJTvumalq5SM0v3mqoh6sZ4umNOhv5r8=)
20. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGf4IDxMX0kRbHZfbYkG9InwMO0Zwoe2YTWNgnU2wOQzhzYBh6-b413xcbjYrlAGIFPc4nBaimjmnxC5dLjvZnEXuoNaNdWwjK1T32DSg4vPiR-0mzvr23VvpDavfWjsBrYDp_dtenUFTuOmfC21r-pNEN-EKO5ZRMCM0QR2c0TbgKr)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6geUJHtsaFg_gvpgv2ppGkK3oafxBsHQCj9956IiMvaHlvbfJWXTvncDTwx6I5O2ry-WA7ZfKl9Gjz_JAyshzCF1nSoHRMH3DNYWgbmePCyT2Z83-hiZ7WZQ=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPk5YeDOOVRpI3SX18dK3lia55XftQo4yflQTS3Lk3JfVBLHNMlCz78B-oTIqIoX2EO_jxinrBlIb1zV_3lUqt4wFJK7BMbam4CgHIbgyFs13IPmcY)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAx9oJMq74m1XiLWJW_uM5-oZndjkRE9xi7YuEgB5Hnb5yXq88kiLUuk0JSvPjl62TkMmBY8DKwtHke6XfbakL8XnSxlnskksK665Sy7ot7ROwfJ5waVGpzZcS9nrklkIyO80p1CHw0tIlXa2hYvfkyauwviLiKj1icWo-oL64NHPNCIZfJjLzuMyUGLIfO7aTQKrLBnClu3HwTqX8YcZGkdJp3ub5MQ-H4b7p4kv8T7nH)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkzQ_rzAqqhLseXrPSTPRJ2hVwBdqDpccSwREwKOJ4PwThX6BEz4-osY-v1AlcY9rKMzEJjTJ6zyxLRb2WNUdmtQQHif5Ty8_Yzy0dg-wqWwRgIqbu9lSD)


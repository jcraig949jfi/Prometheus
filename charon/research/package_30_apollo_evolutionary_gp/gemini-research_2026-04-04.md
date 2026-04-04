# Deep Research Brief: Evolutionary Search over Reasoning Primitive DAGs

**Key Findings**
*   **LLM-Guided Evolution:** Research suggests that integrating Large Language Models (LLMs) into genetic programming (GP) can dramatically improve search spaces by replacing blind variation with semantically informed mutations. However, maintaining high-quality populations requires rigorous sandboxing and validation to counteract LLM hallucinations. 
*   **Many-Objective Optimization Scaling:** The evidence leans strongly toward the conclusion that traditional Pareto-dominance mechanisms, such as those used in NSGA-II, suffer severe performance degradation when scaled to 4 or more objectives. Adapting the system to reference-point methods (e.g., NSGA-III) or decomposition-based methods (e.g., MOEA/D) is highly recommended for optimizing 6 objectives simultaneously.
*   **Bloat and Parsimony:** While lexicographic parsimony pressure is a common bloat control mechanism, studies indicate it can be destructive during evolutionary plateaus by prematurely penalizing neutral but structurally necessary mutations. Alternative methods like double tournament selection may offer a more balanced approach.
*   **Search Space Illumination:** Quality-Diversity algorithms, particularly MAP-Elites, have proven highly effective in program synthesis for preventing premature convergence. Combining novelty search with lexicase selection appears to mitigate the risk of novelty search saturating in unconstrained programmatic spaces.

**Overview of the Apollo Architecture**
The Apollo system aims to discover novel routing strategies by searching over directed acyclic graphs (DAGs) consisting of fixed reasoning primitives (e.g., `solve_sat`, `bayesian_update`). The search space spans discrete structural topologies (which primitives to use and how to wire them), executable Python code (the router logic), and continuous parameter tuning (weights, thresholds). The evaluation of these routing strategies is strictly many-objective, utilizing six distinct Pareto objectives: accuracy margin, calibration, ablation delta, generalization, novelty, and parsimony. To traverse this highly complex search space, Apollo utilizes an LLM-assisted mutation strategy powered by a local Qwen 7B model. This report provides an exhaustive literature review of adjacent methodologies, implementation libraries, speedup techniques, and known failure modes to guide the architectural refinement of the Apollo system.

---

## 1. LLM-Guided Genetic Programming (2022-2026)

The integration of Large Language Models into evolutionary computation has birthed a new paradigm often referred to as Evolution through Large Models (ELM) or LLM-Driven Genetic Search [cite: 1, 2]. By replacing or augmenting traditional, syntax-blind mutation and crossover operators with LLM-driven generation, these systems leverage the pre-trained semantic understanding of models to propose intelligent variations. 

### Key Papers
*   **EvoPrompting: Language Models for Code-Level Neural Architecture Search** (Chen et al., 2023, NeurIPS): This foundational paper demonstrates that while LLMs struggle with direct zero-shot program synthesis for complex architectures, coupling them with an evolutionary loop (soft prompt-tuning and adaptive mutation) consistently discovers high-performing, novel architectures. The system was validated on the MNIST-1D and CLRS Algorithmic Reasoning Benchmarks [cite: 3, 4].
*   **Mathematical Discoveries from Program Search with Large Language Models (FunSearch)** (Romera-Paredes et al., 2023, Nature / DeepMind): This breakthrough paper utilizes an LLM (PaLM 2) strictly as a mutation crossover subroutine inside an island-model genetic algorithm. FunSearch evolves Python "priority" functions for mathematical combinatorial optimization, successfully finding novel solutions to the cap set problem by combining an automated evaluator to filter LLM hallucinations with a database of top-performing seed programs [cite: 5, 6].
*   **Guided Evolution: The Automation of Models Advancing Models** (Morris et al., 2024): This framework uses LLMs to directly modify code via an "Evolution of Thought" technique. The LLM reflects on the outcomes of previous mutations, creating a self-sustaining feedback loop that modulates temperature and adapts prompts to maintain genetic diversity while driving intelligent crossovers [cite: 7, 8].
*   **LLM-Guided Genetic Improvement: Envisioning Semantic Aware Automated Software Evolution** (Even-Mendoza et al., 2025): Proposes the use of lightweight machine learning classifiers to approximate and filter LLM-generated patch edits (e.g., identifying semantic nature like "added exception handling") prior to expensive fitness evaluation, significantly speeding up the LLM-guided GP search process [cite: 9].

### Handling LLM Unreliability and Validation
A core challenge of using LLMs as genetic operators is their propensity to generate syntactically invalid or semantically broken code, often termed "hallucinations" in this context [cite: 9, 10]. 
1.  **Strict Evaluator Filtering:** FunSearch addresses this by pairing the LLM explicitly with a high-speed, automated evaluator. The LLM is isolated from the main program context and only prompted to rewrite a specific subroutine; any failure in the evaluator results in immediate discarding of the generated program without polluting the evolutionary database [cite: 5, 10].
2.  **Evolution of Thought (EoT):** Systems like Guided Evolution feed the compilation errors and fitness regressions back into the LLM prompt, asking the model to reflect on why the previous mutation failed and generate a corrected version [cite: 7].
3.  **Fast Approximation Filters:** To prevent wasting compute on evaluating NoOp edits (edits that do not change behavior) or obvious failures, deploying a lightweight classifier (like a fast decision tree or k-NN) to pre-screen the LLM's structural edit can prune the search space efficiently [cite: 9]. 

### LLM Size and the "Quality Cliff"
While flagship systems like FunSearch utilize massive models (e.g., PaLM 2) to achieve mathematical breakthroughs [cite: 6, 10], recent literature indicates that smaller models (in the 7B parameter regime, such as Qwen 7B) can be sufficient if appropriately scaffolded [cite: 11, 12]. The 7B class is generally capable of localized code rewriting and structural mutation (e.g., DAG rewiring) provided that the prompt provides few-shot examples of successful mutations. However, a known quality cliff exists when smaller models are tasked with global reasoning over the entire program architecture simultaneously. To maximize a 7B model's efficacy:
*   Use it strictly as a localized mutation operator (e.g., "rewrite this specific routing function" or "suggest a new edge between Node A and Node B").
*   Implement syntax checking (via Python's `ast.parse()`) and immediate fallback to traditional AST-level perturbations if the LLM output fails validation, guaranteeing a baseline mutation rate even when the LLM degrades [cite: 12].

### Practical Recommendations for Apollo
*   **Subroutine Isolation:** Do not prompt the Qwen 7B model with the entire Apollo codebase. Feed it only the 3-7 node DAG representation and the specific Python "router" code it needs to mutate, similar to FunSearch's methodology [cite: 5, 13].
*   **Ensemble Prompting:** Utilize an ensemble of prompts with varying temperatures. Guided Evolution varies temperature between 0.05 and 0.4 to balance minor syntactic tweaks with larger structural leaps [cite: 7].
*   **AST Fallback Mechanism:** Because a 7B model will occasionally generate invalid Python logic, maintain a robust deterministic fallback loop that performs basic parameter perturbation (e.g., shifting thresholds or weights) if the LLM fails after a specified number of retries [cite: 12].

### Known Pitfalls to Avoid
*   **Unconstrained Prompts:** Giving the LLM too much freedom often leads to programs that violate the fixed reasoning primitive constraint. 
*   **Feedback Loops of Bad Code:** If broken or low-performing programs are accidentally admitted into the elite pool, the LLM will use them as few-shot examples for the next generation, leading to rapid population degradation [cite: 6, 14].

### Open Questions
*   How can an LLM implicitly balance the trade-off between multiple Pareto objectives when generating a mutation, without relying solely on the downstream NSGA-II sorting algorithm?
*   What is the optimal ratio of LLM-generated mutations versus deterministic AST mutations across different stages of evolutionary convergence?

---

## 2. Quality-Diversity Algorithms for Program Spaces

Quality-Diversity (QD) algorithms focus on illuminating the search space by discovering a diverse set of high-performing solutions rather than a single global optimum. This is highly relevant for Apollo, which requires diverse routing strategies for different reasoning tasks.

### Key Papers
*   **Exploring Genetic Programming Systems with MAP-Elites** (Dolson et al., 2018): This paper adapts the Multi-dimensional Archive of Phenotypic Elites (MAP-Elites) algorithm explicitly for GP representations. It demonstrates that mapping programs across phenotypic traits (like program architecture and instruction composition) generates a vastly wider range of architectures than standard evolutionary algorithms [cite: 15, 16].
*   **MAP-Elites for Genetic Programming-Based Ensemble Learning: An Interactive Approach** (Banzhaf et al., 2023): Proposes the use of cosine similarity-based dimensionality reduction (like Kernel PCA) to automatically induce a behavior space from the semantics of GP programs, allowing MAP-Elites to handle highly complex, high-dimensional program behaviors [cite: 17].
*   **Comparing and Combining Lexicase Selection and Novelty Search** (Jundt & Helmuth, 2019, GECCO): Introduces Novelty-Lexicase selection. It demonstrates that standard novelty search fails in unconstrained program synthesis spaces due to lack of direction. By calculating a novelty score for each test case and blending it with lexicase selection, the algorithm achieves superior performance and resists local optima [cite: 18, 19].
*   **Progressive Minimal Criteria Novelty Search (PMCNS)** (Gomes et al., 2015): Addresses the saturation of novelty search by imposing a dynamically adjusting minimal fitness criterion. Solutions must surpass a performance threshold (e.g., 50th percentile) to be considered for their novelty, restricting the search to the "feasible" behavioral space [cite: 20].

### Behavioral Characterization for Programs
In traditional robotics, MAP-Elites uses distinct physical traits (e.g., leg length, weight). For programs like Apollo's routing DAGs, computing meaningful behavioral signatures is non-trivial. The literature suggests:
1.  **Execution Trace / Semantic Signatures:** Running the program on a set of standardized inputs and capturing the output vector (or intermediate node states) to form a semantic vector. Distance between programs is then calculated via cosine similarity or Euclidean distance [cite: 17, 21].
2.  **Architectural Traits:** Using static analysis to define traits such as the number of nodes (3 to 7), depth of the DAG, instruction entropy, or specific primitive inclusion [cite: 15, 22]. 

### Saturation of Novelty Search and Mitigations
Novelty Search often fails in general program synthesis because the space of "novel but useless" programs is infinitely larger than the space of useful programs [cite: 18, 23]. This saturation causes the algorithm to waste evaluations on degenerate DAG topologies. 
*   **Mitigation 1 - Novelty-Lexicase Selection:** Instead of tracking global novelty, assess novelty on a per-test-case basis. If a program solves a specific reasoning task that few other programs in the population solve, it receives a high novelty score for that specific case. This provides a strong gradient toward the objective while maintaining behavioral diversity [cite: 18].
*   **Mitigation 2 - Novelty Search Local Competition (NSLC):** Maintain two populations (feasible and infeasible) or evaluate a program's novelty only against its nearest neighbors in fitness space, ensuring that the algorithm searches for novel ways to *succeed* rather than novel ways to *fail* [cite: 24, 25].

### Practical Recommendations for Apollo
*   **Per-Task Novelty:** Since Apollo evaluates on diverse reasoning tasks, implement behavioral characterization by tracking which primitives activate for which tasks. Compute a k-NN behavioral distance based on these activation vectors.
*   **Progressive Minimal Criteria:** Before calculating the novelty objective for NSGA-II, zero out the novelty score of any program that falls below a baseline accuracy margin, preventing the LLM from exploring "junk" code topologies [cite: 20].

### Known Pitfalls to Avoid
*   **Curse of Dimensionality in Behavior Space:** Defining too many behavioral axes in MAP-Elites dilutes the elite archive, turning it into a random search. Keep phenotypic traits to 2-4 dimensions or use dimensionality reduction [cite: 17, 20].

### Open Questions
*   Can the internal latent representations of the Qwen 7B model be extracted and used as a direct embedding for the behavioral characterization of the generated routing logic?

---

## 3. Multi-Objective Evolutionary Optimization — Scaling and Speedups

Apollo utilizes 6 Pareto objectives (accuracy margin, calibration, ablation delta, generalization, novelty, parsimony). A critical issue is that standard Pareto-based sorting breaks down at this dimensionality.

### The Breakdown of Pareto Dominance
The literature on **Many-Objective Optimization (MaOP)** clearly establishes that Pareto dominance relations lose their selection pressure when the number of objectives exceeds 3 or 4 [cite: 26, 27]. In a 6-objective space, almost every generated solution becomes "non-dominated" (i.e., Pareto-optimal relative to the population), meaning the algorithm can no longer distinguish between mediocre and excellent solutions. The crowding distance operator used in NSGA-II to maintain diversity inadvertently favors poorly converged solutions lying on the extreme boundaries of the high-dimensional space [cite: 27, 28].

### Key Papers and Alternatives to NSGA-II
*   **An Evolutionary Many-Objective Optimization Algorithm Using Reference-Point-Based Nondominated Sorting Approach (NSGA-III)** (Deb & Jain, 2014): Explicitly designed to replace NSGA-II for 4-15 objectives. NSGA-III abandons crowding distance in favor of a set of uniformly distributed reference points in the objective space. Solutions are associated with the closest reference line, ensuring a well-distributed and converged Pareto front [cite: 26, 27].
*   **MOEA/D (Multi-Objective Evolutionary Algorithm based on Decomposition):** Transforms the many-objective problem into a set of single-objective scalar optimization subproblems optimized simultaneously. It performs exceptionally well when combined with local search methodologies [cite: 26, 29].
*   **A Meta-Objective Approach for Many-Objective Evolutionary Optimization** (Wang et al., 2020): Proposes evaluating the convergence and diversity components separately in a "meta-objective" space to rescue the efficacy of standard Pareto dominance, proving effective as a drop-in replacement for NSGA-II scaling [cite: 28].

### Speedups: Surrogate Models and Racing Algorithms
Evaluating programs (especially neural-guided or LLM-guided code) across multiple reasoning tasks is computationally prohibitive.
1.  **Surrogate-Assisted Evaluation:** Surrogate models predict the fitness of a program without fully evaluating it. For genetic programming, where representations are discrete trees/DAGs, traditional neural networks struggle. The literature recommends using **Gaussian Process Regression (Kriging)** or **Radial Basis Function Networks (GP-RBFN)** combined with phenotypic distance metrics (e.g., distance between DAG graph edit distances) to approximate fitness [cite: 21, 30]. Furthermore, KNN algorithms have proven successful as fast surrogate models for GP [cite: 31].
2.  **Racing Algorithms:** Algorithms like **PolarBear** (Pareto-optimal anytime algorithms via Bayesian racing) evaluate candidates iteratively across time or sub-tasks. If statistical bounds show a candidate program is probabilistically dominated by others early in the evaluation battery, the evaluation is aborted [cite: 32, 33]. This is highly applicable to Apollo's task curriculum.
3.  **Adaptive Operator Selection (AOS):** Instead of fixed mutation rates, AOS dynamically chooses which mutation operator to apply based on recent success rates. The **Adaptive Pursuit** algorithm coupled with a multi-armed bandit reward policy outperforms standard probability matching in GP, allowing the system to autonomously decide whether to use an LLM rewrite, a DAG edge mutation, or a parameter tweak [cite: 34, 35].

### Practical Recommendations for Apollo
*   **Upgrade to NSGA-III or MOEA/D:** It is imperative to migrate Apollo's selection algorithm from NSGA-II to NSGA-III or a reference-point method to handle the 6 objectives effectively [cite: 27, 36].
*   **Implement F-Race or Bayesian Racing:** When evaluating a new router program against diverse reasoning tasks, evaluate on a small batch of tasks first. If the accuracy margin is significantly worse than the baseline, terminate the evaluation early to save compute [cite: 33, 37].
*   **Use AOS for Mutation Selection:** Track the success rate of the Qwen 7B's router rewrites versus primitive swaps. Use an Adaptive Pursuit mechanism to heavily weight the LLM operator only when it is actively generating Pareto-improving offspring [cite: 34, 38].

### Known Pitfalls to Avoid
*   **Reference Point Misspecification:** In NSGA-III, if the Pareto front is highly irregular or degenerate, predefined uniform reference points may guide the search into empty regions [cite: 36, 39]. Use adaptive reference point updates (e.g., $\theta$-NSGA-III or A-NSGA-III).

### Open Questions
*   How can surrogate models accurately map the latent embeddings of the LLM-generated code into fitness predictions for the 6 independent objectives simultaneously?

---

## 4. Bloat Control and Convergence in Variable-Length GP

In evolutionary systems with variable-length representations (like Apollo's DAGs and executable Python router strings), programs naturally suffer from **bloat**—the uncontrolled growth of redundant or "intron" code that does not improve fitness but consumes execution time and memory [cite: 40, 41, 42].

### Key Papers
*   **A Comparison of Bloat Control Methods for Genetic Programming** (Luke & Panait, 2006): A seminal analysis comparing depth-limiting, lexicographic parsimony pressure, and double tournament selection [cite: 40, 43].
*   **Destructiveness of Lexicographic Parsimony Pressure and Alleviation by a Concatenation Crossover in Genetic Programming** (Kötzing et al., 2018): Provides theoretical proof that strict lexicographic parsimony pressure actively harms the search process by trapping populations on fitness plateaus [cite: 42, 44].
*   **Influence of Bloat Control on Relocation Rules Automatically Designed via Genetic Programming** (Škalec & Đurasević, 2026): Recent analysis confirming that combining online parsimony pressure with offline pruning achieves massive solution size reductions with minimal performance degradation [cite: 41, 45].

### Lexicographic Parsimony vs. Double Tournament
1.  **Lexicographic Parsimony Pressure:** This method treats size as a tie-breaker. If two programs have identical fitness, the smaller program is selected. **Warning:** Theory shows this is highly destructive during fitness plateaus [cite: 44, 46]. When a population is stuck, it relies on neutral structural mutations (which temporarily increase size without altering fitness) to build the scaffolding needed for the next evolutionary leap. Lexicographic parsimony culls these vital stepping-stones [cite: 42, 47].
2.  **Double Tournament Selection:** A more robust alternative. It runs a tournament based on size, then takes the winners and runs a second tournament based on fitness (or vice versa). This probabilistically favors smaller programs without strictly killing off neutral structural growth [cite: 43, 46].

### Diversity Maintenance: Islands and Speciation
As programs converge toward a local optimum, the population loses diversity.
*   **Island Models:** DeepMind's FunSearch utilizes an Island Model, dividing the population into separate clusters (islands) that evolve independently and occasionally exchange migrants. This prevents a single dominant sub-optimal program from taking over the entire population [cite: 13, 48].
*   **Speciation / Niching:** The Speciating Island Model (SIM) isolates "outlier" programs into their own sub-populations [cite: 49]. If Apollo generates a highly novel DAG wiring that initially performs poorly (a new species), speciation protects it from being immediately culled by highly tuned but stagnant baseline programs [cite: 48, 50].

### Early Warning Signals for Stagnation
*   **Plateau Identification:** Track the ratio of neutral mutations (mutations that change the code but not the fitness). A sudden spike in neutral mutations coupled with a rapid increase in average DAG size indicates the population has hit a plateau and is drifting aimlessly [cite: 12, 47].
*   **Adaptive LLM Intervention:** Use systems like ALEGP (Adaptive LLM-based Evolutionary GP) which monitor for stagnation. If the fitness variance of the population drops below a threshold, dynamically increase the probability of invoking the Qwen 7B model for a drastic structural rewrite rather than relying on AST tuning [cite: 12, 51].

### Practical Recommendations for Apollo
*   **Implement Double Tournament Bloat Control:** Since parsimony is one of your 6 objectives, do not use it as a strict tie-breaker. Treat it as a soft objective or use Double Tournament selection to allow temporary DAG expansion [cite: 43, 46].
*   **Use an Island Model:** Partition Apollo's population into 4-8 islands. Allow the Qwen LLM to sample parents exclusively from within an island, occasionally migrating the best routers between islands to preserve topological diversity [cite: 11, 13].

### Known Pitfalls to Avoid
*   **Over-Pruning:** Forcing the LLM to write maximally concise code too early in the run removes the redundant code blocks that often serve as raw material for future beneficial mutations [cite: 41, 47].

---

## 5. Practical Libraries and Implementations

Choosing the right underlying infrastructure is vital for balancing evolutionary loop speed, multi-objective sorting accuracy, and safe execution of LLM-generated code.

### Framework Comparisons
1.  **Pymoo:** The modern standard for Multi-Objective Optimization in Python. It has a clean API, excellent visualization tools, and native implementations of NSGA-II, NSGA-III, and MOEA/D [cite: 52, 53]. **Verdict:** Highly recommended for Apollo's 6-objective sorting mechanism.
2.  **DEAP:** A highly flexible, general-purpose evolutionary framework. While slightly verbose and lacking the modern MOO defaults of pymoo, it is uniquely suited for building custom Tree-based/DAG-based representations [cite: 27, 52].
3.  **EvoTorch:** Built by NNAISENSE on top of PyTorch, it specializes in massive GPU scaling and vectorization [cite: 54, 55]. It supports genetic programming via stack-based interpreters [cite: 56]. **Verdict:** Excellent if Apollo's primitive evaluation can be fully tensorized; otherwise, the CPU-to-GPU memory transfer overhead may negate its benefits.
4.  **Nevergrad:** Developed by Meta (Facebook), focusing on gradient-free optimization (CMA-ES, Bayesian optimization) and hyperparameter tuning rather than program synthesis. Includes an excellent algorithm selector (NGOpt) [cite: 57, 58].
5.  **OpenELM (CarperAI):** Specifically designed to link LLMs with evolutionary algorithms (MAP-Elites). OpenELM treats the LLM as an intelligent mutation operator to evolve code representations [cite: 59, 60]. **Verdict:** A strong architectural reference for integrating the Qwen 7B model.
6.  **PushGP:** Uses the stack-based "Push" language for autoconstructive evolution. Every variable type has its own execution stack, allowing highly safe and robust code generation without syntax errors [cite: 61, 62]. While powerful, its esoteric syntax makes it less suitable for Apollo, which relies on standard Python primitives [cite: 63].

### Sandboxing Evolved Code
Running LLM-generated Python code safely and concurrently is a major security and stability risk.
*   **Subprocesses with OS-level Isolation (Magpie approach):** Run each candidate in a separate subprocess with a strict timeout (e.g., 1 second). Use Linux `perf` to capture highly accurate instruction counts for the parsimony objective [cite: 64].
*   **Docker / Containerization:** The standard for most modern systems (e.g., Unvibe) where the LLM can generate arbitrary code [cite: 11]. However, the overhead of spinning up containers is often too high for evolutionary loops requiring millions of evaluations.
*   **KeyVM / Recursive Sandboxing:** A lightweight virtual machine architecture that limits execution to specific byte allocations and VM steps [cite: 65].
*   **Apollo Recommendation:** Use Python's `ast.parse` to strip out malicious imports, combined with `multiprocessing` and OS-level `setrlimit` to bound CPU time and memory. This is generally faster than Docker while being significantly more secure than `RestrictedPython` [cite: 12, 66].

### Surrogate Models for Fitness Prediction
To bypass expensive evaluation of the DAG against all reasoning tasks:
*   **PGU-SGP (Pheno-Geno Unified Surrogate GP):** Combines both the structural layout of the DAG (genotype) and the output vectors on a subset of data (phenotype) into a unified feature representation [cite: 67].
*   **KNN / Kriging:** Use the extracted feature representation to query a K-Nearest Neighbors model built from the evaluated archive. If the predicted fitness is vastly inferior to the current Pareto front, skip the actual evaluation [cite: 31, 68].

### Open Questions
*   How seamlessly can `pymoo` be integrated with custom asynchronous evaluation pipelines, given that LLM inference (mutation) and DAG evaluation take vastly different amounts of time?

---

## 6. Failure Case Studies

Analyzing negative results in genetic programming provides critical guardrails for Apollo's system design.

### Known Plateaus and Representation Traps
*   **Deceptive Fitness Landscapes / Sub-problem Mapping:** A major documented failure mode in GP occurs when the fitness function evaluates only the final output of a complex program, failing to reward the solving of necessary sub-problems [cite: 69]. If Apollo's router function requires two distinct logical steps to succeed, but only receives fitness for the final boolean success, the search will plateau. **Mitigation:** Ensure the evaluation metrics provide partial credit or trace-level rewards for correct primitive usage [cite: 70, 71].
*   **Formal Specification Scaling (CDGP):** Counterexample-Driven GP (CDGP) uses SMT solvers to verify programs. However, research shows that as program length grows, the search space grows exponentially, causing exact verification methods to stall completely [cite: 70, 72]. **Lesson for Apollo:** Do not attempt to formally verify the semantic correctness of the 7B's router code; rely purely on empirical test-case evaluation [cite: 73].

### Population Size Dynamics
*   **Increasing Population Size:** In GP, increasing population size theoretically improves diversity. However, experimental data shows a point of diminishing returns where a massive population drastically slows down generation turnover, preventing the algorithm from exploiting good lineages [cite: 14, 29].
*   **The Sweet Spot:** Systems like FunSearch handle this by maintaining a massive passive database (archive) but utilizing a small, highly active sampled population for the immediate evolutionary loop [cite: 6, 13]. Apollo should maintain a small active population (e.g., 50-100 DAGs) managed by an island model to ensure fast iteration, while archiving all evaluated programs in a MAP-Elites grid for future LLM context retrieval.

### Task Curriculum Design
*   **Static vs. Dynamic Task Batteries:** Evaluating every program on a static battery of complex reasoning tasks leads to overfitting and massive computational overhead. 
*   **Dynamic / Co-evolutionary Curriculum:** OpenELM and other recent platforms support the co-evolution of tasks alongside solutions [cite: 59]. Alternatively, implement a curriculum that starts with simple reasoning tasks and progressively introduces harder held-out tasks as the population's accuracy margin improves.

### Practical Recommendations for Apollo
*   **Sub-problem Credit:** Break down the `accuracy margin` objective to evaluate not just the final output score, but whether the router function appropriately routed intermediate data. 
*   **Database vs. Population:** Separate the concept of the evolutionary "population" from the "database of known programs." Use a small population for the NSGA-III sort, but draw few-shot examples for the Qwen 7B prompt from the wider historical database of elites [cite: 6, 74].

### Open Questions
*   How can the system autonomously identify whether stagnation is caused by a limitation in the available fixed primitives, a limitation in the Qwen 7B's coding ability, or a flaw in the multi-objective fitness landscape?

**Sources:**
1. [marktechpost.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxoQRxYGW6iPwjenJ1l7YZ3SLoPeKaACvQD5zFxnXg7nydzjqqveFXC4MXqtdH-YOpdYrIXSyuvBwfTYz0Hv9ttDvZIozgzUlqwYebNbT2Cyc7d-40ykii7SO16f1ZJd_G0NHALWd-hyGJU1BWNRXQeti-8Tklo8i7Dz9uCv5Gf6XI9Eeeo9RkytaCWeJ1F9FtWfoBKa6avgkf4om6Ptq5kZRS64f6laxiuS_3M_7pRVoNPpabNCYVgMG2m7-1Y76coCpw6ijdjPH9T9a3mTqyw1bzyK_ndrMg4KJomyltK5j7Ysv0K7wOfysouN9G8zY=)
2. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZ6JNVFBhsWPCaCbLSDaJiYdBPpArkoHU4GRqq4X_iTw6Y3gAMoP5JjQa1v-YgrUZonxsthbuFoiEp37hugTCXoFfGjV3WcmYgJdZUXt1UnaCNlb7-VuAgYWdOCPCifLtCqPbjvCUUzJ1RZW1gEEmviLhi)
3. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvxy5xcE_qHnOC_I9Wc1lVPNi-KP4WaBhTjeSBv4bXb6XI7dH7Ih1clNz2QhfuzN4U7UkoBMqqeWsavHf7STYfVDDiL4U0dZUavj4z--mMLu6ygFOspaW1VZ6gPPAiIrGjLB6aZdGqEjHab0cwjF76qMW1_ZRn0wRK5ZvXspTcj7JH4yaVLIjwT-KWNpBTQ_WJVQ2tLnYPzsQfsfjqOWuVX6_gVdonjeR6Gbda4VxAAjuPY0kBg_tR1JPmjj48AfYVQoOGzo4=)
4. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEt3MeSXLuimpc7eivpRxSYWGZeqpm6FERU934WjYrv3B6jnN3J-YFdsvbcTKPnHuh4SVlFGa71rYapMaQoGwH6qke1WStsJ-NvDbGJGHRR42A0-jkIZzWxNJMudUZyI-5GSWtOqvf4R3fiiUU7y_QUzJE=)
5. [nyu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8me1kIG0C85ozjgkHtKLj6-9OYCzGdsHbnV0CW4u8upaaj_UbELVRh4kT_BExJOSv03Xy9cHgeBWFlscAmCF1jp_7vJIqLdz1FWhTubJo-Op92R6apROZ6TEr3NDQmVashT7fBg==)
6. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNrFvGe0DxZ7IGk_YQegHv2qFbQAqq8fCfts-xrGW_cjZclBTmq9EXa40StcekYbKo7fhbXA6mUNNyB1nF1MhIozOn3WOljISxFZ3au8p5dYH9OFQWVNov05TmDjsMIvBX7F-qJeX5jTozHnUgUxpBsAugmiiATDy11A==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWJUksVeMc6WKI1rH4Mi7tncsrao62czML7wF8FIYhWwireKYvQbL121DZWQNUwsUcEQfgiQORxESM5Y_cyz_-_VC96gVdGExtr2q681xoUHgVtBSBSHlSHw==)
8. [athina.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG79adXLCR_u51ezFxDmU-h7b3AmEPUq5AaadjtqiNL7o_VlUxFqpfgMcCOYd5jcAukq9fPwWTKY3yo_8SuhtX6RF3JFs2NOzYcYeeFlzM0bkrAOpdJuKFtxrtElNVJJX8acdV3yjO8pwuAgUlRq7Z6VgbPRq9uPpl1uPXybhxFvbrrG08SNNI2ybYFDb_C)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwT2O61hbpIA-znk6Cz4UPW5IfJc-rFZokIezoMOVdqvP-HJ9TMzcH8T42hK9_jD-aqs1h0DtKSW9IWOOgXQKFYgdksSFoiR9P-aj5Xv-uAHyAyOIMSsJvWw==)
10. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVtknS7nObY5REdIDu-EZHAJZ8FbCtx-AXYCAAQD7tZLSD8v55PnSOedJGPT8MCEV1PFpTSAB_7oNv0PRwEWACoho2O9QyX6LQ_LJxDOAAliAqFQapSdBnaZ1fSAOhhYI0IP6hjXBC6KhtjkqLDivTy5pN2v5xXQ2Dd5xEmKHO2MrisebWrz5KlBGB9SlJBUeikbfNhSnasRQJJ4gaU25XkeYOlOgku13R)
11. [dev.to](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHm_tCvy-k-DhrpwavP_vYQWMuE-rk8dyENWPgIE9K8QCl1kZZI5SFe9hMP-835TR_7kwFVGEo-c8sqTNpoUtsBDZZ2H1JdZxEXEllls0n8EFC-KD784Iy4TbMDDRi5Imp_-L_BOy7QlxPezWLo9nBqF7KsiQA4yvRd5k64nY1QsAycCpRH8hX14EUF)
12. [techrxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPb7IAysuaD16e88FL7lNsy9-177ZFcqDqoehmF5o2EUJ3zTRKFKHsFapQTtiupYtKy_Kep--9JR37YfBtfeFSkDtPU883mlcEwedpTUqbfzKSlkGolAHaBbBhBG2nbFN6iFdQZ3-Uo31riNKuyiCPRUDkaHBiC9q3ZHw=)
13. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfiBi8OPNghJZ6ZHDl0FOvlwJTZsDl5_IDUYntqsnu7d04vmmd-wickD1fmHepyTjyBvapP6mjke5PP_a6pTVlaHctbCuf78Tkg1vyF24F-KPQrKeWhxNwCr-U_4DMTxOYHxtnOh5ZLVAKcbhMo7-MDOiZ9W7NkkK-cl-QCm3jqaz4uMYuv1sT9e8PeUs47SbWF0fr37tHkAe4VqwMjeEyyDXtrQyaWXulvLfwIz7bsGNICm5j25rxog==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAGEOv0B2zsaeqR8rVfgk0CzGnURp5Jn45tFAsW5GiMoWcQ7IgjCUcKe9QrYMP9DwVkMSVXlSRK9c_zNeSzWp5ZrpaRUJtExYf6gwfrxsJS8Xhx5R_XNZMOw==)
15. [peerj.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1YjyhTyWSAevphlcmT-lD7OEfb0_6j02x19nVnUlIC5OS359okzEJRAU2eJ_4X8lDhcX90zMdyQpjnQN4VZKRw4h2iR0BGcTmWqTtRh0_tA4ciaI16mrR)
16. [lalejini.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU7wfBFlNH0wSs3p2DE46GG1q2-6s9jDVgFqN4cnB4hfaKcXQeUJ4p_42ajggV_23RwRhUc90ulWCt2V6yZ8z3WDm2qx8-Wz0V-A86VQNLD6KoUBcr2sb4pqQvidlDJXRloZLQxABbVREXCYfXbpcNVRqacHv0vH7iql3vp3KVANT2tg_AXSBXIKA3uKjIUBy_Vh5EMXdoEECNhA==)
17. [mun.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgZIJqd_hfuL-l1awPhpIl6lICw_Q9LKXK9d6sEsq33rZxHV4vkIbUqeW5iJsR0X4_GKkB3yzEN3WgK2IzNyGvKIKXoA63WPpl8n373O8N734rXgvviFUNVFhaUtPjpHRQwEmyGuYg1iwRkN_x0T9MjwKh)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHFC0dLHbEVYfCtCPqk-RXJCu2WDj3tutLa_xivVgFNN-hM-aDJMfjxpUY9-TfN9Ne9uYnPJ5c9zpz-Ljd9T9Ls9ZPHP60d2J6jnwmoAKWfnmsrBm9LQ==)
19. [sigevo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpR83sTJbpQ_KEDBzVUb_jRP0jcqrmfuN1g6hykI-f0eroY1VBzvmCXr9I0hJlgt8FN9X0XLgD2Un1rYZD9gBcq-JpcBNwUSRoc5jUg39-LOxKHVFgYUfn5muu5Tak)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3cOMBxzQSj7Ectb9D2AwUeNUQ2pi2tFmLtFccZrlhKth-TUCOjGj-8NWQ7Izp0ZbpLTg9U5-aslB5RLYg8LyE0qmFjEmgOVszh622K2bf8dJeMk5DiCWcyzwwB-8U1PORaLq2eGWwwOkys_umKJ42ujnhptA60U7Ydm8xqdbhPi2L7NAgrvC9uuaEpos8IEVIMqK2)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3PbTydiSXv8mWnstPUmAzQN9r5uJ68yN2wh7645GARH9Y2jAJ-UGsFNT5Nt5AP6OLt0WroVanFZOuA39SLXVPHtyScXfvsBvrIAycHt57eWBBQJSTJ1Sd-nK8UUPg3I05z5QEHj30M7zIUX_SkFP6o8jR_QQ0E2jOnPh_GrzXFZPwZb1nDzs0J_bZ6pqhJmnp_2FWDi4ej5eBxgfLkSf9XTuvK6CduQ==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWasF8pfi5L8ynZNBe0Lq07cW1dRkMeexQuVmdy56Y1mR6oE52MnYW14t3OYBXWonP9b1QWbQprAxCDraCjZyefSQFJvo1MQ7ng1OKaC_4MN5LFDAO5hosnfwY8THSjRzmEsTMq64OfNJlv-ZtW-lcoqUsQcuyTeFoStoqfEBiAHu9oSWOpMRUHtoxP7Mi-uLLUQc1xGjI2Yj7YDTJvA==)
23. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH36R4LSwARPyTXqm9yD8pKLDieEQvbrapDKp5uLOpMhOO2H76weAaFqaZBX-JN8VxorRIARuh9mmbuoJfRFjsOr70j0ecmdIBcxvnLa30yzfKy9eneoB2LgpFyvNNczsFcHd8u1BO6Zdu0K1EuMkAkqW-5GAodjvkDEuXLxPLdn0Xm5jt8Ly0Gd73l4fGhijhOxWlT14k_PC2goWD_ZVFCKNi51iXHR03eSEVCwNNi)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFr0JXWdG91or6hg39Q4C1uXyrbx0V_Esu9x9ReTT_2ccfW3_BHHinwjgctuyGzPjO1YkKBIGcWjtku_LPEjzAcnnb4_MF4FD3U-kody2hGiC0Mbj8hh3xxfB6FIocP0_d-1UlbYi7OMT8nyU6wAHNZATla3FUTdeoI5YhSn1WKhcKmD8L38J2Z7o1YOl5lXdLkF9A_tscRhSytGGUhfOnhNx1JW0aUJyOwefLfsJw=)
25. [diva-portal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-pWI_dtas3BpkBOqiCEUnuSUVMxoIXZBj8nXFK5aM-SvRr6JTh7xLVX9pkVD72jZ6cMcRKrMNej2DCgvAl2s1SDerPuQunzwXZr_Tl7BNejuSImB4yMibLqCrAUNRxVjG9j7--I7sSOzymVFsdHA1w_GIfX6S4Tw=)
26. [msu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT0Ii7ZsiFzCtYxWgOragmMWckiY8XWmboSXXCTxr5Bqk4RBJzmerlGGuhbiQsL99WfCPOQiwo0fqALjV152EZvqrmOepUbosaedANdw8gePn89sYEU3QZE2aKlACnlp_qVjoVUtnM)
27. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOxkvYPSSfZ0IJktFsPG0Mi0F2_DVu1GHJUh3JgXOJtVJstYhaXCdEcn9GN8E2M9bb9mVQJjGZTmJBUGtFj8F1onlYVCLGF7RDUiMipxrbJwHqn28Iuu_oqfssyczcoYq_6ralz9GMzvhNwzikJyo3UCnBNXyAd9fSATgtZW4UTm-gFjwuP9NYOHUg07nqxAeV4p9n5n1HoH_ooU8ktQHNflrKUQHzEpbIdHZQ39YtJHlxtqNYM5yI2w==)
28. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7qSzX-W_2qB47mBz7a53Ws671Cv1UJNELfQZEt_uYvTm3sajrG1dLl3n1gmHtn2x00xSqi95epGujRWs9SdtPn2yyYgL2780ddImWXEdOcD9MW4C1zJtEKzd7iZRT-2rtO1DXSUiBp_ffeU-1Q3MCDhcF6pCWYuL878_sBdbE2sckSwuzHLRTPClpCW6LiCyv6W4=)
29. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpWeRXgK9_IvDCBZjB5BkenXywRHDBnLfcCFjNU6IJm8332xrbbV2xLCSJB5_BJCcsCHV-rm8hwGEX5P-Iw6Sv3weLfLM9vKvfqsaiK_YLkfeIZv-NWIX937iTpUtnnMUEfDb6iPOb2YHMcjUMy1cvSZcmShjEkVvlhD9j1nTsJbx9eFxnpJpbo_OmcITkcOyspUURvivdxg==)
30. [maynoothuniversity.ie](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_QOkU4gOg3TIiuXc9tK-BxDMwV9k2bXXQnAwePqZozyuN30i3qBzsHMrto2EcR0wOj9XrBawv_mVK8-pBCf8tvAGwiKXZ2MqOys85OFV2cg6Wr5rBY3J_0m59Z_L5D6KPpruGZI_HMIwDKUJR5LPpeyI4kbM4AX-JzVk=)
31. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3pkDFsc1J2wrW50_edOChC2UjNDVFIeBTV68Savk1o0xByeGXhZX5ZjrnsrL7Zmtl6GZVEU1ZriM4_PDvnWu5E-FTFg3x5DJgDaOc8VuEQwCDpozPr7J5y_kQGO5aEUUH0ZBUmrCyErhD9nqUhrAfZeIIFfieE0fOeq0=)
32. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEui8U2NMCPdG-4vKY7AdH_lDRoVTwxymX3NMF7b6Qk43wlXBbOfgWMMqpRBbpl8snZKc0odm6iuDxG5h5-4Hm0naYf-vrhPZskyOd2byZzUG6e86don5LDILByr0CBmQuTs99bHCerSwNYzduX64AZfw==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbsmNsssBlPFFzAtHVTOWxswYWU-J0hw77dvYzZtYFMmCViuHOgiDSQr_eG9HW0iB5n8cJvCZj7itcK5CzDd7x-PRSRLOAywmx8lHntvnlas7aYvY8nrnNHA==)
34. [anu.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmWixukILlO8X_bIDuissCgWXRcLX9AI42uFRPHBUFybtDURQgnlQ9bjs2g-oCrS9g-EWm14E69nKB5PNt2_FFajvAXW9a58X_BUAcvogQEOqsO1X-H3X6K1El5NnWGE_hw5Bs9RmtQPB_7-dFdUUYVhnVBl84W1TR6rgz8sLzcM5mjuiKQdxXKphZmKwunKsCffbmHQ==)
35. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8gNHG5NfjTuspat8NVuNOIHLfkInZjGRaDlNshxzp3T-Sz25av9qCfln82iearPx0oN2By-dWdLQJ0Qn2Czp-3o7n7ZyQ4-jvGy_MvgQ70jlrrLz2rdcQ_ia1mwVkGYVum-Y7oSPVLg==)
36. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3-PB5bZlbKr41qfZ0gzZDct9xd3hrFT_4AlerAvWtts4MiIlMKopTF1ciIU9he5u6d4sqiMUWWwMJCcL0vhaX2iLvbcIDUBJbiWNvwexGj_DmKA6BK1YVw_d89pXGVw==)
37. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENMbEdg3PWYI0COsmk8ahtfKEycDLCOHi7IBefr1JHiIEGUp6073b1unSlZUEG3j1wBWfoSz9rmIaqoF3iipMYLdmO4FImxJ5qFYaaJh0FyrTQaX_XvBEyaOKItg==)
38. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy_WtBNP-Mw0Cc4OKq5jITxyPB02Syogr9027xdquppivEC_kxuJyX5LlisCLTocnPh7B-OJauRH89EOBqazS6Uqpn1O6BGTez4VpDavBvi_yMhTnYnJL3GSz6gPGos5GZiAbzykBZRUUMe4prZXzKcugca9p3MewoGC8=)
39. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6zqsV9BLwKulNy517MG2arfSVSudSRFfRp17CuQCy5VmQV5L1arKA66IqxMxXsf36x1Ko2m4nYxBHlVNO6QNNSicyxxiFDux6WJJTYQcV5r5xBEuseDf49kts9rjvMmx51uDxxn4LgjzRu2x9Q6M4hLlbkeZj3_gjoES7hPDsYmVRKJy5E7jvM85uc2nyhkQygrM=)
40. [gmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjDMAdHV-cwFvKCqqR8dwjPISkpiz_EFJ0oB-LRL8VpMk1fREZPrRw-4-hmGhIOCXAasx26GPeUieqn29lUj7EyjCLRz4D0koHchUM3JcbvDi7dqEELqgBYlaF8D4Q5i9adf4zTq8rGN_oCQ6s8UANJCc2XVMOCvH5-EVoK92zYr51dlBFAtaohODm8LLjys0XVbPqi1dqjPtq)
41. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEi9tBobKFSByjO7-ZfJN1RPm1IaTTVrjODe5DioGDz4joF6Y_iD71IclZRKVlpUo_b6qhYFmsshzvQxhXei8dSi7QoCkRzySoumeU_hO4nqK2zcqTZEvdUTKaiAIo1Jf13MmO2i3lFFw==)
42. [hpi.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhYiAldW_hpliExJWatmZnAZTPGdmRbW8C8qFF822p08rp085fSwVvt4tlpq4wld14v-zBQFHzF8PY9P_YxH7nxWqN-3l-FhPSX4ylCYOTOSrq8hMjCwel5XApTn818UBQeiKlAxjc5hyoyAdikLSy)
43. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvuzpMEyqi3MMrF8XgPElfPf5HT30vxoAx20opkvIL4XlSrTBHffwm6DKmtyX9nA-l8IiSlXCEwjBo8Kq3XN3MlhVXeQSNv2Yx_AkqJ3z84r2KgM4nmAABGHjPjJ75oPZ_kMcW9QrgCsRz_-e23WSFl_75pu4SowYi7rdyKh7bHM7WF4vvh6X2BanOng2EdE92Pzm0WGuFr9-A8zunfGKqzWkLDA==)
44. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhKcx9d6tuG9nkHPvLF-7tFezCNK28xH6YgXbTS2brvnkVnzw-tZlL7iK9tsgPR3mt8Byv22JECOKrAcDuzQ9lxWMTSL8QP1s2V002PyogMatJySjuKw==)
45. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUsybL4Ms0KedxX5J1uUhwQZJTU4GHAoPY9O6lRV61nF-uAqW2n-bS9eEzMNyvZBv2PhP-9x5TTPxQlVvbSU199MYrD-Eapn_HEksupzJkLFIKy2vJtH4vtFagogpY6w==)
46. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZr73tskIGur1ph1OG9R9f0sk1Nn0UGcZz5qPly74wMSzokaftLW8HxI0bnNnGCvELdridwc09l2Z9kUp0Hsy2xFiRLPTB6vmrzazyIFUls5ng20wL)
47. [tu-dortmund.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc9E4Z09fVnReCLl8rk817UV4V6pOuFDYCQYhR-tG7lIDqlO-lIXpHPcNbt6YPum3Iz7gaMfI9PXC2kkLd1xNeTMSagzOC5yCC-15dc1Y-f5VVsYXTrQcPm2YmIC_n2TL_vRXNOI1KcsbrR-gpHOqHZ9Jo8VHQ6fSpakh-hvYzY1XDhB8OpkYMIh4a9Lsd1ghQ2zcgj_k2K6zXHwet)
48. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX-03Ispybi60ftqZzRJDMglLjX-VOHILl3OEdBNehvkQgIhb7JZf_-TRmjxalYp1SWu6YWBfZxP_au_7bdUvKgLy38nwWDtqDUzJMPQOkL4YyN4sx0wpwEjH4dO6S2IpHOQ8OMnrUYFMcOFlma2a6lGXnKDe5Uks9y75xuaIEL315atnmIL0=)
49. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETPUXetSfEXKGCwO8VkeChKcJgJnvwQ3AYd0ZV3poU7Bpcy_jDgAGag3sreL2CXFfexN6RTvZODPvF9g8quCKj0HwG_oFVZSLHbkB_ad4ZJKxnmn1F-Msms-zT_FGZzRdpRs5qchYgRYyIyr51HTMT0Bgqiuk-RM-8TClWA8v3Up5iOu5N143rbk2xKlE_Tt_eEyEXQ5bMrixY2lQvRcutU0o-KuSgT98VqcqeYQ==)
50. [stackexchange.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWosO3YPL62ClsvuwMgcq6aG7PXS_sfUpMXnTd_-yjkyyyTtrVbZAHwFgIDQrEJIGr0KuDRU6SyNpBFgrrDBSXZtziSSHez_kCD68hVqKk880pD3NFOjD3aAG8jB2SAa1bGgPf2WEpYxDecxqwOe8aE10XpxYvL6B15HWEfhaPA0HP4Kfn8IVqqCSOaGqGGze-NxiTYUAR0Z7jJJbwkA==)
51. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYHhs_Za9XRoRsc0tgAxXdwe-H_tTXM6naHePR2JIQcUF0YgdNExnMNXUvb2WRlQreZLdfKufl0d5QsXg2oJghez5fsCKgEVCvEEIt6NZ-ClF8D9RskN2_hw==)
52. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5oMJ3wbNbklAQc4NN257ji1Bkx3wjsJsusfZAz-0BqLnIAU0AfqLQvNsGHAYtZyO4VWaUtyk3fKKpSI6mIuOrI3UVzCTfXtRsPNYxTwJd6KtEjvw3OE0f71XiayHD-PG5LWOA6wh6Gp9L6HARkaz09FMmw3vAiyfh6WXHSBs3Uxsp4fYipC-pAPgXowh1mXy2uwN_yBTybak3rORYQQW5SsIs-rYNxfybvZSo)
53. [pymoo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFw-88rEMQHCPqkEWQ4GDJ9rFiwQd8P3ombcsTPF4IKn2gmVs5Fp6NvS6h9V2khgMmbBU2jpLoNQxmjCKq9TvQL2jo-bGmQFQ8=)
54. [evotorch.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpnAYgmObCBz5bsKJzZ8QiI02v292Pv2UsIRUQmgJ4w7VJg2jg_alIQIA58B3jtQUnN7nhD1BdBIERvSnOhNpRWMVK3diu_v0TqfIkt8rR)
55. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2IhG2F33blSt7KiA_3xx4JARdh7fBozXl2UAU-7WAfPPLoyYjs5weQfiUipW3IbVFMcbuGaVwJmANInH9KBAI9__jSXOdarzJoGB22F8Odmz4K2lUug==)
56. [evotorch.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMGzVh322LcOhNj2C5d4CSHeBBwejsYuulK06V0HJgmpuB4L_FDDd-SuGWsU1Re7vefJ8Yx65CkyZuUvPdG82HYIO5X8e7eKxot1m9h-gBhxR1guR2RlGGjZjnWqbMceNLXBsQGWGwrAXabm_oXgLzGJIqxBaMy1LV2z5qdg==)
57. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyUa48eLeWBX24XrQxGl915WT0aeeKpKhKOK6UK7j-z-3uX3ntn2li6Z54pGi0Om2payzN0OhwFmOLuW1VQHVx4W_GyaNyPai6nwU3oSlQydqh3uxp6JBR9w==)
58. [sigevo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5KhBxRQzNCFR-jqEzLFACEpvJrbepcOad1a-qet2Qf8XHNdCcROnIfjDOM0Om-_LqyysVBRJdleql6O077P3ar7t1SjvUIgARh6zUvq9pq8w-j4cO3uBRDDsciYSEAsfWgjwGyuPGrtMjl2K8XKZL95mqUTHHWMCz7g==)
59. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5KrI3ZawrVNXRrU0Mq8434x_B695l-yKTTsKEi2nXhK1qKP6jW20-uATdKr-KCj1y2EBmXTNxZHFJqdD9NS53gvok65Jgxt8DK4LvVyI_Ts_oBlV-ATJcWg==)
60. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFK2zLx9fNySapvl_qET9evAVvFX4rvRF209anIHP1MXYZ1RdGbA0aRZKSaDFR4PeGmMxrCkw-zbJqUQE_RsEqt0boVkYTWNzNzh_ZCww4bsLmx30rTT3fZD8iKZOGDz9L4JvTwqO_EXop08M7WDViwp9tV8DawXX1KIsLLL3M3cR2bjFkWItUuJsgRkaM9hB3T3pCkV1Z1aYnm)
61. [hampshire.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHl_U8pUkSGTzoQ98OspolQuzL0CSXlX05OoTWNFwgUhwPaSa7fatXpRW-IiSkbyCfPYVHhjZnwB5KR1zkleB64RH9OmhSXP1zNi3Sh6D8dkaRSfMczABNwgDes9FRP0RUm7OdUsA==)
62. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHInV4q0rnmXVJxRVBaOLXt9-0LCjObg7ubBo26pRAP--8BlGAglHdhEwJVDhaUzLjpirtdKB09Vtwyvxs2nPUq6rnCOX_B8vxwqyJbEErwyNv4EXBDYbaJlD4qikiZ1jKWqG1WlqgyR2AsnlFlHA==)
63. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJDa2kKWYG8SpnpypFgPFCfZybi8VYRZBnNPARknf16bADjNDX7hbXa2CYl5lC07SiC8l1HIBDehjc6L9yZ_OBat19vBFVZOBcIgEdsk06ARP_MY_m)
64. [ucl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZCrOuv67U4AKRk_NL7qhbK3f5VClr_YUKOSnfLtJ8MeUrvjpZOWvOHpLKB32J_Wtgw3ub_4z-a3Bx8UQPPpMEv_8ZkGTpseF8s_UbR0-mOBl-7tHWec_fY4xqkkjZ4GzQnO3dLHQJjw==)
65. [esolangs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHiTbvjkvrd_IGGyqb6XEssoiwIId-peVaKMoO0VBG3LPg-wkQVuqtSnHgnrCNc4jV_fhH7gzMSAMptSbPs1wdeF4pFDZ3nooXc_R0w3u801JT-BzB)
66. [unibz.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERlEOofWysQedGxP4CDXluguwQuxVK9j1Hj3ZcLUWp4pEq5nwUFbhCAe59MQCJBjOaBCoy-UkdmrCVcIES2AkIv_HRJi3xvhGic95Gvm3xbfjqtCej2UZf_webVHG3Erd_aATQqzJTNh6dgQsuYYtDxtd6BkJzer9RuoQ3j-qXDaRb9RB9BCIrAo4OtYH1o7gGtsiy0kV2YA==)
67. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgoPZAAyp2ETDT4EWk-C_0L4VORDK7ZrlKqqMBjtb2rgyWHNjBTbpTYoNp_2dymqNAqOng8pLDHzXLNIg7TQOpLjfap_AUu0ehX6JxQwXfqGqTeBjW6_gX312Qf9MsjvzI1eIq5Vy_AI0ulwnHvt9p_MmfNsV7XA==)
68. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEB8_hVJ-rkJn14ZgLn3FxnTucZZWVmNlieHg4Y5OJv04NdBwcR2rHKh1BWEnHfxZr5nNn2qIiOzkEDkMUfvbbc97nDLY0TTz9cktzy7wYcLYiLKfQ0ISmS-6rIzVVEf0mSep0ZeapM1ItiIQfnVG-f5kggNADlrIjhZ9s3G4CsP-DNj-AT-vCl7_T4FweRhpln59A=)
69. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbal5lz9jjJhcdzAgrSCFpKF0FX5u4uePIzBD5wBfb31AYmOBT_madnaiCkqcGEPo16u4mxuSNsbS0GHWEhhFup4av-aqJJNRJjf-scooB3ulQweI3KQ==)
70. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGm61KMigpgb6jiKdSNao6uE-gGY3d5q8E5e_ABG6tafiwUCJLpNwrT4ijsjzH8yzHIs7sUy90WnvFrNB_wbjZHBuneu_WHPGN1-igQj7z-vujIcpUjwNsfyeFFH6q4U_B6Vabjb992b7BDd5pKO1-wlkvVGlHPy3acH9AQgOrsCUdHIcu0058PUilNJw8i2sZj)
71. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIHedkQNvVilBgUFZ5HAX2wqiSytPFR8Y5WOdWbN7FSYdmaud5vOSJ6xw5NH6sh9q-_PuTPtEHCFBdlqIhHn7A1l9hqCagk48PaRsJ_BV4WhDhyVCYAlLZUKGVc24hE7eYIK_IC64LRUsUrSdu6zeTxKHoyqA77haKaHrEvrk8MYN3-zpkPmkrcoBGWidiB4iIq6cxBqyF1AFVvEdOVy8=)
72. [put.poznan.pl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpurqDVrMBsfAbpI75jQfBeEekZIwcaE-FrAm2PDDDMEoYecsD6euhqSUGc-wCf9vCkwP-TAmd2aUWxtmxyoWAy97GWI9ey92R7NMnDOI-3K7FQ97dQflpiBRsBVzYInsOh54vrQsBcWqOXEanPlUn1AD0LJVgOyTJInfGpwEEapFyi1vVSFKcrHg=)
73. [hamilton.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHALfySHPu0I_iO-q2vDxl1T3p_YBV04IVX5-A03yCDw4vZvX8VI7nstpx0jspA7rncJ8nOZsBZYG3-WUp2C0CFqvyK5VSg8HaN-_Ma_AHo2TOzf7Kp0sueMsShlYlyoTr5l5pAjbblmBx4xeUFlzdQmLOidTKyqymt3jZ8oVZd9cbEfLOIKgkh)
74. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2bLI-uounqVkx804sxzJrDavKh28g9dh5VweLA8v7QFDr4rzOjMFflBiifMDd_PKIdv6vME-9YF_plXlbDxbvdH5i0yrWEknBNuYSV2HilVs9AwxadTUcGD4OKyGjfKX-vIT7D5hK8t2jMhGHp5jcvJT0YOZG5qK6v_R0Oedsmku2Uld0R-Xqfyabu3MJc0-N5S8CBqMzISZoqK1rXmELbspk_6850GTlnWmLjsEwe8CZxk4RvtXLCAYnMFb7Y_e3)

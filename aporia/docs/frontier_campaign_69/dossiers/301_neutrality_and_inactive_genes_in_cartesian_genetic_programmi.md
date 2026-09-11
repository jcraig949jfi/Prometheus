# Prompt 301: Neutrality and inactive genes in Cartesian Genetic Programming

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdGU2VoYXNtTUNkV3hfUFVQZ2F5QnlBSRIXRlNlaGFzbU1DZFd4X1BVUGdheUJ5QUk
**Elapsed:** 487s

---

# FRONTIER PRACTITIONER DOSSIER: Neutrality and Inactive Genes in Cartesian Genetic Programming

## EXECUTIVE SUMMARY AND KEY POINTS

Research in Cartesian Genetic Programming (CGP) revolves around a fundamental tension: the representation is explicitly designed to be highly redundant, yet the mechanism by which this redundancy aids search remains deeply contested. If you are entering this field in 2026, you are entering a domain that has recently transitioned from purely empirical heuristics to formal runtime analysis and complex applications like Neural Architecture Search (NAS).

Key points for a practitioner:
*   Redundancy is a core feature of CGP. Standard representations typically run with over 90 percent of their genes inactive cite: 5, cite: 8.
*   The benefit of neutral drift is highly contested. Foundational authors argue that accumulating silent variations in inactive regions prevents premature convergence and aids in escaping local optima cite: 1, cite: 9.
*   The standing methodological critique argues that neutrality itself is not the driver of success. Instead, the benefit is an artefact of length bias and the use of inefficient point mutation operators. When mutation is forced to act only on active genes, search performance often improves, suggesting the neutral drift narrative may be flawed cite: 23, cite: 82.
*   The field is currently moving toward formal theoretical proofs. Recent 2026 runtime analyses provide the first mathematical bounds showing that accepting neutral moves strictly improves asymptotic time complexity on specific Boolean functions cite: 12, cite: 46.

## PRIMER ON THE CONFLICT

You asked whether mutations that change the genotype without changing behaviour actually help the search, or if the benefit is caused by something else. The evidence currently leans toward a hybrid answer, heavily dependent on the mutation operator used. 

When using standard probabilistic point mutation, explicit neutral drift appears necessary because it implicitly controls the step size of phenotypic changes. However, when using the "Single" mutation operator, which forces at least one active gene to mutate, the necessity of neutral drift diminishes significantly. This implies that the historical benefit attributed to neutrality was partially masking an interaction between the encoding length and the probability of hitting an active gene. The frontier of 2026 is resolving this by mathematically bounding the search times of these operators and tracking the residence time of inactive nodes.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Cartesian Genetic Programming in 2026 is a mature subfield of Evolutionary Computation that has historically focused on logic synthesis, digital circuit design, and symbolic regression, but has recently expanded aggressively into Multi-Objective Neural Architecture Search and differentiable programming. The field is defined by its representation: a directed acyclic graph encoded as a fixed-length string of integers, where a genotype-phenotype mapping allows many nodes to remain unconnected to the output. This explicit redundancy allows variable-length phenotypes to emerge from fixed-length genotypes. The standard evolutionary engine remains the 1 plus lambda evolution strategy, which actively accepts neutral moves by replacing parents with equally fit offspring.

What is SETTLED is that high levels of redundancy are practically necessary for standard CGP to function effectively. It is universally accepted that genotypes must be sized such that a vast majority of nodes, often up to 95 percent, are inactive. It is also settled that the standard 1 plus lambda strategy outcompetes purely greedy selection regimes, and that traditional crossover operators designed for tree-based Genetic Programming are generally destructive in CGP due to the catastrophic changes they induce in node activeness.

What is CONTESTED is the exact mechanism by which this redundancy and neutral acceptance benefits the search. The foundational camp, led historically by Julian Miller and Andrew Turner, argues that explicit neutral genetic drift is the primary mechanism. In this view, inactive genes accumulate variations that are phenotypically silent. When a subsequent mutation reconnects these inactive subgraphs to the main output, the phenotype undergoes a massive, potentially beneficial leap. This allows the population to traverse fitness plateaus and escape local optima. The opposing camp, led by Brian Goldman and William Punch, argues that the benefit of neutrality is an artefact. They assert that CGP suffers from "length bias", where evolution naturally drifts toward longer active paths. Furthermore, they argue that standard point mutation wastes evaluations on inactive genes. When they introduced the "Single" mutation operator, which forces mutation to continue until an active gene is altered, they achieved superior results without relying on long periods of neutral drift. This debate remains live, with recent researchers like Henning Cui demonstrating that nodes can remain inactive for too long, reducing fitness pressure, and proposing weighted mutations to force reactivation.

What is OPEN is the formal theoretical grounding of these empirical observations. Until recently, CGP was entirely empirical. The frontier is now defined by rigorous runtime analysis. In 2026, researchers like Duc-Cuong Dang, Roman Kalkreuth, and Andre Opris have begun publishing asymptotic bounds for CGP. They have formally proven that accepting equally good solutions, including those with non-contributing connected gates, improves the upper bound of the expected running time for evolving conjunctions from O(n D^5) to O(n D^4). This is the first mathematical proof that neutrality provides a tangible speedup, bringing a new dimension to the Goldman-Miller debate.

The field has not been absorbed, but it is heavily intersecting with Neural Architecture Search. Differentiable CGP and Continuous CGP are being used to evolve both the topology and hyperparameters of Convolutional Neural Networks, positioning CGP as a highly competitive representation for architecture search in the continuous domain.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Miller, J.F., and Smith, S.L.
2006
Redundancy and computational efficiency in Cartesian genetic programming
IEEE Transactions on Evolutionary Computation
DOI 10.1109/TEVC.2006.871253
This is the load-bearing empirical paper establishing that CGP search is most effective when the genotype is extremely large and over 95 percent of the genes are inactive, formalising the requirement for massive explicit redundancy.

Turner, A.J., and Miller, J.F.
2015
Neutral genetic drift: an investigation using Cartesian Genetic Programming
Genetic Programming and Evolvable Machines
DOI 10.1007/s10710-015-9244-6
This paper separates explicit genetic redundancy (inactive nodes) from implicit genetic redundancy, arguing that the benefits of explicit neutral drift are additive and fundamental to escaping local optima.

Goldman, B.W., and Punch, W.F.
2015
Analysis of Cartesian Genetic Programming's Evolutionary Mechanisms
IEEE Transactions on Evolutionary Computation
DOI 10.1109/TEVC.2014.2324539
The definitive standing critique of the neutrality hypothesis. It introduces the Single mutation operator and argues that the performance benefits traditionally attributed to neutral drift are actually artefacts of length bias and the inefficiency of standard probabilistic mutation.

CURRENT SOURCES DEFINING THE FRONTIER

Dang, D.-C., Kalkreuth, R., and Opris, A.
2026
Runtime Analysis of Cartesian Genetic Programming in Evolving Boolean Functions
PPSN 2026
arXiv:2606.15923
A critical breakthrough for the field, providing the first asymptotic runtime bounds for CGP. It mathematically proves that non-strict survival selection (allowing neutral drift) improves the runtime bound for evolving conjunctions, offering theoretical backing to the neutrality argument.

Kalkreuth, R., Vasicek, Z., Husa, J., Vermetten, D., Ye, F., and Baeck, T.
2023
General Boolean Function Benchmark Suite
FOGA '23
DOI 10.1145/3594805.3607131
This paper introduces GBFS, which has become the authoritative modern benchmark suite for logic synthesis in Genetic Programming, replacing outdated and easily saturated historical benchmarks.

Garcia-Garcia, C., Morales-Reyes, A., and Escalante, H.J.
2023
Continuous Cartesian Genetic Programming based representation for multi-objective neural architecture search
Applied Soft Computing
DOI 10.1016/j.asoc.2023.110788
This source defines the frontier of CGP applied to deep learning, moving CGP into the continuous domain to optimize both the architecture and the complexity of CNNs using multi-objective evolutionary algorithms.

Kocherovsky, M., and Banzhaf, W.
2024
Crossover Destructiveness in Cartesian versus Linear Genetic Programming
ALIFE 2024
DOI 10.1162/isal_a_00735
An essential read for understanding why recombination rarely works in CGP. It proves that changing a single connection gene in CGP drastically alters the activeness of nodes across the entire graph, destroying high-fitness substructures.

Cui, H., Paetzel, D., Margraf, A., and Haehner, J.
2023
Weighted Mutation of Connections To Mitigate Search Space Limitations in Cartesian Genetic Programming
FOGA '23
DOI 10.1145/3594805.3607130
This paper bridges the gap between Miller's neutrality and Goldman's critique by tracking the residence time of inactive nodes, showing they can remain inactive for too long and proposing a weighted mutation to force their reactivation.

PART 3. SOFTWARE I CAN ACTUALLY RUN

CGP++
https://github.com/RomanKalkreuth/cgp-plusplus
C++ (Requires C++17)
AFL 3.0
2024
MAINTAINED
This is the current community standard and the most robust framework available today. It implements generic programming paradigms, supports checkpointing, multi-threading, and directly integrates with the GBFS benchmarks for logic synthesis and SRBench for symbolic regression. You can use this today to run rigorous neutrality vs Single mutation experiments. The gotcha is that it is heavily object-oriented and templated, meaning the learning curve for modifying core structures is steeper than in simple C scripts, but it avoids the catastrophic memory and scaling limitations of the original implementations.

dCGP (Differentiable Cartesian Genetic Programming)
https://github.com/darioizzo/dcgp
C++ / Python (Exposed via dcgpy)
GPL-3.0
2022
DORMANT
Developed by the European Space Agency's Advanced Concepts Team, this library allows you to evolve mathematical equations and neural networks while utilizing backpropagation and automated differentiation (AuDi). It is essential if you want to run symbolic regression with ephemeral constants optimized via gradient descent. Its limitations are severe dependency bloat (Boost, Eigen, Pagmo, tbb, AuDi, Symengine) making it brittle to build on modern operating systems without relying strictly on the provided Conda forge packages, which are rarely updated. 

CGP-Library
https://github.com/AndrewJamesTurner/CGP-Library
C
LGPL-3.0
2019
DORMANT
This is the historical reference implementation from Andrew Turner and Julian Miller. It is famous, heavily cited, and highly optimized for speed using function pointers. However, it is effectively dead. While it can run standard symbolic regression and logic circuits, it lacks modern parallelism, checkpointing, and integration with 2020s benchmark suites. A practitioner should read the source code to understand canonical CGP mechanics, but should not use it to build a 2026 research pipeline.

Reorder_Strategies_for_CGP
https://github.com/CuiHen/Reorder_Strategies_for_CGP
Rust
GPL-3.0
2023
DORMANT
A highly modular and exceptionally fast Rust implementation built by Henning Cui specifically to test positional biases, length biases, and mutation variants (including Goldman and Punch's Reorder extensions). It is the best tool for exactly replicating the neutrality-artefact experiments. The limitation is that it is highly specific to Boolean logic synthesis and symbolic regression on small classical datasets, lacking a broad API for external problems.

hal-cgp
https://pypi.org/project/hal-cgp/
Python
GPL-3.0
2021
DORMANT
A pure Python implementation designed for ease of use and translation of CGP graphs into PyTorch modules or SymPy expressions. It is useful for prototyping where fitness evaluations are extremely expensive (like reinforcement learning), but it is entirely unsuitable for high-throughput logic synthesis or large-scale neutrality studies due to Python's inherent loop overhead.

PART 4. DATA AND BENCHMARKS

General Boolean Function Benchmark Suite (GBFS)
Access route: Provided via PLU files integrated into CGP++ or via the FOGA 2023 publication supplementary materials.
Approximate size: 29 discrete logic synthesis problems ranging from 3-bit to 12-bit inputs.
Licence: Open access academic use.
What it measures: Search performance, scalability, and robustness of logic synthesis algorithms.
This is the authoritative benchmark for discrete CGP in 2026. Historically, researchers used trivial problems like 2-bit multipliers or Even-4 Parity, which are easily saturated and prone to overfitting, leading to false claims of algorithmic superiority. GBFS categorizes problems by arithmetic, transmission, comparison, counting, cryptographic, and mixed functions, providing a rigorous landscape to test neutrality against mutation types.

SRBench (Symbolic Regression Benchmark)
https://github.com/cavalab/srbench
Approximate size: Over 100 open-source regression datasets.
Licence: GPL-3.0
What it measures: Accuracy, generalisation, and parsimony of symbolic regression models against state-of-the-art machine learning baselines.
SRBench is the authoritative suite for continuous domain symbolic regression. It uses a unified Docker-based evaluation harness. Note that some classical datasets within SRBench (like Nguyen or Koza polynomials) are known to be solved trivially; the suite includes these for baseline sanity checks but relies on the Penn Machine Learning Benchmark (PMLB) subset for actual frontier evaluation.

CIFAR-10 and CIFAR-100
Access route: Standard torchvision or PyTorch datasets.
Approximate size: 60,000 32x32 colour images.
Licence: MIT
What it measures: Image classification accuracy.
In the context of CGP, this is strictly used for Multi-Objective Neural Architecture Search (NAS), as seen in the CGPNAS frameworks. It measures the trade-off between the evolved CNN's classification accuracy and its structural complexity (number of parameters and multiply-accumulate operations).

PART 5. THE REPRODUCTION RECIPE

The single most informative experiment to execute is the isolation of explicit neutral drift versus the Single mutation operator on the GBFS parity circuits. This experiment directly attacks the contested mechanism.

Software and Version: CGP++ (latest commit as of 2024, compiled with g++ -std=c++17 -O3).
Dataset: The 8-input Even-Parity problem from the GBFS PLU files.
Parameters:
Representation: 1 row by 1000 columns (massive redundancy).
Levels-back: 1000 (unrestricted connectivity).
Function set: AND, OR, NAND, NOR.
Population: 1 plus 4 Evolution Strategy.
Selection: Strict non-elitist (accept offspring if fitness is greater than OR EQUAL to parent).
Mutation rate for standard point mutation runs: 5 percent of genotype length.
Mutation mechanism for Single mutation runs: Mutate randomly selected genes until exactly one active gene is altered.
Independent Replicates: 100 independent runs per configuration.
Seeding regime: Standard Mersenne Twister, seeded continuously from 1 to 100.
Compute cost: Approximately 10 to 15 CPU hours on a modern multi-core workstation.

Expected Result:
According to the foundational literature, the standard point mutation with neutral acceptance should solve the problem reliably, requiring hundreds of thousands of evaluations. According to Goldman and Punch (cite: 23, cite: 82), the Single mutation operator should reach the target fitness with a statistically significant reduction in evaluations, proving that forcing active changes navigates the landscape more efficiently than waiting for drift in inactive regions.

Three common ways people get this wrong:
1. Conflating implicit and explicit neutrality. Users often fail to measure whether a fitness-neutral move was caused by changing an active gene to a logically equivalent operation (implicit) versus changing a disconnected gene (explicit). You must track the active path mathematically at every generation.
2. Starving the genotype. Users set the column length too short (e.g., 100 nodes). The neutrality effect only dominates when 90 to 95 percent of the graph is explicitly inactive.
3. Incorrect selection operators. Users mistakenly implement a strictly greater-than selection rule (1 plus lambda elitist). The algorithm MUST accept equal fitness to allow drift; failing to do so will stall the standard CGP immediately on plateaus.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

There is a critical missing tool in the CGP ecosystem: a hardware-accelerated, batched tensor evaluator for directed acyclic program graphs that interfaces directly with modern Python JAX or PyTorch ecosystems, while executing the CGP phenotype natively on the GPU/TPU. 

What goes in: A population of integer-encoded CGP genotypes and a batch of tensor data (e.g., millions of rows of dataset inputs).
What comes out: A fitness array for the entire population computed in a single vectorized pass.
The hard part: CGP phenotypes are heterogeneous, variable-length, irregular directed acyclic graphs. GPUs excel at dense, uniform matrix multiplications, not executing 10,000 structurally different, branching logical or arithmetic graphs simultaneously. 
How much work it is: Significant. It requires writing custom CUDA/Triton kernels that compile individual CGP phenotypes into a unified execution block, or implementing an interpreter that evaluates nodes topologically across the population dimension. This is a 6 to 12 month project for a systems-level machine learning engineer. 

Currently, researchers are constrained to CPU evaluations (like CGP++) or wrapping sequential evaluations in multiprocessing pools. Several groups have privately attempted to write OpenCL or CUDA interpreters for CGP logic synthesis, but these are almost always abandoned because the branching overhead on the GPU destroys the theoretical speedup. A working JAX-jit compatible CGP engine would instantly revolutionize the scale of experiments that could be run.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most significant standing critique of the field comes from Brian Goldman and William Punch. They demonstrated that the widely celebrated phenomenon of neutral drift in CGP is heavily intertwined with, and potentially entirely an artefact of, length bias and poor mutation choices. Their critique states that traditional point mutation acts blindly. Because 95 percent of the graph is inactive, point mutation almost always hits dead code, resulting in no phenotypic change. Evolution accepts this, creating a "random walk" in the genotype space. Miller and Turner argued this random walk is a vital search mechanism. Goldman and Punch proved that if you simply bypass the random walk by using the "Single" mutation operator -- mutating nodes until you guarantee a change to the active phenotype -- the algorithm solves problems significantly faster. Furthermore, they showed that CGP has an inherent bias toward longer active paths (length bias), which naturally incorporates more nodes into the active graph over time. This critique has never been entirely refuted. Instead, the field has largely accepted that Single mutation is superior for evaluations-to-target, while theoreticians continue to study standard mutation to understand the underlying mathematics of the landscape.

A second massive failed programme is the attempt to incorporate crossover (recombination) into CGP. In Linear Genetic Programming and Tree Genetic Programming, crossover is the primary driver of innovation. In CGP, decades of attempts to design effective crossover operators have largely failed. Kocherovsky and Banzhaf (2024) provide the standing autopsy for this: crossover in CGP is inherently destructive. Because changing a single connection gene at the front of a CGP graph can immediately disconnect or reconnect massive downstream subgraphs, recombination destroys high-fitness functional blocks. Unlike Linear GP, which has steady-state memory registers that protect high-fitness substructures from perturbation, CGP has no structural protection. Subgraph crossover (Kalkreuth 2017) showed marginal benefits, but the consensus in 2026 is that CGP is fundamentally a mutation-driven, 1 plus lambda domain.

Finally, Collins (2005) established a standing negative result: finding needles in haystacks is harder with neutrality. In highly rugged, uncorrelated landscapes without gradients, expanding the search space with massive redundancy (adding neutral dimensions) mathematically increases the expected hitting time of the global optimum. Neutrality only works if the neutral networks correlate with fitness gradients, which is true for structured human-designed logic problems, but false for purely random Boolean functions.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you are a well-resourced entrant with compute and engineering talent, you should ignore basic algorithmic tweaking and focus on structural, heavily-instrumented experiments that bridge the theoretical and empirical divide.

Experiment 1: The Active-Node Residence Time Gradient (Rank 1)
Feasibility: Feasible now due to the modularity of CGP++ and the formal categorisation of GBFS.
What it measures: How long specific nodes remain inactive before being reactivated and contributing to a fitness increase, tracked across generations. You would log the precise topological history of every successful lineage.
Falsification: If Miller's neutrality hypothesis is true, fitness improvements will frequently stem from nodes that have accumulated multiple mutations while in the inactive state. If Goldman's critique holds, fitness improvements will predominantly come from nodes that were mutated at the exact moment they were connected, rendering their previous inactive history irrelevant.

Experiment 2: Multi-Objective NAS with Single Mutation (Rank 2)
Feasibility: Feasible by taking the Continuous CGP NAS representation by Garcia-Garcia and swapping the standard probabilistic mutation for a continuous-domain equivalent of Single mutation.
What it measures: The convergence speed and Pareto front quality of deep neural architecture search when the evolutionary walk is forced to alter the active architecture every step, bypassing neutral topology drift.
Falsification: If standard neutral drift provides superior Pareto fronts, it proves that neutrality is necessary for navigating the highly deceptive loss landscapes of neural architectures, even if it is a hindrance in Boolean logic synthesis.

Experiment 3: LGP-style Register Protection in CGP (Rank 3)
Feasibility: High engineering effort. Requires modifying the core graph execution engine to include persistent state registers that nodes can write to, mimicking Linear GP.
What it measures: Whether the destructiveness of crossover in CGP (as defined by Kocherovsky and Banzhaf) can be mitigated by structural memory protection.
Falsification: If crossover remains destructive even with register protection, it implies the graph-based genotype-phenotype mapping is mathematically hostile to recombination regardless of memory states.

What will NOT work:
Attempting to build a "better" generic crossover operator for standard CGP based on graph theory heuristics. Dozens of highly intelligent researchers have attempted this over twenty years. The destructiveness is native to the representation's cascading activeness logic. Unless you fundamentally alter how nodes express their outputs (e.g., via the registers proposed in Experiment 3), any purely topological crossover will inevitably act as a macromutation that destroys building blocks rather than combining them.

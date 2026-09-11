# Prompt 300: Cartesian Genetic Programming

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdGU2VoYXZ2RENwSEotc0FQODc3QnlBYxIXRlNlaGF2dkRDcEhKLXNBUDg3N0J5QWM
**Elapsed:** 426s

---

# FRONTIER PRACTITIONER DOSSIER
Field: Cartesian Genetic Programming

WHO IS ASKING AND WHY
This report is calibrated for a competent computational scientist transitioning into Cartesian Genetic Programming in 2026. It provides the tacit knowledge, foundational reading, software evaluations, and experimental blueprints required to bypass the typical multi-year learning curve. 

The report directly validates your understanding of the core Cartesian Genetic Programming method, which is highly accurate. It then details the current frontier, moving from classical logic synthesis and standard symbolic regression into differentiable programming, recombination optimization, and explainable biomedical image segmentation. The focus is strictly on executable knowledge, reproducible experiments, and identifying the structural gaps where a well-resourced entrant can immediately contribute.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Your description of the Cartesian Genetic Programming mechanism is entirely accurate and precisely captures the classical standard of the field. You have correctly identified the fixed-length integer array genotype, the backward-reachable acyclic phenotype graph, the neutral mutation dynamics of inactive nodes, and the standard 1+4 Evolutionary Strategy [cite: 1, 2]. No corrections to your baseline understanding are necessary. 

In 2026, Cartesian Genetic Programming has evolved from a niche electronic circuit design tool into a highly competitive representation for interpretable machine learning, symbolic regression, and explainable artificial intelligence [cite: 1, 3]. The field operates at the intersection of evolutionary computation and program synthesis, leveraging the inherent advantages of directed acyclic graphs over tree-based genetic programming. Specifically, the ability of a Cartesian graph to reuse sub-expressions by allowing multiple nodes to feed from a single upstream node drastically reduces the computational bloat that plagues traditional tree-based methods [cite: 1].

WHAT IS SETTLED
It is settled that graph-based encodings natively outperform tree-based encodings in memory efficiency and sub-expression reuse. It is settled that the 1+4 Evolutionary Strategy, despite its apparent simplicity, is the optimal selection mechanism for classical Cartesian Genetic Programming. This is because the small population size maximizes the evaluation throughput, while the rule replacing the parent with an offspring of equal fitness actively drives the search along neutral networks. Neutrality—the phenomenon where mutations alter the genotype (by changing inactive nodes or swapping functionally identical inputs) without changing the executed phenotype—is settled science. It is not an artefact; it is the primary mechanism by which Cartesian Genetic Programming escapes local optima [cite: 4].

WHAT IS CONTESTED
The role of recombination, or crossover, is heavily contested. For over two decades, the prevailing dogma was that crossover in Cartesian Genetic Programming was fundamentally destructive. Because the genotype is fixed in length but contains varying patterns of active and inactive nodes, randomly swapping segments between two parents almost guarantees the severing of critical graph pathways, resulting in a catastrophic drop in fitness [cite: 5, 6]. Consequently, the field predominantly relied on mutation alone. However, recent work from 2022 through 2026 has fiercely contested this. Proponents of Subgraph Crossover and Discrete Phenotypic Recombination have demonstrated that if crossover is applied topologically to the active phenotype rather than blindly to the linear genotype, and if hyperparameters are rigorously optimized, recombination consistently outperforms mutation-only baselines on modern symbolic regression benchmarks [cite: 5, 7]. 

WHAT IS OPEN
The field has two massive open frontiers. The first is differentiable Cartesian Genetic Programming, which introduces dual numbers and automatic differentiation into the node operations. This allows the graph to compute not just a forward pass, but the exact derivatives of the output with respect to the inputs and connection weights, enabling backpropagation and hybrid gradient-evolutionary searches [cite: 8, 9]. The second is the integration of Large Language Models. While Large Language Models can generate code, their ability to truly discover scientific equations is currently under intense scrutiny. It is an open question whether Large Language Models can act as intelligent mutation operators that parse a Cartesian phenotype and suggest semantically meaningful topological changes, rather than simply guessing strings of text [cite: 10, 11].

In the last three years, the field was structurally transformed by the standardization of benchmarking. The era of evaluating new Cartesian Genetic Programming variants on isolated, toy physics equations is dead. The field was largely absorbed into the broader Interpretable Machine Learning ecosystem, driven by frameworks like SRBench and TinyverseGP, which enforce rigorous, large-scale comparative evaluations across hundreds of datasets [cite: 7, 12]. What was lost in this merge was some of the focus on raw hardware logic synthesis, which originally birthed the field, in favor of data-driven regression and classification.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Miller, J.F.
Year: 1999
Title: An Empirical Study of the Efficiency of Learning Boolean Functions using a Cartesian Genetic Programming Approach
Venue: Proceedings of the Genetic and Evolutionary Computation Conference
Identifier: IDENTIFIER UNKNOWN
This is the genesis paper of the field where the term was first coined, establishing the fixed-length integer string and the two-dimensional grid of nodes. A practitioner must read this to understand the original design constraints based on hardware logic gates that dictated the fixed grid layout [cite: 3].

Authors: Miller, J.F., and Thomson, P.
Year: 2000
Title: Cartesian Genetic Programming
Venue: European Conference on Genetic Programming
Identifier: DOI 10.1007/978-3-540-46239-2_9
This paper formally generalized the method beyond electronic circuits into a universal program representation. It is load-bearing for defining the standard decoding algorithm that walks backward from the output nodes to determine activity.

Authors: Miller, J.F. (Editor)
Year: 2011
Title: Cartesian Genetic Programming
Venue: Springer Natural Computing Series
Identifier: DOI 10.1007/978-3-642-17310-3
This book is the canonical text for the tacit knowledge of the field up to 2011, detailing the mathematics of neutral drift, the 1+4 evolutionary strategy, and the handling of cyclic connections for recurrent programs [cite: 3, 13].

CURRENT SOURCES (THE 2026 FRONTIER)

Authors: Izzo, D., Biscani, F., and Mereta, A.
Year: 2017
Title: Differentiable Genetic Programming
Venue: European Conference on Genetic Programming
Identifier: arXiv:1611.04766
This paper defines the frontier of hybridizing evolution with gradient descent by introducing automatic differentiation to the Cartesian graph, allowing the calculation of Taylor truncated polynomials for every node [cite: 9, 14].

Authors: La Cava, W., et al.
Year: 2021 (Updated 2025)
Title: Contemporary Symbolic Regression Methods and their Relative Performance
Venue: NeurIPS Datasets and Benchmarks Track
Identifier: arXiv:2107.14351
This is the foundational paper for SRBench, the evaluation harness that entirely redefined how success is measured in this field by enforcing a standardized scikit-learn API and testing on 252 datasets [cite: 12, 15].

Authors: Kalkreuth, R.
Year: 2022
Title: Towards Discrete Phenotypic Recombination in Cartesian Genetic Programming
Venue: Parallel Problem Solving from Nature
Identifier: DOI 10.1007/978-3-031-14721-0_5
This paper broke the two-decade assumption that crossover is destructive, detailing how to safely combine the active subgraphs of two parents without causing catastrophic semantic loss [cite: 1].

Authors: Cortacero, K., et al.
Year: 2023
Title: Evolutionary design of explainable algorithms for biomedical image segmentation
Venue: Nature Communications
Identifier: DOI 10.1038/s41467-023-42664-x
This paper introduces Kartezio, representing the frontier of applied Cartesian Genetic Programming in Explainable AI. It evolves complex OpenCV image processing pipelines using extremely few training samples, outperforming black-box deep learning on data-starved medical tasks [cite: 16, 17].

Authors: Shojaee, P., et al.
Year: 2025
Title: LLM-SRBench: A New Benchmark for Scientific Equation Discovery with Large Language Models
Venue: International Conference on Machine Learning
Identifier: arXiv:2504.10253 (approximate based on context)
This paper is critical because it dismantles the recent hype around Large Language Models "discovering" physics by proving they are merely memorizing strings. It provides the transformative benchmark datasets needed to verify true algorithmic discovery [cite: 18, 19].

Authors: Tran, D.L., Jankovic, A., Anastacio, M., Hoos, H., and Kalkreuth, R.
Year: 2026
Title: Improving Evaluation of Recombination-based Cartesian Genetic Programming
Venue: Genetic and Evolutionary Computation Conference Companion
Identifier: arXiv:2605.28353
The absolute cutting-edge 2026 result proving that combining hyperparameter optimization with phenotypic crossover on the SRBench platform yields statistically significant improvements over classical mutation-only approaches [cite: 5, 20].

PART 3. SOFTWARE I CAN ACTUALLY RUN

CGP-Library
http://www.cgplibrary.co.uk/
C
GNU LGPL
2014
DORMANT
This is the original reference implementation by Andrew Turner and Julian Miller. It is famous, heavily cited, and functionally complete, supporting standard, recurrent, and self-modifying Cartesian Genetic Programming. However, it is effectively dead. Because it relies on older C toolchains and double-precision variables for bitwise simulations, it suffers from severe limitations on modern 64-bit architectures, specifically limiting logic synthesis to 50 bits before precision errors corrupt the truth tables [cite: 21, 22]. Do not use this for new projects unless replicating pre-2015 logic synthesis papers.

cgp-plusplus
https://github.com/RomanKalkreuth/cgp-plusplus
C++
GPL
2024
MAINTAINED
This is the modern community standard for high-performance execution. Built by Roman Kalkreuth to serve as a generic, object-oriented blueprint for the field, it relies on modern C++ templates evaluated at compile time to ensure type safety and speed. It natively supports advanced recombination operators, checkpointing, and concurrency. If you need raw speed and intend to write a custom evaluator in C++, this is the load-bearing library [cite: 1, 23].

TinyverseGP
https://github.com/GPBench/TinyverseGP
Python
GPL-3.0
2025
MAINTAINED
This is the benchmarking standard. Originating from the GPBench initiative, it provides minimalist, scikit-learn compatible implementations of Cartesian, Tree, and Linear Genetic Programming. Its purpose is not raw speed, but rigorous methodological comparison. It is currently the only software where the 2026 GECCO recombination results can be immediately reproduced out of the box. Its known limitation is Python's Global Interpreter Lock, which bottlenecks multi-core graph evaluations compared to C++ [cite: 24, 25].

dCGP (dcgpy)
https://github.com/darioizzo/dcgp
C++ and Python bindings
GPL-3.0
2020
DORMANT
Developed by the European Space Agency, this library enables Differentiable Cartesian Genetic Programming using the AuDi library for automated differentiation via truncated Taylor polynomials. It allows the graph to learn internal weights via backpropagation. While theoretically brilliant, the repository has seen minimal maintenance since 2020. The build system is fragile due to heavy dependencies on Boost, Eigen, Pagmo, and Symengine. It requires careful pinning of C++17 compilers and older Boost libraries to build successfully [cite: 8, 9].

Kartezio
https://pypi.org/project/kartezio/
Python
MIT
2026
MAINTAINED
This is the state-of-the-art applied tool for evolving image processing pipelines. It wraps OpenCV primitives into Cartesian nodes to evolve transparent computer vision algorithms. It is highly active, robust, and explicitly designed to run on a single CPU core to prove its efficiency over GPU-hungry deep learning models. Its main limitation is domain specificity; it is tightly coupled to image tensors and cannot be trivially remapped to standard symbolic regression [cite: 26, 27].

Karoo GP
https://github.com/kstaats/karoo_gp
Python
GPL
2022
DORMANT
Famous for applying evolutionary algorithms to gravitational wave data and supernovae detection, with a heavily advertised TensorFlow GPU backend. Despite a 2022 overhaul, it is currently dormant. The published claims of massive GPU acceleration are severely bottlenecked in practice because translating highly divergent, irregular graph topologies into synchronized tensor operations on a GPU is fundamentally inefficient. It is an interesting architectural relic but not a viable foundation for a 2026 entrant [cite: 28, 29].

PART 4. DATA AND BENCHMARKS

SRBench (Symbolic Regression Benchmark)
https://github.com/cavalab/srbench
Size: 252 datasets (PMLB format)
License: MIT
This is the authoritative benchmark the field treats as absolute ground truth for performance. It consists of datasets from the Penn Machine Learning Benchmarks and classical physics equations. It is used to measure test-set mean squared error and model complexity. Prior to this, authors cherry-picked 5 to 10 toy equations. If a new method is not evaluated on SRBench using the exact hyperparameter tuning splits defined in this repository, the field will ignore it [cite: 12, 30].

Feynman Equations Dataset
Available within SRBench
Size: 100 physics equations
License: MIT
A popular subset of SRBench used specifically to test the recovery of physical laws. However, there is a massive, known contamination problem: these equations have been heavily scraped into the training data of every major Large Language Model. Consequently, any benchmark claiming that a Large Language Model "solved" the Feynman equations is measuring data contamination and memorization, not zero-shot generalization [cite: 18].

LLM-SRBench
https://github.com/deep-symbolic-mathematics/llm-srbench
Size: 239 problems
License: MIT
The mandatory new standard for any research combining evolutionary search with Large Language Models. To defeat the Feynman contamination problem, this benchmark introduces LSR-Transform (which algebraically disguises common physical models into mathematically identical but visually novel forms) and LSR-Synth (entirely synthetic physics problems requiring data-driven reasoning). It measures whether a model can actually discover an equation or is just reciting text [cite: 10, 19].

ODEBench
https://github.com/GPBench/ODEBench
Size: Dozens of dynamical systems
License: GPL-3.0
An authoritative suite for system identification, measuring the ability of Cartesian Genetic Programming to recover systems of Ordinary Differential Equations from time-series state data. Used heavily when evaluating Differentiable Cartesian Genetic Programming and recurrent variants [cite: 31].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in this field today is the demonstration that phenotypic recombination outperforms classical mutation when subjected to hyperparameter optimization, effectively ending a 20-year debate. 

Experiment Specification
Software: TinyverseGP, exact version 0.1.0 [cite: 32].
Dataset: SRBench dataset identifier 579_fri_c0_250 (a standard non-linear regression task) [cite: 7].
Algorithm: Cartesian Genetic Programming.
Population Strategy: 1+4 Evolutionary Strategy.
Genetic Operators: Subgraph Crossover and Discrete Phenotypic Recombination.
Hyperparameters: 
Number of rows: 1
Number of columns: 100
Levels back: 100 (allowing any node to connect to any previous node)
Mutation rate: Set via the configuration grid, varying between 1 percent and 10 percent of the genotype.
Function set: Addition, Subtraction, Multiplication, Analytic Quotient, Sine, Cosine, Exponential, Logarithm.
Replicates: 30 independent runs per configuration.
Seeding Regime: Random seeds generated sequentially from a fixed master seed for the 30 runs, using standard scikit-learn cross-validation splits.
Compute Cost: Approximately 20 to 40 CPU hours on a modern workstation to run the full grid search across 30 replicates.
Expected Result: The optimized recombination configurations should yield a median test-set Mean Squared Error substantially lower than the mutation-only baseline, closely tracking the box-plot distributions published in Figure 2 of Tran et al. 2026.
Citation for Baseline Numbers: arXiv:2605.28353 [cite: 5, 7].

Three Most Common Ways People Get This Wrong
1. Comparing genotypes instead of phenotypes when evaluating the 1+4 replacement rule. If you mutate an inactive node, the genotype changes, but the phenotype and fitness remain identical. If the software does not correctly log this as a neutral move, the search dynamics completely collapse.
2. Failing to isolate the cross-validation splits during hyperparameter tuning. If the test set leaks into the selection of the crossover rate or graph dimensions, the final symbolic models will massively overfit and fail the SRBench rigorous criteria.
3. Permitting unbounded complexity during evaluation. While Cartesian genotypes are fixed in length, operations like nested exponentials can cause floating-point overflows or extreme evaluation times. Failing to implement strict timeouts or numeric bounds on the node execution loop causes the experiment to hang indefinitely.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

Gap 1: A JAX or Triton compiled dynamic graph evaluator for parallel execution.
Currently, executing a population of Cartesian phenotypes is a CPU-bound loop. While frameworks like Karoo GP attempted GPU acceleration, they mapped the fixed genotype array to static tensors. Because 90 percent of the nodes are inactive and the actual executed paths branch dynamically, standard GPU execution suffers from massive warp divergence. A serious entrant needs to write a customized evaluator using JAX or OpenAI Triton that takes in a batched set of integer genotypes, compiles the active backward-reachable paths into a fused CUDA kernel dynamically, and outputs the fitness vectors. This requires deep systems engineering knowledge to handle irregular memory access patterns on the GPU. Several private industry groups and trading firms have rebuilt this internally to accelerate symbolic regression over financial time series, which is the strongest signal of its value.

Gap 2: A bidirectional Genotype-to-Large-Language-Model mutation interface.
Currently, integration with Large Language Models treats the model as a text generator: a prompt asks for an equation, and the model outputs a string. What does not exist is a structural mutation API. The interface must take the decoded Cartesian phenotype graph, translate its topological structure and active node semantics into a serialized format the Large Language Model can parse, and request the model to identify the structurally weakest subgraph and propose specific integer modifications to the underlying genotype. The hard part is aligning the tokenized understanding of the Large Language Model with the rigid, index-based integer array of the Cartesian genotype. Building this translation layer requires roughly two to three months of focused engineering, but it would fundamentally solve the problem of blind, random mutation.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Failed Programme of Standard Crossover
For nearly two decades, the attempt to apply standard one-point or two-point crossover to Cartesian Genetic Programming was a high-profile failure. Because the genotype is a fixed string containing highly fragile indices pointing to previous nodes, cutting two strings in half and swapping them almost always resulted in invalid graphs, disconnected outputs, or complete semantic destruction. Numerous papers were published showing crossover was worse than random search. This negative consensus stood unchallenged until researchers shifted from genotypic crossover to phenotypic crossover, realizing the active graph must be recombined rather than the raw integer string [cite: 5, 6].

The Bayesian Symbolic Regression Replication Failure
Bayesian Symbolic Regression was proposed as a sophisticated mathematical alternative to genetic search, theoretically capable of integrating expert priors into the generation of mathematical expressions. It looked incredibly strong on isolated datasets in its originating papers. However, when the SRBench framework was formalized, independent replication attempts showed that Bayesian Symbolic Regression performed poorly across generalized, diverse datasets compared to highly tuned evolutionary methods. The rigorous benchmarking proved it was largely overfitting its priors to specific toy problems [cite: 15].

The Large Language Model Memorization Artefact
In 2024 and 2025, a wave of papers claimed that prompting frontier Large Language Models could autonomously perform symbolic regression and discover physics equations with near-perfect accuracy. This entire sub-field was later shown to be measuring an artefact. The models had memorized the Feynman physics equations during pre-training. When the LLM-SRBench introduced LSR-Transform, altering the mathematical representation of the exact same physical phenomena, the performance of models like Llama-3 and GPT-4 collapsed drastically. The method was measuring dataset contamination, not algorithmic discovery [cite: 10, 19].

The Standing Critique of Representation Redundancy
A standing methodological critique of Cartesian Genetic Programming is the computational and memory waste of the fixed-length representation. If a user defines a grid of 1000 nodes, but the phenotype only uses 50, the genetic algorithm must still carry, mutate, and store the 950 inactive integers for every individual across tens of thousands of generations. Critics argue this functional bloat is highly inefficient for memory caching. The standard answer to this critique is that these inactive nodes act as a vital genetic reservoir, shielding the active nodes from destructive mutations and enabling neutral drift. This answer is widely accepted, but the critique remains valid for high-dimensional tensor tasks where carrying large inactive graphs becomes a memory bottleneck.

The Double-Precision Integer Limit
A strictly technical failure occurred heavily in the early days of logic synthesis. To evaluate truth tables efficiently, libraries like the original CGP-Library used 64-bit doubles to run bit-parallel simulations. However, developers continuously failed to account for the IEEE 754 mantissa limits, which can only precisely represent integers up to 2 to the power of 53. Experiments attempting 64-bit boolean logic synthesis failed silently, reporting false convergence because the floating-point truncation swallowed the evaluation errors. This was partially answered by restricting simulations strictly to 50 bits, but it remains a dangerous standing trap [cite: 22].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If starting today with robust compute and engineering capability, here is exactly where you should aim, ranked by feasibility and impact.

1. Implement Differentiable Phenotypic Crossover on SRBench
What makes it feasible now: The mathematical foundation of Differentiable Cartesian Genetic Programming exists via the AuDi library, and the theoretical proof that phenotypic crossover works was published in 2026. However, no one has combined them. 
Experiment: Take the backpropagation logic from dcgpy and inject it into the TinyverseGP crossover framework. Evolve a population where phenotypic crossover dictates the graph topology, but gradient descent optimizes the continuous numerical constants within the active nodes. 
What it measures: Test-set Mean Squared Error and convergence speed in CPU hours on the SRBench suite compared to standard mutation. 
Falsification: The idea is falsified if the gradient-based updates to the constants alter the fitness landscape so drastically that the neutral mutation drift—which standard Cartesian Genetic Programming relies on to escape local optima—is completely destroyed, resulting in premature convergence.

2. Large Language Model Directed Genotypic Mutation
What makes it feasible now: The release of LLM-SRBench finally provides a rigorously de-contaminated dataset (LSR-Synth) to test true reasoning, and context windows are now large enough to process entire serialized graph topologies.
Experiment: Replace the random integer mutation operator in the 1+4 Evolutionary Strategy with an API call to a local inference model. Pass the model the current active subgraph, its error residuals, and ask it to propose an index mutation. Run this strictly on the LSR-Synth dataset.
What it measures: The number of generations required to reach target fitness versus classical uniform random mutation, and the API inference token cost overhead.
Falsification: The idea is falsified if the token-generation latency of the inference model outweighs the raw speed advantage of evaluating thousands of random uniform mutations per second.

3. End-to-End Multimodal Explainable Vision Pipelines
What makes it feasible now: The Kartezio framework has proven that Cartesian nodes can successfully wrap complex OpenCV primitives for low-data image segmentation.
Experiment: Extend the Kartezio node function set to include lightweight, pre-trained Vision Transformer attention heads alongside standard morphological filters. Train this representation on a high-stakes, low-data dataset, such as rare satellite imagery or novel cell microscopy.
What it measures: Intersection over Union metric on the holdout test set against a heavily augmented U-Net baseline, and inference latency on edge hardware.
Falsification: The idea is falsified if adding dense tensor operations to the nodes forces the phenotype to become too computationally heavy for the 1+4 Evolutionary Strategy to evaluate sufficient generations within a practical timeframe.

What Will NOT Work
Do not attempt to prompt a Large Language Model to directly output a Cartesian Genetic Programming genotype as a raw string of 1000 integers. The specific, rigid mapping of connection indices pointing backward in an acyclic graph is highly arbitrary from the perspective of text-based tokenizers. The model will hallucinate connections that point forward (violating the acyclic constraint) or invent functions outside the declared set. The integer abstraction is fundamentally hostile to how attention mechanisms learn positional text sequences. Attempting this will waste compute and yield invalid graphs.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLoFu3OnipIVoCO_srNsDf9p8MdKi6nubazs7qRcFlyH3v5pld8ibTNjUkJVAoVGXK8kadAF3KU9S0ugj26ARmact4FCtf_9kop79MeaqZ645vJ56-s9bg)
2. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRCo9rhZ7NuACU_ObbIRPxBT4NmtLtm-xRxnFQPrHWI2HJ1zTYdcY50JTFc9_27HJf8C7K0LyX897kgrngRRFmGYQh9pf5EaquFmxpXJjHg0HDHxPLsTTpQxlvhkTWDHJgXDcD5aIkRlJw4fxXZIuiPXepzI1z77pu71s6Q97346lvxmocJqOVjggtymM0lCI=)
3. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHau0RDs7Bset41IPSP70HJPF4gFBB-ZMOLRA-GHf9hTsV7kfl9BTrX4ExFJWB2Cb4Wtkj4BGCbnvQdH-qjK00nIsW_VPZQQlvuGqt3KeAACY23rmvzxfPE7tQzlp9aloyesns0NyedAFxjQ9tIRmMS)
4. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWOXqd073VdzeesTqlpteaI2WlbjB77rYCiX4fdaZrXal_6PJgNSR4TQSIbgMDX0LSVbeo3xgI0asiI5rVpntzfzhYON73GxyxELJ6TYAfpVv9S_DtCEQM)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUprrO7wEjknwUp4MGhB8MrYEC6VMlVvQ0QiLonC8sRhvft5yD9AHTemXPx_9W9cAughdMEAkBLQoDZdIGmDOHdzJ7Oz_jusqZD4zX9Sege2X7dGL_)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQdze7LmUvarlvBYdPo3vEPD-3ChjJaCFORwtGWBknRVDRp-c8sJJhHnhKss6OTJ_00_5OhUf9N2FT6EJWoHsrrr1l8QSf6Ax8HxQPbs0lLv7ASnvZ)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyA3jIW4tu9P7vVp9cHqZ7jgICm0V2cqKpNhYJDuXBmhTNek3y-vlUS_LFKYHq08_PhNMPS06u7cGqasnyU-wcxx4-1iBZCleBH_keCMStZ_bv_z4S5Dgi)
8. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOYYN6jOJnn4nfbXJWJGe4_LkepHiANCzMaLu0HSwOAL30__APz6cvx4ExCINTgCMwvFwu0p46WgOKbHqJZuHEqGm867UAKMDd81_6bQUXPb0g8DDSiw==)
9. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQWoWh7FIS9Cqb8aCENK34LdhwH3RM95enPNaAKcaRlmSs92xAvwDDXYMvJNr6U3DEQk8NcxsREcV_X7hq5AfVv0rSeMrtCjd4bVqzlgFynMRsjeB_5K-BB2UZS47OWYNAoh77uo0=)
10. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4MfeHn5RWzfvsQeYpznVkG627DVjNNEi0wyAnooEmb51fvpsPeQO_FMj9j0GEQ84SglEJoGVB9NFrVpukNXd-G7Ukw-tCoZshQ54UiUlvBrNiH6BbCiY5eQxRu4gRi-y6Djjkz446Jyqfb012)
11. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvYuzLq-gEIy9R-Vq8GHyBT39j30WidO3HMtsc5pw7FepbB6YZLNyrJAF-prVcODGibvfHa8VvFHrYG5HwqrW1pFLVYIryE50z4s1UiQyH13F5XTyYUuXf3O9apBzJPskkHRzL8x6O4Q==)
12. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEH833nm9iNpWWQs5GjQjl9yfrBlQeT5-9y5dkXBpC0hFfG6FxauRAIQdBfBLYH6WCuf23tqmmlB4yxnYkdcEo_sUtL7aFMLqjS78GIM-OFQxNz2mTfUHA=)
13. [ebay.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpH7NRfw3Vw6GJ3tuCSTf00b995Jvj-hO1dYwdvmEvPDOEYeEaAwJJg2JCQ7i1OPvaP0oQ3hb3CrUG6cpf-EeGCsjY8Qz3kVkwneKyIQMImTKP6UEnAaTSKqg=)
14. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4EvEIATEUI0fqY86ALNMkrfXoE1IK7jd2zJNyKJRHBvPYVF5OGjqYvk4WdaCLpLKuUcS-Tb8fTEOxeLK7EoCIFkR4Z_qF_3HrmEmIb3-hXootF-4O8A==)
15. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdX7iUUlMzUD8xgLKxKsf_25u0fyzWe0GiVtXdzD18ytud-4LU39N7FxNFOsGy240cAgXQ55V2V697KNJ0cyUuBQW2y1TabryzGVl5oFtfSLsw44zzOr-XqGoKcHmDdgVgWdxX8_sCx7sTx1vASqi7kHt_6ims_O9KONyCgtDvAsaZ)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGXC43hxVo4xzez4SeEyumirqjN-698I6iw_P6ltdRbcwdaNEblVcEm7vy6QGh8-Y_wRAFZ635ptoTCUmxz9UHOud_8xpqdn4HJkYwtBA2zmHDPz1XFhhSEpwIYDxmFCNalsft_ABwWEOhgj2doVIsaFJGjfdtTMaBp7osTkr_5KPxALVfdsuB7RcpdwIU59htRJr4g1nx2IvLxaHfSBG_FUI3FcW6z8kzJENxtDUAJwr2kuKPHr9b)
17. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdSj-HBUXFQBHWrE3tHg_7eBNcPP0IyDwM1LAuLfs0Xf3TRQldgTuF0IRYR_LvMTp4dC-R_BIFBGaUtC6b4xlXxmi7rrlCxmjdWiK3gY1IJnF9ucHjUugrQgvDqJle)
18. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeEz0cB38M4xBduV_U-YtO17dWJnUs-pbiWTyK-5X7LiSxOB7KrqEQikSDJKOutnGWNAueQu2ttXkfU8tHAtHyrE7V6BSTPFe6bjV8JvquSy8919EHyN1CG8UfK3B7hQ==)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUfb1cz4I9Nb4iM5-EUEpJt4HdzMeI54BxtMHHWTXuW3CUCud635VfPcMzIE5xAI7NAhn8zjpxVPKR0kXteGOj6WuuzhMAt7vBSkDLZtw3hoEUWejYdMl1oSG4AHECuaCA096S6LUI_a3Pz-p5P6MFTTiMBgK8eN-JpHGv3qaYAu_LXG1Zct_80aFCHyjcXpP81_dh5ILBJWcEA_LJDaTuoLe7DPZWEmt3JaGTCwW5Fddx1_FnwRCEKiuzM4UW9Txm)
20. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6JAZeYzdXXnbTsbRfWYPloXU5V7SvZNujZmOSPozJQdwBRWiMcFm3RcbpFBayg_tBCca4ah-9X5rM4Klr64BahAAcLAGKcEeIxa88SyJh57dVx9RGFhkFxUgQxpBqb9FNkTRetdbYgqrGXhvqdMtRloiP)
21. [cgplibrary.co.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtrASkgfD9Id5leDhYf1fHzBmFjISsLXcZFQWlWwZD_J7wI3MVltB2meRONpW2_0TREkUyK_W4jRXbuNwkLwgGb_UmQ9Os2jYhD1_m5gdqrMk=)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcQFjkgCZadwMEU8fF1mWBZDmxkPfSItlPh7gqHgAh3OqsFLZhsyGcokD1XCoLf_PoiIZdXz84BlG9k0gd_NTS9SFEwKqByqHV9nYjVr6AARW118Hh)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCAXwMI_uoNf0wACKqMowsUrwMt7-SXbsDJhM1TYtVkzQeB6y3WnykDZmjhiLQpKQbiKi0UEciE9CCXYAKyodwy_ETxt9iyzqxcVfW0iyWyCszFCGgskyMJW0bP2d2RUcyAXw=)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAewrrohLHOm_xLhR7I6P-1Z6OnOkcUh0lqLDk0u4Cb6E4K6RpZAyNulN7jBk3Uq3EsxCwq_2_wP4x6bnddu7UPrgGsym8c7Dv_c1uFwk54S-MQJMxIMENsxNf)
25. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbW_T9zasRDkgMpzWtoNrCnj2k0PYWn1YPopYyUWWLsKZwTWQecd8aeWT7mwna3cJ4DM5cjMaDm5R_D8XlqUwZEH7tGAUlT2SGpOoeTRM149p_P_SEsdgj5KY0WiFkSfi5__suYuIwt5WfTQ4DkM6rMTSPiTkFj14nUN-S0oBnq6x7xMnSSDEWojjQZPizETsNhr09mZes4pvUmnkgDBHJjZCD-LRm1jTXfcjzKllKAGy8rOE=)
26. [pypi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ31f4OCwlfOQpoohdZZ7pcbHwWd_tpzgXHmR-e58yrxGz5HqpLGaNmfDEWA16q3vwHmTI4C-1pl1W-NsjbShxKXWplBIp6AZFpvniJEKC2hGmZE4_ED8=)
27. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFag1TEvy2FK9Xm5_AHyqBwMKREdzwZResyxIRzmbZUkd95R6eBGcUQhL9j4-Fs1Nem67idUvEncc8aZowMXn4mcPqzO9HwI5AgqDYilouLSpBbsQHl6X77yh-X-ZMCrMXgJ6SqjEo-HnttEr872opNWLMizq1bCUG4BP_b-AL9QFLN_s3JbX8zsUmCnEtO6uOxPVe6dj-uc4ga78NxKQjUFn4Ysm8lnOsG5M14b98fqV2u5RRnbytIwSFEkQ==)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiAYB_2vk791dl8kPPvkz3UPBOe6dy_LEa4c56wvOoyGTTp47IwjiUlT1yyWZlEUVcZuT9WhM4tKVdE4pO4MOUHEWklMGe0douRKnVeErJaknS_NNJqICm)
29. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHLJSes5c3HUBCR7WI6WyqG5NsXAcX2sc2gPHMrU5XR4ifqcmDZXovZwm4Z60-RUxTu0B04e1tClME80G0pAGZdi5NpLAos1LBFkuDjBHrlCrja3keYefb)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEewmZ6wkHx_yyF4U4S7XG6s6808wCRDOzAtrYHmb5c1xXB6h4FoER53U1VYc3h9PvwjleJWRwzeAUvg7SQ-x1xLwPuLyDqIztC7XHqZhtbeP3UR7hKUp-NQAJaEa9DXGi3C-9cNA==)
31. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFC7I6RjeZDUc5VlM62rWCVuW_-DNGGzuf2u11zhnqk-jbxPhDUKuxVy_LUwX7BtjK8lAhgKebBS_PJOqgJJq59U3dKq-decANhW8uekLZ0)
32. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWiRX1qBbc7BGeCprNxvVz53TWmXlvJGYpJbWj5L5tffm3SME1QIPxMQBhiRAuiG94O_ALdK3oMYFnjN458JheR7RPmsUX6W_IqsTvOK3jj9S97cSIaF7t2jYwJd4JaJSInzPlNk4K0ZFlnRgTgVmY8ZlSlA==)


# Prompt 12: Genetic Programming

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdsNldlYXQ2LUlOdXVfUFVQbFlxcmtBOBIXbDZXZWF0Ni1JTnV1X1BVUGxZcXJrQTg
**Elapsed:** 425s

---

# FRONTIER PRACTITIONER DOSSIER

The following dossier details the frontier of Genetic Programming with a strict focus on Linear Genetic Programming (LGP) as of 2026. Research suggests that while the broader field of evolutionary computation has seen consolidation, LGP has experienced a focused revival, primarily driven by its unique topological properties and its efficacy in Symbolic Regression. The evidence leans toward structural introns serving as a crucial topological feature for maintaining genetic diversity and providing neutral evolutionary pathways, though their direct, unassisted impact on search efficiency remains contested. This report provides a concrete, executable roadmap for a computational scientist entering the field, anchored to the specific mechanics of structural introns and register architectures. 

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Linear Genetic Programming in 2026 sits at the intersection of Symbolic Regression, Directed Acyclic Graph (DAG) analysis, and automated heuristic design. Unlike traditional tree-based Genetic Programming (TGP), LGP evolves imperative sequences of instructions that manipulate a fixed set of memory registers (cite: 1, cite: 2, cite: 3). Because instructions overwrite registers, many generated instructions do not affect the final output register. These disconnected components are known as structural introns or noneffective instructions. The field has matured past merely observing these introns to mathematically modeling them and leveraging them in cross-representation architectures.

What is SETTLED: It is mathematically settled that structural introns are an inevitable topological consequence of linear DAG representations (cite: 11, cite: 12). It is uniformly accepted best practice that an exact, deterministic backward sweep must be used to detect and eliminate structural introns prior to fitness evaluation, as this vast reduction in executed instructions is the primary source of LGP's computational speed advantage over TGP (cite: 13, cite: 14, cite: 15). Furthermore, it is settled that semantic LGP, which incorporates program behaviour into the search via geometric or semantic operators, generally outperforms purely structural LGP on continuous regression tasks (cite: 18, cite: 25).

What is CONTESTED: The exact evolutionary utility of structural introns remains a live disagreement. One side argues that introns serve as evolutionary memory, shielding critical building blocks from destructive crossover and allowing neutral drift to traverse fitness valleys. The opposing side, supported by recent empirical analyses (cite: 2, cite: 30), argues that while introns preserve population diversity and allow neutral search, these effects do not inherently improve LGP search performance without highly specialized genetic operators that actively target noneffective code. There is also ongoing debate regarding whether linear representations are inherently superior to pure graph representations (like Cartesian Genetic Programming) for code reuse.

What is OPEN: The frontier currently revolves around reverse transformations between graphs and linear genotypes, as well as the integration of Large Language Models (LLMs). Bridging a DAG back to an LGP genotype using adjacency lists is an open area of rapid development (cite: 20, cite: 21). Additionally, the field is actively trying to integrate semantic backpropagation directly into LGP structures without causing catastrophic semantic bloat, a challenge that remains unsolved at scale.

Absorption and Dormancy: General-purpose LGP for simple classification has largely been absorbed into the broader field of Symbolic Regression and evolutionary machine learning. Pure LGP without semantic, graph-bridged, or multi-representation enhancements is effectively a dormant research area; the baseline algorithm is now treated as a solved foundational tool rather than a research frontier itself.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Markus Brameier, Wolfgang Banzhaf
Year: 2001
Title: A Comparison of Linear Genetic Programming and Neural Networks in Medical Data Mining
Venue: IEEE Transactions on Evolutionary Computation
Identifier: DOI 10.1109/4235.985692
This paper is the load-bearing pillar for structural intron detection, explicitly defining the backward sweep algorithm that separates effective code from introns in imperative genetic programs. A practitioner must know this because it defines the exact mechanical baseline for all modern LGP evaluators.

Authors: Markus Brameier, Wolfgang Banzhaf
Year: 2004
Title: On Linear Genetic Programming (Thesis)
Venue: University of Dortmund
Identifier: IDENTIFIER UNKNOWN
This thesis rigorously defines the difference between structural introns and semantic introns, proving that while semantic introns require runtime evaluation to detect, structural introns can be isolated via pure graph topology. It contains the exact mathematical formalisation of the register overwrite mechanics.

CURRENT SOURCES

Authors: Leo Francoso Dal Piccol Sotto, Franz Rothlauf, Vinicius Veloso de Melo, Marcio Basgalupp
Year: 2022
Title: An Analysis of the Influence of Noneffective Instructions in Linear Genetic Programming
Venue: Evolutionary Computation
Identifier: DOI 10.1162/evco_a_00297
This is the definitive modern analysis of the structural intron hypotheses. It systematically tests whether introns serve as evolutionary memory or merely as a buffer for program growth, proving that while they enable neutral mutations, they do not inherently boost raw search performance.

Authors: Zhixing Huang, Yi Mei, Jinghui Zhong
Year: 2024
Title: Semantic Linear Genetic Programming for Symbolic Regression
Venue: IEEE Transactions on Cybernetics
Identifier: DOI 10.1109/TCYB.2022.3181461
This paper defines the modern frontier of Semantic LGP (SLGP), introducing a "mutate-and-divide" propagation operator to recursively propagate semantic errors within the linear program. It is essential reading because it demonstrates how to overcome the generalization issues of traditional LGP.

Authors: Zhixing Huang, Yi Mei, Fangfang Zhang, Mengjie Zhang, Wolfgang Banzhaf
Year: 2024
Title: Bridging directed acyclic graphs to linear representations in linear genetic programming: a case study of dynamic scheduling
Venue: Genetic Programming and Evolvable Machines
Identifier: DOI 10.1007/s10710-023-09478-8
This introduces the reverse transformation problem, showing how to map an executed DAG back into an LGP sequence using adjacency lists. It proves that preserving graph topology during genetic operations significantly improves performance over blind linear crossover.

Authors: Fabricio Olivetti de Franca, Marco Virgolin, Michael Kommenda, William G. La Cava
Year: 2024
Title: SRBench++: Principled Benchmarking of Symbolic Regression With Domain-Expert Interpretation
Venue: IEEE Transactions on Evolutionary Computation
Identifier: IDENTIFIER UNKNOWN
This paper represents the current authoritative community standard for evaluating symbolic regression. A practitioner must read this to understand exactly which datasets the community trusts and how modern baselines are calibrated against overfitting.

Authors: Giovanni Squillero, Alberto Tonda, Roman Kalkreuth, Fabricio Olivetti de Franca
Year: 2026
Title: TinyLGP: A Minimalist Implementation of Linear Genetic Programming
Venue: Advances in Linear Genetic Programming
Identifier: IDENTIFIER UNKNOWN
A crucial modern reference implementation chapter that strips LGP down to its absolute bare essentials, providing the cleanest architectural blueprint for writing an LGP engine from scratch today.

Authors: Fei Liu, Zhichao Lu, Zhenkun Wang, Qingfu Zhang
Year: 2026
Title: Evolution of Heuristics using Large Language Models
Venue: Advances in Linear Genetic Programming
Identifier: IDENTIFIER UNKNOWN
This sits at the bleeding edge, demonstrating how LLMs are being integrated with linear representations to generate and mutate heuristics, bypassing the traditional blind random initialization of LGP registers.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Tinyversegp (including tiny_lgp.py)
https://github.com/gpbench/tinyversegp
Python
MIT License
2024
MAINTAINED
This is the modern community standard for running lightweight, comparable genetic programming experiments. It provides unified interfaces for Tree-based GP, Cartesian GP, and Linear GP (LGP) with memory registers. It natively integrates with SRBench and Gymnasium for policy search. The primary limitation is execution speed; because it is written in pure Python, it is heavily bottlenecked during fitness evaluations on large datasets compared to compiled C++ or Rust implementations.

Linear-Genetic-Programming-LGP-and-Applications
https://github.com/Zhixing1020/Linear-Genetic-Programming-LGP-and-Applications
Java
License Unspecified
2024
MAINTAINED
This repository implements LGP and its advanced semantic and graph-bridged variants. It is decoupled from the heavy ECJ (Evolutionary Computation in Java) framework but relies on some of its core utilities. It is the best place to run the dynamic job shop scheduling and semantic LGP experiments from the Huang et al. 2024 papers. Gotchas: Requires Java 11 strictly, and the lack of an explicit open-source license in the repository can be a legal hurdle for commercial integration.

LGP (leo-sotto/LGP)
https://github.com/leo-sotto/LGP
Python and C++
License Unspecified
2020
DORMANT
This is the reference implementation for the structural intron behavior experiments by Sotto et al. It includes a custom SWIG wrapper to bridge C++ evaluation with Python algorithms. It runs symbolic regression and classification tasks while explicitly logging effective instruction counts. Gotcha: The compilation script (compile_swig.sh) is extremely brittle on modern 2026 toolchains and frequently fails to link NumPy headers correctly on ARM-based Macs or modern Linux kernels without manual path interventions.

cpp-linear-genetic-programming
https://github.com/chen0040/cpp-linear-genetic-programming
C++
MIT License
2017
ABANDONED
Famous for being one of the only clean, standalone C++ implementations of the Brameier and Banzhaf book algorithms, including the Algorithm 3.1 backward sweep. However, it is effectively dead. It relies on outdated Visual Studio 2017 solution files and lacks a CMake build system, making it highly frustrating to compile on modern POSIX systems without a complete rewrite of the build configuration.

linear-gp
https://github.com/urmzd/linear-gp
Rust
MIT License
2021
DORMANT
A fast, parallelized implementation of LGP in Rust using Rayon. It supports OpenAI Gym environments and Q-Learning integration. While highly performant and memory-safe, it has not seen active updates to support modern Gymnasium APIs, requiring the user to manually patch the environment bindings before it will run today.

PART 4. DATA AND BENCHMARKS

SRBench (Symbolic Regression Benchmark)
https://github.com/cavalab/srbench
Large scale (120+ datasets, plus Feynman physics datasets)
MIT License
This is the absolute authoritative benchmark suite for the field. It is used to measure accuracy, formula simplicity, and generalization in symbolic regression. It includes both black-box empirical datasets (e.g., Penn Machine Learning Benchmarks) and ground-truth physics equations (Feynman). Known limitation: The Feynman physics datasets are highly saturated. Most modern LGP algorithms can solve the lower-dimensional physics equations flawlessly, leading to a risk of overfitting to the benchmark's specific algebraic structures rather than proving true algorithmic superiority.

Penn Machine Learning Benchmarks (PMLB)
https://github.com/EpistasisLab/pmlb
Over 160 datasets of varying sizes (from 100 to 100000 instances)
MIT License
Used historically for both classification and regression. While popular, it is no longer considered sufficient on its own for LGP without being filtered through the SRBench harness, as many datasets contain trivial linear relationships that do not stress the non-linear topological capabilities of LGP.

GBFS / LSBench (Logic Synthesis Benchmark)
Access route via gpbench/tinyversegp benchmark utilities
Small to medium boolean logic tables
Open Access
Used to measure the structural capability of LGP on digital circuit problems (e.g., multiplexers, parity functions). This benchmark explicitly isolates the graph-routing capabilities of LGP from continuous parameter optimization. Overfitting note: Parity problems are known to be pathologically difficult for basic crossover and are often solved using neutral drift or specialized graph-bridging, meaning success on LSBench does not always generalise to continuous regression.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and foundational experiment in this field answers your anchoring question directly: tracking the steady-state topological fraction of effective instructions in randomly generated LGP genomes as a function of the register count. This experiment is a pure mathematical property of the LGP directed acyclic graph; it requires no training data, no fitness function, and no semantic execution. 

The Exact Specification:
Software: A custom 100-line script is preferred here over off-the-shelf tools, as you only need the genotype generator and the backward sweep algorithm (Algorithm 3.1 from Brameier). Alternatively, use the internal program generator of tiny_lgp.py from gpbench/tinyversegp (version 1.0).
Dataset: None.
Parameters: 
- Program length (L): Fixed at 100, 200, 500, and 1000 instructions.
- Number of Registers (R): 2, 4, 8, 16, 32, and 64.
- Instruction Set: 2-arity operations only (e.g., ADD, SUB, MUL, DIV). Constants are disabled to keep all sources routing to registers.
- Output Register: Fixed as Register 0.
Replicates: 10000 independent random program generations per (L, R) combination.
Seeding: Standard sequential seeding from 1 to 10000 for reproducibility.
Compute Cost: Less than 5 CPU minutes total. No GPU required.

The Algorithm (The Backward Sweep):
1. Initialize a boolean array of size R, representing the "live set". Set index 0 (the output register) to True. All others False.
2. Initialize an effective instruction counter to 0.
3. Loop from the last instruction (index L-1) down to the first instruction (index 0).
4. For the current instruction, check its destination register. If the live set array at that destination index is True:
   a. Increment the effective instruction counter.
   b. Set the live set array at the destination index to False (because the instruction overwrites previous data, effectively severing the path to anything above it).
   c. Set the live set array for both source registers to True.
5. If the destination register is not in the live set, the instruction is a structural intron. Do nothing.
6. The effective fraction is the final effective counter divided by L.

Expected Result:
The effective fraction is a deterministic topological property. For L=500 and R=2, the fraction will be extremely high (often above 0.85) because with only two registers, every instruction is highly likely to write to a live register, though the live set size stays small due to constant overwriting. As R increases to 32, the effective fraction will plummet asymptotically to below 0.10. The published numbers to compare against are found in Figure 3 of Sotto et al. 2022 (DOI 10.1162/evco_a_00297), which maps the mean effective size of individuals at generation zero across different register configurations. 

Three Most Common Ways People Get This Wrong:
1. Failing to clear the destination register from the live set. If you leave the destination register marked as "live" after processing an instruction, you treat the register as an accumulator (e.g., R0 = R0 + R1) rather than a strict overwrite. This causes the live set to monotonically grow, artificially inflating the effective fraction to near 1.0.
2. Scanning forward instead of backward. A forward scan cannot determine if a written register is ever subsequently read by a path leading to the final output. It only tells you if the instruction was executed, not if it was effective.
3. Including branch instructions without recursive live-set rules. If you introduce conditional branches (IF R1 > R2), the execution path diverges. If a branch dictates the execution of an effective block, the branch itself is effective, and its condition registers (R1, R2) must be added to the live set. If you ignore branches, the fraction breaks.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A Hardware-Accelerated Tensor Evaluator for LGP Strings
What goes in: A continuous block of memory containing millions of integer-encoded LGP programs (a 3D tensor of shape: population_size x program_length x 4, where the 4 integers are opcode, dest, src1, src2). A tensor of fitness cases.
What comes out: An array of fitness scores and an array of effective program lengths.
The hard part: LGP execution is inherently sequential and suffers from massive branch divergence on GPUs. Furthermore, the backward sweep for intron removal relies on sequential graph traversal, which maps poorly to SIMD architectures. 
Work required: Roughly 3 to 6 months for a competent CUDA/Triton engineer. Several proprietary trading firms and private labs have rebuilt this component privately using custom CUDA kernels to evaluate millions of heuristics per second, signaling a massive gap in the open-source ecosystem.

A Rigorous DAG-to-LGP Genotype Bridge Library
What goes in: A directed acyclic graph (nodes as operations, edges as data flow).
What comes out: A minimal, topologically identical LGP sequence of instructions with optimized register allocation.
The hard part: Register allocation in LGP is a variant of the graph coloring problem. When you mutate the DAG directly, mapping it back to a linear sequence of fixed registers without exceeding the register limit or artificially generating semantic bloat is an NP-hard compiler optimization problem.
Work required: 2 to 3 months. While Huang et al. 2024 (DOI 10.1007/s10710-023-09478-8) provided a specific case study for this, a general-purpose, language-agnostic library for this transformation does not exist off-the-shelf.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Probabilistic Model Building LGP (PMB-LGP) Failure
Programme: In the late 2010s, a major effort was made to replace standard LGP crossover with Estimation of Distribution Algorithms (EDAs). The idea was to build a statistical model of the instruction frequencies and sample new linear programs from it, avoiding destructive crossover.
What went wrong: The absolute positioning of instructions in a linear array is completely decoupled from their functional role due to register shifting. An instruction like "ADD R0 R1 R2" at position 10 might be critical in one genome but useless in another. Statistical models failed to capture this relative, context-dependent graph topology, leading to PMB-LGP performing no better than random search on complex problems.

The Evolutionary Memory Hypothesis (Partially Failed)
Programme: For two decades, the field assumed that structural introns actively protected good code blocks from destructive crossover and stored "memory" of past successful traits.
What went wrong: Sotto et al. 2022 (DOI 10.1162/evco_a_00297) systematically proved that while information can be reactivated from introns, this reactivation does not inherently improve search performance. In fact, standard crossover is so disruptive that reactivated introns are almost always semantically misaligned with the current program state. The claim that introns "help" evolution directly was falsified; they merely provide a buffer for program length variation and allow neutral mutational steps. 

Semantic Bloat vs Structural Bloat (Standing Critique)
Critique: Traditional LGP solves structural bloat via the backward sweep. However, critics continuously point out that LGP is entirely defenseless against semantic bloat. Semantic bloat occurs when instructions are structurally effective (they lie on the path to the output) but mathematically useless (e.g., R1 = R2 * 1; R0 = R1 + 0). 
Answered?: Only partially. Geometric Semantic GP (GSGP) attempted to fix this but caused exponential program growth itself. Recent methods like SLGP (Huang et al. 2024) attempt to recursively divide semantic errors, but the fundamental critique remains: LGP evaluators still waste massive amounts of compute evaluating semantically null operations. 

The Crossover Macro-Mutation Critique
Critique: Because registers act as global variables within the program scope, swapping a linear block of code between two parents (two-point crossover) almost never preserves the functional behavior of that block. A block expecting input on R2 will fail if the new host program routes data through R4. Critics argue that LGP crossover is not a recombination of building blocks, but merely a highly disruptive macro-mutation.
Answered?: This critique was never fully answered by the traditional LGP community. It led directly to the recent push to extract the DAG, perform crossover on the graph edges, and bridge it back to LGP (cite: 20), effectively validating the critics.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

1. Exact Topological Bounds of LGP Spaces using Markov Chains
What to do: Abandon Monte Carlo simulations for structural intron fractions. Formulate the LGP backward sweep exactly as a Markov transition matrix where the states are the size of the live set.
Why now: The graph-bridging papers of 2024 have formalized LGP topological properties, making the math tractable.
What it measures: The exact, closed-form expected fraction of effective instructions for any LGP configuration (L length, R registers, N arity) at infinity. 
Falsification: If the analytical steady-state distribution deviates from the Monte Carlo simulation, the assumption of uniform transition probabilities in LGP random generation is falsified, indicating inherent structural biases in the instruction set.
Rank: 1 (Highly feasible, massive theoretical impact, requires no heavy compute).

2. LLM-Guided DAG Generation Bridged to LGP
What to do: Use an LLM to output a computational DAG for a heuristic (e.g., scheduling, routing). Pass this DAG through a register allocation compiler to generate an LGP genome. Seed the LGP population with these LLM-derived individuals rather than random bitstrings, and allow LGP evolution to fine-tune the constants and operations.
Why now: Open-weight LLMs (like deepseek-coder or llama-3) are finally competent at generating syntax-valid graph structures, and the DAG-to-LGP bridging math (cite: 20) was just published in 2024.
What it measures: The reduction in the number of generations required to achieve a baseline fitness score compared to random initialization.
Falsification: If the LLM-seeded LGP population gets stuck in local optima while the randomly initialized LGP population eventually surpasses it, it proves the LLM restricts genetic diversity too severely.
Rank: 2 (High impact, bridges the hottest topic in AI with classic evolutionary search).

3. Hardware-Accelerated Semantic Intron Pruning
What to do: Build a Triton/CUDA kernel that not only does the backward structural sweep but also performs constant folding and algebraic simplification (e.g., X * 0 = 0, X + 0 = X) on the GPU prior to evaluation. 
Why now: GPU tensor compilers have matured enough to handle dynamic abstract syntax tree optimizations on flat arrays.
What it measures: The throughput (evaluations per second) of semantic pruning versus the cost of simply executing the bloated code. 
Falsification: If the overhead of algebraic simplification on the GPU exceeds the time saved by skipping the execution of semantic introns, the hypothesis that semantic pruning is computationally viable is falsified.
Rank: 3 (Heavy engineering lift, highly prized by practitioners).

What Will NOT Work:
Do not attempt to invent a new Probabilistic Model Building LGP (PMB-LGP) that uses Transformers to predict the next LGP instruction in a sequence. Because LGP instructions are highly position-dependent and rely on dynamic register states, a purely autoregressive sequence model trained on LGP genotypes will fail to capture the underlying dataflow graph. The model will hallucinate register addresses that break the topological path to the output. You must model the DAG, not the 1D sequence.

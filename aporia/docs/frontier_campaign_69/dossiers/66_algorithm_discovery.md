# Prompt 66: Algorithm Discovery

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdHR2FmYXAyX0hlU05fUFVQc0lpcGtROBIXR0dhZmFwMl9IZVNOX1BVUHNJaXBrUTg
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: ALGORITHM DISCOVERY

Key Points:
*   The field of Algorithm Discovery has definitively transitioned from pure genetic programming to Large Language Model-guided evolutionary search.
*   The primary bottleneck for practitioners is no longer generating candidate algorithms, but rather constructing fast, secure, and distributed execution sandboxes to evaluate them.
*   Methodological integrity is currently contested; widespread benchmark contamination has cast doubt on whether AI models are discovering new algorithms or merely interpolating from their massive pre-training data.
*   The most promising frontier for a newcomer is targeting environments with zero pre-training representation, such as custom hardware scheduling or novel physical simulations.

Overview of the Paradigm Shift
The search for algorithms via computational evolution has fundamentally changed. Historically, methods relied on structural mutations of syntax trees or execution graphs. These approaches often collapsed under the sheer size of the combinatorial search space. Today, the field uses pre-trained language models as the mutation engine, providing massive structural priors that keep the evolutionary search anchored to viable code. This synthesis of evolutionary computation and deep learning has solved the search-space problem but introduced profound questions regarding evaluation and originality.

Practitioner Challenges
For a computational scientist entering this space, the literature obscures the engineering reality. Published papers emphasize the elegance of the models, but the tacit knowledge of the field is that infrastructure is everything. The ability to safely and cheaply execute millions of untrusted, mutated programs per hour is what separates successful labs from the rest. Furthermore, existing toolchains are highly fragmented, and reference implementations from major corporate labs are frequently released in a crippled, non-replicable state.

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Algorithm Discovery in 2026 is almost entirely defined by the merger of evolutionary algorithms with Large Language Models, a paradigm often termed LLM-Guided Evolutionary Search. Classical Genetic Programming, which mutated abstract syntax trees, bitstrings, or execution graphs, is effectively dormant. It has been absorbed into the LLM ecosystem. What was lost in this merge is true zero-bias discovery; modern systems rely heavily on the human code patterns embedded in their pre-training data. The specific method you anchored to, where a genome is interpreted as a graph of primitive operations with indexed memory (the PADO lineage), correctly describes the conceptual foundation of the field, but the "genome" is now almost exclusively executable Python or C++ code strings mutated by an LLM, rather than bespoke bitstrings.

What is SETTLED is that pairing an LLM with a programmatic evaluator and an evolutionary loop works. Systems like AlphaDev and FunSearch proved that this architecture can discover verifiably correct algorithms that exceed human baselines (cite: 2, 4, 35). It is settled that algorithms must be evaluated on their execution outputs, not their syntax, using cheap, exact oracles.

What is CONTESTED is the learning dynamics of the generator. The dominant faction (originating with DeepMind's FunSearch) treats the LLM as a static mutation operator that does not learn during the search (cite: 16). An opposing faction (e.g., the EPFL/Apple EvoTune group) argues this is massively inefficient and advocates for applying Reinforcement Learning to fine-tune the LLM continuously during the evolutionary loop (cite: 6, 52). Furthermore, there is a live disagreement regarding benchmark contamination. Critics argue that many "discoveries" on standard scientific benchmarks are artifacts of the LLMs having seen the target equations during pre-training (cite: 2, 39).

What is OPEN is the ability to discover algorithms in domains where exact, low-cost evaluators do not exist. Open-ended algorithm discovery without a rigid, mathematical fitness function remains unsolved.

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Teller, A., and Veloso, M.
1995
PADO: Learning tree structured algorithms for orchestration into an object recognition system
Technical Report CMU-CS-95-101
IDENTIFIER UNKNOWN
This establishes the specific anchor method you described: evolving arbitrary directed graphs of primitives with indexed memory that are interpreted and judged on outputs. A practitioner must know this to understand the origins of evaluator-in-the-loop program search and why raw genetic operations hit a scaling wall (cite: 12, 13, 63).

Miller, J. F., and Thomson, P.
2000
Cartesian Genetic Programming
European Conference on Genetic Programming
IDENTIFIER UNKNOWN
Introduces Cartesian Genetic Programming, where programs are represented as indexed graphs encoded by integer strings. It is essential for understanding how the field attempted to enforce structure on the genome before the advent of LLMs (cite: 11, 12).

CURRENT SOURCES

Romera-Paredes, B., et al.
2023
Mathematical discoveries from program search with large language models
Nature
DOI 10.1038/s41586-023-06924-6
The FunSearch paper. This is the absolute load-bearing pillar of the modern field, demonstrating that an LLM paired with an evolutionary loop can solve open mathematical problems (the cap set problem) by evolving the program that generates the solution (cite: 16, 31).

Mankowitz, D. J., et al.
2023
Faster sorting algorithms discovered using deep reinforcement learning
Nature
IDENTIFIER UNKNOWN
The AlphaDev paper. Essential for understanding how DeepMind formulated algorithm discovery as an Assembly Game played by AlphaZero, resulting in micro-optimizations that were upstreamed to LLVM (cite: 2, 4, 25).

Novikov, A., et al.
2025
AlphaEvolve: A coding agent for scientific and algorithmic discovery
arXiv:2506.13131
Describes DeepMind's successor to FunSearch, proving that this architecture can scale to evolving entire codebases, optimizing Google datacenter schedulers, and surpassing Strassen's matrix multiplication algorithm for 4x4 matrices (cite: 31, 33, 48).

Surina, A., et al.
2025
Algorithm Discovery With LLMs: Evolutionary Search Meets Reinforcement Learning
arXiv:2504.05108
The EvoTune paper. Defines the current frontier by answering the critique that static LLMs are inefficient. It proves that using RL to update the LLM during the evolutionary search drastically reduces the required sample complexity (cite: 6, 52, 56).

Wang, et al.
2026
Modular strategy-space layer for LLM-driven program search
arXiv:2604.24372
A critical advancement showing that maintaining a population-level state of natural-language reasoning strategies, rather than just executable programs, prevents the evolutionary search from saturating and confusing syntactically different implementations of the same idea (cite: 9).

Zheng, et al.
2025
Evo-MCTS: Automated Algorithmic Discovery for Scientific Computing through LLM-Guided Evolutionary Search
arXiv:2508.03661
Demonstrates how to integrate tree-structured evolutionary search with Monte Carlo Tree Search to respect domain-specific physical constraints, solving the problem of unconstrained LLM hallucinations in scientific computing (cite: 8).

Chan, J. S., et al.
2024
MLE-bench: Evaluating Machine Learning Agents on Machine Learning Engineering
arXiv:2410.07095
The authoritative benchmark paper from OpenAI measuring how well agents can actually perform ML engineering tasks, highlighting the severe limitations and costs of running these systems end-to-end on Kaggle-style problems (cite: 41, 59, 62).

La Cava, W., et al.
2021
Contemporary Symbolic Regression Methods and their Relative Performance
NeurIPS
IDENTIFIER UNKNOWN
The original SRBench paper. While older, it is the best comprehensive survey and benchmarking standard for symbolic regression, necessary for understanding how non-LLM search methods are rigorously compared (cite: 36, 38).

## PART 3. SOFTWARE I CAN ACTUALLY RUN

alphadev
https://github.com/google-deepmind/alphadev
Python, C++
Apache 2.0
2024
ABANDONED
This is the reference implementation for DeepMind's AlphaDev. It is effectively dead and was archived by the owners in August 2024. It contains only pseudocode for the agent and environment. You cannot run the published experiment with this repository; the actual execution environments and MCTS infrastructure are missing (cite: 21, 23, 24).

FunSearch
https://github.com/google-deepmind/funsearch
Python
Apache 2.0
2023
DORMANT
The reference implementation from the originating authors for FunSearch. It provides the problem specifications for the cap set and bin packing tasks, but it explicitly strips out the LLM integration, the distributed infrastructure, and the execution sandbox. It is entirely unbuildable for frontier experiments out of the box (cite: 16, 18, 68).

OpenFunsearch
https://github.com/Remmie0/OpenFunsearch
Python
IDENTIFIER UNKNOWN
2024
MAINTAINED
This is the community standard that most people actually use. It patches the massive holes in DeepMind's release by integrating open LLM support for Llama, Huggingface GGUF, and OpenAI APIs, alongside command-line execution and a Jupyter analysis harness. It can run the cap set experiment today. Its main limitation is that its sandboxing is rudimentary, making it dangerous to run on your host machine without strict containerization (cite: 20, 46, 57).

PySR
https://github.com/MilesCranmer/PySR
Python, Julia
Apache 2.0
2026
MAINTAINED
The state-of-the-art framework for symbolic regression. Version 2.0 transformed it into a highly modular framework where operators, crossover, and search loops are entirely configurable. It allows for the injection of "guesses" from agentic loops. It runs mathematical algorithm discovery reliably today, but relies on a Julia backend which can occasionally cause segfaults when clashing with Python machine learning libraries like PyTorch (cite: 26, 28, 29).

EvoTune
https://claire-labo.github.io/EvoTune/
Python
IDENTIFIER UNKNOWN
2025
MAINTAINED
The reference implementation for combining RL with evolutionary search. While newer, it provides the missing link that FunSearch lacks: updating the LLM weights based on evolutionary feedback. The primary gotcha is the immense computational overhead required to run RL fine-tuning alongside the evolutionary generation loop (cite: 6, 52).

## PART 4. DATA AND BENCHMARKS

SRBench and SRBench++
https://github.com/cavalab/srbench
Size: 252 datasets including PMLB and Feynman equations.
Licence: IDENTIFIER UNKNOWN
Used to measure the accuracy, complexity, and interpretability of symbolic regression algorithms. This is treated by the field as the authoritative benchmark. However, it suffers from severe contamination. The Feynman physics equations are deeply embedded in the pre-training data of all modern LLMs, meaning high scores often reflect memorization rather than algorithmic discovery (cite: 36, 37, 39).

LLM-SRBench
IDENTIFIER UNKNOWN
Size: 239 problems across four scientific domains.
Licence: IDENTIFIER UNKNOWN
Specifically built to counter the saturation of SRBench. It measures true symbolic accuracy by transforming common physical models into highly uncommon mathematical representations (LSR-Transform) to explicitly defeat LLM memorization. This is the modern benchmark a practitioner should target for mathematical discovery (cite: 39).

MLE-bench
https://github.com/openai/mle-bench
Size: 75 Kaggle competitions.
Licence: IDENTIFIER UNKNOWN
Used to measure end-to-end machine learning engineering by AI agents. It tests if an agent can write the code to train a model and format a valid submission. Known limitations include high variance (low replicability) and prohibitive cost, often taking over 1800 GPU hours for a single comprehensive evaluation pass. Furthermore, because Kaggle leaderboards are public, pre-training contamination remains a standing concern (cite: 41, 44, 61, 62).

## PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in this field is the discovery of the Cap Set construction for dimension n=8 using the FunSearch methodology.

Software and version: OpenFunsearch (https://github.com/Remmie0/OpenFunsearch), current main branch as of 2026.
Dataset/Generator: The Cap Set mathematical environment provided natively in the OpenFunsearch repository (adapted from DeepMind's original release). No external dataset is needed.
Parameters:
Model: OpenAI API using gpt-4o or o1-preview.
Temperature: 1.0 (requires high entropy for diversity).
Islands: 10 independent evolutionary islands.
Population size: 50 programs per island.
Tournament size: 2 for selecting parents.
Initial Skeleton: The basic priority function evaluating to a scalar, exactly as specified in the repository's cap_set domain configuration.
Seeding regime: 5 independent replicates, random seed integers 1 to 5 for the evolutionary loop, standard API seeding for the LLM.
Compute cost: Approximately 100 to 200 CPU hours for the evaluator loop, and roughly 300 to 500 US dollars in API token costs (or equivalent local GPU hours for a 70B parameter open model).
Expected result: The system will output a generated priority function that discovers an admissible cap set of size 512 for n=8.
Citation for comparison: Romera-Paredes et al., 2023 (cite: 31).

The three most common ways people get this experiment wrong:
1. Over-constraining the LLM prompt. Practitioners often try to force the LLM to output specific logical structures, which limits the evolutionary search space and prevents the emergence of the non-intuitive heuristics that actually solve the problem.
2. Inadequate sandboxing leading to pipeline collapse. LLMs frequently generate code with infinite loops or memory leaks. If the execution environment does not aggressively kill processes that exceed a strict microsecond timeout, the entire evolutionary loop will hang.
3. Collapsing diversity. If the island migration parameters are too aggressive, the entire population converges on a single local optimum, turning the search into a random walk around a dead end.

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A severe gap in the open-source ecosystem is the lack of a distributed, language-agnostic, low-latency execution sandbox explicitly designed for continuous LLM-driven evolutionary loops. DeepMind stripped this out of the FunSearch release, and every serious entrant must currently rebuild it.

Interface requirements:
Input: A massive batch (10000 to 100000) of untrusted source code strings (Python or C++) representing mutated genomes.
Output: A synchronized array of scalar fitness scores, boolean crash flags, and truncated execution traces.

The hard part:
Standard sandboxing tools like Docker or Podman introduce massive containerization overhead. When evaluating millions of tiny programs, a 500-millisecond container spin-up time makes the experiment computationally unviable. You cannot rely on OS-level virtualization.

Work estimate:
This requires writing a highly optimized, persistent process manager (likely in Rust or C++) that uses lightweight WebAssembly (Wasm) runtimes or strict seccomp-bpf filtering to execute dynamic code in isolated memory spaces with microsecond spin-up times. Several independent labs and quant funds have rebuilt this privately, signaling it is a major barrier to entry. Building a robust version will take an experienced systems engineer two to three months.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The PADO Scaling Failure: The foundational methods of arbitrary graph-based and tree-based genetic programming (the lineage of PADO and classic SR) failed to scale to complex software. Direct crossover and mutation on syntax graphs without semantic priors resulted in massively rugged fitness landscapes. The vast majority of generated programs were either uncompilable or trivial. This entire programmatic direction was abandoned by the frontier in favor of using LLMs to provide the structural syntax priors (cite: 11, 13).

The AlphaDev Micro-Optimization Critique: DeepMind's claim of discovering fundamentally new algorithms via AlphaZero (AlphaDev) was sharply critiqued. While AlphaDev found a faster 5-element sorting routine by omitting a single assembly instruction, critics demonstrated this was merely the micro-optimization of hot leaf routines, not the discovery of a new asymptotic complexity class. The latency gains drop from roughly 70 percent for tiny inputs to a marginal 1.7 percent for arrays above 250000 elements (cite: 2, 4, 25).

The Verifier Bottleneck: The entire field relies on the assumption that a cheap, exact oracle exists to verify the output of a generated algorithm. FunSearch works because verifying a matrix multiplication or a cap set is mathematically exact. Attempts to apply this paradigm to open-ended scientific discovery or general software engineering have largely failed because no such oracle exists. When the fitness function is fuzzy, the LLM-evolutionary loop rapidly games the metric, optimizing for an artifact of the benchmark rather than solving the phenomenon (cite: 2, 16).

Pre-training Contamination: This is the most severe standing critique of the field. Methods claiming to "discover" physical laws or standard algorithms are frequently shown to be regurgitating their pre-training data. The SRBench datasets (like the Feynman equations) are entirely saturated because LLMs have memorized the standard forms of these equations. The field has no agreed-upon method to prove that an LLM actually synthesized a novel algorithm rather than querying its weights for a heavily represented Github repository. This critique has never been fully answered by the major corporate labs, who refuse to disclose their training sets (cite: 2, 39, 41).

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

To run a frontier experiment as a well-resourced newcomer, avoid trying to beat DeepMind at pure mathematics. Instead, target domains where you can guarantee zero pre-training contamination and where evaluation is cheap but highly asymmetric.

Rank 1: Dynamic LLM-Evolution on Custom Hardware Architectures.
Build an experiment that attempts to discover routing heuristics or scheduling kernels for a novel, proprietary, or highly esoteric hardware architecture (e.g., analog AI accelerators or custom FPGA pipelines). This is feasible now because frameworks like EvoTune allow you to apply RL to the LLM during the search.
What it measures: Execution latency and power draw of the generated control algorithms against human-written baselines.
Falsification: If the LLM-guided loop cannot surpass random genetic mutation baselines in an environment completely absent from its pre-training data, it falsifies the claim that the LLM is doing genuine algorithmic reasoning, proving it is merely an interpolator of human code.

Rank 2: Persistent Strategy Evolution in Scientific Simulation.
Implement the modular strategy-space layer (from arXiv:2604.24372) on top of OpenFunsearch (cite: 9). Task it with discovering numerical integration algorithms for a highly specific fluid dynamics or plasma physics simulation. Maintain a population of explicit natural-language reasoning strategies rather than just tracking code fitness.
What it measures: The token-efficiency and sample-complexity of the search process.
Falsification: If clustering and explicitly prompting the LLM with previous failed strategies does not reduce the number of generations required to reach the target error threshold, it proves that language models cannot effectively utilize long-horizon evolutionary memory.

What will NOT work:
Attempting to discover new asymptotic bounds for classical computer science problems (like generalized matrix multiplication or graph algorithms) using API-based, off-the-shelf LLMs. The search space is too vast, and the number of required evaluations will bankrupt an independent researcher in API costs before yielding a result. Furthermore, these domains are deeply saturated; any easy wins have already been harvested by the originating authors using compute clusters you do not have access to.

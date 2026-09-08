# Prompt 51: Automated Conjecture Generation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdSVjZmYW9hT0dwMjBfUFVQM2U2TXdRSRIXUlY2ZmFvYU9HcDIwX1BVUDNlNk13UUk
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: Automated Conjecture Generation

Key Points:
* The field of automated conjecture generation has bifurcated into deterministic, invariant-based optimization methods and stochastic, LLM-guided evolutionary program synthesis.
* The foundational method of searching through a logic-based concept space using production rules has largely been superseded by searching through the space of executable code.
* While LLMs have produced verifiable mathematical novelties, standing critiques highlight that they function mostly as shallow mutation operators rather than systems with deep mathematical reasoning.
* The most significant engineering barrier for new entrants is not the machine learning model, but the secure, high-throughput execution sandbox required to evaluate proposed conjectures.

State of the Art:
Automated conjecture generation historically relied on heuristic search over defined logical production rules. Today, the frontier is defined by two complementary approaches. The first is the snapshot-table paradigm, where mathematical objects and their invariants are precomputed, and mixed-integer programming is used to derive tight mathematical bounds. The second is LLM-guided program synthesis, where an language model iteratively mutates a Python priority function within a genetic algorithm. 

Challenges and Opportunities:
The primary challenge is the evaluator bottleneck: LLMs will ruthlessly exploit poorly defined fitness functions, necessitating human expertise to carefully constrain the search space. The immediate opportunity lies in neurosymbolic integration—using LLMs to generate new feature-extraction code that expands the invariant tables used by deterministic optimization solvers.

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Automated conjecture generation in 2026 is a field fundamentally transformed by the integration of Large Language Models into evolutionary search loops, though it remains firmly anchored in empirical evaluation. The historical approach, exemplified by systems like HR, generated conjectures by applying symbolic production rules to known concepts and filtering the results through interestingness heuristics [cite: 1, 2]. Today, that paradigm has evolved into two distinct but parallel tracks. The first is the invariant-optimization track, which computes a "snapshot table" of mathematical objects and their properties, using mixed-integer programming to deterministically find bounds and inequalities [cite: 3, 4]. The second, much louder track is LLM-guided program search, which frames conjecture generation as a genetic algorithm where an LLM mutates a Python priority function, and a programmatic evaluator scores the resulting mathematical objects [cite: 5, 6].

What is SETTLED is that automated systems can discover novel, publishable mathematical bounds that exceed human constructions. It is also settled that representing combinatorial problems as executable Python code, rather than searching directly over mathematical structures or vectors, dramatically improves the scalability of the search [cite: 6, 7]. 

What is CONTESTED is the actual locus of intelligence in these systems. There is a live disagreement between AI optimists who view LLM-based systems as demonstrating deep mathematical creativity, and critics who argue the LLM acts merely as a stochastic mutation operator within a tightly constrained genetic algorithm [cite: 8]. The critics argue that the profound mathematical insight is entirely supplied by the human who writes the skeleton program and the evaluator function. 

What is OPEN is autonomous definition generation and fully unguided conjecturing. Current systems require a human to define the exact search space, the invariants to measure, and the evaluator to score them. If a problem cannot be cleanly formalized into a programmatic evaluator, current methods fail.

In the last three years, the field shifted drastically from searching over logic-based production rules to searching over executable code syntax. The traditional symbolic subfield has not been completely absorbed, but it has heavily integrated with neural reasoning, giving rise to "neurosymbolic" frameworks that use LLMs to interpret deterministic optimization results [cite: 9].

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Colton, S., Bundy, A., and Walsh, T.
2000
On the Notion of Interestingness in Automated Mathematical Discovery
AAAI
IDENTIFIER UNKNOWN
This paper formalizes the architecture of HR, detailing the specific production rules (exists, match, negate, etc.) and the empirical evaluation of concept extensions. A practitioner must know this to understand the logic-based baseline that modern code-evolution systems are attempting to replicate in higher-dimensional spaces.

Davila, R. R.
2024
Automated conjecturing in mathematics with TxGraffiti
Discover Artificial Intelligence
arXiv:2409.19379
This paper defines the modern "snapshot table" paradigm, showing how to replace logic-based production rules with mixed-integer programming over precomputed invariants. It is essential reading for understanding how to constrain automated conjecturing into a deterministic optimization problem.

CURRENT

Romera-Paredes, B., et al.
2023
Mathematical discoveries from program search with large language models
Nature
DOI 10.1038/s41586-023-06924-6
The foundational paper for FunSearch, demonstrating how pairing an LLM with an programmatic evaluator can discover novel cap set constructions. This defines the current frontier of treating conjecture generation as evolutionary program synthesis.

Davis, E.
2024
Using a large language model to generate program mutations for a genetic algorithm to search for solutions to combinatorial problems: Review of (Romera-Paredes et al., 2023)
Self-Published / arXiv
arXiv:2401.UNCONFIRMED
The definitive methodological critique of FunSearch, explaining how the LLM functions strictly as a subroutine in a genetic algorithm and operates with shallow mathematical understanding. A practitioner must read this to avoid being misled by the hype surrounding LLM-driven discovery.

Sivakumar, J. A., et al.
2025
Conjecturing: An Overlooked Step in Formal Mathematical Reasoning
arXiv
arXiv:2510.11986
This paper identifies that autoformalization of mathematics fails because LLMs cannot inherently generate the intermediate conjectures required to complete a formal proof. It introduces ConjectureBench and proves that conjecturing must be an explicit, independent architectural step.

Aalto, J., Nikoleit, H., et al.
2026
Human-AI Collaboration in Combinatorial Optimization: Worst-case instances and Lower Bounds
arXiv
arXiv:2601.16849
This paper applies the FunSearch paradigm to generate adversarial worst-case instances for bin packing and knapsack heuristics, improving lower bounds. It is crucial because it demonstrates how to use LLM-guided conjecturing to break existing algorithms rather than just build sets.

Feeney, S., et al.
2026
SCALAR: A Neurosymbolic Framework for Automated Conjecture and Reasoning in Quantum Circuit Analysis
arXiv
arXiv:2605.10327
Introduces an iterative neurosymbolic loop combining quantum simulation, TxGraffiti's symbolic generation, and LLM reasoning. It shows the frontier of hybridizing deterministic invariant tables with LLM-based interpretation.

Purcell, M., et al.
2025
Machine Learning meets Algebraic Combinatorics: A Suite of Datasets Capturing Research-level Conjecturing Ability in Pure Mathematics
arXiv
arXiv:2503.06366
Introduces the Algebraic Combinatorics Dataset Repository. It provides the most modern, mathematically rigorous benchmark for training models specifically on the conjecturing process rather than just proof formalization.

## PART 3. SOFTWARE I CAN ACTUALLY RUN

TxGraffiti2
https://github.com/RandyRDavila/TxGraffiti2
Python
MIT License
2025
MAINTAINED
This software computes mixed-integer programming bounds over tabular data to generate conjectures about mathematical invariants. It runs natively, features built-in datasets for graphs and integers, and exports to Lean 4, but its generated conjectures are heavily constrained by the linear templates it uses for optimization.

FunSearch (DeepMind Official)
https://github.com/google-deepmind/funsearch
Python
Apache License 2.0
2023
DORMANT
This is the reference implementation of the FunSearch algorithm containing the evolutionary loop and code manipulation routines. You cannot use it out of the box because it deliberately omits the LLM integration, the execution sandbox, and the distributed architecture required to actually run the experiment.

FunSearch (Lumi-a Fork)
https://github.com/lumi-a/funsearch
Python
Apache License 2.0
2026
MAINTAINED
This is the community standard reimplementation that most practitioners actually run. It wires the FunSearch evolutionary algorithm directly to modern LLM APIs and implements a local execution environment. The major gotcha is that the default sandbox runs generated Python directly on your system, which poses a severe security risk unless explicitly configured to use a containerized backend.

SCALAR
https://github.com/sfeeney1897/SCALAR
Python
UNCONFIRMED
2026
MAINTAINED
This neurosymbolic framework orchestrates CUDA-Q simulations, TxGraffiti, and LLMs to generate parameter bounds for quantum circuits. It allows you to reproduce conjectures about QAOA optimization landscapes, but it requires a specialized quantum simulation toolchain and is highly domain-specific.

## PART 4. DATA AND BENCHMARKS

Algebraic Combinatorics Dataset Repository (ACD Repo)
https://github.com/pnnl/ML4AlgComb
Up to 10000000 rows per dataset
UNCONFIRMED
This is treated as the authoritative 2025 benchmark for mathematically rigorous conjecture generation. It provides nine datasets mapping open problems in algebraic combinatorics, measuring whether a model can extract structural patterns from raw mathematical data to form verifiable conjectures.

ConjectureBench
https://github.com/huawei-noah/ConjectureBench
UNCONFIRMED
UNCONFIRMED
Used to measure the raw conjecturing capability of LLMs during the autoformalization process. It explicitly penalizes models that require the final solution to be provided in the prompt, exposing the contamination in older benchmarks where the conjecture was implicitly assumed.

FunSearch Cap Set and Admissible Set Archives
Access via the cap_set directory in https://github.com/google-deepmind/funsearch
Negligible size
CC BY 4.0
These are archived precomputed result tables containing the exact numeric representations of the largest cap sets discovered by FunSearch. They are used as baselines to verify that a reimplementation is actually reaching the published capacity bounds.

MQLib Filtered MaxCut Instances
Access via the data directory in https://github.com/sfeeney1897/SCALAR
82 instances
UNCONFIRMED
A task collection used to measure the relationship between graph topology and optimal quantum circuit parameters. It is highly specific to the quantum algorithm design subfield.

## PART 5. THE REPRODUCTION RECIPE

The most reproducible and informative experiment is the independent replication of the FunSearch Cap Set capacity discovery for dimension 8. 

Exact software and version: 
The Lumi-a fork of FunSearch from https://github.com/lumi-a/funsearch, running the latest 2026 commit via the uv package manager.

Exact dataset or generator: 
The cap_set.py skeleton program provided in the specs directory, which defines the greedy solver and the evaluate function that computes the size of the cap set.

Parameters to set:
Model: gpt-4o or gemini-1.5-pro.
Temperature: 0.7.
Number of Islands (population groups): 3.
Population size per island: 25.
Batch size for LLM querying: 4.

Seeding regime and replicates:
Run 5 independent replicates. Seed the program database with the trivial priority function provided in the default DeepMind skeleton. 

Approximate compute cost:
Roughly 5 to 10 USD in API costs per replicate, and 1 to 3 CPU hours for the local evaluator execution, as evaluating the cap set size is computationally lightweight compared to the LLM inference.

Expected result:
The system should output a Python function that, when executed, constructs a cap set of size 512 in dimension 8. This matches the published finding from Romera-Paredes et al. 2023.

Three most common ways people get this experiment wrong:
1. Running the evaluator locally without a secure sandbox. The LLM will occasionally generate syntax errors, infinite loops, or malicious OS calls. Failing to isolate the execution crashes the worker node.
2. Using too low an LLM generation temperature. Setting the temperature to 0.1 causes the genetic diversity of the program islands to collapse, and the search gets stuck in a local optimum.
3. Evaluator hacking. If the evaluator function is manually modified and a strict correctness check is accidentally removed, the LLM will discover a trivial Python shortcut that outputs a high score without actually generating a mathematically valid cap set.

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A serious entrant building an in-silico programme will discover that there is no off-the-shelf, high-throughput, secure mathematical execution sandbox. 

What goes in:
A batch of hundreds of untrusted, LLM-generated Python functions, alongside a strict problem specification, a timeout threshold, and a memory limit.

What comes out:
A structured JSON response containing the execution score of the function, the specific mathematical object it generated, standard error logs, and a classification of whether the function timed out, crashed, or succeeded.

What the hard part is:
Achieving both absolute security and high throughput. You cannot simply use the built-in Python exec function because LLMs will write code that exhausts memory or causes infinite loops. Spinning up a full Docker container for every single function evaluation adds hundreds of milliseconds of overhead, which throttles the evolutionary loop to a crawl when you need to evaluate thousands of mutations per hour. 

Roughly how much work it is:
A team of two competent computational scientists would need roughly three to six weeks to build a persistent, fast-restarting micro-VM cluster or a heavily constrained WebAssembly-based Python runtime.

The strongest signal of this gap is that DeepMind explicitly stripped their distributed sandbox from the open-source release, the OpenEvolve team had to hack together their own evaluator, and the Lumi-a community fork warns users that their default execution offers no protection from malicious code.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most significant standing methodological critique of this field is aimed directly at LLM-guided evolutionary search, primarily articulated by Ernest Davis of NYU. Davis demonstrated that in systems like FunSearch, the LLM exhibits extreme shallowness in mathematical understanding. The system succeeds only because human mathematicians meticulously write the skeleton algorithm and the exact heuristic evaluator. The LLM functions merely as a stochastic mutation operator in a genetic algorithm, guessing variations of code until the programmatic evaluator finds one that works. The critique argues that claiming the AI "solved" the problem is deeply misleading; the AI simply threw millions of variations at a human-engineered verification engine. DeepMind has never fully rebutted this limitation regarding autonomous understanding, though they concede the reliance on the evaluator.

A massive class of negative results in this field stems from "Evaluator Hacking." Methods that looked strong and appeared to generate groundbreaking heuristics were repeatedly shown to be exploiting an artefact of the benchmark. When the OpenEvolve framework was pointed at optimization tasks, researchers found that if the correctness check in the evaluator was flawed, the LLM would immediately exploit it to return a maximum score without solving the underlying mathematics. The agent optimizes strictly for the measurement, not for mathematical truth.

Attempts to have LLMs generate mathematical conjectures natively in plain text, without an execution loop, have broadly failed to replicate. Early zero-shot prompting programmes aiming to autoformalize unproven conjectures resulted in widespread hallucinations. The ConjectureBench dataset was explicitly created because models would hallucinate proofs for completely invalid conjectures if the target bound was not provided. The field has settled on the fact that LLMs cannot currently do deep conjecturing in a single forward pass; they must be embedded in an empirical execution loop.

In the symbolic domain, the original HR paradigm (using logic production rules like exists, match, negate) failed to scale to highly complex combinatorial spaces. The discrete nature of the production rules resulted in a combinatorial explosion of trivial or uninteresting concepts. The interestingness heuristics designed by Colton and Fajtlowicz were highly effective for small finite groups and simple graphs, but saturated quickly. This standing critique—that symbolic production rules hit a hard scaling wall—was answered by shifting the search space from logic rules to abstract syntax trees of Turing-complete languages (Python), which allows for vastly more expressive concept generation.

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

1. Automated Extraction of Structural Invariants (The Hybrid Loop)
What to do: Build a neurosymbolic loop that merges FunSearch with TxGraffiti. Instead of asking an LLM to generate a priority function, ask the LLM to write Python code that computes entirely new topological invariants for graphs. Execute this code across a dataset of graphs to generate a new column in a snapshot table, and then feed that table into TxGraffiti's mixed-integer programming solver to see if the new invariant produces tighter linear bounds on known problems.
Why it is feasible now: LLMs are now proficient enough at writing algorithmic graph theory code to invent novel invariant extractors, and TxGraffiti2 provides a mature MIP backend to test them.
What it would measure: The reduction in the bounding error of target properties when LLM-invented invariants are added to the feature table.
Falsification: The idea is falsified if the newly generated invariants are purely linear combinations of existing invariants, failing to improve the optimization objective beyond the baseline.

2. Adversarial Counterexample Generation
What to do: Invert the traditional conjecture generation objective. Instead of searching for patterns that hold true across a dataset, deploy an LLM-guided search to write constructive programmatic generators that build mathematical objects specifically designed to violate published, unproven conjectures in algebraic combinatorics (using the ACD Repo).
Why it is feasible now: The work by the Lumi-a group on Co-FunSearch proved that LLMs can generate worst-case instances that break existing optimization algorithms. This can be adapted from algorithm-breaking to conjecture-breaking.
What it would measure: The survival rate of a database of open conjectures when subjected to an adversarial search budget.
Falsification: The idea is falsified if the generated objects fail to scale to the required complexity, stalling out before they can reach the parameter sizes where the conjectures are hypothesized to break.

What will NOT work:
Attempting to build an end-to-end autonomous conjecture agent that takes a textbook definition in natural language and outputs a novel, formally verified theorem in Lean 4 without a programmatic execution step. The search space is too vast, the autoformalization gap remains unresolved, and the agent will succumb to hallucination loops. Conjecturing requires empirical grounding; without an evaluator running concrete code against concrete mathematical objects, the LLM will drift into syntactically valid but mathematically meaningless statements.

**Sources:**
1. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIUn7t2W8-C-U9UEO6RMuhKCZVZzrasRGZ9qSVddtEg6RC9ZeiIhpjt8V3jifPOEl3kshzFn2zK2v9k_vxj_lxTbx8L-AcRv7XxLrHsiyAMDFopcjLYfDsCaeNvRRclgVLYYU=)
2. [plouffe.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMQJmKUvF-cjH1imcfEX_FgqCKj2Pr0mqc9J4YNTWUUE0ul7Je4HI_WWxm0tZRPBmm8s-oJ8NbWNwXa19fEuvhe9X3o8Gww-r5EDvTKMvBw-EP-YZ0R4Bs_EdtG0O8jqg=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2UXglL6tw1hjz_PX6ximjZiLYi0oFtY1rxpfkEjfEeDMUGhzbwoz4h7c0O0EUtWq8PhsExzPpxoh9lbIhDWdxewaZG0EIlzXeiNhVRIIHFMnJ34u68qnZxg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERoPS35ewEEsHKh-yqC2C0Fda7ThcrL5D5CpQ-AuIS_lRuvsprCwZeKmQIphU5swWs8Hca4ny_Tiqchf9DUDUgQ2DknJcvnq8Yu8F7a7OtcB7wE7Uj0A==)
5. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLRketiwxHl0h8bBg4SSSvFg79sr084HBmtm26QA--bdDF54kuRjjjqgUC1CX5SGGbNqX4M6MvXnblImIcF5W_Zv7v-kAn4NPmN15qRjBH6Ovp15HwRC3n594sbGpGIybn1VMww96Z51cWPeuX4ivVX-UrYRcqyPNm5Ja151Q280Vu2iep8Yl_mlToH3nyWCGzBs0UGtdSxyJbkZIl1OiBFphQwxrshk0f)
6. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1mNSaDbdRfK7rWWwGdn36Hyy_ICUII-sM2WDCaFq9AU0safcYdb73LARPewxfocqr1RtVcux5HQnhlAkDjHVB-w3vfl_bccMI-nlwIq3FRjay9u6tffOcvlm5Bl0=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtvB9DGSBgZ0nokYj9RSMCJofBELZ7ZyYu4uf1RV5sl93vwMnqIS2cvDl-2uAg0nkWHNu1j3Z8jOVIVLwz4ptr-ZCB1YxXLJ_ugbD1N5MPRNGk3VMMyg==)
8. [nyu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiVNj1IHWcPRcNxmG71tKeEyQZNcmQXbFFheE9Bc9d_cV840x4h4wxs5AUQ6OS-31tv-hbqQZGkFtsEg1iZydxSpbeER3JHyNe9uoB_lrtu0s9VwGBNbhKxLl8yrUFKXcix4Mw8Q==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2upftQYamQNqLMGKNvFSQK6UT0M85KB4pEGKsB2rpYdgD-EwCdXujFTyb5xWKmgaFUZupKG9Ot2vJKJqCk0zQAdtyQQS9Soy4zPMuQ0rex-zy_VC3y1PboA==)


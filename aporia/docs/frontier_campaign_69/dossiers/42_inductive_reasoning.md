# Prompt 42: Inductive Reasoning

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc3MW1mYXZTQUdkLXdzT0lQemZYYXdRURIXNzFtZmF2U0FHZC13c09JUHpmWGF3UVE
**Elapsed:** 304s

---

# FRONTIER PRACTITIONER DOSSIER: INDUCTIVE REASONING

This dossier is prepared for a competent computational scientist entering the field of Inductive Reasoning in 2026. It maps the transition from classical, exact symbolic methods to the current frontier of neuro-symbolic integration, library learning, and program synthesis. 

Key points to understand before beginning your experimental programme:
First, your understanding of the foundational mechanism is historically accurate but practically outdated. The Candidate Elimination algorithm you described was the state of the art in 1982, but it is effectively dead as an experimental method today. Its intolerance to noise and the exponential explosion of the general boundary made it unusable for real-world tasks. 
Second, the conceptual core of Version Spaces survives, but it has been transformed into Version Space Algebras and E-graphs, which are used to search massive spaces of executable programs rather than simple logical conjunctions. 
Third, the field has largely absorbed into Inductive Logic Programming and Neuro-Symbolic AI. The current frontier relies on combining the exactness of logic-based solvers with the pattern-recognition capabilities of neural networks, driven by benchmarks that test human-like fluid intelligence.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

To answer your explicit request for a correction: your description of Candidate Elimination and Version Spaces is historically accurate to Tom Mitchell's foundational work from 1977 and 1982 [cite: 1, 2]. However, as an experimental paradigm, the exact method you described is functionally dead. It collapsed under two fatal flaws. First, it is entirely noise-intolerant; a single mislabelled example results in an empty version space. Second, while the specific boundary S scales reasonably, the general boundary G suffers from severe combinatorial explosion when dealing with highly expressive hypothesis spaces or numerous attributes [cite: 2, 3]. 

Today, the field of Inductive Reasoning has splintered and absorbed into Inductive Logic Programming, Program Synthesis, and Neuro-Symbolic AI. The concept of the Version Space survives not as a pair of boundary sets, but as Version Space Algebras and E-graphs [cite: 4]. These structures compactly represent massive, sometimes infinite, sets of candidate programs by encoding shared sub-expressions as directed acyclic graphs [cite: 5, 6]. Instead of strictly eliminating hypotheses, modern systems use constraints learned from failed evaluations to prune the search space dynamically, a paradigm called "learning from failures" [cite: 7, 8]. 

What is SETTLED: Pure, classical Candidate Elimination cannot scale. Furthermore, pure deep learning models, including massive Large Language Models as of early 2026, fail catastrophically at novel inductive reasoning tasks that require exact skill acquisition from few examples [cite: 9, 10]. Brute-force scaling of neural networks does not yield exact logical induction.

What is CONTESTED: The architecture of the neuro-symbolic bridge. One side argues for natively differentiable logic, mapping logical operations directly to neural weights using frameworks like Logical Neural Networks, which allow gradient-based learning over continuous data while preserving Boolean logic properties [cite: 11, 12]. The opposing side argues for a decoupled approach where Large Language Models act as heuristic guessers or translators, and discrete symbolic solvers like Answer Set Programming engines act as strict verifiers [cite: 13]. 

What is OPEN: Achieving human baseline performance on the Abstraction and Reasoning Corpus. Transferring learned inductive biases across radically different domains without manual specification of the background knowledge. Creating a unified software framework for Bayesian wake-sleep library learning that does not require immense engineering overhead to deploy.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Tom M. Mitchell
Year: 1982
Title: Generalization as Search
Venue: Artificial Intelligence
Identifier: DOI 10.1016/0004-3702(82)90040-6
Why read it: This is the load-bearing paper for the method you anchored on. It formalizes Version Spaces and Candidate Elimination, establishing the theoretical bounds of searching hypothesis spaces by generality [cite: 1].

Authors: Tessa Lau, Steven A. Wolfman, Pedro Domingos, Daniel S. Weld
Year: 2003
Title: Programming by Demonstration Using Version Space Algebra
Venue: Machine Learning
Identifier: DOI 10.1023/B:MACH.0000008084.60811.49
Why read it: This paper rescued version spaces from the combinatorial graveyard. By introducing Version Space Algebra, it allowed version spaces to represent complex, hierarchical program structures compactly, forming the basis for all modern Programming by Example systems [cite: 4, 14].

Authors: Sumit Gulwani
Year: 2011
Title: Automating String Processing in Spreadsheets Using Input-Output Examples
Venue: ACM SIGPLAN Notices
Identifier: DOI 10.1145/1925844.1926423
Why read it: The paper that introduced FlashFill. It is the most successful industrial application of inductive reasoning and Version Space Algebra, proving that exact inductive synthesis can work at consumer scale [cite: 4, 6].

CURRENT SOURCES (THE FRONTIER)

Authors: Andrew Cropper, Rolf Morel
Year: 2021
Title: Learning programs by learning from failures
Venue: Machine Learning
Identifier: DOI 10.1007/s10994-020-05934-z
Why read it: Defines the modern Inductive Logic Programming frontier. It introduces the generate-test-constrain loop used in the Popper system, replacing explicit version space boundaries with Answer Set Programming constraints [cite: 7, 8].

Authors: Kevin Ellis, Catherine Wong, Maxwell Nye, Mathias Sable-Meyer, Luc Cary, Lucas Morales, Luke Hewitt, Armando Solar-Lezama, Joshua B. Tenenbaum
Year: 2021
Title: DreamCoder: Bootstrapping Inductive Program Synthesis with Wake-Sleep Library Learning
Venue: PLDI 2021
Identifier: DOI 10.1145/3453483.3454080
Why read it: Demonstrates how a system can compress its version space over time by inventing new domain-specific language primitives. It is the gold standard for Bayesian inductive program synthesis [cite: 15, 16].

Authors: Prithviraj Sen, Breno W. S. R. de Carvalho, Ryan Riegel, Alexander Gray
Year: 2022
Title: Neuro-Symbolic Inductive Logic Programming with Logical Neural Networks
Venue: AAAI Conference on Artificial Intelligence
Identifier: DOI 10.1609/aaai.v36i8.20795
Why read it: Addresses the noise-intolerance of symbolic ILP by using differentiable logical operators. It sits at the frontier of integrating continuous neural weights with exact first-order logic [cite: 12, 17].

Authors: Zirong Chen, Meiyi Ma
Year: 2026
Title: Reason Popper-ly: Patching In-Context Reasoning with Inductive Logic Programming
Venue: arXiv
Identifier: arXiv:2607.23019
Why read it: Represents the immediate 2026 frontier of using classical ILP solvers as runtime verifiers for Large Language Model reasoning traces, diagnosing and correcting logical violations on the fly [cite: 13].

Authors: Francois Chollet
Year: 2019
Title: On the Measure of Intelligence
Venue: arXiv
Identifier: arXiv:1911.01547
Why read it: Introduces the Abstraction and Reasoning Corpus. While older than 2023, it is mandatory reading because it dictates exactly how inductive reasoning progress is measured today [cite: 10, 18].

PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: Popper
URL: https://github.com/logic-and-learning-lab/Popper
Language: Python, Prolog, ASP
Licence: MIT
Activity: 2025
Verdict: MAINTAINED
What it runs: The state-of-the-art Inductive Logic Programming generate-and-test experiments. It can synthesize logic programs from positive and negative examples while handling noise.
Limitations: Requires SWI-Prolog and Clingo installed. By default, it uses the CPSAT solver which is slow; you must manually download and compile the NuWLS anytime MaxSAT solver to achieve the published performance times. Recursion is supported but causes the search space to explode exponentially if not strictly bounded in the bias file [cite: 19].

Name: DreamCoder
URL: https://github.com/ellisk42/ec
Language: Python, OCaml
Licence: MIT
Activity: 2023
Verdict: DORMANT
What it runs: Wake-sleep library learning experiments where the system invents its own concepts to solve inductive tasks. 
Limitations: The canonical implementation is notoriously fragile and difficult to build on modern toolchains. It relies on a complex interplay between Python neural networks and an OCaml synthesizer, requiring a Singularity container to run reliably [cite: 20, 21]. Most practitioners end up writing their own simplified wake-sleep loops rather than fighting the original repository.

Name: Aleph
URL: https://github.com/friguzzi/aleph
Language: Prolog
Licence: Artistic/GPL
Activity: 2022
Verdict: DORMANT
What it runs: The classical 2000s standard for Inductive Logic Programming. It searches for clauses in a top-down manner and is useful for establishing baselines against modern systems.
Limitations: It is legacy software originally written for the YAP Prolog dialect. The SWI-Prolog port linked above works, but requires formatting examples and background knowledge in a very specific, slightly archaic single-file structure [cite: 22].

Name: PyILP
URL: https://github.com/danyvarghese/PyILP
Language: Python
Licence: MIT
Activity: 2024
Verdict: MAINTAINED
What it runs: A user-friendly Python wrapper that allows you to run classical ILP algorithms like Aleph and Metagol without writing raw Prolog directives.
Limitations: It masks some of the deeper configuration options of the underlying Prolog engines. Good for prototyping and teaching, but less suitable for highly customized frontier experiments [cite: 23, 24].

Name: ARC-AGI
URL: https://github.com/fchollet/ARC-AGI
Language: Python, JavaScript
Licence: Apache 2.0
Activity: 2024
Verdict: MAINTAINED
What it runs: The testing harness and data loader for the Abstraction and Reasoning Corpus. It includes a browser-based interface for human baselining.
Limitations: This is purely a benchmark harness, not a solver. You have to build the inductive engine yourself and interface it with this testing environment [cite: 25].

PART 4. DATA AND BENCHMARKS

Name: ARC-AGI Training and Evaluation Sets
URL: https://github.com/fchollet/ARC-AGI
Size: 800 tasks
Licence: Apache 2.0
Used for: The authoritative benchmark for general inductive reasoning and fluid intelligence. Tasks consist of grid-based input-output pairs requiring few-shot abstraction.
Notes: Do not train your final model on the evaluation set. Base LLMs saturate near zero percent on this without heavy scaffolding. A secondary private evaluation set exists for competitions to prevent test-set contamination and overfitting [cite: 9, 25].

Name: ILP Experiments Suite
URL: https://github.com/logic-and-learning-lab/ilp-experiments
Size: Dozens of datasets
Licence: MIT
Used for: The standard benchmark collection for Inductive Logic Programming. Includes classic program synthesis tasks, game playing like Chess KRK endgame, and biological datasets like Mutagenesis.
Notes: This framework standardizes the evaluation of Popper, Aleph, and Metagol. It is highly reproducible and authoritative for classical and modern ILP comparisons [cite: 26].

Name: DreamCoder Compression Benchmark
URL: https://github.com/mlb2251/compression_benchmark
Size: 27 historical runs across 6 domains
Licence: Unknown
Used for: Studying the intermediate sets of programs processed by DreamCoder's compressor.
Notes: Useful because it isolates the library learning compression phase from the highly expensive neural-guided search phase. It allows you to test new Version Space Algebra refactoring algorithms without running the full wake-sleep pipeline [cite: 27].

PART 5. THE REPRODUCTION RECIPE

The most informative and highly reproducible experiment in this field is the evaluation of the Popper system on the List Transformations benchmark, replicating the core finding that learning from failures via Answer Set Programming constraints drastically outperforms classical ILP search.

Software: Popper version 5.0.1, SWI-Prolog version 8.4 or higher, Clingo version 5.4 or higher. The NuWLS MaxSAT solver must be compiled and added to your system path.
Dataset: The "List Transformations" and "List function problems" datasets from the ilp-experiments repository github.com/logic-and-learning-lab/ilp-experiments [cite: 26].
Parameters: 
Number of variables capped at 7.
Recursion disabled in the bias file.
Predicate invention disabled.
Background knowledge explicitly transformed into Datalog format for preprocessing.
Timeout set to 600 seconds per task.
Replicates: 10 independent trials using sequential random seeds starting from 0.
Compute cost: Approximately 2 to 5 CPU hours on a modern multi-core machine. No GPU required.
Expected result: Popper should achieve greater than 90 percent predictive accuracy on the held-out test examples across the list tasks, converging to exact minimal description length hypotheses significantly faster than the Aleph baseline. Compare your generated results.json to the published tables in Cropper and Morel 2021, "Learning programs by learning from failures" [cite: 7, 8].

Three most common ways people get this experiment wrong:
1. Failing to compile and link the NuWLS anytime MaxSAT solver. Popper will silently fall back to the default CPSAT solver, which works but ruins the execution time metrics, making Popper look artificially slow [cite: 19].
2. Leaving recursion enabled in the bias file. While Popper supports recursion, it exponentially expands the hypothesis space. The list transformation tasks do not require recursion if the background knowledge primitives are sufficient; leaving it on leads to timeouts [cite: 19].
3. Forgetting to translate the Background Knowledge into Datalog. Popper relies on a preprocessing step to ground the background knowledge. If it is not in Datalog format, preprocessing fails or takes too long, ruining the generate-and-test loop efficiency [cite: 19].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

A unified, easily deployable neuro-symbolic framework for wake-sleep library learning in Python. 

Currently, if you want to run experiments combining neural network recognition models with symbolic Version Space search and library extraction, you must either fight the archaic OCaml/Python Singularity container of DreamCoder, or build it yourself. Several research groups have privately rebuilt the DreamCoder pipeline in Python and Rust because the canonical repository is too brittle for rapid experimentation [cite: 21]. 

What goes in: A domain-specific language of primitive operations, and a set of tasks defined by input-output examples.
What comes out: A compressed library of newly invented, human-readable functional primitives, and a trained neural network that maps new tasks to probabilities over that expanded library.
The hard part: Implementing the Version Space Algebra equivalence graphs. You have to write a refactoring algorithm that can take thousands of synthesized programs, identify shared subtrees, and extract them into new library functions while maintaining logical equivalence.
Work required: For a competent computational scientist, building a clean, GPU-accelerated wake-sleep loop with an E-graph backend in Rust/Python will take three to six months. It is a major undertaking, but it is the highest-leverage tool missing from the open-source ecosystem.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most profound negative result in this field is the failure of the exact mechanism you anchored your query on. Pure Candidate Elimination works elegantly in theory but fails catastrophically in practice. The standing critique, formulated by Haussler in 1988 and empirically validated throughout the 1990s, is twofold. First, the size of the general boundary G grows exponentially with the number of attributes. For any non-trivial hypothesis space, maintaining G exhausts system memory. Second, because the method is non-statistical, a single mislabelled training example causes the specific and general boundaries to cross, collapsing the version space to an empty set [cite: 2, 3]. Mitchell himself abandoned strict Candidate Elimination in favour of statistical learning and explanation-based generalization. If you attempt to run Candidate Elimination on real data, you will be measuring noise, not learning.

A massive failed programme in recent years is the attempt to solve the Abstraction and Reasoning Corpus using pure end-to-end deep learning. Between 2019 and 2024, researchers threw increasingly massive Large Language Models and Vision Transformers at ARC-AGI. Because ARC evaluates out-of-distribution generalization on novel tasks, pure statistical pattern matching failed entirely. Despite a fifty-thousand-fold scale-up in base LLM pretraining compute, model performance hovered near zero percent without symbolic scaffolding [cite: 9, 28]. This proved that parameter memorization does not equate to inductive reasoning.

A standing critique of the Neuro-Symbolic field concerns the relaxation of logic. To make Inductive Logic Programming differentiable, many researchers replaced strict Boolean logic with real-valued fuzzy logic, allowing gradients to flow. The critique, which remains largely unanswered by the fuzzy-logic community, is that this destroys the interpretability and exactness of the learned rules. A network might learn that a rule is 0.74 true, which is meaningless in strict programmatic synthesis. The Logical Neural Network framework was built specifically to answer this critique, enforcing strict bounds to recover exact Boolean logic at the output, but it remains computationally expensive to train [cite: 11, 12, 29].

Finally, there is a standing critique regarding ILP benchmarks. Datasets like Mutagenesis or the Michalski Trains are thoroughly saturated. ILP systems frequently achieve high accuracy not by learning the underlying phenomenon, but by overfitting to the closed-world bias of the small datasets. This is why modern practitioners are abandoning these datasets in favour of dynamic program synthesis benchmarks and ARC-AGI [cite: 18, 26].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Experiment 1: LLM-Guided Version Space Search on ARC-AGI
Feasibility: High. The tooling for Large Reasoning Models and Version Space Algebras is now mature enough to integrate.
What to do: Build a neuro-symbolic agent where an LLM proposes highly probable programmatic sub-routines for an ARC task, and a deterministic Version Space Algebra strictly prunes the hypothesis space based on the grid examples. 
What it measures: It measures the reduction in the branching factor of the search tree when guided by a neural prior versus an unguided symbolic search.
Falsification: If the LLM's proposed primitives do not reduce the required search time compared to a uniform prior, the hypothesis that LLMs possess abstract geometric priors is falsified.

Experiment 2: Differentiable Constraint Learning in Popper
Feasibility: Medium. Requires modifying the internals of the Popper ILP system.
What to do: Fork Popper and replace its discrete Clingo/Answer Set Programming constraint generation phase with a Logical Neural Network. Feed the system continuous or noisy data (e.g., raw sensor data or image embeddings) rather than pre-parsed Prolog facts.
What it measures: The predictive accuracy and rule-recovery rate of an ILP system on strictly continuous, noisy data.
Falsification: If the LNN-guided Popper fails to converge faster than a baseline statistical classifier, the utility of strictly bounded differentiable logic in continuous domains is falsified.

Experiment 3: Open-Source Rust Wake-Sleep Learner
Feasibility: High engineering effort, low scientific risk.
What to do: Rebuild the DreamCoder architecture using a modern stack. Use Rust for the exact equivalence-graph library extraction and a standard PyTorch backend for the neural recognition model. Benchmark it on the DreamCoder Compression Benchmark.
What it measures: The computational overhead and sample efficiency of wake-sleep learning when freed from legacy single-threaded OCaml constraints.
Falsification: If the execution time is not improved by at least an order of magnitude, the bottleneck in library learning is fundamentally algorithmic rather than implementation-bound.

What will NOT work:
Do not attempt to fine-tune a base Large Language Model directly on the ARC-AGI training set in hopes of increasing evaluation accuracy. The tasks are designed to be immune to memorization. The model will overfit to the visual syntax of the training grids and fail completely on the evaluation set. True inductive reasoning requires a dynamic, test-time search through a hypothesis space, not static weight updates during pretraining.

**Sources:**
1. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOpt57aOUjFPSMcEGkY2bdxWNQJoc_i65c90TjHQVxwmbM07y1NR_Nle9Yk4PLY3oN3XMZuDBy1vn4i4IJaXo-NeBZUBGqkVgqMbu3ExXuFJLcETF3dVJFYo4KOY63ujIPhr9mRYR6W_TG)
2. [cmu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6woA48mBhk1GtMhGi12TN6P6NLfYETX9Mq_ABCqJ7e1B18I1OHcpm6sCvPquKnD73DSzgxiWvrkw2lv5iSKvC8RdL3tFwbIAg4CBqpu_m2h-BO6Rrwa6OSZanYCsr33gHaSN-q8H_86prhCX_kX18JxtOZnQI)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3ocVGFA0tqglae2qMlfwsKDavZv20gbDwkjjx4cXMUDnfphCU8ICRHckHCnTxp5zy--a4HpHyHJJxxuk2LP58kQzMETYh_J5IPiiTp3VDP3xe4jVuzR02Rg==)
4. [remy.wang](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUT7rNi4BC0zpyXa2zf0ZahGUwhfP9a7PAbprZ1fpMzd4tgck10AX0P9xbdgSaEBQpsEPtZA-aOrtiQNXM6GMmrDQq9OK4i0wy2_gPmv8mYcI2iETs4-Ow)
5. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoLmSrM9wa3hamwpr29kbnHqx9-hZQ6zWv5jHiUgzt0dqTNVesYonjr-olSo6p4uEtKePUR9pGy9ud6c9RsSJX_LGIN0pJjBHwsbYIIvgXFSfzkFGmVTKwClehS5YH-WvCnmSMwePY52vV7ep_uWD47JXx3QcFT_AYfjc=)
6. [microsoft.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNM2UNsmICrxr1CgwyiCqOPYsCCSjfwxkAyXQ7rH_K7wEejClvdDZaNaSgwtkazb4ywAHX9MYMb8JVe_Qxqo6tpXYlUlGQXze1fxyOa5CVsqh6aS9mMfbHofMZJmHWpgnddtReCQOUYRm0kxPY46nBZniC7V8SaGhRXzG46FWYQUtKNShko9iFBAjIHKdCgbfU2XMMIJJH5tGfiqHXxg==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyKERm2k5k_2RsXcsmxsASEW8nSQ_zG6gkLo7dZBwHF5ZbRl0Ci8QVSYL9TOcjNiwcPOxToQ1dB1lPhw2fP3AWDYb5zQ9UxmYM4n7WFBMgm-bJTzdCEg==)
8. [ox.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGp5c03gZDy7WBPwrz1OeRok6kV8Sgz8FB-dMosMw5EnbEn9vZKeRbNdttHCMmk_I5Th9hqMRbHwX1hiD6F-3dzHUy35Vs5QZg9e-oZ0fq7Syyn-0X_KEvjvZFY7nP8_BGwW_xqGNt4txK1nO5qhG-1I-7FpZA3aiGcslQJ)
9. [arcprize.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMZUarE_dXY2kD-hJgzpthmqBy0fGFORQMwnNh0Z-lawYUhRRj2a4_U3GE83w_1FYHUhR3fA8-lMG38OdscYHRYn365RFdgVzVRerghtT09kCSkhk=)
10. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJCbNkEUrDuX5XEb94KfZfwnFeAKbklvBusSuh2K2YxfwyvWl1QA9bk7YeUT5CVve7Y5Gt38KNhg6v9B5_PBEVDCZiYQ2WNE-Vk0btzhjmXdefvs6q8W3gb2jCe14DSg==)
11. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEihirQmsw38ydndnETmFqWpbi3JI4Oit8bKHext47E_Ejb9dg4ps_oGYzxEA-9-JD3TuFeNbC6odv8zDYkpDCL9GWLiAVlSICYPDvVUi3M4b2gqYASKorRF2AC6so=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_hkq6Rq0LXnXg4huoeKuqv-DukfMJxFlyY-cerB6RrrlyB0C64dfgJpQ3VLQp_uXETVE9b5CAOovakQepT53qWiBNvUPuKkLKU4nD7-_hE_2BH5BZmA==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7xAx409H4HnUl7IKQbootbY9e26n_UXzz-eWhuQPU4ZrPabiTvoQaVsLm5GysZeaS_6nqJF1zyb7a0eDgFK5575S1vod6p8_QwFfnPttza3YHdoLxFHwL2Q==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGe9DuNCu5IWNj4JRurfB8CILayXRjS0mOy9wP7wibCrieJurDAo5Sg2I6xfmM2O6rwiv7iQX1LyaXrTYr7E8lFzgANIDC65bFag4xmGZ2e3VHRiv1RyzaPYw==)
15. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHskZRq8S2XMWgdmI_J-8wOGw_ytiQCtOu9KGkErwP57-4JTsS2xxrsJwcIzxkIjdB6045dL_07qBHRo4dhqSP-xlwBoO5G96z2wqlmS8Q2ar1C8zhV71jcjj5iu3vV74syRKYd9GkdavXdv4Ao1yHSg==)
16. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8nwOrzVSKGr9giSV78xQYpN6tJFLKdopP-_AFtCcIhlVcIOev3svUbuOrrXaSge3GrmMg04jHzuOike7XyxkeSEKC-kN53mVseiGKPOBw467Sr2TLxLuIKwNjeKkC4gj5doZQJG-KuxQ290KGqGsz3bt2bd_rXGh508j8ie0Vk_hP2Di-5A41uSAB2AvcJRD3Ou-TgpDRgfpYMBSmGKcyp7FOiQZxDI9ysxuTTQ==)
17. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9Nba3lQFifdkUU6GI_2Qqa5FdcT0WZ6v0C5XbZFcJiwt3vAdzmtb2PUuKvXnPFSAgx_o4oPk0dgAgugymizCfp9jJD3MGlSnPi6K6ah7N8x9EtB3MSCRbTk5wY-aMnq-Si4BQ99qXdD7ImGIPjLbQ3NZ8y8oK9RQ_a3mol3Nz8hbbBhaSJQcJqGvS-Npb0m--5ZCRwvwHO07Qb0HZ4Y-ZXfL9EOLoh-MQv3Q4kGg=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH89nfDU0Qq-JOIdc559h4LKNjEuycPOazNjfLsy9Vhdr4KMmEFYeqeGNVRtAn0rPYge8WiKhe5Qf4ewImM7W21Yuy_xo0-P299QZfTP7PMHBuDY5fnnYJ2uQ==)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHS1wsbjnieoHFgoR27loYf9j22W-C-Wh7PRxtibGijVSkkDWKqfVp2x21AYPKIVVEyDNrZo9kmcWXOmWdQTkCTKnLzZoO-3j4K3DF1tQFeIFg2fyV02D23rl_dshB157_WS-XM6qA=)
20. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnIJX1ci9iRj2b5qLx5CBsh1dySduTzw6xLpuX4psMn3kJ7ECnwEi7I8WY3rwXssGej9snAxU4B3DmceGufT6b3kLeANZxpT7_GTitgvm7jZPyHzY=)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVKGgNw-JynXfen10WLYanHGZCwUp5DlDJN1Ig6GrxgT8gvtwLdUgjFi9jsFtHi4RiTBqQmiShbivnPU-VRrd8vvEYgxPk1GpTfYXzaBWm5tC2hJmMvx7Sy65b9A==)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW4L8UGwAqxz6hBL8lTvqyfBWzrrXm-QsWLqMpyOsaHvUgKcLoe1spMZKWUVUuC_5dkBzLqrxPN8AuKkM5LTMQ0A6ry19ngqzYpBoxp_VBOUGDSEZz4gQ=)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmhKirCpkAuoMq2JCvGHXIFBpS8ZOvzdZP1suesWGz9Oot7E78GvQyr7mP45MjNSbQzaj41BadFp0pBJLEbdrrRR5g7w7jxLDpul0ia76wSW3NMufMkY6WoCVr)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiYquQWSXnIIi9Ksoro1aHH1vANQ1NxYekPb38HM6QkhRIUnoA_OA3tiA1_syMxGBD7IqC4H5yvVBENu1pNf14oRfOMN0p8yNj6jWA3gR90fJnqNnzvpkPHydLexPK)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHN1KBDrDQtqz13VY1eHHKmRZvskCOPbbDnfFwU34hElMGXVRW2MXEorG1wK63gW0sfjfLftc7mzPRzyjgQkRfzU28hvdbEUmKzxv9cegyJ62Yc5csHpq8izg==)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGj1bPNS-KD5DtYBqerkmLDI1UOuLWYKC7X-J2DP6L_joBRHWBkYxpuSwyWduSAldtUHJefeifgjrjdSf0RPTSQ21yASfW_8y8rp4m3PGueinMHvYHKvrZKCSBLMGtgjo5AEa0HJ6Ci26cSrBEL13w=)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHqrFsWvXNjdoYBnGkxsej4CAve_1kwybbqPbnlNTkWhGVROVBN8LGSGQAUgr1rXH_KNQa7P00OseAI1WXjiZEoSWRbTFoAdgnXZs3iaQjRJTLZePOQC5xZbgIcjvEyL9ERqvYiC8=)
28. [lab42.global](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYxMc26jyBvKu43AGYvd33s1jAFTAQuDapdNDIcsE1ZmVK2q74yQAFZkfQL68hqiqH8dYuyCy6YXRqDvnAAgyao9kQQ1dDqr-wd1FHPOTy)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHFhhVUWHS_AuzixanceZKxc-gWLqXqY-_2JjKv9ESaTeKUbpu8s0KD_L5xt4ixYQ2YQXcRSviIWKf13gKe3dtkXEPDS8NB7Lll-pHNwjn1FnnwwFL_9SuhA==)


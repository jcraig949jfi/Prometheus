# Prompt 302: Module acquisition and subgraph reuse in evolved graphs

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdGU2VoYXJLaUNiN1ctc0FQM09HUW9RZxIXRlNlaGFyS2lDYjdXLXNBUDNPR1FvUWc
**Elapsed:** 365s

---

# FRONTIER PRACTITIONER DOSSIER
Field: Module acquisition and subgraph reuse in evolved graphs

**WHO IS ASKING AND WHY**
This report is structured for a computational scientist entering the field of evolved graph representations, specifically focusing on Cartesian Genetic Programming and its modular extensions. It addresses the core mechanisms of subgraph reuse, the entanglement of description length compression with mutation step size, and the precise state of the field in 2026. 

**KEY POINTS AND CONTEXT**
The central question you are anchoring on—whether the performance gains of module acquisition stem from computational reuse or from the systemic change in mutation behaviour—is one of the most profound unresolved confounders in the field. The evidence leans toward the conclusion that the structural linkage of macro-mutations is the primary driver of performance in highly modular graphs, but definitively separating this from description length compression requires experimental harnesses that currently do not exist off the shelf. 

Historically, this field coalesced around Embedded Cartesian Genetic Programming, where subgraph encapsulation was handled dynamically during the evolutionary run. However, pure dynamic module acquisition struggled to scale. As of 2026, the frontier has shifted. Researchers have largely abandoned purely random evolutionary module acquisition in favour of hybrid machine learning approaches, where Transformer architectures and large language models are deployed as surrogate evaluators or intelligent mutators to identify which subgraphs are actually worth compressing.

Below is the definitive, concrete, and highly specific dossier you require to begin running frontier experiments today.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Cartesian Genetic Programming is a graph-based evolutionary algorithm where candidate solutions are encoded as a directed acyclic grid of computational nodes. The genotype is a fixed-length array of integers mapping to functions and connections, but the phenotype is typically much smaller because many nodes do not connect to the final outputs. This creates a highly redundant genotype-phenotype map, allowing for neutral drift—mutations that change the genotype but leave the phenotype and fitness identical. Module acquisition, historically formalized as Embedded Cartesian Genetic Programming [cite: 1], attempts to automatically identify recurring active subgraphs, compress them into reusable modules added to the function set, and allow the algorithm to call them as single nodes. 

What is SETTLED in this field is that raw Cartesian Genetic Programming relies heavily on massive genetic redundancy. It is conclusively established that evolutionary search is most effective when up to 95 percent of the genes are inactive, serving as a protective reservoir for neutral drift [cite: 2, 3]. It is also settled that standard crossover operators are generally destructive and ineffective in this representation; the algorithm is almost entirely driven by mutation [cite: 4, 5]. Furthermore, the Single Active Mutation strategy—where nodes are mutated repeatedly until exactly one active, output-contributing node is altered—is the settled baseline for efficient evaluation, replacing naive probabilistic mutation rates [cite: 6, 7].

What is CONTESTED is the precise mechanism by which structural modifications to the representation improve search. Brian Goldman and William Punch argued that many perceived algorithmic improvements in Cartesian Genetic Programming actually stemmed from unintended corrections to length bias and positional bias, rather than the mechanisms the original authors claimed [cite: 8, 9]. They introduced a Reorder operator to fix this, but more recent work by Cui et al. strongly contests this, demonstrating mathematical and practical flaws in the Reorder operator and proposing refined mutation variants instead [cite: 5, 10]. The debate over whether module acquisition aids search via representational compression or via correlated macro-mutations remains a live disagreement, primarily because isolating the two phenomena requires a bespoke genetic engine that neither side has built.

What is OPEN, and what has changed radically in the last three years, is the method of determining which subgraphs to mutate or package. Between 2023 and 2026, the field of pure evolutionary module acquisition was largely absorbed into the domain of machine-learning-guided surrogate mutation. Pure Embedded Cartesian Genetic Programming is essentially dormant. The frontier is now defined by systems that use Transformer neural networks to observe the genetic log, predict the structural weaknesses in the graph, and guide the mutation or modularisation process directly. What was lost in this merge is the biological purity of an algorithm discovering its own modularity entirely from random walks; what was gained is the ability to scale to problems like 8-bit approximate multipliers, which were previously unreachable from scratch.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Miller, J. F., & Thomson, P.
2000
Cartesian Genetic Programming
European Conference on Genetic Programming
IDENTIFIER UNKNOWN
This is the genesis paper of the field, defining the rectangular grid representation, the integer-based genotype, and the separation of active and inactive genes that allows neutral drift to occur.

Walker, J. A., & Miller, J. F.
2004
Evolution and Acquisition of Modules in Cartesian Genetic Programming
European Conference on Genetic Programming
DOI 10.1007/978-3-540-24650-3_17
The foundational text for your specific anchoring question, introducing the dynamic creation, expansion, and destruction of modules in the graph, and demonstrating its performance against non-modular baselines [cite: 4, 11].

Walker, J. A., & Miller, J. F.
2008
The Automatic Acquisition, Evolution and Reuse of Modules in Cartesian Genetic Programming
IEEE Transactions on Evolutionary Computation
DOI 10.1109/TEVC.2007.903551
This is the definitive, load-bearing exposition of Embedded Cartesian Genetic Programming. A practitioner must read this to understand the exact structural mechanics of how subgraphs are encapsulated and mutated as distinct units [cite: 12, 13].

Goldman, B. W., & Punch, W. F.
2015
Analysis of Cartesian Genetic Programming's Evolutionary Mechanisms
IEEE Transactions on Evolutionary Computation
DOI 10.1109/TEVC.2014.2324539
This paper is mandatory reading because it deconstructs prior assumptions about why these algorithms work. It exposes the hidden length bias and positional bias in standard graph evolution, providing the critical lens through which any claims about modularity must be evaluated [cite: 8, 9].

CURRENT SOURCES (2023 - 2026)

Cortacero, K., Wilson, D. G., et al.
2023
Kartezio: Evolutionary design of explainable algorithms for biomedical image segmentation
Nature Communications
DOI 10.1038/s41467-023-42674-9
This paper proves that modular Cartesian Genetic Programming is alive and highly effective in modern few-shot computer vision tasks, producing transparent processing pipelines that compete with deep learning without requiring GPUs [cite: 14, 15].

Kalkreuth, R.
2024
CGP++: Modern C++ Implementation of Cartesian Genetic Programming
arXiv:2406.09038
The paper introduces the most robust modern architecture for the field. A practitioner needs this to understand how modern implementations handle checkpointing, concurrency, and mutation pipelining compared to legacy C codebases [cite: 16].

Cui, H., Margraf, A., & Hahner, J.
2022
Refining Mutation Variants in Cartesian Genetic Programming
Lecture Notes in Computer Science
DOI 10.1007/978-3-031-21094-5_14
This is the primary critique of the Goldman Reorder operator. It provides the modern community standard for mutation variants, proving that splitting mutation rates between active and inactive nodes, and decaying the number of active node hits over time, yields superior convergence [cite: 7, 17].

Galeta, O., & Sekanina, L.
2026
Genetic Programming with Transformer-Based Mutation for Approximate Circuit Design
arXiv:2605.21055
This paper defines the 2026 frontier. It demonstrates how to replace the blind mutation and modularisation operators with a BERT-based Transformer model trained on thousands of evolutionary logs to predict exactly where and how a subgraph should be altered [cite: 18, 19].

Tomasovic, M., & Sekanina, L.
2026
Multi-Objective Coevolution of Prompts and Templates for Circuit Approximation
Preprint
IDENTIFIER UNKNOWN
This paper represents the extreme edge of the field, showcasing a co-evolutionary approach where a large language model is used as a surrogate mutator without domain-specific training, steered by evolving prompt templates [cite: 20].

There is no modern, comprehensive survey that covers the 2026 machine-learning integration frontier. The best historical summary remains the 2011 book Cartesian Genetic Programming by Julian Miller, which serves as a textbook rather than a frontier survey [cite: 21, 22].

PART 3. SOFTWARE I CAN ACTUALLY RUN

CGP-Library
http://www.cgplibrary.co.uk/ or https://github.com/AndrewJamesTurner/CGP-Library
Language: C
Licence: LGPL
Year of most recent activity: 2015
Verdict: DORMANT
This is the legacy reference implementation by Andrew Turner. It supports standard, recurrent, and neural network graph evolution out of the box. Today, it can run basic symbolic regression and small boolean circuit approximations. Its main gotcha is its age; it lacks native multithreading hooks suitable for massive modern core counts, relies on manual pointer management that can leak during heavy module creation, and the community has largely moved on [cite: 23, 24]. Furthermore, compiling it on modern toolchains sometimes fails due to undefined references in older GCC configurations [cite: 25].

CGP++
https://github.com/RomanKalkreuth/cgp-plusplus
Language: C++
Licence: UNCONFIRMED
Year of most recent activity: 2024
Verdict: MAINTAINED
This is the modern community standard that most serious computational scientists use for bare-metal graph evolution. It provides a generic, object-oriented framework with built-in concurrency support, checkpointing, and parameter interfaces for hyperparameter tuning. It can run the General Boolean Function Benchmark Suite out of the box. The limitation is that it focuses on standard graph evolution; if you want dynamic module acquisition (Embedded CGP), you will have to implement the encapsulation logic on top of its mutation pipeline yourself [cite: 16, 26].

Kartezio
https://github.com/Mantalys/kartezio
Language: C++ and Python
Licence: UNCONFIRMED
Year of most recent activity: 2026
Verdict: MAINTAINED
This is a highly specialized, modular framework built on top of OpenCV for evolving explainable image-processing pipelines. It can run few-shot image segmentation experiments today on a single CPU core. Its gotcha is that it is tightly coupled to computer vision primitives. While the authors state the underlying principles are domain-agnostic, stripping out the OpenCV dependencies to run pure mathematical module acquisition experiments would require essentially gutting the framework [cite: 14].

EvoApproxLib
https://ehw.fit.vutbr.cz/evoapproxlib/ or https://github.com/ehw-fit/evoapproxlib
Language: Verilog, C, Python, Matlab
Licence: UNCONFIRMED
Year of most recent activity: 2025
Verdict: MAINTAINED
This is not an evolutionary engine, but rather the authoritative library of evolved approximate arithmetic circuits generated by multi-objective Cartesian Genetic Programming. You must download this because it contains the exact circuit architectures, Verilog files, and C models that the 2026 frontier uses as training data for Transformer-guided mutation. You cannot run an evolution experiment with this repository alone, but you cannot benchmark a modern module acquisition experiment without it [cite: 27, 28, 29].

A note on famous but dead software: The original Embedded CGP codebase used by Walker and Miller in 2008 is effectively lost to the public domain and unbuildable on modern systems. Any attempt to reproduce their exact module acquisition behaviour requires re-implementing it from their papers.

PART 4. DATA AND BENCHMARKS

EvoApproxLib Dataset
Access route: https://ehw.fit.vutbr.cz/evoapproxlib/
Approximate size: Thousands of 8-bit to 128-bit approximate adders and multipliers.
Licence: UNCONFIRMED
What it measures: Error metrics (Mean Absolute Error, Worst Case Error) versus hardware metrics (Power consumption, Area, Critical Path Delay) for combinational circuits.
This is the authoritative benchmark for hardware-oriented graph evolution. However, there is a known saturation problem: evolving an 8-bit multiplier from a random starting graph using standard mutation or random module acquisition is mathematically intractable and has saturated the capabilities of blind search. Modern experiments bypass this by seeding the population with known conventional multipliers and only evolving the approximations [cite: 19, 30].

General Boolean Function Benchmark Suite
Access route: Provided as PLU files within the CGP++ repository.
Approximate size: Dozens of logic synthesis truth tables.
Licence: UNCONFIRMED
What it measures: The ability of the graph representation to exactly match a target truth table with minimal active nodes.
This is treated as the standard for pure algorithmic capability. Contamination is not an issue, but overfitting can occur if the maximum graph size is set too small, trapping the evolution in local optima before neutral drift can find a modular solution.

Standard Symbolic Regression Datasets
Access route: Typically generated via McDermott et al. 2012 specifications, available in CGP++.
Approximate size: Varies (hundreds of floating-point pairs per equation).
Licence: Open
What it measures: Ability to evolve continuous mathematical functions.
Merely popular, not authoritative. The field knows that symbolic regression via graph evolution is highly sensitive to the chosen function set and terminal constants, often resulting in solutions that memorize the training points but fail to generalize out-of-distribution.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to anchor yourself in this field is the Goldman and Punch 2015 Single Active Mutation baseline. This experiment does not explicitly solve your question about step size versus reuse, because, as stated, no off-the-shelf experiment isolates those two variables cleanly. However, this is the mandatory precursor experiment. If you do not replicate this baseline, any module acquisition results you measure will be hopelessly confounded by length bias.

Software and version: CGP++ (latest commit as of your start date).
Dataset: The 4-bit even parity boolean function (a standard hard problem that requires modularity to scale).
Parameters to set:
Nodes (columns): 100
Rows: 1
Levels back: 100
Function set: AND, OR, NAND, NOR.
Mutation operator: Single Active Mutation.
Population size: 1 parent, 4 offspring (the standard 1 plus 4 Evolutionary Strategy).
Target fitness: Zero errors on the 16 truth-table inputs.
Independent replicates: 100 independent runs.
Seeding regime: Cryptographically secure pseudo-random number generator, with explicitly logged distinct seeds for each run.
Compute cost: Less than 1 CPU hour on a modern desktop.
Expected result: The median number of evaluations to reach a perfect solution should match the baseline numbers published in Goldman and Punch 2015. You are specifically looking to measure the final description length (number of active nodes).

The three most common ways people get this experiment wrong:
First, researchers fail to distinguish between total evaluations and distinct evaluations. Because Single Active Mutation explicitly guarantees a change to the active phenotype, every offspring evaluation is distinct. If you compare it against probabilistic mutation, you must strictly discount the computational cost of evaluating offspring whose active genes were not mutated, or your budget tracking will be flawed.
Second, researchers set the maximum node limit too low. Standard graph evolution requires vast amounts of inactive genes for neutral drift. Constraining the graph to 20 nodes for a 4-bit parity problem will cause severe stagnation.
Third, researchers improperly implement the genotype-phenotype mapping pass, executing inactive nodes during fitness evaluation. This exponentially inflates the CPU time and invalidates the computational cost comparisons.

To answer your specific organizing question, the missing experiment you must build is the Decoupled Linkage Experiment. Currently, when a subgraph is encapsulated into a module, its execution is reused, and its mutational linkage is unified. No existing software allows you to toggle these two features independently.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

To run frontier experiments separating computational reuse from mutational step size, you must build a Decoupled Linkage Graph Engine. No off-the-shelf tool provides this. 

Interface Requirements:
What goes in: A standard one-dimensional Cartesian Genetic Programming integer array, alongside an external array of module definitions.
What comes out: A fitness score, a graph description length, and a distinct tracking of mutational cascade depth.

The Hard Part:
You must engineer a phenotype translation engine that supports Ghost Modules. 
Condition A (Standard Module): A compressed subgraph is stored once. When executed, it computes once and caches the result for all consumers. When mutated, the single structural change propagates to all consumers.
Condition B (Pure Reuse, Decoupled Mutation): The subgraph is compressed and cached for execution speed. However, during the mutation phase, the mutator must treat the module as if it were fully expanded. A mutation hitting the module must only alter one specific spatial instance of that module in the phenotype, breaking the linkage.
Condition C (Pure Mutation, Decoupled Reuse): The subgraph is structurally linked for mutation. If the module mutates, all instances change simultaneously. However, during evaluation, the subgraph is completely unspooled into raw nodes and executed redundantly, preserving the original uncompressed description length.

Roughly how much work it is:
Modifying CGP++ to support this will require writing a custom multi-pass compiler within the fitness evaluation loop. Expect this to take a competent C++ programmer three to four weeks of intense architectural work, specifically handling the dynamic memory allocation required when unspooling Ghost Modules on the fly without leaking memory. The strongest signal that this gap is real is that multiple groups studying length bias and reorder operators have continually written bespoke string-manipulation scripts to analyse phenotypes post-hoc, rather than engineering a native decoupled execution engine.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most persistent failed programme in this field is the attempt to use traditional crossover operators. Decades of attempts to cross over two Cartesian Genetic Programming graphs have consistently failed to outperform pure mutation, or have resulted in catastrophic fitness loss [cite: 4]. Because the spatial position of an active node depends entirely on the routing of the connection genes downstream, splicing the tail of one graph onto the head of another almost invariably connects active paths to inactive, nonsensical junk. Crossover in standard graphs is a dead end.

A specific retracted or corrected result in the theoretical space is the Reorder operator introduced by Goldman and Punch. They proposed Reorder to fix positional bias by physically moving active nodes toward the input side of the graph. However, Cui et al. in 2022 demonstrated empirically that the original Reorder operator possessed a fundamental flaw that often degraded performance on standard benchmarks, requiring a completely refined mutation strategy to actually achieve the promised gains [cite: 7, 10].

A massive standing critique of pure Embedded Cartesian Genetic Programming is that dynamic, random module acquisition suffers from severe early lock-in. Randomly compressing subgraphs into modules at the start of a run often encapsulates highly suboptimal junk code. Because modules are protected from fine-grained point mutation, the search space becomes heavily constrained by these bad building blocks. This method looked strong on toy problems like the Lawnmower problem, but it completely failed to scale to complex real-world arithmetic logic, which is why the EvoApproxLib results were achieved using standard multi-objective graph evolution rather than dynamic module acquisition [cite: 27, 31].

A broader methodological critique of the field is the pervasive failure to account for neutral drift when reporting algorithmic efficiency. Many papers claim that a new mutation operator improves search, when in reality, the operator simply forces the algorithm to take larger steps through neutral networks (plateaus in the fitness landscape where fitness does not change). If a critique was answered, it was usually by implementing Single Active Mutation to standardize the definition of a step. Where it remains unanswered is in the module acquisition literature, which has never fully accounted for how much of a module's success is simply due to it surviving neutral drift long enough to be useful.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the current landscape, a well-resourced newcomer should bypass purely random module acquisition entirely and aim directly at the intersection of decoupled linkage and machine learning.

Experiment 1: The Decoupled Linkage Isolation (Rank 1)
Feasibility: Highly feasible if you build the Decoupled Linkage Graph Engine described in Part 6. 
What it measures: It directly answers your anchoring question. By running the exact same evolutionary budgets under Condition B (Pure Reuse) and Condition C (Pure Macro-Mutation), you measure exactly how much fitness gain is derived from description length compression versus step-size expansion.
Falsification: If Condition C drastically outperforms Condition B, you falsify the idea that module acquisition works because it simplifies the code (library learning), proving instead that it works because it provides correlated macro-mutations that vault over fitness valleys.

Experiment 2: Transformer-Guided Subgraph Compression (Rank 2)
Feasibility: Feasible now due to the public release of the EvoApproxLib dataset and the methodology published by Galeta and Sekanina in May 2026 [cite: 18, 32].
What it measures: Instead of using a Transformer to guide point mutations, use it to explicitly identify and encapsulate subgraphs into modules. You would measure the time to converge on an 8-bit approximate multiplier when a language model dictates the module boundaries, versus random dynamic encapsulation.
Falsification: If the Transformer-guided module acquisition fails to outperform standard point mutation on highly nonlinear circuits, it falsifies the hypothesis that structural semantic priors (what a human or LLM recognizes as a "good module") are actually optimal for an evolutionary algorithm's traversal of a rugged landscape.

Experiment 3: Multi-Objective Length-Penalty Module Destruction (Rank 3)
Feasibility: Feasible using CGP++.
What it measures: Modules naturally protect themselves from point mutations. This experiment would apply a harsh multi-objective Pareto penalty to the size of the module dictionary. Modules that do not actively contribute to a fitness increase over ten generations are forcibly expanded back into raw nodes and subjected to high-rate point mutation. 
Falsification: If this forced destruction stalls the evolution, it falsifies the idea that early lock-in of suboptimal modules is the primary barrier to scaling Embedded Cartesian Genetic Programming.

What will NOT work:
Attempting to run classical Embedded Cartesian Genetic Programming with purely random module creation, expansion, and mutation on modern, high-complexity logic synthesis benchmarks (like an 8-bit by 8-bit multiplier from scratch) will absolutely not work. The search space is too vast, the likelihood of randomly encapsulating a highly optimized full-adder structure is infinitesimally small, and the resulting module bloat will consume your compute budget while the population stagnates in a local optimum. The field abandoned this approach for a reason; you must use either intelligent heuristics, surrogate models, or pre-seeded architectures to scale module acquisition today.

**Sources:**
1. [york.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOWIuTlQpGGaWphwAnonjgpt5VvBMdNVU79MfET-SAY7B04UIzNBcpUyhLdDh49_tmQS_l-yQ1QkXyQfoqojliU1BIBRcV5vxD-kv8tmlNoEvduCE1UsV_RWD6bmFlxsVgRMxnv6J2SffsHyxslW52yz7tlUOZlUKHIfl1IpwmDtwKLUZj1GaVzJji)
2. [scilit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEldKHAtn1UK57xt_AWTZG_tHGSzNBTwlTRZD7BuuHNot4uNpbFL_a6uVPf84bE9sEYJIb5I8S-THlWQxVqPSG7Qygrs9gGAPysv3kzWk-747TF6Hn367bhL4DgBlCr56x0bQtHdnM06TQbkeyHPzX1T1fyeDSQU2TmAg==)
3. [ucl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHG83XR2DT_ESAgRdodk3KZaYe3rDp4TMfzUULyZQN_9keZvl_w9Ngso9vl9UPPusc40lbnnAjmps-IctiXNcy4fBP9TRAB0FYT4WXLixRy6l8yvW0BWZtV88EgFMAnY5GBGULHak9DbA==)
4. [polytechnique.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwq2EOd7ruFv41xedERmzNoiKonYU37F1pLCFDWNrp8hoqze8Oz7utTZVR1VieaRFBkDHMBM8HNPO4aPdT9VC8_DFmtIuWn7AJiHW0MWpI9rvgGwaFgYObLDG3FAd1ujTPk4XDobnLS_BquGAestSx17me9CFcp1G4DLOtELc_K3-rPWojB3BwZ_HUk6XTALAF)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDfkLyUxRdoB18x0oSgR6zTiB38z4MSdv62CjZek8-EyZDrQw2F2Rerwx2BZn8CtMpMitkCwg4O1PNo43Bb28XKkGW2OW7fHDkheUWoAV4A0tXtnAtNBpRBq1vIUeLtgZxQBWTRdU=)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYwUziFpuXFCuXOFlU4WlChHpPCP-aUzbhzI3UmbUXwlydphwOxqaBEzCbBTf2LBTLtWlYme_7v0xiVEIGJ4Vjogi9Q16vZUlhuxVSXCUzDAjBYRfmbjmixbqfPMAOnLeXns-p6zZf8V7QywCCVg0WUuSnO1keVCqaDlskfDHs2rYU6bS9hhUrQ2pvaLHBYZKKpM3ahoZRfKnS)
7. [uni-augsburg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGG2dlPMZKynGq1YNLfi4ypthlm-9rYi0shZanow5d7VuEN0j6od78IzzaJesT9eavi2vrCnREMkwQvtHgu7wDZJHkKgQqLpPwDEJsZ7O-MmNoHp8junWXgtG_wtt3l5Z7kptRm284Py5lJIYPic61V6hHsp7LMZulO)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhrWYUm7m-E_9WafgUX-R8Ccig10-S4faU6c8RzpOMbdmIZC2MhP46MFqSLjojoqoOdLJGt2iwL2ipIIdykPwUwego4UWB9OuV_qm5MTviX9pWVjtv_-He_n64k-dpx7FuKLhpzxwUHg==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoGj8_NvFoKZ0Sy4dP0oyp8gr8zPqFL7YNrxpeOCoowuEQ7Y6w_xqogYsg2r6tP3XAap0mEnsSKdcOe4dwNPTz9MqYYcLEpAKcZTA2Th1XGdEoA22DX-d1Nw==)
10. [uni-augsburg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfn-7b2GsFiEk1sxKd3JbBkNjKqBfA7K8Vd7ivg5naE8ae59MgeDKygINrU1X-_MDYldhtXLPSIaPXD_sFWiOEAHh-Pp1hgBwYWbpPrHu5gJvPnu4xCG3p4ZcC92NKzE0GgIQ5dYqC0f_wFKylkKyk-T7PwhTJFJf2sOklJQ==)
11. [uni-paderborn.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrlpjgKqJNDTfsXImmNVsFNy6rAY_u1mM7WgKhjTgVT56sf3ZEO2_O9jM0nkJfTqX-oP9DsJT-H1kaTDp-XHuQx90abGdvg2P0tZ1Uf8bDhimt8P6s7Uv7nAZ9fTeJyEuOUF4J3dCEO08hLPqWCfA3Lv8z0v-enFOPSRxfS-s=)
12. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKriY42P7-t_dbXOTKCqChXSr8lQMNLm9-J7mv9JmZKi0t4MW8UF1jRKock4ecxFYpkCUJevFktw66PDZekQMEb3E2xDccIAhAAXvpkOouSId1B4-8GBBpd-CEKYN96fw=)
13. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6pSPcDt6I2SvFgZ7JgwAzGTYnC6JFcJngGLHj8Cdw-7qmS9UnlWv-nw5D082HfAceG73CQ5MJuHdj1RdfWEP7LyTh9GD69kuuKYT40SO3Ccim2NLyZi6oOLJE5NN6wGZL_p4ye8UdcdfNzasbQ0w3N6sVc8-gxas31fHGfNlGRmiUSz9GFL462CDI1Hn7Tv2QDurxA4WP_1YiCypjdoFbbuNoFw3nyquyRjreRN4VUoc=)
14. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQlVGUymkGx1PcZmdwBd6SXGOgJrjy-oONde-QBAeEXalOaUB3GAgU0tTA7DVyVibh4KTNlyOxKQIpTAg7JUshJBw4u8t04Sjsm30BRSO27QH_9YM1jR3APHs=)
15. [meteo.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcDAuBXoYTqrrK0eOcGZ4BmldKu3eZe52G_EhN4IXeLyciFv-0cCzPeFNyFw_r07vtJhHgPFUHyJBc96W2NbCjq9zLmWS2HBiXGpvlNL9iV8hMev8HaAYQaALnCxIPymFuM0z6Q4AaDJqWxKE758j1NubsLLuGTBCH3F4=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcLqOND9AHbXZZGAWIXKD1JZqdc2e_5IlbeKNgrXXiPYec-sSfKBIG26Hc78k0vCv5YN6x29RD7SmRT0FmcckvezGW1DsMqZIDPlO0nbx7I1XllpNBo_MyCQ==)
17. [uni-augsburg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGA-jE5iifzXA4x-qMiwxszIjVQf3Q3wb3dONV1x5GFRAvWVGeaThzepQX7p_lUdlAq8iW030TunVE5VXI4ZrbXBy3yIevdiHxXARH6bUICfwn-y7xHsOmlp_fu7mL7Dv2fbFTeUrOjkpeNnaC57ACv4Fwq4ZIXa8g_aHgq4vxa5M2XvFyC)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa2JJLz8oad0jrn-Oz6F-R9sFCDAZlvJho2sHmlJPsedq3hnjUZWg6EkXe_rNTQllSYJveDuSumXjXkWyBx-WseRSfRVy6KDHkLjYdtTgfsshMsTVzxQ==)
19. [theses.cz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO4aBpO1xpcLX4iPTdEPIp6QxpBcvTVId5yF704A6TCRyN8XGJfs5iLQ_3LfAMh5PwgeVZknCciKbmQ_6Ge1xsxicNvo0Ojpwqy2k1FM4zdbhF3-euQsIZOnJoz4s3QNnEZYsg)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwq6PRB5ahHY_dZEUPhNJ6KFTD0VLI4VtPS4aqUGuw30MApzH1YxiQ4JnjFovlfYrA2fG6Att4fW5_4YnJw4BVR24kfYiZByBpYZu3bE4L5n2wCNa_tvsIITZxU09oAcrmQnN2BHrSrcM-CTCpMNp_2JPpTO77HNUfkBsLLvaZdCNm09-NY_9SPOTh_4HKD_5-qYzkxNhr3pnsJnJNjLEel4MyQcFU7mDH_76nJw4GqtM=)
21. [mcnallyjackson.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE70npNL9Dw_ZdfhGxPnsmhYZXbMngO64WpZAJZ0lrL8kcH7OcRWLDgNzhJ-lH4iz7ZZNelLhXtaKB-8GkDBZpvRMhMW-I7aFyBK4w5KObad8YIjhZpOGX2fzcR-5Y4XgHBs0U=)
22. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgMernCaC80DZOd2Rj346W485rhjijfTCbNZJBhg0AmXm80xGQQZR1CIAL90FYcJ-P6Xlf5rrmmLbOIy0YG8uW0QfUK_fodmBIVbhsufKR22zDvp3q-ZH8LkVeMZIorBbjI-KogBmztCg7bbPpge0GcjRlIAXB_gpf-WYOU3rkSJOtGHih_YVMPiG4dh9eUiCOu7UrZ0KRVRmCsJa-oA==)
23. [cgplibrary.co.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzDaN1yQGjuRmR5Ip0Gu6ZyG2c8MImii0owZEMBBGuvnZ8KGKuzjIsphysx8611nfvaZIy0QxiUR8ROYcDhNEUvpee7Ce4G_cU32YV65CXK2Ay)
24. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHbN6iN7xaNlVxT-wRMa8ameNzE3BleV5VoORbXfyT0ATVkVVnpm2tRvn2D6jrjMUylY3VGrhbTyLl5BZ1FiZwek0H8Y2-BdHd8bS93NxUW9oWyxO8UW8R-rdzDZWuBPE7WX-UPLUgxwHp5uXU4qvaQt9WAZ4ghm2VFjn8Su0Qj6nz--VcS8QYkctD6ZdtbnSTXAMlHkFTwx6-pEvJynsfmxtwigLM7TDqj2e7B5kne7Z27Jp82Q-O)
25. [stackoverflow.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7Wr9VbZsr9pnVybqivUcxF4y4-TGWeXSDnZ18MXMJN4IQdufHNBqBC30XfwZDwNd8zrPY0IbffTnhQidl58N66Ss2qFrZqxBkCrDWh-sbNdcFPTFMCvzgrV_EatgFQTrC1AABJHRdI3txGZ8kmOw1LCznhD1N05Hw_UPzvPcP_tQykoNsXkheF6zMCZn-D_nClbBezHtS_qi_vxKIzGHIWyjxJcfg45M5DRFKMgts)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq6OHkxjU-eE7tGq-Q2YhyJNVlRIQfhzdbjFlEjSjVeGD36MFrsyRYJd2b5UhS9e8lxq7iqAcJ1HWERegpPOq2YbGAzAxHVkb3AyBdSqQ8G07b-oO8ZXws7ttFS_u_ELLnMWIe)
27. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFq78bTZvMFrHLktqjKbdpS-6I0jieMCzZLRDlbagA5x0srxSHUf9V-QZgEjQ9dA6Xw6IxnUFrSoRxjUEcgDHSyOnz0PiUQ4jTRqRNJQ_V-nBtF_QibBo2eBFZA_98a8LMCmP0yL75nExV3Ng3LLqNdYK8=)
28. [vutbr.cz](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1fwzq2tyOYR9cnG6a5KbCox3eN5ACkAR4BSl53nezLzL0rgM3ntlL5ShyQxWCs5qoPksjNzEo08HBPvIxZsNNnIg_T57U-tRI4EgY8H6Blmhxeky62B6RaDLvXg==)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_paYmUOU0vC0qNIcSVfLurs8mYyNievl6x5ZsIpwReM9sf5ThkOcE8p9bdHcvD5WzbG5cyIjiYJM4NXyLH4b3VpjruodJVhpyUM-fpAkdHg==)
30. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkOQ3CFJeLlH7AirinE5Z8MQbW2-t4C-EbeRTbjEkkzJoALF1aVly-FXGVqdmj3ZEkH6KlVTIPJSj2SLeP113JQMjMvimq2-3d4WQTXw3dnYgOPivrq0NMzyt_b3GchWTdIoZjCA3d_Q==)
31. [isqed.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGk4f6RZrHbUy1B2IR8PlRL-lSMaLOvqPLMuABUgAoaXKLmg8TqfFDMc7J4pQFuWzB9lCjeXVT7Y_KsFFZp7vSXTHNBgaKlraGcbE8wetS_82qRDb7E-3Q7FQR87P144alYModtD3OocPtzdos3NUZc)
32. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDN18VcWUQ9QCfHietmlr9y9716Q_uz4KHI_Q28rUKHkvQXO4DJaL9ADiFXhZ5iNtZ4g4IfqKq75ScaAS6xJLMmfCVhCjaA4Oy233usQqQo3Zl-epsl_0wQj7-L2-osfAdlt-y9ap4pGraVZ0HLkwwMFNO5TTxm8OObWBN1RvBKbam3r34qSCD-xviMHkbTrOoQis9cQ==)


# Prompt 08: Evolutionary Developmental Systems (Evo-Devo)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdKS1NlYXVtV0c5Q0ExTWtQb1BxZzZBMBIXSktTZWF1bVdHOUNBMU1rUG9QcWc2QTA
**Elapsed:** 365s

---

# FRONTIER PRACTITIONER DOSSIER: Evolutionary Developmental Systems (Evo-Devo)

The study of Genotype-Phenotype maps using Boolean networks sits at the intersection of evolutionary biology, statistical physics, and algorithmic information theory. The core premise is that the developmental process itself heavily skews the raw material upon which natural selection acts. Research suggests that this structural bias is not merely a constraint but a primary driver of evolutionary trajectories.

The following dossier provides a comprehensive, technically specific roadmap for a computational scientist entering the field of in-silico Evo-Devo in 2026. It outlines the foundational literature, modern GPU-accelerated software stack, authoritative datasets, and the standing methodological critiques required to run load-bearing experiments.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of Evolutionary Developmental Systems, specifically through the lens of Genotype-Phenotype maps, has increasingly merged with algorithmic information theory and complex networks research. It focuses on how the structural properties of developmental algorithms constrain and direct evolutionary outcomes. The primary phenomenon of interest is "developmental bias" or "phenotype bias," where the mapping from genetic space to phenotypic space is exponentially skewed. 

To address your specific understanding of the method: your description is mechanically precise but requires a critical correction regarding biological definitions. In classical and modern Boolean network models of evolution, the genotype is strictly defined as the network wiring and the Boolean rules (the truth tables) assigned to each node, not the initial state [cite: 1, 2]. The initial state represents either the environmental conditions or the embryonic starting condition. When you sample different initial states over a fixed network, you are measuring developmental robustness or phenotypic plasticity. When you mutate the wiring or the Boolean functions, you are traversing the genotype space to measure mutational robustness and evolvability [cite: 2, 3]. Furthermore, while K equal to 2 uniform random Boolean networks do sit at the critical boundary between frozen and chaotic regimes, real biological networks achieve criticality not through random K equal to 2 wiring, but through highly canalized Boolean functions (such as nested canalyzing functions) and scale-free topologies [cite: 4, 5].

What is SETTLED in 2026: The existence of massive phenotype bias is no longer debated. The distribution of genotypes to phenotypes follows a heavy-tailed, Zipfian distribution. A phenomenon known as the "arrival of the frequent" dictates that phenotypes with large neutral networks (many genotypes mapping to them) are overwhelmingly more likely to be discovered by random mutation [cite: 6, 7]. This bias strongly correlates with algorithmic simplicity; phenotypes with lower descriptional complexity are exponentially more likely to appear than complex ones [cite: 6, 8].

What is CONTESTED: The absolute supremacy of developmental bias over natural selection in realistic population dynamics. The "arrival of the frequent" is a non-ergodic effect that depends heavily on the assumption that populations do not have infinite mutation supply. A live and heated disagreement exists between the structuralist camp (arguing that mutation bias and phenotype bias dominate what forms appear) and traditional population geneticists who argue that in regimes of large population size and high mutation rates, selection can always "see" and fix the fittest phenotype regardless of its mutational frequency [cite: 9, 10]. 

What is OPEN: Bridging the gap between discrete Boolean attractors and continuous, spatially extended morphological traits. While we can perfectly measure the Lempel-Ziv complexity of a binary cyclic attractor, mapping that mathematical object to a 3D physical body plan without losing the rigorous traceability of the Boolean model remains a frontier challenge. 

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Kauffman, S.A.
Year: 1969
Title: Metabolic stability and epigenesis in randomly constructed genetic nets
Venue: Journal of Theoretical Biology
Identifier: DOI 10.1016/0022-5193(69)90015-0
This is the foundational text establishing Random Boolean Networks as models for gene regulation. A practitioner must know this to understand why K equal to 2 became the historical baseline and how the concepts of state space and cyclic attractors were first mapped to cellular phenotypes.

Authors: Schaper, S., and Louis, A.A.
Year: 2014
Title: The arrival of the frequent: how bias in genotype-phenotype maps can steer populations to local optima
Venue: PLoS One
Identifier: DOI 10.1371/journal.pone.0086635
This paper formalized the "arrival of the frequent" phenomenon. It is mandatory reading because it provides the exact mathematical framework showing how phenotype bias can override fitness differences in evolutionary dynamics, setting the baseline for all modern mutational bias experiments [cite: 7].

Authors: Payne, J.L., and Wagner, A.
Year: 2014
Title: The robustness and evolvability of transcription factor binding sites
Venue: Science
Identifier: DOI 10.1126/science.1249153
While focused on binding sites, Wagner's broader framework of neutral networks is defined here. You must read this to understand how neutral paths allow populations to traverse genotype space without fitness penalties until they become adjacent to novel phenotypes.

Authors: Helikar, T., et al.
Year: 2012
Title: The Cell Collective: Toward an open and collaborative approach to systems biology
Venue: BMC Systems Biology
Identifier: DOI 10.1186/1752-0509-6-96
This paper introduced the Cell Collective, which was the first major attempt to aggregate biological Boolean networks. It is essential for understanding the transition from abstract K equal to 2 random networks to empirically grounded biological models [cite: 11, 12].

CURRENT SOURCES

Authors: Dingle, K., et al.
Year: 2024
Title: Developmental bias and the algorithmic nature of evolution
Venue: PLoS Computational Biology
Identifier: DOI 10.1371/journal.pcbi.1011893
This paper bridges Richard Dawkins's Biomorphs with algorithmic information theory to demonstrate simplicity bias. It is crucial because it gives the formal proof that simple phenotypes are exponentially more likely to be generated by random mutations than complex ones [cite: 6].

Authors: Pastva, S., et al.
Year: 2023
Title: Repository of logically consistent real-world Boolean network models
Venue: Bioinformatics
Identifier: DOI 10.1093/bioinformatics/btad158
This paper introduces the Biodivine Boolean Models dataset, which corrects historical errors in the Cell Collective. A practitioner must read this to understand the specific logical inconsistencies that plague older models and how to properly curate a modern benchmark suite [cite: 11, 13].

Authors: Kadelka, C., and Coberly, B.
Year: 2025
Title: BoolForge: Random Generation and Analysis of Boolean Functions and Networks in Python
Venue: arXiv
Identifier: arXiv:2509.02496
This paper introduces the modern standard for generating Boolean networks with specific structural properties, such as canalization. It is vital for escaping the trap of uniform random network generation and moving toward biologically realistic model sampling [cite: 5].

Authors: Rozum, J.C., et al.
Year: 2021
Title: Parity and time reversal provide new insights into the key regulatory circuits that underpin the biochemical decisions of cells
Venue: Science Advances
Identifier: DOI 10.1126/sciadv.abf8124
This paper describes the stable motif approach to finding attractors without exhaustive state-space search. It is mandatory for understanding how to compute phenotypes in networks far larger than the traditional N equal to 20 limit [cite: 14].

Best Survey:
Authors: Uller, T., et al.
Year: 2018
Title: Developmental Bias and Evolution: A Regulatory Network Perspective
Venue: Genetics
Identifier: DOI 10.1534/genetics.118.300995
This is the single best survey integrating the mechanistic network models of Evo-Devo with population genetics, outlining how bias and selection jointly influence evolution [cite: 15].

PART 3. SOFTWARE I CAN ACTUALLY RUN

The software landscape in this field has historically been a graveyard of unmaintained C code and ad-hoc scripts. By 2026, the community has largely standardized on Python, with heavy compute offloaded to CUDA or specialized symbolic analysis engines. 

Name: BoolForge
URL: https://github.com/ckadelka/BoolForge
Language: Python 3.10+
Licence: MIT
Activity: 2026
Verdict: MAINTAINED
This is the current gold standard for the random generation and analysis of Boolean functions and networks. You will use this to generate your genotype space [cite: 5, 16]. Its primary experiment today is generating constrained ensembles of networks that exhibit precise degrees of canalization, rather than uniform randomness. Known gotchas: while it handles generation and structural analysis perfectly, it falls back to slow pure-Python implementations for exact asynchronous attractor computation if you do not compile its Numba dependencies correctly [cite: 16].

Name: cubewalkers
URL: https://github.com/jcrozum/cubewalkers
Language: Python (with CuPy/CUDA)
Licence: MIT
Activity: 2024
Verdict: MAINTAINED
This is a CUDA-based simulator that evaluates the dynamics of massive ensembles of Boolean networks simultaneously [cite: 3, 17]. You will use this to develop the genotypes into phenotypes. It parses Boolean rules into CUDA kernels. Its primary experiment is running thousands of independent walks across state space to map attractor basin sizes instantly. Known limitations: It requires a compatible NVIDIA GPU and a strict installation matching the local CUDA toolkit version; failing to match CuPy with the correct CUDA driver will silently crash the environment [cite: 17]. 

Name: pystablemotifs
URL: https://github.com/jcrozum/pystablemotifs
Language: Python
Licence: MIT
Activity: 2024
Verdict: MAINTAINED
When your networks exceed N equal to 50, exhaustive state space simulation using cubewalkers becomes impossible. pystablemotifs uses network topology and symbolic logic to find attractors analytically [cite: 14, 18]. You use this when you need the exact phenotype of a massive biological network. Gotchas: It is heavily optimized for asynchronous update schemes and models with clear feedback loops; highly chaotic random networks can cause the algorithm to stall.

Name: CANA
URL: https://github.com/CASCI-lab/CANA
Language: Python
Licence: MIT
Activity: 2021
Verdict: DORMANT
Historically used to extract canalizing redundancy from Boolean networks [cite: 4, 18]. It calculates the effective graph and dynamics canalizing map. While famous for establishing redundancy metrics, it is effectively superseded by BoolForge for generation and structural analysis. It is dormant, and newer versions of Python 3.11+ often break its older dependencies. Use its algorithms as references, but rely on BoolForge for live code.

Name: OEE-metric
URL: https://github.com/amahury/OEE-metric
Language: Python
Licence: MIT
Activity: 2025
Verdict: MAINTAINED
A highly specific pipeline built to characterize open-ended evolution in Random Boolean Networks via undecidability mechanisms [cite: 19]. It provides a full reproducible pipeline for CPU/GPU simulations. Gotchas: The definition of open-endedness used here is heavily tied to residence-time-weighted sum of cycle lengths. It is theoretically dense and the metrics do not easily generalize outside of their specific mathematical framework [cite: 20].

PART 4. DATA AND BENCHMARKS

The field relies on curated sets of empirically validated biological models to test whether theories derived from random networks actually hold in nature.

Name: Biodivine Boolean Models (BBM)
URL: https://github.com/sybila/biodivine-boolean-models
Size: 230+ curated models
Licence: CC-BY-NC 4.0
Use: This is the authoritative benchmark suite treated as ground truth by the field in 2026. It contains Boolean networks ranging up to 300+ variables [cite: 11, 13]. It is used to evaluate attractor finding algorithms and to measure whether biological models exhibit simplicity bias. Known saturation/overfitting: Because models are manually constructed by biologists from literature, they suffer from survivorship bias. Interactions are often only included if they are known to stabilize a desired phenotype. 

Name: The Cell Collective Database
URL: https://cellcollective.org
Size: Thousands of models (mix of curated and user-generated)
Licence: Mixed / Platform restricted
Use: Merely popular, not authoritative for algorithmic benchmarking. Historically the largest repository of Boolean models [cite: 11, 12]. Known contamination: Many user-generated models contain logical inconsistencies, unverified initial conditions, and ad-hoc modifications [cite: 13]. If you run global graph metrics on the raw Cell Collective dataset, you will be measuring the noise of user error. Always use the BBM dataset instead, which mathematically cleansed the best of the Cell Collective.

Name: OEE-metric Benchmark Sets
URL: https://github.com/amahury/OEE-metric/tree/main/metric_validation
Size: Small subset of specific models (B cell, T cell, Cardiac development)
Licence: MIT
Use: A narrow task collection used specifically to validate novelty indexes and open-ended evolution metrics against elementary cellular automata and select gene regulatory networks [cite: 19].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to prove you have mastered the toolchain is the demonstration of Phenotype Bias (The Arrival of the Frequent) in Canalized Boolean Networks. 

Software and Versions: 
BoolForge (latest git main branch as of early 2026) for generation.
cubewalkers (latest git main branch) for simulation.
Python 3.10+, NVIDIA CUDA Toolkit 11.8 or higher.

The Recipe:
1. Use BoolForge to generate an ensemble of 10000 independent Boolean networks. Set N equal to 15 (small enough to be tractable, large enough to show complexity). Set K equal to 3. 
2. Instead of generating uniform random truth tables, use BoolForge to restrict the truth tables to nested canalyzing functions, which mimic biological reality. This is the genotype generation.
3. For each of the 10000 networks, define the phenotype as the steady-state attractors under synchronous updating. 
4. Pass the ensemble to cubewalkers. Generate 5000 random initial conditions (initial states) for each network.
5. Simulate the trajectories for 1000 time steps. Extract the final states from the GPU memory. Group states belonging to the same cyclic attractor.
6. Calculate the frequency of each distinct attractor (phenotype) across all initial conditions and networks. Plot the rank-frequency distribution on a log-log scale.

Seeding and Replicates:
Use a fixed random seed for the Boolean logic generation (e.g., 42) and a separate seed for the initial state generation (e.g., 100). Run 5 independent replicates.

Compute Cost:
Generating the networks takes minutes on a modern CPU. Simulating 10000 networks with 5000 walkers each for 1000 steps takes approximately 1 to 2 hours on a single NVIDIA RTX 3090 or A100 GPU using cubewalkers [cite: 17].

Expected Result:
You will observe a Zipfian distribution. The top 1 percent of phenotypes will absorb over 80 percent of the evolutionary probability space. The robustness will scale logarithmically with frequency. Compare this against the foundational curves published in Schaper and Louis 2014, and the algorithmic complexity bounds in Dingle et al. 2024 [cite: 6, 7].

Three Most Common Ways People Get This Wrong:
1. Assuming structural identity is simple. Two attractors in different networks might represent the exact same logical phenotype under a permutation of node labels. Failing to account for graph isomorphism leads to heavily fragmented basin sizes and destroys the power law curve.
2. Synchronous update artefacts. Synchronous updating forces simultaneous transitions, creating long, artificial cyclic attractors that do not exist under asynchronous or noisy updates. If your dominant phenotypes are entirely long cycles rather than fixed points or small cycles, you are measuring a synchronous artefact [cite: 3].
3. Undersampling the state space. N equal to 15 has 32768 states. Using 5000 walkers only covers 15 percent of the space. You must verify that the basin distribution has stabilized.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments, there are two major missing components in the current open-source stack that serious research groups end up rebuilding privately.

1. The Attractor Isomorphism Engine
What goes in: Two sets of cyclic attractors from two different Boolean networks.
What comes out: A Boolean scalar indicating if the two attractors are identical under any valid permutation of node labels.
The hard part: The subgraph isomorphism problem is NP-complete. When you are simulating mutational trajectories, a mutation might duplicate a gene, rewire it, and change its label. To calculate the true frequency of a phenotype across an evolutionary simulation, you need to know if Network A's attractor is functionally identical to Network B's attractor. Currently, researchers rely on heuristics (like comparing the network's macroscopic density or specific key node values) rather than exact isomorphism. Building a rapid, GPU-accelerated attractor clustering engine would be a massive contribution. 

2. Continuous Morphological Translators
What goes in: A Boolean attractor (e.g., a 100-node vector oscillating between two states).
What comes out: A spatially extended tensor representing a 2D or 3D physical trait (e.g., a concentration gradient or tissue deformation).
The hard part: Evo-Devo fundamentally cares about shape and form (morphogenesis). Boolean networks abstract this away entirely into binary steady states. Several groups privately build ad-hoc bridges where the output of specific Boolean nodes dictates the parameters of a secondary continuous model (like a cellular Potts model). No off-the-shelf framework standardizes this mapping. Building a library that allows a Boolean network in cubewalkers to act as the direct gene-regulatory controller for a spatial cellular automata would bridge systems biology directly to morphological Evo-Devo.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

This field is heavily self-correcting, and several initially promising directions have collapsed under methodological scrutiny. 

The K equal to 2 Randomness Failure
Early research in the 1990s and 2000s heavily leaned on generating Boolean networks by drawing uniform random truth tables for K equal to 2 inputs, as this mathematically guaranteed a phase transition between order and chaos. This programme largely failed to predict actual biological properties. Uniform random networks exhibit fundamentally different topological and dynamic properties than evolved biological networks. Biological rules are canalizing; they have strong structural hierarchies where certain inputs override others (e.g., if Gene A is OFF, the states of B and C do not matter). Discoveries made exclusively on uniform random K equal to 2 networks are now routinely dismissed as artifacts of the generation method [cite: 5]. This is why BoolForge was built to sample from canalizing functions instead.

The Synchronous Cycle Artefact
Historically, to save compute, researchers updated all N nodes in a Boolean network synchronously. This led to a large body of literature categorizing the complex cyclic attractors of these networks as analogs to the cell cycle or circadian rhythms. This was later shown to be measuring an artefact. When identical networks are run with asynchronous updates (where nodes update one at a time randomly), the vast majority of these complex cyclic attractors instantly collapse into simple fixed points or much smaller trap spaces [cite: 3, 21, 22]. Asynchronous or noisy updating is now considered biologically mandatory. If an evolutionary phenomenon relies entirely on synchronous cyclic attractors, it will not replicate in vivo.

The Infinite Population Size Critique (Svensson's Critique)
A standing methodological critique against the "arrival of the frequent" (phenotype bias) concerns population genetics. Critics argue that while developmental bias generates simple phenotypes more frequently, this only matters in small populations or low mutation rate regimes where evolution is mutation-limited. In a massive population (like bacteria), all one-step mutational neighbors are generated continuously. Therefore, selection acts on all possible phenotypes simultaneously, and the fittest will always win, rendering developmental bias moot [cite: 9, 10]. The counter-argument, defended by Louis, Payne, and Stoltzfus, is that genotype spaces are so vast that even bacterial populations cannot explore the whole space. "Arrival of the frequent" remains relevant because the mutational paths to complex highly-fit phenotypes are structurally blocked by the sheer volume of paths leading to simple, moderately-fit phenotypes. This debate is ongoing and represents the fault line between Evo-Devo structuralists and Modern Synthesis adaptationists.

Lempel-Ziv Complexity Saturation
Attempts to correlate phenotype bias with complexity often use Lempel-Ziv (LZ) compression algorithms to measure the "simplicity" of an attractor. This method failed to scale. LZ compression is heavily dependent on string length; for small networks (N less than 50), the binary strings are too short for LZ to provide a meaningful entropy estimate, resulting in massive saturation and step-functions in complexity plots [cite: 6]. Researchers who rely blindly on standard LZ libraries for small Boolean networks are measuring the limitations of the compression window, not the true algorithmic complexity of the phenotype.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the tools, the settled theory, and the standing critiques, here is what a well-resourced computational scientist should actually build and execute. 

Rank 1: The Environmental Fluctuating Evo-Devo Experiment
What to do: Evolutionary models typically evolve a GP map toward a static target phenotype. Using cubewalkers, construct a genetic algorithm where a population of Boolean networks is subjected to a fluctuating environment. Model the environment not as a separate variable, but as periodic forced interventions on a subset of the Boolean nodes, flipping their states every few hundred generations [cite: 3].
Feasibility: Feasible now because cubewalkers allows for probabilistic update rules and control interventions on GPU at scale, which would have taken years of CPU time previously.
What it measures: It measures whether developmental bias (the inherent skew toward simple phenotypes) becomes stronger or weaker when a population must survive in alternating environments.
Falsification: If networks evolved in fluctuating environments do not show a statistically significant increase in the size of their neutral networks (robustness) compared to static environments, the hypothesis that environmental variance drives canalization is falsified.

Rank 2: Simplicity Bias in Asynchronous Empirical Networks
What to do: Cross-reference the "arrival of the frequent" strictly on the BBM empirical dataset using asynchronous updates. Take the 230 validated biological models from the BBM dataset [cite: 11, 13]. Mutate their wiring slightly to generate a neighborhood of biological-adjacent networks. Evaluate their attractors exclusively using asynchronous updates via pystablemotifs or biobalm [cite: 22].
Feasibility: Feasible now because biobalm and the BBM dataset provide the first mathematically clean sandbox to do this without getting bogged down in the synchronous artifacts that plagued earlier random network studies.
What it measures: It measures whether the simplicity bias discovered by Dingle and Louis in abstract Biomorphs and synchronous random Boolean networks holds true for actual, messy, biological asynchronous networks.
Falsification: If the mutated empirical networks produce a flat distribution of phenotypes, or if highly complex biological attractors have larger neutral sets than simple fixed points, the universality of the simplicity bias theory is falsified for higher-order biology.

What will NOT work:
Attempting to scale uniform random K equal to 2 or K equal to 3 Boolean networks to N equal to 10000 to "simulate a whole eukaryotic genome." This will fail. The structural properties of random Boolean networks diverge wildly from biological reality as N scales. The networks become either completely frozen or hopelessly chaotic, and the cyclic attractors stretch to lengths that exceed the heat death of the universe. Compute is not the bottleneck here; the topology is. Without integrating biologically realistic scale-free topology and nested canalyzing functions, scaling up random networks simply scales up the noise. Ensure your foundational generator is constrained by biological priors, using tools like BoolForge, before scaling up the node count.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgR03y5mFYKU98ZeOvEGR1nIeE1IapmLHKiNWAy0WCHujPA4Ie39TqGoSdlLySEZAvLRj3OFtL908S7qOsfJqWC9z-I1I4UFD3LCuLcM-PyUWnIOEJ_vF8jh2pZsY8xjuHIY6o_RZyR4hHfyUkLr1BPuy3CBv0V8TN7AAvBW8pllqlc30p1a29oDBLOkB7Uw_hLci5Ye5nxMOmpBkzihu8sjLFEqzuPw==)
2. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDFbgs6IEo4E4vK-DOIleJYGjJBkF3on4lP3OFuqoZggf-CpIj33aopijI_0AsUOLYphdgLwgVYPLoNveNXkKieBfef8irnVY4BanzWtZyuz3PSkbUS1NA56fMXCjys89vOkQXxqQ=)
3. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6aqrMaEg1QWnsDmn7mPTPuQ_nEWSeuxumHDeoHArxdIaumBrGrbttBsGKwh0lBBfi3Hj0l5wAk8KGcwv9lOwmFojYMN_iPIYSdL_7ZEabfjd4LxXqwBdFAjN5BJC378v1Tv2CCf8G)
4. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAtRuFZC5xl3J9IfnEt8l5G7rMmvNoG-UT3RFOzcxpFjOcVEFmkPOgFa8lPmDdm2dk_rG9GJPV6ILm2tE43uI628cYT6NAVeoEvGYkKzidUmnJhW5dUC9I1OtZ0K_RY2t_p1IJF7V955cM5QG8sEtLuzX8V2GxWjIt3XP0Ic3tKBd51S8I_QDtMzmR)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXhRRWZaONfqTAfGBY_KH3thIhsBv4kKMSFUoazmDT7-q4a4CAF7Fx23yU9NKX2KmbLu9lFmhok6XfU4yhewsdEYVbJXkmHtIqybEkXP_V6PJmGtrmzD4a)
6. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxP1VDv5srz3AlU-rLx6Tg5TGZHhKxKXnyWlr-Iks07bI1NgyEQ4Oy5XKpTwrimRIxT6gV-vBJYcasKOd3SIsyTAFGRnW2J4NMrO0KIhrkfpTwbDq8G5MZwKurRnfIjR80Fvf0PfQ3vhfwEspXkz4mCl19BiWhlSCLny7ncZXcrlUJYA==)
7. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpe7nlR9Z8dalvaZB87fIkyVowlNzkCehYn0fjl4tTS-WERsRlUVaiOYX5IZ-qHFNW5vlEYpeG1_kIhBqmFrTe4w534CBhoyLlsqnpSvCrSAhD2RBwf5FEEr2tbxVR4rQtx6Fu_JZhuq-y7sFpXw==)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEroDj6OIhdQR6EOySHOE6Gd9nF2gkXlxzdfzi1dW_y6dBal8OM3LYsKwjc-0hYlStRpdXsBciGI-QtQi0ipUjrjVJ6hD9sRisMIA2w-VeUBAAxDD76TO_8Im7bI5aZj7e6H3sd-KUN3RUmUaRdWjaFctYV7HNb9kOmGEfRx8EVegadR2a9qAZNxiu_diIMsM6PIMTqTP_96LaYmFmeklAi2VmuVIIUYjXGj69GVn8Au7VphJf8pxNUFXfxPxp)
9. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX6brwfWtc7tC_J-hPjDLCIj9KWsM-0BucLNr0CnDJE1UAXc0rHgymFQxaruZDcV9L3ao-4FIawbyg20imlT2A3orvhvZgV4odosnKbnd7fv5j1TfKsAEVdb7uUVzS3JPtIw2ZEb8NuUjnX1bodw==)
10. [molevol.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEP7ygXFvonGINsKYZa3usvLyUlOBJXVSkIj0RF87CjE4qdxbV7qSjwmsBHcy1byrcVt8b0Kq3hsjglv2h32yyKX9irHYu0Tb8FjsL3GDhHN1bQVwD4fyKoGMm32reT9wE6WUOCOrjLalMtnBcA6302APQYuPZbOpmF_qPFmLEgLk=)
11. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh1tNpsPgWYIBw869jNDL6P3I8vGRQx0gNN__0v4YuzQWEaEvZZQEtSQft9HyR3jAtcuj8sAdsk_9hmIema90qFzTRb85e0Q5WquH8CREpN_CwzJfntPHcgQgLu-fPl3K3n1TA9gpS8gec_MU_kNrv9uyqfkBAgvv0ZA==)
12. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG36l24vQfEpSVang9M8IGS9j_NdRY7siKyi3Fbwxiv_sV80RYFrsXBQN1P1xFwxksCkwl_gWxGPqqRM38pu0DO1ESgqUGa42YHvg21IN5YuX26yHg5JqnSB9WykvuLFy8ZG8kqENE=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjQwup8zoLsd3rqXwAgYq3mF-DiwiuJx8QyT-5xjdxyQA1on3dhUnyqiWbvivQkRyjNoITA-27huqKarLpyG1uhFazEoYD2_1m_0yzihsa61RGGRTlJm8fVuvzVW1V2xgSMzFn68rYQzJ9U5-7zWmGdU9XXtyRXFk7juss1hWOXUyzBNz46wVuYAs1eMVrk_mPxqGz-UWakWQ99IzjOBNCJT0P4423IAtAK7XZ)
14. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIHHnVNI25vUoZqYXCO_kKIO-ZfhGf_QylzOaB9XBODBTqg1KDN7x2xa1DN0FM-XeejLGcIzSkICihCI1Rcg8bn5k0y3BOdpOr26rXVbkG)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUEAWVcDVEZi5MfqXeNK8UWo4DtctIGiT-9_Caj7HVlYc5TaQ3Z2937glOEkmVIUusT4lEMn_sojCPsyK7Q9SnM5pG9t7u_4FLYjwqjlIh1NOcJbpittne3u8VIEuZisTHUO1XDK3KtvO-HPcjuyvcRvH304s2HjE_xDiBEFM9Cj-0oDvTQZAIFmP71m-r6pprXEDY7VKSs101_ogeSjyqVzRJ9gIs4gL8)
16. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxnp1ozT-Ym1nuArEA8xKxu5Z2XamB5AnShqQJZvC_SybIehxC4EIZwUKy8lgnnZJiEF2jjgReuQMf4MDyIA3ckcvtFsxglFgjJ5W-_MxDIl5gVaqcpMP3FCY=)
17. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW0aBlm4d7kHXvYo_laKjfOo9xHea9yeNxLZHvod2tHP2AThZ7jqBt9z1ZA3Ig8gbpWhMKmk4sYSgoTRFxzOxcU_C_P9ycS_XNUpTUvb5uu5w4RpFJ4ZJifA_M)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGETVkIwRbcf8sc_Qb343ihoTJz5xacds1T8OeMZO108OMFqip2F-zTvcD_pmwzWpDm5915pAu5e1Jhcpgx7JHK_cRz63q6aG9eKEJSdCSW)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEeXAvvdAOGR9lmSF4vX6hZ_QGPqJH8_QMQ11buJF2ZfQtmoACCpuhhQka5zfUULTR_A1RW_EeParZBgiw4kCFl_HBiki7ueOtJ5H4UdG5Rlr7U2JlcqBm8ZxE=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhqlcuanbBJQzi-f-0KX5QKEwElptAqnHuJSOTfWyoKPgRpcUHjx0WtoNslDo_7AZtECHpZzTs63CEBsB08J5iIlpRgFI6ASMFNuv3SV97812D5AWI)
21. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDtz3yTR0LtPHKMCIpv-1jXz3kmd6cMdluozKlNSMQw1Zocg1ylVtuJrnggjSyAqqwLdb5bYlyPmTD8qIe8zzy9j9NgG1CuHBEm4PESexjnrsIpYkiwlFFONt5Mwyzm5D9yRqe5Ja0)
22. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcfX7L3GcdgO5JHIBP0o-9LrsPY9-mmbueibeT2MjT6Vsht7j3WKvfz839Y1D9zllR_s0mziNuu7SqyPmBUXoJ5m4Nz3o9EvkfnTzku_dtJPitGNVALiZrVlFK7bD9QRq3XDHLBjAiq2lhVOcVFwNNm0FykblZ5sqA)


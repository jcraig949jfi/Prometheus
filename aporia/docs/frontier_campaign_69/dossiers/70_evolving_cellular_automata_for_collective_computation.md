# Prompt 70: Evolving Cellular Automata for Collective Computation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd5bW1mYXFmaEpzbXhfUFVQNm9xSmlRSRIXeW1tZmFxZmhKc214X1BVUDZvcUppUUk
**Elapsed:** 395s

---

# FRONTIER PRACTITIONER DOSSIER

## Evolving Cellular Automata for Collective Computation

The field of evolving cellular automata for collective computation investigates how decentralized, locally interacting units can self-organize to perform global information processing. Your initial understanding of the density classification task, the genetic algorithm search over 128-bit rule spaces, and the emergence of particle-based computational mechanics is entirely correct and accurately attributed to the foundational work of Mitchell, Crutchfield, and Das [cite: 1, 2, 3]. The particles you describe are boundaries between regular space-time domains that act as information carriers; their collisions function as logic gates. This mechanism remains the canonical example of emergent computation.

However, the methodology to discover these rules has shifted. While genetic algorithms operating on discrete bit strings defined the field in the 1990s and 2000s, the frontier has recently been disrupted by differentiable programming. We are now seeing the rise of Neural Cellular Automata and Differentiable Logic Cellular Automata, which allow researchers to use gradient descent to search discrete rule spaces. This dossier provides the tacit knowledge required to execute frontier experiments in this domain today, bridging the classical genetic algorithm approaches with modern differentiable architectures.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of evolving cellular automata is currently undergoing a renaissance, driven by the collision of traditional complex systems research with modern deep learning. For decades, the field was defined by using genetic algorithms to search the hyper-astronomical rule spaces of discrete cellular automata to find rules capable of global consensus, synchronization, and classification. Today, the field has bifurcated. One branch continues to use evolutionary computation, focusing on asynchronous updates, small-world topologies, and coevolutionary dynamics. The other, rapidly accelerating branch, has replaced genetic algorithms with gradient-based search, specifically through Neural Cellular Automata and Differentiable Logic Cellular Automata [cite: 4, 5, 6]. These modern methods relax the discrete states into continuous probabilities during training, compute gradients to update the rules, and harden back to discrete logic gates during inference [cite: 5, 7]. 

What is SETTLED: It is mathematically settled that no perfect two-state, one-dimensional cellular automaton can solve the density classification task for all possible initial configurations. This was definitively proven by Land and Belew in 1995 [cite: 8, 9, 10]. Because a perfect rule is impossible, the density classification task is universally accepted as a benchmark for approximate collective computation [cite: 11, 12]. It is also settled that the Gacs-Kurdyumov-Levin rule, though originally designed for a different purpose, remains the benchmark for human-designed solutions, achieving roughly 97.8 percent accuracy on a lattice of size 149 [cite: 13, 14, 15].

What is CONTESTED: The mechanisms that best promote the discovery of high-performance rules remain heavily debated. In the late 1990s, Juille and Pollack claimed that co-evolving the cellular automata rules alongside a population of adversarial initial conditions led to superior performance. This is strongly contested by Werfel, Mitchell, and Crutchfield, who provided evidence that the performance gains were actually due to resource sharing, a technique that preserves population diversity, rather than the coevolutionary arms race itself [cite: 1, 16]. Furthermore, the classic Edge of Chaos hypothesis proposed by Packard, which argued that complex computation naturally evolves near the phase transition between order and chaos, is heavily contested. Mitchell and Crutchfield demonstrated that Packard's results were likely an artifact of his specific algorithm and that computation does not strictly require edge-of-chaos dynamics [cite: 17, 18, 19].

What is OPEN: The current frontier is defined by multi-agent communication heterogeneity and the application of cellular automata to abstract reasoning. Recent work in 2026 by Singh explores what happens when different sub-populations of a cellular automaton use mismatched communication protocols or languages, measuring how linguistic distance slows consensus in density classification [cite: 11, 12, 20]. Additionally, scaling emergent computation to solve the Abstraction and Reasoning Corpus is a completely open frontier, with researchers actively attempting to adapt one-dimensional Neural Cellular Automata to perform program search for ARC-AGI tasks [cite: 21, 22, 23].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Mitchell, M., Hraber, P. T., and Crutchfield, J. P.
1993
Revisiting the edge of chaos: Evolving cellular automata to perform computations
Complex Systems
arXiv:adap-org/9303003
This paper is the absolute foundation of the field's methodology, defining the exact genetic algorithm parameters for the density classification task and simultaneously dismantling Packard's edge-of-chaos hypothesis. A practitioner must read this to understand how fitness is calculated and why uniform density distributions are used over binomial ones [cite: 17, 18].

Das, R., Mitchell, M., and Crutchfield, J. P.
1994
A genetic algorithm discovers particle-based computation in cellular automata
Parallel Problem Solving from Nature III
DOI 10.1007/3-540-58484-6_278
This is the paper that introduced computational mechanics to the evolutionary results, proving that the genetic algorithm discovered a particle-and-collision logic system that no human programmed. It defines the exact mechanism you outlined in your query [cite: 1, 2, 3].

Land, M., and Belew, R. K.
1995
No perfect two-state cellular automata for density classification exists
Physical Review Letters
DOI 10.1103/PhysRevLett.74.5148
This short, load-bearing mathematical proof demonstrates that no rule can achieve 100 percent accuracy on the density classification task, establishing the theoretical upper bounds of the field and cementing the task as a permanent benchmark for approximate solutions [cite: 8, 10, 24].

Juille, H., and Pollack, J. B.
1998
Coevolving the ideal trainer: Application to the discovery of cellular automata rules
Genetic Programming 1998
IDENTIFIER UNKNOWN
This paper introduced coevolution and resource sharing to the density classification problem, finding rules that outperformed Mitchell's original genetic algorithm results [cite: 16, 24, 25].

Werfel, J., Mitchell, M., and Crutchfield, J. P.
2000
Resource sharing and coevolution in evolving cellular automata
IEEE Transactions on Evolutionary Computation
DOI 10.1109/4235.887238
A vital methodological critique showing that Juille and Pollack's success was driven by diversity maintenance rather than coevolution. It teaches a practitioner how to rigorously separate algorithmic components to avoid false attribution in evolutionary dynamics [cite: 1, 16].

CURRENT SOURCES (2020-2026)

Mordvintsev, A., Randazzo, E., Niklasson, E., and Levin, M.
2020
Growing Neural Cellular Automata
Distill
DOI 10.23915/distill.00023
While slightly older than 2023, this is the foundational text of the modern era, introducing the differentiable framework that replaces the discrete genetic algorithm with a neural network update rule. It is required reading for transitioning classical cellular automata into the deep learning toolchain [cite: 6, 26, 27].

Miotti, P., Niklasson, E., Randazzo, E., and Mordvintsev, A.
2025
Differentiable Logic Cellular Automata: From Game of Life to Pattern Generation
ALIFE 2025
arXiv:2506.04912
This paper defines the absolute frontier of rule search: using differentiable logic gate networks to learn perfectly discrete rules via gradient descent, entirely bypassing the limitations of genetic algorithms while preserving the discrete nature of classical cellular automata [cite: 4, 5, 7].

Singh, N.
2026
Communication Heterogeneity and Collective Consensus in Neural Cellular Automata
arXiv
arXiv:2606.21202
This paper takes the density classification task and introduces communication heterogeneity, testing how sub-populations with different learned protocols reach consensus. It represents the frontier of combining collective intelligence sociology with cellular automata benchmarks [cite: 12, 20, 28].

Xu, K., and Miikkulainen, R.
2025
Neural Cellular Automata for ARC-AGI
ALIFE 2025
arXiv:2506.15746
This paper adapts Neural Cellular Automata for a one-dimensional variant of the Abstraction and Reasoning Corpus, demonstrating how the field is shifting from simple density tasks to complex, few-shot abstract reasoning [cite: 21, 22, 23].

PART 3. SOFTWARE I CAN ACTUALLY RUN

CellPyLib
https://github.com/lantunes/cellpylib
Python
Apache License 2.0
2024
MAINTAINED
This is the community standard for discrete cellular automata in Python. It natively implements Mitchell's genetic algorithm for the density classification task out of the box. You can use it today to evolve rule tables for radius 3 one-dimensional lattices. Its main limitation is that it relies on CPU-bound Python implementations for rule evaluation, which makes evolving very large neighborhoods or running massive population sizes painfully slow compared to compiled or tensor-optimized code [cite: 29, 30].

Netomaton
https://github.com/lantunes/netomaton
Python
Apache License 2.0
2024
MAINTAINED
Built by the same author as CellPyLib, this generalized framework supports asynchronous updates, small-world topologies, and continuous automata. You can run density classification experiments on Watts-Strogatz graphs today. The gotcha is its extreme generalization; the overhead of supporting arbitrary network topologies makes it much slower for pure one-dimensional array processing than a dedicated dense-array solver [cite: 31, 32].

Liquid Cellular Automata (liquid-ca)
https://github.com/wfvining/liquid-ca
C++
IDENTIFIER UNKNOWN
2019
DORMANT
This implements the density classification task in a liquid cellular automaton environment. While dormant, the C++ codebase is highly valuable as a reference for performance-critical evaluation of the task. It specifically includes benchmarks for measuring the time to reach consensus. It requires standard C++ build tools, but is subject to bit-rot regarding modern CMake configurations [cite: 33].

DiffLogic CA
https://google-research.github.io/self-organising-systems/difflogic-ca/
Python
Apache License 2.0
2025
MAINTAINED
This is the reference implementation from Google Research for Differentiable Logic Cellular Automata. It allows you to run gradient-based searches for discrete logic rules. You can use it today to replicate their pattern generation and game-of-life discovery tasks. The known limitation is that training differentiable logic gates is highly sensitive to initialization and hyperparameter choices; it requires deep familiarity with JAX and tensor operations, and the continuous relaxations can sometimes fail to discretize cleanly during inference [cite: 7, 34].

alphaXiv Autoresearch Harness
https://www.alphaxiv.org/replicate/2606.21202
Python
IDENTIFIER UNKNOWN
2026
MAINTAINED
An emerging community standard for reproducing 2026 papers directly from arXiv. It allows you to spin up the exact environment for Singh's communication heterogeneity experiments on density classification. The gotcha is that it relies heavily on cloud-compute wrappers; you must carefully extract the underlying Marimo notebooks if you wish to run the code natively on your own bare-metal compute [cite: 35].

PART 4. DATA AND BENCHMARKS

Density Classification Task Initial Conditions (Uniform Distribution)
Generated dynamically at runtime
Size: Varies (Typically 100 to 100000 configurations of length 149)
Open Access
This is the authoritative benchmark for the classical task. It is generated by selecting a density uniformly from 0.0 to 1.0, and then distributing that percentage of ones randomly across the lattice. It is used to measure general classification efficacy. It avoids the combinatorial explosion of the binomial distribution [cite: 36, 37].

Density Classification Task Initial Conditions (Binomial/Unbiased Distribution)
Generated dynamically at runtime
Size: Varies
Open Access
This dataset is generated by flipping a fair coin for every cell in the lattice. It is used to measure a rule's robustness against the hardest possible edge cases. Known Contamination: Because the vast majority of initial conditions generated this way have densities extremely close to 0.5, rules evaluated exclusively on this dataset often overfit to specific noise patterns and fail to generalize across the broader density spectrum. A rule scoring highly here might perform poorly on extreme densities [cite: 8, 36].

1D-ARC (Abstraction and Reasoning Corpus for 1D)
https://github.com/fchollet/ARC
Size: 100s of task pairs
Open Access
Adapted from the original 2D ARC dataset by Chollet, the 1D variant is used by researchers in 2025 and 2026 to measure whether evolved or learned cellular automata rules can perform few-shot generalization. It is currently treated as an authoritative benchmark for moving beyond simple synchronization tasks. Known limitation: Many tasks in 1D-ARC can be solved by template matching rather than true algorithmic reasoning, leading to potential saturation [cite: 21].

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to ground yourself in this field is the evolution of a radius-3 one-dimensional cellular automaton for the density classification task, replicating the Mitchell, Hraber, and Crutchfield methodology.

Software and Version:
Use CellPyLib, version 2.2 or latest.
Run it in a standard Python 3.10 environment.

Dataset Generator:
Uniform Density Distribution generator. For each evaluation, generate 100 independent initial conditions. To do this correctly: select a density uniformly between 0.0 and 1.0. Multiply by the lattice size and take the floor to get the exact number of ones. Place them randomly in the array. 

Parameters to Set:
Lattice size (N): 149
Step budget (M): 320
Neighborhood radius (r): 3
Rule space: 2 to the power of 128
Population size: 100 rules
Generations: 100
Selection: Rank selection or tournament selection.
Elitism: Keep the top 20 percent of rules unmodified into the next generation.
Crossover: Single-point crossover.
Mutation: 2 percent per-bit mutation rate (crucial: this is per bit, not per rule).

Replicates and Seeding:
Execute 30 independent runs with unique random seeds to account for the stochastic nature of the genetic algorithm.

Compute Cost:
Using a modern CPU, 30 runs of 100 generations with a population of 100 and 100 initial conditions per evaluation will take roughly 2 to 4 CPU hours. It is entirely feasible on a standard workstation.

Expected Result:
You should expect the best rules to achieve a classification accuracy of approximately 0.80 to 0.86 on out-of-sample uniform initial conditions. You should compare your result against the human-designed Gacs-Kurdyumov-Levin rule, which achieves 0.978 on the same lattice size. The citation for this benchmark comparison is Das, Mitchell, and Crutchfield, 1994, and Land and Belew, 1995 [cite: 1, 8, 10, 37].

The three most common ways people get this experiment wrong:
1. IC Sampling Distribution: Entrants frequently generate initial conditions by flipping a fair coin for every cell (a binomial distribution). This floods the training set with densities near 0.5. The genetic algorithm will fail to find domain-forming rules and will instead evolve block-expanding artifacts. You must sample the density uniformly first, then place the bits [cite: 36, 37].
2. Boundary Conditions: Entrants forget to wrap the edges of the array. The cellular automaton must have periodic (circular) boundary conditions. If the array is padded with zeros instead of wrapped, the particles will reflect off the walls and destroy the global computation [cite: 29, 36].
3. Evaluation Noise: Entrants use the exact same 100 initial conditions for every generation. This causes the genetic algorithm to overfit to those specific patterns. You must generate a fresh set of 100 random initial conditions every single generation to ensure the rules generalize [cite: 37].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

1. Automated Computational Mechanics Extractor
If you evolve a successful rule, you must inspect its space-time diagram visually to identify domains and particles. There is no off-the-shelf software library that takes an arbitrary rule table, simulates it, and automatically outputs a formal grammar of its particles and collisions.
Interface: 
Input: A 128-bit rule array and a lattice trace (2D matrix of space over time).
Output: A list of spatial domains (regular expressions of repeating bit patterns) and a dictionary of particle interactions (e.g., Particle A + Particle B = Particle C).
The hard part: Calculating the local statistical complexity and applying Crutchfield's epsilon-machine reconstruction algorithm programmatically across noisy boundaries. Several groups rebuild basic spatial filters privately, but a robust, open-source computational mechanics pipeline is a major missing component. It would take roughly three to six months of dedicated engineering by a competent mathematician.

2. Differentiable Bit-String Compiler for Massive Radiuses
Current DiffLogic CA implementations are highly tuned for 2D grids and small 3x3 neighborhoods. If you want to evolve 1D rules with very large radiuses (e.g., r=5, which has a rule space of 2 to the power of 2048), standard genetic algorithms collapse. 
Interface:
Input: Radius integer r, JAX tensor of initial conditions.
Output: A fully compiled, backprop-capable 1D causal mask mapping 2r+1 inputs to a single output logit.
The hard part: Writing custom CUDA or JAX kernels that handle continuous relaxations of highly dense 1D neighborhoods without running out of memory. This is roughly one month of work for an experienced machine learning engineer.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Impossibility of Perfect Classification
The most profound negative result in this field is the formal proof by Land and Belew in 1995. They proved mathematically that no two-state cellular automaton can correctly classify all possible configurations for the density classification task. Any rule will misclassify some configurations with densities close to 0.5. This means any search for a perfect 1.0 accuracy rule is a failed programme before it begins [cite: 8, 10, 15]. 

The Edge of Chaos Artefact
In 1988, Norman Packard published highly influential results claiming that when systems adapt to perform complex computation, they naturally evolve toward the "edge of chaos" (a critical parameter zone between order and randomness). This became a massive popular science trope. However, Mitchell, Hraber, and Crutchfield attempted to replicate this and completely failed. They published a standing critique showing that Packard's results were a statistical artefact of his specific search algorithm and mutation biases. When the genetic algorithm was corrected, the rules did not cluster at the edge of chaos. The hypothesis was falsified for this domain, though it occasionally resurfaces in complex systems literature [cite: 17, 18, 19, 38, 39].

The Coevolution versus Resource Sharing Critique
In 1998, Juille and Pollack claimed that they achieved breakthrough accuracy on the density task by using competitive coevolution, pitching the cellular automata against an adversarial population of initial conditions. This looked like a massive win for coevolutionary theory. However, in 2000, Werfel, Mitchell, and Crutchfield published a devastating methodological critique. They decoupled Juille and Pollack's algorithm and proved that the performance gain was almost entirely due to a background mechanism called "resource sharing" (which penalizes rules that solve the same easy initial conditions, forcing the population to maintain diversity). When resource sharing was applied without coevolution, the high performance remained. When coevolution was applied without resource sharing, performance collapsed. This stands as a permanent warning to the field about false attribution in complex optimization loops [cite: 1, 16].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Experiment 1: DiffLogic CA on 1D Density Classification (Rank 1)
What to do: Apply the Google Research DiffLogic CA architecture (designed for 2D Game of Life and morphogenesis) to the classical 1D density classification task. 
Feasibility: Feasible now because DiffLogic CA was open-sourced in 2025. 
What it measures: It measures whether gradient descent on continuous relaxations of logic gates can discover a particle-and-collision computational structure that outperforms the 0.86 accuracy barrier of historical genetic algorithms.
Falsification: If DiffLogic CA converges to rules that lack particle structures (e.g., simple block expanders) or fails to surpass genetic algorithm benchmarks, it suggests that gradient descent on logic networks gets trapped in local minima that genetic algorithms bypass.

Experiment 2: Communication Heterogeneity in Discrete Rule Spaces (Rank 2)
What to do: Replicate Singh's 2026 experiments on communication heterogeneity, but instead of using Neural Cellular Automata with continuous internal states, apply it to the classical discrete rule spaces. Create a lattice where the left half of the cells executes one 128-bit rule, and the right half executes a slightly mutated 128-bit rule (a "linguistic distance"). 
Feasibility: Highly feasible; requires only minor modifications to CellPyLib.
What it measures: Measures the degradation of computational mechanics (do particles die at the border, or do they translate into new particles?).
Falsification: If the lattice still reaches global consensus without a massive time delay, the hypothesis that heterogeneous protocols fatally disrupt emergent computation is falsified [cite: 11, 12].

Experiment 3: Resource-Shared Differentiable Search on 1D-ARC (Rank 3)
What to do: Combine the diversity-maintenance technique of Werfel (resource sharing) with the Neural Cellular Automata training loop for 1D-ARC tasks.
Feasibility: Requires building custom loss functions in JAX, but is entirely possible in 2026.
What it measures: Measures if maintaining a diverse population of Neural Cellular Automata prevents mode collapse when learning few-shot reasoning tasks.
Falsification: If resource sharing provides no improvement over standard batch-averaged stochastic gradient descent, the idea that evolutionary diversity metrics improve differentiable programming is falsified.

What will NOT work:
Attempting to scale the standard discrete genetic algorithm to radius-5 or radius-7 neighborhoods to find better rules will NOT work. The rule space for radius 5 is 2 to the power of 2048. The genetic algorithm will experience complete combinatorial explosion, and mutation operators will fail to navigate the neutral networks of the landscape. Without a gradient to provide directional guidance, brute-force evolutionary scaling on discrete look-up tables is a dead end.

**Sources:**
1. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH72VAy9yyRNQbRpCnbho2nOZ4FAAaAIQZRzPJXTM7WokN4sAibbWXP4jk64AucVgKOMqzK8WT6gVMnV-gSa8VE9fEXnTQOac-tkvGGtoys88EtAxQkFJUky04RLd1ookFS5MehlEs=)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhs3jH6PLpIVESBRiN-www9KPStopMuNCqVz5epVJtN_pmOeRZBAW-V9HcDKTffHk1hobbvMoWwo-0N1saey3I_nXZNqk0qMxP9d4pfIV2iEo7Lxx-AHF9EAnxFtHCQT4VcgPNTkW3zmhhNBhrMdNYHolhHytrOSsvnkbUnAhKkKVHnl50xVyH3Mowz6u4QG6na68WwXt_56paTq60C5Cszsrwk4C6m3SS6tBsy7C2zk0=)
3. [santafe.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbPhLLe4dgwKQHiVTaO1OC_lg4fnoVIScoBuLQ9ZnEsp7Lx9gxW2rTrDdTed9zK4_Q3QJkuOmiR_qvw8Kb8khtpYMe4_ELuz_p3T-Swc41zx_ZvZgjBRLnIW8bMyveLY51iV9aMAk-2Sd6pcKQqykCEhhw5Y0ASsCKebTuO5Te7JknUa_ZeUw9QfdhXa2q_HGlYeIuxsuztSTY2c49vGgg)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3OS_NLQ86cpZKOuhH-gpC3yEqAc1dT_XQDEdWuuDIQHPtpZc6rG0X-Uz7koV0tGfh6YBxxSZPvSppOQ4nQ5_XBcOJkF3eMsmokXTGEXiUrJ4B7O173_pHey05trWN9ZvDTz_Bo8JbcN_4lKH0-k2VN0OpFwJn-_OjXmWtYwcBXHqznf9Qm4F_mb1ld1dIemM-y833NWRXkfIdtfIf3KKymFt0IqsgHXffHdIQJZW3yPv1lf21dS1K)
5. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFuhWCM5N2TzTJ8a-yyWdasRA2Mgc_547fSqt68NWeCD5MPJ5eUVroKdzTPzsvs8B-CsZRUa8UbsG34eTs0cmdaJsFFYqcKPvxtUR37QFuAGrzLQO1ALUizkTeQJjK5UDYFjB93oPSj-_Tn8f1BOjD3BnHTxSe_MramQyyE7UpUmIE3jemsRxnJXVt-NEjOy-j49zxuCy1yRjnjil_fpPo21OjGVq4TRoUcg==)
6. [distill.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEciySIx8h9ofigV_4zNZJ0BsJ--xt43Y70FVSD_STdKlioMda3ahc7WIZjquShV_RyrKgV3esYFW7VnNv5x7MlgyASetmwyHdVlhAw2nkt-eLDToBVcwluYbg=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQED2Rm4NJv7b8k6oJhj3RqD-WBR2-ISWKOwO4wawROj53Huemk7t1bphSnmSqVx93DBEDr_p9antfS9Iwte8YK0923yldisN1TM5tlAC45bNarf_runxK2KDA==)
8. [academia.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX-8zbgikl5CLgvUaOWSV4j_NGfIyrEjYjmmsCc7wvv0NrdX-Z8Hd6BBcCC8_ed0rszOvpbZ4GhunhFn7Xj70mSNWVkOITWQlBrbPaozk6k3cQZvzGP235H74kX77U0lcmKUQxfw1vqcnhfe8UNFrKcoXaeJfOSe_AHJjCnuOMxbp1xRi8WJ4t4YaKl9WJLqHTfZCagG3m8naqnXCxY-A=)
9. [isoperimetric.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4JDace0LKbkaGUksW_dfdCwu9JfFLA1mviY9hvzlPf43WCGPpaNwRdso12FmJXHkGA3qQJ00eeXRuk249nnDQYxGZ_IDycmh85sEDWs_nHJJ0Zx15Eb0zcBfsD3Hm_wN5EXvvsgJ2RB4EZROhaqRhCZM=)
10. [plos.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPQb8jnaMUw8--aye4H2yFbkkdvlCI7pdBiEHYbTPbqXEsalvalSwIjnBlVDH1U0KBLKlwt71vBN_k1B4vA0F9P5VMrgFXnpulqJ6hE9pezqB883vGLZ-Fxw5szmRc-8uPtNa33WsMeIkZGoTdBOLsQWEl3CwVB-7MPJDlmCX0)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9ndoOnRjuzaS7g9kVMVJoM5IluMrFIbmBUz2me7vs5TdjbiVvCO4blGdZkIeuooSnhoiFw4Z1h6oef2oA5ZvVxGFC8dhMq7cRsVDyf3SLdi4VpVY7YOYqhQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHF_fvwNAx-iPHxfFDc8fWCM0vKLOatfHO1Bfco5hHfThk73YUTWfUTuhV4IXVXhgg4SyI0puM3s_-p1eLWVqlUPedz89NRQC3ufiny0x5eDw5m87OGdA==)
13. [melaniemitchell.me](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGindVwzQCazkPwNQv5MZeFO7I3cwdX4MI0rKopJakjaZxyFuH9xJ_KGmtIP-KD95be4yc_RpfexnLMMvAY3VL0LNryfhd21UjGReY3lNb6c3OjpPBse46v-36OymDeLyMpE_3Jaui4tkOU9LXnEQ==)
14. [prosocial.world](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGR8NiqP7EMCq-qTzPurwZG18ORrvF0L1UvULVFcvp1ZXlDmCSHgogum8ZRyeEZs9Or_u4AKbueFuAGj77MhQkoIb7tBE5xUY2iY7hQC6pqCPmNU5gOeewdt6aJOoeyw_47PIbQ5AFqGTnCRlIe_rUIMFglGCxZysrR8dGvSA==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHn1TNQIdflO-wE4Nyabicp7Pf5MucMutc1qK0YwcQpD3bR-3qKkoUfzkVG9W2jbFaovmSr1ItJ6LQpEArJOiDTnn95LrkrzlPdz4Kxt4syOImBdjrttOEt)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUkz2pUvp9Q93qYzhVZFE3Lk_7GClG3km96NhRRt6BmiVdTyyLGvn2dFPmDZ5AnYL9hDYBBuKlydLF-R1UVnsJLr0Co5xmBwGeYgjaVjgFEwavSUxVGQw9VbY_jzGVKAYawqB2YJXypfiA24k7shDO1F5NvJdkZ0ReyszoOteR6RF4wM4_GsbO_OI9A9fcKtlFP1L5_yIhzgI6YSlZ4cf8c41G-iN7asW_rkqdFA0D6TBwI3lNNzjrmCAcOilHm8R2wsbro4UwlGYXTH4iTU1OgQQghiNaJFfKgR7IuuML9GTBhAchHRForMl8QH9FM8bspY5lOKlcTvIULOhnqXxGDzHfon_Sr89r1SNtmjwGJPrYTjMSBzbyH9SH19s0-6tx8BwmmJmgpW8eXliW8rZbxt1iemYyVrdl)
17. [melaniemitchell.me](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1FIqqxVbjEojphB1O1PryW7-kL9-13QvKaHIjeHt4c03NDaT3O9IxpmKzAjJtR4p_urpMFDq9WjrKF91rZAHtb9hLgVm6KKVZ2MHkgFeDOLL3iAQNp9CI5Z1nQtYWRpk1IBFBBqkhJgaDEw==)
18. [complex-systems.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbP3YOgfaEaAiYG11Qk2G5iPCv9SOvMOYwqhEFq-8ryByxyzqHB-9v6CkfLnsTMBGhHnHyHBIsEdaGN0xf4pQtRv0JT5168YeThRVc_i61p-CEM0-UtFctzxtwrAnb-T0gZryUfSL_TzHMmuI=)
19. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFu0zbrOJWLtMl0q5iBVPap3IKk4R7XFiwnl1IRkd-1GANGJyZ7MrIhrMeYsUoJR-BJqtBj2JuOm62Zi6y6pIhvPnYs39CZjWJEyJNiJq2fV1MZoa90fboD-b533eWEGtpzZ1wac8Gp-w==)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxbiuLjPCEbL68AtenxoBVugEzOlirlXMuXNVcw5aiYv1V1CmYZ7aqXYMJnkzwF00NGIGmlICcVAIiCIEW5wj-bko8fpMZ4WG3FLGKxCOqedkt7JNdTEE=)
21. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOM9j0Fe2f9agEH7TDmefGTZ6cS1-xOLOU9uidxIuNPBW4A0r4cRVAaqTMZkAvIYKCl68OiNQw4UmHShvZ9j437nDTofa6dHie-samOtACpH1p0Nqx8k4kONFQ4se4ZIFZbD-0w7AZPzIcXPn-Mg==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeoxp9VJoh_rvQJzGd58J09moU2PFbjf5bDw4M3rdTi8gTEzMW4oQFc2Np9lMCI3FcvN3zALAAq5uYXC6ro9-cskI_VfrV4Mwz-bzULNTeEkWso9awdQZlIQ==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7QUBfiTxeI7W6aX0Dg611hUTfi56P0VOlAJlowuViUH930Z-9gsolmlRyvTO8HKWWIC5Zc3LcWETc1oX1QGcDfsQSaUDxPNgqZPF4bWOs_CWWp60d6Q==)
24. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUrmkS-fqeWxolylx7cjFDES8s-rQkV-kgXivW7UGvEX8n5FOkeHXWfkShiEjMaPPBWvCn0J5YLn4_RAegqCF4DFUNpjdA2vd2vNUtoLeO0VTHIfJpcirXa76Afo0=)
25. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFdMfsby_cu7OLmIg73ahuB8IAOhAo9n2tFkI9OaglWFt6UsfB56hZJRsMw9NjZooxqnonjiOZCqBQarFStHw01wo4dpxMQn_AS12yFqiJzEpBfxHIYZv4VYtX9yHsmYSMp4WPyEBZcvjyXENyNtVaPd0YZ2kDmxuO92LCj2q0YAMmAK0_zo_9DuobGj4UUmJrgM0oJkc=)
26. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEvlBfuf930f-FR847CInCP6yhiOfRNuma29rtNRlzOCcx45woUgg7xxB-h40QZd2Zm9l73nYuj0ZoTp8COQ-7hdM4PDbC19nmYOi1fKgtfA1At2lWQw9vpckF71p4VkpxfmWEGtAzZ84Gn9BzxI3cVK5YU01ADfaF4M6yIaOP4RU4tQ7yxeZgF4yJfufRsIKaAas7mcmEtjyTbUvl1tS9rRK4flIMI7JF76xPiuedgggwkTd6s35eBkV7)
27. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGGD77xK8dBMc0bJt1D1o_PZk_CTDWcwBQzYL6px38nfzzNN8P7TM92MpPy0QY8bcy52HnJWkYv0LsfC1ZrKt2oZOB3lO3O8nJKXuh4YWmhtpC2C4g0oBr646OaxiHcdoolii7AsHS43T1lpL5WcJn5M4gXanhuslGGaRM)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiz08JhIqjO9prCsyHTMB3wws_yuSXsQjIK3fB-GrqEX6yj0uauT1d4bMLet_PWYNMcOYmIrsulNe-vfK940H2H56Bevj1WES2e_Zqwn0b22M9LOW6Uw==)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-fmmYN7nJow0c2ym0ZM3sP8xWH9mUjghfGSsmluU_n31T-4kFqoTC8uFWqbso7QbLsti1lphmRJ8H1hk6R8o307VORi3mpWrNhM-h0TuCOygHUSdfUvzl0uoQ)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWcUZpJxfGH6XrIviQRl8JPpiNq_lwZ-lCVzEhS6LXIcl9_6iuZvvu1LAAAnARI5B6GB6YmKvyfqf4Awe63bnjHvwGQGtesk7LxXqBHebJ0h_ndNdY4y4c7qFz6kYujA==)
31. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV862ubzYp9xedUPeazWJ8h_zlfPgprIB4S-aLjaAERWoOIJ_pzb29g5ApGSVJ3FAsAPp2m34gnMZB6uw2rUsTfhuO7AELEFSx-8WiKZh9bqIqVaFS2cEMliTG)
32. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzXKKXaxqWs9N03JZjgOT9abqponDIEHutKLlEvrLTj-hfEEhxQ9qRSLXZ7dZyuO9WSe7U5u2ZzNXejGa7yICaF53PSc4AE6fKQR3RmCIB0vCGbVnKozq0OEDFbTtQe0Pq5fXdlDLsDioPDYjZw-vzWy0BS27v4d1lxq5fCPGA3Nkl_w0c1Bo=)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBNJQ1TXKErKx5eO2875JD2TwJMF7AEvn8BiGCg6Gt-Gr29CZ78dLyTW4tI6ELjrVMOxYhNsepPKxPMgZK2IK3jWLeIuji8UrbDhh_A8mx1iqirWLNJiDx-VSG)
34. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgM4k5LFBUujgZaDJwb_c8crx5vY8zdfHQj8ZdvMlKFJxiXyiSLmb3o_OMjgcb22dTpV1LuZ0w94TcWUnwacC3_o7Zx7weXKUHKm9S1nEngk9OxpUO97oUTqwgARLqcwXzpy2xgqaXasUv85fnr42lTeWexCqFNsvFiQiHKQ==)
35. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU0GiyZ_EBIeo_GScYZLj17FAukplqOd8oOJYeftKXhMm9D3ANbcN5hk0rB-eQOIF_jzZKjRNhcTwSq8zn_4WY1HzizvQGuFO61fQY5oX7IiEDbI4dFbR_LbIO6Uzz-nElnDg=)
36. [melaniemitchell.me](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXO8AS_GhU7VEanyeMZypu3V-TLkhxljdP7QpzeNyCJArnG5v0ESDFcIkVEDIdcZF00cFda0jfZN9G3NkOhwv3I5QLzJTnbUdPI8_k1E3lMqE5hDSj9lCmO9DdxK-XdQASyT0KQd1YkHeffe3qs_tg8w==)
37. [brandeis.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9oNSF5yjDNrgVkUFY_iFWQ5BFXOGoW-Cd6aZ4eGZmTAK3-RO86gcgckMI_kB1MH98gX5TeOc9qLsNAhxJ2R8DjlPNT6lND00_mWeChFSyK5NlRy7xTx5G5rQ1EVLc1D2_baUf0qJw_5HszQ==)
38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjjvO0Hmuipu1YP0L8Xe9A-t0ZdBj_BjNy89QXhgODlPUm4EVebqWQ3-YnBlDUQkm2aan7ddmdv_gdVTXrhqwQHOH7GfLeZ2AHDjO5MxU7uCaWKjiTTfM=)
39. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgxyXaW_Nss_G0aQZi8T-D_5oKKqMD0zr9OVLGX53InHo8-LB_SUq2V3ar483_IjNAwUsXc2X-G-zjrC3k6XMuEuJkRiBlm1NomKZSjzWxnLqRDWbpgBRj2Q==)


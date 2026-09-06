# Prompt 01: Evolutionary substrates

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdIVktkYW9hY1BKZldqckVQX2ZTZGtRURIXSFZLZGFvYWNQSmZXanJFUF9mU2RrUVE
**Elapsed:** 334s

---

# Evolutionary Substrates: A Methodological Design Analysis for Computational Research Benches

The deployment of computational research benches for investigating evolutionary substrates requires navigating severe architectural constraints to capture the intrinsic experimental practices of distinct scientific disciplines. This report addresses the methodological design task of defining the minimal viable experiments for Artificial Life (ALife), Open-Ended Evolution, Evolutionary Computation, Digital Evolution, and Machine Evolution based on a specific, tightly constrained execution bench. As it stands, the execution bench limits investigations to sealed specifications, single scalar outcome comparisons, and exactly three pre-defined executors (`noop_v0`, `evaluate_bitstring`, and a 1-dimensional `random_walk_v0`). 

Key points regarding the current analysis include:
*   **Methodological Friction:** The existing bench infrastructure severely constrains the expression of population dynamics, spatial interactions, and complex network topologies, which are foundational to evolutionary research. 
*   **Workarounds and Expansions:** While some neutral baseline testing can be co-opted into the existing `random_walk_v0` executor, the vast majority of characteristic experiments in these fields require explicit architectural expansions, notably population-level state memory and spatial grid tracking.
*   **Evidentiary Grounding:** The design templates proposed herein are strictly grounded in canonical literature, ensuring that the theoretical integrity of the simulated experiments matches the published methods of the respective fields.

The following sections exhaustively detail the theoretical background, methodological constraints, and exact executable templates and expansion requests for each of the five target fields. 

## 1. Artificial Life (ALife)

Artificial Life (ALife) represents a vast interdisciplinary effort to understand the fundamental principles of living systems by simulating their behavior in artificial media, typically through bottom-up computational models. A hallmark of ALife research is the study of emergent complexity, where simple local rules give rise to unpredictable, highly structured macro-behaviors. 

### 1.1 Methodological Context
The foundational methodology of ALife was popularized by John Horton Conway's "Game of Life," introduced to the broader scientific community by Martin Gardner in 1970 [cite: 1, 2]. The Game of Life is a zero-player cellular automaton that takes place on an infinite two-dimensional orthogonal grid of square cells, each of which is in one of two possible states: alive or dead. Conway carefully engineered the transition rules to ensure unpredictability and to meet three specific desiderata: there should be no initial pattern for which there is a simple proof of unlimited growth, there should exist initial patterns that apparently do grow without limit, and there should be patterns that evolve for considerable periods before stabilizing [cite: 1, 3]. The rules dictate that any live cell with two or three neighbors survives, any live cell with four or more neighbors dies from overpopulation, any live cell with one or zero neighbors dies from isolation, and any dead cell with exactly three live neighbors becomes a live cell [cite: 1]. 

Research suggests that this simple paradigm opens up an entire field of mathematical and computational exploration, as these local interactions can simulate universal Turing machines and self-replicating automata [cite: 4, 5]. A core operational experiment in ALife involves initializing a grid with a specific density of living cells and iterating the automaton to measure stabilization patterns, oscillating phases, or the spatial occupation share, which typically levels out around 3% [cite: 2]. 

### 1.2 Bench Translation and Constraints
On the current execution bench, reproducing a classic ALife experiment is architecturally impossible using the provided executors. The bench lacks any concept of a spatial grid, nearest-neighbor interaction, or cellular states. The `random_walk_v0` executor provides a 1D stateful path, which is wholly inadequate for simulating the 2D neighborhood rules required by Conway's cellular automaton [cite: 1, 3]. Furthermore, ALife models demand that the state is passed holistically (the entire grid) across time steps (repeats), rather than as a single 1D displacement. Consequently, the smallest honest experiment for ALife necessitates defining a new executor kind to simulate cellular automata dynamics.

BEGIN_TEMPLATE
{
  "template_id": "alife.game_of_life.v0",
  "kind": "cellular_automaton_v0",
  "param_space": {"grid_size": {"int_range": [cite: 6]},
                  "density_percentage": {"int_range": [cite: 7]},
                  "steps": {"int_range": [cite: 6]}},
  "origin": {"source": "LITERATURE",
             "field": "Artificial Life (ALife)",
             "reference": "Conway's Game of Life as described by Martin Gardner (1970) in Scientific American.",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the final population density of living cells in a deterministic 2D cellular automaton after a set number of steps. ALife researchers run this to study the emergence of stable patterns and spatial occupation from local transition rules. A SURVIVED verdict (e.g., verifying density levels out near 3 percent) would confirm the basic deterministic execution of Conway's rules, but it would NOT license the claim that the initial configuration is capable of universal computation, open-ended complexity, or generating unbounded self-replicating gliders."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Artificial Life (ALife)
LACKS: Spatial grid state tracking.
WHY: ALife inherently relies on local interactions between adjacent entities embedded in a spatial topology. The current bench only supports a single scalar seed root and an independent 1D stateful walk, providing no workaround to faithfully represent local spatial neighborhoods or cellular state transitions.
SMALLEST_FORM: A state discipline 'persist_grid' that retains a 2D binary matrix between repeats, taking 'grid_size' and 'density_percentage' parameters, and adding a 'final_density' float field to the result.
BLOCKS: Artificial Life (ALife)
EVIDENCE: Martin Gardner's 1970 Scientific American publication detailing Conway's Game of Life, establishing 2D neighbor-dependent state transitions as the bedrock of ALife computational models.
END_EXPANSION

## 2. Open-Ended Evolution

Open-Ended Evolution (OEE) focuses on systems that continuously produce novel, complex, and adaptive entities without reaching a stable equilibrium or a static evolutionary dead-end. Unlike standard optimization algorithms that halt upon finding a global optimum, OEE systems are designed to exhibit unbounded creativity, much like the Earth's biological biosphere.

### 2.1 Methodological Context
A primary challenge in OEE research is establishing a quantitative metric to verify whether a system is genuinely open-ended. Mark Bedau and Norman Packard (1992) pioneered the use of "evolutionary activity statistics" to solve this problem [cite: 8, 9]. They proposed characterizing evolution in terms of macroscopic behaviors emerging from microscopic organismic interactions, specifically defining evolutionary activity as the rate at which useful genetic innovations are absorbed and persist within a population [cite: 9]. 

To rigorously classify a system, Bedau and Channon introduced methods for calculating the total cumulative evolutionary activity and comparing it against neutral models. A system must demonstrate unbounded adaptive evolutionary activity—meaning the accumulation of novelty must exceed what would be expected from random, non-adaptive drift [cite: 10]. In experimental practice, OEE researchers routinely run "neutral shadow" models to establish a baseline of activity generated purely by random mutations and genetic drift without selective pressure. Subtracting the activity of the neutral model from the experimental system normalizes the statistics and reveals true adaptive dynamics [cite: 11].

### 2.2 Bench Translation and Constraints
Because the bench severely restricts outcome rules to a single scalar comparison and lacks longitudinal trend testing, it cannot directly measure the *rate* of accumulating adaptive innovations. However, the bench *can* execute a neutral shadow model using the existing `random_walk_v0` executor. A stateful 1D random walk acts as a mathematically perfect baseline for unbounded, non-adaptive state space exploration (neutral drift). While it cannot prove open-endedness, it represents the foundational null hypothesis against which OEE researchers evaluate their systems. Because this experiment fits the bench comfortably and represents a real methodological baseline in OEE, we utilize the existing executor.

BEGIN_TEMPLATE
{
  "template_id": "oee.neutral_drift_null.v0",
  "kind": "random_walk_v0",
  "param_space": {"steps": {"int_range": },
                  "step_scale": {"choices": [cite: 6, 7, 12, 13]}},
  "origin": {"source": "LITERATURE",
             "field": "Open-Ended Evolution",
             "reference": "Neutral models for evolutionary activity statistics by Bedau and Packard (1992).",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the absolute state displacement of a random walk across iterations, acting as a neutral null model for unbounded state-space exploration. OEE researchers run this to establish a baseline of non-adaptive 'evolutionary activity' to compare against potentially open-ended systems. A SURVIVED verdict (e.g., displacement exceeding a wide variance threshold) would confirm the presence of continuous unbounded neutral activity, but it would NOT license the claim that the system exhibits true open-ended evolution, because it lacks the adaptive, selectively-favored novelty accumulation required to prove biological creativity."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Open-Ended Evolution
LACKS: Time-series trend testing in the outcome rule.
WHY: Open-Ended Evolution inherently studies the ongoing, unbounded accumulation of novelty or activity over time, requiring trend analysis across iterations to prove continuous growth. The current bench restricts outcome rules to a single scalar comparison on a single snapshot field, offering no faithful workaround to evaluate whether an evolutionary activity metric is continuously increasing across sequential repeats.
SMALLEST_FORM: An outcome rule operator 'TREND_POSITIVE' that performs a linear regression over a specified scalar result field across all repeats and checks if the slope is greater than zero.
BLOCKS: Open-Ended Evolution
EVIDENCE: Bedau and Packard's 1992 introduction of evolutionary activity statistics, which explicitly define open-endedness by classifying the long-term, continuous macroscopic trends of genetic innovations over time.
END_EXPANSION

## 3. Evolutionary Computation

Evolutionary Computation (EC) encompasses a family of algorithms for global optimization inspired by biological evolution, heavily relying on concepts such as reproduction, mutation, recombination, and selection. 

### 3.1 Methodological Context
Unlike ALife's focus on emergent complexity, EC is typically applied to specific, hard optimization problems. Candidate solutions (often represented as bitstrings, vectors, or trees) play the role of individuals in a population, and a fitness function determines the quality of the solutions [cite: 7, 14]. Classic benchmark experiments in EC involve evaluating how efficiently a Genetic Algorithm (GA) can optimize a known fitness landscape, such as the OneMax problem, where the goal is to maximize the number of ones in a bitstring.

Standard EC practice dictates that a population of size *N* is initialized, and over *G* generations, solutions are selected proportionally to their fitness to act as parents [cite: 12, 15]. The crossover and mutation operators explore the search space. The overarching goal is not biological realism, but optimization efficiency and avoiding local minima. 

### 3.2 Bench Translation and Constraints
The execution bench today includes `evaluate_bitstring`, which scores a single bitstring against a hidden target derived from the seed root. While this acts as a fitness function, it does *not* execute an evolutionary algorithm. Because the bench only executes sealed, single-payload experiment specifications, a researcher cannot implement an external population loop and feed it to the bench dynamically. Therefore, to run a characteristic EC experiment natively on this bench, the executor itself must encapsulate the population dynamics and generational loop of a basic Genetic Algorithm. 

BEGIN_TEMPLATE
{
  "template_id": "ec.genetic_algorithm_onemax.v0",
  "kind": "genetic_algorithm_v0",
  "param_space": {"population_size": {"int_range": [cite: 6]},
                  "generations": {"int_range": [cite: 6]},
                  "bit_length": {"int_range": [cite: 16]},
                  "mutation_rate_percent": {"int_range": [cite: 6, 7]}},
  "origin": {"source": "LITERATURE",
             "field": "Evolutionary Computation",
             "reference": "Foundational Genetic Algorithm optimization benchmarks on rugged/hidden landscapes.",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the maximum fitness achieved by a population of evolving bitstrings attempting to match a target over a set number of generations. Evolutionary Computation researchers run this as a foundational benchmark of algorithmic optimization power. A SURVIVED verdict (reaching a specified high fitness threshold) would prove that the genetic algorithm can successfully climb the fitness gradient of the hidden target, but it would NOT license the claim that the algorithm can maintain diverse ecological niches, escape massive deceptive local optima, or adapt to non-stationary environments."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Evolutionary Computation
LACKS: Population-level state memory.
WHY: Evolutionary Computation and Digital Evolution require maintaining, evaluating, and iteratively modifying a set of multiple distinct candidate solutions or genomes simultaneously. The current bench only permits a 1D stateful walk or stateless bitstring evaluation, meaning there is no workaround to simulate the competitive dynamics, crossover, or differential reproduction of a structured population.
SMALLEST_FORM: A state discipline 'persist_population' that retains an array of object payloads between repeats, taking a 'population_size' parameter, and adding a 'max_fitness' scalar field to the final result.
BLOCKS: Evolutionary Computation, Digital Evolution
EVIDENCE: Kenneth Stanley and Risto Miikkulainen's 2002 NEAT paper, which explicitly relies on maintaining a diverse population of topologies and protecting innovation via speciation algorithms.
END_EXPANSION

## 4. Digital Evolution

Digital Evolution is a specialized subset of ALife and EC where self-replicating computer programs evolve within a user-defined computational environment. Unlike standard genetic algorithms where a central loop applies mutations and crossover, digital organisms actively execute their own genetic instructions, carrying out self-replication and interacting with their environment.

### 4.1 Methodological Context
The preeminent platform for Digital Evolution is Avida, developed by Charles Ofria, Christoph Adami, and Richard Lenski. In a landmark 2003 Nature paper, Lenski et al. utilized Avida to address a long-standing challenge to evolutionary theory: explaining the evolutionary origin of complex organismal features [cite: 17]. Critics of evolution (often citing Paley's watchmaker analogy) argue that complex features, which require the coordinated execution of many parts, could not evolve because intermediate stages would have no adaptive value [cite: 18]. 

Using digital organisms—computer programs that self-replicate, mutate, compete, and evolve—Lenski et al. demonstrated that populations could evolve the ability to perform complex logic functions (such as EQU) requiring the coordinated execution of many genomic instructions [cite: 17, 19]. Complex functions evolved by building on simpler functions (like NAND) that had evolved earlier, provided these intermediate functions were selectively favored. Crucially, the researchers found that no particular intermediate stage was essential, and in some cases, mutations that were actively deleterious when they first appeared served as critical stepping-stones in the evolution of the final complex feature [cite: 17, 20]. These findings definitively showed how complex functions could originate by random mutation and natural selection [cite: 17]. 

### 4.2 Bench Translation and Constraints
Simulating digital organisms requires executing a sequence of linear genetic programming instructions. The current bench lacks any instruction-set executor. The smallest honest representation of Lenski's 2003 method is to track the evolution of a logic function capability over sequential updates. Because this relies on the same missing "Population-level state memory" identified in Section 3, we only provide the template here, noting the blocking overlap.

BEGIN_TEMPLATE
{
  "template_id": "de.avida_logic_evolution.v0",
  "kind": "avida_cpu_v0",
  "param_space": {"genome_length": {"int_range": },
                  "updates": {"int_range": }},
  "origin": {"source": "LITERATURE",
             "field": "Digital Evolution",
             "reference": "The evolutionary origin of complex features by Lenski, Ofria, Pennock, and Adami (2003) in Nature.",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures whether a self-replicating digital organism can evolve the ability to perform complex logic functions from simpler instruction sets. Digital evolution researchers run this to study the incremental, step-by-step origin of biological complexity. A SURVIVED verdict confirms that random mutation and natural selection can produce the target complex logic function within the update budget, but it would NOT license the claim that all intermediate mutations were independently adaptive, as the literature explicitly shows deleterious mutations frequently act as necessary stepping-stones."
}
END_TEMPLATE

*(Note: The expansion request blocking this template is identical to that of Evolutionary Computation—Population-level state memory—and has been grouped in the previous section as per prompt instructions).*

## 5. Machine Evolution

Machine Evolution involves applying evolutionary algorithms to optimize the architecture and parameters of machine learning models, primarily Artificial Neural Networks (neuroevolution). 

### 5.1 Methodological Context
A core question in neuroevolution is how to gain a performance advantage by evolving neural network topologies alongside their connection weights, rather than merely optimizing the weights of a fixed architecture [cite: 7]. In 2002, Kenneth O. Stanley and Risto Miikkulainen presented NeuroEvolution of Augmenting Topologies (NEAT), a method that significantly outperformed the best fixed-topology methods on challenging benchmark reinforcement learning tasks [cite: 7, 13]. 

The increased efficiency of NEAT is attributed to three critical components: (1) employing a principled method of crossover of different topologies using historical tracking genes, (2) protecting structural innovation using speciation, and (3) incrementally growing from minimal initial structure (complexifying) [cite: 7, 13]. NEAT demonstrated that evolution can simultaneously optimize and complexify solutions, offering the possibility of evolving increasingly sophisticated behavior over generations and strengthening the analogy with biological evolution [cite: 13]. 

### 5.2 Bench Translation and Constraints
Evolving topologies requires an executor capable of representing, mutating, and crossing over directed graphs (nodes and edges). The existing bench only offers a single scalar value tracking (via `random_walk_v0`) or flat bitstrings. There is no capacity to represent historical tracking markers or topological maps. Therefore, simulating NEAT requires a dedicated executor that manages graph structures.

BEGIN_TEMPLATE
{
  "template_id": "me.neuroevolution_topology.v0",
  "kind": "neuroevolution_v0",
  "param_space": {"input_nodes": {"choices": [cite: 12, 15, 19]},
                  "output_nodes": {"choices": [cite: 7, 12, 15]},
                  "evaluations": {"int_range": }},
  "origin": {"source": "LITERATURE",
             "field": "Machine Evolution",
             "reference": "NeuroEvolution of Augmenting Topologies (NEAT) by Stanley and Miikkulainen (2002), Evolutionary Computation.",
             "proposed_by": "Herakles"},
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This measures the ability of a neuroevolutionary algorithm to solve a hidden task by incrementally complexifying a neural network from a minimal initial structure. Machine evolution researchers run this to verify that evolving topologies alongside weights out-competes fixed-topology optimization. A SURVIVED verdict demonstrates that the complexifying network successfully augments its structure to solve the task, but it would NOT license the conclusion that the resulting evolved topology is the mathematically optimal or absolute minimal architecture possible for the problem domain."
}
END_TEMPLATE

BEGIN_EXPANSION
FIELD: Machine Evolution
LACKS: Graph-based structural state.
WHY: Machine Evolution, particularly neuroevolution methods like NEAT, relies heavily on the incremental augmentation of network topologies (nodes, edges, and historical markers). The bench's stateful components only support a 1D scalar walk, offering no workaround for persisting, crossing over, and structurally mutating dynamic graph structures across computational repeats.
SMALLEST_FORM: A state discipline 'persist_graph' that retains a directed graph with edge weights between repeats, taking a 'max_nodes' parameter, and adding a 'hidden_nodes_count' integer field to the result.
BLOCKS: Machine Evolution
EVIDENCE: Stanley and Miikkulainen's 2002 paper on NEAT, which proves that complexifying neural networks from minimal structures using historical markers for topological crossover yields vastly superior optimization results compared to flat vectors.
END_EXPANSION

## Conclusion

The analysis reveals that the computational bench, in its 2026-09-06 state, is highly restricted in its ability to directly service the fields of Evolutionary Computation, Artificial Life, Digital Evolution, and Machine Evolution without significant architectural expansion. While Open-Ended Evolution can partially adapt the `random_walk_v0` executor as a null model for neutral drift, the remaining disciplines require explicit executor definitions and state disciplines. The deployment of the requested expansions—specifically spatial grid state tracking, time-series outcome rules, population-level memory, and graph-based structural state—would transform the bench into a rigorously capable tool aligned with canonical evolutionary substrate research.

**Sources:**
1. [drikus.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcBwccA4HanFDTOehk1f_Iug0H0Ie2eONoGvlKGuQPs39Uf7ptXZExGsh-Ef7hnycniVpAkrG3OLhPuIAVHhGrnSXS0Ld8B87kyM1Dxo4HMNcTImPYCyXHXPzfZ1gLz0doS-QOUK6Na7KJyEKAZjW6)
2. [scirp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH61ByRxTDuRlBvPGfh-pyvvVUDC9HNxk1lwkZEsShLHTwN79ayArM6LeBX75g1MOHqxl3LbmTyj0O1NyLb0jvzDltYrQkY6noB13BQsdE9PyAC4-SIJXWQBs8s0UmT5VXlxZ5fXxnm8hBmomPgNz3CfOg5Ud0UH08wTw==)
3. [northwestern.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdymM7DQRlZGiv3w_ItgsdMEFvXj1oBlMaOdjBRX4Df4aXBm6AxeS3Vnd5rImqn2aPhz8dap02q2VzVnHGAwGXTUjnhXBNdp107-aB3xJl-XjQkUDx-2XJvktE3sNfSWO3zQ_2paI=)
4. [bstu.by](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkQKpfXFq0h6Mt60xvpQaS1UTlG8eMpDPpmOHt08i5tPfSxpFlL064Zu6kI6OW-8zDB7ht3tHuAqsymLSHejVO4MP8XjnNb5vEQuECOb4dQgtwfOsETkey-cr2jlt0ud7h2zU=)
5. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGMO82K63CNkuxflZlSgUc4N4NpYMog0zIJojov1XPaSx5uZJfBscP6WLo9Z0mfP3HQWq0sV1F253SplgchUbr9TFPhVV9u6QX1xBrjIbFEkvjNTWniHvzsX6yBtsq439Wp1BDX24U750aL9OyheGup2HYF_Pqeh6AznVsPg0kMH7nVot7Xa23vaJGS5p8gLkAJRYfGBhH7YSfVBI8Q17NoKLbJUoBHSbx9QYFmdTVPkh5toHQRObp7-hzHdSQbsQz-A==)
6. [kenyon.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnhPt5Lkk-yaL0dYgIyg4VubHbnl-BdxVUiSTGXChT2DpiToKYTPiv2r9kK_XZy0fJVhD2v-evFLC5H1FK79yOs4jg0Yg95YVSdcN791Dw-XIaXCAFrkZOo8QnWnm1zWB1YsJ4vCIVZLp4RVEY)
7. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVfiGUzCcKRSn594zyuRDs9xB5dn1nxq9fBPz80o9LKXwLB2qIa-kFcm1VHFc2M9Aboe42erfIdMm2zMO3xH0-6FfQVfgCmI6Sloqh1u8_ZC5ongv-VR7jzwiwPg==)
8. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsdD59rwaxjpR39WDwfobfc3bQdmkcbx-J-ZiJlsLTm-Kbd7-Y52E9_d2dZFX5eAN9rc0biFeYnzU68L9YmRkXF5vL5AllBjLWLXYHKw7-w93QgSY83DU_A0wsBnNBQ9r9UVSTETai0g9XvFB9CxhwFogpKLba0qQeCJSs)
9. [philpeople.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkIclF_V8WuPGBTD7IyYWyco-dcvU5OJq6cOnDO34b0bZ2u8eaWff710g1bIzU-y2wcGiepG1LCaDtEH840olqHaQGuZzOUm6txwux6vInM-QVV6E-XMo3lz3M4OZB6h7wTBD1C-NpxwVrejMB45pLAoXvI2_rRSCZwp76)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5mVQwcvN_1w3YWB3iS252zWag2Oj3-ZK1Mr54KZaFvQZfX9sdMVJ81yKsAScV7OvweVcZX-ph3VoFPqvP8CIZ9zi_u8m7BLKPGt1YKcH-IRoPz3AsRsR4bg==)
11. [soton.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzVkqIeJBxw7sGKLAfKxvVh9ZLDRPRt5bSXR0LKs6TMD3vTblkZBAL6phSaJPDmpqXNMBkPWWoqj8MIGazftwhPYSKObEPMvpr7sP7hVYg36dYTc3pJHP2wCVofRuCYlSWk5Vp4J0c)
12. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVyQxSoLz9FGJAfT0_BBJ8o9t4ex8n32Zt3RWUWl_TRD3EJNDGgwvFtEZ9gsjQsLD1HezDMal3NI7AgTvNk31AHHvYBUmye1DkxuFqit9pioiol3Jmfh7Q-iokGmDTIXV0n_JiynlDflpAOI8vSfyuk4kOH9rDwvH8XrTluf2fA1ajJHQf7GfiQg4BmMTocLNyMp789fGOs-9reYsAFYMTpvSEvjzXvQZ_d_cl8rGiuaAdWF44JfbS_BlEpM-tAK7L5hUp70c=)
13. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZwTZU82cKLWJlDE-ewtxbQ326ZtZdKt4CNIEufQcIe-C33mUy7h2hUbgiljMSLBzsd8-KzjPw1PN6vb9IC1LMBZlDU-7RwSEPUYi8MC1nr9E6DavVBSFeroF2f5vH7A==)
14. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfgkM4071kp03FPlVYnQQHGFARYkHQkRYhpb5s3Zw_1EPi2JwklkZYrxjvt3qZOPaL0l2dsX3t5ejwjCd7E5JBQ2FuW7dFkkJhyKC40XnePa7qONKmAeqpGzomLxgxvFpCG3joDGsHDh8DA002vhw0Wv_bOLKvtW2-RH4=)
15. [scirp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUMR0cMWOAvpYX2PuMY2S-GGHbZy2X1EaVfQybcUvYBBoYFoWqiKekdn6f6J07o5Lqn7B3ed1K9AWqBgBderSt1HNJnbifPLJJgpQotOPXeUGX92PeGTzWK9OX-dyy6YaEHW6ni1ErQ7wcoNIpuLq57P6wfyzWMmuyYQ==)
16. [hpi.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxHuMyrYDcGZUUKWUcs8ObIjMu6yS3c0VXl3O4Oiub5jkdLVcM3VM6ipG2DBuPgshLb3-90zvrgs366NxWtZsfFtP6inhEuTpUk8R-AnpEDtjXIRnl95vpCp3TbYN9o56ZdVx20IksfqDE99X2ktKJ)
17. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAs1YAyMTI-PL-3ucGRYVYA__Jc47TQ4gPyaETSjIvNY7uEL8MhuVKG9hBYnrA-ybRmNjIDX9hy3NdbOpCNfQ5yRmtkDUDHwhZLXFy2N5fTwBIOTd48axfUF4_INrE8w==)
18. [free.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtqFOfGxWgTpRZNLz_xZVPRGhY0U1r7MfcQmlcRieSWbPY4XdKsBK-mYg8BOC3f_T2QNtovg32oT1CWD-Zqja7iNeJOp1aKQgKm3xfhkE-bRBSi3qs1NZ9qFWqD0Iq5ZXASAyAt60vgpIE2vd_pIIQzw==)
19. [uchicago.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnonbSBE9bZQPzx33csaWICxOv9x8UfYebC25ahZ8F_uzhBUDiYqL2cY9XaCZUbHjZS4MbY6X235j7OMKrCyS9JI6JMDZKGV9SErgk7G4ILBE6liXZtUD4bSoUnSuTaz4k8TvU1h48vbhe)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtLs1EHl2hZC_h99i98QqIFD-be6T0_0UoLjBLZ4fJCRIwZJaIfKO44unQJm5QIsXUIMvEmVnqc90t70C_nt2kQg5Jh_bSndc0zVXTyiL1ZqtjS95MANK5xaIEkhZvTlKE8d2UNHnPNa-gVgPw4UGLYFRJdroJ8cz3B8FHqk1l5URRkz3WYHMi21Vb-migt3JJLzs=)


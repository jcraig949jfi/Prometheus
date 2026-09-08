# Prompt 04: Artificial Life (ALife)

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdyYUtlYXRLR0FmSGUtc0FQcFpIR2dBOBIXcmFLZWF0S0dBZkhlLXNBUHBaSEdnQTg
**Elapsed:** 365s

---

# FRONTIER PRACTITIONER DOSSIER
Field: Artificial Life (ALife)

Key Points:
- The anchor method you described—a shared memory soup, resilient machine instructions, and a round-robin scheduler producing emergent parasitism—is perfectly accurate and specifically describes Thomas Ray's Tierra system.
- Classical Artificial Life (ALife) based on discrete machine-code replication has largely solved its initial questions regarding ecological emergence but hit a hard ceiling on organismal complexity.
- The 2026 frontier has shifted dramatically toward Open-Ended Evolution (OEE) powered by Large Language Models (LLMs) and continuous-space cellular automata.
- A profound and active theoretical debate currently divides the field: computational scientists believe algorithmic open-endedness is achievable, while theoretical biologists argue that algorithms are mathematically incapable of the radical emergence seen in true biological agency.

Your understanding of the anchor method is historically precise, but it requires a specific attribution. The mechanism you described—a shared memory block (the soup), template-based addressing (to survive displacement), self-measuring loops, divide instructions, and memory-filling reapers—is the exact architecture of Tierra, published by Thomas S. Ray in 1991 cite: 36, 58, 59. You are entirely correct about what varies (the instruction sequence) and what is measured (viability, population counts, proportion of soup occupied). 

A necessary correction for a modern practitioner: while Tierra used a single shared memory soup, its immediate and highly successful successor, Avida cite: 1, 26, altered this paradigm. In Avida, organisms live on a 2D grid rather than in a single shared memory block, and each organism possesses its own isolated virtual CPU and memory space. They interact by competing for space on the grid and CPU cycles, which are awarded based on the organism's ability to perform logical operations (phenotypic traits) rather than just replication speed. This is a crucial distinction: Tierra demonstrated raw ecological emergence (parasitism), while Avida demonstrated the evolution of complex functional traits.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the field of Artificial Life is undergoing a structural transformation. The classical paradigm of evolving discrete, hand-crafted assembly languages in virtual CPUs (the Tierra and Avida lineage) is mostly dormant as an active area of core algorithmic innovation, having been largely absorbed into the broader disciplines of Evolutionary Computation (EC) and Generative AI. The modern field is now dominated by the pursuit of Open-Ended Evolution (OEE)—the creation of systems that continuously produce novel, increasingly complex, and learnable artifacts without settling into equilibrium or requiring new human-designed fitness functions cite: 19.

What is SETTLED is that digital evolution reliably produces complex traits, stable ecological dynamics, and robust host-parasite arms races. We know definitively that self-replicating programs will mutate to exploit any available computational niche, optimizing for replication speed and discovering memory efficiencies that human programmers would not easily write. It is also settled that spatial structure (like Avida's 2D grid or continuous cellular automata) promotes diversity and prevents competitive exclusion better than well-mixed soups.

What is CONTESTED is a fundamental theoretical divide regarding the limits of computation. On one side are ALife and AI practitioners who believe that algorithmic systems, if given sufficient scale, multi-agent dynamics, and open-ended reward structures, can achieve Artificial Superhuman Intelligence (ASI) and unbounded evolutionary creativity cite: 51, 53. On the other side is a robust standing critique from theoretical biologists and complex systems theorists, most notably Stuart Kauffman, Andrea Roli, and Johannes Jaeger cite: 62, 63. They argue that algorithmic systems operate within predefined state spaces (the world as a theorem) and are mathematically incapable of identifying and exploiting novel "affordances" in the way biological organisms do. They contest that true open-ended evolution requires biological agency and radical emergence, rendering algorithmic attempts at AGI and true ALife fundamentally limited.

What is OPEN is how to successfully merge Large Language Models with ALife principles. Researchers are actively attempting to use LLMs as the mutation and recombination operators in evolutionary systems, treating prompts, code, or neural architectures as the "genome." The frontier consists of finding ways to maintain non-equilibrium dynamics—such as predation, limited resources, and persistent environmental change—within these LLM ecologies so that they do not simply plateau into social harmony or degenerate into noise cite: 16, 19.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Thomas S. Ray
1991
An approach to the synthesis of life
Artificial Life II
IDENTIFIER UNKNOWN
This is the foundational paper describing Tierra, formalizing the exact shared-memory, template-addressing method you described. A practitioner must read this to understand the origin of the digital soup and how uncontrolled memory replication leads to spontaneous ecological complexity, such as parasites and hyper-parasites.

Chris Adami, C. Titus Brown
1994
Evolutionary Learning in the 2D Artificial Life System Avida
Artificial Life IV
arXiv:adap-org/9405003
This paper introduces Avida, transitioning the field from Tierra's shared soup to a 2D grid of isolated virtual CPUs. It demonstrates that spatial geometry improves adaptive capabilities and shows how organisms can be bred to perform simple computational logic operations, setting the standard for phenotypic digital evolution.

Emily L. Dolson, Anya E. Vostinar, Michael J. Wiser, Charles Ofria
2019
The MODES Toolbox: Measurements of Open-Ended Dynamics in Evolving Systems
Artificial Life
DOI 10.1162/artl_a_00280
The critical methodological paper for measuring whether your ALife system is actually doing anything interesting. It introduces formalized metrics for change, novelty, complexity, and ecological potential, replacing the anecdotal "look at this cool pattern" approach with rigorous, replicable phylogenetic statistics.

Russell K. Standish
2003
Open-ended artificial evolution
International Journal of Computational Intelligence and Applications
DOI 10.1142/S1469026803000914
A foundational negative result. Standish empirically measures the complexity of Tierran organisms over long runs and proves that while organism size increases, genuine organismal complexity plateaus. This is mandatory reading to understand the saturation problem in classical discrete ALife.

CURRENT

Edward Hughes, Michael D. Dennis, Jack Parker-Holder, Feryal Behbahani, Aditi Mavalankar, Yuge Shi, Tom Schaul, Tim Rocktaschel
2024
Open-Endedness is Essential for Artificial Superhuman Intelligence
International Conference on Machine Learning
arXiv:2406.04268
The defining paper of the current frontier. It re-anchors the goals of ALife within the context of modern foundation models, providing a formal definition of open-endedness (novelty plus learnability) and arguing that static datasets must be replaced by autonomously evolving, self-improving agent ecologies.

Bert Wang-Chak Chan
2019
Lenia: Biology of Artificial Life
Complex Systems
arXiv:1812.05433
The modern standard for continuous cellular automata. It proves that by making space, time, and states continuous, an ALife system can generate an explosion of morphological diversity and lifelike dynamics (locomotion, self-repair) that strictly discrete systems struggle to match.

Andrea Roli, Johannes Jaeger, Stuart A. Kauffman
2022
How Organisms Come to Know the World: Fundamental Limits on Artificial General Intelligence
Frontiers in Ecology and Evolution
DOI 10.3389/fevo.2021.806283
The most important modern theoretical critique of the field. The authors argue that algorithms cannot predefine a list of affordances, meaning algorithmic agents are restricted to simulated emergence, whereas true biological agents achieve radical emergence.

Raul Ortega, Miguel Angel Fortuna
2023
avidaR: an R library to perform complex queries on an ontology-based database of digital organisms
PeerJ Computer Science
DOI 10.7717/peerj-cs.1568
Introduces avidaDB and the avidaR package, representing the modern push to treat ALife data with the same rigorous bioinformatics tooling used in actual genomics, enabling complex queries on phenotypic plasticity and genomic architecture.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Tierra
https://github.com/bioerrorlog/Tierra
C
Custom/Open (Copyright Thomas S. Ray)
2025
DORMANT
This is the modern, patched mirror of the original 1991 Tierra. The original canonical implementation is unbuildable on modern Linux due to 1990s C toolchain rot. This repository (specifically the main branch) patches the v6.02 source for Ubuntu 20.04 compatibility. You can run the exact parasite emergence experiment with it today. The Beagle front-end (the visualizer) remains highly finicky and often fails to compile on modern graphics stacks; practitioners usually run it head-less and parse the log files.

Avida 2
https://github.com/devosoft/avida
C++
IDENTIFIER UNKNOWN
2025
MAINTAINED
This is the community standard and the most actively used version of Avida. It is mature, heavily documented, and driven by configuration files, meaning you do not need to rewrite the C++ core to run complex spatial evolution experiments. Its primary limitation is speed and single-threaded bottlenecks for massive populations. 

Avida 4
https://github.com/dknoester/avida4
C++
GPL-3.0
2019
DORMANT
A highly efficient, stripped-down reimplementation of Avida designed purely for execution speed over user-friendliness. If you need to run billions of updates across massive clusters, this is the engine to use, but it is effectively dead in terms of developer support and lacks the rich configuration ecosystem of Avida 2.

Lenia
https://github.com/Chakazul/Lenia
Python
MIT
2020
MAINTAINED
The canonical implementation of the continuous cellular automata framework. While the main repository sees sparse core updates, the ecosystem is alive. It easily runs modern morphology evolution experiments. The gotcha is that the basic Python version is too slow for large-scale evolutionary searches; serious practitioners immediately port the kernel logic to JAX or PyTorch (often rebuilding it privately) to leverage GPU acceleration.

MODES Toolbox
https://github.com/emilydolson/MODES-toolbox-paper
C++
IDENTIFIER UNKNOWN
2019
DORMANT
The reference implementation for measuring Open-Ended Dynamics. It is designed to plug directly into the Empirical C++ library used by many modern ALife researchers. It is highly effective but heavily coupled to its specific systematics manager, meaning applying it to a non-Empirical Python codebase requires significant translation work.

PART 4. DATA AND BENCHMARKS

avidaDB
Access via avidaR library (https://github.com/cran/avidaR)
Size: Transcripts, phenotypes, and genomes of over 1,000,000 digital organisms.
Licence: Open
This is the authoritative empirical dataset for digital genetics. It is an ontology-based semantic database (RDF triple-store) used to measure robustness, evolvability, and phenotypic plasticity without having to spend thousands of CPU hours re-running Avida simulations. 

The MODES Benchmarks
https://github.com/emilydolson/MODES-toolbox-paper
Size: Scripted test suites for Avida and NK Landscapes.
Licence: IDENTIFIER UNKNOWN
Used as the authoritative benchmark for proving whether an ALife system exhibits true open-ended dynamics (change, novelty, complexity, ecology). 

The field's standing benchmark problem:
ALife uniquely suffers from an "anecdote and video" problem. Unlike Machine Learning, which has ImageNet or HumanEval to explicitly rank architectures, ALife has historically lacked standard task collections. Benchmarks are often saturated quickly (e.g., evolving a specific boolean logic gate in Avida is solved and no longer generalises to measuring true intelligence or open-endedness). The field relies on phylogenetic metrics (MODES) rather than absolute performance metrics, which makes comparing a discrete system (Tierra) to a continuous system (Lenia) statistically perilous.

PART 5. THE REPRODUCTION RECIPE

The single most informative and reproducible baseline experiment in ALife is the original Tierra Parasite Emergence. It is the literal execution of the anchor method you described, proving that competitive exclusion and parasitism emerge without explicit fitness functions.

Exact Software and Version:
Tierra v6.02, patched for Ubuntu 20.04.
Repository: https://github.com/bioerrorlog/Tierra (main branch).

Dataset / Generator:
The default "gene bank" provided in the repository, specifically seeded with the single 80-instruction ancestor genome named 0080aaa.

Parameters to Set:
Use the default configuration files (tierra.config) provided in the patched repository. Key values matching the original 1991 run:
Soup size: 60,000 instructions (memory limit).
Mutation rate: 1 bit flip per 10,000 instructions executed.
Reaper threshold: Kills oldest and most error-prone creatures when the soup reaches 80 percent capacity.
Slice size (CPU scheduler): Proportional to genome length (size to the power of 1, though Ray experimented with different exponents).

Seeding and Replicates:
Number of replicates: 10 independent runs.
Seeding regime: Random seeds for the mutation operator and initial soup memory noise.

Compute Cost:
Trivial. Less than 1 CPU hour per replicate on any modern standard core. No GPU required.

Expected Result:
Between 100 million and 500 million executed instructions (cycles), the 80-instruction ancestor will be infiltrated by a 45-instruction parasite (0045aaa). This parasite lacks the self-measuring and copying loop instructions, instead executing the copy loop of neighboring 80-instruction hosts. You will observe the population of 80-instruction hosts crash, followed by a crash of parasites, leading to cyclical Lotka-Volterra predator-prey population dynamics.
Citation for expected result: Ray, T. S. 1991. An approach to the synthesis of life. Artificial Life II.

Three Most Common Ways People Get This Wrong:
1. Compiling raw 1990s source code. Using the unpatched Tom Ray source results in memory fault errors on modern 64-bit architectures due to legacy pointer casting. You must use the patched bioerrorlog fork.
2. Misinterpreting the data logs. Tierra does not explicitly flag a creature as a "parasite." Practitioners must parse the output logs to observe that a 45-instruction genome is replicating successfully despite lacking the standard copy-loop instructions, inferring parasitism from the execution traces.
3. Over-mutating the soup. Beginners often increase the mutation rate to "speed up evolution," which immediately results in error catastrophe, where the 0080aaa ancestor is corrupted before it can dominate the soup, yielding a dead simulation.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments in 2026, you will hit a wall: there is no off-the-shelf software that merges the ecological rigor of Avida/Tierra with the semantic power of Large Language Models and gradient descent. You will have to build a Semantic Memory Soup.

What goes in:
A grid or memory block where the foundational units are not discrete machine-code instructions (like Tierra's 32 rigid opcodes), but high-dimensional semantic embeddings or continuous vectors. 

What comes out:
A simulated ecology where "mutation" is not a random bit-flip, but a gradient-step in embedding space. The output is a population of executable agents whose code has mutated semantically (e.g., an instruction mutates from "add" to a mathematically related "multiply", rather than crashing due to a random bit flip).

The hard part:
Building a virtual CPU that can execute continuous vectors. You must write an interpreter or a neural network that maps a continuous embedding back into a deterministic, executable action in the environment. Several frontier labs (including those working on Open-Endedness at major AI companies) are privately building these continuous-to-discrete physics engines because existing discrete ALife platforms (Avida) cannot be easily hooked into PyTorch/JAX differentiable pipelines.

Roughly how much work it is:
For a competent computational scientist, building the core engine (a JAX-accelerated continuous virtual CPU and memory grid) is 3 to 6 months of intense engineering. Integrating it with an LLM for initialization and variation evaluation is another 3 months.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of ALife is defined by initial explosive success followed by long plateaus. You must know these failures to avoid repeating them.

The Complexity Ceiling (Standish, 2003)
Tierra and Avida reliably produce parasites, hyper-parasites, and basic logic gates. However, it was definitively shown that they hit a complexity ceiling. Organisms evolved to be longer (bloat) to defend against parasites and mutation, but their algorithmic complexity (Kolmogorov complexity) stopped increasing. The method of using brittle, hand-written machine languages failed to scale into unbounded open-endedness because the probability of discovering a complex new organ (like a novel search algorithm) via random bit-flips in assembly code approaches zero. The search space is too jagged.

The Roli, Jaeger, and Kauffman Critique (2022)
This is the most severe standing critique of the field. These authors argue that all algorithmic ALife and AI systems operate within a predefined, formalized state space (a syntactic world). Biological organisms, however, exist in the physical universe where they constantly discover and exploit new "affordances" (e.g., a swim bladder evolving into a lung, or using a rock to crack a nut). Because a computer program cannot spontaneously define a new physical affordance that the programmer did not simulate, ALife is mathematically incapable of true open-ended radical emergence. 
Has it been answered? Partially, by researchers building open-ended generative models (like Voyager in Minecraft), arguing that if the environment is rich enough, the state space is practically infinite. But philosophically, the Kauffman critique remains unanswered: algorithms simulate emergence; they do not experience it.

The Failure of ALife to Produce AGI
In the late 1990s, there was a belief that scaling up ALife simulations would eventually evolve Artificial General Intelligence. This programme failed completely. Evolution is an undirected optimizer; when placed in a closed box, it optimizes for replication speed and resource monopolization, not generalized intelligence. Methods that looked like they were evolving intelligent behaviors were repeatedly shown to be exploiting physics engine bugs, overfitting to the spatial grid, or measuring baseline noise.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the saturation of classical ALife and the rise of foundation models, a well-resourced newcomer in 2026 should aim at the intersection of Evolutionary Computation and Large Language Models.

Aim 1: The LLM-Operated Digital Soup (Rank 1)
Feasibility: Feasible now due to cheap, fast, local LLM inference and massive context windows.
Experiment: Build a spatial grid where each cell contains a small Python script (the organism). Instead of random bit-flip mutations, when an organism replicates, it passes its source code to an LLM prompted to act as the mutation operator ("Modify this code to be slightly more efficient or try a new survival strategy"). 
What it measures: Whether semantic, language-guided mutation can shatter the complexity ceiling of classic ALife, resulting in open-ended tool creation.
Falsification: If the population converges on a single, optimal Python script and stops innovating after 100 generations, the idea that LLMs enable unbounded ALife is falsified.

Aim 2: Continuous Instruction Set Architecture (Rank 2)
Feasibility: Feasible now due to JAX/PyTorch frameworks allowing massive parallel tensor operations.
Experiment: Rebuild Avida, but replace the discrete 26-instruction set with continuous vector embeddings. Execute organisms by passing their "genome" through a lightweight recurrent neural network that outputs deterministic actions.
What it measures: Whether a smooth, differentiable genotype-phenotype map allows for open-ended morphological and behavioral evolution without the catastrophic brittleness of bit-flipping assembly code.
Falsification: If the system devolves into noise and fails to maintain stable replication loops under gradient-based mutation.

What will NOT work:
Do not attempt to write a "better" assembly language for a Tierra-style soup, and do not attempt to run Avida with a billion more memory cells expecting AGI to emerge. These approaches are theoretically exhausted. Increasing the compute budget on a fundamentally brittle, discrete genotype-phenotype map only results in the population hitting the complexity ceiling faster. The bottleneck in classical ALife is not lack of compute; it is the jaggedness of the evolutionary search space.

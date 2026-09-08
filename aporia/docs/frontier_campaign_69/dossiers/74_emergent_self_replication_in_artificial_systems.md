# Prompt 74: Emergent Self-Replication in Artificial Systems

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdRMjJmYW96TEZyYTFfdU1QX01TUC1BSRIXUTIyZmFvekxGcmExX3VNUF9NU1AtQUk
**Elapsed:** 334s

---

# Frontier Practitioner Dossier: Emergent Self-Replication in Artificial Systems

Key Points:
* Spontaneous emergence of self-replicating programs from random, unselected instruction soups is now a verified empirical phenomenon, transitioning the field from seeded artificial life to true de novo biogenesis simulations cite: 1, 5, 10.
* The frontier, as of 2026, has shifted from merely demonstrating emergence to studying the co-evolution of self-replication and complex functional behaviors, such as mathematical task-solving, within spatially constrained digital environments cite: 7, 21.
* Measurement remains the field's central methodological bottleneck. Detecting a genuine replicator against a background of persistent noise or parasitic loops relies on proxy metrics like high-order entropy (Shannon entropy minus compressed length) and token tracing, which are effective but computationally imprecise cite: 1, 78, 82.
* The choice of computational substrate (the instruction set architecture) dictates whether replication emerges at all. Substrates with short minimum replicator lengths (BFF, Forth, Z80) are highly fertile, while those requiring long complex sequences (SUBLEQ) remain barren cite: 6, 78.
* Theoretical consensus is building around the idea that self-replication is not a biological miracle but a computational inevitability—a stable fixed point or attractor in resource-bounded algorithmic probability cite: 10, 44.

This report is designed for a computational scientist equipped to build and scale simulations, providing the tacit knowledge required to execute frontier experiments in emergent artificial life. It bypasses historical surveys in favor of actionable, concrete operational details, outlining exactly what to run, what to measure, and where the live controversies lie.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the study of emergent self-replication in computational substrates sits at the intersection of Artificial Life (ALife), Algorithmic Information Theory, and Machine Learning. Historically, this field was dominated by simulations like Tierra and Avida, which seeded a hand-written self-replicating ancestor into a memory grid and watched it mutate. That approach successfully modeled Darwinian evolution but assumed away the hardest problem: abiogenesis, or the leap from chaotic pre-life to the first replicator. The modern field, catalyzed heavily by research from Google's Paradigms of Intelligence team from 2024 to 2026, is defined by proving that self-replicators arise spontaneously from purely random initial conditions without explicit fitness functions, selection pressures, or background mutation rates. The environment itself—a bounded memory tape executing simple instructions—is sufficient to drive the phase transition from noise to purposive copying cite: 1, 5, 7.

What is SETTLED: It is now an empirically verified fact that self-replicating programs reliably emerge from purely random instruction soups in certain Turing-complete languages. This transition happens rapidly and is characterized by a sharp drop in the number of unique byte tokens and a spike in complexity. It is also settled that this phenomenon does not require background thermal noise (random bit flips); the self-modification of the programs interacting with one another is sufficient to discover the copying mechanism cite: 1, 5. Furthermore, it is theoretically settled that under resource-bounded universal induction, self-constructing programs (quines) act as stable fixed points, meaning replication is a thermodynamic and algorithmic inevitability rather than a statistical fluke cite: 10, 44.

What is CONTESTED: The primary live disagreement revolves around substrate bias and measurement validity. One side (including researchers like Agüera y Arcas and Mordvintsev) argues that minimal instruction sets like BFF or real-world architectures like the Z80 natively support emergence because computation inherently favors replication cite: 15, 18. The opposing side argues that these results are heavily biased by the chosen instruction sets. A vocal critique points out that architectures like the Z80 contain built-in block copy instructions (LDIR and LDDR). When random combinations happen to trigger a block copy, it looks like emergent life, but skeptics argue it is merely the execution of a hardcoded pattern generator rather than genuine, autonomous self-replication cite: 3. Additionally, the field contests the measurement of complexity. The canonical method uses "high-order entropy," approximated by compressing the soup with the Brotli algorithm cite: 78, 80. Purists argue that relying on commercial compression algorithms as a proxy for Kolmogorov complexity introduces severe artifacts.

What is OPEN: The frontier is currently focused on the co-evolution of replication and arbitrary functional tasks. A major open question is how to reliably induce replication in hostile substrates like SUBLEQ, where the shortest possible replicator is too long to arise by chance cite: 6, 78. Another open frontier is identifying the precise mathematical threshold of instruction set expressiveness that guarantees emergence. 

In the last three years, the field moved entirely away from hand-seeded ALife models. If a paper in 2026 assumes a pre-existing replicator, it is considered evolutionary biology, not origin-of-life research. The field has absorbed much of the "Open-Endedness" community from AI, as researchers realized that true open-ended evolution in neural networks might require the same spontaneous replication dynamics observed in these minimal assembly soups cite: 24, 70.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Agüera y Arcas, B., Alakuijala, J., Evans, J., Laurie, B., Mordvintsev, A., Niklasson, E., Randazzo, E., Versari, L.
Year: 2024
Title: Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction
Venue: arXiv
Identifier: arXiv:2406.19108
This is the paper that rebooted the field. It demonstrates that self-replicators emerge spontaneously from random noise in a Brainfuck variant (BFF) and introduces the high-order entropy and token-tracing metrics used to prove the transition cite: 1, 80. A practitioner must know this to understand the baseline experimental harness.

Authors: Sarkar, A.
Year: 2026 (v2)
Title: The computational inevitability of life: self-replication under resource-bounded nested algorithmic probability
Venue: arXiv
Identifier: arXiv:2010.09646
Provides the formal mathematical framework explaining why the empirical results of Agüera y Arcas are inevitable. It frames self-replication not as an evolutionary accident but as a stable fixed point (attractor) in program space under finite memory and time constraints cite: 10, 44, 73.

Authors: Ray, T. S.
Year: 1991
Title: An approach to the synthesis of life
Venue: Artificial Life II
Identifier: IDENTIFIER UNKNOWN
The canonical paper on Tierra. While its method (seeding a hand-written ancestor) is outdated for biogenesis research, it defines the vocabulary of digital parasitism, hyper-parasitism, and instruction-set vulnerability that modern researchers still use to classify emergent behaviors cite: 5, 36.

Authors: Pargellis, A. N.
Year: 1996
Title: The spontaneous generation of digital life
Venue: Physica D
Identifier: IDENTIFIER UNKNOWN
An early, often-overlooked attempt at spontaneous generation using the Amoeba system. It provides crucial historical context on the difficulty of getting robust self-replicators without guiding the soup heavily cite: 36, 38.

Authors: Marletto, C.
Year: 2015
Title: Constructor theory of life
Venue: Journal of The Royal Society Interface
Identifier: DOI 10.1098/rsif.2014.1226
A theoretical physics perspective on how programmable constructors (replicators) can emerge from elementary substrates, heavily influencing the modern shift toward substrate-independent computational definitions of life cite: 44.

CURRENT SOURCES DEFINING THE FRONTIER

Authors: Cicala, F., Niklasson, E., Randazzo, E., Boukortt, S., Basti, A., Etcheverry, M., Saurous, R. A., Laurie, B., Manyika, J., Agüera y Arcas, B., Richards, B. A.
Year: 2026
Title: Co-evolution of self-replication and function in a digital primordial soup
Venue: arXiv
Identifier: arXiv:2607.09211
The current absolute frontier. It proves that spontaneous replication and complex task-solving (like polynomial evaluation) can co-evolve from random noise when placed in spatial niches with metabolic constraints cite: 7, 21.

Authors: Kumar, A., Lu, C., Kirsch, L., Tang, Y., Stanley, K. O., Isola, P., Ha, D.
Year: 2025
Title: Automating the search for artificial life with foundation models
Venue: Artificial Life
Identifier: IDENTIFIER UNKNOWN
Explores how Large Language Models can be utilized to discover or optimize instruction sets and environmental conditions that foster spontaneous artificial life, bridging the gap between minimal ISAs and modern generative AI cite: 44.

Authors: Cotler, J., Hongler, C., Hudcová, B.
Year: 2025
Title: Self-replication and computational universality
Venue: arXiv
Identifier: arXiv:2510.08342
A rigorous theoretical follow-up that ties the empirical emergence of self-replication directly to the requirements of computational universality, confirming that local universality does not guarantee replication while global universality does cite: 44.

Authors: Valente, D.
Year: 2021
Title: Self-replication of a quantum artificial organism driven by single-photon pulses
Venue: arXiv
Identifier: arXiv:2105.00624
While slightly older, this paper is highly relevant at the frontier for linking the information-processing of self-replication to the dissipation of physical energy (dissipative adaptation), modeling how these principles apply at the quantum mechanical level cite: 70, 71.

PART 3. SOFTWARE I CAN ACTUALLY RUN

cubff
URL: https://github.com/paradigms-of-intelligence/cubff
Language: C++, CUDA, Python
Licence: Apache 2.0
Year: 2025
Maturity: MAINTAINED
This is the reference implementation from Google's Paradigms of Intelligence team. It runs the exact 0D (well-mixed) and 1D/2D spatial primordial soup experiments detailed in Agüera y Arcas (2024). It is written in C++ with optional CUDA acceleration, making it the only tool capable of simulating millions of interactions per second on a GPU cite: 49. It uses Brotli compression for the entropy measurements. Gotchas: The Python bindings exist in a single file (cubff.py) and lack extensive documentation. Modifying the BFF instruction set requires rewriting core C++ headers (bff.inc.h) and recompiling cite: 52.

computational-life
URL: https://github.com/gustavsoderstrom/computational-life
Language: Python (Numba)
Licence: IDENTIFIER UNKNOWN
Year: 2024
Maturity: MAINTAINED
A pure Python reimplementation of the cubff paper. It runs the exact same 0D primordial soup experiment but is designed for accessibility rather than massive scale. It uses Numba for JIT compilation to keep CPU speeds reasonable cite: 11, 81. Gotchas: Instead of using Brotli for the high-order entropy calculation, this implementation uses Python's standard zlib. Because compression ratios differ between algorithms, the absolute numerical threshold for detecting a "state transition" here (spiking above 3.0) will not perfectly match the Brotli numbers published in the canonical paper cite: 81.

zff
URL: https://github.com/znah/zff
Language: Zig, WebAssembly, JavaScript
Licence: IDENTIFIER UNKNOWN
Year: 2024
Maturity: MAINTAINED
Created by Alexander Mordvintsev (co-author of the Google paper), this is an interactive explorer specifically for the Z80 architecture experiments cite: 54, 57. It implements a 2D grid of 16-byte Z80 programs interacting via a modified Z80 emulator. It runs directly in the browser via WASM. Limitations: It is primarily an interactive visualization and exploratory tool. It is not designed to be run headless on a compute cluster for large-scale data collection.

Tierra / Avida
URL: IDENTIFIER UNKNOWN
Language: C
Licence: IDENTIFIER UNKNOWN
Year: 1991 / 2004
Maturity: DORMANT
These are the famous, historical ALife engines cite: 5. While Avida is still technically compilable, both are effectively dead for frontier biogenesis research because they are intrinsically designed around seeding a pre-written organism and defining external fitness landscapes. Do not use these to study spontaneous emergence.

PART 4. DATA AND BENCHMARKS

In this field, static datasets do not exist. The phenomenon relies on dynamic generative execution. The "dataset" is a random initialization matrix, usually populated by a cryptographic or high-quality pseudorandom number generator.

Instead of datasets, the field relies on continuous order parameters (metrics) to benchmark the success and speed of emergence.

Metric 1: High-Order Entropy (The Authoritative Benchmark)
URL: N/A (Computed inline via compression libraries)
Size: Evaluated over the entire soup memory (e.g., 2 to the power of 17 programs of 64 bytes).
What it measures: The gap between Shannon entropy and Kolmogorov complexity cite: 1, 82.
Details: In a soup initialized with random noise, Shannon entropy (symbol diversity) and Kolmogorov complexity (incompressibility) are both high, so their difference is near zero. When a replicator takes over, the tape becomes highly ordered. The Shannon entropy might remain somewhat stable due to mutations, but the Kolmogorov complexity drops massively because the whole soup can be described as "N copies of this specific loop." Thus, high-order entropy spikes.
Overfitting/Contamination: This benchmark is highly contaminated by the choice of compression algorithm. Brotli v1.1.0 is the canonical compressor cite: 80. Using zlib (as in the Python reimplementations) yields different scalar values. Practitioners must benchmark their specific compressor against a known uniform random baseline to establish a valid threshold.

Metric 2: Unique Token Count (The "Radioactive Tracer")
URL: N/A
Size: One 64-bit integer per byte of soup memory.
What it measures: The lineage and physical copying of specific bytes in memory cite: 2, 82.
Details: At epoch 0, every byte in the soup is assigned a unique identifier (token). When the interpreter executes a copy instruction, it copies both the byte value and the token.
Overfitting/Contamination: Token counts strictly measure exact physical byte copying. If a program invents a way to "recreate" itself by performing math rather than direct memory copying, token tracing will fail to detect it. 

Metric 3: Time to First Replicator (TFR)
URL: N/A
What it measures: The number of pairwise interaction epochs required before High-Order Entropy crosses a standard deviation threshold above the noise floor.
Details: This is censored data; in some environments (like SUBLEQ), TFR is infinite within feasible compute bounds cite: 6, 78.

PART 5. THE REPRODUCTION RECIPE

The most reproducible and informative baseline experiment is the 0D (well-mixed) Primordial Soup in the BFF language, as published by Agüera y Arcas et al. (2024).

Exact Software and Version:
Use the `cubff` repository, specifically the CUDA implementation on the `main` branch (commit roughly circa late 2024) cite: 49.

Parameters and Values:
* Substrate: BFF (Brainfuck extended with self-modification and a read/write head).
* Soup Size: 2 to the power of 17 individual programs (131,072 programs).
* Program Length: 64 bytes per program.
* Initial State: Uniform random bytes (0 to 255). Note that only 10 byte values correspond to actual BFF instructions, so 96 percent of the initial tape acts as inactive junk/data cite: 11, 78.
* Execution Limit: 2 to the power of 13 steps per interaction.
* Mutation Rate: 0.00024 (0.024 percent chance of a random bit flip per byte per epoch). For a purist experiment, set this to 0.0 to prove emergence via pure self-modification cite: 11.

Execution Loop:
In each epoch, shuffle the 131,072 programs. Pair them up. For each pair, concatenate them into a single 128-byte tape. Execute the BFF interpreter on that 128-byte tape until it halts or hits the execution limit. Split the 128-byte tape back into two 64-byte halves. Overwrite the original two programs with these new halves cite: 11, 78.

Compute Cost:
Extremely cheap. On a modern GPU (e.g., NVIDIA A100 or RTX 4090), running this to the state transition takes only minutes to a few hours.

Expected Result:
According to the published numbers, a state transition (emergence of stable self-replicators) occurs in roughly 40 percent of independent runs within 16,000 epochs cite: 67. You should observe the Brotli-based high-order entropy remain near 0 for several thousand epochs, then violently spike upward, while the unique token count drops from approximately 8 million to a few thousand cite: 55, 80.

The Three Most Common Ways People Get This Wrong:
1. Mishandling the Palindrome Execution Wrap-Around: Self-replicators in BFF often rely on a palindrome structure so they can copy themselves backward or forward across the boundary of the 128-byte concatenated tape cite: 2, 11. If your interpreter does not enforce the exact modulo arithmetic on the memory boundaries defined in `bff.inc.h`, the emergent replicators will crash and die.
2. Compression Algorithm Mismatch: Expecting the entropy spike to hit the exact scalar value printed in the Google paper while using standard Python `zlib` instead of `brotli`. You must normalize your complexity metric against a known random baseline.
3. Incorrect Zero-Poisoning Handling: During early epochs, "zero-poisoning" occurs where tapes get filled with zeros because random programs tend to overwrite data with empty bytes cite: 55. If your initial interpreter implementation optimizes away zero-execution loops incorrectly, you will alter the algorithmic probability space and prevent emergence.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments rather than replicate the 2024 paper, you will find a severe lack of generalized infrastructure. The following components do not exist off-the-shelf and must be built:

1. A Cross-ISA Universal Soup Harness
What goes in: An arbitrary Instruction Set Architecture definition (e.g., x86, RISC-V, Z80, SUBLEQ, custom ISA) and environment rules (0D mixed, 2D spatial).
What comes out: A high-performance simulation loop that executes the pairwise interactions natively.
The hard part: Currently, cubff only natively supports BFF and requires deep C++ refactoring to change the instruction set. The Z80 experiments were done in an entirely separate Zig/WASM codebase cite: 54. A serious entrant needs a harness that can JIT-compile arbitrary ISAs to GPU kernels so that the thermodynamic properties of different assembly languages can be compared side-by-side. 
Work estimate: 2 to 3 months for a senior systems engineer to build a generalized CUDA/PTX translation layer.

2. A Mathematically Rigorous Kolmogorov Complexity Estimator
What goes in: A snapshot of the soup memory.
What comes out: A scalar value representing the true algorithmic complexity.
The hard part: The field currently relies on Brotli or zlib compression to approximate Kolmogorov complexity cite: 78. These LZ77/Huffman-based algorithms look for literal byte repetitions. They completely fail to compress algebraically generated complexity (e.g., a program that replicates by generating its instructions via mathematical operations rather than `LDIR` block-copying). You would need to build an estimator based on algorithmic probability theory or program synthesis (e.g., searching for the shortest program that generates the soup).
Work estimate: 4 to 6 months of active research, as this borders on open algorithmic information theory problems. Several private groups are currently trying to replace Brotli with lightweight LLM-based token predictors to measure complexity (cross-entropy), which is a strong signal of a tooling gap.

3. Spatiotemporal Lineage Visualizer for Billions of Tokens
What goes in: Token trace logs from a 2D spatial grid experiment.
What comes out: A visual phylogenetic tree showing how specific copy-loops swept spatially across a grid.
The hard part: Managing the sheer volume of data. Tracking the lineage of every byte in a 240x135 grid over 1,000,000 epochs generates terabytes of token provenance data. 

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

This field is heavily constrained by what fails. Understanding the negative results is more important than memorizing the successes.

The SUBLEQ Failure (Negative Result)
The most informative negative result in the 2024 computational life literature is the failure of SUBLEQ. SUBLEQ is a Turing-complete language with a single instruction ("Subtract and Branch if Less than or Equal to Zero"). Despite being fully Turing-complete, exhaustive simulations failed to produce any spontaneous self-replicators cite: 6, 15, 79. The reason is structural: the minimum program length required to execute a self-copying loop in SUBLEQ is extremely long. In a random soup of 64-byte or 128-byte tapes, the probability of assembling that specific long sequence by random mutation or interaction is astronomically low cite: 78. This proves that Turing completeness is a necessary but insufficient condition for the emergence of life; the substrate must possess a short minimum replicator length.

The Z80 LDIR Critique (Standing Critique)
A major methodological critique was leveled against the results generated using the Z80 emulator cite: 15, 18. Critics point out that the Z80 architecture has built-in instructions specifically designed for block memory copying—namely, `LDIR` (Load Increment Repeat) and `LDDR` (Load Decrement Repeat) cite: 3. The critique argues that feeding random noise into an architecture that already has a "copy yourself" command built into the hardware is not a profound demonstration of emergent life. It is merely triggering a pre-existing pattern generator. Proponents counter that the `LDIR` instruction emerged spontaneously as a survival mechanism from earlier, stack-based copying programs, demonstrating an evolutionary arms race rather than a cheap shortcut cite: 3, 57. However, the critique stands unanswered for purists: relying on CISC architectures with complex built-in memory operations obscures whether the replication is genuinely emergent or hardware-induced.

The Tierra / Hand-Coded Ancestor Critique
Historically, the entire first wave of Artificial Life (Tierra, Avida) failed to answer the question of abiogenesis because they initialized their memory with a hand-written, fully functional self-replicator cite: 5. Later analysis showed that this "assumes away the hardest question" and studies only the decay and parasitism of an already-living system. The field has completely internalized this critique; any experiment in 2026 that seeds a working ancestor is considered invalid for studying the origin of life.

The Thermodynamics / Entropy Illusion
Schrödinger suggested life involves decreasing local entropy at the cost of global entropy cite: 30, 33. Critics of computational ALife point out that digital soups do not actually have thermodynamic energy constraints unless artificially imposed. Cicala et al. (2026) answered this critique by introducing "metabolic constraints" (e.g., early halting if a program fails a task, conserving CPU cycles) cite: 21, 60. However, standing critiques maintain that without true physical thermodynamics, digital emergence is just a study of abstract automata attractors, not "life."

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you are a well-resourced entrant with compute, do not rebuild BFF and do not run 0D soups. Aim for the specific, ranked experiments below that push the open frontier.

1. The "Hostile Substrate" Falsification Experiment (Rank 1 - Highly Feasible)
Experiment: Design a custom Turing-complete instruction set that is explicitly engineered to be hostile to self-replication. For example, make memory reads destructive (reading a byte sets it to zero), or require cryptographic hashing to write to adjacent memory cells. Initialize this in a spatial grid and run it for billions of epochs using heavy GPU scaling. 
What it measures: Does resource-bounded algorithmic probability (Sarkar's theory cite: 10, 44) always force the emergence of quines, even when the physics of the environment actively suppresses copying?
Falsification: If replicators never emerge despite massive compute, it falsifies the idea that replication is universally inevitable in Turing-complete spaces, proving that emergence is strictly bounded by the physical "chemistry" (the ISA) of the environment.

2. Co-evolution of Generalization via LLM-designed ISAs (Rank 2 - Feasible)
Experiment: Extend Cicala's 2026 work on task-solving cite: 21. Instead of validating programs on a single fixed polynomial math task, place them in a 3D grid where the mathematical tasks shift dynamically. Use an LLM to design the minimal instruction set architecture that runs the soup cite: 44. 
What it measures: Will emergent replicators develop generalized computational modules (functions/subroutines) that persist across replication events to solve shifting environments?
Falsification: If the replicators simply discard the task-solving machinery and revert to pure `LDIR`-style copying the moment the task changes, it proves that digital parasitism overrides functional complexification in unguided open-ended environments.

3. Continuous Entropy via Neural Prediction (Rank 3 - Conceptually Hard)
Experiment: Run the standard BFF soup, but replace Brotli compression with a small, causal Transformer model trained on-the-fly to predict the next byte in the soup. Use the cross-entropy loss of the model as the true measure of algorithmic complexity.
What it measures: It detects complex, non-repeating replicators that evade LZ77 compression. It measures the true predictive complexity of the digital life.
Falsification: If the Transformer's cross-entropy drops identically to the Brotli compression ratio, it suggests that emergent digital life is strictly limited to simple periodic copying, rather than generating deep algorithmic complexity. 

What will NOT work:
Attempting to scale the Z80 2D grid experiment to billions of programs to watch macro-organisms evolve will not work. The 2024 and 2026 papers show that once a replicator dominates, the soup suffers an ecological collapse into a homogeneous state, occasionally perturbed by simple parasites cite: 8, 42. Without explicit spatial boundaries or highly complex metabolic cost functions, massive scale only results in massive homogeneity. More compute does not solve the open-endedness bottleneck; changing the rules of the substrate does.

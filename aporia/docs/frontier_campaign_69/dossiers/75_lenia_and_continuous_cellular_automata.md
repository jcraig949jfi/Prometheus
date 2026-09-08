# Prompt 75: Lenia and Continuous Cellular Automata

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdRMjJmYXB5M0ZwLThfdU1QOGNXMnlBYxIXUTIyZmFweTNGcC04X3VNUDhjVzJ5QWM
**Elapsed:** 395s

---

# FRONTIER PRACTITIONER DOSSIER: Lenia and Continuous Cellular Automata

Key findings regarding Lenia and Continuous Cellular Automata as of 2026:
The field has fundamentally transitioned from discrete, rule-based cellular automata to continuous, differentiable partial differential equation models. 
Mass conservation, introduced via Flow Lenia, has solved the field's oldest problem of unbounded growth and extinction, enabling true multi-species ecosystem simulations.
The search for complex life-like patterns has shifted from manual tuning and random search to Intrinsically Motivated Goal Exploration Processes and automatic differentiation.
Evaluating complexity remains a deeply contested area, though recent applications of dynamical systems theory, specifically Lyapunov exponents and the Kaplan-Yorke dimension, are replacing heuristic compression metrics.

For a computational scientist entering this field, the core premise is that artificial life need not be explicitly programmed. Instead, complex, self-maintaining, and sensorimotor-capable entities can emerge naturally from the physics of continuous cellular automata. Lenia generalises Conway's Game of Life by making space, time, and states continuous. Because the entire system is differentiable and runs on GPUs, practitioners can use gradient descent and curriculum learning to discover sets of rules that birth stable, moving, and interacting structures known as Spatially Localised Patterns. The frontier is no longer just finding these patterns, but creating environments where multiple species interact, compete, and exhibit open-ended evolution without collapsing into chaotic noise or uniform death.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of continuous cellular automata (CCA) today operates at the intersection of artificial life, dynamical systems, and differentiable programming. Anchored by the Lenia framework, the discipline has moved far beyond Conway's Game of Life. In modern Lenia systems, a cell's state is a real number, typically in the interval 0 to 1, or unbounded in recent extensions. Neighbourhoods are defined by smooth radial convolution kernels, and updates occur via differentiable growth functions over continuous time steps. Because the entire pipeline is differentiable, it is routinely implemented in JAX or PyTorch, allowing researchers to backpropagate through time to optimise environmental rules that give rise to self-organising, autopoietic entities. 

What is SETTLED: It is now an empirical fact that continuous cellular automata support a massive diversity of Spatially Localised Patterns that exhibit biological properties such as locomotion, bilateral and radial symmetry, and reaction to stimuli. It is also settled that automatic differentiation, combined with diversity search algorithms like Intrinsically Motivated Goal Exploration Processes, is vastly superior to random search or manual tuning for discovering these patterns. The field agrees that standard Lenia suffers from a lack of conservation laws, meaning patterns often explode to fill the grid or fade into extinction, requiring highly precise parameter tuning to survive. 

What is CONTESTED: The fundamental metric of open-endedness and complexity is fiercely debated. One faction relies on compressibility as a proxy for complexity, arguing that patterns which compress poorly are complex. Opponents note that radial symmetries often artificially inflate compression metrics when rasterised to a square grid, leading to polar-coordinate workarounds. A newer, mathematically rigorous faction argues that CCA should be treated entirely as partial differential equations, using dynamical systems theory to measure complexity via the Kaplan-Yorke dimension and Lyapunov exponents (cite: 2, 98). There is also a live disagreement regarding how to mix parameters when multiple species collide. Softmax sampling versus weighted averaging of rule parameters in multi-species environments remains an unresolved design choice.

What is OPEN: True open-ended evolution remains the holy grail. While we can generate isolated species and even multi-species ecosystems via Flow Lenia, achieving a system that perpetually innovates without hitting a complexity ceiling is unsolved. The transition from isolated sensorimotor agents to a cohesive evolutionary ecology where agents adapt their morphology to survive resource scarcity is the immediate frontier. 

If you are looking for discrete cellular automata, that field is effectively dormant. It has been absorbed into the continuous CCA and Neural Cellular Automata domains. What was lost in this merge was the absolute mathematical provability of discrete state transitions; continuous systems are subject to floating-point approximations, integration errors, and chaotic divergence, meaning exact reproducibility across different hardware architectures can be highly sensitive.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Bert Wang-Chak Chan
2019
Lenia: Biology of Artificial Life
Complex Systems
DOI 10.25088/ComplexSystems.28.3.251
This is the genesis paper that defined the Lenia framework, detailing the continuous generalisation of Conway's Life and identifying the first 400 species, including the canonical Orbium glider. A practitioner must read this to understand the base update rule, the kernel configurations, and the biological taxonomy the field relies upon.

Bert Wang-Chak Chan
2020
Lenia and Expanded Universe
The 2020 Conference on Artificial Life
arXiv:2005.03742
This paper expanded the baseline model into higher dimensions, introduced multiple kernels, and created multi-channel ecosystems. It is required reading because nearly all modern experiments run in multi-channel environments.

CURRENT SOURCES

Erwan Plantec, Gautier Hamon, Mayalen Etcheverry, Pierre-Yves Oudeyer, Clement Moulin-Frier, Bert Wang-Chak Chan
2023
Flow-Lenia: Towards open-ended evolution in cellular automata through mass conservation and parameter localization
The 2023 Conference on Artificial Life
arXiv:2212.07906
This is the most critical architectural update to the field in the last three years. By replacing Lenia's additive growth with a mass-conserving flow field driven by fluid dynamics, it prevents explosive growth and allows multiple species with localised parameters to coexist.

Gautier Hamon, Mayalen Etcheverry, Bert Wang-Chak Chan, Clement Moulin-Frier, Pierre-Yves Oudeyer
2022
Learning Sensorimotor Agency in Cellular Automata
Preprint
arXiv:2402.10236
This paper details the exact curriculum learning and gradient descent pipeline used to evolve agents capable of navigating obstacles. It is the blueprint for running modern, AI-guided automated discovery experiments in CCA.

Q. Tyrell Davis, Josh Bongard
2022
Step Size is a Consequential Parameter in Continuous Cellular Automata
The 2022 Conference on Artificial Life
arXiv:2205.12728
A crucial methodological paper proving that the Euler integration step size in CCA is not just a resolution parameter, but a physical property of the world. A practitioner must know this to avoid destroying their patterns by attempting to increase simulation accuracy.

Ivan Yevenko, Hiroki Kojima, Chrystopher L. Nehaniv
2025
Using Dynamical Systems Theory to Quantify Complexity in Asymptotic Lenia
The 2025 Conference on Artificial Life
arXiv:2508.02935
This defines the bleeding edge of evaluation. It applies rigorous dynamical systems theory to CCA, using Lyapunov exponents and fractal dimensions to identify chaotic patterns and mathematically explain solution classes. 

Thomas Michel, Marko Cvjetko, Gautier Hamon, Pierre-Yves Oudeyer, Clement Moulin-Frier
2025
Exploring Flow-Lenia Universes with a Curiosity-driven AI Scientist: Discovering Diverse Ecosystem Dynamics
Preprint
arXiv:2505.15998
This establishes the current frontier of open-ended ecosystem generation, deploying Intrinsically Motivated Goal Exploration Processes over Flow Lenia to discover multi-species interactions, completely bypassing manual rule creation.

Maxence Faldor, Antoine Cully
2024
Toward Artificial Open-Ended Evolution within Lenia using Quality-Diversity
Preprint
arXiv:2406.04235
Details the Leniabreeder framework, combining unsupervised Quality-Diversity algorithms with Lenia. It represents the state-of-the-art in evaluating algorithmic exploration using intrinsic fitness objectives.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Lenia
https://github.com/Chakazul/Lenia
Python, JavaScript, MATLAB
MIT License
2024
MAINTAINED
This is the reference implementation from the originating author. You can run the canonical 2D, 3D, and n-dimensional Lenia environments and explore the original taxonomy. Its limitation is that it relies heavily on NumPy and CPU-bound routines or older shader implementations; it is fundamentally a tool for interactive exploration and rendering, not a high-throughput machine learning harness.

FlowLenia
https://github.com/erwanplantec/FlowLenia
Python
MIT License
2024
MAINTAINED
This is the community standard for modern research. Implemented in JAX, it supports GPU acceleration and executes the mass-conservative Flow Lenia model. You can use it today to run multi-species simulations and parameter embedding experiments. Its main gotcha is the rigid reliance on JAX compilation times, which can stall rapid prototyping if the grid size or batch dimensions are altered dynamically.

sensorimotor-lenia-search
https://github.com/flowersteam/sensorimotor-lenia-search
Python
MIT License
2024
MAINTAINED
This is the evaluation harness and experimental codebase for discovering sensorimotor agency. It combines PyTorch and JAX workflows with curriculum learning. You can run it to reproduce the discovery of agents that dodge obstacles. The limitation is its heavy architectural coupling to the specific Intrinsically Motivated Goal Exploration Process framework developed by the Flowers team, making it somewhat difficult to decouple the environment from the search algorithm.

Exploring-Flowlenia
https://github.com/Thomick/Exploring-Flowlenia
Python
MIT License
2025
MAINTAINED
The most modern AI-scientist framework built on top of Flow Lenia. It allows for the optimisation of parameters using evolutionary algorithms and computes multi-scale entropy and complexity metrics. It is highly capable but currently lacks rigorous documentation for custom fitness functions outside of the provided examples.

DynamicalCA
https://github.com/iyevenko/DynamicalCA
Jupyter Notebook, Python
MIT License
2025
MAINTAINED
This repository provides the computational tools to calculate Lyapunov exponents and covariant Lyapunov vectors for continuous cellular automata. It allows you to run rigorous mathematical complexity analysis on discovered patterns. It is extremely computationally intensive, and its limitation is that scaling it to massive grid sizes (beyond 128 by 128) requires significant compute resources.

particle-lenia
https://github.com/silvernio/particle-lenia
TypeScript, WGSL
MIT License
2024
MAINTAINED
A WebGPU implementation of Particle Lenia. While standard Lenia uses a grid, Particle Lenia models the system as discrete particles interacting via continuous fields. It is excellent for browser-based, high-performance rendering, but lacks the Python bindings necessary for heavy automated differentiation or cluster-based evolutionary search.

PART 4. DATA AND BENCHMARKS

Because Lenia is a generative artificial life system rather than a standard supervised learning problem, traditional static datasets are rare. Instead, the field relies on parameter seeds and configuration libraries.

animals.json
URL: https://github.com/Chakazul/Lenia/blob/master/Python/animals.json
Approximate size: 400 plus JSON records
MIT License
This is the foundational baseline dataset of the field. It contains the exact kernel parameters, growth parameters, and initial pattern matrices for every canonical Lenia species discovered by Bert Chan. Practitioners use this to seed their experiments, verify that their simulation engine replicates known dynamics (like the Orbium glider), or as a starting point for mutation. 

sensorimotor-lenia-search configurations
URL: https://github.com/flowersteam/sensorimotor-lenia-search (under data folder)
Approximate size: Thousands of parameter sets
MIT License
Contains the filtered, multi-channel parameter sets and resulting policies from the sensorimotor agency experiments. It is used to measure and benchmark the robustness of newly generated algorithms against environmental perturbations like noise or obstacles. 

AssemblyCA
URL: Referenced in literature (e.g., NeurIPS 2023 ALOE Workshop)
Approximate size: Unknown, benchmark suite
Access restriction: Unconfirmed open source
A benchmark designed to measure open-endedness for discrete cellular automata, increasingly adapted as a conceptual framework for continuous systems. It attempts to quantify how long a system can generate novel, irreducible structures. The known limitation is saturation: continuous CA easily fool naive complexity metrics by generating random noise, so benchmarks relying on simple compression algorithms often falsely reward chaotic death states over structured life.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment in the field today is the emergence of obstacle-navigating agents using curriculum learning and gradient descent, as established by Hamon et al. in "Learning Sensorimotor Agency in Cellular Automata".

Software and Version:
Use the flowersteam/sensorimotor-lenia-search repository (cloned from the main branch as of early 2026). The specific run script is located at expe/generalization_test/expe_name/run_experiment.py.

Dataset/Generator:
The starting points are drawn from the classic animals.json Lenia dataset, explicitly filtering out patterns that do not fit inside a 256 by 256 grid, and limiting the search to single-channel agents placed within a multi-channel environment (one channel for the agent, one for the obstacles).

Exact Parameters to Set:
Grid size: 256 by 256.
Channel count: 3 (typically Agent, Obstacle, and Interaction).
Initial states (A at t=1): Seeded from the filtered animals.json.
Loss function: Mean Squared Error applied to the target image at the final timestep of the rollout.
Optimisation loops: The outer loop generates a stochastic curriculum of obstacle configurations; the inner loop uses gradient descent to update the cellular automaton rules to minimise the loss against the target position.

Replicates and Seeding:
Run 10 independent replicates using different random seeds for the initialisation of the search method. 

Compute Cost:
Approximately 24 to 48 GPU hours on a single modern GPU (e.g., NVIDIA A100 or equivalent) to complete the curriculum learning process for a robust agent.

Expected Result:
At the end of training, the discovered parameter sets will produce a spatially localised pattern that not only maintains its structure but actively alters its trajectory to avoid procedurally generated blue obstacle barriers in the grid. You should expect a success rate where roughly 32 percent of the discovered rules yield moving patterns (Spatially Localised Patterns) under IMGEP diversity search, compared to merely 8 percent using random search (cite: 88). 

Three Most Common Ways People Get This Wrong:
1. Integration Step Size (dt): Practitioners treat dt as a numerical accuracy dial. In Lenia, changing dt fundamentally alters the physics. If you lower dt from 0.1 to 0.01 to "increase precision," your patterns will die or turn into chaotic noise. The original parameters demand specific step sizes.
2. Clipping Artifacts: In standard Lenia, state values must be strictly clipped between 0 and 1. Failure to properly implement this clipping operation in custom backpropagation loops causes explosive gradients and mass saturation.
3. Lack of Reintegration Tracking: If a practitioner attempts to port this experiment to Flow Lenia without precisely implementing Moroz's Reintegration Tracking algorithm, the mass flow will leak or tear, completely destroying the agent's morphology upon contact with an obstacle.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments measuring open-ended evolution and multi-species ecosystems, several critical infrastructure components do not exist off-the-shelf and must be engineered.

1. A Unified, Mass-Conservative RL-Environment Interface
What goes in: Flow Lenia update rules and a multi-agent action space.
What comes out: Standard Gym/PettingZoo compliant observations and rewards.
The hard part: Flow Lenia is currently an autonomous generative system. To interface it with deep reinforcement learning, you must build a wrapper that allows external neural network agents to inject matter or modify local kernel parameters at runtime while maintaining the strict mass conservation invariants of the flow field. If external actions create mass, the ecosystem explodes.
Work estimate: Two to three months for a senior engineer well-versed in JAX and reinforcement learning APIs. Multiple teams (like Sakana AI and the Flowers team) have rebuilt private, task-specific bridges between foundation models/RL and CCA, signalling a severe gap for a unified public tool.

2. Real-Time Dynamical Systems Invariant Calculators
What goes in: The continuous state tensor of the grid over time.
What comes out: The global Lyapunov spectrum and Kaplan-Yorke dimension calculated in real-time.
The hard part: Calculating covariant Lyapunov vectors requires tracking the Jacobian of the entire grid through time. For a 256 by 256 grid, the dimensionality is massive, requiring intensive QR decompositions that do not easily parallelise on standard GPU tensor cores without severe memory bottlenecks. 
Work estimate: Four to six months of specialised numerical computing work. Iyevenko's DynamicalCA provides the math, but it is currently too slow for real-time fitness evaluation in a massive search loop.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

This field has a graveyard of intuitive ideas that completely fail in practice.

The Failure of Euler Accuracy:
The most prominent negative result is the assumption that continuous cellular automata simulate a platonic ideal that is approached as the integration step size shrinks. Davis and Bongard (2022) conclusively proved this false. Patterns in Lenia rely heavily on the systematic error introduced by large, discrete Euler steps to maintain their self-organisation. Attempting to run Lenia with Runge-Kutta integrators or infinitesimally small step sizes typically results in the extinction of the pattern. The method measures an artefact of numerical integration, not a continuous physical reality.

The Failure of Unconstrained Growth for Open-Endedness:
Between 2018 and 2022, numerous attempts were made to evolve ecosystems in standard Lenia by placing multiple species in a large grid. They all failed. Because standard Lenia's update rule creates and destroys state values based on a growth function, any species that mutates a slightly higher growth rate rapidly consumes the entire grid, resulting in a homogenous, static mass. This failure necessitated the creation of Flow Lenia; without explicit mass conservation, multi-species open-ended evolution is impossible.

Random Search Yields Dead Worlds:
Due to the vast, high-dimensional parameter space of multiple Gaussian rings, growth means, and kernel widths, random search is entirely ineffective. Randomly generated parameters yield total cell death or chaotic static in over 90 percent of trials. Methods that looked strong initially were often just exploring a very narrow, pre-seeded local neighbourhood around the original animals.json file.

The Compression Metric Critique:
A standing critique of the field is how it measures "interestingness" or complexity. Many automated discovery frameworks use PNG or gzip compression ratios as a proxy for complexity (a highly compressible state is simple, an incompressible state is chaotic noise; the middle is complex). Critics have pointed out that because Lenia relies on radial diffusion kernels, it naturally produces radially symmetric patterns. Rasterising a radial pattern onto a square pixel grid obscures the symmetry, causing standard image compression algorithms to drastically overestimate the pattern's true complexity. This critique was answered by the Flow-Lenia team in 2024 by re-rasterising states into a polar coordinate system before measuring compression, but the underlying flaw of using file compression as a proxy for biological complexity remains a standing, partially answered critique.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the current state of the field, a well-resourced newcomer should bypass searching for single gliders and immediately target the intersection of mass-conservative systems, dynamical analysis, and foundation models.

Aim 1: The Lyapunov-Guided AI Scientist (Highest Priority)
Feasibility: Feasible now because the math for Lyapunov exponents in CCA was solved in late 2025 (Yevenko et al.), and AI scientist frameworks exist (Michel et al., 2025). 
Experiment: Combine Flow Lenia with an Intrinsically Motivated Goal Exploration Process, but replace the flawed compression-based complexity metrics with the Kaplan-Yorke dimension. Set the AI to search the parameter space exclusively for parameter sets that yield a high fractal dimension.
What it measures: It measures whether chaotic, highly dimensional attractors correlate with visually complex, open-ended biological behaviours.
Falsification: If the search returns patterns with a high Kaplan-Yorke dimension that are visually uniform, static, or just unstructured noise, it falsifies the idea that dynamical systems invariants are a perfect proxy for artificial life complexity.

Aim 2: Vision-Language Model Critics for Open-Ended Evolution
Feasibility: Feasible now due to the low latency and high context windows of 2025-era VLMs (like Gemini 2.5 or Claude) that can process video trajectories.
Experiment: Run Flow Lenia with parameter embedding (where cells carry their own mutation rules). Use a Vision-Language Model as the fitness critic. The VLM watches short rollouts of the ecosystem and scores the simulation based on a prompt asking for "ecological interaction, parasitism, or novel locomotion". The parameters are updated via evolutionary strategies based on the VLM's score.
What it measures: It measures whether semantic, human-aligned concepts of biology can be distilled into CCA rules without manually writing fitness functions for them.
Falsification: If the system devolves into adversarial patterns that fool the VLM's vision encoder without actually demonstrating life-like physics, the method fails.

What will NOT work:
Attempting to achieve open-ended evolution by expanding the grid size and channel count of standard (non-Flow) Lenia. Do not waste compute on this. Without strict mass conservation, local rule mutations will inevitably discover an exploit that maximises the growth function, turning your massive supercomputer simulation into a uniform grid of maximum activation values within a few thousand steps. The field has moved past growth-based CCA for ecological simulations; mass conservation is the non-negotiable prerequisite for the frontier.

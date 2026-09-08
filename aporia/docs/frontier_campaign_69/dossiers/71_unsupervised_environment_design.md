# Prompt 71: Unsupervised Environment Design

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdsV3VmYXRXRks5YVJqckVQb04tYzBBMBIXbFd1ZmF0V0ZLOWFSanJFUG9OLWMwQTA
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: Unsupervised Environment Design

**KEY POINTS**
* The user's baseline understanding of the field is historically accurate but slightly outdated for 2026. While curation of random levels via Prioritized Level Replay (PLR) indeed eclipsed early pure-adversary methods like PAIRED, the current frontier has moved beyond pure random curation.
* Evolutionary mutations applied to curated levels (ACCEL) and joint co-design of tasks and levels (ATLAS) now dominate state-of-the-art results.
* The assumption that value-loss accurately proxies regret is actively contested. Major recent breakthroughs demonstrate that value-loss often collapses or stagnates, and frontier methods are replacing it with transition-prediction errors (TRACED) or direct policy parameter change norms (PACE).
* The canonical software framework (Facebook Research's Dual Curriculum Design repository) was permanently archived in August 2025, forcing practitioners to migrate to modern forks or entirely new JAX-based frameworks.

**HOW THIS DOSSIER IS STRUCTURED**
This report directly addresses the requirements of a practitioner looking to build and execute experiments in Unsupervised Environment Design (UED). It begins with a synthesis of the field's current state and active debates. It then outlines the load-bearing literature, the exact state of available software repositories, and the authoritative benchmarks. Finally, it provides a highly specific reproduction recipe, an analysis of methodological failures, and actionable recommendations for novel experimental design in 2026.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Unsupervised Environment Design (UED) is the study of autocurricula: how to automatically generate and curate a sequence of training environments that constantly match a learning agent's capabilities, thereby maximizing the agent's zero-shot transfer to unseen tasks. Your initial understanding is correct for the 2020 to 2022 era. The field was founded on the concept of minimax regret via PAIRED, which deployed a learned adversary to generate levels. It was soon discovered that Dual Curriculum Design (DCD) methods, which use a replay buffer to curate randomly generated levels based on estimated regret (like Prioritized Level Replay, or PLR), empirically outperformed learned adversaries. 

However, in 2026, the field has evolved. Purely random level generation curated by a buffer scales poorly to massive or complex parameter spaces because random sampling almost never stumbles upon highly structured, solvable levels. The field shifted toward evolutionary UED, spearheaded by ACCEL, which takes high-regret levels from the curation buffer and applies small edits (mutations) to them, compounding complexity over time. More recently, the field has fundamentally reconsidered the scoring metrics used to curate levels, moving away from simple value-loss proxies.

WHAT IS SETTLED
It is settled that static Domain Randomization is insufficient for training truly generalist agents in highly structured domains. It is also settled that pure adversarial generation without a curation buffer is unstable and suffers from entropy collapse, usually generating impossible or trivial levels. Buffer-based curation of environments (replaying previously generated levels proportional to their learning potential) is an absolute necessity for stable UED. Furthermore, the necessity of stopping agent policy updates on uncurated, purely random environments (a technique known as PLR-perpendicular) is settled law for achieving theoretical minimax regret bounds and stable empirical performance.

WHAT IS CONTESTED
The central contest in 2026 is how to accurately measure "regret" or "learning potential" without running expensive oracle policies. 
1. The traditional camp uses value-loss (the temporal difference error of the critic) as a proxy for regret. 
2. The dynamics camp (e.g., the authors of TRACED) argues that value-loss is noisy and incomplete, advocating for a combination of value-loss and transition-prediction error (how poorly the agent's world model predicts the next state).
3. The intrinsic camp (e.g., the authors of PACE) argues that all proxy signals (value, regret, Monte Carlo) are flawed because they do not reflect realized learning. They advocate scoring an environment based on the L2 norm of the policy parameter change induced by training on it.
4. The optimisation camp (e.g., the authors of NCC) abandons traditional UED regret for a generalised learnability score formulated as a nonconvex-strongly-concave optimisation problem.

WHAT IS OPEN
The frontier is currently focused on three open problems. First, dealing with "irreducible regret" in stochastic or partially observable environments, where standard minimax regret forces the curriculum to endlessly sample impossible-to-perfect levels while starving the agent of learnable levels. Second, extending UED from fixed tasks to joint task-level co-design, ensuring that an agent receives both a novel environment layout and a logically feasible task specification within it. Third, scaling UED to multi-agent settings, such as unsupervised partner design for ad-hoc teamwork.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES
These papers define the mechanics of the method you are anchoring to.

Dennis, Jaques, Vinitsky, Bayen, Russell, Critch, Levine
2020
Emergent Complexity and Zero-shot Transfer via Unsupervised Environment Design
NeurIPS
arXiv:2012.02096
This paper defines the field of UED and introduces PAIRED, establishing the theoretical framework of minimax regret as a driver for emergent complexity. It is mandatory reading for the mathematical formulation, even if the empirical method is superseded.

Jiang, Grefenstette, Rocktaschel
2021
Prioritized Level Replay
ICML
arXiv:2010.03934
This paper proves that curating randomly generated levels using temporal-difference error as a scoring proxy induces an implicit curriculum that beats standard domain randomization. It introduces the replay buffer mechanic that all modern UED relies upon.

Jiang, Dennis, Parker-Holder, Foerster, Grefenstette, Rocktaschel
2021
Replay-Guided Adversarial Environment Design
NeurIPS
arXiv:2110.02439
This paper unifies PAIRED and PLR into Dual Curriculum Design (DCD). Crucially, it introduces the counterintuitive PLR-perpendicular method: preventing the agent from updating its policy on uncurated random levels, which dramatically stabilizes convergence to Nash equilibria.

Parker-Holder, Jiang, Dennis, Samvelyan, Foerster, Grefenstette, Rocktaschel
2022
Evolving Curricula with Regret-Based Environment Design
ICML
arXiv:2203.01302
This introduces ACCEL, the pivotal evolutionary method that edits previously high-regret levels rather than relying purely on random sampling. It is the baseline against which all 2024 to 2026 methods evaluate themselves.

CURRENT SOURCES
These papers define the 2026 frontier and the active disagreements in the field.

Beukman, Coward, Matthews, Fellows, Jiang, Dennis, Foerster
2024
Refining Minimax Regret for Unsupervised Environment Design
ICML
arXiv:2402.12284
This paper identifies the "regret stagnation" problem where minimax regret fails in environments with irreducible partial observability. It introduces Bayesian Level-Perfect (BLP) regret and the ReMiDi algorithm to force the curriculum to keep advancing. 

Teoh, Li, Varakantham
2024
CENIE: Novelty-driven Autocurricula
NeurIPS
Submission Number 13226
This introduces a domain-agnostic novelty bonus using Gaussian Mixture Models on the agent's state-action space coverage, arguing that pure regret ignores environment novelty.

Monette, Letcher, Beukman, Jackson, Rutherford, Goldie, Foerster
2025
An Optimisation Framework for Unsupervised Environment Design
RLC
arXiv:2505.20659
This reformulates UED from a heuristic game into a rigorous nonconvex-strongly-concave objective, providing the first provable convergence guarantees for UED outside of the strict zero-sum setting.

Cho, Im, Lee, Yi, Kim, Kim
2026
TRACED: Transition-aware Regret Approximation with Co-learnability for Environment Design
ICLR
arXiv:2506.19997
This paper explicitly deconstructs the flaw in using pure value-loss for regret. It introduces transition prediction error and a co-learnability metric to measure cross-task transfer, vastly improving sample efficiency.

Furelos-Blanco, Pert, Kelbel, Spies, Russo, Dennis
2026
Beyond Fixed Tasks: Unsupervised Environment Design for Task-Level Pairs
AAAI
arXiv:2511.12706
This introduces ATLAS, solving the problem of unaligned task and level generation by modeling tasks as reward machines and jointly mutating both tasks and environments to prevent unsolvable combinations.

Yuan, Yin, Shen, Xie, Yang, Qin, Zeng, Li
2026
PACE: Parameter Change for Unsupervised Environment Design
ICML
arXiv:2605.01358
This paper abandons regret entirely in favor of an intrinsic signal: scoring environments by the squared L2 norm of the policy parameter update they induce, achieving state-of-the-art low-variance evaluation without extra rollouts.

PART 3. SOFTWARE I CAN ACTUALLY RUN

DCD (Dual Curriculum Design Framework)
bare URL: https://github.com/facebookresearch/dcd
Language: Python
Licence: UNCONFIRMED
Most recent activity: 2025
Maturity: DORMANT
This was the canonical community standard codebase for running PAIRED, PLR, PLR-perpendicular, and ACCEL. However, the repository was permanently archived by Facebook Research on August 6, 2025, and is now read-only. It provides the exact reference implementations for foundational methods and the heavily used CarRacing and MiniGrid wrappers. Its limitation is that it relies on outdated dependencies (e.g., pyglet 1.5.11, ancient OpenAI baselines), making it increasingly fragile to build on modern toolchains. If you cannot build it, you must use the TRACED reimplementation below.

TRACED
bare URL: https://github.com/Cho-Geonwoo/TRACED
Language: Python
Licence: CC BY-NC 4.0
Most recent activity: 2026
Maturity: MAINTAINED
This is a modern, active fork built directly on top of the DCD codebase. It contains functional implementations of PLR-perpendicular, Domain Randomization, ACCEL, ADD, CENIE, and the authors' own TRACED algorithm. This is currently the most viable software for running BipedalWalker and MiniGrid UED experiments without dependency hell, though you must still manually fix a known numpy deprecation error by replacing "np.bool" with "np.bool_" in the legacy baselines code.

NCC-UED
bare URL: https://github.com/nmonette/NCC-UED
Language: Python
Licence: UNCONFIRMED
Most recent activity: 2025
Maturity: MAINTAINED
This implements the Optimisation Framework for UED. Crucially, it provides a JAX reimplementation of the Crafter environment (Craftax) alongside MiniGrid and XLand-MiniGrid. It uses Docker natively via a provided Makefile, making it highly reproducible. It evaluates policies using alpha-CVaR (testing the policy on its worst alpha percent of levels), which is rapidly becoming the standard evaluation harness over basic zero-shot mean performance. 

ReMiDi
bare URL: https://github.com/Michael-Beukman/ReMiDi
Language: Python
Licence: UNCONFIRMED
Most recent activity: 2024
Maturity: DORMANT
The reference implementation for refining minimax regret to solve regret stagnation. It includes specific custom environments (T-mazes, blindfold mazes, lever games) explicitly designed to induce irreducible regret. It relies on a custom parallel step wrapper to determine trajectory overlaps for its theoretical guarantees. Practitioners use this codebase primarily to benchmark failure modes of standard UED rather than as a general-purpose library.

ATLAS
bare URL: https://github.com/spike-imperial/atlas
Language: Python
Licence: UNCONFIRMED
Most recent activity: 2026
Maturity: MAINTAINED
The reference implementation for co-designing task-level pairs. It heavily relies on Graph Convolutional Networks (GCNs) to encode Reward Machines representing tasks. It contains unique mutation operators for task-graphs (hindsight edits, state additions) that do not exist in any other UED codebase. The setup requires Conda and specifically JAX with CUDA 12 support.

PART 4. DATA AND BENCHMARKS

Procedurally Generated MiniGrid Mazes
Access route: Accessible via the DCD, TRACED, and ATLAS repositories.
Approximate size: Infinite procedural generation, but evaluated on fixed sets of held-out human-designed configurations (e.g., PerfectMaze, PerfectMazeLarge, PerfectMazeXL).
Licence: Apache 2.0 (underlying Minigrid).
Measurement: This is the authoritative, load-bearing benchmark of the field. It tests 2D partially observable navigation. Generalization is measured by zero-shot success rates on the held-out PerfectMaze configurations.
Known issues: The basic layouts are nearing saturation for modern methods, which is why ATLAS and TRACED have moved to evaluating on XL versions or combining the mazes with complex formal logic tasks (Reward Machines).

Adversarial BipedalWalker
Access route: https://github.com/Cho-Geonwoo/TRACED (inherited from original ACCEL paper).
Approximate size: Procedurally generated terrain (stump height, pit gap width, staircase dimensions).
Licence: MIT (underlying Box2D environment).
Measurement: Measures continuous control locomotion transfer. Evaluated on specific held-out challenging terrains. 
Known issues: Performance heavily depends on the specific mutation parameters (the "editor" bounds) allowed during generation. If bounds are too wide, the walker encounters physically impossible gaps too early, stalling learning. 

Craftax
Access route: https://github.com/nmonette/NCC-UED
Approximate size: Infinite procedural generation of crafter worlds.
Licence: MIT.
Measurement: Measures long-horizon, open-ended survival and crafting mechanics. Evaluated using alpha-CVaR to measure worst-case robustness.
Known issues: Highly complex state space makes standard value-loss proxy exceptionally noisy, causing traditional PAIRED or PLR to struggle significantly compared to direct parameter-change methods (PACE) or generalised learnability (NCC).

PART 5. THE REPRODUCTION RECIPE

The most informative and reproducible baseline experiment to run in 2026 is training ACCEL on Adversarial BipedalWalker, serving as a calibration check against the reported state-of-the-art results in TRACED and PACE.

Software and Version:
Clone the TRACED repository (https://github.com/Cho-Geonwoo/TRACED). Ensure you are using Python 3.8 and pyglet 1.5.11. You must manually execute the numpy deprecation fix in the OpenAI baselines submodule (replace np.bool with np.bool_).

Dataset/Generator:
The BipedalWalker-Adversarial-Easy-v0 environment.

Exact Parameters:
Command line execution via train.py. The required flags to exactly replicate the baseline are:
xpid: ued-BipedalWalker-Adversarial-Easy-v0
env_name: BipedalWalker-Adversarial-Easy-v0
use_gae: True
gamma: 0.99
gae_lambda: 0.9
recurrent_arch: lstm
recurrent_agent: False
recurrent_adversary_env: False
recurrent_hidden_size: 1
use_global_critic: False
lr: 0.0003
noexpgrad: True (disables exponentiated gradient)
epoch: 5
mb: 32 (minibatch size)
v: 0.5 (value loss coefficient)
gc: 0.5 (gradient clipping)
henv: 0.01 (entropy coefficient for environment)
ha: 0.001 (entropy coefficient for agent)
plr: 0.9 (Prioritized Level Replay fraction)
rho: 0.5 (staleness weight)
n: 1000 (buffer size)
st: 0.5 (temperature)
positive_value_loss: True
rank: True
t: 0.1 (mutation rate)
editor: 1.0 (mutation magnitude)
random: True
n3: True
baseeasy: True
tl: 0

Replicates and Seeding:
Execute a minimum of 5 independent replicates (e.g., seeds 4361, 4362, 4363, 4364, 4365).

Approximate Compute Cost:
Between 12 and 18 wall-clock hours per seed on a modern GPU (e.g., RTX 3090 or A100), totaling roughly 60 to 90 GPU hours for a statistically significant sample.

Expected Result:
The zero-shot transfer performance on held-out hard BipedalWalker terrains should converge to a mean solved score comparable to the ACCEL baselines reported in the TRACED paper (cite: arXiv:2506.19997). Specifically, you should see complexity compound visibly: terrains will start flat and progressively feature larger gaps and rougher surfaces as training progresses.

The Three Most Common Reproduction Failures:
1. Environment Horizon Cutoffs: Failing to strictly separate environment termination from timeout truncation in the replay buffer. If timeouts are treated as standard deaths, the regret metric collapses because the agent's value network learns an incorrect baseline.
2. Incomplete PLR-Perpendicular implementation: Accidentally allowing the agent to run gradient updates on the purely random (uncurated) exploration levels. Theory dictates the agent must only train on curated replay levels to maintain the regret bound.
3. Legacy Dependency Breakage: Using modern PyTorch or NumPy against the ancient OpenAI baselines submodule included in DCD/TRACED. This silently corrupts boolean masks or causes shape-broadcasting errors during Generalized Advantage Estimation (GAE) calculations.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to push the frontier in 2026, you will hit a massive infrastructure wall. The entire field is bottlenecked by the requirement that environments must be "underspecified POMDPs" where parameters can be dynamically overridden at episode reset. 

What must be built is a hardware-accelerated, differentiable UED harness for rigid-body physics.
Currently, environments like MiniGrid and BipedalWalker are CPU-bound in Python. Even Craftax is specific to 2D grid logic. If you want to apply PACE or TRACED to 3D robotics (e.g., quadruped locomotion over procedural rubble), you cannot use off-the-shelf MuJoCo or Isaac Gym natively because their APIs do not cleanly support per-environment, step-by-step adversarial parameter mutation fed directly back into a batched PPO buffer without severe GPU-to-CPU transfer bottlenecks.

The Interface Needed:
Input: A batched tensor of environment configurations (friction, mass, joint limits, terrain heightmaps).
Output: A fully unrolled batch of trajectories on the GPU, returning the standard RL tuple plus the exact temporal-difference errors and transition-prediction losses per level, without ever leaving VRAM.
The Hard Part: Managing the replay buffer logic (PLR) purely in JAX or CUDA. The buffer must maintain staleness scores, sort by estimated regret, and apply evolutionary mutations to heightmaps purely via tensor operations. 
Effort: This is a major engineering undertaking, roughly 3 to 6 months for a competent computational scientist. Multiple groups have attempted private, brittle wrappers around Isaac Gym to achieve this, proving the demand exists, but no generalized open-source library provides this cleanly for UED.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of UED is largely a history of realizing that pure game-theoretic formulations break down when applied to deep neural networks.

The Failure of Pure Adversarial Generation
Early UED assumed that a reinforcement learning adversary (the Teacher) optimizing for regret could endlessly generate novel levels from scratch (PAIRED). This empirically failed to scale. In practice, the adversary's policy entropy collapses. Because the design space is so large and the gradient signal from the student's performance is so delayed, the adversary finds a small pocket of high-regret levels and gets stuck there, while the rest of the environment space remains unexplored. The standing critique was that domain randomization often beat PAIRED. This critique was definitively answered by the introduction of Dual Curriculum Design and PLR, which proved that curating randomly generated levels circumvents the adversary's entropy collapse.

The Regret Stagnation Artefact
A major standing critique leveled against all minimax regret methods (PAIRED, PLR, ACCEL) is that they completely fail in environments with irreducible regret. In settings where no policy can ever be perfect (e.g., a T-maze where the goal is randomly placed and invisible until reached), the "optimal" policy still incurs a high loss. The regret proxy spikes. The UED buffer becomes entirely saturated with these impossible-to-perfect levels. The agent trains on them endlessly, learning nothing new, while entirely ignoring solvable levels that have lower regret. This critique was raised and confirmed by Beukman et al. (ReMiDi), who demonstrated that the UED baseline learning flatlines entirely in these setups. Their answer—Bayesian Level-Perfect regret—partially addresses this by forcing the curriculum to step down to lower regret tiers once the top tier stagnates.

The Proxy Metric Collapse
The most severe ongoing critique in 2026 is that the proxy metrics the field relies on are fundamentally misaligned with actual learning. Regret is uncomputable in real-time. The field substitutes it with the Positive Value Loss (the temporal difference error). However, papers like TRACED and PACE have shown that high value loss often just means the Critic network is currently inaccurate, not that the Actor network can actually improve its policy on that level. Furthermore, in environments with sparse rewards, the value loss is uniformly zero for all unsolved levels, providing absolutely no signal for the curriculum to follow. TRACED answered this by adding transition prediction errors. PACE answered this by abandoning value loss entirely and measuring the mathematical norm of the actual policy parameter updates. However, PACE's approach is critiqued as being completely unscalable to Large Language Model-sized policies, because computing the L2 norm of billions of parameters per environment step is computationally ruinous. This critique currently stands unanswered.

Task-Level Misalignment
Methods that scaled environments (changing the layout) completely ignored task scaling (changing the objective). When groups attempted to randomly sample tasks and environments simultaneously, it was a spectacular failure. The majority of generated pairs were unsolvable (e.g., "unlock a blue door" in a level with no blue door). The UED machinery choked because the regret on impossible pairs is zero. This forced the development of ATLAS, answering the critique by co-evolving tasks and levels simultaneously using formal structural mutations.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the current frontier, a well-resourced computational scientist should bypass 2D mazes entirely and target the unaddressed intersections of UED.

1. High-Priority Experiment: Parameter Change UED on Continuous Control 3D Robotics
Feasibility: JAX-based physics (Brax, MJX) now allows extremely fast batched simulations.
Measurement: Implement the PACE algorithm (which scores environments via the L2 norm of the policy update) on a Brax quadruped environment where terrain parameters are the UED levels. Measure zero-shot transfer to held-out rugged terrain against an ACCEL baseline.
Falsification: If the L2 norm of the parameter change becomes statistically indistinguishable from noise due to the continuous action space variance, PACE's core hypothesis is falsified for continuous control.

2. Medium-Priority Experiment: Joint Co-Learnability of Tasks and Morphologies
Feasibility: ATLAS established how to co-evolve tasks and grid layouts. TRACED established how to measure co-learnability (how training on environment A improves performance on environment B).
Measurement: Combine these mechanisms. Apply UED to an agent whose physical morphology (limb lengths, sensor placements) is the "environment" and the locomotion target is the "task". Measure the co-learnability matrix to prove whether certain body-shapes act as necessary stepping-stones for complex tasks.
Falsification: If the co-learnability metric flatlines, it proves that morphological adaptation is too discrete to form a smooth UED curriculum.

3. Low-Priority (Do Not Attempt): Scaling Pure Neural Adversaries
What will NOT work: Attempting to solve the PAIRED entropy collapse by simply throwing more compute, larger transformers, or PPO tuning at the neural adversary. The reward landscape for the adversary (the student's dynamic regret) is inherently non-stationary and hopelessly noisy. Without a curation buffer to act as a memory and selection pressure, or an evolutionary operator to maintain structural validity, the adversary will always degenerate. Compute does not fix the fundamental game-theoretic instability of the two-player UED formulation.

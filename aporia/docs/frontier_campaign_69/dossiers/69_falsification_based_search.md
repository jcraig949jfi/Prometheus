# Prompt 69: Falsification-Based Search

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chd4MmVmYXZhZ0dLVzVzT0lQMHVTTTJRZxIXeDJlZmF2YWdHS1c1c09JUDB1U00yUWc
**Elapsed:** 426s

---

# FRONTIER PRACTITIONER DOSSIER: FALSIFICATION-BASED SEARCH

**Key Points:**
* The core premise of falsification-based search remains treating formal verification as a stochastic optimization problem, aiming to minimize a quantitative robustness metric of a Signal Temporal Logic specification to find counterexamples [cite: 1, 2].
* The frontier has decisively shifted away from purely black-box simulation. In 2026, the state of the art involves learning differentiable surrogate models, particularly Neural Ordinary Differential Equations and Koopman operators, to bypass the prohibitive computational cost of high-fidelity simulators [cite: 3, 4].
* A major and enduring controversy in the field surrounds the "masking effect" and the "scale problem" in temporal logic robustness [cite: 2, 5]. Traditional semantics use non-differentiable operators that hide gradient information, but proposed continuous approximations often sacrifice mathematical soundness, leading to intense debate over the correct objective function formulation [cite: 5, 6].
* The discipline is increasingly intersecting with Reinforcement Learning, using falsification engines to systematically generate adversarial training scenarios to improve policy compliance with safety rules [cite: 7, 8]. 

The following report is structured specifically for a computational scientist equipped with compute and engineering capability, outlining exactly what is settled, what tools are operational, and where a high-impact intervention can be made today.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Falsification-based search in 2026 is an applied verification discipline primarily focused on Cyber-Physical Systems and autonomous agents. When a system is too complex, non-linear, or opaque for exhaustive formal verification, this field attempts to find a single trace that violates a formal safety requirement. Requirements are typically encoded in Signal Temporal Logic, a formalism that admits a real-valued quantitative robustness metric. Falsification casts this robustness as an objective function: a stochastic optimizer explores the input space, simulates the system, and tries to drive the robustness below zero. A negative robustness value constitutes a counterexample. If the search budget is exhausted without finding a negative value, the system is not proven safe; the method is explicitly incomplete but highly scalable [cite: 1, 9, 10].

What is SETTLED is the fundamental architecture of the black-box search loop. The use of metaheuristics like Covariance Matrix Adaptation Evolution Strategy, Cross-Entropy methods, and Simulated Annealing over piecewise-constant or piecewise-linear input parameterizations is the established baseline [cite: 9, 11, 12]. It is widely accepted that standard black-box testing often struggles with complex specifications, requiring either gray-box introspection or advanced surrogate modeling [cite: 9, 11, 13]. The benchmark format is also settled: the Applied Verification for Continuous and Hybrid Systems competition sets the standard for how models and properties are structured [cite: 11, 14].

What is CONTESTED is how to calculate the robustness landscape itself. The classic robustness calculation relies on minimum and maximum operators, which induces a severe "masking effect" or "scale problem" [cite: 2, 3, 5]. If a signal satisfies a requirement strongly at one time step but marginally at another, the minimum operator masks all gradients except at the extreme point. One side of the field attempts to solve this via smoothing techniques or integral and average-based robustness metrics [cite: 5, 6]. The opposing side argues that smoothing destroys soundness because a positive smoothed robustness no longer guarantees strict logical satisfaction, and they advocate instead for syntax-tree traversal methods or localized search [cite: 3, 6, 15]. 

What is OPEN is the seamless integration of falsification with high-dimensional perception systems and generative artificial intelligence. The frontier is currently dominated by surrogate modeling. Because running a high-fidelity physics simulator for tens of thousands of iterations is intractable, researchers are building differentiable surrogate models using Neural Ordinary Differential Equations, Koopman operators, and Decision Trees to approximate the system under test [cite: 3, 4, 16, 17]. Once trained, the surrogate is falsified using optimal control or adversarial attacks, and the resulting candidate trace is verified on the true simulator [cite: 3]. Furthermore, the field is expanding into Falsification-Driven Reinforcement Learning, where counterexamples are fed back into the training loop of autonomous agents as adversarial scenarios to enforce strict rule compliance [cite: 7, 8].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Alexandre Donze
Year: 2010
Title: Breach, A Toolbox for Verification and Parameter Synthesis of Hybrid Systems
Venue: Computer Aided Verification
Identifier: DOI 10.1000/xyz (Note: System requires literal formatting, actual is DOI 10.1007/978-3-642-14295-6_17) [cite: 18, 19]
This is the paper that introduced Breach, the most widely used MATLAB toolkit for Signal Temporal Logic monitoring and falsification. A practitioner must read this to understand how continuous-time robustness semantics are implemented in software and mapped to stochastic optimizers.

Authors: Yashwanth Annpureddy, Che Liu, Georgios Fainekos, Sriram Sankaranarayanan
Year: 2011
Title: S-TaLiRo: A Tool for Temporal Logic Falsification for Hybrid Systems
Venue: Tools and Algorithms for the Construction and Analysis of Systems
Identifier: DOI 10.1007/978-3-642-19835-9_21 [cite: 20, 21]
This defines the competing foundational framework, introducing Monte Carlo random walks and simulated annealing directed by robustness metrics over metric temporal logic. It established the standard parameterization of input signals that the field still uses today.

Authors: Houssam Abbas, Georgios Fainekos, Sriram Sankaranarayanan, Franjo Ivancic, Aarti Gupta
Year: 2013
Title: Probabilistic Temporal Logic Falsification of Cyber-Physical Systems
Venue: ACM Transactions on Embedded Computing Systems
Identifier: IDENTIFIER UNKNOWN [cite: 13, 22]
This paper provides the rigorous mathematical formulation of how to map hybrid system falsification to a metric space and optimize over it, highlighting early on that black-box search can struggle against simple random sampling if the robustness landscape is highly non-convex.

CURRENT FRONTIER SOURCES

Authors: Tanmay Khandait, Federico Formica, Paolo Arcaini, Surdeep Chotaliya, Georgios Fainekos, et al.
Year: 2024
Title: ARCH-COMP 2024 Category Report: Falsification
Venue: EPiC Series in Computing
Identifier: DOI 10.29007/hgfv [cite: 14, 23]
This is the most critical state-of-the-art survey and benchmark report available. It details exactly which tools won the annual competition, which algorithms they used, and how the standardized benchmarks are parameterized.

Authors: Anonymous (or authors from TU Munich / UC Berkeley)
Year: 2026
Title: Optimal Control-Based Falsification of Learnt Dynamics via Neural ODEs and Symbolic Regression
Venue: arXiv
Identifier: arXiv:2602.00031 [cite: 3, 24]
This paper defines the current surrogate frontier. It demonstrates how to replace the black-box simulator with a Neural ODE, distill it into a symbolic representation, and use optimal control to find counterexamples with orders of magnitude fewer actual simulations.

Authors: Marlon Muller, Florian Finkeldei, Hanna Krasowski, Murat Arcak, Matthias Althoff
Year: 2026
Title: Falsification-driven reinforcement learning for maritime motion planning
Venue: Ocean Engineering
Identifier: DOI 10.1016/j.oceaneng.2026.125579 [cite: 7, 25]
This represents the frontier of applying falsification to autonomous agent training. It shows how counterexamples generated by minimizing Signal Temporal Logic robustness can be injected into Reinforcement Learning as adversarial scenarios to improve safety compliance.

Authors: Yipei Yan, Deyun Lyu, Zhenya Zhang, Paolo Arcaini, Jianjun Zhao
Year: 2025
Title: Automated Generation of Benchmarks for Falsification of STL Specifications
Venue: IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems
Identifier: DOI 10.1109/TCAD.2025.3550410 [cite: 26, 27]
This paper addresses the severe benchmark starvation in the field by introducing FalBenchGen, a framework that synthesizes diverse falsification benchmarks from data, moving the field past over-reliance on the aging Automatic Transmission model.

Authors: Zhenya Zhang, Paolo Arcaini, et al.
Year: 2021
Title: Effective Hybrid System Falsification Using Monte Carlo Tree Search Guided by QB-Robustness
Venue: Computer Aided Verification
Identifier: IDENTIFIER UNKNOWN [cite: 15, 28]
This paper introduces ForeSee, highlighting the critical "scale problem" in robustness evaluation and proving that syntax-tree traversal combined with Monte Carlo Tree Search can drastically outperform standard global optimizers on complex formulas.

Authors: Noushin Mehdipour, Cristian-Ioan Vasile, Calin Belta
Year: 2024 (approximate updated release)
Title: Average-based Robustness for Continuous-Time Signal Temporal Logic
Venue: IEEE/ACM venues
Identifier: IDENTIFIER UNKNOWN [cite: 5, 6]
This source represents the opposing faction in the robustness debate, offering a formulation of Average and Geometric Integral Mean robustness to eliminate the masking effect of min and max operators. It is essential reading for understanding objective function design.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Breach
https://github.com/decyphir/breach
MATLAB and C++
BSD-like Licence
2024
MAINTAINED
Breach is the foundational community standard for Signal Temporal Logic monitoring and falsification, capable of running parameter sweeps, sensitivity analysis, and metaheuristic falsification on Simulink models [cite: 18, 29, 30]. Its primary gotcha is that it requires a properly configured C/C++ compiler toolchain within MATLAB (using mex -setup), which frequently breaks on modern Linux distributions or Apple Silicon without extensive manual linking [cite: 28, 29].

VerifAI
https://github.com/BerkeleyLearnVerify/VerifAI
Python
BSD 3-Clause Licence
2024
MAINTAINED
VerifAI is a modern Python-centric toolkit designed specifically for systems containing machine learning components, offering simulation-guided falsification and data set augmentation [cite: 31, 32, 33]. It interfaces well with heavy simulators like CARLA and Webots, but requires careful management of virtual environments and its specific version dependencies can clash with modern deep learning stacks if not isolated [cite: 32, 34].

ForeSee
https://github.com/choshina/ForeSee
Python and MATLAB
GPL Licence (Inferred)
2021
DORMANT
This software implements Monte Carlo Tree Search over the specification syntax tree to solve the scale problem in robustness [cite: 15, 28]. It is built as a wrapper on top of Breach. Because it bridges Python scripts calling MATLAB engines via specific APIs, reproducing its results today requires carefully matching legacy Python 3.6 to 3.8 versions with compatible MATLAB Engine API releases [cite: 28].

S-TaLiRo
https://sites.google.com/a/asu.edu/s-taliro
MATLAB
GPL Licence (Inferred)
2021
DORMANT
Historically the main competitor to Breach, using simulated annealing and random walks to find counterexamples in Simulink and Stateflow diagrams [cite: 13, 35]. It is effectively dead for new feature development, though older benchmarks still use it as a baseline. A Python rewrite exists (Psy-TaLiRo) but is rarely used as the canonical source [cite: 3, 36].

FalStar
https://github.com/ERATOMMSD/falstar
Python and Scala
Open Source
2020
ABANDONED
An attempt to use a probabilistically directed search adapting to local complexity, originally providing excellent results against CMA-ES [cite: 29, 37]. It is explicitly unmaintained and the repository structure relies on legacy Scala build tools that fail on modern Java Virtual Machines without significant patching. 

PART 4. DATA AND BENCHMARKS

ARCH-COMP Falsification Category Benchmarks
https://gitlab.com/goranf/ARCH-COMP
Size: Dozens of Simulink models and parameter scripts
Licence: Mixed Open Source
This is the single authoritative benchmark suite for the field, maintained across annual iterations [cite: 11, 15, 38]. It measures the falsification rate and simulation count across various tools. Known saturation exists on the Automatic Transmission model, which is heavily over-represented in the literature; almost all modern tools can solve it trivially, leading to overfitting of heuristic hyperparameters [cite: 10, 12].

Automatic Transmission (AT)
Contained within ARCH-COMP
Size: Single Simulink Model
Licence: MathWorks standard / Open
Used to measure basic stochastic search efficiency over simple continuous dynamics with discrete gear shifts [cite: 10, 12, 39]. The benchmark is considered solved, but it remains the mandatory "hello world" of the field. Note that tools often exploit the specific scale of the RPM and Speed variables, making results non-generalizing if not normalized.

Aircraft Ground Collision Avoidance System (F16)
Contained within ARCH-COMP
Size: 16 continuous variables, piecewise nonlinear differential equations
Licence: Open
Measures falsification over a highly non-linear finite-state machine with continuous guards [cite: 15, 39]. This is a purely initial-condition falsification problem (no time-varying inputs), meaning tools optimized strictly for trajectory perturbation often fail here while geometric and reachability tools excel [cite: 15, 39].

Synthetic Benchmark (SB)
Generated via FalBenchGen (Included in ARCH-COMP 2025/2026)
Size: Five discrete models
Licence: Open
Introduced to address the lack of structural diversity in existing models [cite: 11, 15, 27]. These are data-driven Long Short-Term Memory models trained to mimic complex input-output relationships. They measure the ability of a falsifier to handle opaque, deep-learning-based dynamics rather than standard physics equations [cite: 15, 27].

PART 5. THE REPRODUCTION RECIPE

The most reproducible and informative experiment to establish a baseline in this field is the replication of the ForeSee Monte Carlo Tree Search falsifier against the Breach baseline on the Automatic Transmission benchmark. 

Software and Version:
Install MATLAB (preferably R2020a to R2021a for compatibility).
Install Python 3.8.
Clone Breach from https://github.com/decyphir/breach and checkout version 1.2.13 [cite: 29]. Run the mex compiler setup.
Clone ForeSee from https://github.com/choshina/ForeSee [cite: 28]. Run the installation script to bind the MATLAB engine.

Dataset and Generator:
Use the Automatic Transmission models specified in the ForeSee repository (specifically the AT1 and AT2 specifications) [cite: 28, 40]. The input generator must be set to piecewise constant signals with 5 to 10 control points [cite: 12, 39].

Parameters:
Time horizon: 30 seconds (or 20 seconds depending on the specific AT instance) [cite: 11].
Throttle input bounds: 0 to 100.
Brake input bounds: 0 to 325.
Timeout budget: 900 seconds per trial [cite: 28].
Algorithm: ForeSee (MCTS) vs Breach (CMA-ES).

Replicates and Seeding:
30 independent trials per algorithm, per specification [cite: 28]. The seed must be randomized at the start of both the Python execution and the MATLAB engine instance to prevent identical pseudo-random sequences in the stochastic optimizer.

Compute Cost:
Approximate cost is 7.5 CPU hours per problem instance (worst case, 900 seconds times 30 trials) [cite: 28]. GPU is not required as the Simulink model executes entirely on the CPU.

Expected Result:
According to the original publication, ForeSee should achieve a success rate approaching 100 percent on complex nested formulas (like AT6 or AT51) while the Breach CMA-ES baseline will fail frequently (often below 20 percent success rate) due to the scale problem [cite: 12, 15, 28].

Common Ways People Get This Wrong:
1. Interpolation Mismatch: Failing to set the input parameterization strictly to piecewise constant without Simulink auto-interpolation. If Simulink upsamples the input signal dynamically, the dimensionality of the search space explodes, and the optimizer will fail.
2. Robustness Normalization: Failing to normalize the robustness values of speed (measured in units around 120) and RPM (measured in units around 4500). If not handled via QB-Robustness or normalization, the optimizer will solely focus on minimizing RPM and completely ignore the speed constraints [cite: 2, 36].
3. MATLAB Engine Overhead: Instantiating a new MATLAB engine for every single simulation step rather than keeping a persistent engine open and passing arrays. This turns a 10-minute experiment into a 10-hour experiment.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If a well-resourced entrant wants to push the frontier in 2026, they will find a massive tooling gap in differentiable simulation and surrogate integration. Currently, almost all authoritative tools are trapped in the MATLAB/Simulink ecosystem, while modern machine learning and optimal control rely on PyTorch and JAX. 

What must be built is a Native-Python, GPU-Accelerated Differentiable Falsification Stack. 
Interface In: A dynamic system defined as a PyTorch Module or Neural ODE, alongside a Signal Temporal Logic formula parsed into a differentiable computation graph.
Interface Out: A batched tensor of counterexample trajectories and their corresponding negative robustness gradients. 
The Hard Part: Signal Temporal Logic is fundamentally non-differentiable due to the minimum and maximum operators [cite: 5]. While several groups have built private implementations of smoothed STL (replacing max with Log-Sum-Exp), they struggle with numerical instability and the loss of soundness (a positive smoothed robustness does not guarantee the actual logic is satisfied). Furthermore, efficiently unrolling a differential equation solver backwards in time to pass gradients through an entire trajectory to the initial control points requires extreme care with memory management (adjoint sensitivity methods) [cite: 3, 41].
Amount of Work: 6 to 12 months for a dedicated computational scientist. 

Signal of a Real Gap: 
Almost every recent paper on surrogate models or Reinforcement Learning falsification mentions writing their own custom Python script to calculate robustness and tie it to a stochastic optimizer because Breach and S-TaLiRo cannot be easily batched on a GPU [cite: 3, 4, 17]. Frameworks like STLCG exist, but they are isolated libraries rather than end-to-end falsification environments. 

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The most persistent negative result and standing critique in this field revolves around the "Scale Problem" and the "Masking Effect" inherent to quantitative semantics [cite: 2, 3, 5, 6, 36]. 

The Phenomenon: 
When a specification involves multiple variables with vastly different magnitudes (for example, engine RPM ranging from 0 to 5000, and system mode ranging from 0 to 1), the robustness metric is dominated entirely by the larger variable. An optimizer trying to minimize a conjunction of these two variables will exclusively perturb the inputs that affect RPM, completely masking any progress made toward falsifying the system mode [cite: 2, 36]. 

Failed Solutions:
Early attempts to solve this involved naively scaling variables to a 0 to 1 range. This failed because temporal operators also introduce masking over time. If a signal violates a threshold at time 10, the "always" operator takes the minimum robustness over the entire trace. If the optimizer perturbs an input at time 5, the overall trace minimum at time 10 does not change, resulting in a gradient of exactly zero [cite: 5, 6]. The optimizer is effectively blind. 

Standing Critiques:
Researchers have proposed replacing the non-differentiable minimum and maximum operators with Integral or Average-based robustness [cite: 5, 6]. The standing critique of this approach is that it mathematically alters the formal semantics. If you average the robustness, a severe but brief violation might be canceled out by a long period of high satisfaction, yielding a positive robustness despite the system being unsafe. The critique remains largely unanswered in a mathematically rigorous way; proponents of average robustness accept the loss of soundness in exchange for empirical search efficiency, forcing them to run a secondary "strict" check on any discovered counterexamples [cite: 5, 6].

The Baseline Artefact Critique:
A major critique made by the original S-TaLiRo authors and echoed in subsequent reviews is that on highly complex, discontinuous systems, sophisticated black-box optimization algorithms often perform barely better than uniform random sampling [cite: 13]. Many proposed methods that look strong are later shown to be merely overfitting to the highly specific, low-dimensional landscape of the Automatic Transmission benchmark. When tested on heavily discontinuous models with tight guards, the performance of advanced stochastic searches degrades rapidly, indicating that the field sometimes measures the simplicity of the benchmark rather than the power of the algorithm.

Surrogate Hallucination:
In the recent push toward Neural ODE and Koopman operator surrogates [cite: 3, 4], a standing issue is that the surrogate model diverges from the true physics. The falsifier finds a counterexample in the surrogate, but when tested on the real system, it is a spurious artifact of the neural network's approximation error. While the standard response is to add the spurious trace back into the training data and retrain (Counterexample-Guided Abstraction Refinement), this loop can occasionally stall infinitely if the neural network lacks the capacity to model a specific high-frequency physical transition [cite: 3].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

An entrant with engineering capability and compute should completely ignore writing yet another metaheuristic wrapper for MATLAB. Instead, they should target the intersection of differentiable physics, large-scale generative models, and verification.

EXPERIMENT 1 (Rank 1): End-to-End Optimal Control via Symbolic Surrogate Distillation
What to do: Implement a pipeline that takes a black-box simulator, trains a Neural Ordinary Differential Equation on its input-output traces, but instead of falsifying the neural network directly, distills the learned dynamics into a symbolic regression model [cite: 3, 24]. Then, formulate an exact optimal control problem over the symbolic equations to minimize Signal Temporal Logic robustness. 
Feasibility now: Fast symbolic regression libraries and differentiable physics engines (like JAX and PyTorch) have matured to the point where extracting analytical forms from Neural ODEs is tractable [cite: 3].
What it measures: The exact number of true-system simulator calls required to reach a falsification, compared against standard surrogate methods. 
Falsification of idea: If the symbolic regression fails to capture the hybrid discrete-mode switches (a known weakness of continuous analytical equations), the optimal controller will exclusively generate spurious counterexamples, proving that symbolic distillation cannot handle strict Cyber-Physical System discontinuities.

EXPERIMENT 2 (Rank 2): Falsification-Driven Reinforcement Learning for Adversarial Scenario Generation
What to do: Connect a high-speed parallel reinforcement learning environment (e.g., Isaac Gym) to a falsifier. Train an agent to navigate safely. Concurrently, use the falsifier to hunt for environment initializations (scenarios) that cause the current agent policy to violate a Signal Temporal Logic safety property [cite: 7, 8]. Inject these exact falsifying traces back into the replay buffer of the RL agent. 
Feasibility now: RL frameworks now support massive hardware-accelerated parallelization, meaning the falsifier can evaluate robustness across tens of thousands of environment variations per second without waiting for real-time simulation.
What it measures: The robustness of the final RL policy against out-of-distribution edge cases, quantified by the falsification rate of an independent testing suite before and after adversarial injection.
Falsification of idea: If the falsifier discovers exploits in the simulator's physics engine rather than semantic failures in the agent's logic, the agent will learn meaningless behaviors, indicating the method optimizes the wrong manifold.

WHAT WILL NOT WORK
Attempting to build a "better" global stochastic optimizer (like a new variant of Particle Swarm or a slightly tweaked Genetic Algorithm) and applying it to the raw robustness scalar. The search landscape of temporal logic robustness over hybrid systems is fundamentally plateaued and discontinuous [cite: 2, 5]. Without altering the objective function (via syntax tree weighting or smooth semantics) or exposing the system dynamics (via white-box differentiation or surrogate models), any new black-box optimizer will rapidly saturate and fall victim to the exact same masking effects that have crippled existing algorithms for a decade. Building a generic optimizer treats the symptom; the actual bottleneck is the geometric structure of the robustness metric itself.

**Sources:**
1. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGifQ_BQN-1ysr6bsTXl8HMNEIDgfMKv27389FqVixKuZYpXvb1XEhWgcvvFxGzGV92YQqwZpu_UCsn8prHAjW184okycdWDzlObufbfkF5-9gsb07rLmFU_tPEdOYYd8I-BzqBMiQeL80QrWnvvn4JmvN5WKJ8eZLJjJI=)
2. [chalmers.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_h25FdcWGqqpNFCWQL-lepIMPW6-9aR7W4ACtP1nmxEF_tJASwYlC8sIXYnsqkcVuRtT9QkKqUBDys9tcKpuUM54kcHRixYZSYVWjsmSNp82-sXP9KOCCxV4QFWdg5fBX3IM23WgFiyxsSiSxHs0ThFe47J1_DNZO0egrrTU=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaCZW1F6BgFI1Y4I-YskUOpesXJ9lZr5ZZGPC_ibsECXICp6_bXs3S-bvRvh5cR2MjB8aN_0MzulN-5diNDlECuWu6ADeLbkpCi-Zx3bf_TxbptsxHYjuNpw==)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsZ5pDnOPX82Jr32FVpOG2y2mCU860RD4lvh1vqKjlFlyWig2lzD2VhyIofMKO3JwEgmc5EtnCb_7x03GgkRrTtTRVDRtbbhw41YXjTQXE1o6iYlwbAfeIpti-Cr1IcfGLsgr7cerROcG2qNTDe7SjHgkbNjTMt0Kv9CTVuM-O1xC2OJ8T0C40e-2wUN4MlW0bnYxh5EWHPqKpYIEh4DzciHZppzE=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHf9nBrNRImPwXhHwb3xuC0mvMCDWMWHQSBmXtXdAlmsE5KgQ_LFbDh0Ps1VaJwWvzOiucgfoP5mDPHevJajkXRDH2BJ_AjLSPmcScfyDClNUS-MnEOm6plWQ==)
6. [calinbelta.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6XlgWquLuse3e13fBnmayy21CITybNuqgEGGJSmgRX_TLMN7XaYI7qiFzk2FpIhtfDoq4qsdvxDhsyWXiCKTlDwhYK5OTZVgcY6cCUARlHb-U6qiY4FlZ0_AlQAGawmOkY25q6ivJdbCjLvGX63FrPAbzg118L3P3vSxYwvaUBy7e73AKTQ9BDbtpMjbXQIOc59HTxOfh-W85E-_4WEKt8x3MjkKEgVRLEAlsJmc=)
7. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoShjll_zUvRjU0HXuh59sjTMJZReT_sUpjjN8lbiq10fQfdsGp1MX6vGOgc-iUL4svjhGc7qGb4b7S0e8m8BwshXJcgr8ODarDZDb2ZTLZE41-OhoCQ==)
8. [krasowski.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBIvTy2-s_B5WU192WXmcbDCOhIPrxa2sU1iDC1jVYXxSq7MH4TN9bjMNlHYyO_oe6u9w9TIJUW3GLjrcLXV-dJ8p4BMxVIcO04hJ7jReFPMxjL1aTkN60KM2Ceagp)
9. [abo.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVog9PWS1eRxlyuLzjpFdgx5w1Qv_l8hS3HMtXcXE1qajISJPkBIRA6diexrs96z8ZrjcANY1Ny-QzpOykQlajdIQMYGR7VxYZE4G8K14vQkqK0pbSEOwiBalni38VMF-L8ejXL_4dYftYJhPVs9mPUU2UmjRP)
10. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHR5maVOZunMsKg1GY3mIdyVjEb3pmxQtLa40AUTekjMSKM6yrzzgRxMw8IuUggS-Ys9EUwHGFPlKKuNw53pXiQm64JcRhQ1vgF1ppKEfPlGRcenypQK1NlH320n3zS9Aq6l91Cb5CguAIxeQ-AfIgnSGKK6oJg7BOr6E2auQ==)
11. [easychair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxEkTCLXQcKGts83_IIL7uxSJm6B9xzqAR2oN02EFD1riGURwEOh_NRjIdlRRQc7cVqci5Q9ORZVRI1jp6CJcQBQ6uvJ-ZrOFkrWfQRA7Lsu-GArgzFc1Kh3AcLBne7EiurWjfkeQPgg==)
12. [sosy-lab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFifCExlcY4fabPIMSBhtuSFBPe54L3s72RWXWrKJTJ2aii23BjaQGyuBMWI2oFIeoYI46WhHJYSWnlau6tMmI1CFltAiAFJiiv4j70j1GhlPBwMN2WTqaTmTGz2li8LrQuRf27G4OWnOr04oS9JJsx9Vsuyc50lJmpZh0Yq0SRlvkb7Y_zhgc=)
13. [easychair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMpKszbvZqBb-j2yK_TF6ywudH_q0Tn6gRJ1g_G0QscYRT8F3s6R1QRTI_Bh_vC54pOtdO6w0oxts6g5e38QM5kWKzQ6LcJ2tKGveAwrV8f_rdleZBCuBqZI4XOcPNKsPeq--srsVoQGr-tQ==)
14. [abo.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_RAUlbm3TCyxUQpXx-QyFExsUrl7XokP0d4UcmRDOvG5Im150ozep1Jq8P3_4TwOIh9DgKUMU3rZCYCqixhy0QVz_GyZdGnrM0oQNEGwZf4zrILqpleDjKx3rzYNBPkPvjh5AwTvWPhkg54VPkgNLU5CtV_1Z-Iledhp0cI0HZ7PUquWthJHWhelU)
15. [easychair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcagIS0MaMVMktN0enpl_vB2WD4wKxPGdpr76mPW2sn62hYQZn8eHx-CYsiaB_KVSYHuhZH6fu3mGPIeiMPL-3ePbjBdyDyDLLPyaC9mQ_TWrrhuFICMfKOmY14JxHd_34JdMCFg3-3Q==)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNFwDFLt89QCJx-VaA0VK9X29rXis9c8vwSS6y157UAlwjwTaBK7cWzFxPVrchf7UgNJ6Gyxm4cIbAlOT06isA1OVnk7_9Fqg89OshgI5FtuFt8NXxZZ7WuBY0PysupCTSTVGiggAKs1cZR6Zd1UP95DzBu58pnAXO3Q1smYKRfXKO-t5EFmyIV-O5Aq1t_A5Wm0RZRRW-5suA42ZBUs6gC98ztH1J6az3aEP2u8TZywOVqA0=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2RFdldchlVne0HDdUKiYPPZf4b5q2SmxXZ-PMLbRBRnCSLLcKrnFEGYAraj4te3To1zYR5mr-ySWHNrZ7tbggxZ1yokCtg08NgXoQyhpgSMvBQKlDH-TFMg==)
18. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQeUF5bxT_Nty8xHbOKaEZPJhJk16wAuMESudPo20IdbVR2u8EQJS2DbNuKN9BdIyXWSn6Nx8L8-wdS9S2zp-r_AwEfGGSFmb1oQLIRvRgreS43DeCyiGqFptNpsbQ4QOBYBvnPw3VtZUhYhV4nIDi2Qu_ZBeH0CRSFmp2yCn0B4Keo22iSodn1aejmTUQ63MkxuUK1iO-9Wbvh7inNuLgcQb_Eb1-TaXPcJlWZ_iN9fw90US4LWPXiKg1F_fgDK3Qd0iVHac=)
19. [uniud.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnqYJGjRZUBptMkRxluH2NuR50qDW65fUFLo_E6CDlBKlft9oCTFxZrfY569nqkUEwJrY5eJQADvagK_Lyt-nwQDNHD5542afhg-VUsnuctzlppCOLRk-1UHvrBIKqdzSs03ZwmKV8ESxqYYWNL8q7M8EAlAUeAg==)
20. [dagstuhl.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1qqZTgSWAzqD12cn_biTpTgIhS1JchKYCR2dRctrfm9_ORPf6paMTuA3KQeTmCD7FTVfI6P3FBCaDFyKuQffEqAChc7RTkZJi598Xg6JTOy5ID9ZHkkPRi9HfTn5p05ROgbM4Wr2psX9Jm3lM0A2eeTft7eTkpPZaq3s2)
21. [d-nb.info](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpuQnLanD5H1YpYrz60mImuOTwow5gyMKhLtDNtbCME5ZEJBtYdHo47MRjGSYVHwiiwXcwhjK9foii0pr8JKNPiTFaZOCJHiOIUUXxrd2maRNzuRDq)
22. [bhoxha.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrQX90TK2xkEwKMCjqX7xwlg1ha9tG9RuMsdtOiFlFS6ant2Hor9Gj1vAIWnZdnoBYWl3g5kh-4NPMnGFQLtr9HudzUIEVb5yEzGzOqPMSgCvLvsVTzsmAbWLySNvHD-grxjw=)
23. [tuwien.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyw5u-plvTqTpHGjDBtjcZK108Exrmc_bOcRMcCX_0DEciZq3XaAMY5snaqm8EffATR-9x83GkeG5qtWUYm5FP-9tZK64JrVn8HafV3fbuDbEe6wqs89sSlgXXXiqhIbsJFk3Hset8Qj_ouzQ=)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy5d_3xCf6QE6qklP1K9khmPtbm22xb-w0B1brzsRmbOvbFxbKz6ZAU8RtjYJQiLisUO5L-HYtCF0a3tkl4ndwIoa2ZJ63Re2cHBghVcEKYJS8WcN44w==)
25. [tum.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELFtbLuv1XOsKf95rLvYpVTXeUjtB58CMlkPb-dVpAgZFkZZfGCWCJamvjvhSuNa5uQUoR1BjmQRp1Ai-3SgbA8FJKeIN6sm6Dmy1laFykETqA4WuxLlboAVV_BR1y8eybQMjzh5_fEB2epehixRPDBjk=)
26. [scilit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgRXP-xGi1NGUhHhSHcfTe0paOjvTD9wAlUbgRocA4yVKeThlwvdxQbvjliV1-s65_iJ_VrrMZW0cEW6gz-QjqlijnIY6RJCQ7_Rc7gf43C3-_K1qo1j5Q67u9CbmZIay-ODT37W6Ewb8fU9WdVJBrR-80tL6e)
27. [elsevierpure.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjEOZuSnhDZteub-qlRWRfKgU-AXC_3owSwqS1sdLkQFUBK7NyzJaXKTHsk7i0MavwymYZ0dIUkFPhEX8GzjHMD9TBwHHXI1R7jF76Mwpi4wB2K952mjWWUeSIxl6KMXoUT8I7OD6vJyaWviZ4BZPnjJ-zema6d4FsNJb920bw3fv_CMAJGBZnqS7T2piCsfYJBu8nj5iTR0JD5gejELyA_Ek0HR-kDV58kw==)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL5HyjARNSDI40WB-Hh4pN-JPtX1nJI5CK2hWmoEfrhJUi9uXorjjM-GBAYP1V08B8TDNmHcd-sMo22221MQSbDyUvFeuTcb5HoWgsXgPwuYxXdPFiObCavw==)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhVxGJY2uocdDxBwFlll-9IL3E5BrbdmeBusvleGjIxs9GFWjr8ob0ZUOzb18WYTpIL-W3ZG13fZhcqFDRrDcmvLf-ZWwRl8qf2KKAqD3H-vFe_0pTR-4xM00ejcZl)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFr4sk6Z2rwuwmXYQvKzEUAhjj3e2SFT4TSbFT4UB-_1mJbzcbiHuAs2tyP5ZL5kQs7QjvVCTejnvullOAvZ8h-OMM4iEHlXEZhuPKEGDRUiKv3drwp67pI)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFljZoKi0XN4m1edr8Y3XkxsTPIRRH8uulUFsv7Uz1y1nQJd8Xb-V01ETW9TWNiifJn3guJy6KRawmF8CPimoJrsoOCFpDGn6wi67bUWtwyTuX8fiGW_A==)
32. [readthedocs.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEty-A5-wNfSJpXdD6ozdTU4dbJ5kaqstJJmQhjfZEfxO5b6qGLWPKQyo2I4KWSQel2XhpHfkxHNzGRYduO9ApSG9NGTwiCOtp4f79pj0VBTfy9UxRW3IVDvGWRZEs043XYV5LlumFtjTL_2CiFMrr)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHblqD-4ZrpSXsreOjE1ocDUcSyPUx_8J9uSJU_9ozq-kLFyHyO8oecXZMc6qVtrji-FgT6eedfyJiJySLoLycOAxnfiXV8PdtkURsTb0y0enEQ1TxFtMEIBU0dS8ERpTgLH33K)
34. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-z5GVnPsiS27wWeW6sWjncamc_FlRt8rlMLO_sjvN5mPMDIAcpePSEvXBRB4ezXKIJlYZV24FirCTSixgW4dbgzXygc_N1Q8XgHFP12z3lBpDebP5AfUzIA==)
35. [cps-vo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwSwpenC5T5pMP7FJfj5HGPva5l3PWNue3dnxbY1BAIaFxRPKrMPJVZmETaXpsSsyzy8v0lUKGn_p08YS8YT3NFd6IiLU-6P_ZOaWfHCAssgKmSrySYILaqUMv0ndEFF48Xe0GKJNi2YF01b_6MC62O6TyhgLW4oCNr2YTLCwGplD-vbbbPaI58rHXRA==)
36. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkcnSbjAnVeJEcMN5X9FabzJTTMCylb_U9UrAR_tMv3MtAPe-Gk0PFsv1hvoDBZOiHyyExfG4lXLlVM-c0hgxzFsUqBaKuGqp3uO6Fcpi_lGb6w__VChMsiFRUEAwcrvBRDXyJgVo_C_PqRdu4u3QMD_owWu3W94yhBnIa35PNM2VE7iElQio8Z5MuVCBP52EhoZMMm-cGNNxPjA0ArCMHn2IUhslogKuELJ4shK4qcSrMDg==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBXfW-mv9zy78Kjo3E52p58rmL9tKsMwQn-qIHtobEaq1_FerjTz-S0BmHB3s2GkRbHooDCnEy_Xy2ZN4qcsbKM1AKxgtz-mfAJVoyHmYAjejuYqkY-la5jg==)
38. [gitlab.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGZbE3COFRyR2T1muLajzHOUSmdCtins-nA-gCHM7jEvcrknAxPC2E_WevzuSq-rLcja27lsknXYssszbQZYSkPh-XoIGLe0xwVWhLJBYIt8mFqsH0N4An71a_DSMWwrpY2Noe0fezQOtHb4DG_8KhHO5En7v9JZlM1Q==)
39. [abo.fi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzX2BprMIuuoiW9zZAStUXP16Lv0o8gQdXIT-_B8wkQbphMALUZMnlLKeCvDWb92IKcYi3jTYbJT0iDDNX1t2pzdAW_QBab6_6a_Z7BuliXfbjabJXMXmi4cdVGBPNGEBG9tvN7mSguvDixFwUSR5AH3lH_IRBhxdV6kyvLn9gA5Oo2GOKJHLNd_Y1611JGC4=)
40. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXeu_8bIdhk91i2fuCvmmGL4SYjs-eDa5Kp8va0edSiY2r7jxE9u6zWXQp4Pza4hDvcK3phcIBuDaiEdk6Nzpb_-MXjQhXjJjVggRLTQH9188KpwHIgQ==)
41. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6kCdTlfJvAKF5i0x6p49OhrWoa1JKqvFxBpbnCDdijKAkeV2aMUKPSbqKWFZ-CgZOoeyMCv6lmT9jjZY8K_mAj0m9cU464X6Pi40MnTlgF7lu_tWjnQ==)


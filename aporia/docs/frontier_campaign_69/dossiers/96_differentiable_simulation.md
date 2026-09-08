# Prompt 96: Differentiable Simulation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiYi1mYXZULUFZLTFfUFVQN2JxeHdBSRIXYmItZmF2VC1BWS0xX1BVUDdicXh3QUk
**Elapsed:** 638s

---

Differentiable simulation represents a fundamental shift in computational science, attempting to merge the forward-predictive power of physics engines with the gradient-based optimization frameworks that drive modern machine learning. Your initial understanding of the mechanism is largely correct, but it requires one critical amendment regarding how modern engines handle contact. While early engines simply unrolled operations and substituted smoothed contact models, frontier engines now frequently cast contact as a nonlinear complementarity problem and use the implicit function theorem to extract gradients at the solution, bypassing the need to backpropagate through the solver iterations entirely. 

The consensus in 2026 is that first-order gradients extracted directly from physics simulators provide massive sample efficiency gains for short-horizon, smooth tasks like system identification or soft-body manipulation. However, for long-horizon, contact-rich control tasks such as quadruped locomotion, the utility of exact gradients remains highly contested. The evidence leans toward the conclusion that the true loss landscape of rigid body contact is pathologically discontinuous, meaning that even a perfectly calculated gradient is often practically useless for global optimization. 

FRONTIER PRACTITIONER DOSSIER
Field: Differentiable Simulation

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Differentiable simulation is the engineering of physical simulation processes—state evolution, collision detection, friction, and integration—to be end-to-end differentiable. This allows a practitioner to extract the analytical gradient of a simulated outcome with respect to initial states, material parameters, or control policies. By embedding the physics engine directly within a computation graph powered by automatic differentiation frameworks like JAX or PyTorch, tasks such as trajectory optimization, morphological design, and sim-to-real transfer are transformed from derivative-free search problems into first-order optimization problems [cite: 1]. 

Your description of the failure modes requires a specific, load-bearing correction. You noted that simulators substitute smoothed contact models which describe a different physics, and that truncation biases the gradient. Both are true, but the primary structural failure mode is what the field now calls "empirical bias" [cite: 2, 3]. When a system is nearly or strictly discontinuous, a first-order estimator derived from a smoothed contact model will often exhibit extremely low variance but point in entirely the wrong direction [cite: 3]. In these regimes, the exact gradient of the smoothed system is an adversarial update for the true discontinuous system. Consequently, the zeroth-order methods you mentioned as baselines (such as REINFORCE or PPO) often strictly outperform differentiable simulators in contact-rich policy learning because the stochasticity of zeroth-order sampling acts as a natural randomized smoother that sees the macro-landscape rather than getting trapped in micro-fissures [cite: 2, 3].

What is SETTLED: First-order gradients are unmatched for system identification, soft-body trajectory optimization, and fluid control [cite: 1, 4]. For rigid-body tasks with minimal or sustained contact (such as drone flight), analytical policy gradients converge orders of magnitude faster than reinforcement learning [cite: 4]. Furthermore, the architectural debate is settled: GPU-native, JAX-based, or Taichi-based parallel execution is mandatory. CPU-bound differentiable simulators are obsolete.

What is CONTESTED: The utility of first-order policy gradients for long-horizon, contact-rich locomotion. Researchers aligned with MIT and Google DeepMind argue that zeroth-order gradients are fundamentally better for locomotion because of the discontinuous landscape [cite: 3]. Researchers aligned with ETH Zurich argue that first-order gradients can solve locomotion if the search is guided by Residual Policy Learning, where the gradient is only asked to optimize a small residual action on top of a stable baseline [cite: 4, 5].

What is OPEN: Hybrid estimators that dynamically switch between zeroth-order and first-order gradients based on the condition number of the local Jacobian [cite: 6]; end-to-end differentiable visual and tactile sensor rendering fused seamlessly with the dynamics graph [cite: 1]; and reliable truncation mechanisms that prevent the exploding gradients caused by the chaotic dynamics of physical systems [cite: 7].

In the last three years, the field experienced a major consolidation. Standalone, experimental differentiable engines have been largely abandoned. The field of pure differentiable rigid-body simulation was effectively absorbed into the machine learning hardware ecosystem via JAX, culminating in DeepMind porting the industry-standard MuJoCo engine to JAX to create MuJoCo MJX [cite: 8, 9]. During this merge, we lost the diversity of integration methods, as the community converged almost entirely on MuJoCo's specific soft-constraint formulation for the sake of standardisation and TPU compatibility.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: F. de Avila Belbute-Peres, K. Smith, K. Allen, J. Tenenbaum, J. Z. Kolter
Year: 2018
Title: End-to-end differentiable physics for learning and control
Venue: Advances in Neural Information Processing Systems
Identifier: arXiv:1803.09519
Result: Derived analytical gradients for a 2D rigid body simulator by formulating the linear complementarity problem of contact as a differentiable optimization layer. A practitioner must know this because it established the blueprint for extracting gradients via the implicit function theorem rather than naive unrolling.

Authors: Y. Hu, L. Anderson, T. Li, Q. Sun, N. Carr, J. Ragan-Kelley, F. Durand
Year: 2019
Title: DiffTaichi: Differentiable Programming for Physical Simulation
Venue: International Conference on Learning Representations
Identifier: arXiv:1910.00935
Result: Introduced a tailored two-scale automatic differentiation system for imperative programming, showing that differentiable elastic object simulation could be dramatically accelerated. This paper birthed the Taichi ecosystem that modern multiphysics engines rely on today [cite: 10, 11].

Authors: L. Metz, C. D. Freeman, S. S. Schoenholz, T. Kachman
Year: 2021
Title: Gradients are Not All You Need
Venue: arXiv preprint
Identifier: arXiv:2111.05803
Result: Demonstrated that backpropagating through long sequences of chaotic dynamics inherently produces exploding gradients due to the spectrum of the system's Jacobian. A practitioner must read this to understand why backpropagation through time fails on long physical horizons, no matter how good the simulator is [cite: 7, 12].

Authors: H. J. T. Suh, M. Simchowitz, K. Zhang, R. Tedrake
Year: 2022
Title: Do Differentiable Simulators Give Better Policy Gradients?
Venue: International Conference on Machine Learning
Identifier: arXiv:2202.00817
Result: Proved that first-order gradient estimators suffer from severe empirical bias in contact-rich settings, and that zeroth-order estimators are often theoretically and practically superior for these tasks. This is the most important critique in the field's history [cite: 2, 3].

Authors: T. A. Howell, S. Le Cleac'h, J. Brüdigam, Q. Chen, J. Sun, J. Z. Kolter, M. Schwager, Z. Manchester
Year: 2022
Title: Dojo: A Differentiable Simulator for Robotics
Venue: arXiv preprint
Identifier: arXiv:2203.00806
Result: Modeled hard contact via a nonlinear complementarity problem solved with a primal-dual interior-point method, obtaining smooth gradients via the implicit function theorem. This proved that you do not need to replace hard contact with spongy, smoothed springs just to get gradients [cite: 13, 14].

CURRENT SOURCES

Authors: R. Newbury, J. Collins, K. He, J. Pan, I. Posner, D. Howard, A. Cosgun
Year: 2024
Title: A Review of Differentiable Simulators
Venue: IEEE Access
Identifier: DOI 10.1109/ACCESS.2024.3425448
Result: The single best comprehensive survey of the field, categorising the design trade-offs in contact models, integrators, and gradient extraction methods. It serves as the definitive map of the current landscape [cite: 15, 16].

Authors: Genesis Authors (X. Zhou, et al.)
Year: 2024
Title: Genesis: A universal and generative physics engine for robotics and beyond
Venue: GitHub / Project Release
Identifier: https://github.com/Genesis-Embodied-AI/Genesis
Result: Released a universal, GPU-parallel multiphysics engine supporting rigid bodies, MPM, FEM, and SPH entirely within a unified differentiation framework. This represents the absolute frontier of computational speed and multi-material coupling in 2026 [cite: 17].

Authors: J. Y. Luo, Y. Song, V. Klemm, F. Shi, D. Scaramuzza, M. Hutter
Year: 2024
Title: Residual Policy Learning for Perceptive Quadruped Control Using Differentiable Simulation
Venue: International Conference on Robotics and Automation
Identifier: arXiv:2410.03076
Result: Demonstrated that first-order policy gradients can successfully train quadruped locomotion if the network only learns a residual over a baseline policy, vastly reducing the gradient variance [cite: 4, 5]. 

Authors: K. Onoda, P. Parmas, M. Yaguchi, Y. Matsuo
Year: 2026
Title: Does "Do Differentiable Simulators Give Better Policy Gradients?" Give Better Policy Gradients?
Venue: arXiv preprint
Identifier: arXiv:2604.18161
Result: Introduced the Discontinuity Detection Composite Gradient, a statistical test that dynamically switches between first-order and zeroth-order estimators when approaching non-smooth regions. This directly answers Suh's 2022 critique by combining the strengths of both methods [cite: 6, 18].

PART 3. SOFTWARE I CAN ACTUALLY RUN

MuJoCo MJX
URL: https://github.com/google-deepmind/mujoco
Language: Python, JAX, C++
Licence: Apache-2.0
Year: 2026
Maturity: MAINTAINED
Experiment it can run: Gradient-based trajectory optimization or analytical policy gradients for rigid-body manipulation and locomotion.
Gotchas: This is the absolute community standard today, scaling to thousands of parallel environments on TPUs or GPUs [cite: 8, 9]. However, while it supports automatic differentiation through its JAX backend, differentiating through the core step function frequently produces NaN gradients exactly at hard contact moments. To mitigate this, you must cast the JAX arrays to float64, which doubles your memory consumption and drastically cuts throughput [cite: 19]. Note also that DeepMind provides two backends: MJX-JAX (which is differentiable) and MJX-Warp (which is much faster for contacts but explicitly does NOT support automatic differentiation) [cite: 8]. Ensure you are using the JAX backend if you need gradients.

Genesis
URL: https://github.com/Genesis-Embodied-AI/genesis-world
Language: Python, Taichi
Licence: Apache-2.0
Year: 2026
Maturity: MAINTAINED
Experiment it can run: Differentiable system identification for deformable materials (fluids, cloth, granular media) and rigid bodies in a unified scene.
Gotchas: Genesis is the current performance king, operating at tens of millions of steps per second via its Quadrants compiler [cite: 17, 20]. It is designed from the ground up for embodied AI. The major gotcha is that while its Material Point Method (MPM) and continuous mechanics solvers have mature differentiability, its differentiable rigid body simulation was labeled experimental until a very recent 0.2.0 release [cite: 17, 21]. The ray-tracing renderer (Nyx) is highly advanced, but backpropagating through the renderer to the physics to solve purely visual sim-to-real gaps remains computationally brutal.

Dojo
URL: https://github.com/dojo-sim/Dojo.jl
Language: Julia
Licence: MIT
Year: 2022
Maturity: DORMANT
Experiment it can run: Forward simulation and trajectory optimization using a maximal-coordinate representation with perfectly conserved energy and momentum [cite: 13].
Gotchas: Dojo solved the contact gradient problem brilliantly using a primal-dual interior-point method that extracts smooth gradients without spongy contact approximations [cite: 14]. However, it is written in Julia. While there is a Python wrapper (dojopy), the necessity of crossing the Python-Julia bridge introduces friction, and the repository has seen very little community uptake compared to JAX-based simulators. It is an excellent theoretical reference implementation but not the tool you want to build a massive pipeline on in 2026.

Brax
URL: https://github.com/google/brax
Language: Python, JAX
Licence: Apache-2.0
Year: 2025
Maturity: DORMANT (as a physics engine)
Experiment it can run: Massively parallel reinforcement learning using PPO or SAC.
Gotchas: This is a vital piece of tacit knowledge. Brax was famously launched as a differentiable physics engine in JAX using position-based dynamics and springs [cite: 22]. It was incredibly fast but suffered from severe physical inaccuracies and artifacting. DeepMind has quietly deprecated the Brax physics engine. The repository still exists, but the maintainers explicitly warn users to use MuJoCo MJX for physics simulation [cite: 22]. The brax/training RL library remains alive and is used to train policies on MJX, but you should not use the native Brax environments (brax/envs) for any physical experiments today.

DiffTaichi
URL: https://github.com/taichi-dev/difftaichi
Language: Python
Licence: MIT
Year: 2021
Maturity: ABANDONED
Experiment it can run: Nothing reliably on modern hardware.
Gotchas: Included here because it is a massively cited load-bearing paper [cite: 10, 23]. However, the framework was absorbed into the main Taichi language repository. The original DiffTaichi repository is dead, incompatible with modern Taichi releases, and unbuildable on current CUDA toolchains [cite: 10]. If you want DiffTaichi's capabilities, you must use Genesis.

Nimble Physics
URL: https://github.com/keenon/nimblephysics
Language: C++
Licence: MIT
Year: 2024
Maturity: DORMANT
Experiment it can run: Human biomechanics trajectory optimization and inverse kinematics from markerless motion capture.
Gotchas: A fork of the DART engine that provided analytical gradients specifically for biomechanics and skeletal models [cite: 24]. The canonical implementation has severe build issues on modern Apple Silicon (ARM64) and requires specific older Python 3.9 environments to pull pre-built wheels [cite: 24]. It is effectively dormant outside of specialized biomechanics circles.

PART 4. DATA AND BENCHMARKS

MuJoCo Playground
URL: https://github.com/google-deepmind/mujoco_playground
Size: Hundreds of megabytes (XML assets, meshes, and pre-tuned configuration files)
Licence: Apache-2.0 (code), CC0 (some texture assets)
Used to measure: Policy convergence wall-clock time, zero-shot sim-to-real transferability, and analytical policy gradient stability.
Notes: This has entirely replaced the old Brax environments as the authoritative benchmark suite for JAX-based continuous control [cite: 25, 26]. It contains highly calibrated models of quadrupeds (e.g., Unitree Go2) and dexterous manipulators. This is the benchmark the field treats as authoritative for demonstrating that your gradient-based optimizer actually scales to real robots.

ManiSkill 3
URL: https://github.com/haosulab/ManiSkill
Size: Multiple terabytes if generated datasets are fully downloaded.
Licence: Apache-2.0
Used to measure: Generalizable embodied AI and manipulation skills.
Notes: While ManiSkill 3 (using SAPIEN) is not strictly a differentiable physics engine in the same way MJX is, it is the most popular task collection for robot manipulation [cite: 27]. If you build a new gradient-based controller, reviewers will expect you to test its sample efficiency against an RL baseline on ManiSkill or MuJoCo Playground tasks. Be warned of saturation: many classical tasks (like block pushing) are entirely saturated by current algorithms and offer no signal for separating frontier methods.

ThinShellLab
URL: https://github.com/Genesis-Embodied-AI/ThinShellLab
Size: Megabytes (scripts and localized assets)
Licence: UNCONFIRMED
Used to measure: Differentiable robotic interactions with thin-shell materials like garments and paper [cite: 28].
Notes: Built on Genesis. Essential if you want to test whether your gradients can survive the catastrophic buckling and self-collision inherent in cloth and paper manipulation.

PART 5. THE REPRODUCTION RECIPE

The most informative and reproducible experiment that demonstrates the exact capabilities and structural flaws of this method is the First-Order Policy Gradient (FoPG) training of a perceptive quadruped using Residual Policy Learning, as defined by Luo et al. [cite: 4, 5]. If you want a faster desktop equivalent, the core physics dynamics can be reproduced using the official DeepMind `training_apg.ipynb` tutorial in MuJoCo MJX [cite: 19]. We will specify the MJX Analytical Policy Gradient baseline, as it is the foundation of Luo's work and exposes the exact truncation and contact biases you need to measure.

Software and Version:
Python 3.10+, MuJoCo 3.x, `mujoco_mjx` (latest PyPI release), and the `brax` training library (v0.14.0 or newer).

Dataset/Generator:
The `CartpoleBalance` or `Ant` environment loaded directly from MuJoCo Playground via `mujoco_playground.locomotion.load()`.

Parameters to set:
1. `jax_enable_x64 = True`. (Mandatory: using float32 will result in NaN gradients the moment the system experiences a hard contact constraint) [cite: 19].
2. `truncation_length = 20`. (The horizon over which BPTT is unrolled. If you push this to 100, the gradients will explode).
3. `learning_rate = 1e-3` using the Adam optimizer.
4. Contact model: Use MuJoCo's default soft constraints (elliptic friction cone, soft impedance). Do not override with hard LCP solvers, or the gradients will vanish.

Replicates and Seeding:
5 independent replicates. Seed regime: JAX PRNG keys initialized from `[cite: 8, 9, 29, 30]`.

Compute Cost:
Roughly 10 to 30 minutes on a single NVIDIA RTX 4090 or A100. Because the gradients have low variance but high computational cost per step, this does not benefit from massive environment parallelization in the same way PPO does [cite: 19].

Expected Result:
Objective value against wall-clock: The FoPG method should reach convergence (maximum reward) in significantly fewer samples than a baseline PPO implementation. However, if tested on a complex contact task (like the Ant), pure FoPG will likely get stuck in a local minimum and fail to achieve the asymptotic reward of PPO. Tracking the gradient norm over the rollout will reveal massive spikes corresponding to foot-ground impacts, demonstrating the truncation bias.

The three most common ways people get this experiment wrong:
1. Failing to cast JAX to `float64`. The forward pass is stable in float32, but the backward pass through the LCP contact solver will immediately generate NaNs [cite: 19].
2. Unrolling the horizon too far. Believing that "more foresight is better," newcomers set the unroll length to 500 steps, completely ignoring the system's Lyapunov exponent, resulting in exponential gradient explosion [cite: 7].
3. Comparing wall-clock time unfairly. Autodifferentiation through `mjx.step` is computationally heavy and scales with O(m * (m+n) * T). A single step of APG is much slower than a single step of PPO. If you plot reward against sample count, APG looks like a miracle; if you plot against wall-clock, the gap narrows dramatically [cite: 19].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to push the frontier in 2026, you will have to build a Differentiable Estimator Routing Layer. 

What goes in: The current state, the action, the Jacobian of the simulator step, and a hyperparameter governing variance tolerance.
What comes out: A policy gradient update that seamlessly blends exact analytical gradients with REINFORCE (zeroth-order) gradients.
The hard part: As established by Suh [cite: 3] and Onoda [cite: 6], exact gradients are actively harmful at discontinuous contact boundaries due to empirical bias. Currently, no off-the-shelf framework automatically monitors the state space and routes gradient computation. You have to write a PyTorch or JAX module that tracks the confidence interval of the gradient or runs a Discontinuity Detection Composite Gradient (DDCG) test in real-time [cite: 6]. If the condition number of the Jacobian spikes (indicating a discontinuity), your layer must automatically detach the auto-diff graph and substitute a score-function gradient estimator for that specific transition.
How much work it is: Moderate to high. The math is settled by the deep RL community, but engineering this efficiently in JAX's `vmap` paradigm without causing massive branching penalties on the GPU is very difficult. Several groups have rebuilt crude versions of this privately by simply injecting heavy Gaussian noise near contacts, which is inefficient.

Additionally, you will need to build Differentiable Actuator Dynamics. MuJoCo MJX and Genesis assume idealized torque limits or perfectly stiff PD controllers. Real robots possess complex electrical motor dynamics (back-EMF, rotor inertia, thermal limits). To do direct gradient-based sim-to-real optimization on a real quadruped, you must write a differentiable motor model that sits between the policy and the physics engine.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

This field is littered with methods that appeared mathematically elegant but failed on contact with physical reality. 

Failed Programme: The Brax Physics Engine
In 2021, Google introduced Brax as a revolutionary JAX-based differentiable physics engine [cite: 22, 31]. It utilized maximal coordinates, position-based dynamics, and spring-based constraints to maximize TPU parallelization. It was incredibly fast. However, the community quickly realized that approximating hard robotic contacts with springs resulted in spongy, inaccurate physics. Policies trained in Brax often exploited these physical artifacts to achieve locomotion that completely failed on real robots. The programme to make Brax the primary engine failed. DeepMind effectively deprecated the Brax physics engine, rewrote the highly accurate MuJoCo engine in JAX (creating MJX), and relegated Brax strictly to an RL training algorithm library [cite: 22]. 

Failed Approach: Pure First-Order Policy Gradients for Long-Horizon Locomotion
Initial excitement suggested that differentiable simulation would render reinforcement learning obsolete. This did not work. If you try to train a humanoid to walk from scratch by backpropagating through a 1000-step differentiable rollout, the gradients either explode into NaNs or vanish to zero. This is structurally unavoidable because physical systems with collisions are chaotic; their Jacobians contain eigenvalues greater than 1, causing exponential growth in the backward pass [cite: 7, 32]. 

Standing Critiques:
1. "Gradients are Not All You Need" (Metz et al., 2021) [cite: 7]. This critique argued that differentiable programming fails on recurrent or unrolled physical systems due to chaos. Truncated Backpropagation Through Time (tBPTT) is used to stop the explosion, but this introduces severe bias because the optimizer is forced to act greedily over short horizons. This critique has never been definitively answered for long-horizon tasks; it is simply managed through hybrid workarounds like Residual Policy Learning [cite: 4].
2. "Do Differentiable Simulators Give Better Policy Gradients?" (Suh, Simchowitz, Zhang, Tedrake, 2022) [cite: 2, 3]. This is the most damaging critique of the field. Suh demonstrated that substituting smoothed contact models (to make the math differentiable) introduces "empirical bias." The analytical gradient of the smoothed system might have zero variance, but it points toward a local minimum that does not exist in the true, hard-contact physical system. Consequently, a noisy, zeroth-order RL algorithm (which explores the macro-landscape) reliably outperforms the exact differentiable gradient on complex tasks. This critique was partially answered in 2026 by Onoda et al., who developed the DDCG method to switch off analytical gradients near discontinuities [cite: 6], and by Luo et al., who bypassed the issue by using RL for the macro-policy and analytical gradients only for the fine-tuning residual [cite: 4].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you have compute and engineering capability, here is exactly what you should do, ranked by feasibility and impact:

1. Differentiable System Identification for Sim-to-Real Transfer
What it is: Take a dataset of real-world robotic manipulation of a highly complex object (e.g., routing a deformable cable or folding a garment). Build a Genesis MPM simulation of that object. Use gradient descent to backpropagate the error between the real trajectory and the simulated trajectory into the physical parameters (stiffness, friction, density) of the virtual object [cite: 33]. 
Why now: Genesis finally has the GPU speed and differentiable continuum mechanics to make this feasible in hours rather than months [cite: 17].
What it measures: The exact parameter values that close the sim-to-real gap for deformable objects.
Falsification: Train a policy on the newly optimized simulation parameters. Deploy the policy on the real robot. If the policy fails, the gradient optimization merely overfit to the noise of the specific real-world trajectory rather than discovering true physical parameters.

2. Hybrid Gradient Routing for Dexterous Manipulation
What it is: Implement the Discontinuity Detection Composite Gradient (DDCG) layer inside MuJoCo MJX [cite: 6]. Train an anthropomorphic robotic hand to perform in-hand reorientation of a cube. 
Why now: The theory for tracking empirical bias is now mature, and JAX allows custom gradient definitions (via `jax.custom_vjp`).
What it measures: Wall-clock convergence time and asymptotic reward against a pure PPO baseline and a pure APG baseline.
Falsification: If the hybrid estimator does not achieve a higher final reward than pure PPO, the overhead of calculating the analytical Jacobians is entirely wasted compute.

What will NOT work:
Do not attempt to train a purely vision-based, end-to-end locomotion policy from raw pixels to motor torques using analytical policy gradients. Backpropagating a gradient from a reward function, through the physical contact model, through the rigid body dynamics, and finally through a differentiable ray-tracing renderer back to the convolutional policy weights will fail catastrophically. The combination of contact discontinuity, rendering discontinuities (occlusions), and the chaotic explosion of the Lyapunov horizon guarantees that the gradient will either be pure noise or immediately overflow to NaN. The variance will destroy the optimizer long before it finds a valid walking gait.

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT5Xh4OnPFE59rFgbKIdbTK2brEI_-zvKRG6D-WFiZgr3w-lsiKVCrnKPKtC1BHWTeLrHKSql75zeeOjpiOHyrVvxSgHu0pbaxIpGEUIbW8INuYmdXZtv9jJNBBfCtn9WDvBaBEeH81mG6pqPF7DXggyA=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEe_CJDkvuYKCNP8jRkUIm9aCL2zghs5Q9rtTo0YB8cjrhPJ7u5Rs_rNru8P2FM3-lHLqUsfZsdmyU1iX0PAenHh7Nih4SQVG-bmNBHWl8kIACcFH2rpRfJ)
3. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_WTuGn61zvCAfew0_z6VgmQwKfaCm_ndcBpKVgCAOQfxZ4adZ28G7R8egYslL_Z3vvxLi1D2ytHF5k7EU4s732aW-9aTYjcuW3kdH95irmRF1YSvvhr75w_adlt61tM_84JJ1MPaZiKI=)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyc9m-KS6NdI9nH4_GMeG-k7PeiBIIu_gS5fvitW91aATPDbS-YUB8EyDOB8mBXCIEYVdZ3JRYkNGC8dwVBBboel34DLWrG1bNiQxZvdyzmDcRmHoR)
5. [uzh.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGG8rYInhWV0mj7yriLKhCC0WAt_CS0q5HcFY40w6VmwNKMUD8PpS3Iwg24dB7s6fwl7P-25qtW0S4MpOw0zPZXTbN6SSuvpH-pXPvqoSfWx0BaMaPDFBn6HIdkBOG_sg==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtMipUTQDBWDYgBF34Oy7V1pRqUnQD8mUCi8cZ0F2iXYggshlMvbHs3raifFeaG9kvggCxsIRNOxhqwwFokER-1qKqzEIHZNxF3YiYZtv7TdIN5oel5clC)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeM2DVKRGdJVKc-wCoC68op2YN8J-hvV898ZeIQkBd2PWq5lmetW6_vZ9iIwQUpa-XlEo3XqDHsC0iblJkBqe60kMKy0gtPeVMhdB6oZdCy5VeXeDc)
8. [readthedocs.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUIIb30NqNIy8V3IYUmSipHbr_Xn6-v03a9QRRn2Q4a-Oqef44t7d1JyVNU70a2U1WIO1_ArW94yVnV0zpahczPv_O34MkdCpgXZ4_OZMZJNeSetvvr66M_r_KkdVGk25fhQsITA==)
9. [roboticscenter.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEylvMZPchoZJDFtG7t_Nt0QXxLH1LZ01EPqkW-YxiSSrGFoSXQzeiylVR5gT49gbYi1pVGw1e8IJVjvoqwEfhz2-GIk25C4Zap3lirTchkT3W7ij_idMctX5tvJQCQyCVTgzBY2lZnzsk=)
10. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRqvCCyrAgAkc_Xrvze3GLYggfzpEbOW5IkVQ18l-4BBX16CefGYPv55_RrUw-2CY7CMHqbt5F_kdx61ieXUCiMujvWLUS2Wkmb79FeOqBQYHZg5nEn_LHnutESOU=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDBkPXHswqL99gHn9xCdjS2U3pRAB_YXUUNDr8-csgN5VCBO_vN4MJQAwNLQRx6oZpKahi3ijmYGJgGX20GmNWffQrw3e0MjvJoiD9zC1A7PiYPrNOA2vs)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6G4KNwJ5x8tiERExLN5_qRoOMATfkOOhYT5WWFew71PHu9-sBduWVLN7LADBzttJWNltSRPKCblcVSXTUD1MyjTEQMXYx_-Jl4Zzdae0IMXQ0hJoovkeW)
13. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3DOmEwd8k93_KA52n_cl5usAGYeKVwRKiPFRKkgl4o58KvyFregoboAOgGfInyROhV2WRyPbKdltFXavFy_Yu-e7kzijK-nG4nobEFIPKZmtI4Abhe1Z0XqfooS9Id9M=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNlLnCrkFAv7-wjvGx7gFPAmkCSaklX097fwCtLlOFmdk07yQwZM098_KCR244C7oEy5cQiiqWjd4vOkR9DSAGhlOEIZhLPG1S41ZgS8sHvsfTKeoQxfmZ)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEAIPOUFydskaZpVoNLiL0zu9IRrkQ7AadPTI4xhjbZR7nY587dovHEZPfZ2_O038XU_EaOiT2_bO4v5IWeszyc6yjY3vsyCu8B0kFEOyr4h26TFt7CmyO-0Y6pjM167Kp1HVBCMgxCejv8GW0euJ3mIp-lNUSx0MmBkpIly4O4xvxvkNwniFLXNYmS4aQ=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEp9zkYD7q0LqYVu9bWRL6X18bNRBTUhcGQe-l7SxbWB9VVKa4y08-tn01z4XMLO1JmG3BBqKVYk1xXowtODQ-D6XUOfhYLugg3PGckOEWfm25SoX82)
17. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3as1oyTEdVWIqCQ3e_8uj10A_0sbWNkucNri1bhZnTvry-xqb30FABeWoeZJRHMT8JExSclyg8ObVXDTY-lPPPPc796GDeAxQZD_diScVheWepm3_kt1lkUw=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPFTxoFwtqxX2WLNFtUijTs5D_tW8iGkkXZwtTnfpw4-AoKMi-72m7MqoOwm59xsRmewJpK6026CEQfpm9h7QQ_I2SwsvyTvLURjTBaB_7S1sBwHAa)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiCt_iqjztm8ykw2l3gTcseh4sFSp8M0qbVZk7j9O_5f7rf2CUq22X5hH0RHiqazhDyWIV3_n6_bYfWsYbwl1938a-EIErDWAH1M7FitATzjUbiFvxb22KChB7phvcYTDsqq-YZoZ3U1tchPDGMHn7R2XjkaL6IrI64mcwOw9N)
20. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWfkLxa6JjxVYnK2MYnYq1U_hOZ3f-rcqjUN5gosavo8scvCuvO8mtOweOgcHKnb69qStjUrkrPg0HjdiTEALcJ39_0ZGSJOx6-2BYCg8y-9JEZmi4rpZGCU4QRUJz5WVFzVTjF4xi1JI=)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKgPMdfAyrJNbVsCsc68enQ7xW8kYMUm3UUA1u1PkUUemmkM3pgbyimXk36OidJMybKst7LCsGDiOayUOWmicLNNP532KmPKu8UrRJ3jY1YnU-xYdDp03bwmoEP1RP0q9ESVcKKp9HES63NxMWsQodyYw=)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGcDuF3ORCtHtm6WViY0ULA0A2AIP8nPT4PmE4nY_G_3Gi2KmuW4gspPX45tEXC_a4vI6dVSXqemlK3jugUWGfndyes3zsSxhqJIyqqFaGpT4-P4M=)
23. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnjxXtXkoMkdOt5dhS13BtgJTimWvB5Vt8-D3Be2wS9zC8aUO5NW-Ay1YMCM7fq03fVMmIuTTlW6XoEI10nOdscaHNOwnRqF85G1aPip8ivFr2bTnyssCKIBtWkwgETw==)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMiu_6ioOjOZANipMJImWUEFCaaBLRy1dcGNeZdRdTr3Y_AVkNFuSMVqaDk7dWA2clKP8APVrOrpQkItTlGERGcsZumgj5GKqvF6EwrcbV8V0b2BZGjeeATtmH4w==)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHof_xLTcoWxT4kG22_6OTfDnQceiXtBbKEAO5UAJT9KkEDrNNLyy9a8ElQdt3BOk9QoM0m8YIEjMHiTNapclwMfs6ftdgmUg-eoP-z2gZwieBc5s8sZH36UoHnkBrEKjQWAibZhc2oXFM=)
26. [sourceforge.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9e7t0OimeUQBUE3hmRJla3nGLrqpouRk4W9nMM5AX8SH2ldPvNBzzlDcBM0NHWyVcdC5B-7RJpPB3_tQ_9sMIePGdkhSMODzRZM_NGf8QvxY6QZ2j9XZromPUVuY3_cVAE256njcnpoQup7L8V7c=)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJK1rdzza0oWmx-DVMNdVG5HS3s1HX817sEIN2enZrd-k6i_Zk9xSQZ0LS-UdDQUD_8qekHhwDTiAjCNs1tRl_sCdNkkQpaBZJB9BrDbjYwcvuQ9NUh3Ym)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7dZd0e8JNM1kgVdXYguCpN_h_yrpJaXEQcdBHHeZ2BnNohUVToxm5gRbX31MOxIoYMi8I9KrdWGj50nV30bioEO4Wh_7vV99J_hYEdMv92dn8wpccpYeNB22I5hjp-ZYVXmm8p3My9Q==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNMFcVHweWb2OpkUth2Pz_KMbnMuk8i1-53gs7nhoH2wBnl9MQAdaQzZ5soqfiKBTqtQwTmC1D_-GyqH4dX1n2LAb2IqHblmJE-fT77K1EW0RSII4fiFSi)
30. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1NoqEv6OdhShJZLCU74VmiviS0aVSqga6OtzwnPjKYyN7zCiilXl0R1d0_Mrclg_SLimwRhpRkmxFBr17G-MmDiHsavUv5JE7eKzrCqGpUk-F73c0F1w1X2hwxrq5745zsU2oyZqu)
31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENGL5wx7BAYT_cAUuYExmwBfkRI5XPLZ0xJ0MIoplfKoEUFoxxPzuRBNvFlRdKJp34CyvZd1JudzY-kUTBefhIlsiwmt0tg-bN-HBV3IVn0m4GA6WL)
32. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7T-Ji8T9tVPeAGpq_CrxVJIndsrDIi2Te-fob4hUvObURIqNG3qnJqY7RWE8_9yFw5cuwRHcwhlhlLUNdEK5vN0EZSSBbsrASU0AgWkeWVCxNHfZ5waDOyOwFi7MisS-3lxPpnoPDXquLmXqOSyvExWyTs5DGj_rH3yTsxLBUCdX8T8jvcg==)
33. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElm1vixU6UfHr-CuRVhz8v-R3uc5UFbyKSszKdlX_x6zWqL4JwIlvxycCBiMA1RzwXUuXpOaLdF2dUNeWIJGBW17yp25tSTAbmgT7o-GIDY6A_McY7Lle2)


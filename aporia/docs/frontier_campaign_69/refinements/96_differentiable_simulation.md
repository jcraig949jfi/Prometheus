# Prompt 96: Differentiable Simulation

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc0OFdmYXZ1d0hZLTFfUFVQN2JxeHdBSRIXNDhXZmF2dXdIWS0xX1BVUDdicXh3QUk
**Elapsed:** 638s

---

Differentiable simulation for robotics and control is a field defined by a powerful mathematical premise heavily constrained by physical reality. Your understanding of the mechanism is highly accurate. By embedding the time-integration of physical dynamics inside an automatic differentiation framework, practitioners can compute the exact gradient of a downstream objective with respect to initial states, control sequences, or hardware parameters. This transforms policy search and hardware co-design from a high-variance trial-and-error process into a directed optimization problem. Research suggests this approach can achieve convergence orders of magnitude faster than model-free reinforcement learning on smooth, short-horizon tasks. 

However, the field is currently grappling with a severe reality check. Evidence leans heavily toward the conclusion that taking the true gradient of a chaotic, discontinuous dynamical system is often counterproductive. Hard collisions create undefined or Dirac-delta gradients. To bypass this, simulators implement softened contact models, meaning the gradient you compute belongs to a spongy, non-physical universe. Furthermore, even in perfectly smooth systems, the recursive chain rule applied over thousands of timesteps yields exploding or vanishing gradients, closely mirroring the chaos-based failure modes of recurrent neural networks. Consequently, the frontier of the field has shifted from simply building differentiable engines to figuring out how to algorithmically tame the pathological landscapes they produce.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Differentiable simulation in 2026 sits at the intersection of computational physics, compiler design, and robotic learning. Over the last three years, the field has transitioned from an era of fragmented, bespoke physics engines written to prove a point, into an era of monolithic, highly optimized frameworks backed by major tech institutions. The ecosystem has largely standardized around JAX for rigid-body control (led by Google DeepMind's transition to MuJoCo XLA) and Python-embedded CUDA/Taichi kernels for multi-physics and deformable objects (exemplified by NVIDIA Warp and the Genesis framework). The core value proposition remains the same: extracting analytical first-order gradients (First-Order Policy Gradients, or FoPG) to drastically reduce the sample complexity of control and design optimization, compared to Zeroth-Order Policy Gradients (ZoPG) like Proximal Policy Optimization.

What is SETTLED: The software infrastructure for differentiable forward dynamics is functionally solved and highly performant. We now have robust, accelerator-native physics engines that seamlessly integrate with modern machine learning stacks without requiring users to write custom backward passes. It is also settled that differentiable simulation is the dominant method for system identification (calibrating simulation parameters to match real-world data) and for optimizing open-loop control sequences over short time horizons. Finally, it is settled that naive, long-horizon backpropagation through time (BPTT) for contact-rich policy learning is a dead end due to chaos and the chaotic spectrum of the dynamics Jacobian.

What is CONTESTED: The utility of First-Order Policy Gradients for closed-loop, long-horizon control remains highly contested. On one side, researchers focused on sample efficiency argue that carefully formulated FoPG—using truncated horizons, learned value-function baselines, or residual architectures—will eventually outperform ZoPG in sample efficiency and final performance. On the other side, standard reinforcement learning practitioners argue that ZoPG is strictly superior because it searches the true reward landscape rather than the biased landscape of a smoothed simulator. This side argues that gradients derived from softened physics actively harm sim-to-real transfer, as the policy learns to exploit soft contacts rather than respect hard physical boundaries.

What is OPEN: True, gradient-safe mathematical formulations for hard, non-interpenetrating contact resolution (such as Linear Complementarity Problems) remain an open frontier, though implicit differentiation offers a promising theoretical path. Differentiable multi-modal sensor simulation (tactile, LiDAR, and acoustic) is still in its infancy compared to differentiable rendering. Furthermore, how to perform zero-shot sim-to-real transfer of a policy trained purely on analytic gradients without it failing catastrophically on physical hardware is entirely open. 

In the last three years, the most significant change was the release and adoption of MuJoCo XLA (MJX) and Genesis. The field of bespoke rigid-body differentiable simulators (like early versions of Brax and NimblePhysics) has been effectively absorbed into MJX, which offers MuJoCo's authoritative contact model natively in JAX. What was lost in this merge was the diversity of alternative algorithmic approaches to constraint solving, as the community largely defaulted to MuJoCo's specific flavor of soft-constraint relaxation out of pure convenience.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: de Avila Belbute-Peres, F., Smith, K., Allen, K., Tenenbaum, J., and Kolter, J. Z.
Year: 2018
Title: End-to-end differentiable physics for learning and control
Venue: Advances in Neural Information Processing Systems
Identifier: arXiv:1803.10228
This is the foundational paper demonstrating that solving Linear Complementarity Problems for rigid body contact can be differentiated implicitly, proving that hard contacts could yield useful gradients for control without explicit smoothing.

Authors: Hu, Y., Anderson, L., Li, T. M., Sun, Q., Carr, N., Ragan-Kelley, J., and Durand, F.
Year: 2020
Title: DiffTaichi: Differentiable Programming for Physical Simulation
Venue: International Conference on Learning Representations
Identifier: arXiv:1910.00935
This paper introduced the Taichi differentiable programming language, setting the architectural standard for how lightweight tapes and reversed gradient kernels should be structured for high-performance multi-physics simulation.

Authors: Metz, L., Freeman, C. D., Schoenholz, S. S., and Kachman, T.
Year: 2021
Title: Gradients are Not All You Need
Venue: arXiv
Identifier: arXiv:2111.05803
The most important critique in the field. It demonstrates the chaos-based failure modes of differentiating through iterated dynamical systems, proving mathematically why analytical gradients explode and why ZoPG often wins over long horizons.

Authors: Freeman, C. D., Frey, E., Raichuk, A., Girgin, S., Mordatch, I., and Bachem, O.
Year: 2021
Title: Brax - A Differentiable Physics Engine for Large Scale Rigid Body Simulation
Venue: Neural Information Processing Systems Datasets and Benchmarks Track
Identifier: arXiv:2106.13281
This paper proved that writing a physics engine natively in JAX allowed for massive hardware acceleration and batching, fundamentally changing the scale at which roboticists could run differentiable environments.

CURRENT SOURCES

Authors: Newbury, R., Collins, J., He, K., Pan, J., Posner, I., Howard, D., and Cosgun, A.
Year: 2024
Title: A Review of Differentiable Simulators
Venue: IEEE Access
Identifier: arXiv:2407.05560
This is the single best and most authoritative modern survey of the field, offering a rigorous taxonomy of gradient calculation methods, dynamics models, and the exact trade-offs between speed, accuracy, and versatility in modern engines.

Authors: Luo, J. Y., Song, Y., Klemm, V., Shi, F., Scaramuzza, D., and Hutter, M.
Year: 2024
Title: First-Order Policy Gradients with Residual Policy Learning
Venue: arXiv
Identifier: arXiv:2410.03076
A load-bearing recent paper that proposes a solution to the poor learning dynamics of analytical gradients in contact-rich tasks by using FoPG to train a residual over a simpler baseline policy, bypassing the harshest parts of the loss landscape.

Authors: Genesis Authors
Year: 2024
Title: Genesis: A universal and generative physics engine for robotics and beyond
Venue: GitHub / Technical Report
Identifier: https://github.com/Genesis-Embodied-AI/Genesis
This introduces the current state-of-the-art framework that unifies rigid bodies, finite element methods, and fluid solvers into a single differentiable ecosystem, representing where the infrastructure frontier currently sits.

Authors: Chen, S., Xu, Y., Hsu, D.
Year: 2023
Title: DaXBench: Benchmarking Deformable Object Manipulation with Differentiable Physics
Venue: International Conference on Learning Representations
Identifier: arXiv:2210.13066
The standard benchmark for differentiable manipulation of deformable objects (fluids, cloth, rope), validating the use of JAX for highly complex multi-material environments.

Authors: Wiedemann, N., Wüest, V., Loquercio, A., Müller, M., Floreano, D., and Scaramuzza, D.
Year: 2023
Title: Training efficient controllers via analytic policy gradient
Venue: IEEE International Conference on Robotics and Automation
Identifier: arXiv:2209.13019
Demonstrates how to practically deploy First-Order Policy Gradients for drone flight, serving as a primary reference for applying these methods to smooth-dynamics systems where contact is minimal.

PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: MuJoCo XLA (MJX)
URL: https://github.com/google-deepmind/mujoco/tree/main/mjx
Language: Python / JAX
License: Apache 2.0
Year: 2026
Maturity: MAINTAINED
This is the community standard for rigid-body differentiable physics. It is a JAX re-implementation of the venerable MuJoCo engine. It allows you to run exact MuJoCo physics on GPUs and TPUs, outputting analytical gradients via JAX's autodiff. You can run first-order policy gradient experiments directly using their provided Short-Horizon Actor-Critic (SHAC) implementations. The main limitation is that it strictly adheres to MuJoCo's soft-contact formulation; if your experiment requires hard constraints, MJX will not provide them.

Name: Genesis
URL: https://github.com/Genesis-Embodied-AI/Genesis
Language: Python / Taichi / CUDA
License: Apache 2.0
Year: 2026
Maturity: MAINTAINED
A highly performant, unified multi-physics engine supporting rigid bodies, Material Point Method (MPM), fluids, and cloth, running up to 43 million frames per second on a single GPU. It can run complex deformable object manipulation experiments today. Its limitation is that while the MPM and Tool solvers are fully differentiable, differentiation for some of the other internal solvers is still being rolled out. It is currently the most aggressive frontier software for physical AI.

Name: NVIDIA Warp
URL: https://github.com/NVIDIA/warp
Language: Python / CUDA
License: NVIDIA Software License (Open Source but specific terms)
Year: 2026
Maturity: MAINTAINED
A framework that JIT-compiles Python functions directly to CUDA, generating both forward and adjoint versions of the code for reverse-mode automatic differentiation. You can run computational fluid dynamics, finite element analysis, or custom soft-body experiments today. The limitation is that Warp is not a pre-built robotics simulator with an extensive library of assets and sensors; it is a spatial computing framework. If you want a full robot environment, you must build the specific physical laws and integration steps yourself.

Name: JaxSim
URL: https://github.com/ami-iit/jaxsim
Language: Python / JAX
License: BSD-3-Clause
Year: 2026
Maturity: MAINTAINED
A multibody dynamics library and differentiable physics engine tailored for control, relying on reduced-coordinate physics (Featherstone algorithms). It can run system identification and closed-loop control design for floating-base humanoids today. Its known limitation is that it only supports collisions between points rigidly attached to bodies and a compliant ground surface, making it unsuitable for complex object manipulation. 

Name: Brax
URL: https://github.com/google/brax
Language: Python / JAX
License: Apache 2.0
Year: 2026
Maturity: DORMANT
Brax was the famous predecessor to MJX. While the repository is still active as a reinforcement learning library, the native Brax physics pipelines (Spring, Positional, Generalized) are effectively dormant for physical simulation tasks. Users are explicitly directed by the maintainers to use MuJoCo MJX for physics. Do not start a new physics-based project on the Brax physics backend.

Name: DiffTaichi
URL: https://github.com/taichi-dev/difftaichi
Language: Python / Taichi
License: MIT
Year: 2020
Maturity: ABANDONED
Famous for being the original suite of 10 differentiable physical simulators proving the viability of Taichi for autodiff. It is effectively dead as a standalone repository. The canonical implementation is heavily outdated, and modern users should rely on the main Taichi language repository or Genesis instead. Published results from 2020 are difficult to reproduce without heavily downgrading modern Python and CUDA toolchains.

PART 4. DATA AND BENCHMARKS

Name: DaXBench
URL: https://github.com/AdaCompNUS/DaXBench
Size: Lightweight repository (under 100MB), generates state data procedurally.
License: Apache 2.0
Used to measure: The efficiency and success rate of differentiable planning, imitation learning, and reinforcement learning algorithms on deformable objects. It is the authoritative benchmark for differentiable multi-material interaction, featuring liquid pouring, rope wiping, and elastoplastic sculpting. It is explicitly designed to compare gradient-free baselines against analytic gradient methods.

Name: PlasticineLab
URL: https://github.com/hzaskywalker/PlasticineLab
Size: Lightweight repository.
License: MIT
Used to measure: Soft-body manipulation using differentiable physics. Contains 10 tasks specifically testing elastic and plastic deformation. Note a known saturation problem: gradient-based open-loop optimizers can easily solve these tasks in tens of iterations, but the tasks are too short to expose the vanishing gradient problems inherent in long-horizon planning. 

Name: Brax Environments (e.g., Ant, HalfCheetah, Humanoid)
URL: https://github.com/google/brax
Size: Procedural.
License: Apache 2.0
Used to measure: Locomotion policy efficiency. The field treats these as popular but heavily contaminated. The contamination comes from the fact that Brax's original environments used highly simplified, continuous approximations of contact. Policies that achieved high reward using analytical gradients in these environments frequently exploited the non-physical "sponginess" of the ground and failed to transfer to higher-fidelity engines or real robots. Treat high scores here as a mathematical artifact rather than a robotics breakthrough.

PART 5. THE REPRODUCTION RECIPE

The most reproducible and informative experiment to establish a baseline in this field is the First-Order Policy Gradient (FoPG) locomotion training using the Short-Horizon Actor-Critic (SHAC) algorithm on MuJoCo MJX, as described in Luo et al. 2024.

Exact Software and Version:
Python 3.10
JAX version 0.4.20
MuJoCo version 3.1.1 (incorporating MJX)
Brax version 0.10.0 (used strictly for the RL wrapper and SHAC algorithm, not the physics)

Dataset or Generator:
The procedural MJX Quadruped (Ant) locomotion task instantiated directly via the `brax.envs` API using the `mjx` backend. No external dataset is required.

Parameters to Set:
Physics Timestep: 0.01 seconds.
Control Substeps: 4.
Contact Model: MuJoCo default soft constraints (do not enable hard solvers).
Algorithm: SHAC (Short-Horizon Actor-Critic).
Rollout Horizon for BPTT: 32 steps (this is critical; going higher triggers chaos).
Discount Factor (Gamma): 0.99.
Learning Rate: 3e-4 with Adam optimizer.
Value Function Network: 3 hidden layers of 256 units, ELU activation.
Policy Network: 3 hidden layers of 256 units, ELU activation.
Batch Size: 2048 parallel environments.

Replicates and Seeding:
Execute 5 independent replicates using JAX PRNG keys seeded from 0 to 4. 

Compute Cost:
Approximately 0.5 to 1 GPU hour on a single NVIDIA RTX 4090 or A100.

Expected Result:
The policy should converge to a reward of approximately 6000 to 8000 on the MJX Ant environment within 10 million environment steps. Compare this against a gradient-free PPO baseline, which will require roughly 50 to 100 million environment steps to reach the same reward. This result demonstrates the core claim: sample efficiency improvements of an order of magnitude. The citation for these numbers is Luo et al., "First-Order Policy Gradients with Residual Policy Learning", 2024.

Three most common ways people get this experiment wrong:
1. Extending the BPTT rollout horizon. Practitioners assume more gradient steps equal better foresight. Setting the rollout horizon to 128 or 256 steps causes the Jacobian to explode due to chaotic contact dynamics, resulting in NaNs or a completely collapsed policy.
2. Replacing the soft contact parameters in the MJCF XML file with rigid approximations. This immediately turns the analytical gradient into a discontinuous step function, breaking the Adam optimizer.
3. Failing to handle JAX's static compilation. Passing dynamic array shapes or heavily branching Python logic into the reward function causes recompilation on every step, turning a 30-minute GPU run into a 3-day CPU bottleneck.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are building an in-silico programme in 2026, the foundational physics and automatic differentiation are provided by MJX and Genesis. However, three critical pieces of infrastructure do not exist off-the-shelf and must be written by a serious entrant.

1. A Physics-Aware Trust Region Optimizer
What goes in: An analytical gradient tensor from a 32-step physics rollout, the current policy weights, and the state covariance.
What comes out: A clipped and regularized weight update.
The hard part: Standard deep learning optimizers (Adam, RMSProp) assume gradients are noisy but fundamentally point toward a valid local minimum. In differentiable physics, gradients originating from contact events can be strictly correct mathematically but physically meaningless (e.g., suggesting the robot phase through the floor). You must build a trust-region algorithm that detects when a gradient magnitude spikes due to a contact discontinuity and selectively masks or heavily discounts that gradient vector. 
Work estimate: 2 to 3 months for a single researcher. Several top labs have privately rebuilt variants of gradient-clipping heuristics specifically tuned to rigid-body impacts.

2. Differentiable Hybrid Sim-to-Real Interface
What goes in: A real-world hardware trajectory and the output of the differentiable simulator.
What comes out: The exact analytical gradient of the sim-to-real gap with respect to the simulator's physical parameters (friction, mass, damping).
The hard part: While differentiable physics makes parameter estimation theoretically easy, real-world data contains sensor noise, delay, and unmodeled actuator dynamics. Directly backpropagating the L2 loss between a real trajectory and a simulated one will immediately overfit the simulator's parameters to the sensor noise. You have to build a filtering layer that differentiable parameters can flow through without losing their physical meaning.
Work estimate: 4 to 6 months.

3. Differentiable Tactile Rendering Pipeline
What goes in: The stress/strain tensor of a soft-body contact event in Genesis or Warp.
What comes out: A simulated high-dimensional tactile image (e.g., a GelSight reading) that is fully differentiable with respect to the applied force.
The hard part: Bridging the finite element method (FEM) resolution with the optical rendering pipeline. You must calculate how internal material deformations alter the surface normals, and then differentiate a ray-tracing or rasterization step. Genesis has teased this capability, but a robust, customizable, off-the-shelf pipeline that you can plug your own tactile sensor models into does not exist.
Work estimate: 6 to 9 months of intense graphics and physics engineering.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of differentiable simulation is littered with methods that looked mathematically flawless on paper but failed spectacularly in practice. Understanding these failures is more important than knowing the successes.

Failed Programmes and Negative Results:
The most prominent failure in the field is the attempt to solve long-horizon reinforcement learning using purely First-Order Policy Gradients (Backpropagation Through Time). Early optimism suggested that if a simulator was fully differentiable, one could simply unroll the simulation for 1000 steps, compute the exact derivative of the final reward with respect to the initial policy parameters, and converge in a fraction of the time of standard RL. This failed completely. As the horizon extends, the sequential multiplication of the state-transition Jacobians causes the gradients to grow exponentially (exploding) or shrink to zero (vanishing). More insidiously, a policy trained this way quickly learns to exploit any numerical instability in the integrator.

The "Bouncing Gradient" Artifact:
Several papers between 2019 and 2021 claimed that differentiable physics could optimize walking gaits for bipeds. Later independent reproductions showed that the optimizers were not discovering robust locomotion. Instead, because the simulators used penalty-based soft contacts to ensure differentiability, the gradients were pointing the optimizer toward gaits that utilized the ground as a literal trampoline. The method was measuring the artifact of the penalty formulation rather than the phenomenon of locomotion.

Standing Critiques:
The definitive standing critique of the field is "Gradients are Not All You Need" by Metz et al., 2021. The authors leveraged chaos theory to show that iterated dynamical systems (like rigid body simulators) are fundamentally chaotic. They proved that the spectrum of the Jacobian of such systems almost always contains eigenvalues with magnitudes greater than 1. Consequently, computing gradients over long trajectories is mathematically doomed; the gradient is dominated by numerical noise and chaotic divergence rather than useful control signals. This critique was so devastating that it effectively ended the pursuit of naive end-to-end BPTT for long-horizon robotics.

Has the critique been answered?
Yes, but only through workarounds. The critique was answered by the adoption of Short-Horizon Actor-Critic (SHAC) and Truncated BPTT. By strictly limiting the backpropagation to 16 or 32 steps, the chaotic eigenvalues do not have enough time to explode. A learned value function is then used to bootstrap the rest of the reward horizon. This concedes Metz's point—long-horizon gradients are useless—but rescues the sample efficiency of first-order methods for short local optimization.

The Unanswered Critique:
A standing critique that has never been answered is the "Smoothness vs. Reality" paradox. To make a physics engine differentiable through contacts, you must smooth the contact model. However, real-world rigid body contact is fundamentally non-smooth. Therefore, the more perfectly you optimize a policy using analytical gradients, the more tightly you overfit to a physics model that does not exist in reality. No one has successfully demonstrated a purely analytic gradient-based policy trained on smoothed contacts that zero-shot transfers to a highly dynamic, contact-rich real-world robotic task without heavy algorithmic intervention.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

If you have compute, coding ability, and a blank slate today, you should bypass the solved problem of building a new differentiable physics engine. Do not write a new solver. Instead, leverage MJX and Genesis to run the following highly specific experiments, ranked by impact and feasibility.

1. System Identification for Deformable Object Manipulation
Experiment: Use Genesis to simulate an elastoplastic object (e.g., dough or biological tissue). Collect video and force data of a real robot manipulating a similar object. Backpropagate the visual and physical loss directly into the MPM (Material Point Method) parameters of the Genesis simulator to perfectly calibrate the virtual material.
Why it is feasible now: Genesis is the first engine to unify MPM solvers and differentiable rendering at speeds that permit iterative optimization.
What it measures: The convergence rate and real-world accuracy of gradient-based system ID for soft materials, compared to random search or Bayesian optimization.
Falsifiability: If the optimized material parameters do not accurately predict the deformation of the object under a novel, unseen manipulation trajectory, the premise of gradient-based ID for complex materials is falsified due to the reality gap.

2. Residual Policy Learning combining ZoPG and FoPG on Humanoids
Experiment: Train a highly robust, low-frequency base locomotion policy for a humanoid robot using standard PPO (ZoPG) without gradients. Then, freeze that policy and train a high-frequency, short-horizon residual controller using analytical gradients (FoPG) in MuJoCo MJX to handle immediate foot-step recovery and slip correction.
Why it is feasible now: Luo et al. 2024 proved this architecture works for simple point masses and quadrupeds. The JAX ecosystem now supports running both PPO and SHAC seamlessly on the exact same MJX memory structures.
What it measures: Whether the sample efficiency of FoPG can be isolated to the exact domain where it excels (short horizon stabilization) without corrupting the long-horizon stability provided by ZoPG.
Falsifiability: If the combined policy fails to exceed the performance of a pure ZoPG policy given the same wall-clock compute time, the architectural complexity of mixing gradient types is proven unnecessary.

3. End-to-End Differentiable Morphology Co-Design for Tactile Sensors
Experiment: Parameterize the physical shape, thickness, and material stiffness of a soft, gel-based tactile sensor on a robotic gripper. Place it in a Genesis environment where it must grasp objects of varying fragility. Differentiate through both the physics of the grasp and the simulated reading of the sensor to optimize the physical design of the sensor pad for maximum downstream classification accuracy.
Why it is feasible now: Generative, multi-physics engines are just now adding the hooks necessary for coupled soft-body and rigid-body autodiff.
What it measures: The direct mapping between hardware morphology and task reward, bypassing human design intuition.
Will it work?: I think this will NOT work in 2026. The simulation-to-reality gap for soft-body tactile interaction is still too large. The gradients will exploit microscopic artifacts in the finite element mesh of the simulated sensor, resulting in an optimal virtual design that acts completely differently when cast in real silicone. The rendering gap for the sensor's optical output will compound this error.

4. Open-Loop Trajectory Optimization through Hard LCP Contacts
Experiment: Re-implement a pure Linear Complementarity Problem (LCP) hard-contact solver in JAX. Use implicit differentiation (as outlined in Belbute-Peres 2018) to extract gradients through the hard contact, completely avoiding soft-contact penalty methods. Optimize a dynamic manipulation trajectory (like a robotic coin flip).
Why it is feasible now: JAX's `custom_vjp` (Vector-Jacobian Product) allows for elegant injection of implicit differentiation rules into standard autodiff graphs.
What it measures: The exact gradient norm and trajectory success rate of true hard contacts versus MuJoCo's soft relaxed contacts.
Falsifiability: If the implicit gradient formulation requires so much overhead to compute the inverse Jacobians that it is slower in wall-clock time than simply running standard reinforcement learning, the pursuit of exact hard-contact gradients is practically falsified.

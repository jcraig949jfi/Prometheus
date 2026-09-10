# Prompt 20: Learning-to-Optimize

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdqS3FlYXBTSU1fSFdfdU1Qc3Vyb21BVRIXaktxZWFwU0lNX0hXX3VNUHN1cm9tQVU
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: LEARNING-TO-OPTIMIZE

LEADING PARAGRAPH

The following dossier synthesises the current empirical, theoretical, and practical frontier of Learning-to-Optimize (L2O). Research suggests that L2O has transitioned from a theoretical curiosity to a computationally viable alternative to hand-crafted optimisers like Adam, though its application remains highly sensitive to the meta-training distribution. It seems likely that the historical barrier to entry—massive compute requirements for meta-training—is being rapidly dismantled by more efficient gradient estimators and PyTorch-native runtime environments. The evidence leans toward hierarchical, tensor-aware hypernetworks as the dominant architecture, replacing the naive coordinate-wise recurrent networks of the late 2010s.

Regarding your current understanding of the mechanism, a critical correction is necessary. Your description flawlessly captures the foundational 2016 era of the field, but it is outdated for the 2026 frontier. First, applying a learned network independently to every coordinate fails to capture global training dynamics; modern architectures use a hierarchical design where a per-tensor LSTM digests global features (e.g., loss trajectory, mean gradient root-mean-square) and outputs weights for a per-parameter Multilayer Perceptron (MLP) (cite: 6, 20). Second, training on ten-dimensional quadratics is a dead end. The loss landscape of quadratics does not transfer to neural networks. The smallest characteristic instance today trains on a distribution of small MLPs and CNNs across datasets like FashionMNIST and CIFAR-10, and tests on held-out architectures (cite: 20, 21).

What follows is an exhaustive, eight-part breakdown designed to equip a computational scientist to build, execute, and measure live experiments in this domain immediately.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Learning-to-Optimize (L2O) is a subfield of meta-learning that treats the design of numerical optimisation algorithms as a machine learning problem. Instead of relying on analytical update rules tuned by human heuristics, L2O parameterises the update rule as a neural network (the optimiser) which takes the gradients and parameters of a target model (the optimisee) as input, and outputs the parameter updates (cite: 1, 5). The field aims to produce optimisers that are faster, require zero hyperparameter tuning, and implicitly encourage optimisees to generalise better by navigating toward flatter regions of the loss landscape (cite: 5).

What is SETTLED: It is settled that learned optimisers can dramatically outperform heavily tuned first-order methods (like AdamW or RMSProp) in both wall-clock time and final generalisation loss on supervised learning tasks, provided they are meta-trained on a sufficiently massive and diverse task distribution (cite: 6, 22). It is also settled that naively applying Truncated Backpropagation Through Time (TBPTT) to meta-train these optimisers fails due to pathological gradient explosion and severe truncation bias (cite: 24, 27). 

What is CONTESTED: The fundamental necessity of exact meta-gradients is highly contested. One camp, led by the authors of "Gradients are Not All You Need" (cite: 28, 32), argues that unrolled optimisation is a chaotic dynamical system. The spectrum of the Jacobian in such systems naturally pushes eigenvalues outside the unit circle, causing chaotic gradient variance. They argue for evolution strategies (ES) or Persistent Evolution Strategies (PES) to smooth the meta-loss landscape (cite: 21). The opposing camp argues that ES scales poorly to highly parameterised optimisers, and instead advocates for probabilistic generalisation frameworks and structural constraints that mathematically ensure convergence without discarding exact gradients (cite: 19, 41).

What is OPEN: The application of L2O to Reinforcement Learning (RL) remains wide open. Learned optimisers built for Supervised Learning, such as DeepMind/Google's VeLO, fail catastrophically on RL tasks (cite: 15, 33). This is because RL agent-gradients are highly stochastic, non-stationary, and non-independent and identically distributed (non-IID) due to correlated transition dynamics (cite: 33, 45). Solving L2O for RL is the current bleeding edge.

In the last three years, the field shifted drastically from scaling at all costs to democratising access and improving compute-efficiency. The release of VeLO in 2022 required 4000 TPU-months, creating a temporary monopoly. By 2025 and 2026, the community reacted by developing compute-efficient meta-generalisation techniques and decoupling the inference of learned optimisers from their JAX-based meta-training environments, porting them to high-speed PyTorch kernels (cite: 57, 58). L2O has not been absorbed into another field, but it has formed a deep symbiosis with the systems-level ML engineering community (MLSys).

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Andrychowicz, M., Denil, M., Gomez, S., Hoffman, M. W., Pfau, D., Schaul, T., Shillingford, B., & de Freitas, N.
Year: 2016
Title: Learning to learn by gradient descent by gradient descent
Venue: NeurIPS
Identifier: arXiv:1606.04474
This is the genesis paper that defined the modern L2O paradigm, introducing the concept of using an LSTM as a coordinate-wise optimiser. A practitioner must read this to understand the baseline mechanics and terminology of the two-loop system.

Authors: Wichrowska, O., Maheswaranathan, N., Hoffman, M. W., Colmenarejo, S. G., Denil, M., Freitas, N., & Sohl-Dickstein, J.
Year: 2017
Title: Learned Optimizers that Scale and Generalize
Venue: ICML
Identifier: arXiv:1703.04813
This paper introduced the hierarchical RNN architecture, proving that to generalise to deeper networks, the optimiser must coordinate information across the optimisee's layer hierarchy rather than acting entirely independently per coordinate.

Authors: Metz, L., Maheswaranathan, N., Nixon, J., Freeman, C. D., & Sohl-Dickstein, J.
Year: 2019
Title: Understanding and correcting pathologies in the training of learned optimizers
Venue: ICML
Identifier: arXiv:1810.10180
Essential reading for the specific failure modes of L2O. It rigorously documents how truncated backpropagation leads to biased gradients, how long unrolls lead to exploding gradients, and introduces the variational bound solution that made later scaling possible (cite: 24, 27).

Authors: Metz, L., Freeman, C. D., Schoenholz, S. S., & Kachman, T.
Year: 2021
Title: Gradients are Not All You Need
Venue: ICLR
Identifier: arXiv:2111.05803
This is the defining methodological critique of the field. It demonstrates mathematically that differentiating through iterative dynamical systems (like L2O inner loops) invokes chaotic regimes where the Jacobian spectrum destroys the utility of exact gradients, necessitating black-box or evolutionary gradient estimators (cite: 30, 32).

CURRENT SOURCES

Authors: Metz, L., Harrison, J., Freeman, C. D., Peshitsky, A., Humphreys, L., Olah, C., ... & Sohl-Dickstein, J.
Year: 2022
Title: VeLO: Training Versatile Learned Optimizers by Scaling Up
Venue: arXiv
Identifier: arXiv:2211.09760
The current high-water mark for SL. VeLO scaled L2O to massive hypernetworks using 4000 TPU-months, demonstrating that an L2O model could replace AdamW completely, requiring zero hyperparameter tuning across a vast array of unseen architectures (cite: 6, 22).

Authors: Lan, Q., Mahmood, A. R., Yan, S., & Xu, Z.
Year: 2024
Title: Learning to Optimize for Reinforcement Learning
Venue: RLC
Identifier: arXiv:2302.01470
This paper defines the frontier of L2O in RL. It documents the catastrophic failure of VeLO in RL contexts and introduces pipeline training to decorrelate agent-gradients, successfully learning an optimiser for RL from scratch (cite: 45, 51).

Authors: Sucker, M., & Ochs, P.
Year: 2025
Title: A Generalization Result for Convergence in Learning-to-Optimize
Venue: ICML
Identifier: arXiv:2410.07704
The best theoretical paper on the frontier. It solves the long-standing problem of providing convergence guarantees for learned optimisers by transferring classical geometric arguments into a PAC-Bayesian probabilistic framework, freeing designers from needing artificial architectural safeguards (cite: 39, 41).

Authors: Therien, B., et al.
Year: 2024
Title: muLO: Compute-Efficient Meta-Generalization of Learned Optimizers
Venue: arXiv
Identifier: IDENTIFIER UNKNOWN
This defines the modern standard for compute-efficient meta-training. It introduces techniques to achieve meta-generalisation without needing thousands of TPU months, establishing the methodologies a single researcher needs to train L2O models on standard GPU clusters.

Authors: Janson, P., Therien, B., Anthony, Q., Huang, X., Moudgil, A., & Belilovsky, E.
Year: 2026
Title: PyLO: Towards Accessible Learned Optimizers in PyTorch
Venue: MLSys
Identifier: arXiv:2506.10315
The ultimate practitioner's guide to deploying L2O. It outlines the translation of JAX-based massive optimisers into CUDA-accelerated PyTorch drop-in replacements, solving the ecosystem lock-in problem and enabling throughput speeds that compete with analytic optimisers (cite: 56, 58).

The Best Survey:
Authors: Chen, T., Chen, X., Chen, W., Heaton, H., Liu, J., Wang, Z., & Yin, W.
Year: 2022
Title: Learning to Optimize: A Primer and a Benchmark
Venue: JMLR
Identifier: arXiv:2103.12828
This remains the most authoritative, comprehensive taxonomy of the field, distinguishing between continuous/discrete optimization, SL/RL applications, and detailing the history of architectures (cite: 16).

PART 3. SOFTWARE I CAN ACTUALLY RUN

Name: learned_optimization
URL: https://github.com/google/learned_optimization
Language: JAX / Python
Licence: Apache 2.0
Year of most recent activity: 2024
Maturity verdict: DORMANT
This is the Google Research reference implementation containing VeLO, smaller baseline learned optimisers, and the massive outer-training pipelines using Persistent Evolution Strategies (PES) (cite: 10, 38). It can run the exact meta-training loop used to create the current state of the art. However, it is a monolithic, highly complex research codebase built deeply into JAX. Its known limitation is that adapting it for novel, non-standard optimizees or running it outside a TPU environment is exceedingly difficult and slow. The codebase is essentially a historical artefact of the VeLO era.

Name: pylo
URL: https://github.com/Belilovsky-Lab/pylo
Language: Python / CUDA / C++
Licence: Apache 2.0 (Inferred)
Year of most recent activity: 2025/2026
Maturity verdict: MAINTAINED
This is the community standard for actually executing learned optimisers on modern ML tasks today. It is a decoupling wrapper that provides highly optimized, fused CUDA kernels for running VeLO and small_fc_lopt directly in PyTorch using the standard torch.optim.Optimizer interface (cite: 55, 57). You can run a drop-in replacement experiment on large-scale pre-training tasks (like ViT-B/16 on ImageNet). The primary gotcha: it is exclusively for meta-testing (inference). You cannot train a new learned optimiser from scratch using PyLO; it only applies pre-trained ones downloaded from the Hugging Face hub (cite: 57, 58). Make sure to set PYLO_CUDA=1 and avoid no-build-isolation errors during pip install to ensure the C++ kernels compile (cite: 55).

Name: optim4rl
URL: https://github.com/sail-sg/optim4rl
Language: JAX / Python
Licence: Apache 2.0
Year of most recent activity: 2024
Maturity verdict: MAINTAINED
This is the reference implementation for the current frontier of L2O in Reinforcement Learning (cite: 50, 52). It contains the pipeline training methodology necessary to handle non-IID agent gradients. You can use this to run meta-training experiments over toy RL environments (gridworlds, simple control) and evaluate zero-shot transfer on Brax environments. The limitation is that it is currently constrained to standard RL agent types (A2C/PPO equivalents) and requires careful environment vectorisation to prevent memory leaks during the unrolled trajectory collection (cite: 45, 53).

Name: mu_learned_optimization
URL: https://github.com/bentherien/mu_learned_optimization
Language: JAX / Python
Licence: Apache 2.0 (Inferred)
Year of most recent activity: 2024/2025
Maturity verdict: MAINTAINED
This is the most viable codebase for a practitioner lacking Google-scale compute who wishes to meta-train new optimisers. It includes features like GPU pre-fetching buffers for tasks to bypass CPU-GPU transfer bottlenecks during meta-training. You can use it to replicate compute-efficient meta-generalisation experiments. The gotcha: memory management is highly manual; the steps_per_jit and num_tasks variables rigidly govern memory, and exceeding VRAM will result in silent JAX compilation hangs rather than clean OOM errors (cite: 9).

PART 4. DATA AND BENCHMARKS

Name: VeLOdrome (and TaskSet)
URL: Access via google/learned_optimization repository
Size: 83 canonical machine learning tasks
Licence: Apache 2.0 (Code), Data relies on public TFDS datasets
What it measures: Generalisation of learned optimisers across a wide spectrum of deep learning architectures (CNNs, Transformers, RNNs, Autoencoders) and data modalities.
Authoritative Status: This is the absolute authoritative benchmark for the field (cite: 20, 22). If an optimiser claims generalisation, it must be evaluated on VeLOdrome.
Limitations: Running the full 83-task benchmark is prohibitively expensive for most academic labs. Therefore, the field heavily utilizes "Mini-VeLOdrome"—a specific 4-task subset consisting of 1-layer, 32-hidden unit MLPs on FashionMNIST, CIFAR-10, MNIST, and SVHN. Contamination warning: Because these four tasks are often used heavily in the outer-loop meta-validation step by resource-constrained researchers, overfitting to these specific image modalities is a known saturation problem (cite: 20, 21).

Name: Brax (RL Generalisation Suite)
URL: https://github.com/google/brax
Size: Dozens of continuous control physics environments
Licence: Apache 2.0
What it measures: Out-of-distribution transfer for L2O models trained on simple reinforcement learning tasks. 
Authoritative Status: Popular but rapidly becoming the standard for L2O-RL papers. Optim4RL uses Brax as its terminal test for zero-shot generalisation, proving that an optimiser trained on a toy gridworld can optimise agents walking a simulated humanoid (cite: 46, 51). 
Limitations: The physics engine simulates massive parallel rollouts, but the underlying optimization landscapes may share unacknowledged geometrical similarities due to the uniform way Brax constructs state-action representations, masking true out-of-distribution generalisation.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to run as your initiation is the PyLO Inference Acceleration Baseline. It establishes the exact latency costs and performance gains of a state-of-the-art learned optimiser against an analytical baseline on a realistic model, avoiding the hundreds of GPU hours required for meta-training.

Software & Version: 
Python 3.11, PyTorch 2.6.0+cu118, CUDA 11.8 (cite: 55).
Library: pylo (GitHub repository Belilovsky-Lab/pylo, exact commit corresponding to MLSys 2026 release).

Dataset: 
ImageNet-1K (via standard torchvision dataloader).
Generator: Vision Transformer (ViT-B/16) architecture from torchvision.models.

Parameters to Set:
Optimiser: small_fc_lopt (loaded automatically from Hugging Face hub via pylo).
Batch Size: 32 (cite: 56, 58).
Learning Rate: Do not set one. The learned optimiser scales itself adaptively.
Weight Decay: 0.1 (decoupled weight decay applied via PyLO wrappers).
Number of independent replicates: 5 seeds (standard initialisation variance).

Compute Cost: 
Less than 2 GPU hours on a single NVIDIA A100-SXM4-80GB to measure stable throughput and initial loss curves.

Expected Result:
You are measuring samples processed per second. The expected result is a throughput of 205.59 samples/second using PyLO's CUDA-accelerated small_fc_lopt, compared to a baseline of 39.36 samples/second if run naively in JAX, and roughly parity with AdamW. Furthermore, the step training loss should descend faster in the first 10,000 steps than a learning-rate-tuned AdamW (cite: 56, 58). 

Three common ways people get this wrong:
1. Environment poisoning during kernel compilation. Users fail to export PYLO_CUDA=1 or run the pip install without the --no-build-isolation flag, causing pip to build in an isolated environment lacking the local system's PyTorch/CUDA headers, resulting in a silent fallback to slow python loops (cite: 55).
2. Dynamic linking order. Users write import pylo.optim.velo_cuda_kernel before import torch. The PyTorch C++ backend must load first, otherwise libc10.so cannot be found, throwing a fatal shared object error (cite: 55).
3. Attempting to tune the learning rate. Practitioners accustomed to Adam apply manual learning rate schedulers to the learned optimiser, fundamentally corrupting the meta-learned magnitude scaling of the network, resulting in immediate divergence.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you intend to run frontier experiments involving the creation of new optimisers, you will hit a massive infrastructure wall. What does not exist today is a PyTorch-native, scalable meta-training framework utilizing Persistent Evolution Strategies (PES) for hierarchical hypernetworks. 

Currently, PyLO provides exclusively the meta-testing interface in PyTorch (cite: 57). The Google learned_optimization library provides the meta-training interface, but it is locked into JAX, largely unmaintained, and highly rigid (cite: 38). If you want to design a novel optimiser architecture and train it, you must build the "Outer Loop Trainer".

Interface Specifications for the Missing Component:
What goes in: A batch of randomly initialised optimisee models (e.g., PyTorch nn.Modules), a stream of dataloader batches, and the PyTorch computation graph of your novel learned optimiser.
What comes out: Unbiased meta-gradient updates to the optimiser's weights.
The hard part: Implementing PES or Truncated BPTT in PyTorch across distributed data parallel (DDP) setups. You must manually unroll the PyTorch computation graph for N steps, accumulate the loss, and backpropagate through the optimiser's parameters without breaking the computational graph or triggering Out-Of-Memory errors. Standard PyTorch is heavily optimized for single-loop gradient descent; backpropagating through the gradient calculations themselves requires extensive use of torch.autograd.grad with create_graph=True, which is notoriously slow and memory-intensive in Python.
Work estimate: This is a 3-to-6 month systems engineering project for a competent computational scientist. 

Signal of a real gap: Both the authors of mu_learned_optimization and Optim4RL explicitly rebuilt simplified JAX outer-loops to bypass the Google learned_optimization monolith (cite: 9, 50). The lack of a PyTorch equivalent forces all PyTorch-native researchers to either learn JAX for the meta-training phase or abandon their architecture ideas.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of L2O is littered with silent failures and retracted assumptions. Understanding them is paramount.

1. The "Gradients are Not All You Need" Failure Mode (Metz et al., 2021)
The most significant negative result in the field is that exact gradient descent is mathematically pathological for training learned optimisers over long horizons. It was originally assumed that you could just unroll the inner optimization loop for 1000 steps and backpropagate through the entire chain. This failed completely. The method differentiates through an iterated dynamical system. The Jacobian of this system naturally develops eigenvalues with magnitudes greater than 1. This chaotic dynamic results in exploding meta-gradients. Conversely, if you truncate the unroll to 10 steps to prevent explosion, the meta-gradients become so severely biased that the optimiser learns short-sighted, greedy update rules that cause the optimisee to diverge at step 100 (cite: 24, 27, 28, 32). This critique has been answered by the adoption of Persistent Evolution Strategies (PES) and variational bounds (cite: 24), but it remains a standing warning: do not trust naive TBPTT in L2O.

2. Catastrophic Failure on Reinforcement Learning (VeLO)
DeepMind and Google built VeLO using 4000 TPU-months, creating an optimiser that beat Adam on almost every SL benchmark. When applied to standard RL tasks, VeLO failed entirely, performing worse than standard SGD (cite: 15, 33). This negative result demonstrated that L2O models overfit to the statistical properties of their meta-training data. Supervised learning gradients are stationary and IID (with proper batch shuffling). RL gradients are highly non-stationary and non-IID because the agent's actions dictate the next state. The learned optimiser's internal RNN state becomes poisoned by this correlation. This critique was partially answered by Optim4RL via pipeline training (decorrelating the gradients by mixing multiple agent streams), but true cross-domain generalisation (training on SL, deploying on RL) remains an unsolved failure (cite: 45, 51).

3. The Memorisation Critique
A standing methodological critique of the field is that L2O does not actually learn "optimisation algorithms" in the analytical sense; rather, it performs dataset-distillation or task-memorisation. Critics argue that the optimiser simply memorises the local loss geometry of the training datasets (like CIFAR-10) and forces the optimisee parameters into a pre-computed basin of attraction, which looks like rapid optimization but is actually data leakage. This critique went unanswered for years until Sucker & Ochs (2025) provided a PAC-Bayesian generalisation result proving that, under specific probabilistic constraints, the trajectory properties of the learned algorithm mathematically transfer to unseen problems, ensuring convergence to stationary points (cite: 39, 41, 43). However, this remains a theoretical defence; empirically, overfitting to the VeLOdrome benchmark is a constant, acknowledged threat.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the computational dominance of massive tech labs in scaling L2O, a well-resourced newcomer must exploit domains where scaling is currently blocked by structural friction, rather than competing on sheer TPU hours.

Experiment 1: L2O for Large Language Model Post-Training (RLHF/DPO)
Rank: 1
What makes it feasible now: The PyLO library allows for the rapid integration of CUDA-accelerated learned optimisers into PyTorch-based alignment frameworks (like TRL or Hugging Face). 
What it would measure: The generalisation of an optimiser meta-trained on proxy alignment tasks (e.g., optimizing a 100M parameter reward model) when deployed zero-shot as the optimiser for a 7B parameter Direct Preference Optimization (DPO) run. You would measure wall-clock time to specific reward thresholds versus AdamW.
What would falsify the idea: If the learned optimiser drives the DPO loss down but results in immediate mode collapse or catastrophic forgetting of the base model capabilities, it falsifies the hypothesis that L2O implicitly preserves generative diversity in flat minima.

Experiment 2: Continuous Adaptation via Elephant Neural Networks
Rank: 2
What makes it feasible now: The recent literature on reducing loss of plasticity in deep continual learning (e.g., Lan's Elephant Neural Networks, cite: 49) can be merged with L2O. 
What it would measure: Measure whether an L2O model can learn a parameter update rule that fundamentally resists the loss of plasticity. You would meta-train the optimiser on a stream of non-stationary, sequentially changing tasks, penalising the meta-loss for the optimisee's dead ReLU ratio or dormant neurons.
What would falsify the idea: If the optimiser prevents plasticity loss simply by enforcing a rigid L2 regularisation equivalent (shrinking all weights to zero), the hypothesis that a dynamic neural optimiser can manage plasticity better than weight-decay is falsified.

Experiment 3: Universal Optimizer Meta-Training in Pure PyTorch
Rank: 3
What makes it feasible now: The community desperation for a PyTorch training equivalent to JAX's learned_optimization. 
What it would measure: Engineering overhead. Rebuilding the PES gradient estimator in PyTorch utilizing the newest torch.compile features to prevent autograd graph explosion, measuring memory overhead and step-time against the JAX baseline.
What would falsify the idea: If the PyTorch computational graph intrinsically requires exponential memory to trace the unrolled optimiser states despite torch.compile, it would prove JAX's functional programming paradigm is strictly necessary for outer-loop meta-training.

What will NOT work:
Attempting to discover a "better Adam" by designing a slightly different hierarchical RNN/MLP architecture and training it on the 4-task Mini-VeLOdrome using standard TBPTT. This will not work because the architecture space is heavily saturated, the 4-task suite guarantees overfitting, and TBPTT will yield chaotic gradients that prevent the meta-loss from fully converging. Without hundreds of thousands of varied tasks and PES (Persistent Evolution Strategies), minor architectural tweaks are statistically meaningless in this field. Do not compete on architecture; compete on the training distribution (RL, Alignment) or the engineering infrastructure (PyTorch).

# Prompt 28: Empowerment

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc3MC1mYXVhNkI3bTJfUFVQay1hbHFRSRIXNzAtZmF1YTZCN20yX1BVUGstYWxxUUk
**Elapsed:** 395s

---

# FRONTIER PRACTITIONER DOSSIER: Empowerment in Reinforcement Learning

The following report addresses the theoretical foundation, practical implementation, and current research frontier of empowerment as an intrinsic motivation mechanism in reinforcement learning. 

Key points to establish before proceeding:
First, the mathematical formulation of empowerment described in your query is fundamentally correct. Empowerment is the channel capacity between an agent's action sequences and future states, representing the maximum mutual information attainable over a given horizon. 
Second, the pure implementation of this mechanism via the Blahut-Arimoto algorithm is effectively dead in modern frontier research due to insurmountable computational scaling issues in continuous and high-dimensional spaces. 
Third, the field has subsequently evolved into variational approximations, most notably Unsupervised Skill Discovery and Unsupervised Reinforcement Learning (URL), which optimize lower bounds of mutual information. 
Fourth, a major statistical limitation regarding the measurement of mutual information bounds the confidence of these neural estimators, posing a standing theoretical crisis for the field. 
Finally, the frontier in 2026 has fractured into two highly promising directions: the integration of causal discovery to filter out spurious environmental entropy, and the application of empowerment-derived diversity metrics to reasoning pathways in Large Language Models.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the study of empowerment exists primarily as a specialized sub-discipline within Unsupervised Reinforcement Learning (URL) and Intrinsic Motivation. The original formulation of empowerment sought to provide a universal, goal-agnostic, agent-centric utility function based on information theory [cite: 1, 2]. An agent computes the channel capacity of its sensorimotor loop, actively seeking states that maximize its potential to reliably inject information into its future environment [cite: 3, 4]. While mathematically elegant, this exact approach has been largely absorbed into the broader paradigm of skill discovery and representation learning. Modern practitioners rarely compute exact channel capacity; instead, they optimize variational lower bounds on mutual information using deep neural networks to parameterize the distributions of actions and future states [cite: 5, 6]. The core philosophy remains intact—agents seek states offering maximum distinguishable control—but the specific mechanism has shifted from discrete state-action transition matrices to continuous, latent-space generative modeling.

What is SETTLED in this field is that pure, exact empowerment calculations are computationally intractable for any domain beyond simple grid-worlds or low-dimensional control tasks. The transition to variational approximations, initiated around 2015 [cite: 6], is considered permanent. Furthermore, it is settled that optimizing mutual information between a latent skill vector and future states (as seen in algorithms like Diversity is All You Need, or DIAYN) successfully induces complex, sensible behaviors such as walking or balancing without extrinsic rewards [cite: 7]. The community broadly agrees that empowerment-based pre-training accelerates downstream task adaptation when sparse rewards are eventually introduced [cite: 8, 9]. 

What is CONTESTED is the validity of the neural estimators used to approximate mutual information, and the handling of environmental distractors. There is a fierce, live disagreement regarding the "Noisy TV Problem," a scenario where an agent is attracted to highly entropic but uncontrollable dynamics (such as a television displaying static). Because the agent's actions (changing the channel) induce massive changes in the sensory state (different static), naive empowerment estimators can be tricked into valuing this state highly. One side of this disagreement, represented by researchers focusing on Causal Action Empowerment (such as Chu, Dayan, and Gopnik), argues that empowerment must be computed over a learned causal graph to isolate variables the agent truly controls [cite: 10, 11]. The opposing side argues that building accurate world models in latent space inherently smooths out unpredictable distractors, meaning better representation learning (like Dreamer-based world models) is sufficient without explicit causal graphs [cite: 12].

What is OPEN is the application of empowerment outside embodied agent locomotion. The frontier has recently expanded into reasoning models, specifically Reinforcement Learning with Verifiable Rewards (RLVR) for Large Language Models. Using sequence-level diversity and empowerment principles to incentivize LLMs to explore diverse reasoning paths (such as the DIVER framework) is a wide-open territory [cite: 13, 14]. Furthermore, overcoming the mathematical proof that any distribution-free high-confidence lower bound on mutual information requires a sample size exponential to the bound remains an open, and possibly unsolvable, statistical challenge [cite: 15, 16]. The field of pure empowerment has been heavily absorbed into Unsupervised RL, and what was lost in this merge was the strict adherence to the agent's raw sensorimotor channel capacity in favor of easily optimized neural proxies.

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Klyubin, Polani, Nehaniv
2005
Empowerment: A universal agent-centric measure of control
2005 IEEE Congress on Evolutionary Computation
DOI 10.1109/CEC.2005.1554676
This is the foundational text that originally defines empowerment mathematically as the Shannon channel capacity between an agent's actuators and its future sensors. A practitioner must read this to understand the true theoretical baseline before it was abstracted away by deep learning [cite: 1, 2].

Salge, Glackin, Polani
2014
Empowerment - An Introduction
Guided Self-Organization: Inception
arXiv:1310.1863
This serves as the single best comprehensive survey and theoretical exposition of the concept, detailing how empowerment acts as a pseudo-utility function and describing early algorithmic approaches for discrete environments [cite: 3, 17].

Mohamed, Rezende
2015
Variational Information Maximisation for Intrinsically Motivated Reinforcement Learning
Advances in Neural Information Processing Systems
arXiv:1509.08731
This paper executes the critical jump from discrete tabular environments to continuous, high-dimensional spaces by introducing variational lower bounds to approximate the mutual information, fundamentally changing how the field computes empowerment [cite: 5, 6].

Eysenbach, Gupta, Ibarz, Levine
2018
Diversity is All You Need: Learning Skills without a Reward Function
International Conference on Learning Representations
arXiv:1802.06070
This paper introduces DIAYN, replacing the raw action-sequence channel capacity with a latent skill conditioning vector, proving that maximizing mutual information between skills and states leads to emergent complex behaviors [cite: 7, 18]. This is the load-bearing paper for modern skill discovery.

CURRENT SOURCES

McAllester, Stratos
2020
Formal Limitations on the Measurement of Mutual Information
Proceedings of the Twenty Third International Conference on Artificial Intelligence and Statistics
arXiv:1811.04251
This is a mathematically rigorous negative result proving that any distribution-free lower bound on mutual information cannot exceed the logarithm of the batch size. Practitioners must know this to understand why their neural estimators fail to scale as the true empowerment of an environment grows [cite: 15, 19].

Laskin, Yarats, Liu, Lee, Zhan, Lu, Cang, Pinto, Abbeel
2021
URLB: Unsupervised Reinforcement Learning Benchmark
35th Conference on Neural Information Processing Systems Track on Datasets and Benchmarks
arXiv:2110.15191
This paper introduces the authoritative benchmark suite (URLB) used to evaluate modern unsupervised RL algorithms, standardizing the two-phase training regime (2 million steps of unsupervised pre-training, 100 thousand steps of supervised fine-tuning) [cite: 8, 9].

Rajeswar, Mazzaglia, Verbelen, Piche, Dhoedt, Courville, Lacoste
2023
Mastering the Unsupervised Reinforcement Learning Benchmark from Pixels
40th International Conference on Machine Learning
arXiv:2209.12016
This paper represents the modern model-based frontier for URLB, demonstrating how to combine world models (DreamerV2) with empowerment-based exploration strategies to drastically outperform earlier model-free baselines [cite: 12, 20].

Dahmani, Dayan, Gopnik
2024
Empowerment and Causal Learning
Workshop: Intrinsically Motivated Open-ended Learning at NeurIPS 2024
IDENTIFIER UNKNOWN
This workshop paper connects empowerment in reinforcement learning with interventionist accounts of causality from cognitive science, providing the theoretical bridge for why maximizing control is synonymous with uncovering causal graphs [cite: 11].

Chu, Rule, Goddu, Dahmani, Dayan, Gopnik
2025
Empowerment through Causal Learning
International Conference on Learning Representations 2025
arXiv:2510.05996
This defines the bleeding edge of the embodied field, introducing a framework where agents construct causal dynamics models and maximize empowerment specifically over the causal structure, vastly improving sample efficiency and mitigating the distractor problem [cite: 10, 21].

Hu, Zhang, Li, Yan, Hu, Cui, Qu, Chen, Cheng, Wang
2026
DIVER: Diversity-Incentivized Exploration for Versatile Reasoning
International Conference on Learning Representations 2026
arXiv:2509.26209
This paper ports the mathematical principles of empowerment and sequence-level diversity to Large Language Models, using them as intrinsic rewards to incentivize deep exploration of reasoning pathways when verifiable external rewards are sparse [cite: 13, 14].

PART 3. SOFTWARE I CAN ACTUALLY RUN

URLB (Unsupervised Reinforcement Learning Benchmark)
https://github.com/rll-research/url_benchmark
Python
MIT License
2021
DORMANT
This is the community standard evaluation harness for the field. It provides the reference implementations for DIAYN, ICM, APT, and others, operating on the DeepMind Control Suite [cite: 22, 23]. You can run the standard 2-million step pre-training and 100k step fine-tuning pipeline out of the box. Its limitation is that it relies on older model-free backbones (DDPG and DrQ-v2) which are highly sample inefficient by 2026 standards, and the repository has not seen major updates in years.

Mastering URLB
https://github.com/mazpie/mastering-urlb
Python
MIT License
2023
DORMANT
This is a modern, much faster reimplementation of the URLB baselines utilizing a world-model backbone (DreamerV2) rather than model-free algorithms [cite: 20]. It can run unsupervised pre-training using DIAYN natively in PyTorch and allows for planning (Dyna-MPC) during fine-tuning. The gotcha is the strict environment dependency; it requires CUDA 10.2 and CUDNN 8, which can be hostile to compile on the absolute latest NVIDIA toolchains without strict Conda environment replication.

DIVER
https://github.com/NJU-RL/DIVER
Python
Apache License 2.0
2026
MAINTAINED
This software represents the frontier of empowerment applied outside of robotics. It runs reinforcement learning with verifiable rewards on LLMs, implementing global sequence-level diversity as an intrinsic reward [cite: 14, 24]. It can be used today to fine-tune open-source reasoning models (like DeepSeek-R1 distillations). It is actively maintained but requires massive multi-GPU compute clusters to replicate the paper's full results.

DIAYN-PyTorch
https://github.com/akazemipour/DIAYN-PyTorch
Python
MIT License
2020
ABANDONED
This was an early, famous standalone implementation of Diversity is All You Need using Soft Actor-Critic (SAC) [cite: 25]. It is effectively dead and its published results are difficult to reproduce with modern versions of PyTorch or Gym due to severe API drift in the underlying reinforcement learning libraries. Do not use this; use the URLB implementations instead.

DiversityIsAllYouNeed-SB3
https://github.com/Egiob/DiversityIsAllYouNeed-SB3
Python
MIT License
2022
UNCONFIRMED
An attempt to implement DIAYN on top of the highly popular Stable Baselines 3 API [cite: 26]. While the integration with SB3 makes it conceptually appealing for rapid prototyping, the repository's activity is unconfirmed and likely dormant, and it lacks the standardized benchmarking harnesses found in URLB.

PART 4. DATA AND BENCHMARKS

DeepMind Control Suite (DMC)
Access route: https://github.com/deepmind/dm_control
Approximate size: Less than 100 MB (Simulator code)
License: Apache License 2.0
This is the absolute bedrock physics simulation environment for continuous control. It is used to measure an agent's ability to manipulate its morphology (e.g., a bipedal walker, a quadruped, a robotic arm). It is an authoritative environment. However, researchers now consider its state-based observations largely saturated.

Unsupervised Reinforcement Learning Benchmark (URLB)
Access route: https://github.com/rll-research/url_benchmark
Approximate size: N/A (Code wrapper around DMC)
License: MIT License
URLB is the specific task collection the field treats as authoritative for measuring empowerment and intrinsic motivation [cite: 8, 9]. It standardizes 12 continuous control tasks across three domains: Walker (stand, walk, run, flip), Quadruped (walk, run, stand, jump), and Jaco arm (reach four different corners). It measures the zero-shot or few-shot adaptation efficiency of an agent that was pre-trained without extrinsic rewards. Contamination note: Because researchers know the 12 downstream tasks in advance, there is a risk of implicit meta-overfitting when tuning the intrinsic reward hyperparameters during the 2 million pre-training steps.

WAVE and DiffSDA Benchmarks
Access route: https://github.com/TCL606/WAVE
Approximate size: Varies (Multimodal datasets)
License: Apache License 2.0
Used for sequential disentanglement and cross-modal learning [cite: 27]. As empowerment moves toward latent video and audio representation learning, these benchmarks measure how well generative models separate static from dynamic factors without labels. This is popular but not yet authoritative.

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative baseline experiment is running the DIAYN skill-discovery agent on the URLB suite using a world-model backbone.

Exact software and version: 
Use the mastering-urlb repository (https://github.com/mazpie/mastering-urlb), specifically the state at the ICML 2023 release commit [cite: 20]. You must instantiate a Conda environment exactly matching their provided YAML file, specifically requiring PyTorch compiled for CUDA 10.2.

Exact dataset or generator: 
DeepMind Control Suite, specifically the "Walker" domain, evaluated on the "Run" task from pixels.

Parameters to set: 
Agent: agent=diayn_dreamer
Pre-training frames: 2,000,000
Fine-tuning frames: 100,000
Use Dyna-MPC during fine-tuning: mpc=True
Initialize both actor and critic from pre-training: init_critic=True, init_actor=True
Number of skills (for DIAYN): 16 (uniform categorical prior)

Replicates and seeding: 
Run exactly 3 independent replicates using distinctly separate random seeds (e.g., 1, 2, 3) [cite: 28].

Compute cost: 
Approximately 30 to 48 hours of continuous wall-clock time on a single NVIDIA A100 or V100 GPU per seed, heavily bound by environment interaction and DreamerV2 latent imagination steps.

Expected result: 
You should observe an aggregated, normalized performance score of approximately 93.59 percent across the URLB suite, far surpassing the model-free DrQ-v2 baseline score of roughly 60 percent [cite: 12, 29]. For the specific Walker Run task, the fine-tuned return should cross 500 within the 100k step budget.

Common ways people get this experiment wrong:
1. Critic Mismatch: During pre-training, the critic learns the scale and variance of the intrinsic empowerment reward. During fine-tuning, the extrinsic task reward is on a completely different scale. If you do not properly re-initialize or rescale the critic head, the policy collapses instantly upon fine-tuning.
2. Latent Collapse in the World Model: If the batch size is too small or the learning rate too high, the DreamerV2 world model suffers posterior collapse, meaning it imagines futures that are physically impossible. The empowerment landscape then drives the agent into exploiting physics bugs in its own imagination.
3. Insufficient Exploration Horizon: Empowerment requires a sufficient horizon \( h \) to measure meaningful mutual information. If the discount factor \( \gamma \) is too low (e.g., 0.90 instead of 0.99), the agent only optimizes for immediate state diversity and fails to learn extended skills like walking.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you are entering this field as a serious computational scientist, you will quickly find that the theoretical math does not match the off-the-shelf tooling. The Klyubin formulation relies on the Blahut-Arimoto algorithm to compute channel capacity [cite: 1, 4]. 

What does not exist: A scalable, continuous-state, GPU-accelerated Blahut-Arimoto solver or a guaranteed unbiased mutual information estimator for continuous RL.

Interface needed:
Input: A batch of trajectories containing state, action, and next-state transitions from a continuous control environment.
Output: A scalar reward value representing the unbiased, exact mutual information between the action sequence and the resulting state distribution, along with the gradient with respect to the policy parameters.

The hard part:
Estimating mutual information in high dimensions requires approximating the marginal distribution of the future state, which involves integrating out the actions. Current neural estimators (like InfoNCE, MINE, or DoE) are heavily biased or strictly bounded by the logarithm of the batch size. As the true empowerment of a complex environment scales to hundreds of bits, the neural estimator saturates and the gradient vanishes. Several groups have privately rebuilt localized, heavily tweaked Difference of Entropies (DoE) estimators with custom cross-entropy clipping just to keep training stable, which is the strongest signal of a deep algorithmic gap. To build a mathematically sound estimator requires roughly a year of dedicated statistical machine learning research, potentially utilizing diffusion models as the density estimator.

What else does not exist: Off-the-shelf Causal Empowerment wrappers.
While the recent Chu et al. 2025 paper proves that maximizing empowerment over a causal graph works [cite: 10, 21], there is no `pip installable` library that automatically wraps a standard Gym environment, performs causal discovery on the state variables, and returns a causally filtered intrinsic reward. You would have to build the causal graph neural network (e.g., using masked sparse regularization) from scratch, intertwine it with the replay buffer, and feed its outputs into a SAC or Dreamer agent. This is a moderate engineering effort, requiring perhaps 2 to 3 months of architectural plumbing.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of empowerment is littered with elegant theories that failed to survive contact with high-dimensional data.

The most devastating standing critique of the field comes from McAllester and Stratos (2020) in their paper "Formal Limitations on the Measurement of Mutual Information" [cite: 15, 16]. They mathematically proved that any distribution-free, high-confidence lower bound on mutual information estimated from \( N \) samples cannot be larger than \( \mathcal{O}(\ln N) \) [cite: 19, 30]. Because empowerment is defined as the maximum mutual information between actions and future states, practitioners were using variational methods to maximize lower bounds on this quantity. McAllester and Stratos demonstrated that in environments with high true empowerment, these bounds completely saturate based purely on batch size. The agent is no longer measuring empowerment; it is measuring a statistical artifact of the batch size [cite: 31]. 

This critique was never fully answered by a mathematical refutation. Instead, the field largely side-stepped it. Practitioners switched to using the Difference of Entropies (DoE) estimator, calculating cross-entropy as a surrogate. DoE provides neither an upper nor a lower bound guarantee on mutual information, meaning the core mathematical foundation of empowerment has been quietly abandoned in practice in favor of "heuristics that happen to go up when diversity goes up" [cite: 16, 30].

Another massive failed programme is the attempt to use pure empowerment directly on raw pixel inputs without a latent world model. Early attempts to scale Variational Information Maximisation to Atari or DMC pixels resulted in agents that became obsessed with specific visual artifacts—a phenomenon known as the "Noisy TV" or "Distractor" problem. Because empowerment seeks to maximize the entropy of the future state conditioned on the action, an agent given a button that changes a screen to random static will press it infinitely. The mutual information between the button press and the highly entropic static is massive. Methods that looked strong in clean, deterministic grid-worlds were later shown to be measuring the environment's background noise rather than genuine agent control [cite: 32].

Claims that failed to replicate include early assertions that empowerment alone is sufficient to solve any survival-based RL task zero-shot. It was later shown that empowerment heavily biases agents toward the center of rooms or states with high physical instability (like keeping a pole perfectly balanced but highly sensitive to input), which does not generalize to goal-directed navigation or complex manipulation unless heavily sculpted by reward shaping. 

Furthermore, the URLB benchmark itself is currently facing a saturation critique. While algorithms like DIAYN, APS, and APT show progress, their fine-tuning success often relies heavily on the fact that the pre-training dynamics of the DeepMind Control Suite perfectly match the fine-tuning dynamics. If the mass of the robot or the friction of the floor is altered between the two phases, empowerment-based pre-training frequently fails to generalize.

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given that raw pixel-based empowerment is statistically bounded and prone to distractors, a well-resourced newcomer should bypass classic model-free continuous control and aim at the immediate frontier.

EXPERIMENT 1: Causal Empowerment in Open-Ended Generative Environments (Highest Priority)
What it is: Implement the Empowerment through Causal Learning framework [cite: 10, 21] inside a modern Minecraft-like or procedurally generated physical environment, rather than the static DMC suite. Use causal discovery to separate the agent's actual avatar from moving background elements (e.g., flowing water, other non-player characters).
Why it is feasible now: The integration of causal graph neural networks with model-based RL (like DreamerV3) has finally matured enough to handle dynamic visual scenes without exploding compute costs.
What it would measure: The divergence in intrinsic reward valuation between a naive DIAYN agent and a Causal Empowerment agent when both are exposed to a "Noisy TV" equivalent in a 3D environment. 
Falsification: If the Causal Empowerment agent still fixates on the TV, or if its zero-shot transfer to a target navigation task is statistically indistinguishable from the naive agent, the hypothesis that causal filtering resolves the distractor problem is falsified.

EXPERIMENT 2: Sequence-Level Diversity as Empowerment in LLM Code Generation (High Priority)
What it is: Build on the DIVER framework [cite: 14, 24], but apply it to software engineering agents rather than math reasoning. Treat the LLM's token generation as the action channel and the compiler's output/AST as the future state. Train the LLM using Reinforcement Learning with Verifiable Rewards (RLVR) to maximize the mutual information between its prompt choices and the execution paths of the resulting code.
Why it is feasible now: DeepSeek-R1 distillations and other open-weight reasoning models have made large-scale RLVR accessible outside of industry labs.
What it would measure: Whether an LLM driven strictly by an empowerment objective (seeking to maximize its control over the verifiable execution state of the computer) will autonomously discover fundamentally novel algorithms without human demonstrations.
Falsification: If the LLM generates highly diverse but syntactically invalid code, or if the "empowered" policy achieves a lower Pass@1 score on SWE-bench compared to standard outcome-based RLHF, the approach is flawed.

EXPERIMENT 3: Diffusion-Based Mutual Information Estimation for Robotics (Moderate Priority)
What it is: Replace the standard InfoNCE or DoE estimators in the URLB benchmark with a latent diffusion model acting as the density estimator for the future state marginals. 
Why it is feasible now: Unsupervised sequential disentanglement using diffusion (e.g., DiffSDA) [cite: 27] provides incredibly accurate conditional probability estimates for sequence data, which were unavailable during the 2018-2021 era of empowerment research.
What it would measure: Whether a diffusion-backed mutual information estimator can break the McAllester-Stratos boundary empirically and provide non-vanishing gradients in environments with true empowerment exceeding 100 bits.
Falsification: If the pre-training phase requires so much compute to train the diffusion model that it violates the standard 2 million step wall-clock budget, or if downstream performance does not exceed the 93.59 percent benchmark set by Rajeswar et al. [cite: 12], it is practically useless for the field.

WHAT WILL NOT WORK:
Do not attempt to scale up model-free empowerment (like SAC + DIAYN) on raw pixels by simply increasing the network size or the pre-training horizon to 100 million steps. It will not work. The statistical limitations of bounding mutual information [cite: 15, 16] mean the agent will stop receiving meaningful learning signals long before it learns useful representations. The intrinsic reward landscape will flatten, and the agent will experience representation collapse. You must either use a world model to structure the latent space, use causal graphs to filter the state, or abandon continuous states entirely for discrete token reasoning.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGfGxNFjypikLTEqFChfqZJcQTfIxlxnuxj1CZgKwofEiMt1oFCAcCnfOqmdZsKNf1unSHz6OlB2qWeeNPlrVIRqruY3lEa3Y-yHjVsaBMTLrrd26wqhxJesCT1K9wmKSbKGxsnxRhIlv9kVBhjo3aQ_9HoFXq0tnTiKut-48Jy3iHqsMyqxHQWSmsqDagi0fhHMpXjXt9GbxicKhvyog=)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-za_ihTpPxWpShFK7L5uv_6czizk2BNLlWiSv9q3MyLC3Kalu18S2xIWPwjAsu97Pe4NczCxzr4cwGum9UtCert6UlXE-9LvmjErsAj2-bmyfDUn2_Go=)
3. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1qL-uEzfSz_nB-RN_iVOw1qMxG9SEU7t5anh7wCYOraKC1TSxgdLHuse07BkXNAtI7cErzL3hqZ7nx6jh9bcYVi5vrNRxBfNXlUDLy2AslXJynJIqKLXs13r2NuFn19N3MFm9fadoisumkk9lC-x_nRd-7BQ6Fws9)
4. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZklUadXhaoH0e7Zs6CZ1zbBiA1FlHoMMi2BXzG89jg-WfFchK7oRfu-sk1zsvnIs-pusJ1scnVaYCp9Hs2uN2PUObwMmtxjujxp3d629c95I8oGa0DovJ1dLxw77AODwjSLRXisbU)
5. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjWfbfxpSdDnqbJuLScGzk22DD0ao2FWb5-M6hFIpQ9DSnHV2oga6MQoW3ijor3_FA2-eZTu049pv03numPUki13jbRcUMYpmo9RxQtc_CuZ7hijYs9ZSmkSyOIvJUpQLxaZdbChasOi1UaK3IFZgJDc73-mrRQ9L_S1acH6AS6P7GurqHrw==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVAeUdMeW7Maop-ceV8x-cDHP9XSMDy_Y1UYsbsF8X_nJQSMQZRuVl0T3B1Y7tk2VXtggDoYSjzS6qTB_c9wZdunxBZoTYFog0RtUYdY33Xaw2-NGiXg==)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiF3fdY4VoPhwEzeBDu2KcPwB2aUylQXoczUh4hblus-U6y66J1yl9crnMrrzYCFzpADivuaR0rbV_Y6VBEvLKkW4Q5W69sUkpRQmcC5QnCEAA43hehlq7xUrLijroHygAs0tRLsG064VhVRYURTchqtlS7Z1ckyXE2qu_hcXVuDcnlbVtmPjl7qjSqycP6sCJ9oJa_qf4O1rPeU9JU4Fj1i65KJvvF1Fdl8On)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5y2a0g_nKElrr0l1DvFLK49RqXs8WmXxBwNeAW4RvNoPz-Mc-XcGJlAp9S8qIwohcD-RTklU2QgxDOH75FonNI4l354Nhw1NTq5jqQX218tnAHjXJsg==)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjLSSoJwoCxrpcixw3yAt1gJqOSJ-w6uyGo8kmW91qyLxRfm4bfzqSkHBDPYRcaVNyftW_9WzmyqkTbbqWPC-mJwI67a4WfDI5eq3ZcC9rPe5GFhYGO-npi0kLGlFV7a6eTF70bPvqI3A5QmnXgaqJ5_suEshnEUNHevAxbi7dHlMgy0UlyLJUOdRWsHvpCSJfReAyp_LBi0_-PQ==)
10. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcrUM5HrsL4NUAEVIjhA6ChPmAbqdYiNjdS9OC8XBYfH_TUw1D82XyEgt8YgF3Hg1fv7nEhL4WCPZthfGmS5R8Y7yOfqdtloCSCrQVV4kz3dQrdbWA75O4UIwFlg0lFxo=)
11. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOYSGrbyw4K4Ua01bSH-ux5v9E7PHSfRkogdWUXzv_yeMnGDFISfQPOTr4Uts_wyvP75Egvx26WPT6j0NdQtkcGycHqwXFOO2QjaQzYlAyhaHgmAEfxE-mjahGkg==)
12. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-wwKFKoTRQd8MPQN-tFDzd95_NohMxnuxFbaRvLVHSGr6z7RZwPJrOjneDiEFsTgKfHDn45ErfWZmYyjXCyVWfIS_hpoVJSJoQeujXwcXS-cMZYt5eIVAfKS6voKAm6F6H5FCt-Xz5VrvWEoZVndGOS4vvQ==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXrcMHkdq0LeV0qCGNErlxv2IgcsSRMdsMd4q9QpYVkpU3WbKnhzCAvfoM-QSiJmDrb2DFkHfgzyit6Tf2ENa_8taaCoMl6g4l_mx78BIYxuMepzcnLRpOtA==)
14. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeHuN4iT86VzzgwPfdgkc_5zt-hD2YnK71bHcVEUAzHmFQLTE_Yt2ofIJLMSjrmO1J5dNc5zhtLPSyQppcL_8korJdcb0IydMgYL3R7mpjBrqGBubhY5InvY5ozmwBii0xe5dSnPVer9kTQeJu7oUJl2t6M-bhpoVkfeiTa-sGvCGHmRVcB26E0T-XO47bFTXF9ZtSpA_CyWJfg2nEUcXR_nSy5Whh7A==)
15. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDe-ulxd0TaKgqKO38A-ZqmJ0oARvSuO6huR154imOsdxn_UrRlDv58whp2Pt_kDq6iYsPcnBWFZUx0GhX6ltqNQBHqeUMPhmvrWKubdrv06im7DCTGh767IXl88neA-W3P_R23ZTy6hgZjw==)
16. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMP9d24Q2-_WLURXtGQwEg6Pq52xAn50pAKwdGQjqw_TeOV7MOsS8X9BiCcvHtbjitd3TmNUYoz6lqgw-nKSOmbKAz8ebeQSoeRCYBd9ieKK7Pe_Rwow__s5I1QMtb2MAqcgnDT0vdnYPTfZmmZTeD1MPhy-xwlic=)
17. [danmackinlay.name](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOTb0MU22CwSvHLGgXVd4cxK4-1kE7yk7SN_eddGMyyzQenU8Vo1WxiQNTvrFNavYeR4cNjxdkWvWHjbXN25LbQgLA93mmNRmZDkK0AdurbUlSj54Ih7v38DxHkxW7mXysZmMGAqIJHDYWbyYhtXmkzmm_iyk7hw==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF1yILL-mE8rEVS3CLF85cqGGL0vmBvr4qOqG-k2QD-5BDyw25q5XgKoP1okF-ZTagiP_2nYH3n-_FoozgrDfWOd1P5QtXUdzXtPpucQhumbREQbVQGZAdG8A==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGRJQZ1IaF_0pAFQ4sTbnyMp9mEqYUssnMgcjm802mw5GcdIGA7MYQA5otKy-U3KHts5nxxyn7x-9fmW0GJ0GZuhwIpP6wdnM2JyG5tDuYeUuHKEVBZg==)
20. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuKNXtoYaHp9TjQBRQ7r1vfedKi6gA4E0W8-3ghlLeXKVBPg94npKcO6nMPHO4xk3apuy66dBT4cow6aTXmVb0vCre1eINGkySnmyL8MHxG2O18mDyUxlyJJrRoSGH)
21. [liverpool.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvXxpU3OTe2SQ3x86sIVm7yrJk0nmP93T6_OAw5ETC7gSaLF1RtxFXyvLAGCC3Ma2LjddVuOtLaYWljxiZmDguNEy6mqPNUD630oUX7slaZAq_JHMEuYj4zZR1ef4k_CxYXRrmGa1IDnQ7yillGUx7fM6Mb51WPnM002AK)
22. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVuKGqRfHrnAO7YnNVykDv-ki1jQYDz9uK2Iz5BKJ9vhbgU7Jzhg5dWAZlZPsW4VCtHVDVxaRbUEkH-BjPwEaniiuR-KE371IAaL7X6DkeOd-LmY6y6pXNIXGbaNQNAdY=)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4WfeJgO4X4RzVoXBjVXiqj4AxQ0HDfiQr48mLcfiwVawx8E8dtpBNueHeIj2qt4oi623zbHkKRA_yI8LAr5j_9GdoZA2hOcrJ8U3PR64FpDSQC5QCr0pJwxjiT1K28hsZczY=)
24. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHEPED8s-dXhxTlF6fT2JhuBpUV9w6R1tMuRlH3OlMPb0Y5HkAk2bDnRcCreqhA6svUuN1OCXmEUVUhLjuiwB_Odk9PjYf_WlJ51ApbwPVMTLeqLIQ8hlpb_g4ymh2bGs=)
25. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6YPxly-AvYtsYsB7jJRaUqjk1TwboK_RyVAcBY97hYuRJoOA_9nxRflNX3_WBcY9xu-mE0s70la2Xr063ZSpywaIqgACGRcGQq0mCJmRl7J-KVvtI5PWGZ8543ODfatyxaQ==)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgiKRLHXvGEh_U_J2bV-QkCbQqeHoPkwREkigIzl7ApbPc8bHP2GWkjiXwXoi8Ew-khHYAWxEUMhjP3kZwZFo5p0SjyC4tiuSIGzUIlSmGHwQxFTmfPbr8QlkoiePHah8qD99in53XZg==)
27. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-YwHRLLzINurM2fzulh3mN0IyLcrhekrVxG-qUDcR5eu9Omz9uzv-QbNIsFWj1tnIrc67Hcqb3fnRPGlmGityo0Z4GnbOa_yXHKbKdLEqLsokVQu4l7e3fkC6-WTVaJQHh2Q=)
28. [imec-publications.be](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa1N21T28uahWFCEeusJgN7J81yuOPQfbufJhgySd9d-VgIe8i_6IpfYBoFzrNNyoQ9x_VffDZ-KPeYnq6BYw9zqz_ORVVBMtJQIw344rKND1UeMPqaxtAptieDUu9u-WYgPPGTJpt1QKxWA0ssjGwu4YaZeq2MSKcknTfcHdPFxD5s-SxCP8TV9HX0XxKEEFn0GXmw714D2a-)
29. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQFDzMiUCnGYNAdsr3DcYxImdlJB7L5Tsgjx8ncMk7FS0GydVbhIz2q826Hf87f_uwyL3QgSPlhbhvWhtWjHTZNyXfpO_5G5zGS3MqBzAX8a7qohLXTEtV06fLKrp9h_j8Ipt5VsQKrDD3p3G47PfI_2LeYlD6mmk=)
30. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZaSrOO31hbFTp2Gop8_E2oSZpc6PIqW7wlcAuOAalpt79jZq_jwuz5eyiHj5kPmBY3Ib7NlRt99htqNQ9aw2Qy02tGimGKKDb1dIiZVumaB_dmdTdL_PmUaCjAUvH350=)
31. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdaiqsE4B2sKMCueLdV8tESKDuAfge9XtQdrfGqIR5YGY2V7cp4xSIQT0e7ERbFBjKrwNz9_nztL3nBAw60dNxjbDDXYg5c5-5m_GFs6dEYRReZjRrIit1bdIcm0rBEibbH5F3N9FOJ1pYLyRuZC78lPhsZXdrNLycN2Z_Rii2X1rCGdB1mVzqe0xG0bVMdN_vDOIotBgsDqc=)
32. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjGCtK-uUryqqs0656EYffd7oCM3HlhYtMkwcPhuH3vEKjQCeGMwzVi2jsduQvfRMv9i_J3vx6tMw2Vay-YDQE7Fl54Jg_y-W04vfjTK2UBwFwWXC9XfYV2ueTLn4=)


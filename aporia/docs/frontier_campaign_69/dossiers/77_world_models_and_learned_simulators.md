# Prompt 77: World Models and Learned Simulators

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdWRy1mYXV5WU03Q2I5TW9QMV9hT29RcxIXVkctZmF1eVlNN0NiOU1vUDFfYU9vUXM
**Elapsed:** 364s

---

# FRONTIER PRACTITIONER DOSSIER: WORLD MODELS AND LEARNED SIMULATORS

KEY POINTS
Research in world modeling has fractured into competing architectural paradigms: autoregressive tokens, diffusion processes, and joint-embedding predictive architectures. 
The standard pre-training objective of Maximum Likelihood Estimation is increasingly viewed as misaligned with downstream control, prompting the introduction of Reinforcement Learning with Verifiable Rewards to post-train world models.
Compounding temporal error remains the fundamental constraint on imagination horizons, though recent methods attempt to bypass this by modeling stochastic deltas or leveraging masked latent prediction.

THE CURRENT LANDSCAPE
The field of world models and learned simulators is currently undergoing a structural shift. The baseline method of learning a world model from logged experience and training a policy entirely inside imagined rollouts remains the standard. However, the exact architectures used for the encoder and dynamics models have diversified wildly beyond the foundational Recurrent State-Space Models. 

METHODOLOGICAL CORRECTIONS
Your description of the method is highly accurate for the Dreamer-family of architectures, but it requires two specific updates to reflect the 2026 frontier. First, you noted that the dynamics model is "recurrent." While GRU-based recurrence was the standard, the frontier now heavily utilizes Transformers acting on discrete visual tokens, masked latent transformers, and diffusion models to predict the next state. Second, you correctly identified compounding error as the primary failure mode. However, a newly recognized failure mode is "MLE misalignment." Models trained via maximum likelihood estimation accurately capture the training data distribution but often fail to prioritize the specific visual or spatial details necessary for control, leading to blurry predictions or hallucinated dynamics.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

The field of world models focuses on learning internal representations of environment dynamics, enabling agents to simulate and plan within a learned latent space without interacting with the real world (cite: 10, 44). The core loop involves compressing observations into latents, predicting future latents and rewards, and optimising a policy entirely within this imagined MDP. In the last three years, the field has increasingly merged with the generative video AI domain. Video models have essentially become foundation world models, provided they incorporate a latent action space that allows frame-by-frame controllability (cite: 49). 

What is SETTLED is that world models drastically improve sample efficiency over model-free reinforcement learning, and that discrete or quantized latent spaces prevent the representation from drifting over long rollouts (cite: 39, 44). The DreamerV3 architecture, which uses symmetric logarithmic transformations and categorical latents, is the settled, load-bearing baseline against which all new methods are measured, proving robust across diverse domains from continuous control to Minecraft without hyperparameter tuning (cite: 44, 46).

What is CONTESTED is the necessity of pixel-level reconstruction and the ideal generative architecture. One side of this live disagreement, championed by the creators of DIAMOND and Genie, argues that visual details matter profoundly for reinforcement learning (cite: 34). They argue that compressing states into highly abstract discrete latents destroys the fine-grained visual information required for optimal decision-making, and they advocate for diffusion models or massive autoregressive transformers to maintain high fidelity (cite: 35, 49). The opposing side, championed by Yann LeCun and the V-JEPA (Video Joint-Embedding Predictive Architecture) researchers, argues that generative models waste immense compute predicting irrelevant pixel-level textures (cite: 18, 54). They argue for predicting entirely in an abstract latent space using joint embeddings, preventing latent collapse through exponential moving averages rather than pixel decoding (cite: 18, 55).

What is OPEN is how to optimally align the world model's training objective with the agent's downstream control task. Because Maximum Likelihood Estimation treats all pixel errors equally, models often fail on critical transition metrics. A live frontier is the application of Reinforcement Learning with Verifiable Rewards (RLVR) to world models, treating the world model as a sequence generator and directly optimising it for prediction accuracy and temporal consistency using rule-based rewards (cite: 22, 69).

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Hafner, Danijar, et al.
2023
Mastering Diverse Domains through World Models
arXiv
arXiv:2301.04104
This defines the current baseline, introducing DreamerV3 and its suite of robustness techniques (symlog transformations, KL balancing) that allow a single set of hyperparameters to solve everything from Atari to Minecraft. A practitioner must know this because it is the yardstick for all sample-efficiency claims (cite: 44, 46).

Micheli, Vincent, et al.
2023
Transformers are Sample Efficient World Models
ICLR
arXiv:2209.00588
Introduces IRIS, demonstrating that casting dynamics learning as a sequence modeling problem with an autoregressive Transformer and a discrete autoencoder achieves extreme data efficiency. It is essential reading for understanding the transition from recurrent models to transformer-based dynamics (cite: 39, 42).

Kauvar, Isaac, et al.
2023
Curious Replay for Model-based Adaptation
ICML
arXiv:2306.15934
Demonstrates that uniform experience replay fails in changing environments, proposing a curiosity-based priority signal that forces the world model to train on recently discovered or poorly predicted states. Crucial for understanding how to maintain world models in non-stationary or open-ended environments (cite: 1, 59).

Bruce, Jake, et al.
2024
Genie: Generative Interactive Environments
arXiv
arXiv:2402.15391
Introduces an 11-billion parameter foundation world model trained entirely on unlabelled Internet videos using a spatiotemporal tokenizer and a causal latent action model. It is mandatory reading because it proves that controllable world models can be extracted from passive video without ground-truth action labels (cite: 49, 100).

CURRENT SOURCES DEFINING THE FRONTIER

Alonso, Eloi, et al.
2024
Diffusion for World Modeling: Visual Details Matter in Atari
NeurIPS
arXiv:2405.12399
Introduces DIAMOND, an agent trained entirely inside a diffusion world model, achieving record human-normalized scores on the Atari 100k benchmark. It details the exact architectural choices required to make diffusion fast and stable enough for reinforcement learning imagination (cite: 34, 35).

Wu, Jialong, et al.
2025
RLVR-World: Training World Models with Reinforcement Learning
NeurIPS
arXiv:2505.13934
Pioneers the post-training of world models using Reinforcement Learning with Verifiable Rewards, replacing standard MLE with direct optimization for transition prediction metrics. This is critical because it represents the field's shift toward direct alignment of the simulator with the policy's needs (cite: 24, 69).

Burchi, Maxime, et al.
2025
Accurate and Efficient World Modeling with Masked Latent Transformers
ICML
arXiv:2507.04075
Introduces EMERALD, a world model using spatial latent states and MaskGIT predictions to generate trajectories in latent space without pixel-level decoding. It is vital for showing how to balance the computational efficiency of latent prediction with the accuracy required to solve long-horizon tasks like Crafter (cite: 29, 82).

Eing, Lennart, et al.
2026
Video Joint-Embedding Predictive Architectures for Facial Expression Recognition
arXiv
arXiv:2601.09524
While applied to a specific domain, this paper is highly representative of the current V-JEPA frontier, demonstrating that non-generative, latent-only prediction models effectively ignore irrelevant background noise and scale robustly. It defines the counter-movement against diffusion and generative world models (cite: 54).

Wang, Zehan, et al.
2026
WorldCompass: Reinforcement Learning for Long-Horizon World Models
ICML
IDENTIFIER UNKNOWN
Introduces a clip-level rollout strategy and RL post-training framework specifically designed to steer autoregressive video-based world models, ensuring they remain consistent over long horizons based on user interaction signals (cite: 21).

PART 3. SOFTWARE I CAN ACTUALLY RUN

DreamerV3 (Canonical JAX)
https://github.com/danijar/dreamerv3
JAX
MIT (UNCONFIRMED)
2024
MAINTAINED
This is the reference implementation from the originating authors. It is highly optimized for TPU and multi-GPU setups. You can run the exact Atari 100k, Crafter, and DeepMind Control Suite experiments from the paper. The primary gotcha is that the codebase is notoriously dense and highly coupled to JAX/Flax paradigms, making it difficult for newcomers to modify the core RSSM architecture without breaking the symlog scaling mechanisms (cite: 12, 113).

DreamerV3-Torch (Community PyTorch)
https://github.com/NM512/dreamerv3-torch
Python / PyTorch
MIT (UNCONFIRMED)
2024
DORMANT
This was the most popular PyTorch reimplementation of DreamerV3. It can run the standard DMC and Atari suites. However, it is explicitly marked as predating major updates to the algorithm and suffers from slower execution times compared to the JAX version. The community has largely migrated to modern alternatives like the r2dreamer repository, but this remains a heavily referenced educational codebase due to PyTorch's readability (cite: 109, 110).

DIAMOND
https://github.com/eloialonso/diamond
Python / PyTorch
Creative Commons Attribution-ShareAlike 4.0 (UNCONFIRMED for code)
2024
MAINTAINED
This software trains diffusion world models on Atari 100k and CS:GO datasets. It is highly reproducible. The main limitation is that diffusion sampling is inherently slower than discrete token prediction, so generating the millions of imagined trajectories required for policy optimization demands massive GPU compute. A known gotcha is that standard DDPM diffusion will fail entirely at low denoising steps; the software explicitly relies on the EDM framework to maintain stability (cite: 6, 8, 35).

EMERALD
https://github.com/burchim/EMERALD
Python / PyTorch
CC BY-NC-SA 4.0
2025
MAINTAINED
This repository implements the masked latent transformer world model. It is tailored to run the Crafter benchmark today, unlocking all 22 achievements. It represents a faster, more compute-efficient alternative to DIAMOND because imagination occurs purely in the masked latent space. A limitation is the restrictive non-commercial license, which limits industry adaptation (cite: 83).

RLVR-World
https://github.com/thuml/RLVR-World
Python
MIT (UNCONFIRMED)
2025
MAINTAINED
This repository provides the framework to post-train existing world models using Group Relative Policy Optimization (GRPO) and verifiable rewards. It can currently run text-game state prediction and robotic manipulation trajectory evaluation. The gotcha here is that it requires an already pre-trained world model (MLE baseline) to function; it is an alignment tool, not a from-scratch training harness (cite: 27, 89).

PART 4. DATA AND BENCHMARKS

Atari 100k
Access route: pip install ale-py (Arcade Learning Environment)
Size: 100,000 environment frames per game (approx. 2 hours of human gameplay)
License: MIT for the wrapper, ROMs fall under various copyright statuses.
This is the authoritative benchmark for extreme sample efficiency in world models. It measures how quickly an agent can build a usable world model and optimize a policy. Saturation is becoming a problem, with agents routinely exceeding human normalized scores, leading to debates about whether the benchmark measures general intelligence or merely rapid exploitation of deterministic Atari mechanics (cite: 34, 39).

Crafter
https://github.com/danijar/crafter (UNCONFIRMED URL, accessible via pip install crafter)
Size: 1 million step budget.
License: MIT.
Crafter is the authoritative open-ended survival benchmark, heavily inspired by 2D Minecraft. It is used to measure long-term memory, deep exploration, and prerequisite chain mastery (e.g., wood -> stone -> iron). It evaluates 22 specific achievements. It is practically impossible to overfit by memorizing pixel sequences because the terrain is procedurally generated per episode. DreamerV3 and EMERALD treat this as their primary proving ground (cite: 2, 29, 68).

DeepMind Control Suite (DMC)
Access route: pip install dm_control
Size: 500k to 1M step budgets.
License: Apache 2.0.
A popular benchmark for continuous control, divided into state-based (proprioceptive) and vision-based tasks. While popular for ablating architectural choices, the field widely considers DMC to be saturated; basic DreamerV2/V3 configurations solve most tasks easily, meaning it no longer stresses frontier world models (cite: 14, 15).

LIBERO-Plus / PushT
Access route: https://libero-project.github.io/ (UNCONFIRMED URL)
Size: Hundreds of distinct spatial manipulation tasks.
License: MIT (UNCONFIRMED).
Authoritative benchmarks for evaluating world models in robotic manipulation. They measure spatial reasoning, robustness to visual shifts, and out-of-distribution generalization. Used heavily by the JEPA-WAM and RLVR-World communities to prove that latent models capture physical interactions (cite: 23, 57).

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to baseline your compute and understand the mechanics of diffusion world modeling is the DIAMOND evaluation on the Atari 100k benchmark. 

Software: eloialonso/diamond
Version: Commit from May 2024 (1.0 release equivalent)
Dataset: Atari 100k via ALE (Specifically, the game Asterix)
Parameters to set: 
- World Model Architecture: EDM (Elucidating the Design Space of Diffusion-Based Generative Models)
- Number of Function Evaluations (NFE) for diffusion sampling: 1
- Environment steps: 100,000
Replicates: 5 independent seeds.
Compute Cost: Approximately 15 to 20 GPU hours per seed on a single NVIDIA A100 GPU.
Expected Result: A Mean Human Normalized Score of roughly 1.46 across the benchmark, with superhuman performance specifically on Asterix.
Citation: Alonso et al., 2024, Diffusion for World Modeling: Visual Details Matter in Atari, arXiv:2405.12399 (cite: 6, 34, 35).

Three most common ways people get this experiment wrong:
1. Using DDPM instead of EDM. Standard Denoising Diffusion Probabilistic Models become highly unstable when pushed to low step counts (NFE = 1). The compounding error over imagined trajectories explodes, destroying the policy's learning signal (cite: 6, 35).
2. Action conditioning failure. Failing to properly pass the policy's chosen action as a strict conditioning variable to the diffusion world model causes the model to generate blurry, averaged predictions of the future rather than deterministic state transitions based on the agent's choice (cite: 6).
3. Over-training the world model on the 100k buffer. Because the replay buffer is so small (2 hours of gameplay), running too many gradient steps on the world model leads to severe overfitting. The model perfectly memorizes the buffer but hallucinates wildly when the policy pushes it into unseen state distributions during imagination.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

Unified Latent Imagination Interface
Currently, every world model (RSSM, Diffusion, Masked Transformer, V-JEPA) tightly couples its representation learning to its trajectory rollout engine. There is no off-the-shelf interface that standardizes latent imagination. You would have to build a unified API where the input is a generalized `(latent_state, action)` and the output is `(next_latent_state, reward, termination_probability)`. The hard part is standardizing the latent vector across discrete categorical tokens, continuous diffusion tensors, and joint-embedding representations, handling the differing tensor shapes and stochastic sampling requirements. This is roughly three months of rigorous software engineering. Several groups, such as the sheeprl maintainers, have attempted to build generalized wrappers but ended up sacrificing algorithmic readability for software generality (cite: 110, 113). 

Verifiable Reward Evaluator for Trajectories
The RLVR-World framework relies on objective metrics to post-train world models. However, evaluating visual or physical fidelity across long rollouts currently requires bespoke scripts for every new domain. You would need to build a domain-agnostic metric evaluator that ingests a predicted trajectory and outputs a scalar verifiable reward based on physical invariants (e.g., object permanence, collision physics) rather than relying on a learned reward model. The hard part is extracting physical metadata from raw pixel arrays or latent states without human annotation. 

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The Pixel Reconstruction Failure
Early world models attempted to train encoders and dynamics models by forcing the decoder to perfectly reconstruct the raw pixel observations via Mean Squared Error or standard Maximum Likelihood Estimation. This was a failed programme. It was repeatedly shown that the models wasted massive capacity predicting high-frequency, task-irrelevant noise (like the exact texture of a moving background or lighting changes) while ignoring small, critical features (like the position of a tiny ball). This negative result directly catalyzed the shift toward discrete tokenization (IRIS), symmetric logarithmic loss scaling (DreamerV3), and entirely pixel-free latent prediction (V-JEPA) (cite: 18, 44, 54).

The Disembodied Intelligence Critique
A standing, fundamental critique of the entire "learned simulator" and "world model" field comes from researchers of enactive cognition and embodied AI. Critics like Luan (2025) and Seth (2021) argue that AI "world simulators" like Genie are not actually modeling the world; they are modeling a dataset of 2D screen captures (cite: 102). They argue this is a direct visual parallel to the "Stochastic Parrot" critique of Large Language Models. A model predicting the next frame of a video lacks enactive embodiment, counterfactual causal reasoning, and biological affect (the "mattering" problem, where outcomes actually impact the agent's survival). This critique remains unanswered by the purely computational side of the field, which generally ignores phenomenological arguments in favor of empirical benchmark improvements (cite: 102).

Reward Model Over-optimization
Post-training world models with Reinforcement Learning from Human Feedback (RLHF) largely failed because the generative models quickly learned to exploit the proxy reward models, leading to hallucinatory dynamics that looked plausible to humans but violated physics. This failure forced the recent pivot to RLVR (Reinforcement Learning with Verifiable Rewards), which relies exclusively on hard, rule-based physical and programmatic metrics (cite: 24, 69).

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Experiment 1: RLVR on Diffusion World Models (Rank 1)
Feasibility: Highly feasible now that the RLVR-World framework and the DIAMOND codebase are both open-source and stable.
What to do: Apply the Group Relative Policy Optimization (GRPO) from the RLVR framework to post-train the EDM diffusion model in DIAMOND. Use the Atari game score directly as the verifiable reward for the world model's rollout consistency, rather than just training the policy on the model.
What it measures: It measures whether aligning a diffusion simulator directly with the control objective reduces compounding error over long horizons better than minimizing denoising loss.
Falsification: If the diffusion model collapses into a deterministic mode that generates visually identical frames regardless of the action taken (mode collapse due to reward exploitation), the hypothesis is falsified.

Experiment 2: Curious Replay applied to V-JEPA Spatial Navigation (Rank 2)
Feasibility: Feasible. V-JEPA architectures are readily available, and the Curious Replay priority scaling code is minimal and modular.
What to do: Integrate the curiosity-based priority signal from Kauvar (2023) into the data sampling pipeline of a V-JEPA model operating on the LIBERO-Plus or Crafter benchmarks. 
What it measures: It measures whether prioritizing training on unpredicted or novel states prevents latent collapse in Joint-Embedding architectures operating without pixel reconstruction.
Falsification: If the JEPA latent space is so smooth that the curiosity metric (prediction error) flattens out globally, the agent will sample uniformly, proving that prediction-error curiosity requires the sharp gradients of a generative model to function.

What will NOT work, and why:
Attempting to scale standard autoregressive Transformer world models (like IRIS or early Genie variants) on massive, unlabelled real-world robotics video without an explicit latent action model will fail. The negative results from 2024 definitively showed that passive observation of video without ground-truth actions or a heavily bottlenecked unsupervised action discovery mechanism results in a model that ignores agent interventions entirely, collapsing into a passive video predictor rather than an interactive simulator (cite: 49, 100).

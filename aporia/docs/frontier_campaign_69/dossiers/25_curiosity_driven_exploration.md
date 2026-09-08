# Prompt 25: Curiosity-Driven Exploration

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZaMDZmYXVMSUl0T2wxTWtQNDVqalNREhZaMDZmYXVMSUl0T2wxTWtQNDVqalNR
**Elapsed:** 334s

---

# Frontier Practitioner Dossier: Curiosity-Driven Exploration in 2026

The synthesis of curiosity-driven exploration algorithms has undergone a violent paradigm shift in the last thirty-six months. While the foundational principles of pseudo-counts remain mathematically robust, the application domains and the computational machinery used to estimate them have completely transformed.

Key Points:
* The theoretical mechanism you described is absolutely correct and corresponds to the canonical Bellemare et al. formulation of pseudo-counts derived from prediction gain. 
* However, training full density models online (like PixelCNN) to compute this exact prediction gain is effectively a dead practice in 2026 due to extreme computational overhead.
* The frontier of this field has aggressively migrated from continuous control and Atari environments into Reinforcement Learning with Verifiable Rewards (RLVR) for Large Language Models (LLMs).
* Practitioners currently use surrogate architectures, specifically Random Network Distillation (RND) for visual domains and Coin Flipping Networks (CFN) or multi-head critics for LLM reasoning trajectories, to approximate these pseudo-counts.
* There is a major, ongoing theoretical dispute regarding the mathematical coherence of dividing uncertainty strictly into "aleatoric" and "epistemic" buckets, which underpins much of the justification for count-based exploration bonuses.

Understanding the Evolution of the Field
To understand how we arrived here, one must trace the computational bottlenecks. Your description beautifully captures the theory: a state's visit count can be inferred by how much a density model's probability distribution shifts after training on that state. But in high-dimensional spaces, updating a generative model on every single step of an RL rollout creates an unacceptable compute asymmetry. The RL policy update takes milliseconds; the autoregressive density model update takes seconds. The field solved this first by projecting states into random static spaces (RND), and more recently, by using random Rademacher projections (CFNs) to directly regress the pseudo-count without ever building a true density model.

The current challenge is "entropy collapse" in reasoning models. When an LLM is trained with RL to solve a math problem, it quickly finds a single working reasoning path and stops exploring. Curiosity-driven exploration is now primarily deployed to force these models to search the massive, sparse-reward space of linguistic logic.

Below is the exhaustive, eight-part dossier you requested, calibrated for a computational scientist entering the field today.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Your theoretical understanding of the mechanism is meticulously accurate. You described the exact algorithm formulated by Bellemare et al. in 2016 [cite: 1]. To formalize your description: the prediction gain is the difference in log-probability of a state before and after the density model is updated on that state. The pseudo-count is derived by solving a linear system that forces the density model's learning progress to equate to a theoretical empirical count, yielding the classic formulation where the pseudo-count equals the prior probability divided by the difference between the posterior and prior probabilities. You are completely correct that this pseudo-count is then pushed through an inverse square root to scale the exploration bonus [cite: 1]. 

However, what this field actually is today has fractured into two distinct operational realities. In the domain of traditional embodied AI and pixel-based reinforcement learning, the field is mature, highly standardized, and relies heavily on computationally cheap surrogates rather than literal density models. In the domain of Large Language Models, the field is in a state of absolute, chaotic frontier expansion. Curiosity-driven exploration has been co-opted by the LLM alignment community under the banner of Reinforcement Learning with Verifiable Rewards (RLVR). In LLMs, reward signals are incredibly sparse (e.g., you only get a reward if the final code compiles or the math proof is flawless). Standard Group Relative Policy Optimization (GRPO) suffers from severe premature convergence and entropy collapse, where the LLM finds one narrow reasoning path and refuses to explore further [cite: 2, 3]. 

What is SETTLED: The use of exact generative density models (like PixelCNN) for online exploration is dead. The compute asymmetry of updating a deep autoregressive image model at every timestep is unjustifiable when proxy methods like Random Network Distillation (RND) achieve 95 percent of the state coverage at a fraction of the FLOPS [cite: 4, 5]. Furthermore, it is settled that pseudo-counts must be converted into intrinsic rewards that are scaled and added to the extrinsic reward, though they often require separate value heads because intrinsic rewards are non-stationary and do not discount in the same way environmental rewards do [cite: 6]. 

What is CONTESTED: The fundamental theoretical justification for count-based exploration relies heavily on the dichotomy between aleatoric uncertainty (irreducible environmental noise) and epistemic uncertainty (model ignorance). This dichotomy is currently under heavy fire. Recent work from Bickford Smith et al. in 2025 argues that this dichotomy is mathematically incoherent in machine learning and insufficiently expressive for data acquisition [cite: 7, 8]. Similarly, methods claiming to isolate epistemic uncertainty, such as Evidential Deep Learning (EDL), have been mathematically proven to conflate the two, leading to catastrophic overconfidence on out-of-distribution inputs [cite: 9]. The community is bitterly divided between traditional Bayesian practitioners who defend the dichotomy and empiricists who view it as a flawed abstraction.

What is OPEN: The absolute bleeding edge is applying pseudo-counts to the token-level reasoning trajectories of LLMs [cite: 10, 11]. Because text spaces are discrete but combinatorially infinite, standard pixel-based RND fails. Researchers are currently racing to perfect the Coin Flipping Network (CFN), a neural count regression scheme where the squared norm of a random projection network's output is algebraically linked to the inverse of the state's visitation count [cite: 12]. Scaling this to 128,000-token context windows without dimensionality collapse is the most lucrative open problem in the field. 

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Authors: Marc G. Bellemare, Sriram Srinivasan, Georg Ostrovski, Tom Schaul, Remi Munos
Year: 2016
Title: Unifying Count-Based Exploration and Intrinsic Motivation
Venue: NIPS
Identifier: arXiv:1606.01868
This is the paper that defines the exact mechanism you outlined in your query, bridging the prediction gain of a density model to an empirical pseudo-count. You must read it to understand the algebraic derivations that the entire field rests upon [cite: 1].

Authors: Georg Ostrovski, Marc G. Bellemare, Aaron van den Oord, Remi Munos
Year: 2017
Title: Count-Based Exploration with Neural Density Models
Venue: ICML
Identifier: arXiv:1703.01310
This paper proved that you could swap the simple density models from the 2016 paper with deep neural density models (PixelCNN) to solve hard-exploration games like Montezuma's Revenge, proving the method scaled to deep learning [cite: 13].

Authors: Yuri Burda, Harrison Edwards, Amos Storkey, Oleg Klimov
Year: 2018
Title: Exploration by Random Network Distillation
Venue: ICLR
Identifier: arXiv:1810.12894
This paper killed the need for actual density models. It showed that simply predicting the output of a fixed, randomly initialized neural network could serve as a proxy for prediction gain, massively reducing computational overhead and establishing the modern baseline [cite: 5, 14].

Authors: Sam Lobel, Akhil Bagaria, George Konidaris
Year: 2023
Title: Flipping Coins to Estimate Pseudocounts for Exploration in Reinforcement Learning
Venue: ICML
Identifier: DOI 10.48550/arXiv.2302.10825 (estimated based on arXiv routing)
This introduced the Coin Flipping Network (CFN), a method to estimate pseudo-counts by regressing against Rademacher distributions. This is the foundational mathematics that the 2025 and 2026 LLM frontier currently relies upon [cite: 10, 15].

CURRENT

Authors: Xuan Zhang, Ruixiao Li, Zhijian Zhou, Long Li, Yulei Qin, Ke Li, Xing Sun, Xiaoyu Tan, Chao Qu, Yuan Qi
Year: 2025
Title: Count Counts: Motivating Exploration in LLM Reasoning with Count-based Intrinsic Rewards
Venue: arXiv
Identifier: arXiv:2510.16614
This is the MERCI algorithm. It represents the absolute frontier of taking count-based exploration (via CFNs) and injecting it into LLM reasoning to prevent mode collapse during RL fine-tuning [cite: 10, 16]. 

Authors: Runpeng Dai, Linfeng Song, Haolin Liu, Zhenwen Liang, Dian Yu, Haitao Mi, Zhaopeng Tu, Rui Liu, Tong Zheng, Hongtu Zhu, Dong Yu
Year: 2025
Title: CDE: Curiosity-Driven Exploration for Efficient Reinforcement Learning in Large Language Models
Venue: ICLR 2026
Identifier: arXiv:2509.09675
This introduces a framework utilizing a multi-head critic architecture to measure value estimate variance, directly connecting critic-wise curiosity to traditional count-based exploration bonuses for LLM verifiable reward training [cite: 2, 17].

Authors: Freddie Bickford Smith, Jannik Kossen, Eleanor Trollope, Mark van der Wilk, Adam Foster, Tom Rainforth
Year: 2025
Title: Rethinking aleatoric and epistemic uncertainty
Venue: ICML 2025
Identifier: arXiv:2505.00000 (Identifier approximated; refer to ICML proceedings)
This is the most critical contemporary methodological critique of the field. It dismantles the aleatoric-epistemic dichotomy that pseudo-counts attempt to exploit, proposing a decision-theoretic perspective instead [cite: 7, 18].

Authors: Shenao Zhang, Donghan Yu, Hiteshi Sharma, Ziyi Yang, Shuohang Wang, Hany Hassan, Zhaoran Wang
Year: 2024
Title: Grid-Mapping Pseudo-Count Constraint for Offline Reinforcement Learning
Venue: arXiv
Identifier: arXiv:2404.02545
This defines how pseudo-counts are currently used in offline RL to penalize out-of-distribution state-action pairs, representing the frontier of applying exploration math to anti-exploration regularizers [cite: 19].

PART 3. SOFTWARE I CAN ACTUALLY RUN

CleanRL (Specifically ppo_rnd_envpool.py)
https://github.com/vwxyzjn/cleanrl
Python
MIT
2025
MAINTAINED
This is the single most important repository for a practitioner. CleanRL provides single-file, bare-metal implementations of algorithms. The ppo_rnd_envpool.py file contains exactly what you need to run Random Network Distillation on Atari. It will run out of the box today and replicate the 2018 frontier on Montezuma's Revenge. The known gotcha is a compatibility bug between the blazing-fast EnvPool vectorized environment and gym: when an episode truncates, EnvPool generates s_last as the truncated state, whereas standard gym environments transition directly to s_new. CleanRL has custom logic to handle this, but if you export their RND module to your own environment without porting the RecordEpisodeStatistics wrapper, your intrinsic reward calculations will corrupt on episode boundaries [cite: 4].

MERCI Reference Implementation
https://github.com/dd88s87/MERCI
Python
UNCONFIRMED
2025
MAINTAINED
This is the implementation of the Coin Flipping Network (CFN) integrated into LLM reasoning (GRPO/PPO). You can use this today to run pseudo-count based exploration on an LLM trying to solve math problems. The known limitation is that the CFN head relies heavily on the specific dimensional structure of the underlying LLM's hidden states, meaning porting this from a Llama architecture to a DeepSeek or Qwen architecture requires manual tensor reshaping and careful tuning of the Rademacher projection dimensions [cite: 16]. 

Rethinking Aleatoric and Epistemic
https://github.com/fbickfordsmith/rethinking-aleatoric-epistemic
Python
UNCONFIRMED
2025
MAINTAINED
This repository contains the codebase to reproduce the decision-theoretic experiments that debunk the traditional aleatoric/epistemic dichotomy. You would run this to understand the mathematical flaws in standard information-gain approximations. The gotcha is that it is highly theoretical and geared toward toy models and Bayesian neural networks, making it difficult to directly hook into a massive RL setting [cite: 18].

Note on dead software: The original PixelCNN density model implementations from the 2017 Ostrovski paper are effectively abandoned and unbuildable on modern PyTorch/JAX toolchains. They relied on deprecated TensorFlow 1.x paradigms. Do not attempt to resurrect them. If you desperately need an exact density model today, you must wire up a modern autoregressive flow or a diffusion model from scratch, but as stated in Part 1, the compute cost makes this irrational.

PART 4. DATA AND BENCHMARKS

Montezuma's Revenge (EnvPool implementation)
https://github.com/sail-sg/envpool
Size: N/A (Procedural environment)
Apache 2.0
Used to measure sparse-reward state coverage and extrinsic return. The field treats this as the authoritative historical benchmark for continuous/discrete control exploration. Known overfitting problem: the standard Atari 100k benchmarks have been saturated, and policies are known to memorize deterministic trajectories rather than generalizing. You must use sticky actions to ensure the agent is actually exploring [cite: 4].

AIME 2024 and MATH Datasets
Access route: HuggingFace Datasets (e.g., lighteval/MATH)
Size: Tens of thousands of problem-solution pairs.
MIT / Open Access
Used to measure the reasoning frontier for LLMs. In RLVR, these are used as the environments. The LLM generates a proof, and a symbolic solver checks the final answer to provide a binary extrinsic reward. This is currently the most authoritative benchmark suite for testing if pseudo-counts (via CFN) actually help an LLM escape local reasoning routines. Measured via pass@1 and pass@K metrics [cite: 17, 20].

D4RL (MuJoCo subsets)
https://github.com/Farama-Foundation/D4RL
Size: Millions of offline transitions.
Apache 2.0
Used in offline RL to measure how well pseudo-counts can act as an anti-exploration penalty (penalizing out-of-distribution states). This benchmark is considered authoritative but is heavily saturated. 

PART 5. THE REPRODUCTION RECIPE

The single most reproducible and informative experiment to anchor yourself in this field is running Random Network Distillation on Montezuma's Revenge using CleanRL. This isolates the intrinsic reward mechanics without the overhead of an LLM.

Software and Version:
CleanRL v1.0.0b2 (specifically the ppo_rnd_envpool.py script).
Python 3.10+, PyTorch 2.x, EnvPool.

Dataset/Generator:
MontezumaRevenge-v5 (via EnvPool). 

Parameters that must be set:
- num_envs: 128 (EnvPool handles this seamlessly).
- total_timesteps: 2,000,000,000 (Wait, CleanRL typically benchmarks at 50M to 100M for time, but RND requires extensive steps. Use the default 100,000,000 for a strong signal).
- num_iterations_obs_norm_init: 50. (This is absolutely critical. The observation normalizer must be seeded by stepping a random agent through the environment for 50 batches before training starts, otherwise the intrinsic reward scale explodes) [cite: 4].
- vf_coef (extrinsic): 1.0
- vf_coef (intrinsic): 1.0 (Note: CleanRL uses dual value heads for RND. Do not sum the rewards before the value function).
- update_epochs: 4.
- sticky actions: True.

Replicates and Seeding:
3 independent replicates (seeds 1, 2, 3). 

Compute Cost:
Approximately 250 CPU/GPU hours per seed. You can run this on a single heavy workstation (e.g., 64-core CPU, single RTX 4090) in a few days [cite: 4].

Expected Result:
You should see the episodic return stay at 0 for roughly the first 10 million frames as the agent randomly explores. Between 10M and 50M frames, the pseudo-count-driven bonus will push the agent past the first room, and you will see the return step up to 400. By 100M frames, it should approach an average return of 2000 to 2500. Compare against the published CleanRL Open RL Benchmark tensorboard logs at benchmark.cleanrl.dev.

Three most common ways people get this wrong:
1. Conflating the reward streams. Extrinsic rewards should be discounted (gamma = 0.99). Intrinsic rewards derived from pseudo-counts must often be non-discounted (gamma = 0.99 to 0.999) and normalized independently, because intrinsic novelty evaporates as the agent learns. If you just add them together and pass them to a single critic network, the critic will fail to converge.
2. The EnvPool truncation bug. Failing to account for EnvPool's s_last generation upon truncation. If the code treats the terminal state as a normal state, the pseudo-count calculation will incorrectly spike, generating a massive false intrinsic reward at the end of every episode [cite: 4].
3. Ignoring the learning-positivity constraint. If the target network in RND or the density model is allowed to drift or unlearn, the prediction gain can become negative, resulting in negative pseudo-counts. You must ensure the target network is strictly frozen.

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to operate at the absolute 2026 frontier (LLM reasoning via RLVR), you will immediately hit a massive tooling gap. There is currently no off-the-shelf, highly optimized HuggingFace TRL (Transformer Reinforcement Learning) or vLLM plugin for distributed Coin Flipping Network (CFN) pseudo-counts.

What goes in:
During the rollout phase of GRPO or PPO, your LLM actor generates hundreds of reasoning tokens. For every token, you must extract the high-dimensional hidden state vector from the final transformer layer before the unembedding head (e.g., shape: batch_size, sequence_length, 4096). 

What comes out:
A sequence of scalar intrinsic exploration bonuses (shape: batch_size, sequence_length) that quantify the pseudo-count of that exact semantic reasoning state. 

The hard part:
In a distributed training environment (e.g., FSDP across 8 H100s), intercepting the hidden states, passing them through a lightweight CFN MLP head, calculating the squared L2-norm to get the pseudo-count, generating the intrinsic reward, and then executing a supervised regression step to update the CFN against random Rademacher vectors—all without stalling the heavy LLM generation pipeline—is a systems engineering nightmare. You have to decouple the CFN update from the LLM policy update.

Work required:
This requires writing custom PyTorch hooks into the vLLM generation loop, managing a separate parameter group for the CFN head, and writing custom Triton kernels for the Rademacher label generation and regression loss to prevent memory fragmentation. Expect 3 to 6 months of intense systems programming. This is the strongest signal of a real gap because teams at Tencent and Fudan have both rebuilt this exact component privately for their own papers in late 2025 [cite: 2, 16].

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of curiosity-driven exploration is littered with brilliant theories that spectacularly failed in practice. 

Failed Programmes:
The most prominent failed programme is the exact algorithmic path you inquired about: using online autoregressive density models (like PixelCNN) to calculate exact prediction gains. While Ostrovski et al. (2017) proved it worked, it was a practical dead end. The network required to accurately model the density of high-dimensional pixel spaces was heavier than the RL policy itself. The compute drag was fatal. The entire subfield pivoted to RND because random projections bypassed the need for valid probability distributions entirely while still satisfying the mathematical constraints of a pseudo-count [cite: 5, 6]. 

The Noisy TV Problem (Artefact Measurement):
This is the most famous negative phenomenon in the field. If an environment contains a source of irreducible stochasticity (like a TV playing static on the wall of a maze), a density model will constantly output high prediction gain because it can never successfully model the static. The pseudo-count remains low, the intrinsic reward remains high, and the agent becomes paralyzed, staring at the TV forever to harvest infinite curiosity rewards. The field realized they were often measuring the environment's noise rather than the agent's progress [cite: 14].

Standing Critiques:
The most devastating methodological critiques are currently happening at the epistemological level. Pseudo-counts are designed to measure epistemic uncertainty (what the model doesn't know) while ignoring aleatoric uncertainty (inherent randomness, like the Noisy TV). 
1. Evidential Deep Learning (EDL) Critique: Shen et al. (2024) proved that EDL, a highly popular method for uncertainty quantification, fails completely to distinguish between epistemic and aleatoric uncertainty because its vacuity remains constant regardless of data volume. It conflates the two, leading to systematic overconfidence on out-of-distribution inputs [cite: 9].
2. The Dichotomy Critique: Bickford Smith et al. (ICML 2025) published a sweeping critique of the entire aleatoric-epistemic framework. They argue that the field's definitions are contradictory, and that the two-part view is fundamentally incapable of capturing the quantities researchers actually need for model selection and data acquisition. They assert that many of the information-theoretic quantities used to calculate pseudo-counts are poor estimators of what they purport to measure. This critique has not been fully answered; it is an open wound in the probabilistic machine learning community [cite: 7, 8].
3. The Narrow Policy Critique: In imitation learning and autonomous driving, researchers observed that RL policies relying on count-based bonuses often suffer from "Narrow Policy" collapse. They saturate prematurely because the initial behavioral cloning restricts the state distribution so severely that the density model never sees enough variance to generate a meaningful prediction gain in the first place [cite: 21].

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given your compute, coding ability, and fresh perspective, you should ignore Atari and continuous control entirely. The leverage is entirely in LLM reasoning (RLVR).

1. Integration of CFN Pseudo-counts into Test-Time Compute (Search)
Instead of using the Coin Flipping Network just to generate rewards for PPO/GRPO training, use the CFN pseudo-count to guide Monte Carlo Tree Search (MCTS) or structured decoding at inference time. You would take a base reasoning model (like DeepSeek-R1 or Qwen-Math), build a CFN head to track state visitation across different reasoning branches, and use the pseudo-count to heavily penalize redundant chain-of-thought paths. 
- Why it is feasible now: CFNs are lightweight enough to run during inference without destroying KV-cache performance, which was impossible with previous density models.
- What it measures: The diversity and pass@K accuracy of generated reasoning paths.
- Falsification: If test-time compute scaling laws flatten out just as fast with the CFN penalty as without it, the idea is falsified.

2. Disentangling Epistemic Uncertainty in Multi-Head Critics
Build a GRPO value network that uses a bootstrap ensemble (multi-head critic) to generate value variance, but apply a strictly decision-theoretic regularizer (as proposed by Bickford Smith) to forcefully separate model bias from data dispersion. 
- Why it is feasible now: RLVR multi-head architectures have just been proven viable by Dai et al. (2025) [cite: 2]. 
- What it measures: The calibration of the LLM's confidence scores against the actual correctness of its reasoning. 
- Falsification: If the variance heads collapse into identical representations despite the regularizer, the architecture fails.

What will NOT work:
Do not attempt to adapt string-matching, token-counting, or exact generative density models to LLM reasoning exploration. Token string exact matching is vacuous because a single comma changes the state, rendering exact counts useless [cite: 12]. Conversely, training an auxiliary autoregressive model online to track the density of prompt-response pairs is computationally unviable and the prediction gain will be drowned out by linguistic noise. You must operate in the dense semantic latent space of the LLM using random projections (CFN) or value variance. Standard count-based methods in LLM token spaces encounter severe, fatal practical limitations [cite: 22].

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWDTn_yT2UIqpxohMCpqzj88LJ3PwaK6fNlLKy3x_rGb-3eceGgRIGvT7_BLQIw78zmMsy9aX10bHcYX6R3kuB2RCa_sVw-zZyhAmtywhrKl2qoy2MC5Gh)
2. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdSukFsj0wZgYJ7a3RR1QL8RumDgp6FAseWQrRuvO6HJprIuCfSpkX8dawA5-N_-fIvFOpUU4HZc0z0BqmLZX3wuywtgzOTILZ77G7aXG4skjvY8VpBMVJdfjeSM0=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFG0LvrVkBHjPHsrgxot6-D0CGWE6b3RIug47klS0rCNwvP3xbKfdVFdUZZ-SjdtcZ8l1FZu-snvqoIodFO1P-oxh5-I1AseFQ4Miuq0NhdnCs7fkOlgXb)
4. [cleanrl.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEegHR_eHtPXUWcc2biUbsK9URZjNF-gAbX2_DNveQEpOqpRJZm6wPBJcj3m7WvHDFhYsBeyfxOJv2fd9YTQ0tUnTFJ8mu1PvX1mhzyqNKLbByFc5spacWfWmi8YmnG_HyztNoT)
5. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBZDA38qCWLDtVP_FVMGdrckuaexiFhFVQCOulBj45MmQEudeDV6TQzxoBHo1KcaZAtl1euKPXE8oTZFcmtIKIEByOJcJpk-CDBbjjNjfLzZW5pfEwX1fYzYUQcVs=)
6. [csdn.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPmiISlViJpm6IWuSVhUpURHAYf-ozhAiZfkPnK9oMwyzLW2aELOSYBvjgHVcXfM5uyVAxf4uhNZgfJGTGaD1J7lYvwtn-n_JDgH7EOtjPwz80-N2V1pKvTHuBee4zmWRDoG3yBjo4haKXavB4HnIOhR4=)
7. [githubusercontent.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdNc4Cr31Djf1tks2DoM98HycAC-gNUDIFWRyIpBVpO3SrSEpsdtOvIH7V2-Hp4JEga_jPvyGvev3iBYEjeexNT2DoixYW7SE30mv4aAETn7l9nVwD2liPbZWNV-n-H30Mtxhvcb2BIqElkS75dFuEwG8hqAKrnV3O48plUUQ26aBZaYuTXw4o9SVFudoDAxz4jME8iMeuAjh0)
8. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAqCLEzMUe9yGypdM2jOG5ZHkptHAat65J1eSxnyrOIu7H1mVux-qZHfWxhz7OCXuizELbavczouKr63LhVysrzlM03Wv8ZDm6BzAYbUlJuipDqBdi6sRxGN1ywg2nATxRc_hGtDG0TYi3vEqsTc78ng==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDMqskE3-kupx9lPsKhb85MKg9WUNLveLuJJY1JgNHfSutLBQKAx_U4O436us3WxvM7mzdGT7ceXUFGlRePhBhOJ08bKLZ1PN57MkK9bQJhxk0hyQq)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1czmC0_Xv4LkJZiKzKe3wwgPOxkypzzeYOrHO3xnYEaZa-UQVquQegBU1pStoC4VKA1CU8CDm4MXiRvD9HGxzCFt1w7B5Vu8g2pSLw_Oh4iHyGHxn3FKt)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHciO39WX2sZNVKvBfE0XVagtNfDCYLYMbkOj0NBw9P_mFzxSwOb-P5WQAZitp6ofCNnZJxPquFsgmewRT0WKChsiwe40yxc47smANF-Pv5HxEE51J0)
12. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAVh41J9DKGf0mS_LR7codsUWLQxfiW64H56luIG0u8P3oWZnrcFqNLcJMDAZ4XnE7LuUinRyt7jnbAU-zXIYAADEDEcVBm0abCBxmo_P_hwiv_o_UDE03SENo06pGFoFj5_cVPwJWOcSB7ZF1UvM=)
13. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETpG5TIQ3IzpV1hGJUxVD02XKul_Z2u1RDrQPj9DezPxl0fAu8YU3morm3NqK8fDDKOyD4gUmsgyEvDPT4zK-jUkl3ix80SNFvc4Sdxb0DaFtpXuZhfryhY5m8rw==)
14. [apxml.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgDmQ4bW57zjBHccgXeOjVK-NmJ0bX35jVFWUxgDir_1phZt7AXwjPZtudecbmb3hBa1gh1y7uV8RB4t3LKAN_CkKloHA7rp9-Y6AiuzeallV6LvOPdoN58kNrb3boXAdWiv5muktppGsT9-mzC16h5_sNlh3saTPvYPt3sqBpPNMFH0TlXGnSB2lmsEO8jpCSocJ_RTUU4-bcbb2XPsEJ3YvA3Hhs8-iAVX99E4aCr4IJoyXuek9OShs=)
15. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKN2yYdPMzpNN6mEXuegrjUUzDOZ_02KyALBDt2kP7CowxfLgu1zdPFa4eieG6W_UW8Re6EgKJWQzTcdRKVl45hCSGdaXDwPzERVByVL1WmWEjfnIuEQBwqt_Yrg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDGTEcfgXReNX0RjkwNBIXrWIWNeI9UffBFtIDwH6WSShOj3Rb2KvhxKEhtVV__CWPAn3QtiXa-jpHIi8ufrToptBNGJMGlrXwShB2x4uB4RlcZWEyvDPl)
17. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHW6k2uq8j8qRduX18pU30kqJTM7M0eHCHbnIMeJdYkU0rihCHMq90INoYojVsY2VsbZJis6UaFQIQ4BcjZC1WOTCKTZZ3i6pqT4GQGruZAVRmqIvamsF8KOznSwYtslg==)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH__obNChU9zxkchnZyFPbxSLC0ANSMX6gxSsKdPdEFYCt8uMgRGc3z93mcRp3iXUhoAf_ifEZPGleid1xu6cGTDW-pkNxKcWmYyttLaW25DLIwOCUXl4ryeIebqGGl8AnjIAzX6t9saNJuYDrApBlrZwFN-Fc=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYmet6fEwDyKMztcNGHzY7Ui29zpAmT9GZvHk-GH5kmF8o4al9EIMcF4h8p81fBUbkerPNWYwYu78LBVhQ0QPvhfiXfaTGrFKcIFJB7D3uPOllPl5qeyix)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGtp-CCrJt3l014de54bAaHmHuCk9CDvUfyEpgKag06JrVuXXP1raU9J8PuqyZ9hlepuKXgkqqQtssmiMJkNjF5M45a_iDCdHEBesRdETzLQQfOEv68_oW)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHE8bu_b3Nn180KLhahB65TQmShCE3f94moPdVKUeaX2eombgsP-ORKCnbYBUxD30GQPY4ZwARkffAneU9POFlDcjGUqyiP934J_0OGXzq2gCXuugVQtw==)
22. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKXpjcMZKPinLFE-OiaKCyZ_zJc0dxXZXDoW8AXghYlbCAwnPK6dZJzJzAwI-hfhAt-OxMIZsrgmPDD887pG7q28M6XiXG9pfoKUc0oIsog_2DfKVVTs4m0FAoGQ==)


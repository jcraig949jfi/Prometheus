# Prompt 27: Artificial Curiosity

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcyVS1mYXBDbENwM2lfdU1QajllTjBBYxIXMlUtZmFwQ2xDcDNpX3VNUGo5ZU4wQWM
**Elapsed:** 334s

---

# FRONTIER PRACTITIONER DOSSIER: Artificial Curiosity

The field of artificial curiosity, often formalized as intrinsic motivation within reinforcement learning, tackles the fundamental problem of exploration in sparse-reward environments. Research suggests that relying solely on extrinsic rewards provided by the environment leaves agents completely unguided during long horizons, leading to random walks that fail to discover meaningful behaviors [cite: 1, 2]. The evidence leans toward self-supervised predictive models as a robust solution: by equipping the agent with a world model and rewarding it for states where its model fails, the agent is intrinsically drawn to the boundaries of its own knowledge [cite: 3, 4, 5]. 

However, this intuitive mechanism is notoriously vulnerable to environmental stochasticity, commonly known as the Noisy TV problem, where unpredictable dynamics permanently hijack the agent's attention [cite: 6, 7, 8]. Modern approaches mitigate this by predicting fixed random projections rather than forward dynamics, or by leveraging Large Language Models and multi-agent peer contexts to ground the novelty signal in semantic meaning [cite: 9, 10, 11]. This dossier maps the exact pathway to reproducing the foundational experiments of this field, detailing the operational software, the authoritative benchmarks, and the specific failure modes you will encounter when building curiosity-driven agents in 2026.

PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Artificial curiosity in 2026 is an active, highly empirical subfield of unsupervised reinforcement learning. The mechanism you described—a controller network maximizing the prediction error of a model network—is precisely the Intrinsic Curiosity Module introduced nearly a decade ago [cite: 4, 12, 13]. The arithmetic consequence of this adversarial coupling is indeed an emergent boredom: as the model learns the dynamics of a region, the prediction error approaches zero, the intrinsic reward vanishes, and the controller is forced to migrate to novel states to maintain its reward stream [cite: 3, 4]. 

What is SETTLED is that pure forward-dynamics prediction error fails catastrophically in stochastic environments. This is universally known as the Noisy TV problem [cite: 6, 8, 14]. If an environment contains irreducible aleatoric uncertainty, such as static on a screen or leaves blowing in the wind, the model network can never reduce its prediction error. The controller network, seeking to maximize error, will lock onto this stochasticity and refuse to leave, resulting in a paralyzed agent [cite: 7, 8]. It is also settled that Random Network Distillation is the canonical workaround for high-dimensional continuous state spaces [cite: 9, 15]. Instead of predicting the next state, the model network predicts the output of a randomly initialized, frozen target network applied to the next state. Because the target network is deterministic, irreducible environmental noise does not cause irreducible prediction error, effectively bypassing the Noisy TV trap [cite: 7, 9, 16].

What is CONTESTED is whether pure exploration is sufficient for downstream competence. One side, championed by researchers utilizing the Unsupervised Reinforcement Learning Benchmark, argues that state-visitation and prediction-error metrics are the best proxies for acquiring a general-purpose pre-trained agent [cite: 17]. The opposing side argues that novelty-seeking alone is semantically blind. These researchers propose that curiosity must be anchored to behavioral skills, semantic captions from foundation models, or peer-agent behavior [cite: 10, 11]. The live disagreement centers on representation learning: whether the feature encoder should be trained by the curiosity signal itself, or if curiosity should operate over a frozen representation derived from an external foundation model.

What is OPEN is the scalable deployment of these intrinsic rewards in open-ended, procedurally generated environments and multi-agent systems [cite: 18, 19, 20]. In the last three years, the frontier has shifted significantly away from solving deterministic Atari games toward procedurally generated survival benchmarks and Large Language Model-guided exploration [cite: 10, 19]. Rather than relying strictly on the arithmetic of prediction error, the frontier now explores "artificial intelligence feedback", where a foundation model evaluates the semantic novelty of an agent's trajectory and generates a reward signal, preventing the agent from pursuing physically novel but semantically useless noise [cite: 10, 21]. Furthermore, multi-agent frameworks have emerged where curiosity is calibrated against the inferred intentions of peer agents, filtering out environmental noise by focusing on social context [cite: 11, 18].

PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL

Pathak, Agrawal, Efros, and Darrell
2017
Curiosity-driven Exploration by Self-supervised Prediction
International Conference on Machine Learning
arXiv:1705.05363
This paper formalizes the Intrinsic Curiosity Module, establishing the core method of using forward dynamics prediction error in a latent feature space as an intrinsic reward [cite: 4, 5]. A practitioner must know this because it defines the exact baseline architecture and highlights the necessity of an inverse dynamics model to ignore uncontrollable environmental features.

Burda, Edwards, Storkey, and Klimov
2018
Exploration by Random Network Distillation
International Conference on Learning Representations
arXiv:1810.12894
This paper introduces the Random Network Distillation algorithm, which solves the Noisy TV problem by training a predictor network to mimic a fixed, random target network [cite: 9, 15, 22]. It is essential reading because Random Network Distillation remains the most robust, widely implemented, and computationally lightweight curiosity mechanism in the field.

Sekar, Rybkin, Daniilidis, Abbeel, Hafner, and Pathak
2020
Planning to Explore via Self-Supervised World Models
International Conference on Machine Learning
arXiv:2005.05960
This paper introduces Plan2Explore, demonstrating how an agent can use a learned world model to seek out expected future novelty through planning, rather than relying on retrospective prediction errors [cite: 23, 24]. It bridges the gap between model-based reinforcement learning and intrinsic motivation.

Laskin, Yarats, Liu, Lee, Zhan, Lu, Cang, Pinto, and Abbeel
2021
URLB: Unsupervised Reinforcement Learning Benchmark
Thirty-fifth Conference on Neural Information Processing Systems Datasets and Benchmarks Track
arXiv:2110.15191
This paper introduces the Unsupervised Reinforcement Learning Benchmark, establishing the standard two-phase protocol: reward-free pre-training followed by downstream task adaptation [cite: 17, 25, 26]. It is required reading because it standardized how curiosity methods are evaluated against one another in continuous control.

CURRENT

Rajeswar, Mazzaglia, Verbelen, Piche, Dhoedt, Courville, and Lacoste
2023
Mastering the Unsupervised Reinforcement Learning Benchmark from Pixels
International Conference on Machine Learning
arXiv:2209.12016
This paper resolves many of the pixel-based failures in the Unsupervised Reinforcement Learning Benchmark by combining world-model-based agents with task-aware fine-tuning and a hybrid planner [cite: 27, 28]. It sits at the frontier of making intrinsic motivation work efficiently directly from high-dimensional vision rather than underlying state vectors.

Klissarov, D'Oro, Sodhani, Raileanu, Bacon, Vincent, Zhang, and Henaff
2023
Motif: Intrinsic Motivation from Artificial Intelligence Feedback
International Conference on Learning Representations
arXiv:2310.00166
This paper introduces Motif, replacing raw prediction error with a reward model trained on Large Language Model preferences over observation captions [cite: 10, 20]. It redefines the frontier by showing that semantic curiosity outperforms physical prediction error in complex, open-ended environments like NetHack.

Pan, Liu, and Wang
2025
Wonder Wins Ways: Curiosity-Driven Exploration through Multi-Agent Contextual Calibration
Advances in Neural Information Processing Systems
arXiv:2509.20648
This paper introduces CERMIC, a framework that calibrates intrinsic curiosity using inferred multi-agent context to filter noisy surprise signals in decentralized, communication-free settings [cite: 11, 18]. It pushes the frontier into multi-agent systems, solving the uniform novelty bias that treats all unexpected observations equally.

Hafner
2021
Crafter: An Open World Survival Benchmark
Thirty-fifth Conference on Neural Information Processing Systems Datasets and Benchmarks Track
arXiv:2109.06780
While slightly before 2023, this paper provides the Crafter benchmark, which has become the de facto testing ground for evaluating deep exploration and semantic curiosity, replacing Atari [cite: 29, 30]. You must know it because it exposes the brittleness of early curiosity methods that overfit to deterministic environments.

For a comprehensive survey, read "Curiosity-driven Exploration - Part 3: Noisy-TV Problem and Drawbacks of Curiosity-driven Reinforcement Learning" by Modirshanechi et al., 2022, or the extensive review by Aubret et al., 2019, which catalogues the taxonomy of intrinsic rewards [cite: 6].

PART 3. SOFTWARE I CAN ACTUALLY RUN

CleanRL
https://github.com/vwxyzjn/cleanrl
Python
MIT Licence
Approximate most recent activity: 2024
Maturity: MAINTAINED
CleanRL provides highly readable, single-file implementations of reinforcement learning algorithms. The specific file ppo_rnd_envpool.py runs Proximal Policy Optimization combined with Random Network Distillation on Atari environments [cite: 31, 32]. It is the most reliable way to reproduce the Montezuma's Revenge exploration result today. Known gotchas include a strict dependency on the EnvPool vectorization library; specifically, versions of EnvPool newer than 0.6.4 altered how truncated states are returned, which breaks the state observation logic in this specific file if not carefully managed [cite: 32]. Furthermore, this specific file does not support Windows or macOS natively due to EnvPool constraints [cite: 32].

URLB (Unsupervised Reinforcement Learning Benchmark)
https://github.com/rll-research/url_benchmark
Python
MIT Licence
Approximate most recent activity: 2022
Maturity: DORMANT
This is the canonical reference implementation from the originating authors of the URLB paper, providing an evaluation harness for Intrinsic Curiosity Module, Random Network Distillation, and several other unsupervised methods on top of the DeepMind Control Suite [cite: 17, 33]. It allows you to run a standard two-phase experiment: pre-training a DDPG agent without rewards, and fine-tuning it with rewards. The major limitation is that the codebase is rigid, deeply tied to an older version of the DeepMind Control Suite, and largely abandons pixel-based evaluation in favor of state-based evaluation because the algorithms struggled to converge on pixels [cite: 27, 34].

Mastering-URLB
https://github.com/mazpie/mastering-urlb
Python
MIT Licence
Approximate most recent activity: 2023
Maturity: DORMANT
This repository modernizes the URLB evaluation by wrapping the benchmark around DreamerV2 world models rather than the model-free DDPG agents used in the original URLB [cite: 27, 35]. It can actually run pixel-based unsupervised pre-training and downstream fine-tuning today. It is a vital alternative to the original URLB repository if you want to use visual observations. The known gotcha is its heavy compute requirement and strict dependence on CUDA 10.2 and CUDNN 8, making it difficult to build on modern PyTorch toolchains without specific legacy Docker containers [cite: 35].

Crafter
https://github.com/danijar/crafter
Python
MIT Licence
Approximate most recent activity: 2024
Maturity: MAINTAINED
Crafter is a fast, 2D open-world survival game designed specifically to test exploration and curiosity [cite: 19, 29]. You can run the environment natively in modern Python. The community standard for evaluating agents on this environment is found in the separate repository https://github.com/danijar/crafter-baselines, which provides Docker containers for running Random Network Distillation and Plan2Explore [cite: 36]. The gotcha is that the baselines repository uses older library versions wrapped strictly in Docker; attempting to extract the algorithms and run them directly on a modern host machine usually breaks due to dependency drift [cite: 36].

Controllable-Agent
https://github.com/facebookresearch/controllable_agent
Python
MIT Licence
Approximate most recent activity: 2025
Maturity: MAINTAINED
This is a modern wrapper around the URLB codebase maintained by researchers extending URLB to forward-backward agents and custom reward structures [cite: 37]. It is an actively updated alternative to the dormant original URLB repository, featuring simplified replay buffers and Hydra configurations. As an active research project, it explicitly warns users to expect no backward compatibility [cite: 37].

PART 4. DATA AND BENCHMARKS

Unsupervised Reinforcement Learning Benchmark (URLB)
Access route: Provided through the DeepMind Control Suite via the URLB repository.
Size: 12 continuous control tasks across 3 domains (Walker, Quadruped, Jaco Arm).
Licence: MIT.
This benchmark is treated by the field as authoritative for continuous control. It measures adaptation efficiency: how fast an agent can learn a downstream task after 2 million steps of reward-free exploration [cite: 17, 25]. A known problem with URLB is saturation on the state-based metrics for the simpler Walker tasks, while the pixel-based versions remain extremely difficult for model-free methods [cite: 27, 34].

Crafter Benchmark
Access route: https://github.com/danijar/crafter
Size: Procedurally generated infinite dataset, evaluated over 30 million environment steps per run.
Licence: MIT.
Crafter evaluates wide and deep exploration, representation learning, and long-term reasoning [cite: 29, 30]. It measures an agent's ability to unlock 22 semantically meaningful achievements, calculating a geometric mean of success rates as the final score. It explicitly prevents overfitting and memorization by generating a new map for every episode [cite: 19]. It is heavily authoritative for evaluating the robustness of artificial curiosity algorithms against stochastic environments.

NetHack Learning Environment (NLE)
Access route: https://github.com/facebookresearch/nle
Size: Procedurally generated roguelike environment.
Licence: NetHack General Public License.
Used prominently by Motif, this environment measures an agent's ability to navigate extreme partial observability, long horizons, and complex semantics [cite: 10, 20]. It is one of the hardest single-environment reinforcement learning benchmarks available. Methods that rely on simple state novelty fail completely here due to the vast, procedurally generated combinatorial space.

VMAS, Meltingpot, and SMACv2
Access route: Public GitHub repositories for each respective benchmark.
Size: Dozens of multi-agent scenarios.
Licence: Various open-source licences (Apache 2.0, MIT).
These suites are used to measure multi-agent exploration and decentralized coordination under sparse rewards, as seen in the CERMIC evaluation [cite: 11, 18]. They are authoritative in the multi-agent reinforcement learning subfield but less commonly used for single-agent artificial curiosity.

PART 5. THE REPRODUCTION RECIPE

The most reproducible and informative experiment is the execution of Random Network Distillation on the Atari game Montezuma's Revenge using CleanRL. This experiment conclusively demonstrates how prediction error computed against a fixed random network provides enough intrinsic motivation to navigate a notoriously hard-exploration environment that standard algorithms fail to solve.

Exact software and version: 
CleanRL version 1.0.0b2. Python 3.9. 
Target script: cleanrl/ppo_rnd_envpool.py [cite: 31, 38, 39].

Exact dataset: 
MontezumaRevenge-v5 accessed via EnvPool version 0.6.4 [cite: 32, 40].

Parameters to set: 
total-timesteps: 1500000000 (1.5 billion frames). 
num-envs: 128 (EnvPool handles this internally). 
num-steps: 128. 
learning-rate: 0.0001. 
num-iterations-obs-norm-init: 50. 
update-epochs: 4. 
ext-coef: 2.0 (Extrinsic reward coefficient). 
int-coef: 1.0 (Intrinsic reward coefficient). 
Sticky actions must be enabled in EnvPool to match the original paper's stochasticity [cite: 32].

Replicates and seeding: 
Run 3 independent replicates. CleanRL supports exact seeding via the --seed flag. Use seeds 1, 2, and 3.

Approximate compute cost: 
Executing 1.5 billion frames takes approximately 250 GPU hours per seed on an NVIDIA A100 or V100 GPU [cite: 32]. 

Expected result: 
The episodic return should rise from near 0 to an average of 10000 to 14000 points. Compare this against the learning curves published in the original Random Network Distillation paper by Burda et al., 2018, or the CleanRL openrlbenchmark report [cite: 9, 32, 40].

Three most common ways people get this experiment wrong:
1. Environment Truncation Bugs: Using an EnvPool version newer than 0.6.4 or swapping EnvPool for Gym version 0.23.1 alters whether the observation vector at the end of an episode contains the final truncated state or the first state of the next episode. This silent misalignment destroys the trajectory continuity required for accurate advantage estimation [cite: 32].
2. Target Network Gradients: Failing to freeze the random target network. While CleanRL correctly extracts the data using .data to prevent gradient tracking, practitioners writing their own loops often forget to wrap the target network in a no_grad context. If the target network updates, the prediction error collapses to zero trivially, and exploration halts [cite: 41].
3. Intrinsic Reward Normalization: Failing to normalize the intrinsic reward stream. The scale of the prediction error varies wildly over the course of training. If the intrinsic reward is not normalized by its running standard deviation before being added to the extrinsic reward, it will completely dominate the value function, causing catastrophic forgetting of the actual game objectives [cite: 2, 3, 42].

PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to run frontier experiments in 2026, you will quickly find a gap in tooling for integrating Large Language Model feedback directly into real-time reinforcement learning loops for visual environments. 

What has to be built: A low-latency, asynchronous episodic memory and captioning buffer that bridges continuous pixel control and foundation model API calls. 

What goes in: High-dimensional visual observations streaming at 60 frames per second, and the current state visitation counts.
What comes out: A dense, normalized intrinsic reward signal representing the semantic novelty of the state.
What the hard part is: Large Language Models cannot be queried at 60Hz per environment worker during a rollout phase due to inference latency and context window costs.
Roughly how much work it is: Significant (3 to 6 months of engineering). You must build an asynchronous architecture where the agent interacts with the environment using a fast, local proxy reward model, while a parallel process periodically samples trajectory buffers, generates textual captions using a Vision-Language Model, queries a Large Language Model for preference rankings on those captions (as in Motif), and updates the local proxy reward model [cite: 10, 43].

Several groups have rebuilt similar asynchronous reward updating components privately to support methods like Motif and CERMIC [cite: 11, 43]. The lack of a standardized, off-the-shelf "Foundation Model Intrinsic Reward Wrapper" that drops into libraries like CleanRL or Stable-Baselines3 is the strongest signal of a real gap.

Furthermore, for multi-agent contextual curiosity (as in CERMIC), there is no off-the-shelf dynamic intention graph extractor for partially observable environments [cite: 11, 18]. You would have to construct a custom graph neural network memory module that tracks peer agent histories to modulate your own agent's intrinsic reward, which currently requires highly customized PyTorch code heavily coupled to the specific simulator.

PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of artificial curiosity is defined by methods that looked mathematically elegant but failed empirically due to the complexity of actual environments.

The Noisy TV Problem: This is the most famous negative result. The Intrinsic Curiosity Module, which calculates reward based on the forward prediction error of the next state, fails when the environment contains stochastic, unpredictable elements. Burda et al. proved this by literally placing a television playing static noise inside a 3D maze. The agent stares at the static indefinitely because the prediction error remains permanently high. The method was measuring environmental aleatoric uncertainty rather than the agent's epistemic uncertainty [cite: 6, 7, 8, 14].

Trivial Randomness and Couch Potato Agents: Similarly, if the representation encoder is updated by the same loss that trains the prediction model, the encoder learns to collapse useful features and preserve only random noise, maximizing the intrinsic reward easily but completely halting skill acquisition. The agent becomes a "couch potato" [cite: 8, 13]. The critique here is that coupled optimization of representation and prediction creates degenerate solutions.

Overfitting to the Benchmark (Montezuma's Revenge): Random Network Distillation was heralded as a breakthrough for solving Montezuma's Revenge. However, it was later shown that Random Network Distillation relies heavily on the deterministic nature of Atari. When applied to procedurally generated environments like NetHack or Crafter, where the map layout changes every episode, standard Random Network Distillation often fails to generalize [cite: 20, 29, 30]. The method measured the ability to memorize a specific state space topology rather than the phenomenon of generalizable curiosity.

The URLB Pixel Failure: When the Unsupervised Reinforcement Learning Benchmark was published, the authors noted that while state-based unsupervised pre-training showed progress, pixel-based unsupervised pre-training essentially failed. Pure curiosity methods operating on raw pixels could not solve the benchmark tasks [cite: 17, 34]. The critique was that curiosity in pixel space is too noisy and unstructured. This critique was partially answered by later work (such as Mastering URLB from Pixels) which demonstrated that replacing model-free agents with world-model-based agents (Dreamer architecture) could successfully bridge the gap [cite: 27].

The Uniform Novelty Bias Critique: In multi-agent systems, pure novelty-seeking algorithms treat all unexpected observations equally. The standing critique, answered recently by the CERMIC framework, is that an agent should not be curious about random variations in its peers' behaviors if those behaviors do not affect the task dynamics [cite: 11, 44]. 

PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the current landscape, a well-resourced newcomer should focus entirely on semantic and contextual curiosity, leaving pure arithmetic pixel-prediction error behind. 

Experiment 1: Vision-Language Model Curiosity on Open-World Survival.
What to do: Extend the Motif framework (which used text-based NetHack) to the visual Crafter benchmark. Use a fast Vision-Language Model to generate captions of Crafter frames, and a Large Language Model to score the semantic novelty of those frames, training a proxy reward model to guide a DreamerV2 agent. 
Why it is feasible now: Local, fast Vision-Language Models and efficient asynchronous reinforcement learning architectures make real-time multimodal feedback possible. 
What it measures: Whether semantic curiosity scales to visual procedurally generated environments better than Random Network Distillation. 
Falsification: The idea is falsified if the LLM-guided agent achieves a lower Crafter score than the baseline Plan2Explore agent, indicating that semantic abstraction deletes critical low-level exploratory signals. 

Experiment 2: Multi-Agent Contextual Calibration on Real-World Robotics.
What to do: Implement the CERMIC multi-agent calibration framework on a physics-based simulator with simulated sensor noise (e.g., Habitat or Isaac Gym). 
Why it is feasible now: CERMIC has just established the theoretical framework for peer-calibrated exploration in 2025 [cite: 11, 18], and CleanRL recently added Isaac Gym support for heavily accelerated continuous control [cite: 38, 39]. 
What it measures: Whether intention-graph calibration successfully ignores aleatoric physical sensor noise in a way that Random Network Distillation cannot. 
Falsification: Falsified if the agents exhibit the same Noisy-TV paralysis as standard baseline algorithms when introduced to environments with high wind or moving irrelevant distractors.

Experiment 3: Unsupervised Data Generation for Offline RL.
What to do: Run URLB pre-training using Random Network Distillation to generate massive, diverse replay buffers, and then train offline reinforcement learning algorithms on those buffers to solve arbitrary downstream tasks.
Why it is feasible now: Theoretical frameworks for Unsupervised Data Generation have recently proven that unsupervised RL methods can minimize the worst-case regret for unknown tasks by generating diverse datasets [cite: 45, 46].
What it measures: The utility of curiosity-driven exploration purely as an autonomous data collection engine, rather than an online learning algorithm.
Falsification: Falsified if offline RL trained on a random-walk dataset outperforms the dataset generated by the curiosity-driven agent.

What will NOT work: 
Do not attempt to scale the Intrinsic Curiosity Module or base Random Network Distillation on high-fidelity, highly stochastic real-world robotic domains. It will not work because physical environments contain infinite irreducible noise (e.g., textures, lighting changes, dynamic backgrounds). The arithmetic of predicting raw pixels or raw random features guarantees that the agent will be captured by the most unpredictable element in the room, ignoring the task entirely [cite: 8, 13, 14]. Pursuing forward-dynamics prediction error without a mechanism for semantic filtering or aleatoric noise isolation is a proven dead end.

**Sources:**
1. [geeksforgeeks.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEL26GuDK4yPLvjlA0KLzJbHAlbp86M4EwRVrucE-tWKrZ4obPLopTjv1MA2QCUxj5NjWAxLGUEo2HhaL1-k8KfqUt0jGGghC-ZWEHZIBgVhL4YguX6VF6zLp_hntoI_o-oHi0U2LYWWDNX_FJYULtYYpFlnowgFf65Ayli9gFEKtCrhjkYm5ae_VQ3tuP9CB4ppQ==)
2. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz-3b3-mtyq2U3pAfvdih_O75VZcJSyOxLzQOzKCTECK6ZVXnM8t3LT8ERiE-wZDUb3T_LpWtcfj8r-kmTpjqXc2BiS5QY-BaCaI79m3Ay_etXlB3ejXeA1AjBys7A54-ZD65bYQKvt5uDIQCKMjXkkpbQyFayl-zlEVLwPhqtMdcTB5WJVtRZ0dJy-qfj_j11QiOxndshTE7hCUEkOAplTO30pNQcqn1V1UkS2UQ=)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTQGYzt9xRn3vJQduaOW_C553pFV-7KhInCEzugRU9o1lceUfbtJd-RKOOa7nEPXDdjJhviBkIK_3F2kmvO1a5qX36NLXdvVrrmfUMt_68ZUKsl3MMgUylXgF5ep6im-s-Z4qnH_Iopz5cZx_5YAWjSmA-eEep5_ITxKbfIkz91aW29EjQAISN8aRiFQ==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9xI85YIg7TP5oj5AXFYEyrHrPMecgomqZ-Zm5-wHiDY6kNfAoly2dr_nE0eRgV-z42J5M79d4wf564LevKexYdA2v_UEiCeo5KkUyQ5O9fa5J0pSo71pM-e-ESK9Y2oPw)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEW-T2wJD4piWJO_jh-rF-4IsXDcyDtZsM9Ii4C3m41FAtsd3ujowPaGSWhwAtnU_8tRyeI_ZpWx4oz9FJZTa51CPuv4Mil1j8F6aNd3-vX0pNGgyNj)
6. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLL9jXfiil9WxNR1J41pQff5EdU6cyX31yZTqo9-HD2aPOIwrMUnf8Ap6dNy0ZJ2eZgCydMXe3yeDJ3hrSzUcpRqxICf4e-POXB3f43Vm5jUWK94ZNeaMh9zq3ba6qhPU=)
7. [openai.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfc64Km5L9PsjeSsr8T-nNl20Rmb3fmL4mpoD9LdZbN1ki4Blhd-0NFaoJCiF2aXE3b6qMhpwoPZKMkW-M_MMCH27LwmHztJ8xC3rFLllbh1S6TkM8HMgwLAIrlrKqGQGWEMDv-5Wz2y8xPUIJjiYICAUnp36JWrJxgczgaUhfkyPHWA==)
8. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVraodImUrZGd2ClHgq8DNee90XWFhFJXInlDE4ZWWWh3HdhaQpAnE9mw1NM0fntzT8m7vNG_OqBddJzjoDMVsfRcMuF0L4ck2MBAMBvzztqJaySkv4IK3ifM4jeXHozytvNCMMf2Ban3huGbrUM43d3UO)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpzdNm60A3R4by3i_G9Smtm0EdEvXAK7sI3sdtHsPDcpqRWlkhIjiDrKZ_tbG3PV_18ojS_BkwLsxx-QcCHFoRg_5Tl6zD9SSAumthIvO4t2NWR1SM)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpLVNh3mDr0n58Rw6rLL36Vbo3ioxgSnFDuXKgJ_ZIDyG5jRy1xuKJWF_zf39bZD1BpMjRvMvSPeuEwpwD_-WeCdPFT1RU-gw5Pug_sS19eSz3DaWwaxZQ)
11. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8WgDyuFLn0ud2r6qOrHidf8tuEa5YSS59O_fmVcBdooulxAIgdqS-VS5uzZwC6BPEwAb9skNQzysM8A-NCw1Fw1HgoCpJMZ-IYSQqEVtJmqZb2n4Ur6rm3hq2wjdKcJjzVw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZVfTtHIHdn688Ca51hg8_J3OCUKxQAiED7gTv-WorYb81De9whza9edLG9VCy9pOy7ug-CRQAXzuD57b64__-DfLqrBSQp6FVmPw7VcuqAX9eIO_B)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHexLMhyUWvv-BkQt7GwLZntNmG8AFgxkGFknq-71ehgmQ2CsC2nnCpAUNBDDPdnzposWlCsqeZwfHgIGHjhtA_grcUZtZv7kO30kk7d1Z4Nw7_gYC3_G_nEaWOHUSV0-_ZjR7HiuvLGq_ARF9Sij5CwXiGXAcSQ5kVJz4aUYWlMxWp3zGr3be7CK5sr68Bj-sCByAqRurcMW6W0mDEdx6ktkA=)
14. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjmS08FLHy7Eab6Zy1Vs8fUcLR8ayDyro6wJj5_qWHQOilNydFaZLau6cDHGwjrEgQvcr6SE_bh4QWsjFCCnUsk3fbUc40jZ5UrM8POGMVSzNytozB_n8KUvZuZHEUhRzFHCftjMPHXVqOZJRkNegdp1_21ala5uzNkviG4BrFL2fArw0ShF3G8zxYRfXJLXHxspabJKQ8zsfqckMqjvpBSI0ymuwlmA==)
15. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxXM3Z2bxfLoFFXpTTzrGc1HcTJLLjRpz2x_N187WkvsfmVM7bPy96uLQ5eT8lhrDjtl-sLBDZKEkGmEDGlTvagP2weHvuxZu_TfP4xdcPyk392XARAyCCa6MuNXyEpXGWoKv0kxmHhRIJlUK_RdYMzKOkETgDB1Pbpvz2EJ4C0jFgW1S5xA_sma5qDkQR6Q==)
16. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtIscmeKcMgubs3oqDB5FPDJG6jzSWZGfybfIIM5wyrKAWC6ieC66_MsioAGZkUspc4sefOPxz7WsL20rIn7yQLkgzTPEtI-0P7Jpzt4Q90UiD8OyIht7obaH92g==)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG11cbjMTeU9JsoakfxLmK3oFcBYLKDByvnh-eLpmvgxUVEp1aYbyCEj0bRyZ04kaPkH3pCrW9LUuqazbbAG7QwcK7Z42828kbT6TF0dvfcR7LVdXkN)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsXGjr8JwYggjQgZxejWz5_etA1pon0VdO3cLrtuQB-CHFd8-Q1xV40jLHfx7Bn7Go9RXZ9Y9BinDtwxfR4OIFmcS3ytrGc4iT1VdpWuiwQ0ntlYaq)
19. [pypi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcLbb_1sgzpWOf5YM-Z1PCnk4SuhLosFmRlTgyMHhlNwzGEwzuAIhWfga0eBMXCWGxt2pqpqUCFoZNtkDm6icg9o-lQD-hhZWLSuEJEDub1QDgopFcUtq4__QjfMo=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRdUgkrKkI7R8y0TSvW8F_vMgGMr95aGxy4wBCTCZg-cFUEqFcN_S7XYy7ubu_JSc7CFd0Y1vzNsJIRxsepdkAGamNo-ZKnU5F8FAUxMx-uYbO9iGy)
21. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4U6Nxzs-IWhITYmBNJOLzDXFEfj317l3XP1QTPx_Up4juJZXbLWMF0EPIBFNC2ZwJ_eSyy0vPMWowO0_VvUbSThSWckn5oBx9zUNZd155GmNxF7YqlK4viKdQiQ==)
22. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy2oNGvdJ-GKZejxevxeUxmR2kd8Q-pUL4AurMVSP-GEPbU1KbGEXYKO-tYhXZp4di3Yms5IEIwj-LoJDhWYJS31iumcfyrMvYY0eWMVJ_dR33XP1aeGKDvGDS5RUnnjUPElCRocQX6FSrUPO7nv7uYX6kfYX5tX1v2PlLIUF_Kr2f-f3tYaAW57EOtcxCPE7mylxi4OYFY6knmktSfvAXAgi_CRXofSPmdEYVIRxmp-1kC5z3D585zXp6y4s=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_0phsQ4jxaIgL32yFe-2-WZFmgUJyGKikyt_9oo7gQAHUZQvuTr1MXbNmXjml-_hKDsKqlUbENLEkVky9I3JOCuBVwtwVo95VLUKu0hOf4JMdWVWc5EkK)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVJg9z54rowOLNBVNSyCL1G-Gsu1xza0yHPvxISndLlK9rA6SyqGQMR5p6eXOLV81KzVasz6bwjv48xZKPsQ4FBswROzpCcdaaE3WYlDv60B7_svbG)
25. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMH6OcT6fux620evApQY4SZOVFG6FKWYDaVNkjsX34Tcc-3jptFkGJd01lD3CnGsMgfBeXIm3ySJbxq4IkNDHAarKEK1OEWGkzj4UpZOk2YMEWLfCzKMQJEIObQ-DcEw==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0_Xrl8bq2zArRtHHFqbghoNASA_EZzB99v0Z1Np_crfeX6fviJmsZ7SwOLs1YyhrxtjHd3zJFD6hk5eqvLNmcMxhkgFc9IdI1c_q_EL6v_B_FOyIS)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN0VNlhyfpcdjzJlbLCGQOXdGtrMRieBcAd6uL0QYoHKP8aGSER5dsjB2ZLFaovWoz7WdLb8lQ_7LIctvBqbWFxrYwdC08CYo5wt4rucVYSo2aUH6l)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXNl_X2Ktqzt9ryB2kgslXNN2EZypgBmCX70981kJKNUqz6eOc7NzAdoJzdZbWrGRd7coCcnYJ9brWWj-I15cOLG77lMJV_0NS688FE2JKKOmJ803d)
29. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6T2JXGAaaQEJAYckB-_qlWr0kIuPi_Da8DAyuh1VvUK8bJL3dQ9_kzGllwidEXYWmDL_c0WqJ2MkTEUOQM75BTUdkA2DAWQ33ZiJMrbVI1yuhbudmTwc=)
30. [danijar.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbpXE-xC9Hrscy-kdxFKvlNbi5A_06vpgoAcWeB-nv_5l99T4Lz75SREy6FZhIpq6mMXIug_HaMkwPQr8A_kjUVi6r2rPnd5Hssel9oBmcvzZLBLY4Osrkcw==)
31. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEo-lm0bxYCTktQ5bWrLdmV71hTdp_fkOR9zfIKBhkzTVmVL8HkoEwGfCB12p-39Dg-_jDg4wgZv3-SYTV-smjZMCGdYXUpegStGxrJE7AEZF6PKLK6rZU=)
32. [cleanrl.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxWmkpckYWAaw-fM3fMre48GrMDDFISoCci6dpNRLYVgsayhzcSZSrLAx85i7YMM-IO0kxg8CjsFyBlMHh8OGl9EvuzGEHTDRPdN1qIZ0smQ7iRYwmJBDoHcSMwyNH5hPw9DYV)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOlgpIVJLxqgmsvmPQs1cGPMORvalwuQWptM9-pCXTMxUsqnsh3X5TCD3L8gBx465vLq9DisYvGtoqgG648oEdtyFFZN9b_8ouMkvEPvwdwHWL_ee3e8zSFcEStHxTSBMf3g==)
34. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEefWMbwpHRReQxvAOurOm3YDaDC49riF4Vxmcc0hPk2i6N7A7Kr-uqvhe9yCSCZRLLeGnXl5gaemkAtmexIR7qRVJXRicIOvUXB5JyVLQZqkMB53Ma3T7DG_ySKZLrQFqlH915fTzIyIqNsq6jPvcUTBVl)
35. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfbWu6_gWNGd91tIqX_CzICmELkcWfErz1I5CjNdzdMIJwzMKABP8Q4V68FUGso8znegxjMaZku6NdKVpZnAzgmB090qyETSv4HoAvt3XiveydjhqoJpgo2b64cSI=)
36. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt9wSq-rr9Ohrsobr1YtiCVTWsPJKU6PCRAb7Oa5Pn1-gFdJIUTbBf3rVgcj-k8AbBB64RkOAduyiOpvLGDBjM2-M0p3jSNWVX5A5aq5LWFUZYPksSFkFMPN9Z3aonYKj5)
37. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHIknu_KX5PGLUeBWv1TefR-a4ncvupL5ytO6ZJtbW8wOIIaGAvPDc91B3HUCkRahleZv-PlpIShf0oGN7ngXiTaUlNKaVYYC5KJGGU2Try7446knTh2JmNnasfQT-oHv1AjZp_vSHvAgV7Q==)
38. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdfQvxyuqftTE3OpC2ukcQFFmo2EmuHL7XDhIsYQHrGz7SqA5tm6XwR2qY7yXeKLPkMXKAjRk4S_QzDIHLQNb9dfRyPfq5IvCRKChPL7JbV-V4YpMzYo2qMpTlp5Z0Ewg=)
39. [sourceforge.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_fo_sEgRUp9u49zZCI_0seru5NEBJEkTFXl9rujemozAbmQgLMED6vgSKnifsc8Umn_nrTiQzxIkFmdXrPuxmcJqpfosivkNl77akrMjshbqaFFKurDhpSjESG7BENVKKua_syE-splHn1YrKxNgrtZuSkQ==)
40. [wandb.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcKd4S64EkaNZLYkKSC7VBCI787-z-Ep3z_ix7rK4_5o5bMx0A9KQFXpJmjfkczebgHa546uIQtfcSac9r_0YV76yUq8qan62guexrBx8VSSd5Po3i8d9lVoIWH0O3lkpEIuz4fw0qWUYNXilEBXEVp7_msCDLCdVSEEqwJneqeotAz6DH5oHQj-ah65SDlxQCW8NPeDE91r5lkekXwQGrZyV2)
41. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXEB5aABLuiH_SnimxzpKUYNeeykIETQF3A6THQjVWxWYnhCmeENtQlY0ldqDkdAnXqfXqbTfAeCCCZ4oNLt7qZW9iYfUtTtuXEOZaPgJwYP74b3EvbrZ9SWQQ3WfLmv_Fxg==)
42. [csdn.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzSVuwUW4cnMX-mWJLbPRdmBFjW510CeKQ5TxN0OQFLWWAbcZvhVA-bwZNZU7Lcqo_JPmLa0Oaqku-eu4YyPP8MEcCeM0y9izU0ZCBbj-cKGHyPdvo2n7IQ2RqmjCGn8tpDHWnohbi4fqhjUt6unjeKs0=)
43. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4Knpf_wBmYJFU_fERZQ0GJrbFqvNc5qgh4ufyc1-Z6XIqrekRMkM9Ed876zIQmxtxL8nuvPMw649rPP5SS8oehMZw-qLf-pa-0OsKLOFMC2zARWdg7IyMhJbLeZex74gDxxM1sXfpn8nA5kJkjrA1c2pGL0FvKC8wf7FQr159Lb9r2DQ64hw5IbxD61dO6EmlkxV5sPoZBIWE_R_xpCf4qfMjmVp_bji9xCyuDsmkUZpLrWnHoFZL8ZQtd0XwDvYmH07J)
44. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhl9kN7M8OyYYbhbq5NjjGOLA47pE2z13ygjJZFjA6xyHCxT_WkOFVnuKEuD_Jo7mrTGRNoNUiznBd87vDMNN5TMOtOVC_jZUh0F_YgS8qotMjJG2PxzI5jSt4QnCGDAzKXABbfrrtdlV4404PzuHCe7xAkw4FtFlJH-QM-bWpDeLyDNWJHCZWjZCa32Mk0s6gt6UbmUklQsUMgd1W-kcffzAO14bC9OXwaGs3ktKODWWmO92i_VlEHVn6iVbcrEds)
45. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGItiCO9veSpgbbOQkgr14j2QxlvccnZnxRegNeHeqMNiZn-NR_e2WNRtiXsxWH2FQ5-iI23V7n9-CgshfFK2ysP0G27laHFr0pt0bpZ-WOiDw7LEfSF2a0gRKywclwaAx2u-Cq_p5041cxfN1ge61Mbgb8xdHBg17BjJEDJpBMCt7bAhxAuc2a7vyAxSpFWl0SkUUZwk5-Am-_6o53FotSrr8=)
46. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYcTYxR2gIEb9p4WYa3HroJn27JUua04ZS5xE6A_gMnnB4t8fHXLJzg0gXVEWeCVwIa7ur_xPOWHeo77sGnhv9M8JS_Et1kOs6t5DcrXsuCSjoXt5a-P1Q)


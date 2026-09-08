# Prompt 24: Autocurricula

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdaMDZmYXNYdElJdmhfdU1QOGJqXzhBcxIXWjA2ZmFzWHRJSXZoX3VNUDhial84QXM
**Elapsed:** 364s

---

# Frontier Practitioner Dossier: Autocurricula in Multi-Agent Reinforcement Learning

The study of autocurricula—the spontaneous generation of increasingly complex learning challenges through agent interaction—has undergone a radical architectural shift. The phenomenon you described, anchored by OpenAI's seminal Emergent Tool Use research, remains the conceptual north star of the field. However, the engineering reality of how these experiments are conducted has transformed. Pure multi-agent competitive self-play in heavy physics simulators has largely been superseded by Unsupervised Environment Design, hardware-accelerated environments written natively in JAX, and the integration of Vision Language Models to score algorithmic progress.

Your understanding of the hide-and-seek mechanism is highly accurate, but it requires one vital correction regarding how the results were measured. You noted that identifying a regime boundary is a change-point judgement over a long time series. In the original research, these boundaries were not identified by an automated, generalized metric [cite: 1]. They were hand-annotated by researchers using bespoke, hard-coded environment heuristics, such as tracking the maximum movement of a box or the exact count of locked ramps during a preparation phase [cite: 2]. The lack of a universal, algorithmic metric for detecting "new strategies" remains one of the most profound bottlenecks in the field, and a major reason why the community pivoted toward algorithmic teachers that explicitly calculate the learnability of a task.

Furthermore, the famous "box surfing" phase you referenced was not a natural strategic evolution, but an exploitation of a flaw in the physics engine. Agents discovered that by locking a box and pushing against it in a specific way, they could break the simulation's momentum calculations and fly across the map [cite: 1]. This highlights a crucial tacit reality: in open-ended physical autocurricula, agents will relentlessly hack the simulator before they learn human-interpretable strategies.

The report below is engineered specifically for your entry into this field today. It strips away the hype and focuses entirely on what is actively maintained, what actually reproduces, and where the algorithmic frontier currently sits.

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

In 2026, the field of Autocurricula exists at the intersection of Multi-Agent Reinforcement Learning and Unsupervised Environment Design. Originally, the field was defined by symmetric zero-sum self-play, where the curriculum was a natural byproduct of two opposing forces escalating their strategies [cite: 3]. Today, this pure form of self-play has been largely absorbed by Unsupervised Environment Design. In this paradigm, the autocurriculum is formalized as a game between a "Teacher" algorithm that parameterizes and generates environments, and a "Student" agent that attempts to solve them [cite: 4, 5]. The Teacher is rewarded for generating tasks that sit perfectly at the frontier of the Student's capabilities. 

What is SETTLED: It is mathematically and empirically settled that naive Domain Randomization, randomly sampling environments, fails catastrophically as task complexity increases [cite: 5, 6]. The probability of randomly generating a task that is solvable but challenging becomes vanishingly small. An adaptive autocurriculum is strictly required to achieve zero-shot generalization in complex spaces. It is also settled that modern research cannot be conducted in Python-stepped simulators; the field has almost entirely migrated to JAX-native environments that allow millions of steps per second on a single GPU [cite: 7, 8].

What is CONTESTED: The absolute core of the field is currently locked in a methodological war over how the Teacher should score the environments it generates. The dominant approach for years was "Regret," measuring the gap between optimal performance and the agent's current performance [cite: 4, 5]. However, a recent wave of literature has demonstrated that common regret approximations are fundamentally flawed, arguing that they do not measure true "learnability" but simply correlate with the agent's raw success rate [cite: 6, 9]. This causes the autocurriculum to stagnate, feeding agents tasks they have already mastered. The opposing camp advocates for variance-based scores or novelty-based regularization.

What is OPEN: Jointly co-evolving both the "Task" (the rules/rewards) and the "Level" (the physical layout) simultaneously [cite: 5]. Another massively open frontier is Visual Inspection of Policies, which uses lightweight Video Large Language Models to visually watch agent rollouts and dynamically propose the next curriculum step, completely bypassing scalar reward hacking [cite: 10, 11].

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Baker, B., Kanitscheider, I., Markov, T., Wu, Y., Powell, G., McGrew, B., Mordatch, I.
Year: 2020
Title: Emergent Tool Use From Multi-Agent Autocurricula
Venue: International Conference on Learning Representations
Identifier: arXiv:1909.07528
The exact paper anchoring your query, detailing the hide-and-seek methodology, the six phases of strategy emergence, and the use of scale to drive multi-agent autocurricula [cite: 1]. A practitioner must know this to understand the historical goalpost of the field.

Authors: Dennis, M., Jaques, N., Vinitsky, E., Bayen, A., Russell, S., Critch, A., Levine, S.
Year: 2020
Title: Emergent Complexity and Zero-shot Transfer via Unsupervised Environment Design
Venue: Neural Information Processing Systems
Identifier: arXiv:2012.02096
This paper formalized Unsupervised Environment Design, shifting the field from pure competitive self-play to the Teacher-Student minimax regret framework [cite: 4]. It is the load-bearing pillar for modern autocurriculum generation.

Authors: Jiang, M., Dennis, M., Parker-Holder, J., Foerster, J., Grefenstette, E., Rocktaschel, T.
Year: 2021
Title: Replay-Guided Adversarial Environment Design
Venue: Neural Information Processing Systems
Identifier: arXiv:2010.10443
Introduced Prioritized Level Replay, a technique that curates randomly generated levels based on the agent's learning potential [cite: 12]. This is the algorithmic backbone of most modern reproduction attempts.

CURRENT FRONTIER SOURCES

Authors: Matthews, M., Beukman, M., et al.
Year: 2024
Title: Craftax: A Lightning-Fast Benchmark for Open-Ended Reinforcement Learning
Venue: International Conference on Machine Learning
Identifier: arXiv:2402.16801
This paper introduces the premier JAX-based environment for testing open-ended autocurricula, running 250 times faster than its Python predecessor [cite: 7]. It is vital because it redefines the compute baseline for a single practitioner.

Authors: Rutherford, A., Beukman, M., Willi, T., Lacerda, B., Hawes, N., Foerster, J.
Year: 2024
Title: Sampling for Learnability in Unsupervised Environment Design
Venue: OpenReview (Under review / published)
Identifier: https://openreview.net/forum?id=iEeiZlTbts
The most devastating critique of current autocurriculum metrics [cite: 6]. The authors prove mathematically and empirically that existing regret methods fail to identify scenarios an agent can only sometimes solve, providing the new state-of-the-art metric.

Authors: Furelos-Blanco, D., Pert, C., Kelbel, F., Dennis, M.
Year: 2025
Title: Beyond Fixed Tasks: Unsupervised Environment Design for Task-Level Pairs (ATLAS)
Venue: arXiv preprint
Identifier: arXiv:2511.12706
This defines the current cutting edge of generation, extending autocurricula to simultaneously co-design the physical environment and the internal state-machine of the task itself [cite: 5, 13].

Authors: Lee, H., Oh, J., Lee, B.
Year: 2026
Title: TABX: A High-Throughput Sandbox Battle Simulator for Multi-Agent Reinforcement Learning
Venue: arXiv preprint
Identifier: arXiv:2602.01665
The multi-agent successor to JAX gridworlds, offering a highly modular, massively parallel battle simulator [cite: 8, 14]. This is the exact software architecture a modern hide-and-seek experiment would be built upon.

Authors: Pante, L., Fanti, A., Capobianco, R.
Year: 2026
Title: Open-ended Multi-agent Autocurricula via Visual Inspection of Policies with Multi-modal LLMs
Venue: arXiv preprint
Identifier: arXiv:2607.08193
Introduces VIP, demonstrating that feeding video frames of policy execution to a Vision Language Model provides a better curriculum trajectory than local scalar reward signals [cite: 10, 11].

BEST SURVEY

Authors: Yuan, L., Zhang, Z., Li, L., Guan, C., Yu, Y.
Year: 2023
Title: A Survey of Progress on Cooperative Multi-agent Reinforcement Learning in Open Environment
Venue: arXiv preprint
Identifier: arXiv:2312.01058
The single best mapping of the transition from closed, static reinforcement learning to dynamic, open-ended environments [cite: 15, 16].

## PART 3. SOFTWARE I CAN ACTUALLY RUN

multi-agent-emergence-environments
https://github.com/openai/multi-agent-emergence-environments
Python
MIT
2020
ABANDONED
This is the canonical reference implementation from the originating authors of the Emergent Tool Use paper [cite: 1, 17]. It is effectively dead. It relies on outdated versions of MuJoCo, which previously required proprietary licenses, and legacy OpenAI Gym wrappers that have since been deprecated. The published results cannot be reliably reproduced with modern toolchains without massive containerization efforts, and even then, the compute cost spans tens of thousands of CPU hours.

Craftax
https://github.com/MichaelTMatthews/Craftax
JAX
MIT
2024
MAINTAINED
A reimplementation of the Crafter benchmark written entirely in JAX [cite: 7, 18]. Today, a practitioner can run 1 billion environment interactions of open-ended curriculum learning in 51 minutes on a single GPU. It is the community standard for testing Unsupervised Environment Design throughput and single-agent open-endedness.

TABX (Totally Accelerated Battle Simulator in JAX)
https://anonymous.4open.science/r/TABX-00CA
JAX
UNKNOWN (Pending de-anonymization)
2026
MAINTAINED
The absolute frontier of multi-agent physics and battle simulation [cite: 8]. Because it is powered by hardware-accelerated JAX execution, it allows thousands of multi-agent scenarios to run in parallel. This is what you must build your custom multi-agent autocurriculum experiments on top of.

BenchMARL
https://github.com/facebookresearch/BenchMARL
Python
MIT
2024
MAINTAINED
The authoritative community standard for running and benchmarking Multi-Agent Reinforcement Learning algorithms [cite: 19, 20]. It is backed by TorchRL and tightly integrated with rigorous statistical reporting tools. It runs Multi-Agent Proximal Policy Optimization natively, making it the perfect harness for evaluating policies.

Melting Pot
https://github.com/google-deepmind/meltingpot
Python
Apache 2.0
2024
MAINTAINED
DeepMind's flagship multi-agent suite, offering over 50 substrates and 256 unique test scenarios [cite: 21, 22]. It is used to run zero-shot social generalization experiments. The limitation is that it relies on DeepMind's dmlab2d backend, which can be notoriously finicky to compile outside of their provided Docker containers.

Neural MMO
https://github.com/NeuralMMO/environment
Python
MIT
2024
MAINTAINED
A massively multi-agent environment simulating MMO dynamics [cite: 23, 24]. It runs efficiently and is heavily utilized for research into population dynamics, but it abstracts away physics (no continuous forces, no ramps or boxes) in favor of grid-based resource management.

## PART 4. DATA AND BENCHMARKS

Melting Pot 2.0
https://github.com/google-deepmind/meltingpot
Size: Over 50 games, 256 test populations.
Licence: Apache 2.0
Used to measure: Social generalization and cooperative intelligence [cite: 21, 22]. It tests whether an agent trained in a multi-agent autocurriculum can cooperate with unfamiliar, hold-out policies.
Limitation: Melting Pot suffers from a known overfitting phenomenon. Agents highly optimize for "handshake protocols" with their training partners. When placed with a held-out population, even one behaving optimally, the agents collapse because the specific sequence of expected actions is broken.

Craftax Benchmark
https://github.com/MichaelTMatthews/Craftax
Size: Procedurally generated, unbounded state space.
Licence: MIT
Used to measure: Deep exploration, long-term reasoning, and the effectiveness of autocurricula over 1 billion timesteps [cite: 7]. The field treats Craftax as an authoritative throughput and open-endedness baseline.

TABX Scenario Suite
https://anonymous.4open.science/r/TABX-00CA
Size: Procedurally configurable battlefields and unit compositions.
Licence: UNKNOWN
Used to measure: Emergent tactical coordination in multi-agent continuous-action battlefields under partial observability [cite: 25].

Overcooked Generalisation Challenge
Access via the Cooperative AI framework.
Size: Fixed set of kitchen layouts.
Licence: MIT
Used to measure: Ad-hoc teamwork and curriculum effectiveness.
Limitation: Highly saturated. Standard Deep Q-Learning algorithms have largely solved the basic layouts, and remaining failures are often artifacts of grid-locking rather than a lack of cooperative intelligence [cite: 26, 27].

## PART 5. THE REPRODUCTION RECIPE

Because the original MuJoCo Hide-and-Seek experiment requires infrastructure beyond a single researcher's workstation and lacks a maintained codebase, the field has universally adopted fast-compiled environments to measure the exact same theoretical autocurriculum phenomena. 

The single most reproducible and informative experiment in the modern field is the solving of Craftax-Classic using a Proximal Policy Optimization baseline augmented by a Prioritized Level Replay autocurriculum [cite: 7].

Software and version: Craftax v1.0, using the JAX-native PPO implementation provided in the official repository.
Dataset/Generator: The Craftax-Classic procedural environment generator [cite: 7].
Parameters: 
- Total environment interactions: 1,000,000,000 (1 Billion) [cite: 7].
- Discount factor: 0.99
- Gradient clipping: 0.5 [cite: 28].
- Number of parallel environments: 1024 or 2048 (hardware dependent).
Replicates and seeding: 5 independent replicates, seeded 1 to 5.
Compute cost: Approximately 51 minutes on a single NVIDIA A100 or RTX 4090 GPU [cite: 7].
Expected result: The PPO agent achieves a mean score representing 90 percent of the maximum possible return on the Craftax-Classic logic [cite: 7].
Citation for number: Matthews et al., 2024, arXiv:2402.16801.

Three most common ways people get this experiment wrong:
1. Failing to utilize `jax.jit` compilation over the entire environment step and policy update loop. If any array is passed back to the CPU during the step loop, the execution time balloons from 51 minutes to several days.
2. Misconfiguring the autocurriculum buffer. If Prioritized Level Replay is used but the buffer size is too small, the agent experiences catastrophic forgetting, unlearning basic navigation while trying to learn advanced resource harvesting.
3. Ignoring the auto-reset wrappers. In hardware-accelerated environments, episodes do not halt the batch. They silently reset, and the observation must be correctly masked so the terminal state of the previous episode does not bleed into the value calculation of the next.

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you intend to perfectly merge the physical, continuous-force complexity of the 2019 Hide-and-Seek experiment with the massive throughput of 2026 JAX engineering, you will face a stark gap. 

What must be built: A multi-agent, 3D continuous-physics sandbox (comparable to MuJoCo) written entirely in JAX, specifically architected to expose its internal procedural generation parameters to an adversarial Teacher algorithm for Unsupervised Environment Design.

Interface: 
- Input: A continuous parameter vector from a Teacher algorithm defining the exact dimensions of walls, ramps, and the mass of pushable objects.
- Output: Hardware-vectorized observations, rewards, and continuous physics states for up to 4096 parallel multi-agent games simultaneously, fully compiled via XLA.
- The hard part: Differentiable or purely vectorized physics engines (like Brax) exist, but they are notoriously unstable when dealing with stacked rigid bodies (e.g., agents trying to push a ramp against a wall while standing on a box). Resolving these micro-collisions inside a JAX static graph without causing physics explosions or NaN values is incredibly difficult. 
- Work estimate: 3 to 6 months of intense physics engineering and custom XLA kernel writing.
- Private rebuilding: Several major labs (including DeepMind and OpenAI) maintain highly guarded, proprietary GPU-physics simulators specifically because the open-source community has not coalesced around a stable, multi-agent rigid-body JAX physics standard.

Additionally, a robust continuous-space "Learnability" metric must be written. Current variance-based metrics (like SFL) were designed for environments with binary success/failure outcomes [cite: 6, 9]. Building a metric that calculates the variance of a continuous reward over a dynamically shifting multi-agent policy is a missing component that requires custom implementation.

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

The history of autocurricula is defined by highly publicized triumphs followed by quiet methodological collapse. A practitioner must be deeply aware of the following failures.

The Stagnation of Regret-Based Curriculum:
For years, the field believed that maximizing the "regret" of a proposed environment (the difference between optimal performance and the current agent's performance) was the key to an infinite autocurriculum. It did not work. Standing critiques, specifically from Rutherford et al. in 2024 [cite: 6], proved that practical approximations of regret do not correlate with a task's true learnability. Instead, they strongly correlate with the agent's raw success rate. Teachers trained to maximize regret simply learned to exploit the metric by serving the student environments that were already largely solved, leading to profound learning stagnation [cite: 9]. The critique remains unassailable, forcing the field to pivot toward Variance-based success metrics.

The Failure of Language-Model Physics Design:
Recent attempts to achieve open-endedness by allowing Large Language Models to write Python code to generate new physical environments (e.g., Eurekaverse) have produced stunning demos but fail catastrophically in unconstrained practice [cite: 29]. The standing critique is that LLMs inherently hallucinate physical impossibilities. They frequently generate obstacle courses that are mathematically impassable, wasting millions of GPU cycles as the student agents desperately attempt to solve literally impossible tasks. Without a formal, deterministic verifier, LLM-driven autocurricula collapse under their own generated garbage.

Catastrophic Forgetting in Pure Self-Play:
The narrative that simply putting two competitive teams against each other yields an endless upward spiral of intelligence is false. The negative reality is that agents routinely experience catastrophic forgetting. In Hide-and-Seek, once the hiders learned to completely lock the room, the seekers stopped chasing and unlearned their running skills. If the environment parameters were reset, the advanced seekers would lose to primitive, newly-initialized hiders because they forgot how to pursue moving targets. This is why complex archiving systems and historical policy play (playing against past versions of opponents) must be hard-coded into the training loop, compromising the purity of the "unsupervised" claim.

The Artifact Measurement Critique:
A standing methodological critique of the original multi-agent emergence papers is that the "phases" of intelligence were identified by human observers projecting intention onto algorithmic noise [cite: 1]. The specific strategies (like ramp defense) only emerged reliably under heavy, undisclosed hyperparameter tuning, and the metrics used to classify them were brittle heuristics (e.g., counting how far a box moved). This critique has never been definitively answered, which is why the field largely abandoned emergent competitive evaluation in favor of rigorous, zero-shot transfer benchmarks like Craftax.

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

To run a frontier experiment today as a well-resourced newcomer, you must abandon the legacy Python/MuJoCo stacks and leverage high-throughput computation paired with modern metric redesigns. 

Experiment 1: Visual Inspection of Policies (VIP) over High-Throughput Battle Dynamics
What to do: Integrate an open-weights Vision Language Model with the TABX multi-agent environment. Instead of the Teacher algorithm relying on hacked scalar regret to generate new battle terrains, feed episode video frames directly to the VLM. Prompt the VLM to score whether the agents exhibited novel tactical coordination, and use that signal to mutate the environment parameters for the next generation [cite: 10, 11].
Feasibility: This was impossible two years ago due to the inference latency of VLMs. Today, with lightweight local vision models and JAX environment throughput, the asynchronous evaluation loop is entirely viable.
What it measures: Whether semantic, human-aligned curriculum judgments from a foundation model can prevent the learning stagnation and physics-hacking inherent in scalar autocurricula.
Falsification: If the VLM-guided curriculum converges to a lower zero-shot win rate against held-out heuristic bots than a purely random domain-randomization baseline, the visual-guidance hypothesis is falsified.
Rank: 1 (Highest impact, directly bridges foundation models and MARL).

Experiment 2: Co-Evolving Tasks and Levels (ATLAS) in Cooperative MARL
What to do: Replicate the ATLAS architecture, but instead of applying it to a single agent navigating a grid, apply it to a multi-agent cooperative team in a continuous space. Co-design the physical constraints of the level alongside the formal Reward Machine defining the team's objective [cite: 5, 13].
Feasibility: Feasible now because the mathematics of Reward Machines have been successfully integrated with Unsupervised Environment Design.
What it measures: Whether a multi-agent team can adapt to completely shifting rule sets and topologies faster than they adapt to shifting topologies alone.
Falsification: If the co-evolution of the task parameters causes the multi-agent coordination layer to repeatedly collapse, proving that multi-agent teams require stable reward topologies to maintain communication protocols.
Rank: 2

Experiment 3: Variance-Based Sampling for Learnability in Asymmetric Self-Play
What to do: Apply the "Sampling for Learnability" (SFL) metric, which scores tasks by the variance of their binary success rate rather than regret, to a competitive two-team environment [cite: 6, 9]. 
Feasibility: Highly feasible. SFL has been proven on single-agent robotics and grids, but its application to multi-agent symmetric competition is an open target.
What it measures: Whether replacing regret with variance prevents the cyclical forgetting and strategy stagnation seen in classic hide-and-seek architectures.
Falsification: If the strategy regimes still plateau, indicating that the failure is inherent to the environment's state space capacity rather than the curriculum metric.
Rank: 3

What will NOT work:
Attempting to build a "Hide-and-Seek 2.0" by scaling up PPO inside a high-fidelity Unreal Engine or Unity physics simulation [cite: 30]. While the physics will look incredible, you will be bottlenecked by CPU-GPU transfer times and environment step latencies. The agents will require billions of interactions to learn complex tool use, which will take months of real-time rendering. Furthermore, relying on standard regret metrics to drive the environment complexity will guarantee that your agents plateau on trivial tasks. The frontier belongs entirely to pure-tensor JAX environments guided by variance metrics or foundation model oversight.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6FYM6XyWXJVGOykUiv4lzVqzjDobJDb8gO8qidsHj8Jk1pGGS0Gr2kPpe5y4lP-JNfr9rKTsN-3FV--ZmTW0ITHlYxQmL_dVcyS2A7zwIWFYT60GN_g==)
2. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEX-GvNHK1cgBUk3dVXKgzV20YdXLq3EpCbXOa-QRk-LEdkBMcmW4gRm1iGCcmrNyC0CdOvcBiRLY7k0ecXlUaldYjNDHwkIqQuv3hDVjMLYakfjEc42C2qJQEAq7IvXeEBmIAdGajnoOrJAXYvWyofXAiJ4Ba8BbXhJgaB1Q==)
3. [gwern.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUAjIaOilBEtWkCvkX274Wp-FLmE7dPtD7Pux5k-gLkfjDroyCd2I8GJZDx5yj6wujkJQUhOFS6awZDBEigkDDq-xdzUp0DjjYGjWnYZ1605UCcVuViB-i7rfTbRqbaCVsaL8awbU1evG6aC32_LlgEEgA2Q==)
4. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOAQzlxCfs3McEUMZZJ3J20B8pJjJwac0wcRYMToguRDn4eAXp-xtBsXtHYu1aF6qkQO9xJirDSwHxpii_lZW7i2uCfZ9TKjV1Dc6AN2XtxzqeRbtHqmCn6K48oC07LxmKZcL3)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHdzD7HqhsAWG5EgBqGa18vZkpVxLOqP6ZjoPaVErKJV-3Oom8jCTqGWCfAWStZN7S_7L4H27Kp22kKIPuyTlIbJUSP69xmtt6TXAhjkgDoNQxKo1Wwag8_Q==)
6. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGahZJ8-KUxHliZW5IAIx5E8ZRrAgBg7JZX9f1LLnJbFJatawE6hoPqDxdA3_7jISvs99ErWURI-4kaeKpgYDFtY0MKEa6vB-HPlfJfilS_J_UGFeKSHMtmkf3E9coZFCLOgrMvhSd6sF4M0ZdV54jtBzg=)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9sQYE8sopkZKC_bC11Hl4FP53arcJO0TQVNw_2PxsNIM82b3340Q_2rvU2hs_aUiN3ERxWZqWvGxm37M99c-V_rX_w38sm9D0yE1W7tRIGT-H-XpE4TQewA==)
8. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgxoioZTA0VgJaieLJuQfQs1xMkREjZyprPLGBuO7jjJ_vsEGpRX5Ldff9xBVrMcDUOId3fDaGZvZrG9HevGIVV7njOJ2A4h5XUdShRty1QWUufZ6JSYdgsENlDcEWGQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkrcSh-EFSJZXZsmO5ckLgWb_-4tsQpbm5P4R1zEkp16HyySejxOwfAVqDb8AEyuvGeS5tPYg36aqPNCwIMOaipJ5HRNnh1Q7Ew_AZ11N1V-nzqH83eenlAg==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpvglwLZlLXBI_stVAAuDVWz4C4pmadXlXQwSWSDt6gunKYNeP4kt52zyWBdCkcPcOYKNP8i0DrX12104sU74BocZU67gcxScwS-j-xYxA_Pjdt9uD5se5tg==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJz0rib0UnFQKMK3UOx49Tzb39Fmy8hdCgPqN7oiR6GKJy1EE2CDgfSQ_uGl1VwCvjWIljhQ0OPxoI78GQPBW5qekNNmFeaM7JEQSgx47Vbw2FmZ0KPw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0wCudLkpEpqRuRG2r5uvXrMQj3W_ljV4lJpw483JgdA3ahTkoP0p2ZY2V_yrt9TmiTQJIBdLkOTWJWV8OYs_oizJSZHIxK8kJJrmVubUF9pVXm07W8ow3DA==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrWZoylxLX84SFwXucc-u-GDvtDPrEiWvHg7AULwuVSGytDjGbOe8jbEEGcYT7mKEtuvB5dvSeN13yrvBBX3R4702sPPlQTHOukMOQz0toiui0UYtk1w==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmbZNaV4c0k4iYDG5sgJ0OsQVvjGMHJ9sUkrXalXl5BeQcfjKZvIA3DkIDv4_Uac0rk-AVllXAFSqQIk9T4UjC4kYcRmlDyxFNb5ro2tdZVm_RXCrL3w==)
15. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo8AEVhSgB9QBIBiWFDNskJ7S9IAiltx0TEkQUxM2ejo9tih8Q4Lm1RunJtrIiRdq4erc7ijTKIoYrOZO0k0e-wRxvyAIhPqg9c8pD3Rqjo9IvVpxKIaQZgySu7nY=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9OKC5Y8SpJjERQqtwqdeiPwBmDMYv_PJLgdPA7x_9znbIffroT7PKrwe1-PkZkscuqkfh-V7BVyen38HQRtfv2fy1zNOx6aLM8PGUnwrz5nX6rnIHIw==)
17. [vercel.app](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLH9kXjwvMSehym-wNw7087SJ-M54t7utwm2R5Il9L1XyhTbKoyLjHA_Ewwkx1HKXVeXjHDr--y1j8h_VwtjmbjG38FLPO4sFyTO3yBHCSnZnJs8qvLnjt4PrMFyuzBO0mtwtfXzLvfBRh5XCB3w5QwjhiMi7kusU=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLaAvn6z_WLAHHgwfgcuZhUWdgaMEWopWWE0QDDvPh4iACOABWVAXBBH155nEKUgIYZZ_BTEg6975fOR6h3ollOSgN36uVTkV2rAadK6Pg34F-uZ5V820HCQ==)
19. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbw3AM3LfcKutR6MqpNwmhWaHfsEn7VLil2ms5MJv1L7mxKuha4MS6-6LHW2BlrFoFEWldVPAGtyC1GFUEmn3k5JaRRPAG_2kMrnw72ccHo2BomhMSALxCPx2v9MBl7geAFaQ=)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGm4sd1ALrwXaWwWbx4XYynHXNHSeEiy6AprE-vHZPdi_Dv2jjZjxfW6obeCbLDd-Is9CyGG6YiBqak0JDAsS2R-QprgGbG34TCRdqDSEfQftjtr4lFX45pdA==)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXOpvGqfEd3iA2v5M0yDHeQywncLPEkbZ_pdNbM7kGXhgNJp3PZpdh27ky6GFtq5aaaeQ7S_RgL7RxwvJbPMfsKfrAXhvwKjsl2k5pHsZAB_Mca9lKnxXvtzDTO87Q02EIGPY=)
22. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF614MFGZVTjIzcLMuoSanSCioOEeeRWlg9zpD8P_uKoCOUkJWaOUxpPpwEH0RsPfcqQRM1pFP5CD_HfWmNd-o_O3oJX_aVSOMfa40WPKU2Q6PnwcV2evQy2b7lvGQ=)
23. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVylgsBcNQrkejeqLuNhqbnAMLdRUkmJJSJK8k9I49mhdn5BIb24OEom0Us7koDTfc2T7jru1kYAB2_85idTbf5wCrdlGZsnPZTQGjDNLgnXIm_Wd87UJTQjyqdzux)
24. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlGWi1L8QJgahIakeLiQwiAUP610vORTnU2eTO0IV3FoTGh0E71tVmojR1Ebvb7WZmWNNZ569drrmwEJodwIw-yfLlaSobstjn4RZz6jkewGfJ7VRId04=)
25. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQ9HuYQZGbpKZM6Ela_zcp9jLcJpjUeeIi_7pcFOa0NUL4geahJMKNfPmF4KLGpfTsSL7ja8Pz2OEbUtlFGsDfoz8ZIUAMx6vJHj1S8iN0EUhxfaEJc6O_Vg1jsWkBBtc=)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIXWsjKx_GBJd0iP6N8FscUtZ6hh8OyLNdLEr8mrRcMRcNX4GuDTNgFpZ62Uf7bF0IHzSpf4JPAEO6BU5hnoEjiD4Y3Us2uxcdmtZm4yqx2JFQkbqNKv6Hvc51afDexCMqBHBdYw-GaKcVobS9q3UWQgwIIi9obmJbBHcCSwja1f_z62P8Z_-adLZeJsTnZwi_J_sDu4wwzCINlo2aiUE3k4YQ)
27. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAW4w7ux6JQsXqPK76U_UoKcAFfXcbOplDxzUjXq6kHyC9gPJiE4Uors9xpEbG5R37VcwsLOeJ-u6hR1i5ZI_HapudEy9_usag2AdV4ZCK9p1nDnyoA6juTMg7_yc=)
28. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqZWYLTil5u8OFlifAHksCxzjDMm4oo_4ET5_lo9bvy4KKCVSnGKMxCV-7jXdx5r_Smp2H_70FGKtBMHe_bXlNsoif1iMsOWJ9FKEN-BIx_U0k2ORpXoKDtln0q5QdiDXIjhbLw55HxtXF5_eA8KQqE93RWlrDx7AklIdGDUU3-5xbCq2zjpQFe_OxR08_e2OI8Pre-dBqbrtR)
29. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXRD0sXzDup315sGZfZNkQv6iQDBq4O5cGVI1T70fEmE7Gs6W-F8INnI3g4Q5c4wDWSYQklG19lZbjGSdavBqQi42ZjWh2xenUOGBwgot7L2EnhGnHFW0H-vzqXSoxXHvQ1N6LOpUzrMQYlIna5wfc5MzVmgGfrvrWcxNyo3sZ6w==)
30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH3nDGPNzxuT0hZdKhYand7d3PfcwoIkLgLS7rofzhKTiUMvQXWMNlcdEe1t9xPiVQ6ZJ6EEIRZpLiPJ5gy-y5CkefrgN1nXVfH-n9qPk04OTTHWp95nXi9Op1yJrgj8gigDJQz7XCj-Y=)


# Prompt 46: Learning-to-Search

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdmMXVmYXMtakFfVzFfUFVQOTUtb3lRSRIXZjF1ZmFzLWpBX1cxX1BVUDk1LW95UUk
**Elapsed:** 304s

---

# FRONTIER PRACTITIONER DOSSIER: Learning-to-Search

Key Points
* The fundamental mechanism of Learning-to-Search (L2S) and DAgger—converting imitation into a no-regret online learning problem to break quadratic error compounding—remains theoretically sound and practically essential in 2026 [cite: 1, 2]. 
* The field has effectively bifurcated and merged into two modern domains: LLM Agent Post-Training (under the moniker On-Policy Distillation) and Robot Learning (as Interactive Imitation Learning) [cite: 3, 4].
* The classical L2S software ecosystem is largely dormant, replaced by distributed asynchronous architectures built around HuggingFace Hub and modern reinforcement learning libraries [cite: 5, 6].
* Current frontier research is focused on decoupling trajectory generation from divergence metrics, mitigating "causal confusion," and escaping local optima induced by suboptimal teachers [cite: 7, 8].

The State of the Art
Research suggests that while the foundational mathematics of DAgger are settled, its application at scale is highly contested. The most active debates revolve around the direction of the Kullback-Leibler divergence used for token-level supervision, and the mechanisms by which student policies can safely explore without being trapped in degenerate agreement loops with their teachers [cite: 8, 9]. 

The Practitioner's Pathway
For an in-silico computational scientist entering this space, the immediate goal is not to write a new L2S algorithm from scratch, but to build an asynchronous rollout-and-supervision flywheel. The evidence leans toward utilizing multi-turn language model agents in environments like SWE-bench, applying DAgger-style teacher-interleaved rollouts to achieve state-of-the-art reasoning capabilities [cite: 10, 11].

## PART 1. THE FIELD IN 2026, AND ITS FRONTIER

Learning-to-Search in 2026 is no longer a standalone discipline. It has been thoroughly absorbed into two distinct fields: LLM Post-Training (often branded as On-Policy Distillation or iterative Direct Preference Optimization) and Embodied AI (branded as Interactive Imitation Learning or Human-In-the-Loop DAgger) [cite: 3, 4]. What was lost in this merge was the explicit structured-prediction framing of the mid-2010s, where features were engineered and search spaces were explicitly defined graphs. Today, the search space is the autoregressive decoding tree of a transformer, and the transition function is the prompt-to-response generation step [cite: 12]. 

Your description of the mechanism is exactly correct. The core trick of DAgger is on-policy state coverage: by rolling out a mixture policy, the student visits states it is actually likely to induce during deployment, and the teacher provides corrective labels at those specific states [cite: 1, 10]. Because the student trains on its own marginal state distribution, the evaluation matches the training distribution, converting the imitation learning problem into a no-regret online learning problem [cite: 2]. This limits the error scaling with respect to the task horizon to a linear boundary, rather than the quadratic compounding error that plagues standard off-policy behavioral cloning [cite: 1, 13].

What is SETTLED: The theoretical necessity of on-policy data collection for long-horizon sequential decision making is unquestioned. Standard supervised fine-tuning (SFT) on fixed expert traces is universally acknowledged to fail on long horizons due to covariate shift [cite: 4, 14].

What is CONTESTED: The exact mathematical objective used to distill the teacher's knowledge once the on-policy trajectory is generated. There is a live disagreement between proponents of forward-KL (which behaves like SFT with soft targets) and reverse-KL (which behaves like policy-gradient Reinforcement Learning with a dense teacher-student log-ratio reward) [cite: 3, 8]. 

What is OPEN: Escaping the "KL Agreement Trap" and overcoming causal confusion. When a high-capacity student is trained via DAgger, it frequently learns to avoid states where it might disagree with the teacher, or it latches onto nuisance variables (like stylistic tics) rather than the causal reasoning path [cite: 7, 9]. Furthermore, dealing with suboptimal teachers remains an open theoretical gap; DAgger strictly bounds the student to the teacher's performance, which is a liability if the teacher is flawed [cite: 15, 16].

## PART 2. THE READING LIST THAT ACTUALLY MATTERS

FOUNDATIONAL SOURCES

Authors: Ross, S., Gordon, G. J., and Bagnell, J. A.
Year: 2011
Title: A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning
Venue: AISTATS
Identifier: arXiv:1011.0686
The paper that introduces DAgger, providing the mathematical proof that iterative dataset aggregation reduces the compounding error of imitation learning from quadratic to linear with respect to the task horizon [cite: 1, 2].

Authors: Daume III, H., Langford, J., and Marcu, D.
Year: 2009
Title: Search-based structured prediction
Venue: Machine Learning Journal
Identifier: DOI 10.1007/s10994-009-5106-x
Introduces Searn, the direct predecessor to DAgger. A practitioner must read this to understand how complex structured prediction problems can be cleanly reduced to binary classification tasks via a learned heuristic [cite: 17, 18].

Authors: Chang, K.-W., Krishnamurthy, A., Agarwal, A., Daume III, H., and Langford, J.
Year: 2015
Title: Learning to Search Better Than Your Teacher
Venue: ICML
Identifier: arXiv:1502.02206
Introduces LOLS (Locally Optimal Learning to Search), demonstrating the critical flaw in DAgger: if the reference policy is suboptimal, DAgger will force the learner to mimic bad decisions. LOLS incorporates one-step deviations to guarantee local optimality even with a poor teacher [cite: 15, 19].

Authors: de Haan, P., Jayaraman, D., and Levine, S.
Year: 2019
Title: Causal Confusion in Imitation Learning
Venue: NeurIPS
Identifier: arXiv:1905.11979
Identifies "causal misidentification," a phenomenon where giving an imitation learning policy more information actually degrades performance because the policy latches onto effects rather than causes. Crucial for understanding why simple DAgger sometimes fails in complex state spaces [cite: 7, 20].

CURRENT SOURCES (2023-2026)

Authors: Li, C., Qiang, R., Huang, J., Gao, C., Zhang, C., He, N., and Dai, B.
Year: 2026
Title: Revisiting DAgger in the Era of LLM-Agents
Venue: arXiv
Identifier: arXiv:2605.12913
Adapts DAgger to multi-turn language model agents. It proves that teacher-interleaved trajectory collection mitigates covariate shift in long-horizon coding tasks, allowing a 4B model to outperform 8B systems on SWE-bench [cite: 10, 11].

Authors: Zhao, A., Xin, H., Fan, Y., Tong, J., Li, W., and Shen, X.
Year: 2026
Title: Decoupling KL and Trajectories: A Unified Perspective for SFT, DAgger, Offline RL, and OPD in LLM Distillation
Venue: arXiv
Identifier: arXiv:2605.16826
The best modern survey and unification of the field. It dissects On-Policy Distillation into prefix sources and KL directions, proving that DAgger-style on-policy SFT and offline-RL style distillation are just different axes of the same objective [cite: 3, 8].

Authors: Yuan, W., Pang, R. Y., Cho, K., Sukhbaatar, S., Xu, J., and Weston, J.
Year: 2024
Title: Self-Rewarding Language Models
Venue: arXiv
Identifier: arXiv:2401.10020
Demonstrates how to eliminate the external teacher entirely. The model acts as its own DAgger oracle via LLM-as-a-Judge prompting, creating a continuous self-alignment loop using iterative Direct Preference Optimization [cite: 21, 22].

Authors: Welte, E., and Rayyes, R.
Year: 2025
Title: Interactive imitation learning for dexterous robotic manipulation: challenges and perspectives-a survey
Venue: Frontiers in Robotics and AI
Identifier: DOI 10.3389/frobt.2025.1682437
The single best survey on the physical embodiment side of DAgger. It maps out how interactive imitation learning handles the high-dimensional continuous control problems that text-based LLMs avoid [cite: 4, 23].

## PART 3. SOFTWARE I CAN ACTUALLY RUN

imitation
URL: https://github.com/HumanCompatibleAI/imitation
Language: Python
Licence: MIT
Year: 2024
Maturity: MAINTAINED
This is the community standard for algorithmic baselines. You can use it today to run a mathematically pure implementation of DAgger on Gym environments like CartPole or continuous control environments like HalfCheetah. It is built on Stable Baselines 3. Known limitations: It is heavily coupled to traditional MDP reinforcement learning interfaces and does not easily scale to autoregressive transformer token generation without significant hacking [cite: 24, 25].

lerobot
URL: https://github.com/huggingface/lerobot
Language: Python
Licence: Apache 2.0
Year: 2026
Maturity: MAINTAINED
The state-of-the-art framework for Human-in-the-Loop (HIL) DAgger in embodied AI. As of version 0.6.0, it contains a dedicated DAgger rollout strategy that handles asynchronous pauses, leader-follower interpolation, and trajectory merging. You can use it to train Vision-Language-Action (VLA) models on custom datasets. Gotcha: The DAgger pipeline requires specific hardware setups (e.g., SO-ARM100) with programmatic torque toggles to handle the autonomous-to-teleoperation handoffs smoothly [cite: 26, 27].

Decoupled-Distill
URL: https://github.com/EIT-NLP/Decoupled-Distill
Language: Python
Licence: UNCONFIRMED
Year: 2026
Maturity: MAINTAINED
The reference implementation for the 2026 paper "Decoupling KL and Trajectories". It provides the scaffolding to run DAgger-style on-policy SFT for language models on mathematical reasoning datasets. It is highly optimized, reducing per-token memory overhead from O(V) intermediates to O(1) running statistics [cite: 8, 28]. Limitation: Heavily specialized for Qwen architectures and reasoning tasks.

Vowpal Wabbit
URL: https://github.com/VowpalWabbit/vowpal_wabbit
Language: C++
Licence: BSD
Year: 2024
Maturity: DORMANT
This is the historical home of Learning-to-Search (Searn, LOLS). It contains heavily optimized C++ reductions of structured prediction to contextual bandits. While the overall repository is maintained for ad-tech and contextual bandits, the specific Learning-to-Search subsystem has seen little architectural modernization since the mid-2010s [cite: 5, 29]. Do not try to run modern deep learning experiments here.

## PART 4. DATA AND BENCHMARKS

SWE-bench Verified
URL: https://www.epoch.ai/benchmarks/swe-bench-verified
Size: 500 instances
Licence: MIT
Used to measure the ability of an LLM agent to solve real-world GitHub issues by generating and applying patches to a codebase. The field treats this as authoritative for long-horizon agentic capabilities. Important contamination note: Because these are real, historical GitHub issues from popular Python repositories like Django and scikit-learn, the solutions exist in the pre-training data of frontier models. Furthermore, recent audits suggest that even the "Verified" subset retains some underspecified tests. It remains the gold standard for measuring DAgger agent success, but absolute scores above 40 percent should be viewed skeptically [cite: 30, 31].

LeRobot Behavior1k and SO-101 Datasets
URL: https://huggingface.co/lerobot
Size: Terabytes of video and proprioceptive state data
Licence: Apache 2.0 / CC-BY-4.0
Used to measure continuous control imitation learning. This is the community standard for visual-motor policies. It is used to pre-train base policies before fine-tuning them via HIL-DAgger [cite: 32, 33].

OpenAssistant / UltraFeedback
URL: HuggingFace Hub
Size: 10000 to 100000 preference pairs
Licence: Various open licences
Used to measure basic preference alignment. These datasets are frequently used to cold-start the reward models in iterative DPO or Self-Rewarding Language Model experiments before the models begin generating their own on-policy states [cite: 34].

## PART 5. THE REPRODUCTION RECIPE

The most informative experiment to run in 2026 is the on-policy teacher-interleaved DAgger rollout for multi-turn language agents, specifically reproducing the setup from "Revisiting DAgger in the Era of LLM-Agents" [cite: 10]. 

Software and Version:
OpenHands (formerly OpenDevin) framework for the agent scaffolding.
vLLM for serving the models.
Decoupled-Distill codebase for the actual gradient updates.

Dataset:
SWE-bench Verified (500 instances).

Parameters and Values:
Student model: Qwen3-8B.
Teacher/Oracle model: Qwen3-72B (or GPT-4o).
Beta decay schedule: Start at beta 0.8 (taking teacher action 80 percent of the time), decaying linearly to 0.1 over 5 iterations.
Context window: 32000 tokens.
Max interaction turns per issue: 50.
Training length curriculum: Entropy-gated, starting at 128 tokens and expanding to 4096 tokens only when predictive entropy remains stable.

Replicates and Seeding:
3 independent replicates with different global seeds for the trajectory generation phase, as sampling variance in the student heavily impacts the state distribution [cite: 8, 10].

Approximate Compute Cost:
Generation/Rollout phase: 300 to 500 A100 GPU hours (generating multi-turn rollouts is heavily bottlenecked by autoregressive decoding of the teacher/student mixture).
Training phase: 50 A100 GPU hours per iteration.

Expected Result:
The baseline Supervised Fine-Tuning (SFT) on the teacher's off-policy traces will achieve roughly 26.2 percent resolution rate on SWE-bench Verified. The DAgger-trained student should achieve approximately 29.8 percent, a gain of 3.6 points. The per-step test loss evaluated on the student's own rollout trajectories will scale linearly with the number of turns, whereas the SFT model's loss will compound quadratically and fail catastrophically after turn 15 [cite: 10, 11].

Three Most Common Ways People Get This Wrong:
1. Data Discarding: Practitioners often discard the dataset from iteration i when moving to iteration i+1. DAgger requires Dataset Aggregation; you must train on the union of all data collected across all previous rounds, optionally applying an exponential decay factor to older data to manage disk space, but never fully dropping it [cite: 1, 6].
2. Off-Policy Evaluation: Evaluating the student's test loss against the teacher's static dataset. The entire point of DAgger is to evaluate the student on the states the student visits. If you measure loss on off-policy traces, DAgger will look worse than SFT [cite: 12].
3. The KL Agreement Trap: If the teacher and student are interleaved too passively, the student learns to output low-confidence tokens so the teacher takes over, or learns to mimic the teacher's formatting without learning the reasoning. This leads to early entropy collapse [cite: 9].

## PART 6. WHAT DOES NOT EXIST AND WOULD HAVE TO BE BUILT

If you want to push the frontier of in-silico DAgger for LLM agents, you will have to build a Distributed Asynchronous Advantage-Gated Flywheel. 

Currently, off-the-shelf tools either assume a synchronous step-by-step Markov Decision Process (like the `imitation` library) or are hardcoded for specific robotic teleoperation (like `lerobot`). For LLM reasoning, training and trajectory rollout run at vastly different speeds. 

What goes in:
A cluster of rollout worker nodes generating text trajectories via an API-gated teacher model and a locally hosted student model.
A central training node holding the student weights.

What comes out:
A continuous stream of trajectory prefixes, logged to a central HuggingFace Hub dataset or Redis queue, annotated with token-level forward-KL divergences. The training node continuously pulls this dataset, computes the DAgger updates, and pushes updated student weights back to the rollout workers.

The hard part:
State deduplication and trust-region filtering. In text generation, "states" are arbitrary string prefixes. You must build a mechanism that detects when a rollout worker is trapped in a loop (e.g., repeating the same shell command in SWE-bench) and programmatically terminates the rollout to avoid flooding the aggregation buffer with degenerate supervision [cite: 9]. Furthermore, you must decouple the token-level KL direction from the prefix source on the fly, dynamically switching between forward-KL for novel states and reverse-KL for well-understood states [cite: 3]. 

Roughly how much work it is:
A competent computational scientist could build the orchestrator in roughly 6 to 8 weeks. The signal that this is a real gap is that multiple frontier labs (Physical Intelligence, HuggingFace, Georgia Tech) have all built proprietary, internal asynchronous hubs to handle multi-machine rollout-and-train loops specifically because no open standard exists for asynchronous LLM DAgger [cite: 6, 11].

## PART 7. NEGATIVE RESULTS, FAILED PROGRAMMES, AND STANDING CRITIQUES

Causal Confusion (The Core Failure Mode)
The most profound negative result in the imitation learning field is "Causal Confusion," formalized by de Haan et al. in 2019 [cite: 7]. They demonstrated that giving an imitation learning policy access to more historical state information often degrades performance. The policy learns spurious correlations—for example, it learns that applying the brakes is highly correlated with the dashboard brake light being on. When it drives, it waits for the brake light to turn on before braking, crashing the car. In LLM agents, this manifests as the student learning the teacher's syntactical formatting (e.g., always wrapping thoughts in specific XML tags) rather than the underlying search logic. The critique stands: pure DAgger does not inherently solve causal misidentification. It was partially answered by implementing targeted interventions (forcing the model to act without the confounding variables to see if it still knows what to do), but causal confusion remains a massive hurdle [cite: 20, 35].

The Suboptimal Teacher Critique (LOLS)
DAgger's mathematical guarantees assume the oracle is optimal. In 2015, Chang et al. proved that if the teacher makes mistakes, DAgger's regret bounds force the student to eagerly learn those mistakes. A student trained by DAgger can never surpass its teacher; it will asymptotically approach the teacher's suboptimal ceiling [cite: 16, 19]. This was answered by the development of LOLS (Locally Optimal Learning to Search), which mixes in the student's own rollouts to find one-step deviations that yield higher rewards than the teacher's choice. However, in modern LLM distillation, LOLS is rarely used because calculating exact one-step deviation rewards across a vocabulary of 100000 tokens is computationally infeasible.

The KL Agreement Trap and Outcome-Confounded Local Supervision
Recent 2026 literature highlights a critical failure in scaling On-Policy Distillation. When applying DAgger to LLMs using token-level KL matching, researchers discovered that models fall into the "KL Agreement Trap" [cite: 9]. The student learns to generate highly conservative, low-entropy prefixes that the teacher will trivially agree with. Furthermore, crossing token-level teacher-student divergence with final-answer correctness revealed that local divergence cannot localize where a trajectory actually became unrecoverable. Methods that blindly match teacher logits on student trajectories fail to correct the specific pivotal reasoning fork that doomed the rollout. This critique is currently unanswered and is the subject of intense ongoing research [cite: 9].

Failed Programmes: Pure Behavioural Cloning on Long Horizons
The most replicated negative result is that scaling up the dataset size for pure off-policy Supervised Fine Tuning (Behavioral Cloning) does not solve compounding errors for long-horizon agentic tasks. As demonstrated repeatedly on SWE-bench and robotic manipulation, beyond a certain horizon (typically 10 to 15 actions), the state distribution shifts so far from the training manifold that the model enters out-of-distribution states and hallucinates catastrophically. The idea that "more data solves covariate shift" has been falsified [cite: 4, 14].

## PART 8. WHERE AN ENTRANT SHOULD ACTUALLY AIM IN 2026

Given the compute, the coding ability, and the in-silico focus, here are the specific experiments a well-resourced newcomer should execute, ranked by impact.

1. The Entropy-Gated Causal DAgger Experiment
What it is: Combine the entropy-gated length curriculum from Zhao (2026) with the causal intervention framework of de Haan (2019). Run a DAgger loop on a math reasoning dataset, but actively mask out intermediate scratchpad tokens during the teacher query phase to see if the teacher's prediction relies on spurious chain-of-thought correlations. 
Why it is feasible now: The decoupling of KL and trajectories allows for precise token-level manipulation that was impossible when DAgger was treated as a monolithic objective [cite: 3]. 
What it measures: The ratio of true causal reasoning to stylistic memorization in distilled LLMs.
Falsification: If masking the intermediate stylistic tokens does not increase the teacher-student divergence, the idea that causal confusion is driven by stylistic artifacts is falsified.

2. Process-Based Self-Rewarding DAgger
What it is: Implement the DAgger algorithm, but entirely eliminate the external teacher. Use a frozen version of the model to generate the rollouts, and use a step-wise LLM-as-a-Judge prompt to provide the corrective labels at each visited state [cite: 21, 36]. 
Why it is feasible now: Models like Llama-3 and Qwen3 now possess sufficient baseline reasoning to act as reliable judges of their own intermediate states, a capability that did not exist in open weights prior to 2024.
What it measures: The self-improvement ceiling of an isolated model on SWE-bench without external frontier-model API calls.
Falsification: If the model's test loss diverges after 3 iterations of self-aggregation, it proves that the model's internal reward signal is not robust enough to overcome its own distribution shift.

3. Trust-Region On-Policy Distillation
What it is: Restrict reverse-KL distillation strictly to teacher-reliable trust regions on student rollouts. If the student wanders into a state where the teacher's predictive entropy spikes (indicating the teacher is also confused), apply forward-KL to mismatched outlier tokens instead, or terminate the rollout entirely [cite: 9].
Why it is feasible now: Fast inference engines (vLLM) allow real-time entropy calculation during the generation phase to dynamically gate the loss function.
What it measures: Training stability and response length inflation compared to standard DAgger.

What will NOT work:
Attempting to scale DAgger by using a larger context window to feed the model more historical trajectory data. As proven by the causal confusion literature, feeding a model more historical observation data in an imitation learning setup exacerbates nuisance-variable correlation [cite: 7, 37]. The model will simply learn to correlate its next action with irrelevant tokens deep in its context window, accelerating the KL Agreement Trap and degrading out-of-distribution generalization. Focus on the quality of the state visits and the precision of the KL objective, not the size of the observation history.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEonR-OyvpmeyPGI5IxBHf276oX3Uc-Ops4FoTNSmGmcpWc_-Gtp_jK0xInPJinQkK6-UCVjgz3mRQiss0L0wgbkw6i6HnP1BYsK_AoaQovBDW18R0x)
2. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvg44I0JbpWVspwAu1Z-AQWkNt3QglvsfS7zr7_pTFzoJJ4cTGNXhp17O1sZK0b64YVXsD6AjuYmpSWm1RnPcHSqWiHeLsoZkFk6pv81DaUuPNcULM4aIcXRouVw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNidu9CUDW-neEfB3PIw8wFiFSNPfKrsX9bUv-poKxZbulUv9MWOdiFAN0Y766BfQums83Xg5eo3pXDOf9T2i_hIuWw-fKszoXDcjxUcD4BbD1hztzsg==)
4. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4bXOlHRnq8w1ylZtYT-YhFg2xL0Xi6K4OHe2RovvbG6ZY9_FobmFMJise2HJ3BCoq69CQU3p4v2QHOYH9FHV3pc8l0jnOz9uo3hrIM0K_o_YtYDXhj89fusCttDfeU04JwozgIN6MFg4gWIUabxz9gjQLbljDPJNFKRweJztKNJKTmpCUQRQQmjOTluIqstpKhco=)
5. [vowpalwabbit.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWucxBnXtT0rTrpFV_5mgdd7Nvb8B31LC8IbHIbJSJGXTF75PLGdsKwLSbz2ef2DIHyV92-Hm7LqsCky7QemZY0eetwIfvlT-XOIdC7QH263ifu9J2PpKMctiRKw==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeJ8fW7v3NRveHvnICps4ak2aWNCg_wBVtle8xiMDGvvIh9j05AsDJItqwBJQd7UnhES1sk9Q_B_UpzVnH_zIP-ZKsydss_OzyM_agmri79QAcPbPBq4LZuw==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDh-wfve2gtFr4HBwIhNm7trUgY04WGapwq_7tO720tEjM9QEKCVy38R26KToORMdfg2d3BMP4ebHOrN5lyo7cZpvM-RfW0tQ7vKYHGJoIkpUOG8lOcg==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeuacCtLjqFBvSaCaE8osbbJHYrkYSD4mJOvRAQsbWWHd6zkObR9ptZM5zL-08z3Rd5PiVq9p41pJ_JMEPvf1jBmhS8RU6duG6lRdf_fwEI_4FQO1NKA==)
9. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaj5ns1b0m8Qe7ukCaNU-qX9MXH_LRl6aS0CQ3VwZ4mhKwjO4Q_2Ji57JNF7xXbUjTAR4rSx2gWCi2j71t16qzlywD9hit8ABHYsjOcm66kBwG_Ygf9ghWuTj6-PI5Zq2t2QoznCvFk12DoShPFJMIr1Bf)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGr-0FQC2-RN_rHG-jAkyILNkDauWdhzEioHzMmDApLx46mfPbKg1tuzHdldFxAL1OqC5nw8M1vR2zIZCbYbLS8PFq1xsM3SpvlLEWIvGXMzwAgNs3jFdEXbw==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpq47b-ZrzSqOQvbvtIP_Cakb-Kec5ryyOpdv-BZCWEEb9STZRvo6ow8iO8xRFzqUvKnRwOb4seW1rU9FRzn4h5T_a-15SvOoPjd4kOam7ohhSePZCMw==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHE84A9YoeM_hztdXRKSG9ajJl8-CmbgdVCGyzwoHsCBykFznv6_NoPU82WRbB8kZe7qnNwHaqa4ozHP5NBI6vOMzh0sQlKKKWcOIhOAnF0oJyI9HwCTArK9Q==)
13. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9GVhx8ibyXOKhbyFV7WptwSoH53FfkqJnXS8XZGHB9fZVw4IgURr6XmkM_jBnQcjfjlrZTv9d2Tz16wJJ6-ykCADbKHydwvBi0OXpxx8kwT2YdId_gzRUy2V1D2M=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeWgHNmJ416O-MxmvPcn24VjIhd85fxFn5-LtmIwsdDfKVQiWPirfeKCJJMDU1lfVUYeQ01gb4YyOV6RaH57t1pELOdPGD9Bv3vtAyQ4MJomMfd5FW1g==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-lhkgHMl3t6PTTtvc4wuobP5amK3YQzYPuBPl7zIrthAPuB4sOPGUzqtSKmP6QC5esSL4SI2LJp0vHIAcJjQ6FY78nxr7PApWk86Htia0ceDI22-ajQ==)
16. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElQCYpNLCJ6G3rsGPtnLOfyKNM8DyBA4Y669GPzK5gzvLwR_7LJ3NYugVHatn4JhKLqDzRa0xLRiho1P97iuiYy2P_wwaU_daRnn8cUh1XMAJ4JsRN8ByDveF2xmcM9yYNs88=)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMzQI7TPLBQc_5LUAJlyAS_M2-o8cCD36o3wnQhWK3GTwqPhYjOt-Vrsnk22I6J_w7gmHrx_C_tDVq1QrTiKhSgXQ3VFmKmMgEpL9ju1Ajzq2RFHrk)
18. [proquest.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHws8oSPjBdhI0jT_1v_24i_70ks6ilhAqg-frzlEZMS44fo1yzH-M5HqZeMSI72N8WA7LYJCNtEkPbDnCBnQ5rtqllelYq9cVrUjfYs5dr6UtZ6M2NmvQafXAwGtBcx3hDqYVzRbCVB0SrAu_xdjAuPEKtxJwxu-yR0zJKn4Gekol6QbXSh3uxBVT8_W5ccwY7D1dY5VTJX-y5mv4=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaONlxI3QS9kqwjSA-IaYuAS2lNQDnCMgRlJNJowX3HZb3wUhvA-CsK6dayr7G6ev0reDyzl_SnMklCWP8ym8FSqcI0N1oj5cGXRbFSD0ArGE_cIZAXQ==)
20. [upenn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFXHsYp33Ku3NgdhkOHSSmlXvZe2PC8zulmFtgbegpMhCunFDu0lGLl9LW1xt1qaGZvBbQizlajH0orFpT6M5VWbIVgisXV81cfPVlKpc-NR3c5o5c5AFS8VD0QqPAN3QrUs4MqkKaxgP8XF-GHyvcvHbshxglOKn4C1tdqGIWCrdmD3UnrIICqqJRKEsK84bQHu9yetQQnrwLONfPAYloNXwy6BEXn5A1)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFd4eOnQolyjcmg232wTX9OLn_pqZu8M1Pq1lASHszk42rOAjaZtXszPcYaeNMfe7qltMfeotng8JxK-oCzvnVs8NTkp8105QneVbDX4xM_jPSRv_KiYsNO68c=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEG2C4K0pvUfXUzGtf_-pKXrbo-PedKekkK8HDEs1WTFc3E8L2K1I1Tob4RkF7ERjtvNUUt3DRP7cn5c5GMUfX6PCFxuxcrB_i1HiWxFIa3JJ9-QW33xg==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQS3MWtq_RCACzVZTKMztjx6mWGTuZkXh5Lk6RaYxuDZpNUqwiqd4MDb7Og8CZ2Pn58KwIE5w8Cga64ss4RM_6PoQq4aQeGMWbZe_4zXa-EVcQB-ZxuMmYE-YT2qS20iKfD9SViOgi6YjJCXtj4hgIUn02DkZwmdRIyxt6FeevVchqMPrxC5E22yLr-cOhBDWHdgr0yGaGou5PuG7bacor7Z256W3XwnNcA4lRb1q9H6OOyeOb9K9CdSQ5zrx0Gp4fXyEW1O9ofHCbWffTDGoT)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBayxJXnMDwUe7favyGneXKT052TigiUpdKoGql4jabPUrUOXwzfDwgXwF1KJjlOJDcU4ltL0tcd4EePWbv-kHmNI_zk9IFuU_BlJVfIvXacGauBDPrE817EfZMRprnKwBPO9a)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-awqwB2qR061YA95BgMmDAOLacGzelny40D41Z981Bi-BMipY2YvtZTocPapmZwX7Gk2T9PoKIuC8zPb-cXhq7QBSIEW-c3MC8Hd03a3RkWiF_Dt5SMte_4JMapeTXkoX_w==)
26. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE06_FcKJFrEJKeFZ-HQFqrvDgtVy219KmUIkSoUs1ymfMoQ5P_N_op62M0lX3gfKqUc2J7pPevhyulRBttd5sXKjPr5RH2-h0_0OYhePrOchxrFSKkP1A0J-Z58I58chGxlCM6F376oSLDKlTaggkTR0ZLqy9SRMDUavq1s13aBAD_sYRIl5RhEHM=)
27. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlj98iA_yJFVIekwZrhBecwmSSVkMaY-HEMttzgVH2-4nA8QDE2ZOrNZMmiRUEDdzZNXRpQr4prGBT8RU3gGfeNvQ0lGeu6FFk7b7ZoU439AWvV7fwdQYW_dyloHpMV0tKOvWpH8MWHQ==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4mNyghR5-Cjtf2edRPf5F2gJ7bMhZ_jPCNpiKY8fg80P-IMG__f_KpcKGemS7GT9pSLQ6khaifUZUd0hmZzrTu6JF7NVzKHFJI9s-eA24raHpkoJSh4TvKw==)
29. [hunch.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbgRQr65x7P2cisljDaElUHyx3ZZfjg4sm2CemD089AXdRAy4ZmoqWKWkJcVisZZ4wBvPiZX1IYQnccMYuY_52oI_STO0vAtBsXPqeDyNRdlI=)
30. [epoch.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9vlD5k4PKhVdmelgKlxJycDsNreMfx5ilKjSBpE9mu_1TwTGd2BoX2mPZH4GFdrzmWboAv79ag4tMvJoA53OHecDqTq6sRhe56uK2k4pGTF2EaYLUgFiJw7A-lOjkmu3eKjdF)
31. [steel.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHD3qSV5Cz4ur71F74gbGuFasmS44RqK8ZFIzGL0iwmYRWP_VsLs85s3qF104sTA6fKkWkpNKNhg52WKKdYW9gGph9Py877G4HJk4pPRNbkSw4tXHzVAn9jrz-EvKh5vKerZgPTzf4glpD-4hgxQuAKTJdxXA==)
32. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFp0kJ6mW5Ihl5H6lM7R1jAfMMAvEJnDuv_iihlAdmoH2juD4J95TTAvWGSFEhEA1rZbYpCVZwgA8CN_IwPB2CpUlqIQYLHjSAFf_Kb8tV2Mtd1oHHNFLN3lDTllWfwOSSgQGQ2EHw=)
33. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7Sq9WkIITMzzWpcq3EK4eEFDvK7NJz3vW4ox81BAt6VC4ztA4oU8wwjnTXcMV4aPFZDymizb_zjVFS01PYAo0_SMm-MK2cLFz0-yMk8P9ZdkdB74NQ2WvoNZFFHa6G_4ZY0HJ3OQ-Xw==)
34. [oxen.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEipo5Y2bsSbWRFlSshWF4EyHJJYNQmjeI4_pGG-E7-TzKWQEVrqgDhMYn3lIsm3exXm9lb-xPOFldEH_DTYm42PvFgtVEQ-GHWlG1bgu7zpmAsUdJcPpyYsitBwbN8i1a2vYbOTzZXqco40qzLNtI3qg242bQrHYKL)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7BNmSP1hJBc2lg7l8n3x5SmTdS0Q_X-3AEXb0cbkXDcDwAaTKkRptqWmXjoDf6xtpoA6vHYsANQcie4c9AsZKB1ttlrOI0JzT6eWiMovBqGiDNUOg2w==)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7v8L1afq32xWfgHmh7fRxjc9oWEmRO75nQqzQiObkYEjH6TsuzWhEbTJwSJ4im5FBcCS8TEgeRogBFpxRPuTImqXWKjPFT12zEflR4d9s-hXPHxTvEQ==)
37. [almond.bot](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZR7Jtcw6m9SUtKwFPALSORk68hqwZcxfvYPJpZwat4u64fVyBRkIwikknTQeMEqVUN0LkaLF1yGzDgITOjnGxrk1THmkn4ZcRyj86KFGyOSKGzhybngeXvU2aPTE-K-RRatXy9ow=)


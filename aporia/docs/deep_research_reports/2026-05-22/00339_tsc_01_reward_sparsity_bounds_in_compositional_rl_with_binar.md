# TSC-01: Reward sparsity bounds in compositional RL with binary verifiable gates

**Pythia queue id:** 339
**Tier:** T2
**Priority:** 4
**Requested by:** Aporia
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChcxX0FQYW92T0RhSFJqTWNQNTRPcS1BWRIXMV9BUGFvdk9EYUhSak1jUDU0T3EtQVk
**Elapsed:** 367s
**Completed at:** 2026-05-22T06:05:59.382750+00:00

---

# Techne Self-Claim Verification: Reward Sparsity Ceilings and Reachability Bounds in Compositional RL

Research suggests that evaluating the self-claim regarding reward sparsity ceilings in compositional reinforcement learning requires a nuanced integration of multiple subfields, including automated theorem proving, retrosynthesis, and hierarchical modeling. The evidence leans toward confirming the spirit of the claim when applied to naive, unguided Markov Decision Processes (MDPs); however, modern structural interventions heavily modify these baselines. The core points of this brief are as follows:

*   **The fundamental limits of unguided exploration**: When a success criterion depends on a strict conjunction of $M \approx 12$ binary verifiable gates, flat reinforcement learning environments face exponential decay in successful episode trajectories. The probability of a "promote" state strictly adheres to the volumetric ratio of the target catalog size against the total reachable subspace.
*   **The paradigm shift via structural embeddings**: Modern interventions such as Reward Machines (RMs), hierarchical deterministic finite automata (cDFAs), and progress prediction models fundamentally alter the reachability denominator. By tracking intermediate gates, these systems break the single $M=12$ sparse kill-path into $12$ dense, localized reach-avoid problems.
*   **Advancements in Theorem-Proving RL**: Systems like LeanProgress demonstrate that predicting the remaining steps in a formal proof can act as a pseudo-dense reward, improving the traversal of strictly gated environments and mitigating catastrophic sparsity.
*   **Relaxation of Reachability Assumptions**: Recent theoretical work utilizing Tsallis entropy regularizers proves that exact, uniform strong reachability is not strictly necessary for convergence, provided that a single bounded policy exists, indicating that structured exploration can overcome seemingly insurmountable probabilistic priors.

These findings highlight the complexity of modern compositional reinforcement learning. While the geometric constraints of the state space dictate rigid mathematical limits on naive exploration, the field has aggressively evolved to bypass these limits through structural, hierarchical, and predictive abstraction. 

***

## 1. Brief Summary

The literature confirms the mathematical spirit of the self-claim for unguided exploration—where the probability of traversing a strict 12-gate kill-path is strictly bounded by the catalog-to-subspace ratio—but falsifies its practical permanence, as 2024–2026 breakthroughs in compositional reward machines, hierarchical structures, and proof-progress predictors systematically bypass this sparsity ceiling by fragmenting the reachable subspace.

## 2. Flagged Findings

### Consensus on Reward Sparsity and the Curse of Dimensionality
Current literature universally acknowledges the catastrophic failure of standard flat Reinforcement Learning (RL) architectures when confronted with temporally extended, sparse-reward tasks defined by logical conjunctions of verifiable conditions (gates) [cite: 1, 2, 3]. When an agent must satisfy a sequence or conjunction of $M$ independent conditions (e.g., $M \approx 12$ binary gates) to receive a non-zero reward, the variance of return estimates inflates, yielding uninformative gradients [cite: 2]. Under these conditions, the consensus confirms the Techne claim's fundamental premise: the unguided prior probability of completing an episode (PROMOTE) is tightly bounded by the ratio of valid solution states (the catalog-size) over the exponentially exploding volume of the explored state space (the reachable-subspace) [cite: 4]. 

### Where the Consensus and the Claim Might Be Wrong: Structural Mitigation
The Techne self-claim risks falling into **PATTERN_BASE_RATE_NEGLECT** by assuming the |reachable-subspace| denominator remains static and uniform during policy execution. The 2024–2026 literature demonstrates that agents no longer operate in flat MDPs. The introduction of Reward Machines (RMs) [cite: 5, 6, 7], compositional Deterministic Finite Automata (cDFAs) [cite: 1], and physics-informed Reward Machines (pRMs) [cite: 8] structurally decompose the $M=12$ kill-path into localized sub-MDPs. By exposing the internal automata of the verifiable gates, the agent receives dense, non-Markovian progress tracking that effectively shrinks the operational |reachable-subspace| at each gate [cite: 5, 7, 9]. 

Furthermore, the assumption that bounds on reachability necessitate unscalable priors is challenged by recent advances in regularized learning dynamics. For instance, the deployment of Tsallis entropy in zero-sum Markov games [cite: 10, 11, 12] relaxes the traditionally stringent "strong reachability" assumptions. Tsallis entropy, derived from statistical physics, enforces a wider exploration of suboptimal actions, leading to faster mixing times and polynomial-time convergence without demanding uniform reachability bounds over the entire subspace [cite: 10, 12, 13]. 

Additionally, researchers risk **PATTERN_PRIME_GRAVITATIONAL_OVERFIT** when attempting to hand-craft dense reward shaping to overcome the $M=12$ ceiling. Manual potential-based shaping often leads agents to exploit local optima rather than completing the true logical conjunction [cite: 2]. Current state-of-the-art avoids this by utilizing Hierarchical Reinforcement Learning (HRL) equipped with meta-learning and autonomous subgoal discovery [cite: 3, 14, 15], or by employing automated theorem-proving step predictors (e.g., LeanProgress) which act as dynamic, verifiable heuristics rather than static shaping functions [cite: 16, 17].

## 3. Problem Statement

The precise object being interrogated is the **probabilistic bound on success (PROMOTE prior) for episodic reinforcement learning operating under extreme reward sparsity**, specifically characterized by a success criterion demanding the satisfaction of a conjunction of $M$ binary verifiable gates (with $M \approx 12$ defining the minimal length of the "kill-path").

In formal terms, the environment is modeled as a Markov Decision Process (MDP) or a Non-Markovian task mapped to a Reward Machine $R_{P_{SA}} = \langle U, u_0, F, \delta_u, \delta_r \rangle$ [cite: 6]. The condition of success requires traversing from $u_0$ to an accepting state $u_A \in F$ through exactly or approximately 12 transitional criteria $\delta_u(u_i, L_i) = u_{i+1}$ [cite: 5]. 

The Techne query postulates that without structural intervention, the expected per-episode probability of generating a successful trajectory—defined as PROMOTE—is constrained by the inequality:
\[ P(\text{PROMOTE}) \leq \frac{\text{catalog-size}}{|\text{reachable-subspace}|} \]

We are tasked with evaluating this geometric constraint against baselines in theorem-proving (ProofRL, Lean), retrosynthesis, and spatial/graph partitioning (BC-Tree), examining how modern reachability limits, coverability, and compositional bounds relate to this hypothesized ceiling.

## 4. Status & Bounds

### Last Known Status
As of 2025–2026, the strict sparsity ceiling defined by the ratio of catalog-size to reachable-subspace holds true *only* for unstructured, flat multi-step environments without intrinsic motivation, memory augmentation, or hierarchical decomposition [cite: 2, 3]. In applied domains such as automated theorem proving in Lean 4 [cite: 18, 19], pure flat PPO (Proximal Policy Optimization) routinely times out or fails on long-horizon proofs due to this exact combinatorial explosion [cite: 20].

However, the operational status of the field has evolved beyond flat MDPs. By utilizing frameworks such as LeanProgress [cite: 16, 21] or AlphaProof [cite: 19], agents use LLM-guided tactic generation paired with Monte-Carlo Tree Search (MCTS) and progress predictors to dynamically estimate the distance to the goal. LeanProgress, for example, achieves a 75.8% accuracy (Mean Absolute Error of 3.15) in predicting the remaining steps in a formal proof [cite: 16, 21]. This shifts the algorithmic paradigm from a blind search bounded by the total reachable subspace to an informed A*/best-first search guided by a dense heuristic [cite: 17].

### Current Best Bounds and Conditional Qualifiers
1. **Cumulative Reachability and Coverability**: In online reinforcement learning, sample efficiency is dictated by coverability constraints rather than the absolute size of the state space. Bounds formulated around cumulative reachability show that learning an $\epsilon$-optimal policy relies on the representation conditions of the value function class $F$ [cite: 4]. If the 12-gate sequence features low coverability, sample-efficient exploration is still possible, conditionally relying on the agent's ability to model the intermediate value functions [cite: 4].
2. **Polynomial-Time Convergence via Tsallis Entropy**: In decentralized zero-sum Markov games, past algorithms assumed "strong reachability" (the expected time to visit any state from any state is bounded by an integer $L$) [cite: 22, 23]. Recent bounds achieved using Tsallis entropy regularization relax this, proving finite-time convergence to an approximate Nash equilibrium with polynomial sample complexity in $1/\epsilon$ ($\tilde{O}(1/\epsilon^{24rb+28})$ time) requiring only a single policy with bounded reachability [cite: 12, 23]. This mathematically proves that traversing complex gated environments does not require the entire subspace to be uniformly reachable.
3. **Verified Safe Reinforcement Learning (VSRL)**: When gates represent safety constraints (a "kill-path" in a literal, safety-critical sense), bounds are verified using differentiable reachability tools. VSRL provides $K$-step verified safe controllers, proving that safety violations can be mathematically bounded to zero over a finite horizon $K$, directly restricting the reachable subspace to only verified regions [cite: 24, 25]. 
4. **Proxy Graph and BC-Tree Bounds**: For large discrete search spaces, Block Cut-vertex (BC) trees representing biconnected components reduce indexing time and index size significantly (e.g., providing $1.1 \times$ to $10 \times$ faster searches over traditional hashing) [cite: 26]. Graph proxy algorithms using BC-Trees explicitly bounded sampling quality improvements (e.g., 25% by BCP-W) over existing methods, showcasing how structural decomposition mathematically shrinks the effective $|reachable-subspace|$ [cite: 27].

## 5. Literature (Primary Sources)

The fundamental assertions in this research brief are backed by the following primary texts from the 2024–2026 horizon:

*   **Theorem Proving and Formal Logic RL:**
    *   Huang, S., Song, P., George, R. J., & Anandkumar, A. (2025). *LeanProgress: Guiding Search for Neural Theorem Proving via Proof Progress Prediction*. Transactions on Machine Learning Research (TMLR); arXiv:2502.17925. [cite: 16, 17, 28, 29]
    *   Wu, Z., Huang, S., et al. (2024). *InternLM2.5-StepProver: Advancing Automated Theorem Proving via Expert Iteration on Large-Scale LEAN Problems*. Tech Report. [cite: 30]
    *   Petrik, M. (2025). *AML Fall 25: Reinforcement learning for formal proofs*. Includes citations of AlphaProof, DeepSeek-Prover-V1.5, TacticZero. [cite: 19]
    *   Beneficial-AI-Foundation (n.d.). *NumpySpec: Automated Theorem Proving RL agents learning to prove mathematical properties in Lean 4*. [cite: 18]
*   **Compositional / Hierarchical RL and Reward Machines:**
    *   Levina, K., Pappas, N., Karapantelakis, A., Vulgarakis Feljan, A., & Seipp, J. (2024). *Numeric Reward Machines*. ICAPS Workshop on Bridging the Gap Between AI Planning and Reinforcement Learning (PRL). [cite: 9, 31]
    *   Parac, et al. (2024). *Probabilistic Induction of Reward Machines (PROB-IRM)*. Proceedings of KR. [cite: 5]
    *   Furelos-Blanco, D., et al. (2023). *Hierarchical Reward Machines*. PMLR. [cite: 7]
    *   Various Authors (2025). *Physics-informed Reward Machines (pRMs)*. [cite: 8]
    *   Butbaia, G., et al. (2024). *Hierarchical Reinforcement Learning for Sparse-Reward Search in Commutative Algebra*. ICML. [cite: 32]
*   **Reachability Bounds and Tsallis Entropy:**
    *   Ouhamma, R., & Kamgarpour, M. (2024/2025). *Learning in Zero-Sum Markov Games: Relaxing Strong Reachability and Mixing Time Assumptions*. arXiv:2312.08008v3 / ICML 2024. [cite: 12, 22, 23, 33]
    *   Wu, J., Zhang, H., & Vorobeychik, Y. (2024). *Verified Safe Reinforcement Learning for Neural Network Dynamic Models*. NeurIPS. [cite: 25]
*   **BC-Tree and Retrosynthesis RL:**
    *   Guo, N., et al. (2026). *HELM: Hybrid Spatial Index of Moving Objects at Large Scales Tuned with Multi-Agent Reinforcement Learning*. [cite: 26]
    *   Hong, S., et al. (2018/Recent works). *BC Tree based Proxy Graphs for Visualization of Big Graphs*. [cite: 27]
    *   Various (2026). *Retrosynthesis-RL using DQN for exploring chemical pathways*. [cite: 34]

## 6. Attack Vectors

When targeting the $M=12$ kill-path threshold, researchers deploy various "attack vectors" to circumvent the fundamental sparsity limit defined by the catalog-to-subspace ratio.

### Live Techniques

**1. Reward Machines (RMs) and cDFAs (Compositional RL)**
The most direct assault on the $M=12$ sparsity problem is the formulation of the task as a Compositional Deterministic Finite Automaton (cDFA) or a Reward Machine. Instead of a single flat environment where reward is only achieved at the 12th gate, the RM provides a finite-state machine representation of non-Markovian reward functions [cite: 5]. Each gate transition $\delta_u(u_i, L_i) = u_{i+1}$ represents a localized sub-task [cite: 5]. 
This explicitly fragments the $M=12$ kill-path. Rather than sampling the joint probability of 12 events, the agent solves $12$ local reach-avoid problems [cite: 1]. Furthermore, hierarchical variations like HRMs (Hierarchical Reward Machines) allow an RM to call other RMs, effectively modularizing the reachable subspace and isolating the exploration requirements [cite: 7]. In physical implementations, physics-informed RMs (pRMs) incorporate known physical dynamics to drive counterfactual experience generation, drastically improving sample efficiency [cite: 8].

**2. Proof Progress Prediction (Theorem-Proving-RL)**
In automated theorem proving (ATP), solving a complex mathematical theorem acts identically to satisfying $M$ verifiable gates (the tactics). Because the space of valid propositions is exponentially dense with useless "strange theorems" or "one-way functions" [cite: 20], pure RL random walks fail. Live techniques like LeanProgress model this by balancing datasets of proof trees and training an LLM (e.g., DeepSeek Coder 1.3B) to predict the remaining steps from a given proof state [cite: 16, 17]. 
When integrated into a best-first search, the tactic log probabilities are linearly combined with the predicted number of remaining steps [cite: 16, 21]. This heuristic behaves as a dense progress signal, directly navigating the agent away from infinite dead-ends (the "kill subspace") and increasing the Mathlib4 pass rate over baseline [cite: 16]. This tactic avoids the catalog-to-subspace limit by imposing a gradient over the otherwise flat subspace.

**3. Tsallis Entropy Smoothing for Bounded Reachability**
To ensure an agent physically covers the reachable subspace without requiring infinite time (strong reachability), researchers replace standard softmax Shannon entropy with Tsallis entropy regularization in policy updates [cite: 10, 12]. Tsallis entropy mathematically forces broader exploration of suboptimal actions, resulting in faster mixing times and overcoming the strict bounds of local Markov chains [cite: 10]. In multi-agent scenarios, this technique yields polynomial-time convergence to Nash equilibria assuming only weak reachability limits (i.e., the existence of an irreducible and aperiodic policy pair) [cite: 12, 13]. This is critical for generating reliable priors on reaching the $M$th gate in dynamic, adversarial, or noisy fields.

**4. BC-Tree Proxy Graph Indexing**
In large-scale spatial or discrete state exploration, BC-Trees (Block Cut-vertex trees) or Ball-Cone trees are utilized. A BC-tree decomposes a graph into biconnected components, allowing an RL agent to index and search macro-structures rather than micro-states [cite: 27, 35]. In spatial multi-agent reinforcement learning (e.g., moving objects), BC-Trees provide a 1.1x to 10x faster search by pruning point-level data and focusing on bounded conical or block structures [cite: 26]. This directly reduces $|\text{reachable-subspace}|$ by clustering topologically equivalent states, massively increasing the per-episode PROMOTE prior.

**5. Retrosynthesis-RL**
Similar to theorem proving, retrosynthesis requires finding a sequence of chemical reactions to construct a target molecule [cite: 34]. The chemical space is virtually infinite. Live techniques utilize deep Q-networks (DQN) paired with MCTS to propose reaction pathways, effectively learning the "gates" (chemical validities) required to slice through the massive combinatorial subspace [cite: 34].

### Exhausted Approaches

**1. Flat Reward Shaping**
The historical approach to sparse rewards was potential-based manual reward shaping [cite: 2]. While mathematically proven not to alter the optimal policy under strict conditions, manual shaping across $12$ binary gates typically introduces multi-objective non-stationarity and "shaping risk" [cite: 2]. Agents frequently learn to harvest intermediate rewards in a loop without ever passing the final gates, leading to catastrophic local minima. This is largely abandoned in favor of formal RMs or learned progress predictors.

**2. Unguided Option Discovery in HRL**
While Hierarchical RL is powerful, early attempts to autonomously derive subgoals based simply on state novelty or simple partition heuristics (e.g., reaching rarely-visited partitions in Atari) are proving too slow and computationally brittle for strict formal verification environments like Lean or large algebra problems [cite: 14]. The community is moving away from blind novelty toward logically specified boundaries (e.g., LTL constraints) [cite: 36].

## 7. Cross-References

*   **Calibration Pattern Links**: 
    *   **PATTERN_BASE_RATE_NEGLECT**: As noted in Section 2, evaluating the PROMOTE prior using only catalog-size divided by reachable-subspace neglects the base rate of structural modifications. Contemporary agents do not view the subspace uniformly; they use embeddings, Tsallis entropy [cite: 10], and progress heuristics [cite: 16] to warp the topological distance to the goal, rendering naive volume-ratio calculations obsolete.
    *   **PATTERN_PRIME_GRAVITATIONAL_OVERFIT**: In hierarchical RL frameworks attempting to bypass the $M=12$ barrier, algorithms that over-rely on intermediate pseudo-rewards (such as maximizing branch factor simply to increase complexity [cite: 20]) often overfit to the sub-goals. The agent gets gravitationally locked in the early steps of the kill-path and fails to generalize to the global task completion. 
*   **Related Open Problems**: 
    *   *Credit Assignment in HRL*: The "Conductor Confound" remains an issue where it is difficult to determine whether a failure to hit the 12th gate was due to a flawed high-level subtask sequence or poor execution of primitive actions by the low-level policy [cite: 3].
    *   *LLM Hallucination vs. Formal Verification*: In theorem-proving RL, LLMs propose tactics (gates) that are often mathematically invalid (hallucinations). While Lean 4 provides an absolute binary verifier (kill-path), closing the loop between the LLM's generative prior and the verifier's strict bounds is an ongoing research frontier [cite: 17, 21].
*   **Candidate Primitives**:
    *   **Tsallis Entropy Regularizers**: As a primitive for policy smoothing, it systematically outperforms Shannon entropy in breaking through sparse bottlenecks by enforcing mathematically rigorous suboptimal exploration [cite: 10, 12].
    *   **cDFAs / Reward Machines**: Function as the ultimate primitive for compiling natural language or logical constraints into executable RL guidance algorithms [cite: 1].

***

## Verdict to Techne

**Verdict: The literature leaves open and conditionally confirms the mathematical spirit of the self-claim, while falsifying its practical relevance to modern state-of-the-art systems.**

1. **Confirmation of Spirit**: The Techne claim states that `With ~12 binary gates in the kill-path, per-episode prior on PROMOTE <= catalog-size / |reachable-subspace|`. If an agent is executing a purely random or naive Markovian policy, the literature agrees [cite: 3, 4]. Extreme reward sparsity dictates that the baseline probability of success is physically limited by the volumetric density of target solutions within the available state space.
2. **Falsification in Practice**: The claim fails to account for the structural interventions defining the 2024–2026 literature. By employing Reward Machines [cite: 6, 7], predicting proof progress (LeanProgress) [cite: 16], decomposing large spaces with BC-Trees [cite: 26, 27], and ensuring bounded reachability via Tsallis entropy [cite: 10, 12], modern compositional and hierarchical RL effectively fragments the 12-gate sequence. The agent no longer explores the entire $|reachable-subspace|$ simultaneously; it explores highly constrained, localized subspaces step-by-step. Consequently, the actual per-episode PROMOTE prior in a well-structured compositional RL agent is vastly exponentially higher than the naive `catalog-size / |reachable-subspace|` limit.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj3Kp_sFrIehS5iHypQnIIyYmlQy_HPyN6GwVjTTdCe8Zh9h3WPGJlaMJyfX8_OeBFbriW7nE0IWFw_g8U1zvvdNRGmp1688jFYQedKOglMiOh2VJk6p6Qnw==)
2. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxsxmpfGp4zCrnH4pIViqDj5Nj8xhmY4ZtA1d6jZxG5L5scHr5h7irC1yGDtic0939PVMN0vDmsNxxVBck9Ts049lxLzIM2oMDPVAKPLs3M0hR8HVTrFLwrgrMq-TC1Q==)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTgDycppky6moFPQhQ29WBAOCTld4wy6KKbJVxCKpqhE-cTJMfSBZCSEooNr43FjWFuY6nejCY0A_1NhM-j3xEI8iVdSF70yjKTh5aQcI0-3XGueDt5UKbnP9aUhSptJrXNM-P1BPs8II=)
4. [nsf.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJe7NY4wL_M6EYSNWzUN_1457aQ1L5yeWGc4IxWa4qGPGN-wUYfnSoJfZUOmxBcyjtasycyEHOk2FKzc8cCG8yKNjTtLaPGrpGiKtFHyZpGSwFpkLc4wqaBLkjn6_gFy4=)
5. [kr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcnQTV1n7l42mI1ok2_PmValQ0CZUqxGw7ioHA8bJHHK18mN9IqmCUrDLnCUz6iBQbFrWcPCls7gQ9cEBsymXS0-AdtccD56k7q0fJ56IlsqXms4nfphsAehC5zmwNWV63jbb55nKZIx8IM4u4x8j-jXkRvA==)
6. [jair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHP-vq12xz1ouXfYbbagl0ML2v5xYDLfE2lfYM9fjhS3EwUx_HG0pEVtxFuqFmuVe-Hmph4irUSBpO0S2AsGWfkTbB09YwyWzwuQisvIaJQZAAW4T4J_3Ll5-hMI5fRqauw_V-49lc-7pwc2YCErPdWcaixvPN-vhfhAQC)
7. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCu2PDeS1aNPTemJrtYgHxTMwetFQ0BJ_fQS8eh6zAbGMPLvyVpfAHYbQcsC4iEOvWbYdqeJoPK5GsJzNjDmE2pxCXdXuQqahH7RvkR_yeso7RmEtQCY2YlBcUMs7h6Px8v-ecSlzgKLGl1M_lX4gkGTxq3gUJh6tu-1xZ-K5CHw==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsvkkEVwkBeiWVeBoaUn_gIHmtmxNyjl3UXVZRElZ4a04t-N_b3NsyzR1bqLLTOSQ-u9R7Mh1wWWak7OaGtTWqMptEocA7xm4kJFiQA6v845RZb6JI0Q==)
9. [mrlab.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7NUf8TJIqkHLq5U5zUwm57EWPSpDawXHS6vPZuEyFfilvadyxhOg-Cp1sGoz_gTo3i99UnPMBVVYX87doFSWpQuSS7qlh8a-Sq6z5HI7qtBepWgoR8HXGSSOahayLTO3-i0I6YyzT7nLDpWa4)
10. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWv8amN4J9b6CWekRDRTbF1SPpN1HVgryAvVGBhLXl24au6nqOoPKKMX7tz-bUl2fy-ZnpRTHEGZvldCHQDcMyb6o2G0qtL2raawe8UOyOEYcj-e_H4FRiUV51eeA2kGONr0HkW2gGijmV4G3MD2lKb5c=)
11. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1ZVDEGafc5THj57fJVw7zUO7zBqszQXEplIWgRg1DNpae7nxN9MzPSolPZoFYuyw_zl8b6jMg2AdYoDYJcn2ClIy6RlNjmsmHsHSmTR18hscIQEZMKyHxHH47m_ySBhK2zk4f1pgHrRldh8mmWdNs1zDTjjqRI8cjj6br7SPDW4cKdCxSj6TI6UeSu-0qjFqPhPXbgPe_cx-vODRz2EaOYh--u1ERj3RnPr4LYafX_prT6qpeUGgWPIrB0dZ6a94eP_O-)
12. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5VB1qTcC8yPZXF-zUAD4d_PYPZ27eXFFyqEU7mDR_H7Jtukg8OiM6u38vZIyOdE8dH4RjXLk8q2ZzsJhpTBvhDFW1pkt86A-wn0SfOWgT38yXEI7dAT2c2Bdf1JhQ)
13. [aimodels.fyi](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBKkCU4ITbJmQ92TUF3c1kdpp7Y-Ha_FU16o7aw-n1WrzCnXwQa0Jwzm04XjrsXFmupWC2mnUmcGThahs3Wmb5ieXY8lQvaW1HTKN9EsTK4dVL6CxiNYDQyX1xXpfL0e6V8wjlLrEcHDtYcKBuN8VbSocqdqfqpgLpyzAQrXEYY4Pu2TW5_el4dJQ=)
14. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgiroKGq0ak3vnHYrJ1CBpPgjQD-xdhVQZidHCk-QTG3nKFqK4qt_r_m5lR7uP4w3nUHgzqvvG-4u9W87sbBRxG9XLDIMrVF7WLpQZT5kjaj-yWpXEO7Rtb3gVK4dgaoUEzcFZt4ZJpDCLV3C2Q9R_pt8=)
15. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHQqUoZfQb3oxizWEuFyq8C3a7Z_Dvqj0IAa9_rMpQA2hZRzF-1djBYlrbhVQLdHxG-LmDDz0XZUGTkRL8eaMlkBkmy5nrh1fYKwZJJlf6kPKHke41ToFqgOh8ikpdDedISgey8n7KAg==)
16. [leandojo.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc3Dpqb6EclwizULdM79ah4TDFtNyqpjJdxi_4Cw_t-2yN3aDbIFmhi9foAH1K4Z7PTaxVAJBiHu6SxL8hhPUbbZECkkw5MDRquRj2I9k0rOGUqtjjSAuTBeGvIg==)
17. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSP4KkyFI3KwZoD3fOq_2t5KN91m-xQD2BTqpiNnUpJcMfjH6FmUBh8Lr8qmG1Irhc8hEALyWr3bejZSRsSqSVZKwYXv01r8pDxKHtVXiyVYhqu3sT8QeZ3EEGnbC-Fmc2dl2QRof2_e2j-YAZJRwCmR6-9Jc4mVuOdbCWz7KjnQeejPRrJUQIzNEhJX1DqzJtqIKT-NX-UVmoyDQwzOYuvQj33hCLNRgOtVKX_OSXqg==)
18. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaBm3UP45SSa4Nddp5r_nfCrrlIHez0pnwH-O_QNbLfbGDxv2SNOfqg_ZwYayp7oglzUC36qvvBBnfICOxRa8cxhJMciw01mlUbXnvnkzxUEmiRmkJtjf8eHowWfZJsM1wWszSkpTzzr0VAw==)
19. [gitlab.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy9xwD2PygLDu8JsqtUOF45ytAsXNHfcD__8oJu9yYGgNtwALaPtApLI-4pSzcGEJdi6AfroQkruuKByQcK88E3Go-mBg9xaxHOLBNLc4euFh1FibJBeXDTDygKWbOTw==)
20. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEhrxrB41ZxxXTxsjIF02aJhTeNyLQkyKVfSbO35s1JD56cxOb7QekRPjOpVNjVbniaosFd-v8umURJjTuiE0vuofXct2iwFQKW2mg9rGDWHzZAGl77C0M5MaxVEU8Ng9RI82oU3_WZlSNl7J5AWIj2QqfWpoeUbm2A3JHtWMtb29sZZgZvd3_cUr4OKcW0zN-KtdLPhcTIy5lmV0xl7GPV8bPErDOzQ8jgamNnFo3z2Ng-QjhJ-cwwrdlhG1PxgkGx43MOdKIyZw==)
21. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_NRQIYK2WhsGtpdQauE9U7xAnii11GJWcMx7mc_EWVKW2uEaQsUT47XZmZ_Hv_V0A29DFclN-Wm-8SzX16sNIQwQAvH2EkbPlGY66q9lrhtlXhmxOrUh9KrEWOhCDlHE=)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2J0SrxIIKbaNUi9iO8I6_6Xq68fX97wBoX5YT6bgDSdMIy2YOygUIgPrRFUds6hCfvDcWx5mj6R0-SL9Mg7jJzFOQKkQ9oskjiDnF18KNI5jdJxUFuNaMDg==)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9ZbMBAjvEodaQaije8qzPytvXaTBgnJC1slZA_o_Qgzqn-FOe3zYXj3SrskiiBV2Boq3fmzgZBxwPhAdSTXk551V3VadIc1o6P9r_JRMmdYNhabQ6lA==)
24. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxsKmisDhs1aNP_noHl8TMmOqPUwH1mtT7qFsxhpvBkNGjq0IOrEQgM03ZE5DpYnVyMbTDaKkexPEAIO1jviRF3Se7SFdYfpS93hDC2HI-sfvYITt_UDCI6IfDvHHtIPswudS9tJGlulRI_NRHcB9k4Z-uUuk=)
25. [liner.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKw39Wq4yJgBVVHXoWtGFnsDZZBv1r8xKud4IjaxyMw_4FPwJQqjFQ89w5qLFzAjMXid7L1k1wRF1HUieX51G4QHp3PfP20pLPrNbbdpALM_y-ahvj9P-lOfYvWf9JYgsl2EeCYAJAaGaF7POpHUV1hZQqVEbNpe5iP9sdF3fC0F7lDFHzOp7eHeG2wSa3c79Qw6fZhQ==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSz1j0XhNg32J7iE8xq5QEU6L6vgEEj3jg87jIRsw9aMrzPk0UxB_oIa70oHpAie_JjlSxR_o9tSQmYJE3TTFFW6lWeH-jcOxrp5faugz5kttayUzKT0UN-upqLYiKr-5NCWgLrM3r2LDM1QGpAcwYKnSRMbp9U-gz)
27. [ocha.ac.jp](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzqMJYR1X3751o_Kj6kVSamB9nsIaS7A7twgApgqwsn8FCzb8Ep5_VBAHR7VGUBKytKo7WKFklcAkuCwyxikwMxvO4ApXO_KdDeBAqJeOrkZjRd5ZtE-3_2lkW94-ljQxdWOQ71m5w)
28. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1DJOkof01ZRGmvUuHC1p0H9S44y71M3p8XeHdcUo_7sixbOTboJ0ZhM0DxIIMHA86OsHjp3BqhU04EPa14N2p3jeVNgiP5gCxuXU_J0WCjT_TVNGlDd8fF_3b2A5f8g==)
29. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1-uCG8a-8t15CRH4DLsYILyuJCMoQHW1Fws0MU2zibaE50MBR8SiC_Fd82vzGpOLW3ifTTlxsv47cw_RaJvNOKF92xYPunrsvwI0ixJVZvCjJkjN4Ov8X96OrVVYBG3gOdx-IFWnuwCyHqCrRfa2ED593373mtvD8WN61hCGnLZ7u7BrS-eMUTWVJNEtdIV7_jyeJFKKCQqLV3o87PDpMIi66JiFZjiRcVeZiv7v54RfA4TVfGjd7tEmUxD_Z)
30. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdtfyvs5EQNQjh11EYRUbEP8NvM1ZoqKVPL_jbRZabeutcespNxq2Rclt4L7_3l7x-II9zoiKqse56TVEKhz8H-_0WZTrPTWyFaPsTyp0log==)
31. [mrlab.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOG8LAVI7yzxXn-4T43IEjfZfg8cgDUtA8kX-WOTEK59VZXGKqHmhBBvpRsLzZhtIOcWDQ4W1DmOHKiT1PV7yZrLxvqoMh8B16D4Nn3umFObDSJmXa8eYKNpr2-TH_RmxWdGH9o16sExo5kQPiCA==)
32. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAgglFavFnl76LMDWz5BaWT-AgUpENr7jVEPfKrsO9xuyOnNRvjHSHNOq4WVQ8JOHMkf2PYF8fuEZ9fGWSLXGrjkaHEbKEq0bize5Y86M4KYlg7LqVxV5WCO3Sd_gPpw==)
33. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERfJVtINXGdDNL2g5u-5dw5pvryQo-UvUg23zb4Rhq_NwglHmZ10OE0QGDRfQwQ6FN-xO20jt3a3uWbe5obWZCGrYFoGDpwjUgDX5iV_Gqt6UqLMBV9TqI)
34. [researchhub.org.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaetjaGN1Vzorql88qRp_Jz43kT9IWvG2Hnzb3K3708h5umwL3UKo6DLOXhwtht_uk1q1LZrcvqYSycZkX52R_DYS2mhdTsHLL0iUoN4NOMhPdRsnLJo4FFLAawaeQ_62zNU6QVICPVHx82f1ju-eX1U9ppvZtgczwW0UpyQTJUa8ZD-Jv5Bz3)
35. [cwi.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHooLMfQHtPtM_lbCpJso5cuOcMJ7rKuZOEe-QPKv-Fbezde9MEJ_Srmqc8yAGL0_qFgMn-L7HG1yTOlII1C8zC0W3PcnrwRDLuAksFfS6Ez-IN1GJgnKMuZ7n4O94LSTBMULpmkuGWY_c=)
36. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-X8UDG974eETUcOg7U4EvQl9Jfw7541mWjeyc8z_4FcxGKLgATV5-Cjs1LV4Z2WQmc_yJEXnw75dzUnPq3cHJ__IuJ6JYLMjf6MdbUg50H3PsIV-XS42wPAhHjGFcEAcGcIcjFjBGVsNUMoZaonsaCM_p345-)


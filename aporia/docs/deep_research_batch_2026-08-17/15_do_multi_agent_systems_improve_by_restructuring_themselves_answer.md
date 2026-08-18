# Organizational Heredity in Multi-Agent Systems: Structural Mutation, Ablation Verification, and Failure Modes

**Key Points**
*   **Feasibility**: Multi-agent systems capable of runtime organizational mutation—diagnosing failures and spawning specialized child agents—are buildable today and distinct from weight-level neural learning. 
*   **Verification**: Empirical evidence demonstrates that dynamic topological restructuring causally improves performance. Frameworks utilizing ablation controls confirm that structural mutation outperforms static, single-agent, and non-collaborative baselines.
*   **Failure Modes**: Unbounded "role proliferation" is a primary attack vector. Deeply recursive agent delegation multiplies resource consumption, degrades context, and exacerbates coordination friction, ultimately causing systemic failure.
*   **Cross-References**: System performance is vulnerable to "Base Rate Neglect" (assuming any agent addition guarantees improvement while ignoring baseline tool failure rates) and the "Conductor Confound" (centralized routers becoming operational bottlenecks).

Research indicates that the paradigm of "organizational heredity" in multi-agent systems—where an agentic system adapts its structural topology and role composition dynamically based on telemetry and failure diagnosis—is a rapidly maturing frontier in artificial intelligence [cite: 1, 2]. By factorizing overloaded parent agents into specialized child agents, systems can bypass the limitations of monolithic context windows and mixed-action saturation. Crucially, the validity of these interventions is established not through self-reported agent confidence, but through rigorous ablation controls and shadow-mode validation that isolate the causal impact of architectural boundaries [cite: 2, 3].

However, this structural fluidity introduces acute systemic risks. The unconstrained generation of child agents (role proliferation) can fragment authority, explode token consumption, and dilute task context, leading to catastrophic degradation in performance [cite: 4, 5]. Furthermore, cognitive and structural biases, such as base rate neglect during sequential multi-agent evidence updating, and the conductor confound inherent to centralized routing topologies, present significant challenges to scaling organizational mutation [cite: 6, 7]. The following exhaustive report synthesizes the current literature on automated team design, structural mutation, and the causal verification of multi-agent specialization.

---

## 1. Introduction: The Paradigm of Organizational Heredity

In traditional computational learning paradigms, systems adapt to environmental pressures primarily through weight-level adaptation—updating neural network parameters or aligning continuous representations based on loss gradients [cite: 1]. In contrast, **organizational heredity** frames adaptation as a topological and structural process occurring at inference time. Drawing conceptually from biological theories of autopoiesis and economic theories of corporate spinoffs—where progeny inherit and modify the knowledge structures of their parent entities—computational organizational heredity enables multi-agent systems to restructure their own communication and delegation graphs dynamically [cite: 8, 9].

The mechanism specified in the problem statement operates as follows:
1.  **Diagnosis**: A parent agent experiences a measurable deficit or failure (e.g., tool error accumulation, context thrashing, or high queue depth).
2.  **Structural Mutation**: The system diagnoses the bottleneck and produces a specialized child agent to handle a decomposed subset of the workload.
3.  **Verification**: The child causally improves the parent's measured performance, a fact that is verified strictly through ablation controls rather than the system's own self-reported improvement.

This framework is not merely theoretical; it is actively implemented in modern agentic architectures such as Autonomous Topology Mutation (ATM) [cite: 2, 10], the Multi-Agent Network Topology Adaptation (MANTA) framework [cite: 1, 11], and the Agentic Neural Network (ANN) [cite: 12]. These systems maintain frozen model weights but dynamically evolve their collaboration structures, roles, and validation pathways based on real-time execution telemetry [cite: 1].

## 2. Dynamic Role Generation and Structural Mutation

The foundation of organizational heredity relies on the system's ability to monitor its own deficits and autonomously generate specialized roles. The literature on multi-agent reinforcement learning (MARL) and large language model (LLM) orchestration establishes that static, pre-defined roles are often inflexible when task requirements vary unpredictably across domains [cite: 13, 14]. 

### 2.1 Telemetry-Driven Diagnosis
To trigger the birth of a child agent, the system must first quantify a deficit. The **Autonomous Topology Mutation (ATM)** framework provides a blueprint for this diagnostic process. ATM utilizes a "Bottleneck Index," a six-signal telemetry vector that continuously monitors agent health [cite: 2, 10]. This index tracks:
*   Queue depth (pending tool calls or messages).
*   Context thrash (rapid eviction or overwriting of working memory).
*   Tool-error rates.
*   Role entropy (the degree to which an agent is mixing disparate action categories).
*   Retry-loop rates.
*   Cross-agent wait times [cite: 2, 10].

When a warmup-calibrated threshold on this Bottleneck Index is breached for multiple consecutive execution ticks, the system diagnoses an "overload" [cite: 2, 10]. A parent agent attempting to juggle too many distinct capabilities will inevitably suffer from context dilution. ATM responds by factorizing the overloaded parent agent into specialized sub-agents, seamlessly hot-swapping the parent into a coordinator role while preserving its external identity to the rest of the multi-agent network [cite: 2, 10].

### 2.2 Trace Auditing and Playbook Generation
Similarly, the **MANTA** framework treats network topology as an execution-time object of self-improvement [cite: 1]. MANTA operates by executing a task under an initial, task-conditioned topology. A "Trace Auditor" monitors the collaboration trace for process-observable anomalies—such as an overloaded branch, missing validation checks, or premature consensus—without judging the final answer's correctness [cite: 1, 11]. 

If a structural deficiency is exposed, MANTA applies a bounded structural mutation (e.g., adding a specialized verifier, splitting a role, or altering the execution order) [cite: 1]. To establish true organizational heredity across episodes, MANTA maintains both a short-term playbook for intra-run repair and a long-term playbook that distills topology-selection and repair experiences across multiple executions, effectively transferring structural "genes" to future task environments [cite: 1, 15].

### 2.3 Agentic Neural Networks and Forward/Backward Passes
The concept of dynamically spawning specialized child agents based on deficits is also mirrored in **Agentic Neural Networks (ANN)**. In ANN, the multi-agent system mimics the forward and backward passes of a neural network via "textual backpropagation" [cite: 12]. During the forward phase, a task is decomposed, and a team of agents is formed dynamically for a specific subtask layer. If the outcome is suboptimal, a backward phase is triggered. Textual feedback acts as a gradient, guiding adjustments to agent roles, prompts, and coordination mechanisms—effectively mutating the organizational structure to resolve the diagnosed failure [cite: 12].

## 3. Causal Verification Under Ablation Control

The prompt stipulates a critical constraint: self-reported improvement is inadmissible; the system must verify the causal impact of the specialized child agent via ablation control. Recent empirical literature explicitly addresses this requirement, proving that structural boundaries and dynamic child agents objectively improve performance metrics compared to ablated baselines.

### 3.1 Strict Ablation in ATM (Autonomous Topology Mutation)
The developers of ATM implemented stringent safety invariants and ablation controls to verify performance improvements. ATM uses a "shadow-before-live validation" invariant (Invariant 3), ensuring no candidate topology receives live traffic until it successfully passes a shadow validation window [cite: 2, 10]. 

In a controlled ablation study consisting of 720 DeepSeek-V3-driven task runs across multiple workloads, the introduction of the ATM factorizer (which splits the parent into specialized children) lifted code-task success from a baseline of 3.3% to 61.7% (+58 percentage points) [cite: 2, 16]. By comparing the fully mutated topology against an "A0" ablation condition (a static, single-agent or non-mutating baseline), the researchers causally linked the performance spike directly to the structural mutation and the isolation of state memory across the specialized children [cite: 2, 16].

### 3.2 Fresh-Context Verification and Agent-Boundary Ablation
Further evidence of the necessity of isolated child agents comes from studies on "fresh-context verification." In multi-agent coding workflows (such as Shipshape, SciAgent, and GoalOS), a parent agent is often prevented from auditing its own work due to context pollution [cite: 17, 18]. SciAgent, an audit-grade scientific computation harness, forces a role-separated parent/child execution where "fresh-context verification" is applied over recorded artifacts [cite: 19]. 

In a highly relevant ablation study conducted on the Data Agent Benchmark (DAB), researchers tested the causal impact of the agent boundary itself [cite: 3]. They compared a single agent instructed via "prose methodology" to be careful, versus a structural architecture utilizing an "agent-boundary + fresh-context-verify mutation" [cite: 3]. The prose methodology yielded a negligible change (-0.008), whereas the structural ablation proved that the agent-boundary mutation was solely responsible for a significant +0.070 performance lift [cite: 3]. This conclusively demonstrates that the explicit topological boundary of a newly spawned, specialized child agent with fresh context is the causal driver of performance improvement, entirely independent of the LLM's self-reported or prompted "reasoning" [cite: 3].

### 3.3 IDSTune and Multi-Agent Collaborative Ablations
The **IDSTune** framework, designed for integrated database system tuning, provides another robust ablation control case study. IDSTune generates specialized agents to manage different database components (knobs, indexes, views) [cite: 20, 21]. In their ablation studies, researchers removed the collaborative supervisor and forced the specialized agents to operate independently (non-collaborative variant), and also tested a single-agent baseline that attempted to optimize all dimensions simultaneously [cite: 21, 22]. 

The results showed that both the single-agent baseline and the non-collaborative multi-agent variant consistently underperformed the fully structured IDSTune framework [cite: 21, 22]. The authors concluded that the performance gap highlights the absolute necessity of structured communication and iterative coordination among specialized child agents [cite: 21]. Without the distinct organizational structure, the dimensions became entangled in a "single monolithic reasoning process," leading to suboptimal decisions [cite: 21].

## 4. Attack Vectors and Failure Modes: Role Proliferation

While structural mutation and the generation of specialized child agents can dramatically improve performance, the primary attack vector and operational failure mode is **role proliferation**. When a system recursively generates child agents without strict bounds, the resulting organizational complexity collapses the system under its own weight. 

### 4.1 The Mechanism of Role Proliferation Failure
Role proliferation occurs when a system creates numerous highly specific, overlapping roles that fragment authority, complicate coordination, and duplicate capabilities [cite: 4, 23]. In enterprise architecture, excessive role mapping increases policy complexity and administrative overhead, fundamentally degrading governance [cite: 4, 23]. In runtime multi-agent systems, this translates directly to a catastrophic explosion in token consumption, latency, and context degradation [cite: 5].

The multi-agent orchestration engine **Codex** explicitly documents this failure mode. Codex governs parallel agent orchestration via two critical parameters: `max_threads` (concurrency limit) and `max_depth` (recursion limit) [cite: 5]. 
*   `max_threads` allows parallel independent tasks (e.g., 6 agents auditing 6 different files simultaneously), which is highly efficient [cite: 5].
*   `max_depth`, however, controls how deeply an agent can spawn its own child agents. 

According to Codex's architectural documentation, modifying `max_depth` is highly dangerous. Raising the depth limit turns broad instructions into repeated, recursive fan-out [cite: 5]. An agent that delegates to a child, which in turn delegates to another child, exponentially multiplies token usage, network latency, and resource consumption at every hierarchical level [cite: 5]. The performance degradation is predicted precisely by the depth of the organizational tree and the presence of *sequential dependencies*. If Child Agent B requires the output of Child Agent A to proceed, but they are spawned in parallel or at deep arbitrary levels, the system enters a wait-state (wasting thread slots) or executes with incomplete context, predictably resulting in hallucinations or failed tasks [cite: 5].

### 4.2 Bounded Mutation as a Defense Mechanism
To defend against role proliferation, frameworks like MANTA and ATM implement strict constraints. MANTA employs a "bounded structural mutation" strategy, which limits the number of modifications applied during any single repair cycle [cite: 1]. Ablation studies on MANTA's mutation budget reveal a non-linear return on investment: the first structural change captures the vast majority of the benefit, and allowing up to three changes marginally extends coverage to the most difficult tasks. However, infinite mutation budgets simply waste tokens without yielding further task success [cite: 1, 11].

Similarly, ATM enforces "Invariant 1: Capability Monotonicity," ensuring that the aggregate capabilities of the child agents are strictly a subset of the parent's authorized capabilities [cite: 2, 10]. This prevents a localized failure from triggering the spontaneous generation of over-privileged child agents, a critical security guardrail against automated privilege escalation [cite: 2, 10].

## 5. Cross-References: Cognitive and Structural Biases

The efficacy of organizational heredity is further complicated by phenomena mapped from human behavioral economics and distributed systems theory onto multi-agent networks. The query highlights two specific cross-references: PATTERN_BASE_RATE_NEGLECT and PATTERN_CONDUCTOR_CONFOUND.

### 5.1 PATTERN_BASE_RATE_NEGLECT
**Does adding *any* agent help equally?** 

Base rate neglect is a cognitive bias wherein an entity overweights recent, specific evidence (representativeness) while ignoring the underlying statistical baseline (base rate) [cite: 7, 24]. In multi-agent systems, this pattern manifests in two critical ways.

First, during sequential belief updating, multi-agent populations are highly susceptible to base rate neglect. In synthetic simulations (such as the PsybORG+ cybersecurity environment modeling APT attackers), agents exhibit sequential base rate neglect by overweighting recent local signals and failing to account for the global prior, leading to compounding errors in multi-agent inference [cite: 7, 24]. An agent sequence modeled on recursive Bayesian updating ($logit(posterior) = \omega_1 \cdot logit(prior) + \omega_2 \cdot logit(likelihood)$) where $\omega_1 < 1.0$ mathematically demonstrates this neglect, causing the collective belief trajectory to overreact to localized noise and diverge from objective reality [cite: 7].

Second, at the architectural level, base rate neglect explains a common fallacy in MAS design: the assumption that adding more specialized agents invariably improves outcomes. Designers often neglect the *base rate of tool failures* or the baseline friction of inter-agent handoffs [cite: 2, 25]. As seen in ATM's Bottleneck Index, the error rate of tool interactions and cross-agent wait times can quickly exceed the theoretical advantage of specialization [cite: 2, 25]. If a child agent is spawned to solve a minor deficit, but the base rate of handoff hallucination is 15%, adding the agent may actually degrade the net system probability of success. Thus, adding *any* agent does not help equally; a child agent only improves performance if its specialized utility strictly outweighs the systemic base-rate cost of its instantiation and coordination [cite: 5, 25].

### 5.2 PATTERN_CONDUCTOR_CONFOUND
The Conductor Confound describes the structural vulnerability inherent in centralized multi-agent routing. Many traditional multi-agent systems (e.g., AutoGen, MetaGPT, or standard LangChain routing) rely on a central "manager" or "router" agent to evaluate inputs, break down tasks, and delegate to specialists [cite: 6, 26]. 

While this mimics a human organizational hierarchy, it introduces a severe bottleneck. Relying on a central controller inflates deployment complexity and renders the entire system highly vulnerable if the conductor fails, hallucinates, or becomes overloaded [cite: 6, 26]. If the conductor misinterprets the state, it will misroute tasks, starving capable child agents of necessary data while overwhelming others.

Decentralized architectures, such as **AgentNet**, attempt to solve the Conductor Confound by allowing agents to dynamically reconfigure their connections and distribute tasks via a Directed Acyclic Graph (DAG) without a central orchestrator, enhancing fault tolerance [cite: 6, 26]. In the context of organizational heredity, ATM directly addresses the Conductor Confound during its mutation phase: when a monolithic agent is factorized into children, the original agent is transformed into a lightweight coordinator, but the state transfer is strictly governed by privacy-level-aware routing invariants [cite: 2, 10]. By stripping the parent of execution responsibilities and enforcing formal routing paths, the system mitigates the risk of the conductor becoming a computational or cognitive bottleneck [cite: 2, 10].

## 6. Synthesis and Conclusion

The design of a multi-agent system utilizing **organizational heredity**—where diagnosis of a failure triggers the generation of a specialized child agent to causally improve performance—is empirically validated and technologically feasible today [cite: 1, 2]. Research firmly establishes that structural adaptation at inference time is distinct from parametric weight updates and can yield massive performance gains, as evidenced by frameworks like ATM, MANTA, and IDSTune [cite: 1, 2, 21].

Crucially, the integrity of this paradigm depends heavily on **ablation controls**. The literature demonstrates that "prose-based" agent self-correction is largely ineffective, whereas strict topological boundaries (e.g., fresh-context verification via an isolated child agent) are the true causal drivers of improved task resolution [cite: 3, 19].

However, system architects must strictly guard against the fatal attack vector of **role proliferation**. Unbounded recursive generation (excessive `max_depth`) leads to token explosions, context degradation, and coordination collapse [cite: 5]. Designers must also account for **Base Rate Neglect**, recognizing that the overhead and failure rates of inter-agent communication can negate the benefits of specialization [cite: 2, 25], and the **Conductor Confound**, ensuring that the mechanism responsible for diagnosing deficits and spawning children does not itself become an unrecoverable bottleneck [cite: 6, 26]. By binding structural mutations with formal safety invariants, multi-agent systems can achieve safe, evolutionary organizational heredity.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqMS1R-ZQO8zrE2ylZp2WVINIu8TiIUsBC__Ajdh-pfHDuHgsM57g8_Ico2Z1dIlkYtBc2439XQbbURnUfN9wSo7SQ6jbYKe0LKBGpCZJkxEyR6IEddfJwmw==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUJ6id800j4JU7xOGwR9x0Z9avJpTichd3W80n2TlRAY0HP4ObAFZjBE0OU2jyQn6fLTEn6v2yGSB7_GObjHg_zy852mDEVLiTOhY0Xwz1eFaVOWR71W0bDg==)
3. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4yKscRsf4Wtmsj5kLmHSOnF7V1niu4UJeIsQHtG18lvr-J5rCElU9BcoJIlvspuy1ig1_8GcgjoeCExyj7wSrZvvX7e_ynKJ3MGu_jGznRLJ2dXOI61fzvgGZ3EOCchxjnXrxBkbMIiSTz52LXw==)
4. [autexa.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDt-yzYHO4YEhyUgIxVbBHOmnoGfaMMAQHecS8MrPSQnVuRgcwpOtKbYch2dKLPDcUQhMSdmt6FRR2Dm7BcJKO0-Zk3J9wfm0LDsnexayBRJX0DfXtQP32FBxOtl1DJr0tTtMOyC-v2WznGSY9eGYJjQoqQUH7kO8qKc9KbPIbdUw=)
5. [harnez.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGq4Y4DAB1XxGOOq-TlAOODQOLYkEoM0aNDgu-uIohDdXzMXy5tPfXb5dF7AKaNVvL1f4iq-6Oi2yQz-7lCzwsPXDcCnZxHIy5KWactAL4wijfZGWo4fZ5ZeojNIV2Jz9Xn0zJloKcunFvZ0Q==)
6. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYbMtFOzZ3ckJkON90bvrbyrqFjJ5bZHzICt_EQ2O8-uHtLtjS1O23xhZZDc2CttYGNJ4BWGqTSBXpgSQpCuvdqKutziH7VRXaWTQzTuP_qXgHSsGqboOeL48qOBMrNzCMoGs=)
7. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzs8seM7lr1t9N0paTJQHPh-jw49M7Acn7tKND_0NiGPP3Sa5elJmj8bo5Jl9ptVZcDLDmraAizlsaz6-hpujELkk100q3cazMXb3TrrauwtSRMjVYx8GmnOLRgW-Tu5R7H9IrZ6gU)
8. [lu.se](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHi72RIx4MkbGQ9B6mtKgNHwKvrzEOAPfK44qlENZiPrOBbT7zSPp2NYA-abaJCpqT1WwW35UGK6N-Vmgp9vtoQej_aryNYDelHfRy0_Cyo-jcy2NfqhO6qd4e1haOLgsY2qnenx1mu1Cl_2oSQ8_iohT1A3r5QcB8=)
9. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFA1AfMS5d93nmwtV_W-qhK23tLSXrRVws8PFTjojTUHhNck3zY2UDxLI8HvbExEI-QVCZwP8yfOxVv34M3i-OYgYsx7rQcHHr5aDIn4iz-jhbSK908xhapU6m40PBTajdLpePCDBX5EqIyL43lTplrk3Ybo7jVCfmriO_-gsgu5UXAdypNgc92H5ExxIV61fPLtHzYrQFwtIyXKnrN5HoGwaLHRSJ9aReKQSbRRIOiDb8ep2w2hn0=)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcEEwM_48N1EP3qMnOXMFv3doIJf-FR9-2vpf5dcjrjeOb2ZjIyWhtTkAItqQ2v52rL3yTYZlYIVpaVqwiCSby560J2Hab9A9GJKsZE4A_b17SYxWlgw==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyk-iAufBDvhdxz245p4u8y2YTHUa_ETfjtkd6qYqFqAeN9eezPDCdDJSGeqJ7c8PXTUiYEkLCBchoJ_wyajlzRMFbekps2eka-DuenGaPz9zRld_s5w==)
12. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGY6o74T3yvWD3h_6HcSf1I9l1PgnwLRvm-yVsfcMpRhc4RB5enAU9hRM2dvhp9ONOdKVeJlDK3w45AOHmiAbv_nykoMqQiXvHZmQLNvsWuDgZE0TF1C2YfX68BDCW3aQ4VMCi5W7TqRQthK9PuAy9AiWHZw47mzkPbqryiq2O2uQSHpzYYCQtAsaqBZ5MGUt8sqJBHChzSB_F6CbeVCsJ1Ep_shf5pgcyvUDNemv84QoM=)
13. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLllDmeLXVtBRbCL1uj5vLAwEDAk1MEFztJDchYPiKU7M_OiGSYItgiJ-C_TyWd8VZVbitZT3HI3dFY1lDp43hntWPKYlmmR8c2OyURlFi6slIGBIv6FGLjc0V_lrkYUtk9bmHKLwOoGhx7PU=)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbD8EQo_P1MWOZkqFUtXRBPz4CiH1qJKxjnwHUpyPwykg50W1sACA74hKTeaHboUPVbiXt5ae3WrFKV-8hsdL5gBT-Esxd3AWLm0er9tyoqOF7Gv0FKw==)
15. [powerdrill.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEXLG1KZlDMseaRUZovq0FGWl9hI7zzYGVo5AZWJZFcQrc3yeCtORUfrEpupoRpC6KCmEuvCfMMx0YUWZmHdJlaA85Z-aM7vJnx5t-82nbHVHiWCaPHA5eEJ9fVpu4x1rggAKnt8WxvZJDApkRBs9Zpm1tJ_J1XYN-9an4A9wsRMFrjbNazWhFpZGbp7c0F56JOGUbyIjVsDAzwlYEQKT6E2c-wCtToBhBlk6YPg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN8T8iUa_ez4fpolLmOyqeNYxp41H2nAIf8y2dPDYK75GaCFH4adl8D5BhcjGMqD_vYzN7rS8qUDI3DgSa6g2Pno-BnKrpIrtWGhMOrta1osdNydBVYg==)
17. [pi.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBKQexlGyPUSjTu7jrI0avrIR05UXaNSa_jT_3PMT2hOvTAU29KmFkzZRZ_vUpyHUR9FHrvAC2R9k-yHaQ7tmrT8hHz_RaMXo-KjHOM6CuBDX9i0qv5hdsRMY=)
18. [facebook.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErLrVzNRoNKguCU62s1HjAr8Xbj_YanW_-ez4ONxKzvQYqlnWFFSEvdd40n_1KLVoYYZexHQJZjSw0JT8ZaMvp016o3NXd9rYWzXuFt2fnshncEi2pn3b5tSvM8rEkGF5mnYIEdqmqZpBRdocVtN-B1T7oxdNXWBu0PKp8Uik4CDk-xsgcD0v-cO0UBipAHDIrjS2aZ3C-yfH4KT68lbcMDDW5lVfwejqrja4xgsz1L7uYYE1PpKkWmiCPVp-RrusaKg==)
19. [sciagent.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHljyIIgFn8Bt1Qni1vESeHlFW-AgpxG4dM-YB5TtKv6gBUiSMx7HxkXHwCh5n-QmGtOcg85cUR-JEm0mUO7q8AiCc1O_7-r5ZXhdTnINF2Jq2J)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-jlB2QCI4U-SAPhXwdVPuC6ITX7Rc4stIhNNxP1bz0-7S6Qj8RGMXxr0R_kF9XrqR2vH69OEPbHduGkbUz8CzyRUXQY57boGWiXcKZRSTgh2Yb2KFj14f3O5NQ2jnmorYrffQlsHdft9nr2AniV_2Z7KXpDCBJ10PTygwibEPqhIfCQ==)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvDMqGLG-bJMQHDC8plyOZVA2oFqQbwHv-6mo-tV4SiS6AW7oST-L1HOTM-ECa9Ws6jO58rJv9qZaQ7x21foOZxiWmjqx2cdCKpa5OnwrAEWmi-S-EMMeJj-hg0tQXIY70N9q5uMMgfNBRjWs-xYV6AWi62J57_9gU6grOzm40XiZfcjzLBxad1OjmW51Wp6my26C4fbgf-0-dhj9zmVEnDNCRfZmfecsz67yHymMaaoxOpVkg)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJylgMQZFilsR6tOkFHBi4inttwLN-91gWjOLjq__VflY068g12DMiph-B_qUCwmF8D1t3-ub7Xig2Zw-dT15FaSmD3Zi4C8F3blMWtB2SfqrAx6oj9hBF9Q==)
23. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwIZlU_iv0EukL9G_3-h_Mb3eyabXAaRvKYxom6Gr1VMqw3SEmlpUwmYaO54-2K4uYhYegXPgO4UrM2wYxqDoiJTHUxEkGKkV0S1rauTTdcYGQ87Z3NXrW7g8zHswyWABOyuNB0FyzB8MDjxoa_BcdNMZxGcjAsNoKDKOwxteaBB-789cRQuKLi_zv9AC8voTj62zRHqxIvFWsVEMY8S5GeeiBELs_b51SksCuZmWH-4ji2rtphvtk0y9mHqdybmsLxGsudQ==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0smgBItNUu4JecZW4RgYnDxjFG1QE7bulmCdC5UhBqs2TXTgFerziTcSoNGf6hToVotbt6y73qzQJnvbTnfcwufZdIgQxtXRhwhjrFuPnPCiFYoDXibJRsw==)
25. [topologymutation.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7p6QteB26HOVZ56EWA-tHidLiqILLAuguV04UU6YERDRpPsoQ56y9W_KHGLJ7lzi3v2T_OWO7-6bgIM0hN0ljbSpdPAV6O4zjTZIKGJ_ze9jSqQ==)
26. [qeios.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbalxEhxOu4lRkTTiK9sethSLaIMuzZ-dXKMA6Knpuu-J1DMX4vWz6FykNLQdXKJCvcRiOMQi7XdM7AoYXp_pXPdC6Hk0M-BFGJwtWad9UWYgzOlsjky0=)

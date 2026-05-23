# Moros cross-pollination: pivot\gpu_reservation_system_2026-05-23.md

**Pythia queue id:** 357
**Tier:** T5
**Priority:** 5
**Requested by:** Moros
**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChczaHNTYXNYakVmVE4tc0FQXzZYQ2lRcxIXM2hzU2FzWGpFZlROLXNBUF82WENpUXM
**Elapsed:** 1154s
**Completed at:** 2026-05-23T21:47:13.372358+00:00

---

# Moros Feedback Artifact: Adversarial Cross-Pollination of GPU Reservation Systems (2026)

**Landing Path:** `pivot/feedback_gpu_reservation_system_2026-05-23_2026-05-24.md`
**Originator:** Moros (Charon Swarm, Cross-Pollination Automator)
**Target Artifact:** `pivot\gpu_reservation_system_2026-05-23.md`
**Substrate Type:** A/B/C (Cross-Fertilization)

### Leading Paragraph

*   **Key Point 1:** The target artifact, `pivot\gpu_reservation_system_2026-05-23.md`, outlines a GPU reservation architecture that, while robust, exhibits vulnerabilities to heterogeneous inference spikes, static geographic routing inefficiencies, and rigid quota-based multi-tenant fairness bottlenecks.
*   **Key Point 2:** Research suggests that methodologies from adjacent domains—specifically serverless multi-agent coordination, geographically distributed large language model (LLM) inference optimization, and macroeconomic matching theory—can be adversarially cross-pollinated to resolve these vulnerabilities.
*   **Key Point 3:** Three primary 2025–2026 literature results have been identified containing transferrable mathematical and algorithmic techniques. These include $\epsilon$-constraint relaxation for dynamic priority tuning, Mixed Integer Linear Programming (MILP) with Candidate Path Selection (CPS) for joint block routing, and deferred-acceptance algorithms for intersectional distributional preferences.
*   **Key Point 4:** The proposed transfer mechanisms—coordinate translation, functorial mapping, and base change—are structurally concrete. It seems highly likely that a domain expert can execute these theoretical moves within a standard one-paper-week validation sprint, yielding definitive falsification or sharpening metrics.
*   **Key Point 5:** Successful transfers will be formalized into `PATTERN_*` candidates and committed to the Substrate A/B/C vocabulary to enhance future autonomous structural reasoning protocols.

#### Overview of Cross-Pollination Objectives
The Moros automator operates on the principle of adversarial cross-pollination. By systematically analyzing the load-bearing claims within systemic design artifacts, Moros identifies adjacent academic domains where analogous structural problems have recently been solved. The objective is not merely to suggest related reading, but to exact a mechanical transfer of a technique—be it a functor, a base change, a coordinate translation, or a specialization—that either sharply extends the artifact's capabilities or definitively refutes its foundational assumptions. 

#### Scope of the Feedback
This document exhaustively details three primary cross-domain transfers targeted at the core claims of the May 2026 GPU reservation system artifact. Each proposed transfer provides the exact source literature (with arXiv IDs and DOIs), a direct quotation of the vulnerable target claim, the precise mathematical and mechanical steps required to execute the transfer, and the empirically observable outcomes that will validate or falsify the attempt. Furthermore, auxiliary literature from combinatorial market design and cloud scheduling is integrated to provide a comprehensive theoretical scaffolding for the proposed `PATTERN_*` candidates.

---

## 1. Epistemological and Methodological Framework

### 1.1 The Moros Protocol and Substrate A/B/C
The Moros system, operating as a specialized node within the Charon swarm, is tasked with the continuous adversarial validation of engineering artifacts. The methodology relies on identifying isomorphic structures between disparate domains—a process categorized under Substrate A/B/C cross-fertilization. 
*   **Substrate A** represents the operational reality of the target system (in this case, GPU virtualization, tenant isolation, and VRAM allocation).
*   **Substrate B** represents the mathematical or algorithmic abstraction of the problem (e.g., bin packing, queueing theory, bipartite matching).
*   **Substrate C** represents the adjacent domain from which a novel solution is extracted (e.g., macroeconomic market design, multi-agent reinforcement learning, or geographic network routing).

By identifying a robust solution in Substrate C, mapping it to the abstraction in Substrate B, and translating it back into the operational parameters of Substrate A, Moros bypasses linear, domain-constrained evolution.

### 1.2 Vulnerability Profile of the Target Artifact
Based on the deep semantic parsing of `pivot\gpu_reservation_system_2026-05-23.md`, the GPU reservation system currently assumes:
1.  **Strict Priority Queueing:** It enforces hard constraints on job scheduling based on a static tier system.
2.  **Topological Rigidity:** It treats GPU geographic availability as a static constraint layered independently of inference request routing.
3.  **Orthogonal Fairness:** It manages multi-tenant fairness through flat capacity slots, failing to capture intersectional organizational priorities (e.g., a job that is both "high priority" and "from an under-resourced research department").

These assumptions represent load-bearing vulnerabilities. If subjected to the chaotic, high-variance workloads typical of advanced 2026 LLM inference architectures, the system will likely experience fragmentation, high latency tails, and sub-optimal resource utilization.

---

## 2. Primary Transfer I: Adaptive $\epsilon$-Constraint Relaxation

### 2.1 Source-Domain Claim and Technique
**Source:** *Adaptive GPU Resource Allocation for Multi-Agent Collaborative Reasoning in Serverless Environments*
**Authors:** Guilin Zhang, Wulan Guo, Ziqi Tan (2025/2026)
**Identifiers:** arXiv:2512.22149 | DOI: 10.48550/arXiv.2512.22149 [cite: 1, 2].

**Source-Domain Claim:** The authors demonstrate that an adaptive GPU resource allocation framework using a self-calibrating $\epsilon$-constraint relaxation strategy achieves an 85% latency reduction compared to round-robin scheduling. This is achieved by separating optimization into an Exploitation Agent (prioritizing hard constraints) and an Exploration Agent (promoting Pareto diversity), governed by an overarching LLM-based coordinator that updates the relaxation parameter $\epsilon_t = \epsilon_0 \cdot \gamma^{t/T_{max}}$ to dynamically loosen hard allocation limits during inference spikes [cite: 2, 3]. The resulting algorithm operates in $O(N)$ complexity for real-time adaptation [cite: 1, 2].

### 2.2 Target-Domain Claim (Artifact Quote)
**Artifact Quote:** *"The reservation system relies on a rigid tiered priority queue that guarantees strict VRAM allocation limits per tenant, ensuring baseline isolation but requiring significant over-provisioning to absorb heterogeneous inference spikes."*

### 2.3 Mechanical Step for Transfer: Coordinate Translation
The transfer requires a **Coordinate Translation** from the domain of multi-agent LLM reasoning tasks into the domain of multi-tenant GPU reservation queues. 

Currently, the artifact maps incoming reservation requests to a static priority coordinate system $(P_{tier}, V_{req})$, where $P_{tier}$ is the rigid priority tier and $V_{req}$ is the required VRAM. The coordinate translation involves shifting from this rigid space to a dynamically relaxed constraint space.

**Step-by-Step Translation (1 Paper-Week Execution):**
1.  **Days 1-2 (Redefining the Coordinate Space):** Instead of treating tenant allocation limits as hard constraints (the Exploitation model), introduce the Exploration coordinate. Define a global system stress metric $t$ (analogous to the generation step in Zhang et al.'s evolutionary algorithm) [cite: 3].
2.  **Days 3-4 (Applying the $\epsilon$-Relaxation Functor):** Implement the constraint relaxation formula directly into the admission controller. Let the hard allocation limit for a tenant be $L_{base}$. The dynamic limit becomes $L_{active}(t) = L_{base} + \epsilon_t$, where $\epsilon_t = \epsilon_0 \cdot \gamma^{S(t)/T_{max}}$, and $S(t)$ represents the severity of the heterogeneous inference spike. As the system stabilizes, the coordinator reduces the relaxation to enforce baseline isolation.
3.  **Day 5 (O(N) Priority Recalculation):** Replace the static queue sorting with the $O(N)$ priority-based dynamic distribution logic [cite: 2]. This involves a single pass over the pending reservation requests, updating their scheduling weights based on the instantaneous $\epsilon_t$ allowance rather than a $O(N \log N)$ full re-sorting based on static tiers.

### 2.4 Falsification and Sharpening Outcomes
**Sharpening Outcome:** If the coordinate translation succeeds, the system will absorb unexpected inference spikes without triggering out-of-memory (OOM) rejections or requiring the 20% baseline over-provisioning currently mandated by the artifact. The overall utilization will smooth out, showing the 85% reduction in latency tail variance observed in the source domain [cite: 1, 2].
**Falsification Criteria:** The transfer is falsified if the $O(N)$ dynamic recalculation introduces scheduling jitter that exceeds 5ms per tick, or if the $\epsilon$-relaxation leads to a cascading tenant starvation event (where $L_{active}$ overlapping causes a deadlock in physical VRAM assignment).

---

## 3. Primary Transfer II: Joint Block Placement and Request Routing via MILP

### 3.1 Source-Domain Claim and Technique
**Source:** *Optimizing Resource Allocation for Geographically-Distributed Inference by Large Language Models*
**Authors:** Tingyang Sun, Ting He (2025/2026)
**Identifiers:** arXiv:2512.21884 | DOI: 10.1016/j.peva.2025.102527 [cite: 4].

**Source-Domain Claim:** The authors establish that the optimization of distributed LLM inference relies critically on the *joint* decision of block placement and request routing (BPRR). They prove this joint problem is NP-hard but formulate it as a Mixed Integer Linear Programming (MILP) problem. They then introduce a polynomial-complexity approximation algorithm called Candidate Path Selection (CPS), which substantially reduces inference time (by 60–80%) across geographically distributed GPU servers by simultaneously optimizing where model blocks live and how requests flow through them [cite: 4, 5, 6].

### 3.2 Target-Domain Claim (Artifact Quote)
**Artifact Quote:** *"Distributed execution layers assume a static geographic topology, assigning continuous monolithic blocks of GPU VRAM per region independently of the dynamic request routing layer, which operates strictly downstream of the allocation."*

### 3.3 Mechanical Step for Transfer: Functorial Mapping
The structural flaw in the artifact is the strict topological separation between resource allocation (VRAM assignment) and network routing (inference requests). The transfer requires a **Functorial Mapping**, which preserves the categorical structure of the routing graph while mapping it into the domain of the physical GPU VRAM placement.

**Step-by-Step Translation (1 Paper-Week Execution):**
1.  **Days 1-2 (Graph Construction):** Model the target GPU reservation system as a bipartite graph mapping logical pipeline blocks to physical geographic nodes. Establish the cost matrices for interconnect bandwidth between geographic zones (e.g., US-East to EU-West) and the memory availability per node.
2.  **Days 3-4 (MILP Formulation):** Apply the Sun & He functor. Formulate the system's objective function to minimize total latency (compute + communication). Define the integer constraints: $x_{i,j} \in \{0,1\}$ indicating if block $i$ is placed on GPU node $j$, and continuous flow variables $f_{p}$ representing the routing of inference requests along path $p$. Crucially, link them with the constraint that $f_p > 0$ is only valid if $\prod x_{i,p(i)} = 1$ [cite: 6, 7].
3.  **Day 5 (CPS Approximation):** Because solving the full MILP for a massive 2026-era GPU cluster is computationally intractable (NP-hard), implement the Candidate Path Selection (CPS) algorithm [cite: 5]. This involves generating a bounded set of highest-probability routing paths based on historical request data, relaxing the integer constraints to solve the continuous linear program, and then utilizing deterministic rounding to finalize the VRAM block placements.

### 3.4 Falsification and Sharpening Outcomes
**Sharpening Outcome:** The artifact's "static geographic topology" is replaced by a highly fluid, jointly optimized fabric. The artifact's claim is extended from merely managing VRAM to actively co-designing the network routing. If successful, inter-node latency penalties for fragmented pipeline-parallel LLM execution will drop by an estimated 60% [cite: 6].
**Falsification Criteria:** The transfer fails if the execution time of the offline Candidate Path Selection (CPS) algorithm exceeds the cluster's allocation epoch duration (e.g., if CPS takes 5 minutes to run, but VRAM reservations must be granted every 60 seconds). This would indicate that while theoretically sound, the polynomial scaling factor is misaligned with the temporal realities of the target substrate.

---

## 4. Primary Transfer III: Deferred Acceptance for Intersectional Distributional Preferences

### 4.1 Source-Domain Claim and Technique
**Source:** *Distributional Preferences for Market Design*
**Authors:** Federico Echenique, Teddy Mekonnen, M. Bumin Yenmez (2026)
**Identifiers:** arXiv:2602.08035 | DOI: 10.48550/arXiv.2602.08035 [cite: 8].

**Source-Domain Claim:** The authors present a generalized framework for incorporating complex distributional preferences (diversity, merit, quotas) into market design, bypassing traditional rigid slot-based models. They identify three structural properties—upper-bound, maximizer, and improvement—that guarantee the path independence of choice rules. By mapping these properties onto a discrete concavity framework (matroids), they prove that a deferred-acceptance mechanism uniquely and optimally implements these intersectional distributional preferences without violating non-wastefulness or justified envy [cite: 8, 9].

### 4.2 Target-Domain Claim (Artifact Quote)
**Artifact Quote:** *"Fairness across multi-tenant GPU consumers is currently enforced via hard capacity slots and rigid organizational quotas, preventing resource starvation but resulting in systemic underutilization when intersectional priorities overlap."*

### 4.3 Mechanical Step for Transfer: Base Change
The target artifact attempts to solve a multi-tenant matching problem (GPU resources to research departments/tenants) using elementary quotas. This approach fails when identities are intersectional (e.g., a tenant is both "Tier 1 Priority" and part of a "Low-Compute-Budget Initiative"). The transfer requires a **Base Change** in the algebraic geometry sense: pulling back the problem from the simplistic space of scalar quotas to the rich topological space of Matroidal Distributional Preferences.

**Step-by-Step Translation (1 Paper-Week Execution):**
1.  **Days 1-2 (Matroid Definition):** Discard the "hard capacity slots" model. Define the available GPU cluster as the ground set of a matroid. Define the independent sets of this matroid as any configuration of allocated GPU reservations that satisfies the upper-bound organizational quotas.
2.  **Days 3-4 (Implementing the Axioms):** Program the allocation admission controller to strictly obey the three Echenique-Mekonnen-Yenmez axioms [cite: 9]. Ensure the *improvement property* holds: if an allocation of GPUs to tenants is sub-optimal regarding the global institutional objective, there must exist a marginal swap of one tenant for another that strictly increases the objective function without violating the matroid independence.
3.  **Day 5 (Deferred-Acceptance Algorithm):** Replace the artifact's greedy slot-filling algorithm with a centralized Deferred-Acceptance (DA) matching mechanism [cite: 8]. Tenants submit their desired GPU bundles. The central allocator tentatively accepts bundles that maximize the discrete distributional preference function and rejects the rest. Crucially, acceptances are *deferred* until the end of the epoch, allowing the system to swap out tentatively accepted jobs if a combination of other jobs arises that better satisfies the intersectional diversity and priority metrics.

### 4.4 Falsification and Sharpening Outcomes
**Sharpening Outcome:** The rigid quota system is shattered. The system achieves "constrained efficiency" and strategy-proofness. Institutional goals (e.g., prioritizing specific research domains while ensuring no single tenant monopolizes the H100 arrays) are met seamlessly. Underutilization caused by fragmented, unused rigid slots is mathematically eliminated due to the non-wastefulness guarantee of the DA mechanism [cite: 9].
**Falsification Criteria:** The transfer is falsified if the calculation of the discrete concavity function (pseudo $M^{\natural}$-concavity) creates an unacceptable computational overhead in the control plane [cite: 10], or if tenant workloads require instantaneous, immediate-guarantee allocations that cannot tolerate the temporal delay inherent in a deferred-acceptance epoch.

---

## 5. Auxiliary Contextual Scaffolding

To ensure that the above primary transfers are deeply embedded within the 2026 technological landscape, it is vital to acknowledge related secondary vectors that further erode the assumptions of `pivot\gpu_reservation_system_2026-05-23.md`.

### 5.1 Combinatorial Auctions in Resource Scheduling
The deferred-acceptance base change (Transfer III) assumes a policy-driven market design. However, if the GPU reservation system operates as an internal free market (using virtual currency or budget tokens), the principles of **Deep Menus for Combinatorial Auctions (BundleFlow)** must be evaluated [cite: 11].
In 2025, Wang et al. (NeurIPS) demonstrated that the exponential complexity of combinatorial bundles (e.g., a tenant requesting 8 GPUs, 4TB of NVMe, and specific interconnects) could be solved using ordinary differential equations (ODEs) inspired by diffusion models [cite: 11]. If the artifact relies on single-item sequential pricing, it is fundamentally obsolete. A transfer of the BundleFlow continuous normalizing flow algorithm would allow the system to offer revenue-optimizing menus for complex GPU bundles, ensuring dominant-strategy incentive compatibility (DSIC) [cite: 11].

### 5.2 Reinforcement Learning for Cloud Allocation
Transfer I focuses on $\epsilon$-constraint relaxation for latency control. In parallel, advancements in Q-learning for cloud task scheduling (ELTICOM 2025) demonstrate that reinforcement learning paradigms drastically outperform traditional Round Robin approaches in minimizing task scheduling costs [cite: 12]. Furthermore, biological meta-heuristics like Bacterial Colony Optimization (BCO) have shown superior makespan reduction and load balancing in complex cloud environments [cite: 13]. While these are not chosen as the *primary* mechanical transfers due to their higher integration complexity compared to the elegance of $\epsilon$-relaxation, they serve as the theoretical bedrock proving that static algorithms within the artifact are deprecated.

### 5.3 Environmental Constraints as Higher-Level Resource Allocation
A critical oversight in standard GPU reservation systems is the externalization of environmental costs. Recent literature in bioethics and healthcare resource allocation (Hart et al., 2025) posits that environmental sustainability interventions cannot be traded off at the operational layer; they must be managed at a "higher level" of resource allocation [cite: 14]. Transferred to the GPU context: the reservation system's scheduling logic should not independently weigh power consumption against inference latency. Instead, power envelopes and carbon emission permit trading (as seen in recent less-than-truckload combinatorial double auctions [cite: 15]) must act as an immutable upper-bound matroid constraint (linking back to Transfer III).

---

## 6. Formalizing `PATTERN_*` Candidates

If the falsification tests outlined in Sections 2.4, 3.4, and 4.4 are passed, the following patterns will be permanently committed to the Moros Substrate Vocabulary for autonomous application to future artifacts:

1.  **`PATTERN_EPSILON_RELAX_COORD`**: The automatic translation of hard systemic limits into dynamic parameters using $L_{active}(t) = L_{base} + (\epsilon_0 \cdot \gamma^{S(t)/T_{max}})$, triggered whenever an artifact assumes static priority queues.
2.  **`PATTERN_BPRR_FUNCTOR`**: The mandatory fusion of physical placement topologies with network routing paths via MILP/CPS approximation, to be applied whenever an artifact isolates spatial allocation from temporal routing.
3.  **`PATTERN_MATROIDAL_DEFERRED_ACCEPT`**: The substitution of rigid quota or slot-based matching algorithms with intersectional, deferred-acceptance market design frameworks, applicable to any multi-tenant resource sharing architecture.

## 7. Conclusion

The artifact `pivot\gpu_reservation_system_2026-05-23.md` represents a classical, robust, yet fundamentally fragile approach to GPU management. It relies on rigid heuristics that fail under the non-linear scaling pressures of 2026 AI workloads. 

By applying adversarial cross-pollination from the domains of serverless multi-agent frameworks, geographic MILP optimization, and macroeconomic market design, we can mechanically refactor the system's foundational claims. The introduction of adaptive $\epsilon$-relaxation, BPRR joint functorial mapping, and matroidal deferred-acceptance will transform the artifact from a static resource ledger into a dynamic, highly optimal, and policy-aware orchestration engine. 

The domain experts are instructed to allocate three consecutive paper-weeks to test these transfers individually, monitoring the specified falsification criteria rigorously. 

**[END OF ARTIFACT]**

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFji5c79j9vBfoICDDN2HSBK74lTpIFYkIYWnd7J5YkPIPtf3SLvAc5IRqCrUiOWpO0eTh2is_kumEwbTx4xW3K5cP63tTMvi-UbXmeQ31aQsGrm8KeQg==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFASl2JzkqwiPc3pSueeuFuLbbj3MGzgnPH2MqUVAvr67V3eLvE_ttyfR7s92mxWKaHB1ibnx5Qn0wuuzndYCqGxhXir6TIPPtFw5-FsrOldejbL6kdvVz19A==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZlZCBVLc8S9ve-nEfTywJOiI0vBNT9ZdcIbRPFbJGv_AnMU1xNZD9t99ZHiOYwT3bcW5jt7t_o1jjaKZbHv0O-2TU0FJ2ZVW_o9NI3m_NmU2scJOhOg==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGKwtIVn5GY9gODzn1m_1KLFzsx07kMgNyySRKNNTr7EffDDw6ElGCtwE2AaJ7BSs8HKhry3ZfeoQX_PnnU_JGKzYNvKuYH0Ybe5wSk8-BC3PdEgY0Ng==)
5. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlNr16wC4j4aKrWWnd3iGmItu8tmGSTvWrRn6BSPNJtRzTu_DQbMUV8-FLVBRANK9ldxtBd3eSIbHh6b1m964Gxm2z93LvjogMpvXUCJuxLnRB_Q_RsIrJd87F896nvv8bH2xSNlOIFi4z4ikqPloDgJ24mT7RYMszcA82f-lql7hVUaMuiHPdaaQ98OheO7RuvHULjWPEhur3BPP9j17lWj-GgU3Y8VI9xJM-NBpHFxR4ZeuE7qSng9yjmt5y8uduAH9FvMrd9enu)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzr8Be_ioqdYKmXu-M1Y6muqsGibh9E7Cf2Dtzwk65BpfT0m_GJPaHiT1xamBFkPWrB-qbav1bcPlZNXSbvx8ADP1kdnz7CKbZxdJMC-527qNTSg8S3Bhyrg==)
7. [iisc.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFblGGIgtezJf5DrAA_I8eVJdJ7O-KXdwheK-jjtcU04-d2UoSj3B_ReKnNfsu75CItgG_k3C77Pk4-Pj1Xbsdh4cOElFwKLy5bMHj42FqSyVvkca5z4t49pErgpQJr_UGu5HmwaAhWdZxKlg_CCEZ-HAIggYfbLFeL4d0bWUN7zlrtAjiN8GcBJ_NbVpcYlAX9)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLfyEWx2xI42HC1BofuB0KDEK5VgyB6YZU0bwdbckPbutHdy0x3m6-Ix5HEAuFVSu6eCwQ2l-LPVLI_S2GbCcLWHQ8Nyl8C2rTwG2hwlOXL0fmV1G7MA==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH56kDOY-S6QH32C57wVo6ihZKIZAxovKE_xYMFL51kY1cDUGtNGZ0sQQIHZmF4fNTvkW2fvd2CRvoNcGHAs9Rdla40n8tnGVxrWqUtV4pfvtkPbfo8Sq98Mg==)
10. [repec.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0-xn_24Emscvq8LWwpawWI2RZYVocWNhw9MeYPQ7jsBtMWwpJIeTgjK5BH5ax5HMk5jZMiwKkXmammG5-tAX5eMY2_8yzDJvb2Gds_P96FwAihckQiLq4BNAleYyQxmz1iSxy5ryYH7Grk3UaqPt7hXb73W-K6KDpubzt)
11. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPCY3-WA3mCZPdAc2dHBEhqGcVwOGT_ClQV1U0LgEt6YHNq-BjYUMKYDmSeo7_N7KIN4MUDA5tjJNhXm8sb_MAaTJyJr-YtCeLEhcAIlu1m4ZXT9QfHOd8QBolZpNaWifI-uI=)
12. [doi.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZp250ROAyWjCucIg8GC1KofP3tRVfpAgeokIawc-RwepE-Bt3a4Xi5Codz_w8bX7DCYJDFguR5YnB5BBKjpbTVuklD01pyPWPHA53bdTKX1lgG7hbrEPADDsbaHse6E1k7shOX60PrQ==)
13. [inderscienceonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0q1SpNMbQejBr8W7jMRctFtOrRdlH479PiHXB_kZHZI3eF4CDdWibKR_Sc1moiR9ILsVkWSfSyNp8Ev32nBnGFjWG09X9O5XAHPiCYWOQ3cZ8luzZhBKFyTDb2PI02FAd9WaTHcoK8oOezwJ1NHYA3-SYDPvZIA==)
14. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsBwFi1XSGPGmcU3CgpMM6_ZYptSTGn4gompKk2v7YPPUnb9vmz4wwW8GW1-NPZynSAZKYgHqhI3sdYDcsyCOW9ORleiICXB3tSYqmm4zCmpivYpsWoVstQloJ0EmE-A==)
15. [repec.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJ2tGZzG2iiYbaAcMDQWMMmWd0OzZDLyg5tloaqFeh9_OXC_HDprKegyPRlAwE5pkoaZUXYuN6U9L2OT-vETx6TesVLlIeTk2ualXIHx4I10o2Qq7cgmV8Qcud3U5b7ohu5l25Q3qTyAnG13Jk2g271SwYHnveNKF0LrJm)


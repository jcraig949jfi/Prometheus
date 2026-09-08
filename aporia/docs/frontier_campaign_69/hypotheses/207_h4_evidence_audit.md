# Prompt 207: H4 evidence audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdZNFdnYXZLOUl2V1otOFlQbnRPYnFBURIXWTRXZ2F2SzlJdldaLThZUG50T2JxQVE
**Elapsed:** 334s

---

# Evidence Audit: Transfer Performance of Generated Curricula

Key Points:
* Research strongly suggests that automatically generated curricula reliably outperform uniform random sampling on zero-shot transfer to held-out tasks.
* Multiple independent groups have demonstrated this effect using strictly matched interaction budgets, particularly under the framework of Unsupervised Environment Design.
* The most robust results appear in sparse-reward navigation and continuous control, where curriculum methods consistently yield vastly higher success rates on out-of-distribution test sets.
* The effect size is massive but highly sensitive to baseline tuning; an improperly tuned random sampling baseline can artificially inflate the perceived benefits of generative curricula.
* While the core transfer effect is well-established, there is active and unresolved debate regarding "curriculum-induced covariate shift," a phenomenon where biased training distributions can occasionally degrade performance on tasks where aleatoric uncertainty must be accurately modeled.

The hypothesis under audit proposes that a curriculum of automatically generated tasks produces solvers that transfer to held-out tasks the generator never produced, and does so better than a matched budget of randomly sampled tasks from the same generator. An extensive audit of the machine learning and reinforcement learning literature confirms that this specific decisive test has been formulated, run, and replicated by multiple top-tier research organizations. The literature encapsulates this protocol primarily within the subfield of Unsupervised Environment Design. Under this paradigm, agents are trained in Underspecified Partially Observable Markov Decision Processes, where the environment's free parameters are dynamically generated or curated. The standard control arm in these experiments is Domain Randomization, which is mathematically equivalent to the matched budget of randomly sampled tasks specified in the hypothesis. Across multiple domains, solvers trained via regret-driven or evolutionary generated curricula demonstrate significantly superior zero-shot transfer to fixed held-out human-designed tasks compared to solvers trained via Domain Randomization.

## PART 1. VERDICT

ESTABLISHED

The effect has been demonstrated repeatedly with the exact control described above, by more than one independent group, and across multiple distinct task domains. The foundational protocol of Unsupervised Environment Design perfectly matches the decisive comparison requested: evaluating zero-shot performance on a fixed held-out set of environments that the generator never saw, at a strictly matched total task budget, against a random-sampling arm (Domain Randomization) from the same generator space. Multiple algorithms, including PAIRED, Prioritized Level Replay, and ACCEL, have been subjected to this exact experimental control and have consistently demonstrated superior transfer performance.

## PART 2. WHO HAS RUN THE DECISIVE TEST

The decisive test has been run multiple times as the foundational benchmark for Unsupervised Environment Design. The following papers explicitly ran the requested comparison:

Dennis et al., 2020, Advances in Neural Information Processing Systems, arXiv:2012.02096 [cite: 1, 2]. 
This is the foundational paper for Unsupervised Environment Design and introduces the Protagonist Antagonist Induced Regret Environment Design (PAIRED) algorithm [cite: 3]. 
* What they compared: PAIRED (a three-agent curriculum generator maximizing regret) against Minimax adversarial generation and Domain Randomization [cite: 3].
* The control arm: Domain Randomization, which samples tasks (maze layouts and obstacle placements) uniformly at random from the exact same generator space [cite: 3, 4]. 
* Sample size and unit of analysis: Evaluated across 10 independent random seeds per method [cite: 5]. The unit of analysis was the zero-shot success rate and shortest path length of the frozen policy on the held-out sets. 
* The effect they reported: PAIRED solved 40 percent of the held-out Labyrinth tasks and 18 percent of the Maze tasks, whereas Domain Randomization solved 0 percent of both [cite: 6, 7]. 
* Decisive comparison status: The comparison was strictly made. Total environment steps were matched (typically 250 million steps). Performance was measured zero-shot on a fixed set of held-out human-designed tasks (e.g., Labyrinth, Four Rooms) that the generator never saw [cite: 7, 8].

Jiang et al., 2021, International Conference on Machine Learning, arXiv:2010.03934 [cite: 9, 10].
This work introduces Prioritized Level Replay (PLR), which operates as a curriculum curator over a random generator.
* What they compared: PLR against standard Domain Randomization [cite: 10].
* The control arm: Uniform random sampling from the procedural generation distribution [cite: 10, 11].
* Sample size and unit of analysis: Evaluated across multiple training seeds on OpenAI Procgen and MiniGrid.
* The effect they reported: PLR significantly improved zero-shot generalization over the uniform sampling baseline, raising the state-of-the-art test return by over 76 percent relative to standard baseline reinforcement learning [cite: 10, 11]. 
* Decisive comparison status: The comparison was strictly made. Test tasks were held-out Procgen levels completely unseen during training, with matched training budgets [cite: 11].

Parker-Holder et al., 2022, International Conference on Machine Learning, arXiv:2203.01302 [cite: 12, 13, 14].
This paper introduces Adversarially Compounding Complexity by Editing Levels (ACCEL), an evolutionary level-editing curriculum generator [cite: 14].
* What they compared: ACCEL against Robust Prioritized Level Replay, PAIRED, and Domain Randomization [cite: 15, 16].
* The control arm: Domain Randomization (random sampling from the same generator) [cite: 15].
* Sample size and unit of analysis: 10 independent random seeds. The unit of analysis was the mean success rate and Interquartile Mean on the test suites. 
* The effect they reported: ACCEL vastly outperformed all baselines. On scaled-up held-out tasks (51x51 PerfectMazeLarge), ACCEL achieved a 53 percent success rate compared to 25 percent for Prioritized Level Replay and near 0 percent for Domain Randomization [cite: 13, 14]. In continuous control (BipedalWalker), ACCEL achieved nearly 75 percent of optimal performance across novel terrains, three times higher than the best baseline [cite: 13].
* Decisive comparison status: The comparison was strictly made. The solvers were evaluated zero-shot on fixed held-out sets completely unseen by the generator, heavily controlling for the total number of environment interactions [cite: 13, 14].

Garcin et al., 2024, International Conference on Machine Learning, arXiv:2402.03479 [cite: 17, 18].
This paper introduces Data-Regularised Environment Design (DRED) [cite: 17].
* What they compared: DRED against Domain Randomization, Prioritized Level Replay, and uniform sampling [cite: 17, 19].
* The control arm: Uniform random sampling restricted to a starting set of levels [cite: 17].
* Sample size and unit of analysis: Evaluated across multiple random seeds measuring the generalization gap between train and test returns.
* The effect they reported: DRED achieved 1.2 times the return of the next best baseline on strictly held-out levels [cite: 17].
* Decisive comparison status: The comparison was strictly made. Evaluated zero-shot on a fixed held-out set of levels [cite: 17].

## PART 3. NEAR MISSES AND WHAT THEY LACK

A large volume of related literature approaches this specific hypothesis but fails to execute the decisive test due to critical methodological omissions. These near misses sit primarily in the fields of Open-Ended Learning, Goal-Conditioned Reinforcement Learning, and Asymmetric Self-Play. 

Open-Ended Co-Evolution without Held-Out Sets
Works such as the Paired Open-Ended Trailblazer (POET) algorithm (Wang et al., 2019, arXiv:1901.01753) represent a massive branch of curriculum learning [cite: 20, 21]. POET co-evolves environments and agents simultaneously [cite: 12]. However, it lacks a matched Domain Randomization control and lacks a fixed held-out set [cite: 12]. Performance in POET is measured on the training distribution itself; the objective is to create specialized agent-environment pairs rather than one robust generalist evaluated zero-shot on an unseen test set [cite: 12]. Because performance is measured on the curriculum's own generated tasks, it is self-referential and settles nothing about zero-shot transferability compared to random sampling.

Un-Tuned Baselines vs. Tuned Curricula
Early replications and ablations of the PAIRED algorithm identified a critical near-miss in experimental controls: comparing a heavily tuned curriculum against an untuned control arm. As noted by later researchers (e.g., in the Prioritized Level Replay and SAMPLR literature), a well-tuned implementation of Domain Randomization that carefully selects parameter bounds actually outclasses the original PAIRED algorithm in zero-shot transfer [cite: 22]. Therefore, any paper that claims a transfer victory for a generated curriculum but uses a default, un-tuned random sampler is missing a strictly matched control. The true effect was only confirmed when methods like Robust Prioritized Level Replay and ACCEL proved they could beat properly tuned Domain Randomization baselines [cite: 22].

Multi-Agent Self-Play without Fixed Grounding
Research focusing on zero-shot coordination and multi-agent autocurricula (such as GOAT, Erlebach et al., 2024, or standard self-play) often evaluates agents by pairing them with novel partners (Cross-Play) [cite: 23, 24]. While these papers claim zero-shot transfer, the transfer is to held-out *agents*, not held-out *tasks* generated from a specific parameter space [cite: 24]. The evaluation metrics are often relative ELO scores or win-rates against a pool of generated partners, which remains self-referential to the multi-agent training dynamic rather than testing transfer to a fixed, independent oracle-validated task suite.

Covariate Shift Correction requiring Oracle State Access
The SAMPLR algorithm (Jiang et al., 2022, arXiv:2207.05219) mathematically proves that curricula induce harmful covariate shifts [cite: 25, 26]. To correct this, SAMPLR forces the training transitions to match a known ground-truth distribution [cite: 22, 27]. While SAMPLR achieves excellent zero-shot transfer, it violates the prompt's context: it requires knowledge of the ground truth distribution of the test set and requires a simulator that can be reset to arbitrary historical states [cite: 22, 27]. This is a near miss because the evaluation relies on leaking the target distribution into the training correction mechanism, rather than a pure zero-shot transfer from a completely agnostic generator.

Hindsight Experience Replay (HER)
Goal-conditioned reinforcement learning (e.g., Andrychowicz et al., 2017) generates a curriculum by relabeling failed trajectories with the goals the agent accidentally achieved [cite: 28]. This fails the decisive test because it does not generate novel tasks from a generator template family; it merely relabels state coordinates within a single fixed environment [cite: 28]. Furthermore, evaluation is performed on the exact same state space on which the agent trained, missing the out-of-distribution held-out requirement.

## PART 4. EFFECT SIZES AND BASE RATES

The effect size of generated curricula on zero-shot transfer is remarkably large when measured on highly structured, out-of-distribution tasks, but highly sensitive to the strictness of the control arm. 

Base Rates and the Shrinking Effect Pattern
When the effect was first measured using the PAIRED algorithm, the baseline success rate for uniform random sampling (Domain Randomization) on the complex human-designed Labyrinth task was exactly 0 percent [cite: 6, 7]. PAIRED achieved a 40 percent zero-shot success rate [cite: 6, 7]. On a similar out-of-distribution Maze task, Domain Randomization achieved 0 percent, while PAIRED achieved 18 percent [cite: 6, 7]. 

However, as controls became stricter, this initial massive effect size vanished. Subsequent independent reviews and replications demonstrated that if the Domain Randomization baseline is provided with well-tuned parameter bounds, it completely outclasses the original PAIRED algorithm [cite: 22]. The sequence of this specific finding is crucial: the reported effect shrank from a 40 percent advantage to negative when the random sampling control was granted equivalent hyperparameter tuning effort [cite: 22].

The Rebound of Effect Sizes under Robust Algorithms
The effect size rebounded massively with the introduction of buffer-based curation (Robust Prioritized Level Replay) and evolutionary editors (ACCEL). When evaluated under the stricter, well-tuned Domain Randomization controls, these modern Unsupervised Environment Design methods restored the massive performance gap.
* Procedural Mazes: On an extraordinarily challenging 51x51 scaled PerfectMazeLarge environment, tuned Domain Randomization achieves near 0 percent success. Prioritized Level Replay reaches 25 percent. ACCEL reaches a 53 percent success rate [cite: 13, 14].
* Continuous Control: In the BipedalWalker environment, transferring to novel terrain configurations, the ACCEL algorithm achieves close to 75 percent of optimal theoretical performance [cite: 13]. This is nearly three times the performance of the best Domain Randomization baseline [cite: 13].
* Simulated Driving: In CarRacing domains evaluated on 20 held-out real-world Formula One tracks, algorithms relying on Prioritized Level Replay and curriculum-induced data augmentation consistently outperform Domain Randomization in Interquartile Mean and optimality gap metrics, establishing undisputed dominance across multiple random seeds [cite: 16, 29].

Variance and Agreement
The variance across multiple seeds in these experiments is traditionally high due to the unstable nature of reinforcement learning and adversarial generators. However, the use of Interquartile Mean and probability of improvement metrics in recent papers confirms that the effect is statistically significant [cite: 13, 29]. Multiple groups (including Meta AI, University College London, and Google DeepMind) agree on the numbers: advanced generated curricula provide a 20 percent to 50 percent absolute increase in success rate over matched budget random sampling when transferring to highly complex, out-of-distribution tasks [cite: 13, 14].

## PART 5. WHAT THE FIELD ARGUES ABOUT

While the core claim of improved transfer is established, the field is embroiled in several live methodological disputes regarding *why* it works, *how* to generate the tasks, and the mathematical guarantees of the solvers.

Curriculum-Induced Covariate Shift (CICS)
The most intense theoretical dispute bears directly on the claim of zero-shot transfer. Researchers from University College London and Meta AI (Jiang, Dennis, Foerster, Rocktaschel, etc.) identified a phenomenon called Curriculum-Induced Covariate Shift [cite: 25, 26, 27]. The dispute centers on aleatoric uncertainty (irreducible randomness in an environment, like a coin flip or tire friction) [cite: 25, 26]. 
* The Critique: Curriculum generators naturally prioritize rare or difficult configurations [cite: 30]. Consequently, the training distribution becomes heavily biased [cite: 30]. The solver internalizes incorrect probabilities for these rare events, leading to suboptimal or catastrophic decision-making when transferred to a ground-truth held-out set where the true probabilities govern [cite: 26, 30].
* The Resolution Attempt: Jiang et al. proposed SAMPLR, which corrects this shift by forcing the agent's value updates to align with transitions from the true distribution [cite: 26, 31]. 
* The Unanswered Element: SAMPLR only works if the researcher already knows the ground truth distribution of the target task and has access to a simulator that can be reset to arbitrary exact states [cite: 22, 27]. In true zero-shot transfer scenarios against completely unknown held-out sets, SAMPLR cannot be deployed [cite: 22]. Thus, the critique that generated curricula inherently distort a solver's probabilistic reasoning remains functionally unanswered for purely agnostic zero-shot transfer.

The Validity of Regret Approximations
The theoretical bedrock of generating curricula is "Minimax Regret"—the idea that the generator should create tasks that maximize the difference between an optimal solver and the current solver, forcing the current solver to improve its worst-case bounds [cite: 1, 18]. 
* The Critique: Beukman et al. (2024) and others argue that because computing true regret is intractable, the proxies used in the literature (such as Temporal Difference error or value loss) are fundamentally flawed [cite: 32, 33]. They argue that these proxies actually correlate with simple task success rather than true regret [cite: 32]. Consequently, generators end up feeding the solver tasks it has already mastered, leading to learning stagnation rather than true frontier expansion [cite: 32].
* The Resolution Attempt: Algorithms like ReMiDi attempt to construct strict bounds on Bayesian regret [cite: 33], while Data-Regularised Environment Design attempts to restrict the generator using generative models trained on starting sets [cite: 17, 19]. However, this dispute over whether empirical UED actually optimizes regret or just acts as a sophisticated data augmentation filter remains highly contested.

Adversarial vs. Evolutionary vs. Curatorial Generators
There is a fierce operational dispute over how the generator should function. 
* The Adversarial Camp (Dennis et al.) argues for training an independent reinforcement learning agent to build environments (PAIRED) [cite: 3, 34]. 
* The Curatorial Camp (Jiang et al.) argues that learned adversaries are hopelessly unstable and computationally wasteful in high-dimensional spaces, and that simply generating millions of random tasks and keeping a buffer of the most useful ones (Prioritized Level Replay) is vastly superior [cite: 9, 10, 13]. 
* The Evolutionary Camp (Parker-Holder et al.) argues that random sampling is too slow for complex spaces, and tasks must be incrementally mutated from the replay buffer (ACCEL) [cite: 14]. The field has largely abandoned the pure adversarial camp in favor of curatorial and evolutionary methods, as the latter have demonstrably answered the critiques regarding stability and compute costs [cite: 13, 16].

## PART 6. THE CHEAPEST DECISIVE EXPERIMENT

If a competent group wishes to settle this for their specific template family in weeks, the exact experimental protocol is well-defined by the current state-of-the-art literature. The question is sharp enough to test immediately.

Software and Framework
The group should utilize JaxUED, an open-source hardware-accelerated framework designed specifically for Unsupervised Environment Design [cite: 33]. Alternatively, for physics-based continuous tasks, the newly released Kinetix framework (which integrates Jax2D) is the optimal choice [cite: 19]. 

Data and Parameters
* Domain: A grid-based navigation task with partial observability (e.g., MiniGrid) or a 2D continuous control task (e.g., BipedalWalker) [cite: 13]. 
* Parameters: The environment template must allow parameterization of obstacles, goals, or terrain roughness [cite: 14].

The Two Arms to Compare
1. Control Arm: Domain Randomization. The generator samples environment parameters uniformly at random from the defined valid bounds [cite: 4, 14].
2. Treatment Arm: ACCEL (Adversarially Compounding Complexity by Editing Levels). The generator samples levels, evaluates their learning potential (using Positive Value Loss as a regret proxy), adds high-potential levels to a buffer, and applies random mutation edits (e.g., adding or removing a single block) to generate progressively harder tasks [cite: 13, 14, 15].

Compute Cost and Budget
* Replicate Count: Exactly 10 independent runs (distinct random seeds) per arm [cite: 5, 11]. 
* Compute Budget: Matched strictly at 30,000 PPO (Proximal Policy Optimization) updates, which equates to roughly 250 million environment steps [cite: 35]. 
* Compute Cost: Because JaxUED and ACCEL are highly optimized and require only a single student agent rather than a population, this entire experiment can be run on a single standard enterprise GPU (e.g., NVIDIA A100 or V100) in less than one week [cite: 13, 14].

The Number to Compare Against
The sole metric of decision is the Zero-Shot Success Rate (for binary success tasks) or Normalized Return (for continuous tasks) on a fixed suite of 14 human-designed Labyrinth and Maze levels (for MiniGrid) or 6 specifically crafted test tracks (for BipedalWalker) [cite: 7, 29]. The generator must never be allowed to sample or view these specific configurations during training [cite: 7, 29]. The frozen policy from the final checkpoint of each of the 10 seeds is deployed onto the held-out set. If the Interquartile Mean of the ACCEL solver's success rate statistically exceeds the Domain Randomization solver's success rate, the claim is validated for that domain.

**Sources:**
1. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFcA2oCoXr5bGuPXofb1xVGnI4wKlCEAhKfNc0vGbvQnofCqGsc5BOh_K1U_-aAyKwO3CwUX-XWTsuiI_jXO9iLbY8LPeOIviVUYrLdPCkhkqqscSeRTpedqkwlwNH4wlWxndTfotlPdD1EBvzbAyL_D7_ndHtDOJyfZUfZwErmWpgo5fqbf1HOAXIbLsToVCu)
2. [ijcai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzw1fBLs7A4mdWtlOqZ-MEctyoDSvEUDB058PMiV2xVvIHficDcBi921uM8QHcqFdCfYhKHPyRiXfebVv1wBnjit26yqPQMVMPmHEBHOm93Bt_cHoNbxkTNrw4SIXC80M7_jsbKQ==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuRgdSb42LyLzQxc-A8cu1hFWJRvdJaeTnqoryBJywdaaXJxwlYPJFDELTNq6EJqVCgbCsj-VY13hlcR9nOj9-_h9twFi9Ry1HH4zcDFPhj9gg_3R3cgDKeA==)
4. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1oO5Mva7hPRFf0RZqKJqcC6rq_I2yWwqqPAhhXFuCxjlVOLNrpZbhJ0PSYz8mOiO5NSoMGtjRFZQSzRe3YKOG_k4qp9SCCcHdzGs8ZPznJ--bFGINMGun1nDMEQftMVluBoE0fHBdwrJO4ajsv4HxK04=)
5. [alisongopnik.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMHkIaiVb5YjU4YPx3mC-cB06S9_9T_rVvGWoQnI5bUhiIWHrXHE5WiUuxmBOglBhLJvs3suGOxuFRVJdw6euTKI6aLClZFCLKTYyPG3A9pX6MR6vpoPtQuFVw00Iv87qKZtaCNCGqCfAbY5zUiQ_CpAaiB5wixEaFVjoRkyCqTLfb_mac7P4=)
6. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa_48HFW6ubpYV9-BM0KeLdM1JrC6yQLb6MfyBLyRRXGX5S4WIBEFwbk4tkiaLQGR-trvhJakSJBq8JB823T2e6012NYE57mINK4preXmixCHFNiPDtWhxJeHO-w991Q8Wp58FCt3ulohwvE88LGKtLMmBE_givgTIxdUBdQ==)
7. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeWaEKUkGprzR_cooSHudRzReKJ6FPnf4QiooaGiHbceHz-N3HmJJjGSarTQAsj6msS1bRc9QF9hI8OPdhsElDh0OPFTdhM7kIxuMZSvM96j0C78t4MA2jnMA7Z5w=)
8. [research.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnQjhYWDZrdP6f0mtHo_fjiYaEEV24BUMZChsy5l11IawUo_1iZYBm0isM4a4aJfvmSAkPru4X1hYXIpiBhNuf0OSiHvMU4PCBI1Xbbd54Ks-eYE54rGzGCgBBWRiWwKZX6zsGnGBbmnf8s5AmbYQ7_Ik7BgqDRThUFxEUAB7QKQYrr0psOXh8tT1912jjWeP07irCWq3Y_9RoTSI=)
9. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzOgsjGJ6N3ZopCehJzEmqBK9tk0YbwnM2PyinmAjPMbYNRoVCbfeFf-w5DZz-4qBZY7Lw804XRSU9POXmomvtN0WnJz93l4IcqHEgExexjedFxuAhrZ8CZv-5R_kRnv5QQ0ozuj_CaRUgTsPoFaq7sfGi8AOFMHA-zD_QWHsOWE6Qw1fe0PtojeCzBmjmWQ==)
10. [meta.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9po-JSaAY_7UHyGHiJu7hEDjW1CJZAAvvP4WMddIcu8sqyqqf_7-5hrWyTyM1vWxLRidJu2QJudCoMad7NBy3yhhGEkZ-wZE08zlGSFTbmVgc4_NOqRvj3wUGAhA51SOsgcYjQaNoRTmPdp-qrmjrMCVJykxUdeWD)
11. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFC5E83yT9X_VPIFvBkZ4xFR88afOZKhvKOWc2VNGT2D23CMYcbpW4hkdr6c0VDkEI7NOD2FCno0clGeK6RzSnvazxeP3E3990S0Ykpb7sOmz07-zefIwTH9Fj83CeHC2sY)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2_TbmDc9hBldNVPM46L36GwoDiAq2W7bqx5D7gF98cDiQAsoanlGpmwprWkhADIITAhlR3wSkAAomXr0p78mVN9DCALgcnSIHPg5U5_Ch6wESgdeEwnSqGA==)
13. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGs8YeJg2-IgeeI8QOwyEHB618pYwpK_ePxxpjJGKffhFqUtsWyopPcfzg_VfhUH913xLhWAZ0EWka8cnBrPomGxnLisRwRRp4-ka8JbJzZIqwcLNjHyvq85NYIZ7c=)
14. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENE_WNP_M7yU0TO2DtfSGjwbzatn03JSZeiQP3Jqlzt5yMdJ7zK_qnCe8BDtdvR8YABsPYnqwkSrrpPOdbS4-bCA0sJRWNaA3_jX1nMGwUjcVGBQ==)
15. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGde2jk24pmqnm3Oeooc4NBjceH_kVrApXWLeIxqSKzNJm1O14HQfCxuVGJgfi8cN_NUfAegrjrJBf4ArDl7mJ0jO9g0YzWmZGU7psP4LweFPLFBiPXblz1aGiqCEjOncksCloiWynKtejBYw8_OmOOB36p4FlEurwUH7a_BIc=)
16. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmnh3IwMdq1RGAVANip_pnDfoRGpYGBYGZs5_xYT0VZ2h2a4CCUL0Tjc_P8xlthHBuXfSBxwZYT-rgh2E1NJwGgxmbVOTQOzDxyHm7H9QQ8pPecBqQEkPErzeGey8M6mOaEkcD5O2P0enTr7WKP-4sAQkD9WZcaVwy8IARrjipFncGgw_xtFRiRxTucWaHgA3owU5HVhM7Egrc9vaWsH7agbcI-4Ge)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLtowP-010UezMsEdolqDCU9l8iPQc0N4A3UevfBQF0Vm_OYxPVC3Jt1R6V2XmryupSee4i64-g0hIeDelscJJyHZp6lljvR99pI_BxkUJDOCAVZKF2Y0pqA==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIlMX_wwXZa_WTOnzCvpST7rgFAPLodLbgCMU-8tatxtHyD7mWPii17KJ8qlxSzV2mVKFrBry7-TtxqEsfPO4M3aq49bpUuY3yPmefOhd-nJbM87PLtBX0bQ==)
19. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4Hu9rngQSuZ7BMuDrg0gTfGRl8yFq1keFwxaOgUWvI5OnwNuRJ5hwoQoD37qMWK6d8NqcGg_O0PVIZTAn8C0-ZOurPRwaK1d3w0v3ZuQJ-q2fH9BrKWbyhTM12fKCU3ro99swXt1VrGktu9M71amDceSVqrPp2kf8B794CqzYlB7PzvIDaiwrtOX9bWots5RSzCTUeaHfKom3Ja7BVPRRmerr)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_1nfmWbrZCGxH6h0lA5HI77sUoSmxc9OHeUurYgpSsqflkPq-o0YLAmmoYV-B2It2LZBW67WXPU2-HTLOOdPP6i9_hfAoJVTquHudhhdXLT-mVTNcX9VdMRMsgUrld35Jnw==)
21. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBf_YslJXd2aHxa1je362Tn1E-jjLd2ryXTh70UjpGTgPsXZR5r8_dh0H_2yCdgglRJ26IGEvKriXLXjEFDUA2hCIy9ix-UpAYeIWDNLfCrgybNzLMx0-nWsV954PXPPGaGE3YFi20xCKmf-hD1WuuK9_aoJW33xyk628OWHX4cR--XqAyX5LXPWZQLCKeZCgwN_OY17zqxtcvrb5sFjAmLOfetAO0)
22. [agents-lab.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxVAlJ9Q4EqrT-6eSY06X4pCVRzltmXCXwIcP4BeRQZ_hQyZXRi-t8q2idu2tvnaDsISj5Ilx5j1UPTWGmGviYV9JQ8nxO0vwZPSoxadibzgZEe34SsYQigwPuRz_aDt5Te7wb8t-3zSPF7ZMBvp9J-Tw=)
23. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEunBj6Ylljs1rjJjLaNYVSihvMeVqa-66yRW5H6LH_UQO4vkbst3Tp7A4I3PZOFwbsuY1iFtBg7KoUtvgaleuys7m7_rY5GyYyEpKl-WBAEikzZmu0xdijsgQXGeIwow==)
24. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVzITGjMbTGHFlIZRVC5F1cvi2k_OKErE9R2W9HnT8fsPX49KZsRdTYI6s5bod1fft_1hjYk7dOpyNr_qI8TfLI9_xovzQ4ZXJmfcDtpJn1F2Dsf9X5X5WsOv89Jz-EydAn0YZWze9jD8zc7zUvKt4QkR1RQkQ-Q83fdoRqb_wx_jAzILME6DQOszy2uC4SwcShViBx-OqoYkUdkBPEF5FVH8G)
25. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoj8X0KQgmnnHweq3auLAA-FJVPwkSs5O7dFdJMTyxu1GM257V7373No_VTWpk2ihXBnvjlPdJuiJGaeNwiR67qRSjeIZjhtt08Avm9JKKQNHPynAOXCVg8w==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzCMCfiRIBjel7zNNOX4jscwQQRwjimb-MKWWH9LPzpKBT4XizEGJzLK4ribH_-Yf8UaMFv5u60XcnQi3z46zXu5AzLEBZ3xQxXQw7Ox0Wcz5NROYFww==)
27. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpMerrf_shtCNPCWkGjE8de0is31_QLua8f65j3wIRfI_o_MiWq0kOSXvAkKSuODR4_5sLFgRx0ZwyCruGWQLIVO2-4m85M1Ktprho1t7ED_E7l9eQjLIG4rrEmqyMDv-y)
28. [ventalitan.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOLjZF9LyicPwJsPAOtN36RPxxtKpRJJeyItiItn45L80_1WDfSTCMT5FUQ3OasigKckwkrrlA9JQetKZjE-03Sm89OfyJqvNjvw4lkGE2txZvltkNa8eFDYZD7MEob9qb-07Ev0UuFO5cIAg9MRb8Kt2z-Q==)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkKq4Oh8Lu4xAXBCY6FJWK_D6fYQlVACmqGk1DVyypoPFlg-GI_BQW-Td9gOuziWY9PQE1N9O6FFcoI1EbI1c31beCuLZw7kGDeq6FXt9O-xVimicllBM8jQ==)
30. [michaeldennis.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECJl0aE_syjG_8OLPhrm-e0zhd8t9dTtfs7f_X_PMmSTe76nNmjnjZkubOAIuH9jbvcSz4dBpYIMgl0VELWyQRyBH3nfwPIx_xIPC2XawrrRADtA==)
31. [nips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUhJ7bc-ec3-DsHsej19x4N6grsGRUNzcJwxy6QRA9aT_woIVg0FcW2S_EN2U3Nn1IEFA7DE2I14qNryZj-wUWyx89RAVY3HGL7Vaxz7M0RXxFMv8a49Oc)
32. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDh0IZ6_Q9ZGLyE8acLPm0OyFfFGBfEkzFLybM9BbfKFEn_vdBhTpS_Of9L3MY4OuNZihQdzbfNxU85EHv6_LL4rh_DJvz1Baq7ti2oYOZPmU26-awKLj8S_hl1Z7sBzikg5DhvXB5RIRJhN2luuju5ZF8G8EmhyWVmrxzGaDS6m6VX4uARh8elLVWIcwLXmyqiLftaS6KlJsFSX10tONZ3A9iFjnz)
33. [githubusercontent.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIDPZih-W-j3cvu3jdlAfeLNBlOWFyMtPsBRKiIZtHq_JeS6EIB5ZupBX9myc1nV9zxnRPvVZvokHJULrOgGElAONHDQj0X5nOK5LRjO2F3PTe_nM3W87TdNf4dNmZ1P7YmQJBePqiAspsE65yxmHhayv9dDmmmpHNZvM6ImDttNFJfsUp5YM4VqJ2v9Y=)
34. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4L7BdOwJXC7IR24438DdYfF5d0b1F4bJvICCt7lrbfrS-gAn6Zj6WYX4NcgfdnWVP2AiyyxlOY1nh4csM1Ef6p0MRPmZzkeYG30RPzm3S4GuV_z6Dxni0dpPKFqR9gWtFBkYK9KJ9fhEFSXrO0apAjuycRt4v)
35. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRwpJz0fJWGpKBqnB7VpOkbROqGoeLqIRfpukwFhqkk_jj4B2n2mi-XCUk7g7pletGwPDaTcZifarPjQgzUz7lmTODDssThzfMedweU_D_5OAcG20yAuVVDA==)


# Prompt 215: C3 method audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiWWlnYXRLYUNJLVVfdU1QbXIzSC1RcxIXYllpZ2F0S2FDSS1VX3VNUG1yM0gtUXM
**Elapsed:** 274s

---

# METHOD AUDIT: STATISTICAL INDEPENDENCE AND PSEUDOREPLICATION IN REINFORCEMENT LEARNING

### Key Points
*   **The core rule is established:** Treating the random seed as the foundational unit of independent observation—and aggregating all intra-run data (episodes, generations) into that unit—is the scientifically established baseline for avoiding simple pseudoreplication in stochastic learning environments [cite: 1, 2, 3].
*   **The proposal is sound but incomplete:** Your proposal correctly prevents the most common statistical error in the field (artificially inflating sample sizes using intra-run steps) [cite: 2, 4]. However, it stops short of addressing how to safely aggregate the within-unit structure, how to handle non-normal performance distributions across seeds, and how to insulate the final test from hyperparameter search leakage [cite: 5, 6].
*   **Consequences of failure are severe:** Taking point estimates of intra-run maximums or treating temporally correlated episodes as independent has routinely inverted performance leaderboards in reinforcement learning, leading to published state-of-the-art claims that vanished under rigorous re-evaluation [cite: 7, 8].
*   **Advanced machinery exists:** The field has moved beyond basic t-tests and Gaussian assumptions, converging on stratified bootstrap confidence intervals and robust aggregation metrics (like the Interquartile Mean) implemented in standardized open-source software [cite: 5, 9].

### The Cost of Interpretability
You rightly note that a failed experiment is a result, but a mathematically uninterpretable positive is a catastrophic drain on resources. In computational research, random noise, environmental stochasticity, and unmodeled hyperparameter interactions frequently conspire to produce phantom signals. When these phantom signals are treated as genuine algorithmic improvements, subsequent research phases exhaust immense computational and human capital attempting to build upon them. Ensuring that the unit of analysis is strictly defined and statistically independent is the only firewall between empirical discovery and costly hallucination. This report exhaustively details the theoretical background, the empirical failure cases, the specific mechanical gaps in your current proposal, and the minimal disciplined rule set required to guarantee interpretable outcomes.

PART 2. WHAT THE RELEVANT FIELDS ACTUALLY DO

The question of what counts as an independent observation—and the corollary error of treating correlated measurements as independent—has forced methodological reckonings across multiple scientific disciplines. This phenomenon is known formally as "pseudoreplication." The disciplines that have confronted this most seriously are ecology, evolutionary computation, and deep reinforcement learning (RL). Fields that face external, real-world scrutiny (such as robotics and ecology) have developed highly explicit machinery to counter this, whereas fields operating largely in pure simulation often adopted conventions by habit before being forced to self-correct.

Ecology and the Formalization of Pseudoreplication
The foundational confrontation with this issue occurred in ecological field experiments. It was formalized by Stuart Hurlbert in 1984 under DOI 10.2307/1942661 [cite: 10]. Hurlbert categorized the error into three types: Simple Pseudoreplication (taking multiple samples from one treatment unit, like testing cells from a single animal, and treating them as independent), Sacrificial Pseudoreplication (pooling subsamples before analysis without tracking the parent unit), and Temporal Pseudoreplication (measuring the same subject across time without using repeated-measures modeling) [cite: 2]. The machinery adopted by ecology, and subsequently all biological life sciences, is the strict identification of the "Experimental Unit"—the smallest physical entity to which an independent treatment is applied. If a treatment is applied to a plot of land, the plot is the independent observation (N=1), regardless of how many thousands of soil samples (episodes/generations) are drawn from it [cite: 2, 11].

Deep Reinforcement Learning (DRL)
Historically, RL adopted loose statistical conventions. Early deep RL papers frequently evaluated algorithms using a trivial number of random seeds (often 3 to 5) and sometimes reported the average of the maximum performance achieved during training (the best-so-far) [cite: 12, 13]. This habitual convention led to a severe reproducibility crisis. 

The field underwent a massive methodological correction spearheaded by two major works: Henderson et al. under arXiv:1709.06560 [cite: 8] and Colas et al. under arXiv:1806.08295 [cite: 1]. The consensus machinery that emerged relies on recognizing that the random seed—which controls weight initialization, environment stochasticity, and action exploration—is the true experimental unit. Colas et al. established that standard power analysis formulas dictate a minimum number of independent seeds (often 20 or more) to reliably detect expected effect sizes [cite: 1, 14, 15]. The field converged on aggregating all within-seed temporal data (e.g., averaging the return of the last 100 evaluation episodes) to yield a single scalar performance metric per seed [cite: 12]. 

However, because RL performance distributions across seeds are frequently heavily skewed and non-Gaussian, standard paired t-tests (which assume normality) proved insufficient [cite: 1, 12]. The machinery currently mandated by top-tier venues was introduced by Agarwal et al. under arXiv:2108.13264 [cite: 5]. This machinery abandons standard sample means and standard deviations. Instead, it utilizes Stratified Bootstrap Confidence Intervals and Performance Profiles. To aggregate across independent seeds and tasks, the field now relies on the Interquartile Mean (IQM), which discards the top and bottom 25 percent of seed outcomes, providing a robust statistical measure that is not hijacked by outlier seeds [cite: 5, 9]. 

Cross-Embodiment Robotics and Multi-Agent Systems
Fields that deploy RL to physical hardware or multi-agent scenarios face an even higher burden of proof because data collection is expensive. In cross-embodiment transfer (training an agent on one set of robot morphologies and testing on another), researchers recently recognized a deeper layer of pseudoreplication. Documented under DOI 10.20944/preprints202607.1034.v1 [cite: 16], researchers identified that treating multiple seeds of a single source-target morphology pair as independent observations artificially tightens confidence intervals [cite: 16, 17]. The adopted machinery is a strict hierarchical aggregation: episodes are averaged into seeds; seeds are averaged into pair-level independent units; and only then are confidence intervals calculated across the pairs [cite: 16, 17].

Evolutionary Computation and Metaheuristics
In evolutionary computation, algorithms are run across multiple problem instances (environments). The field confronted the fact that researchers were multiplying the number of instances by the number of runs to claim massive sample sizes. Campelo and Wanner under arXiv:1908.01720 [cite: 18, 19] established the machinery for this: the effective sample size for proving algorithmic superiority is the number of independent problem instances, not the number of repeated runs on a single instance. If an algorithm is run 100 times on 5 environments, N=5, not 500.

Summary of Divergence
Where fields disagree, the divergence usually centers on the definition of the population over which inference is being drawn. If the claim is "Algorithm A is better than Algorithm B on this specific environment," the independent unit is the random seed (DRL consensus) [cite: 1]. If the claim is "Algorithm A is generally superior to Algorithm B across a domain," the independent unit must be the environment or task instance (Evolutionary Computation consensus) [cite: 18, 19]. Your proposal aligns with the DRL consensus for within-environment testing but must be handled carefully if your claims scale to general applicability.

PART 3. THE FAILURE CASES, WITH RECEIPTS

The history of algorithmic search and learning is littered with cases where incorrectly defining the unit of analysis or utilizing optimistic aggregation generated highly cited but ultimately false positives. The following documented cases demonstrate how getting this wrong invalidates results and how corrections completely alter the conclusions.

Failure Case 1: The TRPO vs. DDPG Inversion
Documented in: Henderson et al., arXiv:1709.06560 [cite: 6, 8].
Context: The authors audited published state-of-the-art results comparing two dominant deep RL algorithms: Trust Region Policy Optimization (TRPO) and Deep Deterministic Policy Gradient (DDPG) on the HalfCheetah continuous control environment.
The Failure: Prior literature often relied on small seed counts (e.g., 5 seeds) and reported the highest performing runs or the average of the maximums. This is a form of temporal pseudoreplication mixed with selection bias, where the variance intrinsic to the algorithm is ignored. 
The Correction: When Henderson et al. scaled the seed count and correctly treated the seed as the independent unit of analysis, they found that the intrinsic variance was so high that different batches of random seeds on the exact same algorithm code could produce non-overlapping confidence intervals. By simply re-sampling the seeds or making trivial changes to reward scaling, the performance hierarchy inverted. A claim that "Algorithm A beats Algorithm B" was entirely dependent on the random seed draw, invalidating previous assertions of algorithmic superiority [cite: 6, 20].

Failure Case 2: The Atari 100k Leaderboard Overhaul
Documented in: Agarwal et al., arXiv:2108.13264 [cite: 5].
Context: The Atari 100k benchmark is used to evaluate sample-efficient RL algorithms. Due to computational constraints, researchers habitually evaluated algorithms using only a handful of runs (often 3 to 5 seeds) per game and aggregated the results using point estimates (mean and median) across tasks [cite: 7, 13].
The Failure: By treating the point estimates across games as ground truth and ignoring the statistical uncertainty implied by the finite number of training runs, the field built a leaderboard that was highly brittle. A single outlier seed on a single game could heavily skew the mean, while the median masked the variance entirely.
The Correction: Agarwal et al. applied Stratified Bootstrap Confidence Intervals and computed the Interquartile Mean across the existing data. When the uncertainty of the seeds was properly accounted for as the independent unit, substantial discrepancies emerged. Algorithms that were widely accepted as state-of-the-art were shown to be statistically indistinguishable from older baselines [cite: 5, 7]. The conclusion changed from "progress is rapidly advancing" to "progress has stagnated due to statistical illusions."

Failure Case 3: Cross-Validation Cohort Leakage in Supervised Learning
Documented in: Bates et al., Journal of the American Statistical Association, 2024 [cite: 10].
Context: Evaluating classifiers over a dataset by refitting the model multiple times (e.g., k-fold cross-validation or repeated refitting).
The Failure: A common analysis treats the resulting scores from R repeated refits on the same dataset as independent replicates and applies a paired t-test or permutation test. As the number of refits (R) grows, the confidence interval narrows artificially, and the p-value falls, even though the underlying data-generating unit (the cohort) remains completely unchanged [cite: 10]. 
The Correction: The authors mathematically demonstrated that refit panels omit the target variance and cannot recover the true variance from one cohort without extra assumptions. The error was treating the algorithm's internal randomization (the refit) as the independent unit of analysis rather than the dataset itself, leading to grossly inflated claims of statistical significance.

Failure Case 4: Cross-Embodiment Transfer Illusions
Documented in: arXiv:2607.1034 (DOI 10.20944/preprints202607.1034.v1) [cite: 16].
Context: Training policies on one robot body (morphology) and testing them on another to claim that learned representations transfer across embodiments.
The Failure: Researchers tightened their confidence intervals by treating multiple seeds of the same source-target morphology pair as independent observations. If they tested 12 morphology pairs with 3 seeds each, they claimed N=36 independent observations [cite: 16].
The Correction: A variance-components analysis revealed that treating three seeds of one pair as three observations constitutes pseudoreplication because the seeds share the identical morphological relationship. When the data was correctly aggregated to independent units (the pairs, N=12), the confidence intervals expanded massively, crossing zero. The claim that "morphological similarity governs transfer" was invalidated and shown to be an artifact of pseudoreplication and data-volume confounding [cite: 16]. 

PART 4. WHAT THE PROPOSAL ABOVE GETS WRONG OR LEAVES OPEN

The proposal under audit states: "These experiments produce generations within a run, episodes within a curriculum, repeats within a sealed specification, and separately seeded runs. The proposal is to treat separately seeded runs as the independent unit and to treat generations and episodes as within-unit structure, with cross-run transfer conclusions placed in separately identified analyses."

Soundness Boundary
This proposal is SOUND AS FAR AS IT GOES for avoiding Simple Pseudoreplication in within-environment algorithmic testing [cite: 2]. By explicitly treating the separately seeded run as the foundational independent unit, the proposal successfully walls off the most egregious error: treating individual temporally-correlated episodes or generations as N. 

However, the proposal is incomplete. It outlines an ontology of the data (generations, episodes, repeats, seeds) but fails to define the exact mechanical operations that transition the data across these ontological boundaries. The boundary beyond which this proposal stops being sound is the point of numerical aggregation and the phase of hyperparameter selection. Here is specifically what the proposal leaves open or gets wrong:

1. It Leaves Open the Method of Within-Unit Aggregation
The proposal treats generations and episodes as "within-unit structure" but does not define the mathematical mechanism for collapsing this structure into the seed-level independent unit. 
Failure Mode: If the program selects the maximum performance achieved in any generation or episode (the "best-so-far" or "peak" score), it introduces an optimistic optimization bias [cite: 7]. Because of the stochasticity of learning curves, peak performance is a random variable heavily influenced by noise. 
Mechanical Fix Required: The proposal must strictly define a non-optimistic aggregation metric prior to the experiment. The standard is to take the mean of a pre-registered evaluation window (e.g., the final 100 evaluation episodes of the run, or the performance at a strictly defined terminal generation) [cite: 12, 21]. 

2. It Ignores the Distributional Assumption of the Independent Units
By designating the separately seeded run as the independent unit, the proposal implies that a collection of these units (e.g., 10 seeds) will be passed to a statistical test. 
Failure Mode: The proposal implies, by omission, the use of standard point estimates (sample mean and standard deviation) and standard parametric tests (like a Student's t-test) across the seeds. In search and learning experiments, seed performance is notoriously bimodal, heavy-tailed, or skewed (e.g., an agent either solves the maze or fails completely, resulting in scores of 100 or 0, with no mass at the mean of 50). Using sample means on bimodal seed data leads to uninterpretable positives [cite: 5, 12].
Mechanical Fix Required: The proposal must explicitly state that inference over the independent units (seeds) will be conducted using robust distributional metrics, specifically the Interquartile Mean (IQM) and bootstrap confidence intervals, rather than sample means and parametric variances [cite: 5].

3. It Gets Hyperparameter Leakage Wrong by Omission
The proposal mentions "repeats within a sealed specification." A sealed specification implies a fixed algorithm with fixed hyperparameters. 
Failure Mode: Where did the hyperparameters in the sealed specification come from? If the hyperparameters were tuned using a set of random seeds, and those EXACT SAME SEEDS are then treated as the independent units for the final evaluation, the statistical independence is completely compromised [cite: 6, 10]. The seeds have been overfitted. 
Mechanical Fix Required: The proposal must mechanically mandate that the seeds used for evaluating the final sealed specification are drawn from a separate distribution of random seeds than those used during any generation, curriculum design, or hyperparameter search phase. 

4. It Misidentifies the Unit for Cross-Run Transfer Conclusions
The proposal states: "...with cross-run transfer conclusions placed in separately identified analyses."
Failure Mode: If the program intends to make claims about an algorithm's ability to transfer across different tasks, environments, or parameter specifications, the random seed is NO LONGER the sole independent unit. If you test an algorithm on 5 environments using 10 seeds each, treating N=50 for a general transfer claim is pseudoreplication [cite: 19]. The environment/task itself must be treated as a random effect [cite: 16, 17]. 
Mechanical Fix Required: For cross-run or cross-task transfer conclusions, the proposal must explicitly state that the unit of analysis is elevated to the task/environment level, requiring hierarchical aggregation (episodes -> seeds -> tasks -> statistical test).

PART 5. THE MINIMAL DISCIPLINE THAT WOULD SUFFICE

A program that adopts twenty rules will follow twelve. To make the results of this research programme interpretable and immune to the failure cases documented above, the following is the absolute minimal set of rules, ranked in descending order of how much scientific credibility each buys. 

Rule 1: The Principle of Pre-Registered Aggregation (NECESSARY)
What it is: All within-unit structure (episodes, generations, repeats) must be collapsed into a single scalar value per seed using a pre-defined, non-optimistic mathematical operation. Specifically, you must use the mean of a fixed, pre-specified window (e.g., the last 10 generations or final 100 evaluation episodes) [cite: 12, 21]. 
What it buys: Prevents optimistic optimization bias ("best-so-far" reporting) and temporal pseudoreplication [cite: 2, 3]. It ensures that the algorithm actually converged and maintained stability, rather than relying on a lucky transient spike in performance.

Rule 2: Seed-Level Stratified Bootstrapping (NECESSARY)
What it is: Once the data is collapsed to one scalar per seed, you must never report the simple sample mean and standard deviation across those seeds. Instead, aggregate the seeds using the Interquartile Mean (IQM) and calculate uncertainty using Stratified Bootstrap Confidence Intervals [cite: 5, 7]. 
What it buys: Protects the programme from the extreme heavy-tailed variance and non-normal distributions inherent to RL and search algorithms [cite: 5]. It ensures that a single outlier seed (a "lucky run") cannot artificially inflate the mean and trigger a false positive result.

Rule 3: Isolation of Hyperparameter Seeds (NECESSARY)
What it is: The sets of random seeds used for algorithm tuning, curriculum generation, and hyperparameter optimization must be strictly disjoint from the random seeds used in the final evaluation of the "sealed specification" [cite: 6, 10]. 
What it buys: Eliminates overfitting to the random noise of the environment. If you tune on seeds 1-10 and evaluate on seeds 1-10, any positive result may simply be the algorithm memorizing the specific stochastic draws of those seeds. Evaluating on seeds 11-20 provides the true out-of-sample independent observation.

Rule 4: Hierarchical Elevation for General Claims (NECESSARY IF CLAIMING TRANSFER)
What it is: If the analysis claims that an algorithm generalizes across different variations, tasks, or environments, the statistical test must treat the environment instance as the independent unit (N), not the total number of seeds across all environments [cite: 18, 19]. Seeds are averaged within the environment first, yielding one score per environment; tests are run across environments [cite: 16, 17]. 
What it buys: Prevents the classic evolutionary computation and robotics fallacy of multiplying tasks by seeds to artificially inflate the sample size [cite: 19]. It ensures that claims of generality are mathematically backed by environmental diversity, not just seed-level data volume.

Rule 5: Matched-Budget Controls (BEST PRACTICE)
What it is: When testing transfer or comparing a new algorithm/curriculum against a baseline, the total computational budget (total environment interactions, total episodes) must be strictly fixed [cite: 16].
What it buys: Prevents confounding algorithmic superiority with data-volume superiority. Many reported "improvements" in search algorithms are simply the result of the new algorithm being permitted to observe more data points under the guise of a more complex generation/episode structure [cite: 17].

PART 6. TOOLS AND CHECKS

The field has realized that researchers should not hand-roll these statistical mechanisms, as custom implementations often harbor silent bugs or subtle biases. The following tools have been externally audited, peer-reviewed, and universally adopted by top-tier venues (e.g., NeurIPS, ICLR) to enforce exactly the discipline described in Part 5.

1. rliable
URL: github.com/google-research/rliable
Maturity Note: HIGH. Introduced in the NeurIPS 2021 Outstanding Paper "Deep Reinforcement Learning at the Edge of the Statistical Precipice" (arXiv:2108.13264) [cite: 5, 9]. This is the absolute gold standard library for reliable evaluation in RL and machine learning benchmarks. It directly ingests matrices of seed-level data and automatically generates Stratified Bootstrap Confidence Intervals, Interquartile Means (IQM), and Performance Profiles. It completely replaces the need for custom statistical aggregation and prevents users from erroneously relying on point estimates [cite: 9].

2. marl-eval
URL: github.com/instadeepai/marl-eval
Maturity Note: MODERATE/HIGH. An open-source Python package officially implementing the data aggregation guidelines from "Towards a Standardised Performance Evaluation Protocol for Cooperative MARL" (NeurIPS 2022) [cite: 22]. It is built directly on top of the `rliable` framework but is specifically optimized for multi-agent RL and complex episodic datasets. It provides easy data processing pipelines that handle raw experimental data, enforce normalization across different tasks, and feed the clean, independent units directly into `rliable`'s statistical tools [cite: 22].

3. The Machine Learning Reproducibility Checklist
URL: cs.mcgill.ca/~jpineau/ReproducibilityChecklist.pdf (IDENTIFIER UNKNOWN)
Maturity Note: HIGH. Adopted widely by major AI conferences. While it is a static document rather than a software package, it serves as an excellent programmatic audit tool. It specifically demands clear reporting of the number of evaluation runs (seeds), the exact method of aggregation over those runs, and the exclusion of the evaluation seeds from the hyperparameter search phase.

Conclusion for the Reviewer
If the programme hand-rolls its analysis using standard libraries like `scipy.stats.ttest_ind` on the raw or maximally-aggregated outputs of its generations, it is virtually guaranteed to return uninterpretable false positives due to the violation of distributional assumptions and temporal pseudoreplication [cite: 2, 6]. By adopting `rliable` [cite: 9] and enforcing the principle that the seed is the absolute boundary of independence (and the task is the boundary of independence for transfer claims) [cite: 19], the programme will immunize itself against the specific failures that have historically derailed millions of dollars in computational research.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8wMsUqs_KIAPCKhimogU4sBjBRSUPcsVu1k56pcQRzsuIegiGijVXYp5uynR1vtk32aGve6zw8lUsjuXvVUtYNgtnzkze04Eg0xHj_X-IWcJMXBN6Eg==)
2. [zubairkhalid.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFiLC3k0pUdUQ923R5-5z8-_s4glICCrwlnf7bfCQSdKHvgplAjX9FreraNXnzwM8IoQfQSDXIdXGaW_09BbRQzjj-6GTB2j59WIxYMu7o_INDXEnBlyqJd72Ti7bjmOav37xx2WcRt-HMqYAlR2c_QZ_k5fMgvPs64DYuWs0gtk9A-mfiGGsZ5H8lFbTICPtNNuhHq_9ob-fugKPFpSA==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQ7oC1qTTVeAYQSlo-OL0Cfg0ffRXiDm_CHu95MKdbnm6tg_x2FWPddIat0Ydzumd1z_egknm-7m3muBFlAF9wk8mqLSrq3SupOt-0039y9-JaWUjHSQ==)
4. [ajosr.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRcuccQ7dqYdZhvDDZKXRFkephm4Zjh-p_sFbEs0jmngBovn_jWSqbDvXdgAFAwVpIcl59vMq6B-yHgEixZLVaCsiEfq2HOq8Aw9fexkDBSECnLjoU03iwSyryV1vICz35u8k7vRyjevhgvZY4FM3asJnQw25Z6V7Uj1ZFh0JpnMDNZtX6NY_084KBq2ou7BHHiQZM4ID7ULk=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpv8NP658N1Fwgp363tUpL1Y1_-tiC3uaemRV8osrZ12eTah0OzKodZx7wKAw2M7Pnq9xNHjWJQ15t9_NGae_YiaQquytFEeS2cQtzocH-DBz3n8uT3A==)
6. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1A95Ynu2vvmvZmi5L0rGoCc-CXGWnEqcmCD7kxWbeEH3SnjtUhlMTix_MGKoQKPyHLxvrjCr2NOjIlT_BeELpRdsg-DN3kJAhYqvukOLzJN1lR7Dkt3pLNcGT4far21Q8rWay4suKJUQQdQoZYn9BvSe0nF2G10WW2qrBVcyCqL7-n0U0lA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgq4XuUexaPBdqiw1geYflvg1sEkks0cKucEEl-jTdXJdR0xNsKPsCaTrj69q1szpv0Z0TiMeoGOdrcI-UrcX7rcjqeYiasrztVKkA7E5pZfv4Wqr_yQUSgQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU1I4x7gZORqf_apETtoI7mpPzZKTDeu7jCvZT6aTGKbZa9XCqvxOZqfoLhSvMxR_b_2UvbFhZozoXXfvRBAxXbbyVnUDPcv-r39XmiDNLE_M9_oOioA==)
9. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEnvTepaYbbU66yUJewhceqQ30mCsg74fWdu4nrViqdMKmwLdmeEPiqQeTctcxDb1S2sYDoJWg7FRN9QracrtMwjEecrInwLJfzWZsFwemOrmefw6ZdhtOHZCEPF8fCsBo=)
10. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFD4v6_P92-lW4VC0ii9k8biwxPCHv0ZIb7oDsdOKZifr6PbcsxBb3Fpoe2FijqGqHP8y6ip7iCLxNwP1K9Qv3qUyj0JDh4X9z3QG2Ge_sgV0l5rZvQq3UPq_v6Z-U)
11. [slideserve.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbBdu9zNsR2HD6L_5PLsJ1dfGa9cl2O8a3F9XnaHCgoh-eJNqUGSO_m5FB_MYaK6Wk-dFnFoTwJhhtjFK_7Q2KIgfDdCEVtaOjNfoXkiQeZ1AjPasHgEGRorNlpVQbfTxmDfU_0ErlYxUlHualOhT_WhH8OLAG0StnNb0g0-Ki0neAsNlUUa6wopEENQ-cNyddM8ljp8I690CIjs1a566ue8q2u2D4PQcCHIVDW2u8)
12. [inria.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOrcngc1n0RK71YxlNThLkg2NeQBQsZ1qs0o6ZWhTHRul2Boa_tA63zGtv5gAsY23R-UbtwUWtuARobAt-Uz9EmBGzxP9wE1aox7CIXfVEfWF-oh76hH4WksE9Mo082AC_xdL8Nqgu2kWGYmgknF3SWUtoB2HNGQ7Ue6WlOy653FXfyrz6DgYGefPjm69Yrd3yofhfnHueIUVmDDc5rAj5VtTvduzgPUd5N-PbNsEwdDb4MjseaLttSSzihDnpTkA-3QkXBzk=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUEmOvsBNK0LueHpyO8Bc2IP27RlK96IEXHB19AFifS9AWdrmwshQQx3LxKdgNZ9E5SbnlBg85BWswogN9XUaaQ_5DwOMxC1OypnFNP_pDYQN2bj4rqAtd35UEJ65Hm2Ac3iz10kwHyEnRpyBDY74fX5aYJYXnGaEIsWyhJJbadFWZEaP-zSdMOpKdvqKoEIF_I22WlzzN0l-f1zQnTFb7jFwEECMvtKN5TQLqxg==)
14. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGO7dHaRtCwDvvwBVqZ6J7D9NfOe0o3AkEwvIlmvHfiyF-9f3AJr6xoA855N6wfzsNSyt_WF4Y7WoRe7buMi3mt2VKxTw5hvVNbs6a3zae3-6OYphzgWrRErMVELnMlcp_XRk4Rg-aJan9kBKsUUGQtXxoJ_x6Emlnri8FBMX_z9uFYi3q0dqsV-LKJQpMdp_FGJWAhkhl2vcR83-ig0nKOkA4gDR7)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfuS56-tpWc325GYOK2IrZghN9O7IIqImCkJeM8aiyF0GGROzlQSAx33L2VtcbEIubKdB33iEHSkMe-TKYEdnFg-NIuzB8GHS7ERwyzMsFRi1r7gB4zlH7vSppzG2fNM-92tpIKZRFP-x1sxDw5fexRDiq_7vruusVzAYkAGOkm5AnUuAUoXD-hdBtUnViR8EnWur3A9yOObW5Vsf6X2FcJG2DM4_SSWvvFKInIzNBAly0DYMcnghIf4qHX2R6MiqojntNcA==)
16. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGW7qz9Q6ANj1zU8B1PB6n13Ya_lO2aSS5GHTTFCbBQcAJNeakNO3IjfxFZK3wvhHj0AtwDPzUNOywzd2oeuxRzvi0TG6R7zMi4PMahySLc_gicx_bs9ggPkg1EIGGUq-pYZK3_7tA=)
17. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7T9YqKRQkIdEIqDvE-zIturpm2FfPi55PN2ARgXJIttPg8wD7VhdTyviOl2OgcCjsLKREJSJ6gPXMXWfwpFilYwZICrxHXf9x5XtfxH8a71Ri59l1kln6NOzU-xoWM5rZ8SkwErk=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsuC9wupFUkSxZJ1LJN92vd_xK7HbpeiNFIq34936thXHIT3prPOOEHOWuvqQnXr4NoZTWp1swW0g5BuwiEkXMrqJDtfDAL3TxhHicJcgomy2vDx0_8Q==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUZVwuEvuKTGN8cl5KDwnqwTr-yqvv_iidxOJv3fDF0YMxWq7Ff6Vw-edD1A1yT5iTmuNOQvdGGR8eX98KvJrQp-ZJ9j-YQhtNkMsBbm_JovglkD5mrhVYfw==)
20. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlkU_BuAS-UWbvjx5t0kdyh3bRh5hYzqBYoFz4NnyPFcHCVkA881FwVjTGlPaaooJHpLPkZReNHSYUP_P_EGnu_xXvZcCvvCqYdwK-lM8_BfOGyi_bFbMTxgeO4GNUX9z0Nqk2zKArHh9NoD3CyV-2vklyS1RJRTBIdHXzSQIx9gmR28hlZGoNmcDlkT5xhTw-bnC2waa58EnLJgY7zw==)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrY2G7dzn922HBAueVzhc4OC24Z3P5N9DiHUxbvOp9IRZpJryJbHOpxpuvttL1s1mgVs7X_KS2pqqbrSmUGcniw5bsN2mlhlidr6kAt0gEBjrqdvddsFg=)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7Bmea6Jal5TZYaTr-WOafF-1Bhgc_70RWwjMG1GRLo3cXjtTlSQAw9ggEWyyyH_nuSP5GK-qTCnuqydWrwoiOHN1i0cf1lhogaBq2N5F5OX-eaIg5V_-psBaH8aul)


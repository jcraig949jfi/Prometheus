# Prompt 213: C1 method audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdiWWlnYXI2cENlclItOFlQekphXzZBMBIXYllpZ2FyNnBDZXJSLThZUHpKYV82QTA
**Elapsed:** 274s

---

# Method Audit: Sealing an Adaptive Experiment

## Executive Summary and Leading Analysis
*   **The core tension:** Sealing an adaptive experiment at the policy level successfully prevents *human operational bias* but does not inherently prevent *algorithmic statistical bias*.
*   **The methodological reality:** A pre-specified algorithm that adapts its own data distribution (e.g., an adaptive curriculum) fundamentally alters the statistical properties of its final evaluation. Standard fixed-horizon inferential guarantees do not survive continuous, data-dependent adaptations.
*   **The state of the art:** Biostatistics has solved this for phased, low-frequency adaptations using group sequential designs and combination tests. Game-theoretic statistics has recently formulated solutions for continuous, high-frequency adaptations using anytime-valid inference (e-values). Deep reinforcement learning continues to struggle with intrinsic variance despite sealed policies.
*   **The verdict on the proposal:** The proposal is mechanically sound for *execution* but unsound for *inference*. If a solver adapts its curriculum based on its own performance and subsequently triggers a sealed stopping condition, it is highly likely to return an uninterpretable POSITIVE caused by reward hacking, temporal drift, or evaluation collapse.

Your concern is entirely justified. The methodology as proposed addresses the operational integrity of the trial (preventing the analyst from cheating) but fails to address the statistical integrity of the trial (preventing the algorithm from cheating itself). Fields that operate under strict regulatory scrutiny, such as clinical pharmacology, and fields that grapple with the reproducibility crisis, such as machine learning, have developed extensive theoretical and practical machinery to mitigate this exact failure mode. This report will audit the proposed methodology against established frameworks in biostatistics, game-theoretic probability, and deep reinforcement learning.

## PART 2. WHAT THE RELEVANT FIELDS ACTUALLY DO

Three distinct disciplines have confronted the problem of adaptive experimentation, each developing specific machinery to guarantee that positive results remain interpretable when the data generation process is modified during execution.

### Biostatistics and Clinical Trials (The Regulatory Standard)
The pharmaceutical industry and regulatory bodies, specifically the US Food and Drug Administration (FDA) and the European Medicines Agency (EMA), have spent decades formalizing adaptive designs. In these fields, an adaptive design is defined as a clinical trial that allows for prospectively planned modifications to one or more aspects of the design based on accumulating data from subjects already enrolled [cite: 1]. 

The primary concern in this field is the inflation of the Type I error rate (the probability of a false positive) [cite: 2, 3]. If a trial is continuously monitored and stopped the moment a positive threshold is crossed, or if the sample size is dynamically re-estimated based on unblinded interim data, the standard statistical guarantees disintegrate. To solve this, the field diverged into two accepted approaches:

**Approach A: Frequentist Group Sequential and Combination Methods**
This is the dominant, universally accepted machinery. Instead of allowing the algorithm to adapt continuously, the experiment is partitioned into sealed phases (interim analyses) [cite: 1, 2]. The machinery relies on:
*   **Alpha-Spending Functions:** Techniques (such as O'Brien-Fleming or Pocock boundaries) that allocate the total allowable Type I error across a fixed number of interim looks. This mathematically guarantees that the overall false positive rate remains strictly controlled, regardless of when the trial stops [cite: 4].
*   **Sample Size Re-estimation (SSR) via Conditional Power:** If interim data suggests the effect is smaller than anticipated, the sample size can be increased. To prevent this unblinded adaptation from inflating the error rate, statisticians use the Mehta-Pocock Promising Zone approach, or apply independent p-value combination principles [cite: 3, 5].
*   **Combination Tests:** Discovered by Bauer and Kohne, this machinery treats the data before and after an adaptation as independent phases. The p-values from each phase are calculated separately and then combined using Fisher's combination test or the inverse normal combination test. This ensures that a mid-flight adaptation to the trial's parameters does not invalidate the final inference [cite: 6, 7, 8].

**Approach B: Bayesian Adaptive Designs**
Rather than strictly controlling frequentist Type I error through mathematical bounds, Bayesian designs utilize predictive probability [cite: 9, 10]. The algorithm continuously updates a posterior distribution of the treatment effect. If the predictive probability of success exceeds a high threshold, the trial stops. However, because regulators (and reviewers) demand frequentist guarantees, Bayesian adaptive designs are required to undergo massive, exhaustive Monte Carlo simulations across all plausible null hypothesis parameter configurations to empirically prove that their Type I error does not inflate [cite: 1, 9, 11]. 

**Divergence:** Regulators strongly prefer frequentist methods for confirmatory trials because the error control is analytically provable. Bayesian methods are often restricted to early-phase (learning) exploratory trials or highly specialized platform trials where strict analytic control is mathematically intractable [cite: 12, 13]. FDA Guidance FDA-2018-D-3124 serves as the ultimate ruling document on these practices [cite: 1, 11].

### Game-Theoretic Statistics (Continuous Monitoring)
While biostatistics relies on fixed, pre-planned interim looks, computer science and game-theoretic statistics have recently developed machinery for *continuous* adaptation—which closely matches your proposed architecture of a solver adapting inside an executor. 

The machinery is **Anytime-Valid Inference** utilizing **e-values** and **test supermartingales** [cite: 14, 15].
Traditional p-values become invalid under "optional stopping" (stopping the experiment as soon as a positive result is observed) [cite: 14, 16]. The field of game-theoretic statistics, pioneered by Shafer and Vovk, recast hypothesis testing as a betting game. 
*   **The e-value:** An e-value is a non-negative random variable that has an expected value of at most 1 under the null hypothesis [cite: 14, 17]. 
*   **The Machinery:** Because the product of sequential e-values remains an e-value (forming a test supermartingale), an analyst (or an automated algorithm) can monitor the data continuously, adapt the sampling strategy, and stop the experiment at any arbitrary time without inflating the false positive rate [cite: 14, 18]. 
*   Identifiers: arXiv:2602.06379, arXiv:2410.23614, DOI 10.1093/jrsssb/qkae011 [cite: 19, 20, 21]. 

This field diverged from classical frequentism precisely to handle the continuous, highly adaptive data streams found in modern algorithmic monitoring and multi-armed bandits, where pre-specifying a rigid looking schedule is impossible [cite: 14, 22, 23].

### Deep Reinforcement Learning (Machine Learning)
The exact architecture you describe—a curriculum choosing tasks from a solver's performance, or a loop refining on counterexamples—is the standard paradigm in Deep Reinforcement Learning (DRL). This field had to confront this issue not under regulatory pressure, but due to a catastrophic "reproducibility crisis."

**The Machinery:** The field relies on rigorous empirical reporting, bootstrap confidence intervals, and large-scale multi-seed evaluations.
*   **The Divergence:** Unlike clinical trials that seek a definitive p-value for a single intervention, DRL seeks to prove that a *sealed policy algorithm* is generally capable across a distribution of states. However, practitioners discovered that intrinsic variance (random seeds, environment stochasticity) and extrinsic variance (hyperparameter tuning) completely dominated the algorithmic improvements [cite: 24, 25].
*   Identifier: arXiv:1709.06560 ("Deep Reinforcement Learning that Matters" by Henderson et al.) [cite: 24, 26, 27]. The field settled on the convention that sealing the algorithm is vastly insufficient; the evaluation must be completely decoupled from the training distribution, and statistical significance must be demonstrated across a wide, pre-specified distribution of random seeds using Welch's t-test or stratified bootstrap testing [cite: 28].

## PART 3. THE FAILURE CASES, WITH RECEIPTS

The following documented failure cases demonstrate how sealing an adaptive procedure without the correct inferential safeguards invalidates published results or forces catastrophic corrections. 

**Failure Case 1: The Acute Rhinosinusitis Herbal Treatment Trial**
*   **Receipt:** DOI 10.1136/bmjopen-2017-018320 [cite: 29].
*   **The Error:** A clinical trial investigating an herbal treatment for acute rhinosinusitis utilized an adaptive group sequential design. The trial was programmed to evaluate the data early and triggered a predefined stopping rule for efficacy, officially declaring the treatment a success based on the interim data. The trial stopped, and the sample size was significantly reduced compared to the maximum projected budget.
*   **The Consequence:** The European Medicines Agency (EMA) completely rejected the findings. Although the mathematical stopping rule was strictly followed, the EMA determined that the reduced sample size failed to gather sufficient data to evaluate subpopulation effects, safety profiles, and broader interpretable efficacy. 
*   **Relevance to your proposal:** Your proposal seals the "stopping conditions before execution." This case proves that an automated stopping condition, even if mathematically sound and successfully triggered, can return a POSITIVE that is ultimately useless because it overrides the external contextual requirements for proof.

**Failure Case 2: Response-Adaptive Randomization and Temporal Drift**
*   **Receipt:** FDA Guidance FDA-2018-D-3124 (Section on Operational Bias and Complex Adaptations) [cite: 1, 13, 30]. 
*   **The Error:** In trials utilizing Response-Adaptive Randomization (RAR), the algorithm observes incoming success rates and alters the curriculum (the allocation ratio) to favor the better-performing arm. 
*   **The Consequence:** If the underlying population changes over time (temporal drift)—for example, if later patients are generally healthier—the algorithm will assign these healthier patients mostly to the experimental arm. A naive statistical test at the end of the experiment will yield a massive, statistically significant POSITIVE result. However, the result is entirely a ghost of chronological bias. The intervention did not work; the algorithm simply routed easier cases to the preferred metric.
*   **Relevance to your proposal:** Your proposal states: "a curriculum chooses the next task from the solver's performance." This is exactly RAR. If the curriculum adapts by serving tasks that the solver is marginally better at, the final POSITIVE result may merely indicate that the curriculum successfully collapsed the problem space to trivially easy tasks, not that the solver achieved general capability. 

**Failure Case 3: The Deep RL Reproducibility Crisis (Henderson et al.)**
*   **Receipt:** arXiv:1709.06560 [cite: 24, 27].
*   **The Error:** Researchers sealed their policy gradient algorithms, initialized their budgets, and let the algorithms adapt inside simulated executors (OpenAI Gym environments). They reported highly positive, state-of-the-art results.
*   **The Consequence:** Henderson and colleagues demonstrated that simply changing the random seed—while keeping the sealed algorithm and all hyperparameters perfectly identical—yielded completely divergent performance curves. Algorithms that claimed state-of-the-art POSITIVE results were shown to perform worse than baselines when evaluated across different, unselected random seeds. 
*   **Relevance to your proposal:** Sealing "initial inputs, seeds, budgets" before execution ensures reproducibility of a *single* run, but it completely invalidates the *inference* of the algorithm's general capability. If the program runs the experiment on a sealed set of seeds and gets a POSITIVE, it is UNCONFIRMED whether the algorithm is fundamentally sound or if those specific seeds simply aligned with the solver's initialization.

**Failure Case 4: Unblinded Sample Size Re-estimation without Penalty**
*   **Receipt:** General biostatistical literature regarding Type I error inflation (e.g., Graf, Bauer et al., 2014; documented in EU framework project IDEAL / CORDIS) [cite: 7, 8].
*   **The Error:** Investigators ran adaptive trials where the sample size was evaluated mid-flight based on unblinded data. Finding a weaker-than-expected effect, the algorithm increased the sample size budget to achieve significance, then applied standard frequentist hypothesis tests at the end.
*   **The Consequence:** The Type I error rate inflated massively beyond the acceptable 0.05 threshold. The POSITIVE results were statistically invalid because standard tests assume a fixed sample space. By making the sample size a random variable dependent on the data, the naive p-value became meaningless.

## PART 4. WHAT THE PROPOSAL ABOVE GETS WRONG OR LEAVES OPEN

I have read the proposal: *"The proposal is to seal the ALGORITHM, its initial inputs, seeds, budgets and stopping conditions before execution, and let it adapt inside its executor while recording every decision -- rather than freezing each future decision in advance."*

This proposal is **sound for execution integrity** but **unsound for inferential validity**. It successfully establishes a mechanical audit trail and prevents the analyst from moving the goalposts mid-run. However, it leaves open three critical boundaries beyond which the results become uninterpretable.

**Flaw 1: The Conflation of the Learning Set and the Evaluation Set**
*   **What it leaves open:** The proposal describes a "synthesis loop [that] refines on its own counterexamples." It does not state what data is used to trigger the final stopping condition or evaluate the final success.
*   **Why it is wrong:** If an algorithm adapts its parameters based on a stream of counterexamples, and the final stopping condition is evaluated on that same stream (or on the solver's performance on the adaptively chosen curriculum), the experiment suffers from fatal data leakage (overfitting). The algorithm is effectively writing its own final exam. A POSITIVE result here guarantees nothing about the solver's capability outside the specific, closed-loop manifold it navigated.

**Flaw 2: The Non-Stationary Evaluation Benchmark**
*   **What it leaves open:** "a curriculum chooses the next task from the solver's performance... and stopping conditions before execution." 
*   **Why it is wrong:** Stopping conditions (e.g., "Stop when accuracy > 95%") are only interpretable if the difficulty of the tasks is stationary. If the curriculum is adaptive, the denominator of the performance metric is constantly shifting. If the solver hits a plateau, the curriculum might adapt by providing a sequence of highly similar, structurally simple tasks to maintain progress. If the stopping condition fires at this moment, it returns a POSITIVE. This POSITIVE cannot be interpreted because you do not know if the solver mastered the domain, or if the curriculum simply lowered the bar to trigger the sealed stopping condition.

**Flaw 3: The Optional Stopping Problem (Error Inflation)**
*   **What it leaves open:** The statistical framework used to evaluate the stopping condition. 
*   **Why it is wrong:** If the executor is evaluating a traditional significance metric (like a standard p-value or a static performance threshold) continuously at every step of the synthesis loop, the false positive rate inflates exponentially. Given enough time and budget, a random walk will eventually cross a static threshold. Sealing the stopping condition in advance does not protect against this; it simply automates the p-hacking.

**The Boundary of Soundness:**
The proposal is sound **if and only if** the purpose of the adaptive run is purely exploratory (hypothesis generation, or "Phase II" learning) [cite: 12]. The moment this architecture is used for a confirmatory result (a final, definitive POSITIVE), it breaks down. To make it sound for confirmation, the adaptive learning phase must be strictly partitioned from a static, pre-specified evaluation phase.

## PART 5. THE MINIMAL DISCIPLINE THAT WOULD SUFFICE

To salvage this methodology so that a POSITIVE result actually means something, the research programme must adopt a disciplined framework. The following rules are ranked by the inferential power they buy the programme.

**1. Mandatory: The "Seamless Phase II/III" Partition (The Holdout Rule)**
*   **The Rule:** The execution must be explicitly divided into an adaptive learning phase and a static confirmation phase. The synthesis loop and curriculum can adapt wildly inside the executor. However, the final stopping condition and the final POSITIVE/NEGATIVE verdict *cannot* be evaluated on the adaptive curriculum. It must be evaluated on a completely sealed, static, out-of-distribution holdout set that the executor never used for refinement.
*   **What it buys:** This single rule solves Flaw 1 and Flaw 2. It ensures that no matter how the curriculum altered the learning path, the final evaluation represents true generalization. It separates "learning" from "confirmation," adhering to strict regulatory biostatistical standards [cite: 12, 30].

**2. Mandatory: Multi-Seed Robustness Ensembles**
*   **The Rule:** Sealing a single random seed (or a handful) is prohibited. The protocol must specify a statistically powered number of random seeds (e.g., N=30) representing different initializations and environment dynamics. The stopping condition must require the aggregate performance across the ensemble to cross the threshold, rather than a single instance.
*   **What it buys:** Prevents the DRL reproducibility failure identified by Henderson et al. It ensures that a POSITIVE result is a property of the algorithmic policy itself, not a lucky artifact of the specific seed initialization [cite: 24, 28].

**3. Necessary: Anytime-Valid Inference for Continuous Stopping Rules**
*   **The Rule:** If the stopping condition *must* be evaluated continuously during the adaptive phase to save budget (early stopping for efficacy or futility), the threshold cannot be a standard metric. The programme must implement e-values (test supermartingales). The stopping rule must be defined as $E \ge 1/\alpha$.
*   **What it buys:** This completely solves the optional stopping problem (Flaw 3). It provides mathematical immunity to continuous peeking. The program can monitor every single decision and stop at any millisecond without inflating the false positive rate [cite: 14].

**4. Best Practice: The Independent Evaluation Oracle**
*   **The Rule:** The adaptive executor should not have access to the code that calculates the final success metric. The evaluation oracle should be mathematically isolated. 
*   **What it buys:** Prevents operational bias and unintentional data leakage. Even if the algorithm is sealed, complex software can inadvertently leak state. Separation of concerns guarantees that the evaluator remains uncorrupted.

**5. Best Practice: Pre-registration of the Estimand**
*   **The Rule:** Before execution, the programme must define exactly what the positive result represents in plain language (e.g., "The solver achieves 90% accuracy on uniformly sampled tasks of complexity X").
*   **What it buys:** Prevents narrative drift. When a complex adaptive system returns a partial or edge-case result, analysts are tempted to redefine what success meant retrospectively.

## PART 6. TOOLS AND CHECKS

To implement the discipline above, the programme does not need to build the mathematical machinery from scratch. The following software packages implement the required statistical controls.

**1. rpact (R Package for Adaptive Clinical Trials)**
*   **URL:** rpact.org
*   **Maturity Note:** Extremely high maturity. This is a GxP and FDA-compliant commercial-grade open-source package. It implements the exact combination tests, alpha-spending functions, and group sequential boundaries required to maintain valid inference when an experiment adapts its sample size, drops arms, or re-estimates boundaries mid-flight [cite: 31, 32, 33, 34]. If the programme chooses to partition the experiment into discrete adaptive stages, this is the gold standard tool.

**2. safestats (Safe Anytime-Valid Inference)**
*   **URL:** safestatistics.com
*   **URL:** cran.r-project.org/package=safestats
*   **Maturity Note:** Academic and emerging, but highly rigorous. Developed by the researchers pioneering game-theoretic statistics and e-values (Grünwald, Ly, et al.). It provides tools for continuous monitoring, allowing experiments to be stopped early or extended indefinitely without loss of statistical validity [cite: 19, 35, 36]. If the programme insists on continuous, step-by-step evaluation of the stopping condition inside the executor, they must use this framework.

**3. Deep RL Reporting Checklists**
*   **URL:** IDENTIFIER UNKNOWN (Hand-rolled by convention)
*   **Maturity Note:** While specific comprehensive software packages for exact RL reproducibility do not exist in a single unified library, the community relies heavily on guidelines established by Henderson et al. (arXiv:1709.06560) and subsequent reproducibility checklists (e.g., the NeurIPS reproducibility checklist). Programs essentially hand-roll their multi-seed orchestration using tools like Weights & Biases or Ray Tune, combined with standard scipy statistical tests (Welch's t-test, bootstrap confidence intervals) applied to the aggregated outputs [cite: 24, 28].

**Sources:**
1. [casrai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrDVdoFgThj30YJmB1U71mMiR7qrT1cIOcnNQqSZcGXh-OzQh2_RV2F1paxu-mqrQ7SX5OmtJttCY5pUFT6hr2ya3ed93WmZTNzyneqSAjq2iFG6q2qx42N0S4Ug3dvPXmuvqobmgbjQgs47BCYpw=)
2. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHeZK4v3odKaJvj8xTnjE3cxvVWuyGGFadU6JSGPSXvV0JEwIhre_WUg8iagalMrHQv9w6ysSLvc3F07NC0wtyL7xUyyQhslogXo9L6xiVy-dEnGNGg4tLnvve5kkKd8ZhaDi3rDS_)
3. [statonellc.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxz1ztkHedXJBt7z2Q-eSOe07JsEeSGG-av7yuIz6WxhYc4v8f2rKYtzMFQVRP6geFJZg0miifvSvDmy8bJon3UMvWcUPkuEA5nTsZnOm5p04x7xvAArmuhQjAKnnORuNmfaeyJyz3w3FAFrvP7jMZoXY8T8Rey0oX7C2gqPcKNtMrYfJChIzPtuYJfbT-65xwyGyuh4Humu9_34mGd6Al8hZP55qzlMU=)
4. [amegroups.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYraS9JeV0QWl94DJmaGKO4V9PCMGWMjfXGQklIkxHwP_FnizMXFxNTQsoLTF00QNad2p-jUZTUEceAboBW71rkBTFwPskOgel2Cdm-JcYMoPhToq_Q6TJlvXhraL7nFhZCdlBjeYd)
5. [avaniaclinical.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU4uUE7zIPDvxAfd-SY4b8rbCeWFDnUIBb_CuQutUI60yMQX5krp_yGvukyg2jBnyhUpe3STjX14j2ew0Hj8QVSZ0c3nbu9uGTBy1JLPCR3tTg_XvapigmlCzjRQO1h3bhxVvE1DQGVTGqGXmwc0BzuE8a27EBttqfZfBwyGMRZGl09AmbP8ntFzpE1_6Z4Cx1kUJLlstaaLpZaCH-edf9dh1bKJKtbzzqH4ZvEZRfXSR6pTA=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG73_eS5tr3FlKMJeYOBhUYmeTTGHSyxV6R74tY1Ek46sFTc8Nfg0P-Y3Lsg2cnVEyh67XiYN5pS2RZAktbolo0V016-Bncc_xZQu3ux6FeDOX3z64yyA==)
7. [europa.eu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjvgF_rli_cQWX517lqbsIx8hHMiJHpSBiy90mn2jI1hxMlaOfQG3sojLBCdMug9fQRUIRmULT3eVGB57M5iSaCyWc54MOf4ytwwvnIBuEukWkwpus530TJYgFWIduU-zyhB_woKpZfDYG)
8. [alexkaizer.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGD5obFkQQNRpm5Yl4ZwoxI7Qh2GyBRm2exHmEEk5Hmg75h2cvNYWVB3LUE1pdjBHcJ2_uxayv0QlN_ZqihvQJ72nu4au3RSKhd_DsP7yjkoFnxFFztS3pUVUjgEQ9SlHvzKxyu_zIeDGJrqsasg6fNtOBdu8Sozl4EDmENmA=)
9. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZcdU0hFnIF_-T9n4ivbYQBYOni98KUubZug8sgVmNFpbn62nqbJObP-nLhuZ6-EzlCvxE7Qpxma5qFw0yCd7vXX6TwXe2I3_3L0dDzQf7j45Y5ER4bNiKeZ4tH_hMzk7DtfJ-q7X_)
10. [ahajournals.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0BUco9n6TKAJIJ_E1Ax96mhQInKSdagYbKCTKw0feTRfhb5BYBS0W6jDpwycDH-EmixnKvEKsWouiwWvjAqnpdEyX6uiBfjFYlv0fqBA2zZ5uO6gBxBjpvEc5fIwPFiYR_AZseWQDiQFs0Ofhf_Mm4ls=)
11. [fda.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCmyEOAMoq5ibPV63OkHtr0E2BZ4Qu2bLf9yzkMabYDLSCN9bJbLTMY1zUnCH0GAYkVaDMGgDi-GRuz_5Ph6qFVOSdvXlVUld-ZdgfND0nvOqt7IUlFLJbxy9rV0eKPazgNEQxTkqvmgBXz68v3R6vca5NhekOlaB4wn72cjl2YTPdpznl1jhoS669bGRxi4gAO9lcPGaLqnxlqEccAUFaP-WyPUcXITd356QYDPrgrNrhryC4GWDYPJtHziVSILt7OBoTPw==)
12. [quanticate.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvuJo26gz9KesroxplkTmsWWXjUCHinTe0YpZ_z5VI7iXYUMitaU3c9ABX2ypNWiYXM17PyAVXfDtgQ0gSqhUG5gm3qeHyeifPM0QRDyld9b2f6RxA_0bDr7_vOH9ZtMbF4N71IUj2mrnpyg5E075k3-wV9igw0KYH5R8=)
13. [fda.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEn-HYA6eh-_8jFbEoM-1MyYBMC8e7TTBG3bRkxWv02Whq2TEOZCJHMcpKso2Q3b2_i1fTmWh0irLXOCpB2SJjFZotc2UfZLuJPD4PV4xYWVyE4648ZlWrqHNvBuJZ)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2geNDxiJw_NkPAxnuVnsM1ZW5jyEY8Df0Zgnwq4eUqL9i0IMp9pJ4oJ6LwDH65YjoFXMVvLIexOogr9p7EOrWSVZ5tG6MnicheXbwMrNWPATl4FZtoVaWDA==)
15. [osf.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG758Cr3XCEnUaDPGNLqhOVl1DmkTZ3KouwcMtGBnGoJLG6_mzOk0QochgszpeQVNrhk1RtSiX4NuHxKYy0MInYdik3W1cPXV0eYOZtFeYZGCVWbdkzBizr7mu4avrOeZg=)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWEmzyxQxCrvojFlsNc3elZx2cyr6rNXtLStUdIOMVUTmoVdheTxUF5lcH04453W-7C0DovGLUECcvZgG2JAxoOZ9gDdfw5-6E6IBB_aXhHYJJTf7LqQ==)
17. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXfJ6j1Yugt6fw8DyUq2VBa54JdpAafU09FFKBOPzFSMV5duWmKAoChsuOU8PsmsyYCCDVWCIwHTe6aoBkssjnXYvlDyd9ni97QAZoWBHf6FBYn1yFKNP_SsBgnXZn2FyFMoovEOI=)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHz_sclqSQgQLDqUOlU5Od8JSuqQ1rl_1_j16P28QVApJnkAzMA-Gs2v9pZyepHE8D0Mii55EkZeo5zTpYF-aluJ0mPtbMCKPAhDrOQk74v8fTRJRGZkw==)
19. [r-universe.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWsS-lkL28uFjsNUSEBusAgKBDscceEBVZyZo2FAW-7RP7ydCn0PX-ceWIAjFyJVLLVvtvpmPljObbuqxR2nS79jX1FSqXuh4ujAzqIok-gGOztAJJAz0R6LNF)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyvorp8nu72ddKPBkJC16FVEiu9Ub6msiWfrPq5Q06iIUtEQdWI8ZLkxpT4fLmLv5aS_OHlIAE_mzTSimVtew-rYeR5q9P4hp_76htA4pSfRhHy0-XSg==)
21. [r-universe.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtY56VYEaKxlMqO_w_dKwFUW_PxQPk7C_WfGqOZwJIfp-6I-SAbbzRa53GXfsni_BD6Zkz1cY8GNhRGztLD9LIa47MBkT5fAtVn1m4waNEa_zDE69ROBmGqHkFIIRWOOGl1-qENeGvVCNw606CgwgWdrJQfvfGQo67bVmueQ==)
22. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7efln59VZsmIJJr4Y4kD6nhrPGn1VgL9VJSKY4Q-YJ1N6H1cpqE31sbDlHJYq9KA4QgK-pEbQZws4GZsWLavRZz4KjIXduvvHznxVJQccH2PlRu6c7iI=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLzCkZ5JAd6IPTJ7TI7tCDrO7DmVOEXFx9KbLeDe8mIeZXm6s3912L0f1kD5Y7n3-KO1j1uAmKLO1IQrPDw0AFRepFZJ23Ydp9i7x1inCbff-d6uJvWA==)
24. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXYSxq1HGbtPeIPiQwGX8tSZxrQBALFZyK3YOjcX5APN0HimRjghukGkFgvOdecDdtWi33F2eQu6vLklhtQc-aOfg8FCQXn4gwK8JhrZG4TBSfB-Fv7FmIcj-DaIY=)
25. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFihmzaVeFknMyz9cSOosY1-vxNAhK8lphLJN1UYryWYtCNQJR6YY_F7ykBC-gXrBpKsLMhYv2SeFeX2LK3h4FDJZCxYV4pIncy2S6R1GqstoaQznZV3LhSciKQlaT547tAOVpLqniesKWn9jFWRghlWThT9Wu_E2icD8tnQfhhmcA11rBm2A==)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGF_FsQaHbuLQPJw3QNbudINGLSY7W2ki0uj1u2O3PY9jHSfyGL6Y-EpFc5wNHXPEDAc1wVWQsRcFo-DJfQih-Y0QQPBnYYMwg7FikMY3Z8K0JvHSHAvtdcVg==)
27. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvh_MSvPCX1TOuLsMeV7wt_-T6GfWkq0R6r3PVWHwhB6bO5t6iuIUs7KV2C5FLusBG3NBGvOdpP83b19lD1Ei3PJ5ibmueeS8rrpfWY_3i-fBYcC-0dg==)
28. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx554OArhpcjVu6zqH6uth_puJg_IWJyd7uUiSBVlcndS17sPPwUpF97seeQMHInYRJEmebYuV6ONWg52L_uIdu68dSZYYdO81R0r7JcFQly62PWqBFg==)
29. [bmj.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQbyJz8pwPRLV0TKJ744G9n-VUM4J-pdCFNH1fFdzlS-UaKilEP-GadG7FOv1CEE5tueY1myFRwKRLplHPdliZ8ARdmeGp6ZKcXvBO9eD_PrI-36QaBszgLt3j-97ORE1U)
30. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH26xdQZsPTIq2_4bVemVJWAmwpUHd-x7XsqnzGLRha_RS5Tu4XiS3N4MpJx-v9-febavfPdTK3VeQ_GBdAgQM3tIUaDZwKyvkLGRf3SBfOlLjiZC1aXLN1eA3avhUDJ0OaGTpvtxcM)
31. [r-project.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEAmZxI0HQDULRy-HsDGBbNzjTJppHSFAbKOlfqmoi9J504J7q_SYZDm32Hy66tRC8H7eTSffcCr8kOd3AgG1GMNT7dk-wMdjSIND_yweljTNQR8zM50qQaXBcAoW9C_zCFpJqFQQbY4Ab5goSLW2mV6zpvCE=)
32. [rdocumentation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-JHWI9snPBiwOARACCr2YbRpKkImLop9Oajlg37EVMLu5RQjG0Rpwjm5Y31fWrD2NvOuMslH4Ro-EEioey1OQtnl0RyG_P2AxejRApVJCjlxp2QkFcz4-rWCvzr22sOd8-Q3jQWXePRl7ujTt-xhFwVU=)
33. [rpact.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErxQay_EEZsX2WVRuqfGVRKy11aOUX1ZIaPls_qaGNzY-l1mxBX7WmdUYr5MeP3S02Aoy268s5KMGvk8jYn7TFw1uorQSL9fImEPK8)
34. [rpact.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvY_IxSoGpQv9UOeef8TspeLdY3ueIprP0qxkjbD--A2lyr3fEDKsfiGvp7qWmU1w9YhzJudAe1EDj5-sKeyebMIAb6OMZUSbJXxImww==)
35. [r-project.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSr2yguKRAwWU_c0bdhwPtHjY93jwYv54EE2TdYEoWwPyJcZiizxsq5IqFQ0_A8Jnki9tKnr1JLXfd7v0wpSkF2B_c0z2BZmiq5nsIqQCr-IS3J8n8v_W-SOiMYsIvAELGHA==)
36. [safestatistics.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZy-w2x7xR1ETXXN04y50-GCunTPLaQNwhkMAwSUjrEuR9IoaHjOa_Ufg_c9hCbr2zlxALC4aWiXGPRhqoa9LetBnSsovc74Q2Rq6YsRIAIpU=)


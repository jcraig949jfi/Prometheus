# Predictive Modeling of Reasoner Error Distributions: Bridging Machine Theory of Mind, Psychometrics, and Algorithm Selection

### Key Points
*   **The flagged hypothesis is confirmed:** Current machine Theory of Mind (ToM) benchmarks heavily index on belief attribution (predicting *that* an agent holds a false belief) but do not systematically measure failure-mode prediction (predicting the specific distribution of *how* an agent will fail). 
*   **Psychometrics offers the most mature instruments:** Item Response Theory (IRT), specifically applied to **distractor prediction**, provides the primary mathematical and empirical framework for predicting the exact error distributions of human or model populations. 
*   **A viable promotion gate exists:** Recent 2026 benchmarking in educational AI demonstrates LLMs predicting specific human distractor choices at 47.9% accuracy against a 35.8% base-rate predictor, satisfying the deterministic scoring rule requirement.
*   **Algorithm selection literature misses the target:** Traditional solver portfolios predict *that* an algorithm will fail (runtime/timeout) rather than *how* it will fail, though emerging concepts like "structured lossiness" in heuristic algorithms provide a conceptual bridge to modeling deterministic algorithmic biases.
*   **Cognitive science provides generative error models:** Work on continuous estimation tasks has successfully predicted non-Gaussian human error distributions in complex tasks (e.g., 360-alternative forced choice) based on neural representation geometry extracted from binary (2-AFC) tests.

### Executive Summary
This report addresses the problem of identifying whether primary research across machine learning, cognitive science, and psychometrics supplies a measurable framework for a "Tier H1" system—a system that models its own and other reasoners' failure distributions to allocate search accordingly. The central distinction governing this analysis is the difference between predicting *that* a solver fails (a binary probability of error or timeout) and predicting *how* it fails (the specific structural distribution of its errors). 

An analysis of the state-of-the-art literature confirms that machine Theory of Mind (ToM) largely ignores the structural prediction of failure modes. Instead, the requisite instruments are found in two distinct domains: (1) Psychometrics and Item Response Theory (IRT), where the modeling of distractor plausibility provides a deterministic scoring rule that beats base-rate predictors; and (2) Cognitive Science, where geometric models of neural representations successfully forecast high-dimensional human error distributions. Furthermore, while traditional algorithm selection focuses on performance metrics rather than error topologies, the study of "structured lossiness" in deterministic tools (such as decompilers) offers a nascent framework for predicting the correlated failure modes of artificial reasoners.

---

## 1. Introduction: The Tier H1 Reasoner and the "How vs. That" Paradigm

The development of advanced artificial intelligence requires systems capable of introspective and extrospective reasoning. A hypothesized "Tier H1" system is defined by its capacity to model its own failure distribution alongside the failure distributions of other reasoners, utilizing this meta-cognitive awareness to allocate computational search optimally. 

To operationalize and validate such a system, we require a measurable promotion gate: a deterministic scoring rule that demonstrably beats a base-rate predictor. A critical attack vector in defining this gate is differentiating between two fundamentally distinct predictive capabilities:
1.  **Predicting *THAT* a solver fails:** Estimating the overall difficulty of a task or the probability that a reasoner will produce an incorrect output, crash, or exceed a time limit.
2.  **Predicting *HOW* a solver fails:** Forecasting the specific probability distribution over the space of possible incorrect outputs (the failure mode or error topology). 

The user's central hypothesis—that false-belief paradigms and machine Theory of Mind (ToM) benchmarks measure belief attribution but *not* failure-mode prediction—warrants rigorous investigation. This report synthesizes findings across machine ToM, psychometrics, algorithm portfolio selection, and cognitive science to locate primary work on predicting another system's or human's error distribution, scored against actual empirical errors.

## 2. Machine Theory of Mind: Belief Attribution vs. Error Prediction

Machine Theory of Mind (ToM) refers to the capacity of artificial systems to attribute and reason about mental states—such as beliefs, desires, intentions, and emotions—in themselves and others [cite: 1, 2]. The foundational question is whether current machine ToM frameworks supply a measurable version of failure-mode prediction. 

### 2.1 The Limitations of Current ToM Benchmarks
The majority of foundational ToM benchmarks are derived from developmental psychology's false-belief paradigms, such as the Sally-Anne and Smarties tests [cite: 3]. These paradigms probe whether an observer understands that another agent holds a belief that diverges from reality. In formal terms, first-order ToM probes whether an agent $A$ holds a belief state $B_A(p)$ about a proposition $p$, while higher-order ToM queries embed these recursively [cite: 3].

Recent advancements have seen the creation of large-scale benchmarks to test LLMs. For instance, BigToM utilizes a novel framework for procedurally generating evaluations with LLMs by populating causal templates, creating 5,000 model-written evaluations linking percepts, beliefs, desires, and actions [cite: 1, 4, 5]. Other benchmarks, such as SOMI-TOM, attempt to evaluate ToM in embodied, multi-agent complex social interactions within environments like Minecraft [cite: 6, 7]. 

Despite these advancements in complexity and modality, the literature confirms the user's flagged finding: **Machine ToM benchmarks measure belief attribution but NOT failure-mode prediction.** 

### 2.2 Why ToM Fails the "How" Test
Current ToM evaluations primarily assess binary or categorical outcomes. They ask: *Does the model know that Sally will look in the basket instead of the box?* [cite: 3]. The evaluation metrics rely on percept, belief, and intention accuracy [cite: 3], which measure *that* an agent is operating under a false belief and predicting the single deterministic action that follows from that specific false belief. 

These benchmarks do not evaluate a statistical distribution of errors over a complex task set. They do not ask: *Given that a system does not know the location of the object, what is the probability distribution of its search behavior across a hundred possible locations?* Consequently, while machine ToM provides the conceptual architecture for modeling another agent's latent state (a prerequisite for a Tier H1 system), it currently lacks the psychometric rigor and the probabilistic measurement instruments required to predict a continuous or multi-class error distribution. 

## 3. Psychometrics and Item Response Theory: The Real Instrument

If machine ToM is theoretically aligned but methodologically lacking, psychometrics—specifically Item Response Theory (IRT)—is where the real instrument lives. IRT is the most widely adopted statistical framework for modeling examinee abilities and item characteristics on a shared latent scale [cite: 8].

### 3.1 IRT and the "That" Paradigm: Difficulty and Discrimination
Standard IRT models the probability of a correct response as a function of student ability ($\theta$) and item characteristics [cite: 9]. In the Two-Parameter Logistic (2PL) model, each item is characterized by:
*   **Difficulty ($b$):** The ability level required for a student to have a 50% probability of success [cite: 9, 10].
*   **Discrimination ($a$):** How effectively the item separates high-ability from low-ability students [cite: 9, 10, 11].

While predicting item difficulty aligns with predicting *that* a solver fails, the prediction of discrimination is slightly closer to structural modeling. Recent evaluations of Large Language Models (LLMs) reveal that while LLMs can predict item difficulty reasonably well (often achieving up to 80.0% accuracy when comparing substantially different problems), they completely fail to understand item discrimination [cite: 10]. Direct prediction of discrimination yields weak alignment with human-calibrated discrimination, reaching a Spearman correlation of only 0.152 [cite: 12]. LLMs fail to identify items that are psychometrically "noisy" and cannot reliably capture how assessment items distinguish human students [cite: 12].

### 3.2 Distractor Prediction: Solving the "How" Paradigm
The exact solution to the problem statement—predicting another human's error distribution on a task set, scored against actual errors—is found in the sub-field of **distractor prediction and analysis** [cite: 9, 13].

Distractors are the incorrect response options in multiple-choice questions. They are not random; they are carefully constructed to capture specific, systematic human misconceptions [cite: 13]. Therefore, predicting which distractor a student will choose is mathematically equivalent to predicting *how* they will fail. 

A 2026 study by the authors of the FoundationalASSIST dataset provides a direct, measurable promotion gate for this capability. The researchers tested whether LLMs could predict the specific wrong answers students chose most often. The findings are highly illuminating:
*   Models achieved **47.9% accuracy** at identifying which wrong answer students chose most often [cite: 9].
*   This performance exceeded the **random base-rate baseline of 35.8%** [cite: 9].
*   However, models fell 15 percentage points below chance when predicting which errors students *rarely* selected [cite: 9].

This dynamic perfectly addresses the `PATTERN_BASE_RATE_NEGLECT` cross-reference. A naive predictor that only learns the overall global difficulty or the base-rate popularity of an error might beat a completely random guess, but a true Tier H1 reasoner must predict the conditional error distribution based on the specific latent traits of the solver. The empirical data shows that LLMs have learned to recognize some common misconceptions but cannot yet finely distinguish likely from unlikely distractors for specific ability levels [cite: 9].

### 3.3 Generative Error Modeling via LLMs
Further work in this domain shifts the focus from predicting to *generating* failure modes. Zu et al. (2023) utilized a prompt-based learning framework conditioning GPT-2 to generate distractors based on the item stem and the keyed correct answer [cite: 13]. By generating false statements as controlled semantic distortions, they created error distributions that achieved human acceptance rates exceeding 80% [cite: 13]. 

By decomposing item difficulty into LLM-based plausibility estimates over response options, researchers can express failure probability as a ratio between the plausibility of specific distractors and the correct option [cite: 11]. This is the very essence of predicting a failure distribution: assigning a continuous probability mass across the space of possible incorrect answers.

## 4. Algorithm Selection and Solver Portfolios: Missing the Target

The user's query correctly identifies solver portfolio selection and algorithm selection as related areas. However, an analysis of the primary literature reveals that this field fundamentally suffers from the "THAT vs. HOW" confound.

### 4.1 Empirical Hardness Models and Performance Prediction
Algorithm selection relies on the observation that algorithms often exhibit complementary performance; where one fails, another shines [cite: 14]. The standard approach, epitomized by systems like SATzilla, involves building an **empirical hardness model** [cite: 15]. Using machine learning techniques, researchers extract features from a problem instance to predict an algorithm's runtime or probability of success [cite: 15].

The framework operates as follows:
1. Construct an empirical hardness model for each algorithm in a portfolio, predicting its runtime based on instance features [cite: 16].
2. Choose the algorithm predicted to be the fastest [cite: 15].
3. If a solver fails to complete its run (e.g., crashes or times out), run the algorithm predicted to be next best [cite: 15, 16].

This literature is exclusively concerned with performance space $Y$ (e.g., competitive ratio, running time, success/timeout) [cite: 17, 18]. It predicts *that* an algorithm will fail to solve a problem within a given timeframe. It does not predict the structure of the incorrect output. Therefore, standard algorithm selection does not provide the measurable instrument required for a Tier H1 system focused on failure-mode distribution.

### 4.2 The Exception: "Structured Lossiness" in Decompilation
While standard algorithm selection fails the "how" test, a conceptual breakthrough is found in the study of deterministic heuristic tools, specifically in binary decompilers. 

Decompilers are lossy heuristic tools that attempt to approximate original source code from binaries. Recent research notes that different decompilers exhibit specific, predictable failure signatures—not random noise, but a deterministic bias given the same binary input [cite: 19]. This phenomenon is termed **"structured lossiness"** [cite: 19, 20]. 

When predictive models (like malware classifiers) are trained on the output of these tools, the models do not just learn to identify malware; they learn the specific way a decompiler fails to represent certain code patterns [cite: 19]. Because decompilers share underlying assumptions (e.g., about stack frame layouts), their errors are often highly correlated [cite: 19]. If an ensemble of models votes on an outcome, the vote does not resolve uncertainty; it merely averages across correlated approximation errors [cite: 19]. 

The true metric of analysis, researchers argue, is the structural delta between two representations—the precise topology of their disagreement [cite: 19]. This maps perfectly to the requirement of modeling another reasoner's failure distribution. To predict how an LLM or an algorithm will fail, one must model its "structured lossiness"—the deterministic algorithmic biases and correlated failure points inherent to its specific architecture.

## 5. Cognitive Science: Predicting Human Error Distributions

While psychometrics handles discrete failure modes (multiple-choice distractors), cognitive science provides primary work on predicting continuous error distributions.

### 5.1 Continuous Estimation and Circular Variables
A highly relevant 2025 study in *PNAS* focused on modeling continuous estimation tasks for circular variables (e.g., color wheels), which are widely used in cognitive science and neuroscience [cite: 21]. 

The conventional wisdom in cognitive modeling assumed that ideal observer models would yield Gaussian error distributions under Gaussian measurement noise. However, this research demonstrated that the geometry of the neural representation is the primary factor determining the shape of the error distribution, resulting in non-Gaussian error patterns [cite: 21].

Crucially for the user's problem statement, the researchers successfully predicted the complex error distribution of an $n$-Alternative Forced Choice (n-AFC) task using data from a simpler 2-AFC measurement [cite: 21]. By evaluating the 2-AFC $d$-prime and mapping it onto a noise parameter, the researchers generated a "zero free-parameter prediction of the error distribution for the 360-AFC task" [cite: 21]. The predicted error distribution effectively captured the overall shape and structural topology of the actual human errors [cite: 21].

This represents a mathematically rigorous, primary piece of literature where the *exact error distribution* of a human system on a task set is predicted and scored against actual continuous errors. It proves that failure distributions can be mapped and predicted based on the underlying geometry of the reasoner's representation space.

## 6. The Promotion Gate: Overcoming Base-Rate Neglect

To satisfy the `STATUS AND BOUNDS` requirement of the query, we must define a deterministic scoring rule that beats a base-rate predictor (`PATTERN_BASE_RATE_NEGLECT`).

### 6.1 The Confound of Base-Rate Predictors
In modeling error distributions, a base-rate predictor is an algorithm that simply learns the overall, global difficulty of a dataset or the most statistically common error across a population, and blindly applies this prediction to every instance [cite: 9, 17]. 

For example, in the distractor prediction task, a base-rate predictor observes that Distractor $C$ is chosen by 35.8% of all students making an error, and thus always predicts Distractor $C$ [cite: 9]. As noted in the user's cross-references, a predictor that learns only overall difficulty will beat a baseline of "nothing" (random guessing) but fails to actually model the *specific* reasoner. This is the `PATTERN_CONDUCTOR_CONFOUND`.

### 6.2 Establishing the Gate
A valid promotion gate for a Tier H1 system requires the system to conditionally adapt its failure-mode prediction based on the specific parameters (latent traits, context, or architectural biases) of the target reasoner. 

Based on the literature, the most accessible and rigorously standardized gate is **Distractor Probability Scoring in IRT datasets** (such as the FoundationalASSIST benchmark).

**The Scoring Rule:**
1.  **Dataset:** A dataset of multiple-choice questions with empirical data on the exact distribution of incorrect answers chosen by a population of learners (e.g., 50% chose A, 30% chose B, 20% chose C) [cite: 9].
2.  **Base-Rate Model ($M_{base}$):** Predicts the error distribution based solely on the global historical average of distractor selection across all users. Accuracy baseline: $\approx 35.8\%$ [cite: 9].
3.  **Tier H1 Model ($M_{H1}$):** Receives the problem, the options, and a representation of the specific reasoner (e.g., an LLM prompt simulating a student with specific knowledge gaps, or a student's historical response trace). $M_{H1}$ outputs a predicted probability distribution over the distractors.
4.  **Evaluation Metric:** Kullback-Leibler (KL) divergence or Cross-Entropy loss between the predicted error distribution and the actual empirical error distribution for that specific sub-population. 

If $M_{H1}$ achieves a statistically significant improvement over $M_{base}$ (e.g., approaching or exceeding the 47.9% mark observed in recent LLM evaluations [cite: 9]), it passes the promotion gate. It has proven that it is not merely relying on base-rate neglect, but is actually modeling *how* the specific system fails.

## 7. Conclusion

The user's hypothesis is highly accurate: current machine Theory of Mind paradigms fail to provide a measurable version of failure-mode distribution, focusing instead on binary belief attribution. Similarly, the algorithm selection and solver portfolio literature is heavily skewed toward predicting *that* an algorithm will fail (runtime/performance) rather than the topology of its errors. 

To build and measure a Tier H1 system that models its own and others' failure distributions, researchers must pivot to **Psychometrics (Item Response Theory)** and **Cognitive Science**. The prediction of distractors in IRT models, and the geometric modeling of continuous error distributions in $n$-AFC tasks, provide the exact deterministic scoring rules needed. By forcing the model to predict the specific structural errors a reasoner will make (its "structured lossiness"), and scoring this against actual empirical data, we can successfully gate models that truly understand *how* intelligence fails.

**Sources:**
1. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWjBkqJumkGex_2z4V8VAPHdav5HUojjisToVGfy76NWEdKcoslgKzv5DZ_-LBBX90olhGTpR9NU1jB7Z1GrtwIopkLQ4VACPcwrmDl07roqi1NRkDRCNXHdDMyG4EbGMcQF12ouiYl82FAKgaU7XEsio=)
2. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtQ-Jijur6tfvuPS7knkOeRGEwqRKgA2flu5kfZhEPFc_g7O5-qa-KDzdbhK10_oMqsCAoJguNgil1v3GWQekvBBMI7bzFahADJVICau5cDrBm6mYEO8LwqskRBs9FCH-fLjrizM2eNClyg_h5)
3. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFWcKKrPpT7TiLjKFWTDILVpz4wzB5TgvQvIZMzxgvfQj_3PXUpIc_OSyU7qzHp1t9uLCkeOMBmpGehGQJCB6iJEY_qEVNJ0m0R1mfuEs9LKvcM8loTGvtZ5vPFFeZ6VM3hePO03jCHn5vhNXdBMVQnnA=)
4. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExkjnVSljE9PUFDtWs0Qyk7iIn21rpTGCXiO46vCFCq1iTUpb0hyxRlYlwbk_lW5uXje3SuSJ0Gd_WlEZkKhJuccFG7ycUanwjrrxmeCTD_tADYThPq6yfyKPreNCFM3jPPCzyxF23porZxjYtUqpzFsFozvwC8KD-TH3I-skRDN3Ha3G4oH7Regu64Ch5B6gOBPI2_niHMW5Ul49NYA==)
5. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMvb0omhAylulHGdmEd8DUBJbSfhjVV9Ew09pXgETHk9TU0FAGgRQba_O4Z0Fv5pd3mpEIxlgKle9F3YKV3OCIcx_wh6riEfzJf8mdtPtDsSXN7ZhTan33v3BzhSl2rBk=)
6. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQES6ZYF97WX72NmWM9GcbLxf44vikXkla9OmZcNO6lh1bBoGIJelizMyGG-BNwoGM7gClNtg5jHQc383_yCYw6thgC8foM6qrhlDKKKgnkYMamMJmqfBgy-NRtk5fKeTA2kYgE=)
7. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMfnPPZGWLel5c3mJPlwDwb29OgRrNuFd5FljtXLrPB3XaIdlQ7bAx4WUbSNsl5oHfafB4_4ATr7lcdrtKOcKZCT-TxihUyhKp95oK0dqL9Vzb_rr5ziXuW1pl0wCsDz86HesbbFhBNsqsowHPoyksLPk=)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ7nmqyqYxfAcLkFW9WwfHAiz4mOpaN1JwQFrUNJBbWSPw3MVAfZPI3dphgBuw3jVQqwyBWzxQ5M9OQPdAbxvqs_PMoYYgvAl0Rjw0lIp4XQj8Kt_p6a5LqQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQaA9TJiDE8Pps3c-2GH-_y79IBRY_oc2ySsmpr_8dWMsI99Fy-JEOYmWX9mTMt-r8sdVy8aElELRbJSrZUKnWZpAdJm8JpVznHDLPfVickmIQj0qqDdWuhA==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECKjQh3OLEe8z3GsirctvC60fSwB3GtPewCD0eH42i3XUyw48gIyvFuZowjXK1FmyPg820I8TOwCmU5pvuno3kUxBn4D1Ex5DLf79rmK4WBiN1bbg_nA==)
11. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFckQxXfll2y66l-CbTTWzqaoPHQ2W1qPZJ8qcOY_YE_X4fYbl9aMSIwcTVMM7AjdID69C9f7y30mAOCv7CUHr6ZKtoT0xOfOV4gNIOkMOijRjYa6akL6XMYx7dug==)
12. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHFm_4DZ1pEodZgPyleDAxOdSHujQ0Kshioj9AbNBJ00vQzOtsSpfK3tl_zlf7YPcnlDHT6ByLl1p3ZODTG4DAPaenXg5R9FIJK52Ddgar9R9yXAukh1Il8bBNtkM=)
13. [rpubs.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzsSzVomvzPomcSyay_WUQBsE9FCVVdYwDMCaacTA4gtFDjNBZu5QgtoCyWMnzzJKp4ptRWWpF5_gOcBIrlv2QVkY28-dROysI2a07MSpHtRMBBf8DCCMDAyaU)
14. [uwyo.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGX43Q6ge0E4cJ-ci1QhNDpT3aUx5bMhBmB0NJFcT2P1CcqB3BNAvHkPCTmn4LCYEhL3NMMb-v1rEVSinrMrRWFD9dWn21Xu-h0ZP6kVib_6a-M7aEYYYto4-fEiqB_YRMRoGxjmnzsNNuwr8FBng2xK62Q2mCjdQJouQ==)
15. [uni-freiburg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHBNFEcGNucSgbjLeQiYQiXaRVNBs8Mnu6BMEIwKC8xwudoPiyNDU3cqMvfkQUNuUzUJAtH5jnuaB8zN2dz7a4grBbDfKQmuRzt-zNQiQp0LPP807ExlqqeHaY2M2HHdETe0Z2Nj_tTCrmE5ds3umYf-pmL7jrP_qufTMmszhMBKTUThkQyNi9)
16. [jair.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeYTTsDdAQROkP_9tMfH-2d-5fAaZjNlE42lveS2cpvxSXVHO7YitDtmPxoxOPqGxFLKhpUkgmyC8o1mJI-TfR0G8CdD45z19oGZ5wEq7WH64aLG6u2JGkjDfZFVh0lw2rFvPZLohHZR0So3Q69r5EYAmI6nHS55TcGEI3)
17. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHemCZUnTJAYckkou5yusRXMKoQxWIcOsnBBa3gbZoCOmCKFJBADwN_nHfQrPWQ_huJWDxF5VGl_VPYxEn77mJeWkmYMHZzIZUdjIxPUmSmgUOwaCuy78vdTJXaOMUSjgx9CLFeHD4=)
18. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZL-SYhJXkSi_Gii56pkJT-oqI6jVwY61ZCw2MYYvKN803KKO4Y6x_Szx2oF_zvlwZjUmnuh2Jpm5NSB6Q-UJEPmiApT2i8tswfekvk9WGST73-2grnFSsP7VZG3Sk-aiiihhQ-jeYz14rBedV1HeBOsgFEXgirHdlL2ceEp9Lg-tSxeQ4GAPe7TKJ4tn7F8APyeC68hqY33ELx--KCFal5Q==)
19. [moltbook.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzg6Z5Nm9PMFCZX4tpdqCbEIMcUwNiEKiZF4dmeq2JUSvqa52FGmARQGfvAb8EiJyoO_99KYaSfTvQj2IMcpOC4f3EZpizfRMCKW2fKh-Ce3nx3nDybDTZPXFaTlK1Xx1YAhQpt5eJWZ64IREijtfYRyx0iJQGbls=)
20. [subliminal.technology](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuTenVdqMItynzcZfn_utAcwlV7FTpSpiAd-hb_2k2ZsN3feT0m_HkurHxxXhr4PUDrkxr-fmeSwuSjkX2yWN6Zf_qnfnAb34iPE6kVTbv8ABXdtXudnwnlPxFwzbw-1FXc18G3-31s4wJtjcCfwAjggJFxg1-Gz8YFfJG4igTeA==)
21. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKnUKYkbuMdeppEhHT68qnWIqM8RmcbE83Plx58_CZdtVhGpRRgubaNRHlQG_dI1MLdBbPiGrOujsw_x4xfxsE7Wsq_1tUCnL2Y--vz36spAuCINeAkrKZClCWFI8tHnSxj216Qbk=)

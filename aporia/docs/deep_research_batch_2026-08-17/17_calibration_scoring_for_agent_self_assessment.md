# Prompt 17: Calibration scoring for agent self-assessment

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZWTEdEYXZUV0ZfYkJzT0lQcHNXVEFREhZWTEdEYXZUV0ZfYkJzT0lQcHNXVEFR
**Elapsed:** 274s

---

{
  "id": "v1_ChZWTEdEYXZUV0ZfYkJzT0lQcHNXVEFREhZWTEdEYXZUV0ZfYkJzT0lQcHNXVEFR",
  "created": "2026-08-18 01:11:48+00:00",
  "status": "completed",
  "steps": [
    {
      "type": "user_input",
      "content": [
        {
          "text": "SUMMARY. Our ladder's calibration rung requires a system to report solved, probable, or\nunder-constrained and be right about it. We also plan to score our own agents' predictive\ncalibration on the decision market.\n\nFLAGGED FINDINGS. We assume proper scoring rules transfer straightforwardly to agent\nself-assessment. This is possibly naive.\n\nPROBLEM STATEMENT. What are established methods and pitfalls for measuring calibration of reasoning\nsystems on mathematical or verifiable-answer tasks? Include proper scoring rules under small\nsamples, calibration under distribution shift, and resistance to gaming.\n\nSTATUS AND BOUNDS. Our sample sizes are in the tens \u2014 exactly where naive Brier scores mislead.\n\nLITERATURE. Primary: forecasting and calibration literature, language-model calibration studies.\n\nATTACK VECTORS. Small-sample pathologies; how a system can appear calibrated while being useless.\n\nCROSS-REFERENCES. PATTERN_BASE_RATE_NEGLECT. PATTERN_VRAM_TRUNCATION_ARTIFACT.",
          "type": "text",
          "annotations": null
        }
      ]
    },
    {
      "type": "model_output",
      "content": [
        {
          "text": "# Measuring Calibration in Reasoning Systems: Methods, Pitfalls, and Small-Sample Dynamics\n\n**Key Points:**\n*   **Small samples heavily distort standard metrics:** Research suggests that evaluating probabilistic calibration with extremely small sample sizes (e.g., $N < 100$) introduces severe statistical artifacts. Naive metrics like the Expected Calibration Error (ECE) become highly unstable, and even robust methods like the empirical Brier score decomposition exhibit systematic biases.\n*   **Proper scoring rules resist gaming but aren't infallible:** While strictly proper scoring rules (like the Brier score and log loss) theoretically compel agents to report honest beliefs, practical application in decision markets requires careful attention to the \"useless forecast\" pathology. A model can game the perception of calibration by outputting perfectly calibrated but completely uninformative base-rate predictions.\n*   **Sharpness must accompany calibration:** It appears essential to evaluate \"sharpness\"\u2014the concentration of predictive confidence\u2014alongside calibration. A system reporting a task as \"solved\" requires high sharpness, whereas an \"under-constrained\" task naturally yields low sharpness. \n*   **Self-consistency provides a label-free confidence proxy:** For mathematical and verifiable tasks, evidence leans toward using the self-consistency of an agent's reasoning traces (e.g., majority voting over multiple sampled paths) as a highly reliable, intrinsic measure of confidence and task difficulty.\n*   **Distribution shift degrades post-hoc calibration:** Systems calibrated via external statistical corrections (like temperature scaling) frequently fail under domain shifts. Intrinsic calibration methods, such as training models to verbalize their own uncertainty, seem to offer superior robustness when moving from training to operational environments.\n\n**Executive Summary**\nYour query outlines a highly specific and challenging operational environment: designing a calibration rung for reasoning systems operating on verifiable mathematical tasks, evaluated within a decision market, and fundamentally constrained by extremely small sample sizes (in the tens). You correctly suspect that naive applications of proper scoring rules might be insufficient or misleading in this regime. \n\nWhen sample sizes are small, standard calibration metrics break down. The empirical reliability component of the Brier score overestimates miscalibration, making well-calibrated systems appear flawed. Furthermore, metrics like the Expected Calibration Error (ECE) are highly susceptible to binning artifacts and sample starvation, rendering them effectively useless for your use case. To defend against \"useless\" but calibrated forecasts\u2014where an agent might hedge by predicting the base rate to minimize penalties\u2014you must adopt a dual-evaluation paradigm: maximizing sharpness subject to calibration. This report comprehensively details the mathematical foundations of proper scoring rules, the specific pathologies of small-sample evaluation, methods for extracting intrinsic confidence from reasoning language models, and robust strategies to prevent gaming within your decision market.\n\n***\n\n## 1. Introduction: The Challenge of Calibrating Reasoning Systems\n\nThe deployment of autonomous agents capable of complex mathematical and logical reasoning necessitates rigorous mechanisms for self-assessment. In the context of your system's \"calibration rung,\" an agent must independently classify a given task as *solved* (high confidence in a specific outcome), *probable* (moderate confidence leaning toward a specific outcome), or *under-constrained* (uninformative or uniform distribution over possible outcomes). More importantly, the system must \"be right about it,\" meaning its self-reported confidence must statistically align with its actual empirical accuracy. This property is formally known as **predictive calibration**.\n\nEvaluating the calibration of these agents within a decision market introduces a unique set of constraints. Decision markets aggregate beliefs by rewarding accurate probabilistic forecasts. The standard mechanism for such markets involves **proper scoring rules**, which mathematically incentivize honest reporting. However, evaluating probabilistic forecasts becomes statistically pathological when the available sample size is small\u2014specifically, in the tens of instances. In this regime, the fundamental assumptions underlying large-sample statistical metrics disintegrate. The empirical decompositions of scores become biased, variance explodes, and agents may exploit statistical noise to appear calibrated while providing useless, uninformative predictions.\n\nThis report investigates the established methods, systemic pitfalls, and theoretical boundaries of measuring the calibration of reasoning systems. It explicitly addresses the mathematics of proper scoring rules, the calibration-sharpness tradeoff, small-sample pathologies, calibration under distribution shift, and the specific attack vectors agents might use to game the evaluation framework. \n\n***\n\n## 2. Fundamentals of Probabilistic Evaluation: Proper Scoring Rules and Gaming Resistance\n\nTo score agents' predictive calibration on a decision market, the foundation of the evaluation framework must rest on **proper scoring rules**. A scoring rule is a measure of the performance of probabilistic predictions made under uncertainty [cite: 1]. It assigns a numerical penalty or reward based on the predicted probability distribution and the actual materialized outcome.\n\n### 2.1 The Mathematics of Proper Scoring Rules\nLet $\\Omega$ be the set of possible mutually exclusive outcomes, and let $\\mathcal{P}$ be a convex class of probability measures on $\\Omega$. A probabilistic forecast is a probability distribution $P \\in \\mathcal{P}$ reported by the agent. If an event $\\omega \\in \\Omega$ materializes, the forecaster receives a score $S(P, \\omega)$ [cite: 2].\n\nA scoring rule $S$ is considered **proper** if the expected score is optimized when the forecaster reports their true underlying belief $Q$. Assuming we treat the score as a penalty (loss) to be minimized:\n\\[ \\mathbb{E}_{\\omega \\sim Q}[S(Q, \\omega)] \\leq \\mathbb{E}_{\\omega \\sim Q}[S(P, \\omega)] \\]\nfor all $P, Q \\in \\mathcal{P}$. The rule is **strictly proper** if the equality holds *if and only if* $P = Q$ [cite: 2, 3]. \n\nStrictly proper scoring rules are the bedrock of mechanism design in prediction markets because they align the agent's expected utility with honest reporting. There is no mathematical loophole or \"clever way to game it by shading your numbers toward 0 or 1\" [cite: 4]. If an agent believes the true probability of an event is 0.7, reporting 0.7 uniquely maximizes their expected payoff [cite: 1, 5].\n\n### 2.2 Standard Scoring Rules\nSeveral proper scoring rules exist, each with different geometric and penalty characteristics:\n\n1.  **The Brier Score (Quadratic Scoring Rule):** The most common proper scoring rule for categorical outcomes. It measures the mean squared error between predicted probabilities and the actual binary outcomes [cite: 6].\n    \\[ BS = \\frac{1}{N} \\sum_{i=1}^N (p_i - o_i)^2 \\]\n    where $p_i$ is the predicted probability and $o_i \\in \\{0, 1\\}$ is the observed outcome. The Brier score is strictly proper and bounded between 0 (perfect) and 1 (worst) [cite: 6]. It gently penalizes deviations from the truth, making it relatively robust to extreme, single-instance errors [cite: 6].\n2.  **The Logarithmic Score (Log Loss):** Defined as $- \\log(p_i)$ for the realized outcome. While strictly proper, the logarithmic score applies an infinite penalty if an agent assigns a probability of 0 to an event that subsequently occurs [cite: 1, 7]. This heavy penalty for extreme overconfidence can be highly destabilizing in small sample sizes, where a single confident error can dominate the entire agent's score [cite: 8, 9].\n3.  **The Spherical Score:** An alternative strictly proper rule that normalizes the prediction vector, often used in multi-class settings to provide a bounded reward mechanism [cite: 1].\n\n### 2.3 Assuming Transferability to Agent Self-Assessment\nYour query flags the assumption that \"proper scoring rules transfer straightforwardly to agent self-assessment\" as possibly naive. This skepticism is well-founded. While proper scoring rules guarantee that a rational, risk-neutral agent maximizing expected utility will report its true internal probability, this guarantee assumes that the agent *has* a well-calibrated internal representation of uncertainty to begin with. \n\nIn large language models (LLMs) and reasoning systems, the \"true belief\" $Q$ is not explicitly defined. Instead, the model outputs a sequence of tokens based on complex internal activations. If the system's internal mechanisms are inherently miscalibrated (e.g., suffering from deep neural network overconfidence), a proper scoring rule will perfectly elicit this *flawed* internal state [cite: 9, 10]. The market will accurately score the agent's internal belief, but the agent's self-assessment will remain objectively wrong with respect to external reality. Furthermore, in decision markets where agents compete, strategic behavior such as risk-aversion or risk-seeking can distort reports away from true beliefs, even under strictly proper rules [cite: 5, 11].\n\n***\n\n## 3. The Calibration-Sharpness Tradeoff and the \"Useless Forecast\"\n\nA critical attack vector in calibration evaluation is how a system can appear mathematically calibrated while being entirely useless for practical decision-making. To understand this pathology, we must decompose the nature of probabilistic forecasts into two distinct properties: **Calibration** and **Sharpness** [cite: 12, 13, 14].\n\n### 3.1 Defining Calibration and Sharpness\nThis distinction was formalized in the seminal 2007 statistical literature by Gneiting, Balabdaoui, and Raftery, who established the paradigm of \"maximizing the sharpness of the predictive distributions subject to calibration\" [cite: 12, 14, 15].\n\n*   **Calibration (Reliability):** Refers to the statistical consistency between the predicted probabilities and the observed empirical frequencies [cite: 13, 14]. If a model predicts an event with 70% confidence, that event should occur exactly 70% of the time. Calibration is a joint property of the predictions and the actual outcomes [cite: 14].\n*   **Sharpness (Resolution):** Refers to the concentration or narrowness of the predictive distributions, independent of the observed outcomes [cite: 13, 14]. A sharp forecast makes bold, highly confident predictions (e.g., probabilities very close to 0 or 1, or very narrow confidence intervals) [cite: 15].\n\n### 3.2 The Base Rate Neglect and Useless Calibration\nA forecast that is perfectly calibrated is not necessarily useful. Consider an agent tasked with identifying verifiable mathematical errors in a dataset where exactly 85% of the solutions are correct. If the agent simply ignores the specific details of every task and universally reports an 85% probability of correctness for *every single problem*, the agent is perfectly calibrated. The predicted probability (0.85) perfectly matches the observed empirical frequency (0.85) [cite: 12, 16].\n\nHowever, this forecast lacks any **sharpness** and is operationally useless. It is the equivalent of a weather forecaster stating the historical average rainfall every day [cite: 15, 17]. This is a severe vulnerability in decision markets: an agent lacking true discriminative reasoning capabilities can game the calibration metric by identifying the dataset's base rate and perpetually predicting it, thereby minimizing its calibration error while effectively acting as a dead node in the system [cite: 18]. \n\nSimilarly, an agent can issue bounds that span from negative infinity to positive infinity; this forecast will technically capture the true outcome 100% of the time, achieving trivial calibration without providing actionable constraints (i.e., an \"under-constrained\" state masquerading as a \"solved\" state) [cite: 15]. \n\n### 3.3 Mitigating the Useless Forecast via Brier Skill Score\nTo prevent agents from exploiting base-rate predictions, evaluation systems must measure sharpness alongside calibration. Proper scoring rules naturally reward both. However, to explicitly quantify how much better an agent is compared to a useless baseline, the **Brier Skill Score (BSS)** is employed [cite: 4, 19].\n\nThe Brier Skill Score normalizes the agent's Brier Score ($BS$) against the Brier Score of a naive reference model ($BS_{ref}$)\u2014typically the empirical base rate (climatology) of the dataset [cite: 4, 19]:\n\\[ BSS = 1 - \\frac{BS}{BS_{ref}} \\]\n\n*   $BSS = 1$: Perfectly calibrated and perfectly sharp (omniscient).\n*   $BSS = 0$: The model performs exactly as well as the naive base-rate predictor. It provides no additional useful information.\n*   $BSS < 0$: The model is worse than simply guessing the historical average, indicating systematic miscalibration or detrimental overconfidence [cite: 4, 19].\n\nBy tying market rewards to a Skill Score rather than a raw score, agents are forced to provide sharp, discriminative insights to extract value from the market. They must correctly differentiate between \"solved\" and \"under-constrained\" contexts without retreating to the safety of the mean.\n\n***\n\n## 4. Small-Sample Pathologies: Why Naive Metrics Mislead\n\nYour system's operational bounds dictate sample sizes in the tens. This is the most dangerous regime for probabilistic evaluation. In this low-data environment, conventional calibration metrics suffer from severe statistical bias, high variance, and pathological failure modes. Relying on naive metrics in this context will inevitably lead to false conclusions about agent performance.\n\n### 4.1 Expected Calibration Error (ECE) Flaws and Binning Biases\nThe Expected Calibration Error (ECE) is the most widely used metric in deep learning calibration [cite: 20]. It partitions predictions into $M$ bins based on confidence scores and calculates the weighted average of the absolute difference between the empirical accuracy and average confidence in each bin [cite: 21, 22]:\n\\[ ECE = \\sum_{m=1}^M \\frac{|B_m|}{N} |\\text{acc}(B_m) - \\text{conf}(B_m)| \\]\n\n**Why ECE fails catastrophically for small samples:**\n1.  **Binning Artifacts:** ECE is exceptionally sensitive to the number of bins and the bin boundaries (equal-width vs. equal-mass binning) [cite: 20, 23, 24]. In small samples, populating 10 or 15 bins with only a few dozen data points leads to extreme volatility. A bin might contain only 1 or 2 samples, causing the empirical accuracy for that bin to strictly be 0%, 50%, or 100%, wildly mismatching the continuous confidence score [cite: 16, 23, 24].\n2.  **Estimation Bias:** ECE is a statistically biased estimator. Because it takes the absolute value of differences, random sampling noise inherently inflates the ECE [cite: 21, 24]. In small sample sizes, even a perfectly calibrated model will report a high ECE purely due to finite-sample variance [cite: 21].\n3.  **Not a Proper Scoring Rule:** ECE only measures calibration, completely ignoring sharpness [cite: 21]. An uninformative model predicting the base rate can achieve a perfect ECE of 0, rewarding the useless forecast attack vector discussed previously [cite: 16].\n*Recommendation:* ECE should unequivocally be abandoned for evaluating systems with $N < 100$.\n\n### 4.2 The Bias in the Empirical Brier Score Decomposition\nThe Brier Score is heavily favored because it is a proper scoring rule. Furthermore, Murphy's famous decomposition splits the Brier Score into three components: Reliability (Calibration), Resolution (Sharpness), and Uncertainty [cite: 4, 6, 25].\n\\[ BS = \\text{Reliability} - \\text{Resolution} + \\text{Uncertainty} \\]\n*   **Reliability:** The mean squared difference between predicted probabilities and observed frequencies within bins. (Lower is better).\n*   **Resolution:** The variance of the observed frequencies across bins. (Higher is better).\n*   **Uncertainty:** The intrinsic variance of the base rate.\n\n**The Small-Sample Bias:**\nWhile the total Brier score is an unbiased estimator of true predictive accuracy, its individual decomposed components are **highly biased in small samples** [cite: 26, 27]. Extensive research by Ferro and Fricker (2012) and Br\u00f6cker (2012) demonstrated that the empirical estimation of the reliability term is systematically biased upwards (positive bias) when sample sizes are small [cite: 26, 27]. \n\nThis means that in small sample sizes, *every model appears less calibrated than it actually is* [cite: 26]. The random fluctuations in the small sample create false gaps between the prediction and the empirical reality, which the squared reliability term interprets as miscalibration. Simultaneously, the uncertainty term is systematically underestimated [cite: 27]. \n\nIf you score agents based on the empirical reliability term of the Brier decomposition without adjusting for this artifact, you will unfairly penalize well-calibrated agents simply due to the statistical noise of $N$ being in the tens. Ferro and Fricker (2012) proposed an optimal first-order bias correction for these components, which decays the bias significantly and is mandatory for evaluating Brier decompositions in small datasets [cite: 26, 27].\n\n### 4.3 Spiegelhalter's Z-Test Failures\nTo rigorously test if miscalibration is statistically significant, researchers often use Spiegelhalter\u2019s Z-test [cite: 28, 29]. This test derives the expected value and variance of the Brier score under the null hypothesis of perfect calibration, providing a Z-statistic to determine if a model deviates significantly from truth [cite: 28].\n\nHowever, the derivation of Spiegelhalter's Z relies on asymptotic normality via the Central Limit Theorem [cite: 28]. In your regime of tens of samples, the distribution of Z deviates sharply from the standard normal distribution $\\mathcal{N}(0,1)$, rendering the resulting p-values highly unreliable [cite: 28]. Furthermore, if an agent frequently hedges by outputting homogeneous probabilities (e.g., $p_i = 0.5$), the variance denominator in the test can become extremely small, leading to an unstable or undefined Z-statistic [cite: 28]. \n\n***\n\n## 5. Eliciting Calibration in LLMs for Verifiable Tasks\n\nWhen deploying reasoning systems (such as LLMs) on mathematical or verifiable-answer tasks (e.g., GSM8K, MATH, AIME), standard classification calibration techniques (like extracting logit probabilities over a fixed vocabulary) are often insufficient. Mathematical reasoning is an open-ended generative process involving multi-step logic. How can an agent reliably quantify whether a task is \"solved\" or \"under-constrained\"?\n\nRecent literature identifies three primary methods for eliciting confidence and enabling self-assessment in reasoning systems [cite: 30, 31]:\n\n### 5.1 Verbalized Probability and Linguistic Calibration\nCan models simply be asked to state their confidence? Research into \"verbalized probability\" suggests they can. A landmark 2022 study by OpenAI introduced the *CalibratedMath* suite, demonstrating that LLMs can be fine-tuned or prompted to express uncertainty about their own answers in natural language (e.g., outputting \"90% confidence\" alongside their mathematical solution) without requiring access to internal model logits [cite: 9, 32, 33]. \n\nWhen trained appropriately using human feedback or specifically designed prompt structures, these verbalized confidence levels map to probabilities that are remarkably well-calibrated [cite: 32, 33]. This finding is vital for agentic systems: an agent can directly format its output to state its perceived state (\"solved\" with 95% confidence, \"probable\" with 60% confidence) based entirely on linguistic self-assessment [cite: 9, 31]. \n\n### 5.2 Self-Consistency as a Label-Free Confidence Proxy\nThe most robust and actively researched method for calibrating reasoning tasks is **Self-Consistency** [cite: 31, 34]. \n\nBecause generative models exhibit stochasticity, an agent can sample multiple reasoning paths (Chain-of-Thought rollouts) for a single mathematical problem [cite: 34, 35]. Each path represents a different logical trajectory. By extracting the final answer from each path and grouping them into clusters, the agent can use the frequency of the most common answer (majority voting) as a proxy for confidence [cite: 34, 35].\n\n**Why it works:**\nSelf-consistency acts mathematically akin to Monte Carlo dropout [cite: 34]. If an agent samples 20 reasoning paths and 18 converge on the same mathematical answer, the agent can report the task as \"solved\" with high confidence. If the 20 paths yield 15 different answers, the agent is internally uncertain, correctly classifying the problem as \"under-constrained\" [cite: 36]. \n\nThis method turns out to be an incredibly strong, label-free estimator of task difficulty and epistemic uncertainty [cite: 36]. Recent statistical frameworks model this process using a Signal-to-Noise Ratio (SNR) and the Martingale Majority Certificate, proving that the margin of majority voting provides a quantifiable, mathematically sound certificate of the model's internal confidence [cite: 36]. \n\nUsing self-consistency, an agent can achieve highly calibrated confidence scores for mathematical tasks without external supervision [cite: 31]. However, a known attack vector here is \"consistent errors\": if a model possesses a fundamental flaw or gap in its reasoning capabilities, it may consistently hallucinate the *exact same wrong answer* across multiple rollouts [cite: 37]. Self-consistency would wrongly interpret this systematic error as high confidence, leading to severe miscalibration penalties on the decision market [cite: 37].\n\n### 5.3 Internal Mechanisms: Probe Verifiers\nBeyond sampling, recent studies reveal that reasoning models naturally encode the correctness of their intermediate steps within their hidden states [cite: 38]. Lightweight probes (hidden verifiers) can be attached to the model's intermediate layers to verify reasoning correctness autonomously [cite: 38]. This allows the agent to calculate an internal \"probability of true\" ($P(True)$) before even completing the generation [cite: 30, 38].\n\n***\n\n## 6. Calibration Under Distribution Shift\n\nA critical failure point for deployed calibration systems is **distribution shift**. An agent might learn to calibrate perfectly on a known benchmark (e.g., GSM8K) but become disastrously overconfident or underconfident when deployed on novel operational data [cite: 31, 33, 39]. \n\n### 6.1 The Failure of Post-Hoc Corrections\nHistorically, ML systems utilize post-hoc calibration methods like Platt Scaling (logistic regression), Isotonic Regression, or Temperature Scaling. These methods use a small, hold-out validation set to mathematically warp the model's raw confidence scores until they align with empirical reality [cite: 16, 40].\n\nHowever, under distribution shift, these external corrections become highly brittle. Studies examining neural network calibration under severe distribution shifts reveal that post-hoc calibration methods become less effective or even actively detrimental [cite: 41]. If the target deployment distribution shifts from the training distribution, the parameters learned by isotonic regression no longer apply, and the model's outputs skew unpredictably [cite: 39, 41]. \n\n### 6.2 Intrinsic Robustness\nInterestingly, intrinsic calibration methods\u2014where the model learns to assess its own uncertainty rather than relying on a post-hoc mathematical wrapper\u2014show greater resilience to distribution shifts. The OpenAI study on verbalized probabilities found that GPT-3's linguistic expressions of uncertainty remained moderately calibrated even when the type or difficulty of the mathematical questions shifted significantly [cite: 32, 33]. \n\nSimilarly, proxy targets derived from unsupervised self-consistency sampling maintain robustness across language shifts and task domain shifts [cite: 31]. Because self-consistency measures the model's actual generative entropy at inference time, it is not artificially anchored to historical validation data. When the model encounters a novel, confusing distribution, the generative paths naturally diverge, lowering the self-consistency score and correctly shifting the reported state to \"under-constrained\" [cite: 31, 36, 37].\n\n***\n\n## 7. Operational Hazards, Attack Vectors, and Edge Cases\n\nOperating a decision market that scores autonomous agents requires anticipating how statistical artifacts and operational constraints can be weaponized or lead to systemic failure.\n\n### 7.1 The PATTERN_VRAM_TRUNCATION_ARTIFACT\nWhile the query abstractly references this, any reasoning system reliant on prolonged Chain-of-Thought generation is susceptible to VRAM or context-window exhaustion. If an agent is midway through solving a complex mathematical task and is truncated, its self-consistency sampling will collapse. The agent might output highly diverse, truncated tokens, artificially driving its confidence to zero. Conversely, if truncation forces an abrupt, identical failure state across all samples, self-consistency might register false 100% confidence. Systems must explicitly identify truncation artifacts before calculating proper scores, invalidating the round rather than penalizing the agent for hardware-induced miscalibration.\n\n### 7.2 Small-Sample Starvation Tactics\nIf the market scores agents across very small samples, a risk-averse agent might deliberately shrink its effective sample size by withholding predictions or reporting uniform probabilities to avoid the variance penalty of the Brier Score. In a small sample, variance dominates. An agent that attempts to be \"sharp\" risks a massive penalty if it misses, whereas an agent that \"hedges\" rides out the noise. This is related to the aforementioned \"useless calibration\" problem [cite: 15]. The market must mandate minimum reporting thresholds and enforce Brier Skill Scores to ensure agents are penalized for failing to provide discriminative value [cite: 4, 19].\n\n***\n\n## 8. Strategic Formulation for the Calibration Rung\n\nGiven the constraints\u2014sample sizes in the tens, verifiable mathematical tasks, and a decision market vulnerable to gaming\u2014the following established methods and boundaries should formulate the architecture of your calibration rung:\n\n1.  **Abolish Binning Metrics:** Do not use Expected Calibration Error (ECE) or any metric reliant on histogram binning [cite: 21]. In the $N < 100$ regime, binning artifacts will generate noise that overshadows true agent performance [cite: 24].\n2.  **Implement Strictly Proper Scoring Rules:** Use the Brier Score as the fundamental unit of economic exchange in the decision market [cite: 6]. It is strictly proper and mathematically prevents agents from gaming the system via dishonest reporting [cite: 1, 5]. Avoid the Logarithmic Score for small samples, as the infinite penalty for a single overconfident error is too volatile for stable market dynamics [cite: 7].\n3.  **Apply Small-Sample Bias Corrections:** If decomposing the Brier Score into Reliability and Resolution for diagnostic purposes, you *must* implement the optimal first-order bias corrections developed by Ferro and Fricker (2012) [cite: 26, 27]. Failing to do so will result in the market algorithm systematically underestimating the calibration of all participating agents due to sample size artifacts [cite: 26].\n4.  **Enforce the Brier Skill Score (BSS):** To combat the \"useless forecast\" attack vector (where agents perpetually predict the base rate to appear calibrated), agents must be scored relative to a naive baseline [cite: 4, 19]. A BSS > 0 proves the agent is providing sharp, calibrated, and useful insights. A BSS $\\leq 0$ indicates the agent is either miscalibrated or useless, warranting exclusion from the \"solved\" tier [cite: 19].\n5.  **Utilize Self-Consistency for Internal Agent Assessment:** For agents to internally distinguish between \"solved\" and \"under-constrained,\" they should utilize self-consistency sampling (majority voting across reasoning paths) [cite: 34, 36]. This provides a mathematically robust, label-free proxy for epistemic uncertainty that resists distribution shift far better than post-hoc methods like temperature scaling [cite: 31, 36, 37].\n\nBy bridging strictly proper scoring rules with bias-corrected statistics and self-consistency mechanisms, the calibration rung can accurately differentiate between agents that truly possess reasoning capabilities and those that merely exploit the statistical noise inherent in small datasets.\n\n**Sources:**\n1. [lesswrong.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7CdfbJWbQ2rxC-BWXO_-K8O9R2EsdIHhRhCqq6RB8WV4KYcFU5xDsMVV7nE3s9qrv3JaU1m1Z0Fau6ZTjxp7MH_guC2YjylnydklhhpQFOFdT04g50baY2jCr1Jd_)\n2. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXJZpQIlKidUl72lqZejcRoIWZlk_Ys0Rk5pahjPPmwB42pWRduy3lWZPUW7QinFXKogpPLhZeu6BClaGD5Q5sM6XJ4VhT26ZsxZXBc-QrQRDH9n_BrCze-ix6yt-rj6vl-EjkuZd8fb0p4KoKY7rCdVNT-d3bkMQ=)\n3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgPDD-VxIDY64ofTmdzdx4IkgIt_eW2PMFCK-Itr9MgfW4hwLzu8_qWDmtgUlnvAh3Qrq6PF2nZ40yFSGqyHdy9PIFRJalJBR5vwlFA7geNpNHj0e2bg==)\n4. [metricgate.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOohrPvDi4y5FSJLh7Rt2iABn5AarjaMBMAu9KYLpZDayUsEzw0b22MunAKHuXPi4TDt2Ez0NvaANukqWhNDt92Vb2XZraiBi0F0qlnYqATFe7mcbk79GWZtBn7qSlOoliLKu4wmuDVo=)\n5. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfqhJXpkaefyQpFG0WQ2_YA0h47Z1uw_E4DFnVV5AL1RaQyebNcACLSMXeDPGRmbVcXp3N86wl07_Tr7IYTaBXxtREIhUtnH8-Kvf4kRXNpRx8f3AlzlwEkO-F_OZHYfBU4U4Rw57fAAU0huBv5mVt_IU=)\n6. [dataopsschool.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU6kr7tNhVRqg3fAqIQRCNMf0e4vcNAz4B-pEyDO_z9nZ7g1P0cDnZ5Gik-3YLIwHkq9qYzoonsp67vZTqCWbN7R58uzO8QHNOdfNi1gItRSzTuTN28oqVebJJNWPlopV2)\n7. [siam.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpwc6ZJ8EfMAKF7P83geQmQPTOo6O_D4TnoXAwsEh3yUQIV6FKQfGcGCuIiKAoayylbg0SJSwfzKQDwgvyzJWSZM6WTf4-m-pByN-f2mE0DdOW11soHbeXxlsuuFKMoM4o2ks=)\n8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcWGEBxM86aPyzl-gSJ5XMpYrWP0tXnyaUh82UHArS4SRFe3B8XATStFUGCU_k3XqHTmFeb9K4BXUGN_O-5mxl7_lzioVBitg5xqzaWH9gjrynGQGZUMnMzV3I3JaNHWh_p2shE6FgKhvR-NCZo3YDtbR64fXrYSwETIgmexhnVAHobhqjz5RIS-XueKhpum_bQQM2samJu9Taajyijg==)\n9. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqtP3b1LXqcHDH8HjuDqCj43cycihxwfqpm9MFQHPn2_BK2hQd9hF9zvCoKSRl5gbN78noq-hWpUHzmlGUmULxWDFf1piYNcgMpXTDmP4h7qGeJ_lOsO_kq52PfmiXNOs63ho5cSHgiV-A1pNs)\n10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGS-3ZbiNLVBwsHh29KjTEWonG2Z8nvH8B1voUMRbhwGpfd2RSk0wMHFBVSjlYtbR4FxoKMuAt1-d_5tEjifkPFSrO9GAJbA8ES1rV8-n-Wr8DoLItyJJcJoQ==)\n11. [informs.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpkhb3RNQrsXD1f26w2-TrNezbIDra-kTrN3n8T2T7T2E8w2CcMF328YFCQpPKevHc14KPRIzWm3QNnN0CQ_w91ns18Fv--HoRR1tZ-Q_hCcAL94mq6J_q3EOPGmrpQ01tDF03ZN4mZIobCJ5eLXw=)\n12. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoindVvodYAkr3YvxXd64UptD8tpxSp5AVt3EfDL-w7gAHwdbQfD0CR7bQJ2qywPPIOGhM6dvTAMomIdvHkON3FWjODcRVzpUnWOOLBdPxITp_9Ywy0PM2OAJKNiwHxEVUuyeDD7tJuM8L5Dw-8P_4wwfONkzXXMwOSSk=)\n13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHUN6BONxJL06k6S5Q4jeMsoKUdR9Sjc00Y-DPh8_BTO5YJsgKQiyWt0u5tuB-aYM7dMoJbtKGbKekOduH1wmfowny9bBo1ZdKyPU5zl9dNvMjiGbF4y0efQ==)\n14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe_pihnuNXCcr3ZSxfwAil8zqo3lUxbPR0n8Coz1TO6iiW2Co7y8Kc5Zb9kbfa8-Kk4IEXX4ph8-uu4PtY6IODxm77cGze-stRIBq9riivxAj-DWBjgofvI_nItzk0h1Ad3NplDCrSRx7Gl7iuuj87y_jefqEa1yexAW1VEwu8ZC7bLdkW57dl7pY4pkhVOFlSR_m7tENlbdiT)\n15. [towardsai.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzv5nc-OhcqBZPgIe6r79OYf0rrUWlVVZdykf2qwpuz3dncdzXEUR7Zo9xlP4inxzoClbltzzUUj3YQXWjAU8JVYVuFE_pQ9SQe71zD3C_ur6hgnHucq4mL4lxPOh5h5sWh0tFCxuq13C6LJ0b9E7dcrZ6846YmyBHVR-CbhUOQU8WbzSLmF_Lprdbh5TQ6feCsSK-SjkgDDCSyKDdsokNotFFiwbtTxkug3vdXw==)\n16. [metricgate.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOQzVL-HhXxn9UDU2t3SAF7WoK8qGDvPJ8FyBLpjRdYsmulsljCP1zEAv1IuBX8ViwKk3bCaVDiJyvCkWbTc75otLkagJ6IpyTdsM7-kL91jPdcqfBMn4BV_yPeXUu72wOaN4xzXhBin9vGf9ACY6L9w==)\n17. [adyog.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUBZb82kfW5vSheXCukQC2-UWRMkVXmr_0WMugRRrz31mMWdXl_m9Jr9kfwg5-v5WxwaLKExBz9AyhLaxO0vAGkBDQgXJCnKZqHQApqRjeEsl4TO_Ci6qgO81Fe8WPIG-EUhkmfIC9AD3gA8FBIhD3ZpBfylTZAgTNM7kVhuNfw5ax)\n18. [ucl.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCapsldzW9WyUvFqY2iemX66V6nlzRTNJs59JctHGHlWTrn5qmsTMwpK7t1O4iRNLkNJJNGMZ9dzSctVXowDvjb9EawaK9mwUoKJnaH5dY8AcsleZ3gUZWjRKD2-Wg3UmewPbpfikhljA10AUeraFr0GYSjA==)\n19. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ_jqxJX3_FAvG0T_Ozd9DAYM190X837B5gBqTczdJsr7bGoIR_CcU0gSqisBJ7sjC8aI5ZfgH2wCL0wsCE-Q0E93ahx7aOeWbLECIr3sVDhPk46tjsSro79ha_GHsv5VMl1j_rVxBExvvdQ==)\n20. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8po80sNhwNAFGRQrzXUbRuGx2Me1CetOpFmmkhCoPqtwnJbfcTQBwbkgBR6Zo5gQ3LFSag6ymTXkBxE855A9U6jf5NgoH6aH96ZW_NoMWbHxZq8X3Mo3971FEtpYTBghWkz6mgw6MI5VLcDZmqU0ljcpdwlFfL2k=)\n21. [dkfz.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEysnfwhiB5dVcKZL1I1de4CcLx4eVX_eP_OYQuDyCPK78QEXq5PT1qD5VCqQVjIAQcoNIO1rluCTREVIufD7ijj03GBGKYgBQV0Iutyr1VmIcfuBFAOgRzx8_mrFN4hvHdQWmAUAxQtUY_oN6XB-HHgaUvy7kt0j617jksASF3VQ==)\n22. [towardsdatascience.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDSBqNBhLI5U3QorCoYP4MSqliWELTAtQUFvrEMycpDkPwRrIpLsm7s4eoIQ2iLihAiZrtkd3Zx7z-EFURPl3JYGXR1spXI47Q-6w2Mo4s_OLb4RtqdS57Ewd1w_t1ueFAQrB6QUSKcWTkDUW4VcjTE_C_9Iqrs1Ki3WZuJ7L3k_U_05B41ZTWgv4mr91cAdTSQ1UlZXJCQUjkrdZluw==)\n23. [dswok.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjd3VyyKDiNGfIsJ206_hP-qvIE9TTHxD8mVZ0dyH5tUPvGvDc4hiW9IvWDPgEoc2dU1UfnT1H5Z2EHT443qm5tvwxfjR2S7OjzGaH0nyKq6U6hKHhLI6hG-CWLOUoMVkDYkALWyc=)\n24. [colorado.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_eTbZq1swXn8bGpG-j5RS7OsiJu9ftzONpVnKoyctqGMPZNGO1qyT7E5mefudw5xBEZWFxYLSRVCOgOAeDWLGlo_XSAQKjJA8opGQcScoO-fRq2u8Ip5wKlQw50NzdEm5LNNU5ebPL5SstCH-ocG6XEaRzzf3dLeBHt5BHPfKP1N-4QbWC_5-WsOQQStp7btI6Rh72Nio)\n25. [scikit-learn.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRA5ppLL-FSE0CX1D8LHesTeXXF15wpRt0J9hlc5-YWnHhykcN9pIey29K0CViydlHMVjcPnnESgj2gAN_fOViXaf1bXesoj90FS7ay-lMaLo_kulQ4qO-_GwkQsyLVVawxnQuSHBforUA9g5PSQ==)\n26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERVkRJ13JM1sCha_PjCj6vwvA0FrUIjQrMGq9gzMo-DkFXzJ1xCDKfrRjZ2B4MY_4yuER3cMRtsJV3su0IHwf0r2dAFNl105TXCkyO4WmrJH5tgp0nkYaJBOitwrgwz0A7evPKelFFxHwZm_oXfEAk6eHPBKCX9vfwTDwnfsQ9j8_F9AUxuLZI2LZubjdZJUFQGaoKJ6pTA32J)\n27. [exeter.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHccgvfXru8cYc0YQd4YDlpGB3UDe2pPdz9Yl9OaBN64orFcQ2IN4SUp4yAgHerJYUrQWJgMK8ti2Wb5kLdHUcreXnWzgYuBxOsIgS2JTL_NtdPt4przTqW3plqSRtGABD9MEBi9ScWe94rtnprttkuXDsiLR9IYVoECk2mUvzro_GmjNkOb-PMomDtkgSYbIf8fSOjhWznxuvCitf-l6bfvq8uBxYEkA==)\n28. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsXCMDN_7LKcG4VVfPKq4bMICNSgO_XD399mydwfLWjigC4iDFqEm0qWxPocNWvD_LP399qCisp-0UdHmDRUT7mQ97b9Kt3s8rsQduWEW7QAI8JNRuocfqk9sKVp0o0KLpj5U7Sn5vzKIU-ktpgp0pOQNNVtK18DWDc3VUL0vsVhiv8WcUksbAtYdlYPs=)\n29. [jvsmedicscorner.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyr5eEIav34bWewueK2f7FWmIZinZoFSVvL1l5WiFI8PE3wnk9mbMVJ1y9x34IEbXb5LShjwiELqGDfuex5MEJyOMbI8YJs8Ta-3ZOWvm5mXPNCas1A27jSrJxhdZ0ke_uPq7w0pplcNUH5Lltzjw7C-unP7gmfqQyfoq5Ddnt7GANNPsW)\n30. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoQa0Zl1aLBJLUsVNVH-xhR90An8KpnjxpQ4nVoZvgKtrvSq4Co0DlTL3MS8ZB5a9DXhQtlX6cQzyR_rXqAMgPKFXYrrQ89nbgy3BeBMDcPB8SvRXwit2pwL1cNdzDC629jUmuNkAk1Q==)\n31. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A==)\n32. [openai.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO6x6p5M2Gi6qEuy0YC1UbRMywWo4vh0s5lceyGyJ6k9mw3AUdbQh_xzlPdQmQ-B7mBYdza2Nn7cF8Yu38O6SkxKDifLjMkI-29xP8QYy9sw_hJTcDWRxwMftN5tGG2p4nRoCXFZZq-M3k301ULivuqH1RF3OBsZPVhgiQRvRnBf41szkP)\n33. [truthful.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnH8oYwgYKEXMo35jd5aZeZa2edhx9jGiLZ4UQLjfxrcSQStGOLqOJ8dUsn4ELHkJ7Fo2C-JKwlulr6ZoSu624caeeKkrLst5lUDzLIbhuJG17A-JNzLuQ0aH3Mmdj0UBVJdNcBQ==)\n34. [themoonlight.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmPH8yrW0jIZ49ad_nmjhIxWPfql9j_VmQqC2epb4uczLyDYyuIJBN79t7TYIYZCq_SL71mKsUjfk7CpFKOs2MKt1jSbFCdkoy0wLAFtB2HT1aETN6YgWkKP0i20ia3w718OySjYAIbCQ7tVI_FFtTihnOBj5HSMoAEnw9LwZXGeAyQ2XaZBKY2DRL0bPKZbY3vA==)\n35. [aman.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDvrNC-UdI7cdC6aK5i5almoZQd6ECWQc96UG_oARvmAOf7o336sfcBciqaN7F-jj_ZLRrnnntSRwSBwBcvngCT6DFyYvgPGVffmS9vWaKiXsMUUjg-vdZWiktwW7wAyNg7IM=)\n36. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl2bgRgDglC36z5ceRBIaKegeevvexxFDbLye3ttV-ZGAecg1gViHRMLrWqpcA_CuXXoP7TY_SpvOdGDmacqsdjADJ0nqJIWLxEClgdb5aLUtTsRIPQNC54w6SjPoJIyYkiM9IaPRPtxgmJi-oxkX07PkvkQ==)\n37. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgre_qOjuWP9D1bdMu-qynfvJFhHnZ3cJLODQlNs7abtKu87E-OEf9fNznD3xmy3RqTxSGXwI0tQKPEm9U21IWOMNqNWdPuFYXWBEnj28dgpt3NmQ_PBaGQei7mye5HgZpBQNsO7ddwgZNSepGys2Tb4D_ZSwBEAPCfOs0DQcIP1gk4rP6dA0m)\n38. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtJpSqhy-lWBNIxG3u652jWnxKs9lgKpKyh2UXbjtLuVI_GO8MWGe2K0O0axQ-dJ1YC2m42LP8eumVf7LlALARwHZ8JjEvjXCnsJ-_MKwRQbI5NQTK_W-LAw==)\n39. [iclr.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8HeCKElKJRuIYU2k_spnOMZl1-XIeQNX0EzDM6Mcfy8sgPV6tS0f-Fvr1v0S1mybJh0z6UsBpzjuujViKqn4CnooJfIn_MjeoWMkNeAlhw9VxgIE1r0_CGlad)\n40. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDR1QpcCPU3VG2RM0zLnix-CFNYbOmg85o9y14j1KhFMCcH-Be5oRNSGHg8icpmiw_fD8UkK5E-NBoULQVSPNVvza00SYSU40b95yxJHJirlxvEp16Syb4p8IWvseqB75UoonZ2s7wobT6c6A3m41CSOgdmO47_ncoj7kjT9F0mQ_fECaaTgfvJHEsRoHzaGOZHw5z6mgTlWSY5PXf1w==)\n41. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvfkVKaMwde3Qe4T2TFsmkNbNLp9G6Eec5GnOxrx0o5tWKuCsnTxVnTHZe_ShXA6AU55SyWoLrl2NylWks2vRwKSaeNftg2mD9wewQEq1LubLUneQwaIDYg4zatRUbRCxqTO1uH_qo)\n",
          "type": "text",
          "annotations": [
            {
              "type": "url_citation",
              "end_index": 5474,
              "start_index": 5465,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7CdfbJWbQ2rxC-BWXO_-K8O9R2EsdIHhRhCqq6RB8WV4KYcFU5xDsMVV7nE3s9qrv3JaU1m1Z0Fau6ZTjxp7MH_guC2YjylnydklhhpQFOFdT04g50baY2jCr1Jd_"
            },
            {
              "type": "url_citation",
              "end_index": 5993,
              "start_index": 5984,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXJZpQIlKidUl72lqZejcRoIWZlk_Ys0Rk5pahjPPmwB42pWRduy3lWZPUW7QinFXKogpPLhZeu6BClaGD5Q5sM6XJ4VhT26ZsxZXBc-QrQRDH9n_BrCze-ix6yt-rj6vl-EjkuZd8fb0p4KoKY7rCdVNT-d3bkMQ="
            },
            {
              "type": "url_citation",
              "end_index": 6418,
              "start_index": 6406,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgPDD-VxIDY64ofTmdzdx4IkgIt_eW2PMFCK-Itr9MgfW4hwLzu8_qWDmtgUlnvAh3Qrq6PF2nZ40yFSGqyHdy9PIFRJalJBR5vwlFA7geNpNHj0e2bg=="
            },
            {
              "type": "url_citation",
              "end_index": 6418,
              "start_index": 6406,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXJZpQIlKidUl72lqZejcRoIWZlk_Ys0Rk5pahjPPmwB42pWRduy3lWZPUW7QinFXKogpPLhZeu6BClaGD5Q5sM6XJ4VhT26ZsxZXBc-QrQRDH9n_BrCze-ix6yt-rj6vl-EjkuZd8fb0p4KoKY7rCdVNT-d3bkMQ="
            },
            {
              "type": "url_citation",
              "end_index": 6689,
              "start_index": 6680,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOohrPvDi4y5FSJLh7Rt2iABn5AarjaMBMAu9KYLpZDayUsEzw0b22MunAKHuXPi4TDt2Ez0NvaANukqWhNDt92Vb2XZraiBi0F0qlnYqATFe7mcbk79GWZtBn7qSlOoliLKu4wmuDVo="
            },
            {
              "type": "url_citation",
              "end_index": 6820,
              "start_index": 6808,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7CdfbJWbQ2rxC-BWXO_-K8O9R2EsdIHhRhCqq6RB8WV4KYcFU5xDsMVV7nE3s9qrv3JaU1m1Z0Fau6ZTjxp7MH_guC2YjylnydklhhpQFOFdT04g50baY2jCr1Jd_"
            },
            {
              "type": "url_citation",
              "end_index": 6820,
              "start_index": 6808,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfqhJXpkaefyQpFG0WQ2_YA0h47Z1uw_E4DFnVV5AL1RaQyebNcACLSMXeDPGRmbVcXp3N86wl07_Tr7IYTaBXxtREIhUtnH8-Kvf4kRXNpRx8f3AlzlwEkO-F_OZHYfBU4U4Rw57fAAU0huBv5mVt_IU="
            },
            {
              "type": "url_citation",
              "end_index": 7169,
              "start_index": 7160,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU6kr7tNhVRqg3fAqIQRCNMf0e4vcNAz4B-pEyDO_z9nZ7g1P0cDnZ5Gik-3YLIwHkq9qYzoonsp67vZTqCWbN7R58uzO8QHNOdfNi1gItRSzTuTN28oqVebJJNWPlopV2"
            },
            {
              "type": "url_citation",
              "end_index": 7408,
              "start_index": 7399,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU6kr7tNhVRqg3fAqIQRCNMf0e4vcNAz4B-pEyDO_z9nZ7g1P0cDnZ5Gik-3YLIwHkq9qYzoonsp67vZTqCWbN7R58uzO8QHNOdfNi1gItRSzTuTN28oqVebJJNWPlopV2"
            },
            {
              "type": "url_citation",
              "end_index": 7529,
              "start_index": 7520,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU6kr7tNhVRqg3fAqIQRCNMf0e4vcNAz4B-pEyDO_z9nZ7g1P0cDnZ5Gik-3YLIwHkq9qYzoonsp67vZTqCWbN7R58uzO8QHNOdfNi1gItRSzTuTN28oqVebJJNWPlopV2"
            },
            {
              "type": "url_citation",
              "end_index": 7785,
              "start_index": 7773,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7CdfbJWbQ2rxC-BWXO_-K8O9R2EsdIHhRhCqq6RB8WV4KYcFU5xDsMVV7nE3s9qrv3JaU1m1Z0Fau6ZTjxp7MH_guC2YjylnydklhhpQFOFdT04g50baY2jCr1Jd_"
            },
            {
              "type": "url_citation",
              "end_index": 7785,
              "start_index": 7773,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpwc6ZJ8EfMAKF7P83geQmQPTOo6O_D4TnoXAwsEh3yUQIV6FKQfGcGCuIiKAoayylbg0SJSwfzKQDwgvyzJWSZM6WTf4-m-pByN-f2mE0DdOW11soHbeXxlsuuFKMoM4o2ks="
            },
            {
              "type": "url_citation",
              "end_index": 7965,
              "start_index": 7953,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqtP3b1LXqcHDH8HjuDqCj43cycihxwfqpm9MFQHPn2_BK2hQd9hF9zvCoKSRl5gbN78noq-hWpUHzmlGUmULxWDFf1piYNcgMpXTDmP4h7qGeJ_lOsO_kq52PfmiXNOs63ho5cSHgiV-A1pNs"
            },
            {
              "type": "url_citation",
              "end_index": 7965,
              "start_index": 7953,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcWGEBxM86aPyzl-gSJ5XMpYrWP0tXnyaUh82UHArS4SRFe3B8XATStFUGCU_k3XqHTmFeb9K4BXUGN_O-5mxl7_lzioVBitg5xqzaWH9gjrynGQGZUMnMzV3I3JaNHWh_p2shE6FgKhvR-NCZo3YDtbR64fXrYSwETIgmexhnVAHobhqjz5RIS-XueKhpum_bQQM2samJu9Taajyijg=="
            },
            {
              "type": "url_citation",
              "end_index": 8153,
              "start_index": 8144,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7CdfbJWbQ2rxC-BWXO_-K8O9R2EsdIHhRhCqq6RB8WV4KYcFU5xDsMVV7nE3s9qrv3JaU1m1Z0Fau6ZTjxp7MH_guC2YjylnydklhhpQFOFdT04g50baY2jCr1Jd_"
            },
            {
              "type": "url_citation",
              "end_index": 9041,
              "start_index": 9028,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqtP3b1LXqcHDH8HjuDqCj43cycihxwfqpm9MFQHPn2_BK2hQd9hF9zvCoKSRl5gbN78noq-hWpUHzmlGUmULxWDFf1piYNcgMpXTDmP4h7qGeJ_lOsO_kq52PfmiXNOs63ho5cSHgiV-A1pNs"
            },
            {
              "type": "url_citation",
              "end_index": 9041,
              "start_index": 9028,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGS-3ZbiNLVBwsHh29KjTEWonG2Z8nvH8B1voUMRbhwGpfd2RSk0wMHFBVSjlYtbR4FxoKMuAt1-d_5tEjifkPFSrO9GAJbA8ES1rV8-n-Wr8DoLItyJJcJoQ=="
            },
            {
              "type": "url_citation",
              "end_index": 9403,
              "start_index": 9390,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfqhJXpkaefyQpFG0WQ2_YA0h47Z1uw_E4DFnVV5AL1RaQyebNcACLSMXeDPGRmbVcXp3N86wl07_Tr7IYTaBXxtREIhUtnH8-Kvf4kRXNpRx8f3AlzlwEkO-F_OZHYfBU4U4Rw57fAAU0huBv5mVt_IU="
            },
            {
              "type": "url_citation",
              "end_index": 9403,
              "start_index": 9390,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpkhb3RNQrsXD1f26w2-TrNezbIDra-kTrN3n8T2T7T2E8w2CcMF328YFCQpPKevHc14KPRIzWm3QNnN0CQ_w91ns18Fv--HoRR1tZ-Q_hCcAL94mq6J_q3EOPGmrpQ01tDF03ZN4mZIobCJ5eLXw="
            },
            {
              "type": "url_citation",
              "end_index": 9812,
              "start_index": 9794,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe_pihnuNXCcr3ZSxfwAil8zqo3lUxbPR0n8Coz1TO6iiW2Co7y8Kc5Zb9kbfa8-Kk4IEXX4ph8-uu4PtY6IODxm77cGze-stRIBq9riivxAj-DWBjgofvI_nItzk0h1Ad3NplDCrSRx7Gl7iuuj87y_jefqEa1yexAW1VEwu8ZC7bLdkW57dl7pY4pkhVOFlSR_m7tENlbdiT"
            },
            {
              "type": "url_citation",
              "end_index": 9812,
              "start_index": 9794,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHUN6BONxJL06k6S5Q4jeMsoKUdR9Sjc00Y-DPh8_BTO5YJsgKQiyWt0u5tuB-aYM7dMoJbtKGbKekOduH1wmfowny9bBo1ZdKyPU5zl9dNvMjiGbF4y0efQ=="
            },
            {
              "type": "url_citation",
              "end_index": 9812,
              "start_index": 9794,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoindVvodYAkr3YvxXd64UptD8tpxSp5AVt3EfDL-w7gAHwdbQfD0CR7bQJ2qywPPIOGhM6dvTAMomIdvHkON3FWjODcRVzpUnWOOLBdPxITp_9Ywy0PM2OAJKNiwHxEVUuyeDD7tJuM8L5Dw-8P_4wwfONkzXXMwOSSk="
            },
            {
              "type": "url_citation",
              "end_index": 10103,
              "start_index": 10085,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe_pihnuNXCcr3ZSxfwAil8zqo3lUxbPR0n8Coz1TO6iiW2Co7y8Kc5Zb9kbfa8-Kk4IEXX4ph8-uu4PtY6IODxm77cGze-stRIBq9riivxAj-DWBjgofvI_nItzk0h1Ad3NplDCrSRx7Gl7iuuj87y_jefqEa1yexAW1VEwu8ZC7bLdkW57dl7pY4pkhVOFlSR_m7tENlbdiT"
            },
            {
              "type": "url_citation",
              "end_index": 10103,
              "start_index": 10085,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzv5nc-OhcqBZPgIe6r79OYf0rrUWlVVZdykf2qwpuz3dncdzXEUR7Zo9xlP4inxzoClbltzzUUj3YQXWjAU8JVYVuFE_pQ9SQe71zD3C_ur6hgnHucq4mL4lxPOh5h5sWh0tFCxuq13C6LJ0b9E7dcrZ6846YmyBHVR-CbhUOQU8WbzSLmF_Lprdbh5TQ6feCsSK-SjkgDDCSyKDdsokNotFFiwbtTxkug3vdXw=="
            },
            {
              "type": "url_citation",
              "end_index": 10103,
              "start_index": 10085,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoindVvodYAkr3YvxXd64UptD8tpxSp5AVt3EfDL-w7gAHwdbQfD0CR7bQJ2qywPPIOGhM6dvTAMomIdvHkON3FWjODcRVzpUnWOOLBdPxITp_9Ywy0PM2OAJKNiwHxEVUuyeDD7tJuM8L5Dw-8P_4wwfONkzXXMwOSSk="
            },
            {
              "type": "url_citation",
              "end_index": 10268,
              "start_index": 10254,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe_pihnuNXCcr3ZSxfwAil8zqo3lUxbPR0n8Coz1TO6iiW2Co7y8Kc5Zb9kbfa8-Kk4IEXX4ph8-uu4PtY6IODxm77cGze-stRIBq9riivxAj-DWBjgofvI_nItzk0h1Ad3NplDCrSRx7Gl7iuuj87y_jefqEa1yexAW1VEwu8ZC7bLdkW57dl7pY4pkhVOFlSR_m7tENlbdiT"
            },
            {
              "type": "url_citation",
              "end_index": 10268,
              "start_index": 10254,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHUN6BONxJL06k6S5Q4jeMsoKUdR9Sjc00Y-DPh8_BTO5YJsgKQiyWt0u5tuB-aYM7dMoJbtKGbKekOduH1wmfowny9bBo1ZdKyPU5zl9dNvMjiGbF4y0efQ=="
            },
            {
              "type": "url_citation",
              "end_index": 10454,
              "start_index": 10444,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe_pihnuNXCcr3ZSxfwAil8zqo3lUxbPR0n8Coz1TO6iiW2Co7y8Kc5Zb9kbfa8-Kk4IEXX4ph8-uu4PtY6IODxm77cGze-stRIBq9riivxAj-DWBjgofvI_nItzk0h1Ad3NplDCrSRx7Gl7iuuj87y_jefqEa1yexAW1VEwu8ZC7bLdkW57dl7pY4pkhVOFlSR_m7tENlbdiT"
            },
            {
              "type": "url_citation",
              "end_index": 10614,
              "start_index": 10600,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe_pihnuNXCcr3ZSxfwAil8zqo3lUxbPR0n8Coz1TO6iiW2Co7y8Kc5Zb9kbfa8-Kk4IEXX4ph8-uu4PtY6IODxm77cGze-stRIBq9riivxAj-DWBjgofvI_nItzk0h1Ad3NplDCrSRx7Gl7iuuj87y_jefqEa1yexAW1VEwu8ZC7bLdkW57dl7pY4pkhVOFlSR_m7tENlbdiT"
            },
            {
              "type": "url_citation",
              "end_index": 10614,
              "start_index": 10600,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHUN6BONxJL06k6S5Q4jeMsoKUdR9Sjc00Y-DPh8_BTO5YJsgKQiyWt0u5tuB-aYM7dMoJbtKGbKekOduH1wmfowny9bBo1ZdKyPU5zl9dNvMjiGbF4y0efQ=="
            },
            {
              "type": "url_citation",
              "end_index": 10764,
              "start_index": 10754,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzv5nc-OhcqBZPgIe6r79OYf0rrUWlVVZdykf2qwpuz3dncdzXEUR7Zo9xlP4inxzoClbltzzUUj3YQXWjAU8JVYVuFE_pQ9SQe71zD3C_ur6hgnHucq4mL4lxPOh5h5sWh0tFCxuq13C6LJ0b9E7dcrZ6846YmyBHVR-CbhUOQU8WbzSLmF_Lprdbh5TQ6feCsSK-SjkgDDCSyKDdsokNotFFiwbtTxkug3vdXw=="
            },
            {
              "type": "url_citation",
              "end_index": 11311,
              "start_index": 11297,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOQzVL-HhXxn9UDU2t3SAF7WoK8qGDvPJ8FyBLpjRdYsmulsljCP1zEAv1IuBX8ViwKk3bCaVDiJyvCkWbTc75otLkagJ6IpyTdsM7-kL91jPdcqfBMn4BV_yPeXUu72wOaN4xzXhBin9vGf9ACY6L9w=="
            },
            {
              "type": "url_citation",
              "end_index": 11311,
              "start_index": 11297,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoindVvodYAkr3YvxXd64UptD8tpxSp5AVt3EfDL-w7gAHwdbQfD0CR7bQJ2qywPPIOGhM6dvTAMomIdvHkON3FWjODcRVzpUnWOOLBdPxITp_9Ywy0PM2OAJKNiwHxEVUuyeDD7tJuM8L5Dw-8P_4wwfONkzXXMwOSSk="
            },
            {
              "type": "url_citation",
              "end_index": 11500,
              "start_index": 11486,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzv5nc-OhcqBZPgIe6r79OYf0rrUWlVVZdykf2qwpuz3dncdzXEUR7Zo9xlP4inxzoClbltzzUUj3YQXWjAU8JVYVuFE_pQ9SQe71zD3C_ur6hgnHucq4mL4lxPOh5h5sWh0tFCxuq13C6LJ0b9E7dcrZ6846YmyBHVR-CbhUOQU8WbzSLmF_Lprdbh5TQ6feCsSK-SjkgDDCSyKDdsokNotFFiwbtTxkug3vdXw=="
            },
            {
              "type": "url_citation",
              "end_index": 11500,
              "start_index": 11486,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUBZb82kfW5vSheXCukQC2-UWRMkVXmr_0WMugRRrz31mMWdXl_m9Jr9kfwg5-v5WxwaLKExBz9AyhLaxO0vAGkBDQgXJCnKZqHQApqRjeEsl4TO_Ci6qgO81Fe8WPIG-EUhkmfIC9AD3gA8FBIhD3ZpBfylTZAgTNM7kVhuNfw5ax"
            },
            {
              "type": "url_citation",
              "end_index": 11821,
              "start_index": 11811,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCapsldzW9WyUvFqY2iemX66V6nlzRTNJs59JctHGHlWTrn5qmsTMwpK7t1O4iRNLkNJJNGMZ9dzSctVXowDvjb9EawaK9mwUoKJnaH5dY8AcsleZ3gUZWjRKD2-Wg3UmewPbpfikhljA10AUeraFr0GYSjA=="
            },
            {
              "type": "url_citation",
              "end_index": 12142,
              "start_index": 12132,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzv5nc-OhcqBZPgIe6r79OYf0rrUWlVVZdykf2qwpuz3dncdzXEUR7Zo9xlP4inxzoClbltzzUUj3YQXWjAU8JVYVuFE_pQ9SQe71zD3C_ur6hgnHucq4mL4lxPOh5h5sWh0tFCxuq13C6LJ0b9E7dcrZ6846YmyBHVR-CbhUOQU8WbzSLmF_Lprdbh5TQ6feCsSK-SjkgDDCSyKDdsokNotFFiwbtTxkug3vdXw=="
            },
            {
              "type": "url_citation",
              "end_index": 12523,
              "start_index": 12510,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ_jqxJX3_FAvG0T_Ozd9DAYM190X837B5gBqTczdJsr7bGoIR_CcU0gSqisBJ7sjC8aI5ZfgH2wCL0wsCE-Q0E93ahx7aOeWbLECIr3sVDhPk46tjsSro79ha_GHsv5VMl1j_rVxBExvvdQ=="
            },
            {
              "type": "url_citation",
              "end_index": 12523,
              "start_index": 12510,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOohrPvDi4y5FSJLh7Rt2iABn5AarjaMBMAu9KYLpZDayUsEzw0b22MunAKHuXPi4TDt2Ez0NvaANukqWhNDt92Vb2XZraiBi0F0qlnYqATFe7mcbk79GWZtBn7qSlOoliLKu4wmuDVo="
            },
            {
              "type": "url_citation",
              "end_index": 12732,
              "start_index": 12719,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ_jqxJX3_FAvG0T_Ozd9DAYM190X837B5gBqTczdJsr7bGoIR_CcU0gSqisBJ7sjC8aI5ZfgH2wCL0wsCE-Q0E93ahx7aOeWbLECIr3sVDhPk46tjsSro79ha_GHsv5VMl1j_rVxBExvvdQ=="
            },
            {
              "type": "url_citation",
              "end_index": 12732,
              "start_index": 12719,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOohrPvDi4y5FSJLh7Rt2iABn5AarjaMBMAu9KYLpZDayUsEzw0b22MunAKHuXPi4TDt2Ez0NvaANukqWhNDt92Vb2XZraiBi0F0qlnYqATFe7mcbk79GWZtBn7qSlOoliLKu4wmuDVo="
            },
            {
              "type": "url_citation",
              "end_index": 13130,
              "start_index": 13117,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ_jqxJX3_FAvG0T_Ozd9DAYM190X837B5gBqTczdJsr7bGoIR_CcU0gSqisBJ7sjC8aI5ZfgH2wCL0wsCE-Q0E93ahx7aOeWbLECIr3sVDhPk46tjsSro79ha_GHsv5VMl1j_rVxBExvvdQ=="
            },
            {
              "type": "url_citation",
              "end_index": 13130,
              "start_index": 13117,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOohrPvDi4y5FSJLh7Rt2iABn5AarjaMBMAu9KYLpZDayUsEzw0b22MunAKHuXPi4TDt2Ez0NvaANukqWhNDt92Vb2XZraiBi0F0qlnYqATFe7mcbk79GWZtBn7qSlOoliLKu4wmuDVo="
            },
            {
              "type": "url_citation",
              "end_index": 14048,
              "start_index": 14038,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8po80sNhwNAFGRQrzXUbRuGx2Me1CetOpFmmkhCoPqtwnJbfcTQBwbkgBR6Zo5gQ3LFSag6ymTXkBxE855A9U6jf5NgoH6aH96ZW_NoMWbHxZq8X3Mo3971FEtpYTBghWkz6mgw6MI5VLcDZmqU0ljcpdwlFfL2k="
            },
            {
              "type": "url_citation",
              "end_index": 14260,
              "start_index": 14246,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEysnfwhiB5dVcKZL1I1de4CcLx4eVX_eP_OYQuDyCPK78QEXq5PT1qD5VCqQVjIAQcoNIO1rluCTREVIufD7ijj03GBGKYgBQV0Iutyr1VmIcfuBFAOgRzx8_mrFN4hvHdQWmAUAxQtUY_oN6XB-HHgaUvy7kt0j617jksASF3VQ=="
            },
            {
              "type": "url_citation",
              "end_index": 14260,
              "start_index": 14246,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDSBqNBhLI5U3QorCoYP4MSqliWELTAtQUFvrEMycpDkPwRrIpLsm7s4eoIQ2iLihAiZrtkd3Zx7z-EFURPl3JYGXR1spXI47Q-6w2Mo4s_OLb4RtqdS57Ewd1w_t1ueFAQrB6QUSKcWTkDUW4VcjTE_C_9Iqrs1Ki3WZuJ7L3k_U_05B41ZTWgv4mr91cAdTSQ1UlZXJCQUjkrdZluw=="
            },
            {
              "type": "url_citation",
              "end_index": 14553,
              "start_index": 14535,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjd3VyyKDiNGfIsJ206_hP-qvIE9TTHxD8mVZ0dyH5tUPvGvDc4hiW9IvWDPgEoc2dU1UfnT1H5Z2EHT443qm5tvwxfjR2S7OjzGaH0nyKq6U6hKHhLI6hG-CWLOUoMVkDYkALWyc="
            },
            {
              "type": "url_citation",
              "end_index": 14553,
              "start_index": 14535,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8po80sNhwNAFGRQrzXUbRuGx2Me1CetOpFmmkhCoPqtwnJbfcTQBwbkgBR6Zo5gQ3LFSag6ymTXkBxE855A9U6jf5NgoH6aH96ZW_NoMWbHxZq8X3Mo3971FEtpYTBghWkz6mgw6MI5VLcDZmqU0ljcpdwlFfL2k="
            },
            {
              "type": "url_citation",
              "end_index": 14553,
              "start_index": 14535,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_eTbZq1swXn8bGpG-j5RS7OsiJu9ftzONpVnKoyctqGMPZNGO1qyT7E5mefudw5xBEZWFxYLSRVCOgOAeDWLGlo_XSAQKjJA8opGQcScoO-fRq2u8Ip5wKlQw50NzdEm5LNNU5ebPL5SstCH-ocG6XEaRzzf3dLeBHt5BHPfKP1N-4QbWC_5-WsOQQStp7btI6Rh72Nio"
            },
            {
              "type": "url_citation",
              "end_index": 14848,
              "start_index": 14830,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOQzVL-HhXxn9UDU2t3SAF7WoK8qGDvPJ8FyBLpjRdYsmulsljCP1zEAv1IuBX8ViwKk3bCaVDiJyvCkWbTc75otLkagJ6IpyTdsM7-kL91jPdcqfBMn4BV_yPeXUu72wOaN4xzXhBin9vGf9ACY6L9w=="
            },
            {
              "type": "url_citation",
              "end_index": 14848,
              "start_index": 14830,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjd3VyyKDiNGfIsJ206_hP-qvIE9TTHxD8mVZ0dyH5tUPvGvDc4hiW9IvWDPgEoc2dU1UfnT1H5Z2EHT443qm5tvwxfjR2S7OjzGaH0nyKq6U6hKHhLI6hG-CWLOUoMVkDYkALWyc="
            },
            {
              "type": "url_citation",
              "end_index": 14848,
              "start_index": 14830,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_eTbZq1swXn8bGpG-j5RS7OsiJu9ftzONpVnKoyctqGMPZNGO1qyT7E5mefudw5xBEZWFxYLSRVCOgOAeDWLGlo_XSAQKjJA8opGQcScoO-fRq2u8Ip5wKlQw50NzdEm5LNNU5ebPL5SstCH-ocG6XEaRzzf3dLeBHt5BHPfKP1N-4QbWC_5-WsOQQStp7btI6Rh72Nio"
            },
            {
              "type": "url_citation",
              "end_index": 15032,
              "start_index": 15018,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEysnfwhiB5dVcKZL1I1de4CcLx4eVX_eP_OYQuDyCPK78QEXq5PT1qD5VCqQVjIAQcoNIO1rluCTREVIufD7ijj03GBGKYgBQV0Iutyr1VmIcfuBFAOgRzx8_mrFN4hvHdQWmAUAxQtUY_oN6XB-HHgaUvy7kt0j617jksASF3VQ=="
            },
            {
              "type": "url_citation",
              "end_index": 15032,
              "start_index": 15018,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_eTbZq1swXn8bGpG-j5RS7OsiJu9ftzONpVnKoyctqGMPZNGO1qyT7E5mefudw5xBEZWFxYLSRVCOgOAeDWLGlo_XSAQKjJA8opGQcScoO-fRq2u8Ip5wKlQw50NzdEm5LNNU5ebPL5SstCH-ocG6XEaRzzf3dLeBHt5BHPfKP1N-4QbWC_5-WsOQQStp7btI6Rh72Nio"
            },
            {
              "type": "url_citation",
              "end_index": 15161,
              "start_index": 15151,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEysnfwhiB5dVcKZL1I1de4CcLx4eVX_eP_OYQuDyCPK78QEXq5PT1qD5VCqQVjIAQcoNIO1rluCTREVIufD7ijj03GBGKYgBQV0Iutyr1VmIcfuBFAOgRzx8_mrFN4hvHdQWmAUAxQtUY_oN6XB-HHgaUvy7kt0j617jksASF3VQ=="
            },
            {
              "type": "url_citation",
              "end_index": 15269,
              "start_index": 15259,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEysnfwhiB5dVcKZL1I1de4CcLx4eVX_eP_OYQuDyCPK78QEXq5PT1qD5VCqQVjIAQcoNIO1rluCTREVIufD7ijj03GBGKYgBQV0Iutyr1VmIcfuBFAOgRzx8_mrFN4hvHdQWmAUAxQtUY_oN6XB-HHgaUvy7kt0j617jksASF3VQ=="
            },
            {
              "type": "url_citation",
              "end_index": 15427,
              "start_index": 15417,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOQzVL-HhXxn9UDU2t3SAF7WoK8qGDvPJ8FyBLpjRdYsmulsljCP1zEAv1IuBX8ViwKk3bCaVDiJyvCkWbTc75otLkagJ6IpyTdsM7-kL91jPdcqfBMn4BV_yPeXUu72wOaN4xzXhBin9vGf9ACY6L9w=="
            },
            {
              "type": "url_citation",
              "end_index": 15829,
              "start_index": 15813,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRA5ppLL-FSE0CX1D8LHesTeXXF15wpRt0J9hlc5-YWnHhykcN9pIey29K0CViydlHMVjcPnnESgj2gAN_fOViXaf1bXesoj90FS7ay-lMaLo_kulQ4qO-_GwkQsyLVVawxnQuSHBforUA9g5PSQ=="
            },
            {
              "type": "url_citation",
              "end_index": 15829,
              "start_index": 15813,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOohrPvDi4y5FSJLh7Rt2iABn5AarjaMBMAu9KYLpZDayUsEzw0b22MunAKHuXPi4TDt2Ez0NvaANukqWhNDt92Vb2XZraiBi0F0qlnYqATFe7mcbk79GWZtBn7qSlOoliLKu4wmuDVo="
            },
            {
              "type": "url_citation",
              "end_index": 15829,
              "start_index": 15813,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU6kr7tNhVRqg3fAqIQRCNMf0e4vcNAz4B-pEyDO_z9nZ7g1P0cDnZ5Gik-3YLIwHkq9qYzoonsp67vZTqCWbN7R58uzO8QHNOdfNi1gItRSzTuTN28oqVebJJNWPlopV2"
            },
            {
              "type": "url_citation",
              "end_index": 16396,
              "start_index": 16382,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERVkRJ13JM1sCha_PjCj6vwvA0FrUIjQrMGq9gzMo-DkFXzJ1xCDKfrRjZ2B4MY_4yuER3cMRtsJV3su0IHwf0r2dAFNl105TXCkyO4WmrJH5tgp0nkYaJBOitwrgwz0A7evPKelFFxHwZm_oXfEAk6eHPBKCX9vfwTDwnfsQ9j8_F9AUxuLZI2LZubjdZJUFQGaoKJ6pTA32J"
            },
            {
              "type": "url_citation",
              "end_index": 16396,
              "start_index": 16382,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHccgvfXru8cYc0YQd4YDlpGB3UDe2pPdz9Yl9OaBN64orFcQ2IN4SUp4yAgHerJYUrQWJgMK8ti2Wb5kLdHUcreXnWzgYuBxOsIgS2JTL_NtdPt4przTqW3plqSRtGABD9MEBi9ScWe94rtnprttkuXDsiLR9IYVoECk2mUvzro_GmjNkOb-PMomDtkgSYbIf8fSOjhWznxuvCitf-l6bfvq8uBxYEkA=="
            },
            {
              "type": "url_citation",
              "end_index": 16623,
              "start_index": 16609,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERVkRJ13JM1sCha_PjCj6vwvA0FrUIjQrMGq9gzMo-DkFXzJ1xCDKfrRjZ2B4MY_4yuER3cMRtsJV3su0IHwf0r2dAFNl105TXCkyO4WmrJH5tgp0nkYaJBOitwrgwz0A7evPKelFFxHwZm_oXfEAk6eHPBKCX9vfwTDwnfsQ9j8_F9AUxuLZI2LZubjdZJUFQGaoKJ6pTA32J"
            },
            {
              "type": "url_citation",
              "end_index": 16623,
              "start_index": 16609,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHccgvfXru8cYc0YQd4YDlpGB3UDe2pPdz9Yl9OaBN64orFcQ2IN4SUp4yAgHerJYUrQWJgMK8ti2Wb5kLdHUcreXnWzgYuBxOsIgS2JTL_NtdPt4przTqW3plqSRtGABD9MEBi9ScWe94rtnprttkuXDsiLR9IYVoECk2mUvzro_GmjNkOb-PMomDtkgSYbIf8fSOjhWznxuvCitf-l6bfvq8uBxYEkA=="
            },
            {
              "type": "url_citation",
              "end_index": 16734,
              "start_index": 16724,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERVkRJ13JM1sCha_PjCj6vwvA0FrUIjQrMGq9gzMo-DkFXzJ1xCDKfrRjZ2B4MY_4yuER3cMRtsJV3su0IHwf0r2dAFNl105TXCkyO4WmrJH5tgp0nkYaJBOitwrgwz0A7evPKelFFxHwZm_oXfEAk6eHPBKCX9vfwTDwnfsQ9j8_F9AUxuLZI2LZubjdZJUFQGaoKJ6pTA32J"
            },
            {
              "type": "url_citation",
              "end_index": 16993,
              "start_index": 16983,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHccgvfXru8cYc0YQd4YDlpGB3UDe2pPdz9Yl9OaBN64orFcQ2IN4SUp4yAgHerJYUrQWJgMK8ti2Wb5kLdHUcreXnWzgYuBxOsIgS2JTL_NtdPt4przTqW3plqSRtGABD9MEBi9ScWe94rtnprttkuXDsiLR9IYVoECk2mUvzro_GmjNkOb-PMomDtkgSYbIf8fSOjhWznxuvCitf-l6bfvq8uBxYEkA=="
            },
            {
              "type": "url_citation",
              "end_index": 17449,
              "start_index": 17435,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERVkRJ13JM1sCha_PjCj6vwvA0FrUIjQrMGq9gzMo-DkFXzJ1xCDKfrRjZ2B4MY_4yuER3cMRtsJV3su0IHwf0r2dAFNl105TXCkyO4WmrJH5tgp0nkYaJBOitwrgwz0A7evPKelFFxHwZm_oXfEAk6eHPBKCX9vfwTDwnfsQ9j8_F9AUxuLZI2LZubjdZJUFQGaoKJ6pTA32J"
            },
            {
              "type": "url_citation",
              "end_index": 17449,
              "start_index": 17435,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHccgvfXru8cYc0YQd4YDlpGB3UDe2pPdz9Yl9OaBN64orFcQ2IN4SUp4yAgHerJYUrQWJgMK8ti2Wb5kLdHUcreXnWzgYuBxOsIgS2JTL_NtdPt4przTqW3plqSRtGABD9MEBi9ScWe94rtnprttkuXDsiLR9IYVoECk2mUvzro_GmjNkOb-PMomDtkgSYbIf8fSOjhWznxuvCitf-l6bfvq8uBxYEkA=="
            },
            {
              "type": "url_citation",
              "end_index": 17620,
              "start_index": 17606,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsXCMDN_7LKcG4VVfPKq4bMICNSgO_XD399mydwfLWjigC4iDFqEm0qWxPocNWvD_LP399qCisp-0UdHmDRUT7mQ97b9Kt3s8rsQduWEW7QAI8JNRuocfqk9sKVp0o0KLpj5U7Sn5vzKIU-ktpgp0pOQNNVtK18DWDc3VUL0vsVhiv8WcUksbAtYdlYPs="
            },
            {
              "type": "url_citation",
              "end_index": 17620,
              "start_index": 17606,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyr5eEIav34bWewueK2f7FWmIZinZoFSVvL1l5WiFI8PE3wnk9mbMVJ1y9x34IEbXb5LShjwiELqGDfuex5MEJyOMbI8YJs8Ta-3ZOWvm5mXPNCas1A27jSrJxhdZ0ke_uPq7w0pplcNUH5Lltzjw7C-unP7gmfqQyfoq5Ddnt7GANNPsW"
            },
            {
              "type": "url_citation",
              "end_index": 17833,
              "start_index": 17823,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsXCMDN_7LKcG4VVfPKq4bMICNSgO_XD399mydwfLWjigC4iDFqEm0qWxPocNWvD_LP399qCisp-0UdHmDRUT7mQ97b9Kt3s8rsQduWEW7QAI8JNRuocfqk9sKVp0o0KLpj5U7Sn5vzKIU-ktpgp0pOQNNVtK18DWDc3VUL0vsVhiv8WcUksbAtYdlYPs="
            },
            {
              "type": "url_citation",
              "end_index": 17952,
              "start_index": 17942,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsXCMDN_7LKcG4VVfPKq4bMICNSgO_XD399mydwfLWjigC4iDFqEm0qWxPocNWvD_LP399qCisp-0UdHmDRUT7mQ97b9Kt3s8rsQduWEW7QAI8JNRuocfqk9sKVp0o0KLpj5U7Sn5vzKIU-ktpgp0pOQNNVtK18DWDc3VUL0vsVhiv8WcUksbAtYdlYPs="
            },
            {
              "type": "url_citation",
              "end_index": 18147,
              "start_index": 18137,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsXCMDN_7LKcG4VVfPKq4bMICNSgO_XD399mydwfLWjigC4iDFqEm0qWxPocNWvD_LP399qCisp-0UdHmDRUT7mQ97b9Kt3s8rsQduWEW7QAI8JNRuocfqk9sKVp0o0KLpj5U7Sn5vzKIU-ktpgp0pOQNNVtK18DWDc3VUL0vsVhiv8WcUksbAtYdlYPs="
            },
            {
              "type": "url_citation",
              "end_index": 18376,
              "start_index": 18366,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsXCMDN_7LKcG4VVfPKq4bMICNSgO_XD399mydwfLWjigC4iDFqEm0qWxPocNWvD_LP399qCisp-0UdHmDRUT7mQ97b9Kt3s8rsQduWEW7QAI8JNRuocfqk9sKVp0o0KLpj5U7Sn5vzKIU-ktpgp0pOQNNVtK18DWDc3VUL0vsVhiv8WcUksbAtYdlYPs="
            },
            {
              "type": "url_citation",
              "end_index": 19008,
              "start_index": 18994,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoQa0Zl1aLBJLUsVNVH-xhR90An8KpnjxpQ4nVoZvgKtrvSq4Co0DlTL3MS8ZB5a9DXhQtlX6cQzyR_rXqAMgPKFXYrrQ89nbgy3BeBMDcPB8SvRXwit2pwL1cNdzDC629jUmuNkAk1Q=="
            },
            {
              "type": "url_citation",
              "end_index": 19008,
              "start_index": 18994,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A=="
            },
            {
              "type": "url_citation",
              "end_index": 19514,
              "start_index": 19497,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO6x6p5M2Gi6qEuy0YC1UbRMywWo4vh0s5lceyGyJ6k9mw3AUdbQh_xzlPdQmQ-B7mBYdza2Nn7cF8Yu38O6SkxKDifLjMkI-29xP8QYy9sw_hJTcDWRxwMftN5tGG2p4nRoCXFZZq-M3k301ULivuqH1RF3OBsZPVhgiQRvRnBf41szkP"
            },
            {
              "type": "url_citation",
              "end_index": 19514,
              "start_index": 19497,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqtP3b1LXqcHDH8HjuDqCj43cycihxwfqpm9MFQHPn2_BK2hQd9hF9zvCoKSRl5gbN78noq-hWpUHzmlGUmULxWDFf1piYNcgMpXTDmP4h7qGeJ_lOsO_kq52PfmiXNOs63ho5cSHgiV-A1pNs"
            },
            {
              "type": "url_citation",
              "end_index": 19514,
              "start_index": 19497,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnH8oYwgYKEXMo35jd5aZeZa2edhx9jGiLZ4UQLjfxrcSQStGOLqOJ8dUsn4ELHkJ7Fo2C-JKwlulr6ZoSu624caeeKkrLst5lUDzLIbhuJG17A-JNzLuQ0aH3Mmdj0UBVJdNcBQ=="
            },
            {
              "type": "url_citation",
              "end_index": 19716,
              "start_index": 19702,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO6x6p5M2Gi6qEuy0YC1UbRMywWo4vh0s5lceyGyJ6k9mw3AUdbQh_xzlPdQmQ-B7mBYdza2Nn7cF8Yu38O6SkxKDifLjMkI-29xP8QYy9sw_hJTcDWRxwMftN5tGG2p4nRoCXFZZq-M3k301ULivuqH1RF3OBsZPVhgiQRvRnBf41szkP"
            },
            {
              "type": "url_citation",
              "end_index": 19716,
              "start_index": 19702,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnH8oYwgYKEXMo35jd5aZeZa2edhx9jGiLZ4UQLjfxrcSQStGOLqOJ8dUsn4ELHkJ7Fo2C-JKwlulr6ZoSu624caeeKkrLst5lUDzLIbhuJG17A-JNzLuQ0aH3Mmdj0UBVJdNcBQ=="
            },
            {
              "type": "url_citation",
              "end_index": 19951,
              "start_index": 19938,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqtP3b1LXqcHDH8HjuDqCj43cycihxwfqpm9MFQHPn2_BK2hQd9hF9zvCoKSRl5gbN78noq-hWpUHzmlGUmULxWDFf1piYNcgMpXTDmP4h7qGeJ_lOsO_kq52PfmiXNOs63ho5cSHgiV-A1pNs"
            },
            {
              "type": "url_citation",
              "end_index": 19951,
              "start_index": 19938,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A=="
            },
            {
              "type": "url_citation",
              "end_index": 20130,
              "start_index": 20116,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmPH8yrW0jIZ49ad_nmjhIxWPfql9j_VmQqC2epb4uczLyDYyuIJBN79t7TYIYZCq_SL71mKsUjfk7CpFKOs2MKt1jSbFCdkoy0wLAFtB2HT1aETN6YgWkKP0i20ia3w718OySjYAIbCQ7tVI_FFtTihnOBj5HSMoAEnw9LwZXGeAyQ2XaZBKY2DRL0bPKZbY3vA=="
            },
            {
              "type": "url_citation",
              "end_index": 20130,
              "start_index": 20116,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A=="
            },
            {
              "type": "url_citation",
              "end_index": 20304,
              "start_index": 20290,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDvrNC-UdI7cdC6aK5i5almoZQd6ECWQc96UG_oARvmAOf7o336sfcBciqaN7F-jj_ZLRrnnntSRwSBwBcvngCT6DFyYvgPGVffmS9vWaKiXsMUUjg-vdZWiktwW7wAyNg7IM="
            },
            {
              "type": "url_citation",
              "end_index": 20304,
              "start_index": 20290,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmPH8yrW0jIZ49ad_nmjhIxWPfql9j_VmQqC2epb4uczLyDYyuIJBN79t7TYIYZCq_SL71mKsUjfk7CpFKOs2MKt1jSbFCdkoy0wLAFtB2HT1aETN6YgWkKP0i20ia3w718OySjYAIbCQ7tVI_FFtTihnOBj5HSMoAEnw9LwZXGeAyQ2XaZBKY2DRL0bPKZbY3vA=="
            },
            {
              "type": "url_citation",
              "end_index": 20554,
              "start_index": 20540,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDvrNC-UdI7cdC6aK5i5almoZQd6ECWQc96UG_oARvmAOf7o336sfcBciqaN7F-jj_ZLRrnnntSRwSBwBcvngCT6DFyYvgPGVffmS9vWaKiXsMUUjg-vdZWiktwW7wAyNg7IM="
            },
            {
              "type": "url_citation",
              "end_index": 20554,
              "start_index": 20540,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmPH8yrW0jIZ49ad_nmjhIxWPfql9j_VmQqC2epb4uczLyDYyuIJBN79t7TYIYZCq_SL71mKsUjfk7CpFKOs2MKt1jSbFCdkoy0wLAFtB2HT1aETN6YgWkKP0i20ia3w718OySjYAIbCQ7tVI_FFtTihnOBj5HSMoAEnw9LwZXGeAyQ2XaZBKY2DRL0bPKZbY3vA=="
            },
            {
              "type": "url_citation",
              "end_index": 20650,
              "start_index": 20640,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmPH8yrW0jIZ49ad_nmjhIxWPfql9j_VmQqC2epb4uczLyDYyuIJBN79t7TYIYZCq_SL71mKsUjfk7CpFKOs2MKt1jSbFCdkoy0wLAFtB2HT1aETN6YgWkKP0i20ia3w718OySjYAIbCQ7tVI_FFtTihnOBj5HSMoAEnw9LwZXGeAyQ2XaZBKY2DRL0bPKZbY3vA=="
            },
            {
              "type": "url_citation",
              "end_index": 20950,
              "start_index": 20940,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl2bgRgDglC36z5ceRBIaKegeevvexxFDbLye3ttV-ZGAecg1gViHRMLrWqpcA_CuXXoP7TY_SpvOdGDmacqsdjADJ0nqJIWLxEClgdb5aLUtTsRIPQNC54w6SjPoJIyYkiM9IaPRPtxgmJi-oxkX07PkvkQ=="
            },
            {
              "type": "url_citation",
              "end_index": 21080,
              "start_index": 21070,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl2bgRgDglC36z5ceRBIaKegeevvexxFDbLye3ttV-ZGAecg1gViHRMLrWqpcA_CuXXoP7TY_SpvOdGDmacqsdjADJ0nqJIWLxEClgdb5aLUtTsRIPQNC54w6SjPoJIyYkiM9IaPRPtxgmJi-oxkX07PkvkQ=="
            },
            {
              "type": "url_citation",
              "end_index": 21354,
              "start_index": 21344,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl2bgRgDglC36z5ceRBIaKegeevvexxFDbLye3ttV-ZGAecg1gViHRMLrWqpcA_CuXXoP7TY_SpvOdGDmacqsdjADJ0nqJIWLxEClgdb5aLUtTsRIPQNC54w6SjPoJIyYkiM9IaPRPtxgmJi-oxkX07PkvkQ=="
            },
            {
              "type": "url_citation",
              "end_index": 21501,
              "start_index": 21491,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A=="
            },
            {
              "type": "url_citation",
              "end_index": 21738,
              "start_index": 21728,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgre_qOjuWP9D1bdMu-qynfvJFhHnZ3cJLODQlNs7abtKu87E-OEf9fNznD3xmy3RqTxSGXwI0tQKPEm9U21IWOMNqNWdPuFYXWBEnj28dgpt3NmQ_PBaGQei7mye5HgZpBQNsO7ddwgZNSepGys2Tb4D_ZSwBEAPCfOs0DQcIP1gk4rP6dA0m"
            },
            {
              "type": "url_citation",
              "end_index": 21899,
              "start_index": 21889,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgre_qOjuWP9D1bdMu-qynfvJFhHnZ3cJLODQlNs7abtKu87E-OEf9fNznD3xmy3RqTxSGXwI0tQKPEm9U21IWOMNqNWdPuFYXWBEnj28dgpt3NmQ_PBaGQei7mye5HgZpBQNsO7ddwgZNSepGys2Tb4D_ZSwBEAPCfOs0DQcIP1gk4rP6dA0m"
            },
            {
              "type": "url_citation",
              "end_index": 22106,
              "start_index": 22096,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtJpSqhy-lWBNIxG3u652jWnxKs9lgKpKyh2UXbjtLuVI_GO8MWGe2K0O0axQ-dJ1YC2m42LP8eumVf7LlALARwHZ8JjEvjXCnsJ-_MKwRQbI5NQTK_W-LAw=="
            },
            {
              "type": "url_citation",
              "end_index": 22252,
              "start_index": 22242,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtJpSqhy-lWBNIxG3u652jWnxKs9lgKpKyh2UXbjtLuVI_GO8MWGe2K0O0axQ-dJ1YC2m42LP8eumVf7LlALARwHZ8JjEvjXCnsJ-_MKwRQbI5NQTK_W-LAw=="
            },
            {
              "type": "url_citation",
              "end_index": 22387,
              "start_index": 22373,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtJpSqhy-lWBNIxG3u652jWnxKs9lgKpKyh2UXbjtLuVI_GO8MWGe2K0O0axQ-dJ1YC2m42LP8eumVf7LlALARwHZ8JjEvjXCnsJ-_MKwRQbI5NQTK_W-LAw=="
            },
            {
              "type": "url_citation",
              "end_index": 22387,
              "start_index": 22373,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoQa0Zl1aLBJLUsVNVH-xhR90An8KpnjxpQ4nVoZvgKtrvSq4Co0DlTL3MS8ZB5a9DXhQtlX6cQzyR_rXqAMgPKFXYrrQ89nbgy3BeBMDcPB8SvRXwit2pwL1cNdzDC629jUmuNkAk1Q=="
            },
            {
              "type": "url_citation",
              "end_index": 22717,
              "start_index": 22699,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8HeCKElKJRuIYU2k_spnOMZl1-XIeQNX0EzDM6Mcfy8sgPV6tS0f-Fvr1v0S1mybJh0z6UsBpzjuujViKqn4CnooJfIn_MjeoWMkNeAlhw9VxgIE1r0_CGlad"
            },
            {
              "type": "url_citation",
              "end_index": 22717,
              "start_index": 22699,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnH8oYwgYKEXMo35jd5aZeZa2edhx9jGiLZ4UQLjfxrcSQStGOLqOJ8dUsn4ELHkJ7Fo2C-JKwlulr6ZoSu624caeeKkrLst5lUDzLIbhuJG17A-JNzLuQ0aH3Mmdj0UBVJdNcBQ=="
            },
            {
              "type": "url_citation",
              "end_index": 22717,
              "start_index": 22699,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A=="
            },
            {
              "type": "url_citation",
              "end_index": 23076,
              "start_index": 23062,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOQzVL-HhXxn9UDU2t3SAF7WoK8qGDvPJ8FyBLpjRdYsmulsljCP1zEAv1IuBX8ViwKk3bCaVDiJyvCkWbTc75otLkagJ6IpyTdsM7-kL91jPdcqfBMn4BV_yPeXUu72wOaN4xzXhBin9vGf9ACY6L9w=="
            },
            {
              "type": "url_citation",
              "end_index": 23076,
              "start_index": 23062,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDR1QpcCPU3VG2RM0zLnix-CFNYbOmg85o9y14j1KhFMCcH-Be5oRNSGHg8icpmiw_fD8UkK5E-NBoULQVSPNVvza00SYSU40b95yxJHJirlxvEp16Syb4p8IWvseqB75UoonZ2s7wobT6c6A3m41CSOgdmO47_ncoj7kjT9F0mQ_fECaaTgfvJHEsRoHzaGOZHw5z6mgTlWSY5PXf1w=="
            },
            {
              "type": "url_citation",
              "end_index": 23344,
              "start_index": 23334,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvfkVKaMwde3Qe4T2TFsmkNbNLp9G6Eec5GnOxrx0o5tWKuCsnTxVnTHZe_ShXA6AU55SyWoLrl2NylWks2vRwKSaeNftg2mD9wewQEq1LubLUneQwaIDYg4zatRUbRCxqTO1uH_qo"
            },
            {
              "type": "url_citation",
              "end_index": 23543,
              "start_index": 23529,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvfkVKaMwde3Qe4T2TFsmkNbNLp9G6Eec5GnOxrx0o5tWKuCsnTxVnTHZe_ShXA6AU55SyWoLrl2NylWks2vRwKSaeNftg2mD9wewQEq1LubLUneQwaIDYg4zatRUbRCxqTO1uH_qo"
            },
            {
              "type": "url_citation",
              "end_index": 23543,
              "start_index": 23529,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8HeCKElKJRuIYU2k_spnOMZl1-XIeQNX0EzDM6Mcfy8sgPV6tS0f-Fvr1v0S1mybJh0z6UsBpzjuujViKqn4CnooJfIn_MjeoWMkNeAlhw9VxgIE1r0_CGlad"
            },
            {
              "type": "url_citation",
              "end_index": 24013,
              "start_index": 23999,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFO6x6p5M2Gi6qEuy0YC1UbRMywWo4vh0s5lceyGyJ6k9mw3AUdbQh_xzlPdQmQ-B7mBYdza2Nn7cF8Yu38O6SkxKDifLjMkI-29xP8QYy9sw_hJTcDWRxwMftN5tGG2p4nRoCXFZZq-M3k301ULivuqH1RF3OBsZPVhgiQRvRnBf41szkP"
            },
            {
              "type": "url_citation",
              "end_index": 24013,
              "start_index": 23999,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnH8oYwgYKEXMo35jd5aZeZa2edhx9jGiLZ4UQLjfxrcSQStGOLqOJ8dUsn4ELHkJ7Fo2C-JKwlulr6ZoSu624caeeKkrLst5lUDzLIbhuJG17A-JNzLuQ0aH3Mmdj0UBVJdNcBQ=="
            },
            {
              "type": "url_citation",
              "end_index": 24170,
              "start_index": 24160,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A=="
            },
            {
              "type": "url_citation",
              "end_index": 24544,
              "start_index": 24526,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgre_qOjuWP9D1bdMu-qynfvJFhHnZ3cJLODQlNs7abtKu87E-OEf9fNznD3xmy3RqTxSGXwI0tQKPEm9U21IWOMNqNWdPuFYXWBEnj28dgpt3NmQ_PBaGQei7mye5HgZpBQNsO7ddwgZNSepGys2Tb4D_ZSwBEAPCfOs0DQcIP1gk4rP6dA0m"
            },
            {
              "type": "url_citation",
              "end_index": 24544,
              "start_index": 24526,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl2bgRgDglC36z5ceRBIaKegeevvexxFDbLye3ttV-ZGAecg1gViHRMLrWqpcA_CuXXoP7TY_SpvOdGDmacqsdjADJ0nqJIWLxEClgdb5aLUtTsRIPQNC54w6SjPoJIyYkiM9IaPRPtxgmJi-oxkX07PkvkQ=="
            },
            {
              "type": "url_citation",
              "end_index": 24544,
              "start_index": 24526,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A=="
            },
            {
              "type": "url_citation",
              "end_index": 26084,
              "start_index": 26074,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzv5nc-OhcqBZPgIe6r79OYf0rrUWlVVZdykf2qwpuz3dncdzXEUR7Zo9xlP4inxzoClbltzzUUj3YQXWjAU8JVYVuFE_pQ9SQe71zD3C_ur6hgnHucq4mL4lxPOh5h5sWh0tFCxuq13C6LJ0b9E7dcrZ6846YmyBHVR-CbhUOQU8WbzSLmF_Lprdbh5TQ6feCsSK-SjkgDDCSyKDdsokNotFFiwbtTxkug3vdXw=="
            },
            {
              "type": "url_citation",
              "end_index": 26258,
              "start_index": 26245,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ_jqxJX3_FAvG0T_Ozd9DAYM190X837B5gBqTczdJsr7bGoIR_CcU0gSqisBJ7sjC8aI5ZfgH2wCL0wsCE-Q0E93ahx7aOeWbLECIr3sVDhPk46tjsSro79ha_GHsv5VMl1j_rVxBExvvdQ=="
            },
            {
              "type": "url_citation",
              "end_index": 26258,
              "start_index": 26245,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOohrPvDi4y5FSJLh7Rt2iABn5AarjaMBMAu9KYLpZDayUsEzw0b22MunAKHuXPi4TDt2Ez0NvaANukqWhNDt92Vb2XZraiBi0F0qlnYqATFe7mcbk79GWZtBn7qSlOoliLKu4wmuDVo="
            },
            {
              "type": "url_citation",
              "end_index": 26686,
              "start_index": 26676,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEysnfwhiB5dVcKZL1I1de4CcLx4eVX_eP_OYQuDyCPK78QEXq5PT1qD5VCqQVjIAQcoNIO1rluCTREVIufD7ijj03GBGKYgBQV0Iutyr1VmIcfuBFAOgRzx8_mrFN4hvHdQWmAUAxQtUY_oN6XB-HHgaUvy7kt0j617jksASF3VQ=="
            },
            {
              "type": "url_citation",
              "end_index": 26801,
              "start_index": 26791,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_eTbZq1swXn8bGpG-j5RS7OsiJu9ftzONpVnKoyctqGMPZNGO1qyT7E5mefudw5xBEZWFxYLSRVCOgOAeDWLGlo_XSAQKjJA8opGQcScoO-fRq2u8Ip5wKlQw50NzdEm5LNNU5ebPL5SstCH-ocG6XEaRzzf3dLeBHt5BHPfKP1N-4QbWC_5-WsOQQStp7btI6Rh72Nio"
            },
            {
              "type": "url_citation",
              "end_index": 26949,
              "start_index": 26940,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHU6kr7tNhVRqg3fAqIQRCNMf0e4vcNAz4B-pEyDO_z9nZ7g1P0cDnZ5Gik-3YLIwHkq9qYzoonsp67vZTqCWbN7R58uzO8QHNOdfNi1gItRSzTuTN28oqVebJJNWPlopV2"
            },
            {
              "type": "url_citation",
              "end_index": 27067,
              "start_index": 27055,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7CdfbJWbQ2rxC-BWXO_-K8O9R2EsdIHhRhCqq6RB8WV4KYcFU5xDsMVV7nE3s9qrv3JaU1m1Z0Fau6ZTjxp7MH_guC2YjylnydklhhpQFOFdT04g50baY2jCr1Jd_"
            },
            {
              "type": "url_citation",
              "end_index": 27067,
              "start_index": 27055,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfqhJXpkaefyQpFG0WQ2_YA0h47Z1uw_E4DFnVV5AL1RaQyebNcACLSMXeDPGRmbVcXp3N86wl07_Tr7IYTaBXxtREIhUtnH8-Kvf4kRXNpRx8f3AlzlwEkO-F_OZHYfBU4U4Rw57fAAU0huBv5mVt_IU="
            },
            {
              "type": "url_citation",
              "end_index": 27225,
              "start_index": 27216,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpwc6ZJ8EfMAKF7P83geQmQPTOo6O_D4TnoXAwsEh3yUQIV6FKQfGcGCuIiKAoayylbg0SJSwfzKQDwgvyzJWSZM6WTf4-m-pByN-f2mE0DdOW11soHbeXxlsuuFKMoM4o2ks="
            },
            {
              "type": "url_citation",
              "end_index": 27474,
              "start_index": 27460,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERVkRJ13JM1sCha_PjCj6vwvA0FrUIjQrMGq9gzMo-DkFXzJ1xCDKfrRjZ2B4MY_4yuER3cMRtsJV3su0IHwf0r2dAFNl105TXCkyO4WmrJH5tgp0nkYaJBOitwrgwz0A7evPKelFFxHwZm_oXfEAk6eHPBKCX9vfwTDwnfsQ9j8_F9AUxuLZI2LZubjdZJUFQGaoKJ6pTA32J"
            },
            {
              "type": "url_citation",
              "end_index": 27474,
              "start_index": 27460,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHccgvfXru8cYc0YQd4YDlpGB3UDe2pPdz9Yl9OaBN64orFcQ2IN4SUp4yAgHerJYUrQWJgMK8ti2Wb5kLdHUcreXnWzgYuBxOsIgS2JTL_NtdPt4przTqW3plqSRtGABD9MEBi9ScWe94rtnprttkuXDsiLR9IYVoECk2mUvzro_GmjNkOb-PMomDtkgSYbIf8fSOjhWznxuvCitf-l6bfvq8uBxYEkA=="
            },
            {
              "type": "url_citation",
              "end_index": 27643,
              "start_index": 27633,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERVkRJ13JM1sCha_PjCj6vwvA0FrUIjQrMGq9gzMo-DkFXzJ1xCDKfrRjZ2B4MY_4yuER3cMRtsJV3su0IHwf0r2dAFNl105TXCkyO4WmrJH5tgp0nkYaJBOitwrgwz0A7evPKelFFxHwZm_oXfEAk6eHPBKCX9vfwTDwnfsQ9j8_F9AUxuLZI2LZubjdZJUFQGaoKJ6pTA32J"
            },
            {
              "type": "url_citation",
              "end_index": 27872,
              "start_index": 27859,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ_jqxJX3_FAvG0T_Ozd9DAYM190X837B5gBqTczdJsr7bGoIR_CcU0gSqisBJ7sjC8aI5ZfgH2wCL0wsCE-Q0E93ahx7aOeWbLECIr3sVDhPk46tjsSro79ha_GHsv5VMl1j_rVxBExvvdQ=="
            },
            {
              "type": "url_citation",
              "end_index": 27872,
              "start_index": 27859,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOohrPvDi4y5FSJLh7Rt2iABn5AarjaMBMAu9KYLpZDayUsEzw0b22MunAKHuXPi4TDt2Ez0NvaANukqWhNDt92Vb2XZraiBi0F0qlnYqATFe7mcbk79GWZtBn7qSlOoliLKu4wmuDVo="
            },
            {
              "type": "url_citation",
              "end_index": 28079,
              "start_index": 28069,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ_jqxJX3_FAvG0T_Ozd9DAYM190X837B5gBqTczdJsr7bGoIR_CcU0gSqisBJ7sjC8aI5ZfgH2wCL0wsCE-Q0E93ahx7aOeWbLECIr3sVDhPk46tjsSro79ha_GHsv5VMl1j_rVxBExvvdQ=="
            },
            {
              "type": "url_citation",
              "end_index": 28325,
              "start_index": 28311,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl2bgRgDglC36z5ceRBIaKegeevvexxFDbLye3ttV-ZGAecg1gViHRMLrWqpcA_CuXXoP7TY_SpvOdGDmacqsdjADJ0nqJIWLxEClgdb5aLUtTsRIPQNC54w6SjPoJIyYkiM9IaPRPtxgmJi-oxkX07PkvkQ=="
            },
            {
              "type": "url_citation",
              "end_index": 28325,
              "start_index": 28311,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmPH8yrW0jIZ49ad_nmjhIxWPfql9j_VmQqC2epb4uczLyDYyuIJBN79t7TYIYZCq_SL71mKsUjfk7CpFKOs2MKt1jSbFCdkoy0wLAFtB2HT1aETN6YgWkKP0i20ia3w718OySjYAIbCQ7tVI_FFtTihnOBj5HSMoAEnw9LwZXGeAyQ2XaZBKY2DRL0bPKZbY3vA=="
            },
            {
              "type": "url_citation",
              "end_index": 28517,
              "start_index": 28499,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEgre_qOjuWP9D1bdMu-qynfvJFhHnZ3cJLODQlNs7abtKu87E-OEf9fNznD3xmy3RqTxSGXwI0tQKPEm9U21IWOMNqNWdPuFYXWBEnj28dgpt3NmQ_PBaGQei7mye5HgZpBQNsO7ddwgZNSepGys2Tb4D_ZSwBEAPCfOs0DQcIP1gk4rP6dA0m"
            },
            {
              "type": "url_citation",
              "end_index": 28517,
              "start_index": 28499,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGl2bgRgDglC36z5ceRBIaKegeevvexxFDbLye3ttV-ZGAecg1gViHRMLrWqpcA_CuXXoP7TY_SpvOdGDmacqsdjADJ0nqJIWLxEClgdb5aLUtTsRIPQNC54w6SjPoJIyYkiM9IaPRPtxgmJi-oxkX07PkvkQ=="
            },
            {
              "type": "url_citation",
              "end_index": 28517,
              "start_index": 28499,
              "title": null,
              "url": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHpzDaYRrR81uXBtbmehO2yDfJsMlmJipfLSu-Eir4hw61m1B8A_2QJW-vsNK1i-2U63MvlNH8sr2E4TxIJbDzo0bHsi4zCTAml6uHPouXUgd0AqvMA7xMw6A=="
            }
          ]
        }
      ]
    }
  ],
  "updated": "2026-08-18 01:11:48+00:00",
  "agent": "deep-research-pro-preview-12-2025",
  "agent_config": null,
  "environment": null,
  "environment_id": null,
  "input": null,
  "model": null,
  "previous_interaction_id": null,
  "response_format": null,
  "response_mime_type": null,
  "response_modalities": null,
  "role": null,
  "service_tier": null,
  "system_instruction": null,
  "tools": null,
  "usage": {
    "cached_tokens_by_modality": null,
    "grounding_tool_count": [
      {
        "count": 15,
        "type": "google_search"
      }
    ],
    "input_tokens_by_modality": [
      {
        "modality": "text",
        "tokens": 166380
      }
    ],
    "output_tokens_by_modality": [
      {
        "modality": "text",
        "tokens": 9271
      }
    ],
    "tool_use_tokens_by_modality": null,
    "total_cached_tokens": 0,
    "total_input_tokens": 166380,
    "total_output_tokens": 9271,
    "total_thought_tokens": 17930,
    "total_tokens": 244023,
    "total_tool_use_tokens": 50442
  },
  "webhook_config": null,
  "object": "interaction"
}

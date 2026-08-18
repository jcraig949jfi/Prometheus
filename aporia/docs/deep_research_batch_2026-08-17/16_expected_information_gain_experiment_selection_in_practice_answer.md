# Optimizing Automated Scientific Discovery: An Analysis of Expected Information Gain Pathologies, Discrimination Count, and Filer Calibration in Decision Markets

**Key Points**
*   **Expected Information Gain (EIG) Limitations:** While mathematically rigorous, EIG-driven experimental selection is fundamentally vulnerable to myopia, capability gating, and cost-blindness, often failing to value constructive, foundational experiments in automated scientific discovery.
*   **Hypothesis Discrimination vs. Parameter Estimation:** Shifting the focus from continuous parameter estimation to discrete scientific hypotheses favors "investigative scaffolding." In small, coarse hypothesis spaces, a simple discrimination count may outperform computationally fragile EIG calculations.
*   **The Interpretability-Informativity Trade-off:** High EIG scores often encourage highly complex, maximally perturbing experiments that, while theoretically informative, produce outcomes that are practically uninterpretable due to human and algorithmic representational constraints.
*   **Filer Calibration in Decision Markets:** Utilizing predicted versus realized information gains to build a calibration track record for human or algorithmic "filers" introduces necessary friction, grounding the experimental market in realized validity and preventing rank-parity leaks or oracle collapse.

The pursuit of automated scientific discovery has increasingly relied on Bayesian experimental design (BED) and active learning to navigate complex search spaces. However, when these methodologies are applied to discrete, scientific hypothesis sets rather than continuous model parameters, significant pathologies emerge. This report investigates the documented failures of information-gain-driven selection—specifically myopia, cost-blindness, and degenerate hypothesis sets. It further evaluates the theoretical viability of ranking candidate experiments by discrimination count rather than estimated value, and examines the role of filer calibration in maintaining the integrity of decision markets. 

***

## 1. Introduction and Problem Statement

The architecture of scientific discovery is undergoing a paradigm shift. Modern automated scientific discovery systems and "AI co-scientists" are increasingly tasked with closing the loop between hypothesis generation, experimental design, execution, and belief updating [cite: 1, 2]. Within this context, deciding *which* experiment to run next is a critical bottleneck.

The prevailing methodology in the literature relies on maximizing a local score, typically Expected Information Gain (EIG) per unit cost, to select the most informative next step [cite: 3]. This approach, deeply rooted in Bayesian Optimal Experimental Design (BOED), has been successful in optimizing continuous model parameters [cite: 4, 5]. However, applying EIG-driven selection to explicit, discrete *scientific hypothesis ledgers*—particularly in regimes constrained to roughly five to ten coarse hypotheses—exposes severe practical and theoretical vulnerabilities. 

Your proposed decision market introduces a counter-paradigm: ranking candidate experiments by the number of live hypotheses their outcome would discriminate between (discrimination count), and scoring each filer's predicted versus realized gain to build a calibration track record. This approach addresses the hypothesis that discrimination count is a more robust ranking signal than estimated EIG value, and that filer calibration prevents the ranking system from degenerating into a self-fulfilling oracle.

This report systematically synthesizes the literature to address the problem statement: What does the literature establish about optimal experiment design, BED, and active learning applied to *scientific hypothesis sets* rather than model parameters? Specifically, we will document the pathologies of EIG criteria, including myopia, capability gating (cost-blindness), and degenerate hypothesis sets, and evaluate the proposed solutions within the bounds of noisy cost estimates and coarse hypothesis spaces.

***

## 2. Theoretical Foundations: BED and Active Learning for Scientific Hypotheses

To understand the failures of EIG, we must first establish its mathematical foundations and how the literature differentiates between parameter estimation and hypothesis discrimination.

### 2.1 The Expected Information Gain (EIG) Paradigm
Expected Information Gain is the central objective in Bayesian Optimal Experimental Design [cite: 6]. It quantifies the expected reduction in uncertainty about an unknown variable (parameter or hypothesis) that a candidate experiment would provide [cite: 5]. EIG is most commonly measured by the Kullback-Leibler (KL) divergence between a posterior and a prior distribution, representing the mutual information between the latent variables and potential observations [cite: 4, 6]. 

In a standard BED framework, the goal is to optimize the experimental design to maximize this expected utility over all possible outcomes [cite: 4, 7]. However, the computational burden is immense. Evaluating EIG generally requires estimating the posterior normalizing constant and computing nested expectations [cite: 8, 9]. While advanced techniques like Multilevel Monte Carlo (MLMC) and amortized neural networks have been proposed to accelerate these calculations, they remain highly sensitive to prior misspecification and finite-sample estimation noise [cite: 5, 8].

### 2.2 Model Parameters vs. Scientific Hypotheses
The literature explicitly distinguishes between experimental design for parameter estimation and design for model (or hypothesis) discrimination. 
*   **Parameter Estimation:** Focuses on narrowing the variance of continuous variables within a single, pre-determined model (e.g., determining the exact reaction rate in a chemical equation).
*   **Model/Hypothesis Discrimination:** Focuses on determining *which* discrete model or generative framework best explains the physical system [cite: 10, 11]. 

When applying BED to scientific hypothesis sets, the Bayesian epistemology framework requires that the set of plausible hypotheses considered at any one time be restricted to a finite set [cite: 12]. The goal of the experiment is to solicit data that disambiguates these scientific hypotheses [cite: 13]. Evidence shifts beliefs in proportion to how well it discriminates between the competitors; evidence that is equally expected under all hypotheses is uninformative [cite: 12]. 

This distinction is operationalized in active learning through algorithms like Bayesian Active Learning by Disagreement (BALD). BALD targets epistemic uncertainty by selecting data points that maximize the mutual information between the predicted outcome and the model hypotheses [cite: 14, 15]. In discrete classification or finite hypothesis spaces, BALD effectively seeks the experiment for which the hypotheses *disagree* the most about the predicted outcome [cite: 16, 17]. 

While BALD and discrete T-optimal discriminating designs [cite: 10] represent the theoretical gold standard for hypothesis discrimination, their practical application in automated laboratories exposes critical, documented pathologies.

***

## 3. Documented Pathologies of Information-Gain-Driven Selection

The literature provides extensive documentation on the practical failures of EIG and active learning criteria, particularly when applied to real-world scientific discovery workflows rather than abstract statistical benchmarks. These "attack vectors" highlight why pure EIG maximization often fails in practice.

### 3.1 Pathology 1: Myopia and the Horizon Problem
The vast majority of standard BOED and active learning approaches are inherently "myopic" or "greedy" [cite: 8, 18]. A myopic planner optimizes the experimental design by looking only one step ahead, maximizing the immediate expected information gain without considering how the current decision influences the information garnered from future steps [cite: 4, 18].

In complex scientific investigations, the optimal sequence of experiments is rarely greedy. Bounded-horizon observation functionals fail because they do not account for the sequential value of information [cite: 3]. For example, a myopic agent might repeatedly choose slight variations of an easily accessible, low-cost experiment that provides marginal information, rather than investing in a sequence of experiments that individually yield less immediate information but collectively rule out a massive swath of the hypothesis space. 

While non-myopic frameworks have been proposed—such as GO-CBED (which optimizes over entire intervention sequences) [cite: 19], GLASSES (which uses stochastic simulation for look-ahead) [cite: 8], and 2-OPT-C (a two-step lookahead for constrained Bayesian optimization) [cite: 20]—these solutions are computationally explosive. They require exact inference over graph structures or heavy Monte Carlo rollouts, making them incompatible with the noisy cost estimates and rapid iteration required by practical decision markets [cite: 19, 20].

### 3.2 Pathology 2: Cost-Blindness and Capability Gating
A more severe structural limitation of myopic EIG is its blindness to "constructive actions" or "capability gating" [cite: 3, 21]. In automated scientific discovery, many actions do not yield immediate empirical data; instead, they acquire an epistemic capability—such as calibrating an instrument, building a data pipeline, synthesizing a chemical precursor, or refining a simulator [cite: 3, 21].

The mathematical architecture of EIG makes it impossible to value these actions. Because EIG is a functional of the predictive distribution of within-horizon observations, a constructive experiment that simply changes the feasible action set *beyond* that horizon yields an EIG of exactly zero [cite: 3]. Consequently, any myopic information-maximizing planner will be strictly dominated by any measurement that yields even a microscopic amount of positive information, completely ignoring the necessary foundational steps of science [cite: 3].

As Hassoon and Dredze (2026) formally prove, for every lookahead depth $d$, there exists an instance where a myopic information-maximizing planner fails because it cannot value actions that modify the downstream action graph [cite: 3, 22]. Attempts to fix this via submodular relaxation or simple cost reweighting fail because one cannot reweight a value that is structurally absent from the scoring functional itself [cite: 3]. Therefore, EIG-driven selection is fundamentally "cost-blind" in environments where costs reflect the necessary acquisition of capabilities rather than just the price of drawing a sample.

### 3.3 Pathology 3: Degenerate Hypothesis Sets and the Interpretability Trade-off
Active learning strategies, particularly BALD, rely on maximizing disagreement among hypotheses [cite: 17, 23]. However, this leads to significant pathologies when hypothesis sets become degenerate. 

**Degenerate Policies and Extreme Perturbations:**
When an agent optimizes strictly for EIG, it quickly learns to exploit the mathematical objective by proposing extreme, "degenerate" experiments. In settings like sequential dialogue or physical perturbation, agents driven by EIG converge to degenerate policies where they repeatedly issue vague, non-specific queries, or extreme physical interventions, simply because these actions mathematically maximize variance and disagreement among the hypotheses [cite: 24]. 

Cheyette et al. (2025) explicitly document this "informativity-interpretability tradeoff" [cite: 25]. Standard EIG assumes perfect, unbounded computational inference. If an algorithm is told to maximize information gain about gene functions, it might propose an experiment that knocks out 50 genes simultaneously. While the *theoretical* EIG of this experiment is massive, the results are completely uninterpretable to human scientists—and often to the algorithm itself—because of bounded representational capacities [cite: 25]. The complex epistemic interactions make it impossible to assign causal attribution.

**Rank Parity Leak and Duplicate Noise:**
In active learning with batch acquisition, methods relying on model disagreement (like BALD) suffer from severe performance degradation when exposed to near-duplicate data or degenerate hypotheses [cite: 14]. If two hypotheses are effectively identical but artificially duplicated in the ledger, the disagreement metric becomes skewed, leading to a "rank parity leak." The system wastes resources trying to discriminate between degenerate variations of the same core theory, failing to explore distinct regions of the hypothesis space [cite: 14, 23].

### 3.4 Pathology 4: Base Rate Neglect and Hallucinations of Information
A final pathology of EIG is its equation of *surprise* with *information*. EIG measures the divergence between prior and posterior; therefore, outcomes that are highly unexpected yield high information gain [cite: 4, 6]. 

In real-world scientific environments with noisy sensors or misspecified priors, this leads to a dangerous manifestation of **pattern base rate neglect**. If an experiment returns anomalous, noisy data, the EIG calculation interprets this extreme deviation from the prior as a massive gain in information [cite: 26, 27]. The algorithm will aggressively prioritize experiments that generate inexplicable noise, treating experimental failure as scientific discovery.

Recent literature on Large Language Models (LLMs) and automated reasoning directly addresses this via "abductive plausibility" [cite: 26]. When information-gain-driven detectors encounter a highly surprising claim, they must check if the informational divergence can be justified by any computationally reasonable abductive hypothesis [cite: 26]. If an experiment yields high EIG but lacks *abductive plausibility* (i.e., it cannot be coherently explained by any combination of the core hypotheses), it is an "informational hallucination" rather than true evidence [cite: 26]. Pure EIG metrics fail to penalize these contradictions, resulting in unresolvable abductive failures [cite: 26].

***

## 4. Defending the Discrimination Count: Investigative Scaffolding

Given the profound vulnerabilities of EIG—myopia, cost-blindness, degeneracy, and hallucination—the literature provides strong theoretical support for your proposed alternative: ranking candidate experiments by how many live hypotheses their outcome would discriminate between (Discrimination Count).

### 4.1 Investigative Scaffolding and Coarse Hypotheses
Your constraint to operate with "roughly five to ten coarse hypotheses" perfectly aligns with the epistemological concept of **Investigative Scaffolding** [cite: 28, 29, 30]. In the historical and observational sciences (e.g., paleobiology, geology), researchers rarely begin by attempting to estimate continuous parameters. Instead, they utilize a "scaffold" of coarse-grained, disjunctive hypotheses [cite: 28, 31].

For example, the "Snowball Earth" hypothesis initially functioned as a coarse scaffold to explain glacial traces. Only after this coarse hypothesis was established and discriminated from non-glacial explanations did researchers generate fine-grained hypotheses (e.g., distinguishing a total "Snowball" from a partial "Slushball" Earth) [cite: 29]. 

Conflating these stages is detrimental. Coarse-grained functional hypotheses are required *before* it is clear what evidence could possibly discriminate between fine-grained ones [cite: 28, 31]. A system that attempts to calculate continuous EIG over fine-grained parameters before the coarse scaffold is resolved will inevitably fall victim to the myopia and cost-blindness described earlier. By explicitly defining a ledger of 5-10 coarse hypotheses, your decision market forces the system to respect the scaffolding process, isolating empirically tractable difference-makers ("one-shot hypotheses") that provide the raw materials for future, more complex explanations [cite: 32].

### 4.2 Discrimination Count vs. EIG under Noisy Constraints
In an environment characterized by noisy cost estimates and non-asymptotic theory, simple heuristic ranking rules frequently outperform complex Bayesian integrations. Psychological and decision-science literature explicitly contrasts "cue validity" (analogous to EIG/predictive power) with "discrimination rate" (the proportion of pairs in which a cue discriminates between alternatives) [cite: 33].

Research on bounded rationality demonstrates that the "tally rule"—which simply counts the number of correct discriminations a cue makes—is highly robust. In environments where discrimination rates are held constant, various alternative ordering criteria (including complex weighted validities) mathematically converge to the exact same rank order [cite: 33]. 

When translated to your decision market:
1.  **Robustness to Noise:** Calculating the exact KL-divergence (EIG) requires highly accurate priors, precise noise models, and stable cost estimates [cite: 6]. If the cost estimates are noisy, the EIG/cost ratio becomes highly volatile, leading to erratic experimental rankings. A simple discrimination count (e.g., "Experiment A rules out 4 out of 10 hypotheses; Experiment B rules out 2") is a topological metric. It is vastly more robust to noise, prior misspecification, and small-sample variance.
2.  **Mitigating the Interpretability Trade-off:** By ranking based on discrimination count among *coarse* hypotheses, the system naturally avoids the degenerate "perturb everything" experiments. An experiment that perfectly discriminates exactly half of the ledger is highly interpretable, whereas an experiment that slightly shifts the probability mass of all hypotheses (high EIG) is not.
3.  **Solving the Capability Gating Problem:** If the decision market allows filers to propose "constructive actions" (e.g., building an assay) and logically link them to the future discrimination of hypotheses, human filers can manually bridge the horizon gap that myopic algorithms cannot. The discrimination count becomes the ultimate terminal reward, but human reasoning maps the path to it, bypassing algorithmic cost-blindness [cite: 3, 21].

***

## 5. Filer Calibration: Preventing the Oracle Collapse

The second flagged finding in your query states that "filer calibration prevents the ranking from becoming an oracle." While the literature explicitly covering human prediction markets in scientific experimental design is sparse (most "calibration" literature in this domain refers to hardware/filter calibration, e.g., IXPE observatory calibration wheels [cite: 34, 35, 36]), we can synthesize the principles of epistemic tracking and active inference to support this claim.

### 5.1 The Danger of Oracle Collapse and Consensus Drift
If a decision market solely aggregates predictions of which experiment will yield the highest discrimination without accountability, it risks falling into **preference optimization compression** or consensus drift [cite: 37]. In AI and human forecasting, post-training or market forces often compress output diversity toward a safe consensus, omitting tacit procedural knowledge and failure risks [cite: 37]. The ranking system becomes a self-fulfilling "oracle" where experiments are funded simply because they are highly ranked by the consensus, rather than because they are actually effective.

### 5.2 Closing the Epistemic Loop through Calibration
Your proposed solution—scoring each filer's *predicted* versus *realized* gain to build a calibration track record—is the structural equivalent of the "Closed Epistemic Loop" required for autonomous scientific discovery [cite: 38].

In Scientific AI, progress is measured not just by task reward, but by the growth of explanatory capacity validated against physical reality [cite: 38]. If a discovery system (or a market of human filers) lacks feedback from physical experiments back to the computational model, it cannot escape the "McNamara fallacy" (optimizing only for what is easily measured, like predicted score, rather than true scientific utility) [cite: 37].

By enforcing a strict accounting of predicted vs. realized discrimination, the market introduces essential epistemic friction:
1.  **Discounting Overconfident Proposers:** Filers who consistently exploit the theoretical objective (e.g., proposing high-EIG, highly perturbed experiments that fail in the lab due to complexity) will suffer poor realized gains. Their calibration track record will degrade, reducing their influence in future rankings. This naturally filters out the "interpretability" pathology [cite: 25].
2.  **Pricing Experimental Uncertainty:** As noted in advanced AI grant-review concepts, tracking historical calibration allows the market to effectively "price experimental uncertainty in real time" [cite: 39]. A highly calibrated filer who proposes a moderate-discrimination experiment with high physical reliability will outrank a poorly calibrated filer proposing a massive, but physically dubious, experiment.
3.  **Abductive Accountability:** When realized gains fail to match predictions, it forces the market into abductive reasoning [cite: 26, 40]. The failure of the experiment to discriminate the hypotheses as predicted becomes a data point itself, signaling that either the hypotheses are misspecified, or the experimental assumptions are flawed.

***

## 6. Synthesis and Operational Recommendations

Your decision market's approach—relying on bounded, discrete hypothesis sets, discrimination counting, and strict filer calibration—is not merely a heuristic shortcut; it is a theoretically sound defense against the well-documented mathematical pathologies of classical Bayesian Experimental Design. 

Based on the literature review spanning automated scientific discovery, cognitive heuristics, and information theory, the following operational conclusions apply to your system:

1.  **Validate Discrimination Count over EIG:** The literature confirms that expected-information-gain criteria fail catastrophically under noisy constraints, bounded horizons, and complex multi-variable interventions [cite: 3, 25]. In a finite space of 5-10 coarse hypotheses, calculating continuous EIG is computationally wasteful and epistemically dangerous. A discrimination count (seeking maximum disagreement among discrete version spaces) acts as a robust, non-parametric topological filter that resists the variance and hallucinations inherent in EIG [cite: 24, 33].
2.  **Leverage Scaffolding for Coarse Hypotheses:** Strictly enforce the "coarse" nature of the hypotheses. Do not allow the ledger to become polluted with highly granular, parameterized variations of the same theory. This prevents "rank parity leaks" and degenerate hypothesis sets from breaking the discrimination count [cite: 14, 28].
3.  **Implement Bounded Representational Penalties:** Acknowledge the informativity-interpretability tradeoff [cite: 25]. Ensure that the market allows filers to challenge experiments that, while theoretically discriminating many hypotheses, are practically impossible to execute or interpret (e.g., experiments requiring the simultaneous control of too many noisy variables). 
4.  **Calibrate to Defeat Capability Gating:** Because algorithms cannot intrinsically value "constructive" actions (building tools, assays) [cite: 21], the calibration of human filers is the only way to navigate capability gating. Calibrated filers can foresee that taking an initial action with zero immediate discrimination will unlock a subsequent action with massive discrimination. Rewarding filers for accurate long-term realized trajectories will organically solve the myopia that plagues automated BOED systems.

By grounding the decision market in discrete discrimination and realized epistemic accountability, your framework effectively sidesteps the asymptotic mirages of traditional information theory, providing a robust architecture for practical, resource-constrained scientific discovery.

**Sources:**
1. [4m4.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdkNK4l_zKbXnPqa6ghuuB47sSGn2Kd2rM_h19OM5FqgIOcMGEuBQHBu3O2B4GNZiZEr1yarB6cm8yhztA6iwonG043rWJveqWvz7tk3aRW7v0e6z471fgUtQFNa2V-oNIwad0P0C52rFrK9p-VQWYjmr4HNIdoXbo)
2. [northflow.no](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGadHfOD7Oh7zuIhJ96H1ajWU3UERPsRC93djOOs93HmbTR1BFlv7GWmxWxkDeEJgytAgJYB5urksfRrRh9hX0eaP_DgdojgDXlsPQPGqugAfTOxuDTww==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuhFK-RQZk-6_s954pinW6lj019go88xtGPMAQDYvBi2FFONvCPxMNrCG3chKUccSL2E7o1w_kQWeAaTjFyz2zNNYmPRrL3VvuO9CBFY6UQmcwvOuJWBJh)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeji76l0-hX9g5EU2SZeQbabbvDkdeyw-oe2MpFMNdBM_i-7VlFHgjKjFK1M_4nFkuhnh7yBZfvCwRmGGGTndfvBL5seAjBteJLTLObUEZc-oN4IlA)
5. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZvMc-IOinkPVBjyLt666crq5yz1T12DCEFCno1Ak2tA3IKA3mlKFNhhehPeqfbJQ897V76Yk0lVbnLTfbOCvXrx0jTJPorPDRkUHXSMua06lkkIMHd7NOcgAs4V7qFkkR8q_aHc0p29GBwyoszWsymbLy6NY1)
6. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-or-Jr41RrPMElFRTzAL9IIpUv9gL2mbyxpdYSGdPKYRjeKoIlxXVHsuumIJQrEKn-JnTkX-RBk5wPFkUHUMCp107BibIBmhT-9cZgk_9DvGV9HTiCqqaoF9EAHuTo-FypZwCpe3uSNQAGcHbRHqhWQ48Lw==)
7. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvmmZED3QoC0dvuCPewUSoULktTH1Yrr3DGwhBjw6cOtYOYbbRNOsYHYf9jkMvmZCbhYTyZHFLOwIzJj9FDbOTLv8xXCDajWbEHgw3vSUBB1JaVGNakvyZ3W602n24xV8EDHkRonkqJvS88gkrgas3n46z2tDUc69qcA--t-CFgXPYgY-_g0KqdyzN-EjsIoHDwriyQiLXDmpBkXb7s0-EFoMYtlZYpagy0wM7JQmRWQjK-9adqJnCTAAysk_vHbN-9M692BLEaQgS3xTFYPGs83dy8gWID8f0vfcMfRNb7aMSpO1P)
8. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZRo6tjNvCQC-9qrbo2pzQvHD6ge538g5b9lu3r2LOPk6KUQrWN08KzoMFalMQl7P8jlGK9RioB9PzSdyNeb3MKeIL5OZsbVD5TXIyp2mvdh0gTICtsIHoOS6syr4k4FYTHhWbQdtR1Mgz-oraHneBrdu-wWOsvd4s89vddObF2m_OG08kU4qazkQewfzmZUrYY7KNgszpaBS8WgATomdys1czmKMe_NtyhZ8Ocxao)
9. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxKeUXlB6b8OthWWsVLYczZLYwhmCYCB2hYAr6kt5mePpEwbrPGLdUCzBEteBvyZ1mpwcfOb6S2c-SyQKXSsP9yyJ9EXCann0xAFYY-sXn_511iP1xnSCVBT4man4=)
10. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrXPZvLon7FvdeUaux7gBxNF71f6vOGhg0OqZVTGXYmw7BL3KgwSSzCmtiFx_0ow-amxQ6aI_SxR4sO78GKa6MuNQjpVPVa4wBolVeiuLT2KIes1RsO6qfpTZw5RKrEF9chY8lxJA=)
11. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA8kp5BM5XbovHPwb1nt8Q3hwo2jUYYxf5I0c37b_-FIcvqqumT7VrR-esT3UXuS4qob-DYyXStzUjSnWmMyndWgiR1TbDYY61C6Z1w_KyDOzB_ehELACpf459Hz_mr_Np2_6yd3nqs9Nwc0xnYMtyGAL9C0O6)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLex2_fOCcnuVG8kgMURzkZMf93uOkI1hxijBYbvLwdSRSgJkGwOQYs3ECLGrQ-B_fbHSE7DzERgCL0UVKO7Nhc6y33ClgoyyZddRwv25vnc2AOSZW-2Kg)
13. [bsahely.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7-dD6K8QlVxtwJXFMwMdFk0egUBrE_lfwOOgfKpaUe6ocjUhzY8Ycn8EwX9uCgDrzY-2Uy4WUh_n6TXb3WqpC2hoS-5TobIUlJ53wQDMZdcC7zdPSVJPVRyk9icWLcCv5anGHBIjHV-ie-B6NKzv6sIvljPuag0om2lWjoY7g9gkFetsCTLJ7UmP9_dohswT0Vh8IUFc5Iv670bZVHaM=)
14. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsrp7LJgt6vNN9g9C2Bpne14KrKwRlXjnpcvSKzArL8FfD2_RfHVKGJgxNW2XKWZ56KIiffkEZWbJgabvXDj5LIuYr2egrdsAGfctWcBYaoyBDLIWmCObisZkWYDEE4w9EbfMziCO-bdfqaljyxcPjtA==)
15. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGx1BP74NjYfR0SMaHspWMgTKrSefofJwOUnCl4I0bsHRuD1yDEn2fYrwP2cX9_CMbzG2TheY0biLF93r0BmuGdyMMPzVf5ndvD3xe6rlt50ijTm-G6cFClgPCTmsqm4gLQEy-iUldiCGEhmAE2Q0Fvtp-aQrLMJ9sJYRb_DF08RqaSUimgnpORCFnAEfXX2LOFe2STcyukUNfCe2vON_TR5mtCUB-njRvVDg==)
16. [learnbayesstats.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGq0-qkE5VmQeU9EOLkJeatrIJKffYJuJAkBm4iAPbfRmYQ_LXPOvXZJ1Tg2N2QghOfnbtYDrjEAHSx-eo2hrLBtyrpWTxFYIJzGAMzTl9wW2E6hKYKpdR2gXtNhzVClaGnQvhP14xD5Mf9sHka7L2nAKxkGk27Pcd5wkNt4ClQ6DG7spA-)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjlBxQZEJIT-fFtxPO3pOeCDqsjdWEVQdst7Gt-xN-nwuWR8LVrNJtgabpZIyzl52HzB1OVDCb1g_IJFrhYHaek4wDFa-BIJim_I23xmk_bG5k4fQ=)
18. [desirivanova.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNA1FbjJKxFxyaakTHjcM3ecWdo-5LxjQFWA-FcnE8L3tbJRGNLbdq9Ah7B81h3oNOYXNviV6cFz-YLA4Wy3Qi4Y4MiouOZnVxKjjgkJ5nSCpE7eo8qGqArfRxDF2n)
19. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2VVv2IPLG7uk5ZfwMOqilSqfoO9yR1B5CxVlp2Aj_Ze1wToJR3LfG5-GJieej-sV-MYHoxA_LsXhxFRqDl-Yr_q1o1RV_MzEGU3lWi8N6aklCKp0k0RRE7QDJoxSWpQ==)
20. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFq63wOgopxCHLPOwhrctDqLbi9wUTmGNDjeI6a9OMAGx_vdQChcWt3H5l6tuZkFk7hDwen1WluVgm8T4axUjlK_v9wVO6NYD-f2OQtDJyjy7ndAfXgijxtY7Zqzmnf1Jv-3T1q3BYQ-kmOgppRj9E0KyFTUx7-rrdYIptTthFVk7vFdbv1I76h5Rruhpg2)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFvVA17YXh7nqH-FTTfQ9HKpMGjpdr-0YfmxF2e2m_ln7edNYGimQRqubBPSdELy8NZr17DdTq4pR9vjmo1m2iw0FkZigDJJ4yhq_HZciqT5uXLadl-3cm6y7eMTBf1mtN9Ep-IqWzQbuqQrZZ8wvUP-KTWi6AvAqWphpQPd2NDlc1g948PsQlHbt7_ySfFZICRO3hsarXhwk-jqe00lI4qC3bjnkFJq1ImhMLGNqQ-BDokt_yG9wk1NU11hCHEcA-k-dfgUfKO)
22. [aigc.news](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzga-PCUuS6_cqae8pao2v3IyNgj2nN1e0Fki73GxjtiwfSASaYKodXpUJ3dxlBw1BHsiupdhp5SCEWTacyO1wmmaIzWabzR4YTVOI05aYqzAOwQfEG_2ZmweOdCZcqYb3K6cEBZkYQJdBoIxy0L1v5tyLkS9gzeBrKVnioprdPCm3sXoVBZBW8RD_PDmaLG9i8rc1yg4VDjJ86P2u046mMtRCxv1bPRh0mvZ078Inc1BcNp8sMTSX0J-U5HmsesXbvg==)
23. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZ2_gB6hTSfy0ew1Gqk7X1LDKH1UdPxipsxC1dU0LtWVRxLBKA4dJ2Er5BktyYSVzebb6mHVwNQwzzuZgMU9r3p91GEhdNFej5oRtG9klO6gLK9qNgEnOwx8QXmVVCK681FRMXjPUMu8cgOWiDvW2U8Yczow==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3pokhwDw1ycyn0ggme9Kvm2nN17aztTGKCs0QJpR20ltHKmq5PAG-h_IShmrhoFPMjG_ndvLyZGo-ADBqfiqswdNTjiEutfNqwN3OFt3LdQXo0szFAMVE)
25. [samcheyette.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxtHgvuLFp_Mrxv-yJeK158cETYn0oflkgtcTfTh8E-LHCuQ6eYzXEq5PASN1UT0E6kZiYZsQFZjOTLpVROzCsH-EBifJy-mGUWoB4CASh2wv7O8HmccCxNHEEEC7yD3AAv6TbSSrNrV4lF_g71BR1T-d_HU6lWQsY)
26. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGi3Aa6j-w-66Rc4842wpqryK4hlkXgZDq8juU8g0RffjK9heeoUjksZfBo2RQY824ej74FljYiFTte1V5df-3RriTzKC7sVxLVlfN1rZzCHUq_r3MEDrJqjweZhTfD-XhGL53YzDzy)
27. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGe-oasY-mKmO14ggfEoKmaLChXXlP4c1HFml_Tmn_5ph58ShohNd3AD9nVklxO8VQytUUdydSI51ILHI3wnbeMQiIg6ZCgf3N0UtsAoBfspP1Xosj4TE5sh6ckJQ==)
28. [scispace.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe6_FeVs2QmpR33LCdrAbRvb4ROMxCGgSlk5hCSyt6dIyeo1JhXOqP77466AuQ7-5ncdgRBitSyB6V0qc-Lc2I8K3ftBH8Gh5TTFxTOVgMp37oBsBCuq8GP2UtTMCrJVB-X_4t3ChkXyzQsXW0ew_o5vgj4bXx63dAM14aiBxHpAV71AwKT-4GS3C3mD205YKERGf7uPfFyfE=)
29. [thebsps.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkVnzXVJrZoCQ9BWON76t9FVj8t_N5FOpwz2ZDKcwu9eZpM_IAlPqBYqbuSZEQnBsIWQmSvOwg6FuIKhgrrkcm1wGyWVmWbsdednQKQ4OW4c29RWu0aXTH2WbYpnuU33S-Ee4FuZIo-CMMshgDIhwVxWZLHcAb3njnTfeO)
30. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzhj46WOyely3Du1Mizf2BiQ68QCRqMUX8YZxItEHvnUxEx8WCTQqZcCapEn8sQDJR6H_HLnpBbCD3AqUBtlaJskCdYWTrO_O-k-MNCFdWmM6Mxrymw8MsgnHr3ltQ75V2Ld3DY6mxJ93-1-8ZhkUOcNrDvaprSoCeb-9b0nFhK1UQoRmPpmm74nhywmn9kGhxqpkYdCGYFMp_EJRpX5nn_sJec_mYRCgksWQJtA==)
31. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCgifuJOVo-z9Ty74JfkuV8M6mqexgVL6y1Ob87Mk2S4nCj7hhkGODMkQ7HVhb_BUgRYhEOSltnoOIsP53kDou3voqBbxSZO4SrZGCKWr8o7ClPbQo8xV5dUxKnDALqoKoschZBnUi534Z99CE5AH6EBhtCqsyJyq6cIdO2nhJxxXQy1WAG9wW5AsW9IvQYGepMQI9YL-ZpZHS34fe9HD74ktrjzzHjs0StW_Ir4U5mwZIxuLecUhV-5qz4uFtkEGOs4k-)
32. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm81UZCdhIoKUsJa-n-QSDiSK_VXxscgP5BEpzKmS-XASeX3XyZkwZ8ZMlA5_dO8p5dVaih2Dzl_nb8hwYGKldZozCm02z0Axc0UXYu4sr6013is98XHSlr8AoCq5e_1VPzydVq0m00tpnHitt86uQ7r7zm0uiHXmcMvLVgcnXb2X-ttoOF668jV4aLm6vYN4aCecNtMwEFXan48nBPG8EEBpj47NujcZdrzU_v7TM45JoTgk9rUjv)
33. [escholarship.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHbbsFqd40xlydL0DToG9d0pmjv5hSXzUr6OqCfbECElBXF8KCq2vUBqb9c2HIsDuZz1R0qqVBnerEme6C342a_yB39m8t0DLu04NGvvEcO6dfwg26EYMh0ghnD7_8J_YiDpGaZQOMU5vJgUrhpA0=)
34. [spacefoundation.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYDj4kDIidQgsBLQpseOozvm7Y_OA2PBL8Ss59GilSwUAQdSuOMiV4Cf73KisXNN95la6xixmDYcvCS8L7TDaLRHUwLnLdFBFFKsU7pKvNmU-G3fF6HBGapcrCcsZaQ20iSf669JG9029rkoT4P6MzgOmBjjUOd4HefJRUGIYnlP7D4-9NErT4CXzTbnFpW7w0PFadoWK3ACk_ppgDdmf-RtTJgnGId2OOORjx8xPH9eIZyS1DntvEH0JJAB9RgyaqNlZ3xsyWApYeKT-yiPb9_h6xL_bOJ-iB)
35. [comp-ocpm.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFGq1wumvFLnNARdHk0i9TGO3oqv2to-HQh7gmFP6MYUuAfWPzQ1_RjQ0sR-hg_I4g4ZSusxgTC34VpfgP2KjysPbYplzuXXuHZqcoqw-9vYUYT4vhC2lG1Cv3-SkExjM=)
36. [ijettjournal.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjkpOdQc-DUU1bKMboOxNqixcwOpgc7EpuKjh1BCKq35VcP4Oc0PkL8fHf3dX0mmJktvNNP_DauX74zZjFNQ3fbeO2Xr8qOFqM8gMbQHLFiraO7R6bvJe_OdfCuRgceG2WAZ9nwDPm7eJmbrgSUJo_v-OSUUMSe72K3g==)
37. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELkUlbcAhmu-ofE8ZJ3GvEDtVRnJvXHUNRt9cQdL_gX-6hx0g-wmn3xNuIem_dmsTfXDcDfNxTYpBUMdSp4l_RnTwxbwyY-shrmWeAlKqI-7WW_AyVKICO)
38. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOpHNCuWpD30-15zIbM8rF3BeWEbYd_jhtUP0G7dZs5OUzMlkPX6K93cfsmH5498h61MdI15hU6l4M7VldDxftpjT3HkzWbfc7svPL-kJt1b8jh2ZuxnP7D-aBMckqr6YxsjVnDQ==)
39. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6Dff1ye-6uo3AUkRFpCYJpy20Zxz40V_7L0NNawP2Sd_44Rg7B6no4RX7He_GzKFmeNiCy2Gt1ea-XwAEdkRbRnd0zOdljDbjwg3ZPvP8PhoMgYcQkP2Km2Y0X4YrnkmWOZ0LJMiEPOaLrPrKW4MVBi_bBs_pjOiDwWJ0YQstUeR5FTiqxU_yQ2X8Rkf9HpzKQHg6ccay_YY=)
40. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3af4o6D4bJqIcrnRiF1mDSkaGm5XNP3-alewoXbq32VxV1sniOP0TJsbuBNHujLbxCJdSTFV-FVpkFZsHzitJEjDXwpMnWVyt3YtUOoUqeJH8e1b-mqzu4SL1DGUjpRwjgNFEwdigBpSeMmxPx7tBuqDxDDTRFg==)

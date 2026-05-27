# Prompt 15: G17 Causal-Intervention — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chdnb1lXYXZDU0QtcWExTWtQNXBDUTRRdxIXZ29ZV2F2Q1NELXFhMU1rUDVwQ1E0UXc
**Elapsed:** 243s

---

# Advanced Causal Inference at Pearl's Rung 2: Evaluating Label-Shuffle Interventions, Phase Transitions, and Sequential Do-Calculus in the G17 Architecture

**Key Points**
*   **Label-shuffle is a mathematically weak intervention** that primarily tests robustness against noise rather than true structural causality. Pearl's Rung 2 requires precise, surgical $do$-operator manipulations.
*   **The $M=1.26$ threshold represents a critical phase transition.** Advanced methodologies, such as the Supremum Augmented Dickey-Fuller (SADF) test and Phase Equilibrium Degree (PED), can automatically detect such tipping points in causal-effect surfaces.
*   **Chaining interventions is strictly necessary for deep causal discovery.** Real-world systems exhibit sequential dependencies where a secondary intervention $do(B=b \mid do(A=a))$ reveals hidden structures invisible to single-step tests.
*   **The G17 loader operates fundamentally as an instrument validation tool.** By confirming the known Salem moderation effect, it calibrates the apparatus. Its true value lies in subsequent deployment against unknown, latent structures.

**Overview**
The pursuit of causal inference within complex mathematical and algorithmic substrates necessitates rigorous evaluation frameworks grounded in Judea Pearl’s ladder of causation. This report analyzes the G17 `CAUSAL-INTERVENTION` framework, specifically addressing its current reliance on label-shuffle null tests and its transition toward more sophisticated $do$-operator implementations. By examining the phase transition detected at threshold $M=1.26$, we explore the intersection of causal inference and statistical mechanics. 

**Methodological Shift**
Recent advancements from 2024 to 2026 highlight a paradigm shift away from simple randomization toward explicit structural causal models (SCMs). Incorporating methodologies such as Mathematical Causal Graphs (MCG), implicit causal chain discovery, and Combinatorial Causal Bandits (CCB) provides a blueprint for upgrading the G17 loader to version 2. This report details the theoretical justification, concrete specifications, and statistical robustness checks required to elevate G17 into a state-of-the-art causal discovery engine.

---

## 1. Introduction: The Epistemology of Pearl's Rung 2 in the G17 Loader

Judea Pearl’s foundational ladder of causation categorizes reasoning into three hierarchical levels: Association (Rung 1), Intervention (Rung 2), and Counterfactuals (Rung 3) [cite: 1]. The current G17 `CAUSAL-INTERVENTION` loader operates at Rung 2 by applying a label-shuffle intervention to test whether a parent correlation survives. The expected `kill_pattern: correlation_survives_intervention` implies that if the correlation persists despite the perturbation, it is deeply structural rather than a spurious artifact of the data distribution.

The LIVE deployment independently reproduced the ITER-4 Salem moderation finding, demonstrating a high degree of statistical significance (observed=0.997 vs null_p95=0.024) and detecting a phase transition at threshold $M=1.26$. However, while label-shuffling is computationally convenient, it is fundamentally a weak intervention. It disrupts associative links by injecting noise, but it does not formally substitute the structural equations governing the nodes—the defining characteristic of the $do$-operator [cite: 2]. To mature the G17 architecture, we must transition from generic noise-injection methodologies to explicit causal surgeries that align with recent (2024–2026) literature on mathematical-catalog substrates.

## 2. Moving Beyond Label-Shuffle: Advanced Rung 2 Methodologies

Label-shuffling randomized class labels to test the null hypothesis of independence. In the context of Pearl’s framework, a true Rung 2 intervention, denoted as $do(X=x)$, requires severing all incoming causal edges to the target variable $X$ and forcing it to a specific value [cite: 1, 3]. This simulates a randomized controlled manipulation rather than merely degrading the informational integrity of the dataset [cite: 4]. 

A survey of 2024–2026 literature reveals three highly applicable Pearl Rung 2 methodologies specifically suited for mathematical-catalog substrates and algorithmic reasoning tasks:

### 2.1. Mathematical Causal Graphs (MCG) via the CAMA Framework
The CAusal MAthematician (CAMA) framework introduces Mathematical Causal Graphs (MCG), a structural representation that captures the causal dependencies between mathematical theorems and solution strategies [cite: 5, 6]. Instead of randomly shuffling parameters, CAMA applies $do$-interventions to the high-level representation of a problem. In its reasoning stage, CAMA feeds structured causal information back into a Large Language Model (LLM) to guide problem-solving. This methodology operates strictly at Rung 2 by intervening on the sequence of knowledge application (e.g., enforcing the use of a specific theorem) to observe the causal effect on the final reasoning output [cite: 5].

### 2.2. LLM-as-Interventional-Simulator (CIKA Framework)
The Causal Knowledge Activation (CIKA) framework pioneers the use of an LLM as an active $do$-operator simulator [cite: 7]. In mathematical reasoning tasks, confounding variables such as "problem difficulty" naturally distort the observed relationship between knowledge access and problem-solving success. CIKA applies the $do$-calculus backdoor criterion to separate these confounders [cite: 7]. By explicitly applying $do(c_i = 1)$—where $c_i$ represents a mathematical concept—the framework computes the interventional causal effect (Average Treatment Effect) of activating specific knowledge. This is vastly superior to a label-shuffle because it actively manipulates the latent semantic state while preserving the underlying structure [cite: 7].

### 2.3. Combinatorial Causal Bandits (CCB)
In scenarios where the causal graph skeleton is unknown or partially observed, the Combinatorial Causal Bandits (CCB) framework provides a methodology for executing simultaneous $do$-interventions across a subset of variables [cite: 8, 9]. Applied to Binary Generalized Linear Models (BGLMs), CCB algorithms optimize expected regret by strategically intervening on multiple nodes. This methodology is directly applicable to the G17 substrate, as it allows the loader to apply targeted interventions to combinations of substrate parameters rather than globally shuffling labels, thereby identifying the minimal sufficient interventional set required to sever a correlation [cite: 9, 10].

## 3. Automatic Phase-Transition Detection in Intervention Curves

The discovery of a phase transition at $M=1.26$ during the ITER-18 multi-threshold sweep $[1.20, 1.40]$ is a substrate-grade observation. In causal effect surfaces, a phase transition occurs when the intervention threshold crosses a critical critical point, causing a sudden collapse or emergence of causal structural integrity. Recent literature provides rigorous statistical and physical frameworks for the automated detection of these tipping points.

### 3.1. Phase Equilibrium Degree (PED) and Spin-Field Frameworks
Deng et al. (2026) introduced the Phase Equilibrium Degree (PED) within the SpinFlow framework, unifying statistical physics with macroscopic phase inference [cite: 11]. Inspired by the Heisenberg model, PED quantifies the structural alignment of a system and topologically localizes phase-transition points without prior network topology knowledge. In the context of the G17 loader, calculating the PED across the threshold sweep $[1.20, 1.40]$ would allow the system to automatically pinpoint $M=1.26$ as the state where the "model-data equilibrium is most severely broken," effectively detecting the nucleation center of the intervention's failure [cite: 11].

### 3.2. Explosiveness Testing via Supremum Augmented Dickey-Fuller (SADF)
Phase transitions are frequently preceded by critical fluctuations [cite: 12]. Colchero Paetz (2026) demonstrated that the Supremum Augmented Dickey-Fuller (SADF) test, originally used in econometrics to detect explosive market behaviors, is highly effective for detecting physical phase transitions, such as those in Charge Density Waves [cite: 12]. The SADF test identifies a rolling time-series (or in our case, an intervention threshold curve) as "explosive" when the variance grows beyond stationary expectations. Implementing a Generalized SADF (GSADF) on the G17 sweep curve would automatically flag the variance explosion preceding $M=1.26$, serving as a purely data-driven, automated transition detector [cite: 13, 14].

### 3.3. Bivariate Change-Point Detection (MOSUM)
For complex intervention curves, Plomer et al. (2025) proposed bivariate change-point detection using moving sum (MOSUM) statistics [cite: 15, 16]. This methodology jointly evaluates the mean and empirical variance across a sequence, effectively detecting abrupt changes in multi-dimensional states. By monitoring both the survival probability of the correlation and the variance of the permutation tests simultaneously, the MOSUM kernel estimator provides a rigorous statistical test for localizing the $M=1.26$ phase transition threshold [cite: 16, 17].

## 4. Cross-Plugin Intervention Chains and Causal Discovery

The current G17 implementation executes a single-step intervention: applying a perturbation and testing for correlation survival. However, complex substrates involve sequential causal dependencies. A correlation that survives a primary intervention might collapse if a secondary intervention is conditioned upon the first. This requires transitioning to cross-plugin intervention chains.

### 4.1. The Mathematics of Sequential $do$-Calculus
Chaining interventions requires evaluating the conditional interventional distribution $P(Y \mid do(X_1=x_1), do(X_2=x_2 \mid X_1=x_1))$. This represents intervening on node $A$, observing the updated structural equations, and subsequently intervening on node $B$ given the new post-intervention topology. Gumucio and Zhang (2026) address sequential interventions using the $do$-operator, noting that actions taken at one step influence future available actions and feasibility constraints [cite: 18]. 

### 4.2. Implicit Causal Chain Discovery
Allein et al. (2026) formally defined the task of Implicit Causal Chain Discovery [cite: 19]. In complex argumentation and reasoning substrates, intermediate causal mechanisms (e.g., $A \rightarrow B \rightarrow C$) are often latent. Their methodology utilizes LLMs to systematically infer and generate intermediate causal steps connecting a cause-effect pair [cite: 19, 20]. Applying this to G17 v2, the loader would actively search for the mediating variable $B$ between the source $A$ and target $C$. If the $A \rightarrow C$ correlation survives $do(A)$, the loader chains the intervention: $do(B \mid do(A))$. If the correlation then collapses, $B$ is identified as the critical structural mediator. Furthermore, Chen et al. (2025) demonstrate that simulating causal effects through sequential $do$-interventions allows for dynamic counterfactual reasoning, directly evaluating the likelihood of an outcome across the full sequence of actions [cite: 21].

## 5. G17 v2 Loader Design Specification

Based on the theoretical frameworks above, the G17 v2 loader must be re-architected. The concrete specification integrates true structural interventions, thermodynamic phase-transition detection, domain transfer, and chained causal tracking.

### (a) Do-Operator Intervention Beyond Label Shuffle
**Mechanism:** Replace `g17_lehmer_label_shuffle` with `g17_structural_dropout_do_operator`.
**Implementation:** Instead of randomizing the class labels, the intervention must perform a graph-surgery operation. For instance, to test the Salem moderation effect, the loader will explicitly sever the incoming edges to the Salem-class flag.
*   **Action:** Dropout the Salem-class flag from the prediction pipeline entirely, or fix it to a constant value $do(Salem\_Flag = 0)$ for all nodes, overriding the natural distribution [cite: 2, 3].
*   **Evaluation:** Recalculate the downstream correlation. If the correlation survives, the relationship does not causally depend on the Salem class.

### (b) Automatic Phase-Transition Detection in Sweep
**Mechanism:** Integrate a GSADF / MOSUM rolling-window monitor.
**Implementation:** During the multi-threshold sweep $[1.20, 1.40]$ with step resolution $\Delta M = 0.01$:
*   Compute the first derivative of the causal effect surface and the local variance (fluctuations) of the survival metric.
*   Apply the GSADF test [cite: 13, 14]. If the test statistic exceeds the critical threshold, flag the region as a phase transition.
*   Calculate the Phase Equilibrium Degree (PED) continuously. The specific point where $PED(M)$ exhibits the maximum drop from the stable-zone baseline is automatically recorded as the exact transition threshold (e.g., $M=1.26$) [cite: 11].

### (c) Cross-Domain Intervention Transfer
**Mechanism:** Transportability of causal interventions.
**Implementation:** A causal structure validated in one domain should ideally exhibit transportability. The v2 loader will take the causal mechanism validated in the original substrate and apply it to a cross-domain target, such as a BSD-context (Berkeley Software Distribution) label-shuffle on a rank-class binary.
*   If the exact same threshold ($M=1.26$) triggers a phase transition in the BSD-context, it proves universal scale-invariance of the causal mechanism across domains.

### (d) New Kill Pattern: `intervention_chain_collapses_at_step_N`
**Mechanism:** Sequential tracking of structural integrity.
**Implementation:** 
1.  Apply $do(A)$. Check survival. If `True`, proceed.
2.  Apply $do(B \mid do(A))$. Check survival. If `True`, proceed.
3.  Apply $do(C \mid do(A, B))$. Check survival. If `False`, log pattern.
*   **Output:** The loader emits the kill pattern `intervention_chain_collapses_at_step_3`, proving that the causal structure is highly resilient but relies on a tripartite dependency graph. This directly maps to Combinatorial Causal Bandits logic, revealing the exact subset size $K$ required to shatter the underlying graph [cite: 8, 9].

## 6. Statistical Robustness of the $M=1.26$ Phase Transition

The original ITER-18 finding utilized $200$ permutations per sweep point. While sufficient for exploratory signal detection, 200 permutations lack the statistical power to definitively characterize the thermodynamic properties of a phase transition, leading to potential Type I errors (false positive transitions) due to high variance at the tipping point. 

### Proposed Robustness Check
To validate the $M=1.26$ transition as a substrate-grade physical reality rather than a statistical artifact, we propose a high-resolution refit:
*   **Domain:** Narrow the sweep to $[1.235, 1.285]$ (a neighborhood around 1.26).
*   **Resolution:** Increase step size to $\Delta M = 0.005$.
*   **Permutations:** Execute the canonical $1000$ permutations per point.

### The Null Hypothesis ($H_0$)
In the context of phase-transition detection via intervention curves, the robustness check tests a specific null hypothesis regarding the continuity and variance of the system:
*   **$H_0$:** The survival correlation metric $S(M)$ is a smooth, continuous function with respect to $M$, and its first derivative $\frac{dS}{dM}$ does not contain any discontinuities. Furthermore, the variance of the permutation tests $\sigma^2(M)$ is homoscedastic (constant) across the interval $[1.235, 1.285]$.
*   **Alternative Hypothesis ($H_1$):** A genuine phase transition exists. If it is a first-order transition, $\frac{dS}{dM}$ will exhibit a sharp discontinuity at $M=1.26$. If it is a second-order continuous phase transition, $S(M)$ is continuous, but the variance $\sigma^2(M)$ will exhibit a dramatic divergence (critical explosiveness) exactly at $T_c = 1.26$ [cite: 12]. 
By running 1000 permutations, the estimation of $\sigma^2(M)$ becomes highly precise, allowing a GSADF explosiveness test to definitively reject $H_0$ if critical fluctuations are genuinely present at $M=1.26$ [cite: 14].

## 7. Contrarian View: G17 as Instrument Validation vs. Novel Discovery

A rigorous steelman of the contrarian critique asserts that G17 is essentially performing **Instrument Validation**. Because the Salem moderation effect was theoretically and empirically known prior to the LIVE run, detecting it at $M=1.26$ does not constitute a novel discovery of underlying nature. 

**The Steelman Argument:**
In high-energy physics or complex network analysis, a new detector is never first pointed at the unknown. It is first pointed at a known standard candle. By successfully reproducing the Salem moderation finding (observed=0.997 vs null_p95=0.024), G17 proved that its statistical plumbing, permutation limits, and phase-transition detection arrays are properly calibrated. It established the baseline sensitivity and specificity of the `kill_pattern` framework. Therefore, the value of ITER-18 is not the discovery of the Salem effect, but the empirical proof that the G17 loader is a functional, unbiased epistemological instrument capable of isolating structural causality from correlative noise.

### Proposing 3 Tests for Novel Structure Discovery
Having validated the instrument, G17 v2 must be deployed against unexplored algorithmic topologies where the ground truth is entirely unknown. 

**1. Latent Algorithmic Alignment Pathways in Mathematical Substrates**
Using the CAMA framework's Mathematical Causal Graphs (MCG) [cite: 5], G17 will test whether LLMs inherently map distinct mathematical domains (e.g., Algebra vs. Geometry) to a shared latent causal manifold. 
*   **Test:** Intervene on the geometric syntax of a problem (e.g., transforming a spatial topology problem into a pure algebraic graph problem) using the $do$-operator. 
*   **Expected Novelty:** If the semantic solution capability survives this syntactic $do$-intervention, G17 will discover a novel, domain-agnostic causal reasoning backbone inside the model's weights.

**2. Cross-Substrate Interventional Transferability (The Semantic Payload Test)**
While current observations assume that causal mechanisms are heavily tied to their training distributions, G17 can test the limits of out-of-distribution causal robustness.
*   **Test:** Extract a complex causal chain validated in code-generation tasks (e.g., object-oriented inheritance dependencies). Apply a cross-domain intervention by projecting this exact causal graph onto a natural language logic puzzle. 
*   **Expected Novelty:** Detecting a `correlation_survives_intervention` across entirely disjoint substrates would prove the existence of universal, substrate-independent causal representations in AI models.

**3. Emergent Capability Tipping Points (Critical Threshold Discovery)**
LLM scaling laws suggest that capabilities "emerge" at certain parameter scales. G17 can investigate whether these are smooth continuous functions or genuine phase transitions.
*   **Test:** Apply a sequential intervention chain (as defined in v2) to the model's internal attention heads, sequentially masking (using $do(Head_i = 0)$) heads known to handle long-term context. Use the automated MOSUM and PED transition detection over the depth of the intervention.
*   **Expected Novelty:** Instead of a gradual degradation, G17 may discover a strict thermodynamic phase transition where reasoning completely collapses at exactly `intervention_chain_collapses_at_step_N`. This would prove that "emergent" reasoning is physically analogous to a percolation threshold, fundamentally rewriting our understanding of neural network mechanics.

## Conclusion

The current G17 loader successfully executed its primary mandate: acting as a standard candle to validate Pearl Rung 2 testing within algorithmic substrates. By recognizing the limitations of the label-shuffle and embracing the explicit $do$-calculus of structural SCMs, Mathematical Causal Graphs, and Combinatorial Causal Bandits, the v2 architecture will transition from validation to true discovery. The rigorous automation of phase-transition detection at critical thresholds like $M=1.26$, paired with sequential intervention chaining, provides a mathematically sound, highly advanced framework for mapping the hidden causal topologies of complex models.

**Sources:**
1. [pymc-marketing.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlnEY3AMcd8330Ds_S9P9EaVO1iB3Vojsa10qq4iefMnB4MfPP568J36vMvS16YU2jP2119UCBDl7kUny8DtINjl172__Smf3RabKIhrhpaMk_aQN8ztIHaf71aTu5To1vrxXrIupKksjrAzLQx9rDZChqwd3Nc2FaZf8S8i-PgJjt_Q==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFggoKH-ZdVCxdCJNYoORGsYHh8HDT5lC0Y6pGnvM1o_ZVdL1TwiTWpI6uw0Pu0evIo6EY7nlwj99W8xXtUaLtLX1TWZaK9VLFkODq7VaZcbSzcccSz6Zbe)
3. [shadecoder.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEiMXT3HzaxMN_yuc3OVlMOS4mXQ06cpBQsVgp6eHG0Yg0bKed70Kkw-P26a64AQIjTdBpAAkupIe9stKiHLu8_96ds_KXjg_9G8mTSyzSe16ClPhpVzfqtCOsic-7BSCa9sesBDnSYCuTSpLXqKiLPEnqEgEkURjHf6GtcySjd2NQ=)
4. [shadecoder.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-tuZtwskgmYrv7psEvccWiNY0cEIQlDPbe-pD0h35dcIeYB4IRZt95r9m0D7TkS6WZznOGK9KygyZKZRqm6dLSjh0G_QVG0KOvcohliXCPQZhvk0bBf-P2Z3nr6YU592Yb7nCc7ppCaa5tRv2vmSnNDrda8gJ92p4uCdkRgPm8RzbMBbrHO-uCZrcwmNfpA==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAPDux9RJxggt4y7I_0uE6ObidpIRWXH9DRn5na5w44Q8IibXuAqzlBH6hdzKHai8DtIbMKqnGbksRJvijakOzeZV32rWmox4nhDWKmj89rEaNQn3Gcw2V)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoDXavu4c1wOE0uabuw_JFU76hXqjBYBpKLijCxKJ8iZFRF9y7QMQcnQ9eShaUiA6UMwjECqjPrJnmf0_xA9A_lHx5Q1tWVp-oxuC-Bl2TcPxio0Q7)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXIY06GxzMcYkm_dxglu6_d0IvQTv2AcSlv1GXde9CsGl9b8zrJt1xgWBtJ2Ud02UVRGU5BYIRpKzt40vCMujp1jtKE9UK9l9AQimmPsLup8tpqgT9O7G0)
8. [githubusercontent.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDrcH0Q4UMwYfpWs8OpddVmMeoPfZfvnSt438ryIEWZbjwY9YGAzHFZ9rc046l5I6EBLfXGACIzMDyHj6gwWpyK08fwTjVZ1alf3ayS8a8Yf0LH0McVj3AoB3GrTJ5pI9CiZkkkmmBXYVIxrrQuwIlVhjvEEujHNUCGuHdNKSFVYQzhkVhgA==)
9. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwb0Fheo0yX4zxplqvktGZcASSxM9lEcl2UHbcaSIKTlsdo0KPUMis_4iGoTpt6KPeDgtsNfCPdbQIMdmGQ_FgkdFyY8Gw7j0-ZiL4aeI9-YV0-5QfvV9rdRCc2rD6Ts1qZhfi)
10. [aaai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIgehVgMN11sfrQ4TADMTDNKUGPYFsEf4KUxkVrW5cjNpxKkHk-FBNspePOoRG-SSXtT-dsOkVrMY5w_zHNl0o_UziC8wfCmrc_nIpgPD6hBGGC9niQXJ-cGCBeBdRaiCyKAOX_t1K7D1ZK5IfluYDSg==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4-hSdzoJb2RUzXGbmMzPF8aFKgjd5Dr5yM3pMAcjHSggYDNXB8-Rf9xyCDV915RECSkDE5Nmz63gGERBz_0O2uKdE_YAJd8nwkcAZ24tqus5e3dkTdqNw)
12. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmJ0CMGiXfze6QHQbyhOx7yLJXoLQfgsHcq7bW5fbDQB37YVu8w9i0rZdryk3-GLr2-9OpbWhlbp4t_HvZ1I01zQ84fjP0Bvft63yPVBaVqzolBryeBPadXqJEtmSs)
13. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuydlEFzIu1cKRCOQ0gWKnXy2Gv72Qy3fo0w-Ma95hWklYAAJRnXeKkjJ7OCmkrGcLWq2S1iAqGy9ZYHyGYuSPabetyGaCLERZl09DN3PCvCWnwbkuvlZuk9Xe8g==)
14. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOxaX7iuvOK-gbcZizXWX5-mQguES8KbQbgJ_MhDwrn6FJEEhk58Dxqxmoi2aVz6F4AaVU69vLwyLSUSl5mBrDrFj1IquI6aapIVOPSra6XEjNCXdy6JpwAzc1m2WKbiDNPQznhg==)
15. [uni-frankfurt.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYVnRQlP7ldYC6fFcl3stzfH9rL3TC77CVqT76z-jtDYliFFMA41KREM8u31WYbAG2btAoAlKYnLKwtiAbbSPYodHUoPCiz24zB9KyZ7Urv1ihohF1Z1GNFCoTxYttBT8emQEdsNHkzdqND5XljpFgbnHJHCOncSWEYl-fPJa0Nfpn9pB0iM0kCNi-RN-S)
16. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrqWcdPgkJj9_fTGbSn-B9q3DQNazBBGbj8KtKC-micPDnVDLdKDzDULZndvJj-LYNb3gtOKyuS7eZdOfhoNt3NSfS0fRTkiwAIGp-f3j86qdkbI-5BnSZ53zccl2pTHgx5kmt9qxfcPHDtKwd4Imm_QTGe_xCe9LvtKDiyFawuctfj0nzc8vprtp7qJEgFi7BPpYF3Eq-GNylq80GJHJzWYd9VXSYVR_FusUy1GPkvE8RPQv91bk2ixF1Hdl4DwdAA1LP_5W3m8h_VxQe3hZWqT0FxO1RHXkx8gtJ0fO566JZ3tE=)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEa0JonPxjUpdCQH0TNAkXpcHSxPlBTIYNIv5fN2MGOA2B9uPh3zpVv69_S9pLszAA_HUcZHyffyDeTIG4Fxz4JuYPyHSL7UvFOBTpX0eYjL3-p3g0ikwFYK71xkh-9a7nuhoSMFxaEVshUPMK1BoXb6ypD7Rm83PjZQqe1q31VWqSVIsq1kYl6g_rDVMbqZYdwDjxk6kh3UZB4vlKKKR5SZpw59r-fKG8=)
18. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExETIgaaPDAZm8nPl66Xaa1mJzZ5XFFDEdGx7nBKBah2_93sFZKrIAduXfYlDIAH7UUY3_aEjl3W1CqFH9fQbDdqQzt_1jkrXw8GKzRMWVhPM8W_b60dv4tqo8UdyI6dkf_7bqhDjAprx3Wai1iI_GGv1cFqWkNWvoRmfIlS6_VsZT2k81sspEHrY=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFE006RzMvoLtkIKnbrgZBVKUIcfAUQLraFfdRtxp2Hdy2VXs58pR-aEbK-vGqapUCKgVGVd3MU6UzRhpwtYEauCYgGvAsDMBDCtzkjIDJBvrj8Tx_B2B1)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqP591XPKC0rDesfkdQMoJHCrTfc3zlVZb0HD1cTy5iJxuQkIw7qQarJnchJjNNlkVW42uj5emmq19-eTyJBihAKvZjKuvJjob2ItumKRFkJb5tAoU)
21. [phmsociety.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbbypQ3pRtvnA16upVjMr0fNRVeyj7YWSk2bFr4xRbTGJfA9AKJr2gqmJ_vfVAbPvvlmgNSL950jcKBEq9FuFzFm2_uxc32V23jV6X8kk9jH2jr_SSYvIQni0qg-fdGI7QIPmjIrHbbaq9e5EZiIYNp47WxpjOKnXE73N7_ElkzlzVLZyXyw8=)


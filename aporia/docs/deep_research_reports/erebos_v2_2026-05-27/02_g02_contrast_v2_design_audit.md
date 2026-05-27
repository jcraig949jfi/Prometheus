# Prompt 02: G02 Contrast — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chdnb0VXYXF6T0xxSFJqTWNQdEtQT3FBMBIXZ29FV2Fxek9McUhSak1jUHRLUE9xQTA
**Elapsed:** 304s

---

# G02 CONTRAST: Upgrading Empirical Falsification Design from V1 to V2

**Key Points:**
*   **Permutation Vulnerability:** The current V1 loader's reliance on naive, single-step label shuffling risks massive Type I error inflation due to structural confounding in mathematical catalogs. Advanced alternatives like Westfall-Young max-T, conditional, and stratified permutations are required to isolate genuine algebraic signals from domain-specific noise.
*   **Threshold Selection:** Static thresholding (e.g., arbitrarily testing at $M=1.30$ vs $M\_LEHMER$) masks continuous moderate-deviation phenomena. The adoption of Bayes-optimal thresholding operating on the $\sqrt{\log n / n}$ scale provides a mathematically rigorous, adaptive framework for threshold sweeps.
*   **Multiple Comparisons:** Selecting the maximum divergence across multiple structural binaries (Salem, Smyth, Degree Parity) without correction guarantees false discoveries. Benjamini-Hochberg False Discovery Rate (FDR) control and conformal selective inference provide modern, robust solutions.
*   **Arithmetic Limits:** Non-parametric permutation tests inherently assume exchangeability, an assumption that collapses in highly deterministic domains like elliptic curves, modular forms, and $L$-functions. In such domains, structural probability models (e.g., random matrix theory or Cohen-Lenstra heuristics) must replace the permutation null.

**Executive Summary:**
When analyzing mathematical catalogs (such as polynomials evaluated for Lehmer's conjecture), statistical methods are deployed to detect structural anomalies. The V1 `G02 CONTRAST` loader currently identifies differences between two groups (e.g., Salem vs. non-Salem polynomials) by checking if their survival rates diverge beyond what one would expect if the labels were simply shuffled (the permutation null). However, this naive approach fails when we test multiple thresholds, compare multiple overlapping groupings, or when the mathematical objects contain hidden confounding layers (like polynomial degree). By integrating methodologies published between 2024 and 2026, we can specify a highly rigorous V2 architecture. This upgraded design utilizes Max-T step-down permutations, False Discovery Rate (FDR) corrections, and Bayes-optimal thresholding to ensure that a "promoted" signal is a genuine mathematical property rather than an artifact of algorithmic multiple-peeking. 

---

## 1. Permutation Null Alternatives

The V1 architecture utilizes a single-step, unconditional random shuffle of binary labels to establish a null hypothesis (`permutation_null`). While computationally inexpensive and valid for strictly independent, unconfounded randomized controlled trials, this approach is fundamentally compromised in observational or deterministic mathematical databases. In mathematical catalogs, features are highly correlated, and latent structures (e.g., the degree of the polynomial, the trace, or the Galois group) act as severe confounders. 

To resolve this, the V2 loader must implement modern permutation algorithms. Based on literature from 2024 to 2026, the following three advanced permutation methodologies address critical failure modes that the V1 loader currently misses.

### (a) Westfall-Young Max-T Permutation
The Westfall-Young step-down permutation procedure (also known as the Max-T method) constructs a joint null distribution for multiple hypothesis tests simultaneously. In this framework, in each permutation step $b$, the algorithm computes the maximum test statistic across all tested variables (or all thresholds): $T_{max}^{(b)} = \max_{k} T_k^{(b)}$. The observed statistics are then compared against the empirical distribution of these maxima. 

**Failure Mode Caught:** *Family-Wise Error Rate (FWER) Inflation across correlated variables.*
The naive single-step shuffle tests each hypothesis (or threshold) independently, failing to account for the overlapping feature space in number-theoretic catalogs. For example, if we test multiple correlated structural flags (e.g., Salem status, reciprocal status, and trace parity), the naive test will yield false discoveries simply by taking the maximum of correlated variables. Westfall-Young strictly controls the FWER under complex dependence structures [cite: 1]. Recent literature demonstrates its superiority in generating robust, exact significance assessments in highly correlated, high-dimensional spaces without relying on flawed asymptotic assumptions [cite: 2]. Furthermore, in 2026, Westfall-Young permutations combined with kernel density estimations were successfully deployed to disentangle deeply masked structural similarities (density support intersections) in high-dimensional datasets [cite: 3].

### (b) Conditional Permutation (Berrett et al. / Niu / Lai & Guan)
Instead of uniformly assigning labels across the entire dataset, a Conditional Permutation Test isolates the specific effect of a feature $X$ on an outcome $Y$ by conditioning on a set of known confounders $Z$. Building upon the foundational work by Berrett et al., recent 2024-2025 advancements—such as the Multivariate Sufficient Statistic Conditional Randomization Test (MS-CRT) [cite: 4] and Inverse Conditional Permutations (ICP) [cite: 5]—allow practitioners to draw exchangeable copies of $X$ from the estimated conditional distribution $\mathbb{P}(X|Z)$. 

**Failure Mode Caught:** *Latent Structural Confounding.*
In the Mahler measure context, suppose Salem numbers are disproportionately prevalent among low-degree polynomials. If the naive V1 loader blindly shuffles the "Salem" label, it will mix high-degree non-Salem polynomials with low-degree Salem polynomials. The resulting divergence will highlight a "degree effect," falsely reporting it as a "Salem effect." Conditional permutation corrects this by strictly permuting the Salem label *only among polynomials of the same degree* (or by weighting the permutation probabilistically based on $\mathbb{P}(\text{Salem}|\text{Degree})$). It detects when an observed effect is merely a proxy for an underlying nuisance variable.

### (c) Hierarchical / Stratified Permutation
A stratified permutation test partitions the dataset into fixed, disjoint strata (bins) based on categorical or clustered metadata. Permutations are then restricted to occur strictly *within* each stratum, ensuring that the margins of the stratifying variable remain perfectly fixed across all pseudo-random iterations. Recent literature from 2024 to 2026 showcases the critical necessity of this method in structured graph networks and spatiotemporal data. For instance, French et al. (2024) developed a stratified permutation test to eliminate the need to model complex cross-correlations by assuming exchangeability only within defined clusters [cite: 6]. Similarly, Queme et al. (2026) proved that uniform permutation on biological networks is inherently miscalibrated for hub-enriched sets, whereas degree-stratified permutation restores nominal false positive control [cite: 7, 8].

**Failure Mode Caught:** *Simpson’s Paradox and Hub-Bias.*
If the dataset consists of nested topological families (e.g., cyclotomic polynomials vs. non-cyclotomic, or differing Galois architectures), an aggregate simple shuffle will wash out subgroup-specific variances. If Salem numbers are heavily represented in a specific "hub" of the mathematical catalog, a non-stratified permutation will overestimate the significance of the Salem flag. Stratified permutation tests catch the failure mode where a global signal contradicts or exaggerates local, within-class noise levels.

---

## 2. The Threshold-Choice Problem

In V1, the threshold is treated as a static hyperparameter. The `LIVE FINDING` indicates that the statistical divergence between Salem and non-Salem polynomials is entirely invisible at the extreme Lehmer bound ($M_{LEHMER}$) but overwhelmingly dominant at a relaxed bound ($M=1.30$). This represents a classic statistical pathology: selecting a single, arbitrary threshold risks Type II errors (missing true discoveries at $M=1.30$) or Type I errors (chasing noise at $M_{LEHMER}$). 

### Principled Methodology: Calibrated Threshold Sweeps via Stability Selection
To maximize discriminating power without overfitting to a single arbitrary cut-off, we must move to a **calibrated threshold sweep**. Rather than selecting a single cut-off, the methodology evaluates the test statistic continuously across a sequence of thresholds $M \in [1.176, 1.40]$. However, taking the maximum divergence across this sweep constitutes multiple testing. We resolve this by embedding the threshold sweep within a stability selection framework or the Westfall-Young Max-T permutation procedure described above. The optimal threshold is explicitly calculated as the one that maximizes the permuted-adjusted divergence. As Gupta et al. (2025) note in multi-omics frameworks, algorithmic robustness over multiple thresholds relies on stability selection, protecting against spurious correlations through rigorous bootstrapping and falsification modeling [cite: 9].

### A Bayes-Optimal Threshold Criterion
While frequentist adjustments control error rates, Bayesian decision theory provides an exact mathematical criterion for *optimal* threshold selection. In classical hypothesis testing, critical values (like $p=0.05$) remain constant regardless of sample size, which leads to the Lindley paradox (where large datasets detect trivial, meaningless effects as "highly significant"). 

In early 2026, Datta, Polson, Sokolov, and Zantedeschi [cite: 10] solved the precise asymptotics for Bayes-optimal sparse testing. They established that a threshold $\tau$ minimizing the average probability of error (balancing Type I and Type II errors) does *not* exist on the Central Limit Theorem scale $\mathcal{O}(1)$, nor on the severe Bonferroni scale $\mathcal{O}(\log p)$. Instead, the **Bayes-optimal threshold operates on the moderate deviation scale of $\sqrt{\log n/n}$** [cite: 11]. 

Specifically, under symmetric 0-1 loss and a regular prior, the exact critical threshold constant $t_{crit}$ is defined as:
\[ t_{crit} = \sqrt{\log(\pi n / 2)} \]
[cite: 10]. 

By adopting this Bayes-optimal criterion, the V2 loader can calculate the local density of polynomials around any $M$ (acting as $n$, the effective sample size at that slice). We can dynamically assign a significance threshold that formally optimizes the Bayes risk. Furthermore, training paradigms such as the Bayes Optimal Learning Threshold (BOLT) loss, introduced by Naeini et al. (2025), demonstrate how setting thresholds mapped to the $f$-divergence can align empirical testing natively with the Bayes error rate [cite: 12]. 

---

## 3. Multiple-Comparisons Discipline

The current V1 implementation runs `G02` across three separate binary classifications (`salem`, `smyth`, `deg_parity`) and natively "reports the strongest result." This is a severe methodological trap. By picking the maximum divergence of three tests without penalty, the stochastic distribution of the maximum is shifted drastically to the right compared to a single test. The reported $p$-value is artificially deflated, guaranteeing a flood of false positives as the number of binary flags grows.

### The Right Correction: False Discovery Rate (FDR)
The naive choice (no correction) is mathematically invalid. On the other end of the spectrum, the Bonferroni correction (or FWER control) is overly draconian. Bonferroni forces the $\alpha$-level to $\alpha / k$. In mathematical discovery, where signals are often highly correlated and faint, FWER control destroys statistical power, forcing researchers to discard genuine, reproducible signals. 

The correct disciplinary standard is the **False Discovery Rate (FDR)**, specifically the Benjamini-Hochberg (BH) procedure, or modern conformal selective inference methods. FDR controls the *expected proportion of false rejections among all rejected hypotheses*, rather than the probability of making even one mistake. 

**Arguments Against the Naive Choice and Bonferroni:**
1.  **Naive Choice:** Ignoring multiple testing ensures that as we probe hundreds of mathematical classes, our chance of finding a $p < 0.05$ result approaches 100%. "A large part of science may be false" without it, which is exactly why the 2024 Rousseeuw Prize for Statistics was awarded to Benjamini and Hochberg for the FDR framework [cite: 13].
2.  **Bonferroni (FWER):** FWER assumes that every binary test is completely independent. In mathematical catalogs, `salem` and `smyth` classifications have significant geometric overlap. Applying Bonferroni penalizes the researcher for testing correlated hypotheses, crashing the test's power to zero. As Temple et al. (2025) note in their analysis of selection scans, while FWER is strictly conservative, consensus scientific discovery often requires less stringent FDR limits because strict FWER eliminates overlapping, multi-locus correlated signals entirely [cite: 14]. 

**Recent 2024-2026 Literature Justification:**
*   **Jin (2024/2025)** introduced *Weighted Conformal Selection* for biomedical discovery, proving that standard independent p-value combination fails under covariate shift. By utilizing positive dependence among overlapping queries, finite-sample FDR control calibrates individual selection thresholds without the catastrophic power loss of FWER methods [cite: 15].
*   **Gupta et al. (2025)** demonstrated that while simple t-tests flag thousands of artifacts, employing stability selection combined with rigorous FDR control protects against spurious feature correlations while maintaining enough power to build predictive models on multi-omics data [cite: 9].

The V2 loader must implement the Benjamini-Hochberg procedure, transforming raw empirical p-values into $q$-values (FDR-adjusted p-values), promoting only those binaries where $q < 0.05$.

---

## 4. V2 Loader Design

To formalize the `G02` V2 specification, the updated architecture must move from isolated, static queries to a joint, dynamic statistical manifold. 

### (a) Calibrated Threshold Sweep + Max-T Null
The V2 kernel `run_continuous_sweep_maxt` will compute the survival fractions $S$ across an array of bounds (e.g., $M \in [1.1, 1.4]$ in steps of $0.01$). For a given binary flag, in each permutation iteration $b \in [1, B]$:
1.  Shuffle the target labels.
2.  Compute the divergence test statistic $D_m^{(b)}$ at every threshold $m$.
3.  Store the maximum statistic across the sweep: $T_{max}^{(b)} = \max_{m} D_m^{(b)}$.

The global p-value for the flag is calculated as the proportion of $T_{max}^{(b)}$ that exceed the *maximum observed divergence* across the sweep. This entirely eliminates the threshold-search penalty.

### (b) Multi-Binary-Aware FDR
Once the global, threshold-optimized p-values are obtained for `salem`, `smyth`, `deg_parity`, etc., the loader pushes these $p$-values through a Benjamini-Hochberg FDR filter. 
1.  Sort the $K$ p-values: $p_{(1)} \leq p_{(2)} \leq \dots \leq p_{(K)}$.
2.  Find the largest index $i$ such that $p_{(i)} \leq \frac{i}{K} \alpha$.
3.  All flags with $p$-values $\leq p_{(i)}$ are marked as significant.

### (c) Effect-Size Reporting
A significant $p$-value only indicates that the null hypothesis is unlikely; it says nothing about the *magnitude* of the mathematical phenomenon. Given large catalog sizes (e.g., $N=10^6$ polynomials), tiny, irrelevant divergences will trigger $p < 0.05$. V2 must emit standardized effect sizes.
*   **Cohen's $h$:** Because we are comparing *survival fractions* (proportions $p_1$ and $p_2$), the mathematically correct metric is Cohen's $h$, which applies an arcsine transformation to stabilize variance:
    \[ h = 2 \arcsin(\sqrt{p_1}) - 2 \arcsin(\sqrt{p_2}) \]
*   **Hedges' $g$:** If we examine the continuous Mahler measure distributions between two classes, Hedges' $g$ (a bias-corrected Cohen's $d$ for unequal sample sizes) should be reported to quantify the shift in distribution means.

### New Kill Patterns in V2
The transition to V2 allows for highly granular, descriptive rejection states that V1 cannot perceive:
1.  `REJECTED: fwer_max_t_null`: The effect was only significant because V1 cherry-picked a threshold. Under a Max-T threshold sweep, the divergence is consistent with a random walk across multiple thresholds.
2.  `REJECTED: fdr_multiple_comparisons`: The flag showed nominal significance ($p=0.03$), but was rejected because it failed the FDR threshold when tested alongside 50 other structural flags.
3.  `REJECTED: trivial_effect_size`: The flag passed all statistical significance tests ($p < 10^{-5}$) because the catalog size is massive, but was killed because Cohen's $h < 0.10$ (the absolute difference in survival fraction is mathematically uninteresting).

---

## 5. When is a Binary the Wrong Abstraction?

`G02` currently relies entirely on binary splits. However, mathematical structures frequently exist on continuous or countably infinite gradients. Discretizing a continuous variable into a binary flag (e.g., setting a hard cut-off like "Trace > 10" vs "Trace $\leq$ 10") discards massive amounts of Fisher information, vastly reducing the power of the test and introducing arbitrary boundary effects. 

Here are three specific cases where the correct test is a continuous covariate (utilizing regressions, correlations, or gradient-based permutations) and what the binary design misses:

1.  **Mahler Measure vs. Maximum Root Modulus (Root Isolation):**
    If we are testing how the proximity of the largest root to the unit circle dictates survival against Lehmer's bound, the modulus $\rho = |\alpha_{max}|$ is a continuous real number. A binary split ("$\rho > 1.5$") misses the functional form of the decay. A continuous regression (e.g., survival probability modeled via logistic regression on $\rho$) will capture whether the boundary behavior is linear, exponential, or asymptotic, which is vital for formulating precise mathematical conjectures.
2.  **Galois Group Density / Orbit Lengths:**
    For a polynomial of degree $d$, the size of its Galois group $|G|$ can range from $d$ (cyclic) to $d!$ (symmetric). This is a scale spanning vast orders of magnitude. A binary split ("Symmetric vs. Non-Symmetric") entirely collapses the intermediate structures (e.g., alternating groups, dihedral groups). A continuous log-linear regression against $\log(|G|)$ will reveal if the survival fraction scales proportionally with the entropy of the root permutations. The binary design completely misses the spectrum of intermediate algebraic symmetries.
3.  **Coefficient Sparsity ($L_1$ Norm or Height):**
    The study of sparse vs. dense polynomials is governed by the continuous distribution of coefficient heights (e.g., $\sum |c_i|$). A binary test for "sparse" vs "dense" requires an arbitrary, human-selected threshold. By testing the continuous covariate (e.g., calculating the Pearson or distance correlation between the $L_1$ norm and the test statistic), the test absorbs the entire distribution. The binary design risks missing a smooth gradient effect, where every incremental increase in sparsity linearly increases the probability of hitting Lehmer's bound.

---

## 6. Contrarian: A Substrate Where Permutation Null is Wrong

While permutation tests are standard in empirical data science (e.g., biostatistics, clinical trials), they are profoundly flawed when applied to deep **arithmetic geometry**, such as the study of **Elliptic Curves, Modular Forms, and the Birch and Swinnerton-Dyer (BSD) Conjecture**.

### Why the Permutation Null is the Wrong Inferential Framework
The fundamental assumption of a permutation test is **exchangeability under the null hypothesis**. This implies that, if there is no "treatment effect," any label could have been assigned to any object with equal probability. In biology, shuffling a "drug vs placebo" label makes sense because the assignment was randomized. 

In deterministic mathematics, exchangeability is an illusion. Consider testing the parity of the analytic rank of elliptic curves against their Root Number ($W \in \{+1, -1\}$) from their $L$-functions. By the functional equation of the $L$-function, if $W = +1$, the analytic rank *must* be even; if $W = -1$, the analytic rank *must* be odd. 

If a `G02` loader were to shuffle the Root Number labels across a database of elliptic curves (like the LMFDB) to create a "permutation null," it would be creating mathematically impossible objects (e.g., an elliptic curve with a root number of $+1$ but an odd analytic rank). The permutation null generates a universe that violently contradicts the fundamental theorems of arithmetic. Comparing observed data to mathematically prohibited noise yields no valid epistemological insights. The null space is not "random noise"; it is algebraically invalid.

### The Replacement: Arithmetic Heuristic Nulls (Structural Random Models)
In domains governed by deep algebraic symmetries, non-parametric shuffling must be replaced by **parametric, structurally-aware probabilistic heuristics**. 
*   **Cohen-Lenstra Heuristics:** When studying the structure of class groups of quadratic fields, one does not shuffle class numbers. Instead, one models the null hypothesis by assuming class groups behave like random finite abelian groups weighted inversely by the size of their automorphism groups ($\frac{1}{|\text{Aut}(G)|}$). 
*   **Random Matrix Theory (GUE / p-adic groups):** In the context of modular forms and BSD, the spacing of the zeros of $L$-functions on the critical line is strictly modeled by the eigenvalues of large random matrices from the Gaussian Unitary Ensemble (GUE). 

To falsify a conjecture in these domains, the statistical test must not ask: *"Is this divergence larger than if I randomly swapped labels?"* Instead, it must ask: *"Is this divergence larger than what is predicted by the Haar measure on the corresponding p-adic matrix group?"* The inferential framework shifts from non-parametric exchangeability to algebraic measure theory.

**Sources:**
1. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyQJbOGnBhBrmPQVHSNrmzIfXnqLNCoJjLmakeFDq2_7IZqW-MTVH7-zmVsls7lUnOu7yGnMxDPHlKTNSLOzvBk2d6KAaOOYicCSrim4wkSjCrb-J_6ALfynD3mUmoZY-z0o_nOsGEjQN6blLmH-Lwrx-d0Tp6Duzk1hovbnGaLZrOZsofXqs1fjKbuZeDyB1Vok5qyj7AawVS4f_BlKRuNlTJmERnKMNoEtewzdSRW4SgvGKFXfE__SP6c4ylYLRP_5Ysd5oZRhhyFqWi-0ZKbu_KyMHZ0LN-EDYUUOpWAnDoYK_1XS0HzCTvoX4WPqHC)
2. [unipd.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaSoo6_GyMRymXU5jWbCuQRiaJaciLU966MhpD8cQBX1tnqEgwBqxNIjP97sFaf78UUEyz3-fySPl-nc20EKBGlZVBZUQD89bi3B3sPEzr8yvP_XzNzmq--PBMDa4qp1_WnIsXg1k=)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-oqLr-2-itxwZRv0D1VonYMzL19Dt_Rl6gYDGVekT6VbAE6qIFUbkfDzabA7F0UMNF05F6r6n7HP5Oozfp7YpllSV7XSceSPnrvbWPusR-NOktbFPtd4P)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHokEpX3D40HnWdQgJt9GQhm23DrS4P0oKqMvqNGdo506Nydxm-qiDnWb4mv7pehtTcONlA4pOizpWPUkr_hRd6Tq8Loz3MyzlRY-wfa3nQzC5h8NhzIxyw)
5. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxiLla1VBH5scU2FNo03JrbcYyP4s1D8RkBhYJemO45VQHsHqhjLTK-Vd3nRm2nyfTlaYW1q__ku26A5F61FeCGgAbIXq2xsrN9f20yWS-3n4ZFDoi_FQvwwCIUYm3)
6. [copernicus.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF71q1zTVT5-PP6HIr4AlRpLcDK6TA4Gnauf_WfgpKLGszBMi8K8lLJLuiMd6BD9Smd5vey3a9zk2LHauQxExGAyJzPG6ivCnj9f8KTNuuD6s6ARXU22AZur1pmKavrXt-hb3VS3DNM)
7. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6nLTJjuNshq2KQ1w_65GK6AEY2Zsz5B5Vu-iFbWrm9e6X2U8a9MINN9GAWSBZaYy9Orx0LNM7I1T7-G1HYNWjIWpBibxaBMP5YmyHmkJ48O4hj_SahA-jquDNYHXQ7-UxL8tHVc9nZqEflTzjPAT182FM1O1AYUAgO98=)
8. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFVKfBRlatGiFoVv41mFNX-46Nvu-15cU-kN9qFqkos2i0yfgwkyHf09pIdXtUWV5q5r0vJIqYdMsHZ7ij3Lw2XbyjLaCg2MnHWgbqRDLaxrNBsuZrzZIbRcC3FJpD-kuM0sJADvl5pxtH0KA4DIwYrZgCSzwOxXHnIMg==)
9. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjGYyRYEv8Y2mGlE5DdkASdD7gObLIQRG5rMHMpqHnwF1uwoFPJdp1-31JhkAZZPwy3ACWM6JiUyWkF1rR4QWbcUpYtvI_gvfJu_qKM6TaSop1_0hTxFEkMGGIwgtf6ExL5FXlxM7YqSwLPdzgI2GgDn6lM1Lg00N3ms7iLD9K0Fs8e2zE5stPCGth2n1uD-MS)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeci8PckBS3fmbWZB8Sw8MVHPg9Pz1-ku7P_4TyVQWBJnZsJAZo_3XH27xdEFR2mNwODvPBR4Q_OCMs4S3bN0X_vfEiU6gxh-XpdhdUMy6zOUC8kd2vzj_)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqqpdvbg71BIOBkJbwhgG_QKYuablUSDLemfR7LqldY2n9CsByY2e9Q0mrGmxUVcNJgvQQECZR8QqufyqXwxTE2oQtn_vqhV5URMQF-i6CeqLswpdi5gaf)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWF7FusYiacaMYsjdhBGSf0vH7Wbn-q60J_SnI6dV884Uzp_bGbvK1GxqDkeHkvdiXNMGQW3UXWmqnFa3LAJ9EW_n32ZJlf6qJulgdoPUxNmxXoQKqOlcW)
13. [imstat.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHB6vKdSt2tY18q8-sreOvwjZCq784NqXfoBidiedtkmeHdg4BGdgoUwRgyWjlOXZgN62uWa7HUIKBUqaEpqruXJilJ7KjGGtEcrnWBcG_27K9UtXluqP5hG_R_K8RzohDJFnF7VOpNThtiArSuc8PaQWR5q82FHRkANXKL8VZvO005eGM=)
14. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRvhx7YOb8j7TEoWfKFWOmDYDrxpGQbyy_hPuMxkLVcyBQKqYFeOBbV7mCf6XEfwBkKdOxZptYz4OI8e563jdXmGg73t0nCfVjjmfiQ57x43iPSeUrbOQlTHAX__oJLiI5diiZpGwp)
15. [imstat.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuw6CcLAmtdv_enCTOdgJVHFZm4W5ZegAZu0d-DoTZwupEcgh9DOR7wz4aZ91G1Xck_IdlFJKho0ltebY5wdU-C0dZAPpuXIlDif4YHpvmci6muXGy45NDKZoNwDpVpGfEeNM-i3mM7Zci70ZtQF_Ao_1h1L2aMq5QQGy5Z9OxSwprlvhQ_OQG-cRiXwNNNg==)


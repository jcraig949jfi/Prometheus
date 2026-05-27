# Prompt 13: G15 Cross-Generator MI — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chdnb1lXYXRuTUR0U0wxTWtQaTVHbm9ROBIXZ29ZV2F0bk1EdFNMMU1rUGk1R25vUTg
**Elapsed:** 243s

---

# Comprehensive Analysis of Mutual-Information Estimation, Cross-Detector Triangulation, and Confound Control in Multi-Source Experimental Data

**Key Points**
*   **Estimation Bias in Sparse Matrices:** The baseline Shannon plugin estimator used in v1/v2 pipelines introduces severe positive bias in sparse regimes (13 plugins $\times$ 21 kill patterns with only 420 observations). Research suggests that employing Bayesian Nonparametric frameworks with Dirichlet process priors offers a mathematically rigorous correction for finite-sample biases.
*   **Confounding Variables:** The absence of conditioning on the `parent_problem` introduces spurious correlations. Estimating Conditional Mutual Information (CMI) effectively isolates the residual dependencies, though it exacerbates sparsity, requiring advanced estimators.
*   **Multi-Source Triangulation:** Moving beyond pairwise statistics, substrate-grade signals can be robustly identified by requiring concurrent observations from $\ge 3$ distinct plugins. This paradigm mirrors multi-messenger correlation physics and high-stakes data triangulation. 
*   **Dynamic Log Classification:** Hard-coded filtering for control-flow kill patterns is brittle. Implementing self-supervised temporal contrastive learning models (e.g., LogBERT architectures) allows for the dynamic, automated classification of bookkeeping logs versus genuine failures.
*   **The Contrarian Position:** While information-theoretic measures are powerful, classical frequentist statistics such as Pearson's $\chi^2$ test or Cramér's V may offer superior interpretability, well-defined null distributions, and robustness against the specific sparsity profile of the G15 joint distribution.

This report addresses the theoretical limitations and architectural evolutions necessary for the G15 CROSS-GEN MI system. The transition from raw plugin estimators to advanced Bayesian frameworks, conditional independence testing, and self-supervised log anomaly detection represents a necessary maturation of the analysis pipeline. While information theory provides a rich vocabulary for system dependencies, we also seriously engage with classical statistical methods that may better suit the specific dimensional constraints of the current dataset.

---

## 1. Mutual Information Estimation on Small Sparse Joint Distributions

### 1.1 The Pathology of the Plug-in Estimator in Sparse Regimes
The current G15 v1 and v2 loaders utilize the standard plug-in (maximum likelihood) estimator for Shannon Mutual Information (MI), defined empirically over the plugin and kill_pattern counts:

\[ \hat{I}_{\text{plugin}}(X; Y) = \sum_{x \in X} \sum_{y \in Y} \hat{p}(x,y) \log \frac{\hat{p}(x,y)}{\hat{p}(x)\hat{p}(y)} \]

The G15 observation space consists of $|X| = 13$ plugins and $|Y| = 21$ kill patterns, resulting in a joint contingency table of $13 \times 21 = 273$ cells. With $N = 420$ observations, the average cell occupancy is approximately $1.54$. In this sparse regime, the empirical plug-in estimator is notoriously and predictably biased upwards. The Miller-Madow first-order bias correction approximates this inflation as:

\[ \text{Bias}(\hat{I}) \approx \frac{|X||Y| - |X| - |Y| + 1}{2N} \]

Applying the G15 parameters: $\frac{(13-1)(21-1)}{2 \times 420} = \frac{12 \times 20}{840} = \frac{240}{840} \approx 0.285$ nats. 

The LIVE FINDING (ITER-13) notes that the v2 MI is $0.16$ nats. Because $0.16$ nats is *less* than the theoretical first-order bias of $0.285$ nats, the apparent information in the v2 filter is essentially indistinguishable from statistical noise. The system is capturing noise artifacts of finite sampling rather than true plugin-pattern coupling.

### 1.2 Modern Corrected Estimators (2024-2026)
To resolve this, the estimation strategy must shift from naive frequency counts to regularized or Bayesian approaches. Recent advances in 2024-2026 have formalized highly robust estimators.

**Bayesian Nonparametric (BNP) Estimation with Dirichlet Priors:**
For categorical/discrete variables, introducing a Dirichlet prior over the multinomial distribution of the $X \times Y$ contingency table acts as a structural regularizer. By utilizing a symmetric Dirichlet prior characterized by concentration parameter $\alpha$, the cell probabilities are updated via pseudo-counts:

\[ \hat{p}(x,y) = \frac{n_{x,y} + \alpha}{N + |X||Y|\alpha} \]

Recent literature significantly advances this paradigm. A prominent 2025 study by Fazeliasl et al. introduces a deep Bayesian Nonparametric (BNP) framework utilizing finite representations of the Dirichlet process posterior to incorporate regularization directly into MI estimation [cite: 1, 2]. This framework mitigates the sharp fluctuations in the MI loss landscape that occur due to poor out-of-sample performance in empirical distribution functions, integrating both prior knowledge and empirical data [cite: 1, 2]. By leveraging Dirichlet processes, the estimator reduces sensitivity to sample variability and outliers, which is mathematically ideal for the G15 system's small batch (420 observations) and sparse cell conditions [cite: 1, 2].

**Recommendation:** For the discrete $13 \times 21$ categorical space of the G15 loader, a **Bayesian MI estimator with a Jeffrey's ($\alpha=0.5$) or Perks ($\alpha=1/|X||Y|$) Dirichlet prior** is the optimal choice. It avoids the continuous-space assumptions of KSG (Kraskov-Stögbauer-Grassberger) and bypasses the instability of Jackknife resampling in heavily zero-inflated tables. It allows the system to assert $\text{MI} = 0$ confidently when the data lacks sufficient evidence of correlation.

---

## 2. Conditional MI for Confound Control

### 2.1 The Need for Conditioning
The v2 pipeline employs a marginal MI computation: $I(\text{plugin}; \text{kill\_pattern})$. However, claims (and their resultant failures) do not arise in a vacuum; they inherit structural characteristics from their `parent_problem` (e.g., specific BL-C-* datasets). If certain plugins are exclusively routed specific types of parent problems, and those problems inherently trigger specific kill patterns, the resulting plugin-pattern coupling is entirely spurious—a classic epidemiological confounder.

To test whether the plugin-pattern coupling persists *after* controlling for the origin of the claim, the v3 loader must implement Conditional Mutual Information (CMI):

\[ I(\text{plugin}; \text{kill\_pattern} \mid \text{parent\_problem}) = \mathbb{E}_{Z} \left[ I(\text{plugin}; \text{kill\_pattern} \mid \text{parent\_problem} = z) \right] \]

### 2.2 Methodological Implementation and 2025-2026 Research
Implementing CMI on the G15 data partitions the 420 observations further into strata defined by `parent_problem`, drastically amplifying the sparsity problem. 

To address this, modern CMI estimation relies on sophisticated nonparametric approaches. The `conMItion` R package, introduced in a 2026 study by Wang et al., provides a robust framework for assessing both linear and non-linear associations while effectively accounting for confounding factors [cite: 3, 4]. `conMItion` allows for finite-sample permutation testing within strata to generate valid $p$-values without relying on asymptotic distributions [cite: 3, 4]. 

Furthermore, 2025 research by Popescu et al. investigates non-parametric conditional independence testing specifically for mixed categorical and continuous variables, providing optimized $k$-nearest-neighbor (kNN) CMI estimators that detect dependencies robustly across different data distributions [cite: 5]. Because our variables (plugin, kill_pattern, parent_problem) are strictly categorical, entropy-decomposition estimators are preferred over continuous metric-space nearest-neighbor methods. 

For the v3 specification, we define the CMI as:
\[ \text{CMI}(X; Y | Z) = H(X, Z) + H(Y, Z) - H(X, Y, Z) - H(Z) \]
Using the Bayesian Dirichlet-prior entropy estimators for each of the four joint/marginal entropy terms ensures that the resulting CMI does not artificially inflate due to the extreme stratification across multiple parent problems.

---

## 3. Cross-Instrument Triangulation as MI-Equivalent

### 3.1 Substrate-Grade Signal Detection
The primary theoretical objective of the G15 cross-gen MI system is to detect systemic, plugin-independent structural failures (`uncorrelated_residual_failures`). Information-theoretic MI treats plugins as independent identically distributed (i.i.d.) sensors. However, true epistemological confidence in experimental substrates derives from multi-source triangulation.

Drawing from 2024-2025 research in multi-source experimental data and multi-messenger astronomy, cross-detector correlation relies heavily on concurrent independent verification. For instance, in astrophysical signal detection, verifying gravitational wave events explicitly requires cross-detector correlation analysis where time delays and coincident strain amplitudes confirm the signal against localized detector noise [cite: 6, 7]. Similarly, in meta-analyses of multi-source experimental data, overcoming experimental heterogeneity and small sample sizes is achieved through robust triangulation frameworks [cite: 8, 9]. 

### 3.2 The $\ge 3$ Triangulation Refinement
In the context of G15, a "claim" that generates the exact same `kill_pattern` across multiple distinct plugins represents a high-fidelity signal. We can operationalize this through a Salem moderation triangulation structural equivalent:

*   **Weak Signal:** Claim fails on 1 plugin. (Could be local plugin configuration).
*   **Moderate Signal:** Claim fails on 2 plugins.
*   **Substrate-Grade Strong Signal:** Claim fails on $\ge 3$ distinct plugins with the identical non-bookkeeping `kill_pattern`.

Instead of purely calculating $I(\text{plugin}; \text{kill\_pattern})$, which aggregates over the entire dataset, we compute the **Cross-Plugin Claim Agreement**. If $I(\text{plugin}; \text{kill\_pattern}) \approx 0$, it implies that knowing the plugin gives no information about the kill pattern—which is exactly what we want for universal, substrate-level errors. By tagging claims where $|\text{unique\_plugins}| \ge 3$, we extract the exact records driving this conditional independence.

---

## 4. v2 Loader Design: Concrete Specification for G15 v3

The `g15_v3` architecture integrates the insights from Bayesian estimation, conditional confounding, and multi-source triangulation. 

### 4.1 Structural Specification
*   **4.1.a Bayesian Dirichlet-prior Shannon MI:** 
    Replace the empirical `p * log(p)` with a Dirichlet-smoothed entropy module.
    ```python
    def bayesian_mi(df, x_col, y_col, alpha=0.5):
        # alpha=0.5 is Jeffreys prior
        joint_counts = pd.crosstab(df[x_col], df[y_col])
        N = joint_counts.sum().sum()
        shape_x, shape_y = joint_counts.shape
        
        # Add pseudo-counts
        smoothed_joint = (joint_counts + alpha) / (N + shape_x * shape_y * alpha)
        marginal_x = smoothed_joint.sum(axis=1)
        marginal_y = smoothed_joint.sum(axis=0)
        
        # Compute MI
        mi = 0
        for i in smoothed_joint.index:
            for j in smoothed_joint.columns:
                p_xy = smoothed_joint.loc[i, j]
                p_x = marginal_x[i]
                p_y = marginal_y[j]
                mi += p_xy * np.log(p_xy / (p_x * p_y))
        return mi
    ```

*   **4.1.b Conditional MI on `parent_problem`:**
    Execute the entropy decomposition $H(X,Z) + H(Y,Z) - H(X,Y,Z) - H(Z)$ using the same Bayesian smoothing to evaluate if $I(\text{plugin}; \text{kill\_pattern} | \text{parent\_problem}) \le \epsilon$.

*   **4.1.c Cross-plugin Claim-Counting:**
    Group by `claim_id` and compute `nunique()` of `plugin_id`. 
    ```sql
    SELECT claim_id, kill_pattern, COUNT(DISTINCT plugin_id) as plugin_agreement_count
    FROM kill_ledgers
    GROUP BY claim_id, kill_pattern
    HAVING plugin_agreement_count >= 3
    ```

*   **4.1.d New `kill_pattern`: `triangulated_artifact`:**
    If a claim triggers a failure across $\ge 3$ plugins, but human-in-the-loop or oracle verification dictates the claim itself is fundamentally broken/hallucinated, it is classified as a `triangulated_artifact`. This captures the phenomenon where multiple plugins "agree", but they agree on a structurally invalid artifact.

---

## 5. The Control-Flow Filter: Learned Classifiers

### 5.1 The Fragility of Hard-Coded Suffixes
The v2 loader utilizes a `control-flow filter` that relies on hard-coded suffixes (e.g., `_bookkeeping`, `_init`) to drop uninformative rows, reducing the MI from 1.41 to 0.16. As the system scales and engineers add novel plugins and kill patterns, this hard-coded list will rot, leading to data leakage where structural bookkeeping inflates the MI.

### 5.2 Self-Supervised Log Anomaly Detection
Instead of explicit rules, the v3 loader should treat the `kill_ledger` as a stream of system logs and apply a learned, self-supervised classifier. Research in 2024-2026 has revolutionized log parsing through temporal contrastive learning and self-supervised sequence modeling.

Methods like **LogBERT** and **ALogSCAN** utilize Transformer architectures to learn the normal syntactic behavior of operational logs without requiring labeled anomalies [cite: 10, 11]. By training a two-layer transformer encoder on known normal event sequences (e.g., the expected execution flow of a claim evaluation), the model computes a pseudo log-likelihood (PLL) for each log token [cite: 10]. Routine bookkeeping tasks exhibit highly predictable temporal sequences (high PLL), whereas true, uncorrelated residual failures manifest as severe deviations from the temporal norm (low PLL) [cite: 10, 12].

Additionally, the LogMT framework demonstrates that multi-task self-supervised learning can extract semantic meanings directly from raw, unparsed log messages, utilizing attention-based Transformer models to categorize log anomalies accurately [cite: 13, 14]. 

**Implementation Strategy:**
1.  **Sequence Modeling:** Treat the lifecycle of a `claim_id` as a sequence of `kill_pattern` events.
2.  **Self-Supervised Training:** Train a lightweight semantic retrieval model (e.g., a BERT-derived model or ALogSCAN equivalent) on historical ledgers to predict the next event in a claim's lifecycle [cite: 11, 12].
3.  **Inference Thresholding:** If a `kill_pattern` is predicted by the model with $>95\%$ confidence based on preceding events (e.g., `plugin_start` $\rightarrow$ `schema_validation`), it is classified as `bookkeeping` and filtered. If it constitutes an unpredictable break in the execution graph, it is passed through as a true failure for MI analysis.

---

## 6. Contrarian Perspective: MI is the Wrong Statistic

### 6.1 The Steelman Argument against Mutual Information
While Mutual Information provides a mathematically elegant non-linear measure of dependence, it is arguably the wrong statistic for the G15 CROSS-GEN system under its current constraints (small $N$, discrete, heavily sparse tables). 

**Argument 1: Interpretability and Dimensional Scaling**
MI outputs in 'nats' or 'bits'. In the G15 v1 dataset, $\text{MI} = 1.41$ nats. To an engineer or decision-maker, this number lacks intuitive scaling. Does $1.41$ nats imply a catastrophic coupling or a minor correlation? The theoretical maximum is $\min(H(X), H(Y))$, which fluctuates dynamically based on marginal distributions.

**Argument 2: Asymptotic Distributions and the $\delta$-method**
A rigorous 2025 study by Marinescu et al. on the use of Mutual Information for testing independence leverages the $\delta$-method to prove that the difference between empirical MI and true MI can be approximated by a linear combination of $\chi^2$ (chi-square) random variables [cite: 15, 16]. Because the gradient vanishes when testing independence, a second-order approximation is required, making the asymptotic distribution of MI highly complex [cite: 16]. The study proves that relying on MI without accounting for this complex distribution leads to significant interpretation errors [cite: 16]. 

**Argument 3: The Superiority of $\chi^2$ and Cramér's V for Small Discrete Joints**
A simpler, classical approach like the Pearson $\chi^2$ test of independence, coupled with an effect size metric like Cramér's V, is vastly superior for small contingency tables.
*   **Well-Understood Null Hypothesis:** The $\chi^2$ test explicitly tests against the null hypothesis of independence, yielding a standard $p$-value.
*   **Cramér's V Normalization:** Cramér's V normalizes the $\chi^2$ statistic strictly between 0 and 1:
    \[ V = \sqrt{\frac{\chi^2}{N \min(|X|-1, |Y|-1)}} \]
    Unlike MI, a Cramér's V of $0.05$ universally indicates negligible association, and $0.80$ indicates massive coupling. It is inherently resistant to changes in the matrix dimensions, making it robust if the number of plugins or kill patterns expands [cite: 17].

**Argument 4: Zero-Inflation handling**
Sparse data with 420 observations across 273 cells implies many zero-valued cells. Information-theoretic MI struggles violently with zero-probabilities (requiring smoothing or pseudo-counts that artificially bias the metric). Exact tests like Fisher's Exact Test or Monte Carlo permutation $\chi^2$ tests perfectly handle sparse zero-inflated tables, yielding exact probabilities of independence without relying on density estimation assumptions [cite: 18]. 

### Conclusion of the Contrarian View
By replacing MI with Cramér's V alongside a permutation-based $\chi^2$ $p$-value, G15 would immediately gain a standardized, normalized [cite: 19] metric for plugin-pattern correlation. This bypasses the need for complex Bayesian Dirichlet priors simply to correct for the mathematical artifacts of Shannon entropy in low-$N$ regimes, trading an opaque information-theoretic concept for a transparent, universally understood frequentist framework. Both paradigms are valid, but the engineering simplicity and epistemological clarity of Cramér's V strictly outweigh the theoretical elegance of Mutual Information in sparse, low-volume substrate monitoring.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdz4qTSlkS8asAw6eI7LFvpn9D5Z_RfACrlgGCqCHXRQ41CVl5pGAPF5AooKut4-JGqxBCZYX9mal1ugklQIiI8xC1hefQx0KbVX4pc5_vVhIb9CL_YA==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVEaNeifzzu1X4TWaOIO02xOYrcv_qt15j-_vuKp1imFInET1CRwLgLgDbtHh1Jl53IcPVfyphKjwGOorPsWHnqK6ZsGlMW5xKSicrTzn8ZXo9EApq9NmX1A==)
3. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2pefNqsE1h2ZWBUHRFOP_7CpwEifby9prfPtHYkd1k773xbm3qM9bKttRDjHcjoEzshS0hEpJFfmXUMll92UkFRaIp0pFO3WlgjBC2EvjYYBTdyh2xvqyGelp_iQ_Ibd7lezhsp3HJ2s6pGWoepaFpGk=)
4. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5Kfht2YTK3q5upW7p7aVzsbDJ8VvNSYEgHv9nf5la0lqPulDsJKuyZSt5e2zwZEDcINFqAg7w5I99-Vq2oKnbwePil148gdOMpkYnZz_suSrtm5RI0glBsPsEgVLmWQfqZUtmNaHaIiwhNc6eW05NjPaQH7QAwigejFQ0cHP5Zsd4WFz6YSxRGnSY43bt46HTKhreldRodGGNsO3N24r7M2fLMQdgklgx1ag6M9O__V1FDd-g-F6H5n5qrMD9)
5. [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFRKl4giUYRzPPobiHo9HS5P-fS44kO0cR9ggDW6oi6TiXpCT6e75-mss2LCN6BkH8R_XaUcR1_EQfj6cDV7E4UEck98H8qqfrsHX_1fXza-MZmkydDeIrkLm-V8XcE7sE-DXhsxA5csQ==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFxb5wWlWLuABN1NXMpkYy0kE1IaRGV0uRGjrkKLf_8zACo9HMAE8S4QIgNFZfPG4jYU2FypRKP0xYzgHb-a8KikN82XWXSBok7pLMqSjlY_E_KbBYbA==)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLn7g8D1QTHfTpB37t5IzKNPFavWGxQ-jPmsUze5efm6QObk6ahFdN0Q1DrM7fEj4XObNiFRKHyE5AbO2nMEfhUKc9FhvJt3xmfyWqV6OX3v7ArOMfGjGSJA==)
8. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE8NfQ1oMC4rsQbSffWirbzvxJC9PpIvMIYagirVJcLGzSModE0hSxPxJWN_CYeJIVq9JMyZeuUNvDc5tklppqXWSoo4p3ITyKrjYlq5MLTvbCP1GkyAfIMxUTTfGSQvjwxCPzyLXKjBw==)
9. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIDS4E2aSR1xu1JVcjJYcIUnkYWZI6j2N2sYMiCNP2ifXHdDtKE6frgnmNdzqvlwOw7u38ZT_aDQ-AgaRHUauQraRAxSekY7Of7mhHv00gjzhUpilPwcJQGo4hyJGYAmc4BnPuJc2fpqKRJGc0PXSQyOVRdVois7g=)
10. [ubhara.ac.id](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcYLzUntGe-2MxTgjqtueqRvAd6f0qmmXm0UcKZkYeiKiFEKiBDn6rNIE8iHzY6fd9idIBFlvJI6frFCPnimoSuJvqtGGnkY9DB7ltgSbZcCFNsrK_7KjR-_D5TPjT0q9KF1_RqYcT48SV6lKTJo9BodaH07o=)
11. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhmjNdzZIgODl_zkpEv09HOGHKh5LmUFV2y0Rk3qc_N9UrxETVD_6F2PWOcyzHYNwV71krU8GBcjv-_BvK8OncB5HioI4LBpChE11UZdPCI3J4-dq4xw5h5owBOCywEi6DTyOTjarYRiUArrqdeKePAM-fJw==)
12. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb87QpYSSR3qQdhEKeMT0gPQ4P0Z7smut-XH6i77qJRhTKXtuXjgMM_6BTMDudQSxeAVYvesYlKNQrkUmCigWNHW9LIVQyxZYUUMm_sRTYOoxhbN_AHM6rNOwrhB_f_GrTBwlydEo=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCFSMsnlwr3xd7iUSIhMxf_Z3KeCSX5Y9cAYAY6bBxwPiyN6zJU_9v42H2gMt8t914p5fGhbSvhvWRZpOVmEebgrn8Y702yh04lu9vmphQV_4iM2x-6T2cmmnF7OvNBmiJxR0zfY_sZI907m6MePZWHjAJtJKhArMy7QnhDxebPi5SrE5-1pdo-20JsMI8yXYTiJldi4L-fw9uzNiaJlr3aW7Ho5nDVskp2d-IZFWlo0US)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnb7GZsmW1iGpUocGdhLcJQUtjc8RMzCUdESOtrIwlbdoU5SoZlIaRo1x9n6UxNRDfBvQ3JyKQ9dLq1LX2oDbZR-0hOCR-4VkheyN47A2Qvb1-0eZDqyThbB0FIayPT3j1finITRNbWLvUPkNXGYrRrUHMQi_CccCxKDEuL9KtLxcS9iLD0XRH_hCMNdA9_VWmCb4E3kkgnI3eW3jj2UxGVwmUQ1-4jU9tYtzhtJ4S5X6OASed1-BB20CfDzgEcz2f)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_RjqIC8CsKjoFvlwyERHRXTyn0APYXXufVGgWAn7O24iJHIGvKl2DOdHSFctb4vrWqZvaSv05P3pfmDTzLD5FjC9Fe0AxkYOJ8E42KY5sn1QLN-o6DfLe3w==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOjwSREt6GzJEgEq5AMNrvBvR75UzU5qTYvLLrX-ATrm0scRwnKfVTzop6Q7USk3BsrsmkRhJHM4g0Zo2MZv34ByCd9egRkED4fb51ZthSOmvsu9Eqaw==)
17. [grokipedia.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtf5xMg1FM24xWVmevkmzeZufRCYQbmv3RuAONZucKOZtGr011hVD9oRq5xVwqulzXbTie_veIOP2VvQHVap4fMZvtK_rijlq-fMc2RJDnbTJxhLr1JUJK54nE2LxSk1m5)
18. [royalsocietypublishing.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmd8PmEYsXrcUB28HIkt8QfLkptxNUS5ShBMP1BsmMLq6vs8yVtjsYiE41FoiCDlDoYAgkd7roPBMX9aRANuPpVls1ha2aeRvs7RhWArAzU0eBFv9qTTjfsSB4B30-qdsRgGR7afjvf58E4TIs-3mEV2MriL-QUagWB5vEPHF_4zglzxJseE1ki6XaL8EM_1E9QQyiOmGZrqxKuhXqEUz20S99qAC61nI1Lh1DzLoT)
19. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWsQEuE40rorM2n8RE2DXt2uJsow3nNW9YCIo7QmoX6xWHj10lG74LvQfV_P8gzqHkx-2E1UgmhNMFOsQGH2v33ndoE6ypZMgJOPQ-IE5XwXjqiqzS-eBYDYG2sDTpfxAmq5Q6PsMCAC5kmBaAqYju2FUkeY1Vfn3oHWOduw==)


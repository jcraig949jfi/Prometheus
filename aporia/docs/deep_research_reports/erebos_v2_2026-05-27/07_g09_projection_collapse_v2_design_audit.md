# Prompt 07: G09 Projection-Collapse — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdJWVFXYXNQeUtfVE0tc0FQNktyMXlBMBIXSVlRV2FzUHlLX1RNLXNBUDZLcjF5QTA
**Elapsed:** 243s

---

# Advanced Methodologies in Single-Coordinate Signal Isolation and Dimensionality-Reduction-Based Hypothesis Testing

**Key Points:**
*   Scientific claims often rely on complex, multi-dimensional models, but researchers frequently attempt to isolate a single "dominant" variable to explain the phenomenon. While this simplifies understanding, it risks obscuring genuine complexity.
*   Recent advancements (2024–2026) in explainable artificial intelligence (XAI), such as Shapley values, Integrated Gradients, and feature ablation, provide mathematical frameworks to measure feature importance, though each can be misleading under certain conditions (e.g., collider bias or out-of-distribution sampling).
*   The transition from a "feature-agnostic" random ablation approach (v1) to a "feature-specific" isolation approach (v2) allows for more precise hypothesis testing. If dropping the single most important variable fails to destroy the model's predictive power, the underlying claim is genuinely multi-dimensional.
*   Not all claims should be projected onto a single coordinate. Claims involving conditional independence, intricate polynomial relations, or topological invariants are inherently synergistic; attempting to isolate a single explanatory variable for these claims constitutes a category error.

**Overview of the Problem**
In the evaluation of scientific claims and complex predictive models, there is an ongoing tension between reductionism (isolating the single most important factor) and holism (acknowledging the distributed nature of the system). The G09 PROJECTION-COLLAPSE protocol seeks to interrogate claims by projecting a complex composition onto its highest-variance coordinate. If a claim asserts that a complex interaction drives a phenomenon, but a single variable captures >95% of the predictive power, the claim's purported complexity is a mirage. Conversely, if dropping coordinates leaves a `residual_survival` of predictive power, the claim is genuinely complex. 

**The Proposed V2 Solution**
The current v1 loader relies on random 50% subsampling (Lehmer ablation), which is feature-agnostic and frequently results in false rejections because it fails to target the actual coordinates carrying the signal. The proposed v2 loader utilizes Shapley-value attribution to rank features, specifically dropping the absolute highest-contributing coordinate. This forces the model to prove that its predictive power is distributed across multiple coordinates, rather than relying on a single dominant feature.

**Broader Context**
Understanding when to ablate a feature (remove it entirely) versus when to stratify on it (hold it constant to control for confounding) is critical for rigorous scientific discovery. Furthermore, certain mathematical spaces—such as those explored in Mossinghoff polynomials or Bayesian conditional independence graphs—defy single-coordinate projection entirely, requiring entirely different verification paradigms. 

***

## 1. Projection Methodologies (2024–2026)

The pursuit of "isolating the dominant explanatory coordinate" in complex scientific claims has been revolutionized by Explainable Artificial Intelligence (XAI). However, applying these methods to scientific discovery requires a rigorous understanding of their theoretical limits. Below is a survey of three primary methodologies published between 2024 and 2026, including their mathematical formulations and the specific conditions under which they produce misleading results.

### 1.1 Shapley Value Attribution
Shapley values, derived from cooperative game theory, have become a cornerstone for measuring multivariate feature importance in scientific discovery [cite: 1, 2]. The method assigns a marginal contribution score to each feature by averaging its impact across all possible feature coalitions. Recent innovations, such as **GeoShapley** [cite: 3, 4] and **FastShap** for single-cell biology [cite: 5, 6], adapt these values to handle spatial data and high-dimensional biological data, respectively.

*   **When it is Misleading (Collider Bias and Causal Suppression):** 
    Purely data-driven Shapley values are highly susceptible to causal artifacts, most notably **collider bias** and **suppression** [cite: 7, 8]. As highlighted in 2026 research on *cc-Shapley* (causal context Shapley), if a model conditions on a common effect (a collider), spurious statistical associations are introduced between its causes [cite: 7, 9]. Conventional Shapley values evaluate features in the observational context of other features without respecting the underlying causal graph. Consequently, a feature might receive a massive attribution score not because it causally drives the target, but because conditioning on other features unblocks a non-causal path [cite: 10, 11]. Therefore, without causal context, Shapley-based single-coordinate isolation can incorrectly identify a suppressor or collider as the "dominant" explanatory coordinate.

### 1.2 Integrated Gradients (IG)
Integrated Gradients (IG) is an axiomatic attribution method that calculates feature importance by integrating the gradients of the model's output with respect to its inputs along a path from a user-defined baseline to the actual input [cite: 12]. Recent 2025 advancements include **Path-Weighted Integrated Gradients (PWIG)**, which incorporates customizable weighting functions to mitigate noise along different segments of the integration path [cite: 13].

*   **When it is Misleading (Out-of-Distribution Traversals and Baseline Dependency):** 
    IG is mathematically guaranteed to satisfy sensitivity and implementation invariance, but it is heavily dependent on the choice of the baseline and the integration path [cite: 13]. IG is misleading when the straight-line interpolation between the baseline and the input traverses regions of the feature space that are completely unrepresented in the training data (out-of-distribution). In such cases, the gradients obtained are effectively random artifacts of the model's unconstrained behavior in empty topological spaces. Furthermore, in highly non-linear scientific claims, gradient saturation can cause IG to miss the dominant coordinate entirely, assigning high importance to variables that merely trigger early activation thresholds rather than those that carry the true explanatory variance [cite: 12, 14].

### 1.3 Feature Ablation (Dimensional Dropout)
Feature ablation involves systematically replacing specific input variables with a baseline value (e.g., zero or the dataset mean) and measuring the resulting degradation in model performance [cite: 15]. Recent applications in 2025 include thermodynamic load forecasting [cite: 16, 17] and multi-dimensional dynamic circulatory failure prediction [cite: 14], where ablation is used to quantify the strict necessity of specific variables.

*   **When it is Misleading (Collinearity and Temporal Multi-Output Masking):** 
    Ablation is deeply misleading when applied to systems with high **collinearity** or redundancy. If a complex claim relies on two highly correlated variables (e.g., two redundant biomarkers), ablating the dominant one may cause no drop in performance because the model simply shifts its reliance to the correlated surrogate. Thus, ablation will falsely conclude that the dominant coordinate is irrelevant [cite: 15, 18]. Furthermore, as demonstrated in 2025 studies on dynamic circulatory failure, feature ablation fails in time-varying multi-output models; it produces multi-dimensional attribution maps that obscure sustained pathophysiological patterns, making it impossible to isolate a single temporally stable dominant coordinate [cite: 14].

***

## 2. The 50%-Ablation Choice: Moving to Feature-Specific V2

The current v1 loader relies on `g09_lehmer_ablation`, which utilizes a deterministic 50% random subsample of the coordinate catalog. This approach is fundamentally **feature-agnostic**. By randomly dropping half the features, the loader tests the model's robustness to general information loss, but it completely fails the core objective of the G09 protocol: *isolating the single highest-variance coordinate*. If the true signal is distributed across 10 coordinates, dropping a random 5 of them will reduce performance, leading to a `residual_survival` verdict. If the true signal rests entirely in 1 coordinate, dropping a random 5 has a 50% chance of missing that coordinate entirely, again leading to a false `residual_survival` verdict.

### 2.1 Proposed V2: Feature-Specific Ablation
To rectify this, the v2 loader must abandon random subsampling in favor of targeted, feature-specific ablation. The objective is to identify the candidate "single dominant coordinate," remove it exclusively, and re-test the parent claim.

**Concrete Decision Rules:**
1.  **Coordinate Ranking:** Upon receiving a complex claim \( C \) with a feature set \( X = \{x_1, x_2, ..., x_n\} \), compute an attribution score \( S(x_i) \) for every coordinate using a robust XAI method.
2.  **Dominant Coordinate Identification:** Define the candidate dominant coordinate \( x_d \) as the feature where \( \arg\max_{x_i} S(x_i) \). 
3.  **Variance Check:** Before proceeding to ablation, calculate the relative attribution mass \( M_d = \frac{S(x_d)}{\sum S(x_i)} \). If \( M_d \ge 0.95 \), the model is already heavily centralized on one coordinate.
4.  **Targeted Ablation:** Create an ablated dataset \( X' = X \setminus \{x_d\} \). 
5.  **Re-evaluation:** Train/test the claim on \( X' \). Let \( P_{full} \) be the predictive power (e.g., AUC, R-squared) of the full model, and \( P_{abl} \) be the predictive power of the ablated model.
6.  **Verdict Thresholding:** 
    *   If \( P_{abl} < \tau \cdot P_{full} \) (where \( \tau \) is a harsh threshold, e.g., 0.10): The single dropped coordinate contained almost all the predictive power. The claim is mathematically simple. **Emit:** `projection_collapse`.
    *   If \( P_{abl} \ge \tau \cdot P_{full} \): The remaining coordinates still carry significant predictive power. The complex claim is genuinely multi-dimensional. **Emit:** `residual_survival`.

***

## 3. Shapley-Value Integration for G09 V2

To operationalize the ranking step in the v2 loader, we must integrate a theoretically sound attribution metric. Shapley values are the optimal choice because they are the only method guaranteed to satisfy the axioms of efficiency, symmetry, null player, and additivity [cite: 1, 2]. 

### 3.1 Shapley in Scientific Discovery (2024–2026)
Recent literature extensively validates the use of Shapley values for scientific discovery, moving beyond mere "black-box" explanation into causal hypothesis testing:
*   **FastShap for Single-Cell Biology (2025):** Tozzo et al. (2025) developed `Single-cell FastShap`, which efficiently amortizes the computation of Shapley values for high-dimensional biological data. They demonstrated that Shapley values can be used not just for model explanation, but for rational biomarker discovery by identifying granular subgroups most important for population size predictions [cite: 5, 6]. This validates the use of Shapley for isolating dominant coordinates in highly complex datasets.
*   **cc-Shapley (2026):** Martin and Haufe (2026) introduced *causal context Shapley (cc-Shapley)*, addressing the fatal flaw of standard Shapley values: collider bias. cc-Shapley acts as an interventional modification that leverages knowledge of the data's causal structure to eradicate spurious associations [cite: 7, 8, 11].
*   **GeoShapley (2024):** Li (2024) introduced *GeoShapley*, which extends the framework to conceptualize spatial location as a player in a model prediction game, allowing for the precise measurement of spatial versus non-spatial effects in geospatial phenomena [cite: 3, 4, 19].
*   **Shapley for Feature Selection (2025):** Trotskii et al. (2025) empirically validated that Shapley value-based feature selection is highly competitive with traditional methods (like Minimum Redundancy Maximum Relevance) for enhancing biomedical scientific discovery [cite: 20, 21].

### 3.2 Proposing G09 V2 Shapley Ranking
The G09 v2 loader will implement an amortized, causal-aware Shapley module (inspired by FastShap and cc-Shapley) to rank the feature coordinates. By using the conditional expectation of the output given a subset of inputs, the loader calculates the exact marginal contribution of each variable. This ensures that the "single dominant coordinate" selected for ablation is mathematically rigorous and not a byproduct of gradient saturation or localized heuristics.

***

## 4. V2 Loader Design Specification

The following is a concrete specification for the G09 V2 loader, moving from feature-agnostic Lehmer sampling to targeted Shapley-ablation.

### 4.1 Specification Algorithms

**A. Per-Coordinate Ablation Sweep & Shapley-Style Attribution**
```python
def g09_v2_evaluate_claim(claim_C, dataset, causal_graph=None):
    # Step 1: Shapley-style attribution
    # Utilize cc-Shapley if a causal graph is provided to avoid collider bias, 
    # otherwise default to amortized TreeSHAP/FastSHAP.
    shapley_scores = compute_cc_shapley(claim_C.model, dataset, causal_graph)
    
    # Step 2: Identify the dominant coordinate
    dominant_coord, max_score = max(shapley_scores.items(), key=lambda x: x[cite: 16])
    total_score = sum(abs(score) for score in shapley_scores.values())
    
    # Step 3: Check Single Dominant Detection Criterion
    survival_mass = abs(max_score) / total_score
    
    if survival_mass >= 0.95:
        # The model is inherently collapsed; 95% of attribution is on one node.
        return "projection_collapse", dominant_coord
        
    # Step 4: Per-coordinate targeted ablation
    ablated_dataset = dataset.drop(columns=[dominant_coord])
    claim_C_ablated = retrain_and_evaluate(claim_C.architecture, ablated_dataset)
    
    # Step 5: Evaluate Residuals
    residual_power = claim_C_ablated.performance / claim_C.original_performance
    
    if residual_power < 0.05:
        return "projection_collapse", dominant_coord
    else:
        return "multi_coordinate_distributed", None
```

### 4.2 Definition of Detection Criteria & Kill Patterns
*   **(c) "Single Dominant" Detection Criterion:** 
    A coordinate \( T \) is flagged as the "single dominant" coordinate if its absolute Shapley attribution mass accounts for \( \ge 95\% \) of the total absolute attribution across all \( N \) coordinates. Alternatively, upon actual ablation of \( T \), if the parent claim \( C \)'s predictive \( R^2 \) or AUC drops by \( \ge 95\% \), the criterion is met.
*   **(d) New Kill Pattern: `multi_coordinate_distributed`:**
    Replaces the generic `residual_survival`. When the highest-ranked coordinate is removed, and the model maintains >5% of its original predictive power, the loader emits `multi_coordinate_distributed`. This explicitly signals: *"No single dominant coordinate exists. The signal is strictly distributed across a multi-dimensional topological space. Dimensionality-reduction hypothesis testing is invalid for this claim."*

***

## 5. Cross-Plugin Interaction: G09 vs. G05

Within an epistemic validation framework, plugins G09 and G05 represent two distinct statistical operations that are frequently (and dangerously) conflated: **Ablation** and **Stratification**. 

### 5.1 The Mathematical Distinction
*   **G09 (Ablation / Dimensional Dropout):** G09 alters the feature space by completely removing a coordinate \( X_i \) from the dataset, projecting the data onto the remaining \( N-1 \) dimensions. It forces the model to learn the target \( Y \) using *only* the remaining variables. This answers the question: *Is coordinate \( X_i \) strictly necessary to predict \( Y \)?*
*   **G05 (Stratification / Conditioning):** G05 does not remove a coordinate; rather, it divides the dataset into sub-populations where the coordinate \( X_i \) is held constant (e.g., conditioning on \( X_i = z \)). This answers the question: *Does the relationship between the remaining variables and \( Y \) hold true across different fixed levels of \( X_i \)?*

### 5.2 When to use which: A Precise Decision Matrix
The distinction relies entirely on the causal structure of the scientific claim [cite: 7, 10].

**Use G09 (Ablation) when testing for SUFFICIENCY and NECESSITY:**
If a claimant asserts that a complex 100-gene signature is required to predict a disease, you use G09. You isolate the highest-weighted gene, *drop it*, and see if the remaining 99 genes can still predict the disease. If they can, the single gene was not strictly necessary. If the single gene alone carries 95% of the power, the 100-gene signature is mathematically bloated. G09 is an intervention on the model's architecture.

**Use G05 (Stratification) when testing for CONFOUNDERS and COLLIDERS (Simpson's Paradox):**
If a claimant asserts that Drug A causes Recovery B, but you suspect this is purely driven by a third variable (Patient Age), you use G05. You stratify (condition) on Patient Age. If the effect of Drug A disappears within the age-stratified cohorts, the original claim was confounded [cite: 10, 11]. Conversely, you must strictly *avoid* G05 if the variable is a collider (an effect of both A and B), as conditioning on a collider creates spurious, non-causal associations [cite: 7, 8].

In short: **G09 removes data to test model complexity; G05 fixes data to test causal validity.**

***

## 6. Contrarian: Complex Claims Where G09 Should Not Project

While the G09 PROJECTION-COLLAPSE protocol is devastatingly effective against bloated, over-parameterized models, there is a class of mathematical and scientific claims where projection onto a single dominant coordinate is a fundamental **category error**. In these domains, the information does not reside in the coordinates themselves, but strictly in their interactions, topologies, or tensor products. 

In the context of Mossinghoff polynomials, Bayesian conditional independence, and knot theory / topological invariants, applying G09 is logically invalid. Below are three such claim types:

### 6.1 Conditional Independence Claims in Causal Graphs (d-separation)
In probabilistic graphical modeling and causal inference, a claim of conditional independence asserts that two variables \( X \) and \( Y \) are independent given a set of conditioning variables \( Z \) (\( X \perp\!\!\!\perp_p Y \mid Z \)) [cite: 22, 23, 24]. 
*   **Why G09 Fails:** The conditional independence relation is a property of the *entire joint probability distribution* and the graphical topology (d-separation). If you apply G09 and ablate a specific coordinate from the conditioning set \( Z \), you fundamentally alter the causal pathways (e.g., opening a back-door path or unblocking a collider) [cite: 7]. The claim is intrinsically multi-coordinate; there is no "single dominant variable" that carries the independence property. It is the synergistic state of the entire set \( Z \) that dictates the topological blockage of information flow.

### 6.2 Moment Equivalence and Prouhet-Tarry-Escott Polynomial Relations
The Prouhet-Tarry-Escott (PTE) problem, often studied in the context of Mossinghoff polynomials, asks if there exist two disjoint multisets of integers of size \( n \) having identical \( k \)-th moments for \( 1 \le k \le m \) [cite: 22, 25, 26]. 
*   **Why G09 Fails:** A claim solving a PTE problem relies on a perfectly balanced system of polynomial equations (e.g., \( \sum x_i^k = \sum y_i^k \)). The "predictive power" or validity of the claim relies on the exact arithmetic interplay of *all* coordinates simultaneously. Isolating the "highest variance coordinate" in a multiset solving the PTE problem is mathematically meaningless because removing even a single integer shatters the moment equivalence across all powers up to \( m \). The claim is an irreducible tensor product of its coordinates.

### 6.3 Distributed Topological Invariants (Knot Theory & BSD Contexts)
In topology (e.g., Knot theory) and algebraic geometry (e.g., the Birch and Swinnerton-Dyer conjecture), claims frequently revolve around global invariants. For example, a knot invariant (like the Jones polynomial) is a property of the global embedding of a circle in 3-dimensional space [cite: 27]. 
*   **Why G09 Fails:** A knot cannot be understood by looking at a "single dominant crossing." The topology of the knot is an emergent, holistic property of every crossing point combined. If G09 attempts to "ablate" a coordinate (e.g., severing or ignoring one crossing), the topological structure instantly collapses into an unknot or an entirely different link. The signal is strictly distributed globally. In these substrates, the concept of a "highest-variance coordinate" does not exist; the invariant is inherently a macroscopic property resistant to microscopic reduction. Therefore, applying G09 projection to topological claims results in a complete conceptual misfire.

**Sources:**
1. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFXDq4Hn87Fn1Mob9x5kV-CtxIbXdNfIl_JNOeiLYXVfQNt1siAnFRT4IXozbbl9-u1CVpyWHxjyfQJMeQMeTxDYC_SxsUxwyh9pMO_sWOeeeKjBP6vlj3e6AtYYrT2wG54h3-2vJrmrzDgzkGYMOPaxxdX0B3idg==)
2. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH32pZ4MKlkCe8L8tiMoK0sid517XNwzBs-SHA4mBMBhRRhA7sviCZoKgLJATFanTA-gQ5pjA5Yaeb9MU9yJ_FDfUTXRUa4ZfbRN25KHsnd8z0iQW22ZanRF56EkBacvHKmkWYbm-v7-b_UCqoADcHZpsUK1hmYB4NZh3TrP5jZ5qwv2RMNfZ5LyKGvLu0fCVY=)
3. [repec.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5WXBuu3MD0lz9GNvsdIQfjXT18sNtd0LJFaBmTifCmx42S8KQ0K6r6OhJQ3oX8w1BvLiQOhhidSVuifmqT1pslFjnAUCO2yZMYvBNCuk9-WVR_QJXpm6D9DxZAyGlp_t4UzfPJmEtWAFJYLVufMVLxEkFbw==)
4. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG17AQ9sTKerx6fGUwQBVIr5yXdC4L9uIyDey1_OY1QDOzh03FA8NZx8HnYOUOFQNuTioHlfQBuW2LHtcvnCE-ggTY3oeubYoDqDTDX7HDyS5pxd9-GQA4bC_NxTbS7rCjQ7V2-wWrkaci1tYl24O4gMCMVK7TA)
5. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHx9Eu9IWdY81UuGvxVcSsTzpjywnUkE37BodQN5t-vXYAkInSY8Zi_BctAXm6Aee8cUyb51gZPS6jt8KCb_V-CQuUaRqfPfcwYcyYf05poEuu818BKUVmZxZUG8oKo6SrI50th2THn)
6. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPTdD7qQtCcXDtduR0xuTsfIpcrR61y80yBwOcMRU_QA_QWeBt4CfK4I3M-_qGaii9c5def4vP2JwINanYW0KbF39LREpCxOMoSEOmf333BgaQYgcwc5wxDXSoDrNc)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPgEX3E4MS5Pxu1W_HrYPG9Fmmd22T8yKRNQzMMhcEj2YWdwY34R7bXbFEh7czRmcct293eNArCbwt6RAmFrcc8HPvEHTuxCXcnBGJfXysx-BXIkLtp0Mm)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYpMXUrvR809wnxFKiEVFGWq1BnQ_QkZsRhRDle9zyVgG6_QKIa5RCe6vakGbAWqEj4akcIlpIv0Ruc67-p_0U7CO02Ib_Sya0i5fgiD2WcBuE2lGBsUh4)
9. [ahajournals.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaPzIJXnIMzZgYvk1cu6nWprWptY-f6LV2dgstQ9XzwYTWUOY-PUVq2rx2P8c3_7LY8pTS13VAnlzuKFfW9Zem81vSmEY4J4-c-mtR7gGy_VZ0Onzy6jfdGh0tm66WTptdqdJx77FE_oarBQVLAAgcsQf5gc9m)
10. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxtiJ0B7DlscnnWHZ3NhuG60L54QO1ZR7ZPGgBjvC8-azyhOf4OUVb0h0JGtlH0d98GW97_rgEHBU2UN4ldnBoRQ3qcbz9G0Po9z3AA214_6x7wFfV4H8-Jt9pmARTeH071doue3tr)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9BosVJ2xlS1GpLMYgNln2GJFjvDwaJG8_EXt-Zhvq2r5liFM2jsiT2kAlb6lEaHSSOQwxbV0SqR1BLgnkI2oQzBa__Vows7Cwv2-EXpAuWskLYNqJ)
12. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFSjymDWbiBsSvsSDVBYa5mLf5sibnmFuvx-FYWFoSqgsVrB6TLrXNH5o-bn6PLJZzmLM9tAfpOC8amWPMvuRd0gww3UTYga2dmLkXH-iaa91_aD1BL8xI-nruSiNcN)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwWMxKFY19srGQuPJC-V8zlNEGSKjc6BjBk-2ojozK4_pl4LL4SLkg1yIns1Q6ekxHdcdRlsW4lScnH2RRR3-yxxRZoL_dkfc8ONsoxpcHygr1Lu84BiRq)
14. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb5RyTPIekvVvtJgF4btYvBVyxtoOMJrRBQRgxjbhj8BV2Thww1M1f3nJcYPip8hjPMcPQLFLVi30Bo_nJRbXKEuaSDMP_Pmj2lm05N9oaLafwQNC703JAP17q6njtU1Fex54mBH3Q)
15. [copernicus.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWaBdE4TvonA2UJ4cZ1nUNgvCgafMq2jL0ECvMnP4O_pVEFWQ2aDQ74K87_nZ2rcBCsaVHnlbMK-kYUAa7VYNMYhTzACyZqwjzBK_VtW2CSAhoAovksARdTeM6kzp4xAPPokGS17yw)
16. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5YbYLFYgwOipLEF9DrUhB4_oF71_636flFkXv1N__J8I5daS5y8maj1NkBMOBryHNguLgc1zFcMElgydSDYXQvBmQ9SfEdN2emFoNJwV2gFXyotSqRYhUNzbG1jV0OjdMsu59L7TL4QMBxFPrhWRsjjYlBXtSxB-DdXbgdM0V7IfEu5vaOVRvdlkPgrFvYt3-bC_etdMulteBKAkNhfMCfR0i54j8O6uBo1wHBMyk_wKtWOszn8c70EjMZdLDoCfHxMFWlLncuOzvguucMzO5)
17. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlFFdBPjY4bZvkxDb2gCl5ZzUMLukUOJvMgAQCu6v_Ii1M_PQNepAxsnANUhe0YZScMreyZzMGsnFw6vDaaoOZrMmWSUE68KVYktrKWlvJCn0aa4OMA8Qxs-c=)
18. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFd7Pvs-iZUUPGltXy200iT6IqhNK1nPovVWC2NCnhk9Cwwg8fLNjus3T596qVGiiAd1viFGhn4fS0SBoWwOBIae9KmI3UFFU1GsdwsqtVy7fUtF4PyUntA0v2Oq0KVu4F3hZkLZH4P)
19. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4TY7t_6OQXBZH_-kNQ8M2JIrcj6qfY0vGYAegkv8t3MgKwlo3E1WV2i9JDnc7ISYjmadUXKeZfTjOpfykktYKYgF2u0qWZQOSEXjkqUj-LGvStr-CDC1WOKninA8vcG6e7ZI=)
20. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1O7woqu8rJAePNIYY6iYPItIhUWRuClKVZ4PxXNFshH-cX9bsPwB4HoS9VlFCId5CYHlmhfemxp6fSZDY290BMrsVwViwGthKqB46XCU3LpoY6jLiTKVpzYe_jNxZ35JREqYfMw==)
21. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmmoFff5U2PKeQ-d2zu5QMw0g93bo8dYmLy-0nI02dPTnBwFinaFajfhPnb1DkU8z2Nfq-5scoGm5JzKZhNJAT73kvpxJ2RvTXjwuaBrVJ66JXqdXVmjpDqSEyakIlpl8GiNFBWqqn81_vOpGF5zZ3z8pZcHPGhUqYIXeugcF7TPpKMT8v0NlLVSoZYuju4d_fw2BL9b3VThUFFkG2kpi3uofdxVE=)
22. [ams.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwlm8dje4_hTQeiY5OAgNerqzkDrTqe2BR9Zwit3GY9QcEKtHwq8rnTwaFoiV0UvzsYWAcAQ-D30iopBJPdwL0FZ28lL-qCcye_lO-PA2KTUKwFmifWAAzM-8CVQsM6-x63uqgjzEtNfILFvQQGXomBVH_A0gyQ_tLmDrAAmQNapKpSKU=)
23. [plouffe.fr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfkwnBnl3g0lDkkpMYvIVzSU18jlcOwNwVUKDZvmsZzeMOdeI9N4DLNNswrZVyu16KWFDW8nOI5E9U6Vqzh68xkBSetsAsVkqujrpxTi1YWfpfkjuNmYuNv4YyiTBZGgZ6usLFWz-qDHuhkA==)
24. [ethernet.edu.et](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErQ8TW9vIec3_iK0JUF7no0kqF9pI8SqbGjfGwGy6aY3zK4Bb3oajTBjilif6QZrEX5SWCIT1TfGHpbMnuaJq7x8rGyEOuOt7it2qFiGhVvvjDmqw79mHeAa9Gkay3I_LtTNnNJvdPTyCGVMDkBTliVCEoPT8NELfrUjZMjuo5zHC6bc9HghobLd1ZHA==)
25. [utah.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ1d-m2qpsecmr5CxHvn2tSwYEpPVJlUn33Wj9NkJt9XpjR1FEZOcqh_9i7TSu7p5y3Kgxr7Lb08pJIf59h4SYhzkHZC9pW2OIwgFO0zSvQ6-Z9EaWhkXbkiu8-gZsuZgACKaoWFAp7D-ZQAeVWRzo)
26. [polito.it](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHi4YTX07CLy16LKKhXVdbZs-hFzFTrQMrNfSGTqagHGiSBoB-QpEzbwqsy72VnL-b9OVJ93COGkjHoG0rT0j_569rFsDE_8ZMCRIVzrVFQKi5VbLyZyVo0ZXJ71BXtQoBCEFFvtuRAM_Day1q-xUPBtxuT0bk80mFD7GahYggMi5IiWczZRq1Fvv8j)
27. [carmamaths.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGd3VniOFb2hfPIsxgl0x5GBH_76GaTxdYS8Yfje8fasNKTBn89YKZ7ixslCbjLujtOPfEAE51Vyl2aGwI5Y1dJb48lv-SPz2bRvyQPuouPGScXVAkgiqdoR8PiXRzYrKFoIaRVEkYwLH9PbHokEQ==)


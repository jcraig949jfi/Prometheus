# Prompt 04: G04 Survivor-Tightening — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chc3NElXYXA2SUtmU1o5TW9QbE1IXzRBdxIXNzRJV2FwNklLZlNaOU1vUGxNSF80QXc
**Elapsed:** 213s

---

# Advanced Methodologies in Empirical Conjecture Testing: Bound-Tightening, Parameter-Band Restriction, and Threshold-Search

**Key Points**
*   **Bound-tightening** rigorously tests the robustness of empirical claims by evaluating whether an observed effect survives under strictly constricted parameter bands. 
*   **The evolution of concentration inequalities**—from Hoeffding to empirical-Bernstein and exchangeable-variable bounds—provides a structured taxonomy for assessing the "tightness" of numerical claims. 
*   **Information-optimal band selection** frames threshold searching as a Thresholding Bandit Problem (TBP), utilizing active learning to maximize information gain about a claim's true threshold. 
*   **Multi-band strategies** leverage sequential testing to sweep across parameter bands, identifying phase transitions and optimal threshold boundaries.
*   **Synthetic Null Calibration (SNC)** is critical to prevent performative tightening—a phenomenon where arbitrary thresholds falsely promote claims due to natural clustering in the underlying data distribution. 
*   **Phase diagrams**, generated through cross-plugin interactions (e.g., contrast testing combined with threshold tightening), offer a multidimensional, robust verification of empirical phenomena.

The evaluation of empirical conjectures relies heavily on stress-testing statistical claims. When a claim suggests that a specific effect—such as Salem-class moderation—holds at a certain parameter threshold, researchers must ask: *Is this threshold a fundamental boundary of the effect, or is it an artifact of the data distribution?* Bound-tightening addresses this by deliberately shrinking the parameter band or raising the threshold to see if the claim "survives." While this sounds straightforward, tightening a bound arbitrarily can lead to false positives (if the data naturally clumps around the new threshold) or false negatives (if the threshold is pushed beyond the physical limits of the effect). 

This report delves into the statistical and algorithmic machinery required to optimize this process. We explore how modern probability theory classifies the "tightness" of bounds, how machine learning techniques like multi-armed bandits can optimally search for the correct threshold, and how synthetic control data can calibrate these tests to prevent false discoveries. By integrating these advanced methodologies, we propose a comprehensive design for a next-generation automated conjecture-testing loader.

***

## 1. The Strong-vs-Weak Bound Ladder

In empirical conjecture testing, a claim's robustness is frequently evaluated by the tightness of the mathematical bounds that govern it. Tightening a numerical bound involves moving from a "weak" or conservative inequality to a "strong," adaptive, or specialized inequality that better captures the true behavior of the data. Surveying the published literature from 2024 to 2026 reveals three prominent taxonomies for bound tightening, spanning independent variables, matrix representations, and adaptive sampling.

### Taxonomy 1: The Exchangeability and Variance Ladder (Hoeffding $\to$ Bernstein $\to$ Exchangeable Bernstein)
The most fundamental taxonomy in concentration inequalities involves moving from bounds that rely solely on the range of random variables to those that incorporate variance, and finally, to those that relax the assumption of independent and identically distributed (i.i.d.) data.

1.  **Hoeffding's Inequality (Weak/Conservative):** Assumes bounded random variables $X_i \in [a, b]$ and provides an exponential tail bound based purely on this range. It is highly conservative because it assumes the worst-case variance [cite: 1, 2].
2.  **Bernstein's Inequality (Stronger/Variance-Aware):** Tightens Hoeffding's bound by incorporating the true variance $\sigma^2$ of the variables. In settings where the distribution has low variance, Bernstein provides a significantly tighter bound [cite: 1, 2].
3.  **Exchangeable Hoeffding/Bernstein (Strongest/Structural):** Recent advancements by Foygel Barber (2024/2025) extend these inequalities to weighted sums of exchangeable random variables [cite: 2, 3]. The i.i.d. setting is a strictly stronger condition; by relaxing this to exchangeability (meaning the joint distribution is invariant to permutations), these bounds provide a unified view that tightens empirical evaluation in complex sampling designs, such as permutation tests and exchangeable bootstrap methods [cite: 4, 5]. 

### Taxonomy 2: The Self-Normalized and Martingale Ladder (Azuma-Hoeffding $\to$ Doob Martingale Variance $\to$ Empirical Bernstein)
When data is collected sequentially or when the true variance is unknown (as is typical in empirical conjecture testing), the bound ladder must adapt to empirical estimates.

1.  **Azuma-Hoeffding (Weak/Sequential):** Applies to martingales with bounded increments, providing a baseline concentration but suffering from the same worst-case variance bloat as standard Hoeffding [cite: 6].
2.  **Martingale-Variance Inequalities (Stronger/Adaptive):** Incorporates the predictable quadratic variation (the sum of conditional variances). Chugg et al. (2024) demonstrate that by analyzing the Doob-martingale of a norm, one can achieve a dimension-free Bernstein bound [cite: 6].
3.  **Empirical Bernstein and Self-Normalized Bounds (Strongest/Data-Driven):** Because the true variance is rarely known, Empirical Bernstein bounds substitute the sample variance. Recent work on self-normalized martingales establishes sharp, time-uniform empirical Bernstein inequalities that tightly adapt to the realized variance of the sequence, even for vector-valued and heavy-tailed data [cite: 7, 8]. These are classified as "sharp" because the first-order deviation asymptotically matches the exact matrix Bernstein inequality without requiring prior knowledge of the variance [cite: 7].

### Taxonomy 3: The Dimensionality Ladder (Scalar $\to$ Matrix $\to$ Dimension-Free Banach Spaces)
In modern systems, claims often involve multidimensional parameters or matrices (e.g., covariance matrices of user embeddings).

1.  **Scalar Concentration (Weak/1D):** Traditional bounds applied independently to each dimension, requiring union bounds that scale poorly (e.g., $\log d$ factors).
2.  **Matrix Bernstein (Stronger/Spectral):** Tightens the bound by operating on the maximum eigenvalue of symmetric random matrices, adapting to the spectral variance rather than the trace [cite: 7].
3.  **Dimension-Free and Smooth Banach Space Bounds (Strongest/Universal):** Recent work by Martinez-Taboada and Ramdas (2024), as well as Chugg et al. (2025), derive sharp empirical Bernstein inequalities in smooth Banach spaces and dimension-free environments, allowing threshold tests on complex vector spaces without the geometric penalties of traditional bounds [cite: 7, 9].

In the context of the `G04 SURVIVOR-TIGHTENING` loader, promoting a claim through this ladder means successfully replacing a worst-case assumption (Hoeffding) with an empirical-variance assumption (Empirical Bernstein), and ensuring the threshold survives the tighter restriction.

## 2. Information-Optimal Band Selection

The current v1 loader utilizes hardcoded bands, such as $M \in [1.30, 1.50]$ at a threshold of $M=1.40$. This approach is epistemologically fragile; it risks evaluating bands that are either too wide to be informative or too narrow to capture the signal. To formalize "where to tighten," we must transition to an information-optimal methodology anchored in Sequential Testing and Thresholding Bandit Problems (TBP).

### The Thresholding Bandit Framework
In published literature (2024-2025), band selection is optimally modeled as a Thresholding Bandit Problem. In a TBP, the objective is not to maximize cumulative reward, but rather to identify all arms (parameter bands) whose true mean (survival probability of the claim) exceeds a predefined threshold $\tau$, using a limited sampling budget [cite: 10]. 

Feng et al. (2024, 2025) introduce the **Budgeted Thresholding Contextual Multi-Armed Bandit (BT-CMAB)**. This framework simplifies complex online decision-making into a threshold identification task, dramatically reducing sample complexity compared to traditional reward-maximization [cite: 11]. In this framework, regret is defined by the gap between the expected outcome at the chosen band and the predefined target threshold [cite: 12, 13].

### Expected Information Gain (EIG) for Band Ranking
To select the optimal band for tightening, the v2 loader must rank candidate bands by their **Expected Information Gain (EIG)** regarding the parent claim's true tightness. We can frame this through Bayesian Active Learning [cite: 14]. 

1.  **Surrogate Modeling:** We model the survival probability $S(b)$ across the continuous parameter space $b \in \mathcal{B}$ using a Gaussian Process (GP). The GP provides both a mean prediction $\mu(b)$ and an uncertainty estimate $\sigma(b)$ for the survival of the claim at any given band.
2.  **Acquisition Function:** The loader utilizes an information-theoretic acquisition function. Following recent advancements in Guided-Diffusion Bayesian Optimization [cite: 15], we seek the band that maximizes the reduction in entropy about the location of the true boundary. 
3.  **Optimization:** The algorithm queries the band $b^*$ that maximizes the Expected Improvement or the Information Gain:
    $$ b^* = \arg\max_{b \in \mathcal{B}} \text{EIG}(b) = \arg\max_{b} \left( H(P(\text{survival})) - \mathbb{E}_{y|b}[H(P(\text{survival} | y, b))] \right) $$
    where $H$ is the Shannon entropy. 

By employing this active learning threshold search, the loader dynamically identifies the exact parameter band where the claim transitions from "surviving" to "failing," avoiding the inefficiency and arbitrariness of hardcoded intervals.

## 3. Multi-Band Strategies

Relying on a single tightened band exposes the evaluation to localized data anomalies. A robust v2 loader must employ a Multi-Band Strategy, executing a sweep across $K$ bands to derive both per-band verdicts and a global meta-verdict. 

### Sweeping $K$ Bands via Fixed-Budget Exploration
To sweep $K$ candidate bands without exhausting computational or statistical budgets, we rely on the **Fixed Budget Thresholding Bandit** setting [cite: 10, 16]. Thuot et al. (2024/2025) demonstrate that optimal sampling efforts in such spaces must be inversely proportional to the magnitude of the difference between the band's mean and the threshold [cite: 17]. 

The loader will allocate its validation budget $T$ across $K$ contiguous, non-overlapping bands (e.g., $B_1 = [1.30, 1.35], B_2 = [1.35, 1.40], \dots$). Using a Successive Rejects or Track-and-Stop algorithm variant [cite: 17], the loader iteratively samples objects within these bands, discarding bands that definitively pass or fail the survival criteria, and concentrating remaining computational budget on the "boundary" bands where the survival status is highly uncertain.

### Detecting "The Right Band" (Maximal Survival Difference)
To identify the specific band where the survival difference is maximal (the true inflection point of the effect), we utilize **Piecewise Constant Bandit** and **Change-Point Detection** methodologies. 

Recent theoretical work establishes that finding this optimal band requires comparing unknown reward distributions across the action space to locate a change point [cite: 18]. The loader implements a *Binary Search with Backtracking* over the parameter space [cite: 18]. By actively sampling the leftmost, middle, and rightmost points of a parameter interval, the algorithm can detect the steepest gradient in the survival probability function, effectively isolating the exact parameter threshold that governs the Salem-class moderation effect.

### Global Meta-Verdict Logic
Once the $K$ bands are evaluated, the loader aggregates the results into a global meta-verdict:
*   **Robust Universal Survival:** The claim survives across a contiguous block of aggressively tightened bands.
*   **Localized Phenomenon:** The claim only survives in $B_k$, and rapidly decays in $B_{k-1}$ and $B_{k+1}$.
*   **Arbitrary Thresholding:** The survival rate is flat across all $K$ bands, indicating that the original threshold $M=1.40$ holds no special mathematical or empirical significance.

## 4. Contrarian — When Tightening is Performative

A critical vulnerability in bound-tightening is **Performative Tightening**. If the natural distribution of the underlying data is heavily clustered near the tightened threshold (e.g., if 90% of all Salem-class objects naturally possess $M \in [1.30, 1.50]$), the tightened bound will appear to survive robustly. However, this survival is an artifact of the base rate, not an indicator of a strict causal or structural boundary. The tightening falsely promotes the claim.

### Synthetic Null Calibration (SNC)
To detect and penalize performative tightening, we must introduce a "null-tightening" calibration. Published literature from 2024 to 2026 heavily emphasizes the use of synthetic nulls to calibrate classifiers and prevent false discoveries due to structural data artifacts, such as survival bias and over-clustering.

Zhou (2026) introduced **Synthetic Null Calibration (SNC)** to resolve Simpson's paradox in behavioral curves, where aggregate dynamics severely distort individual parameters [cite: 19, 20]. Zhou demonstrated that uncalibrated classifiers yield false positive rates as high as 32% purely due to the structural distribution of the data [cite: 19]. The SNC protocol operates in three steps, which we adapt for the G04 Loader:
1.  **Generate Synthetic Nulls:** Create a synthetic dataset that perfectly mimics the underlying marginal distribution (e.g., the clustering of $M$ values) but explicitly breaks the structural link to the effect being tested (the Salem moderation) [cite: 19, 20]. This aligns with the "Knockoff Features" methodology by DenAdel et al. (2025), where augmented "fake" variables go through the exact same analytic pipeline as negative controls [cite: 21]. Similarly, the DIOgene framework (2024) breaks links by randomly unmatching profiles to calibrate model expectations [cite: 22].
2.  **Apply Identical Tightening Pipeline:** The exact same tightening loader (e.g., restricting to $M \in [1.30, 1.50]$) is applied to both the true data and the synthetic null data of the exact same *size* [cite: 19, 20].
3.  **Compare and Bound:** Calculate the raw survival rate on the real data and the false positive (FP) survival rate on the synthetic nulls. The genuine signal is bounded by the *Excess Rate* ($Raw - FP$) [cite: 19, 20].

If the survival rate of the tightened band on the true data is 0.3766, but the synthetic null dataset (which has the same density of items in $[1.30, 1.50]$ but randomized outcomes) yields a survival rate of 0.3500, the tightening is performative. The high survival is merely an artifact of the data density in that band.

## 5. v2 Loader Design: `g04_survivor_tightening_v2`

Based on the preceding theoretical frameworks, we specify the concrete architecture for the G04 v2 loader.

### A. Information-Optimal Band Selection Module
*   **Input:** A parent claim with parameter space $\mathcal{B}$.
*   **Mechanism:** Initializes a Gaussian Process over $\mathcal{B}$. Executes a sequence of queries using the Expected Information Gain (EIG) acquisition function to identify the thresholding boundary.
*   **Output:** An information-optimal band $B_{opt}$ that tightly bounds the inflection point of the claim's survival.

### B. Null-Tightening Calibration Module
*   **Mechanism:** Implements Synthetic Null Calibration (SNC). 
    *   Generates a synthetic knockoff dataset $D_{null}$ that preserves the covariate distribution of the original dataset $D_{true}$ but breaks the target variable dependency.
    *   Samples subsets of identical size $N$ from both $D_{true}$ and $D_{null}$ falling within $B_{opt}$.
*   **Metric:** Computes $\Delta_{survival} = Survival(D_{true}) - Survival(D_{null})$.
*   **Threshold:** Requires $\Delta_{survival} > \tau_{sig}$ (where $\tau_{sig}$ is derived from an Empirical Bernstein confidence sequence) to validate the tightening.

### C. Execution Loop & Multi-Band Sweep
*   The loader discretizes the parameter space around $B_{opt}$ into $K$ bands.
*   Runs a Fixed Budget Thresholding Bandit algorithm to allocate compute efficiently across the $K$ bands, yielding a survival vector $[s_1, s_2, \dots, s_K]$.

### D. New Kill Patterns (Expected Kill Patterns)
The v2 loader introduces highly specific kill patterns that trigger if the tightened bound fails structural integrity tests:

1.  `strict_threshold_violation`: The standard kill pattern. The optimal tightened bound $B_{opt}$ causes the claim to fail on objects it previously survived.
2.  `tightening_is_performative`: Triggers when the SNC module returns $\Delta_{survival} \approx 0$. The loader annotates: *"Tightened survival rate ($X\%$) is statistically indistinguishable from synthetic null rate ($Y\%$). Bound tightness is an artifact of underlying covariate density."*
3.  `band_choice_arbitrary`: Triggers when the variance of the survival vector across the $K$ bands is near zero. The loader annotates: *"Claim survival is invariant to threshold tightening across $[B_{min}, B_{max}]$. The chosen threshold represents no actual structural boundary."*
4.  `effect_only_at_specific_band`: Triggers when survival spikes in $B_k$ but collapses in $B_{k-1}$ and $B_{k+1}$. The loader annotates: *"Claim is highly localized to band $B_k$; it is not a general property bounded by a threshold, but a localized resonance."*

## 6. Cross-Plugin Interaction: The Joint G02 + G04 Phase Diagram

Currently, G02 (Contrast) and G04 (Tightening) operate sequentially, emitting isolated verdicts. However, contrast and thresholding are mathematically coupled; the magnitude of a contrast effect (G02) is a direct function of the operative threshold (G04). By fusing them, we transition from single-point hypothesis testing to **Phase Space Mapping**.

### Joint Loader Architecture
The `g02_g04_joint_phase_mapper` simultaneously varies the contrast intensity ($\Delta X$) and the threshold parameter ($M$). 
*   **X-Axis (G02):** Contrast delta (e.g., difference between Salem moderation and baseline).
*   **Y-Axis (G04):** Parameter threshold band (e.g., $M$ varying from 1.00 to 2.00).
*   **Z-Axis (Signal):** The Empirical Bernstein-adjusted statistical significance of the effect.

### Emitting a Phase Diagram
Instead of outputting "PROMOTED" or "KILLED", the joint loader outputs a 2D topological map of the claim's validity. 
*   **Stable Regions (The "Solid" Phase):** Areas where the contrast is high and robust across multiple tightened thresholds. 
*   **Decay Gradients (The "Liquid" Phase):** Regions where tightening the threshold smoothly degrades the contrast effect, allowing researchers to quantify the exact elasticity of the claim.
*   **Null Regions (The "Gas" Phase):** Areas where the effect dissipates entirely. 

By applying Gaussian Process regression over this 2D space, the loader identifies the **Critical Boundary**—the exact contour line in the parameter space where the empirical conjecture breaks down. This phase diagram provides researchers with a holistic, irrefutable geometric proof of the claim's boundaries, vastly superseding the binary pass/fail paradigm of v1 testing loaders. 

***
*In summary, transitioning from G04 v1 to v2 requires abandoning arbitrary hardcoded bounds in favor of information-optimal thresholding bandits, fortified by synthetic null calibration. By understanding where the bound sits on the theoretical tightness ladder and projecting its interplay with contrast testing into a phase diagram, the automated conjecture-testing suite becomes a mathematically rigorous engine for empirical truth.*

**Sources:**
1. [iith.ac.in](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1Cz95IIlUlbgsRYStXZDeCZNkao1Hmf__fqwoZEv5qIkUb7w7-cHpx82OJffJk-99PYGFfcX2f7yShBZj7hF1agd4UqD86gbFhgwLi9A9fn8iraxupiHjv5fj40P0VRGxyn7buJqlG5q-NJ6cbMq4jvtXq4aSNTzcJRNW5abECrAMhsyPIul1VjYTwQ==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCybDDfO475mj3MKVX5KyHWf9p0rval3e97bwNsiItI8w_DF6tHGshvqKbTq2Xb0tzQRsnIR5sAuxSAERuWfnhWNnVnkjWXISA8onldXHf1ng1cYSVtoyKRw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuiBq35uD_HXBU4jG_3UsLiS5RRrsUIbO6QdD96HzHjsCbEm3PynrNKknHXfkeRqqjbY2x4PWOiNV-3EIFyMYPD6ZFY5Xyi8BCRJb3DfqeTp0b08RJfw==)
4. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE73_2gw-S0f4wNMdiCIopGIsofj6k4m-f8e1fgNegZ7Sa8biRTsPe7pJ-JNFLcQHU_HYMjuxGXYUpGV1UiIsOLB8-TZJdU61vj-ZX4vhdbz9Cs8m3Wc0AVFsvBy4FddBjxLTuTcCoFqYO7fF0dSSf_hMBhZ-4fwcgYZnT0uf_UJv9EJZDoBU6G7o2LMLzC-w8x_x_isJjpgxlJMmqTmQxYBSZ1uOvNkZtZiwJJk5OJBzodhxMlpOsUAKEDqs-zjkfaaqktJSnpyv5JRM7AHUN010OePpb1jfwuiGKil5psHHg5iYvAWIK4xriMj7Tby0CSZ8z3AObxOYF8M7g=)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE92ckCAgOKL6sK0fuWTBG9ljddyR6G6YeRwlZj0c5esTEfmybC0xhqvxgkhOAuUSGK7hzQKgPg2jlhia-cYHYVGg6o9N5G3KJJ6lOECbZwI8lPMafEgw==)
6. [benchugg.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFx_DJNnyjaMlwd9cUleZJZz3AZTwYK9KQE_vId0sQRVidVdlnt_6byANrzQ4zxTy8e1RjcVnhE1q4mLcbv22X3dnrkVmdAiPbBZWo84NL5PIc_7dGiKCrp4l98RJXjTrv0ShkgjpffIP4PcWHW)
7. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhkae3IP5qTc4Jdr0-CpHaDw2WxTtce25p0zbP29O2wSmIrAvY1nNI9nvXGefMBvDhn2dNhGzuwX-zyqkDivNZm6Tm-XXrYIwS3QYN5lX_kkmBLeLSt6T2KQ==)
8. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcL07Jr4moMRS1AX2extN6whqMbub7HUXCgsbuYv5P6rSRic-DOKOGIrT4jtQgaXeFVEfyavZtP6ejqGqGCyDI-OPvvGpCbIT4q7emLpdVQL7IuYxtFsONksqBaAcrWhKBHbmeE_eQSkhlOLtYghbOhzxp4PGEQ4YMEOlX)
9. [google.co.cr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz_2MqnpeAu8vnUYMtUJ1F3UxVQfXIAOYFT5iLDTTN4kGxqT3rbRVKqwFFfIwgs9TmHTvrUQv5Onux1P4N2UaYiDaPh5YLBhgyDCPX-sFUTS0LLn8rPYhmzuGRQvgtGmF0JlKuuIOb5HeaUTTIP6W--LVnOg==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGq1W8gfUeVWrUE2Y8q3vdr5Vz6P7KH4F1xFquFgS04XKLBzWLQ3iyrUDkAt62z9QyNZinf1W0OecfoA-KZcgtJqyOw89nLKtTjRwWAkx47Gdo8PHSqZX9jBw==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG99yusgXZNR1fwkcJOq6OmKC3dFZ2KRaHEF3npV89HErFszv8xQBzyk6yG3R8fSALC-Fe_2ZZlQH171DbxL2_mXCTAxuw550gD8giZ1nd0vCHlGzXB7DhafQ==)
12. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-cNHnQi8FH6yz9ARoSOmXuiPBUammCo6uzGpuaxGrlHQ1T2yO7ge-XK3xJEjjr3UKoN_45CxT0iLQSYnI3vY6S2MYQ2Lp7RYXhmHQ3rWqjwsh-m7cUlbwFQKb4awHXtxyGNRc7Clbt7RJ4yFKA6vxH0lBPijh9YQVLnHFog==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-wSao7SI6G2NT1gWmyUkyyFd5Bv01mMxlRIJZvCDATU3ju3Eq2cqc61Nj2M05AVO9RfoSrdEYRpu3HZLq-T5-uPjXLK7FMCYvfUlQsqNjnjE_OMyyWUQ=)
14. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeea7p0FSCr48Vg3zS-EinmbjKAEshPpzSrUWRrg9dIhpwFyQVJXrnYOl98mSxybOWSlyYrt--4OgnIn6o1xXYVTtyLHU6n8j7b_GFeDmeTHh98gnd5GkU3x7CIDsCBDjZqFmwfrS2wtQX-C1xCas5gjbMiEWKza_-xDGhXgSDdFjA1Sn14MGA3hcCDLG9JxsOOLMnKpx3hufK8MR2D6cY4HsPMFOFMmM7ug==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEmuFWhXpKethUIvcmvP978Vm5lUUCSu9nCbogAxG0z17lan1WOZkdytjBQlXAxxbkJrnmoTzCr9d3zV9hI7CxmeADV4-gLDdjqn0PW43osJQwbDKqRlSsFzA==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGT9AnFT5BCWdFTTSZjRQiuHxxh7_ZcBQ6E9JF9r8KbcTcR0TdjkEHSbMa-RIavvqn7LoO_Dek5H5wQ50iYTgqJacnqcLiHz8t7IIjaSG-S77EQaAhXxQ==)
17. [icml.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5Kku1-ssU3BzKfWoKqqrduyQLOs2rbqaODFCaTvjaySBdcFnTgy6kgSV6W73e6ilng8PD3otscZMAkzXlOZuQf9DfEU9nvIlfcDeANAMwUalmenreE9CF8VeotlysOA==)
18. [imperial.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3hNZ9VB1vA3F6HZdTEYA6alqGzQH2s3O158a9QYRSx0E8vQRJBAFBBPjK9R4BJ1f13bqc5_bM7Kg__mJYGYPffLoGCgnQ3zNvcRTtXPV1xifDGfYeKmIlZQVBjNFLgzFj05EefckKjCnZYscs3w7wWSixMUU=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8iI4W1HeCPutj1UOsX5bY4wlD1b0qhh2vp1dWI2xtCgXry1ri3wzrQoXVrXETRLp7ABfLIryE4_XZqnSW3Bw1hVbO92ei41GCnSdvjCDXr-9LnTf1_BH3Bw==)
20. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjOL4qcXZcAVQWOzdSu8q8H_wV3oDog_-3OyPCuYeyT1QBTHD_Jvmu7uruH-WLJEhG5fVXX7KvbWEdx6bEMD_YV-4rNEVNNYb63o4t3f18XaC5UEfFRCKlTTCAR0GUoMKkT8kY4FInDg9ras3pRbc2tjvYx8CwhBDXOBWzwBKik6hdCD_sbmTMiZjYyPyNeExxpa9H5G3VAzeOe1-k8QzikAbdPE3cWDUFCTh41zQTRbvUvROoovVay_d75Lu83pkY-R0pA88JfnC1Nvo=)
21. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh2M1Na8pJREohLMXsYpSFSponovx8nTgq76D6djO0oZW6aLePyBUkNXMHqc8w1dJZNqszfbCFAaIlGdKS92x_mYPM42ceov6uz6EZZlADoshKU67Qszh4m8s=)
22. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHfoJC8pRE3wbdtd5B3hKaOiTI0UEp8NtWkEmEWIcwafBVP29rzZKOUQqQC6Qe8OKhPa4r8YOG5uehfTD6AgtD_KjBKwLNDngrA__fB8fxpva2yH1G8C1eSfk62AZP5fEJtmj_jHqyKWGVXc4ZFjyoayt3MMDfxB-LveQ==)


# Prompt 08: G10 Boundary — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdJWVFXYXBYQUs0YXNqTWNQLW9XMTBBYxIXSVlRV2FwWEFLNGFzak1jUC1vVzEwQWM
**Elapsed:** 213s

---

# Advanced Diagnostic Frameworks for Phase-Transition Detection and Multi-Scale Boundary Inference

**Key Points**
*   **Methodological Vulnerability**: The current G10 loader relies on a simplistic $\max/\operatorname{mean}$ smoothness statistic, which is highly sensitive to sample size ($N$), discretization artifacts, and local variance wash-out, resulting in missed phase transitions (such as the M=1.26 ITER-18 event).
*   **State-of-the-Art Alternatives**: Recent advances (2024–2026) in Topological Data Analysis (Persistent Homology), Bayesian Online Change-Point Detection (BOCPD), and Learning by Confusion provide robust, scale-invariant paradigms for phase transition identification. 
*   **Multi-Scale Necessity**: Boundaries in complex catalogs are rarely confined to a single scale. Transitioning to a multi-scale Wavelet Transform Modulus Maxima (WTMM) framework allows for the distinction between scale-invariant structural boundaries and scale-specific anomalies.
*   **Projection Epistemology**: Many "sharp boundaries" or "cliffs" observed in statistical projections are artifacts of dimensionality reduction. The true value of the G10 loader lies in its capacity to identify which specific geometric projections force these emergent phase transitions.

**Executive Summary**
This report evaluates the current v1 G10 boundary detection loader (`g10_lehmer_threshold_sweep`) and proposes a comprehensive architectural and mathematical upgrade to v2. The existing smoothness ratio ($6.71$ at threshold $3.0$) successfully calibrated the Salem cluster boundary but exhibited a false negative at the M=1.26 ITER-18 phase transition. Through an analysis of 2024–2026 literature, this report outlines the theoretical limitations of the $\max/\operatorname{mean}$ statistic, introduces three advanced alternatives (BOCPD, bottleneck distance from persistent homology, and WTMM), and provides a concrete specification for a multi-scale v2 loader. Furthermore, the report explores the philosophical implications of instrument validation and the contrarian view of phase transitions as projection artifacts.

**Scope and Methodology**
The analysis integrates recent breakthroughs in statistical physics, topological data analysis, and machine learning. Methodologies are evaluated based on their theoretical rigor, empirical lift, and computational tractability within the context of automated scientific catalog data ingestion. The report culminates in a detailed architectural specification for the v2 loader, complete with novel kill patterns and multi-scale scaling parameters.

***

## 1. Phase-Transition Detection Methods (2024–2026)

The identification of phase transitions in complex datasets has evolved significantly beyond traditional statistical physics metrics (e.g., Binder cumulants, specific heat divergence, and finite-size scaling). In the period spanning 2024 to 2026, researchers have increasingly hybridized pure mathematics with machine learning to identify structural breaks and topological shifts in high-dimensional state spaces. The failure of the current `g10_lehmer_threshold_sweep` to detect the M=1.26 ITER-18 phase transition highlights the need for methods that are sensitive to local topological or probabilistic shifts rather than global variance ratios.

### 1.1 Topological Data Analysis (TDA) and Persistent Homology
Topological Data Analysis, specifically persistent homology, tracks the birth and death of topological features (connected components, holes, voids) across a parameter sweep (filtration). Recent literature has demonstrated the efficacy of persistent homology in detecting phase transitions in physical systems. For instance, in 2025, researchers applied TDA to pure SU(3) lattice gauge theory, revealing that Betti curves (tracking homology group ranks) can robustly capture signals of electromagnetic dualities and clearly distinguish between first- and second-order phase transitions [cite: 1]. The geometric structures detected by persistent homology undergo qualitative changes near phase transitions [cite: 1].

Furthermore, the introduction of "Quantum Barcodes" in 2025 establishes that phase transitions manifest as significant discontinuities in persistent homology features, specifically detectable through the persistent Dirac operator spectrum [cite: 2, 3]. By mapping states to a "state cloud," this method isolates topological phase shifts without requiring prior knowledge of the local order parameters [cite: 2]. 

### 1.2 Bayesian Online Change-Point Detection (BOCPD)
Bayesian Online Change-Point Detection algorithms evaluate the posterior probability of a regime shift in real-time or sequence-time data. Rather than looking at global aggregates, BOCPD calculates the run-length $r_t$ (the number of steps since the last change point) and updates this distribution sequentially as new data arrives [cite: 4, 5]. Recent 2024–2026 iterations have enhanced BOCPD to handle highly complex environments. For instance, the BAPR (Bayesian Amnesic Piecewise-Robust) framework unifies BOCD with reinforcement learning to detect abrupt regime changes, characterizing a sharp "phase transition" boundary between stable environments and structural breaks [cite: 6]. 

Another 2026 study applied BOCPD alongside network models to predict the epidemic transmission phase transition of mpox, using the method to quantify subtle fluctuations in prediction errors prior to massive topological perturbations [cite: 7]. In Gaussian processes, a "plug-and-play" BOCPD variant introduced in 2024 deals seamlessly with arbitrary changes in both the mean and variance of 1d-Gaussian processes [cite: 8].

### 1.3 Learning by Confusion (LBC)
Learning by Confusion is a sophisticated, unsupervised machine learning scheme for phase transition detection that has seen extensive refinement between 2024 and 2026 [cite: 9]. The method involves training a neural network (often a Convolutional Neural Network) to perform binary or multi-class classification on the dataset, systematically sweeping a hypothesized phase boundary parameter [cite: 10, 11]. When the hypothesized boundary aligns with the true phase transition, the network's classification accuracy exhibits a distinct "W" shape or a sharp peak, signaling optimal data separation [cite: 10]. Recent advances have generalized LBC from binary classifiers to ternary networks to detect regions with multiple phase boundaries [cite: 12, 13], and applied it successfully to complex systems like the two-dimensional Holstein model to detect charge density wave orders [cite: 11].

### 1.4 Addressing the M=1.26 ITER-18 False Negative
The current `smoothness_ratio` (which relies on the ratio of the maximum first difference to the mean first difference) missed the M=1.26 ITER-18 phase transition. This failure likely occurred because the transition at M=1.26 was an *informational* or *topological* phase shift, rather than a massive disruption in the amplitude of the first derivative. If the baseline data variance (the denominator) was high due to systemic noise, a localized structural break would not produce a $\max(|first\_diff|)$ large enough to exceed the 3.0 threshold.

**Which method would catch it?**
**Persistent Homology (TDA)** would be the most capable of catching the M=1.26 transition. While the $\max/\operatorname{mean}$ ratio collapses geometry into a single scaler, TDA constructs a Vietoris-Rips or cubical complex and monitors the persistent Betti numbers ($\beta_0, \beta_1, \beta_2$) over the parameter $M$ [cite: 1]. Even if the absolute Euclidean distance between adjacent data points at M=1.26 is small (yielding a low first difference), a topological phase transition alters the global connectivity of the manifold. Persistent homology captures this through the sudden birth or death of multi-scale "holes" in the state space [cite: 14], identifying the transition cleanly prior to any catastrophic variance spike.

***

## 2. Alternatives to the Max/Mean Ratio Statistic

The current statistic, $S_M = \frac{\max |\Delta x_i|}{\frac{1}{N}\sum |\Delta x_i|}$, is a theoretically fragile instrument. From a statistical perspective, if the differences $\Delta x_i$ are drawn from an exponential or half-normal distribution (indicative of smooth but noisy degradation), the expected value of the maximum grows proportionally to $\log(N)$ or $\sqrt{\log(N)}$. Consequently, the threshold $3.0$ is discretization-dependent: as the resolution of the sweep increases (larger $N$), the expected ratio naturally inflates, leading to an asymptotic certainty of false positive "sharp boundaries." Furthermore, on very small $N$ (e.g., the current 8 steps), it is highly susceptible to localized variance artifacts.

To correct this, we propose three robust, state-of-the-art alternative statistics.

### 2.1 Alternative A: Bayesian Change-Point Inference (BOCPD)
**Mechanism:** Instead of calculating a brittle, global aggregate, BOCPD evaluates the local hazard function. Let $r_t$ be the "run length" at step $t$ of the threshold sweep. The algorithm computes the joint distribution $P(r_t, x_{1:t})$ and yields the posterior probability of a structural break at any given parameter $M$ [cite: 4, 5]. We can define the boundary statistic as the maximum posterior probability of a change point: $S_{BOCPD} = \max_M P(r_M = 0 | x_{1:N})$. 

**Primary Source (2024-2026):** "Plug-and-Play Bayesian Online Change-Point Detection in Gaussian Processes" (2024) [cite: 8] and "Fine-grained time series data... Bayesian online change detection" (2025) [cite: 4].

**Empirical Lift:** High. BOCPD inherently regularizes against noise by maintaining a probabilistic belief state. It natively handles heteroskedasticity (changes in variance over the sweep) and correctly discounts uniform noise [cite: 8]. This provides a tremendous empirical lift by delivering a true confidence interval for the boundary rather than an arbitrary 3.0 threshold, eliminating false positives caused by isolated outliers.

### 2.2 Alternative B: Bottleneck Distance from Persistent Homology
**Mechanism:** Treat the survival curve or the output of the parameter sweep as a 1D or pseudo-2D point cloud. We apply a filtration (e.g., lower-star filtration) and compute the persistence diagram $D_M$ tracking the topological features. To detect a boundary, we compute the **Bottleneck Distance** $d_B(D_{M}, D_{M+\Delta})$ between adjacent persistence diagrams. The bottleneck distance is defined as the infimum over all bijections between two diagrams of the supremum of the $L_\infty$ distance between matched points [cite: 15]. A phase transition is flagged when $d_B$ exceeds a normalized threshold based on the Wasserstein metric of the preceding stable regime.

**Primary Source (2024-2026):** "Computing the Bottleneck Distance between Persistent Homology Transforms" (2026) [cite: 15, 16], which improves the algorithmic complexity of bottleneck integration to $\tilde{O}(n^5)$ for 3D and $\tilde{O}(n^3)$ for 2D scenarios. 

**Empirical Lift:** Very High. The bottleneck distance is mathematically proven to be stable under bounded perturbations (the Stability Theorem of Persistent Homology). Therefore, it is entirely immune to the discretization-dependent scaling that plagues the $\max/\operatorname{mean}$ ratio. It will provide unparalleled lift in distinguishing between a highly noisy but structurally consistent degradation ("smooth") versus a true topological rupture ("cliff").

### 2.3 Alternative C: Wavelet-Based Singularity Detection (WTMM)
**Mechanism:** The Wavelet Transform Modulus Maxima (WTMM) method is utilized to detect the Hölder exponent (singularity strength) of a signal across multiple scales. By convoluting the parameter sweep data with a wavelet (e.g., a derivative of a Gaussian) at varying scales, WTMM tracks the local maxima of the transform coefficients [cite: 17, 18]. These maxima form "skeleton lines" pointing toward singularities. The Hölder exponent $h(t)$ dictates the nature of the boundary: $h < 1$ indicates a sharp cliff (singularity), while $h \geq 1$ indicates smooth, differentiable degradation [cite: 17, 19].

**Primary Source (2024-2026):** "A Detection Method for Circumferential Alignment of Diminutive Lesions Using Wavelet Transform Modulus Maxima and Higher-Order Local Autocorrelation" (2024/2025) [cite: 20], and recent derivations combining WTMM with complex-valued wavelets to simultaneously characterize instantaneous frequencies and singularities (2025) [cite: 19].

**Empirical Lift:** Moderate to High. WTMM provides a rigorous mathematical classification of the *type* of boundary. Unlike the $\max/\operatorname{mean}$ ratio, which just looks for a large jump, the Hölder exponent derived from WTMM explicitly characterizes the fractal dimension and differentiability of the cliff [cite: 18]. It effortlessly handles multi-scale phenomena and separates noise (which dies out at larger wavelet scales) from true singularities (whose modulus maxima persist across scales) [cite: 18, 21]. 

***

## 3. Multi-Scale Boundary Detection

### The Limitation of Single-Scale Sweeps
The current v1 loader sweeps a *single* scale defined implicitly by the 8 steps between $M_{LEHMER}$ and $1.50$. In complex systems, boundaries are rarely absolute; they are inextricably linked to the resolution of observation. A boundary that appears as a sharp phase transition at a macro-scale may resolve into a smooth, heteroskedastic degradation when sampled at a micro-scale. Relying on a single step-size risks severe aliasing and phase-transition hallucination.

### Proposed v2: Multi-Scale Scale-Space Sweep
We propose a v2 loader that conducts simultaneous sweeps across multiple octaves of band-width (e.g., $N=\{8, 16, 32, 64, 128\}$ steps). Drawing from the rich literature of **Scale-Space Theory** and **Wavelet Transforms**, this architecture will differentiate between two distinct physical realities:
1.  **Scale-Invariant Boundaries:** A true "cliff" (e.g., a first-order phase transition). In scale-space, the topological feature or the wavelet modulus maximum line will persist across all octaves of bandwidth without shifting its position [cite: 18, 21].
2.  **Scale-Specific Boundaries:** A smooth degradation that appears sharp only due to a specific sampling rate (e.g., a second-order transition or a projection artifact). In scale-space, the singularity strength decays, or the location of the maximum gradient shifts as the bandwidth resolution increases.

### Literature Integration
The Wavelet Transform Modulus Maxima (WTMM) framework natively executes this multi-scale operation. By mapping a 1D time series (or parameter sweep) into a 2D surface $W(a,b)$ showing how local patterns evolve with scale $a$ and time/position $b$, WTMM extracts the geometric skeleton of the signal [cite: 21]. Ridges representing singularities form chains across scales [cite: 21]. The behavior of these chains determines scale invariance. Arneodo et al.'s foundational work, continuously expanded through 2024–2026 implementations [cite: 19, 20], dictates that true singularities possess WTMM lines that span from macro-scales $a \to \infty$ down to micro-scales $a \to 0^+$ [cite: 17].

***

## 4. v2 Loader Design Specification

The v2 loader entirely deprecates the $\max/\operatorname{mean}$ ratio. Instead, it deploys a dual-engine analytical framework, utilizing BOCPD as the primary statistical detector and WTMM as a robust secondary verifier across multiple scales.

### 4.1 Concrete Specification

**A. Primary Detector: Bayesian Change-Point (BOCPD)**
The system initializes a Gaussian Process or piecewise linear model. As the parameter $M$ is swept incrementally, the BOCPD algorithm calculates the posterior distribution of the run-length $r_t$. 
*   *Threshold:* If the posterior probability $P(r_t = 0 | M_{1:t}) > 0.95$, a structural break candidate is flagged at $M_t$.

**B. Robustness Verifier: Wavelet Singularity Detector (WTMM)**
To prevent false positives from localized heteroskedastic bursts, the candidate array is passed to the WTMM engine.
*   *Process:* A Continuous Wavelet Transform (using a Gaussian derivative wavelet) is applied over the data at scales $a \in \{2^1, 2^2, 2^3, 2^4\}$.
*   *Validation:* Modulus maxima lines are traced. If a continuous chain of maxima persists across all scales and points to the candidate $M_t$, the Hölder exponent $h(t)$ is calculated [cite: 17, 21]. If $h(t) < 1.0$, it is confirmed as a true mathematical singularity (cliff).

**C. Multi-Scale Sweep Engine**
The loader dynamically increases its resolution. If a boundary is detected at $N=8$, the loader automatically "zooms in" and re-evaluates the local neighborhood at $N=32$ and $N=128$. 

**D. New Kill Patterns and State Transitions**

1.  `smooth_degradation`: 
    *   *Condition:* BOCPD posterior $< 0.95$ globally; WTMM Hölder exponent $h(t) > 1.0$.
    *   *Meaning:* The system decays gradually. The boundary is an illusion of parameterization.
2.  `sharp_boundary_detected`:
    *   *Condition:* BOCPD posterior $\geq 0.95$; WTMM $h(t) < 1.0$ persisting across all scales.
    *   *Meaning:* A true, scale-invariant first-order phase transition or topological rupture.
3.  `multi_scale_boundary_inconsistent`:
    *   *Condition:* BOCPD detects a break at coarse scale ($N=8$), but at fine scale ($N=128$), the WTMM lines dissipate, and the transition resolves into a smooth curve. 
    *   *Meaning:* The claimed "boundary" is merely a sampling artifact (aliasing).
4.  `phase_transition_below_resolution`:
    *   *Condition:* Smoothness detected at coarse scales, but WTMM reveals diverging singular behavior exclusively at the highest resolutions ($N \ge 64$).
    *   *Meaning:* A micro-structural phase transition (like the missed M=1.26 ITER-18 event) that is hidden by the macro-variance of the data.

### 4.2 Architectural Pseudocode
```python
class G10v2Loader:
    def __init__(self, M_start, M_end, BOCPD_thresh=0.95, Holder_thresh=1.0):
        self.scales = [cite: 22, 23]
        self.b_thresh = BOCPD_thresh
        self.h_thresh = Holder_thresh

    def ingest_and_sweep(self, data_claim):
        results_by_scale = {}
        for N in self.scales:
            M_sweep = linspace(M_start, M_end, N)
            signal = execute_claim(data_claim, M_sweep)
            
            # Primary: BOCPD
            bocpd_probs = compute_bocpd_posterior(signal)
            candidate_idx = argmax(bocpd_probs)
            
            # Secondary: WTMM
            wtmm_skeleton = compute_cwt_skeleton(signal, octaves=[cite: 19, 24, 25, 26])
            holder_exp = calculate_holder_exponent(wtmm_skeleton, candidate_idx)
            
            results_by_scale[N] = {
                'prob': bocpd_probs[candidate_idx],
                'holder': holder_exp,
                'is_cliff': (bocpd_probs[candidate_idx] > self.b_thresh) and \
                            (holder_exp < self.h_thresh)
            }
            
        return self._evaluate_kill_patterns(results_by_scale)

    def _evaluate_kill_patterns(self, results):
        if all(res['is_cliff'] for N, res in results.items()):
            return "sharp_boundary_detected"
        elif not results[cite: 22]['is_cliff'] and results['is_cliff']:
            return "phase_transition_below_resolution"
        elif results[cite: 22]['is_cliff'] and not results['is_cliff']:
            return "multi_scale_boundary_inconsistent"
        else:
            return "smooth_degradation"
```

***

## 5. Instrument Validation vs. New Math

The LIVE FINDING (ITER-10) document framed the detection of the Salem cluster boundary at M=1.30 as "instrument validation." This is a tautological epistemological stance: the instrument was praised because it found exactly what the catalog documented. While necessary for calibration, a true scientific instrument must be capable of surfacing **non-tautological structure**—finding phase transitions that the catalog explicitly *does not* document or even contradicts.

G10’s multi-scale smoothness diagnostic could surface non-tautological findings in the following three concrete tests:

### Test 1: Discovering Implicit Scaling Laws in "Unstructured" Manifolds
**Scenario:** A catalog assumes a particular dataset (e.g., latent embeddings of large language models or high-energy particle collision records) exhibits a continuous, Gaussian topology. The catalog explicitly documents no boundaries.
**The Test:** Deploy the v2 Loader (`phase_transition_below_resolution` kill pattern) across multi-scale sweeps of the embedding space.
**Non-Tautological Finding:** If the WTMM engine returns a persistent Hölder exponent $h < 1.0$ at a specific dimensional radius, G10 has discovered an implicit manifold collapse or a structural scaling law limit. This proves the data is not a continuous blob but possesses hidden strata or phase transitions (e.g., grokking thresholds) undocumented by the creators.

### Test 2: Falsifying Documented "Hard" Boundaries (Manifold Smoothing)
**Scenario:** A macroeconomic catalog or biological taxonomy claims a "hard" structural break between two regimes (e.g., a sharp transition between biological species features or recession/bull market states). 
**The Test:** Apply the `multi_scale_boundary_inconsistent` logic. Sweep the transition parameter at highly granular levels ($N=1024$).
**Non-Tautological Finding:** The BOCPD framework reveals that the posterior probability of a change point smears out over the parameter space, and WTMM shows $h(t) > 1.0$. G10 proves the catalog's "boundary" is an artifact of low-resolution human observation. The "cliff" is actually a smooth, heteroskedastic degradation.

### Test 3: Heteroskedastic Divergence in "Stable" Regimes
**Scenario:** The catalog documents a system as being in a stable, stationary phase, anticipating no transitions.
**The Test:** Run persistent homology bottleneck distance calculations [cite: 16] on the temporal or spatial sweep of the parameter.
**Non-Tautological Finding:** Even if the *mean* of the data remains entirely flat (fooling standard statistical checks), the bottleneck distance suddenly spikes. G10 discovers that the internal topology (e.g., the variance matrix or the multi-agent connectivity) has shattered and reorganized. This surfaces a "silent" phase transition—a transition in the covariance/heteroskedastic structure that leaves the first-order mean unaffected.

***

## 6. The Contrarian View: Phase Transitions as Projection Artifacts

In advanced geometry and high-dimensional statistics, there is a contrarian perspective: **true "sharp boundaries" or "cliffs" do not exist in sufficient dimensions.** By the Whitney Embedding Theorem and the principles of manifold unfolding, any abrupt discontinuity or self-intersection in a low-dimensional space can be resolved into a smooth, continuous manifold if embedded in a space of sufficiently high dimensionality. 

When a phase transition appears as a sharp "cliff" in a scientific catalog, it is almost always because the observer has forced a high-dimensional reality through a restrictive, low-dimensional **projection**. The cliff is merely a fold catastrophe, a caustic, or an edge artifact of the chosen coordinate system.

### G10's Value is in the Choice of Projection
If all boundaries become smooth in sufficient dimensions, then the boundary detection algorithm itself is trivial. The profound value of the G10 module is not the detection of the boundary, but **the specific choice of projection that forces the boundary to emerge.** 

By selecting the specific parameter sweep (e.g., $M \in [M_{LEHMER}, 1.50]$) and observing a sharp boundary, G10 is actually identifying a privileged axis of compression. It is finding the exact eigen-vector or projection plane where the underlying high-dimensional complexity collapses into a singular, human-interpretable phase transition. The algorithm is an instrument of *epistemic projection*, not mere statistical tracking.

### What Boundary Projections Would G10 Currently Miss?
Because G10 currently utilizes a naive 1D linear sweep and measures sequential Euclidean distance via the `first_diff` operator, it assumes that the projection axis is orthogonal and linear. It will completely miss:

1.  **Rotational or Manifold-Aligned Projections:** If the data undergoes a phase transition along a curved manifold (e.g., an angular topological wrap), a linear 1D sweep will cross the manifold multiple times or alias the curve, producing a chaotic `first_diff` sequence rather than a clean boundary. The max/mean ratio will interpret this as high baseline noise (smooth degradation) rather than a sharp transition.
2.  **Entangled/Coupled Projections:** In quantum or complex systems, a phase transition often requires a non-linear combination of multiple variables to become observable (e.g., a transition detectable only in the principal components of the covariance matrix, rather than the raw variables) [cite: 27]. G10, observing only a single predefined parameter $M$, is blind to phase boundaries that require a multi-dimensional projection vector to manifest. 

### Conclusion
To transform G10 from a simple calibration script into a mathematically rigorous engine of discovery, the transition from the brittle $\max/\operatorname{mean}$ ratio to a unified BOCPD, TDA, and WTMM multi-scale framework is paramount. By embracing scale-space dynamics, G10 v2 will not only avoid the false negatives of the ITER-18 anomaly but will possess the analytical vocabulary to challenge, rather than merely validate, the fundamental topological assumptions of scientific catalogs.

**Sources:**
1. [cern.ch](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF72m4sxNMtfqWsSUHRz45Z4m7wV_MaTcHo0Mp_NfBkg4YgcE_rYjtFSwx2riZJMSHDDf1ir7N5P0jmgmodwFFwjXq9F0LftUTNml09RFA4mIVg4MgQT0Lb7QrTxuUlV3jPtEGJjpdKNhoJnqlVKzaK0Y1iZxN8XAmELliRl6j64xrANgoDxYkkhiBEA2bWTHRB8Q==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFggKbICd-H6_0MCjmfi8zreiOn6lh-rGwCtZRUIgebrfvc_SFOh8GM62KJ9_nodET6jDO5Klfoydd_RMZXmlbzD3MJ9oZw-oNOuQBL0oVrNzTLMzVpCA==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFg7MfTEvv3DAoNSzWCn63MGE7ULVgLuG5ayEZ_Lzyw1YBNDw25ARGJIL69RfuJojYRB8HkSLV7DWZnmEAmmF267fHS4e1O-C3kDGUOGzhjATw1CjbGCr1N7Q==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3UKHvJ-aZtcU3upG4WvgIEwixuG9GS3NHjCW8h1OhpF06O2Rp0M_qPI3efI-WlFlt0jdk50h8uyVmZMAXWMp_TEv4T6_6-lcjMdK9H_79r4GQa7RrCUWDxQ==)
5. [spiedigitallibrary.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHYIkhTtVYcpAOnKWmA9JWAUvoMGa8pIXAvcxK4VtOISzvGA4G-ldk6eNKZ0D8TAChIjuK_XSHGQHMZb27926VWskTyT2NFZrAXS2H11cDGUngdWhkRiUfFIhF7gk0ZVyjqhLBin8QezZf0rDNgej9I8TRm2mgp6bXrcIIS-DCylGO0W9QA4tclpeW_MmCkibn-qbQoiIPfto5ueNFhC39QN_FnoPOd-puf58R_Cd4cQ28KaLoSM15cmzUOrYf1TS-kfAzMkDIhHQh22OL3SVV7jPnSCLFVkfSTtJB23ddEEkbzoEbUIX0-rXcnSvYbADcKiaA=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5Z0uTpuA8NZyo4ii-a6nhgLEc7S0xZKEtsyN6UVxC7bcd9pmv2oprzvSml-zvi46stTm9vpWdi98jiuaLd7Fe6R22sC4JwN_Ku9TRNIPVaLMr0AxdRA==)
7. [chinacdc.cn](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYIvviNpbf-lDp75KG3efXTFLNsOAnJpmOMhz6D7YC3JfwgkUGIRa_eALB-hSl8rHiZjldfo_4nT3UQfC4Z43HtkBL12co_ou2n5EORqJLH3Q_7JzdQF9W8W9LP3lNe1M3r-Jm_Z7VNy3MTjxucyOmyNFpGewjuJP_f63W2iwR8ZM=)
8. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTkwAeeDLtdBBUfXhiJ2mv-5iRpENigE1cEru43QsEAqD7cEUjtoOuYxsXqFIp60jOyjukbgUDiLqaKY1N6LDxXh8y-bvASKd-x2v-gr9dz6iN0Ez0OvyKAlW7aBkOtrM=)
9. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHi54s81EGcb5-_8SUNyHnjJPEK7e4wJ2nsDX0oG-BVbOilgV8-QIIF4RG9YD0e12-mh7UXYP9BpdiIw3n8dK8OHilaN2WY-7gBGxHug2kfwNjKPWCPxek7ZtVpNzZlJZWmb6NdrSyllRZ4QK-SC-cgz13fg_EO)
10. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZHRxjd8kb8DGC-o-s_hqD6QqNdxGR1mdhRn2KcCN8VN1y3g_HU8jQtLeEpiqbADDaoiRMnD6hPCiwaUl5IeX-l7n-Q4C4XCQAcFLoK9nRALT_NAxI0l54ZZfBKhU=)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdT1b6XuTwO59E9BpfAXWUF85RRqBP765oxe_LFIVvnyaF_RXjqhJhfjrMXNMuyMVjq-nSqs_dd05eUXpaA1U4vbNheCnzwRpNC6lZNb0X5ap__2UzU-q-ng==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGts5Jpfm9aEagP6rm7i6HJN6WlPdZiiCOblfNGOFGN8R70sq9qrovxKNfP1XCwqlGDsIV1pIL_Qp3_GZ83-t_nDrodBAWEKQBptv0wBQSW9IueGhPcZp5vmg==)
13. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaOnknaDRsO5J45rVmWsTAPitlUutYSRrfuWtNrrFCg-BnrSl05bgvJ4DO1ZDhoS5QrTk3KIlZ2KEUcieNq5igLYd_VvUJsl4_qaV8axey5j_WwPWuwdDxrGjFp9rxjTsV_pC-OyrokA==)
14. [topology.rocks](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-ru_ON1lte42cICqe40tlkizgiiX865zGr6yFwEQP7l4aB0u2Ni_mpVinYokO12ix84DRqVIIDqL4c9_wGNei4_VWG2iWbleQHTmWcgBCVnvlyx8XkMsgHoOkwqK9NzgKtjaYrz50dkfP5KHO-mS9-O8flYQ=)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHgFqtvdR3ltHG9Sg8qK5QnfnlxQAe63OY7ihiZdH86cED_RgtKMywL6xan5O2io07pf0BWHZES0icaIFhkhE_AKN4HZ_IVlDsh1vSWH3sVPvUsMs0dVFZEg==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBLKJgez00sRylqARirDx_fQLS60bnyo3qWsnQWdrYQwO7jlb1xTVhi4G3O-8K3Isf5ShdHiWtW6CLAou4rTBxkvpeHB_-1LFoYCNhhqqbwN3M5dOuNg==)
17. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHM5eKvmasMFWMDRmNIxbcyQK95a8w4Q-yXz8nAd_6duOkLKh4gw9N9FhPPPsWYZrHEQbpkJ2uT_iN7xXA1TzEAHwDHslMN72XixlbyjmbLJ5d8Sv41e3-mqH9xqDpSHQfq6Se6OmxY3X7Yt4h_TeXp1FeI4pRykdwghmz_KG4FeXFPA0icFzFvRCe4lUEzyNZOd3NxTWJt5JcKLqCQagpLh2unheL-YK9VK1iuJiLf-UMbSYYHxlb7ZZccNCI-pj8s3CK_y5Q_5cCIiBoRJ9WEPVjgRoUjKU0ysJAFKKcRX-pFTM_pW2KX_XSbKc9Ke5WXvrTS5hcoldTFVyDuDSIjb1xNfMrfh0iYsfhbMV349Ax126zGvX1xt_f3FwJnKkt5tJUiAq0s)
18. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFWGyuEokfrV87mKReiPm238DkyRxHuK6i9iQ5cGkZ10uaKKxzWWYCVbxSLjyIIWqNoYG3EBf8c26ISRQhOMEWV8zHASwsRRjxdcb_x6oEd3mNl046XfwUvNj1_h3DY1e-RAb7f2H-WXkPr3j1K2X3GB_1UfQMO3xPVdM=)
19. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoRjbicLo17sUWY6y1bq8_j2I59oLsWWAdDyMIz0pQQ-5gBGxJmKsRANwg0tZuTSW5fCuOCWmJFEztSd_4t9nCZF4Q9SiMv7czAa1SP4nhn2XvUAlgSyVPIEYLlj8A5wFduHDSF86bUoKdiwU9IAbxG6PeXUTIn1UReODK6IGaxzdLsT2o_LgQBTbPmhJTy_wZMlZDkX6fKbegDTZBkMb1H7BtJPV_ubgsxzL_9jaKNOQud8xWVkBvrE9oU-Mb9lnKC4MaBwSuOX6usYHcpzfN3EjAXJrVWpxwmV9knMwKSeY6eE87B_Oow3vskGzAZBHPcJEaDh4bq44DDiWncFHZgjIkul0ve6Xgxw==)
20. [grafiati.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG34wZ1kaecetAHeuNO_wKGgOeTGDNE6HFVp1RI8Ob04rVzFdmRQ2DNHJZhQ35vA2tTvoNxFDZOQ9TYH9eSBuOGSLrNquLoRhDZf8RceW1NKgI6XU6gh1XfQliPiguD2BXNRaJkEjStYWO5AQnqauGs84vu9vv98hRzS4iOpkNqiZBqaC1GgWRNzA==)
21. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhZHO_gx_3beeru0NG5OoZJUG0-z16sCXBfBRxiLUWRMcJc4YuDI5RWq1s-jaWKYSs9AZwS6_-5ylve4Yo687AAOl2zRNSmjZuSo4H7Q03Zi9btddqdJx2RAGrjI3-UKJq-DXURFc3Gb2IoslOXV89ckrYlNe0lCsPbnY_vg8=)
22. [sparai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFY0ojMYRPUHqqDFhEtB4XNqJ2X4DCiz7wslfGOx-t1bnpzidzYVkhfFIvOf4p3SZ-HWWMLCFbP_gwXFicVj3nFBz2jRW2RoL4ZySRVrLSTjPLJ_4u08qzQKqTHMkcmsHSZaLKfXLFtGfrnsU1vRALwtwrZ8d-Uyu7zlp-OatJz8zWXZdHJXEq1xCPcK02U3bLD7ILXGiM2hQ==)
23. [scipost.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsvSl7VXxV6B21nzkPST2jGMiCjLAZsO5sTYdhUGtXvMVH6r_rVPftW_Ulq4xO7MFM52LUHzcsjfrxBpKBdSRZCWz5-Q7enwVL1saGLJgkgEXC3nxo3o1P7Lv2Ee0Q)
24. [huggingface.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGI8uHAPwD1bN9poQQvzTFAAbcakDpa36ecgfHqiF0PruulPdCeIz5Adq_vZ3rIc8loxpO7qhHIFMkGjYOQ4DGZvJgsCjmXcLsQOuFDZ9-3sXUCkFsvFswcj9flulqn4LbMzKpjkV1rtxIwZoI=)
25. [ics.org.ru](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQ3ejTgBiD0zXJC50Pfk803kl9-9HDdvmCc9Hi1n9pBoosBZqBj_k439uWWEBV1W1EqmC_aMr8_SsYBIeJwK6GqE9WcMxXGMh0t0MNr6q3ZlQOokpcWjW1Wk3vyJWStNimvoGiVPw_Y_HcG8wRZG6ZivuFWCuo1_9OjSzSyw==)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZHzg0Oy4gySGIiJRC42_B445iQlPF-1eESmuPFbUpl_cn7r4iIGGPtr6GCKQJ9AVKKDPp50EepSlSz-UeEZoqvGTAquaNWvF9l9dfQLfkjSplZNvtu-2M5yDe88Qt2RaHt789naKiOreTReF4uxg1VXo2qJ5LIU7_g_iYOu0ilXp4)
27. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3DUs4X6XcBzdMK3ORPwZemcyLffOC1Vzkph-SRA3QJElfvzkVvDdXy9bGaX4qql7lImJljDtbev-uMaEArKds5EgjezKNvBI5SDjympxAI7UArEIBOD_k1Dd5BoQ=)


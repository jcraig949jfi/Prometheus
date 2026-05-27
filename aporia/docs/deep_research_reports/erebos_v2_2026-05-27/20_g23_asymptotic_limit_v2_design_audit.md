# Prompt 20: G23 Asymptotic Limit — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChZhSWdXYW92S0phcTRzT0lQdktfUk9REhZhSWdXYW92S0phcTRzT0lQdktfUk9R
**Elapsed:** 303s

---

# Asymptotic Decay Diagnostics and Error-Scaling in Mahler Measure Catalogs

**Key Points:**
*   **The empirical identification of a $1/\log(N)$ decay law for the minimum Mahler measure at degree $N$ is phenomenologically novel but theoretically anticipated.** While 2024-2026 literature heavily discusses asymptotic bounds on the Mahler measure (e.g., Dobrowolski's classical bounds and recent updates), no peer-reviewed computational catalog explicitly isolates $1/\log(N)$ as the definitive empirical regression law.
*   **The poor fit ($R^2=0.25$) of the log-log model strongly indicates masked structural complexities, such as regime changes or non-stationary decay.** Incorporating broken power-law models—highly utilized in recent 2025-2026 astrophysical and time-series literature—will likely resolve this underfitting by detecting kink-points in the structural complexity of polynomials.
*   **Polynomial degree ($N$) is an imperfect proxy for structural complexity.** Alternative measures, such as coefficient height, sum-of-coefficient-magnitudes (length), effective degree, and the Mahler measure of the derivative, offer more robust state-spaces for decay-law fitting.
*   **A marginal $R^2$ advantage ($0.54$ vs. $0.51$) is insufficient to definitively claim superiority of the $1/\log(N)$ law over the $1/N$ law.** A rigorous bootstrap resampling protocol is required to determine whether this advantage survives statistical variance. 

**Summary of Methodological Shifts:**
The transition from the V1 `g23_lehmer_degree_decay` loader to a V2 architecture necessitates moving beyond simple log-log linear regression. The V1 model hypothesizes an $\mathcal{O}(1/N)$ decay, triggering a kill pattern when the expected $1/N$ decay is not observed. However, the discovery that $1/\log(N)$ marginally outperforms $1/N$ (with an $R^2$ of $0.54$) implies that the polynomial minimum Mahler measure curve converges sub-polynomially to Lehmer's floor. To validate this, the V2 loader must sweep across multiple complexity measures, implement kink-point regression to capture non-stationary decay, and utilize substrate-grade bootstrap confidence intervals to definitively separate true asymptotic laws from sampling-driven noise.

**Contextual Overview of Lehmer's Problem:**
Lehmer's conjecture (1933) posits that there exists an absolute constant $\mu > 1$ such that the Mahler measure $M(P)$ of any non-cyclotomic irreducible polynomial with integer coefficients satisfies $M(P) \ge \mu$ [cite: 1, 2]. The smallest known Mahler measure remains that of Lehmer's degree-10 polynomial, $M(x^{10} + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1) \approx 1.17628$ [cite: 3, 4]. Recent advancements in 2024 and 2025 continue to leverage this conjecture in topology and number theory, yet the empirical rate at which bounded degree limits approach this floor remains an active frontier of diagnostic analysis.

---

## 1. The $1/\log(N)$ Finding: Novelty and Contextual Survey

The LIVE FINDING from the ITER-17 refinement indicates that a $1/\log(N)$ decay law best fits the difference between the minimum Mahler measure at degree $N$, denoted $M_{\min}(N)$, and the absolute known minimum, $M_{\text{LEHMER}}$. The specific regression models $(M_{\min}(N) - M_{\text{LEHMER}})$ against inverse logarithmic scaling. To determine the novelty of this finding, we must survey recent literature on asymptotic bounds, particularly the Schinzel-Zassenhaus conjecture, Smyth's bounds, and updates to computational catalogs.

### 1.1 Recent Literature on Asymptotic Bounds (2024-2026)
A survey of peer-reviewed and announced literature from 2024 to 2026 reveals profound ongoing interest in the asymptotic bounds of the Mahler measure, but an empirical declaration of $1/\log(N)$ as the specific computational decay rate for $M_{\min}(N)$ remains absent from the primary literature.

**Theoretical Lower Bounds:**
The most rigorous theoretical framework surrounding asymptotic limits is Dobrowolski's bound. Dobrowolski (1979) established that for an irreducible polynomial of degree $N \ge 2$, the Mahler measure satisfies a sub-polynomial lower bound of the form $M(P) > 1 + c \left( \frac{\log \log N}{\log N} \right)^3$ [cite: 5, 6]. Voutier (1996) later provided the explicit constant $c = 1/4$ [cite: 2]. While this bound involves logarithmic terms, it is a *theoretical lower bound* proving that if the measure approaches 1, it does so slower than any power of $1/N$.

Recent developments in 2024–2025 focus on topological and dynamical consequences of these bounds rather than computational cataloging of $M_{\min}(N)$ decay:
*   **Pengo (2024)** [cite: 2, 6] provides a comprehensive synthesis of Mahler measures, discussing how Dobrowolski and Voutier's bounds fail to prove Lehmer's conjecture by only a logarithmic factor. The text emphasizes theoretical limits rather than empirical decay fitting.
*   **Garoufalidis and Jeon (2024)** [cite: 7, 8] utilize Lehmer's conjecture as an assumption to estimate the degree of the trace field of hyperbolic Dehn fillings. Their work underscores the pervasive impact of Lehmer's $\mu \approx 1.17628$ floor but does not compute empirical convergence rates.
*   **Knapp and Yip (2025)** [cite: 9, 10] explore the relationship between polynomial root separation and the Mahler measure. They prove that the separation of roots $\text{sep}(f) \ll n^{-1/2} M(f)^{1/(n-1)}$, establishing sharp upper bounds up to a constant factor. While their work intricately links degree $N$ and $M(P)$, it addresses root clustering rather than the asymptotic decay of $M_{\min}(N)$ across a global catalog.
*   **Brunault, Guilloux, Mehrabdollahei, and Pengo (2022-2024)** [cite: 11, 12] study sequences of Laurent polynomials obtained by monomial substitutions, proving their Mahler measures converge to the multivariate Mahler measure. They provide an explicit upper bound for the error term in this convergence, generalizing work by Dimitrov and Habegger, showcasing that error terms in specific multivariable sequences can exhibit power-law decays.

### 1.2 Novelty of the Computational Finding
Is the $1/\log(N)$ finding novel? 
1.  **Theoretically**: No. The foundational architecture of Dobrowolski's limit intrinsically links the decay envelope of Mahler measures to inverse logarithmic degrees [cite: 6]. If Lehmer's conjecture is false, the decay towards 1 is bounded by $\mathcal{O}((\frac{\log \log N}{\log N})^3)$. If Lehmer's conjecture is true, the sequence $M_{\min}(N)$ must asymptote to $M_{\text{LEHMER}}$.
2.  **Empirically / Phenomenologically**: Yes. The explicit log-log and multi-law comparative fit ($1/N$, $1/\log(N)$, $1/\sqrt{N}$, $\exp(-N/10)$) utilizing the Mossinghoff tables and modern successors to declare $1/\log(N)$ as the optimal phenomenological decay rate with $R^2=0.54$ is a novel diagnostic application. No peer-reviewed paper in the 2024-2026 window has published an empirical $R^2$ regression horse-race concluding $1/\log(N)$ is the definitive statistical description of cataloged polynomial decay.

---

## 2. The Log-Log Fit Masks Structure: Non-Stationary Decay and Broken Power-Laws

ITER-17 reports a slope of $-0.21$ and an $R^2 = 0.25$ for the strict log-log fit of $(M_{\min}(N) - M_{\text{LEHMER}})$ versus degree $N$. In the context of asymptotic analysis, an $R^2$ of 0.25 is critically low and indicates that the assumed scale-invariant power-law model ($y = c x^{\alpha}$) is masking underlying structural variance.

### 2.1 The Case for Kink-Point Regression
When a single power-law fails to describe physical or mathematical phenomena over many orders of magnitude, modern statistical analysis relies on **broken power-law (BPL)** or kink-point regression. A broken power law is a piecewise function consisting of conjoined power laws, where each domain possesses its own index (slope) defined by bounding "breaks" [cite: 13].

In the 2024–2026 literature, BPL models have seen explosive adoption across diverse fields facing non-stationary time series and masked structural complexities:
*   **Astrophysics and Lensing (2026):** The TDCOSMO collaboration extensively utilizes BPL mass profiles to model lens galaxies. The BPL model allows for a transition in the radial slope of the density profile, capturing behaviors from flat-density cores to steep gradients [cite: 14, 15].
*   **Time-Series Forecasting (2025):** In evaluating the scaling laws of large language models adapted for time-series, researchers observed "broken power-law like scaling" across five orders of magnitude in model size, utilizing kink-point regression to identify regime changes in Mean Squared Error (MSE) scaling [cite: 16].
*   **Biophysics and Sleep Research (2025):** Schneider et al. (2025) demonstrate that a broken power-law model is strictly superior to single-slope linear regression in describing RR-interval power-spectral densities. They determined custom breaking points to allow for two independent spectral slopes in distinct frequency domains [cite: 17, 18].
*   **High-Energy Pulsars and QPOs (2026):** Yu et al. (2026) model the quasi-periodic oscillation (QPO) fractional root-mean-square (rms) energy relation using a *smoothly broken power law*, successfully identifying break points and non-stationary trends [cite: 19].

### 2.2 Application to the Mahler Measure Catalog
The low $R^2$ for the global log-log fit of Mahler measures strongly implies that the dataset exhibits a kink-point. For instance, Mossinghoff's classical exhaustions completely mapped degrees $N \le 44$ and identified polynomials with measures below $1.3$ [cite: 3]. Above this degree, catalogs become increasingly sparse, relying on heuristic searches (e.g., simulated annealing, LLL algorithm modifications, genetic algorithms) rather than provable exhaustion. 

A broken power-law model for the Mahler measure decay would take the form:
$$ \log(M_{\min}(N) - M_{\text{LEHMER}}) = \begin{cases} \alpha_1 \log N + c_1 & \text{if } N \le N_{\text{break}} \\ \alpha_2 \log N + c_2 & \text{if } N > N_{\text{break}} \end{cases} $$
The poor global fit ($R^2=0.25$) is likely the result of forcing a single $\alpha$ across two distinct regimes: the fully exhausted low-degree regime (where $M_{\min}$ rapidly plummets to Lehmer's value) and the sparse high-degree regime (where sampling limitations create a plateau, flattening the apparent decay).

---

## 3. Alternative Complexity Measures

The V1 loader utilizes the standard polynomial degree $N$ as the sole independent variable for structural complexity. However, the true "complexity" or state-space size of a polynomial $P \in \mathbb{Z}[x]$ is multidimensional. Relying solely on $N$ assumes that all polynomials of degree $N$ are uniformly likely to yield small Mahler measures, which is false; sparse polynomials or polynomials with small coefficients are heavily favored.

Surveying the literature, several alternative complexity metrics offer a more nuanced independent variable for asymptotic regression.

### 3.1 Coefficient Height
The coefficient height of a polynomial $P(x) = \sum_{i=0}^N a_i x^i$ is defined as the maximum absolute value of its coefficients:
$$ H(P) = \max_{0 \le i \le N} |a_i| $$
**Literature Context:** Mahler's measure is closely bounded by coefficient height. As proven by classical inequalities [cite: 3, 9], $\frac{1}{\sqrt{N+1}} H(P) \le M(P) \le \sqrt{N+1} H(P)$. In targeted searches, restricting $H(P) = 1$ (e.g., Littlewood polynomials) drastically alters the expected minimum Mahler measure. Using $H(P)$ as a secondary complexity metric allows the loader to isolate whether decay laws are height-dependent.

### 3.2 Sum of Coefficient Magnitudes (Length)
The length of a polynomial is the $L_1$ norm of its coefficients:
$$ L(P) = \sum_{i=0}^N |a_i| $$
**Literature Context:** Length is highly relevant for bounding the Mahler measure. For instance, Mignotte showed that for an irreducible non-cyclotomic polynomial of length $L$, $M(P) \ge 2^{1/2L}$ [cite: 5]. Recent work by Brunault et al. (2022) utilizes $L_1(P)$ to establish error bounds in the convergence of multivariate Mahler measures [cite: 11, 20]. Measuring decay against $L(P)$ rather than $N$ natively accounts for the sparsity of the polynomial.

### 3.3 Effective Degree
By Kronecker's theorem, a monic polynomial with integer coefficients has $M(P)=1$ if and only if its roots are roots of unity (or zero) [cite: 2, 21]. Therefore, cyclotomic factors do not contribute to the Mahler measure. 
If $P(x) = C(x) \cdot K(x)$ where $C(x)$ is a product of cyclotomic polynomials and $K(x)$ is the non-cyclotomic "core", the **effective degree** is $\text{deg}(K)$.
**Literature Context:** When evaluating $M_{\min}(N)$, polynomials of degree $N$ often achieve small measures by multiplying Lehmer's polynomial (degree 10) with cyclotomic factors of degree $N-10$. Thus, a polynomial of degree 50 may have an *effective degree* of 10. The V1 loader's failure to distinguish between absolute degree and effective degree causes severe horizontal striations in the scatter plot, ruining the $R^2$ of any smooth decay fit. Tracking effective degree resolves this.

### 3.4 Mahler Measure of the Derivative
The Mahler measure of the derivative $M(P')$ has profound connections to the separation of roots. 
**Literature Context:** Knapp and Yip (2025) [cite: 9, 10] rely heavily on the discriminant and root separation of polynomials. Since the discriminant $\Delta(P)$ can be expressed via the resultant of $P$ and $P'$, $M(P')$ acts as a proxy for root clustering. Highly clustered roots near the unit circle influence the overall integration of the logarithmic measure. Plotting $M(P)$ against $M(P')$ may yield distinct linear manifolds independent of degree $N$.

**Summary Table of Alternative Measures:**

| Metric | Definition | Relevant Primary Source | Justification for V2 Inclusion |
| :--- | :--- | :--- | :--- |
| **Degree ($N$)** | Highest exponent with $a_n \ne 0$ | Standard | Baseline comparison. |
| **Height ($H$)** | $\max \|a_i\|$ | Knapp & Yip (2025) [cite: 9] | Distinguishes Littlewood ($H=1$) cases. |
| **Length ($L$)** | $\sum \|a_i\|$ | Brunault et al. (2022) [cite: 11] | Captures polynomial sparsity. |
| **Effective Degree** | $N - \text{deg}(\text{Cyclotomic})$ | Kronecker's Thm [cite: 2] | Removes artificial root-of-unity padding. |
| **Derivative ($M(P')$)** | Mahler measure of $P'$ | Knapp & Yip (2025) [cite: 9] | Proxies complex root separation bounds. |

---

## 4. V2 Loader Design Specification

To rectify the shortcomings of `g23_lehmer_degree_decay` (V1), the V2 loader must systematically dismantle the assumptions of stationarity and univariate complexity. Below is the concrete specification for `g23_v2_asymptotic_diagnostics`.

### 4.1 Broken Power-Law Detector
The V2 loader will implement a piecewise regression algorithm to detect non-stationary decay.
*   **Mechanism:** Iterate through potential breakpoint degrees $N_b \in [10, N_{\max}]$. Fit two independent OLS regressions for $\log y$ vs $\log N$: one for $N \le N_b$ and one for $N > N_b$. 
*   **Selection Criterion:** Utilize the Bayesian Information Criterion (BIC) to penalize the extra parameters of the broken model. If $\text{BIC}_{\text{broken}} < \text{BIC}_{\text{linear}} - 10$, the broken power-law is strictly preferred.
*   **Signal Output:** Output $\alpha_1$ (early decay), $\alpha_2$ (late decay), and $N_b$ (the kink-point). 

### 4.2 Multi-Complexity-Measure Sweep
Rather than a 1D vector of degrees $N$, the loader will accept an $M \times 4$ tensor of complexity metrics for the catalog: $[N, H(P), L(P), N_{\text{eff}}]$.
*   **Sweep Logic:** The multi-law fitter ($1/X, 1/\log X, 1/\sqrt{X}, \exp(-X)$) will be executed in a nested loop over each complexity column.
*   **Metric Prioritization:** The complexity metric yielding the highest global $R^2$ across the best-fit law is designated the "Principal Complexity Axis."

### 4.3 Bootstrap Confidence Intervals
To resolve whether $R^2$ margins are statistically significant, the V2 loader will implement a paired bootstrap.
*   **Procedure:** 
    1. Resample the polynomial catalog with replacement $B = 10,000$ times.
    2. For each resample $b$, compute $R^2_{b, 1/\log}$ and $R^2_{b, 1/N}$.
    3. Calculate the difference $\Delta R^2_b = R^2_{b, 1/\log} - R^2_{b, 1/N}$.
*   **Output:** Calculate the 95% Confidence Interval for $\Delta R^2$. If the CI includes $0$, the loader flags the finding as `statistically_indistinguishable`.

### 4.4 New Kill Patterns
The V2 loader introduces two new failure-state triggers (`kill_patterns`):
1.  `decay_law_changes_at_complexity_K`: Triggered if the Broken Power-Law Detector finds a valid kink-point $N_b$ where the slope changes by more than 50% ($\|\alpha_1 - \alpha_2\| / \|\alpha_1\| > 0.5$). 
2.  `complexity_measure_dependent_finding`: Triggered if the "best fit law" changes depending on the complexity metric used. (e.g., $M_{\min}$ decays as $1/\log(N)$ with respect to Degree, but as $1/L$ with respect to Length).

---

## 5. Connection to Lehmer's Conjecture

The V1 live finding that $M_{\min}(N) - M_{\text{LEHMER}}$ decays at a rate of $1/\log(N)$ has profound philosophical alignment with Lehmer's conjecture.

### 5.1 Asymptotic Convergence to the Floor
If Lehmer's conjecture is true, there exists a strict absolute minimum Mahler measure $>1$, universally hypothesized to be Lehmer's degree-10 polynomial $L(x)$, such that $M_{\text{LEHMER}} \approx 1.17628$ [cite: 2, 4]. 

If $M_{\text{LEHMER}}$ is truly the infimum, the sequence of minimum known Mahler measures at each degree, $M_{\min}(N)$, forms a monotonically decreasing envelope that is lower-bounded by $1.17628$. Because Lehmer's polynomial itself can be padded with cyclotomic factors (e.g., $x^k - 1$) to artificially generate higher-degree polynomials with the *exact same* Mahler measure [cite: 2], $M_{\min}(N)$ trivially reaches the floor for infinitely many degrees. 

However, if we restrict the catalog to **primitive, irreducible, non-cyclotomic** polynomials, the decay of the "true" $M_{\min}(N)$ envelope becomes a measure of algebraic density. A sub-polynomial decay law like $1/\log(N)$ indicates that while it becomes easier to find polynomials with small Mahler measures as the degree increases (due to the exponential growth of the search space), the "distance" to the ultimate Lehmer floor closes agonizingly slowly. 

### 5.2 Canonical Literature on Expected Behavior
Does the literature explicitly test $1/\log(N)$ vs $1/\sqrt{N}$?
Canonical literature heavily favors inverse-logarithmic bounds over inverse-polynomial bounds. The seminal result by Dobrowolski (1979) proved that the Mahler measure is bounded below by a function of $1/\log(N)$ [cite: 5, 6]. Specifically, if $P$ is a non-cyclotomic polynomial of degree $N$:
$$ M(P) > 1 + c \left( \frac{\log \log N}{\log N} \right)^3 $$
While this bounds the decay toward $1$ (if Lehmer is false), the structural form highlights that algebraic numbers close to the unit circle scale logarithmically with degree, driven by resultant geometry and prime factors [cite: 5, 6]. No modern peer-reviewed paper explicitly horse-races $1/\log(N)$ against $1/\sqrt{N}$ as an *empirical* regression task, but theoretically, fractional power-laws like $1/\sqrt{N}$ are universally considered too aggressive for Mahler measure minimization. The sequence decays far slower, making $1/\log(N)$ theoretically harmonious with historical auxiliary function proofs.

---

## 6. Contrarian View: The Best-Fit Law is Sampling-Driven

**The Steelman Argument against $1/\log(N)$:**
The assertion that $1/\log(N)$ is the fundamentally true decay law, simply because it achieves an $R^2$ of $0.54$ compared to the $1/N$ law's $R^2$ of $0.51$, is statistically reckless. This $\Delta R^2 = 0.03$ margin is almost certainly an artifact of sampling bias and the structural limitations of polynomial cataloging.

Polynomial catalogs (like Mossinghoff's) are perfectly exhausted up to degree $N=44$ (and selectively up to 54) [cite: 3]. Beyond degree 54, the known minimum Mahler measures are derived from stochastic heuristic searches—simulated annealing, lattice reduction (LLL), and genetic algorithms [cite: 22]. These algorithms suffer from the "curse of dimensionality." As $N$ increases linearly, the coefficient volume increases exponentially. Consequently, heuristic algorithms drastically *underperform* at high degrees, failing to find the true $M_{\min}(N)$.

Because the catalog fails to find the deepest minimums at high $N$, the empirical $M_{\min}(N)$ curve artificially flattens out. A $1/N$ curve drops sharply; a $1/\log(N)$ curve drops gently. The $1/\log(N)$ model achieves a slightly better $R^2$ not because the underlying mathematical truth follows a logarithmic decay, but because the *search algorithms' failure rate* scales logarithmically, flattening the tail of the data. The "best-fit law" is measuring the exhaustion limit of human computation, not the asymptotic scaling of algebraic integers.

### 6.1 Bootstrap Resolution Procedure
To resolve this with substrate-grade confidence, we propose a Non-Parametric Residual Bootstrap Procedure.

**Step 1: Baseline Fits**
Fit both models to the dataset $\mathcal{D} = \{(N_i, y_i)\}_{i=1}^k$ where $y_i = M_{\min}(N_i) - M_{\text{LEHMER}}$.
*   Model A: $y_i = \beta_A \frac{1}{\log N_i} + c_A + \epsilon_{A,i}$
*   Model B: $y_i = \beta_B \frac{1}{N_i} + c_B + \epsilon_{B,i}$
Store the baseline $R^2_A$ and $R^2_B$.

**Step 2: Residual Resampling**
Calculate the residuals for the *better* model (Model A). 
$$ \hat{\epsilon}_i = y_i - \hat{y}_{A,i} $$
Center the residuals: $\tilde{\epsilon}_i = \hat{\epsilon}_i - \bar{\epsilon}$.

**Step 3: Bootstrapping (10,000 Iterations)**
For $b \in \{1, \dots, 10000\}$:
1.  Generate a synthetic dataset $y^*_{i,b} = \hat{y}_{A,i} + \epsilon^*_i$, where $\epsilon^*_i$ is sampled with replacement from $\tilde{\epsilon}$.
2.  Refit Model A to $y^*_{i,b}$ and calculate $R^{2*}_{A,b}$.
3.  Refit Model B to $y^*_{i,b}$ and calculate $R^{2*}_{B,b}$.
4.  Record $\Delta R^{2*}_b = R^{2*}_{A,b} - R^{2*}_{B,b}$.

**Step 4: Substrate-Grade Confidence Evaluation**
Evaluate the empirical distribution of $\Delta R^{2*}_b$. 
*   If the 95% Confidence Interval for $\Delta R^{2*}$ includes zero or negative values, we **fail to reject** the null hypothesis. The difference between $1/\log(N)$ and $1/N$ is declared indistinguishable from statistical noise. 
*   If the lower bound of the 95% CI is strictly positive, the $1/\log(N)$ advantage is statistically rigorous, refuting the contrarian hypothesis and necessitating further theoretical investigation into the sub-polynomial scaling of Lehmer sequences.

**Sources:**
1. [wisc.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmD0U9fFv4bmm5mVNMSQl8tTikIRkg2ttDiYTRIuMJXuSArYLnQb4quhJZPIHZLmCdnz15H6IeQaWtGGAf16LPAQpBWKgvyvznnvzhn9hmlEEcV9EPAU3t-N6dkYHnhY7hYKMzy65rf_xw)
2. [uni-goettingen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGoavXdhyiGCOqcLiww1PNze6nc7jso0wnnkAzJ8jLoXH3s6wgLgYxVlAkJkAXnJ-uv79THvinmgm5DgSfTBQa3xkJtO0f7NiYMJgh5rnlxVjdQNSb0vei75X5EArI3w3NZM47n6_VftytjWGD59RwEi_il_KnDM__ztuiREQuN41hzybpuCF7jT4_S-IY_RhgejC5wLUPwd7dzkfRJLrB2a2KNK-M=)
3. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG57ZB8uTlRogOJRLYh_3oDRLj0UeglclXuqC8VS_hKq_3FcD6rkD19STB-VpUIgzIABxVSFYbTOVNjHdEBREtkxqN2e544UKoINfnuPei2p9Gra9nFjgqupnytOORIv_F8FvEkNqGiG_3M2-jEbYwZLNjw5Qb8aFeBouNQuBJG)
4. [lolathompson.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOkXzT-5Z_0LgXEfLaNkO28H28HgrwY5JYlF0OxQ2kF2WmBW0ibmErxkOR4iC2_1URpdBzbpx9NQGncR58apR_kgerNGffpyPyGQcbs-sNzNaDKcdbisthhRLoLCbxHZFEi0pTXALxfQc_4-QwqG1i1OrPN5K5guQ6anesCES0OnSyhT8=)
5. [ed.ac.uk](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEY2KltyUaEmaZX0DmcC4uoH0J60yBJqszVI6DcIC3JHOw2iKYzeqG6V1L-jbgY7TDSjifCrHUWZS6yL7RNz8deEYJCBFQ9JGxv2JNrpoqGLxHi4KQvofHx_p1UUdQLuL5zNnQ5-cNXjwM_X2YWEk9dpQo=)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMxU4Rm396rjFElHhlIDwFBiPWXHexNPyE-D7ugPAbtZ1cM24C9VGPV59ghIV4aYTJ3Y6AKgiJbC5NXLJFcceyNAfJ2BBinA_SwZ6LRPWzBbA8EP6dzHynxtcXlbjTcAoreoJ5dUNt7hmt-xQB2soVJAfbNxHpeKqmidUyNw58Rw_WXHfNN76cxWdHvf_eElXTdD0xII4Q7lqJOKbK)
7. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3yWmnMgf3ZG5D5uWuZOoxGWdtVdrow-Vt0_mAAzzpEnhCYDH2nT4Xbs1Yp6D-BxB9lWKOcVKeVpRzpvDTI2KnGSuYLcseXh4Q3-OuSadMDWKYkgh1abfJSMMFaJZEn1Z-ujb4g9xNPKWeOvGBoifyAxXsvlU2-dV4UrnBrpV7xHdELQrDFRyFfiGam_Nh1llutdByv8kV)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBloR3jKTeVKwUsxn-YVnSwQo-Z5EU5bcA3FJeDJ5zi62Fn0BKxjbQeHTd3vkKzl7bXC8rmuA0kZTBCn_v27qz5YYSr2fYaRRTYWq9dFf1JGFR9uz5)
9. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEek8Qd4dV4G8sw1-9BTu993Qb_ZU_sR1_z5qqbG9XAc1QiIL7Izbx7I-W_TkUhn9pHBl3eKzII5A3kD9WkdINlIIwf-6Hfc1XSJNXsyInhusEws40T-aDU14BEV0kpgbyuGfOFArSgr4cH4CAsVoSjXkDnJlo9Tyzx7kFzWTOhAnA9JWti25OQZ7kjcweik7lhjFGwjY_E2XUyTTXfnOUg7XJfBJf6Z5cNN6KiX-nlw27mROfrO9vqhHfh0FyxkdkyqmasQbsX-Bm4INMBSk_G0Qn8cXCfLvPfP3EtT9gmgcY=)
10. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp6jO7gZvt0Oq2W8GmFPgwyR4xQ6Ty9IP_Syb4m-1rvKga-AVVfkJ9dOSUM8p6XZ0H2g6xxMBsF47F1ZEkWVoY_D8qehaDrqJS3oxYAwuz0E9Du9fHFI-E6wYWW2f8qcLgTfJ_cxiTqrjq4daznXWe39BpoTkbR38oZ4BVKvuD9601WOIDbVRmG-LN4wVe93wNgR6cQv4Ck6jC_GmDORCqveFqkgVFyacqeCzOcOQYTlKaxQ==)
11. [centre-mersenne.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgBfIRLTL3gkMiI1iwQtPQ3-0EOkDvija2aP_9t3FRd86vmWpmsylTS-X1i-grL-pDvNr_dCX3iSFPwcatdoRgqyuz3Is0cvH1w81Uq7K2Dlo1G437R8N1n-jRHcJWqhZl5ZX6pHs_G92s8N_2eQ==)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKeeAwYLq4eA-r9qNZun3LU1BQw4EbSop6XnXGdWV1_rJhLO4YEmD171uwNj3cN8l4dKJO7yFykfIFJqPd65LPsi9qx33fTuXUMCcfhbC1eMXMo354)
13. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHBP7dfjtuaRCXavRpUCcs8Bik1Tw06p1-KV3WDgmDcsJIrC0z-Ivy1ZqJ7PiGpwt3vA3cCnI5J0fOebWoKFfcngX80eUPhg_-H52UCdZ1mC6PxBBwhRPLzzBJtn7Gcyri4wHtsm4IIwP-qPO0krRi26mrjtQ==)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdtKv6o_c8TI4QGmI2N1Jy_ao74zwVCCXR7AfGIU3DqoOrkhzIOkQ5684Ny6k6atTs5ajxNaUsE-s0lqS6TSgthzSWmoNpylaTKzuKcvREBLKNJ7AawO-2)
15. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbEh18KaQOH1jNlL4IXx8HdImH3odaHnVTxJecKP9o6aCsq72vto_BdCKwJeRixi5EZK5cu1tUlBvkgcFzimfgN28o2svqzKUZ8YPr0I0KGDx7BgNTCddzFxjzJ35P1Gpfbg-IjwmKmvIrMksBIeoo6qXM1gy1z2MNgUmGPQ==)
16. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnYVyvZhPGWx0NGUVsJUMf6CSnbdTH2lWW0DggysR9jkpz9OjAXutmkNCKN33awSbwwl8N9BPaTrIsO-T9ABajfMOryHaImZJzO2cQzrA-TaeyCEaw9EjV)
17. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGb-Pa7dcYzqRo-XLW1a1oMqnSd_VLKaSQDiQ-FwZOosOd9T3ZemJGpuuKrSTLpe7IIRFreJaW2wK052IL_5LEHl122x6vQ6K2BMpjnJDUicFIz87WQxKkBR3jzZedvt2f5WK5WX6Jawcj5YS0nWvnv)
18. [biorxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeENAdPqDAWaBKM_gAfO7ql2I5FLP1OIVNHhbDrj2gi9aKmCh4QrxJ0bkKQL16MzsmKHEEhDCypBbHTJKp6gKd0fX3xrdxcDZ7FlphkUolqeZJ30wwX9b33P64zUk94_YeXdfpztzhdlqYuaAARcX7UEArkW08dA==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERd8dYNrgbIfJWuOdpVPbvsBuaPTkxsj-FhF-G8D9p1dktWNyABO2lGxrR-aZ6L79iaVqTZgORRjc_AlAh06cMiD3DnrfHf_E-ewNPQbHNLzO7MmxMD-5J)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZg5gNo4DpdjviuZnVuGJD3A9ulo786jfF-1SNGGENEjGJEkucSJ3VSV0xjHbW7kkSAZJi0rZAjXHYS8uEC8mVDLzduDHipEA78VEwGRIqF-usJyAB)
21. [umontreal.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVggSGLZawLrM05GSWivCvjESQdEYi7R4NDVJ7RIWkYo19ZWjFx5_fHyjuvTZVZmbIIxaQL1afeCucAzdyqT9nzw6hmz-7oi7xKdpY-4LmfIEh4hTzXdlk8oyuCMc=)
22. [utexas.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVzPFd_I0D_jX45o_g9sAMAOum637cfEd_b80N2t7_Fkb9AmoLBZ1D0V7wFkV8Z1_fDHB9EWwSGe1MsZHc687qkOc-_0_7vB19CPd6vM-uXmFkRwKlOQQeuqMu-m6qLXpCoN15L3yoqJLf5yUM1i5fzGw=)


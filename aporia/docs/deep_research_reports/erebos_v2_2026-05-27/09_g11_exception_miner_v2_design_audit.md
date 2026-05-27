# Prompt 09: G11 Exception-Miner — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdJWVFXYXRXZkxPMmZqTWNQcmMtMzRBVRIXSVlRV2F0V2ZMTzJmak1jUHJjLTM0QVU
**Elapsed:** 304s

---

# Advanced Anomaly Detection and Hidden-Stratifier Discovery in Number-Theoretic Datasets: An Analysis of Survivor Bias in Mahler Measure Cohorts

**Key Points:**
*   **Hidden Stratifier Discovery:** Recent advancements in causal discovery, particularly Causal Mixture Models (CMM) and latent class vector autoregressive frameworks, offer robust mechanisms for isolating unobserved heterogeneity in computational datasets. Evidence suggests that CMMs are optimally positioned to detect the degree-minima anomalies in Mahler measure survival cohorts by separating latent generative mechanisms.
*   **Sparse Contingency Inference:** The breakdown of asymptotic Pearson $\chi^2$ approximations in extreme frequency imbalances (e.g., $8501:2:14$) mandates exact or resampling-based statistical tests. The Fisher-Freeman-Halton exact test, Monte Carlo permutation methods, and the Likelihood-Ratio G-test provide rigorous alternatives, with Monte Carlo permutations offering the best balance of computational feasibility and exactness for sparse polynomial datasets.
*   **Palindromic and Salem Equivalence:** The finding that $P(\text{Salem}|\text{Palindromic}) = 0.9999$ represents a collision of mathematical necessity and algorithmic selection bias. While all Salem polynomials are strictly reciprocal (palindromic) by definition, the near-perfect inverse probability is an artifact of the bounded search spaces designed to test Lehmer’s conjecture.
*   **Cross-Domain Generalization:** Frameworks designed to identify hidden categoricals in algebraic number theory can be successfully generalized to the Birch and Swinnerton-Dyer (BSD) conjecture and knot theory. Identifying discrepancies between analytic and algebraic ranks or isolating A-polynomial hyperbolic volumes can yield highly significant minority-cell discoveries.
*   **Selection Bias Contrarianism:** The observed $\chi^2 = 191$ over-representation of non-Salem cells at degree-minima is highly likely an artifact of the enumerative bounds of the Mossinghoff dataset. A controlled study generating unbiased polynomial distributions is required to definitively separate mathematical structure from algorithmic truncation.

---

## 1. Introduction: Survivor Bias and Hidden Stratifier Discovery

The analysis of vast mathematical databases—ranging from the L-functions and Modular Forms Database (LMFDB) to specialized catalogs of polynomials generated to test Lehmer’s conjecture—has increasingly necessitated the application of advanced data science and anomaly detection methodologies. In the context of the G11 EXCEPTION-MINER protocol, the objective is to identify a "hidden property $H$" that distinguishes survivors of a high-kill cohort. A "kill pattern" characterized by `out_of_sample_failure` implies that a hypothesized property $H$ fails to predict survival on held-out objects, suggesting the presence of an unobserved, latent stratifier that governs the survivorship distribution.

This report addresses a critical finding within the current iteration of loaders analyzing the Mossinghoff dataset of Mahler measures. Specifically, the loaders have identified a tautological survival path linked to the Salem-class of polynomials (where $M < 1.30$), an extreme over-representation of non-Salem cells at degree-minima (yielding a $\chi^2 = 191$), and a near-perfect equivalence between palindromic flags and Salem-class polynomials. 

To rigorously dissect these findings, this report surveys state-of-the-art methods published between 2024 and 2026 in the fields of causal discovery, latent class analysis, sparse contingency table testing, and pure mathematics relating to Salem numbers and Lehmer's conjecture. The document proceeds through a systematic reconstruction of loader design, a mathematical deconstruction of the Salem-palindromic tautology, and the formulation of cross-domain stratifiers for elliptic curves and knot theory, culminating in a contrarian critique of the degree-minima selection bias.

---

## 2. Hidden-Stratifier Discovery Methods (2024–2026)

The identification of unobserved subgroups that follow distinct causal or generative processes is a central challenge in both computational mathematics and observational statistics. When evaluating a high-kill cohort of polynomials, the failure of a hypothesized property to generalize out-of-sample strongly indicates unobserved heterogeneity. To discover the hidden categorical variable explaining this heterogeneity, recent literature offers powerful frameworks across latent-class regression, finite mixture models, and causal discovery.

### 2.1 Causal Mixture Models (CMM)
A highly relevant method introduced by Mameche et al. (2025) involves the integration of mixture modeling into score-based causal discovery [cite: 1]. Real-world data often consist of unobserved subpopulations generated by distinct causal mechanisms. The CMM approach models each variable as a mixture of structural causal equation models (SEMs), where latent categorical variables (mixing variables) index the assignment of an observation to a specific subpopulation [cite: 1]. 

Unlike traditional methods that assume a single global mixing variable affecting all observations simultaneously, the 2025 CMM framework allows for multiple independent mixing variables, each affecting distinct sets of observed variables [cite: 1]. The structure of the model is inferred jointly with the mixing variables using a score-based causal discovery algorithm, such as Greedy Equivalence Search (GES), which guarantees consistency in recovering the causal structure [cite: 1]. 

### 2.2 Latent Causal Structures with Discrete Latents
A secondary methodology stems from the identifiability of causal graphical models equipped with discrete latent variables. Lee and Gu (2026) addressed the historically challenging problem of non-identifiability in causal graphs containing unmeasured categorical nodes [cite: 2]. Traditional studies often relied on continuous latent variables with linear additive noise models. However, when dealing with categorical logic (such as whether a polynomial is Salem or non-Salem), discrete latent variables are strictly necessary.

Lee and Gu’s framework establishes conditions under which the entire causal graphical model—both the structure and the conditional probabilities—can be uniquely identified without relying on overly restrictive assumptions like tree-structures or pure-child requirements [cite: 2]. By isolating discrete latent variables $H_1 \in \Omega_1$, this method can mathematically isolate the exact categorical bifurcation that leads to distinct downstream observed phenotypes in the dataset.

### 2.3 Basis Function BIC and PAGs for Nonlinear SEMs
The third method focuses on scalable causal discovery from recursive nonlinear data via Truncated Basis Function Scores and Tests, developed by Ramsey and Andrews (2025) [cite: 3]. When relationships between variables are nonlinear or governed by complex algebraic logic, traditional linear causal models fail. The Basis Function BIC (BF-BIC) and Basis Function Likelihood Ratio Test (BF-LRT) accommodate additive nonlinear structures [cite: 3]. 

Crucially, this method supports latent-variable discovery through the construction of Partial Ancestral Graphs (PAGs) [cite: 3]. PAGs generalize Directed Acyclic Graphs (DAGs) by incorporating bidirectional edges that represent unobserved common causes (latent confounders) and explicitly mapping conditional independencies through m-separation [cite: 3]. 

### 2.4 Prediction for the Mossinghoff Degree-Minima Concentration
Among these three methods, the **Causal Mixture Model (CMM)** proposed by Mameche et al. [cite: 1] is the most likely to successfully catch the degree-minima concentration in the Mossinghoff dataset. 

The rationale is twofold. First, the Mossinghoff dataset fundamentally represents a mixture of two distinct mathematical populations: Salem polynomials (whose Mahler measures follow specific density and trace laws) and non-Salem polynomials. These two groups behave according to entirely different generative mechanics regarding the minimization of the Mahler measure. CMM is explicitly designed to handle unobserved subpopulations (e.g., drug responders vs. non-responders, or in this case, structurally minimized Mahler measures vs. brute-force enumerative minima) [cite: 1]. By treating the "degree-minimum" flag as an observed variable and modeling the latent categorical (Salem vs. non-Salem structural capacity) as a mixing variable, CMM would dynamically partition the structural causal equations. It would recognize that the causal link $\text{Degree} \rightarrow \text{Survival}$ operates under completely different parameters depending on the latent state of the polynomial's root distribution, thereby identifying the hidden stratifier natively.

---

## 3. Statistical Inference on Sparse Cells: Chi-Square Alternatives

The g11 loaders (v1/v2/v4) currently rely on the Pearson $\chi^2$ test to evaluate the over-representation of non-Salem cells at degree minima (yielding $\chi^2 = 191$). However, the contingency tables derived from the Mossinghoff real data are pathologically imbalanced, yielding cell counts such as $8501$, $2$, and $14$. 

The Pearson $\chi^2$ test of independence evaluates whether observed frequencies deviate significantly from expected frequencies under a null hypothesis of independence. A fundamental assumption of the asymptotic $\chi^2$ approximation is that the expected count in each cell must be $\geq 5$ [cite: 4, 5, 6]. When tables contain sparse cells (expected frequencies $< 5$, or zero-cells), the $\chi^2$ distribution fails to approximate the true sampling distribution, leading to heavily inflated Type I errors (false positives) and fundamentally unreliable p-values [cite: 6, 7]. Given the extremity of the $8501 : 2 : 14$ split, the reported $\chi^2 = 191$ is mathematically degenerate. 

To resolve this, robust alternatives for sparse, highly skewed contingency tables must be implemented. Three superior alternatives from 2024–2026 literature are proposed below.

### 3.1 Fisher's Exact Test Extension to $k$ Cells (Freeman-Halton)
Fisher’s Exact Test was originally formulated for $2 \times 2$ contingency tables to evaluate exact hypergeometric probabilities without relying on large-sample asymptotic approximations [cite: 5, 6]. The test determines the precise probability of observing a specific matrix of counts, conditioning on the fixed marginal row and column totals [cite: 5]. 

For $r \times c$ tables (where $k > 4$ cells), the natural generalization is the **Freeman-Halton extension** of Fisher's Exact Test [cite: 4, 8]. The probability of any given $r \times c$ table under the null hypothesis of independence is given by the multivariate hypergeometric distribution:
\[ P = \frac{\prod_{i=1}^r R_i! \prod_{j=1}^c C_j!}{N! \prod_{i=1}^r \prod_{j=1}^c E_{ij}!} \]
where $R_i$ and $C_j$ are the marginal totals, $N$ is the total sample size, and $E_{ij}$ are the individual cell counts [cite: 6]. By summing the probabilities of all tables that are at least as extreme as the observed table, an exact p-value is obtained. As noted by Madadizadeh et al. (2026), this extension is the gold standard for sparse data in medical and epidemiological fields, ensuring strict Type I error control [cite: 4]. However, the computational complexity scales factorially, which can render enumeration infeasible for large $N$ unless optimized algorithms are utilized [cite: 5, 6].

### 3.2 Monte Carlo Permutation Chi-Square
To circumvent the computational bottleneck of the exact Freeman-Halton test while maintaining validity over sparse cells, **Monte Carlo permutation tests** (or randomization tests) are highly recommended. Instead of enumerating every possible contingency table that satisfies the marginal constraints, the Monte Carlo approach randomly samples a large number of tables from the exact hypergeometric distribution [cite: 9, 10]. 

In a recent study by Reiser et al. (2025), Monte Carlo simulations were utilized to assess goodness-of-fit for constrained models on high-dimensional, sparse cross-classified tables [cite: 9]. Similarly, Contadora et al. (2026) demonstrated that permutation theories initially introduced by Fisher can be extended to sparse contingency tables of dimensions $m \times 2$ through simulated resampling, showing identical effectiveness to exact tests without the extreme computational overhead [cite: 11]. In the context of the loader, calculating the standard Pearson $\chi^2$ statistic for $10,000$ permuted tables with fixed margins will yield an empirical, exact p-value that is entirely immune to the breakdown of the $\chi^2$ asymptotic distribution.

### 3.3 Likelihood-Ratio G-Test
The **Likelihood-Ratio G-test** (also known as the deviance statistic or maximum likelihood ratio test) is an alternative to the Pearson $\chi^2$ test that is often better behaved in sparse data settings, particularly when assessing nested models or hierarchical constraints [cite: 9]. The G-test is defined as:
\[ G = 2 \sum_{i} O_i \ln\left(\frac{O_i}{E_i}\right) \]
where $O_i$ is the observed count and $E_i$ is the expected count. Reiser et al. (2025) note that while asymptotic G-tests can still struggle with extreme sparseness, likelihood ratio difference tests between unconstrained and constrained models demonstrate substantially higher statistical power than Pearson approximations in large, cross-classified categorical variables suffering from dilution [cite: 9]. When combined with a Williams correction for small samples, or when its reference distribution is simulated via Monte Carlo, the G-test provides superior theoretical grounding grounded in information theory (Kullback-Leibler divergence) compared to the Pearson metric.

---

## 4. The Palindromic $\equiv$ Salem Equivalence: Fact or Artifact?

The G11 EXCEPTION-MINER ITER-19 finding asserts that `palindromic ≡ Salem-class` within the Mossinghoff dataset, yielding an empirical conditional probability of $P(\text{Salem}|\text{Palindromic}) \approx 0.9999$. This observation must be critically evaluated to determine whether it is a substrate-grade enumeration artifact or a deep mathematical fact.

### 4.1 The Mathematical Necessity of Reciprocity (Palindromic Structure)
In algebraic number theory, a **Salem number** $\tau$ is defined as a real algebraic integer $\tau > 1$ such that all of its Galois conjugates (excluding $\tau$ itself) have a modulus less than or equal to 1, with at least one conjugate having a modulus exactly equal to 1 [cite: 12]. 

Because at least one conjugate lies on the unit circle (i.e., $e^{i\theta}$), complex conjugation implies that $e^{-i\theta} = 1/e^{i\theta}$ is also a root. Through Galois theory and the properties of irreducible polynomials over $\mathbb{Q}$, if an algebraic integer has a root on the unit circle, its minimal polynomial must be highly symmetric. Specifically, it is a proven, foundational mathematical theorem that **the minimal polynomial of a Salem number is reciprocal** [cite: 12, 13]. A polynomial $P(z)$ of degree $d$ is reciprocal (palindromic) if it satisfies the condition $P^*(z) = z^d P(1/z) = P(z)$ [cite: 12]. This implies that its coefficients read the same forwards and backwards [cite: 12]. 

Therefore, the statement that *all Salem polynomials are palindromic* is an absolute, unavoidable mathematical fact [cite: 12, 14].

### 4.2 The Enumeration Artifact: The Inverse Probability
While all Salem polynomials are palindromic, the inverse statement—that almost all palindromic polynomials are Salem polynomials ($P(\text{Salem}|\text{Palindromic}) \approx 0.9999$)—is mathematically false in a global sense, but locally true within Mossinghoff's dataset. This is a pure **enumeration artifact**.

Mossinghoff’s dataset is constructed to test **Lehmer's Conjecture**, which asks if there exists an absolute constant $\mu > 1$ such that the Mahler measure $M(P)$ of every non-cyclotomic polynomial with integer coefficients is at least $\mu$ [cite: 15, 16, 17]. The smallest known Mahler measure belongs to Lehmer's polynomial of degree 10, which yields $M \approx 1.17628$ [cite: 12, 17]. 

To search for counterexamples, computational mathematicians like Mossinghoff restrict their search space to families of polynomials most likely to yield low Mahler measures. These searches heavily target:
1.  **Littlewood polynomials** (coefficients restricted to $\pm 1$) or polynomials with restricted heights (e.g., $0, \pm 1$) [cite: 18, 19].
2.  **Reciprocal (Palindromic) polynomials**, because non-reciprocal polynomials have a known, higher theoretical lower bound for their Mahler measure (Smyth's theorem states that non-reciprocal polynomials have $M(P) \geq \Theta_0 \approx 1.3247$) [cite: 20, 21]. Thus, to find a Mahler measure $< 1.30$, the search *must* be restricted to reciprocal polynomials.

When generating millions of reciprocal polynomials of fixed degrees with small coefficients, the vast majority of those whose roots do not explode outward (thereby keeping the Mahler measure small) happen to be products of cyclotomic polynomials (which have $M=1$) or Salem polynomials. If the dataset specifically curates polynomials that survive the filter of $M < 1.30$, the cohort is artificially purged of generic palindromic polynomials with roots far off the unit circle. The $0.9999$ equivalence is simply the algorithmic footprint of Smyth’s theorem dictating that only palindromic polynomials can possess the targeted low Mahler measures, and within that tight algebraic space, Salem polynomials are the dominant non-cyclotomic inhabitants [cite: 22].

Recent 2024–2026 literature supports this tight clustering. Research by Cherubini and Yatsyna (2024) [cite: 14] and subsequent classifications of short Salem polynomials (length 5 and 6) [cite: 12] highlight that the space of small-height, reciprocal polynomials is entirely dominated by Salem numbers and specific Pisot sequences approaching them [cite: 12].

---

## 5. Specification for v2 Loader Design (g11 v5)

To upgrade the G11 EXCEPTION-MINER from v4 to v5, we must eliminate human-supplied tautologies (like the boolean cubes) and implement robust, mathematically generalized discovery pipelines. The g11_v5 specification requires three fundamental pillars: exact statistical testing, enriched latent-class regression, and automated unobserved stratifier discovery.

### 5.1 Primary Statistical Engine: Likelihood-Ratio G-Test
The core contingency evaluation must abandon the uncorrected Pearson $\chi^2$ test.
**Decision Rule 1:** For any proposed categorical stratifier, construct the $r \times c$ contingency table. Calculate the expected cell frequencies.
*   If $\forall i,j \ E_{ij} \geq 5$: Compute the standard Likelihood-Ratio G-test [cite: 9].
*   If $\exists E_{ij} < 5$: Trigger a Monte Carlo Permutation G-test. Generate $B = 10,000$ random contingency tables with identical marginal totals using the Patefield algorithm. Calculate the G-statistic for each. The empirical exact p-value is the proportion of simulated G-statistics greater than or equal to the observed G-statistic [cite: 9, 10].

### 5.2 Latent-Class Regression on a Richer Feature Set
Currently, the loaders rely on trivial flags (palindromic, degree minima). The v5 loader must map the deeper arithmetic geometry of the polynomials. We implement a finite mixture model / latent-class regression [cite: 23, 24, 25] over the following feature vector for each polynomial $P(x)$:
1.  **Degree ($d$):** The algebraic degree of the polynomial.
2.  **Mod-$p$ Reduction Splitting Patterns:** Evaluate $P(x) \pmod p$ for the first 20 primes. The degrees of the irreducible factors modulo $p$ correspond to the cycle types of the Frobenius elements in the Galois group (via Chebotarev's Density Theorem).
3.  **Galois Group Size/Transitivity:** A proxy derived from the mod-$p$ cycle structures. Salem polynomials often have highly restricted Galois groups (e.g., subgroups of the hyperoctahedral group) compared to the generic symmetric group $S_d$.
4.  **Root-Distribution Shape Moments:** Calculate the variance and skewness of the angular distribution of the roots lying on the unit circle.

**Decision Rule 2:** Fit a 2-class and 3-class Latent Class Regression (using EM algorithm [cite: 25]) predicting the continuous Mahler measure $M(P)$ using the enriched feature set. If the Bayesian Information Criterion (BIC) favors the 2-class model over a single-class model by a margin $> 10$, extract the latent class assignments as a new candidate stratifier $H$.

### 5.3 Automatic Stratifier Discovery (No Human Cubes)
To prevent tautological human injections (e.g., Salem $\times$ Smyth cubes), we implement Causal Mixture Models (CMM) [cite: 1].
**Decision Rule 3:** Feed the enriched feature set, the survival outcome, and the latent class assignments into a Greedy Equivalence Search (GES) algorithm parameterized for Partial Ancestral Graphs (PAGs) [cite: 3].
*   The algorithm must search for conditional independence structures. If a latent categorical node strictly m-separates the feature set from the survival outcome, it is flagged as a mathematically native "Hidden Stratifier."
*   *Rejection Criteria:* If the discovered stratifier yields an `out_of_sample_failure` on a held-out testing set of polynomials (e.g., fails to predict survival in degrees $> 60$), the stratifier is logged as an anomaly/artifact rather than a theorem.

---

## 6. Cross-Domain Stratifier Generalization

The methodologies of EXCEPTION-MINER can be ported to other branches of mathematics involving vast computational datasets with unresolved conjectures. We propose generalization analogs for the Birch and Swinnerton-Dyer (BSD) conjecture and Knot Theory.

### 6.1 The Birch and Swinnerton-Dyer (BSD) Domain
The BSD conjecture posits that for an elliptic curve $E$ over $\mathbb{Q}$, the algebraic rank of its Mordell-Weil group $E(\mathbb{Q})$ equals the analytic rank (the order of vanishing of its Hasse-Weil L-function $L(E, s)$ at $s=1$) [cite: 26, 27]. Datasets like the LMFDB catalog millions of curves.
*   **Stratifier 1: Rank Parity Discrepancy Flag.** While BSD implies $r_{alg} = r_{an}$, the Root Number (the sign of the functional equation of the L-function) determines the parity of the analytic rank. A stratifier identifying curves where the computational bounds on the Selmer group suggest an algebraic parity mismatch with the root number would yield massive heterogeneity, identifying curves where the Tate-Shafarevich group ($\text{Sha}(E)$) is behaving anomalously [cite: 28, 29].
*   **Stratifier 2: Tate-Shafarevich $p$-Divisibility Flag.** The order of $\text{Sha}(E)$ must be a perfect square. A latent categorical stratifier separating curves where $|\text{Sha}|$ is divisible by specific primes (e.g., $p=2, 3$) versus trivial $\text{Sha}$ will deeply partition the dataset's algorithmic survival rates, as $p$-descent algorithms notoriously fail or compute indefinitely on non-trivial $p$-primary components [cite: 26].
*   **Stratifier 3: Tunnell Congruent Number Isogeny Flag.** Elliptic curves of the form $y^2 = x^3 - n^2x$ are tied to the congruent number problem [cite: 27]. A stratifier flagging curves with rational 2-torsion points combined with specific modular forms of weight 3/2 could isolate high-kill subsets where standard L-function coefficient generation algorithms suffer from precision loss [cite: 27].
*   **Prediction:** Stratifier 2 ($\text{Sha}$ $p$-divisibility) will yield finding-worthy heterogeneity. Because elements of the Tate-Shafarevich group represent torsors that are locally soluble everywhere but fail to have global rational points, computational solvers will consistently timeout or "kill" these curves, making $\text{Sha} \neq 1$ a perfect hidden stratifier for algorithmic failure.

### 6.2 The Knot Theory Domain
In computational topology, millions of prime knots are tabulated, with invariants like the Jones polynomial, A-polynomial, and hyperbolic volume computed. Boyd [cite: 17] established deep connections between Mahler measures of A-polynomials and hyperbolic volumes.
*   **Stratifier 1: Hyperbolic vs. Torus/Satellite Flag.** Separating knots based on Thurston’s geometric decomposition. Non-hyperbolic knots will show immediate survival anomalies in algorithms optimizing for hyperbolic volume boundaries.
*   **Stratifier 2: A-Polynomial Mahler Measure / Volume Defect.** A stratifier based on the ratio of the Mahler measure of the knot's A-polynomial to its hyperbolic volume ($\pi \log M(A) / \text{Vol}(K)$). Boyd discovered that for certain knots, this ratio yields integers or rational numbers [cite: 17]. A flag separating rational vs. irrational ratios would expose hidden arithmetic structures in the knot complement.
*   **Stratifier 3: Alternating vs. Non-Alternating Flag.** Alternating knots have highly predictable minimal crossing numbers and Tait graph structures.
*   **Prediction:** Stratifier 2 (Volume Defect) will yield the highest heterogeneity. The intersection of hyperbolic geometry and algebraic Mahler measures is highly constrained; knots satisfying rational ratios represent a rare, highly structured mathematical minority that will heavily skew any contingency tables evaluating volume optimization algorithms.

---

## 7. Contrarian Analysis: The Degree-Minima Finding as a Selection-Bias Artifact

The live finding that "non-Salem cells carry degree-minima at 59-77$\times$ expected rate (PROMOTED $\chi^2 = 191$)" is highly provocative, suggesting a deep mathematical link between non-Salem polynomials and the absolute minimum bounds of specific dimensions. However, as an expert reviewer, it is crucial to steelman the contrarian hypothesis: **This result is entirely driven by the algorithmic selection bias of Mossinghoff's search methodology, not by a real underlying mathematical structure.**

### 7.1 Steelmanning the Selection-Bias Artifact
Mossinghoff's research is dedicated to finding the absolute minimal Mahler measures for polynomials of a *fixed degree* [cite: 30]. To achieve this, algorithms utilize Graeffe root-squaring, LLL lattice reduction, and intensive coefficient searches over constrained sets (e.g., $\{ -1, 0, 1 \}$ Littlewood polynomials) [cite: 18, 19]. 

When the algorithm runs for degree $d$, it exhaustively combs the space and halts, outputting the polynomial with the lowest Mahler measure for that specific degree. 
1.  **The Salem Dominance:** For most even degrees, the absolute minimum Mahler measure happens to be a Salem polynomial, because Salem numbers inherently pack their roots on the unit circle, generating the smallest possible non-trivial Mahler measures mathematically allowable [cite: 17, 30].
2.  **The Non-Salem Degree Minima:** However, Salem numbers do not exist uniformly across all degrees and trace combinations with arbitrarily small measures. If a specific degree $d$ geometrically lacks a "small" Salem polynomial, Mossinghoff's exhaustive search will inevitably select the *next best thing*—a non-Salem polynomial (e.g., a Pisot number or a generic reciprocal polynomial) that happens to be the minimum for that degree.
3.  **The Statistical Illusion:** Because Salem polynomials naturally possess lower measures, they dominate the entire catalog of "low Mahler measure polynomials." Therefore, non-Salem polynomials are globally rare in the dataset. But *why* are non-Salem polynomials in the dataset at all? They are only recorded because they were the absolute "degree-minima" for degrees where Salem polynomials were absent. Consequently, 100% of the non-Salem polynomials in the dataset might be degree-minima, creating a massive, inflated $\chi^2$ statistic (59-77$\times$ over-representation). 

The anomaly is not that non-Salem polynomials inherently "prefer" to be degree-minima; rather, it is that Mossinghoff's algorithm only bothers to record a non-Salem polynomial *if* it is a degree-minimum. This is the textbook definition of collider bias or algorithmic selection bias.

### 7.2 Conclusive Distinguishing Check
To conclusively distinguish whether the 59-77$\times$ representation is a mathematical reality or a selection bias artifact, we must completely decouple the dataset from Mossinghoff's "record-keeping" search parameters.

**The Monte Carlo Uniform Sampling Check:**
1.  Define a bounding box for polynomial coefficients (e.g., degree $d \in [cite: 21]$, coefficients $c_i \in [-2, 2]$).
2.  Uniformly sample $1,000,000$ random reciprocal polynomials within these bounds, completely ignoring whether they are "degree-minima."
3.  Calculate the Mahler measure for all generated polynomials and filter for survival ($M < 1.30$).
4.  Within this unbiased, out-of-sample survival cohort, cross-tabulate Salem vs. non-Salem status against their proximity to the theoretical degree-minima. 

If the $\chi^2 = 191$ over-representation vanishes and non-Salem polynomials are distributed uniformly across the Mahler spectrum relative to their degree, the original finding is proven to be a selection-bias artifact. If the non-Salem survivors *still* cluster exclusively at the absolute lower boundary of their respective degrees, then the finding indicates a true, undiscovered topological constraint in algebraic number theory. Given the structure of causal discovery [cite: 2], evaluating this synthetic interventional dataset will uniquely identify the direction of the causal arrow between the algorithmic selection mechanism and the mathematical phenotype.

---

## 8. Conclusion

The application of latent-class regression, causal mixture models, and exact statistical techniques provides a transformative lens through which to view legacy computational mathematics datasets. The G11 EXCEPTION-MINER framework successfully highlighted anomalies in the Mahler measure distributions of Salem polynomials. However, as demonstrated in this report, the intersection of pure mathematics and data science is fraught with enumerative tautologies and selection biases. 

By replacing asymptotic Pearson $\chi^2$ tests with Monte Carlo G-tests, substituting human-supplied boolean cubes with Causal Mixture Models [cite: 1], and recognizing the definitive mathematical reciprocity of Salem minimal polynomials [cite: 12], the next generation of loaders (g11_v5) will effectively separate profound mathematical truths from algorithmic artifacts. Extending these exact, causal frameworks into elliptic curve cryptography (BSD) and topological knot theory promises a fertile ground for the future of automated mathematical discovery.

**Sources:**
1. [cispa.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBfnEGRspXppinswh8b7VLQP5YDJ7UQ3eiwPxzSlfBEven_gjzbmlmhDEIhpfEFkKjarkSvFQ9JdTzeR1P5_8BmlAodvbBefr4lIbSqtuY7JItm_cDiARtC5qqudj_gB1DaovoOW-0kPn52lJNE4RwUsYJPeW7Tehz4g==)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuL03APg-K0fe0tR-Xsmrv7UuGo5uuhqiJJX_hZzUqykYH_hmvUUErfk09fwF1ZhXglr3_Ja-Qx48dv4vCOn0Qz_dsRyuNmKzsAZKMjbFHid052iLZV7wpDg==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrHMiQptE-wSBdNUXz5EV-BhhL2CeEFw_uGTS0pE2YCAynJ_CsyVPBoDG8gz3JjQnQCh7bmgY4R9y8tU7yLutfJjBHzR6AYFmESU4w_TqB7XsMWznp5HKUow==)
4. [riverpublishers.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEF4PFpxG5LzrHP2ZwNYWqy9ec-RrlPLT-4G9O2nfvPSwPdn6SHUoISA1SFsBEdvPcF73y7TNtw6_Tk_jIOiq5hnH2fRA_Q1Gl8jm6c-6rsr7QDCjZP6ZS8sEb9EpwNR3Lf0twliJDqYULW8SPxJdk5DZPUQi3UtZNPdZtodPRqJE1T)
5. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfNa48GnBZeuyGioIEDyaKaMA4F4Q0WmcK6yB15Cc7ctyS1ZLf4GgKZQV7BKDltV1_Q8soebV-igLH61o_XPimiSwiBgwn7hKfAFOgJa6wkuxpAFFzF_b6kw0OIeALIzXPIcO1_Xp8f0GMCA==)
6. [metricgate.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEx7UGgDNNS8Al7iwcqTzBVJV7hSN4d6TGASM9C1FxDf0FJkq9UGv3GcUVUSXX1LWI5TO_xBa2R40jhknMeIUuAF7vbzodsD5h2p776iy9Xq6B7GScbpjeDhFFkGVck8XsD6gNs0fIgbOPUCbg-E4DBo8W0Tg==)
7. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFs24JFqjHtnPzIB90e4x3-33xiHHrzp1LFKmE5JMqacAMDeKJ0t1MVyMY2duZjnOfRJCB3baenZ1e2D9A6f03J5XJrtYv9JhHxhNq1ozF9brDxVfKEsgMYoX4ad2Xw29ylZ92GueEVA==)
8. [datacamp.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGuScTr-ToOMugTg46ou_7J8KYLSRCjlo9P7zGQ9xQcVSYw66sH59nj-GlZY7LuUHCokJ78m3C5cRGbGwgMgMz12Gdkwxcx8TO8aXnC_sezduiCNP6ETuVfVBeGpAKP-9jdEk1lAb0ryPaV)
9. [figshare.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFduXkrJ2qyDU733vrP_QTbA2KPSJICLQqc7KBdb4lSFJEy31-mZSlkjnS0Nro1_sQZmX8vVvOzroyiL0Ux_D5owhMdHiGsoALwRQn0Hq-iOk515e5sc2Jovt6wsdSNySd0iAGrt3LLc77SbgHXpIDb1-thDBEvv9QcmG-LolGQRm0p99MSoNWysXUoXsj3TEbpvzV0pJGb1rmkSw60e0luxRVd-Al6RGV07Yyb3jcc2xK4rFqX6p9dyN8Ea-kUlAywjH7RmA_sObxGEGCG4XQg3Hl8kK32oUejrV-BckYmeEo2EbAgltMK3g==)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLscJvxxHmkpqBBRXsdoqETu8ikOZZiTh8i6jD3YZKGVNFwnXC4ja3B8UClyUWDEK5qVdPQD7L_qzmoNhfFG7eaV14GMP6eXTI80fYYMp4W7eDFmEtjNS3MkxUhuLYR8TB_DCOAyhGsL3HHN4FTJVbNE-dF6mcUFkNLcLlnQ0tUNNBOa_8h4OINnatub8wQ1vSupJX3Pa30syx2Vo-1u-DkLcRjCy2WYqVKheKLqyzGg_zqwzBnhBG)
11. [periodikos.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPDs0P-tyNDWrKT26YhNVBsUHFBizcZawE9Wc-3QU4g2aPnjLEX8iAaXWYyr33pJzA3jeJegPjyVLu3CAWhlL77kqyD8XMJCL9ehTPB_WnMnBeMl3APT9ikty9P70vBPtZDGRJvH8gXz2gIbgWKSxeSA1ZVFZFI7uYCUoDCAtBNu123YuaOP4O3LvkUIMYGlrwGeOk4qA=)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhf8g1TD6gE0OEBDw2q_Sc_qHa5kjNCRwuQk6mAHKvEykGdfKj0PuYcZrt0IAAJRL-QDTGgzVYdAQvHNUHSDnTnVv1Qb2OgdWEPRJkqHP2CmDrLL9uG2lU4w==)
13. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFd_ppvEs4Hn4RQ9ORuaPtcddUmyZrl86KnwP6lN8zrqAyx7mUhBH2Zt5Y67sAf2eqgqLLE_KoRoyYvgy_BCDYMPsa2c3CmOo_VWi2Ayoceo4ohctCDQeQ17jsx6nHQedHId-Af0KoaFMwQvbhDsbgHUfYu9-GF3KGNILF8lL4FzmWdk4zRQo5IqNruhFNyghuTPskJIb2uusezbfFbPmpRCuEPotPd46eL4iqZVK1Lj67LeC3XzV7_j_khFDgdFJlEf1y4PscqxVsSRg5TwkRer5ZvKEv797e45eV4Igs5XmI4C8IEidYCt58HyHDDeElT)
14. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEg5anZbLEkGhtl8-5N7oSp0Qb55H8SEQLiunqatj2doLoCAbWBEPncI6n4kyurcdIRcWwkQM_Wg8Uq_ZbfLGUEdtbevN70jKn4dRIXiDDjeP7D7sDu0PKkXA==)
15. [uni-goettingen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjAMHJAu8_SvRSsNMdbA_FlpOlVC_-cro8H0T4vseuuYVN07LWQz4T-HMW83MOwbxeNboC3c0eXmKmPQZBi7qBEoXP9fYrrab4X_5XgMNdLa1oPsZ5RQwHo91NrjhYyC6hn96RwZshZYMu-bkYD_ls0lm_O9q_79YWXKL9FPTZV-e7j8EywE2_wgje8dqcNNd3-i8QUQjVS2eDugxZQCOXnziZ4nNw)
16. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZvqLP8DZkXvsZNr4-YBkXTmdz6oU0sOnxgstU3-xUcU5d6vN3vUgWtBwE30dZwDkzoKFQVi-JMX8NsYwRjIm-4jPcw2cxcPFyVvDLHyX4wALMJn30us4ZoFtxszlYWW53gCYjuv50-pE=)
17. [umontreal.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjOFHX_8-bfoZbDtwsI56MsXrjae38RjDCgrWRyO_FJl83O87Eni54LHdXrTUdtPnjbzJ5NJ7PdEe3_psVIBVxoM4H2i0jzMgT7tvmmlQx_JY2Zq58F1HtNHJKTZ9Y)
18. [sfu.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE56gcv36hhKFlfe_1etMRTGmlosG3vIvvIqIIZGbdX8FujLchYnwaERnGJCYCv9yN8TIgWTH-5ttJYwlYINTLW3UfYniq_AjVhHZRvZi_s4MsknqocoWBcq83IuPU7GP7OgFPP4RJNIw==)
19. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkEA9_NgzeTVW9PwpEKBpo_b4Jny6Y8sn3IInWx7Y3Z6ofsm8gp8uhcNtwFTf9LU7885wQBWvVl7hShNMWqWW6-jqBIlh2FDNFPu1jM3RmC3xY0ZXCTs_yLt6UUrKEkxIuuEjzyNs7KA==)
20. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwiKx4AbHq485N5jIhu_tCibqvXz0HqFLIp6qji6baEyrfkoQy6QDhqbL5HlkDheYHZzPl49uxdt2oSIlOnxOybogR9V9iGjsPwHrVikmHX6VhS_CU3ZfqaC15hAfzSYcP4z7lCe2K8MQx4AFz4bTEKD9me0pVwc0=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3i04tnsQJBqcUIm2GYUXTCJO36qzQdad3rXDqsCgtQY353Ig_hHhpuN9VUf22C4PXxmbpdEEsfYKleliLXSY7grc7qBNZ5DxMeppb5fIFuVGKtRniNg==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTDVaxqoOmVto3ChWtjr7Z9NlciZ0gH1XbEgJn0QbC7urvPz2wlzS6qOmJlag4uCMcwTBVJ10yJUu4lnejV09q7Z-YuP7YYJcuDaCqFQZDslqZ8WUdI5pODYViUcOBvZZGWLCNzwxztcrXj3Mh5_bzjq4n47gT2HVQXYNIRmkPrSUfvHEn9uYyi6fuwt2VivoOJ7hn0A==)
23. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrQwhpobzoMHOKYiO1JzIEZfhzGU_jV8XL3lopDtfGevEcOO4sjqQBB0TpEGYEfUAt86ED1qzdD6ChSs2lz9fpuvTZlfC0A5LfAcsMBNdOch1Htlt30JDC1FmZeGwrAg==)
24. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEkP8m0S7H59Uv41JAO-JV6XlksBk4dSAcOEt7B5lFDTSzEPFUde_v5bZkaeF5PZSL6pkCkpHVzWKNnRPStHrqeeThKAmpAVA7tgMK-LFyoOzOdHwdjytvaR_mOsv8xWW4Mfe34Ju4QHA==)
25. [repec.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL9YnK95l1G0UHgdz5rG5OX0DtCioYBo_nvaxUxnev6uae3knLE8_YR13kprz1J4tOUiBDZvSAboMAg8RsIVd3xkNVLbud0CE8kDTmdkv-UpB4E63x3bA2nL4B7ZbQUnVDWdBSOuMsuO0GN-AbZznqRUMoLpR86NeT5l-l)
26. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEqLKrqrizkv7a-ewArKW7XbsWy4wjKXd2RB7k4Ly-aHqZD2a5JqEXZkWV9qW5cWK_MSYTCzF1bPYjSb6CnshGgiT7K6gLRvcEIijNzxSsHjXdmJcytpYnrmctCIq0HWUyY2CM22la5_syBD8HZ3brdL7m2xQRL2nGaGkECIZZMT4mbz1Z1Qa4yIH3YtWLaPnf1g==)
27. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG47RMHHKGVWrRF8-YSA0TGd74IWEbdhtsJmgW2WuB2LkUTetxvF3sabqsguBB36CdIUBVUtQMLXZVBih2tgPKP8GF9AAliaUkLFZmlvgpbWTVTPMn6_2jf0Rqe-C7T0Yo0pDqxmk6vRdyOVCQlzLSu9e-6klPesbI=)
28. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4rCJLKn5DIcwLwFP3NBGSaNJDMPw4Fgy1MG2QY99_MaGdPjEup11WISq8AK9JuwjvcyJ7kVwS8Po6FV6n_UQUx07ETS7FKKsrO8nqE-KDeiqjSnMFPf-r3PlSKiYU_ajToPfQf2v6g1BjvlR-qB8-8yo-MM7DsPufnnoQrHYDgWjfgw==)
29. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbF80_B0Z7QpHSeKseeUvokyg7alyQfCRbtCma3ipV9Qd1qMeRY_SOFCXaYn3m8u7vJW3DKL1_LYDBNLbY33s51u-J1QM751cvcqY762lJ9FtTRCnrseLxcNZhe-2PhpJO72hpW-kr0rR5K4DV5L862Vx0hMm15-BqVdT6VVOGS9mmxi1LhJEq66ExWed7bVavebKcZGNekAmxEsykPkY=)
30. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6d75CDAikeriy4s_7K9ngCuf7Ic71zb8LDTewBT8FNJ1gQKPgKuBXrFb3RCB_uhI3cHYzfCtZahPVL52Vl8GYPZ6lWT8Z9M3s8oF7NlTl1B-uw4Ff8E7WnvcSDCNTsuWBIC3jobHA7JmLd5BOHpPCR3UrFBYQqF6yPB1DodEChwVb7yQpP27_zLqMpn5aYJuiGyuCOHy7RtUudGjQuZI8eRdnS2rbAn2SK2uKZOE=)


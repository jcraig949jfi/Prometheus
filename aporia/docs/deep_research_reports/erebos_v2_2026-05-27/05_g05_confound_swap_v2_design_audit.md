# Prompt 05: G05 Confound-Swap — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChY3NElXYXZ1Wk1KZThqckVQMjctek1BEhY3NElXYXZ1Wk1KZThqckVQMjctek1B
**Elapsed:** 306s

---

# Structural Causal Inference in Discrete Mathematical Contexts: Overhauling the G05 CONFOUND-SWAP Architecture

### Executive Summary
*   **Confounding in Pure Mathematics:** Causal inference on deterministic mathematical objects (e.g., elliptic curves, polynomials) is an emerging paradigm. Research suggests that traditional sample-based confounder adjustments must be replaced by continuous optimization and categorical frameworks.
*   **The Heuristic Failure of v1:** The current v1 G05 loader utilizes an argmax-|value| heuristic. The evidence leans toward this being fundamentally flawed, as covariate magnitude conflates topological scale with structural causal influence.
*   **The Power of Stratification:** For discrete mathematical catalogs like the Mossinghoff polynomials, stratification appears to be the most robust method for isolating true causal signals, whereas Propensity Score Matching (PSM) is highly susceptible to collider bias.
*   **The Inverse Problem:** The discovery of "suppressor variables"—which mask true signals rather than creating false ones—requires an entirely new pipeline module, mirroring the logic of confounder identification but focusing on negative indirect correlations.
*   **Categorical Causality:** The philosophical objection that one cannot "intervene" on a pure integer is resolved by Topos Causal Models (TCM). It seems likely that interventions in mathematical spaces can be rigorously defined as subobject classifiers within a category-theoretic framework.

### A Primer for the Layman
Imagine trying to figure out if wearing a certain type of running shoe causes people to run faster. If you just look at data, you might see a connection. But what if only professional athletes buy those shoes? The "professional athlete" factor is a *confounder*—it causes both the choice of shoe and the fast running speed. In the real world, we deal with this by randomizing who gets the shoes, or by carefully matching amateurs with amateurs and pros with pros.

Now, imagine we are not studying people, but abstract mathematical objects, like prime numbers or complex geometric shapes (knots and curves). Sometimes, an algorithm thinks it has found a deep mathematical "cause" for why a shape behaves a certain way. Our system, the **G05 CONFOUND-SWAP**, is designed to double-check these mathematical claims and ensure there isn't a hidden "confounder" confusing the algorithm. However, mathematical objects cannot be randomized in a laboratory. The integer 7 is always the integer 7. This report details how we must upgrade our causal inference systems to handle these immortal, unchangeable mathematical entities using cutting-edge statistical and topological techniques.

---

## 1. Introduction: The Epistemology of Mathematical Confounding

The application of structural causal inference to pure mathematics represents a profound methodological shift. Historically, causal inference has been relegated to the empirical sciences—epidemiology, economics, and psychology—where the Potential Outcomes framework (Rubin causal model) and Structural Causal Models (Pearl's DAGs) are used to untangle physical and social phenomena [cite: 1, 2]. However, the rise of large-scale discrete mathematical catalogs, such as the L-functions and Modular Forms Database (LMFDB), the KnotInfo atlas, and databases of Mossinghoff polynomials, has necessitated the development of "algorithmic conjecture generation" systems [cite: 3, 4, 5]. 

When machine learning models generate hypotheses over these catalogs, they frequently fall victim to structural confounding. A neural network might identify a specific structural property $X$ as the "cause" of an arithmetic property $Y$, completely missing that a deeper, unobserved topological invariant $Z$ rigidly dictates both. The G05 CONFOUND-SWAP plugin was designed to serve as an automated falsification engine to catch these spurious signals. However, its v1 architecture is severely constrained by empirical heuristics (such as the `argmax|value|` selection) that lack a rigorous grounding in the geometry of deterministic data-generating processes.

This report comprehensively overhauls the G05 architecture. By engaging with 2024-2026 primary literature, we construct a v2 specification that abandons magnitude-based heuristics in favor of continuous DAG optimization [cite: 6, 7], integrates Topos Causal Models (TCM) to resolve the philosophical paradox of mathematical interventions [cite: 8, 9], and formally distinguishes between stratification, randomization, and Propensity Score Matching (PSM) in the context of Lehmer's conjecture.

---

## 2. Confounder Identification for Mathematical Objects (Task 1)

Standard PSM and Inverse Probability Weighting (IPW) techniques assume sample populations drawn from independent and identically distributed (i.i.d.) random variables. Mathematical catalog entries—such as Birch and Swinnerton-Dyer (BSD) curves, knots, or modular forms—are fundamentally not "samples." They are exhaustive, deterministic instantiations of logical rules. They represent the entire population of their respective parameter spaces. Therefore, standard confounder adjustment must be adapted to continuous functional spaces, topological redundancy, and spectral geometry.

Below is a survey of three methodologies published between 2024 and 2026 that adapt confounder adjustment to deterministic/mathematical catalogs.

### 2.1. Synergistic-Unique-Redundant Decomposition (SURD) for Deterministic Systems
In 2024, Martínez-Sánchez et al. introduced the **Synergistic-Unique-Redundant Decomposition (SURD)** framework for causality [cite: 10, 11]. While originally applied to complex aerodynamic and turbulence systems, the SURD framework is explicitly designed to handle deterministic, nonlinear systems where traditional probability-based interventions fail [cite: 11, 12].

*   **Target Catalog:** Knot theory (e.g., KnotInfo) and bounded discrete topological spaces. In knot theory, calculating the Jones polynomial or the Khovanov homology involves highly overlapping structural inputs [cite: 3].
*   **The System:** SURD (Synergistic-Unique-Redundant Decomposition).
*   **The Adjustment Operator:** Information-theoretic redundancy decomposition. Instead of traditional IPW, SURD quantifies causality as the increments of redundant, unique, and synergistic information gained about future topological states [cite: 11]. The operator isolates "unique causality" by systematically subtracting the redundant Shannon information shared by highly correlated mathematical invariants (e.g., crossing number and unknotting number) [cite: 10, 12].
*   **Kill_Pattern Equivalent:** `redundant_causation_flagged`. This pattern triggers when the candidate cause is shown to be purely redundant with a known foundational invariant, collapsing the unique causal signal to zero.

### 2.2. Functional Covariate Adjustment via Riesz Representers
Mathematical objects like vectors of knot traces, representations of modular forms, or sequences of polynomial coefficients are highly structured, infinite-dimensional objects. In 2025, Kurisu, Otsu, and Xu extended causal inference to nonparametric functional covariates [cite: 13]. Concurrently, Schmitz (2026) introduced Riesz representer frameworks for unconfoundedness in complex feature spaces [cite: 14].

*   **Target Catalog:** Modular forms and Fourier expansions. A modular form can be represented as an infinite series $f(z) = \sum a_n q^n$. The sequence of coefficients $\{a_n\}$ acts as a functional object.
*   **The System:** Nonparametric Functional PSM / Riesz Representer Networks.
*   **The Adjustment Operator:** Reproducing Kernel Hilbert Space (RKHS) Propensity Weighting. Standard scalar PSM fails on infinite-dimensional objects. This system uses an RKHS kernel to map the functional structure of the mathematical object into a continuous space, allowing for the calculation of a functional propensity score. The adjustment operator is an inverse probability weighting applied in the RKHS continuous limit [cite: 13].
*   **Kill_Pattern Equivalent:** `functional_confound_collapse`. Triggered when controlling for the infinite-dimensional geometry of the mathematical object completely explains away the apparent scalar correlation.

### 2.3. Causal Riemann-Surface Operators (RSCO) for L-Functions
In 2026, Liu developed a highly specialized causal framework for elliptic curves and their corresponding L-functions in the context of the Birch and Swinnerton-Dyer (BSD) conjecture [cite: 15]. This framework utilizes causal boundary conditions on Riemann surfaces to establish spectral independence.

*   **Target Catalog:** Elliptic curves (e.g., LMFDB curves like conductor 256) and the BSD conjecture [cite: 15, 16].
*   **The System:** Causal RSCO (Riemann-Surface Causal Operator).
*   **The Adjustment Operator:** Spectral parameter matching (J-self-adjoint analytic pencils). The method avoids traditional statistical confounding by forcing a causal response kernel on the Riemann surface of the square-root function. If a supposed heuristic "cause" of an elliptic curve's rank is proposed, this operator applies a boundary-conditioned spectral truncation to determine if the arithmetic and analytic ranks remain matched without the heuristic [cite: 15, 17].
*   **Kill_Pattern Equivalent:** `spectral_incompatibility`. This pattern triggers when the rank mismatch $r_{alg} \neq r_{an}$ demonstrates that the proposed causal variable violates the temperedness condition of the automorphic distribution, proving it to be a spurious covariate rather than the structural determinant.

---

## 3. The Fallacy of the Argmax-|Value| Heuristic (Task 2)

The current v1 MVP of G05 relies on a sorted-key heuristic: it identifies the highest-magnitude numeric covariate in a claim's payload and selects it as the candidate confounder (`argmax|value|`). This approach is epistemologically and mathematically flawed.

### 3.1. Why Argmax-|Value| is Wrong
The magnitude of a mathematical covariate has absolutely no correlation with its topological position in a causal Directed Acyclic Graph (DAG) [cite: 18, 19]. 
1.  **Conflation of Scale and Structure:** In number theory, a polynomial's trace or its discriminant might possess massive scalar values (e.g., discriminants of high-degree algebraic numbers), while the actual causal driver—such as a specific symmetry group or a binary Galois property—may be represented as a 0 or 1.
2.  **Collider Bias Vulnerability:** High-magnitude variables are often downstream "sinks" (colliders) where multiple causal pathways accumulate. Conditioning on an argmax collider will inadvertently open backdoor paths, creating phantom correlations rather than identifying true confounds [cite: 20, 21].
3.  **Mediation Misidentification:** The argmax feature might simply be a mediator (a mechanism on the causal pathway). Controlling for a mediator suppresses the true causal signal, leading the G05 loader to falsely emit a `complete_signal_collapse` kill_pattern and wrongfully invalidate a true mathematical discovery [cite: 22, 23].

### 3.2. Causal Discovery Recommendation: The NOTEARS Paradigm
Instead of relying on magnitude, published causal-discovery methodology dictates the use of data-driven graph structure learning. While constraint-based algorithms like the PC algorithm rely on fragile conditional independence (CI) tests that degrade in high dimensions [cite: 24, 25], the optimal recommendation for modern continuous pipelines is the **NOTEARS framework** [cite: 6, 7].

**Primary Citation:** Xu, Z. (2024). *Causal discovery from temporal data: an overview and new perspectives*. ACM Computing Surveys [cite: 6]. (Also supplemented by Niu et al. (2024) [cite: 7] and Zheng et al.'s foundational continuous optimization research [cite: 24]).

The NOTEARS algorithm represents a paradigm shift. It recasts the notoriously difficult combinatorial problem of DAG search (which scales super-exponentially) into a purely continuous optimization problem. It does this by enforcing an acyclicity constraint through the matrix exponential trace function [cite: 7, 26]:
\[ h(W) = \text{tr}(e^{W \circ W}) - d = 0 \]
where $W$ is the weighted adjacency matrix, $\circ$ is the Hadamard product, and $d$ is the number of nodes [cite: 26].

### 3.3. Adapting NOTEARS to Math-Object Catalogs
Mathematical catalogs are discrete and non-stochastic, meaning traditional Gaussian noise assumptions in NOTEARS fail. To adapt NOTEARS to a catalog of Mossinghoff polynomials or Knot topologies:
1.  **Latent Continuous Embedding:** The discrete mathematical properties (e.g., crossing numbers, Betti numbers, Mahler measures) must first be embedded into a continuous latent space using a Geometric Transformer or continuous representation layer [cite: 27].
2.  **Continuous DAG Optimization:** The NOTEARS augmented Lagrangian optimization is run on these continuous embeddings [cite: 7, 28]. The fitness function $||X - XW||_F^2$ measures how well mathematical invariants can be linearly/non-linearly reconstructed from their topological parents, balanced by a sparsity penalty $\lambda_1 ||W||_1$ [cite: 26].
3.  **Thresholding to Markov Equivalence:** The resulting continuous matrix $W$ is thresholded to yield a Completed Partially Directed Acyclic Graph (CPDAG) [cite: 19, 25]. 
4.  **Confounder Selection:** G05 then traverses this CPDAG. Instead of `argmax|value|`, the system selects nodes that satisfy the **backdoor criterion**: nodes that have directed paths to *both* the treatment property and the outcome property, strictly excluding descendants (colliders) [cite: 20, 29].

---

## 4. Stratification vs. Randomization vs. PSM (Task 3)

In causal inference, controlling for a confound involves adjusting the data distribution to isolate the isolated effect of the treatment. The statistical guarantees of Stratification, Randomization, and Propensity Score Matching (PSM) differ wildly when applied to pure mathematics, particularly in the context of **Lehmer's Conjecture** and **Mossinghoff polynomials**.

### 4.1. The Mossinghoff Context: Lehmer's Conjecture and Salem Numbers
Lehmer's conjecture postulates that there is an absolute constant $\epsilon > 0$ such that for every non-cyclotomic algebraic integer $\alpha$, the Mahler measure $M(\alpha) \geq 1 + \epsilon$ [cite: 30, 31]. The current known minimum is Lehmer's polynomial (degree 10), which has a Mahler measure of $\approx 1.17628$. 

When algorithmically searching for polynomials with low Mahler measures (Lehmer survival), a notorious topological feature is the **Salem-class** polynomial [cite: 32]. Salem numbers naturally yield exceptionally low Mahler measures. If a machine learning claim states "Property X causes survival under Lehmer's threshold," we must control for whether the polynomial is a Salem number.

### 4.2. Randomization
*   **Definition:** Intervening directly on the causal graph by flipping coins to assign the treatment variable, severing all incoming arrows to the treatment node [cite: 33].
*   **Mathematical Context:** In observational mathematical catalogs, physical randomization is impossible. You cannot randomly force a polynomial to be Salem-class; its class is deterministically entangled with its irreducible coefficients.
*   **Result:** Randomly *sampling* the catalog does nothing to break the structural confounding. Randomization is effectively useless for catching the Salem-class confound on Lehmer survival because it preserves the endogenous topological distribution of the catalog.

### 4.3. Stratification
*   **Definition:** Partitioning the dataset into mutually exclusive subsets (strata) based on the exact value of the confounding variable, and computing the causal effect within each stratum separately.
*   **Mathematical Context:** Stratification operates on exact logical truths. We split the Mossinghoff catalog into two hard strata: `is_salem = True` and `is_salem = False`.
*   **Result:** **Stratification is the method that correctly catches a Salem-class confound.** By calculating the survival rate of "Property X" entirely within the non-Salem stratum, we can observe if the apparent signal completely collapses. If Property X only correlates with Lehmer survival because it was a byproduct of being a Salem number, the effect size within the non-Salem stratum will drop to zero. Stratification provides deterministic, exact blocking of the backdoor path.

### 4.4. Propensity Score Matching (PSM)
*   **Definition:** Modeling the probability of receiving the "treatment" (or being in a specific class) given a set of covariates, and matching objects with similar probabilities.
*   **Mathematical Context:** PSM is a stochastic approximation tool designed for noisy, high-dimensional human data. When applied to exact mathematical catalogs, it is highly sensitive to model misspecification and the inclusion of inappropriate variables.
*   **Result:** **PSM is the method most likely to falsely identify Salem-class as the cause.** If the logistic regression generating the propensity scores inadvertently includes downstream variables (e.g., the trace of the polynomial, or the location of specific complex roots), it conditions on a **collider**. As established in recent literature on collider bias and suppression [cite: 20, 21], conditioning on a collider opens a spurious non-causal path. The PSM algorithm would force matches between fundamentally distinct topological structures, hallucinating a statistical dependency and falsely confirming a spurious causal signal.

### Summary Table
| Operation | Guarantee | Mossinghoff / Lehmer Outcome |
| :--- | :--- | :--- |
| **Randomization** | Golden standard (if intervention is possible) | Inapplicable. Fails to break deterministic structural dependencies. |
| **Stratification** | Exact structural blocking of specified nodes | **Catches the confound.** Forces exact comparison, collapsing spurious signals. |
| **PSM** | Approximate distributional balancing | **Falsely identifies causality.** Susceptible to collider bias and topological mismatch. |

---

## 5. Architectural Specification for G05 v2 Loader (Task 4)

To resolve the fatal flaws of the v1 MVP, the G05 CONFOUND-SWAP plugin must be upgraded to a sophisticated, data-driven causal pipeline. The v2 loader abandons `argmax|value|` and implements an automated structural causal modeling architecture.

### 5.1. Module A: Data-Driven Confounder Identification
Instead of sorting by magnitude, this module constructs a topological representation of the mathematical catalog.
*   **Input:** The PROMOTED claim payload, including the target parameter $T$, the outcome $Y$ (e.g., Lehmer survival), and the covariate matrix $X$.
*   **Algorithm:** 
    1. Pass $X$ through the `NOTEARS-MLP` continuous optimizer [cite: 34] to extract the Directed Acyclic Graph (DAG) of mathematical properties.
    2. Analyze the DAG using the backdoor criterion (Pearl's do-calculus) [cite: 29].
    3. Identify the minimal adjustment set $Z \subset X$ consisting of common ancestors of $T$ and $Y$.
*   **Output:** The strictly identified candidate confounder set $Z_{confound}$.

### 5.2. Module B: Stratified Re-test Engine
Once $Z_{confound}$ is identified, the system conducts a rigorous test of the original claim.
*   **Algorithm:**
    1. Reject PSM due to collider risks.
    2. Execute categorical **Stratification**. The catalog is partitioned into disjoint sub-manifolds based on the discrete states of $Z_{confound}$ (e.g., $Z=0$ and $Z=1$).
    3. Within each stratum $k$, measure the effect size (e.g., survival fraction $S_k$) of the target parameter $T$ on the outcome $Y$.

### 5.3. Module C: Per-Stratum Survival Fractions and Meta-Verdict
The engine aggregates the stratified results to generate a deterministic meta-verdict.
*   **Data Structure:** A vector of tuples `[(stratum_1, survival_fraction_1), ..., (stratum_N, survival_fraction_N)]`.
*   **Verdict Logic:**
    *   If the survival fraction collapses to zero across all strata: The claim is dead.
    *   If the survival fraction is reduced but non-zero: The original claim was partially true but inflated by the confounder.
    *   If the required adjustment set $Z$ contains the original candidate but requires additional variables to block the path: The initial assumption was incomplete.

### 5.4. Kill Pattern Definitions (v2)
*   `complete_signal_collapse`: (Legacy, Retained). The parent claim was a total shadow of the confounder. Survival fractions in all strata equal 0.
*   `confound_identified_as_partial`: (New). The apparent signal is significantly reduced upon stratification, but a residual statistically significant effect remains. The claim is downgraded but not killed.
*   `confounder_set_not_minimal`: (New). The NOTEARS DAG analysis reveals that the identified confounder $X$ is actually a downstream proxy or part of an entangled set, and a larger topological adjustment set is mathematically required to satisfy the backdoor criterion.

---

## 6. The Inverse-Confound Problem: Suppressor Variables (Task 5)

G05 currently operates entirely on the premise of false positives: finding a variable $X$ that makes an apparent signal disappear. However, causal inference dictates a strict dual to this problem—the phenomenon of **false negatives**, where a true causal relationship is completely hidden until a specific variable is controlled for. 

### 6.1. Defining the Suppressor
A **Suppressor Variable** $Z$ is defined as a variable that increases the predictive validity of another variable by its inclusion in a regression or causal model [cite: 22, 35]. In causal DAG terms, suppression often occurs due to two competing pathways (one positive, one negative) that perfectly cancel each other out, or through complex collider bias structures [cite: 20]. 

If $X \rightarrow Y$ has an effect of $+5$, but $X \rightarrow Z \rightarrow Y$ has an effect of $-5$, the observed marginal correlation between $X$ and $Y$ will be $0$. The apparent *absence* of a signal is an illusion. When we condition on (stratify by) $Z$, the negative pathway is blocked, and the true signal of $+5$ violently reappears. 

### 6.2. Methodology: cc-Shapley Values and Collider Bias
Recent 2024-2026 literature explicitly distinguishes suppressor effects from standard confounding. Haufe et al. (2024) and Wilming et al. (2022, 2026) define suppression heavily through the lens of collider bias [cite: 21]. 

**Methodology:** To identify suppressors, we cannot use standard correlation matrices, because the suppressor often has *near-zero correlation* with the outcome variable [cite: 36]. Instead, the modern approach utilizes **causally-constrained Shapley values (cc-Shapley)** [cite: 21]. By modifying traditional Shapley Additive Explanations (SHAP) with the underlying NOTEARS causal graph, cc-Shapley algorithms can detect when the marginal contribution of a variable is artificially depressed by a mediating or colliding topological feature. Another modern approach is **Convergent Cross Mapping (CCM)**, an empirical dynamic modeling tool used to uncover hidden causal feedback loops that suppress linear correlation metrics [cite: 37].

### 6.3. Plugin Slot Proposal: G05b REVEAL-SUPPRESSOR
To handle the dual problem, we propose a sister plugin to G05.
*   **Slot Name:** `G05b REVEAL-SUPPRESSOR`
*   **Trigger:** Activated when a highly-theorized mathematical claim results in a null finding (zero correlation).
*   **Mechanism:** Runs cc-Shapley value analysis over the NOTEARS DAG to identify nodes that exhibit suppression geometry (competing parallel paths). Conditions on the candidate suppressor and re-evaluates the signal.
*   **Emission:** "The apparent absence of signal is a topological illusion; controlling for the suppressor reveals a statistically robust causal mechanism."
*   **Expected Kill_Pattern:** `hidden_signal_revealed` (the parent's null-hypothesis claim is killed; the mathematical relationship is validated).

---

## 7. The Contrarian Objection: Intervening on the Integer 7 (Task 6)

We must now address a profound metaphysical and mathematical objection to the very premise of this system.

### 7.1. The Category-Theoretic Illusion of the *do*-Operator
The foundational operator of Judea Pearl's causal inference is the $do(X=x)$ operator, which represents a physical or simulated intervention that forcibly sets a variable to a specific state, severing it from its historical causes [cite: 29]. 

**The Objection:** Causal inference on mathematical objects is category-theoretically ill-defined. You cannot perform an intervention on a Platonic mathematical object. The integer 7 is fundamentally, unalterably prime. You cannot define $do(\text{is\_prime}(7) = \text{False})$. Doing so destroys the object; it ceases to be 7. Therefore, without the ability to intervene, "causality" in pure mathematics is an incoherent illusion. The relationships are purely logical tautologies, not causal mechanisms.

### 7.2. Engaging the Objection: Topos Causal Models (TCM)
This objection is historically serious but has been comprehensively solved by recent advances in Categorical Machine Learning. In 2025, Sridhar Mahadevan published groundbreaking work on **Topos Causal Models (TCM)**, which generalize Structural Causal Models into Grothendieck toposes [cite: 8, 9, 38].

Mahadevan argues that the symmetric monoidal categories and simplicial sets underlying causal models do not require physical, temporal interventions [cite: 8, 39]. In a topos category, a mathematical object is defined purely by its morphisms (via the Yoneda Lemma) [cite: 8].

### 7.3. Reframing Interventions as Functorial Pullbacks
In Topos Causal Models, an "intervention" does not mean reaching into the integer 7 and changing its properties. Because the category of TCMs is complete and cocomplete, an intervention is defined using a **subobject classifier** $\Omega$ [cite: 9, 38]. 

When we evaluate $do(\text{is\_salem} = \text{False})$ on a catalog of polynomials, we are not mutating an individual polynomial. Instead, we are using the subobject classifier to induce a **pullback**—a functor that maps the entire structural causal model to a valid sub-model (a new category) where the constraint holds [cite: 8, 9]. The intervention is an operation on the *universe of the catalog*, not on the intrinsic nature of the individual mathematical objects. 

Furthermore, TCMs admit an internal Mitchell-Bénabou language with Kripke-Joyal intuitionistic semantics [cite: 9]. This means we can logically reason about counterfactuals ("What if this polynomial trace were different?") by traversing the partially ordered lattice of subobjects in the topos, perfectly preserving mathematical rigor without violating the immutable nature of the constants themselves [cite: 40].

### 7.4. Why G05 Survives
The G05 architecture survives this contrarian critique because its v2 design (specifically Stratification) perfectly mirrors the Topos Causal Model definition of an intervention. By avoiding PSM (which attempts to morph probabilities) and instead using Stratification (which creates discrete subobject categories via subobject classifiers), G05 is mathematically isomorphic to Mahadevan's functorial pullbacks. 

G05 does not claim to alter the integer 7; it claims to compute the structural mapping of the sub-universe where 7 does not exist. Thus, causal inference on mathematical objects is not an ontological error—it is a sophisticated exercise in categorical topology, and the G05 CONFOUND-SWAP mechanism is entirely mathematically sound.

**Sources:**
1. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEexL4fayiJGh-6-3LGIso2YXmWBclb5NYiPwuauNbsWMK_HqdljZAr7ay6SnLfl8NIs1WooyevyjEFjkkPmentNr3vU62tMQN_RXkKXnZ0KjYeJxU6rA==)
2. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGyRnClPgBSfgHTIYX4XFekzGwc5BWy92g_ARxrkmDmIjo4L-J0v6pgwXdnmZjhD_DNSyXfl1XtlVMuH0ZksN6fPMk5HRU0AzwjuelH1aKXaQCDc5hC7zrk6LoJtUGOwlWAFKHkGy14KHa0qep7YuvRrPxhv6cj7yvm5uUFfXurSFBVXuED3V7ypoIyikWF2b0DX-lOio7_qQldUfkQJTtC9XZb3R5lQbbmFo7GSkxbuoK3a13H)
3. [maa.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBi5vVCYGQ7xS0tssKr0Z0YjN1xN0rOOQopTEZnTZOw0TiRB1O9ozEae5B5IKrsTR7z3fDqyq0_uUAtCMpJgN4YywtZCrvwX1DAmx5Jwx36-npiAUNF3pv_pMoWrZ_9aRKjf0ZdAqzo6rXso9y-u0uEvwYebnggS5lfjmltuHZ)
4. [aimath.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGcy5Q978jctfz-QwrVtJxv06I72lu1R4VXILx8d2ZMbUTVLWdxjIJuyNL2cDX5yMLoX_gUJPKcOr0Vi2KCeQspIT_ZphQpLCVWngIUVpm4TqL89sovqZc=)
5. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAZfydZuPtrFE72uA_yFclfQj4CeRPSM5DRtGVPqOHbLqb01ZfCw_tA5yWe_n5rHBwIKdEVW3dvodAm-favHmftieVAWGeYa12lfcn7wNuueiEadgIPSFX07z1CE91NPX1fJogIf9AIXeR1ZtpV4ou3MndZhibiQBZR7c=)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuKM-Qy8VjE8-HiBHx2000tCBt5QhSlXdWSnsy_DLH8OdURBHR2RDRs0kppf3bQWH_ore8A6olYfQYQt9cO6YRfbdbtvl8QOSTTJIWt1tdI1yMVafmHG8agg==)
7. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX6oDNf1yNUzfzTSRujBzvE7D_njPMOnpieIHHbAGgAkSsmUFjqp4Sj9ZLDYwhu10xJE5bfT5d0YpC_7cq2OqJ-3QB2AgbiKUyQblC4_7hJyNTdQ3Y7lOKlAgP-QTM6uGaxtoeFiHpsjzHbQ==)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNCA74ssNqh1rWgvQcc3Y4oopElH1VUzlU6k-pD-iDgLdAHdd03MExeerDtmOjJuXET1-yW1sjnih3vt0joru3DBK3v-WFnf51TjgTicUo0p-RnX0EEQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEckAYHjVFw70dqpVOV-QAWjKdnh3UDw_rLdxNAwDLEmktJhtOct-3o7zYRtsn6HXGJgZCJ_zVz61NQO0Q3Vc8royFjoE6RHF0OMH1iBVt5TUQ1CoK1Ew==)
10. [sciencedaily.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMmlpkh_P7mmRR-uDFU77aeAJB1l43Wh-NSeKEeCYoW9j1SpPp3UR_LNr2wOnGz2O-80nTJI7uZSyBAYYJa4F98D2zpJ-AybEGui15xJgpJ6tPMiIB7WJJ9xVld7QGM4yn_skyGF9ONjrWhELiY1sOB0WnVQ==)
11. [repec.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3ERhFw2Ni741RhPy27wZTKVLDgtyjQH1HYDzhSp9LbIiFC-84dxRYRwiVAFu1dUSv2KWDUogg86QyJBi9kIYUU6NAMv5-_Q_-I1-OxdsmQ5qn7Dw7ef-jqr17tn8Y2OgnYxtIYow1ehhdlCQrzuTtoRC_nFDX1SF_43XzMFQQXMFBhDnA)
12. [mit.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6U7rV2OyIOloenEOkxIG6Ig9ZaHZFzIpvdlDF4U18WatG2M9EEILGfkrM779uEsOdmd6zISt0Of11W29WeksgicFbWNOzuHaSFc9tIUow1TYrE_ttKnyglgjz5HVgiUo5JRyULiFhZuFDWRlgs2OhOAbMBlwPomfPsIY=)
13. [tandfonline.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-1WyLOq45fjEfHjt_GprHMukXBByN3fogNMgGrOhL8pqhuKrozGRqAUEHXccd63vRAfu27RJQoNBkQCWppcHIGCldLZmK29y-mNBF86CHmnoJE4L7SoZCHOXvVQclVzlXZNdSx7hbmEdQYCZnXbKRSk66dm9Wp7A=)
14. [eurocim.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6NTrQ1LYMn7ksYlOHtZ9968D2LAN9xEDrZMt935qCXJILQ4DTa-QOi3nJMPj-EMWn-sSTIHcxCW-sKHIhcaEQ7pq4WfN38uU49x0218YixxpvP7V2OR6hWJtG4GXfjOBxmDhOyKzeUrWytqR0uE2uSQ==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFygFkUq2A1ciQMPHTPF1-fSUPqenZGWbHRBAXBYU4fsH1sm9ikxqo24xOSMwLYP1z4CA0rwwvg6E-Dg1axkvLtZeb43NjwfH_lktsPZS1i71aQBXNJ6w==)
16. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrof9Z7d7s7b1Af4sC8zrCGz8bDJATCil4ViDXREvy74CkCDxoRyjkPSAQpg9GrdbRD5P76K9TRV38KlAasHVJGOZJ9Aqt2CoVQksRAytuoCOHQR8yDFP9oS7NiHVntdnHK1cikobrCl83dljG7blEPagG6DE_Q1E3GYFBghh1P3ZMVw==)
17. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5sEK7YP9i9yYwva3tTgM3gh_cVmD5l00dk0p_KPWKpypkkU2TH9w4TTAAl2j8IPWYWExZKWpheUzLRpLYhRNcgwED4uAHMLeaKUhgMG2folW-zQWE4itXEWU60ClTHKTOXfkgU7AR4ljF7bQiQjUK3bYGC242bNnyGmPTjpiKZp4bt5PedHybNmK-Gg492MCeMTbePyaORBJ7ZieTewllHQpdMYvTXOf5mjiErbofFgCM0s8FAZe4eubA_8IhYLc=)
18. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFj_ANHYAtQ0BAb47Td7CYTQOpSOG2Z0gYgbgmu8fFPeXsLo-9Pc40gQvgMHyRbV-X48aaeZ6Trm-ThiNbNzkBn58wbDjz1iVBe-SSWYQEuVOPR6_Q5JTPc3TV4TAUIf_8hLERWwoPcuQ==)
19. [pywhy.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeBXiwqTM1wIorZtztYUUHJA6bJ3Trs__mCO9Xh7frIoY2SwifHfiOdaUzpIo0xN_GDTacEPPPcIvF_ReQILhUgTYWB541Nxfb_-A9j8vIszMQUnICsEASVObA1tRdF1aDi10GY7Bv_oxAg-gVKFu7N4cpZ95poD3uZwYfAW5a3wcGKNuTEAnsMw==)
20. [elifesciences.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfUS73wy90GGdPOrBt5ENci2gNiIagnFVOWJdrpojPwSq2Gf7LeSdSsYrm4e08ptFKi7mlNl6J_ULjZK8_k3o_uDUeU8ODOy4ckdtQJLmxCzylliK6rxSrEZuqlOCi)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHml5VDpfAQaID26TXpI9DkacKzzlLp8ebFS3yiGPaQmn323oeovKTrYSQjhBpXsf66WZhnNODpUbrhQIeANMThmbzmWa0JKNoM261K0pQcxxo8ZVRTLZXJDA==)
22. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyPUIyGvmiFz3CNFhDh13KVF0hWR7aqw3EZGbiTMQK3sjNeffFpW759jCqCSpzHrNmLTZSxHbubHdMYXukCuro9GzmCeGMZHKui8rBrUfck949vhNQo2h8t5VVnj9HNOT9MG1c31l8A00a)
23. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET2761PJalN8R4XbIhhgfshVUhA_7PsnjhhHZyPUc5TfHaF6GlLB6NYiTQcfIOkUfOt3oAjD0rMKC0esqlUDAz5e5P_e8kXA8WF5PmDJz59b4m1isvYQjge_M1O7sLBo_GXrsrk0eNUg==)
24. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-yU_J8VkMZHHShAyoV4RKLlRIq2n19Fk63cFsq-PDYe0PjWy9Hy8hdNsuuxTjzfCRvP6JTQ8AoVgh1cSNNooS87CvTX_l-htEyzIj7WCKsCBLU4ivHPWqOgBPtEy17gEbhxJ--eJ-Wa7BcWinQySwwG1Gd2r65aW2hLDadCKuB-sH)
25. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXbI42IRu7VUaBQTeFTE6qsrooNVti-w48SkZFNG25pYbtVkMRYPYibwhR0PB7eN8JoZnwaGBmTDILLSaAaIS-4ekD9_9d_cxKEUB9f95LRvOw7j40pJRX5m4pXOqNzL9qcNqsy3OgWZI7HUo8DPpdte-kLzHcqlhGzA==)
26. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdnuzi15FnEXihkYn4wXy1wRWB4eciZawk-Fea_f_4ayJ9hP6yJye7HEEs7NBkEOTe2Tu3Q8AOzG_rXQpD8_KyAhdxSbBOCB_SnF8Y8CP3f0JKst2DVYseCI5U9eL9MIrYxE0rXsLiZq1MLzGNgV96MA7b9A7_IFofWdKz1g==)
27. [chatpaper.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgc8mITPEX4xCPtMjHU5k6uaIaiN-L2UlLf6UvOWNUZWipPnW_fsUr9YvYpfNhDbBHsNYegJUvtwf8FMvQWzBFTFUZsQKDR7RtfpcCqsOSlikTSGp_dPTtxV6aVKrCUycs2w==)
28. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-dgYdq_TBd11ut90Lr18vOOEqDLsEIzGmLXqm_XJ_6esDs665yWy0N8kpF62IzqiluPmXgRolxiOUN3VY9knNRykZD6kot5oF6VHqqx0YAg2tm_evzAjr9rlKYVI8vaGTsnLJAgfM6APHs34XbkbMRkziAuYqbWrH69xpM98KHJDTmeo8Jv7ToyswEkXzM6yTPia0)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5ENDyI50BO_4LaGkXLhbhZhsucu5j9OyNvsMrzc_54T_QjSRcx3TRo8AVO9oXoHSXXNaBCKzwFMc5kwqD9Q8NzAenFVZsIIyC1LDiQaxJlG299Xd0d0F9vA==)
30. [uni-regensburg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEP4zYu0d6n9w_5vYrD6HYRaOBtHyO39W98eaLUDh0Etl44dfQyJQsVIqRZSHwbBhTQgF54Qvg7jpX1gnfRkqKmEv3H6tBVpQ88CNaYumEWAjAO0aC8GQe5yTgeRplt7qv-mFJVBn9gkuL17-Ls1i6jRTejCLNiELI5me20)
31. [math.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGgUds3YMYCF0IC-CdSxCbl6hb0Q7qMgJEdAwdgNzmmGLJBH1zUy4bpomj5ALzxx49oFma6ZSIgigHj_9GakJ_J0z2fq1fyeGHzv6MoL0T_e_6FU5DaNy-tLvVW37tRW9y6bHrVCycM1wS1GUvMQ-C2RI-9qij6ZOtKZo6ZYEoWplAqJGIz6lGIkERWJDc94VRsa2eWAgJqUTTt-ELci6pF3plVBgiBTY=)
32. [dntb.gov.ua](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGL_L0IRZY-ypsqPhJ9boqXoktT6rhgB1HJtJaa0el-o0tZ-jjJqPHOat31KKt5uMCc3Z3f_VVwJBrrhtHaUbEWCuG78Xzh0ub0OrTPTQAzPCIlm8Yydd5ClOMYy8TA2BNO)
33. [projecteuclid.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnxdxWTjTu3_cN9WHTJJweElAtyVYvuH0U5btZ0bGEFeAE2Ng4oqU4pizhfxQ5TZ8-nLX7JjH3U2d7ctqS8aCIhZFJM5nzaBWaBGGuLtMgsiSBVYYUSceSPZe45ZtXy_Mpb_Th5Vph14Q6dIEbccBJrGdCQZRGbQWo4iMwxU6YHo2IDlzlEvkQQGIOHOHo0rHUhGSkME2eNJKLl-RbSBs8K-89fA8iOKLEbHBfVVjyOtyMWALg8wDf8kstK5GdkNA1Se-2YLec-q74hOu4-L3BzuisjY-yLkRhoBXzbgkOXXy-Myzqbgi-Lg==)
34. [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoBavvHtfO-oLOXlhJ81nK1SLyEuamCfb64JNJC5kGANRi7LV3d7dLVq4DSJYDdwuBjJ3IY3CZnKOxDYNjATiN0I9L3gNhRZmQhENqFCqKuTIasGkBddi9vk6ym6Q71VNhOJUwHbdF8EGexqEILaIEydF_AtdXSzoYmY4Azr8qoaVjWiUpDfFDMcnHHWzw2w4SfY6RwdeNXTfv_Fc14U44csSfRBg1)
35. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTZNmfm3oocgfH0UkSA-XQBoGmn1w-Tzfm3ykEYv7kC5IeD2lYjT7cEDex_yvc2BdvbUl8aXhAwgKVDcFPjlvn4niOMwtR29-I_jj0hR9RNzScVFPha_sHwDbD39S-vP5w8GW46SrkzlDaZiAcyPs60KtiR2-a8rSLBUxeI2Js)
36. [centerstat.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE3umivSlilTIE5UTKzWg1r5727xSFMLcGdnrfH6uDRs3258deG_Rcr6y-88SpqrwYt8TCjlnAZh71IpZ5Q1Q4dnOrq4OiPr1oXyfl1iszW2giRfoq9MveK78-nMVVz1n0wfQ==)
37. [frontiersin.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFipaDrDAPFIGNF6QXAE60i3VF40aVhHwGnwGLAMPGi3n7xT-kbfQ6U7QK49IaeW8QTKDoKVOiuSuoqFRxBep4JSqhtNoGul4gVU1KL02WpOQ5md5aysh48AUF9gFXbv3y1dVO-jifVuwDsttJKZVhrzhYylqDRes6nIlHeyRbNAugFrjn077yuP5aCVQ==)
38. [umass.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFkkf7B_QSXBuKzcIxDefVm9L92BUFbrCdrd33yxDxh-A2Dmc1lIvyR8d0IIZH71lja1kLektz9GSHn_2tlQt2brO0Vb6ZBHUe0nJMaxVz-5FQZIb2yYD81P-5rN4HC6CAv0QoeHNNbR_iV)
39. [umass.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMJ8JMP6eX33JBQNBi_ZN1DXTzePh1j1bUns4bJucKPy61WLhRFZiUInQLb_O9S05QeeBUn4UgfPZJXBqfproMzGEBl2fxTmFhRdhXn6OqaNcVPhyvvvNBdOh3PymfpjD2NAvGYze7GnMq3Q==)
40. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcBxLJ05L9GRG5CNL3rkXwGcp44Zn7aTEYs6TTc6TcRT7V_1Z8pvH6J4yfj565yLK9N9XTqjkBL2astGMhHMRvQdohu_1iafAg0HrfE7i4oq4vvA_jVO_RGT3-H_Xetj4=)


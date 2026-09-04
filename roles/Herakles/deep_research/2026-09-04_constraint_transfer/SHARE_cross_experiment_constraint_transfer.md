> ## Provenance and caveats — read before citing
>
> This document is **machine-generated literature research**. It was produced in
> a single automated deep-research query on **2026-09-04**, run by Project
> Prometheus, and it has **not** been fact-checked against the primary sources
> it names.
>
> Two specific cautions for any reader:
>
> 1. **The citations are not verified.** The numbered `[cite: N]` markers resolve
>    to the source list at the end. Several of those resolve to blogs,
>    encyclopedia entries and aggregator pages rather than to the primary papers
>    named in the text. Treat every attribution as a lead to check, not as an
>    established reference.
> 2. **The report's own evidence standard is the honest part.** It states plainly
>    that the supporting evidence is strong in deterministic software and
>    hardware verification, and **conceptual only** in experimental science. That
>    distinction is load-bearing and should not be smoothed over in summary.
>
> The exact question this answers, verbatim, is public here:
> https://github.com/jcraig949jfi/Prometheus/blob/main/roles/Herakles/deep_research/2026-09-04_constraint_transfer/deck.md
>
> The full record, including the raw interaction, is here:
> https://github.com/jcraig949jfi/Prometheus/tree/main/roles/Herakles/deep_research/2026-09-04_constraint_transfer

---

# Cross-Experiment Constraint Transfer: A Deep Literature Investigation for Project Prometheus

**Key Points:**
* **Conceptual Convergence:** The problem of "cross-experiment constraint transfer" is not named identically in existing literature, but its core mechanics are highly developed across fragmented disciplines. Formal methods rely on **Counterexample-Guided Abstraction Refinement (CEGAR)** [cite: 1, 2]; software engineering utilizes **Metamorphic Testing** and **Property-Based Testing** [cite: 3, 4]; causal inference focuses on **Positivity and Empirical Overlap Diagnostics** [cite: 5, 6]; and operations management studies **Organizational Memory** and **Stop-the-Line (Andon)** systems [cite: 7, 8].
* **Operationalizing Failure:** Transforming a specific experimental failure into a generalized constraint is mathematically analogous to extracting a *metamorphic relation* or an *invariant* from a spurious counterexample [cite: 9, 10]. This is an executable abstraction that catches a class of bugs rather than a single instance.
* **Preflight Validation:** Evaluating experimental designs prior to execution is actively researched under terms like **Statistical Linting**, **Causal Type Systems**, and **Automated Design Validation** [cite: 11, 12, 13]. These tools shift error detection from post hoc correction to a priori compilation failure.
* **State of Evidence:** Deployed engineering practices in software and hardware verification demonstrate that executable constraints strictly reduce defect recurrence [cite: 9, 10, 14]. However, the application of static type checking and automated adversarial compilation to *scientific experimental designs* is largely conceptual or in early prototype phases (e.g., AI scientists and automated research assistants) [cite: 15, 16]. 

The hypothesis driving Project Prometheus—that scientific research systems fail to learn because they do not operationalize prior structural lessons into executable future constraints—identifies a profound vulnerability in multi-agent research environments. When "yesterday's correction does not become tomorrow's impossibility," the system relies on fragile human memory or coarse institutional documentation rather than robust engineering guardrails. 

This report synthesizes evidence from causal inference, formal methods, software engineering, and systems safety to formulate an attack plan for KNOWLEDGE TRANSFER ACROSS EXPERIMENTS. The synthesis confirms that the machinery required to encode a local failure into a structural abstraction, generalize it into a constraint, and apply it as an executable preflight check already exists in adjacent fields. The immediate technical challenge is not inventing new mathematics, but aligning these disparate frameworks into a unified "compiler" for scientific experiments.

***

## PART I - EXECUTIVE FINDING

**Is cross-experiment constraint transfer a coherent and important problem recognised elsewhere under other names?**

Yes. The failure to generalize local errors into structural constraints is universally recognized as the primary bottleneck to systemic reliability. However, it is never called "cross-experiment constraint transfer." Instead, it is solved in isolated domains under specific nomenclatures:
1. **Formal Verification:** The exact pipeline of "Local Failure -> Abstraction -> Constraint -> Check" is formally known as **Counterexample-Guided Abstraction Refinement (CEGAR)** [cite: 2, 10]. When a system model generates a spurious counterexample, the failure is used to systematically refine the abstraction (adding constraints) to ensure that specific class of error can never be reached again [cite: 1].
2. **Software Engineering (Testing):** The problem of lacking an oracle (knowing the exact expected outcome) is solved via **Metamorphic Testing** (Chen, 1998) [cite: 9, 17]. A localized bug is abstracted into a "metamorphic relation"—a universal invariant that must hold across transformed inputs [cite: 14]. 
3. **Causal Inference:** The structural failure of "Estimand-Existence" is meticulously studied as **Positivity Violations** and **Lack of Empirical Overlap** [cite: 18, 19]. The failure to learn from unobserved counterfactuals has led to the development of overlap weights and structural causal models that diagnose missing support before causal estimation [cite: 20, 21].
4. **Safety & Operations:** The failure of humans to retain error corrections is codified as the **Normalization of Deviance** and the degradation of **Organizational Memory** [cite: 7, 8]. The executable countermeasure is the **Andon Cord (Stop-the-line)**, which removes the human decision to proceed when an invariant is broken [cite: 22, 23].

**What are the closest existing fields or systems?**

The closest existing systems actively building pipelines analogous to Prometheus are:
* **Automated Scientific Assistants / AI Scientists:** Systems like AutoRA, Co-Scientist, and OpenClaw automate hypothesis generation, design, and execution [cite: 16, 24]. Some utilize *meta-verification* to retroactively evaluate reasoning [cite: 15].
* **Statistical Linters and Design Validators:** Tools like HubMeta employ statistical linting to detect degenerate data topologies (e.g., taxonomy crises, zero-variance constructs) [cite: 12]. In clinical research, platforms like BioClinica enforce automated design validation rules before a trial is launched [cite: 13, 25].
* **Causal Type Systems:** Emerging theoretical frameworks (e.g., NabiOS, TRACE) propose type systems where causal variables and estimands are typed, and connecting a "social norm" input to a "physical force" output fails to compile [cite: 11, 26].

**Is there evidence that converting past failures into executable future constraints reduces recurrence?**

**Yes, emphatically, in deterministic software/hardware systems.** The adoption of CEGAR in model checking, and property-based/metamorphic testing in critical infrastructure (e.g., CockroachDB, Google GraphicsFuzz) has empirically reduced escaped defect rates to near zero for specific failure classes [cite: 9, 14, 27]. 
**In experimental science, the evidence is conceptual.** Systems are currently hindered by the "oracle problem" (scientific truth is unknown). However, by shifting the constraint from *outcome correctness* to *design structural integrity* (e.g., enforcing positivity, residual variance, temporal precedence), the exact same engineering pipelines can be adapted to drastically reduce the recurrence of degenerate experiments [cite: 28, 29].

***

## PART II - CONCEPT MAP

To operationalize cross-experiment constraint transfer, we must map the specific failure patterns and desired mechanisms of Project Prometheus to established literature terminologies.

| Prometheus Concept | Nearest Literature Term | Key Difference / Context | Primary Sources |
| :--- | :--- | :--- | :--- |
| **Cross-Experiment Constraint Transfer** | **Counterexample-Guided Abstraction Refinement (CEGAR)** | CEGAR applies to state spaces and transition systems; Prometheus applies it to statistical and causal designs. | Clarke et al. (2000) [cite: 2]; Zhang et al. (2017) [cite: 1] |
| **Local Failure / Defect** | **Spurious Counterexample** | In CEGAR, a spurious counterexample is a logically impossible path. In Prometheus, it is a scientifically degenerate design. | Clarke et al. (2000) [cite: 10, 30] |
| **Executable Constraint** | **Metamorphic Relation / Invariant** | An executable constraint defines structural limits (e.g., $Var(X|Z) > 0$). Metamorphic relations define relational limits (e.g., $f(x) \le f(x+c)$). | Chen (1998) [cite: 3, 9]; Lemieux (2015) [cite: 31] |
| **Estimand-Existence Failure** | **Positivity Violation / Lack of Empirical Overlap** | Causal inference explicitly models when sub-populations lack counterfactuals, rendering estimands (ATE, ATT) unidentifiable. | Li et al. (2018) [cite: 19, 21]; Hernan & Robins [cite: 5] |
| **Incremental-Information Failure** | **Conditional Mutual Information (CMI) / Shapley Information Gain (SIG)** | SIG strictly quantifies the marginal utility of a new variable given existing baselines, resisting "internal coherence" fallacies. | Ding et al. (2025) [cite: 32, 33]; Zarchan [cite: 34] |
| **Identification / Temporal Failure** | **Granger Causality / Reverse Causation / Lagged Negative Control** | Mechanisms must defeat predictive precedence and bidirectional confounding. | Holland (1986) [cite: 35]; Casrai [cite: 36] |
| **Experiment Preflight Check** | **Statistical Linting / Automated Design Validation** | Static analysis over a design schema to ensure identifiability and support prior to data peeking. | Fast et al. (2014) [cite: 37, 38]; BioClinica [cite: 13, 39] |
| **Design Type System** | **Causal Type System / Abstract Interpretation** | Enforces that statistical estimators are algebraically and causally valid before execution. | Sewell & Vitek [cite: 40]; TRACE [cite: 26] |
| **Error Retention / Systemic Learning** | **Organizational Memory / Normalization of Deviance** | Human systems silently adapt to failures. Machine systems must encode them as immutable gates (Andon cord). | March & Simon [cite: 22]; Vaughan [cite: 7] |
| **Coverage / Novelty Failure** | **Retrieval-Route Independence / Search Saturation** | Defining a stopping condition for literature and design space exploration to ensure a claim of "absence" is falsifiable. | HubMeta [cite: 12] |

***

## PART III - THE BEST 15 SOURCES

Ranked by relevance for actually building the Prometheus constraint transfer system.

**1. Clarke, E. M., et al. (2000). "Counterexample-Guided Abstraction Refinement." *CAV*.** [cite: 2, 27]
* **Field:** Formal Verification.
* **Precise Contribution:** Formalizes the CEGAR loop: Generate abstraction -> verify -> if spurious counterexample found -> analyze counterexample -> refine abstraction -> repeat.
* **Why it matters here:** This is the exact blueprint for taking a localized experimental failure (a spurious design) and mechanically generating a generalized structural constraint.
* **What transfers:** The algorithmic structure of refining a hypothesis space based on explicit failures.
* **Empirical Result:** CEGAR reduced state-space explosion in model checking, making verification of complex systems computationally tractable [cite: 2].

**2. Chen, T.Y., et al. (1998). "Metamorphic testing: A new approach for generating next test cases."** [cite: 3, 9]
* **Field:** Software Engineering / AI Testing.
* **Precise Contribution:** Solves the "oracle problem" (when truth is unknown) by testing relational properties (metamorphic relations) across multiple executions rather than exact outputs.
* **Why it matters here:** Scientific experiments lack a ground-truth oracle. Metamorphic testing allows Prometheus to generate adversarial preflight tests (e.g., if we randomly permute the target, the incremental information must drop to zero).
* **Empirical Result:** Successfully caught critical bugs in previously "untestable" software like GCC, Weka, and autonomous drones [cite: 3, 41].

**3. Li, F., et al. (2018). "Propensity Score Weighting for Causal Inference with Clustered Data / Overlap Weights."** [cite: 19, 21]
* **Field:** Causal Inference.
* **Precise Contribution:** Identifies how structural and random positivity violations render conventional estimands (ATE, ATT) impossible, and proposes overlap weights to shift the target to the empirical overlap.
* **Why it matters here:** Directly solves the "Estimand-Existence Failure" (Prometheus Failure A). Provides the mathematical framework to detect empty conditioning sets and disjoint supports before an experiment is frozen.
* **Empirical Result:** Minimum variance bounds for causal estimators under lack of overlap [cite: 19].

**4. Ding, H., et al. (2025). "ProMed: Shapley Information Gain Guided Reinforcement Learning."** [cite: 33, 42]
* **Field:** Artificial Intelligence / Healthcare.
* **Precise Contribution:** Introduces Shapley Information Gain (SIG) to quantify the exact marginal utility of acquiring new information, adjusting for existing contextual baselines.
* **Why it matters here:** Addresses "Incremental-Information Failure" (Prometheus Failure B). Proves whether a sophisticated new construct actually contains novel information beyond cheap nuisance proxies.
* **Empirical Result:** Outperformed reactive models by 54.45% by correctly gating decisions on the expected incremental information of a new measurement [cite: 33, 42].

**5. Fast, E., et al. (2014). "Emergent, crowd-scale programming practice in the IDE (Codex)." *CHI*.** [cite: 38, 43]
* **Field:** Human-Computer Interaction / Code Analysis.
* **Precise Contribution:** Introduces **statistical linting**: identifying structural patterns that are internally valid but probabilistically likely to constitute a domain bug.
* **Why it matters here:** Provides the framework for an "Experiment Linter" (Attack Strategy A). It shifts error detection from human review to IDE-level static analysis.
* **What transfers:** The concept of compiling a knowledge base of prior failures into real-time editor warnings [cite: 37, 44].

**6. MacClaessen, K. & Hughes, J. (2000). "QuickCheck: a lightweight tool for random testing of Haskell programs."** (Referenced via Property-Based Testing literature) [cite: 4, 45]
* **Field:** Functional Programming.
* **Precise Contribution:** Established property-based testing (PBT), where properties (invariants) are declared and thousands of random inputs are generated to falsify the property, minimizing the failing case automatically.
* **Why it matters here:** PBT automatically shrinks failures to their minimal structural counterexample, exactly addressing "Question 10: Can prior failures automatically generate new tests?" [cite: 46].

**7. Hernan, M. A., & Robins, J. M. (2024). *Causal Inference: What If*.** [cite: 5, 47]
* **Field:** Epidemiology / Statistics.
* **Precise Contribution:** The definitive text on the assumptions required for causal inference: consistency, exchangeability, and positivity. Differentiates between structural (impossible) and random (empirical) positivity violations [cite: 5, 6].
* **Why it matters here:** Provides the formal mathematical definitions needed to encode "No Support" as an executable type-system constraint.

**8. NabiOS / TRACE (2025/2026). "Causal Type System."** [cite: 11, 26]
* **Field:** Causal AI / System Architecture.
* **Precise Contribution:** Implements a strict type system for causal primitives (Base types: Phys, State, Event, Rule) to prevent nonsensical variable combinations.
* **Why it matters here:** Answers "Question 3: Can experimental designs have a static type system?" by proving that causal estimands can fail to compile if structural preconditions are unmet [cite: 11, 48].

**9. BioClinica (2013). "Automated Design Validation in Clinical Trials (Express EDCplus)."** [cite: 13, 25]
* **Field:** Clinical Trial Management.
* **Precise Contribution:** Deployed enterprise software that subjects clinical trial designs to automated validation rules before "test to live" deployment.
* **Why it matters here:** Proof of deployed engineering practice for preflight checks in rigorous human experimentation, preventing protocol deviations proactively [cite: 39, 49].

**10. Holland, P. W. (1986). "Statistics and Causal Inference." / Granger Causality Literature.** [cite: 35, 50]
* **Field:** Statistics.
* **Precise Contribution:** Delineates predictive precedence (Granger causality) from interventional causality, detailing the specific vulnerabilities of observational mechanisms to reverse causation.
* **Why it matters here:** Addresses "Temporal Failure" (Prometheus Failure C). Defines the exact controls (e.g., cross-lagged, instrumental variables) required to defeat exhaust-plume explanations [cite: 35, 36].

**11. Vaughan, D. (1996). *The Challenger Launch Decision* / Organizational Memory Literature.** [cite: 7, 8]
* **Field:** Sociology / Safety Engineering.
* **Precise Contribution:** The theory of "Normalization of Deviance," where systems repeatedly experience near-misses (or degenerate data) and slowly accept them as standard practice.
* **Why it matters here:** Explains *why* Prometheus currently requires "cross-experiment constraint transfer." Correcting a bespoke error once does not change the organizational memory; only mechanical constraints (stop-the-line) prevent normalization [cite: 7, 22].

**12. HubMeta Research Team (2026). "Statistical Linting: Beyond Inter-Rater Reliability."** [cite: 12]
* **Field:** Meta-Science.
* **Precise Contribution:** Proposes deterministic auditing and statistical linting as the replacement for human-driven systematic review checks, addressing taxonomy crises and construct drift [cite: 12].
* **Why it matters here:** Directly targets measurement validity and dataset shift, ensuring that multi-agent research retains coherent construct definitions.

**13. Zarchan / Information-Theoretic Methods (2021). "Conditional Mutual Information in Data Science."** [cite: 34, 51]
* **Field:** Information Theory.
* **Precise Contribution:** Formalizes $I(X;Y|Z) = 0$ as the condition where $X$ provides no further information about $Y$ once $Z$ is known.
* **Why it matters here:** The absolute most rigorous diagnostic for Incremental Information Failure. If $I(\text{New Construct}; \text{Target} | \text{Cheap Baseline}) \approx 0$, the construct is empirically redundant [cite: 34, 52].

**14. Automated Research Assistants / AutoRA (2024).** [cite: 16, 53]
* **Field:** AI & Meta-Science.
* **Precise Contribution:** Frameworks for closed-loop empirical research using LLMs as experimentalists, prioritizing structured simulation and validation [cite: 16, 53].
* **Why it matters here:** Shows the trajectory of AI in experimental design, highlighting the urgent need for "meta-verification" and fine-grained constraint auditing to prevent LLMs from hallucinating valid-looking but structurally degenerate experiments [cite: 15].

**15. Kanewala, U. & Bieman, J. (2015). "Predicting Metamorphic Relations for Scientific Software."** [cite: 28, 54]
* **Field:** Computational Science / Software Testing.
* **Precise Contribution:** Applies metamorphic testing specifically to scientific and machine learning workflows where exact outcomes are unknown, utilizing graph kernels and SVMs to predict invariants [cite: 28].
* **Why it matters here:** Proves that metamorphic relations can be autonomously mined from scientific models, enabling automated regression test generation for Prometheus [cite: 28, 55].

***

## PART IV - ATTACK STRATEGIES

Ranked from cheapest, highest-information to most ambitious. 

### 1. EXPERIMENT LINTER (Statistical Linting)
* **What it would do:** A deterministic, lightweight static analysis pass over a machine-readable preregistration schema (e.g., JSON/YAML). It flags syntax and structural logic errors (e.g., `conditioner_set == outcome_determinant`).
* **Input Representation:** A structured JSON object defining variables, data types, causal graph edges, and the statistical estimator.
* **Pre-execution Detection:** Unreachable decision branches, trivially collinear covariates, zero-degree-of-freedom setups, missing negative controls.
* **Post-execution Detection:** N/A (runs strictly preflight).
* **False-positive / False-block risk:** Very low. Linters use conservative AST (Abstract Syntax Tree) rules.
* **Implementation Complexity:** Low. Can be written in Python using standard schema validation (Pydantic).
* **LLM Required?** No. Completely deterministic.
* **Generalization:** Highly generalizable across domains.
* **Minimum Viable Prototype (MVP):** A Python script that parses an experiment JSON and asserts that `len(control_group) > 0` and `treatment_variable != target_variable`.
* **Falsification:** If the linter is bypassed or ignored, does the rate of Support/Positivity failures remain the same?

### 2. CAUSAL AND STATISTICAL PREFLIGHT (Executable Support Checks)
* **What it would do:** Injects a "data peeking" safe harbor. Before the full experiment runs, it computes the Propensity Score (PS) distribution on blinded/dummy outcomes to check empirical overlap.
* **Input Representation:** The actual design matrix $X$ and treatment vector $Z$ (with outcome $Y$ strictly masked).
* **Pre-execution Detection:** Positivity violations, disjoint supports, degenerate risk sets, zero-variance predictors.
* **Implementation Complexity:** Medium. Requires integrating causal inference libraries (e.g., `EconML`, `DoWhy`).
* **LLM Required?** No. Uses standard propensity estimation (e.g., logistic regression, XGBoost).
* **False-block risk:** Medium. A stringent overlap threshold might block legitimately novel, highly specialized sub-populations. 
* **MVP:** A preflight hook that calculates $e(x) = P(Z=1|X)$ and aborts if the density overlap between $e(X|Z=1)$ and $e(X|Z=0)$ is below a threshold (e.g., 0.05) [cite: 5, 47].

### 3. FAILURE-TO-REGRESSION COMPILER (CEGAR for Science)
* **What it would do:** The core of the CEGAR loop. When a human researcher or the system catches an Estimand-Existence failure, a script automatically minimizes the exact variables that caused it, generates a `Property-Based Test` asserting that specific variable topology is illegal, and adds it to the CI/CD pipeline.
* **Input Representation:** Abstract Causal Graph (DAG) + Dataset shape.
* **Pre-execution Detection:** Structurally analogous failures disguised by different variable names.
* **Implementation Complexity:** High. Requires automated invariant extraction [cite: 55].
* **LLM Required?** Yes, initially, to translate the semantic postmortem narrative into a formal causal graph invariant, validated by a deterministic checker.
* **MVP:** A database of 5 known failure graphs. The engine checks new experiment graphs for subgraph isomorphism against the failure database.

### 4. INCREMENTALITY / SHAPLEY BASELINE AUDITOR
* **What it would do:** Forces a strict baseline check before accepting a "novel" construct. Automatically computes the Shapley Information Gain (SIG) or Conditional Mutual Information of the new construct against a default cheap baseline (e.g., "current fitness", "random coordinates").
* **Input Representation:** The proposed feature vector $X_{new}$, baseline vector $X_{base}$, and target $Y$.
* **Implementation Complexity:** Medium. Computationally expensive (Shapley values require multiple permutations) but algorithmically well-understood [cite: 32, 42].
* **LLM Required?** No.
* **MVP:** A pipeline step that calculates $R^2_{base}$ and $R^2_{base + new}$. If $\Delta R^2 < \epsilon$, the experiment fails the Incrementality precondition.

### 5. ADVERSARIAL PREREGISTRATION (Metamorphic Test Generation)
* **What it would do:** An LLM-driven adversarial agent attempts to manipulate the experimental design to ensure it passes the syntactic linter while violating scientific validity (e.g., finding proxy variables that leak the target to create perfect prediction). 
* **Input Representation:** Natural language protocol + schema.
* **Pre-execution Detection:** Feature-target leakage, spurious structural similarities, unstated mechanistic confounds.
* **Implementation Complexity:** Very High. 
* **LLM Required?** Yes. Requires an agentic framework (like AutoRA [cite: 16, 53]) acting as a Red Team.
* **False-block risk:** High. Adversarial models may hallucinate impossible confounds, endlessly stalling research.

***

## PART V - MEASUREMENT TOOLKIT

To move beyond concepts, Prometheus must execute specific mathematical algorithms. Here are the precise metrics to diagnose the four Failure Classes.

### A. Diagnosing Support / Estimand-Existence Failure
**1. Empirical Overlap / Positivity via Propensity Scores**
* **Algorithm:** Estimate the propensity score $e(x) = P(Z=1|X=x)$. 
* **Metric:** The area of intersection between the density distributions $f_1(e(x))$ (treated) and $f_0(e(x))$ (control).
* **Threshold:** If the minimum overlap coefficient $\int \min(f_1(e), f_0(e)) de < 0.1$, flag as severe random positivity violation [cite: 5, 56].
* **Alternative Metric:** Weight stabilization check. Calculate Overlap Weights $h(x) = e(x)(1 - e(x))$. If the effective sample size (ESS) collapses, support is degenerate [cite: 19, 21].

**2. Residual Degrees of Freedom**
* **Metric:** $df_{residual} = N - \text{rank}(X)$.
* **Threshold:** Preflight check must assert $df_{residual} > \text{minimum acceptable power threshold}$. 

### B. Diagnosing Incremental-Information Failure
**1. Conditional Mutual Information (CMI)**
* **Formula:** $I(X_{new}; Y | X_{base}) = \iint \int p(x_{new}, y, x_{base}) \log \frac{p(x_{new}, y | x_{base})}{p(x_{new} | x_{base})p(y | x_{base})} dx_{new} dy dx_{base}$ [cite: 34]
* **Diagnostic:** If $CMI \approx 0$, the new construct adds no information beyond the baseline.

**2. Shapley Information Gain (SIG)**
* **Algorithm:** For a set of features $F$, compute the marginal contribution of the new feature $f_{new}$ across all possible subsets of $F$. 
* **Metric:** $\phi(f_{new}) = \sum_{S \subseteq F \setminus \{f_{new}\}} \frac{|S|! (|F| - |S| - 1)!}{|F|!} [V(S \cup \{f_{new}\}) - V(S)]$ [cite: 32, 33].
* **Threshold:** $\phi(f_{new})$ must exceed the computational/financial cost of acquiring $f_{new}$.

### C. Diagnosing Identification / Temporal Failure
**1. Granger-Style Precedence**
* **Algorithm:** Vector Autoregression (VAR). Regress $Y_t$ on $Y_{t-1...t-k}$ and $X_{t-1...t-k}$. 
* **Metric:** F-test on the coefficients of $X_{t-1...t-k}$. If insignificant, $X$ does not precede $Y$ predictively [cite: 35, 36].
* **Reverse-Precedence Check:** Regress $X_t$ on $X_{t-k}$ and $Y_{t-k}$. If $Y$ strongly predicts future $X$, flag high risk of Reverse Causation [cite: 36, 57].

### D. Diagnosing Coverage / Novelty Failure
**1. Retrieval-Route Independence**
* **Algorithm:** Jaccard similarity of citation trees or conceptual knowledge graphs.
* **Metric:** If $Search_A$ and $Search_B$ yield sets of literature $S_A$ and $S_B$, evaluate $\frac{|S_A \cap S_B|}{|S_A \cup S_B|}$.
* **Diagnostic Plot:** A saturation curve. Plot the cumulative number of unique discoveries against the number of independent search queries. If the curve has not plateaued, the claim of "novelty" is unfalsifiable [cite: 12].

***

## PART VI - FAILURE TAXONOMY

The proposed basis—Support, Incrementality, Identification, Coverage—is excellent, remarkably compact, and maps cleanly to statistical and theoretical realities. However, based on the literature of meta-science and organizational learning, it requires a critique and a slight expansion to be MECE (Mutually Exclusive, Collectively Exhaustive).

**Critique of the Current Basis:**
1. **Support (Positivity):** Valid. Covers all mechanical data existence failures (zero variance, disjoint populations, empty sets) [cite: 20, 47].
2. **Incrementality (Information Gain):** Valid. Perfectly isolates the fallacy of internal coherence substituting for marginal utility [cite: 32].
3. **Identification (Temporality / Mechanism):** Valid, but slightly conflates *temporal precedence* with *confounder control*. An experiment can be perfectly temporally ordered but entirely confounded (e.g., omitted variable bias).
4. **Coverage (Sampling space):** Valid. Addresses search and population bounds.

**Proposed Modifications for a Stronger Basis:**
To break the taxonomy, consider an experiment that:
* Has perfect support.
* Has massive incremental information.
* Has flawless temporal and causal identification.
* Saturated the literature space perfectly.
* **BUT measures the completely wrong physical phenomenon because the sensor is broken or the semantic definition of the variable is misaligned.**

This highlights a missing orthogonal dimension: **Construct / Measurement Validity**. 
Furthermore, an experiment might succeed on all four fronts, but over-optimize a decision rule on the training set, failing entirely upon replication. This is **Optimization Degeneracy / Multiplicity**.

**The Optimized 5-Coordinate Basis (SIIMC):**
1. **SUPPORT (Mechanical Existence):** Can the estimand be mathematically observed? (Positivity, Overlap, Variance) [cite: 21].
2. **INCREMENTALITY (Marginal Utility):** Does it beat the cheap baseline? (SIG, CMI) [cite: 32, 33].
3. **IDENTIFICATION (Causal Isolation):** Are alternative mechanistic paths, reverse causation, and confounding blocked? [cite: 35].
4. **MEASUREMENT (Construct Validity):** Does the computational data structure actually correspond to the physical/semantic claim? (Taxonomy drift, semantic mismatch) [cite: 12].
5. **COVERAGE & MULTIPLICITY (Search & Generalization):** Was the space sampled adequately without exhaustive data-dredging?

This five-coordinate system supports robust failure clustering and cross-domain transfer.

***

## PART VII - LEARNING METRICS

To prove that Prometheus is not merely correcting errors, but structurally *learning* from them via Constraint Transfer, we must implement metrics drawn from site reliability engineering and continual learning [cite: 7, 55]. 

**1. Failure Recurrence Rate (FRR):**
* **Definition:** The probability that a failure of class $C$ occurs in an experiment executed after time $t$, given that a constraint for $C$ was committed to the linter at time $t$.
* **Formula:** $FRR_C = \frac{\text{Count of escaped } C \text{ defects post-}t}{\text{Total experiments post-}t}$.
* **Success Criterion:** $FRR \rightarrow 0$.

**2. Lesson Uptake (LU):**
* **Definition:** The probability that a relevant prior constraint was successfully evaluated (passed or flagged) on a new experiment.
* **Formula:** $LU = \frac{\text{Constraints Evaluated on Exp}_i}{\text{Total Applicable Constraints in Knowledge Base}}$. 

**3. Transfer Precision ($P_{trans}$):**
* **Definition:** When a generalized constraint blocks an experiment, how often was the experiment actually scientifically invalid?
* **Formula:** $P_{trans} = \frac{\text{True Positive Blocks}}{\text{True Positive Blocks} + \text{False Positive Blocks}}$.
* **Risk:** Low precision means the constraints are overfitting to the past, strangling legitimate novelty (the "safety bureaucracy" failure mode).

**4. Transfer Recall ($R_{trans}$) / Prevention Yield:**
* **Definition:** The fraction of would-be defects that were successfully caught by preflight checks rather than during expensive execution or postmortem.
* **Formula:** $R_{trans} = \frac{\text{Defects blocked at preflight}}{\text{Total defects discovered (preflight + execution + postmortem)}}$.

**5. False-Block Rate (FBR):**
* **Definition:** The rate at which the Linter/Type System rejects a design that, upon manual human override and execution, yields valid, reproducible science.
* **Formula:** $FBR = 1 - P_{trans}$. 

**6. Transfer Latency (Time-to-Transfer):**
* **Definition:** Time elapsed ($\Delta t$) between a postmortem categorizing a failure and the corresponding constraint being merged into the preflight executable Linter. 

***

## PART VIII - MINIMUM VIABLE EXPERIMENT (MVE)

To falsify the core hypothesis—*that encoding prior experimental failures as reusable executable constraints prevents structurally analogous defects in future designs*—we must design an experiment separating **prose retention** (memory) from **executable constraint transfer** (compilation).

**Title:** The CEGAR-for-Science Efficacy Trial.

**Unit of Analysis:** An LLM-based autonomous agent or human-agent team tasked with designing a sequence of 50 statistical research experiments across diverse domains (e.g., sociology, biomedicine, econometrics).

**Retrospective Setup:** 
1. Compile a library of 100 historical failed experimental designs (e.g., from Prometheus logs).
2. Manually encode 50 of these failures into **Executable Constraints** (the "Experiment Linter").
3. Leave the other 50 failures merely documented as **Prose Postmortems** (Lessons-Learned reports).

**Prospective Test (The Trial):**
* **Treatment Group (Executable Constraints):** The LLM agent generates a design. It is passed through the Experiment Linter. If a constraint is violated, the compilation fails, the linter returns the exact structural error (e.g., "ERROR: Positivity Violation. Sub-population lacks treatment overlap"), and the agent is forced to redesign.
* **Control Group (Prose Retention):** The LLM agent generates a design. It has RAG (Retrieval-Augmented Generation) access to the 50 Prose Postmortems and is instructed to "review past lessons to ensure you don't repeat mistakes." No rigid linter is enforced.

**Blinding:** The agent does not know which 50 failures are linted and which 50 are only prose. 

**Metrics:** 
1. **Prevention Yield:** How many degenerate designs survive to the "execution" phase in Treatment vs. Control?
2. **False-Block Rate:** Does the Linter prevent the agent from designing valid, highly novel experiments? 
3. **Iteration Cost:** Token cost / time taken to finalize a valid design.

**Success Criteria:** 
The Treatment pipeline (Linter) demonstrates a statistically significant reduction in *Failure Recurrence Rate* compared to the Control pipeline (Prose memory). Specifically, errors corresponding to the 50 linted constraints drop to near zero, while errors corresponding to the 50 prose constraints continue to recur (demonstrating the failure of non-executable organizational memory) [cite: 7, 8].

**Failure Criteria / Falsification:**
The entire idea of "Cross-Experiment Constraint Transfer" is falsified if:
1. **The Overfitting Hypothesis:** The Linter blocks 80%+ of all new designs (high False-Block Rate) because generalized constraints derived from one domain are fundamentally incompatible with the semantics of another domain.
2. **The LLM Capability Hypothesis:** The RAG Control group achieves a near-zero recurrence rate simply by "reading" the postmortems, proving that heavy software engineering (Linters/Type Systems) is an unnecessary bureaucratic overhead for advanced language models.

**Obvious Confounds:**
* **Syntactic vs Semantic Catching:** The linter might only catch easily parsed syntactic errors, pushing the agent to design experiments that are syntactically perfect but semantically nonsensical (Goodhart's Law). 

***

## PART IX - OPEN QUESTIONS

The literature points to a robust pipeline for constraint transfer, but the application to *multi-agent scientific discovery* leaves several attackable questions that dictate how Prometheus should be built.

**QUESTION 1:** *Can a Large Language Model reliably compile a natural-language scientific postmortem into a deterministic, AST-parsable JSON constraint?*
* **Why it changes what we build:** If LLMs cannot perform this compilation accurately (i.e., they hallucinate logic), the "Failure-to-Regression Compiler" requires a human-in-the-loop formally trained in causal graphs, severely throttling the speed of organizational learning.

**QUESTION 2:** *At what threshold of dimensionality does empirical overlap (positivity) inherently collapse in observational datasets, and how do we distinguish a structural scientific impossibility from a mere curse-of-dimensionality?*
* **Why it changes what we build:** If high-dimensional covariates mathematically guarantee a positivity violation [cite: 6, 19], our Preflight Support Check will yield a 100% false-block rate for modern ML-scale data, requiring us to build Overlap Weighting [cite: 19, 21] estimators directly into the execution engine rather than blocking at preflight.

**QUESTION 3:** *Are structural causal graphs (DAGs) an expressive enough abstraction layer to capture all 5 dimensions of the SIIMC failure taxonomy, or do we require an ontology that includes explicit variable semantics?*
* **Why it changes what we build:** If DAGs only capture Support and Identification, but fail at Incrementality and Measurement Validity, Prometheus must build a dual-representation system: a causal graph for mathematical validation, and a semantic knowledge graph for taxonomy validation [cite: 12].

**QUESTION 4:** *What is the minimum viable subset of "Metamorphic Relations" that generalize across 80% of scientific domains?*
* **Why it changes what we build:** If there are 1,000 domain-specific metamorphic relations (e.g., biological sequence permutation vs. econometrics lag adjustments), constraint transfer is slow. If there are 5 universal invariants (e.g., permutation invariance, subset monotonicity, monotonic information gain), we can hardcode the Linter in a week.

**QUESTION 5:** *Does enforcing rigid preflight constraints induce "hidden data peeking" by agents attempting to iteratively game the Linter?*
* **Why it changes what we build:** If an agent queries the Support Check 50 times with different covariate sets until it finds a statistically significant subset, it has effectively p-hacked the design phase. We would need to implement an "Adversarial Preregistration Budget," cutting off an agent after $N$ failed compilations. 

***

### CONCLUSION: THE ATTACK PLAN

If Prometheus is to learn from its own scientific failures, **DO NOT** rely on RAG, lessons-learned databases, or LLM context-window memory. These emulate human organizational memory, which is proven to degrade via the normalization of deviance [cite: 7, 8].

Instead, build a **Static Type System & Experiment Linter**. 
1. Define a machine-readable schema for experimental designs (incorporating causal DAGs and statistical estimators).
2. When an experiment fails due to Support or Incrementality, do not just document it. Write a deterministic Python assertion that acts on the JSON schema.
3. Place this Linter as a strict CI/CD gate before the expensive execution of any future experiment. 

By mapping the formal verification concept of **CEGAR** [cite: 2, 10] onto the scientific method, Prometheus transforms the vague, humanistic concept of "learning from mistakes" into the rigorous, deterministic engineering discipline of **regression testing for reality.**

**Sources:**
1. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7SOgtD1AJox4WJCO79EfegHqLQ7VmrHI_t-AG5oMuFFvuyvp1OEvsnUCga-ZSGWPg4xN7aBgIUCgbEQyxLH_yQZE9hWGK3n9u5GC3LdWpLU2pXZ23DMezEHI4yVFbxOmL5V9NUn3YX4FgSe9Zt3kei4O1DGq7QJrvmA==)
2. [technion.ac.il](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGi-8pLIDIqebZt2z_dQA1jFr9R2eDW-g4S4f4FNtvxGTO8r8JL0CRYIYjwjTERYv0ZTfnsCBfXrAZj28GzV1rf0mMKsTNKuFpn5W5AZjDIrx5QGqsnUmydsRt1A0y4RcRhnKH8Lmr1OVu7WNeCDfSrli-PSG4229Jcs2Ee-53gM0-xrEDdg5DM-OH8koStz5WW_TE1RIPqWVP8KjBs)
3. [computer.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH16IrrUoz5SFTpoU69pGHIAmCI0orvSgzqNG5eiPoWleISyIjkIZY8_XAULZjPWK0wRbwurtTbW6m8HA2BA9ACe-sEHqbHyg7q9JQ2tlqJlFXMA9YabXt1tojbgNfy04-HTyCsmoKb8SFGdD37U1eMBdhNugyOsdcOMPJE)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETOdmoXCE7WFG-qipcvW21Ex07IkN0csSNmzZLWEgquRANYdaEwEhKwQ5hmDc9vbkQv8xotaxotrITrCcchtjbAm2QcMU9l5WyIPmZARtp5ev_XNZUZYTZVg==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjqYVM8LyxCCxwT0J2BK7ae7ct56ygHsEe5yTIOE4c6FMqYo1REZhHRDgr2qkYJC_qb5CiMqweUePXDJg_C4-trlOK7sOvdHQIvALE5SlphALfrFMY_cLcvA==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1DBW9P5588te1Xq7qYKFDWsfwcXGzH64HO8-emf2EsPMu60GWe8egwMS5GYcNPFiA_KKSejuVPM9FYNIO0kaj1weZCo1ARukHWAlK25__XY19NcGS8JWfgQ==)
7. [demystifyingindustrialtech.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdGIODMgTTwcuBwSacpZAbqXkxmibdSSpETCdxvymYOOZkUxmtKmDn_wElgbuAh6o9fqoW-sFfkn1-dTnymp_wUIv_uQA88nqNHrXRMWCeuXONSedWymu2YfDxvS9z0RjakYfvzmT-o-zcEww0gMtc2yHL8Eoqpr2-0IYHCGA42zloSpk=)
8. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGe3WOvVNwN8ZuT6yRHRSFURjgdjhEciUzxMtMO9Z2nDNqdJVgmxe1Xk3Kyga4xkT3zDVlqDojOLs6Cre3GrQOBvEXjSDDoLkS2XaYdSKT9N0ZTKUd4nyjl8kwvHA==)
9. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJ6En0QiSjBjiwyt6_VRyxsf3lr_COtRSizToV35dFzuGeG1cTVs7vBA61Ylj9rZ0ADjFr9_V_7yBhUAO_nEXWdaXQsiTvKflK8BHFzPCThWCRkJZPNysz0R4QQoqbeZlwHV1G-NZl)
10. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWwyHZ5NZno-teZLuWG3IhFn-IyfUOOa9evQV9Gg5B1NInAAOQvYBq9wx4qM8GxSlfKWtqNAuqVHDMd9NH5Ts1IKAm14NzSykeKhAKV_sljd076B91FwNdm_F7dgRMm0QH4N-L5SBy4OC3C0akeKWFRWVH-66kQpldzik3pJJLLspBkuyp8xkQOAZ6uKAFXiZfmjwqbA==)
11. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMDGsCuJvFI43T8OAMYmYmgWBcnaDIVNi0XhnXr92atbZTevxSf395FdfTo7ppGr0bgnKIMXA8EMAPNNvPs8KfWomF6ROrLmtXOfGE0koPCkhvnYyLgA==)
12. [hubmeta.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUSqJpuKmQF9EAK4nhsBcBBXLdm-Qt5DkSTzmIMFkjsih8nS50_x8diffamVvXcvoIEmNJYjo8OHRCebHVcMFUIKoclitYq2e3PRTlA9v6)
13. [manufacturingchemist.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTKD8LRH9oZHNHYjawustVu1Qi-8PbHjGtElW7Cq_rc6A6STTkz6v8XhSCJwwSVixT6AfUZwsQrCZJlrvNI1LxDosleqxoXcQrIz3K120XmBcH79avAHsg1cdMhjr06ybcYUT_7LHkLk37STRNaethTEe8RPNp9dGBtAjIbYXQHym454jF4IjQqG3Un9m4cl_TQCycIuom4n18KvOD-MKoVED5)
14. [cockroachlabs.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuSSLgQdZ0_vnS849fAkxEyA3_6rWtSM_JyQA6WQnQrDgp8ug2QQN-kZTNS66SeXYgF63eeMjN1H3zHK8WthC4S8y8jmCpezaCg1y0b3tOx3S5XuxhcwmU13CH89LX1FWkkZ7SMjjdx4Svf-nfzX1Ieo1xwHK5nEUs-w==)
15. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwgemXFWGKRCPbDO8Q-UEdfjtbu1hQnEnj81vT2ihzYCWfyWzYAnxnqsjQ9MVFNY1Ae6RaJojLVdnuCrswfbeY0-pUhVoxfsxLmLmLYWrA7FaGOJRcJUILpw==)
16. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIERK6pspp65b1aWimtpCzPbu2b7yTaNnimIKi8rqF_DKEO5Bu1ok8Z2U007dB1LegpX4Pn8sORD__fl_7V275JXzy7nLxkLKsK8j-VyQfsFM4GdmQDt2IermGHf6bFc7RNv2jKmtX8QBrXZiHBLqqU0-i0otKLu585g==)
17. [giskard.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZ3FLIlIdSTuTOXphL32N_EemWjrwX8WvuJRVxTPDKdpC68G7F3iGXpc4vVDdv4Gqlmf0lke4eFo2k4wgvWgw9DIjieE6amaA3A3niv9KQyAuaygzwfS8j6fF2X1du-h2JfXr8QWNVoKIuQooHEGstBxjBo4tf9D0CX5X2ypUeo3X4)
18. [preprints.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFN6pt8AlK6vQtULcq5MBdistOwsAOsahVfOoRgIqiTUvQb_exvgrOo_tpEyB-HTeaG0vtMr9dw3b6oxQcZFsWzoI5-C_4lnxbILHbB5mlKId81pN1gjTTzAACwBwQtcsT2eszoMow=)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMQ-FnXLeucH6jokSCww5-MJxKps-EslVAzQ7Xl9dDswj18P9CLm47LJEwTCtzyD_l5UNVVV5xCd1GjpfRWqzBv6Isuo0FMaO7ebKDxappRLsF2fxc37tRnw==)
20. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkn7ynsXmLGAJajy66Ik4TsERoQ95HtwBczu_LpP5PHf34fQmmj0WrBIrCibR0sLOHSsODuQQmwhkLSIobd0P2Q3g4-fPY35umFY0ZgeBoK5-MarKj5EmJHF4IlDBtY2m-1Q7M2tI_)
21. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERZZS-sKXppwmwS8XPDdD212Il_D6TMtZsfiSkxxUyVSXmpiBKupKq8Hyo05lDx2Kpc8LUm7byyzDaBU2ELWzW2OsoO2B3dO0FXjjdXb9L_BYQrE2h6K3X2bUTvh6-7dH6Z1dV88TI)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEOZStGHGyGS3dNTaj7Bmc49IBZzFJBTXW3HC09STadufEEFf2cdVxOk3w92TBWUecY75FYlT_VJn2ju3VRgB3QYYpUgX4Aa7kAbrnqgcSIv0afjZFl_QLxmJ4Ykj0Dp4E5ss35Sw2TgLssvy6ql4AqGRP9cYbLFZZ2Zf97WD-ffUF40iMwRz4X1eAxdX7wTdiS)
23. [benchmarksixsigma.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEPUxjoYSDtwphJKIZEN1YTr43iF-siAzwGJ219na_qIPJVPtPbUiLtBEFnSBwrvMSJiLtITdnhC4o7aYdMdGf3j1YnM3lIirvNsMqTtnKY-bHELSi8U53vxP8uZZe7aV-jpK2I7vW6Wmc57g2peegPs96EcT6xJ3uDFPhahpXTrZv2tjXVA==)
24. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFDrBhRDxudhj5fmMyjIkU733vwWi_VGPC1mApJHiuUFxrjSmbnPK0KnT1D9QeJUMdljqq0GoM3K-FkFJbkfKUpFacou0_fGKz3kVJ3Bt6Lq4Y7p9uUKGBpOLS4nh3LVQbT5-aoIHiydiwQrnh7bfZH_1Z1uXqCuxsUQGXyIqbobwbiRI0CegvnVsPM8w6R2cMZOs0Rph7ucA==)
25. [prnewswire.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5HYx9h3plgifttb4nsu8yRts6HKxFUo-zLc9VUy17zYVBdkJ6FizYgb5GR45uXCuYdSdCmWmNQL3Xm1SjNJXOf7YlfjKH85qMRjVweO6vgqcHLRZdeZckLZvquhn5aIY_3B5rm2YU5QC9RWmbn3CVLMvZ9fv7EXCUQh7G39fj8ukE6H6w1UyR9nQgD0CxerVddzevLIPUS_CMzhtWsjBtpmc=)
26. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYNW5pJF4fOmSFvAB9rYdowAFJayGvkjQVlVPHkq_mi_KlyWBsNViLMQwUWRsSgAZKSOTIMHFaGHRXInGbixAkhyJ0qvFHjUcM25VtjBAkWJRrZw9wACV2OQ==)
27. [dblp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGNohUAxKumeNY8GJWANPxOJ-NzOdtPdVA70x3ehu6pGvMvwPKAo6f4VjkIAN6UN-qH7SlsiV8GltZA_Z_0wWnrXuaXNZ5Y1FnV5RLwZZLxvQC8aU-KKVUM4XaLQlDBAU=)
28. [colostate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYpgXY8AaEM2-zlgqboqFt8uH-n8AJt7lmAgnfbw0M9A5Wy17jPfcaFHV40az-dT4a08MLvQszf_530pu2DQrATrl_m15iq3aM8W2OCDymV3tPvjJFz9sKVqezZcUl7sLtMNLzEhRPyHAn9pruJuiXhJNZ66OAxCd1WOx0IEKIM9wRJMQGSNrEK5YEhb8-vuXF6A==)
29. [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-BJ7--6MQvvIHo6kFeFm-aR8XzHgFAMUsHgoDg93nCZMufwipukx64XSaQdneEztevL5GUTJeVCBcbELYPp0PB-RUejdpLqOQrFya1SR-YgVv6bczZ8CurFDktqX-H6d_-ftNtJoUcw==)
30. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo5cUQ8KxjLH6EBGzFHdWKA5zu13waKtPpaliZneBGNSA3b7nx_UJDGMXWHFScmCEfRNzmqhssUlwYi_Ur0ylkD1WKr5K0xgm0hHuZB1aWCiGcOpgjQbitwOn2Jsn3gXdyC_pltvmnig5pEw2uIisYgNI_LZt90tHGO6EeWwBWlk7O9FBGucfmopTaxPdNv4S63O6uKXty1ouQOOFF30fDs0bQIIRUOV6o8NbOgHU54pOkpAycJrhHQYKHXqsQk03maA==)
31. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEtK5MxnTXL5sFH8wI3Hjbq_9YcrrtqkLwYWEB0KBDNW5wz2pS1BusKPQy_T-ajqZlSjr-jENCqeDWtx86fuGo1sNqXEOR9De9FXekirgbjE6UXPASJ-zO049uMxY=)
32. [aclanthology.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEENxROpbCv3ww3KAgF7JrdlY7fkxWjf3XPxDc8bkvis5D-W_LdMgnMOIb0KEcGVgnGcWib8EDpa7Diy1cbIzYPW-3GcImPPe0jmihWj86-sMZgjIFH8xZH20mKprgGky7c0A==)
33. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFTrCogNBsK-Xw2UHdNRU3wjjMotkHmMRo8cjj6-WHlLc8Zt8Ho05Dz2b07V9r0S6MaGz27aOA7ZN2-bPxcaHt6VhKsX5HDt_PScCndXoRDvysi5kSxJkokdC_Bqkh7-5M=)
34. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwYbzRMEK-nKEQxE46y59ag1wNR-L2vY3wAz42pMXLtWtv7KFpKUrp4ox511rU1ZJ4BdeMFqifJQGglmOIgwKd77CjGcsMMFKe9bftFD8ffGalFU3CLrt1lHshC06qqu8fYOXBPcDYMj5qdMyxZ6tli-9aSizwghhDy7FyjTLLQF0=)
35. [substack.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeSOC9T3ldJ0z4PKncxhNuv6P34AadJBQ4MYNSFP-cCQHvzAkTtUjDnQWIvLhZkdlRqkW-LqgtpFF_yy7Pfg3h0a6Vfj-rmINhdwcDIF2J0Gs8QXM4Z9vRh1tFks7BDZJ5BWxY4W7wysQ=)
36. [casrai.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEveKkfqCpRvLiNhpBdzqE3MNPGUFcVDo_BP9TnCqIqaLW-m_X_ypKsXX09UoIX-fr0YVQVpIXsgV2vHHdDjIOCVMKooDLyKfTsS0n9gDMqiL1a7QfK6cCiLsxw-omQ5kdPLvwaWBrlj3rl)
37. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGUZ4liPewgkXkBPm04VP2thw3eJSIyyIJvF_ZD0MqLIrXU4f0angInflJ8G9JuHbxPTJ4Z5iSziWTFxnKZjXiqp1hAzCpOTu0WglHHTuAInaj7U5efWfSRmbR_02oLWFWU29Xx9VIp1DTEGi0uCw=)
38. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFar6jGf9wSdq1NS90F0d_c_MgeHVlq8KdwIDWUn28zUu-FcFiydqs2S_R2hwFcF2CZZM4h6YNAwvKr0U2KoOs7QVdu5t65iGRvn6ogyVWVwa1ePx85Cqs-TfbBF4FaGL0_Wyo0pk7C1VZgQ6TAecyQ_pEVK7qKlXm3fDNRYOSrNBeGPm9y-iMt2_ICELTR7YxgITIx21c4Lk_M5dlNMnl9oQ-UIu3dltwz0p3DlGeeLPp10_4=)
39. [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvf65TDdd7bilHb3dgDTW89hEe0KBFC0I4-UAn_BQn7MNq6oAjVwOYN00WC7wrnDb0JOm_tGGKj6c7clYiWv7fLbEvVYlmCEPIcrCE4cxKt8-PVMtInsZBH1QlWCKa)
40. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHSZrpwyZxm8yVZLTm-Z7ZBs93tMwBae1C4hnPNCIB00Sm8XsJmTtpwtpXmkS0W0yEsWSNxVOwtUaYrvVAEK6Fiam7-IR5lY_RCyW0BfPBeR_uypymcwrohB6X-TK-AWFFirIV_ybVFkWfKuZ_HeTZ6qNH9wkdy9pMqiEOgSgtnTp6tRpUAF2hrx7JLWgoLGFQ8PJUgvbQ=)
41. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHAapOEf8tjfyIEGXNvPuzPiQHf6yEPIyVQlg_zGudi9eYhRTnVWiyaauV36VgBYLIr1HgYvr44qSZmsE4wYgk8DqmggRxzc6lX80ukY_5tN02c8gDg0GE2zuvqntHWg8bDExvartN4Igr9ryty99TkGDwpZqEg0XZfzztgomohX9It0C5P)
42. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7l6zNClQxyQgTILkyJ-nvphSdvOhjonbEPtAJfR35s5LQV0iKGe62QBspM6tgFeIAWa_yNyB1qi1vFEOPhhTZbP5LpBqWelONBQCnb1yHnGpKjCXS3g==)
43. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLFbLo3KPyGp14z3hwkv07QfQ3jLBqTogfQWlo2Zczh8qj17gh1lV5TCvDuYNEK8zLQ7ReVV1cZza9tAoymnyfhUWK_8qzlUoUlb8t90y5X-PIk8jqMG4De5RhfXYILH-YY1KEXF6Qt5H8jkjXrDrCY4gHyMN6lTLiJb_fpfDrc5nFfULtZe5QWUCpTxMHlY9EOHeHRangqxx7A5QcgbwvTj3wSztYekq1-jbZ5X2J-AegvUXCT3Ov0uDtdjdd8HXX)
44. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVvnEUyCLo9rnXmrQi7L55gDQhsh1M0ePvWToZRLmwNmTLjEPBNVCHvYNST3DYU0TwraJHt9IXFx51wDvGdJnngHq1OEfj-ZHquYBudASKGiiwF6olfhLJ2B_hp4trHzfB-LsZCO7s60WyyhByrB6ieypd1rwSZndbk6xyxtIUFaRi3nV_xL2nkeu8QOuXSUzU0w==)
45. [tugraz.at](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVY59FsviI9vWKWU63XBjIc1I5__acFS5Z4r6nRC_5w68ogDRxltn6lbbMC0En6f_gE3TemknpTIgykjZ6LhklWG0mWpjOsCo9U3lRPPv5ljpq4xJmNgczDIBPaOQn2ZOBbCy0jYi1HVZRd2jCB5V85YfuuHCs4W7X1JfofRyczyR48_0=)
46. [tianpan.co](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjsLzb3ofl3RMhFF1ZYwaup3UxO6Ek1X1mGuxGaRiUTa3jXKp-sCeXx--aMJJb-SPy5MbOLt5sGRk3ddXkfx4yLpafp8unUqhF2PUQSn2HwBR5ClYcMX5PuYfemL8Q005RGDmOqEzOizn112M17B56dXI6qm7XQ6BD7Sg=)
47. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-N5VrjesS7RR1WU4i1SXSaFQEWhegST6CUgc6r5557bauZjFWxlYO5Nha87LTsmcQRs0xd8a_xegbSOfY-Sr1U3dg1x-5yeV9Uozh1FidQHG8YnqbLg==)
48. [nabia.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwIAf3PbxO99mYCoinskffb7hd_o1Qz2OyiGNxtA3N58sM37agB31zZgbe1FigvlkWO47wgUu84I8Y-zEdUfJJtyyxOaF74sQp4-GyiG8U_ak5)
49. [patsnap.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxOthtTBZ7OfVmRwGkSOhPIKA4ityRUvq1IW-SQ6hBYTv3sH_396WUL754_TXrVFtFuhj72FZRECxLyvH8aq9VYAExX0nfqGKWlNFGkOkbab4KgDMOnXjY0C5flC_1BVPH5IbmbAeemFhdrN-LHBKmWdK9btlGwEJzrAHmrDgTCUhfgTbywUQ-LYpO8V6v5PQwfJMvOg==)
50. [oup.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2_Oz8iCkhFt_rhicpm_3SBkiHzSAS8FcsVNTM6lesMwaVfwHRJJirhQk2H9yxk_geuORVvKCIhG7XK2-8LhpqxyXnjQ9yuQMIVoC-O7-WgPRofXovgTfe4Wsi8pcINpKYtBIEz1DkeX15tzPzqr4=)
51. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpqTIe4zZjXj55iBWxhhpAQjPKXsJbzqfX6v47xOSVBjJHayjOITyt-gy3m64OQJOvxcZU112DamXjcKJTi3XQTn1loyQLSQhtoe5ORUNWFk47UpgSY8syOA==)
52. [dokumen.pub](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF229pm7y3g9ovIBFBI7fgasNS61ZTKLDoM7vZWFHqfEQGQziW_QU4iUQ8EEXrSWEeT1VEeE0qNy3B3fxFYY74MeaGJ87kCk4AmuH3sSu-RtU5DDfrwH_NVT1Poo23CGKIWVLBbfGzkekGaYMo3_V4Fbjsnmu94qrIm_Oah0uXCzptE4But9oB6ihrKiQEuPq-mWT-GpSuEJA==)
53. [sciencenews.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgZpk5Eu2CVJw5cZ4k7PdOHOoJBNIivQ8GOzRohpwB0wJZ2QUl-QHnQk7gNHng2VvwxN8gpdEoHzwtstDZ9sOFUvqCUMJ8h7UCITeHPK3F1VUAWiizZdhqTH8hXC0rnQj1jYnasd-Hrk1ZIPrjxMJworeC0W9AeCUwEkD71CE=)
54. [iastate.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWsurrsHM94iiLKx4yHh-wchkCCYnq0iDfC7TNjUZYfUm6gAj8ye2bB9sBkgDgV_7ktUmuUHx6E4kbdNFyWuz8n6aAWe0S0EU_eW04zBKQZBsKD_qJ6Mgm7Xhctqbh9FcXp3OVs-Mv-Ywn9_5Xv5NREiQW5FnNZjfkLWhBwvyWuxDmL7GmbXXnlw==)
55. [proquest.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDle3M12XifSZgf_whQP1zWBjh3jJzYpZWdj1x_-2nXGvyUpjp70UJnt7QV3RmY_fQbLbc36yxPj3nkh2SN356db6CESp-abWdpwivOtOI2W1PtDEsBDSYFqWj_bOSB9wCHq-GBb0NxiXrXkgnK77xFMDzqWzc3XXIaatv3CcFGcfFzQf0ZYLO6qtwBkYeU81x5x9FF64wrl0xgyCXNeqDKUfM)
56. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVWgMc7ZpU0Di0az0chD3YnzJJFvBUXvaExBznaBS4vLVbHIFuUU_T8iBf2qFXWKJICYAE3pS7q_Ghv9zvZSSp91izSFbIYdNQcI9SN7sV9Y0Ky8wZQhtHAQ==)
57. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGvekAtfd05CY0I8Et8x9v8Tpf5GLJboAw4v97eoa3JTslgrPLUkpgTyD61DYrEwow7k5BL1ceGr3TtP3mOG1s4nAKwV7ZFOGFjKjcY_KYtEWHYfPBpR_lwtPG4U3yMXM1wSLKxtoTHbFSpBiqm4dgc_2uchF7dlNU=)

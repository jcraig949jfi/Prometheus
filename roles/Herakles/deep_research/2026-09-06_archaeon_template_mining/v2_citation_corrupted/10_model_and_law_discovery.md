# Prompt 10: Model and law discovery

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_ChdabGFkYXJtNExOT3ZfUFVQNGIzMXFRdxIXWmxhZGFybTRMTk92X1BVUDRiMzFxUXc
**Elapsed:** 273s

---

# Benchmarking Model and Law Discovery: A Framework for Computational Research Experimentation

**Key Points:**
*   **Methodological Alignment:** The translation of complex model and law discovery paradigms—such as Symbolic Regression, Equation Discovery, Causal Discovery, and Scientific Machine Learning—into strict, sealed computational bench specifications highlights a fundamental tension between open-ended empirical science and constrained, state-machine verification.
*   **Bench Constraints:** The current computational bench heavily restricts experimental expressivity. With only three exact executors (`noop_v0`, `evaluate_bitstring`, and `random_walk_v0`) and a single scalar comparison outcome rule, representing empirical data-driven fields necessitates the formulation of new executor kinds and specific expansion requests.
*   **Expansion Imperative:** The most critical capability lacking in the current bench is the integration of external empirical datasets and continuous differentiability. Without these, paradigms reliant on observational constraints (e.g., the PC Algorithm) or physics-based loss residuals (e.g., PINNs) cannot be faithfully executed.
*   **Epistemological Limits:** For any proposed specification, a "SURVIVED" verdict under a single scalar comparison rule inherently provides limited scientific license. It signals algorithmic convergence or threshold satisfaction but does not—and cannot—confirm global physical truth or generalization beyond the provided synthetic or narrow evaluation landscape.

The design of a computational research bench necessitates a rigorous accounting of what constitutes an experiment within any given scientific discipline. This report addresses the request to mine a specific cluster of research disciplines—collectively termed "Model and law discovery"—for concrete, runnable experiment templates. The targeted fields are Symbolic Regression, Equation Discovery, Causal Discovery, Scientific Machine Learning, and Computational Mathematics. The challenge lies in translating the rich, heavily empirical literature of these fields into the extremely narrow constraints of a computational bench that relies on sealed specifications, strict parameter spaces, and a solitary scalar outcome rule. 

This analysis does not serve as a traditional literature survey but rather as a design task grounded directly in published methodologies. For each field, we extract the smallest characteristic experiment that accurately reflects the discipline's genuine practice. Where the existing bench executors (`noop_v0`, `evaluate_bitstring`, `random_walk_v0`) fail to capture the honest methodology of a field without severe distortion, new executor kinds are proposed, accompanied by precise capability expansion requests. 

## 1. Symbolic Regression

Symbolic Regression represents a distinct paradigm within machine learning where the structure of the model and its parameters are simultaneously optimized to discover mathematical expressions that best fit a given dataset. Historically and practically, this is most commonly achieved through Genetic Programming (GP).

### 1.1 Methodological Foundations
The foundational architecture of modern Symbolic Regression via GP was formally solidified by John Koza in 1992 [cite: 1, 2]. Genetic programming extends traditional genetic algorithms by increasing the complexity of the structures undergoing adaptation; individuals in a GP population are hierarchical compositions of primitive functions and terminals (variables and constants) appropriate to a specific problem domain [cite: 1]. Rather than explicitly programming a solution, GP views the search for an answer as a search through the space of all possible recursive compositions of available primitives [cite: 1].

The evolutionary process operates iteratively in a dynamical environment. An initial population of random computer programs (compositions of functions and terminals) is generated. Each program is executed and assigned a fitness value based on how well it solves the problem at hand [cite: 3]. The population is then transformed through Darwinian principles: highly fit programs are copied directly to the new generation, while others undergo genetic recombination (crossover) or mutation [cite: 3]. For instance, crossover involves genetically recombining randomly chosen sub-trees of two existing programs, with a typical distribution applying crossover to 90% of the population and reproduction to 10% [cite: 1]. 

A critical methodological constraint in GP is the "Sufficiency Requirement," which mandates that the available primitive functions and terminals must be powerful enough to express a solution to the problem [cite: 3]. Furthermore, the method relies on "closure," ensuring that any function can accept any output from any other function in the primitive set [cite: 3]. Advanced forms, such as Strongly Typed Genetic Programming and Gene Expression Programming, have further refined these constraints to create more efficient genotype/phenotype algorithms [cite: 3, 4].

### 1.2 Translation to the Bench
The current bench provides `evaluate_bitstring`, which evaluates a bitstring against a hidden target derived by hashing a seed root [cite: 1]. While one could hypothetically map a linear GP representation to a bitstring, doing so distorts the fundamentally hierarchical, tree-based nature of traditional Symbolic Regression [cite: 1, 3]. More importantly, SR requires mapping expressions against empirical observation data to calculate fitness, rather than a purely cryptographic landscape. Therefore, proposing a new executor kind is necessary to maintain fidelity to the method.

### 1.3 Smallest Characteristic Experiment Template

BEGIN_TEMPLATE
{
  "template_id": "symbolic_regression_gp.v0",
  "kind": "evaluate_symbolic_tree_v0",
  "param_space": {
    "max_tree_depth": {"int_range": [cite: 5, 6]},
    "population_size": {"int_range": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Symbolic Regression",
    "reference": "Koza, J.R. 1992. Genetic Programming: On the Programming of Computers by Means of Natural Selection",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment evaluates whether a constrained space of hierarchically composed primitive functions can reliably converge on a minimum error threshold when evaluated against a static environment. The field runs this to demonstrate the efficacy of evolutionary search in symbolic space over random search. A SURVIVED verdict implies the population found an expression satisfying the scalar loss limit, but it would NOT license the conclusion that the discovered expression is the true data-generating physical law, nor does it guarantee the expression is parsimonious or generalizing beyond the exact training data."
}
END_TEMPLATE

## 2. Equation Discovery

While Symbolic Regression uses evolutionary search to find equations, Equation Discovery in the modern context frequently leverages sparse regression techniques over pre-defined function libraries to identify governing nonlinear dynamics.

### 2.1 Methodological Foundations
The seminal approach in this domain is the Sparse Identification of Nonlinear Dynamics (SINDy), introduced by Brunton, Proctor, and Kutz in 2016 [cite: 7]. SINDy re-envisions the discovery of dynamical systems from the perspective of sparse regression and compressed sensing [cite: 7]. The foundational premise is that most physical systems are governed by equations with only a few relevant terms, making their governing equations fundamentally sparse within a high-dimensional nonlinear function space [cite: 7].

Given a dynamical system defined by \( \frac{d}{dt}x(t) = f(x(t)) \), where \( x(t) \) denotes the state of the system and \( f(x(t)) \) represents the dynamic constraints (e.g., Newton's laws), SINDy relies on the observation that \( f \) typically consists of only a few terms [cite: 7]. The methodology involves curating a library of candidate nonlinear functions (e.g., polynomials, trigonometric functions) and applying convex sparse optimization to find the minimal subset of candidate functions that accurately describe the time-series measurements [cite: 8]. This approach naturally balances model complexity with descriptive accuracy, avoiding the overfitting commonly seen in unconstrained machine learning models [cite: 7].

SINDy has been extended to handle external forcing and control inputs (SINDYc), ensuring robust performance in both autonomous and forced systems [cite: 8]. Furthermore, when dealing with high-dimensional systems, the method often employs dimensionality reduction techniques like Proper Orthogonal Decomposition (POD) to approximate the system on a low-rank basis before applying sparse identification [cite: 7].

### 2.2 Translation to the Bench
Equation discovery via SINDy cannot be performed using `noop_v0`, `evaluate_bitstring`, or `random_walk_v0`. The methodology explicitly relies on a curated library of functions and a continuous thresholding parameter to prune negligible coefficients [cite: 7, 8]. The absolute smallest honest experiment requires applying a sparse regression algorithm to an internal matrix representing the candidate library.

### 2.3 Smallest Characteristic Experiment Template

BEGIN_TEMPLATE
{
  "template_id": "equation_discovery_sindy.v0",
  "kind": "sparse_regression_sindy_v0",
  "param_space": {
    "library_size": {"int_range": [cite: 6]},
    "sparsity_threshold": {"choices": [cite: 5, 9, 10]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Equation Discovery",
    "reference": "Brunton, S.L., Proctor, J.L., and Kutz, J.N., 2016. Discovering governing equations from data by sparse identification of nonlinear dynamics. PNAS.",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment tests the ability of sparse regression to isolate active terms from a candidate library to represent dynamic constraints. The field runs this to identify parsimonious governing models without overfitting. A SURVIVED verdict indicates that a sparse subset successfully minimized the residual error below the bench's outcome threshold, but it would NOT license the claim that these specific terms are the true underlying physics, as correlated library terms or improper coordinates can yield mathematically equivalent but physically spurious sparse representations."
}
END_TEMPLATE

## 3. Causal Discovery

Causal Discovery seeks to infer the causal structure underlying a set of variables from purely observational data, typically representing this structure as a Directed Acyclic Graph (DAG). 

### 3.1 Methodological Foundations
The cornerstone of constraint-based causal discovery is the PC algorithm, named after its developers Peter Spirtes and Clark Glymour, and detailed extensively in their 2000 textbook *Causation, Prediction, and Search* [cite: 6, 11, 12]. The algorithm operates under the assumption of "Causal Sufficiency," which dictates that there are no unobserved common causes (latent confounders) influencing the measured variables [cite: 11]. 

The PC algorithm functions by exploiting the connection between conditional independence relationships in the data and the graphical concept of d-separation [cite: 11]. It transforms raw probabilistic data into a Completed Partially Directed Acyclic Graph (CPDAG) representing the Markov equivalence class of plausible structures [cite: 11, 12]. The procedure occurs in two primary phases. The first is Adjacency Search (Skeleton Identification): starting with a fully connected undirected graph, the algorithm systematically tests for conditional independencies [cite: 11]. An edge between X and Y is removed if an independent relationship \( X \perp Y | S \) is found for a conditioning set S [cite: 11]. The algorithm starts testing with conditioning sets of size zero and incrementally increases the size [cite: 11]. The second phase orientates the remaining edges by identifying v-structures (e.g., \( A \rightarrow B \leftarrow C \)) and applying deterministic rules [cite: 12].

Implementations of the algorithm must manage computational complexity, as runtime in the worst-case is exponential to the number of nodes [cite: 6]. However, for sparse graphs, it is highly efficient; an implementation on a DECStation 3100 recovered the ALARM network (37 vertices) with fewer than 8% edge errors in under 10 seconds using 20,000 samples [cite: 13]. Extensions like the Target-first Bayes Factor PC (TBF-PC) algorithm use Bayesian Information Criterion (BIC) approximations for conditional independence testing [cite: 14].

### 3.2 Translation to the Bench
The PC algorithm is fundamentally a constraint-based search that eliminates edges based on conditional independence tests [cite: 6, 12]. It is entirely distinct from random walks or bitstring evaluations. The smallest characteristic piece of this method is the skeleton identification phase, governed by the maximum size of the conditioning set and the strictness of the statistical test.

### 3.3 Smallest Characteristic Experiment Template

BEGIN_TEMPLATE
{
  "template_id": "causal_discovery_pc.v0",
  "kind": "pc_algorithm_skeleton_v0",
  "param_space": {
    "max_conditioning_set": {"int_range": [cite: 15]},
    "alpha_significance": {"choices": [cite: 6, 9, 16]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Causal Discovery",
    "reference": "Spirtes, P., Glymour, C., and Scheines, R. 2000. Causation, Prediction, and Search. MIT Press.",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment performs the adjacency pruning phase of the PC algorithm to build an undirected skeleton of conditional dependencies. The field runs this to narrow the hypothesis space of causal DAGs using observational constraints. A SURVIVED verdict demonstrates that the resulting skeleton's density falls within the target scalar range, but it would NOT license the conclusion of a definite causal direction between any two nodes, nor does it guarantee the absence of latent confounders, as it relies strictly on the assumption of Causal Sufficiency."
}
END_TEMPLATE

## 4. Scientific Machine Learning

Scientific Machine Learning (SciML) merges traditional computational physics with deep learning, focusing on embedding physical laws into neural network architectures to solve both forward and inverse problems involving partial differential equations (PDEs).

### 4.1 Methodological Foundations
The definitive framework in this space is Physics-Informed Neural Networks (PINNs), introduced by Maziar Raissi, Paris Perdikaris, and George Em Karniadakis in 2019 [cite: 5, 9, 16]. PINNs act as universal function approximators that embed the knowledge of physical laws—described by nonlinear PDEs—directly into the learning process [cite: 5, 15]. 

Conventional machine learning models often lack robustness in biological and engineering applications due to low data availability [cite: 5]. Without prior physical information, solutions are not unique and can violate physical correctness [cite: 5]. PINNs remedy this by utilizing a loss function that penalizes not only data mismatch but also the residual of the governing physical equations [cite: 5, 9]. Consequently, neural networks can be guided by training datasets that are small or incomplete, and can even find accurate solutions to PDEs without explicit knowledge of boundary conditions [cite: 5]. 

PINNs have been expanded to handle space-time domain decomposition via XPINNs and cPINNs (conservative PINNs), which tailor the framework to conservation laws [cite: 5]. Analyzing the training dynamics using the Neural Tangent Kernel has proven crucial for diagnosing failure modes in multiscale systems, leading to adaptive weighting schemes [cite: 9]. The methodology fundamentally relies on continuous time or discrete time continuous function approximators that are fully differentiable with respect to input coordinates and free parameters [cite: 15, 16].

### 4.2 Translation to the Bench
Because PINNs require full differentiability to compute the physics residual via automatic differentiation [cite: 15], the discrete space of `evaluate_bitstring` and the stateful integer increments of `random_walk_v0` are categorically incapable of representing them. A new executor that provisions a continuous neural network and computes a specified PDE residual over random collocation points is required.

### 4.3 Smallest Characteristic Experiment Template

BEGIN_TEMPLATE
{
  "template_id": "sciml_pinn_residual.v0",
  "kind": "train_physics_informed_nn_v0",
  "param_space": {
    "collocation_points": {"int_range": },
    "epochs": {"choices": }
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Scientific Machine Learning",
    "reference": "Raissi, M., Perdikaris, P., and Karniadakis, G.E., 2019. Physics-informed neural networks: A deep learning framework... Journal of Computational Physics.",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment evaluates whether a neural network can minimize the residual of an embedded physical equation across randomly sampled spatial coordinates without requiring empirical boundary data. The field runs this to demonstrate data-efficient function approximation constrained by physics. A SURVIVED verdict establishes that the network converged to a state where the physical residual is below the specified outcome rule, but it would NOT license the conclusion that the network represents the unique true physical state, as the loss landscape is highly non-convex and the solution may be physically incorrect if preliminary information is insufficiently weighted."
}
END_TEMPLATE

## 5. Computational Mathematics

Computational Mathematics encompasses a broad array of numerical methods used to simulate deterministic and stochastic processes. This includes the formulation of algorithms to approximate solutions that lack closed-form analytical representations.

### 5.1 Methodological Foundations
One of the most ubiquitous tools in computational mathematics is the random walk, used to model phenomena ranging from molecular diffusion to financial market fluctuations. Methodologically, a one-dimensional walk involves sequential stochastic increments. The statistical properties of these walks, such as expected distance from the origin over time or return probabilities, form the basis of Monte Carlo methods and stochastic differential equation solvers. Computational evaluation relies on testing the asymptotic behaviors and stateful progression of these discrete steps over specified budgets.

### 5.2 Translation to the Bench
Unlike the other fields in this cluster, Computational Mathematics maps perfectly to an existing bench capability. The `random_walk_v0` executor is specifically designed as a deterministic one-dimensional walk where increments are drawn from a derived seed and scaled [cite: 1]. Crucially, it is the only stateful kind on the bench, permitting experiments that test persistence and the accumulation of state across repeats. 

### 5.3 Smallest Characteristic Experiment Template

BEGIN_TEMPLATE
{
  "template_id": "computational_mathematics_walk.v0",
  "kind": "random_walk_v0",
  "param_space": {
    "steps": {"int_range": [cite: 6]},
    "step_scale": {"choices": [cite: 6, 9, 10, 16]}
  },
  "origin": {
    "source": "LITERATURE",
    "field": "Computational Mathematics",
    "reference": "Standard discrete stochastic modeling texts (canonical method, matches existing bench capability)",
    "proposed_by": "Herakles"
  },
  "status": "PROPOSED",
  "admitted_by": null,
  "admitted_at": null,
  "rationale": "This experiment executes a stateful computational walk to evaluate the bounds of accumulated spatial translation over time. The field runs this to model diffusion paths or verify the statistical bounds of pseudo-random scaling. A SURVIVED verdict demonstrates that the final position of the walk satisfied the scalar bounds defined in the outcome rule, but it would NOT license the inference that the walk is statistically unbiased or that the underlying seed derivation accurately reflects true physical Brownian motion."
}
END_TEMPLATE

## 6. Required Bench Expansions

To implement the "proposed" templates above, the bench requires distinct capability expansions. The fields of Symbolic Regression, Equation Discovery, and Causal Discovery are structurally similar in their need for empirical data: they are not testing abstract mathematical properties, but rather the relationship between a model and an observed reality [cite: 3, 7, 11]. The field of Scientific Machine Learning requires an entirely different capability: differentiable continuous optimization [cite: 15]. Therefore, two expansions are necessary.

### 6.1 Empirical Dataset Binding

The most glaring omission on the current bench for empirical model discovery is the absence of observational data. Methods like the PC Algorithm operate explicitly on conditional independence relationships found in sample probabilities [cite: 11]. SINDy requires time-series measurements for its sparse regression [cite: 7]. GP requires an environment of test cases to assign fitness [cite: 3].

BEGIN_EXPANSION
FIELD: Causal Discovery
LACKS: A standardized mechanism to inject static empirical observation matrices (datasets) into an executor for candidate evaluation.
WHY: Causal Discovery, Equation Discovery, and Symbolic Regression are empirical fields that derive structure from observed sample data rather than cryptographic landscapes. Without a way to feed observational data matrices into the executor (and evaluate a resulting loss/independence metric), the bench fundamentally restricts discovery to synthetic, self-contained generative rules, locking out all data-driven hypothesis testing.
SMALLEST_FORM: A new payload parameter dataset_identifier (a string resolving to a static matrix provided by the bench environment) and a scalar result field empirical_error emitted by the executor for the outcome_rule to evaluate.
BLOCKS: Symbolic Regression, Equation Discovery, Causal Discovery
EVIDENCE: The PC Algorithm (Spirtes, Glymour, Scheines 2000) requires sample data to test conditional independencies (X ⊥ Y | Z); SINDy (Brunton et al., 2016) specifically infers governing equations "simply from data measurements"; GP (Koza 1992) requires evaluating programs against environments to determine fitness.
END_EXPANSION

### 6.2 Differentiable Continuous Optimization

The second capability gap prevents the execution of modern physics-informed methods. The bench currently supports discrete logic (`evaluate_bitstring`) and simple state accumulation (`random_walk_v0`). It lacks a mechanism to represent continuous variables and compute gradients over them, which is the defining characteristic of SciML.

BEGIN_EXPANSION
FIELD: Scientific Machine Learning
LACKS: An executor environment capable of automatic differentiation to optimize continuous parameterized functions against mathematical residuals.
WHY: Scientific Machine Learning embeds physical laws by calculating the gradients of a neural network's output with respect to its input coordinates (e.g., space and time) to form a PDE residual. No combination of discrete bitstrings or non-differentiable random walks can represent or optimize a continuous differential equation loss landscape.
SMALLEST_FORM: A bench executor that provisions a basic continuous multi-layer perceptron and a parameter continuous_domain_samples that dictates how many spatial points are evaluated for a pre-defined PDE residual, returning a final scalar loss.
BLOCKS: Scientific Machine Learning
EVIDENCE: Physics-Informed Neural Networks (Raissi, Perdikaris, Karniadakis 2019) form a class of universal function approximators that fundamentally require being "fully differentiable with respect to all input coordinates and free parameters" to encode physical constraints.
END_EXPANSION

## Conclusion

The transformation of abstract discovery algorithms into rigid bench specifications exposes the operational limits of automated science. The `computational_mathematics_walk.v0` template proves that some disciplines natively align with constrained, stateful executors. However, the templates generated for Symbolic Regression, Equation Discovery, Causal Discovery, and Scientific Machine Learning heavily underscore the necessity for the proposed expansions. By adhering strictly to the documented mechanics of Koza (1992), Brunton (2016), Spirtes (2000), and Raissi (2019), it becomes clear that computational research benches cannot host true model and law discovery without first accommodating empirical datasets and continuous differentiability.

**Sources:**
1. [genetic-programming.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFS43jICA-H6mBDoorWBJiHPkO9XIRjqCZlKi79MhFG7q8QnH3ESm0unVh_UfCqR_tOJexOPhKyzAxzL2BWa3NKNRXM15KC4E7gW7eI_BWqDh_D8Fv6Js7hKjWq9EiuVdFb6mrGLFtAbs2ez4g2OCqSdg==)
2. [google.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_GKxe8yo5yW2LPu_vdEd0y0xcdibzvvcUWjyDUVCRgK8_5U0IQ1z31O9YBV7LzSgYNveZ7EJvOC8MDi4h7V_DMsNqz2tGQbxgmHMuSZC9pWtJt7YO86qiiDt90MiEQttLL-11W16PwyWcPAM6Jpj3EPiOiF6sK7wtzRB3DVUAj3qZwg==)
3. [uottawa.ca](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyKAJh4DmFPwtjII2xlN9OODOnFQCukHD0u9UI0bDW65w2fdoUNVjiQSLOqP33fB_E7s7maWRrP2oHfb0l3hrdl6eCBMYEYHcdxNe913VTG0E1MIoRHN9wvCIpzBNmW9uC)
4. [semanticscholar.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtnPoBieclAFt0WEjtKHNps-r68GQT281dS4rzkRs05c8GJA9e_I1gsXR2Jeazf98-iVFd6fNewXQm50vkVXAWbqbievX3_0tWfoksF5oukgO2G290rn1-u_bLCIQsBIcKP6TjDhDFFbWQLb-TXTAuY2bjRQ82zqqmWVxRbFUSHdx9Cy2e4buzYrRjoww68GkXoib6MR8Gnc463x81UAUaRsX98lsUiWEOMR2JORyazJL33F6evNBlmRVdd3oP8FA=)
5. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFa1nTQ3_9GMz4Vzzh-ykbafTmpG6LuEFwE3fxLp_lj5ZmcLE_mCOhBnTMw-LD5asTCWVoeDD8UiZAdccC7vl_LjHT-qZ-cuZi-kvRDoXMHUjs4CJLJZuo2WPfTw5JvqhPdK5hj-Csk1X5uml48yZ1UDagCw==)
6. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH4TI3f5UIgMSl51ClkowfLM7lDwywpiNCh9ezz5VAKsy6iL9PkdaktrzuURY55NQEZNnFngymG1w5V25-pHWgMw-994B7JRyqjl8lYGAK7is_573eCFg==)
7. [pnas.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_sCesCoq18AGaJVhqYZy3wfXZXzfvRp5DfowaFfoQ3zUUZ6FgCJ86hox-x5KOnfSyBa66kSqKH_I95UJLxfHh8jjUxiwf83azyEuNUuzQRjq11CGR-CuHRMRLVJvGzOdOWma3Ob8=)
8. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgnbv_U6_zqW8bg2OuU1jL_ra5IdEfoygADv3q5z1E6aV_vEVpOwp7djlr8-rZ6ajxeSZoWN1WBv-ja-JhTGA5iv8TASeWE3ZPJsyQfszyDd0JDxER8b9G1HL_T6koXwJgejkSAiCS2LldA_Nvm0mxS_HEcHTaFcNO7hFaMh75vtlXoPXg)
9. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzT0Y8wz-YJc33HfYc_SZKYmM70CkETyaSQZMAnU4GMV_kPlcIIK0Ur3LK1-KHZga2NP-l1lI6J_VgJoqgWKPqiwt3b0RyypxKBpLltT1fT5FXVvXqK8W4a2ZRLYw=)
10. [scirp.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwi_BSluE4FdWUZjHpLkB1i8TrBc-3trucrfX8NUEo9R6eNl8DE7kT7K-czISyYCBi3sXbDeK1ePbPC5KebHNjr2rccCu9L_bxnT5xwmalx_uFdKjnPwQ2Ukh3sXVwpDKrmy8Snj8lkVxR4yMKq9W8j4XTegrHiu0yxw==)
11. [apxml.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEHFptvlPNXf1aMkl_2tQSwJkRlEzLIEx6jsTP2sH9JWkdtLbnZEi_s06S65-cBDOBchD-iriNt2rdV7Wp26i2RjdGxP6Ys_PUgJYMG2sRvC8Wf0CeUaIQXJ6LG6hpU8yzqyae_EMYbTw55bNLP4fKZRpmj0Cu69RjimQI1RBlsWhKJUFciMb5PxZQG-jjYmwid_YfIcmyGx66JaOMUVjZIzU5nYWIqP_FRCw5avBrBLaf_p8u)
12. [licentiapoetica.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLTEzEub9mY1KfbQQkNvGmM7p_QLt09m6YCzOoG6GX1T5yal4OjDLDuCczyo3ZS1bWorrdToeLZgbDrakyfs58Jor8P-YftLpNg4I_iY6oY0AlZFKRiPuD5hmL3IbqqmjmUPkNaqoJzCNe2EwOIAUoCHKZJ2AXojaSJbFHtwc4UyhkjRy032Df6_0=)
13. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG-EE6saP53MB9IHD-t6o5lrePJ00jnPOLZu8ZjUcGmdRzX_iQMD1Xq6pHnCVF7hJJt1kbsanOS4ZFaFMNhhW_aaU4wv5dYKwhWtCnXwb0ZcS4KDbY4ZSHQohvY2M666_MqzuCddstPvzDY1SypgdrgCfze0Hj7G9XEApVRJ6-snKH4bFfNJOCTb78X4neDaU7Nflb_KL7hGI-iEU98Grs=)
14. [pymc-marketing.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaES_B2-HVW9ISI_qNadBBmyuwnH6MgDtBicWBqIpSYWj2W0oLRM0Dzoi0X-uxO-rPpQUzgf0JwG5nTe8BTDwLY3hiP19JxuM2_A5hBTz3MMmT5SU1MCTFg84qgtLHUJ1Q1RDkH-5ooke50YeyyLBFzHCHbsdOJTYsV4zbMpqHsB6uSHhf7S07WNWI6zeYvcA=)
15. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGHFoH_uVNT7QUzLxTFkXOwEfeSN-DvwdXv2_SEL_ELNqpOmfqK3vXbrhX4odxi-RzviDW9xLUdokM5ftpbEzv_RZy6vK2WNF9zrhJsHlaQUU-HWOEuJnSdgFAi)
16. [brown.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGK6tRo4bGsy_r3ocaVzWiYWnKGgrKbHLMqP7k7Ti9SBhEs6zliuEQYQKUgNue0HmP4S4pO7vK7GmM8x34RwWRy2BLXGoQEjBD6NRViFrRcwyJWyHz8KR78KlpeecDZ6J7HXx85)


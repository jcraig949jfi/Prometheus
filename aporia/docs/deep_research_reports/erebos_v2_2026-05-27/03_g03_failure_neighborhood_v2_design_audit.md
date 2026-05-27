# Prompt 03: G03 Failure-Neighborhood — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chdnb0VXYXFqUkxkX0tqTWNQcEpuQjRRTRIXZ29FV2FxalJMZF9Lak1jUHBKbkI0UU0
**Elapsed:** 273s

---

# An Expert Analysis of Arithmetic Comparison Ladders, Predicate Weakening-Strengthening Operations, and Asymptotic Calculus in Automated Theorem Discovery

**Abstract and Leading Paragraph**

*   **The Current Bottleneck:** The G03 failure-neighborhood loader currently utilizes a rigid, hardcoded, single-step comparison-operator weakening ladder. This heuristic rigidity frequently leads to misclassifications, such as falsely rejecting hypotheses in sparse catalogs (e.g., yielding a `weakening_too_strict` error for Mahler measure boundaries).
*   **Alternative Taxonomies:** Implementing structural ladders derived from Continuous Model Theory (Metric Logic), Modal Interval Analysis, and Proof-Theoretic Uniform Boundedness provides a far more nuanced, multidimensional gradient for evaluating logical predicates compared to strictly syntactic arithmetic relaxation.
*   **Data-Driven Calibration:** The static $\epsilon = 0.05$ threshold is a mathematically arbitrary heuristic. Best practices mandate a dynamic, data-driven calibration tied to the natural density and gap distributions of the specific mathematical catalog in question (such as the Dobrowolski bound decay curve for Lehmer's problem).
*   **Multi-Step Survival Curves:** Transitioning from a one-step evaluation to a multi-step (v2) weakening process generates a "predicate survival curve." The topological shape of this curve acts as a diagnostic fingerprint, distinguishing brittle boundary artifacts from robust, deeply rooted asymptotic truths.
*   **Formal Proof Mining Analogs:** Recent formal verification advancements (2024-2026), particularly the application of Kohlenbach's uniform boundedness to probability theory and structurally aware LLM tactic mining, offer syntactic analogs to Erebos's empirical, substrate-grade semantic weakening. 
*   **The Case for Strengthening:** In mathematically delicate scenarios—such as p-adic equidistribution constraints or disjunctive non-convex interval analysis—weakening is the fundamentally incorrect logical maneuver. Such claims must be aggressively routed to a strengthening operator (G13) to avoid spurious domain collapse.

The automated evaluation of mathematical claims via algorithmic modification of logical predicates lies at the frontier of machine-assisted theorem discovery. In systems like Erebos, the G03 failure-neighborhood loader is tasked with analyzing a rejected claim possessing a detectable arithmetic comparison operator and weakening it down a predefined logical ladder. The expectation is that if a weakened claim becomes overly permissive, a `boundary_collapse` occurs, indicating the original claim was trivially tight. However, empirical LIVE FINDINGS demonstrate that static heuristics (such as an $\epsilon = 0.05$ band resulting in a trivial fraction of 0.0065) trigger false negative rejections (`weakening_too_strict`). This report provides an exhaustive, expert-level academic review of alternative comparison-operator weakening ladders, statistical calibration of $\epsilon$-bands, multi-step survival curve analytics, contemporary proof-mining analogues, and contrarian strengthening protocols. 

## 1. The Taxonomy of Comparison-Operator Weakening Ladders

The current v1 loader relies on a hardcoded syntactical descent: `arith_equality` $\to$ `arith_strict_inequality` $\to$ `arith_nonstrict_inequality` $\to$ `arith_bounded` $\to$ `arith_asymptotic`. While functionally adequate for basic algebraic inequalities, this ladder suffers from semantic blindness. It treats all numbers as classical Dedekind reals and all inequalities as crisp Boolean boundaries. We survey three published taxonomies of comparison-operator weakening from higher logic, interval analysis, and proof theory, identifying exactly what the current ladder fundamentally misses.

### 1.1 Alternative 1: The Continuous Model Theory (Metric Logic) Ladder

In classical first-order logic, the truth value of a predicate is either 0 (False) or 1 (True). However, when dealing with analytic structures, Banach spaces, or probability measure algebras, Boolean logic collapses under the weight of topological proximity [cite: 1, 2]. Continuous model theory, grounded in first-order Łukasiewicz logic, replaces discrete truth values with a continuous spectrum mapped to the compact interval $[cite: 3]$ [cite: 2]. 

In this framework, the universe of a structure is a complete metric space, and equality is replaced by the metric distance $d(x, y)$ [cite: 4]. Predicates are uniformly continuous functions [cite: 1]. The weakening ladder in metric logic operates not by shifting algebraic operators, but by expanding the modulus of continuity:

1.  **Crisp Equality (Zero Distance):** The truth value evaluates exactly to 0.
2.  **Metric Proximity (Distance $\le \epsilon$):** The truth value evaluates to $\le \epsilon$, capturing statements that are "true up to a perturbation" [cite: 1, 5].
3.  **Lipschitz Continuity Satisfaction:** The predicate is weakened to a uniformly continuous function governed by a modulus of continuity $\gamma$ [cite: 1].
4.  **Categorical Approximation:** The claim is weakened from a specific metric structure to a broader class, such as an $\omega$-categorical or guarded Fraïssé Banach space [cite: 1].

**What the v1 Ladder Misses:** The hardcoded v1 ladder misses the concept of *topological continuity*. By viewing strict vs. non-strict inequalities as the primary axis of weakening, it fails to capture uniform convergence and Lipschitz bounds. The continuous logic ladder captures the idea that two models might be "isomorphic up to perturbations," a crucial concept when searching for theorems in functional analysis or operator algebras [cite: 1].

### 1.2 Alternative 2: The Interval Analysis and Modal Ladder

In numeric planning, global optimization, and robust computer algebra systems, exact numeric states are often undecidable or highly non-linear. Interval arithmetic bounds uncertainties by replacing real numbers with intervals. However, standard interval analysis suffers from a lack of algebraic group properties (e.g., lattice operations are not closed with respect to inclusion) [cite: 6].

To combat this, the weakening of comparison operators is structured via a specific ladder of interval relaxations:

1.  **Pointwise Evaluation (Degenerate Interval):** The variable is a crisp value $[x, x]$ [cite: 7].
2.  **Closed Interval Relaxation:** The comparison $x \le y$ is weakened such that there exists $q_1 \in [x_{min}, x_{max}]$ and $q_2 \in [y_{min}, y_{max}]$ where $q_1 \le q_2$. This means two intervals can simultaneously be "greater" and "less" than each other [cite: 7, 8].
3.  **Mixed-Bounded Interval Relaxation:** Boundaries are softened to include combinations of open and closed bounds (e.g., $(x, y]$) to capture asymptotic limit behavior of continuous effects [cite: 8].
4.  **Modal Interval / Dual Operator Weakening:** Classical intervals fail at logical disjunction and equation solving ($A + X = B$). Modal intervals extend the real line to include dual intervals, utilizing semantic quantifiers (universal and existential) embedded directly within the interval bounds. The comparison operators $\le$ and $\ge$ are upgraded to modal inclusion relations [cite: 6].

**What the v1 Ladder Misses:** The v1 ladder cannot express *state-space uncertainty* or *disjunctive validity*. In non-linear systems, a single step down to "bounded" fails to account for bifurcations in the proof space. Modal intervals capture the simultaneous existence of multiple valid sub-states, a critical factor when dealing with catalog entries that exhibit phase-change properties.

### 1.3 Alternative 3: The Proof-Theoretic Uniform Boundedness Ladder

Developed extensively by the Kohlenbach school of applied proof theory (proof mining), this ladder evaluates the *computational content* and *parameter dependency* of a bound [cite: 9, 10, 11]. When analyzing an ineffective existence proof, the goal is to extract a quantitative bound. 

The weakening of a bounding operator here is not about arithmetic syntax, but about logical quantification:

1.  **Exact Computable Realizer:** A highly specific, parameter-dependent exact equality.
2.  **Parameter-Dependent Bound:** An inequality $f(x) \le \Phi(x, y, z)$ where the bound depends intricately on the exact local geometry of the metric space [cite: 12].
3.  **Uniform Bound (via Majorizability):** By applying Kohlenbach's principle of uniform boundedness, the bound is drastically weakened (yet made far more useful) by removing its dependency on specific parameters. The bound $\Phi^*$ becomes highly uniform, relying only on global topological constants [cite: 12, 13].
4.  **Tame Asymptotic Bound:** Further weakening removes complex measure-theoretic properties (such as $\sigma$-additivity) yielding a tame, primitive recursive bound valid even over finitely additive probability spaces [cite: 12].

**What the v1 Ladder Misses:** The current ladder has no concept of *parameter independence*. It simply checks if a bound exists. The proof-theoretic ladder measures *how universal* the bound is, which is the truest measure of a theorem's depth.

## 2. Epsilon-Band Calibration and the Mahler Measure Natural Density Scale

The v1 loader utilizes a hardcoded heuristic: `trivial_fraction ≥ 0.95 → boundary_collapse` over an epsilon-band of $[M_{Lehmer} \pm 0.05]$. The live finding notes that a fraction of $0.0065$ resulted in a `weakening_too_strict` rejection. To understand this failure, we must deeply analyze the mathematical substrate of Lehmer's problem and construct a data-driven calibration methodology.

### 2.1 The Legacy Heuristic: Why $\epsilon = 0.05$?

The Mahler measure of a non-zero polynomial $P(x) = a_0(x - \alpha_1) \cdots (x - \alpha_d)$ with integer coefficients is defined as $M(P) = |a_0| \prod_{i=1}^d \max(1, |\alpha_i|)$ [cite: 14, 15]. Equivalently, by Jensen's formula, it is the exponential of the integral of the log of the polynomial over the unit circle: $M(P) = \exp \left( \int_0^1 \log |P(e^{2\pi i t})| dt \right)$ [cite: 15, 16]. 

A classical theorem of Kronecker states that if $P$ is a monic irreducible polynomial with integer coefficients, $M(P) = 1$ if and only if $P(x) = x$ or $P$ is a cyclotomic polynomial (its roots are roots of unity) [cite: 3, 15, 17]. In 1933, D.H. Lehmer asked whether there exists a constant $\mu > 1$ such that for all non-cyclotomic integer polynomials, $M(P) \ge \mu$ [cite: 14, 15]. Lehmer himself found the polynomial $L(x) = x^{10} + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1$, which has a Mahler measure of $M(L) \approx 1.17628$ [cite: 3, 15].

The value $\epsilon = 0.05$ was almost certainly chosen as an arbitrary, visually appealing fraction of the "Lehmer gap." The gap between the trivial bound (1.0) and Lehmer's record is roughly $0.176$. An epsilon of $0.05$ represents approximately $28\%$ of this fundamental gap. By searching the band $[1.176 \pm 0.05]$, the system is looking for a cluster of polynomials slightly below or above the known minimum. 

However, this static band completely ignores the natural density of algebraic integers. The distribution of Mahler measures is not uniform; it becomes exponentially sparse near $1.0$ and highly dense at higher values. Thus, a fixed $\epsilon$ will trigger `weakening_too_strict` in sparse regions (yielding a trivial fraction of 0.0065) while triggering `boundary_collapse` in dense regions.

### 2.2 Data-Driven Calibration: The Dobrowolski Bound and Gap Distributions

A rigorous, data-driven $\epsilon$ must be dynamically tied to the catalog's natural density scale. For Lehmer's problem, the optimal scaling metric is the Dobrowolski bound. In 1979, Dobrowolski proved that for an irreducible polynomial of degree $d \ge 2$, either $M(P) = 1$ or $M(P) > 1 + c \left( \frac{\log \log d}{\log d} \right)^3$ for an absolute constant $c > 0$ [cite: 3, 15]. This bound falls short of proving Lehmer's conjecture by only a logarithmic factor [cite: 3].

Because the theoretical minimum of the Mahler measure decays as a function of the degree $d$, a static $\epsilon$ is mathematically illiterate. The $\epsilon$-band must be defined locally as a function of the polynomial degree and the variance of the local catalog density.

**Proposed Published Methodology:** 
The calibration of $\epsilon$ should follow the p-adic equidistribution and logarithmic Weil height asymptotics proposed by Dixit and Kala (2025) [cite: 17, 18]. The logarithmic Weil height is $h(\alpha) = \frac{\log M(\alpha)}{d}$ [cite: 17, 18]. Dixit and Kala establish that the height $h(\alpha)$ can be bounded in terms of the number of conjugates that lie in a finite extension of the local field $\mathbb{Q}_p$ [cite: 17, 18]. They prove that Lehmer's conjecture holds for all $\alpha$ such that $\gg \sqrt{d \log d}$ many of its conjugates lie in a finite extension of $\mathbb{Q}_p$ [cite: 17, 18]. 

Therefore, the catalog's natural density scale operates on the order of $\mathcal{O}(\sqrt{d \log d})$. 

### 2.3 Methodological Implementation for Catalog Density

To calibrate $\epsilon$ dynamically:
1.  **Calculate the Local $1-\sigma$ Distribution:** Group the Mossinghoff catalog (or the general database of algebraic integers) into strata based on polynomial degree $d$ and Galois group signatures.
2.  **Determine the Median Gap:** For each stratum, compute the median arithmetic gap between consecutive Mahler measures $\Delta M_{median}$.
3.  **Apply the Asymptotic Scaling Factor:** Define $\epsilon = k \cdot \Delta M_{median}$, where $k$ is calibrated such that the expected baseline trivial fraction is exactly 0.5 (the median). This ensures the epsilon band always captures exactly one standard deviation of local neighbor claims, regardless of whether the predicate is operating in the dense regions of large Mahler measures or the sparse frontier near Lehmer's record.

## 3. Multi-Step Weakening and Predicate Survival Curves

The current G03 loader evaluates a predicate by walking **ONE step** down the ladder. This binary pass/fail mechanism strips away the topological context of the claim. A theorem that becomes trivial after one step of weakening is fundamentally different from a theorem that survives three levels of rigorous relaxation before yielding to triviality.

We propose a v2 architecture that iterates through $N$ steps of a continuous/discrete ladder, recording the `trivial_fraction` at each depth. This generates a **Predicate Survival Curve**.

### 3.1 The Architecture of the N-Step Walk

Assume a predicate comparing two mathematical expressions, $f(x) \circ g(x)$. The multi-step walk systematically relaxes the operator $\circ$:

*   **Depth 0 (Strict Equality):** $f(x) = g(x)$
*   **Depth 1 (Metric/Epsilon Proximity):** $|f(x) - g(x)| \le \epsilon(x)$, where $\epsilon(x)$ is the dynamically calibrated data-driven bound.
*   **Depth 2 (Absolute Bounding):** $f(x) \le g(x) + C$ for some uniform constant $C$.
*   **Depth 3 (Linear Asymptotic / Big-O):** $f(x) \le C \cdot g(x)$ (i.e., $f(x) = \mathcal{O}(g(x))$).
*   **Depth 4 (Logarithmic / Equivalent Asymptotic):** $\log f(x) \sim \log g(x)$ or $f(x) \le C \cdot g(x)^{1+\delta}$.

At each Depth $D_i$, the system queries the mathematical catalog and calculates the survival fraction $S(D_i) = 1 - \text{trivial\_fraction}(D_i)$. 

### 3.2 Survival Curve Construction and Hazard Functions

The survival curve maps Depth $D_i$ on the x-axis to the Survival Fraction $S(D_i)$ on the y-axis. From this, we can compute the discrete hazard function $h(D_i)$, which represents the conditional probability that a predicate becomes trivially true at depth $D_i$, given that it survived up to depth $D_{i-1}$.

### 3.3 Interpreting the Survival Curve Typology

The geometric shape of this curve provides profound insights into the underlying nature of the mathematical claim:

1.  **The Brittle Boundary (Step-Function Collapse):** If $S(D_0) = 0.01$ and $S(D_1) = 0.99$ (a massive drop in survival), the predicate is highly brittle. The curve's shape tells us that the original claim was likely a numerical artifact or an over-fitted boundary condition. The moment it was given $\epsilon$-breathing room, it became universally trivial. Expected action: **REJECT (Boundary Collapse)**.
2.  **The Robust Asymptotic (Long Tail Decay):** If the curve decays slowly—surviving $\epsilon$-proximity, surviving absolute bounding, and only collapsing at Depth 4 (Logarithmic Asymptotic)—the curve's shape indicates a deep, structural truth. The exact equality may have failed, but the structural relationship between $f(x)$ and $g(x)$ is profoundly robust. Expected action: **PROMOTE (Asymptotically Significant)**.
3.  **The Phase Transition (Mid-Ladder Cliff):** If the curve remains flat through Depths 0, 1, and 2, but collapses entirely at Depth 3, it tells us the predicate is strictly bound by additive constants but lacks multiplicative invariant properties. This signals the need for dimensional analysis of the predicate's variables.

## 4. Proof-Mining Analogs in Formal Logic (2024-2026)

The methodology of G03—taking an overly strict or non-effective claim and extracting a weakened, bounded version—is not merely a heuristic search algorithm; it is an empirical reflection of **Proof Mining**, a specialized branch of applied proof theory developed by Ulrich Kohlenbach. Proof mining extracts hidden finitary, combinatorial content (such as algorithms and effective bounds) from proofs that utilize highly infinitary principles [cite: 9, 10, 11]. 

We examine two cutting-edge proof-mining systems and frameworks published between 2024 and 2026 that perform operator-weakening for quantitative bound extraction, and compare them to Erebos.

### 4.1 Proof Mining in Probability Theory: The Kohlenbach School (Neri & Pischke, 2024-2026)

Historically, proof mining was restricted to Polish metric spaces and separable structures [cite: 13]. In a major 2024-2026 advancement, Neri, Pischke, and Oliva extended proof mining to probability theory and stochastic optimization [cite: 12, 19, 20, 21]. 

Their system utilizes a formal representation of the outer measure to define translations that allow for the systematic formalization of probabilistic statements [cite: 12, 19]. The core operator-weakening mechanism relies on Kohlenbach's monotone variant of Gödel's functional interpretation, coupled with a set-theoretically false principle of **uniform boundedness** [cite: 12, 13, 22]. 

When extracting a bound for a probabilistic existence statement, a rigid adherence to classical $\sigma$-additivity (countable additivity of measure spaces) forces the extracted bounds to be computationally explosive or infinitely dependent on the specific geometry of the underlying probability space. Neri and Pischke's metatheorems logically *weaken* the structural requirement of the space—from $\sigma$-additivity down to finite additivity (probability contents rather than measures) [cite: 12, 13, 19, 20]. By utilizing Kohlenbach's uniform boundedness, they replicate the logically strong continuity properties of probability measures in a "tame way," extracting effective bounds that are highly uniform and entirely independent of the parameters of the underlying probability space [cite: 12, 13, 22].

### 4.2 Structural Imitation and Tactic Mining: PROMISE (Ahn et al., 2026)

In the realm of interactive theorem provers (ITPs) like Lean 4 and Coq/Rocq, automated proof generation frequently fails because systems attempt to map surface-level textual similarities [cite: 23, 24]. In April 2026, Ahn et al. introduced **PROMISE (PROof MIning via Structural Embeddings)**, a structure-aware proof mining framework [cite: 23, 24, 25].

Instead of retrieving premises based on string matching, PROMISE treats proof generation as a stateful search process. It "mines structural similarity over proof states and tactic-transition traces" [cite: 23, 24]. In the context of bound extraction and operator weakening, PROMISE observes how goals and assumptions evolve during derivations. If a strict equality goal cannot be discharged, PROMISE mines the tactic-dependence graphs of existing proofs to find structural templates where the tactic sequence applied a weakening operation (e.g., transitioning from a strict evaluation to an asymptotic approximation) [cite: 23].

### 4.3 Automated Asymptotic Bound Extraction: Tao's 2025 Framework

In May 2025, Terence Tao proposed and demonstrated a proof-of-concept tool to automatically verify and extract asymptotic estimates [cite: 26]. Designed to integrate with formal proof assistant languages like Lean, the tool parses complex expressions and applies a database of inequalities (such as Hölder's and Sobolev's) [cite: 26]. The tool explicitly performs operator-weakening by relaxing exact equalities into asymptotic bounding notation ($X \lesssim Y$). It inspects the atomic steps of the proof, tracks the "implied constants" $C_{X,Y}$ across multiplied hypotheses, and optimizes the extracted bounds via linear programming [cite: 26]. This is a direct formalization of transitioning down the asymptotic ladder.

### 4.4 Erebos's Substrate-Grade Version: Additions and Omissions

**What Erebos Adds:** 
Formal proof-mining systems (like Neri & Pischke's metatheorems or Lean tactics) require a fully formalized syntactic proof to operate upon [cite: 12, 23]. Erebos operates on a semantic, substrate-grade level. It does not need the *proof*; it checks the *claim* against massive empirical catalogs (like Mossinghoff's polynomial database). Erebos achieves empirical falsification at scale, uncovering asymptotic truths via brute-force topological modeling of the data rather than via Gödelian functional translations.

**What Erebos Misses:**
Erebos severely lacks the absolute formal guarantees of proof theory. When Neri and Pischke weaken a premise via uniform boundedness, their logical metatheorems *guarantee* that the resulting quantitative bound is computationally tame and universally valid across all relevant spaces [cite: 12, 13]. Erebos's empirical weakening is susceptible to finite-catalog bias; a bound might appear robust over $10^6$ entries but fail spectacularly at infinity, lacking the rigorous safety of Dialectica interpretation [cite: 13, 20]. Furthermore, systems like PROMISE capture the *structural dynamics* of the proof state [cite: 23], a meta-logical insight that Erebos's purely arithmetic ladders cannot access.

## 5. Architecture of the G03 v2 Loader

To synthesize the advancements in continuous model theory, data-driven calibration, and multi-step analytics, we outline the exact specifications for the G03 v2 loader.

### 5.1 (a) Data-Driven Epsilon Calibration Module

Epsilon must no longer be static. It must be computed via a local density kernel applied to the specific catalog being queried.

**Algorithm:**
```python
def compute_dynamic_epsilon(catalog, predicate_domain, target_claim):
    # 1. Isolate the local topological neighborhood of the claim
    neighborhood = catalog.filter_by_domain(predicate_domain)
    
    # 2. Extract natural scaling factor (e.g., Dobrowolski curve for polynomials)
    if predicate_domain == 'Mahler_Measure':
        degree_d = target_claim.get_max_degree()
        scaling_factor = (math.log(math.log(degree_d)) / math.log(degree_d)) ** 3
    else:
        # Generic 1-sigma standard deviation of consecutive gaps
        gaps = calculate_consecutive_gaps(neighborhood)
        scaling_factor = statistics.stdev(gaps)
        
    # 3. Calibrate to ensure baseline trivial fraction median
    epsilon = 0.5 * scaling_factor
    return epsilon
```

### 5.2 (b) Multi-Step Weakening Curve Generator

The v2 loader does not stop after one step. It recursively yields weakened predicates, evaluating the catalog at each depth to generate the survival curve.

```python
def generate_survival_curve(target_claim, ladder, catalog, epsilon):
    curve = []
    current_claim = target_claim
    
    for depth, operation in enumerate(ladder):
        weakened_claim = apply_weakening(current_claim, operation, epsilon)
        trivial_fraction = evaluate_against_catalog(weakened_claim, catalog)
        
        curve.append({
            'depth': depth,
            'operation': operation.name,
            'trivial_fraction': trivial_fraction,
            'survival_rate': 1.0 - trivial_fraction
        })
        current_claim = weakened_claim
        
    return calculate_auc_and_hazard(curve)
```

### 5.3 (c) Per-Domain Ladder Selection

The ladder used must be domain-aware. Applying an arithmetic Big-O relaxation to a topological clustering problem is illogical.

*   **Mahler / Algebraic Number Context:** Utilize the **Proof-Theoretic Uniformity Ladder**. Move from Exact Roots $\to$ Bounded Height $\to$ p-adic Local Field Asymptotics. The focus is on parameter dependency and asymptotic bounds linked to polynomial degree.
*   **Birch and Swinnerton-Dyer (BSD) / Analytic Context:** Utilize the **Continuous Model Theory Ladder**. Move from Exact Rank Equality $\to$ L-function Metric Proximity $\to$ Modulus of Continuity. Analytic L-functions require limits and topological $\epsilon$-neighborhoods, not discrete step functions.
*   **Diophantine Optimization Context:** Utilize the **Modal Interval Ladder**. Shift from Pointwise Equivalence $\to$ Mixed-Bounded Intervals $\to$ Modal Dual Intervals to capture disjunctive state spaces.

### 5.4 Concrete Decision Rules

The decision engine transitions from static thresholds to curve-shape heuristics:

*   **Rule 1: Immediate Boundary Collapse.** If the Hazard Function $h(D_1) > 0.85$ (meaning 85% of the survival capability is lost in the first epsilon-weakening step), the claim is a numeric artifact. $\to$ **REJECT: boundary_collapse**.
*   **Rule 2: Hyper-Rigid Strictness.** If $S(D_3) > 0.98$ (the claim remains almost entirely un-trivial even after deep asymptotic weakening), the catalog is too sparse, or the weakening operations are not touching the relevant constraints. $\to$ **FLAG for Manual Review / Substrate Error**.
*   **Rule 3: Robust Asymptotic Promotion.** If $S(D_1)$ remains high ($> 0.8$), $S(D_2)$ shows gradual decay, and the curve only collapses $h(D_4) > 0.9$ at the maximal asymptotic depth, the predicate captures a fundamental structural truth that transcends immediate parameter values. $\to$ **PROMOTE: robust_asymptotic_core**.

## 6. Contrarian Perspectives: When Weakening is the Wrong Move

The fundamental assumption of the G03 loader is that if a predicate fails, it was *too strict*, and the logical countermeasure is to *weaken* it to find a broader truth. This assumption is systematically false in several advanced mathematical substrates. In these cases, the predicate failed not because it was too strict, but because it lacked specific topological or structural constraints. The correct move is **STRENGTHENING** the predicate (the purview of the G13 loader). If G03 weakly relaxes these claims, it will trigger catastrophic spurious inclusions.

Here are three substrate cases where G03 wrongly applies, requiring routing to G13:

### 6.1 Substrate Case 1: P-adic Equidistribution and Local Field Conjugate Bounds

Consider a claim attempting to bound the logarithmic Weil height $h(\alpha)$ of an algebraic number globally. A rejected claim might suggest that $h(\alpha) > C$ for some arbitrary constant. G03 would attempt to weaken this by dropping the constant or moving to an asymptotic bound. 

**Why Weakening is Wrong:** As demonstrated by Dixit and Kala (2025) [cite: 17, 18], bounding heights globally misses the profound localized behavior of Galois conjugates. When $h(\alpha)$ is small, conjugates are clustered near the unit circle in the complex plane [cite: 17, 18]. The profound mathematical truth lies in the **p-adic analogue** [cite: 17, 18]. 

Instead of weakening the global bound, the predicate must be *strengthened* by imposing a local field constraint: requiring that $\gg \sqrt{d \log d}$ many of the conjugates lie in a finite extension of $\mathbb{Q}_p$ for some prime $p$ [cite: 17, 18]. Weakening the arithmetic operator ignores the topology; strengthening the spatial restriction yields the proof for Lehmer's conjecture over that class [cite: 17].

### 6.2 Substrate Case 2: Disjunctive Interval Analysis and Spurious Relaxations

In numeric planning, finding solutions to non-linear equations $f(x) = 0$ requires bounding regions of the state space [cite: 27]. If an algorithm fails to locate a root, G03 might suggest relaxing the comparison to $f(x) \in [-\epsilon, \epsilon]$. 

**Why Weakening is Wrong:** In interval analysis, convex relaxations (weakening) inherently suffer from the "dependency problem." By expanding a weak interval extension, the relaxation introduces massive swaths of state space that are entirely spurious, leading to weak lower bounding problems and failure to exclude non-roots [cite: 27].

Instead of expanding the interval (weakening), the predicate must be *strengthened* using **Disjunctive Interval Analysis** via Range Decision Diagrams (RDDs) [cite: 28]. By splitting the domain into highly specific, non-contiguous intervals (adding disjunctive logical constraints), we eliminate spurious states while maintaining "All-paths interval consistency" [cite: 28]. Weakening creates a fog of false positives; strengthening via logical disjunction precisely targets the root.

### 6.3 Substrate Case 3: Measure-Theoretic $\sigma$-Additivity and Tame Continuous Bounds

Suppose a claim regarding the convergence of a sequence of random variables (e.g., a Baum-Katz type result for the Strong Law of Large Numbers [cite: 29]) fails because the variables do not perfectly conform to a strict probability measure. G03 would attempt to weaken the rate of convergence (e.g., from polynomial bounds to logarithmic bounds).

**Why Weakening is Wrong:** The failure might not reside in the rate of convergence, but in the adherence to strict classical $\sigma$-additivity [cite: 12]. As shown by Neri and Pischke (2026), attempting to brute-force a bound under classical measure theory leads to computational explosion [cite: 12, 19]. 

The solution is not to weaken the arithmetic convergence bound, but to *strengthen* the foundational model-theoretic premise to a **guarded Fraïssé Banach space** [cite: 1] or to utilize Kohlenbach's uniform boundedness to extract a bound over finitely additive probability spaces (probability contents) [cite: 12, 20]. In continuous logic, classical model-theoretic characterizations (like uncountably categorical theories) fail to maintain structure [cite: 1, 2]. Strengthening the structural definition of the space allows the original, tight convergence bound to remain perfectly valid [cite: 12, 29].

### 6.4 Routing Claims to the G13 Strengthening Module

To prevent G03 from applying spurious weakenings to these cases, a pre-processing classifier must be implemented:
*   If the predicate operates over Galois conjugates, Diophantine geometries, or Berkovich spaces [cite: 17], immediately suspend G03 and route to G13 for **p-adic/topological strengthening**.
*   If the predicate involves non-linear multivariate optimization where the Jacobian contains cyclic dependencies [cite: 8, 27], route to G13 to apply **RDD disjunctive interval splitting** [cite: 28].
*   If the predicate is evaluating measure-theoretic convergence rates [cite: 29], route to G13 for **structural model strengthening** (e.g., transitioning from Polish spaces to general probability contents) prior to evaluating the convergence inequality [cite: 12, 20].

## Conclusion

The evolution of automated theorem discovery necessitates the abandonment of crude, single-dimensional syntactical heuristics. By integrating continuous model theory, multi-step survival analytics, and data-driven epsilon calibrations grounded in phenomena like the Dobrowolski bound, Erebos can transcend simple boundary-pushing. Furthermore, by understanding the formal analogues developed in 2024-2026 within the proof mining and LLM tactic-generation communities, empirical systems can begin to replicate the profound uniformity and parameter independence formally guaranteed by higher proof theory. Ultimately, recognizing when a claim requires structural strengthening rather than arithmetic weakening remains the hallmark of true mathematical intelligence.

**Sources:**
1. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhQl_YanBJ-VjKKtocvDA6i0C3DdzrwB33x2VlbCKZA6rpM22u_Rwg7y9sIFaTB6l-BGe3Bz6V6ak97PXuODBZbNDgTeV_HpqrhooElEkHBhvrPUzU6rXoiVVa9QHOQeGSYixLtGAXvuQy-XkxxmIqEngCtXAQnvqcm0BJRboKkeBicVe9l3JFl2ji)
2. [siu.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFxhaYTrWq293VBv4AKnSqBuigWpZLIc8TtwcJCFhuqOsB-1BRwtCLE6latVEGUi6l_S9rTyAQU4sKg1Psle7rmAdKLX4jmCK1qbbd8EWnfh8aUGBnnCd8yLT_d7m6pNvSBOAj6TLi7zoDiFM3IuWxt8k=)
3. [uni-goettingen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFl4kgMA4K6LsPTW_1PvQchi3oi4RwwQPd5dh7QrXVYXrbuTeAeIZwzOCNb-fQ5FAHxcFO4Q4Eis-KBYUutOQ_m8l-43qV0smWuZOvgOkikNfEwMcjJPyErM5yUQULYJqGVX-dKk332qoKMXRi8fIeKH9thNuxIjFgNjv7PDw1FkbRFRE77pHV3pgvoU-IjmZ8rlIy2z6XgVsYGWkdkCE3uevUdQAvB)
4. [uic.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqEQx3oU2gh62Z42M7sJ8-BG9-HMoAkOurDcF3Hkykh5JLpIlg-GqIdB8jLtJcJRvbsBKzSWfUGlnyp7EdMRrR7EksqEcR-KX92kEjKC20LnvC1VvD9IX7c2gwMpGv7ycOj79P2PA-bN-AdfNAnenvQnXzzbzRQPRMr6bl)
5. [stanford.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuiXw--CK-pPSYQ6cXiTuB5NaQmiei7jEzT5nadduXthgI3snPkd0kz6ImQKwFxGv8M-h27D6Umly2f5I0TmPwSZgLUeyJU9BK04NemhK7UzIDFPsoXA2Gm8U2zO9_KXgKrRIKDoKnB6bc)
6. [ieee.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcG1rkydTtZQOTZOpsLoy6365SkniX9M-rmqExGC4n2Si47vfUvvQU5XPYb6EPDPRS1LduqA7PINqjI8nRq35EDOUqast2FK666h8iKiolQfh_jT_VIl6uVo4zI4m-rciaz-2S-JwW4nHPW9PC7tKo--yif1wLqlUwJOmn9EP8)
7. [robert-mattmueller.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH80lcLhogL6SqBiU5qoQapTLHnumYLf13hYSoTkzyvRqekItcw5fOa5Wl4TnpAmLHteRkaeBpUVHSJQh7HhtEVwDHTbG-BtGDGQevP6WYVtIqfnmgOZCs55J7szpNUfvf6c3aEG4WC-oJS2EAWGKmJhjPGYEocsFC6_O9DtBTSKSdLAUXw1yc7Fbet)
8. [anu.edu.au](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF0rwBKIWbWK7kXtJGSxATknC09iz8Df1V7fCSepOd8ch5Shwh3ZnzwI6XsqgDtuc-4dBa1WvdFKREoetETOm0Yoh217M2tMTI2q69jYow9fPHWVAYz5h-TfzgHkhlOcTQAs33oOExIt1RokRCsosg=)
9. [ilds.ro](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZJrI3nmXgMgORGIGpwkPMur7bSo0ObyW5qn4Z_UVZiDQzwc0ywDz318V8EXaDd2HUl4JGQmGMJWJaJm9M5XVTmgQVYGj2LixtY4n0Mkte80HyBMudEHKhokwuY97jpr7jydjdSbDujmKsatkuchCs17l_5kHAo6GPUxtoJFygQpRC9VmDsQCoobjBSg==)
10. [ilds.ro](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFNwtTVXbGUCBUTnDTtjyMbzxl2ocsK5n0wWYKVbSq4sfWuyV9s4xswa8xoi3fFnwXKon61XABeA7xPpic-z4oyB7HK49nbS24FnVZiLxUBL1SNsPKVDfklmxI)
11. [uni-tuebingen.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGtT4XyexcKtKBXbLqM4bpLqcAN8AljpPl2OJaWmkNUw7dZwuJMY7WFCT-3AashZ4sdAybSsABSgP2Bo1If2Dbd6mxW1L25Gh-rk9jeacEuNrg3woJxF3Kft8xlII9IqrcOyUzRoBWpQaEUhXutdHFwFw5wGSjkWOAbVSI0or3jN6titYPIqDhJ7rYxammS9nD5todKVxELe9zlU8APIfIl3B0tZDBOGO_lxUcGlQlMtrNwusPKYijUJQCnLm7h1L25SgZcK3edCPcJAkMaMax0H7I767ua5-vF0iom5vzeMCSuBKbQT3CdMZGGSbUUA9zJZvj06pM-BRy3YOBm)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFh2gMZX_M1pO5rVYQxlJeb7McqTOmCRLQA8VfnRu5nB2Fd2gou1GPhuxzBszc9OsnP-KcLasKxoKD65LrWlBSS8I6P81NUSA9rMasKVS8lRk28PTSg3NVAZA==)
13. [cambridge.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcNN71Urn4JPtzpAHnXrJQTXTEBhVx23kxmXvT-eXLbSOMtXAGER9O6w5EDqLxkQs6ayF4WpgL0-PzeRd1mKsAt-1hGbYEN5Bcitdzd6ayvbfDGSmjcNlO0wXyoyHsk8oIemXWoEPqhhaWAbHlrKifS74pG2E04bSn2NOzDXzlLvJTnRfUFNbf440eh9FwyZdUDQndqabhayhvvTGQHdv-XLeTgXSwGM2Uh6PXOBVdhvr1rkgQ_k1nbuB8qRY7Zxk9h8bqAZI=)
14. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIGyYH5xQV_Rzjvwfw1MYMn_84aR5laR7F8P5PnfTkxea7QWhvvBVT1sgNDBGtYuFmuYBi9nQJZxFbXRhTzchwMzVMiEjz7qsg5xH5345EJkW0nXetY2cGAKFhWVJiSThYn5FqKV3Nyyc=)
15. [leidenuniv.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_P47rRLLBJssulfZIThYkMnWbBzTqG0CjoNgryb3FdUl-GdnOgUF9hti6aMrYIx6wlIfhPdaKORcRABHKQVwJPmE_W0qCUr3rgNlWC64vMRt56DRAcdjT9YuYrf_UGgMpyNpShXyKdVvd8GJL)
16. [mpg.de](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3DJfQEG_YdtwjKrLX7IMVqLju1XDtG7FnC-rnnhySOuVKmfSNC9nJxNH4sGwNX8YP_aeTMFLffMSj9lBMVEWh6CcL7RzeDgPn0o3X2gF_T_yiVJOv_ZUEiAsZhoA2QaFnBc0ZXdyByrbR-UsCmwm_rP0mViGiMtMs1N4MecfzHzMY)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzT1hWaTCI6E2uDGvaOtRExxiOmuoEAbrblMDAk-6gP4syn2f2kIuIIwNG_ABcEXwP8KeBYohS7MUYe-_SpvgendAbYlBvsV-ADkcclOgZMVN0L9L5kg==)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6awnguhvA-j5eZzZsrOuHNZDEnSXilo1Vuy8mW9hpqOzmINHycpQtLzDP3LMtnw1MvTL3kll1ARBqBKAzW-gfpi8jVWdjiPLvhUs7CEf_xS-0SS9ICw==)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH66xOfxCrdaKrM7aIjoY_RLo7zLCLGdRXJ8vvEcRwIY-xGV1bbORVZujVyFOZ3luy0HE8bO4fAZ8LDwENMUvKjj3IEa0fNZ94HZE4LsbSylTQWRXSmbg==)
20. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdB4e6QNbhBmbgWwkG87TGBo8NiObb3FXKs_v_L86CxPHUZ8CMnBWff6rwTXj-49IeGr4FQQrI5J_lrrDD4Md9j6cy9X_e9NRBibvHuCmWH5YfI5ii_cUyGy8EtpImHgY1J6owghoYNE8XIPH3x9VGdBxJqyIJDQkJPNg=)
21. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQPYbLXR4IjCAEpKOPf3A5BH-3RceeBm7AvpMRmb5DRgxdytT-4XmCtISknUcNlSYNaZEdIYcQQbsvQhn3TczDtP0vZ5WE2xy5wwKtsWmCqeCDCNKdCA==)
22. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwxc3IVMlLa_kmAwJVYzNexzkKX9iZU00nllSLxRZdeqnV_bQxc57o15ocqYTGzl7fyI6j0-X9K_eFbcS0ddtZS18v1cvTSLIOPcDKytz04GnGwnLiRnZxtJDwThcnWiaUDSr6iYtDFfCzXXS6anIOdBHj_davEgbhlCy7-9Iq4AJJ1RSMuS0=)
23. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHISKEvgMbjQWtKxSePWe5xgfDn1jte9S5i6BMaZYmbtJLYaWQ9VPyeQduskowPQJasVA4GX5dvuCMJt3d8v31BglosUHkFfcF7Tjrb_H9H5O6i8mQtwViubQ==)
24. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBUTkM8aD1qWmMxmRv4EMaiRJIZEPF0pGK_hhW1p9Z2fRpZCXKD5uwoV2HXOxc-6BkHDbbWHP8bql1ciXJ306Kg-HsXzuirF2PYha5-KUmqRcHF1F1TQ==)
25. [rndcircle.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqbDceEAtuQ9NuJq1g_x0DRqAialu2c9bSWjkGpqrfi0zIBNfKksUZ9GuqJuSceIvtfM9Z13A_gA26gBx6YbWHvlNRVkIxGw0V9-0ot0zr4nXTPcV-wyLHgd0dRchQxBxuwl2Dnf2F5Vgs1IvG7vUeiYlK0NHmQ_vi1a2-rS0=)
26. [wordpress.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgX9l-j1Mv6OUuV7NtziTcfr1Tbz7rNhUYIh9Q5pOnyU9yTMGFmvEOoNS3vy_18haqJMB8mxqu0Tz3AgFOwLK5AyYPYIFcDQ93MBbrfmY1ceZ9m33LvwIu4ewc-FJv7RqLjzYS1sU4bWoO4jo2FXPDIn2apSntPf_NoouCy0oMrSB6STbgwkH4yrT8WQ==)
27. [uconn.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgdeVdCijyd_qjxNNQE4NByIc2LQo-yKmzscYqNiiphRf3PbaesXu9S01TR6cKfdgBrNcjbv_l_vt0cbPO7IxDGeLNvF90VR1o5t2cUHuxo7h81JLEQ9RuYKRow0ibsojdU6eH3vp6JFzgpx9fPYpzIGo20T4_HA66CKDB7sfDw479Ym5nx7JDkUeI8yxjSlABWCHEDulyldZE8Q==)
28. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmSxuVdreSVxAIhf7h-gHxxryUHTTw1O2I9z4VnPDJ6XMxa3KILjCvf07_AKa8IeJZORR34VaI0USNjrrt3cY6Kz3c52Rg8_THkilKZwf6aZBneYmbf52dGSOAvgEQ6FzPqBTc-9ZsBIm3KbAE)
29. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEy2F3_8xhL6GIBeuJf1PQIZm5SLkFnPrp39diZ75wdE5_UFQmYv61dBpw45CzPd8etbwmoNy2PJDr9r6jD7M0bSFxgQAQrLC5xBYZeNjYftBApTZ1GJA==)


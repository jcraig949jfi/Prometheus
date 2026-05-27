# Prompt 14: G16 Anti-Anchor — v2 design audit

**Agent:** deep-research-pro-preview-12-2025
**Interaction ID:** v1_Chdnb1lXYXFQZEVNS045TW9QamVxSHVRMBIXZ29ZV2FxUGRFTUtOOU1vUGplcUh1UTA
**Elapsed:** 243s

---

# Advanced Methodologies in Adversarial Generation and Anti-Anchor Restrictions: A Comprehensive Review of the G16 Protocol

**Key Points**
*   The G16 ANTI-ANCHOR protocol evaluates the robustness of mathematical conjectures by aggressively pushing numeric parameters to adversarial extremes to test for survival, historically relying on a rigid $10\times$ multiplier.
*   Research suggests that naive scalar multipliers often force parameters into degenerate structural phases, potentially yielding false positives where conjectures survive merely because the adversarial band is trivial or artifactual.
*   Recent advancements (2024–2026) in Large Language Model (LLM) agent architectures—such as Co-FunSearch, CounterMath, and GraphMind—demonstrate that adversarial mathematical generation is shifting toward evolutionary program search and formal verification.
*   It seems likely that transitioning to data-driven, confound-stratified permutation nulls (v2 loader) will substantially reduce type-I errors in anchor validation by ensuring that adversarial subsamples retain the underlying topological and algebraic complexities of the base distribution. 
*   The integration of exploratory agents (e.g., Lethe) with strict numeric-extremum validation protocols (G16) establishes a robust, automated pipeline for systematically breaking or validating canonical examples in high-dimensional mathematical spaces.

**Overview of the Landscape**
The evaluation of formal mathematical statements, heuristics, and algorithmic bounds relies heavily on canonical anchors—examples or parameter sets that firmly ground a conjecture's validity. Adversarial testing of these anchors aims to break the "conjecture survives here" hypothesis. However, the exact mechanics of generating these adversarial examples have historically suffered from arbitrary scaling. New research indicates a paradigm shift toward structurally aware, phase-transition-informed adversarial generation.

**The Contrarian Dilemma**
A persistent controversy in adversarial mathematics is whether extreme parameter pushes validate an anchor's robustness or merely push the anchor into an empty, topologically collapsed regime where the conjecture is trivially true. Addressing this requires a highly controlled, confound-stratified environment that distinguishes genuine survival from structural artifacts.

---

## 1. Adversarial-Example Generation for Mathematical Objects (2024–2026)

The generation of adversarial counterexamples in pure and applied mathematics has transitioned from brute-force computational searches (such as the historical computation of Birch and Swinnerton-Dyer curves or early Lehmer searches) to highly sophisticated, agent-driven evolutionary algorithms and formal theorem-proving architectures. In the 2024–2026 window, the literature emphasizes the use of Large Language Models (LLMs) not just as heuristic guessers, but as programmable operators searching vast topological and structural spaces [cite: 1, 2]. 

The task of generating adversarial inputs for mathematical objects—such as Salem polynomials pushed to degree extremes or elliptic curves explored in sparse, low-conductor cells—requires tools that bridge abstract conceptualization and rigorous formal verification [cite: 3, 4]. Three preeminent systems have emerged to handle adversarial generation and counterexample discovery for mathematical objects.

### 1.1. Co-FunSearch (Collaborative FunSearch)
**Adversarial Generation Method:** Evolutionary Program Search and Interpolation  
**Primary Citations:** Nikoleit (2025) [cite: 2, 5]; Romera-Paredes et al. (2024) [cite: 1]

Co-FunSearch represents a paradigm shift in discovering adversarial lower bounds and counterexamples for combinatorial optimization and heuristic conjectures [cite: 2, 5]. Originating from the FunSearch architecture, which evolved short programs under an automated evaluator to discover new cap-set constructions and bin-packing heuristics [cite: 1, 6], Co-FunSearch integrates an island-based evolutionary algorithm with LLM-driven code variation [cite: 7]. 

To generate adversarial mathematical objects, Co-FunSearch does not manipulate numeric vectors directly (which local searches often fail at due to structural opacity). Instead, it searches the *program space* [cite: 2]. The LLM generates Python code that constructs the adversarial instance. The evaluator then runs the code, scores the output against the conjecture (e.g., maximizing the failure rate of a specific algorithm), and feeds the best-performing scripts back into the LLM for mutation [cite: 1, 5]. By searching for algorithmic generators rather than static instances, Co-FunSearch exploits the low Kolmogorov complexity inherent in deep optimization problems [cite: 2]. This approach successfully disproved the output-polynomial running time conjecture for the Nemhauser-Ullmann knapsack heuristic and generated novel adversarial instances for hierarchical clustering [cite: 2, 5].

### 1.2. CounterMath and Lean 4 Mutational Counterexample Generation
**Adversarial Generation Method:** Symbolic Mutation and Formal Verification Guiding LLM Guess-and-Check  
**Primary Citations:** Li et al. (2026) [cite: 8]; George et al. (2026) [cite: 4, 9]

The CounterMath framework tackles formal counterexample generation by addressing a core limitation of prior LLMs: the inability to guess edge cases and verify them logically [cite: 8]. Identifying adversarial examples in continuous or highly abstract mathematical spaces (e.g., Topology, Real Analysis) requires precise semantic boundaries.

CounterMath employs a "guess-and-check" paradigm formalized within the Lean 4 theorem prover [cite: 8]. Its adversarial generation method relies on a symbolic mutation strategy: it takes existing, provable theorems and systematically drops or mutates specific hypotheses [cite: 3, 8]. This creates a broken conjecture. The LLM is then prompted to generate a formal counterexample to this newly mutated, false conjecture [cite: 8]. Because the entire pipeline is grounded in Lean 4, the proposed adversarial mathematical object is automatically and rigorously checked for validity [cite: 8]. This system operates over formal mathematical representations (often augmented by frameworks like TorchLean, which bridges the semantic gap between numeric execution and abstract verification [cite: 4, 9]), ensuring that the generated adversarial extremum mathematically conforms to the required ambient space.

### 1.3. GraphMind (Optimist-Pessimist Dueling Agents)
**Adversarial Generation Method:** Mixed-Integer Programming (MIP) combined with Monte Carlo Tree Search (MCTS)  
**Primary Citations:** Davila (2024) [cite: 10, 11]

GraphMind is an autonomous system designed specifically for graph theory and discrete mathematics. It operates on a dual-agent framework consisting of an "Optimist" agent that proposes conjectures and a "Pessimist" agent that searches for adversarial counterexamples [cite: 10]. 

The Pessimist generates adversarial mathematical objects (counterexample graphs) by framing the conjecture's negation as an objective function in a Mixed-Integer Programming (MIP) environment [cite: 10]. For highly constrained structural searches where MIP scales poorly, the Pessimist falls back on Deep Reinforcement Learning combined with Monte Carlo Tree Search (MCTS) to incrementally build graph topologies that violate the proposed invariants [cite: 10]. By maintaining an adaptive knowledge base and employing heuristics (like the Hazel and Dalmatian heuristics) to filter out trivialities, the Pessimist agent continually pushes the boundaries of the Optimist's conjectures, forcing the generation of highly specific, sparse, or dense adversarial graphs [cite: 10, 11].

---

## 2. The Fallacy of the Naive $10\times$ Multiplier and Data-Driven Metrics

The G16 ANTI-ANCHOR protocol currently pushes a promoted anchor's numeric parameter to an adversarial extreme using a flat $10\times$ (or $0.1\times$) multiplier. While computationally simple, the $10\times$ multiplier is mathematically naive and analytically dangerous. 

### 2.1. Why is the $10\times$ Multiplier Flawed?
Mathematical objects rarely scale linearly in their structural properties. In complex dynamic systems, number theory, or graph topology, multiplying a parameter by 10 does not represent a uniform "increase in difficulty." Instead, it often projects the object out of the distribution of meaningful mathematical entities entirely. 

For instance, in the study of deep neural network topologies, pushing a parameter (such as sparsity or connectivity) beyond a certain threshold does not merely degrade performance; it causes a mathematical phase transition. Research by Pesce, He, and Caldarelli (2026) demonstrates that structural networks undergo a sharp, second-order critical transition from a cooperative, functional phase to a disordered phase when node degrees are pruned beyond a specific threshold [cite: 12, 13]. If a $10\times$ push places a parameter on the far side of a phase transition, the conjecture is no longer being tested on an "adversarial extreme" of the original class; it is being tested on a fundamentally different, degenerate state of matter [cite: 13].

Furthermore, distributions of mathematical invariants (e.g., the conductor of elliptic curves, the degree of polynomials) are frequently heavy-tailed. A $10\times$ push in a heavy-tailed distribution might still leave the parameter within the dense core of trivial examples, whereas a $10\times$ push in an exponentially decaying distribution might shoot the parameter into an empty mathematical void where no objects exist.

### 2.2. Data-Driven Adversarial-Distance Metrics
To replace the naive scalar multiplier, adversarial generation must rely on intrinsic, data-driven geometric and statistical metrics.

**A. Tail-Percentile-Based Distance**
Rather than applying an arbitrary scalar, the adversarial push should be mapped to the cumulative distribution function (CDF) of the cataloged mathematical objects. 
*   **Definition:** Push the anchor's parameter $x$ to $x_{adv}$ such that $x_{adv} = F^{-1}(0.99)$, where $F$ is the empirical CDF of the catalog distribution. 
*   **Justification:** This guarantees that the adversarial example represents the absolute extreme of *known, valid mathematical existence*. Pushing to the 99th percentile forces the testing framework to evaluate the conjecture in the most boundary-adjacent, yet strictly populated, regions of the parameter space. It normalizes the "push distance" regardless of whether the underlying distribution is Gaussian, log-normal, or Pareto.

**B. Structurally-Equivalent-Class-Based Distance**
In highly structured mathematical domains, continuous parameter pushes are meaningless. Instead, distance must be measured in terms of topological or algebraic equivalence classes.
*   **Definition:** Define a structural phase transition boundary $\partial \Phi$. An adversarial push maps the anchor $A \in C_i$ to an anchor $A_{adv} \in C_{i+1}$, where $C_{i+1}$ is the adjacent degenerate equivalence class (e.g., pushing a dense graph to the exact threshold of the percolation phase transition, but not beyond it).
*   **Justification:** Drawing on the phase-transition phenomena in complex networks [cite: 13], structurally-equivalent distances ensure that the "adversarial" nature of the object maximizes internal stress on the conjecture without changing the fundamental rules of the object's class. By moving to the boundary of the next degenerate class, we evaluate the conjecture at the critical point of symmetry breaking [cite: 12].

---

## 3. Permutation-Null Over Adversarial Band: Confound Stratification

The current ITER-19 refinement utilizes a simple permutation null over the adversarial band, pulling 500 random catalog subsamples of the SAME SIZE to establish statistical significance. However, this approach falls victim to Simpson's Paradox and profound confounding biases.

### 3.1. The Vulnerability of Unstratified Subsampling
When pushing an anchor to an adversarial band (e.g., extreme values of parameter $X$), it is overwhelmingly likely that other latent topological or algebraic parameters ($Y, Z$) will covary. If we test whether an anchor survives the adversarial band and compare its structural variance to a purely random subsample of the catalog, we are confounding the extreme nature of $X$ with the collateral extremes of $Y$ and $Z$. 

For example, if we study the adversarial robustness of a conjecture on graphs and look at extremely large graph orders ($N$), the random subsample of graphs with the same $N$ might be dominated by sparse trees, while our anchor is a dense bipartite graph. If the anchor survives and looks structurally different from the null, we haven't proven that the anchor is robust to size; we've merely proven that dense graphs differ from sparse trees.

### 3.2. Proposing a Confound-Stratified Permutation Null (v2)
To eliminate these artifacts, the v2 pipeline must use a **Null over catalog subsamples STRATIFIED ON CONFOUNDS**. 

*   **Mechanism:** When drawing the 500 null subsamples, the sampler must enforce matching on key structural invariants (e.g., degree distribution, spectral gap, rank, or algebraic genus). If the adversarial anchor has a specific degree distribution $D$, the permutation null must only sample objects from the catalog that fall within the adversarial band $X_{adv} \pm \epsilon$ AND share the distribution $D$.
*   **What this gains:** 
    1.  **Isolation of the Causal Mechanism:** It isolates the effect of the adversarial numeric extreme from auxiliary topological shifts. If the anchor survives and is deemed structurally different from the stratified null, we know the survival is due strictly to the conjecture's intrinsic properties, not an artifact of an unbalanced subsample.
    2.  **Mitigation of Phase-Transition False Positives:** As noted by Schäfer and Wetzel in their work on detecting quantum phase transitions via neural networks [cite: 14], machine learning systems often latch onto trivial order parameters (confounds) to distinguish phases. Stratification forces the evaluator to ignore trivial structural shifts and look for true logical anomalies. It directly prevents the `conjecture_survives_adversarial_attack` result from triggering spuriously just because the adversarial band's native population is skewed.

---

## 4. G16 v2 Loader Design: Concrete Specification

To operationalize the principles of percentile-based distances and confound-stratification, the following is the rigorous architectural specification for the G16 v2 loader.

### 4.1. Core Components

**A. Percentile-Based Adversarial Value Selection**
Instead of the hardcoded scalar `M = 1.20` or `10.0`, the loader queries the catalog's empirical CDF.
```python
def select_adversarial_value(catalog, parameter, percentile=99.0):
    """
    Locates the numeric extreme based on the distribution of known valid objects.
    """
    distribution = catalog.get_distribution(parameter)
    adv_value = distribution.calculate_percentile(percentile)
    return adv_value
```

**B. Confound-Stratified Permutation Null**
The sampling function implements nearest-neighbor matching in the space of structural invariants to build the null.
```python
def generate_stratified_null(catalog, adv_band, anchor, confounds, n_samples=500):
    """
    Builds a null distribution of size n_samples from the adv_band, 
    strictly matching the anchor on the provided confounds.
    """
    band_population = catalog.filter_by_band(adv_band)
    stratified_null = []
    
    for _ in range(n_samples):
        # Mahalanobis distance in the confound vector space
        sample = band_population.sample_nearest_neighbor(anchor.get_confounds(confounds))
        stratified_null.append(sample)
        
    return stratified_null
```

**C. Per-Adversarial-Direction (HIGH and LOW) with Directional Rules**
Mathematical vulnerability is rarely symmetric. The v2 loader forces independent tests for both tails of the distribution.
*   **HIGH Direction:** Pushes parameter to the 99th percentile. Tests for explosion/divergence artifacts.
*   **LOW Direction:** Pushes parameter to the 1st percentile. Tests for collapse/degeneracy artifacts.
*   **Directional Decision Rules:** If an anchor survives HIGH but fails LOW, it is classified as `directionally_fragile`. To achieve full validation (`conjecture_survives_adversarial_attack`), the anchor must survive *both* extreme bands independently against their respective stratified nulls.

**D. New Kill Pattern: `adversarial_band_empty_or_artifact`**
A critical failure mode of v1 is assuming that survival in a band is meaningful if the band itself contains no valid non-trivial objects.
*   **Logic:** Prior to evaluating the conjecture, the loader checks the density and diversity of the stratified null.
*   **Trigger:** If `len(band_population) < MIN_REQUIRED` or if the variance of the structural invariants in the band approaches zero (indicating a topological collapse into a single degenerate state, akin to a completely disordered phase [cite: 13]), the test is immediately aborted.
*   **Result:** The loader outputs the kill pattern `adversarial_band_empty_or_artifact`. This correctly assigns the blame to the limitation of the parameter space, rather than falsely validating the anchor.

---

## 5. Adversarial-Attack Suite Integration: Lethe $\to$ G16 Protocol

Within the broader AI-driven mathematical discovery ecosystem, individual agents perform specialized tasks. Drawing on the metaphorical architecture where "Erebos" handles deep structural memory and its sister agent "Lethe" induces "forgetting" or cold-calls novel, untested candidates [cite: 15, 16], we can define a multi-agent workflow.

Lethe acts as the vanguard exploratory LLM agent. Its mandate is to scour informal mathematical texts, vector databases, and heuristic outputs to identify *cold-call anti-anchor candidates*—hypothetical edge cases that human mathematicians or traditional solvers might have forgotten or overlooked. 

### 5.1. The Handoff Protocol Specification
When Lethe identifies a candidate anchor that seems mathematically plausible but is entirely unverified, it flags the object. To prevent pipeline bottlenecks, the Lethe $\to$ G16 hand-off must be strict, automated, and asynchronous.

1.  **Candidate Formatting and Tagging (Lethe):** 
    Lethe identifies a mathematical object $O$ and hypothesizes it as an anti-anchor against Conjecture $C$. Lethe tags the object with `FLAG_UNTESTED` and embeds a structural representation (e.g., TorchLean SSA/DAG format [cite: 4, 17]) into the message payload.
2.  **The Lethe Queue (Broker):**
    The object is placed into a priority message broker. Items tagged `FLAG_UNTESTED` with high heuristic confidence scores are prioritized.
3.  **Automated Ingestion (G16):**
    The G16 ANTI-ANCHOR protocol continuously polls the queue. Upon receiving $O$, G16 strips the LLM's natural language justifications (to avoid bias) and loads the raw structural representation into the v2 loader.
4.  **Extremum Testing Initialization:**
    G16 automatically computes the empirical percentiles for $O$'s parameters based on the existing mathematical catalog. It immediately forks into two parallel testing tracks: HIGH (99th percentile) and LOW (1st percentile).
5.  **Feedback Loop and Knowledge Update:**
    *   If G16 triggers `adversarial_band_empty_or_artifact`, the signal is sent back to Lethe to update its generative embeddings—teaching the LLM that this region of the parameter space is degenerate.
    *   If G16 triggers `conjecture_survives_adversarial_attack` (the anchor is successfully validated against the stratified null), the anchor is stripped of its `FLAG_UNTESTED` tag, promoted to the canonical database, and broadcasted back to the Erebos memory system for permanent retention.

This explicit protocol ensures that the creative, unstructured hallucination capabilities of an LLM agent like Lethe are strictly harnessed and formalized by the rigid, statistical mechanics of the G16 pipeline.

---

## 6. The Contrarian View: Adversarial Tests Prove the Wrong Thing

Despite the rigor of the v2 loader, a profound contrarian argument remains: **"An anchor surviving a $10\times$ (or 99th percentile) adversarial push is weak evidence of its robustness, because the adversarial push may have inadvertently shifted the object into a structurally trivial regime."**

### 6.1. Steelmanning the Argument
In continuous mathematics, taking a parameter to its limit often simplifies the equation. If we have a complex conjecture involving the interplay of terms $A(x) + B(x) = C(x)$, and we push $x$ to an extreme, it is highly probable that one term completely dominates the others (e.g., $A(x) \to \infty$ while $B(x)$ remains bounded). At this extreme, the conjecture degenerates into $A(x) \approx C(x)$, which might be trivially true. 

Therefore, when the G16 protocol reports that the "anchor survives the adversarial attack," it is not proving that the conjecture is robust to complex stress. It is merely proving that the conjecture is trivially true in a degenerate boundary state. The adversarial push has relieved the internal mathematical tension rather than exacerbating it.

### 6.2. Three Cases Requiring Sophisticated Adversarial Generators
To overcome this, we must identify specific mathematical regimes where scalar pushes are inherently flawed and require highly sophisticated, structure-preserving generators (like Co-FunSearch or CounterMath).

**Case 1: Topological Collapse in Network Pruning**
In graph theory and neural network architectures, decreasing connectivity (a LOW adversarial push) does not result in a linear degradation of properties. As demonstrated by Pesce et al. (2026), pruning a network leads to a sharp phase transition where the system moves from a cooperative phase to a completely disordered phase with collapsed performance [cite: 12, 13]. If an anti-anchor graph is pushed past this critical point, any conjectures about its spectral gap or routing efficiency become trivially void because the graph is essentially disconnected. A sophisticated generator must navigate *exactly* on the critical manifold of the phase transition, maximizing tension without inducing collapse.

**Case 2: Phase Transitions in Physics/Tensor Models**
When evaluating conjectures on multi-index models or quantum spin systems, shifting a parameter like the transverse field or temperature induces a phase transition (e.g., from ferromagnetic to paramagnetic) [cite: 14]. As shown by Arnaboldi, Pesce, et al., algorithms learning high-dimensional functions exhibit distinct phase transitions dependent on learning rate configurations [cite: 18, 19]. Pushing a parameter into the "generative exponent regime" alters the sample complexity fundamentally [cite: 18]. An adversarial test that simply pushes the temperature to $10\times$ tests the conjecture in a known, stable thermal state. A sophisticated generator must instead search for "glass transitions" or regions where the computational hardness is exponentially high [cite: 20], ensuring the conjecture is tested against maximum entropy rather than trivial equilibrium.

**Case 3: Floating-Point and Metric Space Verification Gaps**
In computational mathematics, pushing a value to $10\times$ often induces floating-point overflow, underflow, or precision truncation. A conjecture might "survive" simply because the evaluation metric rounded the adversarial values to zero or infinity, masking the true behavior of the mathematical object. The TorchLean framework explicitly addresses this by formalizing neural networks and mathematical objects with explicit IEEE-754 binary32 semantics within Lean 4 [cite: 4, 17, 21]. If an adversarial generator does not operate within a formally verified, proof-relevant rounding model [cite: 21], pushing parameters to the 99th percentile will likely just test the bounds of the compiler, not the bounds of the conjecture. A sophisticated generator must use abstract interpretation and bound propagation (e.g., CROWN/LiRPA [cite: 9]) to craft adversarial examples that stress the logic of the theorem while remaining strictly within the rigorously defined semantic bounds of the metric space.

---

### Conclusion
The evolution of the G16 ANTI-ANCHOR protocol from a naive, scalar-based testing environment to a confound-stratified, data-driven architecture represents a necessary adaptation to the complexities of modern mathematical discovery. By discarding the $10\times$ multiplier in favor of structural percentiles and integrating advanced LLM-driven generation (Co-FunSearch, CounterMath) alongside strict agent hand-off protocols (Lethe $\to$ G16), the testing of canonical examples moves closer to true formal verification. However, operators must remain vigilant of the contrarian reality: extreme parameters often lead to trivial phases, necessitating generators that respect the critical, topological boundaries of the underlying mathematical spaces.

**Sources:**
1. [deepmind.google](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElHoxqd_gCMGPo_IZYIHd1FZoWS9okAdcx8ivmBMzojn5IkzMZ6Z54omRMOL5pJYVNbT0l7kG0dpBm2-7TF0NA6JJT7LIxx59yRU8T-BjmWli8BCOdmZbMhH32gMgPwK9_vmOESestlfcSpkcV6a-iLz-Ju8VXcduSgc8t-tad4B-GscmDpw7JfuHZ0NOAyBXfzXAnIwSK6M_hZcxsALWJPbbne1tM9DBG)
2. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcW9LYS5lpP9RwOX_l5kMjmpq8OrB8bjbYljs4lafhwPfUIocTaOlE2Wfd1Z5WBEUgIbWNigivlgLsvR02gOYfRoETEsJvpgLR4iywU_w8QdeGoxnC_rQYzw==)
3. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEuVZsMe8KyHcGhrntZMcBOIEY2e9921FzMNmCFwgzFJZoCbKO1esb7RXb3zus6LHlPUzHW8i9XUYkhunKd0xGyCkjl3i3mwFP1W8q6lTcb9TZH6TIv1w==)
4. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8VzutKByckvZRLm0DM-3w50cDDBOj2FB10bvxnLWRw0tU_IuLgMhSVYOXE1M81M-iuE8OEJcjvne2Gwd42Ng_b0bKSZo99-g6QyJDFBZHtVruVE-zyhxolQ==)
5. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAO9jaqolrzxm4tS0CPdpIenGq4U41jjILxIlUG9C6MXcHlVvPJQOVgidJsNgapcT7mBiqUyjP2CRiVQNPhXA3xuy_GYZlM1u6BmzEPsuWydmDpEn-lg==)
6. [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHY7iRuxKmX7CiEQ8sWidcr83Ru9Q6ij0ILNc7J2WgG_tmI30XVO99idrEaQOc7nrjy4Mmep5Fa8hYq8sGY2MHcfK8Mde59xLk4pRCoFGcPt_nFjDptx2ypFDVcgE6PBlLnNnojj0IQGdqN4MOul2GP8l5yc2-vtMdpaO6i7axXY2EyV-psgn0ws1nL8Kddk3dVZGEQKInNv0Kk2hGn5DkiGsYn9wZrl0HfNx9EhIsRpA==)
7. [emergentmind.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZNTaZDdcqHrngCB-kdJNrok6l02gXX8fBPG8TEw2hq_WlusPxdK8Vb1mKQhU0n4QS7AwAxp7f-EdVNRRbPuR5x0ObTu7IZWFQrMBZVLS_8amwCFoQRQC-uBn2Jlnj4dOVqea8lNaOhekVekI-)
8. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcGXlSdXVxqkylaRlV-9VywrEI4Yxmu-A7RfB6-PvI3l6AhcXAIjNPFWaGC3JRgoXQI2mnBZfvbtsNakFyEIoMasnzSZq20JpJvLPKq3kI6xfUQ1EnM1rTuQ==)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGO15Xk3pbk0cj7D4Giguq3qnCnAkxN9lH2LjSit_BZWcTuH_Wm9FPqToJfY2ZyDFhqmIBA9NMfrWS-JhmJq2KgemuzGhoovVkW6HD_SeGLXIFBnpQFSg==)
10. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGvdTav20pqtIUwtdt_torC3dBhc6-iQPXJRZsvMKVqH7A1FZa3oCuQrY-bP66Ngq4tHoxJOo2OJBR0Oh6eOuWURcd0wsHuN7_AHqxNjGsZ-PEFLqC4q581w==)
11. [harvard.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElz4KzWe5Ax_V-LJGh1KTp28XWT6tCCZc_LaKWcKBBTV9J500mwSN1sIUCP4oItB4Ij5-ToPRbJxHHK2ojUNzIJagVfSTUrXpI9c-uvHxA6OIkQuMAwNzfMcco-2yGIZugo60ShitP9ZtS9QgbE06U0eZ6sE_zvOYbPgrKMw9iRO5g-Ii-YMo8vTocfQwI)
12. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzJ_8tsazz658-a9-btOt3QeGyUlsz6GReuH-iOK4K25DJ1i2P8ucaI8uCFYgtIbOMMxxidzW8a-783XQ54muFWEbwuLsBWvOlNt46HABUqW7-9UCvbQ==)
13. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNtDRXabyq1aszLTNqW8150dowOV6OOQbL839ZLEeX8L_RgpCAyoZWw07bFy3gc0-97WmC_IConYCigChwziPxSA3ds7rE5UdjQMI-SmOF3oVeLv9Dm9pFnQ==)
14. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz1LAk8mjjRzJCrk7mdUCBlF4gn1QMX0tq7RQqZSqD4YzYgOSQ8odo1XZnJ8Q44UmJ22SMKaaz7k4feFuKmc6--zT4OSvdXiRch2Z6G286s8FJevzWIojk0FUh1cue7EP_eput20Iqr2qUifycRQWWlL9194PW95bkik7XbAFeZBA=)
15. [rprepository.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8l20FVezB214gKdcFLINYX_qKhWk2RXwICchDf1AyagFKEz7vAiAFk2VwKLmRdZ7fl7Ge6I2aC2S0vwsTIACav2zQdH9qWDSztHL6LytlbfnCPdUZofd1WRSp5Q6-qAhK5hdsNIfKwUsJmQ==)
16. [theoi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnpEjJLDwh35dkMfM9w1M2gqZUnrd9llJ2D97-tZ6AgJ0P4fGfcD5anjvBVYFJgFuilYTxpYdWyFw8YktV1K_Frsh2zY6c4PF_xgsDxczb4fiYqDTAhlWtKVj8wCUf)
17. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHN_gUybBiMsIiU7COEjs8V1tudrVcltogWBfxCllPiFoHV96UI5rOH_yKkhU3M6MCgNVfrc0iV6Yh30rY0fOqbGCbeFQpa2uvzREfIcxjhyxU5jTqW5aZn1Q==)
18. [openreview.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGWDCmeaQyJPwmXssmAaL6_L1H2WyT5FY3SyOItvTyYAHuegCwPIZ6bW7s-QWBTjQhQcsVv_UnWcEG1YlR3VKawqkMf4T8ftHnWCI5nxs1IJioMLv32OPQiuEYL1-e)
19. [toronto.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHefBNov9ZDL5HyVVo-OJHWWeD8CeDD6eu2wosjvlXAHuGo2vWqNE4-ulvgIru6SFd0JcELFHtxfHdw7Nb6krr38z2ejMd5RXJRQ6vQdeVebeQdc0otSfflTY7XnjCTle46JS7bP3fBqZ-6)
20. [ifml.institute](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGD1i0HBoe50PUwj33-rBnmvIM2F_fFV2D-o_q5m18sypzBkHdqfnSA62ElpY1c41KB45JsXxja-t6RpjtcpGqEFpUpxrit9Qe4bTpWLStnmP7EzBrmAVxur6U3N1CeJtZIzvLPOu7rRamJTVqR1tbJ0HkVFCe294-DaEwMfeKmIp9XIB9kPWay8FffAL64dw0TW-XA-zG8IKDEP-eK)
21. [alphaxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQElGe-IkhQEMNNV7cxcb8xK6B1lgpV5wu6cIlFDP8k22U3mzf3HVPzaT0kDv_GDhhMuSpWIFf8ZYrfArl4aWcN9dkEA7K_UIqkfHkwowP82Jf4CGfnHRe3L6LSenJfBupSQdmMB)


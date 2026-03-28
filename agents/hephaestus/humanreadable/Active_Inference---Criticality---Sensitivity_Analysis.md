# Active Inference + Criticality + Sensitivity Analysis

**Fields**: Cognitive Science, Complex Systems, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T01:13:11.238850
**Report Generated**: 2026-03-27T02:16:36.544768

---

## Nous Analysis

**Algorithm: Free‑Energy‑Driven Constraint Propagation (FECP)**  

*Data structures*  
- **Proposition graph** `G = (V, E)` where each node `v_i` holds a parsed proposition (e.g., “X > Y”, “¬P”, “if A then B”).  
- Each node stores a **belief vector** `b_i ∈ ℝ^k` (k = number of possible truth states, typically 2 for true/false) representing the agent’s posterior over the proposition’s truth.  
- Edge weights `w_ij ∈ ℝ` encode the strength of a logical relation (e.g., modus ponens: `w = 1.0` for “A → B”, `w = 0.5` for comparative “X > Y” → “Y < X”).  
- A **precision matrix** `Π = diag(π_1,…,π_n)` where `π_i` is the inverse variance (confidence) of node `i`.  

*Operations*  
1. **Parsing** – regex‑based extractor yields tuples `(type, args)` → creates nodes and edges. Supported types: negation, comparative, conditional, causal, ordering, numeric equality/inequality.  
2. **Active inference step** – compute expected free energy `G = Σ_i π_i * KL(b_i || b_i^prior) + Σ_(i,j) w_ij * D_KL(b_i || T_ij(b_j))`, where `T_ij` is the deterministic transition implied by the edge (e.g., modus ponens maps `b_A=true` to `b_B=true`). Gradient descent on `b` minimizes `G`.  
3. **Criticality tuning** – after each gradient step, compute the susceptibility `χ = Σ_i π_i * Var(b_i)`. If `χ` exceeds a threshold, increase all `π_i` (raise precision) to push the system toward the edge of instability; if `χ` is low, decrease `π_i`. This drives the belief network to a critical point where small input changes produce large, informative belief shifts.  
4. **Sensitivity analysis** – perturb each input proposition’s belief by ε (e.g., flip truth with probability 0.01) and recompute the free energy gradient; the resulting sensitivity `S_i = |ΔG/Δb_i|` quantifies how much the answer depends on that input.  

*Scoring logic*  
For each candidate answer `a`, create a temporary node representing the answer proposition, connect it to the parsed question graph with edges reflecting logical entailment (e.g., answer “X > Y” gets an edge from any extracted “X > Y” statement). Run FECP to convergence, then compute the answer’s **expected free energy** `G_a`. Lower `G_a` indicates higher plausibility; scores are normalized: `score(a) = -G_a / max_a |G_a|`.  

*Structural features parsed*  
Negation (`not`, `no`), comparatives (`greater than`, `less than`, `equal`), conditionals (`if … then …`, `unless`), causal claims (`because`, `leads to`), ordering relations (`first`, `before`, `after`), numeric values and inequalities, and conjunction/disjunction cues (`and`, `or`).  

*Novelty*  
The trio of active inference (expected free energy minimization), criticality‑driven precision adaptation, and local sensitivity‑based weighting has not been combined in a deterministic, numpy‑only text‑scoring tool. Existing work treats each concept separately (e.g., Bayesian model averaging, critical neural nets, or Sobol sensitivity) but none fuse them into a single constraint‑propagation scoring loop for logical reasoning evaluation.  

**Ratings**  
Reasoning: 8/10 — The algorithm directly optimizes beliefs under logical constraints, yielding principled plausibility scores.  
Metacognition: 6/10 — Precision adjustment offers a rudimentary form of confidence monitoring, but lacks higher‑order self‑reflection.  
Hypothesis generation: 5/10 — Sensitivity highlights influential premises, yet the system does not propose novel hypotheses beyond the given graph.  
Implementability: 9/10 — All steps use regex, numpy linear algebra, and simple loops; no external libraries or APIs are required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

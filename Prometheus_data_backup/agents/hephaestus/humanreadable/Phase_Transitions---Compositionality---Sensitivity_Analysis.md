# Phase Transitions + Compositionality + Sensitivity Analysis

**Fields**: Physics, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T15:23:49.651086
**Report Generated**: 2026-03-31T23:05:19.807372

---

## Nous Analysis

**Algorithm**  
We build a bottom‑up *differentiable logical graph* for each candidate answer.  
1. **Parsing** – Using regex‑based patterns we extract atomic propositions and their logical connectives:  
   - Negation (`not`, `no`) → unary node `¬`  
   - Comparatives (`greater than`, `less than`, `equals`) → binary node `cmp` with a numeric threshold  
   - Conditionals (`if … then …`, `unless`) → implication node `→`  
   - Causal claims (`because`, `leads to`) → directed edge node `cause`  
   - Ordering relations (`before`, `after`) → temporal node `≺`  
   - Numeric literals → leaf nodes holding a float value.  
   The output is a directed acyclic graph (DAG) where each node stores a NumPy array `val` (truth value in \([0,1]\) or numeric) and a sensitivity vector `∂score/∂val`.  

2. **Compositional evaluation** – Starting from leaves, we compute node values with standard fuzzy logic:  
   - `¬x = 1 - x`  
   - `x ∧ y = min(x, y)` (implemented as `np.minimum`)  
   - `x ∨ y = max(x, y)` (`np.maximum`)  
   - `x → y = max(1‑x, y)`  
   - `cmp(x, t) = sigmoid(k·(x‑t))` (steepness `k` fixed, gives a smooth phase‑like transition)  
   - `cause(x, y) = x·y`  
   Each operation also propagates sensitivities using the chain rule (e.g., for `z = min(x,y)`, `∂z/∂x = 1` if `x<y` else `0`). All operations are pure NumPy.  

3. **Phase‑transition detection** – After the forward pass we have a base answer score `S = root.val`. We then apply a small perturbation `ε` to each leaf (e.g., `ε=0.01`) and recompute the score, obtaining `S_i^+`. The sensitivity magnitude for leaf `i` is `|S_i^+ - S|/ε`. We compute the *maximum leaf sensitivity* `M`. If `M` exceeds a preset critical value `θ` (chosen from a validation set), we treat the answer as being in a fragile regime — a qualitative phase change in robustness.  

4. **Scoring logic** – Final score = `S * (1 - min(M/θ, 1))`. High base consistency is penalized proportionally to fragility; answers that are both consistent and robust receive scores near 1.  

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering relations (temporal), numeric thresholds, and logical conjunction/disjunction. These are the primitives whose composition determines the overall truth value and whose perturbations trigger the sensitivity‑phase‑transition signal.

**Novelty**  
The approach combines three known ideas — compositional fuzzy evaluation, local sensitivity analysis (used in robust verification of logical circuits), and detecting abrupt changes via a threshold on sensitivity (akin to order‑parameter phase transitions). While each component appears in differentiable logic and robustness literature, their joint use to score reasoning answers is not documented in public toolkits, making the combination novel for this evaluation setting.

**Rating**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency and quantifies robustness via sensitivity, capturing core reasoning demands.  
Metacognition: 6/10 — It provides a self‑assessment of fragility but does not explicitly model the model’s own uncertainty about its parsing.  
Hypothesis generation: 5/10 — Sensitivity scores hint at which atomic propositions are critical, offering weak guidance for generating alternative hypotheses.  
Implementability: 9/10 — All operations are pure NumPy/regex; no external libraries or neural components are required, making it straightforward to code and run.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T20:03:14.045598

---

## Code

*No code was produced for this combination.*

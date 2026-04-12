# Hebbian Learning + Counterfactual Reasoning + Sensitivity Analysis

**Fields**: Neuroscience, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T21:09:23.476627
**Report Generated**: 2026-03-27T02:16:42.621229

---

## Nous Analysis

The algorithm builds a weighted propositional graph from the prompt and updates it with a Hebbian‑style rule, then evaluates each candidate answer by propagating counterfactual perturbations and measuring output sensitivity.

**Data structures**  
- `props`: list of unique propositions extracted from the text (index 0…n‑1).  
- `W`: n×n numpy array, edge weight w_ij representing the strength of the association “i → j”.  
- `T`: n‑dim binary numpy array, current truth assignment of each proposition in the observed world.  
- `conds`: list of tuples (a_idx, c_idx) for each explicit conditional “if A then C” found in the prompt.  

**Operations**  
1. **Initial Hebbian seeding** – For every pair of propositions that co‑occur in the same sentence, update  
   `w_ij ← w_ij + η·(T_i·T_j) – η·(T_i·(1‑T_j))`  
   (η = 0.1). This strengthens links when both are true and weakens them when the antecedent is true but the consequent false, mimicking LTP/LTD.  
2. **Constraint propagation (modus ponens)** – Iterate until convergence: for each (a,c) in `conds`, if `T[a]==1` then set `T[c] ← max(T[c], w_ac)`. Use numpy’s vectorized max to avoid loops.  
3. **Counterfactual perturbation** – For each conditional, create a copy `T̃` where `T̃[a]=1‑T[a]` (flip the antecedent), re‑run step 2, and record the change Δc = |T̃[c]‑T[c]|. Collect all Δc into a vector `δ`.  
4. **Sensitivity analysis** – Approximate the Jacobian of the output score w.r.t. `W` by finite differences: perturb each weight by ε, recompute the final truth vector, and compute the variance of the resulting scores across perturbations. Let `σ` be the standard deviation of these scores.  
5. **Scoring a candidate answer** – The answer is represented as a binary vector `A` over `props`. Consistency `C = (T·A) / sum(A)`. Robustness `R = 1 / (1 + σ)`. Final score `S = C * R`. All steps use only numpy arithmetic and Python’s standard‑library containers.

**Structural features parsed**  
- Negations (`not`, `no`), conditionals (`if … then …`, `unless`), comparatives (`greater than`, `less than`), causal verbs (`cause`, `lead to`, `result in`), numeric values and units, ordering relations (`before`, `after`, `precede`), and explicit quantifiers (`all`, `some`, `none`). Regex patterns extract these and map them to propositions and conditional edges.

**Novelty**  
Pure Hebbian learning is common in neural nets; counterfactual reasoning appears in causal‑inference libraries; sensitivity analysis is used in uncertainty quantification. Combining them to dynamically weight a propositional graph, propagate counterfactuals, and derive a robustness‑adjusted consistency score has not been seen in existing reasoning‑evaluation tools, which typically rely on either static logical theorem proving or similarity‑based metrics. Hence the approach is novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and counterfactuals but lacks deep recursive reasoning.  
Metacognition: 5/10 — the tool does not monitor or adjust its own learning rate or strategy.  
Hypothesis generation: 6/10 — generates alternative worlds via antecedent flips, a modest hypothesis space.  
Implementability: 8/10 — relies solely on numpy and regex; straightforward to code and debug.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Counterfactual Reasoning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Chaos Theory + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

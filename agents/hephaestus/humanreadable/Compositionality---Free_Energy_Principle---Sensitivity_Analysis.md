# Compositionality + Free Energy Principle + Sensitivity Analysis

**Fields**: Linguistics, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:41:11.779844
**Report Generated**: 2026-03-27T06:37:39.770706

---

## Nous Analysis

**Algorithm: Compositional Free‑Energy Sensitivity Scorer (CFESS)**  

**Data structures**  
- `ParseTree`: a directed acyclic graph where each node stores a token span, its syntactic role (subject, predicate, object, modifier), and a list of child node IDs.  
- `FeatureVector`: a NumPy array of shape `(F,)` where each dimension corresponds to a structural feature extracted from the tree (see §2).  
- `EnergyMap`: a dictionary `{node_id: float}` holding the variational free‑energy contribution of each node.  

**Operations**  
1. **Structural parsing** – Using only `re` and the standard library, the prompt and each candidate answer are tokenized and a shallow dependency‑like tree is built. Rules capture:  
   - Negations (`not`, `n't`) → attach a `neg` flag to the predicate node.  
   - Comparatives (`more`, `less`, `-er`, `than`) → create a `comp` node with left/right operands.  
   - Conditionals (`if … then …`) → split into antecedent and consequent sub‑trees linked by a `cond` node.  
   - Numeric values → leaf nodes with a `num` type and the float value stored.  
   - Causal verbs (`cause`, `lead to`, `result in`) → edge label `cause`.  
   - Ordering relations (`before`, `after`, `first`, `last`) → edge label `order`.  

2. **Free‑energy computation** – For each node `n`, compute a local error term `e_n` as the squared difference between the node’s observed feature value (e.g., presence/absence of a negation, numeric magnitude) and a prior expectation `p_n` (set to 0.5 for binary features, 0 for numeric features). The node’s free energy is `F_n = e_n + λ * Σ_{c∈children(n)} F_c`, where λ=0.1 implements a hierarchical prior (the Free Energy Principle). The total free energy of a candidate is `F_total = Σ_n F_n`. Lower `F_total` indicates better compositional fit.

3. **Sensitivity analysis** – Perturb each binary feature by flipping its value (±1) and each numeric feature by adding Gaussian noise σ=0.05. Re‑compute `F_total` for each perturbation; the sensitivity score `S = std(F_total_perturbations)`. High sensitivity means the answer’s score changes sharply under small input changes, indicating low robustness.

4. **Scoring logic** – Final score = `-(F_total + α * S)`, with α=0.2 to penalize sensitivity. Higher (less negative) scores rank candidates better.

**Structural features parsed** (the `FeatureVector` dimensions): presence of negation, comparative direction, conditional antecedent/consequent, numeric magnitude, causal edge count, ordering edge depth, subject‑verb‑object triple count, modal verb presence, quantifier scope.

**Novelty** – The combination mirrors recent work on energy‑based language models (e.g., contrastive predictive coding) and sensitivity‑driven robustness checks, but it explicitly couples compositional syntactic parsing with a variational free‑energy recursion and a perturbation‑based sensitivity term. No published tool uses exactly this triple‑layered scoring pipeline, so the approach is novel in its algorithmic concretization.

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty via free‑energy minimization.  
Metacognition: 5/10 — provides a sensitivity proxy but lacks explicit self‑monitoring of reasoning steps.  
Hypothesis generation: 4/10 — focuses on scoring given answers; does not propose new candidates.  
Implementability: 8/10 — relies only on regex, basic tree ops, NumPy arithmetic, and stdlib.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Compositionality + Free Energy Principle: strong positive synergy (+0.137). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Sensitivity Analysis: strong positive synergy (+0.375). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Ecosystem Dynamics + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Free Energy Principle + Property-Based Testing + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

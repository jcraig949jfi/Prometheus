# Compositionality + Free Energy Principle + Sensitivity Analysis

**Fields**: Linguistics, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:56:19.138799
**Report Generated**: 2026-04-02T04:19:56.610373

---

## Nous Analysis

**Algorithm:**  
1. **Parsing (Compositionality)** – Tokenize the prompt and each candidate answer with regex‑based patterns that extract atomic propositions:  
   - Predicate‑argument tuples `(rel, arg1, arg2?)` for relations like *is‑greater‑than*, *causes*, *negates*.  
   - Literals for numeric comparisons (`value1 < value2`), ordering chains, and boolean flags for negations.  
   Store each proposition as a node in a directed hypergraph `G = (V, E)`, where `V` holds literals and `E` encodes the syntactic rule that combined them (e.g., conjunction, implication).  

2. **Energy Definition (Free Energy Principle)** – Define a variational free energy `F(Q) = ⟨log Q - log P⟩_Q`, where `P` is a generative model of the prompt’s logical structure and `Q` is a candidate‑answer distribution over truth assignments to `V`.  
   - Approximate `Q` as a product of independent Bernoulli variables per literal (mean‑field).  
   - The expected log‑likelihood term reduces to a sum of clause potentials: each clause contributes `0` if satisfied under the current assignment, otherwise a penalty `λ` (hand‑tuned).  
   - The entropy term is analytic for Bernoulli factors.  

3. **Sensitivity‑Guided Optimization** – Compute the gradient of `F` w.r.t each literal’s marginal probability `p_i` using finite differences (perturb `p_i` by ε, re‑evaluate clause satisfaction). This yields a sensitivity vector `∂F/∂p`.  
   - Perform a few steps of gradient descent on the mean‑field parameters to minimize `F`, projecting probabilities back to `[0,1]`.  
   - The final free energy `F*` serves as the score; lower `F*` indicates higher alignment of the candidate answer with the prompt’s logical constraints.  

**Structural features parsed:** negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then …`), causal verbs (`causes`, leads to`), numeric values and units, ordering chains (`A > B > C`), and conjunction/disjunction markers.  

**Novelty:** The combination mirrors recent neuro‑symbolic proposals (e.g., DeepProbLog, Neural Theorem Provers) but replaces learned neural potentials with hand‑crafted clause potentials and uses a pure‑numpy mean‑field free‑energy minimization with explicit sensitivity steps—a configuration not reported in existing open‑source reasoning evaluators.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and propagates constraints, but limited to hand‑crafted predicates.  
Metacognition: 5/10 — no explicit self‑monitoring of uncertainty beyond entropy term.  
Hypothesis generation: 6/10 — gradient step proposes new truth assignments, akin to local search.  
Implementability: 8/10 — relies only on regex, numpy arrays, and basic loops; no external libraries.

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

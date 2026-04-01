# Criticality + Maximum Entropy + Metamorphic Testing

**Fields**: Complex Systems, Statistical Physics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:47:29.686350
**Report Generated**: 2026-03-31T14:34:55.632587

---

## Nous Analysis

The algorithm builds a constraint‑satisfaction model from the prompt, scores each candidate answer by how much it violates those constraints, and then rescores the violations using a maximum‑entropy distribution whose temperature is set at the point of maximal susceptibility (criticality).  

**Data structures**  
- `atoms`: list of parsed propositions, each a tuple `(pred, args, polarity)` where `pred` ∈ {negation, comparative, conditional, causal, ordering, numeric}.  
- `A` (m×n) and `b` (m): NumPy arrays representing linear inequalities/equalities derived from `atoms`. Each row corresponds to one constraint (e.g., for “X > Y” → `x_X - x_Y ≥ ε`).  
- `X` (k×n): feature matrix for k candidate answers; each row `x_i` assigns a real value to every variable appearing in the prompt (0/1 for Boolean predicates, the extracted number for numeric atoms).  

**Operations**  
1. **Parsing** – regexes extract the six structural feature types listed below and fill `atoms`.  
2. **Constraint compilation** – for each atom generate a row in `A,b`:  
   - negation: `x_pred = 0`  
   - comparative (`>`/`<`): `x_subj - x_obj ≥ ε` or `≤ -ε`  
   - conditional (`if P then Q`): `x_P ≤ x_Q + M·(1‑x_P)` (big‑M formulation)  
   - causal (`because`): same as conditional.  
   - ordering (`before/after`): temporal variables ordered similarly to comparatives.  
   - numeric: equality constraint `x_var = value`.  
3. **Violation computation** – `v = np.maximum(0, A @ x_i.T - b)` (shape m). Penalty `p_i = np.sum(v**2)`.  
4. **Critical temperature scan** – evaluate `p_i` over a log‑spaced β range, compute variance of `exp(-β p_i)`. Choose β* where variance peaks (max susceptibility).  
5. **Maximum‑entropy scoring** – `q_i = exp(-β* p_i) / Σ_j exp(-β* p_j)`. Final score = `-log q_i` (higher = worse).  

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`greater than`, `less than`, `≥`, `≤`), conditionals (`if … then …`), causal claims (`because`, `leads to`), numeric values (integers, decimals), ordering relations (`first`, `second`, `before`, `after`, `earlier`).  

**Novelty**  
Maximum‑entropy inference for QA exists (e.g., log‑linear models), and metamorphic testing is used for NLG validation, but none combine a critical‑point temperature selection with constraint propagation derived from explicit logical parsing. This triple coupling is not reported in current surveys, making the approach novel.  

**Ratings**  
Reasoning: 7/10 — captures long‑range logical dependencies via constraint violations and critical susceptibility.  
Metacognition: 6/10 — temperature selection reflects sensitivity to perturbations but does not model higher‑order self‑monitoring.  
Hypothesis generation: 5/10 — focuses on scoring given hypotheses; generation of new candidates is outside scope.  
Implementability: 8/10 — relies only on regex, NumPy linear algebra, and simple loops; no external libraries or neural components.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

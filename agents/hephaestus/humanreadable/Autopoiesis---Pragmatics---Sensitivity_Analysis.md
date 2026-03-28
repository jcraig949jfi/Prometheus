# Autopoiesis + Pragmatics + Sensitivity Analysis

**Fields**: Complex Systems, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T02:41:26.588175
**Report Generated**: 2026-03-27T04:25:51.776512

---

## Nous Analysis

**Algorithm: Self‑Organizing Pragmatic Sensitivity Scorer (SOPSS)**  

1. **Data structures**  
   - `tokens`: list of strings from regex‑tokenized prompt and each candidate answer (preserves order).  
   - `constraints`: dict mapping a variable name (e.g., “X”, “Y”) to a tuple `(type, value_set)` where `type` ∈ {`bool`, `numeric`, `ordinal`}.  
   - `implicature_graph`: directed adjacency list `{(src_var, dst_var): weight}` representing inferred pragmatic relations (e.g., “if A then B”).  
   - `sensitivity_matrix`: NumPy array `S` of shape `(n_vars, n_vars)` where `S[i,j]` quantifies how a perturbation of variable *i* changes the truth value of variable *j* (computed via finite‑difference on the constraint evaluation).  

2. **Operations**  
   - **Structural parsing** – Apply a fixed set of regex patterns to extract:  
     * negations (`not`, `no`),  
     * comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`),  
     * conditionals (`if … then …`, `unless`),  
     * causal markers (`because`, `due to`, `leads to`),  
     * numeric literals and units,  
     * ordering cues (`first`, `second`, `before`, `after`).  
     Each match creates or updates a variable in `constraints` and adds an edge to `implicature_graph` with an initial weight derived from Gricean maxim relevance (e.g., 1.0 for explicit conditionals, 0.5 for implicature).  
   - **Constraint propagation** – Iteratively apply modus ponens and transitivity: for each edge `(u→v,w)` if `u` is satisfied (per its current domain) then tighten `v`’s domain using `w` as a confidence factor; repeat until convergence (≤ 5 passes, guaranteed because domains only shrink).  
   - **Sensitivity analysis** – After propagation, compute `S` by perturbing each variable’s domain by a small epsilon (e.g., ±0.01 for numerics, flipping bool) and measuring the resulting change in satisfied constraints; store the absolute change normalized by epsilon.  
   - **Scoring** – For each candidate answer, compute a pragmatic fit score:  
     `score = Σ_{(u→v,w)∈implicature_graph} w * sat(u) * sat(v) * exp(-α * S[u,v])`  
     where `sat(x)` is 1 if variable `x` is satisfied in the answer’s interpretation, 0 otherwise, and α = 0.5 penalizes edges that are highly sensitive (i.e., fragile to perturbations). Higher scores indicate answers that preserve the self‑producing (autopoietic) organization of the prompt’s meaning while being robust to small input variations.  

3. **Parsed structural features**  
   Negations, comparatives, conditionals, causal markers, numeric values with units, and temporal/ordering relations. These are the primitives that feed variables and edges into the constraint‑propagation loop.  

4. **Novelty**  
   The combination mirrors existing work in logical form extraction (e.g., COGEX) and sensitivity‑based robustness checks (e.g., robustness scores in causal inference), but it uniquely couples autopoiesis‑inspired organizational closure (constraints that must remain self‑consistent) with pragmatic implicature weighting and a explicit sensitivity matrix. No published tool jointly uses a closed‑loop constraint system, pragmatic edge weights, and finite‑difference sensitivity to score answer candidates, making the approach novel in this configuration.  

Reasoning: 7/10 — Captures logical structure and robustness but relies on hand‑crafted regex and linear sensitivity, limiting deep reasoning.  
Metacognition: 5/10 — No explicit self‑monitoring of propagation stability; convergence is assumed rather than diagnosed.  
Hypothesis generation: 4/10 — Generates only deterministic refinements of given variables; no speculative abductive steps.  
Implementability: 9/10 — Uses only regex, NumPy arrays, and basic loops; fully compatible with the stipulated libraries.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Autopoiesis**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Category Theory + Embodied Cognition + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

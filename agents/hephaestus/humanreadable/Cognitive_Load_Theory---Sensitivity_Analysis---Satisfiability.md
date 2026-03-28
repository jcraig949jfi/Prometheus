# Cognitive Load Theory + Sensitivity Analysis + Satisfiability

**Fields**: Cognitive Science, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T13:16:11.552266
**Report Generated**: 2026-03-27T06:37:44.749396

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Constraint Matrix**  
   - Extract atomic propositions from the prompt and each candidate answer using regex patterns for:  
     *Negations* (`not`, `no`), *comparatives* (`>`, `<`, `>=`, `<=`), *conditionals* (`if … then …`, `unless`), *causal claims* (`because`, `leads to`, `results in`), *ordering* (`before`, `after`, `first`, `last`), and *numeric literals*.  
   - Encode each proposition as a Boolean variable `v_i`.  
   - Build a clause list in CNF: each extracted relation becomes one or more clauses (e.g., `X > Y` → `(v_xy ∨ ¬v_yx)`, `if A then B` → `(¬v_a ∨ v_b)`). Store clauses as a NumPy `int8` matrix `C` of shape `(n_clauses, n_vars*2)` where even columns are positive literals, odd columns are negative literals.  

2. **Satisfiability Check (DPLL)**  
   - For a candidate answer, add its clauses to `C` forming `C'`.  
   - Run a pure‑Python DPLL solver that works on the NumPy matrix (unit propagation, pure literal elimination, backtracking). Returns `sat = 1` if satisfiable, else `0`.  
   - If unsat, extract a minimal unsatisfiable core by repeatedly removing clauses and re‑checking sat; core size `core_len` penalizes the answer.  

3. **Sensitivity Analysis**  
   - Identify numeric variables (those arising from comparatives). For each, create a perturbed copy of `C'` where the numeric literal is replaced by `value ± ε` (ε = 0.01 · range of that numeric).  
   - Re‑run DPLL on each perturbed matrix; compute `sat_change = |sat_original - sat_perturbed|`.  
   - Robustness score `R = 1 - (mean(sat_change) / n_numeric)`.  

4. **Cognitive Load Estimation**  
   - Compute chunk load `L = (total literals in C') / L_max`, where `L_max = 7` (Miller’s chunk limit).  
   - Load penalty `P = L` (clipped to `[0,1]`).  

5. **Final Score**  
   ```
   score = sat * R - 0.5 * P - 0.2 * (core_len / n_clauses)
   ```
   Higher scores indicate answers that are logically consistent, robust to small numeric perturbations, and cognitively parsimonious.

**Parsed Structural Features**  
Negations, comparatives, conditionals, causal connectives, temporal ordering, conjunction/disjunction, and explicit numeric constants.

**Novelty**  
Pure SAT‑based QA systems exist, and cognitive load metrics are used in educational tech, but integrating sensitivity analysis (perturb‑and‑re‑check) with a SAT core to jointly measure logical robustness and mental effort is not described in the literature. Hence the combination is novel.

**Rating**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency and robustness, core to reasoning.  
Metacognition: 6/10 — Load penalty approximates awareness of mental effort, but lacks explicit self‑monitoring.  
Hypothesis generation: 5/10 — The method checks given answers; it does not propose new hypotheses beyond the supplied candidates.  
Implementability: 9/10 — Uses only regex, NumPy matrix ops, and a straightforward DPLL solver; no external dependencies.

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

- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 


Similar combinations that forged successfully:
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Cellular Automata + Cognitive Load Theory + Phenomenology (accuracy: 0%, calibration: 0%)
- Chaos Theory + Cognitive Load Theory + Kalman Filtering (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

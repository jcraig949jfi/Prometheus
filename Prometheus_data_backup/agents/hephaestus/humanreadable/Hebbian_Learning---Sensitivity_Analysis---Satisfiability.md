# Hebbian Learning + Sensitivity Analysis + Satisfiability

**Fields**: Neuroscience, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T09:47:45.253438
**Report Generated**: 2026-04-01T20:30:43.874115

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Variable Creation** – Using regex, extract atomic propositions from the prompt and each candidate answer:  
   - Literals (e.g., “X > 5”, “¬Y”, “if A then B”).  
   - Each distinct literal becomes a Boolean variable *vᵢ*; its negation is represented implicitly.  
   - Store clauses as lists of literals (positive or negative) in CNF form.  

2. **Initial Weight Matrix** – Initialize a symmetric weight matrix *W* (size *n×n*, *n* = number of variables) with zeros.  
   - For every pair of literals that appear together in the same clause (prompt or candidate), increment *W[i][j]* and *W[j][i]* by 1. This is the **Hebbian update**: co‑occurring neurons (literals) strengthen their synaptic weight.  

3. **Weighted SAT Evaluation** – For a candidate answer, treat its clause set as constraints.  
   - Compute a *soft* satisfaction score:  
     \[
     S = \sum_{c\in C_{prompt}} w_c \cdot \mathbb{I}[c \text{ is satisfied}]
     \]  
     where *w_c* = average of *W* values over the literals in clause *c* (i.e., the strength of the connections supporting that clause).  
   - Use a pure‑Python DPLL SAT solver (no external libraries) to obtain the Boolean satisfaction indicator 𝕀[·].  

4. **Sensitivity Analysis** – Perturb each weight *W[i][j]* by a small ε (e.g., 0.01) and recompute *S*.  
   - Let *S⁺* and *S⁻* be the scores after +ε and –ε perturbations.  
   - Compute sensitivity as the variance:  
     \[
     \sigma^2 = \frac{1}{m}\sum_{k=1}^{m} (S_k - \bar{S})^2
     \]  
     where *m* = 2·|W| (up/down for each edge) and *S_k* are the perturbed scores.  

5. **Final Score** –  
   \[
   \text{Score} = S - \lambda \cdot \sigma
   \]  
   with λ set to 0.1 to penalize unstable satisfaction. Higher scores indicate answers that are both strongly supported by co‑occurrence evidence and robust to small weight changes.  

**Structural Features Parsed** – Negations (“not”, “¬”), comparatives (“>”, “<”, “≥”, “≤”), conditionals (“if … then …”, “implies”), numeric thresholds, ordering relations (“before”, “after”), and causal cues (“because”, “leads to”). Each maps to a literal or a clause pattern captured by the regex stage.  

**Novelty** – The approach fuses three known ideas: Hebbian‑style co‑occurrence weighting (used in associative networks), weighted MaxSAT (clause weights), and sensitivity/robustness analysis (perturbation of weights). While each component appears separately in literature, their tight integration—using Hebbian updates to initialize clause weights, then evaluating satisfaction and its sensitivity within a pure‑Python SAT solver—has not been reported as a unified scoring mechanism for reasoning answer evaluation.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and robustness, though limited to Boolean abstractions.  
Metacognition: 6/10 — sensitivity provides a crude stability signal but no explicit self‑monitoring.  
Hypothesis generation: 5/10 — generates implicit hypotheses via clause satisfaction but lacks generative search.  
Implementability: 9/10 — relies only on regex, numpy for matrix ops, and a short DPLL solver; feasible in <200 lines.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

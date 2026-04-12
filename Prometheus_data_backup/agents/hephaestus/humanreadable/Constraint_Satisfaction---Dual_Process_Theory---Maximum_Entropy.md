# Constraint Satisfaction + Dual Process Theory + Maximum Entropy

**Fields**: Computer Science, Cognitive Science, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T10:31:25.472292
**Report Generated**: 2026-03-31T18:53:00.554600

---

## Nous Analysis

**Algorithm**  
We build a hybrid scorer that treats each prompt‑candidate pair as a small Constraint Satisfaction Problem (CSP) whose variables are propositional atoms extracted from the text.  

1. **Fast System 1 preprocessing (regex‑based)** – Using only the Python `re` module we scan the prompt and each candidate answer for:  
   * atomic propositions (e.g., “X is Y”, “X > 5”)  
   * negations (`not`, `no`)  
   * comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`)  
   * conditionals (`if … then …`, `unless`)  
   * causal cues (`because`, `leads to`)  
   * ordering relations (`before`, `after`, `first`, `last`)  
   * numeric constants.  
   Each match yields a literal (possibly negated) and, for comparatives/numerics, a linear inequality over a numeric variable. All literals are stored in a list `L`; each inequality is stored as a tuple `(var, op, bound)`.

2. **Slow System 2 constraint propagation** – We construct a CSP:  
   * Boolean variables for each literal (True = literal holds).  
   * Clauses derived from conditionals (e.g., `if A then B` → `¬A ∨ B`).  
   * Transitivity constraints for ordering (e.g., `X < Y ∧ Y < Z → X < Z`).  
   * Arc‑consistency (AC‑3) is run to prune impossible literal assignments; the remaining domains are stored as bit‑sets in a NumPy array `domains.shape = (n_literals, 2)`.  
   * Numeric inequalities are collected into a matrix `A·x ≤ b` and solved with a simple feasibility check (e.g., Fourier‑Motzkin elimination using NumPy) to obtain a feasible region for each numeric variable.

3. **Maximum‑Entropy scoring** – From the feasible CSP we define a set of binary features `f_i(assignment)`: each literal’s truth value, each satisfied clause, and each numeric bound tightness. We learn a log‑linear model (no training data needed) by assigning equal weight to all features that are *consistent* with the CSP (maximum entropy principle). The score of a candidate answer is the probability that its associated literal(s) are true under the max‑ent distribution:  

   \[
   s = \frac{\exp\big(\sum_i w_i f_i(\hat{a})\big)}{\sum_{a' \in \mathcal{A}} \exp\big(\sum_i w_i f_i(a')\big)},
   \]  

   where `\mathcal{A}` is the set of all assignments surviving arc‑consistency and numeric feasibility, and `w_i = 1` for each feature that is not ruled out by the CSP. The denominator is computed by enumerating the (typically small) solution space using backtracking with the pruned domains.

**Parsed structural features** – negations, comparatives, conditionals, numeric values, causal claims, ordering relations, and simple conjunctive/disjunctive combinations thereof.

**Novelty** – The combination mirrors probabilistic soft logic and Markov Logic Networks but replaces weighted rule learning with a pure max‑ent distribution derived directly from arc‑consistency and numeric feasibility, using only NumPy and the stdlib. No prior public tool combines these three exact components in this way.

**Ratings**  
Reasoning: 8/10 — The CSP + max‑ent core captures logical deduction and uncertainty well, though scalability beyond short texts is limited.  
Metacognition: 6/10 — System 1/System 2 split offers a rudimentary reflection on fast vs. slow processing, but no explicit self‑monitoring of search depth.  
Hypothesis generation: 7/10 — Arc‑consistency yields a set of viable worlds; sampling from the max‑ent distribution can generate alternative hypotheses.  
Implementability: 9/10 — All steps rely on regex, NumPy arrays, and basic backtracking; no external libraries or APIs are needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T18:51:10.110086

---

## Code

*No code was produced for this combination.*

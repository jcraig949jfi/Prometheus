# Hebbian Learning + Compositional Semantics + Satisfiability

**Fields**: Neuroscience, Philosophy, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:55:49.697127
**Report Generated**: 2026-03-31T14:34:55.659585

---

## Nous Analysis

**Algorithm**  
We build a weighted constraint graph whose nodes are atomic propositions extracted from the prompt and each candidate answer. Parsing uses deterministic regex patterns to capture:  
- Negations (`not`, `never`) → literal `¬p`  
- Comparatives (`>`, `<`, `≥`, `≤`, `=`) → arithmetic atoms `x > 5` etc.  
- Conditionals (`if … then …`) → implication `p → q`  
- Ordering/temporal (`before`, `after`) → precedence atoms `t1 < t2`  
- Causal (`because`, `leads to`) → causal implication `p → q` (treated like conditionals)  
- Numeric constants → grounded terms.

Each parsed fragment yields a clause in conjunctive normal form (CNF). For example, “If A then not B” becomes the clause `¬A ∨ ¬B`. All clauses from the prompt form a base theory **T**. For a candidate answer **C**, we add its clauses to obtain **T ∪ C**.

**Hebbian learning component**  
We maintain a symmetric weight matrix **W** (numpy array) indexed by proposition IDs. Initially **W** = 0. When a satisfying assignment for **T ∪ C** is found (via a simple DPLL‑style SAT solver using only Python lists and numpy for unit‑propagation), we increment **W[i,j]** for every pair of propositions (i,j) that are both true in that assignment. This implements “neurons that fire together wire together”: co‑occurring literals in satisfying models strengthen their link.

**Scoring logic**  
After processing all candidates, the score of a candidate **C** is the sum of weights of propositions that are true in its *best* satisfying assignment (the one with maximal total weight). Formally:  

```
score(C) = max_{α ⊨ T∪C} Σ_{p_i true in α} Σ_j W[i,j]
```

If **T∪C** is unsatisfiable, score = –∞ (or a large negative penalty). Higher scores indicate answers whose propositions are mutually supportive according to the Hebbian‑learned coherence of the prompt.

**Structural features parsed**  
Negations, comparatives, conditionals, ordering/temporal relations, causal claims, numeric constants, and equality/inequality predicates.

**Novelty**  
The approach combines compositional semantic parsing into logical clauses, a Hebbian‑style co‑occurrence weight update, and weighted MAXSAT‑style scoring. While each piece exists separately (weighted MAXSAT, Hebbian learning in neural nets, semantic parsing), their conjunction as a pure‑numpy, rule‑based scorer for answer selection is not commonly reported in the literature.

**Rating**  
Reasoning: 7/10 — handles logical structure well but struggles with vague or world‑knowledge‑rich language.  
Metacognition: 5/10 — limited self‑monitoring; no explicit confidence estimation beyond SAT outcome.  
Hypothesis generation: 6/10 — can explore alternative assignments via weight‑guided search, yet generation is constrained to the clause space.  
Implementability: 8/10 — relies only on regex, numpy arrays, and a basic DPLL solver; straightforward to code and debug.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

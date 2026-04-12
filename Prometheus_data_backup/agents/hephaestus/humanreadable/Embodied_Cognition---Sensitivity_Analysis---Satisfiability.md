# Embodied Cognition + Sensitivity Analysis + Satisfiability

**Fields**: Cognitive Science, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:31:05.350490
**Report Generated**: 2026-04-02T04:20:11.705042

---

## Nous Analysis

The algorithm builds a lightweight constraint‑satisfaction model from the text, then evaluates each candidate answer by measuring how robustly the model stays satisfiable under small perturbations of its grounded parameters.

**Data structures**  
- `Var`: a symbol with a domain (`bool` for propositions, `float` interval for quantities).  
- `Literal`: `(var, sign)` where `sign` is `+1` (positive) or `-1` (negated).  
- `Clause`: a frozenset of literals (CNF clause).  
- `Formula`: list of clauses.  
- `Grounding`: dict mapping each numeric variable to a concrete value extracted from the prompt or answer.

**Parsing (structural features)**  
Regex patterns extract:  
1. Negations (`not`, `no`, `-`).  
2. Comparatives (`>`, `<`, `>=`, `<=`, `==`, `!=`) producing numeric literals like `(size > 5)`.  
3. Conditionals (`if … then …`) → implication encoded as `(¬A ∨ B)`.  
4. Causal cue words (`because`, `leads to`, `results in`) → same as conditionals.  
5. Ordering/temporal markers (`before`, `after`, `first`, `last`) → numeric timestamps or ordinal vars.  
6. Plain propositions (`the light is on`) → boolean vars.

Each extracted atom becomes a variable; its polarity determines the literal sign. The resulting CNF formula captures the logical backbone of the prompt.

**Scoring logic**  
For a candidate answer:  
1. Ground any numeric variables mentioned in the answer (e.g., “the weight is 7kg”).  
2. Run a DPLL SAT solver (pure Python, using unit propagation and pure‑literal elimination) to test satisfiability. If unsat, compute a minimal unsatisfiable core (MUC) by repeatedly dropping clauses and checking sat; the core size `c` yields a penalty `p = c / |Formula|`.  
3. Perform sensitivity analysis: perturb each grounded numeric value by ±ε (ε = 1% of its range) and re‑run the SAT test. Let `s` be the fraction of perturbations that keep the formula satisfiable.  
4. Final score = `s * (1 - p)`. Answers that satisfy the prompt under many small variations and produce small unsat cores receive higher scores.

This combines embodied grounding (variables tied to perceptible quantities), sensitivity analysis (robustness to input noise), and satisfiability checking (logical consistency).

**Novelty**  
Pure SAT‑based QA exists, and sensitivity analysis is common in scientific modeling, but coupling them with explicit embodied variable extraction (numeric/comparative grounding from language) and using the MUC size as a direct penalty is not documented in current reasoning‑evaluation tools.

**Rating**  
Reasoning: 8/10 — The method captures logical structure and quantifies robustness, giving a principled, explainable score.  
Metacognition: 6/10 — It can detect when an answer is fragile (low sensitivity) but does not explicitly reason about its own reasoning process.  
Hypothesis generation: 5/10 — The solver can propose alternative assignments that satisfy constraints, yet it does not prioritize novel hypotheses beyond model completion.  
Implementability: 9/10 — Only regex, basic data structures, and a pure‑Python DPLL solver are needed; no external libraries beyond numpy (used for interval handling).

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

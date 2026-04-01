# Falsificationism + Compositionality + Sensitivity Analysis

**Fields**: Philosophy, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T11:39:33.865962
**Report Generated**: 2026-03-31T18:05:52.678535

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Use regex‑based patterns to extract atomic propositions from the prompt and each candidate answer:  
   - Literals: `X is Y`, `X > Y`, `X causes Y`, `if X then Y`.  
   - Connectives: `and`, `or`, `not`.  
   Build a binary parse tree where each node stores its operator and child references; leaves are literals with attached type tags (comparison, causal, conditional).  
2. **Falsification‑driven scoring** – For a candidate, generate a set of *falsification probes* by systematically negating each leaf literal (inserting `not` or flipping a comparator) and, for numeric literals, perturbing the value by ±ε (ε = 1 % of the range observed in the prompt). Each probe yields a modified answer tree.  
3. **Constraint propagation (Sensitivity Analysis)** – Treat the prompt as a knowledge base of Horn‑style clauses derived similarly (e.g., “if A then B” → ¬A ∨ B). Run unit‑propagation on the combined set (prompt clauses ∧ answer tree) to detect contradictions.  
   - **Consistency score** = 1 if no contradiction, 0 otherwise.  
   - **Sensitivity penalty** = (number of probes that flip the consistency score) / (total probes).  
4. **Final score** = Consistency score – λ · Sensitivity penalty (λ = 0.5 to balance robustness). Higher scores indicate answers that are both supported by the prompt and resistant to small perturbations.

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`>`, `<`, `≥`, `≤`, `equals`), conditionals (`if … then …`, `unless`), causal cues (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `more than`), numeric values and units, conjunction/disjunction markers, and quantifier phrases (`all`, `some`, `none`). These are captured directly by the regex patterns that feed the parse tree.

**Novelty**  
While compositional parsing and constraint propagation appear in semantic‑parsing and logic‑based QA systems, explicitly coupling them with a Popperian falsification loop and a sensitivity‑analysis penalty is not standard in existing open‑source reasoning evaluators. The approach resembles robustness‑checking in probabilistic programming but operates purely on symbolic structures, making it a novel combination for answer scoring.

**Ratings**  
Reasoning: 7/10 — captures logical consistency and robustness but lacks deeper causal reasoning.  
Metacognition: 5/10 — the method does not monitor its own uncertainty beyond sensitivity counts.  
Hypothesis generation: 6/10 — falsification probes act as generated counter‑hypotheses, though limited to local perturbations.  
Implementability: 8/10 — relies only on regex, basic tree structures, and numpy for numeric ε; fully doable in stdlib + numpy.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T18:05:36.487288

---

## Code

*No code was produced for this combination.*

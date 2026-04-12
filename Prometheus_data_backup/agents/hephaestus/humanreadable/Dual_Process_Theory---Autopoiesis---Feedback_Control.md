# Dual Process Theory + Autopoiesis + Feedback Control

**Fields**: Cognitive Science, Complex Systems, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T10:08:33.685083
**Report Generated**: 2026-03-31T14:34:55.943915

---

## Nous Analysis

**Algorithm**  
The scorer works in two coupled stages that mirror System 1 (fast) and System 2 (slow) while maintaining an autopoietic closure through feedback control.

1. **Data structures**  
   - `props`: list of atomic propositions extracted from the prompt and each candidate answer (strings).  
   - `R`: `numpy.ndarray` of shape `(n_props, n_props)` representing directed relational weights (initial 0).  
   - `b`: `numpy.ndarray` of shape `(n_props,)` holding current belief scores (initial 0).  
   - `gains`: `numpy.ndarray` diagonal matrix `K·I` (scalar gain `K`).  
   - `target`: `numpy.ndarray` indicating which propositions should be true for a given answer (1 for propositions present in the candidate, 0 otherwise).

2. **System 1 – Fast heuristic extraction**  
   - Apply a handful of regex patterns to the raw text to capture:  
     *Negations* (`\bnot\b|\bno\b`), *comparatives* (`\bmore\s+than\b|\bless\s+than\b|\bgreater\s+than\b`), *conditionals* (`\bif\s+.+?\bthen\b`), *causal* (`\bbecause\b|\bleads\s+to\b|\bresults\s+in\b`), *numeric* (`\d+(\.\d+)?\s*[a-zA-Z]+`), *ordering* (`\bbefore\b|\bafter\b|\bearlier\b|\blater\b`).  
   - For each detected relation, create a directed edge `i → j` in `R` with weight `+1` for entailment‑like cues (conditional forward, comparative “more than”, causal “leads to”) and `-1` for contradiction‑like cues (negation flips the sign of the target proposition, comparative “less than”, causal “prevents”).  
   - Initialize `b` with `+1` for propositions appearing unnegated, `-1` for those appearing under a negation, and `0` otherwise.

3. **System 2 – Slow deliberate feedback loop**  
   - Compute consistency error: `e = target - (R @ b)`.  
   - Update beliefs via discrete‑time feedback: `b_new = b + gains @ e`.  
   - Repeat until `‖b_new - b‖₂ < ε` (e.g., 1e‑3) or a max of 20 iterations.  
   - The final belief vector `b*` represents a self‑producing (autopoietic) fixed point where the internal model reproduces the observed relational structure.

4. **Scoring**  
   - For each candidate answer, compute similarity `s = (b* · target) / (‖b*‖·‖target‖)`.  
   - Return `s` as the reasoned score (higher = better alignment with extracted logical structure).

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values with units, and temporal/ordering relations.

**Novelty** – While belief propagation and constraint‑satisfaction models exist, the explicit bifurcation into a fast heuristic graph builder and a slow feedback‑driven autopoietic fixer, implemented with only regex and NumPy, is not common in existing text‑scoring tools.

**Ratings**  
Reasoning: 8/10 — captures logical dependencies and enforces global consistency through iterative feedback.  
Metacognition: 6/10 — limited to error‑signal monitoring; no higher‑level reflection on strategy.  
Hypothesis generation: 5/10 — generates implicit alternative belief states via edge weights but does not produce explicit competing explanations.  
Implementability: 9/10 — relies solely on regex, NumPy arrays, and basic linear algebra; straightforward to code and test.

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

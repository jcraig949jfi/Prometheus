# Metacognition + Hebbian Learning + Compositionality

**Fields**: Cognitive Science, Neuroscience, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T00:45:30.841688
**Report Generated**: 2026-03-31T16:34:28.480452

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Using only `re` we extract atomic propositions from the prompt and each candidate answer. An atom is a tuple `(predicate, arg1, arg2?, polarity)` where polarity captures negation (`¬`). Comparatives (`>`, `<`, `=`), conditionals (`if … then`), causal markers (`because`, `leads to`) and ordering terms (`before`, `after`) are turned into special predicate names (e.g., `GT`, `IF`, `CAUSE`, `BEFORE`).  
2. **Data structures** –  
   * `atoms`: list of unique atom strings observed in the prompt + all candidates.  
   * `P`: binary numpy vector (shape |atoms|) indicating which atoms appear in the prompt.  
   * `C_i`: binary vector for candidate *i*.  
   * `W`: weight matrix (|atoms| × |atoms|) initialized to zero; encodes compositional links.  
   * `R`: fixed rule matrix (same shape) that implements simple logical constraints (transitivity for `GT`, `BEFORE`; modus ponens for `IF`).  
3. **Hebbian update** – For each candidate we compute an outer‑product update  
   ```
   eta = 0.1
   W += eta * (P[:, None] * C_i[None, :])
   ```  
   This strengthens connections between prompt atoms and candidate atoms that co‑occur, mimicking activity‑dependent synaptic strengthening.  
4. **Compositional similarity** – Score_raw = `P @ W @ C_i` (a scalar). This captures the meaning of the whole as weighted sum of part‑wise interactions (Frege’s principle).  
5. **Metacognitive confidence** – Apply the rule matrix to detect violations:  
   ```
   violation = np.maximum(0, R @ C_i - C_i)   # e.g., if GT says A>B and B>C but not A>C
   consistency = 1 - np.linalg.norm(violation) / (np.linalg.norm(C_i) + 1e-8)
   confidence = np.exp(-2.0 * (1 - consistency))   # maps 0→1
   ```  
   Confidence reflects error monitoring and strategy selection (metacognition).  
6. **Final score** – `score_i = score_raw * confidence`. Higher scores indicate answers that are both compositionally aligned with the prompt and internally consistent.

**Structural features parsed** – atomic predicates, negations, comparatives (`>`, `<`, `=`), conditionals (`if … then`), causal markers (`because`, `leads to`), temporal ordering (`before`, `after`), numeric values (converted to atoms like `NUM_5`).  

**Novelty** – Purely algorithmic QA systems often rely on bag‑of‑words or string similarity. Combining Hebbian‑style co‑occurrence weighting with explicit compositional similarity and a metacognitive confidence module is not standard in the literature; while semantic networks with Hebbian learning exist (e.g., HAL), the added constraint‑propagation confidence layer is novel.

**Ratings**  
Reasoning: 8/10 — captures logical structure and numeric relations but limited to shallow rule set.  
Metacognition: 7/10 — provides a principled confidence signal via violation norm, though simplistic.  
Hypothesis generation: 6/10 — edge weights suggest implicit hypotheses; generation is indirect.  
Implementability: 9/10 — uses only `numpy` and `re`; clear matrix operations and regex parsing.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
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

**Forge Timestamp**: 2026-03-31T16:33:14.193226

---

## Code

*No code was produced for this combination.*

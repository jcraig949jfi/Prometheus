# Pragmatics + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Linguistics, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:58:17.880982
**Report Generated**: 2026-04-02T04:20:11.847038

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only the Python `re` module we extract a set of atomic propositions from a prompt and each candidate answer.  
   - Patterns capture:  
     * Negations (`not`, `no`, `-n't`) → polarity = ‑1.  
     * Quantifiers (`all`, `some`, `most`, `few`) → weight = 1.0, 0.5, 0.75, 0.25.  
     * Comparatives (`greater than`, `less than`, `≥`, `≤`) → relation type = `cmp`.  
     * Conditionals (`if … then …`) → relation type = `cond`.  
     * Causal cues (`because`, `causes`, `leads to`) → relation type = `cause`.  
     * Ordering (`before`, `after`, `first`, `last`) → relation type = `order`.  
   - Each proposition is stored as a tuple `(rel, arg1, arg2, polarity, weight)` and appended to a list `props`.  
   - The list is converted to a NumPy structured array `P` of shape `(n,)` with fields `rel_id` (int), `arg1_id`, `arg2_id` (int via a hash‑map of seen tokens), `pol` (‑1/1), `wt` (float).  

2. **Similarity via NCD** –  
   - Serialize `P` to a byte string using `P.tobytes()`.  
   - Compute compressed lengths with `zlib.compress`: `Cx = len(zlib.compress(Px))`, `Cy` for reference, `Cxy = len(zlib.compress(np.concatenate([Px, Py])))`.  
   - Normalized Compression Distance: `NCD = (Cxy - min(Cx, Cy)) / max(Cx, Cy)`.  

3. **Sensitivity‑analysis penalty** –  
   - For each proposition `i` in `Px` create a perturbed copy `Px⁽ⁱ⁾` by flipping one pragmatic feature:  
     * toggle polarity (`pol *= -1`),  
     * replace weight with the next quantifier level (e.g., `some → most`),  
     * invert a conditional antecedent/consequent,  
     * negate a causal cue.  
   - Re‑compute NCD for each perturbed version → array `NCD_pert`.  
   - Sensitivity score `Sens = np.std(NCD_pert)`.  

4. **Final score** –  
   `Score = 1 - NCD - λ * Sens` (with λ = 0.2 tuned on a validation set). Higher scores indicate answers that are both semantically close (low NCD) and robust to pragmatic perturbations (low Sens). All steps use only `re`, `zlib`, `numpy`, and the standard library.

**Structural features parsed**  
Negations, quantifiers, comparatives, conditionals, causal connectives, and temporal/ordering markers. These are the literal triggers of Gricean maxims (quantity, relevance, manner) and thus the pragmatic layer the algorithm respects.

**Novelty**  
The combination is not found in existing surveys: most NCD‑based text similarity works ignore pragmatic perturbations, and sensitivity analysis in NLP usually targets model parameters, not discrete logical features. By explicitly generating proposition‑level perturbations and measuring their impact on a compression‑based distance, the method bridges pragmatics, information‑theoretic similarity, and robustness testing—a novel, model‑free scoring scheme.

**Rating**  
Reasoning: 7/10 — captures logical structure and pragmatic nuance but relies on shallow regex parsing, limiting deep inference.  
Metacognition: 6/10 — provides a self‑check via sensitivity variance, yet offers no explicit uncertainty calibration beyond variance.  
Hypothesis generation: 5/10 — the algorithm scores given candidates; it does not propose new answers or explore alternative interpretations.  
Implementability: 9/10 — uses only `re`, `zlib`, `numpy`; all operations are straightforward and run in milliseconds on modest data.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
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

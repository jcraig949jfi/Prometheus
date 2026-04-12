# Fractal Geometry + Pragmatics + Sensitivity Analysis

**Fields**: Mathematics, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T20:32:41.731384
**Report Generated**: 2026-03-27T06:37:40.065703

---

## Nous Analysis

**Algorithm: Fractal‑Pragmatic Sensitivity Scorer (FPSS)**  

1. **Data structures**  
   - `clauses`: list of dicts, each representing a clause extracted from the answer.  
     ```python
     {
         'text': str,               # raw clause string
         'depth': int,              # nesting level (0 = main clause)
         'polarity': float,         # +1 for affirmative, -1 for negation
         'prag_weight': float,      # 0‑1 score from Grice maxim analysis
         'num_vars': list[float],   # numeric constants found in the clause
         'relations': list[tuple]   # (type, target_clause_idx) e.g., ('implies', 2)
     }
     ```
   - `W`: numpy array of shape `(n_clauses,)` holding the final clause scores.  

2. **Parsing (regex‑based structural extraction)**  
   - Split text into sentences (`re.split(r'[.!?]+')`).  
   - For each sentence, detect subordinate clauses via patterns for commas, conjunctions, and relative pronouns (`re.findall(r'[^,;]*\b(?:that|which|if|because|when)\b[^,;]*[;,]?')`).  
   - Assign `depth` by counting how many enclosing patterns a clause lies inside (power‑law scaling: `fractal_factor = 2**(-depth)`).  
   - Extract polarity (`'not', 'no', 'never'` → -1).  
   - Extract numeric values (`re.findall(r'\b\d+(\.\d+)?\b')`).  
   - Detect relations:  
     * Implication/causality (`if … then`, `because`, `leads to`) → `('implies', target)`.  
     * Ordering/comparison (`greater than`, `before`, `more than`) → `('order', target)`.  
     * Contrast (`but`, `however`) → `('contrast', target)`.  

3. **Pragmatic weighting**  
   - For each clause count violations of Grice’s maxims using keyword lists:  
     * Quantity: too few/more info words (`'some', 'many', 'all'`).  
     * Relevance: presence of off‑topic cue (`'by the way', 'anyway'`).  
     * Manner: vague terms (`'stuff', 'things'`).  
   - `prag_score = 1 - (violations / max_violations)`, clipped to `[0,1]`.  

4. **Sensitivity analysis**  
   - For each numeric variable `v` in a clause, compute a finite‑difference effect on a simple truth heuristic:  
     - If the clause contains a comparison (`>`, `<`, `=`), evaluate truth with `v` and with `v+ε` (`ε=1e-3`).  
     - `delta = |truth(v+ε) - truth(v)|`.  
   - Clause sensitivity `s = sum(delta) * fractal_factor`.  
   - Normalize across clauses: `s_norm = s / (s.max()+1e-9)`.  

5. **Scoring logic**  
   - Base score per clause: `base = prag_weight * fractal_factor`.  
   - Penalize sensitivity: `W[i] = base * (1 - s_norm[i])`.  
   - Final answer score = `W.mean()` (higher = more robust, context‑appropriate, and structurally sound).  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering/temporal relations, numeric constants, quantifiers, discourse markers.  

**Novelty** – While discourse parsing, pragmatic annotation, and sensitivity analysis exist separately, FPSS uniquely combines a fractal depth‑based scaling of clause hierarchy with pragmatic implicature weights and numeric perturbation sensitivity in a single deterministic scoring function. No prior work layers all three mechanisms for answer evaluation.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and context but relies on shallow heuristics for truth.  
Metacognition: 5/10 — limited self‑reflection; no explicit monitoring of internal consistency beyond sensitivity.  
Hypothesis generation: 6/10 — perturbations generate alternative numeric interpretations, but no higher‑order hypothesis search.  
Implementability: 8/10 — uses only regex, numpy, and stdlib; straightforward to code and debug.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Fractal Geometry**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Fractal Geometry + Pragmatics: negative interaction (-0.060). Keep these concepts in separate code paths to avoid interference.

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

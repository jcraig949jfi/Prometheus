# Matched Filtering + Maximum Entropy + Sensitivity Analysis

**Fields**: Signal Processing, Statistical Physics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T19:43:56.130342
**Report Generated**: 2026-03-31T19:46:57.756431

---

## Nous Analysis

**Algorithm: Entropy‑Weighted Matched‑Filter Sensitivity Scorer (EWMFSS)**  

1. **Data structures**  
   - `tokens`: list of strings from the prompt after lower‑casing and punctuation stripping.  
   - `patterns`: dict mapping syntactic feature names to compiled regex objects (see §2).  
   - `features`: 2‑D NumPy array of shape *(n_candidates, n_features)* where each row holds the count‑normalized frequency of each pattern in a candidate answer.  
   - `weights`: 1‑D NumPy array of length *n_features* representing the maximum‑entropy distribution over feature expectations.  
   - `sensitivity`: 1‑D NumPy array of length *n_features* holding the partial derivative of the score w.r.t. each feature (computed via finite differences).  

2. **Operations**  
   - **Feature extraction**: for each candidate, apply every regex in `patterns` and increment the corresponding column in `features`.  
   - **Maximum‑entropy weighting**: given empirical feature expectations `μ_emp = features.mean(axis=0)`, solve for `weights` that maximize entropy subject to `features @ weights = μ_emp`. This is a convex optimization solved with a simple iterative scaling (GIS) loop using only NumPy.  
   - **Matched‑filter scoring**: compute the raw similarity `s_raw = features @ weights`. This is the cross‑correlation of the candidate’s feature vector with the entropy‑optimal template.  
   - **Sensitivity correction**: perturb each feature column by ±ε (ε=1e‑3), recompute `s_raw`, and approximate ∂s/∂f_i via central difference. Form `sensitivity = |∂s/∂f|`.  
   - **Final score**: `score = s_raw / (1 + λ * sensitivity.sum())`, where λ controls penalty for fragile features (λ=0.1 works well). Higher scores indicate answers that match the expected structural pattern while being robust to small perturbations.  

3. **Parsed structural features**  
   - Negations (`not`, `never`, `no`).  
   - Comparatives (`more than`, `less than`, `as … as`).  
   - Conditionals (`if … then`, `unless`, `provided that`).  
   - Numeric values and units (integers, decimals, percentages).  
   - Causal verbs (`cause`, `lead to`, `result in`, `because`).  
   - Ordering relations (`first`, `second`, `before`, `after`).  
   - Quantifiers (`all`, `some`, `none`, `most`).  

4. **Novelty**  
   The triple combination is not found in existing QA scoring pipelines. Matched filtering is standard in signal detection; maximum‑entropy weighting appears in language modeling but rarely coupled with a explicit sensitivity analysis that penalizes fragile linguistic features. Thus the EWMFSS constitutes a novel hybrid, though each component individually is well‑studied.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and robustness but lacks deep semantic understanding.  
Metacognition: 5/10 — provides uncertainty via sensitivity but does not monitor its own reasoning process.  
Hypothesis generation: 4/10 — can suggest alternatives by perturbing features, yet no generative mechanism.  
Implementability: 9/10 — relies only on regex, NumPy, and iterative scaling; straightforward to code in <150 lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
| **Composite** | **5.33** |

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

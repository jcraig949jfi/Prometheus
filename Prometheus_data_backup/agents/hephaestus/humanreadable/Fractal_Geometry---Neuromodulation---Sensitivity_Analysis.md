# Fractal Geometry + Neuromodulation + Sensitivity Analysis

**Fields**: Mathematics, Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T14:30:26.475381
**Report Generated**: 2026-03-31T17:08:00.617719

---

## Nous Analysis

The algorithm builds a multi‑scale proposition graph from the prompt and each candidate answer, then scores the answer by measuring how stably its graph responds to tiny perturbations while applying neuromodulatory gain control.

1. **Data structures**  
   - `nodes`: list of dictionaries `{id, text, type}` where `type` ∈ {fact, neg, comp, cond, caus, order, num}.  
   - `adj`: sparse adjacency matrix (numpy `csr_matrix`) representing directed logical links extracted by regex (e.g., “if X then Y” → edge X→Y).  
   - `scale_factors`: geometric series `s**l` for levels `l=0…L-1` with fractal ratio `s∈(0,1)` (e.g., 0.5).  
   - `modulators`: numpy array `[DA, 5‑HT]` computed per node: DA ↑ if node contains reward‑related cue (“gain”, “benefit”), 5‑HT ↑ if node contains uncertainty cue (“maybe”, “could”).  
   - `weights`: numpy array of node activations, initialized to 1.0.

2. **Operations**  
   - **Parsing**: regex extracts negation (“not”), comparative (“more than”, “less than”), conditional (“if … then”), causal (“because”, “leads to”), ordering (“before”, “after”), and numeric tokens; each creates a node and appropriate edges.  
   - **Fractal scaling**: for each scale `l`, compute `adj_l = (s**l) * adj`; stack to get a 3‑D tensor `adj_stack (L, N, N)`.  
   - **Neuromodulation gain**: `gain = 1 + w_DA*DA + w_5HT*5‑HT` (weights `w_DA, w_5HT` set to 0.2); update node weights: `weights_l = weights * gain` (broadcast over nodes).  
   - **Score propagation**: compute activation vector `a_l = (I - adj_l.T)^-1 @ weights_l` (using numpy.linalg.solve for stability).  
   - **Sensitivity analysis**: perturb each input feature (presence/negation of a token) by ε=1e‑3, recompute `a_l`, finite‑difference gradient `g_l = (a_l^+ - a_l^-)/(2ε)`. Compute robustness penalty `R = exp(-λ * ||g_l||_2)` with λ=0.5.  
   - **Final score**: average over scales `S = (1/L) Σ_l (||a_l||_1 * R_l)`. Higher `S` indicates coherent, robust reasoning.

3. **Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values, quantifiers, and conjunctions; each yields a typed node and directed edge.

4. **Novelty** – While fractal graph scaling, neuromodulatory gain, and sensitivity‑based robustness appear separately in semantic parsing, uncertainty estimation, and model‑checking literature, their conjunction into a single scoring pipeline that iteratively refines logical structure across scales while adjusting gain via neurotransmitter‑like signals and penalizing fragile derivations has not been reported in existing QA evaluation tools.

**Ratings**  
Reasoning: 8/10 — captures multi‑scale logical coherence and robustness via concrete matrix operations.  
Metacognition: 6/10 — provides a stability signal but lacks explicit self‑reflection on its own assumptions.  
Hypothesis generation: 7/10 — alternative scales naturally generate competing interpretations to evaluate.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and standard containers; no external APIs needed.

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

**Forge Timestamp**: 2026-03-31T17:05:57.575997

---

## Code

*No code was produced for this combination.*

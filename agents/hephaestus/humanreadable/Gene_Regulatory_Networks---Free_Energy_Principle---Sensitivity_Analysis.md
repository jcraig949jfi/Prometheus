# Gene Regulatory Networks + Free Energy Principle + Sensitivity Analysis

**Fields**: Biology, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T18:52:09.020917
**Report Generated**: 2026-03-27T23:28:38.459718

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Triples** – Use regex to extract subject‑predicate‑object triples from the prompt and each candidate answer. Patterns capture:  
   - Negations (`not`, `no`, `never`) → predicate flag `neg=1`  
   - Comparatives (`more than`, `less than`, `>`, `<`) → numeric relation flag  
   - Conditionals (`if … then …`) → conditional flag  
   - Causal claims (`because`, `leads to`, `causes`) → causal flag  
   - Numeric values and ordering (`>`, `<`, `before`, `after`).  
   Each triple becomes a node with attributes `(type, polarity, numeric?)`.

2. **Gene Regulatory Network (GRN) construction** – Build a directed bipartite graph **G** = (Vₚ ∪ Vc, E) where Vₚ are prompt triples, Vc are candidate triples. An edge *e* = (pᵢ → cⱼ) exists if the subjects share ≥ 50 % token overlap (Jaccard) **or** objects share ≥ 50 % overlap. Edge weight *w*ᵢⱼ = 1 if predicate polarity matches (both asserted or both negated), *w*ᵢⱼ = –1 if polarity mismatches (assertion vs. negation). Store **W** as an |Vₚ|×|Vc| numpy array.

3. **Free Energy approximation** – Treat the prompt as a generative model predicting edge activation μᵢⱼ = 1 for matching polarity, 0 otherwise. Prediction error εᵢⱼ = wᵢⱼ – μᵢⱼ. Precision (inverse variance) Πᵢⱼ is obtained via a cheap sensitivity analysis: perturb each token in the prompt by random synonym replacement (using a built‑in fallback list) 10 times, recompute *W*, and compute variance σ²ᵢⱼ of εᵢⱼ across perturbations; set Πᵢⱼ = 1/(σ²ᵢⱼ + 1e‑6). Free energy for a candidate is  
   \[
   F = \sum_{i,j} \Pi_{ij}\, \varepsilon_{ij}^2 .
   \]

4. **Scoring** – Convert free energy to a similarity score:  
   \[
   s = \exp(-F) .
   \]  
   Higher *s* indicates lower prediction error and greater robustness to input perturbations.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations (>, <, before/after).

**Novelty** – While GRN‑style graphs, free‑energy/predictive‑coding formulations, and sensitivity analysis each appear separately in cognitive modeling and robustness testing, their joint use as an explicit scoring pipeline for answer evaluation has not been reported in the literature; thus the combination is novel for this application.

**Rating**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on shallow similarity for edges.  
Metacognition: 6/10 — precision estimates give uncertainty awareness, yet are based on limited perturbations.  
Hypothesis generation: 4/10 — the method scores, does not generate new hypotheses.  
Implementability: 8/10 — uses only regex, numpy arrays, and basic loops; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.67** |

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

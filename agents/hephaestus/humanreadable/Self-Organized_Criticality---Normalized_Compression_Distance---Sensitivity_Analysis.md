# Self-Organized Criticality + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Complex Systems, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T08:55:50.998946
**Report Generated**: 2026-04-01T20:30:43.816117

---

## Nous Analysis

**Algorithm**  
1. **Parse** each candidate answer and a reference answer (e.g., a model solution) into a set of logical triples ⟨subject, relation, object⟩ using only regex patterns for:  
   - Negations (`not`, `no`, `never`) → relation prefixed with `¬`.  
   - Comparatives (`more`, `less`, `greater`, `lesser`) → relation `cmp`.  
   - Conditionals (`if … then …`, `when`) → relation `cond`.  
   - Causal verbs (`cause`, `lead to`, `result in`) → relation `cause`.  
   - Numeric values and units → attached as attributes to the object.  
   - Ordering/temporal words (`before`, `after`, `while`) → relation `ord`.  
   - Quantifiers (`all`, `some`, `none`) → relation `quant`.  
   The triples are stored in a list; a directed graph G is built where nodes are entities and edges carry the relation label.

2. **Baseline similarity** – Serialize G (e.g., sorted edge list → string) and compute the Normalized Compression Distance (NCD) to the reference graph G₀ using `zlib` as the compressor:  
   `NCD(G,G₀) = (C(G+G₀) - min(C(G),C(G₀))) / max(C(G),C(G₀))`.  
   Lower NCD indicates higher literal similarity.

3. **Sensitivity‑SOC analysis** – Generate a perturbation set P by applying single‑edge edits to G:  
   - Flip relation sign (add/remove `¬`).  
   - Replace a relation with another from the extracted set (e.g., `cause` → `cond`).  
   - Delete a node and its incident edges.  
   - Insert a spurious node with random relation.  
   For each p∈P compute NCD(Gₚ,G₀). Define an “avalanche” as the number of perturbations whose NCD increase exceeds a fixed ε (e.g., the 75th percentile of all NCD deltas). Collect avalanche sizes A over all perturbation types.

4. **Scoring** – Fit a power‑law to the histogram of A via linear regression on log‑log bins (using `numpy.linalg.lstsq`). Let R² be the goodness‑of‑fit and α the estimated exponent. Final score:  
   `Score = w₁·(1 - NCD_norm) + w₂·R²`, where `NCD_norm` rescales baseline NCD to [0,1] and weights (e.g., w₁=0.6, w₂=0.4) prioritize both similarity and critical‑like response. Answers that are close to the reference *and* produce a scale‑free avalanche distribution receive higher scores.

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, numeric values with units, ordering/temporal relations, quantifiers.

**Novelty**  
NCD is a known similarity metric; sensitivity analysis via input perturbations appears in robustness testing (e.g., CheckList); Self‑Organized Criticality has been used to model bursty behavior in networks. Joining them—using avalanche statistics of NCD changes under systematic logical perturbations to assess answer robustness—is not documented in existing QA or reasoning‑evaluation literature, making the combination novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and evaluates robustness via perturbation‑induced criticality.  
Metacognition: 5/10 — the method does not explicitly monitor or adjust its own reasoning process.  
Hypothesis generation: 4/10 — focuses on scoring given answers, not generating new hypotheses.  
Implementability: 8/10 — relies only on regex, `zlib`, and `numpy` for regression; all are in the standard library or numpy.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
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

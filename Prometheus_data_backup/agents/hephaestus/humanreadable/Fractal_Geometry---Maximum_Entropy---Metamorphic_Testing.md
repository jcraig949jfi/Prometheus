# Fractal Geometry + Maximum Entropy + Metamorphic Testing

**Fields**: Mathematics, Statistical Physics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T21:09:45.683654
**Report Generated**: 2026-03-27T23:28:38.573718

---

## Nous Analysis

The algorithm builds a multi‑scale logical graph from the prompt, assigns a least‑biased probability distribution to possible truth‑states using maximum‑entropy inference, and scores each candidate answer by its likelihood plus a metamorphic‑relation bonus.

**Data structures**  
1. **Sentence list** – raw strings from the prompt.  
2. **Predicate‑arg tuples** – extracted with regex patterns for:  
   * Negation: `\bnot\b`  
   * Comparative: `(\w+)\s+(is\s+)?(greater|less|more|fewer|higher|lower)\s+than\s+(\w+)`  
   * Conditional: `if\s+(.+?)\s+then\s+(.+)`  
   * Causal: `(\w+)\s+(causes?|leads\s+to|results\s+in)\s+(\w+)`  
   * Ordering: `(\w+)\s+(before|after|first|second)\s+(\w+)`  
   * Numeric: `(\d+(?:\.\d+)?)\s*([a-zA-Z]+)`  
   Each tuple becomes a node `(subject, predicate, object)` with a feature vector indicating which relation types it exhibits.  
3. **Hierarchical graph** – nodes are connected by edges labeled with the predicate type. Using a simple community‑detection heuristic (e.g., repeatedly merging nodes that share ≥2 edge types) we generate a fractal‑like decomposition: each level yields a subgraph whose edge‑type distribution mirrors the parent, enabling a box‑counting estimate of a Hausdorff‑dimension‑like scalar *D* at scales *s = 1,2,4,8…*.

**Operations**  
* **Constraint collection** – count observed occurrences *cₖ* of each relation type *k* across all scales.  
* **Maximum‑entropy distribution** – solve for probabilities *pᵢ* over possible truth‑assignments to nodes that maximize *H = -∑ pᵢ log pᵢ* subject to ∑ pᵢ fₖᵢ = cₖ / N (where *fₖᵢ* is the feature count of type *k* in assignment *i*). This is solved with iterative scaling (GIS) using only NumPy matrix ops.  
* **Answer likelihood** – for a candidate answer, extract its predicate‑arg tuple(s), compute its feature vector *fₐ*, and evaluate *log P(answer) = log ∑ᵢ pᵢ·𝟙[fₐ matches assignment i]*.  
* **Metamorphic‑relation test** – define MRs such as: if the answer contains a numeric value *v*, then the statement with *2v* must preserve any comparative ordering present in the prompt; if the answer asserts “X causes Y”, then swapping X and Y should violate a causal MR. Count satisfied MRs (*s*) and violated ones (*v*).  
* **Score** = log P(answer) + λ·s – μ·v (λ, μ tuned on a validation set).

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values with units, and equality statements.

**Novelty** – While maximum‑entropy reasoning (e.g., MaxEnt logistic regression) and fractal graph analysis exist separately, and metamorphic testing is used in software validation, their tight integration—using multi‑scale self‑similar graph constraints as the feature expectations for a MaxEnt distribution and then rewarding MR‑preserving answers—has not been reported in public reasoning‑evaluation tools.

**Ratings**  
Reasoning: 7/10 — captures relational structure and uncertainty but lacks deep semantic parsing.  
Metacognition: 5/10 — provides a self‑consistent entropy‑based confidence estimate yet offers limited introspection about its own uncertainties.  
Hypothesis generation: 6/10 — can sample alternative truth‑assignments from the MaxEnt distribution to propose rival explanations.  
Implementability: 8/10 — relies solely on NumPy for matrix iterations and stdlib regex; no external dependencies.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

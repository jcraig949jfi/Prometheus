# Fractal Geometry + Analogical Reasoning + Compositionality

**Fields**: Mathematics, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T08:22:43.570025
**Report Generated**: 2026-03-27T16:08:16.852262

---

## Nous Analysis

The algorithm builds a hierarchical predicate tree from each text using regex‑based extraction of logical atoms (negation, comparative, conditional, causal, ordering, numeric). Each atom becomes a node with fields: type (string), args (list of constants or sub‑nodes), children (list of child nodes). The tree is constructed recursively: a sentence → clauses → phrases → atoms, yielding a self‑similar structure where sub‑trees resemble the whole — this is the fractal‑geometry component.

To score a candidate answer against a reference answer, we perform an analogical structure‑mapping at every scale. For each depth d we collect the feature vectors of all nodes at that depth: a numpy array v = [one‑hot(type), normalized numeric args, boolean flags for negation/comparative/etc.]. We then compute a bidirectional Hausdorff distance H_d between the two sets {A_d,B_d} using Euclidean norm on v. The similarity at depth d is S_d = 1 − (H_d / (max_possible_distance)). Because deeper levels capture finer granularity, we weight them with a power‑law decay w_d = α·β^d (β < 1, e.g., 0.5) and α = 1 − β to keep Σw_d = 1. The final score is Σ_d w_d·S_d, a compositional aggregation of part‑wise similarities.

Parsed structural features include: negations (“not”, “no”), comparatives (“>”, “<”, “more than”, “less than”), conditionals (“if … then”, “unless”), causal markers (“because”, “leads to”, “causes”), ordering relations (“first”, “second”, “before”, “after”, ordinals), numeric values (integers, decimals, percentages), and quantifiers (“all”, “some”, “none”).

The combination is novel: while tree kernels and recursive neural nets exploit hierarchy, they lack an explicit fractal scaling law and Hausdorff‑style cross‑scale distance; pure analogical mapping (e.g., SME) does not compose similarity across scales with a principled power‑law weighting. Hence the triple fusion is not directly seen in prior art.

Reasoning: 7/10 — captures relational structure and scale‑aware similarity but relies on hand‑crafted regexes, limiting deep semantic nuance.  
Metacognition: 5/10 — the method has no self‑monitoring or uncertainty estimation; scores are deterministic given the parses.  
Hypothesis generation: 6/10 — can propose analogical transfers by matching sub‑trees, yet generation is constrained to observed patterns, not open‑ended invention.  
Implementability: 8/10 — uses only regex, numpy arrays, and recursion; no external libraries or training required, making it straightforward to code and test.

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

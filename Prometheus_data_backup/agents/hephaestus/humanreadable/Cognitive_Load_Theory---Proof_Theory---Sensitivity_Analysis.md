# Cognitive Load Theory + Proof Theory + Sensitivity Analysis

**Fields**: Cognitive Science, Mathematics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:51:12.275115
**Report Generated**: 2026-03-31T20:02:48.362856

---

## Nous Analysis

The algorithm treats each candidate answer as a set of logical chunks that must fit within a limited working‑memory buffer. First, a regex‑based extractor pulls atomic propositions and their logical connectives: negations (“not”, “no”), comparatives (“greater than”, “less than”, “=”), conditionals (“if … then …”, “unless”), causal markers (“because”, “leads to”, “results in”), and ordering/temporal terms (“before”, “after”, “precedes”). Each proposition becomes a node in a directed graph; an edge A→B is added when the text explicitly states an implication or causal relation (e.g., “If A then B”). Numeric values are parsed into separate nodes with attached magnitude attributes.

Next, the proof‑theoretic component normalizes the graph. Using a topological order, the algorithm applies cut‑elimination: if a path A→…→C exists and a direct edge A→C is present, the intermediate nodes are marked as redundant and removed, mimicking proof normalization. The remaining node count gives the **intrinsic load** (essential chunks). Nodes that are not on any path to the conclusion node are flagged as **extraneous load**. Edges that survive cut‑elimination and lie on at least one conclusion‑supporting path constitute the **germane load**.

Sensitivity analysis is then performed on the premise nodes. For each premise, its truth value is flipped (0↔1) while keeping all others fixed; the derivability of the conclusion is re‑checked via a simple forward‑chaining pass. The proportion of perturbations that still yield a valid conclusion is the **robustness score** R∈[0,1]. Sensitivity S = 1 − R.

Final score = (germane load / (intrinsic + extraneous + ε)) × R, where ε avoids division by zero. All quantities are stored as NumPy arrays; graph operations use adjacency matrices and vectorized traversals, requiring only NumPy and the Python standard library.

**Structural features parsed:** negations, comparatives, conditionals, causal claims, ordering/temporal relations, and explicit numeric values.

**Novelty:** While argument‑mining and proof‑tree scoring exist, the explicit integration of Cognitive Load Theory’s chunk‑based working‑memory bound, proof‑theoretic cut‑elimination, and sensitivity‑based robustness checking has not been combined in a publicly available reasoning‑evaluation tool. Existing systems either focus on similarity metrics or isolated logical formalisms, making this triple‑layer approach novel.

Reasoning: 8/10 — captures logical validity and robustness but relies on shallow linguistic cues.  
Metacognition: 6/10 — monitors load and redundancy, yet lacks explicit self‑reflection on strategy shifts.  
Hypothesis generation: 5/10 — excels at checking given hypotheses, weak at proposing new ones.  
Implementability: 9/10 — uses only regex, NumPy arrays, and graph traversals, all feasible in pure Python.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T20:01:49.389549

---

## Code

*No code was produced for this combination.*

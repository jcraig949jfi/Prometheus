# Network Science + Compositional Semantics + Sensitivity Analysis

**Fields**: Complex Systems, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T14:14:37.163080
**Report Generated**: 2026-03-27T16:08:16.511668

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer into a *labeled directed graph* \(G=(V,E)\).  
   - Nodes \(v_i\) store a token string and a type (entity, quantity, predicate).  
   - Edges \(e_{ij}\) store a relation label drawn from a fixed set: `neg`, `and`, `or`, `implies`, `greater-than`, `less-than`, `equals`, `causes`, `part-of`.  
   Extraction uses a handful of regex patterns (e.g., `(\w+)\s+is\s+not\s+(\w+)` → `neg`, `(\d+)\s*>\s*(\d+)` → `greater-than`).  
2. **Compositional semantics** assigns each node a *semantic vector* \(s(v)\in\{0,1\}^k\) where \(k\) is the number of distinct predicate symbols in the prompt; the vector is a one‑hot encoding of the predicate label attached to the node. Edge labels determine how vectors combine:  
   - `and` → logical AND (min), `or` → logical OR (max), `implies` → material implication (¬A ∨ B).  
   Propagation proceeds by a topological‑like sweep: for each node, compute its vector as the function of its in‑neighbors’ vectors according to the edge label. This yields a *truth‑value* \(t(v)\in[0,1]\) for every node.  
3. **Constraint satisfaction score** \(C\) = fraction of nodes whose computed \(t(v)\) matches the expected truth value dictated by the prompt (e.g., a candidate asserting “X > Y” must yield \(t(X)>t(Y)\)).  
4. **Sensitivity analysis**: generate \(N\) perturbed copies of the prompt by randomly flipping negation signs, adding/subtracting a small epsilon to numeric constants, or swapping the direction of comparative edges. For each copy recompute \(C_i\). Sensitivity \(S = \operatorname{std}(C_1…C_N)\).  
5. **Final score** for a candidate answer:  
   \[
   \text{Score}= C - \lambda \cdot S,
   \]  
   where \(\lambda\) (e.g., 0.2) penalizes answers whose truth is fragile under small input changes.

**Parsed structural features**  
- Negations (`not`, `no`)  
- Comparatives and superlatives (`greater than`, `less than`, `most`, `least`)  
- Conditionals (`if … then …`, `only if`)  
- Numeric values and arithmetic relations (`=`, `≠`, `>`, `<`)  
- Causal claims (`causes`, `leads to`, `results in`)  
- Ordering / precedence (`before`, `after`, `precedes`)  
- Conjunction/disjunction (`and`, `or`)  

**Novelty**  
Pure logical‑form scorers exist (e.g., theorem provers) and pure similarity scorers exist (e.g., TF‑IDF cosine). Few works combine a graph‑based compositional semantics engine with a Monte‑Carlo sensitivity penalty to judge answer robustness. This triad is therefore largely unexplored in open‑source, numpy‑only evaluation tools.

**Ratings**  
Reasoning: 7/10 — captures logical structure and propagates constraints, but limited to hand‑crafted regex patterns.  
Metacognition: 5/10 — provides a sensitivity estimate yet lacks higher‑order self‑reflection on why perturbations matter.  
Hypothesis generation: 6/10 — can suggest alternative parses via perturbations, but does not actively generate new hypotheses beyond variation.  
Implementability: 8/10 — relies only on regex, numpy arrays, and simple graph algorithms; straightforward to code in <200 lines.

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

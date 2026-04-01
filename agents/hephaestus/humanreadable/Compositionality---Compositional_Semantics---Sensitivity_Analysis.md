# Compositionality + Compositional Semantics + Sensitivity Analysis

**Fields**: Linguistics, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T00:22:41.247291
**Report Generated**: 2026-03-31T14:34:57.422071

---

## Nous Analysis

**Algorithm: Constraint‑Propagation Scorer (CPS)**  

1. **Parsing & Data Structures**  
   - Tokenise the prompt and each candidate answer with a regex‑based tokenizer that captures:  
     * literals (words, numbers)  
     * logical connectives (`and`, `or`, `not`, `if … then`)  
     * comparators (`>`, `<`, `>=`, `<=`, `=`)  
     * causal markers (`because`, `since`, `leads to`)  
     * quantifiers (`all`, `some`, `none`).  
   - Build a **typed directed hypergraph** `G = (V, E)` where each node `v∈V` holds a typed value (boolean, real, or symbolic constant).  
     * Hyperedges `e∈E` encode compositional rules:  
       - Unary: `¬p` → node `p` → node `¬p` (boolean negation)  
       - Binary: `p ∧ q` → `(p,q)` → node `p∧q` (conjunction)  
       - Comparative: `x > y` → `(x,y)` → node `cmp_gt` (boolean)  
       - Causal: `A because B` → `(B,A)` → node `cause` (boolean)  
   - Store node values in a NumPy structured array `vals` with fields `dtype=[('bool',?),('float',f8)]` and a mask indicating undefined.

2. **Constraint Propagation (Scoring Logic)**  
   - Initialise node values from explicit literals in the candidate answer (e.g., “5” → float 5, “true” → bool True).  
   - Iteratively apply hyperedge functions using NumPy vectorised operations:  
     * Boolean: `vals['bool'][dest] = np.logical_and(vals['bool'][src1], vals['bool'][src2])` etc.  
     * Numeric: `vals['float'][dest] = vals['float'][src1] > vals['float'][src2]` → cast to bool.  
     * Causal: treat as implication `B → A`; compute satisfaction as `¬B ∨ A`.  
   - Propagate until convergence (no change in `vals` or max 10 iterations).  
   - Define a **sensitivity score** for each candidate:  
     ```
     s = 1 - (∑|Δ_out| / (∑|Δ_in| + ε))
     ```
     where `Δ_in` are perturbations applied to input literals (e.g., ±1% noise on numbers, random flip of Boolean literals) and `Δ_out` are the resulting changes in the truth value of the query node (the proposition asked in the prompt).  
   - Lower sensitivity → higher robustness → higher score.

3. **Structural Features Parsed**  
   - Negations (`not`, `no`)  
   - Comparatives (`greater than`, `less than`, `≥`, `≤`)  
   - Conditionals (`if … then`)  
   - Numeric constants and arithmetic expressions  
   - Causal claims (`because`, `leads to`, `results in`)  
   - Ordering relations (`before`, `after`, `greater than`)  
   - Quantifiers (`all`, `some`, `none`).

4. **Novelty**  
   - The combination of Fregean compositionality (hypergraph encoding of syntax‑semantics rules) with a sensitivity‑analysis perturbation scheme is not present in existing open‑source reasoning scorers, which typically use pure logical entailment or similarity metrics.  
   - Related work exists in probabilistic soft logic and differentiable theorem provers, but those rely on gradient‑based learning; CPS stays purely algorithmic, using only NumPy and the stdlib, making it novel in the constrained‑tool setting.

**Ratings**  
Reasoning: 8/10 — captures logical structure and robustness via sensitivity, though limited to first‑order hyperedges.  
Metacognition: 6/10 — does not explicitly monitor its own uncertainty beyond sensitivity magnitude.  
Hypothesis generation: 5/10 — can propose alternative parses by perturbing inputs, but lacks generative hypothesis search.  
Implementability: 9/10 — relies only on regex tokenisation, NumPy arrays, and fixed‑point iteration; straightforward to code in <200 lines.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

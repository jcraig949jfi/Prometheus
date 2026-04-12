# Cognitive Load Theory + Emergence + Compositionality

**Fields**: Cognitive Science, Complex Systems, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:46:05.591000
**Report Generated**: 2026-03-31T19:57:32.958434

---

## Nous Analysis

**Algorithm: Constraint‑Driven Compositional Scorer (CDCS)**  

*Data structures*  
- `tokens`: list of strings from a regex‑based tokenizer that preserves punctuation.  
- `graph`: directed multigraph (`dict[node, list[(rel, target)]]`) where nodes are **entities** (noun phrases, numbers, dates) and edges are **relations** extracted by patterns (e.g., “X is greater than Y”, “X causes Y”, “not X”, “if X then Y”).  
- `weights`: numpy array of shape `(E,)` holding a scalar **germane load** for each edge, initialized to 1.0.  
- `load_budget`: scalar representing the intrinsic load limit (set to the number of distinct entities in the prompt).  

*Operations*  
1. **Structural parsing** – Apply a hierarchy of regexes to capture:  
   - Negations (`not`, `no`, `never`).  
   - Comparatives (`greater than`, `less than`, `≤`, `≥`).  
   - Conditionals (`if … then …`, `unless`).  
   - Causal verbs (`cause`, `lead to`, `result in`).  
   - Ordering/temporal markers (`before`, `after`, `first`, `last`).  
   - Numeric literals and units.  
   Each match creates a node (or reuses an existing node via string normalization) and an edge labeled with the relation type.  

2. **Constraint propagation** – Iteratively apply deterministic inference rules using NumPy vectorized operations:  
   - **Transitivity** for `greater_than`/`less_than` edges: if A→B and B→C then add/update A→C with weight = min(weight_AB, weight_BC).  
   - **Modus ponens** for conditionals: if `if X then Y` edge exists and X is asserted true (node marked true), set Y true and propagate its outgoing edges.  
   - **Negation handling**: a `not` edge flips the truth value of its target; contradictions increase extraneous load.  
   - After each propagation step, compute total **extraneous load** as the sum of weights of edges that violate consistency (e.g., both X true and X false).  

3. **Scoring logic** – For each candidate answer:  
   - Parse the answer into its own graph `G_ans`.  
   - Compute **compositional match score** = Σ_{e∈E_ans ∩ E_prompt} weight(e) / |E_ans| (using NumPy dot product on binary edge‑presence vectors).  
   - Penalize by extraneous load: final_score = compositional_match * exp(-λ * extraneous_load), λ=0.5.  
   - Normalize to [0,1] across all candidates.  

*Structural features parsed* – negations, comparatives, conditionals, causal claims, ordering/temporal relations, numeric values with units, and conjunctive/disjunctive connectives.  

*Novelty* – The combination mirrors recent neuro‑symbolic hybrids (e.g., LTN, Neural‑Logic Machines) but replaces learned tensor operations with explicit NumPy‑based constraint propagation, making the reasoning process fully transparent and grounded in Cognitive Load Theory’s load budgets. No prior work couples load‑budgeted constraint propagation with compositional edge‑wise similarity in a pure‑numpy scorer.  

**Ratings**  
Reasoning: 8/10 — The algorithm captures multi‑step logical inference and quantifies consistency, directly measuring reasoning quality.  
Metacognition: 6/10 — Load budget provides a rudimentary self‑monitor of cognitive effort, but lacks reflective adjustment of strategies.  
Hypothesis generation: 5/10 — Edge generation is deterministic; alternative hypotheses are not explored beyond constraint closure.  
Implementability: 9/10 — Uses only regex, NumPy arrays, and stdlib data structures; no external libraries or training required.

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

**Forge Timestamp**: 2026-03-31T19:56:43.383266

---

## Code

*No code was produced for this combination.*

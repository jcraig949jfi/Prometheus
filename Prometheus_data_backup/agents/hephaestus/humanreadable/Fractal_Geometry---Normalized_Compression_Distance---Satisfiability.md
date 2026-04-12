# Fractal Geometry + Normalized Compression Distance + Satisfiability

**Fields**: Mathematics, Information Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T03:06:11.305136
**Report Generated**: 2026-03-31T14:34:55.689585

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Convert prompt and each candidate answer into a directed labeled graph G = (V,E).  
   - Vertices V are atomic propositions extracted via regex patterns for:  
     *Negations* (`not`, `no`), *comparatives* (`>`, `<`, `>=`, `<=`), *conditionals* (`if … then …`), *causal cues* (`because`, `leads to`), *ordering* (`before`, `after`), *numeric literals* and *equality* (`=`).  
   - Edges E encode the relation type (label) between two atoms (e.g., `if A then B` → edge A→B labeled “cond”; `A > 5` → edge A→value node labeled “gt”).  
   - The graph is stored as two NumPy arrays: a node‑index map (dtype int32) and an edge list `[src, dst, label_id]` (dtype int32).  

2. **Fractal‑structure score** – Apply a box‑counting estimate of the graph’s Hausdorff dimension:  
   - For scales s = 1…max_path_length, count the number of distinct s‑hop neighborhoods needed to cover all nodes (using BFS frontier expansion).  
   - Fit log(N(s)) vs. log(1/s) with NumPy’s `polyfit`; the slope D ≈ fractal dimension. Higher D indicates richer self‑similar hierarchical reasoning.  

3. **Normalized Compression Distance (NCD)** – Serialize each graph to a canonical string (sorted edge triples) and compress with `gzip` (via `zlib`).  
   - NCD(G₁,G₂) = (C(G₁+G₂) – min(C(G₁),C(G₂))) / max(C(G₁),C(G₂)), where C is compressed length. Lower NCD → greater structural similarity to a reference answer (the prompt’s gold graph).  

4. **SAT consistency check** – Translate the graph into a set of Boolean clauses:  
   - Each atom → Boolean variable.  
   - Negation → ¬v.  
   - Comparative/ordinal → encoded via auxiliary variables using simple linear‑order encodings (e.g., `x > y` → (x ∧ ¬y) ∨ …).  
   - Conditional `if A then B` → (¬A ∨ B).  
   - Run a pure‑Python DPLL solver (using only recursion and NumPy for unit‑propagation speed‑ups).  
   - If the clause set is satisfiable, assign a consistency score S = 1; else S = 0.  

**Scoring logic** – For each candidate answer c:  
`score(c) = α·D_c + β·(1 – NCD(G_ref, G_c)) + γ·S_c`  
with α,β,γ ∈ [0,1] summing to 1 (e.g., 0.4,0.4,0.2). Higher score reflects more fractal‑rich, structurally similar, and logically consistent reasoning.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering/temporal relations, numeric values, equality/inequality, and conjunctions implicit in edge labels.

**Novelty** – While fractal dimension, NCD, and SAT solving appear separately in similarity and reasoning literature, their joint use to evaluate answer quality—using a graph‑based fractal measure as a prior, NCD for structural alignment, and a lightweight SAT check for logical consistency—has not been combined in a public reasoning‑evaluation tool. It bridges geometric self‑similarity analysis with compression‑based similarity and constraint satisfaction, which existing tools treat independently.

**Rating**  
Reasoning: 8/10 — captures logical consistency and structural similarity but relies on hand‑crafted encodings for comparatives and causals.  
Metacognition: 6/10 — provides a self‑assessment via fractal dimension and SAT consistency, yet lacks explicit reflection on uncertainty.  
Hypothesis generation: 5/10 — the method scores candidates but does not propose new hypotheses; it only evaluates given answers.  
Implementability: 9/10 — uses only NumPy, zlib, and a simple DPLL solver; all components fit easily within the constraints.

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

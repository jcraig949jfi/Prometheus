# Dual Process Theory + Analogical Reasoning + Causal Inference

**Fields**: Cognitive Science, Cognitive Science, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:15:14.360465
**Report Generated**: 2026-03-27T16:08:16.429669

---

## Nous Analysis

**Algorithm**  
The evaluator builds two typed directed graphs – one from the reference answer (gold) and one from each candidate – using only NumPy arrays and Python’s standard library.  

1. **Parsing (System 1 fast heuristic)**  
   - Regex patterns extract: entities (noun phrases, numbers), predicates (`causes`, `leads to`, `implies`, `greater_than`, `less_than`, `equals`, `not`).  
   - Each entity gets an integer ID via a dictionary; predicates map to relation types R ∈ {CAUSE, COMP, EQ, NEG}.  
   - For each relation type a Boolean adjacency matrix **Aᵣ** ∈ {0,1}^{n×n} is filled (NumPy `zeros`/`ones`).  

2. **Constraint propagation (System 2 deliberate)**  
   - Transitive closure for CAUSE and COMP is computed with Floyd‑Warshall style Boolean matrix multiplication:  
     `for k in range(n): Aᵣ |= Aᵣ @ Aᵣ` (where `@` is NumPy dot, treated as Boolean via `>0`).  
   - This yields inferred causal and ordering relations (do‑calculus approximated by checking if a directed path exists).  

3. **Analogical mapping (structure mapping)**  
   - A similarity matrix **S** ∈ ℝ^{n×n} is built where S[i,j]=1 if entity i (candidate) and j (gold) share the same semantic class (numeric, proper noun, generic noun) – determined by a tiny lookup table (no external models).  
   - The optimal one‑to‑one entity alignment is found by solving the linear sum assignment problem with a simple O(n³) Hungarian implementation using NumPy (cost = 1‑S).  
   - The permutation matrix **P** from this alignment re‑orders candidate adjacency matrices: **Âᵣ** = Pᵀ Aᵣ P.  

4. **Scoring logic**  
   - For each relation type r compute a match score:  
     `match_r = (Âᵣ ∘ Gᵣ).sum() / Gᵣ.sum()` where `∘` is element‑wise product and Gᵣ is the gold’s transitive‑closure matrix.  
   - Final score = w₁·match_CAUSE + w₂·match_COMP + w₃·match_EQ + w₄·match_NEG, with weights summing to 1 (e.g., 0.4,0.3,0.2,0.1).  
   - Scores lie in [0,1]; higher indicates better structural and causal alignment.  

**Parsed structural features**  
- Negations (`not`, `no`) → NEG relation.  
- Comparatives (`more than`, `less than`, `greater`, `less`) → COMP relation.  
- Conditionals (`if … then`, `implies`, `leads to`) → CAUSE relation.  
- Explicit causal claims (`because`, `causes`, `results in`) → CAUSE relation.  
- Ordering/temporal terms (`before`, `after`, `precedes`) → COMP relation.  
- Numeric values (integers, floats) → entity class for similarity matching.  
- Equality (`is`, `equals`, `same as`) → EQ relation.  

**Novelty**  
While semantic graph matching, causal Bayesian nets, and dual‑process models exist separately, fusing fast heuristic extraction, Boolean constraint propagation for causal/ordering inference, and NumPy‑based analogical structure mapping into a single scoring pipeline is not present in current public reasoning evaluators. The combination therefore constitutes a novel algorithmic approach.  

**Ratings**  
Reasoning: 8/10 — captures causal and relational structure with provable constraint propagation.  
Metacognition: 6/10 — includes a fast/slow distinction but lacks explicit self‑monitoring of confidence.  
Hypothesis generation: 5/10 — focuses on scoring given candidates; does not propose new hypotheses.  
Implementability: 9/10 — relies only on regex, NumPy, and basic Python; no external libraries or neural components.

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

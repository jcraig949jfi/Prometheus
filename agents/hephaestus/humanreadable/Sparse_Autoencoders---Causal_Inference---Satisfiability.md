# Sparse Autoencoders + Causal Inference + Satisfiability

**Fields**: Computer Science, Information Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T23:20:48.885513
**Report Generated**: 2026-03-31T17:10:38.129739

---

## Nous Analysis

**Algorithm**  
1. **Sparse feature extraction** – Tokenize the prompt and each candidate answer into a bag of predicate‑atoms (e.g., `X > Y`, `cause(A,B)`, `¬P`). Build a binary matrix `A ∈ {0,1}^{n×m}` where rows are instances (prompt + candidate) and columns are distinct atoms. Learn a dictionary `D ∈ ℝ^{m×k}` (k ≪ m) by solving the sparse coding problem  
   `min_{Z≥0} ‖A − ZD‖_F^2 + λ‖Z‖_1`  
   using coordinate descent (numpy only). The non‑zero entries of `Z` give a sparse activation vector `z_i` for each instance, representing the most salient logical features.  

2. **Causal graph construction** – From the active atoms in `z_i` extract all causal literals `cause(X,Y)`. Assemble a directed acyclic graph `G_i` where nodes are variables and edges are the extracted causes. Apply Pearl’s do‑calculus rules (implemented as simple graph‑search: if a path X→…→Y exists, then `do(X)` affects Y) to compute a binary causal‑consistency matrix `C_i` where `C_{uv}=1` iff the causal relation implied by the prompt holds in the candidate under interventions.  

3. **SAT‑based scoring** – Encode the remaining atoms (comparisons, ordering, negations) as a propositional formula `F_i` in CNF. For each causal edge `(u→v)` that is asserted in the prompt, add a unit clause `v` if `u` is true, otherwise add `¬v`. Run a lightweight DPLL SAT solver (pure Python, using numpy for clause‑matrix ops) to check satisfiability of `F_i`. If `F_i` is satisfiable, the candidate receives a score equal to the sparsity‑weighted sum of activated features:  
   `score_i = ‖z_i‖_1 * sat(F_i)`, where `sat(F_i)=1` if satisfiable else 0.  

**Structural features parsed**  
- Negations (`not`, `never`) → literal polarity.  
- Comparatives (`greater than`, `less than`, `≥`, `≤`) → arithmetic atoms.  
- Conditionals (`if … then …`) → implication clauses.  
- Numeric values → constants in comparison atoms.  
- Causal claims (`cause`, `leads to`, `due to`) → directed edges.  
- Ordering relations (`before`, `after`, `first`, `last`) → temporal atoms encoded as ordering predicates.  

**Novelty**  
Sparse autoencoders have been used for feature disentanglement in neural nets; causal inference is typically paired with graphical models; SAT solving is standard for verification. The concrete combination—learning a sparse dictionary over logical atoms, extracting a causal graph from the sparse code, and then feeding the graph into a SAT checker to enforce consistency—does not appear in existing surveys of reasoning evaluators. While each component is known, their chaining in a pure‑numpy pipeline is novel.  

**Ratings**  
Reasoning: 8/10 — captures logical, causal, and numeric structure via provable constraint propagation.  
Metacognition: 6/10 — the method can detect when its own assumptions (sparsity level, λ) lead to unsatisfiability, but lacks explicit self‑reflection loops.  
Hypothesis generation: 5/10 — produces alternative sparse codes via different λ values, yet does not actively propose new causal hypotheses beyond those present in the text.  
Implementability: 9/10 — relies only on numpy for matrix ops and a pure‑Python DPLL solver; no external libraries or GPU needed.

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

**Forge Timestamp**: 2026-03-31T17:09:48.172605

---

## Code

*No code was produced for this combination.*

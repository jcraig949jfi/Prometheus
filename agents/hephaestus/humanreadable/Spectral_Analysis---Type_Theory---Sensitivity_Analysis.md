# Spectral Analysis + Type Theory + Sensitivity Analysis

**Fields**: Signal Processing, Logic, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T23:00:36.701950
**Report Generated**: 2026-03-31T19:54:52.106218

---

## Nous Analysis

The algorithm builds a typed proposition graph from each candidate answer, then scores it by the spectral prominence of its nodes after weighting them with sensitivity measures.  

1. **Parsing & typing** – Using regex we extract atomic clauses and label them with simple type tags: `Prop` (bare statement), `Conditional` (if‑then), `Comparative` (>, <, more/less), `Causal` (because, leads to), `Negation` (not, no), `Numeric` (detected numbers), `Ordering` (first, before, after). Each clause becomes a node `n_i` with a feature vector `t_i` (one‑hot over types) and a numeric value `v_i` when applicable.  

2. **Dependency edges** – For every pair (i,j) we test entailment patterns:  
   * `Conditional` → `Prop` creates a directed edge i→j if the antecedent matches j.  
   * `Comparative`/`Ordering` yields edges based on magnitude or temporal precedence.  
   * `Causal` yields edges i→j when the cause clause matches i and effect matches j.  
   The adjacency matrix `A` (numpy float) entry `A[i,j]=1` if such a pattern holds, else 0.  

3. **Sensitivity weighting** – For each node we compute a sensitivity score `s_i` by perturbing its numeric value (if any) by a small ε and re‑evaluating the outgoing edges; `s_i = Σ_j |ΔA[i,j]|/ε`. Nodes without numbers get a base sensitivity of 0.1.  

4. **Spectral scoring** – Form the degree matrix `D` (`D[i,i]=Σ_j A[i,j]`). Compute the normalized Laplacian `L = I - D^{-1/2} A D^{-1/2}`. Using numpy’s power iteration we obtain the dominant eigenvector `v₁` (associated with the smallest non‑zero eigenvalue of L, i.e., the smoothest mode).  

5. **Answer score** – Build an answer indicator vector `x` where `x[i]=1` if node i appears in the candidate answer, else 0. The raw spectral alignment is `a = x·v₁`. The final score penalizes volatile nodes: `score = a * (1 - std(s_i * x_i)/mean(s_i * x_i + 1e-6))`. Higher scores indicate answers whose propositions sit in a stable, strongly connected sub‑graph.  

**Structural features parsed**: negations, comparatives, conditionals, causal claims, numeric values, ordering relations, and explicit type tags derived from those patterns.  

**Novelty**: While spectral methods (e.g., PageRank) and type‑theoretic annotations exist separately, jointly weighting a logical dependency graph with sensitivity‑derived node scores and scoring via the Laplacian’s dominant mode is not documented in mainstream QA or argument‑scoring literature.  

Reasoning: 7/10 — captures global coherence and stability but relies on shallow syntactic patterns.  
Metacognition: 5/10 — no explicit self‑monitoring of parsing confidence; sensitivity offers limited reflection.  
Hypothesis generation: 6/10 — eigenmode highlights influential sub‑graphs, suggesting missing links, yet no generative search.  
Implementability: 8/10 — uses only regex, numpy linear algebra, and basic loops; straightforward to code in <200 lines.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:54:45.098145

---

## Code

*No code was produced for this combination.*

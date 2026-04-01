# Neural Plasticity + Pragmatics + Sensitivity Analysis

**Fields**: Biology, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T16:02:48.558193
**Report Generated**: 2026-03-31T16:21:16.567116

---

## Nous Analysis

**Algorithm: Pragmatic‑Hebbian Sensitivity Scorer (PHSS)**  

1. **Data structures**  
   - `nodes`: dict `{id: {'text':str, 'polarity':±1, 'value':float|None, 'uncert':float}}`  
   - `edges`: dict `{src_id: [(tgt_id, edge_type, weight), …]}` where `edge_type ∈ {IMPLIES, CAUSES, GREATER, LESS, EQUAL, NEG}` and `weight` is a float.  
   - `activations`: NumPy array `A` of shape `(N,)` matching node order; `A[i]` ∈ `[0,1]` reflects current belief strength.  
   - `W`: NumPy matrix `(N,N)` where `W[i,j]` = weight of edge `i→j` (zero if absent).  

2. **Parsing (structural features)**  
   Using only `re`, extract propositions matching patterns:  
   - Negation: `\bnot\s+(\w+)` → edge type `NEG`.  
   - Comparatives: `(\w+)\s+(is\s+)?(greater|less|more|fewer)\s+than\s+(\w+)` → `GREATER/LESS`.  
   - Conditionals: `if\s+(.+?)\s+then\s+(.+)` → `IMPLIES`.  
   - Causal claims: `(\w+)\s+causes\s+(\w+)` → `CAUSES`.  
   - Ordering: `(\w+)\s+before\s+(\w+)` → `IMPLIES` with temporal polarity.  
   - Numeric values: capture floats/integers and store in `nodes['value']`.  
   Each extracted triple creates or updates a node and an edge with initial weight `η = 0.1`.  

3. **Hebbian learning & pruning**  
   For each sentence, set activation `A[i]=1` for nodes mentioned, else `0`. Update weights:  
   `W ← W + η * (A[:,None] * A[None,:])`.  
   After processing all sentences, prune: `W[W < τ] ← 0` with `τ = 0.05` (synaptic pruning).  

4. **Pragmatic relevance (implicature)**  
   For a candidate answer `c`, treat its propositions as extra nodes/edges (added temporarily). Compute relevance `R = (sum of weights of candidate edges that connect to any context node) / (total weight of candidate edges)`. This approximates Grice’s quantity & relevance maxims.  

5. **Sensitivity analysis**  
   Perturb input node values: `A_ε = A + ε * randn(N)` with `ε = 0.01`. Propagate once: `B = sigmoid(W.T @ A_ε)` (sigmoid to keep in `[0,1]`). Compute finite‑difference Jacobian approximation `J ≈ (B - B₀)/ε` where `B₀` is unperturbed propagation. Sensitivity `S = ||J||_F` (Frobenius norm).  

6. **Scoring**  
   `score(c) = R * (1 / (1 + S))`. Higher relevance and lower sensitivity yield higher scores. All operations use only NumPy and the standard library.  

**Structural features parsed**: negations, comparatives, conditionals, causal claims, temporal ordering, numeric quantities, and equality relations.  

**Novelty**: The combination mirrors Hebbian weight updating (neural plasticity), pragmatic relevance weighting, and local sensitivity propagation; while each component exists separately, their joint use in a pure‑numpy scoring pipeline for answer evaluation is not documented in existing surveys.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and robustness but relies on linear approximations.  
Metacognition: 5/10 — no explicit self‑monitoring of uncertainty beyond static sensitivity.  
Hypothesis generation: 6/10 — generates implicit hypotheses via edge creation, yet lacks generative search.  
Implementability: 9/10 — all steps are regex‑based, NumPy matrix ops, and fit the constraints.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
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

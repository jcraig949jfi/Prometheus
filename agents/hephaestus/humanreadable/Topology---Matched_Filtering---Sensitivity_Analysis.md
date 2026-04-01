# Topology + Matched Filtering + Sensitivity Analysis

**Fields**: Mathematics, Signal Processing, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T00:44:55.550914
**Report Generated**: 2026-03-31T14:34:57.432072

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Proposition Graph**  
   - Use regex to extract atomic propositions (e.g., “X is greater than Y”, “If A then B”, numeric comparisons).  
   - Each proposition becomes a node `i` with a feature vector `f_i` (one‑hot for type: negation, comparative, conditional, causal, ordering, numeric).  
   - Directed edges `i→j` encode logical relations extracted from cue words:  
     * “not” → negation edge (type = ¬)  
     * “because”, “causes” → causal edge (type = →)  
     * “if … then” → conditional edge (type = ⇒)  
     * “greater than”, “less than” → ordering edge (type = < or >)  
     * “and”, “or” → conjunctive/disjunctive edge (type = ∧, ∨).  
   - Store adjacency as a set of three `numpy.ndarray` matrices `A_type` (shape `n×n`) where each entry is 1 if that edge type exists, else 0.  

2. **Reference Construction**  
   - Build the same graph `G_ref` from a gold‑standard answer (or a set of key propositions).  

3. **Matched‑Filtering Similarity**  
   - Flatten each adjacency tensor into a vector `a = concat(A_¬, A_→, A_⇒, A_<, A_>, A_∧, A_∨)`.  
   - Compute normalized cross‑correlation (the matched filter output):  
     `s = (a·a_ref) / (||a||·||a_ref|| + ε)`.  
   - This yields a value in [0,1] measuring structural alignment while maximizing SNR against random noise.  

4. **Sensitivity Analysis (Robustness Penalty)**  
   - Generate `K` perturbed versions of the candidate graph by randomly flipping `p`% of edges (add/delete) or toggling node negation flags.  
   - For each perturbed graph compute similarity `s_k`.  
   - Estimate sensitivity as the variance `σ² = var([s_k])`.  
   - Define robustness factor `r = 1 / (1 + λ·σ²)` with λ = 0.5 (tunable).  

5. **Final Score**  
   - `score = s * r`.  
   - Higher scores indicate answers that closely match the reference topology and are stable under small perturbations.  

**Parsed Structural Features**  
Negations (“not”, “no”), comparatives (“greater than”, “less than”, “equal to”), conditionals (“if … then”, “unless”), causal claims (“because”, “leads to”, “results in”), ordering relations (“before”, “after”, “precedes”), and explicit numeric values or ranges.  

**Novelty**  
Graph‑based similarity and topological invariants (connected components, cycles) are used in semantic‑parsing kernels, but coupling them with a matched‑filter cross‑correlation step and an explicit sensitivity‑analysis penalty is not present in existing answer‑scoring literature; the combination is therefore novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and stability, though deeper inference (e.g., multi‑step chaining) is limited.  
Metacognition: 5/10 — provides a robustness estimate but lacks explicit self‑monitoring of reasoning steps.  
Hypothesis generation: 4/10 — focuses on scoring given candidates; generating new hypotheses is outside scope.  
Implementability: 8/10 — relies only on regex, NumPy array ops, and basic graph algorithms; straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.33** |

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

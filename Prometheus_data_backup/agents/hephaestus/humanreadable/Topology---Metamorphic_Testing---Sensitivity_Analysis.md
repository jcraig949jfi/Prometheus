# Topology + Metamorphic Testing + Sensitivity Analysis

**Fields**: Mathematics, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T15:42:04.240485
**Report Generated**: 2026-03-27T03:26:11.191355

---

## Nous Analysis

**Algorithm: Topo‑Meta‑Sens Scorer (TMS)**  

1. **Parsing stage** – The input prompt and each candidate answer are tokenized with a rule‑based regex pipeline that extracts a directed labeled graph G = (V, E).  
   - **Nodes (V)** correspond to atomic propositions: entities, quantities, and truth‑valued predicates (e.g., “X > 5”, “¬rain”, “cause(Y)”).  
   - **Edges (E)** encode three relation types derived from the three concepts:  
     *Topological*: adjacency/continuity (e.g., “X is connected to Y”, “hole in Z”) → weight wₜ = 1 if the relation preserves connectivity under ε‑perturbation, else 0.  
     *Metamorphic*: input‑output invariants (e.g., “doubling input doubles output”, “sorting preserves order”) → weight wₘ = 1 if the candidate satisfies the metamorphic relation extracted from the prompt, else 0.  
     *Sensitivity*: partial‑derivative style constraints (e.g., “increase Δx by 0.1 changes y by ≤ 0.05”) → weight wₛ = exp(−|Δy_pred−Δy_obs|/σ) where σ is a tolerance drawn from the prompt.  

   The graph is stored as two NumPy arrays: `node_ids` (int64) and `edge_mat` (float32, shape [E, 3]) where columns are `[src, dst, type]` (type ∈ {0,1,2} for topo, meta, sens).

2. **Constraint propagation** – Using Floyd‑Warshall‑style transitive closure on the adjacency sub‑matrix for each type, we infer implied edges (e.g., if A→ₜ B and B→ₜ C then A→ₜ C). This yields a closure matrix `C` for each relation type.

3. **Scoring logic** – For a candidate answer, compute:  
   ```
   score = α * mean(C_topo) + β * mean(C_meta) + γ * mean(C_sens)
   ```  
   where α,β,γ are normalized weights (default 1/3 each). `mean(C_*)` is the proportion of satisfied constraints after closure. The final score lies in [0,1]; higher means the answer preserves topological invariants, obeys metamorphic relations, and shows low sensitivity to input perturbations.

4. **Parsed structural features** – The regex pipeline specifically captures:  
   - Negations (`not`, `never`, `¬`) → flip truth value of a node.  
   - Comparatives (`>`, `<`, `≥`, `≤`, `more than`, `less than`) → generate sensitivity edges with a Δ‑value.  
   - Conditionals (`if … then …`, `unless`) → create implication edges (type = meta).  
   - Numeric values and units → anchor sensitivity tolerances.  
   - Causal verbs (`cause`, `lead to`, `result in`) → sensitively weighted edges.  
   - Ordering relations (`first`, `after`, `before`) → metamorphic ordering invariants.

**Novelty** – While each constituent idea appears separately (topological data analysis in NLP, metamorphic relation testing, sensitivity‑based robustness scores), their conjunction into a single constraint‑propagation graph that jointly evaluates topological preservation, metamorphic invariants, and sensitivity is not documented in existing surveys. Hence the combination is novel.

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical structure and quantitative sensitivity, providing a principled score beyond surface similarity.  
Metacognition: 6/10 — It can detect when an answer violates its own inferred constraints, but lacks explicit self‑reflection on why a constraint failed.  
Hypothesis generation: 5/10 — The method evaluates given candidates; it does not generate new hypotheses, though the constraint graph could be repurposed for abduction.  
Implementability: 9/10 — Relies only on regex, NumPy array operations, and basic graph algorithms; no external libraries or APIs are required.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Topology**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Criticality + Multi-Armed Bandits + Metamorphic Testing (accuracy: 0%, calibration: 0%)
- Differentiable Programming + Nash Equilibrium + Metamorphic Testing (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

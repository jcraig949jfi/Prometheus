# Chaos Theory + Compositionality + Sensitivity Analysis

**Fields**: Physics, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T00:26:28.829406
**Report Generated**: 2026-04-01T20:30:43.410117

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer into a directed acyclic graph (DAG) where nodes are atomic propositions (literals, comparatives, numeric constants) and edges represent logical connectives (¬, ∧, ∨, →) or syntactic dependencies (subject‑verb‑object, modifier‑head). Store for each node:  
   - `value` ∈ {0,1} (truth of the atom under the prompt)  
   - `eps` = small perturbation magnitude (default 1e‑3)  
   - `type` (literal, negation, conjunction, etc.)  

2. **Compositional evaluation**: recursively compute the node’s output using truth‑table rules for its type. This yields a base truth value `v₀` for the whole answer graph.  

3. **Sensitivity propagation**: for every leaf node, create a perturbed copy where `value ← value ⊕ eps` (flip with probability eps). Re‑evaluate the entire DAG to obtain perturbed output `vᵢ`. Compute the finite‑difference Jacobian approximation `Jₖ = (vᵢ - v₀)/eps` for each leaf `k`.  

4. **Chaos metric (Lyapunov‑like)**: calculate the average logarithmic divergence  
   \[
   \lambda = \frac{1}{N}\sum_{k=1}^{N}\log\frac{|Jₖ|}{\epsilon}
   \]  
   Large positive λ indicates exponential sensitivity to input perturbations (chaotic reasoning).  

5. **Scoring**:  
   - Base match score `S₀` = 1 if the answer graph’s truth value equals the expected answer’s truth value, else 0 (or a fractional match via structural overlap).  
   - Final score `S = S₀ * exp(-α·max(0,λ))`, where α controls penalty for instability (e.g., α=0.5).  
   The procedure uses only NumPy for vectorized perturbation evaluations and Python’s standard library for parsing (regex, stack‑based shunting‑yard).  

**Structural features parsed**  
Negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), causal markers (“because”, “leads to”), ordering relations (“before”, “after”), numeric values and units, quantifiers (“all”, “some”), and conjunctive/disjunctive connectives.  

**Novelty**  
While sensitivity analysis and compositional semantics appear separately in probabilistic soft logic and formal concept analysis, coupling them with a Lyapunov‑exponent‑style chaos measure to penalize unstable reasoning is not present in existing literature. The approach treats logical stability as a dynamical‑system property, offering a novel robustness criterion for answer selection.  

**Rating**  
Reasoning: 7/10 — captures logical structure and sensitivity but relies on binary truth approximations.  
Metacognition: 5/10 — limited self‑reflection; only detects instability, not reasoning about uncertainty.  
Hypothesis generation: 4/10 — excels at evaluating given hypotheses, not proposing new ones.  
Implementability: 8/10 — uses only regex, stacks, and NumPy; straightforward to code in <200 lines.

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

# Dynamical Systems + Hebbian Learning + Sensitivity Analysis

**Fields**: Mathematics, Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T03:41:33.349388
**Report Generated**: 2026-03-31T14:34:55.745584

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions from the prompt and each candidate answer. Each proposition gets a feature vector *f* ∈ {0,1}^k where dimensions correspond to structural primitives: negation, comparative, conditional, causal claim, numeric value, ordering relation. Propositions are nodes in a directed graph; edges are labeled by the relation type (e.g., *implies*, *greater‑than*, *negates*).  
2. **Adjacency matrix** – Build a binary adjacency matrix *A* ∈ ℝ^{n×n} where *A*_{ij}=1 if there is an edge from node *i* to *j*.  
3. **Hebbian weight initialization** – Start with a zero weight matrix *W*. For every pair of nodes that co‑occur in the same clause (prompt or answer), update *W*_{ij} += α · *f*_i · *f*_j (α = 0.1). This implements the “fire together, wire together’’ rule using only NumPy.  
4. **Dynamical update** – Initialise the state *x₀* as the normalized sum of feature vectors of the prompt propositions. Iterate for T = 10 steps:  
   *x*_{t+1} = σ(*W* *x*_t + β *A* *x*_t)  
   where σ is a element‑wise sigmoid (implemented with np.exp) and β = 0.2 mixes relational propagation with Hebbian associations.  
5. **Answer scoring** – Compute the cosine similarity *s* between the final state *x*_T and the answer’s feature vector *f*_ans.  
6. **Sensitivity analysis** – Approximate the Jacobian *J* = ∂*x*_T/∂*x*₀ by finite differences: perturb each dimension of *x*₀ by ε = 1e‑4, re‑run the dynamics, and collect the change in *x*_T. Compute ‖*J*‖_F (Frobenius norm). The final score is *score* = *s* · (1 − ‖*J*‖_F / (‖*J*‖_F + 1)), rewarding answers that are both aligned with the prompt and robust to small input perturbations.  

**Structural features parsed** – negations (“not”, “no”), comparatives (“more than”, “>”, “less than”), conditionals (“if … then”, “unless”), causal claims (“because”, “leads to”, “results in”), numeric values (integers, floats), ordering relations (“first”, “second”, “before”, “after”), and conjunction/disjunction markers.  

**Novelty** – The coupling of a Hebbian‑learned recurrent weight matrix with a deterministic graph‑based dynamical system and a post‑hoc sensitivity penalty is not found in existing reasoning scorers, which typically use pure similarity, rule chaining, or reservoir computing without explicit Jacobian‑based robustness checks.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and dynamics but still approximates deep reasoning with a simple recurrent update.  
Metacognition: 5/10 — sensitivity provides a rudimentary self‑check of robustness, yet lacks higher‑order reflection on the reasoning process itself.  
Hypothesis generation: 4/10 — the model can propose variations via perturbations, but does not actively generate new hypotheses beyond scoring given candidates.  
Implementability: 8/10 — relies solely on NumPy and regex; all operations are straightforward matrix manipulations and finite‑difference loops.

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

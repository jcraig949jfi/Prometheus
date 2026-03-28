# Statistical Mechanics + Global Workspace Theory + Sensitivity Analysis

**Fields**: Physics, Cognitive Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T08:47:00.115663
**Report Generated**: 2026-03-27T16:08:16.211673

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex‑based patterns to extract from each sentence a set of propositional tuples:  
   - `(entity1, relation, entity2, polarity, numeric_value, modality)`  
   Patterns capture: negation (`not`, `no`), comparatives (`>`, `<`, `≥`, `≤`, “more than”, “less than”), conditionals (`if … then`), causal (`because`, “leads to”), ordering (`before`, `after`, “first”, “second”), and quantifiers (`all`, `some`, `none`).  
   Each proposition is stored as a row in a NumPy feature matrix **F** of shape *(n_propositions, n_features)*, where features are binary flags for the linguistic constructs above and a float for any numeric value.

2. **Constraint definition** – From the question and any background facts, build a list of constraint functions **C_k(F)** that return a violation score (0 if satisfied, >0 otherwise). Examples:  
   - Transitivity: if `A > B` and `B > C` then require `A > C`.  
   - Modus ponens: if `if P then Q` and `P` true then require `Q` true.  
   - Numeric consistency: extracted numbers must obey arithmetic statements.  
   Each constraint is applied vectorised over all candidates, yielding a violation matrix **V** of shape *(n_candidates, n_constraints)*.

3. **Statistical‑mechanics scoring** – Assign a uniform weight vector **w** (or learned via simple heuristics). Energy of candidate *i*:  
   `E_i = np.dot(V[i], w)`  
   Compute Boltzmann probabilities with inverse temperature β=1.0:  
   `unnorm = np.exp(-β * E)`  
   `p =unnorm / np.sum(unnorm)`  

4. **Sensitivity analysis (robustness)** – For each candidate, perturb each feature of **F** by a small ε (e.g., flip negation flag, add 1% to numeric value) and recompute *p*. Sensitivity *S_i* is the RMS change in probability across all perturbations:  
   `S_i = np.sqrt(np.mean((p_perturbed - p_i)**2))`  

5. **Final score** – Combine likelihood and robustness:  
   `score_i = p_i * (1 - λ * S_i)` with λ=0.2 (clipped to [0,1]). Higher scores indicate answers that satisfy constraints strongly and are stable under small input changes.

**Parsed structural features** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values, quantifiers, modality markers.

**Novelty** – The blend of an energy‑based ensemble (statistical mechanics), a global‑workspace‑style competition‑ignition mechanism (via probability redistribution), and local sensitivity analysis is not found in existing reasoning scorers. Related work includes Markov Logic Networks and Probabilistic Soft Logic, but those lack the explicit sensitivity‑robustness term and the broadcast‑like normalization step.

**Ratings**  
Reasoning: 7/10 — captures logical constraints and uncertainty via a principled ensemble, but ignores deeper semantic nuance.  
Metacognition: 6/10 — sensitivity term provides a crude self‑check of stability, yet no explicit reasoning‑about‑reasoning loop.  
Hypothesis generation: 5/10 — focuses on scoring given candidates; does not propose new hypotheses.  
Implementability: 8/10 — relies only on regex, NumPy vectorised ops, and simple loops; readily achievable in <200 lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
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

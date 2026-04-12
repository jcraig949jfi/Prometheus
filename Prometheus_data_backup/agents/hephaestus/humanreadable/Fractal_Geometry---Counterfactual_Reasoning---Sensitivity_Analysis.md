# Fractal Geometry + Counterfactual Reasoning + Sensitivity Analysis

**Fields**: Mathematics, Philosophy, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T14:32:43.772803
**Report Generated**: 2026-03-31T18:05:52.683537

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Convert the prompt and each candidate answer into a *labeled directed hypergraph* \(G=(V,E)\).  
   - Nodes \(V\) are atomic propositions extracted via regex patterns for:  
     * negations (`not`, `never`),  
     * comparatives (`greater than`, `less than`, `equals`),  
     * conditionals (`if … then …`, `unless`),  
     * numeric values (integers, floats, percentages),  
     * causal verbs (`cause`, `lead to`, `result in`),  
     * ordering relations (`before`, `after`, `precedes`).  
   - Hyperedges \(E\) represent logical relations: a unary edge for negation, a binary edge for comparatives/causals/ordering, and a ternary edge for conditionals (antecedent → consequent). Edge labels store the type and any numeric constants.  

2. **Counterfactual perturbation** – For each candidate answer, generate a set of *counterfactual worlds* by applying the *do‑calculus*‑style operation: flip the truth value of a randomly selected subset of nodes (respecting logical constraints: flipping a node forces propagation through modus ponens and transitivity). This yields a perturbed hypergraph \(G'\).  

3. **Sensitivity measurement** – Treat each numeric node as a variable \(x_i\). Compute the finite‑difference sensitivity of a scalar *consistency score* \(S(G)\) (defined below) to each \(x_i\):  
   \[
   \frac{\partial S}{\partial x_i}\approx\frac{S(G_{x_i+\epsilon})-S(G_{x_i-\epsilon})}{2\epsilon},
   \]  
   where \(G_{x_i\pm\epsilon}\) is the hypergraph with the numeric value perturbed by a small \(\epsilon\) (e.g., 1% of its magnitude). Aggregate sensitivities into a vector \(\mathbf{s}\).  

4. **Fractal‑geometry regularization** – Tokenize the answer into a sequence of symbols (words, numbers, operators). Build a *multiscale occurrence matrix* \(M_k\) where entry \(M_k[i,j]\) counts co‑occurrences of symbol \(i\) and \(j\) within a sliding window of size \(2^k+1\) (k = 0…K). For each scale compute the box‑counting dimension \(D_k\) of the non‑zero entries of \(M_k\) (treat non‑zero cells as occupied boxes in a 2‑D grid). The fractal score is the variance of \(\{D_k\}\) across scales; low variance indicates self‑similar structure.  

5. **Scoring logic** – Define a base consistency score:  
   \[
   S(G)=\frac{\#\text{satisfied hyperedges}}{\#\text{total hyperedges}},
   \]  
   where a hyperedge is satisfied if its logical condition holds under the current truth assignments (e.g., a causal edge is satisfied if antecedent true ⇒ consequent true).  
   Final answer score:  
   \[
   \text{Score}= S(G) - \lambda_1\|\mathbf{s}\|_2 - \lambda_2 \operatorname{Var}\{D_k\},
   \]  
   with \(\lambda_1,\lambda_2\) small weighting constants (e.g., 0.1). Higher scores reward logical consistency, low sensitivity to numeric perturbations, and self‑similar (fractal) answer structure.  

**Structural features parsed**  
Negations, comparatives, conditionals, numeric values, causal claims, ordering relations, and logical connectives (and/or). These are extracted via regex and fed into the hypergraph representation.

**Novelty**  
The combination is novel: existing reasoning evaluators use either pure logical constraint propagation or similarity‑based metrics. Integrating counterfactual perturbations with finite‑difference sensitivity and a fractal‑dimension regularizer on textual structure has not been reported in the literature on algorithmic reasoning evaluation.

**Rating lines**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency, counterfactual robustness, and sensitivity, capturing core reasoning dimensions.  
Metacognition: 6/10 — It does not explicitly model the answerer’s awareness of uncertainty, though sensitivity provides a proxy.  
Hypothesis generation: 5/10 — The method scores given answers but does not generate new hypotheses; it only assesses existing ones.  
Implementability: 9/10 — All steps rely on regex, numpy array operations, and basic graph algorithms; no external libraries or APIs are needed.

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

**Forge Timestamp**: 2026-03-31T18:04:26.334550

---

## Code

*No code was produced for this combination.*

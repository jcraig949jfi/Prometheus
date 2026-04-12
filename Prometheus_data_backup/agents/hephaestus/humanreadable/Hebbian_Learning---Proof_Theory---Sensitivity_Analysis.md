# Hebbian Learning + Proof Theory + Sensitivity Analysis

**Fields**: Neuroscience, Mathematics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T21:09:03.467502
**Report Generated**: 2026-03-27T02:16:42.615229

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Atom Extraction** – Use regex to capture propositions:  
   - Atoms = predicates (e.g., “X > Y”, “cause(A,B)”, “¬P”).  
   - Store each unique atom in a list `atoms`; build dict `idx[atom] → i`.  
   - Build a binary matrix `A_ref` (reference answer) and `A_cand` (candidate) where `A[k,i]=1` if atom *i* appears in answer *k*.  

2. **Initial Proof‑Theory Graph** – From extracted conditionals (`if P then Q`) and causal clauses create a weighted adjacency matrix `W ∈ ℝ^{n×n}` (numpy).  
   - For each rule `P → Q`, set `W[idx[P], idx[Q]] = w0` (small positive seed).  
   - All other entries start at 0.  

3. **Hebbian Learning Update** – For each candidate‑reference pair:  
   ```
   delta = eta * (A_cand.T @ A_ref)          # outer product of co‑occurrences
   W += delta                                 # strengthen co‑fired synapses
   W *= (1 - lambda_decay)                    # weight decay (LTD analogue)
   ```  
   `eta` is learning rate, `lambda_decay` prevents unbounded growth.  

4. **Forward Chaining (Proof Normalization)** – Compute closure of implications:  
   ```
   activation = A_cand.copy()
   for _ in range(max_iter):
       new = activation @ W                     # numpy mat‑mul
       activation = np.clip(activation + new, 0, 1)   # keep in [0,1]
       if np.allclose(activation, activation @ W): break
   ```  
   The final `activation` vector represents provable atoms given the learned proof network.  

5. **Sensitivity Analysis** – Perturb each input feature (negation flip, numeric threshold ±ε, comparative reversal) and recompute the activation score `S = activation.sum()`.  
   - Approximate gradient: `g_i = (S_plus_i - S_minus_i) / (2ε)`.  
   - Sensitivity penalty: `pen = gamma * np.linalg.norm(g)`.  

6. **Final Score** – `score = S - pen`. Higher scores indicate answers that both provably follow from the reference and are robust to small perturbations.  

**Structural Features Parsed**  
Negations (`not`, `no`), comparatives (`greater than`, `less than`, `more`), conditionals (`if … then`, `unless`), causal claims (`because`, `leads to`), ordering relations (`before`, `after`, `precedes`), numeric values with units, equality/inequality (`=`, `≠`, `≤`, `≥`).  

**Novelty**  
Pure proof‑theoretic solvers ignore robustness; Hebbian‑style weight updates are used in neural nets, not symbolic reasoning; sensitivity analysis is common in uncertainty quantification but rarely coupled to forward‑chaining proof graphs. The triad forms a novel hybrid that jointly learns proof structure, evaluates derivability, and quantifies fragility.  

**Rating**  
Reasoning: 7/10 — captures logical consequence and robustness but approximates proof search with limited depth.  
Metacognition: 6/10 — provides a sensitivity signal that can guide self‑checking, yet lacks explicit uncertainty modeling.  
Hypothesis generation: 5/10 — generates implied atoms via forward chaining, but does not propose alternative hypotheses beyond the learned network.  
Implementability: 8/10 — relies only on regex, NumPy matrix ops, and basic loops; no external libraries or APIs needed.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Proof Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Chaos Theory + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

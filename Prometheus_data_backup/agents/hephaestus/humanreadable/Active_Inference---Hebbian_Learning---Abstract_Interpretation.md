# Active Inference + Hebbian Learning + Abstract Interpretation

**Fields**: Cognitive Science, Neuroscience, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:52:16.302746
**Report Generated**: 2026-03-27T16:08:16.442670

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract propositional tuples from a string:  
   - `(neg, X)` for “not X”  
   - `(comp, X, op, Y)` where `op ∈ {<,>,=,≤,≥}`  
   - `(cond, X, Y)` for “if X then Y”  
   - `(cause, X, Y)` for “X because Y”  
   - `(order, X, Y)` for “X before/after Y”  
   - `(num, X, value)` for numeric mentions.  
   Each tuple is one‑hot encoded into a sparse vector `v ∈ {0,1}^D` (D = number of distinct predicates).  

2. **Constraint propagation (Abstract Interpretation)** – Build a directed graph `G` whose edges are the extracted relations. Run a Floyd‑Warshall‑style transitive closure on `comp` and `order` edges to derive implied inequalities (e.g., if A < B and B < C then A < C). Store the resulting bound matrix `B` (numpy array) where `B[i,j]=1` means i must be less than j.  

3. **Hebbian weight matrix** – Initialize `W = zeros(D,D)`. For each prompt vector `v_p` and each candidate vector `v_c`, update:  
   `W += η (v_p[:,None] @ v_p[None,:] + v_c[:,None] @ v_c[None,:])`  
   (η = 0.01). This implements activity‑dependent strengthening.  

4. **Scoring (Active Inference)** – Compute prediction error:  
   `e = v_p - W @ v_c`  
   Expected free energy (variational bound):  
   `F = 0.5 * e.T @ e + λ * np.linalg.norm(v_c,1)`  
   (`λ = 0.1` penalizes complexity).  
   Final score = `-F` (higher = better).  
   If any candidate violates a bound in `B` (checked via numeric extraction), add a large penalty `C = 100`.  

**Structural features parsed** – negations, comparatives (`>`, `<`, `=`), conditionals, causal clauses, ordering/temporal relations, numeric values, and quantifier scopes (via “all/some” regex).  

**Novelty** – While Hebbian learning and predictive coding have been jointly studied, and abstract interpretation is standard for program analysis, binding them together to derive a free‑energy‑based scoring function over extracted logical propositions is not present in existing NLP evaluation tools.  

**Ratings**  
Reasoning: 7/10 — captures logical inference and uncertainty but relies on shallow syntactic patterns.  
Metacognition: 5/10 — the free‑energy term offers a rudimentary self‑assessment of prediction error, yet no explicit monitoring of search strategies.  
Hypothesis generation: 4/10 — weight updates reinforce co‑occurring propositions, but the system does not propose new hypotheses beyond scoring given candidates.  
Implementability: 9/10 — uses only NumPy and the stdlib; all steps are concrete matrix operations and regex parsing.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
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

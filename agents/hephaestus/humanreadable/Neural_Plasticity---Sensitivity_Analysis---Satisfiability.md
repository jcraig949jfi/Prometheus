# Neural Plasticity + Sensitivity Analysis + Satisfiability

**Fields**: Biology, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T18:15:12.011450
**Report Generated**: 2026-03-27T18:24:05.299832

---

## Nous Analysis

**Algorithm**  
We treat each prompt–candidate pair as a weighted Max‑SAT problem whose variables are atomic propositions extracted from the text.  

1. **Parsing (data structure)** – Using regex we extract:  
   - literals: `var` (e.g., “the drug reduces blood pressure”) with polarity (`+` for affirmative, `-` for negated).  
   - comparatives (`>`, `<`, `=`) → numeric constraints turned into pseudo‑boolean literals (e.g., `pressure < 120`).  
   - conditionals (`if … then …`) → implication clauses `(¬A ∨ B)`.  
   - causal cues (`because`, `leads to`) → same as conditionals.  
   - ordering relations (`before`, `after`) → temporal literals.  
   Each literal gets an integer ID; a clause is a Python list of `(var_id, is_negated)`. All clauses are stored in a NumPy integer matrix `C` of shape `(n_clauses, max_lits_per_clause)` with `-1` padding for unused slots.  

2. **Baseline satisfaction** – We run a unit‑propagation DPLL‑lite loop using only NumPy:  
   - Maintain a boolean assignment vector `a` (size `n_vars`).  
   - Repeatedly find unit clauses (all but one literal falsified) and assign the remaining literal to satisfy it; if a clause becomes all falsified, UNSAT.  
   - The number of satisfied clauses after propagation is `sat = C @ lit_mask > 0` (vectorized).  

3. **Sensitivity analysis** – For each clause we compute how many literals are *critical*: flipping that literal would change the clause’s satisfaction status.  
   - Critical count per clause: `crit = np.sum((C == lit_id) & (lit_mask == 0), axis=1)`.  
   - Overall sensitivity `sens = np.mean(crit) / max_lits_per_clause` (lower = more robust).  

4. **Neural‑plasticity weighting (Hebbian)** – We keep a weight matrix `W` (size `n_vars × n_vars)` initialized to zero. When a candidate matches a known gold answer (provided during tool calibration), we update:  
   - `ΔW = η * (x outer x)` where `x` is the binary literal activation vector of the gold answer.  
   - After each update we prune: set `W[|W| < τ] = 0` (synaptic pruning).  
   - Plasticity score for a candidate: `plast = (x @ W @ x) / (np.linalg.norm(x)**2 + ε)`.  

5. **Final score** –  
   `score = α * (sat / n_clauses) + β * (1 - sens) + γ * plast`  
   with α,β,γ summing to 1 (e.g., 0.4,0.3,0.3). The score lies in `[0,1]`; higher means the candidate better satisfies the logical constraints, is robust to small perturbations, and aligns with learned propositional co‑occurrence patterns.

**Parsed structural features** – Negations, comparatives (`>`, `<`, `=`), conditionals (`if‑then`), causal cues (`because`, `leads to`), numeric values, ordering relations (`before`, `after`), and conjunction/disjunction implied by punctuation.

**Novelty** – The core pieces (Max‑SAT solving, sensitivity‑based robustness, Hebbian weight updates) exist separately in SAT‑solvers, robust optimization, and cognitive‑modeling literature. Their tight integration into a single scoring function for answer evaluation is not commonly reported, making the combination novel in this specific application.

**Rating**  
Reasoning: 8/10 — captures logical structure and robustness, though limited to propositional granularity.  
Metacognition: 6/10 — sensitivity provides a rudimentary self‑check, but no explicit reflection on reasoning strategies.  
Hypothesis generation: 5/10 — weight matrix can suggest related propositions, yet no active hypothesis search.  
Implementability: 9/10 — relies only on NumPy and regex; all steps are straightforward to code.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

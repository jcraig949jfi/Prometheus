# Cognitive Load Theory + Metamorphic Testing + Satisfiability

**Fields**: Cognitive Science, Software Engineering, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T13:18:34.693743
**Report Generated**: 2026-03-27T16:08:16.463669

---

## Nous Analysis

The algorithm builds a lightweight constraint‑satisfaction model from the prompt and each candidate answer, then evaluates how well the answer preserves satisfiability under metamorphic transformations while penalizing unnecessary cognitive load.

**Data structures**  
- `VarMap`: dict mapping each extracted proposition (e.g., “X > Y”, “Z caused W”) to an integer variable ID.  
- `Clauses`: list of clause objects; each clause is a Python set of signed literals (positive for asserted, negative for negated).  
- `NumConstraints`: list of tuples `(coeff_array, bound)` where `coeff_array` is a 1‑D numpy array of variable coefficients and `bound` is a float; encodes linear inequalities from comparatives and arithmetic.  
- `OrderGraph`: adjacency list for temporal/ordering relations (before/after).  

**Parsing (structural features)**  
Regex patterns extract:  
- Negations (`not`, `no`) → negative literals.  
- Comparatives (`>`, `<`, `≥`, `≤`, `equal`) → linear inequalities in `NumConstraints`.  
- Conditionals (`if … then …`) → implication clauses `(¬A ∨ B)`.  
- Causal cue words (`because`, `leads to`) → treated as implications.  
- Ordering terms (`before`, `after`, `first`, `last`) → edges in `OrderGraph`.  
- Numeric tokens → coefficients for `NumConstraints`.  

**Operations**  
1. **Unit propagation** (pure Python loop) on `Clauses` to derive forced assignments; failure → unsatisfiable core.  
2. **Numeric feasibility**: solve the linear system with `numpy.linalg.lstsq`; if residuals > ε, mark conflict.  
3. **Metamorphic relations**: generate two variants of the input – (a) swap two independent ordering edges (should preserve satisfiability), (b) multiply all numeric coefficients by 2 (should preserve feasibility). Run steps 1‑2 on each variant; count violations.  
4. **Cognitive‑load weighting**:  
   - Intrinsic load ≈ number of variables (`len(VarMap)`).  
   - Extraneous load ≈ count of tokens not mapped to any clause or constraint.  
   - Germane load ≈ depth of propagation steps needed to reach a fixed point.  
   Load score = `intrinsic + 0.5*extraneous - 0.2*germane` (lower is better).  

**Scoring logic**  
For each candidate answer:  
`score = - (violations_from_metamorphic + penalty_for_unsatisfiable_core) - λ * load_score`  
where `violations_from_metamorphic` is the number of metamorphic tests that break satisfiability, and λ balances load vs. correctness. Higher scores indicate answers that preserve logical structure with minimal extraneous effort.

**Novelty**  
While SAT‑based answer validation and metamorphic testing exist separately, coupling them with a explicit cognitive‑load penalty to rank explanations is not documented in current tutoring‑system literature; the combination yields a new hybrid evaluator.

**Ratings**  
Reasoning: 8/10 — The method captures logical consistency, numeric feasibility, and order invariance, providing a principled reasoning score.  
Metacognition: 6/10 — Load estimation approximates awareness of mental effort but lacks true self‑monitoring of strategy shifts.  
Hypothesis generation: 5/10 — The system can suggest alternative assignments via propagation, yet it does not actively propose new explanatory hypotheses.  
Implementability: 9/10 — All components use only regex, basic Python data structures, and NumPy linear algebra; no external APIs or neural models are required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: unproductive
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

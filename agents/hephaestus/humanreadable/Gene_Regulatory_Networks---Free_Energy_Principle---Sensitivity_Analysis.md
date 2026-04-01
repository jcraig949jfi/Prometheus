# Gene Regulatory Networks + Free Energy Principle + Sensitivity Analysis

**Fields**: Biology, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T00:06:25.997158
**Report Generated**: 2026-03-31T18:45:06.784802

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Proposition Graph** – Use regex to extract atomic propositions (e.g., “X increases Y”, “not Z”, “value > 5”) and directed relations: *implies* (if‑then), *negation*, *comparative* (>, <, =), *causal* (because, leads to), *temporal* (before/after). Each proposition becomes a node; each relation becomes a weighted edge in an adjacency matrix **A** (size *n×n*). Edge weight = 1 for presence, 0 otherwise; for comparatives we store the numeric difference as a separate feature vector **f** (numpy array).  
2. **Gold‑Answer Reference** – Build the same structures (**A\***, **f\***) from the reference answer.  
3. **Prediction Error (Free Energy)** – Compute variational free energy approximation:  

\[
F = \frac{1}{2}\| (A - A^\*) \circ P \|_F^2 + \frac{1}{2}\| (f - f^\*) \circ Q \|_2^2
\]

where **P** and **Q** are diagonal precision matrices (inverse variance) set to 1 for all edges initially; ∘ denotes element‑wise product. This is a pure numpy Frobenius‑norm operation.  
4. **Sensitivity Analysis** – For each node *i*, perturb its truth value (flip 0↔1 or add ε to its numeric feature) and recompute **F**, yielding ∂F/∂xᵢ via finite differences. Assemble the sensitivity vector **s** = |∂F/∂x|. The robustness penalty is λ‖s‖₁ (λ = 0.1).  
5. **Score** – Lower free energy + sensitivity = better answer. Final score:  

\[
\text{Score}= -\bigl(F + \lambda\|s\|_1\bigr)
\]

Higher (less negative) scores indicate answers that closely match the reference structure and are robust to small perturbations.

**Parsed Structural Features**  
- Negations (“not”, “no”)  
- Comparatives (“greater than”, “less than”, “equal to”)  
- Conditionals (“if … then …”, “unless”)  
- Causal claims (“because”, “leads to”, “results in”)  
- Temporal/ordering (“before”, “after”, “while”)  
- Numeric values and units  
- Quantifiers (“all”, “some”, “none”)  

**Novelty**  
The triple blend mirrors recent structured‑prediction energy networks but adds a explicit sensitivity‑analysis term derived from the Free Energy Principle, which is not standard in current QA‑scoring tools. No known open‑source evaluator combines GRN‑style graph dynamics, variational free‑energy minimization, and robustness gradients in this way.

**Ratings**  
Reasoning: 8/10 — captures logical structure and uncertainty via free energy, though deeper semantic nuance remains limited.  
Metacognition: 6/10 — provides a robustness signal but does not explicitly model self‑monitoring of confidence.  
Hypothesis generation: 5/10 — the method scores given answers; generating new hypotheses would require additional search mechanisms.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and basic loops; readily producible in <200 lines.

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

**Forge Timestamp**: 2026-03-31T18:43:25.193067

---

## Code

*No code was produced for this combination.*

# Free Energy Principle + Sensitivity Analysis + Satisfiability

**Fields**: Theoretical Neuroscience, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T18:49:36.890493
**Report Generated**: 2026-03-31T17:05:22.363394

---

## Nous Analysis

**Algorithm – Variational Free‑Energy SAT Solver (VFESS)**  

1. **Parsing & Data Structures**  
   - *Atoms*: each extracted proposition (e.g., “X > Y”, “If A then B”, numeric value “price = 12”) becomes a Boolean variable \(p_i\) or a real‑valued node \(v_i\).  
   - *Clause set*: logical formulas are converted to conjunctive normal form (CNF) using standard Tseitin transformation; each clause \(C_j\) is stored as a list of literal indices.  
   - *Numeric constraints*: inequalities or equalities are turned into linear expressions \(a^\top x \le b\) and stored in a matrix \(A\) and vector \(b\).  
   - *Causal graph*: directed edges \(X\rightarrow Y\) extracted from causal language are stored as adjacency list \(G\).  

2. **Free‑Energy Approximation**  
   - Prediction error for each node \(i\) is \(e_i = v_i - \hat v_i\) where \(\hat v_i\) is the mean of its parents in \(G\) (linear regression coefficients learned via least‑squares on the current assignment).  
   - Variational free energy \(F = \frac12 e^\top \Sigma^{-1} e + \frac12 \log|\Sigma|\) where \(\Sigma\) is the covariance of prediction errors.  
   - Sensitivity analysis enters by weighting each error term with the Jacobian norm \(\| \partial v_i / \partial x\|\) (computed via finite differences on \(A\)), giving a robustness‑adjusted error \(w_i e_i^2\).  

3. **Scoring Logic**  
   - For a candidate answer, add its assertions as unit clauses (or additional numeric rows).  
   - Run a DPLL‑style SAT solver (pure Python, using numpy for matrix solves) to find a satisfying assignment that minimizes \(F\).  
   - The solver propagates unit clauses, applies transitivity on \(G\) (e.g., \(X\rightarrow Y\) and \(Y\rightarrow Z\) ⇒ \(X\rightarrow Z\)), and uses modus ponens on implication clauses.  
   - If the instance is unsatisfiable, the solver returns the minimal unsatisfiable core (MUC) via clause deletion; the free‑energy contribution of the MUC is added as a penalty.  
   - Final score \(S = -F\) (lower free energy → higher score).  

**Structural Features Parsed**  
- Negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), biconditionals, numeric values and units, ordering relations (“first”, “after”), causal verbs (“causes”, “leads to”), and quantifiers (“all”, “some”).  

**Novelty**  
The combination mirrors recent work on *energy‑based models* for logical reasoning (e.g., SATNet) and *sensitivity‑aware* probabilistic programming, but it explicitly couples variational free‑energy minimization with robustness‑weighted error terms and a pure‑numpy DPLL solver. No published tool integrates all three components in this exact form, making the approach novel for a lightweight, interpretable evaluation metric.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency, numeric constraints, and causal propagation in a principled objective.  
Metacognition: 6/10 — the method can estimate uncertainty via the covariance term but lacks explicit self‑reflection on its own parsing errors.  
Hypothesis generation: 5/10 — generates candidate worlds via SAT search but does not propose new hypotheses beyond satisfying existing constraints.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and a pure‑Python DPLL loop; no external libraries or APIs needed.

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

**Forge Timestamp**: 2026-03-31T17:05:00.057696

---

## Code

*No code was produced for this combination.*

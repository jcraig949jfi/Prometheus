# Constraint Satisfaction + Metamorphic Testing + Sensitivity Analysis

**Fields**: Computer Science, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T18:46:07.466240
**Report Generated**: 2026-03-27T03:26:12.444053

---

## Nous Analysis

The algorithm builds a lightweight constraint‑satisfaction problem (CSP) from the prompt, evaluates each candidate answer against that CSP, then refines the score using metamorphic relations (MRs) and a finite‑difference sensitivity analysis.  

**Data structures**  
- `Var`: a Python object holding a name, domain (set of possible values extracted via regex — numbers, entities, truth‑values), and current assignment.  
- `Constraint`: a tuple `(scope, func)` where `scope` is a list of `Var` objects and `func` returns `True` if the assignment satisfies the relation (e.g., `x > y`, `¬p`, `if p then q`).  
- `CSP`: adjacency list mapping each `Var` to the constraints it participates in.  
- `MR_table`: dictionary `{mr_id: transform_func}` where each `transform_func` takes an answer string and returns a perturbed version (e.g., double numeric values, swap ordering, negate a clause).  
- `Sens_matrix`: NumPy array storing partial derivatives of the CSP‑score w.r.t. each numeric variable (computed by central differences).  

**Operations**  
1. **Parsing** – Regex extracts numeric tokens, comparatives (`>`, `<`, `>=`, `<=`), ordering cues (`first`, `second`, `before`, `after`), negations (`not`, `never`), conditionals (`if … then …`), and causal markers (`because`, `leads to`). Each yields a `Var` and one or more `Constraint` objects added to the CSP.  
2. **CSP solving** – Apply arc consistency (AC‑3) to prune domains; then run a depth‑first backtracking search that stops after the first solution. The CSP‑score for a candidate answer is the fraction of constraints satisfied (`num_sat / total`).  
3. **Metamorphic testing** – For each MR in `MR_table`, generate a transformed answer, compute its CSP‑score, and check whether the expected relation holds (e.g., doubling a number should double the score if the constraint is linear). The MR‑score is the proportion of MRs satisfied.  
4. **Sensitivity analysis** – Perturb each numeric variable by ±ε (ε=1e‑3), recompute CSP‑score, and approximate ∂score/∂value via central differences. The sensitivity penalty is `1 / (1 + np.linalg.norm(grad))`, rewarding stable scores.  
5. **Final score** – `score = w1·CSP + w2·MR + w3·sensitivity`, with weights summing to 1 (e.g., 0.5, 0.3, 0.2).  

**Structural features parsed**  
Numeric values, comparatives, ordering relations, negations, conditionals, causal claims, temporal sequencers, and quantifiers (`all`, `some`, `none`).  

**Novelty**  
While CSP solvers, metamorphic testing, and sensitivity analysis each appear separately in AI‑education, software testing, and uncertainty quantification, their joint use to score free‑form reasoning answers is not documented in the literature. The approach ties logical consistency, output‑level invariances, and robustness to numeric perturbations into a single evaluator, which is novel for textual reasoning assessment.  

**Ratings**  
Reasoning: 8/10 — The CSP core captures logical structure well; metamorphic and sensitivity layers add nuance but rely on hand‑crafted MRs.  
Metacognition: 6/10 — The method can detect when an answer violates expected invariances, yet it does not explicitly model the answerer’s self‑monitoring process.  
Hypothesis generation: 5/10 — It evaluates given candidates rather than generating new hypotheses; hypothesis generation would require additional search mechanisms.  
Implementability: 9/10 — All components use only regex, backtracking, and NumPy; no external libraries or APIs are needed.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Constraint Satisfaction**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Bayesian Inference + Constraint Satisfaction + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Category Theory + Renormalization + Constraint Satisfaction (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

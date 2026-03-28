# Active Inference + Maximum Entropy + Sensitivity Analysis

**Fields**: Cognitive Science, Statistical Physics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:39:19.811731
**Report Generated**: 2026-03-27T02:16:41.829490

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract from the prompt and each candidate answer:  
   - Entities (noun phrases) → symbols *eᵢ*  
   - Predicates and relations → binary factors *r(eᵢ, eⱼ)* (e.g., “is‑greater‑than”, “causes”, “¬”)  
   - Comparatives → inequality constraints on attached numeric values  
   - Conditionals → implication factors *If A then B* encoded as ¬A ∨ B  
   - Causal claims → directed edge *A → B* with a strength variable  
   - Negations → flip polarity of the associated literal.  
   The output is a list of **constraint objects** `C = [(type, vars, coeff)]` where `type ∈ {equality, inequality, implication, exclusion}`.

2. **Maximum‑Entropy Prior** – Build a factor graph where each literal *Lₖ* is a Boolean variable. For each constraint add a potential that forces zero probability for violating assignments (hard constraint) or adds a linear term for soft numeric bounds. The MaxEnt distribution is the uniform distribution subject to these constraints; we obtain it by solving the linear system `A·p = b` with `numpy.linalg.lstsq`, yielding a belief vector `p₀` over all 2ⁿ possible worlds (n = number of literals, kept small by pruning irrelevant symbols).

3. **Active Inference Scoring** – For each candidate answer *a* we compute its **expected free energy**:  
   `F(a) = Expected surprise – λ·Epistemic value`  
   - Expected surprise = −log P(world satisfies a | p₀) = −log ∑₍w₎ p₀[w]·I(w⊨a).  
   - Epistemic value = sensitivity of the belief to perturbations: for each constraint *cᵢ* compute `∂P(a)/∂cᵢ ≈ (P₊ₑ – P₋ₑ)/(2ε)` using finite differences (`ε=1e-3`). Sum absolute sensitivities → information gain.  
   The final score is `S(a) = –F(a)` (higher = better).

**Structural features parsed** – negations, comparatives (`>`, `<`, `≥`, `≤`), conditionals (`if…then`), causal verbs (`because`, `leads to`), ordering relations (`before`, `after`, `precedes`), numeric values with units, conjunctive/disjunctive connectives, and explicit exclusions (`no`, `none`).

**Novelty** – While MaxEnt priors, active inference’s expected free energy, and sensitivity analysis appear separately in probabilistic logic, info‑theoretic RL, and robustness testing, their joint use to score reasoning answers—combining hard logical constraints with an epistemic‑value term derived from constraint perturbations—has not been described in existing QA or explanation‑evaluation tools.

**Ratings**  
Reasoning: 7/10 — captures logical consistency and information gain but relies on approximate belief propagation.  
Metacognition: 6/10 — epistemic value provides a rudimentary self‑assessment of uncertainty, yet lacks full recursive self‑modeling.  
Hypothesis generation: 5/10 — the model can propose worlds that satisfy constraints, but does not actively generate novel hypotheses beyond those implied by the prompt.  
Implementability: 8/10 — uses only regex, NumPy linear algebra, and basic loops; no external libraries or neural components required.

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

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

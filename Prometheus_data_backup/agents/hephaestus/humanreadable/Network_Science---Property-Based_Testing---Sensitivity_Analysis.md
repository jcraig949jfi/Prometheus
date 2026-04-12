# Network Science + Property-Based Testing + Sensitivity Analysis

**Fields**: Complex Systems, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:06:31.156118
**Report Generated**: 2026-03-27T06:37:39.450715

---

## Nous Analysis

**Algorithm**  
1. **Parse** each candidate answer and a reference answer with a fixed set of regex patterns to extract atomic propositions (e.g., “X > 5”, “Y ¬Z”, “if A then B”). Each proposition becomes a node in a directed graph G.  
2. **Edge construction**: for every extracted relation add an edge (u→v) labeled with a type from {IMPLIES, NEG, EQUIV, COMPARATIVE, CAUSAL, ORDER}. Store a weight w = 1 for hard constraints and w = 0.5 for soft defaults. Represent G as an adjacency matrix A ∈ {0,1}^{n×n} (numpy) and a parallel weight matrix W.  
3. **Constraint propagation**: compute the transitive closure T = (A > 0).astype(int) using repeated squaring (Boolean matrix multiplication) until convergence. This yields all implied relations (modus ponens, transitivity).  
4. **Base satisfaction score**: compare T against the reference closure T_ref. Let M = (T == T_ref).sum() and C = T_ref.size. S₀ = M/C ∈ [0,1].  
5. **Property‑based testing perturbation**: generate N random perturbations of the original text (flip a negation, add/subtract ε to a numeric constant, swap antecedent/consequent of a conditional). Use a shrinking loop: after each random change, if the new satisfaction Sᵢ < S₀ keep the change and try a smaller ε; otherwise discard. This yields a set {Sᵢ} of minimal‑failing inputs.  
6. **Sensitivity analysis**: treat the perturbation magnitude δ (e.g., ε for numerics, 1 for logical flips) as an input variable. Approximate the partial derivative of the score via finite differences: ∂S/∂δ ≈ (Sᵢ − S₀)/δᵢ. Compute the variance Var = np.var([∂S/∂δᵢ]) across all perturbations.  
7. **Final score**: Score = S₀ − λ·√Var, where λ ∈ [0,1] balances consistency vs. robustness (chosen via validation). All steps use only numpy and stdlib; no external calls.

**Structural features parsed**  
- Negations (“not”, “no”, “never”)  
- Comparatives (“>”, “<”, “≥”, “≤”, “equals”, “more than”)  
- Conditionals (“if … then …”, “unless”)  
- Causal claims (“because”, “leads to”, “results in”)  
- Ordering relations (“before”, “after”, “first”, “second”)  
- Numeric constants (integers, floats) and units  
- Conjunction/disjunction indicators (“and”, “or”)  

**Novelty**  
While each component—network‑based logical graphs, property‑based testing, and sensitivity analysis—exists separately, their integration into a single scoring pipeline that extracts propositional structure, propagates constraints, then stresses the structure with shrinking perturbations and quantifies output variance is not present in current educational‑assessment tools. Hence the combination is novel.

**Rating**  
Reasoning: 8/10 — captures logical structure and robustness, but may miss deep semantic nuance.  
Metacognition: 6/10 — the method can report sensitivity, giving insight into answer stability, yet lacks explicit self‑reflection on reasoning steps.  
Hypothesis generation: 7/10 — property‑based testing actively proposes minimal counter‑examples, functioning as a hypothesis‑generation mechanism.  
Implementability: 9/10 — relies only on regex, numpy Boolean matrix ops, and simple loops; readily achievable in pure Python.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Network Science**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Property-Based Testing**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Network Science + Sensitivity Analysis: negative interaction (-0.053). Keep these concepts in separate code paths to avoid interference.
- Property-Based Testing + Sensitivity Analysis: strong positive synergy (+0.489). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Free Energy Principle + Property-Based Testing + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-27T00:01:20.694974

---

## Code

*No code was produced for this combination.*

# Pragmatics + Sensitivity Analysis + Satisfiability

**Fields**: Linguistics, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T05:34:32.341642
**Report Generated**: 2026-03-27T06:37:51.784062

---

## Nous Analysis

**Algorithm**  
We build a lightweight weighted‑SAT engine that treats each extracted proposition as a Boolean variable *vᵢ*. A clause *Cⱼ* is a disjunction of literals (e.g., ¬v₁ ∨ v₃) obtained from syntactic patterns; each clause carries a pragmatic weight *wⱼ∈[0,1]* reflecting how strongly the context implicates its truth (higher for utterances that obey Grice’s maxims, lower for hedged or speculative language). All weights are stored in a NumPy array **W** of shape *(m,)* where *m* is the number of clauses.  

Given a candidate answer *A*, we encode it as a set of unit clauses *Uₐ* (e.g., v₅ = True). The scoring proceeds in three steps:

1. **Base satisfiability** – Run a unit‑propagation DPLL loop (pure Python, using NumPy only for fast weight look‑ups) on the clause set *C* ∪ *Uₐ*. If the formula is unsatisfiable, the base score *s₀* = 0; otherwise *s₀* = 1.  
2. **Sensitivity analysis** – Generate *k* perturbed versions of **W** by adding zero‑mean Gaussian noise σ=0.1 and clipping to [0,1]; for each perturbed weight vector **W′** repeat the DPLL check. Let *p* be the proportion of perturbations that flip the satisfiability outcome (i.e., cause a change from sat→unsat or vice‑versa). The sensitivity term is *σₛ* = *p*.  
3. **Final score** – *score* = *s₀* × (1 − *σₛ*). Thus a candidate that is robustly satisfied across perturbations receives a high score; a fragile satisfaction is penalized.

**Parsed structural features**  
- Negations (“not”, “no”, “never”) → ¬v  
- Comparatives (“greater than”, “less than”, “at least”) → arithmetic constraints translated to Boolean guards (e.g., value > 5 → v_gt5)  
- Conditionals (“if … then …”, “unless”) → implication clauses (¬ antecedent ∨ consequent)  
- Causal claims (“because …”, “leads to”) → treated as bidirectional implication for pragmatic weight  
- Ordering relations (“before”, “after”, “first”, “last”) → temporal precedence encoded as precedence variables  
- Numeric thresholds and quantifiers (“all”, “some”, “most”) → mapped to cardinality constraints that are expanded into clause sets via standard encoding (pairwise or ladder encoding).  
All extraction uses regular expressions over the raw token list; the resulting literals are indexed in a dictionary *var_map*.

**Novelty**  
The core is a weighted MaxSAT solver augmented with a Monte‑Carlo sensitivity check. Weighted MaxSAT and probabilistic soft logic exist, but they typically optimize a continuous loss rather than explicitly measuring robustness to input perturbations via repeated SAT calls. Combining pragmatic weighting (context‑dependent implicature) with a sensitivity‑analysis loop is not described in standard SAT‑based QA pipelines, making the combination novel in this specific formulation.

**Ratings**  
Reasoning: 8/10 — The algorithm performs genuine logical inference (unit propagation, DPLL) and evaluates robustness, capturing multi‑step reasoning beyond surface similarity.  
Metacognition: 6/10 — It can detect when its own conclusions are fragile (high sensitivity) but does not explicitly reason about its own uncertainty or propose alternative strategies.  
Hypothesis generation: 5/10 — The method scores given hypotheses; it does not generate new candidate answers or explore alternative parses on its own.  
Implementability: 9/10 — Only NumPy for array ops and the Python standard library (re, itertools, collections) are needed; the DPLL unit‑propagation loop is straightforward to code in <150 lines.

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

- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 


Similar combinations that forged successfully:
- Pragmatics + Hoare Logic + Satisfiability (accuracy: 0%, calibration: 0%)
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

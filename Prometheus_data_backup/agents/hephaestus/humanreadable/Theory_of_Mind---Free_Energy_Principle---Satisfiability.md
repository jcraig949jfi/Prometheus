# Theory of Mind + Free Energy Principle + Satisfiability

**Fields**: Cognitive Science, Theoretical Neuroscience, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T18:14:04.300161
**Report Generated**: 2026-03-27T05:13:35.363550

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using regex we extract atomic propositions from a candidate answer and annotate each with:  
   * polarity (¬),  
   * comparative operators turned into arithmetic constraints (e.g., “X > 5” → X‑5 ≥ 0),  
   * conditionals → implication clauses (A → B),  
   * causal claims → directed edges treated as implication with weight w_c,  
   * ordering relations → transitive constraints (A < B ∧ B < C ⇒ A < C).  
   Each literal also carries a *belief tag* b∈{0,1,2} indicating whether it is asserted as the speaker’s belief, attributed to another agent, or recursively attributed ( Theory of Mind depth).  

2. **Factor‑graph construction** – Every extracted clause becomes a factor φ_i over its literals. The factor’s energy is:  
   \[
   E_i = w_i \cdot [\text{clause unsatisfied}]
   \]  
   where w_i combines:  
   * a base weight from syntactic confidence (e.g., higher for explicit conditionals),  
   * a belief‑mismatch penalty derived from the Free Energy Principle:  
     \[
     \text{penalty}= \lambda \cdot \text{KL}\big(P_{\text{model}}(b)\,||\,P_{\text{prior}}(b)\big)
     \]  
     approximated by a squared difference between the literal’s belief tag and a prior belief distribution (set uniformly for depth 0, decaying with depth).  
   All factors are stored in a NumPy array of shape (n_clauses, n_literals) with entries ∈{‑1,0,1} indicating literal polarity.

3. **Inference / scoring** – We run a lightweight weighted‑MaxSAT procedure:  
   * Initialize all variables to False.  
   * Iterate unit propagation using NumPy dot‑products to detect forced assignments.  
   * When a conflict appears, compute the clause‑weight sum of the conflicting set (a minimal unsatisfiable core) and add its weight to the total energy.  
   * Flip the variable with highest weighted impact (gradient‑free hill‑climb) and repeat until no improvement.  
   The final energy E = ∑E_i is the variational free‑energy proxy; the candidate score is S = ‑E (lower free energy → higher score).  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, numeric thresholds, ordering relations, and belief‑depth markers (e.g., “John thinks that Mary believes …”).  

**Novelty** – While Markov Logic Networks and Probabilistic Soft Logic already blend weighted SAT with probabilistic semantics, the explicit integration of Theory‑of‑Mind recursion into the free‑energy formulation and the use of a pure‑numpy, clause‑weight hill‑climbing solver is not present in existing work.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and belief reasoning via energy minimization.  
Metacognition: 7/10 — models agents’ beliefs but lacks explicit self‑monitoring of uncertainty.  
Hypothesis generation: 6/10 — generates alternative assignments through local search, yet no principled proposal distribution.  
Implementability: 9/10 — relies only on regex, NumPy array ops, and simple loop‑based SAT heuristics, all feasible in stdlib‑plus‑NumPy.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: unproductive
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Theory of Mind**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 


Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

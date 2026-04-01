# Compositionality + Free Energy Principle + Metamorphic Testing

**Fields**: Linguistics, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T03:53:10.679693
**Report Generated**: 2026-03-31T19:52:13.001000

---

## Nous Analysis

The algorithm builds a **compositional factor graph** from each prompt‑answer pair, treats the graph as a variational free‑energy system, and uses metamorphic relations as hard constraints during inference.

1. **Parsing & data structures**  
   - Tokenise the prompt and each candidate answer with regexes that extract:  
     * atomic predicates (e.g., “X is Y”, “X > Y”),  
     * negations (`not`),  
     * comparatives (`>`, `<`, `>=`, `<=`),  
     * conditionals (`if … then …`),  
     * causal cues (`because`, `leads to`),  
     * ordering tokens (`before`, `after`),  
     * numeric constants.  
   - Each atomic predicate becomes a binary variable node \(v_i\in\{0,1\}\).  
   - Every extracted syntactic fragment (e.g., a negated predicate, a conditional antecedent‑consequent pair, a comparative chain) defines a **factor** \(f_k\) that connects the involved variables. The factor’s potential is a simple compatibility table: for a conjunction it rewards both true, for a conditional it penalises antecedent = true & consequent = false, for a comparative it enforces the numeric ordering, etc.  
   - Metamorphic relations are added as extra factors:  
     * *Scale*: if a numeric variable \(v_n\) appears, a factor links \(v_n\) and \(2·v_n\) (error = |value‑2·value|).  
     * *Order‑preservation*: for any ordering chain \(a<b<c\), a factor penalises violations of transitivity.  
   - All factors are stored in a list; the adjacency of variables to factors is kept in two NumPy arrays (`var_to_factor_idx`, `factor_to_var_idx`) for fast lookup.

2. **Free‑energy scoring**  
   - Initialise a mean‑field variational distribution \(q_i = \sigma(\mu_i)\) (logits \(\mu_i\) stored in a NumPy vector).  
   - Iterate a few mean‑field updates: for each variable, compute the expected free‑energy contribution of its incident factors using current \(q\) of neighbours (standard sum‑product on binary factors). Update \(\mu_i\) to minimise local free energy (equivalent to a gradient step on \(\sum_k \text{KL}(q\|p_k)\)).  
   - After convergence, compute the **variational free energy**  
     \[
     F = \sum_k \langle E_k\rangle_q - \sum_i H(q_i)
     \]
     where \(\langle E_k\rangle_q\) is the average factor error (squared deviation from the factor’s ideal truth table) and \(H\) is the Bernoulli entropy. Lower \(F\) indicates the candidate answer better satisfies the compositional, predictive, and metamorphic constraints. The final score is \(-F\) (higher is better).

3. **Structural features parsed**  
   Negations, comparatives, conditionals, causal verbs, ordering tokens, numeric constants, and conjunction/disjunction structures.

4. **Novelty**  
   Pure compositional factor graphs exist in probabilistic soft logic; free‑energy minimization appears in variational inference; metamorphic constraints are used in testing. The specific combination — using metamorphic relations as hard factors inside a free‑energy‑driven mean‑field inference over a compositionally parsed logical graph — has not been described in prior work, making the approach novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and prediction error but remains approximate.  
Metacognition: 5/10 — limited self‑monitoring; only implicit via free‑energy gradient.  
Hypothesis generation: 6/10 — can propose alternative truth assignments via variational updates.  
Implementability: 8/10 — relies solely on regex, NumPy linear algebra, and standard‑library loops.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Compositionality + Free Energy Principle: strong positive synergy (+0.137). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Metamorphic Testing: negative interaction (-0.062). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Kolmogorov Complexity + Compositionality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Plasticity + Compositionality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:51:26.456436

---

## Code

*No code was produced for this combination.*

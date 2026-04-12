# Compositionality + Free Energy Principle + Maximum Entropy

**Fields**: Linguistics, Theoretical Neuroscience, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T15:20:57.496867
**Report Generated**: 2026-03-31T19:23:00.417012

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositionality)** – Use regex to extract atomic propositions and their logical connectives from the prompt and each candidate answer. Each proposition becomes a Boolean variable *vᵢ*. Connectives are turned into factors:  
   * ¬p → unary factor favoring *vᵢ = false*  
   * p ∧ q → binary factor with potential 1 only when both true*  
   * p → q → binary factor penalizing *vᵢ = true, vⱼ = false*  
   * numeric constraints (e.g., “>5”, “=3”) → unary factors over a numeric variable *uₖ* with domain discretized to a small set of values (e.g., 0‑10).  
   All factors are stored as NumPy arrays; the scope of each factor is a list of variable indices.

2. **Constraint‑driven Maximum Entropy** – Initialise a uniform distribution over all variable assignments (max‑entropy prior). For each factor *f* with potential *φ_f*, add a linear constraint that the expected log‑potential under the distribution equals the empirical log‑potential (which is simply log φ_f evaluated on the observed truth values from the prompt). Solve the resulting exponential‑family distribution by iterative proportional fitting (IPF): repeatedly project the current distribution onto each factor’s constraint using NumPy tensor operations. This yields the max‑entropy distribution *P* that satisfies all compositional constraints.

3. **Free‑Energy Principle Scoring** – Compute the variational free energy *F* = ⟨ −log P ⟩_Q + KL(Q‖P) where *Q* is a mean‑field approximation (product of independent Bernoulli/multinomials). In practice, after IPF we already have *P*; we approximate *Q* by the current marginals (the IPF fixed point). Free energy reduces to the negative log‑likelihood of the observed constraints under *P* plus the entropy term, both computable with NumPy.  
   To score a candidate answer *c*, add a unit factor that forces the relevant proposition(s) to the truth value asserted by *c*, re‑run a few IPF sweeps (cheap because only one factor changes), and compute the resulting free energy *F_c*. The score is *−F_c* (lower free energy → higher confidence).  

**Structural Features Parsed** – Negations, conjunctions/disjunctions, conditionals (if‑then), comparatives (> , < , ≥ , ≤), equality/inequality numeric statements, causal claims (“because”, “leads to”), ordering relations (transitive chains such as “A > B > C”), and explicit quantifiers (“all”, “some”).

**Novelty** – The pipeline mirrors Markov Logic Networks and Probabilistic Soft Logic but replaces weighted‑logic learning with a pure maximum‑entropy / variational‑free‑energy inference loop that can be built from NumPy and the std‑lib alone. No existing lightweight evaluation tool combines these three principled layers in this exact way, so the approach is novel for the stated constraints.

**Ratings**  
Reasoning: 7/10 — captures logical structure well but struggles with vague or probabilistic language.  
Metacognition: 5/10 — no mechanism for self‑monitoring or adjusting inference depth.  
Hypothesis generation: 6/10 — can sample alternative assignments from the max‑entropy distribution, giving rudimentary hypotheses.  
Implementability: 8/10 — relies only on NumPy for tensor ops and Python’s re/std‑lib for parsing.

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
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Compositionality + Free Energy Principle: strong positive synergy (+0.137). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Maximum Entropy: strong positive synergy (+0.241). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ergodic Theory + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Kolmogorov Complexity + Compositionality + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Neural Plasticity + Compositionality + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:22:35.229575

---

## Code

*No code was produced for this combination.*

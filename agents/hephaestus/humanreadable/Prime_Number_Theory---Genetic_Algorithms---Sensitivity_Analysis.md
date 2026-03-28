# Prime Number Theory + Genetic Algorithms + Sensitivity Analysis

**Fields**: Mathematics, Computer Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T05:28:04.192323
**Report Generated**: 2026-03-27T06:37:52.104056

---

## Nous Analysis

**Algorithm**  
Each prompt and candidate answer is first parsed into a set of atomic propositions Pᵢ (e.g., “X > Y”, “¬Z”, “if A then B”). Every distinct proposition type is assigned a unique prime number pᵢ via a lookup table built from the first N primes (N ≈ number of unique propositions observed in the training corpus). A proposition set is encoded as the product Π pᵢᵉⁱ, where the exponent eᵢ is 1 if the proposition appears positively, ‑1 if it appears negated, and 0 otherwise. This yields an integer S that uniquely represents the logical content (up to ordering) and allows fast set‑intersection via gcd: overlap = gcd(S_prompt, S_candidate).  

A population of candidate encodings evolves with a standard genetic algorithm: selection proportional to fitness, single‑point crossover on the binary exponent vectors, and mutation that flips the sign of a randomly chosen exponent (adding or removing a proposition, or toggling negation).  

Fitness combines two terms:  
1. **Reasoning score** = log(gcd)/log(max_possible) – measures how many prompt propositions are recovered.  
2. **Sensitivity penalty** = average |Δlog S| over k random input perturbations (e.g., swapping a synonym, flipping a comparator). Perturbations are applied to the prompt before encoding; the penalty quantifies how much the candidate’s encoding changes when the prompt is slightly altered.  

Final fitness = Reasoning − λ·Sensitivity (λ ≈ 0.2). The highest‑fitness individual after a fixed number of generations provides the scored answer; its fitness value is the output score.

**Structural features parsed**  
Negations (“not”, “no”), comparatives (“greater than”, “less than”, “≤”, “≥”), conditionals (“if … then …”, “unless”), causal claims (“because”, “leads to”, “results in”), numeric values and units, ordering relations (“first”, “last”, “between”), and quantifiers (“all”, “some”, “none”). These are extracted via deterministic regex patterns and converted to propositions.

**Novelty**  
Genetic algorithms have been used for answer ranking, and prime‑based hashing appears in checksum and set‑similarity tricks, while sensitivity analysis is common in robustness testing. The specific fusion—using prime factorization to represent logical structure, evolving candidates with a GA, and scoring via a sensitivity‑adjusted overlap metric—has not been described in the literature to the best of my knowledge, making the combination novel.

**Ratings**  
Reasoning: 7/10 — captures logical overlap well but struggles with deep semantic nuance.  
Metacognition: 5/10 — the method does not explicitly model its own uncertainty or learning dynamics.  
Hypothesis generation: 6/10 — GA can propose new proposition combinations, yet guided mainly by fitness, not exploratory curiosity.  
Implementability: 8/10 — relies only on numpy (for array ops) and std‑library (regex, random, math); straightforward to code.

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

- **Prime Number Theory**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Genetic Algorithms**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Ecosystem Dynamics + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Ergodic Theory + Compressed Sensing + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

# Matched Filtering + Type Theory + Sensitivity Analysis

**Fields**: Signal Processing, Logic, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T02:10:04.137608
**Report Generated**: 2026-03-27T02:16:36.772273

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Typed Feature Vectors**  
   - Use a deterministic regex‑based parser to extract a finite set of atomic predicates from the prompt and each candidate answer:  
     *Negation* (`not`, `no`), *Comparative* (`more`, `less`, `-er`), *Conditional* (`if … then`, `implies`), *Numeric* (any integer/float), *Causal claim* (`because`, `due to`, `leads to`), *Ordering* (`>`, `<`, `≥`, `≤`, `before`, `after`).  
   - Each atomic predicate is assigned a simple type from a miniature type theory: `Prop` (truth‑valued), `Num` (real), `Ord` (order relation), `Caus` (cause‑effect). Dependent types are not needed for scoring; the type merely determines which feature slot the predicate occupies.  
   - Build a binary feature vector **f** ∈ {0,1}^k where k is the number of distinct predicate‑type pairs (e.g., `Negation:Prop`, `Comparative:Num`, `Causal:Caus`). For numeric tokens, store the actual value in a parallel real‑valued vector **n** ∈ ℝ^m (m = number of numeric extracts).  

2. **Matched‑Filter Core**  
   - Let **r** be the reference feature vector derived from a human‑provided gold answer (or a consensus answer).  
   - Estimate per‑dimension variance σ_i² from a sensitivity analysis: perturb each input token (swap a negation, add/subtract 1 to a number, flip a conditional) and measure the change in a baseline logical‑consistency score (computed via simple modus‑ponens/chaining on the typed predicates). The average absolute change gives σ_i.  
   - Form the matched‑filter weight vector **w** where w_i = 1/σ_i (dimensions with low sensitivity → high weight).  
   - The raw match score is the dot product **y** = w · (f_cand ⊙ f_ref) + λ·(w_n · (n_cand ⊙ n_ref)), where ⊙ is element‑wise product and λ balances predicate vs. numeric contributions (set λ = 0.5).  
   - Normalize by √(w·w) to obtain a signal‑to‑noise ratio‑like value: **S** = y / √(w·w). Higher **S** indicates the candidate answer correlates strongly with the reference pattern while being robust to small perturbations.  

3. **Scoring Logic**  
   - Return **S** as the final score; optionally map to [0,1] via a sigmoid if a bounded output is desired.  

**Structural Features Parsed**  
Negations, comparatives, conditionals, numeric values, causal claims, ordering relations, equality, and basic quantifiers (each mapped to a typed predicate slot).  

**Novelty**  
Matched filtering is classic in signal processing; type‑theoretic parsing appears in proof‑assistant front‑ends; sensitivity analysis is used in uncertainty quantification. Combining them to weight a cross‑correlation of typed logical features for answer scoring has not, to my knowledge, been published in the NLP or educational‑assessment literature, making the approach novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and robustness but relies on hand‑crafted predicates.  
Metacognition: 5/10 — no explicit self‑monitoring or uncertainty estimation beyond sensitivity weights.  
Hypothesis generation: 6/10 — can suggest alternative parses via perturbation but does not generate novel hypotheses autonomously.  
Implementability: 8/10 — uses only regex, numpy dot products, and basic logic; feasible in <200 lines.

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

- **Matched Filtering**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Type Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Active Inference + Mechanism Design + Type Theory (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Pragmatism + Type Theory (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

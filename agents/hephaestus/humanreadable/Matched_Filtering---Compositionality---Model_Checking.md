# Matched Filtering + Compositionality + Model Checking

**Fields**: Signal Processing, Linguistics, Formal Methods
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T04:04:06.987327
**Report Generated**: 2026-03-27T05:13:42.553568

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Proposition Extraction** – Using regex, the prompt and each candidate answer are tokenized into atomic predicates (e.g., `X > Y`, `¬P`, `if A then B`, `cause(C,E)`, numeric literals). Each predicate receives a unique ID and is stored as a tuple `(id, polarity, args)`.  
2. **Bit‑vector Encoding** – For a fixed universe of `N` possible predicates (derived from the union of prompt + all candidates), each text is represented by a binary vector `v ∈ {0,1}^N` where `v[i]=1` iff predicate *i* appears. Negation flips the bit in a separate “negative” vector `v⁻`.  
3. **Matched‑filter Correlation** – A reference vector `r` is built from the prompt’s specification (the conjunction of all extracted predicates that must hold). The raw similarity score is the normalized cross‑correlation:  
   `s_corr = (v·r) / (||v||·||r||)` (numpy dot product). This rewards answers that contain the expected signal while penalizing extra or missing components.  
4. **Constraint‑based Model Checking** – From the prompt we derive a set of logical constraints (transitivity of `>`, modus ponens for conditionals, consistency rules for negations). These constraints define a finite‑state transition system where each state is a bit‑vector assignment to predicates. Using a simple breadth‑first search (standard library collections.deque) we enumerate all reachable states that satisfy the constraints.  
5. **Specification Satisfaction** – The candidate answer vector `v` is checked against the state space: if `v` (or its closure under the constraints) is a member of the satisfying set, we assign `s_model = 1`; otherwise `s_model = 0`. A softened version computes the fraction of satisfying states reachable from `v` by flipping at most *k* bits (Hamming ball), yielding a graded score.  
6. **Compositional Aggregation** – The final score combines the two components:  
   `Score = α·s_corr + β·s_model`, with α,β set to 0.5 (equal weight) or tuned via simple variance weighting on a validation set.  
   Because the score is a linear combination of independently computed, interpretable terms, the method respects compositionality: the contribution of each extracted predicate can be inspected.

**Structural Features Parsed**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `≥`, `≤`)  
- Conditionals (`if … then …`, `only if`)  
- Causal cues (`because`, `leads to`, `results in`)  
- Numeric values and units  
- Ordering/temporal relations (`before`, `after`, `precedes`)  
- Conjunctions/disjunctions (`and`, `or`)  

**Novelty**  
Pure model‑checking approaches exist for formal verification and some NLI systems, and matched filtering is classic in signal processing. Combining them with a compositional, predicate‑level vector representation to score free‑form answers is not present in mainstream NLP evaluation toolkits; the closest work uses logical form similarity or theorem proving without the correlation‑based filtering step, making this hybrid novel in the context of automated reasoning assessment.

**Rating**  
Reasoning: 7/10 — captures logical consistency and signal‑like relevance but relies on shallow predicate extraction.  
Metacognition: 5/10 — limited self‑reflection; the method does not estimate its own uncertainty beyond the two‑term score.  
Hypothesis generation: 6/10 — can propose alternative worlds via the state‑space search, yet generation is constrained to bit‑flips near the candidate.  
Implementability: 8/10 — uses only numpy for vector ops and std‑lib collections for BFS; no external dependencies.

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
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Model Checking**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Mechanism Design + Model Checking (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

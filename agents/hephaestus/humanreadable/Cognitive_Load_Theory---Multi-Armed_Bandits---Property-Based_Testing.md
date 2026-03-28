# Cognitive Load Theory + Multi-Armed Bandits + Property-Based Testing

**Fields**: Cognitive Science, Game Theory, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T13:15:10.336910
**Report Generated**: 2026-03-27T05:13:38.161084

---

## Nous Analysis

**Algorithm: Bandit‑Guided Property‑Based Consistency Scorer (BPCS)**  

1. **Prompt preprocessing (structural parsing)** – Using only the standard library, the prompt is scanned with regex patterns to extract a set \(P\) of primitive propositions:  
   - Negations (`not`, `no`) → Boolean flag.  
   - Comparatives (`greater than`, `less than`, `>=`, `<=`) → numeric inequality tuples.  
   - Conditionals (`if … then …`) → implication pairs.  
   - Causal cues (`because`, `leads to`) → directed edges.  
   - Ordering relations (`first`, `before`, `after`) → partial‑order constraints.  
   Each proposition is stored as a lightweight tuple (type, operands, polarity). The total number of propositions is capped by a working‑memory chunk limit \(C\) (e.g., \(C=4\)) derived from Cognitive Load Theory: we keep the \(C\) most “intrinsic” propositions (those with the highest term frequency‑inverse document frequency score computed on‑the‑fly) and discard the rest as extraneous load.

2. **Candidate representation** – Each answer \(a_i\) is converted into the same proposition set \(Q_i\) via the same parser.

3. **Property‑based test generation** – For each proposition \(p\in P\) we generate a property \(\phi_p\) that must hold in any correct answer:  
   - Equality/inequality → numeric check using `numpy.allclose`.  
   - Implication → verify that antecedent in \(Q_i\) entails consequent (modus ponens via subset check).  
   - Causal/ordering → check transitive closure with Floyd‑Warshall on a small adjacency matrix (size ≤ \(C\)).  
   Shrinking is attempted by iteratively removing propositions from \(Q_i\) and re‑testing to find a minimal failing subset.

4. **Bandit‑driven evaluation budget** – Treat each answer as an arm of a multi‑armed bandit. Initialize arm scores \(s_i=0\) and pulls \(n_i=0\). For a fixed budget \(B\) (e.g., \(B=20\) evaluations):  
   - Compute Upper Confidence Bound: \(UCB_i = s_i/n_i + \sqrt{2\ln(\sum n_k)/n_i}\).  
   - Pull the arm with highest \(UCB_i\) (explore‑exploit trade‑off).  
   - Run the property‑based test suite on that answer; increment \(n_i\) and update \(s_i\) by adding the proportion of satisfied properties (range [0,1]).  
   - After \(B\) pulls, return the final normalized score \(s_i/n_i\) as the answer’s rating.

5. **Scoring logic** – The final score reflects how well the answer satisfies the intrinsic logical structure of the prompt while respecting limited working‑memory bandwidth; the bandit ensures we focus evaluation on promising candidates, and property‑based shrinking yields diagnostics for failures.

**Structural features parsed** – negations, comparatives, conditionals, causal cues, ordering relations, numeric values, and logical connectives (AND/OR implicit in conjunction of propositions).

**Novelty** – The triplet combination is not documented in existing literature; while each component appears separately (e.g., bandits for active testing, property‑based testing in Hypothesis, cognitive‑load‑aware feature selection), their joint use to allocate a bounded evaluation budget over logical constraints is novel.

**Rating**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency via constraint propagation and numeric checks, capturing core reasoning steps.  
Metacognition: 7/10 — Working‑memory chunking models self‑regulation of load, but lacks explicit monitoring of strategy shifts.  
Hypothesis generation: 6/10 — Property‑based shrinking generates minimal counter‑examples, yet hypothesis space is limited to parsed propositions.  
Implementability: 9/10 — All steps rely on regex, basic data structures, and NumPy for vectorized numeric tests; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Multi-Armed Bandits**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Property-Based Testing**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

Similar combinations that forged successfully:
- Cognitive Load Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Cellular Automata + Cognitive Load Theory + Phenomenology (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

# Criticality + Maximum Entropy + Normalized Compression Distance

**Fields**: Complex Systems, Statistical Physics, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:17:36.294991
**Report Generated**: 2026-03-27T06:37:39.510713

---

## Nous Analysis

The algorithm builds a lightweight logical‑feature extractor, derives maximum‑entropy weights for those features from the prompt, measures how close the weight distribution is to a critical point, and finally blends a compression‑based similarity score with a feature‑match score.

**Data structures**  
- `props`: list of tuples `(subj, rel, obj, modality)` where `modality` ∈ {negation, comparative, conditional, causal, numeric, ordering}. Extracted via a handful of regex patterns (e.g., `r'\bnot\b'` for negation, `r'\bif\s+.+?\bthen\b'` for conditional, `r'\d+(?:\.\d+)?\s*\w+'` for numeric).  
- `feat_counts`: 6‑element numpy array counting each modality in the prompt.  
- `weights`: 6‑element numpy array of MaxEnt parameters λ_i.  
- `entropy`: scalar Shannon entropy of the normalized weight distribution.

**Operations**  
1. **Feature extraction** – run the regex set on prompt and each candidate answer, filling `props` and computing answer‑side modality counts `c_ans`.  
2. **Maximum‑entropy weighting** – solve for λ that satisfies Σ_i λ_i * feat_counts[i] = log Z (partition function) using iterative scaling (GIS) with only numpy dot‑products and log‑sum‑exp. This yields the least‑biased distribution consistent with the prompt’s observed feature frequencies.  
3. **Criticality factor** – compute `H = - Σ p_i log p_i` where `p_i = exp(λ_i)/Σ exp(λ_i)`. Let `H_max = log(6)`. Define `crit = 1 - |H - H_max|/H_max`; `crit` peaks near 0 when the weight distribution is flat (maximum entropy, i.e., the system is at the critical point between order and disorder).  
4. **Similarity scoring** – compute Normalized Compression Distance (NCD) between the raw prompt string and each candidate answer using `zlib.compress` (approximation of Kolmogorov complexity). `ncd = (C(prompt+answer) - min(C(prompt),C(answer))) / max(C(prompt),C(answer))`. Lower NCD means higher algorithmic similarity.  
5. **Final score** – `score = (1 - crit) * (1 - ncd) + crit * (1 - cosine_distance(feat_counts, c_ans))`. When the system is critical (`crit≈1`) the score relies on feature‑match; away from criticality it leans on compression similarity.

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`more`, `less`, `>`, `<`), conditionals (`if…then`, `unless`), causal claims (`because`, `leads to`, `results in`), numeric values (integers, floats with units), ordering relations (`first`, `second`, `before`, `after`, `greater than`, `less than`). Conjunctions (`and`, `or`) are also captured to preserve scope.

**Novelty**  
While NCD has been used for plagiarism detection and MaxEnt for language modeling, coupling them with a criticality‑based switch that dynamically weights compression similarity against logical‑feature matching is not described in the literature. Existing work treats either similarity or logical reasoning in isolation; this hybrid explicitly tunes the balance via an entropy‑driven phase transition, making the combination novel for answer scoring.

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on shallow regex parsing.  
Metacognition: 5/10 — no explicit self‑monitoring of extraction errors or weight convergence.  
Hypothesis generation: 6/10 — feature weights suggest plausible relations but do not generate new hypotheses.  
Implementability: 8/10 — uses only numpy, re, zlib, and basic loops; feasible in <150 lines.

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

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Criticality + Maximum Entropy: negative interaction (-0.066). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Adaptive Control + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Evolution + Criticality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

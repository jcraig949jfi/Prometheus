# Fractal Geometry + Sparse Autoencoders + Neural Oscillations

**Fields**: Mathematics, Computer Science, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T13:54:19.776065
**Report Generated**: 2026-03-26T14:35:10.497003

---

## Nous Analysis

The algorithm builds a multi‑scale sparse code of logical primitives and scores answers by cross‑frequency coupling of those codes.

**Data structures**  
- `chunks[l]`: list of text segments at fractal level `l` (0 = whole sentence, 1 = clause, 2 = phrase).  
- `F`: binary feature matrix `[n_chunks × n_primitives]` where primitives are regex‑detected negations, comparatives, conditionals, causal cues, ordering tokens, numbers, quantifiers.  
- `D`: overcomplete dictionary `[n_primitives × n_atoms]` learned per level by iterative hard‑thresholding (a sparse‑autoencoder step).  
- `A[l]`: sparse activation matrix `[n_chunks × n_atoms]` from ISTA (`A = shrink(DᵀF, λ)`).  
- `pow_low[l] = mean(A[l], axis=0)`, `pow_high[l] = var(A[l], axis=0)`.  

**Operations**  
1. Parse the prompt and each candidate with regexes to fill `F`.  
2. Recursively split text at punctuation depth to create the fractal hierarchy (`chunks[l]`).  
3. For each level `l`, run a fixed number of ISTA iterations (numpy matrix multiplies + soft‑threshold) to obtain `A[l]`.  
4. Compute cross‑frequency coupling `C[l] = pow_low[l] · pow_high[l]` (dot product).  
5. Obtain reference sparse code `A_ref[l]` from the gold answer.  
6. Score candidate `c` as `S = Σ_l C[l] * cosine(A_c[l], A_ref[l])`. Higher `S` indicates better logical alignment.

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`more`, `less`, `-er`), conditionals (`if`, `unless`, `then`), causal claims (`because`, `leads to`, `causes`), ordering relations (`before`, `after`, `first`, `last`), numeric values (integers, fractions, percentages), quantifiers (`all`, `some`, `none`).

**Novelty**  
While hierarchical parsing, sparse coding, and oscillatory coupling appear separately in neuroscience‑inspired NLP, their joint use as a scoring mechanism — fractal decomposition → level‑wise sparse autoencoding → theta‑gamma coupling — has not been combined in existing reasoning‑evaluation tools.

**Ratings**  
Reasoning: 7/10 — captures multi‑scale logical structure but relies on hand‑crafted primitives.  
Metacognition: 5/10 — no explicit self‑monitoring of confidence beyond the coupling score.  
Hypothesis generation: 6/10 — sparse activations hint at latent features, yet no generative proposal step.  
Implementability: 8/10 — only numpy and stdlib; regex, recursive splitting, ISTA loops are straightforward.

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

- **Fractal Geometry**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sparse Autoencoders**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Neural Oscillations**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Abductive Reasoning + Causal Inference + Neural Oscillations (accuracy: 0%, calibration: 0%)
- Active Inference + Neural Oscillations + Mechanism Design (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Neural Oscillations + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

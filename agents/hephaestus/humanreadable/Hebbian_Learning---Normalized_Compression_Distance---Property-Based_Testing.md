# Hebbian Learning + Normalized Compression Distance + Property-Based Testing

**Fields**: Neuroscience, Information Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T05:10:13.986769
**Report Generated**: 2026-03-27T05:13:42.839563

---

## Nous Analysis

Combining Hebbian learning, Normalized Compression Distance (NCD), and property‑based testing yields a **similarity‑driven constraint‑propagation scorer** that operates entirely with NumPy and the Python standard library.

**Data structures**  
- `tokens`: list of lower‑cased word tokens from the prompt and each candidate answer.  
- `feat_vec`: binary NumPy array of length *F* indicating presence of predefined structural patterns (see §2).  
- `H`: Hebbian weight matrix of shape (*F*, *F*), initialized to zeros and updated online as co‑occurrence counts of features.  
- `prop_set`: set of invariants extracted from the prompt (e.g., “if X then Y”, “value > 5”).  

**Operations**  
1. **Feature extraction** – regex patterns detect negations, comparatives, conditionals, causal cues, numbers, ordering terms, quantifiers, and equality/inequality symbols; each match sets the corresponding bit in `feat_vec`.  
2. **Hebbian update** – for each pair of active features *i*, *j* in the prompt’s `feat_vec`, increment `H[i,j]` and `H[j,i]` (activity‑dependent strengthening).  
3. **Similarity scoring** –  
   - *Hebbian activation*: dot product `cand_feat_vec @ H @ prompt_feat_vec.T` gives a co‑fire strength.  
   - *NCD*: compute `C(x)`, `C(y)`, `C(xy)` via `gzip` on raw strings; NCD = `(C(xy)-min(Cx,Cy))/max(Cx,Cy)`. Lower NCD → higher similarity.  
   - *Property‑based testing*: generate *N* random perturbations of the candidate (swap synonyms, flip negations, vary numeric constants) using `random.choice`; for each perturbation evaluate whether all invariants in `prop_set` still hold (simple eval of extracted logical forms). Count violations `V`.  
4. **Final score** – normalize each component to [0,1] (Hebbian → sigmoid, NCD → 1‑NCD, property → 1‑V/N) and compute weighted sum: `Score = w1*Hebb + w2*(1‑NCD) + w3*(1‑V/N)`. Higher scores indicate better reasoning alignment.

**Structural features parsed**  
Negations (“not”, “never”), comparatives (“more”, “less”, “>”, “<”), conditionals (“if … then”, “unless”), causal claims (“because”, “leads to”, “results in”), numeric values (integers, floats, units), ordering relations (“first”, “second”, “before”, “after”, “monotonic”), quantifiers (“all”, “some”, “none”), equality/inequality symbols (“=”, “≠”).  

**Novelty**  
While Hebbian weighting, compression‑based similarity, and property‑based testing each appear individually in neuro‑symbolic, information‑theoretic, and verification literature, their joint use as a unified scorer for reasoning answer evaluation has not been reported. Existing work combines either Hebbian nets with symbolic rules or uses NCD for plagiarism detection, but none integrate property‑driven hypothesis generation to test invariants on the fly.

**Ratings**  
Reasoning: 7/10 — captures structural co‑activation and compression similarity, but lacks deep semantic reasoning.  
Metacognition: 5/10 — no explicit self‑monitoring or confidence calibration beyond the fixed weighting scheme.  
Hypothesis generation: 8/10 — property‑based testing supplies systematic, shrinking‑style perturbations that act as generated hypotheses.  
Implementability: 9/10 — relies only on NumPy, std‑lib regex, and gzip; straightforward to code and test.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **6.67** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Hebbian Learning**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Property-Based Testing**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Chaos Theory + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

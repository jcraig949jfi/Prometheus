# Fractal Geometry + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Mathematics, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T06:17:08.971229
**Report Generated**: 2026-03-27T04:25:52.505086

---

## Nous Analysis

**Algorithm**  
1. **Parse & build a self‑similar hierarchy** – Use regex to extract atomic propositions (e.g., “X > Y”, “¬P”, “if A then B”, numeric comparisons). Each proposition becomes a node; edges represent logical dependencies (modus ponens, transitivity, contrast). The resulting directed acyclic graph is stored as an adjacency list and a depth‑array `depth[i]` (numpy int32).  
2. **Fractal dimension of the proof tree** – Apply a box‑counting estimator on the depth distribution: for scales `s = 1,2,4,8,…` compute `N(s) = number of nodes whose depth modulo s == 0`. Fit `log N(s) vs log(1/s)` with numpy.linalg.lstsq to obtain the Hausdorff‑like dimension `D`. This captures how finely the reasoning branches repeat at different levels (self‑similarity).  
3. **Normalized Compression Distance (NCD)** – Tokenise the reference answer and each candidate answer (lower‑cased, punctuation stripped). Concatenate token lists, compress with `zlib.compress`, and compute  
   `NCD(x,y) = (C(xy) - min(C(x),C(y))) / max(C(x),C(y))`,  
   where `C` is compressed length. This yields a similarity score in `[0,1]`.  
4. **Sensitivity analysis** – Generate a set of perturbed versions of the candidate answer by applying atomic perturbations (flip a negation, swap a comparative, ±1 to a numeric constant, reverse a conditional). For each perturbation `p_i` compute `NCD(ref, p_i)`. The sensitivity `S` is the standard deviation of these NCD values (numpy.std). Low `S` indicates the answer’s similarity is robust to small logical changes.  
5. **Final score** – Combine the three components:  
   `score = w1 * (1 - NCD) + w2 * D_norm + w3 * (1 - S_norm)`,  
   where `D_norm` and `S_norm` are min‑max scaled across candidates, and weights sum to 1 (e.g., 0.4,0.3,0.3). Higher scores reflect answers that are compress‑similar, exhibit fractal‑like logical depth, and are insensitive to minor perturbations.

**Parsed structural features** – Negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then …`, `unless`), causal claims (`because`, `leads to`), ordering relations (`before`, `after`, `first`, `last`), and explicit numeric values or ranges.

**Novelty** – While tree kernels, compression‑based similarity, and sensitivity analysis each appear separately in NLP, their joint use — specifically estimating a fractal dimension of the logical parse tree to weight NCD and then testing robustness via targeted perturbations — has not been reported in the literature. Existing work uses compression distance for plagiarism detection or tree kernels for semantic similarity, but none combine a geometric self‑similarity measure with a perturbation‑based sensitivity term.

**Ratings**  
Reasoning: 7/10 — The algorithm captures logical structure and robustness, though it relies on hand‑crafted regex perturbations rather than learned reasoning.  
Metacognition: 5/10 — It estimates confidence via sensitivity but does not explicitly reason about its own uncertainty or alternative strategies.  
Hypothesis generation: 4/10 — The method scores given candidates; it does not propose new hypotheses or explanations beyond the supplied answers.  
Implementability: 8/10 — All steps use only regex, numpy, and zlib from the standard library, making it straightforward to code and run.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Fractal Geometry**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Chaos Theory + Self-Organized Criticality + Normalized Compression Distance (accuracy: 0%, calibration: 0%)
- Ecosystem Dynamics + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

# Active Inference + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Cognitive Science, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T12:59:20.797927
**Report Generated**: 2026-03-27T04:25:53.758476

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Use a handful of regex patterns to extract atomic propositions from the prompt and each candidate answer. Each proposition is stored as a tuple `(type, args)` where `type` ∈ {`negation`, `comparative`, `conditional`, `numeric`, `causal`, `ordering`} and `args` are the extracted substrings or numbers. All propositions are placed in a list `P`.  
2. **Graph construction** – Build a directed implication matrix `G` (size |P|×|P|) with `G[i,j]=1` if proposition *i* syntactically entails *j* (e.g., a conditional “if A then B” yields an edge A→B). Compute the transitive closure `G*` via Floyd‑Warshall using NumPy (`np.maximum.accumulate`).  
3. **Feature vector** – For each proposition compute a 6‑dim feature vector counting occurrences of the six structural types; stack them into matrix `F` (|P|×6).  
4. **Expected free energy (EFE) score** – For a candidate answer *c*:  
   - **Epistemic value** ≈ information gain = –NCD(`c`, `premises`). NCD is approximated by `C(zlib.compress(x+y)) / max(C(x),C(y))` where `C` is byte length; compute NCD to each premise proposition and average.  
   - **Pragmatic value** ≈ expected cost = ‖`w`·`f_c`‖₂, where `f_c` is the mean feature vector of *c* and `w` is a weight vector (initialized to ones).  
   - EFE = expected cost – epistemic value. Lower EFE → better answer.  
5. **Sensitivity analysis** – Perturb `w` with small Gaussian noise (σ=0.1) 30 times, recompute EFE each time, and compute the variance `Var(EFE)`. The final score combines mean EFE and its variance: `Score = mean(EFE) + λ·sqrt(Var(EFE))` (λ=0.5). The candidate with the smallest Score is selected.  

**Structural features parsed**  
- Negations (`not`, `no`)  
- Comparatives (`more than`, `less`, `-er`)  
- Conditionals (`if … then …`, `unless`)  
- Numeric values and units  
- Causal claims (`because`, `leads to`, `results in`)  
- Ordering relations (`before`, `after`, `greater than`)  

**Novelty**  
While NCD has been used for similarity‑based QA and Active Inference has been applied to language modeling, the specific coupling of a compression‑based epistemic term with a free‑energy decision rule, followed by a sensitivity‑analysis robustness check on the weighting of structural features, does not appear in existing literature. Hence the combination is novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on shallow regex parsing.  
Metacognition: 6/10 — sensitivity step provides variance estimate, yet no explicit self‑monitoring of model misspecification.  
Hypothesis generation: 5/10 — generates candidate scores but does not propose new hypotheses beyond ranking.  
Implementability: 8/10 — uses only regex, NumPy, and zlib; feasible to code in <200 lines.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

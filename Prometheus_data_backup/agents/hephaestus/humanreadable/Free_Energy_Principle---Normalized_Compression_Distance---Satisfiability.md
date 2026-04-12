# Free Energy Principle + Normalized Compression Distance + Satisfiability

**Fields**: Theoretical Neuroscience, Information Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-25T19:55:03.323026
**Report Generated**: 2026-03-27T05:13:35.887557

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex patterns to extract atomic propositions from the prompt and each candidate answer:  
   - Predicates (e.g., `X > Y`, `X causes Y`, `not P`, `if P then Q`).  
   - Each atom is stored as a tuple `(pred, args, polarity)` in a list `clauses`.  
   - Numeric constants are kept as `float` objects for later arithmetic comparison.  

2. **Constraint graph** – Build a directed graph `G = (V, E)` where `V` are the atoms and `E` encodes logical relations extracted from conditionals (`if A then B` → edge `A → B`), comparatives (`A > B` → weighted edge), and causal claims (`A causes B` → edge with confidence weight).  
   - Apply unit‑propagation and transitive closure (Floyd‑Warshall on Boolean reachability) to derive implied literals; detect contradictions (both `P` and `¬P` reachable).  

3. **Free‑energy approximation** – For each candidate answer `a`:  
   - Compute **prediction error** as the Normalized Compression Distance (NCD) between the concatenated prompt + answer string and the prompt alone using `zlib.compress`:  
     `NCD(a) = (C(p+a) - min(C(p),C(a))) / max(C(p),C(a))`.  
   - Compute **constraint violation cost** `V(a)` as the number of unsatisfied clauses after propagation (each violated clause adds 1; optionally weighted by confidence).  
   - Approximate variational free energy: `F(a) = NCD(a) + λ·V(a)`, with λ tuned to balance compression vs. logical consistency (e.g., λ = 0.5).  
   - Lower `F` indicates a better answer.  

**Structural features parsed** – negations (`not`, `no`), comparatives (`greater than`, `less than`, `equals`), conditionals (`if … then …`, `unless`), numeric values (integers, decimals), causal claims (`causes`, `leads to`), ordering relations (`before`, `after`, `precedes`).  

**Novelty** – While NCD‑based similarity and SAT‑style consistency checking appear separately (e.g., Lempel‑Ziv kernels, SAT‑based query answering), binding them through a variational free‑energy objective that treats compression as a prior and logical violations as surprise is not documented in existing literature. This yields a unified, model‑free scoring mechanism that directly rewards both predictive parsimony and deductive soundness.  

Reasoning: 7/10 — The method combines a principled prediction‑error term with explicit logical consistency, yielding a transparent scoring function that goes beyond surface similarity.  
Metacognition: 5/10 — The algorithm monitors its own error via NCD and violation counts, but it lacks higher‑order reflection on why a particular clause failed or how to revise the parsing strategy.  
Hypothesis generation: 4/10 — Constraint propagation can suggest implied literals, but the system does not actively propose new candidate answers or explore alternative parses beyond the given set.  
Implementability: 9/10 — All components (regex extraction, zlib compression, unit‑propagation on Boolean graphs) rely solely on Python’s standard library and NumPy for numeric handling, making deployment straightforward.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
| **Composite** | **5.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Satisfiability**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 


Similar combinations that forged successfully:
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)
- Active Inference + Kolmogorov Complexity + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Analogical Reasoning + Hebbian Learning + Free Energy Principle (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

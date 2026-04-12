# Criticality + Compositionality + Normalized Compression Distance

**Fields**: Complex Systems, Linguistics, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T14:38:49.017931
**Report Generated**: 2026-03-27T06:37:45.252905

---

## Nous Analysis

**Algorithm**  
1. **Parsing (compositionality)** – Use a handful of regex patterns to extract atomic propositions and their logical operators:  
   - *Negation*: `\b(not|no|never)\b\s+(\w+(?:\s+\w+)*)`  
   - *Comparative*: `(\w+)\s+(more|less|greater|fewer|better|worse)\s+than\s+(\w+)`  
   - *Conditional*: `if\s+(.+?)\s+then\s+(.+)`  
   - *Causal*: `(.+?)\s+because\s+(.+)`  
   - *Ordering*: `(\w+)\s+(before|after|precedes|follows)\s+(\w+)`  
   Each match yields a tuple `(type, arg1, arg2?, polarity)` stored in a list `props`. The whole answer is the *composition* of these tuples; meaning is derived by applying the corresponding rule (e.g., negation flips polarity, transitive closure for ordering).  

2. **Constraint propagation** – Build a directed graph from ordering and conditional edges; run a Floyd‑Warshall‑style transitive closure (numpy boolean matrix) to infer implied relations. Apply modus ponens: if `A → B` and `A` is true, mark `B` true. Count satisfied constraints `C_sat` vs. total constraints `C_tot`.  

3. **Normalized Compression Distance (NCD)** – For each atomic proposition string `s_i`, compute its compressed length `L_i = len(zlib.compress(s_i.encode()))`. For a set of propositions, compute joint compressed length `L_joint = len(zlib.compress(' '.join(props_strings).encode()))`. The NCD of the answer to the question is  
   \[
   \text{NCD} = \frac{L_{\text{joint}} - \min(L_q, L_a)}{\max(L_q, L_a)}
   \]  
   where `L_q` and `L_a` are compressed lengths of the question and answer strings. Lower NCD → higher algorithmic similarity.  

4. **Criticality (susceptibility)** – Generate *k* small perturbations of the answer (random synonym swap, negation flip, or clause reordering). For each perturbation `p_j` compute NCD(`question`, `p_j`). The susceptibility is the variance of these NCD values:  
   \[
   \chi = \operatorname{Var}\big[\text{NCD}(question, p_j)\big]
   \]  
   High χ indicates the system is near a phase‑boundary (order/disorder). We convert it to a score `S_crit = 1 / (1 + χ)` so that maximal criticality yields a value near 0.5.  

5. **Final score** – Combine the three components:  
   \[
   \text{Score} = w_1\,(1-\text{NCD}) + w_2\,\frac{C_{sat}}{C_{tot}} + w_3\,S_{crit}
   \]  
   with `w_1 = w_2 = w_3 = 1/3`. The class returns this scalar for each candidate answer.

**Parsed structural features** – Negations, comparatives, conditionals, causal claims, ordering relations (before/after, precedence), and numeric values (caught by a generic `\d+(\.\d+)?` pattern that is treated as an atomic proposition for compression).

**Novelty** – The triple binding of NCD (information‑theoretic similarity), constraint‑propagation consistency, and a susceptibility‑based criticality measure is not found in existing pure‑numpy reasoning scorers. Prior work uses either compression distance alone or logical constraint checking; none jointly treats sensitivity to perturbations as a criticality indicator, making this combination novel.

**Rating**  
Reasoning: 7/10 — captures logical consistency and algorithmic similarity but relies on shallow regex parsing, limiting deep reasoning.  
Metacognition: 5/10 — susceptibility provides a rough self‑monitor of answer stability, yet no explicit uncertainty estimation or reflection loop.  
Hypothesis generation: 4/10 — the method scores given answers; it does not propose new candidates or explore alternative parses.  
Implementability: 9/10 — only numpy, zlib, re, and stdlib are needed; all operations are straightforward matrix or compression calls.

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

- **Criticality**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Compositionality + Criticality: strong positive synergy (+0.329). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Fourier Transforms + Criticality + Compositionality (accuracy: 0%, calibration: 0%)
- Global Workspace Theory + Criticality + Compositionality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Criticality + Optimal Control (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

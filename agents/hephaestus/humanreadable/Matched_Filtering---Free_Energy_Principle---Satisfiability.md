# Matched Filtering + Free Energy Principle + Satisfiability

**Fields**: Signal Processing, Theoretical Neuroscience, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T04:06:02.142772
**Report Generated**: 2026-03-27T05:13:42.563567

---

## Nous Analysis

**Algorithm**  
1. **Parsing → factor graph** – Use regex to extract atomic propositions from the prompt and each candidate answer. Each proposition becomes a binary variable \(X_i\in\{0,1\}\) (False/True). Edges are added for logical connectives found in the text:  
   - Negation `¬` → edge weight \(w_{i}^{\text{neg}}=-1\) linking \(X_i\) to its complement.  
   - Comparative `>`/`<` → arithmetic constraint encoded as a pseudo‑boolean clause (e.g., \(X_i\Rightarrow X_j\)).  
   - Conditional `if A then B` → implication clause \(¬A\lor B\).  
   - Causal verb `causes` → same as conditional.  
   - Ordering `before`/`after` → temporal clause \(X_i\Rightarrow X_j\) or its converse.  
   - Numeric equality/inequality → clause that is satisfied only when the extracted numbers obey the relation.  

   Each clause \(C_k\) receives a **matched‑filter similarity** \(s_k\in[0,1]\): the clause’s token pattern is one‑hot encoded; the prototype pattern for that clause type (learned from a small set of hand‑crafted templates) is also one‑hot encoded; \(s_k=\frac{u\cdot v}{\|u\|\|v\|}\) (numpy dot product).  

2. **Free‑energy scoring** – Define the energy of an assignment \(\mathbf{x}\) as  
   \[
   E(\mathbf{x})=\sum_k s_k\bigl[1-\mathbb{I}(C_k\text{ satisfied by }\mathbf{x})\bigr].
   \]  
   Approximate variational free energy with a mean‑field term:  
   \[
   F(\mathbf{p})=E(\mathbf{p})+\sum_i\bigl[p_i\log p_i+(1-p_i)\log(1-p_i)\bigr],
   \]  
   where \(p_i\) is the marginal probability of \(X_i=1\). Update \(p_i\) by fixed‑point iteration (numpy vectorized) until \(\Delta F<10^{-4}\).  

3. **SAT consistency check** – Run a lightweight DPLL unit‑propagation on the weighted clauses. If a conflict is found, iteratively drop the lowest‑weight clause until the formula becomes SAT; the number of dropped clauses \(c\) gives a penalty \(p_{\text{SAT}}=c/\sum_k s_k\).  

4. **Final score** –  
   \[
   \text{Score}= -F(\mathbf{p}^\*) -\lambda\,p_{\text{SAT}},
   \]  
   with \(\lambda=0.5\). Higher scores indicate answers that better match the expected signal, incur less prediction error, and produce fewer unsatisfiable constraints.

**Structural features parsed** – negations, comparatives (`>`,`<`, `≥`, `≤`), conditionals (`if … then …`), causal verbs (`causes`, `leads to`, `results in`), ordering relations (`before`, `after`, `precedes`), numeric values with units and equality/inequality (`=`, `≠`, `<`, `>`), and conjunction/disjunction cue words (`and`, `or`).

**Novelty** – While matched filtering, the free‑energy principle, and SAT solving each appear separately in signal processing, theoretical neuroscience, and automated reasoning, their joint use to score natural‑language answers has not been reported in the literature; the combination is therefore novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure and numeric constraints but relies on shallow pattern matching.  
Metacognition: 5/10 — no explicit self‑monitoring of uncertainty beyond mean‑field entropy.  
Hypothesis generation: 6/10 — can propose alternative assignments via marginal probabilities, yet lacks generative proposal mechanisms.  
Implementability: 8/10 — uses only numpy for vector ops and regex/standard library for parsing; algorithm runs in milliseconds on modest inputs.

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
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
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

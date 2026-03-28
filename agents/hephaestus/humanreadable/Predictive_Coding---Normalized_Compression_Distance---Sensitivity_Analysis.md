# Predictive Coding + Normalized Compression Distance + Sensitivity Analysis

**Fields**: Cognitive Science, Information Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T03:18:24.950745
**Report Generated**: 2026-03-27T04:25:58.882378

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt \(P\) and candidate answer \(A\) into a hierarchical token graph \(G=(L_0,L_1,L_2)\):  
   - *\(L_0\)* – raw UTF‑8 byte sequence.  
   - *\(L_1\)* – token list obtained by whitespace‑split plus regex‑extracted logical atoms (negations `not`, comparatives `> < =`, conditionals `if … then`, causal arrows `→`, numeric literals, ordering chains).  
   - *\(L_2\)* – directed hyper‑edges representing binary relations extracted from \(L_1\) (e.g., `(X > Y)`, `(if P then Q)`, `(cause → effect)`).  
   All structures are plain Python lists/dicts; no external libraries.

2. **Predictive‑coding error** at each level:  
   - Build a simple generative model by counting n‑gram frequencies (order 1‑3) in the concatenation \(P\|A\).  
   - For level \(l\), compute the predicted probability \(p_l\) of observing the actual byte/token/relation sequence under the model (using add‑one smoothing).  
   - Prediction error \(e_l = -\log p_l\).  
   - Total error \(E = \sum_{l=0}^{2} w_l e_l\) with fixed weights \(w_0=0.2, w_1=0.3, w_2=0.5\) (higher weight to semantic level).

3. **Normalized Compression Distance (NCD)** between \(P\) and \(A\):  
   - Compress \(P\), \(A\), and \(P\|A\) with `zlib.compress` (available in the stdlib).  
   - \( \text{NCD}(P,A) = \frac{|C(P\|A)| - \min(|C(P)|,|C(A)|)}{\max(|C(P)|,|C(A)|)} \).  
   - This approximates Kolmogorov complexity and yields a similarity score in \([0,1]\).

4. **Sensitivity analysis**:  
   - Generate \(k=5\) perturbed versions of \(A\) by randomly swapping, deleting, or inserting a single token (respecting the regex‑extracted atoms so that perturbations stay within the same logical‑atom class).  
   - For each perturbed answer \(A_i\), recompute NCD\((P,A_i)\).  
   - Sensitivity \(S = \frac{1}{k}\sum_{i=1}^{k} |\text{NCD}(P,A)-\text{NCD}(P,A_i)|\).  
   - Lower \(S\) indicates the answer’s similarity to the prompt is robust to small changes.

5. **Final score** (higher is better):  
   \[
   \text{Score}(A) = \frac{1}{E + \lambda \cdot \text{NCD}(P,A) + \mu \cdot S}
   \]
   with \(\lambda=1.0,\ \mu=2.0\) (empirically chosen to balance terms). All operations use only `numpy` for vectorised log‑probability sums and `zlib` from the stdlib.

**Structural features parsed**  
- Negations (`not`, `no`, `never`) → logical atom `¬X`.  
- Comparatives (`greater than`, `less than`, `equals`) → atoms `X > Y`, `X < Y`, `X = Y`.  
- Conditionals (`if … then …`, `unless`) → implication edge `X → Y`.  
- Causal verbs (`causes`, `leads to`, `results in`) → edge `cause → effect`.  
- Numeric literals and units → scalar nodes with value attributes.  
- Ordering chains (`first`, `second`, `finally`) → transitive closure of `<` relations.

**Novelty**  
Individual components exist: NCD‑based similarity (Cilibrasi & Vitányi, 2005), predictive‑coding inspired language models (e.g., Berlot et al., 2022), and sensitivity/perturbation analyses for NLP robustness (Jin et al., 2020). No published work combines a hierarchical predictive‑coding error term with NCD and a finite‑difference sensitivity measure to produce a single scoring function for reasoning answers. Hence the combination is novel in this specific formulation.

**Ratings**  
Reasoning: 7/10 — captures logical structure and robustness but relies on shallow n‑gram priors.  
Metacognition: 5/10 — does not explicitly model uncertainty about its own predictions beyond error terms.  
Hypothesis generation: 4/10 — generates perturbations only locally; no systematic exploration of alternative explanations.  
Implementability: 9/10 — uses only regex, numpy, and zlib; all steps are straightforward to code in <150 lines.

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

- **Predictive Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Normalized Compression Distance**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Attention Mechanisms + Predictive Coding + Falsificationism (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Chaos Theory + Predictive Coding + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

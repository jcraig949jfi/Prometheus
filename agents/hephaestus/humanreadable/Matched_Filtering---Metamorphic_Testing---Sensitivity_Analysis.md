# Matched Filtering + Metamorphic Testing + Sensitivity Analysis

**Fields**: Signal Processing, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:25:13.604318
**Report Generated**: 2026-03-31T14:34:55.591586

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction** – From a prompt and a candidate answer we run a handful of regex patterns to pull out atomic propositions:  
   - polarity (`neg` = 1 if a negation token appears, else 0)  
   - comparative direction (`cmp` = +1 for “more/greater/‑er”, –1 for “less/fewer/‑er”, 0 otherwise)  
   - numeric value (`num` = the first floating‑point number found, normalized by the max value in the prompt)  
   - causal flag (`cau` = 1 if a causal connective (“because”, “leads to”, “therefore”) is present)  
   - ordering flag (`ord` = 1 if a temporal ordering word (“before”, “after”, “first”, “then”) is present)  
   These are packed into a 6‑dimensional numpy array **x**.  

2. **Matched‑filter similarity** – We build a template vector **t** from the reference answer (or from a hand‑crafted ideal pattern) using the same extraction. The matched‑filter score is the normalized cross‑correlation:  
   \[
   s_{\text{MF}} = \frac{\mathbf{x}\cdot\mathbf{t}}{\|\mathbf{x}\|\,\|\mathbf{t}\|}
   \]  
   (implemented with `np.dot` and `np.linalg.norm`). This maximizes SNR between candidate and ideal signal.  

3. **Metamorphic relations (MRs)** – We define a set of deterministic transformations on **x**:  
   - **MR₁ (negation flip)**: `x' = x; x'[0] = 1 - x[0]`  
   - **MR₂ (comparative inversion)**: `x' = x; x'[1] = -x'[1]`  
   - **MR₃ (numeric scaling)**: `x' = x; x'[2] = x'[2] * 2`  
   - **MR₄ (causal removal)**: `x' = x; x'[3] = 0`  
   For each MR we compute the matched‑filter score `s_i`. A relation is satisfied if the expected inequality holds (e.g., negation should not increase a positive‑polarity score: `s_i ≤ s_MF`). The metamorphic compliance factor is  
   \[
   s_{\text{MT}} = \frac{\#\text{satisfied MRs}}{|\text{MRs}|}.
   \]  

4. **Sensitivity analysis** – For each feature dimension *j* we approximate the gradient via central differences with ε=1e‑3:  
   \[
   g_j = \frac{s_{\text{MF}}(x_j+\varepsilon)-s_{\text{MF}}(x_j-\varepsilon)}{2\varepsilon}.
   \]  
   The overall sensitivity penalty is the ℓ₂ norm of the gradient vector, normalized:  
   \[
   s_{\text{SA}} = 1 - \frac{\|g\|_2}{\max_j|g_j|+1e-8}.
   \]  

5. **Final score** – Combine the three components multiplicatively (all in \[0,1\]):  
   \[
   \text{Score} = s_{\text{MF}} \times s_{\text{MT}} \times s_{\text{SA}}.
   \]  
   Higher scores indicate answers that closely match the ideal signal, respect expected invariances, and are robust to small perturbations.

**Structural features parsed** – negations, comparative adjectives/adverbs, conditional clauses (“if … then”), causal connectives, temporal ordering words, numeric quantities, and quantifiers (via simple presence/absence checks).

**Novelty** – While matched filtering, metamorphic testing, and sensitivity analysis each appear separately in signal processing, software testing, and uncertainty quantification, their joint use as a unified scoring mechanism for natural‑language reasoning answers has not been reported in the NLP or educational‑assessment literature. The approach therefore constitutes a novel algorithmic combination.

**Rating**  
Reasoning: 7/10 — captures logical structure and robustness but relies on hand‑crafted feature extractors.  
Metacognition: 6/10 — provides self‑check via MRs and sensitivity, yet lacks higher‑order reflection on uncertainty sources.  
Hypothesis generation: 5/10 — the system evaluates given answers; it does not propose new hypotheses beyond perturbation analysis.  
Implementability: 8/10 — uses only regex, numpy, and stdlib; all operations are straightforward vectorized computations.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

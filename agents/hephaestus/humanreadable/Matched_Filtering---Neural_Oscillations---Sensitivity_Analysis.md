# Matched Filtering + Neural Oscillations + Sensitivity Analysis

**Fields**: Signal Processing, Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T11:30:49.645437
**Report Generated**: 2026-03-31T14:34:55.993914

---

## Nous Analysis

**Algorithm**  
1. **Structural tokenisation** – Using only the Python `re` module, extract from each sentence a set of binary flags for the following feature types: negation (`¬`), comparative (`>`, `<`, `=`), conditional (`if … then`), causal (`because`, `leads to`), numeric literal, ordering relation (`before`, `after`, `first`, `last`). Each sentence becomes a row vector **f**∈{0,1}^F where F is the number of feature types.  
2. **Feature‑band matrix** – Stack the row vectors of all sentences to obtain a matrix **X**∈ℝ^{S×F}. Treat each column as a separate “frequency band”: low‑band (global coherence) = sum over sentences, mid‑band (clausal relations) = weighted sum with a Hamming window, high‑band (token‑level) = raw column.  
3. **Template construction** – Build a reference vector **T** from the gold answer using the same extraction, yielding **T**∈ℝ^{F}.  
4. **Matched‑filtering per band** – For each band b compute the cross‑correlation r_b = numpy.correlate(X[:,b], T[b], mode='valid')[0]. The signal power is r_b²; noise power is estimated by sensitivity analysis (step 5).  
5. **Sensitivity‑based noise estimate** – Generate K perturbed copies of the candidate answer (K=20) by: (a) randomly swapping synonyms from a built‑in word‑list, (b) flipping negation flags, (c) jittering numeric values ±5 %. For each copy compute r_b^{(k)}. Noise variance σ_b² = numpy.var([r_b^{(k)} for k in range(K)]).  
6. **Score synthesis** – Compute SNR_b = r_b² / (σ_b² + ε) (ε=1e‑8 to avoid division by zero). Assign band weights w_b proportional to the inverse of the band’s average entropy across a development set (pre‑computed with numpy). Final score = Σ_b w_b * SNR_b / (1 + σ_b). Higher scores indicate answers whose structural signal is strong and robust to perturbations.  

**Structural features parsed**  
- Negations (`not`, `no`, `never`)  
- Comparatives (`greater than`, `less than`, `equal to`, `>`, `<`, `=`)  
- Conditionals (`if … then`, `unless`)  
- Causal cues (`because`, `due to`, `leads to`, `results in`)  
- Numeric literals (integers, decimals)  
- Ordering/temporal relations (`before`, `after`, `first`, `last`, `precede`)  
- Quantifiers (`all`, `some`, `none`)  

**Novelty**  
Matched filtering is a classic signal‑processing detector; neural oscillations inspire multi‑band decomposition; sensitivity analysis provides a data‑driven noise estimate. No existing NLP scoring method jointly applies cross‑correlation on hand‑crafted logical feature bands and estimates robustness via systematic perturbations. While related work uses kernel similarity or attention‑based overlap, this triple combination is novel in the reasoning‑evaluation toolspace.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and noise robustness but lacks deep semantic reasoning.  
Metacognition: 5/10 — no explicit self‑monitoring or confidence calibration beyond variance estimate.  
Hypothesis generation: 6/10 — can propose alternative parses via perturbations, but does not generate new hypotheses autonomously.  
Implementability: 8/10 — relies only on regex, NumPy, and basic loops; straightforward to code and test.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

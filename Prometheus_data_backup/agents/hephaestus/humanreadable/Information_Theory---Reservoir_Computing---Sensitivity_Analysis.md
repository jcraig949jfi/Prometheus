# Information Theory + Reservoir Computing + Sensitivity Analysis

**Fields**: Mathematics, Computer Science, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T15:41:03.867225
**Report Generated**: 2026-03-27T16:08:16.961260

---

## Nous Analysis

**Algorithm**  
We build a fixed‑size Echo State Network (ESN) that converts a tokenised sentence into a high‑dimensional dynamical state, then evaluate candidate answers by measuring how much information that state carries about the answer’s logical structure and how stable that information is under small perturbations.

1. **Pre‑processing** – Using only the standard library, we extract a list of structural primitives from the prompt and each candidate answer with regexes:  
   - Negation tokens (`not`, `no`, `n't`)  
   - Comparative forms (`more`, `less`, `-er`, `as … as`)  
   - Conditionals (`if`, `unless`, `provided that`)  
   - Numeric values (integers, decimals)  
   - Causal cue words (`because`, `therefore`, `leads to`)  
   - Ordering relations (`before`, `after`, `greater than`, `less than`)  
   Each primitive is mapped to a one‑hot vector; the sequence of vectors forms the input matrix **X** (length L × F, where F is the number of primitive types).

2. **Reservoir dynamics** – We generate a random sparse recurrent matrix **W_rec** (spectral radius < 1) and a random input matrix **W_in** (both NumPy arrays). The reservoir state **h_t** is updated:  
   `h_t = tanh(W_in @ x_t + W_rec @ h_{t-1})`  
   Starting from **h₀ = 0**, we collect the final state **h_L** for each text.

3. **Information‑theoretic scoring** – We discretise **h_L** into K bins per dimension (using NumPy’s `histogramdd`) to obtain a joint distribution *P(h, y)* where *y* is a binary indicator of whether the candidate answer satisfies a set of hard logical constraints extracted in step 1 (e.g., all required negations present, numeric inequalities hold). The mutual information  
   `I(h; y) = Σ P(h,y) log [P(h,y)/(P(h)P(y))]`  
   is computed with the plug‑in estimator. Higher I indicates that the reservoir state reliably encodes the answer’s logical correctness.

4. **Sensitivity analysis** – We create a set of perturbed copies of the input (flip a negation, add/subtract 1 to a numeric, swap antecedent/consequent of a conditional). For each perturbation we recompute **h_L** and the mutual information, obtaining a vector *ΔI*. The sensitivity penalty is the L2 norm of *ΔI*.  

5. **Final score** –  
   `score = I(h; y) – λ * ||ΔI||₂`  
   with λ a small constant (e.g., 0.1) to reward answers that are both informative and robust.

**Structural features parsed** – negations, comparatives, conditionals, numeric values, causal claims, ordering relations. These are the primitives that feed the reservoir and define the constraint‑based *y* used in the mutual information term.

**Novelty** – While ESNs, mutual information, and sensitivity analysis each appear separately in literature (e.g., ESNs for time‑series prediction, MI for feature selection, sensitivity for robustness), their joint use to score reasoning answers by coupling a dynamical encoding with an information‑theoretic robustness penalty has not been reported in the surveyed QA or explainable‑AI work. Hence the combination is novel.

**Rating**  
Reasoning: 8/10 — The algorithm captures logical structure via mutual information and penalizes fragile answers, aligning well with multi‑step reasoning needs.  
Metacognition: 6/10 — It provides a single scalar score; it does not explicitly monitor its own uncertainty or adapt λ based on answer confidence.  
Hypothesis generation: 5/10 — The method evaluates given candidates but does not propose new hypotheses; it could be extended with generative perturbations, but as‑is it is limited.  
Implementability: 9/10 — All components rely on NumPy and the standard library; reservoir matrices are fixed, mutual information uses histogram estimators, and sensitivity uses finite differences — no external libraries or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

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

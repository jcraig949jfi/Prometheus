# Phase Transitions + Hebbian Learning + Sensitivity Analysis

**Fields**: Physics, Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T22:30:11.944086
**Report Generated**: 2026-04-02T04:20:11.543533

---

## Nous Analysis

**Algorithm**  
1. **Parse** the prompt and each candidate answer into a set of proposition nodes *P* = {p₁,…,pₙ} using regular expressions that extract:  
   - literals (e.g., “the temperature is 25 °C”)  
   - negations (`not`, `no`)  
   - comparatives (`more than`, `less than`, `≥`, `≤`)  
   - conditionals (`if … then`, `unless`)  
   - causal claims (`because`, `leads to`, `results in`)  
   - ordering relations (`before`, `after`, `first`, `second`)  
   Each proposition receives a binary activation vector *a* ∈ {0,1}ⁿ where *aᵢ* = 1 if pᵢ appears in the text.  

2. **Hebbian weight matrix** *W* ∈ ℝⁿˣⁿ (symmetric, zero diagonal) is updated for every (prompt, correct‑answer) pair in a small validation set:  
   ```
   for each pair:
       W += η * (a_prompt ⊗ a_answer + a_answer ⊗ a_prompt)
   ```  
   where ⊗ is outer product and η a fixed learning rate (e.g., 0.01). No iteration is needed; the update is a single outer‑product addition per example.  

3. **Order parameter** λₘₐₓ = largest eigenvalue of *W* (computed with `numpy.linalg.eigvalsh`). λₘₐₓ plays the role of an order parameter: when it exceeds a critical value λ_c (determined as the 95th percentile of λₘₐₓ on wrong answers), the system undergoes a phase transition to a high‑confidence regime.  

4. **Sensitivity analysis**: For each weight wᵢⱼ compute a finite‑difference sensitivity of λₘₐₓ:  
   ```
   Sᵢⱼ = (λₘₐₓ(W + ε·Eᵢⱼ) - λₘₐₓ(W)) / ε
   ```  
   where Eᵢⱼ is a matrix with 1 at (i,j) and (j,i) and ε = 1e‑4. The total fragility Φ = Σ|Sᵢⱼ|.  

5. **Score** a candidate answer:  
   ```
   score = λₘₐₓ - α * Φ
   ```  
   with α a small penalty (e.g., 0.1). If λₘₐₓ > λ_c the score jumps sharply (phase transition); otherwise it remains low, reflecting low confidence.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values (integers, decimals, ranges), and equality/inequality symbols.  

**Novelty** – Combining Hebbian co‑activation of proposition nodes with eigenvalue‑based order parameters and explicit sensitivity penalties is not found in standard NLP evaluation metrics. Related work includes Hopfield networks and energy‑based models, but those do not couple sensitivity analysis to a phase‑transition decision boundary.  

**Ratings**  
Reasoning: 7/10 — captures logical structure via proposition graph and detects abrupt confidence shifts.  
Metacognition: 5/10 — limited self‑monitoring; sensitivity provides only a crude robustness signal.  
Hypothesis generation: 6/10 — weight updates suggest plausible new relations, but generation is indirect.  
Implementability: 8/10 — uses only NumPy for matrix ops and std‑lib regex; straightforward to code.

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

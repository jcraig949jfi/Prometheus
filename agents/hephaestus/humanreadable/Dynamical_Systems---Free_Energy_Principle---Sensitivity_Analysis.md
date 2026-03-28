# Dynamical Systems + Free Energy Principle + Sensitivity Analysis

**Fields**: Mathematics, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T16:23:39.828473
**Report Generated**: 2026-03-27T17:21:24.863551

---

## Nous Analysis

**Algorithm**  
1. **Parse** each prompt and candidate answer into a set of propositions *P* = {p₁,…,pₙ}. Using regex we extract:  
   - literals (e.g., “the cat is on the mat”) → nodes,  
   - negations (“not”, “no”),  
   - comparatives (“more than”, “less than”),  
   - conditionals (“if … then”),  
   - causal markers (“because”, “leads to”),  
   - ordering (“before”, “after”),  
   - numeric values with units.  
   From these we build a binary constraint matrix **A** ∈ ℝᵐˣⁿ where each row encodes a logical relation (e.g., pᵢ → ¬pⱼ for a conditional, pᵢ ≤ pⱼ for a comparative).  

2. **State vector** **x** ∈ [0,1]ⁿ represents the current belief strength that each proposition is true. Initialize **x**₀ with a weak prior (e.g., 0.5).  

3. **Free‑energy gradient step** (dynamical system):  
   \[
   \mathbf{x}_{t+1}= \mathbf{x}_t - \eta \nabla F(\mathbf{x}_t),\quad 
   \nabla F = (\mathbf{x}_t-\boldsymbol\mu) + \lambda \mathbf{A}^\top(\mathbf{A}\mathbf{x}_t-\mathbf{y})
   \]  
   where **y** is the observed truth vector extracted from the candidate answer (1 for asserted true literals, 0 for asserted false), **μ** is a prior mean (0.5), η a step size, λ a weighting of constraint violation. Iterate until ‖xₜ₊₁−xₜ‖ < ε (≈10⁻⁴).  

4. **Sensitivity analysis**: compute the Jacobian of the update w.r.t. **y**:  
   \[
   \mathbf{J}= \frac{\partial \mathbf{x}_{t+1}}{\partial \mathbf{y}} = 
   (\mathbf{I}-\eta(\mathbf{I}+\lambda\mathbf{A}^\top\mathbf{A}))^{-1}\eta\lambda\mathbf{A}^\top
   \]  
   The robustness penalty is the Frobenius norm ‖J‖_F (or trace(JᵀJ)).  

5. **Score** the candidate:  
   \[
   S = -F(\mathbf{x}_\infty) - \alpha \,\|\mathbf{J}\|_F
   \]  
   Lower free energy (better prediction error minimization) increases score; higher sensitivity decreases it, penalizing answers whose truth depends fragilely on input perturbations.  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric values/units.  

**Novelty** – While dynamical‑systems belief updating, free‑energy minimization, and sensitivity analysis each appear separately in cognitive modeling or robust inference, their joint use as a scoring mechanism for answer selection has not been reported in existing QA or reasoning‑evaluation literature.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and updates beliefs via a principled dynamical process.  
Metacognition: 6/10 — provides a global free‑energy measure but lacks explicit self‑monitoring of update steps.  
Hypothesis generation: 7/10 — sensitivity matrix reveals which propositions most affect belief, enabling alternative hypothesis inspection.  
Implementability: 9/10 — relies only on NumPy for matrix ops and stdlib regex; no external APIs or neural components.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

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

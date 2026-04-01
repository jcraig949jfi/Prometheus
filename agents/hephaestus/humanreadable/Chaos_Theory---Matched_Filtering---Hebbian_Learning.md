# Chaos Theory + Matched Filtering + Hebbian Learning

**Fields**: Physics, Signal Processing, Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T01:50:17.700550
**Report Generated**: 2026-03-31T19:54:52.114218

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction** – For each prompt and candidate answer, run a fixed set of regex patterns to pull atomic propositions:  
   - Negations (`not`, `no`) → binary flag `neg`  
   - Comparatives (`greater than`, `less than`, `more`) → token `comp` with direction  
   - Conditionals (`if … then …`) → token `cond` with antecedent/consequent IDs  
   - Numeric values → float token `num` with value  
   - Causal claims (`because`, `leads to`, `results in`) → token `cause` with source/target IDs  
   - Ordering relations (`before`, `after`, `first`, `last`) → token `order` with temporal/size direction  

   Each proposition is assigned an index; a candidate becomes a sparse binary vector **x**∈{0,1}^F (F = total distinct propositions).  

2. **Reference template** – From a small set of gold answers, compute the mean vector **r** = mean(**x_gold**) (still in [0,1]).  

3. **Matched‑filter score** – Compute the normalized cross‑correlation (dot product) between candidate and reference:  
   `s0 = (x·r) / (‖x‖‖r‖)` (numpy dot and linalg.norm). This is the optimal detector for a known signal in white noise.  

4. **Chaos‑inspired stability penalty** – Generate K small perturbations of **x** by flipping each bit with probability ε (e.g., 0.01) → **x̃_k**. Compute their matched‑filter scores s_k. Estimate a finite‑time Lyapunov exponent:  
   `λ = (1/K) Σ log(|s_k – s0| / ε)`.  
   Large λ indicates sensitive dependence → unstable reasoning. Define stability factor `σ = exp(-λ)` (∈(0,1]).  

5. **Hebbian weight adaptation** – Maintain a symmetric weight matrix **W**∈ℝ^{F×F} initialized to zero. After each batch, for every candidate with combined score `c = s0 * σ`, update:  
   `W ← W + η * (c * (x xᵀ))` (outer product, η learning rate).  
   The weighted similarity for a new candidate becomes `s = (xᵀ W x) / (‖x‖‖W x‖)`, injecting Hebbian co‑activation learning.  

6. **Final score** – `score = s0 * σ * (1 + α * (xᵀ W x))`, α a small scaling term. Higher scores reflect better match to reference, low sensitivity to perturbations, and reinforcement of frequently co‑occurring logical structures.  

**Parsed structural features** – Negations, comparatives, conditionals, numeric values, causal claims, ordering relations (all extracted via deterministic regex).  

**Novelty** – While matched filtering, Lyapunov‑exponent analysis, and Hebbian learning each appear in signal processing, dynamical systems, and neuroscience, their joint use for scoring logical structure in text has not been reported in the literature; the combination creates a stability‑aware, adaptive similarity measure rather than a pure kernel or bag‑of‑words method.  

**Ratings**  
Reasoning: 8/10 — captures logical fidelity, sensitivity to perturbation, and Hebbian reinforcement of useful patterns.  
Metacognition: 6/10 — provides a self‑assessment via stability factor but lacks explicit reflection on uncertainty sources.  
Hypothesis generation: 5/10 — can propose higher‑scoring candidates by exploring perturbations, yet no generative mechanism beyond similarity maximization.  
Implementability: 9/10 — relies only on NumPy vector operations, outer products, and regex; feasible in <200 lines.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:54:20.814983

---

## Code

*No code was produced for this combination.*

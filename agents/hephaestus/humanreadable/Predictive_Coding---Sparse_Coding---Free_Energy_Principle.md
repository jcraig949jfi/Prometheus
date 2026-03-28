# Predictive Coding + Sparse Coding + Free Energy Principle

**Fields**: Cognitive Science, Neuroscience, Theoretical Neuroscience
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T12:47:34.241385
**Report Generated**: 2026-03-27T06:37:44.625398

---

## Nous Analysis

The combined algorithm treats each candidate answer as a sparse latent code that must reconstruct the prompt under a hierarchical generative model while minimizing variational free energy.  

**Data structures**  
- `prompt_tokens`: list of word IDs from a fixed vocabulary (size V).  
- `answer_tokens`: same for each candidate.  
- `W_l`: numpy array shape (V, K_l) – dictionary at hierarchical level l (learned offline via Olshausen‑Field sparse coding on a corpus).  
- `a_l`: sparse activation vector (K_l,) for level l, enforced by L1 penalty λ‖a_l‖₁.  
- `ε_l`: prediction‑error vector (V,) at level l.  

**Operations**  
1. **Encode** each answer into a multi‑level sparse code by solving  
   `min_{a_l} ‖x - W_l a_l‖₂² + λ‖a_l‖₁` where `x` is the one‑hot bag‑of‑words of the answer; iterate l=1…L with a top‑down prediction `x̂_l = W_{l+1} a_{l+1}` and compute ε_l = x - x̂_l.  
2. **Predictive coding pass**: propagate ε_l upward, update higher‑level activities via gradient descent on free energy `F = Σ_l ½‖ε_l‖₂² + λ‖a_l‖₁`.  
3. **Score** the candidate by the final free energy `F` after convergence; lower F indicates better prediction of the prompt when the answer is used as top‑down input (i.e., we replace the prompt’s bag‑of‑words with the answer’s reconstruction and compute F).  

**Structural features parsed** (via regex before encoding)  
- Negations (`not`, `n’t`) → flip sign of associated token weight.  
- Comparatives (`more than`, `less than`) → insert a numeric constraint token.  
- Conditionals (`if … then …`) → create two‑clause sub‑graphs with directed edges.  
- Numeric values → extract as separate tokens with magnitude‑scaled one‑hot vectors.  
- Causal claims (`because`, `leads to`) → add directed edge tokens.  
- Ordering relations (`first`, `last`, `before`, `after`) → encode positional tokens.  

These features modify the one‑hot input `x` so that the sparse coding step must respect logical structure, making free energy sensitive to reasoning errors.  

**Novelty**  
The specific coupling of hierarchical predictive coding with offline Olshausen‑Field sparse dictionaries and a free‑energy scoring function has not been published as a unified reasoning evaluator; prior work uses either predictive coding neural nets or sparse coding alone, but not the combined variational free‑energy objective for answer ranking.  

**Ratings**  
Reasoning: 8/10 — captures hierarchical error propagation and constraint satisfaction, strong for logical deduction.  
Metacognition: 6/10 — can monitor its own free‑energy reduction but lacks explicit self‑reflection on strategy shifts.  
Hypothesis generation: 5/10 — generates sparse reconstructions but does not propose new hypotheses beyond given candidates.  
Implementability: 9/10 — relies only on numpy (sparse coding via ISTA) and regex; no external libraries needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: unproductive
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Predictive Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Sparse Coding**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Free Energy Principle + Predictive Coding: strong positive synergy (+0.600). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Free Energy Principle + Sparse Coding: negative interaction (-0.064). Keep these concepts in separate code paths to avoid interference.

Similar combinations that forged successfully:
- Fractal Geometry + Predictive Coding + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Predictive Coding + Falsificationism + Free Energy Principle (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

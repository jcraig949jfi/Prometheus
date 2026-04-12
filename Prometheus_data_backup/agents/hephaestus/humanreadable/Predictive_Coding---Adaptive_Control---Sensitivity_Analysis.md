# Predictive Coding + Adaptive Control + Sensitivity Analysis

**Fields**: Cognitive Science, Control Theory, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T10:38:50.372704
**Report Generated**: 2026-03-31T17:15:56.398561

---

## Nous Analysis

**Algorithm**  
We build a lightweight, numpy‑based scorer that treats a candidate answer as a set of propositional features and updates a linear generative model online, while penalizing solutions that are fragile to small perturbations.

1. **Feature extraction** – For each sentence we run a handful of regexes to detect:  
   - Negations (`\bnot\b|\bno\b|\bnever\b`)  
   - Comparatives (`\bmore\b|\bless\b|\bthan\b|\bgreater\b|\blesser\b`)  
   - Conditionals (`\bif\b.*\bthen\b|\bunless\b|\bprovided\b`)  
   - Numeric tokens (`\d+(\.\d+)?`)  
   - Causal cues (`\bbecause\b|\bleads to\b|\bresults in\b|\bdue to\b`)  
   - Ordering relations (`\bbefore\b|\bafter\b|\bfirst\b|\blast\b|\bprecedes\b|\bfollows\b`)  
   Each detected cue yields a binary feature; numeric values are normalized (e.g., divided by the max number seen in the prompt) and added as a continuous feature. The output is a feature matrix **X** ∈ ℝ^{p×f} (p propositions, f features).

2. **Generative model (predictive coding)** – A weight vector **w** ∈ ℝ^{f} predicts the expected correctness of a proposition: ŷ = X·w. The prediction error for a candidate is e = y_true – ŷ, where y_true is a binary label supplied by a simple rubric (e.g., 1 if the answer contains the required claim, 0 otherwise). The total error is the L2 norm ‖e‖₂.

3. **Adaptive control (online weight update)** – After scoring a candidate we adjust **w** with a delta rule:  
   **w** ← **w** + α·e·X̄, where X̄ is the mean feature vector of the candidate and α∈(0,1) is a small learning rate. This implements self‑tuning: the model reduces surprise on seen patterns.

4. **Sensitivity analysis** – We compute how the score changes if each feature is perturbed by ±δ (δ=0.1). The sensitivity vector is s = |w|·δ (since ŷ is linear). The overall fragility is ‖s‖₁. The final score combines accuracy and robustness:  
   Score = ŷ – λ·‖s‖₁, with λ controlling the trade‑off.

All operations use numpy dot products, norms, and simple array updates; no external libraries are needed.

**Structural features parsed** – Negations, comparatives, conditionals, numeric values, causal claims, ordering relations (as listed above). These are the primitives the algorithm treats as observable variables in its hierarchical generative model.

**Novelty** – Predictive coding provides a Bayesian error‑minimization view; adaptive control supplies an online self‑tuning regulator; sensitivity analysis adds a robustness penalty. While each component appears in cognitive science or control literature, their conjunction for scoring reasoning answers via a linear, numpy‑implemented model is not documented in existing QA or educational‑assessment tools, making the combination novel for this application.

**Reasoning: 8/10** – The algorithm directly models logical structure and updates beliefs, yielding coherent error‑based scores.  
**Metacognition: 6/10** – It monitors prediction error but does not explicitly reason about its own uncertainty beyond the sensitivity term.  
**Hypothesis generation: 7/10** – By adjusting **w**, it forms implicit hypotheses about which features predict correctness, though hypothesis space is limited to linear combos.  
**Implementability: 9/10** – Only numpy and stdlib are used; regex feature extraction and linear algebra are straightforward and efficient.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T17:15:40.257742

---

## Code

*No code was produced for this combination.*

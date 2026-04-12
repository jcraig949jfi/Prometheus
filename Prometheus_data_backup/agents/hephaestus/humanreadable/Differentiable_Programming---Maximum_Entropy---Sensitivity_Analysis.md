# Differentiable Programming + Maximum Entropy + Sensitivity Analysis

**Fields**: Computer Science, Statistical Physics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T03:11:32.308981
**Report Generated**: 2026-03-31T14:34:50.096717

---

## Nous Analysis

**Algorithm**  
We build a maximum‑entropy (log‑linear) model over a set of binary/logical features extracted from the prompt + each candidate answer.  
*Data structures*  
- `feat_mat`: `np.ndarray` of shape `(n_cands, n_feat)` where each row is a feature vector for one answer. Features are indicator functions for parsed linguistic patterns (see §2).  
- `w`: `np.ndarray` of shape `(n_feat,)` – the weight vector to be learned.  
- `emp_exp`: `np.ndarray` of shape `(n_feat,)` – empirical feature expectations derived solely from the prompt (treated as the “true” distribution).  

*Operations* (all using only NumPy and the stdlib)  
1. **Feature extraction** – deterministic regex‑based parsers fill `feat_mat`.  
2. **Score computation** – `logits = feat_mat @ w` (unnormalized log‑probabilities).  
3. **Log‑partition** – `logZ = scipy.special.logsumexp(logits)` (implemented with `np.max` and `np.log(np.sum(np.exp(logits - np.max(logits)))) + np.max(logits)` to stay in stdlib).  
4. **Log‑likelihood** – `LL = np.dot(emp_exp, w) - logZ`.  
5. **Differentiable programming** – we derive the gradient analytically: `grad = emp_exp - model_exp`, where `model_exp = (feat_mat.T @ np.exp(logits - logZ)) / np.sum(np.exp(logits - logZ))`. This gradient is obtained via a manual reverse‑mode pass (no external autodiff library).  
6. **Weight update** – simple gradient ascent: `w += lr * grad`. Iterate until LL change < 1e‑4.  
7. **Sensitivity analysis** – the Jacobian of the log‑probability w.r.t. input feature perturbations is `J = np.diag(p) - np.outer(p, p)` where `p = np.exp(logits - logZ) / np.sum(np.exp(logits - logZ))`. Multiplying `J` by the feature‑perturbation vector yields the change in score for each answer, giving a robustness measure.  

*Scoring logic* – after convergence, the final score for each candidate is its normalized log‑probability `logp = logits - logZ`. The answer with the highest `logp` is selected; the magnitude of `logp` also reflects confidence, while the sensitivity Jacobian quantifies how fragile that confidence is to small perturbations in the parsed features.  

**Structural features parsed**  
- Negation tokens (`not`, `never`, `no`).  
- Comparative/superlative adjectives and adverbs (`more`, `less`, `best`, `worse`).  
- Conditional constructions (`if … then`, `unless`, `provided that`).  
- Causal connectives (`because`, `leads to`, `results in`, `due to`).  
- Numeric expressions with units and operators (`5 km`, `≥ 3`, `twice as`).  
- Ordering/temporal relations (`before`, `after`, `earlier`, `later`).  
- Quantifiers (`all`, `some`, `none`, `most`).  
- Entity mentions and proper nouns (captured via simple regex for capitalized tokens).  

**Novelty**  
The combination mirrors a conditional random field (CRF) with hand‑crafted logical features, but the learning loop uses explicit differentiable programming (manual reverse‑mode gradient) and the final scoring step reports a sensitivity‑based robustness metric. Existing work (e.g., DeepProbLog, Neural Theorem Provers) couples neural networks to logical reasoning; here we replace the neural net with a pure NumPy max‑ent learner, making the approach transparent and easily auditable. While maximum‑entropy modeling and sensitivity analysis are classic, their joint use for answer scoring via differentiable weight updates is not common in public reasoning‑evaluation tools.  

**Ratings**  
Reasoning: 8/10 — The method captures logical structure, learns weights from prompt constraints, and provides a principled probabilistic score.  
Metacognition: 6/10 — It offers a sensitivity measure but lacks explicit self‑reflection on uncertainty sources beyond local perturbations.  
Hypothesis generation: 7/10 — Feature extraction yields interpretable patterns that can be inspected and expanded; however, generation of new hypotheses is limited to the predefined feature set.  
Implementability: 9/10 — All components rely solely on NumPy and the Python standard library; no external ML packages or APIs are required.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Differentiable Programming**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 


Similar combinations that forged successfully:
- Adaptive Control + Mechanism Design + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Differentiable Programming + Abductive Reasoning (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

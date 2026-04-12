# Self-Organized Criticality + Free Energy Principle + Sensitivity Analysis

**Fields**: Complex Systems, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T12:10:47.457854
**Report Generated**: 2026-03-31T16:21:16.409115

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions \(p_i\) from a prompt and each candidate answer. Each proposition gets a binary truth variable \(x_i\in\{0,1\}\) (1 if the proposition is asserted, 0 if negated or absent).  
2. **Knowledge graph** – Build a weighted adjacency matrix \(W\in\mathbb{R}^{n\times n}\) where \(W_{ij}\) encodes the strength of an implication \(p_i\rightarrow p_j\) extracted from conditionals, causal verbs, or comparatives (e.g., “if A then B” → \(W_{AB}=1\); “A causes B” → \(W_{AB}=0.8\); negations flip the sign).  
3. **Self‑organized criticality dynamics** – Initialize activity vector \(a^{(0)} = x\). Iterate:  
   \[
   a^{(t+1)} = \sigma\!\left(W a^{(t)}\right),\qquad \sigma(z)=\frac{1}{1+e^{-z}}
   \]  
   After each step compute the avalanche size \(\Delta a^{(t)} = a^{(t+1)}-a^{(t)}\). Stop when the distribution of \(\|\Delta a^{(t)}\|_2\) over the last k steps exhibits a power‑law tail (estimated via linear fit on log‑log histogram; slope ≈ ‑1). This is the SOC critical point.  
4. **Free‑energy (prediction error)** – Compute prediction \(\hat a = W a^{*}\) where \(a^{*}\) is the fixed‑point activity. Free energy \(F = \|a^{*}-\hat a\|_2^2\). Lower F indicates the candidate’s propositions are better predicted by the implicit model.  
5. **Sensitivity analysis** – Jacobian \(J = \frac{\partial a^{*}}{\partial x}\) approximated by finite differences: perturb each input proposition \(x_i\) by ±ε, re‑run the SOC loop, and record change in \(a^{*}\). Sensitivity score \(S = \sum_i |J_{ii}|\) (total self‑influence). High S means the answer is fragile to small wording changes.  
6. **Final score** – \(\text{Score} = -\alpha F - \beta S\) (α,β > 0 tuned on a validation set). Lower free energy and lower sensitivity yield higher scores.

**Structural features parsed** – negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), causal verbs (“because”, “leads to”, “results in”), numeric values and units, ordering/temporal markers (“first”, “before”, “after”), quantifiers (“all”, “some”, “none”).

**Novelty** – While SOC, free‑energy principle, and sensitivity analysis appear separately in cognitive modeling and ML, their joint use to drive a deterministic, numpy‑based scoring pipeline for answer evaluation has not been reported in the literature.

**Rating**  
Reasoning: 8/10 — captures logical propagation, prediction error, and robustness in a single differentiable‑free system.  
Metacognition: 6/10 — the scheme monitors its own activity distribution but lacks explicit self‑reflection on hypothesis quality.  
Hypothesis generation: 7/10 — alternative activity patterns emerge naturally under perturbation, enabling hypothesis ranking.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and standard‑library loops; no external APIs or neural nets.

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

**Forge Timestamp**: 2026-03-31T15:25:32.661538

---

## Code

*No code was produced for this combination.*

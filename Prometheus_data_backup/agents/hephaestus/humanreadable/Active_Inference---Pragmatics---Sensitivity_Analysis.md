# Active Inference + Pragmatics + Sensitivity Analysis

**Fields**: Cognitive Science, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T12:57:25.122936
**Report Generated**: 2026-03-31T19:09:43.811530

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Using a handful of regex patterns we extract propositions from the prompt and each candidate answer. A proposition is stored as a lightweight Python object with fields:  
   - `type` ∈ {`atomic`, `negation`, `conditional`, `comparative`, `causal`}  
   - `args` (tuple of constants or variable placeholders)  
   - `polarity` (+1 for affirmed, –1 for negated)  
   - `weight` (pragmatic relevance, initialized to 1.0)  
   The set of distinct propositions `{p₀,…,pₙ₋₁}` defines a binary world vector **w** ∈ {0,1}ⁿ.  

2. **Belief representation** – A numpy array `b` of length 2ⁿ holds the agent’s belief over all possible worlds (initialized uniform).  

3. **Generative likelihood** – For a candidate answer `a` we build a likelihood vector `Lₐ[w]` = ∏ᵢ `wᵢ^{matchᵢ}` where `matchᵢ` = 1 if the answer asserts `pᵢ` (or its negation) and the world satisfies it, otherwise 0. This is computed efficiently with numpy broadcasting.  

4. **Expected free energy (Active Inference)** –  
   \[
   G(a) = \underbrace{-\sum_w b[w]\log Lₐ[w]}_{\text{expected surprise}} \;+\; \underbrace{H(b)}_{\text{entropy of belief}}
   \]  
   where `H(b) = -∑ b log b`. Lower `G` means the answer better explains the world under current beliefs.  

5. **Pragmatic weighting** – Before step 4 we modulate each proposition’s contribution to the likelihood by a relevance weight derived from Grice‑style maxims:  
   - *Informativeness*: inverse of proposition frequency in the prompt.  
   - *Relevance*: distance (in token count) from the question focus, transformed with a softmax.  
   The weight multiplies the corresponding column in the likelihood product, effectively scaling surprise for context‑ually salient clauses.  

6. **Sensitivity analysis** – For each proposition `pᵢ` we create a perturbed belief `b⁽ⁱ⁾` by flipping the truth value of `pᵢ` in all worlds (i.e., `b⁽ⁱ⁾[w] = b[w⊕eᵢ]`). We recompute `G⁽ⁱ⁾(a)` and compute the standard deviation across perturbations:  
   \[
   S(a) = \sqrt{\frac{1}{n}\sum_i \bigl(G⁽ⁱ⁾(a)-\bar G\bigr)^2}
   \]  
   A low `S` indicates the answer’s score is robust to small changes in the input.  

7. **Final score** –  
   \[
   \text{Score}(a) = -G(a) + \lambda \, \exp\!\bigl(-\beta\, S(a)\bigr)
   \]  
   with λ,β set to modest constants (e.g., 0.5, 2.0). The algorithm uses only numpy for array ops and the standard library for regex and data structures.

**Structural features parsed** – negations (`not`, `no`), comparatives (`greater than`, `less than`, `≤`, `≥`), conditionals (`if … then …`, `unless`), causal claims (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `first`, `last`), numeric values (integers, decimals), and quantifiers (`all`, `some`, `none`, `most`).  

**Novelty** – While each component has precedents (probabilistic logic programming for belief updating, Grice‑based weighting in computational pragmatics, and variance‑based sensitivity in uncertainty quantification), their tight coupling inside an active‑inference expected‑free‑energy loop—where epistemic foraging drives answer selection, pragmatics shapes the likelihood, and sensitivity quantifies robustness—has not been reported as a unified scoring mechanism.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on discrete world enumeration, limiting scalability.  
Metacognition: 6/10 — entropy term provides a basic self‑assessment of belief uncertainty; no higher‑order reflection on the inference process itself.  
Hypothesis generation: 5/10 — the model evaluates given candidates; it does not propose new hypotheses beyond the supplied set.  
Implementability: 8/10 — all steps use regex, numpy vectorized ops, and plain Python objects; no external libraries or APIs needed.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Active Inference**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Active Inference + Pragmatics: strong positive synergy (+0.236). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Active Inference + Epistemology + Network Science (accuracy: 0%, calibration: 0%)
- Active Inference + Free Energy Principle + Model Checking (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:09:21.743374

---

## Code

*No code was produced for this combination.*

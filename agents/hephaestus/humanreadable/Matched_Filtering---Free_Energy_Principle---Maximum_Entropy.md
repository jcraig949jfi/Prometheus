# Matched Filtering + Free Energy Principle + Maximum Entropy

**Fields**: Signal Processing, Theoretical Neuroscience, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T04:05:31.617363
**Report Generated**: 2026-03-27T06:37:51.427560

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction** – From the prompt and each candidate answer we build a binary feature vector **f** ∈ {0,1}^k using deterministic regexes that capture:  
   - negation tokens (`not`, `no`, `n’t`)  
   - comparatives (`more`, `less`, `-er`, `than`)  
   - conditionals (`if`, `unless`, `provided that`)  
   - numeric values (integers, decimals, percentages)  
   - causal cues (`because`, `since`, `therefore`, `leads to`)  
   - ordering relations (`before`, `after`, `first`, `last`, `>`, `<`).  
   Each regex yields a single dimension; the vector is the concatenation of all matches (order fixed across prompt and candidates).  

2. **Constraint matrix (prompt model)** – From the prompt’s feature vector **fₚ** we construct a diagonal weight matrix **W** = diag(w₁,…,w_k) where w_i = 1 if the i‑th feature appears in the prompt, else 0. This encodes the hard constraints that a correct answer must share the same structural pattern.  

3. **Maximum‑entropy distribution** – Given constraints **Wf = fₚ**, the least‑biased distribution over feature vectors is the exponential family:  
   \[
   p(f) = \frac{1}{Z}\exp\bigl(\lambda^\top (Wf)\bigr),\qquad 
   \lambda = \log\frac{fₚ}{1-fₚ}
   \]  
   (λ computed element‑wise; zeros give λ=0). The partition function Z is obtained analytically because W is diagonal: Z = ∏_i (1+e^{λ_i w_i}).  

4. **Variational free energy** – For a candidate **f_c** we define a simple mean‑field variational distribution q(f) = δ_{f,f_c} (a point mass). The free energy is:  
   \[
   F = \underbrace{-\log p(f_c)}_{\text{energy}} + \underbrace{D_{KL}(q\|p)}_{=\ -\log p(f_c)} = -2\log p(f_c).
   \]  
   Using numpy we compute log‑p via dot‑product: log p = λᵀ(Wf_c) − log Z.  

5. **Matched‑filtering score** – Treat the prompt’s weighted feature vector **t = Wfₚ** as a template. The candidate’s matched‑filter output is the normalized cross‑correlation:  
   \[
   m = \frac{t^\top (Wf_c)}{\|t\|\,\|Wf_c\|}.
   \]  
   (Implemented with `np.dot` and `np.linalg.norm`).  

6. **Final score** – Combine the two terms (lower free energy is better, higher correlation is better):  
   \[
   S = -F + \alpha\,m,
   \]  
   with α set to 1.0 for equal weighting. Candidates are ranked by descending S.  

**Structural features parsed**  
Negations, comparatives, conditionals, numeric values, causal claims, and ordering relations (including transitive chains derived from `>`, `<`, `before`, `after`).  

**Novelty**  
Matched filtering, free‑energy minimization, and maximum‑entropy inference have each been applied separately to language modeling or signal detection. Their joint use to score reasoning answers — by treating structural constraints as a template, deriving a least‑biased distribution, and evaluating candidates via both energetic and correlation terms — has not been reported in the literature, making the combination novel for this task.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and noise robustness but ignores deeper semantic nuance.  
Metacognition: 5/10 — algorithm does not monitor its own uncertainty beyond the free‑energy term.  
Hypothesis generation: 6/10 — can propose alternative feature vectors via sampling from the max‑entropy distribution, though not explicit.  
Implementability: 8/10 — relies only on regex, numpy linear algebra, and basic loops; straightforward to code in <150 lines.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Matched Filtering**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Free Energy Principle**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 35% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Maximum Entropy**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 

- Free Energy Principle + Maximum Entropy: strong positive synergy (+0.241). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Ergodic Theory + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Prime Number Theory + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)
- Thermodynamics + Free Energy Principle + Maximum Entropy (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

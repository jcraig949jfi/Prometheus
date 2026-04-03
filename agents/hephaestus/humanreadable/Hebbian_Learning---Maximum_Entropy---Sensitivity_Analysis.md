# Hebbian Learning + Maximum Entropy + Sensitivity Analysis

**Fields**: Neuroscience, Statistical Physics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:41:34.614250
**Report Generated**: 2026-04-02T04:20:11.835038

---

## Nous Analysis

**Algorithm**  
1. **Parse & encode** – Using regex we extract atomic propositions *pᵢ* (e.g., “X increases Y”, “¬Z”, “A > B”) from the prompt and each candidate answer. Each proposition gets an index *i* and a signed activation *aᵢ∈{‑1,0,1}* (‑1 for negation, 0 for absent, 1 for asserted).  
2. **Hebbian weight matrix** – Initialize a symmetric numpy array *W*∈ℝⁿˣⁿ with zeros. For every sentence in the prompt, for each pair *(i,j)* where both *aᵢ* and *aⱼ* are non‑zero, update  
   \[
   W_{ij}\leftarrow W_{ij}+ \eta\, a_i a_j
   \]  
   with learning rate η=0.1. This implements activity‑dependent strengthening (Hebbian).  
3. **Maximum‑Entropy constraint solving** – Treat each proposition as a binary variable *xᵢ*. The expected co‑occurrence under the model must match the empirical Hebbian strengths:  
   \[
   \mathbb{E}[x_i x_j]=\frac{W_{ij}+1}{2}\quad\text{(scaled to }[0,1]\text{)}.
   \]  
   We solve for log‑linear parameters *θ* using Iterative Scaling (GIS) with numpy: start θ=0, repeatedly adjust θᵢ←θᵢ+log( Cᵢ / 𝔼[xᵢ] ) until convergence, where Cᵢ is the target expectation derived from *W*. The resulting distribution is  
   \[
   P(x)=\frac{1}{Z}\exp\Big(\sum_i\theta_i x_i+\sum_{i<j}W_{ij}x_i x_j\Big).
   \]  
4. **Sensitivity analysis** – For each input feature *fₖ* (presence/negation of a specific token), compute the finite‑difference gradient of the log‑probability of a candidate answer’s proposition set *S*:  
   \[
   g_k=\frac{\log P_S(\theta+\epsilon e_k)-\log P_S(\theta-\epsilon e_k)}{2\epsilon},
   \]  
   with ε=1e‑3. The sensitivity score is the ℓ₂ norm ‖g‖₂.  
5. **Scoring** – For a candidate answer *S* (set of propositions with signs), compute its log‑probability under *P*:  
   \[
   \text{logP}_S=\sum_{i\in S}\theta_i+\sum_{i<j,i,j\in S}W_{ij}-\log Z.
   \]  
   Final score = logP_S − λ‖g‖₂, with λ=0.5 to penalize fragile predictions.

**Structural features parsed**  
- Negations (“not”, “no”, “¬”)  
- Comparatives and superlatives (“greater than”, “less than”, “most”, “least”)  
- Conditionals (“if … then”, “provided that”, “unless”)  
- Causal verbs (“causes”, “leads to”, “results in”, “due to”)  
- Temporal/ordering relations (“before”, “after”, “precedes”)  
- Numeric values with units and arithmetic relations (“=”, “≈”, “≥”, “≤”)  
- Quantifiers (“all”, “some”, “none”)  

**Novelty**  
Pure Hebbian updates are common in neuroscience‑inspired ML but rarely paired with MaxEnt constraint propagation and explicit sensitivity gradients for answer scoring. Existing work uses weighted Markov logic networks or neural attention; this combination replaces learning with a biologically plausible Hebbian step, then enforces maximum‑entropy consistency, and finally quantifies robustness via sensitivity — an approach not seen in current NLP evaluation tools.

**Ratings**  
Reasoning: 7/10 — captures logical structure and uncertainty but relies on linear approximations.  
Metacognition: 6/10 — sensitivity provides a rudimentary self‑check of robustness, yet no higher‑order reflection.  
Hypothesis generation: 5/10 — generates implicit distributions over propositions, but does not propose new hypotheses beyond scoring.  
Implementability: 9/10 — only numpy and stdlib needed; all steps are concrete, deterministic loops.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
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

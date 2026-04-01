# Sparse Autoencoders + Criticality + Compositionality

**Fields**: Computer Science, Complex Systems, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T15:07:51.785257
**Report Generated**: 2026-03-31T16:21:16.546114

---

## Nous Analysis

**Algorithm**  
1. **Parse** the prompt with a handful of regex patterns to extract atomic propositions \(p_i\) (e.g., “X > Y”, “¬A”, “if B then C”, “because D”). Each proposition gets an index \(i\) and a type (negation, comparative, conditional, causal, ordering, numeric).  
2. **Build a dictionary matrix** \(W\in\{0,1\}^{m\times k}\) where each column \(w_i\) is a one‑hot vector for proposition \(p_i\). \(m\) is the number of distinct propositions observed in the prompt; \(k\) is the same (we start with an identity dictionary).  
3. **Sparse coding step** (the autoencoder‑like part): for each candidate answer \(a_j\) we create a binary observation vector \(x_j\in\{0,1\}^m\) indicating which propositions appear in the answer (again via regex). We solve \(\min_{\alpha_j}\|x_j-W\alpha_j\|_2^2+\lambda\|\alpha_j\|_0\) using Orthogonal Matching Pursuit (OMP) – a pure‑numpy iterative process that yields a sparse coefficient vector \(\alpha_j\). The reconstruction error \(e_j=\|x_j-W\alpha_j\|_2^2\) measures how well the answer can be expressed as a combination of prompt propositions.  
4. **Criticality weighting**: compute the empirical variance of each dictionary atom across all candidates, \(s_i=\mathrm{var}(\{\alpha_{j,i}\}_j)\). High \(s_i\) indicates a direction where small changes in answer produce large changes in representation (susceptibility). Form a diagonal weight matrix \(S=\mathrm{diag}(s)\).  
5. **Compositional scoring**: using the same regex parse, recursively evaluate the logical form of the answer (truth‑functional semantics) to obtain a binary truth vector \(t_j\) where \(t_{j,i}=1\) if proposition \(p_i\) is satisfied under the answer’s interpretation (negations flip, conditionals use material implication, etc.). The final score is  
\[
\text{score}_j = -\big(e_j + \lambda\|\alpha_j\|_0\big) \;+\; \alpha_j^\top S t_j .
\]  
All operations use only NumPy arrays and Python’s standard‑library `re`.

**Structural features parsed** – negations (“not”, “no”), comparatives (“>”, “<”, “greater than”, “less than”), conditionals (“if … then …”, “implies”), causal claims (“because”, “leads to”), ordering relations (“before”, “after”, “first”, “last”), numeric values, conjunctions/disjunctions (“and”, “or”).  

**Novelty** – While sparse autoencoders, criticality‑based susceptibility, and compositional truth‑functional evaluation each appear separately, their joint use—where sparsity‑learned coefficients are weighted by susceptibility and then combined with a compositional truth vector—is not described in existing NLP reasoning tools, making the combination novel.

**Rating**  
Reasoning: 7/10 — captures logical structure and sparsity but relies on linear approximations.  
Metacognition: 5/10 — limited self‑monitoring; no explicit uncertainty estimation beyond variance.  
Hypothesis generation: 6/10 — can propose alternative sparse codes, but generation is rudimentary.  
Implementability: 8/10 — straightforward NumPy/OMP and regex; no external dependencies.

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

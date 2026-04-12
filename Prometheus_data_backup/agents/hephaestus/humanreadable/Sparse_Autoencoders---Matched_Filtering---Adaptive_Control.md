# Sparse Autoencoders + Matched Filtering + Adaptive Control

**Fields**: Computer Science, Signal Processing, Control Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T20:52:52.215262
**Report Generated**: 2026-03-31T14:34:57.257924

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only `re` we extract a set of propositional tuples `P = {(s, p, o, pol, mod)}` where `s` and `o` are noun phrases, `p` is a verb or relational phrase, `pol ∈ {+1,‑1}` marks negation, and `mod` encodes modality (conditional, comparative, causal, numeric, ordering). Each distinct predicate type is assigned an index `i`.  
2. **Sparse dictionary** – Maintain a matrix `D ∈ ℝ^{F×K}` (F = number of feature dimensions, K = dictionary size) initialized randomly. For a parsed question we build a binary feature vector `x ∈ {0,1}^F` where `x_i = 1` if predicate `i` appears (weighted by polarity and modality flags). The sparse code `a` is obtained by one iteration of **matching pursuit**:  
   ```
   r = x
   while ‖r‖₂ > τ:
       i = argmax_j |d_jᵀ r|
       a_i = sign(d_jᵀ r) * (d_jᵀ r)
       r = r - a_i * d_j
   ```  
   `τ` is a sparsity threshold.  
3. **Matched‑filter scoring** – A reference answer (gold) is parsed and encoded to obtain its sparse code `a_ref`. The similarity score is the normalized cross‑correlation (matched filter):  
   ```
   sim = (a · a_ref) / (‖a‖₂ * ‖a_ref‖₂ + ε)
   ```  
4. **Adaptive control** – After each scoring episode we compute an error `e = y_target - sim` (where `y_target` is a provisional label from a simple rule‑based baseline). The dictionary is updated with an online K‑SVM step:  
   ```
   D ← D + η * e * (a_ref - D a) aᵀ
   λ ← λ + β * e   # sparsity regularizer
   ```  
   `η, β` are small learning rates. The final score combines similarity and a penalty for missing propositions:  
   ```
   score = sim - α * ‖a - a_ref‖₁
   ```  

**Structural features parsed** – negations (`not`, `no`), comparatives (`more … than`, `less … than`), conditionals (`if … then`, `unless`), causal claims (`because`, `leads to`, `results in`), numeric values with units, ordering relations (`before/after`, `greater/less than`), and conjunctions/disjunctions.

**Novelty** – While sparse coding and matched filtering are classic signal‑processing tools, and adaptive control appears in adaptive signal processing, their joint use for structured propositional encoding and online template tuning in a pure‑numpy reasoning scorer has not been reported in the literature; existing NLP scorers rely on bag‑of‑words, TF‑IDF cosine, or neural similarity, making this combination novel.

**Ratings**  
Reasoning: 7/10 — captures logical structure via sparse codes and correlates with a reference template, but limited to linear matching.  
Metacognition: 5/10 — only a simple error‑driven adaptation; no explicit self‑monitoring of confidence or strategy selection.  
Hypothesis generation: 6/10 — can propose alternative parses via residual pursuit, yet lacks generative recombination of predicates.  
Implementability: 8/10 — relies solely on regex, NumPy linear algebra, and basic loops; straightforward to code and debug.

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

# Sparse Autoencoders + Kalman Filtering + Normalized Compression Distance

**Fields**: Computer Science, Signal Processing, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T23:54:53.445609
**Report Generated**: 2026-04-02T04:20:11.600532

---

## Nous Analysis

**Algorithm**  
1. **Parsing & feature extraction** – Using only `re` we extract from each text (reference answer and candidate answer) a list of atomic propositions *pᵢ*. Each proposition is encoded as a tuple *(predicate, subject, object, polarity, comparative‑op, numeric‑value, causal‑flag)*. From the tuple we build a binary feature vector *f* of length *V* (the vocabulary of predicates, comparatives, causal markers, and unit‑annotated numbers). Negations flip polarity; comparatives map to `<,>,<=,>=`; conditionals produce two linked propositions with a temporal edge; causal flags link cause→effect.  

2. **Sparse autoencoder dictionary** – Offline, we run a simple iterative hard‑thresholding algorithm (OMP) on a corpus of reasoning texts to learn a dictionary *D ∈ ℝ^{V×k}* (k≈50) that yields sparse codes *α* with ‖α‖₀ ≤ 5. The dictionary and its transpose are stored as NumPy arrays.  

3. **State representation** – The latent state *xₜ ∈ ℝ^{k}* is the sparse code of the reference answer’s feature vector *f_ref*: *x₀ = argmin_α ‖f_ref − Dα‖₂² + λ‖α‖₁* (solved with a few ISTA iterations).  

4. **Kalman filtering update** – For each candidate answer we compute its feature vector *f_cand* and its observation *z = D⁺ f_cand* (pseudo‑inverse gives a dense observation). We assume a linear Gaussian model:  
   - Prediction: *x̂ = F x_{t-1}*, *P̂ = F P_{t-1} Fᵀ + Q* (with *F = I*, *Q = 1e‑4 I*).  
   - Observation model: *H = I*, *R = σ² I* (σ² set to median variance of *z* over a validation set).  
   - Kalman gain: *K = P̂ Hᵀ (H P̂ Hᵀ + R)⁻¹*.  
   - State update: *x_t = x̂ + K (z − H x̂)*, *P_t = (I − K H) P̂*.  

5. **Scoring** – The innovation *ν = z − H x̂* is fed into the Negative Compression Distance (NCD) approximated by the ratio of compressed lengths:  
   - Compute *L(z)* = length of `zlib.compress(z.tobytes())`.  
   - Compute *L(x̂)* similarly.  
   - Compute *L([z;x̂])* = length of concatenated bytes.  
   - NCD = (L([z;x̂]) − min(L(z),L(x̂))) / max(L(z),L(x̂)).  
   The final score = −NCD (higher is better). Lower NCD indicates the candidate’s compressed representation is close to the filtered belief state, i.e., it preserves the parsed structural propositions.

**Structural features parsed**  
- Atomic predicates (verbs, relations)  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `≥`, `≤`)  
- Conditionals (`if … then`, `unless`)  
- Causal markers (`because`, `causes`, `leads to`)  
- Temporal/ordering terms (`before`, `after`, `first`, `second`)  
- Numeric values with units (e.g., `5 km`, `3.2%`)  

**Novelty**  
Sparse autoencoders provide disentangled, dictionary‑based features; Kalman filtering supplies recursive belief updates over those features; NCD offers a model‑free, compression‑based similarity. While each component appears individually in representation learning, state tracking, and similarity measurement, their joint use for scoring reasoned answers—where parsing yields propositional features, sparse coding yields a latent state, Kalman filtering refines it with observed candidate features, and NCD quantifies residual divergence—has not been reported in existing work, making the combination novel.

**Ratings**  
Reasoning: 7/10 — The method explicitly propagates logical structure through a Kalman update, capturing consistency and contradiction better than pure similarity metrics.  
Metacognition: 5/10 — No explicit mechanism for monitoring uncertainty beyond the Kalman covariance; self‑reflection is limited.  
Hypothesis generation: 4/10 — The system scores given candidates but does not propose new answers or alternative parses.  
Implementability: 8/10 — All steps rely on NumPy and the Python standard library; dictionary learning uses simple OMP, and Kalman updates are linear algebra.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 8/10 |
| **Composite** | **5.33** |

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

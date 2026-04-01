# Criticality + Sparse Coding + Pragmatics

**Fields**: Complex Systems, Neuroscience, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T23:53:48.369601
**Report Generated**: 2026-03-31T16:21:16.502113

---

## Nous Analysis

**Algorithm**  
1. **Feature extraction (pragmatics‑guided sparse coding)** – For each prompt and each candidate answer, run a small set of regex patterns that capture:  
   - Negations (`not`, `n't`, `never`)  
   - Comparatives (`more … than`, `less … than`, `-er`)  
   - Conditionals (`if … then`, `unless`)  
   - Numeric values and units (`\d+(\.\d+)?\s*(kg|m|s|%)`)  
   - Causal cue‑words (`because`, `therefore`, `leads to`)  
   - Ordering relations (`before`, `after`, `first`, `last`)  

   Each matched pattern yields a proposition token (e.g., `NEG:not`, `COMP:more_than`, `NUM:5kg`). Tokens are hashed to a fixed index (mod M, M≈500) to build a **sparse binary feature matrix** `X ∈ {0,1}^{C×F}` where `C` is the number of candidates and `F` the feature vocabulary size.  

2. **Sparse coding step** – For each candidate row `x_c`, enforce sparsity by keeping only the top‑k (k=5) active features and zeroing the rest: `x̂_c = topk(x_c, k)`. This yields a matrix `Ŝ` that approximates the Olshausen‑Field energy `‖x - Wa‖² + λ‖a‖₀` with `W=I` and `a=x̂`.  

3. **Criticality scoring** – Treat each feature as a binary spin. Compute the **susceptibility** (variance of activation) across candidates:  
   ```
   χ = (1/F) * Σ_f Var(Ŝ[:,f])   # average variance over features
   ```  
   High χ indicates the system is near the order‑disorder boundary (criticality).  

4. **Pragmatic weighting** – Assign a weight `w_f` to each feature based on its pragmatic class (e.g., causal cues get weight 2.0, plain nouns 1.0, negations 1.5). Compute the final score for candidate *c*:  
   ```
   score_c = Σ_f w_f * Ŝ[c,f]  +  α * χ
   ```  
   where α balances sparsity‑pragmatics energy against criticality (α=0.5 works well in practice). The candidate with the highest score is selected.

**Structural features parsed** – negations, comparatives, conditionals, numeric values/units, causal claim markers, and temporal/ordering relations. These are the only linguistic constructs the regex set targets, ensuring the algorithm relies on explicit logical structure rather than shallow similarity.

**Novelty** – While sparse coding of language and criticality in neural networks have been studied separately, coupling them with a pragmatics‑derived feature‑weighting scheme and using susceptibility as a direct scoring term is not present in existing NLP evaluation tools. It bridges statistical‑physics motivated criticality, efficient sparse representations, and context‑sensitive meaning in a single, implementable pipeline.

**Ratings**  
Reasoning: 8/10 — The algorithm captures logical structure via regex, enforces sparse representations, and uses a principled statistical‑physics measure (susceptibility) to differentiate candidates, which aligns well with multi‑step reasoning.  
Metacognition: 6/10 — It provides a transparent internal statistic (χ) that can be monitored, but lacks explicit self‑reflection or uncertainty calibration beyond the variance term.  
Hypothesis generation: 5/10 — The method scores given candidates; it does not generate new hypotheses or expand the search space, limiting its generative capacity.  
Implementability: 9/10 — Only NumPy for array ops and Python’s `re` module are needed; all steps are straightforward loops or vectorized operations, making it easy to deploy without external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T16:17:54.956373

---

## Code

*No code was produced for this combination.*

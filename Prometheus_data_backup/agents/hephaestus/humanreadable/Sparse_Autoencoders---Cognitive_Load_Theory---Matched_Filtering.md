# Sparse Autoencoders + Cognitive Load Theory + Matched Filtering

**Fields**: Computer Science, Cognitive Science, Signal Processing
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T23:52:34.952091
**Report Generated**: 2026-04-02T04:20:11.597532

---

## Nous Analysis

**Algorithm**  
1. **Feature dictionary (sparse autoencoder)** – Offline, we learn a set of K binary pattern vectors \(D\in\{0,1\}^{K\times F}\) where each column \(f\) is a prototypical logical fragment (e.g., “X > Y”, “if A then B”, negation “not C”). Learning uses an ℓ₁‑penalized reconstruction loss so \(D\) is over‑complete and each text fragment maps to a sparse coefficient vector \(s\in\mathbb{R}^{K}\) with few non‑zeros.  
2. **Text parsing** – A prompt or candidate answer is scanned with a fixed regex library that extracts atomic propositions: comparatives, numeric thresholds, conditional antecedents/consequents, causal verbs (“causes”, “leads to”), ordering (“before”, “after”), and explicit negations. Each proposition is looked up in a hash table that maps its string to a column index in \(D\); the result is a binary indicator vector \(x\in\{0,1\}^{F}\).  
3. **Sparse coding step** – Solve \(\min_{s}\|x-Ds\|_{2}^{2}+\lambda\|s\|_{1}\) using a few iterations of ISTA (all numpy). The solution \(s\) is the sparse representation of the input.  
4. **Matched‑filter scoring** – For each candidate answer we compute its sparse vector \(s_{c}\). The detection statistic is the cross‑correlation (matched filter) \(r = s^{\top}Ds_{c}\). Because \(D\) is orthonormalized (via SVD) this reduces to \(r = \hat{s}^{\top}\hat{s}_{c}\) where \(\hat{s}=D^{T}s\) are the coefficients in the dictionary basis.  
5. **Cognitive‑load weighting** – Intrinsic load ≈ \(\|s\|_{0}\) (number of propositions). Extraneous load ≈ \(\|x-Ds\|_{2}^{2}\) (reconstruction error). Germane load ≈ \(r\). Final score:  
\[
\text{Score}= \frac{r}{\alpha\|s\|_{0}+\beta\|x-Ds\|_{2}^{2}+\epsilon}
\]  
with \(\alpha,\beta\) set to reflect working‑memory limits. Higher scores indicate answers that preserve the prompt’s logical structure while using few, germane features.

**Structural features parsed** – negations (“not”, “never”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), numeric values and thresholds, causal claims (“causes”, “leads to”), ordering relations (“before”, “after”, “precedes”), and conjunctive/disjunctive connectives.

**Novelty** – The combination is not a direct replica of prior work. Sparse coding has been used for feature learning, matched filtering for signal detection, and cognitive load for weighting, but fusing them into a single detection‑style scoring pipeline for textual reasoning is undocumented; the closest analogues are template‑matching with sparsity priors in computer vision or compressive‑sensing detection, none of which treat logical propositions as the signal.

**Ratings**  
Reasoning: 7/10 — captures logical structure via sparse dictionary and matched filter, but relies on hand‑crafted regex and linear scoring.  
Metacognition: 6/10 — explicit load terms mimic awareness of working‑memory limits, yet no higher‑order self‑regulation modeling.  
Hypothesis generation: 5/10 — the method scores existing candidates; it does not propose new answers.  
Implementability: 8/10 — all steps use numpy and stdlib; sparse coding via ISTA is straightforward, and regex parsing is lightweight.

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

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

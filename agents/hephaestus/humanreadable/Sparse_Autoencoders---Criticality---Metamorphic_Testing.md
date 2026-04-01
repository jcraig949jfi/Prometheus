# Sparse Autoencoders + Criticality + Metamorphic Testing

**Fields**: Computer Science, Complex Systems, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T08:24:09.201987
**Report Generated**: 2026-03-31T16:23:53.877779

---

## Nous Analysis

**Algorithm**  
1. **Dictionary learning (Sparse Autoencoder)** – Using only NumPy, run an iterative soft‑thresholding algorithm (ISTA) on a small corpus of reasoning sentences to learn a dictionary \(D\in\mathbb{R}^{m\times k}\) where each column corresponds to a logical primitive (negation, comparative, conditional, numeric magnitude, causal direction, ordering). The reconstruction loss is \(\|x-Da\|_2^2+\lambda\|a\|_1\); the sparse code \(a\) is the candidate answer’s representation.  
2. **Metamorphic‑test perturbations** – Define a set \(\mathcal{M}\) of MRs:  
   * M1: double any numeric token → expected code shift \(Δ_{M1}=D\beta_{num}\) (β learned from numeric examples).  
   * M2: swap two conjuncts in a conditional → expected shift \(Δ_{M2}=0\) (meaning‑preserving).  
   * M3: prepend “not” → expected shift \(Δ_{M3}=D\beta_{neg}\).  
   For each MR \(m\in\mathcal{M}\) generate a perturbed version of the input, encode it to obtain code \(a^{(m)}\), and compute the violation \(v_m=\|a^{(m)}-(a+Δ_m)\|_2\).  
3. **Criticality analysis** – Form the matrix \(A=[a, a^{(m_1)},…,a^{(m_{|\mathcal{M}|})}\in\mathbb{R}^{k\times (1+|\mathcal{M}|)}\). Compute the covariance \(C=\frac{1}{n}AA^T\) and its eigenvalues \(\{λ_i\}\). Fit a power‑law \(λ_i\propto i^{-α}\) via linear regression on log‑log scores; the distance to criticality is \(δ=|α-α_{crit}|\) with \(α_{crit}=1\) (1/f spectrum).  
4. **Scoring** – Sparsity \(s=\|a\|_0/k\). Final score for a candidate answer:  
\[
\text{Score}=s\;\exp(-δ)\;\Bigl(1-\frac{1}{|\mathcal{M}|}\sum_{m}v_m\Bigr)
\]  
Higher scores indicate answers that are (i) represented by few active logical primitives, (ii) lie near a critical point (maximal susceptibility to meaningful perturbations), and (iii) satisfy the metamorphic relations.

**Structural features parsed** – Negations, comparatives (more/less), conditionals (if‑then), numeric values and arithmetic relations, causal claims (because/therefore), ordering relations (before/after, greater/less).

**Novelty** – While sparse coding, criticality diagnostics, and metamorphic testing each appear separately in NLP, their joint use—using a learned logical dictionary to evaluate MR‑induced shifts and critical spectral scaling—has not been reported in existing work.

**Rating**  
Reasoning: 8/10 — The algorithm directly measures logical consistency via MR violations and sparsity, providing a principled, gradient‑free reasoning score.  
Metacognition: 6/10 — It offers a single scalar reflecting internal stability (criticality) but lacks explicit self‑reflection or uncertainty estimation.  
Hypothesis generation: 5/10 — The approach can suggest which MR caused high violation, but does not generate new hypotheses beyond error localization.  
Implementability: 9/10 — All steps rely on NumPy linear algebra and iterative thresholding; no external libraries or APIs are required.

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

**Forge Timestamp**: 2026-03-31T16:23:22.624563

---

## Code

*No code was produced for this combination.*

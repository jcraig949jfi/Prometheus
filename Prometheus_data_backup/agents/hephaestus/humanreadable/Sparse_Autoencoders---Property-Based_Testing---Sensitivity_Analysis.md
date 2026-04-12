# Sparse Autoencoders + Property-Based Testing + Sensitivity Analysis

**Fields**: Computer Science, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T18:27:13.424414
**Report Generated**: 2026-03-31T19:12:21.993304

---

## Nous Analysis

**Algorithm**  
We build a sparse‑dictionary encoder that maps any sentence to a binary feature vector *f* ∈ {0,1}^M, where each dictionary atom corresponds to a primitive logical construct (negation, comparative, conditional, causal link, numeric token, quantifier). The dictionary *D* ∈ ℝ^{M×V} (V = vocabulary size) is learned offline on a corpus of reasoning texts using an iterative hard‑thresholding version of the K‑SVD algorithm (only NumPy linalg ops).  

Given a reference answer R and a candidate answer C, we:  

1. **Encode** – compute sparse codes a_R, a_C by solving min‖x‖₀ s.t.‖Rx − d‖₂ ≤ τ with Orthogonal Matching Pursuit (OMP).  
2. **Perturb** – using Property‑Based Testing, generate a set P of perturbed versions of C by applying stochastic rewrite rules: swap synonyms, invert comparatives (>→<, ≥→≤), toggle negations, add/subtract a small ε to every numeric token, and flip causal direction. A shrinking phase keeps only those perturbations that change the reconstruction error the most, yielding a minimal failing set P_min.  
3. **Sensitivity** – for each feature i in the dictionary, compute a finite‑difference influence score:  
   Δ_i = (1/|P_min|) ∑_{p∈P_min} | recon_err(a_C, p) − recon_err(a_C + ε·e_i, p) |,  
   where recon_err =‖D·a − text_vec(p)‖₂² and e_i is the unit vector on atom i.  
4. **Score** – final merit S(C) = − (‖D·a_R − D·a_C‖₂² + λ·∑_i Δ_i), with λ balancing fidelity and robustness. Higher S means the candidate preserves the reference’s logical structure while being insensitive to small, meaning‑preserving perturbations.

**Structural features parsed** – negations, comparatives (≥, >, ≤, <), conditionals (if‑then), causal markers (because, leads to), numeric constants, ordering chains, quantifiers (all, some, none), and conjunctive/disjunctive connectives.

**Novelty** – Sparse autoencoders for logical feature extraction, property‑based testing for adversarial shrinking, and sensitivity analysis for influence measurement have each been used separately in NLP or verification, but their joint use to score reasoning answers is not documented in the literature; existing QA metrics rely on token overlap or neural similarity, not on explicit logical sparsity plus robustness‑driven influence weighting.

**Ratings**  
Reasoning: 7/10 — captures logical primitives via sparse codes and measures preservation under systematic perturbations.  
Metacognition: 5/10 — the method evaluates robustness but does not explicitly reason about its own confidence or error sources.  
Hypothesis generation: 6/10 — property‑based testing generates and shrinks perturbed hypotheses, though the space is limited to predefined rewrite rules.  
Implementability: 8/10 — all steps (dictionary learning via K‑SVD, OMP, NumPy array ops, simple loops for perturbations) run with only NumPy and the Python standard library.

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

- **Sparse Autoencoders**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 37% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Property-Based Testing**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Sensitivity Analysis**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Sensitivity Analysis + Sparse Autoencoders: negative interaction (-0.057). Keep these concepts in separate code paths to avoid interference.
- Property-Based Testing + Sensitivity Analysis: strong positive synergy (+0.489). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Free Energy Principle + Property-Based Testing + Sensitivity Analysis (accuracy: 0%, calibration: 0%)
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Free Energy Principle + Sensitivity Analysis (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:10:49.850481

---

## Code

*No code was produced for this combination.*

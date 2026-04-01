# Sparse Autoencoders + Dual Process Theory + Proof Theory

**Fields**: Computer Science, Cognitive Science, Mathematics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T02:47:07.364055
**Report Generated**: 2026-03-31T19:57:32.968433

---

## Nous Analysis

**Algorithm**  
We build a *Sparse Proof‑Net Scorer* (SPNS). Input: a prompt P and a set of candidate answers {A₁…A_k}.  
1. **Structural parsing** – Using regex‑based patterns we extract a set of atomic propositions 𝒫 from P and each A_i. Propositions are typed (e.g., `Neg(x)`, `Comp(x,y)`, `Cond(ante,cons)`, `NumEq(v)`, `Cause(e₁,e₂)`, `Ord(x<y)`). Each proposition is one‑hot encoded into a binary vector v∈{0,1}^d where d is the size of the proposition type vocabulary.  
2. **Dictionary learning (Sparse Autoencoder)** – We learn a dictionary D∈ℝ^{d×m} (m≫d) that reconstructs proposition vectors with an L1 sparsity penalty. Training uses only the prompt propositions 𝒫_P; the encoder yields a sparse code z = ReLU(Dᵀv) with hard‑thresholding to keep the top k non‑zeros (k≈5). The decoder reconstructs v̂ = Dz. Reconstruction error e = ‖v−v̂‖₂² measures how well a proposition set fits the learned “proof‑step” basis.  
3. **Dual‑process scoring** –  
   *System 1 (fast)*: compute a similarity score s₁ = cos(z_P, z_{A_i}) between the sparse codes of prompt and candidate.  
   *System 2 (slow)*: treat the non‑zero entries of z_{A_i} as active proof‑net nodes. Apply constraint propagation (transitivity of `Ord`, modus ponens for `Cond`, cancellation of double `Neg`) using numpy matrix operations to derive a closure C. If a contradiction (e.g., both `NumEq(5)` and `¬NumEq(5)`) appears, mark the candidate invalid (s₂=0); otherwise s₂=1.  
4. **Final score** S_i = α·(1−e_{A_i}) + β·s₁ + γ·s₂, with α+β+γ=1 (e.g., 0.4,0.3,0.3). Higher S indicates a better answer.

**Parsed structural features** – negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then …`), numeric values and equations, causal verbs (`because`, `leads to`), ordering relations (`before`, `after`, `precedes`).

**Novelty** – Sparse coding of logical forms has been explored in neural‑symbolic works (e.g., DSCL, Logic Tensor Networks). Dual‑process architectures appear in cognitive‑inspired AI (e.g., System 1/System 2 nets). Proof‑net based validation is used in linear logic reasoners. The novelty lies in tightly coupling a *learned sparse dictionary* of proof steps with *explicit constraint propagation* in a two‑stage scoring pipeline, a combination not reported in existing surveys.

**Ratings**  
Reasoning: 8/10 — captures both fast similarity and slow proof‑checked validity.  
Metacognition: 6/10 — system 2 provides a rudimentary self‑check, but no explicit monitoring of confidence.  
Hypothesis generation: 5/10 — generates candidate proofs via sparse codes, yet lacks exploratory search beyond top‑k activations.  
Implementability: 9/10 — relies only on regex, numpy linear algebra, and simple thresholding; no external libraries needed.

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

**Forge Timestamp**: 2026-03-31T19:57:01.598030

---

## Code

*No code was produced for this combination.*

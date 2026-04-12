# Sparse Autoencoders + Hebbian Learning + Metamorphic Testing

**Fields**: Computer Science, Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T17:54:56.720366
**Report Generated**: 2026-03-27T18:24:04.879839

---

## Nous Analysis

**Algorithm**  
We build a sparse‑code scorer that learns a dictionary of logical primitives from a small corpus of reasoned explanations using a Hebbian‑style update, then represents each candidate answer as a sparse vector over that dictionary. Metamorphic relations (MRs) are applied to the answer text; the scorer rewards reconstructions that are stable under those transformations and penalizes violations of extracted logical constraints.

1. **Dictionary learning (Hebbian + sparsity)**  
   - Tokenize each training sentence into a binary bag‑of‑words vector **x** ∈ {0,1}^V (V = vocab size).  
   - Initialize dictionary **D** ∈ ℝ^{V×K} (K ≫ V) with small random values.  
   - For each **x**, compute a sparse code **a** by one iteration of ISTA:  
     **a** ← S_{λ}( **a** + η **D**ᵀ(**x** − **D a**) ), where S_{λ} is soft‑thresholding (L1 sparsity).  
   - Update **D** with a Hebbian rule: **D** ← **D** + η (**x** − **D a**) **a**ᵀ, then renormalize columns.  
   - Repeat over the corpus; the result is a set of atoms that capture recurring logical patterns (e.g., “X > Y”, “if P then Q”, “not R”).

2. **Encoding a candidate answer**  
   - Convert answer text to the same binary vector **xₐ**.  
   - Compute its sparse code **aₐ** with ISTA (fixed T = 10 iterations).  
   - Reconstruction error: **E_rec** = ‖**xₐ** − **D aₐ**‖₂² (lower = better).

3. **Metamorphic consistency**  
   - Define a set of MRs as regex‑based transformations that preserve answer semantics:  
     *double negation* (¬¬P → P), *conditional swap* (if P then Q ↔ if ¬Q then ¬P), *ordering reversal* (A before B ↔ B after A).  
   - For each MR, apply it to the answer string → **xₐ′**, encode → **aₐ′**.  
   - Consistency penalty: **E_mr** = ∑‖**aₐ** − **aₐ′**‖₁ (sum over MRs). Small **E_mr** means the answer respects the relation.

4. **Constraint propagation**  
   - Extract atomic constraints via regex:  
     - Comparatives: “X > Y”, “X ≤ Y”.  
     - Ordering: “X before Y”, “X after Y”.  
     - Conditionals: “if X then Y”.  
     - Negations: “not X”.  
   - Build a directed graph; run transitive closure (Floyd‑Warshall on Boolean matrix) to infer implied relations.  
   - Count violated constraints (e.g., both X > Y and Y > X present). Penalty **E_c** = #violations.

5. **Final score**  
   **Score** = − **E_rec** − λ₁ **E_mr** − λ₂ **E_c** (λ₁, λ₂ = 0.5 tuned on a validation set). Higher scores indicate answers that are well‑reconstructed, stable under MRs, and logically consistent.

**Structural features parsed**  
Numerical values, comparatives (> , < , ≥ , ≤ , =), ordering terms (before, after, first, last), negations (not, no, never), conditionals (if … then …, unless), causal markers (because, leads to, therefore), conjunctive/disjunctive connectors (and, or, but).

**Novelty**  
Sparse autoencoders with Hebbian‑style dictionary updates are established in unsupervised feature learning (Olshausen & Field, 1996; sparse autoencoders, 2011). Metamorphic testing is well‑known in software engineering but has not been applied to NLP answer scoring. The specific fusion—learning a logical primitive dictionary via Hebbian sparsity, then scoring answers by reconstruction error, MR stability, and constraint‑violation penalties—does not appear in existing literature, making the combination novel.

**Ratings**  
Reasoning: 7/10 — The algorithm captures logical structure via sparse codes and MR consistency, offering a principled way to reward correct reasoning while penalizing contradictions.  
Metacognition: 5/10 — It lacks explicit self‑monitoring or confidence estimation; scores are purely reconstruction‑based.  
Hypothesis generation: 6/10 — By generating transformed answers under MRs, it implicitly creates alternative hypotheses, but does not rank or select among them.  
Implementability: 8/10 — All steps use only NumPy (matrix ops, soft‑thresholding, Floyd‑Warshall) and Python’s re module; no external libraries or APIs are required.

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

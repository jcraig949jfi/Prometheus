# Sparse Autoencoders + Free Energy Principle + Compositional Semantics

**Fields**: Computer Science, Theoretical Neuroscience, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T15:12:02.549712
**Report Generated**: 2026-03-31T16:21:16.547113

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Proposition Extraction** – Using regex we extract atomic propositions (e.g., “X is Y”, “X > Y”, “if X then Y”) and label each with a type token (negation, comparative, conditional, causal, numeric, quantifier). Each proposition is turned into a one‑hot vector **v** over a fixed vocabulary of lexical stems (size V).  
2. **Sparse Dictionary Learning (offline)** – From a large corpus we learn a dictionary **D** ∈ ℝ^{V×K} (K ≪ V) with an L1 sparsity penalty via iterative orthogonal matching pursuit (OMP). The dictionary columns are normalized; the learned **D** captures reusable semantic features (e.g., “agent‑action”, “quantity‑compare”).  
3. **Compositional Encoding** – For each proposition we compute a sparse code **α** = OMP(**v**, D, τ) where τ sets the maximum number of non‑zero entries. Complex propositions are built recursively:  
   - Negation: **α_not** = **W_neg**·**α** (learned diagonal matrix flipping sign of relevant features).  
   - Comparative: **α_comp** = **α_subj** – **α_obj** (vector subtraction).  
   - Conditional: **α_cond** = **W_then**·**α_then** + **W_if**·**α_if** (learned linear maps).  
   - Causal: similar additive composition with a causal weight matrix.  
   The result is a sparse representation **α_q** for the question and **α_a** for each candidate answer.  
4. **Free‑Energy Scoring** – Variational free energy for a candidate is approximated as  
   \[
   F = \frac{1}{2}\| \mathbf{v}_q - D\boldsymbol{\alpha}_a \|_2^2 + \lambda\|\boldsymbol{\alpha}_a\|_1,
   \]  
   where the first term is prediction error (how well the answer’s sparse code reconstructs the question’s observation) and the second term enforces sparsity (the “complexity” cost). Lower F → higher plausibility. The score returned is **S = –F** (higher is better). All operations use only NumPy for linear algebra and the Python standard library for regex and OMP.

**Structural Features Parsed** – Negations (“not”, “no”), comparatives (“greater than”, “less than”, “equals”), conditionals (“if … then …”), causal claims (“because”, “leads to”), numeric values and units, ordering relations (“first”, “before”, “after”), quantifiers (“all”, “some”, “none”), and conjunction/disjunction cues.

**Novelty** – While sparse coding and predictive‑coding (free energy) have been studied separately in neuroscience and ML, their direct combination as a deterministic scoring engine for QA — using learned dictionary bases, explicit compositional operators, and a variational free‑energy loss — has not been reported in the literature. Existing work either uses neural similarity or pure logical theorem provers; this hybrid sits between them.

**Ratings**  
Reasoning: 7/10 — captures logical structure and prediction error but relies on linear approximations.  
Metacognition: 5/10 — no explicit self‑monitoring of confidence beyond the free‑energy magnitude.  
Hypothesis generation: 6/10 — can propose alternative parses via different sparse codes, but search is limited to OMP sparsity level.  
Implementability: 8/10 — only NumPy and stdlib; dictionary learning and OMP are straightforward to code.

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

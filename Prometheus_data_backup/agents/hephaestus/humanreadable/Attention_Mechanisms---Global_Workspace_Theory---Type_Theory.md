# Attention Mechanisms + Global Workspace Theory + Type Theory

**Fields**: Computer Science, Cognitive Science, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T02:58:47.991135
**Report Generated**: 2026-04-01T20:30:43.487121

---

## Nous Analysis

**Algorithm**  
1. **Parsing → Typed Proposition List**  
   - Use regex to extract elementary clauses:  
     *Negation* (`not`), *Comparative* (`>`, `<`, `=`), *Conditional* (`if … then …`), *Causal* (`because`, `leads to`), *Numeric* (`[0-9]+(\.[0-9]+)?`), *Ordering* (`before`, `after`, `greater than`, `less than`), *Quantifier* (`all`, `some`, `none`).  
   - Each clause becomes a proposition `p_i = (type, subj, pred, obj, mods)`.  
   - `type` is one-hot encoded (≈10 dimensions). Lexical tokens of `subj`, `pred`, `obj` are hashed with a fixed‑size char‑n‑gram function into a 50‑dim vector (numpy only). The final proposition vector `v_i = concat(type_onehot, lexical_vec)` → shape (60,).  
   - Store all propositions of the question in matrix **Q** (n_q × 60) and of a candidate answer in **C** (n_c × 60).

2. **Attention Weighting (Multi‑Head Self/Cross Attention)**  
   - For each head `h` (h=4, dim_k=15):  
     `Q_h = Q W_q^h`, `K_h = C W_k^h`, `V_h = C W_v^h` where `W` are random orthogonal numpy matrices (fixed seed).  
     Compute scaled dot‑product: `A_h = softmax(Q_h K_h^T / sqrt(dim_k))`.  
     Output per head: `O_h = A_h V_h`.  
   - Concatenate heads → **R** (n_q × 60) = relevance‑weighted question representation for each candidate proposition.

3. **Global Workspace Ignition & Constraint Propagation**  
   - Ignition: select top‑k (k=3) rows of **R** with highest max‑attention score → workspace matrix **W** (k × 60).  
   - Broadcast: compute workspace centroid `c = mean(W, axis=0)`.  
   - Constraint propagation (single iteration, numpy only):  
     *Transitivity* for ordering: if `p_a` says `x > y` and `p_b` says `y > z` then infer `x > z` (add vector for inferred proposition).  
     *Modus Ponens* for conditionals: if `p_a` is `if A then B` and `p_b` asserts `A` then add `B`.  
     *Numeric*: evaluate simple arithmetic expressions (`+`, `-`, `*`, `/`) using extracted numbers.  
   - After propagation, recompute centroid `c'`.

4. **Scoring**  
   - Score = cosine similarity between `c'` and the question centroid `c_q = mean(Q, axis=0)`.  
   - Penalty = 0.1 × number of violated constraints (e.g., a comparative that contradicts propagated ordering).  
   - Final score = similarity – penalty (clipped to [0,1]).

**Structural Features Parsed**  
Negations, comparatives, conditionals, causal cues, numeric values & units, ordering/temporal relations, quantifiers, equality statements.

**Novelty**  
Purely symbolic attention over typed propositions combined with a global workspace broadcasting step is not present in existing surveys; prior work treats attention as a neural similarity metric or uses separate symbolic reasoners, but not the integrated attention‑workspace‑type‑theory loop described.

**Rating**  
Reasoning: 7/10 — captures logical structure and propagates inferences, but limited to shallow, rule‑based constraints.  
Metacognition: 5/10 — workspace provides a global broadcast analogy, yet no explicit self‑monitoring of confidence.  
Hypothesis generation: 4/10 — can propose inferred propositions via modus ponens/transitivity, but lacks exploratory search.  
Implementability: 8/10 — relies only on regex, numpy linear algebra, and fixed random matrices; no external libraries or training needed.

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

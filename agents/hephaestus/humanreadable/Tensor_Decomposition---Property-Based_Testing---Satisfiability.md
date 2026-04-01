# Tensor Decomposition + Property-Based Testing + Satisfiability

**Fields**: Mathematics, Software Engineering, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T03:11:18.358123
**Report Generated**: 2026-03-31T18:00:36.920322

---

## Nous Analysis

**Algorithm – Tensor‑Decomposed Constraint Score (TDCS)**  

1. **Parsing & Encoding**  
   - From each candidate answer we extract a set of atomic propositions \(P=\{p_1,…,p_m\}\) using regex patterns for negations, comparatives, conditionals, numeric thresholds, causal verbs (“causes”, “leads to”), and ordering relations (“before”, “greater than”).  
   - Each atomic proposition becomes a Boolean variable. Numeric literals are turned into linear constraints (e.g., \(x>5\)).  
   - A reference answer (or a set of gold‑standard statements) is encoded the same way, yielding a target constraint set \(C^{\*}\).

2. **Constraint Tensor Construction**  
   - Build a third‑order binary tensor \(\mathcal{T}\in\{0,1\}^{N\times M\times K}\) where  
     * mode 1 \(N\) = number of candidate answers,  
     * mode 2 \(M\) = distinct atomic propositions across all candidates,  
     * mode 3 \(K\) = distinct constraint types (equality, inequality, implication, conjunction).  
   - Entry \(\mathcal{T}_{i,j,k}=1\) iff candidate \(i\) contains proposition \(j\) participating in constraint type \(k\); otherwise 0.  
   - The same tensor is built for the reference set, yielding \(\mathcal{T}^{\*}\).

3. **Tensor Decomposition (CP)**  
   - Apply CANDECOMP/PARAFAC decomposition (alternating least squares using only NumPy) to both tensors, obtaining factor matrices \(A,B,C\) and \(A^{\*},B^{\*},C^{\*}\) with rank \(R\) (chosen via explained variance > 90%).  
   - The reconstruction error \(E = \|\mathcal{T}-\hat{\mathcal{T}}\|_F^2 / \|\mathcal{T}\|_F^2\) measures how well the candidate’s logical structure aligns with the latent space learned from all answers.

4. **Property‑Based Testing & Shrinking**  
   - Treat the Boolean variables as inputs to a property: “the candidate’s constraints are jointly satisfiable with the reference constraints”.  
   - Using Hypothesis‑style random generation (pure Python `random.getrandbits`) we sample assignments to the variables, evaluate the combined constraint set (unit‑propagation SAT solver written with NumPy arrays), and record failing assignments.  
   - A shrinking loop repeatedly flips bits to reduce the Hamming weight of the failing assignment, yielding a minimal failing input (MFI).  
   - Let \(s\) be the size of the MFI (number of variables that must change to regain satisfiability); smaller \(s\) indicates higher compatibility.

5. **Scoring Logic**  
   \[
   \text{Score}_i = \underbrace{(1-E_i)}_{\text{structural fit}} \times \underbrace{\left(1-\frac{s_i}{|P|}\right)}_{\text{constraint compatibility}}
   \]
   Scores lie in \([0,1]\); higher values mean the candidate’s logical and numeric structure closely matches the reference while requiring few changes to become jointly satisfiable.

**Structural Features Parsed**  
Negations (`not`, `no`), comparatives (`greater than`, `less than`, `≥`, `≤`), conditionals (`if … then …`, `implies`), numeric values and thresholds, causal claims (`causes`, `leads to`, `results in`), ordering relations (`before`, `after`, `precedes`, `greater than`).

**Novelty**  
Combining CP tensor decomposition with property‑based testing and a lightweight SAT solver for answer scoring is not present in mainstream educational‑assessment tools. Prior work uses either tensor methods for semantic embeddings or SAT‑based consistency checks, but not the joint decomposition‑testing‑shrinking loop that directly yields a numeric compatibility score from raw logical structure.

**Ratings**  
Reasoning: 8/10 — The algorithm captures multi‑way logical interactions and quantifies satisfaction via SAT, offering deeper reasoning than surface similarity.  
Metacognition: 6/10 — It provides error and mismatch signals but does not explicitly monitor its own confidence or adapt rank dynamically.  
Hypothesis generation: 7/10 — Property‑based testing actively generates candidate falsifying assignments and shrinks them, a strong hypothesis‑driven search.  
Implementability: 9/10 — All components (regex parsing, NumPy‑based ALS for CP, unit‑propagation SAT, random bit sampling) rely solely on NumPy and the Python standard library.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

*No Coeus enrichment available for this combination.*

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T17:59:49.619589

---

## Code

*No code was produced for this combination.*

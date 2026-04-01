# Cognitive Load Theory + Type Theory + Proof Theory

**Fields**: Cognitive Science, Logic, Mathematics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:50:48.034830
**Report Generated**: 2026-03-31T14:34:57.380072

---

## Nous Analysis

**Algorithm**  
1. **Parsing & Typing** – Use regex to extract atomic propositions of the form `¬P`, `P ∧ Q`, `P → Q`, `P ∨ Q`, `X > Y`, `X = Y`, and causal clauses `X causes Y`. Each token is assigned a simple type from a finite set: `Entity`, `Number`, `Bool`. A proposition `P(t1,…,tn)` gets the function type `τ1 → … → τn → Bool` where each `τi` is the type of its argument. Store propositions in a list `props` and their types in a parallel NumPy array `typed` of shape `(m,)` where `m` is the number of propositions; each entry is an integer encoding the type tuple (using a predefined hash).  
2. **Well‑Typed Filter** – Compute a Boolean mask `well = np.all(typed == expected_type, axis=1)` where `expected_type` is the type signature derived from the predicate symbol table. Discard any candidate answer that fails this mask (extraneous load).  
3. **Horn Clause Construction** – For each conditional `A → B` generate a Horn clause `(A) ⇒ B`. Collect all clauses in a list `clauses`. Build a binary adjacency matrix `C` of shape `(m,m)` where `C[i,j]=1` if the head of clause `i` unifies with the body of clause `j` (unification reduces to type equality and constant matching, both O(1) with NumPy equality).  
4. **Proof Normalization via Cut Elimination** – Compute the transitive closure of `C` with repeated squaring (`np.linalg.matrix_power`) to obtain `C*`, which encodes all derivable implications without explicit cut steps. The length of a normalized proof for a target proposition `p` is the smallest `k` such that `(C*)^k[p, goal] > 0`. This is found by iterating powers until convergence, counting the iteration at which the goal becomes reachable.  
5. **Scoring** –  
   - **Intrinsic load** = proof length `k` (shorter = better).  
   - **Extraneous load** = number of propositions in the candidate that were filtered out by the well‑Typed mask.  
   - **Germane load** = number of distinct intermediate propositions used in the proof (non‑zero entries in the proof path).  
   Final score = `-(α·k + β·extraneous) + γ·germane`, with fixed weights `α=1.0, β=2.0, γ=0.5`. Lower (more negative) scores indicate higher quality reasoning.

**Structural Features Parsed**  
Negations (`not`, `¬`), comparatives (`>`, `<`, `≥`, `≤`, `=`), conditionals (`if … then …`, `→`), disjunctions (`or`), causal verbs (`causes`, `leads to`), ordering relations (`before`, `after`), and numeric literals. These are captured directly by the regex patterns that produce the atomic propositions used above.

**Novelty**  
The combination is not a direct replica of existing systems. While type checking and Horn‑clause resolution are standard in proof assistants, coupling them with a cognitive‑load‑based penalty/extraneous‑reward metric and using NumPy‑based matrix powers for cut‑elimination yields a novel, lightweight scoring pipeline that operates purely on symbolic structure without neural components.

**Rating**  
Reasoning: 8/10 — The algorithm captures deductive depth and relevance via proof length and extraneous filtering, aligning well with multi‑step reasoning tasks.  
Metacognition: 6/10 — It estimates workload (intrinsic/extraneous/germane) but lacks explicit self‑monitoring of strategy shifts.  
Hypothesis generation: 5/10 — The system evaluates given hypotheses; it does not propose new ones beyond what is present in the input.  
Implementability: 9/10 — All steps use only regex, NumPy array operations, and basic Python control flow, making it straightforward to code and run without external dependencies.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

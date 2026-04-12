# Cognitive Load Theory + Compositionality + Sensitivity Analysis

**Fields**: Cognitive Science, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T11:02:40.990214
**Report Generated**: 2026-03-31T17:18:34.424820

---

## Nous Analysis

**Algorithm**  
1. **Parse → Symbolic Graph** – Tokenize the prompt and each candidate answer with regexes that capture:  
   - literals (numbers, proper nouns)  
   - predicates (verbs, adjectives)  
   - logical operators (¬, ∧, ∨, →)  
   - relational tokens (comparatives, ordering, causality, negation)  
   Build a directed acyclic graph *G* where nodes are atomic propositions and edges are labeled with the operator that combines them (compositionality). Each node stores its intrinsic chunk size (1) and its depth in the graph (working‑memory load).  

2. **Load Computation** – For each candidate:  
   - *Intrinsic load* = Σ depth(node) (sum of dependency depths).  
   - *Extraneous load* = count of tokens that do not map to any node (e.g., filler words).  
   - *Germane load* = number of edges that satisfy a valid inference rule (modus ponens, transitivity, contrapositive) identified by a forward‑chaining pass over *G*.  
   Cognitive‑load score = –(α·intrinsic + β·extraneous – γ·germane) (higher is better).  

3. **Compositional Meaning** – Assign each primitive node a vector embedding from a fixed lookup table (e.g., one‑hot for predicates, scaled numeric for numbers). Propagate meaning upward using simple combination rules:  
   - ¬v = 1 – v  
   - v₁ ∧ v₂ = min(v₁, v₂)  
   - v₁ ∨ v₂ = max(v₁, v₂)  
   - v₁ → v₂ = max(1‑v₁, v₂)  
   The root vector *R* is the candidate’s semantic representation.  

4. **Sensitivity Analysis** – Generate *k* perturbed copies of the prompt by randomly:  
   - flipping the sign of a numeric literal (±10%)  
   - toggling a negation or swapping ∧/∨  
   Re‑parse each copy, recompute *R*, and calculate the Euclidean distance ‖R – R₀‖₂. Sensitivity score = –std(distances) (lower variance → higher robustness).  

5. **Final Score** = w₁·(cosine similarity between candidate *R* and prompt *R*) + w₂·cognitive‑load score + w₃·sensitivity score, with weights summing to 1. All operations use only Python’s `re`, `collections`, and `numpy`.

**Structural Features Parsed**  
Negations, comparatives (`>`, `<`, `=`), conditionals (`if…then`), causal markers (`because`, `leads to`), ordering relations (`first`, `before`), numeric values, and conjunctive/disjunctive connectives.

**Novelty**  
While cognitive‑load metrics, compositional semantic parsers, and sensitivity analysis each appear separately in NLP and ML literature, their joint use to evaluate reasoning answers — specifically combining load‑based penalties with compositional vector propagation and perturbation‑based robustness — has not been reported in existing work.

**Rating**  
Reasoning: 8/10 — captures logical structure and consistency via explicit graph propagation.  
Metacognition: 7/10 — load terms approximate working‑memory constraints but lack learner‑state modeling.  
Hypothesis generation: 6/10 — robustness check hints at alternative interpretations but does not actively generate new hypotheses.  
Implementability: 9/10 — relies solely on regex, numpy arithmetic, and simple graph algorithms; no external libraries needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
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

**Forge Timestamp**: 2026-03-31T17:17:05.368209

---

## Code

*No code was produced for this combination.*

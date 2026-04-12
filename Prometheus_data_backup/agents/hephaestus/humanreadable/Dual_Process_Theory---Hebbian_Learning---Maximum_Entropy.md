# Dual Process Theory + Hebbian Learning + Maximum Entropy

**Fields**: Cognitive Science, Neuroscience, Statistical Physics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T06:34:41.908506
**Report Generated**: 2026-04-01T20:30:43.655121

---

## Nous Analysis

**Algorithm**  
We build a hybrid scorer that alternates between a fast, Hebbian‑based similarity pass (System 1) and a slow, constraint‑propagation pass that enforces maximum‑entropy consistency (System 2).  

1. **Feature extraction** – Using only the standard library we parse each prompt and candidate answer into a sparse feature vector *f* ∈ ℝᴰ. Dimensions capture:  
   - token presence (lower‑cased words)  
   - negated tokens (prefixed “not_”)  
   - comparative/superlative markers (“more_”, “most_”, “less_”, “least_”)  
   - conditional antecedent/consequent flags (“if_”, “then_”)  
   - numeric constants (scaled to [0,1])  
   - causal cue pairs (“cause_→_effect”)  
   - ordering symbols (“<”, “>”, “≤”, “≥”)  

   Vectors are stored as `numpy.ndarray` of shape (N_candidates, D).  

2. **Hebbian weight matrix** – From a small development set we compute co‑occurrence counts *C* = FᵀF (numpy dot product). The weight matrix *W* = log(1 + *C*) implements activity‑dependent strengthening; higher *W* means two features frequently appear together in correct answers.  

3. **System 1 scoring** – Base score *s₀* = F · W · 1ᵀ (vector‑matrix‑vector product) gives a fast heuristic affinity of each answer to the learned answer pattern.  

4. **System 2 constraint propagation** – We formulate linear constraints *Ax = b* derived from parsed structure:  
   - transitivity of ordering (“A < B ∧ B < C → A < C”)  
   - modus ponens for conditionals (“if P then Q” ∧ P → Q)  
   - numeric equality/inequality  
   - negation flipping sign of a feature.  

   We seek a score vector *s* that maximizes entropy *H(s) = −∑ sᵢ log sᵢ* subject to *Ax = b* and *s₀* as a prior mean. Using numpy we solve the dual via iterative scaling (Generalized Iterative Scaling), yielding the maximum‑entropy distribution *s* that respects all logical constraints while staying close to the Hebbian heuristic.  

5. **Final score** – The normalized *s* is returned as the answer rating.  

**Structural features parsed** – negations, comparatives, conditionals, numeric values, causal claims, ordering relations (including transitive chains).  

**Novelty** – While each component (Hebbian weighting, constraint satisfaction, MaxEnt) exists separately, their tight coupling—using Hebbian co‑occurrence as the prior in a MaxEnt‑constrained inference loop—has not been reported in public reasoning‑evaluation tools.  

Reasoning: 7/10 — captures logical structure and learns from data, but relies on linear constraints that may miss deeper abstractions.  
Metacognition: 6/10 — System 2 provides a deliberate check, yet the model lacks explicit self‑monitoring of its own uncertainty.  
Hypothesis generation: 5/10 — heuristic generation is limited to feature co‑occurrence; novel hypothesis synthesis is weak.  
Implementability: 8/10 — all steps use only NumPy and the Python standard library; no external APIs or neural nets required.

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

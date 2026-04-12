# Dual Process Theory + Free Energy Principle + Property-Based Testing

**Fields**: Cognitive Science, Theoretical Neuroscience, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:26:52.720584
**Report Generated**: 2026-03-31T16:29:10.726365

---

## Nous Analysis

The algorithm treats a prompt as a set of logical constraints extracted via regex‑based pattern matching (negations, comparatives, conditionals, causal cues, numeric thresholds, ordering). Each constraint is stored as a Horn clause Cᵢ: body → head, encoded in a binary matrix A (shape m × n) where rows are clauses and columns are propositional atoms; a weight vector w (given by cue strength) quantifies importance. A candidate answer is parsed into an atom truth vector x ∈ {0,1}ⁿ.  

**Fast (System 1) score:** compute the variational free‑energy approximation F = ∑ᵢ wᵢ · max(0, bodyᵢ·x − headᵢ·x). This is the sum of weighted prediction errors (unsatisfied clause bodies without heads). The initial heuristic score S₀ = 1/(1+F).  

**Slow (System 2) refinement:** invoke property‑based testing to generate perturbations δ of the answer (token swaps, insertions, deletions) using a shrinking strategy that binary‑searches edit distance while re‑evaluating F. The minimal perturbation δ* that yields the lowest F defines the refined score S = 1/(1+F_min). Numpy handles matrix‑vector products for F computation; the shrinking loop uses only random.choice and list slicing from the stdlib.  

**Parsed structural features:** negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”, “unless”), causal verbs (“because”, “leads to”, “results in”), numeric values with thresholds, ordering relations (“before”, “after”, “more than”), and conjunctive/disjunctive connectives.  

**Novelty:** While each concept exists separately, their conjunction — using property‑based testing to search for minimal‑error answer variants under a free‑energy‑derived logical loss, guided by dual‑process timing — has not been reported in the literature. Existing tools either rely on similarity metrics or pure rule chaining; this hybrid adds a stochastic shrinking phase that explicitly seeks the simplest correction to satisfy extracted constraints.  

Reasoning: 7/10 — captures logical consistency but depends on accurate regex extraction.  
Metacognition: 6/10 — dual‑process split is heuristic; no explicit self‑monitoring of search depth.  
Hypothesis generation: 8/10 — property‑based testing systematically proposes and shrinks answer variants.  
Implementability: 9/10 — all operations are numpy matrix ops and stdlib loops; no external dependencies.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 8/10 |
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

**Forge Timestamp**: 2026-03-31T16:28:14.184370

---

## Code

*No code was produced for this combination.*

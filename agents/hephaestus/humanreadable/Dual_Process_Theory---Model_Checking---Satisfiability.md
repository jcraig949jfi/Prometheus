# Dual Process Theory + Model Checking + Satisfiability

**Fields**: Cognitive Science, Formal Methods, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:26:47.776350
**Report Generated**: 2026-03-27T16:08:16.433670

---

## Nous Analysis

The algorithm treats a prompt and each candidate answer as a set of logical constraints that must be jointly satisfiable. First, a fast System 1 pass extracts surface features with regular expressions: atomic propositions (e.g., “the cat is on the mat”), comparatives (“>”, “<”), numeric equalities, negations (“not”), conditionals (“if … then …”), causal cues (“because”, “leads to”), and temporal ordering (“before”, “after”). Each extracted element becomes a literal Lᵢ. Negations produce ¬Lᵢ; comparatives generate arithmetic constraints (e.g., x > 5) stored as linear inequality tuples; conditionals yield implication clauses Lₐ → L_b (converted to ¬Lₐ ∨ L_b); causal cues are modeled as bidirectional implications when justified, otherwise as Lₐ → L_b with a confidence weight.

These literals and clauses form a CNF clause set C and a constraint store S (inequalities). System 2 then performs a lightweight model‑checking pass: it builds a state‑transition graph where each state assigns truth values to a subset of literals; edges correspond to flipping a literal consistent with S. A breadth‑first search explores states up to a depth bound (e.g., 6) checking whether any reachable state satisfies all clauses in C (unit propagation with conflict‑driven clause learning simplified to pure Python). If a satisfying state is found, the candidate receives a logical consistency score Sₗ = 1 − (d / D) where d is the depth at which satisfaction was first seen and D the max depth; otherwise Sₗ = 0.

The System 1 heuristic score Sₕ is a weighted sum of matched features (e.g., 0.2 per correct negation, 0.15 per correct numeric relation, 0.1 per correct causal cue). The final answer score is α·Sₕ + (1‑α)·Sₗ with α = 0.4, giving priority to deliberate verification while retaining fast intuition.

**Structural features parsed:** negations, comparatives, numeric equalities/inequalities, conditionals, causal connectives, temporal ordering (before/after), conjunction/disjunction, and quantifier‑free predicates.

This triple‑blend is not found in existing answer‑scoring tools; prior work uses either SAT‑based consistency checking or model‑checking of temporal specs, but never couples them with a Dual‑Process‑style fast/slow weighting scheme.

Reasoning: 8/10 — captures logical consistency and heuristic intuition, improving over pure similarity baselines.  
Metacognition: 7/10 — the α weighting provides a rudimentary self‑assessment of when to trust fast vs. slow scores, though limited to a fixed scalar.  
Hypothesis generation: 6/10 — the search can propose alternative truth assignments, but does not generate novel explanatory hypotheses beyond constraint satisfaction.  
Implementability: 9/10 — relies only on regex, basic data structures, unit propagation, and BFS; all feasible with numpy (for numeric checks) and the Python standard library.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

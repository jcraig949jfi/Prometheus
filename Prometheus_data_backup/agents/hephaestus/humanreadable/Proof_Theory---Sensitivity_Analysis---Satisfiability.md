# Proof Theory + Sensitivity Analysis + Satisfiability

**Fields**: Mathematics, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T11:29:42.312312
**Report Generated**: 2026-04-01T20:30:43.905114

---

## Nous Analysis

The algorithm builds a lightweight SMT‑style constraint system from the premise text and each candidate answer, then uses proof‑theoretic normalization (cut‑elimination) to simplify the clause set, and finally applies sensitivity analysis to quantify how much the numeric components must shift for the answer to become satisfiable.  

**Data structures** – Each parsed sentence yields a set of literals stored as Python tuples. A literal is either a Boolean atom (e.g., `Rain`) or a numeric comparison (`x ≥ 5`) represented by a coefficient vector `c` and a threshold `t` (`c·x ⊗ t`). The whole knowledge base is a list of clauses, where a clause is a list of literals (disjunction). Unit clauses are kept separately for fast propagation.  

**Operations** – 1) **Parsing** extracts atoms, negations, comparatives, conditionals (`if A then B` → clause `¬A ∨ B`), causal claims (treated as conditionals), and ordering chains (transitivity encoded as `A ≤ B ∧ B ≤ C → A ≤ C`). 2) **Proof normalization** applies unit propagation and resolution (cut elimination) iteratively, removing redundant literals and producing a simplified clause set in conjunctive normal form. 3) **Satisfiability check** uses a basic DPLL back‑track solver (pure Python) with numpy arrays for fast vector‑dot evaluations of numeric literals. 4) **Sensitivity analysis** computes, for each numeric literal, the minimal L1 perturbation `δ` needed to flip its truth value (interval arithmetic on the coefficient vector). The overall perturbation for a candidate answer is the sum of `δ` over all literals that are falsified in the current model; if the answer is already satisfiable, perturbation = 0.  

**Scoring** – Score = `1 / (1 + perturbation)`. Higher scores indicate answers that require smaller changes to become consistent with the premises, rewarding logical coherence and robustness.  

**Structural features parsed** – negations, comparatives (`>`, `<`, `=`), conditionals, causal implications, ordering/transitive chains, and explicit numeric thresholds.  

**Novelty** – While proof‑theoretic normalization and SAT solving are classic, coupling them with a sensitivity‑driven perturbation score for textual reasoning is uncommon in NLP evaluation; it resembles differentiable SAT (NeuroSAT) and probabilistic soft logic but stays fully symbolic and uses only numpy/stdlib.  

Reasoning: 8/10 — strong deductive grounding but limited handling of vague or probabilistic language.  
Metacognition: 5/10 — no explicit self‑monitoring of proof search depth or strategy shifts.  
Hypothesis generation: 6/10 — can produce minimal unsatisfiable cores as counter‑examples, but not creative abductive hypotheses.  
Implementability: 9/10 — relies solely on numpy for vector ops and stdlib for parsing/search, making it readily portable.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
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

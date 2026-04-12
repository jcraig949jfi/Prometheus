# Cognitive Load Theory + Property-Based Testing + Sensitivity Analysis

**Fields**: Cognitive Science, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T01:02:03.515120
**Report Generated**: 2026-03-31T19:57:32.908440

---

## Nous Analysis

The algorithm builds a lightweight symbolic‑numeric evaluator that treats each candidate answer as a set of logical propositions extracted from the text. First, a deterministic parser (regex‑based) produces a directed acyclic graph (DAG) where nodes are atomic propositions (e.g., “X > Y”, “¬P”, “cause(A,B)”) and edges represent explicit relations (comparatives, conditionals, causal links). Each node stores its type and any numeric constants.  

From Cognitive Load Theory we compute an intrinsic load score Lᵢ for the answer: Lᵢ = α·|V| + β·|E| + γ·Σ cᵢ, where |V| and |E| are node and edge counts, and cᵢ is the cardinality of any chunk (e.g., a conjunctive clause) identified by maximal strongly‑connected sub‑graphs after ignoring direction. Extraneous load is approximated by the number of negation and modal operators; germane load is the proportion of nodes that participate in a derivable chain (via forward chaining).  

Property‑Based Testing supplies a generator that, given the DAG, creates perturbations: (1) flip truth value of a randomly selected literal, (2) add/subtract ε to a numeric constant, (3) replace a comparative with its opposite, (4) insert or delete a causal edge. The generator uses a shrinking strategy: after a failing perturbation is found, it repeatedly attempts to halve ε or remove a literal to reach a minimal failing set.  

Sensitivity Analysis quantifies how the answer’s score changes under these perturbations. For each perturbation p we compute ΔS(p) = |S(original) − S(p)|, where S is a deterministic scoring function that rewards satisfied constraints (modus ponens, transitivity) and penalizes violations. The final answer score is  

Score = (1 − λ·Lᵢ/ Lₘₐₓ) · (1 − μ·meanₚΔS(p)/ΔSₘₐₓ),  

with λ,μ∈[0,1] weighting load and sensitivity; Lₘₐₓ and ΔSₘₐₓ are normalising constants derived from a calibration set.  

The parser extracts: negations (“not”, “no”), comparatives (“greater than”, “less than”), conditionals (“if … then …”), numeric values, causal claims (“causes”, “leads to”), and ordering relations (“before”, “after”, “precedes”).  

**Novelty.** Property‑based testing and sensitivity analysis are well‑studied in software verification and causal inference, while cognitive load metrics appear in educational tech. Combining them to drive a text‑scoring engine that simultaneously measures structural complexity, robustness to minimal perturbations, and working‑memory load has not, to my knowledge, been published; the closest analogues are automated essay scoring with rubric‑based constraints, but they lack the systematic shrinking‑based perturbation loop.  

Reasoning: 7/10 — The method captures logical consistency and numeric sensitivity, but relies on hand‑crafted parsers that may miss nuanced linguistic phenomena.  
Metacognition: 6/10 — Load estimation approximates working‑memory demand yet omits learner‑specific factors like prior knowledge.  
Hypothesis generation: 5/10 — Perturbation generation explores local variations but does not propose alternative explanatory structures beyond the given answer.  
Implementability: 8/10 — All components (regex parsing, DAG ops, simple numeric loops, numpy for sensitivity) fit easily within numpy and the standard library.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:56:15.386270

---

## Code

*No code was produced for this combination.*

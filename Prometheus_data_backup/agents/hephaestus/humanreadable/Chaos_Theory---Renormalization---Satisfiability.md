# Chaos Theory + Renormalization + Satisfiability

**Fields**: Physics, Physics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T06:44:38.677970
**Report Generated**: 2026-03-31T18:50:23.283762

---

## Nous Analysis

The algorithm builds a hierarchical constraint network from the text, solves it with a DPLL‑style SAT solver, and evaluates each candidate answer by measuring both satisfaction and sensitivity to perturbations — a Lyapunov‑like exponent computed across renormalization scales.

**Data structures**  
- `VarMap`: dict mapping each extracted propositional atom (e.g., “X>Y”, “¬Cause”) to an integer index.  
- `ClauseList`: list of clauses, each a Python set of signed integers (positive = literal, negative = negation).  
- `RenormTree`: a binary tree where each leaf contains a block of variables (size ≤ B, e.g., 8) and internal nodes store the union of their children’s variable sets.  
- `Assign`: numpy array of shape (n_vars,) with values in {0,1,‑1} (‑1 = unassigned).

**Operations**  
1. **Structural parsing** – regex extracts literals for negations (`not`, `no`), comparatives (`>`, `<`, `≥`, `≤`), conditionals (`if … then …`), causal cues (`because`, `leads to`), ordering (`before`, `after`), and numeric thresholds. Each literal becomes a variable; its polarity is stored in the clause.  
2. **Clause construction** – each sentence yields one or more clauses (e.g., “If A then B” → ¬A ∨ B).  
3. **Renormalization** – variables are grouped by sliding‑window co‑occurrence; leaves of `RenormTree` hold these groups. Internal nodes represent coarser scales.  
4. **DPLL solving** – unit propagation and pure‑literal elimination are performed on `ClauseList` using numpy for fast array look‑ups; backtracking explores assignments.  
5. **Scoring a candidate** – the candidate supplies a full assignment; the solver computes the fraction of satisfied clauses `sat`.  
6. **Sensitivity (Lyapunov) measure** – for each variable, flip its value, recompute `sat` (using incremental propagation), record Δsat. The average absolute Δsat over all variables gives `ε`. The Lyapunov‑like score is `λ = log(ε + 1e‑9)`. Lower λ indicates robustness.  
7. **Final score** = `sat – α·λ` (α ≈ 0.2 balances satisfaction vs. stability).

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, ordering relations, numeric thresholds, and conjunctive/disjunctive connectives.

**Novelty**  
Pure SAT‑based semantic scoring exists, but coupling it with a multi‑scale renormalization hierarchy and a Lyapunov exponent–style stability metric is not documented in NLP or KR literature; the combination yields a novel way to quantify both logical fit and structural sensitivity.

**Reasoning:** 7/10 — captures logical consistency and sensitivity, but approximative renormalization may miss subtle dependencies.  
**Metacognition:** 5/10 — the method evaluates its own stability via λ, yet lacks explicit self‑reflection on search strategy depth.  
**Hypothesis generation:** 6/10 — generates alternative assignments during backtracking, providing implicit hypotheses, but does not output them explicitly.  
**Implementability:** 8/10 — relies only on regex, numpy arrays, and recursive backtracking; all feasible in plain Python.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T18:50:22.366799

---

## Code

*No code was produced for this combination.*

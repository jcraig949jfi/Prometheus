# Apoptosis + Sensitivity Analysis + Satisfiability

**Fields**: Biology, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T22:18:46.288951
**Report Generated**: 2026-03-31T14:34:57.350074

---

## Nous Analysis

**1. Algorithm – Robust‑Core SAT Scorer**  
*Data structures*  
- `var_map: dict[str, int]` – maps each propositional atom extracted from the prompt and candidate answer to an integer index.  
- `clauses: List[List[int]]` – each clause is a list of signed literals (positive for the variable, negative for its negation).  
- `premise_weights: np.ndarray` – float32 array, one weight per premise clause, initialized to 1.0.  
- `assignment: np.ndarray` – int8 array of shape (n_vars,) with values ‑1 (unassigned), 0 (false), 1 (true).  

*Operations*  
1. **Parsing → CNF** – Convert the prompt (premises) and each candidate answer into conjunctive normal form using a deterministic rule‑based translator (handles negations, comparatives → inequality literals, conditionals → implication‑to‑CNF, ordering → transitive closure).  
2. **Initial SAT check** – Run a unit‑propagation‑based DPLL solver (pure Python loops, numpy for fast literal‑count updates). If the formula is UNSAT, invoke **conflict analysis**: traverse the implication graph to produce a minimal unsatisfiable core (MUC) – the set of premise clauses whose simultaneous removal restores SAT. This step embodies the *apoptosis* principle: systematically excising offending premises.  
3. **Weight adjustment** – For each clause `c` in the MUC, multiply its weight by a decay factor `α < 1` (e.g., 0.5). Premises outside the core keep weight 1.0.  
4. **Sensitivity analysis** – For each premise clause `p_i`, temporarily flip its truth value in the current best model (obtained from the SAT solver under weighted MaxSAT: maximize sum of satisfied premise weights). Re‑run unit propagation; record whether the answer literal flips. The sensitivity score for `p_i` is the proportion of flips that change the answer’s truth value.  
5. **Final answer score** –  
   \[
   \text{Score} = \underbrace{\frac{\sum_i w_i \cdot sat_i}{\sum_i w_i}}_{\text{weighted premise satisfaction}} \times
   \underbrace{\bigl(1 - \frac{1}{n_{prem}}\sum_i \text{sens}_i\bigr)}_{\text{robustness term}}
   \]  
   where `sat_i` is 1 if premise `i` is satisfied in the weighted MaxSAT model, `sens_i` its sensitivity, and `n_{prem}` the number of premises. Higher scores indicate answers that are both well‑supported by resilient premises and minimally dependent on fragile ones.

**2. Parsed structural features**  
- Negations (`not`, `-`) → literal sign.  
- Comparatives (`>`, `<`, `≥`, `≤`, `=`) → arithmetic literals encoded as difference constraints (handled via auxiliary Boolean variables).  
- Conditionals (`if … then …`, `implies`) → implication → CNF (¬A ∨ B).  
- Causal claims (`because`, `leads to`) → treated as conditionals with a temporal ordering variable.  
- Ordering relations (`before`, `after`, `first`, `last`) → encoded as transitive closure of precedence literals.  
- Numeric values → mapped to interval literals (e.g., `x ∈ [5,7]`).  

**3. Novelty**  
The triplet maps to known techniques: SAT‑based reasoning, MUC extraction (used in debugging), and local sensitivity (one‑at‑a‑time perturbation). Their *joint* use as a unified scoring function for natural‑language candidate answers is not described in the literature; existing work treats each component in isolation (e.g., SAT for logic puzzles, sensitivity for numerical models, MUC for conflict explanation). Hence the combination is novel in the context of automated answer grading.

**Rating**  
Reasoning: 8/10 — The algorithm directly evaluates logical consistency, robustness, and minimal conflict, capturing core aspects of deductive reasoning.  
Metacognition: 6/10 — It can report which premises caused sensitivity or were excised, offering rudimentary self‑explanation, but lacks higher‑order reflection on its own uncertainty.  
Hypothesis generation: 5/10 — While it can suggest alternative premise sets (via weighted MaxSAT) that would flip the answer, it does not autonomously generate new conjectures beyond perturbation.  
Implementability: 9/10 — All steps rely on deterministic parsing, unit propagation (numpy‑accelerated), and simple loops; no external libraries or neural components are required.

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

# Evolution + Property-Based Testing + Sensitivity Analysis

**Fields**: Biology, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T09:15:21.306391
**Report Generated**: 2026-03-31T16:23:53.880780

---

## Nous Analysis

**Algorithm**  
We treat each candidate answer as a genotype consisting of a set of logical propositions extracted from the text. A proposition is a tuple `(type, polarity, vars, bounds)` where `type ∈ {negation, comparative, conditional, causal, numeric, ordering, quantifier}`; `polarity` is ±1 for presence/absence; `vars` are the entity or variable symbols; `bounds` hold numeric thresholds when applicable. All propositions are stored in a list `P`.  

From `P` we build a constraint graph `G`. Directed edges represent modus ponens (`if A then B`) and transitivity of ordering (`A < B ∧ B < C ⇒ A < C`). Numeric propositions contribute interval constraints; causal claims contribute directed influence edges with a weight of 1.  

**Fitness evaluation** (the “phenotype”) proceeds in three stages:  

1. **Baseline consistency** – Count satisfied constraints in `G` using a simple forward‑chaining algorithm; each satisfied edge adds 1, each violated edge subtracts 1. This yields `f₀`.  
2. **Mutation generation (Property‑Based Testing)** – Apply a shrinking‑style mutation operator to the answer: randomly flip a negation, perturb a numeric value within ±10 % of its bound, swap the antecedent/consequent of a conditional, or replace a causal cue with a neutral phrase. Each mutant produces a new proposition set `P′` and graph `G′`.  
3. **Sensitivity analysis** – For each mutant compute its fitness `fᵢ`. Sensitivity `S` is the mean absolute drop `‖f₀ − fᵢ‖` over a fixed‑size mutation batch (e.g., 50).  

The final score is `score = f₀ − λ·S`, where λ balances consistency against robustness (chosen as 0.5). The algorithm iterates: the top‑scoring answer seeds the next generation via elitist selection, mutations are reapplied, and the process stops after a fixed number of generations or when improvement stalls. Shrinking is invoked when a mutant fails (score < threshold) to isolate the minimal subset of propositions causing the failure, mirroring Hypothesis’ shrinking phase.  

**Parsed structural features**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `≥`, `≤`)  
- Conditionals (`if … then …`, `unless`)  
- Causal claims (`because`, `leads to`, `causes`)  
- Numeric values and units  
- Ordering relations (`before`, `after`, `first`, `last`)  
- Quantifiers (`all`, `some`, `none`)  

**Novelty**  
While property‑based testing and sensitivity analysis are well studied in software and uncertainty quantification, and evolutionary search appears in program synthesis, their joint use to score natural‑language reasoning answers—using mutation‑driven robustness as a direct penalty on logical consistency—has not been described in existing literature.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and robustness to perturbations.  
Metacognition: 6/10 — limited self‑reflection beyond sensitivity; no explicit uncertainty modeling.  
Hypothesis generation: 7/10 — mutants act as hypotheses about failing inputs; shrinking isolates minimal causes.  
Implementability: 9/10 — relies only on regex, numpy for vector ops, and Python stdlib.

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

**Forge Timestamp**: 2026-03-31T16:21:36.113891

---

## Code

*No code was produced for this combination.*

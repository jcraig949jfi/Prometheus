# Pragmatics + Nash Equilibrium + Sensitivity Analysis

**Fields**: Linguistics, Game Theory, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T13:33:07.725797
**Report Generated**: 2026-03-31T16:34:28.503452

---

## Nous Analysis

The algorithm builds a propositional‑constraint graph from the prompt and each candidate answer, then treats answer selection as a zero‑sum game between the responder and an adversarial “nature” that perturbs inputs.  

**Data structures**  
- `Prop`: tuple `(subj, rel, obj, polarity, modality)` where `polarity ∈ {+1,‑1}` encodes negation, `modality ∈ {assert, conditional, causal}`.  
- `Constraint`: derived from a Prop; for comparatives we store a numeric bound `(var, op, value)`.  
- `World`: a specific perturbation of the prompt (numeric values shifted by ±ε, polarity flipped, conditional antecedent/ consequent swapped). Represented as a list of altered Constraints.  
- `Payoff matrix` `U ∈ ℝ^{A×W}` where `A` = number of candidate answers, `W` = number of worlds; entry `U[a,w]` is the degree to which answer `a` satisfies all constraints in world `w` (computed as the fraction of satisfied constraints, 0–1).  

**Operations**  
1. **Parsing** – regex extracts subject‑verb‑object triples, detects negations (`not`, `n’t`), comparatives (`>`, `<`, `≥`, `≤`, “more than”), conditionals (`if … then …`), causal markers (`because`, `leads to`), and numeric tokens with units. Each yields a Prop inserted into a directed graph.  
2. **Constraint propagation** – Floyd‑Warshall style transitive closure derives implied ordering and equality constraints; modus ponens propagates conditionals when antecedent is true.  
3. **Answer evaluation** – for each world, compute satisfaction of every Prop; unsatisfied Prop reduces payoff proportionally to its weight (default 1).  
4. **Perturbation set** – generate worlds by independently varying each numeric constraint within a tolerance ε (e.g., 5% of its value), flipping polarity of each negation, and swapping antecedent/consequent of each conditional.  
5. **Game solution** – treat the responder as choosing a mixed strategy over answers, nature choosing a mixed strategy over worlds. Compute the Nash equilibrium of the zero‑sum game via linear programming (simplex implemented with numpy.linalg.lstsq on the payoff matrix). The equilibrium value `v` is the final score for the prompt (higher = more robust answer).  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering/temporal relations, numeric values with units, quantifier scope (“all”, “some”), and speech‑act markers that affect modality (e.g., “I suggest” vs. “It is”).  

**Novelty** – While pragmatic enrichment, game‑theoretic answer aggregation, and sensitivity analysis appear separately in literature, their joint use to define a minimax robustness score over a explicitly constructed perturbation space has not been combined in a pure‑numpy, rule‑based tool.  

Reasoning: 8/10 — captures logical consistency and uncertainty via equilibrium, but relies on linear approximations of satisfaction.  
Metacognition: 6/10 — limited self‑monitoring; parsing confidence is not fed back into strategy updates.  
Hypothesis generation: 7/10 — generates alternative worlds as explicit hypotheses about missing or noisy context.  
Implementability: 9/10 — uses only regex, numpy matrix ops, and a simple simplex loop; no external libraries needed.

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

**Forge Timestamp**: 2026-03-31T16:33:23.322387

---

## Code

*No code was produced for this combination.*

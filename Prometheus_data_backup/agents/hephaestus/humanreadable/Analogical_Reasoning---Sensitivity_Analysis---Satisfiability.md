# Analogical Reasoning + Sensitivity Analysis + Satisfiability

**Fields**: Cognitive Science, Statistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-31T19:24:49.491079
**Report Generated**: 2026-03-31T19:46:57.746431

---

## Nous Analysis

**Algorithm**  
The tool builds a *hybrid constraint‑satisfaction graph* from each answer. First, a deterministic regex‑based parser extracts atomic propositions:  
- **Entities** → variables (e.g., `X`, `Y`).  
- **Predicates** → binary relations (`greaterThan`, `causes`, `equals`).  
- **Logical connectives** → implication (`if P then Q`), negation (`¬P`), conjunction/disjunction.  
Each proposition becomes a clause in a conjunctive‑normal‑form (CNF) formula. Numeric predicates are attached to interval domains (e.g., `value(X) ∈ [0,100]`).  

Analogical reasoning supplies a *reference template* graph `G_ref` derived from a model answer. The candidate’s proposition graph `G_cand` is matched to `G_ref` using a label‑preserving subgraph isomorphism heuristic (node/edge type equality, ignoring variable names). The similarity score `S_ana = |M| / max(|V_ref|,|V_cand|)` where `M` is the set of matched nodes/edges.

Sensitivity analysis is performed by perturbing each numeric bound in the candidate’s clauses by ±ε (ε = 1% of the range) and re‑running a unit‑propagation SAT solver. For each clause `c`, we compute the change in satisfied‑clause count Δc; the sensitivity weight `w_c = 1 / (1 + |Δc|)`. Clauses with high sensitivity receive lower weight in the final score.

Scoring logic:  
1. Run unit propagation on the weighted CNF; let `sat` be the number of satisfied clauses.  
2. Compute a minimal unsatisfiable core (MUC) via greedy clause removal; let `core_size` be its length.  
3. Final score = `α·(sat / total_clauses) + β·S_ana + γ·(1 – core_size/total_clauses) – δ·Σ w_c·perturbation_penalty`, with α,β,γ,δ tuned to sum to 1.  

**Parsed structural features**  
Negations (`not`, `no`), comparatives (`greater than`, `less than`, `more`), conditionals (`if … then`, `unless`), causal cues (`because`, `leads to`), ordering (`before`, `after`, `ranked`), numeric values with units, and equality/inequality tokens.

**Novelty**  
Each piece — semantic parsing, SAT‑based consistency checking, sensitivity analysis, and analogical graph matching — exists separately. Prior answer‑scoring systems rely on surface similarity or isolated reasoning modules; none combine constraint propagation with analogical transfer and sensitivity‑weighted clause scoring in a single deterministic pipeline, making this combination novel for automated reasoning evaluation.

**Ratings**  
Reasoning: 8/10 — captures logical structure and robustness but depends on heuristic matching.  
Metacognition: 6/10 — provides explicit uncertainty via sensitivity yet lacks self‑reflective monitoring.  
Implementability: 9/10 — uses only regex, numpy, and standard‑library SAT/propagation code.  
Hypothesis generation: 5/10 — focuses on verification rather than generating new conjectures.

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

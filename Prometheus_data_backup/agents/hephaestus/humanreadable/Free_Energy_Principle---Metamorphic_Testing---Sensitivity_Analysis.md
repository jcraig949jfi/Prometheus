# Free Energy Principle + Metamorphic Testing + Sensitivity Analysis

**Fields**: Theoretical Neuroscience, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T20:32:42.703602
**Report Generated**: 2026-04-02T04:20:11.280138

---

## Nous Analysis

The algorithm builds a lightweight propositional graph from each candidate answer, evaluates how well it satisfies a set of metamorphic relations (MRs), penalizes sensitivity to small input perturbations, and interprets the total as variational free energy to be minimized.  

**Data structures**  
- `Proposition`: `{text, polarity (±1), modality (certain/possible), num_val (float or None), scope (tuple of variables)}`.  
- `MR`: a function `(p, q) → bool` that encodes a transformation invariant (e.g., double‑input, order‑swap, negation‑flip).  
- `Graph`: adjacency list where edges are labeled with the MR that generated them.  

**Operations**  
1. **Parsing** – regex extracts propositions for:  
   - Negations (`not`, `no`),  
   - Comparatives (`greater than`, `less than`, `≥`, `≤`),  
   - Conditionals (`if … then …`, `because`, `leads to`),  
   - Causal keywords (`cause`, `effect`),  
   - Ordering relations (`before`, `after`, `first`, `last`),  
   - Numeric values (`\d+(\.\d+)?`).  
   Each extracted chunk becomes a `Proposition`.  
2. **MR application** – for every pair of propositions, apply a predefined MR set:  
   - *Double*: if `p.num_val` exists, check `q.num_val ≈ 2·p.num_val`.  
   - *Order‑swap*: if `p` expresses `A > B`, verify `q` expresses `B < A`.  
   - *Negation*: if `p` contains `not`, verify `q` lacks it (or vice‑versa).  
   - *Scalar‑add*: add a small constant ε to numeric values and see if the relation persists.  
   The proportion of satisfied MRs yields a **consistency score** C ∈ [0,1].  
3. **Sensitivity analysis** – generate N perturbed variants of the answer (synonym swap, numeric ±ε, insertion/removal of a negation). For each variant recompute C; compute the standard deviation σ_C.  
4. **Free‑energy score** – FE = (1 − C) + λ·σ_C, with λ set to 0.5. Lower FE indicates better prediction‑error minimization. Final answer score = 1 / (1 + FE), normalized to [0,1].  

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering/temporal relations, numeric constants, quantifiers (`all`, `some`, `none`).  

**Novelty** – While metamorphic testing, sensitivity analysis, and the free‑energy principle each appear in software testing, uncertainty quantification, and cognitive modeling respectively, their joint use to score natural‑language reasoning answers has not been reported in the literature, making the combination novel.  

**Ratings**  
Reasoning: 7/10 — captures logical consistency and robustness but lacks deep semantic understanding.  
Metacognition: 6/10 — monitors sensitivity to perturbations, a rudimentary form of self‑check.  
Hypothesis generation: 5/10 — limited to proposing perturbations; does not generate new explanatory hypotheses.  
Implementability: 8/10 — relies only on regex, numpy arrays, and pure Python; straightforward to code and test.

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

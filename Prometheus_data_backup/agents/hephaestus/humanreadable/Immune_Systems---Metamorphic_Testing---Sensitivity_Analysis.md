# Immune Systems + Metamorphic Testing + Sensitivity Analysis

**Fields**: Biology, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T23:59:07.724565
**Report Generated**: 2026-03-31T17:10:38.132740

---

## Nous Analysis

**Algorithm – Clonal Metamorphic Sensitivity Scorer (CMSS)**  

1. **Data structures**  
   - `Prop`: a namedtuple `(type, polarity, args)` where `type ∈ {NUM, COMP, ORDER, CAUSAL, COND, NEG}` and `args` holds extracted tokens (e.g., numbers, variable names).  
   - `AnswerGraph`: a directed graph (`dict[int, list[int]]`) where nodes are `Prop` indices and edges represent explicit relations extracted from the candidate answer (e.g., “A > B” → edge from A to B with label `>`).  
   - `Population`: a NumPy array of shape `(P, M)` where `P` is the number of clones (mutants) and `M` is the number of propositions; each entry is a float fitness contribution for that proposition.  
   - `PerturbationSet`: a list of metamorphic operators (functions) that transform an `AnswerGraph`:  
        * `scale_num(k)` – multiply all `NUM` args by `k` (k∈{0.5,2})  
        * `swap_order(i,j)` – exchange the subjects of two `ORDER` propositions  
        * `toggle_neg(p)` – flip polarity of a `NEG` proposition  
        * `cond_invert(c)` – swap antecedent/consequent of a `COND` proposition  
        * `causal_reverse(c)` – invert direction of a `CAUSAL` edge  

2. **Operations**  
   - **Parsing**: regex extracts propositions from prompt and candidate answer, filling `Prop` objects and building the reference graph `G_ref` and answer graph `G_ans`.  
   - **Clonal expansion**: generate `P` clones by randomly applying 1‑3 metamorphic operators from `PerturbationSet` to `G_ans`.  
   - **Constraint propagation**: for each clone, run a forward‑chaining modus‑ponens engine over `G_ref` ∪ clone graph, marking satisfied propositions (binary 1/0). Store results in `Population`.  
   - **Fitness calculation**: `fitness = Population.mean(axis=1)` – proportion of satisfied propositions per clone.  
   - **Sensitivity analysis**: compute variance of fitness across clones for each perturbation type (`sens = np.var(fitness_by_operator, axis=0)`). Overall sensitivity = `sens.mean()`.  
   - **Score**: `score = fitness_mean - λ * sensitivity`, where λ=0.2 penalizes answers whose correctness is fragile under metamorphic perturbations.  

3. **Structural features parsed**  
   - Numerics and scalars (`NUM`)  
   - Comparatives (`>` `<` `=` `≥` `≤`) → `COMP`  
   - Ordering/temporal relations (`before`, `after`, `earlier`) → `ORDER`  
   - Negations (`not`, `no`, `never`) → `NEG`  
   - Conditionals (`if … then …`, `unless`) → `COND`  
   - Causal markers (`because`, `leads to`, `results in`) → `CAUSAL`  
   - Conjunctions/disjunctions (`and`, `or`) used to combine propositions.  

4. **Novelty**  
   Pure metamorphic testing or sensitivity analysis appear in software verification and uncertainty quantification, respectively. Immune‑inspired clonal selection is used in optimization but rarely paired with explicit metamorphic operators for answer scoring. The triple integration—clonal variant generation, metamorphic relation enforcement, and perturbation‑based sensitivity—is not documented in existing NLP reasoning‑evaluation tools, making the combination novel.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and robustness via clonal selection and metamorphic constraints.  
Metacognition: 6/10 — limited self‑reflection; score relies on predefined perturbation set rather than dynamic strategy adaptation.  
Hypothesis generation: 7/10 — generates diverse answer mutants, enabling exploration of alternative interpretations.  
Implementability: 9/10 — uses only regex, NumPy arrays, and standard‑library graph operations; no external models needed.

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

**Forge Timestamp**: 2026-03-31T17:08:47.468195

---

## Code

*No code was produced for this combination.*

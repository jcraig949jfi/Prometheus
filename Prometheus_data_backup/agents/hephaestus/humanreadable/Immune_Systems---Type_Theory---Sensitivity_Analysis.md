# Immune Systems + Type Theory + Sensitivity Analysis

**Fields**: Biology, Logic, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T03:18:16.518248
**Report Generated**: 2026-03-31T16:31:50.629895

---

## Nous Analysis

**Algorithm: Clonal‑Typed Sensitivity Scorer (CTSS)**  
1. **Parsing & Typing** – The prompt and each candidate answer are tokenized with a rule‑based regex extractor that builds a typed abstract syntax tree (TAST). Nodes carry a simple type from a finite hierarchy: `Prop` (proposition), `Num` (numeric term), `Ord` (ordering term), `Cause` (causal link), `Neg`, `Comp` (comparative), `Cond` (conditional). Dependent‑type annotations are added where a node’s type depends on a sibling (e.g., a `Cause` node’s type is `Prop → Prop`).  
2. **Clause Extraction** – From each TAST we extract Horn‑style clauses: `Head :- Body1, Body2, …`. Negations become `¬p` literals; comparatives become `x > y` atoms; conditionals become `p → q`. Numeric literals are kept as concrete `Num` values.  
3. **Clonal Selection** – For each candidate, we generate a clonal population of proof attempts: start with the set of clauses from the prompt, then iteratively **mutate** by (a) adding a literal from the candidate, (b) applying resolution/unification using numpy arrays to represent literal signatures (type‑coded one‑hot vectors). Affinity of a clone is the fraction of its body literals that unify with prompt clauses **and** satisfy type constraints (checked via a lookup table). The top‑k clones survive; the process repeats for a fixed number of generations (clonal expansion).  
4. **Sensitivity Evaluation** – For the surviving clones we compute a sensitivity score: perturb each input token (swap synonym, drop a negation, tweak a numeric value by ±1 %) using a small set of predefined perturbations; re‑run the clonal selection and record the drop in affinity. The sensitivity penalty is the L2 norm (numpy) of affinity drops across perturbations. Final score = affinity − λ·sensitivity, with λ tuned to balance fit vs. robustness.  

**Structural Features Parsed** – Negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then …`), numeric values and units, causal verbs (`because`, `leads to`), ordering relations (`before`, `after`), and type‑dependent constructs (e.g., “the *amount* of X”).  

**Novelty** – Clonal selection algorithms exist in artificial immune systems; type‑theoretic parsing appears in proof‑assistants; sensitivity analysis is standard in robustness testing. Their combination—using affinity‑driven clonal expansion guided by dependent types and penalized by perturbation‑based sensitivity—has not been described in the literature, making the approach novel.  

**Ratings**  
Reasoning: 8/10 — captures logical structure and robustness, but relies on hand‑crafted rules.  
Metacognition: 6/10 — limited self‑reflection; no explicit monitoring of search beyond affinity.  
Hypothesis generation: 7/10 — clonal mutation yields diverse proof hypotheses.  
Implementability: 9/10 — uses only regex, numpy arrays, and standard‑library data structures.

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

**Forge Timestamp**: 2026-03-31T16:31:04.145938

---

## Code

*No code was produced for this combination.*

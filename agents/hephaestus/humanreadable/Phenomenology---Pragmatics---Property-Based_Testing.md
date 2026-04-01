# Phenomenology + Pragmatics + Property-Based Testing

**Fields**: Philosophy, Linguistics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T23:23:03.864006
**Report Generated**: 2026-03-31T14:34:57.396072

---

## Nous Analysis

**Algorithm**  
The tool builds a *propositional constraint graph* from each candidate answer and scores it by how well the graph satisfies a specification derived from the reference answer using property‑based testing.  

1. **Parsing (phenomenology + pragmatics)** – A set of regex patterns extracts elementary propositions:  
   - `Proposition = {subject: str, predicate: str, obj: str|None, quantifier: str, polarity: bool, modality: str, numeric: float|None, tense: str}`  
   Patterns capture negations (`not`, `no`), comparatives (`>`, `<`, `more than`, `less than`), conditionals (`if … then …`), causal markers (`because`, `leads to`), ordering (`before`, `after`), and explicit numbers. Each match creates a Proposition object and is stored in a list `props`.  

2. **Constraint graph construction** – Nodes are propositions; directed edges represent logical relations inferred from the text:  
   - *Taxonomy*: `subject` → `predicate` (type).  
   - *Comparison*: numeric values → inequality edges.  
   - *Conditional*: antecedent → consequent (implication).  
   - *Causal*: cause → effect.  
   - *Ordering*: temporal markers → precedence edges.  
   The graph is stored as adjacency matrices `A_qual` (qualitative) and `A_num` (numeric) using NumPy arrays of shape `(n, n)`.  

3. **Constraint propagation** – Apply transitive closure on `A_qual` (Floyd‑Warshall style) to derive implicit relations (e.g., if A → B and B → C then A → C). For numeric edges, propagate bounds using interval arithmetic (e.g., if x > 5 and x < 10 then 5 < x < 10). Violations (e.g., a node forced both true and false) are recorded as unsolved constraints.  

4. **Property‑based testing & shrinking** – Treat the reference answer’s proposition set as a *specification*. Generate random perturbations of the candidate’s propositions:  
   - Entity swap, quantifier flip (`all` ↔ `some`), polarity toggle, numeric jitter (±10 %), modality change.  
   Each perturbed version is re‑parsed and run through the constraint propagator; a version is **failing** if any constraint is violated.  
   Using a Hypothesis‑style shrinking loop, the algorithm reduces the perturbation size (number of altered fields) until a minimal failing perturbation is found. Let `k_min` be the number of altered fields in that minimal failure and `k_max` the total number of fields across all propositions. The *property score* is `1 - k_min / k_max`.  

5. **Final score** – Combine structural satisfaction (`sat = proportion of constraints satisfied after propagation`) with the property score:  
   `score = 0.6 * sat + 0.4 * (1 - k_min / k_max)`.  
   The score lies in `[0,1]` and can be thresholded for pass/fail.  

**Structural features parsed**  
Negations, comparatives, conditionals, causal markers, ordering/temporal markers, explicit numbers, quantifiers (`all`, `some`, `none`), modal verbs (`must`, `might`, `should`), and attributive adjectives.  

**Novelty**  
While logical‑form extraction, pragmatic enrichment (Grice‑style constraints), and property‑based testing each appear separately in the literature, no published system fuses all three into a single constraint‑propagation + property‑testing scoring loop. This combination is therefore novel.  

**Ratings**  
Reasoning: 7/10 — captures logical structure and pragmatic implicature but relies on shallow regex, limiting deep semantic nuance.  
Metacognition: 5/10 — the algorithm does not explicitly model the answerer’s confidence or self‑monitoring; it only evaluates output consistency.  
Hypothesis generation: 8/10 — property‑based generation with shrinking systematically explores the answer space to find minimal counterexamples.  
Implementability: 9/10 — uses only regex, NumPy matrix ops, and standard‑library loops; no external dependencies or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 8/10 |
| Implementability | 9/10 |
| **Composite** | **6.67** |

**Novelty**: unproductive
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

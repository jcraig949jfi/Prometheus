# Symbiosis + Dual Process Theory + Metamorphic Testing

**Fields**: Biology, Cognitive Science, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T00:41:10.993329
**Report Generated**: 2026-04-02T04:20:11.648042

---

## Nous Analysis

**Algorithm: Symbiotic Dual‑Process Metamorphic Scorer (SDMS)**  

1. **Data structures**  
   - `PromptGraph`: directed labeled multigraph where nodes are extracted propositions (e.g., “X > Y”, “if A then B”) and edges encode logical relations (negation, implication, ordering, equality). Built with `dict[node_id, dict]` and adjacency lists (`list[(target_id, relation_type)]`).  
   - `AnswerGraphs`: list of one such graph per candidate answer.  
   - `MetamorphicCache`: `numpy.ndarray` of shape `(n_answers, n_relations)` storing Boolean satisfaction of each metamorphic relation (MR) for each answer.  

2. **Parsing (System 1 – fast, pattern‑based)**  
   - Apply a fixed set of regexes to capture:  
     * numeric literals (`\d+(?:\.\d+)?`) → numeric nodes,  
     * comparatives (`>`, `<`, `>=`, `<=`, `=`) → ordering edges,  
     * negations (`not`, `n’t`, `no`) → negation edges,  
     * conditionals (`if … then …`, `when …`) → implication edges,  
     * causal cue words (`because`, `due to`, `leads to`) → causal edges.  
   - Each match creates a node with a type tag (`NUM`, `COMP`, `COND`, `CAUS`, `NEG`).  

3. **Constraint propagation (System 2 – slow, deliberate)**  
   - Initialise a truth‑value vector `v` (float32) for each node (`1.0` = true, `0.0` = false, `0.5` = unknown).  
   - Iterate until convergence (max 10 passes):  
     * **Modus ponens**: if `A → B` edge exists and `v[A] > 0.5` then set `v[B] = max(v[B], v[A])`.  
     * **Transitivity** for ordering: if `X > Y` and `Y > Z` then enforce `v[X > Z] = min(v[X > Y], v[Y > Z])`.  
     * **Negation**: `v[¬P] = 1.0 - v[P]`.  
   - Use numpy vectorised operations on adjacency matrices for speed.  

4. **Metamorphic relation testing**  
   - Define a small MR set derived from the prompt:  
     * **Doubling**: if a numeric node `n` appears, create MR `n' = 2·n` and check that any derived comparative (`n' > m`) holds when `2·n > m` holds in the propagated graph.  
     * **Order preservation**: for any ordering edge `a > b`, MR states that swapping both sides (`b > a`) must flip truth value.  
   - For each answer, evaluate each MR by re‑running the propagation on a mutated copy of the answer graph (only the affected numeric/comparative nodes changed). Store Boolean result in `MetamorphicCache`.  

5. **Scoring logic**  
   - Base score = average truth‑value of all nodes in the answer graph after propagation (`np.mean(v)`).  
   - MR penalty = proportion of violated MRs (`1 - np.mean(MetamorphicCache, axis=1)`).  
   - Final score = `0.7 * base_score + 0.3 * (1 - MR_penalty)`. Higher scores indicate answers that are both logically consistent with the prompt and respect the defined metamorphic invariants.  

**Structural features parsed** – numeric values, comparatives, ordering chains, negations, conditionals, causal assertions, and explicit equality statements.  

**Novelty** – The combination mirrors “symbiosis” by treating the prompt and answer as mutually beneficial entities that co‑evolve through constraint propagation; dual‑process theory supplies the fast‑parse/slow‑reason split; metamorphic testing supplies oracle‑free validation via MRs. While each component exists separately (e.g., semantic parsers, logic solvers, MR‑based testing), their tight integration in a single lightweight scorer is not documented in public literature, making the approach novel for automated reasoning evaluation.  

**Ratings**  
Reasoning: 8/10 — captures logical consistency and invariant preservation with provable propagation.  
Metacognition: 6/10 — limited self‑monitoring; relies on fixed MR set rather than dynamic MR discovery.  
Hypothesis generation: 5/10 — generates hypotheses only via predefined MRs; no open‑ended abductive step.  
Implementability: 9/10 — uses only regex, numpy arrays, and plain Python data structures; no external dependencies.

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

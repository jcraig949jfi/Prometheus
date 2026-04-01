# Embodied Cognition + Compositionality + Type Theory

**Fields**: Cognitive Science, Linguistics, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T10:27:49.872713
**Report Generated**: 2026-03-31T14:34:55.971913

---

## Nous Analysis

**Algorithm**  
We build a lightweight *typed dependency graph* (TDG) for each sentence.  
1. **Parsing (Compositionality + Embodied Cognition)** – Using only the standard library, we tokenize the prompt and each candidate answer with regex‑based patterns that extract:  
   - atomic predicates (e.g., “X is Y”, “X > Y”, “if X then Y”)  
   - modal/affordance markers (e.g., “can”, “must”, “because”) that map to sensorimotor grounding predicates such as `GRASP(X)`, `MOVE(X,Y)`.  
   Each extracted triple `(subject, relation, object)` becomes a node labeled with a *type* drawn from a small hierarchy: `Entity`, `Quantity`, `Event`, `Property`.  
2. **Type‑checking (Type Theory)** – We assign each node a type and verify that the relation’s signature matches (e.g., `>` expects `Quantity` on both sides). Mismatches incur a fixed penalty (`-1.0`). This is a simple lookup table; no external solver is needed.  
3. **Constraint propagation (Embodied Cognition)** – Grounded affordances are treated as Horn clauses: `CAN(X, Y) :- GRASP(X), REACHABLE(Y,X)`. We iteratively apply forward chaining using numpy arrays to store boolean truth values for each grounded predicate. Transitivity of `>` and `<=` is encoded as matrix multiplication on the adjacency matrix of quantity nodes.  
4. **Scoring** – For each candidate, we compute:  
   - **Type‑fit score** = proportion of nodes passing type checks.  
   - **Grounded‑consistency score** = proportion of affordance clauses satisfied after propagation (numpy sum of true clauses / total clauses).  
   - **Compositional overlap** = Jaccard index of predicate sets between prompt and candidate (numpy‑based set ops).  
   Final score = 0.4·type‑fit + 0.4·grounded‑consistency + 0.2·compositional overlap, clamped to [0,1].

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then …`), causal markers (`because`, `leads to`), numeric values and units, ordering relations (`first`, `before`, `after`), and affordance verbs (`can lift`, `must avoid`).

**Novelty**  
The combination mirrors existing neuro‑symbolic pipelines (e.g., LTN, DeepProbLog) but replaces neural components with deterministic regex‑based parsing, simple type theory, and numpy‑driven Horn‑clause propagation. No prior work publishes this exact triple‑layered TDG scoring scheme using only stdlib+numpy, so it is novel in the constrained‑resource setting.

**Ratings**  
Reasoning: 7/10 — captures logical structure and grounded consistency but relies on shallow regex parsing, limiting deep semantic nuance.  
Metacognition: 5/10 — the system can detect type mismatches and unsatisfied affordances, offering a rudimentary confidence estimate, yet lacks self‑reflective revision loops.  
Hypothesis generation: 4/10 — hypothesis formation is implicit in forward chaining; no explicit generation of alternative explanations beyond what the rules allow.  
Implementability: 9/10 — all steps use regex, basic Python containers, and numpy arrays; no external libraries or APIs are required, making it straightforward to deploy.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 4/10 |
| Implementability | 9/10 |
| **Composite** | **5.33** |

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

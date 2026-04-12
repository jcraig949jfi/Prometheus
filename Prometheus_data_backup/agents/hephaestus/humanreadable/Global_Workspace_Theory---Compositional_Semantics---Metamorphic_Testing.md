# Global Workspace Theory + Compositional Semantics + Metamorphic Testing

**Fields**: Cognitive Science, Philosophy, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:41:52.912809
**Report Generated**: 2026-03-27T04:25:55.953087

---

## Nous Analysis

**Algorithm**  
1. **Parsing & representation** – Use a handful of regex patterns to extract atomic propositions from a prompt and each candidate answer:  
   - Predicates: `is(X, Y)`, `greater(X, Y)`, `less(X, Y)`, `equal(X, Y)`, `before(X, Y)`, `after(X, Y)`, `cause(X, Y)`.  
   - Logical connectives: `not`, `and`, `or`, `if … then …`.  
   - Numeric terms are captured as floats with optional units.  
   The output is a directed acyclic graph (DAG) where nodes are atoms and edges encode syntactic combination (function application). This DAG is the *compositional semantics* layer: leaf nodes map to primitive predicates (looked up in a tiny dictionary), internal nodes apply the corresponding logical or arithmetic operator (e.g., `greater` → `np.greater`).  

2. **Global Workspace ignition** – Initialise a Boolean workspace array `W` (size = number of distinct atoms) with `False`. For each atom whose truth can be determined directly from the prompt (e.g., a given fact), set the corresponding entry to `True`. These are the *ignited* items.  

3. **Constraint propagation (metamorphic testing layer)** – Define a set of metamorphic relations (MRs) that must hold between the prompt and any valid answer:  
   - **MR1 (Negation flip)**: if `not P` appears in the prompt, the answer must assert `P` → false.  
   - **MR2 (Comparative monotonicity)**: swapping the two sides of a `greater/less` relation must invert the truth value.  
   - **MR3 (Numeric scaling)**: multiplying both sides of a numeric equality by a constant preserves truth.  
   - **MR4 (Ordering transitivity)**: if `before(A,B)` and `before(B,C)` are in the prompt, then `before(A,C)` must hold in the answer.  
   For each MR, build a small NumPy matrix that encodes the relation (e.g., an adjacency matrix for ordering). Propagate truth values through these matrices using Boolean matrix multiplication (`np.logical_or.reduce(np.logical_and(W[:,None], M), axis=0)`) until a fixed point is reached. Each propagation step corresponds to a *global broadcast* of newly ignited propositions.  

4. **Scoring** – Let `S` be the number of MRs satisfied after propagation, `V` the number violated. Raw score = `S - V`. Normalise to `[0,1]` by dividing by the total number of MRs examined. The final score is returned as a float.  

**Structural features parsed**  
Negations (`not`, `no`), comparatives (`more than`, `less than`, `>`, `<`), conditionals (`if … then …`, `unless`), numeric values and units, ordering relations (`first`, `last`, `before`, `after`, `earlier`, `later`), causal cues (`because`, `leads to`, `results in`), conjunction/disjunction (`and`, `or`).  

**Novelty**  
Purely symbolic tools often rely on hand‑coded rule bases or SAT solvers; neural approaches use embeddings. The presented combo — compositional semantic DAG, a Global Workspace‑style broadcast via iterative Boolean matrix propagation, and a systematic metamorphic‑relation test suite — is not found in existing public reasoning evaluators. It bridges Fregean compositionality, a cognitive‑inspired activation mechanism, and MR‑based oracle‑free testing, making it novel in the scope of lightweight, numpy‑only evaluators.  

**Ratings**  
Reasoning: 7/10 — captures logical, numeric, and relational structure but lacks deeper abductive or analogical reasoning.  
Metacognition: 5/10 — workspace provides basic monitoring of ignited facts, yet no higher‑level self‑assessment of uncertainty.  
Hypothesis generation: 4/10 — generates alternative answers only via predefined MRs; limited creative hypothesis formation.  
Implementability: 9/10 — relies solely on regex, NumPy Boolean ops, and plain‑Python control flow; straightforward to code and debug.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Global Workspace Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositional Semantics**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Category Theory + Global Workspace Theory + Epistemology (accuracy: 0%, calibration: 0%)
- Category Theory + Global Workspace Theory + Network Science (accuracy: 0%, calibration: 0%)
- Category Theory + Renormalization + Global Workspace Theory (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

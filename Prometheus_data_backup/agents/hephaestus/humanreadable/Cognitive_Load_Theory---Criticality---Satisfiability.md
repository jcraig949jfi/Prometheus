# Cognitive Load Theory + Criticality + Satisfiability

**Fields**: Cognitive Science, Complex Systems, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:43:29.045871
**Report Generated**: 2026-04-02T04:20:11.716040

---

## Nous Analysis

The algorithm builds a lightweight SAT model from each candidate answer, then blends satisfiability, criticality proximity, and cognitive‑load weighting into a single score.

**Data structures**  
- `var_map: dict[str, int]` maps each extracted proposition (e.g., “X>5”, “¬Y”, “if A then B”) to a variable ID.  
- `clauses: List[Set[int]]` stores CNF clauses as sets of signed integers (positive = literal, negative = negated literal).  
- `load_weights: Dict[int, Tuple[float,float,float]]` holds intrinsic, extraneous, germane load per variable (computed from clause length, duplication, and semantic depth).  

**Operations**  
1. **Structural parsing** – regex extracts atomic propositions and connects them with logical operators (¬, ∧, ∨, →). Each proposition becomes a variable; each connective yields a clause (e.g., “if A then B” → ¬A ∨ B).  
2. **Unit propagation** – a DPLL‑style unit‑propagation loop iteratively assigns forced literals, simplifies clauses, and detects contradictions.  
3. **Unsat core approximation** – if a conflict occurs, the algorithm records the set of clauses involved in the propagation trail; a simple hitting‑set reduction yields an approximate minimal unsat core.  
4. **Sat score** – `sat = 1 - (|unsat_core| / |clauses|)`.  
5. **Criticality factor** – compute clause‑to‑variable ratio α = |clauses|/|vars|; criticality = 4·α·(1‑α), peaking at α=0.5 (the SAT phase transition).  
6. **Cognitive load** – intrinsic load = mean clause length; extraneous load = fraction of duplicate or tautological clauses; germane load = 1‑(intrinsic+extraneous)/2. Load = intrinsic + extraneous – germane (lower is better).  
7. **Final score** – `score = sat * criticality / (load + ε)` with ε=1e‑6 to avoid division by zero.

**Structural features parsed**  
Negations, comparatives (`>`, `<`, `=`), conditionals (`if … then …`), numeric constants, causal cues (`because`, `leads to`), ordering relations (`before`, `after`), and conjunctive/disjunctive connectives.

**Novelty**  
While SAT‑based consistency checking and cognitive‑load weighting appear separately in tutoring systems, coupling them with a criticality‑proximity term that measures distance to the SAT phase transition is not documented in the literature, making the triple combination novel.

Reasoning: 7/10 — captures logical consistency and difficulty but relies on approximate unsat core.  
Metacognition: 6/10 — load proxy reflects mental effort yet omits learner‑specific state.  
Hypothesis generation: 5/10 — limited to extracting explicit propositions; no generative abductive step.  
Implementability: 8/10 — uses only regex, dicts, sets, and simple loops; readily coded in numpy‑free Python.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

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

# Dual Process Theory + Emergence + Pragmatics

**Fields**: Cognitive Science, Complex Systems, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:18:00.361613
**Report Generated**: 2026-04-02T04:20:11.695041

---

## Nous Analysis

**Algorithm**  
The scorer works in two phases that mirror System 1 (fast) and System 2 (slow).  

*Data structures*  
- `tokens`: list of strings from regex‑based tokenisation (preserves punctuation).  
- `props`: dictionary mapping each extracted propositional atom (e.g., “X > Y”, “¬P”, “cause(A,B)”) to a unique integer ID.  
- `constraints`: list of tuples `(op, id1, id2)` where `op` ∈ {‘=’, ‘≠’, ‘<’, ‘>’, ‘→’, ‘∧’} representing logical relations extracted via regex patterns for comparatives, conditionals, causal clauses, and ordering.  
- `fast_scores`: numpy array of shape `(n_candidates,)` for System 1 heuristics.  
- `slow_scores`: numpy array of same shape for System 2 deliberation.

*Operations*  
1. **Fast pass (System 1)** – For each candidate, compute a feature vector `f` using only numpy:  
   - counts of negations (`¬`), modality words (`must`, `might`), numeric constants, and quantifier scope depth.  
   - Apply a fixed weight vector `w_fast` (learned offline or set heuristically) → `fast_scores = f @ w_fast`.  
2. **Slow pass (System 2)** – Build a propositional constraint graph from `props` and `constraints`.  
   - Perform unit propagation and transitive closure (Floyd‑Warshall on the ordering sub‑graph) using only numpy matrix operations.  
   - Detect contradictions: if both `X → Y` and `X → ¬Y` are derivable, assign a penalty; otherwise compute a coherence score as the fraction of satisfied constraints.  
   - `slow_scores = coherence * w_slow`.  
3. **Emergent macro score** – Combine the two levels: `score = fast_scores + slow_scores`. The macro property (overall reasoning quality) emerges from the micro‑level constraint satisfiability, embodying weak emergence.

**Structural features parsed**  
Negations, modal auxiliaries, comparatives (`>`, `<`, `≥`, `≤`), equality, conditionals (`if … then …`), causal verbs (`cause`, `lead to`), temporal ordering (`before`, `after`), quantifiers (`all`, `some`, `none`), and numeric expressions.

**Novelty**  
While dual‑process, emergent constraint solving, and pragmatic enrichment each appear in neuro‑symbolic or formal semantics work, the specific combination — using only numpy/std‑lib to run a fast heuristic layer followed by a deterministic constraint‑propagation layer that yields an emergent coherence score — has not been published as a standalone evaluation tool.

**Rating lines**  
Reasoning: 8/10 — captures logical structure and consistency but lacks deep semantic understanding.  
Metacognition: 6/10 — system can monitor its own fast/slow balance via score disparity, yet no explicit self‑reflection loop.  
Hypothesis generation: 5/10 — derives implied propositions via propagation, but does not rank alternative abductive hypotheses.  
Implementability: 9/10 — relies solely on regex, numpy arrays, and basic matrix ops; no external dependencies.

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

# Active Inference + Neural Oscillations + Satisfiability

**Fields**: Cognitive Science, Neuroscience, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:53:39.385422
**Report Generated**: 2026-03-27T16:08:16.443671

---

## Nous Analysis

**Algorithm**  
We build a lightweight SAT‑based scorer that treats each candidate answer as a set of provisional truth assignments to propositions extracted from the question and answer text.  

1. **Parsing & data structures** – Using regex we extract atomic propositions (e.g., “X > Y”, “A causes B”, “¬C”) and encode them as integer indices. A clause matrix `C` of shape `(n_clauses, n_vars)` holds literals in {-1,0,1} (0 = absent, 1 = positive, -1 = negated). A weight vector `w` (numpy array) stores clause importance derived from linguistic cues (e.g., comparatives get higher weight).  

2. **Oscillatory constraint propagation** – We simulate two coupled rhythms: a fast “gamma” step that performs unit‑propagation on the current clause set (pure NumPy vectorized scan) and a slow “theta” step that modulates clause weights based on the global error (free‑energy) after each gamma sweep. Concretely:  
   - Gamma: `changed = True; while changed:` compute satisfied = `np.any(C * assign[:,None] == 1, axis=1) | np.any(C * assign[:,None] == -1, axis=0)`, update `assign` via unit clauses, set `changed` if any flip.  
   - Theta: compute expected free energy `F = np.sum(w * np.maximum(0, -satisfied.astype(float))) - α * entropy(assign)`, then update `w ← w * (1 + β * F)` (β small). Iterate for a fixed number of theta cycles (e.g., 5).  

3. **Scoring** – After convergence, the free‑energy `F` quantifies how poorly the candidate answer satisfies the extracted constraints. Lower `F` → higher score. We normalize scores across candidates: `score = -F / np.max(-F)` (so best = 1).  

**Structural features parsed** – Negations (`not`, `no`), comparatives (`greater than`, `less than`, `≥`, `≤`), conditionals (`if … then …`, `unless`), causal claims (`because`, `leads to`, `results in`), ordering relations (`before`, `after`, `first`, `last`), numeric equality/inequality, and conjunctive/disjunctive connectives (`and`, `or`).  

**Novelty** – Pure SAT‑based QA exists, and oscillatory neural models have been applied to constraint satisfaction, while active inference supplies a decision‑theoretic cost function. The tight coupling of gamma‑style unit propagation with theta‑weighted free‑energy minimization, all implemented with NumPy, does not appear in prior work, making the combination novel.  

**Ratings**  
Reasoning: 8/10 — The method directly evaluates logical consistency of answers against extracted constraints, capturing core reasoning steps.  
Metacognition: 6/10 — Free‑energy provides a global uncertainty measure, but the algorithm lacks explicit self‑reflection on its own parsing errors.  
Hypothesis generation: 5/10 — It scores given candidates; generating new hypotheses would require additional search machinery not built in.  
Implementability: 9/10 — Only NumPy and stdlib are needed; all operations are vectorized regex parsing, matrix multiplication, and simple loops.

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

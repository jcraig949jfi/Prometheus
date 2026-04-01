# Dual Process Theory + Free Energy Principle + Sensitivity Analysis

**Fields**: Cognitive Science, Theoretical Neuroscience, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T10:15:16.592969
**Report Generated**: 2026-03-31T19:17:41.610789

---

## Nous Analysis

The algorithm treats each candidate answer as a set of propositions extracted from the prompt and the answer itself. **Data structures** are:  
- `Proposition` objects stored in a NumPy‑structured array with fields `id` (int), `type` (enum: atomic, negated, comparative, causal, numeric), `truth` (bool or float), `value` (float for numerics).  
- An adjacency matrix `A` (bool, shape [n,n]) where `A[i,j]=1` encodes a logical dependency extracted from conditionals (“if X then Y”), causal cues (“X leads to Y”), or transitive relations (“X > Y → X > Z”).  
- A prior potential vector `π` (uniform) and a likelihood potential `L` derived from the answer’s proposition truth values.

**Operations** (all using only NumPy and the stdlib):  
1. **Structural parsing** – regex patterns pull out negations (`not`, `no`), comparatives (`>`, `<`, `=`), conditionals (`if … then …`), causal keywords (`because`, `leads to`, `results in`), numeric tokens, and ordering phrases (`more than`, `less than`, `before`, `after`). Each match creates a Proposition and populates `A`.  
2. **Constraint propagation** – compute the transitive closure of `A` with Floyd‑Warshall (`np.maximum.reduce(np.minimum.reduce(...))`) to derive all implied truths.  
3. **System 1 heuristic** – fast surface score `h = cosine(tfidf(prompt), tfidf(answer))` using only term‑frequency vectors from the stdlib.  
4. **System 2 free‑energy** – prediction error `e = Σ |π_i – L_i|` where `L_i` is the truth value after propagation; free energy `F = e + H` with entropy `H = -Σ π_i log π_i` (uniform prior → constant).  
5. **Sensitivity analysis** – randomly perturb each proposition’s truth (flip Boolean or add ε~N(0,0.01) to numerics) 20 times, recompute `F`, and take the standard deviation `s`. High `s\) indicates fragile reasoning.  
6. **Final score** – `score = w1·h – w2·F – w3·s` (weights sum to 1, tuned on a validation set). The answer with the highest score is selected.

**Structural features parsed**: negations, comparatives, conditionals, causal language, numeric values, ordering relations (greater/less, before/after), and explicit equality statements.

**Novelty**: While each component—dual‑process heuristics, variational free‑energy minimization, and sensitivity probing—has precedents in cognitive science and ML, their conjunction into a single, numpy‑only scoring pipeline that intertwines fast surface heuristics with deliberate constraint‑based error and robustness analysis has not been reported in existing reasoning‑evaluation tools.

Reasoning: 7/10 — captures logical consistency and prediction error but relies on hand‑crafted regexes that may miss complex syntax.  
Metacognition: 6/10 — the System 1/System 2 split gives a rudimentary self‑monitoring signal via the heuristic vs. free‑energy trade‑off.  
Hypothesis generation: 5/10 — the method evaluates given answers rather than generating new hypotheses; it can rank candidates but does not propose novel explanations.  
Implementability: 8/10 — all steps use only NumPy and the Python standard library, making deployment straightforward and dependency‑free.

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

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-31T19:15:17.489763

---

## Code

*No code was produced for this combination.*

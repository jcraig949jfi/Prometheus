# Dual Process Theory + Network Science + Multi-Armed Bandits

**Fields**: Cognitive Science, Complex Systems, Game Theory
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:18:06.429472
**Report Generated**: 2026-03-31T19:15:02.843534

---

## Nous Analysis

The algorithm builds a propositional graph from each candidate answer, assigns fast heuristic rewards via structural feature extraction, then refines those rewards through slow deliberative constraint propagation, while a multi‑armed bandit allocates computational effort to the most promising answers.

**Data structures**  
- `props`: list of dictionaries, each with keys `text`, `type` (negation, comparative, conditional, numeric, causal, ordering), and `span`. Extracted by regex patterns over the answer string.  
- `adj`: `numpy.ndarray` of shape (n,n) where `adj[i,j]=1` if proposition *i* logically supports *j* (e.g., antecedent→consequent for conditionals, same subject for comparatives, shared entity for causal). Built deterministically from `props`.  
- `heuristic`: `numpy.ndarray` of shape (n,) containing a weighted sum of feature matches (e.g., +1 for correct negation handling, +0.5 for numeric equality, –1 for mismatched causal direction). Weights are fixed scalars.  
- `score`: `numpy.ndarray` (n,) holding the current deliberative belief for each proposition.  
- For each answer arm *a*: `emp_mean[a]` (average reward), `pulls[a]` (number of deliberative iterations allocated), `ucb[a]` (Upper Confidence Bound).

**Operations**  
1. **Fast stage (System 1)**: compute `heuristic` for each answer in O(|props|) using numpy vectorized operations on the feature matrix.  
2. **Slow stage (System 2)**: iteratively update `score` until convergence or a max‑step limit:  
   `score ← α·heuristic + (1‑α)·(adj.T @ score) / (adj.T @ np.ones(n) + ε)`  
   where α∈[0,1] balances prior heuristic and network influence; `@` is matrix multiplication. This implements belief propagation (constraint propagation) over the logical graph.  
3. **Answer‑level reward**: `reward[a] = np.sum(score * coverage[a])`, where `coverage[a]` is a binary vector indicating which propositions appear in answer *a*.  
4. **Bandit allocation**: after each slow‑stage iteration, update `emp_mean[a]` with the latest `reward[a]`, increment `pulls[a]`, and recompute `ucb[a] = emp_mean[a] + c·sqrt(log(total_pulls)/pulls[a])`. The next iteration focuses computational budget on the arm with highest `ucb`.  

**Structural features parsed**  
- Negations (`not`, `no`)  
- Comparatives (`greater than`, `less than`, `equal to`)  
- Conditionals (`if … then …`, implication)  
- Numeric values and units  
- Causal claims (`because`, `leads to`, `results in`)  
- Ordering relations (`before`, `after`, `first`, `last`)  
- Conjunctions/disjunctions (`and`, `or`)  

**Novelty**  
Pure graph‑based reasoning or pure bandit‑based answer selection exist, but the explicit coupling of a dual‑process heuristic/deliberative loop with a UCB‑driven allocation of deliberative steps to individual answers has not been described in the literature. The approach thus combines three well‑studied paradigms in a new scoring pipeline.

**Ratings**  
Reasoning: 7/10 — captures logical structure via graph propagation but relies on hand‑crafted feature weights and limited inference depth.  
Metacognition: 6/10 — distinguishes fast heuristic vs slow deliberative updates, yet lacks explicit self‑monitoring of confidence beyond the bandit bound.  
Implementability: 9/10 — uses only regex, numpy arrays, and standard‑library loops; no external dependencies or training required.  
Hypothesis generation: 5/10 — the bandit drives exploration of answer candidates, but the hypothesis space is confined to extracted propositions, limiting creative abductive leaps.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
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

**Forge Timestamp**: 2026-03-31T19:14:52.595529

---

## Code

*No code was produced for this combination.*

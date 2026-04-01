# Falsificationism + Sparse Coding + Satisfiability

**Fields**: Philosophy, Neuroscience, Logic
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T11:39:12.930210
**Report Generated**: 2026-03-31T16:26:32.030507

---

## Nous Analysis

The algorithm builds a sparse logical representation of the prompt and each candidate answer, then scores candidates by how few new conflicts they introduce when added to a background knowledge base, using unit‑propagation‑based SAT solving as a falsification test.

**Data structures**  
- `lit2id`: dictionary mapping each extracted literal (e.g., `Bird`, `¬Flies(x)`, `Weight>5`) to an integer index.  
- `KB`: list of clauses, each clause a Python list of signed literal IDs (positive for asserted, negative for negated).  
- `cand_vec`: NumPy uint8 array of shape `(num_literals,)` with 1s at indices of literals present in the candidate; all other entries 0 (sparse coding).  
- `assign`: NumPy int8 array of same shape, values `-1` (unassigned), `0` (false), `1` (true) during propagation.

**Operations**  
1. **Parsing** – regex extracts literals and their polarity from the prompt and each candidate; each literal is mapped via `lit2id`.  
2. **Clause construction** – prompt sentences are converted to clauses (e.g., “If Bird then Flies” → `[¬Bird, Flies]`).  
3. **Scoring a candidate** –  
   a. Initialize `assign` to `-1`.  
   b. Insert unit clauses from `cand_vec` (set corresponding literals to true).  
   c. Run unit propagation: repeatedly scan `KB`; if a clause has all literals false except one unassigned, assign that literal to satisfy the clause; if a clause becomes all false, record a conflict and stop propagation for that candidate.  
   d. `conflict_count` = number of clauses that became unsatisfied before propagation halted (approximate unsatisfiable core size).  
   e. Raw score = `1 / (1 + conflict_count)`.  
   f. Final score = raw score × exp(−‖cand_vec‖₀ / τ), where ‖·‖₀ is the L0 norm (number of active literals) and τ a sparsity‑temperature constant, rewarding sparse candidate explanations.

**Structural features parsed** – negations (`not`, `no`), comparatives (`greater than`, `less than`), conditionals (`if … then …`), causal cues (`because`, `leads to`), ordering relations (`before`, `after`, `precedes`), numeric thresholds and equality statements.

**Novelty** – While sparse coding and SAT‑based reasoning appear separately in neuroscience and formal verification, their joint use for evaluating answer correctness—using sparsity as a prior and conflict count as a falsification score—has not been reported in existing QA or explanation‑ranking work.

**Ratings**  
Reasoning: 8/10 — captures logical consistency and falsifiability directly, but relies on shallow parsing that may miss deep semantic nuance.  
Metacognition: 6/10 — the method can estimate its own uncertainty via conflict count, yet lacks explicit self‑reflection on parsing failures.  
Hypothesis generation: 7/10 — generates candidate explanations implicitly via literal sets; however, it does not propose novel hypotheses beyond the given answer space.  
Implementability: 9/10 — uses only regex, NumPy arrays, and straightforward unit propagation; no external libraries or training required.

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

**Forge Timestamp**: 2026-03-31T16:25:20.723310

---

## Code

*No code was produced for this combination.*

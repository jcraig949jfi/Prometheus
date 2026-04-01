# Multi-Armed Bandits + Model Checking + Metamorphic Testing

**Fields**: Game Theory, Formal Methods, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-28T13:39:37.569827
**Report Generated**: 2026-03-31T16:23:53.891780

---

## Nous Analysis

**Algorithm**  
We build a hybrid scorer that treats each candidate answer as a “arm” in a multi‑armed bandit problem, where the reward of pulling an arm is the degree to which the answer satisfies logical constraints extracted from the prompt and remains stable under metamorphic transformations of the prompt.

1. **Prompt parsing → constraint set**  
   - Use regular expressions to extract atomic propositions, comparatives (`>`, `<`, `=`), conditionals (`if … then …`), ordering keywords (`before`, `after`, `when`), negations (`not`, `no`), and causal cues (`because`, `leads to`).  
   - Each extracted element becomes a clause in conjunctive normal form (CNF).  
   - Store clauses as a list of tuples `[(lit_id, polarity), …]` where `lit_id` indexes a proposition symbol.

2. **Finite‑state model**  
   - Construct a deterministic finite‑state automaton (FSA) that encodes all worlds consistent with the prompt clauses.  
   - States are bit‑vectors of length *n* (number of propositions).  
   - Transitions correspond to setting a proposition true/false while respecting clause satisfaction (checked via a pre‑computed lookup table).  
   - Model checking is a simple BFS/DFS over the FSA to verify whether a candidate answer’s proposition assignment reaches an accepting state; the number of violated clauses is counted (`violations`).

3. **Metamorphic relations (MRs)**  
   - Define a fixed set of MRs as functions that transform the prompt string:  
     *Swap*: exchange two symmetric entities.  
     *Negate*: insert/delete a `not`.  
     *Scale*: multiply numeric constants by 2.  
     *Reverse order*: invert `before/after`.  
   - Each MR is an arm of the bandit.

4. **Bandit‑driven MR selection**  
   - Maintain for each arm *i*: empirical mean reward `μ_i` (numpy array) and pull count `n_i`.  
   - Reward for pulling arm *i* on a candidate answer = `-Δviolations`, i.e., reduction in violations after applying the MR and re‑checking the answer.  
   - At each scoring iteration, select the arm with highest Upper Confidence Bound: `UCB_i = μ_i + c * sqrt(log(total_pulls)/n_i)`.  
   - Update `μ_i` and `n_i` with observed reward.

5. **Scoring logic**  
   - Base score `S_base = -violations`.  
   - Bandit bonus `S_bandit = α * (average μ_i over arms pulled for this answer)`, where α ∈ [0,1] balances exploration vs. exploitation.  
   - Final score `S = S_base + S_bandit`.  
   - Higher `S` indicates better logical consistency and stability under meaningful prompt perturbations.

**Structural features parsed**  
Negations, comparatives, conditionals, ordering/temporal keywords, numeric constants, causal conjunctions, and symmetric entity pairs (e.g., “X vs. Y”).

**Novelty**  
While model checking, metamorphic testing, and bandit algorithms each appear separately in verification, testing, and adaptive sampling literature, their tight integration — using a bandit to allocate metamorphic‑testing budget while checking answers against an explicit‑state model — has not been applied to scoring reasoning answers. It adapts ideas from property‑based testing and adaptive test generation but is novel in this specific scoring pipeline.

**Ratings**  
Reasoning: 8/10 — The method directly evaluates logical consistency and stability, capturing core reasoning demands.  
Metacognition: 6/10 — Limited self‑reflection; the bandit tracks reward but does not reason about its own uncertainty beyond UCB.  
Hypothesis generation: 7/10 — MRs act as hypothesis generators about how answers should change under prompt perturbations.  
Implementability: 9/10 — All components rely on regex, numpy arrays, and explicit‑state BFS; no external libraries or neural models needed.

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

**Forge Timestamp**: 2026-03-31T16:23:43.889463

---

## Code

*No code was produced for this combination.*

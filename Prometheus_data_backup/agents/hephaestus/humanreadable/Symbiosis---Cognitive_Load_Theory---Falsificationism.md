# Symbiosis + Cognitive Load Theory + Falsificationism

**Fields**: Biology, Cognitive Science, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T00:41:30.940287
**Report Generated**: 2026-03-27T06:37:41.914634

---

## Nous Analysis

**Algorithmic core**  
1. **Parsing stage** – Using only `re` we extract propositional atoms and logical operators from the prompt and each candidate answer:  
   - Atoms: noun phrases, numeric constants, named entities.  
   - Operators: `if … then …` (implication), `because` / `causes` (causal), `greater/less than` (comparative), `equals` (equational), `not` (negation), `and` / `or` (conjunction/disjunction).  
   Each atom gets a unique integer ID; we store its textual form in a list `atoms`.  

2. **Graph construction** – Build a directed adjacency list `graph[id] = set(target_ids)` for every implication/causal edge. Separate sets hold:  
   - `neg[id]` – atoms explicitly negated.  
   - `cmp[(id1, id2, op)]` – comparative/numeric relations.  
   - `mutual[id]` – set of atoms that appear bidirectionally (symbiosis signal).  

3. **Bounded forward‑chaining (cognitive load)** – Choose a working‑memory capacity `W` (e.g., 7). Initialize a frontier with atoms directly asserted in the answer. While frontier not empty and `len(active) ≤ W`:  
   - Pop an atom `a`.  
   - For each `b in graph[a]` add `b` to `active` and frontier.  
   - Apply modus ponens on stored conditionals (if both antecedent and implication present, add consequent).  
   - Propagate comparatives via simple transitivity (e.g., `a > b` & `b > c → a > c`).  
   - If adding a proposition would exceed `W`, halt and increment a load‑penalty counter.  

4. **Falsificationist scoring** – After propagation, check for contradictions:  
   - If both `x` and `¬x` are in `active`, count one successful falsification.  
   - Let `F` be the number of such contradictions.  

5. **Symbiosis reward** – Compute the proportion of edges that are reciprocal:  
   - `S = ( Σ_{a} |mutual[a]| ) / (2 * |E|)`, where `|E|` is total implication/causal edges.  
   - Higher `S` indicates mutually supportive statements (mutualism/holobiont analogy).  

6. **Final score** – `score = α * F + β * S - γ * load_penalty`, with fixed weights (e.g., α=2, β=1.5, γ=1). The candidate with the highest score is selected.

**Structural features parsed**  
- Negations (`not`, `no`, `never`).  
- Conditionals (`if … then …`, `provided that`).  
- Causals (`because`, `causes`, `leads to`).  
- Comparatives (`greater than`, `less than`, `at least`).  
- Numeric values and units.  
- Ordering relations (`before`, `after`, `first`, `last`).  
- Conjunctions/disjunctions (`and`, `or`).  

**Novelty**  
Existing reasoning scorers rely on pure similarity (bag‑of‑words, TF‑IDF) or on full‑scale logic solvers. This design uniquely blends three independent principles: (1) a symbiosis‑inspired mutual‑support metric, (2) a cognitively bounded forward‑chaining process that mirrors working‑memory limits, and (3) a falsificationist reward for deriving contradictions. No published tool combines all three in a single, lightweight, numpy‑only pipeline.

**Ratings**  
Reasoning: 8/10 — captures logical inference, contradiction detection, and mutual support, though limited to shallow syntactic patterns.  
Metacognition: 7/10 — explicit working‑memory bound models self‑regulation of load, but lacks higher‑order reflection on strategy.  
Hypothesis generation: 6/10 — generates derived propositions via forward chaining, yet does not rank or prioritize novel hypotheses beyond contradiction checks.  
Implementability: 9/10 — relies only on regex, numpy for simple vector ops, and Python stdlib; easy to embed in an evaluation harness.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 7/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Symbiosis**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Falsificationism**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 34% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.


Similar combinations that forged successfully:
- Apoptosis + Falsificationism + Self-Organized Criticality (accuracy: 0%, calibration: 0%)
- Attention Mechanisms + Predictive Coding + Falsificationism (accuracy: 0%, calibration: 0%)
- Cellular Automata + Cognitive Load Theory + Phenomenology (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

**Status**: Scrapped
**Reason**: api_call_failed

**Forge Timestamp**: 2026-03-26T18:44:01.015388

---

## Code

*No code was produced for this combination.*

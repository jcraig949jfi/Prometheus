# Cognitive Load Theory + Pragmatics + Mechanism Design

**Fields**: Cognitive Science, Linguistics, Economics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T19:49:33.984361
**Report Generated**: 2026-03-27T05:13:39.712280

---

## Nous Analysis

1. **Algorithm** – *Constraint‑Propagating Pragmatic Scorer (CPPS)*  
   - **Input**: prompt `P`, list of candidate answers `A = [a₁,…,a_k]`.  
   - **Data structures**  
     - `tokens`: list of strings from regex `\w+|[^\w\s]` applied to each text.  
     - `props`: dict `{id: (type, args)}` where `type ∈ {atom, neg, cond, caus, comp, num, quant}` and `args` are the constituent token indices.  
     - `graph`: boolean numpy adjacency matrix `G ∈ {0,1}^{n×n}` (`n = len(props)`) where `G[i,j]=1` iff proposition `i` entails proposition `j` (extracted from explicit “if … then …”, causal cues, or transitive comparatives).  
     - `feat`: numpy vector `[len, neg_cnt, comp_cnt, caus_cnt, num_cnt, quant_cnt]` for each answer.  
   - **Operations**  
     1. **Extraction** – regex patterns capture:  
        - Negations (`not`, `no`, `-n't`).  
        - Comparatives (`more than`, `less than`, `-er`).  
        - Conditionals (`if`, `unless`, `provided that`).  
        - Causal connectives (`because`, `since`, `therefore`).  
        - Numeric values (`\d+(\.\d+)?`).  
        - Ordering quantifiers (`all`, `some`, `none`).  
        Each match creates a proposition entry in `props`.  
     2. **Graph construction** – for every conditional `if X then Y` set `G[id(X), id(Y)]=1`; for causal `X because Y` set `G[id(Y), id(X)]=1`; for comparatives `X > Y` set `G[id(X), id(Y)]=1`.  
     3. **Constraint propagation** – compute transitive closure with Floyd‑Warshall using numpy: `reach = (np.maximum.accumulate(G, axis=0) | np.maximum.accumulate(G, axis=1)).astype(bool)`.  
     4. **Consistency score** – let `E` be the set of proposition IDs entailed by the prompt (derived similarly). For each answer compute `c = |reach[answer_ids] ∩ E| / |E|`.  
     5. **Load penalty** – extraneous load approximated by normalized feature vector: `l = (feat·w_ex)/‖feat‖` where `w_ex = [0,1,0,0,0,0]` (negations & hedges count).  
     6. **Germane reward** – relevance per Grice’s maxim of quantity/relevance: `g = (feat·w_gr)/‖feat‖` where `w_gr = [0,0,1,1,1,1]` (comparatives, causals, numerics, quantifiers).  
     7. **Mechanism‑design utility** – designer wants truthful answers with minimal effort: `u = α·c – β·l + γ·g – δ·(len/ max_len)`. Choose `α,β,γ,δ` so that maximizing `u` incentivizes reporting the correct entailment set (truth‑telling is a dominant strategy).  
   - **Output**: score `s_i = (u_i - min(u))/(max(u)-min(u))` for each candidate, returned as a numpy array.  

2. **Parsed structural features** – negations, comparatives, conditionals, causal connectives, numeric values, ordering relations (“more than”, “less than”), quantifiers (“all”, “some”, “none”), and temporal markers (“before”, “after”).  

3. **Novelty** – Pure logic‑based scorers exist (e.g., LogicNLP) and cognitive‑load metrics have been added to rubrics, but coupling them with a mechanism‑design utility function that explicitly enforces incentive compatibility for truthful reporting is not present in the literature. Hence the combination is novel.  

**Ratings**  
Reasoning: 7/10 — solid logical closure and consistency measurement, but limited handling of deep semantics and world knowledge.  
Metacognition: 5/10 — the tool does not model self‑monitoring or confidence calibration beyond the load penalty.  
Hypothesis generation: 6/10 — transitive closure yields implicit inferences, yet no abductive or creative hypothesis formation.  
Implementability: 9/10 — relies only on regex, numpy matrix ops, and basic arithmetic; no external libraries or training required.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 9/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Mechanism Design**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 38% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.

- Cognitive Load Theory + Pragmatics: strong positive synergy (+0.267). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Cognitive Load Theory + Mechanism Design: strong positive synergy (+0.188). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.
- Mechanism Design + Pragmatics: strong positive synergy (+0.174). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Cognitive Load Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Fractal Geometry + Cognitive Load Theory + Mechanism Design (accuracy: 0%, calibration: 0%)
- Theory of Mind + Pragmatics + Mechanism Design (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

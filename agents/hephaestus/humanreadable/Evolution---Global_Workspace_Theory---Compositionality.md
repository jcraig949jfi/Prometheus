# Evolution + Global Workspace Theory + Compositionality

**Fields**: Biology, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T18:49:18.460226
**Report Generated**: 2026-03-27T06:37:47.458946

---

## Nous Analysis

The algorithm builds a **compositional proposition graph** from each prompt and candidate answer, then runs an **evolutionary global‑workspace dynamics** to measure how well the answer’s propositions ignite and persist.

**Data structures**  
- `Prop`: a NumPy structured array with fields `(pred_id: int, arg1: int, arg2: int, polarity: int8, weight: float32)`. `pred_id` indexes a predicate extracted by regex (e.g., “greater_than”, “cause”, “equal”). `arg1/arg2` are token IDs of the arguments; for unary predicates `arg2 = -1`. `polarity` = +1 for affirmative, –1 for negated. `weight` is the current fitness.  
- `Graph`: adjacency matrix `A` (bool) where `A[i,j]=True` if proposition *i* can infer *j* via a rule (modus ponens, transitivity, numeric constraint).  
- `Workspace`: a boolean mask `W` indicating which propositions are currently “globally broadcast”.

**Operations**  
1. **Parsing** – Regex extracts predicates, arguments, negations, comparatives (`>`, `<`, `=`), conditionals (`if … then …`), causal cues (`because`, `leads to`), and numeric literals. Each extracted clause becomes a row in `Prop`.  
2. **Rule construction** –  
   - *Modus ponens*: if `Prop[i]` is `P → Q` and `Prop[j]` matches `P`, set `A[i,k]` where `k` indexes `Q`.  
   - *Transitivity*: for ordering predicates (`greater_than`, `less_than`) compute Floyd‑Warshall on the numeric arg values to fill implied ordering edges.  
   - *Numeric evaluation*: gather all linear constraints (e.g., `x > 5`, `y = 2x`) into a matrix `C` and vector `b`; use `np.linalg.lstsq` to obtain a least‑squares solution; propositions whose numeric args satisfy the solution within tolerance get an incoming edge from a hidden “constraint” node.  
3. **Evolutionary workspace dynamics** – Initialize `W` with propositions directly present in the prompt (weight = 1.0). For `G` generations (e.g., 10):  
   - **Selection**: compute fitness `f_i = weight_i * (1 + 0.1 * sum(W))`.  
   - **Reproduction**: copy the top‑k propositions; apply mutation by adding Gaussian noise (`σ=0.05`) to `weight` and randomly flipping polarity with probability 0.02.  
   - **Ignition**: set `W` to the union of currently active propositions and all nodes reachable via one step of `A` from any active node (broadcast).  
   - **Decay**: multiply all weights by 0.99 to simulate drift.  
4. **Scoring** – After `G` generations, the score for a candidate answer is the fraction of its propositions that are in `W` multiplied by their average final weight.

**Structural features parsed** – negations, comparatives, conditionals, causal connectives, numeric values, equality/inequality, ordering relations, conjunctions/disjunctions, universal/existential quantifiers (via “all”, “some”).

**Novelty** – The triple blend is not a direct replica of existing systems. Evolutionary fitness selection with mutation mirrors memetic algorithms, but coupling it to a global‑workspace broadcast mechanism and a strictly compositional semantic graph is uncommon; most neuro‑symbolic hybrids use static logical parsers or neural attention, not an explicit ignition‑selection loop. Thus the approach is novel in its specific integration.

**Ratings**  
Reasoning: 7/10 — The algorithm captures inference via constraint propagation and evolutionary selection, offering a mechanistic scoring that goes beyond surface similarity.  
Metacognition: 5/10 — It monitors its own broadcast state and adjusts weights, but lacks higher‑order reflection on its search strategy.  
Hypothesis generation: 6/10 — Mutation creates new proposition variants, enabling limited hypothesis exploration, though guided generation is weak.  
Implementability: 8/10 — Relies only on regex, NumPy linear algebra, and basic data structures; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 7/10 |
| Metacognition | 5/10 |
| Hypothesis Generation | 6/10 |
| Implementability | 8/10 |
| **Composite** | **6.0** |

**Novelty**: novel
**High Potential**: No

---

## Coeus Causal Intelligence

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Evolution**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Global Workspace Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Compositionality**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Compositionality + Global Workspace Theory: strong positive synergy (+0.293). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Global Workspace Theory + Criticality + Compositionality (accuracy: 0%, calibration: 0%)
- Bayesian Inference + Evolution + Criticality (accuracy: 0%, calibration: 0%)
- Category Theory + Global Workspace Theory + Epistemology (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

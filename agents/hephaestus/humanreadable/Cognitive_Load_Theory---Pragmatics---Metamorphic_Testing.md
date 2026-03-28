# Cognitive Load Theory + Pragmatics + Metamorphic Testing

**Fields**: Cognitive Science, Linguistics, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-26T13:14:40.672326
**Report Generated**: 2026-03-27T05:13:38.160084

---

## Nous Analysis

**Algorithm**  
1. **Parsing stage** – Using only regex and the stdlib, extract propositional atoms from the prompt and each candidate answer. Each atom is a tuple `(pred, args, mods)` where `pred` is the verb/noun phrase, `args` are noun‑phrase arguments, and `mods` is a bit‑mask encoding detected structural features: negation, comparative (`> < = ≤ ≥`), conditional (`if … then`), causal (`because`, `leads to`), ordering (`before/after`, `more/less`), numeric value, and quantifier. Store all atoms in a NumPy structured array `A` of shape `(N,)` with fields for each feature (bool or float).  

2. **Metamorphic relation matrix** – Define a set of binary metamorphic relations (MRs) that must hold between any two answers *x* and *y*:  
   - *Monotonicity*: if `x` contains a stronger comparative claim than `y` (e.g., “more than 5” vs “more than 3”), then the score of `x` must be ≥ score of `y`.  
   - *Invariance under negation*: swapping a negation flips the truth‑value expectation.  
   - *Conditional transitivity*: if `x` asserts “if P then Q” and `y` asserts P, then the score of `y` must not exceed the score of `x` for Q.  
   Build an adjacency matrix `M` (N×N) where `M[i,j]=1` if MR(i→j) is required.  

3. **Constraint propagation** – Treat `M` as a directed graph and compute the transitive closure with a Floyd‑Warshall‑style Boolean product using NumPy (`np.logical_or.reduce`). The resulting matrix `C` indicates all implied score‑ordering constraints.  

4. **Pragmatic load scoring** – For each answer compute three sub‑scores:  
   - *Relevance* (`R`): cosine similarity between TF‑IDF vectors of prompt and answer (implemented with NumPy).  
   - *Informativeness* (`I`): inverse of chunk size; chunk size approximated by number of conjunctive clauses (`len(re.findall(r'\b(and|or)\b', ans)) + 1`).  
   - *Clarity* (`C`): penalty for ambiguous mods (e.g., both negation and comparative in same atom).  
   Pragmatic score `P = w_R*R + w_I*I - w_C*C`.  

5. **Load penalty** – `L = α * (token count / max_len) + β * (average nesting depth of parentheses)`.  

6. **Final score** – For each answer `i`:  
   ```
   S_i = λ1 * (1 - violation_rate_i) + λ2 * P_i - λ3 * L_i
   ```  
   where `violation_rate_i` is the fraction of constraints in `C` that answer `i` breaks (computed by comparing its feature vector to the constraints).  

**Structural features parsed** – negations, comparatives, conditionals, causal verbs, ordering relations (temporal/quantitative), numeric values, quantifiers, and conjunctive/disjunctive connectives.  

**Novelty** – While metamorphic testing, pragmatic feature extraction, and cognitive‑load‑aware chunking each appear separately in literature (e.g., MR‑based program testing, Grice‑maxim heuristics in NLP, CLT‑inspired model compression), their conjunction in a pure‑algorithmic scorer that uses constraint propagation to enforce MRs while explicitly penalizing extraneous load has not been reported.  

**Ratings**  
Reasoning: 7/10 — The algorithm captures logical consistency via MRs and propagates constraints, but relies on shallow lexical features rather than deep semantic reasoning.  
Metacognition: 6/10 — Load penalty mimics awareness of cognitive effort, yet the model does not adapt its own strategy based on observed difficulty.  
Hypothesis generation: 5/10 — It can suggest which constraints are violated, but does not generate alternative explanatory hypotheses beyond scoring.  
Implementability: 8/10 — All components use only regex, NumPy, and stdlib; no external libraries or training data are required.

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

The following concepts have historical causal signatures regarding their ability to form computable reasoning tools. Adjust your implementation strategy accordingly:

- **Cognitive Load Theory**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Pragmatics**: Moderate positive synergy. Use this concept to support the primary logic, perhaps as a secondary validation step or scoring modifier.  GOODHART WARNING: This concept scores well on static tests but only 36% adversarial survival. Ensure your implementation handles paraphrased, shuffled, and extended versions of prompts, not just the literal patterns.
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

- Cognitive Load Theory + Pragmatics: strong positive synergy (+0.267). These concepts reinforce each other — integrate them tightly rather than implementing as independent checks.

Similar combinations that forged successfully:
- Cognitive Load Theory + Pragmatics + Multi-Armed Bandits (accuracy: 0%, calibration: 0%)
- Active Inference + Pragmatics + Property-Based Testing (accuracy: 0%, calibration: 0%)
- Category Theory + Embodied Cognition + Pragmatics (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

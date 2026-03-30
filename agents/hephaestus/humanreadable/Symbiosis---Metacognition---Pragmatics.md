# Symbiosis + Metacognition + Pragmatics

**Fields**: Biology, Cognitive Science, Linguistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T18:26:55.992081
**Report Generated**: 2026-03-27T23:28:38.539718

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – For each candidate answer, apply a fixed set of regex patterns to extract propositions. Each proposition is stored as a dict:  
   ```python
   {
       "text": str,                # original clause
       "polarity": int,            # +1 affirmative, -1 negated
       "type": str,                # "comparative", "conditional", "causal", "numeric", "quantifier"
       "vars": tuple,              # normalized arguments (e.g., ("X","Y") for "X > Y")
       "weight": float             # pragmatic relevance (see step 3)
   }
   ```  
   Patterns catch negations (“not”, “no”), comparatives (“more than”, “>”, “<”), conditionals (“if … then”, “unless”), causal markers (“because”, “leads to”), numeric tokens, and ordering words (“before”, “after”).  

2. **Symbiosis graph** – Build an N×N compatibility matrix **C** (numpy.ndarray) where N is the number of propositions. For each pair (i,j):  
   - If predicates match and args are identical → **C[i,j] = +1** (entailment).  
   - If one is the negation of the other → **C[i,j] = -1** (contradiction).  
   - For comparatives, apply transitivity: if *A > B* and *B > C* then *A > C* adds +0.5 to **C[A,C]**.  
   - Otherwise **C[i,j] = 0**.  
   The symbiosis score is the net mutual support:  
   ```python
   symbiosis = np.sum(np.maximum(C, 0)) - np.sum(np.maximum(-C, 0))
   ```

3. **Metacognition (confidence calibration)** – Initialize a belief vector **b** with the proposition weights. Iterate belief propagation: **b = sigmoid(np.dot(C, b))** for 5 steps (sigmoid = 1/(1+exp(-x))). Compute the normalized variance:  
   ```python
   metacog = 1 - (np.std(b) / (np.mean(b) + 1e-8))
   ```  
   Higher values indicate stable, self‑consistent beliefs.

4. **Pragmatics** – For each proposition compute a relevance weight as TF‑IDF overlap with the prompt prompt_text (using only stdlib collections and numpy for vector operations). The average relevance **prag** multiplies the other two terms.

5. **Final score** –  
   ```python
   score = symbiosis * metacog * prag
   ```  
   The class returns this scalar for each candidate; higher scores reflect answers that are mutually supportive, self‑confident, and context‑appropriately pragmatic.

**Structural features parsed**  
Negations, comparatives, conditionals, causal claims, numeric values, ordering relations (before/after, first/second), quantifiers (all, some, none), and modal verbs (might, must). These are the primitives the regex set captures.

**Novelty**  
Pure‑algorithm QA scorers typically use hash similarity, bag‑of‑words, or simple rule‑based entailment. The proposed triple‑layer—symbiosis‑style mutual‑support graph, metacognitive belief‑propagation confidence, and pragmatic TF‑IDF weighting—has not been combined in existing open‑source reasoning‑evaluation tools, making the approach novel, though it draws on argumentation frameworks and belief‑propagation literature.

**Rating**  
Reasoning: 7/10 — captures logical compatibility and transitive reasoning but lacks deep semantic parsing.  
Metacognition: 6/10 — provides a basic confidence estimate via belief propagation, yet approximates true uncertainty crudely.  
Hypothesis generation: 5/10 — the model scores existing answers; it does not generate new hypotheses.  
Implementability: 8/10 — relies only on regex, numpy, and stdlib; all steps are straightforward to code.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

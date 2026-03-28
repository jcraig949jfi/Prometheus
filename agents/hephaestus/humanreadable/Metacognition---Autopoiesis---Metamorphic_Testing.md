# Metacognition + Autopoiesis + Metamorphic Testing

**Fields**: Cognitive Science, Complex Systems, Software Engineering
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T02:56:19.217184
**Report Generated**: 2026-03-27T03:26:15.154032

---

## Nous Analysis

The algorithm builds a self‑producing constraint network from each candidate answer, propagates logical and numeric constraints to a fixed point, evaluates satisfaction of metamorphic relations, and calibrates a confidence score.

**Data structures**  
- `props`: list of dicts `{subj, pred, obj, polarity, modality}` extracted by regex patterns.  
- `rel_mat`: N×N numpy boolean matrix where `rel_mat[i,j]=True` encodes a directed relation (e.g., `props[i]` entails `props[j]`).  
- `conf`: numpy array of length N holding a provisional confidence for each proposition (initially 0.5).  
- `num_vals`: dict mapping proposition indices to extracted numeric constants.

**Operations**  
1. **Parsing** – regex extracts triples for: negations (`not`), comparatives (`>`, `<`, `>=`, `<=`), equality, conditionals (`if … then …`), causal cues (`because`, `leads to`), ordering adverbs (`before`, `after`, `first`, `then`), and quantifiers. Each triple becomes a proposition.  
2. **Initial relation seeding** – for each pair (i,j) set `rel_mat[i,j]=True` if the predicates imply entailment (e.g., same subject & predicate with stronger comparator).  
3. **Autopoietic closure** – iteratively compute `new = rel_mat @ rel_mat` (boolean matrix multiplication) and update `rel_mat = rel_mat | new` until no change (fixed point). This enforces transitivity and modus ponens without external axioms.  
4. **Contradiction detection** – a contradiction exists when `rel_mat[i,j]` and `rel_mat[j,i]` are both true for opposing polarity propositions. Count contradictions `C`.  
5. **Metamorphic testing** – for every comparative proposition, generate a transformed numeric version (add/subtract a constant k) and verify that the same relational predicate holds in the transformed world; tally satisfied metamorphic checks `M` out of total `T`.  
6. **Raw score** – `S_raw = (1 - C / (|props|+1)) * (M / T)`.  
7. **Metacognitive calibration** – using a small validation set, fit an isotonic regression (numpy only) mapping `S_raw` to observed human scores; apply this map to produce final confidence‑calibrated score `S_final`.

**Structural features parsed**  
Negations, comparatives, equality, conditionals, causal verbs, temporal ordering adverbs, numeric constants, and quantifiers.

**Novelty**  
Purely logic‑based QA scorers exist (e.g., textual entailment checks), but none combine autopoietic fixed‑point constraint propagation, metamorphic relation validation, and metacognitive isotonic calibration into a single self‑producing scoring loop. The closest work is constraint‑based semantic parsing, yet it lacks the self‑referential closure and confidence‑calibration steps.

**Ratings**  
Reasoning: 8/10 — captures multi‑step logical and numeric reasoning via closure and metamorphic checks.  
Metacognition: 7/10 — provides confidence calibration but relies on a small validation set for isotonic regression.  
Hypothesis generation: 6/10 — focuses on verifying given answers rather than generating new hypotheses.  
Implementability: 9/10 — uses only regex, numpy boolean algebra, and standard library; no external models or APIs.

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

- **Metacognition**: Causally neutral. Implement as requested without over-indexing on its mechanics. 
- **Autopoiesis**: Historical inhibitor. Tools relying heavily on this tend to fail reasoning traps. Do NOT use this for direct scoring; restrict it to the confidence() wrapper or structural parsing support only. 
- **Metamorphic Testing**: Causally neutral. Implement as requested without over-indexing on its mechanics. 

Similar combinations that forged successfully:
- Category Theory + Ergodic Theory + Metacognition (accuracy: 0%, calibration: 0%)
- Category Theory + Metacognition + Criticality (accuracy: 0%, calibration: 0%)
- Chaos Theory + Autopoiesis + Criticality (accuracy: 0%, calibration: 0%)

GLOBAL: The final tool must strictly beat the NCD compression baseline. Use structural parsing (negations, comparatives, conditionals, numeric evaluation) as the primary scoring signal. NCD is only a tiebreaker for candidates where no structural signal is detected.

---

## Hephaestus Forge Status

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

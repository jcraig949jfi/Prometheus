# Metacognition + Pragmatics + Compositional Semantics

**Fields**: Cognitive Science, Linguistics, Philosophy
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T01:23:04.253191
**Report Generated**: 2026-04-02T04:20:11.701041

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositional Semantics)** – Use a handful of regex patterns to extract primitive propositions from the prompt and each candidate answer:  
   - Entities (`\b[A-Z][a-z]*\b`)  
   - Predicates (`\b(is|are|was|were|has|have|does|did)\b`)  
   - Relations (`\b(more than|less than|greater than|before|after|because|leads to|if.*then)\b`)  
   - Negations (`\bnot\b|\bno\b`)  
   - Quantifiers (`\ball\b|\bsome\b|\bmost\b|\bnone\b`)  
   - Numeric values (`\d+(\.\d+)?`)  
   Each proposition becomes a node; binary relations become directed edges labeled with the relation type. Store the graph as a dictionary `graph[entity] = {neighbor: {rel_type: bool}}` and a parallel NumPy array `feat` of shape `(n_props, 8)` encoding presence of negation, comparative, conditional, causal, numeric, quantifier, modality, and polarity.

2. **Constraint Propagation (Logical Reasoning)** – Initialize a truth matrix `T` from explicit propositions (True/False). Apply transitive closure for ordering relations (`>`, `<`, `before`, `after`) using Floyd‑Warshall on the numeric/ordinal sub‑graph. Apply modus ponens for conditionals: if `if A then B` edge exists and `A` is True, set `B` True. Iterate until fixed point. The logical entailment score for a candidate is the fraction of its propositions that evaluate to True after propagation.

3. **Pragmatic Adjustment** – Compute a pragmatic weight `w_prag` ∈ [0,1]:  
   - Penalize violations of Grice’s maxims: excess redundancy (repeated predicates) → `-0.1`; lack of relevance (no overlap with prompt entities) → `-0.2`; informativeness (missing expected quantifier when prompt contains one) → `-0.15`.  
   - Boost for appropriate speech act detected via cue words (`explain`, `justify`, `suggest`).  
   Final pragmatic factor = `sigmoid(sum adjustments)`.

4. **Metacognitive Calibration** – Derive a confidence `c_meta` ∈ [0,1]:  
   - Base confidence = 0.5 + 0.1*(log(answer length) - mean_log_len)/std_log_len.  
   - Error monitoring: if any proposition and its negation both become True after propagation, subtract 0.3.  
   - Strategy selection: if the prompt contains a conditional, weight logical score higher (0.7) vs. pragmatic (0.3); otherwise reverse.  
   Meta score = `c_meta * (w_logic*logic_score + w_prag*pragmatic_score)`.

**Structural Features Parsed** – negations, comparatives, conditionals, causal claims, numeric values, ordering relations, quantifiers, modality, polarity.

**Novelty** – While logical form extraction, pragmatic enrichment, and confidence calibration appear separately in the literature (e.g., CCG parsers, implicature models, calibration nets), integrating all three into a single deterministic, numpy‑only scoring pipeline that jointly propagates constraints, adjusts for Gricean maxims, and calibrates via internal error checks is not documented in existing work.

Reasoning: 7/10 — solid logical core but limited to hand‑crafted patterns.  
Metacognition: 6/10 — confidence heuristics are simple; no true self‑reflective loop.  
Hypothesis generation: 5/10 — the system evaluates given answers; it does not propose new ones.  
Implementability: 9/10 — relies only on regex, dictionaries, and NumPy; straightforward to code.

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

*Not yet attempted by Hephaestus.*

---

## Code

*No code was produced for this combination.*

# Dual Process Theory + Active Inference + Normalized Compression Distance

**Fields**: Cognitive Science, Cognitive Science, Information Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T12:12:27.463221
**Report Generated**: 2026-03-27T16:08:16.428670

---

## Nous Analysis

**Algorithm**  
1. **Parsing** – Use regex to extract atomic propositions from the prompt and each candidate answer:  
   - Negations: `\bnot\b|\bn’t\b` → flag `neg=True`.  
   - Comparatives: `(more|less|greater|fewer|\d+\s*(%|percent))\s+\w+` → store as `(attr, op, value)`.  
   - Conditionals: `if\s+(.+?),\s+then\s+(.+)` → directed edge `antecedent → consequent`.  
   - Causal claims: `\bbecause\b|\bdue to\b` → edge `cause → effect`.  
   - Ordering relations: `before|after|precedes|follows` → temporal edge.  
   - Numeric values: `\d+(\.\d+)?` → attach to the preceding noun phrase.  
   Each proposition is stored as a tuple `(text, polarity, type, slots)` where `slots` holds extracted comparatives, numbers, etc. All propositions from a string are placed in a list `props`.  

2. **Constraint graph** – Build a directed adjacency matrix `G` (numpy bool) where `G[i,j]=True` if proposition *i* entails proposition *j* (from conditionals, causals, ordering). Initialize reflexive self‑loops.  

3. **Constraint propagation** – Apply transitive closure (Floyd‑Warshall on bools) and modus ponens: iterate until no change, setting `G[i,k] |= G[i,j] & G[j,k]`. Derive a truth vector `T` by initializing `T[i]=True` for propositions that appear asserted in the prompt (positive polarity) and false for negated ones; propagate `T` through `G` (`T = T @ G` with boolean arithmetic) to obtain implied truths.  

4. **Similarity via compression** – Compute Normalized Compression Distance (NCD) between the concatenated string of prompt propositions `P` and candidate propositions `C` using `zlib.compress` (stdlib).  
   `NCD(P,C) = (|PC|_z - min(|P|_z,|C|_z)) / max(|P|_z,|C|_z)` where `|·|_z` is compressed length. Lower NCD indicates higher algorithmic similarity.  

5. **Scoring** – Define expected free energy approximation:  
   `EF = α * NCD(P,C) + β * (1 - sat_ratio)` where `sat_ratio = (# of propositions in C that are true under T) / len(C)`.  
   Scores are `-EF` (higher is better). `α,β` are fixed weights (e.g., 0.5 each) set via numpy arrays.  

**Structural features parsed** – negations, comparatives, conditionals, causal language, temporal ordering, numeric quantities, and explicit assertions/denials.  

**Novelty** – While compression‑based similarity (NCD) and logical constraint propagation appear separately, coupling them through an active‑inference‑style expected free energy term that treats fast similarity as epistemic value and slow constraint satisfaction as pragmatic value is not present in existing surveys. No known tool jointly optimizes these two objectives in a single scoring function.  

**Ratings**  
Reasoning: 7/10 — captures both surface similarity and deep logical consistency, but relies on hand‑crafted regex which may miss complex constructions.  
Metacognition: 6/10 — the EF term provides a rudimentary uncertainty‑sensitivity, yet no explicit monitoring of search depth or alternative hypotheses.  
Hypothesis generation: 5/10 — generates implied propositions via propagation, but does not propose new candidate structures beyond those present in inputs.  
Implementability: 8/10 — uses only regex, numpy, and stdlib (zlib); all operations are O(n²) at worst and straightforward to code.

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

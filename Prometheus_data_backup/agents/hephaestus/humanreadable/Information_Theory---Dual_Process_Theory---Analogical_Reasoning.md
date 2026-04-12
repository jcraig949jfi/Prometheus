# Information Theory + Dual Process Theory + Analogical Reasoning

**Fields**: Mathematics, Cognitive Science, Cognitive Science
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-27T21:30:26.441180
**Report Generated**: 2026-03-27T23:28:38.580717

---

## Nous Analysis

**Algorithm – Relational‑Entropy Scorer (RES)**  

1. **Parsing stage (System 1‑style fast extraction)**  
   - Input: prompt *P* and each candidate answer *Aᵢ*.  
   - Use a fixed set of regex patterns to extract **atomic propositions** and **binary relations** from both texts.  
     - Patterns target:  
       - Negations (`not`, `no`, `-`) → flag `neg=True`.  
       - Comparatives (`greater than`, `less than`, `>`, `<`) → relation type `cmp`.  
       - Conditionals (`if … then …`, `unless`) → antecedent/consequent slots.  
       - Causal verbs (`cause`, `lead to`, `result in`) → relation type `caus`.  
       - Ordering (`first`, `second`, `before`, `after`) → relation type `ord`.  
       - Numeric values (`\d+(\.\d+)?`) → attached as attributes.  
   - Each proposition becomes a node **n** with fields: `{id, type, polarity, value?}`.  
   - Each relation becomes an edge **e** with fields: `{src, tgt, rel_type, weight}` where `weight` starts at 1.0.

2. **Constraint‑propagation stage (System 2‑style deliberate reasoning)**  
   - Build a directed graph *G* from the union of nodes/edges of *P* and *Aᵢ*.  
   - Apply deterministic rules to propagate truth values:  
     - **Modus ponens**: if `if X then Y` edge exists and `X` is true → set `Y` true.  
     - **Transitivity** for `ord` and `caus`: if `a→b` and `b→c` then infer `a→c` (add edge with weight = min(weights)).  
     - **Negation handling**: a node marked `neg=True` flips the boolean of its literal.  
   - Iterate until fixed point (≤ |V| passes).  
   - After propagation, compute a binary truth vector **t** for all nodes in *P* (true/false/unknown).

3. **Information‑theoretic scoring (Analogical mapping + entropy)**  
   - For each candidate, construct a **joint distribution** over the proposition nodes of *P* and *Aᵢ*:  
     - Let `p(x)` = proportion of true nodes in *P* (|{x∈P | t(x)=True}| / |P|).  
     - Let `qᵢ(x)` = proportion of true nodes mapped from *Aᵢ* to *P* via exact structural match (same `id`, `type`, `rel_type`). Unmatched nodes get probability 0.  
   - Compute **KL‑divergence** `D_KL(p‖qᵢ) = Σ p(x) log(p(x)/qᵢ(x))` (treat 0→0 contribution as 0, avoid log(0) by adding ε=1e‑12).  
   - The **score** for candidate *i* is `Sᵢ = -D_KL(p‖qᵢ)`. Higher score means the answer’s relational structure preserves the information content of the prompt after logical propagation.

**Structural features parsed** – negations, comparatives, conditionals, causal claims, ordering relations, numeric attributes.

**Novelty** – The combination mirrors existing work on logical form extraction (e.g., Logic Tensor Networks) and KL‑based answer selection, but the explicit dual‑stage (fast regex → slow constraint propagation) followed by an information‑theoretic analogical match is not described in a single published pipeline; thus it is novel in this specific configuration.

**Ratings**  

Reasoning: 8/10 — captures logical inference and information preservation, though limited to hand‑crafted patterns.  
Metacognition: 6/10 — System 1/System 2 split is modeled but no self‑monitoring of uncertainty beyond KL.  
Hypothesis generation: 5/10 — generates inferred edges via propagation, but does not propose new relational structures beyond those present.  
Implementability: 9/10 — relies only on regex, numpy for array ops, and pure Python loops; straightforward to code.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 5/10 |
| Implementability | 9/10 |
| **Composite** | **6.33** |

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

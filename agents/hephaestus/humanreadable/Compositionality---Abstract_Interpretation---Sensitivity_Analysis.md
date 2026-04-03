# Compositionality + Abstract Interpretation + Sensitivity Analysis

**Fields**: Linguistics, Formal Methods, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-02T02:57:00.968770
**Report Generated**: 2026-04-02T04:20:11.845038

---

## Nous Analysis

**Algorithm**  
1. **Parsing (compositionality)** – Use a handful of regex patterns to extract atomic propositions from the prompt and each candidate answer:  
   - Predicates: `(\w+)\s+(is|are|was|were)\s+(.+)` → `(subject, copula, complement)`  
   - Comparatives: `(\w+)\s+([<>]=?)\s+(\d+(\.\d+)?) → (left, op, right)`  
   - Conditionals: `if\s+(.+?)\s+then\s+(.+)` → `(antecedent, consequent)`  
   - Causal verbs: `(.+?)\s+(causes|leads to|results in)\s+(.+)` → `(cause, effect)`  
   - Negations: `\bnot\b` or `n't` attached to a predicate.  
   Each proposition becomes a node with fields `{type, args, polarity}`; type ∈ {EQ, NEQ, LT, GT, LE, GE, IF, CAUSE, NOT}.  

2. **Constraint graph** – Build a directed graph `G = (V, E)` where `V` are propositions and `E` encodes logical dependencies (e.g., the antecedent of an IF points to its consequent; a CAUSE points from cause to effect).  

3. **Abstract interpretation (fix‑point propagation)** – Assign each numeric variable an interval `[l, u]` (initially `[−∞, +∞]`). For each node, define abstract transfer functions:  
   - `LT(x, c)`: `u = min(u, c‑ε)`  
   - `GT(x, c)`: `l = max(l, c+ε)`  
   - `IF(p, q)`: if `p` is known true, propagate `q`’s constraints; if false, block propagation.  
   - Boolean nodes use three‑valued logic (T/F/⊥) with ⊥ meaning unknown.  
   Iterate over `G` with a work‑list until intervals and truth values stop changing (Kleene fix‑point).  

4. **Sensitivity analysis** – For each numeric constant `c_i` in the prompt, perturb it by `±δ` (δ = 1% of |c_i| or 0.01 if zero), re‑run the fix‑point, and record the change in the candidate’s disagreement measure (see below). The sensitivity score `S = (1/n) Σ_i |Δ disagreement_i| / δ`.  

5. **Scoring** – Translate the candidate answer into the same proposition set, compute a disagreement `D`:  
   - Numeric: L1 distance between candidate’s implied interval and the propagated interval (0 if inside).  
   - Boolean: 0 if matches propagated truth value, 1 if opposite, 0.5 if unknown.  
   - Structural: count of missing/extra edges in the candidate’s graph vs. `G`.  
   Final score `= −(D + λ·S)` (λ balances robustness; higher is better). All operations use only `numpy` for interval arithmetic and Python’s `re`, `collections`, `itertools`.  

**Structural features parsed** – negations, comparatives (`<, >, ≤, ≥`), equality, conditionals (`if…then`), causal verbs (`causes, leads to`), ordering relations (`before, after, precedes`), numeric constants, and basic quantifiers (`all, some`) via keyword triggers.  

**Novelty** – While each piece (compositional semantic parsing, abstract interpretation fix‑point, sensitivity‑based robustness) exists in program analysis and formal verification, their joint use as a lightweight scoring mechanism for open‑ended QA answers has not been described in the literature; it adapts static analysis techniques to a pure‑numpy, rule‑based evaluator.  

**Ratings**  
Reasoning: 8/10 — captures logical dependencies and numeric bounds via provable fix‑point propagation.  
Metacognition: 6/10 — the method can estimate its own uncertainty (sensitivity) but lacks explicit self‑reflection on parse failures.  
Hypothesis generation: 5/10 — generates implicit hypotheses (intervals, truth values) but does not propose alternative parses beyond the deterministic extractor.  
Implementability: 9/10 — relies solely on regex, numpy arrays, and a work‑list loop; no external libraries or neural components needed.

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

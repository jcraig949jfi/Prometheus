# Compositional Semantics + Metamorphic Testing + Sensitivity Analysis

**Fields**: Philosophy, Software Engineering, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-04-01T11:32:25.916752
**Report Generated**: 2026-04-01T20:30:43.906114

---

## Nous Analysis

**Algorithm**  
1. **Parsing (Compositional Semantics)** – Tokenize the prompt and each candidate answer with a small regex‑based lexer that extracts:  
   - numeric literals (`\d+(\.\d+)?`)  
   - comparatives (`>`, `<`, `>=`, `<=`, `=`)  
   - logical connectives (`and`, `or`, `not`)  
   - conditionals (`if … then …`, `because …`)  
   - causal markers (`causes`, `leads to`)  
   Build an abstract syntax tree (AST) where each node has fields `{type, value, children}`. Types include `NUM`, `COMP`, `COND`, `NEG`, `CAUSAL`, `CONJ`, `DISJ`. The meaning of a complex node is computed recursively: e.g., a `COND` node is true iff its antecedent child is false or its consequent child is true (material implication); a `COMP` node evaluates the numeric relation between its two children.  

2. **Metamorphic Relations (MRs)** – Define a finite set of input‑level mutations that preserve the intended semantics of a correct answer:  
   - **Scale**: multiply all numeric literals by a constant `k>0` (e.g., `k=2`).  
   - **Swap**: exchange the two operands of a commutative comparative (`a > b` ↔ `b < a`).  
   - **Negate‑Flip**: apply double negation (`not not P` → `P`).  
   - **Order‑Insert**: insert a tautological ordering (`x ≤ x`) anywhere.  
   For each candidate answer, generate its MR‑transformed versions using the same parser.  

3. **Sensitivity Analysis** – For each MR set, compute the constraint‑satisfaction score:  
   - Traverse the AST and collect atomic propositions (leaf nodes).  
   - Build a constraint graph where edges represent required relations (e.g., from a `COMP` node an edge `a > b`).  
   - A proposition is satisfied if the graph admits a consistent assignment (checked via simple propagation: transitivity for order, unit resolution for Horn‑style conditionals).  
   - Base score `S₀ = (# satisfied propositions) / (total propositions)`.  
   - For each MR `i`, compute score `Sᵢ`. Sensitivity `σ = Var({Sᵢ})` (numpy variance).  
   - Final score `S = S₀ * exp(-λ·σ)`, with λ=1.0 to penalize answers whose correctness fluctuates under MRs.  

**Structural Features Parsed** – Negations, comparatives, conditionals, causal claims, numeric values, ordering relations, conjunctions/disjunctions, and double‑negation patterns.  

**Novelty** – While compositional semantics, metamorphic testing, and sensitivity analysis each appear separately in NLP‑reasoning work, their tight integration—using MR‑generated perturbations to measure sensitivity of a compositional constraint‑satisfaction score—is not present in existing surveys.  

**Ratings**  
Reasoning: 7/10 — The algorithm captures logical structure and derives a principled correctness metric, but it relies on hand‑crafted MRs and simple propagation, limiting depth of reasoning.  
Metacognition: 6/10 — Sensitivity to MRs offers a rudimentary form of self‑check, yet the method does not explicitly model uncertainty about its own parsing or MR selection.  
Hypothesis generation: 5/10 — The system evaluates given candidates; it does not generate new answer hypotheses beyond applying predefined MRs.  
Implementability: 8/10 — All steps use regex, basic AST construction, numpy for variance, and pure Python control flow; no external libraries or neural components are required.

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

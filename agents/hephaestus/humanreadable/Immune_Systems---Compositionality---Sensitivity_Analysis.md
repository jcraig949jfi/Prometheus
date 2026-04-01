# Immune Systems + Compositionality + Sensitivity Analysis

**Fields**: Biology, Linguistics, Statistics
**Nous Model**: nvidia/nemotron-3-super-120b-a12b
**Nous Timestamp**: 2026-03-29T03:17:38.943628
**Report Generated**: 2026-03-31T14:34:57.559070

---

## Nous Analysis

**Algorithm – Clonal‑Compositional Sensitivity Scorer (CCSS)**  
The scorer treats each candidate answer as a set of logical clauses extracted by regex. A clause is a tuple `(type, [lit₁, lit₂, …])` where `type ∈ {EQ, NEQ, LT, GT, LE, GE, IMP, AND, OR, NOT}` and each literal is either a Boolean variable (e.g., “the drug reduces symptoms”) or a numeric expression (`var op const`). All clauses are stored in a list `clauses`.  

1. **Parsing (Compositionality)** – Regex patterns capture:  
   * Negations (`not`, `no`) → `NOT`  
   * Comparatives (`greater than`, `less than`, `≥`, `≤`) → `GT/LT/GE/LE`  
   * Equality (`is`, `equals`) → `EQ/NEQ`  
   * Conditionals (`if … then …`, `because`) → `IMP`  
   * Causal keywords (`leads to`, `causes`) → treated as `IMP` with a confidence weight.  
   * Numeric values with units → numeric literals.  
   The output is a directed hyper‑graph where edges represent implications; the graph is topologically sorted for fast propagation.

2. **Base Satisfaction** – Starting from an initial truth assignment (all variables = False, numerics = 0), unit‑propagation walks the graph: whenever an antecedent of an `IMP` becomes true, the consequent is forced true; numeric clauses are satisfied if the expression evaluates true. The number of satisfied clauses `S₀` is the base score (0 ≤ S₀ ≤ |clauses|).

3. **Sensitivity Analysis** – For each atomic literal `lᵢ` we create a perturbed copy:  
   * Boolean literals are flipped.  
   * Numerics are perturbed by `±ε` (ε = 1e‑3 of the variable’s magnitude).  
   Using NumPy we vectorize the perturbation of all literals, re‑run unit‑propagation, and obtain satisfied counts `Sᵢ`. Sensitivity is the mean absolute change:  
   `σ = (1/N) Σ |Sᵢ – S₀|`.  

4. **Immune‑Inspired Selection** – The candidate answer is an “antibody”. We compute affinity `A = S₀ – λ·σ` (λ = 0.5 balances fit vs. robustness). A memory set of the top‑k answers is kept; clonal expansion creates mutants by randomly swapping two clauses or negating a literal, re‑scoring them, and inserting high‑affinity mutants into memory. The final score returned for a prompt is the highest affinity in memory.

**Parsed Structural Features** – Negations, comparatives, equality, conditionals (`if‑then`), causal keywords, ordering relations (before/after), numeric constants with units, and conjunctive/disjunctive combinations.

**Novelty** – Purely symbolic scorers exist (e.g., logic‑based QA), and immune‑inspired optimization appears in evolutionary algorithms, but the tight integration of clause‑level compositional parsing, unit‑propagation based satisfaction, and explicit sensitivity‑driven affinity scoring is not described in prior work. It therefore constitutes a novel combination.

**Rating**  
Reasoning: 8/10 — captures logical structure and robustness, though limited to shallow clause‑level reasoning.  
Metacognition: 6/10 — provides an internal sensitivity estimate but lacks higher‑order self‑reflection on reasoning strategies.  
Hypothesis generation: 7/10 — clonal expansion yields diverse mutants, enabling exploratory hypothesis generation.  
Implementability: 9/10 — relies only on regex, NumPy vectorization, and basic graph algorithms; no external libraries or APIs needed.

### Scores

| Metric | Score |
|--------|-------|
| Reasoning | 8/10 |
| Metacognition | 6/10 |
| Hypothesis Generation | 7/10 |
| Implementability | 9/10 |
| **Composite** | **7.0** |

**Novelty**: unproductive
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
